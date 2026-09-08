#!/usr/bin/env python3
# component: session-protocol-sync
# implements: ADR-0025
# intent: docs/architecture.md
# constraints: none; only fixed repository entry files are updated
# last_intent_review: 2026-09-08
"""Synchronize one portable protocol into self-contained agent entry files."""

import argparse
from pathlib import Path
import sys

START = "<!-- LINTEL:SESSION-PROTOCOL:START -->"
END = "<!-- LINTEL:SESSION-PROTOCOL:END -->"
SOURCE = "scaffolding/01-foundation/SESSION-PROTOCOL.md"
TARGETS = (
    "AGENTS.md",
    "CLAUDE.md",
    "scaffolding/01-foundation/AGENTS.md.template",
    "scaffolding/01-foundation/CLAUDE.md.template",
)


def canonical_block(root: Path) -> str:
    """Read the canonical payload once, independent of user-global files."""
    payload = (root / SOURCE).read_text(encoding="utf-8-sig").strip()
    if not payload or START in payload or END in payload:
        raise ValueError("Canonical protocol must be nonempty and contain no block markers")
    return f"{START}\n{payload}\n{END}"


def replace_block(content: str, block: str) -> str:
    """Preserve project prose; reject malformed or duplicate ownership markers."""
    starts, ends = content.count(START), content.count(END)
    if starts == ends == 0:
        return content.rstrip() + "\n\n" + block + "\n"
    if starts != 1 or ends != 1 or content.index(END) < content.index(START):
        raise ValueError("Expected exactly one ordered pair of session-protocol markers")
    left = content.index(START)
    right = content.index(END) + len(END)
    return content[:left] + block + content[right:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("sync", "check"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        block = canonical_block(root)
        planned = []
        for relative in TARGETS:
            path = root / relative
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                raise ValueError(f"Unsafe protocol target: {relative}")
            content = path.read_text(encoding="utf-8-sig")
            expected = replace_block(content, block)
            if content != expected:
                planned.append((relative, path, expected))
        if args.command == "check":
            for relative, _, _ in planned:
                print(f"DRIFT: {relative}")
            if planned:
                return 1
            print(f"PASS: session protocol synchronized in {len(TARGETS)} entry files")
            return 0
        for relative, path, expected in planned:
            with path.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(expected)
            print(f"UPDATED: {relative}")
        print(f"PASS: session protocol synchronized in {len(TARGETS)} entry files")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
