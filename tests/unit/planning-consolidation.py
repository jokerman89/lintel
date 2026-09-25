# component: planning-consolidation-regressions
# implements: ADR-0026, ADR-0028, ADR-0029
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: synthetic fixtures only; no client execution or independent-review claim
# last_intent_review: 2026-09-25
"""Check planning methods and their real shared work/evidence consumers."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[2]
RETIRED = (
    "office-hours", "plan-ceo-review", "plan-eng-review", "plan-design-review",
    "plan-devex-review", "devex-review", "plan-tune", "autoplan",
)
SURVIVING = ("define", "inspect", "plan", "scope", "discover", "analyze")


def required_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    if not text.strip():
        raise ValueError(f"Required planning source is empty: {path}")
    return text


def skill(name: str) -> str:
    return required_text(ROOT / "skills" / name / "SKILL.md")


def section(text: str, heading: str) -> str:
    start = text.index(heading) + len(heading)
    remainder = text[start:]
    boundary = re.search(r"\n#{1,3} ", remainder)
    return remainder[:boundary.start()] if boundary else remainder


def bash_block(text: str, heading: str) -> str:
    match = re.search(r"```bash\n(.*?)\n```", section(text, heading), re.S)
    if match is None:
        raise ValueError(f"Required executable example missing: {heading}")
    return match.group(1)


class PlanningSourceTests(unittest.TestCase):
    def assert_terms(self, text: str, terms: tuple[str, ...]) -> None:
        text = " ".join(text.split())
        for term in terms:
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_required_sources_and_frontmatter(self):
        for name in SURVIVING:
            with self.subTest(skill=name):
                text = skill(name)
                frontmatter = text.split("---", 2)[1]
                self.assertIn(f"name: {name}\n", frontmatter)
                for field in ("layer", "description", "tools", "voice", "cli_support"):
                    self.assertRegex(frontmatter, rf"(?m)^{field}: \S")
        with self.assertRaises(FileNotFoundError):
            required_text(ROOT / "skills" / "missing-planning-source" / "SKILL.md")

    def test_define_intake_preserves_selection_and_authority(self):
        text = skill("define")
        intake = required_text(ROOT / "skills" / "define" / "references" / "intake.md")
        self.assert_terms(text, (
            "workflow_resume", "li-work-artifacts.py", "--view context",
            "LINTEL_SCOPE_PATH", "FEATURE fast-path", "decision_resolved",
            "original", "existing authorization", "DRAFT", "APPROVED",
            "review-report", "required_policy",
        ))
        self.assert_terms(intake, (
            "Defect or maintenance", "Migration", "Research or comparison",
            "Feature or internal tool", "strategy", "ask nothing",
            "one decision at a time", "not release authority",
        ))

    def test_define_retains_exploration_strategy_and_private_role_boundaries(self):
        text = skill("define")
        self.assert_terms(text, (
            "--scope", "--reference", "--mode", "full|minimal", "--lens",
            "engineering|strategy|venture", "rough idea", "smallest useful outcome",
            "Status quo", "Observed behavior", "Future fit", "Scope alternatives",
            "build, reuse, partner or defer", "role.sensitivity=private",
            "no fixed interview quota", "not an independent",
        ))
        self.assertIn("minimal never skips", text)

    def test_inspect_targets_and_repeatable_lenses(self):
        text = skill("inspect")
        self.assert_terms(text, (
            "--target plan|repo", "default: plan", "default: engineering",
            "--lens engineering|design|devex", "repeatable", "--map",
            "--scope", "--baseline", "--product-type", "--fresh-clone",
            "--time-budget", "read-only", "actual host", "no model",
        ))
        self.assertIn("original", section(text, "### Plan target"))
        self.assertIn("tracked", section(text, "### Repository target"))
        self.assertIn("untracked", section(text, "### Repository target"))

    def test_engineering_review_preserves_short_leaf_and_package_acceptance(self):
        text = section(skill("inspect"), "### Engineering lens")
        self.assert_terms(text, (
            "2-5 minutes", "every leaf", "Decompose now", "Accept with concern",
            "one outcome", "write owner", "dependencies", "aggregate",
            "spec", "quality", "Failure modes", "regression",
            "Architecture", "Code quality", "Tests", "Performance",
            "cli_support", "voice", "Distribution", "What already exists",
        ))

    def test_design_review_preserves_all_six_pillars_without_score_clearance(self):
        text = section(skill("inspect"), "### Design lens")
        self.assert_terms(text, (
            "Information hierarchy", "Interaction states", "Edge cases",
            "Subtraction", "Trust", "Accessibility", "keyboard", "contrast",
            "reduced motion", "advisory", "not browser evidence",
        ))

    def test_devex_review_distinguishes_plan_metrics_and_observed_journeys(self):
        text = section(skill("inspect"), "### Developer-experience lens")
        self.assert_terms(text, (
            "Plan", "Repository", "time-to-hello-world", "Test loop",
            "Deploy", "Local fidelity", "Error", "Documentation",
            "Script ergonomics", "Recovery", "synthetic", "unrun",
            "do not fall back to in-place mutation",
            "Missing baseline means no comparison",
        ))

    def test_plan_routes_to_inspect_and_retains_separate_analysis(self):
        text = skill("plan")
        for lens in ("engineering", "design", "devex"):
            self.assertIn(f"/li:inspect --target plan --lens {lens}", text)
        self.assert_terms(text, (
            "li-work-artifacts.py", "workflow_resume", "qa_requirements",
            "../review/references/evidence.md", "--skill inspect",
            "delegates to /li:analyze", "plan-step8",
            "/li:handoff-size-check --map", "two-stage review",
        ))
        self.assertIn("/li:inspect", skill("analyze"))

    def test_inspection_evidence_is_shared_not_heading_clearance(self):
        text = skill("inspect")
        self.assert_terms(text, (
            "../review/references/evidence.md", "qa_requirements", "required_policy",
            "workflow_resume", "prepare", "li-review-log", "li-review-read",
            "--expected", "--corroboration", "--skill inspect",
            "latest applicable", "release_clearance: false", "snapshot",
            "spec", "quality", "separately attributable", "required_controls",
            "inspect-plan-engineering", "inspect-repo-devex",
        ))
        bash_block(text, "### Persist via first-party")
        self.assertNotRegex(text, r'li-review-log\s+\'\{')

    def test_redundant_sources_are_gone_and_owned_consumers_do_not_route_to_them(self):
        for name in RETIRED:
            with self.subTest(retired=name):
                self.assertFalse((ROOT / "skills" / name / "SKILL.md").exists())
        texts = [skill(name) for name in SURVIVING]
        texts.append(required_text(ROOT / "skills" / "define" / "references" / "intake.md"))
        for text in texts:
            for name in RETIRED:
                with self.subTest(retired=name):
                    self.assertNotIn(name, text)


FIXTURE = runpy.run_path(str(ROOT / "tests" / "unit" / "review_evidence.py"))


class PlanningEvidenceTests(FIXTURE["Fixture"]):
    def observed_inspect(self, *, status="pass", controls=None):
        self.record(status=status, controls=controls)
        self.review["skill"] = "inspect"
        if status == "fail":
            self.review["controls"][0]["status"] = "fail"
        self.corroborate()
        self.write_json(self.request["record_path"], self.review)
        self.env.update(
            review_record=self.record_file.as_posix(),
            review_context=self.expected_file.as_posix(),
            corroboration=self.observed_file.as_posix(),
        )

    def persist_inspect(self, *, ok=0):
        snippet = bash_block(skill("inspect"), "### Persist via first-party")
        return self.run_command(["bash", "-c", snippet], ok=ok)

    def test_actual_inspect_writer_latest_reader_and_qa(self):
        self.observed_inspect()
        self.persist_inspect()
        self.read(skill="inspect", ok=0)
        plan_reader = bash_block(skill("plan"), "### Step 9")
        self.run_command(["bash", "-c", plan_reader], ok=0)
        self.assertEqual(self.qa().returncode, 0)
        self.cli("ship", "--repo", self.repo, "--expected", self.expected_file,
                 "--corroboration", self.observed_file, "--qa", self.qa_file,
                 "--skill", "inspect", ok=0)
        self.observed_inspect(status="fail")
        self.persist_inspect(ok=3)
        self.read(skill="inspect", ok=3)
        self.run_command(["bash", "-c", plan_reader], ok=3)
        self.cli("ship", "--repo", self.repo, "--expected", self.expected_file,
                 "--corroboration", self.observed_file, "--qa", self.qa_file,
                 "--skill", "inspect", ok=3)

    def test_inspect_refuses_stale_selected_content_and_missing_independence(self):
        self.observed_inspect()
        self.persist_inspect()
        self.write("source.txt", "changed after review\n")
        self.read(skill="inspect", ok=3)
        self.write("source.txt", "after\n")
        self.observed_file.unlink()
        result = self.persist_inspect(ok=None)
        self.assertNotEqual(result.returncode, 0)

    def test_immutable_mandatory_qa_cannot_be_downgraded(self):
        self.observed_inspect()
        self.persist_inspect()
        tests = FIXTURE["observed_tests"]()
        tests["requirement"] = "advisory"
        inputs = self.write_json("qa-input.json", {"controls": [tests]})
        result = self.cli("qa", "--repo", self.repo, "--expected", self.expected_file,
                          "--input", inputs, ok=None)
        self.assertNotEqual(result.returncode, 0)

    def test_plan_and_repo_lens_contexts_cannot_reuse_each_other(self):
        lens = "inspect-plan-engineering"
        self.request["required_controls"].append(lens)
        controls = [FIXTURE["control"](name) for name in ("spec", "quality", lens)]
        self.observed_inspect(controls=controls)
        self.persist_inspect()
        for different in ("inspect-repo-engineering", "inspect-plan-design"):
            with self.subTest(required=different):
                self.request["required_controls"][-1] = different
                self.prepare()
                self.read(skill="inspect", ok=3)

    def test_one_lens_cannot_omit_another_required_lens(self):
        self.request["required_controls"].extend(
            ["inspect-plan-engineering", "inspect-plan-design"]
        )
        controls = [
            FIXTURE["control"](name)
            for name in ("spec", "quality", "inspect-plan-engineering")
        ]
        self.observed_inspect(controls=controls)
        self.assertNotEqual(self.persist_inspect(ok=None).returncode, 0)

    def test_unmapped_inspection_never_grants_release_clearance(self):
        selected = self.root / "inspection-snapshot.json"
        snapshot = self.cli("snapshot", "--repo", self.repo, "--base", self.base,
                            "--select", "source.txt")
        selected.write_text(snapshot.stdout, encoding="utf-8")
        controls = self.write_json("inspection-input.json", {
            "controls": [FIXTURE["control"]()],
            "required_policy": FIXTURE["neutral_policy"](),
        })
        result = self.cli("inspect", "--repo", self.repo, "--snapshot", selected,
                          "--input", controls)
        observed = json.loads(result.stdout)
        self.assertEqual(observed["purpose"], "inspection")
        self.assertFalse(observed["release_clearance"])
        self.write("source.txt", "new selected input\n")
        result = self.cli("inspect", "--repo", self.repo, "--snapshot", selected,
                          "--input", controls, ok=None)
        self.assertNotEqual(result.returncode, 0)

    def test_selected_spec_kit_map_keeps_original_task_ids_and_draft_status(self):
        self.write("tasks.md", "- [ ] T014 Keep the existing interface.\n")
        mapping = json.loads((self.repo / "work.json").read_text(encoding="utf-8"))
        mapping.update(workflow="spec-kit", tasks="tasks.md", status="DRAFT")
        self.write_json("work.json", mapping)
        self.write("unrelated.md", "- [ ] T999 Unrelated newer work.\n")
        sibling = deepcopy(mapping)
        sibling["tasks"] = "unrelated.md"
        self.write_json("unrelated-work.json", sibling)
        command = [
            self.env["LINTEL_PYTHON"], ROOT / "bin" / "li-work-artifacts.py",
            "--repo", self.repo, "--map", "work.json", "--view", "context",
        ]
        result = json.loads(self.run_command(command, ok=0).stdout)
        self.assertEqual(set(result["tasks"]), {"T014"})
        self.assertEqual(result["artifacts"]["tasks"], "tasks.md")
        self.assertEqual(result["status"], "DRAFT")
        self.assertFalse(result["release_clearance"])
        (self.repo / "tasks.md").unlink()
        self.assertNotEqual(self.run_command(command).returncode, 0)


if __name__ == "__main__":
    unittest.main()
