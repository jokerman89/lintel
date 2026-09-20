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
                                env=dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                                         PYTHONDONTWRITEBYTECODE="1"))
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

    def test_manual_readme_navigation_survives_installed_source_clone(self):
        self.run_cli(client="other")
        clone = self.base / "navigation-clone"
        git = shutil.which("git")
        self.assertTrue(git, "Git is required for the real fresh navigation clone")
        env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                   GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")
        for arguments in (("init", "-q"), ("add", "."),
                          ("-c", "user.name=Lintel Test", "-c", "user.email=lintel-test@example.invalid",
                           "-c", "commit.gpgsign=false", "commit", "-qm", "test: preserve bundled navigation",
                           "-m", "Co-authored-by: Copilot App <223556219+Copilot@users.noreply.github.com>"),
                          ("clone", "-q", str(self.target), str(clone))):
            result = subprocess.run([git, *arguments], cwd=self.target, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        required = (
            "docs/README.md", "docs/faq.md", "docs/concepts/engineering-modules.md",
            "docs/concepts/pack-resolver.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "CHANGELOG.md",
        )
        transitive = ("docs/concepts/pack-inheritance.md", "docs/concepts/agent-memory.md",
                      "docs/showcase/README.md", "docs/showcase/lintel-the-harness.html",
                      "docs/wiki/skills.md", "docs/migrations/_INDEX.md",
                      "LICENSE", "skills/design-dna/ATTRIBUTION.md")
        for target in (self.target, clone):
            bundle = target / ".github/lintel"
            self.run_cli("check", target=target, source=bundle)
            readme = (bundle / "README.md").read_text(encoding="utf-8")
            for relative in required:
                with self.subTest(target=target.name, link=relative):
                    self.assertIn(f"]({relative})", readme)
                    self.assertTrue((bundle / relative).is_file(), f"Missing bundled README target: {relative}")
            for relative in transitive:
                self.assertTrue((bundle / relative).is_file(), relative)
            for relative in ("LICENSE", "CODE_OF_CONDUCT.md", "skills/design-dna/ATTRIBUTION.md"):
                self.assertEqual((bundle / relative).read_bytes(),
                                 (ROOT / relative).read_bytes().replace(b"\r\n", b"\n"), relative)
            self.assertIn("source-repository links", (bundle / "CONTRIBUTING.md").read_text())
            self.assertFalse((bundle / ".claude").exists())
        bundle = clone / ".github/lintel"
        missing = bundle / "docs/faq.md"
        missing.unlink()
        manifest_path = bundle / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        del manifest["files"][".github/lintel/docs/faq.md"]
        manifest_path.write_text(json.dumps(manifest))
        before = {str(path.relative_to(clone)): path.read_bytes() for path in clone.rglob("*")
                  if path.is_file() and ".git" not in path.parts}
        result = self.run_cli("check", target=clone, source=bundle, success=False)
        self.assertIn("docs", result.stderr)
        self.assertIn("faq.md", result.stderr)
        self.assertEqual(before, {str(path.relative_to(clone)): path.read_bytes() for path in clone.rglob("*")
                                 if path.is_file() and ".git" not in path.parts})

    def test_transitive_public_link_missing_source_and_managed_drift(self):
        self.run_cli(client="other")
        source = self.target / ".github/lintel"
        entry = source / "docs/faq.md"
        with entry.open("a", encoding="utf-8") as output:
            output.write("\n[Another public guide][next]\n\n[next]: extra/next.md\n")
        downstream = self.base / "navigation-downstream"
        downstream.mkdir()
        (downstream / "keep.txt").write_text("Project content.\n")
        result = self.run_cli(client="other", source=source, target=downstream, success=False)
        self.assertIn("next.md", result.stderr)
        self.assertEqual([p.name for p in downstream.iterdir()], ["keep.txt"])
        next_guide = source / "docs/extra/next.md"
        next_guide.parent.mkdir()
        next_guide.write_text(
            "[Image](chart.svg)\n\n```md\n[Example](not-a-resource.md)\n```\n"
            "[Template](<name>.md)\n[Source only](../../.claude/runtime/not-copied.md)\n",
            encoding="utf-8")
        (next_guide.parent / "chart.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>\n')
        self.run_cli(client="other", source=source, target=downstream)
        self.run_cli("check", target=downstream, source=downstream / ".github/lintel")
        installed = downstream / ".github/lintel/docs/extra/next.md"
        self.assertTrue(installed.is_file())
        self.assertTrue(installed.with_name("chart.svg").is_file())
        self.assertIn("not fetched or live-verified", installed.read_text())
        self.assertFalse((downstream / ".github/lintel/.claude").exists())
        original = installed.read_bytes()
        installed.write_bytes(original + b"\nProject-owned change must survive.\n")
        result = self.run_cli("check", source=source, target=downstream, success=False)
        self.assertIn("Modified managed file", result.stderr)
        result = self.run_cli(client="other", source=source, target=downstream, success=False)
        self.assertIn("Modified managed file", result.stderr)
        self.assertEqual(installed.read_bytes(), original + b"\nProject-owned change must survive.\n")

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
