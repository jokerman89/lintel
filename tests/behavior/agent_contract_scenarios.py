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
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT
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
        self.assertTrue(names, "The original public-name inventory must not be empty")
        self.assertEqual(len(names), len({name.casefold() for name in names}),
                         "Original role names must be unique, including case")
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

class RenderedRoleContracts(unittest.TestCase):
    """Instantiate retained source templates; these are not live-agent observations."""

    def yaml_report(self, agent, root_key, source_text=None):
        sys.path.insert(0, str(SOURCE / "lib"))
        from profile_context import parse_manifest
        blocks = re.findall(r"```yaml\n(.*?)\n```",
                            read(agent) if source_text is None else source_text, re.S)
        block = next(value for value in blocks if value.lstrip().startswith(root_key + ":"))
        block = block.replace("<name>", "fixture").replace("<number>", "10")
        block = block.replace("<lower>", "10").replace("<upper>", "25")
        block = re.sub(r"<[^>\n]+>", "fixture", block)
        if block.startswith(root_key + ":\n  - "):
            # Check the declared single-item example, then use the existing mapping parser.
            self.assertEqual(len(re.findall(r"(?m)^  - ", block)), 1)
            item = "\n".join(line[4:] for line in block.splitlines()[1:])
            return {root_key: [parse_manifest(item)]}
        return parse_manifest(block)

    def test_architect_template_accepts_two_viable_options_without_a_fixed_winner(self):
        text = read("agents/engineering/Architect.md")
        report = text.split("## Report format", 1)[1].split("## Edge cases", 1)[0]
        rendered = report.replace("<viable alternatives>",
                                  "### A - Existing component\nReuse the local invariant.\n"
                                  "### B - New component\nAdditional operational ownership.")
        rendered = rendered.replace("<chosen option or defer>", "A")
        options = re.findall(r"(?m)^### ([A-Z]) [^\n]+", rendered)
        self.assertEqual(options, ["A", "B"])
        recommendation = rendered.split("## Recommendation", 1)[1].split("## Interface", 1)[0]
        self.assertRegex(recommendation.strip(), r"^A because")
        self.assertNotIn("## Three alternatives", rendered)

    def test_research_template_keeps_external_unavailability_and_caller_sources_distinct(self):
        text = read("agents/engineering/ResearchSynthesizer.md")
        template = text.split("## Report format", 1)[1].split("## Edge cases", 1)[0]
        for value in ("unavailable; no permitted binding",
                      "caller supplied primary source; recorded publisher/date"):
            rendered = template.replace("<external source status and evidence or limitation>", value)
            self.assertIn("External: " + value, rendered)
            self.assertNotIn("--include-web", rendered)
        self.assertIn("does not expand this role's tools", text)

    def test_capacity_template_carries_range_source_and_falsifying_check(self):
        report = self.yaml_report("agents/engineering/CapacityPlanner.md", "capacity_model")
        component = report["capacity_model"]["per_component"]["component_fixture"]
        self.assertEqual(component["projection_range_ms"], [10, 25])
        for key in ("measurement_source", "workload_window", "projection_assumptions",
                    "falsifying_check", "evidence_state"):
            self.assertTrue(component[key], key)
        self.assertNotIn("top-3 components", read("agents/engineering/CapacityPlanner.md"))

    def test_sli_template_preserves_denominator_and_missing_data(self):
        report = self.yaml_report("agents/engineering/ObservabilityArchitect.md", "slis")
        self.assert_sli_contract(report)

    def assert_sli_contract(self, report):
        sli = report["slis"][0]
        for key in ("eligible_events", "good_events", "no_data_behavior", "verification"):
            self.assertIn(key, sli)
        self.assertTrue(sli["eligible_events"])
        self.assertTrue(sli["good_events"])
        self.assertEqual(sli["no_data_behavior"], "unknown")
        self.assertTrue(sli["verification"])

    def test_actual_sli_template_omissions_and_healthy_no_data_are_rejected(self):
        path = "agents/engineering/ObservabilityArchitect.md"
        original = read(path)
        for field in ("eligible_events", "good_events", "verification"):
            mutated, count = re.subn(rf"(?m)^    {field}:.*\n", "", original)
            self.assertGreater(count, 0)
            with self.subTest(removed=field), self.assertRaises(AssertionError):
                self.assert_sli_contract(self.yaml_report(path, "slis", mutated))
        mutated, count = re.subn(r"(?m)^    no_data_behavior:.*$", "    no_data_behavior: healthy", original)
        self.assertEqual(count, 1)
        with self.assertRaises(AssertionError):
            self.assert_sli_contract(self.yaml_report(path, "slis", mutated))

    def report_template(self, path, source_text=None):
        text = read(path) if source_text is None else source_text
        return text.split("## Report format", 1)[1].split("## Edge cases", 1)[0]

    def assert_rendered_fields(self, template, values):
        rendered = template
        for token, value in values.items():
            self.assertIn(token, template)
            rendered = rendered.replace(token, value)
        for value in values.values():
            self.assertIn(value, rendered)
        return rendered

    def test_dependency_template_retains_contrary_exposure_and_policy_cases(self):
        template = self.report_template("agents/security/DependencyAuditor.md")
        common = {"<advisory id>": "fixture-advisory", "<scanner rank>": "critical",
                  "<affected package and artifact scope>": "fixture-package / selected build"}
        cases = (
            {"<exposure or applicability>": "not applicable to selected runtime",
             "<evidence state and reference>": "grounded: fixture-scope-proof",
             "<requirement and policy source>": "advisory: fixture-policy",
             "<disposition and next action>": "not a release clearance; retain observation"},
            {"<exposure or applicability>": "unknown",
             "<evidence state and reference>": "unverified: runtime inventory absent",
             "<requirement and policy source>": "mandatory: fixture-policy",
             "<disposition and next action>": "blocked pending required evidence"},
        )
        for case in cases:
            rendered = self.assert_rendered_fields(template, {**common, **case})
            self.assertIn(case["<exposure or applicability>"], rendered)
        without_evidence = template.replace("<evidence state and reference>", "")
        with self.assertRaises(AssertionError):
            self.assert_rendered_fields(without_evidence, {**common, **cases[1]})

    def test_sbom_template_does_not_hide_source_only_or_mismatched_inventory(self):
        template = self.report_template("agents/security/SBOMAuditor.md")
        values = {
            "<inventory artifact digest and scope>": "source-digest-A / source-only",
            "<requested artifact digest and scope>": "image-digest-B / runtime",
            "<inventory coverage and unmet observations>": "unverified runtime coverage; request image inventory",
        }
        rendered = self.assert_rendered_fields(template, values)
        self.assertIn("source-only", rendered)
        self.assertIn("unverified runtime coverage", rendered)
        with self.assertRaises(AssertionError):
            self.assert_rendered_fields(
                template.replace("<inventory coverage and unmet observations>", ""), values)

    def test_oauth_template_keeps_missing_token_or_provider_evidence_explicit(self):
        template = self.report_template("agents/security/OAuthFlowReviewer.md")
        for missing in ("token signature/claims", "provider configuration"):
            values = {
                "<pass | warning | fail | unverified>": "unverified",
                "<token internals, provider configuration or other required observations not supplied>": missing,
                "<supplied flow evidence and source>": "fixture flow binding observations",
                "<required evidence owner or authorized handoff; not performed here>": "identity owner; not performed",
            }
            rendered = self.assert_rendered_fields(template, values)
            self.assertIn("- Assessment: unverified", rendered)
            self.assertIn(missing, rendered)
            with self.assertRaises(AssertionError):
                self.assert_rendered_fields(
                    template.replace("<required evidence owner or authorized handoff; not performed here>", ""),
                    values)

    def test_system_templates_emit_source_and_verification_not_just_prose(self):
        nfr = self.yaml_report("agents/engineering/SystemArchitect.md", "nfr_spec")["nfr_spec"]
        for item in (nfr["latency"]["critical_journey_fixture"],
                     nfr["throughput"]["endpoint_fixture"],
                     nfr["error_rate"]["endpoint_fixture"], nfr["availability"],
                     nfr["observability"]["per_component"]):
            self.assertTrue(item["source"])
            self.assertTrue(item["verification"])
            self.assertTrue(item["evidence_state"])
        invariants = self.yaml_report("agents/engineering/SystemArchitect.md", "invariants")
        self.assertTrue(invariants["invariants"][0]["verification"])

    def test_pipeline_stage_contracts_retain_lateness_identity_and_lineage(self):
        text = read("agents/engineering/DataPipelineDesigner.md")
        report = text.split("## Report format", 1)[1].split("## Edge cases", 1)[0]
        rows = ("| ingest | event time | wm-1 | quarantine late data | event-id | "
                "deduplicate by event-id | intake owner | source-v1 / replay-case |\n"
                "| aggregate | event time | wm-2 | correction pane | event-id + pane | "
                "replace pane atomically | aggregate owner | transform-v2 / late-case |")
        rendered = report.replace("<stage contract rows>", rows)
        actual = [line for line in rendered.splitlines() if line.startswith("| ingest |")
                  or line.startswith("| aggregate |")]
        self.assertEqual(len(actual), 2)
        for row in actual:
            self.assertEqual(len(row.strip("|").split("|")), 8)
        for label in ("Watermark", "Late-data policy", "Replay identity", "Sink idempotency",
                      "Rejected/conflicting owner", "Source / verification"):
            self.assertIn(label, rendered)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args, remaining = parser.parse_known_args()
    ROOT = args.root.resolve()
    print("DOCUMENTARY/SYNTHETIC checks only: no model, browser, database or domain runtime is exercised.",
          flush=True)
    unittest.main(argv=[__file__, *remaining], verbosity=2)
