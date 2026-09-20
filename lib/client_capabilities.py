# component: client-capabilities
# implements: ADR-0024, ADR-0025, ADR-0028
# intent: .claude/plans/universal-implementation/spec.md
# constraints: stdlib only; data selection is not execution, permission or independent review
# last_intent_review: 2026-09-20
"""One surface/evidence reader for installers, shell compatibility and session routing."""
from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlsplit

DEFAULT_REGISTRY = Path(__file__).with_name("cli-tiers.yaml")
OPERATION_IDS = frozenset((
    "question", "plan", "instructions", "skills", "read", "edit", "shell",
    "browser", "delegate", "isolate", "memory", "resume", "hooks",
    "plugin_control", "model_control",
))
FALLBACKS = frozenset((
    "conversation", "artifact-plan", "explicit-read", "blocked", "manual-evidence",
    "manual-handoff", "serial", "artifact-handoff", "unsupported",
))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_date(value: Any) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
    require(isinstance(value, dict), f"Expected JSON object: {path}")
    return value


def validate_registry(registry: dict) -> None:
    require(isinstance(registry, dict) and type(registry.get("schema_version")) is int
            and registry["schema_version"] == 2, "Unsupported client registry schema")
    operations, sources, surfaces = (registry.get(key) for key in ("operations", "sources", "surfaces"))
    require(isinstance(operations, dict) and set(operations) == OPERATION_IDS, "Incomplete operation contract")
    for name, operation in operations.items():
        require(isinstance(operation, dict) and nonempty(operation.get("intent"))
                and isinstance(operation.get("fallback"), str)
                and operation.get("fallback") in FALLBACKS, f"Malformed operation: {name}")
    require(isinstance(sources, dict) and bool(sources), "Missing official sources")
    for name, source in sources.items():
        require(isinstance(source, dict), f"Malformed source: {name}")
        url = source.get("url", "")
        require(isinstance(url, str) and urlsplit(url).scheme == "https" and bool(urlsplit(url).netloc),
                f"Invalid public source URL: {name}")
        require(valid_date(source.get("checked")) and nonempty(source.get("version"))
                and nonempty(source.get("conditions")), f"Missing dated source conditions: {name}")
    require(isinstance(surfaces, dict) and "other" in surfaces, "Missing surfaces/manual route")
    for name, record in surfaces.items():
        require(isinstance(name, str) and bool(re.fullmatch(r"[a-z][a-z0-9-]*", name))
                and isinstance(record, dict), f"Malformed surface: {name}")
        require(nonempty(record.get("label")) and nonempty(record.get("family"))
                and record.get("surface") in ("cli", "desktop", "ide", "cloud", "manual"),
                f"Surface must identify one CLI/desktop/IDE/cloud kind: {name}")
        discovery = record.get("discovery")
        require(isinstance(discovery, dict) and discovery.get("kind") in ("skills", "copilot", "manual"),
                f"Missing discovery route: {name}")
        if discovery["kind"] == "manual":
            require(discovery.get("root") is None and discovery.get("source") is None,
                    f"Manual discovery cannot claim a native root: {name}")
        else:
            require(isinstance(discovery.get("root"), str)
                    and bool(re.fullmatch(r"\.[a-z][a-z0-9-]*/skills", discovery["root"]))
                    and isinstance(discovery.get("source"), str)
                    and discovery["source"] in sources, f"Unsafe or unsourced discovery root: {name}")
            require(discovery["kind"] != "copilot" or discovery["root"] == ".github/skills",
                    f"Unexpected Copilot discovery root: {name}")
        require(isinstance(record.get("preserved"), list)
                and all(nonempty(path) for path in record["preserved"]), f"Malformed preserved routes: {name}")
        hook_adapter = record.get("hook_adapter")
        if hook_adapter is not None:
            require(isinstance(hook_adapter, dict) and hook_adapter.get("path") in record["preserved"]
                    and nonempty(hook_adapter.get("activation")), f"Malformed optional hook adapter: {name}")
        require(isinstance(record.get("sources", []), list)
                and all(isinstance(key, str) and key in sources for key in record.get("sources", [])), f"Unknown surface source: {name}")
        vendor = record.get("vendor")
        require(isinstance(vendor, dict) and set(vendor) <= OPERATION_IDS, f"Malformed vendor claims: {name}")
        for operation, claim in vendor.items():
            require(isinstance(claim, dict) and claim.get("status") in ("documented", "conditional", "unsupported")
                    and isinstance(claim.get("source"), str)
                    and claim["source"] in sources, f"Unsourced vendor claim: {name}.{operation}")
        observations = record.get("observations", {})
        require(isinstance(observations, dict) and set(observations) <= OPERATION_IDS,
                f"Malformed observations: {name}")
        for operation, observation in observations.items():
            require(isinstance(observation, dict)
                    and observation.get("status") in ("observed", "partial", "failed"),
                    f"Invalid observation status: {name}.{operation}")
            revision = observation.get("lintel_revision")
            require(nonempty(observation.get("scenario")) and valid_date(observation.get("checked"))
                    and (revision is None or (isinstance(revision, str)
                         and bool(re.fullmatch(r"[0-9a-f]{40}", revision))))
                    and nonempty(observation.get("evidence")), f"Unbound observation: {name}.{operation}")
            if observation["status"] == "observed":
                require(nonempty(observation.get("host_version")) and revision is not None,
                        f"Missing observed host version/revision: {name}")
            else:
                require(nonempty(observation.get("limitations")), f"Missing partial/failed observation limits: {name}")
    aliases = registry.get("aliases")
    require(isinstance(aliases, dict), "Missing compatibility aliases")
    for name, target in aliases.items():
        require(isinstance(target, str) and name not in surfaces and target in surfaces
                and name != target, f"Collapsed or invalid alias: {name}")


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict:
    registry = read_json(path)
    validate_registry(registry)
    return registry


def surface_id(registry: dict, name: str) -> str:
    canonical = registry["aliases"].get(name, name)
    require(canonical in registry["surfaces"], f"Unknown client surface: {name}; use other for an explicit manual route")
    return canonical


def describe(registry: dict, name: str) -> dict:
    canonical = surface_id(registry, name)
    record = deepcopy(registry["surfaces"][canonical])
    record["id"] = canonical
    record["operations"] = {}
    for operation, contract in registry["operations"].items():
        claim = record["vendor"].get(operation)
        source = deepcopy(registry["sources"][claim["source"]]) if claim else None
        vendor = {"status": claim["status"] if claim else "unknown",
                  "sources": [source] if source else [],
                  "conditions": source["conditions"] if source else "Not established for this surface."}
        delivered = {"kind": "operation-contract", "binding": "shims/universal/ADAPTER.md",
                     "fallback": contract["fallback"]}
        if operation == "skills":
            discovery = record["discovery"]
            delivered.update(kind="manual" if discovery["kind"] == "manual" else "native-files",
                             binding=discovery["root"] or ".github/lintel/START.md")
        elif operation in ("hooks", "plugin_control", "model_control"):
            delivered.update(kind="not-installed", binding=None)
            if operation == "hooks" and record.get("hook_adapter"):
                delivered.update(kind="optional-native-adapter", binding=record["hook_adapter"]["path"],
                                 conditions=record["hook_adapter"]["activation"])
        observed = deepcopy(record.get("observations", {}).get(operation, {
            "status": "not_run", "scenario": None, "host_version": None,
            "lintel_revision": None, "checked": None, "evidence": None,
        }))
        record["operations"][operation] = {
            "intent": contract["intent"], "vendor": vendor, "delivered": delivered, "observed": observed,
        }
    return record


def validate_session(registry: dict, session: dict) -> None:
    require(isinstance(session, dict) and type(session.get("schema_version")) is int
            and session["schema_version"] == 1, "Unsupported session binding schema")
    require(nonempty(session.get("session_id")), "Supply the actual stable session/work context ID; do not generate one per shell")
    require(isinstance(session.get("surface"), str), "Missing session surface")
    surface_id(registry, session["surface"])
    require(session.get("host_version") is None or nonempty(session["host_version"]), "Invalid host version")
    bindings = session.get("bindings")
    require(isinstance(bindings, dict) and set(bindings) <= OPERATION_IDS, "Unknown or malformed session operations")
    for operation, binding in bindings.items():
        require(isinstance(binding, dict) and nonempty(binding.get("tool"))
                and type(binding.get("available")) is bool
                and binding.get("permission") in ("allowed", "ask", "denied", "unknown"),
                f"Invalid tool binding: {operation}")
    isolation = session.get("isolation")
    require(isinstance(isolation, dict)
            and isolation.get("kind") in ("none", "git-worktree", "isolated-patch", "host-scoped-write")
            and type(isolation.get("attributable")) is bool, "Malformed isolation evidence")
    require(not isolation["attributable"] or (
        isolation["kind"] != "none" and nonempty(isolation.get("evidence"))), "Attributable isolation requires evidence")
    require(session.get("profile_ref") is None or isinstance(session["profile_ref"], dict),
            "profile_ref must be the effective-profile helper's object, not an invented string")
    require(session.get("work_map") is None or nonempty(session["work_map"]), "Invalid work-map reference")


def resolve(registry: dict, session: dict) -> dict:
    """Select operations from caller-inspected bindings; never invoke tools or grant access."""
    validate_session(registry, session)
    selected = {}
    for operation, contract in registry["operations"].items():
        binding = session["bindings"].get(operation)
        mode, tool = contract["fallback"], None
        reason = "No available tool binding; use the explicit fallback."
        if binding:
            if binding["permission"] == "denied":
                mode, reason = "blocked", "Host permission denied; no alternate channel bypass."
            elif binding["permission"] != "allowed":
                mode, reason = "approval-required", "Resolve the actual host permission before acting."
            elif binding["available"]:
                mode, tool, reason = "native", binding["tool"], "Available permitted binding; execution still belongs to the host."
        selected[operation] = {"mode": mode, "tool": tool, "reason": reason}
    isolation = session["isolation"]
    delegation = selected["delegate"]["mode"]
    if delegation == "native":
        execution = "native-isolated" if (selected["isolate"]["mode"] == "native"
                                         and isolation["attributable"]) else "serial"
    elif delegation in ("blocked", "approval-required"):
        execution = delegation
    else:
        execution = "manual-handoff"
    return {
        "schema_version": 1, "surface": surface_id(registry, session["surface"]),
        "session_id": session["session_id"], "host_version": session.get("host_version"),
        "work_map": session.get("work_map"), "profile_ref": deepcopy(session.get("profile_ref")),
        "operations": selected, "execution_mode": execution, "independent_review": "outstanding",
        "evidence_level": "declared-session-bindings", "executed": False,
    }


def compatibility_field(registry: dict, name: str, field: str) -> str:
    """Legacy hints describe delivered files, never a runtime dispatch authorization."""
    canonical = registry["aliases"].get(name, name)
    if canonical not in registry["surfaces"]:
        return {"id": "other", "label": name, "tier": "best-effort", "hooks_supported": "false",
                "skills_native": "false", "subagents": "none", "install": "explicit manual handoff"}.get(field, "")
    record = describe(registry, canonical)
    native_files = record["discovery"]["kind"] != "manual"
    values = {
        "id": canonical, "label": record["label"], "tier": "supported" if native_files else "best-effort",
        "hooks_supported": "true" if record["operations"]["hooks"]["delivered"]["kind"] == "optional-native-adapter" else "false",
        "skills_native": "true" if native_files else "false",
        "subagents": "sequenced" if record["operations"]["delegate"]["vendor"]["status"] in ("documented", "conditional") else "none",
        "install": f"python3 bin/li-adapter.py init --client {canonical} --target <repo>",
    }
    return values.get(field, "")


def markdown_table(registry: dict) -> str:
    lines = ["| Surface | Delivered discovery route | Vendor delegation | Live Lintel evidence |",
             "|---|---|---|---|"]
    for name in registry["surfaces"]:
        record = describe(registry, name)
        route = record["discovery"]["root"] or "manual canonical-file handoff"
        evidence = "partial session observations" if record.get("observations") else "not_run"
        delegation = record["operations"]["delegate"]["vendor"]["status"]
        lines.append(f"| {record['label']} | {route} | {delegation} | {evidence} |")
    return "\n".join(lines)
