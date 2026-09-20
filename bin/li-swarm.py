#!/usr/bin/env python3
# component: swarm-cli
# implements: ADR-0026, ADR-0027
# intent: .claude/plans/swarming-work/spec.md
# constraints: read-only; standard library only; never executes artifact content
# last_intent_review: 2026-09-08
"""Read-only validation and evidence gates for a Lintel swarm."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))

from swarm_contract import (  # noqa: E402
    ValidationResult,
    check_lane_scope,
    lane_states,
    load_swarm_contract,
    ready_frontier,
    validate_coordination,
    verify_close,
)


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="working repository root")
    parser.add_argument("--coord", required=True, help="repository-relative coordination.json path")


def _emit(result: ValidationResult, **payload: object) -> int:
    output = result.as_dict()
    output.update(payload)
    print(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if result.ok else 1


def _changed_paths(args: argparse.Namespace) -> list[str]:
    paths = list(args.changed or [])
    if args.paths_file:
        if args.paths_file == "-":
            content = sys.stdin.read()
        else:
            content = Path(args.paths_file).read_text(encoding="utf-8-sig")
        paths.extend(line for line in content.splitlines() if line != "")
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate topology and ownership")
    _common(validate_parser)

    wave_parser = subparsers.add_parser("wave", help="show the next evidence-aware ready frontier")
    _common(wave_parser)

    status_parser = subparsers.add_parser("status", help="show lane evidence states")
    _common(status_parser)

    verify_parser = subparsers.add_parser("verify", help="fail unless every lane has complete independent evidence")
    _common(verify_parser)

    scope_parser = subparsers.add_parser("check-scope", help="validate one attributable lane change set")
    _common(scope_parser)
    scope_parser.add_argument("--task", required=True, help="lane task_id")
    scope_parser.add_argument("--changed", action="append", help="one repository-relative changed path; repeat as needed")
    scope_parser.add_argument("--paths-file", help="newline-delimited paths, or - for stdin")

    args = parser.parse_args()
    try:
        if args.command == "validate":
            result = validate_coordination(args.repo, args.coord)
            return _emit(result)
        if args.command == "wave":
            result, frontier = ready_frontier(args.repo, args.coord)
            return _emit(result, frontier=frontier)
        if args.command == "status":
            result = validate_coordination(args.repo, args.coord)
            states = []
            if result.ok and result.contract is not None:
                states, evidence = lane_states(args.repo, result.contract)
                result.diagnostics.extend(evidence)
            return _emit(result, lanes=states)
        if args.command == "verify":
            result, states = verify_close(args.repo, args.coord)
            return _emit(result, lanes=states)
        if args.command == "check-scope":
            result = check_lane_scope(args.repo, args.coord, args.task, _changed_paths(args))
            return _emit(result, task_id=args.task)
    except (OSError, UnicodeError) as error:
        print(json.dumps({"ok": False, "diagnostics": [{"severity": "error", "code": "io", "path": "", "message": str(error)}]}, indent=2), file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
