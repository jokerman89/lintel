"""Behavior tests against real adapter processes and isolated consumer repositories."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("li_copilot", ROOT / "bin/li-copilot.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class CopilotKit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sandbox = tempfile.TemporaryDirectory(prefix="lintel-copilot-tests-")
        cls.base = Path(cls.sandbox.name).resolve()
        cls.source = cls.base / "source"
        cls.source.mkdir()
        # Freeze a real source snapshot so parallel work in the checkout cannot
        # introduce unrelated source drift between init and check.
        for name in adapter.COMPONENTS:
            shutil.copytree(ROOT / name, cls.source / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in adapter.DOCS + ("LICENSE", "shims/copilot/COPILOT.md"):
            if (ROOT / name).is_file():
                (cls.source / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, cls.source / name)

    @classmethod
    def tearDownClass(cls):
        # TemporaryDirectory owns this exact sandbox; no user path is deleted.
        assert cls.base.name.startswith("lintel-copilot-tests-")
        cls.sandbox.cleanup()

    def setUp(self):
        self.target = self.base / self._testMethodName
        self.target.mkdir()

    def run_cli(self, command="init", success=True, source=None, target=None, script=None):
        result = subprocess.run(
            [sys.executable, str(script or self.source / "bin/li-copilot.py"), command,
             "--target", str(target or self.target), "--source", str(source or self.source)],
            capture_output=True, text=True, encoding="utf-8")
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def snapshot(self):
        return {p.relative_to(self.target).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.target.rglob("*") if p.is_file() and not p.is_symlink()}

    def test_fresh_portable_clone_and_idempotence(self):
        self.run_cli()
        before = self.snapshot()
        self.run_cli()
        self.assertEqual(before, self.snapshot())
        self.run_cli("check")
        self.assertTrue((self.target / ".github/lintel/scaffolding/01-foundation/templates/plan/spec.template.md").is_file())
        self.assertIn(".claude/runtime/", (self.target / ".gitignore").read_text())
        self.assertFalse((self.target / ".github/hooks").exists())
        self.assertFalse((self.target / ".github/lintel/hooks").exists())
        self.assertFalse(json.loads((self.target / adapter.INVENTORY).read_text())["hooks_installed"])
        # A different clone with only committed artifacts remains independently usable.
        clone = self.base / "fresh-clone"
        shutil.copytree(self.target, clone)
        self.run_cli("check", target=clone, source=clone / ".github/lintel", script=clone / ".github/lintel/bin/li-copilot.py")
        no_home = dict(os.environ, HOME=str(self.base / "empty-home"), LINTEL_HOME=str(clone / ".claude/runtime/lintel-home"))
        result = subprocess.run([sys.executable, str(clone / ".github/lintel/bin/li-copilot.py"), "check", "--target", str(clone)], env=no_home, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_preserves_existing_project_instructions_and_memory(self):
        (self.target / ".github").mkdir()
        (self.target / ".github/copilot-instructions.md").write_text("Team policy stays.\n")
        (self.target / "AGENTS.md").write_text("Existing project agent rules.\n")
        self.run_cli()
        self.assertEqual((self.target / ".github/copilot-instructions.md").read_text(), "Team policy stays.\n")
        self.assertTrue((self.target / "AGENTS.md").read_text().startswith("Existing project agent rules.\n"))
        self.assertIn(adapter.PROTOCOL_START.decode(), (self.target / "AGENTS.md").read_text())
        memory = self.target / ".claude/memory/lessons.md"
        memory.write_text("Our durable lesson.\n")
        self.run_cli()
        self.run_cli("check")
        self.assertEqual(memory.read_text(), "Our durable lesson.\n")

    def test_modified_managed_file_refuses_entire_update(self):
        self.run_cli()
        path = self.target / ".github/skills/li-plan/SKILL.md"
        path.write_text(path.read_text() + "\nTeam modification.\n")
        before = self.snapshot()
        self.assertIn("Modified managed file", self.run_cli(success=False).stderr)
        self.assertEqual(before, self.snapshot())
        self.run_cli("check", success=False)

    def test_full_protocol_is_portable_and_project_prose_survives_update(self):
        team_rules = b"# Team rules\r\nKeep our existing command: make test.\r\n"
        (self.target / "CLAUDE.md").write_bytes(team_rules)
        self.run_cli()
        canonical = adapter.read_file(self.source, "scaffolding/01-foundation/SESSION-PROTOCOL.md").strip()
        for relative in ("AGENTS.md", "CLAUDE.md"):
            self.assertIn(canonical, (self.target / relative).read_bytes())
        entry = self.target / "CLAUDE.md"
        entry.write_bytes(entry.read_bytes() + b"\nAdditional team rule.\n")
        self.run_cli()
        self.run_cli("check")
        self.assertTrue(entry.read_bytes().startswith(team_rules))
        self.assertTrue(entry.read_bytes().endswith(b"Additional team rule.\n"))
        original = entry.read_bytes()
        entry.write_bytes(original.replace(canonical, canonical + b"\nUnauthorized local protocol mutation.\n"))
        before = self.snapshot()
        self.assertIn("Modified session protocol", self.run_cli(success=False).stderr)
        self.assertEqual(before, self.snapshot())

    def test_incomplete_protocol_marker_refuses_without_changes(self):
        (self.target / "AGENTS.md").write_bytes(b"Team rules.\n" + adapter.PROTOCOL_START + b"\npartial")
        before = self.snapshot()
        self.assertIn("Malformed session protocol", self.run_cli(success=False).stderr)
        self.assertEqual(before, self.snapshot())

    def test_unmanaged_collision_refuses_before_foundation_writes(self):
        collision = self.target / ".github/agents/lintel-builder.agent.md"
        collision.parent.mkdir(parents=True)
        collision.write_text("Our own builder.\n")
        before = self.snapshot()
        self.assertIn("Unmanaged collision", self.run_cli(success=False).stderr)
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_missing_managed_file_detected_and_repaired(self):
        self.run_cli()
        (self.target / ".github/skills/li-build/SKILL.md").unlink()
        self.run_cli("check", success=False)
        self.run_cli()
        self.run_cli("check")

    def test_missing_runtime_ignore_is_detected_and_repaired(self):
        self.run_cli()
        ignore = self.target / ".gitignore"
        ignore.unlink()
        self.assertIn("runtime/ ignore rule", self.run_cli("check", success=False).stderr)
        self.run_cli()
        self.run_cli("check")
        ignore.write_text("# Project ignores\n*.local\n")
        self.assertIn("runtime/ ignore rule", self.run_cli("check", success=False).stderr)
        self.run_cli()
        self.run_cli("check")
        self.assertIn("*.local", ignore.read_text())

    def test_source_update_is_reviewable_and_deterministic(self):
        self.run_cli()
        upgraded = self.base / "upgraded-source"
        shutil.copytree(self.source, upgraded)
        path = upgraded / "skills/plan/SKILL.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nAn updated planning instruction.\n", encoding="utf-8")
        protocol = upgraded / "scaffolding/01-foundation/SESSION-PROTOCOL.md"
        protocol.write_text(protocol.read_text(encoding="utf-8") + "\nA new shared startup requirement.\n", encoding="utf-8")
        self.run_cli("check", source=upgraded, success=False)
        self.run_cli(source=upgraded)
        self.run_cli("check", source=upgraded)
        self.assertIn("updated planning", (self.target / ".github/lintel/skills/plan/SKILL.md").read_text(encoding="utf-8"))
        self.assertIn("new shared startup requirement", (self.target / "AGENTS.md").read_text(encoding="utf-8"))

    def test_inventory_traversal_and_windows_paths_refused(self):
        self.run_cli()
        manifest = self.target / adapter.INVENTORY
        original = json.loads(manifest.read_text())
        for unsafe in ("../../escape", "/absolute", "C:/escape", ".github/../escape", ".github\\escape", "AGENTS.md", ".github/skills/li-plan/./SKILL.md", ".github/skills//li-plan/SKILL.md"):
            forged = dict(original)
            forged["files"] = {unsafe: "0" * 64}
            manifest.write_text(json.dumps(forged))
            self.run_cli(success=False)
        manifest.write_text(json.dumps(original))

    def test_invalid_inventory_root_types_are_clean_errors(self):
        self.run_cli()
        manifest = self.target / adapter.INVENTORY
        for value in (None, [], "invalid", 7, {"schema_version": True, "files": {}}):
            manifest.write_text(json.dumps(value))
            before = self.snapshot()
            for command in ("init", "check"):
                result = self.run_cli(command, success=False)
                self.assertIn("ERROR: Unsupported or malformed Copilot inventory", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(before, self.snapshot())

    def test_symlink_parent_refused(self):
        outside = self.base / "outside"
        outside.mkdir(exist_ok=True)
        try:
            (self.target / ".github").symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"Host does not allow creating symlinks: {exc}")
        self.assertIn("Symlink/reparse", self.run_cli(success=False).stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_dogfood_has_no_recursive_source_copy(self):
        local = self.base / "dogfood"
        shutil.copytree(self.source, local)
        (local / "AGENTS.md").write_text("Read canonical repository instructions.\n")
        self.run_cli(source=local, target=local)
        self.run_cli("check", source=local, target=local)
        self.assertFalse((local / ".github/lintel/skills").exists())
        self.assertFalse((local / "CORE-PRINCIPLES.md").exists())
        self.assertIn("../../../skills/plan/SKILL.md", (local / ".github/skills/li-plan/SKILL.md").read_text())

    def test_pack_resolver_uses_bundled_code_and_project_state(self):
        self.run_cli()
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(bash, "Bash is required for the actual downstream runtime test")
        env = dict(os.environ)
        for name in list(env):
            if name.startswith("LINTEL_") or name.startswith("_AUDIT_"):
                env.pop(name)
        script = '''set -e
source .github/lintel/lib/copilot-env.sh
lintel_copilot_env "$PWD"
source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"
test "$(resolve_pack_field compliance.mode)" = advisory
source "$LINTEL_SOURCE_ROOT/lib/paths.sh"
test "$(lintel_plans_dir)" = "$PWD/.claude/plans"
test "$LINTEL_SOURCE_ROOT" = "$PWD/.github/lintel"
test "$LINTEL_HOME" = "$PWD/.claude/runtime/lintel-home"
'''
        result = subprocess.run([bash, "-c", script], cwd=self.target, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.target / ".github/lintel/.claude").exists())

    def test_crlf_source_and_autocrlf_clone(self):
        crlf = self.base / "crlf-source"
        shutil.copytree(self.source, crlf)
        source_skill = crlf / "skills/plan/SKILL.md"
        source_skill.write_bytes(source_skill.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        (self.target / ".gitattributes").write_text("*.custom binary\n")
        self.run_cli(source=crlf)
        self.assertNotIn(b"\r\n", (self.target / ".github/lintel/skills/plan/SKILL.md").read_bytes())
        self.assertIn("*.custom binary", (self.target / ".gitattributes").read_text())
        self.run_cli("check", source=self.source)
        git = shutil.which("git")
        self.assertTrue(git, "Git is required for the real autocrlf clone test")
        def run_git(*args, cwd=self.target):
            result = subprocess.run([git, *args], cwd=cwd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        run_git("init", "-q")
        run_git("config", "core.autocrlf", "true")
        run_git("add", ".")
        run_git("-c", "user.name=Lintel Test", "-c", "user.email=lintel-test@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "Test portable kit")
        clone = self.base / "autocrlf-clone"
        run_git("-c", "core.autocrlf=true", "clone", "-q", str(self.target), str(clone), cwd=self.base)
        self.run_cli("check", target=clone, source=clone / ".github/lintel", script=clone / ".github/lintel/bin/li-copilot.py")
        # A later negation must not turn a textual rule into a false safety signal.
        with (clone / ".gitignore").open("a", encoding="utf-8") as handle:
            handle.write("\n!.claude/runtime/\n")
        result = self.run_cli("check", target=clone, source=clone / ".github/lintel", script=clone / ".github/lintel/bin/li-copilot.py", success=False)
        self.assertIn("Git does not confirm", result.stderr)
        self.run_cli(target=clone, source=clone / ".github/lintel", script=clone / ".github/lintel/bin/li-copilot.py", success=False)

    def test_legacy_scaffold_renders_full_protocol_from_shared_source(self):
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(bash)
        env = {key: value for key, value in os.environ.items() if not key.startswith("LINTEL_")}
        result = subprocess.run([bash, str(self.source / "bin/li-scaffold"), "init", "--target", str(self.target), "--name", "A test project"], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        canonical = adapter.read_file(self.source, "scaffolding/01-foundation/SESSION-PROTOCOL.md").strip()
        for relative in ("AGENTS.md", "CLAUDE.md"):
            self.assertIn(canonical, (self.target / relative).read_bytes().replace(b"\r\n", b"\n"))
        self.assertEqual(canonical, (self.target / "SESSION-PROTOCOL.md").read_bytes().replace(b"\r\n", b"\n").strip())

    def test_copilot_scaffold_rejects_unsupported_options_before_writes(self):
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(bash)
        for option in ("--name", "--pack", "--mode", "--voice", "--compliance"):
            result = subprocess.run([bash, str(self.source / "bin/li-scaffold"), "init", "--copilot", "--target", str(self.target), option, "team"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("unsupported options", result.stderr)
            self.assertEqual(list(self.target.iterdir()), [])

    def test_bundled_scaffold_works_without_executable_file_modes(self):
        self.run_cli()
        legacy = self.base / "legacy-consumer"
        legacy.mkdir()
        git = shutil.which("git")
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(git and bash)
        result = subprocess.run([git, "init", "-q", str(legacy)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        bundle = self.target / ".github/lintel"
        for helper in (bundle / "bin").iterdir():
            if helper.is_file():
                helper.chmod(0o600)
        env = {key: value for key, value in os.environ.items() if not key.startswith("LINTEL_")}
        result = subprocess.run([bash, str(bundle / "bin/li-scaffold"), "init", "--target", str(legacy)], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((legacy / ".claude/lintel-layout.yaml").is_file())

    def test_bundled_envelope_validator_cannot_be_silently_skipped(self):
        self.run_cli()
        bundle = self.target / ".github/lintel"
        validator = bundle / "bin/li-envelope-validate"
        validator.chmod(0o600)
        invalid = self.target / "invalid-envelope.yaml"
        invalid.write_text("not-an-envelope: true\n")
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(bash)
        env = {key: value for key, value in os.environ.items() if not key.startswith("LINTEL_")}
        script = '''source .github/lintel/lib/copilot-env.sh
lintel_copilot_env "$PWD"
bash "$LINTEL_SOURCE_ROOT/bin/li-envelope-replay" invalid-envelope.yaml
'''
        result = subprocess.run([bash, "-c", script], cwd=self.target, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("envelope failed validation", result.stderr)
        validator.unlink()
        result = subprocess.run([bash, "-c", script], cwd=self.target, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("required envelope validator is missing", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
