#!/usr/bin/env python3
# component: discovery-consumer-tests
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P13.md
# constraints: synthetic roots; executed caller blocks, not model/client acceptance
# last_intent_review: 2026-09-22
"""Exercise the shipped consumer examples without a second production inventory."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "catalog_metadata_support", ROOT / "tests/unit/catalog-metadata.py",
)
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)


def body(name):
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def block(name, heading):
    section = body(name).split(heading, 1)
    if len(section) != 2:
        raise AssertionError(f"{name}: missing caller section {heading}")
    found = re.search(r"(?m)^ *```bash\n(.*?)^ *```", section[1], re.S)
    if not found:
        raise AssertionError(f"{name}: missing Bash caller under {heading}")
    return textwrap.dedent(found.group(1))


def tree_snapshot(root):
    physical = native_io_path(root)
    return support.files_snapshot(physical), sorted(
        path.relative_to(physical).as_posix() for path in physical.rglob("*") if path.is_dir()
    )


class DiscoveryConsumers(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            prefix="discovery-consumer-", dir=os.environ["TEMP"],
        )
        self.base = Path(self.temporary.name).resolve()
        self.addCleanup(self.cleanup)
        self.repo = self.base / "project with spaces"
        self.cwd = self.base / "unrelated cwd"
        self.repo.mkdir()
        self.cwd.mkdir()
        self.env = {
            key: value for key, value in os.environ.items() if key.upper() in {
                "PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "SYSTEMDRIVE",
                "OS", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS",
            }
        }
        for key, relative in {
            "HOME": "home", "USERPROFILE": "home", "APPDATA": "app",
            "LOCALAPPDATA": "local", "TEMP": "tmp", "TMP": "tmp", "TMPDIR": "tmp",
            "XDG_CONFIG_HOME": "xdg-config", "XDG_CACHE_HOME": "xdg-cache",
            "XDG_DATA_HOME": "xdg-data", "CLAUDE_CONFIG_DIR": "claude",
            "COPILOT_HOME": "copilot", "LINTEL_HOME": "lintel",
            "LINTEL_PACKS_DIR": "lintel/packs",
        }.items():
            selected = self.base / relative
            selected.mkdir(parents=True, exist_ok=True)
            self.env[key] = selected.as_posix()
        self.env.update(
            LINTEL_SOURCE_ROOT=ROOT.as_posix(), LINTEL_REPO_ROOT=self.repo.as_posix(),
            LINTEL_PROFILE_FILE=(self.base / "lintel/profile.yaml").as_posix(),
            LINTEL_ACTIVE_PACK_FILE=(self.base / "lintel/packs/active-pack").as_posix(),
            LINTEL_AUDIT_DIR=(self.base / "lintel/audit").as_posix(),
            LINTEL_JOBS_REGISTRY=(self.base / "lintel/jobs/_active.md").as_posix(),
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=(self.base / "home/.gitconfig").as_posix(),
            GIT_CEILING_DIRECTORIES=self.base.as_posix(), GIT_TERMINAL_PROMPT="0",
            PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", LINTEL_ASCII="1",
            python_cmd=Path(sys.executable).as_posix(),
        )
        if os.name == "nt":
            self.env["HOMEDRIVE"] = self.base.drive
            self.env["HOMEPATH"] = str(self.base / "home")[len(self.base.drive):]
        git = shutil.which("git")
        git_bash = Path(git).resolve().parent.parent / "bin/bash.exe" if git else None
        self.bash = (
            str(git_bash) if os.name == "nt" and git_bash and git_bash.is_file()
            else shutil.which("bash")
        )
        self.assertTrue(self.bash, "Bash is required for actual consumer examples")
        self.write(self.repo / ".claude/lintel-layout.yaml", "layout_version: 5\n")
        self.write(
            self.base / "home/.lintel/jobs/_active.md",
            "PERSONAL JOBS MUST NOT BE READ\n",
        )
        self.write(
            self.repo / "bin/li-catalog.py",
            "raise RuntimeError('target helper must not execute')\n",
        )
        self.write(self.cwd / "json.py", "raise RuntimeError('cwd import decoy')\n")
        self.preflight()

    def preflight(self):
        for key in (
            "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "TMPDIR",
            "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_DATA_HOME", "CLAUDE_CONFIG_DIR",
            "COPILOT_HOME", "LINTEL_HOME", "LINTEL_PACKS_DIR", "LINTEL_PROFILE_FILE",
            "LINTEL_ACTIVE_PACK_FILE", "LINTEL_AUDIT_DIR", "LINTEL_JOBS_REGISTRY",
            "LINTEL_REPO_ROOT",
        ):
            path = Path(self.env[key])
            self.assertTrue(path.is_absolute() and path.resolve().is_relative_to(self.base), key)
            for ancestor in (path, *path.parents):
                if ancestor.exists():
                    self.assertFalse(ancestor.is_symlink(), key)
                    self.assertFalse(getattr(ancestor.lstat(), "st_file_attributes", 0) & 0x400, key)
                if ancestor == self.base:
                    break
        self.assertEqual(Path(self.env["GIT_CEILING_DIRECTORIES"]), self.base)
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_CONFIG_COUNT", "BASH_ENV", "ENV",
                    "PYTHONPATH", "GH_TOKEN", "GITHUB_TOKEN", "LINTEL_REQUIRED_POLICY"):
            self.assertNotIn(key, self.env)

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        return path

    def cleanup(self):
        self.preflight()
        self.assertEqual(self.base, Path(self.temporary.name).resolve())
        self.assertEqual(self.base.parent, Path(os.environ["TEMP"]).resolve())
        physical = native_io_path(self.base)
        if physical.exists():
            shutil.rmtree(physical)
        self.temporary.cleanup()

    def run_command(self, command):
        self.preflight()
        return subprocess.run(
            command, cwd=self.cwd, env=self.env, capture_output=True, check=False,
            text=True, encoding="utf-8",
        )

    def shell(self, script, *args):
        return self.run_command([
            self.bash, "--noprofile", "--norc", "-c", script, "consumer", *args,
        ])

    def unchanged(self, name, heading, *args, expected=0):
        before = tree_snapshot(self.base)
        result = self.shell(block(name, heading), *args)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertEqual(tree_snapshot(self.base), before, "consumer wrote into a fixture root")
        self.assertNotIn("PERSONAL JOBS MUST NOT BE READ", result.stdout)
        self.assertNotIn("target helper must not execute", result.stderr)
        return result

    def make_map(self, name, pending="T014"):
        folder = self.repo / "specs" / name
        contents = {
            "spec": "# Requirements\nKeep original acceptance.\n",
            "plan": "# Design\nPreserve selected work.\n",
            "tasks": f"- [x] T001 Baseline\n- [ ] {pending} Selected task (depends T001)\n",
            "prompt": f"Continue original {pending}.\n",
        }
        for key, text in contents.items():
            self.write(folder / (key + ".md"), text)
        mapping = {
            "schema_version": 1, "workflow": "spec-kit", "status": "APPROVED",
            **{key: f"specs/{name}/{key}.md" for key in contents},
        }
        self.write(folder / "work.json", json.dumps(mapping))
        return f"specs/{name}/work.json", mapping

    def profile(self, operation, *args, reference=""):
        return self.run_command([
            sys.executable, "-I", "-B", str(ROOT / "lib/profile_context.py"),
            "--source", str(ROOT), "--repo", str(self.repo),
            "--home", self.env["LINTEL_HOME"], "--packs", self.env["LINTEL_PACKS_DIR"],
            "--pointer", self.env["LINTEL_ACTIVE_PACK_FILE"], "--context", "consumer-fixture",
            "--reference", reference, operation, *args,
        ])

    def make_cycle(self, cycle, selected, mapping, status="STARTING"):
        created = self.profile("bind", "consumer-fixture")
        self.assertEqual(created.returncode, 0, created.stderr)
        reference = created.stdout.strip()
        policy = self.profile("required-policy", reference=reference)
        self.assertEqual(policy.returncode, 0, policy.stderr)
        path = self.profile("context-path", reference=reference)
        self.assertEqual(path.returncode, 0, path.stderr)
        self.profile_path = Path(path.stdout)
        self.env.update(
            fixture_cycle=cycle, fixture_map=selected,
            fixture_artifacts=json.dumps(
                {key: mapping[key] for key in ("spec", "plan", "tasks", "prompt")} if mapping else {}
            ),
            fixture_reference=reference, fixture_policy=policy.stdout.strip(),
            fixture_profile_file=path.stdout, fixture_status=status,
        )
        result = self.shell("""
set -euo pipefail
source "$LINTEL_SOURCE_ROOT/lib/state.sh"
state_cycle_begin "$fixture_cycle" full "work_map_path=$fixture_map" \
  "work_artifacts=$fixture_artifacts" "profile_reference=$fixture_reference" \
  "profile_context_file=$fixture_profile_file" "required_policy=$fixture_policy"
state_append BUILD "$fixture_status" next=REVIEW "cycle_id=$fixture_cycle"
""")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def uniformity_source(self):
        source = self.base / "trusted source"
        for relative in (
            "bin/li-uniformity", "lib/uniformity-coverage.sh",
            "tests/shape/uniformity-coverage.sh",
        ):
            self.write(source / relative, (ROOT / relative).read_text(encoding="utf-8"))
        for folder in ("agents", "hooks", "packs"):
            (source / folder).mkdir()
        self.write(source / "skills/cycle/SKILL.md", (
            "---\nname: cycle\nlayer: foundation\ndescription: Synthetic workflow\n"
            "workflow_root: true\nnecessity: REQUIRED\n---\nMethod\n"
        ))
        self.env.update(LINTEL_SOURCE_ROOT=source.as_posix(), WGEN_TS="2026-09-22T00:00:00Z")
        generated = self.shell('bash "$LINTEL_SOURCE_ROOT/bin/li-uniformity" --stdout')
        self.assertEqual(generated.returncode, 0, generated.stdout + generated.stderr)
        self.matrix = self.write(
            source / ".claude/engineering/audits/uniformity-matrix.md", generated.stdout,
        )
        return source

    def test_discovery_callers_expose_real_selection_and_literal_operations(self):
        for name in ("catalog", "help", "skill-router", "welcome", "status"):
            with self.subTest(name=name):
                text = body(name)
                self.assertIn("li-catalog.py", text)
                self.assertIn("source", text)
                self.assertIn("selected", text)
        for name in ("catalog", "help", "skill-router", "welcome"):
            self.assertIn("--selection=", body(name))
        self.assertIn("--list-selections", body("catalog"))
        self.assertIn("at most three", body("skill-router"))

    def test_welcome_query_is_literal_and_does_not_create_state(self):
        for query in ("match", "$(touch unwanted-marker)", "[$.*]", "--check"):
            self.env["keyword"] = query
            result = self.unchanged("welcome", "## 3. Discover the selected method")
            value = json.loads(result.stdout)
            self.assertFalse(value["executed"])
            if query == "match":
                self.assertIn("skill:skill-router", [entry["id"] for entry in value["entries"]])
        self.assertFalse((self.repo / ".claude/runtime").exists())

    def test_selection_caller_uses_installed_operation_not_a_new_router(self):
        self.env["selection"] = "demo-script"
        result = self.unchanged("help", "### Selected capability")
        value = json.loads(result.stdout)
        self.assertEqual(value["selection"]["order"], ["core", "demo-script"])
        self.assertEqual(
            {entry["name"] for entry in value["entries"] if entry["kind"] == "agent"},
            {"DemoNarrativeArc", "DemoNarratorJunior", "SlideNarrationCritic"},
        )
        self.assertNotIn("## Behavioral traits", result.stdout)
        for selection in ("", "demo-script*", "$(touch selection-marker)"):
            self.env["selection"] = selection
            before = tree_snapshot(self.base)
            failed = self.shell(block("help", "### Selected capability"))
            self.assertNotEqual(failed.returncode, 0)
            self.assertTrue(failed.stderr)
            self.assertEqual(tree_snapshot(self.base), before)

    def test_status_selects_original_map_without_jobs_or_profile_creation(self):
        selected, _ = self.make_map("chosen")
        self.make_map("newer-decoy", pending="T900")
        self.env["LINTEL_WORK_MAP"] = selected
        result = self.unchanged("status", "## Workflow")
        self.assertIn('"work_map": "' + selected + '"', result.stdout)
        self.assertIn('"T014"', result.stdout)
        self.assertNotIn('"T900"', result.stdout)
        self.assertIn("UNVERIFIED", result.stdout)
        self.assertNotIn("No active jobs", result.stdout)
        self.assertFalse((self.repo / ".claude/runtime").exists())

    def test_status_refuses_missing_selection_without_manufacturing_work(self):
        result = self.unchanged("status", "## Workflow", expected=2)
        self.assertIn("NEEDS_CONTEXT", result.stderr)
        self.assertFalse((self.repo / ".claude/runtime").exists())

    def test_status_two_cycles_retain_starting_and_blocked_states(self):
        selected, mapping = self.make_map("chosen")
        decoy, other = self.make_map("later", pending="T900")
        self.make_cycle("one", selected, mapping)
        self.make_cycle("two", decoy, other, "DONE")
        self.env.update(LINTEL_CYCLE_ID="one", LINTEL_WORK_MAP=selected)
        result = self.unchanged("status", "## Workflow")
        self.assertIn("BUILD STARTING", result.stdout)
        self.assertNotIn('"T900"', result.stdout)
        changed = self.shell("""
set -euo pipefail
source "$LINTEL_SOURCE_ROOT/lib/state.sh"
state_append BUILD BLOCKED next=REVIEW cycle_id=one
""")
        self.assertEqual(changed.returncode, 0, changed.stderr)
        result = self.unchanged("status", "## Workflow")
        self.assertIn("BUILD BLOCKED", result.stdout)
        self.assertNotIn("BUILD DONE", result.stdout)
        self.assertIn('"release_clearance": false', result.stdout)

    def test_status_wrong_initiative_refuses_without_writes(self):
        selected, mapping = self.make_map("chosen")
        decoy, _ = self.make_map("decoy", pending="T900")
        self.make_cycle("one", selected, mapping)
        self.env.update(LINTEL_CYCLE_ID="one", LINTEL_WORK_MAP=decoy)
        result = self.unchanged("status", "## Workflow", expected=2)
        self.assertIn("initiative", result.stderr)
        self.assertNotIn('"tasks":', result.stdout)

    def test_status_current_cycle_uses_its_saved_original_map(self):
        selected, mapping = self.make_map("chosen")
        later, other = self.make_map("later", pending="T900")
        self.make_cycle("one", selected, mapping)
        self.make_cycle("two", later, other, "BLOCKED")
        result = self.unchanged("status", "## Workflow")
        self.assertIn("Cycle: two", result.stdout)
        self.assertIn('"T900"', result.stdout)
        self.assertNotIn('"T014"', result.stdout)

    def test_status_missing_artifact_does_not_select_another_map(self):
        selected, mapping = self.make_map("chosen")
        self.make_map("decoy", pending="T900")
        (self.repo / mapping["tasks"]).unlink()
        self.env["LINTEL_WORK_MAP"] = selected
        result = self.unchanged("status", "## Workflow", expected=1)
        self.assertIn("ERROR", result.stderr)
        self.assertNotIn('"tasks":', result.stdout)

    def test_status_incomplete_entry_and_absent_cycle_are_not_done(self):
        selected, mapping = self.make_map("chosen")
        self.make_cycle("one", selected, mapping)
        self.env.update(LINTEL_CYCLE_ID="one", LINTEL_WORK_MAP=selected)
        ledger = self.repo / ".claude/runtime/state/00-state.md"
        ledger.write_bytes(ledger.read_bytes() + (
            b"---\nphase: BUILD\nentry_format: 1\ncycle_id: one\nstatus: DONE\n"
        ))
        result = self.unchanged("status", "## Workflow")
        self.assertIn("BUILD INCOMPLETE", result.stdout)
        self.assertNotIn("BUILD DONE", result.stdout)
        self.env["LINTEL_CYCLE_ID"] = "not-recorded"
        result = self.unchanged("status", "## Workflow", expected=2)
        self.assertIn("selected cycle", result.stderr)

    def test_status_caller_profile_mismatch_is_not_silently_discarded(self):
        selected, mapping = self.make_map("chosen")
        self.make_cycle("one", selected, mapping)
        reference = json.loads(self.env["fixture_reference"])
        reference["generation"] += 1
        self.env.update(
            LINTEL_CYCLE_ID="one", LINTEL_WORK_MAP=selected,
            LINTEL_PROFILE_REFERENCE=json.dumps(reference),
        )
        result = self.unchanged("status", "## Workflow", expected=2)
        self.assertIn("PROFILE_REFERENCE_MISMATCH", result.stderr)
        self.assertFalse((self.base / "lintel/audit").exists())

    def test_status_profile_drift_refuses_without_audit_or_rebind(self):
        selected, mapping = self.make_map("chosen")
        required = self.write(
            self.repo / ".claude/profile-requirements.json",
            '{"schema_version":1,"required_pack":"synthetic"}',
        )
        pack = self.write(self.base / "lintel/packs/synthetic/pack.yaml", (
            "name: synthetic\nversion: 1.0.0\n"
            "compliance: {mode: hard, hooks: [synthetic-check]}\n"
            "voice: {default_tier: internal}\n"
            "navigation: {default_workflow: cycle}\n"
        ))
        self.make_cycle("one", selected, mapping)
        self.env.update(LINTEL_CYCLE_ID="one", LINTEL_WORK_MAP=selected)
        stamp = pack.stat()
        pack.write_text(pack.read_text().replace("hard", "off"), encoding="utf-8")
        os.utime(pack, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        result = self.unchanged("status", "## Workflow", expected=2)
        self.assertIn("PROFILE_", result.stderr)
        self.assertNotIn('"tasks":', result.stdout)
        self.assertTrue(required.is_file())
        self.assertFalse((self.base / "lintel/audit").exists())

    def test_status_missing_profile_is_not_recreated(self):
        selected, mapping = self.make_map("chosen")
        self.make_cycle("one", selected, mapping)
        self.env.update(LINTEL_CYCLE_ID="one", LINTEL_WORK_MAP=selected)
        native_io_path(self.profile_path).unlink()
        result = self.unchanged("status", "## Workflow", expected=2)
        self.assertIn("PROFILE_CONTEXT_MISSING", result.stderr)
        self.assertFalse(native_io_path(self.profile_path).exists())

    def test_status_supplementary_jobs_stay_repo_local(self):
        selected, _ = self.make_map("chosen")
        self.env["LINTEL_WORK_MAP"] = selected
        self.write(self.repo / ".claude/runtime/jobs/_active.md", "REPO JOB OBSERVATION\n")
        result = self.unchanged("status", "## Workflow")
        self.assertIn("REPO JOB OBSERVATION", result.stdout)
        self.assertIn('"T014"', result.stdout)

    def test_status_archive_listing_is_opt_in_and_repo_local(self):
        selected, _ = self.make_map("chosen")
        self.env["LINTEL_WORK_MAP"] = selected
        self.write(self.repo / ".claude/runtime/jobs/_archive/saved/job.yaml", "job_id: saved\n")
        self.write(self.base / "home/.lintel/jobs/_archive/private/job.yaml", "job_id: private\n")
        ordinary = self.unchanged("status", "## Workflow")
        self.assertNotIn("saved/job.yaml", ordinary.stdout)
        archived = self.unchanged("status", "## Workflow", "--all")
        self.assertIn("saved/job.yaml", archived.stdout)
        self.assertNotIn("private/job.yaml", archived.stdout)

    def test_status_retains_bound_native_cycle_without_inventing_a_map(self):
        self.make_cycle("native-cycle", "", {})
        self.env["LINTEL_CYCLE_ID"] = "native-cycle"
        result = self.unchanged("status", "## Workflow")
        self.assertIn("No map is bound", result.stdout)
        self.assertIn("BUILD STARTING", result.stdout)
        self.assertNotIn('"tasks":', result.stdout)

    def test_status_injected_resume_reader_failure_is_not_hidden_by_printf(self):
        selected, mapping = self.make_map("chosen")
        self.make_cycle("one", selected, mapping)
        self.env.update(LINTEL_CYCLE_ID="one", LINTEL_WORK_MAP=selected)
        script = block("status", "## Workflow")
        anchor = 'source "$source_root/lib/state.sh"\n'
        self.assertEqual(script.count(anchor), 1)
        script = script.replace(anchor, anchor + "state_resume_phase() { return 7; }\n")
        before = tree_snapshot(self.base)
        result = self.shell(script)
        self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
        self.assertIn("ERROR", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(tree_snapshot(self.base), before)

    def test_uniformity_real_floor_and_matrix_read_are_nonmutating(self):
        self.uniformity_source()
        result = self.unchanged("uniformity", "## Workflow", "--check")
        self.assertIn("floor A satisfied", result.stdout)
        self.assertIn("clean", result.stdout)
        matrix = self.unchanged("uniformity", "## Workflow", "--matrix")
        self.assertIn("adoption", matrix.stdout.lower())

    def test_uniformity_actual_floor_failure_survives_later_messages(self):
        source = self.uniformity_source()
        skill = source / "skills/cycle/SKILL.md"
        skill.write_text(skill.read_text().replace("necessity: REQUIRED\n", ""), encoding="utf-8")
        result = self.unchanged("uniformity", "## Workflow", "--check", expected=1)
        self.assertIn("floor A", result.stdout)
        self.assertNotIn("matrix is stale", result.stdout)

    def test_uniformity_staleness_is_warn_only_not_an_execution_error(self):
        self.uniformity_source()
        self.matrix.write_text(self.matrix.read_text() + "\nstale fixture\n", encoding="utf-8")
        result = self.unchanged("uniformity", "## Workflow", "--check")
        self.assertIn("STALE", result.stdout)

    def test_uniformity_missing_resources_do_not_use_target_executables(self):
        source = self.uniformity_source()
        (source / "tests/shape/uniformity-coverage.sh").unlink()
        self.write(self.cwd / "tests/shape/uniformity-coverage.sh", "touch executed-decoy\n")
        result = self.unchanged("uniformity", "## Workflow", expected=2)
        self.assertIn("UNAVAILABLE", result.stderr)
        self.assertFalse((self.cwd / "executed-decoy").exists())

    def test_uniformity_matrix_absence_differs_from_stale(self):
        self.uniformity_source()
        self.matrix.unlink()
        for mode in ("--matrix", "--check"):
            result = self.unchanged("uniformity", "## Workflow", mode, expected=2)
            self.assertIn("UNAVAILABLE", result.stderr)
            self.assertNotIn("STALE", result.stdout)

    def test_uniformity_actual_generator_error_is_not_labeled_stale(self):
        source = self.uniformity_source()
        (source / "lib/uniformity-coverage.sh").unlink()
        result = self.unchanged("uniformity", "## Workflow", "--check", expected=2)
        self.assertIn("not found", result.stderr)
        self.assertNotIn("STALE", result.stdout)

    def test_uniformity_injected_exits_remain_errors(self):
        source = self.uniformity_source()
        self.write(source / "bin/li-uniformity", "echo synthetic-error >&2\nexit 1\n")
        result = self.unchanged("uniformity", "## Workflow", "--check", expected=1)
        self.assertIn("ERROR", result.stderr)
        self.assertNotIn("STALE", result.stdout)
        self.write(source / "tests/shape/uniformity-coverage.sh", "echo injected-floor-error >&2\nexit 7\n")
        result = self.unchanged("uniformity", "## Workflow", expected=7)
        self.assertIn("injected-floor-error", result.stderr)

    def test_skillify_checks_literal_aliases_before_any_draft_write(self):
        self.env["draft_relative"] = "drafts/new/SKILL.md"
        for name in ("match", "skill-router", "MATCH", "$(touch author-marker)", "../escape", ""):
            self.env["skill_name"] = name
            before = tree_snapshot(self.base)
            result = self.shell(block("skillify", "### Check name and destination"))
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(result.stderr)
            self.assertEqual(tree_snapshot(self.base), before)

    def test_skillify_accepts_bare_name_but_not_wrapper_or_existing_target(self):
        self.env.update(skill_name="regen-mocks", draft_relative="drafts/regen-mocks/SKILL.md")
        result = self.unchanged("skillify", "### Check name and destination")
        self.assertIn("regen-mocks", result.stdout)
        self.write(self.repo / self.env["draft_relative"], "PRESERVE EXISTING DRAFT\n")
        self.unchanged("skillify", "### Check name and destination", expected=2)
        self.env.update(skill_name="li-regen-mocks", draft_relative="drafts/unused/SKILL.md")
        self.unchanged("skillify", "### Check name and destination", expected=2)

    def test_skillify_refuses_outside_destination(self):
        self.env.update(skill_name="regen-mocks", draft_relative="../outside/SKILL.md")
        self.unchanged("skillify", "### Check name and destination", expected=2)

    def test_skillify_missing_source_does_not_run_target_helper(self):
        source = self.base / "absent helpers"
        source.mkdir()
        self.env.update(
            LINTEL_SOURCE_ROOT=source.as_posix(), skill_name="regen-mocks",
            draft_relative="drafts/regen-mocks/SKILL.md",
        )
        self.unchanged("skillify", "### Check name and destination", expected=2)

    def test_template_and_exact_draft_frontmatter_validation(self):
        template = (ROOT / "scaffolding/01-foundation/TEMPLATE-skill.md").read_text(encoding="utf-8")
        self.assertTrue(template.startswith("---\n"))
        text = template.replace("{{name}}", "regen-mocks").replace("{{description}}", "Draft a repeatable mock workflow.")
        draft = self.write(self.repo / "drafts/regen-mocks/SKILL.md", text)
        self.env["draft"] = draft.as_posix()
        result = self.unchanged("skillify", "### Validate the exact draft")
        self.assertIn("required fields", result.stdout)
        self.assertNotIn("deployed", result.stdout)
        self.write(draft, text.replace("layer: foundation\n", "") + "\nlayer: body-decoy\n")
        result = self.unchanged("skillify", "### Validate the exact draft", expected=1)
        self.assertIn("missing layer", result.stdout)
        self.assertIn("INVALID", result.stderr)

    def test_exact_draft_check_rejects_body_only_or_unclosed_headers(self):
        draft = self.repo / "drafts/invalid/SKILL.md"
        self.env["draft"] = draft.as_posix()
        for text in (
            "# Body\n```yaml\n---\nname: decoy\nlayer: foundation\n---\n```\n",
            "---\nname: invalid\nlayer: foundation\n",
        ):
            self.write(draft, text)
            result = self.unchanged("skillify", "### Validate the exact draft", expected=1)
            self.assertIn("INVALID", result.stderr)
            self.assertIn("missing frontmatter", result.stdout)

    def test_eval_worked_counts_and_partial_scope_are_truthful(self):
        text = body("eval")
        cases = re.findall(
            r"^\| (R[123]) \| (\d+)/(\d+) \| (\d+)/(\d+) \| (PASS|FAIL|INSUFFICIENT) \|$",
            text, re.M,
        )
        self.assertEqual(len(cases), 3)
        for cell, correct_good, good, correct_bad, bad, verdict in cases:
            correct_good, good, correct_bad, bad = map(int, (correct_good, good, correct_bad, bad))
            expected = (
                "INSUFFICIENT" if min(good, bad) < 2
                else "PASS" if correct_good / good >= .9 and correct_bad / bad >= .9 else "FAIL"
            )
            self.assertEqual(verdict, expected, cell)
        self.assertIn("PARTIAL_SCOPE", text)
        self.assertIn("NOT_EVALUATED", text)
        self.assertIn("manual", text)
        self.assertNotIn("CALIBRATED if \u226510", text)
        self.assertNotIn("Voice ship prerequisite: met", text)
        self.assertNotIn("Claude Opus", text)
        self.assertNotIn("Audit-logged each run", text)


if __name__ == "__main__":
    with support.isolated_environment() as outer:
        fixture_keys = {
            "HOME", "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "APPDATA", "LOCALAPPDATA",
            "TEMP", "TMP", "TMPDIR", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_DATA_HOME",
            "CLAUDE_CONFIG_DIR", "COPILOT_HOME", "LINTEL_HOME", "LINTEL_PACKS_DIR",
            "LINTEL_AUDIT_DIR", "LINTEL_PROFILE_FILE", "LINTEL_JOBS_REGISTRY",
            "LINTEL_REPO_ROOT", "LINTEL_SOURCE_ROOT", "GIT_CONFIG_NOSYSTEM",
            "GIT_CONFIG_GLOBAL", "GIT_CEILING_DIRECTORIES", "GIT_TERMINAL_PROMPT",
            "PYTHONDONTWRITEBYTECODE", "PYTHONUTF8",
        }
        system_keys = {
            "PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "SYSTEMDRIVE",
            "OS", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS",
        }
        for key in tuple(os.environ):
            if key.upper() not in fixture_keys | system_keys:
                del os.environ[key]
        for key in (
            "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "TMPDIR",
            "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_DATA_HOME", "CLAUDE_CONFIG_DIR",
            "COPILOT_HOME", "LINTEL_HOME", "LINTEL_PACKS_DIR", "LINTEL_AUDIT_DIR",
            "LINTEL_PROFILE_FILE", "LINTEL_JOBS_REGISTRY", "LINTEL_REPO_ROOT",
            "GIT_CONFIG_GLOBAL",
        ):
            path = Path(os.environ[key])
            assert path.is_absolute() and path.resolve().is_relative_to(outer), key
            for ancestor in (path, *path.parents):
                if ancestor.exists():
                    assert not ancestor.is_symlink(), key
                    assert not getattr(ancestor.lstat(), "st_file_attributes", 0) & 0x400, key
                if ancestor == outer:
                    break
        assert Path(os.environ["GIT_CEILING_DIRECTORIES"]) == outer
        native_spec = importlib.util.spec_from_file_location(
            "consumer_native_paths", ROOT / "lib/native_paths.py",
        )
        native = importlib.util.module_from_spec(native_spec)
        native_spec.loader.exec_module(native)
        native_io_path = native.native_io_path
        unittest.main()
