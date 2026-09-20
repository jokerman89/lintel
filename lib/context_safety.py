# component: context-safety
# implements: ADR-0005, ADR-0006, ADR-0010
# intent: .claude/plans/universal-implementation/packages/P03.md
# constraints: stdlib; explicit roots; no shell evaluation or host-capacity mutation
# last_intent_review: 2026-09-20
"""Bounded context manifests and owned-file primitives; never executes selected text."""
import argparse
from fnmatch import fnmatchcase
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
from typing import Sequence
import unicodedata

SKIP_DIRS = {".git", ".hg", ".svn", ".venv", "node_modules", "__pycache__"}
MAX_CANDIDATES = 10000


def is_link(path: Path) -> bool:
    return path.is_symlink() or bool(path.exists() and
                                    getattr(path.lstat(), "st_file_attributes", 0) & 0x400)


def checked_root(value: Path) -> Path:
    root = Path(os.path.abspath(value))
    for part in (root, *root.parents):
        if is_link(part):
            raise ValueError(f"Symlink/reparse root refused: {part}")
    if not root.is_dir() or root == Path(root.anchor):
        raise ValueError(f"An explicit non-root directory is required: {root}")
    return root.resolve()


def relative_path(value: str) -> str:
    """Use the portable managed-path boundary established by li-copilot.py."""
    rel = PurePosixPath(value)
    if (not value or value != rel.as_posix() or rel.is_absolute()
            or any(p in (".", "..") for p in rel.parts)
            or any(c in value for c in "\\:") or any(ord(c) < 32 or ord(c) == 127 for c in value)
            or any(p.endswith((" ", ".")) or re.fullmatch(r"(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])",
                                                         p.split(".")[0]) for p in rel.parts)):
        raise ValueError(f"Unsafe relative path: {value!r}")
    return value


def path_key(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold()


def selector_path(value: str) -> str:
    # Backslashes are path separators at the user-input boundary, never escapes.
    value = value.replace("\\", "/")
    if value.startswith("./"):
        value = value[2:]
    return relative_path(value)


def safe_path(root: Path, relative: str) -> Path:
    relative_path(relative)
    path = root
    for part in PurePosixPath(relative).parts:
        path = path / part
        if is_link(path):
            raise ValueError(f"Symlink/reparse path refused: {path}")
        if path != root / relative and path.exists() and not path.is_dir():
            raise ValueError(f"Parent is not a directory: {path}")
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"Path escapes root: {relative}")
    return path


def read_owned(root: Path, relative: str, max_bytes: int | None = None) -> tuple[bytes, dict]:
    path = safe_path(root, relative)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"Not a regular file: {path}")
    if max_bytes is not None and before.st_size > max_bytes:
        raise ValueError(f"File exceeds byte bound: {relative}")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    with os.fdopen(os.open(path, flags), "rb") as stream:
        data = stream.read() if max_bytes is None else stream.read(max_bytes + 1)
        opened = os.fstat(stream.fileno())
    after = safe_path(root, relative).lstat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_mode)
    if identity(before) != identity(opened) or identity(before) != identity(after):
        raise ValueError(f"File changed while reading: {relative}")
    if max_bytes is not None and len(data) > max_bytes:
        raise ValueError(f"File exceeds byte bound: {relative}")
    return data, {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data),
                  "mode": stat.S_IMODE(before.st_mode)}


def file_state(root: Path, relative: str) -> dict | None:
    path = safe_path(root, relative)
    if not path.exists():
        return None
    return read_owned(root, relative)[1]


def atomic_write(root: Path, relative: str, data: bytes, mode: int = 0o600, *,
                 expected: dict | None = None, check_expected: bool = False) -> None:
    path = safe_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path = safe_path(root, relative)
    fd, name = tempfile.mkstemp(prefix=".lintel-write-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(mode)
        safe_path(root, relative)
        if check_expected and file_state(root, relative) != expected:
            raise ValueError(f"File changed while staging its replacement: {relative}")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def json_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def checkpoint_directory(directory: Path, *, create=False) -> Path:
    directory = Path(os.path.abspath(directory))
    for parent in (directory, *directory.parents):
        if is_link(parent) or (parent.exists() and not parent.is_dir()):
            raise ValueError(f"Unsafe checkpoint directory: {parent}")
    if create:
        directory.mkdir(parents=True, exist_ok=True)
    return checked_root(directory)


def reserve_checkpoint(directory: Path, name: str) -> Path:
    directory = checkpoint_directory(directory, create=True)
    relative_path(name)
    if "/" in name or not name.endswith("-context-save.md"):
        raise ValueError("Invalid checkpoint filename.")
    for number in range(1, 10000):
        candidate = (name if number == 1 else
                     name.removesuffix("-context-save.md") + f"-copy{number:04d}-context-save.md")
        path = safe_path(directory, candidate)
        try:
            with path.open("xb"):
                pass
            return path
        except FileExistsError:
            continue
    raise ValueError("Checkpoint name collision bound exceeded.")


def matches(path: str, pattern: str, *, root: Path | None = None) -> bool:
    parts = path.split("/")
    rules: list[str] = []
    for rule in pattern.split("/"):
        if rule != "**" or not rules or rules[-1] != "**":
            rules.append(rule)

    def segment_matches(i: int, j: int) -> bool:
        if fnmatchcase(parts[i], rules[j]):
            return True
        if root is None or not fnmatchcase(parts[i].lower(), rules[j].lower()):
            return False
        candidate = root.joinpath(*parts[:i + 1])
        alias = candidate.with_name(parts[i].swapcase())
        if alias.name == candidate.name or is_link(alias):
            return False
        try:
            return candidate.samefile(alias)
        except FileNotFoundError:
            return False

    # reachable[j] means the first j rules matched the consumed path prefix.
    # Rolling rows evaluate each path/rule state once, without recursive backtracking.
    reachable = [True] + [False] * len(rules)
    for j, rule in enumerate(rules):
        if rule == "**":
            reachable[j + 1] = reachable[j]
    for i in range(len(parts)):
        following = [False] * (len(rules) + 1)
        for j, rule in enumerate(rules):
            if rule == "**":
                following[j + 1] = following[j] or reachable[j + 1]
            elif reachable[j]:
                following[j + 1] = segment_matches(i, j)
        reachable = following
        if not any(reachable):
            return False
    return reachable[-1]


def _glob_files(root: Path, pattern: str) -> list[str]:
    def raise_walk_error(error: OSError) -> None:
        raise error

    prefix = []
    for part in pattern.split("/"):
        if any(c in part for c in "*?["):
            break
        prefix.append(part)
    start = safe_path(root, "/".join(prefix)) if prefix else root
    if start.is_file():
        return [start.relative_to(root).as_posix()] if len(prefix) == len(pattern.split("/")) else []
    if not start.exists():
        return []
    result, examined = [], 0
    for folder, dirs, names in os.walk(start, followlinks=False, onerror=raise_walk_error):
        dirs[:] = sorted(d for d in dirs if d.casefold() not in SKIP_DIRS and not is_link(Path(folder) / d))
        examined += len(dirs) + len(names)
        if examined > MAX_CANDIDATES:
            raise ValueError("Context search exceeds 10000 entries; narrow the glob.")
        for name in sorted(names):
            path = Path(folder) / name
            relative = path.relative_to(root).as_posix()
            if not is_link(path) and matches(relative, pattern, root=root):
                safe_path(root, relative)
                result.append(relative)
    return result


def _root_relative(root: Path, path: Path) -> str:
    absolute = Path(os.path.abspath(path))
    if not absolute.is_relative_to(root):
        raise ValueError(f"State path is outside the selected root: {path}")
    return relative_path(absolute.relative_to(root).as_posix())


def _exclusions(root: Path, path: Path | None) -> tuple[list[str], list[str]]:
    if path is None:
        return [], []
    relative = _root_relative(root, path)
    if not safe_path(root, relative).exists():
        return [], []
    data = json.loads(read_owned(root, relative, 65536)[0])
    if (not isinstance(data, dict) or type(data.get("schema_version")) is not int
            or data.get("schema_version") != 1
            or data.get("owner") != str(root)):
        raise ValueError("Unknown or foreign context exclusions; inspect before replacing.")
    for key in ("paths", "patterns"):
        if not isinstance(data.get(key), list):
            raise ValueError(f"Invalid context exclusion {key}.")
        for value in data[key]:
            if not isinstance(value, str):
                raise ValueError("Context exclusions must be relative strings.")
            relative_path(value)
    return data["paths"], data["patterns"]


def _excluded_identities(root: Path, paths: Sequence[str]) -> set[tuple[int, int]]:
    identities = set()
    for relative in paths:
        path = safe_path(root, relative)
        try:
            info = path.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISREG(info.st_mode):
            identities.add((info.st_dev, info.st_ino))
    return identities


def update_exclusions(root: Path, path: Path, paths: Sequence[str] = (),
                      patterns: Sequence[str] = (), *, clear: bool = False) -> dict:
    root = checked_root(root)
    relative = _root_relative(root, path)
    old_paths, old_patterns = _exclusions(root, path)
    selected = [] if clear else sorted(set(old_paths) | {selector_path(p) for p in paths})
    globs = [] if clear else sorted(set(old_patterns) | {selector_path(p) for p in patterns})
    record = {"schema_version": 1, "owner": str(root), "paths": selected, "patterns": globs}
    encoded = json_bytes(record)
    if len(encoded) > 65536:
        raise ValueError("Exclusions exceed the 64KiB reader bound; narrow the selection.")
    atomic_write(root, relative, encoded)
    return {**record, "tokens_removed_from_context": 0, "disk_bytes_removed": 0,
            "effect": "future selections only; existing conversation is unchanged"}


def adr_metadata(text: str) -> dict:
    def field(name: str) -> str | None:
        found = re.search(rf"^\s*(?:-\s+)?(?:\*\*)?{name}:(?:\*\*)?\s*([^\r\n]+)",
                          text, re.M | re.I)
        return found[1].strip(" '\"") if found else None

    title = re.search(r"^#\s+(.+)$", text, re.M)
    status = field("status")
    known = re.match(r"(accepted|proposed|deprecated|superseded|rejected)\b", status or "", re.I)
    date = re.search(r"\d{4}-\d{2}-\d{2}", field("date") or status or "")
    return {"title": title[1] if title else None, "status": known[1].lower() if known else "unknown",
            "raw_status": status, "date": date[0] if date else None}


def select_files(root: Path, paths: Sequence[str] = (), patterns: Sequence[str] = (), *,
                 exclude_file: Path | None = None, excludes: Sequence[str] = (),
                 max_files: int = 40, max_bytes: int = 262144, limit: int | None = None,
                 topic: str | None = None, adr_status: str | None = None) -> dict:
    root = checked_root(root)
    if not paths and not patterns:
        raise ValueError("Supply explicit --path or --glob selections; there is no whole-repo default.")
    if max_files < 1 or max_bytes < 1 or (limit is not None and not 1 <= limit <= max_files):
        raise ValueError("Selection limits must be positive; limit cannot exceed max-files.")
    if adr_status not in (None, "all", "active", "accepted"):
        raise ValueError("Unknown ADR status filter.")
    omitted_paths, omitted_globs = _exclusions(root, exclude_file)
    omitted_keys = _excluded_identities(root, omitted_paths)
    omitted_globs += [selector_path(p) for p in excludes]
    candidates, unmatched, excluded = set(), [], []
    for value in paths:
        relative = selector_path(value)
        path = safe_path(root, relative)
        if not path.exists():
            unmatched.append(value)
        elif not path.is_file():
            raise ValueError(f"Literal target is not a file; use a bounded glob: {value}")
        else:
            candidates.add(relative)
    for value in patterns:
        found = _glob_files(root, selector_path(value))
        if not found:
            unmatched.append(value)
        candidates.update(found)
    files, scanned_bytes = [], 0
    for relative in sorted(candidates):
        alias_excluded = False
        if omitted_keys:
            info = safe_path(root, relative).lstat()
            alias_excluded = (info.st_dev, info.st_ino) in omitted_keys
        if ({p.casefold() for p in PurePosixPath(relative).parts} & SKIP_DIRS
                or relative in omitted_paths or alias_excluded
                or any(matches(relative, p, root=root) for p in omitted_globs)):
            excluded.append(relative)
            continue
        data, state = read_owned(root, relative, max_bytes)
        scanned_bytes += len(data)
        if scanned_bytes > max_bytes * 4:
            raise ValueError("Candidate scan exceeds its byte bound; narrow the selection.")
        text = data.decode("utf-8", errors="replace")
        count = text.casefold().count(topic.casefold()) if topic else 0
        name_match = bool(topic and topic.casefold() in relative.casefold())
        if topic and not count and not name_match:
            continue
        item = {"path": relative, **state, "estimated_tokens": (len(data) + 3) // 4}
        if topic:
            item["score"] = (3 if name_match else 0) + (2 if count >= 5 else int(count > 0))
        if adr_status:
            item["adr"] = adr_metadata(text)
            status = item["adr"]["status"]
            if ((adr_status == "active" and status not in ("accepted", "proposed", "unknown"))
                    or (adr_status == "accepted" and status not in ("accepted", "unknown"))):
                excluded.append(relative)
                continue
        files.append(item)
    if topic:
        files.sort(key=lambda f: (-f["score"], f["path"]))
    omitted_count = max(0, len(files) - limit) if limit is not None else 0
    if limit is not None:
        files = files[:limit]
    total = sum(f["size"] for f in files)
    if len(files) > max_files or total > max_bytes:
        raise ValueError("Context selection exceeds its file/byte bound; narrow it explicitly.")
    return {"schema_version": 1, "source_root": str(root),
            "status": "empty" if not files else ("partial" if unmatched else "selected"),
            "selectors": {"paths": list(paths), "patterns": list(patterns)},
            "files": files, "bytes": total, "estimated_tokens": (total + 3) // 4,
            "estimate_method": "ceil(UTF-8/source bytes / 4); not tokenizer or active context usage",
            "unmatched": unmatched, "excluded": excluded, "omitted_count": omitted_count}


def context_budget(selected_bytes: int, *, capacity_tokens: int | None = None,
                   used_tokens: int | None = None, capacity_source: str | None = None,
                   usage_source: str | None = None, usage_kind: str = "observed",
                   reserve_tokens: int = 0) -> dict:
    for value in (selected_bytes, capacity_tokens, used_tokens, reserve_tokens):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("Byte/token counts must be nonnegative integers.")
    if capacity_tokens is not None and (not capacity_source or capacity_tokens == 0):
        raise ValueError("Capacity requires a positive host-reported limit and its source.")
    if used_tokens is not None and (not usage_source or usage_kind not in ("observed", "estimated")):
        raise ValueError("Usage requires its source and observed/estimated classification.")
    estimate = (selected_bytes + 3) // 4
    known = capacity_tokens is not None and used_tokens is not None
    headroom = max(0, capacity_tokens - used_tokens) if known else None
    admission = "unknown"
    if known:
        admission = ("over-capacity" if used_tokens > capacity_tokens or estimate + reserve_tokens > headroom else
                     ("estimated-fit" if usage_kind == "estimated" else "within-reported-headroom"))
    return {"capacity_tokens": capacity_tokens, "capacity_source": capacity_source,
            "used_tokens": used_tokens, "usage_kind": usage_kind if used_tokens is not None else "unknown",
            "usage_source": usage_source, "headroom_tokens": headroom,
            "headroom_kind": usage_kind if known else "unknown",
            "selected_bytes": selected_bytes, "estimated_input_tokens": estimate,
            "estimate_method": "ceil(source bytes / 4); excludes unobserved conversation and output",
            "reserve_tokens": reserve_tokens, "admission": admission}


def perf_advice(report: dict, *, budget: int | None = None, ceiling: int | None = None,
                decay_policy: str = "conservative", off: bool = False) -> dict:
    if any(value is not None and (type(value) is not int or value < 1) for value in (budget, ceiling)):
        raise ValueError("Local advisory budgets must be positive integers.")
    if budget is not None and ceiling is not None and budget > ceiling:
        raise ValueError("Requested working set exceeds the local advisory ceiling.")
    if decay_policy not in ("prompt-operator", "aggressive", "conservative", "retain-all"):
        raise ValueError("Unknown advisory retrieval strategy.")
    fit = "not-requested" if off or budget is None else "unknown"
    if not off and budget is not None and report["headroom_tokens"] is not None:
        fit = "exceeds-headroom" if budget > report["headroom_tokens"] else "within-reported-headroom"
    return {**report, "advice_active": not off, "local_working_set_budget": None if off else budget,
            "local_advisory_ceiling": None if off else ceiling,
            "retrieval_strategy": None if off else decay_policy, "host_settings_changed": False,
            "requested_working_set_fit": fit,
            "cost_estimate": None, "cost_reason": "Current provider pricing and billable usage not supplied"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    select = commands.add_parser("select", allow_abbrev=False)
    cool = commands.add_parser("cool", allow_abbrev=False)
    reserve = commands.add_parser("reserve", allow_abbrev=False)
    directory = commands.add_parser("check-directory", allow_abbrev=False)
    for command in (reserve, directory):
        command.add_argument("--directory", type=Path, required=True)
    reserve.add_argument("--name", required=True)
    for command in (select, cool):
        command.add_argument("--root", type=Path, required=True)
        command.add_argument("--path", action="append", default=[])
        command.add_argument("--glob", "--pattern", dest="patterns", action="append", default=[])
        command.add_argument("--exclude-file", type=Path)
    select.add_argument("--exclude", action="append", default=[])
    select.add_argument("--max-files", type=int, default=40)
    select.add_argument("--max-bytes", type=int, default=262144)
    select.add_argument("--limit", type=int)
    select.add_argument("--topic")
    select.add_argument("--adr-status", choices=("all", "active", "accepted"))
    cool.add_argument("--clear", action="store_true")
    budget = commands.add_parser("budget", allow_abbrev=False)
    perf = commands.add_parser("perf", allow_abbrev=False)
    for command in (budget, perf):
        command.add_argument("--bytes", type=int, default=0)
        command.add_argument("--capacity", type=int)
        command.add_argument("--used", type=int)
        command.add_argument("--capacity-source")
        command.add_argument("--usage-source")
        command.add_argument("--usage-kind", choices=("observed", "estimated"), default="observed")
        command.add_argument("--reserve", type=int, default=0)
    perf.add_argument("--budget", type=int)
    perf.add_argument("--ceiling", type=int)
    perf.add_argument("--decay-policy", default="conservative")
    perf.add_argument("--off", action="store_true")
    perf.add_argument("--cost-estimate", action="store_true",
                      help="Report cost as unknown unless actual billing inputs are available.")
    args = parser.parse_args()
    try:
        if args.command == "reserve":
            print(reserve_checkpoint(args.directory, args.name))
            return 0
        if args.command == "check-directory":
            checkpoint_directory(args.directory)
            return 0
        if args.command == "select":
            result = select_files(args.root, args.path, args.patterns, exclude_file=args.exclude_file,
                                  excludes=args.exclude, max_files=args.max_files,
                                  max_bytes=args.max_bytes, limit=args.limit, topic=args.topic,
                                  adr_status=args.adr_status)
        elif args.command == "cool":
            if not args.exclude_file:
                raise ValueError("Cooling requires an explicit repo-owned exclusions file.")
            result = update_exclusions(args.root, args.exclude_file, args.path, args.patterns,
                                       clear=args.clear)
        else:
            result = context_budget(args.bytes, capacity_tokens=args.capacity, used_tokens=args.used,
                                    capacity_source=args.capacity_source, usage_source=args.usage_source,
                                    usage_kind=args.usage_kind, reserve_tokens=args.reserve)
            if args.command == "perf":
                result = perf_advice(result, budget=args.budget, ceiling=args.ceiling,
                                     decay_policy=args.decay_policy, off=args.off)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 1 if args.command == "select" and result["status"] != "selected" else 0
    except (ValueError, OSError, RecursionError) as error:
        print(f"context-safety: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
