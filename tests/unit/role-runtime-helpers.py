#!/usr/bin/env python3
# component: role-runtime-helper-tests
# implements: ADR-0028, ADR-0034
# intent: .claude/plans/v2-findings/plan.md
# constraints: owned synthetic Git repositories only; no hook overrides or live recovery
# last_intent_review: 2026-10-03
"""Execute the extracted helpers, not Markdown copies or a simulated host policy."""
import hashlib
import itertools
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BASH = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
BISECT = ROOT / "bin/li-isolated-bisect"
RECOVERY = ROOT / "lib/migration-recovery.sh"


def state(path):
    return (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mode & 0o777)


class RoleRuntimeHelpers(unittest.TestCase):
    def setUp(self):
        self.assertTrue(BASH, "Bash is required, not an optional passing skip")
        self.base = Path(tempfile.mkdtemp(prefix="rh-")).resolve()
        self.addCleanup(self.cleanup)
        self.env = dict(os.environ, GIT_OPTIONAL_LOCKS="0",
                        GIT_CEILING_DIRECTORIES=self.base.as_posix())
        self.source = self.base / "source with spaces"
        self.source.mkdir()

    def cleanup(self):
        if os.environ.get("LINTEL_RETAIN_FIXTURES") == "1":
            print(f"Retained synthetic fixture: {self.base}", flush=True)
            return
        self.assertTrue(self.base.name.startswith("rh-"))
        self.assertEqual(self.base.parent, Path(tempfile.gettempdir()).resolve())
        root = Path("\\\\?\\" + str(self.base)) if os.name == "nt" else self.base

        def remove_readonly_file(operation, path, error):
            candidate = Path(path)
            candidate.relative_to(root)
            mode = candidate.lstat().st_mode
            if not isinstance(error[1], PermissionError) or not stat.S_ISREG(mode) or mode & stat.S_IWRITE:
                raise error[1]
            candidate.chmod(mode | stat.S_IWRITE)
            operation(path)

        shutil.rmtree(root, onerror=remove_readonly_file)

    def git(self, *args, cwd=None):
        result = subprocess.run(["git", "--no-pager", "-C", str(cwd or self.source), *args],
                                cwd=self.base, env=self.env, capture_output=True, check=True)
        return result.stdout

    def history(self):
        self.assertTrue(BISECT.is_file(), "the extracted helper is required")
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        hooks = self.source / ".git/hooks"
        self.assertFalse([p for p in hooks.iterdir() if not p.name.endswith(".sample")],
                         "unexpected fixture hooks; do not bypass them")
        target = self.source / "value.txt"
        commits = []
        for value in ("good", "good again", "bad", "bad again"):
            target.write_text(value + "\n", encoding="utf-8")
            self.git("add", "value.txt")
            self.git("commit", "-qm", value)
            commits.append(self.git("rev-parse", "HEAD").decode().strip())
        target.write_text("caller staged\n", encoding="utf-8")
        self.git("add", "value.txt")
        target.write_text("caller unstaged\n", encoding="utf-8")
        (self.source / "untracked ; literal.txt").write_text("caller untracked\n", encoding="utf-8")
        return commits

    def caller_state(self):
        names = (".git/HEAD", ".git/index", ".git/config", "value.txt", "untracked ; literal.txt")
        return {name: state(self.source / name) for name in names}

    def bisect(self, bad, good, repro, trial, *, source_repo=None, intercept_git=False):
        # Environment operands survive MSYS startup literally, including spaces,
        # semicolons and $; only this fixed invocation is shell source.
        source = self.source if source_repo is None else source_repo
        env = dict(self.env, TEST_HELPER=BISECT.as_posix(), TEST_SOURCE=source.as_posix(),
                   TEST_BAD=bad, TEST_GOOD=good, TEST_REPRO=repro.as_posix(),
                   TEST_TRIAL=trial.as_posix())
        command = 'bash "$TEST_HELPER" "$TEST_SOURCE" "$TEST_BAD" "$TEST_GOOD" "$TEST_REPRO" "$TEST_TRIAL"'
        if intercept_git:
            command = (
                'git() { case "${3:-}" in '
                'rev-parse) printf "%040d\\n" 0; return 0 ;; '
                'merge-base) return 0 ;; esac; '
                'printf "PATH_SOURCE=%s\\nPATH_REPRO=%s\\nPATH_TRIAL=%s\\n" '
                '"$source_repo" "$reproducer" "$trial"; return 97; }; '
                'source "$TEST_HELPER" "$TEST_SOURCE" "$TEST_BAD" "$TEST_GOOD" "$TEST_REPRO" "$TEST_TRIAL"'
            )
        return subprocess.run([BASH, "-c", command],
            cwd=self.base, env=env, capture_output=True, text=True, encoding="utf-8")

    def assert_reset(self, trial, bad):
        self.assertTrue(trial.is_dir(), "helper must retain the owned trial")
        self.assertEqual(self.git("rev-parse", "HEAD", cwd=trial).decode().strip(), bad)
        self.assertEqual(self.git("for-each-ref", "refs/bisect", cwd=trial), b"")
        for name in ("BISECT_START", "BISECT_LOG"):
            path = self.git("rev-parse", "--path-format=absolute", "--git-path", name,
                            cwd=trial).decode().strip()
            self.assertFalse(Path(path).exists(), name)

    def test_bisect_finds_real_middle_commit_and_preserves_caller(self):
        commits = self.history()
        before = self.caller_state()
        repro = self.base / "repro ; literal $.sh"
        repro.write_text('grep -q "^good" value.txt\n', encoding="utf-8")
        trial = self.base / "trial ; literal $"
        result = self.bisect(commits[-1], commits[0], repro, trial)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, rf"{commits[2]} is the first (?:bad|'bad') commit")
        self.assertRegex(result.stdout, rf"(?m)^# first (?:bad|'bad') commit: \[{commits[2]}\]")
        self.assert_reset(trial, commits[-1])
        self.assertEqual(before, self.caller_state())

    def test_bisect_runner_error_resets_and_retains_trial(self):
        commits = self.history()
        before = self.caller_state()
        repro = self.base / "runner-error.sh"
        repro.write_text("exit 255\n", encoding="utf-8")
        trial = self.base / "trial-error"
        result = self.bisect(commits[-1], commits[0], repro, trial)
        self.assertNotEqual(result.returncode, 0)
        self.assert_reset(trial, commits[-1])
        self.assertEqual(before, self.caller_state())

    def test_relative_operands_keep_the_invocation_cwd_and_preserve_caller(self):
        commits = self.history()
        before = self.caller_state()
        repro = self.base / "relative repro ; $.sh"
        repro.write_bytes(b'grep -q "^good" value.txt\n')
        trial = self.base / "relative trial ; $"
        result = self.bisect(
            commits[-1], commits[0], repro.relative_to(self.base), trial.relative_to(self.base),
            source_repo=self.source.relative_to(self.base),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, rf"{commits[2]} is the first (?:bad|'bad') commit")
        self.assert_reset(trial, commits[-1])
        self.assertFalse((self.source / trial.name).exists())
        self.assertEqual(before, self.caller_state())

    def test_relative_paths_are_native_before_any_worktree_write(self):
        repro = self.base / "probe repro ; $.sh"
        trial = self.base / "probe trial ; $"
        result = self.bisect(
            "bad", "good", repro.relative_to(self.base), trial.relative_to(self.base),
            source_repo=self.source.relative_to(self.base), intercept_git=True,
        )
        self.assertEqual(result.returncode, 97, result.stdout + result.stderr)
        observed = dict(line.split("=", 1) for line in result.stdout.splitlines())
        expected = {"PATH_SOURCE": self.source, "PATH_REPRO": repro, "PATH_TRIAL": trial}
        self.assertEqual(set(observed), set(expected))
        for key, path in expected.items():
            self.assertTrue(Path(observed[key]).is_absolute(), observed[key])
            self.assertEqual(os.path.normcase(os.path.normpath(observed[key])),
                             os.path.normcase(str(path)))
        self.assertFalse(trial.exists())
        self.assertFalse(repro.exists())
        self.assertEqual(list(self.source.iterdir()), [])

    def test_invalid_ref_literal_ref_and_existing_trial_refuse_without_caller_changes(self):
        commits = self.history()
        before = self.caller_state()
        repro = self.base / "not-used.sh"
        repro.write_text("exit 0\n", encoding="utf-8")
        occupied = self.base / "occupied"
        occupied.mkdir()
        marker = occupied / "keep"
        marker.write_text("do not replace", encoding="utf-8")
        for bad, good, trial in (
            ("missing", commits[0], self.base / "missing-ref"),
            (commits[-1] + "; touch must-not-exist", commits[0], self.base / "literal-ref"),
            (commits[0], commits[-1], self.base / "reversed-bounds"),
            (commits[-1], commits[0], occupied),
        ):
            with self.subTest(bad=bad, trial=trial.name):
                result = self.bisect(bad, good, repro, trial)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(before, self.caller_state())
                self.assertEqual(marker.read_text(encoding="utf-8"), "do not replace")
                if trial != occupied:
                    self.assertFalse(trial.exists())
        self.assertFalse((self.base / "must-not-exist").exists())

    def test_recovery_truth_table_empty_mismatched_and_literal_states(self):
        self.assertTrue(RECOVERY.is_file())
        marker = self.source / "partial"
        marker.write_text("partial migration stays", encoding="utf-8")
        before = state(marker)
        for approved, observed, verification, authorization, effects in itertools.product(
            ("", "step 2; literal $", "other"),
            ("", "step 2; literal $"),
            ("verified", "unverified"),
            ("exact-scope", "other-target"),
            ("none", "possible-live-write"),
        ):
            args = (approved, observed, verification, authorization, effects)
            expected = bool(approved) and approved == observed and (
                verification, authorization, effects) == ("verified", "exact-scope", "none")
            # The predicate's five arguments are data; it performs no recovery.
            env = dict(self.env, TEST_RECOVERY=RECOVERY.as_posix(),
                       **{f"ARG{i}": value for i, value in enumerate(args)})
            result = subprocess.run([BASH, "-c",
                'bash "$TEST_RECOVERY" "$ARG0" "$ARG1" "$ARG2" "$ARG3" "$ARG4"'],
                cwd=self.source, env=env, capture_output=True)
            self.assertEqual(result.returncode, 0 if expected else 1, args)
            self.assertEqual(result.stdout, b"")
            self.assertEqual(state(marker), before)
        for count in range(5):
            result = subprocess.run([BASH, str(RECOVERY), *(["x"] * count)],
                                    cwd=self.source, env=self.env, capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(state(marker), before)

    def test_recovery_is_sourceable_without_changing_shell_state(self):
        self.assertTrue(RECOVERY.is_file())
        env = dict(self.env, TEST_RECOVERY=RECOVERY.as_posix())
        command = (
            'before_opts="$-"; before_pwd="$PWD"; '
            'source "$TEST_RECOVERY"; '
            '[ "$before_opts" = "$-" ] && [ "$before_pwd" = "$PWD" ] && '
            'migration_recovery_allowed "step 1" "step 1" verified exact-scope none'
        )
        result = subprocess.run([BASH, "-c", command], cwd=self.source, env=env, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, b"")


if __name__ == "__main__":
    unittest.main(verbosity=2)
