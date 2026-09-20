# component: snapshot-ownership-test
# implements: ADR-0010
# intent: .claude/plans/universal-implementation/packages/P03.md
# constraints: all mutation and failure injection uses disposable fixtures
# last_intent_review: 2026-09-20
from datetime import datetime, timedelta, timezone
from contextlib import redirect_stderr
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SOURCE / "lib"))
spec = importlib.util.spec_from_file_location("li_snapshot", SOURCE / "bin/li-snapshot.py")
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


class SnapshotOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lintel-snapshot-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "owned root"
        self.root.mkdir()
        self.store = self.base / "backups with spaces"
        self.store.mkdir()
        (self.root / "a file.txt").write_bytes(b"original a\x00\n")
        (self.root / "b.txt").write_bytes(b"original b\n")
        (self.root / "unrelated.txt").write_text("user work")

    def create(self, absent=()):
        return snapshot.create_snapshot(self.root, self.store, ["a file.txt", "b.txt"], absent)

    def change_and_bind(self, identifier):
        (self.root / "a file.txt").write_bytes(b"owned change a")
        (self.root / "b.txt").write_bytes(b"owned change b")
        expected = {p: snapshot.file_state(self.root, p) for p in ("a file.txt", "b.txt")}
        snapshot.bind_result(self.root, self.store, identifier, expected)

    def test_verified_copy_and_normalized_manifest(self):
        created = self.create()
        manifest = snapshot.load_snapshot(self.root, self.store, created["id"])
        self.assertEqual(manifest["owner"], str(self.root))
        self.assertEqual(manifest["state"], "complete")
        for entry in manifest["files"]:
            data = (self.root / entry["path"]).read_bytes()
            self.assertEqual(entry["sha256"], hashlib.sha256(data).hexdigest())
            blob = self.store / created["id"] / "blobs" / entry["sha256"]
            self.assertEqual(blob.read_bytes(), data)

    def test_owned_rollback_preserves_unrelated_work_and_handles_new_file(self):
        created = self.create(["new file.txt"])
        (self.root / "a file.txt").write_bytes(b"owned a")
        (self.root / "b.txt").unlink()
        (self.root / "new file.txt").write_text("owned new")
        (self.root / "unrelated.txt").write_text("more user work")
        expected = {p: snapshot.file_state(self.root, p)
                    for p in ("a file.txt", "b.txt", "new file.txt")}
        snapshot.bind_result(self.root, self.store, created["id"], expected)
        result = snapshot.restore_snapshot(self.root, self.store, created["id"])
        self.assertEqual(result["state"], "complete")
        self.assertEqual((self.root / "a file.txt").read_bytes(), b"original a\x00\n")
        self.assertEqual((self.root / "b.txt").read_bytes(), b"original b\n")
        self.assertFalse((self.root / "new file.txt").exists())
        self.assertEqual((self.root / "unrelated.txt").read_text(), "more user work")
        self.assertEqual(snapshot.restore_snapshot(self.root, self.store, created["id"])["changed"], [])

    def test_unattributed_or_later_user_changes_conflict_before_any_write(self):
        created = self.create()
        (self.root / "a file.txt").write_text("unattributed")
        with self.assertRaises(ValueError):
            snapshot.restore_snapshot(self.root, self.store, created["id"])
        self.change_and_bind(created["id"])
        (self.root / "b.txt").write_text("user changed owned path later")
        with self.assertRaises(ValueError):
            snapshot.restore_snapshot(self.root, self.store, created["id"])
        self.assertEqual((self.root / "a file.txt").read_bytes(), b"owned change a")
        self.assertEqual((self.root / "b.txt").read_text(), "user changed owned path later")
        with self.assertRaises(ValueError):
            snapshot.bind_result(self.root, self.store, created["id"],
                                 {p: snapshot.file_state(self.root, p) for p in ("a file.txt", "b.txt")})

    def test_interrupted_restore_is_resumable_and_never_reported_complete(self):
        created = self.create()
        self.change_and_bind(created["id"])
        apply = snapshot._apply_restore
        calls = []

        def interrupt(*args):
            calls.append(args)
            if len(calls) == 2:
                raise OSError("synthetic interruption")
            return apply(*args)

        with patch.object(snapshot, "_apply_restore", side_effect=interrupt), self.assertRaises(OSError):
            snapshot.restore_snapshot(self.root, self.store, created["id"])
        journal = json.loads((self.store / created["id"] / "restore.json").read_text())
        self.assertEqual(journal["state"], "in-progress")
        self.assertEqual((self.root / "unrelated.txt").read_text(), "user work")
        result = snapshot.restore_snapshot(self.root, self.store, created["id"])
        self.assertEqual(result["state"], "complete")
        self.assertEqual((self.root / "b.txt").read_bytes(), b"original b\n")
        (self.root / "a file.txt").write_text("new user change")
        with self.assertRaises(ValueError):
            snapshot.restore_snapshot(self.root, self.store, created["id"])

    def test_tampered_partial_foreign_and_old_snapshots_are_refused(self):
        for mutation in ("path", "incomplete", "foreign", "version", "blob"):
            with self.subTest(mutation=mutation):
                created = self.create()
                folder = self.store / created["id"]
                manifest_path = folder / "manifest.json"
                manifest = json.loads(manifest_path.read_text())
                if mutation == "path":
                    manifest["files"][0]["path"] = "../outside"
                elif mutation == "incomplete":
                    manifest["state"] = "copying"
                elif mutation == "foreign":
                    manifest["owner"] = str(self.base)
                elif mutation == "version":
                    manifest["schema_version"] = 0
                else:
                    (folder / "blobs" / manifest["files"][0]["sha256"]).write_bytes(b"corrupt")
                manifest_path.write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    snapshot.restore_snapshot(self.root, self.store, created["id"])
        old = self.store / "snapshot-20260501"
        old.mkdir()
        (old / "a file.txt").write_text("old cp -r backup")
        with self.assertRaises(ValueError):
            snapshot.restore_snapshot(self.root, self.store, old.name)
        self.assertTrue((old / "a file.txt").exists())
        self.assertEqual((self.root / "a file.txt").read_bytes(), b"original a\x00\n")

    def test_root_traversal_symlink_and_snapshot_store_overlap_fail(self):
        for path in ("../outside", "C:/outside", "/root", "a/../b.txt", "b.txt:stream",
                     "b.txt.", "b.txt ", "aux.txt"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                snapshot.create_snapshot(self.root, self.store, [path])
        nested = self.root / "backups"
        nested.mkdir()
        with self.assertRaises(ValueError):
            snapshot.create_snapshot(self.root, nested, ["b.txt"])
        from unittest.mock import patch
        with patch.object(snapshot, "is_link", return_value=True):
            with self.assertRaises(ValueError):
                snapshot.create_snapshot(self.root, self.store, ["b.txt"])
        with self.assertRaises(ValueError):
            snapshot.restore_snapshot(self.root, self.store, "../outside")

    def test_wrong_result_receipt_and_stale_receipt_cannot_authorize_restore(self):
        created = self.create()
        with self.assertRaises(ValueError):
            snapshot.bind_result(self.root, self.store, created["id"], {"../outside": None})
        self.change_and_bind(created["id"])
        receipt_path = self.store / created["id"] / "result.json"
        receipt = json.loads(receipt_path.read_text())
        receipt["snapshot_digest"] = "0" * 64
        receipt_path.write_text(json.dumps(receipt))
        with self.assertRaises(ValueError):
            snapshot.restore_snapshot(self.root, self.store, created["id"])
        self.assertEqual((self.root / "a file.txt").read_bytes(), b"owned change a")

    def test_failed_copy_never_activates_partial_snapshot(self):
        with patch.object(snapshot, "read_owned", side_effect=OSError("synthetic read failure")):
            with self.assertRaises(OSError):
                self.create()
        self.assertEqual(list(self.store.glob("snapshot-*")), [])
        self.assertEqual((self.root / "b.txt").read_bytes(), b"original b\n")

    def test_windows_publication_retry_is_bounded_and_attributable(self):
        error = PermissionError("synthetic Windows activation lock")
        error.winerror = 5
        original = Path.rename
        attempts = []

        def transient(path, target):
            attempts.append(target)
            if len(attempts) == 1:
                raise error
            return original(path, target)

        warnings = io.StringIO()
        with patch.object(Path, "rename", transient), patch.object(snapshot.time, "sleep"), redirect_stderr(warnings):
            created = self.create()
        self.assertEqual(created["publication_retries"], 1)
        self.assertIn("retry 1/4", warnings.getvalue())
        self.assertEqual(snapshot.load_snapshot(self.root, self.store, created["id"])["state"], "complete")
        before = set(self.store.glob("snapshot-*"))
        with patch.object(Path, "rename", side_effect=error) as rename, \
                patch.object(snapshot.time, "sleep"), redirect_stderr(warnings), self.assertRaises(OSError):
            self.create()
        self.assertEqual(rename.call_count, 5)
        self.assertEqual(set(self.store.glob("snapshot-*")), before)
        self.assertTrue(list(self.store.glob(".pending-*")))
        self.assertEqual((self.root / "a file.txt").read_bytes(), b"original a\x00\n")

    def test_source_change_during_copy_never_publishes_stale_snapshot(self):
        original = snapshot.read_owned
        changed = False

        def read_then_change(root, relative, *args):
            nonlocal changed
            result = original(root, relative, *args)
            if root == self.root and not changed:
                changed = True
                (self.root / relative).write_bytes(b"concurrent user bytes")
            return result

        with patch.object(snapshot, "read_owned", side_effect=read_then_change), self.assertRaises(ValueError):
            self.create()
        self.assertEqual(list(self.store.glob("snapshot-*")), [])
        self.assertEqual((self.root / "a file.txt").read_bytes(), b"concurrent user bytes")

    def test_late_edit_during_restore_staging_is_preserved(self):
        created = self.create()
        self.change_and_bind(created["id"])
        original = snapshot.atomic_write

        def change_before_replace(root, relative, data, *args, **kwargs):
            if root == self.root:
                (self.root / relative).write_bytes(b"late user edit")
            return original(root, relative, data, *args, **kwargs)

        with patch.object(snapshot, "atomic_write", side_effect=change_before_replace), self.assertRaises(ValueError):
            snapshot.restore_snapshot(self.root, self.store, created["id"])
        self.assertEqual((self.root / "a file.txt").read_bytes(), b"late user edit")
        self.assertEqual((self.root / "b.txt").read_bytes(), b"owned change b")
        with self.assertRaises(ValueError):
            snapshot.restore_snapshot(self.root, self.store, created["id"])

    def test_native_directory_escape_is_refused(self):
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "preserve.txt").write_text("outside the owned root")
        link = self.root / "escape"
        if os.name == "nt":
            env = dict(os.environ, LINTEL_TEST_LINK=str(link), LINTEL_TEST_TARGET=str(outside))
            made = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                                   "New-Item -ItemType Junction -Path $env:LINTEL_TEST_LINK "
                                   "-Target $env:LINTEL_TEST_TARGET -ErrorAction Stop | Out-Null"],
                                  env=env, capture_output=True)
            self.assertEqual(made.returncode, 0, made.stderr)
        else:
            link.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            snapshot.create_snapshot(self.root, self.store, ["escape/preserve.txt"])
        self.assertEqual((outside / "preserve.txt").read_text(), "outside the owned root")

    def test_retention_is_union_of_newest_five_and_recent_thirty_days(self):
        now = datetime(2026, 9, 20, tzinfo=timezone.utc)
        ids = []
        for age in (90, 80, 70, 60, 50, 40, 2):
            created = self.create()
            ids.append(created["id"])
            manifest_path = self.store / created["id"] / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["created_at"] = (now - timedelta(days=age)).isoformat()
            manifest_path.write_text(json.dumps(manifest))
        unrelated = self.store / "user-notes"
        unrelated.mkdir()
        (unrelated / "keep.txt").write_text("not owned")
        plan = snapshot.retention_plan(self.root, self.store, now=now)
        self.assertEqual(set(plan["eligible"]), set(ids[:2]))
        self.assertEqual(set(plan["keep"]), set(ids[2:]))
        dates = {}
        for identifier in ids:
            manifest_path = self.store / identifier / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            dates[identifier] = manifest["created_at"]
            manifest["created_at"] = (now - timedelta(days=1)).isoformat()
            manifest_path.write_text(json.dumps(manifest))
        self.assertEqual(set(snapshot.retention_plan(self.root, self.store, now=now)["keep"]), set(ids))
        for identifier in ids:
            manifest_path = self.store / identifier / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["created_at"] = dates[identifier]
            manifest_path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            snapshot.prune_snapshots(self.root, self.store, [ids[-1]], now=now)
        snapshot.prune_snapshots(self.root, self.store, ids[:2], now=now)
        self.assertTrue((unrelated / "keep.txt").exists())
        self.assertTrue(all((self.store / p).exists() for p in ids[2:]))

    def test_cli_binds_operation_evidence_and_restores_exact_bytes(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        command = [sys.executable, str(SOURCE / "bin/li-snapshot.py"), "--root", str(self.root),
                   "--store", str(self.store)]

        def run(*args):
            result = subprocess.run([*command, *args], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)

        created = run("create", "--path", "a file.txt")
        (self.root / "a file.txt").write_bytes(b"owned update")
        expected = self.base / "operation-result.json"
        expected.write_text(json.dumps({"a file.txt": snapshot.file_state(self.root, "a file.txt")}))
        run("bind", created["id"], "--expected", str(expected))
        self.assertEqual(run("verify", created["id"])["owner"], str(self.root))
        self.assertEqual(run("restore", created["id"])["state"], "complete")
        self.assertEqual((self.root / "a file.txt").read_bytes(), b"original a\x00\n")

    def test_refactor_restore_preserves_preexisting_index_and_worktree_changes(self):
        env = dict(os.environ, HOME=str(self.base), GIT_CONFIG_NOSYSTEM="1",
                   GIT_CONFIG_GLOBAL=str(self.base / "no-global-config"))

        def git(*args):
            return subprocess.run(["git", "-C", str(self.root), *args], env=env,
                                  check=True, capture_output=True).stdout

        git("init", "-q")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        git("config", "core.hooksPath", str(self.base / "no-hooks"))
        git("config", "core.autocrlf", "false")
        git("add", "a file.txt", "b.txt")
        git("commit", "-qm", "baseline")
        (self.root / "b.txt").write_bytes(b"user staged")
        git("add", "b.txt")
        (self.root / "b.txt").write_bytes(b"user unstaged")
        before = (git("diff", "--binary"), git("diff", "--cached", "--binary"),
                  git("status", "--porcelain=v1", "-z"), git("rev-parse", "HEAD"))
        created = self.create()
        self.change_and_bind(created["id"])
        snapshot.restore_snapshot(self.root, self.store, created["id"])
        self.assertEqual(before, (git("diff", "--binary"), git("diff", "--cached", "--binary"),
                                 git("status", "--porcelain=v1", "-z"), git("rev-parse", "HEAD")))
        self.assertEqual((self.root / "unrelated.txt").read_text(), "user work")


if __name__ == "__main__":
    unittest.main(verbosity=2)
