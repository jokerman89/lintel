#!/usr/bin/env python3
# component: lintel-events
# implements: ADR-0005, ADR-0008, ADR-0028
# intent: .claude/plans/universal-implementation/packages/P08.md
# constraints: stdlib only; reads explicit files and never writes; absence is unobserved, never a verdict
# last_intent_review: 2026-09-23
"""Structured reader for Lintel audit JSONL, classified through lib/event-catalog.json.

Exit codes, in order of precedence: 2 unreadable file, catalog failure or usage error;
4 at least one line and at least one diagnostic (regardless of filters); 3 absent or
empty file, or nothing left after filtering; 0 at least one selected valid record.
Exits 3 and 4 are data outcomes: callers branch on them instead of running under set -e.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
from pathlib import Path  # noqa: E402
import re  # noqa: E402

SOURCE_ROOT = Path(__file__).resolve().parent.parent
NATIVE_PATHS = SOURCE_ROOT / "lib" / "native_paths.py"
CATALOG = SOURCE_ROOT / "lib" / "event-catalog.json"
SCHEMA_VERSION = 1
REQUIRED_ENVELOPE = ("kind", "operator", "cycle_id")
STRUCTURAL = ("malformed_json", "missing_envelope", "non_string_value")
FORBIDDEN = re.compile(r"\b(healthy|dead|firing|enforced|complete)\b")
TIMESTAMP = re.compile(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(\.\d{1,9})?(Z|[+-]\d{2}:\d{2})")
DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


class ReaderError(Exception):
    """A usage, input or catalog failure: exit 2, never an unobserved result."""


class DuplicateKey(ValueError):
    def __init__(self, key: str):
        super().__init__(key)
        self.key = key


def _load_native_io():
    info = NATIVE_PATHS.lstat() if NATIVE_PATHS.exists() else None
    if info is None or NATIVE_PATHS.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400:
        raise ReaderError(f"trusted path helper missing or linked: {NATIVE_PATHS}")
    spec = importlib.util.spec_from_file_location("lintel_events_native_paths", NATIVE_PATHS)
    if spec is None or spec.loader is None:
        raise ReaderError(f"cannot load trusted path helper: {NATIVE_PATHS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.native_io_path


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def _reject_constant(name):
    raise ValueError(f"non-finite JSON number {name}")


def _strings(value) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def validate_catalog(catalog) -> None:
    def need(condition, message):
        if not condition:
            raise ReaderError(f"event catalog invalid: {message}")

    need(isinstance(catalog, dict), "top level is not an object")
    need(catalog.get("schema_version") == SCHEMA_VERSION, "unsupported schema_version")
    need(isinstance(catalog.get("catalog_version"), int), "catalog_version must be an integer")
    vocabulary = catalog.get("vocabulary", {})
    for name in ("records_when", "class", "check"):
        need(_strings(vocabulary.get(name)), f"vocabulary.{name} must list strings")
    for value in vocabulary["class"] + vocabulary["check"]:
        need(not FORBIDDEN.search(value), f"verdict token in vocabulary value {value!r}")
    categories = catalog.get("categories")
    need(isinstance(categories, dict) and categories, "categories must be a non-empty object")
    for category, meta in categories.items():
        need(isinstance(meta, dict) and isinstance(meta.get("kinds"), dict), f"{category}: kinds must be an object")
        if meta.get("delegated") is not None:
            need(isinstance(meta["delegated"], str) and not meta["kinds"],
                 f"{category}: a delegated category lists no classified kinds")
            continue
        for kind, entry in meta["kinds"].items():
            where = f"{category}/{kind}"
            need(isinstance(entry, dict), f"{where}: entry must be an object")
            need(_strings(entry.get("producers")) and entry["producers"], f"{where}: producers required")
            need(_strings(entry.get("records_when")) and entry["records_when"]
                 and set(entry["records_when"]) <= set(vocabulary["records_when"]), f"{where}: records_when")
            need(_strings(entry.get("fields")), f"{where}: fields must list strings")
            aliases = entry.get("aliases")
            need(isinstance(aliases, dict) and all(_strings(v) and v and set(v) <= set(entry["fields"])
                                                   for v in aliases.values()), f"{where}: aliases")
            rules = entry.get("rules")
            need(isinstance(rules, list) and rules and rules[-1].get("when") == {},
                 f"{where}: rules must end with a default")
            for rule in rules:
                need(isinstance(rule, dict) and isinstance(rule.get("when"), dict), f"{where}: rule shape")
                need(rule.get("class") in vocabulary["class"] and rule.get("check") in vocabulary["check"],
                     f"{where}: rule class/check")
                for field, wanted in rule["when"].items():
                    need(field in entry["fields"], f"{where}: rule field {field} is not catalogued")
                    need(isinstance(wanted, str) or (_strings(wanted) and wanted), f"{where}: rule value")


def load_catalog(native_io, path: Path = CATALOG) -> dict:
    try:
        catalog = json.loads(native_io(path).read_bytes().decode("utf-8"), object_pairs_hook=_pairs,
                             parse_constant=_reject_constant)
    except (OSError, UnicodeError, ValueError) as error:
        raise ReaderError(f"event catalog unavailable: {path}: {error}") from error
    validate_catalog(catalog)
    return catalog


def parse_time(value: str, *, date_only: bool = False):
    match = TIMESTAMP.fullmatch(value)
    try:
        if match:
            year, month, day, hour, minute, second = (int(part) for part in match.groups()[:6])
            fraction, zone = match.group(7), match.group(8)
            micro = int((fraction[1:] + "000000")[:6]) if fraction else 0
            if zone == "Z":
                tz = dt.timezone.utc
            else:
                sign = -1 if zone[0] == "-" else 1
                tz = dt.timezone(sign * dt.timedelta(hours=int(zone[1:3]), minutes=int(zone[4:6])))
            return dt.datetime(year, month, day, hour, minute, second, micro, tzinfo=tz).astimezone(dt.timezone.utc)
        match = DATE.fullmatch(value) if date_only else None
        if match:
            return dt.datetime(*(int(part) for part in match.groups()), tzinfo=dt.timezone.utc)
    except ValueError:
        return None
    return None


def read_source(native_io, path: Path):
    """Return (state, bytes). Only the explicitly named file is ever opened."""
    try:
        target = native_io(path)
        if not target.exists():
            return "absent", None
        if not target.is_file():
            return "unreadable", "not a regular file"
        return "present", target.read_bytes()
    except (OSError, ValueError) as error:
        return "unreadable", str(error)


def classify(entry: dict, fields: dict):
    for rule in entry["rules"]:
        if all(fields.get(field) == wanted if isinstance(wanted, str) else fields.get(field) in wanted
               for field, wanted in rule["when"].items()):
            return rule["class"], rule["check"]
    return None, None


def examine(number, raw, tail, category, meta, kind_filter, since):
    """Classify one physical line; returns (outcome, payload)."""
    def diagnostic(code, detail):
        return "diagnostic", {"line": number, "code": code, "detail": detail}

    if tail:
        return diagnostic("incomplete_tail", "the final line has no newline and may be a partial write")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return diagnostic("malformed_json", "the line is not UTF-8")
    if not text.strip():
        return diagnostic("malformed_json", "blank line")
    try:
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_reject_constant)
    except DuplicateKey as error:
        return diagnostic("duplicate_key", f"key {error.key!r} appears more than once")
    except ValueError:
        return diagnostic("malformed_json", "the line is not a JSON value")
    if not isinstance(value, dict):
        return diagnostic("missing_envelope", "the record is not a JSON object")
    missing = [key for key in REQUIRED_ENVELOPE if key not in value]
    if missing:
        return diagnostic("missing_envelope", "missing " + ", ".join(missing))
    loose = sorted(key for key, item in value.items() if not isinstance(item, str))
    if loose:
        return diagnostic("non_string_value", "non-string value for " + ", ".join(loose))
    kind, delegated = value["kind"], meta.get("delegated")
    entry = meta.get("kinds", {}).get(kind)
    if entry is None and not delegated:
        return diagnostic("unknown_kind", f"kind {kind!r} is not catalogued for category {category!r}")
    stamp = value.get("ts")
    when = parse_time(stamp) if stamp else None
    info = {"undated": when is None, "kind": kind, "when": when}
    if kind_filter is not None and kind != kind_filter:
        return "filtered", info
    if since is not None:
        if when is None:
            return "undated", {"line": number, "code": "undated",
                               "detail": "no usable ts; excluded from the since window and reported"} | info
        if when < since:
            return "filtered", info
    fields = {key: item for key, item in value.items() if key not in ("ts", "kind", "operator", "cycle_id")}
    if delegated:
        row = {"line": number, "category": category, "kind": kind, "ts": stamp, "class": None, "check": None,
               "fields": None, "normalized": None, "delegated": delegated}
    else:
        klass, check = classify(entry, fields)
        normalized = {}
        for name, sources in entry["aliases"].items():
            for source in sources:
                if source in fields:
                    normalized[name] = fields[source]
                    break
        row = {"line": number, "category": category, "kind": kind, "ts": stamp, "class": klass,
               "check": check, "fields": fields, "normalized": normalized}
    return "record", {**info, "row": row}


def analyse(data, category, meta, kind_filter, since):
    counters = {"lines": 0, "valid": 0, "selected": 0, "malformed": 0, "duplicate_key": 0, "unknown_kind": 0,
                "undated": 0, "incomplete_tail": False}
    out, diagnostics, by_kind = [], [], {}
    if not data:
        return counters, out, diagnostics, by_kind
    lines = data.split(b"\n")
    complete = data.endswith(b"\n")
    if complete:
        lines.pop()
    for index, raw in enumerate(lines):
        number = index + 1
        tail = not complete and index == len(lines) - 1
        counters["lines"] += 1
        outcome, payload = examine(number, raw, tail, category, meta, kind_filter, since)
        if outcome == "diagnostic":
            code = payload["code"]
            if code in STRUCTURAL:
                counters["malformed"] += 1
            elif code in ("duplicate_key", "unknown_kind"):
                counters[code] += 1
            elif code == "incomplete_tail":
                counters["incomplete_tail"] = True
            diagnostics.append(payload)
            out.append({"line": number, "diagnostic": code, "detail": payload["detail"]})
            continue
        counters["valid"] += 1
        counters["undated"] += 1 if payload["undated"] else 0
        if outcome == "undated":
            diagnostics.append({key: payload[key] for key in ("line", "code", "detail")})
            out.append({"line": number, "diagnostic": "undated", "detail": payload["detail"]})
            continue
        if outcome == "filtered":
            continue
        counters["selected"] += 1
        row = payload["row"]
        out.append(row)
        item = by_kind.setdefault(row["kind"], {"count": 0, "classes": {}, "first": None, "last": None,
                                                "delegated": row.get("delegated")})
        item["count"] += 1
        if not item["delegated"]:
            pair = (row["class"], row["check"])
            item["classes"][pair] = item["classes"].get(pair, 0) + 1
        if payload["when"] is not None:
            if item["first"] is None or payload["when"] < item["first"][0]:
                item["first"] = (payload["when"], row["ts"])
            if item["last"] is None or payload["when"] >= item["last"][0]:
                item["last"] = (payload["when"], row["ts"])
    return counters, out, diagnostics, by_kind


def summarize_kinds(by_kind):
    result = {}
    for kind, item in sorted(by_kind.items()):
        pairs = item["classes"]
        uniform = next(iter(pairs)) if len(pairs) == 1 else (None, None)
        entry = {"count": item["count"], "class": uniform[0], "check": uniform[1],
                 "first_ts": item["first"][1] if item["first"] else None,
                 "last_ts": item["last"][1] if item["last"] else None}
        if item["delegated"]:
            entry["delegated"] = item["delegated"]
        else:
            entry["breakdown"] = [{"class": klass, "check": check, "count": count}
                                  for (klass, check), count in sorted(pairs.items())]
        result[kind] = entry
    return result


def emit(text: str) -> None:
    sys.stdout.buffer.write(text.encode("utf-8"))
    sys.stdout.buffer.flush()


def build_parser():
    parser = argparse.ArgumentParser(prog="li-events", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("summary", "records"):
        command = sub.add_parser(name)
        command.add_argument("--file", required=True, type=Path)
        command.add_argument("--category")
        command.add_argument("--kind")
        command.add_argument("--since")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(os.path.abspath(args.file))
    category = args.category or (path.name[:-len(".jsonl")] if path.name.endswith(".jsonl") else path.stem)
    summary = {"schema_version": SCHEMA_VERSION, "catalog_version": None,
               "source": {"path": path.as_posix(), "state": "absent"}, "status": "error",
               "records": {"lines": 0, "valid": 0, "selected": 0, "malformed": 0, "duplicate_key": 0,
                           "unknown_kind": 0, "undated": 0, "incomplete_tail": False},
               "by_kind": {}, "diagnostics": [], "evidence": "observed_records_only",
               "verification": "not_performed", "enforcement": "not_established"}
    try:
        since = None
        if args.since is not None:
            since = parse_time(args.since, date_only=True)
            if since is None:
                raise ReaderError(f"--since must be an ISO-8601 date or UTC timestamp: {args.since!r}")
        native_io = _load_native_io()
        state, data = read_source(native_io, path)
        summary["source"]["state"] = state
        catalog = load_catalog(native_io)
        summary["catalog_version"] = catalog["catalog_version"]
        if state == "unreadable":
            raise ReaderError(f"cannot read {path.as_posix()}: {data}")
    except ReaderError as error:
        print(f"li-events: {error}", file=sys.stderr)
        if args.command == "summary":
            summary["error"] = str(error)
            emit(json.dumps(summary, ensure_ascii=False) + "\n")
        return 2
    meta = catalog["categories"].get(category, {"kinds": {}})
    counters, rows, diagnostics, by_kind = analyse(data, category, meta, args.kind, since)
    if diagnostics:
        status, code = "observed_with_diagnostics", 4
    elif counters["selected"] == 0:
        status, code = "unobserved", 3
    else:
        status, code = "observed", 0
    if args.command == "records":
        emit("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
        return code
    summary.update(status=status, records=counters, by_kind=summarize_kinds(by_kind), diagnostics=diagnostics)
    if meta.get("delegated"):
        summary["delegated"] = meta["delegated"]
    emit(json.dumps(summary, ensure_ascii=False) + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
