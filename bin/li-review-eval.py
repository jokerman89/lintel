#!/usr/bin/env python3
# component: review-eval-cli
# implements: ADR-0021, ADR-0028, ADR-0040
# intent: .claude/plans/adaptive-review/spec.md
# constraints: stdlib only; reads only the named JSON files and prints JSON; never executes targets, models, network, subprocesses or submissions
# last_intent_review: 2026-09-28
"""Offline review/benchmark scorer for imported observations.

Exit 0 = report printed; 2 = invalid input; 3 = comparison refused (unmatched provenance).
Every report carries release_clearance: false and leaderboard_eligible: false.
"""
import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import review_evaluation as ev  # noqa: E402


def emit(value, code=0):
    print(json.dumps(value, indent=2, sort_keys=False))
    return code


def _load(path, role, inputs):
    doc, digest = ev.load_json(Path(path))
    inputs[role] = digest
    return doc


def _review(inventory_path, run_path):
    inputs = {}
    inventory = _load(inventory_path, "inventory", inputs)
    run = _load(run_path, "run", inputs)
    return ev.evaluate_review(inventory, run, inputs)


def _benchmark(plan_path, receipts_path):
    inputs = {}
    plan = _load(plan_path, "plan", inputs)
    receipts = _load(receipts_path, "receipts", inputs)
    return ev.evaluate_benchmark(plan, receipts, inputs)


def _pair(args, shared, base, cand, parser):
    shared_value = getattr(args, shared)
    base_value, cand_value = getattr(args, base), getattr(args, cand)
    if shared_value and (base_value or cand_value):
        parser.error(f"use --{shared} or --{base.replace('_', '-')}/--{cand.replace('_', '-')}, not both")
    if shared_value:
        return shared_value, shared_value
    if not (base_value and cand_value):
        parser.error(f"--{shared} or both --{base.replace('_', '-')} and --{cand.replace('_', '-')} are required")
    return base_value, cand_value


def main(argv=None):
    parser = argparse.ArgumentParser(prog="li-review-eval", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    hashing = sub.add_parser("hash", help="print canonical hashes a run or receipt file must bind")
    target = hashing.add_mutually_exclusive_group(required=True)
    target.add_argument("--inventory")
    target.add_argument("--plan")

    review = sub.add_parser("review", help="score imported review observations against a fixed inventory")
    review.add_argument("--inventory", required=True)
    review.add_argument("--run", required=True)

    bench = sub.add_parser("benchmark", help="aggregate imported CyberGym verification receipts")
    bench.add_argument("--plan", required=True)
    bench.add_argument("--receipts", required=True)

    cmp_review = sub.add_parser("compare-review", help="matched comparison of two review runs")
    cmp_review.add_argument("--inventory")
    cmp_review.add_argument("--baseline-inventory")
    cmp_review.add_argument("--candidate-inventory")
    cmp_review.add_argument("--baseline", required=True)
    cmp_review.add_argument("--candidate", required=True)

    cmp_bench = sub.add_parser("compare-benchmark", help="matched comparison of two receipt sets")
    cmp_bench.add_argument("--plan")
    cmp_bench.add_argument("--baseline-plan")
    cmp_bench.add_argument("--candidate-plan")
    cmp_bench.add_argument("--baseline", required=True)
    cmp_bench.add_argument("--candidate", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            path = args.inventory or args.plan
            doc, digest = ev.load_json(Path(path))
            result = ev.describe_hashes(doc, "inventory" if args.inventory else "plan")
            result["input_sha256"] = digest
            return emit(result)
        if args.command == "review":
            return emit(_review(args.inventory, args.run))
        if args.command == "benchmark":
            return emit(_benchmark(args.plan, args.receipts))
        if args.command == "compare-review":
            base_inv, cand_inv = _pair(args, "inventory", "baseline_inventory", "candidate_inventory", cmp_review)
            result = ev.compare_review(_review(base_inv, args.baseline), _review(cand_inv, args.candidate))
        else:
            base_plan, cand_plan = _pair(args, "plan", "baseline_plan", "candidate_plan", cmp_bench)
            result = ev.compare_benchmark(_benchmark(base_plan, args.baseline), _benchmark(cand_plan, args.candidate))
        return emit(result, 3 if result["status"] == "refused" else 0)
    except ev.EvaluationError as exc:
        return emit({"status": "invalid", "errors": exc.errors,
                     "release_clearance": False, "leaderboard_eligible": False}, 2)


if __name__ == "__main__":
    sys.exit(main())
