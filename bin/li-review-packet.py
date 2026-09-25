#!/usr/bin/env python3
# component: review-packet-cli
# implements: ADR-0036, ADR-0028
# intent: skills/review/references/method.md
# constraints: stdlib only; never invokes models, sessions or network; writes only the named output files
# last_intent_review: 2026-09-25
"""Review Method packet helper: select questions, render one packet body, check reports.

Subcommands print JSON. Exit 0 = ok (for check: a complete, consistent report, whatever its
outcome), 3 = valid input but an incomplete, inconsistent or unusable report, 2 = invalid input.
The caller dispatches reviewers; this helper renders and checks text.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import review_method as rm  # noqa: E402


def emit(value, code=0):
    print(json.dumps(value, indent=2))
    return code


def _git(repo, *args):
    try:
        out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return (out.stdout.strip() or None) if out.returncode == 0 else None


def _tags(value):
    return [tag.strip() for tag in (value or "").split(",") if tag.strip()]


def _catalog(args):
    return rm.load_catalog(rm.CATALOG_PATH, [*rm.project_catalogs(args.repo), *(args.catalog or [])])


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="li-review-packet", description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--catalog", type=Path, action="append", help="extra namespaced question catalog")
    sub = parser.add_subparsers(dest="command", required=True)

    questions = sub.add_parser("questions", help="standing questions selected for a subject")
    questions.add_argument("--kind", required=True)
    questions.add_argument("--stage", choices=rm.STAGES, required=True)
    questions.add_argument("--tags", default="")

    tags = sub.add_parser("tags", help="advisory surface tags from paths and diff text")
    tags.add_argument("--paths", nargs="*", default=[])
    tags.add_argument("--text-file", type=Path)

    render = sub.add_parser("render", help="write the packet body, its meta and optionally a request")
    render.add_argument("--kind", required=True)
    render.add_argument("--stage", choices=rm.STAGES, required=True)
    render.add_argument("--subject-file", type=Path, required=True)
    render.add_argument("--subject-ref", required=True)
    render.add_argument("--commit")
    render.add_argument("--acceptance", action="append", default=[])
    render.add_argument("--tags", default="")
    render.add_argument("--context-file", type=Path)
    render.add_argument("--body-out", type=Path, required=True)
    render.add_argument("--meta-out", type=Path)
    render.add_argument("--request-out", type=Path, help="also write a single-review request")
    render.add_argument("--requested-by")
    render.add_argument("--coordinator", help="coordinator session id")
    render.add_argument("--surface", help="exact client surface, e.g. copilot-app")
    render.add_argument("--repository")
    render.add_argument("--branch")
    render.add_argument("--model")
    render.add_argument("--effort")
    render.add_argument("--context-tier")
    render.add_argument("--cycle-id")
    render.add_argument("--work-map")

    check = sub.add_parser("check", help="validate a reviewer report against its packet meta")
    check.add_argument("--report", type=Path, required=True)
    check.add_argument("--meta", type=Path, required=True)
    check.add_argument("--header", choices=("review", "mars"), default="review")

    outcome = sub.add_parser("outcome", help="append one opt-in calibration outcome")
    outcome.add_argument("--sq", required=True)
    outcome.add_argument("--outcome", choices=rm.OUTCOMES, required=True)
    outcome.add_argument("--ref", required=True)
    outcome.add_argument("--note")
    outcome.add_argument("--log", type=Path)

    outcomes = sub.add_parser("outcomes", help="summarize calibration outcomes and proposals")
    outcomes.add_argument("--log", type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "tags":
            text = args.text_file.read_text(encoding="utf-8-sig", errors="replace") if args.text_file else ""
            return emit(rm.suggest_tags(_catalog(args), args.paths, text))
        if args.command == "questions":
            selected = rm.select_questions(_catalog(args), args.kind, _tags(args.tags), args.stage)
            return emit({"stage": args.stage, "kind": args.kind, "questions": selected})
        if args.command == "render":
            catalog = _catalog(args)
            tag_list = _tags(args.tags)
            selected = rm.select_questions(catalog, args.kind, tag_list, args.stage)
            context = args.context_file.read_text(encoding="utf-8-sig") if args.context_file else None
            body = rm.render_body(kind=args.kind, stage=args.stage, subject_ref=args.subject_ref,
                                  subject_text=args.subject_file.read_text(encoding="utf-8-sig"),
                                  questions=selected, commit=args.commit, acceptance=args.acceptance,
                                  tags=tag_list, context_text=context)
            meta = rm.method_meta(kind=args.kind, stage=args.stage, subject_ref=args.subject_ref, body=body,
                                  questions=selected, commit=args.commit, acceptance=args.acceptance,
                                  tags=tag_list)
            request = None
            if args.request_out:
                missing = [flag for flag, value in (("--requested-by", args.requested_by),
                                                    ("--surface", args.surface)) if not value]
                rm.require(not missing, f"a request needs {', '.join(missing)}")
                remote = _git(args.repo, "config", "--get", "remote.origin.url")
                fields = {
                    "requested_by": args.requested_by, "coordinator_session": args.coordinator or "manual",
                    "coordinator_surface": args.surface,
                    "repository": args.repository or rm.repository_slug(remote) or "unknown",
                    "branch": args.branch or _git(args.repo, "branch", "--show-current") or "unknown",
                    "commit": args.commit or _git(args.repo, "rev-parse", "HEAD") or "unknown",
                    "subject_kind": args.kind, "subject_ref": args.subject_ref, "stage": args.stage,
                    "brief_sha256": meta["brief_sha256"], "method": rm.METHOD_VERSION,
                    "questions": meta["questions"] or "none",
                    "reasoning_effort": args.effort or "host-default",
                    "context_tier": args.context_tier or "host-default", "reply_via": "final-response",
                }
                optional = {"requested_model": args.model, "cycle_id": args.cycle_id,
                            "work_map": args.work_map, "tags": tag_list or None}
                fields.update({key: value for key, value in optional.items() if value})
                request = rm.render_request(fields, body, rm.load_schema())
            _write(args.body_out, body)
            written = rm.sha256_bytes(args.body_out.read_bytes())
            rm.require(written == meta["brief_sha256"], "written body differs from the rendered body")
            if args.meta_out:
                _write(args.meta_out, json.dumps(meta, indent=2) + "\n")
            if request is not None:
                _write(args.request_out, request)
            return emit({"brief_sha256": meta["brief_sha256"], "body": args.body_out.as_posix(),
                         "meta": args.meta_out.as_posix() if args.meta_out else None,
                         "request": args.request_out.as_posix() if args.request_out else None,
                         "stage": args.stage, "kind": args.kind, "tags": tag_list,
                         "questions": meta["questions"]})
        if args.command == "check":
            result = rm.check_report(args.report.read_text(encoding="utf-8-sig"), rm.read_json(args.meta),
                                     prefix=args.header)
            return emit(result, 0 if result["usable"] else 3)
        log = args.log or (args.repo / rm.OUTCOME_LOG)
        if args.command == "outcome":
            record = rm.outcome_record(_catalog(args), args.sq, args.outcome, args.ref, args.note)
            rm.append_outcome(log, record)
            return emit({"ok": True, "log": log.as_posix(), "record": record})
        return emit(rm.summarize_outcomes(log))
    except (rm.MethodError, OSError, ValueError, KeyError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
