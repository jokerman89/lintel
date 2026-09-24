#!/usr/bin/env python3
# component: mars-cli
# implements: ADR-0028 (draft MARS decision in .claude/plans/mars/adr-draft.md)
# intent: .claude/plans/mars/spec.md
# constraints: stdlib only; never invokes models, sessions or network; writes only the named panel file
# last_intent_review: 2026-09-24
"""MARS (Multi-Model Adversarial Review & Screening) data helper.

Subcommands print JSON. Exit 0 = ok/eligible, 3 = valid but not eligible, 2 = invalid input.
The caller owns dispatch, consent and closing sessions; this helper only decides and records.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import mars_contract as mc  # noqa: E402


def emit(value, code=0):
    print(json.dumps(value, indent=2))
    return code


def _git(*args):
    """Read-only repository facts for the origin header; None when unavailable."""
    try:
        out = subprocess.run(["git", *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None if out.returncode == 0 else None


def origin_from(args):
    remote = _git("config", "--get", "remote.origin.url") or ""
    repo = args.repository or (remote.rstrip("/").removesuffix(".git").split("github.com")[-1].lstrip(":/") or None)
    return {"requested_by": args.requested_by, "trigger": args.trigger, "caller": args.caller,
            "coordinator_surface": args.surface, "repository": repo,
            "branch": args.branch or _git("branch", "--show-current"),
            "commit": args.commit or _git("rev-parse", "HEAD"),
            "cycle_id": args.cycle_id, "work_map": args.work_map}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="li-mars", description=__doc__.splitlines()[0])
    parser.add_argument("--defaults", type=Path, default=mc.DEFAULTS_PATH)
    sub = parser.add_subparsers(dest="command", required=True)

    roster = sub.add_parser("roster", help="latest model per family + effective effort/context")
    roster.add_argument("--host", type=Path, required=True, help="host capability snapshot JSON")
    roster.add_argument("--families", help="comma-separated override, e.g. claude,gpt,grok,mai,gemini")

    offer = sub.add_parser("offer", help="may a caller offer MARS? (never consent)")
    offer.add_argument("--request", type=Path, required=True)

    panel = sub.add_parser("panel", help="panel state")
    psub = panel.add_subparsers(dest="action", required=True)

    def origin_args(p, required):
        p.add_argument("--requested-by", required=required, help="who asked, e.g. 'operator via <session>'")
        p.add_argument("--trigger", choices=("explicit", "cycle-offer", "review-offer"), required=required)
        p.add_argument("--caller", required=required, help="standalone | cycle:PLAN | review | ...")
        p.add_argument("--surface", required=required, help="exact client surface, e.g. copilot-app")
        p.add_argument("--repository")
        p.add_argument("--branch")
        p.add_argument("--commit")
        p.add_argument("--cycle-id")
        p.add_argument("--work-map")

    init = psub.add_parser("init")
    init.add_argument("--panel", type=Path, required=True)
    init.add_argument("--id", required=True)
    init.add_argument("--owner", required=True)
    init.add_argument("--brief", type=Path, required=True)
    init.add_argument("--consent", required=True)
    init.add_argument("--kind", default="review")
    init.add_argument("--subject-ref")
    origin_args(init, True)
    origin = psub.add_parser("origin", help="fill origin on a panel created without it (unset fields only)")
    origin.add_argument("--panel", type=Path, required=True)
    origin.add_argument("--subject-ref")
    origin_args(origin, True)
    brief = psub.add_parser("brief", help="render one reviewer request: mars-request header + body")
    brief.add_argument("--panel", type=Path, required=True)
    brief.add_argument("--slot", required=True)
    brief.add_argument("--round", type=int, required=True)
    brief.add_argument("--body", type=Path, required=True)
    brief.add_argument("--out", type=Path, required=True)
    brief.add_argument("--lens")
    add = psub.add_parser("add")
    add.add_argument("--panel", type=Path, required=True)
    add.add_argument("--slot", required=True)
    add.add_argument("--model", required=True)
    add.add_argument("--transport", choices=mc.TRANSPORTS, required=True)
    add.add_argument("--session")
    add.add_argument("--effort")
    add.add_argument("--context")
    rec = psub.add_parser("record")
    rec.add_argument("--panel", type=Path, required=True)
    rec.add_argument("--slot", required=True)
    rec.add_argument("--round", type=int, required=True)
    rec.add_argument("--result", type=Path, required=True)
    rec.add_argument("--status", default="received", choices=("received", "failed"))
    rec.add_argument("--brief-sha256")
    rec.add_argument("--legacy", action="store_true",
                     help="accept a pre-header report; recorded as header: legacy, never as v1")
    obs = psub.add_parser("observe")
    obs.add_argument("--panel", type=Path, required=True)
    obs.add_argument("--slot", required=True)
    obs.add_argument("--model", required=True)
    obs.add_argument("--evidence", choices=mc.IDENTITY_LEVELS, required=True)
    plan = psub.add_parser("close-plan")
    plan.add_argument("--panel", type=Path, required=True)
    plan.add_argument("--owner", required=True)
    plan.add_argument("--include-incomplete", action="store_true")
    closed = psub.add_parser("mark-closed")
    closed.add_argument("--panel", type=Path, required=True)
    closed.add_argument("--slot", required=True)
    closed.add_argument("--owner", required=True)
    summ = psub.add_parser("summary")
    summ.add_argument("--panel", type=Path, required=True)
    synth = psub.add_parser("synthesis-header", help="mars-synthesis header for the coordinator report")
    synth.add_argument("--panel", type=Path, required=True)

    args = parser.parse_args(argv)
    try:
        defaults = mc.load_defaults(args.defaults)
        schema = mc.load_schema()
        if args.command == "roster":
            families = args.families.split(",") if args.families else None
            result = mc.resolve_settings(mc.read_json(args.host), defaults, families)
            return emit(result, 0 if result["eligible"] else 3)
        if args.command == "offer":
            result = mc.offer_decision(mc.read_json(args.request), defaults)
            return emit(result, 0 if result["offer"] else 3)
        if args.action == "init":
            if args.panel.exists():
                raise mc.ContractError(f"panel already exists: {args.panel}")
            value = mc.new_panel(args.id, args.owner, args.brief, args.consent, defaults, args.kind,
                                 origin_from(args), args.subject_ref)
            mc.write_json(args.panel, value)
            return emit(value)
        value = mc.read_json(args.panel)
        mc.validate_panel(value)
        if args.action == "origin":
            current = value.setdefault("origin", {key: None for key in mc.ORIGIN_FIELDS})
            for key, new in origin_from(args).items():
                if new is not None and current.get(key) in (None, ""):
                    current[key] = new
            if args.subject_ref and value["subject"].get("ref") in (None, value["subject"]["brief_path"]):
                value["subject"]["ref"] = args.subject_ref
            value["subject"].setdefault("ref", value["subject"]["brief_path"])
            value.setdefault("word_limit", defaults["protocol"]["report_word_limit"])
        elif args.action == "brief":
            text, fields = mc.build_request(value, args.slot, args.round,
                                            args.body.read_text(encoding="utf-8-sig"), schema, args.lens)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text, encoding="utf-8", newline="\n")
            return emit({"request": args.out.as_posix(), "sha256": mc.sha256_file(args.out), "header": fields})
        elif args.action == "synthesis-header":
            print(mc.synthesis_header(value, schema, defaults), end="")
            return 0
        elif args.action == "add":
            mc.add_participant(value, args.slot, args.model, args.transport, args.session,
                               args.effort, args.context)
        elif args.action == "record":
            mc.record_round(value, args.slot, args.round, args.result, args.status, args.brief_sha256,
                            schema, args.legacy)
        elif args.action == "observe":
            mc.observe_identity(value, args.slot, args.model, args.evidence)
        elif args.action == "close-plan":
            return emit(mc.close_plan(value, args.owner, args.include_incomplete))
        elif args.action == "mark-closed":
            mc.mark_closed(value, args.slot, args.owner)
        elif args.action == "summary":
            return emit(mc.summary(value))
        mc.write_json(args.panel, value)
        return emit({"ok": True, "panel": value["panel_id"], "status": value["status"]})
    except (mc.ContractError, OSError, ValueError, KeyError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
