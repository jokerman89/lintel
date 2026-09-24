# component: universal-work-lifecycle-tests
# implements: ADR-0026, ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P08.md
# constraints: synthetic data; no host dispatch or global configuration
# last_intent_review: 2026-09-20
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import runpy
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, required=True)
args, remaining = parser.parse_known_args()
ROOT = args.root.resolve()
WORK = runpy.run_path(str(ROOT / "bin/li-work-artifacts.py"))
REVIEW_FIXTURE = runpy.run_path(str(ROOT / "tests/unit/review_evidence.py"))


def skill_block(name, heading):
    text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    section = text.split(heading, 1)[1]
    return re.search(r"```bash\n(.*?)\n```", section, re.S).group(1)


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lintel-lifecycle-")
        self.addCleanup(self.cleanup)
        self.repo = Path(self.temp.name) / "repo with spaces"
        (self.repo / ".claude").mkdir(parents=True)
        (self.repo / "AGENTS.md").write_text("Synthetic work only.\n")
        (self.repo / ".claude/lintel-layout.yaml").write_text("layout_version: 5\n")
        self.env = {**os.environ, "HOME": (Path(self.temp.name) / "home").as_posix(),
                    "LINTEL_HOME": (Path(self.temp.name) / "home/lintel").as_posix(),
                    "LINTEL_REPO_ROOT": self.repo.as_posix(),
                    "LINTEL_SOURCE_ROOT": ROOT.as_posix(), "LINTEL_ASCII": "1",
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
        # Plan-analysis fixtures run the selected interpreter; keep an explicit caller choice.
        self.env.setdefault("LINTEL_PYTHON", Path(sys.executable).as_posix())
        for name in ("LINTEL_CYCLE_ID", "LINTEL_WORK_MAP", "LINTEL_PROFILE_REFERENCE",
                     "LINTEL_PROFILE_CONTEXT", "LINTEL_PROFILE_CONTEXT_FILE",
                     "LINTEL_SESSION_ID", "CLAUDE_SESSION_ID", "LINTEL_PROFILE_PACK",
                     "LINTEL_PACKS_DIR", "LINTEL_AUDIT_DIR", "LINTEL_ACTIVE_PACK_FILE"):
            self.env.pop(name, None)

    def cleanup(self):
        from native_paths import native_io_path
        root = native_io_path(Path(self.temp.name))
        if root.exists():
            shutil.rmtree(root)
        self.temp.cleanup()

    def shell(self, script, expected=0):
        result = subprocess.run(
            ["bash", "-c", 'set -euo pipefail\nsource "$LINTEL_SOURCE_ROOT/lib/state.sh"\n' + script],
            cwd=self.repo, env=self.env, text=True, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.last_stderr = result.stderr
        return result.stdout


class LifecycleTests(FixtureCase):
    def test_cycle_identity_cannot_be_overridden_by_metadata(self):
        self.shell("""
if state_cycle_begin first full cycle_id=second; then exit 97; fi
test ! -e "$(state_file)"
if state_cycle_begin first full cycle_mode=hotfix; then exit 98; fi
test ! -e "$(state_file)"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
for key in work_map_path work_artifacts profile_reference profile_context_file required_policy; do
  if workflow_begin first full "" "$key=forged"; then exit 99; fi
  test ! -e "$(state_file)"
done
""")

    def test_footer_uses_status_not_next_metadata(self):
        for status, label in (("STARTING", "in progress"), ("BLOCKED", "blocked"),
                              ("DONE", "done"), ("DONE_WITH_CONCERNS", "done with concerns")):
            with self.subTest(status=status):
                out = self.shell(f"""
state_append BUILD {status} next=REVIEW
source "$LINTEL_SOURCE_ROOT/lib/cycle-footer.sh"
render_cycle_footer --compact --state "$(state_file)"
""")
                self.assertIn(f"`BUILD` {label}", out)
                if status not in ("DONE", "DONE_WITH_CONCERNS"):
                    self.assertNotIn("`BUILD` done", out)
                    self.assertNotIn("cycle complete", out)

    def test_cycle_close_preserves_segment_and_old_cycle(self):
        out = self.shell("""
state_append CYCLE STARTING cycle_id=one cycle_mode=hotfix
state_append SENSE DONE next=BUILD
state_append BUILD BLOCKED next=REVIEW note=repair
state_append CYCLE DONE cycle_complete=true
state_cycle_segment
""")
        self.assertIn("phase: SENSE", out)
        self.assertIn("phase: BUILD", out)
        out = self.shell("""
state_append CYCLE STARTING cycle_id=two cycle_mode=research-dive
state_append SENSE DONE next=DEFINE
state_cycle_segment "$(state_file)" one
""")
        self.assertIn("cycle_id: one", out)
        self.assertNotIn("cycle_id: two", out)
        self.assertIn("note: repair", out)

    def test_begin_once_and_interrupted_resume(self):
        self.shell("""
state_cycle_begin first full operation=build
state_cycle_begin first full operation=build
test "$(grep -c '^phase: CYCLE$' "$(state_file)")" = 1
state_phase_begin SENSE next=SCOPE
state_append SENSE DONE next=SCOPE
if state_phase_begin SENSE next=SCOPE; then exit 90; else test "$?" = 3; fi
state_phase_begin SCOPE next=DEFINE
test "$(state_resume_phase)" = SCOPE
if state_phase_begin SCOPE; then exit 91; else test "$?" = 2; fi
state_phase_begin --retry SCOPE next=DEFINE
state_append SCOPE DONE next=DEFINE
test "$(state_resume_phase)" = DEFINE
test "$(grep -c '^phase: SENSE$' "$(state_file)")" = 2
""")


class WorkSelectionTests(FixtureCase):
    def named_swarm(self):
        fixture_class = runpy.run_path(str(ROOT / "tests/unit/swarm-contract.py"))["SwarmFixture"]
        fixture = fixture_class(self.repo)
        fixture._write("plan.md", "# Plan\n\n### core - Named work\n\n- [ ] Finish the named work.\n"
                       "\n### Overview\nThis is prose, not another task.\n")
        fixture._write(".claude/plans/example/swarm/briefs/core.md", "# Core brief\n")
        fixture.coordination["lanes"] = [fixture._lane("core", 1, "src/core")]
        fixture.coordination["max_parallel"] = 1
        fixture.save()
        self.assertTrue(fixture.validate().ok)
        return fixture

    def test_named_swarm_singleton_uses_selected_coordination_without_acceptance(self):
        fixture = self.named_swarm()
        fixture.work_map["status"] = "DRAFT"
        fixture.save()
        before = {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
        result = WORK["work_context"](self.repo, Path(fixture.work_map_path))
        self.assertEqual(set(result["tasks"]), {"core"})
        self.assertEqual(result["packages"]["core"]["leaf_ids"], ["core"])
        self.assertEqual(result["packages"]["core"]["leaves"]["core"], result["tasks"]["core"])
        self.assertEqual(result["incomplete_ids"], ["core"])
        self.assertEqual(result["status"], "DRAFT")
        self.assertEqual(result["task_evidence"], "source-status-only")
        self.assertIsNone(result["binding"])
        self.assertFalse(result["release_clearance"])
        self.assertEqual(before, {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()})

    def test_selected_coordination_is_counted_once_and_cannot_switch_initiatives(self):
        fixture = self.named_swarm()
        result = WORK["work_context"](self.repo, Path(fixture.work_map_path),
                                      warm_paths=[fixture.coordination_path])
        paths = {fixture.work_map_path, "spec.md", "plan.md", "prompt.md",
                 fixture.coordination_path}
        self.assertEqual({item["path"] for item in result["manifest"]["files"]}, paths)
        expected_bytes = sum(len((self.repo / path).read_bytes()) for path in paths)
        self.assertEqual(result["manifest"]["bytes"], expected_bytes)
        exact = WORK["work_context"](self.repo, Path(fixture.work_map_path),
                                     max_files=5, max_bytes=expected_bytes)
        self.assertEqual(exact["manifest"]["bytes"], expected_bytes)
        with self.assertRaises(ValueError):
            WORK["work_context"](self.repo, Path(fixture.work_map_path), max_bytes=expected_bytes - 1)
        with self.assertRaises(ValueError):
            WORK["work_context"](self.repo, Path(fixture.work_map_path), max_files=4)
        fixture.coordination["work_map"] = "different-work.json"
        fixture.save()
        before = {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
        with self.assertRaises(ValueError):
            WORK["work_context"](self.repo, Path(fixture.work_map_path))
        self.assertEqual(before, {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()})

    def test_ordinary_heading_does_not_become_a_task_without_explicit_selection(self):
        fixture = self.named_swarm()
        del fixture.work_map["execution_mode"]
        del fixture.work_map["coordination"]
        fixture.save()
        result = WORK["work_context"](self.repo, Path(fixture.work_map_path))
        self.assertEqual(result["tasks"], {})
        self.assertEqual(result["packages"], {})
        self.assertEqual(result["incomplete_ids"], [])
        self.assertEqual(result["task_evidence"], "unrecognized")
        self.assertIsNone(result["binding"])

    def make_map(self, name, workflow="spec-kit"):
        folder = self.repo / "specs" / name
        folder.mkdir(parents=True)
        (folder / "spec.md").write_text("# Requirements\nKeep original acceptance.\n")
        (folder / "plan.md").write_text("# Technical design\nPreserve the API.\n")
        (folder / "tasks.md").write_text(
            "- [x] T001 Establish baseline\n- [ ] T014 Preserve API (depends T001)\n")
        (folder / "prompt.md").write_text("Continue original T014.\n")
        mapping = dict(schema_version=1, workflow=workflow, status="APPROVED",
                       **{key: f"specs/{name}/{key}.md" for key in ("spec", "plan", "tasks", "prompt")})
        (folder / "work.json").write_text(json.dumps(mapping))
        return f"specs/{name}/work.json", mapping

    def test_explicit_map_original_ids_and_no_writes(self):
        selected, mapping = self.make_map("chosen")
        self.make_map("newer-decoy")
        before = {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
        result = WORK["work_context"](self.repo, Path(selected))
        self.assertEqual(result["work_map"], selected)
        self.assertEqual(result["artifacts"], {k: mapping[k] for k in WORK["REQUIRED_ARTIFACTS"]})
        self.assertEqual(list(result["tasks"]), ["T001", "T014"])
        self.assertEqual(result["tasks"]["T014"]["dependencies"], ["T001"])
        self.assertEqual(result["tasks"]["T014"], result["packages"]["T014"]["leaves"]["T014"])
        self.assertFalse(result["tasks"]["T014"]["complete"])
        self.assertFalse(result["release_clearance"])
        self.assertEqual(before, {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()})
        self.assertFalse((self.repo / ".claude/runtime").exists())

    def test_manifest_measures_selected_and_warming_bytes_once(self):
        selected, mapping = self.make_map("chosen")
        (self.repo / "warm.txt").write_text("additional real bytes\n")
        result = WORK["work_context"](self.repo, Path(selected), warm_paths=["warm.txt", mapping["spec"]])
        files = result["manifest"]["files"]
        self.assertEqual(len(files), 6)
        total = sum((self.repo / item["path"]).stat().st_size for item in files)
        self.assertEqual(result["manifest"]["bytes"], total)
        report = WORK["work_budget"](result)
        self.assertEqual(report["capacity_tokens"], None)
        self.assertEqual(report["admission"], "unknown")
        self.assertEqual(report["estimated_input_tokens"], (total + 3) // 4)
        with self.assertRaises(ValueError):
            WORK["work_context"](self.repo, Path(selected), max_bytes=5)
        with self.assertRaises(ValueError):
            WORK["work_context"](self.repo, Path(selected), warm_paths=["missing.txt"])

    def test_budget_matches_reported_capacity_boundary_without_a_default_cap(self):
        selected, _ = self.make_map("chosen")
        context = WORK["work_context"](self.repo, Path(selected))
        estimate = (context["manifest"]["bytes"] + 3) // 4
        inputs = dict(capacity_tokens=estimate + 30, used_tokens=20, reserve_tokens=10,
                      capacity_source="synthetic host observation", usage_source="synthetic observed usage")
        self.assertEqual(WORK["work_budget"](context, **inputs)["admission"], "within-reported-headroom")
        self.assertEqual(WORK["work_budget"](
            context, **{**inputs, "capacity_tokens": estimate + 29})["admission"], "over-capacity")
        self.assertEqual(WORK["work_budget"](
            context, **inputs, usage_kind="estimated")["admission"], "estimated-fit")
        with self.assertRaises(ValueError):
            WORK["work_budget"](context, **{**inputs, "capacity_source": None})

    def test_binding_uses_p05_and_original_mapped_task_progress(self):
        selected, mapping = self.make_map("chosen")
        kwargs = dict(package_id="T014", leaf_ids=["T014"], acceptance_paths=[mapping["spec"]])
        first = WORK["work_context"](self.repo, Path(selected), **kwargs)
        from review_contract import bind_work
        self.assertEqual(first["binding"], bind_work(self.repo, work_map=selected, **kwargs))
        task = self.repo / mapping["tasks"]
        task.write_text(task.read_text().replace("[ ] T014", "[x] T014"))
        second = WORK["work_context"](self.repo, Path(selected), **kwargs)
        self.assertEqual(first["binding"], second["binding"])
        task.write_text(task.read_text().replace("Preserve API", "Break API"))
        changed = WORK["work_context"](self.repo, Path(selected), **kwargs)
        self.assertNotEqual(first["binding"], changed["binding"])
        with self.assertRaises(ValueError):
            WORK["work_context"](self.repo, Path(selected), **{**kwargs, "leaf_ids": ["T999"]})

    def test_missing_selected_artifact_not_hidden_by_other_initiative(self):
        selected, mapping = self.make_map("chosen")
        self.make_map("newer-decoy")
        (self.repo / mapping["spec"]).unlink()
        with self.assertRaises(ValueError):
            WORK["work_context"](self.repo, Path(selected))
        self.assertFalse((self.repo / ".claude/runtime").exists())

    def test_real_profile_and_map_survive_fresh_shell_resume(self):
        selected, mapping = self.make_map("chosen")
        self.make_map("newer-decoy")
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {selected} operation=build
state_phase_begin BUILD next=REVIEW
""")
        result = json.loads(self.shell("""
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_resume first
"""))
        self.assertEqual(result["phase"], "BUILD")
        self.assertEqual(result["operation"], "build")
        self.assertEqual(result["work_map"], selected)
        self.assertEqual(result["artifacts"]["tasks"], mapping["tasks"])
        self.assertEqual(result["profile"]["generation"], 1)
        self.assertFalse(result["required_policy"]["required"])
        before = (self.repo / ".claude/runtime/state/00-state.md").read_bytes()
        self.shell("""
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_resume first specs/newer-decoy/work.json
""", expected=2)
        self.assertEqual(before, (self.repo / ".claude/runtime/state/00-state.md").read_bytes())

    def test_profile_bound_inspection_cannot_override_target_or_map(self):
        selected, _ = self.make_map("chosen")
        decoy, _ = self.make_map("newer-decoy")
        foreign = Path(self.temp.name) / "foreign"
        shutil.copytree(self.repo, foreign)
        self.env["FOREIGN"] = foreign.as_posix()
        for override in ('--repo "$FOREIGN"', '--rep="$FOREIGN"', f"--map={decoy}"):
            with self.subTest(override=override):
                out = self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_inspect {selected} {override}
""", expected=2)
                self.assertEqual(out, "")

    def test_required_profile_drift_blocks_resume_before_output(self):
        selected, _ = self.make_map("chosen")
        pack = Path(self.env["LINTEL_HOME"]) / "packs/strict/pack.yaml"
        pack.parent.mkdir(parents=True)
        pack.write_text("name: strict\nversion: 1.0.0\n"
                        "compliance: {mode: hard, hooks: [synthetic-check]}\n"
                        "voice: {default_tier: internal}\n"
                        "navigation: {default_workflow: cycle}\n")
        (self.repo / ".claude/profile-requirements.json").write_text(
            '{"schema_version":1,"required_pack":"strict"}')
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {selected}
""")
        result = json.loads(self.shell("""
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_resume first
"""))
        self.assertTrue(result["required_policy"]["required"])
        stamp = pack.stat()
        pack.write_text(pack.read_text().replace("hard", "off"))
        os.utime(pack, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        self.assertEqual(self.shell("""
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_resume first
""", expected=2), "")

    def test_cold_resume_does_not_recreate_missing_profile(self):
        selected, _ = self.make_map("chosen")
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {selected}
""")
        from native_paths import native_io_path
        from profile_context import ProfileConfig, context_path
        ref = json.loads(self.shell("state_cycle_field profile_reference"))
        home = Path(self.env["LINTEL_HOME"])
        config = ProfileConfig(ROOT, self.repo, home, home / "packs", home / "packs/active-pack",
                               context_id=ref["context_id"])
        current = native_io_path(context_path(config))
        current.unlink()
        self.assertEqual(self.shell("""
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_resume first
""", expected=2), "")
        self.assertFalse(current.exists())

    def test_two_initiatives_resume_and_append_to_original_history(self):
        first, _ = self.make_map("first")
        second, _ = self.make_map("second")
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {first}
state_phase_begin BUILD next=REVIEW
workflow_begin second research-dive {second}
state_phase_begin SENSE next=DEFINE
state_append SENSE DONE next=DEFINE
""")
        self.shell("""
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_resume first >/dev/null
state_phase_begin --retry BUILD next=REVIEW
state_append BUILD DONE next=REVIEW
test "$(state_phase_record BUILD "$(state_file)" first | state_field status)" = DONE
test "$(state_cycle_field work_map_path "$(state_file)" first)" = specs/first/work.json
test "$(state_resume_phase "$(state_file)" second)" = DEFINE
test -z "$(state_phase_record BUILD "$(state_file)" second)"
test "$(grep -c '^phase: CYCLE$' "$(state_file)")" = 2
""")

    def test_analysis_pointer_and_binding_ignore_stale_global_report(self):
        first, _ = self.make_map("first")
        second, _ = self.make_map("second")
        reports = self.repo / "reports"
        reports.mkdir()
        for name in ("first", "second"):
            (reports / f"{name}.md").write_text(
                f"# Analysis\nwork_map: specs/{name}/work.json\npackage: T014\nleaf: T014\n")
        legacy = self.repo / ".claude/runtime/state/analyze-report.md"
        legacy.parent.mkdir(parents=True)
        legacy.write_text("GREEN from an unrelated initiative; history only\n")
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {first}
state_append ANALYZE DONE analyze_report_path=reports/first.md
workflow_begin second full {second}
state_append ANALYZE DONE analyze_report_path=reports/second.md
""")
        inspect = """
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_resume first >/dev/null
report=$(state_cycle_field analyze_report_path)
workflow_inspect "$LINTEL_WORK_MAP" --package T014 --leaf T014 --acceptance "$report"
"""
        before = json.loads(self.shell(inspect))["binding"]
        self.assertEqual(before["work_map"], first)
        self.assertIn("reports/first.md", before["acceptance_paths"])
        self.assertNotIn("reports/second.md", before["acceptance_paths"])
        self.assertNotIn(".claude/runtime/state/analyze-report.md", before["acceptance_paths"])
        legacy.write_text("RED in still-unrelated global history\n")
        self.assertEqual(json.loads(self.shell(inspect))["binding"], before)
        (reports / "first.md").write_text("# Changed selected analysis\n")
        self.assertNotEqual(json.loads(self.shell(inspect))["binding"], before)

    def plan_analysis_blocks(self):
        text = (ROOT / "skills/plan/SKILL.md").read_text(encoding="utf-8")
        section = text.split("### Step 8 ", 1)[1].split("\n### Step 9 ", 1)[0]
        blocks = re.findall(r"```bash\n(.*?)\n```", section, re.S)
        self.assertEqual(len(blocks), 2, "PLAN Step 8 needs selected request and persisted-link blocks")
        self.assertNotIn("persists `.claude/runtime/state/analyze-report.md`", section)
        self.assertEqual(blocks[0].count("_workflow_guard_analyze_report_path "), 1)
        return blocks

    def produce_plan_analysis(self, cycle, selected):
        prepare, link = self.plan_analysis_blocks()
        self.env.update(LINTEL_CYCLE_ID=cycle, LINTEL_WORK_MAP=selected)
        # Only report prose is synthetic; selection, profile verification and linking are real.
        producer = r'''
workflow_inspect "$LINTEL_WORK_MAP" |
  "$LINTEL_PYTHON" -c '
import json, pathlib, sys
work = json.load(sys.stdin)
assert work["tasks"]["T014"] == work["packages"]["T014"]["leaves"]["T014"]
assert work["binding"] is None and work["release_clearance"] is False
identity = dict(report=sys.argv[1], work_map=work["work_map"], artifacts=work["artifacts"],
                package_id="T014", leaf_ids=["T014"], profile=json.loads(sys.argv[2]),
                required_policy=json.loads(sys.argv[3]))
report = pathlib.Path(sys.argv[1])
report.write_text("# analyze-report\ntrigger: plan-step8\n" +
                  "\n".join(key + ": " + json.dumps(value, sort_keys=True)
                            for key, value in identity.items() if key != "report") +
                  "\nlegs_checked: []\nlegs_incomplete: [synthetic prose; no semantic analysis]\n"
                  "verdict: INCOMPLETE\n", encoding="utf-8")
print(json.dumps(identity, sort_keys=True))
' "$analyze_report_path" "$LINTEL_PROFILE_REFERENCE" "$LINTEL_REQUIRED_POLICY"
'''
        result = json.loads(self.shell(prepare + "\n" + producer))
        self.env.update(analyze_cycle_id=cycle, analyze_work_map=selected,
                        analyze_report_path=result["report"], analyze_status="INCOMPLETE",
                        LINTEL_PROFILE_REFERENCE=json.dumps(result["profile"]),
                        LINTEL_REQUIRED_POLICY=json.dumps(result["required_policy"]))
        self.shell(link)
        return result

    def test_plan_analysis_caller_produces_selected_reports_and_retains_history(self):
        first, _ = self.make_map("first")
        second, second_map = self.make_map("second")
        second_map["status"] = "DRAFT"
        (self.repo / second).write_text(json.dumps(second_map))
        originals = {p: p.read_bytes() for p in (self.repo / "specs").rglob("*") if p.is_file()}
        legacy = self.repo / ".claude/runtime/state/analyze-report.md"
        legacy.parent.mkdir(parents=True)
        legacy.write_text("GREEN from unrelated global history; not current evidence\n")
        legacy_before = legacy.read_bytes()
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {first} operation=plan
state_phase_begin PLAN next=BUILD
workflow_begin second full {second} operation=plan
state_phase_begin PLAN next=BUILD
test -z "$(state_cycle_field analyze_report_path "$(state_file)" first)"
test -z "$(state_cycle_field analyze_report_path "$(state_file)" second)"
""")
        first_result = self.produce_plan_analysis("first", first)
        first_report = Path(first_result["report"])
        first_bytes = first_report.read_bytes()
        second_result = self.produce_plan_analysis("second", second)
        second_report = Path(second_result["report"])
        second_bytes = second_report.read_bytes()
        self.assertEqual(first_report.name, "first-analyze-report.md")
        self.assertEqual(second_report.name, "second-analyze-report.md")
        self.assertEqual(first_report.parent, legacy.parent)
        self.assertEqual(second_report.parent, legacy.parent)
        self.assertEqual(first_bytes, first_report.read_bytes())
        self.assertEqual(legacy_before, legacy.read_bytes())
        for result, selected in ((first_result, first), (second_result, second)):
            self.assertEqual(result["work_map"], selected)
            self.assertEqual(result["artifacts"]["tasks"], selected.replace("work.json", "tasks.md"))
            self.assertEqual(result["leaf_ids"], ["T014"])
            self.assertEqual(result["profile"]["generation"], 1)
            self.assertFalse(result["required_policy"]["required"])
        self.shell("""
test "$(state_cycle_field analyze_report_path "$(state_file)" first)" != \
     "$(state_cycle_field analyze_report_path "$(state_file)" second)"
test "$(state_resume_phase "$(state_file)" first)" = PLAN
test "$(state_resume_phase "$(state_file)" second)" = PLAN
test "$(grep -c '^phase: CYCLE$' "$(state_file)")" = 2
test "$(grep -c '^phase: ANALYZE$' "$(state_file)")" = 2
test "$(state_cycle_field status "$(state_file)" first)" = INCOMPLETE
test "$(state_cycle_field status "$(state_file)" second)" = INCOMPLETE
""")
        repeated = self.produce_plan_analysis("first", first)
        self.assertEqual(repeated, first_result)
        self.assertEqual(second_bytes, second_report.read_bytes())
        self.assertEqual(legacy_before, legacy.read_bytes())
        self.assertEqual(originals, {p: p.read_bytes() for p in (self.repo / "specs").rglob("*")
                                     if p.is_file()})
        acceptance = first_report.relative_to(self.repo).as_posix()
        self.env["ANALYZE_ACCEPTANCE"] = acceptance
        context = json.loads(self.shell("""
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_resume first >/dev/null
workflow_inspect "$LINTEL_WORK_MAP" --package T014 --leaf T014 \
  --acceptance "$ANALYZE_ACCEPTANCE"
"""))
        from review_contract import bind_work
        self.assertEqual(context["binding"], bind_work(
            self.repo, work_map=first, package_id="T014", leaf_ids=["T014"],
            acceptance_paths=[acceptance]))
        self.assertNotIn(str(legacy.relative_to(self.repo)).replace("\\", "/"),
                         context["binding"]["acceptance_paths"])
        self.assertFalse(context["release_clearance"])

    def test_plan_analysis_caller_refuses_map_mismatch_and_required_profile_drift(self):
        prepare, _ = self.plan_analysis_blocks()
        selected, _ = self.make_map("chosen")
        decoy, _ = self.make_map("decoy")
        pack = Path(self.env["LINTEL_HOME"]) / "packs/strict/pack.yaml"
        pack.parent.mkdir(parents=True)
        pack.write_text("name: strict\nversion: 1.0.0\n"
                        "compliance: {mode: hard, hooks: [synthetic-check]}\n"
                        "voice: {default_tier: internal}\n"
                        "navigation: {default_workflow: cycle}\n")
        (self.repo / ".claude/profile-requirements.json").write_text(
            '{"schema_version":1,"required_pack":"strict"}')
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {selected}
""")
        ledger = self.repo / ".claude/runtime/state/00-state.md"
        before = ledger.read_bytes()
        self.env.update(LINTEL_CYCLE_ID="first", LINTEL_WORK_MAP=decoy)
        self.assertEqual(self.shell(prepare, expected=2), "")
        self.assertIn("different initiative", self.last_stderr)
        self.assertEqual(before, ledger.read_bytes())
        self.env["LINTEL_WORK_MAP"] = selected
        self.shell(prepare + '\ntest "$LINTEL_REQUIRED_POLICY" != "{}"\n')
        stamp = pack.stat()
        pack.write_text(pack.read_text().replace("hard", "off"))
        os.utime(pack, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        self.assertEqual(self.shell(prepare, expected=2), "")
        self.assertIn("PROFILE_DRIFT", self.last_stderr)
        self.assertEqual(before, ledger.read_bytes())
        self.assertFalse(list(ledger.parent.glob("*analyze-report.md")))

    def test_plan_analysis_caller_refuses_legacy_global_link(self):
        prepare, _ = self.plan_analysis_blocks()
        selected, _ = self.make_map("chosen")
        legacy = self.repo / ".claude/runtime/state/analyze-report.md"
        legacy.parent.mkdir(parents=True)
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {selected}
""")
        self.env.update(LINTEL_CYCLE_ID="first", LINTEL_WORK_MAP=selected)
        ledger = legacy.parent / "00-state.md"
        for present in (False, True):
            if present:
                legacy.write_text("GREEN from unrelated global history\n")
            for path in (legacy.relative_to(self.repo).as_posix(), legacy.as_posix(), str(legacy)):
                with self.subTest(path=path, present=present):
                    self.env["LEGACY_REPORT"] = path
                    self.shell('state_append ANALYZE DONE analyze_report_path="$LEGACY_REPORT"\n')
                    before = {p: p.read_bytes() for p in ledger.parent.iterdir() if p.is_file()}
                    self.assertEqual(self.shell(prepare, expected=2), "")
                    self.assertIn("legacy global analysis is history", self.last_stderr)
                    self.assertEqual(before, {p: p.read_bytes() for p in ledger.parent.iterdir()
                                              if p.is_file()})

    def test_plan_analysis_identity_keeps_distinct_same_basename_parent(self):
        prepare, _ = self.plan_analysis_blocks()
        selected, _ = self.make_map("chosen")
        alternate = self.repo / "reports/analyze-report.md"
        alternate.parent.mkdir()
        legacy = self.repo / ".claude/runtime/state/analyze-report.md"
        legacy.parent.mkdir(parents=True)
        legacy.write_text("GREEN from unrelated global history\n")
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {selected}
""")
        self.env.update(LINTEL_CYCLE_ID="first", LINTEL_WORK_MAP=selected)
        for present in (False, True):
            if present:
                alternate.write_text("INCOMPLETE selected report in a distinct directory\n")
            for path in (alternate.relative_to(self.repo).as_posix(), alternate.as_posix(), str(alternate)):
                with self.subTest(path=path, present=present):
                    self.env["SELECTED_REPORT"] = path
                    self.shell('state_append ANALYZE INCOMPLETE "analyze_report_path=$SELECTED_REPORT"\n')
                    before = {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
                    out = self.shell('cd "$LINTEL_HOME"\n' + prepare +
                                     '\nprintf "%s" "$analyze_report_path"\n')
                    self.assertEqual(out, path)
                    self.assertFalse(alternate.parent.samefile(legacy.parent))
                    self.assertEqual(before, {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()})

    def test_plan_analysis_identity_refuses_unproven_or_undeclared_parent(self):
        prepare, _ = self.plan_analysis_blocks()
        selected, _ = self.make_map("chosen")
        outside = Path(self.temp.name) / "not-an-authorized-report-root"
        outside.mkdir()
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {selected}
""")
        self.env.update(LINTEL_CYCLE_ID="first", LINTEL_WORK_MAP=selected)
        for path in ((outside / "analyze-report.md").as_posix(),
                     "not-created/selected-analyze-report.md"):
            with self.subTest(path=path):
                self.env["SELECTED_REPORT"] = path
                self.shell('state_append ANALYZE INCOMPLETE "analyze_report_path=$SELECTED_REPORT"\n')
                before = {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
                self.assertEqual(self.shell(prepare, expected=2), "")
                self.assertIn("INCOMPLETE", self.last_stderr)
                self.assertEqual(before, {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()})
                self.assertFalse((self.repo / "not-created").exists())
                self.assertEqual(list(outside.iterdir()), [])

    def test_plan_analysis_identity_uses_existing_case_identity(self):
        prepare, _ = self.plan_analysis_blocks()
        selected, _ = self.make_map("chosen")
        legacy = self.repo / ".claude/runtime/state/analyze-report.md"
        legacy.parent.mkdir(parents=True)
        legacy.write_text("GREEN from unrelated global history\n")
        alternate = legacy.with_name("ANALYZE-REPORT.md")
        case_sensitive = not alternate.exists()
        if case_sensitive:
            alternate.write_text("INCOMPLETE distinct case-sensitive selected report\n")
        self.assertEqual(alternate.samefile(legacy), not case_sensitive)
        print(f"PLAN case-sensitive existing pair observed: {case_sensitive}", flush=True)
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {selected}
""")
        self.env.update(LINTEL_CYCLE_ID="first", LINTEL_WORK_MAP=selected,
                        SELECTED_REPORT=alternate.as_posix())
        self.shell('state_append ANALYZE INCOMPLETE "analyze_report_path=$SELECTED_REPORT"\n')
        before = {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
        out = self.shell(prepare + '\nprintf "%s" "$analyze_report_path"\n',
                         expected=0 if case_sensitive else 2)
        if case_sensitive:
            self.assertEqual(out, alternate.as_posix())
        else:
            self.assertEqual(out, "")
            self.assertIn("legacy global analysis is history", self.last_stderr)
        self.assertEqual(before, {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()})

    def test_plan_analysis_identity_refuses_denied_probe(self):
        prepare, _ = self.plan_analysis_blocks()
        selected, _ = self.make_map("chosen")
        report = self.repo / "reports/selected.md"
        report.parent.mkdir()
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {selected}
""")
        bootstrap = Path(self.temp.name) / "deny_identity.py"
        bootstrap.write_text('''import os
from pathlib import Path
import sys
script = sys.stdin.read()
sys.argv = sys.argv[1:]
parent = Path(sys.argv[4]).parent
real_stat = os.stat
def deny(path, *args, **kwargs):
    if isinstance(path, (str, os.PathLike)) and Path(path) == parent:
        raise PermissionError("synthetic identity access denied")
    return real_stat(path, *args, **kwargs)
os.stat = deny
exec(compile(script, "<actual workflow identity guard>", "exec"), {"__name__": "__main__"})
''', encoding="utf-8")
        wrapper = Path(self.temp.name) / "deny-identity.sh"
        wrapper.write_bytes(b'''#!/usr/bin/env bash
if [ "${1:-}" = - ]; then
  exec "$LINTEL_PYTHON" "$IDENTITY_FAULT_BOOTSTRAP" "$@"
fi
exec "$LINTEL_PYTHON" "$@"
''')
        wrapper.chmod(0o700)
        self.env.update(LINTEL_CYCLE_ID="first", LINTEL_WORK_MAP=selected,
                        SELECTED_REPORT=report.as_posix())
        self.shell('state_append ANALYZE INCOMPLETE "analyze_report_path=$SELECTED_REPORT"\n')
        self.env.update(_LINTEL_PROFILE_PYTHON=wrapper.as_posix(),
                        IDENTITY_FAULT_BOOTSTRAP=bootstrap.as_posix())
        before = {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
        self.assertEqual(self.shell(prepare, expected=2), "")
        self.assertIn("INCOMPLETE", self.last_stderr)
        self.assertIn("synthetic identity access denied", self.last_stderr)
        self.assertEqual(before, {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()})

    def test_plan_analysis_identity_handles_absent_native_case_alias(self):
        prepare, _ = self.plan_analysis_blocks()
        selected, _ = self.make_map("chosen")
        legacy = self.repo / ".claude/runtime/state/analyze-report.md"
        alternate = legacy.with_name("ANALYZE-REPORT.md")
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {selected}
""")
        self.env.update(LINTEL_CYCLE_ID="first", LINTEL_WORK_MAP=selected,
                        SELECTED_REPORT=str(alternate))
        self.shell('state_append ANALYZE INCOMPLETE "analyze_report_path=$SELECTED_REPORT"\n')
        before = {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
        out = self.shell(prepare + '\nprintf "%s" "$analyze_report_path"\n',
                         expected=2)
        self.assertEqual(out, "")
        self.assertIn("Absent report names may alias", self.last_stderr)
        self.assertEqual(before, {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()})
        self.assertFalse(legacy.exists())
        self.assertFalse(alternate.exists())

    def test_plan_analysis_identity_honors_declared_state_root(self):
        prepare, _ = self.plan_analysis_blocks()
        selected, _ = self.make_map("chosen")
        declared = Path(self.temp.name) / "declared-state"
        self.env["LINTEL_STATE_DIR"] = declared.as_posix()
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {selected}
""")
        self.env.update(LINTEL_CYCLE_ID="first", LINTEL_WORK_MAP=selected)
        before = {p: p.read_bytes() for p in declared.iterdir() if p.is_file()}
        out = self.shell(prepare + '\nprintf "%s" "$analyze_report_path"\n')
        self.assertEqual(Path(out), declared / "first-analyze-report.md")
        self.assertEqual(before, {p: p.read_bytes() for p in declared.iterdir() if p.is_file()})
        legacy = declared / "analyze-report.md"
        self.env["SELECTED_REPORT"] = str(legacy)
        self.shell('state_append ANALYZE INCOMPLETE "analyze_report_path=$SELECTED_REPORT"\n')
        before = {p: p.read_bytes() for p in declared.iterdir() if p.is_file()}
        self.assertEqual(self.shell(prepare, expected=2), "")
        self.assertIn("legacy global analysis is history", self.last_stderr)
        self.assertEqual(before, {p: p.read_bytes() for p in declared.iterdir() if p.is_file()})
        self.assertFalse(legacy.exists())

    def test_plan_analysis_link_refuses_missing_persistence(self):
        prepare, link = self.plan_analysis_blocks()
        selected, _ = self.make_map("chosen")
        self.shell(f"""
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
lintel_copilot_env "$LINTEL_REPO_ROOT"
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_begin first full {selected}
""")
        ledger = self.repo / ".claude/runtime/state/00-state.md"
        before = ledger.read_bytes()
        self.env.update(LINTEL_CYCLE_ID="first", LINTEL_WORK_MAP=selected)
        self.assertEqual(self.shell(prepare + "\nanalyze_status=INCOMPLETE\n" + link, expected=2), "")
        self.assertIn("analysis report was not persisted", self.last_stderr)
        self.assertEqual(before, ledger.read_bytes())
        self.assertFalse(list(ledger.parent.glob("*analyze-report.md")))


class LifecycleRecoveryTests(FixtureCase):
    def test_resume_uses_selected_range_not_a_phase_default_hint(self):
        self.shell("""
state_cycle_begin first hotfix 'phases_selected=SENSE BUILD REVIEW SHIP'
state_phase_begin SENSE next=BUILD
state_append SENSE DONE next=SCOPE
test "$(state_resume_phase)" = BUILD
source "$LINTEL_SOURCE_ROOT/lib/cycle-footer.sh"
footer=$(render_cycle_footer --compact)
case "$footer" in *'next **`BUILD`**'*) : ;; *) exit 97 ;; esac
""")

    def test_unresolved_scope_uses_real_needs_context_state(self):
        (self.repo / "scope.md").write_text("size: XL\nambiguous: yes\n")
        setup = """
scale_size=XL scale_amb=yes depth_schema=tree resolved_intent=deploy
override_route=DEFINE scope_decision_resolved=no
scope_out="$LINTEL_REPO_ROOT/scope.md"
"""
        self.shell(setup + skill_block("scope", "### Step 6 ") +
                   '\ntest "$(state_last status)" = NEEDS_CONTEXT\n'
                   'test "$(state_last next_recommended)" = SCOPE\n')

    def test_truncated_done_transition_stays_incomplete(self):
        self.shell("""
state_cycle_begin first full
state_phase_begin BUILD next=REVIEW
state_append BUILD DONE next=REVIEW note=last-field
""")
        ledger = self.repo / ".claude/runtime/state/00-state.md"
        ledger.write_bytes(b"\n".join(ledger.read_bytes().splitlines()[:-1]) + b"\n")
        self.assertEqual(self.shell("state_resume_phase").strip(), "BUILD")

    def test_operator_metadata_cannot_forge_a_completed_phase(self):
        self.shell("""
state_cycle_begin first full
LINTEL_OPERATOR=$'fixture\\nphase: SHIP\\nstatus: DONE' state_append BUILD BLOCKED next=REVIEW
test "$(state_resume_phase)" = BUILD
test "$(state_last phase)" = BUILD
""")

    def test_cycle_read_error_cannot_become_a_fresh_start(self):
        self.shell("""
state_cycle_begin first full
before=$(cat "$(state_file)")
awk() { return 2; }
if state_cycle_begin second full; then exit 98; fi
unset -f awk
test "$(cat "$(state_file)")" = "$before"
""")

    def test_resume_ignores_metadata_and_retains_loop_back(self):
        self.shell("""
state_cycle_begin first full
state_phase_begin PLAN next=BUILD
state_append PLAN DONE next=BUILD
state_phase_begin BUILD next=REVIEW
state_append BUILD BLOCKED next=REVIEW
state_append RESUME DONE note=inspected
test "$(state_resume_phase)" = BUILD
state_phase_begin --retry PLAN next=BUILD
test "$(state_resume_phase)" = PLAN
state_append PLAN DONE next=BUILD
test "$(state_resume_phase)" = BUILD
""")

    def test_failed_state_write_and_field_injection_are_errors(self):
        self.shell("""
mkdir -p "$(dirname "$(state_file)")"
mkdir "$(state_file)"
if state_append BUILD STARTING 2>/dev/null; then exit 92; fi
""")
        self.shell("""
rmdir "$(state_file)"
if state_append BUILD STARTING 'status=DONE' 2>/dev/null; then exit 93; fi
test ! -e "$(state_file)"
""")

    def test_selected_phase_range_never_duplicates_entry(self):
        self.shell("""
test "$(state_cycle_phases full PLAN BUILD)" = "$(printf 'PLAN\\nBUILD')"
test "$(state_cycle_phases research-dive)" = "$(printf 'SENSE\\nDEFINE\\nDISCOVER')"
test "$(state_cycle_phases full SENSE DEFINE SCOPE)" = "$(printf 'SENSE\\nDEFINE')"
test "$(state_cycle_phases full | grep -c '^SENSE$')" = 1
test "$(state_cycle_phases full | grep -c '^SCOPE$')" = 1
if state_cycle_phases full BUILD PLAN; then exit 94; fi
if state_cycle_phases full SENSE CAPTURE BOGUS; then exit 95; fi
""")

    def test_real_discover_snippets_find_content_and_adr_conventions(self):
        for suffix in ("ts", "js", "py", "go", "rs"):
            path = self.repo / "src" / f"ordinary file.{suffix}"
            path.parent.mkdir(exist_ok=True)
            path.write_text("fixture topic exists only in content\n")
        (self.repo / "docs").mkdir()
        (self.repo / "docs/ordinary.md").write_text("fixture topic\n")
        out = json.loads(self.shell(
            "keyword=fixture\n" + skill_block("discover", "### Step 1 ")))
        self.assertEqual(len(out["files"]), 6)
        self.assertEqual(out["status"], "selected")
        decisions = self.repo / ".claude/decisions"
        decisions.mkdir()
        for number, text in enumerate((
            "# fixture accepted\n- **Status:** Accepted\n- **Date:** 2026-09-20\n",
            "---\nstatus: Proposed\ndate: 2026-09-19\n---\n# fixture proposal\n",
            "# fixture old\n**Status:** Superseded\n",
            "# fixture unknown\nStatus needs reconciliation.\n",
        ), 1):
            (decisions / f"{number:04}-fixture.md").write_text(text)
        out = json.loads(self.shell(
            "keyword=fixture\n" + skill_block("discover", "### Step 2 ")))
        self.assertEqual([f["adr"]["status"] for f in out["files"]],
                         ["accepted", "proposed", "superseded", "unknown"])

    def test_real_discover_inventory_uses_source_and_future_categories(self):
        source = Path(self.temp.name) / "trusted inventory"
        for category in ("engineering", "future-domain"):
            folder = source / "agents" / category
            folder.mkdir(parents=True)
            (folder / "Role with spaces.md").write_text("description: fixture inventory\n")
        decoy = self.repo / "agents/target-decoy"
        decoy.mkdir(parents=True)
        (decoy / "Wrong.md").write_text("description: never read this target as the canonical inventory\n")
        log = Path(self.temp.name) / "inventory-read.txt"
        self.env.update(PROBE_SOURCE=source.as_posix(), PROBE_LOG=log.as_posix())
        self.shell("""
LINTEL_SOURCE_ROOT="$PROBE_SOURCE"
grep() { printf '%s\\n' "${@: -1}" >> "$PROBE_LOG"; command grep "$@"; }
""" + skill_block("discover", "### Step 6 "))
        read = log.read_text()
        self.assertIn("future-domain/Role with spaces.md", read)
        self.assertIn("engineering/Role with spaces.md", read)
        self.assertNotIn("target-decoy", read)

    def test_jobs_reader_keeps_blocked_old_and_unknown_without_writes(self):
        jobs = self.repo / ".claude/runtime/jobs"
        for name, stamp in (("blocked", "2020-01-01T00:00:00Z"), ("unknown", "invalid"), ("missing", None)):
            folder = jobs / name
            folder.mkdir(parents=True)
            (folder / "job.yaml").write_text(
                f"job_id: {name}\nworkflow: cycle\nstatus: BLOCKED\n"
                "current_step: BUILD\n" + (f"last_touched: {stamp}\n" if stamp else "") + "steps: []\n")
        (jobs / "_active.md").write_text("_No active jobs._\n")
        before = {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
        out = self.shell("""
export LINTEL_JOBS_NO_INIT=1
source "$LINTEL_SOURCE_ROOT/bin/_jobs.sh"
list_jobs --read-only
stale_jobs 24
""")
        self.assertIn("blocked", out)
        self.assertIn("BLOCKED", out)
        self.assertIn("unknown", out)
        self.assertIn("age-unknown", out)
        self.assertIn("missing timestamp", out)
        self.assertEqual(before, {p: p.read_bytes() for p in self.repo.rglob("*") if p.is_file()})
        self.assertFalse(Path(self.env["LINTEL_HOME"]).exists())

    def test_context_interpreter_floor_supported_and_unsupported_probes(self):
        # This injects the probe result; it does not claim actual Python 3.9 execution.
        self.shell("""
source "$LINTEL_SOURCE_ROOT/bin/_context.sh"
python3() {
  if [ "$1" = -c ]; then
    [ "$2" = 'import sys; assert sys.version_info >= (3, 9)' ]
  else
    printf 'selected-supported-probe'
  fi
}
python() { return 1; }
test "$(_context_run budget)" = selected-supported-probe
python3() { return 1; }
if _context_run budget; then exit 96; fi
""")

    def test_host_question_binding_not_a_fixed_tool_or_permission_bypass(self):
        from client_capabilities import load_registry, resolve
        registry = load_registry(ROOT / "lib/cli-tiers.yaml")
        session = dict(schema_version=1, session_id="synthetic-intake", surface="other",
                       profile_ref=None, work_map="selected/work.json",
                       isolation=dict(kind="none", attributable=False), bindings={})
        self.assertEqual(resolve(registry, session)["operations"]["question"]["mode"], "conversation")
        session["bindings"]["question"] = dict(tool="host.actual_question", available=True, permission="allowed")
        actual = resolve(registry, session)
        self.assertEqual(actual["operations"]["question"]["tool"], "host.actual_question")
        self.assertFalse(actual["executed"])
        session["bindings"]["question"]["permission"] = "denied"
        self.assertEqual(resolve(registry, session)["operations"]["question"]["mode"], "blocked")


class ReviewSnippetTests(REVIEW_FIXTURE["Fixture"]):
    def test_actual_plan_review_snippet_to_latest_qa_ship(self):
        self.record()
        self.review["skill"] = "plan-eng-review"
        self.corroborate()
        self.write_json(self.request["record_path"], self.review)
        self.env.update(review_record=self.record_file.as_posix(),
                        review_context=self.expected_file.as_posix(),
                        corroboration=self.observed_file.as_posix())
        snippet = skill_block("plan-eng-review", "Persist via first-party")
        self.run_command(["bash", "-c", snippet], ok=0)
        self.read(skill="plan-eng-review", ok=0)
        self.assertEqual(self.qa().returncode, 0)
        self.cli("ship", "--repo", self.repo, "--expected", self.expected_file,
                 "--corroboration", self.observed_file, "--qa", self.qa_file,
                 "--skill", "plan-eng-review", ok=0)
        # Actual later rejecting writer revokes the earlier positive result.
        self.review["status"] = "fail"
        self.corroborate()
        self.write_json(self.request["record_path"], self.review)
        self.run_command(["bash", "-c", snippet], ok=3)
        self.read(skill="plan-eng-review", ok=3)
        self.cli("ship", "--repo", self.repo, "--expected", self.expected_file,
                 "--corroboration", self.observed_file, "--qa", self.qa_file,
                 "--skill", "plan-eng-review", ok=3)


if __name__ == "__main__":
    unittest.main(argv=[__file__, *remaining])
