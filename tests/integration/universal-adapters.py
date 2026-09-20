"""Exercise the real shared installer and installed consumers, without calling a model."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
from client_capabilities import load_registry


class UniversalAdapters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_registry()
        cls.sandbox = tempfile.TemporaryDirectory(prefix="lintel-universal-")
        cls.base = Path(cls.sandbox.name).resolve()

    @classmethod
    def tearDownClass(cls):
        cls.sandbox.cleanup()

    def setUp(self):
        self.target = self.base / self._testMethodName
        self.target.mkdir()
        self.home = self.base / (self._testMethodName + "-unused-home")
        self.home.mkdir()

    def run_cli(self, command="init", client=None, target=None, source=ROOT, success=True, extra=()):
        command_line = [sys.executable, "-S", str(source / "bin/li-adapter.py"), command,
                        "--target", str(target or self.target), "--source", str(source)]
        if client:
            command_line += ["--client", client]
        result = subprocess.run(command_line + list(extra), capture_output=True, text=True, encoding="utf-8",
                                env=dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home)))
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        self.assertEqual(list(self.home.iterdir()), [], "Installer must not write user-global state")
        return result

    def snapshot(self):
        return {p.relative_to(self.target).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.target.rglob("*") if p.is_file() and not p.is_symlink()}

    def test_each_surface_generates_its_route_and_real_source_consumers(self):
        clients = sorted(self.registry["surfaces"])
        self.run_cli(extra=tuple(value for client in clients for value in ("--client", client)))
        self.run_cli("check")
        inventory = json.loads((self.target / ".github/lintel/manifest.json").read_text())
        self.assertEqual(inventory["clients"], clients)
        self.assertFalse(inventory["hooks_installed"])
        for client, record in self.registry["surfaces"].items():
            with self.subTest(client=client):
                expected_root = record["discovery"]["root"]
                if expected_root:
                    self.assertIn(f"{expected_root}/li-plan/SKILL.md", inventory["files"])
                    self.assertTrue((self.target / expected_root / "li-plan/SKILL.md").is_file())
                else:
                    self.assertIn(f"`{client}`: manual", (self.target / ".github/lintel/START.md").read_text())
                result = subprocess.run([sys.executable, "-S", str(self.target / ".github/lintel/bin/li-client-capabilities.py"),
                                         "show", "--client", client], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["id"], client)
        expected_roots = {record["discovery"]["root"] for record in self.registry["surfaces"].values()
                          if record["discovery"]["root"]}
        actual_roots = {str(Path(p).parent.parent).replace("\\", "/") for p in inventory["files"]
                        if p.endswith("/li-plan/SKILL.md")}
        self.assertEqual(actual_roots, expected_roots)
        self.assertTrue((self.target / ".github/lintel/.claude-plugin/plugin.json").is_file())
        self.assertFalse((self.target / ".github/hooks").exists())
        self.assertFalse((self.target / ".github/lintel/hooks").exists())

    def test_multiple_clients_share_one_bundle_and_preserve_copilot(self):
        (self.target / "AGENTS.md").write_bytes(b"# Existing rules\r\nRun our real tests.\r\n")
        (self.target / ".github").mkdir()
        (self.target / ".github/copilot-instructions.md").write_text("Existing team policy.\n")
        self.run_cli(client="copilot-cli")
        copilot = (self.target / ".github/skills/li-plan/SKILL.md").read_bytes()
        self.run_cli(client="codex-cli")
        self.run_cli(client="gemini-cli")
        before = self.snapshot()
        self.run_cli(client="codex-cli")
        self.assertEqual(before, self.snapshot())
        self.run_cli("check")
        self.assertEqual((self.target / ".github/skills/li-plan/SKILL.md").read_bytes(), copilot)
        self.assertEqual((self.target / ".github/copilot-instructions.md").read_text(), "Existing team policy.\n")
        self.assertTrue((self.target / "AGENTS.md").read_bytes().startswith(b"# Existing rules\r\n"))
        manifest = json.loads((self.target / ".github/lintel/manifest.json").read_text())
        self.assertEqual(manifest["clients"], ["codex-cli", "copilot-cli", "gemini-cli"])

    def test_same_native_root_is_shared_without_surface_alias_collapse(self):
        for client in ("codex-cli", "codex-desktop", "antigravity-ide"):
            self.run_cli(client=client)
        self.run_cli("check")
        manifest = json.loads((self.target / ".github/lintel/manifest.json").read_text())
        self.assertEqual(len(manifest["clients"]), 3)
        self.assertEqual(sum(p == ".agents/skills/li-plan/SKILL.md" for p in manifest["files"]), 1)

    def test_managed_and_unmanaged_native_collisions_refuse_all_writes(self):
        collision = self.target / ".gemini/skills/li-plan/SKILL.md"
        collision.parent.mkdir(parents=True)
        collision.write_text("Project-owned plan.\n")
        before = self.snapshot()
        self.assertIn("Unmanaged collision", self.run_cli(client="gemini-cli", success=False).stderr)
        self.assertEqual(before, self.snapshot())
        collision.unlink()
        self.run_cli(client="gemini-cli")
        collision.write_text(collision.read_text() + "\nLocal customization.\n")
        before = self.snapshot()
        self.assertIn("Modified managed file", self.run_cli(client="copilot-app", success=False).stderr)
        self.assertEqual(before, self.snapshot())

    def test_fresh_clone_manual_handoff_and_operation_selection(self):
        self.run_cli(client="other")
        manifest = json.loads((self.target / ".github/lintel/manifest.json").read_text())
        self.assertFalse(any(p.endswith("/li-plan/SKILL.md") for p in manifest["files"]))
        clone = self.base / "manual-clone"
        shutil.copytree(self.target, clone)
        bundle = clone / ".github/lintel"
        self.run_cli("check", target=clone, source=bundle)
        binding = clone / "session.json"
        profile_ref = {"schema_version": 1, "context_id": "fixture-work", "generation": 1,
                       "digest": "sha256:" + "a" * 64, "name": "_default", "version": "fixture"}
        binding.write_text(json.dumps({
            "schema_version": 1, "surface": "other", "session_id": "fixture-work", "host_version": None,
            "work_map": ".claude/plans/example/work.json", "profile_ref": profile_ref,
            "bindings": {"question": {"tool": "different_host.ask", "available": True, "permission": "allowed"}},
            "isolation": {"kind": "none", "attributable": False, "evidence": None},
        }))
        result = subprocess.run([sys.executable, "-S", str(bundle / "bin/li-client-capabilities.py"), "resolve",
                                 "--session", str(binding)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        selected = json.loads(result.stdout)
        self.assertEqual(selected["operations"]["question"]["tool"], "different_host.ask")
        self.assertEqual(selected["execution_mode"], "manual-handoff")
        self.assertEqual(selected["profile_ref"], profile_ref)
        self.assertEqual(selected["independent_review"], "outstanding")
        for resource in ("skills/plan/SKILL.md", "skills/build/SKILL.md", "skills/resume/SKILL.md",
                         "scaffolding/01-foundation/templates/swarm/agent-brief.template.md"):
            self.assertTrue((bundle / resource).is_file(), resource)
        self.assertIn("AGENTS.md", (bundle / "START.md").read_text())
        for workflow in ("cli-fingerprint", "pair-agent", "codex"):
            canonical = bundle / "skills" / workflow / "SKILL.md"
            self.assertIn("../../shims/universal/ADAPTER.md", canonical.read_text(encoding="utf-8"))
            self.assertTrue((canonical.parent / "../../shims/universal/ADAPTER.md").resolve().is_file())

    def test_unknown_client_and_fictional_controls_refuse_before_writes(self):
        for client, extra in (("fictional", ()), ("codex-cli", ("--enable",)),
                              ("copilot-app", ("--model", "imaginary")), ("other", ("--global",))):
            self.run_cli(client=client, extra=extra, success=False)
            self.assertEqual(list(self.target.iterdir()), [])

    def test_spaces_metacharacters_and_user_home_boundary(self):
        project = self.target / "project with spaces & brackets[1]"
        project.mkdir()
        self.run_cli(client="junie-cli", target=project)
        self.run_cli("check", target=project)
        self.assertTrue((project / ".junie/skills/li-plan/SKILL.md").is_file())
        refused = self.run_cli(client="junie-cli", target=self.home, success=False)
        self.assertIn("user-home root", refused.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_tampered_inventory_cannot_claim_other_project_files(self):
        self.run_cli(client="codex-cli")
        inventory_path = self.target / ".github/lintel/manifest.json"
        original = json.loads(inventory_path.read_text())
        for malicious in (".agents/settings.json", ".agents/skills/company/SKILL.md", "../escape",
                          ".agents/skills/li-plan/../outside", ".agents\\skills\\li-plan\\SKILL.md"):
            manifest = dict(original)
            manifest["files"] = {malicious: "0" * 64}
            inventory_path.write_text(json.dumps(manifest))
            before = self.snapshot()
            self.run_cli(client="codex-cli", success=False)
            self.assertEqual(before, self.snapshot())
        inventory_path.write_text(json.dumps(original))


if __name__ == "__main__":
    unittest.main(verbosity=2)
