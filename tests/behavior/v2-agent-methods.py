#!/usr/bin/env python3
# component: v2-agent-method-contracts
# implements: ADR-0028, ADR-0040
# intent: .claude/plans/v2-agent-corrections/spec.md
# constraints: source/report-shaped fixtures only; no agents, commands, payloads or live targets
# last_intent_review: 2026-09-30
"""Check declared static methods and their worked reports, not live model efficacy."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
ROLES = {
    "AccessibilityChecker": "engineering", "APIDesigner": "engineering",
    "CodeReviewer": "engineering", "DatabaseDesigner": "engineering",
    "DebugForensics": "engineering", "SanityChecker": "engineering",
    "PrivacyBoundaryAudit": "security", "SecretsScanReviewer": "security",
    "SecurityAuditor": "security", "ThreatModelDrafter": "security",
    "DevOpsToolchain": "devops", "K8sManifestReviewer": "devops", "TerraformReviewer": "devops",
}
BASE_METADATA = {
    "AccessibilityChecker": "ebbf438650ff3f45560699ec0652e9933a9dd1ca1fca3e1d73f46335e4929ddc",
    "APIDesigner": "e20b50a1adc17e323536bf73b0ae0f7a86b0ef0c061a2d09908a132164c1d0ab",
    "CodeReviewer": "f42314f37765ec639f4b185ccacc6a021fdec0e99211630bd47683c4a1c9a768",
    "DatabaseDesigner": "281e91d2129b70c6489be4012a435bfe1b2324521f56f2c037410eb201b91173",
    "DebugForensics": "0176488f575a4de8d66a382d3b58a0996bb069d51a45ee1b13231cdfe0a4af57",
    "SanityChecker": "0ff1b7cbb21dcaa981897f2253cf98888c8c2d92a5d3e4e763260cdb1a3d5feb",
    "PrivacyBoundaryAudit": "471eff2574a10696b0e8e89717d9a12b53e3830432d489d3c0720aeffc7ce869",
    "SecretsScanReviewer": "6865b85bdefb2a5883e6e5adaec5552ca5aff54b02dcfa5943d3fcd45c8772cd",
    "SecurityAuditor": "7ad003a9685d15e94504906757bbb1661e5fdc1f2f3915a682d697e3ac716876",
    "ThreatModelDrafter": "249acc59e9e8104eb6951d340f79307df8bef86a97a549e4a3b5719c9aeaf149",
    "DevOpsToolchain": "5813601441cf1370973a8cbdc4c618a16e36a770338ef543fa08bdeca938fd41",
    "K8sManifestReviewer": "f7118e7a2128ede3e8da274bb6989307574c757fcc8fccea31622252313e6495",
    "TerraformReviewer": "1a76e9844ab6fa9c50b25d008e3b3b9e12cf0070bdc7be831f2f198c8ac815ac",
}


def read(role: str) -> str:
    return (ROOT / "agents" / ROLES[role] / f"{role}.md").read_text(encoding="utf-8")


def report_template(source: str) -> str:
    match = re.search(r"## Report format\s+```\n(.*?)\n```", source, re.DOTALL)
    if match is None:
        raise AssertionError("A report template is required")
    return match[1]


def worked_report(role: str) -> dict[str, dict[str, str]]:
    source = read(role)
    marker = "## Static contract examples"
    if source.count(marker) != 1:
        raise AssertionError(f"{role}: one scoped worked-report section is required")
    section = source.split(marker, 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] == "Case":
            continue
        if len(cells) != 3 or not re.fullmatch(r"[a-z][a-z0-9-]+", cells[0]) or cells[0] in rows:
            raise AssertionError(f"{role}: malformed or duplicate worked-report row")
        rows[cells[0]] = {"outcome": cells[1], "evidence": cells[2]}
    return rows


def check_report(rows: dict, expected: dict[str, str]) -> None:
    if rows.keys() != expected.keys():
        raise AssertionError("Report must retain every selected case and no unrelated case")
    for key, outcome in expected.items():
        row = rows[key]
        if row.get("outcome") != outcome:
            raise AssertionError(f"{key}: unsupported disposition")
        if not isinstance(row.get("evidence"), str) or len(row["evidence"].strip()) < 12:
            raise AssertionError(f"{key}: evidence or next action is required")


def no_value_fragments(report: dict, value: str) -> None:
    """Fixture-only: reject a full short value or an eight-code-point window of a longer one."""
    if not isinstance(value, str) or not value:
        raise AssertionError("The supplied inert fixture value must be a nonempty string")
    width = min(8, len(value))
    fragments = [value[index:index + width] for index in range(len(value) - width + 1)]

    def check(part):
        if isinstance(part, str):
            if any(fragment in part for fragment in fragments):
                raise AssertionError("Report exposes a supplied value or fragment")
        elif isinstance(part, dict):
            for key, item in part.items():
                check(key)
                check(item)
        elif isinstance(part, (list, tuple)):
            for item in part:
                check(item)

    check(report)


def check_case_evidence(rows: dict, required: dict[str, tuple[str, ...]]) -> None:
    for case, clauses in required.items():
        evidence = rows[case]["evidence"].casefold()
        if any(clause.casefold() not in evidence for clause in clauses):
            raise AssertionError(f"{case}: missing source-example evidence distinction")


def contrast(foreground: tuple[float, ...], background: tuple[float, ...]) -> float:
    def luminance(channels):
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
                  for value in channels]
        return sum(weight * value for weight, value in zip((0.2126, 0.7152, 0.0722), linear))
    low, high = sorted((luminance(foreground), luminance(background)))
    return (high + 0.05) / (low + 0.05)


class AgentMethodCases(unittest.TestCase):
    def evidence(self, rows, required):
        check_case_evidence(rows, required)
        for case, clauses in required.items():
            for clause in clauses:
                with self.subTest(case=case, evidence_clause=clause):
                    changed = deepcopy(rows)
                    changed[case]["evidence"] = re.sub(re.escape(clause), "[omitted]",
                                                     rows[case]["evidence"], flags=re.IGNORECASE)
                    self.assertNotEqual(changed, rows)
                    with self.assertRaises(AssertionError):
                        check_case_evidence(changed, required)

    def method(self, role, phrases, expected):
        text = " ".join(read(role).split())
        for phrase in phrases:
            self.assertTrue(phrase.casefold() in text.casefold(),
                            f"{role}: missing method clause {phrase!r}")
        rows = worked_report(role)
        check_report(rows, expected)
        # Each expected outcome must discriminate a contrary or unsupported report.
        for key in expected:
            with self.subTest(role=role, case=key):
                changed = deepcopy(rows)
                changed[key]["outcome"] = "PASS" if expected[key] != "PASS" else "UNVERIFIED"
                with self.assertRaises(AssertionError):
                    check_report(changed, expected)
                changed = deepcopy(rows)
                changed[key]["evidence"] = ""
                with self.assertRaises(AssertionError):
                    check_report(changed, expected)
        with self.assertRaises(AssertionError):
            check_report({}, expected)
        return rows

    def test_accessibility(self):
        rows = self.method("AccessibilityChecker",
                           ("Observation precondition", "authorized operation", "composite",
                            "browser/state", "STATIC/UNVERIFIED"),
                           {"click-only": "FAIL", "alpha-text": "FAIL",
                            "keyboard-unobserved": "STATIC/UNVERIFIED", "at-unobserved": "STATIC/UNVERIFIED"})
        match = re.search(r"black text at alpha ([0-9.]+) over white composites to (#[0-9a-fA-F]{6})",
                          rows["alpha-text"]["evidence"])
        self.assertIsNotNone(match)
        white, black = (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)
        alpha = float(match[1])
        blended = tuple(alpha * fg + (1 - alpha) * bg for fg, bg in zip(black, white))
        self.assertEqual("#" + "".join(f"{round(channel * 255):02x}" for channel in blended), match[2])
        self.assertGreater(contrast(black, white), 4.5)
        self.assertLess(contrast(blended, white), 4.5)
        self.assertIn("2.1.1", rows["click-only"]["evidence"])

    def test_api_consumers(self):
        rows = self.method("APIDesigner",
                           ("Consumer inventory", "compiler", "ContractTestArchitect",
                            "no mandatory additional actor", "request and response"),
                           {"strict-enum": "BREAKING", "tolerant-unrun": "UNVERIFIED",
                            "tolerant-observed": "COMPATIBLE"})
        self.evidence(rows, {
            "strict-enum": ("generated-v1", "rejects unknown enum values", "owner"),
            "tolerant-unrun": ("compiler/runtime pair", "no supplied compatibility result"),
            "tolerant-observed": ("supplied contract result", "this exact", "no wider client claim"),
        })

    def test_code_review(self):
        source = read("CodeReviewer")
        self.assertNotIn("does it do what the commit message says", source)
        self.method("CodeReviewer", ("original acceptance", "Claude Code", "reviewer-owned report",
                                    "verification-only", "corroboration"),
                    {"empty-no-evidence": "INCOMPLETE", "changed-selection": "STALE",
                     "builder-self-review": "NOT INDEPENDENT"})

    def test_database(self):
        rows = self.method("DatabaseDesigner",
                           ("Reader/writer inventory", "MigrationPlanner", "backfill",
                            "lock wait", "no mandatory additional actor"),
                           {"large-required-column": "SEQUENCING REQUIRED", "fast-default": "LOCK REVIEW REQUIRED"})
        self.evidence(rows, {
            "large-required-column": ("NOT NULL", "old writers", "MigrationPlanner", "backfill/validation"),
            "fast-default": ("constant default", "lock wait/hold", "writer compatibility", "unverified"),
        })
        self.assertIn("SchemaArchitect and DataPipelineDesigner remain separate expertise",
                      " ".join(read("DatabaseDesigner").split()))

    def test_forensics(self):
        rows = self.method("DebugForensics", ("Handoff packet", "prior hypotheses", "command/exit",
                                            "owned trial", "do not repeat", "next discriminating"),
                           {"prior-experiment": "RETAIN", "interrupted-trial": "STOP",
                            "elimination-only": "PROBABLE"})
        self.evidence(rows, {
            "prior-experiment": ("rejected by supplied E1", "same snapshot", "command/exit"),
            "interrupted-trial": ("uncertain effects", "journal/owner", "before dependent execution"),
            "elimination-only": ("lacks direct observation", "not a confirmed fix"),
        })

    def test_sanity(self):
        self.method("SanityChecker", ("Comparison boundary", "producer", "consumer",
                                     "material impact", "sampled", "not a release gate"),
                    {"units-mismatch": "MATERIAL FINDING", "domain-synonym": "NO FINDING",
                     "grep-only-unused": "UNVERIFIED"})

    def test_privacy(self):
        rows = self.method("PrivacyBoundaryAudit", ("supplied payload", "policy source/version",
                                                  "UNVERIFIED", "SecurityAuditor", "no live"),
                           {"forbidden-telemetry": "CONFIRMED GAP", "unknown-backup": "UNVERIFIED",
                            "brand-only": "NO VIOLATION ESTABLISHED"})
        self.evidence(rows, {
            "forbidden-telemetry": ("email", "configured endpoint", "forbidden", "policy P-7", "both artifacts"),
            "unknown-backup": ("No backup destination/configuration evidence", "rather than assume"),
            "brand-only": ("provider name alone", "neither emitted fields", "policy applicability"),
        })

    def test_secrets(self):
        rows = self.method("SecretsScanReviewer",
                           ("supplied scanner", "documented inert", "never echo",
                            "no credential validation", "no history-rewrite"),
                           {"documented-marker": "FALSE POSITIVE", "unowned-value": "UNRESOLVED",
                            "rotation-with-receipt": "ROTATED"})
        self.evidence(rows, {
            "documented-marker": ("documented inert test marker", "supplied fixture provenance", "no value or fragment"),
            "unowned-value": ("no owner", "inertness/revocation evidence", "without trying it"),
            "rotation-with-receipt": ("owner's rotation receipt", "same identity", "own disposition"),
        })
        source = read("SecretsScanReviewer")
        for stale in ("BFG", "git-filter-repo", "Force-push approval", "gitleaks-action",
                      "Train team on secrets management (Key Vault", "keep / cleanup"):
            self.assertNotIn(stale, source)

    def test_security(self):
        rows = self.method("SecurityAuditor",
                    ("Defensive static scope", "tenant ownership", "agent-tool trust boundary",
                     "OWASP Top 10:2021", "repair owner", "no live"),
                    {"constant-query": "NO FINDING", "untrusted-process-flow": "SOURCE FINDING",
                     "tenant-from-body": "SOURCE FINDING", "tool-result-authority": "SOURCE FINDING",
                     "unknown-middleware": "UNVERIFIED", "crypto-storage": "SOURCE FINDING",
                     "client-error-disclosure": "SOURCE FINDING", "dependency-license-missing": "UNVERIFIED",
                     "zero-findings-unseen": "UNVERIFIED"})
        self.evidence(rows, {
            "constant-query": ("constant", "no untrusted path", "alone is not a defect"),
            "untrusted-process-flow": ("Supplied source trace", "structured-argument boundary"),
            "tenant-from-body": ("complete supplied path", "without an ownership check"),
            "tool-result-authority": ("untrusted tool-result text", "without scoped authorization"),
            "unknown-middleware": ("selected artifacts omit", "rather than assume"),
            "crypto-storage": ("password-storage", "required", "repair owner"),
            "client-error-disclosure": ("failure branch", "stack trace", "fail-secure"),
            "dependency-license-missing": ("required license/provenance evidence", "coverage gap"),
            "zero-findings-unseen": ("No findings", "not inspected", "coverage gaps"),
        })

    def test_threats(self):
        source = read("ThreatModelDrafter")
        self.assertNotIn("likelihood times impact", source)
        self.assertNotIn("likelihood × impact = risk", source)
        rows = self.method("ThreatModelDrafter",
                    ("mitigation or accepted risk", "verification", "Owner",
                     "privacy", "tool", "policy-defined", "static"),
                    {"inbound-webhook": "MITIGATE", "agent-tool-boundary": "MITIGATE",
                     "ownerless-acceptance": "INCOMPLETE"})
        self.evidence(rows, {
            "inbound-webhook": ("authentication/integrity", "webhook owner", "verification criteria"),
            "agent-tool-boundary": ("action authority", "tool owner", "static verification artifacts"),
            "ownerless-acceptance": ("no authorized decision", "Owner or verification", "instead of treating silence"),
        })
        self.assertIn("| Owner | Verification / status |", report_template(source))

    def test_devops(self):
        source = read("DevOpsToolchain")
        for stale in ("cloud-architect", "alpine runtime", "pino-based", "deploy is Vercel"):
            self.assertNotIn(stale, source)
        self.method("DevOpsToolchain",
                    ("Artifact/trigger split", "GHActionsReviewer", "K8sManifestReviewer",
                     "TerraformReviewer", "secrets on push", "not run"),
                    {"authorized-diff": "ARTIFACT ONLY", "secret-bearing-push": "AUTHORIZATION REQUIRED",
                     "local-runner": "NOT RUN", "unknown-provider": "NEEDS CONTEXT"})

    def test_kubernetes(self):
        source = read("K8sManifestReviewer")
        self.assertNotIn("security-context quartet", source)
        rows = self.method("K8sManifestReviewer",
                    ("Pod Security Standards", "level/version", "serviceAccountName",
                     "automountServiceAccountToken", "RoleBinding", "ClusterRoleBinding",
                     "requests", "Guaranteed", "UNVERIFIED"),
                    {"equal-resources": "NO RATIO FINDING", "admin-token": "SOURCE FINDING",
                     "unspecified-pss": "UNVERIFIED", "readonly-only": "NO PSS FINDING"})
        self.evidence(rows, {
            "equal-resources": ("nonzero CPU/memory requests equal limits", "every container", "not an automatic"),
            "admin-token": ("effective token automount", "ClusterRoleBinding", "without a scoped need"),
            "unspecified-pss": ("level/version evidence is absent", "rather than assume"),
            "readonly-only": ("alone violates no selected PSS control", "separate applicable read-only policy"),
        })

    def test_terraform(self):
        source = read("TerraformReviewer")
        self.assertNotIn("- main.tf:", source)
        self.method("TerraformReviewer",
                    ("Address transition", "moved", "import", "replace", "supplied plan",
                     "do not run", "reusable module"),
                    {"rename-unmapped": "REPLACEMENT RISK", "rename-mapped": "ADDRESS MAPPED",
                     "module-minimum": "NO PINNING FINDING", "provider-execution": "NOT RUN"})


class CompatibilityChecks(unittest.TestCase):
    def test_names_tools_models_memory_and_discovery_remain(self):
        for role, expected in BASE_METADATA.items():
            with self.subTest(role=role):
                source = read(role)
                front = source.split("---", 2)[1]
                stable = "\n".join(line for line in front.splitlines() if not line.startswith("description:"))
                self.assertEqual(hashlib.sha256(stable.encode()).hexdigest(), expected)
                self.assertIn(f"name: {role}", front)

    def test_selected_relative_links_resolve(self):
        for role, category in ROLES.items():
            path = ROOT / "agents" / category / f"{role}.md"
            for target in re.findall(r"\]\(([^ )]+)\)", path.read_text(encoding="utf-8")):
                if target.startswith(("https:", "http:", "#")):
                    continue
                self.assertTrue((path.parent / target.split("#", 1)[0]).is_file(), f"{role}: {target}")


class ReviewRepairCases(unittest.TestCase):
    SECURITY_CLASSES = (
        "input boundary", "secret exposure", "authorization and tenant ownership",
        "agent-tool trust boundary", "cryptographic use", "security configuration",
        "fail-secure and error disclosure", "logging and monitoring",
        "outbound-request targets", "dependency provenance and license",
    )

    def assert_security_coverage(self, source):
        template = report_template(source)
        match = re.search(r"^## Coverage\n(.*?)(?=^## |\Z)", template, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(match, "Q1: report must disclose class coverage")
        coverage = match[1]
        for name in self.SECURITY_CLASSES:
            self.assertIn(f"| {name} | <traced / UNVERIFIED / n/a> |", coverage)
        self.assertIn("zero findings do not establish coverage", template.casefold())

    def test_q1_security_classes_and_coverage_are_explicit(self):
        source = read("SecurityAuditor")
        self.assert_security_coverage(source)
        workflow = " ".join(source.split("## Workflow", 1)[1].split("## Report format", 1)[0].casefold().split())
        for clause in ("password storage", "key handling", "security-relevant defaults",
                       "fail-secure", "error/log disclosure", "outbound-request targets",
                       "dependency provenance/license"):
            self.assertTrue(clause in workflow, f"Q1: missing static inspection clause {clause!r}")
        for name in self.SECURITY_CLASSES:
            with self.subTest(coverage_class=name):
                mutated = re.sub(rf"^\| {re.escape(name)} \|.*\n", "", source, flags=re.MULTILINE)
                self.assertNotEqual(mutated, source)
                with self.assertRaises(AssertionError):
                    self.assert_security_coverage(mutated)

    def assert_owner_history(self, source):
        template = report_template(source)
        table = template.split("### True positive — already rotated", 1)[1].split("### False positive", 1)[0]
        self.assertIn("History disposition owner / recorded decision", table)
        self.assertIn("<owner decision, or pending>", table)
        self.assertNotIn("keep / cleanup", template)
        self.assertIn("authority reference", template)

    def test_q2_rotation_table_records_only_owner_disposition(self):
        source = read("SecretsScanReviewer")
        self.assert_owner_history(source)
        mutated = source.replace("<owner decision, or pending>", "keep / cleanup")
        self.assertNotEqual(mutated, source)
        with self.assertRaises(AssertionError):
            self.assert_owner_history(mutated)

    def assert_material_report(self, source):
        template = report_template(source)
        material = template.find("## Material contract mismatches")
        candidates = template.find("## Unused-code candidates")
        self.assertGreaterEqual(material, 0, "Q3: material findings need a report slot")
        self.assertGreater(candidates, material)
        for field in ("Producer location", "Consumer location", "Invariant", "Consequence",
                      "Evidence / uncertainty", "Repair owner"):
            self.assertIn(field, template[material:candidates])
        for line in template.splitlines():
            if "legacy-helper.ts" in line or "useOldUser.ts" in line:
                self.assertIn("UNVERIFIED CANDIDATE", line)
                self.assertIn("dynamic/public-entry", line)
        self.assertNotIn("no remaining callers)", template)

    def test_q3_material_mismatch_precedes_uncertain_cleanup(self):
        source = read("SanityChecker")
        self.assert_material_report(source)
        self.assertNotIn("estimates cleanup effort so", source)
        self.assertIn("undocumented assumptions", source.split("## Workflow", 1)[1].casefold())
        for old, new in (
            ("## Material contract mismatches", "## Miscellaneous"),
            ("UNVERIFIED CANDIDATE", "Dead code"),
            ("Evidence / uncertainty", "Evidence"),
        ):
            mutated = source.replace(old, new)
            self.assertNotEqual(mutated, source)
            with self.assertRaises(AssertionError):
                self.assert_material_report(mutated)

    def test_q4_inert_report_redaction_handles_short_and_unicode_values(self):
        # A hand-authored report fixture uses the source's row; no agent receives these values.
        row = worked_report("SecretsScanReviewer")["documented-marker"]
        inert_values = (
            "~", "Z7", "inert42", "INERT_NOT_A_CREDENTIAL_FIXTURE_ONLY_42Z",
            "\u2603", "\u6e2c\u8a66", "INERT_\u2603_\u6e2c\u8a66_\u00e4_FIXTURE",
        )
        for index, value in enumerate(inert_values):
            with self.subTest(fixture=index, length=len(value)):
                supplied = {"finding_id": "S-1", "value": value, "provenance": "documented inert fixture"}
                report = {"finding_id": supplied["finding_id"], "triage": deepcopy(row), "value": "[redacted]"}
                no_value_fragments(report, supplied["value"])
                for fragment in (value, value[:8], value[-8:]):
                    leaks = (
                        {**report, "detail": fragment},
                        {**report, "nested": {"messages": [fragment]}},
                        {**report, fragment: "unexpected field"},
                    )
                    for leaked in leaks:
                        # A decoded JSON report must not hide non-ASCII values behind encoding.
                        decoded = json.loads(json.dumps(leaked, ensure_ascii=True))
                        with self.assertRaises(AssertionError):
                            no_value_fragments(decoded, supplied["value"])
        with self.assertRaises(AssertionError):
            no_value_fragments({}, "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args, remaining = parser.parse_known_args()
    ROOT = args.root.resolve()
    print("DOCUMENTARY / INERT REPORT CONTRACTS ONLY: no model, browser, scanner, credential, cloud or target execution.",
          flush=True)
    unittest.main(argv=[__file__, *remaining], verbosity=2)
