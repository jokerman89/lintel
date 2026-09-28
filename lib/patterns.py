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
TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:[Zz]|\+00:00)\Z")
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
    core = value[:-6] if value.endswith("+00:00") else value[:-1]
    try:
        _dt.datetime.fromisoformat(core.replace("t", "T"))
    except ValueError:
        _fail("invalid_schema", "invalid timestamp", where)
    return value


def _instant(value: str) -> _dt.datetime:
    """Comparable instant for validated timestamps (ordering must not depend on spelling)."""
    core = value[:-6] if value.endswith("+00:00") else value[:-1]
    return _dt.datetime.fromisoformat(core.replace("t", "T")).replace(tzinfo=_dt.timezone.utc)


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
        try:
            with open(path, "rb") as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    _fail("unsafe_path", "only regular files are read", str(path))
                data = stream.read(limit + 1)
        except FileNotFoundError:
            if optional:
                return None
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
    for pack in chain:
        manifest = Path(pack["path"])
        digest = str(pack["digest"])
        ancestry.append({"pack": pack["name"], "version": pack["version"], "root": manifest.parent.as_posix(),
                         "manifest_sha256": digest.removeprefix("sha256:")})
    context = {"schema_version": 1, "status": status, "identity": identity, "source": source,
               "ancestry": ancestry, "diagnostics": diagnostics}
    parse_pack_context(context)
    return context


def build_envelope(repository: Optional[Path], personal: Path, pack_context: Mapping[str, Any],
                   diagnostics: Sequence[Mapping[str, str]] = ()) -> dict:
    """Serialize the roots envelope with JSON (never shell interpolation) and validate it."""
    envelope = {"schema_version": 1,
                "repository": None if repository is None else Path(repository).resolve().as_posix(),
                "personal": Path(personal).resolve().as_posix(), "pack_context": dict(pack_context),
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
    scope: str  # repo | pack | personal (the activating top-level scope)
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
    bindings: list[tuple[str, Binding]] = field(default_factory=list)
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
    if locator == "repo":
        if sources.roots.repository is None:
            _fail("repository_required", "repository locator needs an explicit repository root", status="unavailable")
        return sources.roots.repository / ".claude" / "patterns"
    if locator == "personal":
        return sources.roots.personal / "patterns"
    return _verified_ancestor(sources, locator[5:]).root


def _load_catalog(sources: SourceSet, locator: str, relative: str, scope: str, active: bool, depth: int,
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
        return
    if len(sources.catalogs) >= LIMITS.source_catalogs:
        _fail("resource_limit", f"more than {LIMITS.source_catalogs} source catalogs")
    sources.catalogs.append(LoadedCatalog(locator, scope, path.parent, catalog, active, depth))
    if catalog.bindings:
        if active:
            sources.bindings.extend((scope, binding) for binding in catalog.bindings)
        else:
            sources.notes.append(_note("personal_bindings_inactive",
                                       f"{catalog.source_id} bindings are not auto-applied in v1"))
    allowed = {locator} | {f"pack:{item.pack}" for item in sources.roots.pack_context.ancestry}
    for include in sorted(catalog.includes, key=lambda item: (item.locator, item.path)):
        if include.locator not in allowed:
            _fail("include_locator_refused", f"{catalog.source_id} cannot include from {include.locator}")
        _load_catalog(sources, include.locator, include.path, scope, active, depth + 1, include.sha256,
                      stack + [identity])


def load_sources(roots: Roots, reader: Optional[Reader] = None) -> SourceSet:
    """Load configured catalogs and bindings. Unavailable sources become blockers, not empty success."""
    sources = SourceSet(roots, reader or Reader())
    if roots.repository is not None:
        _load_catalog(sources, "repo", "catalog.json", "repo", True, 0, None, [], optional=True)
        bindings_path = contained_path(roots.repository / ".claude" / "patterns", "bindings.json")
        data = sources.reader.read(bindings_path, kind="bindings", limit=LIMITS.input_bytes, optional=True)
        if data is not None:
            sources.bindings.extend(("repo", binding) for binding in parse_bindings(
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
                _load_catalog(sources, f"pack:{owner[0].pack}", context.source_value, "pack", True, 0, None, [])
            except PatternError as error:
                if error.status != "unavailable":
                    raise
                sources.blockers.append(dict(error.diagnostic()))
    _load_catalog(sources, "personal", "catalog.json", "personal", False, 0, None, [], optional=True)
    seen = set()
    for scope, binding in sources.bindings:
        if (scope, binding.id) in seen:
            _fail("invalid_schema", f"duplicate {scope} binding ID {binding.id}")
        seen.add((scope, binding.id))
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
    return pattern


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

REPORT_KEYS = ("schema_version", "status", "context_digest", "sources", "selected", "candidates",
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


class _Resolution:
    def __init__(self, sources: SourceSet, context: Context, preview_draft: bool, today: _dt.date):
        self.sources, self.context, self.preview_draft, self.today = sources, context, preview_draft, today
        self.nodes: dict[tuple, _Node] = {}
        self.loaded: dict[tuple, tuple] = {}
        self.digests: dict[tuple, str] = {}
        self.diagnostics: list[dict] = list(sources.blockers) + list(sources.notes)
        self.bindings: list[dict] = []

    def problem(self, status: str, code: str, message: str, **details) -> None:
        self.diagnostics.append(_note(code, message, "error", status=status, **details))

    def scope_of(self, ref: ExactRef) -> str:
        loaded = self.sources.by_source(ref.source)
        return loaded.scope if loaded is not None else "personal"

    def expand(self, ref: ExactRef, role: str, scope: str, reason: dict, explicit: bool,
               stack: tuple = (), blocking: Optional[bool] = None) -> Optional[list[_Node]]:
        """Return the node closure, or None when this subtree is blocked (already diagnosed)."""
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
            preview = False
            if state == "draft":
                if not (explicit and not stack and self.preview_draft):
                    _fail("draft_not_eligible", f"{ref.text} is a draft; drafts are never selected for execution"
                          + ("" if explicit else " by bindings or includes"), status="unavailable")
                preview = True
            elif state in ("retired", "revoked"):
                _fail(f"pattern_{state}", f"{ref.text} is {state}", status="unavailable")
            if pattern is None:
                pattern = _read_pattern(self.sources, loaded, entry)
                self.loaded[ref.key] = (loaded, entry, state, replacement, pattern)
        except PatternError as error:
            if error.status == "invalid":
                raise
            if blocking:
                self.diagnostics.append(dict(error.diagnostic(), ref=ref.to_json()))
            else:
                self.diagnostics.append(_note("default_skipped", f"default {ref.text} skipped: {error.message}",
                                              "warning", ref=ref.to_json()))
            return None
        decision = evaluate_selector(pattern.applies_to, self.context)
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
        if state == "deprecated":
            self.diagnostics.append(_note("pattern_deprecated", f"{ref.text} is deprecated", "warning",
                                          ref=ref.to_json(),
                                          replaced_by=(replacement or pattern.replaced_by).to_json()
                                          if (replacement or pattern.replaced_by) else None))
        if preview:
            self.problem("unavailable", "draft_preview_only",
                         f"{ref.text} is a draft preview; this report is not executable selection evidence",
                         ref=ref.to_json())
        closure = [_Node(ref, pattern, state, role, scope, [reason], preview)]
        for child in pattern.includes:
            nodes = self.expand(child, role, scope, {"kind": "include", "parent": ref.to_json()}, False,
                                stack + (ref.key,), blocking)
            if nodes is None:
                self.diagnostics.append(_note("include_blocked", f"{ref.text} is blocked by its include {child.text}",
                                              "info", ref=ref.to_json(), include=child.to_json()))
                return None
            closure.extend(nodes)
        return closure

    def add(self, nodes: Optional[list[_Node]]) -> None:
        for node in nodes or ():
            key = node.ref.key
            current = self.nodes.get(key)
            if current is None:
                self.nodes[key] = node
                continue
            if node.role == "required":
                current.role = "required"
            if _SCOPE_RANK[node.scope] < _SCOPE_RANK[current.scope]:
                current.scope = node.scope
            current.reasons.extend(item for item in node.reasons if item not in current.reasons)
            current.preview = current.preview or node.preview


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
            if (loaded.catalog.source_id, entry.id, entry.version) in resolution.nodes:
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
    return {"schema_version": 1, "status": status, "context_digest": context_digest, "sources": [],
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
            today: Optional[_dt.date] = None, reader: Optional[Reader] = None, explain: bool = False) -> dict:
    """Metadata-first resolution (spec section 5). Invalid input raises PatternError."""
    if type(context_budget) is not int or context_budget < 1:
        _fail("invalid_budget", "context budget must be a positive integer within the resource limit")
    today = today or _dt.datetime.now(_dt.timezone.utc).date()
    reader = reader or Reader()
    sources = load_sources(roots, reader)
    resolution = _Resolution(sources, context, preview_draft, today)
    for scope, binding in sorted(sources.bindings, key=lambda item: (_SCOPE_RANK[item[0]], item[1].id)):
        decision = evaluate_selector(binding.when, context)
        resolution.bindings.append({"scope": scope, "id": binding.id, "role": binding.role,
                                    "decision": decision.decision, "missing_keys": list(decision.missing),
                                    "mismatched_keys": list(decision.mismatched)})
        if decision.decision == "matched":
            for ref in binding.use:
                resolution.add(resolution.expand(ref, binding.role, scope, {
                    "kind": "binding", "binding": binding.id, "scope": scope,
                    "approved_by": binding.approved_by, "approval_ref": binding.approval_ref}, False))
        elif decision.decision == "needs-context" and binding.role == "required":
            resolution.problem("needs-context", "required_binding_needs_context",
                               f"required binding {scope}:{binding.id} needs facts: {', '.join(decision.missing)}",
                               binding=binding.id, scope=scope, missing_keys=list(decision.missing))
    for item in refs:
        resolution.add(resolution.expand(item.ref, item.role, resolution.scope_of(item.ref), {
            "kind": "explicit", "approved_by": item.approved_by, "approval_ref": item.approval_ref}, True))
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
            if node.pattern.review_after and _dt.date.fromisoformat(node.pattern.review_after) < today:
                resolution.problem("unavailable", "review_overdue",
                                   f"{node.ref.text} is past review_after and needs a freshness attestation",
                                   ref=node.ref.to_json())
            for index, source in enumerate(node.pattern.sources):
                if source.is_url:
                    resolution.problem("unavailable", "source_attestation_required",
                                       f"{node.ref.text} source {index} is a URL and needs a reviewed source attestation",
                                       ref=node.ref.to_json(), source_index=index)
        elif node.pattern.review_after and _dt.date.fromisoformat(node.pattern.review_after) < today:
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
                         "clauses": [node.pattern.clause_ref(clause.id) for clause in node.pattern.requirements]})
    statuses = [item["status"] for item in resolution.diagnostics if item.get("severity") == "error" and "status" in item]
    status = _worst(statuses, "ready" if selected else "empty")
    metrics = dict(reader.metrics(), selected_patterns=len(selected), selected_context_code_points=selected_chars,
                   advisory_summary_code_points=sum(len(item["summary"]) for item in candidates["items"]),
                   context_budget=context_budget, bindings_evaluated=len(resolution.bindings))
    report = {"schema_version": 1, "status": status, "context_digest": context.digest,
              "sources": [item.summary() for item in sources.catalogs], "selected": selected,
              "candidates": candidates, "requirements": requirements, "settings": settings,
              "overrides": applied_overrides, "exceptions": applied_exceptions,
              "diagnostics": resolution.diagnostics, "metrics": metrics,
              "limits": "Runtime checks structure and declared provenance only; a repository can forge "
                        "bindings, and approval, source authenticity and prose conflicts need review."}
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
