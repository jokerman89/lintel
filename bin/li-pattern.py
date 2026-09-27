#!/usr/bin/env python3
# component: reusable-patterns-cli
# implements: ADR-0038
# intent: .claude/plans/reusable-patterns/contract.md
# constraints: stdlib only; data-only; prints JSON reports; never executes pattern content, fetches URLs or writes in P1 commands
# last_intent_review: 2026-09-28
"""Deterministic pattern validation and resolution; the launcher supplies resolved roots.

Exit codes: 0 ok/ready/empty, 2 invalid, 3 needs-context, 4 conflict, 5 unavailable,
6 write collision, 7 unmet review requirement. Reports go to stdout, concise
diagnostics to stderr. See .claude/plans/reusable-patterns/contract.md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import patterns as p  # noqa: E402


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise p.PatternError("invalid_arguments", message)


def _input(path: str, what: str, reader: p.Reader):
    data = sys.stdin.buffer.read(p.LIMITS.input_bytes + 1) if path == "-" else \
        reader.read(Path(path), kind="input", limit=p.LIMITS.input_bytes)
    return p.parse_json(data, limit=p.LIMITS.input_bytes, what=what)


def _roots(args, reader: p.Reader) -> p.Roots:
    if bool(args.roots_stdin) == bool(args.roots_file):
        raise p.PatternError("roots_required", "supply exactly one of --roots-stdin or --roots-file")
    return p.parse_roots(_input("-" if args.roots_stdin else args.roots_file, "roots envelope", reader))


def _add_roots(parser):
    parser.add_argument("--roots-stdin", action="store_true", help="read the roots envelope JSON from stdin")
    parser.add_argument("--roots-file", help="read the roots envelope JSON from a file")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="li-pattern", description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)
    envelope = commands.add_parser("envelope", help="build a roots envelope from a profile context record")
    envelope.add_argument("--personal", required=True)
    envelope.add_argument("--repository")
    source = envelope.add_mutually_exclusive_group(required=True)
    source.add_argument("--profile-record", help="profile context record JSON file, or - for stdin")
    source.add_argument("--profile-error", help="profile failure code when no record could be produced")
    envelope.add_argument("--profile-error-message", default="profile context unavailable")
    for name in ("list", "show", "check", "explain", "resolve"):
        command = commands.add_parser(name)
        _add_roots(command)
        if name == "show":
            command.add_argument("--ref", required=True, help="<source>:<id>@<version>")
        if name == "check":
            command.add_argument("--path", help="validate one document instead of the configured sources")
            command.add_argument("--kind", choices=sorted(p.DOCUMENT_KINDS))
        if name in ("explain", "resolve"):
            command.add_argument("--context", required=True)
            command.add_argument("--refs")
            command.add_argument("--overrides")
            command.add_argument("--exceptions")
            command.add_argument("--preview-draft", action="store_true")
            command.add_argument("--context-budget-chars", type=int, default=p.LIMITS.context_budget)
    return parser


def run(argv) -> tuple[dict, int]:
    reader = p.Reader()
    args = build_parser().parse_args(argv)
    if args.command == "envelope":
        if args.profile_record:
            context = p.pack_context_from_profile(_input(args.profile_record, "profile record", reader))
        else:
            context = p.pack_context_from_profile(error=(args.profile_error, args.profile_error_message))
        report = p.build_envelope(Path(args.repository) if args.repository else None, Path(args.personal), context)
        return report, 0
    if args.command == "check" and args.path:
        if args.roots_stdin or args.roots_file:
            raise p.PatternError("invalid_arguments", "check --path takes no roots")
        report = p.check_document(Path(args.path), args.kind, reader)
        return report, 0
    roots = _roots(args, reader)
    if args.command == "list":
        report = p.list_catalogs(roots, reader)
    elif args.command == "show":
        report = p.show_pattern(roots, args.ref, reader)
    elif args.command == "check":
        report = p.check_sources(roots, reader)
    else:
        context = p.parse_context(_input(args.context, "context", reader))
        refs = p.parse_refs(_input(args.refs, "refs", reader)) if args.refs else ()
        overrides = p.parse_overrides(_input(args.overrides, "overrides", reader)) if args.overrides else ()
        exceptions = p.parse_exceptions(_input(args.exceptions, "exceptions", reader)) if args.exceptions else ()
        report = p.resolve(roots, context, refs=refs, overrides=overrides, exceptions=exceptions,
                           preview_draft=args.preview_draft, context_budget=args.context_budget_chars,
                           reader=reader, explain=args.command == "explain")
    return report, p.exit_code(report["status"])


def main(argv=None) -> int:
    try:
        report, code = run(sys.argv[1:] if argv is None else argv)
    except p.PatternError as error:
        report, code = p._empty_report(error.status, [error.diagnostic()]), p.exit_code(error.status)
    for item in report.get("diagnostics", []):
        if item.get("severity") == "error":
            print(f"[lintel/pattern] {item['code']}: {item['message']}", file=sys.stderr)
    sys.stdout.flush()
    sys.stdout.buffer.write(p.emit_json(report).encode("utf-8"))
    sys.stdout.buffer.flush()
    return code


if __name__ == "__main__":
    sys.exit(main())
