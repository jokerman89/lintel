#!/usr/bin/env python3
# component: profile-context
# implements: ADR-0018, ADR-0029
# intent: docs/concepts/pack-resolver.md
# constraints: data-only local manifests; runtime writes restricted to selected home or repo runtime
# last_intent_review: 2026-09-20
"""One pack parser and content-bound profile contract for shell and Python consumers."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, replace
import hashlib
import json
import math
import os
from pathlib import Path, PurePath, PureWindowsPath
import re
import sys
import tempfile
import time
from typing import Union
import uuid


Json = Union[None, bool, int, float, str, list["Json"], dict[str, "Json"]]
KEY = re.compile(r"[A-Za-z_][A-Za-z_0-9-]*\Z")
FIELD = re.compile(r"[A-Za-z_][A-Za-z_0-9-]*(?:\.[A-Za-z_][A-Za-z_0-9-]*)*\Z")
SEMVER = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?\Z"
)
MISSING = object()
MAX_BYTES = 1024 * 1024


class ProfileError(ValueError):
    """A failed policy/context requirement; never a neutral result."""

    def __init__(self, code: str, message: str, *, required: bool = False):
        super().__init__(message)
        self.code = code
        self.required = required


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def _unique(pairs: list[tuple[str, Json]]) -> dict[str, Json]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProfileError("PROFILE_INPUT", "duplicate mapping key")
        result[key] = value
    return result


def _invalid_constant(_: str):
    raise ProfileError("PROFILE_INPUT", "non-finite JSON number")


def read_json(text: str) -> dict[str, Json]:
    try:
        value = json.loads(text, object_pairs_hook=_unique, parse_constant=_invalid_constant)
    except json.JSONDecodeError as exc:
        raise ProfileError("PROFILE_INPUT", f"invalid JSON at line {exc.lineno}") from exc
    if not isinstance(value, dict):
        raise ProfileError("PROFILE_INPUT", "expected a JSON object")
    return value


class ManifestParser:
    """The documented mapping/scalar-list YAML subset, with no executable extensions."""

    def __init__(self, text: str):
        self.lines = []
        ended = False
        for number, raw in enumerate(text.splitlines(), 1):
            if "\t" in raw[:len(raw) - len(raw.lstrip())]:
                self.fail(number, "tabs in indentation")
            line = self.scan(raw, "#")[0].rstrip()
            if not line.strip():
                continue
            if line == "---" and not self.lines:
                continue
            if line == "..." and not ended:
                ended = True
                continue
            if ended or line in ("---", "..."):
                self.fail(number, "multiple YAML documents are unsupported")
            self.lines.append((len(line) - len(line.lstrip(" ")), line.lstrip(" "), number))

    @staticmethod
    def fail(line: int, message: str) -> None:
        raise ProfileError("PACK_INVALID", f"manifest line {line}: {message}")

    @staticmethod
    def scan(text: str, delimiter: str) -> list[str]:
        parts, stack = [], []
        quote = ""
        start = index = 0
        while index < len(text):
            char = text[index]
            if quote:
                if char == "\\" and quote == '"':
                    index += 2
                    continue
                if char == quote:
                    if quote == "'" and text[index:index + 2] == "''":
                        index += 2
                        continue
                    quote = ""
            elif char in "\"'" and (index == 0 or text[index - 1] in " \t:,[{"):
                quote = char
            elif char == delimiter and not stack:
                if delimiter == "#" and index and not text[index - 1].isspace():
                    index += 1
                    continue
                parts.append(text[start:index])
                if delimiter == "#":
                    return parts
                start = index + 1
            elif char in "[{":
                stack.append(char)
            elif char in "]}":
                if not stack or stack.pop() != {"]": "[", "}": "{"}[char]:
                    raise ProfileError("PACK_INVALID", "unbalanced flow collection")
            index += 1
        if quote or stack:
            raise ProfileError("PACK_INVALID", "unterminated quote or flow collection")
        parts.append(text[start:])
        return parts

    @classmethod
    def scalar(cls, text: str) -> Json:
        text = text.strip()
        if text.startswith("'"):
            if len(text) < 2 or not text.endswith("'"):
                raise ProfileError("PACK_INVALID", "unterminated quoted scalar")
            body = text[1:-1]
            if "'" in body.replace("''", ""):
                raise ProfileError("PACK_INVALID", "unsupported single-quote syntax")
            return body.replace("''", "'")
        if text.startswith('"'):
            if any(match.group(1) not in '\\\"nrt' for match in re.finditer(r"\\(.)", text)):
                raise ProfileError("PACK_INVALID", "unsupported quoted escape")
            try:
                value = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ProfileError("PACK_INVALID", "invalid double-quoted scalar") from exc
            if not isinstance(value, str):
                raise ProfileError("PACK_INVALID", "expected quoted string")
            return value
        if text.startswith(("&", "*", "!", "|", ">", "%", "@", "`")):
            raise ProfileError("PACK_INVALID", "unsupported YAML anchor, tag or scalar syntax")
        if text in ("", "~", "null", "Null", "NULL"):
            return None
        if text in ("true", "True", "TRUE"):
            return True
        if text in ("false", "False", "FALSE"):
            return False
        if re.fullmatch(r"-?(?:0|[1-9][0-9]*)", text):
            return int(text)
        if re.fullmatch(r"-?(?:0|[1-9][0-9]*)\.[0-9]+", text):
            value = float(text)
            if not math.isfinite(value):
                raise ProfileError("PACK_INVALID", "non-finite scalar number")
            return value
        if re.search(r":(?:\s|$)", text):
            raise ProfileError("PACK_INVALID", "quote a scalar containing a mapping delimiter")
        return text

    @classmethod
    def flow_items(cls, text: str) -> list[str]:
        if not text.strip():
            return []
        parts = cls.scan(text, ",")
        if not parts[-1].strip():
            parts.pop()
        if any(not part.strip() for part in parts):
            raise ProfileError("PACK_INVALID", "empty flow collection entry")
        return parts

    @classmethod
    def value(cls, text: str, depth: int = 0) -> Json:
        if depth > 40:
            raise ProfileError("PACK_INVALID", "manifest nesting exceeds 40")
        text = text.strip()
        if text.startswith("{"):
            if not text.endswith("}"):
                raise ProfileError("PACK_INVALID", "invalid flow mapping")
            pairs = []
            for part in cls.flow_items(text[1:-1]):
                pieces = cls.scan(part, ":")
                key = pieces[0].strip()
                if len(pieces) < 2 or not KEY.fullmatch(key):
                    raise ProfileError("PACK_INVALID", "mapping keys must be plain identifiers")
                pairs.append((key, cls.value(":".join(pieces[1:]), depth + 1)))
            return _unique(pairs)
        if text.startswith("["):
            if not text.endswith("]"):
                raise ProfileError("PACK_INVALID", "invalid flow list")
            result = []
            for part in cls.flow_items(text[1:-1]):
                if part.strip().startswith(("[", "{")):
                    raise ProfileError("PACK_INVALID", "only scalar list items are supported")
                result.append(cls.scalar(part))
            return result
        return cls.scalar(text)

    def block(self, index: int, indent: int, *, sequence: bool = False, depth: int = 0):
        if depth > 40:
            self.fail(self.lines[index][2], "manifest nesting exceeds 40")
        result = [] if sequence else {}
        while index < len(self.lines):
            spaces, text, number = self.lines[index]
            is_item = text == "-" or text.startswith("- ")
            if spaces < indent or (spaces == indent and sequence != is_item):
                break
            if spaces != indent:
                self.fail(number, "unexpected indentation")
            if sequence:
                item = text[1:].strip()
                if item.startswith(("[", "{")) or re.match(r"[A-Za-z_][\w-]*:\s", item):
                    self.fail(number, "only scalar list items are supported")
                result.append(self.scalar(item))
                index += 1
                continue
            pieces = self.scan(text, ":")
            key = pieces[0].strip()
            if len(pieces) < 2 or not KEY.fullmatch(key):
                self.fail(number, "mapping keys must be plain identifiers")
            if key in result:
                self.fail(number, f"duplicate key: {key}")
            rest = ":".join(pieces[1:]).strip()
            index += 1
            if rest:
                result[key] = self.value(rest)
            elif index < len(self.lines) and (
                self.lines[index][0] > indent or (
                    self.lines[index][0] == indent and self.lines[index][1].startswith("-")
                )
            ):
                child_indent, child_text, _ = self.lines[index]
                value, index = self.block(index, child_indent, sequence=child_text.startswith("-"),
                                          depth=depth + 1)
                result[key] = value
            else:
                result[key] = None
        return result, index

    def parse(self) -> dict[str, Json]:
        if not self.lines:
            return {}
        if self.lines[0][0] != 0:
            self.fail(self.lines[0][2], "root mapping must start in column one")
        value, end = self.block(0, 0)
        if end != len(self.lines):
            self.fail(self.lines[end][2], "unexpected sequence or indentation")
        return value


def parse_manifest(text: str) -> dict[str, Json]:
    return ManifestParser(text).parse()


def field_value(values: dict[str, Json], path: str):
    if not FIELD.fullmatch(path):
        raise ProfileError("PROFILE_INPUT", "invalid dotted field path")
    value = values
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return MISSING
        value = value[part]
    return value


def shell_value(value: Json) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "[" + ", ".join(shell_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return canonical(value).decode("utf-8")
    return str(value)


@dataclass(frozen=True)
class ProfileConfig:
    source: Path
    repo: Path
    home: Path
    packs: Path
    pointer: Path
    context_id: str = ""
    context_file: Path | None = None
    explicit_pack: str = ""
    expected_reference: dict | None = None

    def __post_init__(self):
        for name in ("source", "repo", "home", "packs", "pointer"):
            object.__setattr__(self, name, Path(getattr(self, name)).resolve())
        if self.context_file is not None:
            object.__setattr__(self, "context_file", Path(self.context_file).resolve())
        if not isinstance(self.context_id, str) or not isinstance(self.explicit_pack, str):
            raise ProfileError("PROFILE_INPUT", "context ID and explicit pack must be strings")
        if self.expected_reference is not None:
            validate_profile_reference(self.expected_reference)

    @property
    def requirements(self) -> Path:
        return self.repo / ".claude/profile-requirements.json"

    @property
    def selected(self) -> Path:
        return self.repo / ".claude/runtime/profiles/selected.json"


class Inputs:
    def __init__(self):
        self.files = {}

    def read(self, path: Path, *, optional: bool = False) -> bytes | None:
        path = path.resolve()
        try:
            with path.open("rb") as stream:
                data = stream.read(MAX_BYTES + 1)
        except FileNotFoundError as exc:
            self.files[path.as_posix()] = None
            if optional:
                return None
            raise ProfileError("PACK_INVALID", f"required input is missing: {path}") from exc
        except OSError as exc:
            raise ProfileError("PROFILE_IO", f"cannot read input: {path}: {exc.strerror}") from exc
        if len(data) > MAX_BYTES:
            raise ProfileError("PROFILE_INPUT", f"input exceeds {MAX_BYTES} bytes: {path}")
        self.files[path.as_posix()] = "sha256:" + hashlib.sha256(data).hexdigest()
        return data

    def text(self, path: Path, *, optional: bool = False) -> str | None:
        data = self.read(path, optional=optional)
        if data is None:
            return None
        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ProfileError("PROFILE_INPUT", f"input is not UTF-8: {path}") from exc

    def verify(self) -> None:
        again = Inputs()
        for path in self.files:
            again.read(Path(path), optional=True)
        if again.files != self.files:
            raise ProfileError("PROFILE_DRIFT", "profile inputs changed during resolution; retry explicitly")

    def references(self) -> list[dict]:
        return [{"path": path, "digest": value} for path, value in sorted(self.files.items())]


def pack_directory(config: ProfileConfig, name: str) -> Path:
    if not KEY.fullmatch(name):
        raise ProfileError("PACK_INVALID", "pack name must be a filesystem-safe identifier")
    for root in (config.packs, config.repo / "packs", config.source / "packs"):
        candidate = root / name
        if candidate.is_dir():
            return candidate.resolve()
    raise ProfileError("PACK_INVALID", f"pack or parent not found: {name}")


def select_profile(config: ProfileConfig, inputs: Inputs) -> dict:
    try:
        text = inputs.text(config.requirements, optional=True)
        requirement = read_json(text) if text is not None else None
        if requirement is not None and (
            set(requirement) != {"schema_version", "required_pack"}
            or type(requirement["schema_version"]) is not int
            or requirement["schema_version"] != 1
            or not isinstance(requirement["required_pack"], str)
            or not KEY.fullmatch(requirement["required_pack"])
        ):
            raise ProfileError("PROFILE_INPUT", "invalid profile-requirements schema")
    except ProfileError as exc:
        raise ProfileError("PROFILE_REQUIRED", f"repository requirement cannot load: {exc}",
                           required=True) from exc
    pointer = inputs.text(config.pointer, optional=True)
    selected = pointer.strip() if pointer else ""
    if requirement:
        selected = requirement["required_pack"]
        if config.explicit_pack and config.explicit_pack != selected:
            raise ProfileError("PROFILE_REQUIRED", "explicit selection conflicts with repository required pack",
                               required=True)
        mode, source = "required", config.requirements.as_posix()
    elif config.explicit_pack:
        selected, mode, source = config.explicit_pack, "required", "invocation:LINTEL_PROFILE_PACK"
    elif selected:
        mode, source = "optional", config.pointer.as_posix()
    else:
        selected, mode, source = "_default", "neutral", "bundled-neutral"
    return {"requested": selected, "mode": mode, "source": source, "status": "loaded",
            "explicit_pack": config.explicit_pack or None}


def _semver(value: str) -> tuple:
    match = SEMVER.fullmatch(value)
    if not match:
        raise ProfileError("PACK_COMPATIBILITY", "expected a full semantic version")
    pre = match.group(4).split(".") if match.group(4) else []
    if any(part.isdigit() and len(part) > 1 and part.startswith("0") for part in pre):
        raise ProfileError("PACK_COMPATIBILITY", "invalid semantic prerelease version")
    return tuple(int(match.group(i)) for i in (1, 2, 3)), pre


def _compare_version(left: str, right: str) -> int:
    core_left, pre_left = _semver(left)
    core_right, pre_right = _semver(right)
    if core_left != core_right:
        return 1 if core_left > core_right else -1
    if not pre_left or not pre_right:
        return (not pre_left) - (not pre_right)
    for a, b in zip(pre_left, pre_right):
        if a == b:
            continue
        if a.isdigit() and b.isdigit():
            return 1 if int(a) > int(b) else -1
        if a.isdigit() != b.isdigit():
            return -1 if a.isdigit() else 1
        return 1 if a > b else -1
    return (len(pre_left) > len(pre_right)) - (len(pre_left) < len(pre_right))


def version_satisfies(actual: str, requirement: str) -> bool:
    _semver(actual)
    if not isinstance(requirement, str) or not requirement.strip():
        raise ProfileError("PACK_COMPATIBILITY", "empty or non-string version range")
    terms = re.split(r"[\s,]+", requirement.strip())
    for term in terms:
        match = re.fullmatch(r"(>=|<=|>|<|==|=)?(.+)", term)
        operator, wanted = match.group(1) or "=", match.group(2)
        comparison = _compare_version(actual, wanted)
        accepted = {"=": comparison == 0, "==": comparison == 0, ">": comparison > 0,
                    "<": comparison < 0, ">=": comparison >= 0, "<=": comparison <= 0}
        if not accepted[operator]:
            return False
    return True


def compatibility_source(config: ProfileConfig, inputs: Inputs) -> dict:
    schema = parse_manifest(inputs.text(config.source / "lib/pack-schema.yaml"))
    support = schema.get("runtime_compatibility")
    if not isinstance(support, dict) or not isinstance(support.get("schema_versions"), list) \
            or not isinstance(support.get("capabilities"), dict):
        raise ProfileError("PACK_COMPATIBILITY", "installed pack schema has no compatibility contract")
    product_text = inputs.text(config.source / ".claude-plugin/plugin.json", optional=True)
    product = read_json(product_text).get("version") if product_text is not None else None
    if product is not None:
        if not isinstance(product, str):
            raise ProfileError("PACK_COMPATIBILITY", "invalid installed product version")
        _semver(product)
    return {"schema_versions": support["schema_versions"], "capabilities": support["capabilities"],
            "product_version": product}


def check_compatibility(manifest: dict, supported: dict, name: str) -> dict:
    schema = manifest.get("schema_version", "1")
    if not isinstance(schema, str) or schema not in supported["schema_versions"]:
        raise ProfileError("PACK_COMPATIBILITY", f"pack={name}: unsupported pack schema")
    legacy = manifest.get("requires_lintel")
    if legacy is not None and legacy != ">=4.0.0":
        raise ProfileError("PACK_COMPATIBILITY",
                           f"pack={name}: migrate legacy requires_lintel to product/capability requirements")
    product_range = manifest.get("requires_lintel_product")
    if product_range is not None and (
        supported["product_version"] is None
        or not version_satisfies(supported["product_version"], product_range)
    ):
        raise ProfileError("PACK_COMPATIBILITY", f"pack={name}: incompatible or unknown product version")
    required = manifest.get("requires_capabilities", {})
    if not isinstance(required, dict):
        raise ProfileError("PACK_COMPATIBILITY", f"pack={name}: capability requirements must be a mapping")
    for feature, constraint in required.items():
        actual = supported["capabilities"].get(feature)
        if not isinstance(actual, str) or not version_satisfies(actual, constraint):
            raise ProfileError("PACK_COMPATIBILITY", f"pack={name}: incompatible capability {feature}")
    return {"name": name, "schema_version": schema, "legacy_schema": "schema_version" not in manifest,
            "legacy_marker": legacy, "product_version": supported["product_version"],
            "product_requirement": product_range, "capabilities": required, "status": "compatible"}


def load_chain(config: ProfileConfig, name: str, inputs: Inputs, supported: dict) -> list[dict]:
    chain, seen = [], set()
    while True:
        if name in seen:
            raise ProfileError("PACK_INVALID", "extends cycle detected")
        if len(chain) > 10:
            raise ProfileError("PACK_INVALID", "extends exceeds maximum depth 10")
        seen.add(name)
        manifest_path = pack_directory(config, name) / "pack.yaml"
        manifest = parse_manifest(inputs.text(manifest_path))
        if manifest.get("name") != name:
            raise ProfileError("PACK_INVALID", f"pack={name}: name must match its directory")
        version = manifest.get("version")
        if not isinstance(version, str):
            raise ProfileError("PACK_INVALID", f"pack={name}: version must be a semantic-version string")
        _semver(version)
        compatibility = check_compatibility(manifest, supported, name)
        chain.append({"name": name, "version": version, "path": manifest_path.as_posix(),
                      "digest": inputs.files[manifest_path.resolve().as_posix()],
                      "values": manifest, "compatibility": compatibility})
        parent = manifest.get("extends")
        if parent is None or parent == "":
            break
        if not isinstance(parent, str) or not KEY.fullmatch(parent):
            raise ProfileError("PACK_INVALID", f"pack={name}: extends must be one pack name or null")
        name = parent
    chain.reverse()
    return chain


def _origin(pack: dict, fallback: bool = False) -> dict:
    return {key: pack[key] for key in ("name", "version", "path", "digest")} | {"fallback": fallback}


def _origins(value: Json, path: str, origin: dict, result: dict) -> None:
    result[path] = dict(origin)
    if isinstance(value, dict):
        for key, child in value.items():
            _origins(child, f"{path}.{key}", origin, result)


def merge_chain(chain: list[dict]) -> tuple[dict, dict]:
    values, provenance = {}, {}
    for pack in chain:
        for key, value in pack["values"].items():
            values[key] = deepcopy(value)
            provenance = {path: source for path, source in provenance.items()
                          if path != key and not path.startswith(key + ".")}
            _origins(value, key, _origin(pack), provenance)
    return values, provenance


def validate_values(values: dict) -> None:
    for path in ("voice.default_tier", "compliance.mode", "navigation.default_workflow"):
        value = field_value(values, path)
        if not isinstance(value, str) or not value:
            raise ProfileError("PACK_INVALID", f"missing required scalar: {path}")
    if field_value(values, "compliance.mode") not in ("hard", "advisory", "off"):
        raise ProfileError("PACK_INVALID", "unsupported compliance.mode")
    extension = field_value(values, "extension.is_extension")
    if extension is True or extension in ("true", "yes", "on"):
        for path in ("extension.namespace", "extension.workflow"):
            value = field_value(values, path)
            if not isinstance(value, str) or not value or value in ("null", "~"):
                raise ProfileError("PACK_INVALID", f"extension pack requires {path}")
    for path in ("compliance.hooks", "voice.gates_active", "navigation.high_risk_workflows"):
        value = field_value(values, path)
        if value is not MISSING and (
            not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value)
        ):
            raise ProfileError("PACK_INVALID", f"{path} must be a list of nonempty strings")


def _fill_defaults(values: dict, defaults: dict, origins: dict, default_origins: dict, prefix: str = ""):
    for key, value in defaults.items():
        path = prefix + key
        if key not in values:
            values[key] = deepcopy(value)
            for source_path, origin in default_origins.items():
                if source_path == path or source_path.startswith(path + "."):
                    origins[source_path] = dict(origin, fallback=True)
        elif isinstance(values[key], dict) and isinstance(value, dict):
            _fill_defaults(values[key], value, origins, default_origins, path + ".")


def validate_pack(config: ProfileConfig, name: str) -> tuple[list[dict], dict, dict]:
    inputs = Inputs()
    supported = compatibility_source(config, inputs)
    chain = load_chain(config, name, inputs, supported)
    values, origins = merge_chain(chain)
    validate_values(values)
    inputs.verify()
    return chain, values, origins


def resolve_profile(config: ProfileConfig) -> dict:
    """Resolve current data without mutating a selected context."""
    inputs = Inputs()
    selection = select_profile(config, inputs)
    try:
        supported = compatibility_source(config, inputs)
        neutral_chain = load_chain(config, "_default", inputs, supported)
        defaults, default_origins = merge_chain(neutral_chain)
        validate_values(defaults)
    except ProfileError as exc:
        raise ProfileError("PROFILE_BASELINE", f"neutral baseline cannot load: {exc}",
                           required=selection["mode"] == "required") from exc
    try:
        chain = neutral_chain if selection["requested"] == "_default" else load_chain(
            config, selection["requested"], inputs, supported)
        values, provenance = merge_chain(chain)
        validate_values(values)
    except ProfileError as exc:
        if selection["mode"] != "optional":
            raise ProfileError("PROFILE_REQUIRED", f"required profile cannot load: {exc}", required=True) from exc
        if exc.code not in ("PACK_INVALID", "PACK_COMPATIBILITY", "PROFILE_INPUT"):
            raise
        selection["status"] = "fallback"
        selection["diagnostic"] = {"code": exc.code, "message": str(exc)}
        chain, values, provenance = neutral_chain, deepcopy(defaults), deepcopy(default_origins)
    _fill_defaults(values, defaults, provenance, default_origins)
    inputs.verify()
    identity = lambda pack: {key: pack[key] for key in ("name", "version", "path", "digest")}
    unique_manifests = {pack["path"]: pack for pack in neutral_chain + chain}
    return {
        "roots": {"source": config.source.as_posix(), "repo": config.repo.as_posix(),
                  "packs": config.packs.as_posix(), "pointer": config.pointer.as_posix()},
        "selection": selection, "ancestry": [identity(pack) for pack in chain],
        "baseline": [identity(pack) for pack in neutral_chain],
        "values": values, "provenance": provenance, "inputs": inputs.references(),
        "compatibility": [pack["compatibility"] for pack in unique_manifests.values()],
    }


def _context_id(value: str) -> str:
    if not value or len(value) > 200 or any(ord(char) < 32 for char in value):
        raise ProfileError("PROFILE_CONTEXT_REQUIRED", "supply a stable nonempty work/session context ID")
    return value


def context_path(config: ProfileConfig) -> Path:
    if config.expected_reference is not None:
        config = _reference_selection(config.expected_reference, config)
    if config.context_file is not None:
        path = config.context_file.resolve()
    else:
        _context_id(config.context_id)
        key = hashlib.sha256(canonical([config.repo.as_posix(), config.context_id])).hexdigest()
        path = config.home / "sessions/profiles" / key / "current-profile.json"
    _runtime_path(config, path)
    return path


def _path_identity(path: PurePath) -> tuple[str, ...]:
    """Compare filesystem spellings without changing the paths used for I/O."""
    identity = path
    if isinstance(path, PureWindowsPath):
        text = str(path)
        if text.startswith("\\\\?\\"):
            suffix = text[4:]
            if suffix[:4].lower() == "unc\\":
                text = "\\\\" + suffix[4:]
            elif re.match(r"^[A-Za-z]:\\", suffix):
                text = suffix
            else:
                raise ProfileError("PROFILE_IO", "unsupported Windows filesystem namespace")
        identity = PureWindowsPath(text)
        components = identity.parts[1:]
        if identity.drive.startswith("\\\\"):
            share = identity.drive[2:].split("\\")
            if len(share) != 2:
                raise ProfileError("PROFILE_IO", "runtime UNC identity requires a server and share")
            components = (*share, *components)
        elif not re.fullmatch(r"[A-Za-z]:", identity.drive):
            raise ProfileError("PROFILE_IO", "runtime identity requires an absolute filesystem drive")
        if any(
            part in ("", ".", "..") or part.endswith((".", " "))
            or re.search(r'[\x00-\x1f<>:"|?*]', part)
            or PureWindowsPath(part).is_reserved()
            for part in components
        ):
            raise ProfileError("PROFILE_IO", "ambiguous or non-filesystem Windows path component")
    if not identity.is_absolute() or ".." in identity.parts:
        raise ProfileError("PROFILE_IO", "runtime identity must be absolute and traversal-free")
    return identity.parts


def _runtime_path(config: ProfileConfig, path: Path) -> None:
    if isinstance(path, PureWindowsPath):
        _path_identity(path)
    resolved = _path_identity(path.resolve())
    # Approved roots were resolved at configuration time. Do not follow a newly
    # redirected boundary or case-fold distinct case-sensitive Windows siblings.
    roots = (_path_identity(config.home), _path_identity(config.repo / ".claude/runtime"))
    if not any(resolved[:len(root)] == root for root in roots):
        raise ProfileError("PROFILE_IO", "profile runtime must stay in selected LINTEL_HOME or target runtime")


def _load_json_file(path: Path) -> dict:
    text = Inputs().text(path)
    return read_json(text)


def _record(profile: dict, context_id: str = "", generation: int = 0,
            previous: dict | None = None, reason: str = "") -> dict:
    return {"schema_version": 1, "context_id": context_id or None, "generation": generation,
            "digest": digest(profile), "profile": profile, "previous": previous, "reason": reason}


def validate_profile_reference(reference: dict) -> dict:
    keys = {"schema_version", "context_id", "generation", "digest", "name", "version"}
    if not isinstance(reference, dict) or set(reference) != keys or \
            type(reference["schema_version"]) is not int or reference["schema_version"] != 1 or \
            type(reference["generation"]) is not int or reference["generation"] < 1 or \
            not isinstance(reference["context_id"], str) or \
            not isinstance(reference["digest"], str) or \
            not re.fullmatch(r"sha256:[0-9a-f]{64}", reference["digest"]) or \
            not isinstance(reference["name"], str) or not KEY.fullmatch(reference["name"]) or \
            not isinstance(reference["version"], str):
        raise ProfileError("PROFILE_REFERENCE_MISMATCH", "invalid profile reference schema")
    _context_id(reference["context_id"])
    _semver(reference["version"])
    return reference


def profile_reference(record: dict) -> dict:
    _context_id(record["context_id"] or "")
    return validate_profile_reference({
        "schema_version": 1, "context_id": record["context_id"], "generation": record["generation"],
        "digest": record["digest"], "name": record["profile"]["values"]["name"],
        "version": record["profile"]["values"]["version"],
    })


def _load_record(path: Path) -> dict:
    try:
        record = _load_json_file(path)
        if set(record) != {"schema_version", "context_id", "generation", "digest", "profile", "previous", "reason"} \
                or type(record["schema_version"]) is not int or record["schema_version"] != 1 \
                or not isinstance(record["profile"], dict) or not isinstance(record["reason"], str) \
                or record["digest"] != digest(record["profile"]):
            raise ProfileError("PROFILE_CONTEXT_INVALID", "invalid or corrupted profile context")
        profile = record["profile"]
        if not isinstance(profile.get("selection"), dict) or not isinstance(profile.get("values"), dict):
            raise ProfileError("PROFILE_CONTEXT_INVALID", "missing structured profile")
        profile_reference(record)
        if record["previous"] is not None:
            validate_profile_reference(record["previous"])
        return record
    except (ProfileError, KeyError, TypeError) as exc:
        raise ProfileError("PROFILE_CONTEXT_INVALID", f"cannot verify stored profile context: {exc}") from exc


def _latest_history_record(current: Path, context_id: str) -> dict | None:
    history = current.parent / "history"
    if not history.exists():
        return None
    records = {}
    for path in history.iterdir():
        if not path.is_file() or path.suffix != ".json":
            raise ProfileError("PROFILE_CONTEXT_INVALID", "context history contains an incomplete record")
        record = _load_record(path)
        reference = profile_reference(record)
        if record["context_id"] != context_id or path != _history_path(current, reference):
            raise ProfileError("PROFILE_CONTEXT_INVALID", "context history identity or filename differs")
        if record["generation"] in records:
            raise ProfileError("PROFILE_CONTEXT_INVALID", "context history has conflicting generations")
        records[record["generation"]] = record
    return records[max(records)] if records else None


def _load_current_record(path: Path) -> dict:
    record = _load_record(path)
    latest = _latest_history_record(path, record["context_id"])
    if latest is not None and (
        latest["generation"] > record["generation"]
        or latest["generation"] == record["generation"] and latest != record
    ):
        raise ProfileError("PROFILE_REFERENCE_MISMATCH", "current profile differs from retained generation",
                           required=latest["profile"]["selection"]["mode"] == "required")
    return record


@contextmanager
def _lock(config: ProfileConfig, path: Path):
    _runtime_path(config, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".lock")
    deadline = time.monotonic() + 5
    while True:
        try:
            lock.mkdir()
            break
        except FileExistsError as exc:
            if time.monotonic() >= deadline:
                raise ProfileError("PROFILE_CONTEXT_BUSY", "context is locked; inspect interrupted writer before retry") from exc
            time.sleep(0.05)
    try:
        yield
    finally:
        lock.rmdir()


def _write_json(config: ProfileConfig, path: Path, value: dict) -> None:
    _runtime_path(config, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, prefix=".profile-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(canonical(value) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _retain_record(config: ProfileConfig, path: Path, record: dict) -> None:
    archive = _history_path(path, profile_reference(record))
    if archive.exists():
        if _load_record(archive) != record:
            raise ProfileError("PROFILE_CONTEXT_INVALID", "existing history conflicts; evidence is preserved")
        return
    _write_json(config, archive, record)


def _restore_selection(config: ProfileConfig, record: dict) -> ProfileConfig:
    explicit = record["profile"]["selection"].get("explicit_pack")
    return replace(config, explicit_pack=explicit) if not config.explicit_pack and explicit else config


def _verify_record(config: ProfileConfig, record: dict) -> dict:
    if config.context_id and record["context_id"] != config.context_id:
        raise ProfileError("PROFILE_REFERENCE_MISMATCH", "selected context ID does not match stored context")
    try:
        current = resolve_profile(_restore_selection(config, record))
    except ProfileError as exc:
        raise ProfileError("PROFILE_DRIFT", f"bound profile no longer resolves ({exc.code}); rebind and replan",
                           required=record["profile"]["selection"]["mode"] == "required") from exc
    if digest(current) != record["digest"]:
        raise ProfileError("PROFILE_DRIFT", "bound profile inputs changed; explicit rebind and replan required",
                           required=record["profile"]["selection"]["mode"] == "required")
    return record


def load_profile_context(config: ProfileConfig, *, create: bool = False) -> dict:
    """Load/verify an existing pin, or explicitly allow first binding."""
    if config.expected_reference is not None:
        return verify_profile_reference(config.expected_reference, config)
    if not config.context_id and config.context_file is None:
        if create:
            return _record(resolve_profile(config))
        raise ProfileError("PROFILE_CONTEXT_REQUIRED", "bootstrap or select a stable profile context first")
    path = context_path(config)
    if path.is_file():
        return _verify_record(config, _load_current_record(path))
    if not create or config.context_file is not None:
        raise ProfileError("PROFILE_CONTEXT_MISSING", "selected context is missing; bind explicitly, not as resume")
    with _lock(config, path):
        if path.is_file():
            return _verify_record(config, _load_current_record(path))
        history = path.parent / "history"
        retained = history.exists() and any(history.iterdir())
        if config.selected.exists():
            selected = validate_profile_reference(_load_json_file(config.selected))
            retained = retained or selected["context_id"] == config.context_id
        if retained:
            raise ProfileError("PROFILE_CONTEXT_MISSING",
                               "context was already bound; explicit history-backed recovery is required",
                               required=True)
        record = _record(resolve_profile(config), _context_id(config.context_id), 1, reason="initial binding")
        _retain_record(config, path, record)
        _write_json(config, path, record)
        return record


def _reference_selection(reference: dict, config: ProfileConfig) -> ProfileConfig:
    validate_profile_reference(reference)
    if config.context_id and config.context_id != reference["context_id"]:
        raise ProfileError("PROFILE_REFERENCE_MISMATCH", "handoff names a different context")
    return replace(config, context_id=reference["context_id"], expected_reference=None)


def verify_profile_reference(reference: dict, config: ProfileConfig) -> dict:
    """Verify both live policy inputs and the expected producer identity, without rebinding."""
    selected = _reference_selection(reference, config)
    record = load_profile_context(selected)
    if profile_reference(record) != reference:
        raise ProfileError("PROFILE_REFERENCE_MISMATCH", "handoff profile generation or content differs",
                           required=record["profile"]["selection"]["mode"] == "required")
    return record


def bootstrap_profile_context(config: ProfileConfig) -> dict:
    """Select a durable repository work context when the host supplies no stable ID."""
    if config.context_id or config.context_file or config.expected_reference is not None:
        return load_profile_context(config, create=True)
    with _lock(config, config.selected):
        if config.selected.exists():
            return verify_profile_reference(_load_json_file(config.selected), config)
        selected = replace(config, context_id="repo-work:" + str(uuid.uuid4()))
        record = load_profile_context(selected, create=True)
        _write_json(config, config.selected, profile_reference(record))
        return record


def _history_path(current: Path, reference: dict) -> Path:
    return current.parent / "history" / f"{reference['generation']}-{reference['digest'][7:]}.json"


def rebind_profile_context(config: ProfileConfig, reason: str) -> dict:
    if not reason.strip() or len(reason) > 1000:
        raise ProfileError("PROFILE_INPUT", "rebind requires a nonempty reason (at most 1000 characters)")
    expected = config.expected_reference
    if expected is not None:
        config = _reference_selection(expected, config)
    path = context_path(config)
    # Match bootstrap's lock order. No successful rebind may expose an older
    # selected generation after a later context writer has committed.
    with _lock(config, config.selected):
        with _lock(config, path):
            if path.is_file():
                old = _load_current_record(path)
            else:
                old = _latest_history_record(path, config.context_id)
                if old is None:
                    raise ProfileError("PROFILE_CONTEXT_MISSING",
                                       "cannot recover a missing context without retained history")
            previous = profile_reference(old)
            if expected is not None and previous != expected:
                raise ProfileError("PROFILE_REFERENCE_MISMATCH", "rebind must name the current generation",
                                   required=old["profile"]["selection"]["mode"] == "required")
            if config.context_id and old["context_id"] != config.context_id:
                raise ProfileError("PROFILE_REFERENCE_MISMATCH", "rebind names a different context")
            update_selection = False
            if config.selected.exists():
                selected = validate_profile_reference(_load_json_file(config.selected))
                update_selection = selected["context_id"] == old["context_id"]
                if update_selection and selected != previous:
                    historical = _history_path(path, selected)
                    if not historical.is_file() or profile_reference(_load_record(historical)) != selected:
                        raise ProfileError("PROFILE_REFERENCE_MISMATCH",
                                           "selected reference is not backed by this context's history")
            profile = resolve_profile(_restore_selection(config, old))
            new = _record(profile, old["context_id"], old["generation"] + 1, previous, reason)
            _retain_record(config, path, old)
            _retain_record(config, path, new)
            _write_json(config, path, new)
            if update_selection:
                _write_json(config, config.selected, profile_reference(new))
    return new


def required_policy(record: dict) -> dict:
    """P05 policy-load bridge: loading policy is not evidence its controls passed."""
    profile = record["profile"]
    required = profile["selection"]["mode"] == "required"
    return {"required": required, "status": "loaded" if required else "not_required",
            "source": profile["selection"]["source"], "version": profile["values"]["version"],
            "applicability": "applicable" if required else "not_applicable"}


def _config(args) -> ProfileConfig:
    source = Path(args.source).resolve()
    repo = Path(args.repo).resolve()
    home = Path(args.home).resolve()
    return ProfileConfig(source, repo, home, Path(args.packs).resolve(), Path(args.pointer).resolve(),
                         args.context or "", Path(args.context_file).resolve() if args.context_file else None,
                         args.pack or "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--home", required=True)
    parser.add_argument("--packs", required=True)
    parser.add_argument("--pointer", required=True)
    parser.add_argument("--context", default="")
    parser.add_argument("--context-file", default="")
    parser.add_argument("--pack", default="")
    parser.add_argument("--reference", default="")
    parser.add_argument("operation", choices=(
        "field", "field-json", "provenance", "true", "nullable", "loaded", "selected",
        "validate", "compatibility", "chain", "chain-field", "dir", "yaml-field",
        "context", "reference", "bind", "verify", "rebind", "bootstrap",
        "context-id", "context-path", "required-policy",
    ))
    parser.add_argument("arguments", nargs="*")
    args = parser.parse_args()
    config = _config(args)
    operation, arguments = args.operation, args.arguments
    try:
        if args.reference:
            config = replace(config, expected_reference=read_json(args.reference))
        counts = {
            "field": (1,), "field-json": (1,), "provenance": (1,), "true": (1,), "nullable": (1,),
            "loaded": (0,), "selected": (0,), "validate": (0, 1), "compatibility": (0, 1),
            "chain": (1,), "chain-field": (2,), "dir": (1,), "yaml-field": (2,), "context": (0,),
            "reference": (0,), "bind": (1,), "verify": (0, 1), "rebind": (1,), "bootstrap": (0,),
            "context-id": (0,), "context-path": (0,), "required-policy": (0,),
        }
        if len(arguments) not in counts[operation]:
            raise ProfileError("PROFILE_INPUT", "invalid operation arguments")
        if operation == "yaml-field" and len(arguments) == 2:
            text = Inputs().text(Path(arguments[0]))
            value = field_value(parse_manifest(text), arguments[1])
            if value is MISSING:
                return 1
            print(shell_value(value), end="")
            return 0
        if operation == "dir" and len(arguments) == 1:
            print(pack_directory(config, arguments[0]).as_posix(), end="")
            return 0
        if operation == "selected":
            selection = load_profile_context(config)["profile"]["selection"] \
                if config.expected_reference is not None else select_profile(config, Inputs())
            print(selection["requested"], end="")
            return 0
        if operation in ("validate", "compatibility", "chain", "chain-field"):
            if arguments and not arguments[0].strip():
                raise ProfileError("PROFILE_INPUT", "pack or ancestry must not be empty")
            name = arguments[0].split()[-1] if arguments else "_default"
            chain, values, _ = validate_pack(config, name)
            if operation == "chain":
                print(" ".join(pack["name"] for pack in chain), end="")
            elif operation == "compatibility":
                print(canonical([pack["compatibility"] for pack in chain]).decode("utf-8"))
            elif operation == "chain-field":
                if len(arguments) != 2 or arguments[0].split() != [pack["name"] for pack in chain]:
                    raise ProfileError("PROFILE_INPUT", "chain must match the declared ancestry")
                value = field_value(values, arguments[1])
                if value is MISSING:
                    return 1
                print(shell_value(value), end="")
            return 0
        if operation == "context-path":
            print(context_path(config).as_posix(), end="")
            return 0
        if operation == "context-id":
            if config.expected_reference is None:
                raise ProfileError("PROFILE_CONTEXT_REQUIRED", "context identity requires a verified reference")
            print(_reference_selection(config.expected_reference, config).context_id, end="")
            return 0
        if operation == "bootstrap":
            record = bootstrap_profile_context(config)
        elif operation == "bind":
            if len(arguments) != 1:
                raise ProfileError("PROFILE_CONTEXT_REQUIRED", "bind requires a stable context ID")
            target = _context_id(arguments[0])
            expected = config.expected_reference
            if expected is not None and target != expected["context_id"]:
                expected = None
            config = replace(config, context_id=target, expected_reference=expected)
            record = load_profile_context(config, create=True)
        elif operation == "verify":
            record = verify_profile_reference(_load_json_file(Path(arguments[0])), config) if arguments \
                else load_profile_context(config)
        elif operation == "rebind":
            record = rebind_profile_context(config, arguments[0] if len(arguments) == 1 else "")
        else:
            record = load_profile_context(config, create=True)
        selection = record["profile"]["selection"]
        if selection["status"] == "fallback":
            print("[lintel/profile] OPTIONAL_PROFILE_FALLBACK: optional preference did not load; "
                  "using validated neutral baseline", file=sys.stderr)
        if operation in ("bind", "verify", "rebind", "reference", "bootstrap"):
            print(canonical(profile_reference(record)).decode("utf-8"))
        elif operation == "context":
            print(canonical(record).decode("utf-8"))
        elif operation == "required-policy":
            print(canonical(required_policy(record)).decode("utf-8"))
        elif operation == "loaded":
            print(record["profile"]["values"]["name"], end="")
        elif operation in ("field", "field-json", "provenance", "true", "nullable") and len(arguments) == 1:
            value = field_value(record["profile"]["values"], arguments[0])
            if value is MISSING:
                return 0 if operation in ("field", "nullable") else 1
            if operation == "provenance":
                print(canonical(record["profile"]["provenance"][arguments[0]]).decode("utf-8"))
            elif operation == "field-json":
                print(canonical(value).decode("utf-8"))
            elif operation == "true":
                return 0 if value is True or value in ("true", "yes", "on") else 1
            else:
                print("" if operation == "nullable" and value is None else shell_value(value), end="")
        else:
            raise ProfileError("PROFILE_INPUT", "invalid operation arguments")
        return 0
    except ProfileError as exc:
        if operation == "required-policy":
            # Losing a selected reference cannot prove its policy was optional.
            required = (
                exc.required or config.requirements.exists() or bool(config.explicit_pack)
                or bool(args.reference) or bool(config.context_id or config.context_file)
            )
            print(canonical({"required": required, "status": "error",
                             "source": config.requirements.as_posix() if config.requirements.exists()
                             else "invocation" if config.explicit_pack else "profile-context",
                             "version": "unknown", "applicability": "unknown"}).decode("utf-8"))
        print(canonical({"schema_version": 1, "status": "error", "code": exc.code,
                         "message": str(exc)}).decode("utf-8"), file=sys.stderr)
        return 2
    except OSError as exc:
        print(canonical({"schema_version": 1, "status": "error", "code": "PROFILE_IO",
                         "message": f"local profile I/O failed: {exc.strerror}"}).decode("utf-8"), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
