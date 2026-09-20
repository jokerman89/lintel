#!/usr/bin/env python3
# component: review-evidence-cli
# implements: ADR-0005, ADR-0024, ADR-0028
# intent: .claude/plans/universal-implementation/packages/P05.md
# constraints: trusted source helpers; selected target data; no execution of evidence content
# last_intent_review: 2026-09-20
"""Prepare, validate and consume review evidence; shell adapters own audit routing/writes."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

SOURCE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOURCE_ROOT / "lib"))
from review_contract import (  # noqa: E402
    ContractError, bind_work, canonical_json, content_digest, evaluate_controls,
    evidence_manifest, load_json, resolve_commit, select_latest, snapshot,
    validate_context, validate_decision, validate_review, validate_shape, verify_context, verify_qa, verify_review,
)


def read_object(path: Path) -> dict[str, Any]:
    return load_json(path.read_text(encoding="utf-8-sig"))


def emit(value: Any) -> None:
    print(canonical_json(value))


def prepare(repo: Path, request: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "work_map", "package_id", "leaf_ids", "acceptance_paths", "base", "selection",
        "record_path", "attempt_id", "builder", "independence_required", "purpose",
        "profile", "required_policy", "required_controls",
    }
    if set(request) != fields:
        raise ContractError(f"Request fields differ: {sorted(fields ^ set(request))}")
    context = {key: request[key] for key in (
        "attempt_id", "builder", "independence_required", "purpose", "profile",
        "required_policy", "required_controls",
    )}
    context.update({
        "schema_version": 1,
        "work": bind_work(repo, **{key: request[key] for key in (
            "work_map", "package_id", "leaf_ids", "acceptance_paths",
        )}),
        "snapshot": snapshot(repo, **{key: request[key] for key in ("base", "selection", "record_path")}),
    })
    validate_context(context)
    return context


def audit_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            envelope = load_json(line)
            if "raw" not in envelope:
                records.append(validate_decision(envelope))
                continue
            validate_shape(envelope, "auditEnvelope")
            raw = validate_decision(load_json(envelope["raw"]), history=envelope.get("format") == "history")
            if envelope.get("format") == "history":
                # An explicit archive import is not a newly issued decision.
                continue
            elif envelope.get("format") == "review-v1" and raw.get("schema_version") != 1:
                raise ContractError("Current review audit format requires a version-1 decision")
            elif envelope.get("kind") != raw.get("skill"):
                raise ContractError("Audit kind does not match the raw decision")
            elif raw.get("schema_version") == 1:
                context = raw.get("context")
                snap = context.get("snapshot") if isinstance(context, dict) else None
                if not isinstance(snap, dict) or envelope.get("commit") != snap.get("head") or envelope.get("status") != raw.get("status"):
                    raise ContractError("Audit header does not match the raw decision binding")
            records.append(raw)
        except (ContractError, UnicodeError) as error:
            raise ContractError(f"Review log line {index}: {error}") from error
    return records


def read_gate(args: argparse.Namespace) -> dict[str, Any]:
    if args.expected is None:
        return {"ok": False, "status": "unverified", "problems": ["An explicit --expected context is required; legacy records are history only"]}
    expected = read_object(args.expected)
    validate_context(expected)
    work = expected["work"]
    record = select_latest(
        audit_records(args.log), skill=args.skill,
        work_map=work["work_map"], package_id=work["package_id"],
    )
    if record is None:
        return {"ok": False, "status": "unverified", "problems": ["No applicable review decision"]}
    corroboration = read_object(args.corroboration) if args.corroboration else None
    result = verify_review(args.repo, record, expected=expected, corroboration=corroboration)
    if result["ok"]:
        when = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if when > now + timedelta(minutes=5) or (args.days is not None and when < now - timedelta(days=args.days)):
            result.update(ok=False, status="unverified")
            result["problems"].append("Latest decision is outside the explicitly permitted time window")
    result["gate_skill"] = args.skill
    return result


def ship(args: argparse.Namespace) -> dict[str, Any]:
    # Consume the real shell reader so source/target audit routing has one owner.
    command = [
        "bash", (SOURCE_ROOT / "bin" / "li-review-read").as_posix(),
        "--skill", args.skill, "--expected", args.expected.as_posix(), "--gate-json",
    ]
    if args.corroboration:
        command += ["--corroboration", args.corroboration.as_posix()]
    environment = {
        **os.environ, "LINTEL_SOURCE_ROOT": SOURCE_ROOT.as_posix(),
        "LINTEL_REPO_ROOT": args.repo.resolve().as_posix(),
        "LINTEL_PYTHON": Path(sys.executable).as_posix(),
    }
    read = subprocess.run(command, cwd=args.repo, env=environment, text=True, encoding="utf-8", capture_output=True, check=False)
    if read.returncode not in (0, 3):
        raise ContractError(f"Review reader unavailable: {read.stderr.strip()}")
    result = load_json(read.stdout)
    if read.returncode or result.get("ok") is not True:
        result["ok"] = False
        return result
    expected, qa = read_object(args.expected), read_object(args.qa)
    checks = verify_qa(args.repo, qa, expected=expected)
    result["qa"] = checks
    if checks["blocked"]:
        result.update(ok=False, status="unverified")
        result["problems"].extend(checks["blockers"])
    return result


def log_input(args: argparse.Namespace) -> None:
    data = read_object(args.file) if args.file else load_json(args.input)
    skill = data.get("skill")
    if not isinstance(skill, str) or re.fullmatch(r"[a-z][a-z0-9-]*", skill) is None:
        raise ContractError("A valid skill name is required")
    if args.history:
        status, commit, format_ = "historical", "", "history"
    elif "schema_version" in data:
        validate_review(data)
        status, commit, format_ = data["status"], data["context"]["snapshot"]["head"], "review-v1"
        resolve_commit(args.repo, commit)
        resolve_commit(args.repo, data["context"]["snapshot"]["base"])
    else:
        validate_shape(data.get("status"), "legacyStatus")
        commit = data.get("commit")
        if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{7,64}", commit) is None:
            raise ContractError("Legacy logging requires an explicit commit; it cannot grant strict clearance")
        resolve_commit(args.repo, commit)
        status, format_ = data["status"], "legacy"
    for value in (skill, status, commit, format_, canonical_json(data)):
        print(value)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    for name in ("prepare", "snapshot", "inspect", "controls", "validate", "verify", "qa", "ship", "read", "log-input", "audit-check", "import-lines"):
        command = sub.add_parser(name)
        command.add_argument("--repo", type=Path, default=Path.cwd())
        if name == "prepare":
            command.add_argument("--request", type=Path, required=True)
        if name == "snapshot":
            command.add_argument("--base", required=True)
            command.add_argument("--select", action="append", required=True)
            command.add_argument("--record-path")
        if name in ("controls", "qa", "inspect"):
            command.add_argument("--input", type=Path, required=True)
        if name == "inspect":
            command.add_argument("--snapshot", type=Path, required=True)
        if name in ("validate", "verify"):
            command.add_argument("--record", type=Path, required=True)
        if name in ("verify", "qa", "ship", "read"):
            command.add_argument("--expected", type=Path, required=name != "read")
        if name in ("verify", "ship", "read"):
            command.add_argument("--corroboration", type=Path)
        if name in ("ship", "read"):
            command.add_argument("--skill", default="review")
        if name == "ship":
            command.add_argument("--qa", type=Path, required=True)
        if name == "read":
            command.add_argument("--log", type=Path, required=True)
            command.add_argument("--days", type=int)
            command.add_argument("--gate-json", action="store_true")
        if name == "log-input":
            inputs = command.add_mutually_exclusive_group(required=True)
            inputs.add_argument("--input")
            inputs.add_argument("--file", type=Path)
            command.add_argument("--history", action="store_true")
        if name == "audit-check":
            command.add_argument("--log", type=Path, required=True)
            command.add_argument("--offset", type=int, required=True)
        if name == "import-lines":
            command.add_argument("--file", type=Path, required=True)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "prepare":
            emit(prepare(args.repo, read_object(args.request)))
        elif args.command == "snapshot":
            emit(snapshot(args.repo, base=args.base, selection=args.select, record_path=args.record_path))
        elif args.command == "inspect":
            selected, inputs = read_object(args.snapshot), read_object(args.input)
            validate_shape(selected, "snapshot")
            current = snapshot(
                args.repo, base=selected["base"], selection=selected["selection"],
                record_path=selected["record_path"],
            )
            if selected["result_digest"] != current["result_digest"] or selected["entries"] != current["entries"]:
                raise ContractError("Inspection input changed; collect observations again")
            result = evaluate_controls(inputs["controls"], required_policy=inputs["required_policy"])
            emit({
                "schema_version": 1, "purpose": "inspection", "release_clearance": False,
                "snapshot": selected, "result": result,
                "evidence": evidence_manifest(args.repo, inputs["controls"]),
            })
            return 3 if result["blocked"] else 0
        elif args.command == "controls":
            inputs = read_object(args.input)
            result = evaluate_controls(inputs["controls"], required_policy=inputs["required_policy"])
            emit(result)
            return 3 if result["blocked"] else 0
        elif args.command == "validate":
            emit(validate_review(read_object(args.record)))
        elif args.command == "verify":
            result = verify_review(
                args.repo, read_object(args.record), expected=read_object(args.expected),
                corroboration=read_object(args.corroboration) if args.corroboration else None,
            )
            emit(result)
            return 0 if result["ok"] else 3
        elif args.command == "qa":
            expected, inputs = read_object(args.expected), read_object(args.input)
            verify_context(args.repo, expected)
            qa = {
                "schema_version": 1, "context_digest": content_digest(expected),
                "controls": inputs["controls"], "evidence": evidence_manifest(args.repo, inputs["controls"]),
            }
            result = verify_qa(args.repo, qa, expected=expected)
            emit(qa)
            return 3 if result["blocked"] else 0
        elif args.command == "ship":
            result = ship(args)
            emit(result)
            return 0 if result["ok"] else 3
        elif args.command == "read":
            if args.days is not None and args.days < 0:
                raise ContractError("--days must be nonnegative")
            try:
                result = read_gate(args)
            except (ContractError, OSError, UnicodeError) as error:
                result = {"ok": False, "status": "error", "problems": [str(error)]}
            if args.gate_json:
                emit(result)
            else:
                print(f"## Review records (native: {args.log})")
                print(args.log.read_text(encoding="utf-8") if args.log.is_file() else "NO_REVIEWS")
                print("---VERDICT---")
                print(f"gate_skill: {args.skill}")
                print(f"current_head: {resolve_commit(args.repo, 'HEAD')[:7]}")
                print("VERDICT: Review CLEAR for selected content" if result["ok"] else "VERDICT: BLOCKED (no sufficient current review evidence)")
                for problem in result["problems"]:
                    print(f"reason: {problem}")
            return 0 if result["ok"] else 3
        elif args.command == "log-input":
            log_input(args)
        elif args.command == "audit-check":
            expected_raw = canonical_json(load_json(sys.stdin.read()))
            with args.log.open("rb") as file:
                file.seek(args.offset)
                lines = file.read().decode("utf-8").splitlines()
            if not any(load_json(line).get("raw") == expected_raw for line in lines if line.strip()):
                raise ContractError("Audit writer did not persist this review; no successful receipt")
        elif args.command == "import-lines":
            lines = [
                load_json(line) for line in args.file.read_text(encoding="utf-8-sig").splitlines() if line.strip()
            ]
            for line in lines:
                emit(line)
        return 0
    except (ContractError, OSError, UnicodeError, KeyError, TypeError, ValueError) as error:
        message = f"li-review-evidence: {error}"
        if args.command in ("ship", "verify"):
            emit({"ok": False, "status": "error", "problems": [message]})
            return 3
        print(message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    sys.exit(main())
