#!/usr/bin/env python3
# component: mars-hooks-tests
# implements: ADR-0034
# intent: skills/mars/references/integration.md
# constraints: reads canonical workflow text only; no sessions, models or network
# last_intent_review: 2026-09-25
"""Shape checks for the MARS workflow hooks and REVIEW's method-packet prompts."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DriftTests(unittest.TestCase):
    """RM5 (scoped): REVIEW's reviewer prompts come from the method; MARS hooks use the gate."""

    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_review_stage_prompts_come_from_the_method(self):
        text = self.read("skills/review/SKILL.md")
        stages = text[text.index("### Step 2 — Stage 1"):text.index("### Step 4 — Stage 3")]
        self.assertIn("references/method.md", stages)
        self.assertIn("li-review-packet.py", stages)
        for stale in ("Be terse", "P1 (block ship) / P2 (must fix) / P3 (nit)", "Dimensions:"):
            self.assertNotIn(stale, stages)

    def test_offer_hooks_route_through_the_gate_and_cycle_never_offers(self):
        for relative in ("skills/plan/SKILL.md", "skills/review/SKILL.md", "skills/code-review/SKILL.md"):
            text = self.read(relative)
            self.assertIn("../mars/SKILL.md", text, relative)
            self.assertIn("li-mars.py offer", text, relative)
        cycle = self.read("skills/cycle/SKILL.md")
        self.assertIn("never makes, repeats or upgrades that offer", cycle)
        self.assertIn("checkpoint\n`PLAN-approval`", self.read("skills/plan/SKILL.md"))


if __name__ == "__main__":
    unittest.main(verbosity=1)
