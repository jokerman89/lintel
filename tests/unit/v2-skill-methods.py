#!/usr/bin/env python3
# component: compatible-skill-method-regressions
# implements: ADR-0028, ADR-0029, ADR-0034
# intent: .claude/plans/v2-skill-corrections/spec.md
# constraints: inert synthetic fixtures; no model, live scanner, hook override or publication
# last_intent_review: 2026-09-30
"""Separate source assertions from actual catalog, lesson and domain/SHIP behavior."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODULES = runpy.run_path(str(ROOT / "tests/integration/domain-module-consumers.py"))
DATA = MODULES["DATA"]
OPTIONS = DATA["options"]
DOMAINS = ("ta", "da", "sc", "dh", "tq")
ENGINEERING = {f"skill:{name}" for name in (*DOMAINS, "full-engineering-pass")}
HANDOFF = ROOT / "skills/full-engineering-pass/references/domain-handoff.md"


def section(text: str, heading: str) -> str:
    match = re.search(rf"^{re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if match is None:
        raise AssertionError(f"Missing source section: {heading}")
    return match.group(1)


def caller_contract(module: str) -> str:
    path = ROOT / f"skills/{module}/SKILL.md"
    workflow = section(path.read_text(encoding="utf-8"), "## Workflow")
    links = re.findall(r"\]\(([^)]+domain-handoff\.md#module-caller-procedure)\)", workflow)
    if len(links) != 1 or (path.parent / links[0].split("#")[0]).resolve() != HANDOFF:
        raise AssertionError(f"{module}: admission must resolve to the one shared caller contract")
    return HANDOFF.read_text(encoding="utf-8")


class SourceContracts(unittest.TestCase):
    def test_ship_template_carries_actual_verdict_and_limits(self):
        text = (ROOT / "skills/ship/SKILL.md").read_text(encoding="utf-8")
        template = text.split("### Step 7 \u2014 PR creation (default path)\n", 1)[1].split(
            "\n### Step 8 \u2014 CI / deploy validation", 1,
        )[0]
        self.assertNotIn("Review: passed", template)
        self.assertIn("Review: <actual latest applicable verdict", template)
        self.assertIn("Review limitations:", template)
        self.assertIn("unverified", template)
        self.assertIn("blocked", template)
        self.assertIn("readiness", template)
        self.assertIn("publication", template)

    def test_lesson_report_distinguishes_assessment_from_enforcement(self):
        text = (ROOT / "skills/lessons-add/SKILL.md").read_text(encoding="utf-8")
        for claim in (
            "Layer 2 blocks", "scan on lesson body — BLOCKS", "**Compliance scan.**",
            "Sanity-scan applies",
        ):
            self.assertNotIn(claim, text)
        self.assertIn("li-lessons.py", text)
        self.assertIn("does not scan", text)
        self.assertIn("model-only", text)
        self.assertIn("unverified", text)
        self.assertIn("mandatory", text)
        self.assertIn("Content-safety evidence:", text)

    def test_modules_route_admission_without_repeating_the_algorithm(self):
        for module in DOMAINS:
            with self.subTest(module=module):
                text = (ROOT / f"skills/{module}/SKILL.md").read_text(encoding="utf-8")
                workflow = section(text, "## Workflow")
                self.assertIn("sole owner", workflow)
                self.assertIn("original", workflow)
                self.assertIn("P07", workflow)
                self.assertIn("independent", workflow)
                self.assertNotRegex(workflow, r"(?m)^[1-5]\. (?:Prepare|Record start|Externally prepare)")
                shared = caller_contract(module)
                for marker in (
                    "# lintel-module-context", "# lintel-module-select",
                    "Missing result: do not replay", "### Final verification and independent acceptance",
                ):
                    self.assertIn(marker, shared)
                self.assertIn("references/decision-methods.md", text)
                self.assertIn("## Checkpoint ownership", text)

    def test_ta_invariants_and_available_tools_replace_stale_prescriptions(self):
        text = (ROOT / "skills/ta/SKILL.md").read_text(encoding="utf-8")
        for old in ("(v4.", "New agents:", "cargo-complexity", "npx eslintcc"):
            self.assertNotIn(old, text)
        self.assertIn("invariant", section(text, "## Workflow"))
        self.assertIn("installed", text)
        self.assertIn("unverified", text)
        self.assertIn("optional", text)


class CatalogBehavior(unittest.TestCase):
    def query(self, *arguments: str) -> dict:
        catalog = ROOT / "skills/CATALOG.md"
        before = hashlib.sha256(catalog.read_bytes()).hexdigest()
        run = subprocess.run(
            [sys.executable, "-B", ROOT / "bin/li-catalog.py", "--json", *arguments],
            cwd=ROOT, capture_output=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stderr.decode("utf-8"))
        self.assertEqual(hashlib.sha256(catalog.read_bytes()).hexdigest(), before)
        result = json.loads(run.stdout)
        self.assertFalse(result["executed"])
        return result

    def test_actual_engineering_category_has_exact_six_existing_skills(self):
        selected = self.query("--kind=skill", "--category=engineering")
        self.assertEqual({entry["id"] for entry in selected["entries"]}, ENGINEERING)
        for entry in selected["entries"]:
            self.assertEqual(entry["maturity"], "unknown")
            self.assertEqual([hint["cli"] for hint in entry["cli_support"]], ["claude-code", "codex", "copilot"])

    def test_actual_selection_and_filters_preserve_core_and_method_closure(self):
        complete = self.query("--selection=engineering-modules")
        narrowed = self.query("--selection=engineering-modules", "--kind=skill", "--name=da")
        empty = self.query("--selection=engineering-modules", "--query=not-a-module-name")
        self.assertEqual(complete["selection"]["order"], ["core", "engineering-modules"])
        self.assertEqual(narrowed["selection"], complete["selection"])
        self.assertEqual(empty["selection"], complete["selection"])
        self.assertEqual([entry["id"] for entry in narrowed["entries"]], ["skill:da"])
        self.assertEqual(empty["entries"], [])
        definition = next(item for item in complete["selection"]["definitions"]
                          if item["id"] == "engineering-modules")
        self.assertEqual(set(definition["members"]), ENGINEERING)
        self.assertEqual(definition["requires"], ["core"])
        resources = {item["path"] for item in complete["selection"]["resources"]}
        self.assertIn("skills/full-engineering-pass/references/domain-handoff.md", resources)
        self.assertTrue({f"skills/{module}/references/decision-methods.md" for module in DOMAINS} <= resources)
        core = next(item for item in complete["selection"]["definitions"] if item["id"] == "core")
        inherited = set(core["resources"])
        self.assertTrue(inherited <= resources)
        self.assertTrue(inherited.isdisjoint(definition["resources"]))
        reasons = {item["path"]: item["reasons"] for item in complete["selection"]["resources"]}
        for path in inherited:
            self.assertIn("resource-of:core", reasons[path])
        admission_resources = {
            "bin/li-work-artifacts.py", "bin/li-domain-result.py", "bin/li-review-evidence.py",
            "bin/li-review-read", "bin/li-review-log", "bin/_audit.sh",
            "lib/workflow.sh", "lib/state.sh", "lib/paths.sh", "lib/cycle-modes.sh",
            "lib/pack-resolver.sh", "lib/pack-schema.yaml", "lib/profile_context.py",
            "lib/profile-context-schema.json", "lib/context_safety.py", "lib/native_paths.py",
            "lib/review_contract.py", "lib/review-schema.json", "lib/markdown_source.py",
            "lib/domain_result.py", "lib/domain-result-schema.json", "lib/swarm_contract.py",
            "lib/swarm_snapshot.py", "lib/swarm-schema.json", "lib/swarm_evidence.py",
        }
        self.assertEqual(admission_resources - resources, set())
        for path in admission_resources - inherited:
            self.assertIn("resource-of:engineering-modules", reasons[path])
        self.assertTrue(all(item["maturity"] == "unknown" for item in complete["entries"]))
        self.assertTrue(all(item["status"] == "unknown" and item["evidence"] is None
                            for item in complete["selection"]["source_stages"]))
        unrelated = self.query("--selection=demo-script")
        self.assertTrue(ENGINEERING.isdisjoint(item["id"] for item in unrelated["selection"]["members"]))


class SharedFixtures(MODULES["ModuleConsumers"]):
    def git(self, *arguments):
        return self.run_process([
            OPTIONS.git, "--no-pager", "-c", "core.autocrlf=false", "-c", "core.fsmonitor=false",
            "-c", "user.name=Synthetic fixture", "-c", "user.email=fixture@example.invalid", *arguments,
        ])

    def admission(self, *, expected=0, authority=""):
        contract = caller_contract(getattr(self, "module", "ta"))
        match = re.search(r"```python\n# lintel-module-select\n(.*?)```", contract, re.S)
        self.assertIsNotNone(match)
        run = self.run_process([
            sys.executable, "-B", "-c", match.group(1), ROOT, self.repo,
            ".claude/runtime/meta/prepare.json", authority,
        ], expected=expected)
        return json.loads(run.stdout) if run.returncode == 0 else None

    def exercise_module(self, module: str) -> None:
        self.module = module
        self.selected_map(domains=(module,))
        work = self.bind_request()
        self.assertEqual(work["binding"]["leaf_ids"], ["T014"])
        self.assertEqual(self.request["input_context"]["profile"], self.reference)
        self.assertEqual(self.request["input_context"]["required_policy"], self.policy)
        self.assertEqual(self.policy["status"], "loaded")
        self.produce()
        final = self.prepare_final()
        result = self.verify(command="summary")
        self.assertTrue(result["ok"])
        self.assertFalse(result["release_clearance"])
        self.assertEqual(result["review"], "not_evaluated")
        self.assertEqual(final["work"], work["binding"])
        changed = deepcopy(self.results[module])
        changed["controls"][0]["status"] = "unverified"
        self.write_json(self.result_path(module), changed)
        self.prepare_final()
        self.assertTrue(self.verify(command="summary", expected=3)["blocked"])

    def prepare_ship(self) -> dict:
        self.write("source.txt", b"Reviewed but not yet staged synthetic change.\n")
        self.selected_map()
        self.bind_request()
        self.produce()
        context = self.prepare_final()
        qa = self.verify()["qa"]
        self.write_json(".claude/runtime/meta/qa.json", qa)
        return context

    def review_fixture(self, context: dict, status="pass") -> None:
        checks = [{
            "id": name, "kind": "check", "requirement": "mandatory", "applicability": "applicable",
            "status": status, "reason": "Synthetic gate fixture, not real independent review.",
            "policy": deepcopy(self.controls[0]["policy"]), "evidence": ["evidence/ta.txt"], "observation": {},
        } for name in ("spec", "quality")]
        record = {
            "schema_version": 2, "skill": "review", "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(), "reason": "Synthetic latest-decision fixture.",
            "context": context, "reviewer": {"id": "synthetic-reviewer", "context": "review-1"},
            "provenance": "declared", "controls": checks + self.controls,
            "coverage": {"T014": context["required_controls"]},
            "evidence": DATA["evidence_manifest"](self.repo, checks + self.controls),
        }
        path = context["snapshot"]["record_path"]
        self.write_json(path, record)
        self.write_json(".claude/runtime/meta/corroboration.json", {
            "schema_version": 1, "kind": "human", "source": "synthetic-fixture-only",
            "reference": "not-a-real-independent-actor", "record_digest": DATA["content_digest"](record),
            "attempt_id": context["attempt_id"], "builder": context["builder"], "reviewer": record["reviewer"],
        })
        self.run_process([OPTIONS.bash, ROOT / "bin/li-review-log", "--file", self.repo / path])

    def ship(self, *, expected=0, corroboration=True) -> dict:
        arguments = [
            "ship", "--repo", self.repo, "--expected", self.repo / self.expected_path,
            "--qa", self.repo / ".claude/runtime/meta/qa.json",
        ]
        if corroboration:
            arguments += ["--corroboration", self.repo / ".claude/runtime/meta/corroboration.json"]
        return json.loads(self.p05(*arguments, expected=expected).stdout)

    def test_ship_absent_review_and_staged_input_still_block(self):
        context = self.prepare_ship()
        self.assertTrue(context["independence_required"])
        self.assertEqual(context["required_policy"], self.policy)
        missing = self.ship(expected=3, corroboration=False)
        self.assertFalse(missing["ok"])
        self.assertIn("No applicable review decision", missing["problems"])
        self.review_fixture(context)
        self.assertTrue(self.ship()["ok"])
        self.git("add", "source.txt")
        self.assertFalse(self.ship(expected=3)["ok"])

    def test_ship_latest_rejection_does_not_reuse_the_prior_pass(self):
        context = self.prepare_ship()
        self.review_fixture(context)
        self.assertTrue(self.ship()["ok"])
        self.review_fixture(context, status="fail")
        latest = self.ship(expected=3)
        self.assertFalse(latest["ok"])
        self.assertNotEqual(latest["status"], "pass")

    def test_real_lesson_writer_has_no_implicit_content_scan_receipt(self):
        marker = "INERT-CONTENT-MARKER: retain the chosen target."
        run = self.run_process([
            sys.executable, "-B", ROOT / "bin/li-lessons.py", "add",
            "--title", "Synthetic ownership lesson", "--body", marker,
        ])
        lessons = DATA["safety"].read_owned(self.repo, ".claude/memory/lessons.md")[0]
        self.assertIn(marker.encode(), lessons)
        self.assertNotRegex(run.stdout.lower(), r"(?:scan|safety).{0,20}(?:pass|clear)")
        text = (ROOT / "skills/lessons-add/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Content-safety evidence:", text)
        self.assertIn("model-only", text)


for _module in DOMAINS:
    def _module_case(self, module=_module):
        self.exercise_module(module)
    setattr(SharedFixtures, f"test_module_admission_{_module}", _module_case)


if __name__ == "__main__":
    suite = unittest.TestSuite()
    selected = {name.rsplit(".", 1)[-1] for name in DATA["test_args"]}
    retained = {
        "test_wrong_package_missing_parent_leaf_and_draft_refuse",
        "test_original_work_composition_missing_domain_blocks_high_scores",
        "test_fresh_shell_resume_preserves_cycle_map_and_operation",
        "test_started_attempt_cold_inspection_does_not_replay",
        "test_admission_scope_then_live_drift_refuses_before_continuation",
        "test_failed_error_unknown_and_zero_tests_block_even_high_score",
        "test_immutable_qa_obligations_cannot_be_removed_or_downgraded",
    }
    for case in (SourceContracts, CatalogBehavior, SharedFixtures):
        names = {name for name in case.__dict__ if name.startswith("test_")}
        if case is SharedFixtures:
            names |= retained
        for name in sorted(names & selected if selected else names):
            suite.addTest(case(name))
    if suite.countTestCases() == 0:
        raise SystemExit("ERROR: no selected V2 skill checks")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() and not result.skipped else 1)
