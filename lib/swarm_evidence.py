#!/usr/bin/env python3
# component: swarm-shared-evidence-consumer
# implements: ADR-0027, ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P04.md
# constraints: accepted providers only; no profile creation, dispatch, alternate hashes or P08 import
# last_intent_review: 2026-09-22
"""Consume externally prepared shared evidence without turning local reports into clearance."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Optional

import context_safety as safety
import domain_result
from profile_context import ProfileConfig, ProfileError, required_policy, verify_profile_reference
from review_contract import ContractError, load_json, validate_context, verify_qa, verify_review

SOURCE = Path(__file__).resolve().parent.parent
MAX_RECORD_BYTES = 2 * 1024 * 1024


def _read(repo: Path, path: str) -> dict[str, Any]:
    data, _ = safety.read_owned(repo, path, MAX_RECORD_BYTES)
    return load_json(data.decode("utf-8-sig"))


def _bound_report(repo: Path, path: str, context: Mapping[str, Any]) -> None:
    _, state = safety.read_owned(repo, path, MAX_RECORD_BYTES)
    entry = next((entry for entry in context["snapshot"]["entries"] if entry["path"] == path), None)
    if entry is None or entry["worktree"]["kind"] != "file" or entry["worktree"]["sha256"] != state["sha256"]:
        raise ContractError("Shared context must bind the exact current local report/review bytes")


def _verify_profile(repo: Path, expected: Mapping[str, Any], config: ProfileConfig) -> None:
    if config.repo != repo or config.source != SOURCE:
        raise ContractError("Profile configuration must name this working repository and trusted source")
    if expected["profile"] is None:
        raise ContractError("Shared Swarm acceptance requires an explicit P07 reference, including neutral work")
    observed = verify_profile_reference(expected["profile"], config)
    if required_policy(observed) != expected["required_policy"]:
        raise ContractError("Live P07 required policy differs from the selected shared context")


def _latest_review(
    repo: Path, pointers: Mapping[str, Any], config: ProfileConfig,
) -> dict[str, Any]:
    command = [
        "bash", (SOURCE / "bin/li-review-read").as_posix(), "--skill", pointers["review_skill"],
        "--expected", (repo / pointers["context"]).as_posix(), "--gate-json",
    ]
    if pointers["corroboration"] is not None:
        command.extend(["--corroboration", (repo / pointers["corroboration"]).as_posix()])
    environment = {
        **os.environ, "LINTEL_SOURCE_ROOT": SOURCE.as_posix(), "LINTEL_REPO_ROOT": repo.as_posix(),
        "LINTEL_PYTHON": Path(sys.executable).as_posix(), "LINTEL_HOME": config.home.as_posix(),
        "LINTEL_PACKS_DIR": config.packs.as_posix(), "LINTEL_ACTIVE_PACK_FILE": config.pointer.as_posix(),
    }
    # Historical imports are a separate explicit operation, not a side effect of
    # an acceptance-capable status or resume read.
    environment.pop("GSTACK_HOME", None)
    observed = subprocess.run(command, cwd=repo, env=environment, capture_output=True,
                              text=True, encoding="utf-8", check=False)
    if observed.returncode not in (0, 3):
        raise ContractError("Shared latest-review reader failed: " + observed.stderr.strip())
    result = load_json(observed.stdout)
    if observed.returncode == 3 or result.get("ok") is not True:
        raise ContractError("Latest applicable shared review blocks: " + "; ".join(result.get("problems", [])))
    return result


def verify_shared_lane(
    repo: Path, coordination_path: str, contract: Mapping[str, Any], lane: Mapping[str, Any],
    package: Mapping[str, Any], report: Mapping[str, Any], local_review: Mapping[str, Any],
    *, profile_config: Optional[ProfileConfig],
) -> dict[str, Any]:
    outcome: dict[str, Any] = {
        "ok": False, "status": "unverified", "verification": "shared_evidence_pending",
        "release_clearance": False, "problems": [],
    }
    pointers = lane.get("shared_evidence")
    if not isinstance(pointers, dict):
        outcome["problems"].append("Local v1/v2 observations are not shared acceptance; explicit shared evidence is required")
        return outcome
    if profile_config is None:
        outcome["problems"].append("Explicit profile locations are required; verification never creates or rebinds a profile")
        return outcome
    root = safety.checked_root(repo)
    try:
        expected = _read(root, pointers["context"])
        validate_context(expected)
        work = expected["work"]
        if (
            work["work_map"] != contract["work_map"] or work["package_id"] != lane["task_id"]
            or work["leaf_ids"] != package["leaf_ids"] or expected["attempt_id"] != report["attempt_id"]
        ):
            raise ContractError("Shared work/package/leaf/attempt identity differs from the selected lane")
        if expected["builder"] != {"id": report["worker"], "context": report["actor_ref"]}:
            raise ContractError("Shared builder identity differs from the attributable local report")
        if not set(lane["write_scope"]) <= set(expected["snapshot"]["selection"]):
            raise ContractError("Shared snapshot must select every complete declared product scope")
        if expected["snapshot"]["record_path"] not in (None, pointers["review"]):
            raise ContractError("Shared snapshot may self-exclude only this lane's canonical review JSON")
        authority = {entry["path"] for entry in work["acceptance_manifest"]
                     if entry["start"] is None and entry["end"] is None}
        if not {coordination_path, contract["charter"], lane["brief"]} <= authority:
            raise ContractError("Shared acceptance must bind the complete coordination, charter and lane brief")
        purpose = "verification_only" if package["verification_only"] else "implementation"
        if expected["purpose"] != purpose:
            raise ContractError("Shared purpose differs from the authoritative package's result kind")
        if package["verification_only"] and any(
            entry["base"] != entry[state]
            for entry in expected["snapshot"]["entries"]
            if any(entry["path"] == scope or entry["path"].startswith(scope + "/") for scope in lane["write_scope"])
            for state in ("head", "index", "worktree")
        ):
            raise ContractError("Verification-only package has a changed selected product result")
        if package["review"] != "mechanical" and expected["independence_required"] is not True:
            raise ContractError("Substantive packages cannot disable independent shared review")
        _verify_profile(root, expected, profile_config)
        for path in (lane["report"], lane["review"]):
            _bound_report(root, path, expected)
        decision = _read(root, pointers["review"])
        if decision.get("skill") != pointers["review_skill"]:
            raise ContractError("Selected shared review skill differs from its declared pointer")
        if decision.get("reviewer") != {"id": local_review["reviewer"], "context": local_review["actor_ref"]}:
            raise ContractError("Shared reviewer identity differs from the attributable local review")
        corroboration = _read(root, pointers["corroboration"]) if pointers["corroboration"] else None
        checked = verify_review(root, decision, expected=expected, corroboration=corroboration)
        outcome["review"] = checked
        if not checked["ok"]:
            raise ContractError("Shared review blocks: " + "; ".join(checked["problems"]))
        outcome["latest_review"] = _latest_review(root, pointers, profile_config)
        qa = _read(root, pointers["qa"])
        observed_qa = verify_qa(root, qa, expected=expected)
        outcome["qa"] = observed_qa
        if observed_qa["blocked"]:
            raise ContractError("Shared QA blocks: " + "; ".join(observed_qa["blockers"]))
        if pointers["domain_request"] is not None:
            domain = domain_result.verify_result(
                root, pointers["domain_request"], expected=expected, profile_config=profile_config,
            )
            outcome["domain"] = domain
            if not domain["ok"]:
                raise ContractError("Domain observations block: " + "; ".join(domain["problems"]))
            if domain["qa"] != qa:
                raise ContractError("Selected QA must be the exact freshly verified domain QA, not another observation set")
        else:
            outcome["domain"] = {"verification": "not_requested", "release_clearance": False}
        _verify_profile(root, expected, profile_config)
        outcome.update(ok=True, status="pass", verification="current_shared_evidence")
    except (ValueError, OSError, UnicodeError) as error:
        outcome["status"] = "unverified"
        outcome["problems"].append(f"{error.code}: {error}" if isinstance(error, ProfileError) else str(error))
        if isinstance(error, ProfileError):
            outcome["profile_error"] = {"code": error.code, "required": error.required}
    return outcome
