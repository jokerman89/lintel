#!/usr/bin/env python3
# component: role-runtime-method-tests
# implements: ADR-0028
# intent: .claude/plans/v2-findings/plan.md
# constraints: source routing, template and retained metadata checks; no model/host invocation
# last_intent_review: 2026-10-03
"""Check one method owner and compatible public views; not agent behavior."""
import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def role(name, category="engineering"):
    return read(f"agents/{category}/{name}.md")


def dispatch(module, capability):
    matches = [line for line in read(f"skills/{module}/SKILL.md").splitlines()
               if line.startswith(f"| `{capability}` |")]
    if len(matches) != 1:
        raise AssertionError(f"expected one {module}/{capability} row, got {len(matches)}")
    return matches[0].split("|")[2].strip()


class RoleRuntimeMethods(unittest.TestCase):
    def test_migrator_report_does_not_preset_live_execution_success(self):
        source = (ROOT / "agents/engineering/Migrator.md").read_text(encoding="utf-8")
        report = source.split("## Report format", 1)[1].split("## Edge cases", 1)[0]
        for preset in ("Production touch: yes", "Per-call auth: confirmed", "5 steps applied"):
            self.assertNotIn(preset, report)
        for required in ("artifact-only", "not performed", "not applied", "not run",
                         "authorization evidence", "actual result and evidence"):
            self.assertIn(required, report)

    def link(self, path, target):
        text = read(path)
        self.assertIn(f"]({target})", text)
        resolved = (ROOT / path).parent / target.split("#")[0]
        self.assertTrue(resolved.is_file(), (path, target))
        return resolved.read_text(encoding="utf-8")

    def test_architect_and_backend_use_one_distributed_boundary_method(self):
        method = "skills/ta/references/decision-methods.md"
        for name in ("Architect", "BackendArchitect"):
            self.link(f"agents/engineering/{name}.md", "../../" + method)
        text = read(method)
        for phrase in ("authoritative writer", "consistency window", "retry/idempotency owner",
                       "outbox", "crashes", "shared exhausted connection pool", "27 downstream attempts"):
            self.assertIn(phrase, text)
        row = dispatch("ta", "boundary-review")
        self.assertTrue(row.startswith("Architect"), row)
        self.assertIn("BackendArchitect", row)
        self.assertIn("choose one", row)
        self.assertNotIn("BackendArchitect + Architect", row)
        self.assertIn("conditional", dispatch("ta", "scaling-plan"))
        backend = role("BackendArchitect")
        self.assertIn("current context", backend)
        self.assertIn("APIDesigner", backend)
        self.assertIn("ObservabilityArchitect", backend)
        self.assertNotIn("## Recommendation: B", backend)

    def test_data_owners_and_read_only_schema_view_do_not_duplicate_dispatch(self):
        for name in ("DatabaseDesigner", "DataPipelineDesigner", "SchemaArchitect"):
            self.link(f"agents/engineering/{name}.md", "../../skills/da/references/decision-methods.md")
        for capability, owner in (("schema-design", "DatabaseDesigner"),
                                  ("sharding-plan", "DatabaseDesigner"),
                                  ("analytics-readiness", "DataPipelineDesigner")):
            row = dispatch("da", capability)
            self.assertTrue(row.startswith(owner), row)
            self.assertIn("SchemaArchitect", row)
            self.assertIn("choose one", row)
            self.assertNotIn(" + SchemaArchitect", row)
        text = read("skills/da/references/decision-methods.md")
        for phrase in ("DatabaseDesigner", "DataPipelineDesigner", "SchemaArchitect",
                       "cardinality", "skew", "co-location", "fact grain", "SCD",
                       "conformed", "authoritative writer", "reconciliation"):
            self.assertIn(phrase, text)
        schema = role("SchemaArchitect")
        self.assertIn("Read-only", schema)
        for field in ("polyglot:", "partition_strategy:", "dimensional_model:",
                      "scd_type:", "conformed:", "mapped destination"):
            self.assertIn(field, schema)

    def test_migration_handoff_retains_single_sequence_and_separate_authority(self):
        row = dispatch("da", "migration-plan")
        self.assertIn("then", row)
        self.assertIn("artifact-only", row)
        self.assertIn("MigrationPlanner", row)
        self.assertIn("Migrator", row)
        designer = role("DatabaseDesigner")
        for phrase in ("[MigrationPlanner's method](MigrationPlanner.md)",
                       "no mandatory additional actor", "Keep one sequence",
                       "EXPLAIN ANALYZE", "does not run DDL/DML"):
            self.assertIn(phrase, " ".join(designer.split()))
        planner = role("MigrationPlanner")
        for phrase in ("does not execute", "irreversible", "original work map",
                       "mapped destination", "stop conditions", "migration-plan.md"):
            self.assertIn(phrase, planner)
        self.assertNotIn("Plan goes to `.claude/runtime/state/da/", planner)
        migrator = role("Migrator")
        self.assertIn("artifact-only", migrator)
        self.assertIn("authorized execution", migrator)
        self.assertIn("unknown partial state", migrator)

    def test_planner_and_readonly_use_existing_owners_in_current_context(self):
        self.link("agents/engineering/Planner.md",
                  "../../skills/plan/SKILL.md#step-2--draft-tasks-and-inspect-engineering")
        self.link("agents/engineering/ReadOnly.md",
                  "../../skills/discover/SKILL.md#step-1--codebase-map-grepglob-targeted")
        for name in ("Planner", "ReadOnly"):
            text = role(name)
            self.assertIn("current context", text)
            self.assertIn("do not", text.casefold())
        self.assertNotIn("primary, task decomposition", read("skills/plan/SKILL.md"))
        self.assertIn("non-mutating planning", role("Planner"))
        self.assertIn("shell permission", role("ReadOnly"))
        self.assertIn("Synthesize", role("ReadOnly"))

    def test_changelog_reuses_capture_without_reentering_the_workflow(self):
        self.link("agents/engineering/ChangelogMaintainer.md",
                  "../../skills/capture/SKILL.md#keep-a-changelog-output")
        owner = self.link("skills/capture/SKILL.md",
                          "references/reports.md#keep-a-changelog-output")
        self.assertEqual(owner.count("#### Keep a Changelog output"), 1)
        section = owner.split("#### Keep a Changelog output", 1)[1].split("\n### ", 1)[0]
        for phrase in ("`!`", "explicit deprecation", "release diff", "hand-authored",
                       "reverted", "not automatically", "only when authorized"):
            self.assertIn(phrase, section)
        self.assertNotIn("1. **Detect format.**", role("ChangelogMaintainer"))
        self.assertIn("current context", role("ChangelogMaintainer"))
        self.assertIn("not written", role("ChangelogMaintainer"))
        self.assertIn("do not dispatch", section)

    def test_existing_context_advice_and_document_fidelity_owners_remain(self):
        self.link("agents/engineering/ContextBudgetAdvisor.md",
                  "../../skills/context-budget/SKILL.md#advice---advice")
        self.link("agents/engineering/DocWriter.md",
                  "../../skills/build/references/documentation-fidelity.md")
        self.assertIn("neither delegates to the other", role("DocWriter"))
        self.assertIn("Do not execute the owner's shell recipes", role("ContextBudgetAdvisor"))

    def test_shared_performance_evidence_keeps_sampling_and_distinct_purposes(self):
        target = "../../skills/tq/references/decision-methods.md#comparable-performance-evidence"
        for path in ("agents/devops/PerformanceAnalyzer.md", "agents/engineering/LatencyAnalyzer.md",
                     "agents/engineering/PerfBudgetEnforcer.md"):
            self.link(path, target)
        self.link("skills/ta/references/decision-methods.md",
                  "../../tq/references/decision-methods.md#comparable-performance-evidence")
        text = read("skills/tq/references/decision-methods.md")
        for phrase in ("sample count", "head/tail sampling", "coordinated-omission",
                       "tail uncertainty", "zero baseline", "do not rerun",
                       "CapacityPlanner", "SystemArchitect", "PerfBudgetEnforcer"):
            self.assertIn(phrase, text)
        row = dispatch("tq", "perf-budget-spec")
        self.assertTrue(row.startswith("PerfBudgetEnforcer"), row)
        self.assertIn("missing", row)
        self.assertIn("one", row)
        self.assertNotIn("LatencyAnalyzer + PerfBudgetEnforcer", row)
        self.assertNotIn("Top 3 most-frequent", role("LatencyAnalyzer"))
        for phrase in ("missing_baseline_or_zero_samples: unmeasured", "baseline_range_ms:",
                       "actual_gate_evidence:", "95-112", "101-114"):
            self.assertIn(phrase, role("PerfBudgetEnforcer"))

    def test_helpers_have_single_implementations_and_trusted_callers(self):
        self.link("agents/engineering/RegressionDetective.md", "../../bin/li-isolated-bisect")
        self.link("skills/diagnose/SKILL.md", "../../bin/li-isolated-bisect")
        self.link("agents/engineering/Migrator.md", "../../lib/migration-recovery.sh")
        self.assertIn("${LINTEL_SOURCE_ROOT:?select trusted source}/bin/li-isolated-bisect",
                      read("skills/diagnose/SKILL.md"))
        self.assertNotIn("finish_bisect() {", role("RegressionDetective"))
        self.assertNotIn("migration_recovery_allowed() {", role("Migrator"))
        bisect = read("bin/li-isolated-bisect")
        for signal, code in (("HUP", 129), ("INT", 130), ("TERM", 143)):
            self.assertIn(f"trap 'exit {code}' {signal}", bisect)
        self.assertIn("trap finish_bisect EXIT", bisect)
        self.assertIn("trial_git_options=(-c core.longpaths=true)", bisect)
        self.assertNotIn("core.hooksPath", bisect)
        original_tests = read("tests/unit/context-safety.py")
        self.assertNotIn('re.search(r"```bash\\n(# lintel-isolated-bisect', original_tests)
        self.assertNotIn('re.search(r"```bash\\n(# lintel-migration-recovery-gate', original_tests)

    def test_client_metadata_keeps_copilot_hints_and_states_real_evidence_limits(self):
        for path in (ROOT / "agents").glob("*/*.md"):
            header = path.read_text(encoding="utf-8").split("---", 2)[1]
            self.assertIn("- cli: copilot", header, str(path))
        universal = read("shims/universal/ADAPTER.md")
        for phrase in ("Legacy role metadata", "`tier`", "`memory`", "`model`",
                       "license evidence", "not a permission grant", "cli_support"):
            self.assertIn(phrase, universal)
        template = read("scaffolding/01-foundation/TEMPLATE-agent.md")
        self.assertNotIn("no first-class subagent mechanism", template)
        self.assertNotIn("safe to bundle into any repo", template)
        self.assertIn("not runtime evidence", template)

    def test_derivative_attribution_matches_the_retained_record_without_a_new_date(self):
        spec = importlib.util.spec_from_file_location("role_catalog", ROOT / "bin/li-catalog.py")
        catalog = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(catalog)
        record = catalog.load_text(read("install/upstream-sources.yaml"))["bundled_materials"][
            "design-dna-example-profile"]
        text = role("FrontendArchitect", "frontend")
        header = text.split("---", 2)[1]
        self.assertIn("upstream_url: " + record["source"], header)
        self.assertNotIn("last_verified:", header)
        self.assertIsNone(record["import_commit"])
        self.link("agents/frontend/FrontendArchitect.md", "../../" + record["notice"])
        self.link("agents/frontend/FrontendArchitect.md", "../../" + record["attribution"])
        self.assertIn("import revision remains unknown", text)
        self.assertIn("no new upstream verification", text)


if __name__ == "__main__":
    print("Source method/routing contracts only; helper and renderer execution are tested separately.",
          flush=True)
    unittest.main(verbosity=2)
