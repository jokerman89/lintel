#!/usr/bin/env python3
# component: swarm-result-snapshot
# implements: ADR-0026, ADR-0027
# intent: .claude/plans/universal-implementation/packages/P04.md
# constraints: read-only local files and Git objects; no artifact execution or network
# last_intent_review: 2026-09-20
"""Observable local result identities, pending the shared A22.7 evidence binding."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
from typing import Any, Mapping, Optional, Sequence


def content_bytes(data: bytes) -> bytes:
    if b"\0" not in data:
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            return data
        return data.replace(b"\r\n", b"\n")
    return data


def bytes_digest(data: bytes) -> str:
    return hashlib.sha256(content_bytes(data)).hexdigest()


def value_digest(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _inside(root: Path, path: Path, *, allow_leaf_link: bool = False) -> Path:
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise ValueError("Result path escapes the working repository") from error
    if ".." in relative.parts:
        raise ValueError("Result path escapes the working repository")
    current = root
    for index, part in enumerate(relative.parts):
        current /= part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            break
        if stat.S_ISLNK(metadata.st_mode):
            if allow_leaf_link and index == len(relative.parts) - 1:
                return current
            raise ValueError("Result paths may not traverse symbolic-link directories")
        if (
            getattr(metadata, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        ):
            raise ValueError("Result snapshots do not support reparse points other than explicit symbolic links")
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError("Result path escapes the working repository") from error
    return resolved


def _link_record(root: Path, path: Path, target: bytes) -> dict[str, str]:
    try:
        text = target.decode("utf-8")
        if not text or "\0" in text:
            raise ValueError
        (path.parent / text).resolve().relative_to(root)
    except (UnicodeError, OSError, RuntimeError, ValueError) as error:
        raise ValueError("Symbolic-link target must be UTF-8 data resolving within the working repository") from error
    return {"type": "symlink", "mode": "120000", "digest": hashlib.sha256(target).hexdigest(), "target": text}


def _file_record(
    root: Path, path: Path, *, index_mode: Optional[str] = None, filemode: bool = True, symlinks: bool = True,
) -> dict[str, str]:
    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode):
        if index_mode not in (None, "120000"):
            raise ValueError("Current scoped file type differs from its Git index type")
        return _link_record(root, path, os.readlink(path).encode("utf-8"))
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError("Result snapshots do not support submodules or special files")
    if index_mode == "120000":
        if symlinks:
            raise ValueError("Current regular file replaces an expected Git symbolic link")
        # core.symlinks=false materializes the exact Git link target as a file.
        return _link_record(root, path, path.read_bytes())
    observed_mode = "100755" if metadata.st_mode & stat.S_IXUSR else "100644"
    # On Windows and other core.filemode=false worktrees, Git's index carries
    # the executable bit which the filesystem cannot reliably represent.
    mode = observed_mode if filemode else index_mode or "100644"
    if index_mode is not None and mode != index_mode:
        raise ValueError("Current scoped file mode differs from its Git index mode")
    return {"type": "file", "mode": mode, "digest": bytes_digest(path.read_bytes())}


def scope_snapshot(root: Path, scopes: Sequence[str]) -> dict[str, dict[str, str]]:
    root = root.resolve()
    files: dict[str, dict[str, str]] = {}
    for scope in scopes:
        path = _inside(root, root / scope, allow_leaf_link=True)
        candidates = [path] if path.is_symlink() or path.is_file() else path.rglob("*") if path.is_dir() else []
        for candidate in candidates:
            resolved = _inside(root, candidate, allow_leaf_link=True)
            if resolved.is_symlink() or not resolved.is_dir():
                files[resolved.relative_to(root).as_posix()] = _file_record(root, resolved)
    return dict(sorted(files.items()))


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), "--no-pager", *args],
        capture_output=True, check=False,
    )
    if result.returncode:
        raise ValueError(f"Local Git evidence command failed: {args[0]}")
    return result.stdout


def commit_id(root: Path, revision: str) -> str:
    if not isinstance(revision, str) or not revision or revision.startswith("-"):
        raise ValueError("A nonempty local Git commit reference is required")
    return _git(root, "rev-parse", "--verify", "--end-of-options", revision + "^{commit}").decode("ascii").strip()


def git_changed_paths(root: Path, base: str, head: str) -> list[str]:
    base_id, head_id = commit_id(root, base), commit_id(root, head)
    _git(root, "merge-base", "--is-ancestor", base_id, head_id)
    output = _git(root, "diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--name-only", "-z", base_id, head_id, "--")
    return sorted(path.decode("utf-8") for path in output.split(b"\0") if path)


def _git_scope_snapshot(root: Path, head: str, scopes: Sequence[str]) -> dict[str, dict[str, str]]:
    scope_parts = [
        tuple(os.path.normcase(part) for part in _inside(root, root / scope, allow_leaf_link=True).relative_to(root).parts)
        for scope in scopes
    ]
    files: dict[str, dict[str, str]] = {}
    for item in _git(root, "ls-tree", "-r", "-z", "--full-tree", head).split(b"\0"):
        if not item:
            continue
        metadata, name = item.split(b"\t", 1)
        path = name.decode("utf-8")
        parts = tuple(os.path.normcase(part) for part in Path(path).parts)
        if not any(parts[:len(scope)] == scope for scope in scope_parts):
            continue
        mode, kind, object_id = metadata.split()
        if kind != b"blob" or mode not in (b"100644", b"100755", b"120000"):
            raise ValueError("Git result snapshots support regular files and symbolic links, not submodules")
        data = _git(root, "cat-file", "blob", object_id.decode("ascii"))
        if mode == b"120000":
            files[path] = _link_record(root, root / path, data)
            continue
        files[path] = {
            "type": "file", "mode": mode.decode("ascii"),
            "digest": bytes_digest(data),
        }
    return dict(sorted(files.items()))


def _git_working_snapshot(root: Path, scopes: Sequence[str]) -> dict[str, dict[str, str]]:
    scope_parts = [
        tuple(os.path.normcase(part) for part in _inside(root, root / scope, allow_leaf_link=True).relative_to(root).parts)
        for scope in scopes
    ]
    files: dict[str, dict[str, str]] = {}
    entries: dict[str, list[tuple[str, str]]] = {}
    for entry in _git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if entry:
            metadata, name = entry.split(b"\t", 1)
            mode, _, stage = metadata.decode("ascii").split()
            entries.setdefault(name.decode("utf-8"), []).append((mode, stage))
    untracked = [
        name.decode("utf-8") for name in
        _git(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if name
    ]
    filemode = _git(root, "config", "--type=bool", "--default=true", "--get", "core.filemode").strip() == b"true"
    symlinks = _git(root, "config", "--type=bool", "--default=true", "--get", "core.symlinks").strip() == b"true"
    for path in dict.fromkeys([*entries, *untracked]):
        parts = tuple(os.path.normcase(part) for part in Path(path).parts)
        if not any(parts[:len(scope)] == scope for scope in scope_parts):
            continue
        index_entries = entries.get(path, [])
        if index_entries and (
            len(index_entries) != 1 or index_entries[0][1] != "0" or index_entries[0][0] not in ("100644", "100755", "120000")
        ):
            raise ValueError("Current scoped Git index must contain resolved file/link entries, not submodules")
        resolved = _inside(root, root / path, allow_leaf_link=True)
        try:
            files[path] = _file_record(
                root, resolved, index_mode=index_entries[0][0] if index_entries else None,
                filemode=filemode, symlinks=symlinks,
            )
        except FileNotFoundError:
            continue
    return dict(sorted(files.items()))


def capture_result(
    root: Path, scopes: Sequence[str], *, base: Optional[str] = None, head: Optional[str] = None,
) -> dict[str, Any]:
    root = root.resolve()
    if base is None and head is None:
        return {"kind": "files", "base": None, "head": None, "files": scope_snapshot(root, scopes)}
    if base is None or head is None:
        raise ValueError("Both base and head are required for a Git result snapshot")
    base_id, head_id = commit_id(root, base), commit_id(root, head)
    files = _git_working_snapshot(root, scopes)
    changes = git_changed_paths(root, base_id, head_id)
    if _git_scope_snapshot(root, head_id, scopes) != files:
        raise ValueError("Current scoped files differ from the declared Git result")
    return {"kind": "git", "base": base_id, "head": head_id, "files": files, "changes": changes}


def verify_result(root: Path, scopes: Sequence[str], result: Mapping[str, Any]) -> None:
    if result.get("kind") not in ("files", "git"):
        raise ValueError("Unknown result snapshot kind")
    if result.get("kind") == "files" and (result.get("base") is not None or result.get("head") is not None):
        raise ValueError("File snapshots cannot claim Git base/head evidence")
    if result.get("kind") == "git" and (
        not isinstance(result.get("base"), str) or not isinstance(result.get("head"), str)
    ):
        raise ValueError("Git snapshots must identify both base and head")
    observed = capture_result(root, scopes, base=result.get("base"), head=result.get("head"))
    if dict(result) != observed:
        raise ValueError("Result snapshot no longer matches the observable scoped files or Git change set")
