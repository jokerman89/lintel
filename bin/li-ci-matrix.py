#!/usr/bin/env python3
# component: ci-matrix-planner
# implements: ADR-0037, ADR-0032
# intent: .claude/decisions/0037-pr-ci-tiering.md
# constraints: stdlib only; read-only git; any doubt selects the full matrix; never skips a test on Ubuntu
# last_intent_review: 2026-09-25
"""Choose the operating systems for the CI suite matrix (ADR-0037).

Every run tests every suite part on Ubuntu. macOS and Windows are added for a push, a manual
dispatch, a pull request labelled ``ci:full-matrix``, a pull request whose diff touches a
platform-sensitive path, and whenever the diff cannot be computed. The printed decision lists
the paths that caused it. Exit 0 whenever a decision was made; 2 for invalid arguments.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import html
import json
from pathlib import PurePosixPath
import subprocess
import sys
from typing import Callable, Optional, Sequence, Tuple, Union

sys.dont_write_bytecode = True

FULL_LABEL = "ci:full-matrix"
UBUNTU = "ubuntu-latest"
ALL_OS = (UBUNTU, "macos-latest", "windows-latest")

# The seven suite parts of ADR-0032, with their scope, shard and timeout in minutes.
PARTS = (
    ("unit-1", "unit", "1/2", 180),
    ("unit-2", "unit", "2/2", 180),
    ("integration-1", "integration", "1/4", 300),
    ("integration-2", "integration", "2/4", 300),
    ("integration-3", "integration", "3/4", 300),
    ("integration-4", "integration", "4/4", 300),
    ("other", "other", "1/1", 60),
)

# Any file below these directories can change behaviour on one operating system only.
SENSITIVE_DIRS = ("bin/", "lib/", "install/", ".github/workflows/")
# Below these directories only Markdown is documentation; everything else is sensitive.
SENSITIVE_UNLESS_MARKDOWN_DIRS = ("tests/", "hooks/", "shims/")
SENSITIVE_SUFFIXES = frozenset({
    ".sh", ".py", ".ps1", ".psm1", ".psd1", ".js", ".mjs", ".cjs", ".ts", ".json",
    ".yaml", ".yml", ".toml", ".cmd", ".bat",
})
MARKDOWN_SUFFIXES = frozenset({".md", ".markdown"})
# Only these suffixes count as documentation; an unknown suffix is treated as sensitive.
DOC_SUFFIXES = MARKDOWN_SUFFIXES | frozenset({
    ".html", ".htm", ".txt", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
})
# Added, deleted or renamed files are documentation only below these trees; nothing there is installed.
STRUCTURAL_DOC_DIRS = ("docs/", ".claude/", "presentations/")
SUMMARY_PATH_LIMIT = 50

# One changed path: its `git diff --name-status` letter and the path. A bare string means a content edit.
Change = Tuple[str, str]


class DiffError(RuntimeError):
    """The changed paths could not be determined; the caller must select the full matrix."""


@dataclass(frozen=True)
class Decision:
    tier: str  # "full" or "ubuntu"
    reason: str
    triggers: tuple[str, ...] = ()
    changed: int = 0

    @property
    def operating_systems(self) -> tuple[str, ...]:
        return ALL_OS if self.tier == "full" else (UBUNTU,)


def _normalize(path: str) -> str:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def is_platform_sensitive(path: str, status: str = "M") -> bool:
    """True when this change to a path can behave differently per operating system.

    Content edits (status M) are judged by location and extension. Adding, deleting, renaming,
    copying or retyping a file changes the installed file set, where path length, letter case
    and reserved names differ per system, so any such path outside the documentation-only
    trees is sensitive whatever its extension.
    """
    normalized = _normalize(path)
    if status[:1] != "M" and not normalized.startswith(STRUCTURAL_DOC_DIRS):
        return True
    suffix = PurePosixPath(normalized).suffix.lower()
    if normalized.startswith(SENSITIVE_DIRS):
        return True
    if normalized.startswith(SENSITIVE_UNLESS_MARKDOWN_DIRS) and suffix not in MARKDOWN_SUFFIXES:
        return True
    if not suffix or suffix in SENSITIVE_SUFFIXES:
        return True
    return suffix not in DOC_SUFFIXES


def parse_name_status(raw: bytes) -> list[Change]:
    """Every (status letter, path) in `git diff --name-status -z` output, both sides of a rename or copy."""
    fields = raw.decode("utf-8", "surrogateescape").split("\0")
    if fields and fields[-1] == "":
        fields.pop()
    changes: list[Change] = []
    index = 0
    while index < len(fields):
        status = fields[index]
        if not status or status[0] not in "ACDMRTUX":
            raise DiffError(f"unexpected diff status field {status!r}")
        count = 2 if status[0] in "RC" else 1
        names = fields[index + 1:index + 1 + count]
        if len(names) != count or not all(names):
            raise DiffError("truncated diff output")
        changes.extend((status[0], name) for name in names)
        index += 1 + count
    return changes


def _git(repo: str, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", repo, "-c", "core.quotePath=false", *args],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise DiffError(f"git {args[0]} could not run: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip().splitlines()
        raise DiffError(f"git {args[0]} exited {result.returncode}: {detail[-1] if detail else 'no output'}")
    return result.stdout


def git_changed_paths(repo: str, base: str, head: str) -> list[Change]:
    """Paths changed from the merge base of base and head to head."""
    merge_base = _git(repo, "merge-base", base, head).decode("ascii", "replace").strip()
    if not merge_base:
        raise DiffError("git merge-base returned nothing")
    return parse_name_status(_git(repo, "diff", "--no-ext-diff", "--name-status", "-z", "-M",
                                  merge_base, head, "--"))


def parse_labels(raw: Optional[str]) -> list[str]:
    if raw is None or raw.strip() in ("", "null"):
        return []
    value = json.loads(raw)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError("labels must be a JSON array of strings")
    return value


def decide(event: str, labels_json: Optional[str], base: Optional[str], head: Optional[str],
           changed_paths: Callable[[str, str], Sequence[Union[str, Change]]]) -> Decision:
    """Select the matrix tier. Only a successfully computed, documentation-only PR diff narrows it."""
    if event != "pull_request":
        return Decision("full", f"event {event or '(none)'} always runs the full matrix")
    try:
        labels = parse_labels(labels_json)
    except ValueError as exc:
        return Decision("full", f"pull request labels unreadable ({exc}); failing safe")
    if FULL_LABEL in labels:
        return Decision("full", f"pull request carries the {FULL_LABEL} label")
    if not base or not head:
        return Decision("full", "pull request base or head SHA missing; failing safe")
    try:
        changes = [("M", item) if isinstance(item, str) else (item[0], item[1])
                   for item in changed_paths(base, head)]
    except Exception as exc:  # noqa: BLE001 - any failure to compute the diff must widen, not narrow
        return Decision("full", f"diff computation failed ({exc}); failing safe")
    if not changes:
        return Decision("full", "diff is empty, so docs-only cannot be shown; failing safe")
    triggers = tuple(sorted({f"{path} ({status})" if status != "M" else path
                             for status, path in changes if is_platform_sensitive(path, status)}))
    if triggers:
        return Decision("full", f"{len(triggers)} platform-sensitive path(s) changed", triggers, len(changes))
    return Decision("ubuntu", f"all {len(changes)} changed path(s) are documentation", (), len(changes))


def matrix(decision: Decision) -> dict[str, list]:
    """The strategy.matrix object for the suite job; parts and metadata never vary."""
    return {
        "os": list(decision.operating_systems),
        "part": [part for part, _, _, _ in PARTS],
        "include": [{"part": part, "scope": scope, "shard": shard, "timeout": timeout}
                    for part, scope, shard, timeout in PARTS],
    }


def _display(path: str) -> str:
    """A printable path: undecodable bytes are escaped so reporting never crashes the planner."""
    return path.encode("utf-8", "backslashreplace").decode("utf-8")


def report_lines(decision: Decision) -> list[str]:
    lines = [f"CI matrix tier: {decision.tier} ({', '.join(decision.operating_systems)})",
             f"Reason: {_display(decision.reason)}"]
    if decision.triggers:
        lines.append("Platform-sensitive paths:")
        lines.extend(f"  {_display(path)}" for path in decision.triggers)
    return lines


def summary_markdown(decision: Decision) -> str:
    lines = ["## CI matrix plan (ADR-0037)", "",
             f"- **Tier:** {decision.tier}",
             f"- **Operating systems:** {', '.join(decision.operating_systems)}",
             f"- **Reason:** {_display(decision.reason)}"]
    if decision.changed:
        lines.append(f"- **Changed paths:** {decision.changed}")
    if decision.triggers:
        lines += ["", "Platform-sensitive paths:", ""]
        lines += [f"- <code>{html.escape(_display(path))}</code>"
                  for path in decision.triggers[:SUMMARY_PATH_LIMIT]]
        if len(decision.triggers) > SUMMARY_PATH_LIMIT:
            lines.append(f"- ... and {len(decision.triggers) - SUMMARY_PATH_LIMIT} more (see the job log)")
    if decision.tier != "full":
        lines += ["", f"Apply the `{FULL_LABEL}` label and push, or dispatch the workflow, for macOS and Windows."]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--event", required=True, help="github.event_name")
    parser.add_argument("--labels", help="JSON array of pull request label names")
    parser.add_argument("--base", help="pull request base SHA (or any revision locally)")
    parser.add_argument("--head", help="pull request head SHA (or any revision locally)")
    parser.add_argument("--repo", default=".", help="repository to diff (default: current directory)")
    parser.add_argument("--github-output", help="append matrix= and tier= to this file")
    parser.add_argument("--summary", help="append a Markdown summary to this file")
    args = parser.parse_args(argv)

    try:
        decision = decide(args.event, args.labels, args.base, args.head,
                          lambda base, head: git_changed_paths(args.repo, base, head))
    except Exception as exc:  # noqa: BLE001 - an unexpected planner defect must still test everything
        decision = Decision("full", f"planner error ({exc}); failing safe")
    print("\n".join(report_lines(decision)))
    encoded = json.dumps(matrix(decision), separators=(",", ":"))
    print(f"matrix={encoded}")
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(f"matrix={encoded}\ntier={decision.tier}\n")
    if args.summary:
        with open(args.summary, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(summary_markdown(decision))
    return 0


if __name__ == "__main__":
    sys.exit(main())
