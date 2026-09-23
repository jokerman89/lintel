#!/usr/bin/env python3
# component: lintel-lessons
# implements: ADR-0005, ADR-0006, ADR-0028
# intent: docs/concepts/memory-v2.md
# constraints: stdlib only; one lesson grammar shared with the awk reads in lib/memory.sh; never breaks a lock, reuses an ID or deletes a lesson
# last_intent_review: 2026-09-23
"""ID-managed lessons: allocation, by-ID retrieval, conditional add/update/supersede and promotion.

Grammar: a lesson heading is `## L-<digits> — <title>` (readers also accept ` - `) outside
fenced code. A block runs to the line before the next level-two heading outside a fence.
`superseded_by: L-NNN` and `supersedes: L-NNN` markers may sit on any block line, optionally
behind `> `, with trailing text. IDs compare numerically; a new ID is one more than the
highest ID in the store, including superseded and duplicated IDs.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
from contextlib import contextmanager  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
import datetime as dt  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
from pathlib import Path  # noqa: E402
import re  # noqa: E402
import shlex  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402

SOURCE_ROOT = Path(__file__).resolve().parent.parent
LIB = SOURCE_ROOT / "lib"
AUDIT_HELPER = SOURCE_ROOT / "bin" / "_audit.sh"
MEMORY_HELPER = LIB / "memory.sh"
TEMPLATE = SOURCE_ROOT / "scaffolding" / "01-foundation" / ".claude" / "memory" / "lessons.md"
PROMOTION_TARGET = "scaffolding/01-foundation/.claude/memory/lessons.md"
EM_DASH = "\u2014"
PREFIX = "WARN [lintel/lessons]: "

HEADING = re.compile(r"## L-(\d+)(?:[ \t]*| (?:\u2014|-) (.*?)[ \t]*)")
LOOSE = re.compile(r"## L-")
LEVEL_TWO = re.compile(r"##(?:[ \t]|$)")
DATED = re.compile(r"## \d{4}-\d{2}-\d{2}")
MARKER = re.compile(r"[ \t]*(?:>[ \t]*)?(superseded_by|supersedes):[ \t]*(L-(\d+))")
LESSON_ID = re.compile(r"L-(\d+)")
PROVENANCE = re.compile(r"<!-- lintel-promotion: source_label=([A-Za-z0-9._-]+); source_id=L-(\d+);")
LABEL = re.compile(r"[A-Za-z0-9._-]{1,64}")
OPERATOR = re.compile(r"[A-Za-z0-9._@-]{1,64}")


def _trusted(name: str):
    path = LIB / name
    info = path.lstat() if path.exists() else None
    if info is None or path.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400:
        raise ImportError(f"Required trusted source helper is missing or linked: {path}")
    spec = importlib.util.spec_from_file_location("lintel_lessons_" + path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load required trusted source helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


context_safety = _trusted("context_safety.py")
native_io_path = context_safety.native_io_path


class LessonError(Exception):
    """A refusal with its exit code; nothing was written when it is raised."""

    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


class LessonConflict(LessonError):
    """The store was locked or changed before the conditional replace: exit 9."""

    def __init__(self, message: str):
        super().__init__(9, message)


class Unobserved(LessonError):
    def __init__(self, message: str = "no project lessons store (unobserved)"):
        super().__init__(3, message)


@dataclass
class Lesson:
    number: int
    lesson_id: str
    title: str
    heading: str
    start: int
    end: int = 0
    superseded_by: str | None = None
    supersedes: list = field(default_factory=list)

    @property
    def state(self) -> str:
        return "superseded" if self.superseded_by else "active"


@dataclass
class Parsed:
    raw: list
    lessons: list
    diagnostics: list

    def find(self, number: int) -> list:
        return [lesson for lesson in self.lessons if lesson.number == number]

    def next_id(self) -> str:
        return f"L-{max((lesson.number for lesson in self.lessons), default=0) + 1:03d}"


def _fence_open(text: str):
    match = re.match(r"( {0,3})(`{3,}|~{3,})", text)
    return (match.group(2)[0], len(match.group(2))) if match else None


def _fence_close(text: str, fence) -> bool:
    char, length = fence
    return re.fullmatch(r" {0,3}" + re.escape(char) + "{" + str(length) + r",}[ \t]*", text) is not None


def split_lines(data: bytes | None) -> list:
    """Physical lines with their terminators; only LF separates lines, CR is tolerated."""
    if not data:
        return []
    parts = data.split(b"\n")
    lines = [part + b"\n" for part in parts[:-1]]
    if parts[-1]:
        lines.append(parts[-1])
    return lines


def text_of(raw: bytes) -> str:
    return raw.decode("utf-8", "replace").rstrip("\n").rstrip("\r")


def parse(data: bytes | None) -> Parsed:
    raw = split_lines(data)
    lessons, diagnostics, first, markers = [], [], {}, []
    current, fence = None, None
    for index, line in enumerate(raw):
        text, number = text_of(line), index + 1
        if fence:
            if _fence_close(text, fence):
                fence = None
            continue
        opened = _fence_open(text)
        if opened:
            fence = opened
            continue
        if LEVEL_TWO.match(text):
            if current:
                current.end = index
                lessons.append(current)
                current = None
            heading = HEADING.fullmatch(text)
            if heading:
                value = int(heading.group(1))
                current = Lesson(value, "L-" + heading.group(1), heading.group(2) or "", text[3:], index)
                if value in first:
                    diagnostics.append((number, "duplicate_id",
                                        f"duplicate lesson ID L-{heading.group(1)} (first at line {first[value]})"))
                else:
                    first[value] = number
            elif LOOSE.match(text):
                diagnostics.append((number, "unparseable_heading", f"unparseable lesson heading: {text}"))
            elif DATED.match(text):
                diagnostics.append((number, "dated_heading", f"dated heading is an unindexed legacy entry: {text}"))
            continue
        marker = MARKER.match(text) if current else None
        if marker:
            if marker.group(1) == "superseded_by":
                current.superseded_by = current.superseded_by or marker.group(2)
            else:
                current.supersedes.append(marker.group(2))
            markers.append((number, int(marker.group(3)), marker.group(2)))
    if current:
        current.end = len(raw)
        lessons.append(current)
    for number, target, spelling in markers:
        if target not in first:
            diagnostics.append((number, "missing_supersede_target", f"marker names {spelling}, which does not exist"))
    return Parsed(raw, lessons, sorted(diagnostics))


def report(parsed: Parsed, store: Path) -> None:
    for number, code, detail in parsed.diagnostics:
        print(f"{PREFIX}line {number}: {code}: {detail} ({store.as_posix()})", file=sys.stderr)


def lesson_number(value: str) -> int:
    if value.startswith("global:"):
        raise LessonError(2, "operator lessons sink not activated; global lessons are not ID-managed")
    match = LESSON_ID.fullmatch(value or "")
    if not match:
        raise LessonError(2, f"malformed lesson ID: {value!r}")
    return int(match.group(1))


def newline_of(data: bytes | None) -> bytes:
    if data and data.count(b"\r\n") * 2 > data.count(b"\n"):
        return b"\r\n"
    return b"\n"


def block_lines(lesson_id: str, title: str, body: list, markers=()) -> list:
    return [f"## {lesson_id} {EM_DASH} {title}", *markers, "", *body]


def append_block(base: bytes, lines: list) -> bytes:
    newline = newline_of(base)
    out = base
    if out and not out.endswith(b"\n"):
        out += newline
    if out and not out.endswith(newline + newline):
        out += newline
    return out + b"".join(line.encode("utf-8") + newline for line in lines)


def _bash() -> str:
    bash = shutil.which("bash")
    if bash is None:
        raise LessonError(3, "bash is required to resolve the project lessons store; pass --store")
    return bash


def resolve_project_store():
    """(store, ignored, root) from lib/memory.sh lessons_store_paths, the single resolver."""
    script = ('source "$1" || exit 90\n'
              'p() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf "%s\\n" "$1"; fi; }\n'
              'listing="$(lessons_store_paths)" || exit 3\n'
              "while IFS=$'\\t' read -r key value; do printf '%s\\t%s\\n' \"$key\" \"$(p \"$value\")\"; "
              'done <<< "$listing"\n')
    result = subprocess.run([_bash(), "-c", script, "li-lessons", MEMORY_HELPER.as_posix()],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode == 3:
        raise Unobserved()
    if result.returncode != 0:
        raise LessonError(3, f"cannot resolve the project lessons store: {result.stderr.strip()}")
    values = dict(line.split("\t", 1) for line in result.stdout.splitlines() if "\t" in line)
    if "store" not in values or "root" not in values:
        raise Unobserved()
    ignored = Path(values["ignored"]) if values.get("ignored") else None
    return Path(values["store"]), ignored, Path(values["root"])


def locate(explicit):
    """Resolve the store; reads and writes name any second store they ignore."""
    if explicit:
        return Path(os.path.abspath(explicit)), None, None
    store, ignored, root = resolve_project_store()
    if ignored is not None:
        print(f"{PREFIX}reading {store.as_posix()}; also present and ignored: {ignored.as_posix()}",
              file=sys.stderr)
    return store, ignored, root


def read_store(store: Path):
    """Store bytes, or None when absent. A directory or unreadable file is an error, not absence."""
    target = native_io_path(store)
    try:
        if not target.exists():
            return None
        if not target.is_file():
            raise LessonError(2, f"lessons store is not a regular file: {store.as_posix()}")
        return target.read_bytes()
    except OSError as error:
        raise LessonError(2, f"cannot read lessons store {store.as_posix()}: {error}") from error


def git_toplevel(folder: Path):
    try:
        result = subprocess.run(["git", "-C", str(folder), "rev-parse", "--show-toplevel"], capture_output=True,
                                text=True, encoding="utf-8", errors="replace")
    except OSError:
        return None
    top = result.stdout.strip()
    return Path(top) if result.returncode == 0 and top else None


def lock_seconds() -> float:
    value = os.environ.get("LINTEL_LESSONS_LOCK_SECONDS", "5")
    try:
        seconds = float(value)
    except ValueError:
        seconds = -1
    if not 0 < seconds <= 600:
        raise LessonError(2, f"LINTEL_LESSONS_LOCK_SECONDS must be a positive number of seconds: {value!r}")
    return seconds


@contextmanager
def store_lock(store: Path):
    """The mkdir lock convention: wait up to a timeout, never break a held lock automatically."""
    lock = store.with_name(store.name + ".lock")
    deadline = time.monotonic() + lock_seconds()
    try:
        native_io_path(store.parent).mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise LessonError(4, f"cannot prepare the lessons store directory {store.parent.as_posix()}: {error}") from error
    while True:
        try:
            native_io_path(lock).mkdir()
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise LessonConflict(f"lessons store is locked by {lock.as_posix()}; inspect the interrupted "
                                     "writer before retrying; nothing was written") from None
            time.sleep(0.05)
        except OSError as error:
            raise LessonError(4, f"cannot take the lessons lock {lock.as_posix()}: {error}") from error
    try:
        yield
    finally:
        native_io_path(lock).rmdir()


def write_store(store: Path, build, *, root=None) -> bytes:
    """Conditional write: record the prior state, build from those bytes, compare right before os.replace."""
    try:
        if root is not None:
            base = context_safety.checked_root(Path(root))
            relative = Path(os.path.relpath(store, root)).as_posix()
        else:
            base, relative = context_safety.checked_root(store.parent), store.name
    except (OSError, ValueError) as error:
        raise LessonError(4, f"lessons store location refused: {error}") from error
    with store_lock(store):
        try:
            state = context_safety.file_state(base, relative)
            data = None
            if state is not None:
                data, state = context_safety.read_owned(base, relative)
            new = build(data)
            mode = 0o644 if state is None else state["mode"]
            context_safety.atomic_write(base, relative, new, mode, expected=state, check_expected=True)
        except LessonError:
            raise
        except ValueError as error:
            if str(error).startswith("File changed"):
                raise LessonConflict(f"lessons store changed during the write; retry. Nothing was replaced "
                                     f"({store.as_posix()})") from error
            raise LessonError(4, f"lessons store write refused: {error}") from error
        except OSError as error:
            raise LessonError(4, f"lessons store write failed: {error}") from error
    return new


def emit_audit(event: str, scope: str, lesson_id: str, classification: str, cwd=None) -> None:
    """Advisory lessons event after a successful write; a failure only warns."""
    bash = shutil.which("bash")
    if bash is None:
        print(f"{PREFIX}advisory lessons audit record not written: bash unavailable", file=sys.stderr)
        return
    script = """
        source "$1" || exit 0
        case "$2" in
          lesson_recorded) audit_log lessons lesson_recorded "scope=$3" "id=$4" "classification=$5" ;;
          lesson_updated) audit_log lessons lesson_updated "scope=$3" "id=$4" "classification=$5" ;;
          lesson_superseded) audit_log lessons lesson_superseded "scope=$3" "id=$4" "classification=$5" ;;
        esac
        """
    result = subprocess.run([bash, "-c", script, "li-lessons", AUDIT_HELPER.as_posix(), event, scope, lesson_id,
                             classification], cwd=str(cwd) if cwd else None, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.stderr:
        sys.stderr.write(result.stderr)


def template_bytes() -> bytes:
    return native_io_path(TEMPLATE).read_bytes().replace(b"\r\n", b"\n")


def body_lines(args) -> list:
    if args.body_file:
        try:
            text = native_io_path(Path(os.path.abspath(args.body_file))).read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as error:
            raise LessonError(2, f"cannot read --body-file: {error}") from error
    else:
        text = args.body or ""
    lines = text.replace("\r\n", "\n").strip("\n").split("\n")
    if not any(line.strip() for line in lines):
        raise LessonError(2, "a lesson body is required")
    return lines


def clean_title(value: str) -> str:
    title = (value or "").strip()
    if not title or "\n" in title or "\r" in title:
        raise LessonError(2, "a one-line --title is required")
    return title


def prepare_write(args):
    """Resolve the target store for a write, refusing global scope and missing stores outside a repository."""
    if getattr(args, "scope", "project") == "global":
        raise LessonError(2, "operator lessons sink not activated; nothing was written")
    try:
        store, _, root = locate(args.store)
    except Unobserved:
        raise Unobserved("no project lessons store (unobserved); nothing was written") from None
    if root is None and not native_io_path(store).exists():
        if not native_io_path(store.parent).is_dir() or git_toplevel(store.parent) is None:
            raise Unobserved("no project lessons store outside a repository; nothing was written")
    return store, root


def cmd_inspect(args) -> int:
    store, ignored, _ = locate(args.store)
    data = read_store(store)
    parsed = parse(data)
    report(parsed, store)
    lessons = [{"id": lesson.lesson_id, "number": lesson.number, "title": lesson.title, "line": lesson.start + 1,
                "end_line": lesson.end, "state": lesson.state, "superseded_by": lesson.superseded_by,
                "supersedes": lesson.supersedes} for lesson in parsed.lessons]
    output = {"schema_version": 1, "store": store.as_posix(), "state": "absent" if data is None else "present",
              "ignored_store": ignored.as_posix() if ignored else None, "lessons": lessons,
              "next_id": parsed.next_id(),
              "diagnostics": [{"line": n, "code": c, "detail": d} for n, c, d in parsed.diagnostics]}
    sys.stdout.buffer.write((json.dumps(output, ensure_ascii=False) + "\n").encode("utf-8"))
    return 0


def cmd_next_id(args) -> int:
    store, _, _ = locate(args.store)
    parsed = parse(read_store(store))
    report(parsed, store)
    print(parsed.next_id())
    return 0


def cmd_get(args) -> int:
    number = lesson_number(args.id)
    try:
        store, _, _ = locate(args.store)
    except Unobserved as error:
        print(f"li-lessons: {error}", file=sys.stderr)
        return 1
    data = read_store(store)
    if data is None:
        print(f"li-lessons: project lessons store absent (unobserved): {store.as_posix()}", file=sys.stderr)
        return 1
    parsed = parse(data)
    report(parsed, store)
    matches = parsed.find(number)
    if len(matches) > 1:
        lines = ", ".join(str(lesson.start + 1) for lesson in matches)
        print(f"li-lessons: {args.id} is duplicated (lines {lines}); retrieval refused", file=sys.stderr)
        return 2
    if not matches:
        print(f"li-lessons: {args.id} is absent from {store.as_posix()}", file=sys.stderr)
        return 1
    lesson = matches[0]
    sys.stdout.buffer.write(b"".join(parsed.raw[lesson.start:lesson.end]))
    sys.stdout.buffer.flush()
    return 0


def select(parsed: Parsed, number: int, lesson_id: str) -> Lesson:
    matches = parsed.find(number)
    if len(matches) > 1:
        raise LessonError(2, f"{lesson_id} is duplicated; resolve the duplicate before writing")
    if not matches:
        raise LessonError(1, f"{lesson_id} is absent; nothing was written")
    return matches[0]


def cmd_add(args) -> int:
    title, body = clean_title(args.title), body_lines(args)
    store, root = prepare_write(args)
    allocated = {}

    def build(current):
        base = template_bytes() if current is None else current
        parsed = parse(base)
        report(parsed, store)
        allocated["id"] = parsed.next_id()
        return append_block(base, block_lines(allocated["id"], title, body))

    write_store(store, build, root=root)
    print(allocated["id"])
    print(f"li-lessons: recorded {allocated['id']} in {store.as_posix()}", file=sys.stderr)
    emit_audit("lesson_recorded", "project", allocated["id"], "add", cwd=root or store.parent)
    return 0


def _replace_body(parsed: Parsed, lesson: Lesson, body: list, newline: bytes) -> list:
    """Rewrite only the block body: keep the heading, markers, provenance and the trailing gap."""
    block = parsed.raw[lesson.start:lesson.end]
    old = block[1:]
    gap = len(old)
    while gap > 0 and text_of(old[gap - 1]).strip() in ("", "---"):
        gap -= 1
    kept, fence = [], None
    for line in old[:gap]:
        text = text_of(line)
        if fence:
            fence = None if _fence_close(text, fence) else fence
            continue
        fence = _fence_open(text)
        if not fence and (MARKER.match(text) or text.startswith("<!-- lintel-promotion:")):
            kept.append(line if line.endswith(b"\n") else line + newline)
    new = [line.encode("utf-8") + newline for line in body]
    tail = old[gap:]
    if not tail and lesson.end < len(parsed.raw):
        tail = [newline]
    head = block[0] if block[0].endswith(b"\n") else block[0] + newline
    return parsed.raw[:lesson.start] + [head] + kept + new + tail + parsed.raw[lesson.end:]


def cmd_update(args) -> int:
    number = lesson_number(args.id)
    body = body_lines(args)
    store, root = prepare_write(args)

    def build(current):
        parsed = parse(current)
        report(parsed, store)
        lesson = select(parsed, number, args.id)
        return b"".join(_replace_body(parsed, lesson, body, newline_of(current)))

    write_store(store, build, root=root)
    print(f"li-lessons: updated {args.id} in {store.as_posix()}", file=sys.stderr)
    emit_audit("lesson_updated", "project", args.id, "update", cwd=root or store.parent)
    return 0


def cmd_supersede(args) -> int:
    number = lesson_number(args.id)
    title, body = clean_title(args.title), body_lines(args)
    store, root = prepare_write(args)
    allocated = {}

    def build(current):
        parsed = parse(current)
        report(parsed, store)
        old = select(parsed, number, args.id)
        if old.superseded_by:
            raise LessonError(2, f"{old.lesson_id} is already superseded by {old.superseded_by}; supersede that lesson")
        new_id = parsed.next_id()
        allocated["id"] = new_id
        newline = newline_of(current)
        lines = list(parsed.raw)
        if lines[old.start] and not lines[old.start].endswith(b"\n"):
            lines[old.start] += newline
        stamp = f"superseded_by: {new_id} ({dt.date.today().isoformat()})".encode("utf-8") + newline
        lines.insert(old.start + 1, stamp)
        return append_block(b"".join(lines), block_lines(new_id, title, body, [f"supersedes: {old.lesson_id}"]))

    write_store(store, build, root=root)
    print(allocated["id"])
    print(f"li-lessons: {allocated['id']} supersedes {args.id} in {store.as_posix()}", file=sys.stderr)
    emit_audit("lesson_superseded", "project", allocated["id"], "supersede", cwd=root or store.parent)
    return 0


def git(top: Path, *arguments, check=False):
    """Git in the destination; read-only calls avoid optional index refreshes."""
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(top), *arguments], capture_output=True)
    if check and result.returncode != 0:
        raise LessonError(8, f"git {' '.join(arguments)} failed: {result.stderr.decode('utf-8', 'replace').strip()}")
    return result


def out(result) -> str:
    return result.stdout.decode("utf-8", "replace").strip()


def normalized_title(title: str) -> str:
    return re.sub(r"[^0-9a-z]+", " ", title.casefold()).strip()


def generalized_block(text: str):
    """(title, body) from generalized text with exactly one level-two heading outside fences."""
    lines = text.replace("\r\n", "\n").split("\n")
    headings, fence = [], None
    for index, line in enumerate(lines):
        if fence:
            fence = None if _fence_close(line, fence) else fence
            continue
        fence = _fence_open(line)
        if not fence and LEVEL_TWO.match(line):
            headings.append(index)
    if len(headings) != 1:
        raise LessonError(2, f"the generalized text must contain exactly one level-two heading; found {len(headings)}")
    heading = lines[headings[0]][2:].strip()
    title = re.sub(r"^L-\d+(?:\s+(?:\u2014|-)\s+|\s*$)", "", heading).strip()
    if not title:
        raise LessonError(2, "the generalized heading needs a title")
    body = lines[:headings[0]] + lines[headings[0] + 1:]
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    return title, body


def interactive_label(proposal: str) -> str:
    answer = input(f"Source label to record [{proposal}] (type y to confirm, or a different label): ").strip()
    label = proposal if answer.lower() in ("y", "yes") else answer
    if not LABEL.fullmatch(label or ""):
        raise LessonError(2, "an explicitly confirmed source label matching [A-Za-z0-9._-]{1,64} is required")
    return label


def edit_block(block: bytes) -> str:
    editor = shlex.split(os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi")
    with tempfile.TemporaryDirectory(prefix="lintel-promote-") as scratch:
        path = Path(scratch) / "lesson.md"
        path.write_bytes(block)
        print("Generalize the lesson (strip project-specific names), save and exit; empty it to cancel.")
        subprocess.run([*editor, str(path)], check=False)
        return path.read_bytes().decode("utf-8")


def cmd_promote(args) -> int:
    interactive = sys.stdin.isatty()
    destination = args.lintel_dir or os.environ.get("LINTEL_DIR")
    if not destination:
        raise LessonError(2, "destination not configured: pass --lintel-dir <work tree> or set LINTEL_DIR")
    if args.commit != bool(args.expect_branch):
        raise LessonError(2, "--commit and --expect-branch NAME are required together")
    if args.source_label is not None and not LABEL.fullmatch(args.source_label):
        raise LessonError(2, "--source-label must match [A-Za-z0-9._-]{1,64}")
    if args.operator is not None and not OPERATOR.fullmatch(args.operator):
        raise LessonError(2, "--operator must match [A-Za-z0-9._@-]{1,64}")
    if not interactive:
        missing = [flag for flag, value in (("--id", args.id), ("--generalized-file", args.generalized_file),
                                            ("--source-label", args.source_label)) if value is None]
        if missing:
            raise LessonError(2, "non-interactive promotion requires " + ", ".join(missing))
    generalized = None
    if args.generalized_file:
        try:
            raw = native_io_path(Path(os.path.abspath(args.generalized_file))).read_bytes()
            generalized = generalized_block(raw.decode("utf-8"))
        except (OSError, UnicodeError) as error:
            raise LessonError(2, f"cannot read --generalized-file: {error}") from error
    number = None
    if args.id is not None:
        try:
            number = lesson_number(args.id)
        except LessonError as error:
            raise LessonError(6, f"invalid lesson ID: {error}") from error

    if args.source:
        source = Path(os.path.abspath(args.source))
        if not native_io_path(source).is_file():
            raise LessonError(3, f"source lessons store missing: {source.as_posix()}")
        source_repo = git_toplevel(source.parent)
        if source_repo is None:
            raise LessonError(3, f"--source is outside a Git work tree; nothing was promoted: {source.as_posix()}")
    else:
        try:
            source, _, source_repo = locate(None)
        except Unobserved:
            raise LessonError(3, "no project lessons store (unobserved); pass --source") from None
        if not native_io_path(source).is_file():
            raise LessonError(3, f"source lessons store missing: {source.as_posix()}")

    folder = Path(os.path.abspath(destination))
    top = git_toplevel(folder) if native_io_path(folder).is_dir() else None
    if top is None or os.path.normcase(os.path.abspath(top)) != os.path.normcase(str(folder)):
        raise LessonError(4, f"destination must be the top level of a Git work tree: {folder.as_posix()}")
    target = folder / PROMOTION_TARGET
    if not native_io_path(target).is_file():
        raise LessonError(5, f"promotion target missing: {target.as_posix()}")

    parsed = parse(read_store(source))
    report(parsed, source)
    if number is None:
        for lesson in parsed.lessons:
            print(f"{lesson.lesson_id}\t{lesson.state}\t{lesson.title}")
        chosen = input("Lesson ID to promote (or q to quit): ").strip()
        if chosen in ("", "q"):
            print("Cancelled; nothing was written.")
            return 0
        args.id, number = chosen, lesson_number(chosen)
    matches = parsed.find(number)
    if len(matches) != 1:
        raise LessonError(6, f"{args.id} is {'duplicated' if matches else 'absent'} in {source.as_posix()}")
    lesson = matches[0]
    if generalized is None:
        edited = edit_block(b"".join(parsed.raw[lesson.start:lesson.end]))
        if not edited.strip():
            print("Cancelled; nothing was written.")
            return 0
        generalized = generalized_block(edited)
    title, body = generalized
    label = args.source_label or interactive_label(re.sub(r"[^A-Za-z0-9._-]+", "-", source_repo.name)[:64])
    commit = "unrecorded"
    if args.record_source_commit:
        head = subprocess.run(["git", "-C", str(source_repo), "rev-parse", "HEAD"], capture_output=True, text=True)
        if head.returncode != 0:
            raise LessonError(3, "--record-source-commit needs a source repository with a commit")
        commit = head.stdout.strip()
    provenance = (f"<!-- lintel-promotion: source_label={label}; source_id={lesson.lesson_id}; "
                  f"source_commit={commit}; promoted_on={dt.date.today().isoformat()}"
                  + (f"; operator={args.operator}" if args.operator else "") + " -->")
    relative = PROMOTION_TARGET
    branch = old_head = None
    refs_before = ""
    if args.commit:
        branch = out(git(top, "symbolic-ref", "--short", "-q", "HEAD"))
        problems = []
        if not branch:
            problems.append("HEAD is detached")
        elif branch != args.expect_branch:
            problems.append(f"current branch is {branch}, not {args.expect_branch}")
        if out(git(top, "diff", "--cached", "--name-only")):
            problems.append("the index already has staged changes")
        if git(top, "ls-files", "--error-unmatch", "--", relative).returncode != 0 or \
                out(git(top, "status", "--porcelain", "--", relative)):
            problems.append("the target has an uncommitted change")
        if problems:
            raise LessonError(8, "commit precondition failed: " + "; ".join(problems) + "; nothing was written")
        old_head = out(git(top, "rev-parse", "HEAD"))
        refs_before = out(git(top, "for-each-ref", "--format=%(refname) %(objectname)"))
    allocated = {}

    def build(current):
        existing = parse(current)
        for item in existing.lessons:
            block = b"".join(existing.raw[item.start:item.end]).decode("utf-8", "replace")
            mark = PROVENANCE.search(block)
            if (mark and mark.group(1) == label and int(mark.group(2)) == lesson.number) or \
                    normalized_title(item.title) == normalized_title(title):
                raise LessonError(7, f"already promoted as {item.lesson_id}; nothing was written")
        allocated["id"] = existing.next_id()
        allocated["prior"] = current
        return append_block(current or b"", block_lines(allocated["id"], title, [*body, "", provenance]))

    written = write_store(target, build)
    new_id = allocated["id"]
    print(f"li-lessons-promote: wrote {new_id} to {target.as_posix()} from {label} {lesson.lesson_id}")
    print("Sensitivity: operator-attested; no shared scanner ran on the generalized text.")
    if not args.commit:
        diff = git(top, "diff", "--no-color", "--no-ext-diff", "--", relative)
        sys.stdout.flush()
        sys.stdout.buffer.write(diff.stdout)
        sys.stdout.buffer.flush()
        print("Not committed. HEAD, branches and the index are unchanged. Suggested next steps:")
        print(f"  git -C {shlex.quote(top.as_posix())} add -- {relative}")
        print(f"  git -C {shlex.quote(top.as_posix())} commit -m 'docs(lessons): promote {label} "
              f"{lesson.lesson_id} as {new_id}' -- {relative}")
        emit_audit("lesson_recorded", "promotion", new_id, "promote", cwd=source_repo)
        return 0
    return _commit_promotion(top, relative, target, written, allocated["prior"], branch, old_head, refs_before,
                             f"docs(lessons): promote {label} {lesson.lesson_id} as {new_id}", source_repo, new_id)


def _commit_promotion(top, relative, target, written, prior, branch, old_head, refs_before, message, source_repo,
                      new_id) -> int:
    staged = git(top, "add", "--", relative)
    committed = git(top, "commit", "-q", "-m", message, "--", relative) if staged.returncode == 0 else staged
    if committed.returncode != 0:
        detail = committed.stderr.decode("utf-8", "replace").strip()

        def restore(current):
            if current != written:
                raise LessonConflict("the target changed after the promotion write; it was left untouched")
            return prior

        try:
            write_store(target, restore)
        except LessonConflict:
            print(f"li-lessons-promote: commit failed ({detail}); the target changed afterwards and was not "
                  "restored", file=sys.stderr)
            return 9
        subprocess.run(["git", "-C", str(top), "reset", "-q", "--", relative], capture_output=True)
        print(f"li-lessons-promote: commit failed ({detail}); prior bytes restored and the target unstaged",
              file=sys.stderr)
        return 10
    new_head = out(git(top, "rev-parse", "HEAD"))
    problems = []
    parents = out(git(top, "rev-list", "--parents", "-n", "1", new_head)).split()
    if parents[1:] != [old_head]:
        problems.append("the new commit's parent is not the previous HEAD")
    changed = out(git(top, "diff-tree", "--no-commit-id", "--name-only", "-r", new_head)).splitlines()
    if changed != [relative]:
        problems.append("the commit changed " + ", ".join(changed or ["nothing"]))
    current_ref = f"refs/heads/{branch}"
    moved = lambda listing: sorted(line for line in listing.splitlines() if not line.startswith(current_ref + " "))
    if moved(out(git(top, "for-each-ref", "--format=%(refname) %(objectname)"))) != moved(refs_before):
        problems.append("a ref other than the current branch moved")
    if problems:
        print(f"li-lessons-promote: committed {new_head} on {branch}, but verification failed: "
              + "; ".join(problems) + f". Previous HEAD {old_head}; new HEAD {new_head}. The commit was left in "
              f"place; inspect it and revert or reset it yourself if it is wrong (git -C {top.as_posix()} show "
              f"{new_head}).", file=sys.stderr)
        return 11
    print(f"li-lessons-promote: committed {new_id} as {new_head} on {branch}; not pushed.")
    emit_audit("lesson_recorded", "promotion", new_id, "promote", cwd=source_repo)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="li-lessons", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "next-id"):
        sub.add_parser(name).add_argument("--store")
    get = sub.add_parser("get", help="print one exact block; exit 0 found, 1 absent, 2 duplicated or malformed")
    get.add_argument("--id", required=True)
    get.add_argument("--store")
    for name in ("add", "update", "supersede"):
        command = sub.add_parser(name)
        command.add_argument("--store")
        command.add_argument("--scope", choices=("project", "global"), default="project")
        if name != "add":
            command.add_argument("--id", required=True)
        if name != "update":
            command.add_argument("--title", required=True)
        body = command.add_mutually_exclusive_group(required=True)
        body.add_argument("--body")
        body.add_argument("--body-file")
    promote = sub.add_parser("promote", prog="li-lessons-promote",
                             help="promote one lesson into an explicit Lintel work tree")
    promote.add_argument("--source")
    promote.add_argument("--id")
    promote.add_argument("--generalized-file")
    promote.add_argument("--source-label")
    promote.add_argument("--record-source-commit", action="store_true")
    promote.add_argument("--operator")
    promote.add_argument("--lintel-dir")
    promote.add_argument("--commit", action="store_true")
    promote.add_argument("--expect-branch")
    return parser


COMMANDS = {"inspect": cmd_inspect, "next-id": cmd_next_id, "get": cmd_get, "add": cmd_add,
            "update": cmd_update, "supersede": cmd_supersede, "promote": cmd_promote}


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    name = "li-lessons-promote" if args.command == "promote" else "li-lessons"
    try:
        return COMMANDS[args.command](args)
    except LessonError as error:
        print(f"{name}: {error}", file=sys.stderr)
        return error.code
    except KeyboardInterrupt:
        print(f"{name}: interrupted; the conditional write either completed or replaced nothing", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
