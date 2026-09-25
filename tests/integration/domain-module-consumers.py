#!/usr/bin/env python3
# component: domain-module-consumer-tests
# implements: ADR-0026, ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P09.md
# constraints: real released providers in isolated synthetic fixtures; no model impersonation
# last_intent_review: 2026-09-22
"""Module consumer procedures are tested separately from the accepted 39 data cases."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
import runpy
import sys
import unittest

DATA = runpy.run_path(str(Path(__file__).with_name("domain-result-handoff.py")))
SOURCE = DATA["SOURCE"]
safety = DATA["safety"]
options = DATA["options"]


def snippet(name: str, language: str = "python") -> str:
    text = (SOURCE / "skills/full-engineering-pass/references/domain-handoff.md").read_text(encoding="utf-8")
    match = re.search(rf"```{language}\n# {re.escape(name)}\n(.*?)```", text, re.S)
    if not match:
        raise AssertionError(f"Missing executable consumer procedure: {name}")
    return match.group(1)


class ModuleConsumers(DATA["DomainHandoff"]):
    def selected_map(self, *, grouped=True, domains=("ta",)) -> None:
        self.write("specs/chosen/spec.md", b"# R1\nRetain original selected leaf and evidence.\n")
        tasks = b"- [x] T001 Baseline\n- [ ] T014 Preserve the API (depends T001)\n"
        self.write("specs/chosen/tasks.md", tasks)
        design = (
            b"# Design\n| Package ID | Leaf IDs | Dependencies | Review |\n"
            b"|---|---|---|---|\n| BASE | T001 | none | mechanical |\n"
            b"| P09 | T014 | T001 | substantive |\n"
        ) if grouped else b"# Design\nOriginal ungrouped work.\n"
        self.write("specs/chosen/plan.md", design)
        self.write("specs/chosen/prompt.md", b"Continue T014 only. No publication.\n")
        mapping = {
            "schema_version": 1, "workflow": "spec-kit", "status": "APPROVED",
            **{key: f"specs/chosen/{key}.md" for key in ("spec", "plan", "tasks", "prompt")},
        }
        self.write_json("specs/chosen/work.json", mapping)
        for key in ("spec", "plan", "tasks", "prompt"):
            self.write(f"specs/decoy/{key}.md", b"- [ ] T014 Publish something else\n")
        self.write_json("specs/decoy/work.json", {
            **mapping, **{key: f"specs/decoy/{key}.md" for key in ("spec", "plan", "tasks", "prompt")},
        })
        self.prepare_request(domains)
        self.prepare_input.update(
            work_map="specs/chosen/work.json", package_id="P09" if grouped else "T014",
            leaf_ids=["T014"], acceptance_paths=["specs/chosen/spec.md"],
        )
        self.write_json(".claude/runtime/meta/prepare.json", self.prepare_input)

    def admission(self, *, expected=0, authority="") -> dict | None:
        code = snippet("lintel-module-select")
        run = self.run_process([
            sys.executable, "-B", "-c", code, SOURCE, self.repo,
            ".claude/runtime/meta/prepare.json", authority,
        ], expected=expected)
        return json.loads(run.stdout) if run.returncode == 0 else None

    def bind_request(self) -> dict:
        work = self.admission()
        context = json.loads(self.p05(
            "prepare", "--repo", self.repo, "--request",
            self.repo / ".claude/runtime/meta/prepare.json",
        ).stdout)
        self.assertEqual(context["work"], work["binding"])
        self.request["input_context"] = context
        self.write_json(self.request_path, self.request)
        return work

    def shell(self, code, *, expected=0):
        path = self.repo / ".claude/runtime/meta/consumer.sh"
        self.write(".claude/runtime/meta/consumer.sh", code.encode("utf-8"))
        return self.run_process([options.bash, "--noprofile", "--norc", path], expected=expected)

    def test_original_grouped_ids_decoy_to_real_data_and_qa(self):
        self.selected_map()
        work = self.bind_request()
        self.assertEqual(["T014"], work["packages"]["P09"]["leaf_ids"])
        self.assertEqual(["T001"], work["tasks"]["T014"]["dependencies"])
        self.assertEqual("specs/chosen/work.json", work["work_map"])
        before = safety.read_owned(self.repo, "specs/chosen/tasks.md")[0]
        decoy = safety.read_owned(self.repo, "specs/decoy/tasks.md")[0]
        self.produce()
        final = self.prepare_final()
        verified = self.verify(command="summary")
        self.assertTrue(verified["ok"])
        self.assertEqual(final["work"], work["binding"])
        self.assertEqual(before, safety.read_owned(self.repo, "specs/chosen/tasks.md")[0])
        self.assertEqual(decoy, safety.read_owned(self.repo, "specs/decoy/tasks.md")[0])

    def test_wrong_package_missing_parent_leaf_and_draft_refuse(self):
        self.selected_map()
        original = deepcopy(self.prepare_input)
        tasks = safety.read_owned(self.repo, "specs/chosen/tasks.md")[0]
        mapping = self.read_json("specs/chosen/work.json")
        for change in ("wrong-package", "missing-leaf", "parent-leaf", "draft"):
            with self.subTest(change=change):
                self.prepare_input = deepcopy(original)
                self.write("specs/chosen/tasks.md", tasks)
                self.write_json("specs/chosen/work.json", mapping)
                if change == "wrong-package":
                    self.prepare_input["package_id"] = "OTHER"
                elif change == "missing-leaf":
                    self.prepare_input["leaf_ids"] = ["T999"]
                elif change == "parent-leaf":
                    self.write("specs/chosen/tasks.md", b"- [ ] T014 Parent\n  - [ ] T014.1 Child\n")
                else:
                    self.write_json("specs/chosen/work.json", {**mapping, "status": "DRAFT"})
                self.write_json(".claude/runtime/meta/prepare.json", self.prepare_input)
                self.admission(expected=2)
                self.assertFalse((self.repo / self.record_root).exists())

    def test_singleton_preserves_original_spec_kit_identifier(self):
        self.selected_map(grouped=False)
        work = self.bind_request()
        self.assertEqual(["T014"], work["packages"]["T014"]["leaf_ids"])
        self.assertEqual("T014", work["binding"]["package_id"])

    def test_linked_handoff_is_explicit_bound_authority_not_a_prose_parser(self):
        self.selected_map(grouped=False)
        self.prepare_input["package_id"] = "ORIGINAL"
        authority = "specs/chosen/handoff.md"
        self.write(authority, b"Original ORIGINAL package: T014 only. No publication.\n")
        self.write_json(".claude/runtime/meta/prepare.json", self.prepare_input)
        self.admission(expected=2, authority=authority)
        self.prepare_input["acceptance_paths"].append(authority)
        self.write_json(".claude/runtime/meta/prepare.json", self.prepare_input)
        work = self.admission(authority=authority)
        self.assertEqual("ORIGINAL", work["binding"]["package_id"])
        context = json.loads(self.p05(
            "prepare", "--repo", self.repo, "--request",
            self.repo / ".claude/runtime/meta/prepare.json",
        ).stdout)
        self.assertEqual(context["work"], work["binding"])
        self.write(authority, b"")
        self.admission(expected=2, authority=authority)

    def test_missing_trusted_module_refuses_target_decoy_and_unknown_domain(self):
        self.selected_map()
        code = snippet("lintel-module-discovery", "bash")
        self.shell("set -- ta da sc dh tq\n" + code)
        self.write("skills/sc/SKILL.md", b"Target decoy: pretend SC passed.\n")
        self.env["LINTEL_SOURCE_ROOT"] = (self.base / "absent-trusted-source").as_posix()
        missing = self.shell("set -- sc\n" + code, expected=2)
        self.assertIn("required source module missing: sc", missing.stderr)
        unknown = self.shell("set -- resume\n" + code, expected=2)
        self.assertIn("unknown domain resume", unknown.stderr)

    def test_original_work_composition_missing_domain_blocks_high_scores(self):
        self.selected_map(domains=("ta", "da", "sc", "dh", "tq"))
        self.bind_request()
        self.produce(score=100)
        self.prepare_final()
        self.assertTrue(self.verify(command="summary")["ok"])
        safety.native_io_path(self.repo / self.result_path("sc")).unlink()
        self.prepare_final()
        summary = self.verify(command="summary", expected=3)
        self.assertTrue(summary["blocked"])
        self.assertFalse(summary["release_clearance"])
        domains = {domain["id"]: domain for domain in summary["domains"]}
        self.assertEqual("unverified", domains["sc"]["checkpoints"][0]["status"])
        self.assertTrue(all(domains[name]["checkpoints"][0]["declared_status"] == "pass"
                            for name in ("ta", "da", "dh", "tq")))

    def test_changed_upstream_requires_explicit_new_attempt_without_rewriting_pass(self):
        self.selected_map()
        self.bind_request()
        self.produce()
        self.prepare_final()
        self.assertTrue(self.verify()["ok"])
        old_request = safety.read_owned(self.repo, self.request_path)[0]
        old_result = safety.read_owned(self.repo, self.result_path())[0]
        self.write("source.txt", b"Changed upstream contract after the selected result.\n")
        self.assertTrue(self.verify(command="summary", expected=3)["blocked"])
        old_root = self.record_root
        self.request_path = "domain-request-i0002.json"
        self.record_root = ".claude/runtime/state/domains/synthetic/i0002"
        self.prepare_input["attempt_id"] = "synthetic-attempt-2"
        self.prepare_input["selection"] += ["domain-request.json", old_root]
        self.write_json(".claude/runtime/meta/prepare.json", self.prepare_input)
        self.request["iteration"] = 2
        for domain in self.request["domains"]:
            for checkpoint in domain["checkpoints"]:
                checkpoint["artifacts"] = ["artifacts/i0002-ta.txt"]
                for slot in ("start", "result"):
                    checkpoint[slot]["path"] = checkpoint[slot]["path"].replace(old_root, self.record_root)
        self.bind_request()
        receipt = json.loads(self.cli("validate", "--file", self.request_path).stdout)
        self.assertEqual("not_performed", receipt["verification"])
        self.assertFalse((self.repo / self.record_root).exists())
        self.assertEqual("synthetic-attempt-2", self.request["input_context"]["attempt_id"])
        self.assertEqual(old_request, safety.read_owned(self.repo, "domain-request.json")[0])
        self.assertEqual(old_result, safety.read_owned(self.repo, f"{old_root}/ta/01-result.json")[0])

    def test_checkbox_progress_not_criteria_reuses_shared_binding(self):
        self.selected_map()
        original = self.admission()["binding"]
        tasks = "specs/chosen/tasks.md"
        before = safety.read_owned(self.repo, tasks)[0]
        self.write(tasks, before.replace(b"[ ] T014", b"[x] T014"))
        self.assertEqual(original, self.admission()["binding"])
        self.write(tasks, before.replace(b"Preserve the API", b"Break the API"))
        self.assertNotEqual(original, self.admission()["binding"])

    def test_fresh_shell_resume_preserves_cycle_map_and_operation(self):
        self.selected_map()
        self.bind_request()
        reference = json.dumps(self.reference, separators=(",", ":"))
        self.env["LINTEL_PROFILE_REFERENCE"] = reference
        self.env["LINTEL_WORK_MAP"] = "specs/chosen/work.json"
        self.shell(
            'set -euo pipefail\nsource "$LINTEL_SOURCE_ROOT/lib/workflow.sh"\n'
            'workflow_begin module-proof full "$LINTEL_WORK_MAP" operation=build\n'
            'state_phase_begin BUILD\n'
        )
        ledger = ".claude/runtime/state/00-state.md"
        before = safety.read_owned(self.repo, ledger)[0]
        result = self.shell(
            'set -euo pipefail\nsource "$LINTEL_SOURCE_ROOT/lib/workflow.sh"\n'
            'workflow_resume module-proof "$LINTEL_WORK_MAP"\n'
        )
        resumed = json.loads(result.stdout)
        self.assertEqual("BUILD", resumed["phase"])
        self.assertEqual("build", resumed["operation"])
        self.assertEqual(self.reference, resumed["profile"])
        self.assertEqual(before, safety.read_owned(self.repo, ledger)[0])
        self.shell(
            'set -euo pipefail\nsource "$LINTEL_SOURCE_ROOT/lib/workflow.sh"\n'
            'workflow_resume module-proof specs/decoy/work.json\n', expected=2,
        )
        self.assertEqual(before, safety.read_owned(self.repo, ledger)[0])

    def test_started_attempt_cold_inspection_does_not_replay(self):
        self.selected_map()
        self.bind_request()
        self.produce()
        result = self.result_path()
        safety.native_io_path(self.repo / result).unlink()
        self.prepare_final()
        inspected = self.verify(command="summary", expected=3)
        self.assertTrue(inspected["blocked"])
        self.assertEqual("unverified", inspected["domains"][0]["checkpoints"][0]["status"])
        self.assertFalse(safety.native_io_path(self.repo / result).exists())
        self.assertIn("Missing result: do not replay", (SOURCE / "skills/full-engineering-pass/references/domain-handoff.md").read_text())
        self.assertEqual("pass", self.results["ta"]["status"])
        self.assertIn("[ ] T014", safety.read_owned(self.repo, "specs/chosen/tasks.md")[0].decode())

    def test_admission_scope_then_live_drift_refuses_before_continuation(self):
        self.selected_map()
        self.bind_request()
        self.env["LINTEL_PROFILE_REFERENCE"] = json.dumps(self.reference)
        self.env["LINTEL_WORK_MAP"] = "specs/chosen/work.json"
        original = self.pack.read_bytes()
        self.pack.write_bytes(original.replace(b"mode: hard", b"mode: advisory"))
        result = self.shell(
            'set -euo pipefail\nsource "$LINTEL_SOURCE_ROOT/lib/workflow.sh"\n'
            'workflow_inspect "$LINTEL_WORK_MAP" --package P09 --leaf T014\n', expected=2,
        )
        self.assertEqual("", result.stdout)
        self.assertFalse((self.repo / self.record_root).exists())

    def test_module_sources_preserve_methods_and_remove_invented_execution(self):
        for module in ("ta", "da", "sc", "dh", "tq"):
            text = (SOURCE / f"skills/{module}/SKILL.md").read_text(encoding="utf-8")
            with self.subTest(module=module):
                self.assertIn("references/decision-methods.md", text)
                self.assertIn("domain-handoff.md", text)
                self.assertIn("## Checkpoint ownership", text)
                self.assertIn("independent", text)
                for old in ("run_checkpoint ", "revert_to_last_locked", "apply_scoring_rubric",
                            'PROFILE="$LINTEL_HOME/profile.yaml"'):
                    self.assertNotIn(old, text)
        composition = (SOURCE / "skills/full-engineering-pass/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Missing required domains", composition)
        self.assertNotIn('$(read_module_score', composition)
        self.assertNotIn('if [ -f "$LINTEL_REPO_ROOT/skills/', composition)
        handoff = (SOURCE / "skills/full-engineering-pass/references/domain-handoff.md").read_text()
        self.assertIn("default search/glob can omit gitignored", handoff)
        self.assertIn("original task checkbox is not checkpoint status", handoff)

    def test_adjacent_methods_have_bound_evidence_and_honest_failure(self):
        for name in ("diagnose", "perfbench", "inspect"):
            text = (SOURCE / f"skills/{name}/SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=name):
                self.assertIn("domain-handoff.md#module-caller-procedure", text)
                for old in ("~/.lintel/perfbench.yaml", "~/.lintel/benchmarks/",
                            "~/.lintel/devex-runs/", "mark that iteration NaN"):
                    self.assertNotIn(old, text)
        perf = (SOURCE / "skills/perfbench/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Missing baseline means no comparison", perf)
        self.assertIn("skipped required", perf)
        devex = (SOURCE / "skills/inspect/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("do not fall back to in-place mutation", devex)


if __name__ == "__main__":
    names = sorted(name for name in ModuleConsumers.__dict__ if name.startswith("test_"))
    if DATA["test_args"]:
        selected = {name.rsplit(".", 1)[-1] for name in DATA["test_args"]}
        names = [name for name in names if name in selected]
    if not names:
        raise SystemExit("ERROR: no selected module-consumer tests")
    suite = unittest.TestSuite(ModuleConsumers(name) for name in names)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() and not result.skipped else 1)
