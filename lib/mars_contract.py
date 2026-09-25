# component: mars-contract
# implements: ADR-0034, ADR-0028, ADR-0026
# intent: .claude/plans/mars/spec.md
# constraints: stdlib only; data selection never dispatches models, grants permission or clears release
# last_intent_review: 2026-09-25
"""Roster, offer and panel-state rules for Multi-Model Adversarial Review & Screening (MARS)."""
from __future__ import annotations

import datetime
import hashlib
import importlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

DEFAULTS_PATH = Path(__file__).with_name("mars-defaults.json")
SCHEMA_PATH = Path(__file__).with_name("mars-schema.json")
PROTOCOL_REF = "skills/mars/references/protocol.md"
CANONICAL_ROUTE = ["SENSE", "SCOPE", "DEFINE", "DISCOVER", "PLAN", "BUILD", "REVIEW", "SHIP", "CAPTURE"]
PARTICIPANT_STATES = ("spawned", "reported", "failed", "closed")
COLLECTED = ("reported", "failed")
TRANSPORTS = ("subagent", "nested-session")
IDENTITY_LEVELS = ("host-usage", "host-receipt", "requested-only", "self-report")
ORIGIN_FIELDS = ("requested_by", "trigger", "caller", "coordinator_surface",
                 "repository", "branch", "commit", "cycle_id", "work_map")
SLOT = re.compile(r"^r[1-9][0-9]?$")
HEADER_KEY = re.compile(r"^[a-z][a-z0-9_]*$")


class ContractError(ValueError):
    """Invalid MARS data; callers must not dispatch or close anything."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> Dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=_unique)
    require(isinstance(value, dict), f"expected a JSON object: {path}")
    return value


def write_json(path: Path, value: Dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".mars-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=False)
            handle.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def load_defaults(path: Path = DEFAULTS_PATH) -> Dict[str, Any]:
    defaults = read_json(path)
    require(defaults.get("schema_version") == 1, "unsupported MARS defaults schema")
    return defaults


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ── Message headers (single schema: lib/mars-schema.json) ────────────────────

def load_schema(path: Path = SCHEMA_PATH) -> Dict[str, Any]:
    schema = read_json(path)
    require(schema.get("schema_version") == 1, "unsupported MARS header schema")
    return schema


def _header_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    text = "none" if value is None else str(value)
    require("\n" not in text and "\r" not in text and "```" not in text,
            "header values must be single-line and fence-free")
    return text


def render_header(kind: str, fields: Dict[str, Any], schema: Dict[str, Any]) -> str:
    """Render a validated header as a fenced ```mars-<kind> block in schema field order."""
    spec = schema["headers"][kind]
    validate_header(kind, {k: _header_value(v) for k, v in fields.items()}, schema)
    order = spec["required"] + [k for k in spec["optional"] if k in fields]
    lines = [f"{key}: {_header_value(fields[key])}" for key in order]
    return "```mars-" + kind + "\n" + "\n".join(lines) + "\n```\n"


def parse_header(text: str, kind: str) -> Dict[str, str]:
    """Parse the FIRST fenced mars-<kind> block. It must open the message."""
    body = text.lstrip("\ufeff").lstrip()
    opener = "```mars-" + kind
    require(body.startswith(opener + "\n") or body.startswith(opener + "\r\n"),
            f"message must begin with a ```mars-{kind} header block")
    end = body.find("\n```", len(opener))
    require(end != -1, f"unterminated mars-{kind} header block")
    fields: Dict[str, str] = {}
    for raw in body[len(opener):end].splitlines():
        line = raw.strip()
        if not line:
            continue
        key, sep, value = line.partition(":")
        key = key.strip()
        require(sep == ":" and HEADER_KEY.match(key) is not None, f"malformed header line: {line!r}")
        require(key not in fields, f"duplicate header key: {key}")
        fields[key] = value.strip()
    return fields


def validate_header(kind: str, fields: Dict[str, str], schema: Dict[str, Any]) -> Dict[str, str]:
    spec = schema["headers"].get(kind)
    require(spec is not None, f"unknown header kind: {kind}")
    missing = [key for key in spec["required"] if not fields.get(key)]
    require(not missing, f"mars-{kind} header missing: {', '.join(missing)}")
    unknown = set(fields) - set(spec["required"]) - set(spec["optional"])
    require(not unknown, f"mars-{kind} header has unknown keys: {', '.join(sorted(unknown))}")
    require(fields["mars"] == kind and fields["version"] == "1", f"not a mars-{kind} v1 header")
    for key, allowed in spec.get("enums", {}).items():
        if key in fields:
            require(fields[key] in allowed, f"{key} must be one of {allowed}")
    for key in spec.get("integers", []):
        require(re.fullmatch(r"\d+", fields.get(key, "")) is not None, f"{key} must be a non-negative integer")
    return fields


# ── Roster: latest model per family ──────────────────────────────────────────

def model_family(model_id: str) -> Optional[str]:
    head = model_id.split("-", 1)[0].lower()
    return head if head in ("claude", "gpt", "grok", "mai", "gemini") else None


def _version(model_id: str) -> Tuple[int, ...]:
    numbers = re.findall(r"\d+(?:\.\d+)*", model_id)
    return tuple(int(part) for part in numbers[0].split(".")) if numbers else (0,)


def _words(model_id: str) -> List[str]:
    return [word for word in re.split(r"[-.]", model_id.lower()) if word and not word.isdigit()]


def resolve_roster(available: List[str], defaults: Dict[str, Any],
                   families: Optional[List[str]] = None) -> Dict[str, Any]:
    """Pick the newest usable model per family from the host's actual list."""
    policy = defaults["roster"]
    wanted = families or policy["families"]
    chosen, missing = [], []
    for family in wanted:
        prefs = policy["family_preferences"].get(family, {})
        excluded = set(prefs.get("exclude_tiers", [])) | set(prefs.get("exclude_variants", []))
        candidates = [m for m in dict.fromkeys(available)
                      if model_family(m) == family and not excluded & set(_words(m))]
        if not candidates:
            missing.append(family)
            continue
        ordered = prefs.get("prefer_tiers") or prefs.get("prefer_variants") or []
        fallback = prefs.get("fallback_tiers", [])

        def rank(model: str) -> Tuple[int, Tuple[int, ...], int]:
            words = set(_words(model))
            preferred = [i for i, name in enumerate(ordered) if name in words]
            tier_hit = 2 if preferred else (1 if words & set(fallback) else 0)
            # Claude: tier outranks version ("prefer Opus"); others: version first.
            primary = tier_hit if prefs.get("prefer_tiers") else 0
            variant = -(preferred[0] if preferred else len(ordered))
            return primary, _version(model), variant

        chosen.append({"family": family, "model": max(candidates, key=rank)})
    distinct = len({entry["model"] for entry in chosen})
    return {"roster": chosen, "missing_families": missing,
            "eligible": distinct >= policy["min_participants"]}


def resolve_effort(requested: str, supported: List[str], defaults: Dict[str, Any]) -> Optional[str]:
    order = defaults["settings"]["effort_order"]
    require(requested in order, f"unknown effort: {requested}")
    usable = [effort for effort in order[: order.index(requested) + 1] if effort in supported]
    return usable[-1] if usable else None


def resolve_settings(host: Dict[str, Any], defaults: Dict[str, Any],
                     families: Optional[List[str]] = None) -> Dict[str, Any]:
    """Roster plus effective per-model effort/context from a host capability snapshot."""
    models = host.get("models")
    require(isinstance(models, dict) and models, "host snapshot needs a models object")
    roster = resolve_roster(list(models), defaults, families)
    requested_effort = defaults["settings"]["reasoning_effort"]
    requested_context = defaults["settings"]["context_tier"]
    for entry in roster["roster"]:
        caps = models[entry["model"]]
        entry["requested_effort"] = requested_effort
        entry["effort"] = resolve_effort(requested_effort, caps.get("efforts", []), defaults)
        entry["context_tier"] = requested_context if requested_context in caps.get("context_tiers", []) \
            else defaults["settings"]["context_fallback"]
        entry["downgraded"] = entry["effort"] != requested_effort or entry["context_tier"] != requested_context
    return roster


# ── Offer gate ──────────────────────────────────────────────────────────────

def offer_decision(request: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """Decide whether a caller may OFFER MARS. Never consent, never dispatch."""
    reasons = []
    caller = request.get("caller", "standalone")
    host = request.get("host", {})
    if request.get("is_participant"):
        reasons.append("participant-cannot-offer")
    if request.get("declined"):
        reasons.append("already-declined")
    if request.get("already_offered"):
        reasons.append("already-offered")
    if request.get("dry_run"):
        reasons.append("dry-run")
    for flag, reason in (("per_child_model", "no-per-child-model-selection"),
                         ("separate_contexts", "no-separate-contexts")):
        if host.get(flag) is not True:
            reasons.append(reason)
    if host.get("delegate_permission") != "allowed":
        reasons.append("delegation-not-allowed")
    if host.get("identity_evidence") not in ("host-usage", "host-receipt"):
        reasons.append("identity-unobservable")
    if len(set(host.get("models", []))) < defaults["roster"]["min_participants"]:
        reasons.append("fewer-than-two-models")
    route = request.get("route")
    if caller == "cycle" or route is not None:
        if [phase.upper() for phase in (route or [])] != CANONICAL_ROUTE:
            reasons.append("cycle-route-not-full")
        if request.get("checkpoint") != defaults["offers"]["cycle_checkpoint"]:
            reasons.append("not-cycle-checkpoint")
    elif not defaults["offers"]["standalone_review_offer"]:
        reasons.append("standalone-offers-disabled")
    return {"offer": not reasons, "reasons": reasons,
            "consent_required": True, "auto_mode_is_consent": False, "dispatch": False}


# ── Panel state ─────────────────────────────────────────────────────────────

def new_panel(panel_id: str, owner: str, brief: Path, consent_ref: str,
              defaults: Dict[str, Any], subject_kind: str = "review",
              origin: Optional[Dict[str, Any]] = None, subject_ref: Optional[str] = None) -> Dict[str, Any]:
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", panel_id) is not None, "invalid panel id")
    require(bool(owner.strip()), "owner session id required")
    require(bool(consent_ref.strip()), "consent reference required; an offer is not consent")
    origin = dict(origin or {})
    unknown = set(origin) - set(ORIGIN_FIELDS)
    require(not unknown, f"unknown origin fields: {', '.join(sorted(unknown))}")
    limits = {"max_participants": defaults["roster"]["max_participants"],
              "max_rounds": defaults["protocol"]["max_rounds"]}
    limits["max_calls"] = limits["max_participants"] * limits["max_rounds"]
    return {"schema_version": 1, "kind": "mars-panel", "panel_id": panel_id,
            "owner_session_id": owner, "created_at": now(), "status": "collecting",
            "origin": {key: origin.get(key) for key in ORIGIN_FIELDS},
            "subject": {"kind": subject_kind, "ref": subject_ref or Path(brief).as_posix(),
                        "brief_path": Path(brief).as_posix(), "brief_sha256": sha256_file(brief)},
            "limits": limits, "word_limit": defaults["protocol"]["report_word_limit"],
            "consent": {"reference": consent_ref, "roster": []},
            "participants": []}


def validate_panel(panel: Dict[str, Any]) -> None:
    require(panel.get("kind") == "mars-panel" and panel.get("schema_version") == 1, "not a MARS panel")
    seen_slots, seen_sessions = set(), set()
    parts = panel.get("participants", [])
    require(len(parts) <= panel["limits"]["max_participants"], "too many participants")
    calls = 0
    for part in parts:
        require(SLOT.match(part.get("slot", "")) is not None, f"invalid slot: {part.get('slot')}")
        require(part["slot"] not in seen_slots, f"duplicate slot: {part['slot']}")
        seen_slots.add(part["slot"])
        require(part.get("transport") in TRANSPORTS, f"invalid transport: {part.get('slot')}")
        require(part.get("state") in PARTICIPANT_STATES, f"invalid state: {part['slot']}")
        require(part.get("identity_evidence") in IDENTITY_LEVELS, f"invalid identity evidence: {part['slot']}")
        session = part.get("session_id")
        if session:
            require(session not in seen_sessions, f"session registered twice: {session}")
            require(session != panel["owner_session_id"], "the owner cannot be a participant")
            seen_sessions.add(session)
        rounds = [entry["round"] for entry in part.get("rounds", [])]
        require(rounds == sorted(set(rounds)), f"duplicate/unordered rounds: {part['slot']}")
        require(all(1 <= r <= panel["limits"]["max_rounds"] for r in rounds), f"round over limit: {part['slot']}")
        calls += len(rounds)
    require(calls <= panel["limits"]["max_calls"], "call budget exceeded")


def add_participant(panel: Dict[str, Any], slot: str, model: str, transport: str,
                    session_id: Optional[str], effort: Optional[str], context_tier: Optional[str]) -> None:
    require(panel["status"] == "collecting", "panel is not collecting")
    require(transport != "nested-session" or bool(session_id), "nested sessions need their session id")
    panel["participants"].append({
        "slot": slot, "requested_model": model, "transport": transport,
        "session_id": session_id, "spawned_by": panel["owner_session_id"], "spawned_at": now(),
        "requested_effort": effort, "requested_context_tier": context_tier,
        "state": "spawned", "observed_model": None, "identity_evidence": "requested-only",
        "rounds": [], "closed_at": None})
    panel["consent"]["roster"].append(model)
    validate_panel(panel)


def _participant(panel: Dict[str, Any], slot: str) -> Dict[str, Any]:
    for part in panel["participants"]:
        if part["slot"] == slot:
            return part
    raise ContractError(f"unknown slot: {slot}")


def _origin(panel: Dict[str, Any]) -> Dict[str, Any]:
    origin = panel.get("origin") or {}
    missing = [key for key in ("requested_by", "trigger", "caller", "coordinator_surface",
                               "repository", "branch", "commit") if not origin.get(key)]
    require(not missing, f"panel origin incomplete (set at init): {', '.join(missing)}")
    return origin


def build_request(panel: Dict[str, Any], slot: str, round_no: int, body: str,
                  schema: Dict[str, Any], lens: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """Header + body for one reviewer call. Round 2 is the challenge round."""
    part = _participant(panel, slot)
    require(part["state"] != "closed", "cannot brief a closed participant")
    require(1 <= round_no <= panel["limits"]["max_rounds"], "round over limit")
    if round_no > 1:
        require(any(r["round"] == round_no - 1 and r["status"] == "received" for r in part["rounds"]),
                "challenge needs this slot's received previous round")
    origin = _origin(panel)
    fields: Dict[str, Any] = {
        "mars": "request", "version": 1, "panel": panel["panel_id"], "slot": slot, "round": round_no,
        "round_type": "blind" if round_no == 1 else "challenge",
        "requested_by": origin["requested_by"], "trigger": origin["trigger"], "caller": origin["caller"],
        "consent_ref": panel["consent"]["reference"],
        "coordinator_session": panel["owner_session_id"], "coordinator_surface": origin["coordinator_surface"],
        "repository": origin["repository"], "branch": origin["branch"], "commit": origin["commit"],
        "subject_kind": panel["subject"]["kind"], "subject_ref": panel["subject"]["ref"],
        "brief_sha256": panel["subject"]["brief_sha256"],
        "requested_model": part["requested_model"],
        "reasoning_effort": part.get("requested_effort") or "host-default",
        "context_tier": part.get("requested_context_tier") or "host-default",
        "word_limit": panel.get("word_limit", 900), "reply_via": "final-response", "protocol": PROTOCOL_REF,
    }
    for key in ("cycle_id", "work_map"):
        if origin.get(key):
            fields[key] = origin[key]
    method = panel["subject"].get("method")
    if method:
        fields.update(stage=method["stage"], method=method["version"], questions=method["questions"] or "none")
        if method["tags"]:
            fields["tags"] = method["tags"]
    bound = panel["subject"].get("input")
    if bound:
        fields["snapshot_digest"] = bound["snapshot_digest"]
    if lens:
        fields["lens"] = lens
    header = render_header("request", fields, schema)
    return header + "\n" + body.strip() + "\n", fields


def record_round(panel: Dict[str, Any], slot: str, round_no: int, result: Path,
                 status: str = "received", brief_sha256: Optional[str] = None,
                 schema: Optional[Dict[str, Any]] = None, legacy: bool = False) -> None:
    """Record a report. v1 reports must open with a matching ```mars-report header."""
    require(status in ("received", "failed"), "round status must be received or failed")
    if brief_sha256 is not None:
        require(brief_sha256 == panel["subject"]["brief_sha256"], "report is bound to a different brief")
    part = _participant(panel, slot)
    require(part["state"] != "closed", "cannot record for a closed participant")
    if round_no > 1:
        require(any(r["round"] == round_no - 1 for r in part["rounds"]), "rounds must be sequential")
    entry: Dict[str, Any] = {"round": round_no, "status": status, "result_path": Path(result).as_posix(),
                             "sha256": sha256_file(result), "recorded_at": now(),
                             "header": "legacy" if legacy else "none"}
    if status == "received" and not legacy:
        require(schema is not None, "a header schema is required to record a received report")
        text = Path(result).read_text(encoding="utf-8-sig")
        fields = validate_header("report", parse_header(text, "report"), schema)
        for key, expected in (("panel", panel["panel_id"]), ("slot", slot), ("round", str(round_no)),
                              ("brief_sha256", panel["subject"]["brief_sha256"])):
            require(fields[key] == expected, f"report header {key}={fields[key]!r} does not match {expected!r}")
        entry.update(header="v1", verdict=fields["verdict"], confidence=int(fields["confidence"]),
                     counts={"p1": int(fields["p1"]), "p2": int(fields["p2"]), "p3": int(fields["p3"])},
                     self_reported_model=fields["self_reported_model"])
        method = panel["subject"].get("method")
        if method and fields.get("stage"):
            require(fields["stage"] == method["stage"], f"report stage {fields['stage']!r} differs from the packet")
        if method and round_no == 1:
            coverage = _lib_module("review_method").check_coverage(text, method["questions"])
            entry["coverage"] = {"complete": coverage["complete"], "incomplete": coverage["incomplete"]}
    part["rounds"].append(entry)
    part["state"] = "reported" if status == "received" else "failed"
    validate_panel(panel)


def observe_identity(panel: Dict[str, Any], slot: str, model: str, evidence: str) -> None:
    require(evidence in IDENTITY_LEVELS, f"unknown identity evidence: {evidence}")
    part = _participant(panel, slot)
    part["observed_model"] = model
    part["identity_evidence"] = evidence


def close_plan(panel: Dict[str, Any], owner: str, include_incomplete: bool = False) -> Dict[str, Any]:
    """List ONLY this owner's spawned, collected nested sessions. Never anything else."""
    validate_panel(panel)
    require(owner == panel["owner_session_id"], "caller does not own this panel; refusing to close anything")
    close, keep = [], []
    for part in panel["participants"]:
        eligible_state = part["state"] in COLLECTED or (include_incomplete and part["state"] == "spawned")
        if (part["transport"] == "nested-session" and part.get("session_id")
                and part.get("spawned_by") == owner and eligible_state):
            close.append({"slot": part["slot"], "session_id": part["session_id"]})
        else:
            keep.append({"slot": part["slot"], "state": part["state"], "transport": part["transport"]})
    return {"panel_id": panel["panel_id"], "close": close, "keep": keep}


def mark_closed(panel: Dict[str, Any], slot: str, owner: str) -> None:
    require(owner == panel["owner_session_id"], "caller does not own this panel")
    part = _participant(panel, slot)
    require(part["state"] in COLLECTED or part["state"] == "spawned", "participant already closed")
    part["state"], part["closed_at"] = "closed", now()
    if all(p["state"] == "closed" or p["transport"] == "subagent" for p in panel["participants"]):
        panel["status"] = "closed"


def summary(panel: Dict[str, Any]) -> Dict[str, Any]:
    validate_panel(panel)
    parts = panel["participants"]
    reported = [p for p in parts if any(r["status"] == "received" for r in p["rounds"])]
    observed = {p["observed_model"] for p in reported
                if p["identity_evidence"] in ("host-usage", "host-receipt") and p["observed_model"]}
    requested = {p["requested_model"] for p in reported}
    rounds_run = max((len(p["rounds"]) for p in parts), default=0)
    complete = bool(parts) and all(
        len(p["rounds"]) == rounds_run and all(r["status"] == "received" for r in p["rounds"]) for p in parts)
    result = {"panel_id": panel["panel_id"], "participants": len(parts), "reported": len(reported),
              "operational_status": "complete" if complete else "partial",
              "requested_distinct_models": len(requested), "verified_distinct_models": len(observed),
              "multi_model_verified": complete and len(observed) >= 2 and len(observed) == len(reported),
              "calls": sum(len(p["rounds"]) for p in parts), "release_clearance": False}
    if panel["subject"].get("method"):
        first = [r for p in parts for r in p["rounds"] if r["round"] == 1 and r["status"] == "received"]
        result["coverage_complete"] = bool(first) and all(r.get("coverage", {}).get("complete") for r in first)
    return result


def synthesis_header(panel: Dict[str, Any], schema: Dict[str, Any], defaults: Dict[str, Any],
                     adjudicated: Optional[Sequence[int]] = None,
                     verification: Optional[Dict[str, Any]] = None) -> str:
    """Header for the coordinator's synthesis report; the body is written by the coordinator.

    With adjudicated P1/P2/P3 counts, `outcome` uses the Review Method's single decision rule,
    so a panel and a single review reach the same result for the same findings.
    """
    facts = summary(panel)
    origin = _origin(panel)
    parts = panel["participants"]
    wanted = (defaults["settings"]["reasoning_effort"], defaults["settings"]["context_tier"])
    downgrades = [f"{p['slot']}:{p.get('requested_effort') or 'default'}/{p.get('requested_context_tier') or 'default'}"
                  for p in parts if (p.get("requested_effort"), p.get("requested_context_tier")) != wanted]
    failed = [p["slot"] for p in parts if p["state"] == "failed"
              or any(r["status"] == "failed" for r in p["rounds"])]
    fields: Dict[str, Any] = {
        "mars": "synthesis", "version": 1, "panel": panel["panel_id"], "status": facts["operational_status"],
        "requested_by": origin["requested_by"], "trigger": origin["trigger"], "caller": origin["caller"],
        "coordinator_session": panel["owner_session_id"], "repository": origin["repository"],
        "branch": origin["branch"], "commit": origin["commit"],
        "subject_kind": panel["subject"]["kind"], "subject_ref": panel["subject"]["ref"],
        "brief_sha256": panel["subject"]["brief_sha256"],
        "participants": facts["participants"], "reported": facts["reported"],
        "rounds": max((len(p["rounds"]) for p in parts), default=0), "calls": facts["calls"],
        "requested_models": [f"{p['slot']}={p['requested_model']}" for p in parts],
        "verified_models": [f"{p['slot']}={p['observed_model']}({p['identity_evidence']})" for p in parts
                            if p.get("observed_model")] or "none",
        "multi_model_verified": facts["multi_model_verified"], "release_clearance": False,
    }
    for key in ("cycle_id", "work_map"):
        if origin.get(key):
            fields[key] = origin[key]
    if downgrades:
        fields["downgrades"] = downgrades
    if failed:
        fields["failed_slots"] = failed
    method = panel["subject"].get("method")
    if method:
        fields.update(stage=method["stage"], questions=method["questions"] or "none",
                      coverage_complete=facts["coverage_complete"])
    bound = panel["subject"].get("input")
    if bound:
        fields["snapshot_digest"] = bound["snapshot_digest"]
        fields["input"] = (verification or {}).get("status", "unverified")
    profile = panel.get("profile")
    fields["profile"] = f"{profile['name']}@{profile['version']}#g{profile['generation']}" if profile else "none"
    if adjudicated is not None:
        require(len(adjudicated) == 3 and all(isinstance(n, int) and n >= 0 for n in adjudicated),
                "adjudicated counts are three non-negative integers: p1,p2,p3")
        complete = facts["operational_status"] == "complete" and facts.get("coverage_complete", True) \
            and fields.get("input", "verified") == "verified"
        fields["adjudicated"] = f"p1={adjudicated[0]} p2={adjudicated[1]} p3={adjudicated[2]}"
        fields["outcome"] = _lib_module("review_method").stage_outcome(adjudicated[0], adjudicated[1], complete)
    return render_header("synthesis", fields, schema)


# ── Content binding: method meta, input snapshot, profile reference, inspection ────────────

def _lib_module(name: str):
    """Load a sibling lib module lazily; a MARS run without binding needs none of them."""
    lib = str(Path(__file__).resolve().parent)
    if lib not in sys.path:
        sys.path.insert(0, lib)
    return importlib.import_module(name)


def attach_method(panel: Dict[str, Any], meta: Dict[str, Any]) -> None:
    """Link the frozen brief to the Review Method packet it was rendered from."""
    rm = _lib_module("review_method")
    try:
        rm.validate_meta(meta)
    except rm.MethodError as error:
        raise ContractError(str(error)) from error
    require(meta["brief_sha256"] == panel["subject"]["brief_sha256"], "method meta describes a different brief")
    require(meta["subject_kind"] == panel["subject"]["kind"], "method meta subject kind differs from --kind")
    panel["subject"]["method"] = {"version": meta["method_version"], "stage": meta["stage"],
                                  "questions": list(meta["questions"]), "tags": list(meta["tags"]),
                                  "acceptance": list(meta["acceptance"])}


def attach_profile(panel: Dict[str, Any], repo: Path, reference: Optional[Path] = None) -> None:
    """Record the selected profile reference (P07), or say explicitly that none is selected."""
    path = Path(reference) if reference else Path(repo) / ".claude" / "runtime" / "profiles" / "selected.json"
    if not path.is_file():
        require(reference is None, f"profile reference not found: {path}")
        panel["profile"], panel["profile_status"] = None, "none-selected"
        return
    profile_context = _lib_module("profile_context")
    try:
        panel["profile"] = profile_context.validate_profile_reference(read_json(path))
    except profile_context.ProfileError as error:
        raise ContractError(f"invalid profile reference: {error}") from error
    panel["profile_status"] = "selected"


def output_overlaps(repo: Path, selection: Sequence[str], outputs: Sequence[Path]) -> List[str]:
    """Mutable outputs inside (or containing) the selected input would invalidate the snapshot."""
    root = os.path.normcase(os.path.abspath(repo))
    hits = []
    for output in outputs:
        try:
            relative = os.path.relpath(os.path.normcase(os.path.abspath(output)), root)
        except ValueError:
            continue
        if relative == os.pardir or relative.startswith(os.pardir + os.sep):
            continue
        relative = "" if relative == "." else relative.replace(os.sep, "/")
        for item in selection:
            chosen = os.path.normcase(item).replace("\\", "/").strip("/")
            chosen = "" if chosen in ("", ".") else chosen
            if not chosen or not relative or relative == chosen or relative.startswith(chosen + "/") \
                    or chosen.startswith(relative + "/"):
                hits.append(f"{Path(output).as_posix()} overlaps selection {item!r}")
    return hits


def bind_input(panel: Dict[str, Any], repo: Path, base: str, selection: Sequence[str],
               snapshot_path: Path, outputs: Sequence[Path]) -> Dict[str, Any]:
    """Freeze the selected repository content with review_contract.snapshot before any dispatch."""
    require(bool(selection), "an explicit nonempty selection is required to bind input")
    hits = output_overlaps(repo, selection, [snapshot_path, *outputs])
    require(not hits, "output_overlaps_selection: " + "; ".join(hits)
            + ". Keep MARS records outside the selected input; the selection is not narrowed for you.")
    require(not Path(snapshot_path).exists(), f"input snapshot already exists (immutable): {snapshot_path}")
    review_contract = _lib_module("review_contract")
    try:
        snapshot = review_contract.snapshot(Path(repo), base=base, selection=list(selection))
    except review_contract.ContractError as error:
        raise ContractError(f"input snapshot refused: {error}") from error
    write_json(Path(snapshot_path), snapshot)
    panel["subject"]["input"] = {"repo": os.path.abspath(repo), "snapshot_path": Path(snapshot_path).as_posix(),
                                 "snapshot_digest": snapshot["result_digest"], "base": snapshot["base"],
                                 "head": snapshot["head"], "selection": snapshot["selection"]}
    return snapshot


def verify_input(panel: Dict[str, Any], repo: Optional[Path] = None) -> Dict[str, Any]:
    """Re-snapshot the bound selection. Any change means new observations under a new panel."""
    bound = panel["subject"].get("input")
    if not bound:
        return {"status": "unbound"}
    stored = read_json(Path(bound["snapshot_path"]))
    require(stored.get("result_digest") == bound["snapshot_digest"], "stored input snapshot was modified")
    review_contract = _lib_module("review_contract")
    try:
        current = review_contract.snapshot(Path(repo or bound["repo"]), base=stored["base"],
                                           selection=stored["selection"], record_path=stored["record_path"])
    except review_contract.ContractError as error:
        return {"status": "changed", "snapshot_digest": bound["snapshot_digest"], "reason": str(error),
                "changed_paths": []}
    before = {entry["path"]: entry for entry in stored["entries"]}
    after = {entry["path"]: entry for entry in current["entries"]}
    changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    same = current["result_digest"] == stored["result_digest"] and not changed
    result = {"status": "verified" if same else "changed", "snapshot_digest": bound["snapshot_digest"],
              "changed_paths": changed}
    if not same and not changed:
        result["reason"] = "HEAD or base resolution changed"
    return result


def inspection_record(panel: Dict[str, Any], synthesis_text: str, schema: Dict[str, Any],
                      verification: Dict[str, Any]) -> Dict[str, Any]:
    """Content-bound inspection evidence for REVIEW (purpose: inspection, never clearance)."""
    require(verification["status"] != "changed", "input_changed: collect observations again under a new panel")
    header = validate_header("synthesis", parse_header(synthesis_text, "synthesis"), schema)
    require(header["panel"] == panel["panel_id"] and header["brief_sha256"] == panel["subject"]["brief_sha256"],
            "synthesis belongs to another panel or brief")
    bound = panel["subject"].get("input")
    return {"schema_version": 1, "purpose": "inspection", "source": "mars", "release_clearance": False,
            "panel_id": panel["panel_id"],
            "subject": {key: panel["subject"].get(key) for key in ("kind", "ref", "brief_sha256", "method")},
            "input": verification["status"],
            "snapshot": read_json(Path(bound["snapshot_path"])) if bound else None,
            "profile": panel.get("profile"), "summary": summary(panel),
            "adjudicated": header.get("adjudicated"), "outcome": header.get("outcome"),
            "synthesis_sha256": hashlib.sha256(synthesis_text.encode("utf-8")).hexdigest(),
            "reports": [{"slot": p["slot"], "round": r["round"], "status": r["status"], "sha256": r["sha256"]}
                        for p in panel["participants"] for r in p["rounds"]]}
