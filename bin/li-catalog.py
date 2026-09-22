#!/usr/bin/env python3
# component: skill-catalog
# implements: ADR-0028
# intent: skills/catalog/references/metadata.md
# constraints: discovery is read-only source metadata, not host execution or capability maturity
# last_intent_review: 2026-09-22
"""Generate the Markdown skill catalog, or query compact skill/agent metadata with --json."""

import argparse
from functools import lru_cache
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path, PurePosixPath
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


def register_identity(identities: set[str], kind: str, name: str, path: Path) -> None:
    identity = f"{kind}:{name}".casefold()
    if identity in identities:
        raise ValueError(f"{path}: duplicate discovery identity")
    identities.add(identity)


def generate(root: Path) -> str:
    groups: dict[str, list[tuple[str, str, str]]] = {}
    root = root.resolve()
    files = source_files(root, "skill")
    identities: set[str] = set()
    for path in files:
        fm = frontmatter(path)
        name = scalar(fm, "name", path)
        register_identity(identities, "skill", name, path)
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


def entry_aliases(root: Path, entries: list[dict], kind: str) -> None:
    members = {entry["name"]: entry for entry in entries if entry["kind"] == kind}
    canonical_names = {name.casefold() for name in members}
    owners = {}

    def add(name: str, target: str, source: str, note: Optional[str]) -> None:
        identifier(name, root / source)
        if target not in members or name.casefold() in canonical_names:
            raise ValueError(f"{source}: alias has a missing target or collides with a {kind} identity")
        if name.casefold() in owners and owners[name.casefold()] != target:
            raise ValueError(f"{source}: conflicting {kind} alias identity")
        owners[name.casefold()] = target
        aliases = members[target]["aliases"]
        aliases[:] = [alias for alias in aliases if alias["name"].casefold() != name.casefold()]
        aliases.append({"name": name, "source": source, "note": note})

    for entry in members.values():
        declared = list(entry["aliases"])
        entry["aliases"] = []
        for alias in declared:
            add(alias, entry["name"], entry["path"], None)
    if kind == "skill":
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
    for entry in members.values():
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
    kinds = ("skill", "agent") if kind == "all" else (kind,)
    for selected_kind in kinds:
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
            register_identity(identities, selected_kind, entry_name, path)
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
    for selected_kind in kinds:
        entry_aliases(root, entries, selected_kind)
    total = len(entries)
    entries = filter_entries(entries, query=query, family=family, name=name,
                             category=category, voice=voice, surface=surface)
    return {
        "schema_version": 1, "source_root": str(root), "evidence_level": "source-metadata",
        "executed": False, "total": total, "matched": len(entries), "entries": entries,
    }


def filter_entries(entries: list[dict], *, query: Optional[str] = None,
                   family: Optional[str] = None, name: Optional[str] = None,
                   category: Optional[str] = None, voice: Optional[str] = None,
                   surface: Optional[str] = None) -> list[dict]:
    for value in (query, family, name, category, voice, surface):
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError("Discovery filters must be nonempty literal strings")

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

    return sorted((entry for entry in entries if matches(entry)), key=lambda entry: entry["id"])


def selection_path(root: Path, relative: str, *, directory: bool = False) -> Path:
    if (not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative
            or any(ord(char) < 32 for char in relative)):
        raise ValueError("Selection resources must be literal source-relative paths")
    parts = relative.split("/")
    if (PurePosixPath(relative).is_absolute() or any(part in ("", ".", "..") or part.startswith(".")
                                                   for part in parts)):
        raise ValueError(f"Unsafe selection resource path: {relative!r}")
    path = source_path(root, relative)
    parent = root
    for part in parts:
        if part not in {child.name for child in parent.iterdir()}:
            raise ValueError(f"{relative}: selection resource spelling must match the source")
        parent = parent / part
    if not path.is_file() and not (directory and path.is_dir()):
        raise ValueError(f"{relative}: selection resource is not a regular file")
    return path


def selection_keys(value: object, fields: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{label}: missing or unsupported selection fields")


def selection_strings(value: object, label: str, *, nonempty: bool = False) -> list[str]:
    if (not isinstance(value, list) or (nonempty and not value)
            or any(not isinstance(item, str) or not item.strip() for item in value)
            or len(set(value)) != len(value)):
        raise ValueError(f"{label}: expected unique nonempty strings")
    return value


def selection_id(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", value):
        raise ValueError("Selection IDs must be literal kebab-case names")
    return value


def selection_order(selections: dict) -> list[str]:
    remaining, order = set(selections), []
    while remaining:
        ready = sorted(name for name in remaining if not (set(selections[name]["requires"]) - set(order)))
        if not ready:
            raise ValueError("Selection dependency cycle")
        order.extend(ready)
        remaining.difference_update(ready)
    return order


def selection_data(root: Path, entries: list[dict]) -> tuple[dict, dict, list[str]]:
    path = selection_path(root, "lib/capability-selections.json")
    data = load_text(path.read_text(encoding="utf-8-sig"))
    selection_keys(data, {"schema_version", "shared", "selections", "source_stages"}, str(path))
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Unsupported selection schema version")
    selections, stages = data["selections"], data["source_stages"]
    if not isinstance(selections, dict) or not selections or not isinstance(stages, dict):
        raise ValueError("Missing or malformed selections/source_stages")
    members = {entry["id"]: entry for entry in entries}
    if selection_id(data["shared"]) not in selections:
        raise ValueError("Shared core selection is missing")
    fields = {"source", "members", "requires", "resources", "provenance",
              "inputs", "outputs", "example", "limitations"}
    for name, record in selections.items():
        selection_id(name)
        selection_keys(record, fields, name)
        selection_path(root, record["source"])
        for field in ("members", "requires", "resources", "provenance", "inputs", "outputs", "limitations"):
            selection_strings(record[field], f"{name}.{field}",
                              nonempty=field in ("members", "inputs", "outputs", "limitations"))
        if any(member not in members for member in record["members"]):
            raise ValueError(f"{name}: unknown canonical member ID (aliases are not member IDs)")
        if any(dependency not in selections for dependency in record["requires"]):
            raise ValueError(f"{name}: unknown selection dependency")
        for relative in record["resources"]:
            selection_path(root, relative)
        selection_keys(record["example"], {"path", "heading"}, f"{name}.example")
        selection_path(root, record["example"]["path"])
        heading = text_field(record["example"], "heading", path)
        if not re.fullmatch(r"#{1,6} [^\r\n]+", heading):
            raise ValueError(f"{name}: example needs an exact Markdown heading reference")
    order = selection_order(selections)
    for member, stage in stages.items():
        if member not in members:
            raise ValueError("Unknown source-stage member")
        selection_keys(stage, {"status", "evidence"}, member)
        evidence = stage["evidence"]
        if stage["status"] == "unknown" and evidence is None:
            continue
        if stage["status"] != "staged":
            raise ValueError("Only unknown or source-evidenced staged status is supported")
        selection_keys(evidence, {"path", "description_sha256", "quote"}, member)
        description = members[member]["description"]
        quote = text_field(evidence, "quote", path)
        if (evidence["path"] != members[member]["path"] or quote not in description
                or hashlib.sha256(description.encode("utf-8")).hexdigest() != evidence["description_sha256"]):
            raise ValueError(f"{member}: missing or changed source-stage evidence")

    registry_path = selection_path(root, "install/upstream-sources.yaml")
    registry = load_text(registry_path.read_text(encoding="utf-8-sig"))
    if not isinstance(registry, dict) or not isinstance(registry.get("bundled_materials"), dict):
        raise ValueError("Missing bundled-material provenance registry")
    materials = registry["bundled_materials"]
    for name, material in materials.items():
        selection_id(name)
        if not isinstance(material, dict):
            raise ValueError(f"{name}: malformed provenance record")
        for field in ("source", "relationship", "license", "notice", "attribution", "modifications"):
            text_field(material, field, registry_path)
        if "import_commit" not in material or not (
            material["import_commit"] is None or isinstance(material["import_commit"], str)
            and re.fullmatch(r"[0-9a-f]{40}", material["import_commit"])
        ):
            raise ValueError(f"{name}: import revision must be recorded or explicitly unknown")
        for relative in selection_strings(material.get("local_paths"), f"{name}.local_paths", nonempty=True):
            selection_path(root, relative, directory=True)
        for field in ("notice", "attribution"):
            if selection_path(root, material[field]).stat().st_size == 0:
                raise ValueError(f"{name}: empty {field}")
    for name, record in selections.items():
        if any(reference not in materials for reference in record["provenance"]):
            raise ValueError(f"{name}: unknown provenance record")
        selected_paths = record["resources"] + [record["source"], record["example"]["path"]] + [
            members[member]["path"] for member in record["members"]
        ]
        for reference, material in materials.items():
            if any(path == local or path.startswith(local + "/")
                   for path in selected_paths for local in material["local_paths"]):
                if reference not in record["provenance"]:
                    raise ValueError(f"{name}: missing required provenance reference {reference}")
    return data, materials, order


def selection_metadata(root: Path, requested: Optional[list[str]] = None, *, kind: str = "all",
                       query: Optional[str] = None, family: Optional[str] = None,
                       name: Optional[str] = None, category: Optional[str] = None,
                       voice: Optional[str] = None, cli: Optional[str] = None) -> dict:
    if kind not in ("skill", "agent", "all"):
        raise ValueError("kind must be skill, agent or all")
    if requested is None and (kind != "all" or any(
        value is not None for value in (query, family, name, category, voice, cli)
    )):
        raise ValueError("Selection listing cannot be filtered; select a projection first")
    inventory = metadata(root, kind="all")
    root = Path(inventory["source_root"])
    entries = {entry["id"]: entry for entry in inventory["entries"]}
    data, materials, order = selection_data(root, inventory["entries"])
    definitions = data["selections"]
    if requested is None:
        return {
            "schema_version": 1, "source_root": str(root), "evidence_level": "source-selection-metadata",
            "executed": False, "shared": data["shared"],
            "selections": [{"id": key, **definitions[key]} for key in sorted(definitions)],
            "source_stages": [{"id": key, **data["source_stages"][key]} for key in sorted(data["source_stages"])],
        }
    selection_strings(requested, "requested selections", nonempty=True)
    for selected in requested:
        if selection_id(selected) not in definitions:
            raise ValueError(f"Unknown selection: {selected}")
    chosen = set(requested) | {data["shared"]}
    pending = list(chosen)
    while pending:
        for dependency in definitions[pending.pop()]["requires"]:
            if dependency not in chosen:
                chosen.add(dependency)
                pending.append(dependency)
    reasons: dict[str, set[str]] = {key: set() for key in chosen}
    for key in requested:
        reasons[key].add("requested")
    reasons[data["shared"]].add("shared")
    member_reasons: dict[str, set[str]] = {}
    resources: dict[str, set[str]] = {}
    provenance: dict[str, set[str]] = {}

    def resource(relative: str, reason: str) -> None:
        selection_path(root, relative)
        resources.setdefault(relative, set()).add(reason)

    for key in sorted(chosen):
        record = definitions[key]
        for dependency in record["requires"]:
            reasons[dependency].add(f"required-by:{key}")
        resource(record["source"], f"source-of:{key}")
        resource(record["example"]["path"], f"example-of:{key}")
        for relative in record["resources"]:
            resource(relative, f"resource-of:{key}")
        for member in record["members"]:
            member_reasons.setdefault(member, set()).add(f"member-of:{key}")
            resource(entries[member]["path"], f"member:{member}")
        for reference in record["provenance"]:
            provenance.setdefault(reference, set()).add(f"provenance-of:{key}")
            for field in ("notice", "attribution"):
                resource(materials[reference][field], f"{field}:{reference}")
    selected_entries = [entries[member] for member in member_reasons
                        if kind == "all" or entries[member]["kind"] == kind]
    surface = shared_reader("client_capabilities").surface_id(
        load_registry(source_path(root, "lib/cli-tiers.yaml")), cli
    ) if cli is not None else None
    filtered = filter_entries(selected_entries, query=query, family=family, name=name,
                              category=category, voice=voice, surface=surface)
    inventory.update(total=len(selected_entries), matched=len(filtered), entries=filtered)
    inventory["selection"] = {
        "requested": sorted(requested), "order": [key for key in order if key in chosen],
        "definitions": [{"id": key, **definitions[key]} for key in order if key in chosen],
        "reasons": {key: sorted(reasons[key]) for key in sorted(reasons)},
        "members": [{"id": key, "reasons": sorted(member_reasons[key])} for key in sorted(member_reasons)],
        "resources": [{"path": key, "reasons": sorted(resources[key])} for key in sorted(resources)],
        "provenance": [{
            "id": key, "reasons": sorted(provenance[key]),
            **{field: materials[key][field] for field in (
                "source", "import_commit", "relationship", "license", "notice", "attribution", "modifications",
            )},
        } for key in sorted(provenance)],
        "source_stages": [{"id": key, **data["source_stages"].get(key, {"status": "unknown", "evidence": None})}
                          for key in sorted(member_reasons)],
    }
    return inventory


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
    selection_mode = parser.add_mutually_exclusive_group()
    selection_mode.add_argument("--selection", action="append", help="literal source selection ID; repeat for a union")
    selection_mode.add_argument("--list-selections", action="store_true", help="list source selection definitions and stage evidence")
    args = parser.parse_args()
    filters = {field: getattr(args, field) for field in ("query", "family", "name", "category", "voice", "cli")}
    selected = (args.source_root is not None or args.kind is not None
                or args.selection is not None or args.list_selections) or any(
        value is not None for value in filters.values()
    )
    if not args.json and selected:
        parser.error("metadata selectors require --json; generation/check cannot be filtered or redirected")
    if args.list_selections and (args.kind is not None or any(value is not None for value in filters.values())):
        parser.error("--list-selections cannot be filtered; use --selection for a filtered projection")
    root = SOURCE_ROOT
    try:
        if args.json:
            source = args.source_root if args.source_root is not None else root
            if args.selection is not None or args.list_selections:
                result = selection_metadata(source, args.selection, kind=args.kind or "all", **filters)
            else:
                result = metadata(source, kind=args.kind or "skill", **filters)
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
