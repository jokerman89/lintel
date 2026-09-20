"""Private-sync acceptance against temporary homes and real local bare remotes."""
# component: private-sync-binding-tests
# implements: ADR-0010, ADR-0026
# intent: .claude/plans/universal-implementation/packages/P02.md
# constraints: local fixtures only; no network, credentials or personal configuration
# last_intent_review: 2026-09-20

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
BASH = os.environ.get("LINTEL_TEST_BASH", "bash")
ASSERTIONS = 0


def snapshot(root):
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }


class Fixture:
    def __init__(self, case, directory, kind):
        self.case = case
        self.base = directory
        self.kind = kind
        self.home = directory / "home"
        self.home.mkdir(parents=True)
        self.env = {
            key: value for key, value in os.environ.items()
            if not key.startswith(("GIT_", "LINTEL_"))
        }
        self.env.update(
            HOME=str(self.home),
            USERPROFILE=str(self.home),
            XDG_CONFIG_HOME=str(self.home / ".config"),
            LINTEL_HOME=str(self.home / ".lintel"),
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_TERMINAL_PROMPT="0",
            GIT_ALLOW_PROTOCOL="file",
            GIT_ATTR_NOSYSTEM="1",
            GIT_PAGER="cat",
        )
        self.cache = self.home / ".lintel" / (
            "roles/private" if kind == "roles" else "lessons"
        )
        self.binding = self.home / f".lintel-{kind}-remote.txt"
        self.project = directory / "source" / "project"
        self.make_project(self.project)
        self.trace = directory / "git-trace.log"

    def git(self, directory, *args, ok=True):
        result = subprocess.run(
            ["git", "-C", str(directory), *args],
            env=self.env, capture_output=True, text=True, encoding="utf-8",
        )
        if ok and result.returncode:
            raise AssertionError(f"git {args}: {result.stdout}{result.stderr}")
        return result.stdout.strip()

    def identity(self, directory):
        self.git(directory, "config", "--local", "user.name", "Private sync fixture")
        self.git(directory, "config", "--local", "user.email", "sync@example.invalid")
        self.git(directory, "config", "--local", "commit.gpgSign", "false")

    def make_project(self, directory, origin=None, legacy=False):
        directory.mkdir(parents=True)
        self.git(directory, "init", "-q", "-b", "main")
        self.identity(directory)
        if origin:
            self.git(directory, "remote", "add", "origin", str(origin))
        lessons = directory / ("tasks/lessons.md" if legacy else ".claude/memory/lessons.md")
        lessons.parent.mkdir(parents=True)
        lessons.write_bytes(b"# Source lessons are not overwritten by pull.\n")
        if not legacy:
            (directory / ".claude/lintel-layout.yaml").write_text(
                "layout_version: 5\n", encoding="utf-8"
            )
        return lessons

    def remote(self, name):
        path = self.base / f"{name}.git"
        path.mkdir()
        self.git(path, "init", "-q", "--bare", "-b", "main")
        return path

    def cli(self, command, *args, cwd=None, ok=True):
        result = subprocess.run(
            [BASH, str(ROOT / f"bin/li-{self.kind}-sync"), command, *map(str, args)],
            cwd=cwd or self.project, env=self.env,
            capture_output=True, text=True, encoding="utf-8",
        )
        if ok is not None:
            self.case.check(
                (result.returncode == 0) == ok,
                f"{self.kind} {command}: exit={result.returncode}\n"
                f"{result.stdout}{result.stderr}",
            )
        return result

    def setup(self, remote):
        self.cli("setup", remote)
        self.identity(self.cache)

    def content(self, text, project=None):
        path = (
            self.cache / "architect.md" if self.kind == "roles"
            else (project or self.project) / ".claude/memory/lessons.md"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text)
        return path

    def record(self, content):
        matches = [path for path in self.cache.glob("*.md") if path.read_bytes() == content]
        self.case.equal(len(matches), 1, "one record contains the selected content")
        return matches[0]

    def state(self):
        return (
            snapshot(self.cache),
            self.git(self.cache, "rev-parse", "--verify", "HEAD", ok=False),
            self.git(self.cache, "diff", "--cached", "--binary"),
            self.git(self.cache, "status", "--porcelain"),
        )

    def reject_without_transfer(self, command):
        before = self.state()
        self.trace.write_text("", encoding="utf-8")
        self.env["GIT_TRACE"] = str(self.trace)
        result = self.cli(command, ok=False)
        self.case.equal(self.state(), before, "rejection preserves files, HEAD and index")
        self.case.check(bool(result.stderr.strip()), "rejection supplies an error")
        trace = self.trace.read_text(encoding="utf-8")
        self.case.check(
            "git-upload-pack" not in trace and "git-receive-pack" not in trace,
            "rejection never starts a fetch/push transport",
        )


class PrivateSyncTests(unittest.TestCase):
    kind = "roles"

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lintel-private-sync-")
        self.base = Path(self.temporary.name).resolve()
        self.fixture = Fixture(self, self.base / "alice", self.kind)
        self.addCleanup(self.cleanup)

    def cleanup(self):
        # Only TemporaryDirectory's exact fixture is owned by this test.
        def writable_remove(function, path, _error):
            os.chmod(path, 0o700)
            function(path)
        shutil.rmtree(self.base, onerror=writable_remove)
        self.temporary.cleanup()

    def check(self, condition, message):
        global ASSERTIONS
        ASSERTIONS += 1
        self.assertTrue(condition, message)

    def equal(self, actual, expected, message):
        self.check(actual == expected, f"{message}: expected={expected!r}, actual={actual!r}")

    def test_a26_1_rebinds_actual_origin_and_retains_content(self):
        f = self.fixture
        a, b = f.remote("remote-a"), f.remote("remote-b")
        f.setup(a)
        f.content(b"# First private record.\n")
        f.cli("push")
        old_head = f.git(a, "rev-parse", "HEAD")
        before = f.state()
        f.cli("setup", b)
        self.equal(
            Path(f.git(f.cache, "remote", "get-url", "origin")).resolve(), b,
            "setup B changes the actual origin, not just displayed configuration",
        )
        binding = json.loads(f.binding.read_text(encoding="utf-8"))
        self.equal(binding["enabled"], True, "binding is explicitly enabled")
        self.equal(Path(binding["url"]).resolve(), b, "binding names selected destination")
        self.equal(f.state(), before, "destination change retains files, index and history")
        f.cli("setup", b)
        self.equal(f.state(), before, "repeated setup is idempotent")
        f.content(b"# Changed after choosing B.\n")
        f.cli("push")
        self.equal(f.git(a, "rev-parse", "HEAD"), old_head, "previous remote is untouched")
        self.equal(f.git(b, "rev-parse", "HEAD"), f.git(f.cache, "rev-parse", "HEAD"),
                   "new remote receives the retained history and selected change")

    def test_a26_1_populated_directory_is_not_clobbered(self):
        f = self.fixture
        remote = f.remote("populated")
        f.cache.mkdir(parents=True)
        (f.cache / "README.md").write_bytes(b"# Existing README stays byte-for-byte.\r\n")
        (f.cache / ".gitignore").write_bytes(b"*.draft\nlocal-settings.yaml\n")
        (f.cache / "local-settings.yaml").write_bytes(b"synthetic: local-only\n")
        (f.cache / "retained.md").write_bytes(b"# Existing private content.\n")
        before = snapshot(f.cache)
        result = f.cli("setup", remote, ok=None)
        self.equal(snapshot(f.cache), before, "setup preserves every pre-existing file")
        self.equal(result.returncode, 0, "populated setup succeeds without a fabricated commit")
        self.equal(json.loads(f.binding.read_text())["enabled"], True,
                   "preserved cache has an enabled binding")

    def test_a26_1_failed_setup_does_not_enable_sync(self):
        f = self.fixture
        f.cli("setup", f.base / "nonexistent.git", ok=False)
        self.check(not f.binding.exists(), "failed clone does not leave enabled configuration")
        self.check(not f.cache.exists() or not snapshot(f.cache),
                   "failed setup does not invent or overwrite cache content")

    def test_a26_1_conflicting_clone_preserves_existing_local_and_remote_records(self):
        f = self.fixture
        remote = f.remote("conflicting-setup")
        f.setup(remote)
        f.content(b"# Remote record must not disappear.\n")
        f.cli("push")
        record = f.record(b"# Remote record must not disappear.\n").name
        remote_head = f.git(remote, "rev-parse", "HEAD")
        bob = Fixture(self, self.base / "populated-bob", self.kind)
        bob.cache.mkdir(parents=True)
        (bob.cache / record).write_bytes(b"# Distinct local record must not disappear.\n")
        before = snapshot(bob.cache)
        bob.cli("setup", remote, ok=False)
        self.equal(snapshot(bob.cache), before, "clone conflict preserves local bytes")
        self.equal(f.git(remote, "rev-parse", "HEAD"), remote_head, "remote history is untouched")
        self.check(not bob.binding.exists(), "conflicting setup cannot enable synchronization")

    def test_a26_1_failed_rebind_disables_old_authorization(self):
        f = self.fixture
        a, b = f.remote("old-selection"), f.remote("new-selection")
        f.setup(a)
        f.content(b"# Retained private record.\n")
        f.cli("push")
        before = f.state()
        f.git(f.cache, "config", "--local", f"url.{a.as_posix()}.insteadOf", b.as_posix())
        f.cli("setup", b, ok=False)
        self.equal(f.state(), before, "failed selection preserves cache and index")
        for command in ("push", "pull"):
            f.reject_without_transfer(command)

    def test_a26_2_binding_is_required_and_validated(self):
        f = self.fixture
        f.setup(f.remote("binding"))
        f.content(b"# Baseline.\n")
        f.cli("push")
        valid = {
            "schema_version": 1, "enabled": True,
            "url": str(f.base / "binding.git"), "directory": str(f.cache.resolve()),
        }
        cases = {
            "missing": None,
            "legacy URL only": str(f.base / "binding.git"),
            "disabled": json.dumps(dict(valid, enabled=False)),
            "malformed": "{not-json",
            "unknown schema": json.dumps(dict(valid, schema_version=99)),
            "different cache": json.dumps(dict(valid, directory=str(f.base / "elsewhere"))),
            "not a boolean": json.dumps(dict(valid, enabled="true")),
        }
        for label, value in cases.items():
            with self.subTest(binding=label):
                if value is None:
                    f.binding.unlink(missing_ok=True)
                else:
                    f.binding.write_text(value, encoding="utf-8")
                for command in ("push", "pull"):
                    with self.subTest(command=command):
                        f.reject_without_transfer(command)

    def test_a26_2_effective_fetch_and_push_destinations_must_match(self):
        f = self.fixture
        a, b = f.remote("bound"), f.remote("other")
        f.setup(a)
        f.content(b"# Existing history.\n")
        f.cli("push")
        changes = (
            (("remote.origin.url", str(b)), "origin drift"),
            (("remote.origin.pushurl", str(b)), "pushurl drift"),
            (("remote.origin.url", str(b)), "multiple fetch URLs"),
            (("remote.origin.pushurl", str(a)), "multiple push URLs"),
            ((f"url.{b.as_posix()}.insteadOf", str(a)), "fetch URL rewrite"),
            ((f"url.{b.as_posix()}.pushInsteadOf", str(a)), "push URL rewrite"),
        )
        for (key, value), label in changes:
            with self.subTest(drift=label):
                f.git(f.cache, "config", "--local", "--replace-all", "remote.origin.url", str(a))
                if label == "multiple push URLs":
                    f.git(f.cache, "config", "--local", "--add", key, str(b))
                if label == "origin drift":
                    f.git(f.cache, "config", "--local", "--replace-all", key, value)
                else:
                    f.git(f.cache, "config", "--local", "--add", key, value)
                for command in ("push", "pull", "status"):
                    with self.subTest(command=command):
                        f.reject_without_transfer(command)
                f.git(f.cache, "config", "--local", "--unset-all", key)
        f.git(f.cache, "config", "--local", "remote.origin.url", str(a))

    def test_a26_2_forget_disables_without_deleting_any_content(self):
        f = self.fixture
        remote = f.remote("forget")
        f.setup(remote)
        f.content(b"# Committed record.\n")
        f.cli("push")
        f.content(b"# Uncommitted edit stays.\n")
        (f.cache / "notes.tmp").write_bytes(b"Untracked local data.\x00\n")
        (f.cache / "unrelated.txt").write_bytes(b"Staged local data.\n")
        f.git(f.cache, "add", "--", "unrelated.txt")
        before = f.state()
        origin = f.git(f.cache, "remote", "get-url", "origin")
        f.cli("forget")
        self.equal(f.state(), before, "forget retains all content and Git history/index")
        self.equal(f.git(f.cache, "remote", "get-url", "origin"), origin,
                   "forget does not erase Git remote configuration")
        for command in ("push", "pull"):
            f.reject_without_transfer(command)
        f.cli("forget")
        self.equal(f.state(), before, "forget is idempotent")
        f.cli("setup", remote)
        self.equal(f.state(), before, "explicit re-enable retains all local bytes")

    def test_a26_2_public_arguments_cannot_override_the_wrapper_binding(self):
        f = self.fixture
        remote = f.remote("fixed-wrapper")
        f.setup(remote)
        before = f.state()
        binding_before = f.binding.read_bytes()
        f.cli("--directory", str(f.base / "different-cache"), "setup", remote, ok=False)
        self.equal(f.state(), before, "public arguments cannot override internal cache selection")
        self.equal(f.binding.read_bytes(), binding_before, "public arguments cannot replace binding")

    def test_a26_4_help_and_unconfigured_status_do_not_create_a_cache(self):
        f = self.fixture
        for command in ("help", "--help", "-h"):
            with self.subTest(command=command):
                result = f.cli(command)
                self.check("PRIVATE" in result.stdout, "public help retains the privacy boundary")
                self.check("setup <repo-url>" in result.stdout, "public help describes setup")
        f.cli("status")
        f.cli("--status")
        self.check(not f.cache.exists(), "help/status never initialize or enable private sync")
        self.check(not f.binding.exists(), "help/status leave binding absent")

    def test_a26_4_unrelated_staging_cannot_be_published(self):
        f = self.fixture
        remote = f.remote("staged-data")
        f.setup(remote)
        f.content(b"# Original selected record.\n")
        f.cli("push")
        f.content(b"# Selected change not yet committed.\n")
        (f.cache / "unrelated.txt").write_bytes(b"Unrelated staged local content.\n")
        f.git(f.cache, "add", "--", "unrelated.txt")
        head = f.git(remote, "rev-parse", "HEAD")
        f.reject_without_transfer("push")
        self.equal(f.git(remote, "rev-parse", "HEAD"), head, "unrelated staging is not published")

    def test_a26_4_two_machine_push_pull_and_explicit_origin(self):
        f = self.fixture
        a, b = f.remote("round-trip"), f.remote("decoy")
        f.setup(a)
        source_before = snapshot(f.project)
        f.content(b"# Alice revision one.\n")
        if self.kind == "roles":
            (f.cache / "nested").mkdir()
            (f.cache / "nested/reviewer.md").write_bytes(b"# Nested private role.\n")
            (f.cache / "private.draft").write_bytes(b"Unselected draft.\n")
        f.cli("--push")
        bob = Fixture(self, self.base / "bob", self.kind)
        bob.setup(a)
        self.equal(snapshot(bob.cache), {
            key: value for key, value in snapshot(f.cache).items() if key != "private.draft"
        }, "fresh setup receives the real selected remote content")
        bob_source_before = snapshot(bob.project)
        f.content(b"# Alice revision two.\n")
        f.cli("push")
        bob.git(bob.cache, "remote", "add", "decoy", str(b))
        bob.git(bob.cache, "config", "--local", "branch.main.remote", "decoy")
        bob.git(bob.cache, "config", "--local", "branch.main.merge", "refs/heads/main")
        bob.cli("--pull")
        self.equal(snapshot(bob.project), bob_source_before, "pull preserves repo-local lessons")
        record = bob.record(b"# Alice revision two.\n")
        if self.kind == "roles":
            record.write_bytes(b"# Bob revision three.\n")
        else:
            bob.git(bob.project, "remote", "add", "origin", str(f.project))
            bob.content(b"# Bob's distinct project lessons.\n")
        bob.cli("push")
        f.cli("pull")
        self.equal(snapshot(bob.cache), {
            key: value for key, value in snapshot(f.cache).items() if key != "private.draft"
        }, "changes round-trip back to the first machine")
        self.equal(f.git(b, "for-each-ref", "--format=%(refname)"), "",
                   "unrelated upstream remote is never contacted for sync")
        if self.kind == "roles":
            self.equal(snapshot(f.project), source_before, "role sync does not change source repo")

    def test_a26_4_failed_transport_is_nonzero_and_push_is_retryable(self):
        f = self.fixture
        remote = f.remote("retry")
        f.setup(remote)
        f.content(b"# First revision.\n")
        f.cli("push")
        f.content(b"# Pending revision survives transport failure.\n")
        offline = remote.with_name("temporarily-offline.git")
        remote.rename(offline)
        try:
            f.cli("push", ok=False)
            pending = f.git(f.cache, "rev-parse", "HEAD")
            before = f.state()
            f.cli("pull", ok=False)
            self.equal(f.state(), before, "failed pull preserves local pending commit")
        finally:
            offline.rename(remote)
        f.cli("push")
        self.equal(f.git(remote, "rev-parse", "HEAD"), pending,
                   "retry pushes already committed content even without a file diff")

    def test_a26_4_pull_refuses_conflicting_dirty_content(self):
        f = self.fixture
        remote = f.remote("conflict")
        f.setup(remote)
        f.content(b"# Original.\n")
        f.cli("push")
        bob = Fixture(self, self.base / "conflicting-bob", self.kind)
        bob.setup(remote)
        local_record = bob.record(b"# Original.\n")
        local_record.write_bytes(b"# Bob's unsaved local edit.\n")
        f.content(b"# Alice changed the remote record.\n")
        f.cli("push")
        before = bob.state()
        bob.cli("pull", ok=False)
        self.equal(bob.state(), before, "pull refuses rather than overwriting local edits")

    def test_a26_4_destination_change_never_overwrites_unrelated_history(self):
        f = self.fixture
        a, b = f.remote("history-a"), f.remote("history-b")
        f.setup(a)
        f.content(b"# History belonging to A.\n")
        f.cli("push")
        a_head = f.git(a, "rev-parse", "HEAD")
        bob = Fixture(self, self.base / "independent-history", self.kind)
        bob.setup(b)
        bob.content(b"# Unrelated history belonging to B.\n")
        bob.cli("push")
        b_head = f.git(b, "rev-parse", "HEAD")
        f.cli("setup", b)
        before = f.state()
        f.cli("push", ok=False)
        f.cli("pull", ok=False)
        self.equal(f.state(), before, "unrelated history requires explicit manual reconciliation")
        self.equal(f.git(a, "rev-parse", "HEAD"), a_head, "old remote history is retained")
        self.equal(f.git(b, "rev-parse", "HEAD"), b_head, "selected remote is never force-pushed")


class RolesSyncTests(PrivateSyncTests):
    kind = "roles"

    def test_a26_4_git_symlink_records_retain_their_type(self):
        f = self.fixture
        remote = f.remote("link-record")
        f.setup(remote)
        f.content(b"# Shared role target.\n")
        f.cli("push")
        target_text = f.base / "link-target.txt"
        target_text.write_bytes(b"architect.md")
        blob = f.git(f.cache, "hash-object", "-w", str(target_text))
        f.git(f.cache, "update-index", "--add", "--cacheinfo", f"120000,{blob},linked-role.md")
        f.git(f.cache, "commit", "-qm", "fixture symbolic role")
        f.git(f.cache, "push", "-q", "origin", "HEAD")
        bob = Fixture(self, self.base / "link-reader", "roles")
        bob.setup(remote)
        bob.cli("push")
        self.check(
            f.git(remote, "ls-tree", "HEAD", "--", "linked-role.md").startswith("120000 "),
            "Git's symlink representation survives setup and push without dereferencing",
        )


class LessonsSyncTests(PrivateSyncTests):
    kind = "lessons"

    def test_a26_3_equal_basenames_and_legacy_records_round_trip(self):
        f = self.fixture
        remote = f.remote("legacy")
        f.setup(remote)
        legacy = f.cache / "project.md"
        legacy.write_bytes(b"# Historical basename-only record.\n")
        f.git(f.cache, "add", "--", "project.md")
        f.git(f.cache, "commit", "-qm", "fixture legacy record")
        f.git(f.cache, "push", "-q", "origin", "HEAD")
        project_b = f.base / "different-parent" / "project"
        f.make_project(project_b)
        f.content(b"# Project A.\n")
        f.cli("push")
        record_a = f.record(b"# Project A.\n").name
        f.content(b"# Project B.\n", project=project_b)
        f.cli("push", cwd=project_b)
        record_b = f.record(b"# Project B.\n").name
        self.check(record_a != record_b, "same basename does not share a lesson record")
        self.check(record_a.startswith("project--") and record_b.startswith("project--"),
                   "stable identities retain a readable project name")
        nested = f.project / "nested"
        nested.mkdir()
        f.content(b"# Updated project A.\n")
        f.cli("push", cwd=nested)
        self.equal(f.record(b"# Updated project A.\n").name, record_a,
                   "identity is stable across calls and current subdirectories")
        self.equal(legacy.read_bytes(), b"# Historical basename-only record.\n",
                   "migration keeps the old ambiguous record byte-for-byte")
        self.equal((f.cache / record_b).read_bytes(), b"# Project B.\n",
                   "updating A cannot overwrite B")
        bob = Fixture(self, self.base / "legacy-reader", "lessons")
        bob.setup(remote)
        bob.cli("pull")
        self.equal(snapshot(bob.cache), snapshot(f.cache), "all three records round-trip")

    def test_a26_3_remote_identity_is_stable_across_clone_names_and_file_urls(self):
        f = self.fixture
        vault = f.remote("identity-vault")
        source = f.remote("source-project")
        f.setup(vault)
        f.git(f.project, "remote", "add", "origin", str(source))
        f.content(b"# Shared project, first machine.\n")
        f.cli("push")
        first_record = f.record(b"# Shared project, first machine.\n").name
        other = f.base / "another-checkout-name"
        f.make_project(other, origin=source.as_uri())
        f.content(b"# Shared project, another machine.\n", project=other)
        f.cli("push", cwd=other)
        self.equal(f.record(b"# Shared project, another machine.\n").name, first_record,
                   "local and file URL aliases of one origin keep one stable identity")
        self.check(first_record.startswith("source-project--"),
                   "origin-backed record has a readable name, not a local path")
        self.equal(len(list(f.cache.glob("*.md"))), 1, "renamed clone adds no duplicate record")

    def test_a26_3_distinct_local_origins_are_not_merged_by_git_suffix(self):
        f = self.fixture
        f.setup(f.remote("suffix-vault"))
        origins = [f.base / "source-origin", f.base / "source-origin.git"]
        records = []
        for index, origin in enumerate(origins):
            origin.mkdir()
            f.git(origin, "init", "-q", "--bare", "-b", "main")
            project = f.base / str(index) / "project"
            f.make_project(project, origin=origin)
            content = f"# Distinct repository {index}.\n".encode()
            f.content(content, project=project)
            f.cli("push", cwd=project)
            records.append(f.record(content).name)
        self.check(records[0] != records[1], "distinct local origins retain distinct identities")
        self.equal(len(list(f.cache.glob("*.md"))), 2, "neither source record is overwritten")

    def test_a26_3_linked_worktrees_share_the_canonical_project_identity(self):
        f = self.fixture
        f.setup(f.remote("worktree-vault"))
        f.git(f.project, "add", ".claude")
        f.git(f.project, "commit", "-qm", "fixture source repository")
        f.content(b"# Main worktree lessons.\n")
        f.cli("push")
        original = f.record(b"# Main worktree lessons.\n").name
        linked = f.base / "different-worktree-name"
        f.git(f.project, "worktree", "add", "-q", "-b", "linked-fixture", str(linked))
        f.content(b"# Linked worktree lessons.\n", project=linked)
        f.cli("push", cwd=linked)
        self.equal(f.record(b"# Linked worktree lessons.\n").name, original,
                   "linked worktree uses the same Git common-directory identity")
        self.equal(len(list(f.cache.glob("*.md"))), 1, "worktree names add no duplicate records")

    def test_a26_3_legacy_lessons_source_path_still_works(self):
        f = self.fixture
        remote = f.remote("legacy-source")
        f.setup(remote)
        project = f.base / "old-layout"
        lessons = f.make_project(project, legacy=True)
        lessons.write_bytes(b"# Legacy tasks lessons remain supported.\n")
        f.cli("push", cwd=project)
        f.record(lessons.read_bytes())
        self.equal(lessons.read_bytes(), b"# Legacy tasks lessons remain supported.\n",
                   "legacy source is read without migration or edits")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--leaf", choices=["A26.1", "A26.2", "A26.3", "A26.4"])
    parser.add_argument("--case", action="append", default=[])
    args = parser.parse_args()
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for test_class in (RolesSyncTests, LessonsSyncTests):
        for name in loader.getTestCaseNames(test_class):
            if (
                (not args.leaf or name.startswith("test_" + args.leaf.lower().replace(".", "_")))
                and (not args.case or name in args.case)
            ):
                suite.addTest(test_class(name))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    passed = result.wasSuccessful() and result.testsRun > 0 and ASSERTIONS > 0
    print(f"{'PASS' if passed else 'FAIL'}: private-sync-binding: "
          f"{result.testsRun} scenarios, {ASSERTIONS} assertions, "
          f"{len(result.skipped)} skipped", flush=True)
    sys.exit(0 if passed else 1)
