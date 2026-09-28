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
        self.assertEqual(record("team")["source"], {"state": "absent", "value": None, "origin": None})
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
        return p.build_lock(report, p.parse_context(self.context), now=now)

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
            p.build_lock(report, p.parse_context(ctx()))
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
