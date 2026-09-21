# component: observation-learning-tests
# implements: ADR-0006, ADR-0008, ADR-0028
# intent: .claude/plans/universal-implementation/packages/P08.md
# constraints: advisory freeze and retained retrieval only; A13.1/.2/.4 remain open
# last_intent_review: 2026-09-20
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, required=True)
args, remaining = parser.parse_known_args()
ROOT = args.root.resolve()


class ObservationPreservation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lintel-observations-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "synthetic repo"
        (self.repo / ".claude/memory").mkdir(parents=True)
        (self.repo / ".claude/lintel-layout.yaml").write_text("layout_version: 5\n")
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("LINTEL_", "CLAUDE_"))}
        self.env.update(LINTEL_SOURCE_ROOT=ROOT.as_posix(), LINTEL_REPO_ROOT=self.repo.as_posix(),
                        LINTEL_HOME=(self.root / "home").as_posix(),
                        HOME=(self.root / "home").as_posix(), LINTEL_OPERATOR="fixture",
                        LINTEL_AUDIT_DIR=(self.root / "audit").as_posix(),
                        LINTEL_SESSION_ID="synthetic-freeze")

    def shell(self, script):
        result = subprocess.run(["bash", "-c", "set -euo pipefail\n" + script],
                                cwd=self.repo, env=self.env, capture_output=True,
                                text=True, encoding="utf-8", input="")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_freeze_records_are_advisory_and_legacy_hook_only_warns(self):
        target = self.repo / "src/frozen/file.txt"
        target.parent.mkdir(parents=True)
        target.write_text("fixture baseline\n")
        canonical = self.repo / ".claude/runtime/state/code-freeze/synthetic-freeze.yaml"
        canonical.parent.mkdir(parents=True)
        freeze = "advisory: true\nfrozen:\n  - path: src/frozen/\n    reason: synthetic scope\n"
        canonical.write_text(freeze)
        hook = 'bash "$LINTEL_SOURCE_ROOT/hooks/shared/frozen-zone-warn/run.sh" src/frozen/file.txt'
        self.assertEqual(self.shell(hook), "", "canonical metadata must not be advertised as a wired hook")
        legacy = self.root / "home/freeze/synthetic-freeze.yaml"
        legacy.parent.mkdir(parents=True)
        legacy.write_text(freeze)
        self.assertIn("warn-only", self.shell(hook))
        event = json.loads((self.root / "audit/hooks.jsonl").read_text())
        self.assertEqual(event["kind"], "frozen_zone_warn")
        self.assertEqual(event["hook"], "frozen-zone-warn")
        self.assertEqual(event["tier"], "warn")
        self.assertEqual(self.shell(
            'source "$LINTEL_SOURCE_ROOT/bin/_audit.sh"\naudit_count hooks frozen_zone_warn'), "1\n")
        self.assertEqual(target.read_text(), "fixture baseline\n")
        # No filesystem lock was installed; an explicit fixture write remains possible.
        target.write_text("explicit fixture write\n")
        self.assertEqual(target.read_text(), "explicit fixture write\n")
        body = (ROOT / "skills/code-freeze/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("advisory", body)
        self.assertIn("no universal automatic freeze consumer", body)

    def test_existing_lesson_ids_and_superseded_history_remain_retrievable(self):
        lessons = self.repo / ".claude/memory/lessons.md"
        lessons.write_text("# Lessons\n\n## L-001 - Earlier test rule\n"
                           "superseded_by: L-002 (2026-09-20)\nTests were optional.\n\n"
                           "## L-002 - Keep actual test evidence\n"
                           "Rule: retain verified test output and provenance.\n", encoding="utf-8")
        before = lessons.read_bytes()
        out = self.shell('source "$LINTEL_SOURCE_ROOT/lib/memory.sh"\nlessons_surface test\nlessons_count')
        self.assertIn("L-002", out)
        self.assertNotIn("L-001", out)
        self.assertTrue(out.endswith("1\n"))
        self.assertEqual(lessons.read_bytes(), before)


if __name__ == "__main__":
    unittest.main(argv=[__file__, *remaining])
