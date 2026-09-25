#!/usr/bin/env python3
# component: native-route-contract-tests
# implements: ADR-0028
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: read-only source checks; not runtime or independent-review evidence
# last_intent_review: 2026-09-25
"""Check retained method boundaries after removing redundant public routes."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]


def source(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class NativeRoutes(unittest.TestCase):
    def test_cycle_ranges_keep_the_nine_phase_model(self):
        cycle = source("skills/cycle/SKILL.md")
        for route in (
            "/li:cycle --mode research-dive",
            "/li:cycle --from PLAN --to BUILD",
            "/li:cycle --from REVIEW --to CAPTURE",
        ):
            self.assertIn(route, cycle)
        self.assertRegex(
            cycle,
            r"SENSE\s+.+?\s+SCOPE\s+.+?\s+DEFINE\s+.+?\s+DISCOVER\s+.+?\s+PLAN"
            r"\s+.+?\s+BUILD\s+.+?\s+REVIEW\s+.+?\s+SHIP\s+.+?\s+CAPTURE",
        )
        self.assertIn("not BUILD approval", cycle)
        self.assertIn("BUILD package reviews remain required", cycle)

    def test_confirmation_overlay_retains_owned_recovery_without_host_claims(self):
        cycle = source("skills/cycle/SKILL.md")
        section = cycle.split("### Explicit confirmation and owned recovery", 1)[1]
        section = section.split("### Step 0", 1)[0]
        for boundary in (
            "per-mutation confirmation", "backup", "permission to run it",
            "whole-tree reset", "sanitized", "mandatory audit",
            "does not switch host modes",
        ):
            self.assertIn(boundary, section)

    def test_build_checkpoint_keys_remain_compatible_and_scoped(self):
        build = source("skills/build/SKILL.md")
        for field in ("checkpoint_mode", "checkpoint_push", "Work-map:", "Package:", "Leaves:"):
            self.assertIn(field, build)
        self.assertNotIn("[lintel-context]", build)
        self.assertIn("/li:pause", build)
        self.assertIn("/li:resume --from", build)
        self.assertIn("retain the checkpoint locally", build)
        self.assertIn("Serial self-review is not independent review", build)

    def test_catalog_retains_all_kind_filters_and_literal_selected_query(self):
        catalog = source("skills/catalog/SKILL.md")
        for option in ("--kind=all", "--category=qa", "--voice=internal", "--cli=copilot"):
            self.assertIn(option, catalog)
        selected = catalog.split("### Selected capability", 1)[1].split("## Generate", 1)[0]
        self.assertIn('${selection:?select a nonempty capability ID}', selected)
        self.assertIn('--json --selection="$selection"', selected)
        self.assertNotIn("eval ", selected)
        self.assertIn("not an inventory of active tools", catalog)

    def test_audience_overlay_stays_distinct_from_persistent_role(self):
        role = source("skills/role/SKILL.md")
        audience = role.split("## Audience context without a profile change", 1)[1]
        audience = audience.split("## Role resolution", 1)[0]
        for boundary in (
            "persona-sources", "defining manifest", "selected, authorized",
            "Missing names stay missing", "--clear-audience",
            "neither action edits profile files",
        ):
            self.assertIn(boundary, audience)

    def test_identity_migration_keeps_explicit_choice_and_recovery(self):
        migration = source("skills/migrations/SKILL.md")
        for boundary in (
            "migrations --all", "profile-status", "workprofile",
            'pack-switch "$selected_pack" --reason "$migration_reason"',
            "generation-bound", "old logs, preferences, backups",
            "separate owned operation",
        ):
            self.assertIn(boundary, migration)

    def test_review_reader_keeps_shared_clearance_and_read_only_history(self):
        reader = source("bin/li-review-read")
        self.assertIn("skill=inspect", reader)
        self.assertIn('exec "$python" "$helper" read --repo', reader)
        self.assertIn('if [ -f "$log" ]; then cat "$log"; fi', reader)
        self.assertNotRegex(reader, r"(?m)^\s*(mkdir|audit_log)\b")
        ship = source("skills/ship/SKILL.md")
        self.assertIn("never `--repair` after review", ship)
        self.assertIn("v2 review/context/QA", ship)
        self.assertIn("actual independent corroboration", ship)


if __name__ == "__main__":
    unittest.main()
