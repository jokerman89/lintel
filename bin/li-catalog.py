#!/usr/bin/env python3
# component: skill-catalog
# implements: ADR-0028
# intent: skills/catalog/references/metadata.md
# constraints: discovery is read-only source metadata, not host execution or capability maturity
# last_intent_review: 2026-09-22
"""Generate the Markdown skill catalog, or query compact skill/agent metadata with --json."""

import argparse
from functools import lru_cache
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Optional

SOURCE_ROOT = Path(__file__).resolve().parent.parent
MAX_FRONTMATTER_BYTES = 64 * 1024
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")
sys.dont_write_bytecode = True


def source_path(root: Path, relative: str) -> Path:
    path = root
    for part in Path(relative).parts:
        if part in ("..", ".") or Path(part).is_absolute():
            raise ValueError("Source paths must stay inside the selected source root")
        path = path / part
        info = path.lstat()
        if path.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"{path}: linked or reparse source paths are refused")
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"{path}: source path escapes the selected source root")
    return path


def source_files(root: Path, kind: str) -> list[Path]:
    directory = source_path(root, "skills" if kind == "skill" else "agents")
    files = sorted(directory.glob("*/SKILL.md" if kind == "skill" else "*/*.md"))
    if not files:
        raise ValueError(f"no {kind}s found")
    return [source_path(root, path.relative_to(root).as_posix()) for path in files]


def frontmatter(path: Path) -> str:
    """Stop at the closing delimiter; do not decode or return the prompt body."""
    if not path.is_file():
        raise ValueError(f"{path}: expected a regular source file")
    with path.open("rb") as handle:
        opening = handle.readline(MAX_FRONTMATTER_BYTES + 1)
        if opening.removeprefix(b"\xef\xbb\xbf").rstrip(b"\r\n") != b"---":
            raise ValueError(f"{path}: missing frontmatter")
        lines = []
        size = len(opening)
        while size <= MAX_FRONTMATTER_BYTES:
            line = handle.readline(MAX_FRONTMATTER_BYTES + 1)
            if not line:
                break
            size += len(line)
            if size > MAX_FRONTMATTER_BYTES:
                break
            if line.rstrip(b"\r\n") == b"---":
                return b"".join(lines).decode("utf-8").replace("\r\n", "\n")
            lines.append(line)
    raise ValueError(f"{path}: missing frontmatter end or header exceeds {MAX_FRONTMATTER_BYTES} bytes")


def scalar(frontmatter: str, field: str, path: Path) -> str:
    matches = re.findall(rf"^{re.escape(field)}:[ \t]*(.*?)[ \t]*$", frontmatter, re.MULTILINE)
    if not matches or not matches[0]:
        raise ValueError(f"{path}: missing {field}")
    if len(matches) != 1:
        raise ValueError(f"{path}: duplicate {field}")
    value = matches[0]
    if value[:1] in ("|", ">", "[", "{"):
        raise ValueError(f"{path}: {field} must be a one-line scalar")
    if value[:1] in ("'", '"'):
        if len(value) < 2 or value[:1] != value[-1:]:
            raise ValueError(f"{path}: unterminated {field}")
        value = value[1:-1].replace("''", "'")
    if not value.strip():
        raise ValueError(f"{path}: empty {field}")
    return value


def generate(root: Path) -> str:
    groups: dict[str, list[tuple[str, str, str]]] = {}
    root = root.resolve()
    files = source_files(root, "skill")
    for path in files:
        fm = frontmatter(path)
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


@lru_cache(maxsize=2)
def shared_reader(name: str) -> ModuleType:
    path = source_path(SOURCE_ROOT, f"lib/{name}.py")
    spec = importlib.util.spec_from_file_location(f"lintel_catalog_{name}", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Required trusted catalog helper is unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_registry(path: Path) -> dict:
    return shared_reader("client_capabilities").load_registry(path)


def load_text(text: str) -> Any:
    return shared_reader("envelope_contract").load_text(text)


def text_field(data: dict, field: str, path: Path) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path}: missing or invalid {field}")
    return value


def identifier(value: object, path: Path) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError(f"{path}: invalid discovery name or alias")
    return value


def skill_category(name: str) -> str:
    if name.startswith("plan") or name == "office-hours":
        return "plan"
    if name.startswith("qa") or name in ("investigate", "review", "code-review"):
        return "qa"
    if name.startswith("ship") or name == "review-and-ship":
        return "ship"
    if name.startswith("compliance"):
        return "compliance"
    if name == "eval":
        return "voice"
    if name in ("catalog", "help", "skill-router", "skillify", "uniformity", "welcome", "doctor"):
        return "meta"
    return "ops"


def cli_hints(data: dict, registry: dict, path: Path) -> list[dict]:
    declared = data.get("cli_support")
    if not isinstance(declared, list):
        raise ValueError(f"{path}: cli_support must be a list of declarations")
    result = []
    for hint in declared:
        if isinstance(hint, str):
            name, level = hint, None
        elif isinstance(hint, dict):
            name = text_field(hint, "cli", path)
            level = text_field(hint, "level", path)
        else:
            raise ValueError(f"{path}: invalid cli_support declaration")
        surface = shared_reader("client_capabilities").surface_id(registry, name)
        if any(item["surface"] == surface for item in result):
            raise ValueError(f"{path}: duplicate cli_support surface")
        result.append({"cli": name, "surface": surface, "level": level})
    return result


def skill_aliases(root: Path, entries: list[dict]) -> None:
    skills = {entry["name"]: entry for entry in entries if entry["kind"] == "skill"}
    skill_names = {name.casefold() for name in skills}
    owners = {}

    def add(name: str, target: str, source: str, note: Optional[str]) -> None:
        identifier(name, root / source)
        if target not in skills or name.casefold() in skill_names:
            raise ValueError(f"{source}: alias has a missing target or collides with a skill")
        if name.casefold() in owners and owners[name.casefold()] != target:
            raise ValueError(f"{source}: conflicting skill alias")
        owners[name.casefold()] = target
        aliases = skills[target]["aliases"]
        aliases[:] = [alias for alias in aliases if alias["name"].casefold() != name.casefold()]
        aliases.append({"name": name, "source": source, "note": note})

    for entry in skills.values():
        declared = list(entry["aliases"])
        entry["aliases"] = []
        for alias in declared:
            add(alias, entry["name"], entry["path"], None)
    path = source_path(root, "config/aliases.yaml")
    data = load_text(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or not isinstance(data.get("skill_aliases"), list):
        raise ValueError(f"{path}: missing or invalid skill_aliases")
    declared_names = set()
    for alias in data["skill_aliases"]:
        if not isinstance(alias, dict):
            raise ValueError(f"{path}: invalid skill alias")
        name = text_field(alias, "old", path)
        target = text_field(alias, "new", path)
        note = text_field(alias, "reason", path) if "reason" in alias else None
        if name.casefold() in declared_names:
            raise ValueError(f"{path}: duplicate skill alias")
        declared_names.add(name.casefold())
        add(name, target, "config/aliases.yaml", note)
    for entry in skills.values():
        entry["aliases"].sort(key=lambda alias: alias["name"])


def metadata(root: Path, *, kind: str = "skill", query: Optional[str] = None,
             family: Optional[str] = None, name: Optional[str] = None,
             category: Optional[str] = None, voice: Optional[str] = None,
             cli: Optional[str] = None) -> dict:
    if kind not in ("skill", "agent", "all"):
        raise ValueError("kind must be skill, agent or all")
    for value in (query, family, name, category, voice, cli):
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError("Discovery filters must be nonempty literal strings")
    if not root.is_absolute() or not root.is_dir():
        raise ValueError("Select an existing absolute trusted source root")
    if root.is_symlink() or getattr(root.lstat(), "st_file_attributes", 0) & 0x400:
        raise ValueError("Linked or reparse source root is refused")
    root = root.resolve()
    registry = load_registry(source_path(root, "lib/cli-tiers.yaml"))
    surface = shared_reader("client_capabilities").surface_id(registry, cli) if cli else None
    entries = []
    identities = set()
    for selected_kind in (("skill", "agent") if kind == "all" else (kind,)):
        for path in source_files(root, selected_kind):
            raw = frontmatter(path)
            try:
                data = load_text(raw)
            except ValueError as error:
                raise ValueError(f"{path}: {error}") from error
            if not isinstance(data, dict):
                raise ValueError(f"{path}: frontmatter must be a mapping")
            entry_name = identifier(text_field(data, "name", path), path)
            entry_id = selected_kind + ":" + entry_name
            if entry_id.casefold() in identities:
                raise ValueError(f"{path}: duplicate discovery identity")
            identities.add(entry_id.casefold())
            aliases = data.get("deprecated_aliases", [])
            if (not isinstance(aliases, list) or any(not isinstance(alias, str) for alias in aliases)
                    or len(set(aliases)) != len(aliases)):
                raise ValueError(f"{path}: invalid deprecated_aliases")
            for alias in aliases:
                identifier(alias, path)
            if len({alias.casefold() for alias in aliases}) != len(aliases):
                raise ValueError(f"{path}: duplicate deprecated alias identity")
            entry_category = (skill_category(entry_name) if selected_kind == "skill"
                              else text_field(data, "category", path))
            entries.append({
                "id": entry_id, "kind": selected_kind, "name": entry_name,
                "path": path.relative_to(root).as_posix(),
                "description": text_field(data, "description", path),
                "layer": text_field(data, "layer", path) if selected_kind == "skill" else None,
                "category": entry_category,
                "family": entry_name.split("-", 1)[0] if selected_kind == "skill" else entry_category,
                "voice": text_field(data, "voice", path),
                "aliases": aliases,
                "cli_support": cli_hints(data, registry, path),
                "maturity": "unknown",
            })
    if kind != "agent":
        skill_aliases(root, entries)
    for entry in entries:
        if entry["kind"] == "agent":
            entry["aliases"] = [{"name": alias, "source": entry["path"], "note": None}
                                for alias in entry["aliases"]]
    total = len(entries)

    def matches(entry: dict) -> bool:
        names = [entry["name"], *(alias["name"] for alias in entry["aliases"])]
        searchable = names + [entry["description"], entry["category"], entry["family"]]
        families = names if entry["kind"] == "skill" else [entry["family"]]
        return (
            (query is None or any(query.casefold() in value.casefold() for value in searchable))
            and (family is None or any(value.casefold().startswith(family.casefold()) for value in families))
            and (name is None or name.casefold() in [value.casefold() for value in names])
            and (category is None or entry["category"].casefold() == category.casefold())
            and (voice is None or entry["voice"].casefold() == voice.casefold())
            and (surface is None or any(hint["surface"] == surface for hint in entry["cli_support"]))
        )

    entries = sorted((entry for entry in entries if matches(entry)), key=lambda entry: entry["id"])
    return {
        "schema_version": 1, "source_root": str(root), "evidence_level": "source-metadata",
        "executed": False, "total": total, "matched": len(entries), "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fail if the committed catalog has drifted")
    mode.add_argument("--json", action="store_true", help="print compact metadata only; never write or activate")
    parser.add_argument("--source-root", type=Path, help="absolute metadata data source; helpers remain bound to this script")
    parser.add_argument("--kind", choices=("skill", "agent", "all"), help="metadata inventory (default: skill)")
    parser.add_argument("--query", "--search", help="literal case-insensitive metadata substring")
    parser.add_argument("--family", help="literal name/alias prefix, or agent category prefix")
    parser.add_argument("--name", help="exact name or alias (case-insensitive)")
    parser.add_argument("--category", help="exact display category; not a capability package")
    parser.add_argument("--voice", help="exact declared voice")
    parser.add_argument("--cli", help="declared surface hint; registry aliases do not imply live support")
    args = parser.parse_args()
    filters = {field: getattr(args, field) for field in ("query", "family", "name", "category", "voice", "cli")}
    selected = args.source_root is not None or args.kind is not None or any(
        value is not None for value in filters.values()
    )
    if not args.json and selected:
        parser.error("metadata selectors require --json; generation/check cannot be filtered or redirected")
    root = SOURCE_ROOT
    try:
        if args.json:
            result = metadata(args.source_root if args.source_root is not None else root,
                              kind=args.kind or "skill", **filters)
            sys.stdout.reconfigure(newline="\n")
            print(json.dumps(result, ensure_ascii=True, separators=(",", ":"), allow_nan=False))
            return 0
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
    except (OSError, ValueError, ImportError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
