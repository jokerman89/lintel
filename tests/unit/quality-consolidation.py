#!/usr/bin/env python3
# component: quality-workflow-contracts
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: documentary checks only; no client execution or independent review
# last_intent_review: 2026-09-25
"""Check native quality workflow routing and retained authority/evidence instructions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
RETIRED = ("qa", "qa-only", "investigate", "codex")
CURRENT = ("verify", "diagnose", "cross-check", "code-review", "perfbench")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?m)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.DOTALL
    )
    if match is None:
        raise AssertionError(f"Missing section: {heading}")
    return match.group(1)


class QualityWorkflowContracts(unittest.TestCase):
    def skill(self, name: str) -> str:
        path = f"skills/{name}/SKILL.md"
        self.assertTrue((ROOT / path).is_file(), f"Missing native workflow: {path}")
        return read(path)

    def test_native_entries_replace_duplicates(self) -> None:
        for name in CURRENT:
            with self.subTest(skill=name):
                text = self.skill(name)
                self.assertRegex(text, rf"(?m)^name: {re.escape(name)}$")
                self.assertRegex(text, r"(?m)^layer: foundation$")
                self.assertIn("cli_support:", text)
        for name in RETIRED:
            with self.subTest(retired=name):
                self.assertFalse((ROOT / "skills" / name / "SKILL.md").exists())

    def test_verify_default_is_read_only_and_has_no_implicit_retry(self) -> None:
        text = self.skill("verify")
        modes = section(text, "Modes and authority")
        for phrase in ("read-only default", "--repair", "--no-fix", "conflicting"):
            self.assertIn(phrase, modes)
        self.assertIn("does not authorize", modes)
        readonly = section(text, "Read-only verification")
        for phrase in ("Single run", "No automatic retry", "no fixes", "preflight"):
            self.assertIn(phrase, readonly)
        self.assertIn("side effects", readonly)

    def test_repair_preserves_authority_recovery_and_new_review(self) -> None:
        text = self.skill("verify")
        repair = section(text, "Authorized repair")
        for phrase in (
            "explicit", "owned paths", "frozen", "pre-images", "post-images",
            "conflict", "li-snapshot.py", "new context", "independent review",
            "read-only verification", "assertion", "STUCK",
        ):
            with self.subTest(requirement=phrase):
                self.assertIn(phrase, repair)
        self.assertNotIn("git reset", repair)
        self.assertNotIn("git checkout", repair)

    def test_verify_json_preserves_reporting_fields_not_clearance(self) -> None:
        text = self.skill("verify")
        report = section(text, "Report and JSON compatibility")
        blocks = re.findall(r"```json\n(.*?)\n```", report, re.DOTALL)
        self.assertEqual(1, len(blocks))
        example = json.loads(blocks[0])
        self.assertTrue(
            {"runner", "passes", "failures", "skipped", "exit", "failures_list"}
            <= example.keys()
        )
        self.assertEqual("read-only", example["mode"])
        self.assertEqual(1, example["failures"])
        self.assertEqual(1, len(example["failures_list"]))
        self.assertIn("not a release-clearance record", report)
        self.assertIn("raw runner exit", report)
        for label in ("Iterations:", "Initial failures:", "Auto-fixed:", "Remaining:"):
            self.assertIn(label, report)

    def test_verify_preserves_exact_v2_qa_inventory(self) -> None:
        text = self.skill("verify")
        evidence = section(text, "Evidence and acceptance")
        for phrase in (
            "qa_requirements", "context_digest", "li-review-evidence.py",
            "mandatory", "zero", "skipped", "not_applicable", "profile",
            "latest applicable", "corroboration", "exit 3",
        ):
            with self.subTest(requirement=phrase):
                self.assertIn(phrase, evidence)
        self.assertIn("cannot omit", evidence)
        self.assertIn("retype", evidence)
        self.assertIn("downgrade", evidence)
        self.assertIn("release_clearance: false", evidence)

    def test_diagnose_retains_owned_trials_and_recovery(self) -> None:
        text = self.skill("diagnose")
        for phrase in (
            "owned synthetic", "staged", "untracked", "original IDs",
            "pinned profile", "source/attempt", "next discriminating experiment",
            "not automatically rerun", "pre-images", "post-images", "conflict",
            "li-snapshot.py", "interrupted", "RegressionDetective",
        ):
            with self.subTest(requirement=phrase):
                self.assertIn(phrase, text)
        self.assertIn("../../agents/engineering/RegressionDetective.md#isolated-bisection-procedure", text)
        self.assertIn("No code mutation", text)
        self.assertIn("--cross-check", section(text, "Inputs"))
        self.assertNotIn("--with-codex", section(text, "Inputs"))

    def test_bisect_method_remains_owned_and_recoverable(self) -> None:
        text = read("agents/engineering/RegressionDetective.md")
        self.assertIn("never stash/switch the caller's checkout", text)
        self.assertIn("# lintel-isolated-bisect", text)
        self.assertIn('trap finish_bisect EXIT', text)
        self.assertIn('trap \'exit 130\' INT', text)
        self.assertIn('trap \'exit 143\' TERM', text)
        self.assertIn('bisect reset', text)
        self.assertIn("Recovery/reset fails", text)
        self.assertIn("Never persist it in local/global Git config", text)

    def test_cross_check_is_neutral_but_keeps_authorized_codex_route(self) -> None:
        text = self.skill("cross-check")
        for flag in ("--diff", "--plan", "--code", "--hypothesis", "--reviewer"):
            self.assertIn(flag, section(text, "Inputs"))
        for phrase in (
            "actual", "separate context", "read-only", "manual",
            "codex --help", "codex exec --help", "do not install",
        ):
            self.assertIn(phrase, text)
        self.assertIn("--skill cross-check", text)
        self.assertNotIn("--skill codex", text)
        self.assertIn("cli: codex", read("agents/engineering/CodeReviewer.md"))

    def test_cross_check_carries_shared_binding_and_missing_independence(self) -> None:
        text = self.skill("cross-check")
        for phrase in (
            "lib/review-schema.json", "li-review-log", "li-review-read",
            "attempt", "profile", "latest applicable", "corroboration",
            "release_clearance: false", "not a substitute", "independent review",
        ):
            with self.subTest(requirement=phrase):
                self.assertIn(phrase, text)
        self.assertIn("reviewer repair its own findings", text)
        self.assertIn("record_digest", text)

    def test_code_review_keeps_risk_and_severity_separate_from_clearance(self) -> None:
        text = self.skill("code-review")
        for phrase in (
            "--cross-check", "--no-cross-check", "does not waive",
            "P1", "P2", "P3", "confidence", "snapshot", "dirty",
            "verification-only", "mandatory", "corroboration", "skill: code-review",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("--codex", section(text, "Inputs"))
        self.assertNotIn("--no-codex", section(text, "Inputs"))
        self.assertIn("/inspect", text)
        reviewer = read("agents/engineering/CodeReviewer.md")
        for phrase in ("without fixing", "shared evidence contract", "profile", "verification-only"):
            self.assertIn(phrase, reviewer)

    def test_perfbench_capability_survives_alias_retirement(self) -> None:
        text = self.skill("perfbench")
        self.assertNotRegex(text, r"(?m)^v1_alias:")
        for phrase in (
            "--baseline", "--iterations", "--warmup", "--save-as-baseline",
            "comparable", "uncertainty", "retained", "PerformanceAnalyzer", "/diagnose",
        ):
            self.assertIn(phrase, text)

    def test_owned_callers_use_current_quality_commands(self) -> None:
        documents = sorted((ROOT / "agents").glob("*/*.md"))
        documents += [ROOT / "skills" / name / "SKILL.md" for name in CURRENT]
        pattern = re.compile(
            r"/(?:li:|li-)?(?:qa-only|qa|investigate|codex|office-hours|plan-eng-review"
            r"|design-review|design-html|browse|document-generate)(?=$|[\s`\"(])",
            re.MULTILINE,
        )
        for document in documents:
            with self.subTest(path=document.relative_to(ROOT)):
                self.assertTrue(document.is_file(), f"Missing workflow: {document}")
                self.assertIsNone(pattern.search(document.read_text(encoding="utf-8")))
        runner = read("agents/engineering/TestRunner.md")
        self.assertIn("/verify --repair", runner)
        self.assertIn("/diagnose", runner)
        self.assertIn("zero executed tests", runner)
        self.assertIn("No automatic retry", runner)

    def test_scoped_workflow_links_resolve(self) -> None:
        for name in CURRENT:
            document = ROOT / "skills" / name / "SKILL.md"
            text = self.skill(name)
            for target in re.findall(r"\]\(([^ )]+)\)", text):
                if target.startswith(("http:", "https:", "#")) or "<" in target:
                    continue
                with self.subTest(skill=name, target=target):
                    self.assertTrue((document.parent / target.split("#")[0]).exists())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args, remaining = parser.parse_known_args()
    ROOT = args.root.resolve()
    print("DOCUMENTARY checks only: no shared helper, owned trial or client is executed.",
          flush=True)
    unittest.main(argv=[__file__, *remaining], verbosity=2)
