#!/usr/bin/env python3
# component: reusable-patterns-core-test
# implements: ADR-0038
# intent: .claude/plans/reusable-patterns/plan.md
# constraints: synthetic temporary roots only; never reads a real home, pack or session; no network
# last_intent_review: 2026-09-28
"""Behavior tests for lib/patterns.py and bin/li-pattern.py (verification keys V01-V04, V06)."""
from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
import patterns as p  # noqa: E402

CLI = ROOT / "bin" / "li-pattern.py"
TODAY = dt.date(2026, 9, 28)
TS = "2026-09-01T00:00:00Z"
NOW = dt.datetime(2026, 9, 28, 12, 0, 0, tzinfo=dt.timezone.utc)


def lock_of(report, context, **kwargs):
    """Every test lock is built at a fixed instant, so date-sensitive cases never depend on the wall clock."""
    kwargs.setdefault("now", NOW)
    return p.build_lock(report, context, **kwargs)


def statement(text="The operator stated this expectation."):
    return {"kind": "operator-statement", "ref": text, "root": "statement", "section": "",
            "observed_at": TS, "confidence": "confirmed", "reuse": "internal use"}


def make_pattern(pid, version="1.0.0", status="approved", applies_to=None, requirements=None,
                 includes=(), sources=None, summary=None, **extra):
    value = {
        "schema_version": 1, "id": pid, "version": version, "status": status,
        "summary": summary or f"Summary of {pid}", "owner": "platform team",
        "applies_to": {} if applies_to is None else applies_to, "includes": list(includes),
        "sources": [statement()] if sources is None else sources,
        "requirements": [{"id": "R-1", "level": "must", "text": f"{pid} rule", "verify": "Inspect it."}]
        if requirements is None else requirements,
        "guidance": "", "assets": [],
    }
    if status != "draft":
        value["approval"] = {"by": "architecture board", "reference": "ADR-0038", "at": TS}
    value.update(extra)
    return value


def clause(cid, level, setting=None, value=None, text=None):
    record = {"id": cid, "level": level, "text": text or f"{cid} text", "verify": f"check {cid}"}
    if setting is not None:
        record.update(setting=setting, value=value)
    return record


def ctx(**facts):
    return {"schema_version": 1, "facts": dict(facts), "evidence": {key: "brief.md" for key in facts}}


class Fixture:
    def __init__(self, testcase):
        self._tmp = tempfile.TemporaryDirectory(prefix="lintel-patterns-")
        testcase.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        self.repo = self.root / "repo"
        (self.repo / ".claude" / "patterns").mkdir(parents=True)
        self.home = self.root / "home"
        self.home.mkdir()
        self.packs = self.root / "packs"
        self.packs.mkdir()
        self.pack_context = self.neutral_context()

    # -- packs
    def manifest(self, name, text=None):
        directory = self.packs / name
        directory.mkdir(parents=True, exist_ok=True)
        data = (text or f"name: {name}\nversion: 1.0.0\n").encode("utf-8")
        (directory / "pack.yaml").write_bytes(data)
        return {"pack": name, "version": "1.0.0", "root": directory.as_posix(),
                "manifest_sha256": hashlib.sha256(data).hexdigest()}

    def neutral_context(self):
        ancestor = self.manifest("_default")
        return {"schema_version": 1, "status": "neutral", "identity": {"name": "_default", "version": "1.0.0"},
                "source": {"state": "absent", "value": None, "origin": None}, "ancestry": [ancestor],
                "diagnostics": []}

    def pack_chain(self, source="patterns/catalog.json", origin="base"):
        base, team = self.manifest("base"), self.manifest("team")
        self.pack_context = {
            "schema_version": 1, "status": "resolved", "identity": {"name": "team", "version": "1.0.0"},
            "source": {"state": "value", "value": source, "origin": f"{self.packs.as_posix()}/{origin}/pack.yaml"},
            "ancestry": [base, team], "diagnostics": []}
        return self.packs / origin

    # -- catalogs
    def publish(self, directory, source_id, patterns, bindings=(), includes=(), lifecycle=(), revocations=None,
                name="catalog.json"):
        directory = Path(directory)
        entries = []
        for pattern in patterns:
            relative = f"{pattern['id']}/{pattern['version']}/pattern.json"
            path = directory / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(pattern), encoding="utf-8")
            entries.append({"id": pattern["id"], "version": pattern["version"], "path": relative,
                            "sha256": p.content_digest(pattern), "summary": pattern["summary"],
                            "status": pattern["status"], "applies_to": pattern["applies_to"]})
        catalog = {"schema_version": 1, "source_id": source_id, "entries": entries, "includes": list(includes),
                   "bindings": list(bindings), "lifecycle": list(lifecycle)}
        if revocations is not None:
            catalog["revocations"] = list(revocations)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / name).write_text(json.dumps(catalog), encoding="utf-8")
        return catalog

    @property
    def repo_patterns(self):
        return self.repo / ".claude" / "patterns"

    @property
    def personal_patterns(self):
        return self.home / "patterns"

    def repo_bindings(self, bindings):
        (self.repo_patterns / "bindings.json").write_text(json.dumps({"schema_version": 1, "bindings": bindings}),
                                                          encoding="utf-8")

    def envelope(self, repository=True):
        return p.build_envelope(self.repo if repository else None, self.home, self.pack_context)

    def roots(self, repository=True):
        return p.parse_roots(self.envelope(repository))

    def resolve(self, context, **kwargs):
        kwargs.setdefault("today", TODAY)
        reader = kwargs.pop("reader", None) or p.Reader()
        report = p.resolve(self.roots(), p.parse_context(context), reader=reader, **kwargs)
        return report, reader

    def write_json(self, name, value):
        path = self.root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def cli(self, *args, stdin=None):
        env = {key: value for key, value in os.environ.items() if key in ("SYSTEMROOT", "PATH", "PATHEXT", "COMSPEC")}
        env.update(HOME=str(self.home), USERPROFILE=str(self.home), LINTEL_HOME=str(self.home),
                   TEMP=str(self.root), TMP=str(self.root), PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run([sys.executable, "-I", "-B", str(CLI), *map(str, args)], input=stdin,
                                capture_output=True, env=env, cwd=self.root, timeout=60)
        return result.returncode, json.loads(result.stdout.decode("utf-8")), result.stderr.decode("utf-8")


def ref(source, pattern):
    return {"source": source, "id": pattern["id"], "version": pattern["version"],
            "sha256": p.content_digest(pattern)}


def binding(bid, uses, role="required", when=None):
    return {"id": bid, "when": when or {}, "use": uses, "role": role, "approved_by": "lead",
            "approval_ref": "decision-1"}


def codes(report, severity=None):
    return [item["code"] for item in report["diagnostics"] if severity is None or item.get("severity") == severity]


def tree_digest(root: Path) -> dict:
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*")) if path.is_file()}


class SchemaTests(unittest.TestCase):
    """V01: records, canonical digests, strict JSON, limits and CLI contracts."""

    def assertInvalid(self, function, value, code=None):
        with self.assertRaises(p.PatternError) as caught:
            function(value)
        self.assertEqual(caught.exception.status, "invalid")
        if code:
            self.assertEqual(caught.exception.code, code, caught.exception.message)
        return caught.exception

    def test_pattern_roundtrip_and_canonical_digest(self):
        value = make_pattern("example.internal-dashboard", requirements=[
            clause("DASH-01", "must", "visual.layout.grid", "12-col"), clause("DASH-02", "default"),
            clause("DASH-03", "recommendation")], review_after="2027-01-01",
            extensions={"lintel.note": {"free": "form"}})
        pattern = p.parse_pattern(value)
        self.assertEqual(pattern.id, "example.internal-dashboard")
        self.assertEqual([item.level for item in pattern.requirements], ["must", "default", "recommendation"])
        self.assertEqual(pattern.requirements[0].to_json(), value["requirements"][0])
        self.assertEqual(pattern.clause_ref("DASH-01"), "example.internal-dashboard@1.0.0#DASH-01")
        reordered = json.loads(json.dumps(value, sort_keys=True))
        self.assertEqual(p.parse_pattern(reordered).digest, pattern.digest)
        self.assertEqual(pattern.digest, hashlib.sha256(json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest())
        emitted = p.emit_json({"b": 1, "a": "\u00e5"})
        self.assertEqual(emitted, '{\n  "a": "\u00e5",\n  "b": 1\n}\n')
        self.assertNotIn("\r", emitted)
        self.assertEqual(p.parse_json(b"\xef\xbb\xbf{}", limit=10, what="bom"), {})

    def test_strict_json_rejections(self):
        for data, code in ((b'{"a":1,"a":2}', "duplicate_key"), (b'{"a":NaN}', "non_finite_number"),
                           (b'{"a":Infinity}', "non_finite_number"), (b"{", "invalid_json"),
                           (b"\xff", "invalid_json"), (b"[" * 70 + b"]" * 70, "resource_limit")):
            self.assertInvalid(lambda item: p.parse_json(item, limit=1000, what="t"), data, code)
        self.assertInvalid(lambda item: p.parse_json(item, limit=3, what="t"), b'{"a":1}', "resource_limit")

    def test_pattern_rejections(self):
        base = make_pattern("example.dashboard")
        cases = [
            ({"schema_version": True}, "unsupported_schema"), ({"schema_version": 2}, "unsupported_schema"),
            ({"unexpected": 1}, "invalid_schema"), ({"version": "1.0.0-beta"}, "invalid_schema"),
            ({"version": "01.0.0"}, "invalid_schema"), ({"id": "Dashboard"}, "invalid_schema"),
            ({"id": "nodots"}, "invalid_schema"), ({"status": "active"}, "invalid_schema"),
            ({"summary": "x" * 241}, "resource_limit"), ({"guidance": "g" * 4001}, "resource_limit"),
            ({"requirements": [clause("A", "must"), clause("A", "default")]}, "invalid_schema"),
            ({"requirements": [{"id": "A", "level": "must", "text": "t", "verify": "v", "setting": "x.y"}]},
             "invalid_schema"),
            ({"requirements": [clause("A", "must", "x.y", [1])]}, "invalid_schema"),
            ({"requirements": [clause("A", "must", "x.y", {"k": 1})]}, "invalid_schema"),
            ({"requirements": [clause("a", "must")]}, "invalid_schema"),
            ({"requirements": [clause("A", "should")]}, "invalid_schema"),
            ({"applies_to": {"target": []}}, "invalid_schema"), ({"applies_to": {"Target": ["x"]}}, "invalid_schema"),
            ({"applies_to": {"target": ["a", "a"]}}, "invalid_schema"),
            ({"assets": [{"path": "../x", "kind": "guide", "sha256": "0" * 64}]}, "unsafe_path"),
            ({"assets": [{"path": "a.md", "kind": "guide", "sha256": "0" * 64, "phases": ["deploy"]}]},
             "invalid_schema"),
            ({"extensions": {"plain": 1}}, "invalid_schema"),
            ({"sources": [dict(statement(), observed_at="2026-09-01 00:00")]}, "invalid_schema"),
            ({"sources": [dict(statement(), kind="rumor")]}, "invalid_schema"),
            ({"includes": [{"source": "repo.main", "id": "example.dashboard", "version": "1.0.0",
                            "sha256": "0" * 64}]}, "include_cycle"),
        ]
        for change, code in cases:
            with self.subTest(change=change):
                value = copy.deepcopy(base)
                value.update(change)
                self.assertInvalid(p.parse_pattern, value, code)
        unapproved = copy.deepcopy(base)
        del unapproved["approval"]
        self.assertIn("approval", self.assertInvalid(p.parse_pattern, unapproved).message)
        self.assertInvalid(p.parse_pattern, make_pattern("example.dashboard", sources=[]))
        self.assertInvalid(p.parse_pattern, make_pattern("example.dashboard", requirements=[]))
        drafted = make_pattern("example.dashboard", status="draft")
        self.assertEqual(p.parse_pattern(drafted).status, "draft")
        drafted["approval"] = base["approval"]
        self.assertIn("draft", self.assertInvalid(p.parse_pattern, drafted).message)
        blueprint = make_pattern("example.blueprint", requirements=[], includes=[
            {"source": "repo.main", "id": "example.dashboard", "version": "1.0.0", "sha256": "a" * 64}])
        self.assertEqual(len(p.parse_pattern(blueprint).includes), 1)

    def test_spec_permitted_forms_are_accepted(self):
        """Guard against narrowing the spec: forms it permits must validate (review note R1)."""
        value = make_pattern("example.forms", requirements=[clause("A--B", "must"), clause("-9", "default")],
                             sources=[dict(statement(), observed_at="2026-09-01t00:00:00.5+00:00", section="",
                                           reuse="")],
                             approval={"by": "b" * 300, "reference": "r" * 900, "at": "2026-09-01T00:00:00z"})
        pattern = p.parse_pattern(value)
        self.assertEqual([item.id for item in pattern.requirements], ["A--B", "-9"])
        bound = p.parse_bindings({"schema_version": 1, "bindings": [dict(binding("Team Binding #1", [
            {"source": "repo.main", "id": "example.a", "version": "1.0.0", "sha256": "0" * 64}]))]})
        self.assertEqual(bound[0].id, "Team Binding #1")
        self.assertEqual(p.parse_context({"schema_version": 1, "facts": {"k": "v"},
                                          "evidence": {"k": "e" * 5000}}).facts, {"k": "v"})
        for bad in ("2026-09-01T00:00:00+01:00", "2026-09-01T00:00:00", "2026-09-01 00:00:00Z"):
            with self.subTest(bad=bad):
                self.assertInvalid(p.parse_pattern, dict(value, approval=dict(value["approval"], at=bad)))

    def test_lifecycle_order_uses_instants_not_spellings(self):
        fixture = Fixture(self)
        catalog = fixture.publish(fixture.repo_patterns, "repo.main", [make_pattern("example.dashboard")])
        entry = catalog["entries"][0]
        event = {"id": entry["id"], "version": "1.0.0", "sha256": entry["sha256"], "status": "deprecated",
                 "reason": "r", "reference": "ADR", "at": "2026-09-02T00:00:00Z"}
        same_instant = dict(event, status="retired", at="2026-09-02T00:00:00+00:00")
        self.assertIn("timestamp", self.assertInvalid(p.parse_catalog, dict(catalog, lifecycle=[event, same_instant])).message)
        later = dict(event, status="retired", at="2026-09-02t00:00:01z")
        self.assertEqual(len(p.parse_catalog(dict(catalog, lifecycle=[later, event])).lifecycle), 2)

    def test_catalog_records_lifecycle_and_limits(self):
        fixture = Fixture(self)
        pattern = make_pattern("example.dashboard")
        catalog = fixture.publish(fixture.repo_patterns, "repo.main", [pattern])
        entry = catalog["entries"][0]
        event = {"id": entry["id"], "version": entry["version"], "sha256": entry["sha256"], "status": "deprecated",
                 "reason": "superseded", "reference": "ADR-1", "at": "2026-09-02T00:00:00Z"}
        parsed = p.parse_catalog(dict(catalog, lifecycle=[event, dict(event, status="retired",
                                                                         at="2026-09-03T00:00:00Z")]))
        self.assertEqual([item.status for item in parsed.lifecycle], ["deprecated", "retired"])
        for change, message in (
            ({"lifecycle": [dict(event, status="retired"), dict(event, at="2026-09-03T00:00:00Z")]}, "transition"),
            ({"lifecycle": [event, dict(event, status="retired")]}, "timestamp"),
            ({"lifecycle": [dict(event, status="approved")]}, "deprecated or retired"),
            ({"lifecycle": [dict(event, sha256="1" * 64)]}, "registered entry"),
            ({"revocations": [{k: event[k] for k in ("id", "version", "sha256", "reason", "reference", "at")}] * 2},
             "duplicate"),
            ({"includes": [{"locator": "elsewhere", "path": "c.json", "sha256": "0" * 64}]}, "locator"),
            ({"entries": catalog["entries"] * 2}, "duplicate entry"),
            ({"bindings": [binding("b", [ref("repo.main", pattern)])] * 2}, "duplicate binding"),
            ({"source_id": "Repo"}, "source ID"),
        ):
            with self.subTest(message=message):
                self.assertIn(message, self.assertInvalid(p.parse_catalog, dict(catalog, **change)).message)
        many = dict(catalog, entries=[dict(entry, id=f"example.p{index}") for index in range(p.LIMITS.catalog_entries + 1)])
        self.assertInvalid(p.parse_catalog, many, "resource_limit")

    def test_context_binding_reference_override_exception_inputs(self):
        self.assertEqual(p.parse_context(ctx(target="dashboard")).facts, {"target": "dashboard"})
        self.assertInvalid(p.parse_context, {"schema_version": 1, "facts": {"target": "x"}, "evidence": {}})
        self.assertInvalid(p.parse_context, {"schema_version": 1, "facts": {"target": "x"},
                                             "evidence": {"target": " "}})
        self.assertInvalid(p.parse_bindings, {"schema_version": 1, "bindings": [binding("b", [])]})
        self.assertInvalid(p.parse_bindings, {"schema_version": 1, "bindings": [dict(binding("b", [
            {"source": "repo.main", "id": "example.a", "version": "1.0.0", "sha256": "0" * 64}]), role="optional")]})
        exact = {"source": "repo.main", "id": "example.a", "version": "1.0.0", "sha256": "0" * 64}
        item = {"ref": exact, "role": "default", "approved_by": "me", "approval_ref": "task"}
        self.assertEqual(p.parse_refs([item])[0].role, "default")
        self.assertInvalid(p.parse_refs, [item, item])
        self.assertInvalid(p.parse_refs, [dict(item, role="implicit")])
        override = {"setting": "x.y", "value": 1, "reason": "r", "approval_ref": "a", "replaces": ["example.a@1.0.0#A"]}
        self.assertInvalid(p.parse_overrides, {"schema_version": 1, "items": [override, override]})
        self.assertInvalid(p.parse_overrides, {"schema_version": 1, "items": [dict(override, replaces=["bad"])]})
        exception = {"clause": "example.a@1.0.0#A", "context_digest": "0" * 64, "reason": "r", "approval_ref": "a",
                     "approved_by": "b", "expires": "2026-13-01", "verification": "v"}
        self.assertInvalid(p.parse_exceptions, {"schema_version": 1, "items": [exception]})

    def test_pack_context_shape(self):
        fixture = Fixture(self)
        context = fixture.neutral_context()
        self.assertEqual(p.parse_pack_context(context).status, "neutral")
        for change in ({"source": {"state": "absent", "value": None, "origin": "/x/pack.yaml"}},
                       {"source": {"state": "value", "value": "c.json", "origin": None}},
                       {"source": {"state": "null", "value": None, "origin": None}},
                       {"status": "error"}, {"status": "fallback"}, {"ancestry": []},
                       {"identity": {"name": "other", "version": "1.0.0"}}):
            with self.subTest(change=change):
                self.assertInvalid(p.parse_pack_context, dict(context, **change))
        error = p.pack_context_from_profile(error=("PROFILE_REQUIRED", "required pack missing"))
        self.assertEqual((error["status"], error["identity"], error["source"]["state"]), ("error", None, "unavailable"))

    def test_pack_context_reuses_profile_record(self):
        """RN-01: inherited origin, explicit null, whole-block replacement and fallback from ADR-0029 records."""
        fixture = Fixture(self)
        profile = p._profile_module()
        base_required = ("voice:\n  default_tier: internal\ncompliance:\n  mode: advisory\n"
                         "navigation:\n  default_workflow: cycle\n")

        packs = fixture.root / "profile-packs"

        def pack(name, body):
            (packs / name).mkdir(parents=True, exist_ok=True)
            (packs / name / "pack.yaml").write_text(f"name: {name}\nversion: 1.0.0\n{body}", encoding="utf-8")

        pointer = fixture.home / "active-pack"

        def record(selected):
            pointer.write_text(selected, encoding="utf-8")
            config = profile.ProfileConfig(ROOT, fixture.repo, fixture.home, packs, pointer)
            return p.pack_context_from_profile(profile.resolve_profile(config))

        # The neutral baseline is explicit here (the fixture store outranks the installed source), so the
        # outcome does not depend on whether the installed _default declares patterns.source.
        pack("_default", base_required)
        pack("base", base_required + "patterns:\n  source: patterns/catalog.json\n")
        pack("team", "extends: base\n")
        inherited = record("team")
        self.assertEqual(inherited["status"], "resolved")
        self.assertEqual(inherited["source"]["state"], "value")
        self.assertEqual(Path(inherited["source"]["origin"]), (packs / "base" / "pack.yaml").resolve())
        self.assertEqual([item["pack"] for item in inherited["ancestry"]], ["base", "team"])
        self.assertEqual(inherited["ancestry"][0]["manifest_sha256"],
                         hashlib.sha256((packs / "base" / "pack.yaml").read_bytes()).hexdigest())
        pack("team", "extends: base\npatterns:\n  source: null\n")
        explicit_null = record("team")
        self.assertEqual(explicit_null["source"]["state"], "null")
        self.assertEqual(Path(explicit_null["source"]["origin"]), (packs / "team" / "pack.yaml").resolve())
        pack("team", "extends: base\npatterns:\n  other: x\n")
        self.assertEqual(record("team")["source"], {"state": "absent", "value": None, "origin": None},
                         "legacy neutral baseline without patterns.source: whole-block replacement leaves it absent")
        pack("_default", base_required + "patterns:\n  source: null\n")
        filled = record("team")["source"]
        self.assertEqual((filled["state"], filled["value"], Path(filled["origin"])),
                         ("null", None, (packs / "_default" / "pack.yaml").resolve()),
                         "new neutral baseline: ADR-0029 fills the missing field with its neutral-origin null")
        pack("team", "extends: base\n")
        self.assertEqual(record("team")["source"]["state"], "value", "an inherited value still wins over the default")
        pack("_default", base_required)
        fallback = record("missing-pack")
        self.assertEqual(fallback["status"], "fallback")
        self.assertTrue(fallback["diagnostics"])
        full = {"schema_version": 1, "context_id": None, "generation": 0, "reason": "", "previous": None,
                "profile": {"selection": {"mode": "neutral", "status": "loaded"}, "values": {}, "provenance": {},
                            "ancestry": []}, "digest": "sha256:" + "0" * 64}
        with self.assertRaises(p.PatternError) as caught:
            p.pack_context_from_profile(full)
        self.assertEqual(caught.exception.code, "invalid_pack_context")

    def test_cli_check_envelope_and_error_contract(self):
        fixture = Fixture(self)
        good = fixture.write_json("pattern.json", make_pattern("example.dashboard"))
        code, report, stderr = fixture.cli("check", "--path", good)
        self.assertEqual((code, report["status"], report["kind"]), (0, "ok", "pattern"))
        bad = fixture.write_json("bad.json", dict(make_pattern("example.dashboard"), status="live"))
        code, report, stderr = fixture.cli("check", "--path", bad, "--kind", "pattern")
        self.assertEqual((code, report["status"]), (2, "invalid"))
        self.assertIn("[lintel/pattern] invalid_schema", stderr)
        huge = fixture.root / "context.json"
        huge.write_text(json.dumps(ctx(target="x")) + " " * p.LIMITS.input_bytes, encoding="utf-8")
        envelope = fixture.write_json("roots.json", fixture.envelope())
        before = tree_digest(fixture.root)
        code, report, _ = fixture.cli("resolve", "--roots-file", envelope, "--context", huge)
        self.assertEqual((code, report["diagnostics"][0]["code"]), (2, "resource_limit"))
        self.assertEqual(set(p.REPORT_KEYS) - set(report), set())
        code, report, _ = fixture.cli("resolve", "--roots-file", envelope, "--context", huge, "--roots-stdin")
        self.assertEqual(code, 2)
        self.assertEqual(tree_digest(fixture.root), before, "failed CLI calls must not modify any file")
        code, built, _ = fixture.cli("envelope", "--personal", fixture.home, "--profile-error", "PROFILE_REQUIRED",
                                     "--profile-error-message", "required pack missing")
        self.assertEqual((code, built["pack_context"]["status"], built["repository"]), (0, "error", None))
        code, report, _ = fixture.cli("list", "--roots-stdin", stdin=json.dumps(built).encode("utf-8"))
        self.assertEqual((code, report["status"]), (5, "unavailable"))


class PathTests(unittest.TestCase):
    """V02: containment, links/junctions and size limits, without reading outside the fixture."""

    def test_relative_path_rules(self):
        for value in ("", "/abs", "C:/x", "c:x", "\\\\server\\share", "a\\b", "a//b", "./a", "a/../b", "..",
                      "a/./b", "a/b.", "a/b ", "nul", "a/CON.txt", "a/b\x00", "a/b?c", "a:b", 7):
            with self.subTest(value=value):
                with self.assertRaises(p.PatternError) as caught:
                    p.validate_relative_path(value)
                self.assertEqual(caught.exception.code, "unsafe_path")
        self.assertEqual(str(p.validate_relative_path("example/1.0.0/pattern.json")), "example/1.0.0/pattern.json")

    def _outside(self, fixture):
        outside = fixture.root / "outside"
        outside.mkdir()
        secret = make_pattern("example.secret")
        (outside / "pattern.json").write_text(json.dumps(secret), encoding="utf-8")
        return outside, secret

    def _catalog_with_path(self, fixture, secret, path):
        entry = {"id": secret["id"], "version": "1.0.0", "path": path, "sha256": p.content_digest(secret),
                 "summary": secret["summary"], "status": "approved", "applies_to": {}}
        catalog = {"schema_version": 1, "source_id": "repo.main", "entries": [entry], "includes": [],
                   "bindings": [binding("b", [ref("repo.main", secret)])], "lifecycle": []}
        (fixture.repo_patterns / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")

    def _assert_no_outside_reads(self, reader, outside):
        for _, path in reader.reads:
            self.assertNotIn(outside.resolve(), Path(path).resolve().parents)

    def test_traversal_in_catalog_entry_is_refused(self):
        fixture = Fixture(self)
        outside, secret = self._outside(fixture)
        self._catalog_with_path(fixture, secret, "../../../outside/pattern.json")
        reader = p.Reader()
        with self.assertRaises(p.PatternError) as caught:
            p.load_sources(fixture.roots(), reader)
        self.assertEqual(caught.exception.code, "unsafe_path")
        self._assert_no_outside_reads(reader, outside)

    def test_link_or_junction_escape_is_refused(self):
        fixture = Fixture(self)
        outside, secret = self._outside(fixture)
        link = fixture.repo_patterns / "linked"
        if os.name == "nt":
            import _winapi
            _winapi.CreateJunction(str(outside), str(link))
        else:
            os.symlink(outside, link, target_is_directory=True)
        self.addCleanup(lambda: os.rmdir(link) if os.name == "nt" else os.unlink(link))
        self._catalog_with_path(fixture, secret, "linked/pattern.json")
        reader = p.Reader()
        with self.assertRaises(p.PatternError) as caught:
            p.resolve(fixture.roots(), p.parse_context(ctx()), reader=reader, today=TODAY)
        self.assertEqual((caught.exception.code, caught.exception.status), ("unsafe_path", "invalid"))
        self.assertEqual(reader.count("pattern"), 0)
        self._assert_no_outside_reads(reader, outside)
        with self.assertRaises(p.PatternError):
            p.contained_path(fixture.repo_patterns, "linked")

    def test_include_escape_and_oversize_pattern(self):
        fixture = Fixture(self)
        fixture.publish(fixture.repo_patterns, "repo.main", [], includes=[
            {"locator": "repo", "path": "../../outside.json", "sha256": "0" * 64}])
        with self.assertRaises(p.PatternError) as caught:
            p.load_sources(fixture.roots())
        self.assertEqual(caught.exception.code, "unsafe_path")
        pattern = make_pattern("example.big", guidance="")
        fixture.publish(fixture.repo_patterns, "repo.main", [pattern], bindings=[binding("b", [ref("repo.main", pattern)])])
        path = fixture.repo_patterns / "example.big" / "1.0.0" / "pattern.json"
        path.write_bytes(path.read_bytes() + b" " * p.LIMITS.pattern_bytes)
        with self.assertRaises(p.PatternError) as caught:
            fixture.resolve(ctx())
        self.assertEqual(caught.exception.code, "resource_limit")

    def test_linked_anchors_are_refused_on_every_route(self):
        """PACK review F2: a junctioned repository or personal root is refused before resolution erases it."""
        fixture = Fixture(self)
        outside = fixture.root / "outside"
        (outside / ".claude" / "patterns").mkdir(parents=True)
        secret = make_pattern("example.outside")
        fixture.publish(outside / ".claude" / "patterns", "repo.outside", [secret],
                        bindings=[binding("b", [ref("repo.outside", secret)])])
        home_target = fixture.root / "home-target"
        home_target.mkdir()
        links = {"repository": fixture.root / "repo-link", "personal": fixture.root / "home-link"}
        for name, target in (("repository", outside), ("personal", home_target)):
            link = links[name]
            if os.name == "nt":
                import _winapi
                _winapi.CreateJunction(str(target), str(link))
            else:
                os.symlink(target, link, target_is_directory=True)
            self.addCleanup(lambda path=link: os.rmdir(path) if os.name == "nt" else os.unlink(path))
        before = tree_digest(outside)
        for repository, personal in ((links["repository"], fixture.home), (fixture.repo, links["personal"])):
            with self.subTest(repository=repository.name, personal=personal.name):
                with self.assertRaises(p.PatternError) as caught:
                    p.build_envelope(repository, personal, fixture.pack_context)
                self.assertEqual((caught.exception.code, caught.exception.status), ("invalid_roots", "invalid"))
                raw = {"schema_version": 1, "repository": str(repository), "personal": str(personal),
                       "pack_context": fixture.pack_context, "diagnostics": []}
                with self.assertRaises(p.PatternError):
                    p.parse_roots(raw)
                roots_file = fixture.write_json("linked-roots.json", raw)
                code, report, _ = fixture.cli("list", "--roots-file", roots_file)
                self.assertEqual((code, report["status"]), (2, "invalid"))
        code, report, stderr = fixture.cli("envelope", "--personal", fixture.home, "--repository", links["repository"],
                                           "--profile-error", "PROFILE_REQUIRED")
        self.assertEqual((code, report["status"]), (2, "invalid"))
        self.assertIn("real path", stderr)
        self.assertEqual(tree_digest(outside), before, "nothing was written through the link")
        self.assertEqual(p.build_envelope(outside, fixture.home, fixture.pack_context)["repository"],
                         outside.resolve().as_posix(), "the real path is accepted")

    def test_roots_envelope_validation(self):
        fixture = Fixture(self)
        envelope = fixture.envelope()
        for change in ({"repository": "relative/repo"}, {"personal": "home"},
                       {"repository": str(fixture.root / "missing")}, {"extra": 1}, {"schema_version": "1"}):
            with self.subTest(change=change):
                with self.assertRaises(p.PatternError):
                    p.parse_roots(dict(envelope, **change))
        personal_only = p.parse_roots(fixture.envelope(repository=False))
        self.assertIsNone(personal_only.repository)
        self.assertEqual(p.list_catalogs(personal_only)["status"], "ok")


class SelectorTests(unittest.TestCase):
    """V03: exact selectors, metadata-first selection, bounded advisory output and read counts."""

    def test_selector_decisions(self):
        selector = p.parse_pattern(make_pattern("example.a", applies_to={
            "artifact": ["dashboard", "report"], "audience": ["internal"]})).applies_to
        decide = lambda **facts: p.evaluate_selector(selector, p.parse_context(ctx(**facts)))
        self.assertEqual(decide(artifact="report", audience="internal").decision, "matched")
        self.assertEqual(decide(artifact="dashboard").decision, "needs-context")
        self.assertEqual(decide(artifact="dashboard").missing, ("audience",))
        self.assertEqual(decide(artifact="api").decision, "rejected", "known mismatch beats missing key")
        self.assertEqual(decide(artifact="Dashboard", audience="internal").decision, "rejected")
        universal = p.parse_pattern(make_pattern("example.b")).applies_to
        self.assertEqual(p.evaluate_selector(universal, p.parse_context(ctx())).decision, "matched")

    def _domains(self, fixture):
        dashboard = make_pattern("example.dashboard", applies_to={"artifact": ["dashboard"]})
        network = make_pattern("example.network", applies_to={"artifact": ["deployment"], "target": ["prod"]})
        document = make_pattern("example.report", applies_to={"artifact": ["report"]},
                                requirements=[clause("DOC-1", "must", text="Include a risks section")],
                                assets=[{"path": "guide.md", "kind": "guide", "sha256": "0" * 64}])
        patterns = [dashboard, network, document]
        fixture.publish(fixture.repo_patterns, "repo.main", patterns)
        fixture.repo_bindings([binding(f"bind-{item['id'][8:]}", [ref("repo.main", item)],
                                       when=item["applies_to"]) for item in patterns])
        return patterns

    def test_multi_domain_selection_reads_only_selected_bodies(self):
        fixture = Fixture(self)
        self._domains(fixture)
        report, reader = fixture.resolve(ctx(artifact="report"))
        self.assertEqual(report["status"], "ready")
        self.assertEqual([item["ref"]["id"] for item in report["selected"]], ["example.report"])
        self.assertEqual([item["clause"] for item in report["requirements"]], ["example.report@1.0.0#DOC-1"])
        self.assertEqual((reader.count("pattern"), reader.count("asset")), (1, 0))
        self.assertEqual(report["metrics"]["pattern_reads"], 1)
        unrelated, reader = fixture.resolve(ctx(artifact="backend-change"))
        self.assertEqual((unrelated["status"], reader.count("pattern"), reader.count("asset")), ("empty", 0, 0))
        deployment, _ = fixture.resolve(ctx(artifact="deployment"))
        self.assertEqual(deployment["status"], "needs-context")
        self.assertIn("required_binding_needs_context", codes(deployment))

    def test_advisory_candidates_are_bounded_metadata_only(self):
        fixture = Fixture(self)
        items = [make_pattern(f"example.c{index}", applies_to={"artifact": ["dashboard"]} if index % 2 else {},
                              summary=f"{index} " + "s" * 238) for index in range(8)]
        items.append(make_pattern("example.other", applies_to={"artifact": ["api"]}))
        fixture.publish(fixture.repo_patterns, "repo.main", items)
        report, reader = fixture.resolve(ctx(artifact="dashboard"))
        self.assertEqual(report["status"], "empty")
        self.assertEqual(report["candidates"]["total"], 8)
        self.assertEqual(len(report["candidates"]["items"]), 5)
        self.assertEqual([item["ref"]["id"] for item in report["candidates"]["items"]],
                         ["example.c1", "example.c3", "example.c5", "example.c7", "example.c0"])
        self.assertLessEqual(report["metrics"]["advisory_summary_code_points"], p.LIMITS.advisory_summary_total)
        self.assertTrue(all(len(item["summary"]) <= 240 for item in report["candidates"]["items"]))
        self.assertEqual((reader.count("pattern"), reader.count("asset")), (0, 0))
        self.assertEqual(report["requirements"], [], "unbound suggestions never become requirements")

    def test_list_show_and_read_once(self):
        fixture = Fixture(self)
        dashboard = make_pattern("example.dashboard")
        fixture.publish(fixture.repo_patterns, "repo.main", [dashboard, make_pattern("example.other")], bindings=[
            binding("one", [ref("repo.main", dashboard)]), binding("two", [ref("repo.main", dashboard)])])
        reader = p.Reader()
        listed = p.list_catalogs(fixture.roots(), reader)
        self.assertEqual([item["id"] for item in listed["entries"]], ["example.dashboard", "example.other"])
        self.assertEqual(reader.count("pattern"), 0)
        reader = p.Reader()
        shown = p.show_pattern(fixture.roots(), "repo.main:example.dashboard@1.0.0", reader)
        self.assertEqual((shown["pattern"]["id"], reader.count("pattern")), ("example.dashboard", 1))
        report, reader = fixture.resolve(ctx())
        self.assertEqual(report["selected"][0]["reasons"][1]["binding"], "two")
        self.assertEqual(reader.count("pattern"), 1, "a pattern reached twice is read once")
        envelope = fixture.write_json("roots.json", fixture.envelope())
        code, cli_list, _ = fixture.cli("list", "--roots-file", envelope)
        self.assertEqual((code, cli_list["metrics"]["pattern_reads"]), (0, 0))
        code, cli_show, _ = fixture.cli("show", "--roots-file", envelope, "--ref", "repo.main:example.missing@1.0.0")
        self.assertEqual((code, cli_show["status"]), (5, "unavailable"))

    def test_stale_metadata_and_changed_bytes_are_unavailable(self):
        fixture = Fixture(self)
        pattern = make_pattern("example.dashboard")
        catalog = fixture.publish(fixture.repo_patterns, "repo.main", [pattern],
                                  bindings=[binding("b", [ref("repo.main", pattern)])])
        path = fixture.repo_patterns / "example.dashboard" / "1.0.0" / "pattern.json"
        path.write_text(json.dumps(dict(pattern, guidance="edited")), encoding="utf-8")
        report, _ = fixture.resolve(ctx())
        self.assertEqual((report["status"], codes(report, "error")), ("unavailable", ["pattern_digest_mismatch"]))
        edited = dict(pattern, summary="Different summary")
        path.write_text(json.dumps(edited), encoding="utf-8")
        catalog["entries"][0]["sha256"] = p.content_digest(edited)
        catalog["bindings"] = [binding("b", [ref("repo.main", edited)])]
        (fixture.repo_patterns / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
        report, _ = fixture.resolve(ctx())
        self.assertEqual(codes(report, "error"), ["stale_metadata"])
        checked = p.check_sources(fixture.roots())
        self.assertEqual((checked["status"], checked["checked"][0]["status"]), ("unavailable", "unavailable"))

    def test_personal_scope_is_explicit_only(self):
        fixture = Fixture(self)
        pack_root = fixture.pack_chain()
        pack_rule = make_pattern("example.pack-rule")
        pack_catalog = fixture.publish(pack_root / "patterns", "team.patterns", [pack_rule])
        personal = make_pattern("example.dashboard", requirements=[clause("P-1", "must")])
        fixture.publish(fixture.personal_patterns, "me.personal", [personal],
                        bindings=[binding("mine", [ref("me.personal", personal)])],
                        includes=[{"locator": "pack:base", "path": "patterns/catalog.json",
                                   "sha256": p.content_digest(pack_catalog)}])
        report, reader = fixture.resolve(ctx())
        self.assertEqual((report["status"], reader.count("pattern")), ("empty", 0))
        self.assertEqual(report["candidates"]["total"], 1, "only the active pack entry is advisory")
        self.assertEqual(report["candidates"]["items"][0]["ref"]["id"], "example.pack-rule")
        self.assertIn("personal_bindings_inactive", codes(report))
        explicit = [{"ref": ref("me.personal", personal), "role": "required", "approved_by": "me", "approval_ref": "task"}]
        report, _ = fixture.resolve(ctx(), refs=p.parse_refs(explicit))
        self.assertEqual((report["status"], report["selected"][0]["scope"]), ("ready", "personal"))


class AuthorityTests(unittest.TestCase):
    """V04: mandatory survival, conflicts, precedence, overrides, exceptions and budgets."""

    def test_six_mandatory_patterns_survive_advisory_cap(self):
        fixture = Fixture(self)
        required = [make_pattern(f"example.m{index}") for index in range(6)]
        advisory = [make_pattern(f"example.a{index}") for index in range(10)]
        fixture.publish(fixture.repo_patterns, "repo.main", required + advisory)
        fixture.repo_bindings([binding("mandatory", [ref("repo.main", item) for item in required])])
        report, _ = fixture.resolve(ctx())
        self.assertEqual(report["status"], "ready")
        self.assertEqual(len([item for item in report["requirements"] if item["state"] == "mandatory"]), 6)
        self.assertEqual((report["candidates"]["total"], len(report["candidates"]["items"])), (10, 5))

    def test_required_versus_default_and_must_under_default(self):
        fixture = Fixture(self)
        rules = make_pattern("example.rules", requirements=[clause("A", "must"), clause("B", "default"),
                                                            clause("C", "recommendation")])
        fixture.publish(fixture.repo_patterns, "repo.main", [rules])
        fixture.repo_bindings([binding("dflt", [ref("repo.main", rules)], role="default")])
        report, _ = fixture.resolve(ctx())
        self.assertEqual(report["status"], "conflict")
        self.assertIn("must_under_default_binding", codes(report, "error"))
        fixture.repo_bindings([binding("req", [ref("repo.main", rules)])])
        report, _ = fixture.resolve(ctx())
        self.assertEqual([item["state"] for item in report["requirements"]], ["mandatory", "default", "recommendation"])
        self.assertEqual(report["selected"][0]["reasons"][0]["approval_ref"], "decision-1")

    def _settings(self, fixture, repo_items, pack_items=()):
        fixture.publish(fixture.repo_patterns, "repo.main", [item for item, _ in repo_items])
        bindings = [binding(f"r{index}", [ref("repo.main", item)], role=role) for index, (item, role) in enumerate(repo_items)]
        fixture.repo_bindings(bindings)
        if pack_items:
            pack_root = fixture.pack_chain()
            fixture.publish(pack_root / "patterns", "team.patterns", [item for item, _ in pack_items], bindings=[
                binding(f"p{index}", [ref("team.patterns", item)], role=role)
                for index, (item, role) in enumerate(pack_items)])

    def test_setting_conflicts_and_precedence(self):
        fixture = Fixture(self)
        must_a = make_pattern("example.must-a", requirements=[clause("A", "must", "ui.theme", "dark")])
        must_b = make_pattern("example.must-b", requirements=[clause("B", "must", "ui.theme", "light")])
        self._settings(fixture, [(must_a, "required"), (must_b, "required")])
        report, _ = fixture.resolve(ctx())
        self.assertEqual((report["status"], report["settings"]["ui.theme"]["state"]), ("conflict", "conflict"))
        self.assertIn("must_setting_conflict", codes(report, "error"))

        fixture = Fixture(self)
        default_light = make_pattern("example.default-light", requirements=[clause("D", "default", "ui.theme", "light")])
        self._settings(fixture, [(must_a, "required"), (default_light, "default")])
        report, _ = fixture.resolve(ctx())
        states = {item["clause"]: item["state"] for item in report["requirements"]}
        self.assertEqual(report["status"], "ready")
        self.assertEqual(states["example.default-light@1.0.0#D"], "suppressed")
        self.assertEqual(report["settings"]["ui.theme"]["value"], "dark")

        fixture = Fixture(self)
        default_blue = make_pattern("example.default-blue", requirements=[clause("E", "default", "ui.theme", "blue")])
        self._settings(fixture, [(default_light, "default"), (default_blue, "default")])
        report, _ = fixture.resolve(ctx())
        self.assertEqual(report["status"], "conflict")
        self.assertIn("default_setting_conflict", codes(report, "error"))
        overrides = p.parse_overrides({"schema_version": 1, "items": [{
            "setting": "ui.theme", "value": "blue", "reason": "brief chooses blue", "approval_ref": "brief.md",
            "replaces": ["example.default-light@1.0.0#D", "example.default-blue@1.0.0#E"]}]})
        report, _ = fixture.resolve(ctx(), overrides=overrides)
        self.assertEqual((report["status"], report["settings"]["ui.theme"]["winner"]), ("ready", "override"))
        self.assertEqual(report["overrides"][0]["value"], "blue")

        fixture = Fixture(self)
        pack_dark = make_pattern("example.pack-dark", requirements=[clause("K", "default", "ui.theme", "dark")])
        self._settings(fixture, [(default_light, "default")], [(pack_dark, "default")])
        report, _ = fixture.resolve(ctx())
        self.assertEqual(report["status"], "ready")
        self.assertEqual((report["settings"]["ui.theme"]["value"], report["settings"]["ui.theme"]["scope"]),
                         ("light", "repo"), "repository defaults outrank active-pack defaults")
        states = {item["clause"]: item["state"] for item in report["requirements"]}
        self.assertEqual(states["example.pack-dark@1.0.0#K"], "suppressed")

    def test_null_is_a_json_scalar_setting_value(self):
        """Spec 4.1/4.3: `value` is any JSON scalar, including null; not narrowed."""
        fixture = Fixture(self)
        pattern = p.parse_pattern(make_pattern("example.null", requirements=[clause("N", "must", "ui.banner", None)]))
        self.assertEqual(pattern.requirements[0].to_json()["value"], None)
        self.assertIn("value", pattern.requirements[0].to_json())
        must_null = make_pattern("example.must-null", requirements=[clause("N", "must", "ui.banner", None)])
        must_text = make_pattern("example.must-text", requirements=[clause("T", "must", "ui.banner", "hello")])
        self._settings(fixture, [(must_null, "required")])
        report, _ = fixture.resolve(ctx())
        self.assertEqual(report["status"], "ready")
        self.assertEqual(report["settings"]["ui.banner"], {"state": "mandatory", "value": None,
                                                           "winner": "example.must-null@1.0.0#N", "scope": "repo",
                                                           "clauses": ["example.must-null@1.0.0#N"]})
        fixture = Fixture(self)
        self._settings(fixture, [(must_null, "required"), (must_text, "required")])
        self.assertIn("must_setting_conflict", codes(fixture.resolve(ctx())[0], "error"),
                      "null and a string are different values")
        fixture = Fixture(self)
        default_text = make_pattern("example.default-text", requirements=[clause("D", "default", "ui.banner", "hi")])
        self._settings(fixture, [(default_text, "default")])
        overrides = p.parse_overrides({"schema_version": 1, "items": [{
            "setting": "ui.banner", "value": None, "reason": "brief removes the banner", "approval_ref": "brief.md",
            "replaces": ["example.default-text@1.0.0#D"]}]})
        report, _ = fixture.resolve(ctx(), overrides=overrides)
        self.assertEqual((report["status"], report["settings"]["ui.banner"]["value"]), ("ready", None))

    def test_overrides_and_exceptions(self):
        fixture = Fixture(self)
        must = make_pattern("example.must", requirements=[clause("A", "must", "ui.theme", "dark")])
        self._settings(fixture, [(must, "required")])
        context = ctx(target="dash")
        digest = p.parse_context(context).digest
        override = {"schema_version": 1, "items": [{"setting": "ui.theme", "value": "light", "reason": "r",
                                                    "approval_ref": "a", "replaces": ["example.must@1.0.0#A"]}]}
        report, _ = fixture.resolve(context, overrides=p.parse_overrides(override))
        self.assertEqual(report["status"], "conflict")
        self.assertIn("override_requires_exception", codes(report, "error"))
        exception = {"clause": "example.must@1.0.0#A", "context_digest": digest, "reason": "pilot", "approval_ref": "EX-1",
                     "approved_by": "security", "expires": "2026-12-31", "verification": "manual review"}
        report, _ = fixture.resolve(context, overrides=p.parse_overrides(override),
                                    exceptions=p.parse_exceptions({"schema_version": 1, "items": [exception]}))
        self.assertEqual(report["status"], "ready")
        self.assertEqual(report["requirements"][0]["state"], "waived")
        self.assertEqual(report["exceptions"][0]["approval_ref"], "EX-1")
        for change, code in (({"expires": "2026-09-27"}, "exception_expired"),
                             ({"context_digest": "0" * 64}, "exception_context_mismatch"),
                             ({"clause": "example.must@1.0.0#Z"}, "exception_unknown_clause")):
            with self.subTest(code=code):
                with self.assertRaises(p.PatternError) as caught:
                    fixture.resolve(context, exceptions=p.parse_exceptions(
                        {"schema_version": 1, "items": [dict(exception, **change)]}))
                self.assertEqual(caught.exception.code, code)
        for change, code in (({"setting": "ui.other"}, "override_unknown_setting"),
                             ({"replaces": ["example.must@1.0.0#Q"]}, "override_unknown_clause")):
            with self.subTest(code=code):
                bad = copy.deepcopy(override)
                bad["items"][0].update(change)
                with self.assertRaises(p.PatternError) as caught:
                    fixture.resolve(context, overrides=p.parse_overrides(bad))
                self.assertEqual(caught.exception.code, code)

    def test_explicit_references_keep_applicability_and_roles(self):
        fixture = Fixture(self)
        scoped = make_pattern("example.scoped", applies_to={"artifact": ["dashboard"], "target": ["prod"]})
        fixture.publish(fixture.repo_patterns, "repo.main", [scoped])

        def run(role, **facts):
            refs = p.parse_refs([{"ref": ref("repo.main", scoped), "role": role, "approved_by": "me",
                                  "approval_ref": "task"}])
            return fixture.resolve(ctx(**facts), refs=refs)[0]

        self.assertEqual(run("required", artifact="dashboard", target="prod")["status"], "ready")
        self.assertEqual(run("required", artifact="api")["status"], "conflict")
        self.assertEqual(run("required", artifact="dashboard")["status"], "needs-context")
        self.assertEqual(run("default", artifact="dashboard", target="prod")["status"], "conflict",
                         "an explicit default role never promotes must clauses")

    def test_lifecycle_eligibility_and_draft_preview(self):
        fixture = Fixture(self)
        draft = make_pattern("example.draft", status="draft")
        live = make_pattern("example.live")
        catalog = fixture.publish(fixture.repo_patterns, "repo.main", [draft, live])
        fixture.repo_bindings([binding("b", [ref("repo.main", draft)])])
        report, _ = fixture.resolve(ctx())
        self.assertEqual((report["status"], codes(report, "error")), ("unavailable", ["draft_not_eligible"]))
        fixture.repo_bindings([])
        refs = p.parse_refs([{"ref": ref("repo.main", draft), "role": "required", "approved_by": "me",
                              "approval_ref": "task"}])
        self.assertEqual(fixture.resolve(ctx(), refs=refs)[0]["status"], "unavailable")
        preview, _ = fixture.resolve(ctx(), refs=refs, preview_draft=True)
        self.assertEqual((preview["status"], preview["selected"][0]["preview"]), ("unavailable", True))
        self.assertIn("draft_preview_only", codes(preview, "error"))
        entry = catalog["entries"][1]
        event = {k: entry[k] for k in ("id", "version", "sha256")}
        fixture.publish(fixture.repo_patterns, "repo.main", [draft, live], bindings=[binding("b", [ref("repo.main", live)])],
                        lifecycle=[dict(event, status="deprecated", reason="old", reference="ADR", at=TS)])
        report, _ = fixture.resolve(ctx())
        self.assertEqual(report["status"], "ready")
        self.assertIn("pattern_deprecated", codes(report, "warning"))
        fixture.publish(fixture.repo_patterns, "repo.main", [draft, live], bindings=[binding("b", [ref("repo.main", live)])],
                        lifecycle=[dict(event, status="retired", reason="old", reference="ADR", at=TS)])
        self.assertIn("pattern_retired", codes(fixture.resolve(ctx())[0], "error"))
        fixture.publish(fixture.repo_patterns, "repo.main", [draft, live], bindings=[binding("b", [ref("repo.main", live)])],
                        revocations=[dict(event, reason="unsafe", reference="SEC-1", at=TS)])
        self.assertIn("pattern_revoked", codes(fixture.resolve(ctx())[0], "error"))

    def test_budget_never_truncates_mandatory_clauses(self):
        fixture = Fixture(self)
        big = make_pattern("example.big", requirements=[clause(f"R-{index}", "must", text="t" * 1900)
                                                        for index in range(14)])
        fixture.publish(fixture.repo_patterns, "repo.main", [big], bindings=[binding("b", [ref("repo.main", big)])])
        report, _ = fixture.resolve(ctx())
        self.assertEqual(report["status"], "needs-context")
        self.assertIn("budget_exceeded", codes(report, "error"))
        self.assertEqual(len(report["requirements"]), 14, "the complete clause inventory is still reported")
        self.assertEqual(fixture.resolve(ctx(), context_budget=40000)[0]["status"], "ready")
        with self.assertRaises(p.PatternError):
            fixture.resolve(ctx(), context_budget=0)

    def test_pack_status_and_no_pattern_compatibility(self):
        fixture = Fixture(self)
        report, reader = fixture.resolve(ctx(artifact="anything"))
        self.assertEqual((report["status"], report["requirements"], report["diagnostics"]), ("empty", [], []))
        self.assertEqual(sum(reader.count(kind) for kind in ("pattern", "asset", "manifest")), 0)
        fixture.pack_context = p.pack_context_from_profile(error=("PROFILE_REQUIRED", "company pack missing"))
        self.assertEqual(fixture.resolve(ctx())[0]["status"], "unavailable")
        fixture.pack_context = dict(fixture.neutral_context(), status="fallback",
                                    diagnostics=[{"code": "PACK_INVALID", "message": "broken"}])
        report, _ = fixture.resolve(ctx())
        self.assertEqual((report["status"], codes(report, "error")), ("unavailable", ["pack_context_fallback"]))

    def test_unverified_mandatory_sources_block_until_attested(self):
        fixture = Fixture(self)
        url = make_pattern("example.url", sources=[dict(statement(), root="external", kind="approved-standard",
                                                        ref="https://standards.example/doc")])
        overdue = make_pattern("example.overdue", review_after="2026-01-01")
        fixture.publish(fixture.repo_patterns, "repo.main", [url, overdue])
        fixture.repo_bindings([binding("u", [ref("repo.main", url)])])
        self.assertIn("source_attestation_required", codes(fixture.resolve(ctx())[0], "error"))
        fixture.repo_bindings([binding("o", [ref("repo.main", overdue)])])
        self.assertIn("review_overdue", codes(fixture.resolve(ctx())[0], "error"))
        defaulted = make_pattern("example.soft", review_after="2026-01-01", requirements=[clause("S", "default")])
        fixture.publish(fixture.repo_patterns, "repo.main", [defaulted],
                        bindings=[binding("s", [ref("repo.main", defaulted)], role="default")])
        fixture.repo_bindings([])
        report, _ = fixture.resolve(ctx())
        self.assertEqual(report["status"], "ready")
        self.assertIn("review_overdue_default", codes(report, "warning"))

    def test_cli_resolve_exit_codes(self):
        fixture = Fixture(self)
        rules = make_pattern("example.rules", applies_to={"target": ["prod"]})
        fixture.publish(fixture.repo_patterns, "repo.main", [rules])
        fixture.repo_bindings([binding("req", [ref("repo.main", rules)], when={"artifact": ["deployment"]})])
        envelope = json.dumps(fixture.envelope()).encode("utf-8")
        for facts, expected in (({"artifact": "deployment", "target": "prod"}, (0, "ready")),
                                ({"artifact": "deployment"}, (3, "needs-context")),
                                ({"artifact": "deployment", "target": "dev"}, (4, "conflict")),
                                ({"artifact": "backend"}, (0, "empty"))):
            with self.subTest(facts=facts):
                context = fixture.write_json("context.json", ctx(**facts))
                code, report, stderr = fixture.cli("explain", "--roots-stdin", "--context", context, stdin=envelope)
                self.assertEqual((code, report["status"]), expected)
                self.assertIn("explanation", report)
                self.assertEqual(bool(stderr), code != 0)


class _IncludeCases:
    """Card 2.2.a: pattern/catalog includes, cycles, depth, digests and pack snapshots."""

    def test_includes_inherit_requiredness_and_must_match_context(self):
        fixture = Fixture(self)
        child = make_pattern("example.child", applies_to={"target": ["prod"]}, requirements=[clause("C", "must")])
        parent = make_pattern("example.parent", requirements=[], includes=[ref("repo.main", child)])
        fixture.publish(fixture.repo_patterns, "repo.main", [child, parent],
                        bindings=[binding("b", [ref("repo.main", parent)])])
        report, _ = fixture.resolve(ctx(target="prod"))
        self.assertEqual(report["status"], "ready")
        states = {item["clause"]: (item["state"], item["role"]) for item in report["requirements"]}
        self.assertEqual(states["example.child@1.0.0#C"], ("mandatory", "required"))
        self.assertEqual(report["selected"][0]["reasons"][0]["kind"], "include")
        self.assertEqual(fixture.resolve(ctx(target="dev"))[0]["status"], "conflict")
        report, _ = fixture.resolve(ctx())
        self.assertEqual(report["status"], "needs-context")
        self.assertIn("include_blocked", codes(report))

    def test_cycles_depth_and_conflicting_digests(self):
        fixture = Fixture(self)
        a = make_pattern("example.a", requirements=[], includes=[
            {"source": "repo.main", "id": "example.b", "version": "1.0.0", "sha256": "0" * 64}])
        b = make_pattern("example.b", requirements=[], includes=[ref("repo.main", a)])
        catalog = fixture.publish(fixture.repo_patterns, "repo.main", [a, b])
        a["includes"] = [ref("repo.main", b)]
        catalog = fixture.publish(fixture.repo_patterns, "repo.main", [a, b],
                                  bindings=[binding("x", [ref("repo.main", a)])])
        with self.assertRaises(p.PatternError) as caught:
            fixture.resolve(ctx())
        self.assertIn(caught.exception.code, ("include_cycle", "conflicting_digest"))
        fixture = Fixture(self)
        chain = [make_pattern("example.n0")]
        for index in range(1, p.LIMITS.include_depth + 1):
            chain.append(make_pattern(f"example.n{index}", requirements=[], includes=[ref("repo.main", chain[-1])]))
        fixture.publish(fixture.repo_patterns, "repo.main", chain, bindings=[binding("deep", [ref("repo.main", chain[-1])])])
        report, _ = fixture.resolve(ctx())
        self.assertEqual((report["status"], len(report["selected"])), ("ready", p.LIMITS.include_depth + 1),
                         "exactly 16 include edges is within the limit")
        chain.append(make_pattern(f"example.n{p.LIMITS.include_depth + 1}", requirements=[],
                                  includes=[ref("repo.main", chain[-1])]))
        fixture.publish(fixture.repo_patterns, "repo.main", chain, bindings=[binding("deep", [ref("repo.main", chain[-1])])])
        with self.assertRaises(p.PatternError) as caught:
            fixture.resolve(ctx())
        self.assertEqual(caught.exception.code, "resource_limit", "17 edges exceeds it")

    def test_catalog_includes_ancestry_locators_and_snapshots(self):
        fixture = Fixture(self)
        base_root = fixture.pack_chain(source="patterns/catalog.json", origin="team")
        base_rule = make_pattern("example.base-rule")
        shared = fixture.publish(fixture.packs / "base" / "shared", "base.shared", [base_rule])
        team_rule = make_pattern("example.team-rule")
        fixture.publish(base_root / "patterns", "team.patterns", [team_rule], includes=[
            {"locator": "pack:base", "path": "shared/catalog.json", "sha256": p.content_digest(shared)}],
            bindings=[binding("t", [ref("base.shared", base_rule), ref("team.patterns", team_rule)])])
        report, reader = fixture.resolve(ctx())
        self.assertEqual(report["status"], "ready")
        self.assertEqual(sorted(item["source_id"] for item in report["sources"]), ["base.shared", "team.patterns"])
        self.assertEqual({item["scope"] for item in report["selected"]}, {"pack"})
        self.assertEqual(reader.count("manifest"), 2)
        shared_path = fixture.packs / "base" / "shared" / "catalog.json"
        shared_path.write_text(json.dumps(dict(shared, entries=[])), encoding="utf-8")
        report, _ = fixture.resolve(ctx())
        self.assertEqual(report["status"], "unavailable")
        self.assertIn("include_digest_mismatch", codes(report, "error"))
        (fixture.packs / "team" / "pack.yaml").write_text("name: team\nversion: 1.0.1\n", encoding="utf-8")
        report, _ = fixture.resolve(ctx())
        self.assertEqual(codes(report, "error"), ["pack_snapshot_drift"])

    def test_declared_missing_catalog_and_source_collisions(self):
        fixture = Fixture(self)
        fixture.pack_chain(source="patterns/missing.json")
        report, _ = fixture.resolve(ctx())
        self.assertEqual((report["status"], codes(report, "error")), ("unavailable", ["source_missing"]))
        fixture = Fixture(self)
        pack_root = fixture.pack_chain()
        fixture.publish(pack_root / "patterns", "same.source", [make_pattern("example.one")])
        fixture.publish(fixture.repo_patterns, "same.source", [make_pattern("example.two")])
        with self.assertRaises(p.PatternError) as caught:
            fixture.resolve(ctx())
        self.assertEqual(caught.exception.code, "source_id_collision")
        fixture = Fixture(self)
        fixture.pack_chain(origin="elsewhere")
        report, _ = fixture.resolve(ctx())
        self.assertEqual(codes(report, "error"), ["pack_source_origin_unknown"])


class LockFixture:
    """A ready selection with one mandatory, one default and one recommendation clause."""

    def __init__(self, testcase):
        self.t = testcase
        self.fx = Fixture(testcase)
        self.rules = make_pattern("example.rules", requirements=[
            clause("MUST-1", "must", "ui.theme", "dark"), clause("DEF-1", "default", "ui.density", "compact"),
            clause("REC-1", "recommendation")], assets=[{"path": "guide.md", "kind": "guide", "sha256": "a" * 64,
                                                         "phases": ["build"]}])
        self.other = make_pattern("example.other", requirements=[clause("MUST-2", "must")])
        self.publish()
        self.fx.repo_bindings([binding("req", [ref("repo.main", self.rules)], when={"artifact": ["dashboard"]})])
        self.context = ctx(artifact="dashboard")
        self.lock_path = self.fx.repo / ".claude" / "plans" / "demo" / "patterns.lock.json"
        self.lock_path.parent.mkdir(parents=True)

    def publish(self, extra=(), **kwargs):
        return self.fx.publish(self.fx.repo_patterns, "repo.main", [self.rules, self.other, *extra], **kwargs)

    def lock(self, now=dt.datetime(2026, 9, 28, 1, 2, 3, tzinfo=dt.timezone.utc)):
        report, _ = self.fx.resolve(self.context)
        self.t.assertEqual(report["status"], "ready")
        return lock_of(report, p.parse_context(self.context), now=now)

    def write(self):
        lock = self.lock()
        p.write_lock(self.fx.roots(), self.lock_path, lock)
        return lock

    def read(self):
        return json.loads(self.lock_path.read_text(encoding="utf-8"))

    def verify(self, context=None):
        return p.verify_lock(self.fx.roots(), self.read(), p.parse_context(context or self.context), today=TODAY)

    def task_map(self, **change):
        lock = self.read()
        value = {"schema_version": 1, "selection_digest": lock["selection_digest"], "tasks": ["T1", "T2", "T3"],
                 "packages": [{"id": "P1", "tasks": ["T1", "T2"]}, {"id": "P2", "tasks": ["T3"]}],
                 "clauses": [{"clause": "example.rules@1.0.0#MUST-1", "tasks": ["T1", "T3"]},
                             {"clause": "example.rules@1.0.0#DEF-1", "tasks": ["T2"]}]}
        value.update(change)
        return value


class _LockCases:
    """Card 2.2.b: explicit locks, stable digests and continuation verification."""

    def test_lock_contents_digest_and_portability(self):
        lf = LockFixture(self)
        first = lf.lock()
        second = lf.lock(now=dt.datetime(2027, 1, 1, tzinfo=dt.timezone.utc))
        self.assertEqual(first["selection_digest"], second["selection_digest"], "timestamps are not selection content")
        self.assertEqual(set(first), set(p.LOCK_KEYS))
        self.assertEqual(first["created_at"], "2026-09-28T01:02:03Z")
        self.assertEqual(first["asset_pins"], [{"path": "guide.md", "kind": "guide", "sha256": "a" * 64,
                                                "phases": ["build"], "pattern": ref("repo.main", lf.rules)}])
        self.assertEqual([item["locator"] for item in first["source_snapshots"]], ["repo"])
        self.assertEqual({item["clause"]: item["text"] for item in first["requirements"]}["example.rules@1.0.0#MUST-1"],
                         "MUST-1 text", "compact clause text travels with the lock")
        evidence_only = dict(first, review_evidence=[{"note": "x"}], source_attestations=[{"a": 1}],
                             metrics={"pattern_reads": 99})
        self.assertEqual(p.selection_digest(evidence_only), first["selection_digest"])
        written = p.write_lock(lf.fx.roots(), lf.lock_path, first)
        self.assertEqual(written["path"], ".claude/plans/demo/patterns.lock.json")
        data = lf.lock_path.read_bytes()
        self.assertTrue(data.endswith(b"}\n") and b"\r\n" not in data and not data.startswith(b"\xef\xbb\xbf"))
        for root in (lf.fx.repo, lf.fx.home, lf.fx.packs):
            self.assertNotIn(root.as_posix().encode(), data)
        self.assertEqual(p.parse_lock(json.loads(data))["selection_digest"], first["selection_digest"])

    def test_tampered_or_refused_locks(self):
        lf = LockFixture(self)
        lock = lf.lock()
        tampered = copy.deepcopy(lock)
        tampered["requirements"][0]["text"] = "weakened"
        with self.assertRaises(p.PatternError) as caught:
            p.parse_lock(tampered)
        self.assertIn("selection_digest", caught.exception.message)
        with self.assertRaises(p.PatternError):
            p.parse_lock(dict(lock, context=ctx(artifact="api")))
        report, _ = lf.fx.resolve(ctx())
        self.assertEqual(report["status"], "needs-context")
        with self.assertRaises(p.PatternError) as caught:
            lock_of(report, p.parse_context(ctx()))
        self.assertEqual((caught.exception.code, caught.exception.status), ("lock_refused", "needs-context"))
        p.write_lock(lf.fx.roots(), lf.lock_path, lock)
        before = lf.lock_path.read_bytes()
        with self.assertRaises(p.PatternError) as caught:
            p.write_lock(lf.fx.roots(), lf.lock_path, lf.lock(now=dt.datetime(2027, 1, 1, tzinfo=dt.timezone.utc)))
        self.assertEqual(caught.exception.status, "collision")
        self.assertEqual(lf.lock_path.read_bytes(), before, "an existing lock is never overwritten")
        with self.assertRaises(p.PatternError) as caught:
            p.write_lock(lf.fx.roots(), lf.fx.root / "outside.lock.json", lock)
        self.assertEqual(caught.exception.code, "unsafe_path")
        self.assertEqual(sorted(path.name for path in lf.lock_path.parent.iterdir()), ["patterns.lock.json"],
                         "no temp or lock-file residue")

    def test_verify_lock_continuation_cases(self):
        lf = LockFixture(self)
        lf.write()
        original = lf.lock_path.read_bytes()
        ok = lf.verify()
        self.assertEqual((ok["status"], [item["status"] for item in ok["checked"]]), ("ok", ["ok"]))
        lf.publish(extra=[make_pattern("example.unrelated", applies_to={"artifact": ["api"]})])
        ok = lf.verify()
        self.assertEqual(ok["status"], "ok", "unrelated catalog additions do not disturb a pin")
        self.assertEqual(ok["historical_sources"], json.loads(original)["source_snapshots"])
        self.assertIn("conflict", [lf.verify(ctx(artifact="report"))["status"]])
        self.assertIn("context_changed", codes(lf.verify(ctx(artifact="report")), "error"))
        entry = next(item for item in lf.publish()["entries"] if item["id"] == "example.rules")
        event = {k: entry[k] for k in ("id", "version", "sha256")}
        lf.publish(lifecycle=[dict(event, status="deprecated", reason="r", reference="ADR", at=TS)])
        report = lf.verify()
        self.assertEqual(report["status"], "ok")
        self.assertIn("pinned_deprecated", codes(report, "warning"))
        lf.publish(lifecycle=[dict(event, status="retired", reason="r", reference="ADR", at=TS)])
        self.assertEqual(codes(lf.verify(), "error"), ["pinned_retired"])
        lf.publish(revocations=[dict(event, reason="unsafe", reference="SEC-1", at=TS)])
        report = lf.verify()
        self.assertEqual((report["status"], codes(report, "error")), ("unavailable", ["pinned_revoked"]))
        self.assertEqual(lf.lock_path.read_bytes(), original, "verification never rewrites the lock")

    def test_verify_lock_changed_bytes_missing_source_and_baseline(self):
        lf = LockFixture(self)
        lf.write()
        edited = dict(lf.rules, guidance="changed after locking")
        lf.fx.publish(lf.fx.repo_patterns, "repo.main", [edited, lf.other])
        report = lf.verify()
        self.assertEqual((report["status"], codes(report, "error")), ("unavailable", ["reference_digest_mismatch"]))
        lf.publish()
        (lf.fx.repo_patterns / "catalog.json").unlink()
        self.assertEqual(codes(lf.verify(), "error"), ["source_unavailable"])
        lf.publish()
        lf.fx.repo_bindings([binding("req", [ref("repo.main", lf.rules)], when={"artifact": ["dashboard"]}),
                             binding("new", [ref("repo.main", lf.other)])])
        report = lf.verify()
        self.assertEqual(report["status"], "conflict")
        self.assertEqual(report["baseline"]["added"], ["example.other@1.0.0#MUST-2"])
        self.assertEqual(report["baseline"]["removed"], [])
        lf.fx.repo_bindings([binding("dflt", [ref("repo.main", lf.rules)], role="default",
                                     when={"artifact": ["dashboard"]})])
        report = lf.verify()
        self.assertEqual(report["status"], "conflict", "reducing a mandatory binding is a re-plan, never silent")

    def test_verify_lock_pack_drift_blocks(self):
        lf = LockFixture(self)
        pack_root = lf.fx.pack_chain()
        team_rule = make_pattern("example.team")
        lf.fx.publish(pack_root / "patterns", "team.patterns", [team_rule],
                      bindings=[binding("t", [ref("team.patterns", team_rule)])])
        lf.write()
        self.assertEqual(lf.verify()["status"], "ok")
        (lf.fx.packs / "base" / "pack.yaml").write_text("name: base\nversion: 2.0.0\n", encoding="utf-8")
        self.assertIn("pack_snapshot_drift", codes(lf.verify(), "error"))

    def test_cli_lock_roundtrip(self):
        lf = LockFixture(self)
        envelope = lf.fx.write_json("roots.json", lf.fx.envelope())
        context = lf.fx.write_json("context.json", lf.context)
        code, report, _ = lf.fx.cli("resolve", "--roots-file", envelope, "--context", context, "--lock", lf.lock_path)
        self.assertEqual((code, report["lock"]["path"]), (0, ".claude/plans/demo/patterns.lock.json"))
        code, again, _ = lf.fx.cli("resolve", "--roots-file", envelope, "--context", context, "--lock", lf.lock_path)
        self.assertEqual(code, 6)
        code, verified, _ = lf.fx.cli("verify-lock", "--roots-file", envelope, "--lock", lf.lock_path, "--context", context)
        self.assertEqual((code, verified["status"]), (0, "ok"))
        needs = lf.fx.write_json("needs.json", ctx())
        other = lf.fx.repo / ".claude" / "plans" / "demo" / "other.lock.json"
        code, report, _ = lf.fx.cli("resolve", "--roots-file", envelope, "--context", needs, "--lock", other)
        self.assertEqual((code, other.exists()), (3, False), "no lock for unknown mandatory context")
        entry = next(item for item in lf.publish()["entries"] if item["id"] == "example.rules")
        lf.publish(revocations=[{**{k: entry[k] for k in ("id", "version", "sha256")}, "reason": "r",
                                 "reference": "SEC", "at": TS}])
        code, verified, _ = lf.fx.cli("verify-lock", "--roots-file", envelope, "--lock", lf.lock_path, "--context", context)
        self.assertEqual((code, verified["status"]), (5, "unavailable"))


class _MappingCases:
    """Card 2.2.c: task mapping, projection and review-evidence invalidation."""

    def test_map_preview_write_and_projection(self):
        lf = LockFixture(self)
        lf.write()
        digest = p.content_digest(lf.read())
        preview = p.map_lock(lf.fx.roots(), lf.lock_path, lf.task_map(), expected_lock_digest=digest)
        self.assertEqual((preview["written"], lf.read()["requirement_tasks"]), (False, None))
        written = p.map_lock(lf.fx.roots(), lf.lock_path, lf.task_map(), expected_lock_digest=digest, write=True)
        lock = lf.read()
        self.assertTrue(written["written"])
        self.assertEqual(lock["requirement_tasks"]["mapping_digest"], preview["mapping_digest"])
        self.assertEqual(lock["selection_digest"], p.parse_lock(lock)["selection_digest"],
                         "regrouping work does not change the selection")
        first = p.project_package(lock, lf.task_map(), "P1")
        self.assertEqual([(item["clause"], item["task_ids"]) for item in first["clauses"]],
                         [("example.rules@1.0.0#DEF-1", ["T2"]), ("example.rules@1.0.0#MUST-1", ["T1"])])
        self.assertEqual(first["diagnostics"], [])
        self.assertEqual(sorted(first["settings"]), ["ui.density", "ui.theme"])
        second = p.project_package(lock, lf.task_map(), "P2")
        self.assertEqual([item["clause"] for item in second["clauses"]], ["example.rules@1.0.0#MUST-1"],
                         "shared clauses appear in every owning package")
        self.assertEqual((first["mapping_digest"], first["selection_digest"]),
                         (written["mapping_digest"], lock["selection_digest"]))
        with self.assertRaises(p.PatternError):
            p.project_package(lock, lf.task_map(), "P9")
        regrouped = lf.task_map(packages=[{"id": "P1", "tasks": ["T1", "T2", "T3"]}])
        warned = p.project_package(lock, regrouped, "P1")
        self.assertIn("mapping_not_installed", codes(warned, "warning"))

    def test_map_rejections_leave_lock_unchanged(self):
        lf = LockFixture(self)
        lf.write()
        before = lf.lock_path.read_bytes()
        digest = p.content_digest(lf.read())
        bad_maps = {
            "unknown task": {"packages": [{"id": "P1", "tasks": ["T1", "T2", "T9"]}, {"id": "P2", "tasks": ["T3"]}]},
            "two packages": {"packages": [{"id": "P1", "tasks": ["T1", "T2"]}, {"id": "P2", "tasks": ["T2", "T3"]}]},
            "unowned": {"packages": [{"id": "P1", "tasks": ["T1", "T2"]}]},
            "duplicate task": {"tasks": ["T1", "T1", "T2", "T3"]},
            "unknown clause": {"clauses": [{"clause": "example.rules@1.0.0#NOPE", "tasks": ["T1"]}]},
            "empty mapping": {"clauses": [{"clause": "example.rules@1.0.0#MUST-1", "tasks": []},
                                          {"clause": "example.rules@1.0.0#DEF-1", "tasks": ["T2"]}]},
            "unmapped must": {"clauses": [{"clause": "example.rules@1.0.0#DEF-1", "tasks": ["T2"]}]},
            "unmapped default": {"clauses": [{"clause": "example.rules@1.0.0#MUST-1", "tasks": ["T1"]}]},
            "other selection": {"selection_digest": "0" * 64},
        }
        for name, change in bad_maps.items():
            with self.subTest(name=name):
                with self.assertRaises(p.PatternError) as caught:
                    p.map_lock(lf.fx.roots(), lf.lock_path, lf.task_map(**change), expected_lock_digest=digest,
                               write=True)
                self.assertEqual(caught.exception.status, "invalid")
        self.assertEqual(lf.lock_path.read_bytes(), before)
        with self.assertRaises(p.PatternError) as caught:
            p.map_lock(lf.fx.roots(), lf.lock_path, lf.task_map(), expected_lock_digest="0" * 64, write=True)
        self.assertEqual((caught.exception.code, caught.exception.status), ("stale_lock_digest", "collision"))
        Path(str(lf.lock_path) + ".lock").write_text("another-writer", encoding="utf-8")
        with self.assertRaises(p.PatternError) as caught:
            p.map_lock(lf.fx.roots(), lf.lock_path, lf.task_map(), expected_lock_digest=digest, write=True)
        self.assertEqual(caught.exception.code, "write_locked")
        self.assertEqual(Path(str(lf.lock_path) + ".lock").read_text(encoding="utf-8"), "another-writer",
                         "a foreign lock is never stolen or removed")
        self.assertEqual(lf.lock_path.read_bytes(), before)
        recommendation_optional = lf.task_map()
        self.assertEqual(len(p.parse_task_map(recommendation_optional, lf.read())["clauses"]), 2)

    def test_remap_invalidates_old_task_evidence(self):
        lf = LockFixture(self)
        lf.write()
        first = p.map_lock(lf.fx.roots(), lf.lock_path, lf.task_map(),
                           expected_lock_digest=p.content_digest(lf.read()), write=True)
        lock = lf.read()
        lock["review_evidence"] = [{"mapping_digest": first["mapping_digest"], "clause": "x"}]
        lf.lock_path.write_text(p.emit_json(lock), encoding="utf-8")
        regrouped = lf.task_map(packages=[{"id": "P1", "tasks": ["T1", "T2", "T3"]}])
        second = p.map_lock(lf.fx.roots(), lf.lock_path, regrouped,
                            expected_lock_digest=p.content_digest(lf.read()), write=True)
        self.assertNotEqual(second["mapping_digest"], first["mapping_digest"])
        self.assertEqual((second["previous_mapping_digest"], second["invalidated_review_evidence"]),
                         (first["mapping_digest"], 1))
        self.assertEqual(lf.read()["review_evidence"], lock["review_evidence"], "old evidence is kept, not deleted")
        self.assertEqual(lf.read()["selection_digest"], lock["selection_digest"])

    def test_cli_map_and_project(self):
        lf = LockFixture(self)
        lf.write()
        envelope = lf.fx.write_json("roots.json", lf.fx.envelope())
        task_map = lf.fx.write_json("tasks.json", lf.task_map())
        digest = p.content_digest(lf.read())
        code, report, _ = lf.fx.cli("map", "--roots-file", envelope, "--lock", lf.lock_path, "--task-map", task_map,
                                    "--expected-lock-digest", digest, "--write")
        self.assertEqual((code, report["written"]), (0, True))
        code, report, _ = lf.fx.cli("map", "--roots-file", envelope, "--lock", lf.lock_path, "--task-map", task_map,
                                    "--expected-lock-digest", digest, "--write")
        self.assertEqual(code, 6, "the old digest is stale after the first write")
        code, projected, _ = lf.fx.cli("project", "--lock", lf.lock_path, "--task-map", task_map, "--package", "P2")
        self.assertEqual((code, [item["clause"] for item in projected["clauses"]]),
                         (0, ["example.rules@1.0.0#MUST-1"]))


class PinTests(_IncludeCases, _LockCases, _MappingCases, unittest.TestCase):
    """V06: includes, digests, lifecycle and context changes detected; cold projection complete."""


APPROVAL = {"by": "architecture board", "reference": "ADR-0038 review", "at": "2026-09-27T10:00:00Z"}


def draft(pid="example.dashboard", version="0.1.0", **extra):
    value = make_pattern(pid, version=version, status="draft", **extra)
    value.pop("approval", None)
    return value


class LifecycleTests(unittest.TestCase):
    """V07 (cards 3.1.a-3.1.c): capture, catalog-last publication, index and approve."""

    def setUp(self):
        self.fx = Fixture(self)
        self.root = self.fx.repo_patterns

    def roots(self):
        return self.fx.roots()

    def catalog(self):
        return json.loads((self.root / "catalog.json").read_text(encoding="utf-8"))

    def digest(self):
        return p.content_digest(self.catalog())

    def capture(self, value=None, **kwargs):
        value = value or draft()
        kwargs.setdefault("scope", "repo")
        kwargs.setdefault("name", value["id"])
        return p.capture(self.roots(), value, **kwargs)

    def test_first_capture_creates_source_and_draft(self):
        with self.assertRaises(p.PatternError) as caught:
            self.capture()
        self.assertEqual(caught.exception.code, "source_id_required")
        self.assertFalse((self.root / "catalog.json").exists())
        report = self.capture(source_id="team.repo")
        self.assertEqual((report["written"], report["ref"]["source"], report["published"][0]["recovered_staging"]),
                         (True, "team.repo", False))
        catalog = self.catalog()
        self.assertEqual((catalog["source_id"], [item["status"] for item in catalog["entries"]]), ("team.repo", ["draft"]))
        stored = self.root / "example.dashboard" / "0.1.0" / "pattern.json"
        self.assertEqual(p.content_digest(json.loads(stored.read_text(encoding="utf-8"))), report["ref"]["sha256"])
        listed = p.list_catalogs(self.roots())
        self.assertEqual([(item["id"], item["effective_status"]) for item in listed["entries"]],
                         [("example.dashboard", "draft")])
        self.assertIn("inferred_sources_only", codes(self.capture(
            draft("example.observed", sources=[dict(statement(), kind="observation", confidence="inferred")]),
            expected_catalog_digest=self.digest()), "warning"))

    def test_capture_refusals_write_nothing(self):
        self.capture(source_id="team.repo")
        before = tree_digest(self.root)
        cases = [
            (dict(draft(), status="approved", approval=APPROVAL), {"expected_catalog_digest": self.digest()},
             "capture_not_draft"),
            (draft(), {"name": "example.other", "expected_catalog_digest": self.digest()}, "capture_name_mismatch"),
            (draft(), {}, "expected_digest_required"),
            (draft(), {"expected_catalog_digest": "0" * 64}, "stale_catalog_digest"),
            (draft("example.new"), {"source_id": "other.id", "expected_catalog_digest": self.digest()},
             "source_id_mismatch"),
            (draft(), {"expected_catalog_digest": self.digest()}, "version_exists"),
        ]
        for value, kwargs, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(p.PatternError) as caught:
                    self.capture(value, **kwargs)
                self.assertEqual(caught.exception.code, code)
        self.assertEqual(tree_digest(self.root), before, "refused captures leave every file unchanged")
        with self.assertRaises(p.PatternError) as caught:
            p.capture(p.parse_roots(self.fx.envelope(repository=False)), draft(), scope="repo", name="example.dashboard")
        self.assertEqual(caught.exception.code, "repository_required")

    def test_personal_capture_without_repository(self):
        roots = p.parse_roots(self.fx.envelope(repository=False))
        report = p.capture(roots, draft(), scope="personal", name="example.dashboard", source_id="me.personal")
        self.assertEqual(report["scope"], "personal")
        self.assertTrue((self.fx.home / "patterns" / "catalog.json").is_file())
        self.assertEqual(p.list_catalogs(roots)["entries"][0]["active"], False, "personal content is never active")

    def test_exclusive_lock_and_interrupted_staging(self):
        self.capture(source_id="team.repo")
        foreign = self.root / "catalog.json.lock"
        foreign.write_text("someone-else", encoding="utf-8")
        before = tree_digest(self.root)
        with self.assertRaises(p.PatternError) as caught:
            self.capture(draft("example.second"), expected_catalog_digest=self.digest())
        self.assertEqual((caught.exception.code, caught.exception.status), ("write_locked", "collision"))
        self.assertEqual(tree_digest(self.root), before, "a held lock blocks every write and is never stolen")
        foreign.unlink()
        staged = draft("example.crashed")
        path = self.root / "example.crashed" / "0.1.0" / "pattern.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(staged), encoding="utf-8")
        indexed = p.index_source(self.roots(), self.root, expected_catalog_digest=self.digest())
        self.assertEqual((indexed["written"], [item["id"] for item in self.catalog()["entries"]]),
                         (False, ["example.dashboard"]), "interrupted staging is never discovered by index")
        different = self.root / "example.other" / "0.1.0" / "pattern.json"
        different.parent.mkdir(parents=True)
        different.write_text(json.dumps(draft("example.other", guidance="stray")), encoding="utf-8")
        with self.assertRaises(p.PatternError) as caught:
            self.capture(draft("example.other"), expected_catalog_digest=self.digest())
        self.assertEqual(caught.exception.code, "unregistered_staging_conflict")
        recovered = self.capture(staged, expected_catalog_digest=self.digest())
        self.assertTrue(recovered["published"][0]["recovered_staging"], "the owning operation completes its staging")
        self.assertEqual([item["id"] for item in self.catalog()["entries"]], ["example.dashboard", "example.crashed"])
        self.assertEqual(sorted(item.name for item in self.root.iterdir() if item.name.endswith((".lock", ".tmp"))), [])

    def test_index_rebuilds_metadata_and_preserves_everything_else(self):
        approved = make_pattern("example.live")
        catalog = self.fx.publish(self.root, "team.repo", [approved, make_pattern("example.gone")])
        entry = catalog["entries"][0]
        catalog["lifecycle"] = [{**{k: entry[k] for k in ("id", "version", "sha256")}, "status": "deprecated",
                                 "reason": "superseded", "reference": "ADR", "at": TS}]
        catalog["bindings"] = [binding("keep", [ref("team.repo", approved)])]
        catalog["revocations"] = []
        catalog["extensions"] = {"team.meta": {"owner": "x"}}
        gone = catalog["entries"].pop()
        catalog["entries"][0]["summary"] = "hand-edited summary"
        (self.root / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
        self.assertTrue((self.root / gone["path"]).is_file(), "the removed entry's directory stays on disk")
        report = p.index_source(self.roots(), self.root, expected_catalog_digest=self.digest())
        self.assertEqual(report["rebuilt"], [{"id": "example.live", "version": "1.0.0", "fields": ["summary"]}])
        rebuilt = self.catalog()
        self.assertEqual(rebuilt["entries"][0]["summary"], approved["summary"])
        for key in ("lifecycle", "bindings", "revocations", "includes", "extensions", "source_id"):
            self.assertEqual(rebuilt[key], catalog[key], f"index preserves {key}")
        self.assertEqual([item["id"] for item in rebuilt["entries"]], ["example.live"], "remove->index stays removed")
        self.assertEqual(p.list_catalogs(self.roots())["entries"][0]["effective_status"], "deprecated",
                         "deprecate->index keeps the effective state")
        again = p.index_source(self.roots(), self.root, expected_catalog_digest=self.digest())
        self.assertEqual((again["written"], again["rebuilt"]), (False, []))

    def test_index_refuses_edited_or_missing_content(self):
        pattern = make_pattern("example.live")
        self.fx.publish(self.root, "team.repo", [pattern])
        path = self.root / "example.live" / "1.0.0" / "pattern.json"
        path.write_text(json.dumps(dict(pattern, guidance="edited")), encoding="utf-8")
        before = (self.root / "catalog.json").read_bytes()
        with self.assertRaises(p.PatternError) as caught:
            p.index_source(self.roots(), self.root, expected_catalog_digest=self.digest())
        self.assertEqual(caught.exception.code, "pattern_digest_mismatch")
        path.unlink()
        with self.assertRaises(p.PatternError) as caught:
            p.index_source(self.roots(), self.root, expected_catalog_digest=self.digest())
        self.assertEqual(caught.exception.code, "registered_file_missing")
        self.assertEqual((self.root / "catalog.json").read_bytes(), before)
        with self.assertRaises(p.PatternError) as caught:
            p.index_source(self.roots(), self.fx.root)
        self.assertEqual(caught.exception.code, "invalid_source_root")

    def _draft_path(self, value):
        return self.root / value["id"] / value["version"] / "pattern.json"

    def test_approve_publishes_newer_version_and_keeps_draft(self):
        value = draft()
        self.capture(value, source_id="team.repo")
        draft_bytes = self._draft_path(value).read_bytes()
        args = {"approval_value": APPROVAL, "expected_digest": p.content_digest(value)}
        for version, code in (("0.1.0", "version_not_newer"), ("0.0.9", "version_not_newer")):
            with self.subTest(version=version):
                with self.assertRaises(p.PatternError) as caught:
                    p.approve(self.roots(), self._draft_path(value), version=version, **args)
                self.assertEqual(caught.exception.code, code)
        with self.assertRaises(p.PatternError) as caught:
            p.approve(self.roots(), self._draft_path(value), version="1.0.0", approval_value=APPROVAL,
                      expected_digest="0" * 64)
        self.assertEqual((caught.exception.code, caught.exception.status), ("stale_pattern_digest", "collision"))
        report = p.approve(self.roots(), self._draft_path(value), version="1.0.0", **args)
        self.assertEqual(report["ref"]["version"], "1.0.0")
        self.assertEqual(self._draft_path(value).read_bytes(), draft_bytes, "the draft is left unchanged")
        published = json.loads((self.root / "example.dashboard" / "1.0.0" / "pattern.json").read_text(encoding="utf-8"))
        self.assertEqual((published["status"], published["approval"]), ("approved", APPROVAL))
        self.assertEqual(p.content_digest(published), report["ref"]["sha256"], "approval is inside the digest")
        self.assertEqual([(item["version"], item["status"]) for item in self.catalog()["entries"]],
                         [("0.1.0", "draft"), ("1.0.0", "approved")])
        self.fx.repo_bindings([binding("b", [report["ref"]])])
        self.assertEqual(self.fx.resolve(ctx())[0]["status"], "ready")
        with self.assertRaises(p.PatternError) as caught:
            p.approve(self.roots(), self._draft_path(value), version="1.0.0", **args)
        self.assertEqual(caught.exception.code, "version_exists")
        approved_path = self.root / "example.dashboard" / "1.0.0" / "pattern.json"
        with self.assertRaises(p.PatternError) as caught:
            p.approve(self.roots(), approved_path, version="2.0.0", approval_value=APPROVAL,
                      expected_digest=report["ref"]["sha256"])
        self.assertEqual(caught.exception.code, "approve_not_draft")

    def test_approve_requires_sources_and_approved_dependencies(self):
        self.capture(draft("example.child"), source_id="team.repo")
        child_ref = {"source": "team.repo", "id": "example.child", "version": "0.1.0",
                     "sha256": p.content_digest(draft("example.child"))}
        parent = draft("example.parent", requirements=[], includes=[child_ref])
        self.capture(parent, expected_catalog_digest=self.digest())
        before = tree_digest(self.root)
        with self.assertRaises(p.PatternError) as caught:
            p.approve(self.roots(), self._draft_path(parent), version="1.0.0", approval_value=APPROVAL,
                      expected_digest=p.content_digest(parent))
        self.assertEqual((caught.exception.code, caught.exception.status), ("dependency_not_approved", "unavailable"))
        self.assertEqual(tree_digest(self.root), before)
        child = p.approve(self.roots(), self._draft_path(draft("example.child")), version="1.0.0",
                          approval_value=APPROVAL, expected_digest=child_ref["sha256"])
        updated_parent = draft("example.parent", version="0.2.0", requirements=[], includes=[child["ref"]])
        self.capture(updated_parent, expected_catalog_digest=self.digest())
        report = p.approve(self.roots(), self._draft_path(updated_parent), version="1.0.0", approval_value=APPROVAL,
                           expected_digest=p.content_digest(updated_parent))
        self.assertEqual(report["ref"]["id"], "example.parent", "children-first approval succeeds")
        unsourced = draft("example.unsourced", sources=[])
        self.capture(unsourced, expected_catalog_digest=self.digest())
        with self.assertRaises(p.PatternError) as caught:
            p.approve(self.roots(), self._draft_path(unsourced), version="1.0.0", approval_value=APPROVAL,
                      expected_digest=p.content_digest(unsourced))
        self.assertIn("source", caught.exception.message)

    def test_cli_capture_index_approve(self):
        envelope = self.fx.write_json("roots.json", self.fx.envelope())
        value = draft()
        source = self.fx.write_json("draft.json", value)
        code, report, _ = self.fx.cli("capture", "--roots-file", envelope, "--input", source, "--scope", "repo",
                                      "--name", "example.dashboard", "--source-id", "team.repo")
        self.assertEqual((code, report["written"]), (0, True))
        code, report, stderr = self.fx.cli("capture", "--roots-file", envelope, "--input", source, "--scope", "repo",
                                           "--name", "example.dashboard", "--expected-catalog-digest", self.digest())
        self.assertEqual(code, 6)
        self.assertIn("version_exists", stderr)
        code, report, _ = self.fx.cli("index", "--roots-file", envelope, "--source-root", self.root,
                                      "--expected-catalog-digest", self.digest())
        self.assertEqual((code, report["written"]), (0, False))
        approval = self.fx.write_json("approval.json", APPROVAL)
        code, report, _ = self.fx.cli("approve", "--roots-file", envelope, "--path", self._draft_path(value),
                                      "--version", "1.0.0", "--approval", approval,
                                      "--expected-digest", p.content_digest(value))
        self.assertEqual((code, report["ref"]["version"]), (0, "1.0.0"))


class ReviewRegressionTests(unittest.TestCase):
    """Regressions for independent review of eaffeb6c (F1-F7, advisories); names match the report."""

    def test_f1_ancestor_reparse_points_are_refused_for_reads_and_writes(self):
        for linked in (".claude", ".claude/patterns"):
            with self.subTest(linked=linked):
                fx = Fixture(self)
                outside = fx.root / "outside-target"
                target = outside / "patterns" if linked == ".claude" else outside
                target.mkdir(parents=True)
                secret = make_pattern("example.outside")
                fx.publish(target, "repo.outside", [secret], bindings=[binding("b", [ref("repo.outside", secret)])])
                repo = fx.root / "repo2"
                (repo / ".claude").mkdir(parents=True) if linked != ".claude" else repo.mkdir()
                link = repo / linked
                if os.name == "nt":
                    import _winapi
                    _winapi.CreateJunction(str(outside), str(link))
                else:
                    os.symlink(outside, link, target_is_directory=True)
                self.addCleanup(lambda path=link: os.rmdir(path) if os.name == "nt" else os.unlink(path))
                roots = p.parse_roots(p.build_envelope(repo, fx.home, fx.pack_context))
                reader = p.Reader()
                before = tree_digest(outside)
                for action in (lambda: p.resolve(roots, p.parse_context(ctx()), reader=reader, today=TODAY),
                               lambda: p.list_catalogs(roots, reader),
                               lambda: p.capture(roots, draft("example.new"), scope="repo", name="example.new",
                                                 source_id="repo.new")):
                    with self.assertRaises(p.PatternError) as caught:
                        action()
                    self.assertEqual((caught.exception.code, caught.exception.status), ("unsafe_path", "invalid"))
                self.assertEqual(reader.reads, [], "nothing is read through the reparse point")
                self.assertEqual(tree_digest(outside), before, "nothing is written through it")
        fx = Fixture(self)
        pattern = make_pattern("example.dir")
        fx.publish(fx.repo_patterns, "repo.main", [pattern], bindings=[binding("b", [ref("repo.main", pattern)])])
        body = fx.repo_patterns / "example.dir" / "1.0.0" / "pattern.json"
        body.unlink()
        body.mkdir()
        with self.assertRaises(p.PatternError) as caught:
            fx.resolve(ctx())
        self.assertEqual(caught.exception.code, "unsafe_path", "a directory at a file path is unsafe, not io_error")

    def test_f2_default_bound_integrity_failures_are_unavailable(self):
        for mode in ("tampered", "revoked", "retired", "missing", "draft"):
            with self.subTest(mode=mode):
                fx = Fixture(self)
                good = make_pattern("example.style", status="draft" if mode == "draft" else "approved",
                                    requirements=[clause("S-1", "default", "visual.layout.grid", "12")])
                catalog = fx.publish(fx.repo_patterns, "repo.main", [good])
                r = ref("repo.main", good)
                event = {"id": good["id"], "version": "1.0.0", "sha256": r["sha256"], "reason": "x",
                         "reference": "y", "at": TS}
                if mode == "tampered":
                    (fx.repo_patterns / "example.style" / "1.0.0" / "pattern.json").write_text(
                        json.dumps(dict(good, guidance="tampered")), encoding="utf-8")
                elif mode == "revoked":
                    catalog["revocations"] = [event]
                elif mode == "retired":
                    catalog["lifecycle"] = [dict(event, status="retired")]
                elif mode == "missing":
                    r = dict(r, version="9.9.9")
                (fx.repo_patterns / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
                fx.repo_bindings([binding("style", [r], role="default")])
                report, _ = fx.resolve(ctx())
                self.assertEqual((report["status"], p.exit_code(report["status"])), ("unavailable", 5))
                self.assertNotIn("default_skipped", codes(report))
        fx = Fixture(self)
        scoped = make_pattern("example.scoped", applies_to={"artifact": ["dashboard"]},
                              requirements=[clause("S-1", "default")])
        fx.publish(fx.repo_patterns, "repo.main", [scoped], bindings=[binding("d", [ref("repo.main", scoped)], role="default")])
        report, reader = fx.resolve(ctx(artifact="api"))
        self.assertEqual((report["status"], codes(report)), ("empty", ["default_not_applicable"]),
                         "only selector non-applicability skips a default")
        self.assertEqual(reader.count("pattern"), 0, "metadata-first: a non-applicable record reads no body")

    def test_f2_verify_lock_blocks_pinned_default_failures(self):
        lf = LockFixture(self)
        soft = make_pattern("example.soft", requirements=[clause("D-9", "default")])
        lf.publish(extra=[soft])
        lf.fx.repo_bindings([binding("req", [ref("repo.main", lf.rules)], when={"artifact": ["dashboard"]}),
                             binding("soft", [ref("repo.main", soft)], role="default")])
        lf.write()
        entry = next(item for item in lf.publish(extra=[soft])["entries"] if item["id"] == "example.soft")
        lf.publish(extra=[soft], revocations=[{**{k: entry[k] for k in ("id", "version", "sha256")},
                                               "reason": "r", "reference": "SEC", "at": TS}])
        report = lf.verify()
        self.assertEqual(report["status"], "unavailable")
        self.assertIn("pinned_revoked", codes(report, "error"))

    def test_f3_identical_content_from_two_sources_is_one_clause_identity(self):
        fx = Fixture(self)
        shared = make_pattern("example.shared", requirements=[clause("M-1", "must")])
        pack_root = fx.pack_chain()
        fx.publish(pack_root / "patterns", "pack.base", [shared], bindings=[binding("p", [ref("pack.base", shared)])])
        fx.publish(fx.repo_patterns, "repo.main", [shared],
                   bindings=[binding("r", [ref("repo.main", shared)], role="default", when={"never": ["x"]}),
                             binding("r2", [ref("repo.main", shared)])])
        context = ctx()
        exception = {"clause": "example.shared@1.0.0#M-1", "context_digest": p.parse_context(context).digest,
                     "reason": "r", "approval_ref": "a", "approved_by": "b", "expires": "2099-01-01",
                     "verification": "v"}
        report, _ = fx.resolve(context, exceptions=p.parse_exceptions({"schema_version": 1, "items": [exception]}))
        self.assertEqual(report["status"], "ready")
        self.assertEqual([(item["clause"], item["scope"], item["state"]) for item in report["requirements"]],
                         [("example.shared@1.0.0#M-1", "repo", "waived")])
        self.assertEqual(len(report["selected"]), 1)
        chosen = report["selected"][0]
        self.assertEqual((chosen["role"], chosen["ref"]["source"]), ("required", "repo.main"))
        self.assertEqual([item["source"] for item in chosen["equivalent_refs"]], ["pack.base", "repo.main"])
        self.assertEqual(sorted(reason.get("origin") for reason in chosen["reasons"]), ["pack.base", "repo.main"])
        fx = Fixture(self)
        pack_root = fx.pack_chain()
        other = dict(shared, guidance="different bytes")
        fx.publish(pack_root / "patterns", "pack.base", [other], bindings=[binding("p", [ref("pack.base", other)])])
        fx.publish(fx.repo_patterns, "repo.main", [shared], bindings=[binding("r", [ref("repo.main", shared)])])
        self.assertIn("clause_identity_collision", codes(fx.resolve(ctx())[0], "error"))

    def test_f4_included_pack_catalog_keeps_pack_scope(self):
        results = {}
        for include in (False, True):
            fx = Fixture(self)
            fx.pack_chain()
            pack_grid = make_pattern("example.pack-grid", requirements=[clause("G-1", "default", "visual.layout.grid", "8")])
            pack_catalog = fx.publish(fx.packs / "base" / "patterns", "pack.base", [pack_grid],
                                      bindings=[binding("pg", [ref("pack.base", pack_grid)], role="default")])
            repo_grid = make_pattern("example.repo-grid", requirements=[clause("G-1", "default", "visual.layout.grid", "12")])
            includes = [{"locator": "pack:base", "path": "patterns/catalog.json",
                         "sha256": p.content_digest(pack_catalog)}] if include else []
            fx.publish(fx.repo_patterns, "repo.main", [repo_grid], includes=includes,
                       bindings=[binding("rg", [ref("repo.main", repo_grid)], role="default"),
                                 binding("rp", [ref("pack.base", pack_grid)], role="default", when={"explicit": ["yes"]})])
            report, _ = fx.resolve(ctx())
            results[include] = (report["status"], report["settings"]["visual.layout.grid"]["value"],
                                sorted((item["source_id"], item["scope"]) for item in report["sources"]))
            if include:
                selected, _ = fx.resolve(ctx(explicit="yes"))
                scopes = {item["ref"]["id"]: item["scope"] for item in selected["selected"]}
                self.assertEqual(scopes["example.pack-grid"], "repo",
                                 "a repository binding to a pack pattern selects at repository scope")
        self.assertEqual(results[False], results[True], "including a pack catalog never promotes its bindings")
        self.assertEqual(results[True][:2], ("ready", "12"))
        self.assertEqual(results[True][2], [("pack.base", "pack"), ("repo.main", "repo")])

    def test_f5_personal_patterns_need_explicit_or_repository_authority(self):
        def setup(fx):
            fx.pack_chain()
            fx.publish(fx.packs / "base" / "patterns", "pack.base", [])
            personal = make_pattern("example.personal-rule")
            fx.publish(fx.personal_patterns, "me.personal", [personal])
            return personal

        fx = Fixture(self)
        personal = setup(fx)
        fx.publish(fx.packs / "base" / "patterns", "pack.base", [],
                   bindings=[binding("pp", [ref("me.personal", personal)])])
        report, _ = fx.resolve(ctx())
        self.assertEqual((report["status"], report["selected"]), ("unavailable", []))
        self.assertIn("personal_ref_refused", codes(report, "error"))
        fx = Fixture(self)
        personal = setup(fx)
        blueprint = make_pattern("example.blueprint", requirements=[], includes=[ref("me.personal", personal)])
        fx.publish(fx.packs / "base" / "patterns", "pack.base", [blueprint],
                   bindings=[binding("bp", [ref("pack.base", blueprint)])])
        self.assertIn("personal_ref_refused", codes(fx.resolve(ctx())[0], "error"),
                      "a pack-selected include cannot activate a personal pattern")
        fx = Fixture(self)
        personal = setup(fx)
        fx.repo_bindings([binding("mine", [ref("me.personal", personal)])])
        report, _ = fx.resolve(ctx())
        self.assertEqual((report["status"], report["selected"][0]["scope"]), ("ready", "repo"))
        fx.repo_bindings([])
        explicit = p.parse_refs([{"ref": ref("me.personal", personal), "role": "required", "approved_by": "me",
                                  "approval_ref": "task"}])
        self.assertEqual(fx.resolve(ctx(), refs=explicit)[0]["status"], "ready")

    def test_f6_asset_refs_and_verified_reads(self):
        fx = Fixture(self)
        guide, tokens = b"# Dashboard guide\n", b'{"grid": 12}\n'
        rules = make_pattern("example.visual", assets=[
            {"path": "assets/guide.md", "kind": "guide", "sha256": hashlib.sha256(guide).hexdigest(), "phases": ["build"]},
            {"path": "assets/tokens.json", "kind": "tokens", "sha256": hashlib.sha256(tokens).hexdigest(),
             "domains": ["dashboard"]},
            {"path": "assets/never.md", "kind": "guide", "sha256": "0" * 64, "phases": []}])
        fx.publish(fx.repo_patterns, "repo.main", [rules], bindings=[binding("b", [ref("repo.main", rules)])])
        folder = fx.repo_patterns / "example.visual" / "1.0.0" / "assets"
        folder.mkdir()
        (folder / "guide.md").write_bytes(guide)
        (folder / "tokens.json").write_bytes(tokens)
        report, reader = fx.resolve(ctx())
        self.assertEqual(reader.count("asset"), 0)
        self.assertEqual([item["path"] for item in p.asset_refs(report)], ["assets/guide.md", "assets/tokens.json"],
                         "a present empty filter matches nothing")
        self.assertEqual([item["path"] for item in p.asset_refs(report, kind="tokens", domain="dashboard")],
                         ["assets/tokens.json"])
        self.assertEqual([item["path"] for item in p.asset_refs(report, phase="review")], ["assets/tokens.json"])
        ref_guide = p.asset_refs(report, kind="guide", phase="build")[0]
        reader = p.Reader()
        self.assertEqual(p.read_asset(fx.roots(), ref_guide, phase="build", reader=reader), guide)
        self.assertEqual(reader.count("asset"), 1)
        with self.assertRaises(p.PatternError) as caught:
            p.read_asset(fx.roots(), ref_guide, phase="review")
        self.assertEqual(caught.exception.code, "asset_not_applicable")
        with self.assertRaises(p.PatternError) as caught:
            p.read_asset(fx.roots(), dict(ref_guide, path="assets/tokens.json"))
        self.assertEqual(caught.exception.code, "asset_not_declared")
        with self.assertRaises(p.PatternError):
            p.read_asset(fx.roots(), dict(ref_guide, path="../../catalog.json"))
        (folder / "guide.md").write_bytes(b"tampered\n")
        with self.assertRaises(p.PatternError) as caught:
            p.read_asset(fx.roots(), ref_guide, phase="build")
        self.assertEqual((caught.exception.code, caught.exception.status), ("asset_digest_mismatch", "unavailable"))
        lock = lock_of(report, p.parse_context(ctx()))
        self.assertEqual(lock["asset_pins"], p.asset_refs(report), "lock pins use the same stable shape")

    def test_f7_report_selection_digest_matches_lock(self):
        lf = LockFixture(self)
        report, _ = lf.fx.resolve(lf.context)
        self.assertRegex(report["selection_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(lock_of(report, p.parse_context(lf.context))["selection_digest"], report["selection_digest"])
        needs, _ = lf.fx.resolve(ctx())
        self.assertIsNone(needs["selection_digest"], "no digest for unresolved work")
        empty, _ = lf.fx.resolve(ctx(artifact="api"))
        self.assertEqual(empty["status"], "empty")
        self.assertRegex(empty["selection_digest"], r"^[0-9a-f]{64}$")
        refs = p.parse_refs([{"ref": ref("repo.main", lf.other), "role": "required", "approved_by": "me",
                              "approval_ref": "task"}])
        with_ref, _ = lf.fx.resolve(lf.context, refs=refs)
        self.assertNotEqual(with_ref["selection_digest"], report["selection_digest"])
        self.assertEqual(lock_of(with_ref, p.parse_context(lf.context), refs=refs)["selection_digest"],
                         with_ref["selection_digest"])
        with self.assertRaises(p.PatternError) as caught:
            lock_of(with_ref, p.parse_context(lf.context))
        self.assertEqual(caught.exception.code, "lock_refused", "refs omitted from the lock are detected")
        tampered = copy.deepcopy(report)
        tampered["requirements"][0]["text"] = "edited"
        with self.assertRaises(p.PatternError):
            lock_of(tampered, p.parse_context(lf.context))

    def test_advisories_input_profile_and_timestamps(self):
        fx = Fixture(self)
        envelope = fx.write_json("roots.json", fx.envelope())
        code, report, stderr = fx.cli("resolve", "--roots-file", envelope, "--context", fx.root / "missing.json")
        self.assertEqual((code, report["status"]), (2, "invalid"))
        self.assertIn("input_missing", stderr)
        bad = fx.write_json("profile.json", {"selection": {"mode": "neutral", "status": "loaded"},
                                             "values": {"name": "_default", "version": "1.0.0"}, "provenance": {},
                                             "ancestry": [{"name": "_default", "version": "1.0.0"}]})
        code, report, stderr = fx.cli("envelope", "--personal", fx.home, "--profile-record", bad)
        self.assertEqual((code, report["diagnostics"][0]["code"]), (2, "invalid_pack_context"))
        self.assertNotIn("Traceback", stderr)
        for digits in range(1, 7):
            stamp = "2026-09-01T00:00:00." + "5" * digits + "Z"
            self.assertEqual(p._instant(stamp).microsecond, int(("5" * digits).ljust(6, "0")))
        with self.assertRaises(p.PatternError):
            p._timestamp("2026-02-30T00:00:00Z", "t")
        source = Path(p.__file__).read_text(encoding="utf-8")
        self.assertNotIn("fromisoformat(core", source, "timestamp parsing must not depend on 3.11 fromisoformat")

    def test_positive_real_profile_context_record(self):
        """P3-5: a real stored ADR-0029 context record (with digest) converts and reaches the CLI."""
        fx = Fixture(self)
        profile = p._profile_module()
        packs = fx.root / "profile-packs"
        (packs / "base").mkdir(parents=True)
        (packs / "base" / "pack.yaml").write_text(
            "name: base\nversion: 1.0.0\nvoice:\n  default_tier: internal\ncompliance:\n  mode: advisory\n"
            "navigation:\n  default_workflow: cycle\npatterns:\n  source: patterns/catalog.json\n", encoding="utf-8")
        pointer = fx.home / "active-pack"
        pointer.write_text("base", encoding="utf-8")
        config = profile.ProfileConfig(ROOT, fx.repo, fx.home, packs, pointer, context_id="pattern-test")
        runtime = fx.home / "sessions"
        # Runs before the TemporaryDirectory cleanup: history paths can exceed MAX_PATH, as in
        # tests/integration/universal-profile-context.py, so remove them through the native spelling.
        self.addCleanup(lambda: shutil.rmtree(profile._native_io_path(runtime)) if runtime.exists() else None)
        record = profile.load_profile_context(config, create=True)
        self.assertEqual(set(record) >= {"digest", "profile", "context_id"}, True)
        context = p.pack_context_from_profile(record)
        self.assertEqual((context["status"], context["source"]["state"], context["ancestry"][-1]["pack"]),
                         ("resolved", "value", "base"))
        stored = fx.write_json("record.json", record)
        code, envelope, _ = fx.cli("envelope", "--personal", fx.home, "--repository", fx.repo, "--profile-record", stored)
        self.assertEqual((code, envelope["pack_context"]), (0, context))
        forged = dict(record, profile=dict(record["profile"], values=dict(record["profile"]["values"], version="9.9.9")))
        with self.assertRaises(p.PatternError) as caught:
            p.pack_context_from_profile(forged)
        self.assertEqual(caught.exception.code, "invalid_pack_context")


def _revoke_under_lock(root: Path, entry: dict) -> None:
    """A concurrent writer that honours the per-root lock (as every Lintel writer does)."""
    with p._WriteLock(root / "catalog.json"):
        value = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
        value.setdefault("revocations", []).append({**{k: entry[k] for k in ("id", "version", "sha256")},
                                                    "reason": "unsafe", "reference": "SEC-9", "at": TS})
        p._atomic_write(root / "catalog.json", p.emit_json(value).encode("utf-8"), replace=True)


class MilestoneReviewTests(unittest.TestCase):
    """Regressions for independent review of ae9d6df7 (P2-1, P3-1, P3-2)."""

    def _visual_lock(self):
        fx = Fixture(self)
        guide = b"# guide\n"
        shared = make_pattern("example.visual", assets=[{"path": "guide.md", "kind": "guide",
                                                         "sha256": hashlib.sha256(guide).hexdigest()}])
        pack_root = fx.pack_chain()
        fx.publish(pack_root / "patterns", "pack.base", [shared], bindings=[binding("p", [ref("pack.base", shared)])])
        fx.publish(fx.repo_patterns, "repo.main", [shared, make_pattern("example.unselected", assets=[
            {"path": "guide.md", "kind": "guide", "sha256": hashlib.sha256(guide).hexdigest()}])],
            bindings=[binding("r", [ref("repo.main", shared)])])
        for root in (pack_root / "patterns", fx.repo_patterns):
            (root / "example.visual" / "1.0.0" / "guide.md").write_bytes(guide)
        (fx.repo_patterns / "example.unselected" / "1.0.0" / "guide.md").write_bytes(guide)
        report, _ = fx.resolve(ctx())
        self.assertEqual(report["status"], "ready")
        return fx, report, lock_of(report, p.parse_context(ctx()))

    def test_p2_1_lock_edits_outside_the_old_digest_are_detected(self):
        fx, report, lock = self._visual_lock()
        self.assertEqual(len(p.asset_refs(lock)), 1)
        self.assertEqual(len(lock["selected"][0]["equivalent_refs"]), 2)

        def edited(change):
            value = copy.deepcopy(lock)
            change(value)
            return value

        forged_asset = {"path": "evil.md", "kind": "guide", "sha256": "e" * 64}
        edits = {
            "assets dropped": lambda v: v["selected"][0].update(assets=[]),
            "asset_pins dropped": lambda v: v.update(asset_pins=[]),
            "assets forged": lambda v: (v["selected"][0].update(assets=[forged_asset]),
                                        v.update(asset_pins=[dict(forged_asset, pattern=v["selected"][0]["ref"])])),
            "equivalents dropped": lambda v: v["selected"][0].update(equivalent_refs=[]),
            "reasons forged": lambda v: v["selected"][0].update(reasons=[{"kind": "binding", "binding": "forged"}]),
        }
        for name, change in edits.items():
            with self.subTest(name=name, digest="stale"):
                with self.assertRaises(p.PatternError) as caught:
                    p.parse_lock(edited(change))
                self.assertEqual((caught.exception.code, caught.exception.status), ("invalid_lock", "invalid"))
            with self.subTest(name=name, digest="recomputed by the forger"):
                value = edited(change)
                value["selection_digest"] = p.selection_digest(value)
                try:
                    p.parse_lock(value)
                except p.PatternError as error:
                    self.assertEqual(error.code, "invalid_lock")
                    continue
                try:
                    verified = p.verify_lock(fx.roots(), value, p.parse_context(ctx()), today=TODAY)
                except p.PatternError as error:
                    self.assertEqual((error.code, error.status), ("lock_content_mismatch", "invalid"))
                    continue
                self.assertEqual(verified["status"], "conflict")
                self.assertIn("selection_provenance_changed", codes(verified, "error"))
        self.assertEqual(p.verify_lock(fx.roots(), lock, p.parse_context(ctx()), today=TODAY)["status"], "ok")
        for field, value in (("equivalent_refs", []), ("assets", []), ("reasons", [{"kind": "explicit"}])):
            with self.subTest(report_field=field):
                tampered = copy.deepcopy(report)
                tampered["selected"][0][field] = value
                with self.assertRaises(p.PatternError) as caught:
                    lock_of(tampered, p.parse_context(ctx()))
                self.assertEqual(caught.exception.code, "lock_refused")

    def test_p2_1_real_provenance_change_is_a_replan(self):
        fx, _, lock = self._visual_lock()
        fx.publish(fx.packs / "base" / "patterns", "pack.base", [], bindings=[])
        report = p.verify_lock(fx.roots(), lock, p.parse_context(ctx()), today=TODAY)
        self.assertEqual(report["status"], "unavailable", "the pinned equivalent disappeared")
        fx, _, lock = self._visual_lock()
        visual = json.loads((fx.repo_patterns / "example.visual" / "1.0.0" / "pattern.json").read_text(encoding="utf-8"))
        fx.repo_bindings([binding("extra", [ref("repo.main", visual)])])
        report = p.verify_lock(fx.roots(), lock, p.parse_context(ctx()), today=TODAY)
        self.assertEqual(report["status"], "conflict")
        self.assertEqual(next(item for item in report["diagnostics"]
                              if item["code"] == "selection_provenance_changed")["fields"], ["reasons"])

    def test_p3_1_read_asset_bound_to_a_selection(self):
        fx, report, lock = self._visual_lock()
        selected_ref = p.asset_refs(lock)[0]
        self.assertEqual(p.read_asset(fx.roots(), selected_ref, selection=lock), b"# guide\n")
        self.assertEqual(p.read_asset(fx.roots(), selected_ref, selection=report, context=p.parse_context(ctx())),
                         b"# guide\n")
        with self.assertRaises(p.PatternError) as caught:
            p.read_asset(fx.roots(), selected_ref, selection=report)
        self.assertEqual(caught.exception.code, "selection_not_usable", "a report needs its in-process context")
        unselected = json.loads((fx.repo_patterns / "example.unselected" / "1.0.0" / "pattern.json")
                                .read_text(encoding="utf-8"))
        other = dict(selected_ref, pattern=ref("repo.main", unselected))
        self.assertEqual(p.read_asset(fx.roots(), other), b"# guide\n", "standalone inspection stays honest")
        with self.assertRaises(p.PatternError) as caught:
            p.read_asset(fx.roots(), other, selection=lock)
        self.assertEqual((caught.exception.code, caught.exception.status), ("asset_not_selected", "unavailable"))
        needs, _ = fx.resolve(ctx(), refs=p.parse_refs([{"ref": ref("repo.main", make_pattern(
            "example.scoped", applies_to={"target": ["prod"]})), "role": "required", "approved_by": "me",
            "approval_ref": "task"}]))
        with self.assertRaises(p.PatternError) as caught:
            p.read_asset(fx.roots(), selected_ref, selection=needs)
        self.assertEqual(caught.exception.code, "selection_not_usable")
        tampered = copy.deepcopy(lock)
        tampered["asset_pins"] = []
        with self.assertRaises(p.PatternError) as caught:
            p.read_asset(fx.roots(), selected_ref, selection=tampered)
        self.assertEqual(caught.exception.code, "invalid_lock")

    def _approve_setup(self):
        fx = Fixture(self)
        root = fx.repo_patterns
        child = draft("example.child")
        p.capture(fx.roots(), child, scope="repo", name=child["id"], source_id="team.repo")
        catalog = lambda: json.loads((root / "catalog.json").read_text(encoding="utf-8"))
        approved = p.approve(fx.roots(), root / "example.child" / "0.1.0" / "pattern.json", version="1.0.0",
                             approval_value=APPROVAL, expected_digest=p.content_digest(child))
        parent = draft("example.parent", requirements=[], includes=[approved["ref"]])
        p.capture(fx.roots(), parent, scope="repo", name=parent["id"], expected_catalog_digest=p.content_digest(catalog()))
        child_entry = next(item for item in catalog()["entries"] if item["id"] == "example.child" and
                           item["version"] == "1.0.0")
        return fx, root, parent, child_entry, catalog

    def test_p3_2_approve_never_blesses_a_concurrent_revocation(self):
        fx, root, parent, child_entry, catalog = self._approve_setup()
        original = p.load_sources
        writer = {"result": None}

        def racing_load_sources(*args, **kwargs):
            result = original(*args, **kwargs)
            if writer["result"] is None:
                try:
                    _revoke_under_lock(root, child_entry)
                    writer["result"] = "revoked"
                except p.PatternError as error:
                    writer["result"] = error.code
            return result

        p.load_sources = racing_load_sources
        self.addCleanup(setattr, p, "load_sources", original)
        try:
            outcome = p.approve(fx.roots(), root / "example.parent" / "0.1.0" / "pattern.json", version="1.0.0",
                                approval_value=APPROVAL, expected_digest=p.content_digest(parent))["written"]
        except p.PatternError as error:
            outcome = error.code
        p.load_sources = original
        revoked = any(item["id"] == "example.child" for item in catalog().get("revocations", []))
        approved_parent = any(item["id"] == "example.parent" and item["status"] == "approved"
                              for item in catalog()["entries"])
        self.assertFalse(revoked and approved_parent,
                         f"approval blessed a concurrently revoked dependency (writer={writer['result']}, "
                         f"approve={outcome})")
        self.assertEqual(writer["result"], "write_locked", "dependency checks run inside the owned lock")
        self.assertTrue(approved_parent)

    def test_p3_2_revocation_before_approval_blocks_and_catalog_cas(self):
        fx, root, parent, child_entry, catalog = self._approve_setup()
        _revoke_under_lock(root, child_entry)
        path = root / "example.parent" / "0.1.0" / "pattern.json"
        before = tree_digest(root)
        with self.assertRaises(p.PatternError) as caught:
            p.approve(fx.roots(), path, version="1.0.0", approval_value=APPROVAL, expected_digest=p.content_digest(parent))
        self.assertEqual((caught.exception.code, caught.exception.status), ("dependency_not_approved", "unavailable"))
        self.assertEqual(tree_digest(root), before)
        fx, root, parent, _, catalog = self._approve_setup()
        path = root / "example.parent" / "0.1.0" / "pattern.json"
        with self.assertRaises(p.PatternError) as caught:
            p.approve(fx.roots(), path, version="1.0.0", approval_value=APPROVAL,
                      expected_digest=p.content_digest(parent), expected_catalog_digest="0" * 64)
        self.assertEqual((caught.exception.code, caught.exception.status), ("stale_catalog_digest", "collision"))
        report = p.approve(fx.roots(), path, version="1.0.0", approval_value=APPROVAL,
                           expected_digest=p.content_digest(parent), expected_catalog_digest=p.content_digest(catalog()))
        self.assertTrue(report["written"])


class ResealedLockTests(unittest.TestCase):
    """Regressions for independent review of f1918e12 (P2-R3-1, P3-R3-1..3): resealed forgeries."""

    def setUp(self):
        self.fx = Fixture(self)
        guide = b"# guide\n"
        asset = [{"path": "guide.md", "kind": "guide", "sha256": hashlib.sha256(guide).hexdigest()}]
        self.rules = make_pattern("example.rules", requirements=[clause("MUST-1", "must", "ui.theme", "dark"),
                                                                 clause("DEF-1", "default", "ui.density", "compact")],
                                  assets=asset)
        self.other = make_pattern("example.other", applies_to={"artifact": ["api"]}, assets=asset)
        self.soft = make_pattern("example.soft", requirements=[clause("S-1", "default", "ui.font", "serif")])
        self.fx.publish(self.fx.repo_patterns, "repo.main", [self.rules, self.other, self.soft])
        for pattern in ("example.rules", "example.other"):
            (self.fx.repo_patterns / pattern / "1.0.0" / "guide.md").write_bytes(guide)
        self.fx.repo_bindings([binding("req", [ref("repo.main", self.rules)], when={"artifact": ["dashboard"]})])
        self.context = p.parse_context(ctx(artifact="dashboard"))
        report, _ = self.fx.resolve(ctx(artifact="dashboard"))
        self.report = report
        self.lock = lock_of(report, self.context)

    def verify(self, lock):
        return p.verify_lock(self.fx.roots(), lock, self.context, today=TODAY)

    def reseal(self, change):
        forged = copy.deepcopy(self.lock)
        change(forged)
        forged["asset_pins"] = p.asset_refs(forged)
        forged["status"] = "ready" if forged["selected"] else "empty"
        forged["selection_digest"] = p.selection_digest(forged)
        return forged

    def assert_rejected(self, forged, *codes_expected):
        try:
            report = self.verify(forged)
        except p.PatternError as error:
            self.assertEqual(error.status, "invalid")
            return
        self.assertEqual(report["status"], "conflict", report["diagnostics"])
        self.assertTrue(set(codes_expected) & set(codes(report, "error")), codes(report, "error"))

    def test_genuine_lock_verifies(self):
        self.assertEqual(self.verify(self.lock)["status"], "ok")

    def test_added_selected_record_is_a_conflict_and_cannot_unlock_assets(self):
        api_report, _ = self.fx.resolve(ctx(artifact="api"), refs=p.parse_refs([{"ref": ref("repo.main", self.other),
            "role": "default", "approved_by": "me", "approval_ref": "task"}]))
        grafted = api_report["selected"][0]
        forged = self.reseal(lambda value: value["selected"].append(grafted))
        self.assert_rejected(forged, "selection_changed")
        other_asset = next(item for item in p.asset_refs(forged) if item["pattern"]["id"] == "example.other")
        with self.assertRaises(p.PatternError) as caught:
            p.read_asset(self.fx.roots(), other_asset, selection=self.lock)
        self.assertEqual(caught.exception.code, "asset_not_selected")

    def test_removed_record_edited_text_state_and_status_are_rejected(self):
        cases = {
            "remove only record": (lambda v: (v["selected"].clear(), v["requirements"].clear(), v["settings"].clear()),
                                   ("selection_changed", "requirement_changed", "mandatory_baseline_changed")),
            "edit must text": (lambda v: next(i for i in v["requirements"] if i["clause"].endswith("MUST-1"))
                               .update(text="weakened"), ("requirement_changed",)),
            "must to waived": (lambda v: next(i for i in v["requirements"] if i["clause"].endswith("MUST-1"))
                               .update(state="waived"), ("requirement_changed",)),
            "edit verify": (lambda v: v["requirements"][0].update(verify="trust me"), ("requirement_changed",)),
            "edit setting": (lambda v: v["settings"]["ui.theme"].update(value="light"), ("setting_changed",)),
            "effective status": (lambda v: v["selected"][0].update(effective_status="deprecated"),
                                 ("selection_provenance_changed",)),
            "drop default clause": (lambda v: v["requirements"].remove(
                next(i for i in v["requirements"] if i["clause"].endswith("DEF-1"))), ("requirement_changed",)),
        }
        for name, (change, expected) in cases.items():
            with self.subTest(name=name):
                self.assert_rejected(self.reseal(change), *expected)

    def test_legitimate_later_changes_keep_their_documented_outcomes(self):
        self.fx.repo_bindings([binding("req", [ref("repo.main", self.rules)], when={"artifact": ["dashboard"]}),
                               binding("soft", [ref("repo.main", self.soft)], role="default")])
        report = self.verify(self.lock)
        self.assertEqual(report["status"], "conflict", "R5: an added default binding changes the baseline; re-plan")
        self.assertIn("selection_changed", codes(report, "error"))
        self.fx.repo_bindings([binding("req", [ref("repo.main", self.rules)], when={"artifact": ["dashboard"]})])
        self.assertEqual(self.verify(self.lock)["status"], "ok")
        unrelated = make_pattern("example.unrelated", applies_to={"artifact": ["api"]})
        catalog = self.fx.publish(self.fx.repo_patterns, "repo.main", [self.rules, self.other, self.soft, unrelated])
        self.assertEqual(self.verify(self.lock)["status"], "ok", "an unbound catalog addition leaves the pin valid")
        entry = next(item for item in catalog["entries"] if item["id"] == "example.rules")
        self.fx.publish(self.fx.repo_patterns, "repo.main", [self.rules, self.other, self.soft, unrelated], lifecycle=[
            {**{k: entry[k] for k in ("id", "version", "sha256")}, "status": "deprecated", "reason": "r",
             "reference": "ADR", "at": TS}])
        report = self.verify(self.lock)
        self.assertEqual(report["status"], "ok", "deprecation after locking warns, never conflicts")
        self.assertIn("pinned_deprecated", codes(report, "warning"))
        self.assertEqual(report["checked"][0]["effective_status"], "deprecated", "checked[] reports the current status")

    def test_waived_lock_and_empty_lock_still_verify(self):
        exception = p.parse_exceptions({"schema_version": 1, "items": [{
            "clause": "example.rules@1.0.0#MUST-1", "context_digest": self.context.digest, "reason": "pilot",
            "approval_ref": "EX-1", "approved_by": "security", "expires": "2026-12-31", "verification": "manual"}]})
        report, _ = self.fx.resolve(ctx(artifact="dashboard"), exceptions=exception)
        lock = lock_of(report, self.context)
        verified = p.verify_lock(self.fx.roots(), lock, self.context, today=TODAY)
        self.assertEqual(verified["status"], "ok", "a genuine exception keeps its waiver")
        empty_report, _ = self.fx.resolve(ctx(artifact="none"))
        empty_context = p.parse_context(ctx(artifact="none"))
        empty = lock_of(empty_report, empty_context)
        self.assertEqual((empty["status"], p.verify_lock(self.fx.roots(), empty, empty_context, today=TODAY)["status"]),
                         ("empty", "ok"))

    def test_status_and_budget_are_bound(self):
        wrong_status = copy.deepcopy(self.lock)
        wrong_status["status"] = "empty"
        with self.assertRaises(p.PatternError) as caught:
            p.parse_lock(wrong_status)
        self.assertEqual(caught.exception.code, "invalid_lock")
        for budget in (1_000_000, 50):
            with self.subTest(budget=budget):
                edited = copy.deepcopy(self.lock)
                edited["context_budget"] = budget
                with self.assertRaises(p.PatternError) as caught:
                    p.parse_lock(edited)
                self.assertIn("selection_digest", caught.exception.message)
        with self.assertRaises(p.PatternError) as caught:
            lock_of(self.report, self.context, context_budget=40000)
        self.assertEqual(caught.exception.code, "lock_refused")

    def test_edited_report_selection_is_refused_by_the_shared_digest(self):
        asset = p.asset_refs(self.report)[0]
        self.assertEqual(p.read_asset(self.fx.roots(), asset, selection=self.report, context=self.context), b"# guide\n")
        edited = copy.deepcopy(self.report)
        other = json.loads((self.fx.repo_patterns / "example.other" / "1.0.0" / "pattern.json").read_text(encoding="utf-8"))
        edited["selected"][0]["assets"] = [dict(asset_item) for asset_item in edited["selected"][0]["assets"]]
        forged_ref = dict(asset, pattern=ref("repo.main", other))
        edited["selected"].append(dict(copy.deepcopy(edited["selected"][0]), ref=ref("repo.main", other),
                                       equivalent_refs=[ref("repo.main", other)]))
        with self.assertRaises(p.PatternError) as caught:
            p.read_asset(self.fx.roots(), forged_ref, selection=edited, context=self.context)
        self.assertEqual(caught.exception.code, "selection_not_usable")
        with self.assertRaises(p.PatternError) as caught:
            p.read_asset(self.fx.roots(), asset, selection=self.report, context=p.parse_context(ctx(artifact="x")))
        self.assertEqual(caught.exception.code, "selection_not_usable")

    def test_projection_still_works_on_a_verified_lock(self):
        lock_path = self.fx.repo / "plan.lock.json"
        p.write_lock(self.fx.roots(), lock_path, self.lock)
        task_map = {"schema_version": 1, "selection_digest": self.lock["selection_digest"], "tasks": ["T1"],
                    "packages": [{"id": "P1", "tasks": ["T1"]}],
                    "clauses": [{"clause": "example.rules@1.0.0#MUST-1", "tasks": ["T1"]},
                                {"clause": "example.rules@1.0.0#DEF-1", "tasks": ["T1"]}]}
        p.map_lock(self.fx.roots(), lock_path, task_map, expected_lock_digest=p.content_digest(self.lock), write=True)
        mapped = json.loads(lock_path.read_text(encoding="utf-8"))
        self.assertEqual(self.verify(mapped)["status"], "ok")
        self.assertEqual(len(p.project_package(mapped, task_map, "P1")["clauses"]), 2)


class MaintenanceTests(unittest.TestCase):
    """V07 (cards 3.2.a-3.2.c): update, lifecycle events, bindings, attestations and removal."""

    def setUp(self):
        self.fx = Fixture(self)
        self.root = self.fx.repo_patterns
        self.child = make_pattern("example.child", requirements=[clause("C-1", "must")])
        self.parent = make_pattern("example.parent", requirements=[clause("P-1", "must", "ui.theme", "dark")],
                                   includes=[ref("repo.main", self.child)])
        self.unused = make_pattern("example.unused")
        self.fx.publish(self.root, "repo.main", [self.child, self.parent, self.unused])
        self.fx.repo_bindings([binding("req", [ref("repo.main", self.parent)])])

    def digest(self):
        return p.content_digest(json.loads((self.root / "catalog.json").read_text(encoding="utf-8")))

    def lock_at(self, name="demo"):
        report, _ = self.fx.resolve(ctx())
        lock = lock_of(report, p.parse_context(ctx()))
        path = self.fx.repo / ".claude" / "plans" / name / "patterns.lock.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        p.write_lock(self.fx.roots(), path, lock)
        return lock, path

    def test_update_previews_diff_and_impact_then_publishes_a_new_draft(self):
        self.lock_at()
        path = self.root / "example.child" / "1.0.0" / "pattern.json"
        newer = dict(copy.deepcopy(self.child), version="1.1.0", status="draft",
                     requirements=[clause("C-1", "must", text="stricter"), clause("C-2", "default")])
        newer.pop("approval")
        preview = p.update(self.fx.roots(), path, newer, expected_digest=p.content_digest(self.child))
        self.assertEqual((preview["written"], preview["clause_diff"]["added"], preview["clause_diff"]["changed"]),
                         (False, ["C-2"], ["C-1"]))
        self.assertEqual([item["pattern"]["id"] for item in preview["impact"]["includes"]], ["example.parent"])
        self.assertEqual([item["lock"] for item in preview["impact"]["locks"]], [".claude/plans/demo/patterns.lock.json"])
        self.assertIn("cannot prove", preview["impact"]["inventory_scope"])
        before = path.read_bytes()
        written = p.update(self.fx.roots(), path, newer, expected_digest=p.content_digest(self.child), write=True)
        self.assertEqual(written["published"][0]["version"], "1.1.0")
        self.assertEqual(path.read_bytes(), before, "the old version is intact")
        self.assertEqual(self.fx.resolve(ctx())[0]["status"], "ready", "current pins are unchanged by an update")
        for change, code in (({"version": "1.0.0"}, "version_not_newer"), ({"id": "example.other"}, "update_id_mismatch"),
                             ({"status": "approved", "approval": APPROVAL}, "update_not_draft")):
            with self.subTest(code=code):
                with self.assertRaises(p.PatternError) as caught:
                    p.update(self.fx.roots(), path, {**newer, "version": "1.2.0", **change},
                             expected_digest=p.content_digest(self.child))
                self.assertEqual(caught.exception.code, code)
        with self.assertRaises(p.PatternError) as caught:
            p.update(self.fx.roots(), path, dict(newer, version="1.2.0"), expected_digest="0" * 64)
        self.assertEqual(caught.exception.code, "stale_pattern_digest")

    def test_lifecycle_events_preview_record_and_monotonic_rules(self):
        lock, _ = self.lock_at()
        record = {"reason": "superseded", "reference": "ADR-9", "at": "2026-09-10T00:00:00Z"}
        preview = p.record_lifecycle(self.fx.roots(), "repo.main:example.child@1.0.0", action="deprecate",
                                     record_value=record, expected_catalog_digest=self.digest())
        self.assertEqual((preview["written"], preview["effective_status"]), (False, {"before": "approved",
                                                                                     "after": "deprecated"}))
        self.assertEqual(preview["impact"]["locks"][0]["pins"], ["example.child@1.0.0"])
        before = self.digest()
        with self.assertRaises(p.PatternError) as caught:
            p.record_lifecycle(self.fx.roots(), "repo.main:example.child@1.0.0", action="deprecate",
                               record_value=record, expected_catalog_digest=None, write=True)
        self.assertEqual(caught.exception.code, "expected_digest_required")
        p.record_lifecycle(self.fx.roots(), "repo.main:example.child@1.0.0", action="deprecate", record_value=record,
                           expected_catalog_digest=before, write=True)
        self.assertIn("pinned_deprecated", codes(p.verify_lock(self.fx.roots(), lock, p.parse_context(ctx()),
                                                                today=TODAY), "warning"))
        with self.assertRaises(p.PatternError) as caught:
            p.record_lifecycle(self.fx.roots(), "repo.main:example.child@1.0.0", action="retire",
                               record_value=dict(record, at="2026-09-09T00:00:00Z"),
                               expected_catalog_digest=self.digest(), write=True)
        self.assertEqual(caught.exception.code, "event_not_monotonic")
        p.record_lifecycle(self.fx.roots(), "repo.main:example.child@1.0.0", action="revoke",
                           record_value=dict(record, at="2026-09-11T00:00:00Z"),
                           expected_catalog_digest=self.digest(), write=True)
        verified = p.verify_lock(self.fx.roots(), lock, p.parse_context(ctx()), today=TODAY)
        self.assertEqual((verified["status"], codes(verified, "error")), ("unavailable", ["pinned_revoked"]))
        with self.assertRaises(p.PatternError) as caught:
            p.record_lifecycle(self.fx.roots(), "repo.main:example.child@1.0.0", action="revoke",
                               record_value=dict(record, at="2026-09-12T00:00:00Z"),
                               expected_catalog_digest=self.digest(), write=True)
        self.assertEqual(caught.exception.code, "already_revoked")
        with self.assertRaises(p.PatternError):
            p.record_lifecycle(self.fx.roots(), "repo.main:example.unused@1.0.0", action="revoke",
                               record_value=dict(record, replaced_by=ref("repo.main", self.child)),
                               expected_catalog_digest=self.digest())

    def test_pack_sources_are_read_only(self):
        pack_root = self.fx.pack_chain()
        pack_rule = make_pattern("example.pack-rule")
        self.fx.publish(pack_root / "patterns", "team.patterns", [pack_rule])
        with self.assertRaises(p.PatternError) as caught:
            p.record_lifecycle(self.fx.roots(), "team.patterns:example.pack-rule@1.0.0", action="deprecate",
                               record_value={"reason": "r", "reference": "x", "at": TS}, expected_catalog_digest=None)
        self.assertEqual(caught.exception.code, "read_only_source")

    def test_apply_add_replace_remove_with_reduced_baseline(self):
        bindings = self.root / "bindings.json"
        current = lambda: p.content_digest(json.loads(bindings.read_text(encoding="utf-8")))
        change = {"schema_version": 1, "operation": "add", "id": "extra",
                  "binding": binding("extra", [ref("repo.main", self.unused)]), "reason": "team decision",
                  "approved_by": "lead", "approval_ref": "DEC-7"}
        preview = p.apply_change(self.fx.roots(), change)
        self.assertEqual((preview["written"], preview["required_clauses"]["added"]), (False, ["example.unused@1.0.0#R-1"]))
        with self.assertRaises(p.PatternError) as caught:
            p.apply_change(self.fx.roots(), change, write=True)
        self.assertEqual(caught.exception.code, "expected_digest_required")
        p.apply_change(self.fx.roots(), change, expected_digest=current(), write=True)
        with self.assertRaises(p.PatternError) as caught:
            p.apply_change(self.fx.roots(), change, expected_digest=current(), write=True)
        self.assertEqual(caught.exception.code, "binding_exists")
        removal = dict(change, operation="remove", id="req", binding=None)
        preview = p.apply_change(self.fx.roots(), removal)
        self.assertEqual(preview["required_clauses"]["reduced"],
                         ["example.child@1.0.0#C-1", "example.parent@1.0.0#P-1"])
        self.assertIn("mandatory_baseline_reduced", codes(preview, "warning"))
        before = bindings.read_bytes()
        with self.assertRaises(p.PatternError) as caught:
            p.apply_change(self.fx.roots(), removal, expected_digest="0" * 64, write=True)
        self.assertEqual(caught.exception.code, "stale_bindings_digest")
        self.assertIn("bindings", caught.exception.message)
        self.assertEqual(bindings.read_bytes(), before)
        for bad, code in ((dict(removal, id="nope"), "binding_missing"),
                          (dict(change, operation="replace", id="extra", binding=binding("other", [ref("repo.main", self.unused)])),
                           "invalid_schema"),
                          (dict(removal, binding=binding("req", [ref("repo.main", self.unused)])), "invalid_schema"),
                          (dict(change, reason=""), "invalid_schema")):
            with self.subTest(code=code):
                with self.assertRaises(p.PatternError) as caught:
                    p.apply_change(self.fx.roots(), bad)
                self.assertEqual(caught.exception.code, code)
        replaced = p.apply_change(self.fx.roots(), dict(change, operation="replace", binding=dict(
            binding("extra", [ref("repo.main", self.unused)]), role="default")), expected_digest=current(), write=True)
        self.assertEqual(replaced["required_clauses"]["reduced"], ["example.unused@1.0.0#R-1"])

    def _attested(self, source, **extra):
        pattern = make_pattern("example.attested", sources=[source], **extra)
        self.fx.publish(self.root, "repo.main", [self.child, self.parent, self.unused, pattern])
        self.fx.repo_bindings([binding("att", [ref("repo.main", pattern)])])
        return pattern

    def attestation(self, pattern, source_digest, **change):
        item = {"ref": ref("repo.main", pattern), "source_index": 0, "source_ref": pattern["sources"][0]["ref"],
                "source_digest": source_digest, "reviewed_by": "reviewer", "review_ref": "REV-1",
                "reviewed_at": "2026-09-20T00:00:00Z", "valid_until": "2026-12-31", "purpose": "both"}
        item.update(change)
        return p.parse_attestations({"schema_version": 1, "items": [item]})

    def test_url_and_overdue_sources_need_valid_attestations(self):
        url = dict(statement(), root="external", kind="approved-standard", ref="https://standards.example/doc")
        pattern = self._attested(url)
        self.assertIn("source_attestation_required", codes(self.fx.resolve(ctx())[0], "error"))
        report, _ = self.fx.resolve(ctx(), attestations=self.attestation(pattern, "a" * 64))
        self.assertEqual(report["status"], "ready")
        self.assertEqual(len(report["source_attestations"]), 1)
        for change, reason in (({"valid_until": "2026-09-01"}, "expired"),
                               ({"reviewed_at": "2026-10-01T00:00:00Z"}, "future"),
                               ({"source_ref": "https://other.example"}, "source_ref"),
                               ({"purpose": "freshness"}, None)):
            with self.subTest(change=change):
                report, _ = self.fx.resolve(ctx(), attestations=self.attestation(pattern, "a" * 64, **change))
                self.assertEqual(report["status"], "unavailable")
                if reason:
                    self.assertIn(reason, next(item["message"] for item in report["diagnostics"]
                                               if item["code"] == "attestation_rejected"))
        wrong_digest_ref = self.attestation(pattern, "a" * 64, ref=dict(ref("repo.main", pattern), sha256="b" * 64))
        self.assertEqual(self.fx.resolve(ctx(), attestations=wrong_digest_ref)[0]["status"], "unavailable",
                         "an attestation for other content does not count")

    def test_overdue_statement_and_local_file_sources(self):
        text = "The operator stated this expectation."
        pattern = self._attested(statement(text), review_after="2026-06-01")
        self.assertIn("review_overdue", codes(self.fx.resolve(ctx())[0], "error"))
        good = hashlib.sha256(text.encode("utf-8")).hexdigest()
        self.assertEqual(self.fx.resolve(ctx(), attestations=self.attestation(pattern, good))[0]["status"], "ready")
        self.assertEqual(self.fx.resolve(ctx(), attestations=self.attestation(pattern, "c" * 64))[0]["status"],
                         "unavailable", "a statement digest must hash the statement text")
        old_review = self.attestation(pattern, good, reviewed_at="2026-05-01T00:00:00Z")
        self.assertIn("review_overdue", codes(self.fx.resolve(ctx(), attestations=old_review)[0], "error"),
                      "freshness needs a review on or after review_after")
        doc = self.fx.repo / "docs" / "standard.md"
        doc.parent.mkdir()
        doc.write_bytes(b"standard v1\n")
        local = dict(statement(), root="repository", kind="approved-standard", ref="docs/standard.md")
        pattern = self._attested(local, review_after="2026-06-01")
        attested = self.attestation(pattern, hashlib.sha256(b"standard v1\n").hexdigest())
        self.assertEqual(self.fx.resolve(ctx(), attestations=attested)[0]["status"], "ready")
        doc.write_bytes(b"standard v2\n")
        report, _ = self.fx.resolve(ctx(), attestations=attested)
        self.assertEqual(report["status"], "unavailable", "changed local bytes need recapture, not re-attestation")

    def test_attestation_renewal_preserves_selection_digest(self):
        url = dict(statement(), root="external", kind="approved-standard", ref="https://standards.example/doc")
        pattern = self._attested(url)
        first = self.attestation(pattern, "a" * 64, valid_until="2026-10-31")
        report, _ = self.fx.resolve(ctx(), attestations=first)
        lock = lock_of(report, p.parse_context(ctx()))
        path = self.fx.repo / ".claude" / "plans" / "att" / "patterns.lock.json"
        path.parent.mkdir(parents=True)
        p.write_lock(self.fx.roots(), path, lock)
        self.assertEqual(p.verify_lock(self.fx.roots(), lock, p.parse_context(ctx()), today=TODAY)["status"], "ok",
                         "saved attestations are used when none are supplied")
        later = dt.date(2026, 11, 15)
        self.assertEqual(p.verify_lock(self.fx.roots(), lock, p.parse_context(ctx()), today=later)["status"],
                         "unavailable", "an expired saved attestation blocks continuation")
        renewal = self.attestation(pattern, "a" * 64, reviewed_at="2026-09-27T00:00:00Z", valid_until="2027-06-30")
        written = p.record_attestations(self.fx.roots(), path, renewal, p.parse_context(ctx()),
                                        expected_lock_digest=p.content_digest(lock), today=TODAY)
        renewed = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual((written["written"], renewed["selection_digest"]), (True, lock["selection_digest"]))
        self.assertEqual(renewed["source_attestations"][0]["valid_until"], "2027-06-30")
        self.assertEqual(p.verify_lock(self.fx.roots(), renewed, p.parse_context(ctx()), today=later)["status"], "ok")

    def test_remove_refuses_referenced_or_historic_entries_and_keeps_files(self):
        self.lock_at()
        for target in ("example.child", "example.parent"):
            with self.subTest(target=target):
                preview = p.remove(self.fx.roots(), f"repo.main:{target}@1.0.0", expected_catalog_digest=self.digest())
                self.assertFalse(preview["removable"])
                with self.assertRaises(p.PatternError) as caught:
                    p.remove(self.fx.roots(), f"repo.main:{target}@1.0.0", expected_catalog_digest=self.digest(),
                             write=True)
                self.assertEqual((caught.exception.code, caught.exception.status), ("remove_refused", "conflict"))
        preview = p.remove(self.fx.roots(), "repo.main:example.unused@1.0.0", expected_catalog_digest=self.digest())
        self.assertTrue(preview["removable"])
        self.assertIn("external_consumers_unknown", codes(preview, "warning"))
        path = self.root / "example.unused" / "1.0.0" / "pattern.json"
        p.remove(self.fx.roots(), "repo.main:example.unused@1.0.0", expected_catalog_digest=self.digest(), write=True)
        self.assertTrue(path.is_file(), "no file or history is deleted")
        self.assertNotIn("example.unused", [item["id"] for item in p.list_catalogs(self.fx.roots())["entries"]])
        p.index_source(self.fx.roots(), self.root, expected_catalog_digest=self.digest())
        self.assertNotIn("example.unused", [item["id"] for item in p.list_catalogs(self.fx.roots())["entries"]],
                         "remove->index stays removed")

    def test_lock_scan_is_bounded_to_the_repository_plan_root(self):
        self.lock_at()
        outside = self.fx.root / "other-repo" / ".claude" / "plans" / "x"
        outside.mkdir(parents=True)
        (outside / "patterns.lock.json").write_text("{}", encoding="utf-8")
        (self.fx.repo / ".claude" / "plans" / "broken.lock.json").write_text("{", encoding="utf-8")
        impact = p.dependents(self.fx.roots(), [p.parse_exact_ref(ref("repo.main", self.child), "t")])
        self.assertEqual([item["lock"] for item in impact["locks"]], [".claude/plans/demo/patterns.lock.json"])
        self.assertEqual([item["path"] for item in impact["unreadable_locks"]], [".claude/plans/broken.lock.json"])

    def test_cli_lifecycle_apply_remove(self):
        envelope = self.fx.write_json("roots.json", self.fx.envelope())
        record = self.fx.write_json("record.json", {"reason": "r", "reference": "ADR", "at": TS})
        code, report, _ = self.fx.cli("deprecate", "--roots-file", envelope, "--ref", "repo.main:example.unused@1.0.0",
                                      "--record", record)
        self.assertEqual((code, report["written"]), (0, False))
        code, report, _ = self.fx.cli("deprecate", "--roots-file", envelope, "--ref", "repo.main:example.unused@1.0.0",
                                      "--record", record, "--expected-catalog-digest", self.digest(), "--write")
        self.assertEqual((code, report["written"]), (0, True))
        code, report, _ = self.fx.cli("remove", "--roots-file", envelope, "--ref", "repo.main:example.child@1.0.0",
                                      "--expected-catalog-digest", self.digest(), "--write")
        self.assertEqual(code, 4)
        change = self.fx.write_json("change.json", {"schema_version": 1, "operation": "remove", "id": "req",
                                                    "binding": None, "reason": "r", "approved_by": "a",
                                                    "approval_ref": "b"})
        code, report, _ = self.fx.cli("apply", "--roots-file", envelope, "--change", change)
        self.assertEqual((code, report["written"]), (0, False))


class BundleTests(unittest.TestCase):
    """V08 (cards 3.3.a-3.3.b): exact closure export, whole-bundle import preflight and transformation."""

    def setUp(self):
        self.fx = Fixture(self)
        self.guide = b"# guide\n"
        self.child = make_pattern("example.child", assets=[{"path": "guide.md", "kind": "guide",
                                                            "sha256": hashlib.sha256(self.guide).hexdigest()}],
                                  sources=[dict(statement(), root="repository", ref="docs/private-policy.md")])
        self.parent = make_pattern("example.parent", requirements=[], includes=[ref("team.src", self.child)])
        self.fx.publish(self.fx.personal_patterns, "team.src", [self.child, self.parent])
        (self.fx.personal_patterns / "example.child" / "1.0.0" / "guide.md").write_bytes(self.guide)
        self.out = self.fx.root / "exports" / "bundle-1"
        self.out.parent.mkdir()

    def export(self, refs=None):
        return p.export_bundle(self.fx.roots(), refs or [p.parse_exact_ref(ref("team.src", self.parent), "r")], self.out)

    def version_map(self):
        return [{"original": ref("team.src", self.child), "id": "local.child", "version": "0.1.0"},
                {"original": ref("team.src", self.parent), "id": "local.parent", "version": "0.1.0"}]

    def test_export_writes_exact_closure_without_catalogs_or_absolute_roots(self):
        report = self.export()
        self.assertEqual(sorted(item["id"] for item in report["patterns"]), ["example.child", "example.parent"])
        files = sorted(path.relative_to(self.out).as_posix() for path in self.out.rglob("*") if path.is_file())
        self.assertEqual(files, ["bundle.json", "patterns/team.src/example.child/1.0.0/guide.md",
                                 "patterns/team.src/example.child/1.0.0/pattern.json",
                                 "patterns/team.src/example.parent/1.0.0/pattern.json"])
        blob = b"".join(path.read_bytes() for path in self.out.rglob("*") if path.is_file())
        for root in (self.fx.home, self.fx.repo, self.fx.root):
            self.assertNotIn(root.as_posix().encode(), blob)
        self.assertNotIn(b"catalog", b"".join(path.name.encode() for path in self.out.rglob("*")))
        with self.assertRaises(p.PatternError) as caught:
            self.export()
        self.assertEqual(caught.exception.code, "destination_exists")
        self.assertEqual(sorted(path.name for path in self.out.parent.iterdir()), ["bundle-1"], "no staging residue")

    def test_export_refuses_revoked_members(self):
        catalog = json.loads((self.fx.personal_patterns / "catalog.json").read_text(encoding="utf-8"))
        entry = next(item for item in catalog["entries"] if item["id"] == "example.child")
        catalog["revocations"] = [{**{k: entry[k] for k in ("id", "version", "sha256")}, "reason": "r",
                                   "reference": "S", "at": TS}]
        (self.fx.personal_patterns / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
        with self.assertRaises(p.PatternError) as caught:
            self.export()
        self.assertEqual(caught.exception.code, "pattern_revoked")
        self.assertFalse(self.out.exists())

    def test_import_preview_then_children_first_drafts_with_inert_provenance(self):
        self.export()
        roots = self.fx.roots()
        preview = p.import_bundle(roots, self.out, scope="repo", destination_source="repo.local",
                                  version_map_value=self.version_map())
        self.assertEqual((preview["written"], [item["destination"]["id"] for item in preview["mapping"]]),
                         (False, ["local.child", "local.parent"]))
        self.assertFalse((self.fx.repo_patterns / "catalog.json").exists())
        written = p.import_bundle(roots, self.out, scope="repo", destination_source="repo.local",
                                  version_map_value=self.version_map(), write=True)
        parent = json.loads((self.fx.repo_patterns / "local.parent" / "0.1.0" / "pattern.json").read_text(encoding="utf-8"))
        child_ref = next(item["destination"] for item in written["mapping"] if item["destination"]["id"] == "local.child")
        self.assertEqual((parent["status"], "approval" in parent, parent["includes"]), ("draft", False, [child_ref]))
        provenance = parent["extensions"]["lintel.imported"]
        self.assertEqual((provenance["original"]["id"], provenance["publication_status"], provenance["lifecycle_status"]),
                         ("example.parent", "approved", "approved"))
        self.assertEqual((self.fx.repo_patterns / "local.child" / "0.1.0" / "guide.md").read_bytes(), self.guide)
        self.assertEqual(p.check_sources(roots)["status"], "ok")
        self.fx.repo_bindings([binding("b", [child_ref])])
        self.assertIn("draft_not_eligible", codes(self.fx.resolve(ctx())[0], "error"), "import does not import trust")
        approved = p.approve(roots, self.fx.repo_patterns / "local.child" / "0.1.0" / "pattern.json", version="1.0.0",
                             approval_value=APPROVAL, expected_digest=child_ref["sha256"])
        self.assertEqual(approved["ref"]["id"], "local.child", "local approval is children-first")

    def test_import_rejects_hostile_or_incomplete_bundles_without_writing(self):
        self.export()
        roots = self.fx.roots()
        manifest_path = self.out / "bundle.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        def attempt(expected_code, version_map=None, **kwargs):
            with self.assertRaises(p.PatternError) as caught:
                p.import_bundle(roots, self.out, scope="repo", destination_source=kwargs.get("source", "repo.local"),
                                version_map_value=version_map or self.version_map(), write=True)
            self.assertEqual(caught.exception.code, expected_code)
            self.assertFalse((self.fx.repo_patterns / "catalog.json").exists())

        stray = self.out / "patterns" / "extra.sh"
        stray.write_text("rm -rf /\n", encoding="utf-8")
        attempt("invalid_bundle")
        stray.unlink()
        guide = self.out / "patterns/team.src/example.child/1.0.0/guide.md"
        guide.write_bytes(b"tampered\n")
        attempt("invalid_bundle")
        guide.write_bytes(self.guide)
        attempt("invalid_version_map", version_map=self.version_map()[:1])
        attempt("invalid_version_map", version_map=[dict(item, id="local.same", version="0.1.0") for item in self.version_map()])
        truncated = dict(manifest, patterns=[item for item in manifest["patterns"] if item["ref"]["id"] == "example.parent"],
                         lifecycle=[item for item in manifest["lifecycle"] if item["ref"]["id"] == "example.parent"],
                         files=[item for item in manifest["files"] if "example.parent" in item["path"]])
        for member in ("guide.md", "pattern.json"):
            (self.out / "patterns/team.src/example.child/1.0.0" / member).rename(self.fx.root / f"held-{member}")
        manifest_path.write_text(json.dumps(truncated), encoding="utf-8")
        attempt("external_dependency", version_map=self.version_map()[1:])
        for member in ("guide.md", "pattern.json"):
            (self.fx.root / f"held-{member}").rename(self.out / "patterns/team.src/example.child/1.0.0" / member)
        retired = copy.deepcopy(manifest)
        retired["lifecycle"][0]["effective_status"] = "retired"
        manifest_path.write_text(json.dumps(retired), encoding="utf-8")
        attempt("invalid_bundle")
        retired["lifecycle"][0]["events"] = [{"kind": "lifecycle", "status": "retired", "reason": "r",
                                              "reference": "ADR", "at": TS}]
        manifest_path.write_text(json.dumps(retired), encoding="utf-8")
        attempt("bundle_contains_retired")
        laundered = copy.deepcopy(manifest)
        laundered["lifecycle"][0]["events"] = [{"kind": "revocation", "reason": "r", "reference": "SEC", "at": TS}]
        manifest_path.write_text(json.dumps(laundered), encoding="utf-8")
        attempt("invalid_bundle")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        p.capture(roots, draft("local.child", version="0.1.0"), scope="repo", name="local.child", source_id="repo.local")
        with self.assertRaises(p.PatternError) as caught:
            p.import_bundle(roots, self.out, scope="repo", destination_source="repo.local",
                            version_map_value=self.version_map())
        self.assertEqual((caught.exception.code, caught.exception.status), ("version_exists", "collision"))
        with self.assertRaises(p.PatternError) as caught:
            p.import_bundle(roots, self.out, scope="repo", destination_source="repo.other",
                            version_map_value=self.version_map())
        self.assertEqual(caught.exception.code, "source_id_mismatch")

    def test_import_refuses_links_inside_the_bundle(self):
        self.export()
        outside = self.fx.root / "outside"
        outside.mkdir()
        link = self.out / "patterns" / "linked"
        if os.name == "nt":
            import _winapi
            _winapi.CreateJunction(str(outside), str(link))
        else:
            os.symlink(outside, link, target_is_directory=True)
        self.addCleanup(lambda: os.rmdir(link) if os.name == "nt" else os.unlink(link))
        with self.assertRaises(p.PatternError) as caught:
            p.import_bundle(self.fx.roots(), self.out, scope="repo", destination_source="repo.local",
                            version_map_value=self.version_map())
        self.assertEqual(caught.exception.code, "unsafe_path")

    def test_cli_export_import(self):
        envelope = self.fx.write_json("roots.json", self.fx.envelope())
        refs = self.fx.write_json("refs.json", [ref("team.src", self.parent)])
        code, report, _ = self.fx.cli("export", "--roots-file", envelope, "--refs", refs, "--out", self.out)
        self.assertEqual((code, report["files"]), (0, 3))
        mapping = self.fx.write_json("map.json", self.version_map())
        code, report, _ = self.fx.cli("import", "--roots-file", envelope, "--bundle", self.out, "--scope", "repo",
                                      "--destination-source", "repo.local", "--version-map", mapping)
        self.assertEqual((code, report["written"]), (0, False))


class ReviewCoverageTests(unittest.TestCase):
    """Card 4.2.b.core: review verifies the lock first, then per-clause coverage; never a PASS."""

    def setUp(self):
        self.lf = LockFixture(self)
        self.lf.write()
        p.map_lock(self.lf.fx.roots(), self.lf.lock_path, self.lf.task_map(),
                   expected_lock_digest=p.content_digest(self.lf.read()), write=True)
        self.lock = self.lf.read()

    def evidence(self, **items):
        base = {"example.rules@1.0.0#MUST-1": {"task_ids": ["T1"], "status": "passed", "evidence_refs": ["test.log#12"],
                                               "explanation": "Reviewer ran the check."},
                "example.rules@1.0.0#DEF-1": {"task_ids": ["T2"], "status": "passed", "evidence_refs": ["pr#4"],
                                              "explanation": "Default applied."}}
        for clause, change in items.items():
            if change is None:
                base.pop(clause)
            else:
                base[clause] = dict(base[clause], **change)
        return {"schema_version": 1, "selection_digest": self.lock["selection_digest"],
                "mapping_digest": self.lock["requirement_tasks"]["mapping_digest"],
                "items": [dict(value, clause=clause) for clause, value in base.items()]}

    def review(self, evidence, lock=None):
        return p.review_coverage(self.lf.fx.roots(), lock or self.lock, p.parse_context(self.lf.context), evidence,
                                 today=TODAY)

    def test_complete_evidence_is_ok_but_never_a_clearance(self):
        report = self.review(self.evidence())
        self.assertEqual((report["status"], report["release_clearance"]), ("ok", False))
        self.assertEqual(report["counts"].get("passed"), 2)
        self.assertIn("never a PASS", report["limits"])

    def test_missing_failed_unverified_or_skipped_mandatory_exits_7(self):
        must = "example.rules@1.0.0#MUST-1"
        for name, change in (("missing", None), ("failed", {"status": "failed"}), ("unverified", {"status": "unverified"}),
                             ("not-applicable", {"status": "not-applicable"}), ("waived without exception", {"status": "waived"}),
                             ("passed without refs", {"evidence_refs": []}), ("passed without explanation", {"explanation": " "})):
            with self.subTest(name=name):
                report = self.review(self.evidence(**{must: change}))
                self.assertEqual((report["status"], p.exit_code(report["status"])), ("review-unmet", 7))
        report = self.review(self.evidence(**{"example.rules@1.0.0#DEF-1": None}))
        self.assertEqual(report["status"], "ok")
        self.assertIn("default_unverified", codes(report, "warning"))

    def test_waived_clause_needs_the_locked_exception(self):
        context = p.parse_context(self.lf.context)
        exception = p.parse_exceptions({"schema_version": 1, "items": [{
            "clause": "example.rules@1.0.0#MUST-1", "context_digest": context.digest, "reason": "pilot",
            "approval_ref": "EX-1", "approved_by": "security", "expires": "2026-12-31", "verification": "manual"}]})
        report, _ = self.lf.fx.resolve(self.lf.context, exceptions=exception)
        lock = lock_of(report, context)
        path = self.lf.lock_path.with_name("waived.lock.json")
        p.write_lock(self.lf.fx.roots(), path, lock)
        task_map = dict(self.lf.task_map(), selection_digest=lock["selection_digest"])
        p.map_lock(self.lf.fx.roots(), path, task_map, expected_lock_digest=p.content_digest(lock), write=True)
        waived_lock = json.loads(path.read_text(encoding="utf-8"))
        evidence = dict(self.evidence(**{"example.rules@1.0.0#MUST-1": {"status": "waived", "evidence_refs": ["EX-1"]}}),
                        selection_digest=waived_lock["selection_digest"],
                        mapping_digest=waived_lock["requirement_tasks"]["mapping_digest"])
        result = self.review(evidence, lock=waived_lock)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(next(item for item in result["clauses"] if item["clause"].endswith("MUST-1"))["verdict"], "waived")

    def test_stale_mapping_invalid_items_and_failed_verification(self):
        stale = dict(self.evidence(), mapping_digest="0" * 64)
        self.assertEqual(self.review(stale)["status"], "review-unmet")
        for change, code in (({"task_ids": ["T3"]}, "invalid_evidence"), ({"status": "great"}, "invalid_evidence")):
            with self.subTest(code=code):
                with self.assertRaises(p.PatternError) as caught:
                    self.review(self.evidence(**{"example.rules@1.0.0#DEF-1": change}))
                self.assertEqual(caught.exception.code, code)
        with self.assertRaises(p.PatternError) as caught:
            self.review(dict(self.evidence(), selection_digest="0" * 64))
        self.assertEqual(caught.exception.code, "evidence_selection_mismatch")
        entry = next(item for item in self.lf.publish()["entries"] if item["id"] == "example.rules")
        self.lf.publish(revocations=[{**{k: entry[k] for k in ("id", "version", "sha256")}, "reason": "r",
                                      "reference": "SEC", "at": TS}])
        report = self.review(self.evidence())
        self.assertEqual((report["status"], report["clauses"]), ("unavailable", []),
                         "sources are verified before any coverage is counted")

    def test_unmapped_lock_is_refused_and_cli_exit_code(self):
        unmapped = json.loads(json.dumps(self.lock))
        unmapped["requirement_tasks"] = None
        with self.assertRaises(p.PatternError) as caught:
            self.review(self.evidence(), lock=unmapped)
        self.assertEqual(caught.exception.code, "mapping_required")
        envelope = self.lf.fx.write_json("roots.json", self.lf.fx.envelope())
        context = self.lf.fx.write_json("context.json", self.lf.context)
        evidence = self.lf.fx.write_json("evidence.json", self.evidence(**{"example.rules@1.0.0#MUST-1": None}))
        code, report, stderr = self.lf.fx.cli("review", "--roots-file", envelope, "--lock", self.lf.lock_path,
                                              "--context", context, "--evidence", evidence)
        self.assertEqual((code, report["status"]), (7, "review-unmet"))
        self.assertIn("mandatory_unmet", stderr)


class LockTimeTests(unittest.TestCase):
    """P3-R5-1: a lock is validated at its own creation time before it is returned or written."""

    def test_k1_build_across_exception_expiry_is_refused_and_resume_expiry_still_blocks(self):
        fx = Fixture(self)
        rules = make_pattern("example.rules", requirements=[clause("MUST-1", "must")])
        fx.publish(fx.repo_patterns, "repo.main", [rules], bindings=[binding("b", [ref("repo.main", rules)])])
        context = p.parse_context(ctx())
        exceptions = p.parse_exceptions({"schema_version": 1, "items": [{
            "clause": "example.rules@1.0.0#MUST-1", "context_digest": context.digest, "reason": "pilot",
            "approval_ref": "EX-1", "approved_by": "security", "expires": "2026-12-31", "verification": "manual"}]})
        report, _ = fx.resolve(ctx(), exceptions=exceptions, today=dt.date(2026, 9, 28))
        with self.assertRaises(p.PatternError) as caught:
            p.build_lock(report, context, now=dt.datetime(2027, 1, 1, tzinfo=dt.timezone.utc))
        self.assertEqual(caught.exception.code, "lock_refused")
        lock = p.build_lock(report, context, now=dt.datetime(2026, 9, 28, tzinfo=dt.timezone.utc))
        self.assertEqual(p.verify_lock(fx.roots(), lock, context, today=dt.date(2026, 10, 1))["status"], "ok")
        expired = p.verify_lock(fx.roots(), lock, context, today=dt.date(2027, 1, 1))
        self.assertEqual(expired["status"], "conflict", "a genuinely expired exception still blocks continuation")
        self.assertIn("replan_required", codes(expired, "error"))


class SelectionReportTests(unittest.TestCase):
    """WF review M2: one public helper validates fresh in-process reports (the read_asset floor)."""

    def setUp(self):
        self.fx = Fixture(self)
        self.rules = make_pattern("example.rules", requirements=[
            clause("MUST-1", "must", "ui.theme", "dark"), clause("DEF-1", "default", "visual.layout.max-width", "72ch")],
            assets=[{"path": "guide.md", "kind": "guide", "sha256": hashlib.sha256(b"g\n").hexdigest()}])
        self.extra = make_pattern("example.extra", requirements=[clause("E-1", "default", "ui.font", "serif")])
        self.fx.publish(self.fx.repo_patterns, "repo.main", [self.rules, self.extra])
        self.fx.repo_bindings([binding("req", [ref("repo.main", self.rules)])])
        self.context = p.parse_context(ctx())
        self.report, _ = self.fx.resolve(ctx())

    def refused(self, report, **kwargs):
        kwargs.setdefault("context", self.context)
        with self.assertRaises(p.PatternError) as caught:
            p.validate_selection_report(report, **kwargs)
        self.assertEqual((caught.exception.code, caught.exception.status), ("selection_not_usable", "invalid"))

    def test_fresh_report_is_accepted_without_reading_files(self):
        empty, _ = Fixture(self).resolve(ctx())
        original_read, original_open = p.Reader.read, open

        def forbidden(*_args, **_kwargs):
            raise AssertionError("validate_selection_report must not read files")

        p.Reader.read = forbidden
        self.addCleanup(setattr, p.Reader, "read", original_read)
        import builtins
        builtins.open = forbidden
        try:
            self.assertIs(p.validate_selection_report(self.report, context=self.context), self.report)
            self.assertEqual(p.validate_selection_report(empty, context=self.context)["status"], "empty")
        finally:
            builtins.open = original_open
            p.Reader.read = original_read

    def test_missing_or_wrong_context_and_refs(self):
        self.refused(self.report, context=None)
        self.refused(self.report, context=p.parse_context(ctx(artifact="other")))
        refs_raw = [{"ref": ref("repo.main", self.extra), "role": "default", "approved_by": "me", "approval_ref": "task"}]
        with_refs, _ = self.fx.resolve(ctx(), refs=p.parse_refs(refs_raw))
        self.refused(with_refs)
        self.assertIs(p.validate_selection_report(with_refs, context=self.context, refs=p.parse_refs(refs_raw)), with_refs)
        self.assertIs(p.validate_selection_report(with_refs, context=self.context, refs=refs_raw), with_refs,
                      "raw --refs items are parsed with the same parser")
        with self.assertRaises(p.PatternError):
            p.validate_selection_report(with_refs, context=self.context, refs=[{"bad": 1}])

    def test_edits_with_unchanged_digest_are_refused(self):
        edits = {
            "setting value (M2 repro)": lambda r: r["settings"]["visual.layout.max-width"].update(value="9999px"),
            "requirement text": lambda r: r["requirements"][0].update(text="weakened"),
            "requirement state": lambda r: r["requirements"][0].update(state="waived"),
            "selected assets": lambda r: r["selected"][0].update(assets=[]),
            "selected record added": lambda r: r["selected"].append(dict(copy.deepcopy(r["selected"][0]),
                                                                         ref=ref("repo.main", self.extra))),
            "exceptions": lambda r: r["exceptions"].append({"clause": "x"}),
        }
        for name, change in edits.items():
            with self.subTest(name=name):
                edited = copy.deepcopy(self.report)
                change(edited)
                self.refused(edited)

    def test_invalid_states_and_shapes(self):
        needs, _ = self.fx.resolve(ctx(), refs=p.parse_refs([{"ref": ref("repo.main", make_pattern(
            "example.scoped", applies_to={"target": ["prod"]})), "role": "required", "approved_by": "m",
            "approval_ref": "t"}]))
        for label, value in (("needs-context", needs), ("no digest", dict(self.report, selection_digest=None)),
                             ("lock", p.build_lock(self.report, self.context, now=NOW)),
                             ("missing keys", {"status": "ready", "selection_digest": "0" * 64}),
                             ("preview", dict(copy.deepcopy(self.report), selected=[
                                 dict(self.report["selected"][0], preview=True)])),
                             ("not a mapping", ["x"]),
                             ("status edited to conflict", dict(self.report, status="conflict")),
                             ("status edited to needs-context", dict(self.report, status="needs-context"))):
            with self.subTest(label=label):
                self.refused(value)

    def test_status_must_agree_with_the_selection(self):
        self.assertTrue(self.report["selected"] and any(item["state"] == "mandatory" for item in self.report["requirements"]))
        self.assertTrue(p.asset_refs(self.report), "the flipped report carries required clauses and assets")
        self.refused(dict(self.report, status="empty"))
        empty, _ = Fixture(self).resolve(ctx())
        self.assertEqual(empty["status"], "empty")
        self.refused(dict(empty, status="ready"))

    def test_malformed_shapes_raise_pattern_error_not_python_errors(self):
        cyclic = copy.deepcopy(self.report)
        loop = {}
        loop["self"] = loop
        cyclic["settings"]["visual.layout.max-width"]["value"] = loop
        nan = copy.deepcopy(self.report)
        nan["settings"]["visual.layout.max-width"]["value"] = float("nan")
        for label, value in (("selected None", dict(self.report, selected=None)),
                             ("selected string", dict(self.report, selected="abc")),
                             ("selected with a non-record", dict(self.report, selected=[self.report["selected"][0], 7])),
                             ("NaN setting", nan), ("cyclic setting", cyclic)):
            with self.subTest(label=label):
                self.refused(value)

    def test_refs_must_be_a_list_or_tuple(self):
        refs_raw = [{"ref": ref("repo.main", self.extra), "role": "default", "approved_by": "me", "approval_ref": "task"}]
        with_refs, _ = self.fx.resolve(ctx(), refs=p.parse_refs(refs_raw))
        generator = (item for item in p.parse_refs(refs_raw))
        self.refused(with_refs, refs=generator)
        self.refused(with_refs, refs="not refs")
        self.assertIs(p.validate_selection_report(with_refs, context=self.context, refs=tuple(p.parse_refs(refs_raw))),
                      with_refs)
        with self.assertRaises(p.PatternError) as caught:
            p.validate_selection_report(with_refs, context=self.context, refs=[refs_raw[0], p.parse_refs(refs_raw)[0]])
        self.assertEqual(caught.exception.code, "invalid_schema", "mixed items go through the existing parser")

    def test_legitimate_overrides_and_waivers_pass(self):
        overrides = p.parse_overrides({"schema_version": 1, "items": [{
            "setting": "visual.layout.max-width", "value": "80ch", "reason": "brief", "approval_ref": "b",
            "replaces": ["example.rules@1.0.0#DEF-1"]}]})
        exceptions = p.parse_exceptions({"schema_version": 1, "items": [{
            "clause": "example.rules@1.0.0#MUST-1", "context_digest": self.context.digest, "reason": "pilot",
            "approval_ref": "EX", "approved_by": "sec", "expires": "2026-12-31", "verification": "manual"}]})
        report, _ = self.fx.resolve(ctx(), overrides=overrides, exceptions=exceptions)
        self.assertEqual(report["settings"]["visual.layout.max-width"]["value"], "80ch")
        self.assertIs(p.validate_selection_report(report, context=self.context), report)

    def test_read_asset_uses_the_same_helper(self):
        tampered = copy.deepcopy(self.report)
        tampered["settings"]["visual.layout.max-width"]["value"] = "9999px"
        asset = p.asset_refs(self.report)[0]
        with self.assertRaises(p.PatternError) as caught:
            p.read_asset(self.fx.roots(), asset, selection=tampered, context=self.context)
        self.assertEqual(caught.exception.code, "selection_not_usable")


class StrictBaselineTests(unittest.TestCase):
    """Regressions for independent review of d82b2919 (P2-R4-1, P3-R4-1): omission, laundering, status."""

    def build(self, where):
        fx = Fixture(self)
        rules = make_pattern("example.rules", requirements=[clause("MUST-1", "must", "ui.theme", "dark"),
                                                            clause("DEF-1", "default", "ui.density", "compact"),
                                                            clause("REC-1", "recommendation")])
        soft = make_pattern("example.soft", requirements=[clause("S-1", "default", "ui.font", "serif"),
                                                          clause("S-2", "default", "ui.density", "compact")])
        bindings = [binding("req", [ref("repo.main", rules)]), binding("soft", [ref("repo.main", soft)], role="default")]
        if where == "catalog":
            fx.publish(fx.repo_patterns, "repo.main", [rules, soft], bindings=bindings)
        else:
            fx.publish(fx.repo_patterns, "repo.main", [rules, soft])
            fx.repo_bindings(bindings)
        report, _ = fx.resolve(ctx())
        self.assertEqual({item["ref"]["id"] for item in report["selected"]}, {"example.rules", "example.soft"})
        return fx, lock_of(report, p.parse_context(ctx()))

    def reseal(self, lock, change):
        forged = copy.deepcopy(lock)
        change(forged)
        forged["asset_pins"] = p.asset_refs(forged)
        forged["status"] = "ready" if forged["selected"] else "empty"
        forged["selection_digest"] = p.selection_digest(forged)
        return forged

    def outcome(self, fx, lock):
        try:
            return p.verify_lock(fx.roots(), lock, p.parse_context(ctx()), today=TODAY)["status"]
        except p.PatternError as error:
            return error.status

    @staticmethod
    def drop_soft(value, keep_settings=False):
        value["selected"] = [item for item in value["selected"] if item["ref"]["id"] != "example.soft"]
        value["requirements"] = [item for item in value["requirements"] if not item["clause"].startswith("example.soft")]
        if not keep_settings:
            value["settings"].pop("ui.font")
            value["settings"]["ui.density"]["clauses"] = [
                item for item in value["settings"]["ui.density"]["clauses"] if not item.startswith("example.soft")]

    def test_d1_whole_default_record_omission_on_unchanged_sources(self):
        for where in ("repo", "catalog"):
            with self.subTest(binding_location=where):
                fx, lock = self.build(where)
                self.assertEqual(self.outcome(fx, lock), "ok")
                forged = self.reseal(lock, self.drop_soft)
                self.assertEqual(self.outcome(fx, forged), "conflict")
                report = p.verify_lock(fx.roots(), forged, p.parse_context(ctx()), today=TODAY)
                self.assertIn("selection_changed", codes(report, "error"))
                self.assertNotIn("default_baseline_changed", codes(report))

    def test_d2_d3_setting_laundering_is_internally_inconsistent(self):
        for where in ("repo", "catalog"):
            fx, lock = self.build(where)
            forged_winner = self.reseal(lock, lambda v: (self.drop_soft(v, keep_settings=True),
                                                         v["settings"]["ui.font"].update(value="FORGED")))
            forged_required_default = self.reseal(lock, lambda v: (self.drop_soft(v),
                                                                   v["settings"]["ui.density"].update(value="FORGED")))
            forged_value_only = self.reseal(lock, lambda v: v["settings"]["ui.font"].update(value="FORGED"))
            for name, forged in (("D2 winner outside the lock", forged_winner),
                                 ("D3 required record's default", forged_required_default),
                                 ("value edit with no omission", forged_value_only)):
                with self.subTest(binding_location=where, case=name):
                    with self.assertRaises(p.PatternError) as caught:
                        p.parse_lock(forged)
                    self.assertEqual((caught.exception.code, caught.exception.status), ("invalid_lock", "invalid"))
                    self.assertIn("internally inconsistent", caught.exception.message)

    def test_dropped_clause_without_a_setting_is_detected(self):
        fx, lock = self.build("repo")
        forged = self.reseal(lock, lambda v: v["requirements"].remove(
            next(item for item in v["requirements"] if item["clause"].endswith("#REC-1"))))
        with self.assertRaises(p.PatternError) as caught:
            p.parse_lock(forged)
        self.assertIn("exactly the clauses", caught.exception.message)
        both = self.reseal(lock, lambda v: (v["requirements"].remove(
            next(item for item in v["requirements"] if item["clause"].endswith("#REC-1"))),
            v["selected"][0]["clauses"].remove("example.rules@1.0.0#REC-1")))
        self.assertEqual(self.outcome(fx, both), "invalid", "also dropping it from the record contradicts the pinned body")

    def test_genuine_later_default_addition_and_removal_force_a_replan(self):
        fx, lock = self.build("repo")
        rules = json.loads((fx.repo_patterns / "example.rules" / "1.0.0" / "pattern.json").read_text(encoding="utf-8"))
        fx.repo_bindings([binding("req", [ref("repo.main", rules)])])
        self.assertEqual(self.outcome(fx, lock), "conflict", "a removed default binding is a re-plan")
        fx2 = Fixture(self)
        fx2.publish(fx2.repo_patterns, "repo.main", [rules])
        fx2.repo_bindings([binding("req", [ref("repo.main", rules)])])
        report, _ = fx2.resolve(ctx())
        small = lock_of(report, p.parse_context(ctx()))
        soft = make_pattern("example.soft", requirements=[clause("S-1", "default", "ui.font", "serif")])
        fx2.publish(fx2.repo_patterns, "repo.main", [rules, soft])
        self.assertEqual(p.verify_lock(fx2.roots(), small, p.parse_context(ctx()), today=TODAY)["status"], "ok",
                         "an unbound catalog addition does not disturb the pin")
        fx2.repo_bindings([binding("req", [ref("repo.main", rules)]), binding("soft", [ref("repo.main", soft)],
                                                                             role="default")])
        self.assertEqual(p.verify_lock(fx2.roots(), small, p.parse_context(ctx()), today=TODAY)["status"], "conflict",
                         "a genuine later default binding is a re-plan, not a silent change")

    def test_p3_r4_1_deprecated_at_lock_resealed_as_approved(self):
        fx = Fixture(self)
        rules = make_pattern("example.rules")
        catalog = fx.publish(fx.repo_patterns, "repo.main", [rules])
        entry = catalog["entries"][0]
        fx.publish(fx.repo_patterns, "repo.main", [rules], bindings=[binding("b", [ref("repo.main", rules)])],
                   lifecycle=[{**{k: entry[k] for k in ("id", "version", "sha256")}, "status": "deprecated",
                               "reason": "r", "reference": "ADR", "at": TS}])
        report, _ = fx.resolve(ctx())
        lock = lock_of(report, p.parse_context(ctx()))
        self.assertEqual(lock["selected"][0]["effective_status"], "deprecated")
        self.assertEqual(p.verify_lock(fx.roots(), lock, p.parse_context(ctx()), today=TODAY)["status"], "ok")
        forged = self.reseal(lock, lambda v: v["selected"][0].update(effective_status="approved"))
        verified = p.verify_lock(fx.roots(), forged, p.parse_context(ctx()), today=TODAY)
        self.assertEqual(verified["status"], "conflict", "unchanged catalog: the lock cannot claim it was approved")
        self.assertIn("selection_provenance_changed", codes(verified, "error"))

    def test_override_waiver_empty_map_and_project_still_verify(self):
        fx, lock = self.build("repo")
        context = p.parse_context(ctx())
        overrides = p.parse_overrides({"schema_version": 1, "items": [{
            "setting": "ui.font", "value": "mono", "reason": "brief", "approval_ref": "brief.md",
            "replaces": ["example.soft@1.0.0#S-1"]}]})
        exceptions = p.parse_exceptions({"schema_version": 1, "items": [{
            "clause": "example.rules@1.0.0#MUST-1", "context_digest": context.digest, "reason": "pilot",
            "approval_ref": "EX-1", "approved_by": "security", "expires": "2026-12-31", "verification": "manual"}]})
        report, _ = fx.resolve(ctx(), overrides=overrides, exceptions=exceptions)
        self.assertEqual(report["settings"]["ui.font"]["winner"], "override")
        special = lock_of(report, context)
        self.assertEqual(p.parse_lock(special)["settings"]["ui.font"]["value"], "mono",
                         "a legitimate override winner passes the settle re-derivation")
        verified = p.verify_lock(fx.roots(), special, context, today=TODAY)
        self.assertEqual(verified["status"], "ok")
        empty_report, _ = fx.resolve(ctx(artifact="x"), refs=())
        fx3 = Fixture(self)
        empty_report, _ = fx3.resolve(ctx())
        empty = lock_of(empty_report, p.parse_context(ctx()))
        self.assertEqual(p.verify_lock(fx3.roots(), empty, p.parse_context(ctx()), today=TODAY)["status"], "ok")
        path = fx.repo / "l.lock.json"
        p.write_lock(fx.roots(), path, lock)
        task_map = {"schema_version": 1, "selection_digest": lock["selection_digest"], "tasks": ["T1"],
                    "packages": [{"id": "P1", "tasks": ["T1"]}],
                    "clauses": [{"clause": item["clause"], "tasks": ["T1"]} for item in lock["requirements"]
                                if item["state"] in ("mandatory", "default")]}
        p.map_lock(fx.roots(), path, task_map, expected_lock_digest=p.content_digest(lock), write=True)
        mapped = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(p.verify_lock(fx.roots(), mapped, context, today=TODAY)["status"], "ok")
        self.assertEqual(len(p.project_package(mapped, task_map, "P1")["clauses"]), len(task_map["clauses"]))


class CoreReviewTests(unittest.TestCase):
    """Regressions for independent review of c92ae4dc (P1-C92-1, P3-C92-1..9), using real flows."""

    GUIDE = b"# dashboard guide\n"
    EVIDENCE = b"approved policy excerpt\n"

    def setUp(self):
        self.fx = Fixture(self)

    def asset(self, path="guide.md", data=GUIDE):
        return {"path": path, "kind": "guide", "sha256": hashlib.sha256(data).hexdigest()}

    def version_dir(self, root, pid, version):
        return root / pid / version

    def files(self, root, pid, version):
        return sorted(item.name for item in self.version_dir(root, pid, version).iterdir())

    def test_p1_import_children_first_approve_then_read_asset_and_re_export(self):
        src_root = self.fx.personal_patterns
        child = make_pattern("example.child", assets=[self.asset()])
        parent = make_pattern("example.parent", requirements=[], includes=[ref("team.src", child)])
        self.fx.publish(src_root, "team.src", [child, parent])
        (src_root / "example.child" / "1.0.0" / "guide.md").write_bytes(self.GUIDE)
        bundle = self.fx.root / "bundle"
        p.export_bundle(self.fx.roots(), [p.parse_exact_ref(ref("team.src", parent), "r")], bundle)
        mapping = [{"original": ref("team.src", child), "id": "local.child", "version": "0.1.0"},
                   {"original": ref("team.src", parent), "id": "local.parent", "version": "0.1.0"}]
        imported = p.import_bundle(self.fx.roots(), bundle, scope="repo", destination_source="repo.local",
                                   version_map_value=mapping, write=True)
        child_draft = next(item["destination"] for item in imported["mapping"] if item["destination"]["id"] == "local.child")
        root = self.fx.repo_patterns
        child_ok = p.approve(self.fx.roots(), root / "local.child" / "0.1.0" / "pattern.json", version="1.0.0",
                             approval_value=APPROVAL, expected_digest=child_draft["sha256"])
        self.assertEqual(self.files(root, "local.child", "1.0.0"), ["guide.md", "pattern.json"])
        parent_draft = json.loads((root / "local.parent" / "0.1.0" / "pattern.json").read_text(encoding="utf-8"))
        updated = dict(copy.deepcopy(parent_draft), version="0.2.0", includes=[child_ok["ref"]])
        p.update(self.fx.roots(), root / "local.parent" / "0.1.0" / "pattern.json", updated,
                 expected_digest=p.content_digest(parent_draft), write=True)
        parent_ok = p.approve(self.fx.roots(), root / "local.parent" / "0.2.0" / "pattern.json", version="1.0.0",
                              approval_value=APPROVAL, expected_digest=p.content_digest(updated))
        self.fx.repo_bindings([binding("b", [parent_ok["ref"]])])
        report, _ = self.fx.resolve(ctx())
        self.assertEqual(report["status"], "ready")
        lock = lock_of(report, p.parse_context(ctx()))
        self.assertEqual(p.verify_lock(self.fx.roots(), lock, p.parse_context(ctx()), today=TODAY)["status"], "ok")
        guide = p.asset_refs(lock)[0]
        self.assertEqual(p.read_asset(self.fx.roots(), guide, selection=lock), self.GUIDE)
        self.assertEqual(p.check_sources(self.fx.roots())["status"], "ok")
        again = p.export_bundle(self.fx.roots(), [p.parse_exact_ref(parent_ok["ref"], "r")], self.fx.root / "bundle-2")
        self.assertEqual(again["files"], 3, "re-export carries pattern, child and its asset")

    def test_p1_update_then_approve_carries_assets_and_pattern_sources(self):
        root = self.fx.repo_patterns
        source = dict(statement(), root="pattern", ref="evidence.md",
                      sha256=hashlib.sha256(self.EVIDENCE).hexdigest())
        base = make_pattern("example.visual", assets=[self.asset()], sources=[source])
        self.fx.publish(root, "repo.main", [base])
        (root / "example.visual" / "1.0.0" / "guide.md").write_bytes(self.GUIDE)
        (root / "example.visual" / "1.0.0" / "evidence.md").write_bytes(self.EVIDENCE)
        (root / "example.visual" / "1.0.0" / "unrelated-private.md").write_bytes(b"do not copy\n")
        newer = dict(copy.deepcopy(base), version="1.1.0", status="draft")
        newer.pop("approval")
        p.update(self.fx.roots(), root / "example.visual" / "1.0.0" / "pattern.json", newer,
                 expected_digest=p.content_digest(base), write=True)
        self.assertEqual(self.files(root, "example.visual", "1.1.0"), ["evidence.md", "guide.md", "pattern.json"],
                         "unchanged declared files come from the previous version; nothing else is copied")
        approved = p.approve(self.fx.roots(), root / "example.visual" / "1.1.0" / "pattern.json", version="1.2.0",
                             approval_value=APPROVAL, expected_digest=p.content_digest(newer))
        self.assertEqual(self.files(root, "example.visual", "1.2.0"), ["evidence.md", "guide.md", "pattern.json"])
        self.fx.repo_bindings([binding("b", [approved["ref"]])])
        report, _ = self.fx.resolve(ctx())
        self.assertEqual(p.read_asset(self.fx.roots(), p.asset_refs(report)[0], selection=report,
                                      context=p.parse_context(ctx())), self.GUIDE)
        attestation = p.parse_attestations({"schema_version": 1, "items": [{
            "ref": approved["ref"], "source_index": 0, "source_ref": "evidence.md",
            "source_digest": hashlib.sha256(self.EVIDENCE).hexdigest(), "reviewed_by": "r", "review_ref": "R",
            "reviewed_at": "2026-09-20T00:00:00Z", "valid_until": "2026-12-31", "purpose": "both"}]})
        self.assertEqual(self.fx.resolve(ctx(), attestations=attestation)[0]["status"], "ready",
                         "the carried pattern-root source still attests")

    def test_p1_missing_or_tampered_files_fail_before_publication(self):
        root = self.fx.repo_patterns
        base = make_pattern("example.visual", assets=[self.asset()])
        self.fx.publish(root, "repo.main", [base])
        (root / "example.visual" / "1.0.0" / "guide.md").write_bytes(self.GUIDE)
        changed = dict(copy.deepcopy(base), version="1.1.0", status="draft",
                       assets=[self.asset("new.md", b"new asset\n")])
        changed.pop("approval")
        before = tree_digest(root)
        with self.assertRaises(p.PatternError) as caught:
            p.update(self.fx.roots(), root / "example.visual" / "1.0.0" / "pattern.json", changed,
                     expected_digest=p.content_digest(base), write=True)
        self.assertEqual((caught.exception.code, caught.exception.status), ("declared_file_missing", "unavailable"))
        self.assertEqual(tree_digest(root), before)
        incoming = self.fx.root / "incoming"
        incoming.mkdir()
        (incoming / "new.md").write_bytes(b"tampered\n")
        with self.assertRaises(p.PatternError) as caught:
            p.update(self.fx.roots(), root / "example.visual" / "1.0.0" / "pattern.json", changed,
                     expected_digest=p.content_digest(base), write=True, files_from=incoming)
        self.assertEqual(caught.exception.code, "declared_file_changed")
        self.assertEqual(tree_digest(root), before)
        (incoming / "new.md").write_bytes(b"new asset\n")
        p.update(self.fx.roots(), root / "example.visual" / "1.0.0" / "pattern.json", changed,
                 expected_digest=p.content_digest(base), write=True, files_from=incoming)
        self.assertEqual(self.files(root, "example.visual", "1.1.0"), ["new.md", "pattern.json"])
        draft_file = root / "example.visual" / "1.1.0" / "new.md"
        draft_file.write_bytes(b"edited after capture\n")
        before = tree_digest(root)
        with self.assertRaises(p.PatternError) as caught:
            p.approve(self.fx.roots(), root / "example.visual" / "1.1.0" / "pattern.json", version="1.2.0",
                      approval_value=APPROVAL, expected_digest=p.content_digest(changed))
        self.assertEqual(caught.exception.code, "declared_file_changed")
        self.assertEqual(tree_digest(root), before, "old tree and catalog unchanged")

    def test_p1_capture_carries_declared_files_and_check_detects_missing_ones(self):
        work = self.fx.root / "authoring"
        work.mkdir()
        (work / "guide.md").write_bytes(self.GUIDE)
        value = draft("example.captured", assets=[self.asset()])
        with self.assertRaises(p.PatternError) as caught:
            p.capture(self.fx.roots(), value, scope="repo", name=value["id"], source_id="repo.main")
        self.assertEqual(caught.exception.code, "declared_file_missing")
        self.assertFalse((self.fx.repo_patterns / "catalog.json").exists())
        p.capture(self.fx.roots(), value, scope="repo", name=value["id"], source_id="repo.main", files_from=work)
        self.assertEqual(self.files(self.fx.repo_patterns, "example.captured", "0.1.0"), ["guide.md", "pattern.json"])
        self.assertEqual(p.check_sources(self.fx.roots())["status"], "ok")
        (self.fx.repo_patterns / "example.captured" / "0.1.0" / "guide.md").unlink()
        reader = p.Reader()
        listed = p.list_catalogs(self.fx.roots(), reader)
        self.assertEqual((listed["status"], reader.count("asset")), ("ok", 0), "list stays metadata-only")
        checked = p.check_sources(self.fx.roots())
        self.assertEqual((checked["status"], checked["checked"][0]["status"]), ("unavailable", "unavailable"))
        self.assertIn("declared_file_missing", codes(checked, "error"))
        envelope = self.fx.write_json("roots.json", self.fx.envelope())
        source = work / "second.json"
        second = draft("example.second", assets=[self.asset()])
        source.write_text(json.dumps(second), encoding="utf-8")
        code, report, _ = self.fx.cli("capture", "--roots-file", envelope, "--input", source, "--scope", "repo",
                                      "--name", "example.second", "--expected-catalog-digest",
                                      p.content_digest(json.loads((self.fx.repo_patterns / "catalog.json")
                                                                  .read_text(encoding="utf-8"))))
        self.assertEqual(code, 0, "the CLI takes declared files from the input file's directory")
        self.assertEqual(self.files(self.fx.repo_patterns, "example.second", "0.1.0"), ["guide.md", "pattern.json"])

    def test_p3_1_lifecycle_preview_applies_the_write_rules(self):
        retired = make_pattern("example.retired")
        drafty = draft("example.drafty")
        catalog = self.fx.publish(self.fx.repo_patterns, "repo.main", [retired, drafty])
        entry = catalog["entries"][0]
        self.fx.publish(self.fx.repo_patterns, "repo.main", [retired, drafty], lifecycle=[
            {**{k: entry[k] for k in ("id", "version", "sha256")}, "status": "retired", "reason": "r",
             "reference": "ADR", "at": TS}])
        record = {"reason": "r", "reference": "x", "at": "2026-09-20T00:00:00Z"}
        for ref_text, action in (("repo.main:example.retired@1.0.0", "deprecate"),
                                 ("repo.main:example.drafty@0.1.0", "deprecate")):
            with self.subTest(ref=ref_text):
                with self.assertRaises(p.PatternError) as caught:
                    p.record_lifecycle(self.fx.roots(), ref_text, action=action, record_value=record,
                                       expected_catalog_digest=None)
                self.assertIn("transition", caught.exception.message)
        preview = p.record_lifecycle(self.fx.roots(), "repo.main:example.retired@1.0.0", action="revoke",
                                     record_value=record, expected_catalog_digest=None)
        self.assertEqual(preview["catalog_sha256"], p.content_digest(json.loads(
            (self.fx.repo_patterns / "catalog.json").read_text(encoding="utf-8"))), "preview returns the CAS digest")

    def test_p3_2_default_url_source_warns(self):
        url = make_pattern("example.url", requirements=[clause("D-1", "default")],
                           sources=[dict(statement(), root="external", ref="https://standards.example/doc")])
        self.fx.publish(self.fx.repo_patterns, "repo.main", [url],
                        bindings=[binding("d", [ref("repo.main", url)], role="default")])
        report, _ = self.fx.resolve(ctx())
        self.assertEqual(report["status"], "ready")
        self.assertIn("source_unverified_default", codes(report, "warning"))

    def test_p3_3_p3_4_attestation_inputs_are_validated(self):
        rules = make_pattern("example.rules")
        self.fx.publish(self.fx.repo_patterns, "repo.main", [rules], bindings=[binding("b", [ref("repo.main", rules)])])
        report, _ = self.fx.resolve(ctx())
        lock = lock_of(report, p.parse_context(ctx()))
        good = {"ref": ref("repo.main", rules), "source_index": 0, "source_ref": rules["sources"][0]["ref"],
                "source_digest": "a" * 64, "reviewed_by": "r", "review_ref": "R",
                "reviewed_at": "2026-09-20T00:00:00Z", "valid_until": "2026-12-31", "purpose": "both"}
        for raw in ([{}], ["x"], "x", [good, good], [dict(good, source_index=-1)]):
            with self.subTest(raw=str(raw)[:30]):
                with self.assertRaises(p.PatternError):
                    self.fx.resolve(ctx(), attestations=raw)
                with self.assertRaises(p.PatternError):
                    p.verify_lock(self.fx.roots(), lock, p.parse_context(ctx()), attestations=raw, today=TODAY)
        self.assertEqual(self.fx.resolve(ctx(), attestations=[good])[0]["status"], "ready", "raw valid items work")
        junk = dict(copy.deepcopy(lock), source_attestations=[{"junk": 1}])
        with self.assertRaises(p.PatternError) as caught:
            p.parse_lock(junk)
        self.assertEqual(caught.exception.status, "invalid")

    def test_p3_5_p3_6_p3_7_apply_refuses_unavailable_refs_and_creates_parents(self):
        fx = Fixture(self)
        shutil.rmtree(fx.repo / ".claude")
        rules = make_pattern("example.rules")
        ghost = {"source": "repo.main", "id": "example.ghost", "version": "1.0.0", "sha256": "0" * 64}
        change = {"schema_version": 1, "operation": "add", "id": "g", "binding": binding("g", [ghost]),
                  "reason": "r", "approved_by": "a", "approval_ref": "b"}
        with self.assertRaises(p.PatternError) as caught:
            p.apply_change(fx.roots(), change)
        self.assertEqual((caught.exception.code, caught.exception.status), ("binding_ref_unavailable", "unavailable"))
        self.assertFalse((fx.repo / ".claude").exists())
        pack_root = fx.pack_chain()
        fx.publish(pack_root / "patterns", "team.patterns", [rules])
        real = dict(change, binding=binding("g", [ref("team.patterns", rules)]))
        written = p.apply_change(fx.roots(), real, write=True)
        self.assertTrue(written["written"])
        self.assertTrue((fx.repo / ".claude" / "patterns" / "bindings.json").is_file(), "missing parents are created")
        with self.assertRaises(p.PatternError) as caught:
            p.apply_change(fx.roots(), dict(real, operation="replace"), write=True)
        self.assertIn("--expected-digest", caught.exception.message)
        self.assertIn("bindings", caught.exception.message)

    def test_p3_8_import_preflights_every_destination(self):
        src_root = self.fx.personal_patterns
        child = make_pattern("example.child", assets=[self.asset()])
        self.fx.publish(src_root, "team.src", [child])
        (src_root / "example.child" / "1.0.0" / "guide.md").write_bytes(self.GUIDE)
        bundle = self.fx.root / "bundle"
        p.export_bundle(self.fx.roots(), [p.parse_exact_ref(ref("team.src", child), "r")], bundle)
        blocked = self.fx.repo_patterns / "local.child" / "0.1.0"
        blocked.mkdir(parents=True)
        (blocked / "pattern.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(p.PatternError) as caught:
            p.import_bundle(self.fx.roots(), bundle, scope="repo", destination_source="repo.local",
                            version_map_value=[{"original": ref("team.src", child), "id": "local.child",
                                                "version": "0.1.0"}], write=True)
        self.assertEqual(caught.exception.code, "unregistered_staging_conflict")
        self.assertEqual(sorted(item.name for item in blocked.iterdir()), ["pattern.json"], "no orphaned asset")


class NamespaceTests(unittest.TestCase):
    """Regressions for review of 8addc395 (P3-R6-1, P3-R6-2, note 2): one unambiguous destination namespace."""

    def setUp(self):
        self.fx = Fixture(self)
        self.work = self.fx.root / "work"
        self.work.mkdir()

    def asset(self, path, data):
        return {"path": path, "kind": "guide", "sha256": hashlib.sha256(data).hexdigest()}

    def write(self, name, data):
        target = self.work / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def assert_refused_unchanged(self, action, code="destination_conflict"):
        before = tree_digest(self.fx.root)
        with self.assertRaises(p.PatternError) as caught:
            action()
        self.assertEqual(caught.exception.code, code, caught.exception.message)
        self.assertEqual(tree_digest(self.fx.root), before, "nothing written anywhere")
        return caught.exception

    def capture(self, value, **kwargs):
        kwargs.setdefault("source_id", None if (self.fx.repo_patterns / "catalog.json").exists() else "repo.main")
        if kwargs["source_id"] is None:
            kwargs.pop("source_id")
            kwargs["expected_catalog_digest"] = p.content_digest(json.loads(
                (self.fx.repo_patterns / "catalog.json").read_text(encoding="utf-8")))
        return p.capture(self.fx.roots(), value, scope="repo", name=value["id"], files_from=self.work, **kwargs)

    def test_reserved_body_name_is_refused_for_assets_and_pattern_sources(self):
        self.write("pattern.json", b"{}")
        asset_case = draft("example.pj", assets=[self.asset("pattern.json", b"{}")])
        self.assert_refused_unchanged(lambda: self.capture(asset_case))
        self.assert_refused_unchanged(lambda: self.capture(asset_case), "destination_conflict")
        source_case = draft("example.src", sources=[dict(statement(), root="pattern", ref="Pattern.JSON")])
        self.write("Pattern.JSON", b"{}")
        self.assert_refused_unchanged(lambda: self.capture(source_case))
        plain = draft("example.plain")
        self.capture(plain)
        clash = dict(plain, version="0.2.0", assets=[self.asset("pattern.json", b"{}")])
        self.assert_refused_unchanged(lambda: p.update(
            self.fx.roots(), self.fx.repo_patterns / "example.plain" / "0.1.0" / "pattern.json", clash,
            expected_digest=p.content_digest(plain), files_from=self.work))
        nested = draft("example.nested", assets=[self.asset("docs/pattern.json", b"nested\n")])
        self.write("docs/pattern.json", b"nested\n")
        self.capture(nested)
        self.assertEqual(sorted(path.relative_to(self.fx.repo_patterns / "example.nested" / "0.1.0").as_posix()
                                for path in (self.fx.repo_patterns / "example.nested" / "0.1.0").rglob("*")
                                if path.is_file()), ["docs/pattern.json", "pattern.json"],
                         "a nested file named pattern.json is not the body and is allowed")

    def test_reserved_name_in_a_registered_draft_cannot_orphan_approval(self):
        value = draft("example.approve")
        self.capture(value)
        root = self.fx.repo_patterns / "example.approve" / "0.1.0"
        catalog = json.loads((self.fx.repo_patterns / "catalog.json").read_text(encoding="utf-8"))
        hacked = dict(value, sources=[dict(statement(), root="pattern", ref="pattern.json")])
        (root / "pattern.json").write_text(json.dumps(hacked), encoding="utf-8")
        catalog["entries"][0]["sha256"] = p.content_digest(hacked)
        (self.fx.repo_patterns / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
        for attempt in range(2):
            with self.subTest(attempt=attempt):
                self.assert_refused_unchanged(lambda: p.approve(self.fx.roots(), root / "pattern.json", version="1.0.0",
                                                                approval_value=APPROVAL,
                                                                expected_digest=p.content_digest(hacked)))
        self.assertFalse((self.fx.repo_patterns / "example.approve" / "1.0.0").exists(), "no orphan, retry is clean")

    def test_case_fold_and_prefix_collisions(self):
        data = b"same\n"
        self.write("Guide.md", data)
        self.write("guide.md", data)
        cases = {
            "case variants": draft("example.case", assets=[self.asset("Guide.md", data), self.asset("guide.md", data)]),
            "source vs asset case": draft("example.mixed", assets=[self.asset("guide.md", data)],
                                          sources=[dict(statement(), root="pattern", ref="GUIDE.md")]),
        }
        for name, value in cases.items():
            with self.subTest(name=name):
                self.assert_refused_unchanged(lambda value=value: self.capture(value))
        shared = draft("example.shared", assets=[self.asset("guide.md", data)],
                       sources=[dict(statement(), root="pattern", ref="guide.md", sha256=hashlib.sha256(data).hexdigest())])
        self.capture(shared)
        self.assertEqual(sorted(path.name for path in (self.fx.repo_patterns / "example.shared" / "0.1.0").iterdir()),
                         ["guide.md", "pattern.json"], "an asset and a source naming the same exact file coalesce")

    def test_update_mixing_fallback_and_supplied_files_detects_prefix_collision(self):
        nested_data, flat_data = b"nested\n", b"flat\n"
        self.write("a/b", nested_data)
        base = draft("example.ab", assets=[self.asset("a/b", nested_data)])
        self.capture(base)
        root = self.fx.repo_patterns / "example.ab" / "0.1.0"
        supply = self.fx.root / "supply"
        supply.mkdir()
        (supply / "a").write_bytes(flat_data)
        newer = dict(base, version="0.2.0", assets=[self.asset("a/b", nested_data), self.asset("a", flat_data)])
        for write in (False, True):
            with self.subTest(write=write):
                self.assert_refused_unchanged(lambda write=write: p.update(
                    self.fx.roots(), root / "pattern.json", newer, expected_digest=p.content_digest(base), write=write,
                    files_from=supply))
        valid = dict(base, version="0.2.0", assets=[self.asset("a/b", nested_data), self.asset("a/c", flat_data)])
        (supply / "a").unlink()
        (supply / "a").mkdir()
        (supply / "a" / "c").write_bytes(flat_data)
        p.update(self.fx.roots(), root / "pattern.json", valid, expected_digest=p.content_digest(base), write=True,
                 files_from=supply)
        self.assertEqual(sorted(path.relative_to(self.fx.repo_patterns / "example.ab" / "0.2.0").as_posix()
                                for path in (self.fx.repo_patterns / "example.ab" / "0.2.0").rglob("*") if path.is_file()),
                         ["a/b", "a/c", "pattern.json"], "valid nested paths from both sources are published")

    def test_existing_disk_file_blocks_a_directory_destination_without_traceback(self):
        value = draft("example.disk", assets=[self.asset("a/b", b"x\n")])
        self.write("a/b", b"x\n")
        blocked = self.fx.repo_patterns / "example.disk" / "0.1.0"
        blocked.mkdir(parents=True)
        (blocked / "a").write_bytes(b"stray\n")
        (self.fx.repo_patterns / "catalog.json").unlink(missing_ok=True)
        with self.assertRaises(p.PatternError) as caught:
            p.capture(self.fx.roots(), value, scope="repo", name=value["id"], source_id="repo.main", files_from=self.work)
        self.assertEqual(caught.exception.code, "destination_conflict")
        self.assertEqual(sorted(item.name for item in blocked.iterdir()), ["a"])

    def test_cli_reports_namespace_conflicts_as_invalid_input(self):
        self.write("Guide.md", b"x\n")
        self.write("guide.md", b"x\n")
        source = self.work / "draft.json"
        source.write_text(json.dumps(draft("example.cli", assets=[self.asset("Guide.md", b"x\n"),
                                                                  self.asset("guide.md", b"x\n")])), encoding="utf-8")
        envelope = self.fx.write_json("roots.json", self.fx.envelope())
        code, report, stderr = self.fx.cli("capture", "--roots-file", envelope, "--input", source, "--scope", "repo",
                                           "--name", "example.cli", "--source-id", "repo.main")
        self.assertEqual((code, report["status"]), (2, "invalid"))
        self.assertIn("destination_conflict", stderr)
        self.assertNotIn("Traceback", stderr)


class NamespaceInvariantTests(unittest.TestCase):
    """Review of 445e3ad9 (P3-R8-1, P3-R8-2): the whole namespace invariant, table-driven."""

    REFUSED = [
        ("file vs child, sibling '.'", ["a", "a.md", "a/b"]),
        ("file vs child, sibling '-'", ["a", "a-b", "a/b"]),
        ("file vs child, sibling ' '", ["a", "a b", "a/b"]),
        ("file vs child, sibling '_'", ["a", "a_b", "a/b"]),
        ("file vs grandchild", ["x", "x/y/z"]),
        ("file vs deep child, siblings between", ["d/e", "d/e.txt", "d/e-1", "d/e/f/g"]),
        ("case-varied file vs directory", ["A", "a/b"]),
        ("file case collision", ["Guide.md", "guide.md"]),
        ("directory spelled two ways", ["Docs/x", "docs/y"]),
        ("multilevel ancestor case", ["top/Mid/x", "top/mid/y"]),
        ("unicode casefold ancestor", ["Stra\u00dfe/a", "STRASSE/b"]),
    ]
    ALLOWED = [
        ("similar siblings", ["a", "a.md", "a-b", "a b", "a_b", "ab"]),
        ("nested siblings", ["a/b", "a/c", "a/d/e", "a/d/f"]),
        ("same directory, same spelling", ["docs/x", "docs/y", "docs/sub/z"]),
        ("file named like a sibling directory's prefix", ["a.md", "a/b"]),
    ]

    def keys(self, names):
        return [(name, name.encode("utf-8")) for name in names]

    def test_every_order_of_refused_sets_is_refused(self):
        import itertools
        for label, names in self.REFUSED:
            for order in itertools.permutations(names):
                with self.subTest(label=label, order=order):
                    with self.assertRaises(p.PatternError) as caught:
                        p._check_namespace(self.keys(order))
                    self.assertEqual(caught.exception.code, "destination_conflict")

    def test_every_order_of_allowed_sets_passes(self):
        import itertools
        for label, names in self.ALLOWED:
            for order in itertools.permutations(names):
                with self.subTest(label=label, order=order):
                    self.assertEqual(len(p._check_namespace(self.keys(order))), len(names))
        self.assertEqual(len(p._check_namespace([("docs/x", b"1"), ("docs/x", b"1")])), 1, "same bytes coalesce")
        with self.assertRaises(p.PatternError):
            p._check_namespace([("docs/x", b"1"), ("docs/x", b"2")])

    CLI_CASES = [
        (["a/b"], ["a", "a.md"]), (["a/b"], ["a", "a-b"]), (["a/b"], ["a", "a b"]), (["a/b"], ["A"]),
        (["x/y/z"], ["x"]), (["d/e/f/g", "d/e.txt"], ["d/e", "d/e-1"]),
        (["Docs/x"], ["docs/y"]), (["top/Mid/x"], ["top/mid/y"]),
    ]

    def test_cli_preview_write_and_retry_leave_zero_changes(self):
        """A previous version's files (fallback) plus supplied files, through the real CLI update."""
        for base_names, added in self.CLI_CASES:
            with self.subTest(base=base_names, added=added):
                fx = Fixture(self)

                def put(root, names):
                    records = []
                    for name in names:
                        data = f"{name}\n".encode("utf-8")
                        target = root / name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(data)
                        records.append({"path": name, "kind": "guide", "sha256": hashlib.sha256(data).hexdigest()})
                    return records

                work, supply = fx.root / "work", fx.root / "supply"
                base = draft("example.base", assets=put(work, base_names))
                p.capture(fx.roots(), base, scope="repo", name="example.base", source_id="repo.main", files_from=work)
                newer = dict(base, version="0.2.0", assets=base["assets"] + put(supply, added))
                source = fx.root / "newer.json"
                source.write_text(json.dumps(newer), encoding="utf-8")
                envelope = fx.write_json("roots.json", fx.envelope())
                before = tree_digest(fx.repo)
                for attempt in ("preview", "write", "retry"):
                    args = ["update", "--roots-file", envelope, "--path",
                            fx.repo_patterns / "example.base" / "0.1.0" / "pattern.json", "--input", source,
                            "--expected-digest", p.content_digest(base), "--files-from", supply]
                    if attempt != "preview":
                        args.append("--write")
                    code, report, stderr = fx.cli(*args)
                    self.assertEqual((attempt, code, report["status"]), (attempt, 2, "invalid"), stderr)
                    self.assertIn("destination_conflict", stderr)
                    self.assertNotIn("Traceback", stderr)
                    self.assertEqual(tree_digest(fx.repo), before, f"{attempt} changed the tree")

    def test_valid_names_still_publish_through_capture_and_approve(self):
        fx = Fixture(self)
        work = fx.root / "work"
        names = ["a", "a.md", "a-b", "a b", "docs/x", "docs/sub/y"]
        assets = []
        for name in names:
            data = f"{name}\n".encode("utf-8")
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            assets.append({"path": name, "kind": "guide", "sha256": hashlib.sha256(data).hexdigest()})
        value = draft("example.names", assets=assets)
        p.capture(fx.roots(), value, scope="repo", name=value["id"], source_id="repo.main", files_from=work)
        p.approve(fx.roots(), fx.repo_patterns / "example.names" / "0.1.0" / "pattern.json", version="1.0.0",
                  approval_value=APPROVAL, expected_digest=p.content_digest(value))
        published = sorted(path.relative_to(fx.repo_patterns / "example.names" / "1.0.0").as_posix()
                           for path in (fx.repo_patterns / "example.names" / "1.0.0").rglob("*") if path.is_file())
        self.assertEqual(published, sorted(names + ["pattern.json"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
