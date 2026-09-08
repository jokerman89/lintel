#!/usr/bin/env python3
# component: swarm-contract
# implements: ADR-0026
# intent: .claude/plans/swarming-work/spec.md
# constraints: read-only; standard library only; artifact content is data, never executable
# last_intent_review: 2026-09-08
"""Parse and validate Lintel swarm topology, scope, and close evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterable, Mapping, Optional, Sequence, Tuple, Union


SCHEMA_PATH = Path(__file__).with_name("swarm-schema.json")
EVIDENCE_START = "<!-- lintel-swarm-evidence:v1"
EVIDENCE_END = "-->"
EVIDENCE_VERSION = 1
WORK_MAP_VERSION = 1
WORK_MAP_MODES = {"lintel", "spec-kit"}
WORK_MAP_STATUSES = {"DRAFT", "APPROVED", "COMPLETE"}
ISOLATION_BACKENDS = {"git-worktree", "isolated-patch", "host-scoped-write"}
EXPECTED_SCOPE_RULES = {
    "worker": "write_scope+own_report",
    "reviewer": "own_review",
    "reducers": "coordinator-only",
}
UNIVERSAL_COORDINATOR_PATHS = (".git", ".claude/runtime", ".claude/plans/todo.md")
IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,63}$")
INITIATIVE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


class DuplicateKeyError(ValueError):
    """Raised when JSON tries to hide one value behind a duplicate key."""


class SwarmContractError(ValueError):
    """Raised by the strict loader with all validation diagnostics attached."""

    def __init__(self, diagnostics: Sequence["Diagnostic"]):
        self.diagnostics = list(diagnostics)
        super().__init__("; ".join(item.message for item in diagnostics))


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "path": self.path,
            "message": self.message,
        }


@dataclass
class ValidationResult:
    contract: Optional[dict[str, Any]] = None
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(item.severity == "error" for item in self.diagnostics)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "diagnostics": [item.as_dict() for item in self.diagnostics],
        }


def _reject_duplicate_keys(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"Non-finite JSON number is not allowed: {value}")


def _read_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8-sig"),
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_constant,
    )


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def _path_parts(value: str) -> tuple[str, ...]:
    return tuple(PurePosixPath(value).parts)


def _path_identity(root: Path, value: str) -> Optional[Tuple[str, ...]]:
    """Return the platform-normalized, symlink-resolved identity inside root."""
    try:
        candidate = root.joinpath(*_path_parts(value)).resolve(strict=False)
    except (OSError, RuntimeError, TypeError, ValueError):
        return None
    if not _inside(root, candidate):
        return None
    relative = candidate.relative_to(root)
    return tuple(os.path.normcase(part) for part in relative.parts)


def _paths_overlap(root: Path, left: str, right: str) -> bool:
    left_parts = _path_identity(root, left)
    right_parts = _path_identity(root, right)
    if left_parts is None or right_parts is None:
        return False
    shorter = min(len(left_parts), len(right_parts))
    return left_parts[:shorter] == right_parts[:shorter]


def _path_owned(root: Path, path: str, scope: str) -> bool:
    path_parts = _path_identity(root, path)
    scope_parts = _path_identity(root, scope)
    if path_parts is None or scope_parts is None:
        return False
    return len(path_parts) >= len(scope_parts) and path_parts[: len(scope_parts)] == scope_parts


def _safe_repo_path(
    root: Path,
    value: Any,
    field_path: str,
    diagnostics: list[Diagnostic],
    *,
    must_be_file: bool = False,
) -> Optional[str]:
    if type(value) is not str or not value:
        diagnostics.append(Diagnostic("error", "path.type", field_path, "Expected a nonempty repository-relative POSIX path"))
        return None
    if (
        value != value.strip()
        or value.startswith("/")
        or value.endswith("/")
        or "\\" in value
        or ":" in value
        or "//" in value
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        diagnostics.append(Diagnostic("error", "path.unsafe", field_path, f"Unsafe repository path: {value!r}"))
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or not pure.parts or any(part in ("", ".", "..") for part in pure.parts):
        diagnostics.append(Diagnostic("error", "path.unsafe", field_path, f"Unsafe repository path: {value!r}"))
        return None
    candidate = root.joinpath(*pure.parts).resolve(strict=False)
    if not _inside(root, candidate):
        diagnostics.append(Diagnostic("error", "path.escape", field_path, f"Path resolves outside the repository: {value}"))
        return None
    if must_be_file and not candidate.is_file():
        diagnostics.append(Diagnostic("error", "path.missing", field_path, f"Required file is missing: {value}"))
        return None
    return value


def _validate_branch(value: Any, diagnostics: list[Diagnostic]) -> None:
    invalid = (
        type(value) is not str
        or not value
        or len(value) > 255
        or value != value.strip()
        or value.startswith(("-", "/"))
        or value.endswith(("/", ".", ".lock"))
        or value == "@"
        or "//" in value
        or ".." in value
        or "@{" in value
        or any(character.isspace() or character in "\\~^:?*[" or ord(character) < 32 or ord(character) == 127 for character in value)
        or any(component.startswith(".") or component.endswith(".lock") for component in value.split("/"))
    )
    if invalid:
        diagnostics.append(Diagnostic("error", "branch.invalid", "integration_branch", "integration_branch is not a safe Git ref name"))


def _schema_definition(diagnostics: list[Diagnostic]) -> Optional[dict[str, Any]]:
    try:
        data = _read_json(SCHEMA_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        diagnostics.append(Diagnostic("error", "schema.unavailable", "schema", f"Cannot load swarm schema: {error}"))
        return None
    if not isinstance(data, dict):
        diagnostics.append(Diagnostic("error", "schema.invalid", "schema", "Swarm schema root must be an object"))
        return None
    return data


def _load_coordination_file(root: Path, relative_path: str, diagnostics: list[Diagnostic]) -> Optional[dict[str, Any]]:
    safe = _safe_repo_path(root, relative_path, "coordination", diagnostics, must_be_file=True)
    if safe is None:
        return None
    try:
        data = _read_json(root.joinpath(*_path_parts(safe)))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        diagnostics.append(Diagnostic("error", "coordination.json", "coordination", f"Cannot parse coordination JSON: {error}"))
        return None
    if not isinstance(data, dict):
        diagnostics.append(Diagnostic("error", "coordination.type", "coordination", "Coordination root must be an object"))
        return None
    return data


def _load_work_map(root: Path, relative_path: str, diagnostics: list[Diagnostic]) -> Tuple[Optional[dict[str, Any]], Optional[str]]:
    safe = _safe_repo_path(root, relative_path, "work_map", diagnostics, must_be_file=True)
    if safe is None:
        return None, None
    try:
        data = _read_json(root.joinpath(*_path_parts(safe)))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        diagnostics.append(Diagnostic("error", "work_map.json", "work_map", f"Cannot parse work map JSON: {error}"))
        return None, safe
    if not isinstance(data, dict):
        diagnostics.append(Diagnostic("error", "work_map.type", "work_map", "Work map root must be an object"))
        return None, safe
    if type(data.get("schema_version")) is not int or data.get("schema_version") != WORK_MAP_VERSION:
        diagnostics.append(Diagnostic("error", "work_map.version", "work_map.schema_version", "Swarming requires work-map schema_version 1"))
    if data.get("workflow") not in WORK_MAP_MODES:
        diagnostics.append(Diagnostic("error", "work_map.workflow", "work_map.workflow", "workflow must be lintel or spec-kit"))
    if data.get("status") not in WORK_MAP_STATUSES:
        diagnostics.append(Diagnostic("error", "work_map.status", "work_map.status", "status must be DRAFT, APPROVED or COMPLETE"))
    return data, safe


def _validate_root_shape(data: dict[str, Any], schema: dict[str, Any], diagnostics: list[Diagnostic]) -> None:
    required = set(schema.get("required", ()))
    allowed = set(schema.get("properties", {}))
    for field_name in sorted(required - set(data)):
        diagnostics.append(Diagnostic("error", "root.required", field_name, f"Missing required field: {field_name}"))
    for field_name in sorted(set(data) - allowed):
        diagnostics.append(Diagnostic("error", "root.unknown", field_name, f"Unknown root field: {field_name}"))
    version = data.get("schema_version")
    version_schema = schema.get("properties", {}).get("schema_version", {})
    if (
        type(version) is not int
        or version < version_schema.get("minimum", 1)
        or version > version_schema.get("maximum", 1)
    ):
        diagnostics.append(Diagnostic("error", "root.version", "schema_version", "Unsupported swarm schema_version"))
    initiative = data.get("initiative")
    if type(initiative) is not str or not INITIATIVE.fullmatch(initiative):
        diagnostics.append(Diagnostic("error", "root.initiative", "initiative", "initiative must be a lowercase kebab-case identifier"))
    _validate_branch(data.get("integration_branch"), diagnostics)
    maximum = data.get("max_parallel")
    if type(maximum) is not int or not 1 <= maximum <= 64:
        diagnostics.append(Diagnostic("error", "root.max_parallel", "max_parallel", "max_parallel must be an integer from 1 through 64"))
    if data.get("scope_rules") != EXPECTED_SCOPE_RULES:
        diagnostics.append(Diagnostic("error", "root.scope_rules", "scope_rules", "scope_rules must preserve worker, reviewer, and coordinator ownership"))


def _validate_lanes(
    root: Path,
    data: dict[str, Any],
    schema: dict[str, Any],
    diagnostics: list[Diagnostic],
) -> list[dict[str, Any]]:
    lanes = data.get("lanes")
    if not isinstance(lanes, list) or not lanes:
        diagnostics.append(Diagnostic("error", "lanes.type", "lanes", "lanes must be a nonempty array"))
        return []
    lane_schema = schema.get("$defs", {}).get("lane", {})
    required = set(lane_schema.get("required", ()))
    allowed = set(lane_schema.get("properties", {}))
    valid_lanes: list[dict[str, Any]] = []
    seen_task_ids: set[str] = set()
    seen_artifacts: dict[Tuple[str, ...], str] = {}
    for index, lane in enumerate(lanes):
        prefix = f"lanes[{index}]"
        if not isinstance(lane, dict):
            diagnostics.append(Diagnostic("error", "lane.type", prefix, "Lane must be an object"))
            continue
        valid_lanes.append(lane)
        for field_name in sorted(required - set(lane)):
            diagnostics.append(Diagnostic("error", "lane.required", f"{prefix}.{field_name}", f"Missing required lane field: {field_name}"))
        for field_name in sorted(set(lane) - allowed):
            diagnostics.append(Diagnostic("error", "lane.unknown", f"{prefix}.{field_name}", f"Unknown lane field: {field_name}"))
        task_id = lane.get("task_id")
        if type(task_id) is not str or not IDENTIFIER.fullmatch(task_id):
            diagnostics.append(Diagnostic("error", "lane.task_id", f"{prefix}.task_id", "task_id must be a stable identifier"))
        elif task_id in seen_task_ids:
            diagnostics.append(Diagnostic("error", "lane.duplicate", f"{prefix}.task_id", f"Duplicate task/lane id: {task_id}"))
        else:
            seen_task_ids.add(task_id)
        wave = lane.get("wave")
        if type(wave) is not int or wave < 1:
            diagnostics.append(Diagnostic("error", "lane.wave", f"{prefix}.wave", "wave must be a positive integer"))
        role = lane.get("role")
        if type(role) is not str or not role.strip() or len(role) > 128 or any(ord(char) < 32 or ord(char) == 127 for char in role):
            diagnostics.append(Diagnostic("error", "lane.role", f"{prefix}.role", "role must be a nonempty printable string"))
        isolation = lane.get("isolation")
        if isolation is not None and isolation not in ISOLATION_BACKENDS:
            diagnostics.append(Diagnostic("error", "lane.isolation", f"{prefix}.isolation", "Unknown isolation backend"))
        scope = lane.get("write_scope")
        if not isinstance(scope, list) or not scope:
            diagnostics.append(Diagnostic("error", "lane.write_scope", f"{prefix}.write_scope", "write_scope must be a nonempty array"))
        else:
            seen_scope: set[Tuple[str, ...]] = set()
            for scope_index, raw_path in enumerate(scope):
                path = _safe_repo_path(root, raw_path, f"{prefix}.write_scope[{scope_index}]", diagnostics)
                identity = _path_identity(root, path) if path is not None else None
                if identity is not None and identity in seen_scope:
                    diagnostics.append(Diagnostic("error", "lane.scope_duplicate", f"{prefix}.write_scope[{scope_index}]", f"Duplicate scope path: {path}"))
                elif identity is not None:
                    seen_scope.add(identity)
        for artifact in ("brief", "report", "review"):
            path = _safe_repo_path(root, lane.get(artifact), f"{prefix}.{artifact}", diagnostics, must_be_file=artifact == "brief")
            if path is None:
                continue
            identity = _path_identity(root, path)
            if identity is None:
                continue
            prior = seen_artifacts.get(identity)
            if prior is not None:
                diagnostics.append(Diagnostic("error", "lane.artifact_duplicate", f"{prefix}.{artifact}", f"Artifact path is already owned by {prior}: {path}"))
            else:
                seen_artifacts[identity] = f"{task_id}.{artifact}"
    return valid_lanes


def _validate_task_authority(
    root: Path,
    work_map: Optional[Mapping[str, Any]],
    lanes: Sequence[Mapping[str, Any]],
    diagnostics: list[Diagnostic],
) -> list[str]:
    if work_map is None:
        return []
    tasks = _safe_repo_path(root, work_map.get("tasks"), "work_map.tasks", diagnostics, must_be_file=True)
    if tasks is None:
        return []
    try:
        content = root.joinpath(*_path_parts(tasks)).read_text(encoding="utf-8-sig")
    except OSError as error:
        diagnostics.append(Diagnostic("error", "tasks.read", "work_map.tasks", f"Cannot read mapped tasks: {error}"))
        return []
    found: list[str] = []
    for lane in lanes:
        task_id = lane.get("task_id")
        if type(task_id) is not str or not IDENTIFIER.fullmatch(task_id):
            continue
        escaped = re.escape(task_id)
        patterns = (
            re.compile(rf"^#{{2,6}}\s+{escaped}(?=\s|[-—–:]|$)", re.MULTILINE),
            re.compile(rf"^\s*-\s+\[[ xX]\]\s+{escaped}(?=\s|[-—–:]|$)", re.MULTILINE),
        )
        count = sum(len(pattern.findall(content)) for pattern in patterns)
        if count == 0:
            diagnostics.append(Diagnostic("error", "tasks.missing", "work_map.tasks", f"Lane task_id is absent from mapped tasks: {task_id}"))
        elif count > 1:
            diagnostics.append(Diagnostic("error", "tasks.duplicate", "work_map.tasks", f"Lane task_id is defined more than once in mapped tasks: {task_id}"))
        else:
            found.append(task_id)
    return found


def _validate_topology(
    root: Path,
    data: Mapping[str, Any],
    lanes: Sequence[Mapping[str, Any]],
    protected_paths: Sequence[str],
    diagnostics: list[Diagnostic],
) -> None:
    by_wave: dict[int, list[Mapping[str, Any]]] = {}
    for lane in lanes:
        wave = lane.get("wave")
        if type(wave) is int and wave >= 1:
            by_wave.setdefault(wave, []).append(lane)
        scope = lane.get("write_scope")
        if not isinstance(scope, list):
            continue
        for raw_scope in scope:
            if not isinstance(raw_scope, str):
                continue
            for protected in protected_paths:
                if _paths_overlap(root, raw_scope, protected):
                    diagnostics.append(Diagnostic("error", "scope.protected", f"lanes.{lane.get('task_id')}.write_scope", f"Worker scope overlaps coordinator/reviewer-owned path {protected}: {raw_scope}"))
    for wave, wave_lanes in sorted(by_wave.items()):
        for left_index, left in enumerate(wave_lanes):
            left_scope = left.get("write_scope") if isinstance(left.get("write_scope"), list) else []
            for right in wave_lanes[left_index + 1 :]:
                right_scope = right.get("write_scope") if isinstance(right.get("write_scope"), list) else []
                for left_path in left_scope:
                    for right_path in right_scope:
                        if isinstance(left_path, str) and isinstance(right_path, str) and _paths_overlap(root, left_path, right_path):
                            diagnostics.append(Diagnostic("error", "wave.scope_overlap", f"lanes.wave[{wave}]", f"Same-wave scopes overlap for {left.get('task_id')} and {right.get('task_id')}: {left_path} <> {right_path}"))
        if len(wave_lanes) > 1:
            if data.get("max_parallel") == 1:
                diagnostics.append(Diagnostic("warning", "wave.sequenced", f"lanes.wave[{wave}]", "Multiple lanes will use the sequenced fallback because max_parallel is 1"))
            else:
                for lane in wave_lanes:
                    if lane.get("isolation") not in ISOLATION_BACKENDS:
                        diagnostics.append(Diagnostic("error", "wave.isolation_missing", f"lanes.{lane.get('task_id')}.isolation", "Every writer in a concurrent wave requires attributable isolation"))


def validate_coordination(
    repo: Union[Path, str],
    coordination_path: str,
    *,
    expected_work_map: Optional[str] = None,
) -> ValidationResult:
    """Validate one committed swarm coordination document without executing content."""
    root = Path(repo).resolve()
    diagnostics: list[Diagnostic] = []
    schema = _schema_definition(diagnostics)
    data = _load_coordination_file(root, coordination_path, diagnostics)
    if schema is None or data is None:
        return ValidationResult(data, diagnostics)
    _validate_root_shape(data, schema, diagnostics)
    work_map_path = _safe_repo_path(root, data.get("work_map"), "work_map", diagnostics, must_be_file=True)
    _safe_repo_path(root, data.get("charter"), "charter", diagnostics, must_be_file=True)
    lanes = _validate_lanes(root, data, schema, diagnostics)
    work_map, loaded_work_map_path = _load_work_map(root, data.get("work_map"), diagnostics) if work_map_path else (None, None)
    if (
        expected_work_map is not None
        and loaded_work_map_path is not None
        and _path_identity(root, loaded_work_map_path) != _path_identity(root, expected_work_map)
    ):
        diagnostics.append(Diagnostic("error", "work_map.mismatch", "work_map", f"Coordination points to {loaded_work_map_path!r}; expected {expected_work_map!r}"))
    if work_map is not None:
        if work_map.get("execution_mode") != "swarm":
            diagnostics.append(Diagnostic("error", "work_map.mode", "work_map.execution_mode", "Referenced work map must explicitly opt in with execution_mode 'swarm'"))
        if (
            type(work_map.get("coordination")) is not str
            or _path_identity(root, work_map["coordination"]) != _path_identity(root, coordination_path)
        ):
            diagnostics.append(Diagnostic("error", "work_map.coordination", "work_map.coordination", "Referenced work map must point back to this coordination document"))
    _validate_task_authority(root, work_map, lanes, diagnostics)
    protected: list[str] = [coordination_path, *UNIVERSAL_COORDINATOR_PATHS]
    for value in (data.get("work_map"), data.get("charter")):
        if isinstance(value, str):
            protected.append(value)
    if work_map is not None:
        for name in ("spec", "plan", "tasks", "prompt", "constitution"):
            if isinstance(work_map.get(name), str):
                protected.append(work_map[name])
    for lane in lanes:
        for name in ("brief", "report", "review"):
            if isinstance(lane.get(name), str):
                protected.append(lane[name])
    _validate_topology(root, data, lanes, protected, diagnostics)
    return ValidationResult(data, diagnostics)


def validate_work_map_swarm_fields(
    repo: Union[Path, str],
    work_map: Mapping[str, Any],
    work_map_path: str,
) -> ValidationResult:
    """Validate the optional schema-v1 swarm extension used by li-work-artifacts."""
    mode = work_map.get("execution_mode")
    coordination = work_map.get("coordination")
    if mode is None and coordination is None:
        return ValidationResult(None, [])
    if mode != "swarm" or type(coordination) is not str:
        return ValidationResult(
            None,
            [Diagnostic("error", "work_map.swarm_fields", "work_map", "execution_mode 'swarm' and coordination must be declared together")],
        )
    return validate_coordination(repo, coordination, expected_work_map=work_map_path)


def load_swarm_contract(repo: Union[Path, str], coordination_path: str) -> dict[str, Any]:
    """Strict shared parser entry point for workflow consumers."""
    result = validate_coordination(repo, coordination_path)
    if not result.ok or result.contract is None:
        raise SwarmContractError(result.diagnostics)
    return result.contract


def lane_by_task(contract: Mapping[str, Any], task_id: str) -> Optional[Mapping[str, Any]]:
    for lane in contract.get("lanes", []):
        if isinstance(lane, Mapping) and lane.get("task_id") == task_id:
            return lane
    return None


def _lane_scope_diagnostics(
    root: Path,
    contract: Mapping[str, Any],
    lane: Mapping[str, Any],
    changed_paths: Sequence[str],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    task_id = str(lane.get("task_id"))
    scopes = [item for item in lane.get("write_scope", []) if isinstance(item, str)]
    own_report = lane.get("report")
    own_review = lane.get("review")
    own_report_identity = _path_identity(root, own_report) if isinstance(own_report, str) else None
    own_review_identity = _path_identity(root, own_review) if isinstance(own_review, str) else None
    all_reviews = {
        _path_identity(root, item["review"])
        for item in contract.get("lanes", [])
        if isinstance(item, Mapping) and isinstance(item.get("review"), str)
    }
    all_briefs = {
        _path_identity(root, item["brief"])
        for item in contract.get("lanes", [])
        if isinstance(item, Mapping) and isinstance(item.get("brief"), str)
    }
    other_reports = {
        _path_identity(root, item["report"])
        for item in contract.get("lanes", [])
        if isinstance(item, Mapping) and item.get("task_id") != task_id and isinstance(item.get("report"), str)
    }
    for index, raw_path in enumerate(changed_paths):
        path = _safe_repo_path(root, raw_path, f"changed_paths[{index}]", diagnostics)
        if path is None:
            continue
        identity = _path_identity(root, path)
        if any(_paths_overlap(root, path, protected) for protected in UNIVERSAL_COORDINATOR_PATHS):
            diagnostics.append(Diagnostic("error", "scope.universal", f"changed_paths[{index}]", f"Lane {task_id} may not change universal coordinator path: {path}"))
        elif identity == own_review_identity or identity in all_reviews or identity in all_briefs or identity in other_reports:
            diagnostics.append(Diagnostic("error", "scope.reserved", f"changed_paths[{index}]", f"Lane {task_id} may not change reserved handoff/review path: {path}"))
        elif identity == own_report_identity:
            continue
        elif not any(_path_owned(root, path, scope) for scope in scopes):
            diagnostics.append(Diagnostic("error", "scope.outside", f"changed_paths[{index}]", f"Path is outside lane {task_id} scope: {path}"))
    return diagnostics


def check_lane_scope(
    repo: Union[Path, str],
    coordination_path: str,
    task_id: str,
    changed_paths: Sequence[str],
) -> ValidationResult:
    result = validate_coordination(repo, coordination_path)
    if not result.ok or result.contract is None:
        return result
    diagnostics = list(result.diagnostics)
    lane = lane_by_task(result.contract, task_id)
    if lane is None:
        diagnostics.append(Diagnostic("error", "scope.unknown_lane", "task_id", f"Unknown lane: {task_id}"))
        return ValidationResult(result.contract, diagnostics)
    if not changed_paths:
        diagnostics.append(Diagnostic("error", "scope.empty", "changed_paths", "At least one attributable changed path is required"))
        return ValidationResult(result.contract, diagnostics)
    root = Path(repo).resolve()
    diagnostics.extend(_lane_scope_diagnostics(root, result.contract, lane, changed_paths))
    return ValidationResult(result.contract, diagnostics)


def _read_evidence(path: Path, kind: str, task_id: str, diagnostics: list[Diagnostic]) -> Optional[dict[str, Any]]:
    if not path.is_file():
        diagnostics.append(Diagnostic("error", "evidence.missing", str(path), f"Missing {kind} evidence for {task_id}"))
        return None
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        diagnostics.append(Diagnostic("error", "evidence.read", str(path), f"Cannot read {kind} evidence: {error}"))
        return None
    starts = text.count(EVIDENCE_START)
    if starts != 1:
        diagnostics.append(Diagnostic("error", "evidence.marker", str(path), f"Expected exactly one {EVIDENCE_START} marker"))
        return None
    start = text.index(EVIDENCE_START) + len(EVIDENCE_START)
    end = text.find(EVIDENCE_END, start)
    if end < 0:
        diagnostics.append(Diagnostic("error", "evidence.marker", str(path), "Evidence marker is not closed"))
        return None
    payload = text[start:end].strip()
    try:
        data = json.loads(payload, object_pairs_hook=_reject_duplicate_keys, parse_constant=_reject_constant)
    except (ValueError, json.JSONDecodeError) as error:
        diagnostics.append(Diagnostic("error", "evidence.json", str(path), f"Invalid evidence JSON: {error}"))
        return None
    if not isinstance(data, dict):
        diagnostics.append(Diagnostic("error", "evidence.type", str(path), "Evidence payload must be an object"))
        return None
    if (
        type(data.get("schema_version")) is not int
        or data.get("schema_version") != EVIDENCE_VERSION
        or data.get("artifact_kind") != f"swarm-{kind}"
        or data.get("task_id") != task_id
    ):
        diagnostics.append(Diagnostic("error", "evidence.identity", str(path), f"Evidence identity does not match {kind} for {task_id}"))
    return data


def _nonempty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(type(item) is str and bool(item.strip()) for item in value)


def _passing_checks(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(
            isinstance(item, dict)
            and type(item.get("name")) is str
            and bool(item["name"].strip())
            and type(item.get("status")) is str
            and item["status"] == "PASS"
            for item in value
        )
    )


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(type(item) is str for item in value)


def _report_evidence_diagnostics(
    root: Path,
    contract: Mapping[str, Any],
    lane: Mapping[str, Any],
    report: Mapping[str, Any],
) -> list[Diagnostic]:
    task_id = str(lane["task_id"])
    diagnostics: list[Diagnostic] = []
    if type(report.get("status")) is not str or report.get("status") != "complete":
        diagnostics.append(Diagnostic("error", "report.incomplete", lane["report"], f"Report for {task_id} is not complete"))
    if type(report.get("worker")) is not str or not report["worker"].strip():
        diagnostics.append(Diagnostic("error", "report.worker", lane["report"], f"Report for {task_id} must name a nonempty worker identity"))
    changed_paths = report.get("changed_paths")
    if not _nonempty_string_list(changed_paths):
        diagnostics.append(Diagnostic("error", "report.changed_paths", lane["report"], f"Report for {task_id} needs a nonempty list of nonempty changed-path strings"))
    if not _passing_checks(report.get("checks")):
        diagnostics.append(Diagnostic("error", "report.checks", lane["report"], f"Report for {task_id} needs one or more check objects with a nonempty name and exact PASS status"))
    if not _string_list(report.get("limitations")):
        diagnostics.append(Diagnostic("error", "report.limitations", lane["report"], f"Report for {task_id} must declare a list of limitation strings"))
    if _nonempty_string_list(changed_paths):
        diagnostics.extend(_lane_scope_diagnostics(root, contract, lane, changed_paths))
        report_identity = _path_identity(root, lane["report"])
        changed_identities = [_path_identity(root, path) for path in changed_paths]
        if report_identity not in changed_identities:
            diagnostics.append(Diagnostic("error", "report.own_report", lane["report"], f"Report for {task_id} must include its own report path in changed_paths"))
        scopes = [scope for scope in lane.get("write_scope", []) if isinstance(scope, str)]
        has_product_change = any(
            identity != report_identity and any(_path_owned(root, path, scope) for scope in scopes)
            for path, identity in zip(changed_paths, changed_identities)
        )
        if not has_product_change:
            diagnostics.append(Diagnostic("error", "report.product_change", lane["report"], f"Report for {task_id} must include a changed path in declared write_scope in addition to its own report"))
    return diagnostics


def lane_states(repo: Union[Path, str], contract: Mapping[str, Any]) -> Tuple[list[dict[str, Any]], list[Diagnostic]]:
    root = Path(repo).resolve()
    diagnostics: list[Diagnostic] = []
    states: list[dict[str, Any]] = []
    for lane in contract.get("lanes", []):
        if not isinstance(lane, Mapping) or not isinstance(lane.get("task_id"), str):
            continue
        task_id = lane["task_id"]
        report_path = root.joinpath(*_path_parts(lane["report"]))
        review_path = root.joinpath(*_path_parts(lane["review"]))
        report: Optional[dict[str, Any]] = None
        review: Optional[dict[str, Any]] = None
        report_diagnostics: list[Diagnostic] = []
        review_diagnostics: list[Diagnostic] = []
        if report_path.is_file():
            report = _read_evidence(report_path, "report", task_id, report_diagnostics)
        if review_path.is_file():
            review = _read_evidence(review_path, "review", task_id, review_diagnostics)
        if report is not None:
            if report.get("initiative") != contract.get("initiative"):
                report_diagnostics.append(Diagnostic("error", "evidence.initiative", lane["report"], f"Evidence initiative does not match coordination for {task_id}"))
            report_diagnostics.extend(_report_evidence_diagnostics(root, contract, lane, report))
        if review is not None and review.get("initiative") != contract.get("initiative"):
            review_diagnostics.append(Diagnostic("error", "evidence.initiative", lane["review"], f"Evidence initiative does not match coordination for {task_id}"))
        local = report_diagnostics + review_diagnostics
        state = "not_started"
        if report_path.is_file() and (report is None or report_diagnostics):
            state = "invalid_report"
        elif report is not None and not review_path.is_file():
            state = "awaiting_review"
        elif review_path.is_file() and review is None:
            state = "blocked"
        elif review is not None and report is None:
            state = "blocked"
            local.append(Diagnostic("error", "review.orphan", lane["review"], f"Review evidence exists before report evidence for {task_id}"))
        elif review is not None and (review.get("status") != "complete" or review.get("verdict") != "PASS"):
            state = "rework_required"
        elif report is not None and review is not None:
            stages = review.get("stages")
            if not isinstance(stages, dict) or stages.get("spec") != "PASS" or stages.get("quality") != "PASS":
                state = "rework_required"
            elif not _passing_checks(review.get("checks")):
                state = "blocked"
                local.append(Diagnostic("error", "review.checks", lane["review"], f"Review for {task_id} needs one or more check objects with a nonempty name and exact PASS status"))
            elif not _string_list(review.get("limitations")):
                state = "blocked"
                local.append(Diagnostic("error", "review.limitations", lane["review"], f"Review for {task_id} must declare a list of limitation strings"))
            elif (
                type(review.get("reviewer")) is not str
                or not review["reviewer"].strip()
                or report["worker"].strip().casefold() == review["reviewer"].strip().casefold()
            ):
                state = "blocked"
                local.append(Diagnostic("error", "review.independence", lane["review"], f"Review evidence for {task_id} must name a distinct reviewer"))
            else:
                state = "blocked" if any(item.severity == "error" for item in local) else "complete"
        if state != "invalid_report" and any(item.severity == "error" for item in local):
            state = "blocked"
        diagnostics.extend(local)
        states.append({"task_id": task_id, "wave": lane.get("wave"), "state": state})
    return states, diagnostics


def _contract_work_map_status(
    root: Path,
    contract: Mapping[str, Any],
    diagnostics: list[Diagnostic],
) -> Optional[str]:
    path = _safe_repo_path(root, contract.get("work_map"), "work_map", diagnostics, must_be_file=True)
    if path is None:
        return None
    try:
        work_map = _read_json(root.joinpath(*_path_parts(path)))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        diagnostics.append(Diagnostic("error", "work_map.json", "work_map", f"Cannot parse work map JSON: {error}"))
        return None
    if not isinstance(work_map, dict) or work_map.get("status") not in WORK_MAP_STATUSES:
        diagnostics.append(Diagnostic("error", "work_map.status", "work_map.status", "status must be DRAFT, APPROVED or COMPLETE"))
        return None
    return work_map["status"]


def ready_frontier(repo: Union[Path, str], coordination_path: str) -> Tuple[ValidationResult, dict[str, Any]]:
    result = validate_coordination(repo, coordination_path)
    if not result.ok or result.contract is None:
        return result, {"wave": None, "ready_task_ids": [], "dispatch_task_ids": [], "states": []}
    states, evidence_diagnostics = lane_states(repo, result.contract)
    diagnostics = list(result.diagnostics) + evidence_diagnostics
    work_map_status = _contract_work_map_status(Path(repo).resolve(), result.contract, diagnostics)
    if work_map_status != "APPROVED":
        if work_map_status is not None:
            diagnostics.append(Diagnostic("error", "wave.work_map_status", "work_map.status", f"Dispatch requires work-map status APPROVED; found {work_map_status}"))
        return ValidationResult(result.contract, diagnostics), {
            "work_map_status": work_map_status,
            "wave": None,
            "ready_task_ids": [],
            "dispatch_task_ids": [],
            "states": states,
        }
    incomplete = [state for state in states if state["state"] != "complete"]
    if not incomplete:
        return ValidationResult(result.contract, diagnostics), {"work_map_status": work_map_status, "wave": None, "ready_task_ids": [], "dispatch_task_ids": [], "states": states}
    wave = min(state["wave"] for state in incomplete)
    frontier = [state["task_id"] for state in incomplete if state["wave"] == wave and state["state"] in ("not_started", "rework_required")]
    capacity = result.contract.get("max_parallel", 1)
    return ValidationResult(result.contract, diagnostics), {
        "work_map_status": work_map_status,
        "wave": wave,
        "ready_task_ids": frontier,
        "dispatch_task_ids": frontier[:capacity],
        "states": states,
    }


def verify_close(repo: Union[Path, str], coordination_path: str) -> Tuple[ValidationResult, list[dict[str, Any]]]:
    result = validate_coordination(repo, coordination_path)
    if not result.ok or result.contract is None:
        return result, []
    states, evidence_diagnostics = lane_states(repo, result.contract)
    diagnostics = list(result.diagnostics) + evidence_diagnostics
    for state in states:
        if state["state"] != "complete":
            diagnostics.append(Diagnostic("error", "close.incomplete", f"lanes.{state['task_id']}", f"Lane is not closed: {state['state']}"))
    return ValidationResult(result.contract, diagnostics), states
