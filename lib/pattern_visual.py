#!/usr/bin/env python3
# component: reusable-patterns-visual-adapter
# implements: ADR-0038, ADR-0015, ADR-0016, ADR-0028, ADR-0034
# intent: .claude/plans/reusable-patterns/spec.md
# constraints: stdlib only; consumes lib/patterns.py reports, locks and validators; never recomputes precedence, digests or pattern validation; reads no asset or pattern body itself
# last_intent_review: 2026-09-28
"""Design-spec adapter for reusable patterns (spec sections 8 and 9).

- Discriminate a legacy visual `pattern.json` (its own schema_version 1) from a universal
  pattern and convert its observations into a universal **draft** of defaults, keeping the
  original bytes unchanged as a `visual-legacy` asset.
- Project the final structured-setting winners of a ready resolution into the fixed v1
  destination table of `frontend-design-spec.json`, and check a spec against them per clause.
- Build and verify the pipeline `design-spec.json` attachment that references a lock.

Mechanical checks here are supplemental evidence. They never clear review (ADR-0028), and
unknown settings stay open obligations rather than passes.
"""
from __future__ import annotations

import copy
import datetime as _dt
import hashlib
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Mapping, Optional

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import patterns as p  # noqa: E402

__all__ = (
    "SETTINGS", "PALETTE_PREFIX", "LEGACY_MARKERS", "destination", "classify_document",
    "legacy_to_draft", "stage_draft", "project_visual", "validate_visual", "design_attachment",
    "verify_design_attachment",
)

# Spec section 9: the only mechanically projected settings in v1.
SETTINGS = {
    "visual.layout.max-width": (("layout_grammar", "max_width"), "text"),
    "visual.layout.section-spacing": (("layout_grammar", "section_spacing"), "text"),
    "visual.layout.grid": (("layout_grammar", "grid"), "text"),
    "visual.interaction.scroll-smoothing": (("interaction_signature", "scroll_smoothing"), "boolean"),
    "visual.interaction.hover-intent": (("interaction_signature", "hover_intent"), "text"),
    "visual.interaction.page-transitions": (("interaction_signature", "page_transitions"), "text"),
}
PALETTE_PREFIX = "visual.palette."
_TOKEN = re.compile(r"[a-z][a-z0-9-]*\Z")
_COLOR = re.compile(r"#[0-9A-Fa-f]{6}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_WINNING = ("mandatory", "default", "overridden")
_LIMITS_NOTE = ("Mechanical structured-setting evidence only; prose clauses, source authenticity and "
                "review clearance stay with the ADR-0028 shared review.")

# Top-level fields that only the legacy frontend-style-extract/seed schema uses.
LEGACY_MARKERS = frozenset({"layout_grammar", "motion_language", "interaction_patterns",
                            "component_library_fingerprint", "shader_thesis", "visual_thesis_distilled"})
_UNIVERSAL_ONLY = frozenset({"id", "requirements", "applies_to", "includes", "owner"})
# (legacy container, legacy key, setting, clause ID)
_LEGACY_MAP = (
    ("layout_grammar", "max_width", "visual.layout.max-width", "LAYOUT-MAX-WIDTH"),
    ("layout_grammar", "section_spacing", "visual.layout.section-spacing", "LAYOUT-SECTION-SPACING"),
    ("layout_grammar", "grid", "visual.layout.grid", "LAYOUT-GRID"),
    ("interaction_patterns", "scroll_smoothing", "visual.interaction.scroll-smoothing", "INTERACTION-SCROLL-SMOOTHING"),
    ("interaction_patterns", "hover_intent", "visual.interaction.hover-intent", "INTERACTION-HOVER-INTENT"),
    ("interaction_patterns", "page_transitions", "visual.interaction.page-transitions", "INTERACTION-PAGE-TRANSITIONS"),
)


def _fail(code: str, message: str, status: str = "invalid", where: str = ""):
    raise p.PatternError(code, message, status=status, where=where)


def destination(setting: str) -> Optional[tuple[tuple[str, ...], str]]:
    """Destination path and value kind for a v1 visual setting, or None when unsupported."""
    if setting in SETTINGS:
        return SETTINGS[setting]
    if setting.startswith(PALETTE_PREFIX):
        token = setting[len(PALETTE_PREFIX):]
        if _TOKEN.match(token):
            return ("palette", "tokens", token), "color"
    return None


def _display(path: tuple[str, ...]) -> str:
    if path[:2] == ("palette", "tokens"):
        return f"palette.tokens[{path[2]}]"
    return ".".join(path)


def _typed(kind: str, value: Any) -> bool:
    if kind == "text":
        return isinstance(value, str) and bool(value.strip())
    if kind == "boolean":
        return type(value) is bool
    return isinstance(value, str) and bool(_COLOR.match(value))


def _equal(kind: str, expected: Any, actual: Any) -> bool:
    """Exact type and value comparison; callers type-check `expected` first (M1)."""
    if not _typed(kind, expected) or not _typed(kind, actual):
        return False
    if kind == "color":
        return expected.lower() == actual.lower()
    return type(expected) is type(actual) and expected == actual


_URL = re.compile(r"https://[^\s]+\Z")


def _portable_ref(value: Any) -> str:
    """A committed provenance label: an https URL or a portable relative path (never a local root)."""
    if isinstance(value, str) and _URL.match(value):
        return value
    if isinstance(value, str) and value.split("/", 1)[0].startswith("~"):
        _fail("unportable_source_ref", "source_ref must not name a home directory; use a vault-relative label")
    try:
        return p.validate_relative_path(value, "source_ref").as_posix()
    except p.PatternError as error:
        _fail("unportable_source_ref", f"source_ref must be an https URL or a portable relative label: "
                                       f"{error.message}")


# ---------------------------------------------------------------- legacy discrimination

def classify_document(value: Any, *, location: Optional[str] = None) -> str:
    """Return `universal` or `legacy-visual`; schema_version 1 alone never decides.

    A universal record is one the shared core validator accepts. A legacy record carries the
    legacy visual fields, a `name` and none of the universal-only fields. `location` is only a
    hint: a legacy pattern may live under any `--out` directory, but a universal pattern inside a
    legacy `design-patterns` vault is refused as a likely mix-up.
    """
    if not isinstance(value, dict) or type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        _fail("unknown_pattern_document", "not a schema_version 1 pattern document")
    legacy_location = location is not None and "design-patterns" in PurePosixPath(location).parts
    try:
        p.parse_pattern(value)
    except p.PatternError:
        pass
    else:
        if legacy_location:
            _fail("location_mismatch", "a universal pattern stored in a legacy design-patterns vault", where=location)
        return "universal"
    if isinstance(value.get("name"), str) and value.keys() & LEGACY_MARKERS and not value.keys() & _UNIVERSAL_ONLY:
        return "legacy-visual"
    _fail("unknown_pattern_document", "neither a valid universal pattern nor a legacy visual pattern")


def _observed_at(legacy: dict, fallback: Optional[str]) -> str:
    for candidate in (fallback, legacy.get("generated_at")):
        if isinstance(candidate, str) and p.TIMESTAMP.match(candidate):
            return candidate
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def legacy_to_draft(data: bytes, *, pattern_id: str, applies_to: Mapping[str, Any], owner: str,
                    source_ref: str, version: str = "0.1.0", asset_path: str = "visual-legacy/pattern.json",
                    reuse: str = "rights not established; internal draft only",
                    observed_at: Optional[str] = None, location: Optional[str] = None) -> dict:
    """Convert validated legacy observations into a universal draft of defaults (spec section 9).

    The original bytes become a `visual-legacy` asset with their raw digest; unrecognized fields
    stay in that asset and are not interpreted. Observations are never `confirmed`. The draft is
    validated by the shared core validator and is never approved or registered here.
    `source_ref` is recorded as provenance in the committed draft, so it must be an https URL or
    a portable relative (vault) label; absolute, drive, UNC and home paths are refused.
    """
    source_ref = _portable_ref(source_ref)
    legacy = p.parse_json(data, limit=p.LIMITS.asset_bytes, what="legacy visual pattern")
    if classify_document(legacy, location=location) != "legacy-visual":
        _fail("not_legacy_visual", "the input is already a universal pattern; capture it directly")
    p.validate_relative_path(asset_path, "asset_path")
    confidence = "inferred" if legacy.get("extraction_confidence") in ("high", "medium") else "unknown"
    requirements, mapped, unmapped = [], set(), []
    for container, key, setting, clause_id in _LEGACY_MAP:
        section = legacy.get(container)
        if not isinstance(section, dict) or key not in section:
            continue
        value = section[key]
        kind = SETTINGS[setting][1]
        if not _typed(kind, value):
            unmapped.append({"field": f"{container}.{key}", "reason": f"not a {kind} value; left in the asset"})
            continue
        mapped.add((container, key))
        requirements.append({
            "id": clause_id, "level": "default", "setting": setting, "value": value,
            "text": f"Default {setting} = {p.canonical_json(value).decode('utf-8')}, observed in legacy "
                    f"visual pattern {legacy['name']}.",
            "verify": f"Compare {_display(SETTINGS[setting][0])} in frontend-design-spec.json."})
    tokens = legacy.get("palette", {}).get("tokens") if isinstance(legacy.get("palette"), dict) else None
    if isinstance(tokens, dict):
        for token in sorted(tokens):
            value = tokens[token]
            if not _TOKEN.match(token) or not _typed("color", value):
                unmapped.append({"field": f"palette.tokens.{token}", "reason": "not a v1 token/#RRGGBB value"})
                continue
            mapped.add(("palette", token))
            setting = PALETTE_PREFIX + token
            requirements.append({"id": "PALETTE-" + token.upper(), "level": "default", "setting": setting,
                                 "value": value.lower(),
                                 "text": f"Default palette token {token} = {value.lower()}, observed in legacy "
                                         f"visual pattern {legacy['name']}.",
                                 "verify": f"Compare palette.tokens[{token}] in frontend-design-spec.json."})
    uninterpreted = sorted(key for key in legacy if key not in ("schema_version", "name"))
    digest = hashlib.sha256(data).hexdigest()
    draft = {
        "schema_version": 1, "id": pattern_id, "version": version, "status": "draft",
        "summary": f"Draft visual defaults converted from legacy pattern {legacy['name']}"[:240],
        "owner": owner, "applies_to": copy.deepcopy(dict(applies_to)), "includes": [],
        "sources": [{"kind": "observation", "ref": asset_path, "root": "pattern", "section": "",
                     "observed_at": _observed_at(legacy, observed_at), "confidence": confidence,
                     "reuse": reuse, "sha256": digest}],
        "requirements": requirements,
        "guidance": ("Converted from a legacy visual pattern. Only the v1 structured settings were mapped, "
                     "as defaults. Typography, motion, shader, component, licensing and other fields stay "
                     "unchanged in the visual-legacy asset and are not universal policy. The conversion "
                     "does not verify fonts, accessibility, dependencies or licensing."),
        "assets": [{"path": asset_path, "kind": "visual-legacy", "sha256": digest}],
        "extensions": {"lintel.visual-legacy": {"name": legacy["name"], "original": source_ref}},
    }
    p.parse_pattern(draft, "draft")
    return {"schema_version": 1, "status": "draft", "draft": draft, "asset": {"path": asset_path, "sha256": digest},
            "mapped_settings": [item["setting"] for item in requirements], "unmapped": unmapped,
            "uninterpreted_fields": uninterpreted,
            "unknowns": ["fonts", "accessibility", "licensing", "dependencies"],
            "limits": "A draft for review; conversion never approves, registers or promotes observations."}


def stage_draft(conversion: Mapping[str, Any], data: bytes, directory: Path) -> Path:
    """Write a conversion's draft and its declared legacy asset into a NEW scratch directory.

    The result is capture input: `pattern.json` with its declared sidecar beside it, for
    `li-pattern capture --input <dir>/pattern.json`, which verifies and stages the closure before
    registration. Nothing is written into a catalog here, and nothing is overwritten.
    """
    draft = p.parse_pattern(copy.deepcopy(dict(conversion["draft"])), "draft")
    asset = conversion["asset"]
    if hashlib.sha256(data).hexdigest() != asset["sha256"] or \
            not any(item.path == asset["path"] and item.sha256 == asset["sha256"] for item in draft.assets):
        _fail("asset_digest_mismatch", "the supplied bytes are not the converted legacy asset", "unavailable")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    for relative, content in ((asset["path"], data), ("pattern.json", p.emit_json(draft.raw).encode("utf-8"))):
        target = p.contained_path(directory, relative, "staged draft")
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "xb") as stream:
            stream.write(content)
    return directory / "pattern.json"


# ---------------------------------------------------------------- projection

def _report(resolution: Any, context: Optional[p.Context] = None, refs: Any = ()) -> Mapping[str, Any]:
    """Return a selection the core has checked: a lock, or a report bound to its inputs (M2).

    A lock is re-checked with `parse_lock`; persisted or cross-entry callers pass a lock that
    `verify_lock` accepted. A fresh in-process report must come with the `context` (and any
    explicit `refs`) it was resolved with; the core's public `validate_selection_report` (R10)
    rechecks it, with the public `build_lock` as the pre-R10 route. A report whose content no
    longer matches, or a bare report, is `selection_not_usable`. Non-ready/empty reports are
    returned so their status is reported.
    """
    if not isinstance(resolution, Mapping) or any(key not in resolution for key in p.REPORT_KEYS):
        _fail("invalid_resolution", "expected a resolution report or lock from lib/patterns.py")
    if "created_at" in resolution:
        return p.parse_lock(copy.deepcopy(dict(resolution)))
    if resolution.get("status") not in ("ready", "empty"):
        return resolution
    if not isinstance(context, p.Context):
        _fail("selection_not_usable", "a resolution report is usable only with the context it was resolved "
                                      "with (and its refs); across entries pass a verified lock", "invalid")
    if refs and not all(isinstance(item, p.InvocationRef) for item in refs):
        refs = p.parse_refs(list(refs))
    validate = getattr(p, "validate_selection_report", None)
    if validate is not None:
        # Core R10 helper: same digest material as locks; raises selection_not_usable.
        return validate(resolution, context=context, refs=tuple(refs))
    budget = resolution.get("metrics", {}).get("context_budget", p.LIMITS.context_budget)
    try:
        return p.build_lock(resolution, context, refs=tuple(refs), context_budget=budget)
    except p.PatternError as error:
        _fail("selection_not_usable", f"the report does not match its inputs: {error.message}", "invalid")


def _require_ready(resolution: Mapping[str, Any]) -> str:
    status = resolution["status"]
    if status != "ready":
        _fail("resolution_not_ready", f"visual projection needs a ready resolution (status {status})",
              status=status if status in ("needs-context", "conflict", "unavailable", "invalid") else "invalid")
    digest = resolution.get("selection_digest")
    if not isinstance(digest, str) or not _HEX64.match(digest):
        _fail("selection_unbound", "a ready resolution without selection_digest (for example a preview) "
                                   "is not executable", status="unavailable")
    return digest


def _winners(resolution: Mapping[str, Any]):
    for setting in sorted(resolution["settings"]):
        record = resolution["settings"][setting]
        if not setting.startswith("visual.") or record.get("state") not in _WINNING or "value" not in record:
            if setting.startswith("visual.") and record.get("state") == "conflict":
                _fail("setting_conflict", f"{setting} is in conflict; resolve it before projection", "conflict")
            continue
        yield setting, record


def _review_required(resolution: Mapping[str, Any], unverified: set) -> list[dict]:
    """Selected clauses that mechanical checks do not cover and ordinary review must assess."""
    result = []
    for item in resolution["requirements"]:
        if item["state"] not in ("mandatory", "default", "waived"):
            continue
        setting = item.get("setting")
        if setting is None or setting in unverified or not setting.startswith("visual.") or destination(setting) is None:
            result.append({"clause": item["clause"], "level": item["level"], "state": item["state"],
                           "setting": setting})
    return result


def project_visual(base_spec: Mapping[str, Any], resolution: Mapping[str, Any], *,
                   context: Optional[p.Context] = None, refs: Any = (),
                   phase: Optional[str] = None, domain: Optional[str] = None) -> dict:
    """Apply final visual setting winners to a frontend design spec copy (spec section 9).

    `resolution` is a verified lock, or an in-process report with its `context`/`refs`.
    Empty resolutions leave a genuine no-pattern spec unchanged (ADR-0016 precedence stays); a
    spec that still carries a `pattern_context` is a stale selection and is refused (L4).
    Wrong-shaped existing objects or wrongly typed winners are conflicts, never coerced.
    """
    if not isinstance(base_spec, Mapping):
        _fail("invalid_spec", "the design spec must be a JSON object")
    resolution = _report(resolution, context, refs)
    spec = copy.deepcopy(dict(base_spec))
    if resolution["status"] == "empty" and not resolution["selected"]:
        if "pattern_context" in spec:
            _fail("stale_pattern_context", "the spec carries a pattern_context but the current resolution selects "
                                           "no patterns; re-plan instead of keeping or dropping it", "conflict")
        return {"schema_version": 1, "status": "empty", "spec": spec, "pattern_context": None, "applied": [],
                "unverified_settings": [], "review_required": [], "limits": _LIMITS_NOTE}
    digest = _require_ready(resolution)
    applied, unverified, seen = [], [], set()
    for setting, record in _winners(resolution):
        target = destination(setting)
        common = {"setting": setting, "winner": record.get("winner"), "state": record["state"],
                  "scope": record.get("scope"), "clauses": list(record.get("clauses", []))}
        if target is None:
            unverified.append(dict(common, value=record["value"], status="unverified"))
            continue
        path, kind = target
        value = record["value"]
        if not _typed(kind, value):
            _fail("visual_type_mismatch", f"{setting} needs a {kind} value, not {p.canonical_json(value).decode()}",
                  "conflict")
        if path in seen:
            _fail("duplicate_destination", f"two settings target {_display(path)}", "conflict")
        seen.add(path)
        node = spec
        for part in path[:-1]:
            if part not in node:
                node[part] = {}
            elif not isinstance(node[part], dict):
                _fail("visual_destination_shape", f"existing {part} is not an object; refusing to replace it",
                      "conflict")
            node = node[part]
        present = path[-1] in node
        old = copy.deepcopy(node[path[-1]]) if present else None
        new = value.lower() if kind == "color" else value
        node[path[-1]] = new
        applied.append(dict(common, destination=_display(path), old=old, old_present=present, new=new,
                            status="applied"))
    context = {"schema_version": 1, "selection_digest": digest,
               "clauses": sorted(applied + unverified, key=lambda item: item["setting"]),
               "asset_refs": [ref for ref in p.asset_refs(resolution, phase=phase, domain=domain)
                              if ref["kind"] in ("tokens", "visual-legacy")]}
    spec["pattern_context"] = context
    missing = {item["setting"] for item in unverified}
    return {"schema_version": 1, "status": "ready", "spec": spec, "pattern_context": copy.deepcopy(context),
            "applied": applied, "unverified_settings": sorted(missing),
            "review_required": _review_required(resolution, missing), "limits": _LIMITS_NOTE}


def validate_visual(spec: Mapping[str, Any], resolution: Mapping[str, Any], *,
                    context: Optional[p.Context] = None, refs: Any = ()) -> dict:
    """Check each mapped destination against the resolution; report mismatches by clause.

    `resolution` is a verified lock, or an in-process report with its `context`/`refs`.
    `passed` means only that every mechanical setting matches and none is unverified. It is
    never a review clearance; `review_required` lists what ordinary review must assess. A winner
    whose own value has the wrong type is a failed check for its clause, never a crash (M1).
    """
    if not isinstance(spec, Mapping):
        _fail("invalid_spec", "the design spec must be a JSON object")
    resolution = _report(resolution, context, refs)
    attached = spec.get("pattern_context")
    diagnostics = []
    if resolution["status"] == "empty" and not resolution["selected"]:
        status = "empty"
        if attached is not None:
            status = "failed"
            diagnostics.append({"code": "stale_pattern_context", "severity": "error",
                                "message": "the spec carries a pattern_context but no patterns are selected"})
        return {"schema_version": 1, "status": status, "checks": [], "unverified_settings": [],
                "review_required": [], "diagnostics": diagnostics, "clearance": False, "limits": _LIMITS_NOTE}
    digest = _require_ready(resolution)
    if attached is None:
        diagnostics.append({"code": "pattern_context_missing", "severity": "warning",
                            "message": "no pattern_context; values are still checked but traceability is missing"})
    elif not isinstance(attached, Mapping) or attached.get("selection_digest") != digest:
        diagnostics.append({"code": "stale_pattern_context", "severity": "error",
                            "message": "pattern_context was projected for a different selection"})
    checks, unverified = [], set()
    for setting, record in _winners(resolution):
        target = destination(setting)
        if target is None:
            unverified.add(setting)
            continue
        path, kind = target
        node, present = spec, True
        for part in path:
            if isinstance(node, Mapping) and part in node:
                node = node[part]
            else:
                present = False
                break
        actual = node if present else None
        if not _typed(kind, record["value"]):
            reason = f"the winning value is not a {kind}; correct the pattern (conflict)"
        elif not present:
            reason = "missing"
        elif not _equal(kind, record["value"], actual):
            reason = "type or value differs"
        else:
            reason = ""
        checks.append({"setting": setting, "destination": _display(path), "winner": record.get("winner"),
                       "clauses": list(record.get("clauses", [])), "state": record["state"],
                       "expected": record["value"], "actual": actual, "present": present,
                       "status": "failed" if reason else "passed", "reason": reason})
    failed = any(item["status"] == "failed" for item in checks) or any(
        item["severity"] == "error" for item in diagnostics)
    status = "failed" if failed else ("incomplete" if unverified else "passed")
    return {"schema_version": 1, "status": status, "selection_digest": digest, "checks": checks,
            "unverified_settings": sorted(unverified), "review_required": _review_required(resolution, unverified),
            "diagnostics": diagnostics, "clearance": False, "limits": _LIMITS_NOTE}


# ---------------------------------------------------------------- pipeline design-spec attachment

def _mandatory_clauses(lock: Mapping[str, Any]) -> set:
    return {item["clause"] for item in lock["requirements"]
            if item["level"] == "must" and item["state"] in ("mandatory", "waived")}


def design_attachment(lock: Mapping[str, Any], lock_ref: str) -> dict:
    """The optional `pattern_context` for a pipeline design-spec.json (spec section 8)."""
    lock = p.parse_lock(copy.deepcopy(dict(lock)))
    p.validate_relative_path(lock_ref, "lock_ref")
    clause_ids = sorted(item["clause"] for item in lock["requirements"]
                        if item["state"] in ("mandatory", "default", "waived", "recommendation"))
    return {"schema_version": 1, "selection_digest": lock["selection_digest"], "lock_ref": lock_ref,
            "clause_ids": clause_ids}


def verify_design_attachment(roots: p.Roots, lock_root: Path, attachment: Any, context: p.Context, *,
                             today: Optional[_dt.date] = None, reader: Optional[p.Reader] = None) -> dict:
    """Verify a pipeline attachment: contained lock, same digest, full mandatory clauses, current pins.

    `lock_root` is the run's pattern-state directory inside the repository (for example
    `.claude/runtime/patterns/<run-id>/`, or the run directory itself when the run lives there);
    `lock_ref` is relative to it. Document outputs may live elsewhere; the lock never does (L3).
    An attachment is a reference, not proof. Any mismatch is `unavailable`; the lock is then
    checked with the core `verify_lock` against the current context and sources.
    """
    if not isinstance(attachment, Mapping) or set(attachment) != {"schema_version", "selection_digest",
                                                                 "lock_ref", "clause_ids"}:
        _fail("invalid_attachment", "pattern_context needs schema_version, selection_digest, lock_ref, clause_ids")
    if type(attachment["schema_version"]) is not int or attachment["schema_version"] != 1:
        _fail("invalid_attachment", "unsupported pattern_context schema_version")
    if roots.repository is None:
        _fail("repository_required", "an attached lock lives in the repository; supply its root")
    try:
        relative = Path(lock_root).resolve().relative_to(roots.repository.resolve()).as_posix()
    except ValueError:
        _fail("lock_outside_repository", "the attachment's lock root must be inside the repository "
                                         "(for example .claude/runtime/patterns/<run-id>/)")
    reader = reader or p.Reader()
    p.validate_relative_path(attachment["lock_ref"], "lock_ref")
    try:
        joined = attachment["lock_ref"] if relative == "." else f"{relative}/{attachment['lock_ref']}"
        path = p.contained_path(roots.repository, joined, "lock_ref")
        data = reader.read(path, kind="input", limit=p.LIMITS.catalog_bytes)
    except p.PatternError as error:
        if error.code == "unsafe_path":
            raise
        _fail("attachment_lock_missing", f"attached lock is unreadable: {error.message}", "unavailable")
    except OSError as error:
        _fail("attachment_lock_missing", f"attached lock is unreadable: {error.strerror}", "unavailable")
    lock = p.parse_lock(p.parse_json(data, limit=p.LIMITS.catalog_bytes, what="attached lock"))
    if attachment["selection_digest"] != lock["selection_digest"]:
        _fail("attachment_stale", "pattern_context selection_digest differs from its lock", "unavailable")
    clause_ids = attachment["clause_ids"]
    known = {item["clause"] for item in lock["requirements"]}
    if not isinstance(clause_ids, list) or len(set(clause_ids)) != len(clause_ids) or not set(clause_ids) <= known:
        _fail("attachment_clauses", "pattern_context clause_ids are duplicated or not in the lock", "unavailable")
    missing = sorted(_mandatory_clauses(lock) - set(clause_ids))
    if missing:
        _fail("attachment_clauses", f"pattern_context omits mandatory clauses: {', '.join(missing)}", "unavailable")
    verification = p.verify_lock(roots, lock, context, today=today, reader=reader)
    return {"schema_version": 1, "status": verification["status"], "selection_digest": lock["selection_digest"],
            "lock": lock, "verification": verification}
