#!/usr/bin/env python3
# component: current-command-surface-check
# implements: ADR-0028
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: read-only current-tree check; historical records and notices are not routing
# last_intent_review: 2026-09-25
"""Check current workflow identities and literal local references, without executing them."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from functools import lru_cache
import importlib.util
import hashlib
from html.parser import HTMLParser
from html import unescape
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from urllib.parse import unquote

sys.dont_write_bytecode = True
SOURCE_ROOT = Path(__file__).resolve().parents[2]
RESIDUAL_REGISTER = ".claude/plans/legacy-cleanup/residuals.md"


# Approved entry retirements, including expired central aliases. These are command
# identities, not a ban on words, client vendors, persisted data paths or attribution.
RETIRED_COMMANDS = frozenset("""
office-hours plan-ceo-review plan-eng-review plan-design-review plan-devex-review
devex-review plan-tune autoplan qa qa-only investigate codex learn lessons skillify
document-generate context-save context-restore context-warm-related context-warm-adrs
context-warm-sessions browse scrape open-managed-browser setup-browser-cookies make-pdf
design-consultation design-shotgun design-html design-review retro landing-report health
pair-agent careful code-unfreeze research plan-and-build review-and-ship help v4-migrate
personas-rotate match context-budgetwatch context-snapshot context-dump context-warmup
role-activate role-deactivate role-rotate role-frame role-deep-dive role-update
ta-api-design ta-boundary-review ta-complexity-audit ta-contract-collision
ta-dependency-graph ta-quality-attributes ta-scaling-plan
da-analytics-readiness da-data-contract-collision da-migration-plan da-query-pattern-audit
da-retention-policy da-schema-design da-sharding-plan
sc-audit-path sc-auth-flow sc-compliance-evidence sc-dependency-security sc-incident-runbook
sc-secret-management sc-threat-model
dh-capacity-headroom dh-cost-projection dh-deployment-plan dh-observability-spec
dh-on-call-playbook dh-rollback-strategy dh-sli-slo-spec
tq-chaos-plan tq-contract-test-design tq-coverage-audit tq-flaky-quarantine
tq-perf-budget-spec tq-regression-suite tq-test-pyramid-review
freeze unfreeze benchmark context-tokenwatch
""".split())

# Exceptions are exact files or typed evidence fields, never archival directories.
# The CLI reports every applied exception; none is a claim of review clearance.
SOURCE_EXCEPTIONS = {
    "tests/shape/native-command-surface.py": "The explicit retirement policy, not a routing consumer.",
    "tests/unit/native-command-surface.py": "Deliberate positive and negative regression fixtures.",
    "LICENSE": "The distributed project license must retain its original legal text.",
    "skills/design-dna/LICENSES/MIT-next-level-builder.txt": "Required notice for the retained design corpus.",
    "skills/design-dna/LICENSES/Apache-2.0-anthropic.txt": "Required license for the retained profile adaptation.",
}
IGNORED_DIRECTORIES = frozenset({".git", "node_modules", "__pycache__", ".venv", "venv"})
TEXT_SUFFIXES = frozenset({
    ".md", ".sh", ".ps1", ".py", ".json", ".yaml", ".yml", ".toml",
    ".js", ".mjs", ".html", ".htm", ".txt", ".template", ".example",
})
HOST_SLASH_COMMANDS = frozenset({"help", "skills", "instructions", "plugins", "plugin"})
NAME = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*"
EXPLICIT_COMMAND = re.compile(rf"(?<![\w/:])(?:/li[:-]|skill:)(?P<name>{NAME})(?![\w-])", re.I)
NATIVE_COMMAND = re.compile(rf"(?<![\w/:-])li-(?P<name>{NAME})(?![\w.-])", re.I)
BARE_COMMAND = re.compile(rf"`/(?P<name>{NAME})(?=[\s`])", re.I)
NAMED_SKILL = re.compile(
    rf"(?:\b(?:skill|workflow|command)\s+[`'\"](?P<before>{NAME})[`'\"]|"
    rf"[`'\"](?P<after>{NAME})[`'\"]\s+skill\b)", re.I,
)
SKILL_FIELD = re.compile(
    rf"""(?:^[ \t]*(?:-[ \t]+)?skill\s*[:=]|["']skill["']\s*:|[{{,]\s*skill\s*:|`skill\s*:)"""
    rf"""\s*["']?(?P<name>{NAME})(?=["'\s,}}`]|$)""", re.I,
)
DISTINCTIVE_COMMAND = re.compile(
    r"(?<![\w/.-])(" + "|".join(re.escape(name) for name in sorted(RETIRED_COMMANDS)
                                if "-" in name) + r")(?![\w/.-])", re.I,
)
SKILL_PATH = re.compile(
    rf"(?<![\w-])(?P<prefix>\.(?:github|agents|gemini|claude|cursor|opencode)/skills/|skills/)"
    rf"(?P<name>(?:li:)?{NAME})(?P<tail>(?:/[a-zA-Z0-9_.%-]+)*)(?![\w-])"
)
LINK = re.compile(r"\[[^\]\n]*\]\((<?[^\s)]+>?)(?:\s+['\"][^)]*)?\)")
URL = re.compile(r"\b(?:https?|mailto):[^\s`<>)]+", re.I)
COHORT_REPORTS = {
    f".claude/engineering/audits/lintel-uniformity-findings-cohort{number}-{name}.md": number
    for number, name in (
        (1, "phase-core"), (2, "planner"), (3, "handoff"), (4, "agents"),
        (5, "hooks"), (6, "eng-domains"), (7, "packs-roles"), (8, "cross-cutting"),
    )
}
PEER_REPORTS = {
    f".claude/engineering/audits/lintel-uniformity-cross-X{number}-{name}.md": number
    for number, name in (
        (1, "concept-consistency"), (2, "promise-verification"), (3, "evolution"),
        (4, "entry-point-matrix"), (5, "necessity"),
    )
}
FORMER_HEADERS = frozenset({
    "old", "old name", "former", "former entry", "former entries",
    "retired entry", "retired entries", "removed entry", "removed entries",
})
# The operator reserved this original experiment input, not the presentation subtree.
COMPARISON_DIR = "presentations/tech-shots-2026-09-25/comparison"
COMPARISON_INPUT = "with-lintel/workflow-context.md"
COMPARISON_REVISION = "275a35447c4ad271e05816ade43ac48f1acec24f"


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    code: str
    message: str


def frontmatter(text: str) -> list[str]:
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0] != "---":
        return []
    try:
        return lines[1:lines.index("---", 1)]
    except ValueError:
        return []


def declared_aliases(lines: list[str]) -> list[tuple[int, str]]:
    result = []
    in_aliases = False
    for index, line in enumerate(lines, 2):
        clean = line.split("#", 1)[0].rstrip()
        match = re.match(r"^(?:deprecated_aliases|v1_alias):\s*(.*)$", clean)
        if match:
            in_aliases = not match[1]
            result.extend((index, value.strip(" \t[]'\""))
                          for value in match[1].split(",") if value.strip(" \t[]'\""))
        elif in_aliases and re.match(r"^\s+-\s+", clean):
            result.append((index, re.sub(r"^\s+-\s+", "", clean).strip("'\"")))
        elif clean and not clean[0].isspace():
            in_aliases = False
    return result


def source_files(root: Path) -> list[Path]:
    if (root / ".git").exists():
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            capture_output=True, check=False,
        )
        if result.returncode:
            raise ValueError("Cannot enumerate the current tracked/untracked nonignored tree.")
        paths = sorted(set(result.stdout.decode("utf-8").split("\0")) - {""})
        return [root / relative for relative in paths
                if (root / relative).exists() and (
                    (root / relative).suffix in TEXT_SUFFIXES
                    or Path(relative).name in {"LICENSE", "NOTICE", "COPYING"}
                    or (not Path(relative).suffix and Path(relative).parent.name == "bin")
                )]
    # Synthetic fixture trees need no Git initialization or repository mutation.
    result = []
    for directory, folders, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        folders[:] = sorted(
            name for name in folders
            if name not in IGNORED_DIRECTORIES
            and not (parent / name).is_symlink()
            and not getattr((parent / name).lstat(), "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        )
        for name in sorted(files):
            path = parent / name
            if (path.suffix in TEXT_SUFFIXES or path.name in {"LICENSE", "NOTICE", "COPYING"}
                    or (not path.suffix and parent.name == "bin")):
                result.append(path)
    return result


def evidence_category(value: object) -> str | None:
    """Recognize data envelopes, not their validity, decision or independence."""
    if not isinstance(value, dict) or value.get("schema_version") != 2:
        return None
    if value.get("artifact_kind") in {"swarm-report", "swarm-review"}:
        if {"work_map", "package_id", "leaf_ids", "attempt_id", "acceptance_digest", "result_digest"} <= value.keys():
            return "swarm observation payload"
    if {"work", "snapshot", "profile", "attempt_id", "builder", "qa_requirements"} <= value.keys():
        return "content-bound review context"
    if {"skill", "status", "timestamp", "context", "reviewer", "provenance", "controls",
        "coverage", "evidence"} <= value.keys():
        return "content-bound review decision"
    if {"context_digest", "controls", "evidence"} <= value.keys():
        return "bound QA observation"
    return None


def json_locations(text: str) -> tuple[object, dict[tuple, tuple[int, int, object]]]:
    """Use the JSON decoder to locate values; never infer a field from a line regex."""
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    decoder = json.JSONDecoder(object_pairs_hook=unique)
    value = decoder.decode(text)
    locations = {}

    def whitespace(index):
        return re.compile(r"\s*").match(text, index).end()

    def walk(item, path, start):
        start = whitespace(start)
        index = start
        if isinstance(item, (dict, list)):
            index = whitespace(start + 1)
            children = item.items() if isinstance(item, dict) else enumerate(item)
            for key, child in children:
                if isinstance(item, dict):
                    _, index = decoder.raw_decode(text, index)
                    index = whitespace(index) + 1  # The already-decoded colon.
                index = whitespace(walk(child, (*path, key), index))
                if text[index:index + 1] == ",":
                    index = whitespace(index + 1)
            end = index + 1
        else:
            _, end = decoder.raw_decode(text, start)
        locations[path] = (start, end, item)
        return end

    walk(value, (), 0)
    return value, locations


@lru_cache(maxsize=2)
def observation_support(name: str):
    if name not in {"envelope_contract", "markdown_source"}:
        raise ValueError("Unknown observation support module")
    path = SOURCE_ROOT / "lib" / (name + ".py")
    if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
        raise ValueError("Linked observation support module refused")
    specification = importlib.util.spec_from_file_location("routing_" + name, path)
    if specification is None or specification.loader is None:
        raise ValueError("Required observation support module is unavailable")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def registered_observation_spans(root: Path) -> tuple[dict[str, list[dict]], list[Finding]]:
    register = root / RESIDUAL_REGISTER
    if not register.exists():
        return {}, []
    errors = []
    spans: dict[str, list[dict]] = {}
    try:
        source = register.read_text(encoding="utf-8-sig")
        records = list(re.finditer(
            r"(?m)^<!-- lintel-reviewed-source-spans:v1\r?\n(?P<json>[\s\S]*?)^-->", source))
        if not records:
            return {}, []
        if len(records) != 1:
            raise ValueError("Ambiguous reviewed-span register")
        envelope = observation_support("envelope_contract")
        value = envelope.load_text(records[0]["json"])
        if (not isinstance(value, dict) or set(value) != {"entries"}
                or not isinstance(value["entries"], list)):
            raise ValueError("Reviewed-span register must contain exactly an entries list")
        keys = {"id", "path", "start", "end", "sha256", "category", "reason",
                "source_evidence", "declaration_digest", "review", "corroboration"}
        identifiers = set()
        markdown = observation_support("markdown_source")
        sys.path.insert(0, str(SOURCE_ROOT / "lib"))
        from context_safety import read_owned
        from review_contract import content_digest, load_json, validate_review, validate_shape

        for entry in value["entries"]:
            if not isinstance(entry, dict) or set(entry) != keys:
                raise ValueError("Malformed reviewed-span entry")
            identifier = entry["id"]
            if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", identifier) or identifier in identifiers:
                raise ValueError("Invalid or duplicate reviewed-span ID")
            identifiers.add(identifier)
            relative = entry["path"]
            parts = Path(relative).parts if isinstance(relative, str) else ()
            if (not parts or "\\" in relative or ":" in relative or relative.startswith("/")
                    or any(part in {"", ".", ".."} for part in relative.split("/"))
                    or any(character in relative for character in "*?[")):
                raise ValueError("Reviewed span must name one literal repository-relative source")
            if relative == RESIDUAL_REGISTER or not all(
                    isinstance(entry[field], str) and entry[field].strip()
                    for field in ("start", "end", "category", "reason", "source_evidence")):
                raise ValueError("Reviewed span requires exact markers and a substantive source reason")
            if not all(re.fullmatch(r"[0-9a-f]{64}", entry[field] or "")
                       for field in ("sha256", "declaration_digest")):
                raise ValueError("Reviewed span needs raw source and declaration digests")
            declaration = {key: entry[key] for key in
                           ("id", "path", "start", "end", "sha256", "category", "reason", "source_evidence")}
            if content_digest(declaration) != entry["declaration_digest"]:
                raise ValueError(f"Reviewed-span declaration changed: {identifier}")
            path = root / relative
            for parent in (path, *path.parents):
                if parent == root.parent:
                    break
                if parent.exists() and (parent.is_symlink() or getattr(parent.lstat(), "st_file_attributes", 0) & 0x400):
                    raise ValueError(f"Linked reviewed-span source refused: {relative}")
            data, _ = read_owned(root, relative, 2097152)
            text = data.decode("utf-8")
            boundaries = markdown.classify_markdown(text)
            starts = [line for line in boundaries.lines
                      if text[line.start:line.end] == entry["start"]]
            ends = [line for line in boundaries.lines
                    if text[line.start:line.end] == entry["end"]]
            if len(starts) != 1 or len(ends) != 1 or starts[0].start >= ends[0].start:
                raise ValueError(f"Missing, duplicated or reordered reviewed-span markers: {identifier}")
            if starts[0].container_ids or ends[0].container_ids:
                raise ValueError(f"Nested reviewed-span markers refused: {identifier}")
            if starts[0].kind != "prose" or ends[0].kind != "prose":
                raise ValueError(f"Literal or opaque reviewed-span boundaries refused: {identifier}")
            lower, upper = starts[0].start, ends[0].start
            if lower == 0 and upper >= len(text.rstrip("\r\n")):
                raise ValueError("Whole-file reviewed-span exemptions are forbidden")
            selected = text[lower:upper].encode("utf-8")
            if hashlib.sha256(selected).hexdigest() != entry["sha256"]:
                raise ValueError(f"Reviewed-span raw bytes changed: {identifier}")
            review_path = entry["review"]
            if (not isinstance(review_path, str) or not review_path.startswith(".claude/plans/legacy-cleanup/")
                    or ".." in review_path.split("/") or "\\" in review_path):
                raise ValueError("Reviewed-span decision must be an explicit committed cleanup artifact")
            decision = validate_review(load_json(read_owned(root, review_path, 2097152)[0].decode("utf-8-sig")))
            if (decision["status"] not in {"pass", "unverified"}
                    or decision["reviewer"]["id"] == decision["context"]["builder"]["id"]
                    or decision["reviewer"]["context"] == decision["context"]["builder"]["context"]):
                raise ValueError("Reviewed spans require a distinct review actor/context")
            corroboration_path = entry["corroboration"]
            if (not isinstance(corroboration_path, str)
                    or not corroboration_path.startswith(".claude/plans/legacy-cleanup/")
                    or ".." in corroboration_path.split("/") or "\\" in corroboration_path):
                raise ValueError("Reviewed-span corroboration must be an explicit committed cleanup artifact")
            corroboration = load_json(read_owned(root, corroboration_path, 2097152)[0].decode("utf-8-sig"))
            validate_shape(corroboration, "corroboration")
            if (corroboration["record_digest"] != content_digest(decision)
                    or corroboration["attempt_id"] != decision["context"]["attempt_id"]
                    or corroboration["builder"] != decision["context"]["builder"]
                    or corroboration["reviewer"] != decision["reviewer"]):
                raise ValueError("Reviewed-span actor observation does not match the exact semantic decision")
            source_context = [item for item in decision["context"]["work"]["acceptance_manifest"]
                              if item["path"] == relative and item["start"] is None and item["end"] is None]
            if len(source_context) != 1 or source_context[0]["sha256"] != hashlib.sha256(data).hexdigest():
                raise ValueError(f"Original observation context changed or is not bound: {identifier}")
            approved = [control for control in decision["controls"]
                        if control["id"] == "historical-spans" and control["kind"] == "check"
                        and control["requirement"] == "mandatory" and control["applicability"] == "applicable"
                        and control["status"] == "pass"]
            if len(approved) != 1 or entry["declaration_digest"] not in approved[0]["observation"].get("span_declarations", []):
                raise ValueError(f"Span lacks an exact passing independent semantic observation: {identifier}")
            report_paths = approved[0]["evidence"]
            evidence = {item["path"]: item["sha256"] for item in decision["evidence"]}
            if not report_paths or any(
                    hashlib.sha256(read_owned(root, name, 2097152)[0]).hexdigest() != evidence[name]
                    for name in report_paths):
                raise ValueError("Reviewed-span supporting report is missing or changed")
            previous = spans.setdefault(relative, [])
            if any(lower < item["end"] and upper > item["start"] for item in previous):
                raise ValueError("Overlapping reviewed spans are forbidden")
            previous.append({**entry, "start": lower, "end": upper,
                             "line": text.count("\n", 0, lower) + 1,
                             "end_line": text.count("\n", 0, upper - 1) + 1})
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
        errors.append(Finding(RESIDUAL_REGISTER, 1, "reviewed-span-invalid", str(error)))
        return {}, errors
    return spans, errors


def cohort_yaml_observations(text: str, relative: str, observe, reject) -> None:
    cohort = COHORT_REPORTS.get(relative)
    if cohort is None:
        return
    title = re.search(r"(?im)^#[^\n]*\bCohort\s+([1-8])\b", text)
    dated = re.search(r"(?im)^\*\*(?:Auditor pass date|Audit date|Date):\*\*\s*\d{4}-\d{2}-\d{2}\b", text)
    if title is None or int(title[1]) != cohort or dated is None:
        return
    boundaries = observation_support("markdown_source").classify_markdown(text)
    envelope = observation_support("envelope_contract")
    opening = None
    for line in boundaries.lines:
        content = text[line.content_start:line.end]
        marker = re.fullmatch(r"(`{3,}|~{3,})(.*)", content)
        if line.kind != "fenced_code":
            opening = None
            continue
        if opening is None:
            if marker and marker[2].strip() in {"yaml", "yml"}:
                opening = (marker[1], line.next_start)
            continue
        if not marker or marker[2].strip() or marker[1][0] != opening[0][0] or len(marker[1]) < len(opening[0]):
            continue
        offset = opening[1]
        document = text[offset:line.start]
        opening = None
        if not has_reference(document):
            continue
        if cohort == 8 and not re.search(r"(?m)^layer: provenance\s*$", document):
            continue
        record_line = text.count("\n", 0, offset) + 1
        try:
            value = envelope.load_text(document)
            yaml = envelope._yaml_module()
            node = yaml.compose(document, Loader=yaml.SafeLoader)
        except (envelope.EnvelopeError, ValueError) as error:
            reject(record_line, f"Cohort observation parse failed: {error}")
            continue
        if not isinstance(value, dict):
            reject(record_line, "Unsupported cohort observation: expected an original record mapping")
            continue
        layer_record = cohort == 8 and {"layer", "status", "built_artifacts", "dimensions"} <= value.keys()
        component_record = (
            {"component", "kind", "cohort", "peer_comparison", "operator_decision_required", "priority"} <= value.keys()
            and value.get("cohort") == cohort and type(value.get("cohort")) is int
            and value.get("kind") in {
                "skill", "agent", "hook", "lib", "role",
                "skill (orchestrator, workflow_root)", "skill (composite-delegator)",
            }
            and isinstance(value.get("component"), str)
        )
        if not layer_record and not component_record:
            reject(record_line, "Unsupported cohort observation record; no fields were exempted")
            continue
        selected = set()
        if layer_record:
            selected.add(("built_artifacts", 0))
        else:
            selected.update((key,) for key in ("component", "kind", "cohort", "operator_decision_required", "priority"))
            dimensions = value.get("dimensions")
            if isinstance(dimensions, dict):
                for key, fields in dimensions.items():
                    if isinstance(key, str) and re.fullmatch(r"D(?:[1-9]|1[0-4])_[A-Za-z0-9_]+", key) and isinstance(fields, dict):
                        selected.update(("dimensions", key, field) for field in
                                        ("state", "nano", "macro", "high", "finding", "proposed", "why"))
            deltas = value.get("deltas")
            if isinstance(deltas, dict) and isinstance(value.get("shared_with_role_activate"), str):
                selected.add(("shared_with_role_activate",))
                selected.update(("deltas", field) for field in (
                    "D2_tail", "D3_objects", "D4_entrypoints", "D5_checkpoints", "D6_recovery",
                    "D7_pack", "D9_brief_forge", "D10_knowledge", "D11_subagent", "D13_observability",
                    "cross_ref", "pii_discipline", "integrity_check", "role_in_cohort",
                ))
            selected.update(("peer_comparison", field) for field in
                            ("strongest_peer_in_cohort", "this_component_depth", "uplift_needed"))

        def visit(current, path=()):
            if isinstance(current, yaml.MappingNode):
                for key, child in current.value:
                    if isinstance(key, yaml.ScalarNode):
                        visit(child, (*path, key.value))
            elif isinstance(current, yaml.SequenceNode):
                for index, child in enumerate(current.value):
                    visit(child, (*path, index))
            elif isinstance(current, yaml.ScalarNode) and path in selected:
                observe(offset + current.start_mark.index, offset + current.end_mark.index,
                        "cohort record /" + "/".join(map(str, path)), "source-era cohort field",
                        "Named original cohort-audit value; source marks preserve adjacent fields. This is not current routing, verified binding or execution.")
        visit(node)


def observation_fields(value: object) -> list[tuple[tuple, str, str]]:
    """Classify inspected data fields, not a schema, authorization or binding verdict."""
    if not isinstance(value, dict):
        return []
    selected = []

    def fields(record, prefix, names, category, reason):
        for name in sorted(names):
            if name in record:
                selected.append(((*prefix, name), category, reason))

    if (isinstance(value.get("candidate"), str) and re.fullmatch(r"[0-9a-f]{40}", value["candidate"])
            and isinstance(value.get("reviewer"), dict) and isinstance(value.get("decisions"), list)
            and ("artifact_type" in value or "review_type" in value)):
        category = "declared semantic-review field"
        reason = "Original per-declaration review observation; only exact reviewed-span admission checks its decision and context. Shape is not independence or release clearance."
        fields(value, (), (
            "artifact_type", "review_type", "status", "date", "candidate",
            "decision_target", "representation_mapping", "representation",
            "representation_mapping_path", "representation_mapping_sha256",
            "input_path", "input_sha256", "input_bytes", "reviewer", "result",
            "original_work", "mandatory_semantic_conditions", "required_original_contexts",
            "counterexamples", "verification", "preserved_quality_report", "stop",
            "superseded_crlf_decisions", "representation_decision", "scope", "counts",
            "release_clearance", "canonical_p05_record_written", "overall_acceptance",
            "historical_context_binding", "input", "conditions", "base", "carry_over_source",
            "prior_artifacts_unchanged", "qa_and_guard_limits", "preserved_set01_lf",
            "selected_raw_excerpt_bytes", "selected_declarations", "selected_source_files",
            "identity_binding", "owner_chronology", "common_conditions",
            "checks_actually_performed", "executed_command_ledger",
        ), category, reason)
        for index, decision in enumerate(value["decisions"]):
            if (isinstance(decision, dict) and {"id", "declaration_digest", "decision"} <= decision.keys()
                    and decision["decision"] in {"ACCEPT", "REJECT", "NEEDS_EVIDENCE"}):
                fields(decision, ("decisions", index), (
                    "id", "declaration_digest", "sha256", "raw_sha256", "path",
                    "start", "end", "end_exclusive", "start_line", "end_line_exclusive",
                    "source_lines_inclusive", "decision", "basis", "current_use_analysis",
                    "adjacent_boundary", "specific_counterexample", "prior_crlf_declaration_digest",
                    "current_instruction_found", "semantic_reason", "current_instruction_assessment",
                    "boundary_assessment",
                    "counterexamples", "current_use_inside", "narrowing_suggestion",
                    "source_context_sha256", "source_git_blob", "bounded_narrowing",
                ), category, reason)

    category = evidence_category(value)
    if category:
        fields(value, (), (
            "schema_version", "artifact_kind", "initiative", "task_id", "status", "worker",
            "actor_ref", "isolation_ref", "observed_head", "branch", "work_map", "package_id",
            "leaf_ids", "attempt_id", "acceptance_digest", "result", "result_digest",
            "changed_paths", "deleted_paths", "leaf_results", "checks", "limitations",
            "skill", "timestamp", "reason", "context", "reviewer", "provenance", "controls",
            "coverage", "evidence", "work", "snapshot", "profile", "builder", "purpose",
            "independence_required", "required_policy", "required_controls", "qa_requirements",
            "context_digest",
        ), category, "Recorded evidence field; binding, status and independence are not verified by this routing check.")

    baseline = value.get("baseline")
    if isinstance(baseline, dict):
        baseline = baseline.get("commit")
    if isinstance(baseline, str) and re.fullmatch(r"[a-fA-F0-9]{7,64}", baseline):
        reason = f"Declared source baseline {baseline}; recorded source-era data, not current routing. Baseline/binding not verified."
        inventory_keys = {"path", "group", "bytes", "lines", "skill_refs", "tool_terms"}
        if isinstance(value.get("files"), list):
            for index, entry in enumerate(value["files"]):
                if (isinstance(entry, dict) and inventory_keys <= entry.keys()
                        and isinstance(entry["path"], str) and isinstance(entry["group"], str)
                        and all(type(entry[key]) is int and entry[key] >= 0 for key in ("bytes", "lines"))
                        and all(isinstance(entry[key], list) and all(isinstance(part, str) for part in entry[key])
                                for key in ("skill_refs", "tool_terms"))):
                    fields(entry, ("files", index), inventory_keys, "source-era inventory", reason)
        if ({"scope", "coverage", "findings", "interactions", "limitations"} <= value.keys()
                and isinstance(value["scope"], (str, dict))
                and isinstance(value["coverage"], (list, dict))
                and all(isinstance(value[key], list) for key in ("findings", "interactions", "limitations"))):
            category = "source-era audit review"
            coverage_keys = {"name", "path", "lines_read", "quality", "action", "reason", "evidence"}
            if isinstance(value["coverage"], list):
                for index, entry in enumerate(value["coverage"]):
                    if (isinstance(entry, dict) and coverage_keys <= entry.keys()
                            and isinstance(entry["path"], str) and type(entry["lines_read"]) is int
                            and isinstance(entry["evidence"], list)):
                        fields(entry, ("coverage", index), coverage_keys - {"evidence"}, category, reason)
                        for evidence_index, source in enumerate(entry["evidence"]):
                            if isinstance(source, dict):
                                fields(source, ("coverage", index, "evidence", evidence_index),
                                       ("path", "line", "lines", "note"), category, reason)
            for index, entry in enumerate(value["findings"]):
                if isinstance(entry, dict) and {"id", "evidence", "recommendation"} <= entry.keys():
                    fields(entry, ("findings", index), (
                        "id", "priority", "title", "problem", "impact", "recommendation",
                        "verification", "confidence", "sources",
                    ), category, reason)
                    if isinstance(entry["evidence"], list):
                        for evidence_index, source in enumerate(entry["evidence"]):
                            if isinstance(source, dict):
                                fields(source, ("findings", index, "evidence", evidence_index),
                                       ("path", "line", "lines", "note"), category, reason)
            for index, entry in enumerate(value["interactions"]):
                if isinstance(entry, str):
                    selected.append((("interactions", index), category, reason))
                elif isinstance(entry, dict):
                    fields(entry, ("interactions", index), (
                        "journey", "observation", "related_findings", "topic", "recommendation",
                        "subsystem", "current", "target", "sequence", "preserve", "findings",
                        "provenance", "examples_of_knowhow_to_recover",
                    ), category, reason)
            for index, entry in enumerate(value["limitations"]):
                if isinstance(entry, str):
                    selected.append((("limitations", index), category, reason))

    if (value.get("schema_version") == 1
            and all(isinstance(value.get(key), str) for key in ("initiative", "work_map", "charter"))
            and isinstance(value.get("scope_rules"), dict)
            and value["scope_rules"].get("worker") == "write_scope+own_report"
            and isinstance(value.get("lanes"), list)):
        reason = "Declared ownership may include removed paths; membership is not an import, validated authority or execution."
        if isinstance(value.get("coordinator_paths"), list):
            for index, path in enumerate(value["coordinator_paths"]):
                if isinstance(path, str):
                    selected.append((("coordinator_paths", index), "ownership membership", reason))
        for index, lane in enumerate(value["lanes"]):
            if (isinstance(lane, dict) and isinstance(lane.get("task_id"), str)
                    and isinstance(lane.get("write_scope"), list)):
                for member, path in enumerate(lane["write_scope"]):
                    if isinstance(path, str):
                        selected.append((("lanes", index, "write_scope", member), "ownership membership", reason))
    return selected


def has_reference(text: str) -> bool:
    text = re.sub(r"\\+", "/", text)
    return text.strip(" \t\r\n'\"").casefold() in RETIRED_COMMANDS or any(pattern.search(text) for pattern in (
        EXPLICIT_COMMAND, NATIVE_COMMAND, BARE_COMMAND, NAMED_SKILL, SKILL_FIELD,
        DISTINCTIVE_COMMAND, SKILL_PATH, LINK,
    ))


def comparison_input(value: object) -> str | None:
    if (not isinstance(value, dict) or value.get("schemaVersion") != 1 or value.get("attempt") != 2
            or not isinstance(value.get("provenance"), dict) or not isinstance(value.get("artifacts"), dict)):
        return None
    provenance = value["provenance"]
    recorded = value["artifacts"].get(COMPARISON_INPUT)
    if (provenance.get("sourceRevision") == COMPARISON_REVISION
            and isinstance(provenance.get("frozenAt"), str) and provenance["frozenAt"]
            and isinstance(recorded, str) and recorded):
        return recorded
    return None


def html_source_observations(text: str, observe) -> None:
    offsets = [0]
    for match in re.finditer("\n", text):
        offsets.append(match.end())

    class SourceFields(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.stack = []
            self.nodes = []

        def position(self):
            line, column = self.getpos()
            return offsets[line - 1] + column

        def handle_starttag(self, tag, attributes):
            start = self.position()
            node = {"tag": tag, "attributes": dict(attributes), "start": start,
                    "content": start + len(self.get_starttag_text()), "end": None,
                    "parent": self.stack[-1] if self.stack else None, "children": []}
            self.nodes.append(node)
            if self.stack:
                self.stack[-1]["children"].append(node)
            if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input",
                           "link", "meta", "param", "source", "track", "wbr"}:
                self.stack.append(node)

        def handle_startendtag(self, tag, attributes):
            self.handle_starttag(tag, attributes)
            if self.stack and self.stack[-1]["tag"] == tag:
                self.stack.pop()

        def handle_endtag(self, tag):
            if self.stack and self.stack[-1]["tag"] == tag:
                self.stack.pop()["end"] = self.position()

    parser = SourceFields()
    parser.feed(text)
    parser.close()

    def value(node):
        if node["end"] is None or node["children"]:
            return None
        return unescape(text[node["content"]:node["end"]]).strip()

    source_heading = next((value(node) for node in parser.nodes if node["tag"] == "h1"
                           and value(node) and re.fullmatch(r"[\w.-]+(?:/[\w.-]+)+", value(node))), None)
    excerpt_context = (
        source_heading
        and re.search(r"(?:read.only excerpt|source excerpt)", text, re.I)
        and re.search(r"Full-file SHA-256:\s*<code>[a-f0-9]{64}</code>", text, re.I)
        and re.search(r"(?:revision|snapshot)\s*<code>[a-f0-9]{7,40}</code>", text, re.I)
    )
    for node in parser.nodes:
        content = value(node)
        if content is None:
            continue
        if node["tag"] == "a" and "source-link" in node["attributes"].get("class", "").split():
            target = node["attributes"].get("href", "")
            match = re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+/blob/([a-f0-9]{40})/([^#]+)#L(\d+)", target)
            if match and content == unquote(match[2]) + ":" + match[3]:
                observe(node["content"], node["end"], "pinned source-link label", "source citation",
                        f"Label names source at declared Git revision {match[1]}, not an installed resource. Destination/content truth is not fetched or verified.")
        if not excerpt_context:
            continue
        if node["tag"] == "h1" and content == source_heading:
            observe(node["content"], node["end"], "source-excerpt identity", "declared original source",
                    "Identity label of the explicitly marked line-numbered source excerpt, not a current resource import.")
        elif node["tag"] == "title" and content.startswith(source_heading + " ") and "source excerpt" in content.lower():
            observe(node["content"], node["end"], "source-excerpt title", "declared original source",
                    "Title names the original excerpt source, not a current callable workflow.")
        elif node["tag"] == "code":
            parent = node["parent"]
            if parent and parent["tag"] == "div" and parent["attributes"].get("class") == "source-line":
                identifier = parent["attributes"].get("id", "")
                line = re.fullmatch(r"L(\d+)", identifier)
                anchors = [child for child in parent["children"] if child["tag"] == "a"]
                if (line and len(anchors) == 1 and anchors[0]["attributes"].get("href") == "#" + identifier
                        and value(anchors[0]) == line[1]):
                    observe(node["content"], node["end"], f"original source line {identifier}", "line-numbered source excerpt",
                            f"Escaped/inert code field in the declared excerpt of {source_heading}; no execution, exact-source binding or live workflow acceptance is inferred. Scripts and adjacent fields remain checked.")


def markdown_observations(text: str, relative: str, observe, reported_changes: set[str] | None = None) -> None:
    baseline = re.search(r"(?im)^(?:\*\*)?Baseline(?:\*\*)?:[^\n]*?\b([a-f0-9]{7,64})\b", text)
    if baseline is None and re.search(r"\bhistorical source comparison\b", text, re.I):
        baseline = re.search(r"\b(?:checkpoint|at)\s+`([a-f0-9]{7,64})`", text, re.I)
    if baseline is None:
        baseline = re.search(r"(?im)^\*\*(?:Auditor pass date|Audit date):\*\*\s*(\d{4}-\d{2}-\d{2})", text)
    context = f"Declared source-era context {baseline[1]}; observation only, baseline/binding not verified." if baseline else ""
    cohort = COHORT_REPORTS.get(relative)
    peer = PEER_REPORTS.get(relative)
    original_role = bool(
        (cohort and re.search(rf"(?im)^#[^\n]*\bCohort\s+{cohort}\b", text))
        or (peer and re.search(rf"(?im)^\*\*(?:Cross-cutting pass|Pass):\*\*\s*X{peer}\b", text))
    )
    original_date = re.search(r"(?im)^\*\*(?:Auditor pass date|Audit date|Date):\*\*\s*(\d{4}-\d{2}-\d{2})\b", text)
    peer_context = original_role and original_date is not None
    original_report = (
        relative in {
            ".claude/plans/universal-implementation/reports/P08.md",
            ".claude/plans/universal-implementation/reports/P08-A13.md",
            ".claude/plans/universal-implementation/reports/P11.md",
        }
        and re.search(r"\b[a-f0-9]{40}\b", text) is not None
        and re.search(r"(?im)^#[^\n]*\bP(?:08|11|13)\b", text) is not None
    )
    peer_tables = (
        ({"cohort", "norm", "deviators"}, {"deviators"}),
        ({"#", "promise", "verdict", "should-uphold count", "actually-upholds"}, {"actually-upholds"}),
        ({"#", "mechanism", "thread", "writes?", "consulted?", "verdict"}, {"mechanism", "writes?", "consulted?"}),
        ({"entry-point", "jobs", "brief-forge", "knowledge", "hooks", "packs", "voice", "provenance", "audit-log"}, {"entry-point"}),
        ({"#", "component", "proposed necessity", "proposed `gap_if_skipped` (one line)", "priority"}, {"component"}),
        ({"component", "path", "role in chain"}, {"component", "path"}),
        ({"root", "used by", "nano"}, {"used by", "nano"}),
        ({"agent", "refs", "invoked?", "primary phase(s)/skill(s)"}, {"primary phase(s)/skill(s)"}),
        ({"artifact kind", "exists today", "path"}, {"path"}),
        ({"layer", "sc has (bar)", "da has today", "uplift to reach bar"}, {"uplift to reach bar"}),
        ({"component", "kind", "state"}, {"component"}),
    )

    # These are inspected table field sets, not permission to ignore an audit/report.
    table_fields = (
        {"original source", "original recommendation", "evidence"},
        {"namn", "kvalitet", "åtgärd", "motivering", "belägg"},
        {"original and current source", "original recommendation; source state",
         "responsible package and acceptance", "retained method and output",
         "change or grounded retention rationale", "worked example and evidence", "remaining boundary"},
        {"audit record / original recommendation", "current canonical path and aliases / arguments",
         "retained method and output", "responsible package / leaf", "disposition and rationale",
         "worked example / evidence", "status and evidence limit"},
        {"component", "path", "role in chain"},
        {"skill", "current identity", "owner/evidence and retained current method", "remaining boundary"},
        {"retained names", "current method/arguments", "source and evidence limit"},
    )
    snapshot_fields = {"path", "status", "mode", "bytes (git lf)", "sha-256 (git lf blob)", "commits"}
    headers = []
    table_active = False
    deleted_heading = False
    declared_diff = False
    fence = None
    deleted_fence = False
    inventory_heading = False
    inventory_fence = None
    inventory_lines = []
    diff_fence = None
    diff_lines = []
    release = ""
    removed = False
    offset = 0
    for raw in text.splitlines(keepends=True):
        line = raw.rstrip("\r\n")
        start = offset
        offset += len(raw)
        boundary = re.match(r"^\s{0,3}(`{3,}|~{3,})([^`~]*)$", line)
        if boundary:
            if fence is None:
                fence = boundary[1]
                deleted_fence = deleted_heading and declared_diff and boundary[2].strip() == "text"
                if original_report and inventory_heading and boundary[2].strip() == "text":
                    inventory_fence = start + len(raw)
                    inventory_lines = []
                if original_report and boundary[2].strip() == "diff":
                    diff_fence = start + len(raw)
                    diff_lines = []
            elif boundary[1][0] == fence[0] and len(boundary[1]) >= len(fence) and not boundary[2].strip():
                if inventory_fence is not None and inventory_lines:
                    pattern = r"(?:skills|agents|bin|lib|tests|hooks|docs|install|config|scaffolding|\.claude|\.github)[/\\][\w./\\-]+"
                    if all(re.fullmatch(pattern, value.strip()) for _, value in inventory_lines if value.strip()):
                        for position, value in inventory_lines:
                            if value.strip():
                                observe(position, position + len(value), "original authored-path inventory member",
                                        "source-era path inventory",
                                        "Literal member in the original report's named authored/frozen-path inventory; no current import, validated deletion or execution is implied.")
                if diff_fence is not None and diff_lines:
                    values = [value for _, value in diff_lines]
                    if (any(value.startswith("--- ") for value in values)
                            and any(value.startswith("+++ ") for value in values)
                            and any(re.match(r"^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@", value) for value in values)
                            and all(not value or value.startswith(("--- ", "+++ ", "@@ ", "+", "-", " ", "\\ No newline"))
                                    for value in values)):
                        observe(diff_fence, start, "original unified-diff quotation", "recorded patch data",
                                "The original report quotes a complete file/hunk diff as observed change data; surrounding instructions and executable consumers remain checked.")
                fence = None
                deleted_fence = False
                inventory_fence = diff_fence = None
            continue
        if fence is not None:
            if inventory_fence is not None:
                inventory_lines.append((start, line))
            if diff_fence is not None:
                diff_lines.append((start, line))
            if deleted_fence and re.fullmatch(r"(?:skills|agents|bin|lib|tests|hooks|docs|install)/[\w./-]+", line.strip()):
                observe(start, start + len(line), "deleted path", "deleted-path record",
                        "Literal path in a declared deletion observation with a Git diff source; no execution or independently verified deletion is implied.")
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            headers = []
            table_active = False
            deleted_heading = heading[2].casefold() in {"actual deleted paths", "deleted paths", "removed paths"}
            inventory_heading = bool(re.fullmatch(r"(?:Exact P\d+-authored product paths|Frozen changed paths)",
                                                 heading[2], re.I))
            declared_diff = False
            if len(heading[1]) <= 2:
                version = re.match(r"(\d+\.\d+\.\d+)\b", heading[2])
                release = version[1] if version else ""
                removed = False
            elif len(heading[1]) == 3:
                removed = bool(release) and heading[2].casefold() == "removed"
        if deleted_heading and re.search(r"\bObserved\b.*`git diff [^`]*--diff-filter=D", line):
            declared_diff = True
        if relative == "CHANGELOG.md" and removed:
            for match in re.finditer(r"`(?:skills|bin|lib|tests)/[\w./-]+`", line):
                prefix = line[:match.start()]
                if (re.match(r"^\s*-\s+(?:The\b|Removed\b)", prefix, re.I)
                        and not re.search(r"\b(?:use|import|run|select|selection|load|invoke|execute|source|call|require)\b", prefix, re.I)):
                    observe(start + match.start(), start + match.end(),
                            f"release {release} / Removed / resource", "removed-resource declaration",
                            "Release-note removal is an observation, not a current resource dependency; the declared release is not independently verified.")
        if not line.lstrip().startswith("|"):
            headers = []
            table_active = False
            continue
        pipes = [match.start() for match in re.finditer(r"(?<!\\)\|", line)]
        cells = [(left + 1, right, line[left + 1:right].strip()) for left, right in zip(pipes, pipes[1:])]
        if not cells:
            continue
        if headers and len(headers) == len(cells) and all(re.fullmatch(r":?-{3,}:?", cell[2]) for cell in cells):
            table_active = True
            continue
        if not table_active or len(headers) != len(cells):
            headers = [cell[2] for cell in cells]
            table_active = False
            continue
        normalized = {header.casefold() for header in headers}
        allowed = next((fields for fields in table_fields if fields <= normalized), set()) if context else set()
        reason = context
        if peer_context and len(normalized) == len(headers):
            for required, observed in peer_tables:
                if required <= normalized:
                    allowed = observed
                    reason = (
                        f"Named field of the declared {original_date[1]} cohort/peer source comparison; "
                        "not current dispatch, independently verified history or permission. Other columns remain checked."
                    )
                    break
        if snapshot_fields <= normalized:
            values = {header.casefold(): cell[2].strip("`") for header, cell in zip(headers, cells)}
            if (re.fullmatch(r"[\w.-]+(?:/[\w.-]+)+", values["path"])
                    and values["status"] in {"A", "M", "D", "R"}
                    and re.fullmatch(r"[0-7]{6}", values["mode"])
                    and re.fullmatch(r"\d[\d,]*", values["bytes (git lf)"])
                    and re.fullmatch(r"[a-f0-9]{64}", values["sha-256 (git lf blob)"], re.I)
                    and re.search(r"\b[a-f0-9]{7,40}\b", values["commits"], re.I)):
                allowed = snapshot_fields
                reason = "Recorded per-path bytes/hash/commit tuple; source-era observation only, hashes and deletion status not verified."
        for header, (left, right, _) in zip(headers, cells):
            if header.casefold() in allowed:
                observe(start + left, start + right, f"table column: {header}", "source-era table", reason)
            elif reported_changes and header.casefold() in {"changed source", "paths", "changed surface"}:
                cell = line[left:right]
                for reference in re.finditer(r"`([^`]+)`", cell):
                    path = reference[1].replace("\\", "/")
                    removal = re.search(r"\b(?:removed|retired)\b",
                                        cell[:reference.start()].rsplit(";", 1)[-1], re.I)
                    if path in reported_changes or (
                            removal and f"skills/{path}/SKILL.md" in reported_changes):
                        observe(start + left + reference.start(), start + left + reference.end(),
                                f"reported changed-path cell: {header}", "reported change membership",
                                "This exact path/name also occurs in the original report's changed_paths; result columns and current instructions remain checked. No deletion or review is validated.")


def routing_lines(text: str, relative: str, exemptions: list[dict],
                  recorded_comparison_input: str | None = None,
                  observation_errors: list[tuple[int, str]] | None = None,
                  reviewed_spans: list[dict] | None = None) -> list[str]:
    masked = list(text)
    reported_changes: set[str] = set()

    def observe(start, end, field, category, reason, force=False):
        if not force and not has_reference(text[start:end]):
            return
        exemptions.append({
            "path": relative, "line": text.count("\n", 0, start) + 1,
            "end_line": text.count("\n", 0, end - 1) + 1, "field": field,
            "classification": "OBSERVATION", "category": category, "reason": reason,
        })
        masked[start:end] = ["\n" if char == "\n" else " " for char in text[start:end]]

    for span in reviewed_spans or []:
        observe(span["start"], span["end"], "reviewed original source span: " + span["id"],
                span["category"], span["reason"] +
                " Exact original bytes and semantic review declaration match; this is classification only, not live P05/QA/SHIP clearance.",
                force=True)
    if relative == RESIDUAL_REGISTER:
        for match in re.finditer(r"(?m)^<!-- lintel-reviewed-source-spans:v1\r?\n[\s\S]*?^-->", text):
            observe(match.start(), match.end(), "reviewed-span declarations", "classification metadata",
                    "Literal original markers are data for exact checked observations, not workflow invocations.")
    def json_observations(document, offset=0, prefix=""):
        try:
            value, locations = json_locations(document)
        except ValueError:
            return  # Unrecognized/malformed data gains no observation exemption.
        fields = observation_fields(value)
        if (isinstance(value, dict) and value.get("artifact_kind") == "swarm-report"
                and evidence_category(value) and isinstance(value.get("changed_paths"), list)):
            reported_changes.update(path.replace("\\", "/") for path in value["changed_paths"]
                                    if isinstance(path, str))
        if (relative in {f"{COMPARISON_DIR}/results.json", f"{COMPARISON_DIR}/data.js"}
                and comparison_input(value) is not None):
            fields.append((("artifacts", COMPARISON_INPUT), "recorded comparison input",
                           f"Original experiment input field at declared sourceRevision {COMPARISON_REVISION}; data only, not cryptographic binding or current execution. Other fields and executable JS remain checked."))
        for path, category, reason in fields:
            start, end, _ = locations[path]
            field = prefix + "/" + "/".join(str(part).replace("~", "~0").replace("/", "~1") for part in path)
            observe(offset + start, offset + end, field, category, reason)

    if relative.endswith(".json"):
        json_observations(text)
    elif Path(relative).suffix in {".html", ".htm"}:
        for match in re.finditer(
                r"<script\b(?P<attributes>[^>]*)>(?P<json>[\s\S]*?)</script\s*>",
                text, re.IGNORECASE):
            if re.fullmatch(r"""\s+type\s*=\s*(["'])application/json\1\s*""",
                            match["attributes"], re.IGNORECASE):
                json_observations(match["json"], match.start("json"),
                                  "inert HTML script[type=application/json]")
        html_source_observations(text, observe)
    elif relative == f"{COMPARISON_DIR}/data.js":
        assignment = re.match(r"\s*window\.COMPARISON_DATA\s*=\s*", text)
        if assignment:
            try:
                _, end = json.JSONDecoder().raw_decode(text, assignment.end())
            except ValueError:
                pass  # Nonliteral JS is not recognized as serialized result data.
            else:
                json_observations(text[assignment.end():end], assignment.end(), "window.COMPARISON_DATA")
    elif (relative == f"{COMPARISON_DIR}/{COMPARISON_INPUT}"
          and recorded_comparison_input is not None and text == recorded_comparison_input):
        observe(0, len(text), "original prompt copied from results.json/artifacts/with-lintel~1workflow-context.md",
                "recorded comparison input",
                f"Exact text copy of the reserved experiment's recorded input at sourceRevision {COMPARISON_REVISION}; copy agreement is not cryptographic binding or execution. New or changed prompt text receives no exemption.")
    for match in re.finditer(r"(?m)^[ \t]*<!-- lintel-swarm-evidence:v2\r?\n(?P<json>[\s\S]*?)^[ \t]*-->", text):
        json_observations(match["json"], match.start("json"), "lintel-swarm-evidence:v2")

    if Path(relative).suffix in {".md", ".template"}:
        markdown_observations(text, relative, observe, reported_changes)
        def reject(line, reason):
            if observation_errors is None:
                raise ValueError(reason)
            observation_errors.append((line, reason))
        remaining = "".join(masked)
        cohort_yaml_observations(remaining, relative, observe, reject)
    return "".join(masked).splitlines()


def scan(root: Path, check: str = "all", exemptions: list[dict] | None = None) -> list[Finding]:
    root = root.resolve()
    if exemptions is None:
        exemptions = []
    findings: set[Finding] = set()
    reviewed, reviewed_errors = registered_observation_spans(root)
    findings.update(reviewed_errors)

    def add(path: str, line: int, code: str, message: str) -> None:
        findings.add(Finding(path, line, code, message))

    names = set()
    skill_files = sorted((root / "skills").glob("*/SKILL.md"))
    if not skill_files:
        add("skills", 1, "missing-skill-tree", "No canonical SKILL.md files found.")
    for path in skill_files:
        relative = path.relative_to(root).as_posix()
        if any(part.is_symlink() or getattr(part.lstat(), "st_file_attributes", 0) & 0x400
               for part in (path, path.parent, path.parent.parent)):
            add(relative, 1, "linked-path", "Refusing to read a linked workflow source.")
            continue
        header = frontmatter(path.read_text(encoding="utf-8-sig"))
        values = [line.partition(":")[2].strip(" \t'\"") for line in header
                  if line.startswith("name:")]
        if (len(values) != 1 or not re.fullmatch(NAME, values[0])
                or values[0].startswith("li-") or values[0] != path.parent.name):
            add(relative, 1, "invalid-name", "Canonical name must match its bare skill folder.")
        else:
            names.add(values[0])
        if check != "names":
            if path.parent.name.casefold() in RETIRED_COMMANDS:
                add(relative, 1, "retired-entry", "Retired canonical workflow is still discoverable.")
            for line, alias in declared_aliases(header):
                identity = alias.removeprefix("li-").casefold()
                if identity in RETIRED_COMMANDS:
                    add(relative, line, "retired-alias", f"Retired alias is still declared: {alias}")
    if check == "names":
        return sorted(findings)

    def command(relative: str, line: int, name: str, fixture_literal: bool = False) -> None:
        if name.casefold() in RETIRED_COMMANDS:
            add(relative, line, "retired-command", f"Retired workflow reference: {name}")
        elif name == "generate-X":
            exemptions.append({"path": relative, "line": line, "field": "format placeholder: generate-X",
                               "category": "documented template",
                               "reason": "Uppercase X denotes a format slot, not a callable workflow."})
        elif name not in names:
            if fixture_literal:
                exemptions.append({"path": relative, "line": line, "field": f"test literal: {name}",
                                   "category": "synthetic identity",
                                   "reason": "An unknown identity in test code is not a current workflow declaration; retired identities still fail."})
            else:
                add(relative, line, "missing-command", f"No canonical workflow for: {name}")

    recorded_comparison_input = None
    paths = source_files(root)
    paths.sort(key=lambda path: (path.relative_to(root).as_posix() != f"{COMPARISON_DIR}/results.json",
                                 path.as_posix()))
    for path in paths:
        relative = path.relative_to(root).as_posix()
        if relative in SOURCE_EXCEPTIONS:
            exemptions.append({"path": relative, "line": 1, "field": "$file", "category": "declared source exception",
                               "reason": SOURCE_EXCEPTIONS[relative]})
            continue
        if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
            add(relative, 1, "linked-path", "Refusing to read a linked source file.")
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            add(relative, 1, "read-error", f"Cannot inspect text: {type(error).__name__}")
            continue
        if relative == f"{COMPARISON_DIR}/results.json":
            try:
                record, _ = json_locations(text)
            except ValueError:
                pass
            else:
                recorded_comparison_input = comparison_input(record)
        if path.name == "SKILL.md" and path.parent.name.startswith("li-"):
            if path.parent.name[3:].casefold() in RETIRED_COMMANDS:
                add(relative, 1, "retired-entry", "Retired native wrapper is still discoverable.")
        test_code = relative.startswith("tests/") and path.suffix in {".py", ".sh", ".ps1"}
        former_column = False
        observation_errors: list[tuple[int, str]] = []
        try:
            routed = routing_lines(text, relative, exemptions, recorded_comparison_input,
                                   observation_errors, reviewed.get(relative))
        except ValueError as error:
            add(relative, 1, "observation-parse-error", str(error))
            routed = text.splitlines()
        for line, reason in observation_errors:
            add(relative, line, "observation-parse-error", reason)
        for number, original in enumerate(routed, 1):
            line = URL.sub("", original).replace("\\|", "\x00").replace("\\", "/")
            if line.lstrip().startswith("|"):
                columns = line.split("|")
                first = columns[1].strip().casefold()
                if first in FORMER_HEADERS:
                    former_column = True
                if former_column:
                    if first and first not in FORMER_HEADERS and not re.fullmatch(r"[- :]+", first):
                        exemptions.append({"path": relative, "line": number, "field": "migration table, former-entry column",
                                           "category": "retired-name mapping",
                                           "reason": "The replacement column and all prose remain checked."})
                    line = "|" + " " * len(columns[1]) + "|" + "|".join(columns[2:])
            else:
                former_column = False
            for match in EXPLICIT_COMMAND.finditer(line):
                command(relative, number, match["name"], fixture_literal=test_code)
            for match in NATIVE_COMMAND.finditer(line):
                name = match["name"]
                # Bare li-* names can also be utilities or downstream examples.
                # Validate unknown workflows only in an explicit workflow namespace.
                if name.casefold() in RETIRED_COMMANDS:
                    utilities = [root / "bin" / ("li-" + name + suffix)
                                 for suffix in ("", ".py", ".sh", ".ps1")]
                    if any(item.is_file() for item in utilities):
                        exemptions.append({"path": relative, "line": number,
                                           "field": match[0], "category": "existing utility",
                                           "reason": "A bare utility name/message resolves in bin; explicit workflow invocations remain checked."})
                    else:
                        command(relative, number, name)
            for match in BARE_COMMAND.finditer(line):
                name = match["name"].casefold()
                action = re.search(r"\b(?:run|invoke|use|command|workflow|skill)\b",
                                   line[:match.start()], re.I)
                if action and name in RETIRED_COMMANDS and name not in HOST_SLASH_COMMANDS:
                    command(relative, number, name)
            for match in NAMED_SKILL.finditer(line):
                name = match["before"] or match["after"]
                if name.casefold() in RETIRED_COMMANDS:
                    command(relative, number, name)
            for match in SKILL_FIELD.finditer(line):
                if (path.suffix == ".py" and re.search(r"\bskill\s*:\s*" + re.escape(match["name"]) + r"\b", match[0])
                        and not re.search(r"""[:=]\s*["']""", match[0])):
                    exemptions.append({"path": relative, "line": number,
                                       "field": match[0].strip(), "category": "Python annotation",
                                       "reason": "An unquoted Python type annotation is not a literal workflow identity."})
                    continue
                command(relative, number, match["name"], fixture_literal=test_code)
            if (path.suffix in {".md", ".template"}
                    or (path.suffix in {".json", ".yaml", ".yml", ".toml"}
                        and re.search(r"\b(?:description|workflow|skill|method)\b", line, re.I))):
                for match in DISTINCTIVE_COMMAND.finditer(line):
                    command(relative, number, match[1])
            links = list(LINK.finditer(line))
            for match in SKILL_PATH.finditer(line):
                if line[match.end():match.end() + 1] in {"*", "$", "<", "{"}:
                    continue
                name = match["name"]
                identity = name.removeprefix("li:").removeprefix("li-") if match["prefix"] != "skills/" else name.removeprefix("li:")
                if identity.casefold() in RETIRED_COMMANDS:
                    command(relative, number, identity)
                if any(link.start(1) <= match.start() < link.end(1) for link in links):
                    continue
                if not match["tail"] and identity not in names and identity not in RETIRED_COMMANDS:
                    continue
                target = unquote(match[0].rstrip("."))
                if not Path(target).suffix and identity not in names and identity not in RETIRED_COMMANDS:
                    continue  # Prose such as skills/agents/hooks is a list, not a workflow path.
                if not match["tail"]:
                    target += "/SKILL.md"
                if test_code and not re.search(r"\b(?:ROOT|REPO_ROOT|SOURCE_ROOT)\b", line[:match.start()]):
                    exemptions.append({"path": relative, "line": number, "field": f"test path literal: {target}",
                                       "category": "fixture-relative path",
                                       "reason": "No literal source-root consumer on this line; fixture paths need not exist in the source tree. Retired identities still fail."})
                    continue
                if not (root / target).exists():
                    if (test_code and path.suffix == ".py"
                            and re.search(r"\bself\.assertFalse\s*\(", line[:match.start()])
                            and re.search(r"\.exists\(\)\s*\)", line[match.end():])):
                        exemptions.append({"path": relative, "line": number,
                                           "field": target, "category": "negative absence assertion",
                                           "reason": "This assertion requires the resource to remain absent; positive imports/selections still require it."})
                    else:
                        add(relative, number, "missing-path", f"Unresolved workflow path: {target}")
            if path.suffix in {".md", ".template"}:
                for match in links:
                    target = unquote(match[1].strip("<>").split("#", 1)[0])
                    if (not target or re.match(r"[a-z]+:", target, re.I) or target.startswith("/")
                            or any(token in target for token in ("<", ">", "$", "{", "*"))):
                        continue
                    resolved = (path.parent / target).resolve()
                    if resolved.is_relative_to(root) and not resolved.exists():
                        add(relative, number, "missing-path", f"Unresolved local link: {target}")
    return sorted(findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--check", choices=("all", "names"), default="all")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    exemptions: list[dict] = []
    try:
        findings = scan(args.root, args.check, exemptions)
    except (OSError, ValueError) as error:
        parser.exit(2, f"ERROR: command-surface check failed: {error}\n")
    if args.json:
        print(json.dumps({"ok": not findings, "findings": [asdict(item) for item in findings],
                          "exemptions": exemptions}, indent=2))
    else:
        for item in findings:
            print(f"{item.path}:{item.line}: {item.code}: {item.message}")
        for item in exemptions:
            label = item.get("classification", "EXEMPT")
            print(f"{label} {item['path']}:{item['line']} [{item['field']}] ({item['category']}): {item['reason']}")
        print(f"native-command-surface: {'FAIL' if findings else 'PASS'} ({len(findings)} findings)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
