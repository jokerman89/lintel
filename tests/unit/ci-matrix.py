# component: ci-matrix-planner-test
# implements: ADR-0037
# intent: .claude/decisions/0037-pr-ci-tiering.md
# constraints: temporary git repositories only; no network; never reads the operator's repository state
# last_intent_review: 2026-09-25
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("lintel_ci_matrix", ROOT / "bin" / "li-ci-matrix.py")
assert _spec is not None and _spec.loader is not None
cm = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = cm  # dataclasses resolve string annotations through sys.modules
_spec.loader.exec_module(cm)

FULL = ["ubuntu-latest", "macos-latest", "windows-latest"]


def fixed(paths):
    return lambda base, head: paths


def failing(base, head):
    raise cm.DiffError("unknown revision")


class GitRepo:
    """A throwaway repository with a docs-only branch and a code branch off one base commit."""

    def __init__(self, root: Path):
        self.root = root
        self.git("init", "-q")
        self.git("config", "user.email", "ci-matrix@example.invalid")
        self.git("config", "user.name", "CI matrix test")
        self.git("config", "commit.gpgsign", "false")
        self.write("README.md", "base\n")
        self.write("bin/tool.sh", "#!/usr/bin/env bash\necho base\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.base = self.rev("HEAD")

    def git(self, *args: str) -> str:
        result = subprocess.run(["git", "-C", str(self.root), *args], check=False,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise AssertionError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
        return result.stdout.strip()

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def rev(self, name: str) -> str:
        return self.git("rev-parse", name)

    def branch(self, name: str, changes: dict) -> str:
        self.git("checkout", "-q", "-b", name, self.base)
        for relative, text in changes.items():
            if text is None:
                self.git("rm", "-q", relative)
            else:
                self.write(relative, text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", name)
        return self.rev("HEAD")


class ClassificationTests(unittest.TestCase):
    def test_documentation_paths_are_not_platform_sensitive(self):
        for path in ("README.md", "docs/guide.md", "docs/site/index.html", "notes.txt",
                     "docs/img/diagram.png", "docs/img/logo.SVG", "tests/README.md",
                     "hooks/README.md", "shims/copilot/COPILOT.md", "./docs/a.md"):
            with self.subTest(path=path):
                self.assertFalse(cm.is_platform_sensitive(path))

    def test_code_directories_extensions_and_unknown_files_are_sensitive(self):
        for path in ("bin/li-doctor", "bin/README.md", "lib/notes.md", "install/install.ps1",
                     ".github/workflows/ci.yml", ".github/workflows/README.md", "tests/fixtures/data.txt",
                     "hooks/pre/check.html", "shims/copilot/manifest.json", "skills/x/run.py",
                     "docs/snippet.sh", "config/pack.YAML", "tool.psm1", "a.psd1", "b.mjs", "c.cjs",
                     "d.ts", "e.toml", "f.cmd", "g.bat", "h.js", "LICENSE", "CODEOWNERS",
                     ".gitattributes", "presentations/show/style.css", "docs/archive.tar.gz",
                     ".\\bin\\tool"):
            with self.subTest(path=path):
                self.assertTrue(cm.is_platform_sensitive(path))

    def test_name_status_parser_keeps_both_sides_of_renames(self):
        raw = b"M\0README.md\0R087\0docs/old.md\0bin/new.py\0D\0lib/gone.sh\0"
        self.assertEqual(cm.parse_name_status(raw), ["README.md", "docs/old.md", "bin/new.py", "lib/gone.sh"])
        for broken in (b"R100\0only-one\0", b"?\0x\0", b"M\0"):
            with self.subTest(raw=broken), self.assertRaises(cm.DiffError):
                cm.parse_name_status(broken)


class DecisionTests(unittest.TestCase):
    def test_docs_only_pull_request_runs_ubuntu_only_with_every_part(self):
        decision = cm.decide("pull_request", '["documentation"]', "b", "h", fixed(["README.md", "docs/a.md"]))
        self.assertEqual((decision.tier, decision.triggers, decision.changed), ("ubuntu", (), 2))
        planned = cm.matrix(decision)
        self.assertEqual(planned["os"], ["ubuntu-latest"])
        self.assertEqual(planned["part"], ["unit-1", "unit-2", "integration-1", "integration-2",
                                           "integration-3", "integration-4", "other"])

    def test_code_path_pull_request_runs_full_matrix_and_names_the_trigger(self):
        decision = cm.decide("pull_request", "[]", "b", "h", fixed(["README.md", "lib/x.sh", "docs/y.md"]))
        self.assertEqual((decision.tier, decision.triggers), ("full", ("lib/x.sh",)))
        self.assertEqual(cm.matrix(decision)["os"], FULL)
        self.assertIn("lib/x.sh", "\n".join(cm.report_lines(decision)))
        self.assertIn("<code>lib/x.sh</code>", cm.summary_markdown(decision))

    def test_unusual_path_names_are_reported_without_crashing(self):
        odd = "bin/`<b>`" + "\udcff"  # a backtick, markup and an undecodable byte from surrogateescape
        decision = cm.decide("pull_request", "[]", "b", "h", fixed([odd]))
        self.assertEqual(decision.tier, "full")
        "\n".join(cm.report_lines(decision)).encode("utf-8")
        summary = cm.summary_markdown(decision)
        summary.encode("utf-8")
        self.assertIn("&lt;b&gt;", summary)
        self.assertIn("\\udcff", summary)

    def test_full_matrix_label_forces_full_even_for_docs(self):
        decision = cm.decide("pull_request", '["docs", "ci:full-matrix"]', "b", "h", fixed(["README.md"]))
        self.assertEqual(decision.tier, "full")
        self.assertIn("ci:full-matrix", decision.reason)

    def test_push_and_dispatch_always_run_full_matrix_without_diffing(self):
        for event in ("push", "workflow_dispatch", "schedule", ""):
            with self.subTest(event=event):
                self.assertEqual(cm.decide(event, None, None, None, failing).tier, "full")

    def test_diff_failure_and_doubtful_inputs_fail_safe_to_full(self):
        cases = {
            "diff raises": ("[]", "b", "h", failing),
            "unexpected exception": ("[]", "b", "h", lambda b, h: 1 / 0),
            "missing base": ("[]", "", "h", fixed(["README.md"])),
            "missing head": ("[]", "b", None, fixed(["README.md"])),
            "empty diff": ("[]", "b", "h", fixed([])),
            "bad labels": ("{not json", "b", "h", fixed(["README.md"])),
            "labels not a list": ('{"a": 1}', "b", "h", fixed(["README.md"])),
        }
        for name, (labels, base, head, paths) in cases.items():
            with self.subTest(case=name):
                decision = cm.decide("pull_request", labels, base, head, paths)
                self.assertEqual(decision.tier, "full")
                self.assertEqual(cm.matrix(decision)["os"], FULL)

    def test_full_matrix_matches_adr_0032_parts_and_timeouts(self):
        planned = cm.matrix(cm.Decision("full", "test"))
        self.assertEqual(planned["os"], FULL)
        self.assertEqual(planned["include"], [
            {"part": "unit-1", "scope": "unit", "shard": "1/2", "timeout": 180},
            {"part": "unit-2", "scope": "unit", "shard": "2/2", "timeout": 180},
            {"part": "integration-1", "scope": "integration", "shard": "1/4", "timeout": 300},
            {"part": "integration-2", "scope": "integration", "shard": "2/4", "timeout": 300},
            {"part": "integration-3", "scope": "integration", "shard": "3/4", "timeout": 300},
            {"part": "integration-4", "scope": "integration", "shard": "4/4", "timeout": 300},
            {"part": "other", "scope": "other", "shard": "1/1", "timeout": 60},
        ])


class WorkflowWiringTests(unittest.TestCase):
    """The suite matrix must keep coming from the planner, with every input the planner needs."""

    def test_ci_workflow_consumes_the_planned_matrix(self):
        text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        for marker in ("needs: plan", "matrix: ${{ fromJSON(needs.plan.outputs.matrix) }}",
                       "matrix: ${{ steps.plan.outputs.matrix }}", "fetch-depth: 0",
                       "python3 bin/li-ci-matrix.py", '--event "$EVENT_NAME"', '--labels "$PR_LABELS"',
                       '--base "$BASE_SHA"', '--head "$HEAD_SHA"', '--github-output "$GITHUB_OUTPUT"',
                       '--summary "$GITHUB_STEP_SUMMARY"', "github.event.pull_request.base.sha",
                       "github.event.pull_request.head.sha", "--require-all"):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        self.assertNotIn("os: [ubuntu-latest, macos-latest, windows-latest]", text)
        triggers = text.split("\npermissions:", 1)[0].splitlines()
        start = triggers.index("  pull_request:")
        following = [line for line in triggers[start + 1:] if not line.lstrip().startswith("#")]
        self.assertEqual(following[0], "  workflow_dispatch:", "pull_request must have no branch filter")


class RealGitTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        repo_root = Path(self._tmp.name) / "repo"  # outputs stay outside the work tree
        repo_root.mkdir()
        self.repo = GitRepo(repo_root)

    def run_main(self, *args: str):
        out = Path(self._tmp.name) / "github-output.txt"
        summary = Path(self._tmp.name) / "summary.md"
        for path in (out, summary):
            if path.exists():
                path.unlink()
        with contextlib.redirect_stdout(io.StringIO()):
            code = cm.main(["--repo", str(self.repo.root), "--github-output", str(out),
                            "--summary", str(summary), *args])
        self.assertEqual(code, 0)
        values = dict(line.split("=", 1) for line in out.read_text(encoding="utf-8").splitlines())
        return values["tier"], json.loads(values["matrix"]), summary.read_text(encoding="utf-8")

    def test_docs_only_branch_is_ubuntu_only(self):
        head = self.repo.branch("docs", {"README.md": "changed\n", "docs/new.md": "new\n"})
        tier, planned, summary = self.run_main("--event", "pull_request", "--labels", "[]",
                                               "--base", self.repo.base, "--head", head)
        self.assertEqual((tier, planned["os"]), ("ubuntu", ["ubuntu-latest"]))
        self.assertIn("documentation", summary)

    def test_code_branch_and_deleted_code_are_full(self):
        for name, changes in (("code", {"bin/tool.sh": "#!/usr/bin/env bash\necho changed\n"}),
                              ("delete", {"bin/tool.sh": None}),
                              ("rename", {"README.md": None, "docs/run.py": "base\n"})):
            with self.subTest(branch=name):
                head = self.repo.branch(name, changes)
                tier, planned, summary = self.run_main("--event", "pull_request", "--labels", "null",
                                                       "--base", self.repo.base, "--head", head)
                self.assertEqual((tier, planned["os"]), ("full", FULL))
                self.assertIn("Platform-sensitive paths", summary)

    def test_diff_measured_from_merge_base_ignores_base_branch_progress(self):
        head = self.repo.branch("docs-late", {"docs/a.md": "a\n"})
        base_tip = self.repo.branch("main-moved", {"lib/moved.sh": "echo main\n"})
        tier, planned, _ = self.run_main("--event", "pull_request", "--base", base_tip, "--head", head)
        self.assertEqual((tier, planned["os"]), ("ubuntu", ["ubuntu-latest"]))

    def test_unknown_revision_fails_safe_to_full(self):
        tier, planned, summary = self.run_main("--event", "pull_request", "--labels", "[]",
                                               "--base", "0" * 40, "--head", self.repo.base)
        self.assertEqual((tier, planned["os"]), ("full", FULL))
        self.assertIn("failing safe", summary)

    def test_push_reports_full_without_touching_git(self):
        tier, planned, _ = self.run_main("--event", "push", "--base", "", "--head", "")
        self.assertEqual((tier, planned["os"]), ("full", FULL))


if __name__ == "__main__":
    unittest.main(verbosity=2)
