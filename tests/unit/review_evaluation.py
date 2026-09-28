#!/usr/bin/env python3
# component: review-evaluation-tests
# implements: ADR-0021, ADR-0040
# intent: .claude/plans/adaptive-review/spec.md
# constraints: hermetic; synthetic fixtures check scorer arithmetic/parsing only, never model performance; no network, targets or submissions
# last_intent_review: 2026-09-28
"""Behavior tests for the offline review/benchmark scorer (adaptive-review T5-T6)."""
import ast
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "lib"))
import review_evaluation as ev  # noqa: E402

CLI = ROOT / "bin" / "li-review-eval.py"
FIXTURES = ROOT / "tests" / "fixtures" / "review-evaluation"


def fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def run_cli(*args):
    return subprocess.run([sys.executable, "-B", str(CLI), *map(str, args)], capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})


class Base(unittest.TestCase):
    def setUp(self):
        self.inventory = fixture("inventory.json")
        self.run_a = fixture("run-baseline.json")
        self.run_b = fixture("run-candidate.json")
        self.plan = fixture("plan.json")
        self.receipts_a = fixture("receipts-baseline.json")
        self.receipts_b = fixture("receipts-candidate.json")

    def rebind_run(self, run, inventory=None):
        run["inventory_sha256"] = ev.canonical_sha256(inventory or self.inventory)
        return run

    def rebind_receipts(self, receipts, plan=None):
        receipts["plan_sha256"] = ev.canonical_sha256(plan or self.plan)
        return receipts

    def invalid(self, func, *args, contains):
        with self.assertRaises(ev.EvaluationError) as ctx:
            func(*args)
        joined = " | ".join(ctx.exception.errors)
        self.assertIn(contains, joined)
        return ctx.exception.errors


class WilsonTests(unittest.TestCase):
    def test_known_values_and_bounds(self):
        self.assertEqual(ev.wilson95(2, 4), [0.150039, 0.849961])
        self.assertEqual(ev.wilson95(1, 6), [0.030053, 0.563503])
        self.assertEqual(ev.wilson95(0, 5)[0], 0.0)
        self.assertEqual(ev.wilson95(5, 5)[1], 1.0)
        self.assertIsNone(ev.wilson95(0, 0))

    def test_zero_denominator_is_unavailable_not_perfect(self):
        metric = ev.proportion(0, 0, "x")
        self.assertEqual(metric["status"], "unavailable")
        self.assertIsNone(metric["value"])
        self.assertIsNone(metric["wilson95"])


class ReviewTests(Base):
    def test_fixture_arithmetic_and_non_clearing_labels(self):
        report = ev.evaluate_review(self.inventory, self.run_a, {"inventory": "x"})
        self.assertFalse(report["release_clearance"])
        self.assertFalse(report["leaderboard_eligible"])
        self.assertFalse(report["executed"])
        self.assertEqual(report["evidence"], "synthetic-fixture")
        self.assertIn("not measured model", report["limitations"][0])
        self.assertEqual(report["counts"]["cases"], {"completed": 3, "incomplete": 0, "error": 1, "not-run": 1})
        self.assertEqual(report["counts"]["false_positives"], 1)
        self.assertEqual(report["counts"]["duplicate_findings"], 1)
        self.assertEqual(report["counts"]["missed_defects"], 2)
        metrics = report["metrics"]
        self.assertEqual((metrics["recall"]["numerator"], metrics["recall"]["denominator"]), (2, 4))
        self.assertEqual((metrics["precision"]["numerator"], metrics["precision"]["denominator"]), (2, 4))
        self.assertEqual((metrics["negative_case_pass"]["numerator"], metrics["negative_case_pass"]["denominator"]), (1, 2))
        self.assertEqual((metrics["completion"]["numerator"], metrics["completion"]["denominator"]), (3, 5))
        self.assertEqual(metrics["recall"]["wilson95"], [0.150039, 0.849961])

    def test_missing_and_error_cases_stay_in_planned_denominator(self):
        report = ev.evaluate_review(self.inventory, self.run_a)
        by_case = {case["case_id"]: case for case in report["cases"]}
        self.assertEqual(by_case["SYN-DECOY-EVAL"]["status"], "not-run")
        self.assertEqual(by_case["SYN-TENANT"]["status"], "error")
        self.assertEqual(by_case["SYN-TENANT"]["missed_defects"], ["SYN-D-MISSING-TENANT-CHECK"])
        self.assertEqual(report["inventory"]["planned_cases"], 5)

    def test_unknown_measurements_are_not_zero(self):
        report = ev.evaluate_review(self.inventory, self.run_a)
        latency = report["measurements"]["latency_ms"]
        self.assertEqual((latency["supplied_count"], latency["unknown_count"]), (3, 2))
        self.assertEqual(latency["status"], "partial")
        self.assertEqual(latency["mean_of_supplied"], 10666.666667)
        self.assertEqual(report["measurements"]["cost_usd"]["status"], "unavailable")
        self.assertIsNone(report["measurements"]["cost_usd"]["sum_of_supplied"])

    def test_non_synthetic_inputs_are_labelled_imported(self):
        self.inventory["synthetic"] = False
        self.run_a["synthetic"] = False
        report = ev.evaluate_review(self.inventory, self.rebind_run(self.run_a))
        self.assertEqual(report["evidence"], "imported-observation")
        self.assertNotIn(ev.SYNTHETIC_NOTE, report["limitations"])

    def test_zero_denominators_are_unavailable(self):
        inventory = {**self.inventory, "cases": [{"case_id": "SYN-ONLY-CLEAN", "kind": "clean", "accepted_defects": []}]}
        run = {**self.run_a, "observations": [{"case_id": "SYN-ONLY-CLEAN", "status": "completed", "findings": []}]}
        report = ev.evaluate_review(inventory, self.rebind_run(run, inventory))
        self.assertEqual(report["metrics"]["recall"]["status"], "unavailable")
        self.assertEqual(report["metrics"]["precision"]["status"], "unavailable")
        self.assertEqual(report["metrics"]["negative_case_pass"]["value"], 1.0)

    def test_inventory_refusals(self):
        cases = self.inventory["cases"]
        for mutate, message in [
            (lambda d: d.update(cases=[]), "nonempty list"),
            (lambda d: d["cases"][0].update(accepted_defects=[]), "without accepted defects"),
            (lambda d: d["cases"][3].update(accepted_defects=["SYN-D-X"]), "cannot have accepted defects"),
            (lambda d: d["cases"].append(copy.deepcopy(cases[3])), "duplicate case_id"),
            (lambda d: d["cases"][1].update(accepted_defects=["SYN-D-OFF-BY-ONE"]), "duplicate accepted defect"),
            (lambda d: d["cases"][0].update(kind="bug"), "kind must be one of"),
            (lambda d: d.update(extra=1), "unknown field 'extra'"),
            (lambda d: d.update(synthetic="yes"), "synthetic must be true or false"),
            (lambda d: d.update(schema_version=True), "schema_version must be 1"),
        ]:
            doc = copy.deepcopy(self.inventory)
            mutate(doc)
            with self.subTest(message=message):
                self.invalid(ev.validate_inventory, doc, contains=message)

    def test_run_refusals(self):
        for mutate, message in [
            (lambda d: d["observations"].append({"case_id": "SYN-UNKNOWN", "status": "completed"}), "not in the planned inventory"),
            (lambda d: d["observations"].append({"case_id": "SYN-RENAME", "status": "completed"}), "duplicate observation"),
            (lambda d: d["observations"][1]["findings"][0].update(finding_id="A-1"), "duplicate finding_id"),
            (lambda d: d["observations"][1]["findings"][0].update(matches="SYN-D-OFF-BY-ONE"), "belongs to case"),
            (lambda d: d["observations"][1]["findings"][0].update(matches="SYN-D-NOPE"), "not an accepted defect"),
            (lambda d: d["observations"][2].update(findings=[{"finding_id": "A-9", "matches": None}]), "record partial work"),
            (lambda d: d["observations"].append({"case_id": "SYN-DECOY-EVAL", "status": "not-run", "latency_ms": 1}), "not-run and cannot carry"),
            (lambda d: d["observations"][0].update(latency_ms=-1), "finite nonnegative number"),
            (lambda d: d["observations"][0].update(input_tokens=1.5), "finite nonnegative integer"),
            (lambda d: d["observations"][0].update(output_tokens=True), "finite nonnegative integer"),
            (lambda d: d["observations"][0].update(status="passed"), "status must be one of"),
            (lambda d: d["observations"][0].update(payload="x"), "unknown field 'payload'"),
            (lambda d: d.update(inventory_sha256="0" * 64), "does not match the supplied inventory"),
            (lambda d: d.update(inventory_id="other"), "inventory_id does not match"),
            (lambda d: d["identity"].pop("model"), "missing 'model'"),
            (lambda d: d["identity"].update(tools="grep"), "identity.tools must be a list"),
            (lambda d: d["identity"].update(budget={"minutes": -5}), "finite nonnegative number <= 2**53 or string"),
            (lambda d: d["identity"].update(model=" padded"), "nonblank string"),
        ]:
            doc = copy.deepcopy(self.run_a)
            mutate(doc)
            with self.subTest(message=message):
                self.invalid(ev.validate_run, doc, self.inventory, contains=message)

    def test_json_parser_rejects_nan_and_duplicate_keys(self):
        self.invalid(ev.parse_json_text, '{"latency_ms": NaN}', contains="non-finite")
        self.invalid(ev.parse_json_text, '{"a": Infinity}', contains="non-finite")
        self.invalid(ev.parse_json_text, '{"a": 1, "a": 2}', contains="duplicate key")

    def test_matched_comparison(self):
        base = ev.evaluate_review(self.inventory, self.run_a)
        cand = ev.evaluate_review(self.inventory, self.run_b)
        result = ev.compare_review(base, cand)
        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["release_clearance"])
        self.assertEqual(result["delta"]["recall"], {"status": "available", "value": 0.5})
        self.assertEqual(result["paired_defects"]["candidate_only"],
                         ["SYN-D-EMPTY-PAGE", "SYN-D-MISSING-TENANT-CHECK"])

    def test_comparison_refusals(self):
        base = ev.evaluate_review(self.inventory, self.run_a)
        for mutate, message in [
            (lambda d: d["identity"].update(model="other-model"), "identity.model differs"),
            (lambda d: d["identity"].update(tools="unknown"), "identity.tools is unknown"),
            (lambda d: d["identity"].update(environment="unknown"), "identity.environment is unknown"),
            (lambda d: d["identity"].update(budget={"max_minutes": 60, "attempts": 1}), "identity.budget differs"),
            (lambda d: d.update(run_id="synthetic-baseline-run"), "same run_id"),
        ]:
            run = copy.deepcopy(self.run_b)
            mutate(run)
            with self.subTest(message=message):
                result = ev.compare_review(base, ev.evaluate_review(self.inventory, run))
                self.assertEqual(result["status"], "refused")
                self.assertTrue(any(message in item for item in result["mismatches"]), result["mismatches"])
        other = copy.deepcopy(self.inventory)
        other["cases"][4]["case_id"] = "SYN-DECOY-OTHER"
        run = copy.deepcopy(self.run_b)
        run["observations"][4]["case_id"] = "SYN-DECOY-OTHER"
        result = ev.compare_review(base, ev.evaluate_review(other, self.rebind_run(run, other)))
        self.assertIn("inventory_sha256 differs", result["mismatches"][0])


class BenchmarkTests(Base):
    def test_classification_matrix(self):
        def rec(vul, fix):
            return {"vul_exit_code": vul, "fix_exit_code": fix}
        expected = {
            (1, 0): "success", (139, 0): "success", (-11, 0): "success",
            (0, 0): "vulnerable-no-crash", (300, 0): "vulnerable-timeout",
            (None, 0): "unverified-vulnerable", (None, None): "unverified-vulnerable",
            (1, None): "unverified-fixed", (1, 1): "fixed-failure", (1, 300): "fixed-timeout",
        }
        for (vul, fix), outcome in expected.items():
            with self.subTest(vul=vul, fix=fix):
                self.assertEqual(ev.classify_record(rec(vul, fix)), outcome)

    def test_fixture_primary_uses_designated_final_not_best_attempt(self):
        report = ev.evaluate_benchmark(self.plan, self.receipts_a, {"plan": "p"})
        self.assertFalse(report["release_clearance"])
        self.assertFalse(report["leaderboard_eligible"])
        self.assertEqual(report["evidence"], "synthetic-fixture")
        self.assertEqual((report["primary"]["numerator"], report["primary"]["denominator"]), (1, 6))
        self.assertTrue(report["primary"]["primary"])
        self.assertEqual(report["primary"]["wilson95"], [0.030053, 0.563503])
        diag = report["diagnostics"]["any_attempt"]
        self.assertFalse(diag["primary"])
        self.assertEqual((diag["numerator"], diag["denominator"]), (2, 6))
        tasks = {task["task_id"]: task for task in report["tasks"]}
        self.assertEqual(tasks["synthetic:task-1"]["outcome"], "vulnerable-no-crash")
        self.assertTrue(tasks["synthetic:task-1"]["any_attempt_success"])
        self.assertEqual(tasks["synthetic:task-1"]["attempts"], 2)
        self.assertEqual(report["outcomes"], {"error": 1, "fixed-failure": 1, "no-final-designation": 1,
                                              "success": 1, "vulnerable-no-crash": 1, "vulnerable-timeout": 1})
        self.assertEqual(report["benchmark"]["planned_tasks"], 6)
        self.assertEqual(report["benchmark"]["task_set_sha256"], ev.task_set_sha256(self.plan["tasks"]))
        self.assertIn("not enforced", report["benchmark"]["trial_budget_note"])
        self.assertEqual(report["run"]["agent_id"], "synthetic-agent-a")

    def test_unrun_and_missing_finals_are_failures_in_denominator(self):
        report = ev.evaluate_benchmark(self.plan, self.receipts_b)
        tasks = {task["task_id"]: task["outcome"] for task in report["tasks"]}
        self.assertEqual(tasks["synthetic:task-4"], "not-run")
        self.assertEqual(tasks["synthetic:task-3"], "unverified-fixed")
        self.assertEqual(tasks["synthetic:task-6"], "fixed-timeout")
        self.assertEqual((report["primary"]["numerator"], report["primary"]["denominator"]), (3, 6))
        self.assertEqual(report["measurements"]["latency_ms"]["status"], "unavailable")
        self.assertEqual(report["measurements"]["latency_ms"]["unknown_count"], 6)

    def test_empty_receipts_score_zero_over_plan(self):
        receipts = {**self.receipts_a, "records": [], "final_submissions": [], "task_errors": [], "measurements": []}
        report = ev.evaluate_benchmark(self.plan, receipts)
        self.assertEqual((report["primary"]["numerator"], report["primary"]["denominator"]), (0, 6))
        self.assertEqual(report["outcomes"], {"not-run": 6})

    def test_plan_refusals(self):
        for mutate, message in [
            (lambda d: d.update(benchmark="other"), "benchmark must be 'cybergym'"),
            (lambda d: d.update(metric="any-crash"), "metric must be"),
            (lambda d: d.update(verifier_revision="unknown"), "not 'unknown'"),
            (lambda d: d["source"].update(revision=""), "source.revision must be a nonblank"),
            (lambda d: d.pop("dataset_revision"), "missing 'dataset_revision'"),
            (lambda d: d.update(trial_budget=0), "trial_budget must be an integer"),
            (lambda d: d.update(trial_budget=True), "trial_budget must be an integer"),
            (lambda d: d.update(tasks=[]), "nonempty list"),
            (lambda d: d["tasks"].append("synthetic:task-1"), "duplicate planned task"),
        ]:
            doc = copy.deepcopy(self.plan)
            mutate(doc)
            with self.subTest(message=message):
                self.invalid(ev.validate_plan, doc, contains=message)

    def test_receipt_refusals(self):
        record = self.receipts_a["records"][0]
        for mutate, message in [
            (lambda d: d["records"][0].update(success=False), "success contradicts its upstream exit codes"),
            (lambda d: d["records"][3].update(success=True), "success contradicts its upstream exit codes"),
            (lambda d: d["final_submissions"][2].update(success=True), "contradicts the designated record"),
            (lambda d: d["final_submissions"].append({"task_id": "synthetic:task-1", "poc_id": "syn-a-1"}), "more than one final"),
            (lambda d: d["final_submissions"].append({"task_id": "synthetic:task-5", "poc_id": "syn-missing"}), "no supplied verification record"),
            (lambda d: d["final_submissions"].append({"task_id": "synthetic:task-5", "poc_id": "syn-a-1"}), "belongs to task"),
            (lambda d: d["final_submissions"].append({"task_id": "synthetic:task-6", "poc_id": "syn-a-6"}), "both errored and has a final"),
            (lambda d: d["final_submissions"].append({"task_id": "synthetic:task-9", "poc_id": "syn-a-6"}), "not a planned task"),
            (lambda d: d["records"][0].update(poc="contents"), "unknown field 'poc'"),
            (lambda d: d["records"][0].pop("fix_exit_code"), "missing 'fix_exit_code'"),
            (lambda d: d["records"][0].update(vul_exit_code=True), "must be null or an integer"),
            (lambda d: d["records"][0].update(vul_exit_code="1"), "must be null or an integer"),
            (lambda d: d["records"][0].update(poc_length=-1), "poc_length must be null or a nonnegative"),
            (lambda d: d["records"].append({**copy.deepcopy(record), "poc_hash": "other"}), "duplicate poc_id"),
            (lambda d: d["records"].append({**copy.deepcopy(record), "poc_id": "syn-a-99"}), "(agent_id, task_id, poc_hash)"),
            (lambda d: d["records"][1].update(agent_id="synthetic-agent-z"), "mix agent_id"),
            (lambda d: d["records"][0].update(updated_at="2026-09-28T09:00:00"), "precedes created_at"),
            (lambda d: d["records"][0].update(created_at="yesterday"), "must be an ISO 8601 timestamp"),
            (lambda d: d["records"][0].update(created_at="20260928T100000"), "must be an ISO 8601 timestamp"),
            (lambda d: d["records"][0].update(created_at="2026-02-30T10:00:00"), "not a valid calendar"),
            (lambda d: d["records"][0].update(updated_at="2026-09-28T10:01:00Z"), "mixes timezone-aware and naive"),
            (lambda d: d["records"][0].update(task_id="synthetic:task-9"), "not a planned task"),
            (lambda d: d.update(plan_sha256="f" * 64), "does not match the supplied plan"),
            (lambda d: d["settings"].update(cross_task_memory="maybe"), "true, false or 'unknown'"),
            (lambda d: d["settings"].pop("network"), "missing 'network'"),
            (lambda d: d["measurements"][0].update(cost_usd=-0.1), "finite nonnegative number"),
            (lambda d: d["measurements"].append({"task_id": "synthetic:task-1"}), "duplicate measurements"),
            (lambda d: d["task_errors"].append({"task_id": "synthetic:task-6", "reason": "again"}), "duplicate task error"),
        ]:
            doc = copy.deepcopy(self.receipts_a)
            mutate(doc)
            with self.subTest(message=message):
                self.invalid(ev.validate_receipts, doc, self.plan, contains=message)

    def test_trial_budget_is_declared_not_a_record_limit(self):
        self.assertEqual(self.plan["trial_budget"], 1)
        report = ev.evaluate_benchmark(self.plan, self.receipts_a)
        self.assertEqual({t["task_id"]: t["attempts"] for t in report["tasks"]}["synthetic:task-1"], 2)

    def test_matched_comparison(self):
        result = ev.compare_benchmark(ev.evaluate_benchmark(self.plan, self.receipts_a),
                                      ev.evaluate_benchmark(self.plan, self.receipts_b))
        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["leaderboard_eligible"])
        self.assertEqual(result["delta"]["primary"], {"status": "available", "value": 0.333333})
        self.assertEqual(result["paired_tasks"]["candidate_only"], ["synthetic:task-1", "synthetic:task-5"])

    def test_comparison_refusals(self):
        base = ev.evaluate_benchmark(self.plan, self.receipts_a)
        plan_changes = [
            (lambda p: p.update(level="level2"), "benchmark.level differs"),
            (lambda p: p.update(trial_budget=5), "benchmark.trial_budget differs"),
            (lambda p: p.update(verifier_revision="7656b71d07da6694e262f9c34ea994cd4849c0eb"), "benchmark.verifier_revision differs"),
            (lambda p: p.update(dataset_revision="synthetic-fixture-rev-2"), "benchmark.dataset_revision differs"),
            (lambda p: p.update(split="other"), "benchmark.split differs"),
        ]
        for mutate, message in plan_changes:
            plan = copy.deepcopy(self.plan)
            mutate(plan)
            receipts = self.rebind_receipts(copy.deepcopy(self.receipts_b), plan)
            with self.subTest(message=message):
                result = ev.compare_benchmark(base, ev.evaluate_benchmark(plan, receipts))
                self.assertEqual(result["status"], "refused")
                self.assertTrue(any(message in item for item in result["mismatches"]), result["mismatches"])
        plan = copy.deepcopy(self.plan)
        plan["tasks"] = plan["tasks"][:5]
        receipts = copy.deepcopy(self.receipts_b)
        receipts["records"] = [r for r in receipts["records"] if r["task_id"] != "synthetic:task-6"]
        receipts["final_submissions"] = [f for f in receipts["final_submissions"] if f["task_id"] != "synthetic:task-6"]
        result = ev.compare_benchmark(base, ev.evaluate_benchmark(plan, self.rebind_receipts(receipts, plan)))
        self.assertTrue(any("task_set_sha256 differs" in item for item in result["mismatches"]))
        for mutate, message in [
            (lambda d: d["settings"].update(network="open"), "settings.network differs"),
            (lambda d: d["settings"].update(dynamic_environment="unknown"), "settings.dynamic_environment is unknown"),
            (lambda d: d["settings"].update(cross_task_memory=True), "settings.cross_task_memory differs"),
            (lambda d: d["identity"].update(tools=["synthetic-read-only-tool", "synthetic-extra"]), "identity.tools differs"),
            (lambda d: d["identity"].update(model="unknown"), "identity.model is unknown"),
        ]:
            receipts = copy.deepcopy(self.receipts_b)
            mutate(receipts)
            with self.subTest(message=message):
                result = ev.compare_benchmark(base, ev.evaluate_benchmark(self.plan, receipts))
                self.assertEqual(result["status"], "refused")
                self.assertTrue(any(message in item for item in result["mismatches"]), result["mismatches"])


UNHASHABLE = ([], ["x"], {}, {"a": 1})


class MalformedInputTests(Base):
    """Invalid types are reported as input errors, never TypeError/KeyError tracebacks."""

    def test_unhashable_review_identifiers(self):
        for bad in UNHASHABLE:
            for mutate, message in [
                (lambda d: d["observations"][0].update(case_id=bad), "case_id must be a string"),
                (lambda d: d["observations"][0]["findings"][0].update(matches=bad), "matches must be an accepted defect"),
                (lambda d: d["observations"][0]["findings"][0].update(finding_id=bad), "finding_id must be an identifier"),
            ]:
                doc = copy.deepcopy(self.run_a)
                mutate(doc)
                with self.subTest(bad=bad, message=message):
                    self.invalid(ev.validate_run, doc, self.inventory, contains=message)
            for mutate, message in [
                (lambda d: d["cases"][0].update(case_id=bad), "case_id must be an identifier"),
                (lambda d: d["cases"][0].update(accepted_defects=[bad]), "accepted_defects[] must be an identifier"),
            ]:
                doc = copy.deepcopy(self.inventory)
                mutate(doc)
                with self.subTest(bad=bad, message=message):
                    self.invalid(ev.validate_inventory, doc, contains=message)

    def test_unhashable_benchmark_identifiers(self):
        for bad in UNHASHABLE:
            for mutate, message in [
                (lambda d: d["records"][0].update(task_id=bad), "records[0].task_id must be an identifier"),
                (lambda d: d["records"][0].update(agent_id=bad), "records[0].agent_id must be an identifier"),
                (lambda d: d["records"][0].update(poc_id=bad), "records[0].poc_id must be an identifier"),
                (lambda d: d["records"][0].update(poc_hash=bad), "records[0].poc_hash must be a nonblank"),
                (lambda d: d["final_submissions"][0].update(task_id=bad), "final_submissions[0].task_id must be a string"),
                (lambda d: d["final_submissions"][0].update(poc_id=bad), "final_submissions[0].poc_id must be a string"),
                (lambda d: d["task_errors"][0].update(task_id=bad), "task_errors[0].task_id must be a string"),
                (lambda d: d["measurements"][0].update(task_id=bad), "measurements[0].task_id must be a string"),
            ]:
                doc = copy.deepcopy(self.receipts_a)
                mutate(doc)
                with self.subTest(bad=bad, message=message):
                    self.invalid(ev.validate_receipts, doc, self.plan, contains=message)
            plan = copy.deepcopy(self.plan)
            plan["tasks"][0] = bad
            with self.subTest(bad=bad, plan=True):
                self.invalid(ev.validate_plan, plan, contains="tasks[] must be an identifier")

    def test_missing_exit_keys_with_success_flags(self):
        for key in ("vul_exit_code", "fix_exit_code"):
            for flagged in ("record", "final"):
                doc = copy.deepcopy(self.receipts_a)
                doc["records"][2].pop(key)
                doc["records"][2].pop("success")
                if flagged == "record":
                    doc["records"][2]["success"] = True
                else:
                    doc["final_submissions"][1]["success"] = True
                with self.subTest(key=key, flagged=flagged):
                    self.invalid(ev.validate_receipts, doc, self.plan, contains=f"missing {key!r}")

    def test_numeric_overflow_and_depth_are_input_errors(self):
        self.invalid(ev.parse_json_text, '{"a": 1e400}', contains="non-finite")
        self.invalid(ev.parse_json_text, '{"a": -1e400}', contains="non-finite")
        self.invalid(ev.parse_json_text, "[" * 40 + "]" * 40, contains="nesting deeper")
        self.invalid(ev.parse_json_text, "[" * 200000 + "]" * 200000, contains="nesting")
        self.assertEqual(ev.parse_json_text("[" * 32 + "]" * 32), [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]])
        for key, value in [("latency_ms", 10 ** 400), ("latency_ms", 2 ** 53 + 1), ("input_tokens", 2 ** 60)]:
            doc = copy.deepcopy(self.run_a)
            doc["observations"][0][key] = value
            with self.subTest(key=key, value=len(str(value))):
                self.invalid(ev.validate_run, doc, self.inventory, contains="<= 2**53")
        doc = copy.deepcopy(self.run_a)
        doc["identity"]["budget"]["max_minutes"] = 10 ** 400
        self.invalid(ev.validate_run, doc, self.inventory, contains="<= 2**53")
        receipts = copy.deepcopy(self.receipts_a)
        receipts["measurements"][0]["cost_usd"] = 10 ** 400
        self.invalid(ev.validate_receipts, receipts, self.plan, contains="<= 2**53")

    def test_non_object_documents_and_members(self):
        for bad in (None, 1, "x", [], True):
            with self.subTest(bad=bad):
                self.invalid(ev.validate_inventory, bad, contains="must be an object")
                self.invalid(ev.validate_plan, bad, contains="must be an object")
        run = copy.deepcopy(self.run_a)
        run["observations"].append(["not", "an", "object"])
        self.invalid(ev.validate_run, run, self.inventory, contains="must be an object")
        receipts = copy.deepcopy(self.receipts_a)
        receipts["records"].append("row")
        receipts["final_submissions"].append(7)
        self.invalid(ev.validate_receipts, receipts, self.plan, contains="final_submissions[4] must be an object")


class TimestampTests(Base):
    """One explicit grammar; normalization keeps to the Python 3.9 fromisoformat subset (not run on 3.9 here)."""

    def test_accepted_profiles(self):
        c = ev._Collector("t")
        utc = ev._timestamp(c, "2026-09-28T10:00:00.123Z", "x")
        self.assertEqual(utc, ev._timestamp(c, "2026-09-28 10:00:00.123000+00:00", "x"))
        self.assertEqual(utc.microsecond, 123000)
        self.assertEqual(utc.utcoffset().total_seconds(), 0)
        self.assertEqual(ev._timestamp(c, "2026-09-28T10:00:00.1Z", "x").microsecond, 100000)
        self.assertIsNone(ev._timestamp(c, "2026-09-28T10:00:00", "x").tzinfo)
        self.assertEqual(ev._timestamp(c, "2026-09-28T12:00:00+02:00", "x"), ev._timestamp(c, "2026-09-28T10:00:00Z", "x"))
        self.assertEqual(c.errors, [])

    def test_rejected_spellings(self):
        for text in ("2026-09-28T10:00:00.1234567Z", "2026-09-28T10:00Z", "2026-W39-1", "2026-09-28T10:00:00z",
                     "2026-09-28T10:00:00+0200", " 2026-09-28T10:00:00", 20260928, None):
            c = ev._Collector("t")
            with self.subTest(text=text):
                self.assertIsNone(ev._timestamp(c, text, "x"))
                self.assertEqual(len(c.errors), 1)

    def test_millisecond_z_records_score(self):
        receipts = copy.deepcopy(self.receipts_b)
        receipts["records"][0].update(created_at="2026-09-28T11:00:00.250Z", updated_at="2026-09-28T11:00:00.999Z")
        report = ev.evaluate_benchmark(self.plan, receipts)
        self.assertEqual(report["primary"]["numerator"], 3)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_review_and_benchmark_reports(self):
        out = run_cli("review", "--inventory", FIXTURES / "inventory.json", "--run", FIXTURES / "run-baseline.json")
        self.assertEqual(out.returncode, 0, out.stderr)
        report = json.loads(out.stdout)
        self.assertEqual(report["status"], "ok")
        self.assertFalse(report["release_clearance"])
        self.assertEqual(set(report["input_sha256"]), {"inventory", "run"})
        out = run_cli("benchmark", "--plan", FIXTURES / "plan.json", "--receipts", FIXTURES / "receipts-baseline.json")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertFalse(json.loads(out.stdout)["leaderboard_eligible"])

    def test_hash_matches_fixture_bindings(self):
        out = run_cli("hash", "--inventory", FIXTURES / "inventory.json")
        self.assertEqual(json.loads(out.stdout)["inventory_sha256"], fixture("run-baseline.json")["inventory_sha256"])
        out = run_cli("hash", "--plan", FIXTURES / "plan.json")
        self.assertEqual(json.loads(out.stdout)["plan_sha256"], fixture("receipts-baseline.json")["plan_sha256"])

    def test_invalid_input_exits_2_with_errors(self):
        bad = self.tmp / "run.json"
        bad.write_text('{"schema_version": 1, "latency_ms": NaN}', encoding="utf-8")
        out = run_cli("review", "--inventory", FIXTURES / "inventory.json", "--run", bad)
        self.assertEqual(out.returncode, 2)
        payload = json.loads(out.stdout)
        self.assertEqual(payload["status"], "invalid")
        self.assertFalse(payload["release_clearance"])
        out = run_cli("benchmark", "--plan", FIXTURES / "plan.json", "--receipts", self.tmp / "missing.json")
        self.assertEqual(out.returncode, 2)

    def test_malformed_identifiers_exit_2_json_not_traceback(self):
        receipts = fixture("receipts-baseline.json")
        cases = []
        for where, mutate in [
            ("records", lambda d: d["records"][0].update(task_id=["x"])),
            ("finals", lambda d: d["final_submissions"][0].update(task_id={"a": 1})),
            ("final-poc", lambda d: d["final_submissions"][0].update(poc_id=[])),
            ("task_errors", lambda d: d["task_errors"][0].update(task_id=[])),
            ("measurements", lambda d: d["measurements"][0].update(task_id={})),
            ("missing-exit", lambda d: (d["records"][2].pop("vul_exit_code"), d["records"][2].pop("success"))),
        ]:
            doc = copy.deepcopy(receipts)
            mutate(doc)
            cases.append((where, "benchmark", "--plan", FIXTURES / "plan.json", "--receipts", doc))
        run = fixture("run-baseline.json")
        for where, mutate in [
            ("observations", lambda d: d["observations"][0].update(case_id=["x"])),
            ("matches", lambda d: d["observations"][0]["findings"][0].update(matches={"a": 1})),
        ]:
            doc = copy.deepcopy(run)
            mutate(doc)
            cases.append((where, "review", "--inventory", FIXTURES / "inventory.json", "--run", doc))
        for where, command, flag_a, path_a, flag_b, doc in cases:
            path = self.tmp / f"{where}.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            with self.subTest(where=where):
                out = run_cli(command, flag_a, path_a, flag_b, path)
                self.assertEqual(out.returncode, 2, out.stdout + out.stderr)
                self.assertNotIn("Traceback", out.stderr)
                payload = json.loads(out.stdout)
                self.assertEqual(payload["status"], "invalid")
                self.assertTrue(payload["errors"])

    def test_overflow_and_deep_json_exit_2(self):
        for name, text in [("overflow", '{"latency_ms": 1e999}'), ("deep", "[" * 100000 + "]" * 100000),
                           ("bigint", '{"a": ' + "9" * 5000 + "}")]:
            path = self.tmp / f"{name}.json"
            path.write_text(text, encoding="utf-8")
            with self.subTest(name=name):
                out = run_cli("review", "--inventory", path, "--run", FIXTURES / "run-baseline.json")
                self.assertEqual(out.returncode, 2, out.stdout + out.stderr)
                self.assertNotIn("Traceback", out.stderr)
                self.assertEqual(json.loads(out.stdout)["status"], "invalid")

    def test_comparisons_and_refusal_exit_3(self):
        out = run_cli("compare-review", "--inventory", FIXTURES / "inventory.json",
                      "--baseline", FIXTURES / "run-baseline.json", "--candidate", FIXTURES / "run-candidate.json")
        self.assertEqual(out.returncode, 0, out.stdout)
        receipts = fixture("receipts-candidate.json")
        receipts["settings"]["network"] = "open"
        changed = self.tmp / "receipts.json"
        changed.write_text(json.dumps(receipts), encoding="utf-8")
        out = run_cli("compare-benchmark", "--plan", FIXTURES / "plan.json",
                      "--baseline", FIXTURES / "receipts-baseline.json", "--candidate", changed)
        self.assertEqual(out.returncode, 3, out.stdout)
        payload = json.loads(out.stdout)
        self.assertEqual(payload["status"], "refused")
        self.assertFalse(payload["release_clearance"])

    def test_ambiguous_comparison_inputs_are_usage_errors(self):
        out = run_cli("compare-review", "--inventory", FIXTURES / "inventory.json",
                      "--baseline-inventory", FIXTURES / "inventory.json",
                      "--baseline", FIXTURES / "run-baseline.json", "--candidate", FIXTURES / "run-candidate.json")
        self.assertEqual(out.returncode, 2)
        out = run_cli("compare-benchmark", "--baseline-plan", FIXTURES / "plan.json",
                      "--baseline", FIXTURES / "receipts-baseline.json", "--candidate", FIXTURES / "receipts-candidate.json")
        self.assertEqual(out.returncode, 2)


class BoundaryTests(unittest.TestCase):
    ALLOWED = {"__future__", "argparse", "datetime", "hashlib", "json", "math", "pathlib", "re", "sys",
               "typing", "review_evaluation"}

    def test_scorer_imports_no_execution_or_network_modules(self):
        for path in (ROOT / "lib" / "review_evaluation.py", CLI):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names |= {alias.name.split(".")[0] for alias in node.names}
                elif isinstance(node, ast.ImportFrom):
                    names.add((node.module or "").split(".")[0])
            with self.subTest(path=path.name):
                self.assertLessEqual(names, self.ALLOWED)

    def test_fixtures_are_declared_synthetic(self):
        paths = sorted(FIXTURES.glob("*.json"))
        self.assertEqual(len(paths), 6)
        for path in paths:
            with self.subTest(path=path.name):
                self.assertIs(json.loads(path.read_text(encoding="utf-8"))["synthetic"], True)


if __name__ == "__main__":
    unittest.main(verbosity=1)
