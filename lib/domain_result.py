# component: domain-result
# implements: ADR-0028, ADR-0029, ADR-0031
# intent: .claude/plans/universal-implementation/packages/P09.md
# constraints: data publication and fresh evidence checks only; no P08, dispatch or release clearance
# last_intent_review: 2026-09-22
"""One domain data contract over accepted work, control, profile and owned-I/O APIs."""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import math
from pathlib import Path, PureWindowsPath
import re
import stat
import sys
from typing import Any, Optional

SOURCE_ROOT = Path(__file__).absolute().parent.parent
MAX_DOCUMENT_BYTES = 2 * 1024 * 1024
MAX_EVIDENCE_BYTES = 16 * 1024 * 1024
Json = dict[str, Any]


class DomainError(ValueError):
    """Unusable domain data or unverified identity; never acceptance."""


def _source_preflight() -> None:
    for relative in (
        "lib/domain-result-schema.json", "lib/context_safety.py", "lib/native_paths.py",
        "lib/review_contract.py", "lib/review-schema.json", "lib/markdown_source.py",
        "lib/profile_context.py", "lib/profile-context-schema.json",
    ):
        path = SOURCE_ROOT / relative
        for part in (path, *path.parents):
            info = part.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ImportError(f"Linked trusted domain resource refused: {relative}")
        if not path.is_file():
            raise ImportError(f"Required trusted domain resource missing: {relative}")


_source_preflight()
sys.path.insert(0, str(SOURCE_ROOT / "lib"))
import context_safety as safety  # noqa: E402
from profile_context import (  # noqa: E402
    ProfileConfig, ProfileError, required_policy, validate_profile_reference, verify_profile_reference,
)
from review_contract import (  # noqa: E402
    CONTRACT_VERSION, ContractError, canonical_json, content_digest, evidence_manifest,
    load_json, validate_context, validate_control, validate_shape, verify_context, verify_qa,
)


@lru_cache(maxsize=1)
def _schema() -> Json:
    data = safety.read_owned(safety.checked_root(SOURCE_ROOT), "lib/domain-result-schema.json",
                             MAX_DOCUMENT_BYTES)[0]
    return load_json(data.decode("utf-8"))


def _shape(value: Any, schema: Json, location: str) -> None:
    """Interpret only this envelope's shape; P05 definitions keep their own validator."""
    supported = {"$ref", "anyOf", "type", "const", "enum", "required", "properties",
                 "additionalProperties", "items", "minItems", "maxItems",
                 "pattern", "minimum", "maximum"}
    if set(schema) - supported:
        raise DomainError("Unsupported domain schema keyword")
    if "$ref" in schema:
        reference = schema["$ref"]
        if reference.startswith("review-schema.json#/$defs/"):
            validate_shape(value, reference.rsplit("/", 1)[1])
        elif reference.startswith("#/$defs/"):
            _shape(value, _schema()["$defs"][reference.rsplit("/", 1)[1]], location)
        else:
            raise DomainError("Unsupported domain schema reference")
        return
    if "anyOf" in schema:
        for candidate in schema["anyOf"]:
            try:
                _shape(value, candidate, location)
                return
            except (DomainError, ContractError):
                continue
        raise DomainError(f"{location}: invalid allowed shape")
    types = {"object": isinstance(value, dict), "array": isinstance(value, list),
             "string": isinstance(value, str), "integer": type(value) is int,
             "number": type(value) is int or (type(value) is float and math.isfinite(value)),
             "null": value is None}
    if schema.get("type") and not types.get(schema["type"], False):
        raise DomainError(f"{location}: invalid type")
    if "const" in schema and (value != schema["const"] or type(value) is not type(schema["const"])):
        raise DomainError(f"{location}: invalid constant")
    if "enum" in schema and value not in schema["enum"]:
        raise DomainError(f"{location}: invalid enum")
    if isinstance(value, str) and "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
        raise DomainError(f"{location}: invalid identifier")
    if type(value) in (int, float) and (
        value < schema.get("minimum", -math.inf) or value > schema.get("maximum", math.inf)
    ):
        raise DomainError(f"{location}: value outside bounds")
    if isinstance(value, dict):
        missing = set(schema.get("required", ())) - value.keys()
        properties = schema.get("properties", {})
        if missing or (schema.get("additionalProperties") is False and value.keys() - properties.keys()):
            raise DomainError(f"{location}: missing or unexpected fields")
        for name, definition in properties.items():
            if name in value:
                _shape(value[name], definition, f"{location}.{name}")
    if isinstance(value, list):
        if not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", MAX_DOCUMENT_BYTES):
            raise DomainError(f"{location}: item count outside bounds")
        for item in value:
            _shape(item, schema.get("items", {}), f"{location}[]")


def _validate(data: Json, definition: str) -> None:
    try:
        encoded = canonical_json(data).encode("utf-8")
    except (TypeError, ValueError, RecursionError) as error:
        raise DomainError("Domain data must be finite JSON") from error
    if len(encoded) + 1 > MAX_DOCUMENT_BYTES:
        raise DomainError("Domain document exceeds its byte bound")
    _shape(data, {"$ref": f"#/$defs/{definition}"}, definition)


def _path(value: str) -> str:
    safety.relative_path(value)
    safety.path_identity(PureWindowsPath("C:\\") / value)
    if any(part.casefold() == ".git" for part in value.split("/")):
        raise DomainError("Git metadata is not domain data")
    return value


def _unique_paths(paths: list[str]) -> None:
    seen: set[str] = set()
    for path in paths:
        key = safety.path_key(_path(path))
        if key in seen:
            raise DomainError("Duplicate or case-aliased domain paths")
        seen.add(key)


def _checkpoints(request: Json):
    for domain in request["domains"]:
        for checkpoint in domain["checkpoints"]:
            yield domain["id"], checkpoint


def record_root(request: Json) -> str:
    """Filesystem-safe data namespace, not a lifecycle ledger or inferred source root."""
    return (f".claude/runtime/state/domains/{request['operation_id']}"
            f"/i{request['iteration']:04d}")


def validate_request(data: Json) -> Json:
    """Validate a caller-constructed request without parsing tasks or creating a profile."""
    _validate(data, "request")
    context = data["input_context"]
    validate_context(context)
    if context["work"]["work_map"] is None:
        raise DomainError("Mapped domain data needs the caller's original P05 work binding")
    if context["profile"] is None:
        raise DomainError("An explicit pinned P07 reference is required for domain data")
    validate_profile_reference(context["profile"])
    domains = [domain["id"] for domain in data["domains"]]
    if len(domains) != len(set(domains)):
        raise DomainError("Duplicate expected domain")
    controls, slots, artifacts = [], [], []
    prefix = record_root(data) + "/"
    for domain in data["domains"]:
        ids = [checkpoint["id"] for checkpoint in domain["checkpoints"]]
        if len(ids) != len(set(ids)):
            raise DomainError("Duplicate expected checkpoint")
    for _, checkpoint in _checkpoints(data):
        controls.extend(checkpoint["control_ids"])
        for kind in ("start", "result"):
            path = _path(checkpoint[kind]["path"])
            if not path.startswith(prefix) or not path.endswith(".json"):
                raise DomainError("Publication slot is outside this explicit operation/iteration")
            slots.append(path)
        _unique_paths(checkpoint["artifacts"])
        artifacts.extend(checkpoint["artifacts"])
    if len(controls) != len(set(controls)) or set(controls) != {
        item["id"] for item in context["qa_requirements"]
    }:
        raise DomainError("Checkpoints must assign each immutable QA obligation exactly once")
    _unique_paths(slots)
    _unique_paths(list(dict.fromkeys(artifacts)))
    if {safety.path_key(path) for path in slots} & {safety.path_key(path) for path in artifacts}:
        raise DomainError("Checkpoint metadata cannot be its own artifact")
    return deepcopy(data)


def _spec(record: Json, request: Json) -> Json:
    for domain, checkpoint in _checkpoints(request):
        if domain == record["domain"] and checkpoint["id"] == record["checkpoint"]:
            return checkpoint
    raise DomainError("Record names an unexpected domain or checkpoint")


def validate_checkpoint(data: Json, request: Json) -> Json:
    """Shape/mode/obligation checks only; claimed actors and outcomes are not authority."""
    validate_request(request)
    if not isinstance(data, dict):
        raise DomainError("Checkpoint/result must be a JSON object")
    kind = data.get("kind")
    if kind not in ("domain-checkpoint", "domain-result"):
        raise DomainError("Expected checkpoint or result data")
    definition = "checkpoint" if kind == "domain-checkpoint" else "result"
    _validate(data, definition)
    _path(data["request"]["path"])
    checkpoint = _spec(data, request)
    if data["receiver"] != checkpoint["receiver"]:
        raise DomainError("Receiver role/mode differs from the explicit request")
    if definition == "result":
        _path(data["start"]["path"])
        if data["start"]["path"] != checkpoint["start"]["path"]:
            raise DomainError("Result does not name its expected start record")
        expected = {item["id"]: item for item in request["input_context"]["qa_requirements"]}
        observed = [validate_control(control) for control in data["controls"]]
        ids = [control["id"] for control in observed]
        if len(ids) != len(set(ids)) or set(ids) != set(checkpoint["control_ids"]):
            raise DomainError("Result control inventory differs from its checkpoint")
        for control in observed:
            requirement = expected[control["id"]]
            if {key: control[key] for key in requirement} != requirement:
                raise DomainError("Result changed an immutable P05 QA obligation")
        for field in ("artifacts", "evidence"):
            _unique_paths([reference["path"] for reference in data[field]])
        if not {item["path"] for item in data["artifacts"]} <= set(checkpoint["artifacts"]):
            raise DomainError("Result refers to an undeclared artifact")
        evidence = {path for control in observed for path in control["evidence"]}
        if {item["path"] for item in data["evidence"]} != evidence:
            raise DomainError("Evidence manifest does not match control evidence")
        for decision in data["decisions"]:
            if decision["artifact"] not in {item["path"] for item in data["artifacts"]}:
                raise DomainError("Decision needs a declared artifact reference")
    return deepcopy(data)


def validate_result(data: Json, request: Json) -> Json:
    result = validate_checkpoint(data, request)
    if result["kind"] != "domain-result":
        raise DomainError("A start checkpoint is not a result")
    return result


def read_document(repo: Path, relative: str) -> tuple[Json, Json]:
    """Read one bounded, ordinary owned file using P03 and P05 strict JSON."""
    data, state = safety.read_owned(safety.checked_root(repo), _path(relative), MAX_DOCUMENT_BYTES)
    return load_json(data.decode("utf-8-sig")), {"path": relative, "sha256": state["sha256"]}


def _request(repo: Path, path: str) -> tuple[Json, Json]:
    data, reference = read_document(repo, path)
    request = validate_request(data)
    reserved = [cp[kind]["path"] for _, cp in _checkpoints(request) for kind in ("start", "result")]
    reserved += [item for _, cp in _checkpoints(request) for item in cp["artifacts"]]
    if safety.path_key(path) in {safety.path_key(item) for item in reserved}:
        raise DomainError("Request cannot be a checkpoint publication or artifact")
    return request, reference


def _start(repo: Path, result: Json, request: Json, request_ref: Json) -> tuple[Json, Json]:
    data, reference = read_document(repo, result["start"]["path"])
    validate_checkpoint(data, request)
    if data["kind"] != "domain-checkpoint" or reference != result["start"]:
        raise DomainError("Start record identity differs")
    if data["request"] != request_ref or any(
        data[key] != result[key] for key in ("domain", "checkpoint", "receiver", "producer")
    ):
        raise DomainError("Result differs from its started checkpoint/producer")
    return data, reference


def record_checkpoint(
    repo: Path, request_path: str, record: Json, *, output: str,
    expected_file_state: Optional[Json],
) -> Json:
    """Publish one owned data record; explicit original preimage is mandatory, not inferred."""
    root = safety.checked_root(repo)
    request, reference = _request(root, request_path)
    validate_checkpoint(record, request)
    if record["request"] != reference:
        raise DomainError("Record request identity differs from the supplied request")
    slot = _spec(record, request)["start" if record["kind"] == "domain-checkpoint" else "result"]
    if _path(output) != slot["path"]:
        raise DomainError("Output is not the explicit owned publication slot")
    _validate({"state": expected_file_state}, "expectedState")
    if expected_file_state != slot["expected_state"]:
        raise DomainError("Supplied expected state is not the request's original expected file state")
    if safety.file_state(root, output) != expected_file_state:
        raise DomainError("Publication conflicts with the original expected file state")
    if record["kind"] == "domain-result":
        _start(root, record, request, reference)
    data = (canonical_json(record) + "\n").encode("utf-8")
    safety.atomic_write(root, output, data,
                        mode=expected_file_state["mode"] if expected_file_state is not None else 0o600,
                        expected=expected_file_state, check_expected=True)
    actual, state = safety.read_owned(root, output, MAX_DOCUMENT_BYTES)
    if actual != data:
        raise DomainError("Published data failed readback; preserve the observed state")
    return {"operation": "record", "status": "recorded", "verification": "not_performed",
            "reference": {"path": output, "sha256": state["sha256"]},
            "release_clearance": False}


def _bound_file(repo: Path, path: str, expected: Json, *, digest: Optional[str] = None) -> Json:
    _, state = safety.read_owned(repo, _path(path), MAX_EVIDENCE_BYTES)
    entries = {entry["path"]: entry["worktree"] for entry in expected["snapshot"]["entries"]}
    selected = entries.get(path)
    if selected is None or selected["kind"] != "file" or selected["sha256"] != state["sha256"]:
        raise DomainError(f"File is not bound as current regular content in the selected P05 context: {path}")
    if digest is not None and digest != state["sha256"]:
        raise DomainError(f"Recorded artifact/evidence identity changed: {path}")
    return {"path": path, "sha256": state["sha256"]}


def _current_context(repo: Path, request: Json, expected: Json, config: ProfileConfig) -> None:
    validate_context(expected)
    initial = request["input_context"]
    if {key: value for key, value in initial.items() if key != "snapshot"} != {
        key: value for key, value in expected.items() if key != "snapshot"
    }:
        raise DomainError("Caller-selected P05 context changed work/profile/attempt/obligations")
    if initial["snapshot"]["base"] != expected["snapshot"]["base"] or not set(
        initial["snapshot"]["selection"]
    ) <= set(expected["snapshot"]["selection"]):
        raise DomainError("Final P05 selection must retain the original base and input selections")
    if config.repo != repo or config.source != SOURCE_ROOT.resolve():
        raise DomainError("Profile configuration must name this target and trusted source")
    profile = verify_profile_reference(expected["profile"], config)
    if required_policy(profile) != expected["required_policy"]:
        raise DomainError("Live P07 required policy differs from the selected P05 context")
    verify_context(repo, expected)


def _diagnostic(error: Exception) -> str:
    return f"{error.code}: {error}" if isinstance(error, ProfileError) else str(error)


def _verified_checkpoint(repo: Path, request: Json, request_ref: Json, checkpoint: Json,
                         expected: Json) -> Json:
    result, reference = read_document(repo, checkpoint["result"]["path"])
    validate_result(result, request)
    if _spec(result, request) != checkpoint or result["request"] != request_ref:
        raise DomainError("Checkpoint result belongs to another request or expected slot")
    _, started = _start(repo, result, request, request_ref)
    _bound_file(repo, reference["path"], expected, digest=reference["sha256"])
    _bound_file(repo, started["path"], expected, digest=started["sha256"])
    if {item["path"] for item in result["artifacts"]} != set(checkpoint["artifacts"]):
        raise DomainError("Expected checkpoint artifacts are missing")
    for item in result["artifacts"] + result["evidence"]:
        _bound_file(repo, item["path"], expected, digest=item["sha256"])
    if evidence_manifest(repo, result["controls"]) != sorted(result["evidence"], key=lambda item: item["path"]):
        raise DomainError("P05 control evidence changed")
    return result


def verify_result(repo: Path, request_path: str, *, expected: Json, profile_config: ProfileConfig) -> Json:
    """Re-read all expected results and live context; never use a cached verified flag."""
    outcome: Json = {"operation": "verify", "ok": False, "blocked": True, "status": "unverified",
                     "verification": "incomplete", "release_clearance": False,
                     "review": "not_evaluated", "problems": [], "advisories": [], "domains": [], "qa": None}
    try:
        root = safety.checked_root(repo)
        request, request_ref = _request(root, request_path)
        _current_context(root, request, expected, profile_config)
        _bound_file(root, request_path, expected, digest=request_ref["sha256"])
        controls, producer_problems, producer_advice = [], [], []
        for domain in request["domains"]:
            domain_view = {"id": domain["id"], "checkpoints": []}
            outcome["domains"].append(domain_view)
            for checkpoint in domain["checkpoints"]:
                try:
                    result = _verified_checkpoint(root, request, request_ref, checkpoint, expected)
                except (OSError, ValueError, UnicodeError) as error:
                    message = f"{domain['id']}/{checkpoint['id']}: checkpoint evidence unavailable: {_diagnostic(error)}"
                    outcome["problems"].append(message)
                    domain_view["checkpoints"].append({"id": checkpoint["id"], "status": "unverified"})
                    continue
                controls.extend(result["controls"])
                domain_view["checkpoints"].append({
                    "id": checkpoint["id"], "declared_status": result["status"],
                    "producer": result["producer"], "receiver": result["receiver"],
                    "advisory_score": result.get("advisory_score"),
                })
                if result["status"] != "pass":
                    target = producer_problems if any(
                        control["requirement"] == "mandatory"
                        for control in result["controls"]
                    ) else producer_advice
                    target.append(f"{domain['id']}/{checkpoint['id']}: producer reported {result['status']}")
        if outcome["problems"]:
            return outcome
        qa = {"schema_version": CONTRACT_VERSION, "context_digest": content_digest(expected),
              "controls": controls, "evidence": evidence_manifest(root, controls)}
        checked = verify_qa(root, qa, expected=expected)
        _current_context(root, request, expected, profile_config)
        outcome.update(
            qa=qa, controls=checked, verification="current_inputs",
            problems=checked["blockers"] + producer_problems,
            advisories=checked["advisories"] + producer_advice,
            status=checked["status"],
        )
        outcome["blocked"] = bool(outcome["problems"])
        outcome["ok"] = not outcome["blocked"]
        if outcome["blocked"] and outcome["status"] == "pass":
            outcome["status"] = "unverified"
    except (OSError, ValueError, UnicodeError) as error:
        outcome.update(status="error", verification="incomplete")
        outcome["problems"].append(_diagnostic(error))
    return outcome


def summarize(repo: Path, request_path: str, *, expected: Json, profile_config: ProfileConfig) -> Json:
    """Composition uses exactly the same fresh verifier, not serialized outcome Booleans."""
    result = verify_result(repo, request_path, expected=expected, profile_config=profile_config)
    result["operation"] = "summary"
    return result
