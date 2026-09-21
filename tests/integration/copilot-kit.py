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
JOINED_RUNTIME_RESOURCES = (
    "lib/swarm_snapshot.py", "lib/envelope_contract.py", "lib/envelope-requirements.txt",
    "lib/profile_context.py", "lib/profile-context-schema.json", "lib/pack-schema.yaml",
    "lib/native_paths.py",
    ".claude-plugin/plugin.json",
)
REVIEW_RUNTIME_RESOURCES = (
    "bin/li-review-evidence.py", "bin/li-review-log", "bin/li-review-read",
    "lib/review_contract.py", "lib/review-schema.json",
    "lib/markdown_source.py", "bin/_audit.sh", "lib/paths.sh",
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

    def test_long_git_metadata_runs_real_effective_ignore_validation(self):
        target = self.long_metadata_root()
        shallow = self.target / "git-source"
        shallow.mkdir()
        git = shutil.which("git")
        self.assertTrue(git)
        version = subprocess.run([git, "--version"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(version.returncode, 0, version.stderr)
        result = subprocess.run([git, "init", "--quiet", str(shallow)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in ("staged.txt", "unstaged.txt"):
            (shallow / name).write_bytes(b"Original indexed bytes.\r\n")
        result = subprocess.run([git, "-C", str(shallow), "add", "--", "staged.txt", "unstaged.txt"],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        (shallow / "unstaged.txt").write_bytes(b"Retain the unstaged edit.\r\n")
        (shallow / "untracked.txt").write_bytes(b"Retain the untracked file.\r\n")
        shutil.copytree(shallow, adapter.native_io_path(target), dirs_exist_ok=True)
        self.assertEqual(len(str(target / ".git")), 261)
        self.assertTrue(adapter.native_io_path(target / ".git").is_dir())
        failure = ["Git does not confirm .claude/runtime/ is ignored; review conflicting ignore rules"]
        for current in (target, shallow):
            for name in (".git/HEAD", ".git/index", ".git/config"):
                self.assertTrue(adapter.native_io_path(current / name).is_file(), name)
            for content, code in ((".claude/runtime/\n", 0),
                                  (".claude/runtime/\n!.claude/runtime/\n!.claude/runtime/**\n", 1)):
                with self.subTest(root=str(current), ignored=code == 0):
                    adapter.native_io_path(current / ".gitignore").write_text(content, encoding="utf-8")
                    before = self.native_snapshot(current)
                    windows = ["-c", "core.longpaths=true"] if os.name == "nt" else []
                    argv = [git, "-c", "core.fsmonitor=false", *windows, "-C", str(current),
                            "check-ignore", "--no-index", "--quiet", ".claude/runtime/.lintel-ignore-check"]
                    observed = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
                    preserved = self.native_snapshot(current) == before
                    print(json.dumps({"git_version": version.stdout.strip(), "effective_ignore_argv": argv,
                                      "expected_exit": code, "returncode": observed.returncode,
                                      "stderr": observed.stderr, "bytes_modes_preserved": preserved,
                                      "head_index_config": {name: before[name] for name in
                                                            (".git/HEAD", ".git/index", ".git/config")}}))
                    self.assertEqual(observed.returncode, code, observed.stderr)
                    self.assertTrue(preserved)
                    self.assertEqual(adapter.runtime_ignore_errors(current, content), [] if code == 0 else failure)
                    self.assertEqual(self.native_snapshot(current), before)
            adapter.native_io_path(current / ".git/HEAD").write_bytes(b"not a Git HEAD\n")
            before = self.native_snapshot(current)
            observed = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
            print(json.dumps({"invalid_git_argv": argv, "returncode": observed.returncode,
                              "stderr": observed.stderr, "bytes_modes_preserved": self.native_snapshot(current) == before}))
            self.assertGreater(observed.returncode, 1, observed.stdout + observed.stderr)
            self.assertEqual(adapter.runtime_ignore_errors(current, content), failure)
            self.assertEqual(self.native_snapshot(current), before)

    def test_native_git_operand_directory_and_linked_worktree_gate(self):
        directory = self.long_metadata_root()
        worktree = directory.with_name("worktree-" + "x" * (len(directory.name) - len("worktree-")))
        main = self.base / "git-main"
        admin = main / ".git/worktrees" / worktree.name
        self.assertEqual(len(str(self.base)), 109)
        self.assertFalse(main.exists())
        self.assertEqual((len(str(directory)), len(str(worktree / ".git"))), (256, 261))
        print(json.dumps({"fixture_preflight": {
            "controller": [str(main), len(str(main))], "admin": [str(admin), len(str(admin))],
            "consumer": [str(worktree), len(str(worktree))],
            "git_entry": [str(worktree / ".git"), len(str(worktree / ".git"))],
        }}))
        main.mkdir()
        git = shutil.which("git")
        self.assertTrue(git)
        env = dict(os.environ, GIT_AUTHOR_NAME="Synthetic fixture", GIT_COMMITTER_NAME="Synthetic fixture",
                   GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_EMAIL="fixture@example.invalid")

        def command(*argv):
            return subprocess.run([git, *argv], env=env, text=True, encoding="utf-8", capture_output=True)

        initialized = command("init", "--quiet", str(main))
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        for name in ("staged.txt", "unstaged.txt"):
            (main / name).write_bytes(b"Committed fixture content.\r\n")
        added = command("-C", str(main), "add", "--", "staged.txt", "unstaged.txt")
        self.assertEqual(added.returncode, 0, added.stderr)
        committed = command("-C", str(main), "commit", "--quiet", "-m", "fixture: seed native Git probe")
        self.assertEqual(committed.returncode, 0, committed.stderr)
        (main / "staged.txt").write_bytes(b"Staged fixture edit.\r\n")
        added = command("-C", str(main), "add", "--", "staged.txt")
        self.assertEqual(added.returncode, 0, added.stderr)
        (main / "unstaged.txt").write_bytes(b"Unstaged fixture edit.\r\n")
        (main / "untracked.txt").write_bytes(b"Untracked fixture bytes.\r\n")
        shutil.copytree(main, adapter.native_io_path(directory), dirs_exist_ok=True)
        self.assertTrue(adapter.native_io_path(directory / ".git").is_dir())
        self.assertEqual((len(str(directory)), len(str(worktree))), (256, 256))
        version = command("--version")
        self.assertEqual(version.returncode, 0, version.stderr)
        observed_gate = []
        linked_attempted, linked_available, directory_without_option = False, False, False
        for options in ([], ["-c", "core.longpaths=true"]):
            if options and os.name != "nt":
                break
            if options and linked_attempted and not linked_available and directory_without_option:
                break
            passed = True
            for root in (directory, worktree):
                if root == worktree:
                    if not linked_attempted:
                        linked_attempted = True
                        before_setup = self.native_snapshot(main)
                        setup_options = ["-c", "core.longpaths=true"] if os.name == "nt" else []
                        linked = command(*setup_options, "-C", str(main), "worktree", "add",
                                         "--detach", str(worktree), "HEAD")
                        after_setup = self.native_snapshot(main)
                        self.assertEqual(after_setup[".git/config"], before_setup[".git/config"])
                        print(json.dumps({"fixture_worktree_argv": linked.args, "returncode": linked.returncode,
                                          "stdout": linked.stdout, "stderr": linked.stderr,
                                          "controller_config_preserved": True,
                                          "setup_created": sorted(set(after_setup) - set(before_setup))}))
                        linked_available = linked.returncode == 0
                    if not linked_available:
                        passed = False
                        continue
                    self.assertTrue(adapter.native_io_path(worktree / ".git").is_file())
                io_root = adapter.native_io_path(root)
                self.assertTrue(root.samefile(io_root))
                self.assertEqual((root.stat().st_dev, root.stat().st_ino),
                                 (io_root.stat().st_dev, io_root.stat().st_ino))
                identity = command("-c", "core.fsmonitor=false", *options, "-C", str(io_root),
                                   "rev-parse", "--show-toplevel", "--absolute-git-dir")
                if identity.returncode:
                    print(json.dumps({"identity_argv": identity.args, "returncode": identity.returncode,
                                      "stderr": identity.stderr}))
                    passed = False
                    continue
                top, git_dir_text = identity.stdout.splitlines()
                git_dir = Path(git_dir_text)
                self.assertTrue(io_root.samefile(adapter.native_io_path(Path(top))))
                self.assertTrue(adapter.native_io_path(git_dir).is_dir())
                if root == directory:
                    self.assertTrue(adapter.native_io_path(git_dir).samefile(adapter.native_io_path(root / ".git")))
                else:
                    for name in ("staged.txt", "unstaged.txt", "untracked.txt"):
                        adapter.native_io_path(root / name).write_bytes((main / name).read_bytes())
                    adapter.native_io_path(git_dir / "index").write_bytes((main / ".git/index").read_bytes())
                for text, expected in ((".claude/runtime/\n", 0),
                                       (".claude/runtime/\n!.claude/runtime/\n!.claude/runtime/**\n", 1)):
                    adapter.native_io_path(root / ".gitignore").write_text(text, encoding="utf-8")
                    before_root, before_admin, before_main = (self.native_snapshot(path)
                                                              for path in (root, git_dir, main))
                    result = command("-c", "core.fsmonitor=false", *options, "-C", str(io_root),
                                     "check-ignore", "--no-index", "--quiet", ".claude/runtime/.lintel-ignore-check")
                    preserved = (self.native_snapshot(root) == before_root
                                 and self.native_snapshot(git_dir) == before_admin
                                 and self.native_snapshot(main) == before_main)
                    self.assertTrue(preserved)
                    observation = {"version": version.stdout.strip(), "form": "directory" if root == directory else "worktree-file",
                                   "logical_root": str(root), "io_root": str(io_root),
                                   "lengths": [len(str(root)), len(str(root / ".git"))],
                                   "identity_argv": identity.args, "git_top": top, "git_dir": git_dir_text,
                                   "argv": result.args, "expected": expected, "returncode": result.returncode,
                                   "stderr": result.stderr, "state_preserved": preserved,
                                   "filesystem_identity": [root.stat().st_dev, root.stat().st_ino],
                                   "head_index_config": {
                                       "HEAD": before_admin["HEAD"], "index": before_admin["index"],
                                       "config": before_admin.get("config", before_main[".git/config"]),
                                   },
                                   "seeded_content": {name: before_root[name] for name in
                                                      ("staged.txt", "unstaged.txt", "untracked.txt")}}
                    observed_gate.append(observation)
                    print(json.dumps(observation))
                    passed = passed and result.returncode == expected
                head = adapter.native_io_path(git_dir / "HEAD")
                original = head.read_bytes()
                head.write_bytes(b"invalid fixture HEAD\n")
                try:
                    before_root, before_admin, before_main = (self.native_snapshot(path)
                                                              for path in (root, git_dir, main))
                    invalid = command("-c", "core.fsmonitor=false", *options, "-C", str(io_root),
                                      "check-ignore", "--no-index", "--quiet", ".claude/runtime/.lintel-ignore-check")
                    print(json.dumps({"invalid_argv": invalid.args, "returncode": invalid.returncode,
                                      "stderr": invalid.stderr}))
                    self.assertGreater(invalid.returncode, 1)
                    self.assertEqual(self.native_snapshot(root), before_root)
                    self.assertEqual(self.native_snapshot(git_dir), before_admin)
                    self.assertEqual(self.native_snapshot(main), before_main)
                finally:
                    head.write_bytes(original)
                if root == directory and not options:
                    directory_without_option = passed
            if passed:
                print(json.dumps({"eligible_fixed_variant": {"native_C_operand": True, "extra_options": options},
                                  "observations": len(observed_gate)}))
                return
        self.fail("Neither explicitly authorized native Git operand variant passed both forms.")

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
        for relative in REVIEW_RUNTIME_RESOURCES:
            self.assertTrue((bundle / relative).is_file(), relative)
        request = self.target / "control-input.json"
        control = {
            "id": "synthetic-evidence", "kind": "check", "requirement": "mandatory",
            "applicability": "applicable", "status": "pass",
            "reason": "Synthetic installed-consumer observation.",
            "policy": {"source": "spec.md", "version": "fixture-1", "applicability": "Synthetic package",
                       "jurisdiction": None, "actor": None, "effective_date": None},
            "evidence": ["checks.txt"], "observation": {},
        }
        policy = {"required": False, "status": "not_required", "source": None,
                  "version": None, "applicability": "not_applicable"}
        for status, code in (("pass", 0), ("fail", 3), ("unverified", 3)):
            control["status"] = status
            request.write_text(json.dumps({"controls": [control], "required_policy": policy}), encoding="utf-8")
            result = subprocess.run([sys.executable, "-I", "-B", "-S",
                                     str(bundle / "bin/li-review-evidence.py"), "controls",
                                     "--repo", str(self.target), "--input", str(request)],
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, code, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["blocked"], status != "pass")

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
