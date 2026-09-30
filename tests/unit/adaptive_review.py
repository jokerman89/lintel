#!/usr/bin/env python3
# component: adaptive-review-tests
# implements: ADR-0040, ADR-0036
# intent: .claude/plans/adaptive-review/spec.md
# constraints: synthetic local packets only; no model, network or target execution
# last_intent_review: 2026-09-29
"""Mandatory/advisory obligations and exact-body parity across single and panel reviews."""
import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
import review_method as rm
import mars_contract as mc
import review_context as rc
import review_contract as evidence

PACKET = ROOT / "bin" / "li-review-packet.py"
MARS = ROOT / "bin" / "li-mars.py"


def make_packet(required=(), tags=()):
    questions = rm.select_questions(rm.load_catalog(), "implementation", tags, "quality")
    fields = dict(kind="implementation", stage="quality", subject_ref="fixture.py",
                  questions=questions, required_questions=required, tags=tags)
    body = rm.render_body(subject_text="def total(values): return sum(values)", **fields)
    return body, rm.method_meta(body=body, **fields)


def report(meta, statuses=None, prefix="review"):
    fields = [f"{prefix}: report", "version: 1", "stage: quality",
              f"brief_sha256: {meta['brief_sha256']}", "verdict: pass", "p1: 0",
              "p2: 0", "p3: 0", "confidence: 8", "read_only: attested",
              "self_reported_model: synthetic-fixture", "coverage: explicit selection"]
    if prefix == "mars":
        fields += ["panel: mandatory", "slot: r1", "round: 1"]
    rows = []
    for qid in meta["questions"]:
        status, detail = (statuses or {}).get(qid, ("checked", "Traced fixture.py:1 against its stated contract."))
        rows.append(f"| {qid} | {status} | {detail} |")
    return (f"```{prefix}-report\n" + "\n".join(fields) + "\n```\n\n"
            "## Intent\nReview a synthetic total function.\n\n"
            "## Standing questions\n| SQ | Status | Evidence |\n|---|---|---|\n"
            + "\n".join(rows) + "\n")


def run(*args):
    return subprocess.run([sys.executable, "-B", str(PACKET), *map(str, args)],
                          text=True, capture_output=True)


class ObligationTests(unittest.TestCase):
    def test_method_json_refuses_nonfinite_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "meta.json"
            for value in ("NaN", "Infinity", "-Infinity", "1e999"):
                path.write_text('{"value":' + value + "}", encoding="utf-8")
                with self.assertRaises(rm.MethodError):
                    rm.read_json(path)

    def test_shipped_catalog_defaults_to_advisory(self):
        questions = rm.load_catalog()["questions"]
        self.assertTrue(all(q.get("requirement", "advisory") == "advisory" for q in questions))
        self.assertEqual(rm.required_question_ids(questions), [])

    def test_dependency_applicability_and_obligations_are_not_scanner_rank(self):
        policy = {"required": False, "status": "not_required", "source": None,
                  "version": None, "applicability": "not_applicable"}
        def control(requirement, applicability, status, rank):
            return {
                "id": "dependency-fixture", "kind": "check", "requirement": requirement,
                "applicability": applicability, "status": status,
                "reason": f"Scanner rank {rank}; fixture applicability/evidence is supplied separately.",
                "policy": {"source": "fixture-policy.md", "version": "fixture-1",
                           "applicability": "Selected artifact and dependency scope",
                           "jurisdiction": None, "actor": None, "effective_date": None},
                "evidence": ["fixture-dependency-evidence.json"], "observation": {},
            }
        for requirement, applicability, status, rank, blocked in (
            ("mandatory", "not_applicable", "pass", "critical", False),
            ("mandatory", "unknown", "unverified", "low", True),
            ("mandatory", "applicable", "fail", "low", True),
            ("mandatory", "applicable", "error", "unknown", True),
            ("advisory", "applicable", "fail", "critical", False),
        ):
            with self.subTest(requirement=requirement, applicability=applicability, status=status):
                result = evidence.evaluate_controls(
                    [control(requirement, applicability, status, rank)], required_policy=policy)
                self.assertEqual(result["blocked"], blocked)
                if requirement == "advisory":
                    self.assertTrue(result["advisories"])
                if applicability == "not_applicable":
                    self.assertEqual(result["assurance"], "no_applicable_controls")
        pattern = control("mandatory", "applicable", "pass", "not-a-scanner")
        pattern["id"] = "pattern-clause"
        missing_license = control("mandatory", "unknown", "unverified", "unknown")
        missing_license["id"] = "required-license"
        missing_license["evidence"] = []
        combined = evidence.evaluate_controls([pattern, missing_license], required_policy=policy)
        self.assertTrue(combined["blocked"])
        self.assertIn("required-license", " ".join(combined["blockers"]))
        review = (ROOT / "skills/review/SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("P1: critical CVE or license blocker", review)
        self.assertIn("scanner rank alone", review)

    def test_explicit_obligations_cannot_be_unselected_or_superseded(self):
        questions = rm.select_questions(rm.load_catalog(), "implementation", [], "quality")
        for required in (["SQ-AUTH-01"], ["SQ-ABSENT-01"], ["SQ-U01", "SQ-U01"], "SQ-U01", [{}]):
            with self.assertRaises(rm.MethodError):
                rm.required_question_ids(questions, required)
        self.assertEqual(rm.required_question_ids(questions, ["SQ-U04", "SQ-U01"]), ["SQ-U01", "SQ-U04"])
        catalog = rm.load_catalog()
        catalog["questions"][0]["superseded_by"] = "SQ-U02"
        selected = rm.select_questions(catalog, "implementation", [], "quality")
        with self.assertRaises(rm.MethodError):
            rm.required_question_ids(selected, ["SQ-U01"])

    def test_approved_catalog_can_add_but_not_remove_an_obligation(self):
        with tempfile.TemporaryDirectory() as tmp:
            extension = Path(tmp) / "questions.json"
            question = {
                "id": "SQ-TEAM-01", "class": "domain", "applies_to": ["implementation"],
                "question": "Does the accepted domain invariant hold?",
                "evidence": "Its selected acceptance test.", "since": "2026-09-28",
                "requirement": "mandatory",
            }
            document = {"schema_version": 1, "namespace": "TEAM", "questions": [question]}
            extension.write_text(json.dumps(document), encoding="utf-8")
            catalog = rm.load_catalog(extensions=[extension])
            selected = rm.select_questions(catalog, "implementation", [], "quality")
            self.assertEqual(rm.required_question_ids(selected), ["SQ-TEAM-01"])
            question["requirement"] = "optional-if-fast"
            extension.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaises(rm.MethodError):
                rm.load_catalog(extensions=[extension])

    def test_mandatory_unknown_is_incomplete_and_advisory_unknown_is_visible(self):
        body, meta = make_packet(["SQ-U04"])
        for qid, outcome in (("SQ-U04", "incomplete"), ("SQ-U08", "pass")):
            reply = report(meta, {qid: ("not-checked", "Required observation was not available on this host.")})
            result = rm.check_report(reply, meta, packet_body=body)
            self.assertEqual(result["outcome"], outcome)
            self.assertIn(qid, result["coverage"]["not_checked"])
            self.assertEqual(result["coverage"]["required_unverified"], [qid] if qid == "SQ-U04" else [])
            self.assertFalse(result["release_clearance"])

    def test_grounded_question_na_is_not_a_policy_override(self):
        body, meta = make_packet(["SQ-U04"])
        reply = report(meta, {"SQ-U04": ("n/a", "Selected function is a pure local sum with no authority boundary.")})
        result = rm.check_report(reply, meta, packet_body=body)
        self.assertEqual(result["outcome"], "pass")
        self.assertFalse(result["release_clearance"])
        empty = report(meta, {"SQ-U04": ("n/a", "-")})
        self.assertEqual(rm.check_report(empty, meta, packet_body=body)["outcome"], "incomplete")

    def test_v2_requires_original_body_and_unchanged_inventory(self):
        body, meta = make_packet(["SQ-U04"])
        reply = report(meta)
        with self.assertRaises(rm.MethodError):
            rm.check_report(reply, meta)
        for mutate in ("delete", "empty", "unknown", "downgrade", "questions", "acceptance"):
            broken = copy.deepcopy(meta)
            if mutate == "delete":
                broken.pop("required_questions")
            elif mutate == "empty":
                broken["required_questions"] = []
            elif mutate == "unknown":
                broken["required_questions"] = ["SQ-ABSENT-01"]
            elif mutate == "downgrade":
                broken.update(schema_version=1, method_version="1")
            elif mutate == "questions":
                broken["questions"].remove("SQ-U08")
            else:
                broken["acceptance"] = ["invented-acceptance"]
            with self.assertRaises(rm.MethodError, msg=mutate):
                rm.check_report(reply, broken, packet_body=body)
        with self.assertRaises(rm.MethodError):
            rm.check_report(reply, meta, packet_body=body.replace("\n", "\r\n"))

    def test_legacy_meta_is_labeled_and_never_release_clearance(self):
        body, meta = make_packet()
        legacy = {key: value for key, value in meta.items() if key not in ("depth", "required_questions")}
        legacy.update(schema_version=1, method_version="1")
        result = rm.check_report(report(legacy), legacy)
        self.assertTrue(result["legacy_metadata"])
        self.assertFalse(result["release_clearance"])
        with self.assertRaises(rm.MethodError):
            rm.check_report(report(legacy), legacy, packet_body=body)

    def test_trigger_questions_stay_relevant(self):
        catalog = rm.load_catalog()
        base = {q["id"] for q in rm.select_questions(catalog, "implementation", [], "quality")}
        network = {q["id"] for q in rm.select_questions(catalog, "implementation", ["network"], "quality")}
        deep = {q["id"] for q in rm.select_questions(catalog, "implementation", ["deep-review"], "quality")}
        self.assertIn("SQ-U11", base)
        self.assertNotIn("SQ-NET-01", base)
        self.assertIn("SQ-NET-01", network)
        self.assertNotIn("SQ-MEM-01", network)
        self.assertIn("SQ-DEEP-01", deep)
        self.assertIn("SQ-REL-02", deep)
        self.assertEqual(len(base), 11)
        self.assertLessEqual(len(deep), len(base) + 3)


class PanelParityTests(unittest.TestCase):
    def test_mars_preserves_and_checks_the_same_obligations(self):
        body, meta = make_packet(["SQ-U04"])
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_bytes(body.encode("utf-8"))
            origin = {"requested_by": "fixture", "trigger": "explicit", "caller": "standalone",
                      "coordinator_surface": "test-host", "repository": "fixture/repo",
                      "branch": "fixture", "commit": "fixture"}
            panel = mc.new_panel("mandatory", "fixture-coordinator", brief, "fixture-consent",
                                 mc.load_defaults(), "implementation", origin, "fixture.py")
            mc.attach_method(panel, meta)
            mc.add_participant(panel, "r1", "fixture-model", "subagent", None, None, None)
            self.assertEqual(panel["subject"]["method"]["required_questions"], ["SQ-U04"])
            request, _ = mc.build_request(panel, "r1", 1, body, mc.load_schema())
            self.assertEqual(rm.strip_header(request), body)
            reply = report(meta, {"SQ-U04": ("not-checked", "Boundary evidence missing.")}, prefix="mars")
            result = Path(tmp) / "report.md"
            result.write_text(reply, encoding="utf-8")
            mc.record_round(panel, "r1", 1, result, schema=mc.load_schema())
            self.assertEqual(panel["participants"][0]["rounds"][0]["coverage"]["outcome"], "incomplete")
            single = rm.check_report(reply, meta, prefix="mars", packet_body=body)
            self.assertEqual(single["outcome"], "incomplete")
            broken = copy.deepcopy(panel)
            broken["subject"]["method"]["required_questions"] = []
            with self.assertRaises(mc.ContractError):
                mc.validate_panel(broken)
            broken["subject"]["method"].pop("required_questions")
            with self.assertRaises(mc.ContractError):
                mc.validate_panel(broken)

    def test_legacy_rewrite_cannot_remove_a_v2_mandatory_inventory(self):
        body, meta = make_packet(["SQ-U04"])
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_bytes(body.encode("utf-8"))
            panel = mc.new_panel("mandatory", "owner", brief, "fixture", mc.load_defaults(), "implementation")
            mc.attach_method(panel, meta)
            legacy = {"version": "1", "stage": "quality", "questions": meta["questions"],
                      "tags": meta["tags"], "acceptance": meta["acceptance"]}
            for method in (legacy, None, {}, [], "legacy"):
                broken = copy.deepcopy(panel)
                broken["subject"]["method"] = method
                with self.assertRaises(mc.ContractError, msg=method):
                    mc.validate_panel(broken)
                with self.assertRaises(mc.ContractError, msg=method):
                    mc.summary(broken)
            rewritten = copy.deepcopy(panel)
            rewritten["subject"]["method"] = legacy
            brief.write_bytes(body.replace("review-method v2", "review-method v1", 1).encode("utf-8"))
            with self.assertRaises(mc.ContractError):
                mc.validate_panel(rewritten)

    def test_relative_brief_is_anchored_and_cleanup_needs_no_review_clearance(self):
        body, meta = make_packet(["SQ-U04"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "brief.md").write_bytes(body.encode("utf-8"))
            (root / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
            panel_path = root / "panel.json"
            init = subprocess.run(
                [sys.executable, "-B", str(MARS), "panel", "init", "--panel", "panel.json",
                 "--id", "mandatory", "--owner", "owner", "--brief", "brief.md", "--consent", "fixture",
                 "--kind", "implementation", "--method-meta", "meta.json", "--requested-by", "fixture",
                 "--trigger", "explicit", "--caller", "standalone", "--surface", "test-host"], cwd=root,
                capture_output=True, text=True)
            self.assertEqual(init.returncode, 0, init.stderr)
            panel = json.loads(panel_path.read_text(encoding="utf-8"))
            self.assertTrue(Path(panel["subject"]["brief_path"]).is_absolute())
            elsewhere = root / "elsewhere"
            elsewhere.mkdir()
            summarized = subprocess.run(
                [sys.executable, "-B", str(MARS), "panel", "summary", "--panel", str(panel_path)],
                cwd=elsewhere, capture_output=True, text=True)
            self.assertEqual(summarized.returncode, 0, summarized.stderr)
            origin = subprocess.run(
                [sys.executable, "-B", str(MARS), "panel", "origin", "--panel", str(panel_path),
                 "--subject-ref", "docs/real-subject", "--requested-by", "fixture", "--trigger", "explicit",
                 "--caller", "standalone", "--surface", "test-host"], cwd=elsewhere, capture_output=True, text=True)
            self.assertEqual(origin.returncode, 0, origin.stderr)
            panel = json.loads(panel_path.read_text(encoding="utf-8"))
            self.assertEqual(panel["subject"]["ref"], "docs/real-subject")
            explicit = subprocess.run(
                [sys.executable, "-B", str(MARS), "panel", "origin", "--panel", str(panel_path),
                 "--subject-ref", "docs/another-subject", "--requested-by", "fixture", "--trigger", "explicit",
                 "--caller", "standalone", "--surface", "test-host"], cwd=elsewhere, capture_output=True, text=True)
            self.assertEqual(explicit.returncode, 0, explicit.stderr)
            self.assertEqual(json.loads(panel_path.read_text(encoding="utf-8"))["subject"]["ref"],
                             "docs/real-subject", "origin must not overwrite an explicit subject")
            mc.add_participant(panel, "r1", "fixture", "nested-session", "owned-child", None, None)
            panel["participants"][0]["state"] = "reported"
            panel_path.write_text(json.dumps(panel), encoding="utf-8")
            (root / "brief.md").unlink()
            closed = subprocess.run(
                [sys.executable, "-B", str(MARS), "panel", "close-plan", "--panel", str(panel_path),
                 "--owner", "owner"], cwd=elsewhere, capture_output=True, text=True)
            self.assertEqual(closed.returncode, 0, closed.stderr)
            self.assertEqual(json.loads(closed.stdout)["close"][0]["session_id"], "owned-child")
            with self.assertRaises(mc.ContractError):
                mc.close_plan(panel, "someone-else")
            with self.assertRaises(mc.ContractError):
                mc.summary(panel)


class PacketCliTests(unittest.TestCase):
    def test_depth_uses_raw_evidenced_facts_and_cannot_drop_critical_tags(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            risk = root / "risk.json"
            facts = {"deployment": "production", "exposure": "trusted", "impact": "reversible",
                     "behavior_change": True, "security_boundary": False, "blast_radius": "contained"}
            context = {"schema_version": 1, "facts": facts,
                       "evidence": {key: "accepted fixture scope" for key in facts},
                       "asserted_by": {"actor": "fixture-coordinator", "reference": "fixture task"}}
            risk.write_text(json.dumps(context), encoding="utf-8")
            refused = run("depth", "--risk-file", risk, "--depth", "lean")
            self.assertEqual(refused.returncode, 2, refused.stdout)
            self.assertIn("below the evidenced minimum", refused.stderr)
            selected = run("questions", "--kind", "implementation", "--stage", "quality",
                           "--risk-file", risk, "--tags", "")
            self.assertEqual(selected.returncode, 0, selected.stderr)
            result = json.loads(selected.stdout)
            self.assertEqual(result["depth"]["selected"], "deep")
            self.assertIn("SQ-DEEP-01", [q["id"] for q in result["questions"]])
            self.assertIn("SQ-REL-02", [q["id"] for q in result["questions"]])
            self.assertEqual(result["required_questions"], [], "depth never invents mandatory policy")
            risk.write_text(json.dumps(rc.assess_depth(context)), encoding="utf-8")
            invalid = run("depth", "--risk-file", risk)
            self.assertEqual(invalid.returncode, 2, "serialized assessments cannot replace evidenced input")
            unknown = run("depth")
            self.assertEqual(unknown.returncode, 3)
            self.assertEqual(json.loads(unknown.stdout)["selected"], "standard")

    def test_fact_evidence_and_actor_are_bound_to_packet_bytes(self):
        facts = {"deployment": "local", "exposure": "isolated", "impact": "reversible",
                 "behavior_change": False, "security_boundary": False, "blast_radius": "contained"}
        context = {"schema_version": 1, "facts": facts,
                   "evidence": {key: "fixture" for key in facts},
                   "asserted_by": {"actor": "fixture-coordinator", "reference": "fixture task"}}
        questions = rm.select_questions(rm.load_catalog(), "implementation", [], "quality")
        kwargs = dict(kind="implementation", stage="quality", subject_ref="fixture",
                      questions=questions, subject_text="pass")
        body = rm.render_body(**kwargs, depth=rc.assess_depth(context))
        changed = copy.deepcopy(context)
        changed["asserted_by"]["reference"] = "a different accepted scope"
        self.assertNotEqual(body, rm.render_body(**kwargs, depth=rc.assess_depth(changed)))
        changed = copy.deepcopy(context)
        changed["evidence"]["deployment"] = "a different observed deployment"
        self.assertNotEqual(body, rm.render_body(**kwargs, depth=rc.assess_depth(changed)))
        changed["asserted_by"]["actor"] = "actor\u202espoofed"
        safe = rm.render_body(**kwargs, depth=rc.assess_depth(changed))
        self.assertNotIn("\u202e", safe)
        self.assertIn("\\u202e", safe)

    def test_deep_inventory_and_metadata_fail_explicitly_without_tracebacks(self):
        body, meta = make_packet(["SQ-U04"])
        for depth in (1, 3000):
            with self.subTest(depth=depth), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                body_path, meta_path, reply = [root / name for name in ("body.md", "meta.json", "reply.md")]
                invalid = '{"nested":' + "[" * depth + "0" + "]" * depth + "}"
                # Valid JSON can reach schema validation on runtimes with a deeper decoder limit.
                try:
                    json.loads(invalid)
                except RecursionError:
                    inventory_error = r"^invalid JSON in packet obligation inventory: .+$"
                    metadata_error = rf"^invalid JSON in {re.escape(str(meta_path))}: .+$"
                else:
                    inventory_error = r"^invalid packet obligation inventory$"
                    metadata_error = r"^not a review-method meta record$"
                broken_body = (body.splitlines()[0] + "\n" + rm.INVENTORY_PREFIX
                               + invalid + rm.INVENTORY_SUFFIX + "\n")
                with self.assertRaisesRegex(rm.MethodError, inventory_error):
                    rm.validate_meta(meta, broken_body)
                body_path.write_bytes(broken_body.encode("utf-8"))
                reply.write_text(report(meta), encoding="utf-8")
                panel_path = root / "panel.json"
                for content, expected in ((json.dumps(meta), inventory_error), (invalid, metadata_error)):
                    with self.subTest(expected=expected):
                        meta_path.write_text(content, encoding="utf-8")
                        checked = run("check", "--body", body_path, "--meta", meta_path, "--report", reply)
                        mars = subprocess.run(
                            [sys.executable, "-B", str(MARS), "panel", "init", "--panel", str(panel_path),
                             "--id", "deep-input", "--owner", "fixture", "--brief", str(body_path),
                             "--consent", "fixture", "--method-meta", str(meta_path),
                             "--requested-by", "fixture", "--trigger", "explicit",
                             "--caller", "standalone", "--surface", "test-host"],
                            capture_output=True, text=True)
                        for command, result in (("check", checked), ("panel-init", mars)):
                            with self.subTest(command=command):
                                self.assertEqual(result.returncode, 2, result.stderr)
                                self.assertEqual(result.stdout, "")
                                self.assertNotIn("Traceback", result.stderr)
                                error = json.loads(result.stderr)
                                self.assertEqual(set(error), {"error"})
                                self.assertRegex(error["error"], expected)
                        self.assertFalse(panel_path.exists(), "invalid inputs must not create panel state")

    def test_cli_binds_explicit_obligations_and_original_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subject, body, meta, reply = [root / name for name in ("subject.md", "body.md", "meta.json", "reply.md")]
            subject.write_text("def total(values): return sum(values)\n", encoding="utf-8")
            rendered = run("--repo", root, "render", "--kind", "implementation", "--stage", "quality",
                           "--subject-file", subject, "--subject-ref", "fixture.py", "--body-out", body,
                           "--meta-out", meta, "--require-question", "SQ-U04")
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            data = json.loads(meta.read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], 2)
            reply.write_text(report(data, {"SQ-U04": ("not-checked", "No observation.")}), encoding="utf-8")
            checked = run("check", "--meta", meta, "--body", body, "--report", reply)
            self.assertEqual(checked.returncode, 3, checked.stderr)
            self.assertEqual(json.loads(checked.stdout)["outcome"], "incomplete")
            self.assertEqual(run("check", "--meta", meta, "--report", reply).returncode, 2)
            body.write_bytes(body.read_bytes().replace(b"\n", b"\r\n"))
            self.assertEqual(run("check", "--meta", meta, "--body", body, "--report", reply).returncode, 2)


class IntegrationShapeTests(unittest.TestCase):
    def test_shared_workflow_joins_and_bounded_references(self):
        for name in ("review", "code-review", "cross-check", "build", "sc"):
            text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8-sig")
            self.assertIn("references/adaptive.md", text, name)
        for name in ("adaptive", "security", "sources", "evaluation", "method"):
            path = ROOT / "skills" / "review" / "references" / f"{name}.md"
            self.assertLess(path.stat().st_size, 20_000, name)
        text = (ROOT / "skills" / "review" / "references" / "method.md").read_text(encoding="utf-8-sig")
        self.assertIn('--body "$run/inputs/brief.md"', text)
        self.assertIn("mandatory", text)
        self.assertIn("not-checked", text)


if __name__ == "__main__":
    unittest.main(verbosity=1)
