#!/usr/bin/env python3
# component: copilot-repository-adapter
# implements: ADR-0024, ADR-0025, ADR-0027, ADR-0028
# intent: .claude/plans/universal-implementation/spec.md
# constraints: stdlib only, no network, preserve project prose, preflight all writes
# last_intent_review: 2026-09-20
"""Shared repository adapter generator; preserves the Copilot entry and managed ownership."""
import argparse
from bisect import bisect_right
import hashlib
import html
from html.parser import HTMLParser
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import stat
import string
import subprocess
import sys
import tempfile
from urllib.parse import quote, unquote, urlsplit
from typing import Optional

# Installed-source checks must not create bytecode in the consumer before preflight.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from client_capabilities import load_registry, surface_id
_MARKDOWN_PROVIDER = Path(__file__).resolve().parents[1] / "lib/markdown_source.py"
if not _MARKDOWN_PROVIDER.is_file():
    print(f"ERROR: Required source file is missing: {_MARKDOWN_PROVIDER}", file=sys.stderr)
    raise SystemExit(1)
from markdown_source import LineBoundary, classify_markdown

_NATIVE_PROVIDER = Path(__file__).resolve().parents[1] / "lib/native_paths.py"
if not _NATIVE_PROVIDER.is_file():
    print(f"ERROR: Required source file is missing: {_NATIVE_PROVIDER}", file=sys.stderr)
    raise SystemExit(1)
if _NATIVE_PROVIDER.is_symlink() or getattr(_NATIVE_PROVIDER.lstat(), "st_file_attributes", 0) & 0x400:
    print(f"ERROR: Linked trusted source helper is refused: {_NATIVE_PROVIDER}", file=sys.stderr)
    raise SystemExit(1)
_native_spec = importlib.util.spec_from_file_location("lintel_adapter_native_paths", _NATIVE_PROVIDER)
if _native_spec is None or _native_spec.loader is None:
    print(f"ERROR: Cannot load required source helper: {_NATIVE_PROVIDER}", file=sys.stderr)
    raise SystemExit(1)
_native_paths = importlib.util.module_from_spec(_native_spec)
_native_spec.loader.exec_module(_native_paths)
native_io_path = _native_paths.native_io_path
path_identity = _native_paths.path_identity

SCHEMA = 1
INVENTORY = ".github/lintel/manifest.json"
BUNDLE = ".github/lintel"
PROTOCOL_START = b"<!-- LINTEL:SESSION-PROTOCOL:START -->"
PROTOCOL_END = b"<!-- LINTEL:SESSION-PROTOCOL:END -->"
COMPONENTS = ("bin", "lib", "skills", "agents", "templates", "scaffolding/01-foundation", "packs/_default")
DOCS = ("README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "CHANGELOG.md",
        "docs/README.md", "docs/the-cycle.md", "docs/precedence.md", "docs/compliance.md", "docs/architecture.md",
        "docs/GLOSSARY.md", "docs/spec-kit.md", "docs/getting-started.md", "docs/copilot.md",
        "docs/claude-code.md", "docs/multi-cli.md", "docs/client-adapters.md", "docs/enterprise-adoption.md",
        "docs/concepts/planner-as-module.md", "docs/concepts/agent-dispatch-rules.md", "docs/concepts/orientator.md",
        "docs/concepts/swarming-work.md")
PUBLIC_ROOT_DOCS = frozenset(path for path in DOCS if "/" not in path)
PUBLIC_DOC_SUFFIXES = frozenset((".md", ".html", ".htm", ".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"))
PUBLIC_SOURCE_NOTE = (
    "> **Bundled source guide:** GitHub source-repository links refer to material "
    "outside this portable bundle, not files in the working project. "
    "They follow the public `main` branch and are not fetched or live-verified "
    "by the installer. Private packs, personal settings and `.claude/` "
    "knowledge/runtime content are not copied.\n\n"
)
SOURCE_METADATA = (".claude-plugin/plugin.json", "config/aliases.yaml", "install/upstream-sources.yaml")
TEXT_SUFFIXES = {".md", ".sh", ".bash", ".py", ".json", ".yaml", ".yml", ".csv", ".tsv", ".txt",
                 ".template", ".base", ".html", ".htm", ".css", ".js", ".mjs", ".svg"}
ATTRIBUTES = (
    ".github/lintel/** text=auto eol=lf",
    ".github/skills/li-*/** text=auto eol=lf",
    ".github/agents/lintel-*.agent.md text eol=lf",
    ".github/instructions/lintel-session.instructions.md text eol=lf",
)
WORKFLOWS = {
    "welcome": "Use when joining a repository to inspect Lintel setup and choose a first workflow.",
    "cycle": "Use for a multi-step initiative that needs the complete Lintel planning, implementation, review and capture cycle.",
    "sense": "Use at session start to load relevant memory, inspect repository state and scope the request.",
    "scope": "Use when an initiative needs boundaries, dependencies and an appropriate planning depth.",
    "define": "Use when a request needs requirements, acceptance criteria and a concrete design before implementation.",
    "discover": "Use to map an existing repository, relevant architecture and reusable components before planning changes.",
    "plan": "Use to turn a design into a requirement-traced spec, dependency-ordered build cards and a cold-executor prompt.",
    "build": "Use to implement an authorized plan card by card with spec and quality review and verification evidence.",
    "review": "Use to review changes against the specification, engineering quality and the active policy.",
    "ship": "Use after review to prepare a verified change for a pull request or an explicitly authorized release.",
    "capture": "Use after delivery to record evidence, durable lessons and the next-session handoff.",
    "resume": "Use to resume an interrupted initiative from its saved plan, state and handoff.",
    "spec-kit": "Use when a project uses GitHub Spec Kit to connect its requirements and tasks to Lintel build and review evidence.",
    "swarm": "Use when an approved mapped plan opts in to coordinated multi-agent execution with explicit ownership, attributable isolation and durable evidence.",
}
AGENTS = {
    "planner": ("Plan requirements, specifications and executable build cards for a scoped initiative.", "plan"),
    "builder": ("Implement an authorized build card and produce verification evidence with focused changes.", "build"),
    "reviewer": ("Review a change independently for specification compliance, correctness and missing evidence.", "review"),
}
SWARM_RESOURCES = (
    "skills/swarm/SKILL.md",
    "skills/brief-forge/SKILL.md",
    "bin/li-swarm",
    "bin/li-swarm.py",
    "bin/li-work-artifacts.py",
    "bin/li-envelope-validate",
    "bin/li-envelope-replay",
    "bin/_audit.sh",
    "lib/copilot-env.sh",
    "lib/swarm-schema.json",
    "lib/swarm_contract.py",
    "lib/swarm_evidence.py",
    "lib/swarm_snapshot.py",
    "lib/cli-tiers.yaml",
    "lib/brief-forge.sh",
    "lib/brief-forge-evaluators.sh",
    "lib/envelope-schema.yaml",
    "lib/envelope_contract.py",
    "lib/envelope-requirements.txt",
    "lib/pack-resolver.sh",
    "lib/paths.sh",
    "packs/_default/pack.yaml",
    "scaffolding/01-foundation/templates/swarm/charter.template.md",
    "scaffolding/01-foundation/templates/swarm/coordination.template.json",
    "scaffolding/01-foundation/templates/swarm/agent-brief.template.md",
    "scaffolding/01-foundation/templates/swarm/agent-report.template.md",
    "scaffolding/01-foundation/templates/swarm/agent-review.template.md",
)
ADAPTER_RESOURCES = (
    "lib/client_capabilities.py", "lib/cli-tiers.yaml", "lib/cli-tiers.sh",
    "bin/li-client-capabilities.py", "bin/li-adapter.py", "lib/pack-schema.yaml",
    "lib/markdown_source.py", "lib/profile_context.py", "lib/profile-context-schema.json",
    "lib/native_paths.py",
    "lib/context_safety.py", "lib/managed_transaction.py",
    "bin/li-snapshot.py", "bin/li-managed-transaction.py",
    "lib/review_contract.py", "lib/review-schema.json",
    "bin/li-review-evidence.py", "bin/li-review-log", "bin/li-review-read",
    "bin/li-lifecycle", "bin/li-lifecycle.py", "bin/li-scaffold", "bin/li-doctor",
    "bin/li-migrate-claude-home", "bin/li-pack-scaffold",
    "bin/li-domain-result.py", "lib/domain_result.py", "lib/domain-result-schema.json",
    "lib/state.sh", "lib/cycle-modes.sh", "lib/cycle-footer.sh", "lib/workflow.sh",
    "bin/li-events.py", "lib/event-catalog.json", "bin/li-lessons.py",
    "bin/li-catalog.py", "lib/capability-selections.json",
    "skills/catalog/references/metadata.md", "skills/catalog/references/selections.md",
    "skills/browse/scripts/chromium.mjs", "skills/scrape/scripts/extract.mjs",
    "lib/url_policy.py",
    "skills/design-dna/scripts/design_contract.py",
    "skills/design-dna/references/design-contract.schema.json",
    "skills/design-dna/references/design-contract.md",
    "skills/catalog/references/consumer-checks.md",
    "skills/generate-write/references/fidelity-and-evidence.md",
    "skills/generate-word/references/native-word.md",
    "skills/generate-ppt/references/native-powerpoint.md",
    "skills/generate-xlsx/references/native-xlsx.md",
    "skills/generate-xlsx/scripts/check_xlsx.py",
    "skills/generate-pdf/scripts/prepare_html.py",
    "skills/generate-pdf/scripts/check_pdf.py",
    "skills/generate-pdf/scripts/print_pdf.mjs",
    "skills/generate/scripts/pipeline_inputs.py",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    """Reject traversal, Windows drives, symlink/reparse parents, and non-directories."""
    rel = PurePosixPath(relative)
    if not relative or relative != rel.as_posix() or rel.is_absolute() or any(p in (".", "..") for p in rel.parts) or "\\" in relative or ":" in relative:
        raise ValueError(f"Unsafe managed path: {relative!r}")
    path = root
    for part in rel.parts:
        path = path / part
        native = native_io_path(path)
        if native.is_symlink() or (native.exists() and getattr(native.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError(f"Symlink/reparse point refused: {path}")
        if path != root / relative and native.exists() and not native.is_dir():
            raise ValueError(f"Parent is not a directory: {path}")
    resolved = Path(*path_identity(native_io_path(path).resolve()))
    if not resolved.is_relative_to(Path(*path_identity(root))):
        raise ValueError(f"Path escapes target: {relative}")
    return path


def read_file(root: Path, relative: str) -> bytes:
    path = safe_path(root, relative)
    if not native_io_path(path).is_file():
        raise ValueError(f"Required source file is missing: {path}")
    return source_bytes(path)


NOT_REGULAR = "not-regular"


def owned_reader():
    from context_safety import read_owned
    return read_owned


def observe_path(target: Path, relative: str) -> tuple[Optional[bytes], object]:
    """Return the bytes and state one target read derived, never a later rebuild."""
    path = safe_path(target, relative)
    try:
        info = native_io_path(path).lstat()
    except FileNotFoundError:
        return None, None
    if not stat.S_ISREG(info.st_mode):
        return None, NOT_REGULAR
    return owned_reader()(target, relative)


def observe_file(target: Path, relative: str, observed: dict) -> tuple[Optional[bytes], object]:
    if relative not in observed:
        observed[relative] = observe_path(target, relative)
    return observed[relative]


def decoded(data: bytes) -> str:
    # Same universal-newline text the previous read_text() planning consumed.
    return io.TextIOWrapper(io.BytesIO(data), encoding="utf-8").read()


def admitted_expectations(target: Path, observed: dict, changes: dict) -> dict:
    """Pair each write with its planning observation; fresh reads only reject."""
    expected = {}
    for relative in changes:
        if relative not in observed or observed[relative][1] == NOT_REGULAR:
            raise ValueError(f"Adapter publication lacks a planning observation: {relative}")
        expected[relative] = observed[relative][1]
    for relative in sorted(set(observed) - set(changes)):
        if observe_path(target, relative)[1] != observed[relative][1]:
            raise ValueError(f"Adapter input changed after planning (preserved): {relative}")
    return expected


def source_bytes(path: Path) -> bytes:
    data = native_io_path(path).read_bytes()
    if path.suffix in TEXT_SUFFIXES or not path.suffix:
        data = data.replace(b"\r\n", b"\n")
    return data


def text_bytes(value: str) -> bytes:
    return value.rstrip().encode("utf-8") + b"\n"


def html_attribute_spans(token: str) -> list[tuple[str, int, int]]:
    """Locate values inside a start tag already accepted by HTMLParser."""
    prefix = re.match(r"<[^\s/>]+", token)
    cursor = prefix.end() if prefix else len(token)
    spans = []
    while cursor < len(token):
        while cursor < len(token) and token[cursor] in " \t\r\n\f/":
            cursor += 1
        if cursor == len(token) or token[cursor] == ">":
            break
        start = cursor
        while cursor < len(token) and token[cursor] not in " \t\r\n\f/=>":
            cursor += 1
        name = token[start:cursor].lower()
        if cursor == start:
            cursor += 1
            continue
        while cursor < len(token) and token[cursor].isspace():
            cursor += 1
        if cursor == len(token) or token[cursor] != "=":
            continue
        cursor += 1
        while cursor < len(token) and token[cursor].isspace():
            cursor += 1
        quoted = token[cursor] if cursor < len(token) and token[cursor] in "\"'" else ""
        if quoted:
            cursor += 1
        start = cursor
        while cursor < len(token) and (
                token[cursor] != quoted if quoted else token[cursor] not in " \t\r\n\f>"):
            cursor += 1
        spans.append((name, start, cursor))
        if quoted:
            cursor += 1
    return spans


class HTMLNavigation(HTMLParser):
    """HTML grammar owns tags, quoted attributes, comments and raw script/style data."""
    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=False)
        self.text = text
        self.line_offsets = [0] + [match.end() for match in re.finditer("\n", text)]
        self.links: list[tuple[int, int, str]] = []
        self.code_stack: list[str] = []

    def source_position(self) -> int:
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if self.code_stack or tag in ("pre", "code"):
            if tag in ("pre", "code"):
                self.code_stack.append(tag)
            return
        first = {}
        for name, value in attrs:
            first.setdefault(name, value)
        seen = set()
        for name, start, end in html_attribute_spans(self.get_starttag_text()):
            if name in ("href", "src") and name not in seen and isinstance(first.get(name), str):
                self.links.append((self.source_position() + start, self.source_position() + end, first[name]))
            seen.add(name)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if self.code_stack and tag == self.code_stack[-1]:
            self.code_stack.pop()


def markdown_unescape(value: str) -> str:
    value = re.sub(r"\\([" + re.escape(string.punctuation) + r"])", r"\1", value)
    return re.sub(r"&(?:#[xX][0-9a-fA-F]+|#[0-9]+|[A-Za-z][A-Za-z0-9]+);",
                  lambda match: html.unescape(match[0]), value)


def markdown_label_end(source: "MarkdownSource", start: int, limit: int) -> int:
    text = source.text
    depth, cursor = 1, start + 1
    while cursor < limit:
        char = text[cursor]
        if char == "\\" and cursor + 1 < len(text) and text[cursor + 1] in string.punctuation:
            cursor += 2
            continue
        end = source.region_end(cursor)
        if cursor < end:
            if end > limit:
                return start
            cursor = end
            continue
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return cursor
        cursor += 1
    return start


def markdown_space_end(text: str, start: int, limit: int) -> int:
    cursor = start
    while cursor < limit and text[cursor] in " \t\r\n":
        cursor += 1
    return cursor


def markdown_destination(text: str, start: int, limit: int) -> tuple[int, int, int]:
    cursor, depth = start, 0
    angle = cursor < len(text) and text[cursor] == "<"
    if angle:
        start = cursor = cursor + 1
    while cursor < limit:
        char = text[cursor]
        if char == "\\" and cursor + 1 < len(text) and text[cursor + 1] in string.punctuation:
            cursor += 2
            continue
        if angle:
            if char == ">":
                return start, cursor, cursor + 1
            if char in "\r\n<":
                return start, start, start
        else:
            if char.isspace() or ord(char) < 32:
                break
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
        cursor += 1
    if angle or depth:
        return start, start, start
    return start, cursor, cursor


def markdown_title_end(text: str, start: int, limit: int) -> int:
    if start >= limit or text[start] not in "\"'(":
        return start
    delimiter = ")" if text[start] == "(" else text[start]
    cursor = start + 1
    while cursor < limit:
        if text[cursor] == "\\" and cursor + 1 < len(text) and text[cursor + 1] in string.punctuation:
            cursor += 2
            continue
        if text[cursor] == delimiter:
            return cursor + 1
        cursor += 1
    return start


class MarkdownSource:
    """Navigation-only view over the shared provider's original-coordinate facts."""
    def __init__(self, text: str) -> None:
        self.boundaries = classify_markdown(text)
        self.original = self.boundaries.original
        self.lines = self.boundaries.lines
        characters = list(text)
        for line in self.lines:
            for position in range(line.start, line.end):
                if line.kind in ("fenced_code", "indented_code") or position < line.body.start:
                    characters[position] = " "
            for position in range(line.end, line.next_start):
                if text[position] == "\r":
                    characters[position] = " " if text[position:position + 2] == "\r\n" else "\n"
        self.text = "".join(characters)
        self.starts = [line.start for line in self.lines]
        self.limits = [line.end for line in self.lines]
        for index in range(len(self.lines) - 2, -1, -1):
            current, following = self.lines[index:index + 2]
            if current.kind == following.kind == "prose" and current.container_ids == following.container_ids:
                self.limits[index] = self.limits[index + 1]
        self.region_ends = {}
        for region in self.boundaries.regions:
            if region.kind != "quote":
                self.region_ends[region.span.start] = max(
                    region.span.end, self.region_ends.get(region.span.start, region.span.start))
        html_characters = [char if char in "\r\n" else " " for char in self.text]
        literals = [region.span for region in self.boundaries.regions
                    if region.kind in ("inline_code", "fenced_code", "indented_code", "raw_html_body", "comment")]
        for region in self.boundaries.regions:
            if region.kind == "html_tag" and not any(span.start <= region.span.start < span.end for span in literals):
                html_characters[region.span.start:region.span.end] = self.text[region.span.start:region.span.end]
        self.html_text = "".join(html_characters)

    def region_end(self, position: int) -> int:
        return self.region_ends.get(position, position)

    def line_index(self, position: int) -> int:
        return max(0, bisect_right(self.starts, min(position, max(0, len(self.text) - 1))) - 1)

    def line_at(self, position: int) -> LineBoundary:
        return self.lines[self.line_index(position)]

    def limit(self, position: int) -> int:
        return self.limits[self.line_index(position)]

    def definition_start(self, position: int) -> bool:
        line = self.line_at(position)
        return line.kind == "prose" and line.residual_indent <= 3 and position == line.content_start

    def reference_end(self, destination_end: int, limit: int) -> int:
        """A consumed destination/title terminates at logical EOL or EOF, identically."""
        line = self.line_at(max(0, destination_end - 1))
        cursor = destination_end
        while cursor < line.end and self.text[cursor] in " \t":
            cursor += 1
        if cursor == line.end:
            candidate = markdown_space_end(self.text, line.next_start, limit)
            if candidate < limit and self.text[candidate] in "\"'(":
                title_end = markdown_title_end(self.text, candidate, limit)
                if title_end != candidate:
                    title_line = self.line_at(title_end - 1)
                    if not self.text[title_end:title_line.end].strip(" \t"):
                        return title_line.next_start
            return line.next_start
        if cursor == destination_end or self.text[cursor] not in "\"'(":
            return -1
        title_end = markdown_title_end(self.text, cursor, limit)
        if title_end == cursor:
            return -1
        title_line = self.line_at(title_end - 1)
        return title_line.next_start if not self.text[title_end:title_line.end].strip(" \t") else -1


def markdown_tokens(source: MarkdownSource, definitions: dict) -> tuple[list[tuple[int, int, str]], list[tuple[int, int]], dict]:
    """Lex links, code and definitions without treating punctuation as a filesystem path."""
    text = source.text
    links, excluded, references, suffixes = [], [], set(), {}
    cursor = 0
    while cursor < len(text):
        if cursor in suffixes:
            end = suffixes[cursor]
            excluded.append((cursor, end))
            cursor = end
            continue
        limit = source.limit(cursor)
        char = text[cursor]
        if char == "\\" and cursor + 1 < len(text) and text[cursor + 1] in string.punctuation:
            excluded.append((cursor, cursor + 2))
            cursor += 2
            continue
        end = source.region_end(cursor)
        if end > cursor:
            cursor = end
            continue
        if char == "[":
            close = markdown_label_end(source, cursor, limit)
            if close != cursor:
                label = " ".join(markdown_unescape(text[cursor + 1:close]).split()).casefold()
                after = close + 1
                is_definition = source.definition_start(cursor) and text[after:after + 1] == ":"
                if text[after:after + 1] == "(" or is_definition:
                    destination_start = markdown_space_end(text, after + 1, limit)
                    start, finish, end = markdown_destination(text, destination_start, limit)
                    if is_definition and finish > start:
                        reference_end = source.reference_end(end, limit)
                        if reference_end >= end:
                            definitions.setdefault(label, (start, finish, markdown_unescape(text[start:finish])))
                            line_start = source.line_at(cursor).start
                            cursor = reference_end
                            excluded.append((line_start, cursor))
                            continue
                    elif not is_definition:
                        separated = markdown_space_end(text, end, limit)
                        if separated > end and text[separated:separated + 1] in ("'", '"', "("):
                            title_end = markdown_title_end(text, separated, limit)
                            if title_end != separated:
                                separated = markdown_space_end(text, title_end, limit)
                        if text[separated:separated + 1] == ")":
                            links.append((start, finish, markdown_unescape(text[start:finish])))
                            suffixes[after] = separated + 1
                            cursor += 1
                            continue
                second_start = markdown_space_end(text, after, limit)
                if text[second_start:second_start + 1] == "[":
                    second_end = markdown_label_end(source, second_start, limit)
                    if second_end != second_start:
                        reference = " ".join(markdown_unescape(text[second_start + 1:second_end]).split()).casefold()
                        reference = reference or label
                        if reference in definitions:
                            references.add(reference)
                            suffixes[after] = second_end + 1
                        else:
                            references.add(label)
                    else:
                        references.add(label)
                else:
                    references.add(label)
        cursor += 1
    links.extend(definitions[label] for label in references if label in definitions)
    return links, excluded, definitions


def markdown_navigation(source: MarkdownSource) -> tuple[list[tuple[int, int, str]], list[tuple[int, int]]]:
    # Resolve forward reference labels before deciding whether adjacent brackets form a link.
    _, _, definitions = markdown_tokens(source, {})
    links, excluded, _ = markdown_tokens(source, definitions)
    return links, excluded


def document_links(data: bytes, *, markdown: bool = True) -> list[tuple[int, int, str]]:
    """Return source spans for real Markdown/HTML destinations without running either."""
    text = data.decode("utf-8")
    source = MarkdownSource(text) if markdown else None
    links, excluded = markdown_navigation(source) if source else ([], [])
    characters = list(source.html_text if source else text)
    for start, end in excluded:
        for position in range(start, min(end, len(text))):
            if characters[position] not in "\r\n":
                characters[position] = " "
    parser = HTMLNavigation("".join(characters))
    parser.feed(parser.text)
    parser.close()
    links.extend(parser.links)
    result = {}
    for start, end, value in links:
        decoded = unquote(value)
        if "*" in decoded or re.search(r"<[^<>]*>|\{[^{}]*\}", decoded):
            continue
        result[(start, end)] = value
    return [(start, end, value) for (start, end), value in sorted(result.items())]


def local_link(relative: str, link: str) -> str:
    """Resolve URL paths lexically; never read a link target outside the selected source."""
    parsed = urlsplit(link)
    if parsed.scheme.lower() == "file" or re.match(r"^[A-Za-z]:", link) or "\\" in link:
        raise ValueError(f"Non-portable local documentation link in {relative}")
    if parsed.scheme or parsed.netloc or not parsed.path:
        return ""
    path = unquote(parsed.path)
    if path.startswith(("/", "~")) or "\\" in path or ":" in path or "\x00" in path:
        raise ValueError(f"Unsafe local documentation link in {relative}")
    result = posixpath.normpath(posixpath.join(posixpath.dirname(relative), path))
    if result == ".." or result.startswith("../"):
        raise ValueError(f"Documentation link escapes source: {relative}")
    return result


def public_document(relative: str) -> bool:
    parts = PurePosixPath(relative).parts
    return relative in PUBLIC_ROOT_DOCS or (
        len(parts) > 1 and parts[0] == "docs" and all(not part.startswith(".") for part in parts)
        and PurePosixPath(relative).suffix.lower() in PUBLIC_DOC_SUFFIXES)


def bundle_documentation(source: Path, files: dict[str, bytes]) -> None:
    """Close public navigation only; repository-only links never expand the data bundle."""
    metadata = json.loads(read_file(source, ".claude-plugin/plugin.json"))
    repository = metadata.get("repository") if isinstance(metadata, dict) else None
    if not isinstance(repository, str) or not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+", repository):
        raise ValueError("Public source navigation requires the canonical GitHub repository URL")
    pending, visited = list(DOCS), set()
    while pending:
        relative = pending.pop()
        if relative in visited:
            continue
        if not public_document(relative):
            raise ValueError(f"Documentation selection outside public boundary: {relative}")
        visited.add(relative)
        data = read_file(source, relative)
        if PurePosixPath(relative).suffix.lower() in (".md", ".html", ".htm"):
            text, replacements = data.decode("utf-8"), []
            for start, end, link in document_links(data, markdown=relative.endswith(".md")):
                target = local_link(relative, link)
                if not target:
                    continue
                if public_document(target):
                    pending.append(target)
                elif (target == "docs" or target.startswith("docs/")) and urlsplit(link).path.endswith("/") \
                        and all(not part.startswith(".") for part in PurePosixPath(target).parts):
                    # A directory link must reach real bundled children; do not glob-copy it.
                    for index in ("README.md", "_INDEX.md"):
                        candidate = posixpath.join(target, index)
                        if native_io_path(safe_path(source, candidate)).is_file():
                            pending.append(candidate)
                            break
                elif any(target == component or target.startswith(component + "/") for component in COMPONENTS):
                    directory = urlsplit(link).path.endswith("/")
                    if f"{BUNDLE}/{target}" not in files and not (
                            directory and any(path.startswith(f"{BUNDLE}/{target}/") for path in files)):
                        raise ValueError(f"Missing bundled source target: {relative} -> {link}")
                elif f"{BUNDLE}/{target}" not in files:
                    parsed = urlsplit(link)
                    kind = "tree" if parsed.path.endswith("/") else "blob"
                    url = f"{repository}/{kind}/main/{quote(target, safe='/')}"
                    if parsed.fragment:
                        url += "#" + quote(unquote(parsed.fragment), safe="-_")
                    replacements.append((start, end, url))
            for start, end, url in reversed(replacements):
                text = text[:start] + url + text[end:]
            if replacements and not text.startswith(PUBLIC_SOURCE_NOTE):
                text = PUBLIC_SOURCE_NOTE + text
            data = text.encode("utf-8")
        files[f"{BUNDLE}/{relative}"] = data


def generate(source: Path, target: Path,
             clients: tuple[str, ...] = ("copilot-cli",)) -> tuple[dict[str, bytes], dict[str, bytes], str]:
    local = source == target
    registry = load_registry(native_io_path(safe_path(source, "lib/cli-tiers.yaml")))
    records = [registry["surfaces"][surface_id(registry, client)] for client in clients]
    copilot = any(record["discovery"]["kind"] == "copilot" for record in records)
    files = {}
    # A deliberately scoped source bundle: never copy .git, user packs, runtime,
    # customer material, host settings, hooks, or this generated bundle recursively.
    if not local:
        for component in COMPONENTS:
            folder = safe_path(source, component)
            native_folder = native_io_path(folder)
            if not native_folder.is_dir():
                raise ValueError(f"Missing source component: {component}")
            for candidate in sorted(native_folder.rglob("*")):
                path = folder / candidate.relative_to(native_folder)
                relative = path.relative_to(source).as_posix()
                safe_path(source, relative)
                if native_io_path(path).is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                    files[f"{BUNDLE}/{relative}"] = source_bytes(path)
        for canonical, entry in (("shims/copilot/COPILOT.md", "COPILOT.md"),
                                 ("shims/universal/ADAPTER.md", "ADAPTER.md")):
            bridge = canonical if native_io_path(source / canonical).is_file() else entry
            data = read_file(source, bridge)
            files[f"{BUNDLE}/{entry}"] = data
            files[f"{BUNDLE}/{canonical}"] = data
        for relative in SOURCE_METADATA:
            files[f"{BUNDLE}/{relative}"] = read_file(source, relative)
        bundle_documentation(source, files)
    # These are the direct workflow, validation, handoff, policy, audit/path and
    # template dependencies needed by the swarm entry point. Fail generation if
    # the installed source is incomplete instead of deferring failure to dispatch.
    for relative in SWARM_RESOURCES:
        data = read_file(source, relative)
        if not local and files.get(f"{BUNDLE}/{relative}") != data:
            raise ValueError(f"Swarm resource was not bundled: {relative}")
    for relative in ADAPTER_RESOURCES:
        data = read_file(source, relative)
        if not local and files.get(f"{BUNDLE}/{relative}") != data:
            raise ValueError(f"Adapter resource was not bundled: {relative}")
    # File-relative Markdown links work after copying and in clean cloud clones.
    skill_source = "../../.." if local else "../../lintel"
    bridge_skill = "../../../shims/copilot/COPILOT.md" if local else "../../lintel/COPILOT.md"
    bridge_instruction = "../shims/copilot/COPILOT.md" if local else "lintel/COPILOT.md"
    for name, description in WORKFLOWS.items():
        read_file(source, f"skills/{name}/SKILL.md")
        files[f".github/skills/li-{name}/SKILL.md"] = text_bytes(f"""---
name: li-{name}
description: {description}
---

# Lintel {name}

Read the [Copilot adapter contract]({bridge_skill}) first, then execute the
[canonical {name} workflow]({skill_source}/skills/{name}/SKILL.md) for the user's request.
Resolve source resources relative to that canonical file; write outputs to the working
repository. Follow the adapter's tool mapping, authorization and verification rules.
""")
    bridge_agent = "../../shims/copilot/COPILOT.md" if local else "../lintel/COPILOT.md"
    for name, (description, workflow) in AGENTS.items():
        files[f".github/agents/lintel-{name}.agent.md"] = text_bytes(f"""---
name: lintel-{name}
description: {description}
---

Read the [Copilot adapter contract]({bridge_agent}) and use the
[Lintel {workflow} skill](../skills/li-{workflow}/SKILL.md).
Keep the task bounded to the supplied requirements and repository context. Report
changed files, checks actually run, findings by severity, and unresolved limitations.
Do not claim independent review if you implemented the same change. If delegation
is unavailable, label the pass as self-review and retain the human review gate.
""")
    files[".github/instructions/lintel-session.instructions.md"] = text_bytes(f"""---
applyTo: "**"
---

This repository uses Lintel. Read [the Copilot adapter]({('../' + bridge_instruction)})
before a multi-step task. Load the repository's AGENTS.md and relevant memory and
decisions. Keep plans and durable lessons in .claude/; the directory name is shared
storage, not a requirement to use Claude Code. Use li-plan before substantive work,
li-build for authorized cards and li-review before delivery. Existing user authorization
remains valid; ask only for missing scope or a new permission boundary. Lintel instructions
and reviews complement host permissions and branch rules; they do not enforce them.
""")
    files[".github/copilot-instructions.md"] = text_bytes(f"""# Lintel repository instructions

Read [the repository instructions](../AGENTS.md), then the
[Copilot adapter contract]({bridge_instruction}) for multi-step work.

Use `/li-welcome` to inspect setup, `/li-plan` to create a spec and build cards,
`/li-build` to execute authorized cards, and `/li-review` to verify changes.
Use `/li-cycle` for the complete workflow and `/li-resume` to continue a saved plan.
If slash discovery is unavailable, ask Copilot to read the corresponding
`.github/skills/li-<name>/SKILL.md` and carry out its instructions.

Read project memory and relevant decisions before edits. Verify actual behavior and
report checks, outcomes and limitations. Keep secrets and customer data out of artifacts.
Repository instructions do not replace enterprise policy, tool permissions or human review.
""")
    if not copilot:
        for relative in tuple(files):
            if (relative.startswith((".github/skills/", ".github/agents/", ".github/instructions/"))
                    or relative == ".github/copilot-instructions.md"):
                del files[relative]
    universal_bridge = "shims/universal/ADAPTER.md" if local else f"{BUNDLE}/ADAPTER.md"
    canonical_root = "" if local else BUNDLE + "/"
    for record in records:
        discovery = record["discovery"]
        if discovery["kind"] != "skills":
            continue
        for name, description in WORKFLOWS.items():
            relative = f"{discovery['root']}/li-{name}/SKILL.md"
            parent = posixpath.dirname(relative)
            bridge_link = posixpath.relpath(universal_bridge, parent)
            workflow_link = posixpath.relpath(f"{canonical_root}skills/{name}/SKILL.md", parent)
            project_link = posixpath.relpath("AGENTS.md", parent)
            files[relative] = text_bytes(f"""---
name: li-{name}
description: {description}
---

# Lintel {name}

Read the [project instructions]({project_link}) and [Universal adapter]({bridge_link}),
then execute the [canonical {name} workflow]({workflow_link}) for the user's request.
Use actual available host tools and permissions, not vendor-specific examples as commands.
Resolve source resources relative to the canonical workflow; write state to the working
repository. Missing delegation preserves serial/manual handoff and outstanding independent
review. This file supplies native discovery format, not evidence of live host execution.
""")
    start_parent = BUNDLE
    routes = "\n".join(f"- `{client}`: " + (
        f"native-format files at `{registry['surfaces'][client]['discovery']['root']}/li-*/SKILL.md`."
        if registry["surfaces"][client]["discovery"]["root"] else
        "manual canonical-file handoff; native discovery is unverified.")
        for client in clients)
    files[f"{BUNDLE}/START.md"] = text_bytes(f"""# Start from your task

Read the [project instructions]({posixpath.relpath('AGENTS.md', start_parent)}) and
[Universal operation adapter]({posixpath.relpath(universal_bridge, start_parent)}).
Choose the relevant [plan]({posixpath.relpath(canonical_root + 'skills/plan/SKILL.md', start_parent)}),
[build]({posixpath.relpath(canonical_root + 'skills/build/SKILL.md', start_parent)}),
[review]({posixpath.relpath(canonical_root + 'skills/review/SKILL.md', start_parent)}) or
[resume]({posixpath.relpath(canonical_root + 'skills/resume/SKILL.md', start_parent)}) workflow
by explicit file read if it is not discovered by your host.

## Selected surfaces

{routes}

This is a repository-local source bundle and manual entry, not a plugin activation API.
No hooks, clients, credentials, global configuration or model settings were installed.
Record actual tool/session/version evidence separately. Keep the selected work map and
effective profile reference in package handoffs. Missing independent review stays open.
""")
    # Foundation seed files are user-owned immediately; never upgrade or hash them.
    seeds = {
        "AGENTS.md": text_bytes("""# Repository agent instructions

This repository uses Lintel for planned, reviewable agent sessions. Read
[CORE-PRINCIPLES.md](CORE-PRINCIPLES.md), recent .claude/memory/lessons.md,
.claude/memory/working-state.md and relevant .claude/decisions/ before substantive work.
Keep the current task list in .claude/plans/todo.md. For an initiative, write plan.md,
spec.md and prompt.md under .claude/plans/<initiative>/ and record validation evidence.
Follow existing project instructions in CLAUDE.md when present; surface conflicts.
Customize this file with the project's purpose, ownership, build and test commands.
"""),
        "CLAUDE.md": text_bytes("""# Repository instructions

Project context and ownership live in [AGENTS.md](AGENTS.md). The shared session
protocol below is self-contained and applies to work in this repository.
Add project-specific commands and motivated deviations outside its marked block.
"""),
        "CORE-PRINCIPLES.md": read_file(source, "scaffolding/01-foundation/CORE-PRINCIPLES.md"),
        "EVOLUTION.md": read_file(source, "scaffolding/01-foundation/EVOLUTION.md"),
        ".claude/lintel-layout.yaml": b"layout_version: 5\n",
    }
    for relative in (".claude/memory/lessons.md", ".claude/memory/working-state.md", ".claude/memory/personas.md", ".claude/plans/todo.md", ".claude/decisions/README.md", ".claude/decisions/TEMPLATE.md"):
        seeds[relative] = read_file(source, "scaffolding/01-foundation/" + relative)
    if local:
        seeds = {}  # Lintel already has its foundation; never duplicate it at root.
    return files, seeds, "repository" if local else "vendored"


def load_inventory(target: Path, registry: dict, *, observed: Optional[dict] = None) -> tuple[dict[str, str], dict[str, str], list[str]]:
    data, state = observe_file(target, INVENTORY, {} if observed is None else observed)
    if state is None:
        return {}, {}, []
    if state == NOT_REGULAR:
        raise ValueError(f"Copilot inventory is not a regular file: {INVENTORY}")
    value = json.loads(decoded(data))
    if (not isinstance(value, dict) or type(value.get("schema_version")) is not int
            or value["schema_version"] != SCHEMA or not isinstance(value.get("files"), dict)):
        raise ValueError("Unsupported or malformed Copilot inventory")
    roots = {record["discovery"]["root"] for record in registry["surfaces"].values()
             if record["discovery"]["root"]}
    for relative, sha in value["files"].items():
        safe_path(target, relative)
        native_skill = any(re.fullmatch(re.escape(root) + r"/li-[a-z0-9-]+/SKILL\.md", relative)
                           for root in roots)
        if not (relative.startswith(".github/lintel/") or native_skill or relative.startswith(".github/agents/lintel-") or relative in (".github/copilot-instructions.md", ".github/instructions/lintel-session.instructions.md")):
            raise ValueError(f"Inventory path outside managed namespaces: {relative}")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise ValueError(f"Invalid inventory hash: {relative}")
    blocks = value.get("blocks", {})
    if not isinstance(blocks, dict):
        raise ValueError("Malformed protocol block inventory")
    for relative, sha in blocks.items():
        if relative not in ("AGENTS.md", "CLAUDE.md") or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise ValueError(f"Invalid protocol block inventory: {relative}")
    clients = value.get("clients", ["copilot-cli"])
    if (not isinstance(clients, list) or not clients or not all(isinstance(client, str) for client in clients)
            or len(set(clients)) != len(clients)
            or any(client not in registry["surfaces"] for client in clients)):
        raise ValueError("Malformed adapter client inventory")
    return value["files"], blocks, clients


def protocol_updates(source: Path, target: Path, seeds: dict[str, bytes],
                     old_blocks: dict[str, str], checking: bool, *,
                     observed: Optional[dict] = None) -> tuple[dict[str, bytes], dict[str, str], list[str]]:
    """Manage only marked protocol blocks; preserve all surrounding project prose."""
    observed = {} if observed is None else observed
    payload = read_file(source, "scaffolding/01-foundation/SESSION-PROTOCOL.md").decode("utf-8-sig").strip().encode("utf-8")
    block = PROTOCOL_START + b"\n" + payload + b"\n" + PROTOCOL_END
    updates, hashes, errors = {}, {}, []
    for relative in ("AGENTS.md", "CLAUDE.md"):
        current, state = observe_file(target, relative, observed)
        if state == NOT_REGULAR:
            errors.append(f"Not a regular protocol file: {relative}")
            continue
        original = current if state else seeds[relative]
        starts, ends = original.count(PROTOCOL_START), original.count(PROTOCOL_END)
        if starts == ends == 0:
            if checking:
                errors.append(f"Missing session protocol block: {relative}")
            separator = b"\n" if original.endswith(b"\n") else b"\n\n"
            merged = original + separator + block + b"\n"
        elif starts == ends == 1 and original.index(PROTOCOL_START) < original.index(PROTOCOL_END):
            begin = original.index(PROTOCOL_START)
            end = original.index(PROTOCOL_END) + len(PROTOCOL_END)
            actual = original[begin:end].replace(b"\r\n", b"\n")
            expected = old_blocks.get(relative, digest(block))
            if digest(actual) != expected:
                errors.append(f"Modified session protocol block (preserved): {relative}")
            if checking and actual != block:
                errors.append(f"Outdated session protocol block: {relative}")
            merged = original[:begin] + block + original[end:]
        else:
            errors.append(f"Malformed session protocol markers (preserved): {relative}")
            continue
        updates[relative] = merged
        hashes[relative] = digest(block)
    return updates, hashes, errors


def verify_links(files: dict[str, bytes], target: Path) -> list[str]:
    missing = []
    for relative, data in files.items():
        native_skill = re.fullmatch(r"\.[a-z][a-z0-9-]*/skills/li-[a-z0-9-]+/SKILL\.md", relative)
        bundled_doc = relative.startswith(BUNDLE + "/") and public_document(relative[len(BUNDLE) + 1:])
        if not (native_skill or bundled_doc or relative.startswith(".github/agents/lintel-") or relative in (".github/copilot-instructions.md", ".github/instructions/lintel-session.instructions.md", f"{BUNDLE}/START.md")):
            continue
        if PurePosixPath(relative).suffix.lower() not in (".md", ".html", ".htm"):
            continue
        for _, _, link in document_links(data, markdown=relative.endswith(".md")):
            key = local_link(relative, link)
            if not key:
                continue
            if bundled_doc and not key.startswith(BUNDLE + "/"):
                missing.append(f"Bundled documentation link escapes source: {relative} -> {link}")
                continue
            if key.startswith(BUNDLE + "/"):
                directory = urlsplit(link).path.endswith("/")
                if key not in files and not (directory and any(path.startswith(key + "/") for path in files)):
                    missing.append(f"Missing bundled documentation target: {relative} -> {link}")
            elif key not in files and not native_io_path(safe_path(target, key)).is_file():
                missing.append(f"Missing generated link: {relative} -> {link}")
    return missing


def atomic_write(path: Path, data: bytes) -> None:
    native_io_path(path.parent).mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".lintel-", dir=native_io_path(path.parent))
    temporary = path.parent / Path(tmp).name
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(native_io_path(temporary), native_io_path(path))
    finally:
        if native_io_path(temporary).exists():
            native_io_path(temporary).unlink()


def runtime_ignore_errors(target: Path, ignore_text: str, *, allow_missing_rule: bool = False) -> list[str]:
    """Verify Git before allowing init to repair a missing required rule."""
    has_rule = ".claude/runtime/" in ignore_text.splitlines()
    if native_io_path(target / ".git").exists():
        git = shutil.which("git")
        if not git:
            return [f"Git ignore verification unavailable for {target}: git executable not found"]
        try:
            result = subprocess.run(
                [git, "-c", "core.fsmonitor=false", "-C", str(target), "check-ignore",
                 "--no-index", "--quiet", ".claude/runtime/.lintel-ignore-check"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        except OSError as error:
            return [f"Git ignore verification unavailable for {target}: {error}"]
        if result.returncode not in (0, 1):
            details = b"\n".join(output for output in (result.stderr, result.stdout) if output)
            diagnostic = details.decode("utf-8", errors="replace").strip() or "no diagnostic output"
            return [f"Git ignore verification failed for {target} (exit {result.returncode}): {diagnostic}"]
        if result.returncode == 1 and has_rule:
            return ["Git does not confirm .claude/runtime/ is ignored; review conflicting ignore rules"]
    if not has_rule and not allow_missing_rule:
        return ["Missing .claude/runtime/ ignore rule; run init"]
    return []


def main(universal: bool = False) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "check", "inspect", "recover"))
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--client", action="append", help="Exact surface ID or alias; repeat for a team; no global installation")
    parser.add_argument("--store", type=Path, help="Separate owned recovery store; defaults to a reported target sibling")
    parser.add_argument("--transaction", help="Exact transaction ID for inspect or explicit recovery")
    args = parser.parse_args()
    target_argument = args.target.absolute()
    target = native_io_path(target_argument).resolve()
    if target_argument.anchor == path_identity(target_argument)[0]:
        target = Path(*path_identity(target))
    # Executable-relative source is stable even after copilot-env sets LINTEL_HOME
    # to project runtime storage. A source override is explicit, never ambient.
    source_argument = (args.source or Path(__file__).resolve().parent.parent).absolute()
    source = native_io_path(source_argument).resolve()
    if source_argument.anchor == path_identity(source_argument)[0]:
        source = Path(*path_identity(source))
    if not native_io_path(target).is_dir():
        raise ValueError(f"Target directory does not exist: {target}")
    if target in (Path(target.anchor), Path.home().resolve()):
        raise ValueError("Target must be a project directory, not a filesystem or user-home root")
    store = args.store or (Path(os.environ["LINTEL_RECOVERY_STORE"]) if os.environ.get("LINTEL_RECOVERY_STORE") else None)
    if args.command in ("inspect", "recover") and not args.transaction:
        parser.error("--transaction is required for inspect/recover")
    # Target observations import these joined helpers lazily; an incomplete
    # source must refuse cleanly before the first target read, never crash.
    for relative in ADAPTER_RESOURCES:
        read_file(source, relative)
    if args.command in ("inspect", "recover"):
        from managed_transaction import default_store, inspect_transaction, recover_transaction
        store = store or default_store(target)
        operation = inspect_transaction if args.command == "inspect" else recover_transaction
        print(json.dumps(operation(target, store, args.transaction), indent=2))
        return
    registry = load_registry(native_io_path(safe_path(source, "lib/cli-tiers.yaml")))
    # Every target read that shapes the plan is recorded once; that observation,
    # not a later rebuild, is the only state a planned write may replace.
    observed = {}
    old, old_blocks, old_clients = load_inventory(target, registry, observed=observed)
    if universal and args.command == "init" and not args.client:
        parser.error("--client is required for init; use other for a manual canonical-file handoff")
    requested = [surface_id(registry, client) for client in args.client] if args.client else (
        ["copilot-cli"] if args.command == "init" or not old_clients else [])
    clients = sorted(set(old_clients + requested))
    files, seeds, mode = generate(source, target, tuple(clients))
    from managed_transaction import apply_files, assert_ready, default_store
    store = store or default_store(target)
    assert_ready(target, store)
    errors = []
    block_updates, block_hashes = {}, {}
    if mode == "vendored":
        block_updates, block_hashes, block_errors = protocol_updates(source, target, seeds, old_blocks, args.command == "check",
                                                                     observed=observed)
        errors.extend(block_errors)
    # Preflight this user-owned file too, before any managed content is written.
    ignore_data, ignore_state = observe_file(target, ".gitignore", observed)
    if ignore_state == NOT_REGULAR:
        raise ValueError(".gitignore is not a regular file")
    existing_ignore = decoded(ignore_data) if ignore_state else ""
    if args.command == "init":
        errors.extend(runtime_ignore_errors(target, existing_ignore, allow_missing_rule=True))
    attributes_data, attributes_state = observe_file(target, ".gitattributes", observed)
    if attributes_state == NOT_REGULAR:
        raise ValueError(".gitattributes is not a regular file")
    existing_attributes = decoded(attributes_data) if attributes_state else ""
    # Preserve a team's existing instruction file. A path-scoped additive entry
    # carries the Lintel pointer instead; unowned files are never adopted silently.
    entry = ".github/copilot-instructions.md"
    if observe_file(target, entry, observed)[1] is not None and entry not in old:
        files.pop(entry, None)
    roots = sorted({registry["surfaces"][client]["discovery"]["root"] for client in clients
                    if registry["surfaces"][client]["discovery"]["root"]})
    attribute_rules = [ATTRIBUTES[0]] + [f"{root}/li-*/** text=auto eol=lf" for root in roots]
    if any(registry["surfaces"][client]["discovery"]["kind"] == "copilot" for client in clients):
        attribute_rules.extend(ATTRIBUTES[2:])
    if entry in files:
        attribute_rules.append(".github/copilot-instructions.md text eol=lf")
    for relative in sorted(set(files) | set(old) | set(seeds)):
        state = observe_file(target, relative, observed)[1]
        if state == NOT_REGULAR:
            errors.append(f"Not a regular file: {relative}")
            continue
        if relative in seeds:
            continue
        actual = state["sha256"] if state else None
        if relative in old and actual not in (None, old[relative]):
            errors.append(f"Modified managed file (preserved): {relative}")
        elif relative not in old and actual is not None:
            # Identical generated files may be checked into Lintel before inventory
            # creation; accepting exact bytes never overwrites custom content.
            if relative not in files or actual != digest(files[relative]):
                errors.append(f"Unmanaged collision (preserved): {relative}")
        if args.command == "check":
            if relative in files and actual != digest(files[relative]):
                errors.append(f"Missing or outdated managed file: {relative}")
            if relative in old and relative not in files:
                errors.append(f"Obsolete managed file: {relative}")
    if args.command == "check":
        for relative in seeds:
            if observe_file(target, relative, observed)[1] in (None, NOT_REGULAR):
                errors.append(f"Missing foundation file: {relative}")
        if not old:
            errors.append("Adapter inventory is missing; run init")
        errors.extend(runtime_ignore_errors(target, existing_ignore))
        if any(rule not in existing_attributes.splitlines() for rule in attribute_rules):
            errors.append("Missing adapter .gitattributes rules; run init")
    errors.extend(verify_links({**files, **seeds}, target))
    if errors:
        raise ValueError("\n".join(errors))
    if args.command == "check":
        print(f"Lintel kit verified: {len(files)} managed files; {mode} source; clients={','.join(clients)}; no live-host validation.")
        return
    # The adapter still owns selection and protected-file policy. The shared
    # primitive receives only this fully preflighted, exact byte mutation plan.
    changes = {}
    for relative, data in sorted(files.items()):
        current, state = observe_file(target, relative, observed)
        if state is None or current != data:
            changes[relative] = data
    for relative, data in block_updates.items():
        current, state = observe_file(target, relative, observed)
        if state is None or current != data:
            changes[relative] = data
    for relative, data in seeds.items():
        if observe_file(target, relative, observed)[1] is None and relative not in block_updates:
            changes[relative] = data
    for relative in sorted(set(old) - set(files)):
        if observe_file(target, relative, observed)[1] is not None:
            changes[relative] = None
    if ".claude/runtime/" not in existing_ignore.splitlines():
        separator = "\n" if existing_ignore.endswith("\n") else "\n\n"
        changes[".gitignore"] = (existing_ignore + separator + "# Lintel local session state\n.claude/runtime/\n").encode("utf-8")
    missing_rules = [rule for rule in attribute_rules if rule not in existing_attributes.splitlines()]
    if missing_rules:
        separator = "\n" if existing_attributes.endswith("\n") else "\n\n"
        changes[".gitattributes"] = (existing_attributes + separator + "# Lintel portable adapter kit\n" + "\n".join(missing_rules) + "\n").encode("utf-8")
    inventory = {"schema_version": SCHEMA, "source_mode": mode, "hooks_installed": False,
                 "clients": clients,
                 "blocks": block_hashes,
                 "files": {relative: digest(data) for relative, data in sorted(files.items())}}
    inventory_bytes = text_bytes(json.dumps(inventory, indent=2, sort_keys=True))
    current_inventory, inventory_state = observe_file(target, INVENTORY, observed)
    if inventory_state is None or current_inventory != inventory_bytes:
        changes[INVENTORY] = inventory_bytes
    # Final consumer admission: guards are rechecked here; write expectations are
    # the planning observations, enforced again by unchanged apply_files.
    expected = admitted_expectations(target, observed, changes)
    modes = {relative: None if data is None else expected[relative]["mode"] if expected[relative] else 0o600
             for relative, data in changes.items()}
    result = apply_files(target, store, changes, expected, modes, label="repository adapter publication",
                         final_paths=[INVENTORY] if INVENTORY in changes else [])
    if result["id"]:
        print(f"Verified file transaction: {result['id']}; recovery store: {result['store']}")
    print(f"Lintel kit ready: {len(files)} managed files; {mode} source; clients={','.join(clients)}. Review the managed inventory and foundation diff.")
    print("Start a new host session and inspect its discovery UI, or read .github/lintel/START.md explicitly. No hooks or host permissions were changed.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
