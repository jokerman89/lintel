#!/usr/bin/env python3
# component: owned-file-snapshot
# implements: ADR-0005, ADR-0010
# intent: .claude/plans/universal-implementation/packages/P03.md
# constraints: explicit owned files, quiescent root, no network or whole-tree replacement
# last_intent_review: 2026-09-20
"""Verified file snapshots and attributable, resumable restore; not a live-system rollback."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Sequence
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from context_safety import (atomic_write, checked_root, file_state, is_link, json_bytes, path_key,
                            read_owned, relative_path, safe_path, selector_path)

SCHEMA = 1
ID_PATTERN = r"snapshot-[0-9a-f]{32}"
MAX_BYTES = 128 * 1024 * 1024


def _locations(root: Path, store: Path) -> tuple[Path, Path]:
    if is_link(Path(root)) or is_link(Path(store)):
        raise ValueError("Snapshot roots cannot be links or reparse points.")
    root, store = checked_root(root), checked_root(store)
    if root.is_relative_to(store) or store.is_relative_to(root):
        raise ValueError("Source and snapshot store must be separate, non-overlapping directories.")
    return root, store


def _folder(store: Path, identifier: str) -> Path:
    if not re.fullmatch(ID_PATTERN, identifier):
        raise ValueError("Unsupported snapshot ID/legacy format; retain it for explicit manual recovery.")
    folder = safe_path(store, identifier)
    if not folder.is_dir():
        raise ValueError(f"Snapshot does not exist: {identifier}")
    return folder


def _state(value) -> dict | None:
    if value is None:
        return None
    if (not isinstance(value, dict) or set(value) != {"sha256", "size", "mode"}
            or not isinstance(value["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", value["sha256"])
            or type(value["size"]) is not int or not 0 <= value["size"] <= MAX_BYTES
            or type(value["mode"]) is not int or not 0 <= value["mode"] <= 0o777):
        raise ValueError("Invalid file-state digest/size/mode.")
    return value


def _entry_state(entry: dict) -> dict | None:
    if entry["sha256"] is None:
        if entry["size"] != 0 or entry["mode"] is not None:
            raise ValueError("Invalid originally-absent file state.")
        return None
    return _state({key: entry[key] for key in ("sha256", "size", "mode")})


def _timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("Invalid snapshot timestamp.")
    moment = datetime.fromisoformat(value)
    if moment.tzinfo is None:
        raise ValueError("Snapshot timestamp needs an explicit timezone.")
    return moment


def _manifest_bytes(folder: Path) -> bytes:
    return read_owned(folder, "manifest.json", 2 * 1024 * 1024)[0]


def load_snapshot(root: Path, store: Path, identifier: str) -> dict:
    root, store = _locations(root, store)
    folder = _folder(store, identifier)
    manifest = json.loads(_manifest_bytes(folder))
    if (not isinstance(manifest, dict) or type(manifest.get("schema_version")) is not int
            or manifest.get("schema_version") != SCHEMA or manifest.get("state") != "complete"
            or manifest.get("owner") != str(root) or manifest.get("id") != identifier):
        raise ValueError("Snapshot is incomplete, unsupported or belongs to a different root.")
    _timestamp(manifest.get("created_at"))
    files = manifest.get("files")
    if not isinstance(files, list) or not 1 <= len(files) <= 5000:
        raise ValueError("Invalid snapshot file inventory.")
    seen, total = set(), 0
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "size", "mode"}:
            raise ValueError("Invalid snapshot file entry.")
        relative = entry["path"]
        if not isinstance(relative, str):
            raise ValueError("Snapshot paths must be strings.")
        relative_path(relative)
        if path_key(relative) in seen or ".git" in relative.casefold().split("/"):
            raise ValueError("Duplicate/aliased or Git-internal snapshot path refused.")
        seen.add(path_key(relative))
        safe_path(root, relative)
        state = _entry_state(entry)
        if state is not None:
            data, copied = read_owned(folder, "blobs/" + state["sha256"], MAX_BYTES)
            if copied["sha256"] != state["sha256"] or len(data) != state["size"]:
                raise ValueError(f"Snapshot blob failed verification: {relative}")
            total += len(data)
            if total > MAX_BYTES:
                raise ValueError("Snapshot exceeds its aggregate byte bound.")
    return manifest


@contextmanager
def _operation_lock(folder: Path):
    lock = safe_path(folder, ".operation-lock")
    try:
        lock.mkdir()
    except FileExistsError as error:
        raise ValueError("Snapshot is locked. Verify no operation is running before recovering a stale lock.") from error
    try:
        yield
    finally:
        lock.rmdir()


def create_snapshot(root: Path, store: Path, paths: Sequence[str], absent: Sequence[str] = ()) -> dict:
    root, store = _locations(root, store)
    existing = [selector_path(p) for p in paths]
    absent = [selector_path(p) for p in absent]
    names = existing + absent
    if not 1 <= len(names) <= 5000 or len({path_key(p) for p in names}) != len(names):
        raise ValueError("Choose 1-5000 unique, explicitly owned file paths.")
    if any(".git" in p.casefold().split("/") for p in names):
        raise ValueError("Git-internal paths are not owned snapshot content.")
    identifier = "snapshot-" + uuid.uuid4().hex
    pending = safe_path(store, ".pending-" + identifier)
    pending.mkdir(mode=0o700)
    files, total = [], 0
    for relative in sorted(names):
        if relative in absent:
            if file_state(root, relative) is not None:
                raise ValueError(f"Expected an absent owned path: {relative}; partial copy retained at {pending}")
            files.append({"path": relative, "sha256": None, "size": 0, "mode": None})
            continue
        data, state = read_owned(root, relative, MAX_BYTES)
        _state(state)
        total += len(data)
        if total > MAX_BYTES:
            raise ValueError(f"Snapshot byte bound exceeded; partial copy retained at {pending}")
        blob = "blobs/" + state["sha256"]
        if not safe_path(pending, blob).exists():
            atomic_write(pending, blob, data)
        copied, _ = read_owned(pending, blob, MAX_BYTES)
        if copied != data:
            raise ValueError(f"Snapshot copy verification failed: {relative}")
        files.append({"path": relative, **state})
    for entry in files:
        if file_state(root, entry["path"]) != _entry_state(entry):
            raise ValueError(f"Source changed during snapshot: {entry['path']}; partial copy retained at {pending}")
    manifest = {"schema_version": SCHEMA, "id": identifier, "owner": str(root), "state": "complete",
                "created_at": datetime.now(timezone.utc).isoformat(), "files": files}
    atomic_write(pending, "manifest.json", json_bytes(manifest))
    pending.rename(safe_path(store, identifier))
    load_snapshot(root, store, identifier)
    return {"id": identifier, "path": str(store / identifier), "state": "complete",
            "files": len(files), "bytes": total}


def _identity(folder: Path) -> str:
    return hashlib.sha256(_manifest_bytes(folder)).hexdigest()


def _read_result(folder: Path, manifest: dict) -> dict | None:
    if not safe_path(folder, "result.json").exists():
        return None
    result = json.loads(read_owned(folder, "result.json", 2 * 1024 * 1024)[0])
    if (not isinstance(result, dict) or type(result.get("schema_version")) is not int
            or result.get("schema_version") != SCHEMA
            or result.get("snapshot_digest") != _identity(folder)
            or result.get("id") != manifest["id"]):
        raise ValueError("Result receipt does not match the verified snapshot.")
    expected = result.get("expected")
    if not isinstance(expected, dict) or set(expected) != {f["path"] for f in manifest["files"]}:
        raise ValueError("Result receipt must cover exactly the snapshot's owned paths.")
    for value in expected.values():
        _state(value)
    return result


def bind_result(root: Path, store: Path, identifier: str, expected: dict) -> dict:
    """Bind caller-recorded post-images; never adopt arbitrary current bytes as owned."""
    root, store = _locations(root, store)
    folder = _folder(store, identifier)
    with _operation_lock(folder):
        manifest = load_snapshot(root, store, identifier)
        if safe_path(folder, "result.json").exists() or safe_path(folder, "restore.json").exists():
            raise ValueError("Result already bound/recovery started; refusing to reauthorize changed files.")
        if not isinstance(expected, dict) or set(expected) != {f["path"] for f in manifest["files"]}:
            raise ValueError("Expected states must cover exactly the snapshot's owned paths.")
        for relative, state in expected.items():
            _state(state)
            if file_state(root, relative) != state:
                raise ValueError(f"Current file does not match the attributable result: {relative}")
        result = {"schema_version": SCHEMA, "id": identifier, "snapshot_digest": _identity(folder),
                  "expected": expected}
        atomic_write(folder, "result.json", json_bytes(result))
        return result


def _apply_restore(root: Path, folder: Path, entry: dict, expected: dict | None) -> None:
    relative = entry["path"]
    if file_state(root, relative) != expected:
        raise ValueError(f"File changed after restore preflight: {relative}")
    original = _entry_state(entry)
    if original is None:
        safe_path(root, relative).unlink()
    else:
        data, copied = read_owned(folder, "blobs/" + original["sha256"], MAX_BYTES)
        if copied["sha256"] != original["sha256"] or copied["size"] != original["size"]:
            raise ValueError(f"Snapshot changed during restore: {relative}")
        atomic_write(root, relative, data, original["mode"], expected=expected, check_expected=True)
    if file_state(root, relative) != original:
        raise ValueError(f"Restored file failed verification: {relative}")


def restore_snapshot(root: Path, store: Path, identifier: str) -> dict:
    root, store = _locations(root, store)
    folder = _folder(store, identifier)
    with _operation_lock(folder):
        manifest = load_snapshot(root, store, identifier)
        receipt = _read_result(folder, manifest)
        digest = _identity(folder)
        journal = None
        if safe_path(folder, "restore.json").exists():
            journal = json.loads(read_owned(folder, "restore.json", 2 * 1024 * 1024)[0])
            if (not isinstance(journal, dict) or type(journal.get("schema_version")) is not int
                    or journal.get("schema_version") != SCHEMA or journal.get("snapshot_digest") != digest
                    or journal.get("state") not in ("in-progress", "complete")
                    or journal.get("result_digest") != hashlib.sha256(json_bytes(receipt)).hexdigest()):
                raise ValueError("Stale or invalid restore journal.")
        changes = []
        for entry in manifest["files"]:
            current = file_state(root, entry["path"])
            original = _entry_state(entry)
            if current == original:
                continue
            if journal and journal["state"] == "complete":
                raise ValueError(f"Snapshot was already restored; later changes are not owned: {entry['path']}")
            if receipt is None or current != receipt["expected"][entry["path"]]:
                raise ValueError(f"Restore conflict; current bytes preserved: {entry['path']}")
            changes.append((entry, current))
        journal = {"schema_version": SCHEMA, "snapshot_digest": digest,
                   "result_digest": hashlib.sha256(json_bytes(receipt)).hexdigest(),
                   "state": "in-progress"}
        atomic_write(folder, "restore.json", json_bytes(journal))
        for entry, expected in changes:
            _apply_restore(root, folder, entry, expected)
        # Recheck the entire owned set before reporting completion.
        for entry in manifest["files"]:
            if file_state(root, entry["path"]) != _entry_state(entry):
                raise ValueError(f"Owned set changed before restore completion: {entry['path']}")
        journal["state"] = "complete"
        atomic_write(folder, "restore.json", json_bytes(journal))
        return {"id": identifier, "state": "complete", "changed": [e["path"] for e, _ in changes]}


def retention_plan(root: Path, store: Path, *, keep: int = 5, days: int = 30,
                   now: datetime | None = None) -> dict:
    root, store = _locations(root, store)
    if type(keep) is not int or keep < 1 or type(days) is not int or days < 1:
        raise ValueError("Retention must keep at least one snapshot and one recent day.")
    now = now or datetime.now(timezone.utc)
    snapshots, protected, unsupported = [], set(), []
    for folder in sorted(store.iterdir()):
        if not re.fullmatch(ID_PATTERN, folder.name):
            unsupported.append(folder.name)
            continue
        manifest = load_snapshot(root, store, folder.name)
        snapshots.append((_timestamp(manifest["created_at"]), folder.name))
        if safe_path(folder, ".operation-lock").exists():
            protected.add(folder.name)
        if safe_path(folder, "restore.json").exists():
            journal = json.loads(read_owned(folder, "restore.json", 2 * 1024 * 1024)[0])
            if journal.get("state") != "complete":
                protected.add(folder.name)
    snapshots.sort(reverse=True)
    protected.update(name for _, name in snapshots[:keep])
    protected.update(name for moment, name in snapshots if moment >= now - timedelta(days=days))
    return {"keep": [name for _, name in snapshots if name in protected],
            "eligible": [name for _, name in snapshots if name not in protected],
            "unsupported_preserved": unsupported}


def prune_snapshots(root: Path, store: Path, identifiers: Sequence[str], *,
                    now: datetime | None = None) -> dict:
    root, store = _locations(root, store)
    eligible = retention_plan(root, store, now=now)["eligible"]
    if not identifiers or len(set(identifiers)) != len(identifiers) or not set(identifiers) <= set(eligible):
        raise ValueError("Prune only explicitly selected eligible snapshots; protected copies stay.")
    inventories = []
    for identifier in identifiers:
        manifest = load_snapshot(root, store, identifier)
        folder = _folder(store, identifier)
        expected = {"manifest.json"}
        expected.update("blobs/" + e["sha256"] for e in manifest["files"] if e["sha256"])
        for optional in ("result.json", "restore.json"):
            if safe_path(folder, optional).exists():
                expected.add(optional)
        actual = set()
        for path in folder.rglob("*"):
            safe_path(folder, path.relative_to(folder).as_posix())
            if path.is_file():
                actual.add(path.relative_to(folder).as_posix())
            elif path != folder / "blobs":
                raise ValueError("Unexpected snapshot directory; refusing pruning.")
        if actual != expected:
            raise ValueError("Unexpected/unowned snapshot content; refusing pruning.")
        inventories.append((folder, expected))
    for folder, files in inventories:
        with _operation_lock(folder):
            for relative in sorted(files):
                safe_path(folder, relative).unlink()
            blobs = safe_path(folder, "blobs")
            if blobs.exists():
                blobs.rmdir()
        folder.rmdir()
    return {"pruned": identifiers}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Explicit authorized source/restore root.")
    parser.add_argument("--store", type=Path, required=True, help="Existing separate snapshot directory.")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("--path", action="append", default=[])
    create.add_argument("--absent", action="append", default=[])
    for name in ("verify", "restore", "bind"):
        command = commands.add_parser(name)
        command.add_argument("id")
        if name == "bind":
            command.add_argument("--expected", type=Path, required=True,
                                 help="JSON object of owned post-image states recorded by the operation.")
    commands.add_parser("list")
    prune = commands.add_parser("prune")
    prune.add_argument("ids", nargs="+", help="Exact eligible IDs from list, explicitly authorized for deletion.")
    args = parser.parse_args()
    try:
        if args.command == "create":
            result = create_snapshot(args.root, args.store, args.path, args.absent)
        elif args.command == "verify":
            result = load_snapshot(args.root, args.store, args.id)
        elif args.command == "bind":
            expected_root = checked_root(args.expected.absolute().parent)
            expected = json.loads(read_owned(expected_root, args.expected.name, 2 * 1024 * 1024)[0])
            result = bind_result(args.root, args.store, args.id, expected)
        elif args.command == "restore":
            result = restore_snapshot(args.root, args.store, args.id)
        elif args.command == "list":
            result = retention_plan(args.root, args.store)
        else:
            result = prune_snapshots(args.root, args.store, args.ids)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"li-snapshot: {error}. Preserve the source and any pending/journal artifacts.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
