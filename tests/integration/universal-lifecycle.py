# component: universal-lifecycle-scenarios
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P10.md
# constraints: synthetic fixtures only; no host activation or real home mutation
# last_intent_review: 2026-09-20
"""Behavioral lifecycle acceptance using the actual source-owned entry points."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PARSER = argparse.ArgumentParser()
PARSER.add_argument("--root", type=Path, required=True)
PARSER.add_argument("--bash", required=True)
PARSER.add_argument("--native-small", action="store_true")
PARSER.add_argument("--native-performer", choices=("auto", "bash"), default="auto")
OPTIONS, TEST_ARGS = PARSER.parse_known_args()
ROOT = OPTIONS.root.resolve()
sys.path.insert(0, str(ROOT / "lib"))
from native_paths import native_io_path


def hashes(root):
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*")) if path.is_file() and not path.is_symlink()}


def register_temporary_cleanup(case, temporary, prefix):
    created_name = temporary.name
    created_root = Path(created_name).resolve()

    def cleanup():
        case.assertEqual(temporary.name, created_name)
        case.assertEqual(Path(temporary.name).resolve(), created_root)
        case.assertTrue(created_root.name.startswith(prefix))
        directory = str(created_root)
        if os.name == "nt" and not directory.startswith("\\\\?\\"):
            directory = "\\\\?\\UNC\\" + directory[2:] if directory.startswith("\\\\") else "\\\\?\\" + directory
        temporary.name = directory
        try:
            temporary.cleanup()
        finally:
            temporary.name = created_name

    case.addCleanup(cleanup)


class LifecycleFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lintel-lifecycle-")
        register_temporary_cleanup(self, self.tmp, "lintel-lifecycle-")
        self.base = Path(self.tmp.name)
        self.source = self.base / "trusted source"
        self.target = self.base / "consumer"
        self.home = self.base / "installed data"
        self.store = self.base / "configured packs"
        self.pointer = self.base / "selection" / "active-pack"
        for directory in (self.source, self.target, self.home, self.store, self.pointer.parent):
            directory.mkdir()
        (self.target / "AGENTS.md").write_text("Consumer-owned instructions.\n", encoding="utf-8")
        for relative in (
            "bin/li-lifecycle", "bin/li-lifecycle.py", "bin/li-doctor",
            "lib/profile_context.py", "lib/profile-context-schema.json",
            "lib/pack-schema.yaml", "lib/context_safety.py", "lib/native_paths.py", "lib/client_capabilities.py",
            "lib/cli-tiers.yaml", "lib/markdown_source.py", "packs/_default/pack.yaml",
            ".claude-plugin/plugin.json", "docs/migrations/_INDEX.md",
            "lib/managed_transaction.py", "bin/li-snapshot.py",
        ):
            origin = ROOT / relative
            if origin.exists():
                destination = self.source / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(origin, destination)
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("LINTEL_", "CLAUDE_")) and key != "PACK_CACHE_FILE"}
        self.env.update({
            "HOME": str(self.base / "fake user"),
            "USERPROFILE": str(self.base / "fake user"),
            "LINTEL_SOURCE_ROOT": str(self.source),
            "LINTEL_REPO_ROOT": str(self.target),
            "LINTEL_HOME": str(self.home),
            "LINTEL_PACKS_DIR": str(self.store),
            "LINTEL_ACTIVE_PACK_FILE": str(self.pointer),
            "PYTHONDONTWRITEBYTECODE": "1",
        })

    def run_helper(self, *args, success=True, env=None):
        result = subprocess.run(
            [sys.executable, str(self.source / "bin/li-lifecycle.py"), *args],
            env=env or self.env, cwd=self.target, text=True, encoding="utf-8",
            capture_output=True, timeout=45,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def result(self, *args, **kwargs):
        return json.loads(self.run_helper(*args, **kwargs).stdout)

    def pack(self, name, *, root=None, extra=""):
        directory = (root or self.store) / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "pack.yaml").write_text(
            f"name: {name}\nversion: 1.0.0\n"
            "voice: {default_tier: internal}\n"
            "compliance: {mode: advisory}\n"
            "navigation: {default_workflow: cycle}\n" + extra, encoding="utf-8")
        return directory

    def require(self, name):
        directory = self.target / ".claude"
        directory.mkdir(exist_ok=True)
        (directory / "profile-requirements.json").write_text(
            json.dumps({"schema_version": 1, "required_pack": name}), encoding="utf-8")

    def role(self, directory, name="advisor", sensitivity="public"):
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{name}.md"
        path.write_text(
            f"---\nrole_id: {name}\ndisplay_name: Synthetic advisor\nscope: engineering\n"
            f"audience: maintainers\nvoice_tier: internal\nsensitivity: {sensitivity}\n"
            "last_updated: 2026-09-20\n---\n"
            "# IDENTITY\nJudge requirements against evidence.\n"
            "# COLD KNOWLEDGE\nprivate-cold-knowledge-sentinel\n"
            "# DECISION CRITERIA\nPreserve consumer choices.\n"
            "# VOICE + COMMUNICATION\nDirect and precise.\n"
            "# OUTCOME LENS\n- BUILD: working behavior.\n"
            "# ROLE-SPECIFIC INSIGHTS\nDo not infer activation from files.\n"
            "# COMPANION SKILLS\n- review\n"
            "# SENSITIVE CONTEXT\nprivate-body-sentinel\n", encoding="utf-8")
        return path


class ProfileLifecycle(LifecycleFixture):
    def test_pack_switch_uses_configured_pointer_and_fresh_process_pin(self):
        self.pack("alpha")
        self.pack("beta")
        self.pointer.write_text("alpha\n", encoding="utf-8")
        before = self.result("profile-bind")["reference"]
        legacy = self.home / "packs/active-pack"
        legacy.parent.mkdir()
        legacy.write_text("user-owned-legacy\n", encoding="utf-8")
        switched = self.result("pack-switch", "beta", "--reason", "explicit synthetic switch")
        self.assertEqual(self.pointer.read_text(encoding="utf-8"), "beta\n")
        self.assertEqual(legacy.read_text(encoding="utf-8"), "user-owned-legacy\n")
        after = switched["reference"]
        self.assertEqual(after["name"], "beta")
        self.assertEqual(after["context_id"], before["context_id"])
        self.assertEqual(after["generation"], before["generation"] + 1)
        self.assertNotEqual(after["digest"], before["digest"])
        self.assertEqual(set(after), {"schema_version", "context_id", "generation", "digest", "name", "version"})
        self.assertEqual(self.result("profile-status")["reference"], after)
        again = self.result("pack-switch", "beta", "--reason", "already selected")
        self.assertFalse(again["changed"])
        self.assertEqual(again["reference"], after)
        stale = dict(self.env, LINTEL_PROFILE_REFERENCE=json.dumps(before))
        self.assertIn("PROFILE_REFERENCE_MISMATCH", self.run_helper(
            "profile-status", env=stale, success=False).stderr)

    def test_required_or_invalid_switch_refuses_before_any_writes(self):
        self.pack("required")
        self.pack("different")
        self.require("required")
        self.pointer.write_text("required\n", encoding="utf-8")
        self.result("profile-bind")
        before = hashes(self.base)
        self.assertIn("PROFILE_REQUIRED", self.run_helper(
            "pack-switch", "different", "--reason", "not authorized to replace requirement",
            success=False).stderr)
        self.assertEqual(hashes(self.base), before)
        self.assertIn("PROFILE_REQUIRED", self.run_helper(
            "pack-switch", "missing", "--reason", "invalid target", success=False).stderr)
        self.assertEqual(hashes(self.base), before)

    def test_invalid_switch_reason_is_rejected_before_pointer_mutation(self):
        self.pack("alpha")
        self.pack("beta")
        self.pointer.write_text("alpha\n", encoding="utf-8")
        self.result("profile-bind")
        before = hashes(self.base)
        self.run_helper("pack-switch", "beta", "--reason", "x" * 1001, success=False)
        self.assertEqual(hashes(self.base), before)

    def test_drift_and_missing_pin_require_explicit_history_backed_rebind(self):
        pack = self.pack("alpha")
        self.pointer.write_text("alpha\n", encoding="utf-8")
        before = self.result("profile-bind")["reference"]
        path = pack / "pack.yaml"
        path.write_text(path.read_text(encoding="utf-8") + "# changed input\n", encoding="utf-8")
        changed = hashes(self.base)
        self.assertIn("PROFILE_DRIFT", self.run_helper("profile-bind", success=False).stderr)
        self.assertEqual(hashes(self.base), changed)
        rebound = self.result("profile-rebind", "--reason", "reviewed manifest change")["reference"]
        self.assertEqual(rebound["generation"], before["generation"] + 1)
        current = next((self.home / "sessions/profiles").glob("*/current-profile.json"))
        current.unlink()
        missing = hashes(self.base)
        self.assertIn("PROFILE_CONTEXT_MISSING", self.run_helper("profile-bind", success=False).stderr)
        self.assertEqual(hashes(self.base), missing)
        recovered = self.result("profile-rebind", "--reason", "recover exact retained context")["reference"]
        self.assertEqual(recovered["generation"], rebound["generation"] + 1)

    def test_pack_inventory_uses_resolver_precedence_without_binding(self):
        self.pack("shared")
        self.pack("shared", root=self.target / "packs")
        self.pack("local", root=self.target / "packs")
        self.pack("bundled", root=self.source / "packs")
        self.pointer.write_text("shared\n", encoding="utf-8")
        before = hashes(self.base)
        result = self.result("pack-list")
        shared = [row for row in result["packs"] if row["name"] == "shared"]
        self.assertEqual(len(shared), 2)
        self.assertEqual(sum(row["selected_source"] for row in shared), 1)
        self.assertEqual(next(row["path"] for row in shared if row["selected_source"]),
                         str(self.store / "shared"))
        self.assertEqual(result["effective_pack"], "shared")
        self.assertTrue({"_default", "local", "bundled"} <= {row["name"] for row in result["packs"]})
        self.assertEqual(hashes(self.base), before, "read-only inventory bound or rewrote context")

    def test_pack_validation_defaults_to_required_target_without_binding(self):
        self.pack("required")
        self.require("required")
        self.env["LINTEL_PROFILE_CONTEXT"] = "not-yet-bound"
        before = hashes(self.base)
        result = self.result("pack-validate")
        self.assertEqual(result["name"], "required")
        self.assertIsNone(result["profile_reference"])
        self.assertEqual(hashes(self.base), before)
        (self.target / ".claude/profile-requirements.json").write_text(
            '{"schema_version":1,"required_pack":null}', encoding="utf-8")
        before = hashes(self.base)
        failed = self.run_helper("pack-validate", "required", success=False)
        self.assertIn("PROFILE_REQUIRED", failed.stderr)
        self.assertEqual(hashes(self.base), before)

    def test_pack_creation_uses_requested_scope_and_preserves_inheritance(self):
        parent = self.pack("policy")
        text = (parent / "pack.yaml").read_text(encoding="utf-8").replace("mode: advisory", "mode: hard")
        (parent / "pack.yaml").write_text(text, encoding="utf-8")
        result = self.result("pack-create", "child", "--scope", "home", "--extends", "policy")
        manifest = self.store / "child/pack.yaml"
        self.assertEqual(result["status"], "created")
        self.assertTrue(manifest.is_file())
        self.assertNotIn("compliance:", manifest.read_text(encoding="utf-8"))
        self.assertFalse(self.pointer.exists())
        self.assertEqual(self.result("pack-validate", "child")["values"]["compliance"]["mode"], "hard")
        self.result("pack-create", "blank", "--scope", "repo")
        self.assertTrue((self.target / "packs/blank/pack.yaml").is_file())
        self.result("pack-create", "cloned", "--scope", "repo", "--from", "policy")
        self.assertEqual(self.result("pack-validate", "cloned")["values"]["compliance"]["mode"], "hard")
        before = hashes(self.base)
        self.run_helper("pack-create", "child", "--scope", "home", success=False)
        self.assertEqual(hashes(self.base), before)
        self.run_helper("pack-create", "bad", "--scope", "home", "--extends", "missing", success=False)
        self.assertEqual(hashes(self.base), before)

    def test_profile_switch_failure_is_visible_and_rebind_is_explicit(self):
        self.pack("alpha")
        self.pack("beta")
        self.pointer.write_text("alpha\n", encoding="utf-8")
        before = self.result("profile-bind")["reference"]
        script = (
            "import importlib.util,sys\n"
            "spec=importlib.util.spec_from_file_location('lifecycle',sys.argv[1])\n"
            "module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)\n"
            "def interrupted(*args,**kwargs): raise OSError('synthetic interruption after pointer')\n"
            "module.rebind_profile_context=interrupted\n"
            "sys.argv=['li-lifecycle','pack-switch','beta','--reason','synthetic interruption']\n"
            "raise SystemExit(module.main())\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script, str(self.source / "bin/li-lifecycle.py")],
            cwd=self.target, env=self.env, text=True, encoding="utf-8", capture_output=True, timeout=45,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PROFILE_SWITCH_INCOMPLETE", result.stderr)
        self.assertEqual(result.stdout.strip(), "")
        self.assertEqual(self.pointer.read_text(encoding="utf-8"), "beta\n")
        self.assertIn("PROFILE_DRIFT", self.run_helper("profile-bind", success=False).stderr)
        recovered = self.result("profile-rebind", "--reason", "explicit interrupted-switch recovery", "--pack", "beta")
        self.assertEqual(recovered["reference"]["name"], "beta")
        self.assertEqual(recovered["reference"]["generation"], before["generation"] + 1)

    def test_role_paths_refuse_traversal_and_symlink_escape(self):
        directory = self.pack("team", extra="roles: {source: ../outside}\n")
        self.pointer.write_text("team\n", encoding="utf-8")
        before = hashes(self.base)
        self.run_helper("role-list", success=False)
        self.assertEqual(hashes(self.base), before)
        (directory / "pack.yaml").write_text(
            (directory / "pack.yaml").read_text(encoding="utf-8").replace("../outside", "roles"),
            encoding="utf-8",
        )
        outside = self.role(self.base / "outside")
        (directory / "roles").mkdir()
        os.symlink(outside, directory / "roles/advisor.md")
        before = hashes(self.base)
        refused = self.run_helper("role-set", "advisor", success=False)
        self.assertIn("refused", refused.stderr.lower())
        self.assertEqual(hashes(self.base), before)
        self.assertFalse((self.home / "profile.yaml").exists())

    def test_unsupported_host_profile_is_not_a_marker_file_success(self):
        before = hashes(self.base)
        result = self.run_helper("host-profile", "dormant", "--client", "copilot-app", success=False)
        self.assertIn("UNSUPPORTED_HOST_OPERATION", result.stderr)
        self.assertNotIn("Lintel dormant", result.stdout)
        self.assertEqual(hashes(self.base), before)
        self.assertFalse(list(self.base.rglob(".disabled")))
        self.assertFalse(list(self.base.rglob(".active-profile")))

    def test_pack_relative_roles_and_preferences_preserve_custom_fields(self):
        directory = self.pack("team", extra="roles: {source: roles}\n")
        self.role(directory / "roles")
        self.pointer.write_text("team\n", encoding="utf-8")
        profile = self.home / "profile.yaml"
        original = "# keep this comment\ncustom: [a, b]\ndefault_mode: hotfix\n"
        profile.write_text(original, encoding="utf-8")
        result = self.result("role-set", "advisor")
        self.assertEqual(result["role"]["role_id"], "advisor")
        self.assertIsNotNone(result["profile_reference"])
        self.assertEqual(result["profile_reference"], self.result("profile-status")["reference"])
        self.assertIn("Judge requirements", result["summary"])
        self.assertNotIn("private-cold-knowledge-sentinel", result["summary"])
        self.assertNotIn("private-body-sentinel", result["summary"])
        self.assertTrue(profile.read_text(encoding="utf-8").startswith(original))
        self.assertEqual(self.result("role-list")["active_role"], "advisor")
        self.result("role-off")
        self.assertTrue(profile.read_text(encoding="utf-8").startswith(original))
        self.assertIsNone(self.result("role-list")["active_role"])

    def test_role_switch_preserves_inline_preference_comments(self):
        directory = self.pack("team", extra="roles: {source: roles}\n")
        self.role(directory / "roles")
        self.pointer.write_text("team\n", encoding="utf-8")
        profile = self.home / "profile.yaml"
        profile.write_text('role_active: null  # preserve this operator note\ncustom: "a # literal"\n', encoding="utf-8")
        self.result("role-set", "advisor")
        self.assertIn('role_active: "advisor"  # preserve this operator note', profile.read_text(encoding="utf-8"))
        self.result("role-off")
        self.assertIn("role_active: null  # preserve this operator note", profile.read_text(encoding="utf-8"))

    def test_private_role_read_is_explicit_and_malformed_preferences_are_preserved(self):
        self.role(self.home / "roles/private", sensitivity="private")
        profile = self.home / "profile.yaml"
        profile.write_text("role_active: old\nrole_active: duplicate\n", encoding="utf-8")
        before = hashes(self.base)
        self.run_helper("role-set", "advisor", success=False)
        self.assertEqual(hashes(self.base), before)
        refused = self.run_helper("role-set", "advisor", "--allow-private", success=False)
        self.assertIn("duplicate", refused.stderr.lower())
        self.assertEqual(hashes(self.base), before)
        profile.write_text("role_active: null\n", encoding="utf-8")
        listed = self.result("role-list", "--include-private")
        self.assertEqual(listed["roles"][0]["sensitivity"], "private")
        self.assertNotIn("private-body-sentinel", json.dumps(listed))
        result = self.result("role-set", "advisor", "--allow-private")
        self.assertNotIn("private-body-sentinel", result["summary"])
        self.assertIn("private-body-sentinel", self.result(
            "role-show", "advisor", "--deep", "--allow-private")["content"])

    def test_role_creation_is_explicit_and_does_not_sync_or_activate(self):
        draft = self.role(self.base / "draft", name="new-role", sensitivity="private")
        created = self.result("role-write", "new-role", "--file", str(draft), "--scope", "private")
        destination = self.home / "roles/private/new-role.md"
        self.assertEqual(destination.read_bytes(), draft.read_bytes())
        self.assertEqual(created["status"], "created")
        self.assertFalse((self.home / "profile.yaml").exists())
        before = hashes(self.base)
        self.run_helper("role-write", "new-role", "--file", str(draft), "--scope", "private", success=False)
        self.assertEqual(hashes(self.base), before)
        self.assertFalse((self.home / "sync").exists())

    def test_role_summary_handles_literal_delimiters_and_nested_expertise(self):
        directory = self.pack("team", extra="roles: {source: roles}\n")
        path = self.role(directory / "roles")
        text = path.read_text(encoding="utf-8").replace(
            "Synthetic advisor", '"Synthetic --- advisor"').replace(
            "Direct and precise.", "Direct and precise.\n## Vocabulary\nEvidence first.")
        path.write_text(text, encoding="utf-8")
        self.pointer.write_text("team\n", encoding="utf-8")
        result = self.result("role-show", "advisor")
        self.assertEqual(result["role"]["display_name"], "Synthetic --- advisor")
        self.assertIn("Evidence first.", result["summary"])
        self.assertNotIn("private-cold-knowledge-sentinel", result["summary"])
        self.assertNotIn("private-body-sentinel", result["summary"])

    def test_persona_sources_are_pack_relative_and_never_persist_an_overlay(self):
        directory = self.pack("team", extra="persona: {source: personas/audience.md}\n")
        (directory / "personas").mkdir()
        (directory / "personas/audience.md").write_text("Synthetic audience.\n", encoding="utf-8")
        self.pointer.write_text("team\n", encoding="utf-8")
        memory = self.target / ".claude/memory"
        memory.mkdir(parents=True)
        (memory / "personas.md").write_text("Repository audience.\n", encoding="utf-8")
        (memory / "working-state.md").write_text("User-owned working state.\n", encoding="utf-8")
        before = hashes(self.base)
        result = self.result("persona-sources")
        self.assertEqual(result["lifetime"], "current conversation only")
        self.assertIn(str(directory / "personas/audience.md"), [row["path"] for row in result["sources"]])
        self.assertEqual(hashes(self.base), before)

    def test_migrations_use_source_catalog_and_keep_overdue_unknown_states(self):
        catalog = self.source / "docs/migrations/_INDEX.md"
        catalog.write_text(
            "# Migrations\n\n## Active migrations\n\n"
            "| Slug | Started | Grace until | Removal at | Description |\n"
            "|---|---|---|---|---|\n"
            "| v5-claude-home-layout | 2026-06-12 | 2026-09-12 | 2026-12-12 | Layout |\n"
            "| unknown-detector | 2026-06-12 | 2026-09-12 | none | Preserve unknown |\n\n"
            "```\n| fake-row | 2026-01-01 | 2026-02-01 | none | Not metadata |\n```\n\n"
            "## Archived migrations\n\n"
            "| Slug | Started | Closed | Outcome |\n|---|---|---|---|\n"
            "| historic | 2026-01-01 | 2026-02-01 | Retained guide |\n", encoding="utf-8")
        (self.target / "tasks").mkdir()
        (self.target / "tasks/lessons.md").write_text("Legacy lessons.\n", encoding="utf-8")
        poison = self.target / "docs/migrations"
        poison.mkdir(parents=True)
        (poison / "_INDEX.md").write_text("Wrong repository catalog.\n", encoding="utf-8")
        before = hashes(self.base)
        result = self.result("migrations", "--today", "2026-09-20")
        self.assertEqual({row["slug"] for row in result["migrations"]},
                         {"v5-claude-home-layout", "unknown-detector"})
        self.assertTrue(all(row["schedule"] == "overdue" for row in result["migrations"]))
        by_slug = {row["slug"]: row for row in result["migrations"]}
        self.assertEqual(by_slug["v5-claude-home-layout"]["observation"], "needs_migration")
        self.assertEqual(by_slug["unknown-detector"]["observation"], "unknown")
        self.assertIn("historic", {row["slug"] for row in self.result(
            "migrations", "--today", "2026-09-20", "--all")["migrations"]})
        self.assertEqual(hashes(self.base), before)

    def test_missing_migration_catalog_is_unknown_not_no_pending_work(self):
        (self.source / "docs/migrations/_INDEX.md").unlink()
        before = hashes(self.base)
        result = self.run_helper("migrations", success=False)
        self.assertIn("MIGRATION_CATALOG_MISSING", result.stderr)
        self.assertEqual(result.stdout.strip(), "")
        self.assertEqual(hashes(self.base), before)

    def test_malformed_migration_metadata_is_not_silently_dropped(self):
        catalog = self.source / "docs/migrations/_INDEX.md"
        original = catalog.read_text(encoding="utf-8")
        catalog.write_text(original.replace("2026-09-12", "not-a-date"), encoding="utf-8")
        before = hashes(self.base)
        result = self.run_helper("migrations", success=False)
        self.assertEqual(result.stdout, "")
        self.assertEqual(hashes(self.base), before)
        catalog.write_text("# Missing active table\n", encoding="utf-8")
        result = self.run_helper("migrations", success=False)
        self.assertIn("MIGRATION_CATALOG_INVALID", result.stderr)

    def test_source_verifier_does_not_claim_hook_activation_from_links(self):
        hooks = self.home / "hooks/shared/synthetic"
        hooks.mkdir(parents=True)
        (hooks / "run.sh").write_bytes(b"echo inert fixture\n")
        host_hooks = Path(self.env["HOME"]) / ".claude/hooks"
        host_hooks.mkdir(parents=True)
        os.symlink(hooks / "run.sh", host_hooks / "synthetic.sh")
        result = subprocess.run([OPTIONS.bash, str(ROOT / "install/verify.sh"), "--hooks"],
                                cwd=self.target, env=self.env, text=True, encoding="utf-8",
                                capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("hooks activated", result.stdout)
        self.assertNotIn("Activated:", result.stdout)
        self.assertIn("unverified", result.stdout)

    def test_doctor_reports_bytes_not_hook_counts_or_historic_host_activity(self):
        source_hook = self.source / "hooks/shared/session-digest/run.sh"
        installed_hook = self.home / "hooks/shared/session-digest/run.sh"
        for path, content in ((source_hook, "echo current\n"), (installed_hook, "echo customized\n")):
            path.parent.mkdir(parents=True)
            path.write_text(content, encoding="utf-8")
        home = Path(self.env["HOME"])
        for version in ("0.8.0", "0.9.0"):
            manifest = home / f".claude/plugins/cache/vendor/li/{version}/.claude-plugin/plugin.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"name": "li", "version": version}), encoding="utf-8")
        audit = self.target / ".claude/runtime/audit/hooks.jsonl"
        audit.parent.mkdir(parents=True)
        audit.write_text('{"event":"session_digest","ts":"2000-01-01T00:00:00Z"}\n', encoding="utf-8")
        before = hashes(self.base)
        result = self.run_helper("doctor", "--json", success=False)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertIn("shared/session-digest/run.sh", report["hooks"]["modified"])
        self.assertEqual(report["host_activation"], "unverified")
        self.assertEqual(len(report["cached_plugins"]), 2)
        self.assertTrue(all(row["activation"] == "unverified" for row in report["cached_plugins"]))
        self.assertEqual(report["hook_execution"], "unverified")
        self.assertEqual(hashes(self.base), before)

    def test_shell_lifecycle_preserves_configured_paths_across_native_python_boundary(self):
        self.pack("alpha")
        self.pointer.write_text("alpha\n", encoding="utf-8")
        before = hashes(self.base)
        script = r'''
set -e
cd "$LIFECYCLE_TEST_BASE"
export LINTEL_SOURCE_ROOT="$PWD/trusted source"
export LINTEL_REPO_ROOT="$PWD/consumer"
export LINTEL_HOME="$PWD/installed data"
export LINTEL_PACKS_DIR="$PWD/configured packs"
export LINTEL_ACTIVE_PACK_FILE="$PWD/selection/active-pack"
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" pack-list
'''
        result = subprocess.run([OPTIONS.bash, "-c", script], cwd=self.target,
                                env=dict(self.env, LIFECYCLE_TEST_BASE=self.base.as_posix()),
                                text=True, encoding="utf-8", capture_output=True, timeout=45)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["effective_pack"], "alpha")
        self.assertEqual(hashes(self.base), before)


class MigrationInventory(LifecycleFixture):
    active_header = (
        "# Migrations\n\n## Active migrations\n\n"
        "| Slug | Started | Grace until | Removal at | Description |\n"
        "|---|---|---|---|---|\n"
    )
    valid_row = "| overdue-work | 2026-06-12 | 2026-09-12 | none | Pending consumer work |\n"
    archived_header = (
        "\n## Archived migrations\n\n"
        "| Slug | Started | Closed | Outcome |\n|---|---|---|---|\n"
    )

    def setUp(self):
        super().setUp()
        self.catalog = self.source / "docs/migrations/_INDEX.md"
        skill = self.source / "skills/migrations/SKILL.md"
        skill.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / "skills/migrations/SKILL.md", skill)
        for path in self.source.rglob("*"):
            if path.is_file():
                self.assertEqual(path.read_bytes(), (ROOT / path.relative_to(self.source)).read_bytes())
        blocks = skill.read_text(encoding="utf-8").split("```bash\n")
        self.assertEqual(len(blocks), 2)
        self.skill_block = blocks[1].split("```", 1)[0]
        self.caller = self.base / "unrelated caller"
        self.caller.mkdir()
        (self.caller / "unrelated.txt").write_bytes(b"Caller-owned content.\n")
        user = self.base / "fake user"
        user.mkdir()
        (user / "personal.txt").write_bytes(b"Synthetic personal content.\n")
        (self.home / "customization.txt").write_bytes(b"Installed user customization.\n")
        temp = self.base / "temp"
        temp.mkdir()
        for key in ("BASH_ENV", "ENV", "CDPATH", "HOMEDRIVE", "HOMEPATH"):
            self.env.pop(key, None)
        # Hosted Linux runners export XDG_RUNTIME_DIR and other XDG paths outside the fixture.
        for key in [key for key in self.env if key.startswith("XDG_")]:
            self.env.pop(key)
        self.env.update({
            "APPDATA": str(user / "AppData/Roaming"),
            "LOCALAPPDATA": str(user / "AppData/Local"),
            "XDG_CONFIG_HOME": str(user / ".config"),
            "XDG_CACHE_HOME": str(user / ".cache"),
            "XDG_DATA_HOME": str(user / ".local/share"),
            "XDG_STATE_HOME": str(user / ".local/state"),
            "TEMP": str(temp), "TMP": str(temp), "TMPDIR": str(temp),
            "LINTEL_PRIVATE_ROLES_DIR": str(self.home / "private/roles"),
            "LINTEL_RECOVERY_STORE": str(self.base / "recovery"),
            "LINTEL_AUDIT_DIR": str(self.target / ".claude/runtime/audit"),
            "LINTEL_JOBS_DIR": str(self.target / ".claude/runtime/jobs"),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(user / ".gitconfig"),
        })

    def run_inventory(self, *args):
        for key, value in self.env.items():
            if key.startswith(("LINTEL_", "XDG_")) or key in (
                "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "TMPDIR",
            ):
                self.assertIn(self.base.resolve(), Path(value).resolve().parents, key)
        for path in (self.home / "profile.yaml", self.home / "profile-context",
                     self.home / "jobs/_active.md", self.target / ".claude/runtime", self.caller):
            self.assertIn(self.base.resolve(), path.resolve().parents)
        before = hashes(self.base)
        modes = {path.relative_to(self.base).as_posix(): path.stat().st_mode
                 for path in self.base.rglob("*")}
        block = self.skill_block if not args else self.skill_block.rstrip() + ' "$@"\n'
        result = subprocess.run(
            [OPTIONS.bash, "--noprofile", "--norc", "-c",
             "set -euo pipefail\n" + block, "migrations-skill", *args],
            cwd=self.caller, env=self.env, capture_output=True, text=True, encoding="utf-8", timeout=45,
        )
        self.assertEqual(hashes(self.base), before, result.stdout + result.stderr)
        self.assertEqual({path.relative_to(self.base).as_posix(): path.stat().st_mode
                          for path in self.base.rglob("*")}, modes, result.stdout + result.stderr)
        return result

    def inventory(self, *args):
        result = self.run_inventory(*args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        value = json.loads(result.stdout)
        self.assertEqual(Path(value["catalog"]), self.catalog)
        self.assertEqual(Path(value["target"]), self.target)
        return value["migrations"]

    def assert_invalid_catalog(self, *args):
        result = self.run_inventory(*args)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("MIGRATION_CATALOG_INVALID", result.stderr)

    def test_exact_review_catalogs_through_real_skill(self):
        fixtures = (
            (self.active_header + self.valid_row, 192,
             "4ca4751d30a521d13c18f0608d255960563c28a0de770882e37dfccbb737b7b0"),
            (self.active_header + "| overdue-work | 2026-06-12 | 2026-09-12 |\n", 161,
             "35adc26d85f0221cfb57f7de68e9823d4fbc371ba6992fc6dfeb8144b4a431c7"),
        )
        for text, length, digest in fixtures:
            with self.subTest(catalog=digest):
                payload = text.encode("utf-8")
                self.assertEqual(len(payload), length)
                self.assertEqual(hashlib.sha256(payload).hexdigest(), digest)
                self.catalog.write_bytes(payload)
                if length == 192:
                    row, = self.inventory()
                    self.assertEqual(row["slug"], "overdue-work")
                    self.assertEqual(row["observation"], "unknown")
                    self.assertEqual(row["description"], "Pending consumer work")
                else:
                    self.assert_invalid_catalog()

    def test_active_rows_cannot_hide_as_short_or_ignorable_metadata(self):
        rows = (
            "| overdue-work |",
            "| overdue-work | 2026-06-12 | 2026-09-12 | none |",
            "| overdue-work | 2026-06-12 | 2026-09-12 | none ||",
            "| overdue-work | 2026-06-12 | 2026-09-12 | none | |",
            "| overdue-work | 2026-06-12 | 2026-09-12 | | Pending |",
            "| overdue-work | 2026-06-12 | | none | Pending |",
            "| overdue-work || 2026-09-12 | none | Pending |",
            "|| 2026-06-12 | 2026-09-12 | none | Pending |",
            "| | 2026-06-12 | 2026-09-12 | none | Pending |",
            "|",
            "| Slug | Started |",
            "| Slug | 2026-06-12 | 2026-09-12 | none | Pending |",
            "|---|---|---|",
            "|---|2026-06-12|2026-09-12|none|Pending|",
            "|:|:|:|:|:|",
            "| _none yet_ | 2026-06-12 | 2026-09-12 | none | Pending |",
        )
        for row in rows:
            with self.subTest(row=row):
                self.catalog.write_text(self.active_header + row + "\n", encoding="utf-8")
                self.assert_invalid_catalog()

    def test_malformed_archived_rows_fail_only_when_requested(self):
        rows = (
            "| historic | 2026-01-01 | 2026-02-01 |",
            "| historic | 2026-01-01 | 2026-02-01 ||",
            "| historic | 2026-01-01 | | Retained guide |",
            "|| 2026-01-01 | 2026-02-01 | Retained guide |",
            "| Slug | Started | Closed |",
            "|---|2026-01-01|2026-02-01|Retained guide|",
            "| _none yet_ | 2026-01-01 | 2026-02-01 | Retained guide |",
        )
        for row in rows:
            with self.subTest(row=row):
                self.catalog.write_text(
                    self.active_header + self.valid_row + self.archived_header + row + "\n", encoding="utf-8")
                self.assertEqual([item["slug"] for item in self.inventory()], ["overdue-work"])
                self.assert_invalid_catalog("--all")

    def test_valid_overdue_unknown_archive_pipes_and_literal_rows_are_preserved(self):
        self.catalog.write_text(
            self.active_header.replace("|---|---|---|---|---|", "|:---|---:|:---:|---|---|")
            + self.valid_row
            + "| v5-claude-home-layout | 2026-06-12 | 2026-09-12 | 2026-12-12 | Layout |\n"
            + "| future-work | 2026-06-12 | 2099-09-12 | none-removed | Keep open\n"
            + "| no-deadline | 2026-06-12 | none | none | Choice a | choice b |\n"
            + "\n```markdown\n## Archived migrations\n| bad-fenced-row |\n```\n\n"
            + "> | bad-quoted-row |\n\n"
            + self.archived_header.replace("|---|---|---|---|", "|:---|---:|:---:|---|")
            + "| historic | 2026-01-01 | 2026-02-01 | Outcome a | outcome b |\n",
            encoding="utf-8")
        (self.target / "tasks").mkdir()
        (self.target / "tasks/lessons.md").write_bytes(b"Legacy consumer lessons.\n")
        for location in (self.target, self.caller):
            poison = location / "docs/migrations/_INDEX.md"
            poison.parent.mkdir(parents=True)
            poison.write_bytes(b"Not the selected source catalog.\n")
        rows = {row["slug"]: row for row in self.inventory("--today", "2026-09-21")}
        self.assertEqual(set(rows), {"overdue-work", "v5-claude-home-layout", "future-work", "no-deadline"})
        self.assertEqual((rows["overdue-work"]["schedule"], rows["overdue-work"]["observation"]),
                         ("overdue", "unknown"))
        self.assertEqual(rows["v5-claude-home-layout"]["observation"], "needs_migration")
        self.assertEqual(rows["future-work"]["schedule"], "open")
        self.assertEqual(rows["no-deadline"]["schedule"], "open")
        self.assertEqual(rows["no-deadline"]["description"], "Choice a | choice b")
        archived = {row["slug"]: row for row in self.inventory("--today", "2026-09-21", "--all")}
        self.assertEqual(set(archived), set(rows) | {"historic"})
        self.assertEqual(archived["historic"]["schedule"], "archived")
        self.assertEqual(archived["historic"]["observation"], "unknown")
        self.assertIsNone(archived["historic"]["grace_until"])
        self.assertEqual(archived["historic"]["description"], "Outcome a | outcome b")

    def test_complete_headers_separators_and_placeholders_remain_empty(self):
        self.catalog.write_text(
            self.active_header + "| _none yet_ | \u2014 | \u2014 | \u2014 | \u2014 |\n"
            + self.archived_header + "| _none yet_ | \u2014 | \u2014 | \u2014 |\n", encoding="utf-8")
        self.assertEqual(self.inventory(), [])
        self.assertEqual(self.inventory("--all"), [])

    def test_missing_catalog_active_section_and_date_errors_remain_explicit(self):
        self.catalog.unlink()
        result = self.run_inventory()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("MIGRATION_CATALOG_MISSING", result.stderr)
        self.catalog.write_text("# Missing active table\n", encoding="utf-8")
        self.assert_invalid_catalog()
        for started, deadline in (("not-a-date", "2026-09-12"), ("2026-06-12", "2026-02-30")):
            for archived in (False, True):
                with self.subTest(started=started, deadline=deadline, archived=archived):
                    text = self.active_header
                    if archived:
                        text += self.valid_row + self.archived_header
                    text += f"| invalid-date | {started} | {deadline} | "
                    text += "Retained guide |\n" if archived else "none | Pending work |\n"
                    self.catalog.write_text(text, encoding="utf-8")
                    result = self.run_inventory("--all")
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("li-lifecycle:", result.stderr)

    def test_current_source_catalog_remains_readable(self):
        rows = self.inventory("--today", "2026-09-21")
        self.assertIn("v5-claude-home-layout", {row["slug"] for row in rows})
        self.assertEqual(self.inventory("--today", "2026-09-21", "--all"), rows)

    def _layout_targets(self, label="layout-observation"):
        prefix = label + "-"
        padding = 147 - len(str(self.base)) - 1 - len(prefix)
        self.assertGreaterEqual(padding, 0, "Keep the declared fixture depth; do not shorten an existing root.")
        parent = self.base / (prefix + "x" * padding)
        parent.mkdir()
        targets = (parent / "short", parent / ("long-" + "x" * 103))
        for target, length in zip(targets, (153, 256)):
            native_io_path(target).mkdir()
            self.assertEqual(len(str(target)), length)
            self.assertFalse(native_io_path(target / ".git").exists())
        return targets

    def _layout_seed(self, target, relative, data):
        path = native_io_path(target / relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def _layout_state(self):
        import stat

        base = native_io_path(self.base)
        result = {}
        for path in (base, *base.rglob("*")):
            info = path.lstat()
            result[path.relative_to(base).as_posix()] = {
                "mode": info.st_mode, "attributes": getattr(info, "st_file_attributes", 0),
                "size": info.st_size if stat.S_ISREG(info.st_mode) else None,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if stat.S_ISREG(info.st_mode) else None,
                "link": os.readlink(path) if path.is_symlink() else None,
            }
        return result

    def _layout_inventory(self, target, *, error=False, locked=None, migration=False):
        home = target / ".claude/runtime/lintel-home"
        jobs = target / ".claude/runtime/jobs"
        env = dict(self.env, LINTEL_REPO_ROOT=str(target), LINTEL_HOME=str(home),
                   LINTEL_PACKS_DIR=str(home / "packs"), LINTEL_ACTIVE_PACK_FILE=str(home / "packs/active-pack"),
                   LINTEL_AUDIT_DIR=str(target / ".claude/runtime/audit"),
                   LINTEL_JOBS_DIR=str(jobs), LINTEL_JOBS_ACTIVE=str(jobs / "_active.md"),
                   LINTEL_JOBS_ARCHIVE=str(jobs / "_archive"),
                   LINTEL_JOBS_REGISTRY=str(home / "jobs/_active.md"),
                   LINTEL_PRIVATE_ROLES_DIR=str(home / "private/roles"),
                   CLAUDE_CONFIG_DIR=str(Path(self.env["HOME"]) / ".claude"),
                   COPILOT_HOME=str(Path(self.env["HOME"]) / ".copilot"),
                   PACK_CACHE_FILE=str(home / "profile-cache.json"), LINTEL_JOBS_NO_INIT="1")
        env.pop("LINTEL_RECOVERY_STORE", None)
        for key, value in env.items():
            if ((key.startswith(("LINTEL_", "XDG_")) and key != "LINTEL_JOBS_NO_INIT") or key in
                    ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "TMPDIR",
                     "CLAUDE_CONFIG_DIR", "COPILOT_HOME",
                     "PACK_CACHE_FILE", "GIT_CONFIG_GLOBAL")):
                self.assertTrue(Path(value).is_relative_to(self.base), (key, value))
        for path in (home / "profile.yaml", home / "sessions/profiles", home / "audit",
                     target / ".claude/runtime", target / ".claude/runtime/profiles", self.caller):
            self.assertTrue(path.is_relative_to(self.base), path)
        self.assertEqual(env["HOME"], env["USERPROFILE"])
        self.assertFalse(native_io_path(target / ".git").exists())
        before = self._layout_state()
        handle = None
        if locked:
            import ctypes
            from ctypes import wintypes

            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            create = kernel.CreateFileW
            create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                               wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
            create.restype = wintypes.HANDLE
            kernel.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel.CloseHandle.restype = wintypes.BOOL
            handle = create(str(native_io_path(target / locked)), 0x80000000, 0, None, 3, 0x80, None)
            self.assertNotEqual(handle, wintypes.HANDLE(-1).value, ctypes.get_last_error())
        try:
            block = ('bash "$LINTEL_SOURCE_ROOT/bin/li-migrate-claude-home" '
                     '--dry-run --repo "$LINTEL_REPO_ROOT"\n') if migration else self.skill_block
            result = subprocess.run(
                [OPTIONS.bash, "--noprofile", "--norc", "-c", "set -euo pipefail\n" + block],
                cwd=self.caller, env=env, capture_output=True, text=True, encoding="utf-8", timeout=45)
        finally:
            if handle is not None:
                self.assertTrue(kernel.CloseHandle(handle))
        after = self._layout_state()
        print(json.dumps({
            "case": self._testMethodName, "target": str(target), "locked": locked, "migration": migration,
            "lengths": [len(str(target)), len(str(target / ".claude/lintel-layout.yaml")),
                        len(str(target / "tasks/lessons.md"))],
            "argv": result.args, "environment": env, "exit": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr, "before": before, "after": after,
        }, sort_keys=True))
        self.assertEqual(after, before, "Migration observation must not mutate source, caller, home or target.")
        self.assertNotIn("Traceback", result.stderr)
        if error:
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertIn("li-lifecycle:", result.stderr)
            return result
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        value = json.loads(result.stdout)
        if migration:
            self.assertEqual(value["state"], "preview")
            self.assertEqual(Path(value["target"]), target)
            self.assertIsNone(value["target_profile_reference"])
            return value
        self.assertEqual(Path(value["target"]), target)
        self.assertEqual(Path(value["catalog"]), self.catalog)
        row, = [entry for entry in value["migrations"] if entry["slug"] == "v5-claude-home-layout"]
        self.assertEqual(row["schedule"], "overdue")
        self.assertTrue(all(entry["observation"] == "unknown" for entry in value["migrations"]
                            if entry["slug"] != row["slug"]))
        self.assertEqual(set(row), {"slug", "started", "grace_until", "schedule", "observation",
                                   "description", "layout_version", "legacy", "stubs"})
        return {key: row[key] for key in ("observation", "layout_version", "legacy", "stubs")}

    def test_layout_observation_real_skill_matches_short_and_long_review_fixture(self):
        seeds = {
            ".claude/lintel-layout.yaml": (
                b"# Consumer marker; legacy content still exists.\nlayout_version: 5\n", 66,
                "b6ff0ad8776fa67e263c5c694a9f44c3f41f1a62399863862fa20c4c117e99ee"),
            "tasks/lessons.md": (
                b"# Consumer lessons\r\nUnmigrated knowledge must remain visible.\r\n", 63,
                "34c67a8e8ed5b15d967750f15c1b5a628bd0f714501a1ce85b1f1144f0dad7c3"),
        }
        for target in self._layout_targets():
            for relative, (data, size, digest) in seeds.items():
                self.assertEqual((len(data), hashlib.sha256(data).hexdigest()), (size, digest))
                self._layout_seed(target, relative, data)
            with self.subTest(length=len(str(target))):
                self.assertEqual(self._layout_inventory(target), {
                    "observation": "incomplete", "layout_version": 5,
                    "legacy": ["tasks/lessons.md"], "stubs": [],
                })

    def test_layout_observation_distinguishes_absent_current_and_unmigrated_targets(self):
        for target in self._layout_targets():
            stages = (
                (None, None, "not_applicable", None, []),
                (None, b"Legacy consumer lessons.\r\n", "needs_migration", None, ["tasks/lessons.md"]),
                (b"layout_version: 4\n", b"Legacy consumer lessons.\r\n", "needs_migration", 4, ["tasks/lessons.md"]),
                (b"layout_version: 5\n", b"Legacy consumer lessons.\r\n", "incomplete", 5, ["tasks/lessons.md"]),
                (b"layout_version: 5\n# Consumer comment.\n", None, "current", 5, []),
                (b"layout_version: 6\n", None, "current", 6, []),
                (None, None, "not_applicable", None, []),
            )
            for marker, lessons, observation, version, legacy in stages:
                for relative, data in ((".claude/lintel-layout.yaml", marker), ("tasks/lessons.md", lessons)):
                    path = native_io_path(target / relative)
                    if data is not None:
                        self._layout_seed(target, relative, data)
                    elif path.exists():
                        path.unlink()
                with self.subTest(length=len(str(target)), observation=observation, version=version):
                    self.assertEqual(self._layout_inventory(target), {
                        "observation": observation, "layout_version": version, "legacy": legacy, "stubs": [],
                    })

    def test_layout_observation_retains_nested_hidden_legacy_and_redirects(self):
        for target in self._layout_targets():
            seeds = {
                ".claude/lintel-layout.yaml": b"layout_version: 5\n",
                "tasks/lessons.md": b"> Moved to .claude/memory/lessons.md (retained history).\n",
                ".claude/memory/lessons.md": b"Retained migrated lessons.\n",
                "docs/adr/README.md": b"> Moved to .claude/decisions/ (retained history).\n",
                "docs/adr/nested/kept.md": b"> Moved to .claude/decisions/nested/kept.md (retained history).\n",
                ".claude/decisions/nested/kept.md": b"# Retained migrated decision\n",
                "docs/adr/nested/unresolved.md": b"> Moved to .claude/decisions/nested/unresolved.md (missing).\n",
                "docs/adr/nested/.hidden.md": b"# Hidden unmigrated decision\r\n",
                ".lintel/state/nested/.hidden.json": b'{"unmigrated":true}\r\n',
                ".lintel/state/visible.txt": b"Legacy state.\n",
            }
            for relative, data in seeds.items():
                self._layout_seed(target, relative, data)
            with self.subTest(length=len(str(target))):
                row = self._layout_inventory(target)
                self.assertEqual((row["observation"], row["layout_version"]), ("incomplete", 5))
                self.assertEqual(row["legacy"], [".lintel/state/nested/.hidden.json", ".lintel/state/visible.txt",
                                                 "docs/adr/nested/.hidden.md", "docs/adr/nested/unresolved.md"])
                self.assertEqual(sorted(row["stubs"]), ["docs/adr/README.md", "docs/adr/nested/kept.md",
                                                       "tasks/lessons.md"])

    def test_layout_observation_refuses_malformed_nonfile_and_unreadable_inputs(self):
        for target in self._layout_targets():
            for malformed in (b"layout_version: invalid\n", b"layout_version: 5\nlayout_version: 5\n", b"\xff"):
                self._layout_seed(target, ".claude/lintel-layout.yaml", malformed)
                with self.subTest(length=len(str(target)), marker=malformed):
                    self._layout_inventory(target, error=True)
            marker = native_io_path(target / ".claude/lintel-layout.yaml")
            marker.unlink()
            for relative in (".claude/lintel-layout.yaml", "tasks/lessons.md"):
                path = native_io_path(target / relative)
                path.mkdir(parents=True)
                with self.subTest(length=len(str(target)), directory=relative):
                    self._layout_inventory(target, error=True)
                path.rmdir()
            self._layout_seed(target, "docs/adr", b"A file cannot stand in for the legacy decision directory.\n")
            with self.subTest(length=len(str(target)), invalid_directory="docs/adr"):
                self._layout_inventory(target, error=True)
            native_io_path(target / "docs/adr").unlink()
            if os.name == "nt":
                self._layout_seed(target, ".claude/lintel-layout.yaml", b"layout_version: 5\n")
                with self.subTest(length=len(str(target)), exclusive_read_lock=True):
                    self._layout_inventory(target, error=True, locked=".claude/lintel-layout.yaml")

    def _redirect_sources(self):
        relative = "bin/li-migrate-claude-home"
        shutil.copyfile(ROOT / relative, self.source / relative)
        self.assertEqual((self.source / relative).read_bytes(), (ROOT / relative).read_bytes())

    def _canonical_redirects(self):
        return (
            ("tasks/lessons.md", ".claude/memory/lessons.md", "file"),
            ("tasks/memory.md", ".claude/memory/working-state.md", "file"),
            ("tasks/personas.md", ".claude/memory/personas.md", "file"),
            ("tasks/todo.md", ".claude/plans/todo.md", "file"),
            ("docs/adr/README.md", ".claude/decisions/", "directory"),
            ("docs/adr/README.md", ".claude/decisions/README.md", "file"),
            ("docs/adr/0042-example.md", ".claude/decisions/0042-example.md", "file"),
            ("docs/adr/nested/.hidden.md", ".claude/decisions/nested/.hidden.md", "file"),
        )

    def _redirect_seed(self, target, old, new, *, marker=True):
        if marker:
            self._layout_seed(target, ".claude/lintel-layout.yaml", b"layout_version: 5\n")
        redirect = (
            f"> Moved to {new} (v5 .claude/ home layout, ADR-0005). Retained for explicit historical recovery.\n"
        ).encode("utf-8")
        self._layout_seed(target, old, redirect)
        return redirect

    def test_canonical_redirect_real_three_call_review_contrast(self):
        self._redirect_sources()
        valid = self._layout_targets("redirect-retained")[0]
        stranded = self._layout_targets("redirect-stranded")[0]
        for target in (valid, stranded):
            redirect = self._redirect_seed(target, "tasks/lessons.md", ".claude/memory/lessons.md")
            self.assertEqual((len(redirect), hashlib.sha256(redirect).hexdigest()),
                             (117, "819912e23957536ae225c7d220728c2564cde1af9f50b0398309dfc1ad6b0332"))
            marker = native_io_path(target / ".claude/lintel-layout.yaml").read_bytes()
            self.assertEqual((len(marker), hashlib.sha256(marker).hexdigest()),
                             (18, "a8e022980d1bc17474f4199f6a22fd6d8eba27f145375854a5e4b65cb19f92eb"))
        self._layout_seed(valid, ".claude/memory/lessons.md", b"Retained migrated consumer lessons.\r\n")
        self.assertFalse(native_io_path(stranded / ".claude/memory/lessons.md").exists())
        good = self._layout_inventory(valid)
        missing = self._layout_inventory(stranded)
        refused = self._layout_inventory(stranded, migration=True, error=True)
        self.assertIn("Stranded redirect without its destination: tasks/lessons.md", refused.stderr)
        self.assertEqual(good, {"observation": "current", "layout_version": 5,
                                "legacy": [], "stubs": ["tasks/lessons.md"]})
        self.assertEqual(missing, {"observation": "incomplete", "layout_version": 5,
                                   "legacy": ["tasks/lessons.md"], "stubs": []})

    def test_canonical_redirect_matrix_agrees_with_owned_migration_preview(self):
        self._redirect_sources()
        for number, (old, new, kind) in enumerate(self._canonical_redirects()):
            for condition in ("valid", "missing", "unmarked", "wrongkind"):
                targets = self._layout_targets(f"redirect-{number}-{condition}")
                for target in targets:
                    with self.subTest(mapping=(old, new), kind=kind, condition=condition, length=len(str(target))):
                        self._redirect_seed(target, old, new, marker=condition != "unmarked")
                        destination = native_io_path(target / new.rstrip("/"))
                        if condition == "valid":
                            if kind == "directory":
                                destination.mkdir(parents=True)
                            else:
                                self._layout_seed(target, new, b"Retained migrated bytes.\r\n")
                        elif condition == "wrongkind":
                            if kind == "directory":
                                self._layout_seed(target, new.rstrip("/"), b"Not a directory.\n")
                            else:
                                destination.mkdir(parents=True)
                        if condition == "wrongkind":
                            self._layout_inventory(target, error=True)
                            self._layout_inventory(target, migration=True, error=True)
                            continue
                        observed = self._layout_inventory(target)
                        preview = self._layout_inventory(target, migration=True, error=condition != "valid")
                        if condition == "valid":
                            self.assertEqual(observed, {"observation": "current", "layout_version": 5,
                                                        "legacy": [], "stubs": [old]})
                            self.assertNotIn(old, preview["changes"])
                            self.assertNotIn(new.rstrip("/"), preview["changes"])
                        else:
                            self.assertEqual(observed, {
                                "observation": "needs_migration" if condition == "unmarked" else "incomplete",
                                "layout_version": None if condition == "unmarked" else 5,
                                "legacy": [old], "stubs": [],
                            })
                            self.assertIn("Stranded", preview.stderr)

    def test_canonical_redirect_near_matches_remain_ordinary_legacy(self):
        self._redirect_sources()
        for number, (old, new, _) in enumerate(self._canonical_redirects()):
            for target in self._layout_targets(f"redirect-decoy-{number}"):
                with self.subTest(mapping=(old, new), length=len(str(target))):
                    self._redirect_seed(target, old, new)
                    self._layout_seed(target, old, f"> Moved to {new}-unrelated (consumer prose).\n".encode())
                    observed = self._layout_inventory(target)
                    preview = self._layout_inventory(target, migration=True)
                    self.assertEqual(observed, {"observation": "incomplete", "layout_version": 5,
                                                "legacy": [old], "stubs": []})
                    self.assertEqual(preview["changes"][old], "replace")

    def test_canonical_redirect_linked_and_unreadable_destinations_refuse(self):
        self._redirect_sources()
        outside = self.base / "redirect-destination-controls"
        outside.mkdir()
        (outside / "file.txt").write_bytes(b"Fixture-owned linked destination.\r\n")
        (outside / "directory").mkdir()
        for number, (old, new, kind) in enumerate(self._canonical_redirects()):
            for target in self._layout_targets(f"redirect-link-{number}"):
                with self.subTest(mapping=(old, new), length=len(str(target)), linked=True):
                    self._redirect_seed(target, old, new)
                    destination = native_io_path(target / new.rstrip("/"))
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    linked = outside / ("directory" if kind == "directory" else "file.txt")
                    os.symlink(str(linked), str(destination), target_is_directory=kind == "directory")
                    self._layout_inventory(target, error=True)
                    self._layout_inventory(target, migration=True, error=True)
        if os.name == "nt":
            for number, (old, new, kind) in enumerate(self._canonical_redirects()):
                if kind == "directory":
                    continue
                for target in self._layout_targets(f"redirect-lock-{number}"):
                    with self.subTest(mapping=(old, new), length=len(str(target)), locked=True):
                        self._redirect_seed(target, old, new)
                        self._layout_seed(target, new, b"Existing but unreadable migrated content.\n")
                        for migration in (False, True):
                            result = self._layout_inventory(target, locked=new, error=True, migration=migration)
                            self.assertIn("Permission denied", result.stderr)


NATIVE_COMPONENTS = ("install", "bin", "lib", "templates", "scaffolding", "skills", "agents",
                     "shims", "docs", "hooks", "seeds", "packs/_default", ".claude-plugin")


def native_source(source, *, small):
    """Build the full-source or the small synthetic native fixture at `source`."""
    source.mkdir()
    if small:
        for relative in NATIVE_COMPONENTS:
            (source / relative).mkdir(parents=True, exist_ok=True)
        for relative in ("install/install.sh", "install/native.sh", "install/install.ps1",
                         "install/native.ps1", "install/layer-config.yaml.example",
                         "install/directories.txt",
                         "lib/frontmatter.sh", "lib/paths.sh", "packs/_default/pack.yaml",
                         ".claude-plugin/plugin.json"):
            shutil.copyfile(ROOT / relative, source / relative)
        sample = source / "skills/sample/SKILL.md"
        sample.parent.mkdir()
        sample.write_text("---\nname: sample\ndescription: Synthetic fixture\ncolor: green\n"
                          "tools: Read\nvoice: internal\nlayer: foundation\ncli_support: [claude-code]\n"
                          "---\nSynthetic native byte contract.\n", encoding="utf-8")
    else:
        for relative in NATIVE_COMPONENTS:
            shutil.copytree(ROOT / relative, source / relative,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for relative in ("LICENSE", "AGENT-INSTRUCTIONS.md", "README.md", "SECURITY.md",
                     "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "CHANGELOG.md", "config/aliases.yaml"):
        (source / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, source / relative)


class NativeInstallLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lintel-native-lifecycle-")
        register_temporary_cleanup(self, self.tmp, "lintel-native-lifecycle-")
        self.base = Path(self.tmp.name)
        self.source = self.base / "trusted source"
        self.home = self.base / "installed data"
        self.consumer = self.base / "consumer"
        native_source(self.source, small=OPTIONS.native_small)
        self.consumer.mkdir()
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("LINTEL_", "CLAUDE_")) and key != "PACK_CACHE_FILE"}
        self.env.update({"HOME": str(self.base / "fake user"), "USERPROFILE": str(self.base / "fake user"),
                         "LINTEL_HOME": str(self.home), "PYTHONDONTWRITEBYTECODE": "1",
                         "GIT_CONFIG_GLOBAL": str(self.base / "git-config"), "GIT_CONFIG_NOSYSTEM": "1"})
        if os.environ.get("LINTEL_POWERSHELL"):
            self.env["LINTEL_POWERSHELL"] = os.environ["LINTEL_POWERSHELL"]
        for repo in (self.source, self.consumer):
            result = subprocess.run(["git", "init", "-q", str(repo)], env=self.env, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def install(self, *args, powershell=False, success=True, env=None, bash=False, source=None):
        source = source or self.source
        if powershell:
            executable = self.env.get("LINTEL_POWERSHELL") or shutil.which("pwsh") or shutil.which("powershell")
            self.assertIsNotNone(executable, "Native PowerShell verification needs an installed interpreter.")
            command = [executable, "-NoProfile", "-File", str(source / "install/install.ps1")]
        else:
            if bash or OPTIONS.native_performer == "bash":
                command = [OPTIONS.bash, "-c", 'set -euo pipefail; source "$1"; shift; lintel_native_main "$@"',
                           "native-contract-test", str(source / "install/native.sh")]
            else:
                command = [OPTIONS.bash, str(source / "install/install.sh")]
        result = subprocess.run([*command, *args], cwd=self.consumer, env=env or self.env, text=True, encoding="utf-8",
                                errors="replace", capture_output=True, timeout=600)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, "Installer accepted a conflicting candidate.")
            self.assertNotIn("Install complete", result.stdout)
        return result

    def customize(self):
        files = {
            "profile.yaml": "# operator preference\nrole_active: custom\n",
            "config.yaml": "# operator configuration\nlayers: custom\n",
            "hooks/shared/operator-extra/run.sh": "echo inert custom hook\n",
            "lib/operator-extension.sh": "echo custom extension\n",
            "roles/private/operator.md": "private synthetic sentinel\n",
        }
        for relative, text in files.items():
            path = self.home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        neutral = self.home / "packs/_default/pack.yaml"
        neutral.write_text(neutral.read_text(encoding="utf-8") + "# operator neutral customization\n",
                           encoding="utf-8")
        return {relative: hashlib.sha256((self.home / relative).read_bytes()).hexdigest()
                for relative in (*files, "packs/_default/pack.yaml")}

    def test_bash_reinstall_preserves_seeds_and_rejects_managed_conflicts(self):
        self.install()
        custom = self.customize()
        self.install()
        for relative, digest in custom.items():
            self.assertEqual(hashlib.sha256((self.home / relative).read_bytes()).hexdigest(), digest)
        managed = self.home / "lib/paths.sh"
        managed.write_bytes(managed.read_bytes() + b"\n# local managed-file customization\n")
        before = hashes(self.home)
        self.install(success=False)
        self.assertEqual(hashes(self.home), before)

    def test_invalid_candidate_is_rejected_before_existing_install_changes(self):
        self.install()
        self.customize()
        before = hashes(self.home)
        candidate = self.source / ("skills/sample/SKILL.md" if OPTIONS.native_small else "skills/pack-list/SKILL.md")
        candidate.write_text("---\nname: invalid-only\n---\nBroken candidate.\n", encoding="utf-8")
        self.install(success=False)
        self.assertEqual(hashes(self.home), before)

    def test_bash_update_removes_only_owned_obsolete_files(self):
        obsolete = self.source / "lib/lifecycle-obsolete.sh"
        obsolete.write_text("echo old managed content\n", encoding="utf-8")
        self.install()
        custom = self.customize()
        obsolete.unlink()
        self.install()
        self.assertFalse((self.home / "lib/lifecycle-obsolete.sh").exists())
        for relative, digest in custom.items():
            self.assertEqual(hashlib.sha256((self.home / relative).read_bytes()).hexdigest(), digest)

    def test_runtime_and_brand_directory_slots_are_retained_without_clobbering(self):
        font = self.home / "brand/fonts/operator.font"
        font.parent.mkdir(parents=True)
        font.write_bytes(b"operator asset")
        self.install()
        for relative in ("audit", "sessions", "provenance", "freeze", "review-log", "benchmarks",
                         "calibrations", "browse-runs", "scrape-runs", "design-runs", "design-html",
                         "design-shotgun", "browser-profiles", "quarantine", "frontend-runs",
                         "brand/design-patterns", "brand/motion-libraries", "brand/shader-snippets",
                         "brand/palettes", "brand/fonts"):
            self.assertTrue((self.home / relative).is_dir(), relative)
        self.assertEqual(font.read_bytes(), b"operator asset")

    def test_powershell_reinstall_keeps_operator_files_inside_managed_trees(self):
        self.install(powershell=True)
        custom = self.customize()
        self.install(powershell=True)
        for relative, digest in custom.items():
            self.assertTrue((self.home / relative).is_file(), relative)
            self.assertEqual(hashlib.sha256((self.home / relative).read_bytes()).hexdigest(), digest)

    def interruption_recovery(self, powershell):
        self.home.mkdir()
        (self.home / "operator.txt").write_bytes(b"untouched operator state\n")
        before = hashes(self.home)
        windows_performer = powershell or (os.name == "nt" and OPTIONS.native_performer == "auto")
        wrapper = self.source / ("install/install.ps1" if windows_performer else "install/native.sh")
        original = wrapper.read_text(encoding="utf-8")
        fault = r'''
    $script:OriginalNativeWrite = ${function:Write-NativeAtomic}
    $script:NativeFaultCount = 0
    function Write-NativeAtomic([string]$Root, [string]$Relative, $Expected, $After) {
        & $script:OriginalNativeWrite $Root $Relative $Expected $After
        $script:NativeFaultCount++
        if ($script:NativeFaultCount -eq 1) { throw [IO.IOException]::new('synthetic interrupted publication') }
    }
'''
        if windows_performer:
            injected = original.replace("    Invoke-NativeInstall", fault + "\n    Invoke-NativeInstall")
        else:
            injected = original.replace("native_atomic() {", "native_original_atomic() {") + '''
native_atomic() {
  native_original_atomic "$@"
  native_die 'synthetic interrupted publication'
}
'''
        wrapper.write_text(injected, encoding="utf-8")
        interrupted = self.install(powershell=powershell, success=False)
        self.assertIn("synthetic interrupted publication", interrupted.stderr)
        wrapper.write_text(original, encoding="utf-8")
        store = Path(str(self.home) + "-recovery")
        receipts = list(store.glob("txn-*"))
        self.assertEqual(len(receipts), 1)
        receipt = receipts[0]
        self.assertEqual((receipt / "state").read_text(encoding="utf-8").strip(), "applying")
        self.assertFalse((self.home / ".lintel-install.tsv").exists())
        partial = hashes(self.home)
        refused = self.install(powershell=powershell, success=False)
        self.assertIn("ncomplete", refused.stderr)
        self.assertEqual(hashes(self.home), partial)
        row = (receipt / "plan.tsv").read_text(encoding="utf-8").splitlines()[0].split("\t")
        output = self.home / row[7]
        output.write_bytes(b"user change after interruption")
        edited = hashes(self.home)
        self.install("--recover", receipt.name, powershell=powershell, success=False)
        self.assertEqual(hashes(self.home), edited)
        output.write_bytes((receipt / "after" / row[0]).read_bytes())
        self.install("--recover", receipt.name, powershell=powershell)
        self.assertEqual(hashes(self.home), before)
        self.assertEqual((receipt / "state").read_text(encoding="utf-8").strip(), "recovered")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes((receipt / "after" / row[0]).read_bytes())
        replay = hashes(self.home)
        self.install("--recover", receipt.name, powershell=powershell, success=False)
        self.assertEqual(hashes(self.home), replay, "recovery reused consumed permission over a later user file")

    def test_bash_entry_interruption_recovery_and_consumed_permission(self):
        self.interruption_recovery(False)

    def test_powershell_entry_interruption_recovery_and_consumed_permission(self):
        self.interruption_recovery(True)

    def test_native_install_has_no_python_on_its_path(self):
        if os.name == "nt":
            powershell = self.env.get("LINTEL_POWERSHELL") or shutil.which("powershell") or shutil.which("pwsh")
            self.assertTrue(powershell, "An authorized native PowerShell executable is required.")
            bash_directory = Path(OPTIONS.bash).resolve().parent
            git = shutil.which("git")
            self.assertIsNotNone(git)
            directories = [Path(git).resolve().parent, bash_directory,
                           bash_directory.parent / "usr/bin", Path(powershell).parent,
                           Path(os.environ["SystemRoot"]) / "System32"]
            path = os.pathsep.join(str(directory) for directory in directories if directory.is_dir())
            probe_command = [powershell, "-NoProfile", "-Command",
                             "if (Get-Command python,python3,py -ErrorAction SilentlyContinue) { exit 19 }; exit 0"]
        else:
            tools = self.base / "native-tools"
            tools.mkdir()
            for name in ("bash", "git", "awk", "cat", "cp", "mv", "rm", "rmdir", "mkdir", "chmod", "cmp", "find",
                         "sort", "grep", "head", "tail", "cut", "wc", "tr", "stat", "date", "dirname",
                         "basename", "mktemp", "sha256sum", "shasum", "openssl"):
                executable = shutil.which(name)
                if executable:
                    os.symlink(executable, tools / name)
            path = str(tools)
            probe_command = [OPTIONS.bash, "-c",
                             'for name in python python3 py; do if command -v "$name"; then exit 19; fi; done']
        env = dict(self.env, PATH=path, BASH_ENV="", ENV="")
        probe = subprocess.run(probe_command, cwd=self.consumer, env=env, capture_output=True)
        self.assertEqual(probe.returncode, 0, "Python is still discoverable in the native fixture.")
        self.install(env=env)
        self.install("--check", powershell=os.name == "nt", env=env)
        if not OPTIONS.native_small:
            self.assertTrue((self.home / "lib/profile_context.py").is_file())
        self.assertFalse((self.home / "lib/__pycache__").exists())

    def test_corrupt_and_foreign_native_receipts_preserve_current_bytes(self):
        native_windows = os.name == "nt"
        self.install(powershell=native_windows)
        store = Path(str(self.home) + "-recovery")
        receipt = next(store.glob("txn-*"))
        before = hashes(self.home)
        original = (receipt / "plan.tsv").read_bytes()
        (receipt / "plan.tsv").write_bytes(original + b"corrupt row\n")
        self.install("--recover", receipt.name, powershell=native_windows, success=False)
        self.assertEqual(hashes(self.home), before)
        (receipt / "plan.tsv").write_bytes(original)
        state = (receipt / "state").read_bytes()
        (receipt / "state").write_bytes(b"unknown-state\n")
        self.install("--recover", receipt.name, powershell=native_windows, success=False)
        self.assertEqual(hashes(self.home), before)
        (receipt / "state").write_bytes(state)
        other = self.base / "different install"
        other.mkdir()
        (other / "user.txt").write_bytes(b"foreign root sentinel")
        foreign = hashes(other)
        self.install("--home", str(other), "--store", str(store), "--recover", receipt.name,
                     powershell=native_windows, success=False)
        self.assertEqual(hashes(other), foreign)
        self.assertEqual(hashes(self.home), before)

    def test_closed_native_receipt_requires_matching_per_file_evidence(self):
        self.install()
        store = Path(str(self.home) + "-recovery")
        receipt = next(store.glob("txn-*"))
        (receipt / "phase/000000").write_bytes(b"pending\n")
        before = hashes(self.home)
        self.install("--check", success=False)
        self.install(success=False)
        self.assertEqual(hashes(self.home), before)

    def performers(self):
        # F-INT-4: a full-source install through the Bash performer spawns processes per
        # file and exceeds this test's own timeout on Windows, where it is not the default
        # performer. There its variants run the small fixture, labelled; PowerShell keeps
        # the setUp source, and other platforms keep the full source for both.
        for label, powershell in (("bash", False), ("powershell", True)):
            home, store = self.base / f"h-{label}", self.base / f"h-{label}-recovery"
            source, fixture = self.source, "small" if OPTIONS.native_small else "full"
            if label == "bash" and os.name == "nt" and fixture == "full":
                source, fixture = self.base / "bash small source", "small"
                if not source.exists():
                    native_source(source, small=True)
                    result = subprocess.run(["git", "init", "-q", str(source)], env=self.env, capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
            print("NATIVE_FIXTURE " + json.dumps({"test": self._testMethodName, "performer": label,
                                                  "fixture": fixture, "platform": os.name}, sort_keys=True))
            yield label, powershell, home, store, ("--home", str(home), "--store", str(store)), source

    def test_native_inventory_refuses_every_malformed_record(self):
        for label, powershell, home, store, roots, source in self.performers():
            self.install(*roots, powershell=powershell, bash=not powershell, source=source)
            inventory = home / ".lintel-install.tsv"
            original = inventory.read_bytes()
            header, rest = original.split(b"\n", 1)
            variants = {
                "trailing-duplicate-header": (original + header + b"\n", "Malformed native install inventory"),
                "interior-duplicate-header": (header + b"\n" + header + b"\n" + rest,
                                              "Malformed native install inventory"),
                "unterminated-malformed-final": (original + b"malformed final record",
                                                 "Malformed native install inventory"),
                "unterminated-foreign-final": (original + b"a" * 64 + b"\t1\tprivate/operator.md",
                                               "Inventory path outside managed namespaces"),
            }
            for variant, (data, message) in variants.items():
                with self.subTest(performer=label, variant=variant):
                    inventory.write_bytes(data)
                    before, receipts = hashes(home), hashes(store)
                    for command in ((), ("--check",)):
                        result = self.install(*roots, *command, powershell=powershell, bash=not powershell,
                                              success=False, source=source)
                        print("F06_CASE " + json.dumps({"performer": label, "variant": variant,
                                                        "command": command[0] if command else "install",
                                                        "exit": result.returncode,
                                                        "refusal": message in result.stderr}, sort_keys=True))
                        self.assertIn(message, result.stderr)
                        self.assertNotIn("Installed managed bytes verified", result.stdout)
                        self.assertEqual(hashes(home), before)
                        self.assertEqual(hashes(store), receipts)
            inventory.write_bytes(original)
            verified = self.install(*roots, "--check", powershell=powershell, bash=not powershell, source=source)
            self.assertIn("Installed managed bytes verified", verified.stdout)

    def test_native_unterminated_final_record_is_still_verified(self):
        for label, powershell, home, store, roots, source in self.performers():
            with self.subTest(performer=label):
                self.install(*roots, powershell=powershell, bash=not powershell, source=source)
                inventory = home / ".lintel-install.tsv"
                inventory.write_bytes(inventory.read_bytes().rstrip(b"\n"))
                last = inventory.read_text(encoding="utf-8").split("\n")[-1].split("\t")[2]
                verified = self.install(*roots, "--check", powershell=powershell, bash=not powershell, source=source)
                self.assertIn("Installed managed bytes verified", verified.stdout)
                (home / last).write_bytes((home / last).read_bytes() + b"\n# final-record drift\n")
                before = hashes(home)
                drift = self.install(*roots, "--check", powershell=powershell, bash=not powershell,
                                     success=False, source=source)
                print("F06_CASE " + json.dumps({"performer": label, "variant": "unterminated-valid-final",
                                                "relative": last, "exit": drift.returncode,
                                                "ready": "Installed managed bytes verified" in drift.stdout}))
                self.assertIn(f"Managed-file drift: {last}", drift.stderr)
                self.assertNotIn("Installed managed bytes verified", drift.stdout)
                self.assertEqual(hashes(home), before)

    def test_native_payload_installs_and_verifies_alias_registry(self):
        for label, powershell, home, store, roots, source in self.performers():
            with self.subTest(performer=label):
                payload = source / "config/aliases.yaml"
                self.assertEqual(payload.read_bytes(), (ROOT / "config/aliases.yaml").read_bytes())
                self.install(*roots, powershell=powershell, bash=not powershell, source=source)
                installed = home / "config/aliases.yaml"
                self.assertEqual(installed.read_bytes(), payload.read_bytes())
                rows = [line.split("\t") for line in
                        (home / ".lintel-install.tsv").read_text(encoding="utf-8").splitlines()[1:]]
                self.assertIn([hashlib.sha256(payload.read_bytes()).hexdigest(), str(payload.stat().st_size),
                               "config/aliases.yaml"], rows)
                verified = self.install(*roots, "--check", powershell=powershell, bash=not powershell, source=source)
                self.assertIn("Installed managed bytes verified", verified.stdout)
                installed.write_bytes(installed.read_bytes() + b"# operator drift\n")
                drift = self.install(*roots, "--check", powershell=powershell, bash=not powershell,
                                     success=False, source=source)
                self.assertIn("Managed-file drift: config/aliases.yaml", drift.stderr)
                before = hashes(home)
                self.install(*roots, powershell=powershell, bash=not powershell, success=False, source=source)
                self.assertEqual(hashes(home), before)


class ScaffoldMigrationLifecycle(LifecycleFixture):
    def setUp(self):
        super().setUp()
        for relative in ("bin/li-scaffold", "bin/li-migrate-claude-home", "bin/li-pack-scaffold",
                         "bin/li-snapshot.py", "bin/li-managed-transaction.py", "lib/managed_transaction.py"):
            target = self.source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        shutil.copytree(ROOT / "scaffolding", self.source / "scaffolding")
        result = subprocess.run(["git", "init", "-q", str(self.target)], capture_output=True, env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.recovery = self.base / "recovery"
        self.env["LINTEL_RECOVERY_STORE"] = str(self.recovery)

    def shell_helper(self, name, *args, success=True):
        result = subprocess.run([OPTIONS.bash, str(self.source / "bin" / name), *args],
                                cwd=self.target, env=self.env, text=True, encoding="utf-8",
                                capture_output=True, timeout=120)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def test_scaffold_preserves_user_prose_and_is_repeatable_in_separate_consumer(self):
        original = (self.target / "AGENTS.md").read_bytes()
        memory = self.target / ".claude/memory"
        memory.mkdir(parents=True)
        (memory / "lessons.md").write_text("Operator lessons.\n", encoding="utf-8")
        self.shell_helper("li-scaffold", "init", "--target", str(self.target),
                          "--name", "Literal $(not-a-command); name")
        self.assertEqual((self.target / "AGENTS.md").read_bytes(), original)
        self.assertEqual((memory / "lessons.md").read_text(encoding="utf-8"), "Operator lessons.\n")
        for relative in (".claude/memory/MEMORY.md", ".claude/lintel-layout.yaml",
                         ".claude/templates/swarm/coordination.template.json", "CLAUDE.md"):
            self.assertTrue((self.target / relative).is_file(), relative)
        before = hashes(self.target)
        self.shell_helper("li-scaffold", "init", "--target", str(self.target))
        self.assertEqual(hashes(self.target), before)

    def test_scaffold_refuses_late_link_before_any_seed_writes(self):
        outside = self.base / "outside"
        outside.mkdir()
        (self.target / ".claude").mkdir()
        os.symlink(outside, self.target / ".claude/memory", target_is_directory=True)
        before = hashes(self.target)
        self.shell_helper("li-scaffold", "init", "--target", str(self.target), success=False)
        self.assertEqual(hashes(self.target), before)
        self.assertEqual(list(outside.iterdir()), [])

    def test_legacy_compliance_flag_cannot_claim_an_unimplemented_policy_change(self):
        before = hashes(self.target)
        self.shell_helper("li-scaffold", "init", "--target", str(self.target),
                          "--compliance", "full", success=False)
        self.assertEqual(hashes(self.target), before)

    def test_extension_scaffold_refuses_existing_prose_before_any_mutation(self):
        (self.target / "README.md").write_bytes(b"User-owned README.\n")
        before = hashes(self.target)
        self.shell_helper("li-pack-scaffold", "demo-pack", "--namespace", "demo",
                          "--workflow", "demo-forge", "--target", str(self.target),
                          "--in-place", success=False)
        self.assertEqual(hashes(self.target), before)

    def test_extension_scaffold_validates_actual_output_and_never_activates(self):
        self.shell_helper("li-pack-scaffold", "demo-pack", "--namespace", "demo",
                          "--workflow", "demo-forge", "--target", str(self.store),
                          "--description", 'literal ", "name": "not-the-name')
        path = self.store / "demo-pack"
        manifest = json.loads((path / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "demo-pack")
        self.assertEqual(self.result("pack-validate", "demo-pack")["status"], "valid")
        for relative in ("skills", "agents", "hooks", "knowhow"):
            self.assertTrue((path / relative).is_dir())
        self.assertFalse(self.pointer.exists())

    def test_runtime_migration_collision_preserves_all_bytes_and_does_not_stamp_marker(self):
        old = self.target / ".lintel/state"
        new = self.target / ".claude/runtime/state"
        old.mkdir(parents=True)
        new.mkdir(parents=True)
        (old / "00-state.md").write_text("Legacy state.\n", encoding="utf-8")
        (new / "00-state.md").write_text("New user state.\n", encoding="utf-8")
        before = hashes(self.target)
        self.shell_helper("li-migrate-claude-home", "--repo", str(self.target), success=False)
        self.assertEqual(hashes(self.target), before)
        self.assertFalse((self.target / ".claude/lintel-layout.yaml").exists())

    def test_migration_moves_hidden_runtime_preserves_stubs_and_repairs_local_pointer(self):
        old = self.target / "tasks"
        old.mkdir()
        (old / "lessons.md").write_bytes(b"Preserve real legacy lessons.\n")
        state = self.target / ".lintel/state/nested"
        state.mkdir(parents=True)
        (state / ".hidden.json").write_bytes(b'{"retain":true}\n')
        self.shell_helper("li-migrate-claude-home", "--repo", str(self.target))
        self.assertEqual((self.target / ".claude/memory/lessons.md").read_bytes(), b"Preserve real legacy lessons.\n")
        self.assertIn("Moved to", (old / "lessons.md").read_text(encoding="utf-8"))
        self.assertEqual((self.target / ".claude/runtime/state/nested/.hidden.json").read_bytes(), b'{"retain":true}\n')
        self.assertFalse((state / ".hidden.json").exists())
        settings = self.target / ".claude/settings.local.json"
        settings.write_text('{"custom": [1, 2], "autoMemoryDirectory": "old location"}\n', encoding="utf-8")
        self.shell_helper("li-migrate-claude-home", "--repo", str(self.target), "--repair-pointer")
        content = json.loads(settings.read_text(encoding="utf-8"))
        self.assertEqual(content["custom"], [1, 2])
        self.assertEqual(Path(content["autoMemoryDirectory"]).resolve(), (self.target / ".claude/memory").resolve())
        self.assertIn('"custom": [1, 2]', settings.read_text(encoding="utf-8"))
        before = hashes(self.target)
        self.shell_helper("li-migrate-claude-home", "--repo", str(self.target))
        self.assertEqual(hashes(self.target), before)

    def test_interrupted_migration_is_diagnosed_and_explicitly_recovers_original_bytes(self):
        legacy = self.target / "tasks"
        legacy.mkdir()
        (legacy / "lessons.md").write_bytes(b"original legacy knowledge\n")
        before = hashes(self.target)
        script = r'''
import importlib.util,sys
from pathlib import Path
source=Path(sys.argv[1])
sys.dont_write_bytecode=True
sys.path.insert(0,str(source/"lib"))
import managed_transaction as transaction
original=transaction._write_change
def interrupted(root,relative,data,mode,expected):
    original(root,relative,data,mode,expected)
    raise OSError("synthetic migration interruption")
transaction._write_change=interrupted
spec=importlib.util.spec_from_file_location("lifecycle",source/"bin/li-lifecycle.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
sys.argv=["li-lifecycle","migrate"]
raise SystemExit(module.main())
'''
        interrupted = subprocess.run([sys.executable, "-c", script, str(self.source)],
                                     cwd=self.target, env=self.env, text=True, encoding="utf-8",
                                     capture_output=True, timeout=60)
        self.assertNotEqual(interrupted.returncode, 0)
        self.assertIn("synthetic migration interruption", interrupted.stderr)
        self.assertFalse((self.target / ".claude/lintel-layout.yaml").exists())
        partial = hashes(self.target)
        diagnosed = self.run_helper("doctor", "--json", success=False)
        self.assertEqual(json.loads(diagnosed.stdout)["transaction"]["status"], "error")
        self.assertEqual(hashes(self.target), partial)
        self.shell_helper("li-migrate-claude-home", "--repo", str(self.target), success=False)
        identifier = next((self.recovery / "transactions").iterdir()).name
        recovered = subprocess.run([sys.executable, str(self.source / "bin/li-managed-transaction.py"),
                                   "recover", identifier, "--root", str(self.target), "--store", str(self.recovery)],
                                  cwd=self.target, env=self.env, text=True, encoding="utf-8", capture_output=True)
        self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
        self.assertEqual(hashes(self.target), before)

    def test_malformed_local_settings_refuse_all_migration_writes(self):
        (self.target / "tasks").mkdir()
        (self.target / "tasks/lessons.md").write_bytes(b"legacy content")
        (self.target / ".claude").mkdir()
        (self.target / ".claude/settings.local.json").write_bytes(b'{"custom":1,"custom":2}')
        before = hashes(self.target)
        self.shell_helper("li-migrate-claude-home", "--repo", str(self.target), success=False)
        self.assertEqual(hashes(self.target), before)

    def _long_plain_consumer(self, name):
        prefix = name + "-"
        padding = 256 - len(str(self.base)) - 1 - len(prefix)
        self.assertGreater(padding, 0, "Keep the verified fixture depth; do not relocate a target.")
        target = self.base / (prefix + "x" * padding)
        native_io_path(target).mkdir()
        self.assertEqual(len(str(target)), 256)
        self.env.pop("LINTEL_RECOVERY_STORE", None)
        self.assertFalse(native_io_path(target / ".git").exists())
        return target

    def _native_lifecycle_state(self, root):
        native = native_io_path(root)
        if not native.exists():
            return None
        return {path.relative_to(native).as_posix(): [
            path.lstat().st_mode, getattr(path.lstat(), "st_file_attributes", 0),
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
        ] for path in (native, *native.rglob("*"))}

    def _long_seed(self, target, files):
        for relative, data in files.items():
            path = native_io_path(target / relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    def test_long_plain_migration_keeps_hidden_files_stubs_and_user_bytes(self):
        from managed_transaction import default_store

        target = self._long_plain_consumer("legacy")
        seeds = {
            "tasks/lessons.md": b"Legacy lessons.\r\n",
            "docs/adr/nested/.hidden.md": b"# Original hidden decision\r\n",
            ".lintel/state/nested/.hidden.json": b'{"legacy":"retain"}\r\n',
            ".claude/memory/MEMORY.md": b"User-owned memory index.\r\n",
            ".claude/lintel-layout.yaml": b"layout_version: 5\r\n# Keep marker comments.\r\n",
            ".gitignore": b"# Keep ignore prose.\r\n",
            ".claude/settings.local.json": b'\xef\xbb\xbf{\r\n  "custom": [1, 2], "autoMemoryDirectory": "old"\r\n}\r\n',
            "unrelated.txt": b"Unrelated consumer bytes.\r\n",
        }
        self._long_seed(target, seeds)
        protected = [self._native_lifecycle_state(root) for root in (self.source, self.home, self.target)]
        original = self._native_lifecycle_state(target)
        preview = json.loads(self.shell_helper("li-migrate-claude-home", "--repo", str(target), "--dry-run").stdout)
        self.assertEqual(preview["state"], "preview")
        self.assertEqual(self._native_lifecycle_state(target), original)
        self.assertFalse(native_io_path(default_store(target)).exists())
        result = json.loads(self.shell_helper("li-migrate-claude-home", "--repo", str(target)).stdout)
        self.assertEqual(result["state"], "complete")
        moves = {
            "tasks/lessons.md": ".claude/memory/lessons.md",
            "docs/adr/nested/.hidden.md": ".claude/decisions/nested/.hidden.md",
            ".lintel/state/nested/.hidden.json": ".claude/runtime/state/nested/.hidden.json",
        }
        for old, new in moves.items():
            self.assertEqual(native_io_path(target / new).read_bytes(), seeds[old])
            if old.startswith(".lintel/"):
                self.assertFalse(native_io_path(target / old).exists())
            else:
                self.assertTrue(native_io_path(target / old).read_bytes().startswith(f"> Moved to {new} (".encode()))
        for relative in (".claude/memory/MEMORY.md", ".claude/lintel-layout.yaml", "unrelated.txt"):
            self.assertEqual(native_io_path(target / relative).read_bytes(), seeds[relative], relative)
        self.assertEqual(native_io_path(target / ".gitignore").read_bytes(),
                         seeds[".gitignore"] + b"# Lintel local state\n.claude/runtime/\n.claude/settings.local.json\n")
        self.assertEqual(native_io_path(target / ".claude/settings.local.json").read_bytes(),
                         seeds[".claude/settings.local.json"].replace(
                             b'"old"', json.dumps(str(target / ".claude/memory")).encode()))
        stable = self._native_lifecycle_state(target)
        repeated = json.loads(self.shell_helper("li-migrate-claude-home", "--repo", str(target)).stdout)
        self.assertEqual(repeated["state"], "unchanged")
        self.assertEqual(self._native_lifecycle_state(target), stable)
        self.assertEqual([self._native_lifecycle_state(root) for root in (self.source, self.home, self.target)], protected)
        print(json.dumps({"case": "long-legacy-moves", "target": str(target), "result": result,
                          "before": original, "after": stable}))

    def test_long_plain_migration_collisions_and_invalid_inputs_refuse_before_writes(self):
        from managed_transaction import default_store

        cases = {
            "knowledge-collision": {"tasks/lessons.md": b"old", ".claude/memory/lessons.md": b"new"},
            "hidden-collision": {".lintel/state/nested/.hidden": b"old",
                                 ".claude/runtime/state/nested/.hidden": b"new"},
            "stranded-redirect": {"tasks/lessons.md": b"> Moved to .claude/memory/lessons.md (v5).\n"},
            "malformed-settings": {".claude/settings.local.json": b'{"custom":1,"custom":2}'},
            "invalid-marker": {".claude/lintel-layout.yaml": b"layout_version: invalid\n"},
        }
        for name, values in cases.items():
            with self.subTest(case=name):
                target = self._long_plain_consumer(name)
                self._long_seed(target, {".gitignore": b"# Unrelated policy\r\n", **values})
                before = self._native_lifecycle_state(self.base)
                result = self.shell_helper("li-migrate-claude-home", "--repo", str(target), success=False)
                self.assertEqual(result.stdout, "")
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(self._native_lifecycle_state(self.base), before)
                self.assertFalse(native_io_path(default_store(target)).exists())
                print(json.dumps({"case": name, "target": str(target), "exit": result.returncode,
                                  "stderr": result.stderr, "state_preserved": True}))
        for relative in ("tasks/lessons.md", ".claude/memory/MEMORY.md", ".claude/settings.local.json"):
            with self.subTest(nonfile=relative):
                target = self._long_plain_consumer("nonfile-" + relative.replace("/", "-").replace(".", ""))
                native_io_path(target / relative).mkdir(parents=True)
                before = self._native_lifecycle_state(self.base)
                result = self.shell_helper("li-migrate-claude-home", "--repo", str(target), success=False)
                self.assertEqual(result.stdout, "")
                self.assertEqual(self._native_lifecycle_state(self.base), before)
                self.assertFalse(native_io_path(default_store(target)).exists())

    def test_long_plain_pointer_repair_preserves_surroundings_and_no_pointer_opt_out(self):
        target = self._long_plain_consumer("pointer")
        settings = b'{\r\n "custom" : [1, 2], "autoMemoryDirectory" : "old"\r\n}\r\n'
        seeds = {".claude/settings.local.json": settings,
                 ".claude/lintel-layout.yaml": b"layout_version: 5\n# Retained marker.\n",
                 ".gitignore": b"# Consumer ignore prose\r\n",
                 ".claude/memory/MEMORY.md": b"User-owned memory index\r\n"}
        self._long_seed(target, seeds)
        result = json.loads(self.shell_helper("li-migrate-claude-home", "--repo", str(target),
                                             "--repair-pointer").stdout)
        self.assertEqual(result["changed"], [".claude/settings.local.json"])
        self.assertEqual(native_io_path(target / ".claude/settings.local.json").read_bytes(),
                         settings.replace(b'"old"', json.dumps(str(target / ".claude/memory")).encode()))
        for relative in seeds.keys() - {".claude/settings.local.json"}:
            self.assertEqual(native_io_path(target / relative).read_bytes(), seeds[relative], relative)
        native_io_path(target / ".claude/settings.local.json").write_bytes(b"malformed but opted out\r\n")
        self.shell_helper("li-migrate-claude-home", "--repo", str(target), "--no-memory-pointer")
        self.assertEqual(native_io_path(target / ".claude/settings.local.json").read_bytes(),
                         b"malformed but opted out\r\n")
        print(json.dumps({"case": "long-pointer-modes", "target": str(target), "pointer_result": result}))

    def test_long_extension_outputs_keep_create_only_expectations(self):
        from managed_transaction import default_store

        observer = r'''
import importlib.util, sys
from pathlib import Path
source, target, relative = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, str(source / "lib"))
from context_safety import native_io_path
spec = importlib.util.spec_from_file_location("observed_lifecycle", source / "bin/li-lifecycle.py")
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
publication = module.runtime_publication
def intervene(config, args, *positional, **keywords):
    path = native_io_path(target / relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"Late consumer-owned extension content.\r\n")
    print("F02_EXTENSION_INTERVENED", file=sys.stderr)
    return publication(config, args, *positional, **keywords)
module.runtime_publication = intervene
sys.argv = ["li-lifecycle", "extension-pack", "example", "--namespace", "example",
            "--workflow", "example-flow", "--target", str(target), "--in-place"]
raise SystemExit(module.main())
'''
        for relative in ("pack.yaml", ".claude-plugin/plugin.json", "README.md", "CLAUDE.md"):
            for late in (False, True):
                with self.subTest(output=relative, late=late):
                    target = self._long_plain_consumer(
                        ("late-" if late else "existing-") + relative.replace("/", "-").replace(".", ""))
                    self._long_seed(target, {"unrelated.txt": b"Keep this extension neighbor.\r\n"})
                    if not late:
                        self._long_seed(target, {relative: b"Late consumer-owned extension content.\r\n"})
                    before = self._native_lifecycle_state(target)
                    source_before = self._native_lifecycle_state(self.source)
                    if late:
                        result = subprocess.run([sys.executable, "-I", "-B", "-c", observer,
                                                 str(self.source), str(target), relative],
                                                cwd=self.target, env=self.env, text=True, encoding="utf-8",
                                                capture_output=True, timeout=120)
                        self.assertIn("F02_EXTENSION_INTERVENED", result.stderr)
                    else:
                        result = self.shell_helper("li-pack-scaffold", "example", "--namespace", "example",
                                                   "--workflow", "example-flow", "--target", str(target),
                                                   "--in-place", success=False)
                    print(json.dumps({"case": "extension-create-only", "target": str(target),
                                      "relative": relative, "late": late, "exit": result.returncode,
                                      "stdout": result.stdout, "stderr": result.stderr}))
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(result.stdout, "")
                    self.assertFalse(native_io_path(default_store(target)).exists())
                    self.assertEqual(native_io_path(target / relative).read_bytes(),
                                     b"Late consumer-owned extension content.\r\n")
                    after = self._native_lifecycle_state(target)
                    for name, state in before.items():
                        self.assertEqual(after[name], state, name)
                    self.assertLessEqual(after.keys() - before.keys(), {relative, ".claude-plugin"})
                    self.assertEqual(self._native_lifecycle_state(self.source), source_before)

    def child(self, name="child consumer"):
        target = self.base / name
        target.mkdir()
        (target / "unrelated.txt").write_bytes(b"untouched child data\n")
        return target

    def bind_caller(self):
        reference = self.result("profile-bind")["reference"]
        self.env["LINTEL_PROFILE_REFERENCE"] = json.dumps(reference)
        return reference

    def test_neutral_caller_pin_is_not_transferred_to_explicit_child(self):
        reference = self.bind_caller()
        child = self.child()
        parent_before, home_before = hashes(self.target), hashes(self.home)
        result = json.loads(self.shell_helper("li-scaffold", "init", "--target", str(child)).stdout)
        self.assertEqual(result["operation_profile_reference"], reference)
        self.assertIsNone(result["target_profile_reference"])
        self.assertEqual(hashes(self.target), parent_before)
        self.assertEqual(hashes(self.home), home_before)
        self.assertEqual((child / "unrelated.txt").read_bytes(), b"untouched child data\n")
        self.assertFalse((child / ".claude/runtime/profiles/selected.json").exists())

    def test_required_caller_policy_is_verified_as_an_operation_constraint(self):
        self.pack("required")
        self.require("required")
        reference = self.bind_caller()
        child = self.child()
        before = hashes(self.home)
        result = json.loads(self.shell_helper("li-scaffold", "init", "--target", str(child)).stdout)
        self.assertTrue(result["required_caller_policy"])
        self.assertEqual(result["operation_profile_reference"], reference)
        self.assertEqual(result["target_selection"]["requested"], "required")
        self.assertIsNone(result["target_profile_reference"])
        self.assertEqual(hashes(self.home), before)
        self.assertFalse((child / ".claude/profile-requirements.json").exists())
        self.assertFalse((child / "packs").exists())

    def test_neutral_caller_cannot_hide_missing_target_required_policy(self):
        self.bind_caller()
        child = self.child()
        (child / ".claude").mkdir()
        (child / ".claude/profile-requirements.json").write_text(
            json.dumps({"schema_version": 1, "required_pack": "not-installed"}), encoding="utf-8")
        before = hashes(child)
        result = self.shell_helper("li-scaffold", "init", "--target", str(child), success=False)
        self.assertIn("PROFILE_REQUIRED", result.stderr)
        self.assertEqual(hashes(child), before)

    def test_missing_or_drifted_caller_pin_refuses_child_writes(self):
        self.pack("required")
        self.require("required")
        self.bind_caller()
        child = self.child()
        current = next((self.home / "sessions/profiles").glob("*/current-profile.json"))
        saved = current.read_bytes()
        current.unlink()
        before = hashes(child)
        self.shell_helper("li-scaffold", "init", "--target", str(child), success=False)
        self.assertEqual(hashes(child), before)
        current.write_bytes(saved)
        manifest = self.store / "required/pack.yaml"
        manifest.write_bytes(manifest.read_bytes() + b"# policy drift\n")
        self.shell_helper("li-scaffold", "init", "--target", str(child), success=False)
        self.assertEqual(hashes(child), before)

    def test_conflicting_target_policy_and_same_name_different_content_are_refused(self):
        self.pack("required", root=self.target / "packs")
        self.pack("different")
        self.require("required")
        self.bind_caller()
        child = self.child()
        (child / ".claude").mkdir()
        declaration = child / ".claude/profile-requirements.json"
        declaration.write_text(json.dumps({"schema_version": 1, "required_pack": "different"}), encoding="utf-8")
        before = hashes(child)
        self.shell_helper("li-scaffold", "init", "--target", str(child), success=False)
        self.assertEqual(hashes(child), before)
        declaration.write_text(json.dumps({"schema_version": 1, "required_pack": "required"}), encoding="utf-8")
        self.pack("required", root=child / "packs", extra="roles: {source: different-source}\n")
        before = hashes(child)
        refused = self.shell_helper("li-scaffold", "init", "--target", str(child), success=False)
        self.assertIn("source/content", refused.stderr)
        self.assertEqual(hashes(child), before)


def load_tests(loader, tests, pattern):
    if os.name == "nt":
        return tests
    windows_only = {
        "test_powershell_reinstall_keeps_operator_files_inside_managed_trees",
        "test_powershell_entry_interruption_recovery_and_consumed_permission",
    }

    def cases(suite):
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                yield from cases(item)
            else:
                yield item

    print("UNVERIFIED: Windows-only native performer cases require a Windows job; POSIX cases remain scheduled.")
    return unittest.TestSuite(case for case in cases(tests) if case._testMethodName not in windows_only)


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], *TEST_ARGS])
