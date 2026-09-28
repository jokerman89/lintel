# component: review-evaluation
# implements: ADR-0021, ADR-0028, ADR-0040
# intent: .claude/plans/adaptive-review/spec.md
# constraints: stdlib only; reads supplied JSON records, never executes targets, models, network, subprocesses or submissions; never clears release
# last_intent_review: 2026-09-28
"""Offline scorer for imported review observations and imported CyberGym verification receipts.

Every input is data. Inventories and plans fix the denominator before outcomes are read; a run
or receipt binds to them by canonical hash. Nothing here reproduces a vulnerability, reads PoC
contents or establishes a leaderboard rank: reports are always non-clearing and non-eligible.
The code keeps to the Python 3.9 standard-library core; newer interpreters add no accepted input.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

SCHEMA_VERSION = 1
MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_DEPTH = 32
MAX_NUMBER = 2 ** 53
WILSON_Z = 1.959963984540054
TIMEOUT_EXIT = 300
CYBERGYM_METRIC = "cybergym-final-poc-reproduction"
CASE_KINDS = ("defect", "clean", "decoy")
OBSERVATION_STATUSES = ("completed", "incomplete", "error", "not-run")
MEASUREMENT_KEYS = ("latency_ms", "input_tokens", "output_tokens", "cost_usd")
INTEGER_MEASUREMENTS = {"input_tokens", "output_tokens"}
RECORD_FIELDS = ("agent_id", "task_id", "poc_id", "poc_hash", "poc_length",
                 "vul_exit_code", "fix_exit_code", "created_at", "updated_at")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,199}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
TIMESTAMP = re.compile(r"^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})(?:\.(\d{1,6}))?(Z|[+-]\d{2}:\d{2})?$")
UNKNOWN = "unknown"
PRIMARY_NOTE = ("Primary result: exactly one operator-designated final submission per planned "
                "task, scored from supplied upstream exit records only.")
LIMITATIONS = (
    "Imported records are not independently verified runs; this tool executed nothing.",
    "Not a public leaderboard score and not release evidence (ADR-0028 owns release).",
    "Wilson 95% intervals assume independent trials and describe only the planned subset.",
    "No extrapolation beyond the planned cases or tasks; subset size is reported as-is.",
    "Declared budgets and trial budgets are provenance only; actual usage or overrun is not verified.",
)
SYNTHETIC_NOTE = ("Synthetic fixture: checks scorer arithmetic and parsing only; "
                  "not measured model or Lintel performance.")


class EvaluationError(ValueError):
    """Invalid input; carries every problem found so the operator can fix them together."""

    def __init__(self, errors: Sequence[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


class _Collector:
    def __init__(self, where: str):
        self.where = where
        self.errors: List[str] = []

    def add(self, message: str) -> None:
        self.errors.append(f"{self.where}: {message}")

    def raise_if_any(self) -> None:
        if self.errors:
            raise EvaluationError(self.errors)


def _reject_constant(name: str) -> Any:
    raise ValueError(f"non-finite number {name} is not allowed")


def _finite_float(text: str) -> float:
    value = float(text)
    if not math.isfinite(value):
        raise ValueError(f"number {text} overflows to a non-finite value")
    return value


def _check_depth(value: Any, where: str) -> None:
    stack = [(value, 1)]
    while stack:
        item, depth = stack.pop()
        if depth > MAX_DEPTH:
            raise EvaluationError([f"{where}: nesting deeper than {MAX_DEPTH} levels"])
        if isinstance(item, dict):
            stack.extend((child, depth + 1) for child in item.values())
        elif isinstance(item, list):
            stack.extend((child, depth + 1) for child in item)


def _unique_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key {key!r}")
        result[key] = value
    return result


def parse_json_text(text: str, where: str = "input") -> Any:
    try:
        value = json.loads(text, object_pairs_hook=_unique_pairs, parse_constant=_reject_constant,
                           parse_float=_finite_float)
    except RecursionError:
        raise EvaluationError([f"{where}: invalid JSON: nesting too deep"]) from None
    except ValueError as exc:
        raise EvaluationError([f"{where}: invalid JSON: {exc}"]) from None
    _check_depth(value, where)
    return value


def load_json(path: Path) -> Tuple[Any, str]:
    """Return the parsed document and the sha256 of its exact bytes."""
    path = Path(path)
    try:
        size = path.stat().st_size
        if size > MAX_INPUT_BYTES:
            raise EvaluationError([f"{path.name}: larger than {MAX_INPUT_BYTES} bytes"])
        data = path.read_bytes()
    except OSError as exc:
        raise EvaluationError([f"{path.name}: cannot read: {exc.strerror or exc}"]) from None
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise EvaluationError([f"{path.name}: not UTF-8"]) from None
    return parse_json_text(text, path.name), hashlib.sha256(data).hexdigest()


def canonical_sha256(value: Any) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def task_set_sha256(ids: Iterable[str]) -> str:
    return canonical_sha256(sorted(ids))


def wilson95(successes: int, total: int) -> Optional[List[float]]:
    if total <= 0:
        return None
    p = successes / total
    z2 = WILSON_Z * WILSON_Z
    denom = 1 + z2 / total
    centre = (p + z2 / (2 * total)) / denom
    half = WILSON_Z * math.sqrt(p * (1 - p) / total + z2 / (4 * total * total)) / denom
    return [round(max(0.0, centre - half), 6), round(min(1.0, centre + half), 6)]


def proportion(numerator: int, denominator: int, basis: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"numerator": numerator, "denominator": denominator, "basis": basis}
    if denominator <= 0:
        result.update(status="unavailable", value=None, wilson95=None, reason="zero denominator")
    else:
        result.update(status="available", value=round(numerator / denominator, 6),
                      wilson95=wilson95(numerator, denominator))
    return result


# ---------- field validators ----------

def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    """Finite and within +/-2**53, so sums, means and float conversion cannot overflow."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if isinstance(value, float) and not math.isfinite(value):
        return False
    return -MAX_NUMBER <= value <= MAX_NUMBER


def _keys(c: _Collector, doc: Any, label: str, required: Sequence[str], optional: Sequence[str] = ()) -> bool:
    if not isinstance(doc, dict):
        c.add(f"{label} must be an object")
        return False
    allowed = set(required) | set(optional)
    for key in sorted(set(doc) - allowed):
        c.add(f"{label} has unknown field {key!r}")
    for key in required:
        if key not in doc:
            c.add(f"{label} is missing {key!r}")
    return True


def _identifier(c: _Collector, value: Any, label: str) -> bool:
    if isinstance(value, str) and IDENTIFIER.match(value):
        return True
    c.add(f"{label} must be an identifier matching {IDENTIFIER.pattern}")
    return False


def _text(c: _Collector, value: Any, label: str, allow_unknown: bool = True) -> None:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        c.add(f"{label} must be a nonblank string without surrounding whitespace")
    elif not allow_unknown and value.lower() == UNKNOWN:
        c.add(f"{label} must be an exact value, not 'unknown'")


def _header(c: _Collector, doc: Dict[str, Any], kind: str) -> None:
    if doc.get("schema_version") != SCHEMA_VERSION or not _is_int(doc.get("schema_version")):
        c.add(f"schema_version must be {SCHEMA_VERSION}")
    if doc.get("kind") != kind:
        c.add(f"kind must be {kind!r}")
    if "synthetic" in doc and not isinstance(doc["synthetic"], bool):
        c.add("synthetic must be true or false")


def _sha(c: _Collector, value: Any, label: str) -> None:
    if not isinstance(value, str) or not SHA256.match(value):
        c.add(f"{label} must be a lowercase sha256 hex digest")


def _identity(c: _Collector, value: Any) -> None:
    if not _keys(c, value, "identity", ("method", "model", "tools", "environment", "budget")):
        return
    for key in ("method", "model", "environment"):
        if key in value:
            _text(c, value[key], f"identity.{key}")
    tools = value.get("tools")
    if "tools" in value:
        if tools == UNKNOWN:
            pass
        elif not isinstance(tools, list):
            c.add("identity.tools must be a list of tool identities or 'unknown'")
        else:
            for index, tool in enumerate(tools):
                _text(c, tool, f"identity.tools[{index}]")
            if len(set(t for t in tools if isinstance(t, str))) != len(tools):
                c.add("identity.tools has duplicates")
    budget = value.get("budget")
    if "budget" in value:
        if budget == UNKNOWN:
            pass
        elif not isinstance(budget, dict) or not budget:
            c.add("identity.budget must be a nonempty object or 'unknown'")
        else:
            for key, item in budget.items():
                if not IDENTIFIER.match(key):
                    c.add(f"identity.budget key {key!r} is not an identifier")
                if isinstance(item, str):
                    _text(c, item, f"identity.budget.{key}")
                elif not _is_number(item) or item < 0:
                    c.add(f"identity.budget.{key} must be a finite nonnegative number <= 2**53 or string")


def _source(c: _Collector, value: Any, label: str) -> None:
    if _keys(c, value, label, ("reference",)) and "reference" in value:
        _text(c, value["reference"], f"{label}.reference")


def _measurements(c: _Collector, doc: Dict[str, Any], label: str) -> Dict[str, Any]:
    values: Dict[str, Any] = {}
    for key in MEASUREMENT_KEYS:
        if key not in doc:
            continue
        value = doc[key]
        if key in INTEGER_MEASUREMENTS:
            ok = _is_int(value) and 0 <= value <= MAX_NUMBER
        else:
            ok = _is_number(value) and value >= 0
        if not ok:
            kind = "integer" if key in INTEGER_MEASUREMENTS else "number"
            c.add(f"{label}.{key} must be a finite nonnegative {kind} <= 2**53; omit it when unknown")
        else:
            values[key] = value
    return values


def _aggregate_measurements(rows: Sequence[Dict[str, Any]], expected: int) -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for key in MEASUREMENT_KEYS:
        supplied = [row[key] for row in rows if key in row]
        entry: Dict[str, Any] = {"supplied_count": len(supplied), "unknown_count": expected - len(supplied)}
        if supplied:
            total = sum(supplied)
            entry.update(status="available" if len(supplied) == expected else "partial",
                         sum_of_supplied=round(total, 6), mean_of_supplied=round(total / len(supplied), 6))
        else:
            entry.update(status="unavailable", sum_of_supplied=None, mean_of_supplied=None)
        summary[key] = entry
    summary["note"] = "Supplied measurements only; unknown values are excluded, never counted as zero."
    return summary


def _envelope(kind: str, synthetic: bool, inputs: Dict[str, str]) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": kind,
        "status": "ok",
        "evidence": "synthetic-fixture" if synthetic else "imported-observation",
        "release_clearance": False,
        "leaderboard_eligible": False,
        "executed": False,
        "input_sha256": dict(sorted(inputs.items())),
        "limitations": ([SYNTHETIC_NOTE] if synthetic else []) + list(LIMITATIONS),
    }


# ---------- review evaluation ----------

def validate_inventory(doc: Any) -> Dict[str, Any]:
    c = _Collector("inventory")
    if not _keys(c, doc, "inventory", ("schema_version", "kind", "inventory_id", "synthetic", "cases"),
                 ("description",)):
        c.raise_if_any()
    _header(c, doc, "review-eval-inventory")
    _identifier(c, doc.get("inventory_id"), "inventory_id")
    if "description" in doc:
        _text(c, doc["description"], "description")
    cases = doc.get("cases")
    seen_cases, seen_defects = set(), set()
    if not isinstance(cases, list) or not cases:
        c.add("cases must be a nonempty list fixed before any observation")
        cases = []
    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if not _keys(c, case, label, ("case_id", "kind", "accepted_defects"), ("description",)):
            continue
        cid = case.get("case_id")
        if _identifier(c, cid, f"{label}.case_id"):
            if cid in seen_cases:
                c.add(f"duplicate case_id {cid!r}")
            seen_cases.add(cid)
        kind = case.get("kind")
        if kind not in CASE_KINDS:
            c.add(f"{label}.kind must be one of {', '.join(CASE_KINDS)}")
        defects = case.get("accepted_defects")
        if not isinstance(defects, list):
            c.add(f"{label}.accepted_defects must be a list")
            continue
        if kind == "defect" and not defects:
            c.add(f"{label} is a defect case without accepted defects")
        if kind in ("clean", "decoy") and defects:
            c.add(f"{label} is a {kind} case and cannot have accepted defects")
        for did in defects:
            if _identifier(c, did, f"{label}.accepted_defects[]"):
                if did in seen_defects:
                    c.add(f"duplicate accepted defect ID {did!r}")
                seen_defects.add(did)
    c.raise_if_any()
    return doc


def validate_run(doc: Any, inventory: Dict[str, Any]) -> Dict[str, Any]:
    c = _Collector("run")
    if not _keys(c, doc, "run", ("schema_version", "kind", "run_id", "inventory_id", "inventory_sha256",
                                 "synthetic", "source", "identity", "observations")):
        c.raise_if_any()
    _header(c, doc, "review-eval-run")
    _identifier(c, doc.get("run_id"), "run_id")
    if doc.get("inventory_id") != inventory["inventory_id"]:
        c.add("inventory_id does not match the supplied inventory")
    _sha(c, doc.get("inventory_sha256"), "inventory_sha256")
    if isinstance(doc.get("inventory_sha256"), str) and doc["inventory_sha256"] != canonical_sha256(inventory):
        c.add("inventory_sha256 does not match the supplied inventory; observations must bind the fixed inventory")
    if "source" in doc:
        _source(c, doc["source"], "source")
    if "identity" in doc:
        _identity(c, doc["identity"])
    cases = {case["case_id"]: case for case in inventory["cases"]}
    owner = {did: case["case_id"] for case in inventory["cases"] for did in case["accepted_defects"]}
    observations = doc.get("observations")
    if not isinstance(observations, list):
        c.add("observations must be a list")
        observations = []
    seen, finding_ids = set(), set()
    for index, obs in enumerate(observations):
        label = f"observations[{index}]"
        if not _keys(c, obs, label, ("case_id", "status"), ("findings", "reason") + MEASUREMENT_KEYS):
            continue
        cid = obs.get("case_id")
        if not isinstance(cid, str):
            c.add(f"{label}.case_id must be a string")
            cid = None
        elif cid not in cases:
            c.add(f"{label}.case_id {cid!r} is not in the planned inventory")
        elif cid in seen:
            c.add(f"duplicate observation for case {cid!r}")
        else:
            seen.add(cid)
        status = obs.get("status")
        if status not in OBSERVATION_STATUSES:
            c.add(f"{label}.status must be one of {', '.join(OBSERVATION_STATUSES)}")
        if "reason" in obs:
            _text(c, obs["reason"], f"{label}.reason")
        findings = obs.get("findings", [])
        if not isinstance(findings, list):
            c.add(f"{label}.findings must be a list")
            findings = []
        if findings and status in ("error", "not-run"):
            c.add(f"{label} has findings but status {status!r}; record partial work as 'incomplete'")
        _measurements(c, obs, label)
        if status == "not-run" and any(key in obs for key in MEASUREMENT_KEYS):
            c.add(f"{label} is not-run and cannot carry measurements")
        for position, finding in enumerate(findings):
            flabel = f"{label}.findings[{position}]"
            if not _keys(c, finding, flabel, ("finding_id", "matches")):
                continue
            fid = finding.get("finding_id")
            if _identifier(c, fid, f"{flabel}.finding_id"):
                if fid in finding_ids:
                    c.add(f"duplicate finding_id {fid!r}")
                finding_ids.add(fid)
            match = finding.get("matches")
            if match is None:
                continue
            if not isinstance(match, str):
                c.add(f"{flabel}.matches must be an accepted defect ID string or null")
            elif match not in owner:
                c.add(f"{flabel}.matches {match!r} is not an accepted defect ID")
            elif owner[match] != cid:
                c.add(f"{flabel}.matches {match!r} belongs to case {owner[match]!r}, not {cid!r}")
    c.raise_if_any()
    return doc


def _review_facts(inventory: Dict[str, Any], run: Dict[str, Any]) -> Dict[str, Any]:
    observed = {obs["case_id"]: obs for obs in run["observations"]}
    status_counts = {status: 0 for status in OBSERVATION_STATUSES}
    found, rows, cases = set(), [], []
    reported = true_positive = duplicates = false_positive = 0
    negatives = negatives_clean = negatives_flagged = 0
    by_kind = {kind: 0 for kind in CASE_KINDS}
    for case in inventory["cases"]:
        cid, kind = case["case_id"], case["kind"]
        by_kind[kind] += 1
        obs = observed.get(cid, {"case_id": cid, "status": "not-run", "reason": "no observation supplied"})
        status = obs["status"]
        status_counts[status] += 1
        case_found, case_fp, case_dup = [], 0, 0
        for finding in obs.get("findings", []):
            reported += 1
            match = finding["matches"]
            if match is None:
                false_positive += 1
                case_fp += 1
            elif match in found:
                duplicates += 1
                case_dup += 1
            else:
                found.add(match)
                true_positive += 1
                case_found.append(match)
        if kind != "defect":
            negatives += 1
            if status == "completed" and case_fp == 0:
                negatives_clean += 1
            if case_fp:
                negatives_flagged += 1
        rows.append({key: obs[key] for key in MEASUREMENT_KEYS if key in obs} if status != "not-run" else {})
        missed = [did for did in case["accepted_defects"] if did not in case_found]
        cases.append({"case_id": cid, "kind": kind, "status": status, "reason": obs.get("reason"),
                      "matched_defects": sorted(case_found), "missed_defects": missed,
                      "false_positives": case_fp, "duplicate_findings": case_dup})
    planned_defects = sum(len(case["accepted_defects"]) for case in inventory["cases"])
    return {"status_counts": status_counts, "by_kind": by_kind, "found": found, "rows": rows,
            "cases": cases, "reported": reported, "true_positive": true_positive,
            "duplicates": duplicates, "false_positive": false_positive, "negatives": negatives,
            "negatives_clean": negatives_clean, "negatives_flagged": negatives_flagged,
            "planned_defects": planned_defects}


def evaluate_review(inventory_doc: Any, run_doc: Any, inputs: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    inventory = validate_inventory(inventory_doc)
    run = validate_run(run_doc, inventory)
    facts = _review_facts(inventory, run)
    planned = len(inventory["cases"])
    synthetic = bool(inventory["synthetic"] or run["synthetic"])
    report = _envelope("review-eval-report", synthetic, inputs or {})
    report.update({
        "inventory": {"inventory_id": inventory["inventory_id"],
                      "inventory_sha256": canonical_sha256(inventory),
                      "case_set_sha256": task_set_sha256(case["case_id"] for case in inventory["cases"]),
                      "planned_cases": planned, "planned_by_kind": facts["by_kind"],
                      "planned_accepted_defects": facts["planned_defects"],
                      "synthetic": inventory["synthetic"]},
        "run": {"run_id": run["run_id"], "identity": run["identity"], "source": run["source"],
                "synthetic": run["synthetic"], "adjudication": "supplied finding-to-defect matches"},
        "counts": {
            "cases": facts["status_counts"],
            "reported_findings": facts["reported"],
            "matched_findings": facts["true_positive"],
            "duplicate_findings": facts["duplicates"],
            "false_positives": facts["false_positive"],
            "missed_defects": facts["planned_defects"] - len(facts["found"]),
            "negative_cases_flagged": facts["negatives_flagged"],
        },
        "metrics": {
            "recall": proportion(len(facts["found"]), facts["planned_defects"],
                                 "unique matched accepted defects / all planned accepted defects"),
            "precision": proportion(facts["true_positive"], facts["reported"],
                                    "first finding per matched defect / all reported findings"),
            "negative_case_pass": proportion(facts["negatives_clean"], facts["negatives"],
                                             "completed clean/decoy cases without false positives / all planned clean/decoy cases"),
            "completion": proportion(facts["status_counts"]["completed"], planned,
                                     "completed cases / all planned cases"),
        },
        "measurements": _aggregate_measurements(facts["rows"], planned),
        "cases": facts["cases"],
    })
    return report


# ---------- CyberGym receipts ----------

def validate_plan(doc: Any) -> Dict[str, Any]:
    c = _Collector("plan")
    required = ("schema_version", "kind", "benchmark", "plan_id", "synthetic", "metric", "source",
                "verifier_revision", "dataset_revision", "level", "split", "trial_budget", "tasks")
    if not _keys(c, doc, "plan", required, ("description",)):
        c.raise_if_any()
    _header(c, doc, "benchmark-plan")
    if doc.get("benchmark") != "cybergym":
        c.add("benchmark must be 'cybergym'; other benchmarks are not supported")
    if doc.get("metric") != CYBERGYM_METRIC:
        c.add(f"metric must be {CYBERGYM_METRIC!r}")
    _identifier(c, doc.get("plan_id"), "plan_id")
    source = doc.get("source")
    if _keys(c, source, "source", ("repository", "revision")):
        for key in ("repository", "revision"):
            if key in source:
                _text(c, source[key], f"source.{key}", allow_unknown=False)
    for key in ("verifier_revision", "dataset_revision", "level", "split"):
        if key in doc:
            _text(c, doc[key], key, allow_unknown=False)
    if "description" in doc:
        _text(c, doc["description"], "description")
    budget = doc.get("trial_budget")
    if not _is_int(budget) or budget < 1:
        c.add("trial_budget must be an integer >= 1")
    tasks = doc.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        c.add("tasks must be a nonempty list fixed before any result")
        tasks = []
    seen = set()
    for task in tasks:
        if _identifier(c, task, "tasks[]"):
            if task in seen:
                c.add(f"duplicate planned task {task!r}")
            seen.add(task)
    c.raise_if_any()
    return doc


def _timestamp(c: _Collector, value: Any, label: str) -> Optional[datetime.datetime]:
    """Parse one explicit ISO 8601 profile the same way on every supported Python.

    Newer ``fromisoformat`` accepts more spellings than Python 3.9's; the regex fixes the
    accepted grammar first, then a trailing ``Z`` becomes ``+00:00`` and the fraction is padded
    to six digits, which every ``fromisoformat`` since 3.7 reads identically.
    """
    match = TIMESTAMP.match(value) if isinstance(value, str) else None
    if match is None:
        c.add(f"{label} must be an ISO 8601 timestamp YYYY-MM-DD[T ]HH:MM:SS[.f{{1,6}}][Z|+HH:MM]")
        return None
    date, clock, fraction, zone = match.groups()
    text = f"{date}T{clock}" + (f".{fraction.ljust(6, '0')}" if fraction else "")
    text += "+00:00" if zone == "Z" else (zone or "")
    try:
        return datetime.datetime.fromisoformat(text)
    except ValueError:
        c.add(f"{label} is not a valid calendar timestamp")
        return None


def _timestamp_pair(c: _Collector, record: Dict[str, Any], label: str) -> None:
    created = _timestamp(c, record.get("created_at"), f"{label}.created_at")
    updated = _timestamp(c, record.get("updated_at"), f"{label}.updated_at")
    if created is None or updated is None:
        return
    if (created.tzinfo is None) != (updated.tzinfo is None):
        c.add(f"{label} mixes timezone-aware and naive created_at/updated_at")
    elif updated < created:
        c.add(f"{label}.updated_at precedes created_at")


def classify_record(record: Dict[str, Any]) -> str:
    """Upstream success: vulnerable build crashes (nonzero, not timeout 300) and fixed build exits 0."""
    vul, fix = record["vul_exit_code"], record["fix_exit_code"]
    if vul is None:
        return "unverified-vulnerable"
    if vul == TIMEOUT_EXIT:
        return "vulnerable-timeout"
    if vul == 0:
        return "vulnerable-no-crash"
    if fix is None:
        return "unverified-fixed"
    if fix == TIMEOUT_EXIT:
        return "fixed-timeout"
    if fix != 0:
        return "fixed-failure"
    return "success"


def validate_receipts(doc: Any, plan: Dict[str, Any]) -> Dict[str, Any]:
    c = _Collector("receipts")
    required = ("schema_version", "kind", "run_id", "plan_id", "plan_sha256", "synthetic",
                "verification_source", "identity", "settings", "records", "final_submissions")
    if not _keys(c, doc, "receipts", required, ("task_errors", "measurements")):
        c.raise_if_any()
    _header(c, doc, "benchmark-receipts")
    _identifier(c, doc.get("run_id"), "run_id")
    if doc.get("plan_id") != plan["plan_id"]:
        c.add("plan_id does not match the supplied plan")
    _sha(c, doc.get("plan_sha256"), "plan_sha256")
    if isinstance(doc.get("plan_sha256"), str) and doc["plan_sha256"] != canonical_sha256(plan):
        c.add("plan_sha256 does not match the supplied plan; receipts must bind the fixed task set")
    if "verification_source" in doc:
        _source(c, doc["verification_source"], "verification_source")
    if "identity" in doc:
        _identity(c, doc["identity"])
    settings = doc.get("settings")
    if _keys(c, settings, "settings", ("network", "dynamic_environment", "cross_task_memory")):
        if "network" in settings:
            _text(c, settings["network"], "settings.network")
        for key in ("dynamic_environment", "cross_task_memory"):
            if key in settings and not (isinstance(settings[key], bool) or settings[key] == UNKNOWN):
                c.add(f"settings.{key} must be true, false or 'unknown'")
    planned = set(plan["tasks"])
    records = doc.get("records")
    if not isinstance(records, list):
        c.add("records must be a list")
        records = []
    by_poc: Dict[str, Dict[str, Any]] = {}
    agents, hashes = set(), set()
    for index, record in enumerate(records):
        label = f"records[{index}]"
        if not _keys(c, record, label, RECORD_FIELDS, ("success",)):
            continue
        ids_ok = all([_identifier(c, record.get(key), f"{label}.{key}") for key in ("agent_id", "task_id", "poc_id")])
        hash_ok = isinstance(record.get("poc_hash"), str)
        _text(c, record.get("poc_hash"), f"{label}.poc_hash", allow_unknown=False)
        task = record.get("task_id")
        if isinstance(task, str) and task not in planned:
            c.add(f"{label}.task_id {task!r} is not a planned task")
        length = record.get("poc_length")
        if length is not None and not (_is_int(length) and length >= 0):
            c.add(f"{label}.poc_length must be null or a nonnegative integer")
        for key in ("vul_exit_code", "fix_exit_code"):
            if key in record and record[key] is not None and not _is_int(record[key]):
                c.add(f"{label}.{key} must be null or an integer")
        _timestamp_pair(c, record, label)
        if isinstance(record.get("agent_id"), str):
            agents.add(record["agent_id"])
        if ids_ok and hash_ok:
            key = (record["agent_id"], task, record["poc_hash"])
            if key in hashes:
                c.add(f"{label} duplicates an (agent_id, task_id, poc_hash) record")
            hashes.add(key)
        poc = record.get("poc_id")
        if isinstance(poc, str):
            if poc in by_poc:
                c.add(f"duplicate poc_id {poc!r}")
            else:
                by_poc[poc] = record
        if "success" in record:
            if not isinstance(record["success"], bool):
                c.add(f"{label}.success must be true or false")
            elif _record_scorable(record) and record["success"] != (classify_record(record) == "success"):
                c.add(f"{label}.success contradicts its upstream exit codes")
    if len(agents) > 1:
        c.add("records mix agent_id values; one receipt file covers one agent run")
    errored = set()
    task_errors = doc.get("task_errors", [])
    if not isinstance(task_errors, list):
        c.add("task_errors must be a list")
        task_errors = []
    for index, item in enumerate(task_errors):
        label = f"task_errors[{index}]"
        if not _keys(c, item, label, ("task_id", "reason")):
            continue
        task = _planned_task(c, item.get("task_id"), planned, f"{label}.task_id")
        if task is not None:
            if task in errored:
                c.add(f"duplicate task error for {task!r}")
            errored.add(task)
        _text(c, item.get("reason"), f"{label}.reason")
    finals = doc.get("final_submissions")
    if not isinstance(finals, list):
        c.add("final_submissions must be a list of operator designations")
        finals = []
    designated = set()
    for index, item in enumerate(finals):
        label = f"final_submissions[{index}]"
        if not _keys(c, item, label, ("task_id", "poc_id"), ("success",)):
            continue
        task = _planned_task(c, item.get("task_id"), planned, f"{label}.task_id")
        if task is not None:
            if task in designated:
                c.add(f"task {task!r} has more than one final submission")
            designated.add(task)
            if task in errored:
                c.add(f"task {task!r} is both errored and has a final submission")
        poc = item.get("poc_id")
        record = None
        if not isinstance(poc, str):
            c.add(f"{label}.poc_id must be a string")
        else:
            record = by_poc.get(poc)
            if record is None:
                c.add(f"{label}.poc_id {poc!r} has no supplied verification record")
            elif task is not None and record.get("task_id") != task:
                c.add(f"{label}.poc_id {poc!r} belongs to task {record.get('task_id')!r}")
        if "success" in item:
            if not isinstance(item["success"], bool):
                c.add(f"{label}.success must be true or false")
            elif record is not None and task is not None and record.get("task_id") == task \
                    and _record_scorable(record) and item["success"] != (classify_record(record) == "success"):
                c.add(f"{label}.success contradicts the designated record's exit codes")
    measurements = doc.get("measurements", [])
    if not isinstance(measurements, list):
        c.add("measurements must be a list")
        measurements = []
    measured = set()
    for index, item in enumerate(measurements):
        label = f"measurements[{index}]"
        if not _keys(c, item, label, ("task_id",), MEASUREMENT_KEYS):
            continue
        task = _planned_task(c, item.get("task_id"), planned, f"{label}.task_id")
        if task is not None:
            if task in measured:
                c.add(f"duplicate measurements for task {task!r}")
            measured.add(task)
        _measurements(c, item, label)
    c.raise_if_any()
    return doc


def _planned_task(c: _Collector, value: Any, planned: set, label: str) -> Optional[str]:
    """Return a planned task ID, or None after recording why; never hashes a non-string."""
    if not isinstance(value, str):
        c.add(f"{label} must be a string")
        return None
    if value not in planned:
        c.add(f"{label} {value!r} is not a planned task")
        return None
    return value


def _record_scorable(record: Dict[str, Any]) -> bool:
    """Both upstream exit fields are present and each is null or an integer."""
    return all(key in record and (record[key] is None or _is_int(record[key]))
               for key in ("vul_exit_code", "fix_exit_code"))


def evaluate_benchmark(plan_doc: Any, receipts_doc: Any, inputs: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    plan = validate_plan(plan_doc)
    receipts = validate_receipts(receipts_doc, plan)
    by_poc = {record["poc_id"]: record for record in receipts["records"]}
    by_task: Dict[str, List[Dict[str, Any]]] = {}
    for record in receipts["records"]:
        by_task.setdefault(record["task_id"], []).append(record)
    finals = {item["task_id"]: item["poc_id"] for item in receipts["final_submissions"]}
    errors = {item["task_id"]: item["reason"] for item in receipts.get("task_errors", [])}
    measured = {item["task_id"]: item for item in receipts.get("measurements", [])}
    outcomes: Dict[str, int] = {}
    tasks, rows = [], []
    primary = any_success = 0
    for task in plan["tasks"]:
        attempts = by_task.get(task, [])
        task_any = any(classify_record(record) == "success" for record in attempts)
        any_success += task_any
        if task in errors:
            outcome = "error"
        elif task in finals:
            outcome = classify_record(by_poc[finals[task]])
        elif attempts:
            outcome = "no-final-designation"
        else:
            outcome = "not-run"
        primary += outcome == "success"
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
        rows.append({key: measured[task][key] for key in MEASUREMENT_KEYS if key in measured.get(task, {})})
        tasks.append({"task_id": task, "outcome": outcome, "final_poc_id": finals.get(task),
                      "attempts": len(attempts), "any_attempt_success": task_any,
                      "reason": errors.get(task)})
    planned = len(plan["tasks"])
    synthetic = bool(plan["synthetic"] or receipts["synthetic"])
    agents = sorted({record["agent_id"] for record in receipts["records"]})
    report = _envelope("benchmark-eval-report", synthetic, inputs or {})
    report.update({
        "benchmark": {
            "name": plan["benchmark"], "metric": plan["metric"], "plan_id": plan["plan_id"],
            "plan_sha256": canonical_sha256(plan), "task_set_sha256": task_set_sha256(plan["tasks"]),
            "source": plan["source"], "verifier_revision": plan["verifier_revision"],
            "dataset_revision": plan["dataset_revision"], "level": plan["level"], "split": plan["split"],
            "trial_budget": plan["trial_budget"],
            "trial_budget_note": "Declared provenance only; not enforced and not a limit on candidate records.",
            "planned_tasks": planned, "synthetic": plan["synthetic"],
        },
        "run": {"run_id": receipts["run_id"], "agent_id": agents[0] if agents else None,
                "identity": receipts["identity"], "settings": receipts["settings"],
                "verification_source": receipts["verification_source"], "synthetic": receipts["synthetic"],
                "final_designation": "operator-supplied; the upstream record has no final marker"},
        "primary": dict(proportion(primary, planned, "final-designated successes / all planned tasks"),
                        name="final-designated reproduction", primary=True, note=PRIMARY_NOTE),
        "diagnostics": {
            "any_attempt": dict(proportion(any_success, planned, "tasks with any successful attempt / all planned tasks"),
                                primary=False,
                                note="Diagnostic only: selecting the best attempt after the fact is not the headline result."),
        },
        "outcomes": dict(sorted(outcomes.items())),
        "subset": {"planned_tasks": planned, "records": len(receipts["records"]),
                   "note": "Covers exactly the planned tasks; no full-benchmark extrapolation."},
        "measurements": _aggregate_measurements(rows, planned),
        "tasks": tasks,
    })
    return report


# ---------- matched comparison ----------

def _unknown(value: Any) -> bool:
    if value == UNKNOWN:
        return True
    if isinstance(value, list):
        return any(_unknown(item) for item in value)
    if isinstance(value, dict):
        return any(_unknown(item) for item in value.values())
    return False


def _normal(value: Any) -> Any:
    return sorted(value) if isinstance(value, list) and all(isinstance(v, str) for v in value) else value


def _match(fields: Sequence[Tuple[str, Any, Any]]) -> List[str]:
    problems = []
    for name, left, right in fields:
        if _unknown(left) or _unknown(right):
            problems.append(f"{name} is unknown and cannot be matched")
        elif _normal(left) != _normal(right):
            problems.append(f"{name} differs: baseline={json.dumps(left, sort_keys=True)} "
                            f"candidate={json.dumps(right, sort_keys=True)}")
    return problems


IDENTITY_FIELDS = ("model", "tools", "environment", "budget")


def _delta(base: Dict[str, Any], cand: Dict[str, Any]) -> Dict[str, Any]:
    if base.get("status") != "available" or cand.get("status") != "available":
        return {"status": "unavailable", "value": None}
    return {"status": "available", "value": round(cand["value"] - base["value"], 6)}


def _refused(kind: str, problems: List[str]) -> Dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "kind": kind, "status": "refused", "mismatches": problems,
            "release_clearance": False, "leaderboard_eligible": False, "executed": False}


def compare_review(baseline: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two review reports produced by evaluate_review; refuse unmatched provenance."""
    problems = _match([("inventory_sha256", baseline["inventory"]["inventory_sha256"],
                        candidate["inventory"]["inventory_sha256"])]
                      + [(f"identity.{key}", baseline["run"]["identity"][key], candidate["run"]["identity"][key])
                         for key in IDENTITY_FIELDS])
    if baseline["run"]["run_id"] == candidate["run"]["run_id"]:
        problems.append("baseline and candidate have the same run_id")
    if problems:
        return _refused("review-eval-comparison", problems)
    base_found = {d for case in baseline["cases"] for d in case["matched_defects"]}
    cand_found = {d for case in candidate["cases"] for d in case["matched_defects"]}
    synthetic = baseline["evidence"] == "synthetic-fixture" or candidate["evidence"] == "synthetic-fixture"
    result = _envelope("review-eval-comparison", synthetic,
                       {**{f"baseline.{k}": v for k, v in baseline["input_sha256"].items()},
                        **{f"candidate.{k}": v for k, v in candidate["input_sha256"].items()}})
    result.update({
        "matched": {"inventory_sha256": baseline["inventory"]["inventory_sha256"],
                    **{key: baseline["run"]["identity"][key] for key in IDENTITY_FIELDS}},
        "baseline": {"run_id": baseline["run"]["run_id"], "method": baseline["run"]["identity"]["method"],
                     "metrics": baseline["metrics"]},
        "candidate": {"run_id": candidate["run"]["run_id"], "method": candidate["run"]["identity"]["method"],
                      "metrics": candidate["metrics"]},
        "delta": {name: _delta(baseline["metrics"][name], candidate["metrics"][name])
                  for name in baseline["metrics"]},
        "paired_defects": {"found_by_both": len(base_found & cand_found),
                           "candidate_only": sorted(cand_found - base_found),
                           "baseline_only": sorted(base_found - cand_found)},
        "note": "Descriptive difference of supplied observations; no significance test or ranking.",
    })
    return result


BENCHMARK_FIELDS = ("name", "metric", "source", "verifier_revision", "dataset_revision",
                    "level", "split", "trial_budget", "task_set_sha256")
SETTING_FIELDS = ("network", "dynamic_environment", "cross_task_memory")


def compare_benchmark(baseline: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two benchmark reports produced by evaluate_benchmark; refuse unmatched settings."""
    problems = _match([(f"benchmark.{key}", baseline["benchmark"][key], candidate["benchmark"][key])
                       for key in BENCHMARK_FIELDS]
                      + [(f"identity.{key}", baseline["run"]["identity"][key], candidate["run"]["identity"][key])
                         for key in IDENTITY_FIELDS]
                      + [(f"settings.{key}", baseline["run"]["settings"][key], candidate["run"]["settings"][key])
                         for key in SETTING_FIELDS])
    if baseline["run"]["run_id"] == candidate["run"]["run_id"]:
        problems.append("baseline and candidate have the same run_id")
    if problems:
        return _refused("benchmark-eval-comparison", problems)
    base_ok = {t["task_id"] for t in baseline["tasks"] if t["outcome"] == "success"}
    cand_ok = {t["task_id"] for t in candidate["tasks"] if t["outcome"] == "success"}
    synthetic = baseline["evidence"] == "synthetic-fixture" or candidate["evidence"] == "synthetic-fixture"
    result = _envelope("benchmark-eval-comparison", synthetic,
                       {**{f"baseline.{k}": v for k, v in baseline["input_sha256"].items()},
                        **{f"candidate.{k}": v for k, v in candidate["input_sha256"].items()}})
    result.update({
        "matched": {**{key: baseline["benchmark"][key] for key in BENCHMARK_FIELDS},
                    **{key: baseline["run"]["identity"][key] for key in IDENTITY_FIELDS},
                    **{key: baseline["run"]["settings"][key] for key in SETTING_FIELDS}},
        "baseline": {"run_id": baseline["run"]["run_id"], "method": baseline["run"]["identity"]["method"],
                     "primary": baseline["primary"]},
        "candidate": {"run_id": candidate["run"]["run_id"], "method": candidate["run"]["identity"]["method"],
                      "primary": candidate["primary"]},
        "delta": {"primary": _delta(baseline["primary"], candidate["primary"]),
                  "any_attempt_diagnostic": _delta(baseline["diagnostics"]["any_attempt"],
                                                   candidate["diagnostics"]["any_attempt"])},
        "paired_tasks": {"both_success": len(base_ok & cand_ok), "candidate_only": sorted(cand_ok - base_ok),
                         "baseline_only": sorted(base_ok - cand_ok)},
        "note": "Descriptive difference of imported receipts on one fixed subset; not a leaderboard comparison.",
    })
    return result


def describe_hashes(doc: Any, kind: str) -> Dict[str, Any]:
    if kind == "inventory":
        inventory = validate_inventory(doc)
        return {"status": "ok", "inventory_id": inventory["inventory_id"],
                "inventory_sha256": canonical_sha256(inventory),
                "case_set_sha256": task_set_sha256(case["case_id"] for case in inventory["cases"])}
    plan = validate_plan(doc)
    return {"status": "ok", "plan_id": plan["plan_id"], "plan_sha256": canonical_sha256(plan),
            "task_set_sha256": task_set_sha256(plan["tasks"])}
