#!/usr/bin/env python3
# component: swarm-shared-binding-tests
# implements: ADR-0027, ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P04.md
# constraints: verified synthetic process roots; real providers; no unaccepted P08 or live actors
# last_intent_review: 2026-09-22
"""Actual P05/P07/P09 consumption; synthetic records are not independent people."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SOURCE / "lib"))
sys.path.insert(0, str(SOURCE / "tests/unit"))
import profile_context as profile
import review_contract as review
import context_safety as safety
from native_paths import native_io_path

spec = importlib.util.spec_from_file_location("swarm_fixture", SOURCE / "tests/unit/swarm-contract.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SwarmFixture = module.SwarmFixture
swarm = module.swarm


def encoded(value: object) -> str:
    return review.canonical_json(value) + "\n"


class SharedBinding(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lintel-swarm-shared-")
        self.addCleanup(self.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.repo = self.root / "target"
        self.repo.mkdir()
        self.home = self.root / "home"
        self.env = {key: value for key, value in os.environ.items() if key in (
            "PATH", "PATHEXT", "SystemRoot", "WINDIR", "SystemDrive", "COMSPEC",
        )}
        for key, path in {
            "HOME": self.home, "USERPROFILE": self.home,
            "APPDATA": self.home / "AppData/Roaming", "LOCALAPPDATA": self.home / "AppData/Local",
            "XDG_CONFIG_HOME": self.home / ".config", "XDG_CACHE_HOME": self.home / ".cache",
            "XDG_DATA_HOME": self.home / ".local/share", "TEMP": self.root / "tmp",
            "TMP": self.root / "tmp", "TMPDIR": self.root / "tmp",
            "LINTEL_HOME": self.home / ".lintel", "LINTEL_PACKS_DIR": self.home / ".lintel/packs",
            "LINTEL_AUDIT_DIR": self.repo / ".claude/runtime/audit",
            "LINTEL_STATE_DIR": self.repo / ".claude/runtime/state",
            "LINTEL_JOBS_DIR": self.repo / ".claude/runtime/jobs",
        }.items():
            path.mkdir(parents=True, exist_ok=True)
            self.env[key] = path.as_posix()
        self.env.update({
            "LINTEL_ACTIVE_PACK_FILE": (self.home / ".lintel/packs/active-pack").as_posix(),
            "LINTEL_REPO_ROOT": self.repo.as_posix(), "LINTEL_SOURCE_ROOT": SOURCE.as_posix(),
            "LINTEL_PYTHON": Path(sys.executable).as_posix(), "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1", "PYTHONIOENCODING": "utf-8",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never",
        })
        self.fixture = SwarmFixture(self.repo)
        self.fixture.coordination["lanes"] = [self.fixture.coordination["lanes"][0]]
        self.fixture.coordination["max_parallel"] = 1
        self.lane = self.fixture.coordination["lanes"][0]
        self.paths = {
            "context": ".claude/runtime/swarm/BC1/context.json",
            "review": ".claude/runtime/reviews/swarm-BC1.json",
            "qa": ".claude/runtime/swarm/BC1/qa.json",
            "corroboration": ".claude/runtime/swarm/BC1/corroboration.json",
            "domain_request": None,
            "review_skill": "review",
        }
        self.lane["shared_evidence"] = self.paths
        self.fixture.save()
        self.write(".claude/lintel-layout.yaml", "layout_version: 5\n")
        self.write(".gitignore", ".claude/runtime/\n")
        self.write("src/core/file.py", "baseline result\n")
        self.git("init", "-q", "-b", "synthetic")
        self.git("add", ".")
        self.git("commit", "-qm", "test: synthetic baseline")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()
        self.config = profile.ProfileConfig(
            SOURCE, self.repo, self.home / ".lintel", self.home / ".lintel/packs",
            self.home / ".lintel/packs/active-pack", context_id="swarm-shared-fixture",
        )
        self.assert_isolation()
        pin = profile.load_profile_context(self.config, create=True)
        self.reference = profile.profile_reference(pin)
        self.policy = profile.required_policy(pin)

    def cleanup(self):
        self.assertEqual(Path(self.temporary.name).resolve(), self.root)
        self.assertTrue(self.root.name.startswith("lintel-swarm-shared-"))
        self.temporary.name = str(native_io_path(self.root))
        self.temporary.cleanup()

    def assert_isolation(self):
        for key in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME",
                    "XDG_CACHE_HOME", "XDG_DATA_HOME", "TEMP", "TMP", "TMPDIR", "LINTEL_HOME",
                    "LINTEL_PACKS_DIR", "LINTEL_ACTIVE_PACK_FILE", "LINTEL_AUDIT_DIR",
                    "LINTEL_STATE_DIR", "LINTEL_JOBS_DIR", "LINTEL_REPO_ROOT"):
            self.assertTrue(Path(self.env[key]).resolve().is_relative_to(self.root), key)
        self.assertFalse(any(key in self.env for key in (
            "GSTACK_HOME", "GH_TOKEN", "GITHUB_TOKEN", "PACK_CACHE_FILE", "BASH_ENV",
            "PYTHONPATH", "LINTEL_PROFILE_REFERENCE", "GIT_CONFIG_COUNT",
        )))

    def run_process(self, arguments, *, expected=0):
        self.assert_isolation()
        arguments = [str(arg) for arg in arguments]
        input_text = None
        if arguments[0] == "bash":
            input_text = "exec " + shlex.join(arg.replace("\\", "/") for arg in arguments) + "\n"
            arguments = ["bash"]
        result = subprocess.run(arguments, input=input_text, cwd=self.repo, env=self.env,
                                capture_output=True, text=True, encoding="utf-8", timeout=90, check=False)
        if expected is not None:
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def git(self, *args):
        return self.run_process([
            "git", "-c", "core.autocrlf=false", "-c", "commit.gpgsign=false",
            "-c", f"core.hooksPath={self.root / 'no-hooks'}",
            "-c", "user.name=Synthetic fixture", "-c", "user.email=fixture@example.invalid", *args,
        ])

    def write(self, relative, value):
        self.fixture._write(relative, value)

    def write_json(self, relative, value):
        self.write(relative, encoded(value))

    def p05(self, command, *args, expected=0):
        run = self.run_process([sys.executable, "-B", SOURCE / "bin/li-review-evidence.py",
                                command, "--repo", self.repo, *args], expected=expected)
        return json.loads(run.stdout) if run.stdout.strip() else None

    def consume(self, command="verify", *, expected=0, profile_args=True):
        arguments = [sys.executable, "-B", SOURCE / "bin/li-swarm.py", command,
                     "--repo", self.repo, "--coord", self.fixture.coordination_path]
        if profile_args:
            arguments += ["--profile-home", self.config.home, "--profile-packs", self.config.packs,
                          "--profile-pointer", self.config.pointer]
        return json.loads(self.run_process(arguments, expected=expected).stdout)

    def scope_command(self, path, *, actor="reviewer", expected=0):
        return self.run_process([
            sys.executable, "-B", SOURCE / "bin/li-swarm.py", "check-scope",
            "--repo", self.repo, "--coord", self.fixture.coordination_path,
            "--task", "BC1", "--actor", actor, "--changed", path,
        ], expected=expected)

    def observe(self):
        run = self.run_process([sys.executable, "-I", "-B", "-c",
                               "import unittest\nclass Check(unittest.TestCase):\n"
                               " def test_synthetic(self): self.assertEqual(2+2,4)\nunittest.main()\n"])
        self.assertIn("Ran 1 test", run.stderr)
        self.write("evidence/checks.txt", run.stdout + run.stderr)
        self.controls = [{
            **deepcopy(self.requirement),
            "status": "pass", "reason": "Observed synthetic test, not a live agent.",
            "evidence": ["evidence/checks.txt"],
            "observation": {"command": "python -I -B synthetic unittest", "executed": 1,
                            "failed": 0, "skipped": 0, "exit_code": run.returncode},
        }]

    def prepare(self, *, verification_only=False, mechanical=False, domain=False):
        self.assert_isolation()
        if verification_only:
            self.write("plan.md", "# Plan\n### BC1 Core\n**Result:** verification-only\n")
        if mechanical:
            self.write("plan.md", "# Plan\n| Package ID | Leaf IDs | Owner / edit boundary | Review |\n"
                       "|---|---|---|---|\n| BC1 | T1 | builder; src/core | mechanical |\n\n- [ ] T1 Core\n")
        if domain:
            self.paths["domain_request"] = ".claude/runtime/swarm/BC1/domain-request.json"
            self.fixture.save()
        leaves = ["T1"] if mechanical else ["BC1"]
        self.requirement = {
            "id": "tests", "kind": "tests", "requirement": "mandatory", "applicability": "applicable",
            "policy": {"source": "spec.md", "version": "synthetic-1", "applicability": "Synthetic acceptance",
                       "jurisdiction": None, "actor": None, "effective_date": None},
        }
        self.request = {
            "work_map": self.fixture.work_map_path, "package_id": "BC1", "leaf_ids": leaves,
            "acceptance_paths": ["spec.md", self.fixture.coordination_path, self.fixture.coordination["charter"], self.lane["brief"]],
            "base": self.base, "selection": [*self.lane["write_scope"]],
            "record_path": self.paths["review"], "attempt_id": "attempt-1",
            "builder": {"id": "worker-BC1", "context": "synthetic:worker-BC1"},
            "independence_required": not mechanical, "purpose": "verification_only" if verification_only else "implementation",
            "profile": self.reference, "required_policy": self.policy,
            "required_controls": ["spec", "quality", "tests"],
            "qa_requirements": [deepcopy(self.requirement)],
        }
        self.write_json(".claude/runtime/swarm/initial-prepare.json", self.request)
        self.initial_context = self.p05("prepare", "--request", self.repo / ".claude/runtime/swarm/initial-prepare.json")
        self.fixture.write_evidence(self.lane, verification_only=verification_only,
                                    review_overrides={"mode": "coordinator"} if mechanical else None)
        if domain:
            self.produce_domain()
        else:
            self.observe()
        self.request["selection"] += [self.lane["report"], self.lane["review"], "evidence"]
        self.finalize()

    def p09(self, command, *args, expected=0):
        run = self.run_process([sys.executable, "-B", SOURCE / "bin/li-domain-result.py",
                               command, "--repo", self.repo, *args], expected=expected)
        return json.loads(run.stdout)

    def ref(self, path):
        self.assert_isolation()
        _, state = safety.read_owned(self.repo, path)
        return {"path": path, "sha256": state["sha256"]}

    def produce_domain(self):
        initial = self.initial_context
        prefix = ".claude/runtime/state/domains/swarm-fixture/i0001/ta"
        checkpoint = {
            "id": "observed", "receiver": {"role": "TestRunner", "mode": "verification"},
            "control_ids": ["tests"], "artifacts": [],
            "start": {"path": prefix + "/start.json", "expected_state": None},
            "result": {"path": prefix + "/result.json", "expected_state": None},
        }
        self.domain_request = {
            "schema_version": 1, "kind": "domain-request", "operation_id": "swarm-fixture", "iteration": 1,
            "input_context": initial, "domains": [{"id": "ta", "checkpoints": [checkpoint]}],
            "advisory_preferences": {}, "release_clearance": False,
        }
        self.write_json(self.paths["domain_request"], self.domain_request)
        self.write_json(".claude/runtime/swarm/original-state.json", {"state": None})
        common = {
            "schema_version": 1, "domain": "ta", "checkpoint": "observed", "receiver": checkpoint["receiver"],
            "producer": initial["builder"], "provenance": "declared", "release_clearance": False,
            "request": self.ref(self.paths["domain_request"]),
        }
        self.write_json(".claude/runtime/swarm/domain-input.json", {**common, "kind": "domain-checkpoint"})
        self.p09("record", "--request", self.paths["domain_request"], "--file", ".claude/runtime/swarm/domain-input.json",
                 "--output", checkpoint["start"]["path"], "--expected-state", ".claude/runtime/swarm/original-state.json")
        self.observe()
        self.domain_result = {
            **common, "kind": "domain-result", "start": self.ref(checkpoint["start"]["path"]),
            "status": "pass", "reason": "Actual synthetic unittest, not live specialist execution.",
            "controls": deepcopy(self.controls), "evidence": review.evidence_manifest(self.repo, self.controls),
            "artifacts": [], "decisions": [], "limitations": ["Synthetic actors only."],
            "next": {"owner": "coordinator", "action": "Arrange actual independent review."},
        }
        self.write_json(".claude/runtime/swarm/domain-input.json", self.domain_result)
        self.p09("record", "--request", self.paths["domain_request"], "--file", ".claude/runtime/swarm/domain-input.json",
                 "--output", checkpoint["result"]["path"], "--expected-state", ".claude/runtime/swarm/original-state.json")
        self.domain_result_path = checkpoint["result"]["path"]
        self.domain_start_path = checkpoint["start"]["path"]
        self.request["selection"] += [self.paths["domain_request"], prefix]

    def finalize(self):
        self.write_json(".claude/runtime/swarm/prepare.json", self.request)
        self.context = self.p05("prepare", "--request", self.repo / ".claude/runtime/swarm/prepare.json")
        self.write_json(self.paths["context"], self.context)
        self.write_json(".claude/runtime/swarm/qa-input.json", {"controls": self.controls})
        self.qa = self.p05("qa", "--expected", self.repo / self.paths["context"],
                           "--input", self.repo / ".claude/runtime/swarm/qa-input.json")
        self.write_json(self.paths["qa"], self.qa)
        controls = deepcopy(self.controls)
        for name in ("spec", "quality"):
            item = deepcopy(self.controls[0])
            item.update(id=name, kind="check", observation={})
            controls.append(item)
        self.decision = {
            "schema_version": review.CONTRACT_VERSION, "skill": "review", "status": "pass",
            "timestamp": datetime.now(timezone.utc).isoformat(), "reason": "Synthetic provider fixture only.",
            "context": self.context, "reviewer": {"id": "reviewer-BC1", "context": "synthetic:reviewer-BC1"},
            "provenance": "declared", "controls": controls,
            "coverage": {leaf: list(self.context["required_controls"]) for leaf in self.context["work"]["leaf_ids"]},
            "evidence": review.evidence_manifest(self.repo, controls),
        }
        self.log()
        if self.paths["corroboration"] is not None:
            self.write_json(self.paths["corroboration"], {
                "schema_version": 1, "kind": "host", "source": "synthetic test, not host proof",
                "reference": "fixture-only", "record_digest": review.content_digest(self.decision),
                "attempt_id": self.context["attempt_id"], "builder": self.context["builder"],
                "reviewer": self.decision["reviewer"],
            })

    def log(self):
        self.write_json(self.paths["review"], self.decision)
        self.run_process(["bash", SOURCE / "bin/li-review-log", "--file", self.repo / self.paths["review"]])

    def test_real_no_domain_chain_passes_all_acceptance_consumers(self):
        self.prepare()
        for command in ("status", "wave", "resume", "verify"):
            value = self.consume(command)
            self.assertTrue(value["ok"])
            states = value["frontier"]["states"] if "frontier" in value else value["lanes"]
            self.assertEqual(states[0]["state"], "complete")
            self.assertTrue(states[0]["shared_evidence"]["ok"])

    def test_local_reports_alone_are_inspection_not_shared_clearance(self):
        self.prepare()
        (self.repo / self.paths["corroboration"]).unlink()
        for command in ("status", "wave", "resume", "verify"):
            self.assertFalse(self.consume(command, expected=1)["ok"])
        local = self.consume("inspect", profile_args=False)
        self.assertTrue(local["ok"])
        self.assertFalse(local["release_clearance"])
        self.assertEqual(local["verification"], "local_observations_only")

    def test_new_pointer_cannot_alias_authority_or_another_actor(self):
        original = deepcopy(self.paths)
        for field in ("context", "review", "qa", "corroboration", "domain_request"):
            for path in ("plan.md", self.lane["report"], original["review"], ".claude"):
                if field == "review" and path == original["review"]:
                    continue
                with self.subTest(field=field, path=path):
                    self.paths.update(original)
                    self.paths[field] = path
                    self.fixture.save()
                    value = self.consume("validate", profile_args=False, expected=1)
                    self.assertFalse(value["ok"])
        self.paths.update(original)
        self.fixture.save()

    def test_later_rejection_and_malformed_log_block_every_shared_consumer(self):
        self.prepare()
        good = deepcopy(self.decision)
        self.decision["status"] = "fail"
        self.decision["reason"] = "New independent synthetic rejection."
        self.log()
        self.write_json(self.paths["review"], good)
        for command in ("status", "wave", "resume", "verify"):
            self.assertFalse(self.consume(command, expected=1)["ok"])
        self.decision = good
        self.log()
        self.assertTrue(self.consume()["ok"])
        log = self.repo / ".claude/runtime/audit/reviews.jsonl"
        with log.open("a", encoding="utf-8") as stream:
            stream.write('{"malformed":\n')
        self.assertFalse(self.consume(expected=1)["ok"])
        self.log()
        self.assertTrue(self.consume()["ok"], "a newer actual valid decision can supersede obsolete bad evidence")

    def test_changed_context_attempt_selected_output_and_report_revoke_shared_evidence(self):
        self.prepare()
        original = (self.repo / "src/core/file.py").read_bytes()
        self.write("src/core/file.py", "unreviewed result\n")
        self.consume(expected=1)
        (self.repo / "src/core/file.py").write_bytes(original)
        self.assertTrue(self.consume()["ok"])
        changed = deepcopy(self.context)
        changed["attempt_id"] = "different-attempt"
        self.write_json(self.paths["context"], changed)
        self.consume(expected=1)
        self.write_json(self.paths["context"], self.context)
        with (self.repo / self.lane["report"]).open("a", encoding="utf-8") as stream:
            stream.write("\nchanged local report\n")
        self.consume(expected=1)

    def test_missing_retyped_downgraded_and_zero_qa_never_clear(self):
        self.prepare()
        cases = []
        missing = deepcopy(self.qa)
        missing["controls"] = []
        cases.append(missing)
        for key, value in (("kind", "check"), ("requirement", "advisory"), ("applicability", "not_applicable")):
            value_qa = deepcopy(self.qa)
            value_qa["controls"][0][key] = value
            cases.append(value_qa)
        zero = deepcopy(self.qa)
        zero["controls"][0]["observation"]["executed"] = 0
        cases.append(zero)
        for value in cases:
            self.write_json(self.paths["qa"], value)
            self.consume(expected=1)
        self.write_json(self.paths["qa"], self.qa)
        self.assertTrue(self.consume()["ok"])

    def test_profile_generation_drift_lost_pin_and_wrong_target_block_without_rebinding(self):
        self.prepare()
        wrong = deepcopy(self.context)
        wrong["profile"]["generation"] += 1
        self.write_json(self.paths["context"], wrong)
        self.consume(expected=1)
        self.write_json(self.paths["context"], self.context)
        pin = profile.context_path(self.config)
        retained = native_io_path(pin).read_bytes()
        native_io_path(pin).unlink()
        missing = self.consume(expected=1)
        self.assertEqual(missing["lanes"][0]["shared_evidence"]["profile_error"]["code"], "PROFILE_CONTEXT_MISSING")
        self.assertFalse(native_io_path(pin).exists())
        native_io_path(pin).write_bytes(retained)
        self.assertTrue(self.consume()["ok"])
        self.write_json(".claude/profile-requirements.json", {"schema_version": 1, "required_pack": "missing-company"})
        drift = self.consume(expected=1)
        self.assertEqual(drift["lanes"][0]["shared_evidence"]["profile_error"]["code"], "PROFILE_DRIFT")
        (self.repo / ".claude/profile-requirements.json").unlink()
        self.assertTrue(self.consume()["ok"])
        other = self.root / "other-repo"
        other.mkdir()
        wrong_config = profile.ProfileConfig(SOURCE, other, self.config.home, self.config.packs, self.config.pointer)
        result, _ = swarm.verify_close(self.repo, self.fixture.coordination_path, profile_config=wrong_config)
        self.assertFalse(result.ok)

    def test_substantive_manual_requires_corroboration_but_mechanical_can_be_explicit(self):
        self.prepare(mechanical=True)
        (self.repo / self.paths["corroboration"]).unlink()
        self.paths["corroboration"] = None
        self.fixture.save()
        self.fixture.write_evidence(self.lane, review_overrides={"mode": "coordinator"})
        self.finalize()
        self.assertTrue(self.consume()["ok"])

    def test_verification_only_no_domain_needs_no_fictitious_product_edit(self):
        self.prepare(verification_only=True)
        self.assertTrue(self.consume()["ok"])
        self.write("src/core/file.py", "a real product edit cannot be verification-only\n")
        self.fixture.write_evidence(self.lane, verification_only=True)
        self.finalize()
        self.consume(expected=1)

    def test_actual_domain_data_is_reverified_and_never_becomes_review(self):
        self.prepare(domain=True)
        result = self.consume()
        domain = result["lanes"][0]["shared_evidence"]["domain"]
        self.assertTrue(domain["ok"])
        self.assertFalse(domain["release_clearance"])
        self.assertEqual(domain["review"], "not_evaluated")
        self.assertEqual(domain["qa"], self.qa)
        (self.repo / self.paths["corroboration"]).unlink()
        self.consume(expected=1)

    def test_missing_domain_start_or_result_and_failed_observation_block_even_after_reprepare(self):
        self.prepare(domain=True)
        result_file = self.repo / self.domain_result_path
        original = result_file.read_bytes()
        result_file.unlink()
        self.finalize()
        self.consume(expected=1)
        result_file.write_bytes(original)
        start_file = self.repo / self.domain_start_path
        start = start_file.read_bytes()
        start_file.unlink()
        self.finalize()
        self.consume(expected=1)
        start_file.write_bytes(start)
        failed = deepcopy(self.domain_result)
        failed["status"] = "fail"
        failed["controls"][0]["status"] = "fail"
        self.write_json(self.domain_result_path, failed)
        self.finalize()
        self.consume(expected=1)
        result_file.write_bytes(original)
        self.finalize()
        self.assertTrue(self.consume()["ok"])

    def test_shared_pointer_hardlinks_and_actor_write_boundaries(self):
        self.prepare()
        for field in ("context", "review", "qa", "corroboration"):
            path = self.repo / self.paths[field]
            original = path.read_bytes()
            path.unlink()
            os.link(self.repo / "plan.md", path)
            self.consume("validate", profile_args=False, expected=1)
            for actor in ("worker", "reviewer"):
                self.assertFalse(swarm.check_lane_scope(
                    self.repo, self.fixture.coordination_path, "BC1", [self.paths[field]], actor=actor,
                ).ok)
            path.unlink()
            path.write_bytes(original)
        self.assertTrue(swarm.check_lane_scope(
            self.repo, self.fixture.coordination_path, "BC1", [self.paths["review"]], actor="reviewer",
        ).ok)
        for actor in ("worker", "reviewer"):
            self.assertFalse(swarm.check_lane_scope(
                self.repo, self.fixture.coordination_path, "BC1", [self.paths["context"]], actor=actor,
            ).ok)

    def test_attempt_leaf_and_corroboration_identity_cannot_be_relabelled(self):
        self.prepare()
        original = (self.repo / self.paths["corroboration"]).read_bytes()
        receipt = json.loads(original)
        for mutation in ("attempt_id", "record_digest", "reviewer"):
            changed = deepcopy(receipt)
            changed[mutation] = {"id": "worker-BC1", "context": "synthetic:worker-BC1"} if mutation == "reviewer" else "wrong"
            self.write_json(self.paths["corroboration"], changed)
            self.consume(expected=1)
        (self.repo / self.paths["corroboration"]).write_bytes(original)
        decision = deepcopy(self.decision)
        decision["coverage"] = {}
        self.write_json(self.paths["review"], decision)
        self.consume(expected=1)
        self.write_json(self.paths["review"], self.decision)
        self.assertTrue(self.consume()["ok"])

    def test_changed_scoped_modes_and_links_cannot_reuse_shared_context(self):
        self.prepare()
        self.git("add", "--", "src")
        self.git("commit", "-qm", "test: selected product commit requires reprepare")
        self.consume(expected=1)
        self.finalize()
        self.assertTrue(self.consume()["ok"])
        self.git("update-index", "--chmod=+x", "--", "src/core/file.py")
        self.consume(expected=1)
        self.git("update-index", "--chmod=-x", "--", "src/core/file.py")
        self.assertTrue(self.consume()["ok"])
        path = self.repo / "src/core/file.py"
        original = path.read_bytes()
        self.write("src/core/copy.py", original.decode("utf-8"))
        path.unlink()
        os.symlink("copy.py", path)
        self.consume(expected=1)
        path.unlink()
        path.write_bytes(original)
        (self.repo / "src/core/copy.py").unlink()
        self.assertTrue(self.consume()["ok"])

    def test_git_fan_in_reprepares_shared_evidence_and_keeps_serial_manual_modes(self):
        heads = []
        for name, path in (("one", "src/core/file.py"), ("two", "docs/parallel.txt")):
            worktree = self.root / name
            self.git("worktree", "add", "-q", "-b", "synthetic-" + name, str(worktree), self.base)
            target = worktree / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("isolated synthetic " + name + "\n", encoding="utf-8")
            common = ["git", "-C", worktree, "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false",
                      "-c", f"core.hooksPath={self.root / 'no-hooks'}", "-c", "user.name=Fixture",
                      "-c", "user.email=fixture@example.invalid"]
            self.run_process([*common, "add", "--", path])
            self.run_process([*common, "commit", "-qm", "test: isolated lane result"])
            heads.append(self.run_process([*common, "rev-parse", "HEAD"]).stdout.strip())
        for head in heads:
            self.git("merge", "--no-ff", "-qm", "test: serial attributable fan-in", head)
            self.git("merge-base", "--is-ancestor", head, "HEAD")
        self.prepare()
        self.assertTrue(self.consume()["ok"])
        for mode in ("native", "sequenced", "none"):
            result = self.run_process([
                sys.executable, "-B", SOURCE / "bin/li-swarm.py", "resume",
                "--repo", self.repo, "--coord", self.fixture.coordination_path, "--host-capability", mode,
                "--profile-home", self.config.home, "--profile-packs", self.config.packs,
                "--profile-pointer", self.config.pointer,
            ])
            self.assertEqual(json.loads(result.stdout)["frontier"]["states"][0]["state"], "complete")
        self.git("add", "--", self.lane["report"], self.lane["review"], "evidence", "src")
        self.git("commit", "-qm", "test: changed selected Git states invalidate precommit context")
        self.consume(expected=1)
        self.finalize()
        self.assertTrue(self.consume()["ok"])
        self.write("unrelated.txt", "unrelated source\n")
        self.git("add", "--", "unrelated.txt")
        self.git("commit", "-qm", "test: unrelated coordinator commit")
        self.assertTrue(self.consume()["ok"])

    def test_non_circular_selection_and_complete_product_scope_are_required(self):
        self.prepare()
        self.request["selection"] = [self.lane["report"], self.lane["review"], "evidence"]
        self.finalize()
        self.consume(expected=1)
        self.request["selection"].append("src/core")
        self.finalize()
        self.assertTrue(self.consume()["ok"])
        context = self.repo / self.paths["context"]
        retained = context.read_bytes()
        self.request["selection"].append(self.paths["context"])
        self.write_json(".claude/runtime/swarm/prepare.json", self.request)
        circular = self.p05("prepare", "--request", self.repo / ".claude/runtime/swarm/prepare.json")
        self.write_json(self.paths["context"], circular)
        self.consume(expected=1)
        context.write_bytes(retained)

    def test_reviewer_cannot_claim_runtime_ledger_as_review_json(self):
        self.paths["review"] = ".claude/runtime/state/operation.json"
        self.fixture.save()
        self.consume("validate", profile_args=False, expected=1)

    def test_manual_human_attestation_is_separate_from_local_actor_names(self):
        self.prepare()
        receipt_path = self.repo / self.paths["corroboration"]
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt.update(kind="human", source="synthetic manual-attestation fixture", reference="not a real person's review")
        self.write_json(self.paths["corroboration"], receipt)
        result = self.consume()
        independence = result["lanes"][0]["shared_evidence"]["review"]["independence"]
        self.assertEqual(independence["provenance"], "human_attested")
        receipt_path.unlink()
        self.consume(expected=1)
        self.assertFalse(self.consume("inspect", profile_args=False)["release_clearance"])

    def test_review_runtime_aliases_reject_all_six_public_gate_cases_without_writes(self):
        slot = self.repo / self.paths["review"]
        slot.parent.mkdir(parents=True, exist_ok=True)
        for target_name in (".claude/runtime/state/operation.json", ".claude/runtime/audit/reviews.jsonl",
                            ".claude/runtime/jobs/current.json"):
            self.write(target_name, '{"synthetic_sentinel":"must remain byte-identical"}\n')
            target = self.repo / target_name
            before = target.read_bytes()
            for kind in ("hardlink", "symlink"):
                with self.subTest(target=target_name, kind=kind):
                    if kind == "hardlink":
                        os.link(target, slot)
                    else:
                        os.symlink(os.path.relpath(target, slot.parent), slot)
                    self.assertTrue(os.path.samefile(target, slot))
                    try:
                        validation = self.run_process([
                            sys.executable, "-B", SOURCE / "bin/li-swarm.py", "validate",
                            "--repo", self.repo, "--coord", self.fixture.coordination_path,
                        ], expected=None)
                        scoped = self.scope_command(self.paths["review"], expected=None)
                        self.assertEqual(target.read_bytes(), before)
                        self.assertEqual((validation.returncode, scoped.returncode), (1, 1),
                                         validation.stdout + scoped.stdout)
                        self.assertFalse(json.loads(validation.stdout)["ok"])
                        self.assertFalse(json.loads(scoped.stdout)["ok"])
                    finally:
                        slot.unlink()
                    self.assertEqual(target.read_bytes(), before)
        self.assertTrue(self.consume("validate", profile_args=False)["ok"])
        self.scope_command(self.paths["review"])

    def test_shared_metadata_rejects_directory_leaves_and_linked_or_file_parents(self):
        original = deepcopy(self.paths)
        for field in ("context", "review", "qa", "corroboration", "domain_request"):
            path = self.repo / (original[field] or ".claude/runtime/swarm/BC1/domain-request.json")
            self.paths[field] = path.relative_to(self.repo).as_posix()
            self.fixture.save()
            path.mkdir(parents=True, exist_ok=True)
            with self.subTest(field=field, kind="directory-leaf"):
                self.consume("validate", profile_args=False, expected=1)
                self.scope_command(self.paths[field], expected=1)
            path.rmdir()
            self.paths.update(original)
        self.fixture.save()
        review_parent = self.repo / ".claude/runtime/reviews"
        review_parent.rmdir()
        target = self.repo / ".claude/runtime/state/alternate-reviews"
        target.mkdir()
        for kind in ("symlink", "junction") if os.name == "nt" else ("symlink",):
            with self.subTest(kind=kind, missing_leaf=True):
                if kind == "junction":
                    self.run_process(["cmd.exe", "/d", "/c", "mklink", "/J", review_parent, target])
                else:
                    os.symlink(target, review_parent, target_is_directory=True)
                try:
                    self.consume("validate", profile_args=False, expected=1)
                    self.scope_command(self.paths["review"], expected=1)
                    self.assertFalse((target / "swarm-BC1.json").exists())
                finally:
                    review_parent.rmdir() if kind == "junction" else review_parent.unlink()
        review_parent.write_text("ordinary file, not a parent", encoding="utf-8")
        self.consume("validate", profile_args=False, expected=1)
        self.scope_command(self.paths["review"], expected=1)
        review_parent.unlink()
        self.assertTrue(self.consume("validate", profile_args=False)["ok"], "safe missing ancestors may be planned")

    def test_reverse_review_alias_path_is_not_the_assigned_reviewer_slot(self):
        slot = self.repo / self.paths["review"]
        self.write_json(self.paths["review"], {"synthetic": "ordinary metadata"})
        before = slot.read_bytes()
        alias = slot.with_name("alternate-review.json")
        for kind in ("symlink", "hardlink"):
            with self.subTest(kind=kind):
                os.symlink(slot.name, alias) if kind == "symlink" else os.link(slot, alias)
                self.assertTrue(os.path.samefile(slot, alias))
                try:
                    self.scope_command(alias.relative_to(self.repo).as_posix(), expected=1)
                    self.assertEqual(slot.read_bytes(), before)
                finally:
                    alias.unlink()
        self.scope_command(self.paths["review"])

    def test_ordinary_coordinator_references_never_grant_reviewer_or_worker_runtime_scope(self):
        for field, path in (
            ("context", ".claude/runtime/state/selected-context.json"),
            ("qa", ".claude/runtime/swarm/BC1/qa.json"),
            ("corroboration", ".claude/runtime/jobs/selected-attestation.json"),
            ("domain_request", ".claude/runtime/state/domains/selected-request.json"),
        ):
            self.paths[field] = path
            self.write_json(path, {"synthetic": "reference only"})
        self.write_json(self.paths["review"], {"synthetic": "reviewer slot"})
        self.fixture.save()
        self.assertTrue(self.consume("validate", profile_args=False)["ok"])
        self.scope_command(self.paths["review"])
        for field in ("context", "qa", "corroboration", "domain_request"):
            for actor in ("worker", "reviewer"):
                with self.subTest(field=field, actor=actor):
                    self.scope_command(self.paths[field], actor=actor, expected=1)
        self.scope_command(self.paths["review"], actor="worker", expected=1)

    def test_actual_p05_containing_directory_selection_covers_lane_and_future_files(self):
        self.prepare()
        self.request["selection"] = ["src" if path == "src/core" else path for path in self.request["selection"]]
        self.finalize()
        accepted = self.p05(
            "ship", "--expected", self.repo / self.paths["context"],
            "--corroboration", self.repo / self.paths["corroboration"],
            "--qa", self.repo / self.paths["qa"], "--skill", "review",
        )
        self.assertTrue(accepted["ok"], "the real shared provider already accepts this complete parent")
        unchanged_context = (self.repo / self.paths["context"]).read_bytes()
        for command in ("status", "wave", "resume", "verify"):
            with self.subTest(command=command):
                self.assertTrue(self.consume(command)["ok"])
        self.assertEqual((self.repo / self.paths["context"]).read_bytes(), unchanged_context)
        self.write("src/core/future.txt", "new file is included by the selected parent\n")
        self.consume(expected=1)
        self.fixture.write_evidence(self.lane)
        self.finalize()
        self.assertTrue(self.consume()["ok"])
        self.assertIn("src/core/future.txt", [entry["path"] for entry in self.context["snapshot"]["entries"]])

    def test_partial_sibling_prefix_or_missing_selection_never_covers_full_lane(self):
        self.prepare()
        self.write("src/core-sibling/item.txt", "sibling")
        self.write("sr/item.txt", "misleading prefix")
        self.write("src2/item.txt", "different sibling")
        metadata = [self.lane["report"], self.lane["review"], "evidence"]
        for selection in ([], ["src/core/file.py"], ["src/core-sibling"], ["sr"], ["src2"]):
            with self.subTest(selection=selection):
                self.request["selection"] = [*selection, *metadata]
                self.finalize()
                self.consume(expected=1)
        self.request["selection"] = ["src", *metadata]
        self.finalize()
        self.assertTrue(self.consume()["ok"])

    def test_actual_p05_parent_selection_retains_a_tracked_directory_deletion(self):
        self.prepare()
        product = self.repo / "src/core/file.py"
        product.unlink()
        product.parent.rmdir()
        product.parent.parent.rmdir()
        self.git("add", "-u", "--", "src/core/file.py")
        self.git("commit", "-qm", "test: reviewed deletion of the scoped directory content")
        head = self.git("rev-parse", "HEAD").stdout.strip()
        self.fixture.write_evidence(self.lane, base=self.base, head=head)
        self.request["selection"] = ["src" if path == "src/core" else path for path in self.request["selection"]]
        self.finalize()
        accepted = self.p05(
            "ship", "--expected", self.repo / self.paths["context"],
            "--corroboration", self.repo / self.paths["corroboration"],
            "--qa", self.repo / self.paths["qa"], "--skill", "review",
        )
        self.assertTrue(accepted["ok"])
        for command in ("status", "wave", "resume", "verify"):
            with self.subTest(command=command):
                self.assertTrue(self.consume(command)["ok"])

    def test_selected_ordinary_file_is_not_a_parent_for_future_scope(self):
        from swarm_evidence import selection_covers_scope

        self.prepare()
        self.request["selection"] = ["src/core/file.py", self.lane["report"], self.lane["review"], "evidence"]
        self.finalize()
        selection = self.context["snapshot"]["selection"]
        self.assertTrue(selection_covers_scope(self.repo, "src/core/file.py", selection))
        self.assertFalse(selection_covers_scope(self.repo, "src/core/file.py/future", selection))
        self.assertFalse(selection_covers_scope(self.repo, "src/core", selection))
        self.consume(expected=1)
        self.assertTrue(selection_covers_scope(self.repo, "src/core/future", ["src"]))
        self.assertFalse(selection_covers_scope(self.repo, "not-created/future", ["not-created"]))

    def test_shared_consumption_rechecks_regular_single_link_metadata(self):
        from swarm_evidence import verify_shared_lane

        self.prepare()
        diagnostics = []
        report = swarm._read_evidence(self.repo / self.lane["report"], "report", "BC1", diagnostics)
        local_review = swarm._read_evidence(self.repo / self.lane["review"], "review", "BC1", diagnostics)
        package = swarm.package_sources(self.repo, self.fixture.coordination)["BC1"]
        self.assertEqual(diagnostics, [])
        context = self.repo / self.paths["context"]
        protected = self.repo / ".claude/runtime/state/operation.json"
        retained = context.read_bytes()
        protected.write_bytes(retained)
        context.unlink()
        os.link(protected, context)
        try:
            result = verify_shared_lane(
                self.repo, self.fixture.coordination_path, self.fixture.coordination,
                self.lane, package, report, local_review, profile_config=self.config,
            )
            self.assertFalse(result["ok"])
            self.assertIn("single-link", " ".join(result["problems"]))
            self.assertEqual(protected.read_bytes(), retained)
        finally:
            context.unlink()
            context.write_bytes(retained)
        self.assertTrue(self.consume()["ok"])

    def test_shared_destination_inspection_errors_never_grant_scope(self):
        self.assertTrue(self.consume("validate", profile_args=False)["ok"])
        original = safety.safe_path

        def refuse_inspection(*args, **kwargs):
            raise PermissionError("synthetic inspection refusal")

        safety.safe_path = refuse_inspection
        try:
            invalid = swarm.validate_coordination(self.repo, self.fixture.coordination_path)
            self.assertFalse(invalid.ok)
            self.assertIn("shared.destination", {item.code for item in invalid.diagnostics})
            rejected = swarm.check_lane_scope(
                self.repo, self.fixture.coordination_path, "BC1", [self.paths["review"]], actor="reviewer",
            )
            self.assertFalse(rejected.ok)
        finally:
            safety.safe_path = original
        self.assertTrue(self.consume("validate", profile_args=False)["ok"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
