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
            command.add_argument("--attestations")
        if name == "resolve":
            command.add_argument("--lock", help="write a new lock file (inside the repository) for ready/empty only")
    verify = commands.add_parser("verify-lock")
    _add_roots(verify)
    verify.add_argument("--lock", required=True)
    verify.add_argument("--context", required=True)
    verify.add_argument("--attestations")
    verify.add_argument("--write", action="store_true", help="install validated attestations in the lock (CAS)")
    verify.add_argument("--expected-lock-digest")
    mapping = commands.add_parser("map")
    _add_roots(mapping)
    mapping.add_argument("--lock", required=True)
    mapping.add_argument("--task-map", required=True)
    mapping.add_argument("--expected-lock-digest", required=True)
    mapping.add_argument("--write", action="store_true")
    project = commands.add_parser("project")
    project.add_argument("--lock", required=True)
    project.add_argument("--task-map", required=True)
    project.add_argument("--package", required=True)
    capture = commands.add_parser("capture", help="register a new draft (never approves or overwrites)")
    _add_roots(capture)
    capture.add_argument("--input", required=True)
    capture.add_argument("--scope", required=True, choices=("repo", "personal"))
    capture.add_argument("--name", required=True, help="the draft's pattern ID, confirmed explicitly")
    capture.add_argument("--source-id", help="namespaced source ID; required on the first capture in a scope")
    capture.add_argument("--expected-catalog-digest")
    index = commands.add_parser("index", help="verify registered entries and regenerate derived metadata")
    _add_roots(index)
    index.add_argument("--source-root", required=True)
    index.add_argument("--expected-catalog-digest")
    approve = commands.add_parser("approve", help="publish a strictly newer approved version of a draft")
    _add_roots(approve)
    approve.add_argument("--path", required=True)
    approve.add_argument("--version", required=True)
    approve.add_argument("--approval", required=True, help="JSON {by, reference, at}")
    approve.add_argument("--expected-digest", required=True, help="content digest of the reviewed draft")
    approve.add_argument("--expected-catalog-digest", help="optional CAS on the catalog the caller reviewed")
    update = commands.add_parser("update", help="preview or publish a strictly newer draft version")
    _add_roots(update)
    update.add_argument("--path", required=True)
    update.add_argument("--input", required=True)
    update.add_argument("--expected-digest", required=True)
    update.add_argument("--expected-catalog-digest")
    update.add_argument("--write", action="store_true")
    for action in p.LIFECYCLE_ACTIONS:
        event = commands.add_parser(action, help=f"preview or record a {action} event with its impact")
        _add_roots(event)
        event.add_argument("--ref", required=True)
        event.add_argument("--record", required=True)
        event.add_argument("--expected-catalog-digest")
        event.add_argument("--write", action="store_true")
    remove = commands.add_parser("remove", help="preview or unregister one unreferenced entry; files are kept")
    _add_roots(remove)
    remove.add_argument("--ref", required=True)
    remove.add_argument("--expected-catalog-digest")
    remove.add_argument("--write", action="store_true")
    apply = commands.add_parser("apply", help="preview or write one repository binding change")
    _add_roots(apply)
    apply.add_argument("--change", required=True)
    apply.add_argument("--expected-digest")
    apply.add_argument("--write", action="store_true")
    export = commands.add_parser("export", help="write a local bundle of exact refs and their closure")
    _add_roots(export)
    export.add_argument("--refs", required=True, help="JSON array of exact references")
    export.add_argument("--out", required=True)
    importer = commands.add_parser("import", help="validate and preview a bundle; --write stages drafts")
    _add_roots(importer)
    importer.add_argument("--bundle", required=True)
    importer.add_argument("--scope", required=True, choices=("repo", "personal"))
    importer.add_argument("--destination-source", required=True)
    importer.add_argument("--version-map", required=True)
    importer.add_argument("--expected-catalog-digest")
    importer.add_argument("--write", action="store_true")
    review = commands.add_parser("review", help="verify the lock, then per-clause evidence coverage")
    _add_roots(review)
    review.add_argument("--lock", required=True)
    review.add_argument("--context", required=True)
    review.add_argument("--evidence", required=True)
    review.add_argument("--attestations")
    return parser


def _attestations(args, reader: p.Reader):
    return p.parse_attestations(_input(args.attestations, "attestations", reader)) if args.attestations else ()


def _pattern_input(path: str, reader: p.Reader):
    return p.parse_json(reader.read(Path(path), kind="input", limit=p.LIMITS.pattern_bytes),
                        limit=p.LIMITS.pattern_bytes, what="pattern input")


def _lock_input(path: str, reader: p.Reader):
    return p.parse_json(reader.read(Path(path), kind="input", limit=p.LIMITS.catalog_bytes),
                        limit=p.LIMITS.catalog_bytes, what="lock")


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
    if args.command == "project":
        report = p.project_package(_lock_input(args.lock, reader), _input(args.task_map, "task map", reader),
                                   args.package)
        return report, 0
    roots = _roots(args, reader)
    if args.command == "list":
        report = p.list_catalogs(roots, reader)
    elif args.command == "show":
        report = p.show_pattern(roots, args.ref, reader)
    elif args.command == "check":
        report = p.check_sources(roots, reader)
    elif args.command == "verify-lock":
        attestations = _attestations(args, reader)
        context = p.parse_context(_input(args.context, "context", reader))
        if args.write:
            if not args.expected_lock_digest or not attestations:
                raise p.PatternError("invalid_arguments", "--write needs --attestations and --expected-lock-digest")
            report = p.record_attestations(roots, Path(args.lock), attestations, context,
                                           expected_lock_digest=args.expected_lock_digest, reader=reader)
        else:
            report = p.verify_lock(roots, _lock_input(args.lock, reader), context, reader=reader,
                                   attestations=attestations)
    elif args.command == "update":
        report = p.update(roots, Path(args.path), _pattern_input(args.input, reader), expected_digest=args.expected_digest,
                          write=args.write, expected_catalog_digest=args.expected_catalog_digest, reader=reader)
    elif args.command in p.LIFECYCLE_ACTIONS:
        report = p.record_lifecycle(roots, args.ref, action=args.command, record_value=_input(args.record, "record", reader),
                                    expected_catalog_digest=args.expected_catalog_digest, write=args.write,
                                    reader=reader)
    elif args.command == "remove":
        report = p.remove(roots, args.ref, expected_catalog_digest=args.expected_catalog_digest, write=args.write,
                          reader=reader)
    elif args.command == "apply":
        report = p.apply_change(roots, _input(args.change, "change", reader), expected_digest=args.expected_digest,
                                write=args.write, reader=reader)
    elif args.command == "export":
        refs = [p.parse_exact_ref(item, "refs") for item in _input(args.refs, "refs", reader)]
        report = p.export_bundle(roots, refs, Path(args.out), reader=reader)
    elif args.command == "import":
        report = p.import_bundle(roots, Path(args.bundle), scope=args.scope, destination_source=args.destination_source,
                                 version_map_value=_input(args.version_map, "version map", reader), write=args.write,
                                 expected_catalog_digest=args.expected_catalog_digest, reader=reader)
    elif args.command == "review":
        report = p.review_coverage(roots, _lock_input(args.lock, reader),
                                   p.parse_context(_input(args.context, "context", reader)),
                                   _input(args.evidence, "evidence", reader), attestations=_attestations(args, reader),
                                   reader=reader)
    elif args.command == "map":
        report = p.map_lock(roots, Path(args.lock), _input(args.task_map, "task map", reader),
                            expected_lock_digest=args.expected_lock_digest, write=args.write, reader=reader)
    elif args.command == "capture":
        report = p.capture(roots, p.parse_json(reader.read(Path(args.input), kind="input", limit=p.LIMITS.pattern_bytes),
                                               limit=p.LIMITS.pattern_bytes, what="draft"),
                           scope=args.scope, name=args.name, source_id=args.source_id,
                           expected_catalog_digest=args.expected_catalog_digest, reader=reader)
    elif args.command == "index":
        report = p.index_source(roots, Path(args.source_root), expected_catalog_digest=args.expected_catalog_digest,
                                reader=reader)
    elif args.command == "approve":
        report = p.approve(roots, Path(args.path), version=args.version,
                           approval_value=_input(args.approval, "approval", reader),
                           expected_digest=args.expected_digest,
                           expected_catalog_digest=args.expected_catalog_digest, reader=reader)
    else:
        context = p.parse_context(_input(args.context, "context", reader))
        refs = p.parse_refs(_input(args.refs, "refs", reader)) if args.refs else ()
        overrides = p.parse_overrides(_input(args.overrides, "overrides", reader)) if args.overrides else ()
        exceptions = p.parse_exceptions(_input(args.exceptions, "exceptions", reader)) if args.exceptions else ()
        report = p.resolve(roots, context, refs=refs, overrides=overrides, exceptions=exceptions,
                           preview_draft=args.preview_draft, context_budget=args.context_budget_chars,
                           reader=reader, explain=args.command == "explain", attestations=_attestations(args, reader))
        if args.command == "resolve" and args.lock:
            if report["status"] not in ("ready", "empty"):
                report["diagnostics"].append({"code": "lock_not_written", "severity": "info",
                                              "message": f"no lock written for status {report['status']}"})
            else:
                lock = p.build_lock(report, context, refs=refs, context_budget=args.context_budget_chars)
                report["lock"] = p.write_lock(roots, Path(args.lock), lock)
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
