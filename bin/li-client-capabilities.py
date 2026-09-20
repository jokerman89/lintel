#!/usr/bin/env python3
# component: client-capabilities-cli
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/spec.md
# constraints: read-only, stdlib, no host calls or permission changes
# last_intent_review: 2026-09-20
"""Validate source claims or select operations from actual caller-inspected session bindings."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from client_capabilities import (DEFAULT_REGISTRY, compatibility_field, describe,
                                 load_registry, markdown_table, read_json, resolve, surface_id)


def main() -> None:
    sys.stdout.reconfigure(newline="\n")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "list", "show", "resolve", "normalize", "field", "table"))
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--client")
    parser.add_argument("--field")
    parser.add_argument("--session", type=Path)
    args = parser.parse_args()
    registry = load_registry(args.registry)
    if args.command in ("show", "normalize", "field") and not args.client:
        parser.error("--client is required")
    if args.command == "resolve" and not args.session:
        parser.error("--session is required")
    if args.command == "field" and not args.field:
        parser.error("--field is required")
    if args.command == "list":
        print("\n".join(registry["surfaces"]))
    elif args.command == "table":
        print(markdown_table(registry))
    elif args.command == "field":
        if args.client not in registry["surfaces"] and args.client not in registry["aliases"]:
            print(f"WARNING: unknown surface {args.client!r}; returning manual compatibility hints only.", file=sys.stderr)
        print(compatibility_field(registry, args.client, args.field))
    elif args.command == "normalize":
        print(surface_id(registry, args.client))
    else:
        result = (describe(registry, args.client) if args.command == "show" else
                  resolve(registry, read_json(args.session)) if args.command == "resolve" else
                  {"schema_version": 2, "surfaces": len(registry["surfaces"]),
                   "status": "valid", "live_host_validation": False})
        print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
