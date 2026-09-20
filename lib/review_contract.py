# component: review-contract
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/packages/P05.md
# constraints: read-only Git/filesystem; declared identity is not authentication
# last_intent_review: 2026-09-20
"""Shared result validation and explicit content identity. No dispatch or audit writes."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from datetime import datetime
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from typing import Any, Optional, Union

Json = dict[str, Any]
AUDIT_RECORD = ".claude/runtime/audit/reviews.jsonl"


class ContractError(ValueError):
    """Invalid, unavailable or ambiguous evidence; never a passing result."""


def _pairs(pairs: list[tuple[str, Any]]) -> Json:
    result: Json = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise ContractError(f"Non-finite JSON value: {value}")


def _number(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ContractError(f"Non-finite JSON number: {value}")
    return number


def load_json(text: str) -> Json:
    """Parse one object strictly, including nested duplicate keys and NaN/Infinity."""
    try:
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_number)
    except (json.JSONDecodeError, UnicodeError, RecursionError) as error:
        raise ContractError(f"Invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise ContractError("Expected a JSON object")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def content_digest(value: Any) -> str:
    """SHA-256 of canonical JSON, including the whole decision for corroboration."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def _schema() -> Json:
    return load_json(Path(__file__).with_name("review-schema.json").read_text(encoding="utf-8"))


def _validate(value: Any, schema: Json, location: str) -> None:
    # Only the keywords used by the shipped schema are needed; no runtime dependency.
    supported = {
        "$ref", "anyOf", "type", "const", "enum", "minLength", "pattern",
        "minimum", "maximum", "minItems", "items", "uniqueItems", "required",
        "properties", "additionalProperties", "title", "description", "$comment",
    }
    if set(schema) - supported:
        raise ContractError(f"{location}: unsupported shipped schema keywords: {sorted(set(schema) - supported)}")
    if "$ref" in schema:
        _validate(value, _schema()["$defs"][schema["$ref"].split("/")[-1]], location)
        return
    if "anyOf" in schema:
        for choice in schema["anyOf"]:
            try:
                _validate(value, choice, location)
                return
            except ContractError:
                continue
        raise ContractError(f"{location}: does not match an allowed shape")
    kind = schema.get("type")
    types = {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "boolean": type(value) is bool,
        "integer": type(value) is int,
        "number": type(value) in (int, float) and math.isfinite(value),
        "null": value is None,
    }
    if kind and not types[kind]:
        raise ContractError(f"{location}: expected {kind}")
    if "const" in schema and (value != schema["const"] or type(value) is not type(schema["const"])):
        raise ContractError(f"{location}: expected {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise ContractError(f"{location}: unsupported value {value!r}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or (
            "pattern" in schema and re.search(schema["pattern"], value) is None
        ):
            raise ContractError(f"{location}: invalid string")
    if type(value) in (int, float):
        if value < schema.get("minimum", -math.inf) or value > schema.get("maximum", math.inf):
            raise ContractError(f"{location}: outside allowed range")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise ContractError(f"{location}: missing required items")
        if schema.get("uniqueItems") and len({canonical_json(v) for v in value}) != len(value):
            raise ContractError(f"{location}: duplicate items")
        for index, item in enumerate(value):
            _validate(item, schema.get("items", {}), f"{location}[{index}]")
    if isinstance(value, dict):
        missing = set(schema.get("required", [])) - value.keys()
        if missing:
            raise ContractError(f"{location}: missing {', '.join(sorted(missing))}")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in properties:
                _validate(item, properties[key], f"{location}.{key}")
            elif additional is False:
                raise ContractError(f"{location}: unexpected field {key}")
            elif isinstance(additional, dict):
                _validate(item, additional, f"{location}.{key}")


def validate_shape(value: Any, definition: str) -> None:
    """Validate one named definition from the single shipped schema."""
    _validate(value, _schema()["$defs"][definition], definition)


def validate_control(control: Mapping[str, Any]) -> Json:
    if not isinstance(control, Mapping):
        raise ContractError("A control must be an object")
    result = deepcopy(dict(control))
    validate_shape(result, "control")
    for path in result["evidence"]:
        relative_path(path)
    return result


def _observed_status(control: Json) -> tuple[str, str]:
    status = control["status"]
    policy = control["policy"]
    grounded = bool(policy["source"] and policy["version"] and control["evidence"])
    if control["applicability"] == "unknown":
        return "unverified", "Applicability is unknown"
    if not grounded:
        return "unverified", "Policy source/version or evidence is missing"
    if control["applicability"] == "not_applicable":
        return status, "Grounded not-applicable decision"
    if status != "pass":
        return status, control["reason"]
    observation = control["observation"]
    if control["kind"] == "tests":
        counts = [observation.get(key) for key in ("executed", "failed", "skipped")]
        if any(type(value) is not int or value < 0 for value in counts):
            return "unverified", "Test counts are unavailable"
        executed, failed, skipped = counts
        exit_code = observation.get("exit_code")
        if type(exit_code) is not int or not isinstance(observation.get("command"), str) or not observation["command"].strip():
            return "unverified", "Test command or exit code is unavailable"
        if failed or exit_code != 0:
            return "fail", "Tests failed or the runner did not exit successfully"
        if not executed or skipped:
            return "unverified", "Zero executed tests or skipped acceptance checks"
    elif control["kind"] == "browser":
        states, tool = observation.get("states"), observation.get("tool")
        if (
            observation.get("executed") is not True or not isinstance(tool, str) or not tool.strip()
            or not isinstance(states, list) or not states
            or any(not isinstance(state, str) or not state.strip() for state in states)
        ):
            return "unverified", "Browser/tool/state observations are missing"
    elif control["kind"] == "contrast":
        ratio, size = observation.get("ratio"), observation.get("text_size")
        if type(ratio) not in (int, float) or not math.isfinite(ratio) or not 1 <= ratio <= 21 or size not in ("normal", "large"):
            return "unverified", "A measured ratio and normal/large text classification are required"
        if ratio < (4.5 if size == "normal" else 3.0):
            return "fail", "Measured text contrast fails WCAG AA SC 1.4.3"
    elif control["kind"] == "policy":
        if not all(policy[key] for key in ("jurisdiction", "actor", "effective_date")):
            return "unverified", "Regulatory applicability needs jurisdiction, actor and effective date"
    return status, control["reason"]


def evaluate_controls(controls: Sequence[Mapping[str, Any]], *, required_policy: Mapping[str, Any]) -> Json:
    """Pure evaluation; mandatory unknown/error/failure cannot be averaged away."""
    if not isinstance(controls, (list, tuple)) or not isinstance(required_policy, Mapping):
        raise ContractError("Controls must be an array and required_policy an object")
    policy = dict(required_policy)
    validate_shape(policy, "requiredPolicy")
    results, blockers, advisories = [], [], []
    seen: set[str] = set()
    for item in controls:
        control = validate_control(item)
        if control["id"] in seen:
            raise ContractError(f"Duplicate control ID: {control['id']}")
        seen.add(control["id"])
        status, reason = _observed_status(control)
        exempt = (
            control["applicability"] == "not_applicable"
            and bool(control["policy"]["source"] and control["policy"]["version"] and control["evidence"])
            and control["status"] not in ("error", "fail")
        )
        unresolved = not exempt and (control["applicability"] != "applicable" or status != "pass")
        result = {**control, "effective_status": status, "effective_reason": reason, "exempt": exempt}
        results.append(result)
        if unresolved:
            target = blockers if control["requirement"] == "mandatory" else advisories
            target.append(f"{control['id']}: {reason}")
    if policy["required"]:
        if (
            policy["status"] != "loaded" or not (policy["source"] or "").strip()
            or not (policy["version"] or "").strip()
            or policy["applicability"] == "unknown"
        ):
            blockers.append("required-policy: load/source/version/applicability is unresolved")
        elif policy["applicability"] == "applicable" and not any(c["requirement"] == "mandatory" for c in results):
            blockers.append("required-policy: mandatory control results are missing")
    elif policy["status"] in ("unverified", "error"):
        advisories.append(f"optional-policy: {policy['status']}; no successful activation is claimed")
    applicable = [c for c in results if not c["exempt"]]
    statuses = {c["effective_status"] for c in applicable}
    aggregate = next((s for s in ("error", "fail", "unverified") if s in statuses), "pass")
    if not applicable:
        aggregate = "unverified"
    if blockers and aggregate == "pass":
        aggregate = "unverified"
    return {
        "schema_version": 1,
        "status": aggregate, "blocked": bool(blockers), "blockers": blockers, "advisories": advisories,
        "assurance": "no_applicable_controls" if not applicable else "observed_controls",
        "controls": results, "required_policy": policy,
    }


def relative_path(value: str, *, allow_root: bool = False) -> str:
    if not isinstance(value, str) or not value or any(ord(c) < 32 for c in value) or ":" in value:
        raise ContractError(f"Invalid repository-relative path: {value!r}")
    value = value.replace("\\", "/")
    if value == "." and allow_root:
        return value
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ("", ".", "..") for p in value.rstrip("/").split("/")):
        raise ContractError(f"Unsafe repository-relative path: {value!r}")
    if any(p.casefold() == ".git" for p in path.parts):
        raise ContractError("Git metadata is not review input")
    return path.as_posix()


def _path(repo: Path, value: str, *, regular: bool = False) -> Path:
    name = relative_path(value)
    path = repo / name
    current = repo
    for part in PurePosixPath(name).parts[:-1]:
        current = current / part
        if current.is_symlink() or (current.exists() and not current.is_dir()):
            raise ContractError(f"Input traverses a symlink or non-directory: {name}")
        if not current.resolve().is_relative_to(repo):
            raise ContractError(f"Input escapes repository: {name}")
    if regular and (path.is_symlink() or not path.is_file()):
        raise ContractError(f"Evidence/authority must be a regular local file: {name}")
    if regular and not path.resolve().is_relative_to(repo):
        raise ContractError(f"Evidence/authority escapes repository: {name}")
    return path


def _git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "--no-pager", "-C", str(repo), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    )
    if result.returncode:
        raise ContractError(f"Git {' '.join(args[:2])} failed: {result.stderr.decode('utf-8', 'replace').strip()}")
    return result.stdout


def _root(repo: Path) -> Path:
    root = Path(repo).resolve()
    reported = Path(os.fsdecode(_git(root, "rev-parse", "--show-toplevel")).strip()).resolve()
    if root != reported:
        raise ContractError("--repo must name the repository root")
    return root


def resolve_commit(repo: Path, value: str) -> str:
    if not isinstance(value, str) or not value.strip() or value.startswith("-"):
        raise ContractError("A nonempty bound commit is required")
    result = _git(repo, "rev-parse", "--verify", f"{value}^{{commit}}").decode().strip()
    validate_shape(result, "commit")
    return result


def _selected(path: str, selection: Sequence[str]) -> bool:
    return any(s == "." or path == s or path.startswith(s + "/") for s in selection)


def _snapshot_digest(value: Json) -> str:
    # Global HEAD is provenance. Per-path HEAD/index/base remain part of identity,
    # allowing unrelated commits without confusing changed selected content.
    return content_digest({key: item for key, item in value.items() if key not in ("head", "result_digest")})


def _absent() -> Json:
    return {"kind": "absent", "mode": "000000", "sha256": None}


def _record_path(repo: Path, value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = relative_path(value)
    if re.fullmatch(r"\.claude/runtime/reviews/[A-Za-z0-9._-]+\.json", value) is None:
        raise ContractError("Self-exclusion is only for one review JSON under .claude/runtime/reviews/")
    path = _path(repo, value)
    if path.is_symlink():
        raise ContractError("A review record cannot be a symlink")
    if path.exists():
        validate_review(load_json(path.read_text(encoding="utf-8")))
    return value


def snapshot(
    repo: Path, *, base: str, selection: Sequence[str], record_path: Optional[str] = None,
) -> Json:
    """Bind literal selected files/directories, including index, dirty/new and deletion states."""
    repo = _root(repo)
    base, head = resolve_commit(repo, base), resolve_commit(repo, "HEAD")
    selection = sorted({relative_path(p, allow_root=True) for p in selection})
    if not selection:
        raise ContractError("Explicit nonempty input selection is required")
    record_path = _record_path(repo, record_path)
    excluded = {AUDIT_RECORD, record_path}
    tables: dict[str, dict[str, tuple[str, str]]] = {"base": {}, "head": {}, "index": {}}
    for label, revision in (("base", base), ("head", head)):
        for row in _git(repo, "ls-tree", "-r", "-z", revision).split(b"\0"):
            if row:
                meta, name = row.split(b"\t", 1)
                mode, _, oid = meta.decode().split()
                path = os.fsdecode(name)
                if _selected(path, selection) and path not in excluded:
                    tables[label][path] = (mode, oid)
    for row in _git(repo, "ls-files", "--stage", "-z").split(b"\0"):
        if row:
            meta, name = row.split(b"\t", 1)
            mode, oid, stage = meta.decode().split()
            path = os.fsdecode(name)
            if _selected(path, selection) and path not in excluded:
                if stage != "0":
                    raise ContractError(f"Unresolved index conflict: {path}")
                tables["index"][path] = (mode, oid)
    names = set().union(*(table.keys() for table in tables.values()))

    def walk(path: Path) -> None:
        relative = path.relative_to(repo).as_posix()
        if relative in excluded:
            return
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            names.add(relative)
        elif path.is_dir():
            if path.resolve() != path or not path.resolve().is_relative_to(repo):
                raise ContractError(f"Selected directory is a junction/alias: {relative}")
            for child in sorted(path.iterdir()):
                if child.name.casefold() != ".git":
                    walk(child)

    for item in selection:
        walk(repo if item == "." else _path(repo, item))
        if not any(_selected(path, [item]) for path in names):
            raise ContractError(f"Selected input has no tracked or working content: {item}")
    cache: dict[str, str] = {}

    def git_state(entry: Optional[tuple[str, str]]) -> Json:
        if entry is None:
            return _absent()
        mode, oid = entry
        if mode not in ("100644", "100755", "120000"):
            raise ContractError("Selected submodules/special Git entries require a separate explicit review")
        if oid not in cache:
            cache[oid] = hashlib.sha256(_git(repo, "cat-file", "blob", oid)).hexdigest()
        return {"kind": "symlink" if mode == "120000" else "file", "mode": mode, "sha256": cache[oid]}

    entries = []
    for name in sorted(names):
        relative_path(name)
        path = _path(repo, name)
        states = {label: git_state(table.get(name)) for label, table in tables.items()}
        if path.is_symlink():
            working = {"kind": "symlink", "mode": "120000", "sha256": hashlib.sha256(os.fsencode(os.readlink(path))).hexdigest()}
        elif not path.exists():
            working = _absent()
        elif path.is_file():
            mode = "100755" if path.stat().st_mode & stat.S_IXUSR else "100644"
            if os.name == "nt":
                mode = next((states[k]["mode"] for k in ("index", "head", "base") if states[k]["kind"] == "file"), "100644")
            working = {"kind": "file", "mode": mode, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        else:
            raise ContractError(f"Unsupported selected file type: {name}")
        entries.append({"path": name, **states, "worktree": working})
    result = {
        "base": base, "head": head, "selection": selection,
        "record_path": record_path, "entries": entries,
    }
    result["result_digest"] = _snapshot_digest(result)
    validate_shape(result, "snapshot")
    return result


def bind_work(
    repo: Path, *, work_map: Optional[str], package_id: str, leaf_ids: Sequence[str],
    acceptance_paths: Sequence[Union[str, Json]],
) -> Json:
    """Bind chosen authority bytes or explicit unique start/end-line excerpts."""
    repo = Path(repo).resolve()
    refs = deepcopy(list(acceptance_paths))
    if not refs:
        raise ContractError("Explicit acceptance source selection is required")
    for ref in refs:
        validate_shape(ref, "acceptanceRef")
    required_declaration = ".claude/profile-requirements.json"
    if (repo / required_declaration).exists() or (repo / required_declaration).is_symlink():
        if required_declaration not in refs:
            refs.append(required_declaration)
    map_digest = None
    if work_map is not None:
        work_map = relative_path(work_map)
        data = _path(repo, work_map, regular=True).read_bytes()
        mapping = load_json(data.decode("utf-8-sig"))
        if type(mapping.get("schema_version")) is not int or mapping["schema_version"] != 1 or mapping.get("workflow") not in ("lintel", "spec-kit"):
            raise ContractError("Unsupported selected work-map identity")
        if mapping.get("status") not in ("APPROVED", "COMPLETE"):
            raise ContractError("Selected work map is not approved")
        map_digest = hashlib.sha256(data).hexdigest()
        explicit = {ref if isinstance(ref, str) else ref["path"] for ref in refs}
        for role in ("spec", "plan", "tasks", "prompt"):
            path = relative_path(mapping.get(role))
            if path not in explicit:
                refs.append(path)
                explicit.add(path)
        if mapping.get("constitution") and mapping["constitution"] not in explicit:
            refs.append(relative_path(mapping["constitution"]))
    refs = sorted(refs, key=canonical_json)
    manifest = []
    for ref in refs:
        name = relative_path(ref if isinstance(ref, str) else ref["path"])
        if name == AUDIT_RECORD or name.startswith(".claude/runtime/reviews/"):
            raise ContractError("Review storage is not an acceptance source")
        data = _path(repo, name, regular=True).read_bytes()
        start, end = (None, None) if isinstance(ref, str) else (ref["start"], ref["end"])
        if start is not None:
            lines = data.decode("utf-8").splitlines(keepends=True)
            starts = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == start]
            ends = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == end]
            if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
                raise ContractError(f"Acceptance excerpt boundaries missing, repeated or reversed: {name}")
            data = "".join(lines[starts[0]:ends[0]]).encode("utf-8")
        manifest.append({"path": name, "start": start, "end": end, "sha256": hashlib.sha256(data).hexdigest()})
    result = {
        "work_map": work_map, "map_digest": map_digest, "package_id": package_id,
        "leaf_ids": list(leaf_ids), "acceptance_paths": refs,
        "acceptance_manifest": manifest, "acceptance_digest": content_digest(manifest),
    }
    validate_shape(result, "work")
    return result


def validate_context(context: Json) -> None:
    validate_shape(context, "context")
    snap, work = context["snapshot"], context["work"]
    if snap["result_digest"] != _snapshot_digest(snap):
        raise ContractError("Snapshot digest does not bind its manifest")
    if work["acceptance_digest"] != content_digest(work["acceptance_manifest"]):
        raise ContractError("Acceptance digest does not bind its manifest")
    if (work["work_map"] is None) != (work["map_digest"] is None):
        raise ContractError("Work-map identity is unbound")
    if work["package_id"] != work["package_id"].strip() or any(leaf != leaf.strip() for leaf in work["leaf_ids"]):
        raise ContractError("Package/leaf identities must not have surrounding whitespace")
    paths = [entry["path"] for entry in snap["entries"]]
    if paths != sorted(set(paths)):
        raise ContractError("Snapshot paths must be unique and sorted")
    for path in paths:
        relative_path(path)
        if not _selected(path, snap["selection"]) or path in (snap["record_path"], AUDIT_RECORD):
            raise ContractError("Snapshot contains unselected or self-excluded content")
    for entry in snap["entries"]:
        for key in ("base", "head", "index", "worktree"):
            state = entry[key]
            absent = state["kind"] == "absent"
            if absent != (state["sha256"] is None) or absent != (state["mode"] == "000000"):
                raise ContractError(f"Inconsistent absent-file state: {entry['path']}")
            if state["kind"] == "symlink" and state["mode"] != "120000":
                raise ContractError(f"Inconsistent symlink state: {entry['path']}")
            if state["kind"] == "file" and state["mode"] not in ("100644", "100755"):
                raise ContractError(f"Inconsistent regular-file state: {entry['path']}")


def validate_review(record: Mapping[str, Any]) -> Json:
    """Pure shape and internal-binding validation; a valid record is not clearance."""
    if not isinstance(record, Mapping):
        raise ContractError("A review must be an object")
    result = deepcopy(dict(record))
    validate_shape(result, "review")
    validate_context(result["context"])
    try:
        timestamp = datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError("Review timestamp must be ISO-8601") from error
    if timestamp.tzinfo is None:
        raise ContractError("Review timestamp must include its timezone")
    controls = evaluate_controls(result["controls"], required_policy=result["context"]["required_policy"])["controls"]
    ids = {control["id"] for control in controls}
    if set(result["coverage"]) != set(result["context"]["work"]["leaf_ids"]):
        raise ContractError("Review coverage must name every selected leaf, and no other leaves")
    if any(not set(references) <= ids for references in result["coverage"].values()):
        raise ContractError("Leaf coverage references a missing control")
    for leaf, references in result["coverage"].items():
        if not set(result["context"]["required_controls"]) <= set(references):
            raise ContractError(f"Leaf {leaf} is missing required control coverage")
    if set(result["context"]["required_controls"]) - ids:
        raise ContractError("A required control is missing")
    for control in controls:
        if control["id"] in result["context"]["required_controls"] and control["requirement"] != "mandatory":
            raise ContractError("A required control cannot be downgraded to advisory")
    expected_paths = {path for control in controls for path in control["evidence"]}
    paths = [item["path"] for item in result["evidence"]]
    if len(paths) != len(set(paths)) or set(paths) != expected_paths:
        raise ContractError("Evidence manifest must bind exactly the controls' evidence links")
    for path in paths:
        relative_path(path)
        if path in (result["context"]["snapshot"]["record_path"], AUDIT_RECORD):
            raise ContractError("A decision cannot be its own supporting evidence")
    return result


def select_latest(
    records: Sequence[Mapping[str, Any]], *, skill: str, work_map: Optional[str], package_id: str,
) -> Optional[Json]:
    """Select by append order and scope BEFORE status, age, attempt or digest checks."""
    latest = None
    for record in records:
        if record.get("skill", record.get("kind")) != skill:
            continue
        context = record.get("context")
        work = context.get("work") if isinstance(context, dict) else None
        if isinstance(work, dict) and "work_map" in work and "package_id" in work:
            try:
                scope_map = relative_path(work["work_map"]) if work["work_map"] is not None else None
                validate_shape(work["package_id"], "text")
                scope_package = work["package_id"].strip()
            except ContractError:
                pass  # Invalid scope is unbound, not a reason to resurrect an older PASS.
            else:
                if (scope_map, scope_package) != (work_map, package_id):
                    continue
        latest = dict(record)
    return latest


def evidence_manifest(repo: Path, controls: Sequence[Mapping[str, Any]]) -> list[Json]:
    repo = Path(repo).resolve()
    names = sorted({path for control in controls for path in control["evidence"]})
    return [
        {"path": name, "sha256": hashlib.sha256(_path(repo, name, regular=True).read_bytes()).hexdigest()}
        for name in names
    ]


def verify_context(repo: Path, context: Json) -> None:
    validate_context(context)
    work, snap = context["work"], context["snapshot"]
    current_work = bind_work(
        repo, work_map=work["work_map"], package_id=work["package_id"],
        leaf_ids=work["leaf_ids"], acceptance_paths=work["acceptance_paths"],
    )
    if current_work != work:
        raise ContractError("Selected work/acceptance sources changed")
    current = snapshot(repo, base=snap["base"], selection=snap["selection"], record_path=snap["record_path"])
    if current["result_digest"] != snap["result_digest"]:
        raise ContractError("Selected base/head/index/working content changed")
    declaration = Path(repo) / ".claude" / "profile-requirements.json"
    if declaration.exists() or declaration.is_symlink():
        required = load_json(_path(Path(repo).resolve(), ".claude/profile-requirements.json", regular=True).read_text(encoding="utf-8"))
        name = required.get("required_pack")
        if type(required.get("schema_version")) is not int or required["schema_version"] != 1 or not isinstance(name, str) or not name.strip():
            raise ContractError("PROFILE_REQUIRED: invalid required-policy declaration")
        if not context["required_policy"]["required"] or not context["profile"] or context["profile"]["name"] != name:
            raise ContractError("PROFILE_REQUIRED: required profile is missing from the verified context")
    if context["required_policy"]["required"] and context["profile"] is None:
        raise ContractError("PROFILE_REQUIRED: required profile reference is missing")


def verify_review(
    repo: Path, record: Mapping[str, Any], *, expected: Json, corroboration: Optional[Json] = None,
) -> Json:
    """Check content and policy plus caller-supplied host/human provenance, not authentication."""
    independence: Json = {"declared": False, "corroborated": False, "provenance": "declared"}
    result: Json = {"ok": False, "status": "unverified", "problems": [], "independence": independence}
    try:
        review = validate_review(record)
        validate_context(expected)
        if review["context"] != expected:
            raise ContractError("Review context differs from the selected work/attempt/profile/control contract")
        verify_context(repo, expected)
        controls = evaluate_controls(review["controls"], required_policy=expected["required_policy"])
        result["controls"] = controls
        result["problems"].extend(controls["blockers"])
        result["status"] = review["status"]
        if review["status"] != "pass":
            result["problems"].append(f"Latest review decision is {review['status']}: {review['reason']}")
        if expected["work"]["work_map"] is None:
            result["problems"].append("Unmapped inspection is not release clearance; mapped implementation authority is required")
        if evidence_manifest(repo, review["controls"]) != sorted(review["evidence"], key=lambda v: v["path"]):
            result["problems"].append("Control evidence files changed")
        by_id = {control["id"]: control for control in controls["controls"]}
        for leaf, ids in review["coverage"].items():
            if not any(
                by_id[id_]["requirement"] == "mandatory"
                and by_id[id_]["applicability"] == "applicable"
                and by_id[id_]["effective_status"] == "pass" for id_ in ids
            ):
                result["problems"].append(f"Leaf {leaf} has no verified mandatory acceptance")
        if expected["purpose"] == "implementation" and not any(
            entry["base"] != entry["worktree"] for entry in expected["snapshot"]["entries"]
        ):
            result["problems"].append("Implementation review has no changed selected result")
        builder, reviewer = expected["builder"], review["reviewer"]
        distinct = builder["id"] != reviewer["id"] and builder["context"] != reviewer["context"]
        independence["declared"] = distinct
        if corroboration is not None:
            validate_shape(corroboration, "corroboration")
            if (
                corroboration["record_digest"] != content_digest(review)
                or corroboration["attempt_id"] != expected["attempt_id"]
                or corroboration["builder"] != builder or corroboration["reviewer"] != reviewer
            ):
                raise ContractError("Corroboration does not bind this decision/attempt/actors")
            independence.update({
                "corroborated": distinct,
                "provenance": "host_observed" if corroboration["kind"] == "host" else "human_attested",
                "source": corroboration["source"], "reference": corroboration["reference"],
            })
        if expected["independence_required"] and not independence["corroborated"]:
            result["problems"].append("Independent review is only declared, absent, or the same actor/context")
        result["ok"] = not result["problems"]
        if not result["ok"] and result["status"] == "pass":
            result["status"] = "unverified"
    except (ContractError, OSError, UnicodeError) as error:
        result["status"] = "error"
        result["problems"].append(str(error))
    return result


def verify_qa(repo: Path, qa: Json, *, expected: Json) -> Json:
    """Read-only QA must cover nonzero tests and the same immutable context."""
    validate_shape(qa, "qa")
    verify_context(repo, expected)
    if qa["context_digest"] != content_digest(expected):
        raise ContractError("QA belongs to a different content/acceptance/attempt/profile context")
    tests = [c for c in qa["controls"] if c["kind"] == "tests" and c["requirement"] == "mandatory" and c["applicability"] == "applicable"]
    if not tests:
        raise ContractError("QA has no required executed test scope")
    result = evaluate_controls(qa["controls"], required_policy=expected["required_policy"])
    if evidence_manifest(repo, qa["controls"]) != sorted(qa["evidence"], key=lambda v: v["path"]):
        raise ContractError("QA evidence files changed")
    return result
