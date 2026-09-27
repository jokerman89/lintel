"""Behavior tests against real adapter processes and isolated consumer repositories."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
checks_spec = importlib.util.spec_from_file_location(
    "installed_consumer_checks", Path(__file__).with_name("installed_consumer_checks.py"))
checks = importlib.util.module_from_spec(checks_spec)
checks_spec.loader.exec_module(checks)
REVIEW_RUNTIME_RESOURCES = checks.REVIEW_RUNTIME_RESOURCES
profile_continuity, review_controls = checks.profile_continuity, checks.review_controls
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
    "skills/web-session/scripts/chromium.mjs", "skills/web-session/scripts/extract.mjs",
    "skills/web-session/references/browser-operations.md",
    "skills/web-session/references/browse.md", "skills/web-session/references/scrape.md",
    "skills/web-session/references/open.md", "skills/web-session/references/cookies.md",
    "skills/code-freeze/scripts/freeze.py",
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
    "skills/web-session/scripts/chromium.mjs",
    "skills/code-freeze/scripts/freeze.py",
    "skills/generate-pdf/scripts/print_pdf.mjs",
    "skills/generate/scripts/pipeline_inputs.py",
)
spec = importlib.util.spec_from_file_location("li_copilot", ROOT / "bin/li-copilot.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
F05_BYTES = b"F05 intervening consumer bytes\r\n"
# Real adapter publication with one test-only intervention. "planned" fires after
# every planning observation: the candidate's admission call, or the frozen
# producer's first post-plan state capture (its file_state expected rebuild).
# "writer" fires at unchanged apply_files entry, after final adapter admission.
F05_DRIVER = r'''
import importlib.util,sys
from pathlib import Path
sys.dont_write_bytecode=True
source,target,store=map(Path,sys.argv[1:4])
relative,operation,phase=sys.argv[4:7]
sys.path.insert(0,str(source/"lib"))
import context_safety
import managed_transaction as transaction
spec=importlib.util.spec_from_file_location("adapter",source/"bin/li-copilot.py")
adapter=importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
fired=[]
def intervene():
    if fired:
        return
    fired.append(phase)
    path=adapter.native_io_path(adapter.safe_path(target,relative))
    if operation=="create" and path.exists():
        raise AssertionError("create intervention needs an absent path")
    if operation in ("edit","delete") and not path.is_file():
        raise AssertionError("edit/delete intervention needs a present file")
    if operation=="delete":
        path.unlink()
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(b"F05 intervening consumer bytes\r\n")
    print(f"F05_INTERVENTION={phase}:{operation}:{relative}",file=sys.stderr,flush=True)
def intercept(owner,name):
    original=getattr(owner,name)
    def intervening(*values,**options):
        intervene()
        return original(*values,**options)
    setattr(owner,name,intervening)
if phase=="planned":
    if hasattr(adapter,"admitted_expectations"):
        intercept(adapter,"admitted_expectations")
    else:
        intercept(context_safety,"file_state")
elif phase=="writer":
    intercept(transaction,"apply_files")
else:
    raise AssertionError(phase)
sys.argv=["li-copilot","init","--source",str(source),"--target",str(target),"--store",str(store)]
try:
    adapter.main()
except (ValueError,OSError) as error:
    print(error,file=sys.stderr)
    raise SystemExit(17)
if not fired:
    raise AssertionError("intervention point was not reached")
'''
F05_CONSUMER = {
    "AGENTS.md": b"# Consumer agents\r\n\r\nKeep this project prose.\r\n",
    "CLAUDE.md": b"Consumer Claude prose without a block.\n",
    ".gitignore": b"node_modules/\r\n",
    ".gitattributes": b"*.bin binary\r\n",
    "custom.json": b'{"owned":"consumer"}\n',
}
F05_MANAGED = ".github/lintel/scaffolding/01-foundation/templates/plan/spec.template.md"


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

    def catalog_query(self, bundle, *arguments, cwd, env=None, no_site=False):
        command = [sys.executable, "-I", *(["-S"] if no_site else []),
                   "-B", str(bundle / "bin/li-catalog.py"), *arguments]
        return subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                              text=True, encoding="utf-8")

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
        for arguments in (("--json", "--name=skill-router"),
                          ("--json", "--selection=demo-script", "--kind=agent")):
            result = self.catalog_query(bundle, *arguments, cwd=unrelated)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            value = json.loads(result.stdout)
            self.assertFalse(value["executed"])
            self.assertNotIn("## Behavioral traits", result.stdout)
            if "--name=skill-router" in arguments:
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
        result = self.catalog_query(clone_bundle, "--json", "--selection=demo-script",
                                    "--kind=agent", cwd=unrelated, env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual({item["id"] for item in json.loads(result.stdout)["entries"]}, {
            "agent:DemoNarrativeArc", "agent:DemoNarratorJunior", "agent:SlideNarrationCritic",
        })
        missing_parser = self.catalog_query(clone_bundle, "--json", "--selection=demo-script",
                                            cwd=unrelated, env=env, no_site=True)
        self.assertNotEqual(missing_parser.returncode, 0)
        self.assertEqual(missing_parser.stdout, "")
        self.assertIn("PyYAML", missing_parser.stderr)
        manifest_path = clone / adapter.INVENTORY
        original_manifest = manifest_path.read_bytes()
        for relative in (
            "skills/generate-write/references/fidelity-and-evidence.md",
            "skills/generate-xlsx/scripts/check_xlsx.py",
            "skills/generate-pdf/scripts/prepare_html.py",
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
            result = self.catalog_query(bundle, "--json", *arguments, cwd=unrelated, env=env)
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
        canonical_result = self.catalog_query(self.source, "--json", "--kind=all", cwd=unrelated, env=env)
        self.assertEqual(canonical_result.returncode, 0, canonical_result.stdout + canonical_result.stderr)
        canonical = json.loads(canonical_result.stdout)
        self.assertEqual(full["entries"], canonical["entries"])
        self.assertEqual(full["total"], len(canonical["entries"]))
        self.assertEqual(full["matched"], canonical["matched"])
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

    def test_native_publication_keeps_the_original_263_character_destination(self):
        parent_length = 239
        padding = parent_length - len(str(self.target)) - len("\\publication-")
        self.assertGreater(padding, 0, "Run at the declared fixture depth; never shorten an existing target.")
        folder = self.target / ("publication-" + "x" * padding)
        folder.mkdir()
        destination = folder / "agent-brief.template.md"
        self.assertEqual(len(str(folder)), 239)
        self.assertEqual(len(str(destination)), 263)
        relative = destination.relative_to(self.target).as_posix()
        self.assertEqual(adapter.safe_path(self.target, relative), destination)
        adapter.atomic_write(destination, b"exact long destination\r\n")
        self.assertEqual(adapter.native_io_path(destination).read_bytes(), b"exact long destination\r\n")
        self.assertEqual(adapter.read_file(self.target, relative), b"exact long destination\n")
        self.assertEqual(sorted(path.name for path in folder.iterdir()), ["agent-brief.template.md"])
        self.assertFalse(str(adapter.safe_path(self.target, relative)).startswith("\\\\?\\"))

    def test_missing_native_helper_cannot_fall_back_to_target_pythonpath(self):
        broken = self.base / "source without native helper"
        shutil.copytree(self.source, broken)
        helper = broken / "lib/native_paths.py"
        helper.unlink()
        (self.target / "native_paths.py").write_text(
            "raise RuntimeError('target native helper executed')\n", encoding="utf-8")
        before = self.snapshot()
        result = subprocess.run(
            [sys.executable, str(broken / "bin/li-copilot.py"), "init",
             "--source", str(broken), "--target", str(self.target)],
            cwd=self.target, env=dict(os.environ, PYTHONPATH=str(self.target)),
            text=True, encoding="utf-8", capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(f"Required source file is missing: {helper}", result.stderr)
        self.assertNotIn("target native helper executed", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.snapshot(), before)

    def default_consumer(self):
        parent = Path(tempfile.gettempdir()).resolve()
        padding = 94 - len(str(parent)) - 1 - len("p10np-") - 8
        self.assertGreaterEqual(padding, 0, "The exact default fixture must not relocate a longer TEMP.")
        temporary = tempfile.TemporaryDirectory(prefix="p10np-" + "x" * padding, dir=parent)
        created_name = temporary.name
        base = Path(created_name).resolve()

        def cleanup():
            self.assertEqual(temporary.name, created_name)
            self.assertEqual(Path(temporary.name).resolve(), base)
            self.assertTrue(base.name.startswith("p10np-"))
            temporary.name = str(adapter.native_io_path(base))
            try:
                temporary.cleanup()
            finally:
                temporary.name = created_name

        self.addCleanup(cleanup)
        source = base / "exact-source"
        target = base / "installed consumer"
        shutil.copytree(self.source, source)
        target.mkdir()
        (target / "AGENTS.md").write_bytes(b"Consumer AGENTS.md.\n")
        (target / "unrelated.txt").write_bytes(b"Unrelated consumer-owned data\n")
        self.assertEqual((len(str(base)), len(str(target))), (94, 113))
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("LINTEL_", "CLAUDE_", "GSTACK_"))
               and key not in ("PACK_CACHE_FILE", "BASH_ENV", "ENV", "CDPATH", "PYTHONPATH")}
        for name in ("HOME", "USERPROFILE", "TEMP", "TMP", "TMPDIR"):
            self.assertIn(parent.parent, Path(env[name]).resolve().parents, name)
        self.assertNotIn("LINTEL_RECOVERY_STORE", env)
        self.assertNotIn("LINTEL_HOME", env)
        return base, source, target, env

    def native_snapshot(self, root):
        native = adapter.native_io_path(root)
        return {path.relative_to(native).as_posix():
                (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mode)
                for path in native.rglob("*") if path.is_file() and not path.is_symlink()}

    def long_metadata_root(self):
        padding = 256 - len(str(self.target)) - len("\\metadata-")
        self.assertGreater(padding, 0, "Keep the declared fixture depth; do not relocate a long parent.")
        root = self.target / ("metadata-" + "x" * padding)
        adapter.native_io_path(root).mkdir()
        self.assertEqual(len(str(root)), 256)
        return root

    def test_long_protocol_metadata_preserves_prose_eol_and_modified_block_refusal(self):
        target = self.long_metadata_root()
        payload = adapter.read_file(self.source, "scaffolding/01-foundation/SESSION-PROTOCOL.md").strip()
        block = adapter.PROTOCOL_START + b"\n" + payload + b"\n" + adapter.PROTOCOL_END
        original = b"User prose before.\r\n" + block.replace(b"\n", b"\r\n") + b"\r\nUser prose after.\r\n"
        agents = adapter.native_io_path(target / "AGENTS.md")
        agents.write_bytes(original)
        seeds = {"AGENTS.md": b"not the existing user prose\n", "CLAUDE.md": b"fresh seed\n"}
        old = {"AGENTS.md": adapter.digest(block)}
        before = self.native_snapshot(target)
        updates, hashes, errors = adapter.protocol_updates(self.source, target, seeds, old, False)
        self.assertEqual(errors, [])
        self.assertTrue(updates["AGENTS.md"].startswith(b"User prose before.\r\n"))
        self.assertTrue(updates["AGENTS.md"].endswith(b"\r\nUser prose after.\r\n"))
        self.assertEqual(hashes["AGENTS.md"], old["AGENTS.md"])
        self.assertEqual(self.native_snapshot(target), before)
        agents.write_bytes(original.replace(b"## ", b"## User changed ", 1))
        edited = self.native_snapshot(target)
        _, _, errors = adapter.protocol_updates(self.source, target, seeds, old, False)
        self.assertIn("Modified session protocol block (preserved): AGENTS.md", errors)
        self.assertEqual(self.native_snapshot(target), edited)

    def test_long_generated_link_metadata_checks_real_missing_and_linked_targets(self):
        target = self.long_metadata_root()
        guide = adapter.native_io_path(target / "user-guide.md")
        guide.write_bytes(b"User-owned guide.\n")
        files = {".github/skills/li-sense/SKILL.md": b"[Guide](../../../user-guide.md)\n"}
        before = self.native_snapshot(target)
        self.assertEqual(adapter.verify_links(files, target), [])
        self.assertEqual(self.native_snapshot(target), before)
        guide.unlink()
        self.assertEqual(adapter.verify_links(files, target),
                         ["Missing generated link: .github/skills/li-sense/SKILL.md -> ../../../user-guide.md"])
        outside = self.base / "outside-guide.md"
        outside.write_bytes(b"Outside selected target.\n")
        os.symlink(outside, guide)
        with self.assertRaisesRegex(ValueError, "Symlink/reparse"):
            adapter.verify_links(files, target)
        self.assertEqual(outside.read_bytes(), b"Outside selected target.\n")

    def test_long_public_directory_index_is_selected_from_the_real_source(self):
        source = self.long_metadata_root()
        shutil.copytree(self.source, adapter.native_io_path(source), dirs_exist_ok=True)
        readme = adapter.native_io_path(source / "README.md")
        readme.write_bytes(readme.read_bytes() + b"\n[Long directory index](docs/native-path-index/)\n")
        index = adapter.native_io_path(source / "docs/native-path-index/README.md")
        index.parent.mkdir()
        index.write_bytes(b"# Real selected directory index\n")
        before = self.native_snapshot(source)
        files, seeds, mode = adapter.generate(source, self.target)
        self.assertEqual(mode, "vendored")
        self.assertEqual(files[".github/lintel/docs/native-path-index/README.md"], index.read_bytes())
        self.assertEqual(adapter.verify_links({**files, **seeds}, self.target), [])
        self.assertEqual(self.native_snapshot(source), before)
        index.unlink()
        files, seeds, _ = adapter.generate(source, self.target)
        self.assertTrue(any("docs/native-path-index/" in error
                            for error in adapter.verify_links({**files, **seeds}, self.target)))

    def _git_fixture(self):
        home, self._git_caller, temporary = (self.target / name for name in ("home", "caller", "temp"))
        for path in (home, self._git_caller, temporary):
            path.mkdir()
            (path / "unrelated-sentinel.txt").write_bytes(b"Retain this fixture-owned sentinel.\r\n")
        self._git_empty_path = temporary / "no-git"
        self._git_empty_path.mkdir()
        self._git_env = {key: os.environ[key] for key in
                         ("SystemRoot", "WINDIR", "COMSPEC", "SYSTEMDRIVE", "PATHEXT", "PATH")
                         if key in os.environ}
        self._git_env.update({
            "HOME": str(home), "USERPROFILE": str(home), "HOMEDRIVE": home.drive,
            "HOMEPATH": str(home)[len(home.drive):],
            "APPDATA": str(home / "AppData/Roaming"), "LOCALAPPDATA": str(home / "AppData/Local"),
            "XDG_CONFIG_HOME": str(home / ".config"), "XDG_CACHE_HOME": str(home / ".cache"),
            "XDG_DATA_HOME": str(home / ".local/share"), "XDG_STATE_HOME": str(home / ".local/state"),
            "TEMP": str(temporary), "TMP": str(temporary), "TMPDIR": str(temporary),
            "CLAUDE_CONFIG_DIR": str(home / ".claude"), "COPILOT_HOME": str(home / ".copilot"),
            "GSTACK_STATE_DIR": str(home / ".gstack"),
            "LINTEL_SOURCE_ROOT": str(self.source), "LINTEL_REPO_ROOT": str(self._git_caller),
            "LINTEL_HOME": str(home / "lintel"), "LINTEL_PACKS_DIR": str(home / "lintel/packs"),
            "LINTEL_ACTIVE_PACK_FILE": str(home / "lintel/packs/active-pack"),
            "LINTEL_AUDIT_DIR": str(self._git_caller / ".claude/runtime/audit"),
            "LINTEL_JOBS_DIR": str(self._git_caller / ".claude/runtime/jobs"),
            "LINTEL_JOBS_ACTIVE": str(self._git_caller / ".claude/runtime/jobs/_active.md"),
            "LINTEL_JOBS_ARCHIVE": str(self._git_caller / ".claude/runtime/jobs/_archive"),
            "LINTEL_JOBS_REGISTRY": str(home / "lintel/jobs/_active.md"),
            "LINTEL_PRIVATE_ROLES_DIR": str(home / "lintel/private/roles"),
            "PACK_CACHE_FILE": str(home / "lintel/cache.json"), "LINTEL_JOBS_NO_INIT": "1",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(home / ".gitconfig"),
            "GIT_TERMINAL_PROMPT": "0", "GIT_AUTHOR_NAME": "Synthetic fixture",
            "GIT_COMMITTER_NAME": "Synthetic fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid", "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
        })
        self._git_executable = shutil.which("git", path=self._git_env["PATH"])
        self.assertTrue(self._git_executable, "Real Git is required; an unavailable control is not a skip.")
        version = self._git_run([self._git_executable, "--version"])
        self.assertEqual(version.returncode, 0, version.stderr)
        self._git_version = version.stdout.strip()

    def _git_run(self, argv, env=None):
        env = env or self._git_env
        nonpaths = {"LINTEL_JOBS_NO_INIT"}
        for key, value in env.items():
            if (key.startswith(("LINTEL_", "XDG_")) and key not in nonpaths) or key in (
                    "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "TMPDIR",
                    "CLAUDE_CONFIG_DIR", "COPILOT_HOME", "GSTACK_STATE_DIR", "PACK_CACHE_FILE",
                    "GIT_CONFIG_GLOBAL"):
                self.assertTrue(Path(value).is_relative_to(self.base), (key, value))
        home, caller = Path(env["LINTEL_HOME"]), Path(env["LINTEL_REPO_ROOT"])
        for path in (home / "profile.yaml", home / "sessions/profiles", home / "audit",
                     caller / ".claude/runtime", caller / ".claude/runtime/profiles"):
            self.assertTrue(path.is_relative_to(self.base), path)
        self.assertNotIn("LINTEL_RECOVERY_STORE", env)
        self.assertTrue(self._git_caller.is_relative_to(self.base))
        return subprocess.run(argv, cwd=self._git_caller, env=env, text=True, encoding="utf-8",
                              capture_output=True, timeout=300)

    def _git_fixture_state(self):
        native = adapter.native_io_path(self.base)
        return {path.relative_to(native).as_posix():
                (path.lstat().st_mode, hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)
                for path in (native, *native.rglob("*"))}

    def _git_operation(self, target, command, *, installed=False, available=True, expected=None):
        from managed_transaction import default_store

        self.assertTrue(target.is_relative_to(self.base))
        store = default_store(target)
        self.assertTrue(store.is_relative_to(self.base))
        source = target / adapter.BUNDLE if installed else self.source
        env = dict(self._git_env, LINTEL_SOURCE_ROOT=str(source))
        if not available:
            env["PATH"] = str(self._git_empty_path)
        before = self._git_fixture_state()
        git_required = adapter.native_io_path(target / ".git").exists()
        observed = None
        if available:
            argv = [self._git_executable, "-c", "core.fsmonitor=false", "-C", str(target),
                    "check-ignore", "--no-index", "--quiet", ".claude/runtime/.lintel-ignore-check"]
            if git_required:
                observed = self._git_run(argv, env)
                if expected == "error":
                    self.assertNotIn(observed.returncode, (0, 1), observed.stdout + observed.stderr)
                elif expected is not None:
                    self.assertEqual(observed.returncode, expected, observed.stdout + observed.stderr)
        else:
            lookup = self._git_run([sys.executable, "-I", "-B", "-c",
                                   "import shutil; print(shutil.which('git'))"], env)
            self.assertEqual((lookup.returncode, lookup.stdout), (0, "None\n"), lookup.stderr)
        self.assertEqual(self._git_fixture_state(), before, "The independent producer must be read-only.")
        ignore = adapter.native_io_path(target / ".gitignore")
        original_ignore = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
        has_rule = ".claude/runtime/" in original_ignore.splitlines()
        verification_error = git_required and (not available or observed.returncode not in (0, 1))
        negated = git_required and available and observed.returncode == 1 and has_rule
        missing = command == "check" and not has_rule
        failure = verification_error or negated or missing
        result = self._git_run(
            [sys.executable, "-B", str(source / "bin/li-copilot.py"), command,
             "--target", str(target), "--source", str(source)], env)
        after = self._git_fixture_state()
        state_hash = lambda state: hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
        changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
        print(json.dumps({
            "git_version": self._git_version, "target": str(target),
            "lengths": [len(str(target)), len(str(target / ".git"))],
            "producer": {"argv": observed.args, "exit": observed.returncode, "stdout": observed.stdout,
                         "stderr": observed.stderr} if observed is not None else
                        {"available": available, "required": git_required},
            "adapter": {"argv": result.args, "exit": result.returncode,
                        "stdout": result.stdout, "stderr": result.stderr},
            "state_before": state_hash(before), "state_after": state_hash(after),
            "all_paths_bytes_modes_preserved": before == after, "changed_paths": changed,
            "head_index_config": {path: value for path, value in before.items()
                                 if "/.git/" in path and Path(path).name in ("HEAD", "index", "config")},
        }))
        self.assertNotIn("Traceback", result.stderr)
        if failure:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(after, before, "Refusal must precede target, inventory, receipt and store writes.")
            if verification_error:
                if available:
                    self.assertIn("Git ignore verification failed", result.stderr)
                    self.assertIn(f"exit {observed.returncode}", result.stderr)
                    if observed.stderr.strip():
                        self.assertIn(observed.stderr.strip(), result.stderr)
                else:
                    self.assertIn("Git ignore verification unavailable", result.stderr)
                    self.assertIn("git executable not found", result.stderr)
                self.assertIn(str(target), result.stderr)
                self.assertNotIn("review conflicting ignore rules", result.stderr)
            elif negated:
                self.assertIn("Git does not confirm", result.stderr)
            else:
                self.assertIn("Missing .claude/runtime/ ignore rule", result.stderr)
        else:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Lintel kit verified:" if command == "check" else "Lintel kit ready:", result.stdout)
            if command == "check":
                self.assertEqual(after, before)
            else:
                allowed = tuple(path.relative_to(self.base).as_posix() for path in (target, store))
                protected = lambda path: not any(path == prefix or path.startswith(prefix + "/") for prefix in allowed)
                self.assertEqual({key: value for key, value in after.items() if protected(key)},
                                 {key: value for key, value in before.items() if protected(key)})
                entry = (target / ".git").relative_to(self.base).as_posix()
                self.assertEqual({key: value for key, value in after.items() if key == entry or key.startswith(entry + "/")},
                                 {key: value for key, value in before.items() if key == entry or key.startswith(entry + "/")})
                for name in ("staged.txt", "unstaged.txt", "untracked.txt"):
                    key = (target / name).relative_to(self.base).as_posix()
                    self.assertEqual(after.get(key), before.get(key), name)
                self.assertTrue(ignore.read_text(encoding="utf-8").startswith(original_ignore))
                self.assertIn(".claude/runtime/", ignore.read_text(encoding="utf-8").splitlines())
                self.assertTrue(adapter.native_io_path(target / adapter.INVENTORY).is_file())
        return observed

    def test_long_git_metadata_runs_real_effective_ignore_validation(self):
        self._git_fixture()
        target = self.long_metadata_root()
        shallow = self.target / "git-source"
        shallow.mkdir()
        initialized = self._git_run([self._git_executable, "init", "--quiet", str(shallow)])
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        for name in ("staged.txt", "unstaged.txt"):
            (shallow / name).write_bytes(b"Original indexed bytes.\r\n")
        added = self._git_run([self._git_executable, "-C", str(shallow), "add", "--", "staged.txt", "unstaged.txt"])
        self.assertEqual(added.returncode, 0, added.stderr)
        (shallow / "unstaged.txt").write_bytes(b"Retain the unstaged edit.\r\n")
        (shallow / "untracked.txt").write_bytes(b"Retain the untracked file.\r\n")
        shutil.copytree(shallow, adapter.native_io_path(target), dirs_exist_ok=True)
        self.assertEqual((len(str(target)), len(str(target / ".git"))), (256, 261))
        self.assertTrue(adapter.native_io_path(target / ".git").is_dir())
        self.assertFalse(adapter.native_io_path(target / ".gitignore").exists())
        for content in (None, ".claude/runtime/\n",
                        ".claude/runtime/\n!.claude/runtime/\n!.claude/runtime/**\n"):
            if content is not None:
                adapter.native_io_path(target / ".gitignore").write_text(content, encoding="utf-8")
            for command in ("init", "check"):
                with self.subTest(command=command, ignore=content):
                    self._git_operation(target, command)
        adapter.native_io_path(target / ".gitignore").write_text(".claude/runtime/\n", encoding="utf-8")
        adapter.native_io_path(target / ".git/HEAD").write_bytes(b"not a Git HEAD\n")
        for command in ("init", "check"):
            with self.subTest(command=command, invalid_git=True):
                self._git_operation(target, command, expected="error")
        print(json.dumps({"long_linked_worktree_positive": "UNVERIFIED; no setup or compatibility retry attempted"}))

    def test_git_verification_directory_linked_and_plain_folder_controls(self):
        self._git_fixture()
        main, linked, plain = (self.base / name for name in ("git-main", "git-linked-control", "git-plain-control"))
        main.mkdir()
        initialized = self._git_run([self._git_executable, "init", "--quiet", str(main)])
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        for name in ("staged.txt", "unstaged.txt"):
            (main / name).write_bytes(b"Committed fixture content.\r\n")
        added = self._git_run([self._git_executable, "-C", str(main), "add", "--", "staged.txt", "unstaged.txt"])
        self.assertEqual(added.returncode, 0, added.stderr)
        committed = self._git_run([self._git_executable, "-C", str(main), "commit", "--quiet",
                                   "-m", "fixture: seed supported Git controls"])
        self.assertEqual(committed.returncode, 0, committed.stderr)
        config = (main / ".git/config").read_bytes()
        setup = self._git_run([self._git_executable, "-C", str(main), "worktree", "add", "--detach", str(linked), "HEAD"])
        self.assertEqual(setup.returncode, 0, setup.stdout + setup.stderr)
        self.assertEqual((main / ".git/config").read_bytes(), config)
        self.assertTrue((main / ".git").is_dir())
        self.assertTrue((linked / ".git").is_file())
        print(json.dumps({"supported_control_setup": setup.args, "exit": setup.returncode,
                          "controller_config_preserved": True, "not_long_linked_acceptance": True}))
        for root in (main, linked):
            before = self._git_fixture_state()
            identity = self._git_run([self._git_executable, "-c", "core.fsmonitor=false", "-C", str(root),
                                      "rev-parse", "--show-toplevel", "--absolute-git-dir"])
            self.assertEqual(identity.returncode, 0, identity.stderr)
            self.assertEqual(self._git_fixture_state(), before)
            top, git_dir_text = identity.stdout.splitlines()
            git_dir = Path(git_dir_text)
            self.assertTrue(root.samefile(Path(top)))
            self.assertTrue(git_dir.is_dir())
            if root == main:
                self.assertTrue(git_dir.samefile(root / ".git"))
            else:
                self.assertTrue(git_dir.is_relative_to(main / ".git/worktrees"))
            print(json.dumps({"supported_control_identity": identity.args, "top": top, "git_dir": git_dir_text,
                              "lengths": [len(str(root)), len(str(root / ".git")), len(str(git_dir))]}))
            (root / "staged.txt").write_bytes(b"Staged fixture edit.\r\n")
            added = self._git_run([self._git_executable, "-C", str(root), "add", "--", "staged.txt"])
            self.assertEqual(added.returncode, 0, added.stderr)
            (root / "unstaged.txt").write_bytes(b"Unstaged fixture edit.\r\n")
            (root / "untracked.txt").write_bytes(b"Untracked fixture bytes.\r\n")
            ignore = root / ".gitignore"
            ignore.write_text("# User ignores\n*.local\n", encoding="utf-8")
            self._git_operation(root, "check", expected=1)
            self._git_operation(root, "init", expected=1)
            self._git_operation(root, "check", installed=True, expected=0)
            valid = ignore.read_text(encoding="utf-8")
            ignore.write_text(valid + "!.claude/runtime/\n!.claude/runtime/**\n", encoding="utf-8")
            for command in ("init", "check"):
                with self.subTest(root=root.name, command=command, negated=True):
                    self._git_operation(root, command, installed=True, expected=1)
            ignore.write_text(valid, encoding="utf-8")
            head = git_dir / "HEAD"
            saved_head = head.read_bytes()
            head.write_bytes(b"invalid fixture HEAD\n")
            try:
                for command in ("init", "check"):
                    with self.subTest(root=root.name, command=command, invalid_git=True):
                        self._git_operation(root, command, installed=True, expected="error")
            finally:
                head.write_bytes(saved_head)
            for content in ("# Missing required rule\n", valid):
                ignore.write_text(content, encoding="utf-8")
                for command in ("init", "check"):
                    with self.subTest(root=root.name, command=command, unavailable_git=True, ignore=content):
                        self._git_operation(root, command, installed=True, available=False)
            ignore.write_text(valid, encoding="utf-8")
            self._git_operation(root, "check", installed=True, expected=0)
        plain.mkdir()
        (plain / ".gitignore").write_text("# Plain folder custom rule\n*.local\n", encoding="utf-8")
        self._git_operation(plain, "init", available=False)
        self._git_operation(plain, "check", installed=True, available=False)

    def default_cli(self, source, target, env, command="init", *, transaction=None, trace=None, success=True):
        argv = [str(source / "bin/li-adapter.py"), command, "--source", str(source), "--target", str(target)]
        if command == "init":
            argv += ["--client", "copilot-cli"]
        if transaction:
            argv += ["--transaction", transaction]
        if trace:
            observer = r'''
import json,runpy,sys
events=[]
def observe(event,values):
    if event == "os.rename":
        events.append([str(values[0]),str(values[1])])
sys.addaudithook(observe)
trace=sys.argv[1]
sys.argv=sys.argv[2:]
try:
    runpy.run_path(sys.argv[0],run_name="__main__")
finally:
    with open(trace,"x",encoding="utf-8") as handle:
        json.dump(events,handle)
'''
            argv = ["-c", observer, str(trace), *argv]
        result = subprocess.run([sys.executable, "-B", *argv], cwd=target, env=env,
                                text=True, encoding="utf-8", capture_output=True, timeout=300)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def test_original_default_113_128_paths_init_check_and_owned_recovery(self):
        base, source, target, env = self.default_consumer()
        before, source_before = self.native_snapshot(target), self.native_snapshot(source)
        trace = base / "actual-publication-operands.json"
        result = self.default_cli(source, target, env, trace=trace)
        match = re.search(r"Verified file transaction: (transaction-[a-f0-9]{32}); recovery store: ([^\r\n]+)",
                          result.stdout)
        self.assertIsNotNone(match, result.stdout)
        identifier, store = match.group(1), Path(match.group(2))
        self.assertEqual(store.parent, base)
        self.assertEqual(len(str(store)), 128)
        self.assertTrue(store.name.startswith(".lintel-recovery-"))
        pairs = [(str(Path(*adapter.path_identity(Path(first)))),
                  str(Path(*adapter.path_identity(Path(second)))))
                 for first, second in json.loads(trace.read_bytes())]
        blobs = [(first, second) for first, second in pairs
                 if ".pending-snapshot-" in first and Path(first).parent.name == "blobs"]
        self.assertIn((218, 260), [(len(first), len(second)) for first, second in blobs])
        installed = self.native_snapshot(target)
        inventory = json.loads((target / adapter.INVENTORY).read_bytes())
        self.assertIn(".github/lintel/lib/native_paths.py", inventory["files"])
        self.default_cli(target / adapter.BUNDLE, target, env, "check")
        self.default_cli(source, target, env)
        self.assertEqual(self.native_snapshot(target), installed)
        plan = json.loads((store / "transactions" / identifier / "plan.json").read_bytes())
        self.assertEqual(plan["owner"], str(target))
        self.assertEqual(plan["source"], str(source))
        published = (target / "AGENTS.md").read_bytes()
        recovery = json.loads(self.default_cli(source, target, env, "recover", transaction=identifier).stdout)
        self.assertEqual(recovery["state"], "recovered")
        self.assertEqual(recovery["store"], str(store))
        self.assertEqual(self.native_snapshot(target), before)
        (target / "AGENTS.md").write_bytes(published)
        edited = self.native_snapshot(target)
        self.default_cli(source, target, env, "recover", transaction=identifier, success=False)
        self.assertEqual(self.native_snapshot(target), edited)
        self.assertEqual(self.native_snapshot(source), source_before)
        print("Observed default dimensions: fixture=94 target=113 store=128; snapshot publication=218->260.")

    def test_canonical_default_caller_child_keeps_verified_parent_and_unbound_child(self):
        base, source, target, env = self.default_consumer()
        self.default_cli(source, target, env)
        bundle = target / adapter.BUNDLE
        for relative in ("bin/li-scaffold", "bin/li-lifecycle.py", "lib/native_paths.py",
                         "lib/context_safety.py", "lib/profile_context.py", "lib/managed_transaction.py"):
            self.assertEqual((bundle / relative).read_bytes(), adapter.source_bytes(source / relative))
        bash = shutil.which("bash")
        self.assertTrue(bash)
        home = target / ".claude/runtime/lintel-home"
        script = r'''set -euo pipefail
source .github/lintel/lib/copilot-env.sh
lintel_copilot_env "$PWD"
printf '%s\n' "$LINTEL_PROFILE_REFERENCE"
'''
        bound = subprocess.run([bash, "--noprofile", "--norc", "-c", script],
                               cwd=target, env=env, text=True, encoding="utf-8", capture_output=True, timeout=60)
        self.assertEqual(bound.returncode, 0, bound.stdout + bound.stderr)
        reference = json.loads(bound.stdout)
        self.assertEqual(reference["generation"], 1)
        parent_before, home_before = self.native_snapshot(target), self.native_snapshot(home)
        source_before, user_before = self.native_snapshot(source), self.native_snapshot(Path(env["USERPROFILE"]))
        child = base / "child consumer"
        child.mkdir()
        (child / "unrelated.txt").write_bytes(b"Child-owned data.\r\n")
        bridge = r'''set -euo pipefail
source .github/lintel/lib/copilot-env.sh
lintel_copilot_env "$PWD"
bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" init --target "$1"
'''
        result = subprocess.run([bash, "--noprofile", "--norc", "-c", bridge, "caller-child", str(child)],
                                cwd=target, env=env, text=True, encoding="utf-8", capture_output=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(value["operation_profile_reference"], reference)
        self.assertIsNone(value["target_profile_reference"])
        self.assertFalse(value["required_caller_policy"])
        self.assertEqual(self.native_snapshot(target), parent_before)
        self.assertEqual(self.native_snapshot(home), home_before)
        self.assertEqual(self.native_snapshot(source), source_before)
        self.assertEqual(self.native_snapshot(Path(env["USERPROFILE"])), user_before)
        self.assertEqual((child / "unrelated.txt").read_bytes(), b"Child-owned data.\r\n")
        self.assertFalse((child / ".claude/runtime/profiles").exists())
        self.assertFalse((child / ".claude/runtime/lintel-home").exists())
        self.assertFalse((child / ".claude/profile-requirements.json").exists())
        self.assertFalse((child / "packs").exists())
        history = [path for path in adapter.native_io_path(home).rglob("*.json") if path.parent.name == "history"]
        self.assertTrue(history)
        print("Observed canonical default caller/child; longest retained history path:",
              max(len(str(Path(*adapter.path_identity(path)))) for path in history))

    def test_canonical_required_caller_policy_refuses_missing_drifted_and_conflicting_context(self):
        base, source, target, env = self.default_consumer()
        self.default_cli(source, target, env)
        home = target / ".claude/runtime/lintel-home"
        for name in ("strict", "different"):
            pack = home / "packs" / name / "pack.yaml"
            pack.parent.mkdir(parents=True)
            pack.write_text(
                f"name: {name}\nversion: 1.0.0\nvoice: {{default_tier: internal}}\n"
                "compliance: {mode: hard}\nnavigation: {default_workflow: cycle}\n", encoding="utf-8")
        (target / ".claude/profile-requirements.json").write_text(
            json.dumps({"schema_version": 1, "required_pack": "strict"}), encoding="utf-8")
        bash = shutil.which("bash")
        self.assertTrue(bash)
        bootstrap = r'''set -euo pipefail
source .github/lintel/lib/copilot-env.sh
lintel_copilot_env "$PWD"
'''
        bound = subprocess.run([bash, "--noprofile", "--norc", "-c",
                                bootstrap + 'printf \'%s\\n\' "$LINTEL_PROFILE_REFERENCE"\n'],
                               cwd=target, env=env, text=True, encoding="utf-8", capture_output=True, timeout=60)
        self.assertEqual(bound.returncode, 0, bound.stdout + bound.stderr)
        reference = json.loads(bound.stdout)
        self.assertEqual(reference["name"], "strict")
        bridge = bootstrap + 'bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" init --target "$1"\n'

        def run_child(name, *, required=None, success=True, resolver_failure=False):
            child = base / name
            child.mkdir()
            (child / "unrelated.txt").write_bytes(b"Retain child-owned bytes.\n")
            if required:
                (child / ".claude").mkdir()
                (child / ".claude/profile-requirements.json").write_text(
                    json.dumps({"schema_version": 1, "required_pack": required}), encoding="utf-8")
            before = self.native_snapshot(child)
            parent_before, home_before = self.native_snapshot(target), self.native_snapshot(home)
            source_before = self.native_snapshot(source)
            user_before = self.native_snapshot(Path(env["USERPROFILE"]))
            audit_relative = ".claude/runtime/audit/pack-resolver.jsonl"
            audit_path = target / audit_relative
            audit_before = audit_path.read_bytes() if audit_path.exists() else b""
            result = subprocess.run([bash, "--noprofile", "--norc", "-c", bridge, "caller-child", str(child)],
                                    cwd=target, env=env, text=True, encoding="utf-8", capture_output=True, timeout=120)
            parent_after = self.native_snapshot(target)
            if resolver_failure:
                # The accepted shell bootstrap audits refusal without changing the caller pin or home.
                audit_after = audit_path.read_bytes()
                self.assertTrue(audit_after.startswith(audit_before))
                record, = [json.loads(line) for line in audit_after[len(audit_before):].splitlines()]
                self.assertEqual(record["kind"], "pack_resolver_fail")
                self.assertEqual(record["msg"], "operation=bootstrap profile-context-unresolved")
                if audit_relative in parent_before:
                    self.assertEqual(parent_after[audit_relative][1], parent_before[audit_relative][1])
                parent_before.pop(audit_relative, None)
                parent_after.pop(audit_relative)
            self.assertEqual(parent_after, parent_before)
            self.assertEqual(self.native_snapshot(home), home_before)
            self.assertEqual(self.native_snapshot(source), source_before)
            self.assertEqual(self.native_snapshot(Path(env["USERPROFILE"])), user_before)
            self.assertFalse((child / ".claude/runtime/profiles").exists())
            self.assertFalse((child / ".claude/runtime/lintel-home").exists())
            self.assertFalse((child / "packs").exists())
            if success:
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                value = json.loads(result.stdout)
                self.assertTrue(value["required_caller_policy"])
                self.assertEqual(value["operation_profile_reference"], reference)
                self.assertIsNone(value["target_profile_reference"])
                self.assertEqual(value["target_selection"]["requested"], "strict")
                self.assertEqual((child / "unrelated.txt").read_bytes(), b"Retain child-owned bytes.\n")
                self.assertEqual((child / ".claude/profile-requirements.json").exists(), bool(required))
            else:
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(result.stdout, "")
                self.assertEqual(self.native_snapshot(child), before)
            return result

        run_child("neutral child")
        run_child("matching child", required="strict")
        run_child("conflicting child", required="different", success=False)
        current, = adapter.native_io_path(home).rglob("current-profile.json")
        pin = current.read_bytes()
        current.unlink()
        try:
            missing = run_child("missing caller", success=False, resolver_failure=True)
            self.assertIn("PROFILE_", missing.stderr)
            self.assertFalse(current.exists())
        finally:
            current.write_bytes(pin)
        manifest = home / "packs/strict/pack.yaml"
        content, times = manifest.read_bytes(), manifest.stat()
        manifest.write_bytes(content + b"# same-mtime required policy drift\n")
        os.utime(manifest, ns=(times.st_atime_ns, times.st_mtime_ns))
        try:
            drifted = run_child("drifted caller", success=False, resolver_failure=True)
            self.assertIn("PROFILE_", drifted.stderr)
        finally:
            manifest.write_bytes(content)
            os.utime(manifest, ns=(times.st_atime_ns, times.st_mtime_ns))
        run_child("retained caller")

    def _scaffold_state(self, root):
        native = adapter.native_io_path(root)
        if not native.exists():
            return None
        return {path.relative_to(native).as_posix(): [
            path.lstat().st_mode, getattr(path.lstat(), "st_file_attributes", 0),
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
        ] for path in (native, *native.rglob("*"))}

    def _scaffold_fixture(self):
        base, source, caller, env = self.default_consumer()
        self.default_cli(source, caller, env)
        bundle = caller / adapter.BUNDLE
        for relative in ("bin/li-scaffold", "bin/li-lifecycle", "bin/li-lifecycle.py",
                         "lib/context_safety.py", "lib/managed_transaction.py", "lib/profile_context.py"):
            self.assertEqual((bundle / relative).read_bytes(), adapter.source_bytes(source / relative))
        bash = shutil.which("bash")
        self.assertTrue(bash)
        bootstrap = ('set -euo pipefail\nsource .github/lintel/lib/copilot-env.sh\n'
                     'lintel_copilot_env "$PWD"\n')
        result = subprocess.run([bash, "--noprofile", "--norc", "-c",
                                 bootstrap + "printf '%s\\n' \"$LINTEL_PROFILE_REFERENCE\"\n"],
                                cwd=caller, env=env, text=True, encoding="utf-8", capture_output=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        reference = json.loads(result.stdout)
        self.assertEqual(reference["generation"], 1)
        home = caller / ".claude/runtime/lintel-home"
        history = [path for path in adapter.native_io_path(home).rglob("*.json")
                   if path.parent.name == "history"]
        self.assertEqual(max(len(str(Path(*adapter.path_identity(path)))) for path in history), 304)
        return base, source, caller, env, bash, bootstrap, reference

    def _scaffold_seed(self, child):
        seeds = {
            "AGENTS.md": b"Consumer-owned AGENTS prose.\r\n",
            "CLAUDE.md": b"Consumer-owned CLAUDE prose.\r\n",
            ".claude/memory/lessons.md": b"Consumer-owned durable lessons.\r\n",
            ".claude/memory/MEMORY.md": b"Consumer-owned memory index.\r\n",
            ".claude/rules/README.md": b"Consumer-owned rules.\r\n",
            ".claude/settings.local.json":
                b'{"custom":"consumer-owned","autoMemoryDirectory":"preserve-or-update-only-this"}\r\n',
            ".claude/lintel-layout.yaml": b"layout_version: 5\n# Preserve this consumer comment.\n",
            ".gitignore": b"# Consumer ignore policy\r\n.claude/runtime/\r\n.claude/settings.local.json\r\n",
            "unrelated.txt": b"Unrelated consumer file.\r\n",
        }
        for relative, data in seeds.items():
            path = adapter.native_io_path(child / relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        return seeds

    def _scaffold_call(self, fixture, child, *arguments, success=True, intercept=None):
        base, source, caller, env, bash, bootstrap, reference = fixture
        self.assertNotIn("LINTEL_RECOVERY_STORE", env)
        self.assertNotIn("LINTEL_HOME", env)
        self.assertFalse(adapter.native_io_path(child / ".git").exists())
        protected = (source, caller, Path(env["USERPROFILE"]))
        before = [self._scaffold_state(path) for path in protected]
        if intercept is None:
            command = bootstrap + 'bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" "$@"\n'
            argv = [bash, "--noprofile", "--norc", "-c", command, "installed-scaffold", *arguments,
                    "--target", str(child)]
        else:
            command = bootstrap + r'''
python="$1"; observer="$2"; child="$3"; relative="$4"; operation="$5"; phase="$6"; shift 6
"$python" -I -B -c "$observer" "$LINTEL_SOURCE_ROOT" "$relative" "$operation" "$phase" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" --home "$LINTEL_HOME" \
  --packs "$LINTEL_PACKS_DIR" --pointer "${LINTEL_ACTIVE_PACK_FILE:-$LINTEL_PACKS_DIR/active-pack}" \
  --context "${LINTEL_PROFILE_CONTEXT:-}" --context-file "${LINTEL_PROFILE_CONTEXT_FILE:-}" \
  --reference "$LINTEL_PROFILE_REFERENCE" --profile-pack "${LINTEL_PROFILE_PACK:-}" \
  scaffold "$@" --target "$child"
'''
            relative, operation, *phases = intercept
            phase = phases[0] if phases else "producer"
            observer = r'''
import hashlib, importlib.util, json, sys
from pathlib import Path
source, relative, operation, phase = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
sys.path.insert(0, str(source / "lib"))
from context_safety import native_io_path, safe_path
spec = importlib.util.spec_from_file_location("observed_lifecycle", source / "bin/li-lifecycle.py")
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
def mutate(target):
    path = native_io_path(safe_path(target, relative))
    if operation == "delete":
        path.unlink()
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"layout_version: 4\n# Intervening marker.\n" if operation == "marker"
                         else b"Intervening consumer-owned bytes.\r\n")
    root = native_io_path(target)
    state = {entry.relative_to(root).as_posix(): [
        entry.lstat().st_mode, getattr(entry.lstat(), "st_file_attributes", 0),
        hashlib.sha256(entry.read_bytes()).hexdigest() if entry.is_file() else None,
    ] for entry in (root, *root.rglob("*"))}
    print("F02_INTERVENING_STATE=" + json.dumps(state, sort_keys=True), file=sys.stderr)
if phase == "producer":
    publication = module.runtime_publication
    def intervene(config, args, *positional, **keywords):
        mutate(config.repo)
        return publication(config, args, *positional, **keywords)
    module.runtime_publication = intervene
else:
    import managed_transaction
    publication = managed_transaction.apply_files
    def intervene(root, *positional, **keywords):
        mutate(root)
        return publication(root, *positional, **keywords)
    managed_transaction.apply_files = intervene
sys.argv = ["li-lifecycle", *sys.argv[5:]]
raise SystemExit(module.main())
'''
            argv = [bash, "--noprofile", "--norc", "-c", command, "observed-scaffold",
                    sys.executable, observer, str(child), relative, operation, phase, *arguments]
        result = subprocess.run(argv, cwd=caller, env=env, text=True, encoding="utf-8",
                                capture_output=True, timeout=180)
        self.assertEqual([self._scaffold_state(path) for path in protected], before,
                         "The installed caller, pin/history, source and synthetic personal home must be unchanged.")
        for relative in (".claude/runtime/profiles", ".claude/runtime/lintel-home",
                         ".claude/profile-requirements.json", "packs"):
            self.assertFalse(adapter.native_io_path(child / relative).exists(), relative)
        print(json.dumps({"case": self._testMethodName, "child": str(child), "length": len(str(child)),
                          "arguments": list(arguments), "interception": intercept,
                          "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}))
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(value["operation_profile_reference"], reference)
            self.assertIsNone(value["target_profile_reference"])
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout, "")
        return result

    def test_installed_scaffold_preserves_seeded_short_and_long_plain_targets(self):
        from managed_transaction import default_store

        fixture = self._scaffold_fixture()
        base = fixture[0]
        for name, length, seeded in (("short seeded consumer", 116, True),
                                     ("long-seeded-", 256, True), ("long-absent-", 256, False)):
            child = base / (name + "x" * (length - len(str(base)) - 1 - len(name)))
            adapter.native_io_path(child).mkdir()
            self.assertEqual(len(str(child)), length)
            seeds = self._scaffold_seed(child) if seeded else {}
            before = self._scaffold_state(child)
            store = default_store(child)
            self.assertFalse(adapter.native_io_path(store).exists())
            for arguments in (("check",), ("init", "--dry-run")):
                preview = json.loads(self._scaffold_call(fixture, child, *arguments).stdout)
                self.assertEqual(preview["state"], "preview")
                self.assertEqual(self._scaffold_state(child), before)
                self.assertFalse(adapter.native_io_path(store).exists())
                for relative in seeds.keys() - {".claude/settings.local.json"}:
                    with self.subTest(length=length, arguments=arguments, relative=relative):
                        self.assertNotIn(relative, preview["changes"])
            self._scaffold_call(fixture, child, "init")
            published = self._scaffold_state(child)
            print(json.dumps({"case": "seeded-foundation-bytes", "length": length, "target": str(child),
                              "before": before, "after": published}))
            for relative, data in seeds.items():
                actual = adapter.native_io_path(child / relative).read_bytes()
                if relative == ".claude/settings.local.json":
                    data = data.replace(b'"preserve-or-update-only-this"',
                                        json.dumps(str(child / ".claude/memory")).encode("utf-8"))
                with self.subTest(length=length, relative=relative, seeded=seeded):
                    self.assertEqual(actual, data, relative)
                    self.assertEqual(published[relative][:2], before[relative][:2], relative)
            for relative in ("AGENTS.md", "CLAUDE.md", ".claude/memory/MEMORY.md",
                             ".claude/memory/lessons.md", ".claude/rules/README.md"):
                self.assertTrue(adapter.native_io_path(child / relative).is_file(), relative)
            stable, store_before = self._scaffold_state(child), self._scaffold_state(store)
            repeated = json.loads(self._scaffold_call(fixture, child, "init").stdout)
            self.assertEqual(repeated["state"], "unchanged")
            self.assertEqual(self._scaffold_state(child), stable)
            self.assertEqual(self._scaffold_state(store), store_before)
            if length == 256 and seeded:
                missing = child / "CLAUDE.md"
                adapter.native_io_path(missing).unlink()
                settings = child / ".claude/settings.local.json"
                adapter.native_io_path(settings).write_bytes(seeds[".claude/settings.local.json"])
                self._scaffold_call(fixture, child, "init", "--no-memory-pointer")
                self.assertTrue(adapter.native_io_path(missing).is_file())
                self.assertEqual(adapter.native_io_path(settings).read_bytes(), seeds[".claude/settings.local.json"])
                for relative in seeds.keys() - {"CLAUDE.md", ".claude/settings.local.json"}:
                    with self.subTest(mixed=relative):
                        self.assertEqual(adapter.native_io_path(child / relative).read_bytes(), seeds[relative], relative)

    def test_installed_scaffold_refuses_late_long_target_changes(self):
        from managed_transaction import default_store

        fixture = self._scaffold_fixture()
        base = fixture[0]
        planned_cases = (
            ("absent-seed", "AGENTS.md", "create"),
            ("absent-destination", ".claude/memory/lessons.md", "create"),
            ("ignore-edit", ".gitignore", "edit"), ("ignore-delete", ".gitignore", "delete"),
            ("settings-edit", ".claude/settings.local.json", "edit"),
            ("settings-delete", ".claude/settings.local.json", "delete"),
            ("legacy-edit", "tasks/lessons.md", "edit"), ("legacy-delete", "tasks/lessons.md", "delete"),
            ("existing-marker", ".claude/lintel-layout.yaml", "marker"),
            ("absent-marker", ".claude/lintel-layout.yaml", "marker"),
            ("migrating-marker", ".claude/lintel-layout.yaml", "marker"),
        )
        cases = [(name, relative, operation, "producer") for name, relative, operation in planned_cases]
        cases += [(name, relative, operation, "writer") for name, relative, operation in planned_cases
                  if name != "existing-marker"]
        for name, relative, operation, phase in cases:
            with self.subTest(case=name, phase=phase):
                prefix = "late-" + phase + "-" + name + "-"
                child = base / (prefix + "x" * (256 - len(str(base)) - 1 - len(prefix)))
                adapter.native_io_path(child).mkdir()
                self.assertEqual(len(str(child)), 256)
                self._scaffold_seed(child)
                if name == "absent-seed":
                    adapter.native_io_path(child / relative).unlink()
                if name.startswith("legacy-") or name == "absent-destination":
                    adapter.native_io_path(child / ".claude/memory/lessons.md").unlink()
                    legacy = adapter.native_io_path(child / "tasks/lessons.md")
                    legacy.parent.mkdir()
                    legacy.write_bytes(b"Original legacy knowledge.\r\n")
                if name.startswith("ignore-"):
                    adapter.native_io_path(child / ".gitignore").write_bytes(b"# Retain this merge input.\r\n")
                if name == "absent-marker":
                    adapter.native_io_path(child / relative).unlink()
                if name == "migrating-marker":
                    adapter.native_io_path(child / relative).write_bytes(b"layout_version: 4\n")
                store = default_store(child)
                self.assertFalse(adapter.native_io_path(store).exists())
                result = self._scaffold_call(fixture, child, "init", success=False,
                                             intercept=(relative, operation, phase))
                observed = next(line.removeprefix("F02_INTERVENING_STATE=")
                                for line in result.stderr.splitlines() if line.startswith("F02_INTERVENING_STATE="))
                self.assertEqual(self._scaffold_state(child), json.loads(observed))
                self.assertFalse(adapter.native_io_path(store).exists())
                self.assertRegex(result.stderr.lower(), r"changed|expected state")
                self.assertNotIn("Traceback", result.stderr)

    def test_post_admission_guard_change_is_preserved_without_atomicity_claim(self):
        fixture = self._scaffold_fixture()
        base = fixture[0]
        name = "unguarded-after-admission-"
        child = base / (name + "x" * (256 - len(str(base)) - 1 - len(name)))
        adapter.native_io_path(child).mkdir()
        self.assertEqual(len(str(child)), 256)
        seeds = self._scaffold_seed(child)
        result = self._scaffold_call(fixture, child, "init",
                                     intercept=(".claude/lintel-layout.yaml", "marker", "writer"))
        value = json.loads(result.stdout)
        self.assertEqual(value["state"], "complete")
        marker = adapter.native_io_path(child / ".claude/lintel-layout.yaml").read_bytes()
        self.assertEqual(marker, b"layout_version: 4\n# Intervening marker.\n")
        self.assertNotIn(".claude/lintel-layout.yaml", value["changed"])
        plan = json.loads(adapter.native_io_path(
            Path(value["store"]) / "transactions" / value["id"] / "plan.json").read_bytes())
        self.assertNotIn(".claude/lintel-layout.yaml", plan["files"])
        for relative, data in seeds.items():
            if relative == ".claude/lintel-layout.yaml":
                continue
            if relative == ".claude/settings.local.json":
                data = data.replace(b'"preserve-or-update-only-this"',
                                    json.dumps(str(child / ".claude/memory")).encode("utf-8"))
            else:
                self.assertNotIn(relative, plan["files"], relative)
            self.assertEqual(adapter.native_io_path(child / relative).read_bytes(), data, relative)
        print(json.dumps({"boundary": "POST_ADMISSION_GUARD_NOT_PROTECTED", "target": str(child),
                          "actual_exit": result.returncode, "state": value["state"],
                          "intervening_marker_preserved": True, "guard_absent_from_write_plan": True,
                          "limitation": "An unchanged input can change after final admission; no atomicity claimed."}))

    def test_interrupted_adapter_publication_requires_explicit_owned_recovery(self):
        (self.target / "AGENTS.md").write_bytes(b"Consumer-owned prose.\r\n")
        (self.target / "custom.json").write_bytes(b'{"owned":"consumer"}\n')
        before = self.snapshot()
        store = self.base / "adapter-interruption-store"
        script = r'''
import importlib.util,sys
from pathlib import Path
sys.dont_write_bytecode=True
source,target,store=map(Path,sys.argv[1:])
sys.path.insert(0,str(source/"lib"))
import managed_transaction as transaction
original=transaction._write_change
writes=[]
def interrupted(root,relative,data,mode,expected):
    original(root,relative,data,mode,expected)
    writes.append(relative)
    if len(writes)==1:
        raise OSError("synthetic failure after adapter publication")
transaction._write_change=interrupted
spec=importlib.util.spec_from_file_location("adapter",source/"bin/li-copilot.py")
adapter=importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
sys.argv=["li-copilot","init","--source",str(source),"--target",str(target),"--store",str(store)]
try:
    adapter.main()
except (ValueError,OSError) as error:
    print(error,file=sys.stderr)
    raise SystemExit(17)
'''
        result = subprocess.run([sys.executable, "-c", script, str(self.source), str(self.target), str(store)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 17, result.stdout + result.stderr)
        self.assertIn("synthetic failure", result.stderr)
        self.assertNotIn("Lintel kit ready", result.stdout)
        self.assertFalse((self.target / adapter.INVENTORY).exists())
        receipts = list((store / "transactions").iterdir())
        self.assertEqual(len(receipts), 1)
        identifier = receipts[0].name
        retry = subprocess.run([sys.executable, str(self.source / "bin/li-copilot.py"), "init",
                                "--source", str(self.source), "--target", str(self.target), "--store", str(store)],
                               capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(retry.returncode, 0, retry.stdout)
        self.assertIn("incomplete", retry.stderr.lower())
        recovered = subprocess.run([sys.executable, str(self.source / "bin/li-copilot.py"), "recover",
                                    "--source", str(self.source), "--target", str(self.target),
                                    "--store", str(store), "--transaction", identifier],
                                   capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
        self.assertEqual(self.snapshot(), before)
        self.run_cli()
        self.run_cli("check")

    def _f05_call(self, case, relative, operation, phase):
        store = case.parent / (case.name + "-store")
        self.assertFalse(store.exists())
        result = subprocess.run([sys.executable, "-c", F05_DRIVER, str(self.source), str(case), str(store),
                                 relative, operation, phase], capture_output=True, text=True, encoding="utf-8")
        return result, store

    def _f05_refused(self, case, relative, operation, phase, guard=False):
        before = self.snapshot(case)
        result, store = self._f05_call(case, relative, operation, phase)
        expected = dict(before)
        if operation == "delete":
            expected.pop(relative)
        else:
            expected[relative] = hashlib.sha256(F05_BYTES).hexdigest()
        after = self.snapshot(case)
        print("F05_CASE " + json.dumps({
            "test": self._testMethodName, "case": case.name, "relative": relative, "operation": operation,
            "phase": phase, "guard": guard, "exit": result.returncode, "ready": "Lintel kit ready" in result.stdout,
            "only_intervention_changed": after == expected, "store_absent": not store.exists()}, sort_keys=True))
        self.assertIn(f"F05_INTERVENTION={phase}:{operation}:{relative}", result.stderr)
        self.assertEqual(result.returncode, 17, result.stdout + result.stderr)
        self.assertNotIn("Lintel kit ready", result.stdout)
        message = ("Adapter input changed after planning (preserved): " if guard
                   else "Caller expected state does not match current bytes: ") + relative
        self.assertIn(message, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(after, expected)
        self.assertFalse(store.exists())

    def _f05_installed(self, root):
        root.mkdir()
        self.run_cli(target=root)
        start, stale, older = ".github/lintel/START.md", ".github/lintel/obsolete.md", b"# Older kit start\n"
        (root / start).write_bytes(older)
        (root / stale).write_bytes(b"# Retired kit page\n")
        inventory = json.loads((root / adapter.INVENTORY).read_text(encoding="utf-8"))
        inventory["files"][start] = hashlib.sha256(older).hexdigest()
        inventory["files"][stale] = hashlib.sha256(b"# Retired kit page\n").hexdigest()
        (root / adapter.INVENTORY).write_bytes(json.dumps(inventory, indent=2).encode("utf-8") + b"\n")
        return start, stale

    def test_f05_fresh_late_creations_refuse_before_publication(self):
        for index, relative in enumerate((".github/lintel/START.md", "AGENTS.md", ".claude/memory/lessons.md",
                                          ".gitignore", ".gitattributes", adapter.INVENTORY)):
            with self.subTest(relative=relative):
                case = self.target / f"c{index}"
                case.mkdir()
                self._f05_refused(case, relative, "create", "planned")

    def test_f05_consumer_late_input_changes_refuse(self):
        cases = (("AGENTS.md", "edit", "planned"), ("AGENTS.md", "delete", "planned"),
                 ("CLAUDE.md", "edit", "planned"), (".gitignore", "edit", "planned"),
                 (".gitignore", "delete", "planned"), (".gitattributes", "edit", "planned"),
                 (".gitattributes", "delete", "planned"), (".github/lintel/START.md", "create", "planned"),
                 ("AGENTS.md", "edit", "writer"), (".gitignore", "delete", "writer"))
        for index, (relative, operation, phase) in enumerate(cases):
            with self.subTest(relative=relative, operation=operation, phase=phase):
                case = self.target / f"c{index}"
                case.mkdir()
                for name, data in F05_CONSUMER.items():
                    (case / name).write_bytes(data)
                self._f05_refused(case, relative, operation, phase)

    def test_f05_installed_late_changes_and_guards_refuse(self):
        start, stale = self._f05_installed(self.target / "tpl")
        cases = ((start, "edit", "planned", False), (start, "delete", "planned", False),
                 (stale, "edit", "planned", False), (adapter.INVENTORY, "edit", "planned", False),
                 (adapter.INVENTORY, "delete", "planned", False), (F05_MANAGED, "edit", "planned", True),
                 (".claude/memory/lessons.md", "delete", "planned", True), (".gitignore", "edit", "planned", True),
                 ("AGENTS.md", "edit", "planned", True), (start, "edit", "writer", False),
                 (stale, "delete", "writer", False), (adapter.INVENTORY, "edit", "writer", False))
        for index, (relative, operation, phase, guard) in enumerate(cases):
            with self.subTest(relative=relative, operation=operation, phase=phase):
                case = self.target / f"c{index}"
                shutil.copytree(self.target / "tpl", case)
                self._f05_refused(case, relative, operation, phase, guard)

    def test_f05_post_admission_guard_is_a_labelled_limitation(self):
        start, _ = self._f05_installed(self.target / "tpl")
        case = self.target / "tpl"
        result, store = self._f05_call(case, F05_MANAGED, "edit", "writer")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"F05_INTERVENTION=writer:edit:{F05_MANAGED}", result.stderr)
        self.assertEqual((case / F05_MANAGED).read_bytes(), F05_BYTES)
        self.assertEqual((case / start).read_bytes(), adapter.generate(self.source, case)[0][start])
        check = self.run_cli("check", success=False, target=case)
        self.assertIn(f"Modified managed file (preserved): {F05_MANAGED}", check.stderr)
        print(json.dumps({"boundary": "POST_ADMISSION_GUARD_NOT_PROTECTED", "target": str(case),
                          "actual_exit": result.returncode, "intervening_guard_preserved": True,
                          "later_check_reports": "Modified managed file (preserved)",
                          "limitation": "An unchanged adapter input can change after final admission; no atomicity claimed."}))

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

    def test_review_closure_is_declared_and_missing_source_refuses_before_writes(self):
        declared = set(adapter.SWARM_RESOURCES + adapter.ADAPTER_RESOURCES)
        self.assertTrue(set(REVIEW_RUNTIME_RESOURCES) <= declared,
                        sorted(set(REVIEW_RUNTIME_RESOURCES) - declared))
        broken = self.base / "missing-review-source"
        shutil.copytree(self.source, broken)
        for index, relative in enumerate(REVIEW_RUNTIME_RESOURCES):
            with self.subTest(relative=relative):
                target = self.target / str(index)
                target.mkdir()
                (target / "user.txt").write_bytes(b"unaltered consumer evidence\r\n")
                before = self.snapshot(target)
                path = broken / relative
                content = path.read_bytes()
                path.unlink()
                try:
                    result = self.run_cli(source=broken, target=target, success=False)
                    self.assertIn(f"Required source file is missing: {path}", result.stderr)
                    self.assertEqual(self.snapshot(target), before)
                finally:
                    path.write_bytes(content)

    def test_installed_review_controls_use_real_schema_and_reject_required_failure(self):
        self.run_cli()
        bundle = self.target / adapter.BUNDLE
        review_controls(self, bundle, self.target)

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

    def test_installed_observation_helper_missing_refuses_before_target_reads(self):
        # F-INT-2: planning reads the target through context_safety; a missing
        # installed helper must be the clean source refusal, not an import crash.
        self.run_cli()
        bundle = self.target / adapter.BUNDLE
        helper = bundle / "lib/context_safety.py"
        content = helper.read_bytes()
        helper.unlink()
        before = self.snapshot()
        siblings = sorted(path.name for path in self.base.iterdir())
        try:
            for entry, arguments in (("li-copilot.py", ("check",)), ("li-copilot.py", ("init",)),
                                     ("li-adapter.py", ("init", "--client", "copilot-cli"))):
                with self.subTest(entry=entry, arguments=arguments):
                    result = subprocess.run(
                        [sys.executable, str(bundle / "bin" / entry), *arguments,
                         "--target", str(self.target), "--source", str(bundle)],
                        capture_output=True, text=True, encoding="utf-8")
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertEqual(result.stdout, "")
                    self.assertEqual(result.stderr, f"ERROR: Required source file is missing: {helper}\n")
                    self.assertEqual(before, self.snapshot())
                    self.assertEqual(siblings, sorted(path.name for path in self.base.iterdir()))
        finally:
            helper.write_bytes(content)
        self.run_cli("check", source=bundle, script=bundle / "bin/li-copilot.py")

    def test_joined_installed_profile_is_pinned_across_fresh_shells_and_detects_drift(self):
        # Keep the fixture's nested runtime paths inside native Windows path limits.
        target = self.base / "profile-consumer"
        target.mkdir()
        self.run_cli(target=target)
        home = self.base / "joined-profile-unused-home"
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(bash)
        profile_continuity(self, target / adapter.BUNDLE, target, home, bash)

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
