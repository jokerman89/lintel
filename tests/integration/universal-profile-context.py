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
            "lib/context_safety.py", "bin/li-lifecycle", "bin/li-lifecycle.py",
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

    @unittest.skipUnless(os.name == "nt", "native Windows default-home long-path lifecycle")
    def test_default_home_long_runtime_keeps_fresh_shells_history_rebind_and_drift(self):
        self.target = self.base / ("profile-consumer-" + "x" * 95)
        self.target.mkdir()
        (self.target / "AGENTS.md").write_text("Synthetic long-path consumer.\n", encoding="utf-8")
        (self.target / ".claude").mkdir()
        self.require("_default")
        home = self.target / ".claude/runtime/lintel-home"
        runtime = self.target / ".claude/runtime"

        def native(path):
            return Path("\\\\?\\" + str(path))

        def cleanup_runtime():
            if native(runtime).exists():
                shutil.rmtree(native(runtime))

        self.addCleanup(cleanup_runtime)
        unused_home = self.base / "unused-operator-home"
        unused_home.mkdir()
        env = {key: value for key, value in self.env.items()
               if not key.startswith(("LINTEL_", "CLAUDE_"))}
        env.update(LINTEL_SOURCE_ROOT=self.source.as_posix(), LINTEL_REPO_ROOT=self.target.as_posix(),
                   HOME=str(unused_home), USERPROFILE=str(unused_home))
        first = json.loads(self.shell(BOOTSTRAP, env=env, source_resolver=False).stdout)
        repeated = json.loads(self.shell(BOOTSTRAP, env=env, source_resolver=False).stdout)
        self.assertEqual(repeated, first)
        self.assertEqual(first["generation"], 1)
        selected = self.target / ".claude/runtime/profiles/selected.json"
        currents = list(native(home).glob("sessions/profiles/*/current-profile.json"))
        self.assertEqual(len(currents), 1)
        current = currents[0]
        logical_current = Path(str(current)[4:])
        history = current.parent / "history"
        self.assertGreater(len(str(logical_current.parent)), 260)
        self.assertGreater(len(str(logical_current.with_name(logical_current.name + ".lock"))), 260)
        archives = list(history.iterdir())
        self.assertEqual([item.name for item in archives], [f"1-{first['digest'][7:]}.json"])
        self.assertGreater(len(str(archives[0].parent)), 260)
        record = json.loads(current.read_text(encoding="utf-8"))
        self.assertEqual(record["profile"]["roots"]["repo"], self.target.resolve().as_posix())
        self.assertEqual(record["profile"]["roots"]["source"], self.source.resolve().as_posix())
        for provenance in record["profile"]["provenance"].values():
            self.assertFalse(provenance["path"].startswith("//?/"))
        before = {path.name: path.read_bytes() for path in [current, selected, *archives]}
        self.assertEqual(json.loads(self.shell(BOOTSTRAP, env=env, source_resolver=False).stdout), first)
        self.assertEqual({path.name: path.read_bytes() for path in [current, selected, *archives]}, before)
        reference_file = self.target / "handoff.json"
        reference_file.write_text(json.dumps(first), encoding="utf-8")
        verification_env = dict(env, HANDOFF=reference_file.as_posix())
        resumed = self.shell(
            'source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"\n'
            'lintel_copilot_env "$LINTEL_REPO_ROOT" || exit $?\n'
            'verify_profile_context "$HANDOFF" || exit $?\n'
            'profile_required_policy || exit $?\n',
            env=verification_env, source_resolver=False,
        )
        self.assertEqual(json.loads(resumed.stdout.splitlines()[0]), first)
        self.assertIs(json.loads(resumed.stdout.splitlines()[1])["required"], True)
        rebound = json.loads(self.shell(
            'source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"\n'
            'lintel_copilot_env "$LINTEL_REPO_ROOT" || exit $?\n'
            'rebind_profile_context "explicit long-path replan"',
            env=env, source_resolver=False,
        ).stdout)
        self.assertEqual(rebound["generation"], 2)
        self.assertEqual(rebound["digest"], first["digest"])
        self.assertEqual(archives[0].read_bytes(), before[archives[0].name])
        self.assertEqual(sorted(path.name for path in history.iterdir()),
                         [f"1-{first['digest'][7:]}.json", f"2-{first['digest'][7:]}.json"])
        expected_bytes = {path.name: path.read_bytes() for path in [current, selected, *history.iterdir()]}
        manifest = self.source / "packs/_default/pack.yaml"
        data, stamp = manifest.read_bytes(), manifest.stat()
        manifest.write_bytes(data + b"\n# Synthetic same-mtime long-path drift\n")
        os.utime(manifest, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        refused = self.shell(BOOTSTRAP, env=env, source_resolver=False, success=False)
        self.assertIn("PROFILE_DRIFT", refused.stderr)
        self.assertEqual({path.name: path.read_bytes() for path in [current, selected, *history.iterdir()]},
                         expected_bytes)
        manifest.write_bytes(data)
        os.utime(manifest, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        self.assertEqual(json.loads(self.shell(BOOTSTRAP, env=env, source_resolver=False).stdout), rebound)
        self.assertEqual(list(unused_home.iterdir()), [])
        self.assertFalse(list(native(home).rglob(".profile-*")))
        self.assertFalse(list(native(home).rglob("*.lock")))

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

    def test_repeated_three_process_bootstrap_keeps_exact_required_profile(self):
        self.pack("strict")
        for round_number in range(12):
            with self.subTest(round=round_number):
                target = self.base / f"parallel-target-{round_number}"
                home = self.base / f"parallel-home-{round_number}"
                target.mkdir()
                (target / "AGENTS.md").write_text("Synthetic parallel bootstrap.\n", encoding="utf-8")
                (target / ".claude").mkdir()
                (target / ".claude/profile-requirements.json").write_text(
                    '{"schema_version":1,"required_pack":"strict"}', encoding="utf-8",
                )
                env = dict(self.env, LINTEL_REPO_ROOT=target.as_posix(), LINTEL_HOME=home.as_posix(),
                           LINTEL_AUDIT_DIR=(home / "audit").as_posix())
                env.pop("LINTEL_PROFILE_CONTEXT")
                code = BOOTSTRAP + "\nprofile_required_policy || exit $?\nresolve_pack_field compliance.mode"
                processes = [
                    subprocess.Popen(
                        [OPTIONS.bash, "-c", code], cwd=target, env=env, text=True, encoding="utf-8",
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    ) for _ in range(3)
                ]
                references = []
                try:
                    for process in processes:
                        stdout, stderr = process.communicate(timeout=45)
                        self.assertEqual(process.returncode, 0, stderr + stdout)
                        lines = stdout.splitlines()
                        self.assertEqual(len(lines), 3, stdout)
                        references.append(json.loads(lines[0]))
                        policy = json.loads(lines[1])
                        self.assertIs(policy["required"], True)
                        self.assertEqual(policy["status"], "loaded")
                        self.assertEqual(lines[2], "hard")
                finally:
                    for process in processes:
                        if process.poll() is None:
                            process.kill()
                            process.communicate()
                self.assertTrue(all(reference == references[0] for reference in references))
                self.assertEqual(references[0]["generation"], 1)
                self.assertEqual(json.loads(
                    (target / ".claude/runtime/profiles/selected.json").read_text(encoding="utf-8"),
                ), references[0])
                self.assertEqual(len(list(home.glob("sessions/**/current-profile.json"))), 1)

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

    def assert_bootstrap_missing_pin_is_not_first_use(self, *, repository_required=False):
        self.pack("strict")
        if repository_required:
            self.require("strict")
        env = dict(self.env, RESULT_DIR=self.target.as_posix())
        env.pop("LINTEL_PROFILE_CONTEXT")
        invocation = "" if repository_required else "LINTEL_PROFILE_PACK=strict "
        result = self.shell(
            'source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"\n'
            + invocation + 'lintel_copilot_env "$LINTEL_REPO_ROOT" || exit $?\n'
            'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
            'profile_required_policy >"$RESULT_DIR/before-policy.json" || exit $?\n'
            'profile_context_reference >"$RESULT_DIR/before-reference.json" || exit $?\n'
            'pin=$(_profile_cli context-path) || exit $?\n'
            'printf "%s" "$pin" >"$RESULT_DIR/pin-path"\n'
            'rm -- "$pin" || exit $?\n'
            'policy_rc=0; profile_required_policy >"$RESULT_DIR/after-policy.json" || policy_rc=$?\n'
            'field_rc=0; resolve_pack_field compliance.mode >"$RESULT_DIR/after-field" || field_rc=$?\n'
            'printf "%s %s\\n" "$policy_rc" "$field_rc"\n',
            env=env, source_resolver=False,
        )
        policy_before = json.loads((self.target / "before-policy.json").read_text(encoding="utf-8"))
        self.assertIs(policy_before["required"], True)
        self.assertEqual(policy_before["status"], "loaded")
        self.assertEqual(result.stdout.strip(), "2 2", result.stderr)
        policy_after = json.loads((self.target / "after-policy.json").read_text(encoding="utf-8"))
        self.assertIs(policy_after["required"], True)
        self.assertEqual(policy_after["status"], "error")
        self.assertEqual(policy_after["applicability"], "unknown")
        self.assertEqual((self.target / "after-field").read_text(encoding="utf-8"), "")
        self.assertFalse(Path((self.target / "pin-path").read_text(encoding="utf-8")).exists())

    def test_invocation_scoped_documented_bootstrap_cannot_recreate_lost_pin(self):
        self.assert_bootstrap_missing_pin_is_not_first_use()

    def test_repo_required_documented_bootstrap_cannot_recreate_lost_pin(self):
        self.assert_bootstrap_missing_pin_is_not_first_use(repository_required=True)

    def selection_entrypoint(self, entry):
        self.pack("strict")
        env = dict(self.env, RESULT_DIR=self.target.as_posix())
        env.pop("LINTEL_PROFILE_CONTEXT")
        if entry == "bootstrap":
            return env, (
                'source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"\n'
                'LINTEL_PROFILE_PACK=strict lintel_copilot_env "$LINTEL_REPO_ROOT" || exit $?\n'
                'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
            )
        if entry in ("bind", "clear"):
            env["LINTEL_PROFILE_CONTEXT"] = "matrix-" + entry
            command = 'bind_profile_context "$LINTEL_PROFILE_CONTEXT"' if entry == "bind" else "clear_pack_cache"
            return env, (
                'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
                f'LINTEL_PROFILE_PACK=strict {command} >/dev/null || exit $?\n'
            )
        producer = dict(self.env, LINTEL_PROFILE_PACK="strict", LINTEL_PROFILE_CONTEXT="matrix-" + entry)
        reference = json.loads(self.shell("profile_context_reference", env=producer).stdout)
        handoff = self.target / ("matrix-" + entry + ".json")
        handoff.write_text(json.dumps(reference), encoding="utf-8")
        env["HANDOFF"] = handoff.as_posix()
        if entry == "verify":
            return env, (
                'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
                'verify_profile_context "$HANDOFF" >/dev/null || exit $?\n'
            )
        self.assertEqual(entry, "rebind")
        env["LINTEL_PROFILE_CONTEXT"] = reference["context_id"]
        return env, (
            'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
            'rebind_profile_context "explicit matrix replan" >/dev/null || exit $?\n'
        )

    def test_all_selection_entrypoints_export_exact_reference_to_actual_child(self):
        for entry in ("bootstrap", "bind", "verify", "rebind", "clear"):
            with self.subTest(entrypoint=entry):
                env, selection = self.selection_entrypoint(entry)
                result = self.shell(
                    selection
                    + 'printf "%s\\n" "${LINTEL_PROFILE_REFERENCE:-}"\n'
                    'profile_context_reference || exit $?\n'
                    'profile_required_policy || exit $?\n'
                    'bash -c \'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
                    'profile_context_reference || exit $?\n'
                    'profile_required_policy || exit $?\n'
                    'resolve_pack_field compliance.mode || exit $?\'',
                    env=env, source_resolver=False,
                )
                lines = result.stdout.splitlines()
                self.assertEqual(len(lines), 6, result.stdout)
                self.assertTrue(lines[0], "selection exported no exact reference")
                reference = json.loads(lines[0])
                self.assertEqual(reference, json.loads(lines[1]))
                self.assertEqual(reference, json.loads(lines[3]))
                for index in (2, 4):
                    policy = json.loads(lines[index])
                    self.assertIs(policy["required"], True)
                    self.assertEqual(policy["status"], "loaded")
                self.assertEqual(lines[5], "hard")

    def test_cli_bootstrap_returns_complete_reference_not_an_id_only_binding(self):
        self.pack("strict")
        env = dict(self.env, LINTEL_PROFILE_PACK="strict")
        env.pop("LINTEL_PROFILE_CONTEXT")
        result = self.shell("_profile_cli bootstrap", env=env)
        reference = json.loads(result.stdout)
        self.assertEqual(set(reference),
                         {"schema_version", "context_id", "generation", "digest", "name", "version"})
        self.assertEqual(reference["name"], "strict")
        self.assertEqual(reference["generation"], 1)
        consumer = dict(env, LINTEL_PROFILE_REFERENCE=json.dumps(reference))
        consumer.pop("LINTEL_PROFILE_PACK")
        self.assertEqual(json.loads(self.shell("profile_context_reference", env=consumer).stdout), reference)
        self.assertEqual(self.shell("resolve_pack_field compliance.mode", env=consumer).stdout, "hard")

    def test_all_selection_entrypoints_reject_child_rebind_until_explicit_verify(self):
        for entry in ("bootstrap", "bind", "verify", "rebind", "clear"):
            with self.subTest(entrypoint=entry):
                env, selection = self.selection_entrypoint(entry)
                result = self.shell(
                    selection
                    + 'profile_context_reference >"$RESULT_DIR/parent-reference.json" || exit $?\n'
                    'bash -c \'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
                    'rebind_profile_context "explicit child replan"\' >"$RESULT_DIR/child-reference.json" || exit $?\n'
                    'rc=0; resolve_pack_field compliance.mode >"$RESULT_DIR/stale-field" || rc=$?\n'
                    'printf "%s\\n" "$rc"\n'
                    'if [ "$rc" -eq 0 ]; then exit 0; fi\n'
                    'verify_profile_context "$RESULT_DIR/child-reference.json" >/dev/null || exit $?\n'
                    'profile_context_reference || exit $?\n'
                    'profile_required_policy || exit $?\n'
                    'resolve_pack_field compliance.mode || exit $?\n',
                    env=env, source_resolver=False,
                )
                lines = result.stdout.splitlines()
                self.assertEqual(lines[0], "2", result.stdout)
                self.assertEqual((self.target / "stale-field").read_text(encoding="utf-8"), "")
                child = json.loads((self.target / "child-reference.json").read_text(encoding="utf-8"))
                parent = json.loads((self.target / "parent-reference.json").read_text(encoding="utf-8"))
                self.assertEqual(child["generation"], parent["generation"] + 1)
                self.assertEqual(json.loads(lines[1]), child)
                self.assertIs(json.loads(lines[2])["required"], True)
                self.assertEqual(lines[3], "hard")

    def test_same_id_bind_does_not_clear_expected_generation(self):
        env, selection = self.selection_entrypoint("bind")
        result = self.shell(
            selection
            + 'bash -c \'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
            'rebind_profile_context "explicit independent generation"\' >/dev/null || exit $?\n'
            'bind_profile_context "$LINTEL_PROFILE_CONTEXT"',
            env=env, source_resolver=False, success=False,
        )
        self.assertIn("PROFILE_REFERENCE_MISMATCH", result.stderr)

    def test_id_only_create_cannot_reset_missing_context_with_retained_history(self):
        self.pack("strict")
        env = dict(self.env, LINTEL_PROFILE_PACK="strict")
        first = json.loads(self.shell("profile_context_reference", env=env).stdout)
        second = json.loads(self.shell("rebind_profile_context 'recorded generation two'", env=env).stdout)
        path = Path(self.shell("_profile_cli context-path", env=env).stdout)
        path.unlink()
        history_before = {item.name: item.read_bytes() for item in path.parent.glob("history/*.json")}
        self.assertTrue(history_before)
        resumed = dict(self.env)
        for command in (
            "get_loaded_pack", 'bind_profile_context "$LINTEL_PROFILE_CONTEXT"',
            "clear_pack_cache",
            'source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"\nlintel_copilot_env "$LINTEL_REPO_ROOT"',
        ):
            with self.subTest(command=command):
                result = self.shell(command, env=resumed, success=False)
                self.assertIn("PROFILE_CONTEXT_MISSING", result.stderr)
                self.assertFalse(path.exists())
                self.assertEqual({item.name: item.read_bytes() for item in path.parent.glob("history/*.json")},
                                 history_before)
        self.assertEqual(second["generation"], first["generation"] + 1)

    def test_first_generation_history_blocks_id_only_recreation_and_unknown_policy_is_required(self):
        self.pack("strict")
        env, selection = self.selection_entrypoint("bind")
        self.shell(selection, env=env, source_resolver=False)
        pin = Path(self.shell("_profile_cli context-path", env=env).stdout)
        pin.unlink()
        result = self.shell("profile_required_policy", env=env, success=False, error_data=True)
        policy = json.loads(result.stdout)
        self.assertIs(policy["required"], True)
        self.assertEqual(policy["status"], "error")
        self.assertEqual(policy["applicability"], "unknown")
        self.assertIn("PROFILE_CONTEXT_MISSING", result.stderr)
        self.assertFalse(pin.exists())
        self.assertEqual(len(list(pin.parent.glob("history/*.json"))), 1)

    def test_all_selection_entrypoints_reject_missing_and_replaced_pin_in_parent_and_child(self):
        replacement = self.target / "replacement-neutral.json"
        neutral = self.shell(
            "profile_context_json", env=dict(self.env, LINTEL_PROFILE_CONTEXT="replacement-fixture"),
        ).stdout
        replacement.write_text(neutral, encoding="utf-8")
        for entry in ("bootstrap", "bind", "verify", "rebind", "clear"):
            with self.subTest(entrypoint=entry):
                env, selection = self.selection_entrypoint(entry)
                env["REPLACEMENT"] = replacement.as_posix()
                result = self.shell(
                    selection
                    + 'pin=$(_profile_cli context-path) || exit $?\n'
                    'cp -- "$pin" "$RESULT_DIR/original-current.json" || exit $?\n'
                    'for change in missing replacement; do\n'
                    '  if [ "$change" = missing ]; then rm -- "$pin"; else cp -- "$REPLACEMENT" "$pin"; fi\n'
                    '  policy_rc=0; profile_required_policy >"$RESULT_DIR/$change-parent-policy.json" || policy_rc=$?\n'
                    '  field_rc=0; resolve_pack_field compliance.mode >"$RESULT_DIR/$change-parent-field" || field_rc=$?\n'
                    '  printf "%s %s\\n" "$policy_rc" "$field_rc"\n'
                    '  CHANGE="$change" bash -c \'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
                    '    policy_rc=0; profile_required_policy >"$RESULT_DIR/$CHANGE-child-policy.json" || policy_rc=$?\n'
                    '    field_rc=0; resolve_pack_field compliance.mode >"$RESULT_DIR/$CHANGE-child-field" || field_rc=$?\n'
                    '    printf "%s %s\\n" "$policy_rc" "$field_rc"\'\n'
                    '  cp -- "$RESULT_DIR/original-current.json" "$pin" || exit $?\n'
                    'done\n'
                    'resolve_pack_field compliance.mode || exit $?\n',
                    env=env, source_resolver=False,
                )
                self.assertEqual(result.stdout.splitlines(), ["2 2", "2 2", "2 2", "2 2", "hard"])
                for change in ("missing", "replacement"):
                    for consumer in ("parent", "child"):
                        policy = json.loads((self.target / f"{change}-{consumer}-policy.json").read_text(encoding="utf-8"))
                        self.assertIs(policy["required"], True)
                        self.assertEqual(policy["status"], "error")
                        self.assertEqual(policy["applicability"], "unknown")
                        self.assertEqual((self.target / f"{change}-{consumer}-field").read_text(encoding="utf-8"), "")

    def test_python_create_true_distinguishes_initial_binding_from_lost_history(self):
        self.pack("strict")
        script = r'''
import json
from dataclasses import replace
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
import profile_context as profile
source, repo, home = map(Path, sys.argv[2:])
config = profile.ProfileConfig(source, repo, home, home / "packs", home / "packs/active-pack",
                               context_id="python-work", explicit_pack="strict")
first = profile.load_profile_context(config, create=True)
reference = profile.profile_reference(first)
pin = profile.context_path(config)
pin.unlink()
try:
    profile.load_profile_context(replace(config, explicit_pack=""), create=True)
except profile.ProfileError as error:
    assert error.code == "PROFILE_CONTEXT_MISSING", error.code
else:
    raise AssertionError("create=True recreated a previously bound context")
assert not pin.exists()
recovered = profile.rebind_profile_context(
    replace(config, explicit_pack="", expected_reference=reference),
    "explicit recovery of missing first published generation",
)
assert recovered["generation"] == 2
assert profile.required_policy(recovered)["required"] is True
assert recovered["profile"]["values"]["compliance"]["mode"] == "hard"
print(json.dumps(profile.profile_reference(recovered)))
'''
        result = subprocess.run(
            [sys.executable, "-c", script, str(self.source / "lib"), str(self.source),
             str(self.target), str(self.home)], cwd=self.target, env=self.env,
            text=True, encoding="utf-8", capture_output=True, timeout=45,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["generation"], 2)

    def test_bootstrap_rebind_explicitly_recovers_latest_required_pin_and_updates_children(self):
        env, selection = self.selection_entrypoint("bootstrap")
        result = self.shell(
            selection
            + 'profile_context_reference || exit $?\n'
            'for iteration in first second; do\n'
            '  pin=$(_profile_cli context-path) || exit $?\n'
            '  rm -- "$pin" || exit $?\n'
            '  rebind_profile_context "explicit latest-pin recovery $iteration" || exit $?\n'
            '  profile_required_policy || exit $?\n'
            '  bash -c \'source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
            '    profile_context_reference || exit $?\n'
            '    resolve_pack_field compliance.mode || exit $?\'\n'
            '  printf "\\n"\n'
            'done\n',
            env=env, source_resolver=False,
        )
        lines = result.stdout.splitlines()
        references = [json.loads(lines[index]) for index in (0, 1, 5)]
        self.assertEqual([ref["generation"] for ref in references], [1, 2, 3])
        for offset in (1, 5):
            self.assertIs(json.loads(lines[offset + 1])["required"], True)
            self.assertEqual(json.loads(lines[offset + 1])["status"], "loaded")
            self.assertEqual(json.loads(lines[offset + 2]), json.loads(lines[offset]))
            self.assertEqual(lines[offset + 3], "hard")
        selected = self.target / ".claude/runtime/profiles/selected.json"
        self.assertEqual(json.loads(selected.read_text(encoding="utf-8")), references[-1])
        history = sorted(json.loads(path.read_text(encoding="utf-8"))["generation"]
                         for path in (self.home / "sessions").glob("**/history/*.json"))
        self.assertEqual(history, [1, 2, 3])

    def test_retained_latest_generation_rejects_current_rollback_without_expected_reference(self):
        self.pack("strict")
        env = dict(self.env, LINTEL_PROFILE_PACK="strict")
        self.shell("profile_context_reference", env=env)
        pin = Path(self.shell("_profile_cli context-path", env=env).stdout)
        old_bytes = pin.read_bytes()
        current = json.loads(self.shell("rebind_profile_context 'publish generation two'", env=env).stdout)
        pin.write_bytes(old_bytes)
        history_before = {path.name: path.read_bytes() for path in pin.parent.glob("history/*.json")}
        for command in ("profile_context_reference", "get_loaded_pack"):
            with self.subTest(command=command):
                result = self.shell(command, env=self.env, success=False)
                self.assertIn("PROFILE_REFERENCE_MISMATCH", result.stderr)
                self.assertEqual(pin.read_bytes(), old_bytes)
                self.assertEqual({path.name: path.read_bytes() for path in pin.parent.glob("history/*.json")},
                                 history_before)
        self.assertEqual(current["generation"], 2)

    def test_explicit_recovery_requires_unambiguous_untampered_history(self):
        self.pack("strict")
        env = dict(self.env, LINTEL_PROFILE_PACK="strict")
        self.shell("profile_context_reference", env=env)
        pin = Path(self.shell("_profile_cli context-path", env=env).stdout)
        archives = list(pin.parent.glob("history/*.json"))
        self.assertEqual(len(archives), 1)
        before = archives[0].read_bytes()
        pin.unlink()
        archives[0].write_text("{}", encoding="utf-8")
        result = self.shell("rebind_profile_context 'reject corrupted recovery'", env=env, success=False)
        self.assertIn("PROFILE_CONTEXT_INVALID", result.stderr)
        self.assertFalse(pin.exists())
        archives[0].write_bytes(before)
        duplicate = archives[0].with_name("1-" + "0" * 64 + ".json")
        duplicate.write_bytes(before)
        result = self.shell("rebind_profile_context 'reject ambiguous recovery'", env=env, success=False)
        self.assertIn("PROFILE_CONTEXT_INVALID", result.stderr)
        self.assertFalse(pin.exists())

    def test_failed_bootstrap_preserves_binding_and_explicit_new_work_still_initializes(self):
        env, selection = self.selection_entrypoint("bind")
        result = self.shell(
            selection
            + 'profile_context_reference >"$RESULT_DIR/initial.json" || exit $?\n'
            'source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"\n'
            'if lintel_copilot_env "$LINTEL_REPO_ROOT" conflicting-context; then exit 90; fi\n'
            'profile_context_reference || exit $?\n'
            'profile_required_policy || exit $?\n'
            'bind_profile_context genuinely-new-work || exit $?\n'
            'profile_required_policy || exit $?\n',
            env=env, source_resolver=False,
        )
        lines = result.stdout.splitlines()
        self.assertEqual(json.loads(lines[0]), json.loads((self.target / "initial.json").read_text(encoding="utf-8")))
        self.assertIs(json.loads(lines[1])["required"], True)
        new = json.loads(lines[2])
        self.assertEqual(new["context_id"], "genuinely-new-work")
        self.assertEqual(new["generation"], 1)
        self.assertEqual(new["name"], "_default")
        self.assertEqual(json.loads(lines[3])["status"], "not_required")

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
        self.assertEqual(len(archives), 2)
        history = {json.loads(path.read_text(encoding="utf-8"))["generation"]:
                   json.loads(path.read_text(encoding="utf-8")) for path in archives}
        self.assertEqual(history[1]["digest"], first["digest"])
        self.assertEqual(history[2]["digest"], second["digest"])
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
        self.assertEqual(history, [1, 2, 3])

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
        self.assertEqual(history, [1, 2, 3])

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
        manifest = self.pack("strict", 'requires_lintel_product: ">=0.9.0 <1.0.0"\n')
        self.require("strict")
        self.select("_default")
        (self.home / "profile.yaml").write_bytes(b"# Operator-owned preference\nrole_active: none\n")
        host_home = self.base / "host home"
        host_home.mkdir()
        env = dict(self.env, HOME=str(host_home), USERPROFILE=str(host_home))
        for name in ("HOME", "USERPROFILE", "LINTEL_SOURCE_ROOT", "LINTEL_REPO_ROOT",
                     "LINTEL_HOME", "LINTEL_PACKS_DIR", "LINTEL_ACTIVE_PACK_FILE", "LINTEL_AUDIT_DIR"):
            self.assertTrue(Path(env[name]).resolve().is_relative_to(self.base.resolve()), name)
        skill = (ROOT / "skills/pack-validate/SKILL.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```bash\n(.*?)\n```", skill, re.DOTALL)
        self.assertEqual(len(blocks), 1)

        def snapshot():
            return {path.relative_to(self.base).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in self.base.rglob("*") if path.is_file()}

        def validate(target="", *, reference=None, success=True):
            invocation = dict(env, target=target)
            if reference is not None:
                invocation["LINTEL_PROFILE_REFERENCE"] = json.dumps(reference)
            before = snapshot()
            result = self.shell(blocks[0], env=invocation, success=success, source_resolver=False)
            self.assertEqual(snapshot(), before, "Validation changed source, target, profile or host-home bytes")
            return json.loads(result.stdout) if success else result

        product = json.loads((self.source / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        for target in ("", "strict"):
            with self.subTest(binding="unbound", target=target or "selected"):
                result = validate(target)
                self.assertEqual(result["name"], "strict")
                self.assertEqual(result["status"], "valid")
                self.assertEqual(result["values"]["version"], "1.2.3")
                self.assertEqual(result["values"]["voice"]["default_tier"], "internal")
                self.assertEqual(result["values"]["compliance"],
                                 {"mode": "hard", "hooks": ["synthetic-evidence"]})
                self.assertEqual(result["values"]["navigation"]["default_workflow"], "controlled")
                self.assertEqual(result["compatibility"], [{
                    "name": "strict", "schema_version": "1", "legacy_schema": True,
                    "legacy_marker": None, "product_version": product,
                    "product_requirement": ">=0.9.0 <1.0.0", "capabilities": {}, "status": "compatible",
                }])
                self.assertIsNone(result["profile_reference"])
                self.assertEqual(result["host_activation"], "not performed")
        self.assertFalse(list((self.home / "sessions").glob("**/current-profile.json")))
        self.assertFalse((self.target / ".claude/runtime/profiles/selected.json").exists())

        requirements = self.target / ".claude/profile-requirements.json"
        valid_requirements = requirements.read_bytes()
        requirements.write_text('{"schema_version":1,"required_pack":null}', encoding="utf-8")
        for target in ("", "strict", "_default"):
            with self.subTest(required_policy="malformed", target=target or "selected"):
                invalid = validate(target, success=False)
                self.assertIn("PROFILE_REQUIRED", invalid.stderr)
        self.assertFalse(list((self.home / "sessions").glob("**/current-profile.json")))
        requirements.write_bytes(valid_requirements)

        # Only the explicit producer binds a pin; the actual skill must verify it without rebinding.
        reference = json.loads(self.shell("profile_context_reference", env=env).stdout)
        self.assertEqual(reference["name"], "strict")
        for target in ("", "strict"):
            result = validate(target, reference=reference)
            self.assertEqual(result["profile_reference"], reference)
            self.assertEqual(result["host_activation"], "not performed")

        original, times = manifest.read_bytes(), manifest.stat()
        manifest.write_bytes(original + b"# same-mtime required-policy drift\n")
        os.utime(manifest, ns=(times.st_atime_ns, times.st_mtime_ns))
        for target in ("", "_default"):
            with self.subTest(binding="drifted", target=target or "selected"):
                invalid = validate(target, reference=reference, success=False)
                self.assertIn("PROFILE_DRIFT", invalid.stderr)
        manifest.write_bytes(original)
        os.utime(manifest, ns=(times.st_atime_ns, times.st_mtime_ns))
        self.assertEqual(validate(reference=reference)["profile_reference"], reference)

        current = next((self.home / "sessions").glob("**/current-profile.json"))
        original_pin = current.read_bytes()
        current.unlink()
        for target in ("", "_default"):
            with self.subTest(binding="missing", target=target or "selected"):
                invalid = validate(target, reference=reference, success=False)
                self.assertIn("PROFILE_CONTEXT_MISSING", invalid.stderr)
                self.assertFalse(current.exists())
        current.write_bytes(original_pin)
        self.assertEqual(validate(reference=reference)["profile_reference"], reference)

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
