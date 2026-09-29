#!/usr/bin/env python3
# component: reusable-patterns-workflow-test
# implements: ADR-0038, ADR-0028
# intent: .claude/plans/reusable-patterns/plan.md
# constraints: synthetic temporary roots only; real resolver/CLI/launcher/adapter processes; a missing command fails, never mocked
# last_intent_review: 2026-09-28
"""V09: real helper outputs reach work IDs, continuation and review; missing evidence fails.

Each class maps to a workflow-lane leaf. The phase skills link one consumer contract; these
tests exercise the commands that contract names, including the real `bin/li-pattern` launcher
and the core `review` command. A missing command is a failure, never a skip or a mock;
host/model acceptance (V17) is a separate, fresh-session category.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pattern_consumer_fixtures import (  # noqa: E402
    CLI, CONTRACT, NOW, ROOT, TODAY, Fixture, binding, cli_commands, clause, codes, ctx, load_design_contract, make_pattern, p,
    pv, ref, tree_digest,
)

COMMANDS = cli_commands()
DASHBOARD = {"artifact": ["dashboard"]}
CONSUMERS = (
    "sense", "scope", "define", "discover", "cycle", "plan", "build", "resume", "review", "ship", "capture",
    "generate", "generate-outline", "generate-write", "generate-design", "generate-qa", "generate-word",
    "generate-ppt", "generate-pdf", "generate-xlsx", "generate-visio", "ta", "da", "sc", "dh", "tq",
    "frontend-style-extract", "generate-style-learn", "frontend-design", "design-dna", "frontend-typography",
    "frontend-motion", "frontend-shader", "generate-web", "generate-app", "frontend-design-review",
)


def require(command):
    if command not in COMMANDS:
        raise AssertionError(f"the joined CLI lacks `{command}`; this is a failure, not a skip")


class Workspace:
    """A dashboard baseline with must/default/recommendation clauses and Spec Kit style task IDs."""

    def __init__(self, testcase):
        self.t = testcase
        self.fx = Fixture(testcase)
        self.rules = make_pattern("example.dashboard", applies_to=DASHBOARD, requirements=[
            clause("NAV", "must", text="Navigation stays visible."),
            clause("EMPTY", "must", text="Every panel has an empty state."),
            clause("DENSITY", "default", "ui.density", "compact"),
            clause("TIPS", "recommendation")])
        self.publish()
        self.fx.repo_bindings([binding("dash", [ref("repo.main", self.rules)], when=DASHBOARD)])
        self.initiative = self.fx.repo / ".claude" / "plans" / "demo"
        self.initiative.mkdir(parents=True)
        self.lock = self.initiative / "patterns.lock.json"
        self.context = self.fx.write_json("context.json", ctx(artifact="dashboard"))

    def publish(self, **kwargs):
        return self.fx.publish(self.fx.repo_patterns, "repo.main", [self.rules], **kwargs)

    def resolve(self, *extra, lock=None):
        args = ["resolve", "--context", self.context, *extra]
        if lock is not None:
            args += ["--lock", lock]
        return self.fx.cli(*args)

    def plan(self):
        code, report, _ = self.resolve(lock=self.lock)
        self.t.assertEqual((code, report["status"]), (0, "ready"))
        lock = json.loads(self.lock.read_text(encoding="utf-8"))
        task_map = {"schema_version": 1, "selection_digest": lock["selection_digest"],
                    "tasks": ["T001", "T002", "T003"],
                    "packages": [{"id": "P1", "tasks": ["T001", "T002"]}, {"id": "P2", "tasks": ["T003"]}],
                    "clauses": [{"clause": "example.dashboard@1.0.0#NAV", "tasks": ["T001", "T003"]},
                                {"clause": "example.dashboard@1.0.0#EMPTY", "tasks": ["T002"]},
                                {"clause": "example.dashboard@1.0.0#DENSITY", "tasks": ["T002"]}]}
        map_path = self.fx.write_json("task-map.json", task_map)
        code, mapped, _ = self.fx.cli("map", "--lock", self.lock, "--task-map", map_path,
                                      "--expected-lock-digest", p.content_digest(lock), "--write")
        self.t.assertEqual((code, mapped["written"]), (0, True))
        return map_path, task_map


class ConsumerContractTests(unittest.TestCase):
    """4.1.a: one invocation/result contract with every failure branch."""

    def test_contract_documents_every_runtime_status_and_exit(self):
        text = CONTRACT.read_text(encoding="utf-8")
        rows = dict(re.findall(r"^\| `?([a-z -]+?)`? \| (\d) \|", text, re.M))
        for status in ("empty", "ready", "needs-context", "conflict", "unavailable", "invalid"):
            self.assertEqual(int(rows[status]), p.EXIT_CODES[status], status)
        self.assertEqual(int(rows["write collision"]), p.EXIT_CODES["collision"])
        self.assertEqual(int(rows["unmet review"]), p.EXIT_CODES["review-unmet"])

    def test_every_consumer_links_the_single_contract_without_a_local_resolver(self):
        for name in CONSUMERS:
            text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("../pattern/references/consumer-contract.md", text, name)
            self.assertNotRegex(text, r"(?i)def resolve|selection_digest\s*=\s*sha|sha256\(.*selection", name)

    def test_every_failure_branch_through_the_real_cli(self):
        ws = Workspace(self)
        code, report, stderr = ws.resolve()
        self.assertEqual((code, report["status"], stderr), (0, "ready", ""))
        code, report, stderr = ws.fx.cli("resolve", "--context", ws.fx.write_json("c2.json", ctx(artifact="report")))
        self.assertEqual((code, report["status"]), (0, "empty"), "a known mismatch does not block")
        ws.fx.repo_bindings([binding("dash", [ref("repo.main", ws.rules)],
                                     when={"artifact": ["dashboard"], "deployment.target": ["prod"]})])
        code, report, stderr = ws.resolve()
        self.assertEqual((code, report["status"]), (3, "needs-context"))
        self.assertIn("required_binding_needs_context", stderr)
        conflicting = make_pattern("example.other", applies_to=DASHBOARD,
                                   requirements=[clause("D", "must", "ui.density", "spacious")])
        ws.rules["requirements"][2] = clause("DENSITY", "must", "ui.density", "compact")
        ws.fx.publish(ws.fx.repo_patterns, "repo.main", [ws.rules, conflicting])
        ws.fx.repo_bindings([binding("dash", [ref("repo.main", ws.rules), ref("repo.main", conflicting)],
                                     when=DASHBOARD)])
        code, report, stderr = ws.resolve()
        self.assertEqual((code, report["status"]), (4, "conflict"))
        self.assertIn("must_setting_conflict", stderr)
        other_path = ws.fx.repo_patterns / "example.other" / "1.0.0" / "pattern.json"
        other_path.write_text(json.dumps(dict(conflicting, summary="edited after publication")), encoding="utf-8")
        code, report, stderr = ws.resolve()
        self.assertEqual((code, report["status"]), (5, "unavailable"), "changed bytes are never re-blessed")
        other_path.write_text("{}", encoding="utf-8")
        code, report, _ = ws.resolve()
        self.assertEqual((code, report["status"]), (2, "invalid"), "a corrupt source is visible, not empty")
        ws.context.write_text("{\"schema_version\": 1, \"facts\": {\"a\": \"b\"}}", encoding="utf-8")
        code, report, _ = ws.resolve()
        self.assertEqual((code, report["status"]), (2, "invalid"))
        code, report, stderr = ws.fx.cli("no-such-command")
        self.assertEqual((code, report["diagnostics"][0]["code"]), (2, "invalid_arguments"),
                         "a missing command is reported, never an empty success")

    def test_linked_roots_are_invalid_never_an_empty_selection(self):
        fx = Fixture(self)
        linked_repo, linked_home = fx.root / "repo-link", fx.root / "home-link"
        for link, target in ((linked_repo, fx.repo), (linked_home, fx.lintel_home)):
            if os.name == "nt":
                made = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
                if made.returncode:
                    self.skipTest("platform: cannot create a directory junction here")
            else:
                os.symlink(target, link, target_is_directory=True)
        context = fx.write_json("context.json", ctx(artifact="dashboard"))
        for repository, personal in ((linked_repo, fx.lintel_home), (fx.repo, linked_home)):
            envelope = {"schema_version": 1, "repository": repository.as_posix(), "personal": personal.as_posix(),
                        "pack_context": fx.pack_context, "diagnostics": []}
            roots = fx.write_json("linked-roots.json", envelope)
            result = subprocess.run([sys.executable, "-I", "-B", str(CLI), "resolve", "--roots-file", str(roots),
                                     "--context", str(context)], capture_output=True, env=fx.env(), cwd=fx.root,
                                    timeout=120)
            report = json.loads(result.stdout.decode("utf-8"))
            self.assertEqual((result.returncode, report["status"]), (2, "invalid"))
            self.assertIn(codes(report)[0], ("invalid_roots", "unsafe_path"))
            self.assertNotEqual(report["status"], "empty")
            with self.assertRaises(p.PatternError) as raised:
                p.build_envelope(repository, personal, fx.pack_context)
            self.assertEqual((raised.exception.code, raised.exception.status), ("invalid_roots", "invalid"))
            self.assertIn("real path", raised.exception.message)

    def test_launcher_envelope_matches_direct_cli(self):
        ws = Workspace(self)
        envelope = ws.fx.use_launcher_roots()
        neutral = envelope["pack_context"]
        self.assertEqual((neutral["status"], neutral["identity"]["name"]), ("neutral", "_default"))
        self.assertEqual((neutral["source"]["state"], neutral["source"]["value"]), ("null", None),
                         "the real neutral manifest declares patterns.source: null")
        code, launched, stderr = ws.fx.launcher("resolve", "--context", ws.context)
        self.assertEqual((code, launched["status"]), (0, "ready"), stderr)
        _, direct, _ = ws.resolve()
        api, _ = ws.fx.resolve(ctx(artifact="dashboard"))
        self.assertEqual(launched["selection_digest"], direct["selection_digest"])
        self.assertEqual(launched["selection_digest"], api["selection_digest"])
        self.assertEqual(launched["requirements"], direct["requirements"])
        self.assertEqual(launched["sources"], direct["sources"])

    def test_fallback_or_error_profile_without_sources_is_never_no_patterns(self):
        """M3: an empty-looking repository under a fallback/error profile still surfaces unavailable."""
        for status, diagnostics in (("fallback", [{"code": "optional_pack_missing", "message": "team pack absent"}]),
                                    ("error", [{"code": "profile_drift", "message": "pointer changed"}])):
            fx = Fixture(self)
            fx.pack_context = dict(fx.neutral_context(), status=status, diagnostics=diagnostics,
                                   identity=None if status == "error" else fx.pack_context["identity"])
            context = fx.write_json("context.json", ctx(artifact="dashboard"))
            for command in (("list",), ("resolve", "--context", context)):
                code, report, stderr = fx.cli(*command)
                self.assertEqual((code, report["status"]), (5, "unavailable"), (status, command))
                self.assertIn(f"pack_context_{status}", stderr)
                self.assertNotEqual(report["status"], "empty")

    def test_launcher_surfaces_a_fallback_profile(self):
        """P07 optional selection of a missing pack falls back to neutral; patterns must not proceed."""
        fx = Fixture(self)
        packs = fx.lintel_home / "packs"
        packs.mkdir(parents=True)
        (packs / "active-pack").write_text("ghost\n", encoding="utf-8", newline="\n")
        code, envelope, _ = fx.launcher("roots")
        self.assertEqual(code, 0)
        self.assertEqual((envelope["pack_context"]["status"], envelope["pack_context"]["identity"]["name"]),
                         ("fallback", "_default"))
        context = fx.write_json("context.json", ctx(artifact="dashboard"))
        for command in (("list",), ("resolve", "--context", context)):
            code, report, stderr = fx.launcher(*command)
            self.assertEqual((code, report["status"]), (5, "unavailable"), (command, stderr))
            self.assertIn("pack_context_fallback", codes(report, "error"))
            self.assertIn("OPTIONAL_PROFILE_FALLBACK", stderr)


class StartupTests(unittest.TestCase):
    """4.1.b: metadata-only startup, pre-design resolution and source checks; no guessed target."""

    def test_sense_lists_metadata_without_bodies_or_assets(self):
        ws = Workspace(self)
        code, report, _ = ws.fx.cli("list")
        self.assertEqual(code, 0)
        self.assertEqual((report["metrics"]["pattern_reads"], report["metrics"]["asset_reads"]), (0, 0))
        self.assertIn("example.dashboard", json.dumps(report))
        self.assertNotIn("Navigation stays visible", json.dumps(report))

    def test_unknown_target_never_becomes_a_guessed_deployment_baseline(self):
        ws = Workspace(self)
        network = make_pattern("example.network", applies_to={}, requirements=[
            clause("PRIVATE", "must", "network.ingress", "private-endpoint")])
        ws.fx.publish(ws.fx.repo_patterns, "repo.main", [ws.rules, network])
        ws.fx.repo_bindings([binding("prod-net", [ref("repo.main", network)], when={"deployment.target": ["prod"]})])
        before = tree_digest(ws.fx.repo)
        context = ws.fx.write_json("backend.json", ctx(artifact="service", platform="container"))
        code, report, _ = ws.fx.cli("resolve", "--context", context, "--lock", ws.lock)
        self.assertEqual((code, report["status"]), (3, "needs-context"))
        self.assertEqual(report["requirements"], [])
        self.assertIn("deployment.target", json.dumps(report["diagnostics"]))
        self.assertEqual(tree_digest(ws.fx.repo), before, "no lock for unknown mandatory context")
        known = ws.fx.write_json("backend-dev.json", ctx(artifact="service", **{"deployment.target": "dev"}))
        code, report, _ = ws.fx.cli("resolve", "--context", known)
        self.assertEqual((code, report["status"]), (0, "empty"), "a known non-matching target is not blocked")

    def test_discover_flags_unattested_url_sources(self):
        ws = Workspace(self)
        ws.rules["sources"] = [{"kind": "approved-standard", "ref": "https://standards.example/doc",
                                "root": "external", "section": "2", "observed_at": "2026-09-01T00:00:00Z",
                                "confidence": "confirmed", "reuse": "internal"}]
        ws.publish()
        ws.fx.repo_bindings([binding("dash", [ref("repo.main", ws.rules)], when=DASHBOARD)])
        code, report, stderr = ws.resolve()
        self.assertEqual((code, report["status"]), (5, "unavailable"))
        self.assertIn("source_attestation_required", stderr)


class PlanEquivalenceTests(unittest.TestCase):
    """4.1.c: direct and cycle PLAN are the same call; no sources adds nothing."""

    def test_direct_and_cycle_plan_produce_the_same_selection(self):
        ws = Workspace(self)
        cycle_lock = ws.initiative / "cycle.lock.json"
        _, direct, _ = ws.resolve(lock=ws.lock)
        _, cycle, _ = ws.resolve(lock=cycle_lock)
        api, _ = ws.fx.resolve(ctx(artifact="dashboard"))
        self.assertEqual(direct["selection_digest"], cycle["selection_digest"])
        self.assertEqual(direct["selection_digest"], api["selection_digest"])
        self.assertEqual(direct["lock"]["selection_digest"], cycle["lock"]["selection_digest"])
        self.assertEqual(direct["requirements"], cycle["requirements"])

    def test_no_sources_adds_no_prompts_reads_or_files(self):
        fx = Fixture(self)
        before = tree_digest(fx.repo)
        context = fx.write_json("context.json", ctx(artifact="dashboard"))
        code, report, stderr = fx.cli("resolve", "--context", context)
        self.assertEqual((code, report["status"], stderr), (0, "empty", ""))
        self.assertEqual((report["requirements"], report["candidates"]["total"]), ([], 0))
        self.assertEqual((report["metrics"]["pattern_reads"], report["metrics"]["asset_reads"]), (0, 0))
        self.assertEqual([item for item in report["diagnostics"] if item["severity"] != "info"], [])
        self.assertEqual(tree_digest(fx.repo), before)

    def test_plan_maps_clauses_to_existing_task_ids_only(self):
        ws = Workspace(self)
        map_path, task_map = ws.plan()
        lock = json.loads(ws.lock.read_text(encoding="utf-8"))
        self.assertEqual(lock["requirement_tasks"]["tasks"], ["T001", "T002", "T003"])
        incomplete = dict(task_map, clauses=task_map["clauses"][:1])
        code, report, _ = ws.fx.cli("map", "--lock", ws.lock, "--task-map", ws.fx.write_json("bad.json", incomplete),
                                    "--expected-lock-digest", p.content_digest(lock))
        self.assertEqual(code, 2)
        self.assertIn("unmapped_clause", codes(report))
        invented = dict(task_map, clauses=task_map["clauses"] + [{"clause": "example.dashboard@1.0.0#TIPS",
                                                                  "tasks": ["T999"]}])
        code, report, _ = ws.fx.cli("map", "--lock", ws.lock, "--task-map", ws.fx.write_json("inv.json", invented),
                                    "--expected-lock-digest", p.content_digest(lock))
        self.assertEqual(code, 2, "an invented task ID is refused")


class ContinuationTests(unittest.TestCase):
    """4.2.a-wf: BUILD/RESUME verify pins and hand out complete package projections."""

    def test_build_projects_complete_packages_with_unchanged_task_ids(self):
        ws = Workspace(self)
        map_path, _ = ws.plan()
        code, verified, _ = ws.fx.cli("verify-lock", "--lock", ws.lock, "--context", ws.context)
        self.assertEqual((code, verified["status"]), (0, "ok"))
        projections = {}
        for package in ("P1", "P2"):
            code, projection, _ = ws.fx.cli("project", "--lock", ws.lock, "--task-map", map_path,
                                            "--package", package, roots=False)
            self.assertEqual(code, 0)
            projections[package] = {item["clause"]: item["task_ids"] for item in projection["clauses"]}
        self.assertEqual(projections["P1"], {"example.dashboard@1.0.0#NAV": ["T001"],
                                             "example.dashboard@1.0.0#EMPTY": ["T002"],
                                             "example.dashboard@1.0.0#DENSITY": ["T002"]})
        self.assertEqual(projections["P2"], {"example.dashboard@1.0.0#NAV": ["T003"]},
                         "a shared mandatory clause appears in every owning package")

    def test_changed_revoked_or_recontexted_pins_block_continuation(self):
        ws = Workspace(self)
        ws.plan()
        path = ws.fx.repo_patterns / "example.dashboard" / "1.0.0" / "pattern.json"
        original = path.read_bytes()
        path.write_text(json.dumps(dict(ws.rules, summary="edited")), encoding="utf-8")
        code, report, _ = ws.fx.cli("verify-lock", "--lock", ws.lock, "--context", ws.context)
        self.assertEqual((code, report["status"]), (5, "unavailable"))
        path.write_bytes(original)
        digest = p.content_digest(ws.rules)
        ws.publish(revocations=[{"id": "example.dashboard", "version": "1.0.0", "sha256": digest,
                                 "reason": "withdrawn", "reference": "incident-1", "at": "2026-09-10T00:00:00Z"}])
        code, report, _ = ws.fx.cli("verify-lock", "--lock", ws.lock, "--context", ws.context)
        self.assertEqual((code, report["status"]), (5, "unavailable"))
        self.assertIn("pinned_revoked", codes(report))
        ws.publish()
        other = ws.fx.write_json("other.json", ctx(artifact="dashboard", audience="public"))
        code, report, _ = ws.fx.cli("verify-lock", "--lock", ws.lock, "--context", other)
        self.assertEqual((code, report["status"]), (4, "conflict"))
        self.assertIn("context_changed", codes(report))

    def test_resume_detects_a_changed_mandatory_baseline(self):
        ws = Workspace(self)
        ws.plan()
        extra = make_pattern("example.audit", applies_to=DASHBOARD, requirements=[clause("LOG", "must")])
        ws.fx.publish(ws.fx.repo_patterns, "repo.main", [ws.rules, extra])
        ws.fx.repo_bindings([binding("dash", [ref("repo.main", ws.rules)], when=DASHBOARD),
                             binding("audit", [ref("repo.main", extra)], when=DASHBOARD)])
        code, report, _ = ws.fx.cli("verify-lock", "--lock", ws.lock, "--context", ws.context)
        self.assertEqual((code, report["status"]), (4, "conflict"))
        self.assertEqual(report["baseline"]["added"], ["example.audit@1.0.0#LOG"])
        self.assertEqual(json.loads(ws.lock.read_text(encoding="utf-8"))["requirement_tasks"]["tasks"],
                         ["T001", "T002", "T003"], "the original lock is never rewritten")


class ReviewTests(unittest.TestCase):
    """4.2.b-wf: clause coverage is supplemental evidence; unmet mandatory evidence exits 7."""

    def setUp(self):
        require("review")
        self.ws = Workspace(self)
        self.map_path, _ = self.ws.plan()
        self.lock = json.loads(self.ws.lock.read_text(encoding="utf-8"))

    def item(self, clause_id, status="passed", tasks=("T001",), refs=("tests/report.txt",)):
        return {"clause": f"example.dashboard@1.0.0#{clause_id}", "task_ids": list(tasks), "status": status,
                "evidence_refs": list(refs), "explanation": "Reviewed the referenced artifact."}

    def review(self, items):
        evidence = {"schema_version": 1, "selection_digest": self.lock["selection_digest"],
                    "mapping_digest": self.lock["requirement_tasks"]["mapping_digest"], "items": items}
        return self.ws.fx.cli("review", "--lock", self.ws.lock, "--context", self.ws.context,
                              "--evidence", self.ws.fx.write_json("evidence.json", evidence))

    def complete(self):
        return [self.item("NAV", tasks=("T001", "T003")), self.item("EMPTY", tasks=("T002",)),
                self.item("DENSITY", tasks=("T002",))]

    def test_complete_evidence_is_coverage_not_clearance(self):
        code, report, _ = self.review(self.complete())
        self.assertEqual(code, 0)
        self.assertNotIn('"clearance": true', json.dumps(report).lower())

    def test_omitted_failed_or_unverified_mandatory_clauses_exit_7(self):
        for items in (self.complete()[1:], [self.item("NAV", "failed", ("T001", "T003"))] + self.complete()[1:],
                      [self.item("NAV", "unverified", ("T001", "T003"))] + self.complete()[1:]):
            code, _, _ = self.review(items)
            self.assertEqual(code, 7)

    def test_passed_without_evidence_references_is_not_a_pass(self):
        items = [self.item("NAV", tasks=("T001", "T003"), refs=())] + self.complete()[1:]
        code, _, _ = self.review(items)
        self.assertIn(code, (2, 7))

    def test_mandatory_not_applicable_in_the_old_lock_is_refused(self):
        items = [self.item("NAV", "not-applicable", ("T001", "T003"))] + self.complete()[1:]
        code, _, _ = self.review(items)
        self.assertIn(code, (2, 7))


class CaptureTests(unittest.TestCase):
    """4.2.c: capture proposes drafts; cold handoff reconstructs from explicit artifacts."""

    def test_capture_proposes_a_draft_that_never_applies(self):
        ws = Workspace(self)
        draft = make_pattern("example.proposal", version="0.1.0", status="draft", applies_to=DASHBOARD,
                             requirements=[clause("NEW", "must")])
        code, report, _ = ws.fx.cli("capture", "--input", ws.fx.write_json("draft.json", draft), "--scope",
                                    "personal", "--name", "example.proposal", "--source-id", "personal.me")
        self.assertEqual((code, report["status"]), (0, "ok"))
        refs = [{"ref": report["ref"], "role": "required", "approved_by": "me", "approval_ref": "chat"}]
        refs_file = ws.fx.write_json("refs.json", refs)
        code, resolved, _ = ws.resolve("--refs", refs_file)
        self.assertEqual((code, resolved["status"]), (5, "unavailable"))
        code, preview, _ = ws.resolve("--refs", refs_file, "--preview-draft", lock=ws.initiative / "draft.lock.json")
        self.assertEqual(preview["status"], "unavailable")
        self.assertFalse((ws.initiative / "draft.lock.json").exists(), "a draft preview is never locked")
        code, baseline, _ = ws.resolve()
        self.assertNotIn("example.proposal", json.dumps(baseline["selected"]), "capture never re-binds")

    def test_cold_handoff_reconstructs_the_package_from_saved_files(self):
        ws = Workspace(self)
        map_path, _ = ws.plan()
        _, original, _ = ws.resolve()
        code, projection, _ = ws.fx.cli("project", "--lock", ws.lock, "--task-map", map_path, "--package", "P1",
                                        roots=False)
        self.assertEqual(code, 0)
        by_clause = {item["clause"]: item for item in original["requirements"]}
        for item in projection["clauses"]:
            self.assertEqual(item["text"], by_clause[item["clause"]]["text"])
            self.assertEqual(item["state"], by_clause[item["clause"]]["state"])
        self.assertEqual(projection["selection_digest"], original["selection_digest"])


class DocumentPipelineTests(unittest.TestCase):
    """4.3.a-c: pipeline attachment, direct entry and format providers share one selection."""

    def setUp(self):
        self.fx = Fixture(self)
        self.doc = make_pattern("example.tech-doc", applies_to={"artifact": ["technical-document"]}, requirements=[
            clause("SECURITY", "must", "document.required-section", "Security considerations",
                   text="The document has a Security considerations section."),
            clause("TONE", "default", "document.tone", "neutral")])
        self.fx.publish(self.fx.repo_patterns, "repo.docs", [self.doc])
        self.fx.repo_bindings([binding("doc", [ref("repo.docs", self.doc)],
                                       when={"artifact": ["technical-document"]})])
        self.run = self.fx.repo / ".claude" / "runtime" / "patterns" / "run-7"
        self.run.mkdir(parents=True)
        self.context = p.parse_context(ctx(artifact="technical-document"))
        report, _ = self.fx.resolve(ctx(artifact="technical-document"))
        self.report = report
        self.lock = p.build_lock(report, self.context, now=NOW)
        p.write_lock(self.fx.roots(), self.run / "patterns.lock.json", self.lock)
        self.attachment = pv.design_attachment(self.lock, "patterns.lock.json")

    def verify(self, attachment):
        return pv.verify_design_attachment(self.fx.roots(), self.run, attachment, self.context, today=TODAY)

    def test_pipeline_attachment_is_verified_and_accepted_by_the_shared_validator(self):
        result = self.verify(self.attachment)
        self.assertEqual(result["status"], "ok")
        self.assertIn("example.tech-doc@1.0.0#SECURITY", self.attachment["clause_ids"])
        design = {"version": "1.0", "source": "pipeline", "palette": {}, "fonts": {},
                  "per_format": {"word": {"sections": []}}, "pattern_context": self.attachment}
        loaded = load_design_contract().validate_spec(design, "pipeline")
        self.assertEqual(loaded["kind"], "pipeline")

    def test_absent_stale_or_incomplete_attachment_is_not_a_pass(self):
        for change, code in (({"selection_digest": "0" * 64}, "attachment_stale"),
                             ({"clause_ids": ["example.tech-doc@1.0.0#TONE"]}, "attachment_clauses"),
                             ({"lock_ref": "missing.lock.json"}, "attachment_lock_missing")):
            with self.assertRaises(p.PatternError) as raised:
                self.verify(dict(self.attachment, **change))
            self.assertEqual((raised.exception.code, raised.exception.status), (code, "unavailable"))
        with self.assertRaises(p.PatternError):
            self.verify(dict(self.attachment, lock_ref="../outside.json"))
        with self.assertRaises(p.PatternError):
            self.verify({"schema_version": 1})

    def test_changed_source_after_attachment_blocks_the_stage(self):
        path = self.fx.repo_patterns / "example.tech-doc" / "1.0.0" / "pattern.json"
        path.write_text(json.dumps(dict(self.doc, guidance="edited")), encoding="utf-8")
        self.assertEqual(self.verify(self.attachment)["status"], "unavailable")

    def test_direct_brief_and_pipeline_receive_the_same_clauses(self):
        direct, _ = self.fx.resolve(ctx(artifact="technical-document"))
        attached = self.verify(self.attachment)["lock"]
        self.assertEqual(direct["requirements"], attached["requirements"])
        self.assertEqual(direct["selection_digest"], attached["selection_digest"])

    def test_document_outputs_elsewhere_keep_the_lock_in_the_repository(self):
        """L3: the run's documents may live outside the repository; the lock and its root never do."""
        outside = self.fx.root / "document outputs" / "run-7"
        outside.mkdir(parents=True)
        (outside / "design-spec.json").write_text(json.dumps({"pattern_context": self.attachment}), encoding="utf-8")
        self.assertEqual(self.verify(self.attachment)["status"], "ok")
        with self.assertRaises(p.PatternError) as raised:
            pv.verify_design_attachment(self.fx.roots(), outside, self.attachment, self.context, today=TODAY)
        self.assertEqual((raised.exception.code, raised.exception.status), ("lock_outside_repository", "invalid"))
        with self.assertRaises(p.PatternError) as raised:
            p.write_lock(self.fx.roots(), outside / "patterns.lock.json", self.lock)
        self.assertFalse((outside / "patterns.lock.json").exists())

    def test_unrelated_format_fact_does_not_change_the_selection(self):
        """L5: selection invariance only. Card 4.3.c's conversion duty is a V18 source review plus the existing provider compatibility tests (RN-14)."""
        for provider in ("docx", "pptx", "pdf", "xlsx", "vsdx"):
            report, _ = self.fx.resolve(ctx(artifact="technical-document", format=provider))
            mandatory = [item["clause"] for item in report["requirements"] if item["state"] == "mandatory"]
            self.assertEqual(mandatory, ["example.tech-doc@1.0.0#SECURITY"], provider)

    def test_removed_required_section_fails_review(self):
        require("review")
        task_map = {"schema_version": 1, "selection_digest": self.lock["selection_digest"], "tasks": ["D1"],
                    "packages": [{"id": "DOC", "tasks": ["D1"]}],
                    "clauses": [{"clause": "example.tech-doc@1.0.0#SECURITY", "tasks": ["D1"]},
                                {"clause": "example.tech-doc@1.0.0#TONE", "tasks": ["D1"]}]}
        lock_path = self.run / "patterns.lock.json"
        code, _, _ = self.fx.cli("map", "--lock", lock_path, "--task-map", self.fx.write_json("m.json", task_map),
                                 "--expected-lock-digest", p.content_digest(self.lock), "--write")
        self.assertEqual(code, 0)
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        evidence = {"schema_version": 1, "selection_digest": lock["selection_digest"],
                    "mapping_digest": lock["requirement_tasks"]["mapping_digest"], "items": [
                        {"clause": "example.tech-doc@1.0.0#SECURITY", "task_ids": ["D1"], "status": "failed",
                         "evidence_refs": ["qa-report.json"], "explanation": "The section was removed."},
                        {"clause": "example.tech-doc@1.0.0#TONE", "task_ids": ["D1"], "status": "passed",
                         "evidence_refs": ["qa-report.json"], "explanation": "Tone reviewed."}]}
        code, _, _ = self.fx.cli("review", "--lock", lock_path, "--context",
                                 self.fx.write_json("ctx.json", ctx(artifact="technical-document")),
                                 "--evidence", self.fx.write_json("e.json", evidence))
        self.assertEqual(code, 7)


class EngineeringTests(unittest.TestCase):
    """4.3.d: target-bound expectations, scoped projections, unknown target blocks."""

    def setUp(self):
        self.fx = Fixture(self)
        self.net = make_pattern("example.prod-network", applies_to={"deployment.target": ["prod"]}, requirements=[
            clause("INGRESS", "must", "network.ingress", "private-endpoint"),
            clause("TLS", "must", "network.tls-min", "1.2")])
        self.visual = make_pattern("example.web", applies_to={"artifact": ["website"]}, requirements=[
            clause("MAX", "default", "visual.layout.max-width", "1200px")],
            assets=[{"path": "tokens.json", "kind": "tokens", "sha256": "b" * 64}])
        self.fx.publish(self.fx.repo_patterns, "repo.eng", [self.net, self.visual])
        self.fx.repo_bindings([
            binding("prod", [ref("repo.eng", self.net)], when={"deployment.target": ["prod"]}),
            binding("web", [ref("repo.eng", self.visual)], role="default", when={"artifact": ["website"]})])

    def test_unknown_target_blocks_dependent_design(self):
        report, reader = self.fx.resolve(ctx(artifact="service"))
        self.assertEqual(report["status"], "needs-context")
        self.assertEqual(report["requirements"], [])
        self.assertEqual((reader.count("pattern"), reader.count("asset")), (0, 0))

    def test_known_target_projects_only_target_clauses_and_no_visual_assets(self):
        report, reader = self.fx.resolve(ctx(artifact="service", **{"deployment.target": "prod"}))
        self.assertEqual(report["status"], "ready")
        self.assertEqual([item["clause"] for item in report["requirements"]],
                         ["example.prod-network@1.0.0#INGRESS", "example.prod-network@1.0.0#TLS"])
        self.assertEqual(reader.count("asset"), 0)
        self.assertEqual(p.asset_refs(report, kind="tokens"), [])
        lock = p.build_lock(report, p.parse_context(ctx(artifact="service", **{"deployment.target": "prod"})), now=NOW)
        task_map = {"schema_version": 1, "selection_digest": lock["selection_digest"], "tasks": ["SC-1", "DH-1"],
                    "packages": [{"id": "sc", "tasks": ["SC-1"]}, {"id": "dh", "tasks": ["DH-1"]}],
                    "clauses": [{"clause": "example.prod-network@1.0.0#TLS", "tasks": ["SC-1"]},
                                {"clause": "example.prod-network@1.0.0#INGRESS", "tasks": ["DH-1"]}]}
        sc = p.project_package(lock, task_map, "sc")
        self.assertEqual([item["clause"] for item in sc["clauses"]], ["example.prod-network@1.0.0#TLS"])
        self.assertEqual(list(sc["settings"]), ["network.tls-min"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
