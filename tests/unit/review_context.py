#!/usr/bin/env python3
# component: review-context-tests
# implements: ADR-0040, ADR-0028
# intent: .claude/plans/adaptive-review/spec.md
# constraints: hermetic temp dirs and labeled in-process provider doubles; no models, network or real provider acceptance
# last_intent_review: 2026-09-28
"""Behavior tests for evidenced review depth (T1/T2) and the optional pattern adapter (T3/T4).

Pattern tests use a PROVIDER DOUBLE, not the real reusable-patterns provider. They prove the
adapter's call order and pass-through; real frozen-provider compatibility is coordinator T11.
"""
import ast
import json
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "lib"))
import review_context as rc  # noqa: E402

LOW = {"deployment": "internal", "exposure": "trusted", "impact": "reversible",
       "behavior_change": False, "security_boundary": False, "blast_radius": "contained"}


def ctx(facts=None, evidence=None, actor="builder@example", reference="plan.md#T1", **overrides):
    facts = dict(LOW if facts is None else facts)
    value = {"schema_version": 1, "facts": facts,
             "evidence": {key: f"evidence/{key}.md" for key in facts} if evidence is None else evidence,
             "asserted_by": {"actor": actor, "reference": reference}}
    value.update(overrides)
    return value


class DepthDecision(unittest.TestCase):
    def test_low_risk_known_facts_permit_lean(self):
        result = rc.assess_depth(ctx())
        self.assertEqual((result["minimum"], result["selected"], result["status"]), ("lean", "lean", "ok"))
        self.assertEqual(result["question_tags"], [])
        self.assertEqual(result["unknown_facts"], [])
        self.assertEqual(result["recommended_independence"], "independent")
        self.assertIs(result["release_clearance"], False)
        self.assertEqual(result["authority"], {"selects_model": False, "mars_consent": False,
                                               "authorizes_execution": False})
        self.assertEqual(result["asserted_by"], {"actor": "builder@example", "reference": "plan.md#T1"})
        self.assertEqual([item["fact"] for item in result["source_evidence"]], list(rc.AXES))

    def test_local_and_isolated_also_permit_lean(self):
        facts = dict(LOW, deployment="local", exposure="isolated")
        self.assertEqual(rc.assess_depth(ctx(facts))["selected"], "lean")

    def test_each_high_consequence_independently_requires_deep(self):
        cases = [
            ("deployment", "production", ["deep-review", "production"]),
            ("exposure", "untrusted", ["deep-review", "security-critical"]),
            ("impact", "sensitive", ["deep-review", "security-critical"]),
            ("impact", "irreversible", ["deep-review", "security-critical"]),
            ("security_boundary", True, ["deep-review", "security-critical"]),
            ("blast_radius", "shared", ["deep-review"]),
        ]
        for axis, value, tags in cases:
            with self.subTest(axis=axis, value=value):
                result = rc.assess_depth(ctx(dict(LOW, **{axis: value})))
                self.assertEqual((result["minimum"], result["selected"], result["status"]), ("deep", "deep", "ok"))
                self.assertEqual(result["question_tags"], tags)
                self.assertEqual(result["recommended_independence"], "independent-staged")
                self.assertTrue(any(reason.startswith(f"{axis}=") and "deep" in reason for reason in result["reasons"]))
                with self.assertRaises(rc.DepthRefused):
                    rc.assess_depth(ctx(dict(LOW, **{axis: value})), "standard")
                with self.assertRaises(rc.DepthRefused):
                    rc.assess_depth(ctx(dict(LOW, **{axis: value})), "lean")

    def test_behavior_change_alone_is_standard(self):
        result = rc.assess_depth(ctx(dict(LOW, behavior_change=True)))
        self.assertEqual((result["minimum"], result["selected"], result["status"]), ("standard", "standard", "ok"))
        self.assertEqual(result["question_tags"], [])
        self.assertTrue(any("rules out lean" in reason for reason in result["reasons"]))
        with self.assertRaises(rc.DepthRefused):
            rc.assess_depth(ctx(dict(LOW, behavior_change=True)), "lean")

    def test_every_unknown_is_visible_and_never_lean(self):
        for axis in rc.AXES:
            for absent in (False, True):
                with self.subTest(axis=axis, absent=absent):
                    facts = dict(LOW)
                    if absent:
                        del facts[axis]
                    else:
                        facts[axis] = "unknown"
                    evidence = {key: "ref" for key in facts if facts[key] != "unknown"}
                    result = rc.assess_depth(ctx(facts, evidence))
                    self.assertEqual((result["minimum"], result["selected"]), ("standard", "standard"))
                    self.assertEqual(result["status"], "needs-context")
                    self.assertEqual(result["unknown_facts"], [axis])
                    self.assertEqual(result["facts"][axis], "unknown")
                    self.assertEqual(result["question_tags"], ["risk-unknown"])
                    with self.assertRaises(rc.DepthRefused):
                        rc.assess_depth(ctx(facts, evidence), "lean")

    def test_unknown_with_deep_floor_keeps_both(self):
        facts = dict(LOW, deployment="production", exposure="unknown")
        evidence = {key: "ref" for key in facts if key != "exposure"}
        result = rc.assess_depth(ctx(facts, evidence))
        self.assertEqual((result["selected"], result["status"]), ("deep", "needs-context"))
        self.assertEqual(result["question_tags"], ["deep-review", "production", "risk-unknown"])

    def test_unknown_may_carry_evidence_but_known_needs_it(self):
        facts = dict(LOW, impact="unknown")
        result = rc.assess_depth(ctx(facts))
        self.assertIn({"fact": "impact", "value": "unknown", "reference": "evidence/impact.md"},
                      result["source_evidence"])

    def test_no_context_is_standard_needs_context(self):
        result = rc.assess_depth(None)
        self.assertEqual((result["minimum"], result["selected"], result["status"]),
                         ("standard", "standard", "needs-context"))
        self.assertEqual(result["unknown_facts"], list(rc.AXES))
        self.assertEqual(result["question_tags"], ["risk-unknown"])
        self.assertIsNone(result["asserted_by"])
        self.assertIsNone(result["context_sha256"])
        self.assertIs(result["release_clearance"], False)
        with self.assertRaises(rc.DepthRefused):
            rc.assess_depth(None, "lean")
        self.assertEqual(rc.assess_depth(None, "deep")["question_tags"], ["deep-review", "risk-unknown"])

    def test_explicit_higher_is_allowed(self):
        standard = rc.assess_depth(ctx(), "standard")
        self.assertEqual((standard["minimum"], standard["selected"]), ("lean", "standard"))
        self.assertEqual(standard["question_tags"], [])
        self.assertIn("explicit request raises depth from lean to standard", standard["reasons"])
        deep = rc.assess_depth(ctx(), "deep")
        self.assertEqual((deep["minimum"], deep["selected"]), ("lean", "deep"))
        self.assertEqual(deep["question_tags"], ["deep-review"])
        from_standard = rc.assess_depth(ctx(dict(LOW, behavior_change=True)), "deep")
        self.assertEqual((from_standard["minimum"], from_standard["selected"]), ("standard", "deep"))
        same = rc.assess_depth(ctx(), "lean")
        self.assertEqual(same["selected"], "lean")

    def test_invalid_requests_fail(self):
        for requested in ("fast", "", None, True, 1, "LEAN", "Deep"):
            with self.subTest(requested=requested), self.assertRaises(rc.ContextError):
                rc.assess_depth(ctx(), requested)

    def test_booleans_and_integers_are_distinct(self):
        for axis in ("behavior_change", "security_boundary"):
            for value in (0, 1, "true", "false", "False", None, 0.0):
                with self.subTest(axis=axis, value=value), self.assertRaises(rc.ContextError):
                    rc.assess_depth(ctx(dict(LOW, **{axis: value})))
        for axis in ("deployment", "exposure", "impact", "blast_radius"):
            for value in (True, False, 1, 0, None, "Production", ["local"]):
                with self.subTest(axis=axis, value=value), self.assertRaises(rc.ContextError):
                    rc.assess_depth(ctx(dict(LOW, **{axis: value})))
        for version in (True, "1", 1.0, 2, 0, None):
            with self.subTest(version=version), self.assertRaises(rc.ContextError):
                rc.assess_depth(ctx(schema_version=version))

    def test_malformed_contexts_fail(self):
        base = ctx()
        bad = [
            [], "context", 1,
            {key: value for key, value in base.items() if key != "asserted_by"},
            {key: value for key, value in base.items() if key != "evidence"},
            {key: value for key, value in base.items() if key != "facts"},
            dict(base, extra=True),
            dict(base, facts=[]),
            dict(base, evidence=[]),
            dict(base, facts=dict(LOW, lines_changed=3)),
            dict(base, facts=dict(LOW, deployment="staging")),
            dict(base, evidence=dict(base["evidence"], risk="x")),
            dict(base, evidence={key: value for key, value in base["evidence"].items() if key != "impact"}),
            dict(base, evidence=dict(base["evidence"], impact="   ")),
            dict(base, evidence=dict(base["evidence"], impact="")),
            dict(base, evidence=dict(base["evidence"], impact=7)),
            dict(base, evidence=dict(base["evidence"], impact="x" * (rc.MAX_TEXT + 1))),
            dict(base, asserted_by=None),
            dict(base, asserted_by="builder"),
            dict(base, asserted_by={"actor": "builder"}),
            dict(base, asserted_by={"reference": "plan.md"}),
            dict(base, asserted_by={"actor": " ", "reference": "plan.md"}),
            dict(base, asserted_by={"actor": "builder", "reference": ""}),
            dict(base, asserted_by={"actor": "builder", "reference": "plan.md", "role": "owner"}),
            dict(base, asserted_by={"actor": 1, "reference": "plan.md"}),
        ]
        for index, value in enumerate(bad):
            with self.subTest(index=index), self.assertRaises(rc.ContextError):
                rc.assess_depth(value)

    def test_missing_evidence_names_the_fact(self):
        value = ctx(evidence={key: "ref" for key in LOW if key != "security_boundary"})
        with self.assertRaisesRegex(rc.ContextError, "security_boundary=false needs a nonblank evidence"):
            rc.assess_depth(value)

    def test_does_not_mutate_input_and_is_deterministic(self):
        value = ctx()
        snapshot = json.dumps(value, sort_keys=True)
        first, second = rc.assess_depth(value), rc.assess_depth(value)
        self.assertEqual(first, second)
        self.assertEqual(json.dumps(value, sort_keys=True), snapshot)
        self.assertEqual(rc.render_assessment(first), rc.render_assessment(second))

    def test_changed_fact_or_provenance_changes_rendered_context(self):
        base = rc.assess_depth(ctx(), "standard")
        variants = {
            "fact": ctx(dict(LOW, behavior_change=True)),
            "evidence": ctx(evidence=dict({key: f"evidence/{key}.md" for key in LOW}, impact="other.md")),
            "actor": ctx(actor="someone-else"),
            "reference": ctx(reference="plan.md#T2"),
        }
        rendered = rc.render_assessment(base)
        for name, value in variants.items():
            with self.subTest(name=name):
                other = rc.assess_depth(value, "standard")
                self.assertNotEqual(other["context_sha256"], base["context_sha256"])
                self.assertNotEqual(rc.render_assessment(other), rendered)

    def test_render_shows_provenance_and_refuses_clearance(self):
        text = rc.render_assessment(rc.assess_depth(ctx(evidence=dict(
            {key: "ref" for key in LOW}, impact="a|b\nc"))))
        self.assertIn("builder@example (plan.md#T1)", text)
        self.assertIn("| impact | reversible | a\\|b c |", text)
        self.assertIn("Release clearance: false", text)
        forged = dict(rc.assess_depth(ctx()), release_clearance=True)
        with self.assertRaises(rc.ContextError):
            rc.render_assessment(forged)
        with self.assertRaises(rc.ContextError):
            rc.render_assessment({"selected": "lean"})
        self.assertIn("Asserted by: not supplied", rc.render_assessment(rc.assess_depth(None)))


class ReadContext(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, text):
        path = self.tmp / "context.json"
        path.write_bytes(text.encode("utf-8") if isinstance(text, str) else text)
        return path

    def test_valid_file_round_trips(self):
        path = self.write(json.dumps(ctx()))
        self.assertEqual(rc.assess_depth(rc.read_context(path))["selected"], "lean")

    def test_strict_json(self):
        cases = ['{"schema_version": 1, "schema_version": 1}', '{"x": NaN}', '{"x": Infinity}', "[]",
                 "not json", b"\xff\xfe"]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(rc.ContextError):
                rc.read_context(self.write(text))
        with self.assertRaises(rc.ContextError):
            rc.read_context(self.write(" " * (rc.MAX_CONTEXT_BYTES + 1)))

    def test_hook_messages_are_preserved(self):
        with self.assertRaisesRegex(rc.ContextError, "^duplicate JSON key: schema_version$"):
            rc.read_context(self.write('{"schema_version": 1, "schema_version": 1}'))
        with self.assertRaisesRegex(rc.ContextError, "^non-finite JSON number refused: NaN$"):
            rc.read_context(self.write('{"x": NaN}'))

    def test_deep_nesting_within_size_limit_is_context_error(self):
        depth = 10000
        for opener, closer in (("[", "]"), ('{"a":', "}")):
            text = '{"x": ' + opener * depth + "0" + closer * depth + "}"
            self.assertLessEqual(len(text.encode("utf-8")), rc.MAX_CONTEXT_BYTES)
            with self.subTest(opener=opener), self.assertRaisesRegex(rc.ContextError, "nested too deeply"):
                rc.read_context(self.write(text))

    def test_integer_digit_limit_is_context_error(self):
        text = '{"x": ' + "9" * 5000 + "}"
        self.assertLessEqual(len(text), rc.MAX_CONTEXT_BYTES)
        if hasattr(sys, "get_int_max_str_digits") and 0 < sys.get_int_max_str_digits() < 5000:
            with self.assertRaisesRegex(rc.ContextError, "^context file is not valid JSON: "):
                rc.read_context(self.write(text))
        else:
            # Interpreters without the digit limit parse it; the value is still subject to assess_depth.
            self.assertEqual(len(str(rc.read_context(self.write(text))["x"])), 5000)


class SourceShape(unittest.TestCase):
    SOURCE = (ROOT / "lib" / "review_context.py").read_text(encoding="utf-8")

    def test_core_parses_as_python_3_9(self):
        ast.parse(self.SOURCE, feature_version=(3, 9))

    def test_no_network_model_or_process_imports(self):
        imported = set()
        for node in ast.walk(ast.parse(self.SOURCE)):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertFalse(imported & {"socket", "urllib", "http", "subprocess", "requests", "ssl", "patterns"})
        self.assertNotIn("read_asset(", self.SOURCE)
        self.assertNotIn("os.environ", self.SOURCE)


# ---------------------------------------------------------------- PROVIDER DOUBLE (not the real provider)

class DoublePatternError(Exception):
    def __init__(self, code, message, *, status="invalid"):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status

    def diagnostic(self):
        return {"code": self.code, "severity": "error", "status": self.status, "message": self.message}


def make_double(verify_status="ok", coverage_status="ok", clauses=None, fail_parse=None, verify_warning=False):
    """PROVIDER DOUBLE: records calls; its outputs are synthetic, never live acceptance evidence."""
    calls = []

    class Reader:
        def __init__(self):
            self.reads = []

        def read(self, path, *, kind, limit):
            self.reads.append((kind, Path(path)))
            data = Path(path).read_bytes()
            if len(data) > limit:
                raise DoublePatternError("resource_limit", "too big")
            return data

        def metrics(self):
            kinds = ("catalog", "bindings", "pattern", "asset", "manifest", "input")
            return {f"{kind}_reads": sum(1 for item, _ in self.reads if item == kind) for kind in kinds}

    def parser(name):
        def parse(value, *args, **kwargs):
            calls.append(name)
            if fail_parse == name:
                raise DoublePatternError("invalid_schema", f"{name} rejected")
            return ("parsed", name, value)
        return parse

    def parse_json(data, *, limit, what):
        calls.append(f"parse_json:{what}")
        return json.loads(data)

    warning = {"code": "pinned_deprecated", "severity": "warning", "message": "pinned x is deprecated"}

    def verify_lock(roots, lock, context, *, reader, attestations=()):
        calls.append(("verify_lock", attestations))
        if verify_status == "ok":
            diagnostics = [dict(warning)] if verify_warning else []
        else:
            diagnostics = [{"code": "context_changed", "severity": "error", "status": verify_status,
                            "message": "re-plan"}]
        return {"schema_version": 1, "status": verify_status, "diagnostics": diagnostics}

    def project_package(lock, task_map, package):
        calls.append(("project_package", package))
        return {"schema_version": 1, "status": "ok", "package": package, "tasks": task_map["tasks"],
                "clauses": clauses if clauses is not None else [], "settings": lock["settings"],
                "diagnostics": [{"code": "mapping_not_installed", "severity": "warning", "message": "map"}]}

    def review_coverage(roots, lock, context, evidence, *, attestations=(), reader=None):
        calls.append(("review_coverage", attestations))
        # Like the real provider, coverage re-reports its own verification diagnostics.
        diagnostics = [dict(warning)] if verify_warning else []
        if coverage_status != "ok":
            diagnostics.append({"code": "mandatory_unmet", "severity": "error", "status": coverage_status,
                                "message": "x"})
        return {"schema_version": 1, "status": coverage_status, "release_clearance": False, "clauses": [],
                "diagnostics": diagnostics}

    def read_asset(*args, **kwargs):
        raise AssertionError("the adapter must never read an asset automatically")

    double = types.SimpleNamespace(
        Reader=Reader, LIMITS=types.SimpleNamespace(input_bytes=256 * 1024, catalog_bytes=2 * 1024 * 1024),
        PatternError=DoublePatternError, parse_json=parse_json, parse_roots=parser("parse_roots"),
        parse_context=parser("parse_context"), parse_attestations=parser("parse_attestations"),
        verify_lock=verify_lock, project_package=project_package, review_coverage=review_coverage,
        read_asset=read_asset, fetch=read_asset)
    return double, calls


class PatternAdapter(unittest.TestCase):
    """All cases below use a PROVIDER DOUBLE or synthetic provider files, not the real provider."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.lock = {"settings": {"team.style": {"value": "strict", "clauses": ["x@1.0.0#A"]}},
                     "exceptions": [{"clause": "x@1.0.0#B", "reason": "approved waiver"}],
                     "asset_pins": [{"path": "docs/guide.md", "kind": "doc", "sha256": "0" * 64}]}
        self.files = {}
        for name, value in (("roots", {"schema_version": 1}), ("lock", self.lock), ("context", {"facts": {}}),
                            ("task_map", {"tasks": ["T1", "T2"]}), ("coverage", {"items": []}),
                            ("attestations", {"items": []})):
            path = self.tmp / f"{name}.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            self.files[name] = path

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def call(self, *, coverage=False, attestations=False, package="P1"):
        return rc.prepare_pattern_review(
            roots=self.files["roots"], lock=self.files["lock"], context=self.files["context"],
            task_map=self.files["task_map"], package=package,
            coverage=self.files["coverage"] if coverage else None,
            attestations=self.files["attestations"] if attestations else None)

    def assert_unavailable(self, result, code):
        self.assertEqual(result["status"], "unavailable")
        self.assertNotEqual(result["status"], "empty")
        self.assertFalse(result["provider"]["available"])
        self.assertEqual(result["provider"]["code"], code)
        self.assertEqual(result["diagnostics"][0]["code"], code)
        self.assertIsNone(result["projection"])
        self.assertIsNone(result["verification"])
        self.assertIsNone(result["metrics"])
        self.assertIs(result["release_clearance"], False)

    def test_absent_provider_is_unavailable_before_reading_inputs(self):
        for path in self.files.values():
            path.unlink()
        with rc._provider_path(self.tmp / "missing" / "patterns.py"):
            self.assert_unavailable(self.call(coverage=True), "provider_missing")

    def test_absent_provider_ignores_ambient_patterns_module(self):
        decoy = self.tmp / "ambient"
        decoy.mkdir()
        (decoy / "patterns.py").write_text("raise AssertionError('ambient import')\n", encoding="utf-8")
        sys.path.insert(0, str(decoy))
        sys.modules["patterns"] = types.SimpleNamespace(**vars(make_double()[0]))
        try:
            with rc._provider_path(self.tmp / "missing" / "patterns.py"):
                self.assert_unavailable(self.call(), "provider_missing")
        finally:
            sys.path.remove(str(decoy))
            sys.modules.pop("patterns", None)

    def test_old_python_is_unavailable(self):
        original = rc.PROVIDER_MIN_PYTHON
        rc.PROVIDER_MIN_PYTHON = (99, 0)
        try:
            with rc._provider_path(self.tmp / "patterns.py"):
                self.assert_unavailable(self.call(), "provider_python_unsupported")
        finally:
            rc.PROVIDER_MIN_PYTHON = original

    def test_broken_or_incompatible_provider_file_is_unavailable(self):
        broken = self.tmp / "broken" / "patterns.py"
        broken.parent.mkdir()
        broken.write_text("def broken(:\n", encoding="utf-8")
        with rc._provider_path(broken):
            self.assert_unavailable(self.call(), "provider_load_failed")
        self.assertNotIn(rc._MODULE_NAME, sys.modules)
        partial = self.tmp / "partial" / "patterns.py"
        partial.parent.mkdir()
        partial.write_text("def verify_lock(*args, **kwargs):\n    return {}\n", encoding="utf-8")
        with rc._provider_path(partial):
            result = self.call()
            self.assert_unavailable(result, "provider_incompatible")
            self.assertIn("project_package", result["provider"]["reason"])

    def test_loads_trusted_file_under_private_name_not_ambient(self):
        provider = self.tmp / "trusted" / "patterns.py"
        provider.parent.mkdir()
        provider.write_text("from dataclasses import dataclass\n@dataclass(frozen=True)\nclass Limits:\n"
                            "    input_bytes: int = 1\nMARK = 'trusted-file'\n", encoding="utf-8")
        sys.modules["patterns"] = types.SimpleNamespace(MARK="ambient")
        try:
            with rc._provider_path(provider):
                module, info = rc._load_provider()
            self.assertIsNone(module)
            self.assertEqual(info["code"], "provider_incompatible")
            self.assertEqual(sys.modules[rc._MODULE_NAME].MARK, "trusted-file")
            self.assertEqual(Path(sys.modules[rc._MODULE_NAME].__file__), provider)
        finally:
            sys.modules.pop("patterns", None)
            sys.modules.pop(rc._MODULE_NAME, None)
            rc._CACHE.update(path=None, module=None)

    def test_real_sibling_is_observed_absent_or_trusted(self):
        """Observed state of the real sibling; the real verify/project/review join stays coordinator T11."""
        sibling = ROOT / "lib" / "patterns.py"
        module, info = rc._load_provider()
        if not sibling.exists():
            self.assertIsNone(module)
            self.assertEqual(info["code"], "provider_missing")
            self.assert_unavailable(self.call(), "provider_missing")
            return
        if sys.version_info[:2] < rc.PROVIDER_MIN_PYTHON:
            self.assertEqual(info["code"], "provider_python_unsupported")
            self.assert_unavailable(self.call(), "provider_python_unsupported")
            return
        self.assertTrue(info["available"], info)
        self.assertEqual(Path(info["source"]), sibling.resolve())
        self.assertEqual(Path(module.__file__).resolve(), sibling.resolve())
        for name in rc.PROVIDER_API:
            self.assertTrue(callable(getattr(module, name)) or name == "LIMITS", name)

    def test_failed_verification_never_projects_or_reads_assets(self):
        for status in ("conflict", "unavailable", "needs-context"):
            with self.subTest(status=status):
                double, calls = make_double(verify_status=status)
                with rc._provider_double(double):
                    result = self.call(coverage=True, attestations=True)
                self.assertEqual(result["status"], status)
                self.assertIsNone(result["projection"])
                self.assertIsNone(result["coverage"])
                self.assertIsNone(result["exceptions"])
                self.assertIsNone(result["asset_refs"])
                self.assertEqual(result["diagnostics"][0]["code"], "context_changed")
                self.assertNotIn(("project_package", "P1"), calls)
                self.assertFalse([call for call in calls if isinstance(call, tuple) and call[0] == "review_coverage"])
                self.assertNotIn("parse_json:task map", calls)
                self.assertEqual(result["metrics"]["asset_reads"], 0)
                self.assertIs(result["release_clearance"], False)
                self.assertTrue(result["provider"]["double"])

    def test_verified_projection_is_verbatim_and_not_truncated(self):
        clauses = [{"clause": f"org.pattern@1.0.0#C{index:03d}", "level": "must", "state": "mandatory",
                    "text": "must " + "x" * 3000, "task_ids": ["T1"]} for index in range(300)]
        double, calls = make_double(clauses=clauses)
        with rc._provider_double(double):
            result = self.call()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["projection"]["clauses"], clauses)
        self.assertEqual(len(result["projection"]["clauses"]), 300)
        self.assertEqual(result["projection"]["settings"], self.lock["settings"])
        self.assertEqual(result["projection"]["tasks"], ["T1", "T2"])
        self.assertEqual(result["package"], "P1")
        self.assertEqual(result["exceptions"], self.lock["exceptions"])
        self.assertEqual(result["asset_refs"], self.lock["asset_pins"])
        self.assertEqual(result["metrics"]["asset_reads"], 0)
        self.assertEqual(result["metrics"]["input_reads"], 4)
        self.assertIsNone(result["coverage"])
        self.assertFalse(result["coverage_supplied"])
        self.assertEqual([item["code"] for item in result["diagnostics"]], ["mapping_not_installed"])
        order = [call if isinstance(call, str) else call[0] for call in calls]
        self.assertLess(order.index("verify_lock"), order.index("project_package"))
        self.assertLess(order.index("parse_roots"), order.index("verify_lock"))
        self.assertIs(result["release_clearance"], False)
        result["projection"]["clauses"].clear()
        self.assertEqual(len(clauses), 300)

    def test_coverage_status_propagates_and_never_clears(self):
        for status in ("ok", "review-unmet"):
            with self.subTest(status=status):
                double, calls = make_double(coverage_status=status)
                with rc._provider_double(double):
                    result = self.call(coverage=True, attestations=True)
                self.assertEqual(result["status"], status)
                self.assertTrue(result["coverage_supplied"])
                self.assertEqual(result["coverage"]["status"], status)
                self.assertIs(result["release_clearance"], False)
                attested = [call[1] for call in calls if isinstance(call, tuple)
                            and call[0] in ("verify_lock", "review_coverage")]
                self.assertEqual(attested, [("parsed", "parse_attestations", {"items": []})] * 2)
                self.assertIn("parse_json:evidence", calls)
                self.assertEqual(result["metrics"]["asset_reads"], 0)

    def test_verification_warnings_always_reach_top_level(self):
        for with_coverage in (False, True):
            with self.subTest(coverage=with_coverage):
                double, _ = make_double(verify_warning=True)
                with rc._provider_double(double):
                    result = self.call(coverage=with_coverage)
                codes = [item["code"] for item in result["diagnostics"]]
                self.assertEqual(result["status"], "ok")
                self.assertEqual(codes.count("pinned_deprecated"), 1)
                self.assertIn("mapping_not_installed", codes)
                self.assertEqual(result["verification"]["diagnostics"][0]["code"], "pinned_deprecated")
                if with_coverage:
                    self.assertEqual(result["coverage"]["diagnostics"][0]["code"], "pinned_deprecated")
        double, _ = make_double(verify_warning=True, coverage_status="review-unmet")
        with rc._provider_double(double):
            result = self.call(coverage=True)
        self.assertEqual([item["code"] for item in result["diagnostics"]],
                         ["pinned_deprecated", "mapping_not_installed", "mandatory_unmet"])
        self.assertEqual(result["status"], "review-unmet")

    def test_provider_errors_keep_their_status(self):
        double, calls = make_double(fail_parse="parse_roots")
        with rc._provider_double(double):
            result = self.call()
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["diagnostics"][0]["code"], "invalid_schema")
        self.assertIsNone(result["verification"])
        self.assertNotIn("verify_lock", [call[0] for call in calls if isinstance(call, tuple)])
        self.assertIsNotNone(result["metrics"])

    def test_arguments_are_required(self):
        double, _ = make_double()
        with rc._provider_double(double):
            for package in ("", "  ", None, 3):
                with self.subTest(package=package), self.assertRaises(rc.ContextError):
                    self.call(package=package)
            with self.assertRaises(rc.ContextError):
                rc.prepare_pattern_review(roots=None, lock=self.files["lock"], context=self.files["context"],
                                          task_map=self.files["task_map"], package="P1")
            with self.assertRaises(TypeError):
                rc.prepare_pattern_review(self.files["roots"])  # keyword-only inputs


if __name__ == "__main__":
    unittest.main(verbosity=1)
