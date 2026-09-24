#!/usr/bin/env python3
# component: swarm-shared-binding-tests
# implements: ADR-0027, ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P04.md
# constraints: verified synthetic process roots; real providers; no unaccepted P08 or live actors
# last_intent_review: 2026-09-22
"""Actual P05/P07/P09 consumption; synthetic records are not independent people."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import runpy
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[2]
# Resolve Bash through PATH; Windows process search would otherwise prefer System32's WSL launcher.
BASH = shutil.which("bash") or "bash"
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
            "HOMEDRIVE": self.home.drive, "HOMEPATH": str(self.home)[len(self.home.drive):],
            "GIT_CEILING_DIRECTORIES": self.root.as_posix(), "GIT_ALLOW_PROTOCOL": "",
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
        self.assertEqual(Path(self.env["HOMEDRIVE"] + self.env["HOMEPATH"]).resolve(), self.home)

    def run_process(self, arguments, *, expected=0):
        self.assert_isolation()
        arguments = [str(arg) for arg in arguments]
        input_text = None
        if arguments[0] == "bash":
            input_text = "exec " + shlex.join(arg.replace("\\", "/") for arg in arguments) + "\n"
            arguments = [BASH]
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

    def consume(self, command="verify", *options, expected=0, profile_args=True):
        arguments = [sys.executable, "-B", SOURCE / "bin/li-swarm.py", command,
                     "--repo", self.repo, "--coord", self.fixture.coordination_path, *options]
        if profile_args:
            arguments += ["--profile-home", self.config.home, "--profile-packs", self.config.packs,
                          "--profile-pointer", self.config.pointer]
            if self.config.context_file is not None:
                arguments += ["--profile-context-file", self.config.context_file]
        result = self.run_process(arguments, expected=expected)
        self.last_stderr = result.stderr
        return json.loads(result.stdout or result.stderr)

    def provider_context(self, selected=None, **options):
        self.assert_isolation()
        reader = runpy.run_path(str(SOURCE / "bin/li-work-artifacts.py"))
        return reader["work_context"](self.repo, Path(selected or self.fixture.work_map_path), **options)

    def grouped_map(self, workflow="lintel"):
        self.fixture.work_map["workflow"] = workflow
        self.fixture.work_map["tasks"] = "tasks.md" if workflow == "spec-kit" else "plan.md"
        leaf_ids = ["T011", "T027"] if workflow == "spec-kit" else ["1.1.a", "1.1.b"]
        tasks = (f"- [x] {leaf_ids[0]} Establish baseline\n"
                 f"- [ ] {leaf_ids[1]} Preserve result (depends {leaf_ids[0]})\n")
        plan = ("# Plan\n| Package ID | Leaf IDs | Owner / edit boundary |\n"
                "|---|---|---|\n| BC1 | " + ", ".join(leaf_ids) + " | builder; src/core |\n\n")
        self.write("plan.md", plan + (tasks if workflow == "lintel" else ""))
        if workflow == "spec-kit":
            self.write("tasks.md", tasks)
        self.fixture.save()
        return leaf_ids

    def decoy_map(self):
        selected = ".claude/plans/decoy/work.json"
        mapping = {key: value for key, value in self.fixture.work_map.items()
                   if key not in ("execution_mode", "coordination")}
        for key in ("spec", "plan", "tasks", "prompt"):
            mapping[key] = ".claude/plans/decoy/" + key + ".md"
            self.write(mapping[key], (self.repo / self.fixture.work_map[key]).read_text(encoding="utf-8"))
        self.write_json(selected, mapping)
        return selected

    def filesystem_state(self):
        self.assert_isolation()
        root = native_io_path(self.root)
        return {path.relative_to(root).as_posix():
                ("directory" if path.is_dir() else "file", path.lstat().st_mode,
                 path.lstat().st_mtime_ns, None if path.is_dir() else path.read_bytes())
                for path in root.rglob("*")}

    def workflow(self, body, *arguments, expected=0):
        script = ('set -euo pipefail\nexport _LINTEL_PROFILE_PYTHON="$LINTEL_PYTHON"\n'
                  'source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"\n' + body)
        return self.run_process(["bash", "--noprofile", "--norc", "-c", script, "swarm-cycle-fixture",
                                 *arguments], expected=expected)

    def begin_cycle(self, cycle="original", selected=None, *, phase="BUILD", config=None):
        config = config or self.config
        self.assert_isolation()
        reference = profile.profile_reference(profile.load_profile_context(config))
        return self.workflow(
            'export LINTEL_PROFILE_REFERENCE="$3" LINTEL_PROFILE_CONTEXT_FILE="$4"\n'
            'workflow_begin "$1" full "$2" operation=build\n'
            'state_phase_begin "$5" next=REVIEW\n',
            cycle, selected or self.fixture.work_map_path, encoded(reference),
            profile.context_path(config).as_posix(), phase,
        )

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
        leaves = swarm.package_sources(self.repo, self.fixture.coordination)["BC1"]["leaf_ids"]
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
            "schema_version": review.CONTRACT_VERSION, "skill": self.paths["review_skill"], "status": "pass",
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

    def test_review_skill_preflight_consumes_the_actual_p05_grammar(self):
        schema = json.loads((SOURCE / "lib/swarm-schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$defs"]["sharedEvidence"]["properties"]["review_skill"],
                         {"$ref": "review-schema.json#/$defs/skill"})
        for value in ("1-review", "Review", "review_skill", "review.skill", "review skill", "", None, 4):
            with self.subTest(value=value):
                with self.assertRaises(review.ContractError):
                    review.validate_shape(value, "skill")
                self.paths["review_skill"] = value
                self.fixture.save()
                rejected = self.consume("validate", profile_args=False, expected=1)
                self.assertIn("shared.skill", {item["code"] for item in rejected["diagnostics"]})
        for value in ("review", "plan-eng-review", "review-" + "a" * 96):
            with self.subTest(value=value):
                review.validate_shape(value, "skill")
                self.paths["review_skill"] = value
                self.fixture.save()
                self.assertTrue(self.consume("validate", profile_args=False)["ok"])

    def test_long_p05_skill_name_reaches_actual_log_and_all_shared_consumers(self):
        self.paths["review_skill"] = "review-" + "a" * 96
        self.fixture.save()
        self.prepare()
        for command in ("status", "wave", "resume", "verify"):
            with self.subTest(command=command):
                self.assertTrue(self.consume(command)["ok"])

    def test_selected_work_is_the_actual_provider_view_with_original_alias_and_no_writes(self):
        self.prepare()
        selected = self.provider_context()
        before = {path: path.read_bytes() for path in self.repo.rglob("*")
                  if path.is_file() and ".git" not in path.relative_to(self.repo).parts}
        for command in ("status", "wave", "resume", "verify"):
            with self.subTest(command=command):
                result = self.consume(command, "--map", self.fixture.work_map_path)
                self.assertEqual(result["work_context"], selected)
                self.assertEqual(result["work_context"]["artifacts"]["plan"],
                                 result["work_context"]["artifacts"]["tasks"])
                self.assertFalse(result["work_context"]["release_clearance"])
                self.assertIsNone(result["work_context"]["binding"])
        self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_grouped_tree_and_spec_kit_leaves_match_the_actual_work_provider(self):
        for workflow in ("lintel", "spec-kit"):
            with self.subTest(workflow=workflow):
                leaf_ids = self.grouped_map(workflow)
                self.prepare()
                selected = self.provider_context()
                self.assertEqual(selected["packages"]["BC1"]["leaf_ids"], leaf_ids)
                for command in ("status", "wave", "resume", "verify"):
                    result = self.consume(command, "--map", self.fixture.work_map_path)
                    self.assertEqual(result["work_context"], selected)
                    self.assertEqual(result["work_context"]["packages"]["BC1"]["leaf_ids"], leaf_ids)

    def test_explicit_other_map_and_backpointer_mismatch_block_every_consumer(self):
        self.grouped_map("spec-kit")
        self.prepare()
        decoy = self.decoy_map()
        for command in ("status", "wave", "resume", "verify"):
            with self.subTest(command=command):
                rejected = self.consume(command, "--map", decoy, expected=1)
                self.assertIn("work.selection", {item["code"] for item in rejected["diagnostics"]})
                self.assertTrue(self.consume(command, "--map", self.fixture.work_map_path)["ok"])
        original = self.fixture.work_map["coordination"]
        self.fixture.work_map["coordination"] = ".claude/plans/decoy/coordination.json"
        self.fixture.save()
        try:
            for command in ("status", "wave", "resume", "verify"):
                self.assertFalse(self.consume(command, expected=1)["ok"])
        finally:
            self.fixture.work_map["coordination"] = original
            self.fixture.save()

    def test_missing_empty_or_oversized_selected_input_fails_before_shared_gate(self):
        self.prepare()
        prompt = self.repo / self.fixture.work_map["prompt"]
        retained = prompt.read_bytes()
        decoy = self.decoy_map()
        self.env["LINTEL_WORK_MAP"] = decoy
        for value in (None, b" \n", b"x" * 262145):
            with self.subTest(value="missing" if value is None else len(value)):
                if value is None:
                    prompt.unlink()
                else:
                    prompt.write_bytes(value)
                try:
                    with self.assertRaises(ValueError):
                        self.provider_context()
                    for command in ("status", "wave", "resume", "verify"):
                        rejected = self.consume(command, expected=1)
                        self.assertIn("work.selection", {item["code"] for item in rejected["diagnostics"]})
                finally:
                    prompt.write_bytes(retained)
        self.assertTrue(self.consume()["ok"])

    def test_target_reader_and_workflow_decoys_are_data_not_source(self):
        self.prepare()
        self.begin_cycle()
        self.write("bin/li-work-artifacts.py", "raise RuntimeError('TARGET READER MUST NOT EXECUTE')\n")
        self.write("lib/workflow.sh", "echo target-workflow-ran > TARGET-EXECUTED\nexit 97\n")
        previous = self.env["LINTEL_SOURCE_ROOT"]
        self.env["LINTEL_SOURCE_ROOT"] = self.repo.as_posix()
        try:
            for command in ("status", "wave", "resume", "verify"):
                result = self.consume(command)
                self.assertEqual(result["work_context"]["work_map"], self.fixture.work_map_path)
                self.assertFalse((self.repo / "TARGET-EXECUTED").exists())
            before = self.filesystem_state()
            resumed = self.consume("resume", "--cycle-id", "original")
            self.assertEqual(resumed["recovery"]["mode"], "persisted-cycle")
            self.assertEqual(self.filesystem_state(), before)
            self.assertFalse((self.repo / "TARGET-EXECUTED").exists())
        finally:
            self.env["LINTEL_SOURCE_ROOT"] = previous

    def test_original_task_progress_is_not_clearance_or_a_new_acceptance_hash(self):
        leaf_ids = self.grouped_map("spec-kit")
        self.prepare()
        binding = self.context["work"]
        task_file = self.repo / self.fixture.work_map["tasks"]
        task_file.write_text(task_file.read_text(encoding="utf-8").replace("[ ] " + leaf_ids[1],
                                                                         "[x] " + leaf_ids[1]), encoding="utf-8")
        selected = self.provider_context(package_id="BC1", leaf_ids=leaf_ids,
                                         acceptance_paths=binding["acceptance_paths"])
        self.assertEqual(selected["binding"], binding)
        self.assertEqual(selected["incomplete_ids"], [])
        self.assertFalse(selected["release_clearance"])
        self.assertTrue(self.consume()["ok"])
        (self.repo / self.paths["corroboration"]).unlink()
        self.assertFalse(self.consume(expected=1)["ok"])
        self.finalize()
        task_file.write_text(task_file.read_text(encoding="utf-8").replace("Preserve result", "Change acceptance"),
                             encoding="utf-8")
        self.assertNotEqual(self.provider_context(package_id="BC1", leaf_ids=leaf_ids,
                                                 acceptance_paths=binding["acceptance_paths"])["binding"], binding)
        for command in ("status", "wave", "resume", "verify"):
            self.assertFalse(self.consume(command, expected=1)["ok"])

    def test_artifact_only_resume_keeps_host_modes_without_reading_runtime(self):
        self.prepare(verification_only=True)
        state = self.repo / ".claude/runtime/state/00-state.md"
        state.write_text("not a selected cycle\n", encoding="utf-8")
        retained = state.read_bytes()
        self.env["LINTEL_CYCLE_ID"] = "ambient-decoy"
        for mode in ("native", "sequenced", "none"):
            result = self.consume("resume", "--host-capability", mode)
            self.assertEqual(result["recovery"], {"mode": "artifact-only", "release_clearance": False})
            self.assertEqual(result["frontier"]["states"][0]["state"], "complete")
            self.assertFalse(result["release_clearance"])
        (self.repo / self.lane["report"]).unlink()
        (self.repo / self.lane["review"]).unlink()
        for mode in ("native", "sequenced", "none"):
            result = self.consume("resume", "--host-capability", mode)
            self.assertEqual(result["frontier"]["host_capability"], mode)
            self.assertEqual(result["frontier"]["dispatch_task_ids"], ["BC1"])
            self.assertEqual(result["frontier"]["states"][0]["state"], "not_started")
        self.assertEqual(state.read_bytes(), retained)

    def test_cold_cycle_resume_uses_actual_provider_and_original_not_newer_initiative(self):
        self.grouped_map("spec-kit")
        self.prepare()
        decoy = self.decoy_map()
        self.begin_cycle()
        self.begin_cycle("newer-decoy", decoy, phase="SENSE")
        direct = json.loads(self.workflow('workflow_resume "$1" "$2"\n',
                                         "original", self.fixture.work_map_path).stdout)
        before = self.filesystem_state()
        result = self.consume("resume", "--cycle-id", "original", "--map", self.fixture.work_map_path)
        self.assertEqual(result["recovery"], {"mode": "persisted-cycle", **direct})
        self.assertEqual(result["recovery"]["phase"], "BUILD")
        self.assertEqual(result["recovery"]["operation"], "build")
        self.assertEqual(result["recovery"]["profile"], self.reference)
        self.assertEqual(result["recovery"]["required_policy"], self.policy)
        self.assertFalse(result["recovery"]["release_clearance"])
        self.assertEqual(result["work_context"]["packages"]["BC1"]["leaf_ids"], ["T011", "T027"])
        self.assertEqual(result["frontier"]["states"][0]["state"], "complete")
        self.assertEqual(self.filesystem_state(), before)

    def test_requested_absent_or_other_cycle_never_falls_back_or_executes_identifiers(self):
        self.prepare()
        decoy = self.decoy_map()
        self.begin_cycle()
        self.begin_cycle("other", decoy, phase="SENSE")
        before = self.filesystem_state()
        for cycle in ("missing", "other", "original; touch CYCLE-INJECTION"):
            with self.subTest(cycle=cycle):
                rejected = self.consume("resume", "--cycle-id", cycle, expected=2)
                self.assertFalse(rejected["ok"])
                self.assertIn("work.resume", {item["code"] for item in rejected["diagnostics"]})
                self.assertNotIn("recovery", rejected)
                self.assertEqual(self.filesystem_state(), before)
        rejected = self.consume("resume", "--cycle-id", "", expected=1)
        self.assertFalse(rejected["ok"])
        self.assertEqual(self.filesystem_state(), before)

    def test_missing_or_drifted_resume_pin_emits_diagnostics_without_any_filesystem_write(self):
        self.begin_cycle()
        audit = self.repo / ".claude/runtime/audit"
        self.assertEqual(list(audit.iterdir()), [])
        audit.rmdir()
        global_audit = self.config.home / "audit"
        self.assertFalse(global_audit.exists())
        pin = native_io_path(profile.context_path(self.config))
        retained = pin.read_bytes()
        declaration = self.repo / ".claude/profile-requirements.json"
        for condition in ("missing", "drift"):
            with self.subTest(condition=condition):
                if condition == "missing":
                    pin.unlink()
                else:
                    self.write_json(".claude/profile-requirements.json",
                                    {"schema_version": 1, "required_pack": "unavailable-synthetic-profile"})
                try:
                    before = self.filesystem_state()
                    rejected = self.consume("resume", "--cycle-id", "original", expected=2)
                    self.assertFalse(rejected["ok"])
                    self.assertIn("not-persisted", self.last_stderr)
                    event = next(line for line in self.last_stderr.splitlines()
                                 if line.startswith("lintel-swarm resume diagnostic (not-persisted):"))
                    self.assertEqual(shlex.split(event.split(":", 1)[1]), [
                        "pack-resolver", "pack_resolver_fail", "msg=operation=verify profile-context-unresolved",
                    ])
                    self.assertEqual(self.filesystem_state(), before)
                    self.assertFalse(audit.exists())
                    self.assertFalse(global_audit.exists())
                    if condition == "missing":
                        self.assertFalse(pin.exists())
                finally:
                    if condition == "missing":
                        pin.write_bytes(retained)
                    else:
                        declaration.unlink()

    def test_saved_profile_generation_and_policy_mismatches_preserve_resume_state(self):
        self.begin_cycle()
        ledger = self.repo / ".claude/runtime/state/00-state.md"
        original = ledger.read_text(encoding="utf-8")
        reference = deepcopy(self.reference)
        reference["generation"] += 1
        policy = deepcopy(self.policy)
        policy["version"] = "different-synthetic-policy"
        for field, replacement in (("profile_reference", reference), ("required_policy", policy)):
            with self.subTest(field=field):
                lines = [field + ": " + review.canonical_json(replacement) if line.startswith(field + ":")
                         else line for line in original.splitlines()]
                ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
                before = self.filesystem_state()
                self.assertFalse(self.consume("resume", "--cycle-id", "original", expected=2)["ok"])
                self.assertEqual(self.filesystem_state(), before)
        ledger.write_text(original, encoding="utf-8")

    def test_truncated_transition_preserves_interrupted_phase_despite_complete_lane(self):
        self.prepare()
        self.begin_cycle()
        self.workflow('state_append BUILD DONE cycle_id=original next=REVIEW\n')
        ledger = self.repo / ".claude/runtime/state/00-state.md"
        ledger.write_bytes(b"\n".join(ledger.read_bytes().splitlines()[:-1]) + b"\n")
        before = self.filesystem_state()
        result = self.consume("resume", "--cycle-id", "original")
        self.assertEqual(result["recovery"]["phase"], "BUILD")
        self.assertFalse(result["recovery"]["release_clearance"])
        self.assertEqual(result["frontier"]["states"][0]["state"], "complete")
        self.assertEqual(self.filesystem_state(), before)

    def test_cycle_profile_cannot_be_replaced_by_another_valid_shared_context(self):
        self.prepare()
        other = replace(self.config, context_id="second-valid-context")
        self.assert_isolation()
        other_reference = profile.profile_reference(profile.load_profile_context(other, create=True))
        self.begin_cycle(config=other)
        before = self.filesystem_state()
        rejected = self.consume("resume", "--cycle-id", "original", expected=1)
        self.assertEqual(rejected["recovery"]["profile"], other_reference)
        self.assertEqual(rejected["frontier"]["states"][0]["state"], "awaiting_shared_evidence")
        self.assertEqual(self.filesystem_state(), before)
        self.config, self.reference = other, other_reference
        self.prepare()
        self.assertTrue(self.consume("resume", "--cycle-id", "original")["ok"])

    def test_explicit_state_and_profile_file_are_used_without_ambient_reselection(self):
        state = self.repo / ".claude/runtime/state explicit"
        state.mkdir()
        self.env["LINTEL_STATE_DIR"] = state.as_posix()
        self.config = replace(self.config, context_file=profile.context_path(self.config))
        self.assert_isolation()
        self.reference = profile.profile_reference(profile.load_profile_context(self.config))
        self.prepare(verification_only=True)
        self.begin_cycle()
        self.env["LINTEL_STATE_DIR"] = (self.repo / ".claude/runtime/unrelated-state").as_posix()
        before = self.filesystem_state()
        result = self.consume("resume", "--cycle-id", "original", "--state-dir", state)
        self.assertTrue(result["ok"])
        self.assertEqual(result["recovery"]["profile"], self.reference)
        self.assertEqual(result["recovery"]["phase"], "BUILD")
        self.assertEqual(self.filesystem_state(), before)
        self.assertFalse(self.consume("resume", "--cycle-id", "original", expected=2)["ok"])
        self.assertFalse(self.consume("resume", "--state-dir", state, expected=1)["ok"])
        self.assertEqual(self.filesystem_state(), before)

    def test_cycle_resume_in_another_target_cannot_transfer_the_profile_pin(self):
        self.prepare()
        self.begin_cycle()
        other = self.root / "other-target"
        shutil.copytree(self.repo, other, ignore=shutil.ignore_patterns(".git"))
        before = self.filesystem_state()
        observed = self.run_process([
            sys.executable, "-B", SOURCE / "bin/li-swarm.py", "resume", "--repo", other,
            "--coord", self.fixture.coordination_path, "--cycle-id", "original",
            "--state-dir", other / ".claude/runtime/state",
            "--profile-home", self.config.home, "--profile-packs", self.config.packs,
            "--profile-pointer", self.config.pointer,
        ], expected=2)
        self.assertFalse(json.loads(observed.stdout)["ok"])
        self.assertEqual(self.filesystem_state(), before)

    def test_cycle_aware_domain_data_and_later_rejection_keep_the_original_shared_gate(self):
        self.prepare(domain=True)
        self.begin_cycle()
        before = self.filesystem_state()
        result = self.consume("resume", "--cycle-id", "original")
        domain = result["frontier"]["states"][0]["shared_evidence"]["domain"]
        self.assertTrue(domain["ok"])
        self.assertFalse(domain["release_clearance"])
        self.assertEqual(domain["review"], "not_evaluated")
        self.assertEqual(self.filesystem_state(), before)
        path = self.repo / self.domain_result_path
        retained = path.read_bytes()
        path.unlink()
        self.finalize()
        self.assertFalse(self.consume("resume", "--cycle-id", "original", expected=1)["ok"])
        path.write_bytes(retained)
        self.finalize()
        original = deepcopy(self.decision)
        self.decision["status"] = "fail"
        self.log()
        self.write_json(self.paths["review"], original)
        rejected = self.consume("resume", "--cycle-id", "original", expected=1)
        self.assertEqual(rejected["frontier"]["states"][0]["state"], "awaiting_shared_evidence")
        self.decision = original
        self.log()
        self.assertTrue(self.consume("resume", "--cycle-id", "original")["ok"])

    def test_named_legacy_singleton_keeps_the_original_swarm_parser_contract(self):
        self.lane["task_id"] = "core"
        self.write("plan.md", "# Plan\n### core Core implementation\n")
        self.fixture.save()
        self.assertTrue(swarm.validate_coordination(self.repo, self.fixture.coordination_path).ok)
        original = swarm.package_sources(self.repo, self.fixture.coordination)["core"]
        self.assertEqual(original["leaf_ids"], ["core"])
        for command in ("status", "wave", "resume"):
            with self.subTest(command=command):
                result = self.consume(command)
                self.assertEqual(result["work_context"]["packages"]["core"], original)
                self.assertFalse(result["work_context"]["release_clearance"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
