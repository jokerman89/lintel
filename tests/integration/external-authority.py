# component: selected-external-authority-regressions
# implements: ADR-0024, ADR-0028, ADR-0029
# intent: docs/spec-kit.md, docs/enterprise-profile-value.md
# constraints: synthetic repositories/profiles only; no Spec Kit, hooks, network or model execution
# last_intent_review: 2026-10-03
"""Exercise the existing P03/work-map/P05/P07 APIs, not a second authority parser."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
from native_paths import native_io_path
from profile_context import (
    ProfileConfig, ProfileError, field_value, load_profile_context,
    profile_reference, required_policy, verify_profile_reference,
)
from review_contract import (
    CONTRACT_VERSION, ContractError, bind_work, content_digest, evidence_manifest,
    verify_context, verify_qa, verify_review,
)

WORK = runpy.run_path(str(ROOT / "bin/li-work-artifacts.py"))
PREPARE = runpy.run_path(str(ROOT / "bin/li-review-evidence.py"))["prepare"]
OBSERVATIONS = []


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lintel-ext-")
        self.root = Path(self.temporary.name)
        self.addCleanup(self.cleanup)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.env = dict(os.environ)
        for key in list(self.env):
            if key.startswith(("LINTEL_", "CLAUDE_")):
                self.env.pop(key)
        for key, name in {
            "HOME": "home", "USERPROFILE": "home", "APPDATA": "appdata",
            "LOCALAPPDATA": "localappdata", "TMP": "temp", "TEMP": "temp", "TMPDIR": "temp",
            "XDG_CONFIG_HOME": "xdg-config", "XDG_CACHE_HOME": "xdg-cache",
            "XDG_DATA_HOME": "xdg-data", "XDG_STATE_HOME": "xdg-state",
            "XDG_RUNTIME_DIR": "xdg-runtime",
        }.items():
            path = self.root / name
            native_io_path(path).mkdir(parents=True, exist_ok=True)
            self.env[key] = path.as_posix()
        self.env.update(PYTHONDONTWRITEBYTECODE="1", GIT_TERMINAL_PROMPT="0")
        self.map_path = "work.json"
        self.mapping = {
            "schema_version": 1, "workflow": "spec-kit", "status": "APPROVED",
            "spec": "specs/chosen/spec.md", "plan": "specs/chosen/plan.md",
            "tasks": "specs/chosen/tasks.md", "prompt": "handoff.md",
            "constitution": ".specify/memory/constitution.md",
        }
        self.write("work.json", json.dumps(self.mapping) + "\n")
        self.write(self.mapping["spec"], "# Acceptance\nT008 preserves original behavior.\n"
                   "T103 closes the selected convergence finding.\n"
                   "The independently required synthetic-required check must observe source.txt == after.\n")
        self.write(self.mapping["plan"], "# Design\nRetain the selected API.\n")
        self.tasks = ("# Original tasks\n\n- [x] T001 Establish baseline\n"
                      "- [ ] T008 Preserve behavior (depends T001)\n"
                      "\n## Convergence follow-up\n\n"
                      "- [ ] T103 Close original gap (depends T008)\n")
        self.write(self.mapping["tasks"], self.tasks)
        self.write("handoff.md", "Continue original T008 then convergence-appended T103.\n")
        self.write(self.mapping["constitution"], "# Principles\nPreserve original task authority.\n")
        # These are explicitly selected fixture paths, NOT a guessed extension layout.
        self.reports = [
            "inputs/analysis.md", "inputs/converge.md",
            "inputs/bug-assessment.md", "inputs/assessment.md",
        ]
        for path, text in zip(self.reports, (
            "# Original analysis\nT008 coverage is incomplete.\n",
            "# Original convergence\nT103: missing behavior. Source: original T008.\n",
            "# Original bug assessment\npartial: reproduction retained for T103.\n",
            "# Original assessment\nneeds-clarification: no implementation approval supplied.\n",
        )):
            self.write(path, text)
        self.registration = "inputs/supplied-host-observation.txt"
        self.write(self.registration, "Synthetic supplied registration observation; version unknown.\n"
                   "consistency command registered; workflow gate enabled; after hook disabled.\n")
        self.write("inputs/unselected-newer.md", "- [ ] T999 Not the selected task source\n")
        self.write(".gitignore", ".claude/runtime/\n")
        self.write("source.txt", "before\n")
        self.selected_ids = ["T008", "T103"]

    def cleanup(self):
        path = Path(self.temporary.name)
        self.assertEqual(path, self.root)
        self.assertTrue(path.name.startswith("lintel-ext-"))
        self.temporary.name = str(native_io_path(path))
        self.temporary.cleanup()

    def write(self, name, text):
        path = native_io_path(self.repo / name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        return path

    def bytes(self, name):
        return native_io_path(self.repo / name).read_bytes()

    def context(self, **kwargs):
        return WORK["work_context"](
            self.repo, Path(self.map_path), package_id="selected",
            leaf_ids=self.selected_ids, acceptance_paths=self.reports, **kwargs,
        )

    def observe(self, **data):
        OBSERVATIONS.append({"test": self.id(), **data})

    def git(self, *args):
        result = subprocess.run(["git", "--no-pager", *args], cwd=self.repo, env=self.env,
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def baseline(self):
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/synthetic")
        self.git("config", "user.name", "Synthetic fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        # Ordinary fixture-only commit, with no hook override or --no-verify.
        self.git("add", "--", ".gitignore", "work.json", "handoff.md", "specs", ".specify", "inputs", "source.txt")
        self.git("commit", "-qm", "synthetic acceptance baseline")
        base = self.git("rev-parse", "HEAD")
        self.write("source.txt", "after\n")
        return base

    def control(self, name="spec"):
        return {
            "id": name, "kind": "check", "requirement": "mandatory",
            "applicability": "applicable", "status": "pass",
            "reason": "Observed only the synthetic fixture's source.txt.",
            "policy": {"source": self.mapping["spec"], "version": "fixture-1",
                       "applicability": "Selected synthetic acceptance only",
                       "jurisdiction": None, "actor": None, "effective_date": None},
            "evidence": ["observation.txt"], "observation": {},
        }

    def prepare(self, *, profile=None, policy=None, requirements=None):
        if requirements is None:
            check = self.control("source-check")
            requirements = [{key: deepcopy(check[key]) for key in (
                "id", "kind", "requirement", "applicability", "policy")}]
        base = self.baseline()
        self.assertEqual(self.bytes("source.txt"), b"after\n")
        self.write("observation.txt", "Observed synthetic source.txt: after\n")
        request = {
            "work_map": self.map_path, "package_id": "selected",
            "leaf_ids": self.selected_ids, "acceptance_paths": self.reports,
            "base": base, "selection": ["source.txt"],
            "record_path": ".claude/runtime/reviews/decision.json",
            "attempt_id": "synthetic-1", "builder": {"id": "fixture", "context": "same-actor"},
            # This is explicitly a mechanical synthetic test, never independent review of Lintel.
            "independence_required": False, "purpose": "implementation", "profile": profile,
            "required_policy": policy or {
                "required": False, "status": "not_required", "source": None,
                "version": None, "applicability": "not_applicable",
            },
            "required_controls": ["spec", *[item["id"] for item in requirements]],
            "qa_requirements": list(requirements),
        }
        return PREPARE(self.repo, request)

    def decision(self, context, controls):
        return {
            "schema_version": CONTRACT_VERSION, "skill": "review", "status": "pass",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "Synthetic contract fixture, not a review of the product change.",
            "context": deepcopy(context), "reviewer": deepcopy(context["builder"]),
            "provenance": "declared", "controls": controls,
            "coverage": {leaf: [c["id"] for c in controls] for leaf in self.selected_ids},
            "evidence": evidence_manifest(self.repo, controls),
        }


class SelectedReports(Fixture):
    def test_original_ids_and_converge_append_are_the_only_tasks(self):
        before = self.bytes(self.mapping["tasks"])
        result = self.context()
        self.assertEqual(list(result["tasks"]), ["T001", "T008", "T103"])
        self.assertEqual(result["tasks"]["T103"]["dependencies"], ["T008"])
        self.assertEqual(result["incomplete_ids"], ["T008", "T103"])
        self.assertNotIn("T999", result["tasks"])
        self.assertEqual(before, self.bytes(self.mapping["tasks"]))
        self.assertEqual(WORK["load_work_map"](self.repo, Path(self.map_path)), self.mapping)
        self.assertFalse(result["release_clearance"])
        self.observe(ids=list(result["tasks"]), task_sha256=hashlib.sha256(before).hexdigest(),
                     map_schema=result["manifest"]["schema_version"], clearance=result["release_clearance"])

    def test_selected_reports_are_counted_once_in_p03_and_bound_by_p05(self):
        result = self.context(warm_paths=[self.registration, self.reports[0]])
        expected = {self.map_path, *[v for k, v in self.mapping.items()
                                    if k in WORK["REQUIRED_ARTIFACTS"] or k == "constitution"],
                    *self.reports, self.registration}
        self.assertEqual({item["path"] for item in result["manifest"]["files"]}, expected)
        self.assertEqual(result["manifest"]["bytes"], sum(len(self.bytes(p)) for p in expected))
        self.assertEqual(result["binding"], bind_work(
            self.repo, work_map=self.map_path, package_id="selected",
            leaf_ids=self.selected_ids, acceptance_paths=self.reports))
        self.assertEqual(WORK["work_budget"](result)["estimated_input_tokens"],
                         (result["manifest"]["bytes"] + 3) // 4)
        self.observe(manifest=result["manifest"], binding=result["binding"])

    def test_selected_reports_cannot_evade_file_or_byte_limits(self):
        plain = WORK["work_context"](self.repo, Path(self.map_path))
        for limits in ({"max_files": len(plain["manifest"]["files"])},
                       {"max_bytes": plain["manifest"]["bytes"]}):
            with self.subTest(limits=limits), self.assertRaises(ValueError):
                self.context(**limits)

    def test_acceptance_excerpt_still_counts_its_original_full_source(self):
        path = self.reports[0]
        self.write(path, "# Original analysis\n## Selected\nT103: missing behavior.\n## End\nOther context.\n")
        ref = {"path": path, "start": "## Selected", "end": "## End"}
        result = WORK["work_context"](self.repo, Path(self.map_path), package_id="selected",
                                      leaf_ids=self.selected_ids, acceptance_paths=[ref])
        entry = next(item for item in result["manifest"]["files"] if item["path"] == path)
        self.assertEqual(entry["size"], len(self.bytes(path)))
        self.assertEqual(result["binding"]["acceptance_paths"].count(ref), 1)

    def test_missing_escaping_or_malformed_selected_report_fails_without_task_edits(self):
        before = self.bytes(self.mapping["tasks"])
        for selection in (["inputs/missing.md"], ["../outside.md"], [{"path": self.reports[0]}]):
            with self.subTest(selection=selection), self.assertRaises((ValueError, OSError)):
                WORK["work_context"](self.repo, Path(self.map_path), package_id="selected",
                                      leaf_ids=self.selected_ids, acceptance_paths=selection)
        self.assertEqual(before, self.bytes(self.mapping["tasks"]))

    def test_reports_and_registration_do_not_grant_draft_approval(self):
        self.mapping["status"] = "DRAFT"
        self.write(self.map_path, json.dumps(self.mapping))
        view = WORK["work_context"](self.repo, Path(self.map_path), warm_paths=self.reports)
        self.assertEqual(view["status"], "DRAFT")
        self.assertIsNone(view["binding"])
        self.assertFalse(view["release_clearance"])
        with self.assertRaisesRegex(ContractError, "not approved"):
            self.context()

    def test_report_task_id_and_append_drift_invalidate_real_p05_context(self):
        context = self.prepare()
        verify_context(self.repo, context)
        changes = {
            self.reports[1]: self.bytes(self.reports[1]) + b"New convergence observation.\n",
            self.mapping["tasks"]: self.tasks.replace("T103", "T104").encode(),
        }
        for path, changed in changes.items():
            before = self.bytes(path)
            native_io_path(self.repo / path).write_bytes(changed)
            with self.assertRaisesRegex(ContractError, "acceptance sources changed") as failure:
                verify_context(self.repo, context)
            self.observe(path=path, negative=str(failure.exception))
            native_io_path(self.repo / path).write_bytes(before)
        self.write(self.mapping["tasks"], self.tasks + "- [ ] T104 Another converge gap (depends T103)\n")
        self.assertIn("T104", self.context()["tasks"])
        with self.assertRaisesRegex(ContractError, "acceptance sources changed"):
            verify_context(self.repo, context)

    def test_original_progress_normalization_does_not_approve_or_rewrite_tasks(self):
        context = self.prepare()
        original = self.bytes(self.mapping["tasks"])
        updated = original.replace(b"[ ] T103", b"[x] T103")
        native_io_path(self.repo / self.mapping["tasks"]).write_bytes(updated)
        verify_context(self.repo, context)
        self.assertEqual(context["work"], self.context()["binding"])
        self.assertEqual(self.bytes(self.mapping["tasks"]), updated)
        self.assertFalse(self.context()["release_clearance"])

    def test_selected_registration_changes_remain_input_drift_not_guessed_capabilities(self):
        self.reports.append(self.registration)
        context = self.prepare()
        self.write(self.registration, "Synthetic supplied observation: after hook now enabled.\n")
        with self.assertRaisesRegex(ContractError, "acceptance sources changed"):
            verify_context(self.repo, context)


class WholeBlockRequirements(Fixture):
    def setUp(self):
        super().setUp()
        # Declared by accepted work BEFORE resolving any pack or gathering observations.
        required = self.control("synthetic-required")
        self.requirement = {key: deepcopy(required[key]) for key in (
            "id", "kind", "requirement", "applicability", "policy")}

    def profile(self, replacement):
        store = self.root / "packs"
        for name, text in {
            "organization-base": (
                "voice:\n  default_tier: internal\nnavigation:\n  default_workflow: cycle\n"
                "compliance:\n  mode: hard\n  hooks: [synthetic-required]\n"),
            "team": "extends: organization-base\n" + (
                "compliance:\n  mode: off\n  hooks: []\n" if replacement else ""),
        }.items():
            path = native_io_path(store / name / "pack.yaml")
            path.parent.mkdir(parents=True)
            path.write_text(f'schema_version: "1"\nname: {name}\nversion: 1.0.0\n' + text,
                            encoding="utf-8")
        self.write(".claude/profile-requirements.json",
                   '{"schema_version":1,"required_pack":"team"}\n')
        self.cfg = ProfileConfig(
            source=ROOT, repo=self.repo, home=self.root / "home",
            packs=store, pointer=self.root / "home/active-pack", context_id="synthetic-team",
        )
        loaded = load_profile_context(self.cfg, create=True)
        reference = profile_reference(loaded)
        verified = verify_profile_reference(reference, self.cfg)
        return verified, reference, required_policy(verified)

    def test_omitted_block_really_inherits_the_parent_control(self):
        record, reference, policy = self.profile(replacement=False)
        self.assertEqual(field_value(record["profile"]["values"], "compliance.hooks"),
                         ["synthetic-required"])
        self.assertEqual(field_value(record["profile"]["values"], "compliance.mode"), "hard")
        self.assertEqual(policy["status"], "loaded")
        self.assertTrue(policy["required"])
        self.observe(profile=reference, policy=policy, provenance=record["profile"]["provenance"]["compliance"])

    def test_replaced_block_cannot_clear_independently_required_p05_control(self):
        record, reference, policy = self.profile(replacement=True)
        hooks = field_value(record["profile"]["values"], "compliance.hooks")
        self.assertEqual(hooks, [])
        self.assertEqual(field_value(record["profile"]["values"], "compliance.mode"), "off")
        self.assertEqual(policy["status"], "loaded")
        self.assertTrue(policy["required"])
        context = self.prepare(profile=reference, policy=policy, requirements=[self.requirement])
        frozen = content_digest(context)
        # Reproduce the mistake: collecting only the resolved child hook list loses a requirement.
        controls = [self.control(), *[self.control(name) for name in hooks]]
        review = self.decision(context, controls)
        result = verify_review(self.repo, review, expected=context)
        self.assertFalse(result["ok"], result)
        self.assertEqual(result["status"], "error")
        self.assertTrue(any("control" in problem for problem in result["problems"]), result)
        qa = {"schema_version": CONTRACT_VERSION, "context_digest": frozen,
              "controls": [], "evidence": []}
        with self.assertRaisesRegex(ContractError, "QA control IDs") as failure:
            verify_qa(self.repo, qa, expected=context)
        self.assertEqual(content_digest(context), frozen)
        self.assertEqual(profile_reference(verify_profile_reference(reference, self.cfg)), reference)
        self.observe(profile=reference, policy=policy, resolved_hooks=hooks,
                     immutable_requirements=context["qa_requirements"],
                     review_gate=result, qa_negative=str(failure.exception))

    def test_policy_load_does_not_waive_or_downgrade_immutable_requirement(self):
        _, reference, policy = self.profile(replacement=True)
        context = self.prepare(profile=reference, policy=policy, requirements=[self.requirement])
        valid = self.control("synthetic-required")
        qa = {"schema_version": CONTRACT_VERSION, "context_digest": content_digest(context),
              "controls": [valid], "evidence": evidence_manifest(self.repo, [valid])}
        self.assertFalse(verify_qa(self.repo, qa, expected=context)["blocked"])
        for field, value in (("requirement", "advisory"), ("applicability", "not_applicable")):
            changed = deepcopy(qa)
            changed["controls"][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ContractError, "immutable fields"):
                verify_qa(self.repo, changed, expected=context)
        missing = deepcopy(qa)
        missing["controls"][0].update(status="unverified", reason="No control invocation observed.")
        result = verify_qa(self.repo, missing, expected=context)
        self.assertTrue(result["blocked"])
        self.observe(unverified_gate=result, immutable_requirements=context["qa_requirements"])

    def test_same_mtime_parent_change_invalidates_child_pin_without_rebind(self):
        _, reference, _ = self.profile(replacement=True)
        parent = native_io_path(self.cfg.packs / "organization-base/pack.yaml")
        before = parent.stat()
        parent.write_bytes(parent.read_bytes() + b"# changed parent content\n")
        os.utime(parent, ns=(before.st_atime_ns, before.st_mtime_ns))
        with self.assertRaises(ProfileError) as failure:
            verify_profile_reference(reference, self.cfg)
        self.assertEqual(failure.exception.code, "PROFILE_DRIFT")
        self.observe(negative=failure.exception.code, profile=reference)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path)
    args, remaining = parser.parse_known_args()
    run = unittest.main(argv=[sys.argv[0], *remaining], verbosity=2, exit=False)
    if args.evidence:
        with native_io_path(args.evidence).open("x", encoding="utf-8") as stream:
            json.dump({"tests_run": run.result.testsRun, "failures": len(run.result.failures),
                       "errors": len(run.result.errors), "skipped": len(run.result.skipped),
                       "observations": OBSERVATIONS}, stream, indent=2)
            stream.write("\n")
    sys.exit(not run.result.wasSuccessful())
