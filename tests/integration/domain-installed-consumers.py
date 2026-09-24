#!/usr/bin/env python3
# component: installed-domain-consumer-tests
# implements: ADR-0028, ADR-0029, ADR-0030
# intent: .claude/plans/universal-implementation/packages/P09.md
# constraints: accepted P10 install; short synthetic roots; no injected LINTEL selectors; no live-role claim
# last_intent_review: 2026-09-24
"""Installed P09 closure; retains source/fixture/native-actor evidence as distinct levels."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--work-dir", type=Path)
parser.add_argument("--surface", choices=("native", "lifecycle"), default="native" if os.name == "nt" else "lifecycle")
parser.add_argument("--pwsh", default=shutil.which("pwsh"))
parser.add_argument("--bash", default=shutil.which("bash"))
parser.add_argument("--git", default=shutil.which("git"))
parser.add_argument("--worker", action="store_true")
parser.add_argument("--installed", type=Path)
parser.add_argument("--cold", action="store_true")
options = parser.parse_args()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")


def clean_environment(root):
    env = {key: os.environ[key] for key in
           ("PATH", "PATHEXT", "SystemRoot", "WINDIR", "SystemDrive", "COMSPEC") if key in os.environ}
    home = root / "h"
    env.update({
        "HOME": str(home), "USERPROFILE": str(home), "HOMEDRIVE": home.drive,
        "HOMEPATH": str(home)[len(home.drive):],
        "APPDATA": str(home / "AppData/Roaming"), "LOCALAPPDATA": str(home / "AppData/Local"),
        "XDG_CONFIG_HOME": str(home / ".config"), "XDG_CACHE_HOME": str(home / ".cache"),
        "XDG_DATA_HOME": str(home / ".local/share"),
        "TEMP": str(root / "t"), "TMP": str(root / "t"), "TMPDIR": str(root / "t"),
        "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never", "GIT_OPTIONAL_LOCKS": "0",
        "GIT_CEILING_DIRECTORIES": str(root), "GIT_PAGER": "cat", "PAGER": "cat",
    })
    for name in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "XDG_CACHE_HOME",
                 "XDG_DATA_HOME", "TEMP", "TMP", "TMPDIR"):
        selected = Path(env[name])
        assert selected.is_relative_to(root)
        selected.mkdir(parents=True, exist_ok=True)
    assert not any(name.startswith("LINTEL_") for name in env)
    assert not any(name in env for name in ("GH_TOKEN", "GITHUB_TOKEN", "BASH_ENV", "PYTHONPATH", "CLAUDE_PLUGIN_ROOT"))
    return env


class LoggedProcesses:
    def __init__(self, root, env):
        self.root, self.env, self.counter = root, env, 0
        self.logs = root / "logs"
        self.logs.mkdir(exist_ok=True)

    def run(self, argv, *, cwd=None, env=None, capture_output=True, text=True, encoding="utf-8"):
        assert capture_output and text and encoding == "utf-8"
        actual_env = env or self.env
        assert not any(key.startswith("LINTEL_") for key in actual_env)
        assert actual_env["HOME"] == actual_env["USERPROFILE"]
        assert Path(actual_env["HOME"]).is_relative_to(self.root)
        assert not any(key in actual_env for key in ("GH_TOKEN", "GITHUB_TOKEN", "BASH_ENV", "PYTHONPATH"))
        self.counter += 1
        stem = self.logs / str(self.counter)
        args = [str(arg) for arg in argv]
        with stem.with_suffix(".stdout.log").open("xb") as out, stem.with_suffix(".stderr.log").open("xb") as err:
            result = subprocess.run(args, cwd=cwd or self.root, env=actual_env, stdout=out, stderr=err,
                                    timeout=240, check=False)
        raw_out, raw_err = stem.with_suffix(".stdout.log").read_bytes(), stem.with_suffix(".stderr.log").read_bytes()
        plain_json(stem.with_suffix(".json"), {
            "argv": args, "cwd": str(cwd or self.root), "exit_code": result.returncode,
            "home": actual_env["HOME"], "userprofile": actual_env["USERPROFILE"],
            "temp": actual_env["TEMP"], "git_ceiling": actual_env["GIT_CEILING_DIRECTORIES"],
            "lintel_selectors": [], "stdout_sha256": hashlib.sha256(raw_out).hexdigest(),
            "stderr_sha256": hashlib.sha256(raw_err).hexdigest(),
        })
        return subprocess.CompletedProcess(args, result.returncode, raw_out.decode("utf-8"), raw_err.decode("utf-8"))


def worker():
    installed = options.installed.resolve()
    original_args = [
        str(ROOT / "tests/integration/domain-module-consumers.py"), "--root", str(installed),
        "--bash", options.bash, "--git", options.git,
        "--artifacts-root", str(options.work_dir / "logs/domain"), "--without-selectors",
    ]
    sys.argv = original_args
    module = runpy.run_path(str(ROOT / "tests/integration/domain-module-consumers.py"))
    data = module["DATA"]
    for name in ("context_safety", "profile_context", "review_contract"):
        assert Path(sys.modules[name].__file__).resolve().is_relative_to(installed), name
    assert module["SOURCE"] == installed

    class InstalledCases(module["ModuleConsumers"]):
        def setUp(self):
            super().setUp()
            self.assertFalse(any(name.startswith("LINTEL_") for name in self.env))
            self.assertLess(max(len(str(self.repo)), len(str(self.home))), 100)

        def test_installed_discovery_and_removed_dependency(self):
            for name in ("ta", "da", "sc", "dh", "tq", "full-engineering-pass"):
                result = self.run_process([sys.executable, "-I", "-B", installed / "bin/li-catalog.py",
                                           "--json", "--kind=skill", "--name", name])
                self.assertEqual([f"skill:{name}"], [entry["id"] for entry in json.loads(result.stdout)["entries"]])
            self.selected_map()
            self.bind_request()
            self.cli("validate", "--file", self.request_path)
            self.write("lib/domain_result.py", b"raise RuntimeError('target fallback must never load')\n")
            removed = installed / "lib/domain_result.py"
            original = removed.read_bytes()
            removed.unlink()
            try:
                refused = self.cli("validate", "--file", self.request_path, expected=None)
                self.assertNotEqual(0, refused.returncode)
                self.assertEqual("", refused.stdout)
                self.assertIn("domain_result", refused.stderr)
                self.assertNotIn("target fallback must never load", refused.stderr)
            finally:
                removed.write_bytes(original)
            self.cli("validate", "--file", self.request_path)

        def test_installed_receiver_contract_and_mismatch(self):
            role = installed / "agents/engineering/ContractTestArchitect.md"
            self.assertIn("name: ContractTestArchitect", role.read_text(encoding="utf-8"))
            self.assertIn("ContractTestArchitect", (installed / "skills/tq/SKILL.md").read_text(encoding="utf-8"))
            discovered = self.run_process([sys.executable, "-I", "-B", installed / "bin/li-catalog.py",
                                            "--json", "--kind=agent", "--name=ContractTestArchitect"])
            self.assertEqual(["agent:ContractTestArchitect"],
                             [item["id"] for item in json.loads(discovered.stdout)["entries"]])
            self.selected_map(domains=("tq",))
            self.bind_request()
            cp = self.request["domains"][0]["checkpoints"][0]
            cp["receiver"] = {"role": "ContractTestArchitect", "mode": "design-only"}
            self.write_json(self.request_path, self.request)
            self.produce()
            self.prepare_final()
            self.assertTrue(self.verify(command="summary")["ok"])
            for field, value in (("role", "UnselectedReceiver"), ("mode", "authorized-execution")):
                bad = deepcopy(self.results["tq"])
                bad["receiver"][field] = value
                self.write_json(".claude/runtime/meta/wrong-receiver.json", bad)
                self.cli("validate", "--file", ".claude/runtime/meta/wrong-receiver.json",
                         "--request", self.request_path, expected=2)

    if options.cold:
        case = InstalledCases("test_installed_receiver_contract_and_mismatch")
        case.setUp()
        case.temp._finalizer.detach()
        case.selected_map(domains=("ta", "tq"))
        case.write("specs/chosen/spec.md", b"""# Synthetic installed cold handoff
R1 / T014: Design consumer/provider compatibility tests for an optional response field.
Provider v2 adds nullable note to GET /status. Consumer A rejects unknown fields;
consumer B accepts unknown fields but distinguishes omitted note from null.
Keep both consumers in the matrix; no average compatibility verdict.
APIDesigner supplied the surface; ContractTestArchitect designs tests only.
No API, database, browser or deployment action is authorized.
""")
        case.bind_request()
        case.request["domains"][0]["checkpoints"][0]["receiver"] = {"role": "APIDesigner", "mode": "artifact-only"}
        tq = case.request["domains"][1]["checkpoints"][0]
        tq["id"] = "contract_tests_complete"
        tq["receiver"] = {"role": "ContractTestArchitect", "mode": "design-only"}
        case.write_json(case.request_path, case.request)
        case.produce(score=100)
        case.write("historical-tq-result.json", data["safety"].read_owned(case.repo, case.result_path("tq"))[0])
        data["safety"].native_io_path(case.repo / case.result_path("tq")).unlink()
        case.prepare_final()
        summary = case.verify(command="summary", expected=3)
        case.write_json("inspection.json", summary)
        case.write_json("handoff.json", {
            "installed_source": str(installed), "target": str(case.repo),
            "original_map": "specs/chosen/work.json", "package": "P09", "leaf": "T014",
            "request": case.request_path, "expected": case.expected_path,
            "role": "agents/engineering/ContractTestArchitect.md",
            "module": "skills/tq/SKILL.md", "profile": case.reference,
            "known_effects": "No domain action was executed; only caller synthetic data records. Read-only design is authorized.",
            "negative": "Do not accept the old result or high score as clearance for the missing current required result.",
        })
        plain_json(options.work_dir / "cold-fixture.json", {
            "target": str(case.repo), "home": str(case.home), "installed": str(installed),
            "handoff": str(case.repo / "handoff.json"), "profile": case.reference,
            "evidence_kind": "real installed producer/consumer, synthetic observations; native handoff not yet executed",
        })
        print("Prepared fresh installed cold fixture; no native behavior claimed.", flush=True)
        return 0

    selected = [
        InstalledCases("test_installed_discovery_and_removed_dependency"),
        InstalledCases("test_original_grouped_ids_decoy_to_real_data_and_qa"),
        InstalledCases("test_wrong_package_missing_parent_leaf_and_draft_refuse"),
        InstalledCases("test_original_work_composition_missing_domain_blocks_high_scores"),
        InstalledCases("test_failed_error_unknown_and_zero_tests_block_even_high_score"),
        InstalledCases("test_started_attempt_cold_inspection_does_not_replay"),
        InstalledCases("test_installed_receiver_contract_and_mismatch"),
        InstalledCases("test_portable_paths_reject_windows_aliases_and_traversal"),
    ]
    outcome = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
    print("Installed process/data/transport checks only; not native role execution.", flush=True)
    return 0 if outcome.wasSuccessful() and not outcome.skipped else 1


def installed_suite():
    if not options.bash or not options.git or (options.surface == "native" and not options.pwsh):
        raise SystemExit("Required existing runtime missing; native needs approved PowerShell 7. No automatic restore.")
    if options.surface == "native" and Path(options.pwsh).name.lower() != "pwsh.exe" and os.name == "nt":
        raise SystemExit("Select approved PowerShell 7 explicitly; Windows PowerShell 5.1 is not a fallback.")
    temporary = None
    if options.work_dir is None:
        temporary = tempfile.TemporaryDirectory(prefix="lid-")
        work = Path(temporary.name).resolve()
    else:
        work = options.work_dir.resolve()
        work.mkdir(parents=True, exist_ok=False)
    if os.name == "nt" and len(str(work)) > 65:
        raise SystemExit("Choose an explicitly authorized short fixture root; no long-path workaround is attempted.")
    env = clean_environment(work)
    processes = LoggedProcesses(work, env)
    kit, store = work / "kit", work / "store"
    powershell_version = None
    if options.surface == "native":
        pwsh = processes.run([
            options.pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command",
            "if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'PowerShell 7 required' }; "
            "if ($HOME -ne $env:USERPROFILE) { throw 'HOME differs from synthetic USERPROFILE' }; "
            "$PSVersionTable.PSVersion.ToString()",
        ])
        if pwsh.returncode:
            raise RuntimeError(pwsh.stderr)
        powershell_version = pwsh.stdout.strip()
        command = [options.pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
                   ROOT / "install/install.ps1", "-Source", ROOT, "-Home", kit, "-Store", store]
        check_command = [*command, "-Check"]
        inventory = kit / ".lintel-install.tsv"
    else:
        consumer = work / "consumer"
        consumer.mkdir()
        entry = [sys.executable, "-I", "-B", ROOT / "bin/li-lifecycle.py",
                 "--repo", consumer, "--store", store, "scaffold"]
        command = [*entry, "init", "--target", consumer, "--copilot"]
        check_command = [*entry, "check", "--target", consumer, "--copilot"]
        kit = consumer / ".github/lintel"
        inventory = kit / "manifest.json"
    installed = processes.run(command)
    if installed.returncode:
        raise RuntimeError("Selected P10 install failed; preserve evidence and report, do not repair:\n" + installed.stderr)
    checked = processes.run(check_command)
    if checked.returncode:
        raise RuntimeError(checked.stderr)
    baseline = {str(path.relative_to(kit)): digest(path) for path in kit.rglob("*") if path.is_file()}
    max_path = max(len(str(path)) for path in kit.rglob("*"))
    if os.name == "nt" and max_path >= 235:
        raise RuntimeError(f"Fixture exceeded its conservative short-path budget: {max_path}")

    helper_spec = importlib.util.spec_from_file_location(
        "installed_consumer_checks", Path(__file__).with_name("installed_consumer_checks.py"))
    shared = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(shared)
    case = unittest.TestCase()
    review_target = work / "review"
    review_target.mkdir()
    shared.review_controls(case, kit, review_target, run=processes.run)
    profile_target = work / "profile"
    profile_target.mkdir()
    (profile_target / "AGENTS.md").write_text("# Synthetic installed profile consumer\n", encoding="utf-8")
    shared.profile_continuity(case, kit, profile_target, work / "unused-home", options.bash, run=processes.run)
    child = [sys.executable, "-B", __file__, "--worker", "--installed", kit,
             "--work-dir", work, "--bash", options.bash, "--git", options.git]
    measured = processes.run(child)
    if measured.returncode:
        raise RuntimeError("Installed domain checks failed; retain raw logs:\n" + measured.stderr)
    methods = re.search(r"Ran (\d+) tests?", measured.stderr)
    case.assertIsNotNone(methods, "The installed worker must report its actual test count.")
    case.assertEqual(8, int(methods.group(1)))
    cold = processes.run([*child, "--cold"])
    if cold.returncode:
        raise RuntimeError("Installed cold preparation failed:\n" + cold.stderr)
    after = {str(path.relative_to(kit)): digest(path) for path in kit.rglob("*") if path.is_file()}
    case.assertEqual(baseline, after, "Installed source changed or received runtime output.")
    final_check = processes.run(check_command)
    case.assertEqual(0, final_check.returncode, final_check.stdout + final_check.stderr)
    max_fixture_path = max(len(str(path)) for path in work.rglob("*"))
    if os.name == "nt" and max_fixture_path >= 235:
        raise RuntimeError(f"Fixture exceeded the short-path budget: {max_fixture_path}")
    plain_json(work / "installed-receipt.json", {
        "source": str(ROOT), "installed": str(kit), "surface": options.surface,
        "powershell": powershell_version, "install_exit": installed.returncode,
        "install_checks": [checked.returncode, final_check.returncode],
        "domain_suite_exit": measured.returncode, "cold_preparation_exit": cold.returncode,
        "domain_methods": int(methods.group(1)),
        "injected_lintel_selectors": [], "managed_inventory_sha256": digest(inventory),
        "installed_files": len(baseline), "max_installed_path": max_path,
        "max_fixture_path": max_fixture_path,
        "installed_source_unchanged": True, "native_role_execution": "not_run_by_this_suite",
        "scope": "Actual P10 installed short-path closure; not copied-source, live client registration, old finite attempts or whole parent acceptance.",
    })
    print(f"PASS installed domain closure: {work}", flush=True)
    if temporary is not None:
        print("Disposable automatic fixture will be cleaned; use --work-dir for retained native handoff evidence.", flush=True)
        temporary.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(worker() if options.worker else installed_suite())
