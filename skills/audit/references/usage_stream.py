# component: audit-usage-stream
# implements: ADR-0008, ADR-0034
# intent: skills/audit/references/usage.md
# constraints: read-only explicit source; reuse event parser; bounded scan, rows and aggregates
# last_intent_review: 2026-10-09
"""Bound usage reporting without replacing the shared event schema or classifier."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from decimal import Decimal, InvalidOperation
import importlib.util
import json
import os
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[3]
MAX_BYTES = 8 * 1024 * 1024
MAX_LINES = 100000
MAX_LINE = 64 * 1024
MAX_SKILLS = 1024
MAX_DETAILS = 50
MAX_DETAIL_BYTES = 64 * 1024


def legacy_summary(events, display):
    """The li-events.py summary contract; streaming fields are added beside it, never instead."""
    return {"schema_version": events.SCHEMA_VERSION, "catalog_version": None,
            "source": {"path": display, "state": "absent"}, "status": "error",
            "records": {"lines": 0, "valid": 0, "selected": 0, "malformed": 0, "duplicate_key": 0,
                        "unknown_kind": 0, "undated": 0, "incomplete_tail": False},
            "by_kind": {}, "diagnostics": [], "evidence": "observed_records_only",
            "verification": "not_performed", "enforcement": "not_established"}


def source_state(native_io, path):
    """Classify the named source like li-events.read_source without reading its bytes."""
    try:
        target = native_io(path)
        if not target.exists():
            return "absent", target, None
        if not target.is_file():
            return "unreadable", target, "not a regular file"
        return "present", target, None
    except (OSError, ValueError) as error:
        return "unreadable", None, str(error)


def report(args, events, native_io, summary, display):
    since = None
    if args.since is not None:
        since = events.parse_time(args.since, date_only=True)
        if since is None:
            raise events.ReaderError(f"--since must be an ISO-8601 date or UTC timestamp: {args.since!r}")
    state, path, problem = source_state(native_io, Path(display))
    summary["source"]["state"] = state
    catalog = events.load_catalog(native_io)
    summary["catalog_version"] = catalog["catalog_version"]
    if state == "unreadable":
        raise events.ReaderError(f"cannot read {display}: {problem}")
    meta = catalog["categories"].get("usage-skill", {"kinds": {}})
    counters = {"lines": 0, "valid": 0, "selected": 0, "malformed": 0,
                "duplicate_key": 0, "unknown_kind": 0, "undated": 0, "incomplete_tail": False}
    diagnostics, preview, skills, diagnostic_codes, by_kind = [], [], {}, {}, {}
    diagnostic_count = bytes_read = detail_bytes = detail_count = 0
    complete = True
    aggregate_complete = True
    oversized_detail = False

    def diagnose(line, code, detail):
        nonlocal diagnostic_count, aggregate_complete
        diagnostic_count += 1
        aggregate_complete = False
        diagnostic_codes[code] = diagnostic_codes.get(code, 0) + 1
        item = {"line": line, "code": code, "detail": detail[:512]}
        if len(diagnostics) < MAX_DETAILS:
            diagnostics.append(item)
        return item

    def detail(item):
        nonlocal detail_bytes, detail_count
        detail_count += 1
        size = len(json.dumps(item).encode("utf-8"))
        if len(preview) < min(args.limit, MAX_DETAILS) and detail_bytes + size <= MAX_DETAIL_BYTES:
            preview.append(item)
            detail_bytes += size

    if state == "present":
        with path.open("rb") as stream:
            initial = path.stat()
            while True:
                remaining = MAX_BYTES - bytes_read
                if remaining == 0 or counters["lines"] == MAX_LINES:
                    if stream.tell() < path.stat().st_size:
                        complete = False
                        diagnose(counters["lines"], "processing_bound",
                                 "scan bound reached; remaining input and totals are incomplete")
                    break
                raw = stream.readline(min(MAX_LINE + 1, remaining))
                if not raw:
                    break
                bytes_read += len(raw)
                counters["lines"] += 1
                number = counters["lines"]
                if len(raw) > MAX_LINE or (not raw.endswith(b"\n") and bytes_read == MAX_BYTES
                                          and stream.tell() < path.stat().st_size):
                    diagnose(number, "oversized_line", "line exceeds bounded parser input; not materialized")
                    aggregate_complete = False
                    oversized_detail = True
                    # Drain the same physical line in bounded chunks, never join it.
                    while not raw.endswith(b"\n") and bytes_read < MAX_BYTES:
                        raw = stream.readline(min(MAX_LINE, MAX_BYTES - bytes_read))
                        if not raw:
                            break
                        bytes_read += len(raw)
                    if not raw.endswith(b"\n") and stream.tell() == path.stat().st_size:
                        counters["incomplete_tail"] = True
                        diagnose(number, "incomplete_tail", "oversized final line has no terminating newline")
                    continue
                outcome, payload = events.examine(
                    number, raw.rstrip(b"\n"), not raw.endswith(b"\n"),
                    "usage-skill", meta, args.kind, since)
                if outcome in ("diagnostic", "undated"):
                    code = payload["code"]
                    if code in events.STRUCTURAL:
                        counters["malformed"] += 1
                    elif code in ("duplicate_key", "unknown_kind"):
                        counters[code] += 1
                    elif code == "incomplete_tail":
                        counters["incomplete_tail"] = True
                    if outcome == "undated":
                        counters["valid"] += 1
                        counters["undated"] += 1
                    diagnose(number, code, payload["detail"])
                    detail({"line": number, "diagnostic": code, "detail": payload["detail"][:512]})
                    continue
                counters["valid"] += 1
                counters["undated"] += int(payload["undated"])
                if outcome == "filtered":
                    continue
                counters["selected"] += 1
                row = payload["row"]
                detail(row)
                # Same per-kind classification fold as li-events.analyse, one row at a time.
                item = by_kind.setdefault(row["kind"], {"count": 0, "classes": {}, "first": None,
                                                        "last": None, "delegated": row.get("delegated")})
                item["count"] += 1
                if not item["delegated"]:
                    pair = (row["class"], row["check"])
                    item["classes"][pair] = item["classes"].get(pair, 0) + 1
                if payload["when"] is not None:
                    if item["first"] is None or payload["when"] < item["first"][0]:
                        item["first"] = (payload["when"], row["ts"])
                    if item["last"] is None or payload["when"] >= item["last"][0]:
                        item["last"] = (payload["when"], row["ts"])
                fields = row["fields"] or {}
                skill = fields.get("skill")
                if not skill:
                    diagnose(number, "missing_skill", "missing or empty fields.skill; excluded from aggregates")
                    aggregate_complete = False
                    continue
                if len(skill) > 256 or (skill not in skills and len(skills) == MAX_SKILLS):
                    diagnose(number, "skill_bound", "skill length/cardinality bound; aggregates incomplete")
                    aggregate_complete = False
                    continue
                aggregate = skills.setdefault(skill, {"count": 0, "tokens_est": Decimal(0)})
                aggregate["count"] += 1
                value = fields.get("tokens_est")
                if value is not None:
                    try:
                        if len(value) > 64:
                            raise InvalidOperation
                        token = Decimal(value)
                        if not token.is_finite() or abs(token) > Decimal("1e18"):
                            raise InvalidOperation
                        aggregate["tokens_est"] += token
                    except InvalidOperation:
                        diagnose(number, "invalid_tokens_est", "token estimate is not bounded numeric input")
                        aggregate_complete = False
                else:
                    diagnose(number, "missing_tokens_est", "token estimate not observed; totals incomplete")
                    aggregate_complete = False
            final = path.stat()
            if (initial.st_size, initial.st_mtime_ns) != (final.st_size, final.st_mtime_ns):
                complete = False
                diagnose(counters["lines"], "source_changed",
                         "source changed during scan; observations are not an atomic snapshot")
    top = sorted(skills, key=lambda skill: (-skills[skill]["count"], skill))[:args.topn]
    summary.update({
        "status": ("observed_with_diagnostics" if diagnostic_count else
                   "observed" if counters["selected"] else "unobserved"),
        "records": counters, "by_kind": events.summarize_kinds(by_kind), "diagnostics": diagnostics,
        "category": "usage-skill",
        "window": {"since": args.since, "kind": args.kind},
        "diagnostic_count": diagnostic_count,
        "diagnostic_codes": diagnostic_codes,
        "diagnostics_omitted": diagnostic_count - len(diagnostics),
        "processing": {"bytes_read": bytes_read, "complete": complete,
                       "detail_incomplete": oversized_detail or detail_count > len(preview) or not complete,
                       "preview_rows": len(preview), "preview_bytes": detail_bytes,
                       "max_bytes": MAX_BYTES, "max_lines": MAX_LINES, "max_line_bytes": MAX_LINE},
        "usage": {"aggregate_complete": complete and aggregate_complete and bool(counters["selected"]),
                  "by_skill": {skill: {"count": skills[skill]["count"],
                                      "tokens_est": str(skills[skill]["tokens_est"])} for skill in top},
                  "skills_observed": len(skills), "topn": args.topn},
    })
    if meta.get("delegated"):
        summary["delegated"] = meta["delegated"]
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Preview: at most {min(args.limit, MAX_DETAILS)} rows; bounded details, not all input.")
    for item in preview:
        print(json.dumps(item))
    return 4 if diagnostic_count else 0 if counters["selected"] else 3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--kind")
    parser.add_argument("--since")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--topn", type=int, default=20)
    args = parser.parse_args()
    if args.limit < 1 or not 1 <= args.topn <= MAX_DETAILS:
        parser.error("limit must be positive and topn must be between 1 and 50")
    spec = importlib.util.spec_from_file_location("lintel_usage_events", SOURCE / "bin/li-events.py")
    if spec is None or spec.loader is None:
        print("audit usage: trusted event reader unavailable", file=sys.stderr)
        return 2
    events = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(events)
    display = Path(os.path.abspath(args.file)).as_posix()
    summary = legacy_summary(events, display)
    try:
        return report(args, events, events._load_native_io(), summary, display)
    except (events.ReaderError, OSError, ValueError, RecursionError) as error:
        print(f"audit usage: {error}", file=sys.stderr)
        # Matches li-events summary: a parseable error summary, never a partial row dump.
        summary["status"] = "error"
        summary["error"] = str(error)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
