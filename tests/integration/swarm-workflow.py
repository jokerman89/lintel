#!/usr/bin/env python3
# component: swarm-workflow-integration-test
# implements: ADR-0026
# intent: .claude/plans/swarming-work/spec.md
# constraints: hermetic fixture; no network, agent spawn, or artifact execution
# last_intent_review: 2026-09-08
"""Exercise work map -> safe wave -> evidence -> close across the shared contract."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))

import swarm_contract as swarm  # noqa: E402


def load_work_artifacts_module():
    spec = importlib.util.spec_from_file_location("li_work_artifacts", ROOT / "bin/li-work-artifacts.py")
    if spec is None or spec.loader is None:
        raise AssertionError("cannot import li-work-artifacts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(root: Path, relative: str, content: str) -> None:
    target = root.joinpath(*Path(relative).parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def evidence(root: Path, lane: dict[str, object], initiative: str) -> None:
    task_id = str(lane["task_id"])
    report_path = str(lane["report"])
    review_path = str(lane["review"])
    product_path = f"src/{task_id.lower()}/change.txt"
    report = {
        "schema_version": 1,
        "artifact_kind": "swarm-report",
        "initiative": initiative,
        "task_id": task_id,
        "status": "complete",
        "worker": f"worker-{task_id}",
        "changed_paths": [product_path, report_path],
        "checks": [{"name": f"focused-{task_id}", "status": "PASS"}],
        "limitations": [],
    }
    review = {
        "schema_version": 1,
        "artifact_kind": "swarm-review",
        "initiative": initiative,
        "task_id": task_id,
        "status": "complete",
        "reviewer": f"reviewer-{task_id}",
        "verdict": "PASS",
        "stages": {"spec": "PASS", "quality": "PASS"},
        "checks": [{"name": f"review-{task_id}", "status": "PASS"}],
        "limitations": [],
    }
    write(root, product_path, f"change for {task_id}\n")
    write(root, report_path, f"# Report\n\n{swarm.EVIDENCE_START}\n{json.dumps(report)}\n{swarm.EVIDENCE_END}\n")
    write(root, review_path, f"# Review\n\n{swarm.EVIDENCE_START}\n{json.dumps(review)}\n{swarm.EVIDENCE_END}\n")


def run_cli(repo: Path, command: str, coordination_path: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "bin/li-swarm.py"), command, "--repo", str(repo), "--coord", coordination_path],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"{command} failed ({result.returncode}): {result.stderr}{result.stdout}")
    return json.loads(result.stdout)


def main() -> None:
    work_artifacts = load_work_artifacts_module()
    with tempfile.TemporaryDirectory(prefix="lintel-swarm-workflow-") as temporary:
        repo = Path(temporary).resolve()
        initiative = "integration-example"
        plan_dir = ".claude/plans/integration-example"
        work_map_path = f"{plan_dir}/work.json"
        coordination_path = f"{plan_dir}/swarm/coordination.json"
        tasks = "# Plan\n\n### BC1 — Core\n\n### BC2 — Docs\n\n### BC3 — Adapter\n"
        for name, body in (
            ("spec.md", "# Specification\n"),
            ("plan.md", tasks),
            ("prompt.md", "# Handoff\n"),
            ("swarm/charter.md", "# Charter\n"),
        ):
            write(repo, f"{plan_dir}/{name}", body)

        lanes = [
            {
                "task_id": "BC1",
                "wave": 1,
                "role": "CoreBuilder",
                "write_scope": ["src/bc1"],
                "brief": f"{plan_dir}/swarm/briefs/BC1.md",
                "report": f"{plan_dir}/swarm/reports/BC1.md",
                "review": f"{plan_dir}/swarm/reviews/BC1.md",
            },
            {
                "task_id": "BC2",
                "wave": 2,
                "role": "DocWriter",
                "isolation": "git-worktree",
                "write_scope": ["src/bc2"],
                "brief": f"{plan_dir}/swarm/briefs/BC2.md",
                "report": f"{plan_dir}/swarm/reports/BC2.md",
                "review": f"{plan_dir}/swarm/reviews/BC2.md",
            },
            {
                "task_id": "BC3",
                "wave": 2,
                "role": "AdapterBuilder",
                "isolation": "isolated-patch",
                "write_scope": ["src/bc3"],
                "brief": f"{plan_dir}/swarm/briefs/BC3.md",
                "report": f"{plan_dir}/swarm/reports/BC3.md",
                "review": f"{plan_dir}/swarm/reviews/BC3.md",
            },
        ]
        for lane in lanes:
            write(repo, str(lane["brief"]), f"# Brief: {lane['task_id']}\n")

        work_map = {
            "schema_version": 1,
            "workflow": "lintel",
            "status": "APPROVED",
            "spec": f"{plan_dir}/spec.md",
            "plan": f"{plan_dir}/plan.md",
            "tasks": f"{plan_dir}/plan.md",
            "prompt": f"{plan_dir}/prompt.md",
            "execution_mode": "swarm",
            "coordination": coordination_path,
        }
        coordination = {
            "schema_version": 1,
            "initiative": initiative,
            "work_map": work_map_path,
            "charter": f"{plan_dir}/swarm/charter.md",
            "integration_branch": "codex/integration-example",
            "max_parallel": 2,
            "scope_rules": dict(swarm.EXPECTED_SCOPE_RULES),
            "lanes": lanes,
        }
        write(repo, work_map_path, json.dumps(work_map, indent=2) + "\n")
        write(repo, coordination_path, json.dumps(coordination, indent=2) + "\n")

        loaded = work_artifacts.load_work_map(repo, Path(work_map_path))
        assert loaded["execution_mode"] == "swarm"
        first = run_cli(repo, "wave", coordination_path)
        assert first["frontier"]["dispatch_task_ids"] == ["BC1"]

        allowed = swarm.check_lane_scope(repo, coordination_path, "BC1", ["src/bc1/change.txt", str(lanes[0]["report"])])
        assert allowed.ok, [item.as_dict() for item in allowed.diagnostics]
        blocked = swarm.check_lane_scope(repo, coordination_path, "BC1", ["src/bc2/change.txt"])
        assert not blocked.ok and any(item.code == "scope.outside" for item in blocked.diagnostics)

        evidence(repo, lanes[0], initiative)
        second = run_cli(repo, "wave", coordination_path)
        assert second["frontier"]["dispatch_task_ids"] == ["BC2", "BC3"]
        evidence(repo, lanes[1], initiative)
        evidence(repo, lanes[2], initiative)
        closed = run_cli(repo, "verify", coordination_path)
        assert closed["ok"] is True
        assert all(lane["state"] == "complete" for lane in closed["lanes"])

        legacy = dict(work_map)
        legacy.pop("execution_mode")
        legacy.pop("coordination")
        write(repo, work_map_path, json.dumps(legacy, indent=2) + "\n")
        assert work_artifacts.load_work_map(repo, Path(work_map_path))["workflow"] == "lintel"

    print("PASS: mapped swarm advances candidate waves, checks scope/evidence, closes, and preserves legacy maps")


if __name__ == "__main__":
    main()
