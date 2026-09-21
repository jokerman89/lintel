# component: managed-transaction-tests
# implements: ADR-0030
# intent: .claude/plans/universal-implementation/packages/P10.md
# constraints: isolated file roots and accepted P03 recovery; no host operations
# last_intent_review: 2026-09-20
import argparse
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, required=True)
options, remaining = parser.parse_known_args()
sys.dont_write_bytecode = True
sys.path.insert(0, str(options.root.resolve() / "lib"))
from context_safety import file_state, native_io_path


class ManagedTransaction(unittest.TestCase):
    def setUp(self):
        self.module = importlib.import_module("managed_transaction")
        self.tmp = tempfile.TemporaryDirectory(prefix="lintel-txn-")
        created_name = self.tmp.name
        created_root = Path(created_name).resolve()

        def cleanup():
            self.assertEqual(self.tmp.name, created_name)
            self.assertEqual(Path(self.tmp.name).resolve(), created_root)
            self.assertTrue(created_root.name.startswith("lintel-txn-"))
            self.tmp.name = str(native_io_path(created_root))
            try:
                self.tmp.cleanup()
            finally:
                self.tmp.name = created_name

        self.addCleanup(cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "consumer"
        self.store = self.base / "store"
        self.root.mkdir()
        (self.root / "a.txt").write_bytes(b"before a")
        (self.root / "b.txt").write_bytes(b"before b")
        (self.root / "custom.txt").write_bytes(b"never owned")
        self.changes = {"a.txt": b"after a", "b.txt": b"after b", "new.txt": b"created"}
        self.expected = {name: file_state(self.root, name) for name in self.changes}
        mode = self.expected["a.txt"]["mode"]
        self.modes = {name: mode for name in self.changes}

    def apply(self):
        return self.module.apply_files(self.root, self.store, self.changes, self.expected,
                                       self.modes, label="synthetic consumer operation", final_paths=["new.txt"])

    def files(self):
        return {p.name: p.read_bytes() for p in self.root.iterdir() if p.is_file()}

    def test_exact_create_update_delete_and_explicit_recovery(self):
        self.changes["b.txt"] = None
        self.modes["b.txt"] = None
        before = self.files()
        result = self.apply()
        self.assertEqual(result["state"], "complete")
        self.assertFalse((self.root / "b.txt").exists())
        self.assertEqual((self.root / "new.txt").read_bytes(), b"created")
        self.assertEqual((self.root / "custom.txt").read_bytes(), b"never owned")
        recovered = self.module.recover_transaction(self.root, self.store, result["id"])
        self.assertEqual(recovered["state"], "recovered")
        self.assertEqual(self.files(), before)

    def test_stale_expected_aliased_paths_and_overlapping_store_refuse_before_writes(self):
        (self.root / "a.txt").write_bytes(b"user edit")
        before = self.files()
        with self.assertRaises(ValueError):
            self.apply()
        self.assertFalse(self.store.exists())
        self.assertEqual(self.files(), before)
        self.expected["a.txt"] = file_state(self.root, "a.txt")
        with self.assertRaises(ValueError):
            self.module.apply_files(self.root, self.root / "store", self.changes, self.expected,
                                    self.modes, label="invalid overlap")
        self.assertFalse((self.root / "store").exists())
        self.changes["../escape"] = b"bad"
        self.expected["../escape"] = None
        self.modes["../escape"] = self.modes["a.txt"]
        with self.assertRaises(ValueError):
            self.apply()
        self.assertFalse(self.store.exists())
        self.assertEqual(self.files(), before)

    def test_interruption_is_visible_and_recovery_rejects_user_edits(self):
        original = self.module._write_change
        writes = []

        def interrupted(root, relative, data, mode, expected):
            original(root, relative, data, mode, expected)
            writes.append(relative)
            if len(writes) == 1:
                raise OSError("synthetic failure after atomic publication")

        before = self.files()
        with patch.object(self.module, "_write_change", side_effect=interrupted):
            with self.assertRaisesRegex(OSError, "synthetic"):
                self.apply()
        identifiers = [p.name for p in (self.store / "transactions").iterdir()]
        self.assertEqual(len(identifiers), 1)
        identifier = identifiers[0]
        self.assertNotEqual(self.module.inspect_transaction(self.root, self.store, identifier)["state"], "complete")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.apply()
        (self.root / "b.txt").write_bytes(b"user after interruption")
        edited = self.files()
        with self.assertRaises(ValueError):
            self.module.recover_transaction(self.root, self.store, identifier)
        self.assertEqual(self.files(), edited)
        (self.root / "b.txt").write_bytes(b"before b")
        self.module.recover_transaction(self.root, self.store, identifier)
        self.assertEqual(self.files(), before)

    def test_post_recovery_permission_is_consumed_even_for_the_old_postimage(self):
        result = self.apply()
        self.module.recover_transaction(self.root, self.store, result["id"])
        (self.root / "a.txt").write_bytes(b"after a")
        user = self.files()
        with self.assertRaises(ValueError):
            self.module.recover_transaction(self.root, self.store, result["id"])
        self.assertEqual(self.files(), user)

    def test_corrupt_foreign_receipt_and_changed_stage_refuse_before_recovery(self):
        result = self.apply()
        foreign = self.base / "different consumer"
        foreign.mkdir()
        with self.assertRaises(ValueError):
            self.module.recover_transaction(foreign, self.store, result["id"])
        before = self.files()
        receipt = self.store / "transactions" / result["id"]
        plan = json.loads((receipt / "plan.json").read_text(encoding="utf-8"))
        plan["label"] = "tampered plan"
        (receipt / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.module.recover_transaction(self.root, self.store, result["id"])
        self.assertEqual(self.files(), before)

    def test_default_store_binds_full_root_and_existing_empty_store_is_not_adopted(self):
        other = self.base / "second" / self.root.name
        other.mkdir(parents=True)
        first = self.module.default_store(self.root)
        second = self.module.default_store(other)
        self.assertNotEqual(first.name, second.name)
        self.assertEqual(first.parent, self.root.parent)
        self.assertEqual(second.parent, other.parent)
        self.store.mkdir()
        before = self.files()
        with self.assertRaises(ValueError):
            self.apply()
        self.assertEqual(list(self.store.iterdir()), [])
        self.assertEqual(self.files(), before)

    def test_terminal_labels_cannot_hide_missing_or_incomplete_evidence(self):
        result = self.apply()
        folder = self.store / "transactions" / result["id"]
        path = folder / "journal.json"
        journal = json.loads(path.read_text(encoding="utf-8"))
        journal["files"]["a.txt"] = "pending"
        path.write_text(json.dumps(journal), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.module.assert_ready(self.root, self.store)

    def long_paths(self):
        parent = self.base / "deep consumer and store"
        while len(str(parent)) < 275:
            parent /= "same-location-" + "x" * 40
        self.root, self.store = parent / "consumer", parent / "owned store"
        native_io_path(self.root).mkdir(parents=True)
        for name, content in (("a.txt", b"before a"), ("b.txt", b"before b"),
                              ("custom.txt", b"never owned")):
            native_io_path(self.root / name).write_bytes(content)
        self.expected = {name: file_state(self.root, name) for name in self.changes}
        self.modes = {name: self.expected["a.txt"]["mode"] for name in self.changes}
        self.assertGreater(len(str(self.root)), 275)
        self.assertGreater(len(str(self.store)), 275)
        self.assertFalse(str(self.root).startswith("\\\\?\\"))
        self.assertFalse(str(self.store).startswith("\\\\?\\"))

    def native_files(self):
        return {path.name: path.read_bytes() for path in native_io_path(self.root).iterdir()
                if path.is_file()}

    def test_long_native_io_preserves_logical_receipts_and_exact_recovery(self):
        self.long_paths()
        self.changes["b.txt"] = None
        self.modes["b.txt"] = None
        before = self.native_files()
        result = self.apply()
        self.assertEqual(result["state"], "complete")
        self.assertEqual(result["store"], str(self.store))
        self.assertEqual(self.native_files(), {"a.txt": b"after a", "new.txt": b"created",
                                              "custom.txt": b"never owned"})
        folder = self.store / "transactions" / result["id"]
        plan = json.loads(native_io_path(folder / "plan.json").read_bytes())
        marker = json.loads(native_io_path(self.store / self.module.MARKER).read_bytes())
        snapshot = json.loads(native_io_path(
            self.store / "snapshots" / result["snapshot_id"] / "manifest.json").read_bytes())
        self.assertEqual(plan["owner"], str(self.root))
        self.assertEqual(marker["owner"], str(self.root))
        self.assertEqual(snapshot["owner"], str(self.root))
        self.module.assert_ready(self.root, self.store)
        inspected = self.module.inspect_transaction(self.root, self.store, result["id"])
        self.assertEqual(inspected["state"], "complete")
        self.assertFalse(native_io_path(self.store / ".operation-lock").exists())
        recovered = self.module.recover_transaction(self.root, self.store, result["id"])
        self.assertEqual(recovered["state"], "recovered")
        self.assertEqual(recovered["store"], str(self.store))
        self.assertEqual(self.native_files(), before)
        self.module.assert_ready(self.root, self.store)
        native_io_path(self.root / "a.txt").write_bytes(b"after a")
        edited = self.native_files()
        with self.assertRaises(ValueError):
            self.module.recover_transaction(self.root, self.store, result["id"])
        self.assertEqual(self.native_files(), edited)

    def test_long_native_interruption_conflict_lock_and_foreign_store_refuse(self):
        self.long_paths()
        before = self.native_files()
        original = self.module._write_change

        def interrupted(*args):
            original(*args)
            raise OSError("synthetic long-path interruption after real write")

        with patch.object(self.module, "_write_change", side_effect=interrupted):
            with self.assertRaisesRegex(OSError, "synthetic long-path interruption"):
                self.apply()
        identifier, = [path.name for path in native_io_path(self.store / "transactions").iterdir()]
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.module.assert_ready(self.root, self.store)
        native_io_path(self.root / "b.txt").write_bytes(b"user edit after interruption")
        edited = self.native_files()
        with self.assertRaisesRegex(ValueError, "conflict"):
            self.module.recover_transaction(self.root, self.store, identifier)
        self.assertEqual(self.native_files(), edited)
        native_io_path(self.root / "b.txt").write_bytes(before["b.txt"])
        lock = native_io_path(self.store / ".operation-lock")
        lock.mkdir()
        with self.assertRaisesRegex(ValueError, "locked"):
            self.module.recover_transaction(self.root, self.store, identifier)
        self.assertTrue(lock.is_dir())
        lock.rmdir()
        foreign = self.root.parent / "foreign consumer"
        native_io_path(foreign).mkdir()
        with self.assertRaisesRegex(ValueError, "foreign"):
            self.module.recover_transaction(foreign, self.store, identifier)
        self.module.recover_transaction(self.root, self.store, identifier)
        self.assertEqual(self.native_files(), before)
        unowned = self.root.parent / "unowned store"
        native_io_path(unowned).mkdir()
        with self.assertRaisesRegex(ValueError, "Unowned"):
            self.module.apply_files(self.root, unowned, self.changes, self.expected,
                                    self.modes, label="not authorized by existence")
        self.assertEqual(list(native_io_path(unowned).iterdir()), [])
        self.assertEqual(self.native_files(), before)


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], *remaining])
