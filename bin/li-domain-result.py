#!/usr/bin/env python3
# component: domain-result-cli
# implements: ADR-0028, ADR-0029, ADR-0031
# intent: .claude/plans/universal-implementation/packages/P09.md
# constraints: trusted source, explicit target/profile paths; data operations only
# last_intent_review: 2026-09-22
"""Validate, publish or freshly inspect non-clearing domain data."""

from __future__ import annotations

import argparse
from pathlib import Path
import stat
import sys

sys.dont_write_bytecode = True
SOURCE = Path(__file__).absolute().parent.parent


def main() -> int:
    if sys.version_info < (3, 9):
        print("ERROR [lintel/domain]: Python 3.9+ is required.", file=sys.stderr)
        return 2
    try:
        helper = SOURCE / "lib/domain_result.py"
        for path in (helper, *helper.parents):
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ImportError("Linked trusted domain helper/ancestor refused")
        if not helper.is_file():
            raise ImportError("Required trusted domain helper is missing")
        sys.path.insert(0, str(SOURCE / "lib"))
        from domain_result import (
            DomainError, ProfileConfig, canonical_json, read_document, record_checkpoint,
            summarize, validate_checkpoint, validate_request, verify_result,
        )
        from profile_context import ProfileError
    except (ImportError, OSError) as error:
        print(f"ERROR [lintel/domain]: trusted source unavailable: {error}", file=sys.stderr)
        return 2

    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "record", "verify", "summary"):
        command = commands.add_parser(name, allow_abbrev=False)
        command.add_argument("--repo", type=Path, required=True)
        command.add_argument("--request", required=name != "validate")
        if name in ("validate", "record"):
            command.add_argument("--file", required=True)
        if name == "record":
            command.add_argument("--output", required=True)
            command.add_argument("--expected-state", required=True,
                                 help="repo-relative JSON containing the original {state: null|P03-state}")
        if name in ("verify", "summary"):
            command.add_argument("--expected", required=True, help="external caller-selected P05 v2 context")
            command.add_argument("--profile-home", type=Path, required=True)
            command.add_argument("--profile-packs", type=Path, required=True)
            command.add_argument("--profile-pointer", type=Path, required=True)
            command.add_argument("--profile-context-file", type=Path)
    args = parser.parse_args()
    try:
        if args.command in ("validate", "record"):
            value, _ = read_document(args.repo, args.file)
            if value.get("kind") == "domain-request":
                if args.command == "record":
                    raise DomainError("The caller constructs requests; record publishes checkpoints/results only")
                validate_request(value)
            else:
                if not args.request:
                    raise DomainError("Checkpoint/result validation requires its explicit request")
                request, _ = read_document(args.repo, args.request)
                validate_checkpoint(value, request)
            if args.command == "validate":
                result = {"operation": "validate", "status": "valid",
                          "verification": "not_performed", "release_clearance": False}
            else:
                if args.output in (args.file, args.request, args.expected_state):
                    raise DomainError("Publication cannot overwrite its inputs")
                state, _ = read_document(args.repo, args.expected_state)
                if set(state) != {"state"}:
                    raise DomainError("Expected file state must be explicit, not inferred")
                result = record_checkpoint(args.repo, args.request, value, output=args.output,
                                           expected_file_state=state["state"])
        else:
            expected, _ = read_document(args.repo, args.expected)
            config = ProfileConfig(
                source=SOURCE, repo=args.repo, home=args.profile_home, packs=args.profile_packs,
                pointer=args.profile_pointer, context_file=args.profile_context_file,
            )
            consume = summarize if args.command == "summary" else verify_result
            result = consume(args.repo, args.request, expected=expected, profile_config=config)
        print(canonical_json(result))
        return 3 if result.get("blocked") else 0
    except (ValueError, OSError, UnicodeError) as error:
        message = f"{error.code}: {error}" if isinstance(error, ProfileError) else str(error)
        if args.command in ("verify", "summary"):
            print(canonical_json({"operation": args.command, "ok": False, "blocked": True,
                                  "status": "error", "verification": "incomplete",
                                  "release_clearance": False, "problems": [message]}))
            return 3
        print(f"ERROR [lintel/domain]: {message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
