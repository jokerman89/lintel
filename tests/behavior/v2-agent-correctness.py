#!/usr/bin/env python3
# component: v2-agent-correctness-contracts
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/v2-findings/spec.md
# constraints: source/template checks only; no models, network, legal findings or host enforcement
# last_intent_review: 2026-10-03
"""Regressions for the seven original V2 agent-correctness clauses, not agent efficacy."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPECIALISTS = (
    "SystemArchitect", "SchemaArchitect", "ContractTestArchitect",
    "ObservabilityArchitect", "CapacityPlanner", "PerfBudgetEnforcer", "DeploymentEngineer",
)
REGULATORY = (
    "compliance/EUAIActReviewer", "compliance/GDPRReviewer",
    "compliance/SOC2Reviewer", "security/ComplianceOfficer",
)
DRAFTERS = (
    "communication/EmailCustomerDrafter", "communication/BlogPostDrafter",
    "communication/LinkedInPostDrafter", "customer/ExecutiveBriefingDrafter",
    "customer/ProposalDrafter", "customer/RFPResponseDrafter",
)
CURRENCY_SLOTS = {
    "<primary source location and provision, or unavailable>": "unavailable",
    "<consolidated text or edition/amendments, or unknown>": "unknown",
    "<effective date and source, or unknown>": "unknown",
    "<application or transition dates per obligation, or unknown>": "unknown",
    "<date of actual source verification, or unknown>": "unknown",
    "<caller-confirmed responsible owner, or unassigned>": "unassigned",
    "<verified for stated scope | unverified>": "unverified",
    "<retrieval/evidence limit and next verification action>": "no current source supplied; request owner verification",
}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def role(name: str) -> str:
    return read(f"agents/{name if '/' in name else 'engineering/' + name}.md")


def normalized(text: str) -> str:
    return " ".join(text.split())


def table_cell(text: str, identifier: str) -> str:
    rows = [line for line in text.splitlines() if line.startswith(f"| `{identifier}` |")]
    if len(rows) != 1:
        raise AssertionError(f"Expected one {identifier} row, got {len(rows)}")
    return rows[0].split("|")[2].strip()


def report(text: str) -> str:
    return text.split("## Report format", 1)[1].split("## Edge cases", 1)[0]


class CorrectnessContracts(unittest.TestCase):
    def require(self, text, *clauses):
        value = normalized(text)
        for clause in clauses:
            self.assertIn(clause, value)

    def render(self, text, slots):
        for slot, value in slots.items():
            self.assertIn(slot, text, f"Missing actual report slot: {slot}")
            text = text.replace(slot, value)
        return text

    def assert_planning_route(self, text, capability):
        cell = table_cell(text, capability)
        self.assertIn("DeploymentEngineer", cell)
        self.assertNotIn("ReleaseEngineer", cell)

    def test_e04_dh_and_sc_dispatch_and_checkpoint_owners(self):
        for module, capabilities in (
            ("dh", ("deployment-plan", "rollback-strategy", "on-call-playbook",
                    "deployment_plan_locked", "on_call_ready")),
            ("sc", ("incident-runbook",)),
        ):
            text = read(f"skills/{module}/SKILL.md")
            for capability in capabilities:
                with self.subTest(module=module, capability=capability):
                    self.assert_planning_route(text, capability)
                    mutant = text.replace("DeploymentEngineer", "ReleaseEngineer")
                    with self.assertRaises(AssertionError):
                        self.assert_planning_route(mutant, capability)
            for capability in set(capabilities) & {"rollback-strategy", "on-call-playbook", "incident-runbook"}:
                self.assertIn("SecurityAuditor", table_cell(text, capability))

    def test_e04_execution_role_is_not_the_planning_default(self):
        text = role("ReleaseEngineer")
        description = re.search(r"(?m)^description: (.*)$", text)[1]
        self.assertIn("explicitly authorized", description)
        self.assertNotIn("squash", description)
        self.require(text, "planning-only", "DeploymentEngineer", "authorization",
                     "actual result/exit", "unapproved")
        self.assertNotIn("**planning-only** (default", text)
        self.require(role("DeploymentEngineer"), "pipeline", "on-call", "incident-runbook",
                     "failed recovery", "SecurityAuditor")

    def test_e04_shared_method_and_legacy_receiver_data_remain_distinct(self):
        method = read("skills/dh/references/decision-methods.md")
        self.assertNotIn("ReleaseEngineer designs the pipeline", method)
        self.require(method, "DeploymentEngineer", "recovery/runbook", "explicitly authorized")
        handoff = read("skills/full-engineering-pass/references/domain-handoff.md")
        self.require(handoff, "Legacy", "planning-only", "not a dispatch instruction",
                     "DeploymentEngineer", "Migrator", "artifact-only")

    def test_e08_planner_renders_only_viable_options_and_can_defer(self):
        text = report(role("Planner"))
        for count, recommendation in ((1, "reuse"), (2, "defer")):
            options = "\n".join(f"### O{i}: viable fixture option" for i in range(count))
            rendered = self.render(text, {
                "<viable approaches>": options, "<chosen option or defer>": recommendation,
                "<evidence, assumptions and uncertainty>": "supplied source; workload unmeasured",
            })
            self.assertEqual(len(re.findall(r"(?m)^### O\d:", rendered)), count)
            self.assertIn(recommendation, rendered)
            for old in ("Three approaches", "Recommendation: B", "option B", "Modify Y.ts (3 hunks)"):
                self.assertNotIn(old, rendered)
        with self.assertRaises(AssertionError):
            self.render(text.replace("<chosen option or defer>", "B"), {"<chosen option or defer>": "defer"})
        self.assertNotIn("three-alternative structure", role("Planner"))

    def assert_perf_contract(self, text):
        output = text.split("## Output shape", 1)[1].split("## Anti-patterns", 1)[0]
        for field in ("baseline_revision:", "candidate_revision:", "measurement_source:",
                      "workload_window:", "sample_count:", "baseline_range_ms:",
                      "candidate_range_ms:", "uncertainty:", "evidence_state:",
                      "threshold_basis:", "missing_baseline_or_zero_samples: unmeasured",
                      "condition:", "required_observation:"):
            self.assertIn(field, output)
        for old in ("5-10%", "10-20%", "≥20%", "# e.g. 10% drift"):
            self.assertNotIn(old, output)
        return output

    def test_e08_perf_template_carries_unmeasured_and_evidence_derived_thresholds(self):
        text = role("PerfBudgetEnforcer")
        output = self.assert_perf_contract(text)
        for status in ("unmeasured", "estimated"):
            rendered = self.render(output, {
                "<observed | estimated | unmeasured>": status,
                "<evidence-derived condition or unmeasured>": "unmeasured",
                "<number or unmeasured>": "unmeasured",
            })
            self.assertIn("evidence_state: " + status, rendered)
            self.assertIn("condition: unmeasured", rendered)
        for field in ("uncertainty:", "threshold_basis:", "missing_baseline_or_zero_samples: unmeasured"):
            mutant = text.replace(field, "omitted:")
            with self.assertRaises(AssertionError):
                self.assert_perf_contract(mutant)

    def test_e08_selected_deployment_and_capacity_templates_do_not_force_numbers_or_option_quota(self):
        output = role("DeploymentEngineer").split("## Output shape", 1)[1].split("## Anti-patterns", 1)[0]
        self.assertNotRegex(output, r"(?m)^\s+(percent|duration_minutes): \d+")
        self.assertNotIn("error_rate < 0.5%", output)
        self.assertIn("evidence_state:", output)
        self.assertNotIn("2-3 mitigation options", role("CapacityPlanner"))

    def test_e09_planner_shell_is_a_task_boundary_not_read_only_enforcement(self):
        text = role("Planner")
        self.assertIn("tools: Read, Grep, Glob, Bash", text)
        self.require(text, "Bash can write", "task restriction, not a sandbox",
                     "side effects", "authorized caller", "not run")
        self.assertNotIn("Read-only — produces the plan", text)

    def test_e09_previous_research_and_accessibility_repairs_remain(self):
        research = role("ResearchSynthesizer")
        self.require(research, "caller-supplied", "does not expand this role's tools",
                     "network request", "externally unverified")
        self.assertNotIn("--include-web", research)
        accessibility = role("AccessibilityChecker")
        self.require(accessibility, "actual observation", "STATIC/UNVERIFIED",
                     "revision and browser/state", "AT announcement")

    def assert_return_contract(self, text):
        footer = text.split("## How operators read your output", 1)[1]
        self.require(footer, "Return proposed", "original work", "package", "leaf",
                     "caller", "mapped destination", "persistence", "checkpoint")
        self.assertNotIn(".claude/runtime/state/", footer)

    def test_e11_read_only_specialists_return_identity_and_do_not_choose_paths(self):
        for name in SPECIALISTS:
            with self.subTest(role=name):
                text = role(name)
                self.assert_return_contract(text)
                with self.assertRaises(AssertionError):
                    self.assert_return_contract(text.replace("mapped destination", "arbitrary file"))
                self.assertIn("domain-handoff.md#module-caller-procedure", text)

    def test_e11_migration_recovery_and_existing_module_persistence_survive(self):
        planner = role("MigrationPlanner")
        self.require(planner, "migration-plan.md", "does not execute", "irreversible",
                     "sql_up", "sql_down", "recovery owner")
        da = read("skills/da/SKILL.md")
        self.require(da, "migration-plan.md", "Unknown migration effects", "missing result means interrupted")
        self.require(read("skills/ta/SKILL.md"), "caller persists returned artifacts")
        self.require(read("skills/tq/SKILL.md"), "perf_budgets_locked", "contract_tests_complete")

    def test_e13_changelog_method_uses_delivered_behavior_not_commit_prefixes(self):
        text = role("ChangelogMaintainer")
        self.require(text, "../../skills/capture/SKILL.md#keep-a-changelog-output")
        self.require(read("skills/capture/SKILL.md"),
                     "](references/reports.md#keep-a-changelog-output)")
        method = read("skills/capture/references/reports.md").split("#### Keep a Changelog output", 1)[1].split("\n### ", 1)[0]
        self.require(method, "`!`", "breaking change", "explicit deprecation", "release diff",
                     "hand-authored", "reverted", "not automatically", "only when authorized")
        for stale in ("Added (feat)", "Changed (refactor", "chore with !-deprecation",
                      "chore with !-remove", 'group as "Other"'):
            self.assertNotIn(stale, text)
            self.assertNotIn(stale, method)
        slots = {"<baseline and release refs>": "fixture-base..fixture-candidate",
                 "<delivered behavior and evidence>": "no delivered change: feature reverted before release",
                 "<proposed | updated with authorized path and actual result | not written>": "not written"}
        rendered = self.render(report(text), slots)
        self.assertIn("Action: not written", rendered)
        with self.assertRaises(AssertionError):
            self.render(report(text).replace("<delivered behavior and evidence>", "feat = Added"), slots)

    def test_e13_existing_ship_caller_already_selects_actual_release_scope(self):
        step = read("skills/ship/SKILL.md").split("### Step 10", 1)[1].split("### Step 11", 1)[0]
        self.require(step, "actual commit/tag range", "delivered work", "only when those outputs are requested",
                     "does not create a tag")
        self.assertNotIn("Conventional", step)

    def assert_currency_template(self, text):
        template = report(text) if "## Report format" in text else text.split("## Output shape", 1)[1]
        for field in ("primary_source:", "consolidated_version:", "effective_date:",
                      "application_date:", "verified_on:", "responsible_owner:",
                      "currency_status:", "verification_limit:"):
            self.assertIn(field, template)
        rendered = self.render(template, CURRENCY_SLOTS)
        self.assertIn("verified_on: unknown", rendered)
        self.assertIn("responsible_owner: unassigned", rendered)
        self.assertIn("currency_status: unverified", rendered)
        return rendered

    def test_f04_every_regulatory_report_retains_unknown_currency_and_owner(self):
        for name in REGULATORY:
            with self.subTest(role=name):
                text = role(name)
                self.assert_currency_template(text)
                self.assertIn("decision-methods.md#regulatory-source-and-currency-record", text)
                for slot in CURRENCY_SLOTS:
                    with self.assertRaises(AssertionError):
                        self.assert_currency_template(text.replace(slot, "invented default"))

    def test_f04_primary_source_method_is_per_framework_not_a_new_policy_schema(self):
        text = read("skills/sc/references/decision-methods.md")
        self.require(text, "## Regulatory source and currency record", "not a new framework",
                     "verified_on", "responsible_owner", "unassigned", "not the report-generation date",
                     "qualified legal", "unavailable", "consolidated")
        for framework, source in (("SOC", "AICPA"), ("GDPR", "EUR-Lex"), ("AI Act", "EUR-Lex"),
                                  ("HIPAA", "HHS"), ("PCI", "PCI SSC"), ("FedRAMP", "NIST"),
                                  ("ISO", "ISO")):
            rows = [line for line in text.splitlines() if line.startswith("|") and framework in line]
            self.assertTrue(any(source in line for line in rows), framework)

    def test_f04_ai_act_template_can_carry_overlapping_duties(self):
        template = report(role("compliance/EUAIActReviewer"))
        for obsolete in ("### If high-risk:", "### If limited-risk:", "### If GPAI:"):
            self.assertNotIn(obsolete, template)
        self.require(template, "assess independently", "overlap", "Article 5", "Article 6",
                     "Article 50", "GPAI", "qualified legal")
        rendered = self.render(template, {
            "<high-risk applicability and evidence>": "requires qualified review of supplied use",
            "<transparency applicability and evidence>": "separate candidate duty; evidence missing",
            "<GPAI applicability and evidence>": "separate provider question; actor unresolved",
        })
        for value in ("requires qualified review", "separate candidate duty", "actor unresolved"):
            self.assertIn(value, rendered)

    def test_f04_preserves_gpai_and_transparency_navigation(self):
        self.require(role("compliance/EUAIActReviewer"), "Annex XI", "Art 53",
                     "deepfake", "emotion-recognition", "notification", "safety evaluation",
                     "cybersecurity", "navigation", "not a pre-approved checklist")

    def assert_voice_contract(self, text):
        self.require(text, "resolve_pack_field voice.gates_active", "resolve_pack_field voice.corpus",
                     "authorized caller", "unavailable", "not configured")
        self.assertNotRegex(text, r"Voice gate via .*compliance")
        self.assertNotIn("voice/compliance gates", text)
        self.assertIn("Internal review checklist", text)

    def test_f05_each_retained_drafter_routes_voice_separately(self):
        for name in DRAFTERS:
            with self.subTest(role=name):
                text = role(name)
                self.assert_voice_contract(text)
                with self.assertRaises(AssertionError):
                    self.assert_voice_contract(text.replace("voice.gates_active", "compliance.hooks"))

    def assert_separate_copy(self, text):
        blocks = re.findall(r"```markdown\n(.*?)\n```", report(text), re.S)
        self.assertEqual(len(blocks), 2, "Customer copy and internal handoff must be separate templates")
        self.assertNotIn("Internal review checklist", blocks[0])
        self.assertNotIn("Voice review from", blocks[0])
        self.assertIn("Internal review checklist", blocks[1])
        self.assertIn("Voice review from", blocks[1])

    def test_f05_rendered_customer_copy_excludes_internal_checklists(self):
        for name in DRAFTERS:
            with self.subTest(role=name):
                text = role(name)
                self.assert_separate_copy(text)
                mutant = text.replace("```markdown\n", "```markdown\n## Internal review checklist\n", 1)
                with self.assertRaises(AssertionError):
                    self.assert_separate_copy(mutant)

    def test_f05_claim_consent_disclosure_and_placement_guards_survive(self):
        for name in DRAFTERS:
            with self.subTest(role=name):
                text = role(name)
                self.require(text, "consent", "disclosure", "commitment", "proof", "separate internal")
        self.require(role("communication/BlogPostDrafter"), "Ratios", "not bypasses", "workload")
        self.require(role("communication/LinkedInPostDrafter"), "percentages", "do not authorize disclosure")
        self.require(role("customer/RFPResponseDrafter"), "original requirement IDs", "responding team",
                     "never hide a capability gap", "source/version/date")

    def test_names_and_declared_tools_are_not_expanded_or_removed(self):
        expected = {f"engineering/{name}": "Read, Grep, Glob" for name in SPECIALISTS}
        expected.update({name: "Read, Grep, Glob, Bash" for name in REGULATORY})
        expected["security/ComplianceOfficer"] = "Read, Grep, Glob"
        expected.update({name: "Read, Bash, Grep, Glob" for name in DRAFTERS})
        expected.update({"engineering/Planner": "Read, Grep, Glob, Bash",
                         "engineering/ReleaseEngineer": "Read, Bash, Edit, Grep, Glob",
                         "engineering/ChangelogMaintainer": "Read, Bash, Edit, Grep"})
        for name, tools in expected.items():
            with self.subTest(role=name):
                front = role(name).split("---", 2)[1]
                self.assertRegex(front, rf"(?m)^name: {name.split('/')[-1]}$")
                self.assertRegex(front, rf"(?m)^tools: {re.escape(tools)}$")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args, remaining = parser.parse_known_args()
    ROOT = args.root.resolve()
    print("DOCUMENTARY/SOURCE TEMPLATE checks only: no model efficacy, legal currency or host enforcement.",
          flush=True)
    unittest.main(argv=[__file__, *remaining], verbosity=2)
