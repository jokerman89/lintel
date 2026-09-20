#!/usr/bin/env python3
# component: swarm-workflow-integration-test
# implements: ADR-0026, ADR-0027
# intent: .claude/plans/swarming-work/spec.md
# constraints: hermetic fixture; no network, agent spawn, or artifact execution
# last_intent_review: 2026-09-20
"""Exercise work map -> safe wave -> evidence -> close across the shared contract."""

from __future__ import annotations

import importlib.util
import json
import os
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


def evidence(
    root: Path, lane: dict[str, object], initiative: str,
    *, base: str | None = None, head: str | None = None, with_review: bool = True,
) -> None:
    task_id = str(lane["task_id"])
    report_path = str(lane["report"])
    review_path = str(lane["review"])
    product_path = f"src/{task_id.lower()}/change.txt"
    if head is None:
        write(root, product_path, f"change for {task_id}\n")
    coordination_path = f".claude/plans/{initiative}/swarm/coordination.json"
    snapshot = swarm.snapshot_lane(root, coordination_path, task_id, "attempt-1", base=base, head=head)
    product_paths = snapshot["result"].get("changes", [product_path])
    report = {
        "schema_version": swarm.EVIDENCE_VERSION,
        "artifact_kind": "swarm-report",
        "initiative": initiative,
        "task_id": task_id,
        "status": "complete",
        "worker": f"worker-{task_id}",
        "actor_ref": f"synthetic:worker-{task_id}",
        "isolation_ref": f"temporary-fixture:{task_id}",
        **snapshot,
        "leaf_results": {leaf: [{"name": f"acceptance-{leaf}", "status": "PASS"}] for leaf in snapshot["leaf_ids"]},
        "changed_paths": [*product_paths, report_path],
        "checks": [{"name": f"focused-{task_id}", "status": "PASS"}],
        "limitations": [],
    }
    review = {
        "schema_version": swarm.EVIDENCE_VERSION,
        "artifact_kind": "swarm-review",
        "initiative": initiative,
        "task_id": task_id,
        "status": "complete",
        "reviewer": f"reviewer-{task_id}",
        "actor_ref": f"synthetic:reviewer-{task_id}",
        "mode": "independent",
        "changed_paths": [review_path],
        "verdict": "PASS",
        "stages": {"spec": "PASS", "quality": "PASS"},
        "checks": [{"name": f"review-{task_id}", "status": "PASS"}],
        "limitations": [],
    }
    write(root, report_path, f"# Report\n\n{swarm.EVIDENCE_START}\n{json.dumps(report)}\n{swarm.EVIDENCE_END}\n")
    review["binding"] = swarm.review_binding(root, lane, report)
    if with_review:
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


def git(repo: Path, *args: str, expected: int = 0) -> str:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(
        ["git", "-C", str(repo), "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", *args],
        env=env, capture_output=True, text=True, check=False,
    )
    if result.returncode != expected:
        raise AssertionError(f"fixture Git {args[0]} failed: {result.stderr}")
    return result.stdout.strip()


def git_worktree_scenario() -> None:
    with tempfile.TemporaryDirectory(prefix="lintel-swarm-git-") as temporary:
        parent = Path(temporary)
        repo = parent / "integration"
        repo.mkdir()
        git(repo, "init", "-q", "-b", "integration")
        git(repo, "config", "user.name", "Synthetic fixture")
        git(repo, "config", "user.email", "fixture@example.invalid")
        hooks = parent / "empty-hooks"
        hooks.mkdir()
        git(repo, "config", "core.hooksPath", str(hooks))
        initiative = "git-fan-in"
        plan = f".claude/plans/{initiative}"
        coord = f"{plan}/swarm/coordination.json"
        mapping = f"{plan}/work.json"
        lanes = []
        for task_id in ("BC1", "BC2"):
            lane = {
                "task_id": task_id, "wave": 1, "role": "FixtureBuilder", "isolation": "git-worktree",
                "write_scope": [f"src/{task_id.lower()}"],
                "brief": f"{plan}/swarm/briefs/{task_id}.md",
                "report": f"{plan}/swarm/reports/{task_id}.md",
                "review": f"{plan}/swarm/reviews/{task_id}.md",
            }
            lanes.append(lane)
            write(repo, lane["brief"], f"# Brief {task_id}\n\n## Task\nImplement {task_id}.\n\n## Ownership\n"
                  f"Write only src/{task_id.lower()}.\n\n## Acceptance\n- The focused fixture passes.\n")
        for name, text in (
            ("spec.md", "# Spec\nPreserve both isolated results.\n"),
            ("plan.md", "# Plan\n### BC1 Core\n### BC2 Adapter\n"),
            ("prompt.md", "# Cold handoff\n"),
            ("swarm/charter.md", "# Charter\nCoordinator integrates; no automatic agents.\n"),
        ):
            write(repo, f"{plan}/{name}", text)
        write(repo, mapping, json.dumps({
            "schema_version": 1, "workflow": "lintel", "status": "APPROVED",
            "spec": f"{plan}/spec.md", "plan": f"{plan}/plan.md", "tasks": f"{plan}/plan.md",
            "prompt": f"{plan}/prompt.md", "execution_mode": "swarm", "coordination": coord,
        }))
        write(repo, coord, json.dumps({
            "schema_version": 1, "initiative": initiative, "work_map": mapping,
            "charter": f"{plan}/swarm/charter.md", "integration_branch": "integration", "max_parallel": 2,
            "coordinator_paths": ["generated"], "scope_rules": dict(swarm.EXPECTED_SCOPE_RULES), "lanes": lanes,
        }))
        write(repo, ".gitignore", "__pycache__/\n")
        git(repo, "add", "--", ".claude", ".gitignore")
        git(repo, "commit", "-qm", "test: seed synthetic swarm")
        base = git(repo, "rev-parse", "HEAD")
        for capability, expected in (("native", 2), ("sequenced", 1), ("none", 1)):
            result, frontier = swarm.ready_frontier(repo, coord, host_capability=capability)
            assert result.ok and len(frontier["dispatch_task_ids"]) == expected
        worker_heads = []
        for lane in lanes:
            task_id = lane["task_id"]
            worker = parent / task_id
            git(repo, "worktree", "add", "-q", "-b", f"lane-{task_id}", str(worker), base)
            assert git(worker, "rev-parse", "--show-toplevel") != git(repo, "rev-parse", "--show-toplevel")
            product_path = f"src/{task_id.lower()}/change.txt"
            write(worker, product_path, f"isolated {task_id}\n")
            write(worker, f"src/{task_id.lower()}/__pycache__/ignored.pyc", "ignored generated fixture\n")
            git(worker, "add", "--", product_path)
            git(worker, "commit", "-qm", f"test: isolated result {task_id}")
            product_head = git(worker, "rev-parse", "HEAD")
            evidence(worker, lane, initiative, base=base, head=product_head, with_review=False)
            resumed = run_cli(worker, "resume", coord)
            current = next(state for state in resumed["frontier"]["states"] if state["task_id"] == task_id)
            assert current["state"] == "awaiting_review", "runtime loss must not fabricate a reviewer"
            closed, _ = swarm.verify_close(worker, coord)
            assert not closed.ok
            git(worker, "add", "--", lane["report"])
            git(worker, "commit", "-qm", f"test: preserved report {task_id}")
            review_base = git(worker, "rev-parse", "HEAD")
            evidence(worker, lane, initiative, base=base, head=product_head)
            git(worker, "add", "--", lane["review"])
            git(worker, "commit", "-qm", f"test: synthetic review record {task_id}")
            review_head = git(worker, "rev-parse", "HEAD")
            scope = subprocess.run(
                [sys.executable, str(ROOT / "bin/li-swarm.py"), "check-scope", "--repo", str(worker),
                 "--coord", coord, "--task", task_id, "--actor", "reviewer",
                 "--base", review_base, "--head", review_head],
                capture_output=True, text=True, check=False,
            )
            assert scope.returncode == 0, scope.stdout + scope.stderr
            worker_heads.append(review_head)

        breach = parent / "breach"
        git(repo, "worktree", "add", "-q", "-b", "scope-breach", str(breach), base)
        write(breach, "src/bc2/outside.txt", "not BC1-owned\n")
        git(breach, "add", "--", "src/bc2/outside.txt")
        git(breach, "commit", "-qm", "test: deliberate scope breach")
        rejected = subprocess.run(
            [sys.executable, str(ROOT / "bin/li-swarm.py"), "check-scope", "--repo", str(breach),
             "--coord", coord, "--task", "BC1", "--base", base, "--head", git(breach, "rev-parse", "HEAD")],
            capture_output=True, text=True, check=False,
        )
        assert rejected.returncode == 1
        reviewer_rejected = subprocess.run(
            [sys.executable, str(ROOT / "bin/li-swarm.py"), "check-scope", "--repo", str(breach),
             "--coord", coord, "--task", "BC1", "--actor", "reviewer",
             "--base", base, "--head", git(breach, "rev-parse", "HEAD")],
            capture_output=True, text=True, check=False,
        )
        assert reviewer_rejected.returncode == 1
        assert (breach / "src/bc2/outside.txt").read_text(encoding="utf-8") == "not BC1-owned\n"
        for head in worker_heads:
            git(repo, "merge", "--no-ff", "-qm", "test: deterministic isolated fan-in", head)
            git(repo, "merge-base", "--is-ancestor", head, "HEAD")
        closed = run_cli(repo, "verify", coord)
        assert all(state["state"] == "complete" for state in closed["lanes"])
        assert (repo / "src/bc1/change.txt").is_file() and (repo / "src/bc2/change.txt").is_file()
        write(repo, "src/bc1/unreviewed.txt", "new unreviewed scoped file\n")
        invalidated, _ = swarm.verify_close(repo, coord)
        assert not invalidated.ok, "an untracked scoped addition must invalidate the bound result"
        (repo / "src/bc1/unreviewed.txt").unlink()
        assert swarm.verify_close(repo, coord)[0].ok
        conflict = parent / "conflict"
        git(repo, "worktree", "add", "-q", "-b", "conflicting-result", str(conflict), "HEAD")
        write(conflict, "src/bc1/change.txt", "isolated conflicting revision\n")
        git(conflict, "add", "--", "src/bc1/change.txt")
        git(conflict, "commit", "-qm", "test: preserve conflicting source")
        write(repo, "src/bc1/change.txt", "coordinator conflicting revision\n")
        git(repo, "add", "--", "src/bc1/change.txt")
        git(repo, "commit", "-qm", "test: independent coordinator revision")
        git(repo, "merge", "--no-ff", "--no-commit", "conflicting-result", expected=1)
        assert git(repo, "diff", "--name-only", "--diff-filter=U") == "src/bc1/change.txt"
        assert not swarm.verify_close(repo, coord)[0].ok
        assert (conflict / "src/bc1/change.txt").read_text(encoding="utf-8") == "isolated conflicting revision\n"
        for lane, head in zip(lanes, worker_heads):
            assert git(parent / lane["task_id"], "rev-parse", "HEAD") == head
    print("PASS: real isolated Git worktrees, actor scope, interrupted review, serial/manual fallback, merge conflicts and ancestry-preserving fan-in")


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
    git_worktree_scenario()


if __name__ == "__main__":
    main()
