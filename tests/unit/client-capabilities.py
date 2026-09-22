"""Behavioral contract for surface evidence and current-session operation selection."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
import client_capabilities as capabilities


class ClientCapabilities(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = capabilities.load_registry(ROOT / "lib/cli-tiers.yaml")

    def session(self, **bindings):
        return {
            "schema_version": 1, "session_id": "fixture-session",
            "surface": "copilot-app", "host_version": None,
            "bindings": bindings,
            "isolation": {"kind": "none", "attributable": False, "evidence": None},
        }

    def binding(self, tool="host.ask", permission="allowed", available=True):
        return {"tool": tool, "permission": permission, "available": available}

    def test_surfaces_do_not_collapse(self):
        groups = (
            ("claude-code", "claude-desktop"),
            ("copilot-cli", "copilot-app", "copilot-vscode", "copilot-cloud"),
            ("codex-cli", "codex-desktop", "codex-ide", "codex-cloud"),
            ("cursor-cli", "cursor-ide", "cursor-cloud"),
            ("opencode-cli", "opencode-desktop", "opencode-ide"),
            ("droid-cli", "factory-desktop", "factory-cloud"),
            ("antigravity-cli", "antigravity-desktop", "antigravity-ide"),
            ("kiro-cli", "kiro-ide", "kiro-web"),
            ("devin-cli", "devin-desktop", "devin-local", "devin-cloud"),
            ("junie-cli", "junie-ide"),
            ("cline-cli", "cline-ide"), ("continue-cli", "continue-ide"),
        )
        for group in groups:
            resolved = [capabilities.surface_id(self.registry, name) for name in group]
            self.assertEqual(resolved, list(group))
            self.assertEqual(len(set(resolved)), len(group))
        self.assertIn("aider-cli", self.registry["surfaces"])

    def test_legacy_aliases_are_unambiguous(self):
        for old, new in {"claude": "claude-code", "codex": "codex-cli",
                         "copilot": "copilot-cli", "copilot-coding-agent": "copilot-cloud",
                         "cursor": "cursor-ide", "gemini": "gemini-cli",
                         "opencode": "opencode-cli", "droid": "droid-cli",
                         "factory-droid": "droid-cli", "windsurf": "devin-desktop"}.items():
            self.assertEqual(capabilities.surface_id(self.registry, old), new)
        with self.assertRaises(ValueError):
            capabilities.surface_id(self.registry, "invented-host")

    def test_evidence_layers_round_trip_without_promotion(self):
        decoded = json.loads(json.dumps(self.registry))
        capabilities.validate_registry(decoded)
        record = capabilities.describe(decoded, "gemini-cli")
        skill = record["operations"]["skills"]
        self.assertEqual(skill["vendor"]["status"], "documented")
        self.assertEqual(skill["delivered"]["kind"], "native-files")
        self.assertEqual(skill["observed"]["status"], "not_run")
        self.assertTrue(skill["vendor"]["sources"][0]["checked"])
        self.assertTrue(skill["vendor"]["sources"][0]["version"])
        browser = capabilities.describe(decoded, "opencode-desktop")["operations"]["browser"]
        self.assertEqual(browser["vendor"]["status"], "unknown")
        self.assertEqual(browser["observed"]["status"], "not_run")
        hook = capabilities.describe(decoded, "claude-code")["operations"]["hooks"]
        self.assertEqual(hook["delivered"]["kind"], "optional-native-adapter")
        self.assertIn("not installed", hook["delivered"]["conditions"])
        self.assertEqual(hook["observed"]["status"], "not_run")

    def test_invalid_registry_fails_closed(self):
        mutations = (
            lambda r: r.update(schema_version=True),
            lambda r: r["surfaces"]["copilot-cli"].update(surface="cli/desktop"),
            lambda r: r["aliases"].update({"copilot-app": "copilot-cli"}),
            lambda r: r["aliases"].update({"fiction": "missing"}),
            lambda r: r["surfaces"]["codex-cli"]["discovery"].update(root="../.agents/skills"),
            lambda r: r["surfaces"]["codex-cli"]["discovery"].update(source="missing"),
            lambda r: r["surfaces"]["codex-cli"]["vendor"]["skills"].update(status="full"),
            lambda r: r["sources"]["codex-skills"].update(checked="yesterday"),
            lambda r: r["sources"]["codex-skills"].update(url="file:///private"),
        )
        for mutate in mutations:
            registry = copy.deepcopy(self.registry)
            mutate(registry)
            with self.assertRaises(ValueError):
                capabilities.validate_registry(registry)

    def test_observation_needs_actual_version_revision_and_evidence(self):
        registry = copy.deepcopy(self.registry)
        registry["surfaces"]["codex-cli"]["observations"] = {
            "skills": {"status": "observed", "scenario": "discovery",
                       "host_version": None, "lintel_revision": "not-a-revision",
                       "checked": "2026-09-20", "evidence": None}
        }
        with self.assertRaises(ValueError):
            capabilities.validate_registry(registry)

    def test_partial_observation_retains_unknown_identity(self):
        partial = capabilities.describe(self.registry, "copilot-app")["operations"]["delegate"]["observed"]
        self.assertEqual(partial["status"], "partial")
        self.assertIsNone(partial["host_version"])
        self.assertIsNone(partial["lintel_revision"])
        self.assertTrue(partial["limitations"])

    def test_alternate_question_tool_is_selected_not_renamed(self):
        session = self.session(question=self.binding("client.confirm_with_operator"))
        result = capabilities.resolve(self.registry, session)
        self.assertEqual(result["operations"]["question"]["mode"], "native")
        self.assertEqual(result["operations"]["question"]["tool"], "client.confirm_with_operator")
        self.assertEqual(result["evidence_level"], "declared-session-bindings")
        self.assertFalse(result["executed"])

    def test_absent_question_uses_conversation(self):
        result = capabilities.resolve(self.registry, self.session())
        self.assertEqual(result["operations"]["question"]["mode"], "conversation")
        self.assertEqual(result["execution_mode"], "manual-handoff")
        self.assertEqual(result["independent_review"], "outstanding")

    def test_permission_denial_or_unknown_cannot_be_bypassed(self):
        for permission, mode in (("denied", "blocked"), ("ask", "approval-required"),
                                 ("unknown", "approval-required")):
            session = self.session(question=self.binding(permission=permission))
            self.assertEqual(capabilities.resolve(self.registry, session)["operations"]["question"]["mode"], mode)

    def test_unavailable_tool_never_selected(self):
        result = capabilities.resolve(self.registry, self.session(
            browser=self.binding("browser.navigate", available=False)))
        self.assertEqual(result["operations"]["browser"]["mode"], "manual-evidence")
        self.assertIsNone(result["operations"]["browser"]["tool"])

    def test_parallel_requires_attributable_isolation_not_only_worktree_label(self):
        session = self.session(delegate=self.binding("host.delegate"),
                               isolate=self.binding("host.worktree"))
        session["isolation"] = {"kind": "git-worktree", "attributable": False, "evidence": None}
        self.assertEqual(capabilities.resolve(self.registry, session)["execution_mode"], "serial")
        session["isolation"].update(attributable=True, evidence="fixture distinct worktree paths")
        self.assertEqual(capabilities.resolve(self.registry, session)["execution_mode"], "native-isolated")
        session["bindings"]["isolate"]["permission"] = "denied"
        self.assertEqual(capabilities.resolve(self.registry, session)["execution_mode"], "serial")

    def test_delegation_is_not_independent_review(self):
        result = capabilities.resolve(self.registry, self.session(delegate=self.binding("host.delegate")))
        self.assertEqual(result["execution_mode"], "serial")
        self.assertEqual(result["independent_review"], "outstanding")

    def test_missing_controls_explicitly_unsupported(self):
        result = capabilities.resolve(self.registry, self.session(shell=self.binding("host.shell")))
        for operation in ("hooks", "plugin_control", "model_control"):
            self.assertEqual(result["operations"][operation]["mode"], "unsupported")
            self.assertIsNone(result["operations"][operation]["tool"])

    def test_invalid_session_is_not_a_success_shaped_default(self):
        for change in (
            {"surface": "fiction"},
            {"bindings": {"question": {"tool": "ask", "available": "yes", "permission": "allowed"}}},
            {"bindings": {"made_up": self.binding()}},
            {"isolation": {"kind": "git-worktree", "attributable": True, "evidence": None}},
        ):
            session = self.session()
            session.update(change)
            with self.assertRaises(ValueError):
                capabilities.resolve(self.registry, session)

    def test_cli_validation_and_describe_are_real_consumers(self):
        for arguments in (["validate"], ["show", "--client", "copilot-app"]):
            result = subprocess.run([sys.executable, str(ROOT / "bin/li-client-capabilities.py"), *arguments],
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIsInstance(json.loads(result.stdout), dict)

    def test_shell_list_is_lf_only_even_with_native_windows_python(self):
        result = subprocess.run([sys.executable, str(ROOT / "bin/li-client-capabilities.py"), "list"],
                                capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(b"\r", result.stdout)
        self.assertIn(b"\ncopilot-app\n", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
