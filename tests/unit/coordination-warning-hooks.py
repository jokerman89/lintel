#!/usr/bin/env python3
# component: coordination-warning-hook-tests
# implements: ADR-0008, ADR-0029
# intent: skills/da/references/preferences.md
# constraints: inert text fixtures only; no activation, live scans, model calls or cleanup
# last_intent_review: 2026-10-03
"""Exercise the two optional heuristics, not migration/auth correctness."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
BASH = os.environ.get("LINTEL_TEST_BASH") or (
    r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt" else shutil.which("bash")
)
HOOKS = ("da-migration-irreversible-warn", "sc-auth-bypass-warn")


class WarningHeuristics(unittest.TestCase):
    def setUp(self):
        # Retain fixtures for inspection. In particular, do not recursively delete
        # an owned or caller-selected tree during teardown.
        self.root = Path(tempfile.mkdtemp(prefix="coordination-warning-"))
        self.env = os.environ.copy()
        for key in list(self.env):
            if key.startswith("LINTEL_") or key in ("CLAUDE_SESSION_ID", "CYCLE_ID", "PACK_CACHE_FILE"):
                self.env.pop(key)
        for key in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA",
                    "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_DATA_HOME",
                    "XDG_STATE_HOME", "XDG_RUNTIME_DIR", "TEMP", "TMP", "TMPDIR"):
            path = self.root / key.lower()
            path.mkdir()
            self.env[key] = path.as_posix()
        self.env.update({
            "LINTEL_SOURCE_ROOT": ROOT.as_posix(),
            "LINTEL_REPO_ROOT": self.root.as_posix(),
            "LINTEL_HOME": (self.root / "home/.lintel").as_posix(),
            "LINTEL_PACKS_DIR": (ROOT / "packs").as_posix(),
            "LINTEL_ACTIVE_PACK_FILE": (self.root / "absent-active-pack").as_posix(),
            "LINTEL_AUDIT_DIR": (self.root / "audit").as_posix(),
            "PYTHONDONTWRITEBYTECODE": "1", "GIT_PAGER": "cat",
        })

    def put(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_hook(self, hook, relative, *, fail_grep=False):
        path = self.root / relative
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        command = [str(BASH), "--noprofile", "--norc",
                   (ROOT / "hooks/shared" / hook / "run.sh").as_posix(), relative]
        env = self.env
        if fail_grep:
            env = dict(env, TEST_HOOK=(ROOT / "hooks/shared" / hook / "run.sh").as_posix(),
                       TEST_INPUT=relative)
            command = [str(BASH), "--noprofile", "--norc", "-c",
                       'grep() { if [ "${1:-}" = "-cE" ]; then '
                       'printf "inert grep failure\\n" >&2; return 2; fi; command grep "$@"; }; '
                       'source "$TEST_HOOK" "$TEST_INPUT"']
        result = subprocess.run(command, cwd=self.root, env=env, input="",
                                text=True, capture_output=True, timeout=45)
        self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())
        print(json.dumps({"argv": command, "cwd": str(self.root), "exit": result.returncode,
                          "stdout": result.stdout, "stderr": result.stderr,
                          "input_sha256_unchanged": before}))
        return result

    def test_migration_warning_is_a_text_heuristic(self):
        self.put("migrations/001.up.sql", "-- Inert documentation words: DROP TABLE example\n")
        result = self.run_hook(HOOKS[0], "migrations/001.up.sql")
        self.assertEqual(result.returncode, 0)
        self.assertIn("filename/regex heuristic", result.stdout)
        self.assertIn("not proof", result.stdout)
        self.assertNotIn("--ignore-", result.stdout)

    def test_leading_dash_filenames_are_literal_operands(self):
        for hook, relative, text in (
            (HOOKS[0], "-migration.up.sql", "-- Inert glossary: DROP TABLE example\n"),
            (HOOKS[1], "-mauth.txt", 'Inert glossary: role = "admin"\n'),
        ):
            with self.subTest(hook=hook):
                self.put(relative, text)
                result = self.run_hook(hook, relative)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("filename/regex heuristic", result.stdout)
                self.assertNotIn("unavailable", result.stderr)

    def test_collection_errors_warn_without_becoming_clean_counts(self):
        for hook, relative in ((HOOKS[0], "migrations/error.up.sql"), (HOOKS[1], "auth-error.txt")):
            with self.subTest(hook=hook):
                self.put(relative, "Inert fixture input.\n")
                result = self.run_hook(hook, relative, fail_grep=True)
                self.assertEqual(result.returncode, 0)
                self.assertIn("inert grep failure", result.stderr)
                self.assertIn("text observation unavailable", result.stderr)
                self.assertNotIn("filename/regex heuristic matched", result.stdout)

    def test_exact_dash_file_is_read_without_consuming_stdin(self):
        selected = self.root / "-"
        selected.write_bytes(b"fixture-hit\n")
        before = hashlib.sha256(selected.read_bytes()).hexdigest()
        env = dict(self.env, TEXT_HELPER=(ROOT / "hooks/shared/_text.sh").as_posix())
        result = subprocess.run(
            [str(BASH), "--noprofile", "--norc", "-c",
             'set -euo pipefail; source "$TEXT_HELPER"; hook_text_count fixture-hit -; '
             'IFS= read -r remaining; printf "stdin_after=%s\\n" "$remaining"'],
            cwd=self.root, env=env, input="bystander input\n",
            text=True, capture_output=True, timeout=45,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "1\nstdin_after=bystander input\n")
        self.assertEqual(before, hashlib.sha256(selected.read_bytes()).hexdigest())

    def test_down_filename_suppresses_only_the_hint(self):
        self.put("migrations/002.up.sql", "-- Inert documentation words: TRUNCATE example\n")
        self.put("migrations/002.down.sql", "-- Placeholder text, no recovery implementation\n")
        result = self.run_hook(HOOKS[0], "migrations/002.up.sql")
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_down_marker_suppresses_only_the_hint(self):
        self.put("migrations/003.up.sql", "-- Inert documentation words: DROP COLUMN example\n-- down\n")
        result = self.run_hook(HOOKS[0], "migrations/003.up.sql")
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_auth_comment_warns_without_executing_auth_code(self):
        self.put("auth-notes.txt", 'Inert glossary text, not code: role = "admin"\n')
        result = self.run_hook(HOOKS[1], "auth-notes.txt")
        self.assertEqual(result.returncode, 0)
        self.assertIn("filename/regex heuristic", result.stdout)
        self.assertIn("direct_role:1", result.stdout)
        self.assertIn("not proof", result.stdout)
        self.assertNotIn("--ignore-", result.stdout)

    def test_nonmatching_text_is_advisory_silence(self):
        self.put("auth-notes.txt", "This file contains documentation only.\n")
        result = self.run_hook(HOOKS[1], "auth-notes.txt")
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_optional_field_absence_is_not_required_profile_failure(self):
        self.put("ordinary-notes.txt", "No recognized filename or text pattern.\n")
        for hook in HOOKS:
            with self.subTest(hook=hook):
                result = self.run_hook(hook, "ordinary-notes.txt")
                self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_required_profile_lookup_errors_are_not_swallowed(self):
        self.put("ordinary-notes.txt", "No recognized filename or text pattern.\n")
        self.env["LINTEL_PROFILE_PACK"] = "missing-coordination-fixture"
        for hook in HOOKS:
            with self.subTest(hook=hook):
                result = self.run_hook(hook, "ordinary-notes.txt")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("PROFILE_REQUIRED", result.stderr)

    def test_sources_drop_dead_loops_and_unparsed_options(self):
        for hook in HOOKS:
            with self.subTest(hook=hook):
                script = (ROOT / "hooks/shared" / hook / "run.sh").read_text(encoding="utf-8")
                doc = (ROOT / "hooks/shared" / hook / "HOOK.md").read_text(encoding="utf-8")
                self.assertNotIn("--ignore-", script + doc)
                self.assertNotIn("found_patterns", script)
                self.assertNotIn("| while", script)
                self.assertIn("filename/regex", doc)
                self.assertIn("optional", doc.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
