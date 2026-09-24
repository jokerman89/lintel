#!/usr/bin/env python3
# component: installed-discovery-closure-tests
# implements: ADR-0028, ADR-0030
# intent: .claude/plans/universal-implementation/packages/P13.md
# constraints: accepted lifecycle route; short synthetic roots; no LINTEL selectors or live-model claims
# last_intent_review: 2026-09-24
"""P10-installed discovery, retained aliases/assets and discriminating consumer negatives."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--fixture-root", type=Path)
parser.add_argument("--keep-fixtures", action="store_true")
OPTIONS, TEST_ARGS = parser.parse_known_args()


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kit = load("accepted_copilot_kit_cases", "tests/integration/copilot-kit.py")
selection = load("accepted_catalog_selection_cases", "tests/unit/catalog-selection.py")


class InstalledDiscovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = (OPTIONS.fixture_root or Path(tempfile.gettempdir())).resolve(strict=True)
        if parent.is_symlink() or getattr(parent.lstat(), "st_file_attributes", 0) & 0x400:
            raise ValueError("Fixture root must be an ordinary owned directory")
        if OPTIONS.keep_fixtures:
            cls.temporary = None
            cls.run_root = Path(tempfile.mkdtemp(prefix="p13i-", dir=parent))
        else:
            cls.temporary = tempfile.TemporaryDirectory(prefix="p13i-", dir=parent)
            cls.run_root = Path(cls.temporary.name)
        cls.counter = 0
        print("INSTALLED_DISCOVERY_ROOT=" + str(cls.run_root), flush=True)

    @classmethod
    def tearDownClass(cls):
        if cls.temporary is not None:
            assert Path(cls.temporary.name) == cls.run_root
            cls.temporary.cleanup()

    def setUp(self):
        type(self).counter += 1
        self.base = self.run_root / str(self.counter)
        self.base.mkdir()
        self.source = ROOT
        self.target = self.base / "t"
        self.target.mkdir()
        (self.target / "consumer-owned.txt").write_bytes(b"preserve consumer state\r\n")
        self.logs = self.base / "e"
        self.logs.mkdir()
        self.cwd = self.base / "cwd"
        self.cwd.mkdir()
        self.sequence = 0
        system = {
            "PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "SYSTEMDRIVE",
            "OS", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS",
        }
        env = {key: value for key, value in os.environ.items() if key.upper() in system}
        for key, relative in {
            "HOME": "h", "USERPROFILE": "h", "APPDATA": "a", "LOCALAPPDATA": "l",
            "TEMP": "tmp", "TMP": "tmp", "TMPDIR": "tmp",
            "XDG_CONFIG_HOME": "x/c", "XDG_CACHE_HOME": "x/k", "XDG_DATA_HOME": "x/d",
            "CLAUDE_CONFIG_DIR": "claude", "COPILOT_HOME": "copilot",
        }.items():
            path = self.base.joinpath(*relative.split("/"))
            path.mkdir(parents=True, exist_ok=True)
            self.assertEqual(path.resolve(), path)
            self.assertFalse(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)
            env[key] = str(path)
        env.update(GIT_CEILING_DIRECTORIES=str(self.run_root), GIT_TERMINAL_PROMPT="0",
                   GCM_INTERACTIVE="Never", GIT_PAGER="cat", PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
        if os.name == "nt":
            env.update(HOMEDRIVE=self.base.drive, HOMEPATH=str(self.base / "h")[len(self.base.drive):])
        self.environment = mock.patch.dict(os.environ, env, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.assertEqual(Path.home(), self.base / "h")
        self.assertFalse(any(key.startswith("LINTEL_") for key in os.environ))
        self.assert_short(self.base / "worst-case/.github/lintel" / max(
            (path.relative_to(ROOT) for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts),
            key=lambda path: len(str(path)),
        ))
        self.source_before = self.snapshot(ROOT)
        self.addCleanup(self.assert_source_unchanged)

    def assert_short(self, path):
        self.assertLess(len(str(path).encode("utf-16-le")) // 2, 220,
                        "Use an explicitly selected shorter synthetic fixture root before this test, not a long-path workaround")

    def snapshot(self, target=None):
        root = target or self.target
        return {
            "files": selection.support.files_snapshot(root),
            "directories": sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_dir()),
        }

    def fixture_snapshot(self):
        return {
            "files": {path.relative_to(self.base).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in self.base.rglob("*") if path.is_file() and not path.is_relative_to(self.logs)},
            "directories": sorted(path.relative_to(self.base).as_posix() for path in self.base.rglob("*")
                                  if path.is_dir() and not path.is_relative_to(self.logs)),
        }

    def assert_source_unchanged(self):
        self.assertEqual(self.snapshot(ROOT), self.source_before)
        self.assertFalse(any(key.startswith("LINTEL_") for key in os.environ))

    def command(self, argv, cwd=None, env=None, read_only=False):
        effective = dict(env or os.environ)
        self.assertFalse(any(key.startswith("LINTEL_") for key in effective))
        self.sequence += 1
        stem = self.logs / f"{self.sequence:03d}"
        request = {"argv": [str(value) for value in argv], "cwd": str(cwd or self.cwd),
                   "environment": effective, "lintel_selectors": [],
                   "observed_fixture_root": str(self.base), "read_only": read_only,
                   "excluded_observation_path": str(self.logs),
                   "started_at": datetime.now(timezone.utc).isoformat()}
        stem.with_suffix(".request.json").write_text(json.dumps(request, indent=2), encoding="utf-8")
        before = self.fixture_snapshot()
        with stem.with_suffix(".stdout").open("wb") as out, stem.with_suffix(".stderr").open("wb") as err:
            result = subprocess.run(argv, cwd=cwd or self.cwd, env=effective,
                                    stdout=out, stderr=err, timeout=600, check=False)
        stdout, stderr = stem.with_suffix(".stdout").read_bytes(), stem.with_suffix(".stderr").read_bytes()
        after = self.fixture_snapshot()
        stem.with_suffix(".result.json").write_text(json.dumps({
            "exit": result.returncode, "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
            "fixture_changed": before != after, "ended_at": datetime.now(timezone.utc).isoformat(),
        }, indent=2), encoding="utf-8")
        if read_only:
            self.assertEqual(before, after)
        for path in self.base.rglob("*"):
            self.assert_short(path)
        return subprocess.CompletedProcess(argv, result.returncode, stdout.decode("utf-8"), stderr.decode("utf-8"))

    def run_cli(self, command="init", success=True, source=None, target=None, script=None):
        source, target = Path(source or self.source), Path(target or self.target)
        if script is not None:
            self.assertEqual(Path(script), source / "bin/li-copilot.py")
        store = self.base / ("s-" + hashlib.sha256(str(target).encode()).hexdigest()[:8])
        self.assert_short(store / "transactions/00000000-0000-0000-0000-000000000000/journal.json")
        result = self.command([
            sys.executable, "-I", "-B", str(source / "bin/li-lifecycle.py"),
            "--source", str(source), "--repo", str(target), "--store", str(store),
            "scaffold", command, "--target", str(target), "--client", "copilot-cli",
        ])
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('"state": "adapter_verified"', result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def catalog_query(self, bundle, *arguments, cwd, env=None, no_site=False):
        command = [sys.executable, "-I", *(["-S"] if no_site else []),
                   "-B", str(bundle / "bin/li-catalog.py"), *arguments]
        return self.command(command, cwd=cwd, env=env, read_only=True)

    def query(self, bundle, *arguments, success=True):
        result = self.command([sys.executable, "-I", "-B", str(bundle / "bin/li-catalog.py"),
                               "--json", *arguments], read_only=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(value["source_root"], str(bundle))
            self.assertFalse(value["executed"])
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertTrue(result.stderr)
        return result

    def installed(self):
        self.run_cli()
        self.run_cli("check")
        bundle = self.target / kit.adapter.BUNDLE
        manifest = json.loads((self.target / kit.adapter.INVENTORY).read_bytes())
        self.assertEqual(manifest["clients"], ["copilot-cli"])
        self.assertFalse(manifest["hooks_installed"])
        expected, _, _ = kit.adapter.generate(self.source, self.target)
        for relative, digest in manifest["files"].items():
            data = (self.target / relative).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest, relative)
            self.assertEqual(data, expected[relative], relative)
        self.assertEqual((bundle / "bin/li-catalog.py").read_bytes(),
                         kit.adapter.source_bytes(ROOT / "bin/li-catalog.py"))
        return bundle

    test_portable_selection = kit.CopilotKit.test_selected_catalog_runs_from_portable_bundle_without_source_fallback
    test_optional_family_closure = kit.CopilotKit.test_optional_family_closures_survive_portable_clone

    def test_all_methods_aliases_and_worked_examples_survive_installation(self):
        bundle = self.installed()
        before = self.snapshot()
        source = json.loads(self.query(ROOT, "--kind=all").stdout)
        installed = json.loads(self.query(bundle, "--kind=all").stdout)
        self.assertEqual(installed["entries"], source["entries"])
        aliases, module_capabilities = 0, 0
        for entry in installed["entries"]:
            path = bundle / entry["path"]
            self.assertEqual(path.read_bytes(), kit.adapter.source_bytes(ROOT / entry["path"]))
            for alias in entry["aliases"]:
                aliases += 1
                found = json.loads(self.query(bundle, "--kind=" + entry["kind"], "--name=" + alias["name"]).stdout)
                self.assertEqual(found["entries"], [entry])
                if entry["name"] in ("ta", "da", "sc", "dh", "tq"):
                    capability = alias["name"][len(entry["name"]) + 1:]
                    self.assertIn("| `" + capability + "` |", path.read_text(encoding="utf-8"))
                    module_capabilities += 1
        self.assertEqual((aliases, module_capabilities), (46, 35))
        index = json.loads(self.query(bundle, "--list-selections").stdout)
        for definition in index["selections"]:
            example = definition["example"]
            text = (bundle / example["path"]).read_text(encoding="utf-8")
            self.assertIn(example["heading"], text.splitlines())
            self.assertTrue(definition["inputs"] and definition["outputs"] and definition["limitations"])
            if definition["id"] in selection.FAMILIES:
                section = text.split(example["heading"] + "\n", 1)[1].split("\n## ", 1)[0]
                for label in ("**Inputs.**", "**Method and output.**", "**Negative.**", "**Evidence limit.**"):
                    self.assertIn(label, section)
        self.assertEqual(before, self.snapshot())

    def test_unresolvable_alias_refuses_even_an_unmatched_query(self):
        bundle = self.installed()
        path = bundle / "config/aliases.yaml"
        original = path.read_bytes()
        old, new = b"    new: skill-router\n", b"    new: p13-absent-method\n"
        self.assertEqual(original.count(old), 1)
        path.write_bytes(original.replace(old, new, 1))
        before = self.snapshot()
        for arguments in (("--kind=skill", "--name=match"),
                          ("--selection=demo-script", "--query=does-not-match-anything")):
            result = self.query(bundle, *arguments, success=False)
            self.assertIn("config/aliases.yaml", result.stderr)
            self.assertIn("missing target", result.stderr)
            self.assertEqual(before, self.snapshot())

    def test_literal_and_malformed_installed_selections_refuse_without_writes(self):
        bundle = self.installed()
        before = self.snapshot()
        value = json.loads(self.query(bundle, "--selection=demo-script", "--query=$(touch p13-marker)").stdout)
        self.assertEqual(value["matched"], 0)
        self.assertEqual(before, self.snapshot())
        self.query(bundle, "--selection=../../not-a-selection", success=False)
        self.assertEqual(before, self.snapshot())
        path = bundle / "lib/capability-selections.json"
        original = path.read_bytes()
        for invalid in (b"", b"{}", b"not-json-or-yaml: ["):
            path.write_bytes(invalid)
            corrupted = self.snapshot()
            self.query(bundle, "--selection=demo-script", "--query=unmatched", success=False)
            self.assertEqual(corrupted, self.snapshot())
        path.write_bytes(original)
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.cwd / "p13-marker").exists())

    def test_metadata_first_body_observation_and_injected_exposure(self):
        bundle = self.installed()
        before = self.snapshot()
        literal = json.loads(self.query(bundle, "--selection=demo-script", "--kind=agent",
                                       "--name=DemoNarrativeArc").stdout)
        for injected in (False, True):
            trace = self.logs / ("injected-body.json" if injected else "selected-body.json")
            command = [sys.executable, "-I", "-B", str(ROOT / "tests/integration/catalog-installed-probe.py"),
                       "--source", str(bundle), "--trace", str(trace)]
            if injected:
                command.append("--inject-unrelated")
            result = self.command(command, read_only=True)
            value = json.loads(trace.read_bytes())
            if injected:
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertIn("UNRELATED_BODY_EXPOSURE", result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertTrue(value["injected_whole_body_read"])
                self.assertFalse(value["body_reads"][0]["allowed"])
            else:
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(value["metadata"], literal)
                self.assertEqual([event["operation"] for event in value["events"]],
                                 ["metadata-complete", "selected-body"])
                self.assertEqual(len(value["body_reads"]), 1)
                self.assertEqual(value["body_reads"][0]["path"],
                                 str(bundle / literal["entries"][0]["path"]))
            self.assertEqual(before, self.snapshot())


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], *TEST_ARGS], verbosity=2)
