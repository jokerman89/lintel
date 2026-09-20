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


def _inside(root: Path, path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError("Result path escapes the working repository") from error
    return resolved


def scope_snapshot(root: Path, scopes: Sequence[str]) -> dict[str, str]:
    root = root.resolve()
    files: dict[str, str] = {}
    for scope in scopes:
        path = _inside(root, root / scope)
        candidates = [path] if path.is_file() else path.rglob("*") if path.is_dir() else []
        for candidate in candidates:
            resolved = _inside(root, candidate)
            if candidate.is_symlink() and candidate.is_dir():
                raise ValueError("Nested directory aliases need explicit real-path scopes for result capture")
            if resolved.is_file():
                files[resolved.relative_to(root).as_posix()] = bytes_digest(resolved.read_bytes())
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


def _git_scope_snapshot(root: Path, head: str, scopes: Sequence[str]) -> dict[str, str]:
    scope_parts = [
        tuple(os.path.normcase(part) for part in _inside(root, root / scope).relative_to(root).parts)
        for scope in scopes
    ]
    files: dict[str, str] = {}
    for item in _git(root, "ls-tree", "-r", "-z", "--full-tree", head).split(b"\0"):
        if not item:
            continue
        metadata, name = item.split(b"\t", 1)
        path = name.decode("utf-8")
        parts = tuple(os.path.normcase(part) for part in Path(path).parts)
        if not any(parts[:len(scope)] == scope for scope in scope_parts):
            continue
        mode, kind, object_id = metadata.split()
        if kind != b"blob" or mode not in (b"100644", b"100755"):
            raise ValueError("Git result snapshots require regular files, not links or submodules")
        files[path] = bytes_digest(_git(root, "cat-file", "blob", object_id.decode("ascii")))
    return dict(sorted(files.items()))


def _git_working_snapshot(root: Path, scopes: Sequence[str]) -> dict[str, str]:
    scope_parts = [
        tuple(os.path.normcase(part) for part in _inside(root, root / scope).relative_to(root).parts)
        for scope in scopes
    ]
    files: dict[str, str] = {}
    names = _git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0")
    for name in names:
        if not name:
            continue
        path = name.decode("utf-8")
        parts = tuple(os.path.normcase(part) for part in Path(path).parts)
        if not any(parts[:len(scope)] == scope for scope in scope_parts):
            continue
        resolved = _inside(root, root / path)
        if resolved.is_file():
            files[path] = bytes_digest(resolved.read_bytes())
    return dict(sorted(files.items()))


def capture_result(
    root: Path, scopes: Sequence[str], *, base: Optional[str] = None, head: Optional[str] = None,
) -> dict[str, Any]:
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
