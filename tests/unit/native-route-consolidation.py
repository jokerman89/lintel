#!/usr/bin/env python3
# component: native-route-contract-tests
# implements: ADR-0028
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: read-only source checks; not runtime or independent-review evidence
# last_intent_review: 2026-09-25
"""Check retained method boundaries after removing redundant public routes."""

from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]


def source(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class NativeRoutes(unittest.TestCase):
    def test_cycle_ranges_keep_the_nine_phase_model(self):
        cycle = source("skills/cycle/SKILL.md")
        for route in (
            "/li:cycle --mode research-dive",
            "/li:cycle --from PLAN --to BUILD",
            "/li:cycle --from REVIEW --to CAPTURE",
        ):
            self.assertIn(route, cycle)
        self.assertRegex(
            cycle,
            r"SENSE\s+.+?\s+SCOPE\s+.+?\s+DEFINE\s+.+?\s+DISCOVER\s+.+?\s+PLAN"
            r"\s+.+?\s+BUILD\s+.+?\s+REVIEW\s+.+?\s+SHIP\s+.+?\s+CAPTURE",
        )
        self.assertIn("not BUILD approval", cycle)
        self.assertIn("BUILD package reviews remain required", cycle)

    def test_confirmation_overlay_retains_owned_recovery_without_host_claims(self):
        cycle = source("skills/cycle/SKILL.md")
        section = cycle.split("### Explicit confirmation and owned recovery", 1)[1]
        section = section.split("### Step 0", 1)[0]
        for boundary in (
            "per-mutation confirmation", "backup", "permission to run it",
            "whole-tree reset", "sanitized", "mandatory audit",
            "does not switch host modes",
        ):
            self.assertIn(boundary, section)

    def test_build_checkpoint_keys_remain_compatible_and_scoped(self):
        build = source("skills/build/SKILL.md")
        for field in ("checkpoint_mode", "checkpoint_push", "Work-map:", "Package:", "Leaves:"):
            self.assertIn(field, build)
        self.assertNotIn("[lintel-context]", build)
        self.assertIn("/li:pause", build)
        self.assertIn("/li:resume --from", build)
        self.assertIn("retain the checkpoint locally", build)
        self.assertIn("Serial self-review is not independent review", build)

    def test_catalog_retains_all_kind_filters_and_literal_selected_query(self):
        catalog = source("skills/catalog/SKILL.md")
        for option in ("--kind=all", "--category=qa", "--voice=internal", "--cli=copilot"):
            self.assertIn(option, catalog)
        selected = catalog.split("### Selected capability", 1)[1].split("## Generate", 1)[0]
        self.assertIn('${selection:?select a nonempty capability ID}', selected)
        self.assertIn('--json --selection="$selection"', selected)
        self.assertNotIn("eval ", selected)
        self.assertIn("not an inventory of active tools", catalog)

    def test_audience_overlay_stays_distinct_from_persistent_role(self):
        role = source("skills/role/SKILL.md")
        audience = role.split("## Audience context without a profile change", 1)[1]
        audience = audience.split("## Role resolution", 1)[0]
        for boundary in (
            "persona-sources", "defining manifest", "selected, authorized",
            "Missing names stay missing", "--clear-audience",
            "neither action edits profile files",
        ):
            self.assertIn(boundary, audience)

    def test_identity_migration_keeps_explicit_choice_and_recovery(self):
        migration = source("skills/migrations/SKILL.md")
        for boundary in (
            "migrations --all", "profile-status", "workprofile",
            'pack-switch "$selected_pack" --reason "$migration_reason"',
            "generation-bound", "old logs, preferences, backups",
            "separate owned operation",
        ):
            self.assertIn(boundary, migration)

    def test_review_reader_keeps_shared_clearance_and_read_only_history(self):
        reader = source("bin/li-review-read")
        self.assertIn("skill=inspect", reader)
        self.assertIn('exec "$python" "$helper" read --repo', reader)
        self.assertIn('if [ -f "$log" ]; then cat "$log"; fi', reader)
        self.assertNotRegex(reader, r"(?m)^\s*(mkdir|audit_log)\b")
        ship = source("skills/ship/SKILL.md")
        self.assertIn("never `--repair` after review", ship)
        self.assertIn("v2 review/context/QA", ship)
        self.assertIn("actual independent corroboration", ship)

    def test_resume_selector_discriminates_phases_steps_and_literal_paths(self):
        git = shutil.which("git")
        native_bash = Path(git).resolve().parent.parent / "bin/bash.exe" if git else None
        bash = (str(native_bash) if os.name == "nt" and native_bash and native_bash.is_file()
                else shutil.which("bash"))
        self.assertIsNotNone(bash, "Bash is required for the read-only selector")
        script = 'source "$1/bin/_context.sh"; shift; context_resume_kind "$@"'
        for operand, steps, kind in (
            ("BUILD", ["BUILD"], "phase"),
            ("build", ["build"], "step"),
            ("1.2.a", ["1.2.a", "2.1.a"], "step"),
            ("./BUILD", ["BUILD"], "checkpoint"),
            (r".\BUILD", ["BUILD"], "checkpoint"),
            ("C:/owned/BUILD", ["BUILD"], "checkpoint"),
            ("notes/1.2.a", ["1.2.a"], "checkpoint"),
            ("missing-step", ["1.2.a"], "checkpoint"),
        ):
            with self.subTest(operand=operand):
                result = subprocess.run(
                    [bash, "--noprofile", "--norc", "-c", script, "selector",
                     ROOT.as_posix(), operand, *steps],
                    cwd=ROOT, capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), kind)
        for operands in ([], [""], ["--explicit"]):
            with self.subTest(invalid=operands):
                result = subprocess.run(
                    [bash, "--noprofile", "--norc", "-c", script, "selector",
                     ROOT.as_posix(), *operands],
                    cwd=ROOT, capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr)
        # Construct the literal newline inside Bash: native Windows argv transport
        # can split it before the selector receives a single operand.
        newline_script = 'source "$1/bin/_context.sh"; context_resume_kind "$(printf \'BUILD\\nSHIP\')"'
        result = subprocess.run(
            [bash, "--noprofile", "--norc", "-c", newline_script, "selector", ROOT.as_posix()],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr)

    def test_freeze_glob_uses_real_owned_files_without_launching_audit_process(self):
        specification = importlib.util.spec_from_file_location(
            "freeze_pattern_fixture", ROOT / "skills/code-freeze/scripts/freeze.py")
        freeze = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(freeze)
        with tempfile.TemporaryDirectory(prefix="freeze-pattern-unit-") as temporary:
            repo = Path(temporary).resolve()
            directory = repo / "src" / "frozen"
            directory.mkdir(parents=True)
            for name in ("first.txt", "second.txt", "keep.md"):
                (directory / name).write_text(name, encoding="utf-8")
            state = repo / ".claude/runtime/state/code-freeze/fixture.yaml"

            def invoke(*arguments):
                output, errors = io.StringIO(), io.StringIO()
                argv = ["freeze.py", "--repo", str(repo),
                        "--state-dir", ".claude/runtime/state", "--session", "fixture", *arguments]
                with mock.patch.object(sys, "argv", argv), redirect_stdout(output), redirect_stderr(errors):
                    status = freeze.main()
                return status, output.getvalue(), errors.getvalue()

            with mock.patch.object(freeze, "record_audit") as audit:
                status, output, errors = invoke("src/frozen/*.txt", "--reason", "bounded fixture")
                self.assertEqual(status, 0, errors)
                self.assertEqual([row["path"] for row in json.loads(output)["frozen"]],
                                 ["src/frozen/first.txt", "src/frozen/second.txt"])
                audit.assert_called_once_with(
                    repo, "freeze", ["src/frozen/first.txt", "src/frozen/second.txt"], "bounded fixture")
                before = state.read_bytes()
                for operands in (("--lift", "src/frozen/*.txt"),
                                 ("missing/*.txt",), ("../outside/*.txt",),
                                 ("src/frozen/file:stream",)):
                    with self.subTest(refused=operands):
                        status, output, errors = invoke(*operands)
                        self.assertEqual(status, 2)
                        self.assertEqual(output, "")
                        self.assertTrue(errors)
                        self.assertEqual(state.read_bytes(), before)
                self.assertEqual(audit.call_count, 1)
                self.assertEqual(sorted(path.name for path in directory.iterdir()),
                                 ["first.txt", "keep.md", "second.txt"])


if __name__ == "__main__":
    unittest.main()
