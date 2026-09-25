# component: managed-transaction-tests
# implements: ADR-0030
# intent: .claude/plans/universal-implementation/packages/P10.md
# constraints: isolated file roots and accepted P03 recovery; no host operations
# last_intent_review: 2026-09-24
import argparse
from contextlib import ExitStack, contextmanager, redirect_stderr
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
import context_safety
from context_safety import file_state, native_io_path

# F-INT-5: host functions captured before any test patch; the shield calls them directly.
HOST_REPLACE, HOST_READ, HOST_SLEEP = os.replace, context_safety.read_owned, time.sleep
HOST_WINERRORS = (5, 32, 33)
HOST_DELAYS = (0.02, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2)
UNSTABLE_READ = "File changed while reading: "


def plain_path(path) -> str:
    text = os.fspath(path)
    if text.startswith("\\\\?\\UNC\\"):
        text = "\\\\" + text[8:]
    elif text.startswith("\\\\?\\"):
        text = text[4:]
    return os.path.normcase(os.path.abspath(text))


class HostTransientExhausted(AssertionError):
    """A real host transient outlasted the bounded shield, so the test fails explicitly."""


class HostTransientShield:
    """Keep real host transients out of the product's journal retry budget (F-INT-5).

    Replacement injections wrap os.replace above this shield, so an error from the host
    replacement below it is real. Read injections change a file inside a read, below the
    shield, and mark each change, so only an unmarked identity refusal counts as a host
    transient. Absorbing real transients leaves the product's sleeps and notices exactly
    those the test injected. Every absorption is reported; a bounded budget turns a
    persistent host failure into an explicit test failure instead of a product retry or a pass.
    """
    reports = []

    def __init__(self, roots, *, source="host", replace=HOST_REPLACE, read=HOST_READ, sleep=HOST_SLEEP):
        self.roots, self.source = [plain_path(root) for root in roots], source
        self.host_replace, self.host_read, self.host_sleep = replace, read, sleep
        self.injections, self.rereading, self.absorbed = 0, False, []

    def owned(self, path) -> bool:
        candidate = plain_path(path)
        for root in self.roots:
            try:
                if os.path.commonpath([root, candidate]) == root:
                    return True
            except ValueError:
                continue
        return False

    def absorb(self, kind, path, retry, error):
        outcome = "absorbed-host-transient" if retry < len(HOST_DELAYS) else "unabsorbed-host-transient"
        record = {"F-INT-5": outcome, "source": self.source, "class": kind, "path": plain_path(path),
                  "shield_retry": retry + 1, "winerror": getattr(error, "winerror", None), "error": str(error)}
        if self.source == "host":
            HostTransientShield.reports.append(record)
        print(json.dumps(record), flush=True)
        if retry == len(HOST_DELAYS):
            raise HostTransientExhausted(f"Host {kind} transient outlasted {retry} shield retries: {path}") from error
        self.absorbed.append(record)
        self.host_sleep(HOST_DELAYS[retry])

    def replace(self, source, target, *args, **kwargs):
        for retry in range(len(HOST_DELAYS) + 1):
            try:
                return self.host_replace(source, target, *args, **kwargs)
            except OSError as error:
                if getattr(error, "winerror", None) not in HOST_WINERRORS or not self.owned(target):
                    raise
                self.absorb("replace", target, retry, error)

    def read_owned(self, root, relative, *args, **kwargs):
        for retry in range(len(HOST_DELAYS) + 1):
            injections, self.rereading = self.injections, retry > 0
            try:
                return self.host_read(root, relative, *args, **kwargs)
            except ValueError as error:
                if (str(error) != UNSTABLE_READ + relative or self.injections != injections
                        or not self.owned(Path(root) / relative)):
                    raise
                self.absorb("read", Path(root) / relative, retry, error)
            finally:
                self.rereading = False


class ManagedTransaction(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        reports = HostTransientShield.reports
        absorbed = [record for record in reports if record["F-INT-5"] == "absorbed-host-transient"]
        print(json.dumps({"F-INT-5": "host-transient-summary", "absorbed": len(absorbed),
                          "replace": sum(record["class"] == "replace" for record in absorbed),
                          "read": sum(record["class"] == "read" for record in absorbed),
                          "unabsorbed": len(reports) - len(absorbed)}), flush=True)

    def host_patches(self, shield):
        return [patch("os.replace", new=shield.replace),
                *(patch.object(owner, "read_owned", new=shield.read_owned)
                  for owner in (context_safety, self.module, self.module.snapshot))]

    def inject(self):
        """Mark a deliberate change made during a read, so no shield absorbs its refusal."""
        for shield in self.shields:
            shield.injections += 1

    def rereading(self):
        return any(shield.rereading for shield in self.shields)

    @contextmanager
    def simulated_host(self, *, roots=None, replace=None, read=None):
        """A fresh shield over a simulated host; the real shield stays beneath replacements."""
        delays = []
        shield = HostTransientShield(roots or (self.base,), source="simulated",
                                     replace=replace or self.shields[0].replace,
                                     read=read or self.shields[0].read_owned, sleep=delays.append)
        with ExitStack() as stack:
            for patcher in self.host_patches(shield):
                stack.enter_context(patcher)
            self.shields.append(shield)
            try:
                yield shield, delays
            finally:
                self.shields.remove(shield)

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
        self.shields = [HostTransientShield((self.base, created_root))]
        for patcher in self.host_patches(self.shields[0]):
            patcher.start()
            self.addCleanup(patcher.stop)
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

    @unittest.skipUnless(os.name == "nt", "platform: windows-only; native Windows store arguments and sharing-violation retry")
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

    def disturbed_journal_reads(self, selected, *, injected=True):
        """Reset the owned journal's timestamps inside chosen reads, as IC-F01 observed."""
        original_open, original_fstat = os.open, os.fstat
        journals, reads, disturbed = {}, [], []

        def opened(path, flags, *args, **kwargs):
            descriptor = original_open(path, flags, *args, **kwargs)
            if Path(path).name == "journal.json" and not self.rereading():
                journals[descriptor] = Path(path)
            return descriptor

        def status(descriptor):
            path = journals.pop(descriptor, None)
            if path is not None:
                reads.append(str(path))
                if selected(len(reads)):
                    current = os.lstat(path)
                    os.utime(path, ns=(current.st_atime_ns, current.st_mtime_ns - 340_000_000))
                    disturbed.append(len(reads))
                    if injected:
                        self.inject()
            return original_fstat(descriptor)

        return reads, disturbed, (patch("os.open", side_effect=opened), patch("os.fstat", side_effect=status))

    def test_journal_identity_disturbance_rereads_only_a_stable_owned_journal(self):
        for site in ("entry", "staging-check"):
            for disturbances in range(1, 5):
                with self.subTest(site=site, disturbances=disturbances):
                    self.retry_trial(f"disturbed-{site}-{disturbances}")
                    with self.module._lock(self.root, self.store):
                        folder, planned = self.journal_fixture(existing=True)
                        previous = native_io_path(folder / "journal.json").read_bytes()
                        # Each attempt reads the journal twice: its verification, then the staging check.
                        chosen = (set(range(1, disturbances + 1)) if site == "entry"
                                  else {2 * attempt for attempt in range(1, disturbances + 1)})
                        reads, disturbed, patches = self.disturbed_journal_reads(lambda number: number in chosen)
                        notices = io.StringIO()
                        with patches[0], patches[1], patch("time.sleep") as delays, redirect_stderr(notices):
                            self.module._save_journal(folder, planned)
                        self.assertEqual(disturbed, sorted(chosen))
                        self.assertEqual(native_io_path(folder / "journal.json").read_bytes(),
                                         self.module.json_bytes(planned))
                        self.assertNotEqual(previous, self.module.json_bytes(planned))
                        self.assertEqual(sorted(path.name for path in native_io_path(folder).iterdir()),
                                         ["journal.json"])
                        self.assertEqual([call.args[0] for call in delays.call_args_list],
                                         [0.05 * 2 ** attempt for attempt in range(disturbances)])
                        lines = notices.getvalue().splitlines()
                        self.assertEqual(lines, [f"li-transaction: owned journal changed during a verification read; "
                                                 f"retry {attempt}/4." for attempt in range(1, disturbances + 1)])
                        print(json.dumps({"IC-F01": "injected-transient", "site": site,
                                          "disturbed_reads": disturbed, "journal_reads": len(reads),
                                          "notices": lines, "published": True}))

    def test_journal_identity_disturbance_is_bounded_and_content_changes_still_refuse(self):
        self.retry_trial("disturbed-persistent")
        with self.module._lock(self.root, self.store):
            folder, planned = self.journal_fixture(existing=True)
            previous = native_io_path(folder / "journal.json").read_bytes()
            reads, disturbed, patches = self.disturbed_journal_reads(lambda number: True)
            notices = io.StringIO()
            with patches[0], patches[1], patch("time.sleep") as delays, redirect_stderr(notices):
                with self.assertRaises(ValueError) as failure:
                    self.module._save_journal(folder, planned)
            self.assertEqual(str(failure.exception), "File changed while reading: journal.json")
            self.assertEqual(disturbed, [1, 2, 3, 4, 5])
            self.assertEqual([call.args[0] for call in delays.call_args_list], [0.05, 0.1, 0.2, 0.4])
            self.assertEqual(len(notices.getvalue().splitlines()), 4)
            self.assertEqual(native_io_path(folder / "journal.json").read_bytes(), previous)
            self.assertEqual(sorted(path.name for path in native_io_path(folder).iterdir()), ["journal.json"])
            print(json.dumps({"IC-F01": "injected-persistent", "attempts": 5, "notices": 4,
                              "same_message": True, "journal_preserved": True}))
        self.retry_trial("disturbed-content-change")
        with self.module._lock(self.root, self.store):
            folder, planned = self.journal_fixture(existing=True)
            target = native_io_path(folder / "journal.json")
            intervening = b'{"consumer":"intervening journal edit during its staging check"}\n'
            original_open, original_fstat = os.open, os.fstat
            journals, reads = {}, []

            def opened(path, flags, *args, **kwargs):
                descriptor = original_open(path, flags, *args, **kwargs)
                if Path(path).name == "journal.json" and not self.rereading():
                    journals[descriptor] = Path(path)
                return descriptor

            def status(descriptor):
                if journals.pop(descriptor, None) is not None:
                    reads.append(descriptor)
                    if len(reads) == 2:
                        with open(target, "wb") as stream:
                            stream.write(intervening)
                        self.inject()
                return original_fstat(descriptor)

            notices = io.StringIO()
            with patch("os.open", side_effect=opened), patch("os.fstat", side_effect=status), \
                    patch("time.sleep") as delays, redirect_stderr(notices):
                with self.assertRaisesRegex(ValueError, "changed before replacement retry; preserve it"):
                    self.module._save_journal(folder, planned)
            self.assertEqual(target.read_bytes(), intervening)
            self.assertEqual(len(reads), 3)
            self.assertEqual([call.args[0] for call in delays.call_args_list], [0.05])
            self.assertEqual(len(notices.getvalue().splitlines()), 1)
            print(json.dumps({"IC-F01": "content-change-refused", "journal_reads": len(reads),
                              "notices": notices.getvalue().splitlines(), "intervening_bytes_preserved": True}))

    def test_journal_identity_disturbance_after_replacement_denial_keeps_b01_rule(self):
        original_replace = os.replace
        windows = SimpleNamespace(name="nt", path=os.path)
        for scenario in ("unchanged", "edited-during-denial"):
            with self.subTest(scenario=scenario):
                self.retry_trial("denied-disturbed-" + scenario)
                with self.module._lock(self.root, self.store):
                    folder, planned = self.journal_fixture(existing=True)
                    target = native_io_path(folder / "journal.json")
                    intervening = b'{"consumer":"intervening journal edit during denial"}\n'
                    # Read 1 establishes the before-state, read 2 is the staging check and
                    # read 3 verifies the journal after the injected replacement denial.
                    reads, disturbed, patches = self.disturbed_journal_reads(lambda number: number == 3)
                    attempts = []

                    def replace(source, destination):
                        if Path(destination) == target:
                            attempts.append(str(source))
                            if len(attempts) == 1:
                                if scenario == "edited-during-denial":
                                    target.write_bytes(intervening)
                                raise self.replacement_error(source, destination, 5)
                        return original_replace(source, destination)

                    notices = io.StringIO()
                    with patches[0], patches[1], patch.object(self.module, "os", windows), \
                            patch("os.replace", side_effect=replace), patch("time.sleep") as delays, \
                            redirect_stderr(notices):
                        if scenario == "unchanged":
                            self.module._save_journal(folder, planned)
                        else:
                            with self.assertRaisesRegex(ValueError, "changed before replacement retry; preserve it"):
                                self.module._save_journal(folder, planned)
                    self.assertEqual(disturbed, [3])
                    self.assertEqual([call.args[0] for call in delays.call_args_list], [0.05])
                    self.assertEqual(notices.getvalue().splitlines(),
                                     ["li-transaction: Windows blocked owned journal replacement; retry 1/4 (winerror 5)."])
                    self.assertEqual(target.read_bytes(),
                                     self.module.json_bytes(planned) if scenario == "unchanged" else intervening)
                    self.assertEqual(len(attempts), 2 if scenario == "unchanged" else 1)
                    print(json.dumps({"IC-F01": "denial-then-disturbed-verification", "scenario": scenario,
                                      "replacement_attempts": len(attempts), "journal_reads": len(reads),
                                      "notices": notices.getvalue().splitlines()}))

    def test_journal_identity_disturbance_during_apply_publishes_or_stays_recoverable(self):
        self.retry_trial("disturbed-apply-transient")
        armed = {"reads": 0}
        reads, disturbed, patches = self.disturbed_journal_reads(lambda number: number == armed["reads"])
        original_write = self.module._write_change

        def published(root, relative, *args):
            original_write(root, relative, *args)
            if relative == "a.txt":
                armed["reads"] = len(reads) + 1

        notices = io.StringIO()
        with patches[0], patches[1], patch.object(self.module, "_write_change", side_effect=published), \
                redirect_stderr(notices):
            result = self.apply()
        self.assertEqual(result["state"], "complete")
        self.assertEqual(len(disturbed), 1)
        self.assertEqual(self.module.inspect_transaction(self.root, self.store, result["id"])["state"], "complete")
        self.assertEqual(self.files(), {"a.txt": b"after a", "b.txt": b"after b", "custom.txt": b"never owned",
                                        "new.txt": b"created"})
        self.assertEqual(notices.getvalue().splitlines(),
                         ["li-transaction: owned journal changed during a verification read; retry 1/4."])
        print(json.dumps({"IC-F01": "apply-transient", "state": result["state"],
                          "notices": notices.getvalue().splitlines()}))

        self.retry_trial("disturbed-apply-persistent")
        before = self.files()
        armed = {"reads": None}
        reads, disturbed, patches = self.disturbed_journal_reads(
            lambda number: armed["reads"] is not None and number >= armed["reads"])

        def published_then_persistent(root, relative, *args):
            original_write(root, relative, *args)
            if relative == "a.txt":
                armed["reads"] = len(reads) + 1

        notices = io.StringIO()
        with patches[0], patches[1], patch.object(self.module, "_write_change", side_effect=published_then_persistent), \
                patch("time.sleep") as delays, redirect_stderr(notices):
            with self.assertRaisesRegex(ValueError, "^File changed while reading: journal.json$"):
                self.apply()
        self.assertEqual(len(disturbed), 5)
        self.assertEqual([call.args[0] for call in delays.call_args_list], [0.05, 0.1, 0.2, 0.4])
        self.assertFalse(native_io_path(self.store / ".operation-lock").exists())
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
        print(json.dumps({"IC-F01": "apply-persistent", "state": state, "notices": len(notices.getvalue().splitlines()),
                          "recovery": recovered["state"], "original_bytes_restored": True}))

    def host_denial(self, *, times, code=5):
        """A simulated host denying owned journal replacement below the shield under test."""
        errors, below = [], self.shields[0].replace

        def replace(source, target, *args, **kwargs):
            if Path(target).name == "journal.json" and (times is None or len(errors) < times):
                error = OSError(errno.EACCES, "simulated host replacement denial", str(source), None, str(target))
                error.winerror = code
                errors.append(error)
                raise error
            return below(source, target, *args, **kwargs)

        return errors, replace

    def test_host_transient_shield_stays_beneath_injections_and_is_bounded(self):
        windows = SimpleNamespace(name="nt", path=os.path)
        verification = "li-transaction: owned journal changed during a verification read; retry {}/4."
        denial = "li-transaction: Windows blocked owned journal replacement; retry 1/4 (winerror 5)."
        for scenario in ("denied-once", "staging-check-4", "read-disturbed", "persistent", "nonretryable", "unowned"):
            with self.subTest(scenario=scenario):
                self.retry_trial("host-shield-" + scenario)
                with self.module._lock(self.root, self.store):
                    folder, planned = self.journal_fixture(existing=True)
                    previous = native_io_path(folder / "journal.json").read_bytes()
                    errors, replace = self.host_denial(times=None if scenario == "persistent" else 1,
                                                       code=80 if scenario == "nonretryable" else 5)
                    # The two observed points: a lone host denial, and one after four injected disturbances.
                    chosen = {"staging-check-4": {2, 4, 6, 8}, "read-disturbed": {1}}.get(scenario, set())
                    reads, disturbed, patches = self.disturbed_journal_reads(
                        lambda number: number in chosen, injected=scenario != "read-disturbed")
                    host = ({"read": HOST_READ} if scenario == "read-disturbed" else
                            {"replace": replace, "roots": (self.base / "elsewhere",) if scenario == "unowned" else None})
                    refusal = {"persistent": HostTransientExhausted, "nonretryable": OSError}.get(scenario)
                    notices = io.StringIO()
                    with self.simulated_host(**host) as (shield, host_delays), patches[0], patches[1], \
                            patch.object(self.module, "os", windows), patch("time.sleep") as delays, \
                            redirect_stderr(notices):
                        if refusal:
                            with self.assertRaises(refusal) as failure:
                                self.module._save_journal(folder, planned)
                        else:
                            self.module._save_journal(folder, planned)
                    lines = notices.getvalue().splitlines()
                    product_delays = [call.args[0] for call in delays.call_args_list]
                    absorbed = [record["class"] for record in shield.absorbed]
                    self.assertEqual(disturbed, sorted(chosen))
                    self.assertEqual(sorted(path.name for path in native_io_path(folder).iterdir()), ["journal.json"])
                    self.assertEqual(native_io_path(folder / "journal.json").read_bytes(),
                                     previous if refusal else self.module.json_bytes(planned))
                    if scenario == "staging-check-4":
                        self.assertEqual(product_delays, [0.05, 0.1, 0.2, 0.4])
                        self.assertEqual(lines, [verification.format(attempt) for attempt in range(1, 5)])
                    elif scenario == "unowned":
                        self.assertEqual(product_delays, [0.05])
                        self.assertEqual(lines, [denial])
                    else:
                        delays.assert_not_called()
                        self.assertEqual(lines, [])
                    if scenario == "persistent":
                        self.assertIs(failure.exception.__cause__, errors[-1])
                        self.assertEqual(len(errors), len(HOST_DELAYS) + 1)
                        self.assertEqual(absorbed, ["replace"] * len(HOST_DELAYS))
                        self.assertEqual(host_delays, list(HOST_DELAYS))
                    elif scenario == "nonretryable":
                        self.assertIs(failure.exception, errors[0])
                        self.assertEqual((len(errors), absorbed, host_delays), (1, [], []))
                    elif scenario == "unowned":
                        self.assertEqual((len(errors), absorbed, host_delays), (1, [], []))
                    elif scenario == "read-disturbed":
                        self.assertEqual((len(errors), len(reads), absorbed, host_delays), (0, 2, ["read"], [0.02]))
                    else:
                        self.assertEqual((len(errors), absorbed, host_delays), (1, ["replace"], [0.02]))
                    print(json.dumps({"F-INT-5": "simulated-host-point", "scenario": scenario,
                                      "shield_absorbed": absorbed, "host_errors": len(errors),
                                      "product_delays": product_delays, "product_notices": lines}))


if __name__ == "__main__":
    # Verbose output names each skip reason, which the runner needs to classify platform-only skips.
    unittest.main(argv=[sys.argv[0], *remaining], verbosity=2)
