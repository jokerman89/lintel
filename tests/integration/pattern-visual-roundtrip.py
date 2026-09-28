#!/usr/bin/env python3
# component: reusable-patterns-visual-roundtrip-test
# implements: ADR-0038, ADR-0016, ADR-0028, ADR-0034
# intent: .claude/plans/reusable-patterns/plan.md
# constraints: synthetic temporary roots only; real CLI subprocesses and the shared design validator; no renderer, browser, network or real home
# last_intent_review: 2026-09-28
"""V11: actual selection -> adapter -> frontend spec -> review, including negative cases.

The resolution comes from the real `bin/li-pattern.py` process over synthetic catalogs; the spec
is checked by the shared design validator and by `validate_visual` as frontend-design-review
consumes it. This is local integration evidence, not rendering or host acceptance. Cases that
need the pack-lane launcher or later core commands skip with an explicit PENDING reason.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pattern_consumer_fixtures import (  # noqa: E402
    Fixture, binding, clause, ctx, load_design_contract, make_pattern, p, pv, read_asset_accepts_selection, ref,
    tree_digest, visual_base_spec,
)

WEBSITE = {"artifact": ["website"]}
TOKENS = json.dumps({"accent": "#1a2b3c"}).encode("utf-8")
GUIDE = b"# Backend guide\nSynthetic backend guidance.\n"


class Roundtrip:
    """A repository-bound dashboard baseline, a pack default and an explicitly selectable personal default."""

    def __init__(self, testcase):
        self.t = testcase
        self.fx = Fixture(testcase)
        self.dashboard = make_pattern("example.dashboard", applies_to=WEBSITE, requirements=[
            clause("MAX", "must", "visual.layout.max-width", "1200px"),
            clause("SMOOTH", "default", "visual.interaction.scroll-smoothing", True),
            clause("ACCENT", "default", "visual.palette.accent", "#1A2B3C"),
            clause("NAV", "must", text="Primary navigation stays visible on every dashboard view.")],
            assets=[{"path": "tokens.json", "kind": "tokens", "sha256": hashlib.sha256(TOKENS).hexdigest(),
                     "domains": ["frontend"]}])
        self.backend = make_pattern("example.backend", applies_to={"artifact": ["service"]}, requirements=[
            clause("LOGS", "must", text="Structured logs carry a correlation ID.")],
            assets=[{"path": "guide.md", "kind": "guide", "sha256": hashlib.sha256(GUIDE).hexdigest()}])
        self.fx.publish(self.fx.repo_patterns, "repo.main", [self.dashboard, self.backend],
                        assets={"example.dashboard": {"tokens.json": TOKENS}, "example.backend": {"guide.md": GUIDE}})
        self.fx.repo_bindings([
            binding("dashboard", [ref("repo.main", self.dashboard)], when=WEBSITE),
            binding("backend", [ref("repo.main", self.backend)], when={"artifact": ["service"]})])
        pack_dir = self.fx.pack_source()
        self.pack = make_pattern("team.web", applies_to=WEBSITE, requirements=[
            clause("GRID", "default", "visual.layout.grid", "bento"),
            clause("SMOOTH", "default", "visual.interaction.scroll-smoothing", False)])
        self.fx.publish(pack_dir, "team.patterns", [self.pack],
                        bindings=[binding("team-web", [ref("team.patterns", self.pack)], role="default", when=WEBSITE)])
        self.personal = make_pattern("me.hover", applies_to=WEBSITE, requirements=[
            clause("HOVER", "default", "visual.interaction.hover-intent", "pronounced"),
            clause("GRID", "default", "visual.layout.grid", "12-col")])
        self.fx.publish(self.fx.personal_patterns, "personal.me", [self.personal])
        self.run = self.fx.repo / ".claude" / "runtime" / "patterns" / "run-1"
        self.run.mkdir(parents=True)

    def resolve(self, artifact="website", refs=None, overrides=None):
        context = self.fx.write_json(f"context-{artifact}.json", ctx(artifact=artifact))
        args = ["resolve", "--context", context]
        if refs is not None:
            args += ["--refs", self.fx.write_json("refs.json", refs)]
        if overrides is not None:
            args += ["--overrides", self.fx.write_json("overrides.json", overrides)]
        return self.fx.cli(*args)

    def personal_ref(self):
        return [{"ref": ref("personal.me", self.personal), "role": "default", "approved_by": "operator",
                 "approval_ref": "brief.md"}]


class VisualRoundtripTests(unittest.TestCase):
    def setUp(self):
        self.rt = Roundtrip(self)
        self.design = load_design_contract()

    def project(self, report):
        spec = pv.project_visual(visual_base_spec(), report)["spec"]
        path = self.rt.run / "frontend-design-spec.json"
        path.write_text(json.dumps(spec), encoding="utf-8")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_selection_adapter_spec_review_roundtrip(self):
        code, report, _ = self.rt.resolve(refs=self.rt.personal_ref())
        self.assertEqual((code, report["status"]), (0, "ready"))
        winners = {key: value["value"] for key, value in report["settings"].items()}
        self.assertEqual(winners["visual.interaction.scroll-smoothing"], True, "repository default beats pack default")
        self.assertEqual(winners["visual.layout.grid"], "bento", "pack default beats explicit personal default")
        self.assertEqual(winners["visual.interaction.hover-intent"], "pronounced", "personal default fills a gap")
        spec = self.project(report)
        self.assertEqual(spec["layout_grammar"], {"max_width": "1200px", "grid": "bento"})
        self.assertEqual(spec["interaction_signature"]["hover_intent"], "pronounced")
        self.assertEqual(spec["typography"], visual_base_spec()["typography"], "Design DNA choices stay")
        self.assertEqual(self.design.validate_spec(spec)["kind"], "frontend")
        review = pv.validate_visual(spec, report)
        self.assertEqual(review["status"], "passed")
        self.assertFalse(review["clearance"])
        self.assertIn("example.dashboard@1.0.0#NAV", {item["clause"] for item in review["review_required"]},
                      "prose must clauses stay with ordinary review")

    def test_review_fails_when_the_built_spec_drifts_from_the_baseline(self):
        _, report, _ = self.rt.resolve()
        spec = self.project(report)
        drifted = copy.deepcopy(spec)
        drifted["layout_grammar"]["max_width"] = "1440px"
        drifted["palette"]["tokens"]["accent"] = "#000000"
        review = pv.validate_visual(drifted, report)
        self.assertEqual(review["status"], "failed")
        failed = {item["winner"] for item in review["checks"] if item["status"] == "failed"}
        self.assertEqual(failed, {"example.dashboard@1.0.0#MAX", "example.dashboard@1.0.0#ACCENT"})

    def test_brief_override_cannot_bypass_a_mandatory_setting(self):
        override = {"schema_version": 1, "items": [{
            "setting": "visual.layout.max-width", "value": "960px", "reason": "brief", "approval_ref": "brief.md",
            "replaces": ["example.dashboard@1.0.0#MAX"]}]}
        code, report, _ = self.rt.resolve(overrides=override)
        self.assertEqual((code, report["status"]), (4, "conflict"))
        with self.assertRaises(p.PatternError):
            pv.project_visual(visual_base_spec(), report)

    def test_unrelated_backend_work_reads_zero_visual_assets(self):
        code, report, _ = self.rt.resolve(artifact="service")
        self.assertEqual((code, report["status"]), (0, "ready"))
        self.assertEqual([item["ref"]["id"] for item in report["selected"]], ["example.backend"])
        self.assertEqual(report["metrics"]["asset_reads"], 0)
        self.assertNotIn("visual.layout.max-width", report["settings"])
        self.assertEqual(pv.project_visual(visual_base_spec(), report)["spec"]["layout_grammar"],
                         visual_base_spec()["layout_grammar"])
        self.assertEqual(p.asset_refs(report, kind="tokens"), [])

    def test_assets_are_read_only_on_explicit_need_through_the_core(self):
        _, report, _ = self.rt.resolve()
        self.assertEqual(report["metrics"]["asset_reads"], 0, "selection alone reads no asset")
        refs = pv.project_visual(visual_base_spec(), report)["pattern_context"]["asset_refs"]
        self.assertEqual([(item["path"], item["kind"]) for item in refs], [("tokens.json", "tokens")])
        reader = p.Reader()
        kwargs = {"selection": report} if read_asset_accepts_selection() else {}
        data = p.read_asset(self.rt.fx.roots(), refs[0], domain="frontend", reader=reader, **kwargs)
        self.assertEqual((data, reader.count("asset")), (TOKENS, 1))
        with self.assertRaises(p.PatternError):
            p.read_asset(self.rt.fx.roots(), refs[0], domain="backend", **kwargs)

    def test_foreign_assets_are_refused_for_a_selection(self):
        if not read_asset_accepts_selection():
            self.skipTest("PENDING join: read_asset(selection=) arrives with core R3 (f1918e12)")
        _, report, _ = self.rt.resolve()
        _, backend, _ = self.rt.resolve(artifact="service")
        foreign = p.asset_refs(backend)[0]
        with self.assertRaises(p.PatternError) as raised:
            p.read_asset(self.rt.fx.roots(), foreign, selection=report)
        self.assertEqual(raised.exception.status, "unavailable")

    def test_no_patterns_roundtrip_is_unchanged_and_writes_nothing(self):
        fx = Fixture(self)
        before = tree_digest(fx.repo)
        context = fx.write_json("context.json", ctx(artifact="website"))
        code, report, stderr = fx.cli("resolve", "--context", context)
        self.assertEqual((code, report["status"], stderr), (0, "empty", ""))
        self.assertEqual((report["metrics"]["pattern_reads"], report["metrics"]["asset_reads"]), (0, 0))
        base = visual_base_spec()
        self.assertEqual(pv.project_visual(base, report)["spec"], base)
        self.assertEqual(self.design.validate_spec(base), self.design.validate_spec(
            pv.project_visual(base, report)["spec"]))
        self.assertEqual(tree_digest(fx.repo), before)

    def test_legacy_import_roundtrip_stays_default_and_schema_only(self):
        seed = Path(p.__file__).resolve().parents[1] / "seeds/brand/design-patterns/ultra-modern-lovable-style/pattern.json"
        data = seed.read_bytes()
        conversion = pv.legacy_to_draft(data, pattern_id="example.lovable", applies_to=WEBSITE, owner="design",
                                        source_ref="seed")
        approved = dict(conversion["draft"], status="approved", version="1.0.0",
                        approval={"by": "design review", "reference": "synthetic-review", "at": "2026-09-02T00:00:00Z"})
        fx = Fixture(self)
        fx.publish(fx.repo_patterns, "repo.main", [approved],
                   assets={"example.lovable": {"visual-legacy/pattern.json": data}})
        fx.repo_bindings([binding("legacy", [ref("repo.main", approved)], role="default", when=WEBSITE)])
        report, reader = fx.resolve(ctx(artifact="website"))
        self.assertEqual({item["state"] for item in report["requirements"]}, {"default"})
        self.assertEqual(reader.count("asset"), 0)
        spec = pv.project_visual(visual_base_spec(), report)["spec"]
        self.assertEqual(spec["layout_grammar"]["section_spacing"], "clamp(4rem, 8vw, 8rem)")
        ref_legacy = [item for item in spec["pattern_context"]["asset_refs"] if item["kind"] == "visual-legacy"]
        kwargs = {"selection": report} if read_asset_accepts_selection() else {}
        self.assertEqual(p.read_asset(fx.roots(), ref_legacy[0], **kwargs), data, "original bytes are preserved")

    def test_launcher_gives_the_same_selection_as_the_direct_cli(self):
        fx = Fixture(self)
        fx.publish(fx.repo_patterns, "repo.main", [self.rt.dashboard],
                   assets={"example.dashboard": {"tokens.json": TOKENS}})
        fx.repo_bindings([binding("dashboard", [ref("repo.main", self.rt.dashboard)], when=WEBSITE)])
        context = fx.write_json("context.json", ctx(artifact="website"))
        code, launched, _ = fx.launcher("resolve", "--context", context)
        _, direct, _ = fx.cli("resolve", "--context", context)
        self.assertEqual((code, launched["status"]), (0, "ready"))
        self.assertEqual(launched["selection_digest"], direct["selection_digest"])
        self.assertEqual(pv.project_visual(visual_base_spec(), launched)["spec"],
                         pv.project_visual(visual_base_spec(), direct)["spec"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
