#!/usr/bin/env python3
# component: adaptive-pattern-integration-tests
# implements: ADR-0040
# intent: .claude/plans/adaptive-review/spec.md
# constraints: real optional provider, synthetic local roots; no private packs, network or asset execution
# last_intent_review: 2026-09-28
"""Exercise the optional-provider boundary, and genuine locks when patterns is installed."""
import copy
import datetime
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
import review_context as rc

PROVIDER = ROOT / "lib" / "patterns.py"
PACKET = ROOT / "bin" / "li-review-packet.py"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


class ProviderBoundaryTests(unittest.TestCase):
    def test_installed_provider_state_is_explicit(self):
        provider, info = rc._load_provider()
        if PROVIDER.is_file() and sys.version_info >= (3, 10):
            self.assertTrue(info["available"])
            self.assertEqual(Path(provider.__file__).resolve(), PROVIDER.resolve())
        else:
            self.assertFalse(info["available"])
            result = rc.prepare_pattern_review(roots=Path("absent-roots.json"), lock=Path("absent-lock.json"),
                                               context=Path("absent-context.json"), task_map=Path("absent-map.json"),
                                               package="P1")
            self.assertEqual(result["status"], "unavailable")
            self.assertFalse(result["release_clearance"])


if PROVIDER.is_file() and sys.version_info >= (3, 10):
    class RealProviderJoinTests(unittest.TestCase):
        def setUp(self):
            self.tmp = tempfile.TemporaryDirectory(prefix="adaptive-pattern-")
            self.addCleanup(self.tmp.cleanup)
            self.root = Path(self.tmp.name).resolve()
            self.p, info = rc._load_provider()
            self.assertTrue(info["available"])
            self.repo = self.root / "repo"
            self.home = self.root / "personal"
            self.repo.mkdir()
            self.home.mkdir()
            pack = self.root / "neutral"
            pack.mkdir()
            manifest = b"name: _default\nversion: 1.0.0\n"
            (pack / "pack.yaml").write_bytes(manifest)
            ancestry = {"pack": "_default", "version": "1.0.0", "root": pack.as_posix(),
                        "manifest_sha256": hashlib.sha256(manifest).hexdigest()}
            self.envelope = {
                "schema_version": 1, "repository": self.repo.as_posix(), "personal": self.home.as_posix(),
                "pack_context": {
                    "schema_version": 1, "status": "neutral",
                    "identity": {"name": "_default", "version": "1.0.0"},
                    "source": {"state": "absent", "value": None, "origin": None},
                    "ancestry": [ancestry], "diagnostics": [],
                }, "diagnostics": [],
            }
            self.context = {"schema_version": 1, "facts": {"artifact": "library"},
                            "evidence": {"artifact": "accepted synthetic task"}}
            now = datetime.datetime.now(datetime.timezone.utc)
            timestamp = now.isoformat()
            self.pattern = {
                "schema_version": 1, "id": "example.review", "version": "1.0.0", "status": "approved",
                "summary": "Synthetic domain baseline", "owner": "synthetic team",
                "applies_to": {"artifact": ["library"]}, "includes": [],
                "sources": [{"kind": "operator-statement", "ref": "synthetic acceptance", "root": "statement",
                             "section": "", "observed_at": timestamp, "confidence": "confirmed",
                             "reuse": "internal use"}],
                "requirements": [
                    {"id": "M1", "level": "must", "text": "Preserve the accepted invariant", "verify": "local check"},
                    {"id": "D1", "level": "default", "text": "Use the selected style", "verify": "source trace",
                     "setting": "style.mode", "value": "compact"},
                ],
                "guidance": "",
                "assets": [{"path": "guide.md", "kind": "guide", "phases": ["review"],
                            "sha256": hashlib.sha256(b"synthetic selected guide\n").hexdigest()}],
                "approval": {"by": "synthetic owner", "reference": "synthetic task", "at": timestamp},
            }
            self.catalog_root = self.repo / ".claude" / "patterns"
            relative = "example.review/1.0.0/pattern.json"
            write_json(self.catalog_root / relative, self.pattern)
            (self.catalog_root / relative).with_name("guide.md").write_bytes(b"synthetic selected guide\n")
            self.ref = {"source": "repo.test", "id": self.pattern["id"], "version": "1.0.0",
                        "sha256": self.p.content_digest(self.pattern)}
            self.catalog = {
                "schema_version": 1, "source_id": "repo.test",
                "entries": [{key: self.pattern[key] for key in ("id", "version", "summary", "status", "applies_to")}],
                "includes": [], "bindings": [{"id": "baseline", "when": {"artifact": ["library"]},
                                              "use": [self.ref], "role": "required",
                                              "approved_by": "synthetic owner", "approval_ref": "synthetic task"}],
                "lifecycle": [],
            }
            self.catalog["entries"][0].update(path=relative, sha256=self.ref["sha256"])
            write_json(self.catalog_root / "catalog.json", self.catalog)
            self.roots = self.p.parse_roots(self.envelope)
            parsed_context = self.p.parse_context(self.context)
            selected = self.p.resolve(self.roots, parsed_context)
            self.assertEqual(selected["status"], "ready")
            lock = self.p.build_lock(selected, parsed_context)
            self.lock_path = self.repo / ".claude" / "plans" / "test" / "patterns.lock.json"
            self.lock_path.parent.mkdir(parents=True)
            self.p.write_lock(self.roots, self.lock_path, lock)
            self.mapping = {
                "schema_version": 1, "selection_digest": lock["selection_digest"], "tasks": ["T1", "T2"],
                "packages": [{"id": "P1", "tasks": ["T1", "T2"]}],
                "clauses": [{"clause": "example.review@1.0.0#M1", "tasks": ["T1"]},
                            {"clause": "example.review@1.0.0#D1", "tasks": ["T2"]}],
            }
            self.p.map_lock(self.roots, self.lock_path, self.mapping,
                            expected_lock_digest=self.p.content_digest(lock), write=True)
            self.lock = json.loads(self.lock_path.read_text(encoding="utf-8"))
            self.evidence = {
                "schema_version": 1, "selection_digest": self.lock["selection_digest"],
                "mapping_digest": self.lock["requirement_tasks"]["mapping_digest"],
                "items": [{"clause": "example.review@1.0.0#M1", "task_ids": ["T1"], "status": "passed",
                           "evidence_refs": ["synthetic-check:1"], "explanation": "Synthetic clause observation."}],
            }
            self.inputs = {
                "roots": write_json(self.root / "roots.json", self.envelope),
                "lock": self.lock_path, "context": write_json(self.root / "context.json", self.context),
                "task_map": write_json(self.root / "mapping.json", self.mapping),
                "package": "P1", "coverage": write_json(self.root / "evidence.json", self.evidence),
            }

        def test_genuine_lock_projection_and_coverage_match_the_provider(self):
            result = rc.prepare_pattern_review(**self.inputs)
            expected = self.p.project_package(self.lock, self.mapping, "P1")
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["projection"], expected)
            self.assertFalse(result["release_clearance"])
            self.assertFalse(result["coverage"]["release_clearance"])
            self.assertEqual(len(result["projection"]["clauses"]), 2)
            self.assertEqual(result["projection"]["settings"]["style.mode"]["value"], "compact")
            self.assertEqual(result["asset_refs"], self.lock["asset_pins"])
            self.assertTrue(any(d["code"] == "default_unverified" for d in result["diagnostics"]))
            self.assertEqual(result["metrics"].get("asset_reads"), 0, result["metrics"])

        def test_missing_mandatory_coverage_is_not_pass(self):
            missing = {**self.evidence, "items": []}
            write_json(self.inputs["coverage"], missing)
            result = rc.prepare_pattern_review(**self.inputs)
            self.assertEqual(result["status"], "review-unmet")
            self.assertFalse(result["release_clearance"])
            completed = subprocess.run(
                [sys.executable, "-B", str(PACKET), "pattern-context", "--roots", str(self.inputs["roots"]),
                 "--lock", str(self.lock_path), "--context", str(self.inputs["context"]),
                 "--task-map", str(self.inputs["task_map"]), "--package", "P1",
                 "--coverage", str(self.inputs["coverage"])], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 7, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["status"], "review-unmet")

        def test_revoked_source_stops_before_projection(self):
            self.catalog["revocations"] = [{
                **{key: self.ref[key] for key in ("id", "version", "sha256")},
                "reason": "synthetic revocation", "reference": "synthetic owner",
                "at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }]
            write_json(self.catalog_root / "catalog.json", self.catalog)
            result = rc.prepare_pattern_review(**self.inputs)
            self.assertEqual(result["status"], "unavailable")
            self.assertIsNone(result["projection"])
            self.assertIsNone(result["coverage"])
            self.assertIsNone(result["asset_refs"])

        def test_unknown_or_fallback_profile_is_not_empty(self):
            fallback = copy.deepcopy(self.envelope)
            fallback["pack_context"]["status"] = "fallback"
            fallback["pack_context"]["diagnostics"] = [{"code": "PROFILE_INVALID", "message": "Synthetic fallback."}]
            write_json(self.inputs["roots"], fallback)
            result = rc.prepare_pattern_review(**self.inputs)
            self.assertIn(result["status"], ("unavailable", "conflict"))
            self.assertIsNone(result["projection"])
            self.assertFalse(result["release_clearance"])


if __name__ == "__main__":
    print("Pattern provider: " + ("installed; real synthetic-lock join" if PROVIDER.is_file()
                                 else "not installed; unavailable-boundary check only"))
    unittest.main(verbosity=1)
