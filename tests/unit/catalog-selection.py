#!/usr/bin/env python3
# component: catalog-selection-tests
# implements: ADR-0028
# intent: skills/catalog/references/selections.md
# constraints: source-only selection; synthetic homes; no installed or live-host acceptance
# last_intent_review: 2026-09-23
"""Selection closure, evidence and preservation over the existing catalog inventory."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "bin" / "li-catalog.py"
spec = importlib.util.spec_from_file_location("catalog_metadata_tests", ROOT / "tests/unit/catalog-metadata.py")
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)

FAMILIES = {
    "design-knowledge": {
        "requires": ["core"],
        "skills": "design-dna design-consultation",
        "agents": "",
    },
    "frontend-design": {
        "requires": ["design-knowledge"],
        "skills": (
            "frontend-design frontend-typography frontend-motion frontend-shader "
            "frontend-design-review frontend-style-extract design-html design-review "
            "design-shotgun plan-design-review generate-style-learn generate-web "
            "generate-app browse open-managed-browser"
        ),
        "agents": (
            "FrontendArchitect TypographyCurator MotionDirector ShaderEngineer "
            "DesignSystemAuditor WebExperienceCritic AccessibilityChecker"
        ),
    },
    "document-content": {
        "requires": ["design-knowledge"],
        "skills": "generate generate-outline generate-write generate-design generate-qa document-generate",
        "agents": "SystemArchitect WordTechnicalEditor DesignSystemAuditor",
    },
    "document-word": {
        "requires": ["core"], "skills": "generate-word", "agents": "WordTechnicalEditor",
    },
    "document-ppt": {
        "requires": ["design-knowledge"], "skills": "generate-ppt",
        "agents": "PPTNarrativeArchitect SlideNarrationCritic",
    },
    "document-pdf": {
        "requires": ["core"], "skills": "generate-pdf make-pdf browse", "agents": "WordTechnicalEditor",
    },
    "document-xlsx": {
        "requires": ["core"], "skills": "generate-xlsx", "agents": "CostAnalyzer CapacityPlanner",
    },
    "document-visio": {
        "requires": ["core"], "skills": "generate-visio", "agents": "SystemArchitect",
    },
    "customer-communication": {
        "requires": ["core"], "skills": "eval",
        "agents": (
            "EmailCustomerDrafter BlogPostDrafter LinkedInPostDrafter CustomerEmpathyCheck "
            "ExecutiveBriefingDrafter PostDemoFollowup ProposalDrafter RFPResponseDrafter"
        ),
    },
    "regulatory-review": {
        "requires": ["core"], "skills": "", "agents": "EUAIActReviewer GDPRReviewer SOC2Reviewer",
    },
}


class CatalogSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = support.load_catalog()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=os.environ["TEMP"], prefix="selection-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.source = self.base / "source"
        self.target = self.base / "target"
        self.target.mkdir()
        (self.target / "sentinel").write_text("preserve target", encoding="utf-8")
        self.write("lib/cli-tiers.yaml", (ROOT / "lib/cli-tiers.yaml").read_text(encoding="utf-8"))
        self.write("config/aliases.yaml", "skill_aliases:\n  - old: prior\n    new: alpha\n")
        self.write("install/upstream-sources.yaml", "bundled_materials: {}\n")
        self.write("skills/alpha/SKILL.md", "---\nname: alpha\nlayer: foundation\ndescription: Alpha method\nvoice: internal\ncli_support: [copilot]\n---\nSECRET BODY ALPHA\n")
        self.write("skills/staged/SKILL.md", "---\nname: staged\nlayer: foundation\ndescription: TEMPLATE ONLY - unimplemented example\nvoice: internal\ncli_support: [copilot]\n---\nSECRET BODY STAGED\n")
        self.write("agents/engineering/Role.md", "---\nname: Role\ncategory: engineering\ndescription: Selected role\nvoice: internal\ncli_support: [codex]\n---\nSECRET BODY ROLE\n")
        self.write("docs/core.md", "# Synthetic core\n")
        self.write("docs/example.md", "# Example\n\nSynthetic inputs and expected draft.\n")
        self.descriptor = {
            "schema_version": 1, "shared": "core",
            "selections": {
                "core": self.selection(["skill:alpha"], source="docs/core.md"),
                "pilot": self.selection(["agent:Role", "skill:staged"], requires=["core"]),
            },
            "source_stages": {"skill:staged": {
                "status": "staged",
                "evidence": {"path": "skills/staged/SKILL.md", "quote": "TEMPLATE ONLY",
                             "description_sha256": hashlib.sha256(b"TEMPLATE ONLY - unimplemented example").hexdigest()},
            }},
        }
        self.save()

    def write(self, relative, text):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def selection(self, members, *, source="agents/engineering/Role.md", requires=()):
        return {
            "source": source, "members": members, "requires": list(requires),
            "resources": ["docs/example.md"], "provenance": [],
            "inputs": ["Approved synthetic brief"], "outputs": ["Draft response; caller persists"],
            "example": {"path": "docs/example.md", "heading": "# Example"},
            "limitations": ["Not host execution or release clearance"],
        }

    def save(self):
        self.write("lib/capability-selections.json", json.dumps(self.descriptor))

    def cli(self, *args, source=None):
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(TOOL), "--source-root", str(source or self.source), *args],
            cwd=self.target, capture_output=True, check=False,
        )

    def refused(self, *args):
        before = support.files_snapshot(self.base)
        result = self.cli("--json", "--selection=pilot", *args)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, b"")
        self.assertTrue(result.stderr)
        self.assertEqual(support.files_snapshot(self.base), before)
        return result

    def test_actual_demo_script_closure_and_shared_contract(self):
        before = support.files_snapshot(self.base)
        result = self.cli("--json", "--selection=demo-script", source=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        ids = {entry["id"] for entry in value["entries"]}
        expected = {"agent:DemoNarrativeArc", "agent:DemoNarratorJunior", "agent:SlideNarrationCritic"}
        self.assertEqual({name for name in ids if name.startswith("agent:")}, expected)
        self.assertTrue({f"skill:{name}" for name in (
            "cycle", "sense", "scope", "define", "discover", "plan", "build", "review",
            "ship", "capture", "resume", "compliance-gate",
        )}.issubset(ids))
        self.assertEqual(value["selection"]["order"], ["core", "demo-script"])
        self.assertEqual(value["selection"]["requested"], ["demo-script"])
        self.assertEqual(value["selection"]["provenance"], [])
        self.assertFalse(value["executed"])
        self.assertTrue(all(entry["maturity"] == "unknown" for entry in value["entries"]))
        resources = {item["path"] for item in value["selection"]["resources"]}
        self.assertIn("skills/review/references/evidence.md", resources)
        self.assertIn("docs/concepts/pack-resolver.md", resources)
        self.assertIn("shims/universal/ADAPTER.md", resources)
        self.assertNotIn("agents/doc-gen/PPTNarrativeArchitect.md", resources)
        self.assertEqual(support.files_snapshot(self.base), before)
        self.assertNotIn(b"## Behavioral traits", result.stdout)

    def test_selection_index_retains_actual_stage_evidence_and_no_mature_claim(self):
        result = self.cli("--json", "--list-selections", source=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(
            [item["id"] for item in value["selections"]],
            sorted({"core", "demo-script", *FAMILIES}),
        )
        stages = {item["id"]: item for item in value["source_stages"]}
        self.assertEqual(set(stages), {"skill:generate-pdf", "skill:generate-visio", "skill:generate-xlsx"})
        self.assertEqual(stages["skill:generate-visio"]["status"], "staged")
        for member in ("skill:generate-pdf", "skill:generate-xlsx"):
            self.assertEqual(stages[member]["status"], "unknown")
            self.assertIsNone(stages[member]["evidence"])
        self.assertFalse(value["executed"])

    def test_closure_is_deterministic_deduplicated_and_explained(self):
        self.descriptor["selections"]["aux"] = self.selection(["agent:Role"], requires=["core"])
        self.descriptor["selections"]["pilot"]["requires"] = ["aux", "core"]
        self.save()
        first = self.cli("--json", "--selection=pilot", "--selection=aux")
        second = self.cli("--json", "--selection=aux", "--selection=pilot")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        value = json.loads(first.stdout)
        self.assertEqual(value["selection"]["order"], ["core", "aux", "pilot"])
        self.assertEqual(len(value["entries"]), 3)
        reasons = {item["id"]: item["reasons"] for item in value["selection"]["members"]}
        self.assertEqual(reasons["agent:Role"], ["member-of:aux", "member-of:pilot"])
        resources = value["selection"]["resources"]
        self.assertEqual(len(resources), len({item["path"] for item in resources}))
        example = next(item for item in resources if item["path"] == "docs/example.md")
        self.assertIn("resource-of:core", example["reasons"])
        self.assertIn("example-of:pilot", example["reasons"])

    def test_filters_apply_after_closure_without_erasing_required_resources(self):
        value = json.loads(self.cli("--json", "--selection=pilot", "--kind=skill", "--name=prior").stdout)
        self.assertEqual([item["id"] for item in value["entries"]], ["skill:alpha"])
        self.assertEqual(value["selection"]["order"], ["core", "pilot"])
        self.assertEqual(len(value["selection"]["members"]), 3)
        empty = self.cli("--json", "--selection=pilot", "--query=$(touch not-a-command)")
        self.assertEqual(empty.returncode, 0, empty.stderr)
        self.assertEqual(json.loads(empty.stdout)["matched"], 0)
        self.assertFalse((self.target / "not-a-command").exists())

    def test_no_selection_does_not_read_or_require_new_descriptor(self):
        before = self.cli("--json", "--kind=all")
        self.assertEqual(before.returncode, 0, before.stderr)
        path = self.source / "lib/capability-selections.json"
        for text in ("{}", "", "malformed ["):
            path.write_text(text)
            after = self.cli("--json", "--kind=all")
            self.assertEqual((before.returncode, before.stdout, before.stderr),
                             (after.returncode, after.stdout, after.stderr))
        path.unlink()
        self.assertEqual(self.cli("--json", "--kind=all").stdout, before.stdout)

    def test_queries_validate_whole_descriptor_and_inventory_before_filters(self):
        self.descriptor["selections"]["unselected"] = self.selection(["agent:Missing"])
        self.save()
        self.refused("--query=no-match")
        del self.descriptor["selections"]["unselected"]
        self.save()
        self.write("agents/engineering/Decoy.md", "---\nname: Decoy\ncategory: engineering\ndescription: Decoy\nvoice: internal\ncli_support: [codex]\ndeprecated_aliases: [Role]\n---\n")
        self.refused("--name=prior")

    def test_repeated_unknown_members_and_dependency_cycles_are_errors(self):
        original = copy.deepcopy(self.descriptor)
        for members, requires in (
            (["agent:Missing"], []), (["agent:Role", "agent:Role"], []),
            (["skill:prior"], []), (["agent:Role"], ["missing"]),
            (["agent:Role"], ["core", "core"]), (["agent:Role"], ["pilot"]),
        ):
            self.descriptor = copy.deepcopy(original)
            self.descriptor["selections"]["pilot"]["members"] = members
            self.descriptor["selections"]["pilot"]["requires"] = requires
            self.save()
            self.refused("--query=no-match")
        self.descriptor = copy.deepcopy(original)
        self.descriptor["selections"]["core"]["requires"] = ["pilot"]
        self.save()
        self.refused()

    def test_malformed_descriptors_and_literal_selection_ids_refuse(self):
        for text in ("", "[]", '{"schema_version":1,"schema_version":1}', '{"schema_version":99}',
                     '{"schema_version":true}', '{"selections":{}}'):
            self.write("lib/capability-selections.json", text)
            self.refused()
        self.save()
        for args in (("--selection=",), ("--selection= ",), ("--selection=*",),
                     ("--selection=../pilot",), ("--selection=$(touch marker)",),
                     ("--selection=pilot",), ("--list-selections",), ("--check",)):
            self.refused(*args)
        self.assertFalse((self.target / "marker").exists())
        result = self.cli("--selection=pilot")
        self.assertNotEqual(result.returncode, 0)
        with self.assertRaises(ValueError):
            self.catalog.selection_metadata(self.source, query="")

    def test_invalid_field_types_and_unsupported_claims_fail_before_output(self):
        original = copy.deepcopy(self.descriptor)
        for mutate in (
            lambda d: d.update(shared=[]),
            lambda d: d.update(source_stages=[]),
            lambda d: d.update(maturity="mature"),
            lambda d: d["selections"].update({"PILOT": d["selections"].pop("pilot")}),
            lambda d: d["selections"]["pilot"].update(members=[{}]),
            lambda d: d["selections"]["pilot"].update(members=[]),
            lambda d: d["selections"]["pilot"].update(requires=False),
            lambda d: d["selections"]["pilot"].update(inputs=[]),
            lambda d: d["selections"]["pilot"].update(outputs=[4]),
            lambda d: d["selections"]["pilot"].update(limitations=[""]),
            lambda d: d["selections"]["pilot"].update(resources=["docs/example.md", "docs/example.md"]),
            lambda d: d["selections"]["pilot"].update(source="../target/sentinel"),
            lambda d: d["selections"]["pilot"].update(example={"path": "docs/example.md", "heading": "missing heading shape"}),
            lambda d: d["selections"]["pilot"].update(executed=True),
        ):
            with self.subTest(mutate=mutate):
                self.descriptor = copy.deepcopy(original)
                mutate(self.descriptor)
                self.save()
                self.refused("--query=no-match")

    def test_paths_must_be_explicit_normalized_source_files(self):
        original = copy.deepcopy(self.descriptor)
        for path in ("../target/sentinel", str(self.target / "sentinel"), "C:secret",
                     r"docs\example.md", "docs//example.md", "docs/./example.md",
                     "docs/../docs/example.md", "docs/missing.md", "docs",
                     "DOCS/example.md",
                     ".claude/runtime/private.md"):
            self.descriptor = copy.deepcopy(original)
            self.descriptor["selections"]["pilot"]["resources"] = [path]
            self.save()
            self.refused()
        self.descriptor = original
        self.descriptor["selections"]["pilot"]["resources"] = ["docs/example.md"] * 2
        self.save()
        self.refused()

    def test_no_unrelated_prompt_body_read_or_exposure(self):
        original = Path.read_bytes
        def bounded(path):
            if path.name == "SKILL.md" or path.parent.parent.name == "agents":
                raise AssertionError("selection read a prompt body")
            return original(path)
        with mock.patch.object(Path, "read_bytes", bounded):
            result = self.catalog.selection_metadata(self.source, ["pilot"])
        encoded = json.dumps(result)
        self.assertNotIn("SECRET BODY", encoded)
        self.assertEqual({item["id"] for item in result["entries"]}, {"skill:alpha", "skill:staged", "agent:Role"})

    def test_linked_selection_resource_is_refused(self):
        resource = self.source / "docs/example.md"
        original = Path.lstat
        def linked(path):
            result = original(path)
            if path == resource:
                return mock.Mock(st_file_attributes=0x400, st_mode=result.st_mode)
            return result
        with mock.patch.object(Path, "lstat", linked):
            with self.assertRaisesRegex(ValueError, "linked|reparse"):
                self.catalog.selection_metadata(self.source, ["pilot"])

    def test_actual_selection_examples_resolve_without_becoming_execution_evidence(self):
        data = self.catalog.selection_metadata(ROOT)
        for record in data["selections"]:
            text = (ROOT / record["example"]["path"]).read_text(encoding="utf-8")
            self.assertIn(record["example"]["heading"], text.splitlines())
            self.assertTrue(record["inputs"] and record["outputs"] and record["limitations"])
        result = self.catalog.selection_metadata(ROOT, ["demo-script"])
        demo = next(record for record in result["selection"]["definitions"] if record["id"] == "demo-script")
        self.assertIn("Critique", " ".join(demo["outputs"]))
        self.assertIn("caller", " ".join(demo["outputs"]))
        self.assertFalse(result["executed"])

    def test_data_and_target_helpers_are_not_selection_code(self):
        trap = "from pathlib import Path\nPath('selection-decoy').write_text('NO')\nraise RuntimeError('target code')\n"
        for directory in (self.source / "lib", self.target):
            for name in ("envelope_contract.py", "client_capabilities.py"):
                (directory / name).write_text(trap, encoding="utf-8")
        before = support.files_snapshot(self.base)
        result = self.cli("--json", "--selection=pilot")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(support.files_snapshot(self.base), before)
        self.assertFalse((self.target / "selection-decoy").exists())

    def test_stage_requires_current_exact_description_evidence(self):
        value = json.loads(self.cli("--json", "--selection=pilot").stdout)
        stages = {item["id"]: item for item in value["selection"]["source_stages"]}
        self.assertEqual(stages["skill:staged"]["status"], "staged")
        self.assertEqual(stages["agent:Role"]["status"], "unknown")
        original = copy.deepcopy(self.descriptor)
        for mutate in (
            lambda d: d["source_stages"]["skill:staged"].update(status="mature"),
            lambda d: d["source_stages"]["skill:staged"].update(evidence=None),
            lambda d: d["source_stages"]["skill:staged"]["evidence"].update(path="skills/alpha/SKILL.md"),
            lambda d: d["source_stages"]["skill:staged"]["evidence"].update(quote="READY TO SHIP"),
            lambda d: d["source_stages"]["skill:staged"]["evidence"].update(description_sha256="0" * 64),
            lambda d: d["source_stages"].update({"skill:missing": {"status": "unknown", "evidence": None}}),
        ):
            self.descriptor = copy.deepcopy(original)
            mutate(self.descriptor)
            self.save()
            self.refused("--query=no-match")
        self.descriptor = original
        self.save()
        path = self.source / "skills/staged/SKILL.md"
        path.write_text(path.read_text().replace("unimplemented example", "changed source description"))
        self.refused()

    def test_unknown_stage_after_source_implementation_does_not_promote_maturity(self):
        path = self.source / "skills/staged/SKILL.md"
        path.write_text(path.read_text().replace(
            "TEMPLATE ONLY - unimplemented example",
            "Source method available; native validation remains unverified",
        ))
        self.refused()
        self.descriptor["source_stages"]["skill:staged"] = {"status": "unknown", "evidence": None}
        self.save()
        before = support.files_snapshot(self.base)
        result = self.cli("--json", "--selection=pilot")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        stages = {item["id"]: item for item in value["selection"]["source_stages"]}
        self.assertEqual(stages["skill:staged"], {
            "id": "skill:staged", "status": "unknown", "evidence": None,
        })
        self.assertTrue(all(entry["maturity"] == "unknown" for entry in value["entries"]))
        self.assertFalse(value["executed"])
        self.assertEqual(support.files_snapshot(self.base), before)

    def provenance(self):
        notice = self.write("skills/alpha/NOTICE.txt", "Synthetic fixture notice; no imported content.\n")
        attribution = self.write("skills/alpha/ATTRIBUTION.md", "# Synthetic attribution\n")
        data = {"bundled_materials": {"fixture": {
            "source": "https://example.invalid/synthetic", "import_commit": None,
            "relationship": "adapted", "local_paths": ["skills/alpha"],
            "license": "MIT", "notice": notice.relative_to(self.source).as_posix(),
            "attribution": attribution.relative_to(self.source).as_posix(),
            "modifications": "Synthetic test fixture only",
        }}}
        self.write("install/upstream-sources.yaml", json.dumps(data))
        self.descriptor["selections"]["core"]["provenance"] = ["fixture"]
        self.save()
        return notice, attribution

    def test_provenance_closure_retains_unknown_import_and_notices(self):
        notice, attribution = self.provenance()
        before = support.files_snapshot(self.base)
        result = self.cli("--json", "--selection=pilot")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        record = value["selection"]["provenance"][0]
        self.assertEqual(record["id"], "fixture")
        self.assertIsNone(record["import_commit"])
        paths = {item["path"] for item in value["selection"]["resources"]}
        self.assertIn(notice.relative_to(self.source).as_posix(), paths)
        self.assertIn(attribution.relative_to(self.source).as_posix(), paths)
        self.assertEqual(support.files_snapshot(self.base), before)
        self.assertNotIn("Synthetic fixture notice", result.stdout.decode())

    def test_missing_unknown_or_omitted_required_provenance_refuses(self):
        notice, attribution = self.provenance()
        self.descriptor["selections"]["core"]["provenance"] = []
        self.save()
        self.refused()
        self.descriptor["selections"]["core"]["provenance"] = ["unknown"]
        self.save()
        self.refused()
        self.descriptor["selections"]["core"]["provenance"] = ["fixture"]
        self.save()
        for path in (notice, attribution):
            original = path.read_bytes()
            path.unlink()
            self.refused()
            path.write_bytes(original)
            path.write_bytes(b"")
            self.refused()
            path.write_bytes(original)

    def test_core_cannot_be_skipped_and_no_company_policy_is_loaded(self):
        self.descriptor["selections"]["pilot"]["requires"] = []
        self.save()
        result = self.cli("--json", "--selection=pilot")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertIn("core", value["selection"]["order"])
        self.assertIn("shared", value["selection"]["reasons"]["core"])
        self.assertNotIn("profile", value)
        self.assertNotIn("required_policy", value)
        self.assertFalse((self.target / ".claude").exists())
        self.descriptor["shared"] = "missing"
        self.save()
        self.refused()

    def test_actual_optional_families_use_exact_existing_members_and_dependencies(self):
        value = self.catalog.selection_metadata(ROOT)
        records = {record["id"]: record for record in value["selections"]}
        self.assertEqual(set(records), {"core", "demo-script", *FAMILIES})
        for name, expected in FAMILIES.items():
            with self.subTest(selection=name):
                record = records[name]
                members = {f"skill:{skill}" for skill in expected["skills"].split()}
                members.update(f"agent:{agent}" for agent in expected["agents"].split())
                self.assertEqual(set(record["members"]), members)
                self.assertEqual(record["requires"], expected["requires"])
                self.assertEqual(len(record["members"]), len(members))
                selected = self.catalog.selection_metadata(ROOT, [name])
                self.assertIn("core", selected["selection"]["order"])
                self.assertTrue(members <= {entry["id"] for entry in selected["entries"]})
                self.assertFalse(selected["executed"])
                self.assertTrue(all(entry["maturity"] == "unknown" for entry in selected["entries"]))
                self.assertNotIn("profile", selected)
                self.assertNotIn("required_policy", selected)

    def test_standalone_formats_do_not_require_pipeline_or_other_format_bodies(self):
        for name, format_skill in (
            ("document-word", "generate-word"), ("document-pdf", "generate-pdf"),
            ("document-xlsx", "generate-xlsx"),
        ):
            with self.subTest(selection=name):
                value = self.catalog.selection_metadata(ROOT, [name])
                self.assertEqual(value["selection"]["order"], ["core", name])
                skills = {entry["name"] for entry in value["entries"] if entry["kind"] == "skill"}
                self.assertIn(format_skill, skills)
                self.assertTrue({"generate", "generate-design", "frontend-design", "generate-visio"}.isdisjoint(skills))
                self.assertEqual(
                    skills & {"generate-word", "generate-ppt", "generate-pdf", "generate-xlsx"},
                    {format_skill},
                )
        customer = self.catalog.selection_metadata(ROOT, ["customer-communication"])
        self.assertNotIn("demo-script", customer["selection"]["order"])
        self.assertTrue({"agent:DemoNarrativeArc", "agent:DemoNarratorJunior"}.isdisjoint(
            entry["id"] for entry in customer["entries"]
        ))
        visio = self.catalog.selection_metadata(ROOT, ["document-visio"])
        stages = {record["id"]: record for record in visio["selection"]["source_stages"]}
        self.assertEqual(stages["skill:generate-visio"]["status"], "staged")
        self.assertNotIn("agent:NetworkArchitect", {entry["id"] for entry in visio["entries"]})

    def test_actual_family_unions_are_deterministic_and_preserve_every_reason(self):
        requested = ["frontend-design", "document-ppt", "customer-communication", "demo-script"]
        before = support.files_snapshot(self.base)
        first = self.cli("--json", *("--selection=" + name for name in requested), source=ROOT)
        second = self.cli("--json", *("--selection=" + name for name in reversed(requested)), source=ROOT)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        value = json.loads(first.stdout)
        order = value["selection"]["order"]
        self.assertEqual(order.count("core"), 1)
        self.assertEqual(order.count("design-knowledge"), 1)
        self.assertLess(order.index("design-knowledge"), order.index("frontend-design"))
        reasons = {record["id"]: record["reasons"] for record in value["selection"]["members"]}
        self.assertEqual(
            reasons["agent:SlideNarrationCritic"], ["member-of:demo-script", "member-of:document-ppt"],
        )
        paths = [record["path"] for record in value["selection"]["resources"]]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(support.files_snapshot(self.base), before)

    def test_actual_design_source_resources_and_both_notices_are_retained(self):
        for name in ("design-knowledge", "frontend-design", "document-content", "document-ppt"):
            with self.subTest(selection=name):
                value = self.catalog.selection_metadata(ROOT, [name])
                resources = {record["path"] for record in value["selection"]["resources"]}
                provenance = {record["id"]: record for record in value["selection"]["provenance"]}
                self.assertEqual(set(provenance), {"design-dna-corpus", "design-dna-example-profile"})
                self.assertEqual(provenance["design-dna-corpus"]["license"], "MIT")
                self.assertEqual(provenance["design-dna-example-profile"]["license"], "Apache-2.0")
                for record in provenance.values():
                    self.assertIsNone(record["import_commit"])
                    self.assertIn(record["notice"], resources)
                    self.assertIn(record["attribution"], resources)
                    self.assertTrue(record["modifications"])
                csv_paths = {
                    path.relative_to(ROOT).as_posix()
                    for path in (ROOT / "skills/design-dna/data").rglob("*.csv")
                }
                self.assertTrue(csv_paths <= resources)
                for path in (
                    "skills/design-dna/scripts/design_contract.py",
                    "skills/design-dna/references/design-contract.schema.json",
                    "skills/design-dna/scripts/search.py", "skills/design-dna/scripts/core.py",
                    "skills/design-dna/scripts/design_system.py",
                    "skills/design-dna/scripts/emit_tokens.py",
                    "skills/design-dna/scripts/validate_design.py",
                    "skills/design-dna/profiles/anthropic-default.yaml",
                    "lib/context_safety.py", "lib/native_paths.py", "lib/profile_context.py",
                    "lib/review_contract.py", "lib/markdown_source.py",
                ):
                    self.assertIn(path, resources)

    def test_format_sources_keep_standalone_and_pipeline_admission_distinct(self):
        expected = {
            "document-word": {
                "skills/generate-word/references/native-word.md",
                "skills/generate-write/references/fidelity-and-evidence.md",
            },
            "document-ppt": {
                "skills/generate-ppt/references/native-powerpoint.md",
                "skills/design-dna/scripts/search.py",
                "skills/design-dna/data/slides/slide-strategies.csv",
            },
            "document-pdf": {
                "skills/generate-pdf/scripts/prepare_html.py",
                "skills/generate-pdf/scripts/print_pdf.mjs",
                "skills/generate-pdf/scripts/check_pdf.py",
                "skills/browse/scripts/chromium.mjs",
                "skills/browse/references/browser-operations.md",
            },
            "document-xlsx": {
                "skills/generate-xlsx/references/native-xlsx.md",
                "skills/generate-xlsx/scripts/check_xlsx.py",
                "skills/dh/references/decision-methods.md",
                "agents/engineering/CapacityPlanner.md",
            },
            "document-visio": {"skills/generate/agent-mapping.yaml"},
        }
        for name, paths in expected.items():
            with self.subTest(selection=name):
                value = self.catalog.selection_metadata(ROOT, [name])
                resources = {record["path"] for record in value["selection"]["resources"]}
                self.assertTrue(paths <= resources)
                self.assertNotIn("skills/generate/scripts/pipeline_inputs.py", resources)
                for relative in resources:
                    self.assertTrue((ROOT / relative).is_file())
                    self.assertNotIn("\\", relative)
                    self.assertFalse(any(part.startswith(".") for part in relative.split("/")))
                if name in ("document-pdf", "document-xlsx"):
                    member = "skill:generate-" + name.removeprefix("document-")
                    stage = next(row for row in value["selection"]["source_stages"] if row["id"] == member)
                    self.assertEqual(stage, {"id": member, "status": "unknown", "evidence": None})
        content = self.catalog.selection_metadata(ROOT, ["document-content"])
        record = next(row for row in content["selection"]["definitions"] if row["id"] == "document-content")
        required = {
            "skills/generate/scripts/pipeline_inputs.py", "bin/li-work-artifacts.py",
            "lib/swarm_contract.py", "lib/swarm_snapshot.py", "lib/swarm-schema.json",
            "lib/domain_result.py", "lib/domain-result-schema.json",
            "lib/context_safety.py", "lib/native_paths.py", "lib/markdown_source.py",
            "lib/review_contract.py", "lib/review-schema.json",
            "lib/profile_context.py", "lib/profile-context-schema.json",
            "skills/design-dna/scripts/design_contract.py",
            "skills/design-dna/scripts/emit_tokens.py",
            "skills/design-dna/references/design-contract.schema.json",
        }
        self.assertTrue(required <= {row["path"] for row in content["selection"]["resources"]})
        self.assertIn("input-only", " ".join(record["limitations"]))
        self.assertIn("not native", " ".join(record["limitations"]))
        for name in ("document-word", "document-ppt", "document-pdf", "document-xlsx"):
            union = self.catalog.selection_metadata(ROOT, ["document-content", name])
            self.assertTrue(required <= {row["path"] for row in union["selection"]["resources"]})
            self.assertFalse(union["executed"])

    def test_each_new_family_example_has_exact_heading_inputs_outputs_negative_and_limits(self):
        records = {item["id"]: item for item in self.catalog.selection_metadata(ROOT)["selections"]}
        for name in FAMILIES:
            with self.subTest(selection=name):
                example = records[name]["example"]
                self.assertEqual(example["path"], "skills/catalog/references/selections.md")
                text = (ROOT / example["path"]).read_text(encoding="utf-8")
                self.assertIn(example["heading"], text.splitlines())
                section = text.split(example["heading"] + "\n", 1)[1].split("\n## ", 1)[0]
                for label in ("**Inputs.**", "**Method and output.**", "**Negative.**", "**Evidence limit.**"):
                    self.assertIn(label, section)
                self.assertIn("--selection=" + name, section)

    def test_actual_family_queries_keep_literal_alias_and_body_boundaries(self):
        original = Path.read_text
        def metadata_only(path, *args, **kwargs):
            if path.name == "SKILL.md" or path.parent.parent.name == "agents":
                raise AssertionError("whole prompt read during family selection")
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, "read_text", metadata_only):
            selected = self.catalog.selection_metadata(
                ROOT, ["frontend-design", "document-word"], query="$(touch family-marker)",
            )
        self.assertEqual(selected["matched"], 0)
        self.assertTrue(selected["selection"]["resources"])
        before = support.files_snapshot(self.base)
        match = self.cli("--json", "--selection=frontend-design", "--name=match", source=ROOT)
        self.assertEqual(match.returncode, 0, match.stderr)
        self.assertEqual(json.loads(match.stdout)["matched"], 0)
        ordinary = self.cli("--json", "--name=match", source=ROOT)
        self.assertEqual(ordinary.returncode, 0, ordinary.stderr)
        self.assertEqual(json.loads(ordinary.stdout)["entries"][0]["id"], "skill:skill-router")
        self.assertNotIn("## Behavioral traits", json.dumps(selected))
        self.assertNotIn("## What this skill does", json.dumps(selected))
        self.assertEqual(support.files_snapshot(self.base), before)
        self.assertFalse((self.target / "family-marker").exists())

    def test_new_family_descriptor_faults_refuse_before_unmatched_filter_without_writes(self):
        path = ROOT / "lib/capability-selections.json"
        descriptor = self.catalog.load_text(path.read_text(encoding="utf-8"))
        original_read = Path.read_text
        for name in FAMILIES:
            for field, invalid in (
                ("members", ["agent:NetworkArchitect"]),
                ("resources", ["skills/catalog/references/absent-family-resource.md"]),
                ("requires", ["no-such-selection"]),
            ):
                with self.subTest(selection=name, field=field):
                    candidate = copy.deepcopy(descriptor)
                    candidate["selections"][name][field] = invalid
                    def changed(selected, *args, **kwargs):
                        return json.dumps(candidate) if selected == path else original_read(selected, *args, **kwargs)
                    before = support.files_snapshot(self.base)
                    expected_error = FileNotFoundError if field == "resources" else ValueError
                    with mock.patch.object(Path, "read_text", changed), self.assertRaises(expected_error):
                        self.catalog.selection_metadata(ROOT, [name], query="unmatched-literal")
                    self.assertEqual(support.files_snapshot(self.base), before)
        for name in ("design-knowledge", "frontend-design"):
            candidate = copy.deepcopy(descriptor)
            candidate["selections"][name]["provenance"] = []
            def omitted(selected, *args, **kwargs):
                return json.dumps(candidate) if selected == path else original_read(selected, *args, **kwargs)
            with mock.patch.object(Path, "read_text", omitted), self.assertRaisesRegex(ValueError, "provenance"):
                self.catalog.selection_metadata(ROOT, [name], query="unmatched-literal")

    def test_current_preservation_refresh_retains_recommendations_and_exact_delta(self):
        path = ROOT / ".claude/plans/universal-implementation/reports/P13-skills-preservation.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("42abfcba39ac80a271ff57e838ffccb1d7f6ed7c", text)
        self.assertIn("204ea7253b18fb1849fa6de94e1b283b098039b5", text)
        self.assertIn("73", text)
        self.assertIn("53", text)
        delta = text.split("## Accepted-source delta", 1)[1].split("## ", 1)[0]
        names = set(re.findall(r"^\| `([a-z0-9-]+)` \|", delta, re.M))
        self.assertEqual(len(names), 44)
        self.assertIn("swarm", names)
        for path in (
            "P04-final-08879e9.md", "P09-modules-5c99612.md",
            "P11-a14-a1b3a45.md", "P12-common-source-32dac88.md",
            "P13-consumers-4922a6b.md", "P12-pipeline-binding-d4e9188.md",
        ):
            self.assertIn(path, text)
        for role in (
            "DesignSystemAuditor", "FrontendArchitect", "MotionDirector",
            "ShaderEngineer", "TypographyCurator",
        ):
            self.assertIn(f"agents/frontend/{role}.md", text)

    def test_preservation_map_covers_exact_originals_and_swarm_with_grounded_columns(self):
        audit = ROOT / ".claude/engineering/audits/2026-09-20-universal-quality"
        originals = {}
        for file in ("workflow.json", "capabilities.json"):
            for record in json.loads((audit / "reviews" / file).read_text(encoding="utf-8"))["coverage"]:
                self.assertNotIn(record["name"], originals)
                originals[record["name"]] = record
        report = ROOT / ".claude/plans/universal-implementation/reports/P13-skills-preservation.md"
        text = report.read_text(encoding="utf-8")
        rows = {}
        for line in text.splitlines():
            if not line.startswith("| ["):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            match = re.fullmatch(r"\[([a-z0-9-]+)\]\(\.\./\.\./\.\./\.\./skills/\1/SKILL.md\)", cells[0])
            if not match:
                continue
            self.assertEqual(len(cells), 7)
            name = match.group(1)
            self.assertNotIn(name, rows)
            self.assertTrue(all(cells[1:]))
            self.assertRegex(cells[2], r"P\d{2}.*A\d{2}")
            if name in originals:
                self.assertTrue(cells[1].startswith(originals[name]["action"] + ";"))
            rows[name] = cells
        self.assertEqual(set(rows), set(originals) | {"swarm"})
        self.assertEqual(len(originals), 126)
        self.assertIn("P09-agent-preservation.md", text)
        self.assertIn("P04-preservation.md", text)
        self.assertIn("No original leaf is completed", text)
        aliases = self.catalog.load_text((ROOT / "config/aliases.yaml").read_text(encoding="utf-8"))["skill_aliases"]
        self.assertEqual(len(aliases), 46)
        for alias in aliases:
            self.assertIn("`" + alias["old"] + "`", text)
            if alias["new"] in ("ta", "da", "sc", "dh", "tq"):
                capability = alias["old"][len(alias["new"]) + 1:]
                body = (ROOT / "skills" / alias["new"] / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("| `" + capability + "` |", body)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            self.assertTrue((report.parent / target.split("#", 1)[0]).resolve().exists(), target)


if __name__ == "__main__":
    with support.isolated_environment():
        unittest.main()
