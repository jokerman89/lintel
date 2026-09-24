#!/usr/bin/env python3
# component: installed-catalog-read-observer
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/packages/P13.md
# constraints: test-only Path read observation; no model/client or enforcement claim
# last_intent_review: 2026-09-24
"""Observe an installed selection before a chosen body; expose a deliberately bad read."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--trace", required=True, type=Path)
    parser.add_argument("--inject-unrelated", action="store_true")
    args = parser.parse_args()
    if any(key.startswith("LINTEL_") for key in os.environ):
        parser.error("LINTEL selectors must be absent")
    source = args.source.resolve(strict=True)
    support = load("catalog_test_observer", ROOT / "tests/unit/catalog-metadata.py")
    catalog = load("installed_catalog_observed", source / "bin/li-catalog.py")
    allowed, headers, events = set(), [], []
    original_header = catalog.frontmatter
    unrelated = source / "agents/doc-gen/PPTNarrativeArchitect.md"

    def header(path):
        headers.append(str(path))
        if args.inject_unrelated:
            unrelated.read_text(encoding="utf-8")
        return original_header(path)

    catalog.frontmatter = header
    trace = {
        "scope": "Test-owned Path.read_text/read_bytes observation; automatic model context unobserved",
        "source": str(source), "injected_whole_body_read": args.inject_unrelated,
        "header_calls": headers, "events": events,
    }
    try:
        with support.observe_prompt_bodies(allowed) as bodies:
            trace["body_reads"] = bodies
            value = catalog.selection_metadata(
                source, ["demo-script"], kind="agent", name="DemoNarrativeArc",
            )
            events.append({"operation": "metadata-complete", "ids": [entry["id"] for entry in value["entries"]]})
            if value["matched"] != 1 or value["entries"][0]["id"] != "agent:DemoNarrativeArc":
                raise AssertionError("Installed literal selection did not identify the required method")
            selected = catalog.source_path(source, value["entries"][0]["path"])
            allowed.add(selected.resolve())
            body = selected.read_bytes()
            events.append({"operation": "selected-body", "path": str(selected),
                           "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)})
            trace["metadata"] = value
    except AssertionError as error:
        trace["result"] = "refused"
        trace["diagnostic"] = str(error)
        with args.trace.open("x", encoding="utf-8") as handle:
            json.dump(trace, handle, indent=2)
        print(str(error), file=sys.stderr)
        return 3
    trace["result"] = "observed"
    with args.trace.open("x", encoding="utf-8") as handle:
        json.dump(trace, handle, indent=2)
    print(json.dumps({"selected": value["entries"][0]["id"],
                      "body_sha256": events[-1]["sha256"], "executed_role": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
