#!/usr/bin/env python3
# component: swarm-contract
# implements: ADR-0026, ADR-0027
# intent: docs/concepts/swarming-work.md
# constraints: read-only; standard library only; artifact content is data, never executable
# last_intent_review: 2026-09-20
"""Parse and validate Lintel swarm topology, scope, and close evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from typing import TYPE_CHECKING, Any, Iterable, Mapping, Optional, Sequence, Tuple, Union

if TYPE_CHECKING:
    from profile_context import ProfileConfig

from swarm_snapshot import bytes_digest, capture_result, git_changed_paths, value_digest, verify_result

SCHEMA_PATH = Path(__file__).with_name("swarm-schema.json")
EVIDENCE_START = "<!-- lintel-swarm-evidence:v2"
LEGACY_EVIDENCE_START = "<!-- lintel-swarm-evidence:v1"
EVIDENCE_END = "-->"
EVIDENCE_VERSION = 2
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
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
INITIATIVE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
SHARED_POINTERS = ("context", "review", "qa", "corroboration", "domain_request")


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


def _hardlink_identities(
    root: Path,
    parts: Tuple[str, ...],
    cache: dict[Tuple[str, ...], set[Tuple[int, int]]],
) -> set[Tuple[int, int]]:
    if parts in cache:
        return cache[parts]
    path = root.joinpath(*parts)
    try:
        metadata = path.stat()
    except (FileNotFoundError, NotADirectoryError):
        cache[parts] = set()
        return cache[parts]
    identities: set[Tuple[int, int]] = set()
    if stat.S_ISREG(metadata.st_mode) and metadata.st_nlink > 1:
        identities.add((metadata.st_dev, metadata.st_ino))
    elif stat.S_ISDIR(metadata.st_mode):
        def fail_walk(error: OSError) -> None:
            raise error

        for directory, _, filenames in os.walk(path, onerror=fail_walk, followlinks=False):
            for filename in filenames:
                metadata = (Path(directory) / filename).stat()
                if stat.S_ISREG(metadata.st_mode) and metadata.st_nlink > 1:
                    identities.add((metadata.st_dev, metadata.st_ino))
    cache[parts] = identities
    return identities


def _paths_overlap(
    root: Path,
    left: str,
    right: str,
    physical_files: Optional[dict[Tuple[str, ...], set[Tuple[int, int]]]] = None,
) -> bool:
    left_parts = _path_identity(root, left)
    right_parts = _path_identity(root, right)
    if left_parts is None or right_parts is None:
        return False
    shorter = min(len(left_parts), len(right_parts))
    if left_parts[:shorter] == right_parts[:shorter]:
        return True
    # Hard links retain distinct resolved names. Inspect physical identities once
    # per ownership check, including links inside declared directory scopes.
    cache = physical_files if physical_files is not None else {}
    left_files = _hardlink_identities(root, left_parts, cache)
    return bool(left_files and left_files.intersection(_hardlink_identities(root, right_parts, cache)))


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
        or any(character in "*?[" for character in value)
        or "//" in value
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        diagnostics.append(Diagnostic("error", "path.unsafe", field_path, f"Unsafe repository path: {value!r}"))
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or not pure.parts or any(part in ("", ".", "..") for part in pure.parts):
        diagnostics.append(Diagnostic("error", "path.unsafe", field_path, f"Unsafe repository path: {value!r}"))
        return None
    try:
        candidate = root.joinpath(*pure.parts).resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        diagnostics.append(Diagnostic("error", "path.resolve", field_path, "Cannot resolve repository path"))
        return None
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
        shared = lane.get("shared_evidence")
        if "shared_evidence" in lane:
            definition = schema.get("$defs", {}).get("sharedEvidence", {})
            if not isinstance(shared, dict) or set(shared) != set(definition.get("required", [])):
                diagnostics.append(Diagnostic("error", "shared.shape", prefix, "Shared evidence needs exactly the declared external pointer fields"))
                continue
            skill = shared.get("review_skill")
            if not isinstance(skill, str) or not IDENTIFIER.fullmatch(skill):
                diagnostics.append(Diagnostic("error", "shared.skill", prefix, "Shared review_skill must be a stable identifier"))
            for name in SHARED_POINTERS:
                if name in ("corroboration", "domain_request") and shared[name] is None:
                    continue
                path = _safe_repo_path(root, shared[name], f"{prefix}.shared_evidence.{name}", diagnostics)
                if path is not None and not path.endswith(".json"):
                    diagnostics.append(Diagnostic("error", "shared.path", prefix, "Shared provider artifacts must name individual JSON files"))
                if name == "review" and path is not None and not re.fullmatch(
                    r"\.claude/runtime/reviews/[A-Za-z0-9._-]+\.json", path,
                ):
                    diagnostics.append(Diagnostic("error", "shared.review_owner", prefix, "Reviewer-owned JSON must be a single record in .claude/runtime/reviews"))
    return valid_lanes


def _visible_markdown(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return re.sub(r"^(`{3,}|~{3,}).*?^\1[ \t]*$", "", text, flags=re.MULTILINE | re.DOTALL)


def _table_rows(text: str) -> Iterable[dict[str, str]]:
    headers: list[str] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            headers = []
            continue
        raw_cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        cells = [cell.strip("`").strip() for cell in raw_cells]
        lowered = [cell.casefold() for cell in cells]
        if "id" in lowered or "package id" in lowered:
            headers = lowered
        elif headers and len(cells) == len(headers) and not all(re.fullmatch(r"[-: ]+", cell) for cell in cells):
            yield {
                key: raw if key == "owner / edit boundary" else value
                for key, raw, value in zip(headers, raw_cells, cells)
            }


def _source_ids(value: str) -> list[str]:
    if value.strip().casefold() in ("", "-", "none", "n/a"):
        return []
    tokens = re.split(r"[,\s]+", value.replace("`", "").strip())
    if not all(IDENTIFIER.fullmatch(token) for token in tokens):
        raise ValueError("Expected explicit stable IDs, not ranges or free-form dependencies")
    return tokens


def _package_boundary_paths(root: Path, row: Mapping[str, str]) -> list[str]:
    if "owner / edit boundary" not in row:
        return []
    value = row["owner / edit boundary"].strip()
    owner_prefix = re.match(r"^[^`;]+;", value)
    if owner_prefix:
        value = value[owner_prefix.end():]
    boundaries: list[str] = []
    while value:
        token = re.match(r"\s*(?:`([^`\r\n]+)`|([^`,;]+?))\s*([,;]|$)", value)
        if token is None:
            raise ValueError("Explicit edit boundary must list literal repository paths")
        quoted, plain, separator = token.groups()
        path = quoted if quoted is not None else plain.strip()
        if not path or (quoted is None and any(char.isspace() for char in path)) or any(char in "<>" for char in path):
            raise ValueError("Explicit edit boundary requires literal paths; quote paths containing spaces with backticks")
        path = path[:-1] if path.endswith("/") else path
        diagnostics: list[Diagnostic] = []
        if _safe_repo_path(root, path, "work_map.plan.edit_boundary", diagnostics) is None:
            raise SwarmContractError(diagnostics)
        boundaries.append(path)
        value = value[token.end():].strip()
        if separator and not value:
            raise ValueError("Explicit edit boundary has an empty path")
    if not boundaries:
        raise ValueError("Explicit edit boundary is empty; it cannot authorize unrestricted scope")
    return boundaries


def _task_sources(text: str, requested: set[str]) -> dict[str, dict[str, Any]]:
    visible = _visible_markdown(text)
    definitions: dict[str, dict[str, list[str]]] = {}
    completed: dict[str, bool] = {}
    table_dependencies: dict[str, list[str]] = {}
    token = r"([A-Za-z0-9][A-Za-z0-9._-]{0,63})(?=\s|:|[—–]|$)"
    headings = list(re.finditer(r"^#{2,6}\s+" + token + r"[^\n]*", visible, re.MULTILINE))
    for index, match in enumerate(headings):
        task_id = match.group(1)
        if not any(char.isdigit() for char in task_id) and task_id not in requested:
            continue
        next_heading = re.search(r"^#{1,6}\s+", visible[match.end():], re.MULTILINE)
        end = match.end() + next_heading.start() if next_heading else len(visible)
        body = visible[match.start():end]
        definitions.setdefault(task_id, {}).setdefault("heading", []).append(body)
        checkboxes = re.findall(r"^\s*[-*+]\s+\[([ xX])\]", body, re.MULTILINE)
        if checkboxes:
            completed[task_id] = all(mark.casefold() == "x" for mark in checkboxes)
    for match in re.finditer(r"^\s*[-*+]\s+(?:\[([ xX])\]\s+)?" + token + r"[^\n]*", visible, re.MULTILINE):
        task_id = match.group(2)
        if not any(char.isdigit() for char in task_id) and task_id not in requested:
            continue
        definitions.setdefault(task_id, {}).setdefault("list", []).append(match.group(0))
        if match.group(1) is not None:
            completed[task_id] = match.group(1).casefold() == "x"
    for row in _table_rows(visible):
        task_id = row.get("id", "")
        if not IDENTIFIER.fullmatch(task_id):
            continue
        definitions.setdefault(task_id, {}).setdefault("table", []).append(json.dumps(row, sort_keys=True))
        table_dependencies[task_id] = _source_ids(row.get("deps", row.get("dependencies", "")))
    sources: dict[str, dict[str, Any]] = {}
    for task_id, kinds in definitions.items():
        body = "\n".join(part for values in kinds.values() for part in values)
        dependencies = list(table_dependencies.get(task_id, []))
        for dependency_text in re.findall(r"^\s*\*{0,2}Dependencies:\*{0,2}\s*(.*)$", body, re.MULTILINE):
            dependencies.extend(_source_ids(dependency_text))
        for dependency_text in re.findall(r"\(depends ([^;)]+)", body):
            dependencies.extend(_source_ids(dependency_text.replace(" and ", ",")))
        sources[task_id] = {
            "text": body,
            "dependencies": list(dict.fromkeys(dependencies)),
            "complete": completed.get(task_id, False),
            "duplicate": any(len(values) > 1 for values in kinds.values()),
            "verification_only": bool(re.search(r"\*{0,2}Result(?: kind)?:\*{0,2}\s*verification-only\b", body)),
        }
    return sources


def _packages_from_sources(
    root: Path,
    work_map: Optional[Mapping[str, Any]],
    lanes: Sequence[Mapping[str, Any]],
    diagnostics: list[Diagnostic],
) -> dict[str, dict[str, Any]]:
    if work_map is None:
        return {}
    tasks = _safe_repo_path(root, work_map.get("tasks"), "work_map.tasks", diagnostics, must_be_file=True)
    plan = _safe_repo_path(root, work_map.get("plan"), "work_map.plan", diagnostics, must_be_file=True)
    if tasks is None or plan is None:
        return {}
    try:
        task_text = root.joinpath(*_path_parts(tasks)).read_text(encoding="utf-8-sig")
        plan_text = root.joinpath(*_path_parts(plan)).read_text(encoding="utf-8-sig")
        requested = {lane["task_id"] for lane in lanes if isinstance(lane.get("task_id"), str)}
        sources = _task_sources(task_text, requested)
    except (OSError, ValueError) as error:
        diagnostics.append(Diagnostic("error", "tasks.read", "work_map.tasks", f"Cannot read mapped tasks: {error}"))
        return {}
    packages: dict[str, dict[str, Any]] = {}
    assigned: set[str] = set()
    for row in _table_rows(_visible_markdown(plan_text)):
        if "package id" not in row:
            continue
        package_id = row["package id"]
        members = next((value for key, value in row.items() if key.startswith("leaf ids")), "")
        try:
            leaf_ids = _source_ids(members)
            dependencies = _source_ids(row.get("dependencies", ""))
            if not IDENTIFIER.fullmatch(package_id) or not leaf_ids or package_id in packages:
                raise ValueError("Package ID must be unique and have explicit member leaves")
            if len(set(leaf_ids)) != len(leaf_ids) or assigned.intersection(leaf_ids):
                raise ValueError("Every leaf must have exactly one package membership")
            review = row.get("review", row.get("review depth", "substantive")).casefold()
            if review not in ("mechanical", "substantive"):
                raise ValueError("Review depth must be mechanical or substantive")
            result_kind = row.get("result", row.get("result kind", "change")).casefold()
            if result_kind not in ("change", "verification-only"):
                raise ValueError("Result kind must be change or verification-only")
            boundaries = _package_boundary_paths(root, row)
            packages[package_id] = {
                "package_id": package_id, "leaf_ids": leaf_ids, "dependencies": dependencies,
                "review": review, "verification_only": result_kind == "verification-only",
                "boundary_paths": boundaries, "leaves": {},
            }
            assigned.update(leaf_ids)
        except SwarmContractError as error:
            diagnostics.extend(error.diagnostics)
        except ValueError as error:
            diagnostics.append(Diagnostic("error", "package.membership", "work_map.plan", f"{package_id}: {error}"))
    grouped = bool(packages)
    if grouped:
        leaves = {task_id for task_id in sources if not any(other.startswith(task_id + ".") for other in sources)}
        for leaf_id in sorted(leaves - assigned):
            diagnostics.append(Diagnostic("error", "package.unassigned", "work_map.plan", f"Leaf is not assigned to a package: {leaf_id}"))
    else:
        for task_id in requested:
            if task_id in sources:
                packages[task_id] = {
                    "package_id": task_id, "leaf_ids": [task_id],
                    "dependencies": [], "review": "substantive",
                    "verification_only": sources[task_id]["verification_only"],
                    "boundary_paths": [], "leaves": {},
                }
    for package in packages.values():
        leaf_ids = package["leaf_ids"]
        for index, leaf_id in enumerate(leaf_ids):
            source = sources.get(leaf_id)
            if source is None:
                diagnostics.append(Diagnostic("error", "tasks.missing", "work_map.tasks", f"Package leaf is absent from mapped tasks: {leaf_id}"))
                continue
            if source["duplicate"]:
                diagnostics.append(Diagnostic("error", "tasks.duplicate", "work_map.tasks", f"Task has multiple definitions of the same kind: {leaf_id}"))
            if grouped and any(other.startswith(leaf_id + ".") for other in sources):
                diagnostics.append(Diagnostic("error", "package.parent", "work_map.plan", f"Package membership must select leaves, not their parent: {leaf_id}"))
            package["leaves"][leaf_id] = source
            for dependency in source["dependencies"]:
                if dependency in leaf_ids and leaf_ids.index(dependency) >= index:
                    diagnostics.append(Diagnostic("error", "package.order", "work_map.plan", f"{leaf_id} precedes its prerequisite {dependency}"))
                elif dependency not in leaf_ids:
                    package["dependencies"].append(dependency)
        package["dependencies"] = list(dict.fromkeys(package["dependencies"]))
    for package in packages.values():
        package["prerequisites"] = {
            dependency: (
                all(packages[dependency]["leaves"].get(leaf, {}).get("complete", False)
                    for leaf in packages[dependency]["leaf_ids"])
                if dependency in packages else sources.get(dependency, {}).get("complete", False)
            )
            for dependency in package["dependencies"]
        }
    for lane in lanes:
        task_id = lane.get("task_id")
        package = packages.get(task_id)
        if package is None:
            diagnostics.append(Diagnostic("error", "tasks.missing", "work_map.tasks", f"Lane has no authoritative package/singleton: {task_id}"))
        elif package["boundary_paths"] and isinstance(lane.get("write_scope"), list):
            for scope in lane["write_scope"]:
                if isinstance(scope, str) and not any(_path_owned(root, scope, boundary) for boundary in package["boundary_paths"]):
                    diagnostics.append(Diagnostic("error", "package.scope", f"lanes.{task_id}.write_scope", "Lane scope exceeds the explicit package edit boundary"))
    return packages


def package_sources(repo: Union[Path, str], contract: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Read package membership and original leaf definitions; never persist a second backlog."""
    root = Path(repo).resolve()
    diagnostics: list[Diagnostic] = []
    work_map, _ = _load_work_map(root, contract.get("work_map"), diagnostics)
    packages = _packages_from_sources(root, work_map, contract.get("lanes", []), diagnostics)
    if any(item.severity == "error" for item in diagnostics):
        raise SwarmContractError(diagnostics)
    return packages


def _validate_topology(
    root: Path,
    data: Mapping[str, Any],
    lanes: Sequence[Mapping[str, Any]],
    protected_paths: Sequence[str],
    diagnostics: list[Diagnostic],
    physical_files: dict[Tuple[str, ...], set[Tuple[int, int]]],
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
                if _paths_overlap(root, raw_scope, protected, physical_files):
                    diagnostics.append(Diagnostic("error", "scope.protected", f"lanes.{lane.get('task_id')}.write_scope", f"Worker scope overlaps coordinator/reviewer-owned path {protected}: {raw_scope}"))
    for wave, wave_lanes in sorted(by_wave.items()):
        for left_index, left in enumerate(wave_lanes):
            left_scope = left.get("write_scope") if isinstance(left.get("write_scope"), list) else []
            for right in wave_lanes[left_index + 1 :]:
                right_scope = right.get("write_scope") if isinstance(right.get("write_scope"), list) else []
                for left_path in left_scope:
                    for right_path in right_scope:
                        if isinstance(left_path, str) and isinstance(right_path, str) and _paths_overlap(root, left_path, right_path, physical_files):
                            diagnostics.append(Diagnostic("error", "wave.scope_overlap", f"lanes.wave[{wave}]", f"Same-wave scopes overlap for {left.get('task_id')} and {right.get('task_id')}: {left_path} <> {right_path}"))
        if len(wave_lanes) > 1:
            if data.get("max_parallel") == 1:
                diagnostics.append(Diagnostic("warning", "wave.sequenced", f"lanes.wave[{wave}]", "Multiple lanes will use the sequenced fallback because max_parallel is 1"))
            else:
                for lane in wave_lanes:
                    if lane.get("isolation") not in ISOLATION_BACKENDS:
                        diagnostics.append(Diagnostic("error", "wave.isolation_missing", f"lanes.{lane.get('task_id')}.isolation", "Every writer in a concurrent wave requires attributable isolation"))


def _lane_artifacts(lane: Mapping[str, Any]) -> Iterable[tuple[str, str]]:
    for name in ("brief", "report", "review"):
        if isinstance(lane.get(name), str):
            yield name, lane[name]
    if isinstance(lane.get("shared_evidence"), dict):
        for name in SHARED_POINTERS:
            path = lane["shared_evidence"].get(name)
            if isinstance(path, str):
                yield "shared_evidence." + name, path


def _validate_artifact_ownership(
    root: Path,
    lanes: Sequence[Mapping[str, Any]],
    coordinator_paths: Sequence[str],
    diagnostics: list[Diagnostic],
    physical_files: dict[Tuple[str, ...], set[Tuple[int, int]]],
) -> None:
    artifacts: list[tuple[str, str]] = []
    for lane in lanes:
        for name, path in _lane_artifacts(lane):
            owner = f"lanes.{lane.get('task_id')}.{name}"
            for protected in coordinator_paths:
                if name.startswith("shared_evidence.") and protected == ".claude/runtime":
                    continue
                if _paths_overlap(root, path, protected, physical_files):
                    diagnostics.append(Diagnostic("error", "artifact.coordinator", owner, f"Handoff artifact overlaps coordinator authority/output: {protected}"))
            for prior_path, prior_owner in artifacts:
                if _paths_overlap(root, path, prior_path, physical_files):
                    diagnostics.append(Diagnostic("error", "artifact.overlap", owner, f"Handoff artifact overlaps {prior_owner}: {prior_path}"))
            artifacts.append((path, owner))


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
    _packages_from_sources(root, work_map, lanes, diagnostics)
    protected: list[str] = [coordination_path, *UNIVERSAL_COORDINATOR_PATHS]
    for value in (data.get("work_map"), data.get("charter")):
        if isinstance(value, str):
            protected.append(value)
    if work_map is not None:
        for name in ("spec", "plan", "tasks", "prompt", "constitution"):
            if isinstance(work_map.get(name), str):
                protected.append(work_map[name])
    coordinator_paths = data.get("coordinator_paths", [])
    if not isinstance(coordinator_paths, list):
        diagnostics.append(Diagnostic("error", "coordinator_paths.type", "coordinator_paths", "Expected a list of coordinator-owned paths"))
    else:
        seen: set[Tuple[str, ...]] = set()
        for index, value in enumerate(coordinator_paths):
            path = _safe_repo_path(root, value, f"coordinator_paths[{index}]", diagnostics)
            if path is None:
                continue
            identity = _path_identity(root, path)
            if identity in seen:
                diagnostics.append(Diagnostic("error", "coordinator_paths.duplicate", f"coordinator_paths[{index}]", "Duplicate coordinator-owned path or alias"))
            elif identity is not None:
                seen.add(identity)
            protected.append(path)
    physical_files: dict[Tuple[str, ...], set[Tuple[int, int]]] = {}
    try:
        _validate_artifact_ownership(root, lanes, protected, diagnostics, physical_files)
        for lane in lanes:
            protected.extend(path for _, path in _lane_artifacts(lane))
        _validate_topology(root, data, lanes, protected, diagnostics, physical_files)
    except OSError as error:
        diagnostics.append(Diagnostic("error", "path.identity", "ownership", f"Cannot verify physical file ownership: {error}"))
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
    actor: str = "worker",
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    task_id = str(lane.get("task_id"))
    scopes = [item for item in lane.get("write_scope", []) if isinstance(item, str)]
    own_report = lane.get("report")
    own_review = lane.get("review")
    own_report_identity = _path_identity(root, own_report) if isinstance(own_report, str) else None
    own_review_identity = _path_identity(root, own_review) if isinstance(own_review, str) else None
    shared = lane.get("shared_evidence", {})
    own_shared_review = shared.get("review") if isinstance(shared, dict) else None
    own_shared_review_identity = _path_identity(root, own_shared_review) if isinstance(own_shared_review, str) else None
    shared_artifacts = {
        _path_identity(root, path)
        for item in contract.get("lanes", []) if isinstance(item, Mapping)
        for name, path in _lane_artifacts(item) if name.startswith("shared_evidence.")
    }
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
        if actor == "reviewer":
            if identity not in (own_review_identity, own_shared_review_identity):
                diagnostics.append(Diagnostic("error", "scope.reviewer", f"changed_paths[{index}]", f"Reviewer of {task_id} may change only its own review artifact"))
            continue
        if any(_paths_overlap(root, path, protected) for protected in UNIVERSAL_COORDINATOR_PATHS):
            diagnostics.append(Diagnostic("error", "scope.universal", f"changed_paths[{index}]", f"Lane {task_id} may not change universal coordinator path: {path}"))
        elif identity == own_review_identity or identity in all_reviews or identity in all_briefs or identity in other_reports or identity in shared_artifacts:
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
    *,
    actor: str = "worker",
) -> ValidationResult:
    result = validate_coordination(repo, coordination_path)
    if not result.ok or result.contract is None:
        return result
    diagnostics = list(result.diagnostics)
    if actor not in ("worker", "reviewer"):
        diagnostics.append(Diagnostic("error", "scope.actor", "actor", "actor must be worker or reviewer"))
        return ValidationResult(result.contract, diagnostics)
    lane = lane_by_task(result.contract, task_id)
    if lane is None:
        diagnostics.append(Diagnostic("error", "scope.unknown_lane", "task_id", f"Unknown lane: {task_id}"))
        return ValidationResult(result.contract, diagnostics)
    if not changed_paths:
        diagnostics.append(Diagnostic("error", "scope.empty", "changed_paths", "At least one attributable changed path is required"))
        return ValidationResult(result.contract, diagnostics)
    root = Path(repo).resolve()
    diagnostics.extend(_lane_scope_diagnostics(root, result.contract, lane, changed_paths, actor))
    return ValidationResult(result.contract, diagnostics)


def acceptance_digest(repo: Union[Path, str], contract: Mapping[str, Any], lane: Mapping[str, Any]) -> str:
    root = Path(repo).resolve()
    work_map = _read_json(root / contract["work_map"])
    paths = {work_map[name] for name in ("spec", "plan", "tasks", "prompt")}
    paths.update((contract["charter"], lane["brief"]))
    if work_map.get("constitution"):
        paths.add(work_map["constitution"])
    sources = {}
    for path in sorted(paths):
        diagnostics: list[Diagnostic] = []
        if _safe_repo_path(root, path, "acceptance", diagnostics, must_be_file=True) is None:
            raise SwarmContractError(diagnostics)
        text = (root / path).read_text(encoding="utf-8-sig")
        sources[path] = re.sub(r"^(\s*[-*+]\s+)\[[ xX]\]", r"\1[ ]", text, flags=re.MULTILINE)
    return value_digest({
        "work_map": contract["work_map"],
        "mapping": {key: value for key, value in work_map.items() if key != "status"},
        "coordination": contract, "sources": sources,
    })


def snapshot_lane(
    repo: Union[Path, str], coordination_path: str, task_id: str, attempt_id: str,
    *, base: Optional[str] = None, head: Optional[str] = None,
) -> dict[str, Any]:
    """Capture observable inputs/results only; this does not author a PASS or run a reviewer."""
    contract = load_swarm_contract(repo, coordination_path)
    lane = lane_by_task(contract, task_id)
    if lane is None or not isinstance(attempt_id, str) or not IDENTIFIER.fullmatch(attempt_id):
        raise ValueError("A known lane and stable attempt_id are required")
    package = package_sources(repo, contract)[task_id]
    result = capture_result(Path(repo).resolve(), lane["write_scope"], base=base, head=head)
    if result["kind"] == "git":
        diagnostics = _lane_scope_diagnostics(Path(repo).resolve(), contract, lane, result["changes"])
        if diagnostics:
            raise SwarmContractError(diagnostics)
    return {
        "work_map": contract["work_map"], "package_id": task_id,
        "leaf_ids": package["leaf_ids"], "attempt_id": attempt_id,
        "acceptance_digest": acceptance_digest(repo, contract, lane),
        "result": result, "result_digest": value_digest(result),
    }


def brief_payload(repo: Union[Path, str], coordination_path: str, task_id: str) -> dict[str, Any]:
    """Adapt an existing rich brief to the shared envelope body without replacing task authority."""
    from envelope_contract import markdown_brief, validate_content

    contract = load_swarm_contract(repo, coordination_path)
    lane = lane_by_task(contract, task_id)
    if lane is None:
        raise ValueError("Unknown package/singleton lane")
    root = Path(repo).resolve()
    package = package_sources(root, contract)[task_id]
    original = (root / lane["brief"]).read_text(encoding="utf-8-sig")
    content, pointers = markdown_brief(original)
    content.update(
        work_map=contract["work_map"], package_id=task_id, leaf_ids=package["leaf_ids"],
        write_scope=lane["write_scope"], acceptance_digest=acceptance_digest(root, contract, lane),
    )
    work_map = _read_json(root / contract["work_map"])
    pointers = list(dict.fromkeys([
        contract["work_map"], *(work_map[name] for name in ("spec", "plan", "tasks", "prompt")),
        contract["charter"], lane["brief"], *pointers,
    ]))
    validate_content("brief", content)
    return {"content": content, "context_pointers": pointers}


def review_binding(repo: Union[Path, str], lane: Mapping[str, Any], report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        **{name: report.get(name) for name in (
            "work_map", "package_id", "leaf_ids", "attempt_id", "acceptance_digest", "result_digest"
        )},
        "report_digest": bytes_digest((Path(repo) / lane["report"]).read_bytes()),
    }


def _read_evidence(path: Path, kind: str, task_id: str, diagnostics: list[Diagnostic]) -> Optional[dict[str, Any]]:
    if not path.is_file():
        diagnostics.append(Diagnostic("error", "evidence.missing", str(path), f"Missing {kind} evidence for {task_id}"))
        return None
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        diagnostics.append(Diagnostic("error", "evidence.read", str(path), f"Cannot read {kind} evidence: {error}"))
        return None
    starts = text.count(EVIDENCE_START) + text.count(LEGACY_EVIDENCE_START)
    if starts != 1:
        diagnostics.append(Diagnostic("error", "evidence.marker", str(path), f"Expected exactly one {EVIDENCE_START} marker"))
        return None
    marker = EVIDENCE_START if EVIDENCE_START in text else LEGACY_EVIDENCE_START
    start = text.index(marker) + len(marker)
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
        or data.get("schema_version") != (EVIDENCE_VERSION if marker == EVIDENCE_START else 1)
        or data.get("artifact_kind") != f"swarm-{kind}"
        or data.get("task_id") != task_id
    ):
        diagnostics.append(Diagnostic("error", "evidence.identity", str(path), f"Evidence identity does not match {kind} for {task_id}"))
    if marker == LEGACY_EVIDENCE_START:
        diagnostics.append(Diagnostic("error", "evidence.unbound", str(path), "Historical v1 evidence is preserved but cannot close a current content-bound attempt"))
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
    package = package_sources(root, contract)[task_id]
    if type(report.get("status")) is not str or report.get("status") != "complete":
        diagnostics.append(Diagnostic("error", "report.incomplete", lane["report"], f"Report for {task_id} is not complete"))
    if type(report.get("worker")) is not str or not report["worker"].strip():
        diagnostics.append(Diagnostic("error", "report.worker", lane["report"], f"Report for {task_id} must name a nonempty worker identity"))
    for field_name in ("actor_ref", "isolation_ref"):
        if type(report.get(field_name)) is not str or not report[field_name].strip():
            diagnostics.append(Diagnostic("error", "report.provenance", lane["report"], f"Report must declare {field_name}; a role name is not host attribution"))
    if (
        report.get("work_map") != contract["work_map"] or report.get("package_id") != task_id
        or report.get("leaf_ids") != package["leaf_ids"]
        or type(report.get("attempt_id")) is not str or not IDENTIFIER.fullmatch(report["attempt_id"])
    ):
        diagnostics.append(Diagnostic("error", "report.binding", lane["report"], "Work/package/leaf/attempt identity is missing or mismatched"))
    try:
        if report.get("acceptance_digest") != acceptance_digest(root, contract, lane):
            diagnostics.append(Diagnostic("error", "report.acceptance", lane["report"], "Acceptance or handoff source changed; capture and review a new attempt"))
        result = report.get("result")
        if not isinstance(result, dict):
            raise ValueError("Observable result snapshot is required")
        verify_result(root, lane["write_scope"], result)
        if report.get("result_digest") != value_digest(result):
            raise ValueError("Result digest does not match the supplied result snapshot")
        if result["kind"] == "git":
            diagnostics.extend(_lane_scope_diagnostics(root, contract, lane, result["changes"]))
    except (OSError, ValueError) as error:
        diagnostics.append(Diagnostic("error", "report.result", lane["report"], str(error)))
    leaf_results = report.get("leaf_results")
    if (
        not isinstance(leaf_results, dict) or set(leaf_results) != set(package["leaf_ids"])
        or not all(_passing_checks(checks) for checks in leaf_results.values())
    ):
        diagnostics.append(Diagnostic("error", "report.leaves", lane["report"], "Every original member leaf needs nonempty passing acceptance checks"))
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
        if not has_product_change and not package["verification_only"]:
            diagnostics.append(Diagnostic("error", "report.product_change", lane["report"], f"Report for {task_id} must include a changed path in declared write_scope in addition to its own report"))
        result = report.get("result")
        if isinstance(result, dict) and isinstance(result.get("files"), dict):
            product_paths = {path for path in changed_paths if _path_identity(root, path) != report_identity}
            if package["verification_only"] and product_paths:
                diagnostics.append(Diagnostic("error", "report.verification_only", lane["report"], "Verification-only work cannot claim product edits"))
            if result.get("kind") == "git" and isinstance(result.get("changes"), list):
                observed = {path for path in result["changes"] if _path_identity(root, path) != report_identity}
                if product_paths != observed:
                    diagnostics.append(Diagnostic("error", "report.attribution", lane["report"], "Reported product paths differ from the actual Git base/head diff"))
            elif any(path not in result["files"] for path in product_paths):
                diagnostics.append(Diagnostic("error", "report.product_missing", lane["report"], "Claimed product path has no observable file; deletions require Git base/head evidence"))
    return diagnostics


def _review_evidence_diagnostics(
    root: Path, contract: Mapping[str, Any], lane: Mapping[str, Any],
    report: Mapping[str, Any], review: Mapping[str, Any],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    paths = review.get("changed_paths")
    if not _nonempty_string_list(paths):
        diagnostics.append(Diagnostic("error", "review.changed_paths", lane["review"], "Reviewer must declare its attributable changed paths"))
    else:
        diagnostics.extend(_lane_scope_diagnostics(root, contract, lane, paths, "reviewer"))
    if review.get("binding") != review_binding(root, lane, report):
        diagnostics.append(Diagnostic("error", "review.binding", lane["review"], "Review does not bind this exact work, attempt, acceptance, result and report"))
    package = package_sources(root, contract)[lane["task_id"]]
    mode = review.get("mode")
    if mode not in ("independent", "coordinator") or (mode == "coordinator" and package["review"] != "mechanical"):
        diagnostics.append(Diagnostic("error", "review.mode", lane["review"], "Substantive packages require independent review; inline review must be explicitly mechanical"))
    actor = review.get("actor_ref")
    if not isinstance(actor, str) or not actor.strip() or (
        mode == "independent" and actor.strip().casefold() == str(report.get("actor_ref", "")).strip().casefold()
    ):
        diagnostics.append(Diagnostic("error", "review.provenance", lane["review"], "Independent reviewer needs a distinct attributable actor reference"))
    if review.get("base") is not None or review.get("head") is not None:
        try:
            observed = git_changed_paths(root, review.get("base"), review.get("head"))
            diagnostics.extend(_lane_scope_diagnostics(root, contract, lane, observed, "reviewer"))
            if observed != paths:
                raise ValueError("Reviewer changed_paths differ from its actual Git diff")
        except (OSError, ValueError) as error:
            diagnostics.append(Diagnostic("error", "review.attribution", lane["review"], str(error)))
    return diagnostics


def review_input(repo: Union[Path, str], coordination_path: str, task_id: str) -> dict[str, Any]:
    contract = load_swarm_contract(repo, coordination_path)
    lane = lane_by_task(contract, task_id)
    if lane is None:
        raise ValueError("Unknown package/singleton lane")
    root = Path(repo).resolve()
    diagnostics: list[Diagnostic] = []
    report = _read_evidence(root / lane["report"], "report", task_id, diagnostics)
    if report is not None:
        diagnostics.extend(_report_evidence_diagnostics(root, contract, lane, report))
    if diagnostics or report is None:
        raise SwarmContractError(diagnostics)
    package = package_sources(root, contract)[task_id]
    return {
        "binding": review_binding(root, lane, report),
        "report": lane["report"], "review": lane["review"], "review_requirement": package["review"],
        "result": report["result"], "leaf_results": report["leaf_results"],
        "shared_evidence": lane.get("shared_evidence"),
        "verification": "local_observations_only", "release_clearance": False,
        "independence": "A real independent actor must act; this export is not review evidence",
    }


def local_lane_states(repo: Union[Path, str], contract: Mapping[str, Any]) -> Tuple[list[dict[str, Any]], list[Diagnostic]]:
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
        if report is not None and review is not None:
            review_diagnostics.extend(_review_evidence_diagnostics(root, contract, lane, report, review))
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
                or (review.get("mode") != "coordinator" and report["worker"].strip().casefold() == review["reviewer"].strip().casefold())
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


def lane_states(
    repo: Union[Path, str], contract: Mapping[str, Any], *, coordination_path: Optional[str] = None,
    profile_config: Optional[ProfileConfig] = None,
) -> Tuple[list[dict[str, Any]], list[Diagnostic]]:
    states, diagnostics = local_lane_states(repo, contract)
    for state in states:
        state["local_state"] = state["state"]
        state["verification"] = "local_observations_only"
        if state["state"] != "complete":
            continue
        lane = lane_by_task(contract, state["task_id"])
        local_diagnostics: list[Diagnostic] = []
        try:
            from swarm_evidence import verify_shared_lane
            root = Path(repo).resolve()
            report = _read_evidence(root / lane["report"], "report", lane["task_id"], local_diagnostics)
            review = _read_evidence(root / lane["review"], "review", lane["task_id"], local_diagnostics)
            if report is None or review is None or local_diagnostics:
                raise ValueError("Local report/review changed during shared consumption")
            if coordination_path is None:
                mapping = _read_json(root / contract["work_map"])
                coordination_path = mapping["coordination"]
            shared = verify_shared_lane(
                root, coordination_path, contract, lane, package_sources(root, contract)[lane["task_id"]],
                report, review, profile_config=profile_config,
            )
        except (ImportError, OSError, ValueError) as error:
            shared = {"ok": False, "status": "unverified", "problems": [str(error)], "release_clearance": False}
        state["shared_evidence"] = shared
        if not shared["ok"]:
            state["state"] = "awaiting_shared_evidence"
            diagnostics.append(Diagnostic("error", "shared.blocked", f"lanes.{lane['task_id']}", "; ".join(shared["problems"])))
        else:
            state["verification"] = "current_shared_evidence"
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


def _dependency_blockers(
    packages: Mapping[str, Mapping[str, Any]], states: Sequence[Mapping[str, Any]],
) -> dict[str, list[str]]:
    owners = {leaf: key for key, package in packages.items() for leaf in package["leaf_ids"]}
    by_id = {state["task_id"]: state["state"] for state in states}
    external_leaves = {
        dependency: complete
        for package in packages.values() for dependency, complete in package["prerequisites"].items()
        if dependency not in packages and dependency not in owners
    }

    def satisfied(dependency: str, visiting: frozenset[str]) -> bool:
        if dependency in visiting:
            return False
        following = visiting | {dependency}
        if dependency in packages:
            package = packages[dependency]
            complete = (
                by_id[dependency] == "complete" if dependency in by_id else
                all(package["leaves"][leaf]["complete"] for leaf in package["leaf_ids"])
            )
            return complete and all(satisfied(prerequisite, following) for prerequisite in package["dependencies"])
        owner = owners.get(dependency)
        if owner in by_id:
            return satisfied(owner, following)
        if owner is not None:
            leaf = packages[owner]["leaves"][dependency]
            return leaf["complete"] and all(satisfied(prerequisite, following) for prerequisite in leaf["dependencies"])
        return external_leaves.get(dependency, False)

    blocked: dict[str, list[str]] = {}
    for task_id in by_id:
        package = packages[task_id]
        for dependency in package["dependencies"]:
            if not satisfied(dependency, frozenset({task_id})):
                blocked.setdefault(task_id, []).append(dependency)
    return blocked


def _frontier(
    repo: Union[Path, str], coordination_path: str, *, host_capability: Optional[str] = None,
    profile_config: Optional[ProfileConfig] = None, local_observations: bool = False,
) -> Tuple[ValidationResult, dict[str, Any]]:
    result = validate_coordination(repo, coordination_path)
    if not result.ok or result.contract is None:
        return result, {"wave": None, "ready_task_ids": [], "dispatch_task_ids": [], "states": []}
    states, evidence_diagnostics = (
        local_lane_states(repo, result.contract) if local_observations else
        lane_states(repo, result.contract, coordination_path=coordination_path, profile_config=profile_config)
    )
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
    blocked_by = _dependency_blockers(package_sources(repo, result.contract), states)
    if not incomplete:
        if blocked_by:
            diagnostics.append(Diagnostic("error", "wave.prerequisites", "work_map.tasks", "Declared completion has unresolved authoritative prerequisites"))
        return ValidationResult(result.contract, diagnostics), {"work_map_status": work_map_status, "wave": None, "ready_task_ids": [], "dispatch_task_ids": [], "blocked_by": blocked_by, "states": states}
    wave = min(state["wave"] for state in incomplete)
    frontier = [state["task_id"] for state in incomplete if state["wave"] == wave and state["state"] in ("not_started", "rework_required")]
    frontier = [task_id for task_id in frontier if task_id not in blocked_by]
    capacity = result.contract.get("max_parallel", 1)
    if host_capability not in (None, "native", "sequenced", "none"):
        diagnostics.append(Diagnostic("error", "host.capability", "host_capability", "Expected native, sequenced or none"))
        capacity = 0
    elif host_capability in ("sequenced", "none"):
        capacity = min(capacity, 1)
    return ValidationResult(result.contract, diagnostics), {
        "work_map_status": work_map_status,
        "wave": wave,
        "ready_task_ids": frontier,
        "dispatch_task_ids": frontier[:capacity],
        "blocked_by": blocked_by,
        "host_capability": host_capability or "unverified",
        "capability_source": "caller-declared; not a probe of host tools",
        "execution_mode": "manual" if host_capability == "none" else "sequenced" if capacity <= 1 else "isolation-required",
        "states": states,
    }


def ready_frontier(
    repo: Union[Path, str], coordination_path: str, *, host_capability: Optional[str] = None,
    profile_config: Optional[ProfileConfig] = None,
) -> Tuple[ValidationResult, dict[str, Any]]:
    return _frontier(repo, coordination_path, host_capability=host_capability, profile_config=profile_config)


def inspect_local_frontier(
    repo: Union[Path, str], coordination_path: str, *, host_capability: Optional[str] = None,
) -> Tuple[ValidationResult, dict[str, Any]]:
    result, frontier = _frontier(repo, coordination_path, host_capability=host_capability, local_observations=True)
    frontier.update(verification="local_observations_only", release_clearance=False)
    return result, frontier


def _close(
    repo: Union[Path, str], coordination_path: str, *, profile_config: Optional[ProfileConfig] = None,
    local_observations: bool = False,
) -> Tuple[ValidationResult, list[dict[str, Any]]]:
    result = validate_coordination(repo, coordination_path)
    if not result.ok or result.contract is None:
        return result, []
    states, evidence_diagnostics = (
        local_lane_states(repo, result.contract) if local_observations else
        lane_states(repo, result.contract, coordination_path=coordination_path, profile_config=profile_config)
    )
    diagnostics = list(result.diagnostics) + evidence_diagnostics
    status = _contract_work_map_status(Path(repo).resolve(), result.contract, diagnostics)
    if status not in ("APPROVED", "COMPLETE"):
        diagnostics.append(Diagnostic("error", "close.work_map_status", "work_map.status", "Closing work requires current approval or a completed work map"))
    for task_id, dependencies in _dependency_blockers(package_sources(repo, result.contract), states).items():
        diagnostics.append(Diagnostic("error", "close.prerequisites", f"lanes.{task_id}", "Unresolved authoritative prerequisites: " + ", ".join(dependencies)))
    for state in states:
        if state["state"] != "complete":
            diagnostics.append(Diagnostic("error", "close.incomplete", f"lanes.{state['task_id']}", f"Lane is not closed: {state['state']}"))
    return ValidationResult(result.contract, diagnostics), states


def verify_close(
    repo: Union[Path, str], coordination_path: str, *, profile_config: Optional[ProfileConfig] = None,
) -> Tuple[ValidationResult, list[dict[str, Any]]]:
    return _close(repo, coordination_path, profile_config=profile_config)


def inspect_local(repo: Union[Path, str], coordination_path: str) -> Tuple[ValidationResult, list[dict[str, Any]]]:
    """Validate retained local observations only; this never supplies shared acceptance."""
    return _close(repo, coordination_path, local_observations=True)
