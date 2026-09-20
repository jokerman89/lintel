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

    def clone_project(self, project, clone):
        git = shutil.which("git")
        self.assertTrue(git, "Git is required for the real fresh navigation clone")
        env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                   GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")
        for arguments in (("init", "-q"), ("config", "core.autocrlf", "true"), ("add", "."),
                          ("-c", "user.name=Lintel Test", "-c", "user.email=lintel-test@example.invalid",
                           "-c", "commit.gpgsign=false", "commit", "-qm", "test: preserve bundled navigation",
                           "-m", "Co-authored-by: Copilot App <223556219+Copilot@users.noreply.github.com>"),
                          ("-c", "core.autocrlf=true", "clone", "-q", str(project), str(clone))):
            result = subprocess.run([git, *arguments], cwd=project, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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
        self.clone_project(self.target, clone)
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

    def test_c02_literal_html_dependencies_survive_init_check_and_clone(self):
        self.run_cli(client="other")
        source = self.target / ".github/lintel"
        faq = source / "docs/faq.md"
        with faq.open("a", encoding="utf-8") as output:
            output.write("\n[Public asset page](review-fixture/page.html)\n")
        fixture = source / "docs/review-fixture"
        fixture.mkdir()
        (fixture / "page.html").write_text(
            '<!doctype html>\n<html><body><script src="app.js"></script>\n'
            '<a title="1 > 0" href="guide.md">Guide</a></body></html>\n', encoding="utf-8")
        expected = {"app.js": b"window.fixture = true;", "guide.md": b"# Real local guide"}
        for name, content in expected.items():
            (fixture / name).write_bytes(content)
        consumer = self.base / "c02-consumer"
        consumer.mkdir()
        self.run_cli(client="other", source=source, target=consumer)
        self.run_cli("check", source=consumer / ".github/lintel", target=consumer)
        clone = self.base / "c02-clone"
        self.clone_project(consumer, clone)
        self.run_cli("check", source=clone / ".github/lintel", target=clone)
        for target in (consumer, clone):
            manifest = json.loads((target / ".github/lintel/manifest.json").read_text())["files"]
            for name, content in expected.items():
                relative = f".github/lintel/docs/review-fixture/{name}"
                self.assertEqual((target / relative).read_bytes(), content)
                self.assertEqual(manifest[relative], hashlib.sha256(content).hexdigest())
        for name, content in expected.items():
            with self.subTest(missing_source=name):
                (fixture / name).unlink()
                refused = self.base / ("c02-missing-" + name)
                refused.mkdir()
                (refused / "keep.txt").write_bytes(b"unchanged")
                result = self.run_cli(client="other", source=source, target=refused, success=False)
                self.assertIn(name, result.stderr)
                self.assertEqual([(p.name, p.read_bytes()) for p in refused.iterdir()], [("keep.txt", b"unchanged")])
                (fixture / name).write_bytes(content)
        bundle = clone / ".github/lintel"
        manifest_path = bundle / "manifest.json"
        original_manifest = manifest_path.read_bytes()
        for name, content in expected.items():
            with self.subTest(missing_installed=name):
                path = bundle / "docs/review-fixture" / name
                path.unlink()
                manifest = json.loads(original_manifest)
                del manifest["files"][f".github/lintel/docs/review-fixture/{name}"]
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                result = self.run_cli("check", source=bundle, target=clone, success=False)
                self.assertIn(name, result.stderr)
                self.assertFalse(path.exists())
                path.write_bytes(content)
                manifest_path.write_bytes(original_manifest)

    def test_c03_exact_markdown_escapes_and_wrapped_labels_in_real_consumers(self):
        self.run_cli(client="other")
        source = self.target / ".github/lintel"
        faq = source / "docs/faq.md"
        original = faq.read_text(encoding="utf-8")
        fixture = source / "docs/review-fixture"
        fixture.mkdir()
        guide = fixture / "a_b.md"
        guide.write_text("# Real local guide", encoding="utf-8")
        cases = (
            ("opener", r"\[Example, not a link](review-fixture/does-not-exist.md)", False),
            ("destination", r"[Guide](review-fixture/a\_b.md)", True),
            ("wrapped", "[Read the\nwrapped guide](review-fixture/a_b.md)", True),
        )
        for name, text, included in cases:
            with self.subTest(case=name):
                faq.write_text(original + "\n" + text + "\n", encoding="utf-8")
                consumer = self.base / ("c03-" + name)
                consumer.mkdir()
                (consumer / "keep.txt").write_bytes(b"unchanged")
                self.run_cli(client="other", source=source, target=consumer)
                bundle = consumer / ".github/lintel"
                self.run_cli("check", source=bundle, target=consumer)
                manifest = json.loads((bundle / "manifest.json").read_text())["files"]
                self.assertEqual((bundle / "docs/review-fixture/a_b.md").is_file(), included)
                self.assertEqual(".github/lintel/docs/review-fixture/a_b.md" in manifest, included)
                self.assertFalse((bundle / "docs/review-fixture/does-not-exist.md").exists())
                self.assertEqual((consumer / "keep.txt").read_bytes(), b"unchanged")
                if included:
                    guide.unlink()
                    refused = self.base / ("c03-missing-" + name)
                    refused.mkdir()
                    result = self.run_cli(client="other", source=source, target=refused, success=False)
                    self.assertIn("a_b.md", result.stderr)
                    self.assertEqual(list(refused.iterdir()), [])
                    guide.write_text("# Real local guide", encoding="utf-8")
        clone = self.base / "c03-clone"
        self.clone_project(consumer, clone)
        self.run_cli("check", source=clone / ".github/lintel", target=clone)
        self.assertEqual((clone / ".github/lintel/docs/review-fixture/a_b.md").read_bytes(), guide.read_bytes())

    def test_c04_titled_eof_reference_requires_guide_in_installed_clone(self):
        self.run_cli(client="other")
        source = self.target / ".github/lintel"
        faq = source / "docs/faq.md"
        original = faq.read_bytes()
        fixture = b'\n[Guide][p06-eof]\n\n[p06-eof]: review-fixture/guide.md "Title"'
        guide = source / "docs/review-fixture/guide.md"
        guide.parent.mkdir()
        guide.write_bytes(b"# Real local guide")
        expected_guides = set()
        for name, ending in (("eof", b""), ("lf", b"\n"), ("crlf", b"\r\n")):
            with self.subTest(ending=name):
                faq.write_bytes(original + fixture + ending)
                consumer = self.base / ("c04-" + name)
                consumer.mkdir()
                self.run_cli(client="other", source=source, target=consumer)
                bundle = consumer / ".github/lintel"
                self.run_cli("check", source=bundle, target=consumer)
                relative = ".github/lintel/docs/review-fixture/guide.md"
                manifest = json.loads((bundle / "manifest.json").read_text())["files"]
                self.assertIn(relative, manifest)
                self.assertEqual((consumer / relative).read_bytes(), b"# Real local guide")
                expected_guides.add(tuple(path for path in manifest if "review-fixture/" in path))
                clone = self.base / ("c04-clone-" + name)
                self.clone_project(consumer, clone)
                self.run_cli("check", source=clone / ".github/lintel", target=clone)
                self.assertEqual((clone / relative).read_bytes(), b"# Real local guide")
                (clone / relative).unlink()
                manifest_path = clone / ".github/lintel/manifest.json"
                document = json.loads(manifest_path.read_text())
                del document["files"][relative]
                manifest_path.write_text(json.dumps(document), encoding="utf-8")
                result = self.run_cli("check", source=clone / ".github/lintel", target=clone, success=False)
                self.assertIn("guide.md", result.stderr)
                self.assertFalse((clone / relative).exists())
                guide.unlink()
                refused = self.base / ("c04-missing-" + name)
                refused.mkdir()
                (refused / "keep.txt").write_bytes(b"unchanged")
                result = self.run_cli(client="other", source=source, target=refused, success=False)
                self.assertIn("guide.md", result.stderr)
                self.assertEqual([(path.name, path.read_bytes()) for path in refused.iterdir()],
                                 [("keep.txt", b"unchanged")])
                guide.write_bytes(b"# Real local guide")
                self.assertEqual(faq.read_bytes(), original + fixture + ending)
        self.assertEqual(len(expected_guides), 1, "A final newline must not change selected resources")

    def test_c05_quoted_code_is_not_a_dependency_but_real_guide_still_is(self):
        self.run_cli(client="other")
        source = self.target / ".github/lintel"
        faq = source / "docs/faq.md"
        original = faq.read_bytes()
        fixture = (
            b'>     [Code example](review-fixture/does-not-exist.md)\n\n'
            b'[Real guide](review-fixture/guide.md)\n'
        )
        guide = source / "docs/review-fixture/guide.md"
        guide.parent.mkdir()
        guide.write_bytes(b"# Real local guide")
        example = guide.with_name("does-not-exist.md")
        for name, present, content in (
                ("absent", False, fixture), ("present", True, fixture),
                ("unquoted", False, fixture.replace(b"> ", b"", 1))):
            with self.subTest(case=name):
                if present:
                    example.write_bytes(b"# Code-only example, not a dependency\n")
                elif example.exists():
                    example.unlink()
                faq.write_bytes(original + b"\n" + content)
                consumer = self.base / ("c05-" + name)
                consumer.mkdir()
                (consumer / "keep.txt").write_bytes(b"unchanged")
                self.run_cli(client="other", source=source, target=consumer)
                self.run_cli("check", source=consumer / ".github/lintel", target=consumer)
                clone = self.base / ("c05-clone-" + name)
                self.clone_project(consumer, clone)
                self.run_cli("check", source=clone / ".github/lintel", target=clone)
                for target in (consumer, clone):
                    bundle = target / ".github/lintel"
                    manifest = json.loads((bundle / "manifest.json").read_text())["files"]
                    self.assertIn(".github/lintel/docs/review-fixture/guide.md", manifest)
                    self.assertNotIn(".github/lintel/docs/review-fixture/does-not-exist.md", manifest)
                    self.assertEqual((bundle / "docs/review-fixture/guide.md").read_bytes(), b"# Real local guide")
                    self.assertFalse((bundle / "docs/review-fixture/does-not-exist.md").exists())
                self.assertEqual((consumer / "keep.txt").read_bytes(), b"unchanged")
                guide.unlink()
                refused = self.base / ("c05-missing-guide-" + name)
                refused.mkdir()
                (refused / "keep.txt").write_bytes(b"unchanged")
                result = self.run_cli(client="other", source=source, target=refused, success=False)
                self.assertIn("guide.md", result.stderr)
                self.assertEqual([(path.name, path.read_bytes()) for path in refused.iterdir()],
                                 [("keep.txt", b"unchanged")])
                guide.write_bytes(b"# Real local guide")

    def test_installed_shared_provider_has_exact_bytes_and_no_target_import_fallback(self):
        self.run_cli(client="other")
        bundle = self.target / ".github/lintel"
        relative = ".github/lintel/lib/markdown_source.py"
        expected = (ROOT / "lib/markdown_source.py").read_bytes().replace(b"\r\n", b"\n")
        self.assertEqual((self.target / relative).read_bytes(), expected)
        manifest = json.loads((bundle / "manifest.json").read_text())["files"]
        self.assertEqual(manifest[relative], hashlib.sha256(expected).hexdigest())
        marker = self.target / "untrusted-import-executed"
        untrusted = self.target / "lib"
        untrusted.mkdir()
        hostile = "from pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('unexpected')\n"
        (untrusted / "markdown_source.py").write_text(hostile, encoding="utf-8")
        (self.target / "markdown_source.py").write_text(hostile, encoding="utf-8")
        script = (
            "import json,sys; from pathlib import Path; "
            "sys.path.insert(0,str(Path(sys.argv[1])/'lib')); "
            "from markdown_source import classify_markdown; "
            "text='- - ```markdown\\n    - [x] literal\\n    ```\\n\\n<pre>- [x] raw</pre>\\n- [ ] actual'; "
            "facts=classify_markdown(text); "
            "print(json.dumps({'original':facts.original,'items':["
            "{'content':text[i.content.start:i.content.end],'classification':i.classification} "
            "for i in facts.list_items],'regions':[r.kind for r in facts.regions]}))"
        )
        env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home), PYTHONDONTWRITEBYTECODE="1",
                   PYTHONPATH=str(untrusted))
        result = subprocess.run([sys.executable, "-B", "-S", "-c", script, str(bundle)],
                                cwd=self.target, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual([item["content"] for item in output["items"] if item["classification"] == "prose"],
                         ["[ ] actual"])
        self.assertIn("raw_html_body", output["regions"])
        self.assertIn("fenced_code", output["regions"])
        self.assertFalse(marker.exists())
        self.run_cli("check", source=bundle)
        (bundle / "lib/markdown_source.py").unlink()
        before = self.snapshot()
        result = subprocess.run([sys.executable, "-B", "-S", str(bundle / "bin/li-adapter.py"), "check",
                                 "--target", str(self.target)], cwd=self.target, env=env,
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR: Required source file is missing:", result.stderr)
        self.assertIn("markdown_source.py", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(before, self.snapshot())
        self.assertFalse(marker.exists())
        self.assertEqual(list(self.home.iterdir()), [])

    def test_installed_provider_rejects_false_ordered_item_eligibility(self):
        self.run_cli(client="other")
        bundle = self.target / ".github/lintel"
        script = (
            "import json,sys; from pathlib import Path; sys.path.insert(0,str(Path(sys.argv[1])/'lib')); "
            "from markdown_source import classify_markdown; "
            "cases=['Paragraph\\n2. [ ] A05.2 ordinary continuation\\n',"
            "'Paragraph\\n\\n2. [ ] A05.2 real item\\n',"
            "'Paragraph\\n1. [ ] A05.2 real item\\n']; "
            "print(json.dumps([[{'marker':list(i.marker),'content':list(i.content),"
            "'classification':i.classification} for i in classify_markdown(t).list_items] for t in cases]))"
        )
        result = subprocess.run([sys.executable, "-B", "-S", "-c", script, str(bundle)],
                                capture_output=True, text=True, encoding="utf-8",
                                env=dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                                         PYTHONDONTWRITEBYTECODE="1"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout), [
            [], [{"marker": [11, 13], "content": [14, 33], "classification": "prose"}],
            [{"marker": [10, 12], "content": [13, 32], "classification": "prose"}],
        ])
        self.assertEqual(list(self.home.iterdir()), [])

    def test_multiline_inline_script_example_is_not_a_consumer_dependency(self):
        self.run_cli(client="other")
        source = self.target / ".github/lintel"
        faq = source / "docs/faq.md"
        original = faq.read_bytes()
        fixture = (
            b'`<script src="review-fixture/code-only.js">\n</script>`\n\n'
            b'[Real](review-fixture/guide.md)\n'
        )
        directory = source / "docs/review-fixture"
        directory.mkdir()
        guide, example = directory / "guide.md", directory / "code-only.js"
        guide.write_bytes(b"# Real local guide")
        example_bytes = b"SYNTHETIC-CODE-ONLY-SHOULD-NOT-BUNDLE\n"
        for name, present, content in (
                ("multiline-present", True, fixture), ("multiline-absent", False, fixture),
                ("same-line", False, fixture.replace(b">\n</script>", b"></script>"))):
            with self.subTest(case=name):
                if present:
                    example.write_bytes(example_bytes)
                elif example.exists():
                    example.unlink()
                faq.write_bytes(original + b"\n" + content)
                consumer = self.base / ("inline-" + name)
                consumer.mkdir()
                self.run_cli(client="other", source=source, target=consumer)
                self.run_cli("check", source=consumer / ".github/lintel", target=consumer)
                clone = self.base / ("inline-clone-" + name)
                self.clone_project(consumer, clone)
                self.run_cli("check", source=clone / ".github/lintel", target=clone)
                for target in (consumer, clone):
                    bundle = target / ".github/lintel"
                    manifest = json.loads((bundle / "manifest.json").read_text())["files"]
                    self.assertIn(".github/lintel/docs/review-fixture/guide.md", manifest)
                    self.assertNotIn(".github/lintel/docs/review-fixture/code-only.js", manifest)
                    self.assertEqual((bundle / "docs/review-fixture/guide.md").read_bytes(), b"# Real local guide")
                    self.assertFalse((bundle / "docs/review-fixture/code-only.js").exists())
                guide.unlink()
                refused = self.base / ("inline-missing-guide-" + name)
                refused.mkdir()
                (refused / "keep.txt").write_bytes(b"unchanged")
                result = self.run_cli(client="other", source=source, target=refused, success=False)
                self.assertIn("guide.md", result.stderr)
                self.assertEqual([(path.name, path.read_bytes()) for path in refused.iterdir()],
                                 [("keep.txt", b"unchanged")])
                guide.write_bytes(b"# Real local guide")
        faq.write_bytes(original + b"\n" + fixture.replace(b"`", b""))
        actual_html = self.base / "inline-actual-html"
        actual_html.mkdir()
        result = self.run_cli(client="other", source=source, target=actual_html, success=False)
        self.assertIn("code-only.js", result.stderr)
        self.assertEqual(list(actual_html.iterdir()), [])
        example.write_bytes(example_bytes)
        self.run_cli(client="other", source=source, target=actual_html)
        self.run_cli("check", source=actual_html / ".github/lintel", target=actual_html)
        self.assertEqual((actual_html / ".github/lintel/docs/review-fixture/code-only.js").read_bytes(),
                         example_bytes)

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
