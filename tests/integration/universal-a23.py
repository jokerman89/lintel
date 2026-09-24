# component: universal-a23-joined-consumers
# implements: ADR-0026, ADR-0028, ADR-0029, ADR-0030, ADR-0031
# intent: .claude/plans/universal-implementation/packages/P14.md
# constraints: installed synthetic consumers; no provider fixes, jq, config writes or native verdict
# last_intent_review: 2026-09-24
"""Finite installed bridge and joined-chain evidence, not an execution framework."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import runpy
import stat
import subprocess
import sys
import time
import unittest


BASE = "ad1045b8b10a56fa3bcc5c310a8cad84f7ccf2c4"
WORK_MAP = "specs/chosen/work.json"
AUTHORITY = "2557676ee5905695c99d3610e4958fa4fbffd2c9"
WINDOWS_ROOT_BUDGET = 120
OPTIONS = None
RUN = None


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


class LocalRun:
    def __init__(self, options):
        self.options = options
        self.root = options.work_dir.resolve()
        self.source = options.root.resolve()
        self.env = dict(os.environ)
        self.started = time.monotonic()
        self.calls = []
        self.links = []
        self.inventory_observations = []
        self.max_inventory_path = 0
        self.check_environment()
        self.check_path_budget(self.root)
        self.logs = self.root / "logs"
        self.logs.mkdir()
        self.write(self.root / "environment.json", encoded(self.env))
        self.mount = self.mount_observation("before")
        self.assert_source_identity()
        self.source_hashes = self.source_files()
        self.write(self.root / "source-lock.json", encoded({
            "base": BASE, "subject": self.subject, "release": AUTHORITY,
            "files": self.source_hashes,
        }))
        self.safety = runpy.run_path(str(self.source / "lib/context_safety.py"))

    @staticmethod
    def write(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def check_environment(self):
        for key in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "TMPDIR",
                    "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME"):
            if not self.env.get(key):
                raise ValueError("Missing synthetic environment key: " + key)
            path = Path(self.env[key]).resolve()
            if not path.is_relative_to(self.root) or not path.is_dir():
                raise ValueError("Synthetic path is outside the explicit root: " + key)
            for ancestor in (path, *path.parents):
                info = ancestor.lstat()
                if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                    raise ValueError("Linked synthetic root refused: " + str(ancestor))
        if Path(self.env["HOME"]).resolve() != Path(self.env["USERPROFILE"]).resolve():
            raise ValueError("HOME and USERPROFILE must identify the same synthetic directory")
        if not self.env.get("PATH") or not self.env.get("PATHEXT"):
            raise ValueError("Explicit PATH/PATHEXT required")
        for key in self.env:
            if key.startswith("LINTEL_") and key != "LINTEL_POWERSHELL":
                raise ValueError("Caller LINTEL selector leaked into the fixture: " + key)
            if key.startswith(("CLAUDE_", "GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")) or key in (
                "GH_TOKEN", "GITHUB_TOKEN", "BASH_ENV", "ENV", "PYTHONPATH", "PYTHONHOME",
                "PACK_CACHE_FILE", "GIT_DIR", "GIT_WORK_TREE", "GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS",
            ):
                raise ValueError("Ambient execution selector refused: " + key)
        if self.env.get("PYTHONNOUSERSITE") != "1" or self.env.get("PYTHONDONTWRITEBYTECODE") != "1":
            raise ValueError("Python parent and children must be isolated")
        for key in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM"):
            path = Path(self.env[key]).resolve()
            if not path.is_relative_to(self.root) or path.read_bytes():
                raise ValueError("Only the owned empty Git configuration is allowed")
        if Path(self.env["GIT_CEILING_DIRECTORIES"]).resolve() != self.root:
            raise ValueError("Git discovery ceiling differs")
        ps = self.env.get("LINTEL_POWERSHELL")
        if os.name == "nt" and ps and Path(ps).name.lower() != "pwsh.exe":
            raise ValueError("An explicit PowerShell selector must name the approved pwsh.exe")

    @staticmethod
    def check_path_budget(root):
        if os.name == "nt" and len(str(root)) > WINDOWS_ROOT_BUDGET:
            raise ValueError(
                f"A23 fixture root exceeds its declared {WINDOWS_ROOT_BUDGET}-character Windows budget; "
                "no automatic relocation is permitted"
            )

    def run(self, argv, *, cwd=None, expected=0):
        self.check_environment()
        remaining = 1800 - (time.monotonic() - self.started)
        if remaining <= 0:
            raise RuntimeError("A23 evidence exceeded the Windows CI job's 1800-second budget")
        number = len(self.calls) + 1
        stem = self.logs / f"{number:04d}"
        args = [str(arg) for arg in argv]
        record = {
            "number": number, "argv": args, "cwd": str(cwd or self.root),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "lintel_input_selectors": sorted(k for k in self.env if k.startswith("LINTEL_")),
            "expected_exit": expected, "exit": None, "elapsed_seconds": None,
        }
        self.calls.append(record)
        stem.with_suffix(".json").write_bytes(encoded(record))
        start = time.monotonic()
        with stem.with_suffix(".stdout.log").open("xb") as out, stem.with_suffix(".stderr.log").open("xb") as err:
            try:
                completed = subprocess.run(args, cwd=cwd or self.root, env=self.env, stdout=out, stderr=err,
                                           timeout=min(remaining, 480), check=False)
                record["exit"] = completed.returncode
            except (OSError, subprocess.TimeoutExpired) as error:
                record["error"] = str(error)
                raise
            finally:
                record["elapsed_seconds"] = time.monotonic() - start
                record["finished_at"] = datetime.now(timezone.utc).isoformat()
                stem.with_suffix(".json").write_bytes(encoded(record))
        stdout, stderr = stem.with_suffix(".stdout.log").read_bytes(), stem.with_suffix(".stderr.log").read_bytes()
        record.update(stdout_sha256=sha(stdout), stderr_sha256=sha(stderr))
        stem.with_suffix(".json").write_bytes(encoded(record))
        if expected is not None and completed.returncode != expected:
            raise AssertionError(f"Command {number}: expected {expected}, got {completed.returncode}\n"
                                 + (stdout + stderr).decode("utf-8", "replace"))
        return subprocess.CompletedProcess(args, completed.returncode, stdout, stderr)

    def mount_observation(self, label):
        result = self.run([self.options.bash, "--noprofile", "--norc", "-c",
                           "mount | grep ' on /tmp ' || true\ntest -d /tmp\n"])
        if result.stderr:
            raise RuntimeError("Bash startup/mount warning is not acceptance:\n" + result.stderr.decode())
        self.write(self.root / f"mount-{label}.txt", result.stdout)
        return result.stdout

    def assert_source_identity(self):
        self.subject = self.run([self.options.git, "--no-pager", "-C", self.source,
                                 "rev-parse", "HEAD"]).stdout.decode().strip()
        # The dispatch base is provenance, not a history prerequisite for a shallow CI checkout.

    def source_files(self):
        listed = self.run([self.options.git, "--no-pager", "-C", self.source,
                           "ls-files", "-z"]).stdout.decode().split("\0")
        listed += ["tests/integration/universal-a23.py", "tests/integration/universal-a23.sh"]
        listed += [f"tests/fixtures/universal-a23/{name}" for name in
                   ("work.json", "spec.md", "plan.md", "tasks.md", "prompt.md", "pack.yaml")]
        return {name: sha((self.source / name).read_bytes()) for name in set(listed)
                if name and not name.startswith(".claude/plans/universal-implementation/reports/")}

    def git(self, repo, *args, expected=0):
        if not repo.resolve().is_relative_to(self.root):
            raise ValueError("Fixture Git cannot target the source or another repository")
        return self.run([self.options.git, "--no-pager", "-c", "core.autocrlf=false",
                         "-c", "core.fsmonitor=false", "-c", "init.defaultBranch=a23-fixture",
                         "-c", "user.name=Synthetic A23", "-c", "user.email=a23@example.invalid",
                         "-C", repo, *args], cwd=repo, expected=expected)

    def shell(self, bundle, repo, body, *args, expected=0):
        prefix = r'''
set -euo pipefail
source_root="$1"; target="$2"; shift 2
if command -v cygpath >/dev/null 2>&1; then
  source_root="$(cygpath -u "$source_root")"
  target="$(cygpath -u "$target")"
fi
cd "$target"
'''
        return self.run([self.options.bash, "--noprofile", "--norc", "-c", prefix + body,
                         "a23-consumer", bundle, repo, *args], cwd=repo, expected=expected)

    def install(self, name):
        repo = self.root / name
        repo.mkdir()
        self.git(repo, "init", "-q")
        self.write(repo / "unrelated.txt", b"synthetic caller sentinel\n")
        entry = [sys.executable, "-I", "-B", self.source / "bin/li-lifecycle.py",
                 "--repo", repo, "scaffold"]
        self.run([*entry, "init", "--target", repo, "--copilot"], cwd=repo)
        self.run([*entry, "check", "--target", repo, "--copilot"], cwd=repo)
        bundle = repo / ".github" / "lintel"
        for path in ("bin/li-scaffold", "bin/li-lifecycle", "bin/li-lifecycle.py",
                     "lib/copilot-env.sh", "bin/li-work-artifacts.py", "bin/li-domain-result.py",
                     "bin/li-review-evidence.py", "bin/li-review-log", "bin/li-review-read"):
            if not (bundle / path).is_file():
                raise AssertionError("Actual installed helper missing: " + path)
        return repo, bundle

    def tree(self, root):
        root = Path(root).absolute()
        if not root.is_relative_to(self.root):
            raise ValueError("Preservation inventory must stay inside the owned fixture")
        native = self.safety["native_io_path"]
        try:
            native(root).lstat()
        except FileNotFoundError:
            return {}
        root = self.safety["checked_root"](root)
        result, pending = {}, [root]
        while pending:
            directory = pending.pop()
            for entry in sorted(native(directory).iterdir(), key=lambda item: item.name):
                relative = (directory / entry.name).relative_to(root).as_posix()
                if ".git" in Path(relative).parts:
                    continue
                path = self.safety["safe_path"](root, relative)
                mode = native(path).lstat().st_mode
                if stat.S_ISDIR(mode):
                    pending.append(path)
                elif stat.S_ISREG(mode):
                    result[relative] = self.safety["read_owned"](root, relative)[1]["sha256"]
                    self.max_inventory_path = max(self.max_inventory_path, len(str(path)))
                else:
                    raise ValueError("Unsupported preservation input: " + relative)
        return result

    def link(self, name, result, *, negative=False, detail=""):
        self.links.append({"name": name, "category": "executed", "negative": negative,
                           "command_number": len(self.calls), "exit": result.returncode,
                           "detail": detail, "native_scenario": False})


BOOTSTRAP = 'source "$source_root/lib/copilot-env.sh"\nlintel_copilot_env "$PWD"\n'


@contextmanager
def altered(path, data):
    original, info = path.read_bytes(), path.stat()
    path.write_bytes(data)
    try:
        yield
    finally:
        path.write_bytes(original)
        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))


class CombinedConsumers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.neutral, cls.neutral_bundle = RUN.install("neutral")
        cls.caller, cls.bundle = RUN.install("caller")
        cls.fixture = RUN.source / "tests/fixtures/universal-a23"
        cls.home = cls.caller / ".claude/runtime/lintel-home"
        cls.pack = cls.home / "packs/a23-policy/pack.yaml"
        RUN.write(cls.pack, (cls.fixture / "pack.yaml").read_bytes())
        RUN.write(cls.caller / ".claude/profile-requirements.json",
                  encoded({"schema_version": 1, "required_pack": "a23-policy"}))
        cls.reference = json.loads(RUN.shell(cls.bundle, cls.caller, BOOTSTRAP + "profile_context_reference\n").stdout)
        cls.initial_installed = {str(bundle): RUN.tree(bundle) for bundle in (cls.neutral_bundle, cls.bundle)}
        # Reuse the accepted P09 fixture's actual test signal and installed producer imports.
        previous = sys.argv
        sys.argv = ["domain-result-handoff.py", "--root", str(cls.bundle),
                    "--bash", str(OPTIONS.bash), "--git", str(OPTIONS.git),
                    "--without-selectors", "--artifacts-root", str(RUN.root / "p09-fixture")]
        try:
            cls.data = runpy.run_path(str(RUN.source / "tests/integration/domain-result-handoff.py"))
        finally:
            sys.argv = previous
        import profile_context
        import review_contract
        cls.profile = profile_context
        cls.review = review_contract
        cls.config = profile_context.ProfileConfig(
            cls.bundle, cls.caller, cls.home, cls.home / "packs", cls.home / "packs/active-pack",
            context_id=cls.reference["context_id"])
        cls.current_pin = profile_context.context_path(cls.config)

    def child(self, name):
        child = RUN.root / name
        child.mkdir()
        RUN.write(child / "unrelated.txt", b"synthetic child sentinel\n")
        return child

    def scaffold(self, repo, bundle, child, *, prelude="", expected=0, entry="li-scaffold", extra=()):
        body = BOOTSTRAP + prelude + (
            'test -f "$source_root/bin/' + entry + '" || { echo "Required installed helper missing" >&2; exit 84; }\n'
            'bash "$source_root/bin/' + entry + '" ' +
            ("scaffold " if entry == "li-lifecycle" else "") + 'init --target "$1"\n')
        return RUN.shell(bundle, repo, body, child, *extra, expected=expected)

    def test_01_neutral_installed_caller_to_child(self):
        ref = json.loads(RUN.shell(self.neutral_bundle, self.neutral, BOOTSTRAP + "profile_context_reference\n").stdout)
        child = self.child("neutral-child")
        caller_before = RUN.tree(self.neutral)
        result = self.scaffold(self.neutral, self.neutral_bundle, child)
        observed = json.loads(result.stdout)
        self.assertEqual(observed["operation_profile_reference"], ref)
        self.assertIsNone(observed["target_profile_reference"])
        self.assertFalse(observed["required_caller_policy"])
        self.assertEqual(RUN.tree(self.neutral), caller_before)
        self.assertFalse((child / ".claude/runtime/profiles/selected.json").exists())
        self.assertEqual((child / "unrelated.txt").read_bytes(), b"synthetic child sentinel\n")
        self.assertEqual(Path(observed["store"]).parent, child.parent)
        RUN.link("installed-neutral-caller-child", result, detail="Actual installed shell -> lifecycle -> owned publication; defaults retained.")

    def test_02_required_caller_and_matching_target(self):
        for name, matching in (("required-child", False), ("matching-child", True)):
            with self.subTest(name=name):
                child = self.child(name)
                if matching:
                    RUN.write(child / ".claude/profile-requirements.json",
                              encoded({"schema_version": 1, "required_pack": "a23-policy"}))
                before, home_before = RUN.tree(self.caller), RUN.tree(self.home)
                result = self.scaffold(self.caller, self.bundle, child)
                observed = json.loads(result.stdout)
                self.assertTrue(observed["required_caller_policy"])
                self.assertEqual(observed["operation_profile_reference"], self.reference)
                self.assertEqual(observed["target_selection"]["requested"], "a23-policy")
                self.assertIsNone(observed["target_profile_reference"])
                self.assertEqual(RUN.tree(self.caller), before)
                self.assertEqual(RUN.tree(self.home), home_before)
                self.assertFalse((child / ".claude/runtime/profiles/selected.json").exists())
                self.assertFalse((child / ".claude/runtime/lintel-home/sessions").exists())
                self.assertEqual((child / "unrelated.txt").read_bytes(), b"synthetic child sentinel\n")
                RUN.link("installed-" + name, result, detail="Required caller checked as operation constraint; no child generation minted.")

    def test_03_downstream_missing_and_drifted_caller_refuse(self):
        child = self.child("refused-child")
        for kind in ("missing", "drift"):
            with self.subTest(kind=kind):
                caller_before, child_before = RUN.tree(self.caller), RUN.tree(child)
                pin, pack = self.current_pin.read_bytes(), self.pack.read_bytes()
                pin_info, pack_info = self.current_pin.stat(), self.pack.stat()
                hold = RUN.root / "held-current-profile.json"
                prelude = (
                    'mv "$PACK_CACHE_FILE" "$2"\n' if kind == "missing" else
                    'printf "\\n# A23 deliberate producer drift\\n" >> "$LINTEL_HOME/packs/a23-policy/pack.yaml"\n')
                try:
                    result = self.scaffold(self.caller, self.bundle, child, prelude=prelude,
                                           extra=(hold,), expected=2)
                    code = b"PROFILE_CONTEXT_MISSING" if kind == "missing" else b"PROFILE_DRIFT"
                    self.assertIn(code, result.stderr)
                    self.assertEqual(result.stdout, b"")
                    self.assertEqual(RUN.tree(child), child_before)
                    RUN.link("caller-pin-" + kind, result, negative=True,
                             detail="Caller bootstraps first; actual inherited pin is broken before downstream child invocation.")
                finally:
                    self.current_pin.write_bytes(pin)
                    os.utime(self.current_pin, ns=(pin_info.st_atime_ns, pin_info.st_mtime_ns))
                    self.pack.write_bytes(pack)
                    os.utime(self.pack, ns=(pack_info.st_atime_ns, pack_info.st_mtime_ns))
                    if hold.exists():
                        self.assertEqual(hold.read_bytes(), pin)
                        hold.unlink()
                self.assertEqual(RUN.tree(self.caller), caller_before)

    def test_04_conflicting_child_policy_refuses_before_writes(self):
        for kind in ("different-name", "unselected-repository-shadow"):
            with self.subTest(kind=kind):
                child = self.child(kind)
                name = "other-policy" if kind == "different-name" else "a23-policy"
                RUN.write(child / ".claude/profile-requirements.json",
                          encoded({"schema_version": 1, "required_pack": name}))
                if kind != "different-name":
                    RUN.write(child / "packs/a23-policy/pack.yaml",
                              self.pack.read_bytes() + b"roles: {source: changed-policy}\n")
                before, caller_before = RUN.tree(child), RUN.tree(self.caller)
                expected = 2 if kind == "different-name" else 0
                result = self.scaffold(self.caller, self.bundle, child, expected=expected)
                if expected:
                    self.assertIn(b"PROFILE_REQUIRED", result.stderr)
                    self.assertEqual(result.stdout, b"")
                    self.assertEqual(RUN.tree(child), before)
                else:
                    actual = self.profile.resolve_profile(self.profile.ProfileConfig(
                        self.bundle, child, self.home, self.home / "packs", self.home / "packs/active-pack"))
                    self.assertEqual(Path(actual["ancestry"][-1]["path"]), self.pack)
                    self.assertIsNone(actual["values"]["roles"]["source"])
                    self.assertEqual(json.loads(result.stdout)["operation_profile_reference"], self.reference)
                    self.assertEqual((child / "unrelated.txt").read_bytes(), b"synthetic child sentinel\n")
                self.assertEqual(RUN.tree(self.caller), caller_before)
                RUN.link("child-policy-" + kind, result, negative=bool(expected),
                         detail="Configured store precedes unselected child-repository content.")

    def test_04b_selected_same_name_policy_conflict_refuses(self):
        repo = self.child("repo-policy-caller")
        RUN.write(repo / "AGENTS.md", b"# Synthetic source-policy caller\n")
        RUN.write(repo / ".claude/profile-requirements.json",
                  encoded({"schema_version": 1, "required_pack": "a23-policy"}))
        RUN.write(repo / "packs/a23-policy/pack.yaml", self.pack.read_bytes())
        ref = json.loads(RUN.shell(self.bundle, repo, BOOTSTRAP + "profile_context_reference\n").stdout)
        self.assertEqual(ref["name"], "a23-policy")
        child = self.child("selected-source-conflict")
        RUN.write(child / ".claude/profile-requirements.json",
                  encoded({"schema_version": 1, "required_pack": "a23-policy"}))
        RUN.write(child / "packs/a23-policy/pack.yaml",
                  self.pack.read_bytes() + b"roles: {source: changed-policy}\n")
        caller_before, child_before = RUN.tree(repo), RUN.tree(child)
        home = repo / ".claude/runtime/lintel-home"
        config = self.profile.ProfileConfig(self.bundle, repo, home, home / "packs",
                                            home / "packs/active-pack", context_id=ref["context_id"])
        history = self.profile.context_path(config).parent / "history"
        entries = list(RUN.safety["native_io_path"](history).iterdir())
        self.assertTrue(entries, "Actual caller history must be present in the preservation inventory")
        for entry in entries:
            relative = (history / entry.name).relative_to(repo).as_posix()
            self.assertIn(relative, caller_before)
            self.assertEqual(caller_before[relative], RUN.safety["read_owned"](repo, relative)[1]["sha256"])
        RUN.inventory_observations.append({
            "case": "actual-selected-source-caller-history", "root_characters": len(str(RUN.root)),
            "file_count": len(caller_before),
            "history": [{"path": (history / item.name).relative_to(repo).as_posix(),
                         "logical_characters": len(str(history / item.name)),
                         "sha256": caller_before[(history / item.name).relative_to(repo).as_posix()]}
                        for item in entries],
        })
        result = self.scaffold(repo, self.bundle, child, expected=2)
        self.assertIn(b"source/content differs", result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(RUN.tree(repo), caller_before)
        self.assertEqual(RUN.tree(child), child_before)
        RUN.link("selected-same-name-policy-refused", result, negative=True,
                 detail="Actual selected caller-repo versus child-repo policy differs; no configured-store shadow.")

    def test_05_missing_helper_and_supported_alias_are_separate(self):
        child = self.child("helper-child")
        helper = self.bundle / "bin/li-scaffold"
        raw = helper.read_bytes()
        before = RUN.tree(child)
        helper.unlink()
        try:
            result = self.scaffold(self.caller, self.bundle, child, expected=84)
            self.assertIn(b"Required installed helper missing", result.stderr)
            self.assertEqual(RUN.tree(child), before)
            RUN.link("installed-missing-helper", result, negative=True, detail="Explicit preflight; no fallback helper.")
        finally:
            helper.write_bytes(raw)
        alias_child = self.child("alias-child")
        caller_before = RUN.tree(self.caller)
        result = self.scaffold(self.caller, self.bundle, alias_child, entry="li-lifecycle")
        self.assertEqual(json.loads(result.stdout)["operation_profile_reference"], self.reference)
        self.assertEqual(RUN.tree(self.caller), caller_before)
        RUN.link("installed-lifecycle-alias", result)

    def test_06_explicit_custom_home_does_not_replace_default_bridge(self):
        caller, child = self.child("custom-caller"), self.child("custom-child")
        home = RUN.root / "custom-data-home"
        entry = [sys.executable, "-I", "-B", self.bundle / "bin/li-lifecycle.py",
                 "--repo", caller, "--home", home]
        reference = json.loads(RUN.run([*entry, "profile-bind"], cwd=caller).stdout)["reference"]
        before, home_before = RUN.tree(caller), RUN.tree(home)
        result = RUN.run([*entry, "--reference", json.dumps(reference),
                          "scaffold", "init", "--target", child], cwd=caller)
        observed = json.loads(result.stdout)
        self.assertEqual(observed["operation_profile_reference"], reference)
        self.assertEqual(RUN.tree(caller), before)
        self.assertEqual(RUN.tree(home), home_before)
        self.assertIsNone(observed["target_profile_reference"])
        RUN.link("explicit-custom-home-control", result, detail="Separate explicit CLI control; primary installed bootstrap used default homes.")

    def write(self, name, data):
        RUN.write(self.caller / name, data)

    def write_json(self, name, data):
        self.write(name, encoded(data))

    def ref(self, name):
        return {"path": name, "sha256": sha((self.caller / name).read_bytes())}

    def p05(self, operation, *args, expected=0):
        return RUN.run([sys.executable, "-I", "-B", self.bundle / "bin/li-review-evidence.py",
                        operation, "--repo", self.caller, *args], cwd=self.caller, expected=expected)

    def domain(self, operation, *args, expected=0):
        return RUN.run([sys.executable, "-I", "-B", self.bundle / "bin/li-domain-result.py",
                        operation, "--repo", self.caller, *args], cwd=self.caller, expected=expected)

    def test_90_one_installed_profile_work_domain_review_resume_chain(self):
        for name in ("work.json", "spec.md", "plan.md", "tasks.md", "prompt.md"):
            self.write("specs/chosen/" + name, (self.fixture / name).read_bytes())
        self.write_json("specs/decoy/work.json", json.loads((self.fixture / "work.json").read_bytes()))
        self.write("source.txt", b"actual finite joined fixture input\n")
        RUN.git(self.caller, "add", "source.txt", "specs")
        RUN.git(self.caller, "commit", "-qm", "test: original synthetic A23 work input")
        base = RUN.git(self.caller, "rev-parse", "HEAD").stdout.decode().strip()
        profile_record = json.loads(RUN.shell(self.bundle, self.caller, BOOTSTRAP + "profile_context_json\n").stdout)
        reference = self.profile.profile_reference(profile_record)
        policy = self.profile.required_policy(profile_record)
        self.assertEqual(reference, self.reference)
        profile_command = [
            sys.executable, "-I", "-B", self.bundle / "lib/profile_context.py",
            "--source", self.bundle, "--repo", self.caller, "--home", self.home,
            "--packs", self.home / "packs", "--pointer", self.home / "packs/active-pack",
            "--reference", json.dumps({**reference, "digest": "sha256:" + "0" * 64}), "verify",
        ]
        negative = RUN.run(profile_command, cwd=self.caller, expected=2)
        self.assertIn(b"PROFILE_REFERENCE_MISMATCH", negative.stderr)
        RUN.link("P07-produced-reference-refused", negative, negative=True)
        inherited = RUN.shell(self.bundle, self.caller, BOOTSTRAP +
                              'export LINTEL_PROFILE_REFERENCE="$1"\n'
                              'source "$source_root/lib/workflow.sh"\n'
                              f'workflow_begin a23-invalid-profile full {WORK_MAP} operation=build\n',
                              json.dumps({**reference, "digest": "sha256:" + "0" * 64}),
                              expected=2)
        self.assertIn(b"PROFILE_REFERENCE_MISMATCH", inherited.stderr)
        self.assertFalse((self.caller / ".claude/runtime/state/00-state.md").exists())
        RUN.link("P07-inherited-reference-at-P08-refused", inherited, negative=True,
                 detail="Actual workflow_begin consumes the broken inherited producer reference before state writes.")
        work_args = [sys.executable, "-I", "-B", self.bundle / "bin/li-work-artifacts.py",
                     "--repo", self.caller, "--map", WORK_MAP, "--view", "context", "--package", "P09",
                     "--leaf", "T014", "--acceptance", "specs/chosen/spec.md"]
        work_result = RUN.run(work_args, cwd=self.caller)
        work = json.loads(work_result.stdout)
        self.assertEqual(work["packages"]["P09"]["leaf_ids"], ["T014"])
        self.assertEqual(work["tasks"]["T014"]["dependencies"], ["T001"])
        RUN.link("P07-P08-selected-work", work_result)
        wrong = list(work_args)
        wrong[wrong.index("T014")] = "T999"
        negative = RUN.run(wrong, cwd=self.caller, expected=1)
        self.assertIn(b"missing task", negative.stderr)
        RUN.link("P08-original-leaf-refused", negative, negative=True)
        cycle = RUN.shell(self.bundle, self.caller, BOOTSTRAP +
                          'source "$source_root/lib/workflow.sh"\n'
                          f'workflow_begin a23-chain full {WORK_MAP} operation=build\n'
                          'state_phase_begin REVIEW\n')
        RUN.link("P08-original-cycle-selected", cycle)
        requirement = {
            "id": "joined-tests", "kind": "tests", "requirement": "mandatory", "applicability": "applicable",
            "policy": {"source": "specs/chosen/spec.md", "version": "a23-fixture-1",
                       "applicability": "Synthetic original T014 evidence", "jurisdiction": None,
                       "actor": None, "effective_date": None},
        }
        prepare = {
            "work_map": WORK_MAP, "package_id": "P09", "leaf_ids": ["T014"],
            "acceptance_paths": ["specs/chosen/spec.md"], "base": base, "selection": ["source.txt"],
            "record_path": ".claude/runtime/reviews/a23-decision.json", "attempt_id": "a23-synthetic-chain",
            "builder": {"id": "synthetic-builder", "context": "synthetic-build-context"},
            "independence_required": True, "purpose": "verification_only", "profile": reference,
            "required_policy": policy, "required_controls": ["spec", "quality", "joined-tests"],
            "qa_requirements": [requirement],
        }
        self.write_json(".claude/runtime/a23/prepare.json", prepare)
        initial = json.loads(self.p05("prepare", "--request", self.caller / ".claude/runtime/a23/prepare.json").stdout)
        self.assertEqual(initial["work"], work["binding"])
        domain_path = ".claude/runtime/a23/domain-request.json"
        start_path = ".claude/runtime/state/domains/a23-chain/i0001/tq/01-start.json"
        result_path = ".claude/runtime/state/domains/a23-chain/i0001/tq/01-result.json"
        request = {
            "schema_version": 1, "kind": "domain-request", "operation_id": "a23-chain", "iteration": 1,
            "input_context": initial, "advisory_preferences": {}, "release_clearance": False,
            "domains": [{"id": "tq", "checkpoints": [{
                "id": "contract_tests_complete", "receiver": {"role": "Synthetic test receiver", "mode": "fixture-only"},
                "control_ids": ["joined-tests"], "artifacts": ["artifacts/tq.txt"],
                "start": {"path": start_path, "expected_state": None},
                "result": {"path": result_path, "expected_state": None},
            }]}],
        }
        self.write_json(domain_path, request)
        self.write_json(".claude/runtime/a23/absent.json", {"state": None})
        valid = self.domain("validate", "--file", domain_path)
        RUN.link("P08-P09-original-work-context", valid)
        cp = request["domains"][0]["checkpoints"][0]
        common = {"schema_version": 1, "request": self.ref(domain_path), "domain": "tq",
                  "checkpoint": cp["id"], "receiver": cp["receiver"],
                  "producer": initial["builder"], "provenance": "declared", "release_clearance": False}

        def publish(data, path, expected=0):
            self.write_json(".claude/runtime/a23/payload.json", data)
            return self.domain("record", "--request", domain_path, "--file", ".claude/runtime/a23/payload.json",
                               "--output", path, "--expected-state", ".claude/runtime/a23/absent.json",
                               expected=expected)

        started = publish({**common, "kind": "domain-checkpoint"}, start_path)
        self.assertEqual(json.loads(started.stdout)["verification"], "not_performed")
        test_run = RUN.run([sys.executable, "-I", "-B", "-c", self.data["CHECK_CODE"]], cwd=self.caller)
        self.assertIn(b"Ran 1 test", test_run.stderr)
        self.write("evidence/tq.stdout.log", test_run.stdout)
        self.write("evidence/tq.stderr.log", test_run.stderr)
        self.write("artifacts/tq.txt", b"Synthetic original T014: retain actual consumer evidence; no native verdict.\n")
        control = {**deepcopy(requirement), "status": "pass", "reason": "Actual reused P09 fixture unittest executed.",
                   "evidence": ["evidence/tq.stdout.log", "evidence/tq.stderr.log"],
                   "observation": {"command": json.dumps(test_run.args), "executed": 1, "failed": 0,
                                   "skipped": 0, "exit_code": test_run.returncode}}
        record = {**common, "kind": "domain-result", "start": self.ref(start_path), "status": "pass",
                  "reason": "Synthetic fixture observation, not native specialist execution.",
                  "controls": [control], "evidence": self.review.evidence_manifest(self.caller, [control]),
                  "artifacts": [self.ref("artifacts/tq.txt")],
                  "decisions": [{"requirement": "R1", "rationale": "Preserve the actual local check signal.",
                                 "artifact": "artifacts/tq.txt"}],
                  "limitations": ["Test-only actors; no independently observed native result."],
                  "next": {"owner": "fixture reviewer", "action": "Exercise the existing exact review contract."}}
        bad = deepcopy(record)
        bad["controls"][0]["kind"] = "check"
        negative = publish(bad, result_path, expected=2)
        self.assertIn(b"immutable", negative.stderr)
        self.assertFalse((self.caller / result_path).exists())
        RUN.link("P09-typed-producer-mismatch-refused", negative, negative=True)
        publish(record, result_path)
        final_request = {**prepare, "selection": ["source.txt", domain_path, start_path, result_path, "artifacts", "evidence"]}
        self.write_json(".claude/runtime/a23/final-prepare.json", final_request)
        final = json.loads(self.p05("prepare", "--request", self.caller / ".claude/runtime/a23/final-prepare.json").stdout)
        self.write_json(".claude/runtime/a23/final-context.json", final)
        domain_args = ["--request", domain_path, "--expected", ".claude/runtime/a23/final-context.json",
                       "--profile-home", self.home, "--profile-packs", self.home / "packs",
                       "--profile-pointer", self.home / "packs/active-pack"]
        verified = self.domain("verify", *domain_args)
        produced = json.loads(verified.stdout)
        self.assertTrue(produced["ok"])
        self.assertFalse(produced["release_clearance"])
        self.assertEqual(produced["review"], "not_evaluated")
        RUN.link("P09-real-result-to-P05-QA", verified)
        with altered(self.caller / "specs/chosen/tasks.md",
                     (self.caller / "specs/chosen/tasks.md").read_bytes().replace(b"Preserve the API", b"Change the API")):
            negative = self.domain("verify", *domain_args, expected=3)
            self.assertFalse(json.loads(negative.stdout)["ok"])
            RUN.link("P08-work-drift-at-P09-consumer", negative, negative=True)
        self.write_json(".claude/runtime/a23/qa-inputs.json", {"controls": produced["qa"]["controls"]})
        qa_args = ["--expected", self.caller / ".claude/runtime/a23/final-context.json",
                   "--input", self.caller / ".claude/runtime/a23/qa-inputs.json"]
        qa = self.p05("qa", *qa_args)
        self.assertEqual(json.loads(qa.stdout), produced["qa"])
        RUN.link("P09-actual-QA-consumed-by-P05", qa)
        wrong = deepcopy(produced["qa"]["controls"])
        wrong[0]["kind"] = "check"
        with altered(self.caller / ".claude/runtime/a23/qa-inputs.json", encoded({"controls": wrong})):
            negative = self.p05("qa", *qa_args, expected=1)
            self.assertIn(b"immutable", negative.stderr)
            RUN.link("P09-P05-QA-retype-refused", negative, negative=True)
        zero = deepcopy(produced["qa"]["controls"])
        zero[0]["observation"]["executed"] = 0
        with altered(self.caller / ".claude/runtime/a23/qa-inputs.json", encoded({"controls": zero})):
            negative = self.p05("qa", *qa_args, expected=3)
            RUN.link("P05-zero-run-refused", negative, negative=True)
        checks = [{
            "id": name, "kind": "check", "requirement": "mandatory", "applicability": "applicable",
            "status": "pass", "reason": "Synthetic review data only; not independent review of Lintel.",
            "policy": requirement["policy"], "evidence": ["artifacts/tq.txt"], "observation": {},
        } for name in ("spec", "quality")]
        decision = {
            "schema_version": 2, "skill": "review", "status": "pass",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "Synthetic installed review fixture, not a native verdict.",
            "context": final, "reviewer": {"id": "synthetic-reviewer", "context": "synthetic-review-context"},
            "provenance": "declared", "controls": [*checks, *produced["qa"]["controls"]],
            "coverage": {"T014": final["required_controls"]},
            "evidence": self.review.evidence_manifest(self.caller, [*checks, *produced["qa"]["controls"]]),
        }
        self.write_json(".claude/runtime/reviews/a23-decision.json", decision)
        receipt = {"schema_version": 1, "kind": "host", "source": "synthetic-test-data-not-host-authentication",
                   "reference": "A23 regression fixture; independent native acceptance is not asserted.",
                   "record_digest": self.review.content_digest(decision), "attempt_id": final["attempt_id"],
                   "builder": final["builder"], "reviewer": decision["reviewer"]}
        self.write_json(".claude/runtime/a23/synthetic-corroboration.json", receipt)
        RUN.shell(self.bundle, self.caller, BOOTSTRAP +
                  'bash "$source_root/bin/li-review-log" --file .claude/runtime/reviews/a23-decision.json\n')
        reader = ('bash "$source_root/bin/li-review-read" --skill review '
                  '--expected .claude/runtime/a23/final-context.json '
                  '--corroboration .claude/runtime/a23/synthetic-corroboration.json --gate-json\n')
        consumed = RUN.shell(self.bundle, self.caller, BOOTSTRAP + reader)
        self.assertTrue(json.loads(consumed.stdout)["ok"])
        RUN.link("P05-actual-publisher-latest-reader", consumed,
                 detail="Synthetic declared actors/corroboration exercise real data consumers, not native independence.")
        with altered(self.caller / "source.txt", b"later product edit\n"):
            negative = RUN.shell(self.bundle, self.caller, BOOTSTRAP + reader, expected=3)
            self.assertFalse(json.loads(negative.stdout)["ok"])
            RUN.link("P05-exact-content-drift-refused", negative, negative=True)
        resume_body = (BOOTSTRAP + 'source "$source_root/lib/workflow.sh"\n' + reader +
                       'state_append REVIEW DONE next=SHIP evidence=synthetic-a23\n'
                       f'workflow_resume a23-chain {WORK_MAP}\n')
        resumed = RUN.shell(self.bundle, self.caller, resume_body)
        result = json.loads(resumed.stdout.decode().splitlines()[-1])
        self.assertEqual(result["phase"], "SHIP")
        self.assertEqual(result["profile"], reference)
        self.assertFalse(result["release_clearance"])
        RUN.link("P05-current-review-to-P08-resume", resumed,
                 detail="Test caller observes the latest reader, appends phase state and invokes resume; no automatic review-to-resume product link or SHIP.")
        ledger = self.caller / ".claude/runtime/state/00-state.md"
        before = ledger.read_bytes()
        negative = RUN.shell(self.bundle, self.caller, BOOTSTRAP +
                             'source "$source_root/lib/workflow.sh"\n'
                             'workflow_resume a23-chain specs/decoy/work.json\n', expected=2)
        self.assertIn(b"different initiative", negative.stderr)
        self.assertEqual(ledger.read_bytes(), before)
        RUN.link("P08-resume-wrong-map-refused", negative, negative=True)
        later = deepcopy(decision)
        later.update(status="fail", reason="Synthetic later rejection must revoke prior fixture clearance.")
        self.write_json(".claude/runtime/reviews/a23-rejected.json", later)
        RUN.shell(self.bundle, self.caller, BOOTSTRAP +
                  'bash "$source_root/bin/li-review-log" --file .claude/runtime/reviews/a23-rejected.json\n')
        refused = RUN.shell(self.bundle, self.caller, BOOTSTRAP + reader, expected=3)
        self.assertFalse(json.loads(refused.stdout)["ok"])
        RUN.link("P05-later-rejection-refused", refused, negative=True)
        negative_resume = RUN.shell(self.bundle, self.caller, BOOTSTRAP +
            'source "$source_root/lib/workflow.sh"\n' +
            'if ' + reader.rstrip() + '; then exit 91; else rc=$?; test "$rc" = 3; fi\n'
            'state_append REVIEW BLOCKED reason=actual-latest-reader-refused\n'
            f'workflow_resume a23-chain {WORK_MAP}\n')
        self.assertEqual(json.loads(negative_resume.stdout.decode().splitlines()[-1])["phase"], "REVIEW")
        RUN.link("P05-refusal-keeps-resume-at-REVIEW", negative_resume, negative=True,
                 detail="Completed command; its observed reader refusal prevents advancing to SHIP.")

    @classmethod
    def tearDownClass(cls):
        for bundle in (cls.neutral_bundle, cls.bundle):
            if RUN.tree(bundle) != cls.initial_installed[str(bundle)]:
                raise AssertionError("Installed source changed during consumer verification")


class PreservationGuards(unittest.TestCase):
    def test_optional_selector_and_unrelated_selector_refusal(self):
        original = dict(RUN.env)
        try:
            RUN.env.pop("LINTEL_POWERSHELL", None)
            RUN.check_environment()
            if os.name == "nt":
                RUN.env["LINTEL_POWERSHELL"] = r"C:\Program Files\PowerShell\7\pwsh.exe"
                RUN.check_environment()
                RUN.env["LINTEL_POWERSHELL"] = r"C:\synthetic\powershell.exe"
                with self.assertRaisesRegex(ValueError, "explicit PowerShell selector"):
                    RUN.check_environment()
                RUN.env.pop("LINTEL_POWERSHELL")
            RUN.env["LINTEL_HOME"] = str(RUN.root / "unapproved-selector")
            with self.assertRaisesRegex(ValueError, "Caller LINTEL selector"):
                RUN.check_environment()
        finally:
            RUN.env = original

    def test_native_inventory_includes_and_detects_long_file_change(self):
        fixture = RUN.root / "inventory-probe"
        fixture.mkdir()
        # Keep the parent accessible to legacy enumeration so the old leaf test
        # silently omits the long file, rather than only failing to walk a directory.
        relative = "/".join(["n" * 80] * 2 + ["1-" + "a" * 64 + ".json"])
        long_file = fixture / relative
        self.assertGreater(len(str(long_file)), 260)
        safety = RUN.safety
        original, changed = b"original owned long-path content\n", b"changed long-path content\n"
        safety["atomic_write"](fixture, relative, original, expected=None, check_expected=True)
        safety["atomic_write"](fixture, "short.txt", b"unrelated preserved\n", expected=None, check_expected=True)
        before = RUN.tree(fixture)
        self.assertEqual(before, {relative: sha(original), "short.txt": sha(b"unrelated preserved\n")})
        try:
            safety["atomic_write"](fixture, relative, changed)
            after = RUN.tree(fixture)
            self.assertEqual(after.keys(), before.keys())
            self.assertNotEqual(after, before)
            self.assertEqual(after[relative], sha(changed))
            self.assertEqual(after["short.txt"], before["short.txt"])
        finally:
            safety["atomic_write"](fixture, relative, original)
        self.assertEqual(RUN.tree(fixture), before)
        RUN.check_path_budget(RUN.root)
        if os.name == "nt":
            with self.assertRaisesRegex(ValueError, "no automatic relocation"):
                RUN.check_path_budget(RUN.root / ("b" * WINDOWS_ROOT_BUDGET))
        RUN.inventory_observations.append({
            "case": "native-long-file-mutation", "root_characters": len(str(RUN.root)),
            "logical_file_characters": len(str(long_file)), "file_count": len(before),
            "before": before, "changed": after, "restored": RUN.tree(fixture),
        })


def main():
    global OPTIONS, RUN
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--bash", type=Path, required=True)
    parser.add_argument("--git", type=Path, required=True)
    OPTIONS = parser.parse_args()
    RUN = LocalRun(OPTIONS)
    suite = unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromTestCase(PreservationGuards),
        unittest.defaultTestLoader.loadTestsFromTestCase(CombinedConsumers),
    ])
    with (RUN.root / "suite.log").open("x", encoding="utf-8") as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    sys.stderr.write((RUN.root / "suite.log").read_text())
    after_mount = RUN.mount_observation("after")
    if after_mount != RUN.mount:
        raise RuntimeError("Shared /tmp mapping changed; retained roots, no repair attempted")
    if RUN.source_files() != RUN.source_hashes:
        raise RuntimeError("Executing source changed; evidence cannot be accepted")
    duration = time.monotonic() - RUN.started
    outcome = {
        "source_base": BASE, "subject": RUN.subject, "release": AUTHORITY,
        "evidence_category": "executed", "scenario_kind": "installed synthetic producer-consumer tests",
        "methods": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skips": len(result.skipped), "commands": len(RUN.calls), "links": RUN.links,
        "duration_seconds": duration, "windows_ci_budget_seconds": 1800,
        "budget_fraction": duration / 1800, "full_ci_fit": "unverified; other suites share the job budget",
        "source_and_tmp_mount_preserved": True,
        "path_budget": {"root_characters": len(str(RUN.root)),
                        "windows_fixture_root_maximum": WINDOWS_ROOT_BUDGET,
                        "max_inventoried_file_characters": RUN.max_inventory_path,
                        "scope": "test-root admission only, not a product or Git compatibility guarantee"},
        "inventory_observations": RUN.inventory_observations,
        "native_scenario": False, "independent_review": "pending coordinator-assigned reviewer",
        "release_clearance": False, "cleanup": "retained all owned roots and logs; no /tmp mutation",
    }
    RUN.write(RUN.root / "summary.json", encoded(outcome))
    print(encoded(outcome).decode())
    return 0 if result.testsRun and result.wasSuccessful() and not result.skipped and duration < 1800 else 1


if __name__ == "__main__":
    raise SystemExit(main())
