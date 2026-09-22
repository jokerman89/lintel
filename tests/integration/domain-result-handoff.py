#!/usr/bin/env python3
# component: domain-result-handoff-tests
# implements: ADR-0028, ADR-0029, ADR-0031
# intent: .claude/plans/universal-implementation/packages/P09.md
# constraints: synthetic accepted P03/P05/P07 links only; no P08, install or domain actions
# last_intent_review: 2026-09-22
"""Real data CLI and fresh-process evidence consumers; not live specialist behavior."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--root", type=Path, required=True)
parser.add_argument("--bash", required=True)
parser.add_argument("--git", required=True)
options, test_args = parser.parse_known_args()
SOURCE = options.root.resolve()
sys.path.insert(0, str(SOURCE / "lib"))
import context_safety as safety
from profile_context import ProfileConfig, load_profile_context, profile_reference, required_policy
from review_contract import content_digest, evidence_manifest, validate_context, verify_qa

ARTIFACTS = SOURCE / ".claude/runtime/p09-data-core" / uuid.uuid4().hex[:12]
safety.native_io_path(ARTIFACTS).mkdir(parents=True)
CHECK_CODE = (
    "import unittest\n"
    "class Synthetic(unittest.TestCase):\n"
    " def test_observation(self): self.assertEqual(2 + 2, 4)\n"
    "unittest.main()\n"
)


def encoded(data: object) -> bytes:
    return (json.dumps(data, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n").encode()


class DomainHandoff(unittest.TestCase):
    maxDiff = 1200

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="lintel-domain-")
        self.base = Path(self.temp.name).absolute()
        self.addCleanup(self.cleanup)
        self.repo = self.base / "target"
        self.home = self.base / "home"
        self.repo.mkdir()
        self.home.mkdir()
        self.counter = 0
        self.logs = ARTIFACTS / self.id().split(".")[-1]
        safety.native_io_path(self.logs).mkdir()
        self.env = {key: os.environ[key] for key in (
            "PATH", "PATHEXT", "SystemRoot", "WINDIR", "SystemDrive", "COMSPEC",
        ) if key in os.environ}
        self.env.update({
            "PATH": os.pathsep.join((str(Path(options.git).parent), str(Path(options.bash).parent),
                                     str(Path(sys.executable).parent), self.env.get("PATH", ""))),
            "HOME": str(self.home), "USERPROFILE": str(self.home),
            "APPDATA": str(self.home / "AppData/Roaming"),
            "LOCALAPPDATA": str(self.home / "AppData/Local"),
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_CACHE_HOME": str(self.home / ".cache"),
            "XDG_DATA_HOME": str(self.home / ".local/share"),
            "TEMP": str(self.base / "tmp"), "TMP": str(self.base / "tmp"),
            "TMPDIR": str(self.base / "tmp"), "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CEILING_DIRECTORIES": str(self.base),
            "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never",
            "LINTEL_REPO_ROOT": self.repo.as_posix(), "LINTEL_SOURCE_ROOT": SOURCE.as_posix(),
            "LINTEL_PYTHON": Path(sys.executable).as_posix(),
            "LINTEL_HOME": (self.home / ".lintel").as_posix(),
            "LINTEL_PACKS_DIR": (self.home / ".lintel/packs").as_posix(),
            "LINTEL_ACTIVE_PACK_FILE": (self.home / ".lintel/packs/active-pack").as_posix(),
            "LINTEL_AUDIT_DIR": (self.repo / ".claude/runtime/audit").as_posix(),
        })
        for key in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME",
                    "XDG_CACHE_HOME", "XDG_DATA_HOME", "TEMP", "TMP", "TMPDIR", "LINTEL_HOME",
                    "LINTEL_PACKS_DIR", "LINTEL_AUDIT_DIR"):
            path = Path(self.env[key])
            self.assertTrue(path.is_relative_to(self.base))
            path.mkdir(parents=True, exist_ok=True)
            safety.checked_root(path)
        self.assertTrue(self.env.get("PATHEXT") or os.name != "nt")
        self.assertFalse(any(key in self.env for key in (
            "GH_TOKEN", "GITHUB_TOKEN", "BASH_ENV", "PYTHONPATH", "PACK_CACHE_FILE",
            "LINTEL_PROFILE_REFERENCE", "GIT_CONFIG_COUNT",
        )))
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/synthetic")
        self.write(".gitignore", b".claude/runtime/\n")
        self.write(".claude/lintel-layout.yaml", b"layout_version: 5\n")
        self.write("spec.md", b"# Synthetic acceptance\nR1: retain exact domain evidence.\n")
        self.write("plan.md", b"- [ ] T014 Produce scoped evidence\n")
        self.write("prompt.md", b"Execute only the synthetic data evidence case.\n")
        self.write("source.txt", b"synthetic source\n")
        self.write_json("preferences.json", {"latency_advice_ms": 120})
        self.write_json("work.json", {
            "schema_version": 1, "workflow": "spec-kit", "status": "APPROVED",
            "spec": "spec.md", "plan": "plan.md", "tasks": "plan.md", "prompt": "prompt.md",
        })
        self.write_json(".claude/profile-requirements.json",
                        {"schema_version": 1, "required_pack": "synthetic-strict"})
        self.pack = self.home / ".lintel/packs/synthetic-strict/pack.yaml"
        self.pack.parent.mkdir()
        self.pack.write_text(
            "name: synthetic-strict\nversion: 1.0.0\nvoice: {default_tier: internal}\n"
            "compliance: {mode: hard, hooks: [synthetic-evidence]}\n"
            "navigation: {default_workflow: cycle}\n", encoding="utf-8",
        )
        self.config = ProfileConfig(
            SOURCE, self.repo, self.home / ".lintel", self.pack.parent.parent,
            self.pack.parent.parent / "active-pack", context_id="synthetic-domain-context",
        )
        profile = load_profile_context(self.config, create=True)
        self.reference = profile_reference(profile)
        self.policy = required_policy(profile)
        self.git("add", ".")
        self.git("commit", "-qm", "test: establish synthetic data fixture")
        self.base_ref = self.git("rev-parse", "HEAD").stdout.strip()
        self.request_path = "domain-request.json"
        self.expected_path = ".claude/runtime/meta/final-context.json"
        self.file_states = {}
        self.controls = []
        self.results = {}

    def cleanup(self) -> None:
        base = Path(self.temp.name).absolute()
        self.assertEqual(base, self.base)
        self.assertTrue(base.name.startswith("lintel-domain-"))
        safety.checked_root(base)
        if os.name == "nt":
            self.temp.name = str(safety.native_io_path(base))
        self.temp.cleanup()

    def run_process(self, args, *, expected=0, cwd=None, env=None):
        self.counter += 1
        stem = self.logs / str(self.counter)
        argv = [str(arg) for arg in args]
        with safety.native_io_path(stem.with_suffix(".stdout.log")).open("wb") as out, \
                safety.native_io_path(stem.with_suffix(".stderr.log")).open("wb") as err:
            result = subprocess.run(argv, cwd=cwd or self.repo, env=env or self.env,
                                    stdout=out, stderr=err, timeout=60, check=False)
        stdout = safety.native_io_path(stem.with_suffix(".stdout.log")).read_text(encoding="utf-8")
        stderr = safety.native_io_path(stem.with_suffix(".stderr.log")).read_text(encoding="utf-8")
        safety.native_io_path(stem.with_suffix(".json")).write_bytes(encoded({
            "argv": argv, "cwd": str(cwd or self.repo), "exit_code": result.returncode,
            "synthetic_home": self.env["HOME"], "ceiling": self.env["GIT_CEILING_DIRECTORIES"],
        }))
        if expected is not None:
            self.assertEqual(expected, result.returncode, (stdout + stderr)[-2000:])
        return subprocess.CompletedProcess(argv, result.returncode, stdout, stderr)

    def git(self, *args):
        return self.run_process([
            options.git, "--no-pager", "-c", "core.autocrlf=false",
            "-c", "core.fsmonitor=false", "-c", f"core.hooksPath={self.base / 'hooks'}",
            "-c", "user.name=Synthetic fixture", "-c", "user.email=fixture@example.invalid", *args,
        ])

    def write(self, relative: str, data: bytes) -> None:
        safety.atomic_write(safety.checked_root(self.repo), relative, data)

    def write_json(self, relative: str, data: object) -> None:
        self.write(relative, encoded(data))

    def read_json(self, relative: str):
        return json.loads(safety.read_owned(self.repo, relative)[0])

    def ref(self, relative: str) -> dict:
        return {"path": relative, "sha256": safety.read_owned(self.repo, relative)[1]["sha256"]}

    def p05(self, *args, expected=0):
        return self.run_process([sys.executable, "-B", SOURCE / "bin/li-review-evidence.py",
                                 *args], expected=expected)

    def cli(self, command, *args, expected=0, source=SOURCE, cwd=None, env=None):
        return self.run_process([sys.executable, "-B", source / "bin/li-domain-result.py",
                                 command, "--repo", self.repo, *args],
                                expected=expected, cwd=cwd, env=env)

    def profile_args(self):
        return ["--profile-home", self.config.home, "--profile-packs", self.config.packs,
                "--profile-pointer", self.config.pointer]

    def prepare_request(self, domains=("ta",), *, mode="analysis") -> None:
        requirements = [{
            "id": f"{domain}-check", "kind": "tests", "requirement": "mandatory",
            "applicability": "applicable",
            "policy": {"source": "spec.md", "version": "synthetic-1",
                       "applicability": "Synthetic selected evidence", "jurisdiction": None,
                       "actor": None, "effective_date": None},
        } for domain in domains]
        self.prepare_input = {
            "work_map": "work.json", "package_id": "P09", "leaf_ids": ["T014"],
            "acceptance_paths": ["spec.md", "plan.md"], "base": self.base_ref,
            "selection": ["source.txt", "preferences.json"],
            "record_path": ".claude/runtime/reviews/domain-review.json",
            "attempt_id": "synthetic-attempt", "builder": {"id": "synthetic-builder", "context": "build-1"},
            "independence_required": True, "purpose": "implementation", "profile": self.reference,
            "required_policy": self.policy, "required_controls": ["spec", "quality", *[r["id"] for r in requirements]],
            "qa_requirements": requirements,
        }
        self.write_json(".claude/runtime/meta/prepare.json", self.prepare_input)
        initial = json.loads(self.p05("prepare", "--repo", self.repo, "--request",
                                     self.repo / ".claude/runtime/meta/prepare.json").stdout)
        validate_context(initial)
        self.request = {
            "schema_version": 1, "kind": "domain-request", "operation_id": "synthetic",
            "iteration": 1, "input_context": initial, "advisory_preferences": {"latency_advice_ms": 120},
            "domains": [], "release_clearance": False,
        }
        self.record_root = ".claude/runtime/state/domains/synthetic/i0001"
        for domain in domains:
            checkpoint = {
                "id": "analysis_done", "receiver": {"role": "SystemArchitect", "mode": mode},
                "control_ids": [f"{domain}-check"], "artifacts": [f"artifacts/{domain}.txt"],
                "start": {"path": f"{self.record_root}/{domain}/01-start.json", "expected_state": None},
                "result": {"path": f"{self.record_root}/{domain}/01-result.json", "expected_state": None},
            }
            self.request["domains"].append({"id": domain, "checkpoints": [checkpoint]})
        self.write_json(self.request_path, self.request)
        self.write_json(".claude/runtime/meta/absent.json", {"state": None})

    def publish(self, record: dict, path: str, *, expected=0, original_state=None):
        self.write_json(".claude/runtime/meta/payload.json", record)
        state_path = ".claude/runtime/meta/absent.json"
        if original_state is not None:
            state_path = ".claude/runtime/meta/original-state.json"
            self.write_json(state_path, {"state": original_state})
        return self.cli("record", "--request", self.request_path,
                        "--file", ".claude/runtime/meta/payload.json", "--output", path,
                        "--expected-state", state_path, expected=expected)

    def produce(self, *, status="pass", score=95) -> None:
        for domain in self.request["domains"]:
            checkpoint = domain["checkpoints"][0]
            common = {
                "schema_version": 1, "request": self.ref(self.request_path), "domain": domain["id"],
                "checkpoint": checkpoint["id"], "receiver": checkpoint["receiver"],
                "producer": self.request["input_context"]["builder"],
                "provenance": "declared", "release_clearance": False,
            }
            start = {**common, "kind": "domain-checkpoint"}
            published = json.loads(self.publish(start, checkpoint["start"]["path"]).stdout)
            self.assertEqual("not_performed", published["verification"])
            self.assertFalse(published["release_clearance"])
            run = self.run_process([sys.executable, "-I", "-B", "-c", CHECK_CODE])
            executed = int(re.search(r"Ran (\d+) test", run.stderr).group(1))
            self.assertEqual(1, executed)
            evidence = f"evidence/{domain['id']}.txt"
            self.write(evidence, (run.stdout + run.stderr).encode("utf-8"))
            artifact = checkpoint["artifacts"][0]
            self.write(artifact, b"Synthetic R1 decision: retain the measured result; no live system claim.\n")
            requirement = next(r for r in self.request["input_context"]["qa_requirements"]
                               if r["id"] == checkpoint["control_ids"][0])
            control = {**deepcopy(requirement), "status": status, "reason": "Actual synthetic test output.",
                       "evidence": [evidence], "observation": {
                           "command": "python -I -B -c <synthetic unittest>",
                           "executed": executed, "failed": 0, "skipped": 0, "exit_code": run.returncode,
                       }}
            record = {
                **common, "kind": "domain-result", "start": self.ref(checkpoint["start"]["path"]),
                "status": status, "reason": "Synthetic checkpoint observation.",
                "controls": [control], "evidence": evidence_manifest(self.repo, [control]),
                "artifacts": [self.ref(artifact)],
                "decisions": [{"requirement": "R1", "rationale": "Preserve actual evidence.",
                               "artifact": artifact}],
                "limitations": ["No live specialist or domain action executed."],
                "next": {"owner": "coordinator", "action": "Arrange independent review."},
                "advisory_score": score,
            }
            self.publish(record, checkpoint["result"]["path"],
                         original_state=checkpoint["result"]["expected_state"])
            self.results[domain["id"]] = record
            self.controls.append(control)

    def prepare_final(self, *, omit=None) -> dict:
        final = deepcopy(self.prepare_input)
        final["selection"] += [self.request_path, self.record_root, "artifacts", "evidence"]
        if omit:
            final["selection"].remove(omit)
        self.write_json(".claude/runtime/meta/final-prepare.json", final)
        expected = json.loads(self.p05(
            "prepare", "--repo", self.repo, "--request",
            self.repo / ".claude/runtime/meta/final-prepare.json",
        ).stdout)
        self.write_json(self.expected_path, expected)
        return expected

    def verify(self, *, command="verify", expected=0):
        run = self.cli(command, "--request", self.request_path, "--expected", self.expected_path,
                       *self.profile_args(), expected=expected)
        return json.loads(run.stdout)

    def result_path(self, domain="ta"):
        return next(d["checkpoints"][0]["result"]["path"] for d in self.request["domains"] if d["id"] == domain)

    def test_real_producer_cli_fresh_verifier_and_qa(self) -> None:
        self.prepare_request()
        syntax = json.loads(self.cli("validate", "--file", self.request_path).stdout)
        self.assertEqual("not_performed", syntax["verification"])
        self.produce()
        expected = self.prepare_final()
        for command in ("verify", "summary"):
            observed = self.verify(command=command)
            self.assertTrue(observed["ok"])
            self.assertFalse(observed["release_clearance"])
            self.assertEqual("current_inputs", observed["verification"])
            self.assertFalse(verify_qa(self.repo, observed["qa"], expected=expected)["blocked"])
        self.write_json(".claude/runtime/meta/qa-input.json", {"controls": self.controls})
        qa = json.loads(self.p05(
            "qa", "--repo", self.repo, "--expected", self.repo / self.expected_path,
            "--input", self.repo / ".claude/runtime/meta/qa-input.json",
        ).stdout)
        self.assertEqual(observed["qa"], qa)
        self.assertFalse((self.home / "profile.yaml").exists())

    def test_five_domains_missing_result_cannot_hide_behind_scores(self) -> None:
        self.prepare_request(("ta", "da", "sc", "dh", "tq"))
        self.produce(score=100)
        expected = self.prepare_final()
        self.assertTrue(self.verify(command="summary")["ok"])
        path = self.result_path("sc")
        previous = safety.read_owned(self.repo, path)[0]
        safety.native_io_path(self.repo / path).unlink()
        result = self.verify(command="summary", expected=3)
        self.assertFalse(result["ok"])
        self.assertFalse(result["release_clearance"])
        self.write(path, previous)
        self.assertTrue(self.verify(command="summary")["ok"])
        self.assertEqual(expected, self.read_json(self.expected_path))

    def test_missing_started_checkpoint_with_fresh_context_is_incomplete(self) -> None:
        self.prepare_request()
        self.produce()
        safety.native_io_path(self.repo / self.result_path()).unlink()
        self.prepare_final()
        result = self.verify(command="summary", expected=3)
        self.assertTrue(result["blocked"])
        self.assertIn("checkpoint", " ".join(result["problems"]).lower())

    def test_failed_error_unknown_and_zero_tests_block_even_high_score(self) -> None:
        for change in ("fail", "error", "unverified", "zero", "skip", "unknown"):
            with self.subTest(change=change):
                if not self.results:
                    self.prepare_request()
                    self.produce()
                record = deepcopy(self.results["ta"])
                if change in ("fail", "error", "unverified"):
                    record["controls"][0]["status"] = change
                elif change == "zero":
                    record["controls"][0]["observation"]["executed"] = 0
                elif change == "skip":
                    record["controls"][0]["observation"]["skipped"] = 1
                else:
                    record["controls"][0]["applicability"] = "unknown"
                record["advisory_score"] = 100
                self.write_json(self.result_path(), record)
                self.prepare_final()
                self.assertTrue(self.verify(command="summary", expected=3)["blocked"])

    def test_immutable_qa_obligations_cannot_be_removed_or_downgraded(self) -> None:
        self.prepare_request()
        self.produce()
        for mutation in ("missing", "advisory", "check", "not_applicable", "policy"):
            with self.subTest(mutation=mutation):
                record = deepcopy(self.results["ta"])
                if mutation == "missing":
                    record["controls"] = []
                elif mutation == "advisory":
                    record["controls"][0]["requirement"] = "advisory"
                elif mutation == "check":
                    record["controls"][0]["kind"] = "check"
                elif mutation == "not_applicable":
                    record["controls"][0]["applicability"] = "not_applicable"
                else:
                    record["controls"][0]["policy"]["version"] = "rewritten"
                self.write_json(self.result_path(), record)
                self.prepare_final()
                self.assertFalse(self.verify(expected=3)["ok"])

    def test_raw_verified_or_actor_label_does_not_grant_authority(self) -> None:
        self.prepare_request(mode="authorized-execution")
        self.produce()
        record = deepcopy(self.results["ta"])
        record["verified"] = True
        record["producer"] = {"id": "claimed-reviewer", "context": "claimed-independent"}
        self.write_json(self.result_path(), record)
        self.prepare_final()
        self.assertFalse(self.verify(command="summary", expected=3)["ok"])

    def test_request_mode_and_start_producer_must_match_result(self) -> None:
        self.prepare_request(mode="artifact-only")
        self.produce()
        for key in ("mode", "actor", "start"):
            with self.subTest(key=key):
                record = deepcopy(self.results["ta"])
                if key == "mode":
                    record["receiver"]["mode"] = "authorized-execution"
                elif key == "actor":
                    record["producer"]["context"] = "different"
                else:
                    record["start"]["sha256"] = "0" * 64
                self.write_json(self.result_path(), record)
                self.prepare_final()
                self.assertFalse(self.verify(expected=3)["ok"])

    def test_stale_request_artifact_evidence_and_context_are_rejected(self) -> None:
        self.prepare_request()
        self.produce()
        self.prepare_final()
        for path in (self.request_path, "artifacts/ta.txt", "evidence/ta.txt", "source.txt", "preferences.json"):
            with self.subTest(path=path):
                before = safety.read_owned(self.repo, path)[0]
                self.write(path, before + b"\nchanged after prepare\n")
                self.assertFalse(self.verify(command="summary", expected=3)["ok"])
                self.write(path, before)
                self.assertTrue(self.verify()["ok"])

    def test_fresh_context_cannot_hide_changed_declared_artifact(self) -> None:
        self.prepare_request()
        self.produce()
        self.write("artifacts/ta.txt", b"replacement outside recorded artifact identity\n")
        self.prepare_final()
        self.assertFalse(self.verify(expected=3)["ok"])

    def test_final_context_must_select_request_results_and_evidence(self) -> None:
        self.prepare_request()
        self.produce()
        for missing in (self.request_path, self.record_root, "artifacts", "evidence", "preferences.json"):
            with self.subTest(missing=missing):
                self.prepare_final(omit=missing)
                self.assertFalse(self.verify(expected=3)["ok"])

    def test_context_work_profile_attempt_and_obligations_must_match(self) -> None:
        self.prepare_request()
        self.produce()
        original = self.prepare_final()
        for key in ("attempt_id", "profile", "required_policy", "qa_requirements", "work"):
            with self.subTest(key=key):
                changed = deepcopy(original)
                if key == "attempt_id":
                    changed[key] = "new-attempt"
                elif key == "profile":
                    changed[key]["generation"] += 1
                elif key == "required_policy":
                    changed[key]["required"] = False
                elif key == "work":
                    changed[key]["package_id"] = "another-package"
                else:
                    changed[key][0]["policy"]["version"] = "new-obligation"
                self.write_json(self.expected_path, changed)
                self.assertFalse(self.verify(expected=3)["ok"])

    def test_live_profile_drift_same_mtime_and_deleted_pin_refuse(self) -> None:
        self.prepare_request()
        self.produce()
        self.prepare_final()
        old = self.pack.read_bytes()
        stamp = self.pack.stat()
        self.pack.write_bytes(old.replace(b"mode: hard", b"mode: advisory"))
        os.utime(self.pack, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        refused = self.verify(command="summary", expected=3)
        self.assertIn("PROFILE", " ".join(refused["problems"]))
        self.pack.write_bytes(old)
        self.assertTrue(self.verify()["ok"])
        from profile_context import context_path
        pin = context_path(self.config)
        safety.native_io_path(pin).unlink()
        self.assertFalse(self.verify(expected=3)["ok"])
        self.assertFalse(safety.native_io_path(pin).exists(), "Verifier silently bootstrapped a lost pin")

    def test_syntax_recording_stays_nonclearing_even_when_profile_is_stale(self) -> None:
        self.prepare_request()
        self.pack.write_text("malformed: [\n", encoding="utf-8")
        self.produce()
        validation = json.loads(self.cli("validate", "--file", self.result_path(),
                                         "--request", self.request_path).stdout)
        self.assertEqual("not_performed", validation["verification"])
        self.prepare_final()
        self.assertFalse(self.verify(expected=3)["ok"])

    def test_record_requires_original_absence_and_preserves_late_edit(self) -> None:
        self.prepare_request()
        self.produce()
        path = self.result_path()
        original = safety.read_owned(self.repo, path)[0]
        self.write(path, b"later user edit\n")
        refused = self.publish(self.results["ta"], path, expected=2)
        self.assertIn("expected", refused.stderr.lower())
        self.assertEqual(b"later user edit\n", safety.read_owned(self.repo, path)[0])
        self.write_json(".claude/runtime/meta/absent.json", {"state": safety.file_state(self.repo, path)})
        self.publish(self.results["ta"], path, expected=2)
        self.assertEqual(b"later user edit\n", safety.read_owned(self.repo, path)[0])
        self.assertNotEqual(original, safety.read_owned(self.repo, path)[0])

    def test_record_refuses_outside_owned_slot_and_missing_expected_state(self) -> None:
        self.prepare_request()
        self.produce()
        before = safety.read_owned(self.repo, "source.txt")[0]
        self.publish(self.results["ta"], "source.txt", expected=2)
        self.assertEqual(before, safety.read_owned(self.repo, "source.txt")[0])
        run = self.cli("record", "--request", self.request_path,
                       "--file", ".claude/runtime/meta/payload.json",
                       "--output", self.result_path(), expected=2)
        self.assertIn("expected-state", run.stderr)

    def test_malformed_duplicates_nonfinite_and_versions_fail_without_writes(self) -> None:
        self.prepare_request()
        for payload in (
            b'{"kind":"domain-request","kind":"domain-request"}',
            b'{"value":NaN}', b'{"value":1e999}', b'{"unclosed":', b'[]',
            encoded({**self.request, "schema_version": 2}),
            encoded({**self.request, "release_clearance": True}),
            encoded({**self.request, "verified": True}),
        ):
            with self.subTest(payload=payload[:60]):
                self.write(".claude/runtime/meta/invalid.json", payload)
                result = self.cli("validate", "--file", ".claude/runtime/meta/invalid.json", expected=2)
                self.assertEqual("", result.stdout)
                self.assertFalse(safety.native_io_path(self.repo / self.record_root).exists())

    def test_duplicate_unknown_or_unmapped_checkpoint_controls_refuse(self) -> None:
        self.prepare_request()
        for change in ("duplicate-domain", "duplicate-checkpoint", "missing-control", "unknown-domain"):
            with self.subTest(change=change):
                request = deepcopy(self.request)
                if change == "duplicate-domain":
                    request["domains"] *= 2
                elif change == "duplicate-checkpoint":
                    request["domains"][0]["checkpoints"] *= 2
                elif change == "missing-control":
                    request["domains"][0]["checkpoints"][0]["control_ids"] = ["undeclared"]
                else:
                    request["domains"][0]["id"] = "invented"
                self.write_json(".claude/runtime/meta/invalid.json", request)
                self.cli("validate", "--file", ".claude/runtime/meta/invalid.json", expected=2)

    def test_portable_paths_reject_windows_aliases_and_traversal(self) -> None:
        self.prepare_request()
        for suffix in ("../escape.json", "C:/escape.json", "bad:time.json", "NUL.json",
                       "trailing. /file.json", "sub\\file.json", "bad\nname.json", ".git/config",
                       "wild*.json", "wild?.json", "pipe|.json", "angle<.json"):
            with self.subTest(suffix=suffix):
                request = deepcopy(self.request)
                request["domains"][0]["checkpoints"][0]["result"]["path"] = f"{self.record_root}/{suffix}"
                self.write_json(".claude/runtime/meta/invalid.json", request)
                self.cli("validate", "--file", ".claude/runtime/meta/invalid.json", expected=2)
        self.assertFalse((self.base / "escape.json").exists())

    def test_request_case_aliases_and_artifact_record_collisions_refuse(self) -> None:
        self.prepare_request()
        for alias in ("case", "artifact"):
            request = deepcopy(self.request)
            cp = request["domains"][0]["checkpoints"][0]
            if alias == "case":
                cp["result"]["path"] = cp["start"]["path"].upper()
            else:
                cp["artifacts"] = [cp["result"]["path"]]
            self.write_json(".claude/runtime/meta/invalid.json", request)
            self.cli("validate", "--file", ".claude/runtime/meta/invalid.json", expected=2)

    def test_record_before_start_or_with_wrong_request_digest_refuses(self) -> None:
        self.prepare_request()
        self.produce()
        cp = self.request["domains"][0]["checkpoints"][0]
        safety.native_io_path(self.repo / cp["result"]["path"]).unlink()
        for change in ("request", "start"):
            record = deepcopy(self.results["ta"])
            if change == "request":
                record["request"]["sha256"] = "0" * 64
            else:
                safety.native_io_path(self.repo / cp["start"]["path"]).unlink()
            self.publish(record, cp["result"]["path"], expected=2)
            self.assertFalse(safety.native_io_path(self.repo / cp["result"]["path"]).exists())

    def test_publication_failure_is_reported_without_overwriting(self) -> None:
        self.prepare_request()
        self.produce()
        import domain_result
        path = self.result_path()
        safety.native_io_path(self.repo / path).unlink()
        with patch.object(safety.os, "replace", side_effect=OSError("synthetic publication failure")):
            with self.assertRaises(OSError):
                domain_result.record_checkpoint(
                    self.repo, self.request_path, self.results["ta"],
                    output=path, expected_file_state=None,
                )
        self.assertFalse(safety.native_io_path(self.repo / path).exists())
        self.assertFalse(list(safety.native_io_path((self.repo / path).parent).glob(".lintel-write-*")))

    def test_original_owned_preimage_allows_only_its_planned_replacement(self) -> None:
        self.prepare_request()
        slot = self.request["domains"][0]["checkpoints"][0]["result"]
        self.write(slot["path"], b"original owned data awaiting replacement\n")
        original_state = safety.file_state(self.repo, slot["path"])
        slot["expected_state"] = original_state
        self.write_json(self.request_path, self.request)
        self.produce()
        self.assertNotEqual(original_state["sha256"], safety.file_state(self.repo, slot["path"])["sha256"])
        self.prepare_final()
        self.assertTrue(self.verify()["ok"])

    def test_advisory_failure_does_not_downgrade_mandatory_obligations(self) -> None:
        self.prepare_request(("ta", "sc"))
        self.request["input_context"]["qa_requirements"][1]["requirement"] = "advisory"
        self.request["input_context"]["required_controls"].remove("sc-check")
        self.prepare_input["qa_requirements"] = deepcopy(self.request["input_context"]["qa_requirements"])
        self.prepare_input["required_controls"] = deepcopy(self.request["input_context"]["required_controls"])
        self.write_json(self.request_path, self.request)
        self.produce()
        optional = self.results["sc"]
        optional["status"] = "fail"
        optional["controls"][0]["status"] = "fail"
        self.write_json(self.result_path("sc"), optional)
        self.prepare_final()
        observed = self.verify(command="summary")
        self.assertFalse(observed["blocked"])
        self.assertTrue(observed["advisories"])
        self.assertFalse(observed["release_clearance"])

    def test_grounded_not_applicable_and_unknown_policy_remain_distinct(self) -> None:
        self.prepare_request(("ta", "sc"))
        self.request["input_context"]["qa_requirements"][1]["applicability"] = "not_applicable"
        self.prepare_input["qa_requirements"] = deepcopy(self.request["input_context"]["qa_requirements"])
        self.write_json(self.request_path, self.request)
        self.produce()
        self.prepare_final()
        self.assertTrue(self.verify()["ok"])
        changed = deepcopy(self.read_json(self.expected_path))
        changed["required_policy"].update(status="unverified", applicability="unknown")
        self.write_json(self.expected_path, changed)
        self.assertFalse(self.verify(expected=3)["ok"])

    def test_missing_artifact_and_wrong_evidence_hash_block_with_fresh_context(self) -> None:
        self.prepare_request()
        self.produce()
        for change in ("missing", "artifact-hash", "evidence-hash"):
            with self.subTest(change=change):
                result = deepcopy(self.results["ta"])
                if change == "missing":
                    result["artifacts"] = []
                    result["decisions"] = []
                else:
                    result["artifacts" if change == "artifact-hash" else "evidence"][0]["sha256"] = "0" * 64
                self.write_json(self.result_path(), result)
                self.prepare_final()
                self.assertFalse(self.verify(expected=3)["ok"])

    def test_later_p05_rejection_still_blocks_outer_review_reader(self) -> None:
        self.prepare_request()
        self.produce()
        context = self.prepare_final()
        checks = []
        for name in ("spec", "quality"):
            checks.append({
                "id": name, "kind": "check", "requirement": "mandatory", "applicability": "applicable",
                "status": "pass", "reason": "Synthetic gate fixture, not real independent review.",
                "policy": deepcopy(self.controls[0]["policy"]), "evidence": ["evidence/ta.txt"], "observation": {},
            })
        record = {
            "schema_version": 2, "skill": "domain-review", "status": "pass",
            "timestamp": datetime.now(timezone.utc).isoformat(), "reason": "Synthetic reader integration.",
            "context": context, "reviewer": {"id": "synthetic-reviewer", "context": "review-1"},
            "provenance": "declared", "controls": checks + self.controls,
            "coverage": {"T014": context["required_controls"]},
            "evidence": evidence_manifest(self.repo, checks + self.controls),
        }
        review_path = context["snapshot"]["record_path"]
        self.write_json(review_path, record)
        proof = {
            "schema_version": 1, "kind": "human", "source": "synthetic-fixture-only",
            "reference": "not-a-real-independent-actor", "record_digest": content_digest(record),
            "attempt_id": context["attempt_id"], "builder": context["builder"], "reviewer": record["reviewer"],
        }
        proof_path = ".claude/runtime/meta/corroboration.json"
        self.write_json(proof_path, proof)
        self.run_process([options.bash, SOURCE / "bin/li-review-log", "--file", self.repo / review_path])
        read = [options.bash, SOURCE / "bin/li-review-read", "--skill", "domain-review",
                "--expected", self.repo / self.expected_path, "--corroboration",
                self.repo / proof_path, "--gate-json"]
        self.assertTrue(json.loads(self.run_process(read).stdout)["ok"])
        record["status"] = "fail"
        record["reason"] = "Synthetic later rejection."
        self.write_json(review_path, record)
        self.run_process([options.bash, SOURCE / "bin/li-review-log", "--file", self.repo / review_path])
        self.assertFalse(json.loads(self.run_process(read, expected=3).stdout)["ok"])
        observed = self.verify(command="summary")
        self.assertEqual("not_evaluated", observed["review"])
        self.assertFalse(observed["release_clearance"])

    def test_record_is_data_and_never_executes_next_action_or_preferences(self) -> None:
        self.prepare_request(mode="authorized-execution")
        self.request["advisory_preferences"] = {"command": "write should-never-exist", "policy": "advice only"}
        self.write_json(self.request_path, self.request)
        self.produce()
        result = self.results["ta"]
        result["next"]["action"] = "create should-never-exist"
        self.write_json(self.result_path(), result)
        self.prepare_final()
        observed = self.verify()
        self.assertTrue(observed["ok"])
        self.assertFalse(observed["release_clearance"])
        self.assertFalse((self.repo / "should-never-exist").exists())

    def test_copied_source_missing_resource_never_falls_back_to_target(self) -> None:
        self.prepare_request()
        source = self.base / "copied source"
        required = (
            "bin/li-domain-result.py", "lib/domain_result.py", "lib/domain-result-schema.json",
            "lib/context_safety.py", "lib/native_paths.py", "lib/review_contract.py",
            "lib/review-schema.json", "lib/markdown_source.py", "lib/profile_context.py",
            "lib/profile-context-schema.json",
        )
        for relative in required:
            path = source / relative
            safety.native_io_path(path.parent).mkdir(parents=True, exist_ok=True)
            safety.native_io_path(path).write_bytes((SOURCE / relative).read_bytes())
        self.write("domain_result.py", b"raise RuntimeError('hostile target module executed')\n")
        self.write("review_contract.py", b"raise RuntimeError('hostile target provider executed')\n")
        baseline = json.loads(self.cli("validate", "--file", self.request_path, source=source).stdout)
        self.assertEqual("not_performed", baseline["verification"])
        for relative in ("lib/domain_result.py", "lib/review_contract.py", "lib/domain-result-schema.json"):
            path = source / relative
            saved = safety.native_io_path(path).read_bytes()
            safety.native_io_path(path).unlink()
            failed = self.cli("validate", "--file", self.request_path, source=source, expected=2)
            self.assertNotIn("hostile target", failed.stderr)
            self.assertEqual("", failed.stdout)
            self.assertFalse(safety.native_io_path(self.repo / self.record_root).exists())
            safety.native_io_path(path).write_bytes(saved)
        self.assertFalse(list(safety.native_io_path(source).rglob("__pycache__")))

    def test_linked_publication_parent_is_refused_without_writing_outside(self) -> None:
        self.prepare_request()
        self.produce()
        cp = self.request["domains"][0]["checkpoints"][0]
        destination = self.repo / cp["result"]["path"]
        original = safety.read_owned(self.repo, cp["result"]["path"])[0]
        safety.native_io_path(destination).unlink()
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "sentinel").write_bytes(b"keep")
        try:
            os.symlink(outside / "result.json", destination)
        except OSError as error:
            self.skipTest(f"Native symlink creation unavailable: {error}")
        failed = self.publish(json.loads(original), cp["result"]["path"], expected=2)
        self.assertIn("refused", failed.stderr.lower())
        self.assertEqual(b"keep", (outside / "sentinel").read_bytes())
        self.assertFalse((outside / "result.json").exists())

    def test_late_edit_during_atomic_staging_preserves_new_bytes(self) -> None:
        self.prepare_request()
        self.produce()
        import domain_result
        path = self.result_path()
        safety.native_io_path(self.repo / path).unlink()
        original_mkstemp = safety.tempfile.mkstemp

        def concurrent_edit(*args, **kwargs):
            descriptor, name = original_mkstemp(*args, **kwargs)
            safety.native_io_path(self.repo / path).write_bytes(b"concurrent owned-file edit\n")
            return descriptor, name

        with patch.object(safety.tempfile, "mkstemp", side_effect=concurrent_edit):
            with self.assertRaisesRegex(ValueError, "changed"):
                domain_result.record_checkpoint(self.repo, self.request_path, self.results["ta"],
                                                output=path, expected_file_state=None)
        self.assertEqual(b"concurrent owned-file edit\n", safety.read_owned(self.repo, path)[0])

    def test_both_receiver_modes_are_data_not_automatic_actions(self) -> None:
        self.prepare_request()
        import domain_result
        for role, modes in (
            ("Migrator", ("artifact-only", "authorized-execution")),
            ("ReleaseEngineer", ("planning-only", "authorized-execution")),
        ):
            for mode in modes:
                with self.subTest(role=role, mode=mode):
                    request = deepcopy(self.request)
                    cp = request["domains"][0]["checkpoints"][0]
                    cp["receiver"] = {"role": role, "mode": mode}
                    self.assertEqual(cp["receiver"],
                                     domain_result.validate_request(request)["domains"][0]["checkpoints"][0]["receiver"])
        self.assertFalse((self.repo / self.record_root).exists())

    def test_additional_checkpoint_cannot_disappear_from_fresh_summary(self) -> None:
        self.prepare_request(("ta", "sc"))
        extra = deepcopy(self.request["domains"][1]["checkpoints"][0])
        extra["id"] = "policy_checked"
        extra["start"]["path"] = f"{self.record_root}/ta/02-start.json"
        extra["result"]["path"] = f"{self.record_root}/ta/02-result.json"
        self.request["domains"][0]["checkpoints"].append(extra)
        self.request["domains"].pop()
        self.write_json(self.request_path, self.request)
        self.produce()
        self.prepare_final()
        result = self.verify(command="summary", expected=3)
        self.assertIn("policy_checked", " ".join(result["problems"]))

    def test_windows_long_publication_uses_original_location(self) -> None:
        self.prepare_request()
        cp = self.request["domains"][0]["checkpoints"][0]
        prefix = f"{self.record_root}/ta/"
        leaf = "/01-result.json"
        padding = 290 - len(str(self.repo)) - 1 - len(prefix) - len(leaf)
        self.assertGreater(padding, 0, "Do not shorten the selected root to satisfy this fixture")
        self.assertLessEqual(padding, 255)
        cp["result"]["path"] = prefix + "x" * padding + leaf
        self.assertEqual(290, len(str(self.repo / cp["result"]["path"])))
        self.write_json(self.request_path, self.request)
        self.produce()
        self.assertEqual("domain-result", self.read_json(cp["result"]["path"])["kind"])
        result = self.cli("validate", "--request", self.request_path, "--file", cp["result"]["path"])
        self.assertEqual("not_performed", json.loads(result.stdout)["verification"])
        self.assertFalse(cp["result"]["path"].startswith("\\\\?\\"))

    def test_mandatory_negative_header_is_not_hidden_by_na_controls(self) -> None:
        self.prepare_request(("ta", "sc"))
        self.request["input_context"]["qa_requirements"][1]["applicability"] = "not_applicable"
        self.prepare_input["qa_requirements"] = deepcopy(self.request["input_context"]["qa_requirements"])
        self.write_json(self.request_path, self.request)
        self.produce()
        record = self.results["sc"]
        record["status"] = "error"
        self.write_json(self.result_path("sc"), record)
        self.prepare_final()
        self.assertTrue(self.verify(command="summary", expected=3)["blocked"])

    def test_direct_api_invalid_objects_are_explicit_errors(self) -> None:
        self.prepare_request()
        import domain_result
        for value in (None, [], "not JSON object"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    domain_result.validate_request(value)
                with self.assertRaises(ValueError):
                    domain_result.validate_checkpoint(value, self.request)
        for value in ({"kind": []}, {"kind": {}}, {"kind": None}):
            with self.assertRaises(ValueError):
                domain_result.validate_checkpoint(value, self.request)

    def test_wrong_profile_target_and_generation_refuse_fresh_verification(self) -> None:
        self.prepare_request()
        self.produce()
        expected = self.prepare_final()
        import domain_result
        from dataclasses import replace
        wrong = replace(self.config, repo=self.base)
        self.assertFalse(domain_result.verify_result(
            self.repo, self.request_path, expected=expected, profile_config=wrong,
        )["ok"])
        wrong = replace(self.config, context_id="different-context")
        self.assertFalse(domain_result.verify_result(
            self.repo, self.request_path, expected=expected, profile_config=wrong,
        )["ok"])

    def test_new_selected_file_cannot_reuse_prior_context(self) -> None:
        self.prepare_request()
        self.produce()
        self.prepare_final()
        self.write("artifacts/new-unreviewed.txt", b"new selected output\n")
        observed = self.verify(command="summary", expected=3)
        self.assertFalse(observed["ok"])
        self.assertIn("changed", " ".join(observed["problems"]).lower())

    def test_byte_bound_and_empty_receiver_are_explicit_refusals(self) -> None:
        self.prepare_request()
        import domain_result
        oversized = deepcopy(self.request)
        oversized["advisory_preferences"]["oversized"] = "x" * domain_result.MAX_DOCUMENT_BYTES
        self.write_json(".claude/runtime/meta/oversized.json", oversized)
        failed = self.cli("validate", "--file", ".claude/runtime/meta/oversized.json", expected=2)
        self.assertEqual("", failed.stdout)
        self.assertFalse(safety.native_io_path(self.repo / self.record_root).exists())
        for field in ("role", "mode"):
            request = deepcopy(self.request)
            request["domains"][0]["checkpoints"][0]["receiver"][field] = ""
            with self.assertRaises(ValueError):
                domain_result.validate_request(request)

    def test_real_neutral_pin_does_not_claim_required_enterprise_policy(self) -> None:
        from dataclasses import replace
        (self.repo / ".claude/profile-requirements.json").unlink()
        self.config = replace(self.config, context_id="synthetic-neutral-context")
        neutral = load_profile_context(self.config, create=True)
        self.reference = profile_reference(neutral)
        self.policy = required_policy(neutral)
        self.assertEqual("_default", self.reference["name"])
        self.assertFalse(self.policy["required"])
        self.prepare_request()
        self.produce()
        self.prepare_final()
        result = self.verify(command="summary")
        self.assertTrue(result["ok"])
        self.assertFalse(result["controls"]["required_policy"]["required"])
        self.assertEqual("not_required", result["controls"]["required_policy"]["status"])
        self.assertFalse(result["release_clearance"])


if __name__ == "__main__":
    print(f"Evidence logs: {ARTIFACTS}", flush=True)
    print("Accepted P03/P05/P07 data links only; P08, installation and native role execution NOT RUN.",
          flush=True)
    unittest.main(argv=[__file__, *test_args], verbosity=2)
