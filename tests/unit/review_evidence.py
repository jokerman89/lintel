# component: review-contract-regressions
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/packages/P05.md
# constraints: synthetic evidence is not an independent review of Lintel
# last_intent_review: 2026-09-20
"""Exercise real producer, audit reader and SHIP with isolated Git fixtures."""
from copy import deepcopy
from datetime import datetime, timezone
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2]
CLI = SOURCE / "bin" / "li-review-evidence.py"
# Resolve Bash through PATH; Windows process search would otherwise prefer System32's WSL launcher.
BASH = shutil.which("bash") or "bash"
sys.path.insert(0, str(SOURCE / "lib"))
from native_paths import native_io_path, path_identity
from review_contract import CONTRACT_VERSION


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def control(name="spec", kind="check", requirement="mandatory", status="pass"):
    return {
        "id": name, "kind": kind, "requirement": requirement,
        "applicability": "applicable", "status": status,
        "reason": "Fixture observation for the selected acceptance.",
        "policy": {
            "source": "spec.md", "version": "fixture-1",
            "applicability": "Selected fixture package", "jurisdiction": None,
            "actor": None, "effective_date": None,
        },
        "evidence": ["checks.txt"], "observation": {},
    }


def neutral_policy():
    return {
        "required": False, "status": "not_required", "source": None,
        "version": None, "applicability": "not_applicable",
        "reason": "No organizational profile requested in this fixture.",
    }


def qa_requirement(item):
    return {key: deepcopy(item[key]) for key in ("id", "kind", "requirement", "applicability", "policy")}


def observed_tests():
    tests = control("tests", "tests")
    tests["observation"] = {
        "command": "fixture-test", "executed": 3, "failed": 0, "skipped": 0, "exit_code": 0,
    }
    return tests


class Fixture(unittest.TestCase):
    native_root_length = None

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lintel-review-")
        self.addCleanup(self.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "target with spaces"
        if self.native_root_length is not None:
            padding = self.native_root_length - len(str(self.root / "cases" / "target-"))
            self.assertGreater(padding, 0, "Fixture parent cannot retain the declared root length")
            self.repo = self.root / "cases" / ("target-" + "x" * padding)
            self.assertEqual(len(str(self.repo)), self.native_root_length)
        native_io_path(self.repo).mkdir(parents=True)
        self.env = dict(os.environ)
        for key in list(self.env):
            if key.startswith(("LINTEL_", "CLAUDE_", "GSTACK_")):
                self.env.pop(key)
        directories = {
            "HOME": "home", "USERPROFILE": "home", "APPDATA": "appdata",
            "LOCALAPPDATA": "localappdata", "TEMP": "temp", "TMP": "temp", "TMPDIR": "temp",
            "XDG_CONFIG_HOME": "xdg-config", "XDG_DATA_HOME": "xdg-data",
            "XDG_CACHE_HOME": "xdg-cache", "XDG_STATE_HOME": "xdg-state",
            "XDG_RUNTIME_DIR": "xdg-runtime", "LINTEL_HOME": "home/.lintel",
            "GSTACK_HOME": "legacy",
        }
        for key, name in directories.items():
            path = self.root / name
            native_io_path(path).mkdir(parents=True, exist_ok=True)
            self.assertFalse(native_io_path(path).is_symlink())
            self.env[key] = path.as_posix()
        self.env.update({
            "LINTEL_REPO_ROOT": self.repo.as_posix(), "LINTEL_SOURCE_ROOT": SOURCE.as_posix(),
            "LINTEL_PYTHON": Path(sys.executable).as_posix(), "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull, "PYTHONDONTWRITEBYTECODE": "1",
            "GIT_CEILING_DIRECTORIES": self.root.as_posix(),
        })
        if self.native_root_length is not None and os.name == "nt":
            self.assertFalse(any(
                key == "GIT_CONFIG_COUNT" or key.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))
                for key in self.env
            ), "Native fixtures do not inherit arbitrary Git command configuration")
            self.env.update(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.longpaths", GIT_CONFIG_VALUE_0="true")
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/fixture")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "core.hooksPath", str(self.root / "no-hooks"))
        self.write(".claude/lintel-layout.yaml", "layout_version: 5\n")
        self.write(".gitignore", ".claude/runtime/\n")
        self.write("source.txt", "before\n")
        self.write("config.json", '{"setting": 1}\n')
        self.write("delete.txt", "delete me\n")
        self.write("spec.md", "# Acceptance\nA1: fix the fixture.\nA2: preserve config.\n")
        self.write("plan.md", "- [ ] A1 Fix fixture\n- [ ] A2 Preserve config\n")
        self.write("prompt.md", "Implement A1 and A2 in P1.\n")
        self.write_json("work.json", {
            "schema_version": 1, "workflow": "lintel", "status": "APPROVED",
            "spec": "spec.md", "plan": "plan.md", "tasks": "plan.md",
            "prompt": "prompt.md",
        })
        self.write("checks.txt", "fixture check: 3 executed, 0 failed, 0 skipped\n")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture baseline")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.write("source.txt", "after\n")
        self.write("new file.txt", "explicitly selected new content\n")
        self.request = {
            "work_map": "work.json", "package_id": "P1", "leaf_ids": ["A1", "A2"],
            "acceptance_paths": ["spec.md", "plan.md"],
            "base": self.base, "selection": [
                "source.txt", "config.json", "delete.txt", "new file.txt",
            ],
            "record_path": ".claude/runtime/reviews/decision.json",
            "attempt_id": "attempt-1", "builder": {"id": "builder", "context": "build-1"},
            "independence_required": True, "purpose": "implementation",
            "profile": None, "required_policy": neutral_policy(),
            "required_controls": ["spec", "quality", "tests"],
            "qa_requirements": [qa_requirement(observed_tests())],
        }
        self.expected_file = self.root / "expected.json"
        self.observed_file = self.root / "corroboration.json"
        self.qa_file = self.root / "qa.json"
        self.record_file = self.repo / self.request["record_path"]

    def cleanup(self):
        root = Path(self.temporary.name).absolute()
        self.assertEqual(root, self.root)
        self.assertTrue(root.name.startswith("lintel-review-"))
        self.temporary.name = str(native_io_path(root))
        self.temporary.cleanup()

    def run_command(self, args, *, ok=None, input=None):
        if self.native_root_length is not None and os.name == "nt":
            self.assertTrue(self.repo.is_relative_to(self.root / "cases"))
            configuration = {
                key: value for key, value in self.env.items()
                if key == "GIT_CONFIG_COUNT" or key.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))
            }
            self.assertEqual(configuration, {
                "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.longpaths", "GIT_CONFIG_VALUE_0": "true",
            })
        if args[0] == "bash":
            # Avoid Windows CRT/MSYS double-quoting of literal JSON argv.
            self.assertIsNone(input)
            input = "exec " + shlex.join(
                arg.as_posix() if isinstance(arg, Path) else str(arg) for arg in args
            ) + "\n"
            args = [BASH]
        result = subprocess.run(
            [str(arg) for arg in args], cwd=self.repo, env=self.env,
            input=input, text=True, encoding="utf-8", capture_output=True, check=False,
        )
        if ok is not None:
            self.assertEqual(result.returncode, ok, result.stdout + result.stderr)
        return result

    def git(self, *args):
        return self.run_command(["git", *args], ok=0)

    def cli(self, *args, ok=0):
        return self.run_command([sys.executable, CLI, *args], ok=ok)

    def write(self, name, content):
        path = self.repo / name
        native_io_path(path.parent).mkdir(parents=True, exist_ok=True)
        native_io_path(path).write_text(content, encoding="utf-8")
        return path

    def write_json(self, name, value):
        return self.write(name, encoded(value) + "\n")

    def prepare(self):
        request_file = getattr(self, "request_file", self.root / "request.json")
        native_io_path(request_file.parent).mkdir(parents=True, exist_ok=True)
        native_io_path(request_file).write_text(encoded(self.request), encoding="utf-8")
        result = self.cli("prepare", "--repo", self.repo, "--request", request_file)
        self.expected = json.loads(result.stdout)
        native_io_path(self.expected_file).write_text(encoded(self.expected), encoding="utf-8")
        return self.expected

    def record(self, *, status="pass", controls=None):
        if not hasattr(self, "expected"):
            self.prepare()
        controls = list(controls) if controls is not None else [control(), control("quality")]
        fixture_tests = observed_tests()
        if (
            qa_requirement(fixture_tests) in self.expected["qa_requirements"]
            and not any(item["id"] == fixture_tests["id"] for item in controls)
        ):
            controls.append(fixture_tests)
        self.review = {
            "schema_version": CONTRACT_VERSION, "skill": "review", "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "Synthetic decision used only by this regression test.",
            "context": deepcopy(self.expected),
            "reviewer": {"id": "reviewer", "context": "review-1"},
            "provenance": "declared",
            "controls": controls,
            "coverage": {
                leaf: list(self.expected["required_controls"])
                for leaf in self.expected["work"]["leaf_ids"]
            },
            "evidence": [],
        }
        self.bind_evidence(self.review)
        return self.review

    def bind_evidence(self, record):
        paths = sorted({p for item in record["controls"] for p in item["evidence"]})
        record["evidence"] = [
            {"path": path, "sha256": hashlib.sha256(native_io_path(self.repo / path).read_bytes()).hexdigest()}
            for path in paths
        ]

    def log(self, record=None, *, ok=0):
        record = self.review if record is None else record
        native_io_path(self.record_file.parent).mkdir(parents=True, exist_ok=True)
        native_io_path(self.record_file).write_text(encoded(record), encoding="utf-8")
        return self.run_command(
            ["bash", SOURCE / "bin" / "li-review-log", "--file", self.record_file], ok=ok,
        )

    def corroborate(self, record=None, kind="host"):
        record = self.review if record is None else record
        data = {
            "schema_version": 1, "kind": kind,
            "source": "synthetic-host-fixture", "reference": "fixture://separate-invocations",
            "record_digest": digest(record), "attempt_id": record["context"]["attempt_id"],
            "builder": record["context"]["builder"], "reviewer": record["reviewer"],
        }
        native_io_path(self.observed_file).write_text(encoded(data), encoding="utf-8")
        return data

    def read(self, *, ok=0, corroboration=True, skill="review"):
        args = [
            "bash", SOURCE / "bin" / "li-review-read", "--skill", skill,
            "--expected", self.expected_file, "--gate-json",
        ]
        if corroboration:
            args += ["--corroboration", self.observed_file]
        return self.run_command(args, ok=ok)

    def qa(self, *, executed=3, skipped=0, failed=0, exit_code=0, controls=None):
        if controls is None:
            tests = control("tests", "tests")
            tests["observation"] = {
                "command": "fixture-test", "executed": executed, "failed": failed,
                "skipped": skipped, "exit_code": exit_code,
            }
            controls = [tests]
        inputs = self.root / "qa-input.json"
        native_io_path(inputs).write_text(encoded({"controls": controls}), encoding="utf-8")
        result = self.cli(
            "qa", "--repo", self.repo, "--expected", self.expected_file,
            "--input", inputs, ok=None,
        )
        native_io_path(self.qa_file).write_text(result.stdout, encoding="utf-8")
        return result

    def ship(self, *, ok=0):
        return self.cli(
            "ship", "--repo", self.repo, "--expected", self.expected_file,
            "--corroboration", self.observed_file, "--qa", self.qa_file,
            "--skill", "review", ok=ok,
        )


class LegacyRegressions(Fixture):
    def test_empty_commit_is_not_filled_in(self):
        result = self.run_command([
            "bash", SOURCE / "bin" / "li-review-log",
            '{"skill":"plan-eng-review","status":"CLEAR","commit":""}',
        ])
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_duplicate_and_malformed_json_are_rejected(self):
        for text in (
            '{"skill":"review","status":"fail","status":"CLEAR","commit":"' + self.base + '"}',
            '{"skill":"review","status":"CLEAR",}',
            '{"skill":"review","score":NaN}',
            '{"skill":"review","score":1e999}',
        ):
            with self.subTest(text=text):
                result = self.run_command(["bash", SOURCE / "bin" / "li-review-log", text])
                self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_later_negative_cannot_resurrect_old_clearance(self):
        for status in ("CLEAR", "NOT CLEARED"):
            self.run_command([
                "bash", SOURCE / "bin" / "li-review-log", encoded({
                    "skill": "plan-eng-review", "status": status, "commit": self.base[:7],
                }),
            ], ok=0)
        result = self.run_command(["bash", SOURCE / "bin" / "li-review-read"])
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        history = self.run_command(["bash", SOURCE / "bin" / "li-review-read", "--json"], ok=0)
        self.assertIn("NOT CLEARED", history.stdout)


class ReviewEvidence(Fixture):
    def good(self):
        self.record()
        self.log()
        self.corroborate()
        self.assertEqual(self.qa().returncode, 0)

    def test_writer_reader_ship_roundtrip_and_unchanged_reuse(self):
        self.good()
        result = json.loads(self.read().stdout)
        self.assertTrue(result["ok"])
        self.assertEqual(result["independence"]["provenance"], "host_observed")
        self.ship()
        self.write("unrelated.txt", "not in the explicit selection\n")
        self.read()
        self.ship()
        self.git("add", "unrelated.txt")
        self.git("commit", "-qm", "unrelated result")
        self.read()
        self.ship()

    def test_dirty_new_deleted_config_and_acceptance_invalidate(self):
        self.good()
        for path, value in (
            ("source.txt", "later dirty edit\n"), ("new file.txt", "changed new file\n"),
            ("config.json", '{"setting":2}\n'), ("spec.md", "# Different acceptance\n"),
            ("plan.md", "- [ ] A1 Different plan\n"), ("prompt.md", "new handoff\n"),
            ("delete.txt", None), ("checks.txt", "changed command output\n"),
        ):
            with self.subTest(path=path):
                file = self.repo / path
                original = file.read_bytes()
                if value is None:
                    file.unlink()
                else:
                    file.write_text(value, encoding="utf-8")
                self.read(ok=3)
                self.ship(ok=3)
                file.write_bytes(original)
        self.ship()

    def test_selected_directory_includes_later_untracked_file(self):
        self.write("chosen/config.txt", "initial\n")
        self.request["selection"] = ["chosen"]
        self.good()
        self.write("chosen/new.txt", "must not be invisible\n")
        self.read(ok=3)
        self.ship(ok=3)

    def test_explicit_acceptance_excerpt_preserves_unrelated_bookkeeping(self):
        self.write("plan.md", "# P1\nA1: acceptance\nA2: acceptance\n# P2\n- [ ] unrelated\n")
        self.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "# P1", "end": "# P2"},
        ]
        self.good()
        self.write("plan.md", "# P1\nA1: acceptance\nA2: acceptance\n# P2\n- [x] unrelated\n")
        self.read()
        self.ship()
        self.write("plan.md", "# P1\nA1: changed acceptance\nA2: acceptance\n# P2\n- [x] unrelated\n")
        self.read(ok=3)
        self.ship(ok=3)

    def test_selected_task_progress_preserves_acceptance_not_criteria_or_authority(self):
        original = "# P1\n- [ ] A1 Fix fixture\n- [ ] A2 Preserve config\n# P2\n- [ ] B1 Unrelated\n"
        self.write("plan.md", original)
        self.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "# P1", "end": "# P2"},
        ]
        self.good()
        for mark in ("x", "X", " "):
            self.write("plan.md", original.replace("[ ] A1", f"[{mark}] A1"))
            for consumer in ("reader", "ship"):
                with self.subTest(progress=mark, consumer=consumer):
                    result = self.read(ok=None) if consumer == "reader" else self.ship(ok=None)
                    self.assertEqual(result.returncode, 0, f"{consumer} rejected unchanged acceptance after task progress: {result.stderr}")
        for text in (
            original.replace("Fix fixture", "Change the acceptance"),
            original.replace("A1 ", "A3 "),
            original.replace("[ ] A1", "[!] A1"),
        ):
            with self.subTest(changed=text):
                self.write("plan.md", text)
                self.read(ok=3)
                self.ship(ok=3)
        self.write("plan.md", original)
        mapping = json.loads((self.repo / "work.json").read_text(encoding="utf-8"))
        mapping["status"] = "DRAFT"
        self.write_json("work.json", mapping)
        self.read(ok=3)
        self.ship(ok=3)

    def test_task_progress_does_not_hide_explicitly_selected_document_bytes(self):
        self.request["selection"].append("plan.md")
        self.good()
        original = (self.repo / "plan.md").read_text(encoding="utf-8")
        self.write("plan.md", original.replace("[ ] A1", "[x] A1"))
        self.read(ok=3)
        self.ship(ok=3)

    def test_checkbox_outside_mapped_task_progress_remains_acceptance(self):
        self.write("spec.md", "# Acceptance\n- [ ] A1 Must preserve fixture.\n")
        self.good()
        self.write("spec.md", "# Acceptance\n- [x] A1 Must preserve fixture.\n")
        self.read(ok=3)
        self.ship(ok=3)

    def test_task_examples_and_different_leaf_ids_are_not_mutable_progress(self):
        original = (
            "- [ ] A1 Fix fixture\n- [ ] A2 Preserve config\n"
            "```markdown\n- [ ] A1 Required example literal\n"
            "```not-a-closing-fence\n- [ ] A1 Another example literal\n```\n"
            "- [ ] A1.1 Different leaf\n"
        )
        self.write("plan.md", original)
        self.good()
        for text in (
            original.replace("[ ] A1 Required example", "[x] A1 Required example"),
            original.replace("[ ] A1 Another example", "[x] A1 Another example"),
            original.replace("[ ] A1.1", "[x] A1.1"),
        ):
            with self.subTest(changed=text):
                self.write("plan.md", text)
                self.read(ok=3)
                self.ship(ok=3)

    def test_indented_and_list_fenced_examples_are_not_task_progress(self):
        original = (
            "# P1\n- [ ] A1 Main task\n    - [ ] A2 Nested task\n"
            "\n# Literal examples\n\n"
            "    - [ ] A1 Required literal code sample\n"
            "\t- [ ] A2 Required tab-indented literal\n"
            "\n- Example container:\n\n"
            "      - [ ] A1 Code indented inside a list\n"
            "\n- ```markdown\n"
            "  - [ ] A2 Literal in a list fence\n"
            "  ```\n"
        )
        self.write("plan.md", original)
        self.good()
        for text in (
            original.replace("[ ] A1 Required literal", "[x] A1 Required literal"),
            original.replace("[ ] A2 Required tab-indented", "[x] A2 Required tab-indented"),
            original.replace("[ ] A1 Code indented", "[x] A1 Code indented"),
            original.replace("[ ] A2 Literal in a list fence", "[x] A2 Literal in a list fence"),
        ):
            self.write("plan.md", text)
            for consumer in ("reader", "ship"):
                with self.subTest(literal=text, consumer=consumer):
                    result = self.read(ok=None) if consumer == "reader" else self.ship(ok=None)
                    self.assertEqual(result.returncode, 3, f"{consumer} accepted a changed literal example")
        self.write("plan.md", original.replace("[ ] A1 Main task", "[x] A1 Main task").replace("[ ] A2 Nested task", "[X] A2 Nested task"))
        self.read()
        self.ship()

    def test_real_nested_tasks_keep_progress_reuse(self):
        for original in (
            "- Parent group\n    - [ ] A1 Nested task\n    - [ ] A2 Nested sibling\n",
            "1. Parent group\n   - Group\n       - [ ] A1 Nested task\n       - [ ] A2 Nested sibling\n",
            "- Parent group\n\t- [ ] A1 Nested task\n\t- [ ] A2 Nested sibling\n",
            "- Parent paragraph\nlazy continuation\n    - [ ] A1 Nested task\n    - [ ] A2 Nested sibling\n",
        ):
            with self.subTest(layout=original):
                self.write("plan.md", original)
                self.prepare()
                self.record()
                self.log()
                self.corroborate()
                self.assertEqual(self.qa().returncode, 0)
                self.write("plan.md", original.replace("[ ] A1", "[x] A1").replace("[ ] A2", "[X] A2"))
                self.read()
                self.ship()

    def test_nested_task_excerpt_markers_keep_their_real_list_context(self):
        original = "- Parent\n    - [x] A1 Nested task\n    - [x] A2 Nested sibling\n# End\n"
        self.write("plan.md", original)
        self.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "    - [x] A1 Nested task", "end": "# End"},
        ]
        self.good()
        self.write("plan.md", original.replace("[x] A1", "[ ] A1").replace("[x] A2", "[X] A2"))
        self.read()
        self.ship()

    def test_claude_selection_does_not_blanket_exclude_plans(self):
        self.request["selection"].append(".claude")
        self.good()
        self.ship()
        self.write(".claude/plans/changed.md", "selected work document must bind\n")
        self.read(ok=3)
        self.ship(ok=3)

    def test_installed_source_is_used_with_conflicting_cwd_and_target_code(self):
        self.good()
        installed = self.root / "installed" / ".github" / "lintel"
        for name in (
            "bin/li-review-log", "bin/li-review-read", "bin/li-review-evidence.py",
            "bin/_audit.sh", "lib/paths.sh", "lib/review_contract.py", "lib/review-schema.json",
            "lib/markdown_source.py", "lib/native_paths.py",
        ):
            target = installed / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / name, target)
        self.write("lib/review_contract.py", "raise RuntimeError('target code executed')\n")
        self.write("lib/markdown_source.py", "raise RuntimeError('target classifier executed')\n")
        self.write("lib/native_paths.py", "raise RuntimeError('target native helper executed')\n")
        env = dict(self.env)
        env.pop("LINTEL_SOURCE_ROOT")
        command = "exec " + shlex.join([
            "bash", (installed / "bin" / "li-review-read").as_posix(), "--skill", "review",
            "--expected", self.expected_file.as_posix(), "--corroboration", self.observed_file.as_posix(),
            "--gate-json",
        ]) + "\n"
        result = subprocess.run(
            [BASH], input=command, cwd=self.root, env=env, text=True, encoding="utf-8",
            capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])
        self.assertFalse((installed / ".claude").exists())
        (installed / "lib" / "native_paths.py").unlink()
        env["PYTHONPATH"] = (self.repo / "lib").as_posix()
        missing = subprocess.run(
            [BASH], input=command, cwd=self.root, env=env, text=True, encoding="utf-8",
            capture_output=True, check=False,
        )
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("Required trusted source helper is unavailable", missing.stderr)
        self.assertNotIn("target native helper executed", missing.stderr)

    def test_staged_content_and_symlink_type_are_bound(self):
        self.good()
        self.git("add", "source.txt")
        self.read(ok=3)
        self.git("restore", "--staged", "source.txt")
        self.read()
        blob = self.run_command(["git", "hash-object", "-w", "--stdin"], input="elsewhere", ok=0).stdout.strip()
        self.git("update-index", "--add", "--cacheinfo", f"120000,{blob},source.txt")
        self.read(ok=3)

    def test_symlink_bytes_and_no_escape_following(self):
        link = self.repo / "chosen-link"
        try:
            link.symlink_to("source.txt")
        except OSError:
            # Git's symlink objects remain testable on hosts without symlink privilege.
            blob = self.run_command(["git", "hash-object", "-w", "--stdin"], input="source.txt", ok=0).stdout.strip()
            self.git("update-index", "--add", "--cacheinfo", f"120000,{blob},chosen-link")
        self.request["selection"].append("chosen-link")
        self.good()
        if link.is_symlink():
            link.unlink()
            link.symlink_to(self.root / "outside.txt")
        else:
            blob = self.run_command(["git", "hash-object", "-w", "--stdin"], input="../outside.txt", ok=0).stdout.strip()
            self.git("update-index", "--add", "--cacheinfo", f"120000,{blob},chosen-link")
        self.read(ok=3)

    def test_latest_decision_precedes_verdict_and_timestamp_order(self):
        self.good()
        for status in ("fail", "unverified", "error"):
            with self.subTest(status=status):
                rejection = deepcopy(self.review)
                rejection["status"] = status
                rejection["timestamp"] = "2000-01-01T00:00:00+00:00"
                self.log(rejection)
                self.read(ok=3)
                self.ship(ok=3)
                self.log()
                self.read()

    def test_unrelated_scope_does_not_revoke_selected_package(self):
        self.good()
        other = deepcopy(self.review)
        other["context"]["work"]["package_id"] = "P-other"
        other["status"] = "fail"
        self.log(other)
        self.read()
        self.ship()

    def test_history_import_is_inspectable_not_a_new_decision(self):
        self.good()
        old = self.root / "old-review.json"
        old.write_text(encoded({
            "skill": "review", "status": "NOT CLEARED", "commit": "",
            "timestamp": "2000-01-01T00:00:00Z",
        }), encoding="utf-8")
        self.run_command([
            "bash", SOURCE / "bin" / "li-review-log", "--history", "--file", old,
        ], ok=0)
        self.read()
        self.ship()
        raw = self.run_command(["bash", SOURCE / "bin" / "li-review-read", "--json"], ok=0)
        self.assertIn("NOT CLEARED", raw.stdout)

    def test_malformed_or_unbound_latest_record_never_falls_back(self):
        self.good()
        audit = self.repo / ".claude/runtime/audit/reviews.jsonl"
        previous = audit.read_bytes()
        for line in (
            '{"kind":"review","raw":"{broken"}',
            '{"kind":"review","status":"pass","commit":""}',
            '{"kind":"review","kind":"other","raw":"{}"}',
            encoded({"skill": "review", "status": "PASS with caveats", "commit": self.base}),
        ):
            with self.subTest(line=line):
                audit.write_bytes(previous + (line + "\n").encode())
                self.read(ok=3)
                self.ship(ok=3)
        audit.write_bytes(previous)
        self.ship()

    def test_invalid_latest_scope_cannot_hide_a_rejection(self):
        self.good()
        audit = self.repo / ".claude/runtime/audit/reviews.jsonl"
        original = audit.read_bytes()
        for bad_scope in (42, {"bad": "scope"}, "../outside.json"):
            bad = deepcopy(self.review)
            bad["context"]["work"]["work_map"] = bad_scope
            bad["status"] = "fail"
            audit.write_bytes(original + (encoded(bad) + "\n").encode())
            self.read(ok=3)
        audit.write_bytes(original)
        self.ship()

    def test_later_malformed_direct_decision_never_revives_clearance(self):
        self.good()
        audit = self.repo / ".claude/runtime/audit/reviews.jsonl"
        previous = audit.read_bytes()
        malformed = []
        for value in ("missing", None, ""):
            decision = deepcopy(self.review)
            decision["status"] = "fail"
            if value == "missing":
                del decision["skill"]
            else:
                decision["skill"] = value
            malformed.append((f"skill-{value}", decision))
        for field, value in (
            ("schema_version", None), ("schema_version", 99), ("context", None),
            ("controls", []), ("coverage", {}), ("status", "NOT PASS"),
            ("reviewer", None), ("timestamp", "not-a-timestamp"),
        ):
            decision = deepcopy(self.review)
            decision["status"] = "fail"
            decision[field] = value
            malformed.append((f"{field}-{value}", decision))
        missing_version = deepcopy(self.review)
        missing_version["skill"] = "other-review"
        missing_version["status"] = "fail"
        del missing_version["schema_version"]
        malformed.append(("missing-version-other-skill", missing_version))
        corrupt_other = deepcopy(self.review)
        corrupt_other["skill"] = "other-review"
        corrupt_other["context"]["work"]["package_id"] = "P-other"
        corrupt_other["context"]["snapshot"]["result_digest"] = "0" * 64
        malformed.append(("corrupt-other-scope", corrupt_other))
        envelope_masquerade = deepcopy(self.review)
        envelope_masquerade.update(
            status="fail", kind="other-review",
            raw=encoded({"skill": "other-review", "status": "FAIL", "commit": self.base}),
        )
        malformed.append(("current-decision-masquerading-as-envelope", envelope_masquerade))
        for label, decision in malformed:
            audit.write_bytes(previous + (encoded(decision) + "\n").encode())
            for consumer in ("reader", "ship"):
                with self.subTest(case=label, consumer=consumer):
                    result = self.read(ok=None) if consumer == "reader" else self.ship(ok=None)
                    self.assertEqual(result.returncode, 3, f"{consumer} accepted malformed {label}: exit {result.returncode}")
                    self.assertFalse(json.loads(result.stdout)["ok"])
            with self.subTest(case=label, consumer="history"):
                history = self.run_command(["bash", SOURCE / "bin" / "li-review-read", "--json"], ok=0)
                self.assertIn(encoded(decision), history.stdout)
        audit.write_bytes(previous)
        self.read()
        self.ship()

    def test_later_malformed_wrapped_decision_cannot_hide_behind_scope(self):
        self.good()
        audit = self.repo / ".claude/runtime/audit/reviews.jsonl"
        previous = audit.read_bytes()
        for label in (
            "missing-skill-and-kind", "null-skill-and-kind", "invalid-other-review",
            "unknown-envelope-format", "malformed-current-history", "legacy-payload-in-current-envelope",
        ):
            decision = deepcopy(self.review)
            decision["status"] = "fail"
            envelope = {
                "format": f"review-v{CONTRACT_VERSION}", "status": "fail",
                "commit": decision["context"]["snapshot"]["head"],
            }
            if label == "missing-skill-and-kind":
                del decision["skill"]
            elif label == "null-skill-and-kind":
                decision["skill"] = None
                envelope["kind"] = None
            elif label == "invalid-other-review":
                decision["skill"] = "other-review"
                envelope["kind"] = "other-review"
                decision["coverage"] = {}
            elif label == "unknown-envelope-format":
                envelope.update(kind="review", format="unknown")
            elif label == "malformed-current-history":
                envelope.update(kind="review", format="history")
                decision["context"] = None
            else:
                envelope["kind"] = "other-review"
                decision = {"skill": "other-review", "status": "FAIL", "commit": self.base}
            envelope["raw"] = encoded(decision)
            audit.write_bytes(previous + (encoded(envelope) + "\n").encode())
            for consumer in ("reader", "ship"):
                with self.subTest(case=label, consumer=consumer):
                    result = self.read(ok=None) if consumer == "reader" else self.ship(ok=None)
                    self.assertEqual(result.returncode, 3, f"{consumer} accepted malformed {label}: exit {result.returncode}")
                    self.assertFalse(json.loads(result.stdout)["ok"])
        audit.write_bytes(previous)
        self.ship()

    def test_shared_selector_rejects_malformed_before_matching_scope(self):
        from review_contract import ContractError, select_latest
        self.record()
        selected = {
            "skill": "review", "work_map": self.expected["work"]["work_map"],
            "package_id": self.expected["work"]["package_id"],
        }
        for field, value in (("skill", None), ("coverage", {}), ("context", None)):
            bad = deepcopy(self.review)
            bad["skill"] = "other-review"
            bad[field] = value
            with self.subTest(field=field), self.assertRaises(ContractError):
                select_latest([self.review, bad], **selected)

    def test_only_valid_unrelated_decisions_are_outside_the_selected_gate(self):
        self.good()
        audit = self.repo / ".claude/runtime/audit/reviews.jsonl"
        previous = audit.read_bytes()
        for unrelated in ("package", "work-map", "skill"):
            decision = deepcopy(self.review)
            decision["status"] = "fail"
            if unrelated == "package":
                decision["context"]["work"]["package_id"] = "P-other"
            elif unrelated == "work-map":
                decision["context"]["work"]["work_map"] = "other-work.json"
            else:
                decision["skill"] = "other-review"
            with self.subTest(scope=unrelated):
                audit.write_bytes(previous + (encoded(decision) + "\n").encode())
                self.read()
                self.ship()
        audit.write_bytes(previous)

    def test_v1_history_and_older_invalid_records_do_not_poison_new_v2_review(self):
        self.good()
        audit = self.repo / ".claude/runtime/audit/reviews.jsonl"
        current = audit.read_bytes()
        legacy = deepcopy(self.review)
        legacy["schema_version"] = 1
        legacy["context"]["schema_version"] = 1
        del legacy["context"]["qa_requirements"]
        for prior in (
            encoded(legacy),
            '{"schema_version":1,"skill":null,"status":"fail"}',
            '{"broken":',
        ):
            with self.subTest(earlier=prior):
                audit.write_bytes((prior + "\n").encode() + current)
                self.read()
                self.ship()
                audit.write_bytes(current + (prior + "\n").encode())
                self.read(ok=3)
                self.ship(ok=3)
        audit.write_bytes(b"\xff\n" + current)
        self.read()
        self.ship()
        audit.write_bytes(current + b"\xff\n")
        self.read(ok=3)
        self.ship(ok=3)
        audit.write_bytes(current)
        self.run_command([
            "bash", SOURCE / "bin" / "li-review-log", "--history", encoded(legacy),
        ], ok=0)
        self.read()
        self.ship()
        history = self.run_command(["bash", SOURCE / "bin" / "li-review-read", "--json"], ok=0)
        self.assertIn('"format":"history"', history.stdout)
        legacy_context = self.root / "legacy-context.json"
        legacy_context.write_text(encoded(legacy["context"]), encoding="utf-8")
        self.cli("qa", "--repo", self.repo, "--expected", legacy_context, "--input", self.root / "qa-input.json", ok=1)
        audit.write_bytes(current)
        stale_qa = json.loads(self.qa_file.read_text(encoding="utf-8"))
        stale_qa["schema_version"] = 1
        self.qa_file.write_text(encoded(stale_qa), encoding="utf-8")
        self.ship(ok=3)

    def test_writer_reports_failed_persistence(self):
        self.record()
        audit = self.repo / ".claude/runtime/audit/reviews.jsonl"
        audit.mkdir(parents=True)
        result = self.log(ok=1)
        self.assertNotIn("li-review-log: recorded", result.stdout)
        self.assertTrue(result.stderr)

    def test_new_required_policy_declaration_invalidates_neutral_review(self):
        self.good()
        self.write_json(".claude/profile-requirements.json", {
            "schema_version": 1, "required_pack": "synthetic-strict",
        })
        self.read(ok=3)
        self.ship(ok=3)

    def test_ad_hoc_snapshot_bound_inspection_needs_no_map_or_backlog(self):
        (self.repo / "work.json").unlink()
        before = self.git("status", "--porcelain").stdout
        selected = self.cli(
            "snapshot", "--repo", self.repo, "--base", self.base, "--select", "source.txt",
        )
        selection_file = self.root / "inspection-snapshot.json"
        selection_file.write_text(selected.stdout, encoding="utf-8")
        inputs = self.root / "inspection-controls.json"
        tests = control("tests", "tests")
        tests["observation"] = {"command": "fixture-test", "executed": 3, "failed": 0, "skipped": 0, "exit_code": 0}
        inputs.write_text(encoded({"controls": [tests], "required_policy": neutral_policy()}), encoding="utf-8")
        report = self.cli(
            "inspect", "--repo", self.repo, "--snapshot", selection_file, "--input", inputs,
        )
        result = json.loads(report.stdout)
        self.assertFalse(result["release_clearance"])
        self.assertEqual(result["purpose"], "inspection")
        self.assertFalse(result["result"]["blocked"])
        self.assertEqual(before, self.git("status", "--porcelain").stdout)
        self.write("source.txt", "changed during inspection\n")
        self.cli("inspect", "--repo", self.repo, "--snapshot", selection_file, "--input", inputs, ok=1)

    def test_unmapped_review_cannot_be_promoted_to_strict_ship(self):
        self.request["work_map"] = None
        self.record()
        self.log()
        self.corroborate()
        self.qa()
        self.read(ok=3)
        self.ship(ok=3)

    def test_schema_exact_enums_nonempty_bindings_and_full_coverage(self):
        self.record()
        for field, value in (
            ("status", "CLEARED eventually"), ("status", ""), ("provenance", "host_observed"),
        ):
            bad = deepcopy(self.review)
            bad[field] = value
            self.log(bad, ok=1)
        for part, field, value in (
            ("snapshot", "head", ""), ("snapshot", "base", ""),
            ("work", "leaf_ids", []), ("work", "acceptance_digest", ""),
        ):
            bad = deepcopy(self.review)
            bad["context"][part][field] = value
            self.log(bad, ok=1)
        bad = deepcopy(self.review)
        del bad["coverage"]["A2"]
        self.log(bad, ok=1)
        bad = deepcopy(self.review)
        bad["coverage"]["A2"] = ["spec"]
        self.log(bad, ok=1)
        bad = deepcopy(self.review)
        bad["context"]["attempt_id"] = ""
        self.log(bad, ok=1)

    def test_declared_names_are_not_authenticated_independence(self):
        self.good()
        result = json.loads(self.read(ok=3, corroboration=False).stdout)
        self.assertFalse(result["independence"]["corroborated"])
        self.assertEqual(result["independence"]["provenance"], "declared")
        data = self.corroborate()
        data["record_digest"] = "0" * 64
        self.observed_file.write_text(encoded(data), encoding="utf-8")
        self.read(ok=3)
        self.corroborate(kind="human")
        result = json.loads(self.read().stdout)
        self.assertEqual(result["independence"]["provenance"], "human_attested")
        self.review["reviewer"] = self.review["context"]["builder"]
        self.log()
        self.corroborate()
        self.read(ok=3)

    def test_expected_scope_attempt_profile_and_policy_cannot_be_rebound(self):
        self.good()
        original = deepcopy(self.expected)
        different_qa = deepcopy(original["qa_requirements"])
        different_qa[0]["kind"] = "check"
        for field, value in (
            ("attempt_id", "attempt-2"),
            ("profile", {
                "schema_version": 1, "context_id": "strict", "generation": 1,
                "name": "strict", "version": "1", "digest": "sha256:" + "a" * 64,
            }),
            ("required_controls", ["spec", "quality", "missing-control"]),
            ("qa_requirements", different_qa),
        ):
            with self.subTest(field=field):
                changed = deepcopy(original)
                changed[field] = value
                self.expected_file.write_text(encoded(changed), encoding="utf-8")
                self.read(ok=3)
                self.ship(ok=3)
        self.expected_file.write_text(encoded(original), encoding="utf-8")
        self.ship()

    def test_metadata_exclusion_cannot_hide_plans_or_arbitrary_json(self):
        for value in ("plan.md", "config.json", ".claude/plans/work.json", "../outside.json"):
            with self.subTest(value=value):
                self.request["record_path"] = value
                inputs = self.root / "invalid-request.json"
                inputs.write_text(encoded(self.request), encoding="utf-8")
                self.cli("prepare", "--repo", self.repo, "--request", inputs, ok=1)
        self.request["record_path"] = ".claude/runtime/reviews/decision.json"
        self.write_json(self.request["record_path"], {"secretly": "arbitrary input"})
        inputs = self.root / "invalid-request.json"
        inputs.write_text(encoded(self.request), encoding="utf-8")
        self.cli("prepare", "--repo", self.repo, "--request", inputs, ok=1)

    def test_explicit_verification_only_and_no_fictitious_changes(self):
        self.request["selection"] = ["config.json"]
        self.record()
        self.log()
        self.corroborate()
        self.qa()
        self.read(ok=3)
        self.request["purpose"] = "verification_only"
        self.prepare()
        self.record()
        self.log()
        self.corroborate()
        self.qa()
        self.read()
        self.ship()

    def test_deleted_file_is_an_explicit_changed_input(self):
        (self.repo / "delete.txt").unlink()
        self.request["selection"] = ["delete.txt"]
        self.good()
        self.ship()

    def test_snapshot_rejects_absent_unbound_path_and_path_escape(self):
        for path in ("nonexistent.file", "../outside", ".git/config"):
            with self.subTest(path=path):
                self.request["selection"] = [path]
                inputs = self.root / "invalid-request.json"
                inputs.write_text(encoded(self.request), encoding="utf-8")
                self.cli("prepare", "--repo", self.repo, "--request", inputs, ok=1)

    def test_qa_empty_missing_or_stale_cannot_ship(self):
        self.good()
        for counts in ({"executed": 0}, {"skipped": 1}, {"failed": 1, "exit_code": 1}):
            with self.subTest(counts=counts):
                self.assertEqual(self.qa(**counts).returncode, 3)
                self.ship(ok=3)
        self.qa()
        data = json.loads(self.qa_file.read_text(encoding="utf-8"))
        data["context_digest"] = "0" * 64
        self.qa_file.write_text(encoded(data), encoding="utf-8")
        self.ship(ok=3)
        self.qa_file.unlink()
        self.ship(ok=3)

    def test_approved_docs_only_validation_with_grounded_tests_na_can_ship(self):
        self.write("guide.md", "# Guide\nDocumentation-only change.\n")
        self.write("spec.md", "# Acceptance\nA1: check document links.\nA2: check examples.\nTests: not applicable to this docs-only package.\n")
        self.request["selection"] = ["guide.md"]
        self.request["required_controls"].append("document")
        document = control("document")
        document["reason"] = "Fixture document links and examples were checked."
        document["observation"] = {"command": "fixture-document-check", "executed": 1}
        tests_na = control("tests", "tests", status="unverified")
        tests_na["applicability"] = "not_applicable"
        tests_na["reason"] = "Approved spec limits this package to checked documentation; executable tests do not apply."
        self.request["qa_requirements"] = [qa_requirement(document), qa_requirement(tests_na)]
        self.record(controls=[control(), control("quality"), document, tests_na])
        self.log()
        self.corroborate()
        self.read()
        qa = self.qa(controls=[document, tests_na])
        with self.subTest(consumer="qa"):
            self.assertEqual(qa.returncode, 0, qa.stderr)
        with self.subTest(consumer="ship"):
            self.ship()
        for missing in ("source", "version"):
            bad = deepcopy(tests_na)
            bad["policy"][missing] = None
            with self.subTest(unknown_policy=missing):
                self.assertNotEqual(self.qa(controls=[document, bad]).returncode, 0)
                self.ship(ok=3)
        for counts in (
            {"executed": 0, "failed": 0, "skipped": 0, "exit_code": 0},
            {"executed": 2, "failed": 1, "skipped": 0, "exit_code": 1},
            {"executed": 2, "failed": 0, "skipped": 1, "exit_code": 0},
        ):
            required_test = control("tests", "tests")
            required_test["observation"] = {"command": "fixture-tests", **counts}
            with self.subTest(required_tests=counts):
                self.assertNotEqual(self.qa(controls=[document, required_test]).returncode, 0)
                self.ship(ok=3)

    def test_qa_obligations_cannot_be_omitted_downgraded_or_retyped(self):
        tests = observed_tests()
        document = control("documentation")
        self.request["required_controls"].append("documentation")
        self.request["qa_requirements"] = [qa_requirement(tests), qa_requirement(document)]
        self.record(controls=[control(), control("quality"), tests, document])
        self.log()
        self.corroborate()
        self.read()
        self.assertEqual(self.qa(controls=[tests, document]).returncode, 0)
        self.ship()
        omitted = [document]
        advisory_failure = deepcopy(tests)
        advisory_failure.update(requirement="advisory", status="fail")
        retyped = deepcopy(tests)
        retyped.update(kind="check", observation={})
        not_applicable = deepcopy(tests)
        not_applicable.update(applicability="not_applicable", status="unverified")
        changed_policy = deepcopy(tests)
        changed_policy["policy"]["version"] = "different-policy"
        for label, controls in (
            ("omitted", omitted), ("advisory-failure", [advisory_failure, document]),
            ("retyped", [retyped, document]), ("not-applicable", [not_applicable, document]),
            ("policy", [changed_policy, document]), ("duplicate", [tests, tests, document]),
        ):
            with self.subTest(case=label, consumer="qa"):
                self.assertNotEqual(self.qa(controls=controls).returncode, 0)
            forged = {
                "schema_version": CONTRACT_VERSION, "context_digest": digest(self.expected),
                "controls": controls, "evidence": [],
            }
            self.bind_evidence(forged)
            self.qa_file.write_text(encoded(forged), encoding="utf-8")
            with self.subTest(case=label, consumer="ship"):
                self.read()
                self.ship(ok=3)
        failed_tests = deepcopy(tests)
        failed_tests.update(status="fail")
        failed_tests["observation"].update(failed=1, exit_code=1)
        self.assertEqual(self.qa(controls=[failed_tests, document]).returncode, 3)
        self.ship(ok=3)

    def test_qa_contract_and_review_cannot_contradict_each_other(self):
        self.record()
        self.log()
        self.corroborate()
        self.assertEqual(self.qa().returncode, 0)
        audit = self.repo / ".claude/runtime/audit/reviews.jsonl"
        for field, value in (
            ("kind", "check"), ("requirement", "advisory"), ("applicability", "not_applicable"),
        ):
            bad = deepcopy(self.review)
            target = next(item for item in bad["controls"] if item["id"] == "tests")
            target[field] = value
            with self.subTest(review_field=field):
                self.log(bad, ok=1)
                self.log()
                previous = audit.read_bytes()
                audit.write_bytes(previous + (encoded(bad) + "\n").encode())
                self.read(ok=3)
                self.ship(ok=3)
                audit.write_bytes(previous)
        bad = deepcopy(self.review)
        bad["controls"] = [item for item in bad["controls"] if item["id"] != "tests"]
        self.log(bad, ok=1)
        self.log()
        original_request = deepcopy(self.request)
        for case in ("missing-inventory", "duplicate-id", "mandatory-not-required", "advisory-marked-required"):
            self.request = deepcopy(original_request)
            if case == "missing-inventory":
                del self.request["qa_requirements"]
            elif case == "duplicate-id":
                self.request["qa_requirements"] *= 2
            elif case == "mandatory-not-required":
                self.request["required_controls"].remove("tests")
            else:
                self.request["qa_requirements"][0]["requirement"] = "advisory"
            request = self.root / "bad-qa-contract.json"
            request.write_text(encoded(self.request), encoding="utf-8")
            with self.subTest(context=case):
                self.cli("prepare", "--repo", self.repo, "--request", request, ok=1)

    def test_bound_typed_review_requirement_cannot_disappear_from_qa_contract(self):
        document = control("documentation")
        self.request["required_controls"].append("documentation")
        self.request["qa_requirements"] = [qa_requirement(document)]
        self.record(controls=[control(), control("quality"), observed_tests(), document])
        self.log(ok=1)
        audit = self.repo / ".claude/runtime/audit/reviews.jsonl"
        audit.parent.mkdir(parents=True, exist_ok=True)
        audit.write_text(encoded(self.review) + "\n", encoding="utf-8")
        self.corroborate()
        self.read(ok=3)
        self.ship(ok=3)

    def test_genuine_docs_only_contract_without_tests_and_advisory_failure(self):
        document = control("document")
        advice = control("wording", requirement="advisory", status="fail")
        self.request["required_controls"] = ["spec", "quality", "document"]
        self.request["qa_requirements"] = [qa_requirement(document), qa_requirement(advice)]
        self.write("guide.md", "# Guide\nChecked document.\n")
        self.write("spec.md", "# Acceptance\nOnly documentation checks apply; wording advice is not mandatory.\n")
        self.request["selection"] = ["guide.md"]
        self.record(controls=[control(), control("quality"), document, advice])
        self.log()
        self.corroborate()
        self.read()
        self.assertEqual(self.qa(controls=[document, advice]).returncode, 0)
        self.ship()

    def test_qa_needs_actual_applicable_validation_not_only_exemptions(self):
        self.good()
        tests_na = control("tests", "tests", status="unverified")
        tests_na["applicability"] = "not_applicable"
        self.assertEqual(self.qa(controls=[tests_na]).returncode, 1)
        self.ship(ok=3)
        advice = control("optional-document", requirement="advisory")
        self.assertEqual(self.qa(controls=[advice, tests_na]).returncode, 1)
        self.ship(ok=3)


class MarkdownBoundaryEvidence(Fixture):
    def prepare_pipeline(self, source, *, acceptance=None, progress_spans=(), end_progress_span=None):
        (self.repo / "plan.md").write_bytes(source.encode("utf-8"))
        self.prepare()
        selected = next(item for item in self.expected["work"]["acceptance_manifest"] if item["path"] == "plan.md")
        if acceptance is None and selected["start"] is None:
            acceptance = source
        if acceptance is not None:
            preimage = acceptance.encode("utf-8")
            if selected["start"] is not None:
                preimage = b"lintel:task-excerpt\0" + encoded({
                    "text": acceptance, "progress_spans": list(progress_spans),
                    "end_progress_span": end_progress_span,
                }).encode("utf-8")
            self.assertEqual(selected["sha256"], hashlib.sha256(preimage).hexdigest())
        self.record()
        self.log()
        self.corroborate()
        self.assertEqual(self.qa().returncode, 0)
        self.read()
        self.ship()

    def consume_changed(self, source, *, literal):
        preserved_qa = self.qa_file.read_bytes()
        (self.repo / "plan.md").write_bytes(source.encode("utf-8"))
        reader = self.read(ok=None)
        qa = self.qa()
        self.qa_file.write_bytes(preserved_qa)
        ship = self.ship(ok=None)
        for label, result, expected in (
            ("reader", reader, 3 if literal else 0),
            ("qa", qa, 1 if literal else 0),
            ("ship", ship, 3 if literal else 0),
        ):
            with self.subTest(consumer=label):
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                if label != "qa":
                    self.assertEqual(json.loads(result.stdout)["ok"], not literal)

    def literal(self, sample):
        original = "# P1\n- [ ] A1 Main\n- [ ] A2 Main\n\n# Literal examples\n\n" + sample
        self.prepare_pipeline(original)
        self.consume_changed(
            original.replace("[ ] A1 Required literal", "[x] A1 Required literal"), literal=True,
        )

    def progress(self, original):
        self.prepare_pipeline(original)
        self.consume_changed(
            original.replace("[ ] A1", "[x] A1").replace("[ ] A2", "[X] A2"), literal=False,
        )

    def test_literal_compound_fence(self):
        self.literal("- - ```markdown\n    - [ ] A1 Required literal\n    ```\n")

    def test_literal_ordered_compound_fence(self):
        self.literal("1. - ```markdown\n     - [ ] A1 Required literal\n     ```\n")

    def test_literal_raw_pre(self):
        self.literal("<pre>\n- [ ] A1 Required literal\n</pre>\n")

    def test_literal_raw_comment(self):
        self.literal("<!--\n- [ ] A1 Required literal\n-->\n")

    def test_literal_raw_script(self):
        self.literal("<script>\n- [ ] A1 Required literal\n</script>\n")

    def test_literal_raw_div(self):
        self.literal("<div>\n- [ ] A1 Required literal\n</div>\n")

    def test_literal_list_html(self):
        self.literal("- <pre>\n  - [ ] A1 Required literal\n  </pre>\n")

    def test_literal_quoted_fence(self):
        self.literal("> ```markdown\n> - [ ] A1 Required literal\n> ```\n")

    def test_literal_quoted_task(self):
        self.literal("> - [ ] A1 Required literal\n")

    def test_literal_indented(self):
        self.literal("    - [ ] A1 Required literal\n")

    def test_literal_list_indented(self):
        self.literal("- Example\n\n      - [ ] A1 Required literal\n")

    def test_progress_nested(self):
        self.progress("- Parent\n    - [ ] A1 Real task\n    - [ ] A2 Real sibling\n")

    def test_progress_ordered(self):
        self.progress("1. Parent\n   - Group\n       - [ ] A1 Real task\n       - [ ] A2 Real sibling\n")

    def test_progress_tab_nested(self):
        self.progress("- Parent\n\t- [ ] A1 Real task\n\t- [ ] A2 Real sibling\n")

    def test_progress_compound(self):
        self.progress("- - [ ] A1 Real task\n  - [ ] A2 Real sibling\n")

    def test_progress_crlf(self):
        self.progress("- Parent\r\n    - [ ] A1 Real task\r\n    - [ ] A2 Real sibling\r\n")

    def test_literal_excerpt_retains_outer_fence_context(self):
        original = (
            "# P1\n- [ ] A1 Main\n- [ ] A2 Main\n\n"
            "- - ```markdown\n    BEGIN\n    - [ ] A1 Required literal\n    END\n    ```\n"
        )
        self.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "    BEGIN", "end": "    END"},
        ]
        self.prepare_pipeline(original, acceptance="    BEGIN\n    - [ ] A1 Required literal\n")
        self.consume_changed(
            original.replace("[ ] A1 Required literal", "[x] A1 Required literal"), literal=True,
        )

    def test_real_excerpt_marker_retains_outer_list_context(self):
        original = "- Parent\n    - [x] A1 Real task\n    - [ ] A2 Real sibling\n# End\n"
        self.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "    - [x] A1 Real task", "end": "# End"},
        ]
        self.prepare_pipeline(
            original, acceptance="    - [ ] A1 Real task\n    - [ ] A2 Real sibling\n",
            progress_spans=[[7, 8], [30, 31]],
        )
        self.consume_changed(
            original.replace("[x] A1", "[ ] A1").replace("[ ] A2", "[X] A2"), literal=False,
        )

    def test_literal_raw_code(self):
        self.literal("<code>\n- [ ] A1 Required literal\n</code>\n")

    def test_literal_raw_style(self):
        self.literal("<style>\n- [ ] A1 Required literal\n</style>\n")

    def test_literal_same_line_html_and_comment(self):
        for sample in (
            "- Before <pre>- [ ] A1 Required literal</pre>\n",
            "- <!-- [ ] A1 Required literal -->\n",
        ):
            with self.subTest(sample=sample):
                self.literal(sample)

    def test_literal_tab_indented(self):
        self.literal("\t- [ ] A1 Required literal\n")

    def test_literal_compound_quote(self):
        self.literal("- > - [ ] A1 Required literal\n")

    def test_literal_inline_code_and_multiline_script_example(self):
        for sample in (
            "- `- [ ] A1 Required literal`\n",
            "Paragraph `\n<script>\n- [ ] A1 Required literal\n</script>\n`\n",
        ):
            with self.subTest(sample=sample):
                self.literal(sample)

    def test_literal_ordinary_item_continuation(self):
        self.literal("- Parent paragraph\n  [ ] A1 Required literal\n")

    def test_literal_ordered_non_one_paragraph_continuation(self):
        self.literal("Paragraph\n2. [ ] A1 Required literal\n")

    def test_progress_ordered_after_blank_line(self):
        self.progress("Paragraph\n\n2. [ ] A1 Real task\n")

    def test_progress_ordered_one_interrupts_paragraph(self):
        self.progress("Paragraph\n1. [ ] A1 Real task\n")

    def test_literal_opaque_and_unclosed_regions(self):
        for sample in (
            "<![CDATA[\n- [ ] A1 Required literal\n]]>\n",
            "<!--\n- [ ] A1 Required literal",
        ):
            with self.subTest(sample=sample):
                self.literal(sample)

    def test_literal_escaped_checkbox(self):
        self.literal("- \\[ ] A1 Required literal\n")

    def test_progress_unicode_crlf_eof_and_exact_single_character_identity(self):
        original = (
            "# \u03bb \U0001f600\r\n\r\n- [x] **A1**: Real task\r\n"
            "- [X] `A2`: Real sibling\r\n- [x] A1.1 Different leaf\r\n"
            "<pre>- [x] A1 Literal</pre>"
        )
        normalized = original.replace("[x] **A1**", "[ ] **A1**").replace("[X] `A2`", "[ ] `A2`")
        self.prepare_pipeline(original, acceptance=normalized)
        self.consume_changed(normalized, literal=False)
        for changed in (
            normalized.replace("[x] A1.1", "[ ] A1.1"),
            normalized.replace("[x] A1 Literal", "[ ] A1 Literal"),
            normalized.replace("\r\n", "\n"),
            normalized + "\n",
            normalized.replace("\u03bb", "\u03bc"),
        ):
            with self.subTest(changed=changed):
                self.consume_changed(changed, literal=True)

    def test_real_excerpt_end_marker_uses_full_source_span(self):
        original = "# P1\n- [ ] A1 Real task\n- [x] A2 Boundary\n# P2\n"
        self.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "# P1", "end": "- [x] A2 Boundary"},
        ]
        self.prepare_pipeline(
            original, acceptance="# P1\n- [ ] A1 Real task\n",
            progress_spans=[[8, 9]], end_progress_span=[27, 28],
        )
        self.consume_changed(
            original.replace("[ ] A1", "[x] A1").replace("[x] A2", "[ ] A2"), literal=False,
        )

    def test_literal_excerpt_marker_never_normalizes_without_full_source_permission(self):
        original = "- - ```markdown\n    - [x] A1 Required literal\n    END\n    ```\n"
        self.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "    - [x] A1 Required literal", "end": "    END"},
        ]
        self.prepare_pipeline(original, acceptance="    - [x] A1 Required literal\n")
        self.consume_changed(original.replace("[x]", "[ ]"), literal=True)

    def excerpt_context_transition(self, before, after, *, literal=True):
        from review_contract import bind_work
        self.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "# P1", "end": "# End"},
        ]
        self.prepare_pipeline(
            before, acceptance="# P1\n- [ ] A1 Required task\n- [ ] A2 Required task\n",
            progress_spans=[[8, 9], [31, 32]],
        )
        (self.repo / "plan.md").write_bytes(after.encode("utf-8"))
        work = self.expected["work"]
        current = bind_work(
            self.repo, work_map=work["work_map"], package_id=work["package_id"],
            leaf_ids=work["leaf_ids"], acceptance_paths=work["acceptance_paths"],
        )
        with self.subTest(check="work identity"):
            self.assertEqual(current == work, not literal)
        self.consume_changed(after, literal=literal)

    def test_excerpt_context_all_space_into_fence_blocks(self):
        before = "# P1\n- [ ] A1 Required task\n- [ ] A2 Required task\n# End\n"
        self.excerpt_context_transition(before, "```markdown\n" + before + "```\n")

    def test_excerpt_context_fence_retains_literal_x_blocks(self):
        before = "# P1\n- [x] A1 Required task\n- [ ] A2 Required task\n# End\n"
        self.excerpt_context_transition(before, "```markdown\n" + before + "```\n")

    def test_excerpt_context_fence_literal_space_cannot_collide(self):
        before = "# P1\n- [x] A1 Required task\n- [ ] A2 Required task\n# End\n"
        self.excerpt_context_transition(before, "```markdown\n" + before.replace("[x]", "[ ]") + "```\n")

    def test_excerpt_context_pre_literal_space_cannot_collide(self):
        before = "# P1\n- [x] A1 Required task\n- [ ] A2 Required task\n# End\n"
        self.excerpt_context_transition(before, "<pre>\n" + before.replace("[x]", "[ ]") + "</pre>\n")

    def test_excerpt_context_genuine_progress_keeps_identity(self):
        before = "# P1\n- [x] A1 Required task\n- [ ] A2 Required task\n# End\n"
        self.excerpt_context_transition(before, before.replace("[x]", "[X]"), literal=False)

    def test_excerpt_context_unrelated_prefix_suffix_and_commit_keep_identity(self):
        before = "# P1\n- [x] A1 Required task\n- [ ] A2 Required task\n# End\n"
        after = (
            "# Unselected\n- Other list\n  - [x] A1 Outside selection\n\n"
            + before.replace("[x]", "[X]")
            + "\n<pre>\n- [ ] A2 Outside literal\n</pre>\n"
        )
        self.excerpt_context_transition(before, after, literal=False)
        self.git("add", "plan.md")
        self.git("commit", "-qm", "unrelated bookkeeping and task progress")
        self.consume_changed(after, literal=False)

    def test_excerpt_context_nested_unicode_crlf_progress_uses_relative_codepoints(self):
        before = "- Parent\r\n    - [x] A1 \u03bb \U0001f600 task\r\n    - [ ] A2 Required task\r\n# End"
        self.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "    - [x] A1 \u03bb \U0001f600 task", "end": "# End"},
        ]
        canonical = "    - [ ] A1 \u03bb \U0001f600 task\r\n    - [ ] A2 Required task\r\n"
        self.prepare_pipeline(before, acceptance=canonical, progress_spans=[[7, 8], [30, 31]])
        after = "# Unselected \u03bc\r\n- Earlier list\r\n\r\n" + before.replace("[x]", "[X]").replace("[ ] A2", "[x] A2")
        self.consume_changed(after, literal=False)
        for changed in (after.replace("\u03bb", "\u03bc"), after.replace("\r\n", "\n")):
            with self.subTest(changed=changed):
                self.consume_changed(changed, literal=True)

    def test_excerpt_context_end_marker_eligibility_remains_bound(self):
        before = "# P1\nRequired criterion.\n- [ ] A1 Boundary\n"
        self.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "# P1", "end": "- [ ] A1 Boundary"},
        ]
        self.prepare_pipeline(
            before, acceptance="# P1\nRequired criterion.\n", end_progress_span=[28, 29],
        )
        self.consume_changed("```markdown\n" + before + "```\n", literal=True)
        self.consume_changed(before.replace("[ ]", "[X]"), literal=False)

    def test_excerpt_context_literal_to_structural_space_is_not_same_identity(self):
        before = "```markdown\n# P1\n- [ ] A1 Required task\n- [ ] A2 Required task\n# End\n```\n"
        self.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "# P1", "end": "# End"},
        ]
        self.prepare_pipeline(
            before, acceptance="# P1\n- [ ] A1 Required task\n- [ ] A2 Required task\n",
        )
        self.consume_changed(before.removeprefix("```markdown\n").removesuffix("```\n"), literal=True)

    def test_excerpt_context_old_byte_only_receipt_needs_fresh_review(self):
        before = "# P1\n- [x] A1 Required task\n- [ ] A2 Required task\n# End\n"
        canonical = "# P1\n- [ ] A1 Required task\n- [ ] A2 Required task\n"
        self.request["acceptance_paths"] = [
            "spec.md", {"path": "plan.md", "start": "# P1", "end": "# End"},
        ]
        self.prepare_pipeline(before, acceptance=canonical, progress_spans=[[8, 9], [31, 32]])
        old_qa = json.loads(self.qa_file.read_text(encoding="utf-8"))
        work = self.expected["work"]
        entry = next(item for item in work["acceptance_manifest"] if item["path"] == "plan.md")
        byte_only_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.assertNotEqual(entry["sha256"], byte_only_hash)
        entry["sha256"] = byte_only_hash
        work["acceptance_digest"] = digest(work["acceptance_manifest"])
        self.expected_file.write_text(encoded(self.expected), encoding="utf-8")
        self.record()
        self.log()
        self.corroborate()
        old_qa["context_digest"] = digest(self.expected)
        self.qa_file.write_text(encoded(old_qa), encoding="utf-8")
        self.consume_changed(before, literal=True)
        history = self.run_command(["bash", SOURCE / "bin" / "li-review-read", "--json"], ok=0)
        self.assertIn(byte_only_hash, history.stdout)
        self.prepare_pipeline(before, acceptance=canonical, progress_spans=[[8, 9], [31, 32]])
        history = self.run_command(["bash", SOURCE / "bin" / "li-review-read", "--json"], ok=0)
        self.assertIn(byte_only_hash, history.stdout)

    def test_criteria_ids_and_approval_remain_bound_in_all_consumers(self):
        original = "- [ ] A1 Real task\n- [ ] A2 Real sibling\n"
        self.prepare_pipeline(original)
        for changed in (
            original.replace("Real task", "Different criterion"),
            original.replace("A1 ", "A3 "),
            original.replace("[ ] A1", "[!] A1"),
        ):
            with self.subTest(changed=changed):
                self.consume_changed(changed, literal=True)
        mapping = json.loads((self.repo / "work.json").read_text(encoding="utf-8"))
        mapping["status"] = "DRAFT"
        self.write_json("work.json", mapping)
        self.consume_changed(original, literal=True)

    def test_raw_selected_document_progress_still_blocks_all_consumers(self):
        original = "- [ ] A1 Real task\n- [ ] A2 Real sibling\n"
        self.request["selection"].append("plan.md")
        self.prepare_pipeline(original)
        self.consume_changed(original.replace("[ ] A1", "[x] A1"), literal=True)


class NativePathEvidence(Fixture):
    native_root_length = 216

    def setUp(self):
        super().setUp()
        self.configuration = native_io_path(self.repo / ".git" / "config").read_bytes()
        self.addCleanup(self.assert_fixture_configuration)
        environment = patch.dict(os.environ, self.env, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        if os.name == "nt":
            observed = self.git("config", "--show-scope", "--get", "core.longpaths")
            self.assertEqual(observed.stdout.strip().split(), ["command", "true"])
            local = self.run_command(["git", "config", "--local", "--get", "core.longpaths"])
            self.assertEqual(local.returncode, 1)

    def write(self, name, content):
        path = self.repo / name
        native_io_path(path.parent).mkdir(parents=True, exist_ok=True)
        native_io_path(path).write_bytes(content.encode("utf-8"))
        return path

    def assert_fixture_configuration(self):
        self.assertEqual(native_io_path(self.repo / ".git" / "config").read_bytes(), self.configuration)

    def good(self, *, controls=None, qa_controls=None):
        self.record(controls=controls)
        self.log()
        self.corroborate()
        self.assertEqual(self.qa(controls=qa_controls).returncode, 0)
        self.read()
        self.ship()

    def current(self, *, valid, qa_controls=None, qa_code=None):
        old_qa = native_io_path(self.qa_file).read_bytes()
        reader = self.read(ok=None)
        qa = self.qa(controls=qa_controls)
        native_io_path(self.qa_file).write_bytes(old_qa)
        ship = self.ship(ok=None)
        for role, result, code in (
            ("reader", reader, 0 if valid else 3),
            ("qa", qa, (0 if valid else 1) if qa_code is None else qa_code),
            ("ship", ship, 0 if valid else 3),
        ):
            with self.subTest(consumer=role):
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                if role != "qa":
                    self.assertEqual(json.loads(result.stdout)["ok"], valid)

    def test_native_policy_262_bytes_current_and_missing_are_observed(self):
        policy = "packs/rapid-development/policies/inventory.md"
        data = b"Synthetic owner-created policy.\n".ljust(848, b"p")
        self.assertEqual(len(data), 848)
        path = self.write(policy, data.decode("utf-8"))
        native_io_path(path).write_bytes(data)
        self.assertEqual(len(str(path)), 262)
        self.request["acceptance_paths"].append(policy)
        tests = observed_tests()
        tests["policy"]["source"] = policy
        self.request["qa_requirements"] = [qa_requirement(tests)]
        controls = [control(), control("quality"), tests]
        self.good(controls=controls, qa_controls=[tests])
        entry = next(item for item in self.expected["work"]["acceptance_manifest"] if item["path"] == policy)
        self.assertEqual(entry["sha256"], hashlib.sha256(data).hexdigest())
        native_io_path(path).write_bytes(data + b"changed\n")
        self.current(valid=False, qa_controls=[tests])
        native_io_path(path).unlink()
        self.current(valid=False, qa_controls=[tests])
        native_io_path(path).write_bytes(data)
        self.current(valid=True, qa_controls=[tests])

    def test_native_long_authority_evidence_and_current_record_reads(self):
        directory = "authority/" + "a" * 58
        files = {role: f"{directory}/{role}.md" for role in ("spec", "plan", "prompt")}
        for role, name in files.items():
            data = native_io_path(self.repo / f"{role}.md").read_bytes()
            native_io_path(self.write(name, "")).write_bytes(data)
        mapping = f"{directory}/work.json"
        self.write_json(mapping, {
            "schema_version": 1, "workflow": "lintel", "status": "APPROVED",
            **files, "tasks": files["plan"],
        })
        self.request.update(work_map=mapping, acceptance_paths=list(files.values()))
        evidence = "observations/" + "e" * 63 + "/checks.txt"
        self.write(evidence, "Synthetic executed-test observation.\n")
        controls = [control(), control("quality"), observed_tests()]
        for item in controls:
            item["evidence"] = [evidence]
        metadata = self.repo / "metadata" / ("m" * 59)
        native_io_path(metadata).mkdir(parents=True)
        self.request_file = metadata / "request.json"
        self.expected_file = metadata / "expected.json"
        self.observed_file = metadata / "corroboration.json"
        self.qa_file = metadata / "qa.json"
        self.request["record_path"] = ".claude/runtime/reviews/native-" + "r" * 60 + ".json"
        self.record_file = self.repo / self.request["record_path"]
        self.good(controls=controls, qa_controls=[controls[-1]])
        before = deepcopy(self.expected)
        self.prepare()
        self.assertEqual(before, self.expected)
        self.assertNotIn("//?/", encoded(self.expected))
        self.current(valid=True, qa_controls=[controls[-1]])
        old_record = native_io_path(self.record_file).read_bytes()
        native_io_path(self.record_file).write_text('{"not":"a review"}', encoding="utf-8")
        self.current(valid=False, qa_controls=[controls[-1]])
        native_io_path(self.record_file).write_bytes(old_record)
        native_io_path(self.repo / evidence).write_bytes(b"late evidence change\n")
        from review_contract import ContractError, verify_qa
        stale_qa = json.loads(native_io_path(self.qa_file).read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ContractError, "QA evidence files changed"):
            verify_qa(self.repo, stale_qa, expected=self.expected)
        # Fresh QA can observe new evidence; the stale review and restored old QA still cannot ship.
        self.current(valid=False, qa_controls=[controls[-1]], qa_code=0)

    def test_native_selected_directory_keeps_dirty_new_tracked_and_deleted(self):
        selected = "selected/" + "d" * 58
        tracked, deleted, added = (f"{selected}/{name}.txt" for name in ("tracked", "deleted", "new"))
        self.write(tracked, "original tracked\n")
        self.write(deleted, "original deleted\n")
        self.git("add", selected)
        self.git("commit", "-qm", "native selected baseline")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.request.update(base=self.base, selection=[selected])
        self.write(tracked, "dirty tracked\n")
        native_io_path(self.repo / deleted).unlink()
        self.write(added, "new selected\n")
        self.good()
        entries = {item["path"]: item for item in self.expected["snapshot"]["entries"]}
        self.assertEqual(set(entries), {tracked, deleted, added})
        self.assertEqual(entries[deleted]["worktree"], {"kind": "absent", "mode": "000000", "sha256": None})
        self.assertEqual(entries[added]["base"]["kind"], "absent")
        self.assertEqual(entries[tracked]["base"]["sha256"], hashlib.sha256(b"original tracked\n").hexdigest())
        self.assertEqual(entries[tracked]["worktree"]["sha256"], hashlib.sha256(b"dirty tracked\n").hexdigest())
        extra = self.write(f"{selected}/later-new.txt", "later selected content\n")
        self.current(valid=False)
        native_io_path(extra).unlink()
        self.current(valid=True)
        self.git("add", tracked)
        self.current(valid=False)
        self.git("restore", "--staged", tracked)
        self.current(valid=True)

    def test_native_audit_and_long_cli_inputs_preserve_latest_decision(self):
        audit_dir = self.repo / "audit" / ("j" * 63)
        self.env["LINTEL_AUDIT_DIR"] = audit_dir.as_posix()
        self.good()
        decision = deepcopy(self.review)
        decision["status"] = "fail"
        self.log(decision)
        self.read(ok=3)
        self.ship(ok=3)
        self.log()
        self.read()
        self.ship()
        audit = audit_dir / "reviews.jsonl"
        with native_io_path(audit).open("ab") as stream:
            stream.write(b'{"schema_version":2,"status":"fail"}\n')
        self.read(ok=3)
        self.ship(ok=3)
        history = self.run_command(["bash", SOURCE / "bin/li-review-read", "--json"], ok=0)
        self.assertIn('"status":"fail"', history.stdout)

    def test_native_explicit_ignored_domain_record_is_bound_not_omitted(self):
        relative = ".claude/runtime/state/domains/pipeline-fixture/i0001/ta/01-result.json"
        payload = {"fixture_only": "fresh P05-owned opaque input, not a P12 decision", "value": 1}
        path = self.write_json(relative, payload)
        original = native_io_path(path).read_bytes()
        self.assertGreater(len(str(path)), 263)
        self.assertEqual(self.git("check-ignore", relative).stdout.strip(), relative)
        self.request["selection"] = [relative]
        self.good()
        entries = self.expected["snapshot"]["entries"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["path"], relative)
        self.assertEqual(entries[0]["base"], {"kind": "absent", "mode": "000000", "sha256": None})
        self.assertEqual(entries[0]["worktree"]["sha256"], hashlib.sha256(original).hexdigest())
        self.write_json(relative, {**payload, "value": 2})
        self.current(valid=False)
        native_io_path(path).unlink()
        self.current(valid=False)
        native_io_path(path).write_bytes(original)
        self.current(valid=True)

    def test_native_metadata_errors_are_not_missing_snapshots(self):
        import review_contract as contract
        selected = self.write("selected/" + "e" * 58 + "/present.txt", "bound content\n")
        original = Path.lstat

        def failing(path, *args, **kwargs):
            if path_identity(path) == path_identity(selected):
                raise OSError(errno.EINVAL, "injected metadata observation failure")
            return original(path, *args, **kwargs)

        with patch.object(Path, "lstat", failing), self.assertRaises(OSError):
            contract.snapshot(self.repo, base=self.base, selection=[selected.relative_to(self.repo).as_posix()])

    def test_native_audit_observation_errors_are_not_empty_history(self):
        spec = importlib.util.spec_from_file_location("native_review_cli_test", CLI)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        audit = self.write("audit/" + "e" * 63 + "/reviews.jsonl", "{}\n")
        with patch.object(Path, "read_bytes", side_effect=PermissionError("injected audit read refusal")):
            with self.assertRaises(PermissionError):
                module.audit_records(audit)
        native_io_path(audit).unlink()
        self.assertEqual(module.audit_records(audit), [])

    def test_native_representation_and_regular_file_rules_keep_logical_names(self):
        from review_contract import ContractError, bind_work, evidence_manifest
        evidence = "evidence/" + "n" * 60 + "/evidence.txt"
        self.write(evidence, "unchanged synthetic observation\n")
        controls = [control()]
        controls[0]["evidence"] = [evidence]
        ordinary = evidence_manifest(self.repo, controls)
        self.assertEqual(ordinary[0]["path"], evidence)
        self.assertEqual(evidence_manifest(native_io_path(self.repo), controls), ordinary)
        work = dict(work_map="work.json", package_id="P1", leaf_ids=["A1", "A2"],
                    acceptance_paths=["spec.md", "plan.md"])
        self.assertEqual(bind_work(self.repo, **work), bind_work(native_io_path(self.repo), **work))
        for invalid in ("../outside.txt", ".git/config", "input:stream"):
            controls[0]["evidence"] = [invalid]
            with self.subTest(path=invalid), self.assertRaises(ContractError):
                evidence_manifest(self.repo, controls)
        controls[0]["evidence"] = [evidence.rsplit("/", 1)[0]]
        with self.assertRaises(ContractError):
            evidence_manifest(self.repo, controls)

    def test_native_deep_authority_root_includes_required_declaration(self):
        from review_contract import bind_work, evidence_manifest
        root = self.repo / ("deep-root-" + "x" * 75)
        native_io_path(root).mkdir()
        for name, text in (
            ("spec.md", "A1: synthetic bound acceptance\n"),
            ("plan.md", "- [ ] A1 Synthetic task\n"),
            ("prompt.md", "Implement the owned synthetic task.\n"),
            ("work.json", encoded({
                "schema_version": 1, "workflow": "lintel", "status": "APPROVED",
                "spec": "spec.md", "plan": "plan.md", "tasks": "plan.md", "prompt": "prompt.md",
            })),
            (".claude/profile-requirements.json", '{"schema_version":1,"required_pack":"synthetic-required"}'),
        ):
            path = root / name
            native_io_path(path.parent).mkdir(parents=True, exist_ok=True)
            native_io_path(path).write_bytes(text.encode("utf-8"))
        arguments = dict(work_map="work.json", package_id="P1", leaf_ids=["A1"],
                         acceptance_paths=["spec.md", "plan.md"])
        expected = bind_work(root, **arguments)
        self.assertIn(".claude/profile-requirements.json", expected["acceptance_paths"])
        self.assertEqual(bind_work(native_io_path(root), **arguments), expected)
        checks = [control()]
        checks[0]["evidence"] = ["spec.md"]
        self.assertEqual(evidence_manifest(root, checks), [{
            "path": "spec.md", "sha256": hashlib.sha256(b"A1: synthetic bound acceptance\n").hexdigest(),
        }])

    def test_native_domain_context_and_swarm_latest_source_calls(self):
        import domain_result
        import swarm_evidence
        from profile_context import ProfileConfig, load_profile_context, profile_reference, required_policy
        from review_contract import ContractError
        home = self.root / "profile-home"
        config = ProfileConfig(
            source=SOURCE, repo=self.repo, home=home, packs=home / "packs",
            pointer=home / "packs" / "active-pack", context_id="p05-native-owned",
        )
        profile = load_profile_context(config, create=True)
        self.request.update(profile=profile_reference(profile), required_policy=required_policy(profile))
        policy = "packs/rapid-development/policies/inventory.md"
        self.write(policy, "Fresh owner-created acceptance; no P14 input or pin.\n")
        self.request["acceptance_paths"].append(policy)
        metadata = self.repo / "metadata" / ("q" * 63)
        native_io_path(metadata).mkdir(parents=True)
        self.expected_file = metadata / "expected.json"
        self.observed_file = metadata / "corroboration.json"
        self.good()
        request = {"input_context": deepcopy(self.expected)}
        pointers = {
            "context": self.expected_file.relative_to(self.repo).as_posix(),
            "corroboration": self.observed_file.relative_to(self.repo).as_posix(),
            "review_skill": "review",
        }
        domain_result._current_context(self.repo, request, self.expected, config)
        self.assertTrue(swarm_evidence._latest_review(self.repo, pointers, config)["ok"])
        original = native_io_path(self.repo / policy).read_bytes()
        native_io_path(self.repo / policy).write_bytes(b"changed selected acceptance\n")
        with self.assertRaisesRegex(ContractError, "Selected work/acceptance sources changed"):
            domain_result._current_context(self.repo, request, self.expected, config)
        with self.assertRaisesRegex(ContractError, "Latest applicable shared review blocks"):
            swarm_evidence._latest_review(self.repo, pointers, config)
        native_io_path(self.repo / policy).write_bytes(original)
        rejected = deepcopy(self.review)
        rejected["status"] = "fail"
        self.log(rejected)
        with self.assertRaisesRegex(ContractError, "Latest applicable shared review blocks"):
            swarm_evidence._latest_review(self.repo, pointers, config)

    @unittest.skipUnless(os.name == "nt", "platform: windows-only; actual native Windows junction policy")
    def test_native_junction_and_symlink_rules_are_not_replaced_by_provider_policy(self):
        import _winapi
        from review_contract import ContractError, _path, evidence_manifest, snapshot
        real = self.repo / "owned"
        filename = "checks-" + "d" * 63 + ".txt"
        native_io_path(real).mkdir()
        native_io_path(real / filename).write_bytes(b"in-root evidence\n")
        inside = self.repo / "inside-junction"
        # The target is stored as data; only the junction creation path is an I/O operand.
        _winapi.CreateJunction(str(real), str(native_io_path(inside)))
        self.assertEqual(path_identity(Path(os.readlink(native_io_path(inside)))), path_identity(real))
        selected = "inside-junction/" + filename
        self.assertEqual(len(str(self.repo)), 216)
        self.assertGreater(len(str(self.repo / selected)), 262)
        self.assertEqual(_path(self.repo, selected, regular=True), self.repo / selected)
        item = control()
        item["evidence"] = [selected]
        self.assertEqual(evidence_manifest(self.repo, [item]), [{
            "path": selected, "sha256": hashlib.sha256(b"in-root evidence\n").hexdigest(),
        }])
        with self.assertRaisesRegex(ContractError, "junction/alias"):
            snapshot(self.repo, base=self.base, selection=["inside-junction"])
        outside = self.root / "outside"
        native_io_path(outside).mkdir()
        native_io_path(outside / "checks.txt").write_bytes(b"outside sentinel\n")
        escape = self.repo / "outside-junction"
        _winapi.CreateJunction(str(outside), str(native_io_path(escape)))
        with self.assertRaisesRegex(ContractError, "escapes repository"):
            _path(self.repo, "outside-junction/checks.txt", regular=True)
        link_name = "selected-link-" + "s" * 60
        link = self.repo / link_name
        native_io_path(link).symlink_to("source.txt")
        observed = snapshot(self.repo, base=self.base, selection=[link_name])
        self.assertEqual(observed["entries"][0]["worktree"], {
            "kind": "symlink", "mode": "120000", "sha256": hashlib.sha256(b"source.txt").hexdigest(),
        })
        with self.assertRaisesRegex(ContractError, "regular local file"):
            _path(self.repo, link_name, regular=True)
        directory_link = self.repo / "directory-link"
        native_io_path(directory_link).symlink_to(real, target_is_directory=True)
        with self.assertRaisesRegex(ContractError, "symlink or non-directory"):
            _path(self.repo, "directory-link/checks.txt", regular=True)
        self.assertEqual(native_io_path(outside / "checks.txt").read_bytes(), b"outside sentinel\n")


class MandatoryControls(Fixture):
    def evaluate(self, controls, policy=None):
        from review_contract import evaluate_controls
        return evaluate_controls(controls, required_policy=policy or neutral_policy())

    def test_single_mandatory_failure_dominates_any_score(self):
        bad = control("security", status="fail")
        advice = control("style", requirement="advisory")
        advice["advisory_score"] = 100
        for status in ("fail", "error", "unverified"):
            with self.subTest(status=status):
                bad["status"] = status
                result = self.evaluate([bad, advice])
                self.assertTrue(result["blocked"])
        advice["status"] = "fail"
        self.assertFalse(self.evaluate([control(), advice])["blocked"])

    def test_no_controls_and_neutral_is_not_verified_compliance(self):
        result = self.evaluate([])
        self.assertFalse(result["blocked"])
        self.assertEqual(result["assurance"], "no_applicable_controls")
        self.assertNotEqual(result["status"], "pass")

    def test_unknown_required_policy_blocks_without_erasing_requirement(self):
        policy = neutral_policy()
        policy["required"] = True
        for status in ("not_required", "unverified", "error", "loaded"):
            with self.subTest(status=status):
                policy["status"] = status
                self.assertTrue(self.evaluate([control()], policy)["blocked"])

    def test_required_policy_optional_reason_and_unresolved_strings(self):
        policy = neutral_policy()
        del policy["reason"]
        policy.update(required=True, status="loaded", source="fixture://policy", version="1", applicability="applicable")
        self.assertFalse(self.evaluate([control()], policy)["blocked"])
        for value in ("", "   ", None):
            with self.subTest(value=value):
                policy["source"] = value
                self.assertTrue(self.evaluate([control()], policy)["blocked"])

    def test_not_applicable_needs_source_version_reason_and_evidence(self):
        item = control()
        item["applicability"] = "not_applicable"
        item["status"] = "unverified"
        self.assertFalse(self.evaluate([item])["blocked"])
        for key in ("source", "version"):
            bad = deepcopy(item)
            bad["policy"][key] = None
            self.assertTrue(self.evaluate([bad])["blocked"])
        item["applicability"] = "unknown"
        self.assertTrue(self.evaluate([item])["blocked"])
        item["applicability"] = "not_applicable"
        item["evidence"] = []
        self.assertTrue(self.evaluate([item])["blocked"])
        item = control(status="error")
        item["applicability"] = "not_applicable"
        self.assertTrue(self.evaluate([item])["blocked"])

    def test_wcag_aa_3_5_normal_fails_and_large_text_can_pass(self):
        item = control("contrast", "contrast")
        item["policy"]["source"] = "https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html"
        item["policy"]["version"] = "WCAG 2.2 SC 1.4.3"
        item["observation"] = {"ratio": 3.5, "text_size": "normal"}
        self.assertTrue(self.evaluate([item])["blocked"])
        item["observation"]["text_size"] = "large"
        self.assertFalse(self.evaluate([item])["blocked"])
        item["observation"] = {"ratio": 4.5, "text_size": "normal"}
        self.assertFalse(self.evaluate([item])["blocked"])

    def test_browser_and_zero_tests_are_unverified(self):
        for item in (control("browser", "browser"), control("tests", "tests")):
            with self.subTest(kind=item["kind"]):
                self.assertTrue(self.evaluate([item])["blocked"])
                self.assertEqual(self.evaluate([item])["controls"][0]["effective_status"], "unverified")
        browser = control("browser", "browser")
        browser["observation"] = {"tool": "fixture-browser", "executed": True, "states": ["keyboard@desktop"]}
        self.assertFalse(self.evaluate([browser])["blocked"])
        tests = control("tests", "tests")
        tests["observation"] = {"command": "fixture-test", "executed": 0, "failed": 0, "skipped": 0, "exit_code": 0}
        self.assertTrue(self.evaluate([tests])["blocked"])

    def test_controls_cannot_bypass_actual_writer_reader_ship(self):
        cases = [
            control("required-security", status="fail"),
            control("required-scan", status="error"),
            control("tests", "tests"),
            control("browser", "browser"),
            control("policy", "policy"),
            control("contrast", "contrast"),
        ]
        cases[-2]["policy"]["version"] = None
        cases[-1]["observation"] = {"ratio": 3.5, "text_size": "normal"}
        self.prepare()
        self.qa()
        for item in cases:
            with self.subTest(kind=item["id"]):
                self.record(controls=[control(), control("quality"), item])
                self.log()
                self.corroborate()
                self.read(ok=3)
                self.ship(ok=3)

    def test_advisory_failure_preserves_valid_clearance(self):
        advice = control("preference", requirement="advisory", status="fail")
        advice["advisory_score"] = 20
        self.record(controls=[control(), control("quality"), advice])
        self.log()
        self.corroborate()
        self.qa()
        self.read()
        self.ship()

    def test_malformed_control_and_duplicate_ids_rejected(self):
        from review_contract import ContractError
        for field, value in (
            ("requirement", "optional-ish"), ("status", "GREEN"),
            ("applicability", "maybe"), ("reason", ""),
        ):
            item = control()
            item[field] = value
            with self.subTest(field=field), self.assertRaises(ContractError):
                self.evaluate([item])
        with self.assertRaises(ContractError):
            self.evaluate([control(), control()])

    def test_regulatory_known_version_and_unknown_refusal(self):
        item = control("gdpr-article-34", "policy")
        item["policy"].update(
            source="https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng",
            version="2016/679 Article 34", jurisdiction="EU",
            actor="controller", effective_date="2018-05-25",
            applicability="High-risk breach communication; assess Article 34 exceptions.",
        )
        self.assertFalse(self.evaluate([item])["blocked"])
        for field in ("source", "version", "jurisdiction", "actor", "effective_date"):
            missing = deepcopy(item)
            missing["policy"][field] = None
            self.assertTrue(self.evaluate([missing])["blocked"])

    def test_license_contexts_are_not_label_only_verdicts(self):
        tool = control("isolated-gpl-tool", requirement="advisory")
        tool["reason"] = "Fixture policy accepts isolated build tooling; no redistributed combination."
        combined = control("redistributed-combination", status="fail")
        combined["reason"] = "Fixture mandatory distribution policy conflicts with resulting obligations."
        unknown = control("unparsed-license", status="unverified")
        self.assertFalse(self.evaluate([tool])["blocked"])
        self.assertTrue(self.evaluate([combined])["blocked"])
        self.assertTrue(self.evaluate([unknown])["blocked"])


class HookEvidence(Fixture):
    def hook(self, command="gh pr merge 7 --squash"):
        return self.run_command([
            "bash", SOURCE / "hooks" / "shared" / "no-merge-without-review" / "run.sh", command,
        ], ok=0)

    def test_advisory_hook_consumes_real_latest_reader(self):
        self.assertIn("WARN", self.hook().stdout)
        self.record()
        self.log()
        self.corroborate()
        self.env.update(
            LINTEL_REVIEW_CONTEXT=self.expected_file.as_posix(),
            LINTEL_REVIEW_CORROBORATION=self.observed_file.as_posix(),
        )
        self.assertNotIn("WARN", self.hook().stdout)
        self.write("source.txt", "later dirty edit\n")
        self.assertIn("WARN", self.hook().stdout)
        self.write("source.txt", "after\n")
        rejection = deepcopy(self.review)
        rejection["status"] = "fail"
        self.log(rejection)
        self.assertIn("WARN", self.hook().stdout)
        self.assertNotIn("WARN", self.hook("git status").stdout)

    def test_legacy_location_or_cleared_string_never_suppresses_warning(self):
        self.env.update(LINTEL_REVIEW_CONTEXT=self.expected_file.as_posix())
        self.prepare()
        legacy = self.root / "home" / ".lintel" / "review-log" / "entries.jsonl"
        legacy.parent.mkdir(parents=True)
        legacy.write_text(encoded({"kind": "review", "status": "CLEARED", "commit": self.base}), encoding="utf-8")
        self.assertIn("WARN", self.hook().stdout)
        audit = self.repo / ".claude/runtime/audit/reviews.jsonl"
        audit.parent.mkdir(parents=True, exist_ok=True)
        audit.write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertIn("WARN", self.hook().stdout)


if __name__ == "__main__":
    suite_name = sys.argv.pop(1) if len(sys.argv) > 1 else "evidence"
    classes = {
        "legacy": (LegacyRegressions,),
        "evidence": (LegacyRegressions, ReviewEvidence, MarkdownBoundaryEvidence, NativePathEvidence),
        "boundaries": (MarkdownBoundaryEvidence,),
        "native": (NativePathEvidence,),
        "controls": (MandatoryControls,), "hook": (HookEvidence,),
    }[suite_name]
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls) for cls in classes)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
