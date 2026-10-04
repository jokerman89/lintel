# component: external-authority-method-tests
# implements: ADR-0024, ADR-0028, ADR-0029
# intent: docs/spec-kit.md, docs/compliance.md, docs/provenance.md
# constraints: documentary regression only; no host discovery, upstream fetch or control execution
# last_intent_review: 2026-10-03
"""Check shared method/caller closure and preserved dated provenance, not model efficacy."""
from datetime import date
from pathlib import Path
import re
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
OWNER = "skills/spec-kit/references/selected-authority.md"


def text(path):
    return (ROOT / path).read_text(encoding="utf-8")


class ExternalAuthorityMethods(unittest.TestCase):
    def test_single_shared_owner_and_all_direct_callers(self):
        self.assertTrue((ROOT / OWNER).is_file())
        for name in ("spec-kit", "analyze", "define", "diagnose", "fix", "review"):
            with self.subTest(caller=name):
                body = text(f"skills/{name}/SKILL.md")
                self.assertIn("selected-authority.md", body)
                # Resolve actual Markdown links, rather than accepting an inert filename.
                links = re.findall(r"\]\(([^)]+selected-authority\.md(?:#[^)]+)?)\)", body)
                self.assertTrue(links)
                for link in links:
                    self.assertEqual((ROOT / "skills" / name / link.split("#")[0]).resolve(), ROOT / OWNER)
        self.assertIn("selected-authority.md", text("docs/spec-kit.md"))

    def test_observations_and_ownership_not_filename_capability_detection(self):
        owner = text(OWNER)
        for term in ("registration", "known configuration", "enabled", "disabled", "unknown",
                     "workflow", "hook", "one owner", "unsupported", "filename"):
            self.assertIn(term, owner.lower())
        self.assertIn("Do not infer", owner)
        self.assertIn("No Spec Kit installation or command execution", owner)
        self.assertIn("source approval", owner)
        self.assertIn("publication", owner)

    def test_original_reports_and_converge_tasks_use_existing_p03_p05_seams(self):
        owner = text(OWNER)
        for term in ("analysis", "converge", "bug", "assessment", "tasks.md",
                     "--acceptance", "--warm-path", "acceptance_paths", "qa_requirements",
                     "bind_work", "P03", "P05", "P07"):
            self.assertIn(term, owner)
        self.assertIn("only task", owner)
        self.assertIn("work-map schema", owner)
        self.assertIn("drift", owner)
        self.assertNotIn("spec-kit /analyze hole", text("skills/analyze/SKILL.md"))
        self.assertNotIn("adopted from speckit", text("skills/review/SKILL.md"))

    def test_control_conformance_contract_has_all_five_operational_fields(self):
        body = text("docs/compliance.md")
        for term in ("Responsible owner", "Actual mechanism", "Negative test",
                     "Evidence location", "Failure behavior",
                     "model-instructed", "helper-validated-on-invocation", "host/CI-enforced",
                     "qa_requirements", "required_controls"):
            self.assertIn(term, body)
        self.assertIn("selected required control", body)
        self.assertIn("not a new", body)
        for path in ("docs/enterprise-adoption.md", "docs/enterprise-profile-value.md"):
            self.assertIn("compliance.md#selected-control-conformance", text(path))

    def test_inheritance_guidance_preserves_semantics_and_source_approval_boundary(self):
        body = text("docs/enterprise-profile-value.md")
        for term in ("whole", "source approval", "immutable", "P05", "external-authority.sh"):
            self.assertIn(term, body)
        adoption = text("docs/enterprise-adoption.md")
        for term in ("revocation", "rollback", "immutable revision", "migration"):
            self.assertIn(term, adoption)

    def test_old_method_pins_and_import_provenance_remain_dated(self):
        registry = yaml.safe_load(text("install/upstream-sources.yaml"))
        self.assertEqual(registry["last_full_review"], date(2026, 5, 26))
        comparison = registry["method_comparisons"]
        self.assertEqual(comparison["checked"], date(2026, 9, 20))
        self.assertEqual({key: comparison[key] for key in ("gstack", "superpowers", "gsd-core", "ecc")}, {
            "gstack": "a6b3a57512ca6d5c6aa5b68f74f736195021f96e",
            "superpowers": "5bf4e78011075bcfc0dc295f0724994cd123ee71",
            "gsd-core": "88b5775dc8e32ffe8d50fe4db01677650e219ed2",
            "ecc": "934195f955cf0da847d59fcd6f68856bce112d8b",
        })
        corpus = registry["bundled_materials"]["design-dna-corpus"]
        self.assertEqual(corpus["recorded_release"], "v2.5.0")
        self.assertIsNone(corpus["import_commit"])
        self.assertNotIn("skills/design-dna/scripts/validate_design.py", corpus["local_paths"])
        self.assertTrue((ROOT / corpus["notice"]).is_file())
        self.assertTrue((ROOT / corpus["attribution"]).is_file())

    def test_current_facing_references_do_not_invent_new_counts_or_imports(self):
        registry = yaml.safe_load(text("install/upstream-sources.yaml"))
        gsd = registry["sources"]["gsd-redux"]
        self.assertEqual(gsd["repo"], "https://github.com/open-gsd/gsd-core")
        self.assertEqual(gsd["docs"], "https://github.com/open-gsd/gsd-core#readme")
        self.assertEqual(gsd["last_verified"], date(2026, 5, 26))
        self.assertNotRegex(registry["sources"]["ecc"]["description"], r"\b\d+\s+(agents|skills|commands)")
        self.assertIn("c00dc0551583428a10a94443c58c6a41e5e0138c",
                      text("install/upstream-sources.yaml"))
        self.assertIn("2026-09-28", text("docs/provenance.md"))
        self.assertIn("not proof of an installed", text("docs/provenance.md"))

    def test_only_original_map_roles_remain_documented(self):
        body = text("skills/spec-kit/references/work-map.md")
        self.assertIn("--acceptance", body)
        self.assertIn("P03", body)
        self.assertIn("selected-authority.md", body)
        # Selection lives in the existing handoff/evidence interfaces, never extra map fields.
        for field in ('"analysis":', '"converge":', '"bug":', '"assessment":', '"capabilities":'):
            self.assertNotIn(field, body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
