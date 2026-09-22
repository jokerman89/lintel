#!/usr/bin/env python3
# component: profile-and-role-lifecycle
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P10.md
# constraints: consume the structured profile API; no host activation or private sync
# last_intent_review: 2026-09-20
"""Explicit local profile and role operations over the accepted profile contract."""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import date
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Sequence

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from context_safety import (atomic_write, checked_root, file_state, is_link, json_bytes, native_io_path,
                            read_owned, safe_path)
from profile_context import (
    MISSING, ManifestParser, ProfileConfig, ProfileError, bootstrap_profile_context, context_path, field_value,
    digest as profile_digest, load_profile_context, pack_directory, parse_manifest, profile_reference, read_json,
    rebind_profile_context, resolve_profile, validate_pack, validate_profile_reference,
    verify_profile_reference,
)

ROLE_FIELDS = ("role_id", "display_name", "scope", "audience", "voice_tier", "sensitivity")
ROLE_SECTIONS = ("IDENTITY", "COLD KNOWLEDGE", "DECISION CRITERIA", "VOICE + COMMUNICATION",
                 "OUTCOME LENS", "ROLE-SPECIFIC INSIGHTS", "COMPANION SKILLS")
LIGHT_SECTIONS = ("IDENTITY", "VOICE + COMMUNICATION", "OUTCOME LENS", "COMPANION SKILLS")
MAX_ROLE_BYTES = 1024 * 1024
KNOWLEDGE_MOVES = (
    ("tasks/lessons.md", ".claude/memory/lessons.md"),  # legacy-fallback-ok: shared migration/diagnosis mapping
    ("tasks/memory.md", ".claude/memory/working-state.md"),  # legacy-fallback-ok
    ("tasks/personas.md", ".claude/memory/personas.md"),  # legacy-fallback-ok
    ("tasks/todo.md", ".claude/plans/todo.md"),  # legacy-fallback-ok
)
MEMORY_INDEX = b"""# Memory index

Knowledge lives in this repository's .claude/ home.

- [lessons.md](lessons.md) - durable lessons.
- [working-state.md](working-state.md) - current work and next actions.
- [personas.md](personas.md) - operator calibration.
- [../decisions/](../decisions/) - accepted decisions.
- [../plans/todo.md](../plans/todo.md) - selected work and evidence.
"""


def native_path(value: Path) -> Path:
    path = Path(value)
    if os.name == "nt" and str(value).startswith(("/", "\\")) and not path.drive:
        raise ValueError("MSYS_PATH: use bin/li-lifecycle in Bash, or pass native Windows root arguments.")
    return path


def destination(value: Path) -> Path:
    path = Path(os.path.abspath(native_path(value)))
    for parent in (path, *path.parents):
        if is_link(parent):
            raise ValueError(f"Linked lifecycle path refused: {parent}")
        if parent != path and native_io_path(parent).exists() and not native_io_path(parent).is_dir():
            raise ValueError(f"Lifecycle parent is not a directory: {parent}")
    return path


def configuration(args: argparse.Namespace) -> ProfileConfig:
    source = checked_root(native_path(args.source))
    repo = checked_root(native_path(args.repo))
    home = destination(args.home or os.environ.get("LINTEL_HOME") or repo / ".claude/runtime/lintel-home")
    packs = destination(args.packs or os.environ.get("LINTEL_PACKS_DIR") or home / "packs")
    pointer = destination(args.pointer or os.environ.get("LINTEL_ACTIVE_PACK_FILE") or packs / "active-pack")
    reference = args.reference if args.reference is not None else os.environ.get("LINTEL_PROFILE_REFERENCE", "")
    context_file = args.context_file if args.context_file is not None else os.environ.get("LINTEL_PROFILE_CONTEXT_FILE", "")
    context = args.context if args.context is not None else os.environ.get("LINTEL_PROFILE_CONTEXT", "")
    if not context and not reference:
        context = os.environ.get("LINTEL_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID", "")
    return ProfileConfig(
        source, repo, home, packs, pointer, context_id=context,
        context_file=native_path(context_file) if context_file else None,
        explicit_pack=args.explicit_pack if args.explicit_pack is not None else os.environ.get("LINTEL_PROFILE_PACK", ""),
        expected_reference=read_json(reference) if reference else None,
    )


def selected_config(config: ProfileConfig) -> ProfileConfig:
    if config.context_id or config.context_file or config.expected_reference is not None:
        return config
    if config.selected.exists():
        data, _ = read_owned(config.repo, ".claude/runtime/profiles/selected.json")
        reference = validate_profile_reference(read_json(data.decode("utf-8")))
        return replace(config, expected_reference=reference)
    return config


def current_profile(config: ProfileConfig) -> tuple[dict, dict | None]:
    selected = selected_config(config)
    if selected.context_id or selected.context_file or selected.expected_reference is not None:
        record = load_profile_context(selected)
        return record["profile"], profile_reference(record)
    return resolve_profile(config), None


def validation_profile(config: ProfileConfig) -> tuple[dict, dict | None]:
    selected = selected_config(config)
    if selected.expected_reference is not None or selected.context_file is not None:
        return current_profile(selected)
    if selected.context_id and context_path(selected).parent.exists():
        return current_profile(selected)
    return resolve_profile(selected), None


def profile_result(record: dict) -> dict:
    return {"reference": profile_reference(record),
            "selection": record["profile"]["selection"],
            "effective_pack": record["profile"]["values"]["name"]}


def pack_switch(config: ProfileConfig, name: str, reason: str) -> dict:
    if not reason.strip() or len(reason) > 1000:
        raise ValueError("A profile switch requires a nonempty reason of at most 1000 characters.")
    if config.explicit_pack and config.explicit_pack != name:
        raise ProfileError("PROFILE_REQUIRED", "switch conflicts with explicit LINTEL_PROFILE_PACK",
                           required=True)
    candidate = replace(config, explicit_pack=name, expected_reference=None)
    resolve_profile(candidate)
    profile, reference = current_profile(config)
    before = file_state(config.pointer.parent, config.pointer.name) if config.pointer.parent.exists() else None
    old_pointer = read_owned(config.pointer.parent, config.pointer.name)[0] if before else b""
    if reference is not None and profile["values"]["name"] == name and old_pointer.strip() == name.encode("utf-8"):
        return {"changed": False, "reference": reference, "effective_pack": name,
                "pointer": str(config.pointer)}
    if reference is None:
        reference = profile_reference(bootstrap_profile_context(config))
    config.pointer.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(checked_root(config.pointer.parent), config.pointer.name, (name + "\n").encode("utf-8"),
                 before["mode"] if before else 0o600, expected=before, check_expected=True)
    try:
        updated = rebind_profile_context(replace(candidate, expected_reference=reference), reason)
        new_reference = profile_reference(updated)
        verify_profile_reference(new_reference, candidate)
    except (ProfileError, OSError, ValueError) as error:
        raise ValueError(
            "PROFILE_SWITCH_INCOMPLETE: pointer was written but binding did not complete; "
            "preserve the current pointer and retained profile history. Inspect profile-status, "
            f"then explicitly profile-rebind with a reason; no automatic rollback: {error}"
        ) from error
    if new_reference["name"] != name:
        raise ValueError("PROFILE_SWITCH_INCOMPLETE: effective profile differs from the requested pack.")
    return {"changed": True, "previous_reference": reference, "pointer": str(config.pointer),
            **profile_result(updated)}


def pack_list(config: ProfileConfig) -> dict:
    profile, reference = current_profile(config)
    rows, seen_paths = [], set()
    for origin, root in (("store", config.packs), ("repository", config.repo / "packs"),
                         ("source", config.source / "packs")):
        if not root.exists():
            continue
        root = checked_root(root)
        for directory in sorted(root.iterdir()):
            if directory in seen_paths or not directory.is_dir():
                continue
            path = safe_path(root, directory.name + "/pack.yaml")
            if not path.is_file():
                continue
            seen_paths.add(directory)
            row = {"name": directory.name, "path": str(directory), "origin": origin,
                   "selected_source": pack_directory(config, directory.name) == directory}
            try:
                chain, values, _ = validate_pack(replace(config, packs=root), directory.name)
                row.update(valid=True, version=values["version"], compatibility=[
                    member["compatibility"] for member in chain])
            except ProfileError as error:
                row.update(valid=False, diagnostic=f"{error.code}: {error}")
            rows.append(row)
    return {"packs": rows, "effective_pack": profile["values"]["name"], "reference": reference,
            "selection": profile["selection"], "validation_scope": "declared pack contracts, not host activation"}


def create_pack(config: ProfileConfig, args: argparse.Namespace) -> dict:
    name = role_id(args.name)
    current_profile(config)
    for root in (config.packs, config.repo / "packs", config.source / "packs"):
        if safe_path(root, name).exists():
            raise ValueError(f"Pack {name} already exists; current content is preserved.")
    root = config.packs if args.scope == "home" else config.repo / "packs"
    path = safe_path(root, name + "/pack.yaml")
    if args.extends:
        chain, _, _ = validate_pack(config, args.extends)
        data = (f'schema_version: "1"\nname: {name}\nversion: 1.0.0\n'
                f'extends: {args.extends}\n').encode("utf-8")
    else:
        template = args.from_pack or "_default"
        chain, _, _ = validate_pack(config, template)
        source = pack_directory(config, template)
        text = read_owned(source, "pack.yaml")[0].decode("utf-8-sig")
        data = re.sub(r"(?m)^name:[^\r\n]*", f"name: {name}", text).encode("utf-8")
    # Stage only manifests, not private corpora or extension executables. The same
    # resolver validates the new identity and all ancestors before publication.
    with tempfile.TemporaryDirectory(prefix="lintel-pack-") as temporary:
        staging = Path(temporary)
        for parent in chain:
            ancestor = Path(parent["path"])
            atomic_write(staging, parent["name"] + "/pack.yaml", read_owned(ancestor.parent, ancestor.name)[0])
        atomic_write(staging, name + "/pack.yaml", data)
        validate_pack(replace(config, packs=staging), name)
    root.mkdir(parents=True, exist_ok=True)
    atomic_write(checked_root(root), name + "/pack.yaml", data, expected=None, check_expected=True)
    if read_owned(root, name + "/pack.yaml")[0] != data:
        raise ValueError("Pack publication did not verify; preserve the candidate for inspection.")
    return {"status": "created", "name": name, "path": str(path.parent), "activated": False,
            "copied": "manifest only; referenced corpora and host extensions are not copied"}


def configured_asset(profile: dict, field: str) -> Path | None:
    value = field_value(profile["values"], field)
    if value is MISSING or value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a path string or null.")
    path = Path(value)
    if not path.is_absolute():
        origin = Path(profile["provenance"][field]["path"]).parent
        path = safe_path(checked_root(origin), value.replace("\\", "/"))
    return destination(path)


def role_roots(config: ProfileConfig, profile: dict) -> list[tuple[str, Path]]:
    roots = []
    pack = configured_asset(profile, "roles.source")
    if pack is not None:
        roots.append(("pack", pack))
    private = destination(Path(os.environ.get("LINTEL_PRIVATE_ROLES_DIR", config.home / "roles/private")))
    roots.extend((("private", private), ("home", config.home / "roles")))
    return roots


def role_id(name: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
        raise ValueError("Role ID must be a filesystem-safe kebab-case identifier.")
    return name


def role_metadata(header: str, name: str) -> dict:
    data = parse_manifest(header)
    if any(not isinstance(data.get(field), str) or not data[field].strip() for field in ROLE_FIELDS):
        raise ValueError(f"Role {name} requires nonempty metadata: {', '.join(ROLE_FIELDS)}")
    if data["role_id"] != name or data["sensitivity"] not in ("private", "public"):
        raise ValueError(f"Role identity/sensitivity does not match {name}.")
    return data


def role_document(text: str, name: str) -> tuple[dict, str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("Role must start with bounded frontmatter.")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            header = "".join(lines[1:index])
            if len(header) > 65536:
                raise ValueError("Oversized role frontmatter.")
            return role_metadata(header, name), "".join(lines[index + 1:])
    raise ValueError("Role frontmatter is not closed.")


def role_lines(body: str):
    from markdown_source import classify_markdown
    for boundary in classify_markdown(body).lines:
        text = body[boundary.start:boundary.next_start]
        heading = re.match(r"^(#{1,6})\s+(.+)", text) if (
            boundary.kind == "prose" and not boundary.container_ids) else None
        yield text, heading


def read_role_header(root: Path, name: str) -> dict:
    path = safe_path(checked_root(root), role_id(name) + ".md")
    before = path.stat()
    lines, size = [], 0
    # Inventory reads only the header; private body text is never loaded for listing.
    with path.open("r", encoding="utf-8-sig") as stream:
        if stream.readline(4096).strip() != "---":
            raise ValueError(f"Missing role frontmatter: {path}")
        while True:
            line = stream.readline(4096)
            size += len(line)
            if not line or size > 65536:
                raise ValueError(f"Missing or oversized role frontmatter: {path}")
            if line.strip() == "---":
                break
            lines.append(line)
    after = path.stat()
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError("Role changed during metadata inspection.")
    return role_metadata("".join(lines), name)


def find_role(config: ProfileConfig, profile: dict, name: str) -> tuple[str, Path, dict]:
    role_id(name)
    for origin, root in role_roots(config, profile):
        path = safe_path(root, name + ".md")
        if path.is_file():
            metadata = read_role_header(root, name)
            if origin == "private" and metadata["sensitivity"] != "private":
                raise ValueError("A private-store role cannot declare public sensitivity.")
            return origin, path, metadata
    raise ValueError(f"Role not found: {name}; current role is unchanged.")


def preferences(config: ProfileConfig) -> tuple[str, dict, dict | None]:
    path = safe_path(config.home, "profile.yaml")
    if not path.exists():
        return "", {}, None
    data, state = read_owned(config.home, "profile.yaml", MAX_ROLE_BYTES)
    text = data.decode("utf-8-sig")
    return text, parse_manifest(text), state


def active_role(values: dict) -> str | None:
    name = values.get("role_active")
    if name is None or name in ("", "none", "null"):
        return None
    if not isinstance(name, str):
        raise ValueError("role_active must be a role ID or null.")
    return role_id(name)


def read_role(path: Path, name: str, *, allow_private: bool, deep: bool) -> dict:
    metadata = read_role_header(path.parent, name)
    if metadata["sensitivity"] == "private" and not allow_private:
        raise ValueError("PRIVATE_ROLE_CONFIRMATION: explicitly allow private context for this operation.")
    data, state = read_owned(path.parent, path.name, MAX_ROLE_BYTES)
    text = data.decode("utf-8-sig")
    metadata, body = role_document(text, name)
    if metadata["sensitivity"] == "private" and not allow_private:
        raise ValueError("PRIVATE_ROLE_CONFIRMATION: role sensitivity changed during read.")
    selected, include, level = [], False, 6
    for line, heading in role_lines(body):
        if heading:
            title, depth = heading.group(2).strip().rstrip("#").strip().upper(), len(heading.group(1))
            known = any(title == item or title.startswith(item + " (")
                        for item in (*ROLE_SECTIONS, "SENSITIVE CONTEXT"))
            if known or depth <= level:
                include = any(title == item or title.startswith(item + " (") for item in LIGHT_SECTIONS)
                level = depth
        if include:
            selected.append(line)
    summary = "".join(selected).strip()
    if not summary:
        raise ValueError("Role has no lightweight identity/voice/lens sections.")
    result = {"role": metadata, "path": str(path), "sha256": state["sha256"], "summary": summary}
    if deep:
        result["content"] = body
    return result


def set_role(config: ProfileConfig, name: str | None, *, allow_private: bool = False) -> dict:
    profile, reference = current_profile(config)
    text, values, before = preferences(config)
    previous = active_role(values)
    result = {}
    if name is not None:
        _, path, _ = find_role(config, profile, name)
        result = read_role(path, name, allow_private=allow_private, deep=False)
    if previous != name:
        replacement = "role_active: " + (json.dumps(name) if name else "null")
        matches = list(re.finditer(r"(?m)^role_active:[^\r\n]*", text))
        if matches:
            match = matches[0]
            old_line = match.group()
            value_part = ManifestParser.scan(old_line, "#")[0]
            suffix = value_part[len(value_part.rstrip()):] + old_line[len(value_part):]
            updated = text[:match.start()] + replacement + suffix + text[match.end():]
        else:
            updated = text + ("" if not text or text.endswith("\n") else "\n") + replacement + "\n"
        parse_manifest(updated)
        if reference is None:
            record = bootstrap_profile_context(config)
            if record["profile"] != profile:
                raise ValueError("PROFILE_DRIFT: role policy changed before preference mutation.")
            reference = profile_reference(record)
        config.home.mkdir(parents=True, exist_ok=True)
        atomic_write(checked_root(config.home), "profile.yaml", updated.encode("utf-8"),
                     before["mode"] if before else 0o600, expected=before, check_expected=True)
        if active_role(preferences(config)[1]) != name:
            raise ValueError("Role preference write did not verify.")
    return {**result, "previous_role": previous, "active_role": name, "changed": previous != name,
            "profile_reference": reference, "host_activation": "not performed"}


def list_roles(config: ProfileConfig, *, include_private: bool) -> dict:
    profile, reference = current_profile(config)
    _, values, _ = preferences(config)
    rows, seen = [], set()
    for origin, root in role_roots(config, profile):
        if origin == "private" and not include_private:
            continue
        if not root.exists():
            continue
        for path in sorted(checked_root(root).glob("*.md")):
            metadata = read_role_header(root, path.stem)
            if metadata["sensitivity"] == "private" and not include_private:
                continue
            if origin == "private" and metadata["sensitivity"] != "private":
                raise ValueError("A private-store role cannot declare public sensitivity.")
            rows.append({**metadata, "origin": origin, "path": str(path),
                         "selected_source": path.stem not in seen})
            seen.add(path.stem)
    return {"roles": rows, "active_role": active_role(values), "profile_reference": reference}


def write_role(config: ProfileConfig, args: argparse.Namespace) -> dict:
    name = role_id(args.name)
    profile, _ = current_profile(config)
    draft = destination(args.file)
    data, _ = read_owned(checked_root(draft.parent), draft.name, MAX_ROLE_BYTES)
    text = data.decode("utf-8-sig")
    metadata, body = role_document(text, name)
    if metadata["sensitivity"] != args.scope:
        raise ValueError("Role sensitivity must match the explicitly selected destination scope.")
    headings = [match.group(2).strip().rstrip("#").strip().upper()
                for _, match in role_lines(body) if match]
    for required in ROLE_SECTIONS:
        if not any(heading == required or heading.startswith(required + " (") for heading in headings):
            raise ValueError(f"Draft role is missing section: {required}")
    roots = dict(role_roots(config, profile))
    root = roots["private"] if args.scope == "private" else roots.get("pack", roots["home"])
    path = safe_path(root, name + ".md")
    before = file_state(root, path.name) if root.exists() else None
    if before and not args.expected_sha256:
        raise ValueError("Role exists; an explicit update requires its previously reviewed SHA-256.")
    if args.expected_sha256 and (before is None or before["sha256"] != args.expected_sha256):
        raise ValueError("Role update conflicts with its reviewed SHA-256; current bytes preserved.")
    if before:
        existing = read_role_header(root, name)
        if existing["sensitivity"] != args.scope:
            raise ValueError("An update cannot change the role's sensitivity or publication boundary.")
    root.mkdir(parents=True, exist_ok=True)
    atomic_write(checked_root(root), path.name, data, before["mode"] if before else 0o600,
                 expected=before, check_expected=True)
    if read_owned(root, path.name)[0] != data:
        raise ValueError("Role write did not verify.")
    return {"status": "updated" if before else "created", "path": str(path),
            "sha256": file_state(root, path.name)["sha256"], "activated": False, "synchronized": False}


def persona_sources(config: ProfileConfig) -> dict:
    profile, reference = current_profile(config)
    sources = []
    pack = configured_asset(profile, "persona.source")
    if pack is not None:
        if not pack.exists():
            raise ValueError(f"Configured persona source is missing: {pack}")
        sources.append({"origin": "pack", "path": str(pack)})
    local = safe_path(config.repo, ".claude/memory/personas.md")
    if local.is_file():
        sources.append({"origin": "repository", "path": str(local)})
    details = safe_path(config.repo, "docs/personas")
    if details.is_dir():
        for path in sorted(details.glob("*.md")):
            sources.append({"origin": "repository", "path": str(safe_path(details, path.name))})
    return {"sources": sources, "lifetime": "current conversation only", "profile_reference": reference}


def layout_observation(repo: Path) -> dict:
    import stat

    def observed_path(relative: str) -> tuple[Path, os.stat_result | None]:
        path = safe_path(repo, relative)
        try:
            return path, native_io_path(path).lstat()
        except FileNotFoundError:
            return path, None

    def retained_redirect(data: bytes, destination: str) -> bool:
        if not data.startswith(f"> Moved to {destination} (".encode("utf-8")):
            return False
        relative = destination.rstrip("/")
        _, observed = observed_path(relative)
        if observed is None:
            return False
        if destination.endswith("/"):
            if not stat.S_ISDIR(observed.st_mode):
                raise ValueError(f"Redirect destination is not a directory: {relative}")
        else:
            read_owned(repo, relative)
        return True

    _, marker = observed_path(".claude/lintel-layout.yaml")
    version = None
    if marker is not None:
        version = parse_manifest(read_owned(repo, ".claude/lintel-layout.yaml")[0].decode("utf-8")).get("layout_version")
        if type(version) is not int or version < 1:
            raise ValueError("Invalid layout_version; preserve the layout marker and inspect it.")
    legacy, stubs = [], []
    for old, new in KNOWLEDGE_MOVES + (("docs/adr/README.md", ".claude/decisions/"),):  # legacy-fallback-ok
        _, observed = observed_path(old)
        if observed is not None:
            data, _ = read_owned(repo, old, MAX_ROLE_BYTES)
            if new.endswith("/") and not data.startswith(f"> Moved to {new} (".encode("utf-8")):
                new += Path(old).name
            if retained_redirect(data, new):
                stubs.append(old)
            else:
                legacy.append(old)
    for folder in ("docs/adr", ".lintel/state"):
        path, observed = observed_path(folder)
        if observed is None:
            continue
        if not stat.S_ISDIR(observed.st_mode):
            raise ValueError(f"Legacy location is not a directory: {folder}")
        pending = [path]
        while pending:
            directory = pending.pop()
            for native_entry in native_io_path(directory).iterdir():
                entry = directory / native_entry.name
                relative = entry.relative_to(repo).as_posix()
                _, observed = observed_path(relative)
                if observed is None:
                    raise ValueError(f"Layout entry disappeared during inspection: {relative}")
                if stat.S_ISDIR(observed.st_mode):
                    pending.append(entry)
                elif not stat.S_ISREG(observed.st_mode):
                    raise ValueError(f"Legacy entry is not a regular file: {relative}")
                elif relative not in stubs and relative not in legacy:
                    destination_path = ".claude/decisions/" + entry.relative_to(path).as_posix()
                    if folder == "docs/adr" and entry.suffix == ".md":  # legacy-fallback-ok
                        data, _ = read_owned(repo, relative)
                        if retained_redirect(data, destination_path):
                            stubs.append(relative)
                            continue
                    legacy.append(relative)
    status = ("incomplete" if version and version >= 5 else "needs_migration") if legacy else (
        "current" if version and version >= 5 else "not_applicable")
    return {"observation": status, "layout_version": version, "legacy": sorted(legacy), "stubs": stubs}


def migration_inventory(config: ProfileConfig, *, include_archived: bool, today: date) -> dict:
    from markdown_source import classify_markdown
    relative = "docs/migrations/_INDEX.md"
    if not safe_path(config.source, relative).is_file():
        raise ValueError("MIGRATION_CATALOG_MISSING: installed source has no migration catalog; status is unknown.")
    text = read_owned(config.source, relative, MAX_ROLE_BYTES)[0].decode("utf-8-sig")
    classified = classify_markdown(text)
    section, rows, found = "", [], False
    for boundary in classified.lines:
        if boundary.kind != "prose" or boundary.container_ids:
            continue
        line = text[boundary.start:boundary.end].strip()
        if line.startswith("## "):
            section = line[3:].lower()
            found = found or section == "active migrations"
        if section not in ("active migrations", "archived migrations") or not line.startswith("|"):
            continue
        archived = section == "archived migrations"
        if archived and not include_archived:
            continue
        header = (["Slug", "Started", "Closed", "Outcome"] if archived else
                  ["Slug", "Started", "Grace until", "Removal at", "Description"])
        body = line[1:-1] if line.endswith("|") else line[1:]
        # Preserve empty cells and any additional pipes in the final prose field.
        cells = [cell.strip() for cell in body.split("|", len(header) - 1)]
        if len(cells) != len(header) or not all(cells):
            raise ValueError(
                f"MIGRATION_CATALOG_INVALID: {section} row requires {len(header)} nonempty fields: {cells[0]!r}")
        if (cells == header or all(re.fullmatch(r":?-+:?", cell) for cell in cells)
                or cells == ["_none yet_", *(["\u2014"] * (len(header) - 1))]):
            continue
        if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*", cells[0]):
            raise ValueError(f"MIGRATION_CATALOG_INVALID: malformed {section} row: {cells[0]!r}")
        date.fromisoformat(cells[1])
        deadline = None if cells[2] == "none" else date.fromisoformat(cells[2])
        row = {"slug": cells[0], "started": cells[1], "grace_until": None if archived else cells[2],
               "schedule": "archived" if archived else (
                   "overdue" if deadline and deadline < today else "open"),
               "observation": "unknown", "description": cells[-1]}
        if cells[0] == "v5-claude-home-layout":
            row.update(layout_observation(config.repo))
        rows.append(row)
    if not found:
        raise ValueError("MIGRATION_CATALOG_INVALID: active table not found; status is unknown.")
    return {"catalog": str(config.source / relative), "target": str(config.repo), "migrations": rows,
            "date": today.isoformat(), "notice": "A schedule is not removal authorization; unknown detectors stay unknown."}


def doctor(config: ProfileConfig, *, store: Path | None = None, native_store: Path | None = None) -> dict:
    from client_capabilities import load_registry
    from managed_transaction import assert_ready, default_store
    issues = []
    report = {"source": str(config.source), "target": str(config.repo), "home": str(config.home),
              "host_activation": "unverified", "hook_execution": "unverified",
              "installed_clis": [], "cached_plugins": [], "issues": issues}
    load_registry(config.source / "lib/cli-tiers.yaml")
    for name in ("claude", "codex", "cursor", "gemini", "opencode", "copilot", "droid"):
        report["installed_clis"].append({"name": name, "path": shutil.which(name),
                                         "plugin_activation": "unverified"})
    metadata = read_json(read_owned(config.source, ".claude-plugin/plugin.json")[0].decode("utf-8-sig"))
    report["source_version"] = metadata.get("version")
    selected_store = destination(store or os.environ.get("LINTEL_RECOVERY_STORE") or default_store(config.repo))
    try:
        assert_ready(config.repo, selected_store)
        report["transaction"] = {"status": "no_incomplete_operation", "store": str(selected_store)}
    except (ValueError, OSError) as error:
        report["transaction"] = {"status": "error", "store": str(selected_store), "diagnostic": str(error)}
        issues.append("Working target has unresolved transaction/recovery evidence.")
    native_recovery = destination(native_store or Path(str(config.home) + "-recovery"))
    report["native_install"] = {"status": "not_detected"}
    if (config.home / ".lintel-install.tsv").exists() or (native_recovery / ".lintel-recovery-owner").exists():
        installer = safe_path(config.source, "install/install.sh")
        bash = shutil.which("bash")
        if not installer.is_file() or not bash:
            report["native_install"] = {"status": "unverified", "diagnostic": "Approved native checker or Bash is unavailable."}
            issues.append("Native installation could not be checked from this source/host.")
        else:
            try:
                result = subprocess.run(
                    [bash, str(installer), "--check", "--home", str(config.home), "--store", str(native_recovery)],
                    capture_output=True, text=True, encoding="utf-8", timeout=90, check=False,
                )
                report["native_install"] = {"status": "verified" if result.returncode == 0 else "error",
                                             "exit_code": result.returncode,
                                             "diagnostic": result.stdout.strip() if result.returncode == 0 else result.stderr.strip()}
            except subprocess.TimeoutExpired:
                report["native_install"] = {"status": "unverified", "diagnostic": "Native checker exceeded 90 seconds."}
            if report["native_install"]["status"] != "verified":
                issues.append("Native installation is incomplete, changed or unavailable; no repair was attempted.")
    try:
        profile, reference = current_profile(config)
        report["profile"] = {"reference": reference, "selection": profile["selection"],
                             "effective_pack": profile["values"]["name"]}
    except (ValueError, OSError) as error:
        report["profile"] = {"status": "error", "diagnostic": str(error)}
        issues.append("Effective profile could not be verified.")
    required = ("AGENTS.md", "CLAUDE.md", "CORE-PRINCIPLES.md", ".claude/memory/lessons.md",
                ".claude/decisions/README.md", ".claude/lintel-layout.yaml")
    report["foundation_missing"] = [name for name in required if not safe_path(config.repo, name).is_file()]
    if report["foundation_missing"]:
        issues.append("Working target has incomplete foundation files.")
    try:
        report["layout"] = layout_observation(config.repo)
        if report["layout"]["observation"] in ("incomplete", "needs_migration"):
            issues.append("Legacy content needs explicit migration or recovery.")
    except (ValueError, OSError) as error:
        report["layout"] = {"observation": "error", "diagnostic": str(error)}
        issues.append("Layout diagnosis failed; no state was repaired.")
    report["adapter"] = {"status": "not_installed"}
    if safe_path(config.repo, ".github/lintel/manifest.json").exists():
        adapter = safe_path(config.source, "bin/li-adapter.py")
        try:
            result = subprocess.run([sys.executable, str(adapter), "check", "--source", str(config.source),
                                     "--target", str(config.repo)], capture_output=True, text=True,
                                    encoding="utf-8", timeout=90, check=False)
            report["adapter"] = {"status": "verified" if result.returncode == 0 else "error",
                                 "exit_code": result.returncode,
                                 "diagnostic": result.stdout.strip() if result.returncode == 0 else result.stderr.strip()}
        except subprocess.TimeoutExpired:
            report["adapter"] = {"status": "unverified", "diagnostic": "Adapter check exceeded 90 seconds."}
        if report["adapter"]["status"] != "verified":
            issues.append("Managed repository adapter failed its actual check.")
    hooks = {"modified": [], "missing": [], "operator_extra": [], "registration": "unverified"}
    shipped = config.source / "hooks"
    installed = config.home / "hooks"
    if shipped.is_dir() and installed.is_dir():
        source_paths = set()
        for path in sorted((shipped / "shared").rglob("*")):
            relative = path.relative_to(shipped).as_posix()
            safe_path(shipped, relative)
            if not path.is_file():
                continue
            source_paths.add(relative)
            actual = file_state(installed, relative)
            if actual is None:
                hooks["missing"].append(relative)
            elif actual["sha256"] != file_state(shipped, relative)["sha256"]:
                hooks["modified"].append(relative)
        for path in sorted(installed.rglob("*")):
            relative = path.relative_to(installed).as_posix()
            safe_path(installed, relative)
            if path.is_file() and relative not in source_paths:
                hooks["operator_extra"].append(relative)
        if hooks["modified"] or hooks["missing"]:
            issues.append("Installed hook bytes differ; custom content was preserved.")
    else:
        hooks["comparison"] = "unavailable: separate shipped/installed hook files not present"
    report["hooks"] = hooks
    cache = Path(os.environ.get("HOME", Path.home())) / ".claude/plugins/cache"
    if cache.exists():
        cache = checked_root(cache)
        for path in sorted(cache.glob("*/li/*/.claude-plugin/plugin.json")):
            relative = path.relative_to(cache).as_posix()
            try:
                value = read_json(read_owned(cache, relative, MAX_ROLE_BYTES)[0].decode("utf-8-sig"))
                if value.get("name") != "li" or not isinstance(value.get("version"), str):
                    raise ValueError("Cache manifest does not name an exact versioned li plugin.")
                report["cached_plugins"].append({"path": str(path), "version": value["version"],
                                                  "activation": "unverified"})
            except (ValueError, OSError) as error:
                issues.append(f"Invalid cache manifest (not activation evidence): {error}")
    report["audit_log_present"] = safe_path(config.repo, ".claude/runtime/audit/hooks.jsonl").is_file()
    report["status"] = "attention" if issues else "local_checks_verified"
    return report


def print_doctor(report: dict) -> None:
    print("Lintel Doctor - read-only local diagnostics")
    print(f"Source: {report['source']}\nTarget: {report['target']}\nInstalled data: {report['home']}")
    print("\n## Installed CLIs")
    for entry in report["installed_clis"]:
        print(f"  {entry['name']}: {entry['path'] or 'not on PATH'}; plugin activation unverified")
    print("\n## Scaffolding and profile")
    print(f"  Source metadata version: {report['source_version']}")
    print(f"  Missing foundation files: {', '.join(report['foundation_missing']) or 'none'}")
    print(f"  Layout: {report['layout']['observation']}; adapter: {report['adapter']['status']}")
    print(f"  Native install: {report['native_install']['status']}; recovery: {report['transaction']['status']}")
    print(f"  Effective profile: {report['profile'].get('effective_pack', 'unresolved')}")
    print("\n## Hooks and host boundaries")
    print("  Registration and current-session firing unverified; cached versions and historical logs are not proof.")
    for plugin in report["cached_plugins"]:
        print(f"  Cached li version {plugin['version']}: activation unverified ({plugin['path']})")
    for relative in report["hooks"]["modified"] + report["hooks"]["missing"]:
        print(f"  Changed/missing hook: {relative}")
    print(f"\n## Verdict\n  {report['status']}")
    for issue in report["issues"]:
        print(f"  - {issue}")


def json_field(data: bytes, key: str, value: str) -> bytes:
    text = data.decode("utf-8-sig")
    values = read_json(text)
    if values.get(key) == value:
        return data
    decoder = json.JSONDecoder()
    position = text.index("{") + 1
    end_value = position
    while True:
        position += len(text[position:]) - len(text[position:].lstrip())
        if text[position] == "}":
            prefix = (", " if values else "") + json.dumps(key) + ": " + json.dumps(value)
            replacement = text[:end_value] + prefix + text[end_value:]
            break
        name, end = decoder.raw_decode(text, position)
        colon = text.index(":", end)
        start = colon + 1
        start += len(text[start:]) - len(text[start:].lstrip())
        _, end_value = decoder.raw_decode(text, start)
        if name == key:
            replacement = text[:start] + json.dumps(value) + text[end_value:]
            break
        position = end_value
        position += len(text[position:]) - len(text[position:].lstrip())
        if text[position] == ",":
            position += 1
    updated = read_json(replacement)
    if updated != {**values, key: value}:
        raise ValueError("Settings field update changed unrelated values.")
    return (b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b"") + replacement.encode("utf-8")


def migration_changes(repo: Path, *, pointer_only: bool = False,
                      memory_pointer: bool = True) -> tuple[dict, dict, dict]:
    changes, observed, originals = {}, {}, {}

    def observe(relative: str) -> bytes | None:
        if relative not in observed:
            path = native_io_path(safe_path(repo, relative))
            try:
                path.lstat()
            except FileNotFoundError:
                originals[relative], observed[relative] = None, None
            else:
                originals[relative], observed[relative] = read_owned(repo, relative)
        return originals[relative]

    marker = observe(".claude/lintel-layout.yaml")
    version = None
    if marker is not None:
        version = parse_manifest(marker.decode("utf-8")).get("layout_version")
        if type(version) is not int or version not in (1, 2, 3, 4, 5):
            raise ValueError("Unsupported layout marker; preserve it and use an explicit migration plan.")
    if pointer_only and version != 5:
        raise ValueError("Pointer-only repair requires an already migrated v5 target.")

    def move(old: str, new: str, *, redirect: bool) -> None:
        safe_path(repo, new)
        data = observe(old)
        if data is None:
            return
        if old == "docs/adr/README.md" and data.startswith(b"> Moved to .claude/decisions/ ("):  # legacy-fallback-ok
            if not native_io_path(safe_path(repo, ".claude/decisions")).is_dir():
                raise ValueError("Stranded historical decisions redirect.")
            return
        target = observe(new)
        if data.startswith(f"> Moved to {new} (".encode("utf-8")):
            if target is None:
                raise ValueError(f"Stranded redirect without its destination: {old}")
            return
        if target is not None:
            raise ValueError(f"Migration collision (both preserved): {old} and {new}")
        changes[new] = data
        changes[old] = (
            f"> Moved to {new} (v5 .claude/ home layout, ADR-0005). Retained for explicit historical recovery.\n".encode("utf-8")
            if redirect else None
        )

    if not pointer_only:
        for old, new in KNOWLEDGE_MOVES:
            move(old, new, redirect=True)
        for old_root, new_root, redirects in (
            ("docs/adr", ".claude/decisions", True),  # legacy-fallback-ok: explicit migration
            (".lintel/state", ".claude/runtime/state", False),
        ):
            folder = safe_path(repo, old_root)
            if native_io_path(folder).exists():
                if not native_io_path(folder).is_dir():
                    raise ValueError(f"Legacy location is not a directory: {old_root}")
                pending = [folder]
                while pending:
                    directory = pending.pop()
                    for entry in sorted(native_io_path(directory).iterdir()):
                        path = directory / entry.name
                        relative = path.relative_to(repo).as_posix()
                        safe_path(repo, relative)
                        if native_io_path(path).is_dir():
                            pending.append(path)
                        else:
                            move(relative, new_root + "/" + path.relative_to(folder).as_posix(),
                                 redirect=redirects and path.suffix == ".md")
        if observe(".claude/memory/MEMORY.md") is None:
            changes[".claude/memory/MEMORY.md"] = MEMORY_INDEX
        if version != 5:
            changes[".claude/lintel-layout.yaml"] = b"layout_version: 5\n"
        original = observe(".gitignore")
        if original is None:
            original = b""
        text = original.decode("utf-8")
        if ".claude/runtime/" in text.splitlines() and (repo / ".git").exists():
            result = subprocess.run(["git", "-c", "core.fsmonitor=false", "-C", str(repo),
                                     "check-ignore", "--no-index", "--quiet", ".claude/runtime/.lintel-check"],
                                    capture_output=True, check=False)
            if result.returncode:
                raise ValueError("Existing ignore rules do not protect .claude/runtime/; review them explicitly.")
        missing = [rule for rule in (".claude/runtime/", ".claude/settings.local.json") if rule not in text.splitlines()]
        if missing:
            separator = "" if not text or text.endswith("\n") else "\n"
            changes[".gitignore"] = (text + separator + "# Lintel local state\n" + "\n".join(missing) + "\n").encode("utf-8")
    if memory_pointer:
        data = observe(".claude/settings.local.json")
        if data is None:
            data = b"{}\n"
        updated = json_field(data, "autoMemoryDirectory", str(repo / ".claude/memory"))
        if updated != data:
            changes[".claude/settings.local.json"] = updated
    return (changes, {name: observed[name] for name in changes},
            {name: before for name, before in observed.items() if name not in changes})


def runtime_publication(config: ProfileConfig, args: argparse.Namespace, changes: dict,
                        expected: dict, label: str, *, guards: dict,
                        final_paths: Sequence[str] = ()) -> dict:
    from managed_transaction import apply_files, assert_ready, default_store
    store = destination(args.store or os.environ.get("LINTEL_RECOVERY_STORE") or default_store(config.repo))
    assert_ready(config.repo, store)
    if set(changes) != set(expected) or set(guards) & set(changes):
        raise ValueError("Lifecycle changes require their original expected states.")
    modes = {name: None if data is None else expected[name]["mode"] if expected[name] else 0o600
             for name, data in changes.items()}
    for name, before in {**expected, **guards}.items():
        if file_state(config.repo, name) != before:
            raise ValueError(f"Lifecycle input changed after planning: {name}")
    if args.dry_run:
        return {"state": "preview", "target": str(config.repo), "store": str(store),
                "changes": {name: "delete" if data is None else "replace" if expected[name] else "create"
                            for name, data in changes.items()}}
    result = apply_files(config.repo, store, changes, expected, modes, label=label,
                         final_paths=[path for path in final_paths if path in changes])
    if hasattr(args, "operation_evidence"):
        if result["id"]:
            receipt = checked_root(store / "transactions" / result["id"])
            atomic_write(receipt, "operation-profile.json", json_bytes(args.operation_evidence))
        if args.caller_reference is not None:
            verify_profile_reference(args.caller_reference, args.caller_config)
        if profile_digest(resolve_profile(config)) != args.target_profile_digest:
            raise ValueError(f"PROFILE_DRIFT: target policy changed during {result['id']}; inspect the files and replan.")
    return result


def operation_profiles(config: ProfileConfig, args: argparse.Namespace, *,
                       allow_missing: bool = False) -> tuple[ProfileConfig, dict, dict]:
    caller, reference = current_profile(config)
    target = (destination(args.target) if allow_missing else checked_root(args.target)) if args.target else config.repo
    target_config = replace(config, repo=target, context_id="", context_file=None, expected_reference=None)
    required = caller["selection"]["mode"] == "required"
    if required and reference is None:
        raise ValueError("PROFILE_CONTEXT_REQUIRED: explicitly bind the required caller profile before lifecycle mutation.")
    requested = getattr(args, "pack", None)
    if required:
        if requested and requested != caller["values"]["name"]:
            raise ValueError("PROFILE_REQUIRED: render selection conflicts with the required caller policy.")
        target_config = replace(target_config, explicit_pack=caller["values"]["name"])
    elif requested:
        target_config = replace(target_config, explicit_pack=requested)
    target_profile = resolve_profile(target_config)
    if required:
        identity = lambda profile: {key: profile[key] for key in ("ancestry", "baseline", "values", "compatibility")}
        if identity(caller) != identity(target_profile):
            raise ValueError("PROFILE_REQUIRED: target policy source/content differs from the verified caller constraint.")
    evidence = {
        "operation_profile_reference": reference,
        "required_caller_policy": required,
        "target_profile_reference": None,
        "target_selection": target_profile["selection"],
        "policy_enforcement": "profile inputs checked; host controls not executed",
    }
    args.operation_evidence = evidence
    args.caller_config, args.caller_reference = config, reference
    args.target_profile_digest = profile_digest(target_profile)
    return target_config, target_profile, evidence


def scaffold(config: ProfileConfig, args: argparse.Namespace) -> dict:
    if args.copilot or args.client:
        unsupported = [name for name in ("name", "pack", "mode", "voice", "compliance") if getattr(args, name)]
        if unsupported:
            raise ValueError("unsupported options with --copilot/--client: " + ", ".join("--" + name for name in unsupported))
        if args.dry_run:
            raise ValueError("Use the adapter's check for inspection; --dry-run is not an adapter init.")
        config, _, profiles = operation_profiles(config, args)
        entry = "bin/li-copilot.py" if args.copilot else "bin/li-adapter.py"
        command = [sys.executable, str(config.source / entry), args.action, "--source", str(config.source),
                   "--target", str(config.repo)]
        for client in args.client:
            command += ["--client", client]
        if args.store:
            command += ["--store", str(args.store)]
        result = subprocess.run(command, check=False)
        if result.returncode:
            raise ValueError(f"Adapter returned {result.returncode}; installation is not verified.")
        return {"state": "adapter_verified", "target": str(config.repo), "host_activation": "unverified", **profiles}
    if args.compliance is not None:
        raise ValueError("UNSUPPORTED_POLICY_OPERATION: legacy --compliance never configured controls; "
                         "select and validate actual pack policy through pack-switch instead.")
    config, target_profile, profiles = operation_profiles(config, args)
    source = safe_path(config.source, "scaffolding/01-foundation")
    required = ["CLAUDE.md.template", "AGENTS.md.template", "CORE-PRINCIPLES.md", "SESSION-PROTOCOL.md",
                "EVOLUTION.md", "EVOLUTION-LOG.md", "TEMPLATE-skill.md", "TEMPLATE-agent.md",
                ".claude/memory/lessons.md", ".claude/memory/working-state.md", ".claude/memory/personas.md",
                ".claude/memory/personas-example.md", ".claude/plans/todo.md",
                ".claude/decisions/README.md", ".claude/decisions/TEMPLATE.md", ".claude/SUBAGENT-GUIDE.md"]
    required += ["templates/swarm/" + name for name in ("charter.template.md", "coordination.template.json",
                 "agent-brief.template.md", "agent-report.template.md", "agent-review.template.md")]
    templates = {name: read_owned(source, name)[0] for name in required}
    variables = {"REPO_NAME": args.name or config.repo.name, "PACK": target_profile["values"]["name"],
                 "MODE": args.mode or "internal-tool",
                 "VOICE_TIER": args.voice or field_value(target_profile["values"], "voice.default_tier")}
    if any(not isinstance(value, str) or any(ord(char) < 32 for char in value) for value in variables.values()):
        raise ValueError("Scaffold preferences must be single-line literal values.")
    changes, expected, guards = migration_changes(config.repo, memory_pointer=not args.no_memory_pointer)
    preserved = []
    for relative, data in templates.items():
        if relative.endswith(".md.template"):
            relative = relative.removesuffix(".template")
            text = data.decode("utf-8-sig")
            for key, value in variables.items():
                text = text.replace("{{" + key + "}}", value)
            data = text.encode("utf-8")
        elif relative.startswith("templates/swarm/"):
            relative = ".claude/" + relative
        if relative in changes:
            continue
        if relative not in guards:
            guards[relative] = file_state(config.repo, relative)
        if guards[relative] is not None:
            preserved.append(relative)
        else:
            changes[relative] = data
            expected[relative] = guards.pop(relative)
    rules = ".claude/rules/README.md"
    guards[rules] = file_state(config.repo, rules)
    if guards[rules] is None:
        expected[rules] = guards.pop(rules)
        changes[rules] = (
            "# Path-scoped rules\n\nKeep one reviewed rule per file. Use quoted `paths:` globs where the host supports them.\n"
            "Native discovery and hook activation depend on the actual client; other clients read rules explicitly.\n"
        ).encode("utf-8")
    if args.action == "check":
        args.dry_run = True
    result = runtime_publication(config, args, changes, expected, "foundation scaffold",
                                 guards=guards, final_paths=[".claude/lintel-layout.yaml"])
    return {**result, **profiles, "preserved": preserved, "preferences": variables,
            "host_activation": "not performed", "git_index": "unchanged"}


def manifest_yaml(values: dict, indent: int = 0) -> str:
    lines = []
    for key, value in values.items():
        prefix = " " * indent + key + ":"
        if isinstance(value, dict) and value:
            lines.append(prefix + "\n" + manifest_yaml(value, indent + 2).rstrip("\n"))
        else:
            lines.append(prefix + " " + json.dumps(value, ensure_ascii=False))
    return "\n".join(lines) + "\n"


def extension_pack(config: ProfileConfig, args: argparse.Namespace) -> dict:
    name = role_id(args.name)
    if not re.fullmatch(r"[a-z][a-z0-9]*", args.namespace):
        raise ValueError("Namespace must be lowercase alphanumeric.")
    role_id(args.workflow)
    parent = destination(args.target or config.repo)
    target = parent if args.in_place else safe_path(parent, name)
    for filename in ("pack.yaml", ".claude-plugin/plugin.json", "README.md", "CLAUDE.md"):
        if file_state(target, filename) is not None:
            raise ValueError(f"Extension scaffold collision (preserved): {filename}")
    directories = ("skills", "agents", "hooks/shared", "knowhow", "lib", "tests/shape", "tests/unit",
                   ".claude-plugin", ".claude/decisions", ".claude/memory", ".claude/plans", "source")
    for name_in_tree in directories:
        path = destination(target / name_in_tree)
        if native_io_path(path).exists() and not native_io_path(path).is_dir():
            raise ValueError(f"Extension scaffold directory collision: {name_in_tree}")
    args.target = target
    target_config, _, profiles = operation_profiles(config, args, allow_missing=True)
    data = read_owned(config.source, "packs/_default/pack.yaml")[0]
    values = parse_manifest(data.decode("utf-8-sig"))
    values["name"] = name
    values["extension"].update(is_extension=True, namespace=args.namespace, workflow=args.workflow,
                               provides_skills=True, provides_agents=True, provides_hooks=True)
    values["navigation"]["default_workflow"] = args.workflow
    manifest = manifest_yaml(values).encode("utf-8")
    with tempfile.TemporaryDirectory(prefix="lintel-extension-") as temporary:
        staged = Path(temporary)
        atomic_write(staged, name + "/pack.yaml", manifest)
        validate_pack(replace(config, packs=staged), name)
    sanitize = lambda text: "".join(" " if ord(char) < 32 else char for char in text)
    title = sanitize(args.title or name)
    description = sanitize(args.description or f"Lintel extension pack: {name}")
    plugin = {"name": name, "version": "0.1.0", "description": description, "namespace": args.namespace}
    readme = (
        f"# {title}\n\nLintel extension-pack source for `{args.workflow}` (namespace `{args.namespace}`).\n\n"
        "## Build and validate\n\nImplement the declared skills, agents and optional hooks, then validate the pack through "
        "the installed Lintel profile helper. This is a skeleton, not an implemented workflow.\n\n"
        "## Install and run\n\nUse the actual host's supported plugin/skill discovery and its required authorization. "
        "The Claude-format manifest does not establish discovery in other clients. Select pack identity separately "
        "with `pack-switch`; creation does not activate plugins, hooks, policy or private synchronization.\n"
    ).encode("utf-8")
    instructions = (
        f"# Repository instructions for {title}\n\nThis repository is an extension-pack source, not a running host plugin.\n"
        f"Implement `{args.workflow}` from the approved specification. Keep specialist methods under `skills/`, "
        "agent roles under `agents/`, reference knowledge under `knowhow/` and authorized source material under `source/`.\n"
        "Validate actual outputs and retain independent review. Do not register hooks or publish private material "
        "as a side effect of scaffolding.\n"
    ).encode("utf-8")
    changes = {"pack.yaml": manifest, ".claude-plugin/plugin.json": (json.dumps(plugin, indent=2) + "\n").encode("utf-8"),
               "README.md": readme, "CLAUDE.md": instructions}
    if args.dry_run:
        return {"state": "preview", **profiles, "path": str(target), "changes": sorted(changes),
                "activated": False, "implementation": "skeleton"}
    native_io_path(target).mkdir(parents=True, exist_ok=True)
    result = runtime_publication(target_config, args, changes, {name: None for name in changes},
                                 "extension pack scaffold", guards={}, final_paths=["pack.yaml"])
    if not args.dry_run:
        for relative in directories:
            native_io_path(destination(target / relative)).mkdir(parents=True, exist_ok=True)
    return {**result, **profiles, "path": str(target), "namespace": args.namespace,
            "workflow": args.workflow, "activated": False, "implementation": "skeleton"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(os.environ.get(
        "LINTEL_SOURCE_ROOT", Path(__file__).resolve().parents[1])))
    parser.add_argument("--repo", type=Path, default=Path(os.environ.get("LINTEL_REPO_ROOT", Path.cwd())))
    parser.add_argument("--home", type=Path)
    parser.add_argument("--packs", type=Path)
    parser.add_argument("--pointer", type=Path)
    parser.add_argument("--context")
    parser.add_argument("--context-file")
    parser.add_argument("--reference")
    parser.add_argument("--profile-pack", dest="explicit_pack")
    parser.add_argument("--private-roles", type=Path)
    parser.add_argument("--store", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("pack-list", "profile-status", "profile-bind", "role-off", "persona-sources"):
        commands.add_parser(name)
    validate = commands.add_parser("pack-validate")
    validate.add_argument("name", nargs="?")
    create = commands.add_parser("pack-create")
    create.add_argument("name")
    create.add_argument("--scope", required=True, choices=("repo", "home"))
    template = create.add_mutually_exclusive_group()
    template.add_argument("--extends")
    template.add_argument("--from", dest="from_pack")
    switch = commands.add_parser("pack-switch")
    switch.add_argument("name")
    switch.add_argument("--reason", required=True)
    rebind = commands.add_parser("profile-rebind")
    rebind.add_argument("--reason", required=True)
    rebind.add_argument("--pack")
    roles = commands.add_parser("role-list")
    roles.add_argument("--include-private", action="store_true")
    for name in ("role-show", "role-set"):
        command = commands.add_parser(name)
        command.add_argument("name")
        command.add_argument("--allow-private", action="store_true")
        if name == "role-show":
            command.add_argument("--deep", action="store_true")
    writer = commands.add_parser("role-write")
    writer.add_argument("name")
    writer.add_argument("--file", type=Path, required=True)
    writer.add_argument("--scope", choices=("private", "public"), required=True)
    writer.add_argument("--expected-sha256")
    host = commands.add_parser("host-profile")
    host.add_argument("operation", choices=("status", "dormant", "activate"))
    host.add_argument("--client", required=True)
    migrations = commands.add_parser("migrations")
    migrations.add_argument("--all", action="store_true")
    migrations.add_argument("--today", type=date.fromisoformat, default=date.today())
    diagnostic = commands.add_parser("doctor")
    diagnostic.add_argument("--target", dest="repo", type=Path, default=argparse.SUPPRESS)
    diagnostic.add_argument("--source", type=Path, default=argparse.SUPPRESS)
    diagnostic.add_argument("--home", type=Path, default=argparse.SUPPRESS)
    diagnostic.add_argument("--json", action="store_true")
    diagnostic.add_argument("--verbose", "-v", action="store_true")
    diagnostic.add_argument("--quick", action="store_true")
    diagnostic.add_argument("--store", type=Path, default=argparse.SUPPRESS)
    diagnostic.add_argument("--native-store", type=Path)
    foundation = commands.add_parser("scaffold")
    foundation.add_argument("action", choices=("init", "check"))
    foundation.add_argument("--target", type=Path)
    for name in ("name", "pack", "mode", "voice", "compliance"):
        foundation.add_argument("--" + name)
    foundation.add_argument("--copilot", action="store_true")
    foundation.add_argument("--client", action="append", default=[])
    foundation.add_argument("--dry-run", action="store_true")
    foundation.add_argument("--no-memory-pointer", action="store_true")
    foundation.add_argument("--store", type=Path, default=argparse.SUPPRESS)
    migration = commands.add_parser("migrate")
    migration.add_argument("--repo", dest="target", type=Path)
    migration.add_argument("--store", type=Path, default=argparse.SUPPRESS)
    migration.add_argument("--dry-run", action="store_true")
    migration.add_argument("--repair-pointer", action="store_true")
    migration.add_argument("--no-memory-pointer", action="store_true")
    extension = commands.add_parser("extension-pack")
    extension.add_argument("name")
    extension.add_argument("--namespace", required=True)
    extension.add_argument("--workflow", required=True)
    extension.add_argument("--target", type=Path)
    extension.add_argument("--in-place", action="store_true")
    extension.add_argument("--title")
    extension.add_argument("--description")
    extension.add_argument("--store", type=Path, default=argparse.SUPPRESS)
    extension.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        if args.private_roles is not None:
            os.environ["LINTEL_PRIVATE_ROLES_DIR"] = str(destination(args.private_roles))
        config = configuration(args)
        if args.command == "pack-list":
            result = pack_list(config)
        elif args.command == "pack-validate":
            profile, reference = validation_profile(config)
            chain, values, _ = validate_pack(config, args.name or profile["values"]["name"])
            result = {"name": values["name"], "status": "valid", "values": values,
                      "compatibility": [pack["compatibility"] for pack in chain],
                      "profile_reference": reference, "host_activation": "not performed"}
        elif args.command == "pack-create":
            result = create_pack(config, args)
        elif args.command == "pack-switch":
            result = pack_switch(config, args.name, args.reason)
        elif args.command == "profile-bind":
            result = profile_result(bootstrap_profile_context(config))
        elif args.command == "profile-status":
            profile, reference = current_profile(config)
            result = {"reference": reference, "selection": profile["selection"],
                      "effective_pack": profile["values"]["name"]}
        elif args.command == "profile-rebind":
            selected = selected_config(config)
            if args.pack:
                selected = replace(selected, explicit_pack=args.pack)
            result = profile_result(rebind_profile_context(selected, args.reason))
        elif args.command in ("role-set", "role-off"):
            result = set_role(config, args.name if args.command == "role-set" else None,
                              allow_private=getattr(args, "allow_private", False))
        elif args.command == "role-list":
            result = list_roles(config, include_private=args.include_private)
        elif args.command == "role-show":
            profile, _ = current_profile(config)
            _, path, _ = find_role(config, profile, args.name)
            result = read_role(path, args.name, allow_private=args.allow_private, deep=args.deep)
        elif args.command == "role-write":
            result = write_role(config, args)
        elif args.command == "persona-sources":
            result = persona_sources(config)
        elif args.command == "migrations":
            result = migration_inventory(config, include_archived=args.all, today=args.today)
        elif args.command == "doctor":
            result = doctor(config, store=args.store, native_store=args.native_store)
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=True))
            else:
                print_doctor(result)
            return 1 if result["issues"] else 0
        elif args.command == "scaffold":
            result = scaffold(config, args)
        elif args.command == "migrate":
            config, _, profiles = operation_profiles(config, args)
            changes, expected, guards = migration_changes(config.repo, pointer_only=args.repair_pointer,
                                                          memory_pointer=not args.no_memory_pointer)
            result = runtime_publication(config, args, changes, expected, "v5 layout migration",
                                         guards=guards, final_paths=[".claude/lintel-layout.yaml"])
            result.update(profiles)
        elif args.command == "extension-pack":
            result = extension_pack(config, args)
        else:
            from client_capabilities import load_registry, surface_id
            client = surface_id(load_registry(config.source / "lib/cli-tiers.yaml"), args.client)
            if args.operation != "status":
                raise ValueError(f"UNSUPPORTED_HOST_OPERATION: {client} {args.operation} has no shipped "
                                 "enable/disable binding. Use the host's supported controls and verify "
                                 "discovery in a new session; no marker or settings were changed.")
            result = {"surface": client, "status": "unverified", "executed": False,
                      "boundary": "file installation is not plugin activation"}
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0
    except (ValueError, OSError, UnicodeError) as error:
        code = f"{error.code}: " if isinstance(error, ProfileError) else ""
        print(f"li-lifecycle: {code}{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
