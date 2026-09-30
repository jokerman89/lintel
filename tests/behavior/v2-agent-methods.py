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
    serialized = json.dumps(report)
    if any(value[index:index + 8] in serialized for index in range(len(value) - 7)):
        raise AssertionError("Report exposes a supplied value or fragment")


def contrast(foreground: tuple[float, ...], background: tuple[float, ...]) -> float:
    def luminance(channels):
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
                  for value in channels]
        return sum(weight * value for weight, value in zip((0.2126, 0.7152, 0.0722), linear))
    low, high = sorted((luminance(foreground), luminance(background)))
    return (high + 0.05) / (low + 0.05)


class AgentMethodCases(unittest.TestCase):
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
        white = (1.0, 1.0, 1.0)
        opaque = (0.0, 0.0, 0.0)
        blended = tuple(0.4 * fg + 0.6 * bg for fg, bg in zip(opaque, white))
        self.assertGreater(contrast(opaque, white), 4.5)
        self.assertLess(contrast(blended, white), 4.5)
        rows = self.method("AccessibilityChecker",
                           ("Observation precondition", "authorized operation", "composite",
                            "browser/state", "STATIC/UNVERIFIED"),
                           {"click-only": "FAIL", "alpha-text": "FAIL",
                            "keyboard-unobserved": "STATIC/UNVERIFIED", "at-unobserved": "STATIC/UNVERIFIED"})
        self.assertIn("0.4", rows["alpha-text"]["evidence"])
        self.assertIn("2.1.1", rows["click-only"]["evidence"])

    def test_api_consumers(self):
        clients = {"generated-v1": {"queued", "done"}, "tolerant-v2": {"queued", "done", "unknown"}}
        self.assertNotIn("paused", clients["generated-v1"])
        self.assertIn("unknown", clients["tolerant-v2"])
        rows = self.method("APIDesigner",
                           ("Consumer inventory", "compiler", "ContractTestArchitect",
                            "no mandatory additional actor", "request and response"),
                           {"strict-enum": "BREAKING", "tolerant-unrun": "UNVERIFIED",
                            "tolerant-observed": "COMPATIBLE"})
        self.assertIn("generated-v1", rows["strict-enum"]["evidence"])
        self.assertIn("supplied", rows["tolerant-observed"]["evidence"])

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
        self.assertIn("NOT NULL", rows["large-required-column"]["evidence"])
        self.assertNotIn("absorb SchemaArchitect", read("DatabaseDesigner"))

    def test_forensics(self):
        prior = {"H1": {"status": "rejected", "evidence": "E1"},
                 "H2": {"status": "probable", "evidence": "elimination"}}
        trial = {"owner": "fixture-owner", "state": "interrupted"}
        self.assertEqual(prior["H1"]["evidence"], "E1")
        self.assertNotEqual(prior["H2"]["evidence"], "direct observation")
        self.assertEqual(trial["state"], "interrupted")
        self.method("DebugForensics", ("Handoff packet", "prior hypotheses", "command/exit",
                                     "owned trial", "do not repeat", "next discriminating"),
                    {"prior-experiment": "RETAIN", "interrupted-trial": "STOP",
                     "elimination-only": "PROBABLE"})

    def test_sanity(self):
        self.method("SanityChecker", ("Comparison boundary", "producer", "consumer",
                                     "material impact", "sampled", "not a release gate"),
                    {"units-mismatch": "MATERIAL FINDING", "domain-synonym": "NO FINDING",
                     "grep-only-unused": "UNVERIFIED"})

    def test_privacy(self):
        policy = {"id": "P-7", "forbidden_destinations": ["telemetry-prohibited"]}
        payload = {"field": "email", "destination": "telemetry-prohibited", "evidence": "supplied-fixture"}
        self.assertIn(payload["destination"], policy["forbidden_destinations"])
        self.method("PrivacyBoundaryAudit", ("supplied payload", "policy source/version",
                                           "UNVERIFIED", "SecurityAuditor", "no live"),
                    {"forbidden-telemetry": "CONFIRMED GAP", "unknown-backup": "UNVERIFIED",
                     "brand-only": "NO VIOLATION ESTABLISHED"})

    def test_secrets(self):
        sentinel = "INERT_NOT_A_CREDENTIAL_FIXTURE_ONLY_42Z"
        rows = self.method("SecretsScanReviewer",
                           ("supplied scanner", "documented inert", "never echo",
                            "no credential validation", "no history-rewrite"),
                           {"documented-marker": "FALSE POSITIVE", "unowned-value": "UNRESOLVED",
                            "rotation-with-receipt": "ROTATED"})
        no_value_fragments(rows, sentinel)
        for leak in (sentinel, sentinel[:10], sentinel[-10:]):
            with self.assertRaises(AssertionError):
                no_value_fragments({"finding_id": "S-1", "detail": leak}, sentinel)
        source = read("SecretsScanReviewer")
        for stale in ("BFG", "git-filter-repo", "Force-push approval", "gitleaks-action",
                      "Train team on secrets management (Key Vault"):
            self.assertNotIn(stale, source)

    def test_security(self):
        # This representation is data, not executable source, a payload or a scanner input.
        flows = [
            {"source": "constant", "sink": "query-text", "missing_control": None},
            {"source": "untrusted-input", "sink": "process-launch", "missing_control": "structured-arguments"},
            {"source": "request-tenant", "sink": "object-access", "missing_control": "ownership-check"},
            {"source": "tool-result", "sink": "privileged-action", "missing_control": "authority-separation"},
        ]
        self.assertEqual(sum(row["missing_control"] is not None for row in flows), 3)
        self.method("SecurityAuditor",
                    ("Defensive static scope", "tenant ownership", "agent-tool trust boundary",
                     "OWASP Top 10:2021", "repair owner", "no live"),
                    {"constant-query": "NO FINDING", "untrusted-process-flow": "SOURCE FINDING",
                     "tenant-from-body": "SOURCE FINDING", "tool-result-authority": "SOURCE FINDING",
                     "unknown-middleware": "UNVERIFIED"})

    def test_threats(self):
        source = read("ThreatModelDrafter")
        self.assertNotIn("likelihood times impact", source)
        self.assertNotIn("likelihood × impact = risk", source)
        self.method("ThreatModelDrafter",
                    ("mitigation or accepted risk", "verification", "Owner",
                     "privacy", "tool", "policy-defined", "static"),
                    {"inbound-webhook": "MITIGATE", "agent-tool-boundary": "MITIGATE",
                     "ownerless-acceptance": "INCOMPLETE"})
        threats = [
            {"boundary": "inbound-webhook", "disposition": "mitigate", "owner": "webhook-owner",
             "verification": "authorized signature/replay contract check"},
            {"boundary": "agent-tool-boundary", "disposition": "mitigate", "owner": "tool-owner",
             "verification": "static permission and approval contract check"},
        ]
        for threat in threats:
            self.assertTrue(all(threat[key] for key in ("boundary", "disposition", "owner", "verification")))
        changed = {**threats[0], "owner": ""}
        self.assertFalse(all(changed[key] for key in ("boundary", "disposition", "owner", "verification")))

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
        self.method("K8sManifestReviewer",
                    ("Pod Security Standards", "level/version", "serviceAccountName",
                     "automountServiceAccountToken", "RoleBinding", "ClusterRoleBinding",
                     "requests", "Guaranteed", "UNVERIFIED"),
                    {"equal-resources": "NO RATIO FINDING", "admin-token": "SOURCE FINDING",
                     "unspecified-pss": "UNVERIFIED", "readonly-only": "NO PSS FINDING"})
        fixture = {"containers": [{"request_cpu": 1, "limit_cpu": 1, "request_mem": 256, "limit_mem": 256}]}
        self.assertTrue(all(row["request_cpu"] == row["limit_cpu"] and row["request_mem"] == row["limit_mem"]
                            for row in fixture["containers"]))

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args, remaining = parser.parse_known_args()
    ROOT = args.root.resolve()
    print("DOCUMENTARY / INERT REPORT CONTRACTS ONLY: no model, browser, scanner, credential, cloud or target execution.",
          flush=True)
    unittest.main(argv=[__file__, *remaining], verbosity=2)
