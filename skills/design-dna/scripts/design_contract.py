# component: direct-design-contract
# implements: ADR-0015, ADR-0016, ADR-0017, ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P11.md
# constraints: data-only adapters; P03 owns I/O, P05 controls/work, P07 profile identity
# last_intent_review: 2026-09-22
"""One compatibility boundary for design inputs, renderer arguments and advisory review."""
from __future__ import annotations

import argparse
from copy import deepcopy
from functools import lru_cache
import math
from pathlib import Path
import re
import stat
import sys
from typing import Any, Optional

SOURCE = Path(__file__).absolute().parents[3]
SCHEMA = "skills/design-dna/references/design-contract.schema.json"
MAX_BYTES = 2 * 1024 * 1024


def _preflight() -> None:
    for relative in (
        SCHEMA, "skills/design-dna/scripts/emit_tokens.py", "lib/context_safety.py",
        "lib/native_paths.py", "lib/profile_context.py", "lib/profile-context-schema.json",
        "lib/review_contract.py", "lib/review-schema.json", "lib/markdown_source.py",
    ):
        path = SOURCE / relative
        for part in (path, *path.parents):
            info = part.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ImportError(f"Linked trusted design resource refused: {relative}")
        if not path.is_file():
            raise ImportError(f"Required trusted design resource missing: {relative}")


_preflight()
sys.path[:0] = [str(SOURCE / "lib"), str(Path(__file__).absolute().parent)]
import context_safety as safety
from profile_context import (
    ProfileConfig, required_policy, validate_profile_reference, verify_profile_reference,
)
from review_contract import (
    canonical_json, content_digest, load_json, validate_context, validate_shape, verify_context, verify_qa,
)
from emit_tokens import parse_profile


class DesignError(ValueError):
    """Unusable design input; never a fallback to a different brand or stack."""


@lru_cache(maxsize=1)
def _schema() -> dict:
    return load_json(safety.read_owned(safety.checked_root(SOURCE), SCHEMA, MAX_BYTES)[0].decode("utf-8"))


def _shape(value: Any, definition: dict, label: str) -> None:
    """Validate only the local design vocabulary; shared definitions stay with P05."""
    if set(definition) - {
        "$ref", "anyOf", "allOf", "type", "const", "enum", "pattern", "minimum", "maximum",
        "required", "properties", "additionalProperties", "minItems", "items",
    }:
        raise DesignError("Unsupported design schema keyword")
    for rule in definition.get("allOf", []):
        _shape(value, rule, label)
    if "$ref" in definition:
        ref = definition["$ref"]
        if ref.startswith("https://lintel.dev/schemas/review-v2.json#/$defs/"):
            validate_shape(value, ref.rsplit("/", 1)[1])
        elif ref.startswith("#/$defs/"):
            _shape(value, _schema()["$defs"][ref.rsplit("/", 1)[1]], label)
        else:
            raise DesignError("Unsupported design schema reference")
        return
    if "anyOf" in definition:
        for choice in definition["anyOf"]:
            try:
                _shape(value, choice, label)
                return
            except ValueError:
                continue
        raise DesignError(f"{label}: unsupported value")
    kinds = {"object": isinstance(value, dict), "array": isinstance(value, list),
             "string": isinstance(value, str), "boolean": type(value) is bool, "null": value is None,
             "number": type(value) in (int, float) and math.isfinite(value)}
    if definition.get("type") and not kinds.get(definition["type"], False):
        raise DesignError(f"{label}: wrong type")
    if "const" in definition and (
        type(value) is not type(definition["const"]) or value != definition["const"]
    ):
        raise DesignError(f"{label}: unsupported version or discriminator")
    if "enum" in definition and value not in definition["enum"]:
        raise DesignError(f"{label}: unknown choice")
    if isinstance(value, str) and "pattern" in definition and not re.fullmatch(definition["pattern"], value):
        raise DesignError(f"{label}: malformed value")
    if type(value) in (int, float) and not (
        definition.get("minimum", -math.inf) <= value <= definition.get("maximum", math.inf)
    ):
        raise DesignError(f"{label}: outside bounds")
    if isinstance(value, dict):
        properties = definition.get("properties", {})
        additional = definition.get("additionalProperties", True)
        if set(definition.get("required", [])) - value.keys() or (
            additional is False and value.keys() - properties.keys()
        ):
            raise DesignError(f"{label}: missing or unexpected fields")
        for key, item in value.items():
            rule = properties.get(key, additional if isinstance(additional, dict) else {})
            _shape(item, rule, f"{label}.{key}")
    if isinstance(value, list):
        if len(value) < definition.get("minItems", 0):
            raise DesignError(f"{label}: missing items")
        for item in value:
            _shape(item, definition.get("items", {}), label)


def _validate(value: Any, name: str) -> None:
    if len(canonical_json(value).encode("utf-8")) > MAX_BYTES:
        raise DesignError("Design input exceeds byte bound")
    _shape(value, _schema()["$defs"][name], name)


def _motion(motion: dict, interaction: Optional[dict] = None) -> None:
    mode = motion.get("mode")
    if mode in ("none", "css") and motion["libraries"]:
        raise DesignError("None/CSS motion cannot select a JavaScript motion library")
    if mode == "none" and (motion["key_animations"] or (interaction is not None and (
        interaction["scroll_smoothing"] or interaction["page_transitions"] != "none"
    ))):
        raise DesignError("No-motion choice contradicts interactions or animations")
    if mode == "css" and (
        (interaction is not None and interaction["scroll_smoothing"])
        or any(animation.get("library") != "css" for animation in motion["key_animations"])
    ):
        raise DesignError("CSS motion cannot require JavaScript scrolling or animation")
    if mode == "library" and not motion["libraries"]:
        raise DesignError("Library motion needs an explicit selected library")


def _shader(shader: Optional[dict]) -> None:
    if shader:
        if shader["visual_thesis"] == "none":
            if shader["library"] is not None:
                raise DesignError("No-shader choice cannot select a GPU library")
        else:
            budget = shader.get("perf_budget")
            if not shader["library"] or not isinstance(budget, dict) \
                    or budget.get("respect_prefers_reduced_motion") is not True or not all(
                        isinstance(budget.get(key), str) and budget[key].strip()
                        for key in ("fallback_strategy_low_end", "fallback_strategy_no_webgl")
                    ):
                raise DesignError("Shader needs a library and explicit fallback/reduced-motion budget")


def _choices(design: dict, binding: Optional[dict]) -> None:
    motion, shader = design["motion"], design["shader"]
    _motion(motion, design["interaction_signature"])
    _shader(shader)
    roles = [font["role"] for font in design["typography"]["font_stacks"]]
    if len(roles) != len(set(roles)):
        raise DesignError("Duplicate typography role")
    if binding is None:
        return
    if not {"heading", "body"} <= set(roles):
        raise DesignError("Resolved design needs explicit heading and body font roles")
    if not motion.get("mode") or not design.get("palette", {}).get("tokens"):
        raise DesignError("Resolved design needs explicit motion mode and palette tokens")
    renderer = _schema()["x-renderers"][design["target_format"]]
    if binding["project"]["stack"] not in renderer["stacks"]:
        raise DesignError("Target and selected project stack are incompatible; no automatic replacement")
    if not binding["retrieval"]:
        raise DesignError("Resolved design needs retained design-DNA retrieval")
    names = {("font", font["family"]) for font in design["typography"]["font_stacks"]}
    libraries = motion["libraries"] + design["component_libraries"]
    if shader and shader["library"]:
        libraries += [shader["library"]]
    names.update(("library", library["name"]) for library in libraries)
    sources = [(entry["kind"], entry["name"]) for entry in binding["provenance"]]
    if len(sources) != len(set(sources)) or set(sources) != names:
        raise DesignError("Provenance must name every selected font/library exactly once")
    for entry in binding["provenance"]:
        if not entry["evidence"] or re.search(r"(?i)latest|[~^*<>]|\bx\b", entry["version"]):
            raise DesignError("Selected font/library needs exact version, source/license evidence and rationale")
        if entry["kind"] == "library" and binding["project"]["stack"] not in entry.get("stacks", []):
            raise DesignError("Library provenance must support the actual selected project stack")
    fields = [entry["field"] for entry in binding["overrides"]]
    if len(fields) != len(set(fields)):
        raise DesignError("Duplicate brief override")


def validate_spec(data: dict, kind: Optional[str] = None) -> dict:
    """Read historical shapes without inventing the bindings needed for rendering."""
    if kind in ("typography", "motion", "shader"):
        _validate(data, kind)
        if kind == "motion":
            _motion(data)
        elif kind == "shader":
            _shader(data)
        return {"kind": kind, "fragment": deepcopy(data), "renderable": False}
    kind = kind or ("pipeline" if data.get("source") == "pipeline" or "version" in data else "frontend")
    if kind not in ("frontend", "pipeline"):
        raise DesignError("Unknown design envelope")
    _validate(data, kind)
    common = data if kind == "frontend" else data.get("web_design")
    binding = data.get("binding")
    if binding is not None:
        _validate(binding, "binding")
        validate_profile_reference(binding["profile_ref"])
        hash_key = "brief_hash" if kind == "frontend" else "source_content_hash"
        if hash_key in data and data[hash_key] != binding["brief"]["sha256"]:
            raise DesignError("Envelope input hash contradicts the bound brief/content")
        if kind == "pipeline" and (data.get("source") != "pipeline" or data.get("schema_version") != 1):
            raise DesignError("Resolved pipeline needs explicit source and schema_version")
    if common is None:
        if binding is not None:
            raise DesignError("Resolved pipeline needs web_design")
        return {"kind": kind, "design": None, "binding": None, "renderable": False}
    design = {key: deepcopy(common[key]) for key in _schema()["$defs"]["design"]["properties"] if key in common}
    _validate(design, "design")
    _choices(design, binding)
    if kind == "pipeline":
        fonts = {font["role"]: font["family"] for font in design["typography"]["font_stacks"]}
        for role, family in fonts.items():
            if role in data["fonts"] and data["fonts"][role] != family:
                raise DesignError("Pipeline font projection contradicts web_design")
        tokens = design.get("palette", {}).get("tokens", {})
        for key, name in {"text_dark": "ink", "background": "paper", "primary": "accent_primary"}.items():
            if key in data["palette"] and name in tokens and data["palette"][key].lower() != tokens[name].lower():
                raise DesignError("Pipeline palette projection contradicts web_design")
        if "web" not in data["per_format"]:
            raise DesignError("Pipeline has no selected web layout mapping")
    return {"kind": kind, "design": design, "binding": deepcopy(binding),
            "renderable": binding is not None}


def profile_asset(record: dict, config: ProfileConfig) -> tuple[dict, dict]:
    """Resolve the chosen asset by name, never by scanning personal folders."""
    profile = record["profile"]
    settings = profile["values"].get("design", {})
    if not isinstance(settings, dict):
        raise DesignError("Selected design settings must be a mapping")
    selected = settings.get("profile")
    name = "anthropic-default" if selected is None else selected
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise DesignError("Invalid selected design.profile")
    candidates = []
    origin = profile["provenance"].get("design.profile")
    if origin and selected is not None:
        candidates.append(("pack", Path(origin["path"]).parent, f"profiles/{name}.yaml"))
    candidates.append(("source", SOURCE, f"skills/design-dna/profiles/{name}.yaml"))
    for index, (kind, root, relative) in enumerate(candidates):
        try:
            raw, state = safety.read_owned(safety.checked_root(root), relative, MAX_BYTES)
        except FileNotFoundError:
            if index == len(candidates) - 1:
                raise
            continue
        leaves = parse_profile(raw.decode("utf-8"))
        if leaves.get("profile.id") != name or not any(key.startswith("color.") for key in leaves):
            raise DesignError("Selected design asset has no matching identity/palette")
        return {"name": name, "origin": kind, "sha256": state["sha256"]}, leaves
    raise DesignError("Selected design asset is unavailable")


def read_document(repo: Path, path: str) -> tuple[dict, dict]:
    root = safety.checked_root(repo)
    relative = safety.selector_path(path)
    raw, state = safety.read_owned(root, relative, MAX_BYTES)
    return load_json(raw.decode("utf-8-sig")), {"path": relative, "sha256": state["sha256"]}


def _bound(repo: Path, reference: dict, expected: dict) -> bytes:
    validate_shape(reference, "evidenceFile")
    raw, state = safety.read_owned(repo, reference["path"], MAX_BYTES)
    selected = {entry["path"]: entry["worktree"] for entry in expected["snapshot"]["entries"]}
    current = selected.get(reference["path"])
    if not current or current["kind"] != "file" or current["sha256"] != state["sha256"] \
            or reference["sha256"] != state["sha256"]:
        raise DesignError(f"Design input is not bound to the selected current content: {reference['path']}")
    return raw


def _project(binding: dict, repo: Path, expected: dict) -> None:
    project = binding["project"]
    if project["existing"] and not project["manifests"]:
        raise DesignError("Existing project needs selected manifest evidence")
    if safety.native_io_path(safety.safe_path(repo, "package.json")).exists() and not any(
        ref["path"] == "package.json" for ref in project["manifests"]
    ):
        raise DesignError("The existing project package.json must be selected, not bypassed as a new project")
    stacks = set()
    manifest_present = False
    for reference in project["manifests"]:
        raw = _bound(repo, reference, expected)
        if Path(reference["path"]).name.casefold() != "package.json":
            continue
        manifest_present = True
        package = load_json(raw.decode("utf-8"))
        if any(not isinstance(package.get(key, {}), dict) for key in ("dependencies", "devDependencies")):
            raise DesignError("Project dependency fields must be mappings")
        dependencies = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
        if "next" in dependencies:
            stacks.add("next-app")
        elif "react" in dependencies and "vite" in dependencies:
            stacks.add("vite-react")
        if "@sveltejs/kit" in dependencies:
            stacks.add("svelte-kit")
        if "vue" in dependencies:
            stacks.add("vue")
    if (stacks and stacks != {project["stack"]}) or (
        (manifest_present or project["existing"]) and not stacks and project["stack"] != "html"
    ):
        raise DesignError("Selected project technology contradicts or lacks manifest evidence")


def load_design(repo: Path, path: str, *, expected: dict, profile_config: ProfileConfig) -> dict:
    """Verify existing context and exact selected inputs; never bootstrap/rebind or render."""
    root = safety.checked_root(repo)
    if profile_config.repo != root or profile_config.source != SOURCE.resolve():
        raise DesignError("Profile configuration must name this target and trusted source")
    validate_context(expected)
    verify_context(root, expected)
    data, reference = read_document(root, path)
    _bound(root, reference, expected)
    result = validate_spec(data)
    if not result["renderable"]:
        raise DesignError("Legacy design is readable but unresolved; bind explicit current inputs before rendering")
    binding, design = result["binding"], result["design"]
    if binding["profile_ref"] != expected["profile"]:
        raise DesignError("Design and caller-selected profile references differ")
    record = verify_profile_reference(binding["profile_ref"], profile_config)
    if required_policy(record) != expected["required_policy"]:
        raise DesignError("Design policy differs from the external P05 context")
    asset, leaves = profile_asset(record, profile_config)
    if binding["profile_asset"] != asset:
        raise DesignError("Selected design profile asset identity changed")
    for label in (design["palette"].get("source_profile"), design.get("design_dna", {}).get("profile")):
        if label is not None and label != asset["name"]:
            raise DesignError("Design profile label contradicts the verified selected asset")
    _bound(root, binding["brief"], expected)
    for reference_input in binding["retrieval"]:
        _bound(root, reference_input, expected)
    for source in binding["provenance"]:
        for reference_input in source["evidence"]:
            _bound(root, reference_input, expected)
    overrides = {item["field"]: item for item in binding["overrides"]}
    for item in overrides.values():
        if item["evidence"] != binding["brief"]:
            raise DesignError("Aesthetic override needs the selected brief as evidence")
    for key, value in design["palette"]["tokens"].items():
        pinned = leaves.get(f"color.{key}")
        if pinned is not None and value.lower() != pinned.lower() and f"palette.{key}" not in overrides:
            raise DesignError(f"Palette differs from pinned profile without a brief override: {key}")
    for font in design["typography"]["font_stacks"]:
        role = "display" if font["role"] == "heading" else font["role"]
        pinned = leaves.get(f"type.{role}.family")
        if pinned and font["family"] != pinned and f"typography.{font['role']}" not in overrides:
            raise DesignError(f"Typography differs from pinned profile without a brief override: {font['role']}")
    _project(binding, root, expected)
    verify_profile_reference(binding["profile_ref"], profile_config)
    verify_context(root, expected)
    return {**result, "spec": reference, "profile_ref": binding["profile_ref"],
            "context_digest": content_digest(expected), "verification": "current_inputs",
            "release_clearance": False}


def renderer_args(loaded: dict, *, out: str) -> dict:
    """Return literal skill arguments only; the host still owns invocation/permission."""
    if loaded.get("verification") != "current_inputs" or not loaded.get("renderable"):
        raise DesignError("Renderer mapping requires freshly checked design inputs")
    design, binding = loaded["design"], loaded["binding"]
    _choices(design, binding)
    filename = {"frontend": "frontend-design-spec.json", "pipeline": "design-spec.json"}.get(loaded["kind"])
    if filename is None or Path(loaded["spec"]["path"]).name != filename:
        raise DesignError("Renderer mapping requires the canonical filename for the selected envelope")
    output = safety.selector_path(out)
    run = str(Path(loaded["spec"]["path"]).parent).replace("\\", "/")
    renderer = _schema()["x-renderers"][design["target_format"]]
    selector = "--from-frontend-design" if loaded["kind"] == "frontend" else "--from-pipeline"
    if loaded["kind"] == "pipeline" and design["target_format"] == "app":
        raise DesignError("Pipeline-to-app is not an existing entry point; use an explicit frontend envelope")
    argv = [selector, run, renderer["option"], renderer.get("value", binding["project"]["stack"]),
            "--out", output]
    if binding["customer_share"]:
        argv.append("--customer-share")
    return {"skill": renderer["skill"], "args": argv}


def normalize_dimensions(dimensions: list[str]) -> list[str]:
    aliases = _schema()["x-dimensions"]
    result = []
    if not isinstance(dimensions, list) or not dimensions:
        raise DesignError("Select at least one review dimension")
    for name in dimensions:
        if not isinstance(name, str):
            raise DesignError("Review dimension names must be strings")
        canonical = aliases.get(name, name)
        if canonical not in aliases.values() or canonical in result:
            raise DesignError("Unknown or duplicate review dimension")
        result.append(canonical)
    return result


def validate_review(data: dict, dimensions: Optional[list[str]] = None) -> dict:
    """Advisory scoring uses one key vocabulary and cannot clear mandatory controls."""
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1 \
            or not isinstance(data.get("dimensions"), dict):
        raise DesignError("Invalid design review")
    selected = normalize_dimensions(
        list(_schema()["x-dimensions"].values()) if dimensions is None else dimensions
    )
    names = normalize_dimensions(list(data["dimensions"]))
    if set(names) != set(selected):
        raise DesignError("Review does not cover the exact selected dimensions")
    normalized = {}
    for old, name in zip(data["dimensions"], names):
        item = deepcopy(data["dimensions"][old])
        _validate(item, "dimension")
        score = item["score"]
        item["verdict"] = ("unverified" if score is None else "green" if score >= 80
                           else "yellow" if score >= 60 else "red")
        normalized[name] = item
    verdicts = {item["verdict"] for item in normalized.values()}
    verdict = next((value for value in ("red", "unverified", "yellow") if value in verdicts), "green")
    return {**deepcopy(data), "dimensions": normalized, "overall_verdict": verdict,
            "release_clearance": False}


def review_result(data: dict, *, repo: Path, expected: dict, qa: dict,
                  design_path: str, profile_config: ProfileConfig,
                  dimensions: Optional[list[str]] = None) -> dict:
    load_design(repo, design_path, expected=expected, profile_config=profile_config)
    advisory = validate_review(data, dimensions)
    controls = verify_qa(repo, qa, expected=expected)
    return {"advisory": advisory, "controls": controls, "blocked": controls["blocked"],
            "release_clearance": False, "review": "not_evaluated"}


class _Once(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        seen = getattr(namespace, "_seen", set())
        if self.dest in seen:
            parser.error(f"duplicate option: {option_string}")
        setattr(namespace, "_seen", seen | {self.dest})
        setattr(namespace, self.dest, values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "renderer-args", "review"):
        command = commands.add_parser(name, allow_abbrev=False)
        command.add_argument("--repo", type=Path, required=True, action=_Once)
        command.add_argument("--file", required=True, action=_Once)
        if name == "validate":
            command.add_argument("--kind", choices=("frontend", "pipeline", "typography", "motion", "shader"),
                                 action=_Once)
        else:
            command.add_argument("--expected", required=True, action=_Once)
        if name != "validate":
            for flag in ("home", "packs", "pointer"):
                command.add_argument(f"--profile-{flag}", type=Path, required=True, action=_Once)
            command.add_argument("--profile-context-file", type=Path, action=_Once)
        if name == "renderer-args":
            command.add_argument("--out", required=True, action=_Once)
        if name == "review":
            command.add_argument("--design", required=True, action=_Once)
            command.add_argument("--qa", required=True, action=_Once)
            command.add_argument("--dimensions", action=_Once)
    args = parser.parse_args()
    try:
        data, ref = read_document(args.repo, args.file)
        if args.command == "validate":
            result = validate_spec(data, args.kind)
            result.update(operation="validate", verification="not_performed", release_clearance=False)
        else:
            expected, _ = read_document(args.repo, args.expected)
            config = ProfileConfig(SOURCE, args.repo, args.profile_home, args.profile_packs,
                                   args.profile_pointer, context_file=args.profile_context_file)
            if args.command == "renderer-args":
                loaded = load_design(args.repo, args.file, expected=expected, profile_config=config)
                result = {**renderer_args(loaded, out=args.out), "verification": "current_inputs",
                          "executed": False, "release_clearance": False}
            else:
                _bound(safety.checked_root(args.repo), ref, expected)
                qa, _ = read_document(args.repo, args.qa)
                result = review_result(data, repo=args.repo, expected=expected, qa=qa,
                                       design_path=args.design, profile_config=config,
                                       dimensions=args.dimensions.split(",") if args.dimensions else None)
        print(canonical_json(result))
        return 3 if result.get("blocked") else 0
    except (ValueError, OSError, UnicodeError) as error:
        print(f"ERROR [lintel/design]: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
