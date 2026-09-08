#!/usr/bin/env python3
"""Generate a deterministic skill catalog from the repository's frontmatter."""

import argparse
import re
import sys
from pathlib import Path


def scalar(frontmatter: str, field: str, path: Path) -> str:
    match = re.search(rf"^{field}:[ \t]*(.*?)[ \t]*$", frontmatter, re.MULTILINE)
    if not match or not match.group(1):
        raise ValueError(f"{path}: missing {field}")
    value = match.group(1)
    if value[:1] in ("|", ">"):
        raise ValueError(f"{path}: {field} must be a one-line scalar")
    if value[:1] == value[-1:] and value[:1] in ("'", '"'):
        value = value[1:-1].replace("''", "'")
    return value


def generate(root: Path) -> str:
    groups: dict[str, list[tuple[str, str, str]]] = {}
    files = sorted((root / "skills").glob("*/SKILL.md"))
    if not files:
        raise ValueError("no skills found")
    for path in files:
        content = path.read_text(encoding="utf-8-sig")
        block = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", content, re.DOTALL)
        if not block:
            raise ValueError(f"{path}: missing frontmatter")
        fm = block.group(1)
        name = scalar(fm, "name", path)
        layer = scalar(fm, "layer", path)
        description = scalar(fm, "description", path)
        if len(description) > 120:
            description = description[:119] + "…"
        description = description.replace("|", "\\|")
        groups.setdefault(layer, []).append((name, description, path.parent.name))
    lines = [
        "# Lintel Skill Catalog", "",
        "Generated from skill frontmatter. Run `python3 bin/li-catalog.py` after changing a skill.",
        "CI checks this file for drift; edit the source SKILL.md to change a description.", "",
        "Use `/li:<name>` in a Lintel plugin, or ask Copilot to run the named Lintel skill.", "",
        f"Total skills: {len(files)}", "",
    ]
    for layer in sorted(groups, key=lambda value: (value != "foundation", value)):
        rows = groups[layer]
        lines += [f"## {layer} layer ({len(rows)} skills)", "", "| Skill | Description |", "|---|---|"]
        for name, description, folder in sorted(rows):
            lines.append(f"| [`/li:{name}`]({folder}/SKILL.md) | {description} |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed catalog has drifted")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    try:
        expected = generate(root)
        target = root / "skills" / "CATALOG.md"
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != expected:
                print("Catalog is stale. Run: python3 bin/li-catalog.py", file=sys.stderr)
                return 1
            print("Catalog matches skill frontmatter.")
        else:
            with target.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(expected)
            print(f"Generated {target}")
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
