#!/usr/bin/env python3
# component: pptx-source-checker
# implements: ADR-0028, ADR-0033
# intent: .claude/plans/v2-findings/plan.md
# constraints: standard-library, bounded read-only ZIP/XML; no extraction or rendering
# last_intent_review: 2026-10-04
"""Check presented slide/notes relationships and literal source retention, not layout."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import io
import json
import os
from pathlib import Path
import posixpath
import re
import stat
import sys
from typing import Iterable
import xml.etree.ElementTree as ET
import zlib
from zipfile import BadZipFile, ZIP_DEFLATED, ZIP_STORED, ZipFile

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"


@dataclass(frozen=True)
class Limits:
    """Positive limits; native read sizes reserve one byte for overflow detection."""

    archive_bytes: int = 32 * 1024 * 1024
    total_bytes: int = 128 * 1024 * 1024
    member_bytes: int = 16 * 1024 * 1024
    xml_bytes: int = 2 * 1024 * 1024
    source_bytes: int = 2 * 1024 * 1024
    entries: int = 4096
    compression_ratio: int = 200

    def __post_init__(self):
        if any(type(value) is not int or value < 1 for value in vars(self).values()):
            raise ValueError("All checker limits must be positive integers")
        if any(getattr(self, name) >= sys.maxsize
               for name in ("archive_bytes", "xml_bytes", "source_bytes")):
            raise ValueError("Read byte limits must leave room within the native read-size limit")


def _read_file(path: Path, limit: int) -> bytes:
    selected = path.lstat()
    if stat.S_ISLNK(selected.st_mode):
        raise ValueError(f"Linked input refused: {path}")
    if not stat.S_ISREG(selected.st_mode) or selected.st_size > limit:
        raise ValueError(f"Input is not a bounded regular file: {path}")
    with path.open("rb") as stream:
        before = os.fstat(stream.fileno())
        if (not stat.S_ISREG(before.st_mode) or before.st_size > limit
                or (before.st_dev, before.st_ino) != (selected.st_dev, selected.st_ino)):
            raise ValueError(f"Input is not a bounded regular file: {path}")
        raw = stream.read(limit + 1)
        fields = ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns")
        # Path and descriptor timestamps can have different precision on Windows.
        after = path.lstat()
        after_open = os.fstat(stream.fileno())
        if (len(raw) > limit or len(raw) != before.st_size
                or any(getattr(after, key) != getattr(selected, key) for key in fields)
                or any(getattr(after_open, key) != getattr(before, key) for key in fields)):
            raise ValueError(f"Input exceeds bound or changed during read: {path}")
    return raw


def _xml(raw: bytes, name: str, root: str) -> ET.Element:
    try:
        text = raw.decode("utf-8-sig")
        if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", text, re.IGNORECASE):
            raise ValueError(f"DTD/entity XML refused: {name}")
        declaration = re.match(r"<\?xml\b[^?]*\bencoding\s*=\s*['\"]([^'\"]+)", text)
        if declaration and declaration[1].lower() not in ("utf-8", "utf8", "us-ascii"):
            raise ValueError(f"Unsupported XML encoding: {name}")
        document = ET.fromstring(text)
    except (UnicodeError, ET.ParseError) as error:
        raise ValueError(f"Malformed or non-UTF-8 XML: {name}") from error
    if document.tag != root:
        raise ValueError(f"Unexpected XML root/namespace: {name}")
    return document


def _local_part(owner: str, link: dict, directory: str) -> str:
    target = link.get("Target", "")
    if link.get("TargetMode", "Internal") != "Internal" or not target or any(
        char in target for char in ("\\", ":", "%", "?", "#", "\x00")
    ) or target.startswith("//"):
        raise ValueError(f"External or malformed relationship from {owner}")
    part = posixpath.normpath(
        target.lstrip("/") if target.startswith("/") else posixpath.join(posixpath.dirname(owner), target))
    if not re.fullmatch(re.escape(directory) + r"/[^/]+\.xml", part):
        raise ValueError(f"Relationship escapes the expected part directory: {owner}")
    return part


def _rel_name(part: str) -> str:
    return posixpath.join(posixpath.dirname(part), "_rels", posixpath.basename(part) + ".rels")


def _text(document: ET.Element) -> str:
    # Runs split words for formatting; spaces belong between paragraphs, not every a:t.
    return "\n".join("".join(
        node.text or "" if node.tag == f"{{{A}}}t" else "\n"
        for node in paragraph.iter() if node.tag in (f"{{{A}}}t", f"{{{A}}}br"))
        for paragraph in document.iter(f"{{{A}}}p"))


def inspect_pptx(path: Path, *, limits: Limits = Limits()) -> dict:
    """Read only presented slides and their one-to-one notes; orphan text is not coverage."""
    path = Path(path)
    raw = _read_file(path, limits.archive_bytes)
    parts, notes, used_notes, used_slides = {}, [], set(), set()
    try:
        with ZipFile(io.BytesIO(raw)) as package:
            entries = package.infolist()
            if not entries or len(entries) > limits.entries:
                raise ValueError("ZIP entry count exceeds bound or archive is empty")
            names, folded, total = {}, set(), 0
            for entry in entries:
                name = entry.filename
                spelling = name[:-1] if name.endswith("/") else name
                if (not spelling or name.startswith("/") or "\\" in name or "\x00" in name
                        or ":" in name or posixpath.normpath(spelling) != spelling
                        or ".." in spelling.split("/") or name.casefold() in folded):
                    raise ValueError(f"Duplicate, aliased or unsafe ZIP member: {name}")
                folded.add(name.casefold())
                names[name] = entry
                total += entry.file_size
                if (entry.flag_bits & 1 or entry.compress_type not in (ZIP_STORED, ZIP_DEFLATED)
                        or stat.S_ISLNK(entry.external_attr >> 16)
                        or entry.file_size > limits.member_bytes or total > limits.total_bytes
                        or entry.file_size > max(1, entry.compress_size) * limits.compression_ratio):
                    raise ValueError(f"Unsupported ZIP member or compressed/uncompressed bound exceeded: {name}")

            def read_xml(name: str, expected_root: str) -> ET.Element:
                entry = names.get(name)
                if entry is None or entry.is_dir():
                    raise ValueError(f"Missing package part: {name}")
                if entry.file_size > limits.xml_bytes:
                    raise ValueError(f"XML read exceeds bound: {name}")
                with package.open(entry) as stream:
                    data = stream.read(limits.xml_bytes + 1)
                if len(data) > limits.xml_bytes or len(data) != entry.file_size:
                    raise ValueError(f"XML size exceeds bound or declared size: {name}")
                return _xml(data, name, expected_root)

            def links(owner: str) -> dict:
                document = read_xml(_rel_name(owner), f"{{{PR}}}Relationships")
                result = {}
                for node in document:
                    ident = node.get("Id", "")
                    if (node.tag != f"{{{PR}}}Relationship" or not ident or ident in result
                            or not node.get("Type") or not node.get("Target")):
                        raise ValueError(f"Malformed or duplicate relationships: {owner}")
                    result[ident] = dict(node.attrib)
                return result

            def one_link(owner: str, kind: str) -> dict:
                selected = [link for link in links(owner).values()
                            if link["Type"].rsplit("/", 1)[-1] == kind]
                if len(selected) != 1 or selected[0]["Type"] != f"{R}/{kind}":
                    raise ValueError(f"Missing, malformed or duplicate {kind} relationship: {owner}")
                return selected[0]

            presentation = read_xml("ppt/presentation.xml", f"{{{P}}}presentation")
            slide_links = links("ppt/presentation.xml")
            slide_ids = presentation.findall(f"./{{{P}}}sldIdLst/{{{P}}}sldId")
            if not slide_ids:
                raise ValueError("Presentation has no slide references")
            used_ids = set()
            for slide_id in slide_ids:
                ident = slide_id.get(f"{{{R}}}id")
                link = slide_links.get(ident)
                if not link or ident in used_ids or link["Type"] != f"{R}/slide":
                    raise ValueError("Missing, malformed or duplicate presented slide relationship")
                used_ids.add(ident)
                slide = _local_part("ppt/presentation.xml", link, "ppt/slides")
                if slide in used_slides:
                    raise ValueError("Aliased presented slide")
                used_slides.add(slide)
                parts[slide] = _text(read_xml(slide, f"{{{P}}}sld"))
                target = _local_part(slide, one_link(slide, "notesSlide"), "ppt/notesSlides")
                if target in used_notes:
                    raise ValueError("Missing or aliased slide notes part")
                used_notes.add(target)
                parts[target] = _text(read_xml(target, f"{{{P}}}notes"))
                backlink = _local_part(target, one_link(target, "slide"), "ppt/slides")
                if backlink != slide:
                    raise ValueError("Notes backlink does not name its owning slide")
                notes.append(parts[target])
    except (BadZipFile, RuntimeError, NotImplementedError, EOFError, zlib.error) as error:
        raise ValueError(f"Malformed or unsupported PPTX archive: {error}") from error
    return {"parts": parts, "notes": notes, "slides": len(used_slides),
            "artifact": {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}}


def document_text(path: Path, *, limits: Limits = Limits()) -> dict[str, str]:
    """OOXML text only; no native reopen, editability or rendered-layout observation."""
    return inspect_pptx(path, limits=limits)["parts"]


def slide_notes(path: Path, *, limits: Limits = Limits()) -> list[str]:
    return inspect_pptx(path, limits=limits)["notes"]


def missing_content(parts: dict[str, str], required: Iterable[str]) -> list[str]:
    """Literal, whitespace-normalized paragraph/cell coverage, not semantic equivalence."""
    texts = [" ".join(text.split()) for text in parts.values()]
    # A fragment must survive within one actual part, not across unrelated slide boundaries.
    return [fragment for fragment in required
            if not any(" ".join(fragment.split()) in text for text in texts)]


def check_pptx(artifact: Path, sources: Iterable[Path], *, limits: Limits = Limits()) -> dict:
    """Check explicit UTF-8 source excerpts: each blank-line-separated paragraph is required.

    Source markup is literal, not silently stripped. For an already classified Markdown
    inventory, callers can pass its full paragraphs/cells to missing_content instead.
    Neither entry point establishes that the caller's inventory covers its complete brief.
    """
    required, references, seen = [], [], set()
    remaining = limits.source_bytes
    for source in sources:
        path = Path(source)
        if path.resolve() in seen:
            raise ValueError("Duplicate source input")
        seen.add(path.resolve())
        raw = _read_file(path, remaining)
        remaining -= len(raw)
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeError as error:
            raise ValueError(f"Source is not UTF-8: {path}") from error
        fragments = [p.strip() for p in re.split(r"\n[ \t]*\n", text.replace("\r\n", "\n")) if p.strip()]
        if not fragments:
            raise ValueError(f"Source is empty: {path}")
        required.extend(fragments)
        references.append({"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
                           "fragments": len(fragments)})
    if not references:
        raise ValueError("At least one explicit source input is required")
    inspected = inspect_pptx(artifact, limits=limits)
    missing = missing_content(inspected["parts"], required)
    return {"status": "fail" if missing else "pass", "inspection": "zip_xml_source_retention",
            "artifact": inspected["artifact"], "sources": references, "slides": inspected["slides"],
            "required_fragments": len(required), "missing": missing, "limits": vars(limits),
            "native_reopen": "unverified", "editability": "unverified", "rendered_layout": "unverified"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--source", type=Path, action="append", required=True,
                        help="UTF-8 retention source; repeat for more sources; paragraphs are literal")
    args = parser.parse_args()
    try:
        result = check_pptx(args.artifact, args.source)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["missing"] else 0
    except (ValueError, OSError) as error:
        print(f"ERROR [lintel/pptx]: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
