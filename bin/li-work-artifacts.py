#!/usr/bin/env python3
# component: work-artifact-map
# implements: ADR-0024, ADR-0027, ADR-0028
# intent: docs/spec-kit.md
# constraints: read-only; paths must stay inside the working repository
# last_intent_review: 2026-09-20
"""Validate a committed work map without reading runtime state or executing content."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import sys
sys.dont_write_bytecode = True
from typing import Sequence, Union

SOURCE_ROOT = Path(__file__).resolve().parent.parent
if str(SOURCE_ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT / "lib"))

from swarm_contract import validate_work_map_swarm_fields  # noqa: E402

SCHEMA_VERSION = 1
REQUIRED_ARTIFACTS = ("spec", "plan", "tasks", "prompt")


def artifact_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("Artifact paths must be nonempty repository-relative POSIX paths")
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Artifact path escapes the repository: {value}")
    path = (root / value).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f"Artifact is missing or outside the repository: {value}")
    return path


def load_work_map(root: Path, map_path: Path) -> dict:
    root = root.resolve()
    map_path = (root / map_path).resolve()
    if not map_path.is_relative_to(root):
        raise ValueError("Work map must be inside the repository")
    data = json.loads(map_path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != SCHEMA_VERSION:
        raise ValueError("Unsupported work-map schema_version")
    if data.get("workflow") not in ("lintel", "spec-kit"):
        raise ValueError("workflow must be lintel or spec-kit")
    if data.get("status") not in ("DRAFT", "APPROVED", "COMPLETE"):
        raise ValueError("status must be DRAFT, APPROVED or COMPLETE")
    for field in REQUIRED_ARTIFACTS:
        artifact_path(root, data.get(field))
    if data.get("constitution") is not None:
        artifact_path(root, data["constitution"])
    relative_map = map_path.relative_to(root).as_posix()
    swarm_result = validate_work_map_swarm_fields(root, data, relative_map)
    if not swarm_result.ok:
        details = "; ".join(
            f"{item.code} at {item.path}: {item.message}"
            for item in swarm_result.diagnostics
        )
        raise ValueError(f"Invalid swarm work-map extension: {details}")
    return data


def work_context(
    root: Path, map_path: Path, *, warm_paths: Sequence[str] = (), max_files: int = 40,
    max_bytes: int = 262144, package_id: str = "", leaf_ids: Sequence[str] = (),
    acceptance_paths: Sequence[Union[str, dict]] = (),
) -> dict:
    """Derive a read-only view of original artifacts, not another work/status authority."""
    from context_safety import checked_root, read_owned, select_files
    from swarm_contract import _task_sources, load_swarm_contract, package_sources

    root = checked_root(root)
    mapping = load_work_map(root, map_path)
    selected = (root / map_path).resolve().relative_to(root).as_posix()
    artifacts = {key: mapping[key] for key in REQUIRED_ARTIFACTS}
    if mapping.get("constitution"):
        artifacts["constitution"] = mapping["constitution"]
    coordination = mapping.get("coordination")
    context_paths = [selected, *artifacts.values(), *([coordination] if coordination else [])]
    if any(any(char in path for char in "\r\n\t") for path in context_paths):
        raise ValueError("Selected paths contain control characters and cannot be carried in the ledger")
    manifest = select_files(root, paths=[*context_paths, *warm_paths],
                            max_files=max_files, max_bytes=max_bytes)
    if manifest["status"] != "selected":
        raise ValueError(f"Selected work input is incomplete: {manifest['unmatched']}")
    present = {item["path"] for item in manifest["files"]}
    required = {artifact_path(root, path).relative_to(root).as_posix() for path in context_paths}
    if not required <= present:
        raise ValueError("A required work artifact was excluded by the bounded selector")
    texts = {}
    for key, path in artifacts.items():
        text = read_owned(root, path, max_bytes)[0].decode("utf-8-sig")
        if not text.strip():
            raise ValueError(f"Selected {key} artifact is empty: {path}")
        texts[key] = text
    # P04 owns task/package interpretation, including flat, phased, tree and Spec Kit.
    # Match package_sources' universal-newline read, without changing source
    # bytes or P03/P05 hashes.
    task_text = texts["tasks"].replace("\r\n", "\n").replace("\r", "\n")
    contract = (load_swarm_contract(root, coordination) if coordination
                else {"work_map": selected, "lanes": []})
    if artifact_path(root, contract["work_map"]) != artifact_path(root, selected):
        raise ValueError("Selected coordination points to a different work map")
    packages = package_sources(root, contract)
    recognized = {leaf for package in packages.values() for leaf in package["leaf_ids"]}
    tasks = _task_sources(task_text, set(leaf_ids) | recognized)
    leaves = [key for key in tasks if not any(other.startswith(key + ".") for other in tasks)]
    if not packages:
        packages = package_sources(root, {"work_map": selected,
                                          "lanes": [{"task_id": key} for key in leaves]})
    binding = None
    if package_id or leaf_ids or acceptance_paths:
        if not package_id or not leaf_ids or len(set(leaf_ids)) != len(leaf_ids):
            raise ValueError("Acceptance binding requires a package and unique original leaf IDs")
        if any(key not in leaves for key in leaf_ids):
            raise ValueError("Acceptance binding names a missing task or parent rather than a leaf")
        from review_contract import bind_work
        binding = bind_work(root, work_map=selected, package_id=package_id,
                            leaf_ids=list(leaf_ids),
                            acceptance_paths=list(acceptance_paths) or [mapping["spec"]])
    return {"work_map": selected, "workflow": mapping["workflow"], "status": mapping["status"],
            "artifacts": artifacts, "tasks": tasks, "packages": packages,
            "incomplete_ids": [key for key in leaves if not tasks[key]["complete"]],
            "task_evidence": "source-status-only" if tasks else "unrecognized",
            "manifest": manifest, "warming": "selected" if warm_paths else "not-supplied",
            "binding": binding, "release_clearance": False}


def work_budget(context: dict, **capacity) -> dict:
    """Use P03's capacity/usage interpretation over the exact selected input bytes."""
    from context_safety import context_budget
    return {**context_budget(context["manifest"]["bytes"], **capacity),
            "work_map": context["work_map"], "artifacts": context["artifacts"],
            "warming": context["warming"], "policy": "advisory", "release_clearance": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--map", type=Path, required=True, help="explicit committed work.json path")
    parser.add_argument("--view", choices=("map", "context", "budget"), default="map")
    parser.add_argument("--field", help="print one selected field, such as artifacts.tasks")
    parser.add_argument("--warm-path", action="append", default=[], help="literal repo-relative warming input")
    parser.add_argument("--max-files", type=int, default=40)
    parser.add_argument("--max-bytes", type=int, default=262144)
    parser.add_argument("--package", default="")
    parser.add_argument("--leaf", action="append", default=[])
    parser.add_argument("--acceptance", action="append", default=[])
    parser.add_argument("--capacity", type=int)
    parser.add_argument("--capacity-source")
    parser.add_argument("--used", type=int)
    parser.add_argument("--usage-source")
    parser.add_argument("--usage-kind", choices=("observed", "estimated"), default="observed")
    parser.add_argument("--reserve", type=int, default=0)
    args = parser.parse_args()
    try:
        if args.view == "map":
            data = load_work_map(args.repo, args.map)
        else:
            data = work_context(args.repo, args.map, warm_paths=args.warm_path,
                                max_files=args.max_files, max_bytes=args.max_bytes,
                                package_id=args.package, leaf_ids=args.leaf,
                                acceptance_paths=args.acceptance)
            if args.view == "budget":
                data = work_budget(data, capacity_tokens=args.capacity, capacity_source=args.capacity_source,
                                   used_tokens=args.used, usage_source=args.usage_source,
                                   usage_kind=args.usage_kind, reserve_tokens=args.reserve)
        if args.field:
            for field in args.field.split("."):
                if not isinstance(data, dict) or field not in data:
                    raise ValueError(f"Unknown selected field: {args.field}")
                data = data[field]
            print(data if isinstance(data, str) else json.dumps(data, ensure_ascii=True))
        else:
            print(json.dumps(data, indent=2, ensure_ascii=args.view != "map"))
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
