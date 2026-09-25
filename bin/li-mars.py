#!/usr/bin/env python3
# component: mars-cli
# implements: ADR-0034, ADR-0028
# intent: .claude/plans/mars/spec.md
# constraints: stdlib only; never invokes models, sessions or network; writes only the named panel/record files
# last_intent_review: 2026-09-25
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
    remote = _git("config", "--get", "remote.origin.url")
    repo = args.repository or mc._lib_module("review_method").repository_slug(remote)
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
    init.add_argument("--method-meta", type=Path, help="li-review-packet render --meta-out for this brief")
    init.add_argument("--select", action="append", help="bind this repository path (repeatable)")
    init.add_argument("--base", default="HEAD", help="snapshot base commit for --select")
    init.add_argument("--repo", type=Path, default=Path.cwd())
    init.add_argument("--snapshot", type=Path, help="immutable snapshot path (default: next to the brief)")
    init.add_argument("--profile-ref", type=Path, help="profile reference (default: selected profile, if any)")
    origin_args(init, True)
    verify = psub.add_parser("verify-input", help="is the bound selected input unchanged?")
    verify.add_argument("--panel", type=Path, required=True)
    verify.add_argument("--repo", type=Path)
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
    synth.add_argument("--adjudicated",
                       help="adjudicated counts p1,p2,p3[,deviations] -> outcome by the shared rule")
    inspect = psub.add_parser("inspection", help="content-bound inspection record (release_clearance false)")
    inspect.add_argument("--panel", type=Path, required=True)
    inspect.add_argument("--synthesis", type=Path, required=True)
    inspect.add_argument("--out", type=Path)

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
            if args.method_meta:
                mc.attach_method(value, mc.read_json(args.method_meta))
            mc.attach_profile(value, args.repo, args.profile_ref)
            if args.select:
                mc.bind_input(value, args.repo, args.base, args.select,
                              args.snapshot or args.brief.parent / "snapshot.json", [args.panel.parent])
            mc.write_json(args.panel, value)
            return emit(value)
        value = mc.read_json(args.panel)
        mc.validate_panel(value)
        if args.action == "verify-input":
            result = mc.verify_input(value, args.repo)
            return emit(result, 3 if result["status"] == "changed" else 0)
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
            if args.round == 1:
                mc.require(mc.sha256_file(args.body) == value["subject"]["brief_sha256"],
                           "round-1 body differs from the frozen brief; every slot gets the same bytes")
            checked = mc.verify_input(value)
            mc.require(checked["status"] != "changed",
                       "input_changed: the selected input changed; start a new panel with new consent")
            text, fields = mc.build_request(value, args.slot, args.round,
                                            args.body.read_text(encoding="utf-8-sig"), schema, args.lens)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
            return emit({"request": args.out.as_posix(), "sha256": mc.sha256_file(args.out), "header": fields})
        elif args.action == "synthesis-header":
            counts = [int(n) for n in args.adjudicated.split(",")] if args.adjudicated else None
            print(mc.synthesis_header(value, schema, defaults, counts, mc.verify_input(value)), end="")
            return 0
        elif args.action == "inspection":
            record = mc.inspection_record(value, args.synthesis.read_text(encoding="utf-8-sig"), schema,
                                          mc.verify_input(value))
            if args.out:
                mc.require(not args.out.exists(), f"inspection record already exists: {args.out}")
                mc.write_json(args.out, record)
            return emit(record)
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
