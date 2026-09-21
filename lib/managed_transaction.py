# component: owned-file-transaction
# implements: ADR-0030
# intent: .claude/plans/universal-implementation/packages/P10.md
# constraints: caller owns selection; P03 owns snapshots/restore; no automatic rollback
# last_intent_review: 2026-09-20
"""Explicit file publication for Python runtime consumers, not a bare installer."""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
from typing import Mapping, Optional, Sequence
import uuid

sys.dont_write_bytecode = True
from context_safety import (atomic_write, checked_root, file_state, is_link, json_bytes, native_io_path,
                            path_key, read_owned, relative_path, safe_path)

SOURCE = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("lintel_owned_snapshot", SOURCE / "bin/li-snapshot.py")
if _spec is None or _spec.loader is None:
    raise ImportError("Required owned snapshot helper is missing from the installed source.")
snapshot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(snapshot)

SCHEMA = 1
MARKER = ".lintel-managed-store.json"
ID = re.compile(r"transaction-[a-f0-9]{32}")
MAX_BYTES = 128 * 1024 * 1024


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate transaction JSON field.")
        result[key] = value
    return result


def _nonfinite(_: str):
    raise ValueError("Nonfinite transaction value.")


def _json(root: Path, name: str) -> tuple[dict, str]:
    raw, _ = read_owned(root, name, MAX_BYTES)
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                       parse_constant=_nonfinite)
    if not isinstance(value, dict):
        raise ValueError("Transaction record must be an object.")
    return value, hashlib.sha256(raw).hexdigest()


def _same(first, second) -> bool:
    return json_bytes(first) == json_bytes(second)


def default_store(root: Path) -> Path:
    root = root.resolve()
    identity = path_key(str(root)) if os.name == "nt" else str(root)
    key = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return root.parent / (".lintel-recovery-" + key)


def assert_ready(root: Path, store: Path) -> None:
    root, store = _roots(root, store)
    _pending(root, store)


def _roots(root: Path, store: Path) -> tuple[Path, Path]:
    root = checked_root(root)
    if os.name == "nt" and str(store).startswith(("/", "\\")) and not Path(store).drive:
        raise ValueError("Pass --store as a native Windows argument; do not reinterpret an MSYS environment path.")
    store = Path(os.path.abspath(store))
    for parent in (store, *store.parents):
        if is_link(parent) or (native_io_path(parent).exists() and not native_io_path(parent).is_dir()):
            raise ValueError(f"Unsafe recovery store: {parent}")
    if root.is_relative_to(store) or store.is_relative_to(root) or SOURCE.is_relative_to(store) or store.is_relative_to(SOURCE):
        raise ValueError("Recovery store must be separate from the source and target.")
    if native_io_path(store).exists():
        if not native_io_path(safe_path(store, MARKER)).is_file():
            raise ValueError("Unowned recovery store; preserve it rather than adopting existing directories.")
        marker, _ = _json(store, MARKER)
        if marker != {"schema_version": SCHEMA, "owner": str(root)}:
            raise ValueError("Unowned or foreign recovery store; preserve it.")
    return root, store


def _pending(root: Path, store: Path, *, locked: bool = False) -> None:
    if not native_io_path(store).exists():
        return
    if not locked and native_io_path(safe_path(store, ".operation-lock")).exists():
        raise ValueError("Recovery store is locked; verify no operation is running before removing that exact empty lock.")
    folder = safe_path(store, "transactions")
    if native_io_path(folder).exists():
        for candidate in sorted(native_io_path(folder).iterdir()):
            entry = folder / candidate.name
            if not native_io_path(entry).is_dir() or not ID.fullmatch(entry.name):
                raise ValueError("Unknown/incomplete transaction evidence; preserve it for inspection.")
            _, journal, _ = _receipt(root, store, entry.name)
            if journal["state"] not in ("complete", "recovered"):
                raise ValueError(f"Existing incomplete transaction: {entry.name}; recover explicitly before a new operation.")


@contextmanager
def _lock(root: Path, store: Path):
    try:
        native_io_path(store).mkdir(parents=True, exist_ok=False, mode=0o700)
    except FileExistsError:
        _roots(root, store)
    else:
        atomic_write(store, MARKER, json_bytes({"schema_version": SCHEMA, "owner": str(root)}),
                     expected=None, check_expected=True)
    lock = safe_path(store, ".operation-lock")
    try:
        native_io_path(lock).mkdir(mode=0o700)
    except FileExistsError as error:
        raise ValueError("Recovery store is locked; no automatic lock stealing.") from error
    try:
        yield
    finally:
        native_io_path(lock).rmdir()


def _write_change(root: Path, relative: str, data: Optional[bytes], mode: Optional[int], expected) -> None:
    if not _same(file_state(root, relative), expected):
        raise ValueError(f"Target changed before publication: {relative}")
    if data is None:
        native_io_path(safe_path(root, relative)).unlink()
    else:
        atomic_write(root, relative, data, mode, expected=expected, check_expected=True)


def _receipt(root: Path, store: Path, identifier: str) -> tuple[dict, dict, Path]:
    if not ID.fullmatch(identifier):
        raise ValueError("Unsupported transaction ID; retain historical copies for manual recovery.")
    folder = safe_path(store, "transactions/" + identifier)
    folder = checked_root(folder)
    plan, digest = _json(folder, "plan.json")
    journal, _ = _json(folder, "journal.json")
    if (set(plan) != {"schema_version", "id", "owner", "source", "label", "snapshot_id", "snapshot_digest",
                      "files", "final_paths"}
            or type(plan["schema_version"]) is not int or plan["schema_version"] != SCHEMA
            or plan["id"] != identifier or plan["owner"] != str(root) or not isinstance(plan["label"], str)
            or not isinstance(plan["files"], dict) or not 1 <= len(plan["files"]) <= 5000
            or not isinstance(plan["source"], str) or not plan["source"]
            or not isinstance(plan["snapshot_id"], str) or not re.fullmatch(r"snapshot-[a-f0-9]{32}", plan["snapshot_id"])
            or not isinstance(plan["snapshot_digest"], str) or not re.fullmatch(r"[a-f0-9]{64}", plan["snapshot_digest"])
            or not isinstance(plan["final_paths"], list) or not all(isinstance(path, str) for path in plan["final_paths"])
            or len(set(plan["final_paths"])) != len(plan["final_paths"])
            or not set(plan["final_paths"]) <= set(plan["files"])):
        raise ValueError("Unsupported or foreign transaction plan.")
    if (set(journal) != {"schema_version", "id", "plan_digest", "state", "files"}
            or type(journal["schema_version"]) is not int or journal["schema_version"] != SCHEMA
            or journal["id"] != identifier or journal["plan_digest"] != digest
            or journal["state"] not in ("prepared", "applying", "complete", "recovering", "recovered")
            or not isinstance(journal["files"], dict) or set(journal["files"]) != set(plan["files"])
            or any(value not in ("pending", "applying", "applied") for value in journal["files"].values())):
        raise ValueError("Corrupt/unknown transaction journal or plan identity.")
    snapshot_root = safe_path(store, "snapshots")
    original = snapshot.load_snapshot(root, snapshot_root, plan["snapshot_id"])
    raw, _ = read_owned(snapshot_root, plan["snapshot_id"] + "/manifest.json", MAX_BYTES)
    if hashlib.sha256(raw).hexdigest() != plan["snapshot_digest"]:
        raise ValueError("Transaction snapshot identity changed.")
    original_states = {
        entry["path"]: None if entry["sha256"] is None else {key: entry[key] for key in ("sha256", "size", "mode")}
        for entry in original["files"]
    }
    if set(original_states) != set(plan["files"]):
        raise ValueError("Transaction and snapshot ownership differ.")
    seen, total = set(), 0
    for relative, entry in plan["files"].items():
        relative_path(relative)
        safe_path(root, relative)
        if path_key(relative) in seen or ".git" in relative.casefold().split("/"):
            raise ValueError("Aliased or Git-internal transaction path.")
        seen.add(path_key(relative))
        if (not isinstance(entry, dict) or set(entry) != {"before", "after", "blob", "requested_mode"}
                or not _same(entry["before"], original_states[relative])):
            raise ValueError("Transaction before-image differs from its verified snapshot.")
        if entry["after"] is None:
            if entry["blob"] is not None or entry["requested_mode"] is not None:
                raise ValueError("Invalid deletion plan.")
        else:
            if type(entry["requested_mode"]) is not int or not 0 <= entry["requested_mode"] <= 0o777:
                raise ValueError("Invalid publication mode.")
            if not isinstance(entry["blob"], str) or not re.fullmatch(r"staged/[0-9]{4,5}(?:\.[^/\\:]*)?", entry["blob"]):
                raise ValueError("Invalid staged blob reference.")
            data, actual = read_owned(folder, entry["blob"], MAX_BYTES)
            total += len(data)
            if total > MAX_BYTES or not _same(actual, entry["after"]):
                raise ValueError("Staged after-image failed verification.")
    if journal["state"] == "prepared" and any(phase != "pending" for phase in journal["files"].values()):
        raise ValueError("Prepared transaction has contradictory per-file progress.")
    if journal["state"] in ("complete", "recovered"):
        result, _ = _json(snapshot_root, plan["snapshot_id"] + "/result.json")
        if (result.get("schema_version") != snapshot.SCHEMA or result.get("id") != plan["snapshot_id"]
                or result.get("snapshot_digest") != plan["snapshot_digest"]):
            raise ValueError("Terminal transaction lacks its matching snapshot result.")
        if journal["state"] == "complete":
            if (any(phase != "applied" for phase in journal["files"].values())
                    or not _same(result.get("expected"), {path: entry["after"] for path, entry in plan["files"].items()})):
                raise ValueError("Complete transaction contradicts its verified publication.")
        else:
            restored, _ = _json(snapshot_root, plan["snapshot_id"] + "/restore.json")
            if (restored.get("schema_version") != snapshot.RESTORE_SCHEMA or restored.get("state") != "complete"
                    or restored.get("snapshot_digest") != plan["snapshot_digest"]
                    or restored.get("result_digest") != hashlib.sha256(json_bytes(result)).hexdigest()
                    or not isinstance(restored.get("files"), dict) or set(restored["files"]) != set(plan["files"])
                    or any(not isinstance(entry, dict) or entry.get("state") != "restored" for entry in restored["files"].values())):
                raise ValueError("Recovered transaction lacks complete owned-restore evidence.")
    return plan, journal, folder


def _save_journal(folder: Path, journal: dict) -> None:
    atomic_write(folder, "journal.json", json_bytes(journal))


def apply_files(root: Path, store: Path, changes: Mapping[str, Optional[bytes]], expected: Mapping[str, object],
                modes: Mapping[str, Optional[int]], *, label: str, final_paths: Sequence[str] = ()) -> dict:
    """The producer supplies ownership and expected states; this function cannot invent them."""
    root, store = _roots(root, store)
    _pending(root, store)
    changes, expected, modes = dict(changes), deepcopy(dict(expected)), dict(modes)
    if not isinstance(label, str) or not label.strip() or len(label) > 1000:
        raise ValueError("A transaction requires a nonempty label of at most 1000 characters.")
    if set(changes) != set(expected) or set(changes) != set(modes) or len(changes) > 5000:
        raise ValueError("Changes, expected states and modes must cover the same bounded file set.")
    if len(set(final_paths)) != len(final_paths) or not set(final_paths) <= set(changes):
        raise ValueError("Final publication paths must be a unique subset of changes.")
    seen, total, selected = set(), 0, {}
    for relative, data in changes.items():
        relative_path(relative)
        if path_key(relative) in seen or ".git" in relative.casefold().split("/"):
            raise ValueError("Aliased or Git-internal transaction path.")
        seen.add(path_key(relative))
        current = file_state(root, relative)
        if not _same(current, expected[relative]):
            raise ValueError(f"Caller expected state does not match current bytes: {relative}")
        if data is None:
            if modes[relative] is not None:
                raise ValueError("A deletion cannot request file mode changes.")
            if current is not None:
                selected[relative] = None
        else:
            if not isinstance(data, bytes) or type(modes[relative]) is not int or not 0 <= modes[relative] <= 0o777:
                raise ValueError("Publication needs bytes and an explicit supported mode.")
            total += len(data)
            if total > MAX_BYTES:
                raise ValueError("Transaction exceeds the snapshot byte bound.")
            if current is None or read_owned(root, relative)[0] != data or current["mode"] != modes[relative]:
                selected[relative] = data
    if not selected:
        return {"id": None, "state": "unchanged", "changed": [], "store": str(store)}
    with _lock(root, store):
        _pending(root, store, locked=True)
        snapshots = safe_path(store, "snapshots")
        native_io_path(snapshots).mkdir(exist_ok=True, mode=0o700)
        created = snapshot.create_snapshot(root, snapshots,
                                           [path for path in selected if expected[path] is not None],
                                           [path for path in selected if expected[path] is None])
        for relative in selected:
            if not _same(file_state(root, relative), expected[relative]):
                raise ValueError(f"Expected ownership changed during snapshot: {relative}; preserve {created['id']}.")
        identifier = "transaction-" + uuid.uuid4().hex
        folder = safe_path(store, "transactions/" + identifier)
        native_io_path(folder).mkdir(parents=True, mode=0o700)
        files = {}
        for index, (relative, data) in enumerate(sorted(selected.items())):
            blob, after = None, None
            if data is not None:
                blob = f"staged/{index:04d}{Path(relative).suffix}"
                atomic_write(folder, blob, data, modes[relative])
                copied, after = read_owned(folder, blob, MAX_BYTES)
                if copied != data:
                    raise ValueError(f"Staged copy did not verify: {relative}")
            files[relative] = {"before": expected[relative], "after": after, "blob": blob,
                               "requested_mode": modes[relative]}
        raw, _ = read_owned(snapshots, created["id"] + "/manifest.json", MAX_BYTES)
        plan = {"schema_version": SCHEMA, "id": identifier, "owner": str(root), "source": str(SOURCE),
                "label": label, "snapshot_id": created["id"], "snapshot_digest": hashlib.sha256(raw).hexdigest(),
                "files": files, "final_paths": [path for path in final_paths if path in selected]}
        plan_raw = json_bytes(plan)
        atomic_write(folder, "plan.json", plan_raw)
        journal = {"schema_version": SCHEMA, "id": identifier,
                   "plan_digest": hashlib.sha256(plan_raw).hexdigest(), "state": "prepared",
                   "files": {relative: "pending" for relative in files}}
        _save_journal(folder, journal)
        _receipt(root, store, identifier)
        order = sorted(set(files) - set(plan["final_paths"])) + plan["final_paths"]
        journal["state"] = "applying"
        _save_journal(folder, journal)
        for relative in order:
            entry = files[relative]
            journal["files"][relative] = "applying"
            _save_journal(folder, journal)
            data = read_owned(folder, entry["blob"], MAX_BYTES)[0] if entry["blob"] else None
            _write_change(root, relative, data, entry["requested_mode"], entry["before"])
            if not _same(file_state(root, relative), entry["after"]):
                raise ValueError(f"Published file did not verify: {relative}; recover {identifier} explicitly.")
            journal["files"][relative] = "applied"
            _save_journal(folder, journal)
        after = {relative: entry["after"] for relative, entry in files.items()}
        snapshot.bind_result(root, snapshots, created["id"], after)
        journal["state"] = "complete"
        _save_journal(folder, journal)
        return {"id": identifier, "state": "complete", "snapshot_id": created["id"],
                "changed": order, "store": str(store),
                "mode_projection": "Windows file attributes" if os.name == "nt" else "POSIX permission bits"}


def inspect_transaction(root: Path, store: Path, identifier: str) -> dict:
    root, store = _roots(root, store)
    plan, journal, _ = _receipt(root, store, identifier)
    return {"id": identifier, "state": journal["state"], "snapshot_id": plan["snapshot_id"],
            "files": journal["files"], "store": str(store)}


def recover_transaction(root: Path, store: Path, identifier: str) -> dict:
    root, store = _roots(root, store)
    plan, journal, folder = _receipt(root, store, identifier)
    with _lock(root, store):
        snapshots = safe_path(store, "snapshots")
        result_path = plan["snapshot_id"] + "/result.json"
        expected = {}
        for relative, entry in plan["files"].items():
            current = file_state(root, relative)
            if _same(current, entry["before"]):
                expected[relative] = entry["before"]
            elif journal["files"][relative] != "pending" and _same(current, entry["after"]):
                expected[relative] = entry["after"]
            else:
                raise ValueError(f"Recovery conflict; current bytes preserved: {relative}")
        if native_io_path(safe_path(snapshots, result_path)).exists():
            result, _ = _json(snapshots, result_path)
            if native_io_path(safe_path(folder, "recovery-binding.json")).exists():
                binding, _ = _json(folder, "recovery-binding.json")
                if binding != {"plan_digest": journal["plan_digest"], "expected": result.get("expected")}:
                    raise ValueError("Recovery result does not match the retained binding.")
            elif not _same(result.get("expected"), {path: entry["after"] for path, entry in plan["files"].items()}):
                raise ValueError("Result does not match the planned publication.")
        else:
            binding = {"plan_digest": journal["plan_digest"], "expected": expected}
            if native_io_path(safe_path(folder, "recovery-binding.json")).exists():
                prior, _ = _json(folder, "recovery-binding.json")
                if not _same(prior, binding):
                    raise ValueError("Recovery binding changed; preserve current files.")
            else:
                atomic_write(folder, "recovery-binding.json", json_bytes(binding))
            snapshot.bind_result(root, snapshots, plan["snapshot_id"], expected)
        if journal["state"] != "recovered":
            journal["state"] = "recovering"
            _save_journal(folder, journal)
        result = snapshot.restore_snapshot(root, snapshots, plan["snapshot_id"])
        journal["state"] = "recovered"
        _save_journal(folder, journal)
        return {"id": identifier, "state": "recovered", "snapshot_id": plan["snapshot_id"],
                "changed": result["changed"], "store": str(store)}
