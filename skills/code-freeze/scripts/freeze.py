#!/usr/bin/env python3
# component: advisory-freeze-state
# implements: ADR-0005, ADR-0028, ADR-0031
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: repository-owned advisory metadata; no permission or policy changes
# last_intent_review: 2026-09-25
"""Read and conditionally update advisory freeze state; shared by the skill and hook."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import TypedDict

SOURCE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SOURCE / "lib"))
from context_safety import (  # noqa: E402
    atomic_write, checked_root, is_link, native_io_path, read_owned, safe_path,
    select_files, selector_path,
)


class FreezeState(TypedDict):
    advisory: bool
    frozen: list[dict[str, str]]


FIELDS = {"path", "reason", "added_at", "expires"}
MAX_BYTES = 65536


def scalar(text: str) -> str:
    text = text.strip()
    if text.startswith('"'):
        value = json.loads(text)
        if not isinstance(value, str):
            raise ValueError("Freeze fields must be strings.")
        return value
    if text.startswith("'"):
        if len(text) < 2 or not text.endswith("'") or "'" in text[1:-1].replace("''", ""):
            raise ValueError("Invalid quoted freeze field.")
        return text[1:-1].replace("''", "'")
    if not text or text.startswith(("[", "{", "&", "*", "!", "|", ">", "@", "`")):
        raise ValueError("Unsupported freeze scalar; preserve and inspect the state file.")
    return text.split(" #", 1)[0].rstrip()


def decode_state(text: str) -> FreezeState:
    """Accept the existing flat YAML record, without evaluating general YAML."""
    advisory_seen = frozen_seen = False
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    empty = False
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line == "---" and not advisory_seen and not frozen_seen:
            continue
        if line == "advisory: true" and not advisory_seen and not frozen_seen:
            advisory_seen = True
            continue
        if line in ("frozen:", "frozen: []") and not frozen_seen:
            frozen_seen = True
            empty = line.endswith("[]")
            continue
        match = re.fullmatch(r"  - (path):\s*(.*)", line)
        if match and frozen_seen and not empty:
            current = {"path": scalar(match[2])}
            entries.append(current)
            continue
        match = re.fullmatch(r"    ([a-z_]+):\s*(.*)", line)
        if match and current is not None and match[1] in FIELDS and match[1] not in current:
            current[match[1]] = scalar(match[2])
            continue
        raise ValueError(f"Unknown or malformed freeze state at line {number}; nothing replaced.")
    if not frozen_seen or (not empty and not entries):
        raise ValueError("Freeze state needs an explicit frozen list; scope is unknown.")
    return {"advisory": True, "frozen": entries}


def encode_state(state: FreezeState) -> bytes:
    lines = ["advisory: true", "frozen:" if state["frozen"] else "frozen: []"]
    for entry in state["frozen"]:
        lines.append("  - path: " + json.dumps(entry["path"], ensure_ascii=False))
        for key in ("reason", "added_at", "expires"):
            if key in entry:
                lines.append(f"    {key}: " + json.dumps(entry[key], ensure_ascii=False))
    data = ("\n".join(lines) + "\n").encode("utf-8")
    if len(data) > MAX_BYTES:
        raise ValueError("Freeze state exceeds its 64KiB bound; narrow the scope.")
    return data


def relative_scope(root: Path, value: str) -> str:
    relative = selector_path(value.rstrip("/\\"))
    safe_path(root, relative)
    return relative


def scope_matches(root: Path, prefix: str, target: str) -> bool:
    if target == prefix or target.startswith(prefix + "/"):
        return True
    frozen = native_io_path(safe_path(root, prefix))
    if not frozen.exists():
        return False
    candidate = safe_path(root, target)
    for path in (candidate, *candidate.parents):
        if path == root:
            break
        actual = native_io_path(path)
        if actual.exists() and frozen.samefile(actual):
            return True
    return False


def read_state(root: Path, relative: str) -> tuple[FreezeState, dict | None]:
    try:
        data, expected = read_owned(root, relative, MAX_BYTES)
    except FileNotFoundError:
        return {"advisory": True, "frozen": []}, None
    state = decode_state(data.decode("utf-8-sig"))
    seen = set()
    for entry in state["frozen"]:
        path = relative_scope(root, entry["path"])
        if path in seen or any(char in path for char in "*?["):
            raise ValueError("Duplicate or unexpanded freeze path; inspect before changing state.")
        seen.add(path)
    return state, expected


def record_audit(root: Path, action: str, paths: list[str], reason: str) -> None:
    bash = shutil.which("bash")
    if not bash:
        print("WARN [lintel/freeze]: state persisted; Bash audit writer unavailable.", file=sys.stderr)
        return
    environment = dict(os.environ, LINTEL_REPO_ROOT=root.as_posix())
    for path in paths:
        try:
            observed = subprocess.run(
                [bash, "--noprofile", "--norc", "-c",
                 'source "$1" || exit; shift; audit_log "$@"', "freeze-audit",
                 (SOURCE / "bin/_audit.sh").as_posix(), "code-freeze", action,
                 "path=" + path, "reason=" + reason],
                env=environment, capture_output=True, text=True, encoding="utf-8", check=False,
            )
        except OSError as error:
            print(f"WARN [lintel/freeze]: state persisted; audit process unavailable: {error}",
                  file=sys.stderr)
            continue
        if observed.stderr:
            print(observed.stderr.rstrip(), file=sys.stderr)
        if observed.returncode:
            print(f"WARN [lintel/freeze]: audit writer exited {observed.returncode}; state persisted.",
                  file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--state-dir", required=True, type=Path)
    parser.add_argument("--session", required=True)
    parser.add_argument("--legacy-file", type=Path)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--list", action="store_true")
    modes.add_argument("--lift", action="store_true")
    modes.add_argument("--check", metavar="TARGET", help="read-only hook match; prints matching paths")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--reason")
    parser.add_argument("--until")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()
    try:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.session):
            raise ValueError("Select a stable session/cycle ID, not a path or guessed default.")
        if args.all and not args.lift:
            raise ValueError("--all requires --lift.")
        if (args.list or args.check is not None) and (
            args.paths or args.reason is not None or args.until is not None
        ):
            raise ValueError("Read-only freeze modes do not accept mutation operands.")
        if args.lift and (args.until is not None or (args.all and args.paths)):
            raise ValueError("Use --lift with exact paths or --all, without expiry changes.")
        if args.until is not None and not args.until.strip():
            raise ValueError("Supply a nonempty expiry intent; no timer is installed.")
        if not (args.list or args.check is not None or args.paths or args.all):
            raise ValueError("Supply paths, --list, --lift paths or --lift --all.")
        root = checked_root(args.repo)
        state_dir = args.state_dir if args.state_dir.is_absolute() else root / args.state_dir
        relative = (state_dir / "code-freeze" / (args.session + ".yaml")).relative_to(root).as_posix()
        state, expected = read_state(root, relative)
        state_file = safe_path(root, relative)
        legacy = False
        if expected is None and args.legacy_file is not None:
            legacy_root = args.legacy_file.parent
            if any(is_link(path) for path in (legacy_root, *legacy_root.parents)):
                raise ValueError("Linked legacy freeze directory refused; scope is unknown.")
            if native_io_path(legacy_root).exists():
                legacy_root = checked_root(legacy_root)
                old, old_expected = read_state(legacy_root, args.legacy_file.name)
                if old_expected is not None:
                    state, state_file, legacy = old, args.legacy_file, True
                    for entry in state["frozen"]:
                        relative_scope(root, entry["path"])
        if args.check is not None:
            target = Path(args.check)
            value = target.relative_to(root).as_posix() if target.is_absolute() else args.check
            target_relative = relative_scope(root, value)
            for entry in state["frozen"]:
                prefix = relative_scope(root, entry["path"])
                if scope_matches(root, prefix, target_relative):
                    print(entry["path"])
            return 0
        if legacy and not args.list:
            raise ValueError(f"Legacy freeze is read-only: {state_file}; explicitly reconcile it before a repository-state mutation.")
        changed: list[str] = []
        missing: list[str] = []
        prospective: list[str] = []
        if not args.list:
            selected = []
            for value in args.paths:
                path = relative_scope(root, value)
                if any(char in path for char in "*?["):
                    if args.lift:
                        raise ValueError("--lift requires exact recorded paths, not globs.")
                    manifest = select_files(root, patterns=[path])
                    if manifest["status"] != "selected":
                        raise ValueError(f"Freeze glob has no complete selection: {value}")
                    selected.extend(item["path"] for item in manifest["files"])
                else:
                    selected.append(path)
            selected = list(dict.fromkeys(selected))
            if args.lift:
                removed = {relative_scope(root, entry["path"]) for entry in state["frozen"]
                           if args.all or relative_scope(root, entry["path"]) in selected}
                missing = [path for path in selected if path not in removed]
                changed = [entry["path"] for entry in state["frozen"]
                           if relative_scope(root, entry["path"]) in removed]
                state["frozen"] = [entry for entry in state["frozen"]
                                   if relative_scope(root, entry["path"]) not in removed]
            else:
                for path in selected:
                    entry = next((entry for entry in state["frozen"]
                                  if relative_scope(root, entry["path"]) == path), None)
                    if not native_io_path(safe_path(root, path)).exists():
                        prospective.append(path)
                    if entry is None:
                        entry = {"path": path, "added_at": datetime.now(timezone.utc).isoformat(),
                                 "reason": args.reason or "", "expires": args.until or "session"}
                        state["frozen"].append(entry)
                        changed.append(path)
                    else:
                        before = dict(entry)
                        if args.reason is not None:
                            entry["reason"] = args.reason
                        if args.until is not None:
                            entry["expires"] = args.until
                        if entry != before:
                            changed.append(entry["path"])
            if changed:
                encoded = encode_state(state)
                atomic_write(root, relative, encoded, expected=expected, check_expected=True)
                actual, _ = read_owned(root, relative, MAX_BYTES)
                if actual != encoded:
                    raise ValueError("Freeze read-back differs; persistence is unverified.")
                record_audit(root, "unfreeze" if args.lift else "freeze", changed, args.reason or "")
        print(json.dumps({"advisory": True, "state_file": str(state_file),
                          "source": "legacy-read-only" if legacy else "repository",
                          "frozen": state["frozen"], "changed": changed,
                          "not_frozen": missing, "prospective": prospective,
                          "host_enforcement": "not established"}, indent=2, ensure_ascii=True))
        return 0
    except (OSError, ValueError) as error:
        print(f"ERROR [lintel/freeze]: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
