# component: observation-learning-tests
# implements: ADR-0006, ADR-0008, ADR-0028
# intent: .claude/plans/universal-implementation/packages/P08.md
# constraints: synthetic home, Git ceilings and fixture repositories only; no hook activation, P10 surface or real profile access
# last_intent_review: 2026-09-23
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, required=True)
args, remaining = parser.parse_known_args()
ROOT = args.root.resolve()
FIXTURES = ROOT / "tests/fixtures/lessons"
EXPECTED = json.loads((FIXTURES / "expected.json").read_text(encoding="utf-8"))
BASH = shutil.which("bash") or "bash"
PYTHON = sys.executable
EVENTS = ROOT / "bin/li-events.py"
LESSONS = ROOT / "bin/li-lessons.py"
PROMOTE = ROOT / "bin/li-lessons-promote"
BASELINE = ROOT / "scaffolding/01-foundation/.claude/memory/lessons.md"
VERDICT_KEYS = ("status", "evidence", "verification", "enforcement", "class", "check")
FORBIDDEN = re.compile(r"\b(healthy|dead|firing|enforced|complete)\b")
LESSON_DIAGNOSTIC = re.compile(r"^WARN \[lintel/lessons\]: line (\d+): ([a-z_]+): ", re.M)
PROVENANCE = re.compile(
    r"<!-- lintel-promotion: source_label=fixture-app; source_id=L-002; "
    r"source_commit=(unrecorded|[0-9a-f]{40}); promoted_on=\d{4}-\d{2}-\d{2}(; operator=[^ ;]+)? -->")
IS_WINDOWS = os.name == "nt"


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def fixture_bytes(name: str, newline: bytes = b"\n") -> bytes:
    data = (FIXTURES / name).read_bytes().replace(b"\r\n", b"\n")
    return data if newline == b"\n" else data.replace(b"\n", newline)


def fixture_lines(name: str) -> list[str]:
    return fixture_bytes(name).decode("utf-8").split("\n")


def same_path(left, right) -> bool:
    return os.path.normcase(os.path.abspath(str(left))) == os.path.normcase(os.path.abspath(str(right)))


RUNTIME_NOISE = re.compile(r"(?m)^bash(?:\.exe)?: warning: could not find /tmp, please create!\r?\n?")


def product_stderr(text: str) -> str:
    """Drop the MSYS runtime's intermittent /tmp warning; it is not emitted by Lintel code."""
    return RUNTIME_NOISE.sub("", text)


def event(kind="frozen_zone_warn", ts="2026-09-20T10:00:00Z", **fields) -> str:
    value = {"ts": ts, "kind": kind, "operator": "fixture", "cycle_id": "unknown"}
    if kind == "frozen_zone_warn":
        value.update(hook="frozen-zone-warn", tier="warn", frozen_path="src/",
                     edit_target="src/app.py", source="session-freeze")
    value.update(fields)
    return json.dumps(value, separators=(",", ":"))


def has_python(folder: str) -> bool:
    if "windowsapps" in folder.lower():
        return True
    return any(os.path.exists(os.path.join(folder, name))
               for name in ("python", "python3", "python.exe", "python3.exe"))


class Sandbox(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lintel-observations-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.home = self.root / "home"
        scratch = self.root / "tmp"
        for folder in (self.home / "AppData/Roaming", self.home / "AppData/Local", scratch):
            folder.mkdir(parents=True)
        drive, tail = os.path.splitdrive(str(self.home))
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("LINTEL_", "CLAUDE_", "GIT_", "GSTACK_", "PYTHONDONTWRITEBYTECODE"))}
        self.env.update(
            HOME=self.home.as_posix(), USERPROFILE=str(self.home), HOMEDRIVE=drive,
            HOMEPATH=tail or str(self.home), APPDATA=str(self.home / "AppData/Roaming"),
            LOCALAPPDATA=str(self.home / "AppData/Local"), TEMP=str(scratch), TMP=str(scratch),
            TMPDIR=scratch.as_posix(), LINTEL_HOME=(self.home / ".lintel").as_posix(),
            LINTEL_SOURCE_ROOT=ROOT.as_posix(), LINTEL_OPERATOR="fixture", LINTEL_ASCII="1",
            LINTEL_LESSONS_LOCK_SECONDS="0.3", GIT_CEILING_DIRECTORIES=str(self.root),
            GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_NAME="Fixture",
            GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_NAME="Fixture",
            GIT_COMMITTER_EMAIL="fixture@example.invalid", PYTHONDONTWRITEBYTECODE="1")

    def run_cmd(self, argv, *, cwd=None, env=None, stdin="", expect=None, binary=False):
        options = {} if binary else {"text": True, "encoding": "utf-8", "errors": "replace"}
        result = subprocess.run([str(item) for item in argv], cwd=str(cwd or self.root),
                                env=self.env if env is None else env,
                                input=stdin.encode() if binary else stdin, capture_output=True, **options)
        if expect is not None:
            self.assertEqual(result.returncode, expect,
                             f"{argv}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        return result

    def bash(self, script, **kwargs):
        return self.run_cmd([BASH, "-c", script], **kwargs)

    def events(self, *arguments, **kwargs):
        return self.run_cmd([PYTHON, EVENTS, *arguments], **kwargs)

    def lessons(self, *arguments, **kwargs):
        return self.run_cmd([PYTHON, LESSONS, *arguments], **kwargs)

    def git(self, repo, *arguments, expect=0):
        return self.run_cmd(["git", "-C", repo, *arguments], expect=expect)

    def make_repo(self, name, *, v5=True, agents=False):
        repo = self.root / name
        repo.mkdir(parents=True)
        self.git(repo, "init", "-q")
        self.git(repo, "config", "core.autocrlf", "false")
        self.git(repo, "symbolic-ref", "HEAD", "refs/heads/main")
        if v5:
            write(repo / ".claude/lintel-layout.yaml", "layout_version: 5\n")
        if agents:
            write(repo / "AGENTS.md", "Synthetic work only.\n")
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-q", "--allow-empty", "-m", "fixture")
        return repo

    def summary(self, path, *extra, expect=None, env=None):
        result = self.events("summary", "--file", path, *extra, expect=expect, env=env)
        return result, (json.loads(result.stdout) if result.stdout.strip() else None)

    def records(self, path, *extra, expect=None, env=None):
        result = self.events("records", "--file", path, *extra, expect=expect, env=env)
        return result, [json.loads(line) for line in result.stdout.splitlines() if line.strip()]

    def assert_no_verdict(self, value):
        """Only verdict-bearing values are checked; keys, codes and kind names are exempt."""
        if isinstance(value, list):
            for item in value:
                self.assert_no_verdict(item)
            return
        if not isinstance(value, dict):
            return
        for key in VERDICT_KEYS:
            if isinstance(value.get(key), str):
                self.assertIsNone(FORBIDDEN.search(value[key]), value[key])
        if isinstance(value.get("detail"), str):
            self.assertIsNone(FORBIDDEN.search(value["detail"]), value["detail"])
        for key in ("by_kind", "diagnostics"):
            nested = value.get(key)
            self.assert_no_verdict(list(nested.values()) if isinstance(nested, dict) else nested)


class IsolationTests(Sandbox):
    def test_every_home_derived_path_is_synthetic(self):
        probe = self.run_cmd([PYTHON, "-c", "import os; from pathlib import Path; "
                              "print(Path.home()); print(os.path.expanduser('~'))"], expect=0)
        shell = self.bash('p() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; '
                          'else printf "%s\\n" "$1"; fi; }\np "$HOME"\np "$LINTEL_HOME"', expect=0)
        values = probe.stdout.splitlines() + shell.stdout.splitlines() + [self.env["USERPROFILE"]]
        self.assertEqual(len(values), 5)
        for value in values:
            self.assertTrue(os.path.normcase(os.path.abspath(value)).startswith(
                os.path.normcase(str(self.root))), value)


class ObservationPreservation(Sandbox):
    def setUp(self):
        super().setUp()
        self.repo = self.root / "synthetic repo"
        (self.repo / ".claude/memory").mkdir(parents=True)
        write(self.repo / ".claude/lintel-layout.yaml", "layout_version: 5\n")
        self.env.update(LINTEL_REPO_ROOT=self.repo.as_posix(),
                        LINTEL_AUDIT_DIR=(self.root / "audit").as_posix(),
                        LINTEL_SESSION_ID="synthetic-freeze")

    def shell(self, script):
        return self.bash("set -euo pipefail\n" + script, cwd=self.repo, expect=0).stdout

    def test_freeze_records_are_advisory_and_legacy_hook_only_warns(self):
        target = write(self.repo / "src/frozen/file.txt", "fixture baseline\n")
        freeze = "advisory: true\nfrozen:\n  - path: src/frozen/\n    reason: synthetic scope\n"
        write(self.repo / ".claude/runtime/state/code-freeze/synthetic-freeze.yaml", freeze)
        hook = 'bash "$LINTEL_SOURCE_ROOT/hooks/shared/frozen-zone-warn/run.sh" src/frozen/file.txt'
        self.assertEqual(self.shell(hook), "", "canonical metadata must not be advertised as a wired hook")
        write(self.home / ".lintel/freeze/synthetic-freeze.yaml", freeze)
        warned = self.shell(hook)
        self.assertIn("warn-only", warned)
        self.assertIn("/li:code-unfreeze", warned)
        self.assertNotIn("Use /unfreeze", warned)
        record = json.loads((self.root / "audit/hooks.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(record["kind"], "frozen_zone_warn")
        self.assertEqual(record["hook"], "frozen-zone-warn")
        self.assertEqual(record["tier"], "warn")
        self.assertEqual(self.shell(
            'source "$LINTEL_SOURCE_ROOT/bin/_audit.sh"\naudit_count hooks frozen_zone_warn'), "1\n")
        self.assertEqual(target.read_text(encoding="utf-8"), "fixture baseline\n")
        # No filesystem lock was installed; an explicit fixture write remains possible.
        write(target, "explicit fixture write\n")
        self.assertEqual(target.read_text(encoding="utf-8"), "explicit fixture write\n")
        body = (ROOT / "skills/code-freeze/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("advisory", body)
        self.assertIn("no universal automatic freeze consumer", body)
        self.assertNotIn("--ignore-freeze", body.split("## Failure modes", 1)[1])
        self.assertNotIn("shows currently frozen paths", body)
        hook_doc = (ROOT / "hooks/shared/frozen-zone-warn/HOOK.md").read_text(encoding="utf-8")
        self.assertNotIn("--ignore-freeze", hook_doc)
        self.assertIn("$LINTEL_HOME/freeze/", hook_doc)

    def test_existing_lesson_ids_and_superseded_history_remain_retrievable(self):
        lessons = write(self.repo / ".claude/memory/lessons.md",
                        "# Lessons\n\n## L-001 - Earlier test rule\n"
                        "superseded_by: L-002 (2026-09-20)\nTests were optional.\n\n"
                        "## L-002 - Keep actual test evidence\n"
                        "Rule: retain verified test output and provenance.\n")
        before = lessons.read_bytes()
        out = self.shell('source "$LINTEL_SOURCE_ROOT/lib/memory.sh"\nlessons_surface test\nlessons_count')
        self.assertIn("L-002", out)
        self.assertNotIn("L-001", out)
        self.assertTrue(out.endswith("1\n"))
        self.assertEqual(lessons.read_bytes(), before)


class EventReaderTests(Sandbox):
    def log(self, case, text, name="hooks.jsonl"):
        path = self.root / "events" / case / name
        if text is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode("utf-8"))
        return path

    def test_every_exit_precedence_row(self):
        valid = event()
        since = ("--since", "2026-01-01T00:00:00Z")
        rows = [
            ("absent", None, (), 3, "unobserved", {}),
            ("empty", "", (), 3, "unobserved", {"lines": 0}),
            ("filtered", valid + "\n", ("--kind", "session_digest"), 3, "unobserved", {"valid": 1, "selected": 0}),
            ("only-malformed", "{not json\n", (), 4, "observed_with_diagnostics", {"malformed": 1, "valid": 0}),
            ("truncated", valid, (), 4, "observed_with_diagnostics", {"incomplete_tail": True, "valid": 0}),
            ("duplicate-kind", valid[:-1] + ',"kind":"session_digest"}\n', (), 4,
             "observed_with_diagnostics", {"duplicate_key": 1, "valid": 0}),
            ("non-string", event(tier=1) + "\n", (), 4, "observed_with_diagnostics", {"malformed": 1}),
            ("missing-envelope", json.dumps({"ts": "2026-09-20T10:00:00Z", "kind": "frozen_zone_warn"}) + "\n",
             (), 4, "observed_with_diagnostics", {"malformed": 1}),
            ("unknown-kind", event(kind="not_in_catalog") + "\n", (), 4, "observed_with_diagnostics",
             {"unknown_kind": 1}),
            ("undated-since", event(ts="") + "\n", since, 4, "observed_with_diagnostics",
             {"undated": 1, "selected": 0}),
            ("undated-no-filter", event(ts="") + "\n", (), 0, "observed", {"undated": 1, "selected": 1}),
            ("diagnostic-despite-filter", valid + "\n{broken\n", ("--kind", "session_digest"), 4,
             "observed_with_diagnostics", {"malformed": 1, "selected": 0}),
            ("valid", valid + "\n", since, 0, "observed", {"valid": 1, "selected": 1}),
        ]
        codes = {"only-malformed": "malformed_json", "truncated": "incomplete_tail",
                 "duplicate-kind": "duplicate_key", "non-string": "non_string_value",
                 "missing-envelope": "missing_envelope", "unknown-kind": "unknown_kind",
                 "undated-since": "undated", "diagnostic-despite-filter": "malformed_json"}
        for case, text, extra, code, status, counters in rows:
            with self.subTest(case=case):
                path = self.log(case, text)
                result, summary = self.summary(path, *extra, expect=code)
                self.assertEqual(summary["status"], status)
                self.assertEqual(summary["schema_version"], 1)
                self.assertEqual(summary["catalog_version"], 1)
                self.assertEqual(summary["source"]["state"], "absent" if text is None else "present")
                self.assertTrue(same_path(summary["source"]["path"], path))
                self.assertEqual(summary["evidence"], "observed_records_only")
                self.assertEqual(summary["verification"], "not_performed")
                self.assertEqual(summary["enforcement"], "not_established")
                for key, expected in counters.items():
                    self.assertEqual(summary["records"][key], expected, key)
                if case in codes:
                    self.assertEqual([d["code"] for d in summary["diagnostics"]], [codes[case]])
                else:
                    self.assertEqual(summary["diagnostics"], [])
                self.assert_no_verdict(summary)
                records, rows_out = self.records(path, *extra, expect=code)
                self.assert_no_verdict(rows_out)
                if case in codes:
                    self.assertEqual([row.get("diagnostic") for row in rows_out if "diagnostic" in row],
                                     [codes[case]])
                    self.assertFalse(any(row.get("kind") == "session_digest" for row in rows_out))

    def test_valid_record_is_classified_with_raw_and_normalized_fields(self):
        path = self.log("valid", event() + "\n" + event(ts="2026-09-21T10:00:00Z") + "\n")
        result, summary = self.summary(path, expect=0)
        kind = summary["by_kind"]["frozen_zone_warn"]
        self.assertEqual((kind["count"], kind["class"], kind["check"]), (2, "finding", "performed"))
        self.assertEqual((kind["first_ts"], kind["last_ts"]), ("2026-09-20T10:00:00Z", "2026-09-21T10:00:00Z"))
        result, rows = self.records(path, "--since", "2026-09-21T00:00:00Z", expect=0)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(sorted(row), ["category", "check", "class", "fields", "kind", "line",
                                       "normalized", "ts"])
        self.assertEqual((row["line"], row["category"], row["kind"]), (2, "hooks", "frozen_zone_warn"))
        self.assertEqual(row["fields"]["edit_target"], "src/app.py")
        self.assertNotIn("kind", row["fields"])
        self.assertEqual(row["normalized"], {"target_path": "src/app.py"})

    def test_unreadable_catalog_and_usage_failures_exit_two(self):
        directory = self.root / "events/directory.jsonl"
        directory.mkdir(parents=True)
        result, summary = self.summary(directory, expect=2)
        self.assertEqual(summary["status"], "error")
        self.assertEqual(summary["source"]["state"], "unreadable")
        self.assert_no_verdict(summary)
        self.events("summary", expect=2)
        self.events("summary", "--file", directory, "--since", "yesterday", expect=2)
        tree = self.root / "broken-tree"
        (tree / "bin").mkdir(parents=True)
        (tree / "lib").mkdir()
        shutil.copy(EVENTS, tree / "bin/li-events.py")
        shutil.copy(ROOT / "lib/native_paths.py", tree / "lib/native_paths.py")
        write(tree / "lib/event-catalog.json", "{")
        absent = self.root / "events/absent.jsonl"
        broken = self.run_cmd([PYTHON, tree / "bin/li-events.py", "summary", "--file", absent], expect=2)
        self.assertEqual(json.loads(broken.stdout)["status"], "error")

    def test_reader_only_reads_explicit_files_and_writes_no_bytecode(self):
        tree = self.root / "copied source"
        (tree / "bin").mkdir(parents=True)
        (tree / "lib").mkdir()
        shutil.copy(EVENTS, tree / "bin/li-events.py")
        for name in ("native_paths.py", "event-catalog.json"):
            shutil.copy(ROOT / "lib" / name, tree / "lib" / name)
        path = self.log("readonly", event() + "\n")
        env = dict(self.env)
        env.pop("PYTHONDONTWRITEBYTECODE")
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*"))
        for command in ("summary", "records"):
            self.run_cmd([PYTHON, tree / "bin/li-events.py", command, "--file", path], env=env, expect=0)
        after = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*"))
        self.assertEqual(before, after)
        self.assertEqual(list(tree.rglob("__pycache__")), [])


class RoutingTests(Sandbox):
    ROUTE = r'''
source "$LINTEL_SOURCE_ROOT/bin/_audit.sh"
p() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s\n' "$1"; fi; }
p "$(audit_file hooks)"
audit_read_files hooks | while IFS= read -r f; do p "$f"; done
'''

    def route(self, repo, env, prefix=""):
        out = self.bash(prefix + self.ROUTE, cwd=repo, env=env, expect=0).stdout.splitlines()
        return out[0], out[1:]

    def test_writer_path_equals_reader_path_in_every_scope(self):
        v5 = self.make_repo("v5 repo")
        legacy = self.make_repo("unmigrated repo", v5=False)
        copilot = self.make_repo("copilot repo", agents=True)
        explicit = self.root / "explicit audit"
        home_audit = self.home / ".lintel/audit"
        copilot_env = ('source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"\n'
                       'lintel_copilot_env "$LINTEL_REPO_ROOT" >/dev/null || exit 7\n')
        cases = {
            "explicit": (v5, {"LINTEL_AUDIT_DIR": explicit.as_posix()}, "", [explicit / "hooks.jsonl"]),
            "v5": (v5, {}, "", [v5 / ".claude/runtime/audit/hooks.jsonl", home_audit / "hooks.jsonl"]),
            "unmigrated": (legacy, {}, "", [home_audit / "hooks.jsonl"]),
            "copilot": (copilot, {}, copilot_env, [copilot / ".claude/runtime/audit/hooks.jsonl"]),
        }
        for name, (repo, extra, prefix, expected) in cases.items():
            with self.subTest(scope=name):
                env = {**self.env, "LINTEL_REPO_ROOT": repo.as_posix(), **extra}
                writer, readers = self.route(repo, env, prefix)
                self.assertTrue(same_path(writer, expected[0]), (writer, expected[0]))
                self.assertEqual(len(readers), len(expected), readers)
                for actual, wanted in zip(readers, expected):
                    self.assertTrue(same_path(actual, wanted), (actual, wanted))
                self.bash(prefix + 'source "$LINTEL_SOURCE_ROOT/bin/_audit.sh"\n'
                          'audit_log hooks memory_budget_warn hook=memory-budget-warn tier=warn',
                          cwd=repo, env=env, expect=0)
                result, summary = self.summary(expected[0], expect=0)
                self.assertEqual(summary["by_kind"]["memory_budget_warn"]["count"], 1)
                shutil.rmtree(expected[0].parent)

    def test_v5_reads_legacy_history_and_reports_an_unread_second_file(self):
        repo = self.make_repo("v5 repo")
        env = {**self.env, "LINTEL_REPO_ROOT": repo.as_posix()}
        legacy = write(self.home / ".lintel/audit/hooks.jsonl", event() + "\n")
        count = 'source "$LINTEL_SOURCE_ROOT/bin/_audit.sh"\naudit_count hooks frozen_zone_warn'
        only = self.bash(count, cwd=repo, env=env, expect=0)
        self.assertEqual(only.stdout, "1\n")
        write(repo / ".claude/runtime/audit/hooks.jsonl", event() + "\n" + event() + "\n")
        both = self.bash(count, cwd=repo, env=env, expect=0)
        self.assertEqual(both.stdout, "2\n")
        self.assertIn(legacy.as_posix(), both.stderr)
        self.assertIn("not read", both.stderr)

    def test_audit_count_reports_absence_and_undated_exclusions(self):
        repo = self.make_repo("v5 repo")
        env = {**self.env, "LINTEL_REPO_ROOT": repo.as_posix()}
        absent = self.bash('source "$LINTEL_SOURCE_ROOT/bin/_audit.sh"\naudit_count hooks', cwd=repo,
                           env=env, expect=3)
        self.assertEqual(absent.stdout, "")
        self.assertTrue(product_stderr(absent.stderr).startswith("unobserved:"), absent.stderr)
        self.assertIn("hooks.jsonl", absent.stderr)
        undated = json.dumps({"kind": "frozen_zone_warn", "operator": "fixture", "cycle_id": "unknown"},
                             separators=(",", ":"))
        write(repo / ".claude/runtime/audit/hooks.jsonl", event() + "\n" + undated + "\n")
        since = self.bash('source "$LINTEL_SOURCE_ROOT/bin/_audit.sh"\n'
                          'audit_count hooks frozen_zone_warn 2026-01-01T00:00:00Z', cwd=repo, env=env, expect=0)
        self.assertEqual(since.stdout, "1\n")
        self.assertIn("without ts", since.stderr)

    def test_read_only_consumers_create_nothing_on_a_fresh_home(self):
        repo = self.make_repo("v5 repo")
        fresh = self.root / "fresh home"
        env = {**self.env, "HOME": fresh.as_posix(), "USERPROFILE": str(fresh),
               "LINTEL_HOME": (fresh / ".lintel").as_posix(), "LINTEL_REPO_ROOT": repo.as_posix()}
        env.pop("PYTHONDONTWRITEBYTECODE")
        script = r'''
source "$LINTEL_SOURCE_ROOT/bin/_audit.sh"
audit_dir hooks >/dev/null; audit_file hooks >/dev/null; audit_read_files hooks >/dev/null
rc=0; audit_count hooks 2>/dev/null || rc=$?; [ "$rc" = 3 ] || exit 11
rc=0; python3 "$LINTEL_SOURCE_ROOT/bin/li-events.py" summary --file "$(audit_file hooks)" >/dev/null || rc=$?
[ "$rc" = 3 ] || exit 12
source "$LINTEL_SOURCE_ROOT/lib/memory.sh"; lessons_count >/dev/null 2>&1
export LINTEL_JOBS_NO_INIT=1; source "$LINTEL_SOURCE_ROOT/bin/_jobs.sh"; list_jobs --read-only >/dev/null
'''
        self.bash(script, cwd=repo, env=env, expect=0)
        self.assertFalse(fresh.exists())
        self.assertFalse((repo / ".claude/runtime").exists())


class ProducerRoundTripTests(Sandbox):
    def setUp(self):
        super().setUp()
        self.repo = self.make_repo("producer repo")
        self.audit = self.root / "audit"
        self.env.update(LINTEL_REPO_ROOT=self.repo.as_posix(), LINTEL_AUDIT_DIR=self.audit.as_posix(),
                        LINTEL_PACKS_DIR=(self.root / "packs").as_posix())
        (self.root / "packs").mkdir()

    def hook(self, name, *arguments, stdin="", expect=None, source=ROOT):
        return self.run_cmd([BASH, source / "hooks/shared" / name / "run.sh", *arguments], cwd=self.repo,
                            stdin=stdin, expect=expect)

    def read(self, category="hooks"):
        result, rows = self.records(self.audit / f"{category}.jsonl", expect=0)
        self.assert_no_verdict(rows)
        return rows

    def test_secret_scan_block_finding_override_and_unavailable_scanner(self):
        write(self.repo / "leak.txt", "key = ghp_" + "a" * 36 + "\n")
        self.git(self.repo, "add", "leak.txt")
        payload = lambda command: json.dumps({"tool_input": {"command": command}})
        self.hook("secret-scan-block", stdin=payload("git commit -m x"), expect=2)
        self.hook("secret-scan-block", stdin=payload("LINTEL_OVERRIDE_SECRET=1 git commit -m x"), expect=0)
        tree = self.root / "stub tree"
        for relative in ("hooks/shared/secret-scan-block/run.sh", "hooks/shared/_input.sh",
                         "bin/_audit.sh", "lib/paths.sh"):
            (tree / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / relative, tree / relative)
        write(tree / "hooks/shared/_patterns.sh", "# stub: defines no scan_secrets\n:\n")
        self.hook("secret-scan-block", stdin=payload("git commit -m x"), expect=2, source=tree)
        finding, override, unavailable = self.read()
        self.assertEqual({finding["kind"], override["kind"], unavailable["kind"]}, {"secret_scan_block"})
        self.assertEqual((finding["class"], finding["check"]), ("block_decision", "performed"))
        self.assertEqual((finding["fields"]["blocked"], finding["fields"]["tier"]), ("true", "BLOCK"))
        self.assertEqual(finding["normalized"]["patterns"], "github-token")
        self.assertEqual((override["class"], override["check"]), ("override", "not_performed"))
        self.assertEqual(override["fields"]["override"], "true")
        self.assertEqual((unavailable["class"], unavailable["check"]), ("block_decision", "not_performed"))
        self.assertEqual(unavailable["fields"]["reason"], "scanner-unavailable")

    def test_frozen_zone_and_session_digest_records(self):
        self.env["LINTEL_SESSION_ID"] = "producer-freeze"
        write(self.home / ".lintel/freeze/producer-freeze.yaml", "frozen:\n  - path: src/\n")
        write(self.repo / "src/app.py", "print('fixture')\n")
        self.hook("frozen-zone-warn", "src/app.py", expect=0)
        self.hook("session-digest", expect=0)
        frozen, digest = self.read()
        self.assertEqual((frozen["kind"], frozen["class"], frozen["check"]),
                         ("frozen_zone_warn", "finding", "performed"))
        self.assertEqual(frozen["normalized"]["target_path"], "src/app.py")
        self.assertEqual((digest["kind"], digest["class"], digest["check"]),
                         ("session_digest", "observation", "performed"))
        self.assertEqual(digest["fields"]["hook"], "session-digest")

    def test_job_begin_end_and_stale_hooks(self):
        skill = write(self.root / "skill/SKILL.md", "---\nname: fixture-flow\nworkflow_root: true\n---\n")
        begun = self.hook("job-begin", skill.as_posix(), "internal-tool", expect=0)
        job_id = re.search(r"Job started: (\S+)", begun.stdout).group(1)
        stale_id = self.bash('source "$LINTEL_SOURCE_ROOT/bin/_jobs.sh"\njob_create stale-flow internal-tool',
                             cwd=self.repo, expect=0).stdout.strip()
        job_yaml = self.repo / ".claude/runtime/jobs" / stale_id / "job.yaml"
        aged = re.sub(r"^last_touched: .*$", "last_touched: 2000-01-01T00:00:00Z",
                      job_yaml.read_text(encoding="utf-8"), flags=re.M)
        write(job_yaml, aged)
        self.assertIn(stale_id, self.hook("job-stale-warn", expect=0).stdout)
        self.hook("job-end", job_id, "DONE", expect=0)
        rows = self.read("jobs")
        begin = next(r for r in rows if r["kind"] == "job_begin" and r["fields"]["job_id"] == job_id)
        self.assertEqual((begin["fields"]["workflow"], begin["class"], begin["check"]),
                         ("fixture-flow", "observation", "performed"))
        stale = next(r for r in rows if r["kind"] == "job_stale_warn")
        self.assertEqual((stale["fields"]["job_id"], stale["class"]), (stale_id, "finding"))
        end = next(r for r in rows if r["kind"] == "job_end")
        self.assertEqual((end["fields"]["job_id"], end["fields"]["result"], end["class"]),
                         (job_id, "DONE", "observation"))

    def test_brief_forge_blocked_record(self):
        self.bash('source "$LINTEL_SOURCE_ROOT/lib/brief-forge.sh" || exit 9\n'
                  'validate_brief_forge_evaluators not_loaded', cwd=self.repo, expect=1)
        blocked = self.read("brief-forge")[-1]
        self.assertEqual(blocked["kind"], "brief_forge_blocked")
        self.assertEqual((blocked["fields"]["reason"], blocked["fields"]["evaluator"]),
                         ("unknown_evaluator", "not_loaded"))
        self.assertTrue(blocked["fields"]["audit_receipt"])
        self.assertEqual((blocked["class"], blocked["check"]), ("receipt", "not_performed"))

    def test_alias_producers_normalize_target_and_patterns(self):
        write(self.repo / "infra/main.tf", 'sku = "Standard_D8s_v3"\n')
        self.hook("dh-cost-budget-warn", "infra/main.tf", expect=0)
        write(self.home / ".lintel/brand/design-patterns/demo/pattern.json", "{}\n")
        write(self.repo / "src/app.css", "body {}\n")
        self.env["LINTEL_SESSION_ID"] = "alias-fixture"
        self.hook("frontend-design-surface", "src/app.css", expect=0)
        artifact = self.repo / "shots/run one"
        write(artifact / "dom.html", "<p>ops@example.com</p>\n")
        self.hook("no-customer-data-in-screenshot", artifact.as_posix(), expect=0)
        rows = {row["kind"]: row for row in self.read()}
        cost = rows["dh_cost_budget_warn"]
        self.assertEqual(cost["normalized"], {"target_path": "infra/main.tf", "patterns": "sku-large"})
        surface = rows["frontend_design_surface"]
        self.assertTrue(surface["normalized"]["target_path"].endswith("src/app.css"))
        self.assertEqual(surface["normalized"]["target_path"], surface["fields"]["file"])
        self.assertEqual(surface["normalized"]["patterns"], "demo")
        shot = rows["no_customer_data_in_screenshot"]
        self.assertEqual(shot["normalized"], {"target_path": artifact.as_posix(), "patterns": "email"})
        for row in rows.values():
            self.assertEqual((row["class"], row["check"]), ("finding", "performed"))


class ReviewRoundTripTests(Sandbox):
    def test_review_log_is_read_by_review_read_and_only_counted_by_events(self):
        repo = self.make_repo("review repo")
        env = {**self.env, "LINTEL_REPO_ROOT": repo.as_posix()}
        head = self.git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
        payload = json.dumps({"skill": "plan-eng-review", "status": "CLEAR", "commit": head})
        self.run_cmd([BASH, ROOT / "bin/li-review-log", payload], cwd=repo, env=env, expect=0)
        raw = self.run_cmd([BASH, ROOT / "bin/li-review-read", "--json"], cwd=repo, env=env, expect=0)
        self.assertIn('"kind":"plan-eng-review"', raw.stdout)
        gate = self.run_cmd([BASH, ROOT / "bin/li-review-read"], cwd=repo, env=env, expect=3)
        self.assertIn(f"current_head: {head}", gate.stdout)
        log = repo / ".claude/runtime/audit/reviews.jsonl"
        result, summary = self.summary(log, expect=0)
        self.assertEqual((summary["records"]["lines"], summary["records"]["valid"]), (1, 1))
        counted = summary["by_kind"]["plan-eng-review"]
        self.assertEqual((counted["count"], counted["class"], counted["check"]), (1, None, None))
        self.assertEqual(counted["delegated"], "li-review-read")
        result, rows = self.records(log, expect=0)
        self.assertIsNone(rows[0]["fields"])
        self.assertNotIn("CLEAR", result.stdout)


class ReviewLegacyImportTests(Sandbox):
    """The one-time GSTACK_HOME import creates the marker directory only when it writes the marker."""

    def setUp(self):
        super().setUp()
        self.repo = self.make_repo("legacy repo")
        self.audit = self.repo / ".claude/runtime/audit"
        self.marker = self.audit / "reviews-legacy-import.done"
        self.gstack = self.root / "gstack"
        self.legacy = f"{self.gstack.as_posix()}/projects/legacyrepo/main-reviews.jsonl"
        self.env.update(LINTEL_REPO_ROOT=self.repo.as_posix())

    def read(self, *extra, env, expect):
        return self.run_cmd([BASH, ROOT / "bin/li-review-read", *extra], cwd=self.repo, env=env, expect=expect)

    def import_env(self):
        write(Path(self.legacy), "")
        return {**self.env, "GSTACK_HOME": self.gstack.as_posix()}

    def marker_lines(self):
        return self.marker.read_text(encoding="utf-8").splitlines()

    def test_empty_legacy_import_writes_its_marker_without_an_audit_directory(self):
        env = self.import_env()
        self.assertFalse(self.audit.exists())
        self.read("--json", env=env, expect=0)
        self.assertEqual(self.marker_lines(), [self.legacy])
        self.assertEqual([path.name for path in self.audit.iterdir()], [self.marker.name])

    def test_reads_without_a_legacy_import_create_no_audit_directory(self):
        for label, env in (("no GSTACK_HOME", self.env),
                           ("GSTACK_HOME without a legacy file", {**self.env, "GSTACK_HOME": self.gstack.as_posix()})):
            with self.subTest(label):
                self.read("--json", env=env, expect=0)
                self.read(env=env, expect=3)
                self.assertFalse(self.audit.exists())

    def test_a_second_import_run_does_not_duplicate_the_marker(self):
        env = self.import_env()
        for label, existing in (("audit directory already present", True), ("no audit directory", False)):
            with self.subTest(label):
                shutil.rmtree(self.audit, ignore_errors=True)
                if existing:
                    self.audit.mkdir(parents=True)
                for _ in range(2):
                    self.read("--json", env=env, expect=0)
                    self.assertEqual(self.marker_lines(), [self.legacy])


class FailurePropagationTests(Sandbox):
    STATE = ("---\nphase: CYCLE\nentry_format: 1\nstatus: STARTING\ncycle_id: c1\ncycle_mode: full\n"
             "entry_complete: true\n---\nphase: BUILD\nentry_format: 1\nstatus: STARTING\ncycle_id: c1\n"
             "next_recommended: REVIEW\nentry_complete: true\n")

    def setUp(self):
        super().setUp()
        self.env["LINTEL_PACKS_DIR"] = (self.root / "packs").as_posix()
        (self.root / "packs").mkdir()
        self.content = write(self.root / "brief.json", json.dumps({
            "task": "Verify a synthetic package", "constraints": ["No external effects"],
            "acceptance": ["A focused fixture passes"]}))

    def forge(self, repo, env, decision="forge_handoff subagent_spawn swarm FixtureWorker brief \"$BRIEF\""):
        return self.bash('source "$LINTEL_SOURCE_ROOT/lib/brief-forge.sh" || exit 9\n' + decision,
                         cwd=repo, env={**env, "BRIEF": self.content.as_posix()})

    def advisory_and_mandatory(self, repo, env):
        head = self.git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
        write(repo / "src/app.py", "print('fixture')\n")
        write(self.home / ".lintel/freeze/matrix.yaml", "frozen:\n  - path: src/\n")
        env = {**env, "LINTEL_SESSION_ID": "matrix"}
        return {
            "advisory": self.run_cmd([BASH, ROOT / "hooks/shared/frozen-zone-warn/run.sh", "src/app.py"],
                                     cwd=repo, env=env),
            "state_append": self.bash('source "$LINTEL_SOURCE_ROOT/lib/state.sh"\nstate_append SENSE DONE',
                                      cwd=repo, env=env),
            "lesson_add": self.lessons("add", "--title", "Matrix rule", "--body", "matrix.", cwd=repo, env=env),
            "job_create": self.bash('source "$LINTEL_SOURCE_ROOT/bin/_jobs.sh"\njob_create matrix internal-tool',
                                    cwd=repo, env=env),
            "review_log": self.run_cmd([BASH, ROOT / "bin/li-review-log", json.dumps(
                {"skill": "plan-eng-review", "status": "CLEAR", "commit": head})], cwd=repo, env=env),
            "brief_forge": self.forge(repo, env, "write_bypass_audit subagent_spawn swarm worker eligible"),
            "replay": self.run_cmd([BASH, ROOT / "bin/li-envelope-replay", self.envelope, "--apply", "--force"],
                                   cwd=repo, env=env),
        }

    def quiet_hooks(self, repo, env):
        write(repo / ".claude/runtime/state/00-state.md", self.STATE)
        return {
            "session-digest": self.run_cmd([BASH, ROOT / "hooks/shared/session-digest/run.sh"], cwd=repo, env=env),
            "cycle-incomplete-warn": self.run_cmd([BASH, ROOT / "hooks/shared/cycle-incomplete-warn/run.sh"],
                                                  cwd=repo, env=env),
            "cycle-position-inject": self.run_cmd([BASH, ROOT / "hooks/shared/cycle-position-inject/run.sh"],
                                                  cwd=repo, env=env, stdin='{"prompt":"continue"}'),
        }

    def test_unwritable_resolved_audit_directory(self):
        control_repo = self.make_repo("control repo")
        control_env = {**self.env, "LINTEL_REPO_ROOT": control_repo.as_posix(),
                       "LINTEL_AUDIT_DIR": (self.root / "control audit").as_posix()}
        forged = self.forge(control_repo, control_env)
        self.assertEqual(forged.returncode, 0, forged.stderr)
        self.envelope = write(self.root / "envelope.json", forged.stdout)
        control = self.advisory_and_mandatory(control_repo, control_env)
        for name, result in control.items():
            self.assertEqual(result.returncode, 0, f"control {name}: {result.stdout}{result.stderr}")
        explicit_repo = self.make_repo("explicit repo")
        explicit_file = write(self.root / "audit as file", "keep\n")
        v5_repo = self.make_repo("v5 repo")
        write(v5_repo / ".claude/runtime/audit", "keep\n")
        variants = {
            "explicit": (explicit_repo, {"LINTEL_AUDIT_DIR": explicit_file.as_posix()}),
            "v5": (v5_repo, {}),
        }
        for name, (repo, extra) in variants.items():
            with self.subTest(variant=name):
                env = {**self.env, "LINTEL_REPO_ROOT": repo.as_posix(), **extra}
                results = self.advisory_and_mandatory(repo, env)
                for producer in ("advisory", "state_append", "lesson_add", "job_create"):
                    self.assertEqual(results[producer].returncode, 0,
                                     f"{producer}: {results[producer].stdout}{results[producer].stderr}")
                self.assertIn("WARN [lintel/audit]: failed to write", results["advisory"].stderr)
                for producer in ("review_log", "brief_forge", "replay"):
                    self.assertNotEqual(results[producer].returncode, 0, producer)
                for hook, result in self.quiet_hooks(repo, env).items():
                    self.assertEqual((result.returncode, product_stderr(result.stderr)), (0, ""), hook)
                self.assertTrue((self.home / ".lintel/audit").is_dir())

    def test_unwritable_writer_store_fails_without_success_line(self):
        state_repo = self.make_repo("state repo")
        write(state_repo / ".claude/runtime/state", "keep\n")
        env = {**self.env, "LINTEL_REPO_ROOT": state_repo.as_posix()}
        state = self.bash('source "$LINTEL_SOURCE_ROOT/lib/state.sh"\nstate_append SENSE DONE && echo recorded',
                          cwd=state_repo, env=env)
        self.assertNotEqual(state.returncode, 0)
        self.assertNotIn("recorded", state.stdout)
        lesson_repo = self.make_repo("lesson repo")
        write(lesson_repo / ".claude/memory", "keep\n")
        env = {**self.env, "LINTEL_REPO_ROOT": lesson_repo.as_posix()}
        lesson = self.lessons("add", "--title", "Blocked", "--body", "blocked.", cwd=lesson_repo, env=env)
        self.assertNotEqual(lesson.returncode, 0)
        self.assertEqual(lesson.stdout, "")
        jobs_repo = self.make_repo("jobs repo")
        env = {**self.env, "LINTEL_REPO_ROOT": jobs_repo.as_posix(),
               "LINTEL_JOBS_DIR": write(self.root / "jobs as file", "keep\n").as_posix()}
        job = self.bash('source "$LINTEL_SOURCE_ROOT/bin/_jobs.sh"\njob_create blocked internal-tool',
                        cwd=jobs_repo, env=env)
        self.assertNotEqual(job.returncode, 0)
        self.assertEqual(job.stdout, "")
        self.assertIn("job record", job.stderr)
        skill = write(self.root / "skill/SKILL.md", "---\nname: blocked-flow\nworkflow_root: true\n---\n")
        begun = self.run_cmd([BASH, ROOT / "hooks/shared/job-begin/run.sh", skill.as_posix(), "internal-tool"],
                             cwd=jobs_repo, env=env)
        self.assertNotIn("Job started:", begun.stdout)


class LedgerDiagnosisTests(Sandbox):
    CYCLE = ("---\nphase: CYCLE\nentry_format: 1\nstatus: STARTING\ncycle_id: c1\ncycle_mode: full\n"
             "entry_complete: true\n")

    def setUp(self):
        super().setUp()
        self.repo = self.make_repo("ledger repo")
        self.env["LINTEL_REPO_ROOT"] = self.repo.as_posix()
        self.ledger = self.repo / ".claude/runtime/state/00-state.md"

    def state(self, script):
        return self.bash('source "$LINTEL_SOURCE_ROOT/lib/state.sh"\n' + script, cwd=self.repo, expect=0).stdout

    def test_truncated_unknown_format_and_legacy_blocks_are_diagnosed(self):
        write(self.ledger, "---\nphase: BUILD\nentry_format: 1\nts: 2026-09-20T10:00:00Z\nstatus: DONE\n")
        self.assertIn("state_diagnostic: incomplete entry", self.state("state_cycle_segment"))
        self.assertEqual(self.state('state_phase_record BUILD | state_field status').strip(), "INCOMPLETE")
        write(self.ledger, "---\nphase: BUILD\nentry_format: 2\nts: 2026-09-20T10:00:00Z\nstatus: DONE\n"
                           "entry_complete: true\n")
        segment = self.state("state_cycle_segment")
        self.assertIn("state_diagnostic: unsupported entry format", segment)
        self.assertEqual(self.state('state_phase_record BUILD | state_field status').strip(), "UNTRUSTED")
        self.assertNotIn("BUILD", self.state("state_cycle_segment | state_completed_phases"))
        self.assertEqual(self.state("state_resume_phase").strip(), "BUILD")
        write(self.ledger, "---\nphase: SENSE\nstatus: DONE\n")
        self.assertIn("completeness: unknown (legacy entry)", self.state("state_cycle_segment"))
        self.assertEqual(self.state('state_phase_record SENSE | state_field status').strip(), "DONE")

    def test_digest_and_footer_never_show_an_open_phase_as_completed(self):
        cases = {
            "STARTING": ("status: STARTING\nnext_recommended: REVIEW\nentry_complete: true\n", "in progress"),
            "BLOCKED": ("status: BLOCKED\nnext_recommended: REVIEW\nentry_complete: true\n", "blocked"),
            "INCOMPLETE": ("status: DONE\nnext_recommended: REVIEW\n", "incomplete"),
        }
        for status, (tail, label) in cases.items():
            with self.subTest(status=status):
                write(self.ledger, self.CYCLE + "---\nphase: BUILD\nentry_format: 1\ncycle_id: c1\n" + tail)
                footer = self.bash('source "$LINTEL_SOURCE_ROOT/lib/cycle-footer.sh"\nrender_cycle_footer --compact',
                                   cwd=self.repo, expect=0).stdout
                digest = self.run_cmd([BASH, ROOT / "hooks/shared/session-digest/run.sh"], cwd=self.repo, expect=0)
                context = json.loads(digest.stdout)["hookSpecificOutput"]["additionalContext"]
                line = next(l for l in context.splitlines() if l.startswith("Current cycle:"))
                for text in (footer, line):
                    self.assertIn("BUILD", text)
                    self.assertIn(label, text)
                    self.assertNotIn("`BUILD` done", text)
                    self.assertNotIn("cycle complete", text)


class LessonTests(Sandbox):
    def setUp(self):
        super().setUp()
        self.repo = self.make_repo("lesson repo")
        self.store = self.repo / ".claude/memory/lessons.md"
        self.audit = self.root / "audit"
        self.env.update(LINTEL_REPO_ROOT=self.repo.as_posix(), LINTEL_AUDIT_DIR=self.audit.as_posix())

    def memory(self, script, **kwargs):
        return self.bash('source "$LINTEL_SOURCE_ROOT/lib/memory.sh"\n' + script, cwd=self.repo, **kwargs)

    def install(self, name, newline=b"\n"):
        self.store.parent.mkdir(parents=True, exist_ok=True)
        self.store.write_bytes(fixture_bytes(name, newline))
        return self.store

    def diagnostics(self, text):
        return sorted((int(line), code) for line, code in LESSON_DIAGNOSTIC.findall(text))

    def audit_rows(self):
        result, rows = self.records(self.audit / "lessons.jsonl", expect=0)
        return rows

    def test_shared_fixtures_through_both_entry_points(self):
        for name, expected in EXPECTED["fixtures"].items():
            lines = fixture_lines(name)
            for newline in (b"\n", b"\r\n"):
                with self.subTest(fixture=name, crlf=newline == b"\r\n"):
                    self.install(name, newline)
                    wanted_diagnostics = sorted(tuple(item) for item in expected["diagnostics"])
                    count = self.memory("lessons_count", expect=0)
                    self.assertEqual(count.stdout.strip(), str(expected["count"]))
                    self.assertEqual(self.diagnostics(count.stderr), wanted_diagnostics)
                    index = self.memory("lessons_index", expect=0).stdout.splitlines()
                    self.assertEqual([(re.match(r"L-\d+", row).group(0),
                                       "superseded" if row.endswith("(superseded)") else "active")
                                      for row in index],
                                     [(lesson["id"], lesson["state"]) for lesson in expected["lessons"]])
                    recent = self.memory("lessons_recent", expect=0).stdout.splitlines()
                    self.assertEqual(recent, [lines[line - 1][3:] for _, line in expected["recent"]])
                    for keywords, hits in expected["surface"].items():
                        out = self.memory("lessons_surface " + keywords, expect=0).stdout.splitlines()
                        found = sorted((re.match(r"L-\d+", row).group(0),
                                        int(re.search(r"\[matched (\d+)\]$", row).group(1))) for row in out)
                        self.assertEqual(found, sorted(tuple(hit) for hit in hits), keywords)
                    inspected = self.lessons("inspect", "--store", self.store, expect=0)
                    self.assertEqual(self.diagnostics(inspected.stderr), wanted_diagnostics)
                    report = json.loads(inspected.stdout)
                    self.assertEqual(report["next_id"], expected["next_id"])
                    self.assertEqual(sorted((d["line"], d["code"]) for d in report["diagnostics"]),
                                     wanted_diagnostics)
                    for actual, lesson in zip(report["lessons"], expected["lessons"]):
                        self.assertEqual((actual["id"], actual["line"], actual["end_line"], actual["state"]),
                                         (lesson["id"], lesson["line"], lesson["end"], lesson["state"]))
                        self.assertEqual(actual["superseded_by"], lesson.get("superseded_by"))
                        self.assertEqual(actual["supersedes"], lesson.get("supersedes", []))
                    self.assertEqual(len(report["lessons"]), len(expected["lessons"]))
                    next_id = self.lessons("next-id", "--store", self.store, expect=0)
                    self.assertEqual(next_id.stdout.strip(), expected["next_id"])
                    for lesson_id, outcome in expected["get"].items():
                        got = self.lessons("get", "--id", lesson_id, "--store", self.store,
                                           expect=outcome["exit"], binary=True)
                        if outcome["exit"] == 0:
                            start, end = outcome["lines"]
                            block = newline.join(line.encode("utf-8") for line in lines[start - 1:end]) + newline
                            self.assertEqual(got.stdout, block, lesson_id)
                        else:
                            self.assertEqual(got.stdout, b"", lesson_id)

    def test_add_allocates_maximum_plus_one_and_appends(self):
        store = self.install("grammar.md")
        before = store.read_bytes()
        added = self.lessons("add", "--title", "November rule", "--body", "**Rule:** november keyword.",
                             "--store", store, expect=0)
        self.assertEqual(added.stdout.strip(), "L-010")
        after = store.read_bytes()
        self.assertTrue(after.startswith(before))
        self.assertIn("## L-010 — November rule\n".encode("utf-8"), after[len(before):])
        self.lessons("get", "--id", "L-010", "--store", store, expect=0)
        alloc = self.install("allocation.md")
        self.assertEqual(self.lessons("add", "--title", "Next", "--body", "next.", "--store", alloc,
                                      expect=0).stdout.strip(), "L-004")
        rows = self.audit_rows()
        self.assertEqual([(r["kind"], r["fields"]["id"], r["fields"]["scope"], r["fields"]["classification"])
                          for r in rows], [("lesson_recorded", "L-010", "project", "add"),
                                           ("lesson_recorded", "L-004", "project", "add")])

    def test_update_keeps_the_id_and_supersede_stamps_both_blocks(self):
        store = self.install("grammar.md")
        original = fixture_lines("grammar.md")
        self.lessons("update", "--id", "L-003", "--body", "charlie keyword was sharpened.", "--store", store,
                     expect=0)
        updated = store.read_bytes().decode("utf-8").split("\n")
        self.assertEqual(updated[:16], original[:16])
        self.assertEqual(updated[15:18], [original[15], "charlie keyword was sharpened.", ""])
        self.assertEqual(updated[18:], original[18:])
        superseded = self.lessons("supersede", "--id", "L-005", "--title", "Oscar rule replaces foxtrot",
                                  "--body", "oscar keyword.", "--store", store, expect=0)
        self.assertEqual(superseded.stdout.strip(), "L-010")
        old = self.lessons("get", "--id", "L-005", "--store", store, expect=0).stdout.splitlines()
        self.assertRegex(old[1], r"^superseded_by: L-010 \(\d{4}-\d{2}-\d{2}\)$")
        new = self.lessons("get", "--id", "L-010", "--store", store, expect=0).stdout.splitlines()
        self.assertEqual(new[:2], ["## L-010 — Oscar rule replaces foxtrot", "supersedes: L-005"])
        report = json.loads(self.lessons("inspect", "--store", store, expect=0).stdout)
        states = {(item["id"], item["line"]): item["state"] for item in report["lessons"]}
        self.assertEqual(states[("L-005", 27)], "superseded")
        self.assertEqual(self.memory("lessons_count", expect=0).stdout.strip(), "7")
        self.assertEqual([(r["kind"], r["fields"]["id"], r["fields"]["classification"]) for r in self.audit_rows()],
                         [("lesson_updated", "L-003", "update"), ("lesson_superseded", "L-010", "supersede")])

    def test_writes_refuse_absent_duplicate_and_global_targets(self):
        store = self.install("grammar.md")
        before = store.read_bytes()
        self.lessons("update", "--id", "L-006", "--body", "x", "--store", store, expect=1)
        self.lessons("update", "--id", "L-008", "--body", "x", "--store", store, expect=2)
        self.lessons("supersede", "--id", "L-006", "--title", "x", "--body", "x", "--store", store, expect=1)
        self.lessons("supersede", "--id", "L-008", "--title", "x", "--body", "x", "--store", store, expect=2)
        refused = self.lessons("add", "--scope", "global", "--title", "x", "--body", "x", expect=2)
        self.assertIn("operator lessons sink not activated", refused.stderr)
        got = self.lessons("get", "--id", "global:L-001", expect=2)
        self.assertIn("not activated", got.stderr)
        self.assertEqual(store.read_bytes(), before)

    def test_held_lock_and_changed_store_refuse_without_replacing(self):
        store = self.install("grammar.md")
        before = store.read_bytes()
        lock = store.with_name(store.name + ".lock")
        lock.mkdir()
        held = self.lessons("add", "--title", "Locked", "--body", "x", "--store", store, expect=9)
        self.assertIn("locked", held.stderr)
        self.assertTrue(lock.is_dir(), "a held lock is never broken automatically")
        self.assertEqual(store.read_bytes(), before)
        lock.rmdir()
        helper = runpy.run_path(str(LESSONS))

        def racing(current):
            store.write_bytes(b"# concurrent writer\n")
            return (current or b"") + "\n## L-010 — Racing rule\nracing.\n".encode("utf-8")

        with mock.patch.dict(os.environ, self.env, clear=True), self.assertRaises(helper["LessonConflict"]):
            helper["write_store"](store, racing)
        self.assertEqual(store.read_bytes(), b"# concurrent writer\n")

    def test_missing_store_is_created_from_the_template_only_inside_a_repository(self):
        created = self.lessons("add", "--title", "First rule", "--body", "first.", cwd=self.repo, expect=0)
        self.assertEqual(created.stdout.strip(), "L-001")
        data = self.store.read_bytes()
        self.assertTrue(data.startswith(BASELINE.read_bytes().replace(b"\r\n", b"\n")))
        self.assertIn("## L-001 — First rule".encode("utf-8"), data)
        if not IS_WINDOWS:
            self.assertEqual(self.store.stat().st_mode & 0o777, 0o644)
        outside = self.root / "outside"
        outside.mkdir()
        env = dict(self.env)
        env.pop("LINTEL_REPO_ROOT")
        count = self.bash('source "$LINTEL_SOURCE_ROOT/lib/memory.sh"\nlessons_count', cwd=outside, env=env,
                          expect=0)
        self.assertEqual(count.stdout.strip(), "0")
        self.assertIn("no project lessons store (unobserved)", count.stderr)
        self.assertIn("no project lessons store (unobserved)",
                      self.lessons("get", "--id", "L-001", cwd=outside, env=env, expect=1).stderr)
        self.assertIn("no project lessons store",
                      self.lessons("add", "--title", "x", "--body", "y", cwd=outside, env=env, expect=3).stderr)
        self.assertEqual(list(outside.iterdir()), [])
        self.install("empty.md")
        empty = self.memory("lessons_count", expect=0)
        self.assertEqual(empty.stdout.strip(), "0")
        self.assertNotIn("unobserved", empty.stderr)

    def test_unmigrated_repository_names_the_read_and_ignored_stores(self):
        repo = self.make_repo("legacy repo", v5=False)
        (repo / "tasks").mkdir()
        (repo / "tasks/lessons.md").write_bytes(fixture_bytes("grammar.md"))
        (repo / ".claude/memory").mkdir(parents=True)
        (repo / ".claude/memory/lessons.md").write_bytes(fixture_bytes("allocation.md"))
        env = {**self.env, "LINTEL_REPO_ROOT": repo.as_posix()}
        count = self.bash('source "$LINTEL_SOURCE_ROOT/lib/memory.sh"\nlessons_count', cwd=repo, env=env, expect=0)
        self.assertEqual(count.stdout.strip(), "7")
        got = self.lessons("get", "--id", "L-004", cwd=repo, env=env, expect=0)
        for stderr in (count.stderr, got.stderr):
            self.assertIn("tasks/lessons.md", stderr)
            self.assertIn(".claude/memory/lessons.md", stderr)
            self.assertIn("ignored", stderr)

    def test_without_python_reads_work_and_writes_refuse_visibly(self):
        store = self.install("grammar.md")
        before = store.read_bytes()
        env = {**self.env, "PATH": os.pathsep.join(
            entry for entry in self.env["PATH"].split(os.pathsep) if entry and not has_python(entry))}
        env.pop("LINTEL_PYTHON", None)
        probe = self.run_cmd([BASH, "-c", "command -v python3 || command -v python || echo none"], cwd=self.repo,
                             env=env, expect=0)
        self.assertEqual(probe.stdout.strip(), "none")
        self.assertEqual(self.memory("lessons_count", env=env, expect=0).stdout.strip(), "7")
        refused = self.memory("lessons_helper add --title Blocked --body blocked", env=env, expect=2)
        self.assertIn("Python 3.9+ is required", refused.stderr)
        promote = self.run_cmd([BASH, PROMOTE, "--id", "L-001", "--source-label", "fixture-app"], cwd=self.repo,
                               env=env, expect=2)
        self.assertIn("Python 3.9+ is required", promote.stderr)
        self.assertEqual(store.read_bytes(), before)

    def test_global_scope_refuses_and_the_legacy_view_stays_read_only(self):
        legacy = write(self.home / ".lintel/lessons.jsonl", '{"date":"2026-01-01","body":"old operator note"}\n')
        before = legacy.read_bytes()
        view = self.memory("lessons_legacy_operator", expect=0)
        self.assertIn("legacy operator lessons, not ID-managed", view.stdout)
        self.assertIn("old operator note", view.stdout)
        refused = self.lessons("add", "--scope", "global", "--title", "x", "--body", "y", expect=2)
        self.assertIn("operator lessons sink not activated", refused.stderr)
        self.assertEqual(legacy.read_bytes(), before)


class PromotionTests(Sandbox):
    GENERALIZED = "## Keep verified test evidence\n\n**Rule:** retain the verified output of every check.\n"

    def setUp(self):
        super().setUp()
        self.source = self.make_repo("source app")
        write(self.source / ".claude/memory/lessons.md",
              "# Lessons\n\n## L-001 — Local rule\nlocal only.\n\n"
              "## L-002 — Keep test evidence\n**Rule:** retain verified output.\n")
        self.git(self.source, "add", "-A")
        self.git(self.source, "commit", "-q", "-m", "lessons")
        self.dest = self.make_repo("lintel dest", v5=False)
        self.relative = "scaffolding/01-foundation/.claude/memory/lessons.md"
        self.target = self.dest / self.relative
        self.target.parent.mkdir(parents=True)
        self.target.write_bytes(BASELINE.read_bytes().replace(b"\r\n", b"\n"))
        self.git(self.dest, "add", "-A")
        self.git(self.dest, "commit", "-q", "-m", "baseline")
        self.generalized = write(self.root / "generalized.md", self.GENERALIZED)
        self.env.update(LINTEL_REPO_ROOT=self.source.as_posix(), LINTEL_AUDIT_DIR=(self.root / "audit").as_posix())

    def promote(self, *extra, lintel_dir=None, label=True, generalized=None, expect=None, env=None):
        argv = [BASH, PROMOTE, "--id", "L-002", "--generalized-file", (generalized or self.generalized).as_posix()]
        if label:
            argv += ["--source-label", "fixture-app"]
        if lintel_dir is not False:
            argv += ["--lintel-dir", (lintel_dir or self.dest).as_posix()]
        return self.run_cmd(argv + list(extra), cwd=self.source, env=env, expect=expect)

    def snapshot(self, repo):
        read = lambda *a: self.git(repo, "--no-optional-locks", *a, expect=None).stdout
        return (read("rev-parse", "HEAD"), read("symbolic-ref", "-q", "HEAD"), read("for-each-ref", "refs/heads"),
                read("ls-files", "-s"), read("diff", "--cached", "--name-only"))

    def reset(self, repo):
        self.git(repo, "checkout", "-q", "-f", "main")
        self.git(repo, "reset", "-q", "--hard")
        self.git(repo, "clean", "-q", "-fdx")

    def test_help_and_usage_never_depend_on_the_current_directory(self):
        outside = self.root / "outside"
        outside.mkdir()
        env = dict(self.env)
        env.pop("LINTEL_REPO_ROOT")
        helped = self.run_cmd([BASH, PROMOTE, "--help"], cwd=outside, env=env, expect=0)
        self.assertIn("--lintel-dir", helped.stdout)
        self.run_cmd([BASH, PROMOTE, "--bogus"], cwd=outside, env=env, expect=2)

    def test_refusals_write_nothing(self):
        before = self.target.read_bytes()
        env = dict(self.env)
        env.pop("LINTEL_DIR", None)
        self.assertIn("--lintel-dir", self.promote(lintel_dir=False, env=env, expect=2).stderr)
        self.promote(label=False, expect=2)
        self.promote("--source-label", "bad label!", label=False, expect=2)
        zero = write(self.root / "zero.md", "No heading here.\n")
        two = write(self.root / "two.md", "## One\none\n\n## Two\ntwo\n")
        self.promote(generalized=zero, expect=2)
        self.promote(generalized=two, expect=2)
        outside = write(self.root / "outside/lessons.md", "# Lessons\n\n## L-002 — Loose\nloose.\n")
        self.promote("--source", outside.as_posix(), expect=3)
        self.promote("--source", (self.root / "missing.md").as_posix(), expect=3)
        (self.root / "not a repo").mkdir()
        self.promote(lintel_dir=self.root / "not a repo", expect=4)
        empty_dest = self.make_repo("empty dest", v5=False)
        self.promote(lintel_dir=empty_dest, expect=5)
        for bad in ("L-042", "bogus"):
            argv = [BASH, PROMOTE, "--id", bad, "--generalized-file", self.generalized.as_posix(),
                    "--source-label", "fixture-app", "--lintel-dir", self.dest.as_posix()]
            self.run_cmd(argv, cwd=self.source, expect=6)
        self.assertEqual(self.target.read_bytes(), before)
        self.assertNotIn(b"source app", self.target.read_bytes())

    def test_default_mode_writes_only_the_target_in_main_and_linked_worktrees(self):
        worktree = self.root / "lintel worktree"
        self.git(self.dest, "worktree", "add", "-q", "-b", "promo-wt", worktree.as_posix())
        for destination in (self.dest, worktree):
            with self.subTest(destination=destination.name):
                main_before, tree_before = self.snapshot(self.dest), self.snapshot(worktree)
                result = self.promote(lintel_dir=destination, expect=0)
                self.assertIn("+## L-001 — Keep verified test evidence", result.stdout)
                self.assertIn("operator-attested", result.stdout)
                self.assertEqual((self.snapshot(self.dest), self.snapshot(worktree)), (main_before, tree_before))
                status = self.git(destination, "--no-optional-locks", "status", "--porcelain").stdout
                self.assertEqual(status.splitlines(), [" M " + self.relative])
                target = destination / self.relative
                got = self.lessons("get", "--id", "L-001", "--store", target, expect=0).stdout
                self.assertIn("## L-001 — Keep verified test evidence", got)
                self.assertRegex(got, PROVENANCE)
                self.assertIn("source_commit=unrecorded", got)
                self.assertEqual(json.loads(self.lessons("inspect", "--store", target, expect=0).stdout)["diagnostics"],
                                 [])

    def test_recorded_source_commit_and_explicit_operator(self):
        head = self.git(self.source, "rev-parse", "HEAD").stdout.strip()
        self.promote("--record-source-commit", "--operator", "fixture-op", expect=0)
        got = self.lessons("get", "--id", "L-001", "--store", self.target, expect=0).stdout
        self.assertRegex(got, PROVENANCE)
        self.assertIn(f"source_commit={head}", got)
        self.assertIn("operator=fixture-op", got)

    def test_commit_preconditions_refuse_before_any_write(self):
        before = self.target.read_bytes()
        write(self.dest / "other.txt", "unrelated\n")
        self.git(self.dest, "add", "other.txt")
        snapshot = self.snapshot(self.dest)
        self.promote("--commit", "--expect-branch", "main", expect=8)
        self.assertEqual((self.snapshot(self.dest), self.target.read_bytes()), (snapshot, before))
        self.reset(self.dest)
        write(self.target, before.decode("utf-8") + "dirty\n")
        self.promote("--commit", "--expect-branch", "main", expect=8)
        self.assertEqual(self.target.read_bytes(), before + b"dirty\n")
        self.reset(self.dest)
        self.promote("--commit", "--expect-branch", "release", expect=8)
        self.git(self.dest, "checkout", "-q", "--detach")
        self.promote("--commit", "--expect-branch", "main", expect=8)
        self.assertEqual(self.target.read_bytes(), before)

    def test_valid_commit_changes_exactly_one_path_and_rerun_is_idempotent(self):
        old = self.git(self.dest, "rev-parse", "HEAD").stdout.strip()
        self.promote("--commit", "--expect-branch", "main", expect=0)
        new = self.git(self.dest, "rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(new, old)
        self.assertEqual(self.git(self.dest, "rev-parse", "HEAD^").stdout.strip(), old)
        changed = self.git(self.dest, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout
        self.assertEqual(changed.splitlines(), [self.relative])
        self.assertEqual(self.git(self.dest, "--no-optional-locks", "status", "--porcelain").stdout, "")
        snapshot = self.snapshot(self.dest)
        after = self.target.read_bytes()
        rerun = self.promote("--commit", "--expect-branch", "main", expect=7)
        self.assertIn("L-001", rerun.stdout + rerun.stderr)
        self.promote(expect=7)
        self.assertEqual((self.snapshot(self.dest), self.target.read_bytes()), (snapshot, after))

    def test_injected_commit_failure_hook_staging_and_write_conflicts(self):
        before = self.target.read_bytes()
        snapshot = self.snapshot(self.dest)
        hook = self.dest / ".git/hooks/pre-commit"
        write(hook, "#!/bin/sh\nexit 1\n")
        self.promote("--commit", "--expect-branch", "main", expect=10)
        self.assertEqual((self.target.read_bytes(), self.snapshot(self.dest)), (before, snapshot))
        write(hook, "#!/bin/sh\necho extra > extra.txt\ngit add extra.txt\n")
        old = self.git(self.dest, "rev-parse", "HEAD").stdout.strip()
        staged = self.promote("--commit", "--expect-branch", "main", expect=11)
        new = self.git(self.dest, "rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(new, old)
        self.assertIn(old, staged.stdout + staged.stderr)
        self.assertIn(new, staged.stdout + staged.stderr)
        self.assertEqual(sorted(self.git(self.dest, "diff-tree", "--no-commit-id", "--name-only", "-r",
                                         "HEAD").stdout.split()), sorted([self.relative, "extra.txt"]))
        hook.unlink()
        self.git(self.dest, "reset", "-q", "--hard", old)
        self.git(self.dest, "clean", "-q", "-fdx")
        lock = self.target.with_name(self.target.name + ".lock")
        lock.mkdir()
        self.promote(expect=9)
        lock.rmdir()
        self.assertEqual(self.target.read_bytes(), before)
        helper = runpy.run_path(str(LESSONS))
        namespace = helper["write_store"].__globals__
        original = namespace["write_store"]

        def racing(store, build, **options):
            def mutate(current):
                store.write_bytes(b"# concurrent destination writer\n")
                return build(current)
            return original(store, mutate, **options)

        argv = ["promote", "--id", "L-002", "--generalized-file", self.generalized.as_posix(),
                "--source-label", "fixture-app", "--lintel-dir", self.dest.as_posix(),
                "--source", (self.source / ".claude/memory/lessons.md").as_posix()]
        with mock.patch.dict(os.environ, self.env, clear=True), mock.patch.dict(namespace, write_store=racing):
            self.assertEqual(helper["main"](argv), 9)
        self.assertEqual(self.target.read_bytes(), b"# concurrent destination writer\n")


if __name__ == "__main__":
    unittest.main(argv=[__file__, *remaining])
