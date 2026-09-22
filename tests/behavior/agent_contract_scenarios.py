#!/usr/bin/env python3
# component: agent-contract-scenarios
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/packages/P09.md
# constraints: documentary checks and synthetic arithmetic only; no host/model execution
# last_intent_review: 2026-09-22

"""Check retained role documents and worked examples, not live agent behavior."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = Path(".claude/engineering/audits/2026-09-20-universal-quality/agents-inventory.md")
REPORT = Path(".claude/plans/universal-implementation/reports/P09-agent-preservation.md")


def read(relative: str | Path) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def contrast(foreground: str, background: str) -> float:
    def luminance(color: str) -> float:
        channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
                  for value in channels]
        return sum(weight * channel for weight, channel in zip((0.2126, 0.7152, 0.0722), linear))

    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def percentile99(samples: list[int]) -> int:
    return sorted(samples)[math.ceil(0.99 * len(samples)) - 1]


class RoleDocuments(unittest.TestCase):
    def test_s01_inventory_and_preservation_rows(self) -> None:
        names = re.findall(r"^\| \[([A-Za-z0-9]+)\]\(", read(INVENTORY), re.MULTILINE)
        self.assertEqual(69, len(names))
        self.assertEqual(69, len(set(names)))
        roles = {path.stem: path for path in (ROOT / "agents").glob("*/*.md")}
        self.assertTrue(set(names) <= roles.keys(), "An original entry name disappeared")
        for name in names:
            text = roles[name].read_text(encoding="utf-8")
            self.assertRegex(text, rf"(?m)^name: {re.escape(name)}$")
        rows = re.findall(r"^\| \[([A-Za-z0-9]+)\]\(", read(REPORT), re.MULTILINE)
        self.assertCountEqual(names, rows, "Exactly one preservation row per original role")

    def test_s02_blank_brief_has_a_planner_before_a_critic(self) -> None:
        arc = read("agents/customer/DemoNarrativeArc.md")
        narrator = read("agents/customer/DemoNarratorJunior.md")
        critic = read("agents/communication/SlideNarrationCritic.md")
        for phrase in ("Plan mode", "Critique mode", "no script", "arc artifact"):
            self.assertIn(phrase, arc)
        self.assertIn("Plan mode", narrator)
        self.assertIn("does not rewrite", critic)
        self.assertNotIn("Sometimes the model takes 30 sec to warm", narrator)
        self.assertNotIn("Acme tested in their pilot", narrator)

    def test_s03_scope_and_authority_remain_distinct(self) -> None:
        checks = {
            "engineering/MigrationPlanner.md": ("does not execute", "irreversible"),
            "engineering/Migrator.md": ("artifact-only", "authorized execution", "lintel-migration-recovery-gate"),
            "engineering/Explorer.md": ("Locate, don't analyze", "excerpts"),
            "engineering/ReadOnly.md": ("Synthesize", "shell"),
            "engineering/ResearchSynthesizer.md": ("accepted ADR", "divergence"),
            "engineering/CodeReviewer.md": ("without fixing", "shared evidence contract"),
            "engineering/TestRunner.md": ("zero executed tests", "unverified"),
            "engineering/ReleaseEngineer.md": ("planning-only", "on-call", "authorization"),
            "customer/RFPResponseDrafter.md": ("responding team", "Customer-visible", "never hide a capability gap"),
        }
        for path, phrases in checks.items():
            with self.subTest(role=path):
                for phrase in phrases:
                    self.assertIn(phrase, read("agents/" + path))

    def test_s04_specific_false_positive_rules_replace_blankets(self) -> None:
        cases = {
            "security/JWTSecurityReviewer.md": ("RFC 8725", "24h max"),
            "security/OAuthFlowReviewer.md": ("RFC 8252", "plain method = P1 fail"),
            "security/PrivacyBoundaryAudit.md": ("unknown", "EU customer data \u2192 only EU-region compute"),
            "security/SecretsScanReviewer.md": ("redacted", "MS incident response"),
            "devops/K8sManifestReviewer.md": ("Guaranteed", "request \u00d7 1.5"),
            "devops/TerraformReviewer.md": ("reusable module", "local \u2014 P1"),
            "frontend/MotionDirector.md": ("no animation", "hero-reveal (always)"),
            "frontend/ShaderEngineer.md": ("device", "95% smaller"),
            "doc-gen/WordTechnicalEditor.md": ("claim ledger", "Limitations count \u2265 Capabilities count"),
        }
        for path, (present, absent) in cases.items():
            with self.subTest(role=path):
                text = read("agents/" + path)
                self.assertIn(present, text)
                self.assertNotIn(absent, text)

    def test_s05_domain_references_are_linked_without_new_runtime(self) -> None:
        for module in ("ta", "da", "sc", "dh", "tq"):
            with self.subTest(module=module):
                skill = read(f"skills/{module}/SKILL.md")
                self.assertIn("(references/decision-methods.md)", skill)
                reference = read(f"skills/{module}/references/decision-methods.md")
                self.assertIn("Synthetic worked example", reference)
                self.assertIn("Sources", reference)
                self.assertIn("https://", reference)
        self.assertNotIn("sum-of-component-p99 + jitter", read("agents/engineering/SystemArchitect.md"))
        self.assertNotIn("consumers ignore unknown", read("agents/engineering/ContractTestArchitect.md"))

    def test_s06_selected_links_resolve(self) -> None:
        documents = list((ROOT / "agents").glob("*/*.md"))
        documents += [ROOT / f"skills/{module}/references/decision-methods.md"
                      for module in ("ta", "da", "sc", "dh", "tq")]
        documents += [ROOT / REPORT, ROOT / ".claude/plans/universal-implementation/reports/P09.md"]
        for document in documents:
            text = document.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^ )]+)\)", text):
                if target.startswith(("http:", "https:", "#")) or "<" in target:
                    continue
                with self.subTest(file=document.name, target=target):
                    self.assertTrue((document.parent / target.split("#")[0]).exists())


class SyntheticExamples(unittest.TestCase):
    def test_e01_percentiles_are_not_additive(self) -> None:
        a = [101] + [1] * 99
        b = [1, 101] + [1] * 98
        self.assertEqual(2, percentile99(a) + percentile99(b))
        self.assertEqual(102, percentile99([x + y for x, y in zip(a, b)]))

    def test_e02_contrast_recomputed_not_copied(self) -> None:
        self.assertLess(contrast("#10b981", "#f8fafc"), 4.5)
        self.assertLess(contrast("#059669", "#f8fafc"), 4.5)
        self.assertGreaterEqual(contrast("#047857", "#f8fafc"), 4.5)
        text = read("agents/engineering/AccessibilityChecker.md")
        for value in ("#10b981", "#059669", "#047857"):
            self.assertIn(value, text)
        self.assertNotIn("4.8:1", text)

    def test_e03_enum_addition_depends_on_consumer(self) -> None:
        old_values = {"queued", "done"}
        new_value = "paused"
        strict_accepts = new_value in old_values
        tolerant_rendering = new_value if new_value in old_values else "unknown"
        self.assertFalse(strict_accepts)
        self.assertEqual("unknown", tolerant_rendering)
        self.assertIn("paused", read("agents/engineering/ContractTestArchitect.md"))

    def test_e04_replay_counts_effects_once(self) -> None:
        events = [("e1", 3), ("e2", 5), ("e1", 3)]
        self.assertEqual(11, sum(value for _, value in events))
        self.assertEqual(8, sum(dict(events).values()))
        self.assertIn("e1", read("skills/da/references/decision-methods.md"))

    def test_e05_slo_and_retry_arithmetic(self) -> None:
        self.assertEqual(27, 3 ** 3)
        self.assertEqual(5000, round(5_000_000 * (1 - 0.999)))
        self.assertAlmostEqual(20, 0.02 / (1 - 0.999))
        self.assertIn("5,000", read("skills/dh/references/decision-methods.md"))

    def test_e06_narration_accounts_for_silence(self) -> None:
        minutes = 240 / 120 + 40 / 60 + 20 / 60
        self.assertEqual(3, minutes)
        self.assertGreater(minutes, 2)
        self.assertIn("240", read("agents/communication/SlideNarrationCritic.md"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args, remaining = parser.parse_known_args()
    ROOT = args.root.resolve()
    print("DOCUMENTARY/SYNTHETIC checks only: no model, browser, database or domain runtime is exercised.",
          flush=True)
    unittest.main(argv=[__file__, *remaining], verbosity=2)
