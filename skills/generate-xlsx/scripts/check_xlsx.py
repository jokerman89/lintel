#!/usr/bin/env python3
# component: workbook-integrity
# implements: ADR-0028, ADR-0029, ADR-0031
# intent: .claude/plans/universal-implementation/packages/P12.md
# constraints: read-only OOXML integrity; no formula evaluation, cache writes or layout clearance
# last_intent_review: 2026-09-22
"""Inspect persisted XLSX cells and compare explicit source/formula/cache expectations."""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path, PurePosixPath
import posixpath
import re
import sys
from typing import Any, Mapping
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile

SOURCE_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SOURCE_ROOT / "lib"))
from context_safety import checked_root, read_owned, selector_path  # noqa: E402
from review_contract import ContractError, load_json  # noqa: E402

S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"s": S}
MAX_INPUT = 64 * 1024 * 1024
MAX_PART = 16 * 1024 * 1024
MAX_UNPACKED = 64 * 1024 * 1024


class WorkbookError(ValueError):
    """Invalid or unsupported input; never a verified workbook result."""


def _part_name(name: str) -> str:
    path = PurePosixPath(name)
    if not name or path.is_absolute() or name != path.as_posix() or ".." in path.parts \
            or "\\" in name or ":" in name:
        raise WorkbookError(f"Invalid package part: {name!r}")
    return name


def _target(base: str, target: str) -> str:
    if not target or "\\" in target or ":" in target or "#" in target or "%" in target:
        raise WorkbookError(f"Unsupported relationship target: {target!r}")
    resolved = target.lstrip("/") if target.startswith("/") else posixpath.join(posixpath.dirname(base), target)
    return _part_name(posixpath.normpath(resolved))


def _cell_address(value: str) -> str:
    match = re.fullmatch(r"([A-Z]{1,3})([1-9][0-9]{0,6})", value or "")
    if not match:
        raise WorkbookError(f"Invalid cell address: {value!r}")
    column = 0
    for char in match[1]:
        column = column * 26 + ord(char) - ord("A") + 1
    if column > 16384 or int(match[2]) > 1048576:
        raise WorkbookError(f"Cell outside worksheet bounds: {value}")
    return value


def _xml(data: bytes, name: str) -> ET.Element:
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise WorkbookError(f"DTD/entities are unsupported: {name}")
    try:
        return ET.fromstring(data)
    except ET.ParseError as error:
        raise WorkbookError(f"Malformed XML in {name}: {error}") from error


def _decimal(value: Any) -> Decimal:
    if not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", str(value)):
        raise WorkbookError(f"Invalid numeric cell/cache: {value!r}")
    try:
        number = Decimal(str(value))
    except InvalidOperation as error:
        raise WorkbookError(f"Invalid numeric cell/cache: {value!r}") from error
    if not number.is_finite():
        raise WorkbookError(f"Non-finite cell/cache: {value!r}")
    return number


def _text(element: ET.Element) -> str:
    if element.find(".//s:rPh", NS) is not None:
        raise WorkbookError("Phonetic string annotations need an explicit text reader")
    return "".join(node.text or "" for node in element.findall(".//s:t", NS))


def inspect_workbook(data: bytes) -> dict[str, Any]:
    """Read all worksheets, including hidden ones; never calculate or mutate bytes."""
    if not isinstance(data, bytes) or len(data) > MAX_INPUT:
        raise WorkbookError("XLSX input must be bytes within the 64 MiB inspection bound")
    try:
        with ZipFile(BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > 10000 or sum(entry.file_size for entry in entries) > MAX_UNPACKED:
                raise WorkbookError("Package exceeds the declared inspection bounds")
            names = [entry.filename for entry in entries if not entry.is_dir()]
            if len(names) != len(set(names)):
                raise WorkbookError("Duplicate package part")
            parts = {}
            for entry in entries:
                if entry.is_dir():
                    continue
                name = _part_name(entry.filename)
                if entry.file_size > MAX_PART or entry.flag_bits & 1:
                    raise WorkbookError(f"Oversized or encrypted package part: {name}")
                lower = name.lower()
                if "vbaproject" in lower or "/embeddings/" in lower or "/externallinks/" in lower:
                    raise WorkbookError(f"Macros, embedded objects and external workbooks are not allowed: {name}")
                parts[name] = archive.read(entry)
    except (BadZipFile, RuntimeError, NotImplementedError) as error:
        raise WorkbookError(f"Unreadable XLSX package: {error}") from error
    relationships = {}
    for name, value in parts.items():
        if name.endswith(".rels"):
            root = _xml(value, name)
            if root.tag != f"{{{P}}}Relationships":
                raise WorkbookError(f"Unexpected relationship namespace: {name}")
            by_id = {}
            for relation in root:
                identifier = relation.get("Id")
                if relation.tag != f"{{{P}}}Relationship" or not identifier or identifier in by_id:
                    raise WorkbookError(f"Invalid or duplicate relationship: {name}")
                if relation.get("TargetMode", "Internal") != "Internal":
                    raise WorkbookError(f"External relationship is not permitted: {name}")
                by_id[identifier] = relation.attrib
            relationships[name] = by_id
    roots = [item for item in relationships.get("_rels/.rels", {}).values()
             if item.get("Type") == R + "/officeDocument"]
    if len(roots) != 1:
        raise WorkbookError("Exactly one workbook root relationship is required")
    workbook_name = _target("", roots[0].get("Target", ""))
    if workbook_name not in parts:
        raise WorkbookError("Workbook part is missing")
    workbook = _xml(parts[workbook_name], workbook_name)
    if workbook.tag != f"{{{S}}}workbook":
        raise WorkbookError("Unsupported workbook namespace")
    rel_name = posixpath.join(posixpath.dirname(workbook_name), "_rels", posixpath.basename(workbook_name) + ".rels")
    links = relationships.get(rel_name, {})
    string_links = [item for item in links.values() if item.get("Type") == R + "/sharedStrings"]
    if len(string_links) > 1:
        raise WorkbookError("Multiple shared-string parts")
    strings = []
    if string_links:
        name = _target(workbook_name, string_links[0].get("Target", ""))
        if name not in parts:
            raise WorkbookError("Shared-string part is missing")
        table = _xml(parts[name], name)
        strings = [_text(item) for item in table.findall("s:si", NS)]
    sheets, cells, seen_parts, seen_names = [], [], set(), set()
    for sheet in workbook.findall("s:sheets/s:sheet", NS):
        name, identifier = sheet.get("name"), sheet.get(f"{{{R}}}id")
        if not name or name.casefold() in seen_names or identifier not in links:
            raise WorkbookError("Missing, duplicate or unbound worksheet")
        relation = links[identifier]
        if relation.get("Type") != R + "/worksheet":
            raise WorkbookError(f"Unsupported sheet kind: {name}")
        part = _target(workbook_name, relation.get("Target", ""))
        if part not in parts or part in seen_parts:
            raise WorkbookError(f"Missing or aliased worksheet part: {name}")
        seen_parts.add(part)
        seen_names.add(name.casefold())
        sheets.append({"name": name, "state": sheet.get("state", "visible"), "part": part})
        document = _xml(parts[part], part)
        if document.tag != f"{{{S}}}worksheet":
            raise WorkbookError(f"Unsupported worksheet namespace: {name}")
        addresses = set()
        for cell in document.findall("s:sheetData/s:row/s:c", NS):
            address = _cell_address(cell.get("r", ""))
            if address in addresses:
                raise WorkbookError(f"Duplicate cell: {name}!{address}")
            addresses.add(address)
            formulas = cell.findall("s:f", NS)
            values = cell.findall("s:v", NS)
            if len(formulas) > 1 or len(values) > 1:
                raise WorkbookError(f"Ambiguous formula/value: {name}!{address}")
            formula = formulas[0] if formulas else None
            value = values[0].text if values else None
            kind = cell.get("t", "n")
            cache_present = value is not None
            if formula is not None and not cache_present:
                parsed, value_type = None, "empty"
            elif kind == "inlineStr":
                inline = cell.find("s:is", NS)
                if inline is None or formula is not None:
                    raise WorkbookError(f"Invalid inline string: {name}!{address}")
                parsed, value_type = _text(inline), "text"
            elif kind == "s":
                if value is None or not re.fullmatch(r"[0-9]+", value) or int(value) >= len(strings):
                    raise WorkbookError(f"Invalid shared-string index: {name}!{address}")
                parsed, value_type = strings[int(value)], "text"
            elif value is None:
                parsed, value_type = None, "empty"
            elif kind == "n":
                _decimal(value)
                parsed, value_type = value, "number"
            elif kind == "b":
                if value not in ("0", "1"):
                    raise WorkbookError(f"Invalid boolean: {name}!{address}")
                parsed, value_type = value == "1", "bool"
            elif kind in ("str", "e"):
                parsed, value_type = value, "text" if kind == "str" else "error"
            else:
                raise WorkbookError(f"Unsupported cell type {kind}: {name}!{address}")
            cells.append({
                "sheet": name, "cell": address, "formula": (formula.text or "") if formula is not None else None,
                "formula_attributes": dict(formula.attrib) if formula is not None else {},
                "type": value_type, "value": parsed, "stored_type": kind,
                "cache_present": cache_present if formula is not None else None,
            })
    if not sheets:
        raise WorkbookError("Workbook has no worksheets")
    return {"workbook_sha256": hashlib.sha256(data).hexdigest(), "sheets": sheets, "cells": cells}


def _expectations(expected: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(expected, dict) or set(expected) - {"cells", "required_text"} \
            or not isinstance(expected.get("cells"), list) or not expected["cells"]:
        raise WorkbookError("Expectations need a nonempty cells list and optional required_text")
    required_text = expected.get("required_text", [])
    if not isinstance(required_text, list) or any(not isinstance(s, str) or not s for s in required_text):
        raise WorkbookError("required_text must contain nonempty exact source segments")
    seen = set()
    for item in expected["cells"]:
        if not isinstance(item, dict) or set(item) != {"sheet", "cell", "formula", "type", "value"}:
            raise WorkbookError("Each expected cell needs sheet, cell, formula, type and value")
        if not isinstance(item["sheet"], str) or not item["sheet"]:
            raise WorkbookError("Expected sheet name is required")
        _cell_address(item["cell"])
        key = (item["sheet"], item["cell"])
        if key in seen:
            raise WorkbookError(f"Duplicate expected cell: {key}")
        seen.add(key)
        formula = item["formula"]
        if formula is not None and (not isinstance(formula, str) or not formula.lstrip("=")):
            raise WorkbookError("Expected formula must be nonempty text or null")
        value = item["value"]
        valid = {
            "number": type(value) is int or type(value) is float and math.isfinite(value),
            "text": isinstance(value, str), "bool": type(value) is bool, "empty": value is None,
        }
        if not isinstance(item["type"], str) or not valid.get(item["type"], False):
            raise WorkbookError("Expected cell type/value disagree")
    return expected["cells"]


def check_workbook(data: bytes, expected: Mapping[str, Any]) -> dict[str, Any]:
    """Compare persisted values with a supplied oracle; this is not execution evidence."""
    wanted = _expectations(expected)
    workbook = inspect_workbook(data)
    actual = {(cell["sheet"], cell["cell"]): cell for cell in workbook["cells"]}
    selected = {(cell["sheet"], cell["cell"]) for cell in wanted}
    issues = []

    def issue(code: str, status: str, location: str, detail: str) -> None:
        issues.append({"code": code, "status": status, "location": location, "detail": detail})

    for key, cell in actual.items():
        if cell["formula"] is not None and key not in selected:
            issue("unselected_formula", "fail", "!".join(key), "Formula lacks an explicit expected result")
        if cell["type"] == "error":
            issue("formula_error", "fail", "!".join(key), str(cell["value"]))
    for item in wanted:
        key = (item["sheet"], item["cell"])
        location = "!".join(key)
        cell = actual.get(key)
        if cell is None:
            issue("cell_missing", "fail", location, "Expected cell is absent")
            continue
        normalize = lambda text: text[1:] if isinstance(text, str) and text.startswith("=") else text
        if normalize(cell["formula"]) != normalize(item["formula"]):
            issue("formula_mismatch", "fail", location, "Formula text or literal/formula distinction changed")
        if cell["formula_attributes"]:
            issue("unsupported_formula", "unverified", location, "Shared/array/table formula semantics need another reader")
            continue
        if cell["formula"] is not None and not cell["cache_present"]:
            issue("cache_missing", "unverified", location, "No nonempty persisted formula cache; live calculation is separate")
            continue
        if cell["type"] != item["type"]:
            issue("type_mismatch", "fail", location, f"Expected {item['type']}, persisted {cell['type']}")
        elif item["type"] == "number":
            if _decimal(cell["value"]) != _decimal(item["value"]):
                issue("value_mismatch", "fail", location, "Persisted numeric value differs from the independent expected value")
        elif cell["value"] != item["value"]:
            issue("value_mismatch", "fail", location, "Persisted value differs from source/expected value")
    texts = [cell["value"] for cell in workbook["cells"] if cell["type"] == "text" and cell["formula"] is None]
    for segment in expected.get("required_text", []):
        if not any(segment in text for text in texts):
            issue("source_missing", "fail", "source", "Required source segment missing: " + segment[:100])
    status = "fail" if any(item["status"] == "fail" for item in issues) else "unverified" if issues else "pass"
    return {
        "status": status, "workbook_sha256": workbook["workbook_sha256"],
        "layer": "persisted-ooxml-integrity", "issues": issues,
        "selected_cells": len(wanted), "formula_cells": sum(c["formula"] is not None for c in workbook["cells"]),
        "calculation_execution_verified": False, "rendered_layout_verified": False, "release_clearance": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Explicit authorized local artifact root")
    parser.add_argument("--workbook", required=True, help="Workbook path relative to root")
    parser.add_argument("--expect", required=True, help="Expectation JSON path relative to root")
    args = parser.parse_args()
    try:
        root = checked_root(args.root)
        data, _ = read_owned(root, selector_path(args.workbook), max_bytes=MAX_INPUT)
        expectations, _ = read_owned(root, selector_path(args.expect), max_bytes=MAX_PART)
        result = check_workbook(data, load_json(expectations.decode("utf-8-sig")))
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
        return 0 if result["status"] == "pass" else 3
    except (WorkbookError, ContractError, OSError, ValueError, TypeError) as error:
        print(json.dumps({"status": "error", "detail": str(error), "release_clearance": False}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
