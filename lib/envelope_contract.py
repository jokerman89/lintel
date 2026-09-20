#!/usr/bin/env python3
# component: envelope-contract
# implements: ADR-0008, ADR-0027
# intent: .claude/plans/universal-implementation/packages/P04.md
# constraints: explicit local invocation; payload never executed or written to audit
# last_intent_review: 2026-09-20
"""Shared structured envelope construction, validation, evaluation and safe release."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import sys
from typing import Any, Mapping


SCHEMA = Path(__file__).with_name("envelope-schema.yaml")
FORBIDDEN = re.compile(
    r"AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{40,}|ghp_[A-Za-z0-9]{36,}|"
    r"xox[bp]-[A-Za-z0-9-]{20,}|AIza[0-9A-Za-z_-]{35}|"
    r"\$\([^)]*rm\s+-rf|;\s*rm\s+-rf\s+/|curl\s+[^|]*\|\s*sh|"
    r"ignore (?:previous|prior) instructions|system: you are now|new role:",
    re.IGNORECASE,
)


class EnvelopeError(ValueError):
    """A safe-to-print contract diagnostic; never includes untrusted payload text."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if not isinstance(key, str) or key in result:
            raise EnvelopeError("Duplicate or non-string object key")
        result[key] = value
    return result


def _constant(_: str) -> None:
    raise EnvelopeError("Non-finite numbers are not supported")


def _yaml_module():
    try:
        import yaml
    except ImportError as error:
        raise EnvelopeError("Optional PyYAML 6.x is required for legacy YAML input; use JSON or authorize envelope-requirements.txt installation") from error
    return yaml


def load_text(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    except json.JSONDecodeError:
        yaml = _yaml_module()

        class StrictLoader(yaml.SafeLoader):
            pass

        def mapping(loader, node):
            pairs = [(loader.construct_object(key, deep=True), loader.construct_object(value, deep=True))
                     for key, value in node.value]
            return _pairs(pairs)

        StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
        try:
            if any(isinstance(token, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken)) for token in yaml.scan(text)):
                raise EnvelopeError("YAML aliases and anchors are not supported")
            return yaml.load(text, Loader=StrictLoader)
        except yaml.YAMLError as error:
            raise EnvelopeError("Malformed YAML or unsupported YAML tag") from error


def load_document(path: Path) -> Any:
    try:
        return load_text(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError) as error:
        raise EnvelopeError("Cannot read UTF-8 envelope input") from error


@lru_cache(maxsize=1)
def schema() -> dict[str, Any]:
    data = load_document(SCHEMA)
    if not isinstance(data, dict):
        raise EnvelopeError("Envelope schema is unavailable or malformed")
    return data


def _strings(value: Any, *, nonempty: bool = False) -> bool:
    return isinstance(value, list) and (bool(value) or not nonempty) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def _check_type(value: Any, expected: str) -> bool:
    if expected.startswith("nullable_"):
        return value is None or _check_type(value, expected.removeprefix("nullable_"))
    if expected == "string":
        return isinstance(value, str) and bool(value.strip()) and not any(ord(char) < 32 and char not in "\n\t\r" for char in value)
    if expected == "integer":
        return type(value) is int
    if expected == "boolean":
        return type(value) is bool
    if expected in ("string_list", "nonempty_string_list"):
        return _strings(value, nonempty=expected == "nonempty_string_list")
    if expected == "object_list":
        return isinstance(value, list) and all(isinstance(item, dict) for item in value)
    raise EnvelopeError("Unknown schema field type")


def _check_object(value: Any, definition: Mapping[str, Any], location: str) -> None:
    if not isinstance(value, dict):
        raise EnvelopeError(f"{location} must be an object")
    if any(name not in value for name in definition["required"]):
        raise EnvelopeError(f"{location} is missing required fields")
    allowed = set(definition["required"]) | set(definition.get("optional", []))
    if set(value) - allowed:
        raise EnvelopeError(f"{location} contains unsupported fields")
    for name, expected in definition.get("types", {}).items():
        if name in value and not _check_type(value[name], expected):
            raise EnvelopeError(f"{location}.{name} has an invalid type or empty value")
    for name, item_definition in definition.get("items", {}).items():
        for item in value.get(name, []):
            _check_object(item, item_definition, f"{location}.{name}[]")


def reject_forbidden(value: object) -> None:
    try:
        serialized = json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise EnvelopeError("Payload contains unsupported data types") from error
    if FORBIDDEN.search(serialized):
        raise EnvelopeError("Forbidden content detected; redact the original input before retrying")


def validate_content(content_type: str, content: Any) -> None:
    definition = schema()["content_types"].get(content_type)
    if definition is None:
        raise EnvelopeError("Unknown body.content_type")
    if content_type != "payload_freeform":
        _check_object(content, definition, "body.content")


def validate_envelope(value: Any, *, safety: bool = True) -> None:
    if not isinstance(value, dict) or set(value) != {"head", "body", "tail"}:
        raise EnvelopeError("Envelope must contain exactly head, body and tail objects")
    definition = schema()
    for name in ("head", "body", "tail"):
        _check_object(value[name], definition[name], name)
    head, body, tail = value["head"], value["body"], value["tail"]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", head["envelope_id"]):
        raise EnvelopeError("head.envelope_id must be a stable printable identifier")
    if head["envelope_schema_version"] != definition["schema_version"] or head["kind"] not in definition["kinds"]:
        raise EnvelopeError("Unknown envelope version or head.kind")
    try:
        issued = datetime.fromisoformat(head["issued_at"].replace("Z", "+00:00"))
        if issued.tzinfo is None or issued.utcoffset().total_seconds() != 0:
            raise ValueError
    except (TypeError, ValueError, AttributeError) as error:
        raise EnvelopeError("head.issued_at must be an ISO UTC timestamp") from error
    if head["kind"] == "reply" and not head.get("parent_envelope_id"):
        raise EnvelopeError("Replies must identify head.parent_envelope_id")
    validate_content(body["content_type"], body["content"])
    if not 0 <= tail["completeness_score"] <= 100:
        raise EnvelopeError("tail.completeness_score must be an integer from 0 through 100")
    if safety:
        if tail.get("sensitive") is True:
            raise EnvelopeError("Sensitive payload requires a separately authorized handling path")
        reject_forbidden(value)


def markdown_brief(text: str) -> tuple[dict[str, Any], list[str]]:
    matches = list(re.finditer(r"^##\s+([^\n]+)\n", text, re.MULTILINE))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        key = match.group(1).strip().casefold()
        if key in sections:
            raise EnvelopeError("Markdown brief has duplicate sections")
        sections[key] = text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)].strip()

    def values(name: str) -> list[str]:
        body = sections.get(name, "")
        bullets = re.findall(r"^\s*[-*]\s+(.+)$", body, re.MULTILINE)
        return [item.strip().strip("`") for item in bullets] if bullets else [body] if body else []

    content = {
        "task": sections.get("task", ""),
        "constraints": values("constraints") + values("ownership"),
        "acceptance": values("acceptance"),
        "original_markdown": text,
    }
    validate_content("brief", content)
    return content, values("inputs")


def body_for(content_type: str, path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        raise EnvelopeError("Cannot read UTF-8 content input") from error
    pointers: list[str] = []
    if content_type == "brief" and re.search(r"^##\s+Task\s*$", text, re.MULTILINE | re.IGNORECASE):
        content, pointers = markdown_brief(text)
    else:
        content = load_text(text)
        if isinstance(content, dict) and set(content) == {"content", "context_pointers"}:
            pointers = content["context_pointers"]
            content = content["content"]
    validate_content(content_type, content)
    body = {"content_type": content_type, "content": content, "context_pointers": pointers}
    _check_object(body, schema()["body"], "body")
    reject_forbidden(body)
    return body


def head_for(kind: str, sender: str, receiver: str) -> dict[str, Any]:
    head = {
        "envelope_id": envelope_id(), "envelope_schema_version": "1",
        "kind": kind, "from": sender, "to": receiver,
        "issued_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "pack": os.environ.get("LINTEL_ACTIVE_PACK", "_default"),
        "voice_tier": os.environ.get("VOICE_TIER", "internal"),
    }
    if os.environ.get("CYCLE_ID"):
        head["cycle_id"] = os.environ["CYCLE_ID"]
    _check_object(head, schema()["head"], "head")
    if kind not in schema()["kinds"]:
        raise EnvelopeError("Unknown head.kind")
    reject_forbidden(head)
    return head


def envelope_id() -> str:
    milliseconds = int(datetime.now(timezone.utc).timestamp() * 1000)
    value = int.from_bytes(milliseconds.to_bytes(6, "big") + secrets.token_bytes(10), "big")
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    return "".join(alphabet[(value >> shift) & 31] for shift in range(125, -1, -5))


def escape_hatches(content_type: str, sender: str) -> list[str]:
    templates = schema()["escape_hatches"].get(content_type)
    if templates is None:
        raise EnvelopeError("Unknown escape-hatch content type")
    values = [template.format(source=sender) for template in templates]
    reject_forbidden(values)
    return values


def evaluator(name: str, value: Any, root: Path) -> dict[str, Any]:
    if name == "security":
        try:
            reject_forbidden(value)
            return {"score": 100, "budget_used": 50, "notes": "No known forbidden pattern", "status": "PASS"}
        except EnvelopeError:
            return {"score": 0, "budget_used": 50, "notes": "Forbidden pattern detected", "status": "FAIL"}
    if name == "completeness":
        try:
            validate_envelope(value, safety=False)
            return {"score": 100, "budget_used": 30, "notes": "Structured contract satisfied", "status": "PASS"}
        except EnvelopeError:
            return {"score": 0, "budget_used": 30, "notes": "Structured contract incomplete", "status": "FAIL"}
    if name != "stale":
        raise EnvelopeError("Unknown evaluator")
    body = value.get("body") if isinstance(value, dict) else None
    pointers = body.get("context_pointers", []) if isinstance(body, dict) else None
    if not _strings(pointers):
        raise EnvelopeError("body.context_pointers must be a list of strings")
    missing, remote = 0, 0
    for pointer in pointers:
        if pointer.startswith(("https://", "http://")):
            remote += 1
            continue
        path = Path(pointer.removeprefix("file://"))
        path = path if path.is_absolute() else root / path
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            missing += 1
            continue
        if not path.exists():
            missing += 1
    return {"score": max(0, 100 - missing * 30), "budget_used": 40,
            "notes": f"Missing local pointers: {missing}; remote pointers not checked: {remote}",
            "status": "FAIL" if missing else "PASS"}


def checked_result(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) - {"score", "budget_used", "notes", "status", "hard_fail"}:
        raise EnvelopeError("Malformed evaluator result")
    if (
        type(value.get("score")) is not int or not 0 <= value["score"] <= 100
        or type(value.get("budget_used")) is not int or value["budget_used"] < 0
        or not isinstance(value.get("notes"), str)
        or value.get("status", "PASS") not in ("PASS", "FAIL")
        or ("hard_fail" in value and type(value["hard_fail"]) is not bool)
    ):
        raise EnvelopeError("Evaluator result has missing or invalid fields")
    reject_forbidden(value)
    return value


def policy_value(field: str, text: str, *, legacy: bool) -> str:
    if legacy:
        if field == "enabled" and text in ("true", "false"):
            value: Any = text == "true"
        elif field != "enabled" and text.startswith("[") and text.endswith("]"):
            value = [item.strip() for item in text[1:-1].split(",") if item.strip()]
        else:
            raise EnvelopeError("Policy accessor returned a missing or invalid value")
    else:
        try:
            value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
        except json.JSONDecodeError as error:
            raise EnvelopeError("Typed policy accessor did not return JSON") from error
    if field == "enabled":
        if type(value) is not bool:
            raise EnvelopeError("Handoff enabled policy must be boolean")
        return "true" if value else "false"
    if not _strings(value) or any(not re.fullmatch(r"[A-Za-z0-9_:/.-]+", item) for item in value):
        raise EnvelopeError("Evaluator/bypass policy must be a list of stable identifiers")
    reject_forbidden(value)
    return "[" + ", ".join(value) + "]"


def verify_audit_receipt(directory: Path, fields: Mapping[str, str], category: str = "brief-forge") -> None:
    try:
        with (directory / (category + ".jsonl")).open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    record = json.loads(line, object_pairs_hook=_pairs)
                except (ValueError, EnvelopeError):
                    continue
                if isinstance(record, dict) and all(record.get(key) == value for key, value in fields.items()):
                    return
    except (OSError, UnicodeError) as error:
        raise EnvelopeError("Audit persistence failed; no envelope was released") from error
    raise EnvelopeError("Audit receipt is missing; no envelope was released")


def finalize(value: Any, results: Mapping[str, Any], budget: int, directory: Path) -> dict[str, Any]:
    validate_envelope(value)
    if not isinstance(results, dict) or "security" not in results or budget < 0:
        raise EnvelopeError("Complete baseline evaluation and a nonnegative budget are required")
    checked = {name: checked_result(result) for name, result in results.items()}
    if sum(result["budget_used"] for result in checked.values()) > budget:
        raise EnvelopeError("Evaluator budget exhausted; partial evidence cannot be released")
    if any(result.get("status") == "FAIL" or result.get("hard_fail") is True for result in checked.values()):
        raise EnvelopeError("Evaluator failed; no envelope was released")
    score = min(result["score"] for result in checked.values())
    if score < 40:
        raise EnvelopeError("Evaluator score is below the release threshold")
    value["tail"].update(
        completeness_score=score, evaluators_run=list(checked),
        audit_pointer=str(directory / "brief-forge.jsonl"),
    )
    validate_envelope(value)
    return value


def audit_fields(value: Any) -> dict[str, str]:
    validate_envelope(value)
    serialized = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    return {
        "kind": "brief_forge_emitted", "decision": "validated-not-dispatched",
        "envelope_id": value["head"]["envelope_id"],
        "envelope_digest": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
        "content_type": value["body"]["content_type"],
        "score": str(value["tail"]["completeness_score"]),
        "evaluators_run": ",".join(value["tail"]["evaluators_run"]),
    }


def replay_check(value: Any, *, apply: bool, force: bool) -> str:
    validate_envelope(value)
    if apply and not force and value["tail"].get("replay_safe") is not True:
        raise EnvelopeError("Replay is not marked safe; explicit force is required to record apply intent")
    deprecated = value["tail"].get("deprecated_after")
    if apply and deprecated:
        try:
            expiry = datetime.fromisoformat(deprecated.replace("Z", "+00:00"))
            if expiry.tzinfo is None:
                raise ValueError
        except (ValueError, TypeError) as error:
            raise EnvelopeError("Replay expiry must be an ISO timestamp with a timezone") from error
        if expiry <= datetime.now(timezone.utc):
            raise EnvelopeError("Replay has expired")
    return value["head"]["envelope_id"]


def lookup_envelope(identity: str, directories: list[str]) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", identity):
        raise EnvelopeError("Invalid envelope identifier")
    metadata_only = False
    for directory in dict.fromkeys(directories):
        for path in sorted(Path(directory).glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                record = load_text(line)
                if not isinstance(record, dict):
                    raise EnvelopeError("Audit lookup encountered a malformed record")
                if isinstance(record.get("head"), dict) and record["head"].get("envelope_id") == identity:
                    validate_envelope(record)
                    return record
                if record.get("envelope_id") == identity:
                    metadata_only = True
    if metadata_only:
        raise EnvelopeError("Audit record is metadata-only; supply the original envelope artifact and compare its digest")
    raise EnvelopeError("Envelope identifier not found in the selected audit directories")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("id")
    validator = commands.add_parser("validate")
    validator.add_argument("input", nargs="?")
    validator.add_argument("--stdin", action="store_true")
    validator.add_argument("--quiet", action="store_true")
    constructor = commands.add_parser("construct")
    for arg in ("kind", "sender", "receiver", "content_type", "content_file"):
        constructor.add_argument(arg)
    head = commands.add_parser("head")
    for arg in ("kind", "sender", "receiver"):
        head.add_argument(arg)
    body = commands.add_parser("body")
    body.add_argument("content_type")
    body.add_argument("content_file")
    escapes = commands.add_parser("escape-hatches")
    escapes.add_argument("content_type")
    escapes.add_argument("sender")
    tail = commands.add_parser("tail")
    tail.add_argument("score", type=int)
    tail.add_argument("entries", nargs="+")
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("name")
    evaluate.add_argument("input")
    aggregate = commands.add_parser("aggregate")
    aggregate.add_argument("entries", nargs="*")
    wrap = commands.add_parser("wrap-result")
    wrap.add_argument("name")
    wrap.add_argument("result")
    policy = commands.add_parser("policy-value")
    policy.add_argument("field", choices=("enabled", "evaluators", "eligible_skills"))
    policy.add_argument("value")
    policy.add_argument("--legacy-accessor", action="store_true")
    convert = commands.add_parser("json")
    convert.add_argument("input")
    metadata = commands.add_parser("metadata")
    metadata.add_argument("input")
    finish = commands.add_parser("finalize")
    finish.add_argument("input")
    finish.add_argument("results")
    finish.add_argument("budget", type=int)
    finish.add_argument("audit_dir")
    receipt = commands.add_parser("receipt")
    receipt.add_argument("audit_dir")
    receipt.add_argument("receipt_id")
    receipt.add_argument("kind")
    receipt.add_argument("--category", choices=("brief-forge", "envelope-replay"), default="brief-forge")
    audit = commands.add_parser("audit-fields")
    audit.add_argument("input")
    emit = commands.add_parser("release")
    emit.add_argument("input")
    emit.add_argument("audit_dir")
    lookup = commands.add_parser("lookup")
    lookup.add_argument("identity")
    lookup.add_argument("directories", nargs="+")
    for command in ("replay-check", "replay-preview"):
        replay = commands.add_parser(command)
        replay.add_argument("input")
        replay.add_argument("--apply", action="store_true")
        replay.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        value: Any
        if args.command == "id":
            print(envelope_id())
            return 0
        if args.command == "validate":
            if args.stdin == bool(args.input):
                raise EnvelopeError("Supply one input file or --stdin")
            value = load_text(sys.stdin.read()) if args.stdin else load_document(Path(args.input))
            validate_envelope(value)
            if not args.quiet:
                print("envelope OK")
            return 0
        if args.command in ("construct", "head"):
            value = {"head": head_for(args.kind, args.sender, args.receiver)}
        if args.command in ("construct", "body"):
            if args.command == "body":
                value = {}
            value["body"] = body_for(args.content_type, Path(args.content_file))
        if args.command == "construct":
            value["tail"] = {"completeness_score": 0, "evaluators_run": [],
                             "escape_hatches": escape_hatches(args.content_type, args.sender),
                             "audit_pointer": "pending-local-audit"}
            validate_envelope(value)
        if args.command == "escape-hatches":
            print("\n".join(escape_hatches(args.content_type, args.sender)))
            return 0
        if args.command == "tail":
            if len(args.entries) < 2 or not 0 <= args.score <= 100:
                raise EnvelopeError("Tail needs valid score, escape hatches and audit pointer")
            value = {"tail": {"completeness_score": args.score, "evaluators_run": [entry.split(":", 1)[0] for entry in args.entries[:-2]],
                              "escape_hatches": args.entries[-2].splitlines(), "audit_pointer": args.entries[-1]}}
            _check_object(value["tail"], schema()["tail"], "tail")
            reject_forbidden(value)
        if args.command in ("head", "body", "tail"):
            for section, fields in value.items():
                print(section + ":")
                for name, item in fields.items():
                    print("  " + name + ": " + json.dumps(item, ensure_ascii=True, allow_nan=False))
            return 0
        if args.command == "evaluate":
            value = evaluator(args.name, load_document(Path(args.input)), Path(os.environ.get("LINTEL_REPO_ROOT", os.getcwd())))
        if args.command == "aggregate":
            values = [load_text(entry.split(":", 1)[1]) for entry in args.entries if ":" in entry]
            if not values or len(values) != len(args.entries) or any(
                not isinstance(value, dict) or type(value.get("score")) is not int or not 0 <= value["score"] <= 100
                for value in values
            ):
                raise EnvelopeError("Nonempty valid evaluator results are required")
            print(min(value["score"] for value in values))
            return 0
        if args.command == "wrap-result":
            if not re.fullmatch(r"[a-z][a-z0-9_-]*", args.name):
                raise EnvelopeError("Invalid evaluator identifier")
            value = {args.name: checked_result(load_text(args.result))}
        if args.command == "policy-value":
            print(policy_value(args.field, args.value, legacy=args.legacy_accessor))
            return 0
        if args.command in ("json", "metadata"):
            value = load_document(Path(args.input))
            validate_envelope(value)
            if args.command == "metadata":
                print(json.dumps({"head": value["head"], "tail": value["tail"]}, separators=(",", ":")))
                return 0
        if args.command == "finalize":
            entries = []
            for line in Path(args.results).read_text(encoding="utf-8").splitlines():
                entry = load_text(line)
                if not isinstance(entry, dict) or len(entry) != 1:
                    raise EnvelopeError("Each evaluator record must contain exactly one named result")
                entries.extend(entry.items())
            results = _pairs(entries)
            value = finalize(load_document(Path(args.input)), results, args.budget, Path(args.audit_dir))
        if args.command == "receipt":
            verify_audit_receipt(Path(args.audit_dir), {"audit_receipt": args.receipt_id, "kind": args.kind}, args.category)
            return 0
        if args.command in ("audit-fields", "release"):
            value = load_document(Path(args.input))
            fields = audit_fields(value)
            if args.command == "audit-fields":
                print("|".join(fields[key] for key in ("envelope_id", "envelope_digest", "content_type", "score", "evaluators_run")))
                return 0
            verify_audit_receipt(Path(args.audit_dir), fields)
        if args.command == "lookup":
            value = lookup_envelope(args.identity, args.directories)
        if args.command in ("replay-check", "replay-preview"):
            value = load_document(Path(args.input))
            identity = replay_check(value, apply=args.apply, force=args.force)
            if args.command == "replay-check":
                print(identity)
            else:
                print("LINTEL ENVELOPE REPLAY - " + ("APPLY INTENT RECORDED" if args.apply else "DRY-RUN"))
                print("envelope_id: " + identity)
                print("The operator's session owns dispatch; this tool does not invoke a receiver.")
                print("\n".join(json.dumps(value, indent=2, ensure_ascii=True).splitlines()[:40]))
            return 0
        print(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False))
        return 0
    except (EnvelopeError, OSError, UnicodeError, ValueError, TypeError, RecursionError) as error:
        message = str(error) if isinstance(error, EnvelopeError) else "Envelope operation failed; no payload was released"
        if not getattr(args, "quiet", False):
            print("ENVELOPE BLOCKED: " + message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
