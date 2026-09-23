# component: managed-transaction-tests
# implements: ADR-0030
# intent: .claude/plans/universal-implementation/packages/P10.md
# constraints: isolated file roots and accepted P03 recovery; no host operations
# last_intent_review: 2026-09-20
import argparse
from contextlib import redirect_stderr
import errno
import importlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
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

    def retry_trial(self, name):
        directory = self.base / name
        directory.mkdir()
        self.root, self.store = directory / "consumer", directory / "store"
        self.root.mkdir()
        for relative, data in (("a.txt", b"before a"), ("b.txt", b"before b"),
                               ("custom.txt", b"never owned")):
            (self.root / relative).write_bytes(data)
        self.expected = {name: file_state(self.root, name) for name in self.changes}
        self.modes = {name: self.expected["a.txt"]["mode"] for name in self.changes}

    def replacement_error(self, source, target, code):
        error = OSError(errno.EACCES, "injected owned replacement denial")
        if code is not None:
            error.winerror = code
        error.filename, error.filename2 = str(source), str(target)
        return error

    def journal_fixture(self, *, existing):
        folder = self.store / "transactions" / ("transaction-" + "b" * 32)
        native_io_path(folder).mkdir(parents=True)
        previous = {"schema_version": 1, "id": folder.name, "state": "prepared",
                    "plan_digest": "a" * 64, "files": {"a.txt": "pending"}}
        if existing:
            self.module._save_journal(folder, previous)
        planned = {**previous, "state": "applying", "files": {"a.txt": "applying"}}
        return folder, planned

    def test_journal_replace_transients_have_bounded_notices_and_backoff(self):
        original_replace = os.replace
        windows = SimpleNamespace(name="nt", path=os.path)
        for code in (5, 32, 33):
            for failures in range(1, 5):
                for existing in (False, True):
                    with self.subTest(winerror=code, failures=failures, existing=existing):
                        self.retry_trial(f"transient-{code}-{failures}-{existing}")
                        with self.module._lock(self.root, self.store):
                            folder, planned = self.journal_fixture(existing=existing)
                            before = file_state(folder, "journal.json")
                            attempts = []

                            def replace(source, target):
                                if Path(target) == native_io_path(folder / "journal.json"):
                                    self.assertTrue(native_io_path(self.store / ".operation-lock").is_dir())
                                    self.assertEqual(file_state(folder, "journal.json"), before)
                                    attempts.append((str(source), str(target)))
                                    if len(attempts) <= failures:
                                        raise self.replacement_error(source, target, code)
                                return original_replace(source, target)

                            notices = io.StringIO()
                            with patch.object(self.module, "os", windows), patch("os.replace", side_effect=replace), \
                                    patch("time.sleep", wraps=time.sleep) as delays, redirect_stderr(notices):
                                self.module._save_journal(folder, planned)
                            self.assertEqual(len(attempts), failures + 1)
                            self.assertEqual([call.args[0] for call in delays.call_args_list],
                                             [0.05 * 2 ** attempt for attempt in range(failures)])
                            lines = notices.getvalue().splitlines()
                            self.assertEqual(len(lines), failures)
                            for attempt, line in enumerate(lines, 1):
                                self.assertIn("journal", line)
                                self.assertIn(f"retry {attempt}/4", line)
                                self.assertIn(f"winerror {code}", line)
                            self.assertEqual(native_io_path(folder / "journal.json").read_bytes(),
                                             self.module.json_bytes(planned))
                            self.assertEqual(sorted(path.name for path in native_io_path(folder).iterdir()),
                                             ["journal.json"])
                            print(json.dumps({"B01": "injected-transient", "winerror": code,
                                              "failures": failures, "existing": existing,
                                              "attempts": len(attempts), "notices": lines,
                                              "delays": [call.args[0] for call in delays.call_args_list]}))
                        self.assertEqual(self.files(), {"a.txt": b"before a", "b.txt": b"before b",
                                                       "custom.txt": b"never owned"})

    def test_journal_replace_persistent_failure_retains_explicit_recovery(self):
        original_replace = os.replace
        windows = SimpleNamespace(name="nt", path=os.path)
        for code in (5, 32, 33):
            with self.subTest(winerror=code):
                self.retry_trial(f"persistent-{code}")
                before, errors = self.files(), []

                def replace(source, target):
                    if Path(target).name == "journal.json":
                        staged = json.loads(native_io_path(Path(source)).read_bytes())
                        if staged["files"]["a.txt"] == "applied":
                            self.assertTrue(native_io_path(self.store / ".operation-lock").is_dir())
                            error = self.replacement_error(source, target, code)
                            errors.append(error)
                            raise error
                    return original_replace(source, target)

                notices = io.StringIO()
                with patch.object(self.module, "os", windows), patch("os.replace", side_effect=replace), \
                        patch("time.sleep", wraps=time.sleep) as delays, redirect_stderr(notices):
                    with self.assertRaises(OSError) as failure:
                        self.apply()
                self.assertIs(failure.exception, errors[-1])
                self.assertEqual(len(errors), 5)
                self.assertEqual([call.args[0] for call in delays.call_args_list], [0.05, 0.1, 0.2, 0.4])
                self.assertEqual(len(notices.getvalue().splitlines()), 4)
                identifier, = [path.name for path in native_io_path(self.store / "transactions").iterdir()]
                state = self.module.inspect_transaction(self.root, self.store, identifier)
                self.assertEqual(state["state"], "applying")
                self.assertEqual(state["files"]["a.txt"], "applying")
                self.assertEqual(self.files(), {**before, "a.txt": b"after a"})
                with self.assertRaisesRegex(ValueError, "incomplete"):
                    self.apply()
                recovered = self.module.recover_transaction(self.root, self.store, identifier)
                self.assertEqual(recovered["state"], "recovered")
                self.assertEqual(self.files(), before)
                print(json.dumps({"B01": "injected-persistent", "winerror": code, "attempts": len(errors),
                                  "notices": notices.getvalue().splitlines(), "state": state,
                                  "recovery": recovered["state"], "original_bytes_restored": True}))

    def test_journal_replace_nonretryable_and_nonwindows_errors_propagate(self):
        original_replace = os.replace
        for platform, code, replacement in (
                ("nt", 2, True), ("nt", 80, True), ("nt", 1117, True), ("nt", None, True),
                ("posix", 5, True), ("posix", 32, True), ("posix", 33, True),
                ("nt", 5, False)):
            with self.subTest(platform=platform, winerror=code, replacement=replacement):
                self.retry_trial(f"nonretryable-{platform}-{code}-{replacement}")
                with self.module._lock(self.root, self.store):
                    folder, planned = self.journal_fixture(existing=True)
                    before = file_state(folder, "journal.json")
                    errors = []

                    def replace(source, target):
                        if Path(target) == native_io_path(folder / "journal.json"):
                            error = self.replacement_error(source, target, code)
                            if not replacement:
                                error.filename2 = None
                            errors.append(error)
                            raise error
                        return original_replace(source, target)

                    notices = io.StringIO()
                    with patch.object(self.module, "os", SimpleNamespace(name=platform, path=os.path)), \
                            patch("os.replace", side_effect=replace), patch("time.sleep") as delays, \
                            redirect_stderr(notices):
                        with self.assertRaises(OSError) as failure:
                            self.module._save_journal(folder, planned)
                    self.assertEqual(len(errors), 1)
                    self.assertIs(failure.exception, errors[0])
                    delays.assert_not_called()
                    self.assertEqual(notices.getvalue(), "")
                    self.assertEqual(file_state(folder, "journal.json"), before)
                    print(json.dumps({"B01": "injected-nonretryable", "simulated_platform": platform,
                                      "winerror": code, "replacement": replacement, "attempts": 1,
                                      "same_exception": True, "notices": []}))

    def test_journal_replace_refuses_changed_saved_state(self):
        original_replace = os.replace
        windows = SimpleNamespace(name="nt", path=os.path)
        for scenario in ("absent-created", "existing-edited", "existing-deleted", "changed-during-backoff"):
            with self.subTest(scenario=scenario):
                self.retry_trial(scenario)
                with self.module._lock(self.root, self.store):
                    folder, planned = self.journal_fixture(existing=scenario != "absent-created")
                    target = native_io_path(folder / "journal.json")
                    attempts, observed, delays = [], [], []

                    def change():
                        if scenario == "existing-deleted":
                            target.unlink()
                        else:
                            target.write_bytes(b'{"consumer":"intervening journal edit"}\n')
                        observed.append(file_state(folder, "journal.json"))

                    def replace(source, destination):
                        if Path(destination) == target:
                            attempts.append(str(source))
                            if scenario != "changed-during-backoff":
                                change()
                            raise self.replacement_error(source, destination, 5)
                        return original_replace(source, destination)

                    def wait(seconds):
                        delays.append(seconds)
                        change()

                    notices = io.StringIO()
                    with patch.object(self.module, "os", windows), patch("os.replace", side_effect=replace), \
                            patch("time.sleep", side_effect=wait), redirect_stderr(notices):
                        with self.assertRaisesRegex(ValueError, "journal.*changed|changed.*journal"):
                            self.module._save_journal(folder, planned)
                    self.assertEqual(len(attempts), 1)
                    self.assertEqual(len(observed), 1)
                    self.assertEqual(file_state(folder, "journal.json"), observed[0])
                    self.assertEqual(delays, [0.05] if scenario == "changed-during-backoff" else [])
                    self.assertEqual(len(notices.getvalue().splitlines()), len(delays))
                    print(json.dumps({"B01": "changed-journal-refusal", "scenario": scenario,
                                      "attempts": len(attempts), "notices": notices.getvalue().splitlines(),
                                      "intervening_state_preserved": True}))

    def test_journal_replace_requires_held_operation_lock(self):
        self.retry_trial("missing-lock")
        folder = self.store / "transactions" / ("transaction-" + "b" * 32)
        native_io_path(folder).mkdir(parents=True)
        with patch("os.replace", wraps=os.replace) as replacement:
            with self.assertRaisesRegex(ValueError, "lock"):
                self.module._save_journal(folder, {"state": "prepared"})
        replacement.assert_not_called()
        self.assertFalse(native_io_path(folder / "journal.json").exists())

    def test_journal_retry_does_not_retry_other_publications(self):
        original_replace = os.replace
        for phase in ("staged", "plan", "target", "snapshot", "result", "binding", "restore"):
            with self.subTest(phase=phase):
                self.retry_trial("other-" + phase)
                identifier = None
                if phase in ("binding", "restore"):
                    if phase == "binding":
                        original_write = self.module._write_change

                        def interrupt(*args):
                            original_write(*args)
                            raise OSError("injected target interruption for explicit recovery")

                        with patch.object(self.module, "_write_change", side_effect=interrupt):
                            with self.assertRaises(OSError):
                                self.apply()
                        identifier, = [path.name for path in native_io_path(self.store / "transactions").iterdir()]
                    else:
                        identifier = self.apply()["id"]
                errors = []

                def replace(source, target):
                    target = Path(target)
                    selected = (
                        phase == "staged" and target.parent.name == "staged"
                        or phase == "plan" and target.name == "plan.json"
                        or phase == "target" and target == native_io_path(self.root / "a.txt")
                        or phase == "snapshot" and target.name == "manifest.json"
                        or phase == "result" and target.name == "result.json"
                        or phase == "binding" and target.name == "recovery-binding.json"
                        or phase == "restore" and target.name == "restore.json"
                    )
                    if selected:
                        error = self.replacement_error(source, target, 5)
                        errors.append(error)
                        raise error
                    return original_replace(source, target)

                notices = io.StringIO()
                with patch("os.replace", side_effect=replace), patch("time.sleep") as delays, redirect_stderr(notices):
                    with self.assertRaises(OSError) as failure:
                        if identifier:
                            self.module.recover_transaction(self.root, self.store, identifier)
                        else:
                            self.apply()
                self.assertEqual(len(errors), 1)
                self.assertIs(failure.exception, errors[0])
                delays.assert_not_called()
                self.assertEqual(notices.getvalue(), "")
                self.assertFalse(native_io_path(self.store / ".operation-lock").exists())
                print(json.dumps({"B01": "other-publication-not-retried", "phase": phase,
                                  "attempts": len(errors), "same_exception": True, "notices": []}))


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], *remaining])
