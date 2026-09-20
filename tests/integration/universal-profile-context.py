# component: universal-profile-context-scenarios
# implements: ADR-0029
# intent: docs/concepts/pack-resolver.md
# constraints: synthetic fixture packs, temporary homes, subprocess consumers without model calls
# last_intent_review: 2026-09-20
"""Exercise the shell producer and new-process consumers, not a parallel test parser."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


ARGS = argparse.ArgumentParser()
ARGS.add_argument("--root", type=Path, required=True)
ARGS.add_argument("--bash", required=True)
OPTIONS, TEST_ARGS = ARGS.parse_known_args()
ROOT = OPTIONS.root.resolve()
BOOTSTRAP = (
    'source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"\n'
    'lintel_copilot_env "$LINTEL_REPO_ROOT" || exit $?\n'
    'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
    'profile_context_reference'
)


class ProfileLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lintel-profile-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source = self.base / "installed source"
        self.target = self.base / "target"
        self.home = self.base / "home"
        self.store = self.home / "packs"
        self.target.mkdir()
        (self.target / "AGENTS.md").write_text("Synthetic consumer.\n", encoding="utf-8")
        (self.target / ".claude").mkdir()
        self.store.mkdir(parents=True)
        for relative in (
            "lib/pack-resolver.sh", "lib/profile_context.py",
            "lib/profile-context-schema.json", "lib/pack-schema.yaml",
            "lib/copilot-env.sh", "lib/paths.sh", "lib/orientator-routing.sh", "bin/_audit.sh",
            "packs/_default/pack.yaml", ".claude-plugin/plugin.json",
        ):
            destination = self.source / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        self.env = {
            key: value for key, value in os.environ.items()
            if not key.startswith(("LINTEL_", "CLAUDE_")) and key != "PACK_CACHE_FILE"
        }
        self.env.update({
            "LINTEL_SOURCE_ROOT": self.source.as_posix(),
            "LINTEL_REPO_ROOT": self.target.as_posix(),
            "LINTEL_HOME": self.home.as_posix(),
            "LINTEL_PACKS_DIR": self.store.as_posix(),
            "LINTEL_ACTIVE_PACK_FILE": (self.store / "active-pack").as_posix(),
            "LINTEL_AUDIT_DIR": (self.home / "audit").as_posix(),
            "LINTEL_PROFILE_CONTEXT": "synthetic-work",
            "PYTHONDONTWRITEBYTECODE": "1",
        })

    def shell(self, code, *, env=None, success=True, error_data=False, source_resolver=True):
        preamble = 'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n' if source_resolver else ""
        result = subprocess.run(
            [OPTIONS.bash, "-c", preamble + code],
            env=self.env if env is None else env, cwd=self.target,
            text=True, encoding="utf-8", capture_output=True, timeout=45,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
            if not error_data:
                self.assertEqual(result.stdout.strip(), "", "failure emitted success-shaped data")
        return result

    def pack(self, name, extra="", *, root=None, parent=None):
        path = (root or self.store) / name / "pack.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        text = f"name: {name}\nversion: 1.2.3\n"
        if parent:
            text += f"extends: {parent}\n"
        else:
            text += (
                "voice: {default_tier: internal}\n"
                "compliance: {mode: hard, hooks: [synthetic-evidence]}\n"
                "navigation: {default_workflow: controlled}\n"
            )
        path.write_text(text + extra, encoding="utf-8")
        return path

    def select(self, name):
        (self.store / "active-pack").write_text(name + "\n", encoding="utf-8")

    def require(self, name):
        (self.target / ".claude/profile-requirements.json").write_text(
            json.dumps({"schema_version": 1, "required_pack": name}), encoding="utf-8",
        )

    def reference(self):
        return json.loads(self.shell("profile_context_reference").stdout)

    def test_neutral_first_use_and_unbound_boundary(self):
        env = dict(self.env)
        env.pop("LINTEL_PROFILE_CONTEXT")
        self.assertEqual(self.shell("resolve_pack_field compliance.mode", env=env).stdout, "advisory")
        self.assertIn("PROFILE_CONTEXT_REQUIRED", self.shell(
            "profile_context_reference", env=env, success=False,
        ).stderr)
        self.assertEqual(self.reference()["name"], "_default")
        self.assertFalse((self.home / "profile.yaml").exists())

    def test_repository_requirement_cannot_be_replaced_by_global_or_explicit_selection(self):
        self.pack("strict")
        self.pack("preference")
        self.select("preference")
        self.require("strict")
        self.assertEqual(self.reference()["name"], "strict")
        env = dict(self.env, LINTEL_PROFILE_PACK="preference", LINTEL_PROFILE_CONTEXT="conflict")
        self.assertIn("PROFILE_REQUIRED", self.shell("get_loaded_pack", env=env, success=False).stderr)

    def test_missing_invalid_and_incompatible_required_pack_never_become_neutral(self):
        self.require("required")
        self.assertIn("PROFILE_REQUIRED", self.shell("get_loaded_pack", success=False).stderr)
        path = self.pack("required", "compliance: {mode: advisory}\n")
        self.assertIn("PROFILE_REQUIRED", self.shell(
            "resolve_pack_field compliance.mode", success=False,
        ).stderr)
        path.write_text("name: required\nversion: 1.0.0\nextends: missing\n", encoding="utf-8")
        self.assertIn("PROFILE_REQUIRED", self.shell("get_loaded_pack", success=False).stderr)
        self.pack("required", 'schema_version: "99"\n')
        self.assertIn("PROFILE_REQUIRED", self.shell("get_loaded_pack", success=False).stderr)
        self.assertFalse(list((self.home / "sessions").glob("**/*-profile.json")))

    def test_invalid_optional_preference_is_explicit_fallback_not_required_activation(self):
        self.select("missing-preference")
        result = self.shell("profile_context_json")
        record = json.loads(result.stdout)
        self.assertEqual(record["profile"]["selection"]["status"], "fallback")
        self.assertEqual(record["profile"]["selection"]["mode"], "optional")
        self.assertEqual(record["profile"]["values"]["name"], "_default")
        self.assertIn("OPTIONAL_PROFILE_FALLBACK", result.stderr)
        self.require("missing-preference")
        self.assertIn("PROFILE_DRIFT", self.shell("get_loaded_pack", success=False).stderr)

    def test_invalid_neutral_baseline_is_an_error(self):
        (self.source / "packs/_default/pack.yaml").write_text(
            "name: _default\nversion: 1.0.0\nbroken: [\n", encoding="utf-8",
        )
        self.assertIn("PROFILE_BASELINE", self.shell(
            "resolve_pack_field compliance.mode", success=False,
        ).stderr)

    def test_structured_values_whole_block_inheritance_and_provenance(self):
        self.pack("base", "brand: {name: Parent, copy_tone: formal}\n")
        self.pack("child", (
            "voice: {default_tier: external, corpus: null}\n"
            "brand: {name: Child}\n"
            "flags: {disabled: false, quoted_false: 'false', quoted_null: 'null', empty: ''}\n"
            'items: ["a, b", "literal # text", null, false, "null", "false"]\n'
        ), parent="base")
        self.require("child")
        record = json.loads(self.shell("profile_context_json").stdout)
        values = record["profile"]["values"]
        self.assertEqual(values["compliance"]["mode"], "hard")
        self.assertIsNone(values["voice"]["corpus"])
        self.assertIs(values["flags"]["disabled"], False)
        self.assertEqual(values["flags"]["quoted_false"], "false")
        self.assertEqual(values["flags"]["quoted_null"], "null")
        self.assertEqual(values["flags"]["empty"], "")
        self.assertEqual(values["items"], ["a, b", "literal # text", None, False, "null", "false"])
        self.assertNotIn("copy_tone", values["brand"])
        self.assertEqual(json.loads(self.shell("resolve_pack_field_json items").stdout), values["items"])
        origin = json.loads(self.shell("profile_field_provenance compliance.mode").stdout)
        self.assertEqual(origin["name"], "base")
        self.assertEqual(origin["version"], "1.2.3")
        parent = self.store / "base/pack.yaml"
        self.assertEqual(Path(origin["path"]), parent)
        self.assertEqual(origin["digest"], "sha256:" + hashlib.sha256(parent.read_bytes()).hexdigest())
        self.assertFalse(origin["fallback"])
        self.assertEqual([entry["name"] for entry in record["profile"]["ancestry"]], ["base", "child"])
        origin = json.loads(self.shell("profile_field_provenance navigation.orientator_budget_tokens").stdout)
        self.assertEqual(origin["name"], "_default")
        self.assertTrue(origin["fallback"])

    def test_producer_fresh_process_delegated_handoff_and_cold_resume(self):
        self.pack("strict")
        self.require("strict")
        producer = self.shell("bind_profile_context work-42")
        reference = json.loads(producer.stdout)
        self.assertEqual(reference["context_id"], "work-42")
        handoff = self.target / "handoff.json"
        handoff.write_text(json.dumps(reference), encoding="utf-8")
        env = dict(self.env, LINTEL_PROFILE_CONTEXT="work-42")
        self.assertEqual(json.loads(self.shell("profile_context_reference", env=env).stdout), reference)
        env.pop("LINTEL_PROFILE_CONTEXT")
        env["HANDOFF"] = handoff.as_posix()
        env["CLAUDE_SESSION_ID"] = "different-real-host-session-on-resume"
        self.assertEqual(json.loads(self.shell(
            'verify_profile_context "$HANDOFF"', env=env,
        ).stdout), reference)
        self.assertEqual(json.loads(self.shell(
            'verify_profile_context "$HANDOFF"', env=env,
        ).stdout), reference)
        tampered = dict(reference, digest="sha256:" + "0" * 64)
        handoff.write_text(json.dumps(tampered), encoding="utf-8")
        self.assertIn("PROFILE_REFERENCE_MISMATCH", self.shell(
            'verify_profile_context "$HANDOFF"', env=env, success=False,
        ).stderr)

    def test_documented_bootstrap_without_injected_host_id_pins_two_fresh_shells(self):
        self.pack("strict")
        self.require("strict")
        env = dict(self.env)
        env.pop("LINTEL_PROFILE_CONTEXT")
        first = json.loads(self.shell(BOOTSTRAP, env=env, source_resolver=False).stdout)
        second = json.loads(self.shell(BOOTSTRAP, env=env, source_resolver=False).stdout)
        self.assertEqual(first, second)
        self.assertTrue(first["context_id"].startswith("repo-work:"))
        selected = self.target / ".claude/runtime/profiles/selected.json"
        self.assertEqual(json.loads(selected.read_text(encoding="utf-8")), first)
        path = self.store / "strict/pack.yaml"
        stamp = path.stat()
        path.write_text(path.read_text(encoding="utf-8").replace("hard", "off"), encoding="utf-8")
        os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        self.assertIn("PROFILE_DRIFT", self.shell(
            BOOTSTRAP, env=env, success=False, source_resolver=False,
        ).stderr)
        rebind_env = dict(env, LINTEL_PROFILE_CONTEXT=first["context_id"])
        rebound = json.loads(self.shell(
            "rebind_profile_context 'explicit selected-work replan'", env=rebind_env,
        ).stdout)
        self.assertEqual(json.loads(self.shell(
            BOOTSTRAP, env=env, source_resolver=False,
        ).stdout), rebound)

    def test_concurrent_no_id_bootstraps_share_one_binding(self):
        self.pack("strict")
        self.require("strict")
        env = dict(self.env)
        env.pop("LINTEL_PROFILE_CONTEXT")
        processes = [
            subprocess.Popen(
                [OPTIONS.bash, "-c", BOOTSTRAP], cwd=self.target, env=env,
                text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            ) for _ in range(2)
        ]
        references = []
        try:
            for process in processes:
                stdout, stderr = process.communicate(timeout=45)
                self.assertEqual(process.returncode, 0, stderr)
                references.append(json.loads(stdout))
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                    process.communicate()
        self.assertEqual(references[0], references[1])
        self.assertEqual(references[0]["generation"], 1)
        self.assertEqual(len(list((self.home / "sessions").glob("**/current-profile.json"))), 1)

    def test_bootstrap_required_load_failure_does_not_create_successful_selection(self):
        self.require("missing")
        env = dict(self.env)
        env.pop("LINTEL_PROFILE_CONTEXT")
        result = self.shell(
            'source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"\n'
            'lintel_copilot_env "$LINTEL_REPO_ROOT"',
            env=env, success=False, source_resolver=False,
        )
        self.assertIn("PROFILE_REQUIRED", result.stderr)
        self.assertFalse((self.target / ".claude/runtime/profiles/selected.json").exists())

    def test_explicit_invocation_selection_survives_reference_only_resume(self):
        self.pack("strict")
        env = dict(self.env, LINTEL_PROFILE_PACK="strict")
        first = json.loads(self.shell("profile_context_reference", env=env).stdout)
        handoff = self.target / "handoff.json"
        handoff.write_text(json.dumps(first), encoding="utf-8")
        env.pop("LINTEL_PROFILE_PACK")
        env.pop("LINTEL_PROFILE_CONTEXT")
        env["HANDOFF"] = handoff.as_posix()
        self.assertEqual(json.loads(self.shell(
            'verify_profile_context "$HANDOFF"', env=env,
        ).stdout), first)

    def assert_reference_resume_controls_following_reads(self, host_session=None):
        self.pack("strict")
        producer_env = dict(self.env, LINTEL_PROFILE_PACK="strict")
        reference = json.loads(self.shell("profile_context_reference", env=producer_env).stdout)
        handoff = self.target / "required-reference.json"
        handoff.write_text(json.dumps(reference), encoding="utf-8")
        env = dict(self.env, HANDOFF=handoff.as_posix())
        env.pop("LINTEL_PROFILE_CONTEXT")
        if host_session is not None:
            env["CLAUDE_SESSION_ID"] = host_session
        result = self.shell(
            'verify_profile_context "$HANDOFF" || exit $?\n'
            'profile_required_policy || exit $?\n'
            'resolve_pack_field compliance.mode || exit $?\n'
            'printf "\\n"\n'
            'profile_context_reference || exit $?\n'
            'bash -c \'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
            'profile_required_policy || exit $?\n'
            'resolve_pack_field compliance.mode || exit $?\n'
            'printf "\\n"\n'
            'profile_context_reference || exit $?\n'
            'get_active_pack_name || exit $?\n'
            'printf "\\n"\n'
            'get_loaded_pack || exit $?\'',
            env=env,
        )
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 9, result.stdout)
        for index in (0, 3, 6):
            self.assertEqual(json.loads(lines[index]), reference)
        for index in (1, 4):
            policy = json.loads(lines[index])
            self.assertIs(policy["required"], True)
            self.assertEqual(policy["status"], "loaded")
            self.assertEqual(policy["source"], "invocation:LINTEL_PROFILE_PACK")
            self.assertEqual(policy["applicability"], "applicable")
            self.assertEqual(policy["version"], reference["version"])
        self.assertEqual(lines[2], "hard")
        self.assertEqual(lines[5], "hard")
        self.assertEqual(lines[7:], ["strict", "strict"])
        self.assertEqual(len(list((self.home / "sessions").glob("**/current-profile.json"))), 1)

    def test_reference_only_resume_controls_accessors_and_inherited_process_without_host_id(self):
        self.assert_reference_resume_controls_following_reads()

    def test_reference_only_resume_controls_accessors_and_inherited_process_with_new_host_id(self):
        self.assert_reference_resume_controls_following_reads("different-real-host-session")

    def test_resumed_reference_rejects_later_generation_and_missing_pin(self):
        self.pack("strict")
        producer_env = dict(self.env, LINTEL_PROFILE_PACK="strict")
        reference = json.loads(self.shell("profile_context_reference", env=producer_env).stdout)
        pin = Path(self.shell("_profile_cli context-path", env=producer_env).stdout)
        handoff = self.target / "required-reference.json"
        handoff.write_text(json.dumps(reference), encoding="utf-8")
        error_policy = self.target / "missing-pin-policy.json"
        env = dict(self.env, HANDOFF=handoff.as_posix(), PIN=pin.as_posix(),
                   ERROR_POLICY=error_policy.as_posix())
        env.pop("LINTEL_PROFILE_CONTEXT")
        result = self.shell(
            'verify_profile_context "$HANDOFF" >/dev/null || exit $?\n'
            'bash -c \'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
            'rebind_profile_context "explicit child-process replan" >/dev/null\' || exit $?\n'
            'resolve_pack_field compliance.mode',
            env=env, success=False,
        )
        self.assertIn("PROFILE_REFERENCE_MISMATCH", result.stderr)
        updated = json.loads(self.shell("profile_context_reference", env=producer_env).stdout)
        handoff.write_text(json.dumps(updated), encoding="utf-8")
        result = self.shell(
            'verify_profile_context "$HANDOFF" >/dev/null || exit $?\n'
            'rm -- "$PIN" || exit $?\n'
            'if profile_required_policy >"$ERROR_POLICY"; then exit 90; fi\n'
            'resolve_pack_field compliance.mode',
            env=env, success=False,
        )
        self.assertIn("PROFILE_CONTEXT_MISSING", result.stderr)
        policy = json.loads(error_policy.read_text(encoding="utf-8"))
        self.assertIs(policy["required"], True)
        self.assertEqual(policy["status"], "error")
        self.assertEqual(policy["applicability"], "unknown")
        self.assertFalse(pin.exists())

    def test_failed_resume_keeps_the_previous_verified_selection(self):
        self.pack("strict")
        producer_env = dict(self.env, LINTEL_PROFILE_PACK="strict")
        reference = json.loads(self.shell("profile_context_reference", env=producer_env).stdout)
        handoff = self.target / "required-reference.json"
        rejected = self.target / "rejected-reference.json"
        handoff.write_text(json.dumps(reference), encoding="utf-8")
        rejected.write_text(json.dumps(dict(reference, digest="sha256:" + "0" * 64)), encoding="utf-8")
        env = dict(self.env, HANDOFF=handoff.as_posix(), REJECTED=rejected.as_posix())
        env.pop("LINTEL_PROFILE_CONTEXT")
        result = self.shell(
            'verify_profile_context "$HANDOFF" >/dev/null || exit $?\n'
            'if verify_profile_context "$REJECTED"; then exit 90; fi\n'
            'profile_required_policy || exit $?\n'
            'profile_context_reference || exit $?\n'
            'resolve_pack_field compliance.mode',
            env=env,
        )
        lines = result.stdout.splitlines()
        self.assertIn("PROFILE_REFERENCE_MISMATCH", result.stderr)
        self.assertEqual(json.loads(lines[0])["status"], "loaded")
        self.assertIs(json.loads(lines[0])["required"], True)
        self.assertEqual(json.loads(lines[1]), reference)
        self.assertEqual(lines[2], "hard")

    def test_explicit_context_file_and_tampered_context_refuse_replacement(self):
        first = self.reference()
        path = Path(self.shell("_profile_cli context-path").stdout)
        env = dict(self.env, LINTEL_PROFILE_CONTEXT_FILE=path.as_posix())
        env.pop("LINTEL_PROFILE_CONTEXT")
        self.assertEqual(json.loads(self.shell("profile_context_reference", env=env).stdout), first)
        data = json.loads(path.read_text(encoding="utf-8"))
        data["profile"]["values"]["compliance"]["mode"] = "off"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertIn("PROFILE_CONTEXT_INVALID", self.shell("get_loaded_pack", env=env, success=False).stderr)
        outside = dict(env, LINTEL_PROFILE_CONTEXT_FILE=(self.target / "not-runtime.json").as_posix())
        self.assertIn("PROFILE_IO", self.shell("get_loaded_pack", env=outside, success=False).stderr)

    def test_required_policy_bridge_is_not_control_clearance(self):
        optional = json.loads(self.shell("profile_required_policy").stdout)
        self.assertEqual(set(optional), {"required", "status", "source", "version", "applicability"})
        self.assertEqual(optional["status"], "not_required")
        self.assertEqual(optional["applicability"], "not_applicable")
        self.pack("strict")
        self.require("strict")
        self.env["LINTEL_PROFILE_CONTEXT"] = "policy-bridge"
        policy = json.loads(self.shell("profile_required_policy").stdout)
        self.assertIs(policy["required"], True)
        self.assertEqual(policy["status"], "loaded")
        (self.store / "strict/pack.yaml").unlink()
        failure = self.shell("profile_required_policy", success=False, error_data=True)
        result = json.loads(failure.stdout)
        self.assertIs(result["required"], True)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["applicability"], "unknown")

    def test_same_mtime_manifest_parent_pointer_and_deleted_parent_are_drift(self):
        self.pack("base")
        child = self.pack("child", parent="base")
        self.pack("other")
        self.select("child")
        original = self.reference()
        context_file = Path(self.shell("_profile_cli context-path").stdout)
        saved_context = context_file.read_bytes()
        for path, changed in (
            (child, child.read_text(encoding="utf-8") + "brand: {name: Changed}\n"),
            (self.store / "base/pack.yaml", (self.store / "base/pack.yaml").read_text(encoding="utf-8").replace("hard", "off")),
            (self.store / "active-pack", "other\n"),
        ):
            data, stat = path.read_bytes(), path.stat()
            path.write_text(changed, encoding="utf-8")
            os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            self.assertIn("PROFILE_DRIFT", self.shell("resolve_pack_field compliance.mode", success=False).stderr)
            self.assertEqual(context_file.read_bytes(), saved_context)
            path.write_bytes(data)
            os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            self.assertEqual(self.reference(), original)
        parent = self.store / "base/pack.yaml"
        parent.unlink()
        self.assertIn("PROFILE_DRIFT", self.shell("get_loaded_pack", success=False).stderr)
        self.assertEqual(context_file.read_bytes(), saved_context)

    def test_explicit_rebind_preserves_previous_evidence_and_revokes_old_reference(self):
        self.pack("first")
        self.pack("second")
        self.select("first")
        first = self.reference()
        handoff = self.target / "old-reference.json"
        handoff.write_text(json.dumps(first), encoding="utf-8")
        self.select("second")
        self.assertIn("PROFILE_DRIFT", self.shell("get_loaded_pack", success=False).stderr)
        second = json.loads(self.shell("rebind_profile_context 'approved replan'").stdout)
        self.assertEqual(second["generation"], first["generation"] + 1)
        self.assertEqual(second["name"], "second")
        self.assertNotEqual(second["digest"], first["digest"])
        archives = list((self.home / "sessions").glob("**/history/*.json"))
        self.assertEqual(len(archives), 1)
        self.assertEqual(json.loads(archives[0].read_text(encoding="utf-8"))["digest"], first["digest"])
        env = dict(self.env, HANDOFF=handoff.as_posix())
        self.assertIn("PROFILE_REFERENCE_MISMATCH", self.shell(
            'verify_profile_context "$HANDOFF"', env=env, success=False,
        ).stderr)

    def test_concurrent_rebinds_publish_current_and_selected_as_one_transaction(self):
        self.pack("strict")
        self.require("strict")
        env = dict(self.env)
        env.pop("LINTEL_PROFILE_CONTEXT")
        original = json.loads(self.shell(BOOTSTRAP, env=env, source_resolver=False).stdout)
        script = r'''
import json
from contextlib import contextmanager
from pathlib import Path
import sys
import time
sys.path.insert(0, sys.argv[1])
import profile_context as profile
source, repo, home, context, label, schedule = sys.argv[2:]
source, repo, home, schedule = map(Path, (source, repo, home, schedule))
config = profile.ProfileConfig(source, repo, home, home / "packs",
                               home / "packs/active-pack", context_id=context)
original_lock = profile._lock
@contextmanager
def scheduled_lock(config, path):
    if label == "B" and path.with_name(path.name + ".lock").exists():
        (schedule / "release-a").touch()
    with original_lock(config, path):
        yield
    if label == "A" and path == profile.context_path(config):
        (schedule / "a-context-released").touch()
        deadline = time.monotonic() + 15
        while not (schedule / "release-a").exists():
            if time.monotonic() >= deadline:
                raise RuntimeError("test scheduling barrier timed out")
            time.sleep(0.01)
profile._lock = scheduled_lock
try:
    result = profile.rebind_profile_context(config, "synthetic concurrent replan " + label)
    print(json.dumps(profile.profile_reference(result)))
finally:
    if label == "B":
        (schedule / "release-a").touch()
'''
        arguments = [
            sys.executable, "-c", script, str(self.source / "lib"), str(self.source),
            str(self.target), str(self.home), original["context_id"],
        ]
        a = subprocess.Popen(
            arguments + ["A", str(self.base)], cwd=self.target, env=env,
            text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        processes = [a]
        try:
            deadline = time.monotonic() + 15
            marker = self.base / "a-context-released"
            while not marker.exists():
                if a.poll() is not None or time.monotonic() >= deadline:
                    stdout, stderr = a.communicate(timeout=5)
                    self.fail("first rebind did not reach scheduling barrier: " + stderr + stdout)
                time.sleep(0.01)
            b = subprocess.Popen(
                arguments + ["B", str(self.base)], cwd=self.target, env=env,
                text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            processes.append(b)
            references = []
            for process in processes:
                stdout, stderr = process.communicate(timeout=25)
                self.assertEqual(process.returncode, 0, stderr + stdout)
                references.append(json.loads(stdout))
        finally:
            (self.base / "release-a").touch()
            for process in processes:
                if process.poll() is None:
                    process.kill()
                    process.communicate()
        self.assertEqual(sorted(ref["generation"] for ref in references), [2, 3])
        latest = max(references, key=lambda ref: ref["generation"])
        selected = self.target / ".claude/runtime/profiles/selected.json"
        self.assertEqual(json.loads(selected.read_text(encoding="utf-8")), latest)
        resumed = json.loads(self.shell(BOOTSTRAP, env=env, source_resolver=False).stdout)
        self.assertEqual(resumed, latest)
        history = sorted(json.loads(path.read_text(encoding="utf-8"))["generation"]
                         for path in (self.home / "sessions").glob("**/history/*.json"))
        self.assertEqual(history, [1, 2])

    def test_rebind_recovers_history_backed_stale_selected_reference(self):
        self.pack("strict")
        self.require("strict")
        env = dict(self.env)
        env.pop("LINTEL_PROFILE_CONTEXT")
        original = json.loads(self.shell(BOOTSTRAP, env=env, source_resolver=False).stdout)
        rebind_env = dict(env, LINTEL_PROFILE_CONTEXT=original["context_id"])
        second = json.loads(self.shell(
            "rebind_profile_context 'synthetic first replan'", env=rebind_env,
        ).stdout)
        selected = self.target / ".claude/runtime/profiles/selected.json"
        selected.write_text(json.dumps(original), encoding="utf-8")
        self.assertIn("PROFILE_REFERENCE_MISMATCH", self.shell(
            BOOTSTRAP, env=env, success=False, source_resolver=False,
        ).stderr)
        recovered = json.loads(self.shell(
            "rebind_profile_context 'recover interrupted selected-reference publication'",
            env=rebind_env,
        ).stdout)
        self.assertEqual(recovered["generation"], second["generation"] + 1)
        self.assertEqual(json.loads(selected.read_text(encoding="utf-8")), recovered)
        self.assertEqual(json.loads(self.shell(
            BOOTSTRAP, env=env, source_resolver=False,
        ).stdout), recovered)
        history = sorted(json.loads(path.read_text(encoding="utf-8"))["generation"]
                         for path in (self.home / "sessions").glob("**/history/*.json"))
        self.assertEqual(history, [1, 2])

    def test_rebind_preserves_other_selection_and_rejects_unbacked_recovery(self):
        self.pack("strict")
        self.require("strict")
        env = dict(self.env)
        env.pop("LINTEL_PROFILE_CONTEXT")
        original = json.loads(self.shell(BOOTSTRAP, env=env, source_resolver=False).stdout)
        selected = self.target / ".claude/runtime/profiles/selected.json"
        self.shell("bind_profile_context independent-work", env=env)
        self.shell(
            "rebind_profile_context 'independent work replan'",
            env=dict(env, LINTEL_PROFILE_CONTEXT="independent-work"),
        )
        self.assertEqual(json.loads(selected.read_text(encoding="utf-8")), original)
        rebind_env = dict(env, LINTEL_PROFILE_CONTEXT=original["context_id"])
        pin = Path(self.shell("_profile_cli context-path", env=rebind_env).stdout)
        before = pin.read_bytes()
        selected.write_text(json.dumps(dict(original, generation=99)), encoding="utf-8")
        result = self.shell(
            "rebind_profile_context 'reject fabricated selection history'",
            env=rebind_env, success=False,
        )
        self.assertIn("PROFILE_REFERENCE_MISMATCH", result.stderr)
        self.assertEqual(pin.read_bytes(), before)
        self.assertEqual(json.loads(selected.read_text(encoding="utf-8"))["generation"], 99)
        selected.write_text(json.dumps(original), encoding="utf-8")
        self.assertEqual(json.loads(self.shell(
            BOOTSTRAP, env=env, source_resolver=False,
        ).stdout), original)

    def test_compatibility_axes_and_legacy_marker_are_independent(self):
        self.pack("legacy", 'requires_lintel: ">=4.0.0"\n')
        self.assertEqual(self.shell("validate_pack legacy").stdout, "")
        self.pack("compatible", (
            'schema_version: "1"\nrequires_lintel_product: ">=0.9.0 <1.0.0"\n'
            'requires_capabilities: {profile-context: ">=1.0.0", pack-inheritance: "1.0.0"}\n'
        ))
        self.assertEqual(self.shell("validate_pack compatible").stdout, "")
        compatibility = json.loads(self.shell("pack_compatibility compatible").stdout)[0]
        installed_version = json.loads(
            (self.source / ".claude-plugin/plugin.json").read_text(encoding="utf-8"),
        )["version"]
        self.assertEqual(compatibility["schema_version"], "1")
        self.assertEqual(compatibility["product_version"], installed_version)
        self.assertEqual(compatibility["capabilities"],
                         {"profile-context": ">=1.0.0", "pack-inheritance": "1.0.0"})
        for name, extra, diagnostic in (
            ("schema-bad", 'schema_version: "2"\n', "schema"),
            ("product-bad", 'requires_lintel_product: ">=99.0.0"\n', "product"),
            ("capability-bad", 'requires_capabilities: {profile-context: ">=2.0.0"}\n', "capability"),
            ("unknown-feature", 'requires_capabilities: {imaginary-host: "1.0.0"}\n', "capability"),
            ("legacy-ambiguous", 'requires_lintel: ">=5.0.0"\n', "migrate"),
        ):
            self.pack(name, extra)
            result = self.shell(f"validate_pack {name}", success=False)
            self.assertIn(diagnostic, result.stderr)
        self.pack("child", "requires_capabilities: {}\n", parent="capability-bad")
        self.assertIn("capability", self.shell("validate_pack child", success=False).stderr)
        (self.source / ".claude-plugin/plugin.json").unlink()
        self.assertIn("product", self.shell("validate_pack compatible", success=False).stderr)
        self.shell("validate_pack legacy")

    def test_synthetic_profiles_change_routing_control_and_design_inputs(self):
        observed = []
        for name, workflow, mode, gates, design in (
            ("rapid", "deliver", "advisory", [], "rapid-tokens.json"),
            ("strict", "controlled", "hard", ["synthetic-evidence"], "strict-tokens.json"),
        ):
            path = self.pack(name)
            path.write_text(
                f"name: {name}\nversion: 1.0.0\nvoice: {{default_tier: internal}}\n"
                f"compliance: {{mode: {mode}, hooks: {json.dumps(gates)}}}\n"
                f"navigation: {{default_workflow: {workflow}}}\n"
                f"extension: {{is_extension: true, namespace: {name}, workflow: {workflow}}}\n"
                f"brand: {{color_tokens: {design}}}\n", encoding="utf-8",
            )
            self.require(name)
            env = dict(self.env, LINTEL_PROFILE_CONTEXT="task-" + name)
            ref = json.loads(self.shell("profile_context_reference", env=env).stdout)
            route = self.shell(
                'source "$LINTEL_SOURCE_ROOT/lib/orientator-routing.sh"\n'
                'match_workflow build "$(resolve_pack_field navigation.default_workflow)"',
                env=env,
            ).stdout
            self.assertEqual(route, f"/{name}:{workflow}")
            gate_input = json.loads(self.shell("resolve_pack_field_json compliance.hooks", env=env).stdout)
            design_input = json.loads(self.shell("resolve_pack_field_json brand.color_tokens", env=env).stdout)
            self.assertEqual(gate_input, gates)
            self.assertEqual(design_input, design)
            observed.append({"profile_ref": ref, "route": route, "gates": gate_input, "design": design_input})
        self.assertNotEqual(observed[0], observed[1])
        # This records downstream inputs, not a claim that a renderer or corporate control ran.
        artifact = self.target / "synthetic-inputs.json"
        artifact.write_text(json.dumps(observed), encoding="utf-8")
        self.assertEqual(json.loads(artifact.read_text(encoding="utf-8")), observed)

    def test_duplicate_keys_and_unsupported_yaml_are_rejected(self):
        for extra in (
            "version: 2.0.0\n",
            "flags: {enabled: true, enabled: false}\n",
            "flags: &unsafe value\n",
            "flags: !tag value\n",
            "flags: |\n  multiline\n",
            "flags: [unterminated\n",
            "flags: [one,,two]\n",
            "flags: {one: true,,two: false}\n",
            'flags: {quoted: "\\q"}\n',
        ):
            self.pack("bad", extra)
            self.shell("validate_pack bad", success=False)
        (self.target / ".claude/profile-requirements.json").write_text(
            '{"schema_version":1,"required_pack":"a","required_pack":"b"}',
            encoding="utf-8",
        )
        self.assertIn("PROFILE_REQUIRED", self.shell("get_loaded_pack", success=False).stderr)

    def test_invalid_cli_arguments_do_not_create_a_binding(self):
        for arguments in ("field", "reference unexpected", "chain ''", "yaml-field missing"):
            self.assertIn("PROFILE_INPUT", self.shell(
                "_profile_cli " + arguments, success=False,
            ).stderr)
        self.assertFalse(list((self.home / "sessions").glob("**/current-profile.json")))

    def test_manifest_values_are_never_executed(self):
        literal = "$(printf injected > profile-code-marker)"
        self.pack("literal", f"brand: {{name: '{literal}'}}\n")
        self.require("literal")
        self.assertEqual(self.shell("resolve_pack_field brand.name").stdout, literal)
        self.assertFalse((self.target / "profile-code-marker").exists())

    def test_validation_skill_executes_shared_contract_without_activation(self):
        self.pack("strict", 'requires_lintel_product: ">=0.9.0 <1.0.0"\n')
        self.require("strict")
        skill = (ROOT / "skills/pack-validate/SKILL.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```bash\n(.*?)\n```", skill, re.DOTALL)
        self.assertEqual(len(blocks), 3)
        result = self.shell("\n".join(blocks), source_resolver=False)
        self.assertIn("PASS: declared runtime contracts passed", result.stdout)
        self.assertIn("live host/company controls remain unverified", result.stdout)
        self.assertFalse(list((self.home / "sessions").glob("**/current-profile.json")))
        (self.target / ".claude/profile-requirements.json").write_text(
            '{"schema_version":1,"required_pack":null}', encoding="utf-8",
        )
        invalid = self.shell("\n".join(blocks), success=False, source_resolver=False)
        self.assertIn("PROFILE_REQUIRED", invalid.stderr)
        self.assertFalse(list((self.home / "sessions").glob("**/current-profile.json")))

    def test_explicit_roots_and_target_data_are_preserved(self):
        self.pack("strict", root=self.target / "packs")
        self.require("strict")
        (self.target / "lib").mkdir()
        (self.target / "lib/profile_context.py").write_text(
            "raise SystemExit('TARGET CODE MUST NOT EXECUTE')\n", encoding="utf-8",
        )
        launcher = self.base / "launcher/lib"
        launcher.mkdir(parents=True)
        shutil.copyfile(self.source / "lib/copilot-env.sh", launcher / "copilot-env.sh")
        env = dict(self.env, LAUNCHER=launcher.as_posix())
        result = self.shell(
            'source "$LAUNCHER/copilot-env.sh"\n'
            'lintel_copilot_env || exit $?\n'
            'profile_context_json', env=env, source_resolver=False,
        )
        profile = json.loads(result.stdout)["profile"]
        self.assertEqual(Path(profile["roots"]["source"]), self.source)
        self.assertEqual(Path(profile["roots"]["repo"]), self.target)
        self.assertEqual(Path(profile["ancestry"][-1]["path"]), self.target / "packs/strict/pack.yaml")
        self.pack("strict")
        self.assertIn("PROFILE_DRIFT", self.shell("get_loaded_pack", success=False).stderr)


if __name__ == "__main__":
    unittest.main(argv=[__file__, *TEST_ARGS], verbosity=2)
