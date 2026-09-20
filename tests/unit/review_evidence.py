# component: review-contract-regressions
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/packages/P05.md
# constraints: synthetic evidence is not an independent review of Lintel
# last_intent_review: 2026-09-20
"""Exercise real producer, audit reader and SHIP with isolated Git fixtures."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[2]
CLI = SOURCE / "bin" / "li-review-evidence.py"
sys.path.insert(0, str(SOURCE / "lib"))


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


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lintel-review-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "target with spaces"
        self.repo.mkdir()
        self.env = dict(os.environ)
        for key in ("LINTEL_AUDIT_DIR", "LINTEL_WORK_MAP", "CLAUDE_PLUGIN_ROOT"):
            self.env.pop(key, None)
        self.env.update({
            "HOME": (self.root / "home").as_posix(), "USERPROFILE": str(self.root / "home"),
            "LINTEL_HOME": (self.root / "home" / ".lintel").as_posix(),
            "GSTACK_HOME": (self.root / "legacy").as_posix(),
            "LINTEL_REPO_ROOT": self.repo.as_posix(), "LINTEL_SOURCE_ROOT": SOURCE.as_posix(),
            "LINTEL_PYTHON": Path(sys.executable).as_posix(), "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull, "PYTHONDONTWRITEBYTECODE": "1",
        })
        (self.root / "home").mkdir()
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
            "required_controls": ["spec", "quality"],
        }
        self.expected_file = self.root / "expected.json"
        self.observed_file = self.root / "corroboration.json"
        self.qa_file = self.root / "qa.json"
        self.record_file = self.repo / self.request["record_path"]

    def run_command(self, args, *, ok=None, input=None):
        if args[0] == "bash":
            # Avoid Windows CRT/MSYS double-quoting of literal JSON argv.
            self.assertIsNone(input)
            input = "exec " + shlex.join(
                arg.as_posix() if isinstance(arg, Path) else str(arg) for arg in args
            ) + "\n"
            args = ["bash"]
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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, name, value):
        return self.write(name, encoded(value) + "\n")

    def prepare(self):
        request_file = self.root / "request.json"
        request_file.write_text(encoded(self.request), encoding="utf-8")
        result = self.cli("prepare", "--repo", self.repo, "--request", request_file)
        self.expected = json.loads(result.stdout)
        self.expected_file.write_text(encoded(self.expected), encoding="utf-8")
        return self.expected

    def record(self, *, status="pass", controls=None):
        if not hasattr(self, "expected"):
            self.prepare()
        self.review = {
            "schema_version": 1, "skill": "review", "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "Synthetic decision used only by this regression test.",
            "context": deepcopy(self.expected),
            "reviewer": {"id": "reviewer", "context": "review-1"},
            "provenance": "declared",
            "controls": controls if controls is not None else [control(), control("quality")],
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
            {"path": path, "sha256": hashlib.sha256((self.repo / path).read_bytes()).hexdigest()}
            for path in paths
        ]

    def log(self, record=None, *, ok=0):
        record = self.review if record is None else record
        self.record_file.parent.mkdir(parents=True, exist_ok=True)
        self.record_file.write_text(encoded(record), encoding="utf-8")
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
        self.observed_file.write_text(encoded(data), encoding="utf-8")
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
        inputs.write_text(encoded({"controls": controls}), encoding="utf-8")
        result = self.cli(
            "qa", "--repo", self.repo, "--expected", self.expected_file,
            "--input", inputs, ok=None,
        )
        self.qa_file.write_text(result.stdout, encoding="utf-8")
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
        ):
            target = installed / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / name, target)
        self.write("lib/review_contract.py", "raise RuntimeError('target code executed')\n")
        env = dict(self.env)
        env.pop("LINTEL_SOURCE_ROOT")
        command = "exec " + shlex.join([
            "bash", (installed / "bin" / "li-review-read").as_posix(), "--skill", "review",
            "--expected", self.expected_file.as_posix(), "--corroboration", self.observed_file.as_posix(),
            "--gate-json",
        ]) + "\n"
        result = subprocess.run(
            ["bash"], input=command, cwd=self.root, env=env, text=True, encoding="utf-8",
            capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])
        self.assertFalse((installed / ".claude").exists())

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
            ("schema_version", None), ("schema_version", 2), ("context", None),
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
                "format": "review-v1", "status": "fail",
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
        for field, value in (
            ("attempt_id", "attempt-2"),
            ("profile", {
                "schema_version": 1, "context_id": "strict", "generation": 1,
                "name": "strict", "version": "1", "digest": "sha256:" + "a" * 64,
            }),
            ("required_controls", ["spec", "quality", "missing-control"]),
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
        self.request["required_controls"] += ["document", "tests"]
        document = control("document")
        document["reason"] = "Fixture document links and examples were checked."
        document["observation"] = {"command": "fixture-document-check", "executed": 1}
        tests_na = control("tests", "tests", status="unverified")
        tests_na["applicability"] = "not_applicable"
        tests_na["reason"] = "Approved spec limits this package to checked documentation; executable tests do not apply."
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
                self.assertEqual(self.qa(controls=[document, bad]).returncode, 3)
                self.ship(ok=3)
        for counts in (
            {"executed": 0, "failed": 0, "skipped": 0, "exit_code": 0},
            {"executed": 2, "failed": 1, "skipped": 0, "exit_code": 1},
            {"executed": 2, "failed": 0, "skipped": 1, "exit_code": 0},
        ):
            required_test = control("tests", "tests")
            required_test["observation"] = {"command": "fixture-tests", **counts}
            with self.subTest(required_tests=counts):
                self.assertEqual(self.qa(controls=[document, required_test]).returncode, 3)
                self.ship(ok=3)

    def test_qa_needs_actual_applicable_validation_not_only_exemptions(self):
        self.good()
        tests_na = control("tests", "tests", status="unverified")
        tests_na["applicability"] = "not_applicable"
        self.assertEqual(self.qa(controls=[tests_na]).returncode, 1)
        self.ship(ok=3)
        advice = control("optional-document", requirement="advisory")
        self.assertEqual(self.qa(controls=[advice, tests_na]).returncode, 1)
        self.ship(ok=3)


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
        "legacy": (LegacyRegressions,), "evidence": (LegacyRegressions, ReviewEvidence),
        "controls": (MandatoryControls,), "hook": (HookEvidence,),
    }[suite_name]
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls) for cls in classes)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
