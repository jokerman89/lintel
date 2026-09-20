#!/usr/bin/env python3
# component: swarm-contract-tests
# implements: ADR-0026, ADR-0027
# intent: .claude/plans/swarming-work/spec.md
# constraints: hermetic temporary repositories; standard library only
# last_intent_review: 2026-09-20
"""Focused regression tests for the Lintel swarm contract."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Optional
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "lib"))
SPEC = importlib.util.spec_from_file_location("swarm_contract", REPO_ROOT / "lib/swarm_contract.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load swarm contract")
swarm = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = swarm
SPEC.loader.exec_module(swarm)


def diagnostic_codes(result: object) -> set[str]:
    return {item.code for item in result.diagnostics}


class SwarmFixture:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.coordination_path = ".claude/plans/example/swarm/coordination.json"
        self.work_map_path = ".claude/plans/example/work.json"
        self._write("spec.md", "# Specification\n")
        self._write("plan.md", "# Plan\n\n### BC1 — Core\n\n### BC2 — Adapter\n\n### BC3 — Docs\n")
        self._write("prompt.md", "Continue from the committed map.\n")
        self._write(".claude/plans/example/swarm/charter.md", "# Charter\n")
        for task_id in ("BC1", "BC2", "BC3"):
            self._write(f".claude/plans/example/swarm/briefs/{task_id}.md", f"# Brief {task_id}\n")
        self.work_map = {
            "schema_version": 1,
            "workflow": "lintel",
            "status": "APPROVED",
            "spec": "spec.md",
            "plan": "plan.md",
            "tasks": "plan.md",
            "prompt": "prompt.md",
            "execution_mode": "swarm",
            "coordination": self.coordination_path,
        }
        self.coordination = {
            "schema_version": 1,
            "initiative": "example",
            "work_map": self.work_map_path,
            "charter": ".claude/plans/example/swarm/charter.md",
            "integration_branch": "codex/example",
            "max_parallel": 2,
            "scope_rules": {
                "worker": "write_scope+own_report",
                "reviewer": "own_review",
                "reducers": "coordinator-only",
            },
            "lanes": [
                self._lane("BC1", 1, "src/core"),
                self._lane("BC2", 2, "src/adapter", isolation="git-worktree"),
                self._lane("BC3", 2, "docs/swarm", isolation="isolated-patch"),
            ],
        }
        self.save()

    def _lane(self, task_id: str, wave: int, scope: str, *, isolation: Optional[str] = None) -> dict[str, object]:
        lane: dict[str, object] = {
            "task_id": task_id,
            "wave": wave,
            "role": "Implementer",
            "write_scope": [scope],
            "brief": f".claude/plans/example/swarm/briefs/{task_id}.md",
            "report": f".claude/plans/example/swarm/reports/{task_id}.md",
            "review": f".claude/plans/example/swarm/reviews/{task_id}.md",
        }
        if isolation is not None:
            lane["isolation"] = isolation
        return lane

    def _write(self, relative: str, content: str) -> None:
        path = self.root.joinpath(*Path(relative).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def save(self) -> None:
        self._write(self.work_map_path, json.dumps(self.work_map, indent=2))
        self._write(self.coordination_path, json.dumps(self.coordination, indent=2))

    def validate(self):
        self.save()
        return swarm.validate_coordination(self.root, self.coordination_path)

    def write_evidence(
        self,
        lane: dict[str, object],
        *,
        out_of_scope: bool = False,
        stage: str = "PASS",
        report_overrides: Optional[dict[str, object]] = None,
        review_overrides: Optional[dict[str, object]] = None,
        verification_only: bool = False,
    ) -> None:
        task_id = str(lane["task_id"])
        report_path = str(lane["report"])
        scope = str(lane["write_scope"][0])
        product_path = f"{scope}/file.py"
        if not verification_only:
            self._write(product_path, f"observable result for {task_id}\n")
        changed = ([("outside/file.py" if out_of_scope else product_path)] if not verification_only else []) + [report_path]
        snapshot = swarm.snapshot_lane(self.root, self.coordination_path, task_id, "attempt-1")
        report = {
            "schema_version": swarm.EVIDENCE_VERSION,
            "artifact_kind": "swarm-report",
            "initiative": "example",
            "task_id": task_id,
            "status": "complete",
            "worker": f"worker-{task_id}",
            "actor_ref": f"synthetic:worker-{task_id}",
            "isolation_ref": f"temporary-fixture:{task_id}",
            **snapshot,
            "leaf_results": {leaf: [{"name": "focused acceptance test", "status": "PASS"}] for leaf in snapshot["leaf_ids"]},
            "changed_paths": changed,
            "checks": [{"name": "focused test", "status": "PASS"}],
            "limitations": [],
        }
        review = {
            "schema_version": swarm.EVIDENCE_VERSION,
            "artifact_kind": "swarm-review",
            "initiative": "example",
            "task_id": task_id,
            "status": "complete",
            "reviewer": f"reviewer-{task_id}",
            "actor_ref": f"synthetic:reviewer-{task_id}",
            "mode": "independent",
            "changed_paths": [str(lane["review"])],
            "verdict": "PASS" if stage == "PASS" else "FAIL",
            "stages": {"spec": stage, "quality": stage},
            "checks": [{"name": "independent inspection", "status": "PASS"}],
            "limitations": [],
        }
        if report_overrides:
            report.update(report_overrides)
        self._write(report_path, f"# Report\n\n{swarm.EVIDENCE_START}\n{json.dumps(report)}\n{swarm.EVIDENCE_END}\n")
        review["binding"] = swarm.review_binding(self.root, lane, report)
        if review_overrides:
            review.update(review_overrides)
        self._write(str(lane["review"]), f"# Review\n\n{swarm.EVIDENCE_START}\n{json.dumps(review)}\n{swarm.EVIDENCE_END}\n")


class SwarmContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="lintel-swarm-")
        self.fixture = SwarmFixture(Path(self.temporary.name))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _directory_alias(self, target: Path, alias: Path) -> None:
        target.mkdir(parents=True, exist_ok=True)
        alias.parent.mkdir(parents=True, exist_ok=True)
        try:
            alias.symlink_to(target, target_is_directory=True)
        except OSError:
            if os.name != "nt":
                raise
            created = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(alias), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            if created.returncode != 0:
                self.skipTest(f"directory aliases unavailable: {created.stderr or created.stdout}")

    def test_valid_contract_and_current_dogfood_contract(self) -> None:
        self.assertTrue(self.fixture.validate().ok)
        current = swarm.validate_coordination(
            REPO_ROOT,
            ".claude/plans/swarming-work/swarm/coordination.json",
        )
        self.assertTrue(current.ok, [item.as_dict() for item in current.diagnostics])

    def test_schema_identity_and_templates_are_parseable(self) -> None:
        schema = json.loads((REPO_ROOT / "lib/swarm-schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "https://lintel.dev/schemas/swarm-coordination-v1.json")
        self.assertEqual(schema["properties"]["schema_version"]["maximum"], 1)
        template = REPO_ROOT / "scaffolding/01-foundation/templates/swarm/coordination.template.json"
        self.assertEqual(json.loads(template.read_text(encoding="utf-8"))["schema_version"], 1)

    def test_bc2_sources_have_clean_whitespace(self) -> None:
        paths = (
            "lib/swarm-schema.json",
            "lib/swarm_contract.py",
            "bin/li-swarm",
            "bin/li-swarm.py",
            "scaffolding/01-foundation/templates/swarm/charter.template.md",
            "scaffolding/01-foundation/templates/swarm/coordination.template.json",
            "scaffolding/01-foundation/templates/swarm/agent-brief.template.md",
            "scaffolding/01-foundation/templates/swarm/agent-report.template.md",
            "scaffolding/01-foundation/templates/swarm/agent-review.template.md",
            "tests/unit/swarm-contract.py",
            ".claude/plans/swarming-work/swarm/reports/BC2.md",
        )
        for relative in paths:
            text = (REPO_ROOT / relative).read_text(encoding="utf-8")
            self.assertTrue(text.endswith("\n"), relative)
            bad_lines = [index for index, line in enumerate(text.splitlines(), 1) if line.endswith((" ", "\t"))]
            self.assertEqual(bad_lines, [], relative)

    def test_old_work_map_without_swarm_fields_remains_valid(self) -> None:
        old_map = copy.deepcopy(self.fixture.work_map)
        old_map.pop("execution_mode")
        old_map.pop("coordination")
        result = swarm.validate_work_map_swarm_fields(self.fixture.root, old_map, self.fixture.work_map_path)
        self.assertTrue(result.ok)
        self.assertIsNone(result.contract)

    def test_swarm_work_map_fields_are_atomic_and_point_back(self) -> None:
        incomplete = copy.deepcopy(self.fixture.work_map)
        incomplete.pop("coordination")
        result = swarm.validate_work_map_swarm_fields(self.fixture.root, incomplete, self.fixture.work_map_path)
        self.assertFalse(result.ok)
        self.assertIn("work_map.swarm_fields", diagnostic_codes(result))
        self.fixture.work_map["coordination"] = "other.json"
        result = self.fixture.validate()
        self.assertFalse(result.ok)
        self.assertIn("work_map.coordination", diagnostic_codes(result))

    def test_unsafe_paths_and_duplicate_json_keys_fail_closed(self) -> None:
        self.fixture.coordination["integration_branch"] = "codex/example\x7fhidden"
        result = self.fixture.validate()
        self.assertFalse(result.ok)
        self.assertIn("branch.invalid", diagnostic_codes(result))

        self.fixture = SwarmFixture(self.fixture.root)
        self.fixture.coordination["lanes"][0]["write_scope"] = ["../outside"]
        result = self.fixture.validate()
        self.assertFalse(result.ok)
        self.assertIn("path.unsafe", diagnostic_codes(result))

        for wildcard_path in ("src/*", "src/file?.py", "src/[ab].py"):
            with self.subTest(wildcard_path=wildcard_path):
                self.fixture = SwarmFixture(self.fixture.root)
                self.fixture.coordination["lanes"][0]["write_scope"] = [wildcard_path]
                result = self.fixture.validate()
                self.assertFalse(result.ok)
                self.assertIn("path.unsafe", diagnostic_codes(result))

        raw = '{"schema_version":1,"schema_version":1}'
        self.fixture._write(self.fixture.coordination_path, raw)
        result = swarm.validate_coordination(self.fixture.root, self.fixture.coordination_path)
        self.assertFalse(result.ok)
        self.assertIn("coordination.json", diagnostic_codes(result))

    def test_work_map_status_is_structural_but_only_approved_dispatches(self) -> None:
        cli = REPO_ROOT / "bin/li-swarm.py"
        for status in ("DRAFT", "COMPLETE"):
            with self.subTest(status=status):
                self.fixture.work_map["status"] = status
                self.fixture.save()
                structural = swarm.validate_coordination(self.fixture.root, self.fixture.coordination_path)
                self.assertTrue(structural.ok)

                result, frontier = swarm.ready_frontier(self.fixture.root, self.fixture.coordination_path)
                self.assertFalse(result.ok)
                self.assertIn("wave.work_map_status", diagnostic_codes(result))
                self.assertEqual(frontier["work_map_status"], status)
                self.assertEqual(frontier["ready_task_ids"], [])
                self.assertEqual(frontier["dispatch_task_ids"], [])

                wave = subprocess.run(
                    [sys.executable, str(cli), "wave", "--repo", str(self.fixture.root), "--coord", self.fixture.coordination_path],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(wave.returncode, 1)
                wave_result = json.loads(wave.stdout)
                self.assertFalse(wave_result["ok"])
                self.assertEqual(wave_result["frontier"]["dispatch_task_ids"], [])

                status_result = subprocess.run(
                    [sys.executable, str(cli), "status", "--repo", str(self.fixture.root), "--coord", self.fixture.coordination_path],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(status_result.returncode, 0, status_result.stderr + status_result.stdout)
                self.assertTrue(json.loads(status_result.stdout)["ok"])

        self.fixture.work_map["status"] = "INVENTED"
        invalid = self.fixture.validate()
        self.assertFalse(invalid.ok)
        self.assertIn("work_map.status", diagnostic_codes(invalid))

    def test_resolved_path_identity_closes_alias_bypasses(self) -> None:
        plan_alias = self.fixture.root / "plan-alias"
        self._directory_alias(self.fixture.root / ".claude/plans/example", plan_alias)
        scope = swarm.check_lane_scope(
            self.fixture.root,
            self.fixture.coordination_path,
            "BC1",
            ["plan-alias/swarm/reviews/BC1.md"],
        )
        self.assertFalse(scope.ok)
        self.assertIn("scope.reserved", diagnostic_codes(scope))

        self.fixture.coordination["lanes"][0]["write_scope"] = ["plan-alias"]
        protected = self.fixture.validate()
        self.assertFalse(protected.ok)
        self.assertIn("scope.protected", diagnostic_codes(protected))

        self.fixture = SwarmFixture(self.fixture.root)
        adapter_alias = self.fixture.root / "adapter-alias"
        self._directory_alias(self.fixture.root / "src/adapter", adapter_alias)
        self.fixture.coordination["lanes"][2]["write_scope"] = ["adapter-alias"]
        overlap = self.fixture.validate()
        self.assertFalse(overlap.ok)
        self.assertIn("wave.scope_overlap", diagnostic_codes(overlap))

        with tempfile.TemporaryDirectory(prefix="lintel-swarm-outside-") as outside:
            escape_alias = self.fixture.root / "escape-alias"
            self._directory_alias(Path(outside), escape_alias)
            self.fixture.coordination["lanes"][0]["write_scope"] = ["escape-alias"]
            escaped = self.fixture.validate()
            self.assertFalse(escaped.ok)
            self.assertIn("path.escape", diagnostic_codes(escaped))

    def test_universal_coordinator_paths_block_validation_scope_and_close(self) -> None:
        for protected_path in swarm.UNIVERSAL_COORDINATOR_PATHS:
            with self.subTest(protected_path=protected_path):
                fixture = SwarmFixture(self.fixture.root)
                fixture.coordination["lanes"][0]["write_scope"] = [protected_path]
                result = fixture.validate()
                self.assertFalse(result.ok)
                self.assertIn("scope.protected", diagnostic_codes(result))

        self.fixture = SwarmFixture(self.fixture.root)
        runtime_alias = self.fixture.root / "runtime-alias"
        self._directory_alias(self.fixture.root / ".claude/runtime", runtime_alias)
        self.fixture.coordination["lanes"][0]["write_scope"] = ["runtime-alias"]
        result = self.fixture.validate()
        self.assertFalse(result.ok)
        self.assertIn("scope.protected", diagnostic_codes(result))

        self.fixture = SwarmFixture(self.fixture.root)
        scope = swarm.check_lane_scope(
            self.fixture.root,
            self.fixture.coordination_path,
            "BC1",
            ["runtime-alias/attempt.json"],
        )
        self.assertFalse(scope.ok)
        self.assertIn("scope.universal", diagnostic_codes(scope))

        for lane in self.fixture.coordination["lanes"]:
            self.fixture.write_evidence(lane)
        lane = self.fixture.coordination["lanes"][0]
        self.fixture.write_evidence(
            lane,
            report_overrides={"changed_paths": ["runtime-alias/attempt.json", lane["report"]]},
        )
        close, states = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertFalse(close.ok)
        self.assertIn("scope.universal", diagnostic_codes(close))
        self.assertEqual(states[0]["state"], "invalid_report")

    def test_duplicate_lanes_and_duplicate_mapped_tasks_fail(self) -> None:
        self.fixture.coordination["lanes"].append(copy.deepcopy(self.fixture.coordination["lanes"][0]))
        result = self.fixture.validate()
        self.assertFalse(result.ok)
        self.assertIn("lane.duplicate", diagnostic_codes(result))
        self.fixture = SwarmFixture(self.fixture.root)
        self.fixture._write("plan.md", "# Plan\n\n### BC1 — First\n\n### BC1 — Duplicate\n\n### BC2 — Two\n\n### BC3 — Three\n")
        self.fixture.save()
        result = swarm.validate_coordination(self.fixture.root, self.fixture.coordination_path)
        self.assertFalse(result.ok)
        self.assertIn("tasks.duplicate", diagnostic_codes(result))

    def test_missing_brief_fails(self) -> None:
        self.fixture.coordination["lanes"][0]["brief"] = ".claude/plans/example/swarm/briefs/missing.md"
        result = self.fixture.validate()
        self.assertFalse(result.ok)
        self.assertIn("path.missing", diagnostic_codes(result))

    def test_handoff_artifacts_cannot_alias_coordinator_authority(self) -> None:
        protected = [
            self.fixture.work_map_path,
            self.fixture.coordination_path,
            str(self.fixture.coordination["charter"]),
            "plan.md",
            "spec.md",
            "prompt.md",
            ".claude/plans",
            ".claude/runtime/report.md",
            ".git/report.md",
        ]
        for artifact in ("brief", "report", "review"):
            for path in protected:
                with self.subTest(artifact=artifact, path=path):
                    fixture = SwarmFixture(self.fixture.root)
                    fixture.coordination["lanes"][0][artifact] = path
                    result = fixture.validate()
                    self.assertFalse(result.ok)
                    self.assertIn("artifact.coordinator", diagnostic_codes(result))

        self.fixture = SwarmFixture(self.fixture.root)
        self._directory_alias(self.fixture.root / ".claude/plans/example", self.fixture.root / "authority-alias")
        self.fixture.coordination["lanes"][0]["report"] = "authority-alias/work.json"
        self.assertIn("artifact.coordinator", diagnostic_codes(self.fixture.validate()))
        scope = swarm.check_lane_scope(
            self.fixture.root, self.fixture.coordination_path, "BC1", [self.fixture.work_map_path]
        )
        self.assertFalse(scope.ok, "the own-report exception must never grant authority writes")

    def test_handoff_artifacts_reject_ancestor_and_alias_overlap(self) -> None:
        self.fixture.coordination["lanes"][0]["report"] = ".claude/plans/example/swarm/reports"
        result = self.fixture.validate()
        self.assertFalse(result.ok)
        self.assertIn("artifact.overlap", diagnostic_codes(result))
        self.fixture = SwarmFixture(self.fixture.root)
        self._directory_alias(self.fixture.root / ".claude/plans/example/swarm/reviews", self.fixture.root / "review-alias")
        self.fixture.coordination["lanes"][0]["report"] = "review-alias/BC2.md"
        self.assertIn("artifact.overlap", diagnostic_codes(self.fixture.validate()))

    def test_project_coordinator_outputs_protect_scopes_and_handoffs(self) -> None:
        for actor_path in ("write_scope", "brief", "report", "review"):
            for path in ("skills/CATALOG.md", "skills", "generated/schema.json"):
                with self.subTest(actor_path=actor_path, path=path):
                    fixture = SwarmFixture(self.fixture.root)
                    fixture.coordination["coordinator_paths"] = ["skills/CATALOG.md", "generated"]
                    fixture.coordination["lanes"][0][actor_path] = [path] if actor_path == "write_scope" else path
                    result = fixture.validate()
                    self.assertFalse(result.ok)
                    expected = "scope.protected" if actor_path == "write_scope" else "artifact.coordinator"
                    self.assertIn(expected, diagnostic_codes(result))
        self.fixture = SwarmFixture(self.fixture.root)
        self.fixture.coordination["coordinator_paths"] = ["skills/CATALOG.md", "generated"]
        self.assertTrue(self.fixture.validate().ok)
        self._directory_alias(self.fixture.root / "skills", self.fixture.root / "skills-alias")
        self.fixture.coordination["lanes"][0]["write_scope"] = ["skills-alias/CATALOG.md"]
        self.assertIn("scope.protected", diagnostic_codes(self.fixture.validate()))
        self.fixture.coordination["coordinator_paths"] = ["../outside"]
        self.assertIn("path.unsafe", diagnostic_codes(self.fixture.validate()))

    def test_reviewer_owns_only_its_review_artifact(self) -> None:
        lane = self.fixture.coordination["lanes"][0]
        allowed = swarm.check_lane_scope(
            self.fixture.root, self.fixture.coordination_path, "BC1", [lane["review"]], actor="reviewer"
        )
        self.assertTrue(allowed.ok)
        for path in ("src/core/file.py", lane["report"], self.fixture.work_map_path,
                     self.fixture.coordination["lanes"][1]["review"], ".claude/runtime/review.json"):
            with self.subTest(path=path):
                result = swarm.check_lane_scope(
                    self.fixture.root, self.fixture.coordination_path, "BC1", [path], actor="reviewer"
                )
                self.assertFalse(result.ok)
        cli = subprocess.run(
            [sys.executable, str(REPO_ROOT / "bin/li-swarm.py"), "check-scope",
             "--repo", str(self.fixture.root), "--coord", self.fixture.coordination_path,
             "--task", "BC1", "--actor", "reviewer", "--changed", lane["review"]],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(cli.returncode, 0, cli.stderr + cli.stdout)

    def test_current_flat_phased_tree_and_spec_kit_task_formats(self) -> None:
        cases = (
            ("T1", "| ID | Title | Files | Deps | Owner / subagent | Tokens |\n"
                   "|---|---|---|---|---|---|\n| T1 | Implement core | src/core | - | builder | 100 |\n"
                   "\n### T1: Implement core\n**Acceptance:** Works.\n"),
            ("1.1", "## Phase 1\n| ID | Title | Files | Deps | Owner / subagent | Tokens |\n"
                    "|---|---|---|---|---|---|\n| 1.1 | Implement core | src/core | - | builder | 100 |\n"),
            ("1.1.a", "## Phase 1\n### 1.1 Parent\n- 1.1.a Implement core\n- 1.1.b Verify core\n"
                      "\n## Per-task detail\n### 1.1.a: Implement core\n**Acceptance:** Works.\n"),
            ("T001", "## Phase 1: Setup\n- [ ] T001 [P] [US1] Implement src/core/file.py\n"),
        )
        for task_id, content in cases:
            with self.subTest(task_id=task_id):
                fixture = SwarmFixture(self.fixture.root)
                fixture.coordination["lanes"] = [fixture.coordination["lanes"][0]]
                fixture.coordination["lanes"][0]["task_id"] = task_id
                fixture._write("plan.md", "# Plan\n\n" + content)
                result = fixture.validate()
                self.assertTrue(result.ok, [item.as_dict() for item in result.diagnostics])
                packages = swarm.package_sources(fixture.root, result.contract)
                self.assertEqual(packages[task_id]["leaf_ids"], [task_id])

    def _grouped_fixture(self) -> None:
        self.fixture.coordination["lanes"] = [self.fixture.coordination["lanes"][0]]
        self.fixture.coordination["lanes"][0]["task_id"] = "P1"
        self.fixture._write(
            "plan.md",
            "# Plan\n\n## Work packages\n"
            "| Package ID | Outcome | Leaf IDs (dependency order) | Owner / edit boundary | Dependencies | Acceptance evidence | Review |\n"
            "|---|---|---|---|---|---|---|\n"
            "| P1 | Core behavior | 1.1.a, 1.1.b | builder; src/core | - | per-leaf tests | substantive |\n"
            "\n## Phase 1\n### 1.1 Parent\n- [ ] 1.1.a Implement core\n- [ ] 1.1.b Verify core\n"
            "\n## Per-task detail\n### 1.1.a: Implement core\n**Acceptance:** Returns a value.\n"
            "**Dependencies:** none\n### 1.1.b: Verify core\n**Acceptance:** Negative input fails.\n"
            "**Dependencies:** 1.1.a\n",
        )
        self.fixture.save()

    def test_packages_reference_unchanged_leaves_and_review_depth(self) -> None:
        self._grouped_fixture()
        result = self.fixture.validate()
        self.assertTrue(result.ok, [item.as_dict() for item in result.diagnostics])
        package = swarm.package_sources(self.fixture.root, result.contract)["P1"]
        self.assertEqual(package["leaf_ids"], ["1.1.a", "1.1.b"])
        self.assertEqual(package["review"], "substantive")
        self.assertIn("Negative input fails.", package["leaves"]["1.1.b"]["text"])
        self.assertEqual(package["leaves"]["1.1.b"]["dependencies"], ["1.1.a"])

    def test_packages_reject_missing_duplicate_parent_and_unassigned_leaves(self) -> None:
        for before, after in (
            ("1.1.a, 1.1.b", "1.1.a, missing1"),
            ("1.1.a, 1.1.b", "1.1.a, 1.1.a, 1.1.b"),
            ("1.1.a, 1.1.b", "1.1, 1.1.b"),
            ("1.1.a, 1.1.b", "1.1.a"),
            ("1.1.a, 1.1.b", "1.1.b, 1.1.a"),
        ):
            with self.subTest(after=after):
                self._grouped_fixture()
                plan = self.fixture.root / "plan.md"
                plan.write_text(plan.read_text(encoding="utf-8").replace(before, after), encoding="utf-8")
                self.assertFalse(self.fixture.validate().ok)

    def test_wave_checks_authoritative_leaf_dependencies(self) -> None:
        self.fixture.coordination["lanes"][0]["wave"] = 2
        self.fixture.coordination["lanes"][1]["wave"] = 1
        self.fixture.coordination["lanes"][2]["wave"] = 3
        self.fixture._write("plan.md", "# Plan\n### BC1 Core\n### BC2 Adapter\n**Dependencies:** BC1\n### BC3 Docs\n")
        self.fixture.save()
        result, frontier = swarm.ready_frontier(self.fixture.root, self.fixture.coordination_path)
        self.assertEqual(frontier["dispatch_task_ids"], [])
        self.assertIn("BC1", frontier["blocked_by"]["BC2"])

    def test_grouped_lane_cannot_widen_the_authoritative_edit_boundary(self) -> None:
        self._grouped_fixture()
        self.fixture.coordination["lanes"][0]["write_scope"] = ["src"]
        self.assertIn("package.scope", diagnostic_codes(self.fixture.validate()))

    def test_real_brief_template_adapts_with_work_package_and_original_data(self) -> None:
        self._grouped_fixture()
        lane = self.fixture.coordination["lanes"][0]
        original = (REPO_ROOT / "scaffolding/01-foundation/templates/swarm/agent-brief.template.md").read_text(encoding="utf-8")
        original = original.replace("<task-id>", "P1").replace("<package-id>", "P1")
        original = original.replace("<observable acceptance condition>", "Each leaf has a passing focused check")
        original = original.replace("<authoritative input path>", "spec.md")
        self.fixture._write(lane["brief"], original)
        payload = swarm.brief_payload(self.fixture.root, self.fixture.coordination_path, "P1")
        self.assertEqual(payload["content"]["original_markdown"], original)
        self.assertEqual(payload["content"]["leaf_ids"], ["1.1.a", "1.1.b"])
        self.assertEqual(payload["content"]["work_map"], self.fixture.work_map_path)
        self.assertEqual(payload["content"]["write_scope"], ["src/core"])

    def test_same_wave_overlap_and_missing_isolation_fail(self) -> None:
        self.fixture.coordination["lanes"][2]["write_scope"] = ["src/adapter/subtree"]
        result = self.fixture.validate()
        self.assertFalse(result.ok)
        self.assertIn("wave.scope_overlap", diagnostic_codes(result))
        self.fixture = SwarmFixture(self.fixture.root)
        self.fixture.coordination["lanes"][1].pop("isolation")
        self.fixture.coordination["lanes"][2].pop("isolation")
        result = self.fixture.validate()
        self.assertFalse(result.ok)
        self.assertIn("wave.isolation_missing", diagnostic_codes(result))

    def test_sequenced_fallback_is_valid_and_explicit(self) -> None:
        self.fixture.coordination["max_parallel"] = 1
        self.fixture.coordination["lanes"][1].pop("isolation")
        self.fixture.coordination["lanes"][2].pop("isolation")
        result = self.fixture.validate()
        self.assertTrue(result.ok)
        self.assertIn("wave.sequenced", diagnostic_codes(result))

    def test_scope_allows_owned_path_and_own_report_only(self) -> None:
        allowed = swarm.check_lane_scope(
            self.fixture.root,
            self.fixture.coordination_path,
            "BC1",
            ["src/core/file.py", ".claude/plans/example/swarm/reports/BC1.md"],
        )
        self.assertTrue(allowed.ok)
        review = swarm.check_lane_scope(
            self.fixture.root,
            self.fixture.coordination_path,
            "BC1",
            [".claude/plans/example/swarm/reviews/BC1.md"],
        )
        self.assertFalse(review.ok)
        self.assertIn("scope.reserved", diagnostic_codes(review))
        outside = swarm.check_lane_scope(
            self.fixture.root,
            self.fixture.coordination_path,
            "BC1",
            ["src/adapter/file.py"],
        )
        self.assertFalse(outside.ok)
        self.assertIn("scope.outside", diagnostic_codes(outside))

    def test_ready_frontier_waits_for_review(self) -> None:
        result, frontier = swarm.ready_frontier(self.fixture.root, self.fixture.coordination_path)
        self.assertTrue(result.ok)
        self.assertEqual(frontier["wave"], 1)
        self.assertEqual(frontier["ready_task_ids"], ["BC1"])
        lane = self.fixture.coordination["lanes"][0]
        self.fixture.write_evidence(lane)
        (self.fixture.root / lane["review"]).unlink()
        result, frontier = swarm.ready_frontier(self.fixture.root, self.fixture.coordination_path)
        self.assertTrue(result.ok)
        self.assertEqual(frontier["wave"], 1)
        self.assertEqual(frontier["ready_task_ids"], [])
        self.assertEqual(frontier["states"][0]["state"], "awaiting_review")

    def test_report_is_fully_validated_before_awaiting_review(self) -> None:
        lane = self.fixture.coordination["lanes"][0]
        self.fixture.write_evidence(lane)
        (self.fixture.root / str(lane["review"])).unlink()
        result, frontier = swarm.ready_frontier(self.fixture.root, self.fixture.coordination_path)
        self.assertTrue(result.ok)
        self.assertEqual(frontier["states"][0]["state"], "awaiting_review")

        invalid_reports = (
            ({"schema_version": True}, "evidence.identity"),
            ({"checks": [{"name": "test", "status": "FAIL"}]}, "report.checks"),
            ({"changed_paths": []}, "report.changed_paths"),
            ({"changed_paths": ["src/core/file.py"]}, "report.own_report"),
            ({"changed_paths": [lane["report"]]}, "report.product_change"),
            ({"changed_paths": ["outside/file.py", lane["report"]]}, "scope.outside"),
        )
        for overrides, expected in invalid_reports:
            with self.subTest(expected=expected):
                self.fixture.write_evidence(lane, report_overrides=overrides)
                (self.fixture.root / str(lane["review"])).unlink()
                result, frontier = swarm.ready_frontier(self.fixture.root, self.fixture.coordination_path)
                self.assertFalse(result.ok)
                self.assertIn(expected, diagnostic_codes(result))
                self.assertEqual(frontier["states"][0]["state"], "invalid_report")
                self.assertNotEqual(frontier["states"][0]["state"], "awaiting_review")

    def test_close_evidence_fails_incomplete_then_passes(self) -> None:
        result, states = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertFalse(result.ok)
        self.assertEqual(states[0]["state"], "not_started")
        for lane in self.fixture.coordination["lanes"]:
            self.fixture.write_evidence(lane)
        result, states = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertTrue(result.ok, [item.as_dict() for item in result.diagnostics])
        self.assertTrue(all(state["state"] == "complete" for state in states))

    def test_changed_acceptance_result_report_and_attempt_revoke_completion(self) -> None:
        for mutation in ("acceptance", "result", "report", "attempt"):
            with self.subTest(mutation=mutation):
                with tempfile.TemporaryDirectory(prefix="lintel-swarm-binding-") as temporary:
                    fixture = SwarmFixture(Path(temporary))
                    for lane in fixture.coordination["lanes"]:
                        fixture.write_evidence(lane)
                    lane = fixture.coordination["lanes"][0]
                    if mutation == "acceptance":
                        fixture._write("spec.md", "# Specification\nNew mandatory acceptance.\n")
                    elif mutation == "result":
                        fixture._write("src/core/file.py", "unreviewed rework\n")
                    elif mutation == "report":
                        path = fixture.root / lane["report"]
                        path.write_text(path.read_text(encoding="utf-8") + "\nUnreviewed report amendment.\n", encoding="utf-8")
                    else:
                        path = fixture.root / lane["report"]
                        path.write_text(path.read_text(encoding="utf-8").replace("attempt-1", "attempt-2"), encoding="utf-8")
                    result, _ = swarm.verify_close(fixture.root, fixture.coordination_path)
                    self.assertFalse(result.ok, mutation)

    def test_nonexistent_product_path_is_not_evidence(self) -> None:
        for lane in self.fixture.coordination["lanes"]:
            self.fixture.write_evidence(lane)
        lane = self.fixture.coordination["lanes"][0]
        path = self.fixture.root / "src/core/file.py"
        if path.exists():
            path.unlink()
        result, _ = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertFalse(result.ok, "a claimed path with no observable result cannot close")

    def test_all_package_leaves_need_acceptance_evidence(self) -> None:
        self._grouped_fixture()
        lane = self.fixture.coordination["lanes"][0]
        self.fixture.write_evidence(lane, report_overrides={"leaf_results": {"1.1.a": [{"name": "test", "status": "PASS"}]}})
        result, _ = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertFalse(result.ok)

    def test_reviewer_scope_and_identity_bind_the_report(self) -> None:
        for overrides in (
            {"changed_paths": ["src/core/file.py"]},
            {"actor_ref": "synthetic:worker-BC1"},
            {"binding": {"report_digest": "0" * 64}},
        ):
            with self.subTest(overrides=overrides):
                for lane in self.fixture.coordination["lanes"]:
                    self.fixture.write_evidence(lane)
                self.fixture.write_evidence(self.fixture.coordination["lanes"][0], review_overrides=overrides)
                result, _ = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
                self.assertFalse(result.ok)

    def test_manual_review_export_never_creates_clearance(self) -> None:
        lane = self.fixture.coordination["lanes"][0]
        self.fixture.write_evidence(lane)
        (self.fixture.root / lane["review"]).unlink()
        exported = swarm.review_input(self.fixture.root, self.fixture.coordination_path, "BC1")
        self.assertEqual(exported["binding"]["package_id"], "BC1")
        self.assertNotIn("verdict", exported)
        self.assertIn("not review evidence", exported["independence"])
        result, frontier = swarm.ready_frontier(self.fixture.root, self.fixture.coordination_path, host_capability="none")
        self.assertTrue(result.ok)
        self.assertEqual(frontier["states"][0]["state"], "awaiting_review")

    def test_explicit_verification_only_package_needs_no_fictitious_edit(self) -> None:
        self._grouped_fixture()
        plan = self.fixture.root / "plan.md"
        plan.write_text(plan.read_text(encoding="utf-8").replace(
            "| Review |", "| Review | Result |"
        ).replace("|---|---|---|---|---|---|---|", "|---|---|---|---|---|---|---|---|").replace(
            "| substantive |", "| substantive | verification-only |"
        ), encoding="utf-8")
        self.fixture.save()
        self.fixture.write_evidence(self.fixture.coordination["lanes"][0], verification_only=True)
        result, states = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertTrue(result.ok, [item.as_dict() for item in result.diagnostics])
        self.assertEqual(states[0]["state"], "complete")

    def test_legacy_evidence_remains_historical_not_current_clearance(self) -> None:
        for lane in self.fixture.coordination["lanes"]:
            self.fixture.write_evidence(lane)
        lane = self.fixture.coordination["lanes"][0]
        path = self.fixture.root / lane["report"]
        body = path.read_text(encoding="utf-8").replace(swarm.EVIDENCE_START, swarm.LEGACY_EVIDENCE_START)
        body = body.replace('"schema_version": 2', '"schema_version": 1')
        path.write_text(body, encoding="utf-8")
        result, _ = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertFalse(result.ok)
        self.assertIn("evidence.unbound", diagnostic_codes(result))

    def test_checkbox_completion_does_not_change_acceptance_identity(self) -> None:
        self._grouped_fixture()
        self.fixture.write_evidence(self.fixture.coordination["lanes"][0])
        path = self.fixture.root / "plan.md"
        path.write_text(path.read_text(encoding="utf-8").replace("- [ ]", "- [x]"), encoding="utf-8")
        result, _ = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertTrue(result.ok, [item.as_dict() for item in result.diagnostics])

    def test_withdrawn_approval_or_external_prerequisite_prevents_close(self) -> None:
        self.fixture._write("plan.md", "# Plan\n- [x] T0 Baseline\n### BC1 Core\n**Dependencies:** T0\n### BC2 Adapter\n### BC3 Docs\n")
        for lane in self.fixture.coordination["lanes"]:
            self.fixture.write_evidence(lane)
        self.assertTrue(swarm.verify_close(self.fixture.root, self.fixture.coordination_path)[0].ok)
        self.fixture.work_map["status"] = "DRAFT"
        self.fixture.save()
        self.assertIn("close.work_map_status", diagnostic_codes(swarm.verify_close(self.fixture.root, self.fixture.coordination_path)[0]))
        self.fixture.work_map["status"] = "APPROVED"
        self.fixture.save()
        path = self.fixture.root / "plan.md"
        path.write_text(path.read_text(encoding="utf-8").replace("[x] T0", "[ ] T0"), encoding="utf-8")
        self.assertIn("close.prerequisites", diagnostic_codes(swarm.verify_close(self.fixture.root, self.fixture.coordination_path)[0]))

    def test_only_explicit_mechanical_packages_allow_inline_review(self) -> None:
        self._grouped_fixture()
        lane = self.fixture.coordination["lanes"][0]
        overrides = {"mode": "coordinator", "reviewer": "worker-P1", "actor_ref": "synthetic:worker-P1"}
        self.fixture.write_evidence(lane, review_overrides=overrides)
        result, _ = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertFalse(result.ok)
        self.assertIn("review.mode", diagnostic_codes(result))
        path = self.fixture.root / "plan.md"
        path.write_text(path.read_text(encoding="utf-8").replace("| substantive |", "| mechanical |"), encoding="utf-8")
        self.fixture.write_evidence(lane, review_overrides=overrides)
        result, _ = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertTrue(result.ok, [item.as_dict() for item in result.diagnostics])

    def test_close_rejects_failed_review_and_out_of_scope_report(self) -> None:
        for lane in self.fixture.coordination["lanes"]:
            self.fixture.write_evidence(lane)
        self.fixture.write_evidence(self.fixture.coordination["lanes"][0], stage="FAIL")
        result, _ = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertFalse(result.ok)
        self.assertIn("close.incomplete", diagnostic_codes(result))
        self.fixture.write_evidence(self.fixture.coordination["lanes"][0], out_of_scope=True)
        result, _ = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertFalse(result.ok)
        self.assertIn("scope.outside", diagnostic_codes(result))

    def test_evidence_types_and_product_change_fail_closed(self) -> None:
        cases = (
            ({"schema_version": True}, {}, "evidence.identity"),
            ({"checks": ["test: PASS"]}, {}, "report.checks"),
            ({"checks": [{"name": "", "status": "PASS"}]}, {}, "report.checks"),
            ({"checks": [{"name": "test"}]}, {}, "report.checks"),
            ({"checks": [{"name": "test", "status": "FAIL"}]}, {}, "report.checks"),
            ({"limitations": [True]}, {}, "report.limitations"),
            ({}, {"checks": ["inspection: PASS"]}, "review.checks"),
            ({}, {"checks": [{"name": "", "status": "PASS"}]}, "review.checks"),
            ({}, {"checks": [{"name": "inspection"}]}, "review.checks"),
            ({}, {"checks": [{"name": "inspection", "status": "FAIL"}]}, "review.checks"),
            ({}, {"limitations": [True]}, "review.limitations"),
        )
        for report_overrides, review_overrides, expected in cases:
            with self.subTest(expected=expected, report=report_overrides, review=review_overrides):
                for lane in self.fixture.coordination["lanes"]:
                    self.fixture.write_evidence(lane)
                self.fixture.write_evidence(
                    self.fixture.coordination["lanes"][0],
                    report_overrides=report_overrides,
                    review_overrides=review_overrides,
                )
                result, _ = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
                self.assertFalse(result.ok)
                self.assertIn(expected, diagnostic_codes(result))

        lane = self.fixture.coordination["lanes"][0]
        for item in self.fixture.coordination["lanes"]:
            self.fixture.write_evidence(item)
        self.fixture.write_evidence(lane, report_overrides={"changed_paths": [lane["report"]]})
        result, _ = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertFalse(result.ok)
        self.assertIn("report.product_change", diagnostic_codes(result))

        self.fixture.write_evidence(lane, report_overrides={"changed_paths": ["src/core/file.py"]})
        result, _ = swarm.verify_close(self.fixture.root, self.fixture.coordination_path)
        self.assertFalse(result.ok)
        self.assertIn("report.own_report", diagnostic_codes(result))

    def test_cli_validate_and_scope_exit_codes(self) -> None:
        cli = REPO_ROOT / "bin/li-swarm.py"
        valid = subprocess.run(
            [sys.executable, str(cli), "validate", "--repo", str(self.fixture.root), "--coord", self.fixture.coordination_path],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(valid.returncode, 0, valid.stderr + valid.stdout)
        self.assertTrue(json.loads(valid.stdout)["ok"])
        invalid = subprocess.run(
            [sys.executable, str(cli), "check-scope", "--repo", str(self.fixture.root), "--coord", self.fixture.coordination_path, "--task", "BC1", "--changed", "outside/file.py"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(invalid.returncode, 1)
        self.assertFalse(json.loads(invalid.stdout)["ok"])

        paths_file = self.fixture.root / "changed-paths.txt"
        paths_file.write_text(" src/core/file.py \n", encoding="utf-8")
        whitespace = subprocess.run(
            [sys.executable, str(cli), "check-scope", "--repo", str(self.fixture.root), "--coord", self.fixture.coordination_path, "--task", "BC1", "--paths-file", str(paths_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(whitespace.returncode, 1)
        whitespace_result = json.loads(whitespace.stdout)
        self.assertFalse(whitespace_result["ok"])
        self.assertIn("path.unsafe", {item["code"] for item in whitespace_result["diagnostics"]})


if __name__ == "__main__":
    unittest.main(verbosity=2)
