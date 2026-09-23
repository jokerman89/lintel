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
JOINED_RUNTIME_RESOURCES = (
    "lib/swarm_snapshot.py", "lib/swarm_evidence.py",
    "lib/envelope_contract.py", "lib/envelope-requirements.txt",
    "lib/profile_context.py", "lib/profile-context-schema.json", "lib/pack-schema.yaml",
    "lib/native_paths.py",
    "lib/context_safety.py", "lib/review_contract.py", "lib/review-schema.json",
    "bin/li-review-evidence.py", "bin/li-review-log", "bin/li-review-read",
    "bin/li-domain-result.py", "lib/domain_result.py", "lib/domain-result-schema.json",
    "lib/state.sh", "lib/cycle-modes.sh", "lib/cycle-footer.sh", "lib/workflow.sh",
    "bin/li-catalog.py", "lib/capability-selections.json",
    "skills/catalog/references/metadata.md", "skills/catalog/references/selections.md",
    "skills/browse/scripts/chromium.mjs", "skills/scrape/scripts/extract.mjs",
    "lib/url_policy.py", "config/aliases.yaml", "install/upstream-sources.yaml",
    ".claude-plugin/plugin.json",
    "skills/design-dna/scripts/design_contract.py",
    "skills/design-dna/references/design-contract.schema.json",
    "skills/design-dna/references/design-contract.md",
    "skills/catalog/references/consumer-checks.md",
    "skills/generate-write/references/fidelity-and-evidence.md",
    "skills/generate-word/references/native-word.md",
    "skills/generate-ppt/references/native-powerpoint.md",
    "skills/generate-xlsx/references/native-xlsx.md",
    "skills/generate-xlsx/scripts/check_xlsx.py",
    "skills/generate-pdf/scripts/prepare_html.py",
    "skills/generate-pdf/scripts/check_pdf.py",
    "skills/generate-pdf/scripts/print_pdf.mjs",
    "skills/generate/scripts/pipeline_inputs.py",
)
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
        shutil.copytree(ROOT / "docs", cls.source / "docs")
        for name in adapter.DOCS + adapter.SOURCE_METADATA + ("LICENSE", "shims/copilot/COPILOT.md", "shims/universal/ADAPTER.md"):
            if (ROOT / name).is_file():
                (cls.source / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, cls.source / name)

    @classmethod
    def tearDownClass(cls):
        # TemporaryDirectory owns this exact sandbox; no user path is deleted.
        assert cls.base.name.startswith("lintel-copilot-tests-")
        assert Path(cls.sandbox.name).resolve() == cls.base
        if os.name == "nt":
            # Retain TemporaryDirectory's readonly handling for long native paths.
            directory = str(cls.base)
            if not directory.startswith("\\\\?\\"):
                directory = "\\\\?\\UNC\\" + directory[2:] if directory.startswith("\\\\") else "\\\\?\\" + directory
            cls.sandbox.name = directory
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

    def snapshot(self, target=None):
        root = target or self.target
        return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob("*") if p.is_file() and not p.is_symlink()}

    def test_browser_modules_use_portable_text_bytes(self):
        module = self.target / "browser.mjs"
        module.write_bytes(b"export const fixture = 'ok';\r\n")
        self.assertEqual(adapter.source_bytes(module), b"export const fixture = 'ok';\n")
        binary = self.target / "sample.png"
        binary.write_bytes(b"\x89PNG\r\n\x1a\n")
        self.assertEqual(adapter.source_bytes(binary), b"\x89PNG\r\n\x1a\n")

    def test_selected_catalog_runs_from_portable_bundle_without_source_fallback(self):
        target = self.base / "selection"
        target.mkdir()
        (target / "consumer-owned.txt").write_bytes(b"preserve consumer selection state\r\n")
        self.run_cli(target=target)
        self.run_cli("check", target=target)
        before = self.snapshot(target)
        self.run_cli(target=target)
        self.assertEqual(before, self.snapshot(target))
        bundle = target / adapter.BUNDLE
        for relative in adapter.SOURCE_METADATA + JOINED_RUNTIME_RESOURCES:
            self.assertEqual((bundle / relative).read_bytes(),
                             adapter.source_bytes(self.source / relative))
        for relative in (
            "skills/design-dna/ATTRIBUTION.md",
            "skills/design-dna/LICENSES/MIT-next-level-builder.txt",
            "skills/design-dna/LICENSES/Apache-2.0-anthropic.txt",
        ):
            self.assertEqual((bundle / relative).read_bytes(),
                             adapter.source_bytes(self.source / relative))
        unrelated = self.base / "unrelated-cwd"
        unrelated.mkdir()
        for arguments in (("--json", "--name=match"),
                          ("--json", "--selection=demo-script", "--kind=agent")):
            result = subprocess.run(
                [sys.executable, "-I", "-B", str(bundle / "bin/li-catalog.py"), *arguments],
                cwd=unrelated, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            value = json.loads(result.stdout)
            self.assertFalse(value["executed"])
            self.assertNotIn("## Behavioral traits", result.stdout)
            if "--name=match" in arguments:
                self.assertEqual([item["id"] for item in value["entries"]], ["skill:skill-router"])
            else:
                self.assertEqual({item["id"] for item in value["entries"]}, {
                    "agent:DemoNarrativeArc", "agent:DemoNarratorJunior",
                    "agent:SlideNarrationCritic",
                })
                self.assertEqual(value["selection"]["order"], ["core", "demo-script"])
                for resource in value["selection"]["resources"]:
                    self.assertTrue((bundle / resource["path"]).is_file(), resource["path"])
        self.assertEqual(before, self.snapshot(target))
        self.assertEqual(list(unrelated.iterdir()), [])
        clone = self.base / "sc"
        shutil.copytree(target, clone)
        clone_bundle = clone / adapter.BUNDLE
        self.run_cli("check", target=clone, source=clone_bundle,
                     script=clone_bundle / "bin/li-copilot.py")
        empty_home = self.base / "selection-empty-home"
        empty_home.mkdir()
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("LINTEL_", "CLAUDE_"))}
        env.update(HOME=str(empty_home), USERPROFILE=str(empty_home),
                   PYTHONDONTWRITEBYTECODE="1")
        clone_before = self.snapshot(clone)
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(clone_bundle / "bin/li-catalog.py"),
             "--json", "--selection=demo-script", "--kind=agent"],
            cwd=unrelated, env=env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual({item["id"] for item in json.loads(result.stdout)["entries"]}, {
            "agent:DemoNarrativeArc", "agent:DemoNarratorJunior", "agent:SlideNarrationCritic",
        })
        missing_parser = subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(clone_bundle / "bin/li-catalog.py"),
             "--json", "--selection=demo-script"],
            cwd=unrelated, env=env, capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(missing_parser.returncode, 0)
        self.assertEqual(missing_parser.stdout, "")
        self.assertIn("PyYAML", missing_parser.stderr)
        manifest_path = clone / adapter.INVENTORY
        original_manifest = manifest_path.read_bytes()
        for relative in (
            "skills/generate-write/references/fidelity-and-evidence.md",
            "skills/generate-xlsx/scripts/check_xlsx.py",
            "skills/generate-pdf/scripts/check_pdf.py",
        ):
            path = clone_bundle / relative
            original_resource = path.read_bytes()
            inventory = json.loads(original_manifest)
            del inventory["files"][f"{adapter.BUNDLE}/{relative}"]
            manifest_path.write_text(json.dumps(inventory), encoding="utf-8")
            path.unlink()
            missing_before = self.snapshot(clone)
            try:
                result = self.run_cli(
                    "check", target=clone, source=clone_bundle,
                    script=clone_bundle / "bin/li-copilot.py", success=False,
                )
                self.assertIn(f"Required source file is missing: {path}", result.stderr)
                self.assertEqual(missing_before, self.snapshot(clone))
            finally:
                path.write_bytes(original_resource)
                manifest_path.write_bytes(original_manifest)
        self.assertEqual(clone_before, self.snapshot(clone))
        self.assertEqual(list(empty_home.iterdir()), [])
        self.assertEqual(list(unrelated.iterdir()), [])

    def test_optional_family_closures_survive_portable_clone(self):
        target = self.base / "families"
        target.mkdir()
        self.run_cli(target=target)
        clone = self.base / "fc"
        shutil.copytree(target, clone)
        bundle = clone / adapter.BUNDLE
        self.run_cli("check", target=clone, source=bundle, script=bundle / "bin/li-copilot.py")
        unrelated = self.base / "family-cwd"
        unrelated.mkdir()
        empty_home = self.base / "family-home"
        empty_home.mkdir()
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("LINTEL_", "CLAUDE_"))}
        env.update(HOME=str(empty_home), USERPROFILE=str(empty_home),
                   PYTHONDONTWRITEBYTECODE="1")

        def query(*arguments, success=True):
            result = subprocess.run(
                [sys.executable, "-I", "-B", str(bundle / "bin/li-catalog.py"),
                 "--json", *arguments],
                cwd=unrelated, env=env, capture_output=True, text=True, encoding="utf-8")
            if success:
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            else:
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
            return result

        expected = {
            "core", "demo-script", "design-knowledge", "frontend-design",
            "document-content", "document-word", "document-ppt", "document-pdf",
            "document-xlsx", "document-visio", "customer-communication", "regulatory-review",
        }
        expected_bundle, _, _ = adapter.generate(self.source, target)
        before = self.snapshot(clone)
        index = json.loads(query("--list-selections").stdout)
        self.assertEqual({item["id"] for item in index["selections"]}, expected)
        self.assertFalse(index["executed"])
        full = json.loads(query("--kind=all").stdout)
        self.assertEqual(full["total"], 196)
        for name in sorted(expected):
            with self.subTest(selection=name):
                result = query(f"--selection={name}")
                selected = json.loads(result.stdout)
                self.assertFalse(selected["executed"])
                self.assertTrue(all(entry["maturity"] == "unknown" for entry in selected["entries"]))
                self.assertNotIn("## Behavioral traits", result.stdout)
                self.assertIn("core", selected["selection"]["order"])
                for resource in selected["selection"]["resources"]:
                    relative = resource["path"]
                    key = f"{adapter.BUNDLE}/{relative}"
                    public_document = relative.startswith("docs/") or relative in adapter.PUBLIC_ROOT_DOCS
                    expected_bytes = expected_bundle[key] if public_document else \
                        adapter.source_bytes(self.source / relative)
                    self.assertEqual((bundle / relative).read_bytes(), expected_bytes, relative)
                for material in selected["selection"]["provenance"]:
                    self.assertIsNone(material["import_commit"])
                    for field in ("notice", "attribution"):
                        self.assertTrue((bundle / material[field]).read_bytes())
                if name in ("document-word", "document-pdf", "document-xlsx"):
                    self.assertEqual(selected["selection"]["order"], ["core", name])
                if name == "document-visio":
                    stages = {item["id"]: item for item in selected["selection"]["source_stages"]}
                    self.assertEqual(stages["skill:generate-visio"]["status"], "staged")
        first = query("--selection=document-word", "--selection=document-content")
        second = query("--selection=document-content", "--selection=document-word")
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(before, self.snapshot(clone))
        for relative in (
            "skills/design-dna/LICENSES/MIT-next-level-builder.txt",
            "skills/design-dna/LICENSES/Apache-2.0-anthropic.txt",
            "skills/design-dna/data/typography.csv",
        ):
            path = bundle / relative
            original = path.read_bytes()
            path.unlink()
            missing_before = self.snapshot(clone)
            try:
                refused = query("--selection=frontend-design", success=False)
                self.assertIn(path.name, refused.stderr)
                self.assertEqual(missing_before, self.snapshot(clone))
            finally:
                path.write_bytes(original)
        self.assertEqual(before, self.snapshot(clone))
        self.assertEqual(list(empty_home.iterdir()), [])
        self.assertEqual(list(unrelated.iterdir()), [])

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

    def test_swarm_wrapper_and_complete_source_resource_inventory(self):
        self.run_cli()
        wrapper = self.target / ".github/skills/li-swarm/SKILL.md"
        self.assertTrue(wrapper.is_file())
        self.assertIn("../../lintel/skills/swarm/SKILL.md", wrapper.read_text(encoding="utf-8"))
        inventory = json.loads((self.target / adapter.INVENTORY).read_text(encoding="utf-8"))["files"]
        for relative in adapter.SWARM_RESOURCES + adapter.ADAPTER_RESOURCES + adapter.SOURCE_METADATA:
            installed = f"{adapter.BUNDLE}/{relative}"
            self.assertIn(installed, inventory)
            self.assertTrue((self.target / installed).is_file(), installed)

    def test_missing_mandatory_swarm_dependency_refuses_before_writes(self):
        broken = self.base / "missing-swarm-dependency-source"
        shutil.copytree(self.source, broken)
        before = self.snapshot()
        for relative in adapter.SWARM_RESOURCES + adapter.ADAPTER_RESOURCES + adapter.SOURCE_METADATA:
            with self.subTest(relative=relative):
                path = broken / relative
                content = path.read_bytes()
                path.unlink()
                try:
                    result = self.run_cli(success=False, source=broken)
                    if relative == "lib/cli-tiers.yaml":
                        self.assertIn("ERROR:", result.stderr)
                        self.assertIn("cli-tiers.yaml", result.stderr)
                    else:
                        self.assertIn(f"Required source file is missing: {path}", result.stderr)
                    self.assertEqual(before, self.snapshot())
                finally:
                    path.write_bytes(content)

    def test_joined_runtime_dependencies_refuse_incomplete_source_before_writes(self):
        broken = self.base / "missing-joined-dependency-source"
        shutil.copytree(self.source, broken)
        for index, relative in enumerate(JOINED_RUNTIME_RESOURCES):
            with self.subTest(relative=relative):
                target = self.target / str(index)
                target.mkdir()
                (target / "consumer-owned.txt").write_bytes(b"retain exact consumer bytes\r\n")
                before = self.snapshot(target)
                path = broken / relative
                content = path.read_bytes()
                path.unlink()
                try:
                    result = self.run_cli(source=broken, target=target, success=False)
                    self.assertIn(f"Required source file is missing: {path}", result.stderr)
                    self.assertEqual(before, self.snapshot(target))
                finally:
                    path.write_bytes(content)

    def test_joined_installed_dependencies_cannot_be_hidden_by_inventory_removal(self):
        self.run_cli()
        bundle = self.target / adapter.BUNDLE
        manifest_path = self.target / adapter.INVENTORY
        original = manifest_path.read_bytes()
        for relative in JOINED_RUNTIME_RESOURCES:
            with self.subTest(relative=relative):
                path = bundle / relative
                content = path.read_bytes()
                inventory = json.loads(original)
                self.assertIn(f"{adapter.BUNDLE}/{relative}", inventory["files"])
                del inventory["files"][f"{adapter.BUNDLE}/{relative}"]
                manifest_path.write_text(json.dumps(inventory), encoding="utf-8")
                path.unlink()
                before = self.snapshot()
                try:
                    result = self.run_cli("check", source=bundle,
                                          script=bundle / "bin/li-copilot.py", success=False)
                    self.assertIn(f"Required source file is missing: {path}", result.stderr)
                    self.assertEqual(before, self.snapshot())
                finally:
                    path.write_bytes(content)
                    manifest_path.write_bytes(original)
        self.run_cli("check", source=bundle, script=bundle / "bin/li-copilot.py")

    def test_joined_installed_profile_is_pinned_across_fresh_shells_and_detects_drift(self):
        # Keep the fixture's nested runtime paths inside native Windows path limits.
        target = self.base / "profile-consumer"
        target.mkdir()
        self.run_cli(target=target)
        (target / ".claude/profile-requirements.json").write_text(
            json.dumps({"schema_version": 1, "required_pack": "_default"}), encoding="utf-8")
        home = self.base / "joined-profile-unused-home"
        home.mkdir()
        env = {key: value for key, value in os.environ.items()
               if not key.startswith("LINTEL_") and key != "CLAUDE_SESSION_ID"}
        env.update(HOME=str(home), USERPROFILE=str(home), PYTHONDONTWRITEBYTECODE="1")
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(bash)
        script = '''set -e
source .github/lintel/lib/copilot-env.sh
lintel_copilot_env "$PWD"
printf '%s\\n' "$LINTEL_PROFILE_REFERENCE"
'''

        def bootstrap():
            return subprocess.run([bash, "-c", script], cwd=target, env=env,
                                  capture_output=True, text=True, encoding="utf-8")

        first = bootstrap()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        reference = json.loads(first.stdout)
        self.assertEqual(reference["name"], "_default")
        repeated = bootstrap()
        self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
        self.assertEqual(json.loads(repeated.stdout), reference)
        selected = target / ".claude/runtime/profiles/selected.json"
        pin = selected.read_bytes()
        manifest = target / adapter.BUNDLE / "packs/_default/pack.yaml"
        content, times = manifest.read_bytes(), manifest.stat()
        manifest.write_bytes(content + b"\n# Same-mtime input drift\n")
        os.utime(manifest, ns=(times.st_atime_ns, times.st_mtime_ns))
        try:
            refused = bootstrap()
            self.assertNotEqual(refused.returncode, 0, refused.stdout + refused.stderr)
            self.assertIn("PROFILE_", refused.stderr)
            self.assertEqual(refused.stdout, "")
            self.assertEqual(selected.read_bytes(), pin)
        finally:
            manifest.write_bytes(content)
            os.utime(manifest, ns=(times.st_atime_ns, times.st_mtime_ns))
        restored = bootstrap()
        self.assertEqual(restored.returncode, 0, restored.stdout + restored.stderr)
        self.assertEqual(json.loads(restored.stdout), reference)
        self.assertEqual(list(home.iterdir()), [])

    def test_joined_installed_swarm_and_json_envelope_use_stdlib_dependencies(self):
        self.run_cli()
        bundle = self.target / adapter.BUNDLE
        product = self.target / "product.txt"
        product.write_text("original synthetic product\n", encoding="utf-8")
        script = '''import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "lib"))
from swarm_contract import capture_result, verify_result
root = Path(sys.argv[2])
result = capture_result(root, ["product.txt"])
verify_result(root, ["product.txt"], result)
(root / "product.txt").write_text("changed synthetic product\\n", encoding="utf-8")
try:
    verify_result(root, ["product.txt"], result)
except ValueError:
    print(json.dumps(result))
else:
    raise AssertionError("installed snapshot accepted changed product bytes")
'''
        result = subprocess.run([sys.executable, "-I", "-B", "-S", "-c", script,
                                 str(bundle), str(self.target)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        snapshot = json.loads(result.stdout)
        self.assertEqual(snapshot["kind"], "files")
        self.assertIn("product.txt", snapshot["files"])
        envelope = {
            "head": {"envelope_id": "synthetic-installed", "envelope_schema_version": "1",
                     "kind": "subagent_spawn", "from": "plan", "to": "fixture",
                     "issued_at": "2026-09-20T00:00:00Z"},
            "body": {"content_type": "brief", "content": {
                "task": "Inspect synthetic product", "constraints": ["No publication"],
                "acceptance": ["Report observed bytes"]}},
            "tail": {"completeness_score": 100, "evaluators_run": [], "escape_hatches": [],
                     "audit_pointer": ".claude/runtime/audit/synthetic.jsonl"},
        }
        path = self.target / "synthetic-envelope.json"
        command = [sys.executable, "-I", "-B", "-S", str(bundle / "lib/envelope_contract.py"),
                   "validate", str(path)]
        path.write_text(json.dumps(envelope), encoding="utf-8")
        valid = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        envelope["head"]["kind"] = "invented-kind"
        path.write_text(json.dumps(envelope), encoding="utf-8")
        invalid = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(invalid.returncode, 0, invalid.stdout + invalid.stderr)
        self.assertFalse((self.target / ".claude/runtime/audit").exists())

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
test -f "$LINTEL_SOURCE_ROOT/bin/li-swarm.py"
test -f "$LINTEL_SOURCE_ROOT/lib/swarm-schema.json"
test -f "$LINTEL_SOURCE_ROOT/scaffolding/01-foundation/templates/swarm/agent-brief.template.md"
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
        for name in ("charter.template.md", "coordination.template.json", "agent-brief.template.md",
                     "agent-report.template.md", "agent-review.template.md"):
            self.assertTrue((self.target / ".claude/templates/swarm" / name).is_file(), name)
        brief = (self.target / ".claude/templates/swarm/agent-brief.template.md").read_text(encoding="utf-8")
        self.assertTrue((self.target / "CORE-PRINCIPLES.md").is_file())
        self.assertIn("`CORE-PRINCIPLES.md`", brief)
        self.assertNotIn("scaffolding/01-foundation/CORE-PRINCIPLES.md", brief)

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

    def test_bundled_scaffold_prefers_installed_source_root_over_runtime_home(self):
        self.run_cli()
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(bash)
        env = {key: value for key, value in os.environ.items() if not key.startswith("LINTEL_")}
        script = '''set -e
source .github/lintel/lib/copilot-env.sh
lintel_copilot_env "$PWD"
test "$LINTEL_HOME" = "$PWD/.claude/runtime/lintel-home"
mkdir downstream-scaffold
bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" init --target "$PWD/downstream-scaffold" --name downstream
'''
        result = subprocess.run([bash, "-c", script], cwd=self.target, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        downstream = self.target / "downstream-scaffold"
        self.assertTrue((downstream / ".claude/templates/swarm/coordination.template.json").is_file())
        self.assertFalse((self.target / ".claude/runtime/lintel-home/scaffolding").exists())

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
