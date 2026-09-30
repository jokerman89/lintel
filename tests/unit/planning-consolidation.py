# component: planning-consolidation-regressions
# implements: ADR-0026, ADR-0028, ADR-0029, ADR-0034
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: synthetic fixtures only; no client execution or independent-review claim
# last_intent_review: 2026-09-29
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

    def rendered_premise_row(self, source_text):
        self.assertIn("#### Conditional pivotal premise record", source_text)
        block = source_text.split("#### Conditional pivotal premise record", 1)[1].split(
            "### 7.", 1)[0]
        row = next(line for line in block.splitlines() if line.startswith("| <premise"))
        values = {
            "<premise and original decision ID>": "D014: current API remains compatible",
            "<constraint or assumption and basis>": "assumption; target runtime behavior is unknown",
            "<evidence or source; unknown if absent>": "source contract R1; target check unrun",
            "<observable falsifier>": "target rejects the existing response shape",
            "<smallest authorized check or proposed-unapproved check>": "proposed owned compatibility fixture; not run",
            "<decision consequence and owner>": "maintainer chooses adapter or defers migration",
            "<observed, unknown or check-not-run status>": "unknown; check not run",
        }
        for token, value in values.items():
            row = row.replace(token, value)
        return row, list(values.values())

    def assert_premise_row(self, row, expected):
        self.assertEqual([cell.strip() for cell in row.strip("|").split("|")], expected)

    def test_define_template_preserves_falsifier_authority_and_unknown_status(self):
        original = skill("define")
        row, expected = self.rendered_premise_row(original)
        self.assert_premise_row(row, expected)
        selected_design = "# Existing design\nOriginal task: T014\n\n" + row + "\n"
        self.assertIn("Original task: T014", selected_design)
        self.assertIn("check not run", selected_design)
        for source_text in (
            original.replace("<observable falsifier>", ""),
            original.replace("<smallest authorized check or proposed-unapproved check>", ""),
            original.replace("<observed, unknown or check-not-run status>", "verified"),
        ):
            with self.subTest(mutation=source_text[-80:]), self.assertRaises(AssertionError):
                mutated, _ = self.rendered_premise_row(source_text)
                self.assert_premise_row(mutated, expected)

    def test_define_condition_does_not_reinterview_approved_work_or_expand_migration(self):
        text = skill("define")
        self.assert_terms(text, (
            "only unsupported or contested pivotal premises",
            "omit the table", "no additional question or proof exercise",
            "approved T014", "proposed check is not permission",
            "chosen_reading", "decision_resolved",
            "compatibility-only migration", "missing compatibility facts",
        ))
        intake = required_text(ROOT / "skills/define/references/intake.md")
        self.assertIn("If that list is empty, ask nothing", intake)
        self.assertIn('"Implement approved T014"', intake)
        self.assertIn("not questions about startup demand or payment", intake)

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
            "/li:context-budget --handoff --map", "two-stage review",
        ))
        self.assertIn("/li:inspect", skill("analyze"))

    def test_native_finalization_and_capture_keep_one_approval_source(self):
        plan = skill("plan")
        self.assert_terms(section(plan, "### Step 10"), (
            "actual retained authorization", "approval source and scope",
            "author or inspect these documents is not approval",
            "does not extend implementation or publication authority",
            "selected work map APPROVED", "does not create approval",
            "does not replace required review evidence",
        ))
        self.assertNotIn("draft, finalized in CAPTURE", plan)
        self.assert_terms(skill("capture"), (
            "A DRAFT remains DRAFT", "CAPTURE does not approve drafts",
            "existing approval is not erased", "Planned or unrun checks",
        ))
        prompt = required_text(ROOT / "scaffolding/01-foundation/templates/plan/prompt.template.md")
        self.assertIn("stop before BUILD", " ".join(prompt.split()))
        self.assertIn("tasks.md remains authoritative", " ".join(prompt.split()))
        self.assertNotIn("skip DEFINE/PLAN, they're done", prompt)

    def test_handoff_callers_use_budget_owner_without_weakening_boundaries(self):
        for name in ("plan", "capture", "spec-kit"):
            with self.subTest(skill=name):
                text = skill(name)
                self.assertIn("/li:context-budget --handoff --map", text)
                self.assertNotIn("/li:handoff-size-check --map", text)
        for name in ("plan", "capture"):
            self.assert_terms(skill(name), (
                "--skip-handoff-size-check", "SKIP_HANDOFF_SIZE_CHECK=1",
                "required limit", "unknown",
            ))
        owner = skill("context-budget")
        self.assert_terms(owner, (
            "workflow_resume", "original work", "leaf", "not-supplied",
            "never a pass", "required policy", "No extra agent",
        ))

    def test_budget_optional_observation_agrees_with_catalog_producer(self):
        catalog = json.loads(required_text(ROOT / "lib/event-catalog.json"))
        event = catalog["categories"]["handoff-size-checks"]["kinds"]["size_check"]
        self.assertEqual(event["producers"],
                         ["instruction-only:skills/context-budget/SKILL.md"])
        owner = skill("context-budget")
        optional = section(owner, "### Optional handoff observation")
        self.assert_terms(optional, ("separately authorized", "opt-in", "actual", "never"))
        example = bash_block(owner, "### Optional handoff observation")
        call = "audit_log handoff-size-checks size_check"
        self.assertRegex(example, r"(?m)^audit_log handoff-size-checks size_check\b")
        self.assertEqual(owner.count(call), 1)
        for field in event["fields"]:
            self.assertIn(field + "=", example)
        self.assertNotIn(call, skill("handoff-size-check"))
        route = required_text(ROOT / "skills/context-budget/references/route.sh")
        self.assertNotIn("audit_log", route)

    def test_budget_route_has_portable_empty_array_expansion(self):
        route = required_text(ROOT / "skills/context-budget/references/route.sh")
        portable = '${arguments[@]+' + '"${arguments[@]}"' + '}'
        self.assertEqual(route.count(portable), 2)
        self.assertNotIn(' "${arguments[@]}"', route)

    def test_budget_owner_preserves_authority_and_small_work_guidance(self):
        self.assert_terms(skill("context-budget"), (
            "Do not silently cut authority files",
            "Routine small edits need no extra",
        ))

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
    def instantiate_native_drafts(self):
        paths = {}
        for role in ("spec", "plan", "prompt"):
            template = required_text(
                ROOT / "scaffolding/01-foundation/templates/plan" / (role + ".template.md"))
            rendered = template.replace("<wedge title>", "Fixture draft").replace("<date>", "2026-09-29")
            relative = f"draft/{role}.md"
            self.write(relative, rendered)
            paths[role] = relative
        mapping = {
            "schema_version": 1, "workflow": "lintel", "status": "DRAFT",
            **paths, "tasks": paths["plan"],
        }
        self.write_json("draft/work.json", mapping)
        return paths, mapping

    def actual_plan_artifact_gate(self, selected, *, ok):
        text = skill("plan").split("### Step 11a", 1)[1].split("\n### Step 11b", 1)[0]
        block = re.search(r"```bash\n(.*?)\n```", text, re.S)
        self.assertIsNotNone(block, "The actual PLAN completeness recipe is required")
        recipe = block[1]
        python = recipe.split("<<'PY'\n", 1)[1].split("\nPY\n", 1)[0]
        return self.run_command(
            [self.env["LINTEL_PYTHON"], "-B", "-", ROOT / "bin/li-work-artifacts.py",
             self.repo, self.repo / selected],
            input=python, ok=ok,
        )

    def test_instantiated_native_files_start_draft_and_reader_does_not_promote(self):
        paths, mapping = self.instantiate_native_drafts()
        before = {path: (self.repo / path).read_bytes() for path in [*paths.values(), "draft/work.json"]}
        for role, path in paths.items():
            with self.subTest(role=role):
                text = (self.repo / path).read_text(encoding="utf-8")
                status = re.search(r"(?m)^\*\*Status:\*\*\s+(\S+)", text)
                self.assertIsNotNone(status, f"Generated {role} has no explicit status")
                self.assertEqual(status[1], "DRAFT")
        read = self.run_command(
            [self.env["LINTEL_PYTHON"], ROOT / "bin/li-work-artifacts.py",
             "--repo", self.repo, "--map", "draft/work.json"], ok=0,
        )
        self.assertEqual(json.loads(read.stdout), mapping)
        blocked = self.actual_plan_artifact_gate("draft/work.json", ok=1)
        self.assertIn("selected work must be APPROVED", blocked.stderr)
        self.assertEqual(before, {path: (self.repo / path).read_bytes() for path in before})

    def test_actual_plan_gate_rejects_approval_headings_without_approved_map(self):
        paths, _ = self.instantiate_native_drafts()
        for path in paths.values():
            text = (self.repo / path).read_text(encoding="utf-8")
            self.write(path, "**Status:** APPROVED\n" + text)
        before = {path: (self.repo / path).read_bytes() for path in [*paths.values(), "draft/work.json"]}
        blocked = self.actual_plan_artifact_gate("draft/work.json", ok=1)
        self.assertIn("selected work must be APPROVED", blocked.stderr)
        self.assertEqual(before, {path: (self.repo / path).read_bytes() for path in before})

    def test_recorded_existing_approval_preserves_artifacts_and_original_ids(self):
        # The fixture supplies recorded approval; this gate does not authenticate a human grant.
        self.write("plan.md", "### T017 Keep the existing interface\n\n- [ ] Verify the original R1.\n")
        before = {path: (self.repo / path).read_bytes()
                  for path in ("work.json", "spec.md", "plan.md", "prompt.md")}
        self.actual_plan_artifact_gate("work.json", ok=0)
        read = self.run_command(
            [self.env["LINTEL_PYTHON"], ROOT / "bin/li-work-artifacts.py",
             "--repo", self.repo, "--map", "work.json", "--view", "context"], ok=0,
        )
        context = json.loads(read.stdout)
        self.assertEqual(context["status"], "APPROVED")
        self.assertEqual(set(context["tasks"]), {"T017"})
        self.assertEqual(context["artifacts"]["tasks"], "plan.md")
        self.assertFalse(context["release_clearance"])
        self.assertEqual(before, {path: (self.repo / path).read_bytes() for path in before})

    def test_rendered_spec_links_observable_acceptance_to_original_verification(self):
        template = required_text(ROOT / "scaffolding/01-foundation/templates/plan/spec.template.md")
        cases = {
            "R1": ("T017", "Empty input is rejected without writing data.", "empty-input"),
            "R2": ("T023", "Valid input preserves the existing value.", "valid-input"),
        }
        lines = []
        for line in template.replace("<wedge title>", "Input validation").splitlines():
            for requirement, (task, expected_result, anchor) in cases.items():
                if not line.startswith(f"| {requirement} |"):
                    continue
                for placeholder, value in {
                    "<requirement>": f"Validate {requirement}",
                    "<T1 / 1.1 / 1.1.a>": task, "<\u2026>": task,
                    "<expected result or original criterion link>": expected_result,
                    "<verification reference and evidence state>":
                        f"[Planned check](checks.md#{anchor}); evidence not run",
                }.items():
                    line = line.replace(placeholder, value)
            lines.append(line)
        rendered = "\n".join(lines) + "\n"
        self.write("spec.md", rendered)
        self.write("plan.md", "### T017 Reject empty input\n\n- [ ] Implement R1.\n\n"
                   "### T023 Preserve valid input\n\n- [ ] Implement R2.\n")
        self.write("checks.md", "## Empty input\n\nCall the input validator with an empty value; "
                   "expect rejection and no write.\n\n## Valid input\n\nCall the input validator "
                   "with an existing value; expect that value to be preserved.\n")
        actual = (self.repo / "spec.md").read_text(encoding="utf-8")
        for requirement, (task, expected_result, anchor) in cases.items():
            row = next(line for line in actual.splitlines() if line.startswith(f"| {requirement} |"))
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            self.assertEqual(len(cells), 6)
            self.assertEqual(cells[3], task)
            self.assertEqual(cells[4], expected_result)
            self.assertEqual(cells[5], f"[Planned check](checks.md#{anchor}); evidence not run")
            self.assertIn("### " + task, (self.repo / "plan.md").read_text(encoding="utf-8"))
            reference = re.search(r"\[Planned check\]\(([^)]+)\)", cells[5])[1]
            path, selected_anchor = reference.split("#", 1)
            evidence_text = (self.repo / path).read_text(encoding="utf-8")
            headings = [re.sub(r"\s+", "-", line.lstrip("# ").lower())
                        for line in evidence_text.splitlines() if line.startswith("#")]
            self.assertIn(selected_anchor, headings)

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
