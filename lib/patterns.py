#!/usr/bin/env python3
# component: reusable-patterns-core
# implements: ADR-0038, ADR-0029, ADR-0028
# intent: .claude/plans/reusable-patterns/spec.md
# constraints: stdlib only; data-only records; never executes, fetches or shells out; reads only contained files under supplied roots
# last_intent_review: 2026-09-28
"""Single validator and resolver for data-only reusable patterns.

The public contract is recorded in `.claude/plans/reusable-patterns/contract.md`.
Consumers import this module (or call `bin/li-pattern.py`); they never re-implement
validation. Nothing read here is executed, fetched or interpolated into a shell.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import datetime as _dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

__all__ = (
    "SCHEMA_VERSION", "LIMITS", "EXIT_CODES", "PatternError", "Reader",
    "ExactRef", "Clause", "SourceRecord", "Asset", "Approval", "Selector", "Pattern",
    "CatalogEntry", "CatalogInclude", "LifecycleEvent", "Revocation", "Binding", "Catalog",
    "Context", "InvocationRef", "Override", "ExceptionRecord", "PackAncestor", "PackContext",
    "Roots", "SelectorDecision",
    "parse_json", "canonical_json", "content_digest", "emit_json", "exit_code",
    "validate_relative_path", "contained_path",
    "parse_pattern", "parse_catalog", "parse_bindings", "parse_context", "parse_refs",
    "parse_overrides", "parse_exceptions", "parse_pack_context", "parse_roots",
    "parse_exact_ref", "parse_ref_text", "evaluate_selector",
    "pack_context_from_profile", "build_envelope", "load_sources",
    "list_catalogs", "show_pattern", "check_document", "check_sources", "resolve",
    "build_lock", "write_lock", "parse_lock", "selection_digest", "verify_lock",
    "parse_task_map", "map_lock", "project_package", "capture", "index_source", "approve",
    "asset_refs", "read_asset", "dependents", "record_lifecycle", "update",
    "parse_attestations", "merge_attestations", "apply_change", "record_attestations", "remove",
    "parse_review_evidence", "review_coverage", "export_bundle", "import_bundle",
)

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Limits:
    pattern_bytes: int = 64 * 1024
    catalog_bytes: int = 2 * 1024 * 1024
    input_bytes: int = 256 * 1024
    catalog_entries: int = 2000
    source_catalogs: int = 32
    include_depth: int = 16
    selected_patterns: int = 256
    asset_bytes: int = 4 * 1024 * 1024
    bundle_bytes: int = 32 * 1024 * 1024
    json_depth: int = 64
    candidates: int = 5
    candidate_summary: int = 240
    advisory_summary_total: int = 1200
    context_budget: int = 24000


LIMITS = Limits()

# Exit codes are part of the public contract (spec section 6).
EXIT_CODES = {
    "ok": 0, "ready": 0, "empty": 0,
    "invalid": 2, "needs-context": 3, "conflict": 4, "unavailable": 5,
    "collision": 6, "review-unmet": 7,
}
_STATUS_RANK = {"ready": 0, "empty": 0, "ok": 0, "needs-context": 1, "conflict": 2,
                "unavailable": 3, "collision": 4, "review-unmet": 4, "invalid": 5}

NAMESPACED_ID = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*)+\Z")
SETTING = re.compile(r"[a-z][a-z0-9-]*(?:\.[a-z0-9][a-z0-9-]*)+\Z")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")
CLAUSE_ID = re.compile(r"[A-Z0-9-]+\Z")
SELECTOR_KEY = re.compile(r"[a-z][a-z0-9_.-]*\Z")
PACK_NAME = re.compile(r"[A-Za-z_][A-Za-z_0-9-]*\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
TIMESTAMP = re.compile(r"(\d{4})-(\d{2})-(\d{2})[Tt](\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?(?:[Zz]|\+00:00)\Z")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
FQ_CLAUSE = re.compile(r"(?P<id>[^@#\s]+)@(?P<version>[^@#\s]+)#(?P<clause>[^@#\s]+)\Z")
REF_TEXT = re.compile(r"(?P<source>[^:@\s]+):(?P<id>[^:@\s]+)@(?P<version>[^:@\s]+)\Z")
DIAGNOSTIC_CODE = re.compile(r"[a-z][a-z0-9_]*\Z")
PHASES = frozenset({"sense", "scope", "define", "discover", "plan", "build", "review", "ship",
                    "capture", "resume", "standalone"})
_RESERVED = re.compile(r"(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?\Z", re.I)
_REPARSE_POINT = 0x400
SCOPES = ("explicit", "repo", "pack", "personal")
# Free-text fields the spec leaves unbounded are limited only by their document byte limit.
_FREE = LIMITS.input_bytes
_SCOPE_RANK = {name: index for index, name in enumerate(SCOPES)}
_MAX_TEXT = 2000


class PatternError(Exception):
    """An explicit, machine-readable failure; never converted into an empty success."""

    def __init__(self, code: str, message: str, *, status: str = "invalid", where: str = ""):
        if status not in EXIT_CODES or status in ("ok", "ready", "empty"):
            raise ValueError(f"not a failure status: {status}")
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.where = where

    def diagnostic(self) -> dict:
        record = {"code": self.code, "severity": "error", "status": self.status, "message": self.message}
        if self.where:
            record["where"] = self.where
        return record


def exit_code(status: str) -> int:
    return EXIT_CODES[status]


def _fail(code: str, message: str, where: str = "", status: str = "invalid"):
    raise PatternError(code, message, status=status, where=where)


# ---------------------------------------------------------------- JSON

def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("duplicate_key", f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(name):
    _fail("non_finite_number", f"non-finite JSON number: {name}")


def _check_depth(value: Any, limit: int) -> None:
    stack = [(value, 1)]
    while stack:
        item, depth = stack.pop()
        if depth > limit:
            _fail("resource_limit", f"JSON nesting exceeds {limit} levels")
        if isinstance(item, dict):
            stack.extend((child, depth + 1) for child in item.values())
        elif isinstance(item, list):
            stack.extend((child, depth + 1) for child in item)


def parse_json(data: bytes, *, limit: int, what: str) -> Any:
    """Strict UTF-8 JSON: optional BOM, no duplicate keys, no NaN/Infinity, bounded size/depth."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("parse_json expects bytes")
    if len(data) > limit:
        _fail("resource_limit", f"{what} exceeds {limit} bytes")
    try:
        text = bytes(data).decode("utf-8-sig")
    except UnicodeDecodeError:
        _fail("invalid_json", f"{what} is not UTF-8")
    try:
        value = json.loads(text, object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)
    except PatternError as error:
        error.message = f"{what}: {error.message}"
        raise
    except RecursionError:
        _fail("resource_limit", f"{what} nesting is too deep")
    except json.JSONDecodeError as error:
        _fail("invalid_json", f"{what} is not valid JSON (line {error.lineno})")
    _check_depth(value, LIMITS.json_depth)
    return value


def canonical_json(value: Any) -> bytes:
    """Digest input: sorted keys, compact separators, UTF-8, no trailing newline."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def content_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def emit_json(value: Any) -> str:
    """Emitted form: UTF-8 without BOM, sorted keys, LF line endings, trailing newline."""
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


# ---------------------------------------------------------------- field validators

def _object(value: Any, where: str, required: Iterable[str], optional: Iterable[str] = ()) -> dict:
    if not isinstance(value, dict):
        _fail("invalid_schema", "expected a JSON object", where)
    required, optional = set(required), set(optional)
    missing = sorted(required - value.keys())
    if missing:
        _fail("invalid_schema", f"missing required field(s): {', '.join(missing)}", where)
    unknown = sorted(value.keys() - required - optional)
    if unknown:
        _fail("invalid_schema", f"unknown field(s): {', '.join(unknown)}", where)
    return value


def _schema_version(value: dict, where: str) -> None:
    version = value.get("schema_version")
    if type(version) is not int or version != SCHEMA_VERSION:
        _fail("unsupported_schema", "schema_version must be the integer 1", where)


def _string(value: Any, where: str, *, limit: int = _MAX_TEXT, empty: bool = False) -> str:
    if not isinstance(value, str):
        _fail("invalid_schema", "expected a string", where)
    if not empty and not value.strip():
        _fail("invalid_schema", "expected a nonempty string", where)
    if len(value) > limit:
        _fail("resource_limit", f"string exceeds {limit} code points", where)
    if any(ord(char) < 32 and char not in "\n\r\t" for char in value):
        _fail("invalid_schema", "control characters are not allowed", where)
    return value


def _matching(value: Any, pattern: re.Pattern, where: str, what: str, limit: int = 128) -> str:
    if not isinstance(value, str) or len(value) > limit or not pattern.fullmatch(value):
        _fail("invalid_schema", f"invalid {what}: {value!r}", where)
    return value


def _array(value: Any, where: str, *, nonempty: bool = False) -> list:
    if not isinstance(value, list):
        _fail("invalid_schema", "expected an array", where)
    if nonempty and not value:
        _fail("invalid_schema", "expected a nonempty array", where)
    return value


def _timestamp(value: Any, where: str) -> str:
    """UTC RFC 3339: `Z`/`z` or `+00:00` offset, optional fraction (spec 4.1)."""
    if not isinstance(value, str) or not TIMESTAMP.fullmatch(value):
        _fail("invalid_schema", "expected a UTC RFC3339 timestamp (Z or +00:00)", where)
    try:
        _instant(value)
    except ValueError:
        _fail("invalid_schema", "invalid timestamp", where)
    return value


def _instant(value: str) -> _dt.datetime:
    """Comparable instant for validated timestamps (ordering must not depend on spelling)."""
    match = TIMESTAMP.fullmatch(value)
    year, month, day, hour, minute, second, fraction = match.groups()
    return _dt.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second),
                        int((fraction or "0").ljust(6, "0")), tzinfo=_dt.timezone.utc)


def _date(value: Any, where: str) -> str:
    if not isinstance(value, str) or not DATE.fullmatch(value):
        _fail("invalid_schema", "expected an ISO date YYYY-MM-DD", where)
    try:
        _dt.date.fromisoformat(value)
    except ValueError:
        _fail("invalid_schema", "invalid date", where)
    return value


def _scalar(value: Any, where: str):
    """A JSON scalar: string, number, boolean or null (spec 4.1); never an array or object."""
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        if len(value) > _MAX_TEXT:
            _fail("resource_limit", "scalar value is too long", where)
        return value
    _fail("invalid_schema", "value must be a JSON scalar (string, number, boolean or null)", where)


def _extensions(value: Any, where: str) -> dict:
    if not isinstance(value, dict):
        _fail("invalid_schema", "extensions must be a mapping", where)
    for key in value:
        _matching(key, NAMESPACED_ID, where, "namespaced extension key")
    return value


def validate_relative_path(value: Any, where: str = "path") -> PurePosixPath:
    """Portable contained relative path (a data format; never a shell path)."""
    if not isinstance(value, str) or not value or len(value) > 512:
        _fail("unsafe_path", "path must be a nonempty string of at most 512 characters", where)
    if "\\" in value or ":" in value or value.startswith("/"):
        _fail("unsafe_path", f"backslash, drive, colon or absolute path refused: {value!r}", where)
    if any(ord(char) < 32 for char in value):
        _fail("unsafe_path", "control characters refused in path", where)
    parts = value.split("/")
    for part in parts:
        if part in ("", ".", "..") or part.endswith((".", " ")) or _RESERVED.fullmatch(part) \
                or any(char in part for char in '<>"|?*'):
            _fail("unsafe_path", f"empty, dot, reserved or ambiguous path segment refused: {value!r}", where)
    return PurePosixPath(*parts)


def _is_link(path: Path) -> bool:
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return False
    except OSError as error:
        _fail("unsafe_path", f"cannot inspect path: {error.strerror}", str(path))
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & _REPARSE_POINT)


def contained_path(root: Path, relative: str, where: str = "path") -> Path:
    """Join a portable relative path under root, refusing links, junctions and escapes."""
    parts = validate_relative_path(relative, where).parts
    base = Path(root)
    if _is_link(base):
        _fail("unsafe_path", "linked source root refused", where)
    current = base
    for part in parts:
        current = current / part
        if _is_link(current):
            _fail("unsafe_path", f"linked path component refused: {relative}", where)
    try:
        resolved, anchor = current.resolve(), base.resolve()
    except OSError as error:
        _fail("unsafe_path", f"cannot resolve path: {error}", where)
    if resolved != anchor and anchor not in resolved.parents:
        _fail("unsafe_path", f"path escapes its root: {relative}", where)
    return current


class Reader:
    """Every file read goes through here, bounded and counted by kind (spec section 6 metrics)."""

    KINDS = ("catalog", "bindings", "pattern", "asset", "manifest", "input")

    def __init__(self):
        self.reads: list[tuple[str, Path]] = []

    def count(self, kind: str) -> int:
        return sum(1 for item, _ in self.reads if item == kind)

    def read(self, path: Path, *, kind: str, limit: int, optional: bool = False) -> Optional[bytes]:
        if kind not in self.KINDS:
            raise ValueError(f"unknown read kind: {kind}")
        if _is_link(path):
            _fail("unsafe_path", "linked file refused", str(path))
        if os.path.isdir(path):
            _fail("unsafe_path", f"expected a regular {kind} file, found a directory", str(path))
        try:
            with open(path, "rb") as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    _fail("unsafe_path", "only regular files are read", str(path))
                data = stream.read(limit + 1)
        except FileNotFoundError:
            if optional:
                return None
            if kind == "input":
                _fail("input_missing", "the supplied input file does not exist", str(path))
            _fail("source_missing", f"declared {kind} file is missing", str(path), status="unavailable")
        except IsADirectoryError:
            _fail("unsafe_path", "expected a regular file", str(path))
        except PermissionError as error:
            _fail("io_error", f"cannot read {kind}: {error.strerror}", str(path), status="unavailable")
        self.reads.append((kind, path))
        if len(data) > limit:
            _fail("resource_limit", f"{kind} file exceeds {limit} bytes", str(path))
        return data

    def metrics(self) -> dict:
        return {f"{kind}_reads": self.count(kind) for kind in self.KINDS}


# ---------------------------------------------------------------- typed records

@dataclass(frozen=True)
class ExactRef:
    source: str
    id: str
    version: str
    sha256: str

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.source, self.id, self.version)

    @property
    def text(self) -> str:
        return f"{self.source}:{self.id}@{self.version}"

    def to_json(self) -> dict:
        return {"source": self.source, "id": self.id, "version": self.version, "sha256": self.sha256}


@dataclass(frozen=True)
class Selector:
    """Mapping of fact key to accepted exact values: AND between keys, OR within a key."""
    terms: tuple[tuple[str, tuple[str, ...]], ...]

    def to_json(self) -> dict:
        return {key: list(values) for key, values in self.terms}


@dataclass(frozen=True)
class Clause:
    id: str
    level: str
    text: str
    verify: str
    setting: Optional[str] = None
    value: Any = None

    def to_json(self) -> dict:
        record = {"id": self.id, "level": self.level, "text": self.text, "verify": self.verify}
        if self.setting is not None:
            record.update(setting=self.setting, value=self.value)
        return record


@dataclass(frozen=True)
class SourceRecord:
    kind: str
    ref: str
    root: str
    section: str
    observed_at: str
    confidence: str
    reuse: str
    sha256: Optional[str] = None

    @property
    def is_url(self) -> bool:
        return self.root == "external" and re.match(r"https?://", self.ref, re.I) is not None


@dataclass(frozen=True)
class Asset:
    path: str
    kind: str
    sha256: str
    phases: Optional[tuple[str, ...]] = None
    domains: Optional[tuple[str, ...]] = None


@dataclass(frozen=True)
class Approval:
    by: str
    reference: str
    at: str


@dataclass(frozen=True)
class Pattern:
    id: str
    version: str
    status: str
    summary: str
    owner: str
    applies_to: Selector
    includes: tuple[ExactRef, ...]
    sources: tuple[SourceRecord, ...]
    requirements: tuple[Clause, ...]
    guidance: str
    assets: tuple[Asset, ...]
    review_after: Optional[str]
    approval: Optional[Approval]
    replaced_by: Optional[ExactRef]
    extensions: Mapping[str, Any]
    raw: Mapping[str, Any] = field(repr=False, compare=False)
    digest: str = ""

    def clause_ref(self, clause_id: str) -> str:
        return f"{self.id}@{self.version}#{clause_id}"


@dataclass(frozen=True)
class CatalogEntry:
    id: str
    version: str
    path: str
    sha256: str
    summary: str
    status: str
    applies_to: Selector

    def to_json(self) -> dict:
        return {"id": self.id, "version": self.version, "path": self.path, "sha256": self.sha256,
                "summary": self.summary, "status": self.status, "applies_to": self.applies_to.to_json()}


@dataclass(frozen=True)
class CatalogInclude:
    locator: str
    path: str
    sha256: str


@dataclass(frozen=True)
class LifecycleEvent:
    id: str
    version: str
    sha256: str
    status: str
    reason: str
    reference: str
    at: str
    replaced_by: Optional[ExactRef] = None


@dataclass(frozen=True)
class Revocation:
    id: str
    version: str
    sha256: str
    reason: str
    reference: str
    at: str


@dataclass(frozen=True)
class Binding:
    id: str
    when: Selector
    use: tuple[ExactRef, ...]
    role: str
    approved_by: str
    approval_ref: str


@dataclass(frozen=True)
class Catalog:
    source_id: str
    entries: tuple[CatalogEntry, ...]
    includes: tuple[CatalogInclude, ...]
    bindings: tuple[Binding, ...]
    lifecycle: tuple[LifecycleEvent, ...]
    revocations: tuple[Revocation, ...]
    extensions: Mapping[str, Any]
    raw: Mapping[str, Any] = field(repr=False, compare=False)
    digest: str = ""

    def entry(self, pattern_id: str, version: str) -> Optional[CatalogEntry]:
        for item in self.entries:
            if item.id == pattern_id and item.version == version:
                return item
        return None


@dataclass(frozen=True)
class Context:
    facts: Mapping[str, str]
    evidence: Mapping[str, str]
    digest: str


@dataclass(frozen=True)
class InvocationRef:
    ref: ExactRef
    role: str
    approved_by: str
    approval_ref: str


@dataclass(frozen=True)
class Override:
    setting: str
    value: Any
    reason: str
    approval_ref: str
    replaces: tuple[str, ...]

    def to_json(self) -> dict:
        return {"setting": self.setting, "value": self.value, "reason": self.reason,
                "approval_ref": self.approval_ref, "replaces": list(self.replaces)}


@dataclass(frozen=True)
class ExceptionRecord:
    clause: str
    context_digest: str
    reason: str
    approval_ref: str
    approved_by: str
    expires: str
    verification: str

    def to_json(self) -> dict:
        return {"clause": self.clause, "context_digest": self.context_digest, "reason": self.reason,
                "approval_ref": self.approval_ref, "approved_by": self.approved_by,
                "expires": self.expires, "verification": self.verification}


@dataclass(frozen=True)
class PackAncestor:
    pack: str
    version: str
    root: Path
    manifest_sha256: str


@dataclass(frozen=True)
class PackContext:
    status: str
    identity: Optional[Mapping[str, str]]
    source_state: str
    source_value: Optional[str]
    source_origin: Optional[str]
    ancestry: tuple[PackAncestor, ...]
    diagnostics: tuple[Mapping[str, str], ...]
    raw: Mapping[str, Any] = field(repr=False, compare=False)


@dataclass(frozen=True)
class Roots:
    repository: Optional[Path]
    personal: Path
    pack_context: PackContext
    diagnostics: tuple[Mapping[str, str], ...]


@dataclass(frozen=True)
class SelectorDecision:
    decision: str  # matched | rejected | needs-context
    matched: tuple[str, ...]
    missing: tuple[str, ...]
    mismatched: tuple[str, ...]


# ---------------------------------------------------------------- parsers

def parse_exact_ref(value: Any, where: str) -> ExactRef:
    _object(value, where, ("source", "id", "version", "sha256"))
    return ExactRef(
        _matching(value["source"], NAMESPACED_ID, where, "source ID"),
        _matching(value["id"], NAMESPACED_ID, where, "pattern ID"),
        _matching(value["version"], VERSION, where, "version", 64),
        _matching(value["sha256"], HEX64, where, "sha256 digest", 64),
    )


def parse_ref_text(value: str) -> tuple[str, str, str]:
    """`<source>:<id>@<version>` for show/remove style lookups (no digest)."""
    match = REF_TEXT.fullmatch(value or "")
    if not match:
        _fail("invalid_reference", "expected <source>:<id>@<version>", "--ref")
    _matching(match["source"], NAMESPACED_ID, "--ref", "source ID")
    _matching(match["id"], NAMESPACED_ID, "--ref", "pattern ID")
    _matching(match["version"], VERSION, "--ref", "version", 64)
    return match["source"], match["id"], match["version"]


def _selector(value: Any, where: str) -> Selector:
    if not isinstance(value, dict):
        _fail("invalid_schema", "selector must be a mapping", where)
    terms = []
    for key in sorted(value):
        _matching(key, SELECTOR_KEY, where, "selector key")
        values = _array(value[key], f"{where}.{key}", nonempty=True)
        for item in values:
            _string(item, f"{where}.{key}", limit=128)
        if len(set(values)) != len(values):
            _fail("invalid_schema", "duplicate selector values", f"{where}.{key}")
        terms.append((key, tuple(values)))
    return Selector(tuple(terms))


def _unique_refs(values: list, where: str) -> tuple[ExactRef, ...]:
    refs = tuple(parse_exact_ref(item, f"{where}[{index}]") for index, item in enumerate(values))
    if len({ref.key for ref in refs}) != len(refs):
        _fail("invalid_schema", "duplicate exact references", where)
    return refs


def parse_pattern(value: Any, where: str = "pattern") -> Pattern:
    required = ("schema_version", "id", "version", "status", "summary", "owner", "applies_to",
                "includes", "sources", "requirements", "guidance", "assets")
    _object(value, where, required, ("review_after", "approval", "replaced_by", "extensions"))
    _schema_version(value, where)
    status = value["status"]
    if status not in ("draft", "approved", "deprecated", "retired"):
        _fail("invalid_schema", "status must be draft, approved, deprecated or retired", f"{where}.status")
    pattern_id = _matching(value["id"], NAMESPACED_ID, f"{where}.id", "pattern ID")
    version = _matching(value["version"], VERSION, f"{where}.version", "version", 64)
    includes = _unique_refs(_array(value["includes"], f"{where}.includes"), f"{where}.includes")
    if any(ref.id == pattern_id and ref.version == version for ref in includes):
        _fail("include_cycle", "a pattern cannot include itself", f"{where}.includes")
    sources = []
    for index, item in enumerate(_array(value["sources"], f"{where}.sources")):
        at = f"{where}.sources[{index}]"
        _object(item, at, ("kind", "ref", "root", "section", "observed_at", "confidence", "reuse"), ("sha256",))
        if item["kind"] not in ("operator-statement", "approved-standard", "observation"):
            _fail("invalid_schema", "unknown source kind", f"{at}.kind")
        if item["root"] not in ("pattern", "repository", "external", "statement"):
            _fail("invalid_schema", "unknown source root", f"{at}.root")
        if item["confidence"] not in ("confirmed", "inferred", "unknown"):
            _fail("invalid_schema", "unknown source confidence", f"{at}.confidence")
        ref = _string(item["ref"], f"{at}.ref")
        if item["root"] in ("pattern", "repository"):
            validate_relative_path(ref, f"{at}.ref")
        digest = item.get("sha256")
        if digest is not None:
            _matching(digest, HEX64, f"{at}.sha256", "sha256 digest", 64)
        sources.append(SourceRecord(item["kind"], ref, item["root"],
                                    _string(item["section"], f"{at}.section", limit=_FREE, empty=True),
                                    _timestamp(item["observed_at"], f"{at}.observed_at"), item["confidence"],
                                    _string(item["reuse"], f"{at}.reuse", limit=_FREE, empty=True), digest))
    clauses, seen = [], set()
    for index, item in enumerate(_array(value["requirements"], f"{where}.requirements")):
        at = f"{where}.requirements[{index}]"
        _object(item, at, ("id", "level", "text", "verify"), ("setting", "value"))
        clause_id = _matching(item["id"], CLAUSE_ID, f"{at}.id", "clause ID", 128)
        if clause_id in seen:
            _fail("invalid_schema", f"duplicate clause ID {clause_id}", at)
        seen.add(clause_id)
        if item["level"] not in ("must", "default", "recommendation"):
            _fail("invalid_schema", "clause level must be must, default or recommendation", f"{at}.level")
        if ("setting" in item) != ("value" in item):
            _fail("invalid_schema", "setting and value appear together", at)
        setting = _matching(item["setting"], SETTING, f"{at}.setting", "setting") if "setting" in item else None
        scalar = _scalar(item["value"], f"{at}.value") if "value" in item else None
        clauses.append(Clause(clause_id, item["level"], _string(item["text"], f"{at}.text"),
                              _string(item["verify"], f"{at}.verify"), setting, scalar))
    assets, asset_paths = [], set()
    for index, item in enumerate(_array(value["assets"], f"{where}.assets")):
        at = f"{where}.assets[{index}]"
        _object(item, at, ("path", "kind", "sha256"), ("phases", "domains"))
        validate_relative_path(item["path"], f"{at}.path")
        if item["path"] in asset_paths:
            _fail("invalid_schema", "duplicate asset path", at)
        asset_paths.add(item["path"])
        if item["kind"] not in ("guide", "tokens", "diagram", "example", "visual-legacy"):
            _fail("invalid_schema", "unknown asset kind", f"{at}.kind")
        phases = domains = None
        if "phases" in item:
            phases = tuple(_array(item["phases"], f"{at}.phases"))
            if any(phase not in PHASES for phase in phases) or len(set(phases)) != len(phases):
                _fail("invalid_schema", "phases must be unique known phase IDs", f"{at}.phases")
        if "domains" in item:
            domains = tuple(_string(entry, f"{at}.domains", limit=128)
                            for entry in _array(item["domains"], f"{at}.domains"))
            if len(set(domains)) != len(domains):
                _fail("invalid_schema", "duplicate domains", f"{at}.domains")
        assets.append(Asset(item["path"], item["kind"],
                            _matching(item["sha256"], HEX64, f"{at}.sha256", "sha256 digest", 64),
                            phases, domains))
    approval = None
    if "approval" in value:
        _object(value["approval"], f"{where}.approval", ("by", "reference", "at"))
        approval = Approval(_string(value["approval"]["by"], f"{where}.approval.by", limit=_FREE),
                            _string(value["approval"]["reference"], f"{where}.approval.reference", limit=_FREE),
                            _timestamp(value["approval"]["at"], f"{where}.approval.at"))
    if status == "draft" and approval is not None:
        _fail("invalid_schema", "a draft carries no operative approval", f"{where}.approval")
    if status in ("approved", "deprecated"):
        if approval is None:
            _fail("invalid_schema", f"{status} pattern requires approval provenance", where)
        if not sources:
            _fail("invalid_schema", f"{status} pattern requires at least one source", where)
        if not clauses and not includes:
            _fail("invalid_schema", f"{status} pattern requires a requirement or include", where)
    replaced_by = parse_exact_ref(value["replaced_by"], f"{where}.replaced_by") if "replaced_by" in value else None
    return Pattern(
        pattern_id, version, status, _string(value["summary"], f"{where}.summary", limit=240),
        _string(value["owner"], f"{where}.owner", limit=_FREE), _selector(value["applies_to"], f"{where}.applies_to"),
        includes, tuple(sources), tuple(clauses), _string(value["guidance"], f"{where}.guidance", limit=4000, empty=True),
        tuple(assets), _date(value["review_after"], f"{where}.review_after") if "review_after" in value else None,
        approval, replaced_by, _extensions(value.get("extensions", {}), f"{where}.extensions"),
        value, content_digest(value),
    )


def _binding(value: Any, where: str) -> Binding:
    _object(value, where, ("id", "when", "use", "role", "approved_by", "approval_ref"))
    if value["role"] not in ("required", "default"):
        _fail("invalid_schema", "binding role must be required or default", f"{where}.role")
    return Binding(_string(value["id"], f"{where}.id", limit=_FREE),
                   _selector(value["when"], f"{where}.when"),
                   _unique_refs(_array(value["use"], f"{where}.use", nonempty=True), f"{where}.use"),
                   value["role"], _string(value["approved_by"], f"{where}.approved_by", limit=_FREE),
                   _string(value["approval_ref"], f"{where}.approval_ref", limit=_FREE))


def _binding_list(values: Any, where: str) -> tuple[Binding, ...]:
    bindings = tuple(_binding(item, f"{where}[{index}]") for index, item in enumerate(_array(values, where)))
    if len({item.id for item in bindings}) != len(bindings):
        _fail("invalid_schema", "duplicate binding IDs", where)
    return bindings


_TRANSITIONS = {"approved": {"deprecated", "retired"}, "deprecated": {"retired"}}


def parse_catalog(value: Any, where: str = "catalog") -> Catalog:
    _object(value, where, ("schema_version", "source_id", "entries", "includes", "bindings", "lifecycle"),
            ("revocations", "extensions"))
    _schema_version(value, where)
    source_id = _matching(value["source_id"], NAMESPACED_ID, f"{where}.source_id", "source ID")
    raw_entries = _array(value["entries"], f"{where}.entries")
    if len(raw_entries) > LIMITS.catalog_entries:
        _fail("resource_limit", f"catalog exceeds {LIMITS.catalog_entries} entries", where)
    entries, keys = [], set()
    for index, item in enumerate(raw_entries):
        at = f"{where}.entries[{index}]"
        _object(item, at, ("id", "version", "path", "sha256", "summary", "status", "applies_to"))
        entry = CatalogEntry(
            _matching(item["id"], NAMESPACED_ID, f"{at}.id", "pattern ID"),
            _matching(item["version"], VERSION, f"{at}.version", "version", 64),
            str(validate_relative_path(item["path"], f"{at}.path")),
            _matching(item["sha256"], HEX64, f"{at}.sha256", "sha256 digest", 64),
            _string(item["summary"], f"{at}.summary", limit=240), item["status"],
            _selector(item["applies_to"], f"{at}.applies_to"))
        if entry.status not in ("draft", "approved", "deprecated", "retired"):
            _fail("invalid_schema", "unknown entry status", f"{at}.status")
        if (entry.id, entry.version) in keys:
            _fail("invalid_schema", f"duplicate entry {entry.id}@{entry.version}", at)
        keys.add((entry.id, entry.version))
        entries.append(entry)
    by_key = {(item.id, item.version): item for item in entries}
    includes = []
    for index, item in enumerate(_array(value["includes"], f"{where}.includes")):
        at = f"{where}.includes[{index}]"
        _object(item, at, ("locator", "path", "sha256"))
        locator = item["locator"]
        if not isinstance(locator, str) or not (locator in ("repo", "personal") or
                                                (locator.startswith("pack:") and PACK_NAME.fullmatch(locator[5:]))):
            _fail("invalid_schema", "include locator must be repo, personal or pack:<name>", f"{at}.locator")
        includes.append(CatalogInclude(locator, str(validate_relative_path(item["path"], f"{at}.path")),
                                       _matching(item["sha256"], HEX64, f"{at}.sha256", "sha256 digest", 64)))
    if len({(item.locator, item.path) for item in includes}) != len(includes):
        _fail("invalid_schema", "duplicate catalog includes", f"{where}.includes")

    def event_target(item: dict, at: str) -> CatalogEntry:
        entry = by_key.get((item.get("id"), item.get("version")))
        if entry is None or entry.sha256 != item.get("sha256"):
            _fail("invalid_schema", "event does not reference a registered entry digest", at)
        return entry

    lifecycle = []
    for index, item in enumerate(_array(value["lifecycle"], f"{where}.lifecycle")):
        at = f"{where}.lifecycle[{index}]"
        _object(item, at, ("id", "version", "sha256", "status", "reason", "reference", "at"), ("replaced_by",))
        event_target(item, at)
        if item["status"] not in ("deprecated", "retired"):
            _fail("invalid_schema", "lifecycle events record deprecated or retired only", f"{at}.status")
        lifecycle.append(LifecycleEvent(
            item["id"], item["version"], item["sha256"], item["status"],
            _string(item["reason"], f"{at}.reason", limit=_FREE), _string(item["reference"], f"{at}.reference", limit=_FREE),
            _timestamp(item["at"], f"{at}.at"),
            parse_exact_ref(item["replaced_by"], f"{at}.replaced_by") if "replaced_by" in item else None))
    for key, entry in by_key.items():
        events = sorted((item for item in lifecycle if (item.id, item.version) == key), key=lambda item: _instant(item.at))
        state = entry.status
        for previous, current in zip([None] + events[:-1], events):
            if previous is not None and _instant(previous.at) == _instant(current.at):
                _fail("invalid_schema", f"conflicting lifecycle events share a timestamp for {key[0]}@{key[1]}", where)
            if current.status not in _TRANSITIONS.get(state, set()):
                _fail("invalid_schema", f"invalid lifecycle transition {state} -> {current.status} for {key[0]}@{key[1]}", where)
            state = current.status
    revocations = []
    for index, item in enumerate(_array(value.get("revocations", []), f"{where}.revocations")):
        at = f"{where}.revocations[{index}]"
        _object(item, at, ("id", "version", "sha256", "reason", "reference", "at"))
        event_target(item, at)
        revocations.append(Revocation(item["id"], item["version"], item["sha256"],
                                      _string(item["reason"], f"{at}.reason", limit=_FREE),
                                      _string(item["reference"], f"{at}.reference", limit=_FREE),
                                      _timestamp(item["at"], f"{at}.at")))
    if len({(item.id, item.version) for item in revocations}) != len(revocations):
        _fail("invalid_schema", "duplicate revocations", f"{where}.revocations")
    return Catalog(source_id, tuple(entries), tuple(includes), _binding_list(value["bindings"], f"{where}.bindings"),
                   tuple(lifecycle), tuple(revocations), _extensions(value.get("extensions", {}), f"{where}.extensions"),
                   value, content_digest(value))


def parse_bindings(value: Any, where: str = "bindings") -> tuple[Binding, ...]:
    _object(value, where, ("schema_version", "bindings"))
    _schema_version(value, where)
    return _binding_list(value["bindings"], f"{where}.bindings")


def parse_context(value: Any, where: str = "context") -> Context:
    _object(value, where, ("schema_version", "facts", "evidence"))
    _schema_version(value, where)
    facts, evidence = value["facts"], value["evidence"]
    if not isinstance(facts, dict) or not isinstance(evidence, dict):
        _fail("invalid_schema", "facts and evidence must be mappings", where)
    for key, fact in facts.items():
        _matching(key, SELECTOR_KEY, f"{where}.facts", "fact key")
        _string(fact, f"{where}.facts.{key}", limit=128)
    if set(evidence) != set(facts):
        _fail("invalid_schema", "every fact needs exactly one evidence reference", f"{where}.evidence")
    for key, reference in evidence.items():
        _string(reference, f"{where}.evidence.{key}", limit=_FREE)
    return Context(dict(facts), dict(evidence), content_digest(value))


def parse_refs(value: Any, where: str = "refs") -> tuple[InvocationRef, ...]:
    items = []
    for index, item in enumerate(_array(value, where)):
        at = f"{where}[{index}]"
        _object(item, at, ("ref", "role", "approved_by", "approval_ref"))
        if item["role"] not in ("required", "default"):
            _fail("invalid_schema", "explicit reference role must be required or default", f"{at}.role")
        items.append(InvocationRef(parse_exact_ref(item["ref"], f"{at}.ref"), item["role"],
                                   _string(item["approved_by"], f"{at}.approved_by", limit=_FREE),
                                   _string(item["approval_ref"], f"{at}.approval_ref", limit=_FREE)))
    if len({item.ref.key for item in items}) != len(items):
        _fail("invalid_schema", "duplicate explicit references", where)
    return tuple(items)


def _fq_clause(value: Any, where: str) -> str:
    match = FQ_CLAUSE.fullmatch(value) if isinstance(value, str) else None
    if not match or not NAMESPACED_ID.fullmatch(match["id"]) or not VERSION.fullmatch(match["version"]) \
            or not CLAUSE_ID.fullmatch(match["clause"]):
        _fail("invalid_schema", "expected <pattern-id>@<version>#<clause-id>", where)
    return value


def parse_overrides(value: Any, where: str = "overrides") -> tuple[Override, ...]:
    _object(value, where, ("schema_version", "items"))
    _schema_version(value, where)
    items = []
    for index, item in enumerate(_array(value["items"], f"{where}.items")):
        at = f"{where}.items[{index}]"
        _object(item, at, ("setting", "value", "reason", "approval_ref", "replaces"))
        replaces = tuple(_fq_clause(entry, f"{at}.replaces")
                         for entry in _array(item["replaces"], f"{at}.replaces", nonempty=True))
        if len(set(replaces)) != len(replaces):
            _fail("invalid_schema", "duplicate replaced clauses", f"{at}.replaces")
        items.append(Override(_matching(item["setting"], SETTING, f"{at}.setting", "setting"),
                              _scalar(item["value"], f"{at}.value"), _string(item["reason"], f"{at}.reason", limit=_FREE),
                              _string(item["approval_ref"], f"{at}.approval_ref", limit=_FREE), replaces))
    if len({item.setting for item in items}) != len(items):
        _fail("invalid_schema", "duplicate override settings", f"{where}.items")
    return tuple(items)


def parse_exceptions(value: Any, where: str = "exceptions") -> tuple[ExceptionRecord, ...]:
    _object(value, where, ("schema_version", "items"))
    _schema_version(value, where)
    items = []
    for index, item in enumerate(_array(value["items"], f"{where}.items")):
        at = f"{where}.items[{index}]"
        _object(item, at, ("clause", "context_digest", "reason", "approval_ref", "approved_by", "expires",
                           "verification"))
        items.append(ExceptionRecord(
            _fq_clause(item["clause"], f"{at}.clause"),
            _matching(item["context_digest"], HEX64, f"{at}.context_digest", "context digest", 64),
            _string(item["reason"], f"{at}.reason", limit=_FREE), _string(item["approval_ref"], f"{at}.approval_ref", limit=_FREE),
            _string(item["approved_by"], f"{at}.approved_by", limit=_FREE), _date(item["expires"], f"{at}.expires"),
            _string(item["verification"], f"{at}.verification")))
    if len({item.clause for item in items}) != len(items):
        _fail("invalid_schema", "duplicate exceptions for one clause", f"{where}.items")
    return tuple(items)


def _diagnostic_list(value: Any, where: str) -> tuple[Mapping[str, str], ...]:
    items = []
    for index, item in enumerate(_array(value, where)):
        at = f"{where}[{index}]"
        _object(item, at, ("code", "message"))
        items.append({"code": _string(item["code"], f"{at}.code", limit=128),
                      "message": _string(item["message"], f"{at}.message")})
    return tuple(items)


def _absolute(value: Any, where: str) -> Path:
    if not isinstance(value, str) or not value or len(value) > 4096 or any(ord(char) < 32 for char in value):
        _fail("invalid_roots", "expected an absolute path string", where)
    path = Path(value)
    if not path.is_absolute():
        _fail("invalid_roots", f"path must be absolute: {value}", where)
    return path


def parse_pack_context(value: Any, where: str = "pack_context") -> PackContext:
    _object(value, where, ("schema_version", "status", "identity", "source", "ancestry", "diagnostics"))
    _schema_version(value, where)
    status = value["status"]
    if status not in ("resolved", "neutral", "fallback", "error"):
        _fail("invalid_pack_context", "status must be resolved, neutral, fallback or error", f"{where}.status")
    identity = value["identity"]
    if status == "error":
        if identity is not None:
            _fail("invalid_pack_context", "an error context has no identity", f"{where}.identity")
    else:
        _object(identity, f"{where}.identity", ("name", "version"))
        _matching(identity["name"], PACK_NAME, f"{where}.identity.name", "pack name")
        _string(identity["version"], f"{where}.identity.version", limit=128)
    source = _object(value["source"], f"{where}.source", ("state", "value", "origin"))
    state, source_value, origin = source["state"], source["value"], source["origin"]
    if state not in ("value", "null", "absent", "unavailable"):
        _fail("invalid_pack_context", "source.state must be value, null, absent or unavailable", f"{where}.source")
    if state == "value":
        _string(source_value, f"{where}.source.value", limit=512)
        _absolute(origin, f"{where}.source.origin")
    elif state == "null":
        if source_value is not None:
            _fail("invalid_pack_context", "explicit null has a null value", f"{where}.source")
        _absolute(origin, f"{where}.source.origin")
    elif state == "absent":
        if source_value is not None or origin is not None:
            _fail("invalid_pack_context", "absent has neither value nor origin", f"{where}.source")
    else:
        if source_value is not None:
            _fail("invalid_pack_context", "unavailable carries no usable value", f"{where}.source")
        if origin is not None:
            _absolute(origin, f"{where}.source.origin")
    ancestry = []
    for index, item in enumerate(_array(value["ancestry"], f"{where}.ancestry")):
        at = f"{where}.ancestry[{index}]"
        _object(item, at, ("pack", "version", "root", "manifest_sha256"))
        ancestry.append(PackAncestor(_matching(item["pack"], PACK_NAME, f"{at}.pack", "pack name"),
                                     _string(item["version"], f"{at}.version", limit=128),
                                     _absolute(item["root"], f"{at}.root"),
                                     _matching(item["manifest_sha256"], HEX64, f"{at}.manifest_sha256",
                                               "manifest digest", 64)))
    if len({item.pack for item in ancestry}) != len(ancestry):
        _fail("invalid_pack_context", "duplicate ancestry pack", f"{where}.ancestry")
    if status != "error" and not ancestry:
        _fail("invalid_pack_context", "a usable context has its effective ancestry", f"{where}.ancestry")
    if status != "error" and ancestry[-1].pack != identity["name"]:
        _fail("invalid_pack_context", "ancestry must end with the effective identity", f"{where}.ancestry")
    diagnostics = _diagnostic_list(value["diagnostics"], f"{where}.diagnostics")
    if (status in ("error", "fallback") or state == "unavailable") and not diagnostics:
        _fail("invalid_pack_context", "error, fallback and unavailable contexts carry diagnostics", where)
    return PackContext(status, identity, state, source_value, origin, tuple(ancestry), diagnostics, value)


def parse_roots(value: Any, where: str = "roots") -> Roots:
    """The launcher's stdin envelope: resolved roots plus the same-snapshot pack context."""
    _object(value, where, ("schema_version", "repository", "personal", "pack_context", "diagnostics"))
    _schema_version(value, where)
    repository = None
    if value["repository"] is not None:
        repository = _absolute(value["repository"], f"{where}.repository")
        if not repository.is_dir() or _is_link(repository):
            _fail("invalid_roots", "repository root must be an existing, unlinked directory", f"{where}.repository")
    personal = _absolute(value["personal"], f"{where}.personal")
    if _is_link(personal):
        _fail("invalid_roots", "the personal root must not be a link or junction", f"{where}.personal")
    return Roots(repository, personal, parse_pack_context(value["pack_context"], f"{where}.pack_context"),
                 _diagnostic_list(value["diagnostics"], f"{where}.diagnostics"))


_PROFILE_MODULE = None


def _profile_module():
    """Load the trusted ADR-0029 implementation beside this file (RN-01: reuse, no second parser)."""
    global _PROFILE_MODULE
    if _PROFILE_MODULE is not None:
        return _PROFILE_MODULE
    path = Path(__file__).resolve().with_name("profile_context.py")
    name = "lintel_patterns_profile_context"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None or not path.is_file():
        _fail("profile_unavailable", "trusted profile_context.py is missing", status="unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    _PROFILE_MODULE = module
    return module


def _error_pack_context(code: str, message: str) -> dict:
    return {"schema_version": 1, "status": "error", "identity": None,
            "source": {"state": "unavailable", "value": None, "origin": None}, "ancestry": [],
            "diagnostics": [{"code": code, "message": message}]}


def pack_context_from_profile(record: Optional[Mapping[str, Any]] = None, *, error: Optional[tuple[str, str]] = None) -> dict:
    """Derive the spec section 3 pack context from an ADR-0029 profile record (RN-01).

    `record` is `profile_context.py ... context` output (or its `profile` member). No
    manifest is parsed here: values, provenance and ancestry come from that record.
    """
    if error is not None:
        code, message = error
        return _error_pack_context(_string(code, "profile_error.code", limit=128),
                                   _string(message, "profile_error.message"))
    if not isinstance(record, Mapping):
        _fail("invalid_pack_context", "expected a profile context record")
    module = _profile_module()
    profile = record.get("profile", record)
    if "profile" in record and record.get("digest") != module.digest(profile):
        _fail("invalid_pack_context", "profile record digest does not match its profile", status="unavailable")
    try:
        selection, values = profile["selection"], profile["values"]
        provenance, chain = profile["provenance"], profile["ancestry"]
        identity = {"name": values["name"], "version": values["version"]}
    except (KeyError, TypeError):
        _fail("invalid_pack_context", "profile record lacks selection, values, provenance or ancestry")
    diagnostics = []
    if isinstance(selection.get("diagnostic"), Mapping):
        diagnostics.append({"code": str(selection["diagnostic"].get("code", "PROFILE_FALLBACK")),
                            "message": str(selection["diagnostic"].get("message", "optional profile fallback"))})
    if selection.get("status") == "fallback":
        status = "fallback"
        if not diagnostics:
            diagnostics.append({"code": "PROFILE_FALLBACK", "message": "optional preference did not load"})
    elif selection.get("mode") == "neutral":
        status = "neutral"
    else:
        status = "resolved"
    raw = module.field_value(values, "patterns.source")
    origin_record = provenance.get("patterns.source") if isinstance(provenance, Mapping) else None
    origin = origin_record.get("path") if isinstance(origin_record, Mapping) else None
    if raw is module.MISSING:
        source = {"state": "absent", "value": None, "origin": None}
    elif raw is None and isinstance(origin, str):
        source = {"state": "null", "value": None, "origin": origin}
    elif isinstance(raw, str) and raw and isinstance(origin, str):
        source = {"state": "value", "value": raw, "origin": origin}
    else:
        source = {"state": "unavailable", "value": None, "origin": origin if isinstance(origin, str) else None}
        diagnostics.append({"code": "pack_source_invalid",
                            "message": "patterns.source must be a relative catalog path string or null"})
    ancestry = []
    try:
        for pack in chain:
            manifest = Path(pack["path"])
            ancestry.append({"pack": pack["name"], "version": pack["version"], "root": manifest.parent.as_posix(),
                             "manifest_sha256": str(pack["digest"]).removeprefix("sha256:")})
    except (KeyError, TypeError, AttributeError):
        _fail("invalid_pack_context", "profile ancestry entries need name, version, path and digest")
    context = {"schema_version": 1, "status": status, "identity": identity, "source": source,
               "ancestry": ancestry, "diagnostics": diagnostics}
    parse_pack_context(context)
    return context


def build_envelope(repository: Optional[Path], personal: Path, pack_context: Mapping[str, Any],
                   diagnostics: Sequence[Mapping[str, str]] = ()) -> dict:
    """Serialize the roots envelope with JSON (never shell interpolation) and validate it.

    Each anchor is checked for a link or junction on the spelling the caller supplied, before
    resolution could erase that evidence (the same refusal `parse_roots` applies to an envelope).
    This sees only the given spelling: a physical path already produced upstream, such as Git's
    resolved top level, carries no alias to detect.
    """
    def anchor(value: Path, where: str) -> str:
        logical = Path(value)
        logical = logical if logical.is_absolute() else Path.cwd() / logical
        if _is_link(logical):
            _fail("invalid_roots", f"{where} must not be a link or junction; pass its real path", where)
        return logical.resolve().as_posix()

    envelope = {"schema_version": 1,
                "repository": None if repository is None else anchor(repository, "repository"),
                "personal": anchor(personal, "personal"), "pack_context": dict(pack_context),
                "diagnostics": [dict(item) for item in diagnostics]}
    parse_roots(envelope)
    return envelope


def evaluate_selector(selector: Selector, context: Context) -> SelectorDecision:
    """Any known mismatch rejects; otherwise any missing key needs context; else matched."""
    matched, missing, mismatched = [], [], []
    for key, values in selector.terms:
        if key not in context.facts:
            missing.append(key)
        elif context.facts[key] in values:
            matched.append(key)
        else:
            mismatched.append(key)
    decision = "rejected" if mismatched else "needs-context" if missing else "matched"
    return SelectorDecision(decision, tuple(matched), tuple(missing), tuple(mismatched))


# ---------------------------------------------------------------- sources

@dataclass(frozen=True)
class LoadedCatalog:
    locator: str
    scope: str  # repo | pack | personal: the declaring locator's scope, never the traversal path
    directory: Path
    catalog: Catalog
    active: bool
    depth: int

    def summary(self) -> dict:
        return {"locator": self.locator, "source_id": self.catalog.source_id, "scope": self.scope,
                "active": self.active, "catalog_sha256": self.catalog.digest,
                "entries": len(self.catalog.entries), "include_depth": self.depth}


@dataclass
class SourceSet:
    roots: Roots
    reader: Reader
    catalogs: list[LoadedCatalog] = field(default_factory=list)
    bindings: list[tuple[str, Binding, str]] = field(default_factory=list)  # (scope, binding, origin)
    blockers: list[dict] = field(default_factory=list)
    notes: list[dict] = field(default_factory=list)

    def by_source(self, source_id: str) -> Optional[LoadedCatalog]:
        for item in self.catalogs:
            if item.catalog.source_id == source_id:
                return item
        return None


def _note(code: str, message: str, severity: str = "info", **details) -> dict:
    return {"code": code, "severity": severity, "message": message, **details}


def _verified_ancestor(sources: SourceSet, name: str) -> PackAncestor:
    for ancestor in sources.roots.pack_context.ancestry:
        if ancestor.pack == name:
            break
    else:
        _fail("pack_locator_unknown", f"pack:{name} is not in the effective ancestry", status="unavailable")
    manifest = ancestor.root / "pack.yaml"
    data = sources.reader.read(manifest, kind="manifest", limit=1024 * 1024, optional=True)
    if data is None or not ancestor.root.is_dir():
        _fail("pack_snapshot_missing", f"cached pack root or manifest disappeared: pack:{name}", status="unavailable")
    if hashlib.sha256(data).hexdigest() != ancestor.manifest_sha256:
        _fail("pack_snapshot_drift", f"pack:{name} manifest changed since the profile snapshot; rebind explicitly",
              status="unavailable")
    return ancestor


def _locator_root(sources: SourceSet, locator: str) -> Path:
    """Derived roots are checked component by component from their trusted anchor (F1)."""
    if locator == "repo":
        if sources.roots.repository is None:
            _fail("repository_required", "repository locator needs an explicit repository root", status="unavailable")
        return contained_path(sources.roots.repository, ".claude/patterns", "repository pattern root")
    if locator == "personal":
        return contained_path(sources.roots.personal, "patterns", "personal pattern root")
    ancestor = _verified_ancestor(sources, locator[5:])
    if _is_link(ancestor.root):
        _fail("unsafe_path", f"linked pack root refused: {locator}")
    return ancestor.root


def _locator_scope(locator: str) -> str:
    return "pack" if locator.startswith("pack:") else locator


def _register_bindings(sources: SourceSet, loaded: "LoadedCatalog") -> None:
    if not loaded.catalog.bindings:
        return
    if loaded.active and loaded.scope != "personal":
        sources.bindings.extend((loaded.scope, binding, loaded.catalog.source_id) for binding in loaded.catalog.bindings)
    else:
        sources.notes.append(_note("personal_bindings_inactive" if loaded.scope == "personal" else "inactive_bindings",
                                   f"{loaded.catalog.source_id} bindings are not auto-applied from this location"))


def _load_catalog(sources: SourceSet, locator: str, relative: str, active: bool, depth: int,
                  expected: Optional[str], stack: list, optional: bool = False) -> None:
    if depth > LIMITS.include_depth:
        _fail("resource_limit", f"catalog includes exceed depth {LIMITS.include_depth}")
    root = _locator_root(sources, locator)
    path = contained_path(root, relative, f"{locator}:{relative}")
    identity = (locator, path.resolve().as_posix().casefold() if os.name == "nt" else path.resolve().as_posix())
    if identity in stack:
        _fail("include_cycle", f"catalog include cycle at {locator}:{relative}")
    data = sources.reader.read(path, kind="catalog", limit=LIMITS.catalog_bytes, optional=optional)
    if data is None:
        return
    catalog = parse_catalog(parse_json(data, limit=LIMITS.catalog_bytes, what=f"catalog {locator}:{relative}"),
                            f"{locator}:{relative}")
    if expected is not None and catalog.digest != expected:
        _fail("include_digest_mismatch", f"included catalog {locator}:{relative} does not match its pinned digest",
              status="unavailable")
    existing = sources.by_source(catalog.source_id)
    if existing is not None:
        if existing.catalog.digest != catalog.digest:
            _fail("source_id_collision", f"two catalogs declare source {catalog.source_id} with different content")
        if active and not existing.active:
            upgraded = LoadedCatalog(existing.locator, existing.scope, existing.directory, existing.catalog, True,
                                     min(existing.depth, depth))
            sources.catalogs[sources.catalogs.index(existing)] = upgraded
            sources.notes = [item for item in sources.notes
                             if not (item["code"] in ("personal_bindings_inactive", "inactive_bindings")
                                     and catalog.source_id in item["message"])]
            _register_bindings(sources, upgraded)
        return
    if len(sources.catalogs) >= LIMITS.source_catalogs:
        _fail("resource_limit", f"more than {LIMITS.source_catalogs} source catalogs")
    loaded = LoadedCatalog(locator, _locator_scope(locator), path.parent, catalog, active, depth)
    sources.catalogs.append(loaded)
    _register_bindings(sources, loaded)
    allowed = {locator} | {f"pack:{item.pack}" for item in sources.roots.pack_context.ancestry}
    for include in sorted(catalog.includes, key=lambda item: (item.locator, item.path)):
        if include.locator not in allowed:
            _fail("include_locator_refused", f"{catalog.source_id} cannot include from {include.locator}")
        _load_catalog(sources, include.locator, include.path, active, depth + 1, include.sha256,
                      stack + [identity])


def load_sources(roots: Roots, reader: Optional[Reader] = None) -> SourceSet:
    """Load configured catalogs and bindings. Unavailable sources become blockers, not empty success."""
    sources = SourceSet(roots, reader or Reader())
    if roots.repository is not None:
        _load_catalog(sources, "repo", "catalog.json", True, 0, None, [], optional=True)
        bindings_path = contained_path(roots.repository, ".claude/patterns/bindings.json", "repository bindings")
        data = sources.reader.read(bindings_path, kind="bindings", limit=LIMITS.input_bytes, optional=True)
        if data is not None:
            sources.bindings.extend(("repo", binding, "repo:bindings.json") for binding in parse_bindings(
                parse_json(data, limit=LIMITS.input_bytes, what="repository bindings"), "repo:bindings.json"))
    context = roots.pack_context
    if context.status in ("error", "fallback"):
        for item in context.diagnostics or ({"code": "pack_context_" + context.status, "message": ""},):
            sources.blockers.append(_note("pack_context_" + context.status,
                                          f"pack context {context.status}: {item['code']}: {item['message']}",
                                          "error", status="unavailable"))
    elif context.source_state == "unavailable":
        sources.blockers.append(_note("pack_source_unavailable", "the pack pattern source is unavailable",
                                      "error", status="unavailable"))
    elif context.source_state == "value":
        origin = Path(context.source_origin)
        owner = [item for item in context.ancestry if _same_path(item.root / "pack.yaml", origin)]
        if not owner:
            sources.blockers.append(_note("pack_source_origin_unknown",
                                          "patterns.source was declared outside the effective ancestry",
                                          "error", status="unavailable"))
        else:
            try:
                _load_catalog(sources, f"pack:{owner[0].pack}", context.source_value, True, 0, None, [])
            except PatternError as error:
                if error.status != "unavailable":
                    raise
                sources.blockers.append(dict(error.diagnostic()))
    _load_catalog(sources, "personal", "catalog.json", False, 0, None, [], optional=True)
    seen = set()
    for _, binding, origin in sources.bindings:
        if (origin, binding.id) in seen:
            _fail("invalid_schema", f"duplicate binding ID {binding.id} in {origin}")
        seen.add((origin, binding.id))
    return sources


def _same_path(left: Path, right: Path) -> bool:
    a, b = Path(left).resolve().as_posix(), Path(right).resolve().as_posix()
    return a.casefold() == b.casefold() if os.name == "nt" else a == b


def effective_status(loaded: LoadedCatalog, entry: CatalogEntry) -> tuple[str, Optional[ExactRef]]:
    """Latest validated catalog event wins; revocation overrides any lifecycle state."""
    catalog = loaded.catalog
    for item in catalog.revocations:
        if (item.id, item.version, item.sha256) == (entry.id, entry.version, entry.sha256):
            return "revoked", None
    events = sorted((item for item in catalog.lifecycle
                     if (item.id, item.version, item.sha256) == (entry.id, entry.version, entry.sha256)),
                    key=lambda item: _instant(item.at))
    if events:
        return events[-1].status, events[-1].replaced_by
    return entry.status, None


def _read_pattern(sources: SourceSet, loaded: LoadedCatalog, entry: CatalogEntry) -> Pattern:
    """Read once, validate those bytes, and use the same parsed record (no re-read)."""
    return _read_pattern_bytes(sources, loaded, entry)[1]


def _read_pattern_bytes(sources: SourceSet, loaded: LoadedCatalog, entry: CatalogEntry) -> tuple[bytes, Pattern]:
    path = contained_path(loaded.directory, entry.path, f"{loaded.catalog.source_id}:{entry.id}@{entry.version}")
    data = sources.reader.read(path, kind="pattern", limit=LIMITS.pattern_bytes)
    pattern = parse_pattern(parse_json(data, limit=LIMITS.pattern_bytes, what=f"pattern {entry.id}@{entry.version}"),
                            f"{loaded.catalog.source_id}:{entry.id}@{entry.version}")
    if pattern.digest != entry.sha256:
        _fail("pattern_digest_mismatch", f"{entry.id}@{entry.version} bytes do not match the catalog digest",
              status="unavailable")
    if (pattern.id, pattern.version, pattern.summary, pattern.status, pattern.applies_to) != \
            (entry.id, entry.version, entry.summary, entry.status, entry.applies_to):
        _fail("stale_metadata", f"catalog metadata for {entry.id}@{entry.version} differs from the pattern",
              status="unavailable")
    return data, pattern


def _lookup(sources: SourceSet, ref: ExactRef) -> tuple[LoadedCatalog, CatalogEntry]:
    loaded = sources.by_source(ref.source)
    if loaded is None:
        _fail("source_unavailable", f"source {ref.source} is not configured here", status="unavailable")
    entry = loaded.catalog.entry(ref.id, ref.version)
    if entry is None:
        _fail("reference_missing", f"{ref.text} is not registered", status="unavailable")
    if entry.sha256 != ref.sha256:
        _fail("reference_digest_mismatch", f"{ref.text} digest differs from the registered entry",
              status="unavailable")
    return loaded, entry


# ---------------------------------------------------------------- resolution

REPORT_KEYS = ("schema_version", "status", "context_digest", "selection_digest", "sources", "selected", "candidates",
               "requirements", "settings", "overrides", "exceptions", "diagnostics", "metrics")


@dataclass
class _Node:
    ref: ExactRef
    pattern: Pattern
    effective: str
    role: str
    scope: str
    reasons: list = field(default_factory=list)
    preview: bool = False
    equivalents: list = field(default_factory=list)

    @property
    def identity(self) -> tuple[str, str, str]:
        """Clause identity is source-independent: `<id>@<version>` plus its content digest (spec 4.1/4.2)."""
        return (self.ref.id, self.ref.version, self.ref.sha256)


class _Resolution:
    def __init__(self, sources: SourceSet, context: Context, preview_draft: bool, today: _dt.date):
        self.sources, self.context, self.preview_draft, self.today = sources, context, preview_draft, today
        self.nodes: dict[tuple, _Node] = {}
        self.loaded: dict[tuple, tuple] = {}
        self.digests: dict[tuple, str] = {}
        self.diagnostics: list[dict] = list(sources.blockers) + list(sources.notes)
        self.bindings: list[dict] = []
        self.applied_attestations: list[dict] = []

    def problem(self, status: str, code: str, message: str, **details) -> None:
        self.diagnostics.append(_note(code, message, "error", status=status, **details))

    def scope_of(self, ref: ExactRef) -> str:
        loaded = self.sources.by_source(ref.source)
        return loaded.scope if loaded is not None else "personal"

    def expand(self, ref: ExactRef, role: str, scope: str, reason: dict, explicit: bool, origin: str,
               stack: tuple = (), blocking: Optional[bool] = None) -> Optional[list[_Node]]:
        """Return the node closure, or None when this subtree is blocked or not applicable.

        Integrity, lookup and lifecycle failures of any bound, included or explicit record are
        errors (unavailable) whatever the role; only selector non-applicability of a default
        is a non-blocking skip. `origin` is the selecting authority (repo, pack or explicit).
        """
        if len(stack) > LIMITS.include_depth:
            _fail("resource_limit", f"pattern includes exceed depth {LIMITS.include_depth}")
        if ref.key in stack:
            _fail("include_cycle", f"pattern include cycle at {ref.text}")
        known = self.digests.setdefault(ref.key, ref.sha256)
        if known != ref.sha256:
            _fail("conflicting_digest", f"{ref.text} is referenced with two different digests")
        if blocking is None:
            blocking = role == "required" or explicit
        try:
            if ref.key in self.loaded:
                loaded, entry, state, replacement, pattern = self.loaded[ref.key]
            else:
                loaded, entry = _lookup(self.sources, ref)
                state, replacement = effective_status(loaded, entry)
                pattern = None
            if loaded.locator == "personal" and origin == "pack":
                _fail("personal_ref_refused", f"{ref.text} is personal; pack bindings and their includes never "
                      "activate personal patterns (use an explicit reference or a repository binding)",
                      status="unavailable")
            preview = False
            if state == "draft":
                if not (explicit and not stack and self.preview_draft):
                    _fail("draft_not_eligible", f"{ref.text} is a draft; drafts are never selected for execution"
                          + ("" if explicit else " by bindings or includes"), status="unavailable")
                preview = True
            elif state in ("retired", "revoked"):
                _fail(f"pattern_{state}", f"{ref.text} is {state}", status="unavailable")
        except PatternError as error:
            if error.status == "invalid":
                raise
            self.diagnostics.append(dict(error.diagnostic(), ref=ref.to_json(), role=role))
            return None
        # Metadata first: the validated catalog selector equals the body's, so a non-applicable
        # record is decided with zero body reads.
        decision = evaluate_selector(pattern.applies_to if pattern else entry.applies_to, self.context)
        if decision.decision != "matched":
            details = {"ref": ref.to_json(), "missing_keys": list(decision.missing),
                       "mismatched_keys": list(decision.mismatched)}
            if blocking:
                if decision.decision == "rejected":
                    self.problem("conflict", "applicability_mismatch",
                                 f"{ref.text} does not apply to this context; correct the context or binding", **details)
                else:
                    self.problem("needs-context", "pattern_needs_context",
                                 f"{ref.text} needs facts: {', '.join(decision.missing)}", **details)
            else:
                self.diagnostics.append(_note("default_not_applicable",
                                              f"default {ref.text} not applied ({decision.decision})", "info", **details))
            return None
        if pattern is None:
            try:
                pattern = _read_pattern(self.sources, loaded, entry)
            except PatternError as error:
                if error.status == "invalid":
                    raise
                self.diagnostics.append(dict(error.diagnostic(), ref=ref.to_json(), role=role))
                return None
            self.loaded[ref.key] = (loaded, entry, state, replacement, pattern)
        if state == "deprecated":
            self.diagnostics.append(_note("pattern_deprecated", f"{ref.text} is deprecated", "warning",
                                          ref=ref.to_json(),
                                          replaced_by=(replacement or pattern.replaced_by).to_json()
                                          if (replacement or pattern.replaced_by) else None))
        if preview:
            self.problem("unavailable", "draft_preview_only",
                         f"{ref.text} is a draft preview; this report is not executable selection evidence",
                         ref=ref.to_json())
        closure = [_Node(ref, pattern, state, role, scope, [reason], preview, [ref.to_json()])]
        for child in pattern.includes:
            nodes = self.expand(child, role, scope, {"kind": "include", "parent": ref.to_json()}, False, origin,
                                stack + (ref.key,), blocking)
            if nodes is None:
                self.diagnostics.append(_note("include_blocked", f"{ref.text} is blocked by its include {child.text}",
                                              "info", ref=ref.to_json(), include=child.to_json()))
                return None
            closure.extend(nodes)
        return closure

    def add(self, nodes: Optional[list[_Node]]) -> None:
        """Merge identical content selected through several sources into one clause identity."""
        for node in nodes or ():
            current = self.nodes.get(node.identity)
            if current is None:
                self.nodes[node.identity] = node
                continue
            if node.role == "required":
                current.role = "required"
            if (_SCOPE_RANK[node.scope], node.ref.source) < (_SCOPE_RANK[current.scope], current.ref.source):
                current.scope, current.ref = node.scope, node.ref
            current.reasons.extend(item for item in node.reasons if item not in current.reasons)
            current.equivalents.extend(item for item in node.equivalents if item not in current.equivalents)
            current.equivalents.sort(key=lambda item: (item["source"], item["id"], item["version"]))
            current.preview = current.preview or node.preview
            current.effective = node.effective if node.effective == "deprecated" else current.effective


def _asset_json(asset: Asset) -> dict:
    record = {"path": asset.path, "kind": asset.kind, "sha256": asset.sha256}
    if asset.phases is not None:
        record["phases"] = list(asset.phases)
    if asset.domains is not None:
        record["domains"] = list(asset.domains)
    return record


def _clause_record(node: _Node, clause: Clause, state: str, reason: str = "") -> dict:
    record = {"clause": node.pattern.clause_ref(clause.id), "pattern": node.ref.to_json(), "level": clause.level,
              "role": node.role, "scope": node.scope, "state": state, "text": clause.text, "verify": clause.verify}
    if clause.setting is not None:
        record.update(setting=clause.setting, value=clause.value)
    if reason:
        record["reason"] = reason
    return record


def _same_value(left: Any, right: Any) -> bool:
    return canonical_json(left) == canonical_json(right)


def _settle(resolution: _Resolution, requirements: list[dict], overrides: Sequence[Override],
            exceptions: Sequence[ExceptionRecord]) -> tuple[dict, list[dict], list[dict]]:
    by_clause = {item["clause"]: item for item in requirements}
    applied_exceptions = []
    for item in exceptions:
        target = by_clause.get(item.clause)
        if target is None or target["level"] != "must" or target["state"] != "mandatory":
            _fail("exception_unknown_clause", f"exception targets no selected mandatory clause: {item.clause}")
        if item.context_digest != resolution.context.digest:
            _fail("exception_context_mismatch", f"exception for {item.clause} was granted for another context")
        if _dt.date.fromisoformat(item.expires) < resolution.today:
            _fail("exception_expired", f"exception for {item.clause} expired on {item.expires}")
        target["state"] = "waived"
        target["exception"] = item.to_json()
        applied_exceptions.append(item.to_json())
    settings_present = {item.get("setting") for item in requirements if item.get("setting")}
    override_by_setting = {}
    for item in overrides:
        if item.setting not in settings_present:
            _fail("override_unknown_setting", f"override setting {item.setting} is not in the current selection")
        for clause in item.replaces:
            target = by_clause.get(clause)
            if target is None or target.get("setting") != item.setting:
                _fail("override_unknown_clause", f"override for {item.setting} replaces unknown clause {clause}")
            if target["level"] == "must" and target["state"] != "waived":
                resolution.problem("conflict", "override_requires_exception",
                                   f"override of must clause {clause} needs a matching valid exception", clause=clause)
        override_by_setting[item.setting] = item
    settings = {}
    for setting in sorted(settings_present):
        group = [item for item in requirements if item.get("setting") == setting]
        musts = [item for item in group if item["level"] == "must" and item["state"] == "mandatory"]
        defaults = [item for item in group if item["level"] == "default" and item["state"] == "default"]
        override = override_by_setting.get(setting)
        values = []
        for item in musts:
            if not any(_same_value(item["value"], value) for value in values):
                values.append(item["value"])
        if len(values) > 1:
            resolution.problem("conflict", "must_setting_conflict", f"must clauses disagree on {setting}",
                               setting=setting, clauses=[item["clause"] for item in musts])
            settings[setting] = {"state": "conflict", "clauses": [item["clause"] for item in group]}
            continue
        if override is not None:
            if musts and not _same_value(musts[0]["value"], override.value):
                resolution.problem("conflict", "override_conflicts_with_must",
                                   f"override for {setting} contradicts a mandatory clause", setting=setting)
            for item in defaults:
                item["state"] = "overridden" if item["clause"] in override.replaces else "suppressed"
                item["reason"] = f"explicit task override of {setting}"
            settings[setting] = {"state": "overridden", "value": override.value, "winner": "override",
                                 "scope": "explicit", "clauses": [item["clause"] for item in group]}
            continue
        if musts:
            for item in defaults:
                if not _same_value(item["value"], values[0]):
                    item["state"] = "suppressed"
                    item["reason"] = f"a mandatory clause sets {setting}"
            settings[setting] = {"state": "mandatory", "value": values[0], "winner": musts[0]["clause"],
                                 "scope": musts[0]["scope"], "clauses": [item["clause"] for item in group]}
            continue
        if not defaults:
            settings[setting] = {"state": "none", "clauses": [item["clause"] for item in group]}
            continue
        best = min(_SCOPE_RANK[item["scope"]] for item in defaults)
        top = [item for item in defaults if _SCOPE_RANK[item["scope"]] == best]
        if any(not _same_value(item["value"], top[0]["value"]) for item in top):
            resolution.problem("conflict", "default_setting_conflict",
                               f"same-scope defaults disagree on {setting}; choose one with an override",
                               setting=setting, clauses=[item["clause"] for item in top])
            settings[setting] = {"state": "conflict", "clauses": [item["clause"] for item in group]}
            continue
        for item in defaults:
            if _SCOPE_RANK[item["scope"]] > best and not _same_value(item["value"], top[0]["value"]):
                item["state"] = "suppressed"
                item["reason"] = f"a higher-precedence {top[0]['scope']} default sets {setting}"
        settings[setting] = {"state": "default", "value": top[0]["value"], "winner": top[0]["clause"],
                             "scope": top[0]["scope"], "clauses": [item["clause"] for item in group]}
    return settings, [item.to_json() for item in overrides], applied_exceptions


def _candidates(resolution: _Resolution) -> dict:
    ranked = []
    for loaded in resolution.sources.catalogs:
        if not loaded.active:
            continue
        for entry in loaded.catalog.entries:
            if (entry.id, entry.version, entry.sha256) in resolution.nodes:
                continue
            state, _ = effective_status(loaded, entry)
            if state not in ("approved", "deprecated"):
                continue
            decision = evaluate_selector(entry.applies_to, resolution.context)
            if decision.decision == "rejected":
                continue
            ranked.append((-len(decision.matched), loaded.catalog.source_id, entry.id, entry.version, entry,
                           decision, state))
    ranked.sort(key=lambda item: item[:4])
    items = []
    for _, source, _, _, entry, decision, state in ranked[:LIMITS.candidates]:
        items.append({"ref": ExactRef(source, entry.id, entry.version, entry.sha256).to_json(),
                      "summary": entry.summary[:LIMITS.candidate_summary], "decision": decision.decision,
                      "matched_keys": list(decision.matched), "missing_keys": list(decision.missing),
                      "effective_status": state, "advisory": True})
    return {"total": len(ranked), "items": items}


def _empty_report(status: str, diagnostics: list[dict], context_digest: Optional[str] = None,
                  metrics: Optional[dict] = None) -> dict:
    return {"schema_version": 1, "status": status, "context_digest": context_digest, "selection_digest": None,
            "sources": [],
            "selected": [], "candidates": {"total": 0, "items": []}, "requirements": [], "settings": {},
            "overrides": [], "exceptions": [], "diagnostics": diagnostics, "metrics": metrics or {}}


def _worst(statuses: Iterable[str], default: str) -> str:
    result = default
    for status in statuses:
        if _STATUS_RANK[status] > _STATUS_RANK[result]:
            result = status
    return result


def resolve(roots: Roots, context: Context, *, refs: Sequence[InvocationRef] = (),
            overrides: Sequence[Override] = (), exceptions: Sequence[ExceptionRecord] = (),
            preview_draft: bool = False, context_budget: int = LIMITS.context_budget,
            today: Optional[_dt.date] = None, reader: Optional[Reader] = None, explain: bool = False,
            attestations: Sequence[Mapping[str, Any]] = ()) -> dict:
    """Metadata-first resolution (spec section 5). Invalid input raises PatternError."""
    if type(context_budget) is not int or context_budget < 1:
        _fail("invalid_budget", "context budget must be a positive integer within the resource limit")
    today = today or _dt.datetime.now(_dt.timezone.utc).date()
    attestations = _as_attestations(attestations, "attestations")
    reader = reader or Reader()
    sources = load_sources(roots, reader)
    resolution = _Resolution(sources, context, preview_draft, today)
    for scope, binding, origin_id in sorted(sources.bindings, key=lambda item: (_SCOPE_RANK[item[0]], item[2], item[1].id)):
        decision = evaluate_selector(binding.when, context)
        resolution.bindings.append({"scope": scope, "origin": origin_id, "id": binding.id, "role": binding.role,
                                    "decision": decision.decision, "missing_keys": list(decision.missing),
                                    "mismatched_keys": list(decision.mismatched)})
        if decision.decision == "matched":
            for ref in binding.use:
                resolution.add(resolution.expand(ref, binding.role, scope, {
                    "kind": "binding", "binding": binding.id, "scope": scope, "origin": origin_id,
                    "approved_by": binding.approved_by, "approval_ref": binding.approval_ref}, False, scope))
        elif decision.decision == "needs-context" and binding.role == "required":
            resolution.problem("needs-context", "required_binding_needs_context",
                               f"required binding {scope}:{binding.id} needs facts: {', '.join(decision.missing)}",
                               binding=binding.id, scope=scope, missing_keys=list(decision.missing))
    for item in refs:
        resolution.add(resolution.expand(item.ref, item.role, resolution.scope_of(item.ref), {
            "kind": "explicit", "approved_by": item.approved_by, "approval_ref": item.approval_ref}, True, "explicit"))
    if len(resolution.nodes) > LIMITS.selected_patterns:
        _fail("resource_limit", f"more than {LIMITS.selected_patterns} selected patterns")
    identities = {}
    for node in resolution.nodes.values():
        other = identities.setdefault((node.ref.id, node.ref.version), node)
        if other is not node and other.ref.sha256 != node.ref.sha256:
            resolution.problem("conflict", "clause_identity_collision",
                               f"{node.ref.id}@{node.ref.version} is selected from two sources with different content",
                               refs=[other.ref.to_json(), node.ref.to_json()])
    requirements = []
    for key in sorted(resolution.nodes):
        node = resolution.nodes[key]
        must_under_default = False
        for clause in node.pattern.requirements:
            if clause.level == "must" and node.role != "required":
                must_under_default = True
                requirements.append(_clause_record(node, clause, "conflict", "must clause reached only by a default role"))
            elif clause.level == "must":
                requirements.append(_clause_record(node, clause, "mandatory"))
            elif clause.level == "default":
                requirements.append(_clause_record(node, clause, "default"))
            else:
                requirements.append(_clause_record(node, clause, "recommendation"))
        if must_under_default:
            resolution.problem("conflict", "must_under_default_binding",
                               f"{node.ref.text} has must clauses but is bound only as a default; "
                               "use a required binding or correct the pattern", ref=node.ref.to_json())
        if node.role == "required":
            _attestation_checks(resolution, node, attestations, roots)
        else:
            for index, source in enumerate(node.pattern.sources):
                if source.is_url:
                    resolution.diagnostics.append(_note(
                        "source_unverified_default", f"{node.ref.text} source {index} is an unverified URL; it is "
                        "only a default here, so it warns rather than blocks", "warning", ref=node.ref.to_json(),
                        source_index=index))
        if node.role != "required" and node.pattern.review_after and \
                _dt.date.fromisoformat(node.pattern.review_after) < today:
            resolution.diagnostics.append(_note("review_overdue_default", f"{node.ref.text} is past review_after",
                                                "warning", ref=node.ref.to_json()))
    requirements.sort(key=lambda item: item["clause"])
    settings, applied_overrides, applied_exceptions = _settle(resolution, requirements, overrides, exceptions)
    compact = [{key: item[key] for key in ("clause", "level", "state", "text", "verify", "setting", "value")
                if key in item} for item in requirements if item["state"] not in ("suppressed", "overridden")]
    selected_chars = len(canonical_json(compact).decode("utf-8"))
    if selected_chars > context_budget:
        resolution.problem("needs-context", "budget_exceeded",
                           f"selected context is {selected_chars} code points (budget {context_budget}); "
                           "split the work by task or component; no partial lock is written",
                           selected_code_points=selected_chars, budget=context_budget)
    candidates = _candidates(resolution)
    selected = []
    for key in sorted(resolution.nodes):
        node = resolution.nodes[key]
        selected.append({"ref": node.ref.to_json(), "role": node.role, "scope": node.scope,
                         "effective_status": node.effective, "summary": node.pattern.summary,
                         "reasons": node.reasons, "preview": node.preview,
                         "clauses": [node.pattern.clause_ref(clause.id) for clause in node.pattern.requirements],
                         "assets": [_asset_json(asset) for asset in node.pattern.assets],
                         "equivalent_refs": node.equivalents})
    statuses = [item["status"] for item in resolution.diagnostics if item.get("severity") == "error" and "status" in item]
    status = _worst(statuses, "ready" if selected else "empty")
    metrics = dict(reader.metrics(), selected_patterns=len(selected), selected_context_code_points=selected_chars,
                   advisory_summary_code_points=sum(len(item["summary"]) for item in candidates["items"]),
                   context_budget=context_budget, bindings_evaluated=len(resolution.bindings))
    report = {"schema_version": 1, "status": status, "context_digest": context.digest, "selection_digest": None,
              "sources": [item.summary() for item in sources.catalogs], "selected": selected,
              "candidates": candidates, "requirements": requirements, "settings": settings,
              "overrides": applied_overrides, "exceptions": applied_exceptions,
              "diagnostics": resolution.diagnostics, "metrics": metrics,
              "limits": "Runtime checks structure and declared provenance only; a repository can forge "
                        "bindings, and approval, source authenticity and prose conflicts need review.",
              "source_attestations": resolution.applied_attestations}
    if status in ("ready", "empty") and not any(item["preview"] for item in selected):
        report["selection_digest"] = selection_digest(_lock_material(report, context, refs))
    if explain:
        report["explanation"] = {"bindings": resolution.bindings,
                                 "precedence": ["explicit", "repo", "pack", "personal", "corpus"]}
    return report


# ---------------------------------------------------------------- inspection

def _inspection(status: str, sources: Optional[SourceSet], diagnostics: list[dict], **fields) -> dict:
    report = {"schema_version": 1, "status": status,
              "sources": [item.summary() for item in sources.catalogs] if sources else [],
              "diagnostics": diagnostics, "metrics": sources.reader.metrics() if sources else {}}
    report.update(fields)
    return report


def list_catalogs(roots: Roots, reader: Optional[Reader] = None) -> dict:
    """Catalog summaries only; zero pattern bodies or assets are read."""
    sources = load_sources(roots, reader)
    entries = []
    for loaded in sources.catalogs:
        for entry in loaded.catalog.entries:
            state, replacement = effective_status(loaded, entry)
            entries.append({"source": loaded.catalog.source_id, "scope": loaded.scope, "active": loaded.active,
                            **entry.to_json(), "effective_status": state,
                            "replaced_by": replacement.to_json() if replacement else None})
    entries.sort(key=lambda item: (item["source"], item["id"], item["version"]))
    diagnostics = list(sources.blockers) + list(sources.notes)
    status = _worst((item["status"] for item in sources.blockers), "ok")
    return _inspection(status, sources, diagnostics, entries=entries)


def show_pattern(roots: Roots, ref_text: str, reader: Optional[Reader] = None) -> dict:
    """One validated pattern body; exactly one pattern read."""
    source, pattern_id, version = parse_ref_text(ref_text)
    sources = load_sources(roots, reader)
    loaded = sources.by_source(source)
    if loaded is None:
        _fail("source_unavailable", f"source {source} is not configured here", status="unavailable")
    entry = loaded.catalog.entry(pattern_id, version)
    if entry is None:
        _fail("reference_missing", f"{ref_text} is not registered", status="unavailable")
    pattern = _read_pattern(sources, loaded, entry)
    state, replacement = effective_status(loaded, entry)
    return _inspection("ok", sources, list(sources.blockers) + list(sources.notes),
                       ref=ExactRef(source, pattern_id, version, entry.sha256).to_json(), scope=loaded.scope,
                       effective_status=state, replaced_by=replacement.to_json() if replacement else None,
                       pattern=pattern.raw)


DOCUMENT_KINDS = {
    "pattern": (lambda value: parse_pattern(value), LIMITS.pattern_bytes),
    "catalog": (lambda value: parse_catalog(value), LIMITS.catalog_bytes),
    "bindings": (lambda value: parse_bindings(value), LIMITS.input_bytes),
    "context": (lambda value: parse_context(value), LIMITS.input_bytes),
    "refs": (lambda value: parse_refs(value), LIMITS.input_bytes),
    "overrides": (lambda value: parse_overrides(value), LIMITS.input_bytes),
    "exceptions": (lambda value: parse_exceptions(value), LIMITS.input_bytes),
    "pack-context": (lambda value: parse_pack_context(value), LIMITS.input_bytes),
    "roots": (lambda value: parse_roots(value), LIMITS.input_bytes),
}
_KIND_BY_NAME = {"pattern.json": "pattern", "catalog.json": "catalog", "bindings.json": "bindings"}


def check_document(path: Path, kind: Optional[str] = None, reader: Optional[Reader] = None) -> dict:
    """Validate one explicit document; raises PatternError when invalid."""
    kind = kind or _KIND_BY_NAME.get(Path(path).name)
    if kind not in DOCUMENT_KINDS:
        _fail("unknown_kind", f"specify --kind as one of {', '.join(sorted(DOCUMENT_KINDS))}")
    parser, limit = DOCUMENT_KINDS[kind]
    reader = reader or Reader()
    value = parse_json(reader.read(Path(path), kind="input", limit=limit), limit=limit, what=kind)
    parser(value)
    return {"schema_version": 1, "status": "ok", "kind": kind, "sha256": content_digest(value),
            "diagnostics": [], "metrics": reader.metrics()}


def check_sources(roots: Roots, reader: Optional[Reader] = None) -> dict:
    """Explicit validation of every registered entry, including body digests and metadata."""
    sources = load_sources(roots, reader)
    diagnostics = list(sources.blockers) + list(sources.notes)
    checked = []
    for loaded in sources.catalogs:
        for entry in loaded.catalog.entries:
            try:
                pattern = _read_pattern(sources, loaded, entry)
                _declared_files(pattern, loaded.directory / PurePosixPath(entry.path).parent, reader=sources.reader,
                                what=f"{entry.id}@{entry.version}")
                for child in pattern.includes:
                    _lookup(sources, child)
                checked.append({"source": loaded.catalog.source_id, "id": entry.id, "version": entry.version,
                                "status": "ok"})
            except PatternError as error:
                diagnostics.append(dict(error.diagnostic(), source=loaded.catalog.source_id,
                                        id=entry.id, version=entry.version))
                checked.append({"source": loaded.catalog.source_id, "id": entry.id, "version": entry.version,
                                "status": error.status})
    status = _worst((item["status"] for item in diagnostics if item.get("severity") == "error"), "ok")
    return _inspection(status, sources, diagnostics, checked=checked)

# ---------------------------------------------------------------- write safety (shared by lock and lifecycle writes)

class _WriteLock:
    """Exclusive-creation lock beside a target; released only by its owner, never stolen."""

    def __init__(self, target: Path):
        self.path = Path(str(target) + ".lock")
        self.token = f"{os.getpid()}:{os.urandom(8).hex()}"

    def __enter__(self):
        try:
            descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            _fail("write_locked", f"another writer holds {self.path.name}; retry after it finishes "
                  "(stale locks are never stolen automatically)", status="collision")
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(self.token)
        return self

    def __exit__(self, *_):
        try:
            with open(self.path, encoding="utf-8") as stream:
                owned = stream.read() == self.token
        except OSError:
            return False
        if owned:
            os.unlink(self.path)
        return False


def _atomic_write(path: Path, data: bytes, *, replace: bool) -> None:
    """Write a complete temp file in the same directory, then publish it atomically.

    `replace=False` never overwrites an existing file (collision instead).
    """
    directory = path.parent
    if _is_link(directory) or not directory.is_dir():
        _fail("unsafe_path", "destination directory must exist and be unlinked", str(directory))
    temp = directory / f".{path.name}.{os.getpid()}.{os.urandom(4).hex()}.tmp"
    try:
        with open(temp, "xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if replace:
            os.replace(temp, path)
        elif os.name == "nt":
            try:
                os.rename(temp, path)
            except FileExistsError:
                _fail("destination_exists", f"refusing to overwrite {path.name}", str(path), status="collision")
        else:
            try:
                os.link(temp, path)
            except FileExistsError:
                _fail("destination_exists", f"refusing to overwrite {path.name}", str(path), status="collision")
    finally:
        if temp.exists():
            os.unlink(temp)


def _repository_file(roots: Roots, path: Path, what: str) -> Path:
    """A write target contained in the explicit repository root, with no linked components."""
    if roots.repository is None:
        _fail("repository_required", f"{what} needs an explicit repository root", status="invalid")
    base = roots.repository.resolve()
    candidate = Path(path)
    candidate = candidate if candidate.is_absolute() else Path.cwd() / candidate
    try:
        relative = candidate.resolve().relative_to(base)
    except ValueError:
        _fail("unsafe_path", f"{what} must be inside the repository root", str(path))
    return contained_path(base, relative.as_posix(), what)


# ---------------------------------------------------------------- locks (spec 4.4, card 2.2.b)

LOCK_ADDED_KEYS = ("context", "created_at", "source_snapshots", "asset_pins",
                   "requirement_tasks", "source_attestations", "review_evidence", "invocation_refs",
                   "context_budget")
LOCK_KEYS = REPORT_KEYS + ("limits",) + LOCK_ADDED_KEYS
SELECTED_KEYS = ("ref", "role", "scope", "effective_status", "summary", "reasons", "preview", "clauses", "assets",
                 "equivalent_refs")
_EFFECTIVE_MANDATORY = ("mandatory", "waived")


def _context_json(context: Context) -> dict:
    return {"schema_version": 1, "facts": dict(context.facts), "evidence": dict(context.evidence)}


def _selection_material(lock: Mapping[str, Any]) -> dict:
    """Digest input: complete selected records (refs, roles, scopes, reasons, equivalent refs, clause
    IDs, declared assets), requirements, settings, overrides, exceptions, context, source snapshots
    and invocation refs. Excludes timestamps, metrics, diagnostics, attestations, mapping and evidence.
    `asset_pins` is derived from `selected[].assets` and checked for equality, not digested twice.
    """
    return {"context": lock["context"], "source_snapshots": lock["source_snapshots"],
            "selected": lock["selected"],
            "requirements": lock["requirements"], "settings": lock["settings"],
            "overrides": lock["overrides"], "exceptions": lock["exceptions"],
            "invocation_refs": lock["invocation_refs"], "context_budget": lock["context_budget"]}


def selection_digest(lock: Mapping[str, Any]) -> str:
    return content_digest(_selection_material(lock))


def _invocation_json(item: InvocationRef) -> dict:
    return {"ref": item.ref.to_json(), "role": item.role, "approved_by": item.approved_by,
            "approval_ref": item.approval_ref}


def _snapshots(report: Mapping[str, Any]) -> list[dict]:
    return [{key: item[key] for key in ("locator", "source_id", "scope", "active", "catalog_sha256")}
            for item in report["sources"]]


def _lock_material(report: Mapping[str, Any], context: Context, refs: Sequence[InvocationRef]) -> dict:
    """The one definition of selection content shared by the report and the lock (F7)."""
    return {"context": _context_json(context), "source_snapshots": _snapshots(report),
            "selected": report["selected"], "requirements": report["requirements"], "settings": report["settings"],
            "overrides": report["overrides"], "exceptions": report["exceptions"],
            "invocation_refs": [_invocation_json(item) for item in refs],
            "context_budget": report["metrics"]["context_budget"]}


def build_lock(report: Mapping[str, Any], context: Context, *, refs: Sequence[InvocationRef] = (),
               context_budget: int = LIMITS.context_budget, now: Optional[_dt.datetime] = None) -> dict:
    """Freeze a ready/empty report. Conflicts, unknown context and previews never lock."""
    if report.get("status") not in ("ready", "empty"):
        _fail("lock_refused", f"only ready or empty resolutions can be locked (status {report.get('status')})",
              status=report.get("status") if report.get("status") in EXIT_CODES else "invalid")
    if any(item.get("preview") for item in report["selected"]):
        _fail("lock_refused", "a draft preview is never locked", status="unavailable")
    if report.get("context_digest") != context.digest:
        _fail("lock_refused", "the report was resolved for a different context")
    if report.get("metrics", {}).get("context_budget") != context_budget:
        _fail("lock_refused", "the lock's context budget must be the one the report was resolved with")
    now = now or _dt.datetime.now(_dt.timezone.utc)
    lock = {key: copy_json(report[key]) for key in REPORT_KEYS + ("limits",)}
    lock.update(
        context=_context_json(context),
        created_at=now.astimezone(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        source_snapshots=_snapshots(report),
        asset_pins=asset_refs(report),
        requirement_tasks=None, source_attestations=copy_json(report.get("source_attestations", [])),
        review_evidence=[],
        invocation_refs=[_invocation_json(item) for item in refs], context_budget=context_budget)
    lock["selection_digest"] = selection_digest(lock)
    if report.get("selection_digest") != lock["selection_digest"]:
        _fail("lock_refused", "the report's selection_digest does not match its content or invocation refs")
    try:
        parse_lock(lock)
    except PatternError as error:
        _fail("lock_refused", f"the lock would be invalid at its creation time {lock['created_at']}: {error.message}; "
              "re-resolve at that time (for example, an exception has expired)")
    return lock


def copy_json(value: Any) -> Any:
    return json.loads(canonical_json(value).decode("utf-8"))


def _assert_portable(lock: Mapping[str, Any], roots: Roots) -> None:
    """Durable locks carry locators and source IDs, never local absolute roots (spec 4.4)."""
    text = canonical_json(lock).decode("utf-8")
    probes = {Path(roots.personal).resolve().as_posix(), str(Path(roots.personal).resolve())}
    if roots.repository is not None:
        probes |= {roots.repository.resolve().as_posix(), str(roots.repository.resolve())}
    for ancestor in roots.pack_context.ancestry:
        probes |= {ancestor.root.as_posix(), str(ancestor.root)}
    escaped = {json.dumps(item, ensure_ascii=False)[1:-1] for item in probes}
    if any(item and (item in text or item.casefold() in text.casefold()) for item in probes | escaped):
        _fail("lock_not_portable", "the lock would contain a local absolute root; refusing to write it")


def write_lock(roots: Roots, path: Path, lock: Mapping[str, Any]) -> dict:
    target = _repository_file(roots, path, "lock")
    _assert_portable(lock, roots)
    data = emit_json(lock).encode("utf-8")
    _atomic_write(target, data, replace=False)
    return {"path": target.resolve().relative_to(roots.repository.resolve()).as_posix(),
            "lock_sha256": content_digest(lock), "selection_digest": lock["selection_digest"]}


def parse_lock(value: Any, where: str = "lock") -> dict:
    """Validate structure and self-consistency; tampered clause/selection content is invalid."""
    _object(value, where, LOCK_KEYS)
    _schema_version(value, where)
    if value["status"] not in ("ready", "empty"):
        _fail("invalid_lock", "a lock records only a ready or empty resolution", where)
    if value["status"] != ("ready" if _array(value["selected"], f"{where}.selected") else "empty"):
        _fail("invalid_lock", "status must be ready exactly when patterns are selected", where)
    context = parse_context(value["context"], f"{where}.context")
    if context.digest != value["context_digest"]:
        _fail("invalid_lock", "context_digest does not match the stored context", where)
    _timestamp(value["created_at"], f"{where}.created_at")
    for index, item in enumerate(_array(value["source_snapshots"], f"{where}.source_snapshots")):
        at = f"{where}.source_snapshots[{index}]"
        _object(item, at, ("locator", "source_id", "scope", "active", "catalog_sha256"))
        _matching(item["source_id"], NAMESPACED_ID, at, "source ID")
        _matching(item["catalog_sha256"], HEX64, at, "catalog digest", 64)
    for index, item in enumerate(_array(value["selected"], f"{where}.selected")):
        at = f"{where}.selected[{index}]"
        if not isinstance(item, dict) or item.get("preview") is not False:
            _fail("invalid_lock", "selected records must be non-preview selections", at)
        _object(item, at, SELECTED_KEYS)
        ref = parse_exact_ref(item.get("ref"), f"{at}.ref")
        if item.get("role") not in ("required", "default") or item.get("scope") not in ("repo", "pack", "personal"):
            _fail("invalid_lock", "invalid selection role or scope", at)
        equivalents = [parse_exact_ref(entry, f"{at}.equivalent_refs") for entry in _array(item["equivalent_refs"], at)]
        if ref not in equivalents or any((entry.id, entry.version, entry.sha256) != (ref.id, ref.version, ref.sha256)
                                         for entry in equivalents):
            _fail("invalid_lock", "equivalent_refs must list the same content, including the primary ref", at)
        if not _array(item["reasons"], f"{at}.reasons", nonempty=True) or \
                not all(isinstance(reason, dict) and reason.get("kind") in ("binding", "explicit", "include")
                        for reason in item["reasons"]):
            _fail("invalid_lock", "each selection needs its binding, explicit or include reasons", at)
        for asset_index, asset in enumerate(_array(item["assets"], f"{at}.assets")):
            _object(asset, f"{at}.assets[{asset_index}]", ("path", "kind", "sha256"), ("phases", "domains"))
    if value["asset_pins"] != asset_refs(value):
        _fail("invalid_lock", "asset_pins must equal the assets declared by the selected records", where)
    declared = sorted(clause for item in value["selected"] for clause in item["clauses"])
    recorded = sorted(item["clause"] for item in value["requirements"] if isinstance(item, dict))
    if declared != recorded:
        _fail("invalid_lock", "requirements must list exactly the clauses of the selected records", where)
    clause_ids = set()
    for index, item in enumerate(_array(value["requirements"], f"{where}.requirements")):
        at = f"{where}.requirements[{index}]"
        if not isinstance(item, dict):
            _fail("invalid_lock", "requirement records are objects", at)
        clause_ids.add(_fq_clause(item.get("clause"), f"{at}.clause"))
        if item.get("level") not in ("must", "default", "recommendation") or item.get("state") not in (
                "mandatory", "default", "recommendation", "suppressed", "overridden", "waived"):
            _fail("invalid_lock", "invalid clause level or state", at)
    parse_refs(value["invocation_refs"], f"{where}.invocation_refs")
    if type(value["context_budget"]) is not int or value["context_budget"] < 1:
        _fail("invalid_lock", "context_budget must be a positive integer", where)
    _check_lock_settings(value, where)
    if value["selection_digest"] != selection_digest(value):
        _fail("invalid_lock", "selection_digest does not match the lock content: it was edited or corrupted, or was "
              "produced before contract revision R4 (pre-release); regenerate the lock with resolve --lock", where)
    if value["requirement_tasks"] is not None:
        mapping = dict(value["requirement_tasks"])
        recorded = mapping.pop("mapping_digest", None)
        parse_task_map(mapping, value, f"{where}.requirement_tasks")
        if recorded != content_digest(mapping):
            _fail("invalid_lock", "requirement_tasks mapping_digest does not match its record", where)
    _as_attestations(_array(value["source_attestations"], f"{where}.source_attestations"),
                     f"{where}.source_attestations")
    _array(value["review_evidence"], f"{where}.review_evidence")
    return value


def _mandatory(requirements: Iterable[Mapping[str, Any]]) -> set:
    return {item["clause"] for item in requirements if item["level"] == "must" and item["state"] in _EFFECTIVE_MANDATORY}


def verify_lock(roots: Roots, lock: Mapping[str, Any], context: Context, *,
                today: Optional[_dt.date] = None, reader: Optional[Reader] = None,
                attestations: Sequence[Mapping[str, Any]] = ()) -> dict:
    """Continuation check: pins, current lifecycle/revocations, context and mandatory baseline.

    Never upgrades or rewrites the lock; the original snapshots stay historical evidence.
    """
    lock = parse_lock(lock)
    attestations = _as_attestations(attestations, "attestations")
    reader = reader or Reader()
    sources = load_sources(roots, reader)
    diagnostics = [dict(item) for item in sources.blockers]
    checked = []

    def problem(status, code, message, **details):
        diagnostics.append(_note(code, message, "error", status=status, **details))

    if context.digest != lock["context_digest"]:
        problem("conflict", "context_changed", "the current context differs from the locked context; re-plan",
                locked=lock["context_digest"], current=context.digest)
    pinned = [(item, parse_exact_ref(equivalent, "lock.selected.equivalent_refs"))
              for item in lock["selected"] for equivalent in item["equivalent_refs"]]
    for item, ref in pinned:
        try:
            loaded, entry = _lookup(sources, ref)
            state, _ = effective_status(loaded, entry)
            if state in ("retired", "revoked"):
                _fail(f"pinned_{state}", f"pinned {ref.text} is now {state}", status="unavailable")
            body = _read_pattern(sources, loaded, entry)
            derived = {"summary": body.summary, "clauses": [body.clause_ref(clause.id) for clause in body.requirements],
                       "assets": [_asset_json(asset) for asset in body.assets]}
            if {key: item[key] for key in derived} != derived:
                _fail("lock_content_mismatch", f"the lock's record of {ref.text} does not match its pinned bytes "
                      "(summary, clauses or assets); the lock was edited", "lock.selected")
            if state == "deprecated":
                diagnostics.append(_note("pinned_deprecated", f"pinned {ref.text} is deprecated", "warning",
                                         ref=ref.to_json()))
            checked.append({"ref": ref.to_json(), "status": "ok", "effective_status": state})
        except PatternError as error:
            if error.status == "invalid":
                raise
            diagnostics.append(dict(error.diagnostic(), ref=ref.to_json(), role=item["role"]))
            checked.append({"ref": ref.to_json(), "status": error.status})
    baseline = None
    current = None
    if not any(item.get("severity") == "error" for item in diagnostics):
        refs = parse_refs(lock["invocation_refs"])
        overrides = parse_overrides({"schema_version": 1, "items": lock["overrides"]})
        exceptions = parse_exceptions({"schema_version": 1, "items": lock["exceptions"]})
        try:
            merged = merge_attestations(lock["source_attestations"], attestations)
            current = resolve(roots, context, refs=refs, overrides=overrides, exceptions=exceptions,
                              context_budget=lock["context_budget"], today=today, reader=reader,
                              attestations=merged)
        except PatternError as error:
            problem("conflict", "replan_required", f"the locked inputs no longer resolve: {error.message}",
                    cause=error.code)
            current = None
        if current is not None:
            for item in current["diagnostics"]:
                if item.get("severity") == "error":
                    diagnostics.append(dict(item))
            old, new = _mandatory(lock["requirements"]), _mandatory(current["requirements"])
            if old != new:
                baseline = {"locked": sorted(old), "current": sorted(new), "added": sorted(new - old),
                            "removed": sorted(old - new)}
                problem("conflict", "mandatory_baseline_changed",
                        "current bindings change the mandatory clauses for this context; re-plan with a new lock",
                        added=baseline["added"], removed=baseline["removed"])
            now_digests = {item.catalog.source_id: item.catalog.digest for item in sources.catalogs}
            unchanged = {item["source_id"] for item in lock["source_snapshots"]
                         if now_digests.get(item["source_id"]) == item["catalog_sha256"]}
            _compare_selection(lock, current, problem, diagnostics, unchanged)
    statuses = [item["status"] for item in diagnostics if item.get("severity") == "error" and item.get("status")]
    status = _worst(statuses, "ok")
    mapping = lock["requirement_tasks"]
    return {"schema_version": 1, "status": status, "selection_digest": lock["selection_digest"],
            "mapping_digest": mapping["mapping_digest"] if mapping else None,
            "source_attestations": current["source_attestations"] if current is not None else [],
            "context_digest": context.digest, "checked": checked, "baseline": baseline,
            "historical_sources": lock["source_snapshots"], "diagnostics": diagnostics,
            "metrics": reader.metrics()}



def _identity_of(record: Mapping[str, Any]) -> tuple[str, str, str]:
    return (record["ref"]["id"], record["ref"]["version"], record["ref"]["sha256"])


_SELECTED_COMPARED = ("ref", "role", "scope", "summary", "reasons", "preview", "clauses", "assets", "equivalent_refs")


def _compare_selection(lock: Mapping[str, Any], current: Mapping[str, Any], problem, diagnostics: list,
                       unchanged_sources: set) -> None:
    """Strict comparison of the locked selection with a fresh resolution of the same inputs (R5).

    Any difference in the selected set, a record, a requirement record or a setting is a conflict
    that forces a re-plan, including added or removed defaults: spec 4.4 permits no silent change,
    and an unkeyed lock cannot tell a later binding change from a resealed omission. Unbound catalog
    additions do not change the resolution and pass. The only tolerated difference is a pin that is
    deprecated now but was approved in the lock, and only when that pin's catalog changed since
    locking (a real later deprecation, reported as `pinned_deprecated`). The lock's
    `effective_status` is historical; `checked[].effective_status` is the current status.
    """
    locked = {_identity_of(item): item for item in lock["selected"]}
    fresh = {_identity_of(item): item for item in current["selected"]}
    for key in sorted(locked.keys() - fresh.keys()):
        problem("conflict", "selection_changed", f"{key[0]}@{key[1]} is in the lock but not in the current "
                "selection; re-plan with a new lock", ref=locked[key]["ref"])
    for key in sorted(fresh.keys() - locked.keys()):
        problem("conflict", "selection_changed", f"{key[0]}@{key[1]} ({fresh[key]['role']}) is selected now but "
                "absent from the lock; re-plan with a new lock", ref=fresh[key]["ref"])
    for key in sorted(locked.keys() & fresh.keys()):
        old, new = locked[key], fresh[key]
        changed = sorted(field for field in _SELECTED_COMPARED if canonical_json(old[field]) != canonical_json(new[field]))
        later_deprecation = (old["effective_status"] == "approved" and new["effective_status"] == "deprecated"
                             and new["ref"]["source"] not in unchanged_sources)
        if old["effective_status"] != new["effective_status"] and not later_deprecation:
            changed.append("effective_status")
        if changed:
            problem("conflict", "selection_provenance_changed",
                    f"{key[0]}@{key[1]} is now selected with different {', '.join(sorted(changed))}; re-plan",
                    ref=old["ref"], fields=sorted(changed))
    old_clauses = {item["clause"]: item for item in lock["requirements"]}
    new_clauses = {item["clause"]: item for item in current["requirements"]}
    for clause in sorted(old_clauses.keys() ^ new_clauses.keys()):
        where = "lock" if clause in old_clauses else "current resolution"
        problem("conflict", "requirement_changed", f"{clause} is only in the {where}; re-plan with a new lock",
                clause=clause)
    for clause in sorted(old_clauses.keys() & new_clauses.keys()):
        if canonical_json(old_clauses[clause]) != canonical_json(new_clauses[clause]):
            fields = sorted(key for key in set(old_clauses[clause]) | set(new_clauses[clause])
                            if canonical_json(old_clauses[clause].get(key)) != canonical_json(new_clauses[clause].get(key)))
            problem("conflict", "requirement_changed", f"{clause} differs from the current resolution ({', '.join(fields)})",
                    clause=clause, fields=fields)
    for name in sorted(set(lock["settings"]) | set(current["settings"])):
        if canonical_json(lock["settings"].get(name)) != canonical_json(current["settings"].get(name)):
            problem("conflict", "setting_changed", f"setting {name} differs from the current resolution",
                    setting=name)
    for field in ("overrides", "exceptions"):
        if canonical_json(lock[field]) != canonical_json(current[field]):
            problem("conflict", "selection_changed", f"locked {field} differ from the current resolution")


class _SettleCheck:
    """Minimal resolution stand-in so a lock's settings are re-derived by the same `_settle` logic."""

    def __init__(self, context_digest: str, today: _dt.date):
        self.context = type("LockContext", (), {"digest": context_digest})()
        self.today = today
        self.conflicts: list[str] = []

    def problem(self, status, code, message, **_details):
        self.conflicts.append(f"{code}: {message}")


def _check_lock_settings(value: Mapping[str, Any], where: str) -> None:
    """A lock's requirement states and settings must be exactly what `_settle` derives from its own
    clauses, overrides and exceptions (evaluated at the lock's own creation date)."""
    pristine = []
    for item in value["requirements"]:
        record = {key: item[key] for key in item if key not in ("state", "reason", "exception")}
        if item["level"] == "must":
            if item.get("role") != "required":
                _fail("invalid_lock", f"{item['clause']} is a must clause without a required role", where)
            record["state"] = "mandatory"
        else:
            record["state"] = item["level"]
        pristine.append(record)
    check = _SettleCheck(value["context_digest"], _instant(value["created_at"]).date())
    try:
        settings, overrides, exceptions = _settle(
            check, pristine, parse_overrides({"schema_version": 1, "items": value["overrides"]}),
            parse_exceptions({"schema_version": 1, "items": value["exceptions"]}))
    except PatternError as error:
        _fail("invalid_lock", f"the lock's overrides or exceptions do not settle: {error.message}", where)
    if check.conflicts:
        _fail("invalid_lock", f"the lock's own clauses conflict: {'; '.join(check.conflicts)}", where)
    if canonical_json(pristine) != canonical_json(value["requirements"]) or \
            canonical_json(settings) != canonical_json(value["settings"]) or \
            canonical_json(overrides) != canonical_json(value["overrides"]) or \
            canonical_json(exceptions) != canonical_json(value["exceptions"]):
        _fail("invalid_lock", "the lock's requirement states or settings are not what its own clauses, overrides "
              "and exceptions produce (internally inconsistent)", where)

# ---------------------------------------------------------------- task mapping (spec 4.6, card 2.2.c)

def _task_id(value: Any, where: str) -> str:
    return _string(value, where, limit=256)


def parse_task_map(value: Any, lock: Mapping[str, Any], where: str = "task_map") -> dict:
    """Validate a companion task map against a lock; returns the canonical record."""
    _object(value, where, ("schema_version", "selection_digest", "tasks", "packages", "clauses"))
    _schema_version(value, where)
    if value["selection_digest"] != lock["selection_digest"]:
        _fail("mapping_selection_mismatch", "the task map was made for a different selection", where)
    tasks = [_task_id(item, f"{where}.tasks") for item in _array(value["tasks"], f"{where}.tasks", nonempty=True)]
    if len(set(tasks)) != len(tasks):
        _fail("invalid_task_map", "duplicate task IDs", f"{where}.tasks")
    owner, package_ids = {}, set()
    for index, package in enumerate(_array(value["packages"], f"{where}.packages", nonempty=True)):
        at = f"{where}.packages[{index}]"
        _object(package, at, ("id", "tasks"))
        package_id = _task_id(package["id"], f"{at}.id")
        if package_id in package_ids:
            _fail("invalid_task_map", f"duplicate package {package_id}", at)
        package_ids.add(package_id)
        members = [_task_id(item, f"{at}.tasks") for item in _array(package["tasks"], f"{at}.tasks", nonempty=True)]
        for task in members:
            if task not in tasks:
                _fail("invalid_task_map", f"unknown task {task}", at)
            if task in owner:
                _fail("invalid_task_map", f"task {task} belongs to two packages", at)
            owner[task] = package_id
    unowned = sorted(set(tasks) - owner.keys())
    if unowned:
        _fail("invalid_task_map", f"tasks without a package: {', '.join(unowned)}", f"{where}.packages")
    known = {item["clause"]: item for item in lock["requirements"]}
    mapped = {}
    for index, item in enumerate(_array(value["clauses"], f"{where}.clauses")):
        at = f"{where}.clauses[{index}]"
        _object(item, at, ("clause", "tasks"))
        clause_id = _fq_clause(item["clause"], f"{at}.clause")
        if clause_id not in known:
            _fail("invalid_task_map", f"unknown clause {clause_id}", at)
        if clause_id in mapped:
            _fail("invalid_task_map", f"duplicate clause record {clause_id}", at)
        members = [_task_id(task, f"{at}.tasks") for task in _array(item["tasks"], f"{at}.tasks", nonempty=True)]
        if len(set(members)) != len(members) or any(task not in tasks for task in members):
            _fail("invalid_task_map", f"clause {clause_id} maps duplicate or unknown tasks", at)
        mapped[clause_id] = members
    required = sorted(clause for clause, item in known.items()
                      if (item["level"] == "must" and item["state"] in _EFFECTIVE_MANDATORY)
                      or (item["level"] == "default" and item["state"] == "default"))
    missing = [clause for clause in required if clause not in mapped]
    if missing:
        _fail("unmapped_clause", f"selected must/default clauses without a task: {', '.join(missing)}", where)
    return value


def map_lock(roots: Roots, lock_path: Path, task_map_value: Any, *, expected_lock_digest: str,
             write: bool = False, reader: Optional[Reader] = None) -> dict:
    """Preview (default) or atomically install requirement_tasks under CAS + exclusive lock."""
    reader = reader or Reader()
    target = _repository_file(roots, lock_path, "lock") if write else Path(lock_path)

    def load():
        return parse_json(reader.read(target, kind="input", limit=LIMITS.catalog_bytes),
                          limit=LIMITS.catalog_bytes, what="lock")

    def plan(lock):
        parse_lock(lock)
        digest = content_digest(lock)
        if digest != expected_lock_digest:
            _fail("stale_lock_digest", "the lock changed since it was read; re-read and retry", status="collision")
        mapping = copy_json(parse_task_map(task_map_value, lock))
        mapping_digest = content_digest(mapping)
        installed = dict(mapping, mapping_digest=mapping_digest)
        previous = lock["requirement_tasks"]["mapping_digest"] if lock["requirement_tasks"] else None
        invalidated = sum(1 for item in lock["review_evidence"]
                          if isinstance(item, dict) and item.get("mapping_digest") != mapping_digest)
        updated = dict(lock, requirement_tasks=installed)
        return updated, {"schema_version": 1, "status": "ok", "written": False,
                         "selection_digest": lock["selection_digest"], "mapping_digest": mapping_digest,
                         "previous_mapping_digest": previous, "invalidated_review_evidence": invalidated,
                         "requirement_tasks": installed, "diagnostics": [], "metrics": reader.metrics()}

    if not write:
        return plan(load())[1]
    with _WriteLock(target):
        updated, report = plan(load())
        if selection_digest(updated) != updated["selection_digest"]:
            _fail("invalid_lock", "mapping must not change the selection digest")
        _assert_portable(updated, roots)
        _atomic_write(target, emit_json(updated).encode("utf-8"), replace=True)
    report.update(written=True, lock_sha256=content_digest(updated), metrics=reader.metrics())
    return report


def project_package(lock: Mapping[str, Any], task_map_value: Any, package: str) -> dict:
    """Clauses mapped to one package with IDs and completeness preserved; never a silent top-N."""
    lock = parse_lock(lock)
    mapping = parse_task_map(task_map_value, lock)
    mapping_digest = content_digest(copy_json(mapping))
    packages = {item["id"]: item["tasks"] for item in mapping["packages"]}
    if package not in packages:
        _fail("unknown_package", f"package {package} is not in the task map")
    members = set(packages[package])
    by_clause = {item["clause"]: item for item in lock["requirements"]}
    clauses = []
    for item in mapping["clauses"]:
        tasks = [task for task in item["tasks"] if task in members]
        if tasks:
            clauses.append(dict(copy_json(by_clause[item["clause"]]), task_ids=tasks))
    clauses.sort(key=lambda item: item["clause"])
    settings = {key: value for key, value in lock["settings"].items()
                if any(clause["clause"] in value.get("clauses", []) for clause in clauses)}
    diagnostics = []
    installed = lock["requirement_tasks"]
    if installed is None or installed["mapping_digest"] != mapping_digest:
        diagnostics.append(_note("mapping_not_installed",
                                 "this task map is not the one installed in the lock; run map --write", "warning"))
    return {"schema_version": 1, "status": "ok", "selection_digest": lock["selection_digest"],
            "mapping_digest": mapping_digest, "package": package, "tasks": sorted(members),
            "clauses": clauses, "settings": settings, "diagnostics": diagnostics}

# ---------------------------------------------------------------- publication (spec 7, cards 3.1.a-3.1.c)

def _scope_root(roots: Roots, scope: str) -> tuple[Path, str]:
    if scope == "repo":
        if roots.repository is None:
            _fail("repository_required", "repository scope needs an explicit repository root")
        base, parts = roots.repository, (".claude", "patterns")
    elif scope == "personal":
        base, parts = roots.personal, ("patterns",)
    else:
        _fail("invalid_scope", "scope must be repo or personal; packs publish through their own review")
    return contained_path(base, "/".join(parts), f"{scope} source root"), scope


def _root_for_path(roots: Roots, path: Path) -> tuple[Path, str, str]:
    """Map an explicit file path to (source root, locator, portable relative path)."""
    candidate = Path(path)
    candidate = (candidate if candidate.is_absolute() else Path.cwd() / candidate).resolve()
    for scope in ("repo", "personal"):
        if scope == "repo" and roots.repository is None:
            continue
        root, _ = _scope_root(roots, scope)
        try:
            relative = candidate.relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
        contained_path(root, relative, "pattern path")
        return root, scope, relative
    _fail("unsafe_path", "path is not inside a repository or personal pattern source root", str(path))


def _read_catalog_value(root: Path, reader: Reader) -> tuple[Optional[dict], Optional[str]]:
    data = reader.read(contained_path(root, "catalog.json"), kind="catalog", limit=LIMITS.catalog_bytes,
                       optional=True)
    if data is None:
        return None, None
    value = parse_json(data, limit=LIMITS.catalog_bytes, what="catalog")
    parse_catalog(value, str(root / "catalog.json"))
    return value, content_digest(value)


def _entry_for(pattern: Pattern, relative: str) -> dict:
    return {"id": pattern.id, "version": pattern.version, "path": relative, "sha256": pattern.digest,
            "summary": pattern.summary, "status": pattern.status, "applies_to": pattern.applies_to.to_json()}


def _check_cas(current: Optional[str], expected: Optional[str], what: str, *, obj: str = "catalog",
               flag: str = "--expected-catalog-digest") -> None:
    if current is None and expected is not None:
        _fail(f"stale_{obj}_digest", f"{what}: no {obj} file exists yet; omit {flag}", status="collision")
    if current is not None and expected is None:
        _fail("expected_digest_required", f"{what}: supply {flag} {current} (the current {obj} digest)",
              status="collision")
    if current is not None and expected != current:
        _fail(f"stale_{obj}_digest", f"{what}: the {obj} changed since it was read; re-read and retry",
              status="collision")


def _stage_pattern(root: Path, pattern: Pattern) -> tuple[str, bool]:
    """Write immutable content before the catalog. Returns (relative path, recovered_staging)."""
    relative = f"{pattern.id}/{pattern.version}/pattern.json"
    target = contained_path(root, relative, "pattern destination")
    data = emit_json(pattern.raw).encode("utf-8")
    if target.exists():
        existing = Reader().read(target, kind="pattern", limit=LIMITS.pattern_bytes)
        try:
            same = content_digest(parse_json(existing, limit=LIMITS.pattern_bytes, what="staged pattern")) == pattern.digest
        except PatternError:
            same = False
        if not same:
            _fail("unregistered_staging_conflict",
                  f"an unregistered file already occupies {relative}; inspect it before publishing",
                  str(target), status="collision")
        return relative, True
    for parent in (target.parent.parent, target.parent):
        if _is_link(parent):
            _fail("unsafe_path", "linked destination directory refused", str(parent))
        parent.mkdir(exist_ok=True)
    _atomic_write(target, data, replace=False)
    return relative, False


def _stage_file(root: Path, relative: str, data: bytes) -> None:
    """Stage one immutable non-pattern file (an imported asset); identical bytes are a completed retry."""
    target = contained_path(root, relative, "staged file")
    if target.exists():
        if Reader().read(target, kind="asset", limit=LIMITS.asset_bytes) != data:
            _fail("unregistered_staging_conflict", f"an unregistered file already occupies {relative}",
                  str(target), status="collision")
        return
    parts = PurePosixPath(relative).parts[:-1]
    current = root
    for part in parts:
        current = current / part
        if _is_link(current):
            _fail("unsafe_path", "linked destination directory refused", str(current))
        current.mkdir(exist_ok=True)
    _atomic_write(target, data, replace=False)


def _declared_files(pattern: Pattern, source_dir: Optional[Path], *, fallback_dir: Optional[Path] = None,
                    reader: Optional[Reader] = None, what: str = "pattern") -> list[tuple[str, bytes]]:
    """The exact local file closure of one version: declared assets (digest-verified) and
    `root: pattern` sources (verified against any pinned sha256). Nothing else is ever copied.

    Each file is read contained under `source_dir`, falling back to `fallback_dir` (the previous
    version) for an asset whose digest matches there. A missing or changed file fails before any write.
    """
    reader = reader or Reader()
    wanted: dict[str, Optional[str]] = {}
    for asset in pattern.assets:
        wanted[asset.path] = asset.sha256
    for source in pattern.sources:
        if source.root == "pattern":
            path = str(validate_relative_path(source.ref, "source"))
            pinned = source.sha256
            if path in wanted and wanted[path] is not None and pinned is not None and pinned != wanted[path]:
                _fail("declared_file_conflict", f"{what}: {path} is declared with two different digests")
            wanted[path] = wanted.get(path) or pinned
    result = []
    for path in sorted(wanted):
        expected = wanted[path]
        data = None
        for base in (source_dir, fallback_dir):
            if base is None:
                continue
            candidate = reader.read(contained_path(base, path, f"{what} file"), kind="asset", limit=LIMITS.asset_bytes,
                                    optional=True)
            if candidate is not None and (expected is None or hashlib.sha256(candidate).hexdigest() == expected):
                data = candidate
                break
            if candidate is not None and base is source_dir:
                _fail("declared_file_changed", f"{what}: {path} does not match its declared sha256", status="unavailable")
        if data is None:
            _fail("declared_file_missing", f"{what}: declared file {path} is missing; supply it before publishing",
                  status="unavailable")
        result.append((path, data))
    return result


def _preflight(root: Path, files: Sequence[tuple[str, bytes]]) -> None:
    """Check every destination before the first write: absent, or identical bytes (a completed retry)."""
    for relative, data in files:
        target = contained_path(root, relative, "destination")
        if target.exists():
            existing = Reader().read(target, kind="asset", limit=max(LIMITS.asset_bytes, LIMITS.pattern_bytes))
            same = existing == data
            if not same and relative.endswith("/pattern.json"):
                try:
                    same = content_digest(parse_json(existing, limit=LIMITS.pattern_bytes, what="staged")) == \
                        content_digest(parse_json(data, limit=LIMITS.pattern_bytes, what="staged"))
                except PatternError:
                    same = False
            if not same:
                _fail("unregistered_staging_conflict", f"an unregistered file already occupies {relative}; inspect "
                      "it before publishing", str(target), status="collision")


def _publish(root: Path, reader: Reader, *, expected: Optional[str], build, cas_required: bool = True) -> dict:
    """Exclusive per-root lock, CAS, stage immutable content, then replace the catalog last.

    `build` receives the catalog read inside the lock; every check it makes uses that preimage.
    With `cas_required=False` an omitted `expected` means the in-lock preimage is authoritative;
    a supplied `expected` is always enforced.
    """
    if _is_link(root):
        _fail("unsafe_path", "linked source root refused", str(root))
    root.mkdir(parents=True, exist_ok=True)
    with _WriteLock(root / "catalog.json"):
        value, digest = _read_catalog_value(root, reader)
        if cas_required or expected is not None:
            _check_cas(digest, expected, "publication")
        built = build(value)
        catalog_value, patterns, details = built[:3]
        extra_files = built[3] if len(built) > 3 else ()
        for pattern in patterns:
            if any(item["id"] == pattern.id and item["version"] == pattern.version for item in catalog_value["entries"]):
                _fail("version_exists", f"{pattern.id}@{pattern.version} is already registered", status="collision")
        _preflight(root, [(relative_file, data) for relative_file, data in extra_files] +
                   [(f"{pattern.id}/{pattern.version}/pattern.json", emit_json(pattern.raw).encode("utf-8"))
                    for pattern in patterns])
        staged = []
        for relative_file, data in extra_files:
            _stage_file(root, relative_file, data)
        for pattern in patterns:
            relative, recovered = _stage_pattern(root, pattern)
            catalog_value["entries"].append(_entry_for(pattern, relative))
            staged.append({"id": pattern.id, "version": pattern.version, "sha256": pattern.digest,
                           "path": relative, "recovered_staging": recovered})
        if len(catalog_value["entries"]) > LIMITS.catalog_entries:
            _fail("resource_limit", f"catalog would exceed {LIMITS.catalog_entries} entries")
        parse_catalog(catalog_value)
        _atomic_write(contained_path(root, "catalog.json"), emit_json(catalog_value).encode("utf-8"), replace=True)
    return {"schema_version": 1, "status": "ok", "written": True, "source_id": catalog_value["source_id"],
            "published": staged, "previous_catalog_sha256": digest, "catalog_sha256": content_digest(catalog_value),
            "diagnostics": details, "metrics": reader.metrics()}


def _source_summary(pattern: Pattern) -> list[dict]:
    notes = []
    kinds = {(item.kind, item.confidence) for item in pattern.sources}
    if pattern.sources and all(kind == "observation" or confidence != "confirmed" for kind, confidence in kinds):
        notes.append(_note("inferred_sources_only",
                           "every source is an observation or unconfirmed; review before treating this as policy",
                           "warning"))
    if any(clause.level == "must" for clause in pattern.requirements) and not pattern.sources:
        notes.append(_note("must_without_source", "must clauses have no source yet; approval will require one",
                           "warning"))
    return notes


def capture(roots: Roots, draft_value: Any, *, scope: str, name: str, source_id: Optional[str] = None,
            expected_catalog_digest: Optional[str] = None, reader: Optional[Reader] = None,
            files_from: Optional[Path] = None) -> dict:
    """Register a new draft in an explicit repo/personal scope (never approves, never overwrites).

    Declared assets and `root: pattern` sources are copied from `files_from` (the CLI uses the
    input file's directory) after verification; a draft that declares files needs that directory.
    """
    reader = reader or Reader()
    pattern = parse_pattern(draft_value, "draft")
    if pattern.status != "draft":
        _fail("capture_not_draft", "capture accepts only status draft; approval is a separate reviewed step")
    if pattern.id != name:
        _fail("capture_name_mismatch", f"--name {name} does not match the draft id {pattern.id}")
    root, _ = _scope_root(roots, scope)

    def build(value):
        if value is None:
            if source_id is None:
                _fail("source_id_required", "the first capture in a scope needs --source-id")
            _matching(source_id, NAMESPACED_ID, "--source-id", "source ID")
            loaded = load_sources(roots)
            if any(item.catalog.source_id == source_id for item in loaded.catalogs):
                _fail("source_id_collision", f"source ID {source_id} is already configured elsewhere")
            value = {"schema_version": 1, "source_id": source_id, "entries": [], "includes": [], "bindings": [],
                     "lifecycle": []}
        elif source_id is not None and source_id != value["source_id"]:
            _fail("source_id_mismatch", f"this scope's source is {value['source_id']}, not {source_id}")
        files = _declared_files(pattern, files_from, reader=reader, what=f"{pattern.id}@{pattern.version}")
        extra = [(f"{pattern.id}/{pattern.version}/{name}", data) for name, data in files]
        return copy_json(value), [pattern], _source_summary(pattern), extra

    report = _publish(root, reader, expected=expected_catalog_digest, build=build)
    report["ref"] = ExactRef(report["source_id"], pattern.id, pattern.version, pattern.digest).to_json()
    report["scope"] = scope
    return report


def index_source(roots: Roots, source_root: Path, *, expected_catalog_digest: Optional[str] = None,
                 reader: Optional[Reader] = None) -> dict:
    """Verify registered entries and regenerate their derived metadata; never discovers content."""
    reader = reader or Reader()
    root = None
    for scope in ("repo", "personal"):
        if scope == "repo" and roots.repository is None:
            continue
        candidate, _ = _scope_root(roots, scope)
        if _same_path(candidate, source_root):
            root = candidate
    if root is None:
        _fail("invalid_source_root", "index accepts only the repository or personal pattern source root")
    with _WriteLock(root / "catalog.json"):
        value, digest = _read_catalog_value(root, reader)
        if value is None:
            _fail("source_missing", "no catalog is registered at this source root", status="unavailable")
        _check_cas(digest, expected_catalog_digest, "index")
        rebuilt, diagnostics, changed = copy_json(value), [], []
        for index, entry in enumerate(value["entries"]):
            path = contained_path(root, entry["path"], f"entry {entry['id']}@{entry['version']}")
            data = reader.read(path, kind="pattern", limit=LIMITS.pattern_bytes, optional=True)
            if data is None:
                _fail("registered_file_missing", f"{entry['id']}@{entry['version']} is registered but its file is "
                      "missing; restore it or remove the entry explicitly", status="unavailable")
            pattern = parse_pattern(parse_json(data, limit=LIMITS.pattern_bytes, what="pattern"), entry["path"])
            if pattern.digest != entry["sha256"]:
                _fail("pattern_digest_mismatch", f"{entry['id']}@{entry['version']} bytes differ from the registered "
                      "digest; index never blesses edited content", status="unavailable")
            if (pattern.id, pattern.version) != (entry["id"], entry["version"]):
                _fail("stale_metadata", f"{entry['path']} declares {pattern.id}@{pattern.version}", status="unavailable")
            fresh = _entry_for(pattern, entry["path"])
            if fresh != entry:
                changed.append({"id": entry["id"], "version": entry["version"],
                                "fields": sorted(key for key in fresh if fresh[key] != entry.get(key))})
                rebuilt["entries"][index] = fresh
        parse_catalog(rebuilt)
        if changed:
            _atomic_write(contained_path(root, "catalog.json"), emit_json(rebuilt).encode("utf-8"), replace=True)
    return {"schema_version": 1, "status": "ok", "written": bool(changed), "rebuilt": changed,
            "previous_catalog_sha256": digest, "catalog_sha256": content_digest(rebuilt),
            "diagnostics": diagnostics, "metrics": reader.metrics()}


def _version_key(version: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in version.split("."))


def approve(roots: Roots, path: Path, *, version: str, approval_value: Any, expected_digest: str,
            expected_catalog_digest: Optional[str] = None, reader: Optional[Reader] = None,
            today: Optional[_dt.date] = None) -> dict:
    """Write a strictly newer approved version of a registered draft; the draft stays unchanged.

    `expected_digest` pins the reviewed draft. Dependency and lifecycle checks run on catalogs read
    inside the owned source-root lock, so a revocation committed by another writer of this root
    before the lock is visible and blocks approval. `expected_catalog_digest` optionally pins the
    whole catalog the caller reviewed (spec 7 CAS).
    """
    reader = reader or Reader()
    root, scope, relative = _root_for_path(roots, path)
    _matching(version, VERSION, "--version", "version", 64)
    approval = _object(approval_value, "approval", ("by", "reference", "at"))
    Approval(_string(approval["by"], "approval.by", limit=_FREE),
             _string(approval["reference"], "approval.reference", limit=_FREE), _timestamp(approval["at"], "approval.at"))
    def build(value):
        if value is None:
            _fail("source_missing", "no catalog at this source root", status="unavailable")
        sources = load_sources(roots, reader)
        own = next((item for item in sources.catalogs if item.catalog.source_id == value["source_id"]), None)
        if own is None or own.catalog.digest != content_digest(value):
            _fail("snapshot_mismatch", "the in-lock catalog and the loaded source differ; retry", status="collision")
        entry = next((item for item in value["entries"] if item["path"] == relative), None)
        if entry is None:
            _fail("not_registered", f"{relative} is not a registered entry; capture it first", status="unavailable")
        loaded = next(item for item in sources.catalogs if item.catalog.source_id == value["source_id"])
        catalog_entry = loaded.catalog.entry(entry["id"], entry["version"])
        draft = _read_pattern(sources, loaded, catalog_entry)
        if draft.digest != expected_digest:
            _fail("stale_pattern_digest", "the draft changed since it was reviewed", status="collision")
        state, _ = effective_status(loaded, catalog_entry)
        if state != "draft":
            _fail("approve_not_draft", f"only drafts are approved; {entry['id']}@{entry['version']} is {state}")
        if _version_key(version) <= _version_key(draft.version):
            _fail("version_not_newer", f"--version {version} must be greater than {draft.version}")
        blockers = []
        for child in draft.includes:
            try:
                child_loaded, child_entry = _lookup(sources, child)
                child_state, _ = effective_status(child_loaded, child_entry)
                if child_state not in ("approved", "deprecated"):
                    _fail("dependency_not_approved", f"include {child.text} is {child_state}", status="unavailable")
            except PatternError as error:
                blockers.append(error.diagnostic())
        if blockers:
            raise PatternError("dependency_not_approved", "; ".join(item["message"] for item in blockers),
                               status="unavailable")
        approved = dict(copy_json(draft.raw), version=version, status="approved", approval=approval)
        pattern = parse_pattern(approved, "approved")
        draft_dir = loaded.directory / PurePosixPath(catalog_entry.path).parent
        files = _declared_files(pattern, draft_dir, reader=reader, what=f"{draft.id}@{draft.version}")
        extra = [(f"{pattern.id}/{pattern.version}/{name}", data) for name, data in files]
        return copy_json(value), [pattern], _source_summary(pattern), extra

    report = _publish(root, reader, expected=expected_catalog_digest, build=build, cas_required=False)
    published = report["published"][0]
    report["ref"] = ExactRef(report["source_id"], published["id"], version, published["sha256"]).to_json()
    report["scope"] = scope
    report["draft_left_unchanged"] = relative
    return report

# ---------------------------------------------------------------- assets (F6: stable refs and verified on-demand reads)

def _asset_applies(asset: Mapping[str, Any], phase: Optional[str], domain: Optional[str]) -> bool:
    """Absent filters apply to any task; a present empty filter matches none (spec 4.1)."""
    for key, wanted in (("phases", phase), ("domains", domain)):
        values = asset.get(key)
        if values is None:
            continue
        if not values or (wanted is not None and wanted not in values):
            return False
    return True


def asset_refs(report: Mapping[str, Any], *, kind: Optional[str] = None, phase: Optional[str] = None,
               domain: Optional[str] = None) -> list[dict]:
    """Metadata-only asset references for selected patterns of a report or lock; reads nothing.

    Shape: `{pattern: <exact ref>, path, kind, sha256[, phases][, domains]}` (the lock's asset_pins).
    """
    if phase is not None and phase not in PHASES:
        _fail("invalid_phase", f"unknown phase {phase}")
    result = []
    for item in report["selected"]:
        for asset in item.get("assets", ()):
            if (kind is None or asset["kind"] == kind) and _asset_applies(asset, phase, domain):
                result.append(dict(copy_json(asset), pattern=copy_json(item["ref"])))
    return sorted(result, key=lambda item: (item["pattern"]["source"], item["pattern"]["id"],
                                            item["pattern"]["version"], item["path"]))


def read_asset(roots: Roots, asset_ref: Mapping[str, Any], *, phase: Optional[str] = None,
               domain: Optional[str] = None, reader: Optional[Reader] = None,
               selection: Optional[Mapping[str, Any]] = None, context: Optional[Context] = None,
               refs: Sequence[InvocationRef] = ()) -> bytes:
    """Read one declared asset: contained, listed by its verified pattern and digest-checked before use.

    Workflow consumers pass `selection` so only assets of selected patterns can be activated:

    - A persisted or cross-process lock MUST first pass `verify_lock` with status `ok`; this function
      only parses it. Parsing proves internal consistency, not that the lock matches the current
      sources and bindings (a resealed lock can parse).
    - A report is accepted only in-process, with the `context` and `refs` it was resolved from.

    Without `selection`, this is standalone inspection of any registered approved or deprecated
    pattern (like `show`); it never implies selection. Digests are unkeyed: none of this
    authenticates who produced a lock or report.
    """
    if not isinstance(asset_ref, Mapping):
        _fail("invalid_asset_ref", "asset reference must be an object")
    _object(dict(asset_ref), "asset_ref", ("pattern", "path", "kind", "sha256"), ("phases", "domains"))
    if selection is not None:
        if "created_at" in selection:
            selection = parse_lock(selection)
        elif selection.get("status") not in ("ready", "empty") or selection.get("selection_digest") is None:
            _fail("selection_not_usable", "asset selection requires a lock or a ready/empty report with a "
                  "selection_digest")
        elif context is None or selection.get("context_digest") != context.digest or \
                selection_digest(_lock_material(selection, context, refs)) != selection["selection_digest"]:
            _fail("selection_not_usable", "a report selection is accepted only in-process with the context and "
                  "refs it was resolved from, and only when its selection_digest still matches its content; "
                  "use a lock for anything persisted or passed between processes")
        if dict(asset_ref) not in asset_refs(selection):
            _fail("asset_not_selected", f"{asset_ref.get('path')} is not an asset of the supplied selection",
                  status="unavailable")
    ref = parse_exact_ref(asset_ref["pattern"], "asset_ref.pattern")
    validate_relative_path(asset_ref["path"], "asset_ref.path")
    if phase is not None and phase not in PHASES:
        _fail("invalid_phase", f"unknown phase {phase}")
    reader = reader or Reader()
    sources = load_sources(roots, reader)
    loaded, entry = _lookup(sources, ref)
    state, _ = effective_status(loaded, entry)
    if state not in ("approved", "deprecated"):
        _fail(f"pattern_{state}", f"assets of a {state} pattern are not used", status="unavailable")
    pattern = _read_pattern(sources, loaded, entry)
    declared = next((asset for asset in pattern.assets if asset.path == asset_ref["path"]), None)
    if declared is None or _asset_json(declared) != {key: asset_ref[key] for key in asset_ref if key != "pattern"}:
        _fail("asset_not_declared", f"{asset_ref['path']} is not declared with this kind/digest by {ref.text}",
              status="unavailable")
    if not _asset_applies(_asset_json(declared), phase, domain):
        _fail("asset_not_applicable", f"{declared.path} does not apply to phase={phase} domain={domain}")
    relative = PurePosixPath(entry.path).parent / declared.path
    data = reader.read(contained_path(loaded.directory, relative.as_posix(), f"asset {declared.path}"),
                       kind="asset", limit=LIMITS.asset_bytes)
    if hashlib.sha256(data).hexdigest() != declared.sha256:
        _fail("asset_digest_mismatch", f"{declared.path} bytes differ from the declared digest", status="unavailable")
    return data


# ---------------------------------------------------------------- maintenance (cards 3.2.a-3.2.c)

LOCK_SCAN_LIMIT = 256
INVENTORY_SCOPE = ("configured catalogs (active and personal) and *.lock.json files under the explicit repository "
                   "plan root .claude/plans; it cannot prove that no external consumer exists")


def _key(ref: ExactRef) -> tuple[str, str, str]:
    return (ref.id, ref.version, ref.sha256)


def _scan_locks(roots: Roots, reader: Reader) -> tuple[list[tuple[str, dict]], list[dict]]:
    """Locks under <repository>/.claude/plans only: never other repositories, homes or sessions."""
    if roots.repository is None:
        return [], []
    base = contained_path(roots.repository, ".claude/plans", "plan root")
    if not base.is_dir():
        return [], []
    found, problems = [], []
    for directory, subdirectories, files in os.walk(base, followlinks=False):
        subdirectories[:] = sorted(name for name in subdirectories if not _is_link(Path(directory) / name))
        for name in sorted(files):
            if not name.endswith(".lock.json"):
                continue
            path = Path(directory) / name
            relative = path.relative_to(roots.repository).as_posix()
            if len(found) + len(problems) >= LOCK_SCAN_LIMIT:
                problems.append({"path": relative, "reason": f"scan limit {LOCK_SCAN_LIMIT} reached"})
                continue
            try:
                value = parse_json(reader.read(path, kind="input", limit=LIMITS.catalog_bytes),
                                   limit=LIMITS.catalog_bytes, what="lock")
                found.append((relative, parse_lock(value)))
            except PatternError as error:
                problems.append({"path": relative, "reason": f"{error.code}: {error.message}"})
    return found, problems


def dependents(roots: Roots, targets: Iterable[ExactRef], *, reader: Optional[Reader] = None,
               sources: Optional[SourceSet] = None) -> dict:
    """Bounded impact inventory: includes, bindings and locks that reference any target identity."""
    reader = reader or Reader()
    sources = sources or load_sources(roots, reader)
    wanted = {_key(ref) for ref in targets}
    includes, bindings, unreadable = [], [], []
    for loaded in sources.catalogs:
        for entry in loaded.catalog.entries:
            try:
                pattern = _read_pattern(sources, loaded, entry)
            except PatternError as error:
                unreadable.append({"source": loaded.catalog.source_id, "id": entry.id, "version": entry.version,
                                   "reason": error.code})
                continue
            for child in pattern.includes:
                if _key(child) in wanted:
                    includes.append({"pattern": ExactRef(loaded.catalog.source_id, entry.id, entry.version,
                                                         entry.sha256).to_json(), "include": child.to_json()})
        for binding in loaded.catalog.bindings:
            if any(_key(ref) in wanted for ref in binding.use):
                bindings.append({"origin": loaded.catalog.source_id, "scope": loaded.scope, "active": loaded.active,
                                 "binding": binding.id, "role": binding.role})
    for scope, binding, origin in sources.bindings:
        if origin == "repo:bindings.json" and any(_key(ref) in wanted for ref in binding.use):
            bindings.append({"origin": origin, "scope": scope, "active": True, "binding": binding.id,
                             "role": binding.role})
    locks, lock_problems = _scan_locks(roots, reader)
    pinned = []
    for relative, lock in locks:
        hits = sorted({equivalent["id"] + "@" + equivalent["version"] for item in lock["selected"]
                       for equivalent in item["equivalent_refs"]
                       if (equivalent["id"], equivalent["version"], equivalent["sha256"]) in wanted})
        if hits:
            pinned.append({"lock": relative, "selection_digest": lock["selection_digest"], "pins": hits})
    return {"includes": includes, "bindings": sorted(bindings, key=lambda item: (item["origin"], item["binding"])),
            "locks": pinned, "unreadable_patterns": unreadable, "unreadable_locks": lock_problems,
            "locks_scanned": len(locks), "inventory_scope": INVENTORY_SCOPE}


def _writable(sources: SourceSet, source_id: str) -> "LoadedCatalog":
    loaded = sources.by_source(source_id)
    if loaded is None:
        _fail("source_unavailable", f"source {source_id} is not configured here", status="unavailable")
    if loaded.locator not in ("repo", "personal"):
        _fail("read_only_source", f"{source_id} is a {loaded.scope} source; packs publish through their own review")
    return loaded


def _scope_of_loaded(roots: Roots, loaded: "LoadedCatalog") -> Path:
    root, _ = _scope_root(roots, loaded.locator)
    if not _same_path(root, loaded.directory):
        _fail("read_only_source", f"{loaded.catalog.source_id} is an included catalog, not the scope's root catalog")
    return root


LIFECYCLE_ACTIONS = ("deprecate", "retire", "revoke")


def record_lifecycle(roots: Roots, ref_text: str, *, action: str, record_value: Any,
                     expected_catalog_digest: Optional[str], write: bool = False,
                     reader: Optional[Reader] = None) -> dict:
    """Preview (default) or record a deprecation, retirement or revocation event with its impact."""
    if action not in LIFECYCLE_ACTIONS:
        _fail("invalid_action", f"action must be one of {', '.join(LIFECYCLE_ACTIONS)}")
    reader = reader or Reader()
    source_id, pattern_id, version = parse_ref_text(ref_text)
    allowed = ("reason", "reference", "at") + (("replaced_by",) if action != "revoke" else ())
    record = _object(record_value, "record", ("reason", "reference", "at"), allowed[3:])
    _string(record["reason"], "record.reason", limit=_FREE)
    _string(record["reference"], "record.reference", limit=_FREE)
    _timestamp(record["at"], "record.at")
    replaced = parse_exact_ref(record["replaced_by"], "record.replaced_by") if "replaced_by" in record else None
    sources = load_sources(roots, reader)
    loaded = _writable(sources, source_id)
    root = _scope_of_loaded(roots, loaded)
    entry = loaded.catalog.entry(pattern_id, version)
    if entry is None:
        _fail("reference_missing", f"{ref_text} is not registered", status="unavailable")
    target = ExactRef(source_id, pattern_id, version, entry.sha256)
    before, _ = effective_status(loaded, entry)
    if replaced is not None:
        replacement_loaded, replacement_entry = _lookup(sources, replaced)
        state, _ = effective_status(replacement_loaded, replacement_entry)
        if state not in ("approved", "deprecated") or _key(replaced) == _key(target):
            _fail("invalid_replacement", "replaced_by must be a different approved or deprecated pattern")
    after = "revoked" if action == "revoke" else {"deprecate": "deprecated", "retire": "retired"}[action]

    def apply_event(value):
        """One definition of the event and its rules, used by the preview and the write alike."""
        current = next((item for item in value["entries"] if (item["id"], item["version"]) == (pattern_id, version)), None)
        if current is None or current["sha256"] != entry.sha256:
            _fail("snapshot_mismatch", "the entry changed since the preview; re-read and retry", status="collision")
        events = [item for item in value["lifecycle"] + value.get("revocations", [])
                  if (item["id"], item["version"]) == (pattern_id, version)]
        if any(_instant(item["at"]) >= _instant(record["at"]) for item in events):
            _fail("event_not_monotonic", "a lifecycle event must be later than every earlier event for this entry")
        event = {"id": pattern_id, "version": version, "sha256": entry.sha256, "reason": record["reason"],
                 "reference": record["reference"], "at": record["at"]}
        updated = copy_json(value)
        if action == "revoke":
            if any((item["id"], item["version"]) == (pattern_id, version) for item in value.get("revocations", [])):
                _fail("already_revoked", f"{ref_text} is already revoked; there is no un-revoke in v1")
            updated.setdefault("revocations", []).append(event)
        else:
            event["status"] = after
            if replaced is not None:
                event["replaced_by"] = replaced.to_json()
            updated["lifecycle"].append(event)
        parse_catalog(updated, "catalog after the event")
        return updated

    apply_event(dict(loaded.catalog.raw))
    impact = dependents(roots, [target], reader=reader, sources=sources)
    report = {"schema_version": 1, "status": "ok", "written": False, "action": action, "ref": target.to_json(),
              "effective_status": {"before": before, "after": after}, "impact": impact,
              "catalog_sha256": loaded.catalog.digest, "diagnostics": [], "metrics": reader.metrics()}
    if not write:
        return report

    def build(value):
        return apply_event(value), [], []

    written = _publish(root, reader, expected=expected_catalog_digest, build=build)
    report.update(written=True, catalog_sha256=written["catalog_sha256"],
                  previous_catalog_sha256=written["previous_catalog_sha256"], metrics=reader.metrics())
    return report


def _clause_diff(old: Pattern, new: Pattern) -> dict:
    before = {item.id: item.to_json() for item in old.requirements}
    after = {item.id: item.to_json() for item in new.requirements}
    return {"added": sorted(after.keys() - before.keys()), "removed": sorted(before.keys() - after.keys()),
            "changed": sorted(key for key in before.keys() & after.keys() if before[key] != after[key]),
            "includes_changed": [ref.to_json() for ref in old.includes] != [ref.to_json() for ref in new.includes],
            "applies_to_changed": old.applies_to != new.applies_to}


def update(roots: Roots, path: Path, input_value: Any, *, expected_digest: str, write: bool = False,
           expected_catalog_digest: Optional[str] = None, reader: Optional[Reader] = None,
           files_from: Optional[Path] = None) -> dict:
    """Preview (default) or publish a strictly newer draft version; the existing version stays intact."""
    reader = reader or Reader()
    root, scope, relative = _root_for_path(roots, path)
    new = parse_pattern(input_value, "update")
    if new.status != "draft":
        _fail("update_not_draft", "an update creates a draft; approve it separately after review")
    sources = load_sources(roots, reader)
    value, _ = _read_catalog_value(root, Reader())
    if value is None:
        _fail("source_missing", "no catalog at this source root", status="unavailable")
    loaded = _writable(sources, value["source_id"])
    entry = next((item for item in loaded.catalog.entries if item.path == relative), None)
    if entry is None:
        _fail("not_registered", f"{relative} is not a registered entry", status="unavailable")
    old = _read_pattern(sources, loaded, entry)
    if old.digest != expected_digest:
        _fail("stale_pattern_digest", "the pattern changed since it was reviewed", status="collision")
    if new.id != old.id:
        _fail("update_id_mismatch", f"an update keeps the pattern id {old.id}")
    if _version_key(new.version) <= _version_key(old.version):
        _fail("version_not_newer", f"version {new.version} must be greater than {old.version}")
    old_ref = ExactRef(loaded.catalog.source_id, old.id, old.version, old.digest)
    files = _declared_files(new, files_from, fallback_dir=loaded.directory / PurePosixPath(entry.path).parent,
                            reader=reader, what=f"{new.id}@{new.version}")
    extra = [(f"{new.id}/{new.version}/{name}", data) for name, data in files]
    report = {"schema_version": 1, "status": "ok", "written": False, "scope": scope, "from": old_ref.to_json(),
              "to": ExactRef(loaded.catalog.source_id, new.id, new.version, new.digest).to_json(),
              "clause_diff": _clause_diff(old, new), "impact": dependents(roots, [old_ref], reader=reader, sources=sources),
              "old_version_unchanged": True, "diagnostics": _source_summary(new), "metrics": reader.metrics()}
    if not write:
        return report

    def build(current):
        own = next((item for item in current["entries"] if item["path"] == relative), None)
        if own is None or own["sha256"] != old.digest:
            _fail("snapshot_mismatch", "the pattern changed since the preview; re-read and retry", status="collision")
        return copy_json(current), [new], _source_summary(new), extra

    written = _publish(root, reader, expected=expected_catalog_digest, build=build, cas_required=False)
    report.update(written=True, published=written["published"], catalog_sha256=written["catalog_sha256"],
                  metrics=reader.metrics())
    return report

# ---------------------------------------------------------------- attestations (spec 4.5, card 3.2.b)

ATTESTATION_PURPOSES = ("source-verification", "freshness", "both")


def parse_attestations(value: Any, where: str = "attestations") -> tuple[dict, ...]:
    _object(value, where, ("schema_version", "items"))
    _schema_version(value, where)
    items, seen = [], set()
    for index, item in enumerate(_array(value["items"], f"{where}.items")):
        at = f"{where}.items[{index}]"
        _object(item, at, ("ref", "source_index", "source_ref", "source_digest", "reviewed_by", "review_ref",
                           "reviewed_at", "valid_until", "purpose"))
        ref = parse_exact_ref(item["ref"], f"{at}.ref")
        if type(item["source_index"]) is not int or item["source_index"] < 0:
            _fail("invalid_schema", "source_index must be a nonnegative integer", at)
        _string(item["source_ref"], f"{at}.source_ref", limit=_FREE)
        _matching(item["source_digest"], HEX64, f"{at}.source_digest", "source digest", 64)
        _string(item["reviewed_by"], f"{at}.reviewed_by", limit=_FREE)
        _string(item["review_ref"], f"{at}.review_ref", limit=_FREE)
        _timestamp(item["reviewed_at"], f"{at}.reviewed_at")
        _date(item["valid_until"], f"{at}.valid_until")
        if item["purpose"] not in ATTESTATION_PURPOSES:
            _fail("invalid_schema", f"purpose must be one of {', '.join(ATTESTATION_PURPOSES)}", at)
        identity = (_key(ref), item["source_index"])
        if identity in seen:
            _fail("invalid_schema", "one attestation per pattern source; renewal replaces the earlier record", at)
        seen.add(identity)
        items.append(copy_json(item))
    return tuple(items)


def _as_attestations(items: Any, where: str) -> tuple[dict, ...]:
    """Validate raw or already parsed attestation items with the same parser (PatternError, never KeyError)."""
    if isinstance(items, (str, bytes)) or not isinstance(items, (list, tuple)):
        _fail("invalid_schema", "attestations must be a list of attestation records", where)
    return parse_attestations({"schema_version": 1, "items": list(items)}, where)


def merge_attestations(saved: Sequence[Mapping[str, Any]], supplied: Sequence[Mapping[str, Any]]) -> list[dict]:
    """Renewal replaces evidence for the same pattern/source; it never changes the selection."""
    saved, supplied = _as_attestations(saved, "saved attestations"), _as_attestations(supplied, "attestations")
    def identity(item):
        return ((item["ref"]["id"], item["ref"]["version"], item["ref"]["sha256"]), item["source_index"])
    merged = {identity(item): copy_json(item) for item in saved}
    merged.update({identity(item): copy_json(item) for item in supplied})
    return [merged[key] for key in sorted(merged)]


def _local_source_bytes(roots: Roots, loaded: "LoadedCatalog", entry: CatalogEntry, source: SourceRecord,
                        reader: Reader) -> Optional[bytes]:
    if source.root == "pattern":
        base = loaded.directory / PurePosixPath(entry.path).parent
        return reader.read(contained_path(base, source.ref, "source"), kind="asset", limit=LIMITS.asset_bytes,
                           optional=True)
    if source.root == "repository":
        if roots.repository is None:
            return None
        return reader.read(contained_path(roots.repository, source.ref, "source"), kind="asset",
                           limit=LIMITS.asset_bytes, optional=True)
    return None


def _attestation_problem(item: Mapping[str, Any], pattern: Pattern, roots: Roots, loaded: "LoadedCatalog",
                         entry: CatalogEntry, today: _dt.date, reader: Reader) -> Optional[str]:
    index = item["source_index"]
    if index >= len(pattern.sources):
        return "source_index is outside the pattern's sources"
    source = pattern.sources[index]
    if item["source_ref"] != source.ref:
        return "source_ref does not equal the pattern source at source_index"
    if _instant(item["reviewed_at"]).date() > today:
        return "reviewed_at is in the future"
    if _dt.date.fromisoformat(item["valid_until"]) < today:
        return "the attestation has expired"
    if source.root == "statement":
        if item["source_digest"] != hashlib.sha256(source.ref.encode("utf-8")).hexdigest():
            return "source_digest does not hash the statement text"
    elif source.root in ("pattern", "repository"):
        data = _local_source_bytes(roots, loaded, entry, source, reader)
        if data is None:
            return "the local source file is missing"
        actual = hashlib.sha256(data).hexdigest()
        if item["source_digest"] != actual or (source.sha256 is not None and source.sha256 != actual):
            return "the local source bytes changed since the review (recapture, do not re-attest)"
    return None


def _attestation_checks(resolution: "_Resolution", node: "_Node", attestations: Sequence[Mapping[str, Any]],
                        roots: Roots) -> None:
    """Required patterns: URL sources need source verification; overdue patterns need fresh review."""
    loaded, entry, _, _, pattern = resolution.loaded[node.ref.key]
    mine = {item["source_index"]: item for item in attestations
            if (item["ref"]["id"], item["ref"]["version"], item["ref"]["sha256"]) == node.identity}
    valid = {}
    for index, item in mine.items():
        problem = _attestation_problem(item, pattern, roots, loaded, entry, resolution.today, resolution.sources.reader)
        if problem:
            resolution.diagnostics.append(_note("attestation_rejected", f"{node.ref.text} source {index}: {problem}",
                                                "warning", ref=node.ref.to_json(), source_index=index))
        else:
            valid[index] = item
            resolution.applied_attestations.append(item)
    for index, source in enumerate(pattern.sources):
        if source.is_url and valid.get(index, {}).get("purpose") not in ("source-verification", "both"):
            resolution.problem("unavailable", "source_attestation_required",
                               f"{node.ref.text} source {index} is a URL and needs a current reviewed source attestation",
                               ref=node.ref.to_json(), source_index=index)
    if pattern.review_after and _dt.date.fromisoformat(pattern.review_after) < resolution.today:
        missing = [index for index in range(len(pattern.sources))
                   if valid.get(index, {}).get("purpose") not in ("freshness", "both")
                   or _instant(valid[index]["reviewed_at"]).date() < _dt.date.fromisoformat(pattern.review_after)]
        if missing or not pattern.sources:
            resolution.problem("unavailable", "review_overdue",
                               f"{node.ref.text} is past review_after and needs freshness attestations for "
                               f"every source reviewed on or after {pattern.review_after}",
                               ref=node.ref.to_json(), missing_sources=missing)


# ---------------------------------------------------------------- binding changes (spec 7 apply, card 3.2.b)

def _required_clauses(sources: SourceSet, binding: Optional[Binding]) -> tuple[set, list]:
    """Must clauses a required binding reaches, plus references it cannot reach (reported, never hidden)."""
    if binding is None or binding.role != "required":
        return set(), []
    result, missing, stack, seen = set(), [], list(binding.use), set()
    while stack:
        ref = stack.pop()
        if _key(ref) in seen:
            continue
        seen.add(_key(ref))
        try:
            loaded, entry = _lookup(sources, ref)
            pattern = _read_pattern(sources, loaded, entry)
        except PatternError as error:
            missing.append({"ref": ref.to_json(), "code": error.code})
            continue
        result.update(pattern.clause_ref(item.id) for item in pattern.requirements if item.level == "must")
        stack.extend(pattern.includes)
    return result, sorted(missing, key=lambda item: canonical_json(item["ref"]))


def apply_change(roots: Roots, change_value: Any, *, expected_digest: Optional[str] = None, write: bool = False,
                 reader: Optional[Reader] = None) -> dict:
    """Preview (default) or write one add/replace/remove of a repository binding under CAS."""
    reader = reader or Reader()
    if roots.repository is None:
        _fail("repository_required", "binding changes need an explicit repository root")
    change = _object(change_value, "change", ("schema_version", "operation", "id", "binding", "reason",
                                              "approved_by", "approval_ref"))
    _schema_version(change, "change")
    operation = change["operation"]
    if operation not in ("add", "replace", "remove"):
        _fail("invalid_schema", "operation must be add, replace or remove", "change.operation")
    binding_id = _string(change["id"], "change.id", limit=_FREE)
    for field in ("reason", "approved_by", "approval_ref"):
        _string(change[field], f"change.{field}", limit=_FREE)
    if operation == "remove":
        if change["binding"] is not None:
            _fail("invalid_schema", "remove requires binding: null", "change.binding")
        replacement = None
    else:
        replacement = _binding(change["binding"], "change.binding")
        if replacement.id != binding_id:
            _fail("invalid_schema", "the binding id must equal change.id", "change.binding.id")
    root = contained_path(roots.repository, ".claude/patterns", "repository pattern root")
    path = contained_path(roots.repository, ".claude/patterns/bindings.json", "repository bindings")

    def plan(value):
        current = parse_bindings(value) if value is not None else ()
        existing = next((item for item in current if item.id == binding_id), None)
        if operation == "add" and existing is not None:
            _fail("binding_exists", f"binding {binding_id} already exists; use replace", status="collision")
        if operation != "add" and existing is None:
            _fail("binding_missing", f"binding {binding_id} does not exist")
        items = [copy_json(item) for item in (value or {"bindings": []})["bindings"] if item["id"] != binding_id]
        if replacement is not None:
            items.append(copy_json(change["binding"]))
        new_value = {"schema_version": 1, "bindings": sorted(items, key=lambda item: item["id"])}
        parse_bindings(new_value)
        sources = load_sources(roots, reader)
        if replacement is not None:
            for ref in replacement.use:
                try:
                    loaded, entry = _lookup(sources, ref)
                    state, _ = effective_status(loaded, entry)
                    if state not in ("approved", "deprecated"):
                        _fail(f"pattern_{state}", f"{ref.text} is {state}", status="unavailable")
                    _read_pattern(sources, loaded, entry)
                except PatternError as error:
                    _fail("binding_ref_unavailable", f"binding {binding_id} uses {ref.text}, which cannot be selected "
                          f"({error.code}); a binding may only use registered approved or deprecated patterns",
                          status="unavailable")
        (before, before_missing), (after, _) = _required_clauses(sources, existing), _required_clauses(sources, replacement)
        return new_value, existing, {"before": sorted(before), "after": sorted(after),
                                     "reduced": sorted(before - after), "added": sorted(after - before),
                                     "unreachable_before": before_missing}

    def read():
        data = reader.read(path, kind="bindings", limit=LIMITS.input_bytes, optional=True)
        return None if data is None else parse_json(data, limit=LIMITS.input_bytes, what="repository bindings")

    value = read()
    new_value, existing, required = plan(value)
    report = {"schema_version": 1, "status": "ok", "written": False, "operation": operation, "id": binding_id,
              "before": None if existing is None else copy_json(next(item for item in value["bindings"]
                                                                     if item["id"] == binding_id)),
              "after": copy_json(change["binding"]), "required_clauses": required,
              "provenance": {key: change[key] for key in ("reason", "approved_by", "approval_ref")},
              "bindings_sha256": None if value is None else content_digest(value),
              "limits": "Records an authorized change; it does not validate the approver's authority.",
              "diagnostics": [], "metrics": reader.metrics()}
    if required["unreachable_before"]:
        report["diagnostics"].append(_note("binding_had_unavailable_refs", "the current binding already uses "
                                           "patterns that cannot be selected; its baseline is incomplete", "warning",
                                           refs=required["unreachable_before"]))
    if required["reduced"]:
        report["diagnostics"].append(_note("mandatory_baseline_reduced", "this change removes mandatory clauses "
                                           "from the repository baseline", "warning", clauses=required["reduced"]))
    if not write:
        return report
    base = roots.repository
    for part in (".claude", "patterns"):
        base = base / part
        if _is_link(base):
            _fail("unsafe_path", "linked repository pattern root refused", str(base))
        base.mkdir(exist_ok=True)
    with _WriteLock(path):
        value = read()
        current = None if value is None else content_digest(value)
        _check_cas(current, expected_digest, "apply", obj="bindings", flag="--expected-digest")
        new_value, _, required = plan(value)
        _atomic_write(path, emit_json(new_value).encode("utf-8"), replace=True)
    report.update(written=True, required_clauses=required, bindings_sha256=content_digest(new_value),
                  previous_bindings_sha256=current, metrics=reader.metrics())
    return report


def record_attestations(roots: Roots, lock_path: Path, attestations: Sequence[Mapping[str, Any]], context: Context, *,
                        expected_lock_digest: str, today: Optional[_dt.date] = None,
                        reader: Optional[Reader] = None) -> dict:
    """Install validated attestations in a lock under CAS; the selection digest never changes."""
    reader = reader or Reader()
    target = _repository_file(roots, lock_path, "lock")
    with _WriteLock(target):
        lock = parse_lock(parse_json(reader.read(target, kind="input", limit=LIMITS.catalog_bytes),
                                     limit=LIMITS.catalog_bytes, what="lock"))
        if content_digest(lock) != expected_lock_digest:
            _fail("stale_lock_digest", "the lock changed since it was read; re-read and retry", status="collision")
        report = verify_lock(roots, lock, context, today=today, reader=reader, attestations=attestations)
        if report["status"] != "ok":
            return dict(report, written=False)
        updated = dict(copy_json(lock), source_attestations=report["source_attestations"])
        if selection_digest(updated) != lock["selection_digest"]:
            _fail("invalid_lock", "attestations must not change the selection digest")
        _assert_portable(updated, roots)
        _atomic_write(target, emit_json(updated).encode("utf-8"), replace=True)
    return dict(report, written=True, lock_sha256=content_digest(updated))


def remove(roots: Roots, ref_text: str, *, expected_catalog_digest: Optional[str], write: bool = False,
           reader: Optional[Reader] = None) -> dict:
    """Preview (default) or unregister one unreferenced catalog entry without deleting any file or history."""
    reader = reader or Reader()
    source_id, pattern_id, version = parse_ref_text(ref_text)
    sources = load_sources(roots, reader)
    loaded = _writable(sources, source_id)
    root = _scope_of_loaded(roots, loaded)
    entry = loaded.catalog.entry(pattern_id, version)
    if entry is None:
        _fail("reference_missing", f"{ref_text} is not registered", status="unavailable")
    target = ExactRef(source_id, pattern_id, version, entry.sha256)
    impact = dependents(roots, [target], reader=reader, sources=sources)
    state, _ = effective_status(loaded, entry)
    history = [item for item in loaded.catalog.lifecycle + loaded.catalog.revocations
               if (item.id, item.version) == (pattern_id, version)]
    blockers = []
    if impact["includes"] or impact["bindings"] or impact["locks"]:
        blockers.append("referenced by the inventory (includes, bindings or locks)")
    if history:
        blockers.append("has lifecycle or revocation history, which v1 never deletes")
    if impact["unreadable_patterns"] or impact["unreadable_locks"]:
        blockers.append("the inventory is incomplete (unreadable patterns or locks)")
    report = {"schema_version": 1, "status": "ok", "written": False, "ref": target.to_json(),
              "effective_status": state, "impact": impact, "removable": not blockers, "blockers": blockers,
              "catalog_sha256": loaded.catalog.digest,
              "files_kept": [entry.path],
              "diagnostics": [] if state == "draft" else [_note(
                  "external_consumers_unknown", "removing a published entry cannot prove that no external consumer "
                  "pins it; the file stays on disk", "warning")],
              "metrics": reader.metrics()}
    if not write:
        return report
    if blockers:
        _fail("remove_refused", f"{ref_text} cannot be removed: {'; '.join(blockers)}", status="conflict")

    def build(value):
        current = next((item for item in value["entries"] if (item["id"], item["version"]) == (pattern_id, version)), None)
        if current is None or current["sha256"] != entry.sha256:
            _fail("snapshot_mismatch", "the entry changed since the preview; re-read and retry", status="collision")
        updated = copy_json(value)
        updated["entries"] = [item for item in updated["entries"]
                              if (item["id"], item["version"]) != (pattern_id, version)]
        return updated, [], []

    written = _publish(root, reader, expected=expected_catalog_digest, build=build)
    report.update(written=True, catalog_sha256=written["catalog_sha256"], metrics=reader.metrics())
    return report


# ---------------------------------------------------------------- review coverage (spec 8, card 4.2.b.core)

REVIEW_STATUSES = ("passed", "failed", "waived", "not-applicable", "unverified")


def parse_review_evidence(value: Any, lock: Mapping[str, Any], where: str = "evidence") -> dict:
    _object(value, where, ("schema_version", "selection_digest", "mapping_digest", "items"))
    _schema_version(value, where)
    mapping = lock["requirement_tasks"]
    if mapping is None:
        _fail("mapping_required", "map the lock's clauses to tasks before review (li-pattern map --write)")
    if value["selection_digest"] != lock["selection_digest"]:
        _fail("evidence_selection_mismatch", "the evidence was produced for a different selection", where)
    known = {item["clause"]: item for item in lock["requirements"]}
    tasks_for = {item["clause"]: set(item["tasks"]) for item in mapping["clauses"]}
    items, seen = [], set()
    for index, item in enumerate(_array(value["items"], f"{where}.items")):
        at = f"{where}.items[{index}]"
        _object(item, at, ("clause", "task_ids", "status", "evidence_refs", "explanation"))
        clause = _fq_clause(item["clause"], f"{at}.clause")
        if clause not in known:
            _fail("invalid_evidence", f"unknown clause {clause}", at)
        if clause in seen:
            _fail("invalid_evidence", f"duplicate evidence for {clause}", at)
        seen.add(clause)
        task_ids = [_task_id(task, f"{at}.task_ids") for task in _array(item["task_ids"], f"{at}.task_ids", nonempty=True)]
        if not set(task_ids) <= tasks_for.get(clause, set()):
            _fail("invalid_evidence", f"task_ids for {clause} are not mapped to that clause", at)
        if item["status"] not in REVIEW_STATUSES:
            _fail("invalid_evidence", f"status must be one of {', '.join(REVIEW_STATUSES)}", at)
        refs = [_string(ref, f"{at}.evidence_refs", limit=_FREE) for ref in _array(item["evidence_refs"], at)]
        _string(item["explanation"], f"{at}.explanation", limit=_FREE, empty=True)
        items.append(dict(copy_json(item), evidence_refs=refs))
    return {"mapping_current": value["mapping_digest"] == mapping["mapping_digest"], "items": items}


def review_coverage(roots: Roots, lock: Mapping[str, Any], context: Context, evidence_value: Any, *,
                    attestations: Sequence[Mapping[str, Any]] = (), today: Optional[_dt.date] = None,
                    reader: Optional[Reader] = None) -> dict:
    """Verify the lock and sources first, then per-clause coverage. Supplemental evidence only (RN-02)."""
    lock = parse_lock(lock)
    verified = verify_lock(roots, lock, context, today=today, reader=reader, attestations=attestations)
    base = {"schema_version": 1, "selection_digest": lock["selection_digest"],
            "mapping_digest": (lock["requirement_tasks"] or {}).get("mapping_digest"), "verification": verified,
            "release_clearance": False,
            "limits": "Checks coverage and evidence structure only, not whether cited evidence is true. It is "
                      "supplemental content evidence for the ADR-0028 review contract and never a PASS."}
    if verified["status"] != "ok":
        return dict(base, status=verified["status"], clauses=[], diagnostics=verified["diagnostics"])
    evidence = parse_review_evidence(evidence_value, lock)
    by_clause = {item["clause"]: item for item in evidence["items"]}
    diagnostics, clauses = [], []
    if not evidence["mapping_current"]:
        diagnostics.append(_note("mapping_changed", "the evidence was produced for an earlier task mapping; its "
                                 "task coverage no longer counts", "error", status="review-unmet"))
    for requirement in sorted(lock["requirements"], key=lambda item: item["clause"]):
        clause, state = requirement["clause"], requirement["state"]
        mandatory = requirement["level"] == "must" and state in _EFFECTIVE_MANDATORY
        item = by_clause.get(clause)
        status = item["status"] if item else "missing"
        verdict, reason = "unmet", ""
        if not evidence["mapping_current"]:
            reason = "stale mapping"
        elif status == "missing":
            reason = "no evidence item"
        elif state == "waived":
            verdict = "waived" if status in ("waived", "passed") else "unmet"
            reason = "" if verdict == "waived" else f"a waived clause reported {status}"
        elif status == "passed":
            if item["evidence_refs"] and item["explanation"].strip():
                verdict = "passed"
            else:
                reason = "passed needs evidence references and a review explanation"
        elif status == "waived":
            reason = "no matching valid exception is recorded in the lock"
        elif status == "not-applicable":
            reason = "a mandatory not-applicable needs an applicability correction and a newly resolved lock" \
                if mandatory else ""
            verdict = "unmet" if mandatory else "not-applicable"
        else:
            reason = status
        record = {"clause": clause, "level": requirement["level"], "state": state, "evidence_status": status,
                  "verdict": verdict, "task_ids": item["task_ids"] if item else []}
        if reason:
            record["reason"] = reason
        clauses.append(record)
        if mandatory and verdict == "unmet":
            diagnostics.append(_note("mandatory_unmet", f"{clause}: {reason}", "error", status="review-unmet",
                                     clause=clause))
        elif not mandatory and requirement["state"] == "default" and verdict == "unmet":
            diagnostics.append(_note("default_unverified", f"{clause}: {reason}", "warning", clause=clause))
    status = "review-unmet" if any(item.get("status") == "review-unmet" for item in diagnostics) else "ok"
    counts = {}
    for record in clauses:
        counts[record["verdict"]] = counts.get(record["verdict"], 0) + 1
    return dict(base, status=status, clauses=clauses, counts=counts,
                diagnostics=list(verified["diagnostics"]) + diagnostics)


# ---------------------------------------------------------------- sharing (spec 7, cards 3.3.a-3.3.b)

def _bundle_prefix(ref: ExactRef) -> str:
    return f"patterns/{ref.source}/{ref.id}/{ref.version}"


def _events_json(loaded: "LoadedCatalog", entry: CatalogEntry) -> list[dict]:
    events = []
    for item in loaded.catalog.lifecycle:
        if (item.id, item.version, item.sha256) == (entry.id, entry.version, entry.sha256):
            record = {"kind": "lifecycle", "status": item.status, "reason": item.reason, "reference": item.reference,
                      "at": item.at}
            if item.replaced_by is not None:
                record["replaced_by"] = item.replaced_by.to_json()
            events.append(record)
    for item in loaded.catalog.revocations:
        if (item.id, item.version, item.sha256) == (entry.id, entry.version, entry.sha256):
            events.append({"kind": "revocation", "reason": item.reason, "reference": item.reference, "at": item.at})
    return sorted(events, key=lambda item: _instant(item["at"]))


def export_bundle(roots: Roots, refs: Sequence[ExactRef], out: Path, *, reader: Optional[Reader] = None) -> dict:
    """Write the exact dependency closure and its declared assets to a new directory; nothing is uploaded."""
    reader = reader or Reader()
    if not refs:
        _fail("invalid_arguments", "export needs at least one exact reference")
    out = Path(out)
    out = out if out.is_absolute() else Path.cwd() / out
    if out.exists() or _is_link(out):
        _fail("destination_exists", "export writes a new directory; the destination already exists", str(out),
              status="collision")
    if not out.parent.is_dir() or _is_link(out.parent):
        _fail("unsafe_path", "the export parent must be an existing, unlinked directory", str(out.parent))
    validate_relative_path(out.name, "--out")
    sources = load_sources(roots, reader)
    closure, order, queue = {}, [], list(refs)
    while queue:
        ref = queue.pop(0)
        if _key(ref) in closure:
            continue
        loaded, entry = _lookup(sources, ref)
        state, _ = effective_status(loaded, entry)
        if state in ("retired", "revoked"):
            _fail(f"pattern_{state}", f"{ref.text} is {state}; retired and revoked patterns are not shared",
                  status="unavailable")
        data, pattern = _read_pattern_bytes(sources, loaded, entry)
        assets = []
        for asset in pattern.assets:
            relative = PurePosixPath(entry.path).parent / asset.path
            asset_data = reader.read(contained_path(loaded.directory, relative.as_posix(), f"asset {asset.path}"),
                                     kind="asset", limit=LIMITS.asset_bytes)
            if hashlib.sha256(asset_data).hexdigest() != asset.sha256:
                _fail("asset_digest_mismatch", f"{ref.text} asset {asset.path} changed", status="unavailable")
            assets.append((asset.path, asset_data))
        closure[_key(ref)] = (ref, data, pattern, assets, state, _events_json(loaded, entry))
        order.append(_key(ref))
        queue.extend(pattern.includes)
    files, patterns, lifecycle, total = [], [], [], 0
    payload = []
    for key in order:
        ref, data, pattern, assets, state, events = closure[key]
        prefix = _bundle_prefix(ref)
        payload.append((f"{prefix}/pattern.json", data))
        payload.extend((f"{prefix}/{path}", asset_data) for path, asset_data in assets)
        patterns.append({"ref": ref.to_json(), "path": f"{prefix}/pattern.json"})
        lifecycle.append({"ref": ref.to_json(), "effective_status": state, "events": events})
    seen_paths = set()
    for relative, data in payload:
        validate_relative_path(relative, "bundle path")
        if relative in seen_paths:
            _fail("invalid_bundle", f"two bundle members would share {relative}")
        seen_paths.add(relative)
        total += len(data)
        files.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest()})
    if total > LIMITS.bundle_bytes:
        _fail("resource_limit", f"the bundle would exceed {LIMITS.bundle_bytes} bytes")
    manifest = {"schema_version": 1, "patterns": patterns, "files": sorted(files, key=lambda item: item["path"]),
                "lifecycle": lifecycle}
    staging = out.parent / f".{out.name}.{os.getpid()}.{os.urandom(4).hex()}.tmp"
    staging.mkdir()
    try:
        for relative, data in payload:
            target = staging.joinpath(*PurePosixPath(relative).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "xb") as stream:
                stream.write(data)
        with open(staging / "bundle.json", "xb") as stream:
            stream.write(emit_json(manifest).encode("utf-8"))
        os.rename(staging, out)
    except BaseException:
        import shutil
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return {"schema_version": 1, "status": "ok", "written": True, "out": out.name,
            "patterns": [item["ref"] for item in patterns], "files": len(files), "bytes": total,
            "bundle_sha256": content_digest(manifest),
            "limits": "Local directory only: no upload, no URL fetch, no catalogs, bindings or source documents.",
            "diagnostics": [], "metrics": reader.metrics()}


def _read_bundle(bundle: Path, reader: Reader) -> tuple[dict, dict, dict]:
    bundle = Path(bundle)
    if _is_link(bundle) or not bundle.is_dir():
        _fail("unsafe_path", "the bundle must be an existing, unlinked directory", str(bundle))
    manifest = parse_json(reader.read(bundle / "bundle.json", kind="input", limit=LIMITS.catalog_bytes),
                          limit=LIMITS.catalog_bytes, what="bundle manifest")
    _object(manifest, "bundle", ("schema_version", "patterns", "files", "lifecycle"))
    _schema_version(manifest, "bundle")
    actual, total = {}, 0
    for directory, subdirectories, names in os.walk(bundle, followlinks=False):
        for name in subdirectories:
            if _is_link(Path(directory) / name):
                _fail("unsafe_path", "links and reparse points are refused inside a bundle", str(Path(directory) / name))
        for name in names:
            path = Path(directory) / name
            relative = path.relative_to(bundle).as_posix()
            if relative == "bundle.json":
                continue
            validate_relative_path(relative, "bundle member")
            data = reader.read(path, kind="asset", limit=LIMITS.asset_bytes)
            total += len(data)
            if total > LIMITS.bundle_bytes:
                _fail("resource_limit", f"the bundle exceeds {LIMITS.bundle_bytes} bytes")
            actual[relative] = data
    listed = {}
    for index, item in enumerate(_array(manifest["files"], "bundle.files")):
        _object(item, f"bundle.files[{index}]", ("path", "sha256"))
        path = str(validate_relative_path(item["path"], f"bundle.files[{index}].path"))
        if path in listed:
            _fail("invalid_bundle", f"{path} is listed twice")
        listed[path] = _matching(item["sha256"], HEX64, f"bundle.files[{index}].sha256", "sha256", 64)
    if set(listed) != set(actual):
        _fail("invalid_bundle", "bundle files and manifest disagree: unexpected "
              f"{sorted(set(actual) - set(listed))}, missing {sorted(set(listed) - set(actual))}")
    for path, digest in listed.items():
        if hashlib.sha256(actual[path]).hexdigest() != digest:
            _fail("invalid_bundle", f"{path} does not match its manifest digest")
    records = {}
    for index, item in enumerate(_array(manifest["patterns"], "bundle.patterns", nonempty=True)):
        _object(item, f"bundle.patterns[{index}]", ("ref", "path"))
        ref = parse_exact_ref(item["ref"], f"bundle.patterns[{index}].ref")
        if _key(ref) in records:
            _fail("invalid_bundle", f"{ref.text} appears twice")
        if item["path"] not in actual:
            _fail("invalid_bundle", f"{ref.text} file is not in the bundle")
        pattern = parse_pattern(parse_json(actual[item["path"]], limit=LIMITS.pattern_bytes, what=item["path"]),
                                item["path"])
        if (pattern.id, pattern.version, pattern.digest) != (ref.id, ref.version, ref.sha256):
            _fail("invalid_bundle", f"{item['path']} does not match its exact reference")
        prefix = PurePosixPath(item["path"]).parent
        assets = []
        for asset in pattern.assets:
            member = (prefix / asset.path).as_posix()
            if member not in actual or hashlib.sha256(actual[member]).hexdigest() != asset.sha256:
                _fail("invalid_bundle", f"{ref.text} asset {asset.path} is missing or changed")
            assets.append((asset.path, actual[member]))
        records[_key(ref)] = {"ref": ref, "pattern": pattern, "assets": assets}
    lifecycle = {}
    for index, item in enumerate(_array(manifest["lifecycle"], "bundle.lifecycle")):
        _object(item, f"bundle.lifecycle[{index}]", ("ref", "effective_status", "events"))
        ref = parse_exact_ref(item["ref"], f"bundle.lifecycle[{index}].ref")
        lifecycle[_key(ref)] = copy_json(item)
    if set(lifecycle) != set(records):
        _fail("invalid_bundle", "every bundled pattern needs exactly one lifecycle record")
    for key, item in lifecycle.items():
        at = f"bundle.lifecycle[{records[key]['ref'].text}]"
        revoked, last = False, None
        for index, event in enumerate(_array(item["events"], f"{at}.events")):
            where = f"{at}.events[{index}]"
            if not isinstance(event, dict) or event.get("kind") not in ("lifecycle", "revocation"):
                _fail("invalid_bundle", "each event is a lifecycle or revocation record", where)
            _timestamp(event.get("at"), f"{where}.at")
            if event["kind"] == "revocation":
                revoked = True
            elif event.get("status") not in ("deprecated", "retired"):
                _fail("invalid_bundle", "a lifecycle event is deprecated or retired", where)
            elif last is None or _instant(event["at"]) > _instant(last["at"]):
                last = event
        derived = "revoked" if revoked else last["status"] if last else records[key]["pattern"].status
        if item["effective_status"] != derived:
            _fail("invalid_bundle", f"{at}: effective_status {item['effective_status']} contradicts its events "
                  f"({derived})")
    for key, record in records.items():
        state = lifecycle[key]["effective_status"]
        if state in ("retired", "revoked"):
            _fail("bundle_contains_" + state, f"{record['ref'].text} is {state}; import refuses it",
                  status="unavailable")
        if state not in ("draft", "approved", "deprecated"):
            _fail("invalid_bundle", f"unknown effective status {state}")
        for child in record["pattern"].includes:
            if _key(child) not in records:
                _fail("external_dependency", f"{record['ref'].text} includes {child.text}, which is not in the "
                      "bundle; v1 never fetches external dependencies")
    return manifest, records, lifecycle


def import_bundle(roots: Roots, bundle: Path, *, scope: str, destination_source: str, version_map_value: Any,
                  write: bool = False, expected_catalog_digest: Optional[str] = None,
                  reader: Optional[Reader] = None) -> dict:
    """Validate a whole bundle, preview the children-first transformation, and optionally stage drafts."""
    reader = reader or Reader()
    _manifest, records, lifecycle = _read_bundle(bundle, reader)
    _matching(destination_source, NAMESPACED_ID, "--destination-source", "source ID")
    root, _ = _scope_root(roots, scope)
    mapping = {}
    for index, item in enumerate(_array(version_map_value, "version_map", nonempty=True)):
        at = f"version_map[{index}]"
        _object(item, at, ("original", "id", "version"))
        original = parse_exact_ref(item["original"], f"{at}.original")
        if _key(original) not in records or _key(original) in mapping:
            _fail("invalid_version_map", f"{original.text} is not a bundled record or is mapped twice", at)
        mapping[_key(original)] = (_matching(item["id"], NAMESPACED_ID, f"{at}.id", "pattern ID"),
                                   _matching(item["version"], VERSION, f"{at}.version", "version", 64))
    if set(mapping) != set(records):
        _fail("invalid_version_map", "the version map must cover every bundled record exactly once")
    if len(set(mapping.values())) != len(mapping):
        _fail("invalid_version_map", "two records map to the same destination id and version")
    existing, _ = _read_catalog_value(root, Reader())
    if existing is not None and existing["source_id"] != destination_source:
        _fail("source_id_mismatch", f"this scope's source is {existing['source_id']}, not {destination_source}")
    if existing is None:
        other = load_sources(roots, reader)
        if any(item.catalog.source_id == destination_source for item in other.catalogs):
            _fail("source_id_collision", f"source ID {destination_source} is already configured elsewhere")
    taken = {(item["id"], item["version"]) for item in (existing or {"entries": []})["entries"]}
    clashes = sorted(f"{pid}@{version}" for pid, version in mapping.values() if (pid, version) in taken)
    if clashes:
        _fail("version_exists", f"destination versions already exist: {', '.join(clashes)}", status="collision")
    transformed, order, diagnostics = {}, [], []

    def visit(key, stack=()):
        if key in transformed:
            return
        if key in stack:
            _fail("include_cycle", "the bundle's includes form a cycle")
        record = records[key]
        for child in record["pattern"].includes:
            visit(_key(child), stack + (key,))
        raw = copy_json(dict(record["pattern"].raw))
        new_id, new_version = mapping[key]
        provenance = {"original": record["ref"].to_json(), "publication_status": raw["status"],
                      "approval": raw.get("approval"), "replaced_by": raw.get("replaced_by"),
                      "lifecycle_status": lifecycle[key]["effective_status"]}
        previous = raw.get("extensions", {}).get("lintel.imported")
        if previous is not None:
            provenance["previous"] = previous
        raw.update(id=new_id, version=new_version, status="draft")
        raw.pop("approval", None)
        raw.pop("replaced_by", None)
        raw["includes"] = [transformed[_key(child)]["ref"].to_json() for child in record["pattern"].includes]
        raw["extensions"] = dict(raw.get("extensions", {}), **{"lintel.imported": provenance})
        pattern = parse_pattern(raw, f"import {new_id}@{new_version}")
        transformed[key] = {"ref": ExactRef(destination_source, new_id, new_version, pattern.digest),
                            "pattern": pattern, "assets": record["assets"]}
        order.append(key)
        if lifecycle[key]["effective_status"] == "deprecated":
            diagnostics.append(_note("imported_deprecated", f"{record['ref'].text} was deprecated at its source",
                                     "warning"))

    for key in sorted(records):
        visit(key)
    preview = [{"original": records[key]["ref"].to_json(), "destination": transformed[key]["ref"].to_json()}
               for key in order]
    report = {"schema_version": 1, "status": "ok", "written": False, "scope": scope,
              "destination_source": destination_source, "mapping": preview,
              "limits": "Imported records are drafts; original approval and lifecycle are inert provenance in "
                        "extensions['lintel.imported'], not local trust. Approve children first after review.",
              "diagnostics": diagnostics, "metrics": reader.metrics()}
    if not write:
        return report

    def build(value):
        if value is None:
            value = {"schema_version": 1, "source_id": destination_source, "entries": [], "includes": [],
                     "bindings": [], "lifecycle": []}
        elif value["source_id"] != destination_source:
            _fail("source_id_mismatch", "the destination source changed", status="collision")
        extra = [(f"{transformed[key]['ref'].id}/{transformed[key]['ref'].version}/{path}", data)
                 for key in order for path, data in transformed[key]["assets"]]
        return copy_json(value), [transformed[key]["pattern"] for key in order], diagnostics, extra

    written = _publish(root, reader, expected=expected_catalog_digest, build=build)
    report.update(written=True, published=written["published"], catalog_sha256=written["catalog_sha256"],
                  metrics=reader.metrics())
    return report
