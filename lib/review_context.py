# component: review-context
# implements: ADR-0040, ADR-0028, ADR-0029, ADR-0036
# intent: .claude/plans/adaptive-review/spec.md
# constraints: stdlib only; Python 3.9 core; never runs a model, network request or policy engine; never clears release
# last_intent_review: 2026-09-28
"""Evidenced review depth and an optional, lazy adapter over the reusable-patterns provider.

`assess_depth` translates six declared consequence facts into lean, standard or deep
review. Facts are declared observations, not authenticated truths: the asserting
actor/reference and every evidence reference stay attached to the result. Depth never
selects a model, consents to a multi-model panel or authorizes execution.

`prepare_pattern_review` imports only the trusted sibling `patterns.py` (Python 3.10+
per that provider's contract) and calls its own parse, verify, project and review
functions. A missing provider is unavailable, never an empty catalog. The provider
alone classifies mandatory/default/waived clauses, settings and exceptions; this adapter
passes them through verbatim. Nothing here is release clearance.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, Optional, Tuple

__all__ = (
    "SCHEMA_VERSION", "AXES", "DEPTHS", "REQUESTS", "QUESTION_TAGS", "PROVIDER_MIN_PYTHON",
    "ContextError", "DepthRefused", "read_context", "assess_depth", "render_assessment",
    "prepare_pattern_review",
)

LIB = Path(__file__).resolve().parent
SCHEMA_VERSION = 1
UNKNOWN = "unknown"
# Ordered: the order is part of the rendered context.
AXES: Dict[str, Tuple[Any, ...]] = {
    "deployment": ("local", "internal", "production", UNKNOWN),
    "exposure": ("isolated", "trusted", "untrusted", UNKNOWN),
    "impact": ("reversible", "sensitive", "irreversible", UNKNOWN),
    "behavior_change": (True, False, UNKNOWN),
    "security_boundary": (True, False, UNKNOWN),
    "blast_radius": ("contained", "shared", UNKNOWN),
}
BOOLEAN_AXES = frozenset({"behavior_change", "security_boundary"})
DEPTHS = ("lean", "standard", "deep")
REQUESTS = ("auto",) + DEPTHS
QUESTION_TAGS = ("deep-review", "production", "security-critical", "risk-unknown")
CONTEXT_KEYS = frozenset({"schema_version", "facts", "evidence", "asserted_by"})
ASSERTED_KEYS = frozenset({"actor", "reference"})
MAX_CONTEXT_BYTES = 64 * 1024
MAX_TEXT = 2000
_RANK = {name: index for index, name in enumerate(DEPTHS)}
# Each tuple is (fact, value, adds security-critical). Every one is a deep floor.
_DEEP_FLOORS = (
    ("deployment", "production", False),
    ("exposure", "untrusted", True),
    ("impact", "sensitive", True),
    ("impact", "irreversible", True),
    ("security_boundary", True, True),
    ("blast_radius", "shared", False),
)
_LEAN_ALLOWED = {
    "deployment": ("local", "internal"),
    "exposure": ("isolated", "trusted"),
    "impact": ("reversible",),
    "behavior_change": (False,),
    "security_boundary": (False,),
    "blast_radius": ("contained",),
}
_INDEPENDENCE = {"lean": "independent", "standard": "independent", "deep": "independent-staged"}
_AUTHORITY = {"selects_model": False, "mars_consent": False, "authorizes_execution": False}


class ContextError(ValueError):
    """Malformed consequence context or request; never treat it as a low-risk result."""


class DepthRefused(ContextError):
    """An explicit depth below the evidenced minimum; depth is never silently downgraded."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContextError(message)


def _text(value: Any, where: str) -> str:
    _require(isinstance(value, str) and bool(value.strip()), f"{where} must be a nonblank string")
    _require(len(value) <= MAX_TEXT, f"{where} exceeds {MAX_TEXT} characters")
    return value


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _no_constant(name: str):
    raise ContextError(f"non-finite JSON number refused: {name}")


def read_context(path: Path) -> Dict[str, Any]:
    """Strict, bounded JSON reader for a consequence-context file; validate with assess_depth."""
    with open(Path(path), "rb") as stream:
        data = stream.read(MAX_CONTEXT_BYTES + 1)
    _require(len(data) <= MAX_CONTEXT_BYTES, f"context file exceeds {MAX_CONTEXT_BYTES} bytes")
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs, parse_constant=_no_constant)
    except ContextError:
        raise
    except UnicodeDecodeError as error:
        raise ContextError(f"context file is not UTF-8: {error}") from error
    except json.JSONDecodeError as error:
        raise ContextError(f"context file is not valid JSON: {error}") from error
    except RecursionError as error:
        raise ContextError("context file JSON is nested too deeply") from error
    except ValueError as error:
        # Python 3.11+ refuses integer literals beyond sys.get_int_max_str_digits().
        raise ContextError(f"context file is not valid JSON: {error}") from error
    _require(isinstance(value, dict), "context must be a JSON object")
    return value


def _fact_value(axis: str, value: Any) -> Any:
    allowed = AXES[axis]
    if axis in BOOLEAN_AXES:
        # True == 1 in Python; only real booleans or the exact "unknown" string are facts.
        ok = type(value) is bool or (type(value) is str and value == UNKNOWN)
    else:
        ok = type(value) is str and value in allowed
    _require(ok, f"facts.{axis} must be one of {', '.join(_show(item) for item in allowed)}; got {value!r}")
    return value


def _show(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def _normalize(context: Mapping[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str], Dict[str, str]]:
    _require(isinstance(context, Mapping), "context must be a mapping or None")
    keys = set(context)
    _require(keys == CONTEXT_KEYS,
             f"context keys must be exactly {sorted(CONTEXT_KEYS)}; missing {sorted(CONTEXT_KEYS - keys)}, "
             f"unexpected {sorted(keys - CONTEXT_KEYS)}")
    version = context["schema_version"]
    _require(type(version) is int and version == SCHEMA_VERSION, f"schema_version must be the integer {SCHEMA_VERSION}")
    facts, evidence, asserted = context["facts"], context["evidence"], context["asserted_by"]
    _require(isinstance(facts, Mapping), "facts must be a mapping")
    _require(isinstance(evidence, Mapping), "evidence must be a mapping")
    _require(isinstance(asserted, Mapping), "asserted_by must be a mapping with actor and reference")
    unknown_axes = sorted(str(key) for key in facts if key not in AXES)
    _require(not unknown_axes, f"unknown fact axes: {', '.join(unknown_axes)}")
    stray = sorted(str(key) for key in evidence if key not in facts)
    _require(not stray, f"evidence for undeclared facts: {', '.join(stray)}")
    values: Dict[str, Any] = {}
    references: Dict[str, str] = {}
    for axis in AXES:
        value = _fact_value(axis, facts[axis]) if axis in facts else UNKNOWN
        values[axis] = value
        if axis in evidence:
            references[axis] = _text(evidence[axis], f"evidence.{axis}")
        elif _known(value):
            raise ContextError(f"known fact {axis}={_show(value)} needs a nonblank evidence reference")
    _require(set(asserted) == ASSERTED_KEYS, "asserted_by must contain exactly actor and reference")
    actor = {"actor": _text(asserted["actor"], "asserted_by.actor"),
             "reference": _text(asserted["reference"], "asserted_by.reference")}
    return values, references, actor


def _known(value: Any) -> bool:
    return type(value) is bool or value != UNKNOWN


def _digest(context: Mapping[str, Any]) -> str:
    material = {"schema_version": context["schema_version"], "facts": dict(context["facts"]),
                "evidence": dict(context["evidence"]), "asserted_by": dict(context["asserted_by"])}
    data = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def assess_depth(context: Optional[Mapping[str, Any]], requested: str = "auto") -> Dict[str, Any]:
    """Minimum and selected review depth from evidenced consequence facts.

    Raises ContextError for malformed input and DepthRefused for an explicit lower depth.
    """
    _require(type(requested) is str and requested in REQUESTS, f"requested depth must be one of {', '.join(REQUESTS)}")
    reasons: List[str] = []
    if context is None:
        values = {axis: UNKNOWN for axis in AXES}
        references: Dict[str, str] = {}
        asserted = None
        digest = None
        reasons.append("no consequence context was supplied: standard review with needs-context, never lean")
    else:
        values, references, asserted = _normalize(context)
        digest = _digest(context)
    unknown = [axis for axis in AXES if not _known(values[axis])]
    deep_hits = [(axis, value, security) for axis, value, security in _DEEP_FLOORS
                 if values[axis] is value or (type(value) is str and values[axis] == value)]
    for axis, value, _ in deep_hits:
        reasons.append(f"{axis}={_show(value)} requires deep review (evidence: {references[axis]})")
    if context is not None:
        for axis in unknown:
            reasons.append(f"{axis} is unknown: at least standard review with needs-context")
    blockers = [axis for axis in AXES if _known(values[axis]) and values[axis] not in _LEAN_ALLOWED[axis]]
    if deep_hits:
        minimum = "deep"
    elif unknown or blockers:
        minimum = "standard"
        for axis in blockers:
            reasons.append(f"{axis}={_show(values[axis])} rules out lean (evidence: {references[axis]})")
    else:
        minimum = "lean"
        reasons.append("all six facts are known, evidenced and low-consequence: lean is the minimum")
    if requested == "auto":
        selected = minimum
    elif _RANK[requested] < _RANK[minimum]:
        raise DepthRefused(f"explicit depth {requested} is below the evidenced minimum {minimum}; "
                           "an explicit lower depth is refused, never silently applied")
    else:
        selected = requested
        if selected != minimum:
            reasons.append(f"explicit request raises depth from {minimum} to {selected}")
    tags = []
    if selected == "deep":
        tags.append("deep-review")
    if values["deployment"] == "production":
        tags.append("production")
    if any(security for _, _, security in deep_hits):
        tags.append("security-critical")
    if unknown:
        tags.append("risk-unknown")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "needs-context" if unknown else "ok",
        "requested": requested,
        "minimum": minimum,
        "selected": selected,
        "reasons": reasons,
        "unknown_facts": unknown,
        "facts": dict(values),
        "source_evidence": [{"fact": axis, "value": values[axis], "reference": references[axis]}
                            for axis in AXES if axis in references],
        "asserted_by": asserted,
        "question_tags": tags,
        "recommended_independence": _INDEPENDENCE[selected],
        "context_sha256": digest,
        "authority": dict(_AUTHORITY),
        "release_clearance": False,
    }


def _cell(value: Any) -> str:
    return " ".join(_show(value).replace("|", "\\|").split())


def render_assessment(assessment: Mapping[str, Any]) -> str:
    """Deterministic Markdown for the packet body; any fact or provenance change changes it."""
    needed = {"status", "requested", "minimum", "selected", "reasons", "facts", "source_evidence",
              "asserted_by", "question_tags", "recommended_independence", "context_sha256", "release_clearance"}
    _require(isinstance(assessment, Mapping) and needed <= set(assessment), "not an assess_depth result")
    _require(assessment["release_clearance"] is False, "a review-depth assessment never carries release clearance")
    evidence = {item["fact"]: item["reference"] for item in assessment["source_evidence"]}
    asserted = assessment["asserted_by"]
    lines = [
        "## Review depth",
        "",
        f"- Requested: `{assessment['requested']}`; minimum: `{assessment['minimum']}`; "
        f"selected: `{assessment['selected']}`",
        f"- Status: `{assessment['status']}`",
        "- Asserted by: " + (f"{_cell(asserted['actor'])} ({_cell(asserted['reference'])})" if asserted
                             else "not supplied"),
        f"- Context SHA-256: `{assessment['context_sha256'] or 'none'}`",
        "",
        "| Fact | Value | Evidence |",
        "|---|---|---|",
    ]
    for axis in AXES:
        lines.append(f"| {axis} | {_cell(assessment['facts'][axis])} | {_cell(evidence.get(axis, '-'))} |")
    lines += ["", "Reasons:"] + [f"- {_cell(reason)}" for reason in assessment["reasons"]]
    tags = ", ".join(f"`{tag}`" for tag in assessment["question_tags"]) or "none"
    lines += [
        "",
        f"- Extra question tags: {tags}",
        f"- Recommended independence: `{assessment['recommended_independence']}`",
        "- Release clearance: false. Depth does not select a model, consent to a panel or authorize execution.",
        "- Facts are declared observations. Contest one with a finding; the affected result stops for reassessment.",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------- optional pattern adapter

PROVIDER_FILE = "patterns.py"
PROVIDER_MIN_PYTHON = (3, 10)
PROVIDER_API = ("Reader", "LIMITS", "PatternError", "parse_json", "parse_roots", "parse_context",
                "parse_attestations", "verify_lock", "project_package", "review_coverage")
_MODULE_NAME = "_lintel_review_context_patterns_provider"
_LIMITS = ("Supplemental context only. The provider's review_coverage result stays a supplemental ADR-0028 "
           "control; clause IDs are not standing questions and nothing here is a PASS or release clearance. "
           "Asset references are metadata only; read a selected document explicitly with the provider's read_asset.")
# Private in-process test seam only; there is no CLI or environment override.
_SEAM: Dict[str, Any] = {"double": None, "path": None}
_CACHE: Dict[str, Any] = {"path": None, "module": None}


@contextmanager
def _provider_double(double: Any) -> Iterator[None]:
    """Tests only: inject an in-process provider double (never a live acceptance)."""
    previous = _SEAM["double"]
    _SEAM["double"] = double
    try:
        yield
    finally:
        _SEAM["double"] = previous


@contextmanager
def _provider_path(path: Path) -> Iterator[None]:
    """Tests only: stand in for the sibling provider location."""
    previous = _SEAM["path"]
    _SEAM["path"] = Path(path)
    try:
        yield
    finally:
        _SEAM["path"] = previous


def _unavailable(code: str, message: str, source: Optional[str]) -> Tuple[None, Dict[str, Any]]:
    return None, {"available": False, "source": source, "code": code, "reason": message}


def _load_provider() -> Tuple[Any, Dict[str, Any]]:
    if _SEAM["double"] is not None:
        return _SEAM["double"], {"available": True, "source": "provider-double (test only)", "double": True}
    path = _SEAM["path"] or LIB / PROVIDER_FILE
    source = str(path)
    if tuple(sys.version_info[:2]) < tuple(PROVIDER_MIN_PYTHON):
        return _unavailable("provider_python_unsupported",
                            f"the patterns provider needs Python {PROVIDER_MIN_PYTHON[0]}.{PROVIDER_MIN_PYTHON[1]}+; "
                            f"this is {sys.version_info[0]}.{sys.version_info[1]}", source)
    if os.path.islink(path) or not path.is_file():
        return _unavailable("provider_missing", "the trusted sibling patterns provider is not installed", source)
    if _CACHE["path"] == path and _CACHE["module"] is not None:
        module = _CACHE["module"]
    else:
        spec = importlib.util.spec_from_file_location(_MODULE_NAME, path)
        if spec is None or spec.loader is None:
            return _unavailable("provider_load_failed", "the patterns provider cannot be loaded", source)
        module = importlib.util.module_from_spec(spec)
        # Dataclasses resolve their defining module through sys.modules while executing it.
        previous = sys.modules.get(_MODULE_NAME)
        sys.modules[_MODULE_NAME] = module
        try:
            spec.loader.exec_module(module)
        except Exception as error:  # a broken provider is unavailable, never an empty catalog
            if previous is None:
                sys.modules.pop(_MODULE_NAME, None)
            else:
                sys.modules[_MODULE_NAME] = previous
            return _unavailable("provider_load_failed", f"the patterns provider failed to load: {error}", source)
        _CACHE.update(path=path, module=module)
    missing = [name for name in PROVIDER_API if not hasattr(module, name)]
    if missing:
        return _unavailable("provider_incompatible", f"the patterns provider lacks {', '.join(missing)}", source)
    return module, {"available": True, "source": source}


def _input(provider: Any, reader: Any, path: Any, what: str, limit_name: str = "input_bytes") -> Any:
    limit = getattr(provider.LIMITS, limit_name)
    return provider.parse_json(reader.read(Path(os.fspath(path)), kind="input", limit=limit), limit=limit, what=what)


def _dedupe(diagnostics: List[Any]) -> List[Any]:
    """Drop only exact repeats; review_coverage re-reports its own verification diagnostics."""
    kept: List[Any] = []
    for item in diagnostics:
        if item not in kept:
            kept.append(copy.deepcopy(item))
    return kept


def prepare_pattern_review(*, roots: Path, lock: Path, context: Path, task_map: Path, package: str,
                           coverage: Optional[Path] = None, attestations: Optional[Path] = None) -> Dict[str, Any]:
    """Verify a pattern lock with the trusted provider, then project one package and optional coverage."""
    package = _text(package, "package")
    for name, value in (("roots", roots), ("lock", lock), ("context", context), ("task_map", task_map)):
        _require(value is not None and bool(os.fspath(value)), f"{name} file is required")
    provider, info = _load_provider()
    result: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "status": "unavailable", "provider": info, "package": package,
        "verification": None, "projection": None, "coverage": None, "coverage_supplied": coverage is not None,
        "exceptions": None, "asset_refs": None, "diagnostics": [], "metrics": None,
        "release_clearance": False, "limits": _LIMITS,
    }
    if provider is None:
        result["diagnostics"] = [{"code": info["code"], "severity": "error", "status": "unavailable",
                                  "message": info["reason"]}]
        return result
    reader = provider.Reader()
    try:
        roots_value = provider.parse_roots(_input(provider, reader, roots, "roots envelope"))
        context_value = provider.parse_context(_input(provider, reader, context, "context"))
        saved = provider.parse_attestations(_input(provider, reader, attestations, "attestations")) \
            if attestations is not None else ()
        lock_value = _input(provider, reader, lock, "lock", "catalog_bytes")
        verified = provider.verify_lock(roots_value, lock_value, context_value, reader=reader, attestations=saved)
        result["verification"] = copy.deepcopy(verified)
        if verified["status"] != "ok":
            result.update(status=verified["status"], diagnostics=copy.deepcopy(list(verified["diagnostics"])))
            return result
        projection = provider.project_package(lock_value, _input(provider, reader, task_map, "task map"), package)
        result["projection"] = copy.deepcopy(projection)
        status = projection["status"]
        diagnostics = list(verified["diagnostics"]) + list(projection["diagnostics"])
        if coverage is not None:
            report = provider.review_coverage(roots_value, lock_value, context_value,
                                              _input(provider, reader, coverage, "evidence"),
                                              attestations=saved, reader=reader)
            result["coverage"] = copy.deepcopy(report)
            status = report["status"]
            diagnostics += list(report["diagnostics"])
        result.update(status=status, diagnostics=_dedupe(diagnostics),
                      exceptions=copy.deepcopy(lock_value["exceptions"]),
                      asset_refs=copy.deepcopy(lock_value["asset_pins"]))
        return result
    except provider.PatternError as error:
        result.update(status=error.status, diagnostics=[error.diagnostic()])
        return result
    finally:
        result["metrics"] = reader.metrics()
