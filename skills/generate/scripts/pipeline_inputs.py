#!/usr/bin/env python3
# component: document-pipeline-inputs
# implements: ADR-0028, ADR-0029, ADR-0031
# intent: .claude/plans/universal-implementation/packages/P12.md
# constraints: read-only existing inputs; P03/P05/P07/P08/P09/P11 remain their own authorities
# last_intent_review: 2026-09-23
"""Admit existing document pipeline inputs, without rendering or granting acceptance."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path, PurePosixPath
import re
import runpy
import stat
import sys
from typing import Any, Optional, Sequence

SOURCE = Path(__file__).absolute().parents[3]
MAX_BYTES = 2 * 1024 * 1024
FIELDS = frozenset(("Title", "Subtitle", "Body", "Bullets", "Data-viz"))
FORMATS = frozenset(("word", "ppt", "pdf", "xlsx"))


def _preflight() -> None:
    for relative in (
        "bin/li-work-artifacts.py", "lib/context_safety.py", "lib/native_paths.py",
        "lib/markdown_source.py", "lib/swarm_contract.py", "lib/swarm_snapshot.py", "lib/swarm-schema.json",
        "lib/review_contract.py", "lib/review-schema.json",
        "lib/profile_context.py", "lib/profile-context-schema.json",
        "lib/domain_result.py", "lib/domain-result-schema.json",
        "skills/design-dna/scripts/design_contract.py", "skills/design-dna/scripts/emit_tokens.py",
        "skills/design-dna/references/design-contract.schema.json",
    ):
        path = SOURCE / relative
        for part in (path, *path.parents):
            info = part.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ImportError(f"Linked trusted pipeline resource refused: {relative}")
        if not path.is_file():
            raise ImportError(f"Missing trusted pipeline resource: {relative}")


sys.dont_write_bytecode = True
_preflight()
sys.path.insert(0, str(SOURCE / "lib"))
import context_safety as safety  # noqa: E402
import domain_result  # noqa: E402
from markdown_source import MarkdownBoundaries, classify_markdown  # noqa: E402
from profile_context import ProfileConfig, parse_manifest, required_policy, verify_profile_reference  # noqa: E402
from review_contract import canonical_json, load_json, validate_context, verify_context  # noqa: E402

_design_spec = importlib.util.spec_from_file_location(
    "lintel_pipeline_design", SOURCE / "skills/design-dna/scripts/design_contract.py",
)
if _design_spec is None or _design_spec.loader is None:
    raise ImportError("Cannot load the trusted design compatibility helper")
design_contract = importlib.util.module_from_spec(_design_spec)
sys.modules[_design_spec.name] = design_contract
_design_spec.loader.exec_module(design_contract)
_work_context = runpy.run_path(str(SOURCE / "bin/li-work-artifacts.py"))["work_context"]


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or any(ord(char) < 32 for char in value):
        raise ValueError(f"{label} must be a nonempty single-line string")
    return value


def _bound(root: Path, path: str, expected: dict[str, Any]) -> tuple[bytes, dict[str, str]]:
    relative = safety.selector_path(path)
    raw, state = safety.read_owned(root, relative, MAX_BYTES)
    selected = {entry["path"]: entry["worktree"] for entry in expected["snapshot"]["entries"]}
    current = selected.get(relative)
    if not current or current["kind"] != "file" or current["sha256"] != state["sha256"]:
        raise ValueError(f"Input is not selected with its current bytes: {relative}")
    return raw, {"path": relative, "sha256": state["sha256"]}


def _markdown(raw: bytes, label: str) -> tuple[MarkdownBoundaries, dict[str, Any], int]:
    source = classify_markdown(raw.decode("utf-8"))
    lines = source.lines
    if not lines or source.original[lines[0].start:lines[0].end].lstrip("\ufeff") != "---":
        raise ValueError(f"{label} needs its original frontmatter")
    for line in lines[1:]:
        if source.original[line.start:line.end] == "---":
            metadata = parse_manifest(source.original[lines[0].next_start:line.start])
            return source, metadata, line.next_start
    raise ValueError(f"{label} has unclosed frontmatter")


def _sections(source: MarkdownBoundaries, start: int, *, content: bool = False) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = None
    heading = re.compile(r"##[ \t]+(\u00a7([1-9][0-9]*))(?=[ \t])")
    field = re.compile(r"\*\*(Title|Subtitle|Body|Bullets|Data-viz):\*\*(?=[ \t]|$)")
    for line in source.lines:
        if line.start < start or line.kind != "prose" or line.container_ids or line.residual_indent > 3:
            continue
        body = source.original[line.content_start:line.end]
        match = heading.match(body) or (field.match(body) if content else None)
        if match is None or any(
            region.span.start < line.content_start + match.end() and line.content_start < region.span.end
            for region in source.regions
        ):
            continue
        if body.startswith("##"):
            current = match[1]
            if current in sections:
                raise ValueError(f"Duplicate source section: {current}")
            anchors = re.findall(r"\{#sec-([^}]+)\}", body)
            if (content or anchors) and anchors != [match[2]]:
                raise ValueError(f"Source section anchor disagrees with {current}")
            sections[current] = []
        elif current is None:
            raise ValueError("Source field appears before a canonical section")
        elif match[1] in sections[current]:
            raise ValueError(f"Duplicate source field {match[1]} in section {current}")
        else:
            sections[current].append(match[1])
    if not sections or (content and any(not fields for fields in sections.values())):
        raise ValueError("Canonical source sections/fields are missing")
    return sections


def _projection(design: dict[str, Any], format_name: str, sections: dict[str, list[str]]) -> None:
    key, destination, hook = {
        "word": ("sections", "slot", "WordTechnicalEditor"),
        "ppt": ("layouts", "placeholder", "PPTNarrativeArchitect"),
    }[format_name]
    projection = design["per_format"].get(format_name)
    if not isinstance(projection, dict) or not isinstance(projection.get(key), list) or not projection[key]:
        raise ValueError(f"Missing {format_name} {key}")
    covered = set()
    for row in projection[key]:
        if not isinstance(row, dict) or not isinstance(row.get("section_ref"), str) or row["section_ref"] not in sections:
            raise ValueError(f"Unknown {format_name} source section reference")
        section = row["section_ref"]
        covered.add(section)
        if row.get("design_pass_hook") != hook:
            raise ValueError(f"{format_name} design_pass_hook must retain {hook}; it is not executed here")
        if format_name == "word":
            if type(row.get("heading_level")) is not int or not 1 <= row["heading_level"] <= 6:
                raise ValueError("Word heading_level must be an integer from 1 to 6")
            slots = {"heading", "body"}
        else:
            _text(row.get("layout_name"), "PPT layout_name")
            if type(row.get("layout_index")) is not int or row["layout_index"] < 0:
                raise ValueError("PPT layout_index must be a nonnegative integer")
            slots = {"title", "subtitle", "body"}
        elements = row.get("elements")
        if not isinstance(elements, list) or not elements:
            raise ValueError(f"{format_name} {section} needs source slot references")
        used = set()
        for element in elements:
            if not isinstance(element, dict):
                raise ValueError("A source slot reference must be an object")
            name, source_field = element.get(destination), element.get("content_field")
            if not isinstance(name, str) or name not in slots or name in used:
                raise ValueError(f"Unknown or duplicate {format_name} {destination}: {name}")
            if not isinstance(source_field, str) or source_field not in FIELDS or source_field not in sections[section]:
                raise ValueError(f"Unknown or absent source field in {section}: {source_field}")
            used.add(name)
    if covered != set(sections):
        raise ValueError(f"{format_name} mappings omit source sections: {sorted(set(sections) - covered)}")


def _upstream(root: Path, request_path: str, upstream_expected: dict[str, Any],
              profile_config: ProfileConfig, expected: dict[str, Any]) -> dict[str, Any]:
    raw, reference = _bound(root, request_path, expected)
    request = load_json(raw.decode("utf-8-sig"))
    outcome = domain_result.verify_result(
        root, reference["path"], expected=upstream_expected, profile_config=profile_config,
    )
    if not outcome["ok"] or outcome["verification"] != "current_inputs":
        raise ValueError(f"Upstream domain inputs remain blocked: {outcome['problems']}")
    for domain in request["domains"]:
        for checkpoint in domain["checkpoints"]:
            _bound(root, checkpoint["start"]["path"], expected)
            result_raw, _ = _bound(root, checkpoint["result"]["path"], expected)
            result = load_json(result_raw.decode("utf-8-sig"))
            for item in result["artifacts"] + result["evidence"]:
                _, current = _bound(root, item["path"], expected)
                if current != item:
                    raise ValueError(f"Upstream artifact/evidence changed: {item['path']}")
    return outcome


def load_pipeline_inputs(
    repo: Path, run_dir: str, *, expected: dict[str, Any], profile_config: ProfileConfig,
    package_id: str, leaf_ids: Sequence[str], formats: Sequence[str],
    selected_inputs: Sequence[str] = (), linked_authority: Optional[str] = None,
    upstream_request: Optional[str] = None, upstream_expected: Optional[dict[str, Any]] = None,
    upstream_profile: Optional[ProfileConfig] = None,
) -> dict[str, Any]:
    """Return full current source inputs and diagnostics, not a new persisted envelope."""
    root = safety.checked_root(repo)
    if profile_config.repo != root or profile_config.source != SOURCE.resolve():
        raise ValueError("Profile configuration must name this target and trusted source")
    if isinstance(formats, str) or not formats or any(not isinstance(value, str) for value in formats) \
            or len(set(formats)) != len(formats) or not set(formats) <= FORMATS:
        raise ValueError("Select unique document formats: word, ppt, pdf, xlsx")
    if isinstance(leaf_ids, str) or not leaf_ids or any(not isinstance(value, str) for value in leaf_ids) \
            or len(set(leaf_ids)) != len(leaf_ids):
        raise ValueError("Select unique original work leaf IDs")
    if isinstance(selected_inputs, str) or any(not isinstance(value, str) for value in selected_inputs):
        raise ValueError("Selected inputs must be a sequence of literal relative paths")
    validate_context(expected)
    verify_context(root, expected)
    profile = verify_profile_reference(expected["profile"], profile_config)
    if required_policy(profile) != expected["required_policy"]:
        raise ValueError("Current required policy differs from the external P05 context")
    original = expected["work"]
    if not original["work_map"] or package_id != original["package_id"] or list(leaf_ids) != original["leaf_ids"]:
        raise ValueError("Caller must retain the explicit original work package and leaves")
    work = _work_context(root, Path(original["work_map"]), package_id=package_id,
                         leaf_ids=leaf_ids, acceptance_paths=original["acceptance_paths"])
    if work["status"] not in ("APPROVED", "COMPLETE") or work["binding"] != original:
        raise ValueError("Original work is unapproved or differs from the external P05 binding")
    package = work["packages"].get(package_id)
    if package is not None:
        if not set(leaf_ids) <= set(package["leaf_ids"]):
            raise ValueError("Selected leaves do not belong to the original package")
        membership, prerequisites = "mapped-package", package["prerequisites"]
    else:
        authority = safety.selector_path(linked_authority) if linked_authority else None
        if not authority or authority not in original["acceptance_paths"] \
                or not safety.read_owned(root, authority, MAX_BYTES)[0].strip():
            raise ValueError("Unmapped package grouping needs explicit bound linked authority")
        membership, prerequisites = "linked-authority", {}

    directory = "" if run_dir == "." else safety.selector_path(run_dir)
    if directory and not safety.native_io_path(safety.safe_path(root, directory)).is_dir():
        raise ValueError("The selected pipeline run must be an existing owned directory")
    documents: dict[str, Any] = {}
    metadata = {}
    source_sections = {}
    for name in ("brief.md", "outline.md", "content.md"):
        path = str(PurePosixPath(directory) / name)
        raw, reference = _bound(root, path, expected)
        documents[name] = {**reference, "text": raw.decode("utf-8")}
        if name != "brief.md":
            source, metadata[name], start = _markdown(raw, name)
            source_sections[name] = _sections(source, start, content=name == "content.md")
    outline, content = metadata["outline.md"], metadata["content.md"]
    for child, parent, field in (
        (outline, "brief.md", "source_brief_hash"), (content, "outline.md", "source_outline_hash"),
    ):
        if child.get(field) != documents[parent]["sha256"]:
            raise ValueError(f"Canonical sibling hash mismatch: {field}")
    for field in ("language", "target_formats"):
        if field not in content or content[field] != outline.get(field):
            raise ValueError(f"Original outline/content {field} differs")
    _text(content["language"], "Source language")
    _text(content.get("voice_tier"), "Source voice_tier")
    targets = content["target_formats"]
    if not isinstance(targets, list) or any(not isinstance(value, str) or not value.strip() for value in targets) \
            or len(set(targets)) != len(targets) or not set(formats) <= set(targets):
        raise ValueError("Requested formats must be in the original target_formats")
    sections = source_sections["content.md"]
    if list(sections) != list(source_sections["outline.md"]):
        raise ValueError("Original outline/content section IDs or order differ")
    if "ppt" in formats:
        raw, reference = _bound(root, str(PurePosixPath(directory) / "speaker-notes.md"), expected)
        source, notes, start = _markdown(raw, "speaker-notes.md")
        if notes.get("source_content_hash") != documents["content.md"]["sha256"]:
            raise ValueError("Canonical speaker-notes source_content_hash mismatch")
        if notes.get("language") != content["language"] or list(_sections(source, start)) != list(sections):
            raise ValueError("Speaker-notes language or source section IDs differ")
        documents["speaker-notes.md"] = {**reference, "text": raw.decode("utf-8")}

    design_raw, design_ref = _bound(root, str(PurePosixPath(directory) / "design-spec.json"), expected)
    design = load_json(design_raw.decode("utf-8-sig"))
    design_contract.validate_spec(design, "pipeline")
    if design.get("source_content_hash") != documents["content.md"]["sha256"]:
        raise ValueError("Canonical design source_content_hash mismatch")
    mixed = "web" in design["per_format"] or "web_design" in design or "binding" in design
    if mixed:
        design_contract.load_design(root, design_ref["path"], expected=expected, profile_config=profile_config)
    inputs = {}
    for path in selected_inputs:
        _, reference = _bound(root, path, expected)
        inputs[reference["path"]] = reference
    for format_name in formats:
        if format_name in ("word", "ppt"):
            _projection(design, format_name, sections)
            template = design["per_format"][format_name].get("template_path")
            if template is not None:
                _, reference = _bound(root, _text(template, "Template path"), expected)
                inputs[reference["path"]] = reference
    logo = design.get("logo")
    if logo is not None:
        if not isinstance(logo, dict):
            raise ValueError("Logo declaration must retain its path")
        _, reference = _bound(root, _text(logo.get("path"), "Logo path"), expected)
        inputs[reference["path"]] = reference

    supplied = [value is not None for value in (upstream_request, upstream_expected, upstream_profile)]
    if any(supplied) and not all(supplied):
        raise ValueError("Upstream data requires its own request, final context and explicit profile configuration")
    upstream = None
    if upstream_request is not None and upstream_expected is not None and upstream_profile is not None:
        upstream = _upstream(root, upstream_request, upstream_expected, upstream_profile, expected)
    verify_profile_reference(expected["profile"], profile_config)
    verify_context(root, expected)
    return {
        "operation": "document-pipeline-inputs", "verification": "current_inputs",
        "documents": documents, "design": design, "design_file": {**design_ref, "text": design_raw.decode("utf-8")},
        "section_fields": sections, "selected_inputs": list(inputs.values()),
        "work": original, "profile_ref": expected["profile"], "required_policy": expected["required_policy"],
        "membership": membership, "prerequisites": prerequisites, "task_evidence": work["task_evidence"],
        "design_validation": "mixed-web-and-document-projections" if mixed else "document-projections",
        "upstream": upstream, "executed": False, "release_clearance": False,
    }


class _Once(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        seen = getattr(namespace, "_seen", set())
        if self.dest in seen:
            parser.error(f"{option_string} must occur once")
        setattr(namespace, "_seen", seen | {self.dest})
        setattr(namespace, self.dest, values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--repo", type=Path, required=True, action=_Once)
    parser.add_argument("--from-pipeline", required=True, action=_Once)
    parser.add_argument("--expected", required=True, action=_Once)
    parser.add_argument("--package", required=True, action=_Once)
    parser.add_argument("--leaf", action="append", required=True)
    parser.add_argument("--format", action="append", required=True, choices=sorted(FORMATS))
    parser.add_argument("--selected-input", action="append", default=[])
    parser.add_argument("--linked-authority", action=_Once)
    parser.add_argument("--upstream-request", action=_Once)
    parser.add_argument("--upstream-expected", action=_Once)
    for prefix, required in (("profile", True), ("upstream-profile", False)):
        for suffix in ("home", "packs", "pointer", "context-file"):
            parser.add_argument(f"--{prefix}-{suffix}", type=Path, action=_Once,
                                required=required and suffix != "context-file")
    args = parser.parse_args()
    try:
        root = safety.checked_root(args.repo)
        def read_json(name: str) -> dict[str, Any]:
            raw, _ = safety.read_owned(root, safety.selector_path(name), MAX_BYTES)
            return load_json(raw.decode("utf-8-sig"))

        config = ProfileConfig(SOURCE, root, args.profile_home, args.profile_packs,
                               args.profile_pointer, context_file=args.profile_context_file)
        upstream_values = [args.upstream_request, args.upstream_expected, args.upstream_profile_home,
                           args.upstream_profile_packs, args.upstream_profile_pointer]
        upstream_config = None
        if any(value is not None for value in upstream_values):
            if any(value is None for value in upstream_values):
                raise ValueError("Supply the complete original upstream request/context/profile selection")
            upstream_config = ProfileConfig(SOURCE, root, args.upstream_profile_home, args.upstream_profile_packs,
                                             args.upstream_profile_pointer, context_file=args.upstream_profile_context_file)
        elif args.upstream_profile_context_file is not None:
            raise ValueError("An upstream context-file alone is not an upstream selection")
        result = load_pipeline_inputs(
            root, args.from_pipeline, expected=read_json(args.expected), profile_config=config,
            package_id=args.package, leaf_ids=args.leaf, formats=args.format,
            selected_inputs=args.selected_input, linked_authority=args.linked_authority,
            upstream_request=args.upstream_request,
            upstream_expected=read_json(args.upstream_expected) if args.upstream_expected else None,
            upstream_profile=upstream_config,
        )
        print(canonical_json(result))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(canonical_json({"status": "error", "reason": str(error),
                              "executed": False, "release_clearance": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
