#!/usr/bin/env python3
# component: reusable-patterns-visual-test
# implements: ADR-0038, ADR-0016
# intent: .claude/plans/reusable-patterns/plan.md
# constraints: synthetic temporary roots and the bundled seed pattern (read-only) only; no network, renderer or real home
# last_intent_review: 2026-09-28
"""V10: legacy discrimination/conversion, structured-setting projection and no-pattern compatibility.

These are helper-level tests of lib/pattern_visual.py over real core resolutions. They are not
rendering, browser or host acceptance evidence.
"""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "integration"))
from pattern_consumer_fixtures import (  # noqa: E402
    ROOT, Fixture, binding, clause, ctx, make_pattern, p, pv, ref, visual_base_spec, load_design_contract,
)

SEED = ROOT / "seeds" / "brand" / "design-patterns" / "ultra-modern-lovable-style" / "pattern.json"
SEED_LOCATION = "brand/design-patterns/ultra-modern-lovable-style/pattern.json"
WEBSITE = {"artifact": ["website"]}
WEB = p.parse_context(ctx(artifact="website"))


def visual_pattern(pid="example.visual", level="default", extra=(), **kwargs):
    requirements = [
        clause("MAX", level, "visual.layout.max-width", "1200px"),
        clause("SPACING", level, "visual.layout.section-spacing", "6rem"),
        clause("GRID", level, "visual.layout.grid", "12-col"),
        clause("SMOOTH", level, "visual.interaction.scroll-smoothing", True),
        clause("HOVER", level, "visual.interaction.hover-intent", "subtle"),
        clause("TRANSITIONS", level, "visual.interaction.page-transitions", "fade"),
        clause("ACCENT", level, "visual.palette.accent", "#1A2B3C"),
        *extra]
    return make_pattern(pid, applies_to=WEBSITE, requirements=requirements, **kwargs)


class LegacyTests(unittest.TestCase):
    def setUp(self):
        self.data = SEED.read_bytes()

    def test_legacy_schema_one_is_not_universal_schema_one(self):
        legacy = json.loads(self.data)
        self.assertEqual(legacy["schema_version"], 1)
        self.assertEqual(pv.classify_document(legacy, location=SEED_LOCATION), "legacy-visual")
        with self.assertRaises(p.PatternError) as raised:
            p.parse_pattern(legacy)
        self.assertEqual(raised.exception.status, "invalid")
        universal = visual_pattern()
        self.assertEqual(pv.classify_document(universal, location=".claude/patterns/x/1.0.0/pattern.json"),
                         "universal")

    def test_discrimination_uses_fields_and_location_not_version_alone(self):
        legacy = json.loads(self.data)
        for bad in ({"schema_version": 1}, {"schema_version": True, "name": "x", "layout_grammar": {}},
                    dict(legacy, id="example.mixed"), dict(legacy, schema_version=2)):
            with self.assertRaises(p.PatternError, msg=bad.keys()):
                pv.classify_document(bad)
        for location in (".claude/patterns/legacy/pattern.json", "out/my-style/pattern.json"):
            self.assertEqual(pv.classify_document(legacy, location=location), "legacy-visual",
                             "location is a hint: a documented --out directory is accepted (L2)")
        with self.assertRaises(p.PatternError) as raised:
            pv.classify_document(visual_pattern(), location=SEED_LOCATION)
        self.assertEqual(raised.exception.code, "location_mismatch")

    def test_source_ref_must_be_portable_provenance(self):
        for good in ("brand/design-patterns/x/pattern.json", "https://example.test/style"):
            self.assertEqual(self.convert(source_ref=good)["draft"]["extensions"]["lintel.visual-legacy"]["original"],
                             good)
        for bad in ("C:/Users/someone/private/pattern.json", "//server/share/pattern.json", "/home/me/p.json",
                    "~/.lintel/brand/design-patterns/x/pattern.json", "..\\escape.json", "http://insecure.test/x"):
            with self.assertRaises(p.PatternError, msg=bad) as raised:
                self.convert(source_ref=bad)
            self.assertEqual(raised.exception.code, "unportable_source_ref")
        self.assertEqual(SEED.read_bytes(), self.data)

    def convert(self, data=None, **kwargs):
        kwargs.setdefault("pattern_id", "example.lovable-draft")
        kwargs.setdefault("applies_to", WEBSITE)
        kwargs.setdefault("owner", "design team")
        kwargs.setdefault("source_ref", SEED_LOCATION)
        return pv.legacy_to_draft(self.data if data is None else data, **kwargs)

    def test_conversion_is_a_draft_of_defaults_with_original_bytes_as_asset(self):
        result = self.convert(location=SEED_LOCATION)
        draft = result["draft"]
        parsed = p.parse_pattern(draft)
        self.assertEqual(parsed.status, "draft")
        self.assertNotIn("approval", draft)
        self.assertEqual({item["level"] for item in draft["requirements"]}, {"default"})
        self.assertEqual(result["mapped_settings"], [
            "visual.layout.max-width", "visual.layout.section-spacing", "visual.layout.grid",
            "visual.interaction.scroll-smoothing", "visual.interaction.hover-intent",
            "visual.interaction.page-transitions"])
        values = {item["setting"]: item["value"] for item in draft["requirements"]}
        self.assertEqual(values["visual.layout.max-width"], "1200px")
        self.assertIs(values["visual.interaction.scroll-smoothing"], True)
        digest = hashlib.sha256(self.data).hexdigest()
        self.assertEqual(draft["assets"], [{"path": "visual-legacy/pattern.json", "kind": "visual-legacy",
                                            "sha256": digest}])
        source = draft["sources"][0]
        self.assertEqual((source["kind"], source["confidence"], source["sha256"]), ("observation", "inferred", digest))
        self.assertEqual((source["root"], source["ref"]), ("pattern", "visual-legacy/pattern.json"),
                         "provenance points at the preserved bytes, not an external vault path")
        self.assertEqual(draft["extensions"]["lintel.visual-legacy"]["original"], SEED_LOCATION)
        self.assertNotEqual(source["confidence"], "confirmed")
        self.assertEqual(SEED.read_bytes(), self.data, "the legacy original is never modified")

    def test_unrecognized_fields_stay_uninterpreted_in_the_asset(self):
        result = self.convert()
        for field in ("motion_language", "component_library_fingerprint", "shader_thesis", "license_summary",
                      "typography_ref"):
            self.assertIn(field, result["uninterpreted_fields"])
        text = json.dumps(result["draft"]["requirements"])
        for leaked in ("gsap", "shadcn", "Fraunces", "mesh-gradient", "MIT"):
            self.assertNotIn(leaked, text)
        self.assertEqual(result["unknowns"], ["fonts", "accessibility", "licensing", "dependencies"])

    def test_wrongly_typed_legacy_values_are_not_coerced(self):
        legacy = json.loads(self.data)
        legacy["layout_grammar"]["max_width"] = 1200
        legacy["interaction_patterns"]["scroll_smoothing"] = "yes"
        legacy["extraction_confidence"] = "low"
        result = self.convert(json.dumps(legacy).encode("utf-8"))
        self.assertNotIn("visual.layout.max-width", result["mapped_settings"])
        self.assertNotIn("visual.interaction.scroll-smoothing", result["mapped_settings"])
        self.assertEqual({item["field"] for item in result["unmapped"]},
                         {"layout_grammar.max_width", "interaction_patterns.scroll_smoothing"})
        self.assertEqual(result["draft"]["sources"][0]["confidence"], "unknown")

    def test_universal_input_and_unsafe_asset_paths_are_refused(self):
        with self.assertRaises(p.PatternError):
            self.convert(json.dumps(visual_pattern()).encode("utf-8"))
        with self.assertRaises(p.PatternError):
            self.convert(asset_path="../outside.json")

    def test_stage_draft_writes_capture_input_with_its_sidecar_only(self):
        fx = Fixture(self)
        result = self.convert()
        directory = fx.root / "run" / "draft"
        path = pv.stage_draft(result, self.data, directory)
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), result["draft"])
        self.assertEqual((directory / "visual-legacy" / "pattern.json").read_bytes(), self.data)
        self.assertEqual(sorted(item.relative_to(directory).as_posix() for item in directory.rglob("*")
                                if item.is_file()), ["pattern.json", "visual-legacy/pattern.json"])
        with self.assertRaises(FileExistsError):
            pv.stage_draft(result, self.data, directory)
        with self.assertRaises(p.PatternError) as raised:
            pv.stage_draft(result, self.data + b" ", fx.root / "run" / "other")
        self.assertEqual(raised.exception.code, "asset_digest_mismatch")
        self.assertFalse((fx.root / "run" / "other").exists())
        self.assertFalse(fx.personal_patterns.exists(), "staging never registers anything")

    def test_captured_draft_is_registered_but_never_active(self):
        fx = Fixture(self)
        result = self.convert()
        kwargs = {}
        if "files_from" in inspect.signature(p.capture).parameters:
            kwargs["files_from"] = pv.stage_draft(result, self.data, fx.root / "run" / "draft").parent
        report = p.capture(fx.roots(), result["draft"], scope="personal", name="example.lovable-draft",
                           source_id="personal.designs", **kwargs)
        self.assertEqual(report["status"], "ok")
        catalog = json.loads((fx.personal_patterns / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["entries"][0]["status"], "draft")
        explicit = [{"ref": report["ref"], "role": "default", "approved_by": "me", "approval_ref": "chat"}]
        resolved, _ = fx.resolve(ctx(artifact="website"), refs=p.parse_refs(explicit))
        self.assertEqual(resolved["status"], "unavailable")
        self.assertEqual(resolved["requirements"], [])
        empty, _ = fx.resolve(ctx(artifact="website"))
        self.assertEqual(empty["status"], "empty", "a personal draft never applies without an explicit reference")


class ProjectionFixture:
    def __init__(self, testcase, pattern=None, level="default"):
        self.fx = Fixture(testcase)
        self.pattern = pattern or visual_pattern(level=level, extra=[
            clause("MOOD", level, "visual.mood.energy", "calm"),
            clause("PROSE", level, text="Hero copy leads with the outcome."),
            clause("DENSITY", level, "ui.density", "compact")])
        self.fx.publish(self.fx.repo_patterns, "repo.visual", [self.pattern])
        self.fx.repo_bindings([binding("web", [ref("repo.visual", self.pattern)],
                                       role="required" if level == "must" else "default", when=WEBSITE)])

    def resolve(self, **kwargs):
        return self.fx.resolve(ctx(artifact="website"), **kwargs)[0]


class ProjectionTests(unittest.TestCase):
    def test_every_table_setting_changes_the_actual_spec_value(self):
        report = ProjectionFixture(self).resolve()
        self.assertEqual(report["status"], "ready")
        base = visual_base_spec()
        result = pv.project_visual(base, report, context=WEB)
        spec = result["spec"]
        self.assertEqual(spec["layout_grammar"], {"max_width": "1200px", "section_spacing": "6rem", "grid": "12-col"})
        self.assertEqual(spec["interaction_signature"],
                         {"scroll_smoothing": True, "page_transitions": "fade", "hover_intent": "subtle"})
        self.assertEqual(spec["palette"]["tokens"], {"ink": "#141413", "paper": "#faf9f5", "accent": "#1a2b3c"})
        for key in ("typography", "motion", "shader", "visual_thesis", "voice_tier", "component_libraries"):
            self.assertEqual(spec[key], base[key], key)
        self.assertEqual(base, visual_base_spec(), "the input spec is not mutated")
        context = spec["pattern_context"]
        self.assertEqual(set(context), {"schema_version", "selection_digest", "clauses", "asset_refs"})
        self.assertEqual(context["selection_digest"], report["selection_digest"])
        applied = {item["setting"]: item for item in context["clauses"] if item["status"] == "applied"}
        self.assertEqual(applied["visual.layout.max-width"]["old"], "1152px")
        self.assertEqual(applied["visual.layout.max-width"]["new"], "1200px")
        self.assertEqual(applied["visual.layout.max-width"]["winner"], "example.visual@1.0.0#MAX")
        self.assertFalse(applied["visual.layout.grid"]["old_present"])

    def test_unknown_visual_settings_remain_unverified_obligations(self):
        report = ProjectionFixture(self).resolve()
        result = pv.project_visual(visual_base_spec(), report, context=WEB)
        self.assertEqual(result["unverified_settings"], ["visual.mood.energy"])
        self.assertNotIn("mood", json.dumps(result["spec"]["layout_grammar"]))
        open_clauses = {item["clause"] for item in result["review_required"]}
        self.assertEqual(open_clauses, {"example.visual@1.0.0#MOOD", "example.visual@1.0.0#PROSE",
                                        "example.visual@1.0.0#DENSITY"})
        check = pv.validate_visual(result["spec"], report, context=WEB)
        self.assertEqual(check["status"], "incomplete", "an unverified setting is never a mechanical pass")
        self.assertFalse(check["clearance"])

    def test_wrong_shapes_and_types_conflict_instead_of_coercing(self):
        report = ProjectionFixture(self).resolve()
        wrong = dict(visual_base_spec(), layout_grammar="1200px")
        with self.assertRaises(p.PatternError) as raised:
            pv.project_visual(wrong, report, context=WEB)
        self.assertEqual((raised.exception.code, raised.exception.status), ("visual_destination_shape", "conflict"))
        bad = visual_pattern(extra=[], pid="example.bad")
        bad["requirements"] = [clause("SMOOTH", "default", "visual.interaction.scroll-smoothing", "yes")]
        report = ProjectionFixture(self, pattern=bad).resolve()
        with self.assertRaises(p.PatternError) as raised:
            pv.project_visual(visual_base_spec(), report, context=WEB)
        self.assertEqual((raised.exception.code, raised.exception.status), ("visual_type_mismatch", "conflict"))
        bad["requirements"] = [clause("ACCENT", "default", "visual.palette.accent", "blue")]
        report = ProjectionFixture(self, pattern=bad).resolve()
        with self.assertRaises(p.PatternError):
            pv.project_visual(visual_base_spec(), report, context=WEB)

    def test_only_ready_bound_resolutions_project(self):
        fixture = ProjectionFixture(self, level="must")
        fixture.fx.repo_bindings([binding("web", [ref("repo.visual", fixture.pattern)], when={"artifact": ["website"],
                                                                                           "audience": ["public"]})])
        needs, _ = fixture.fx.resolve(ctx(artifact="website"))
        self.assertEqual(needs["status"], "needs-context")
        with self.assertRaises(p.PatternError) as raised:
            pv.project_visual(visual_base_spec(), needs, context=WEB)
        self.assertEqual(raised.exception.status, "needs-context")
        forged = dict(needs, status="ready", selection_digest=None)
        with self.assertRaises(p.PatternError) as raised:
            pv.project_visual(visual_base_spec(), forged, context=WEB)
        self.assertEqual(raised.exception.code, "selection_not_usable")
        with self.assertRaises(p.PatternError):
            pv.project_visual(visual_base_spec(), {"status": "ready"})

    def test_reports_need_their_inputs_and_matching_content(self):
        """M2: a bare or edited report is refused; a report is bound to its context and refs."""
        report = ProjectionFixture(self).resolve()
        for call in (lambda r, **k: pv.project_visual(visual_base_spec(), r, **k),
                     lambda r, **k: pv.validate_visual(visual_base_spec(), r, **k)):
            with self.assertRaises(p.PatternError) as raised:
                call(report)
            self.assertEqual(raised.exception.code, "selection_not_usable")
            tampered = copy.deepcopy(report)
            tampered["settings"]["visual.layout.max-width"]["value"] = "9999px"
            with self.assertRaises(p.PatternError) as raised:
                call(tampered, context=WEB)
            self.assertEqual(raised.exception.code, "selection_not_usable")
            with self.assertRaises(p.PatternError) as raised:
                call(report, context=p.parse_context(ctx(artifact="website", audience="public")))
            self.assertEqual(raised.exception.code, "selection_not_usable")
        lock = p.build_lock(report, WEB)
        self.assertEqual(pv.project_visual(visual_base_spec(), lock)["spec"],
                         pv.project_visual(visual_base_spec(), report, context=WEB)["spec"])

    def test_report_validation_delegates_to_the_core_helper_when_present(self):
        """R10 `validate_selection_report` is preferred; the build_lock route is only the pre-R10 fallback."""
        from unittest import mock
        report = ProjectionFixture(self).resolve()
        calls = []

        def helper(value, *, context, refs=()):
            calls.append((value is report, context.digest, tuple(refs)))
            return value

        with mock.patch.object(p, "validate_selection_report", helper, create=True):
            pv.project_visual(visual_base_spec(), report, context=WEB)
        self.assertEqual(calls, [(True, WEB.digest, ())])
        if hasattr(p, "validate_selection_report"):
            tampered = copy.deepcopy(report)
            tampered["requirements"][0]["text"] = "edited"
            with self.assertRaises(p.PatternError) as raised:
                pv.validate_visual(visual_base_spec(), tampered, context=WEB)
            self.assertEqual(raised.exception.code, "selection_not_usable")

    def test_explicit_refs_are_part_of_the_bound_inputs(self):
        fx = Fixture(self)
        pattern = visual_pattern(pid="me.visual")
        fx.publish(fx.personal_patterns, "personal.me", [pattern])
        refs = [{"ref": ref("personal.me", pattern), "role": "default", "approved_by": "me", "approval_ref": "brief"}]
        report, _ = fx.resolve(ctx(artifact="website"), refs=p.parse_refs(refs))
        self.assertEqual(report["status"], "ready")
        with self.assertRaises(p.PatternError) as raised:
            pv.project_visual(visual_base_spec(), report, context=WEB)
        self.assertEqual(raised.exception.code, "selection_not_usable")
        spec = pv.project_visual(visual_base_spec(), report, context=WEB, refs=refs)["spec"]
        self.assertEqual(spec["layout_grammar"]["max_width"], "1200px")

    def test_explicit_brief_override_wins_over_defaults_but_not_over_must(self):
        fixture = ProjectionFixture(self)
        override = p.parse_overrides({"schema_version": 1, "items": [{
            "setting": "visual.layout.max-width", "value": "960px", "reason": "brief asks for narrow reading",
            "approval_ref": "brief.md", "replaces": ["example.visual@1.0.0#MAX"]}]})
        report = fixture.resolve(overrides=override)
        spec = pv.project_visual(visual_base_spec(), report, context=WEB)["spec"]
        self.assertEqual(spec["layout_grammar"]["max_width"], "960px")
        must = ProjectionFixture(self, level="must")
        report = must.resolve(overrides=override)
        self.assertEqual(report["status"], "conflict")
        with self.assertRaises(p.PatternError) as raised:
            pv.project_visual(visual_base_spec(), report, context=WEB)
        self.assertEqual(raised.exception.status, "conflict")

    def test_repository_defaults_outrank_pack_defaults_from_the_resolver(self):
        fx = Fixture(self)
        pack_dir = fx.pack_source()
        pack = make_pattern("team.visual", applies_to=WEBSITE,
                            requirements=[clause("MAX", "default", "visual.layout.max-width", "1400px"),
                                          clause("GRID", "default", "visual.layout.grid", "bento")])
        fx.publish(pack_dir, "team.patterns", [pack], bindings=[binding("pack-web", [ref("team.patterns", pack)],
                                                                          role="default", when=WEBSITE)])
        repo = make_pattern("repo.visual-max", applies_to=WEBSITE,
                            requirements=[clause("MAX", "default", "visual.layout.max-width", "1100px")])
        fx.publish(fx.repo_patterns, "repo.visual", [repo])
        fx.repo_bindings([binding("web", [ref("repo.visual", repo)], role="default", when=WEBSITE)])
        report, _ = fx.resolve(ctx(artifact="website"))
        spec = pv.project_visual(visual_base_spec(), report, context=WEB)["spec"]
        self.assertEqual(spec["layout_grammar"]["max_width"], "1100px")
        self.assertEqual(spec["layout_grammar"]["grid"], "bento", "an unconflicted pack default still applies")


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.report = ProjectionFixture(self).resolve()
        self.spec = pv.project_visual(visual_base_spec(), self.report, context=WEB)["spec"]

    def failed(self, spec):
        check = pv.validate_visual(spec, self.report, context=WEB)
        self.assertEqual(check["status"], "failed")
        return {item["winner"] for item in check["checks"] if item["status"] == "failed"}

    def test_mismatch_is_reported_by_clause(self):
        spec = copy.deepcopy(self.spec)
        spec["layout_grammar"]["max_width"] = "1440px"
        self.assertEqual(self.failed(spec), {"example.visual@1.0.0#MAX"})
        spec = copy.deepcopy(self.spec)
        spec["interaction_signature"]["scroll_smoothing"] = "true"
        self.assertEqual(self.failed(spec), {"example.visual@1.0.0#SMOOTH"})
        spec = copy.deepcopy(self.spec)
        del spec["palette"]["tokens"]["accent"]
        self.assertEqual(self.failed(spec), {"example.visual@1.0.0#ACCENT"})

    def test_palette_comparison_is_case_insensitive_and_stale_context_fails(self):
        spec = copy.deepcopy(self.spec)
        spec["palette"]["tokens"]["accent"] = "#1A2B3C"
        self.assertEqual(pv.validate_visual(spec, self.report, context=WEB)["status"], "incomplete")
        spec["pattern_context"]["selection_digest"] = "0" * 64
        check = pv.validate_visual(spec, self.report, context=WEB)
        self.assertEqual(check["status"], "failed")
        self.assertIn("stale_pattern_context", [item["code"] for item in check["diagnostics"]])

    def test_matching_spec_without_unknown_settings_passes_mechanically_only(self):
        pattern = visual_pattern(pid="example.visual-only")
        report = ProjectionFixture(self, pattern=pattern).resolve()
        spec = pv.project_visual(visual_base_spec(), report, context=WEB)["spec"]
        check = pv.validate_visual(spec, report, context=WEB)
        self.assertEqual(check["status"], "passed")
        self.assertEqual(len(check["checks"]), 7)
        self.assertFalse(check["clearance"])

    def test_malformed_scalar_winners_fail_by_clause_in_projection_and_validation(self):
        """M1: any JSON scalar winner of the wrong type is structured, never an exception."""
        for setting, value in (("visual.palette.accent", 5), ("visual.palette.accent", None),
                               ("visual.palette.accent", True), ("visual.layout.max-width", 1200),
                               ("visual.interaction.scroll-smoothing", "true")):
            pattern = visual_pattern(pid="example.bad-scalar", extra=[])
            pattern["requirements"] = [clause("BAD", "default", setting, value)]
            report = ProjectionFixture(self, pattern=pattern).resolve()
            self.assertEqual(report["status"], "ready")
            with self.assertRaises(p.PatternError) as raised:
                pv.project_visual(visual_base_spec(), report, context=WEB)
            self.assertEqual((raised.exception.code, raised.exception.status), ("visual_type_mismatch", "conflict"))
            spec = visual_base_spec()
            spec["palette"]["tokens"]["accent"] = "#1a2b3c"
            check = pv.validate_visual(spec, report, context=WEB)
            self.assertEqual(check["status"], "failed", (setting, value))
            [item] = check["checks"]
            self.assertEqual((item["winner"], item["status"]), ("example.bad-scalar@1.0.0#BAD", "failed"))
            self.assertIn("winning value is not", item["reason"])


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.design = load_design_contract()

    def test_empty_projection_refuses_a_stale_pattern_context(self):
        """L4: a spec projected earlier is never silently kept or stripped when patterns disappear."""
        fx = Fixture(self)
        report, _ = fx.resolve(ctx(artifact="website"))
        stale = dict(visual_base_spec(), pattern_context={"schema_version": 1, "selection_digest": "a" * 64,
                                                          "clauses": [], "asset_refs": []})
        with self.assertRaises(p.PatternError) as raised:
            pv.project_visual(stale, report, context=WEB)
        self.assertEqual((raised.exception.code, raised.exception.status), ("stale_pattern_context", "conflict"))
        self.assertEqual(pv.validate_visual(stale, report, context=WEB)["status"], "failed")

    def test_no_patterns_leaves_the_spec_and_precedence_unchanged(self):
        fx = Fixture(self)
        report, reader = fx.resolve(ctx(artifact="website"))
        self.assertEqual((report["status"], report["selected"]), ("empty", []))
        self.assertEqual((reader.count("pattern"), reader.count("asset")), (0, 0))
        base = visual_base_spec()
        result = pv.project_visual(base, report, context=WEB)
        self.assertEqual(result["spec"], base)
        self.assertNotIn("pattern_context", result["spec"])
        self.assertEqual(pv.validate_visual(base, report, context=WEB)["status"], "empty")
        self.assertEqual(self.design.validate_spec(result["spec"]), self.design.validate_spec(base))

    def test_projected_spec_still_passes_the_shared_design_validator(self):
        report = ProjectionFixture(self).resolve()
        spec = pv.project_visual(visual_base_spec(), report, context=WEB)["spec"]
        loaded = self.design.validate_spec(spec)
        self.assertEqual(loaded["kind"], "frontend")
        self.assertEqual(loaded["design"]["layout_grammar"]["max_width"], "1200px")

    def test_existing_design_validators_still_bound_pattern_values(self):
        report = ProjectionFixture(self).resolve()
        base = visual_base_spec()
        base["motion"] = {"schema_version": 1, "mode": "none", "libraries": [], "key_animations": [],
                          "perf_budget": {"fallback_for_prefers_reduced_motion": "no-animation"}}
        spec = pv.project_visual(base, report, context=WEB)["spec"]
        with self.assertRaises(self.design.DesignError):
            self.design.validate_spec(spec)


if __name__ == "__main__":
    unittest.main(verbosity=2)
