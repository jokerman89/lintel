#!/usr/bin/env python3
# component: mars-contract-tests
# implements: ADR-0036
# intent: .claude/plans/mars/spec.md
# constraints: hermetic temp dirs; no sessions, models or network
# last_intent_review: 2026-09-25
"""Behavior tests for MARS roster, offer gate and panel ownership/close state."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "lib"))
import mars_contract as mc  # noqa: E402

HOST = ROOT / "tests" / "fixtures" / "mars" / "copilot-app-host-2026-09-24.json"
CLI = ROOT / "bin" / "li-mars.py"
OWNER = "owner-session"


class RosterTests(unittest.TestCase):
    def setUp(self):
        self.defaults = mc.load_defaults()
        self.host = mc.read_json(HOST)

    def test_latest_per_family_prefers_opus_and_clamps_effort(self):
        result = mc.resolve_settings(self.host, self.defaults)
        picked = {e["family"]: e for e in result["roster"]}
        self.assertEqual(picked["claude"]["model"], "claude-opus-5.5")
        self.assertEqual(picked["gpt"]["model"], "gpt-6-astra")
        self.assertEqual(picked["grok"]["model"], "grok-4.7")
        self.assertEqual(picked["mai"]["model"], "mai-code-1.1-flash")
        self.assertEqual(picked["claude"]["effort"], "xhigh")
        self.assertEqual(picked["grok"]["effort"], "high")
        self.assertTrue(picked["grok"]["downgraded"])
        self.assertEqual(picked["mai"]["context_tier"], "default")
        self.assertTrue(result["eligible"])

    def test_opus_outranks_newer_sonnet_and_haiku_is_excluded(self):
        models = ["claude-sonnet-9", "claude-opus-5", "claude-haiku-9"]
        result = mc.resolve_roster(models, self.defaults, ["claude"])
        self.assertEqual(result["roster"][0]["model"], "claude-opus-5")

    def test_opus_replacement_falls_back_to_newest_flagship(self):
        result = mc.resolve_roster(["claude-sonnet-6", "claude-sonnet-5", "claude-haiku-7"],
                                   self.defaults, ["claude"])
        self.assertEqual(result["roster"][0]["model"], "claude-sonnet-6")

    def test_newer_generation_wins_and_mini_fast_are_excluded(self):
        result = mc.resolve_roster(["gpt-7-luna", "gpt-6-astra", "gpt-8-mini", "gpt-7.5-sol-fast"],
                                   self.defaults, ["gpt"])
        self.assertEqual(result["roster"][0]["model"], "gpt-7-luna")

    def test_support_for_more_families_and_missing_family_is_reported(self):
        result = mc.resolve_roster(list(self.host["models"]), self.defaults,
                                   ["claude", "gpt", "grok", "mai", "gemini", "llama"])
        self.assertEqual(len(result["roster"]), 5)
        self.assertEqual(result["missing_families"], ["llama"])

    def test_single_family_is_not_multi_model(self):
        result = mc.resolve_roster(["claude-opus-5.5"], self.defaults)
        self.assertFalse(result["eligible"])


class OfferTests(unittest.TestCase):
    def setUp(self):
        self.defaults = mc.load_defaults()
        host = mc.read_json(HOST)
        self.request = {"caller": "cycle", "route": list(mc.CANONICAL_ROUTE),
                        "checkpoint": "PLAN-approval",
                        "host": {**{k: host[k] for k in ("per_child_model", "separate_contexts",
                                                          "delegate_permission", "identity_evidence")},
                                 "models": list(host["models"])}}

    def decide(self, **changes):
        request = copy.deepcopy(self.request)
        for key, value in changes.items():
            if key.startswith("host_"):
                request["host"][key[5:]] = value
            elif value is None:
                request.pop(key, None)
            else:
                request[key] = value
        return mc.offer_decision(request, self.defaults)

    def test_full_cycle_on_capable_host_offers_but_never_consents(self):
        decision = self.decide()
        self.assertTrue(decision["offer"], decision)
        self.assertFalse(decision["dispatch"])
        self.assertTrue(decision["consent_required"])

    def test_partial_or_rerouted_cycle_does_not_offer(self):
        for route in (["SENSE", "BUILD", "REVIEW", "SHIP"], mc.CANONICAL_ROUTE[:-1],
                      list(reversed(mc.CANONICAL_ROUTE)), []):
            self.assertIn("cycle-route-not-full", self.decide(route=route)["reasons"])

    def test_nested_review_in_cycle_cannot_offer_early(self):
        self.assertIn("not-cycle-checkpoint", self.decide(checkpoint="REVIEW")["reasons"])

    def test_capability_gaps_suppress_offer(self):
        self.assertIn("no-per-child-model-selection", self.decide(host_per_child_model=False)["reasons"])
        self.assertIn("identity-unobservable", self.decide(host_identity_evidence="self-report")["reasons"])
        self.assertIn("delegation-not-allowed", self.decide(host_delegate_permission="ask")["reasons"])
        self.assertIn("fewer-than-two-models", self.decide(host_models=["gpt-6-astra"])["reasons"])

    def test_decline_participant_and_dry_run_never_reoffer(self):
        for flag, reason in (("declined", "already-declined"), ("is_participant", "participant-cannot-offer"),
                             ("dry_run", "dry-run"), ("already_offered", "already-offered")):
            self.assertIn(reason, self.decide(**{flag: True})["reasons"])

    def test_standalone_review_can_offer_without_a_cycle(self):
        decision = self.decide(caller="review", route=None, checkpoint=None)
        self.assertTrue(decision["offer"], decision)


ORIGIN = {"requested_by": "operator via owner-session", "trigger": "explicit", "caller": "standalone",
          "coordinator_surface": "copilot-app", "repository": "example/repo", "branch": "feature",
          "commit": "a" * 40}


def report_text(panel, slot_id, round_no, **overrides):
    fields = {"mars": "report", "version": 1, "panel": panel["panel_id"], "slot": slot_id, "round": round_no,
              "brief_sha256": panel["subject"]["brief_sha256"], "verdict": "block", "p1": 1, "p2": 0,
              "p3": 0, "confidence": 9, "read_only": "attested", "self_reported_model": "unknown",
              "coverage": "all three functions"}
    fields.update(overrides)
    lines = "\n".join(f"{k}: {v}" for k, v in fields.items() if v is not None)
    return f"```mars-report\n{lines}\n```\n\n## Findings\n\nF1 P1 conf 9 util.py:3\n"


class PanelTests(unittest.TestCase):
    def setUp(self):
        self.defaults = mc.load_defaults()
        self.schema = mc.load_schema()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.brief = self.root / "brief.md"
        self.brief.write_text("synthetic brief\n", encoding="utf-8")
        self.panel = mc.new_panel("p1", OWNER, self.brief, "operator turn", self.defaults,
                                  "code-review", ORIGIN, "synthetic util.py")
        for slot, model, session in (("r1", "claude-opus-5.5", "s1"), ("r2", "gpt-6-astra", "s2"),
                                     ("r3", "grok-4.7", "s3")):
            mc.add_participant(self.panel, slot, model, "nested-session", session, "xhigh", "long_context")
        mc.add_participant(self.panel, "r4", "mai-code-1.1-flash", "subagent", None, "high", "default")
        self.count = 0

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, text):
        self.count += 1
        path = self.root / f"report-{self.count}.md"
        path.write_text(text, encoding="utf-8")
        return path

    def rec(self, slot, round_no, **overrides):
        path = self.write(report_text(self.panel, slot, round_no, **overrides))
        mc.record_round(self.panel, slot, round_no, path, schema=self.schema)
        return path

    def test_consent_reference_is_required(self):
        with self.assertRaises(mc.ContractError):
            mc.new_panel("p2", OWNER, self.brief, " ", self.defaults)

    def test_close_plan_lists_only_owned_collected_nested_sessions(self):
        self.rec("r1", 1)
        self.rec("r4", 1)
        plan = mc.close_plan(self.panel, OWNER)
        self.assertEqual(plan["close"], [{"slot": "r1", "session_id": "s1"}])
        self.assertEqual({entry["slot"] for entry in plan["keep"]}, {"r2", "r3", "r4"})

    def test_foreign_owner_cannot_close_anything(self):
        with self.assertRaises(mc.ContractError):
            mc.close_plan(self.panel, "someone-else")
        with self.assertRaises(mc.ContractError):
            mc.mark_closed(self.panel, "r1", "someone-else")

    def test_tampered_spawner_or_owner_participant_is_refused(self):
        self.rec("r2", 1)
        self.panel["participants"][1]["spawned_by"] = "other-coordinator"
        self.assertEqual(mc.close_plan(self.panel, OWNER)["close"], [])
        self.panel["participants"][0]["session_id"] = OWNER
        with self.assertRaises(mc.ContractError):
            mc.validate_panel(self.panel)

    def test_duplicate_session_and_budget_limits(self):
        with self.assertRaises(mc.ContractError):
            mc.add_participant(self.panel, "r5", "gemini-3.8-flash", "nested-session", "s1", None, None)
        self.panel["participants"].pop()
        self.rec("r1", 1)
        self.rec("r1", 2)
        with self.assertRaises(mc.ContractError):
            self.rec("r1", 3)

    def test_rounds_are_sequential_and_bound_to_brief(self):
        with self.assertRaises(mc.ContractError):
            self.rec("r2", 2)
        with self.assertRaises(mc.ContractError):
            mc.record_round(self.panel, "r2", 1, self.write(report_text(self.panel, "r2", 1)),
                            brief_sha256="0" * 64, schema=self.schema)

    def test_summary_is_partial_until_all_report_and_never_clears(self):
        self.rec("r1", 1)
        mc.observe_identity(self.panel, "r1", "claude-opus-5.5", "host-usage")
        partial = mc.summary(self.panel)
        self.assertEqual(partial["operational_status"], "partial")
        self.assertFalse(partial["multi_model_verified"])
        for slot in ("r2", "r3", "r4"):
            self.rec(slot, 1)
        summary = mc.summary(self.panel)
        self.assertEqual(summary["operational_status"], "complete")
        self.assertFalse(summary["multi_model_verified"])
        self.assertFalse(summary["release_clearance"])
        for slot, model in (("r1", "claude-opus-5.5"), ("r2", "gpt-6-astra"), ("r3", "grok-4.7"),
                            ("r4", "mai-code-1.1-flash")):
            mc.observe_identity(self.panel, slot, model, "host-usage")
        self.assertTrue(mc.summary(self.panel)["multi_model_verified"])
        self.rec("r1", 2)
        self.assertEqual(mc.summary(self.panel)["operational_status"], "partial",
                         "a round that only some slots completed is partial")
        for slot in ("r2", "r3"):
            self.rec(slot, 2)
        mc.record_round(self.panel, "r4", 2, self.write("no header"), status="failed", schema=self.schema)
        self.assertEqual(mc.summary(self.panel)["operational_status"], "partial",
                         "a failed challenge report keeps the panel partial")

    def test_closing_marks_panel_closed_and_prevents_reclose(self):
        for slot in ("r1", "r2", "r3"):
            self.rec(slot, 1)
            mc.mark_closed(self.panel, slot, OWNER)
        self.assertEqual(self.panel["status"], "closed")
        with self.assertRaises(mc.ContractError):
            mc.mark_closed(self.panel, "r1", OWNER)


class HeaderTests(PanelTests.__bases__[0]):
    def setUp(self):
        PanelTests.setUp(self)

    tearDown = PanelTests.tearDown
    write = PanelTests.write
    rec = PanelTests.rec

    def test_request_header_carries_origin_coordinator_and_settings(self):
        text, fields = mc.build_request(self.panel, "r1", 1, "Subject body", self.schema)
        parsed = mc.validate_header("request", mc.parse_header(text, "request"), self.schema)
        self.assertEqual(parsed["requested_by"], "operator via owner-session")
        self.assertEqual(parsed["coordinator_session"], OWNER)
        self.assertEqual(parsed["round_type"], "blind")
        self.assertEqual(parsed["reasoning_effort"], "xhigh")
        self.assertEqual(parsed["context_tier"], "long_context")
        self.assertEqual(parsed["brief_sha256"], self.panel["subject"]["brief_sha256"])
        self.assertTrue(text.rstrip().endswith("Subject body"))

    def test_challenge_request_requires_received_previous_round(self):
        with self.assertRaises(mc.ContractError):
            mc.build_request(self.panel, "r1", 2, "matrix", self.schema)
        self.rec("r1", 1)
        _, fields = mc.build_request(self.panel, "r1", 2, "matrix", self.schema)
        self.assertEqual(fields["round_type"], "challenge")

    def test_request_needs_complete_origin(self):
        self.panel["origin"]["requested_by"] = None
        with self.assertRaises(mc.ContractError):
            mc.build_request(self.panel, "r1", 1, "body", self.schema)

    def test_report_header_is_parsed_into_the_round(self):
        self.rec("r2", 1, verdict="concerns", p1=0, p2=2, p3=1, self_reported_model="gpt-6-astra")
        entry = self.panel["participants"][1]["rounds"][0]
        self.assertEqual(entry["header"], "v1")
        self.assertEqual(entry["verdict"], "concerns")
        self.assertEqual(entry["counts"], {"p1": 0, "p2": 2, "p3": 1})
        self.assertEqual(self.panel["participants"][1]["identity_evidence"], "requested-only")

    def test_bad_report_headers_are_refused(self):
        cases = [dict(slot_override="r3"), dict(round=2), dict(brief_sha256="f" * 64),
                 dict(verdict="lgtm"), dict(read_only="maybe"), dict(p1="many"), dict(coverage=None),
                 dict(extra_key="x")]
        for case in cases:
            slot = case.pop("slot_override", None)
            text = report_text(self.panel, "r1", 1, **({"slot": slot} if slot else {}), **case)
            with self.assertRaises(mc.ContractError, msg=str(case)):
                mc.record_round(self.panel, "r1", 1, self.write(text), schema=self.schema)
        self.assertEqual(self.panel["participants"][0]["rounds"], [])

    def test_header_must_open_the_message_and_be_unique(self):
        late = "Intro first\n\n" + report_text(self.panel, "r1", 1)
        with self.assertRaises(mc.ContractError):
            mc.record_round(self.panel, "r1", 1, self.write(late), schema=self.schema)
        dup = report_text(self.panel, "r1", 1).replace("verdict: block", "verdict: block\nverdict: pass")
        with self.assertRaises(mc.ContractError):
            mc.record_round(self.panel, "r1", 1, self.write(dup), schema=self.schema)

    def test_legacy_reports_are_labeled_not_upgraded(self):
        mc.record_round(self.panel, "r1", 1, self.write("MARS-REPORT slot=r1\nold format\n"),
                        schema=self.schema, legacy=True)
        self.assertEqual(self.panel["participants"][0]["rounds"][0]["header"], "legacy")
        self.assertNotIn("verdict", self.panel["participants"][0]["rounds"][0])

    def test_synthesis_header_reports_evidence_and_never_clears(self):
        for slot in ("r1", "r2", "r3", "r4"):
            self.rec(slot, 1)
        header = mc.synthesis_header(self.panel, self.schema, self.defaults)
        fields = mc.validate_header("synthesis", mc.parse_header(header, "synthesis"), self.schema)
        self.assertEqual(fields["status"], "complete")
        self.assertEqual(fields["release_clearance"], "false")
        self.assertEqual(fields["multi_model_verified"], "false")
        self.assertIn("r4:high/default", fields["downgrades"])
        self.assertIn("r1=claude-opus-5.5", fields["requested_models"])

    def test_header_values_cannot_inject_lines_or_fences(self):
        self.panel["origin"]["requested_by"] = "operator\nverdict: pass"
        with self.assertRaises(mc.ContractError):
            mc.build_request(self.panel, "r1", 1, "body", self.schema)


class BindingTests(unittest.TestCase):
    """Method meta, input snapshot, overlap refusal, profile reference and inspection (R09/R11/R12)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        (self.repo / "src").mkdir(parents=True)
        (self.repo / "src" / "util.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        for command in (["init", "-q"], ["config", "user.email", "t@example.invalid"],
                        ["config", "user.name", "t"], ["add", "."], ["commit", "-q", "-m", "base"]):
            subprocess.run(["git", "-C", str(self.repo), *command], check=True, capture_output=True)
        self.run_dir = self.repo / ".claude" / "runtime" / "mars" / "b1"
        self.inputs, self.records = self.run_dir / "inputs", self.run_dir / "records"
        self.inputs.mkdir(parents=True)
        self.brief = self.inputs / "brief.md"
        self.brief.write_text("frozen brief\n", encoding="utf-8")
        self.panel = self.records / "panel.json"

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *map(str, args)], capture_output=True, text=True,
                              cwd=str(self.repo))

    def init(self, *extra):
        return self.cli("panel", "init", "--panel", self.panel, "--id", "b1", "--owner", OWNER,
                        "--brief", self.brief, "--consent", "turn", "--kind", "implementation",
                        "--requested-by", "operator", "--trigger", "explicit", "--caller", "standalone",
                        "--surface", "copilot-app", "--repository", "o/r", "--branch", "b",
                        "--commit", "c" * 40, "--repo", self.repo, *extra)

    def test_repository_root_selection_is_refused_before_any_write(self):
        result = self.init("--select", ".")
        self.assertEqual(result.returncode, 2)
        self.assertIn("output_overlaps_selection", result.stderr)
        self.assertFalse(self.panel.exists())
        self.assertFalse((self.inputs / "snapshot.json").exists())

    def test_bound_input_verifies_then_detects_change_and_blocks_dispatch(self):
        made = self.init("--select", "src")
        self.assertEqual(made.returncode, 0, made.stderr)
        self.assertTrue((self.inputs / "snapshot.json").is_file())
        self.assertEqual(self.cli("panel", "add", "--panel", self.panel, "--slot", "r1", "--model", "m-a",
                                  "--transport", "subagent").returncode, 0)
        verified = self.cli("panel", "verify-input", "--panel", self.panel)
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertEqual(json.loads(verified.stdout)["status"], "verified")
        request = self.records / "r1.request.md"
        brief = self.cli("panel", "brief", "--panel", self.panel, "--slot", "r1", "--round", "1",
                         "--body", self.brief, "--out", request)
        self.assertEqual(brief.returncode, 0, brief.stderr)
        self.assertIn("snapshot_digest:", request.read_text(encoding="utf-8"))
        (self.repo / "src" / "util.py").write_text("def f():\n    return 2\n", encoding="utf-8")
        changed = self.cli("panel", "verify-input", "--panel", self.panel)
        self.assertEqual(changed.returncode, 3)
        self.assertEqual(json.loads(changed.stdout)["changed_paths"], ["src/util.py"])
        again = self.cli("panel", "brief", "--panel", self.panel, "--slot", "r1", "--round", "1",
                         "--body", self.brief, "--out", self.records / "again.md")
        self.assertEqual(again.returncode, 2)
        self.assertIn("input_changed", again.stderr)

    def test_round_one_body_must_be_the_frozen_brief(self):
        self.assertEqual(self.init().returncode, 0)
        self.cli("panel", "add", "--panel", self.panel, "--slot", "r1", "--model", "m-a", "--transport", "subagent")
        other = self.inputs / "other.md"
        other.write_text("a different body\n", encoding="utf-8")
        result = self.cli("panel", "brief", "--panel", self.panel, "--slot", "r1", "--round", "1",
                          "--body", other, "--out", self.records / "r1.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("frozen brief", result.stderr)

    def test_profile_reference_is_recorded_validated_or_explicitly_absent(self):
        self.assertEqual(self.init().returncode, 0)
        self.assertEqual(mc.read_json(self.panel)["profile_status"], "none-selected")
        self.panel.unlink()
        reference = {"schema_version": 1, "context_id": "ctx-1", "generation": 1,
                     "digest": "sha256:" + "a" * 64, "name": "_default", "version": "1.0.0"}
        ref_path = Path(self.tmp.name) / "ref.json"
        ref_path.write_text(json.dumps(reference), encoding="utf-8")
        self.assertEqual(self.init("--profile-ref", ref_path).returncode, 0)
        self.assertEqual(mc.read_json(self.panel)["profile"], reference)
        self.panel.unlink()
        ref_path.write_text(json.dumps({**reference, "generation": 0}), encoding="utf-8")
        self.assertEqual(self.init("--profile-ref", ref_path).returncode, 2)

    def test_method_meta_links_questions_and_coverage(self):
        sys.path.insert(0, str(ROOT / "lib"))
        import review_method as rm
        catalog = rm.load_catalog()
        questions = rm.select_questions(catalog, "implementation", [], "quality")
        body = rm.render_body(kind="implementation", stage="quality", subject_ref="src/util.py",
                              subject_text="def f(): return 1", questions=questions)
        self.brief.write_bytes(body.encode("utf-8"))
        meta = rm.method_meta(kind="implementation", stage="quality", subject_ref="src/util.py", body=body,
                              questions=questions)
        meta_path = self.inputs / "method.json"
        meta_path.write_text(json.dumps({**meta, "brief_sha256": "0" * 64}), encoding="utf-8")
        self.assertEqual(self.init("--method-meta", meta_path).returncode, 2)
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        self.assertEqual(self.init("--method-meta", meta_path).returncode, 0, "valid meta")
        panel = mc.read_json(self.panel)
        self.assertEqual(panel["subject"]["method"]["questions"], meta["questions"])
        mc.add_participant(panel, "r1", "m-a", "subagent", None, None, None)
        schema = mc.load_schema()
        rows = "\n".join(f"| {q} | checked | traced src/util.py:1 |" for q in meta["questions"][1:])
        text = report_text(panel, "r1", 1, verdict="pass", p1=0) + \
            f"\n## Standing questions\n| SQ | Status | Evidence |\n|---|---|---|\n{rows}\n"
        path = self.records / "r1-round1.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        mc.record_round(panel, "r1", 1, path, schema=schema)
        entry = panel["participants"][0]["rounds"][0]
        self.assertFalse(entry["coverage"]["complete"])
        self.assertEqual(entry["coverage"]["incomplete"], [meta["questions"][0]])
        self.assertFalse(mc.summary(panel)["coverage_complete"])
        header = mc.validate_header("synthesis", mc.parse_header(
            mc.synthesis_header(panel, schema, mc.load_defaults(), [0, 0, 1]), "synthesis"), schema)
        self.assertEqual(header["outcome"], "incomplete")
        self.assertEqual(header["coverage_complete"], "false")

    def test_outcome_and_inspection_follow_the_shared_rule_and_never_clear(self):
        self.assertEqual(self.init("--select", "src").returncode, 0)
        panel = mc.read_json(self.panel)
        schema, defaults = mc.load_schema(), mc.load_defaults()
        for slot, model in (("r1", "m-a"), ("r2", "m-b")):
            mc.add_participant(panel, slot, model, "subagent", None, None, None)
            path = self.records / f"{slot}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(report_text(panel, slot, 1), encoding="utf-8")
            mc.record_round(panel, slot, 1, path, schema=schema)
        verified = mc.verify_input(panel)
        for counts, outcome in (([1, 0, 0], "fail"), ([0, 2, 0], "changes-requested"), ([0, 0, 3], "pass")):
            header = mc.synthesis_header(panel, schema, defaults, counts, verified)
            fields = mc.validate_header("synthesis", mc.parse_header(header, "synthesis"), schema)
            self.assertEqual(fields["outcome"], outcome)
            self.assertEqual(fields["input"], "verified")
        synthesis = mc.synthesis_header(panel, schema, defaults, [0, 0, 3], verified) + "\n## Agreed\n"
        record = mc.inspection_record(panel, synthesis, schema, verified)
        self.assertEqual((record["purpose"], record["release_clearance"]), ("inspection", False))
        self.assertEqual(record["snapshot"]["result_digest"], panel["subject"]["input"]["snapshot_digest"])
        self.assertEqual(record["outcome"], "pass")
        (self.repo / "src" / "util.py").write_text("changed\n", encoding="utf-8")
        changed = mc.verify_input(panel)
        self.assertEqual(changed["status"], "changed")
        with self.assertRaises(mc.ContractError):
            mc.inspection_record(panel, synthesis, schema, changed)
        stale = mc.validate_header("synthesis", mc.parse_header(
            mc.synthesis_header(panel, schema, defaults, [0, 0, 0], changed), "synthesis"), schema)
        self.assertEqual((stale["input"], stale["outcome"]), ("changed", "incomplete"))

    def method_panel(self, stage, acceptance, slots):
        """A panel whose round-1 reports are real method reports, plus the same text for a single check."""
        sys.path.insert(0, str(ROOT / "lib"))
        import review_method as rm
        questions = rm.select_questions(rm.load_catalog(), "implementation", [], stage)
        body = rm.render_body(kind="implementation", stage=stage, subject_ref="src/util.py",
                              subject_text="def f(): return 1", questions=questions, acceptance=acceptance)
        self.brief.write_bytes(body.encode("utf-8"))
        meta = rm.method_meta(kind="implementation", stage=stage, subject_ref="src/util.py", body=body,
                              questions=questions, acceptance=acceptance)
        panel = mc.new_panel("m1", OWNER, self.brief, "turn", mc.load_defaults(), "implementation", ORIGIN, "x")
        mc.attach_method(panel, meta)
        schema = mc.load_schema()
        texts = {}
        for slot, (verdict, counts, spec_rows) in slots.items():
            mc.add_participant(panel, slot, f"model-{slot}", "subagent", None, None, None)
            text = report_text(panel, slot, 1, verdict=verdict, p1=counts[0], p2=counts[1], p3=counts[2])
            if spec_rows is not None:
                text += "\n## Spec compliance\n| ID | Result | Location | Evidence |\n|---|---|---|---|\n" + \
                    "".join(f"| {key} | {value} | src/util.py:1 | traced |\n" for key, value in spec_rows)
            text += "\n## Standing questions\n| SQ | Status | Evidence |\n|---|---|---|\n" + \
                "".join(f"| {q['id']} | checked | traced src/util.py:1 |\n" for q in questions)
            path = self.records / f"{slot}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode("utf-8"))
            mc.record_round(panel, slot, 1, path, schema=schema)
            texts[slot] = text
        return rm, meta, panel, schema, texts

    def panel_outcome(self, panel, schema, counts):
        header = mc.synthesis_header(panel, schema, mc.load_defaults(), counts, mc.verify_input(panel))
        return mc.validate_header("synthesis", mc.parse_header(header, "synthesis"), schema)["outcome"]

    def test_panel_and_single_reach_the_same_outcome_for_the_same_reports(self):
        """S1: spec rows, unable verdicts and deviations count identically in both modes."""
        cases = (
            ("spec", ["R01", "R02"], ("pass", (0, 0, 0), []), [0, 0, 0, 0], "incomplete"),
            ("quality", [], ("unable", (0, 0, 0), None), [0, 0, 0], "incomplete"),
            ("spec", ["R01"], ("concerns", (0, 0, 0), [("R01", "deviation")]), [0, 0, 0, 1], "changes-requested"),
            ("spec", ["R01"], ("pass", (0, 0, 0), [("R01", "pass")]), [0, 0, 0, 0], "pass"),
        )
        for stage, acceptance, slot_report, adjudicated, expected in cases:
            for leftover in self.records.glob("*.md"):
                leftover.unlink()
            rm, meta, panel, schema, texts = self.method_panel(stage, acceptance, {"r1": slot_report, "r2": slot_report})
            single = rm.check_report(texts["r1"], meta, prefix="mars")
            self.assertEqual(single["outcome"], expected, (stage, slot_report))
            self.assertEqual(self.panel_outcome(panel, schema, adjudicated), expected, (stage, slot_report))
            if acceptance:
                with self.assertRaises(mc.ContractError, msg="deviations may not be omitted"):
                    self.panel_outcome(panel, schema, adjudicated[:3])

    def test_inspection_recomputes_the_outcome_and_review_callers_need_binding(self):
        self.assertEqual(self.init("--select", "src").returncode, 0)
        panel = mc.read_json(self.panel)
        schema, defaults = mc.load_schema(), mc.load_defaults()
        for slot in ("r1", "r2"):
            mc.add_participant(panel, slot, f"m-{slot}", "subagent", None, None, None)
            path = self.records / f"{slot}.md"
            path.write_text(report_text(panel, slot, 1), encoding="utf-8")
            mc.record_round(panel, slot, 1, path, schema=schema)
        verified = mc.verify_input(panel)
        synthesis = mc.synthesis_header(panel, schema, defaults, [1, 0, 0], verified)
        self.assertEqual(mc.inspection_record(panel, synthesis, schema, verified)["outcome"], "fail")
        with self.assertRaises(mc.ContractError):
            mc.inspection_record(panel, synthesis.replace("outcome: fail", "outcome: pass"), schema, verified)
        panel["origin"]["caller"] = "review"
        with self.assertRaises(mc.ContractError):
            mc.inspection_record(panel, synthesis, schema, verified)
        unbound = mc.new_panel("u1", OWNER, self.brief, "turn", defaults, "implementation", ORIGIN, "x")
        mc.add_participant(unbound, "r1", "m-a", "subagent", None, None, None)
        path = self.records / "u1.md"
        path.write_text(report_text(unbound, "r1", 1, verdict="pass", p1=0), encoding="utf-8")
        mc.record_round(unbound, "r1", 1, path, schema=schema)
        header = mc.validate_header("synthesis", mc.parse_header(
            mc.synthesis_header(unbound, schema, defaults, [0, 0, 0]), "synthesis"), schema)
        self.assertEqual((header["input"], header["outcome"]), ("unbound", "pass"))
        unbound["origin"]["caller"] = "review"
        header = mc.validate_header("synthesis", mc.parse_header(
            mc.synthesis_header(unbound, schema, defaults, [0, 0, 0]), "synthesis"), schema)
        self.assertEqual(header["outcome"], "incomplete")

    def test_review_callers_are_normalized_and_need_binding_method_and_counts(self):
        """Any spelling of the review caller gets the REVIEW guards (R1)."""
        sys.path.insert(0, str(ROOT / "lib"))
        import review_method as rm
        schema, defaults = mc.load_schema(), mc.load_defaults()

        def record(panel, name):
            mc.add_participant(panel, "r1", "m-a", "subagent", None, None, None)
            path = self.records / f"{name}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(report_text(panel, "r1", 1, verdict="pass", p1=0), encoding="utf-8")
            mc.record_round(panel, "r1", 1, path, schema=schema)

        def outcome(panel):
            header = mc.synthesis_header(panel, schema, defaults, [0, 0, 0], mc.verify_input(panel))
            return mc.validate_header("synthesis", mc.parse_header(header, "synthesis"), schema)["outcome"]

        unbound = mc.new_panel("c1", OWNER, self.brief, "turn", defaults, "implementation", ORIGIN, "x")
        record(unbound, "c1")
        self.assertEqual(outcome(unbound), "pass")
        for caller in ("review", "REVIEW", " review ", "cycle:REVIEW"):
            unbound["origin"]["caller"] = caller
            self.assertEqual(outcome(unbound), "incomplete", caller)

        self.assertEqual(self.init("--select", "src", "--caller", " Review ").returncode, 0)
        without_method = mc.read_json(self.panel)
        self.assertEqual(without_method["origin"]["caller"], "Review")
        record(without_method, "b1")
        self.assertEqual(outcome(without_method), "incomplete")

        self.panel.unlink()
        (self.inputs / "snapshot.json").unlink()
        questions = rm.select_questions(rm.load_catalog(), "implementation", [], "quality")
        body = rm.render_body(kind="implementation", stage="quality", subject_ref="src/util.py",
                              subject_text="def f(): return 1", questions=questions)
        self.brief.write_bytes(body.encode("utf-8"))
        meta = rm.method_meta(kind="implementation", stage="quality", subject_ref="src/util.py", body=body,
                              questions=questions)
        meta_path = self.inputs / "method.json"
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        made = self.init("--select", "src", "--method-meta", meta_path, "--caller", "review")
        self.assertEqual(made.returncode, 0, made.stderr)
        complete = mc.read_json(self.panel)
        record(complete, "m1")
        verified = mc.verify_input(complete)
        with self.assertRaises(mc.ContractError, msg="a REVIEW inspection needs adjudicated counts"):
            mc.inspection_record(complete, mc.synthesis_header(complete, schema, defaults, None, verified),
                                 schema, verified)

    def test_an_aliased_output_path_still_overlaps(self):
        """S3: a junction or symlink spelling of the repository cannot hide an overlap."""
        alias = Path(self.tmp.name) / "alias"
        try:
            if os.name == "nt":
                import _winapi
                _winapi.CreateJunction(str(self.repo), str(alias))
            else:
                os.symlink(self.repo, alias, target_is_directory=True)
        except (OSError, ImportError, AttributeError) as error:
            self.skipTest(f"cannot create a directory alias here: {error}")
        records = alias / ".claude" / "runtime" / "mars" / "b1" / "records"
        self.assertTrue(mc.output_overlaps(self.repo, ["."], [records]))
        self.assertTrue(mc.output_overlaps(alias, ["src"], [self.repo / "src" / "x.json"]))
        self.assertEqual(mc.output_overlaps(self.repo, ["src"], [records]), [])

    def test_a_case_variant_output_path_overlaps_on_every_host(self):
        """Fail closed on case-insensitive volumes (macOS default) as well as Windows."""
        self.assertTrue(mc.output_overlaps(self.repo, ["src"], [self.repo / "SRC" / "x.json"]))
        self.assertTrue(mc.output_overlaps(self.repo, ["SRC"], [self.repo / "src"]))
        self.assertEqual(mc.output_overlaps(self.repo, ["src"], [self.repo / "docs" / "x.json"]), [])


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True)

    def test_cli_roundtrip_and_exit_codes(self):
        origin = ["--requested-by", "operator", "--trigger", "explicit", "--caller", "standalone",
                  "--surface", "copilot-app", "--repository", "example/repo", "--branch", "b",
                  "--commit", "c" * 40]
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            brief = tmp / "brief.md"
            brief.write_text("b\n", encoding="utf-8")
            panel = tmp / "panel.json"
            init = ["panel", "init", "--panel", str(panel), "--id", "c1", "--owner", OWNER,
                    "--brief", str(brief), "--consent", "turn", *origin]
            self.assertEqual(self.run_cli(*init).returncode, 0)
            self.assertEqual(self.run_cli(*init).returncode, 2)
            self.assertEqual(self.run_cli("panel", "add", "--panel", str(panel), "--slot", "r1",
                                          "--model", "grok-4.7", "--transport", "nested-session",
                                          "--session", "s1", "--effort", "high",
                                          "--context", "long_context").returncode, 0)
            out = tmp / "req.md"
            made = self.run_cli("panel", "brief", "--panel", str(panel), "--slot", "r1", "--round", "1",
                                "--body", str(brief), "--out", str(out))
            self.assertEqual(made.returncode, 0, made.stderr)
            self.assertTrue(out.read_text(encoding="utf-8").startswith("```mars-request\n"))
            plan = json.loads(self.run_cli("panel", "close-plan", "--panel", str(panel),
                                           "--owner", OWNER).stdout)
            self.assertEqual(plan["close"], [])
            self.assertEqual(self.run_cli("panel", "close-plan", "--panel", str(panel),
                                          "--owner", "intruder").returncode, 2)
        self.assertEqual(self.run_cli("roster", "--host", str(HOST)).returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
