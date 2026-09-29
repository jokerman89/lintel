#!/usr/bin/env python3
# component: reusable-patterns-pack-origins-test
# implements: ADR-0038, ADR-0029
# intent: .claude/plans/reusable-patterns/plan.md
# constraints: synthetic temporary roots only; exercises the real launcher and existing profile accessors
# last_intent_review: 2026-09-28
"""V05 (cards 2.1.b-2.1.d): pack origins, same-snapshot transport, fail-closed drift and scopes."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pattern_pack_harness import Harness, binding, codes, make_pattern, p, ref  # noqa: E402


def manifest_path(directory: Path) -> str:
    return (directory / "pack.yaml").resolve().as_posix()


class OriginTests(unittest.TestCase):
    """Value and origin of patterns.source come from one ADR-0029 profile record."""

    def roots(self, h, **env):
        code, envelope, err = h.launch("roots", **env)
        self.assertEqual(code, 0, err)
        return envelope

    def test_neutral_bundled_null_keeps_its_origin_and_is_empty_success(self):
        h = Harness(self)
        context = self.roots(h)["pack_context"]
        self.assertEqual((context["status"], context["identity"]["name"]), ("neutral", "_default"))
        self.assertEqual(context["source"], {"state": "null", "value": None,
                                             "origin": manifest_path(h.source / "packs/_default")})
        code, listed, err = h.launch("list")
        self.assertEqual((code, listed["status"], listed["sources"], err), (0, "ok", [], ""))
        code, report, _ = h.launch("resolve", "--context", h.context())
        self.assertEqual((code, report["status"], report["selected"]), (0, "empty", []))

    def test_legacy_neutral_without_the_field_is_absent_and_compatible(self):
        h = Harness(self)
        h.legacy_neutral()
        context = self.roots(h)["pack_context"]
        self.assertEqual((context["status"], context["source"]),
                         ("neutral", {"state": "absent", "value": None, "origin": None}))
        self.assertEqual(h.launch("list")[0], 0)

    def test_inherited_parent_origin_and_same_snapshot_ancestry(self):
        h = Harness(self)
        base = h.pack("base", extra="patterns: {source: catalogs/base.json}\n")
        team = h.pack("team", extends="base")
        h.select("team")
        rule = make_pattern("example.base-rule")
        h.publish(base / "catalogs", "base.patterns", [rule], bindings=[binding("b", [ref("base.patterns", rule)])],
                  name="base.json")
        context = self.roots(h)["pack_context"]
        self.assertEqual(context["status"], "resolved")
        self.assertEqual(context["source"], {"state": "value", "value": "catalogs/base.json",
                                             "origin": manifest_path(base)})
        self.assertEqual([item["pack"] for item in context["ancestry"]], ["base", "team"])
        self.assertEqual([item["root"] for item in context["ancestry"]],
                         [base.resolve().as_posix(), team.resolve().as_posix()])
        code, record, err = h.accessor("profile_context_json")
        self.assertEqual(code, 0, err)
        profile = json.loads(record)["profile"]
        self.assertEqual([item["manifest_sha256"] for item in context["ancestry"]],
                         [item["digest"].removeprefix("sha256:") for item in profile["ancestry"]],
                         "ancestry digests are the profile snapshot's own, not recomputed")
        # Existing accessors keep their output: value and declaring manifest together.
        self.assertEqual(h.accessor('resolve_pack_field "$1"', "patterns.source")[1], "catalogs/base.json")
        provenance = json.loads(h.accessor('profile_field_provenance "$1"', "patterns.source")[1])
        self.assertEqual((provenance["name"], provenance["fallback"]), ("base", False))
        code, listed, _ = h.launch("list")
        self.assertEqual(code, 0)
        self.assertEqual([(item["locator"], item["scope"], item["active"]) for item in listed["sources"]],
                         [("pack:base", "pack", True)])
        code, report, _ = h.launch("resolve", "--context", h.context())
        self.assertEqual((code, report["status"]), (0, "ready"))
        self.assertEqual({item["scope"] for item in report["selected"]}, {"pack"})

    def test_child_block_and_explicit_null_replace_the_parent(self):
        h = Harness(self)
        base = h.pack("base", extra="patterns: {source: catalogs/base.json}\n")
        h.publish(base / "catalogs", "base.patterns", [make_pattern("example.base-rule")], name="base.json")
        team = h.pack("team", extends="base", extra="patterns: {source: null}\n")
        h.select("team")
        self.assertEqual(self.roots(h)["pack_context"]["source"],
                         {"state": "null", "value": None, "origin": manifest_path(team)})
        self.assertEqual(h.launch("list")[1]["sources"], [], "an ancestor catalog is never crawled")
        # An empty child block replaces the whole parent block; the neutral fill is the
        # effective value, so its fallback origin is reported with it.
        h.pack("team", extends="base", extra="patterns: {}\n")
        self.assertEqual(self.roots(h)["pack_context"]["source"],
                         {"state": "null", "value": None, "origin": manifest_path(h.source / "packs/_default")})
        provenance = json.loads(h.accessor('profile_field_provenance "$1"', "patterns.source")[1])
        self.assertEqual((provenance["name"], provenance["fallback"]), ("_default", True))
        self.assertEqual(h.accessor('resolve_pack_field "$1"', "patterns.source")[1], "null",
                         "the existing shell accessor output is unchanged")
        own = h.pack("team", extends="base", extra="patterns: {source: own.json}\n")
        h.publish(own, "team.patterns", [make_pattern("example.team-rule")], name="own.json")
        self.assertEqual(self.roots(h)["pack_context"]["source"]["origin"], manifest_path(own))
        self.assertEqual([item["locator"] for item in h.launch("list")[1]["sources"]], ["pack:team"])


class FailureTests(unittest.TestCase):
    """Required policy, fallback and declared-missing catalogs are never neutral success."""

    def test_required_pack_failure_is_an_explicit_error(self):
        h = Harness(self)
        (h.repo / ".claude").mkdir()
        (h.repo / ".claude/profile-requirements.json").write_text(
            json.dumps({"schema_version": 1, "required_pack": "missing"}), encoding="utf-8")
        code, envelope, _ = h.launch("roots")
        self.assertEqual(code, 0)
        context = envelope["pack_context"]
        self.assertEqual((context["status"], context["identity"], context["ancestry"]), ("error", None, []))
        self.assertEqual([item["code"] for item in context["diagnostics"]], ["PROFILE_REQUIRED"])
        for command in (("list",), ("resolve", "--context", h.context())):
            code, report, err = h.launch(*command)
            self.assertEqual((code, report["status"]), (5, "unavailable"), command)
            self.assertIn("pack_context_error", codes(report, "error"))
            self.assertIn("PROFILE_REQUIRED", err)
        code, report, _ = h.launch("list", LINTEL_PROFILE_PACK="also-missing")
        self.assertEqual(code, 5)

    def test_optional_fallback_blocks_patterns_but_not_old_callers(self):
        h = Harness(self)
        h.select("ghost")
        context = h.launch("roots")[1]["pack_context"]
        self.assertEqual((context["status"], context["identity"]["name"]), ("fallback", "_default"))
        self.assertTrue(context["diagnostics"])
        code, report, err = h.launch("resolve", "--context", h.context())
        self.assertEqual((code, report["status"]), (5, "unavailable"))
        self.assertIn("pack_context_fallback", codes(report, "error"))
        self.assertIn("OPTIONAL_PROFILE_FALLBACK", err)
        code, value, _ = h.accessor('resolve_pack_field "$1"', "voice.default_tier")
        self.assertEqual((code, value), (0, "internal"), "existing accessor fallback behavior is unchanged")

    def test_declared_missing_catalog_is_unavailable(self):
        h = Harness(self)
        h.pack("base", extra="patterns: {source: catalogs/missing.json}\n")
        h.select("base")
        code, report, _ = h.launch("list")
        self.assertEqual((code, report["status"], codes(report, "error")), (5, "unavailable", ["source_missing"]))


class DriftTests(unittest.TestCase):
    """A bound context fails closed on any changed input until an explicit, reasoned rebind."""

    def bound(self):
        h = Harness(self)
        base = h.pack("base", extra="patterns: {source: catalogs/base.json}\n")
        h.publish(base / "catalogs", "base.patterns", [make_pattern("example.base-rule")], name="base.json")
        h.pack("team", extends="base")
        h.select("team")
        h.session = "pack-lane-session"
        self.assertEqual(h.launch("list")[0], 0)
        return h, base

    def assert_drift(self, h):
        for _ in range(2):  # never an automatic rebind on retry
            code, report, err = h.launch("list")
            self.assertEqual((code, report["status"]), (5, "unavailable"))
            self.assertIn("PROFILE_DRIFT", err)

    def rebind(self, h, reason):
        return h.accessor('rebind_profile_context "$1"', reason)

    def test_manifest_drift_needs_a_reasoned_rebind(self):
        h, base = self.bound()
        manifest = base / "pack.yaml"
        manifest.write_text(manifest.read_text(encoding="utf-8") + "# edited\n", encoding="utf-8", newline="\n")
        self.assert_drift(h)
        self.assertNotEqual(self.rebind(h, "")[0], 0, "an empty reason is refused")
        self.assert_drift(h)
        code, _, err = self.rebind(h, "base manifest reviewed; replan dependent work")
        self.assertEqual(code, 0, err)
        self.assertEqual(h.launch("list")[0], 0)

    def test_pointer_drift_and_missing_cached_root_fail_closed(self):
        h, base = self.bound()
        h.select("base")
        self.assert_drift(h)
        h.select("team")
        self.assertEqual(h.launch("list")[0], 0, "restoring the bound inputs verifies again")
        shutil.rmtree(base)
        self.assert_drift(h)

    def test_adding_the_neutral_field_invalidates_stored_contexts(self):
        h = Harness(self)
        manifest = h.legacy_neutral()
        h.session = "pack-lane-neutral"
        self.assertEqual(h.launch("roots")[1]["pack_context"]["source"]["state"], "absent")
        shutil.copyfile(Path(__file__).resolve().parents[2] / "packs/_default/pack.yaml", manifest)
        self.assert_drift(h)
        self.assertEqual(self.rebind(h, "neutral manifest gained patterns.source: null")[0], 0)
        self.assertEqual(h.launch("roots")[1]["pack_context"]["source"]["state"], "null")

    def test_one_shot_snapshot_drift_and_missing_root(self):
        h = Harness(self)
        base = h.pack("base", extra="patterns: {source: catalogs/base.json}\n")
        h.publish(base / "catalogs", "base.patterns", [make_pattern("example.base-rule")], name="base.json")
        h.select("base")
        roots = h.inputs / "roots.json"
        roots.write_text(json.dumps(h.launch("roots")[1]), encoding="utf-8")
        self.assertEqual(h.cli("list", "--roots-file", roots)[0], 0)
        manifest = base / "pack.yaml"
        original = manifest.read_bytes()
        manifest.write_bytes(original + b"# changed after the snapshot\n")
        code, report, _ = h.cli("list", "--roots-file", roots)
        self.assertEqual((code, codes(report, "error")), (5, ["pack_snapshot_drift"]))
        manifest.write_bytes(original)
        shutil.rmtree(base)
        code, report, _ = h.cli("list", "--roots-file", roots)
        self.assertEqual((code, codes(report, "error")), (5, ["pack_snapshot_missing"]))


class ScopeTests(unittest.TestCase):
    """Catalog scope follows its own locator; personal patterns never activate from a pack."""

    def test_repository_include_of_any_ancestry_catalog_stays_pack_scope(self):
        h = Harness(self)
        base = h.pack("base")
        team = h.pack("team", extends="base", extra="patterns: {source: team.json}\n")
        h.select("team")
        h.publish(team, "team.patterns", [make_pattern("example.team-rule")], name="team.json")
        rule = make_pattern("example.base-rule")
        shared = h.publish(base / "shared", "base.shared", [rule], bindings=[binding("b", [ref("base.shared", rule)])])
        code, report, _ = h.launch("resolve", "--context", h.context())
        self.assertEqual((code, report["status"]), (0, "empty"), "registration alone activates nothing")
        h.publish(h.repo_patterns, "repo.main", [], includes=[
            {"locator": "pack:base", "path": "shared/catalog.json", "sha256": p.content_digest(shared)}])
        code, report, _ = h.launch("resolve", "--context", h.context())
        self.assertEqual((code, report["status"]), (0, "ready"))
        self.assertEqual([(item["ref"]["id"], item["scope"]) for item in report["selected"]],
                         [("example.base-rule", "pack")])
        scopes = {item["source_id"]: item["scope"] for item in report["sources"]}
        self.assertEqual((scopes["repo.main"], scopes["base.shared"]), ("repo", "pack"))
        h.publish(h.repo_patterns, "repo.main", [], includes=[
            {"locator": "pack:stranger", "path": "catalog.json", "sha256": p.content_digest(shared)}])
        code, report, _ = h.launch("list")
        self.assertNotEqual(code, 0)
        self.assertIn("include_locator_refused", codes(report, "error"))

    def test_personal_patterns_are_never_activated_by_a_pack(self):
        h = Harness(self)
        mine = make_pattern("example.mine")
        h.publish(h.home / "patterns", "me.personal", [mine], bindings=[binding("p", [ref("me.personal", mine)])])
        code, listed, _ = h.launch("list")
        self.assertEqual(code, 0)
        self.assertEqual([(item["scope"], item["active"]) for item in listed["sources"]], [("personal", False)])
        self.assertIn("personal_bindings_inactive", codes(listed))
        self.assertEqual(h.launch("resolve", "--context", h.context())[1]["status"], "empty")
        base = h.pack("base", extra="patterns: {source: catalog.json}\n")
        h.select("base")
        h.publish(base, "base.patterns", [], bindings=[binding("uses-personal", [ref("me.personal", mine)])])
        code, report, _ = h.launch("resolve", "--context", h.context())
        self.assertEqual((code, report["status"]), (5, "unavailable"))
        self.assertIn("personal_ref_refused", codes(report, "error"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
