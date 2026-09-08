#!/usr/bin/env python3
# component: work-artifact-map
# implements: ADR-0024
# intent: docs/spec-kit.md
# constraints: read-only; paths must stay inside the working repository
# last_intent_review: 2026-09-08
"""Validate a committed work map without reading runtime state or executing content."""
import argparse
import json
from pathlib import Path, PurePosixPath
import sys

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
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--map", type=Path, required=True, help="explicit committed work.json path")
    args = parser.parse_args()
    try:
        data = load_work_map(args.repo, args.map)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
