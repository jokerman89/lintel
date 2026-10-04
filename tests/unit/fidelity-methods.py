#!/usr/bin/env python3
# component: fidelity-method-tests
# implements: ADR-0017, ADR-0028, ADR-0033
# intent: .claude/plans/v2-findings/plan.md
# constraints: source/caller contracts plus real advisory/P05 helper cases; no model efficacy
# last_intent_review: 2026-10-03
"""Focused contracts for the six fidelity leaves; no rendering or legal conclusions."""
from copy import deepcopy
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "lib"), str(ROOT / "skills/design-dna/scripts")]
import design_contract as design
from review_contract import evaluate_controls

KEYS = ["typography_hierarchy", "motion_coherence", "shader_perf_budget",
        "accessibility_wcag", "brand_conformance", "responsive_fidelity"]
REVIEWERS = (
    "skills/frontend-design-review/SKILL.md",
    "skills/frontend-design-review/references/built-review.md",
    "agents/frontend/DesignSystemAuditor.md", "agents/doc-gen/WebExperienceCritic.md",
)
DOC_METHOD = "skills/build/references/documentation-fidelity.md"


def text(path):
    return (ROOT / path).read_text(encoding="utf-8")


class FidelityMethods(unittest.TestCase):
    def test_palette_child_receives_admitted_files_not_original_urls(self):
        source = text("skills/frontend-style-extract/SKILL.md")
        handoff = source.split("### Step 3 — Optional palette chain", 1)[1].split("### Step 4", 1)[0]
        self.assertIn('"${palette_artifacts[@]}"', handoff)
        self.assertNotIn('"${artifacts[@]}"', handoff)
        for term in ("actual", "HTML/CSS/document files", "source URL/path", "content hash",
                     "refuse the URL-plus-palette", "child remains file-only"):
            self.assertIn(term, " ".join(source.split()))

    def test_app_smoothing_uses_the_selected_runtime_not_a_fixed_provider(self):
        source = text("skills/generate-app/SKILL.md")
        transform = source.split("### Step 4", 1)[1].split("### Step 5", 1)[0]
        self.assertNotIn("wrap children with LenisProvider if", transform)
        self.assertIn("actual bound motion runtime", transform)
        self.assertIn("when Lenis was explicitly selected", transform)
        self.assertIn("none means no animation imports", transform)
        motion = {
            "schema_version": 1, "mode": "library",
            "libraries": [{"name": "fixture-non-lenis-smoother"}],
            "key_animations": [],
            "perf_budget": {"fallback_for_prefers_reduced_motion": "native scrolling"},
        }
        checked = design.validate_spec(motion, "motion")["fragment"]
        design._motion(checked, {"scroll_smoothing": True, "page_transitions": "none"})
        self.assertEqual(checked["libraries"][0]["name"], "fixture-non-lenis-smoother")

    def test_report_only_qa_never_authorizes_a_mutating_editability_probe(self):
        source = text("skills/generate-qa/SKILL.md")
        self.assertIn("In report-only `none` mode, do not perform mutating", source)
        self.assertIn("separately authorized verification on a distinct owned copy", source)
        self.assertIn("remains unverified", source)
        self.assertIn("--fixed-out", source)

    def test_voice_and_compliance_use_distinct_real_control_inputs(self):
        for path in ("skills/generate-app/SKILL.md", "skills/generate-qa/SKILL.md",
                     "skills/generate/SKILL.md"):
            source = text(path)
            self.assertIn("voice.gates_active", source)
            self.assertNotRegex(source, r"(?im)^[^\n]*voice[^\n]*resolve_pack_field compliance\.hooks")
        source = text("skills/generate/SKILL.md")
        self.assertNotIn("compliance-gate --scope", source)
        self.assertIn("controls --input", source)

    def test_pdf_and_nested_palette_overwrite_keep_the_actual_boundaries(self):
        learn = text("skills/generate-style-learn/SKILL.md")
        self.assertIn("no PDF reader here", learn)
        self.assertIn("extension is not an extraction", learn)
        self.assertIn("external read operation only with explicit", " ".join(learn.split()))
        design = text("skills/generate-design/SKILL.md")
        self.assertNotIn("slots — AI generates", design)
        self.assertIn("unavailable-writer boundary", design)
        extract = text("skills/frontend-style-extract/SKILL.md")
        nested = extract.split("### Step 3 — Optional palette chain", 1)[1].split("### Step 4", 1)[0]
        for required in ("--overwrite", "both", "$name.json", "$name-STYLE.md",
                         "exact child invocation", "two preimages", "default refusal"):
            self.assertIn(required, nested)

    def test_post_generation_review_has_one_owner_and_current_evidence_reuse(self):
        owner = "skills/frontend-design-review/references/built-review.md"
        source = text(owner)
        for value in ("one post-generation review owner", "current P05 reader/QA",
                      "independent reviewer provenance", "Additional reviewers",
                      "not merely another alias"):
            self.assertIn(value, " ".join(source.split()))
        for caller in ("skills/generate-app/SKILL.md", "skills/generate-web/SKILL.md",
                       "skills/frontend-design/SKILL.md", "agents/frontend/DesignSystemAuditor.md"):
            self.assertIn("#review-ownership-and-reuse", text(caller))
        self.assertNotIn("Disjoint phases", text("agents/frontend/DesignSystemAuditor.md"))
        self.assertIn("Optional `--review`", text("skills/generate-app/SKILL.md"))

    def test_slide_and_demo_arcs_share_one_structure_owner(self):
        method = "skills/generate-outline/references/narrative-arc.md"
        for path in ("agents/doc-gen/PPTNarrativeArchitect.md", "agents/customer/DemoNarrativeArc.md"):
            source = text(path)
            self.assertIn("../../" + method, source)
            self.assertIn("synthetic", source.casefold())
        self.assertIn("references/narrative-arc.md", text("skills/generate-outline/SKILL.md"))
        shared = text(method)
        for value in ("one arc", "genre", "approved arc", "independent", "actual duration"):
            self.assertIn(value, shared)
        self.assertNotIn("Opening, 5-10%", text("agents/doc-gen/PPTNarrativeArchitect.md"))

    def test_axis_roles_return_drafts_to_one_publication_owner(self):
        method = "skills/frontend-design/references/axis-ownership.md"
        for role, skill in (("TypographyCurator", "frontend-typography"),
                            ("MotionDirector", "frontend-motion"), ("ShaderEngineer", "frontend-shader")):
            source = text(f"agents/frontend/{role}.md")
            caller = text(f"skills/{skill}/SKILL.md")
            self.assertIn("../../" + method, source)
            self.assertIn("../frontend-design/references/axis-ownership.md", caller)
            self.assertIn("Return the draft fragment", source)
            self.assertIn("single publication", caller)
            self.assertIn("authorized lookup", caller)
        self.assertIn("do not declare a web-fetch tool", text(method))
        self.assertIn("write a competing output", text("agents/frontend/MotionDirector.md"))

    def test_one_advisory_rubric_in_all_direct_review_consumers(self):
        for path in REVIEWERS:
            with self.subTest(path=path):
                source = text(path)
                self.assertNotRegex(source, r"1-10|[0-9.]+/10\b|Pillar scores|six-pillar table")
                for key in KEYS:
                    self.assertIn(key, source)
                self.assertIn("unverified", source)
                self.assertIn("P05", source)
        self.assertIn("--include-copy-pillar", text(REVIEWERS[1]))  # retained input alias

    def test_performance_claims_require_measurement_not_screenshots(self):
        source = text(REVIEWERS[0])
        for required in ("FPS", "FOIT", "scroll-jank", "compatible measurement",
                         "DOM", "screenshot", "null"):
            self.assertIn(required, source)
        for path in REVIEWERS:
            with self.subTest(path=path):
                self.assertNotRegex(text(path), r"FOIT >100ms|[Ss]croll-jank >16ms|fps <30|fps drops below 30")
        self.assertIn("measure_contrast.py", source)
        self.assertIn("snapshot", source)
        self.assertIn("review_result", text(REVIEWERS[1]))

    def test_actual_alias_normalization_and_null_unverified_results(self):
        aliases = ["typography", "motion", "shader", "accessibility", "brand", "responsive"]
        self.assertEqual(design.normalize_dimensions(aliases), KEYS)
        data = {"schema_version": 1, "dimensions": {
            key: {"score": None, "findings": ["No compatible timing measurement; unverified."]}
            for key in aliases}}
        original = deepcopy(data)
        result = design.validate_review(data)
        self.assertEqual(list(result["dimensions"]), KEYS)
        self.assertEqual(result["overall_verdict"], "unverified")
        self.assertFalse(result["release_clearance"])
        self.assertEqual(data, original)
        for key in KEYS:
            self.assertIsNone(result["dimensions"][key]["score"])
            self.assertEqual(result["dimensions"][key]["verdict"], "unverified")
        for invalid in (["motion", "motion_coherence"], ["copy"], []):
            with self.assertRaises(ValueError):
                design.normalize_dimensions(invalid)

    def test_actual_advisory_bands_do_not_clear_mandatory_controls(self):
        for score, verdict in ((0, "red"), (59.9, "red"), (60, "yellow"),
                               (79.9, "yellow"), (80, "green"), (100, "green")):
            result = design.validate_review({"schema_version": 1, "dimensions": {
                "typography": {"score": score, "findings": ["Inert fixture, not a rendered observation."]}}},
                ["typography"])
            self.assertEqual(result["dimensions"]["typography_hierarchy"]["verdict"], verdict)
        control = {
            "id": "keyboard", "kind": "check", "requirement": "mandatory",
            "applicability": "applicable", "reason": "Inert control fixture.",
            "policy": {"source": "fixture.md", "version": "1", "applicability": "Fixture only",
                       "jurisdiction": None, "actor": None, "effective_date": None},
            "evidence": ["fixture.txt"], "observation": {}, "advisory_score": 100,
        }
        policy = {"required": False, "status": "not_required", "source": "fixture",
                  "version": "1", "applicability": "not_applicable"}
        for status in ("unverified", "error", "fail"):
            self.assertTrue(evaluate_controls([{**control, "status": status}], required_policy=policy)["blocked"])

    def test_generate_continuation_uses_supported_stages_not_retired_gates(self):
        source = text("skills/generate/SKILL.md")
        self.assertNotIn("--resume", source)
        self.assertNotIn("A15.3.shared", source)
        self.assertNotIn("generate_run_complete", source)
        self.assertNotIn("deliver to N formats without duplicate work", source)
        for marker in ("## Continue an owned run", "current", "pipeline_inputs.py", "--outline",
                       "--content", "--from-pipeline", "--auto-fix none", "--fixed-out"):
            self.assertIn(marker, source)
        for path in ("skills/generate-ppt/SKILL.md", "skills/generate-word/SKILL.md"):
            self.assertNotIn("A15.3.shared", text(path))
        self.assertIn("no PDF reader", source)
        self.assertIn("Visio", source)
        self.assertIn("recalculation", source)
        self.assertIn("No automatic cleanup", source)

    def test_real_mandatory_controls_survive_the_obsolete_gate_test_change(self):
        source = text("tests/integration/document-format-pipeline.py")
        self.assertNotIn('self.assertIn("A15.3.shared", text)', source)
        for kept in ("test_missing_mandatory_rendering_cannot_be_scored_into_pass",
                     "test_unknown_or_ungrounded_applicability_blocks",
                     "test_required_profile_failure_is_not_neutral_fallback",
                     "test_changed_source_and_output_revoke_bound_qa"):
            self.assertIn("def " + kept, source)
        self.assertIn("check_pptx.missing_content(parts, required)", source)
        self.assertIn("slide_notes = check_pptx.slide_notes", source)

    def test_provenance_names_the_actual_adapted_references(self):
        source = text("install/upstream-sources.yaml").split("bundled_materials:", 1)[1]
        self.assertNotRegex(source, r"(?m)^\s+- skills/design-dna/references\s*$")
        for name in ("token-architecture", "primitive-tokens", "semantic-tokens", "component-tokens"):
            path = f"skills/design-dna/references/{name}.md"
            self.assertIn(path, source)
            self.assertTrue((ROOT / path).is_file())
        self.assertNotIn("- skills/design-dna/references/design-contract", source)
        for notice in ("MIT-next-level-builder.txt", "Apache-2.0-anthropic.txt"):
            self.assertTrue((ROOT / "skills/design-dna/LICENSES" / notice).is_file())
            self.assertIn(notice, source)
        self.assertEqual(source.count("import_commit: null"), 2)
        attribution = text("skills/design-dna/ATTRIBUTION.md")
        self.assertIn("primitive,semantic,component}-tokens.md", attribution)
        self.assertIn("Trademark", attribution)

    def test_adr_clarification_is_dated_and_does_not_claim_outcome_measurement(self):
        source = text(".claude/decisions/0017-design-parity-slides-tokens.md")
        self.assertIn("2026-10-03", source)
        self.assertIn("retrieval parity", source)
        self.assertIn("validator/profile seams", source)
        self.assertIn("outcomes remain unmeasured", source)
        for retained in ("## Decision", "**Deliberately scoped OUT**", "## Alternatives considered"):
            self.assertIn(retained, source)

    def test_documentation_fidelity_has_one_direct_owner_without_a_cycle(self):
        method = text(DOC_METHOD)
        for term in ("signatures", "defaults", "return", "errors", "side effects",
                     "accepted documentation", "intent", "replacement", "deprecation",
                     "frozen", "unrun", "changed source", "claim-to-source", "P05"):
            self.assertIn(term.casefold(), method.casefold())
        for caller in ("skills/build/SKILL.md", "skills/ship/SKILL.md",
                       "skills/generate-docs/SKILL.md", "agents/engineering/DocWriter.md"):
            with self.subTest(caller=caller):
                source = text(caller)
                link = re.search(r"\]\(([^)]+documentation-fidelity\.md(?:#[^)]*)?)\)", source)
                self.assertIsNotNone(link)
                self.assertEqual(((ROOT / caller).parent / link[1].split("#")[0]).resolve(), (ROOT / DOC_METHOD).resolve())
        generated = text("skills/generate-docs/SKILL.md")
        writer = text("agents/engineering/DocWriter.md")
        self.assertNotIn("Use `DocWriter` for later drift", generated)
        self.assertNotIn("use `/generate-docs`", writer)
        for target in ("reference", "customer-guide", "tutorial"):
            self.assertIn(target, generated)
        self.assertIn("DRAFT", generated)
        self.assertIn("read it back", generated)
        self.assertIn("mandatory document check", text("skills/ship/SKILL.md"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
