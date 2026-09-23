# component: universal-profile-scenario-preparation
# implements: ADR-0026, ADR-0028, ADR-0029, ADR-0031
# intent: .claude/plans/universal-implementation/packages/P14.md
# constraints: preparation only; synthetic roots; no actors, installer, decisions or clearance
# last_intent_review: 2026-09-23
"""Freeze and verify P14 inputs. This is not a native scenario execution engine."""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import stat
import subprocess
import sys
import time
import unittest


FIXTURE_PATH = "tests/fixtures/universal-profile-scenarios"
MAP = ".claude/plans/universal-implementation/work.json"
ORIGINAL = ("A24.1", "A24.2", "A24.3", "A24.4")
AUTHORITY_PATHS = (
    MAP, ".claude/plans/universal-implementation/spec.md",
    ".claude/plans/universal-implementation/plan.md",
    ".claude/plans/universal-implementation/prompt.md",
    ".claude/plans/universal-implementation/packages/P14.md",
)
LEAVES = ["T001", "T002", "T003"]
OWNER = {"id": "00181e45-3979-4f33-bd31-562e63dc48f0",
         "context": "8fa44739-f562-4213-a6c4-fb7719fc8c9e"}
DIRECTORIES = (
    "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "TMPDIR",
    "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME",
    "LINTEL_HOME", "LINTEL_PACKS_DIR", "LINTEL_AUDIT_DIR", "LINTEL_STATE_DIR",
)
FORBIDDEN = (
    "GH_TOKEN", "GITHUB_TOKEN", "BASH_ENV", "ENV", "PYTHONPATH", "PYTHONHOME",
    "PACK_CACHE_FILE", "CLAUDE_PLUGIN_ROOT", "CLAUDE_SESSION_ID", "GIT_DIR",
    "GIT_WORK_TREE", "GIT_CONFIG_PARAMETERS",
)
WINDOWS_FIXTURE_GIT = {
    "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.longpaths",
    "GIT_CONFIG_VALUE_0": "true",
}
OPTIONS = None
SOURCE = FIXTURES = RUN = None
LOCK = {}
COMMANDS = []
SAFETY = PROFILE = REVIEW = CAPS = DOMAIN = None
WORK = EVIDENCE = SNAPSHOT = None


def encoded(value) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True,
                       allow_nan=False) + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inspected(path: Path, root: Path, *, exists=True) -> Path:
    path = path.absolute()
    if not path.is_relative_to(root) or ".." in path.parts:
        raise ValueError(f"Path is outside the declared synthetic root: {path}")
    for item in (path, *path.parents):
        if item.exists():
            info = item.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError(f"Linked synthetic path refused: {item}")
    if exists and not path.exists():
        raise ValueError(f"Synthetic path does not exist: {path}")
    return path


def inspect_environment(env: dict, root: Path, source: Path, target: Path) -> None:
    if root == Path(root.anchor) or not root.is_dir():
        raise ValueError("An explicit existing non-root synthetic directory is required")
    for key in DIRECTORIES:
        if not env.get(key) or not inspected(Path(env[key]), root).is_dir():
            raise ValueError(f"Missing synthetic {key}")
    for key in FORBIDDEN:
        if key in env:
            raise ValueError(f"Ambient variable refused: {key}")
    git_config = {key: value for key, value in env.items()
                  if key == "GIT_CONFIG_COUNT" or key.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))}
    if git_config and (os.name != "nt" or not target.is_relative_to(root / "cases")
                       or git_config != WINDOWS_FIXTURE_GIT):
        raise ValueError("Only command-scoped longpaths in owned Windows fixture repos are allowed")
    if any(key.startswith(("CLAUDE_", "COPILOT_", "AZURE_", "AWS_", "SSH_")) for key in env):
        raise ValueError("Ambient host/credential selector refused")
    if Path(env["P14_ISOLATION_ROOT"]) != root:
        raise ValueError("Isolation identity changed")
    if Path(env["LINTEL_SOURCE_ROOT"]) != source or Path(env["LINTEL_REPO_ROOT"]) != target:
        raise ValueError("Explicit source/target identity disagrees")
    if source == target or source.is_relative_to(target) or target.is_relative_to(source):
        raise ValueError("Trusted source and target must be separate")
    for key in ("LINTEL_ACTIVE_PACK_FILE", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM"):
        inspected(Path(env[key]), root, exists=key != "LINTEL_ACTIVE_PACK_FILE")
    if Path(env["LINTEL_ACTIVE_PACK_FILE"]).parent != Path(env["LINTEL_PACKS_DIR"]):
        raise ValueError("Active pointer is not owned by the declared pack root")
    if Path(env["LINTEL_STATE_DIR"]) != target / ".claude" / "runtime" / "state":
        raise ValueError("Caller state selector escaped this fixture's target")
    if not target.is_relative_to(Path(env["GIT_CEILING_DIRECTORIES"])):
        raise ValueError("Git discovery ceiling does not contain the target")
    if not env.get("PATH") or not env.get("PATHEXT"):
        raise ValueError("Explicit PATH and PATHEXT are required")
    if env.get("PYTHONNOUSERSITE") != "1" or env.get("PYTHONDONTWRITEBYTECODE") != "1":
        raise ValueError("User-site/bytecode isolation is required")
    if env.get("GIT_CONFIG_NOSYSTEM") != "1" or env.get("GIT_TERMINAL_PROMPT") != "0":
        raise ValueError("Git configuration/prompt isolation is required")


def environment(base: Path, target: Path) -> dict:
    home, temp = base / "home", base / "temp"
    env = {key: os.environ[key] for key in (
        "SystemRoot", "WINDIR", "SystemDrive", "COMSPEC", "PATH", "PATHEXT",
    ) if key in os.environ}
    env.update({
        "HOME": str(home), "USERPROFILE": str(home),
        "HOMEDRIVE": home.drive, "HOMEPATH": str(home)[len(home.drive):],
        "APPDATA": str(home / "AppData" / "Roaming"),
        "LOCALAPPDATA": str(home / "AppData" / "Local"),
        "XDG_CONFIG_HOME": str(home / ".config"),
        "XDG_DATA_HOME": str(home / ".local" / "share"),
        "XDG_CACHE_HOME": str(home / ".cache"),
        "XDG_STATE_HOME": str(home / ".local" / "state"),
        "TEMP": str(temp), "TMP": str(temp), "TMPDIR": str(temp),
        "USER": "synthetic-p14", "USERNAME": "synthetic-p14",
        "P14_ISOLATION_ROOT": str(RUN), "P14_PYTHON": str(Path(sys.executable)),
        "LINTEL_SOURCE_ROOT": str(SOURCE), "LINTEL_REPO_ROOT": str(target),
        "LINTEL_HOME": str(home / ".lintel"),
        "LINTEL_PACKS_DIR": str(home / ".lintel" / "packs"),
        "LINTEL_ACTIVE_PACK_FILE": str(home / ".lintel" / "packs" / "active-pack"),
        "LINTEL_AUDIT_DIR": str(target / ".claude" / "runtime" / "audit"),
        "LINTEL_STATE_DIR": str(target / ".claude" / "runtime" / "state"),
        "LINTEL_PROFILE_CONTEXT": "p14-preparation",
        "LINTEL_OPERATOR": "synthetic-p14", "LINTEL_ASCII": "1",
        "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
        "GIT_CONFIG_GLOBAL": str(base / "empty-git-config"),
        "GIT_CONFIG_SYSTEM": str(base / "empty-git-config"),
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CEILING_DIRECTORIES": str(base),
        "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never",
        "GIT_AUTHOR_NAME": "Synthetic P14", "GIT_COMMITTER_NAME": "Synthetic P14",
        "GIT_AUTHOR_EMAIL": "p14@example.invalid", "GIT_COMMITTER_EMAIL": "p14@example.invalid",
        "GIT_AUTHOR_DATE": "2026-09-23T00:00:00+00:00",
        "GIT_COMMITTER_DATE": "2026-09-23T00:00:00+00:00",
    })
    for key in DIRECTORIES:
        path = inspected(Path(env[key]), RUN, exists=False)
        path.mkdir(parents=True, exist_ok=True)
    (base / "empty-git-config").write_bytes(b"")
    if os.name == "nt" and target.is_relative_to(RUN / "cases"):
        # Git's command scope reaches unmodified provider subprocesses, without
        # persisting config or applying fixture options to source-checkout Git.
        env.update(WINDOWS_FIXTURE_GIT)
    inspect_environment(env, RUN, SOURCE, target)
    return env


def command(argv, *, env, cwd, expected=0):
    inspect_environment(env, RUN, Path(env["LINTEL_SOURCE_ROOT"]), Path(env["LINTEL_REPO_ROOT"]))
    if Path(cwd) == OPTIONS.root and any(key in env for key in WINDOWS_FIXTURE_GIT):
        raise ValueError("Fixture Git options may not reach source-checkout commands")
    number = len(COMMANDS) + 1
    stem = RUN / "logs" / f"{number:04d}"
    argv = [str(item) for item in argv]
    record = {"number": number, "argv": argv, "cwd": str(cwd),
              "home": env["HOME"], "target": env["LINTEL_REPO_ROOT"],
              "ceiling": env["GIT_CEILING_DIRECTORIES"],
              "git_command_configuration": {key: env[key] for key in WINDOWS_FIXTURE_GIT if key in env},
              "started_at": datetime.now(timezone.utc).isoformat(),
              "expected_exit": expected, "exit": None, "elapsed_seconds": None}
    COMMANDS.append(record)
    stem.with_suffix(".json").write_bytes(encoded(record))
    started = time.monotonic()
    with stem.with_suffix(".stdout.log").open("xb") as stdout, \
            stem.with_suffix(".stderr.log").open("xb") as stderr:
        try:
            result = subprocess.run(argv, cwd=cwd, env=env, stdout=stdout, stderr=stderr,
                                    check=False, timeout=90)
        except (OSError, subprocess.TimeoutExpired) as error:
            record["error"] = str(error)
            raise
        finally:
            record["elapsed_seconds"] = time.monotonic() - started
            stem.with_suffix(".json").write_bytes(encoded(record))
    record["exit"] = result.returncode
    stem.with_suffix(".json").write_bytes(encoded(record))
    out, err = stem.with_suffix(".stdout.log").read_bytes(), stem.with_suffix(".stderr.log").read_bytes()
    if expected is not None and result.returncode != expected:
        raise AssertionError(f"Command {number}: expected {expected}, got {result.returncode}\n"
                             + (out + err).decode("utf-8", errors="replace"))
    return subprocess.CompletedProcess(argv, result.returncode, out, err)


def git(repo, env, *args, expected=0):
    options = []
    if Path(repo).is_relative_to(RUN):
        inspected(Path(repo), RUN)
        if Path(repo) != Path(env["LINTEL_REPO_ROOT"]):
            raise ValueError("Git fixture target differs from the declared owned target")
        options = ["-c", "core.autocrlf=false", "-c", "core.fsmonitor=false",
                   "-c", f"core.hooksPath={RUN / 'empty-hooks'}"]
    return command([
        OPTIONS.git, "--no-pager", *options, "-C", repo, *args,
    ], env=env, cwd=repo, expected=expected)


def verify_files(root: Path, files: list) -> None:
    for item in files:
        path = inspected(root / item["frozen"], root)
        if sha(path.read_bytes()) != item["sha256"]:
            raise ValueError(f"Frozen source/fixture drift: {item['frozen']}")


def assert_lock() -> None:
    verify_files(RUN, LOCK["files"])
    for item in LOCK["files"]:
        if sha((OPTIONS.root / item["origin"]).read_bytes()) != item["sha256"]:
            raise ValueError(f"Declared current source/fixture drift: {item['origin']}")
    for item in LOCK["original_authorities"]:
        if sha((OPTIONS.root / item["path"]).read_bytes()) != item["sha256"]:
            raise ValueError(f"Current authority changed during observation: {item['path']}")
    verify_files(RUN, LOCK["original_authorities"])


def freeze() -> None:
    global LOCK
    original_fixtures = OPTIONS.root / FIXTURE_PATH
    base = (original_fixtures / "base-source.txt").read_text(encoding="ascii").strip()
    env = dict(os.environ)
    (RUN / "logs").mkdir()
    (RUN / "empty-hooks").mkdir()
    subject = git(OPTIONS.root, env, "rev-parse", "HEAD").stdout.decode().strip()
    paths = (original_fixtures / "source-paths.txt").read_text(encoding="utf-8").splitlines()
    files = []
    for relative in paths:
        data = (OPTIONS.root / relative).read_bytes()
        committed = git(OPTIONS.root, env, "show", f"{subject}:{relative}").stdout
        if data.replace(b"\r\n", b"\n") != committed.replace(b"\r\n", b"\n"):
            raise ValueError(f"Selected production source differs from declared current revision: {relative}")
        target = SOURCE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files.append({"origin": relative, "frozen": target.relative_to(RUN).as_posix(),
                      "sha256": sha(data), "subject_blob_sha256": sha(committed)})
    for path in sorted(original_fixtures.rglob("*")):
        if path.is_file():
            relative = path.relative_to(original_fixtures)
            target = FIXTURES / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            data = path.read_bytes()
            target.write_bytes(data)
            files.append({"origin": path.relative_to(OPTIONS.root).as_posix(),
                          "frozen": target.relative_to(RUN).as_posix(), "sha256": sha(data)})
    for extension in ("py", "sh"):
        relative = "tests/integration/universal-profile-scenarios." + extension
        harness = (OPTIONS.root / relative).read_bytes()
        name = "harness." + extension
        (RUN / name).write_bytes(harness)
        files.append({"origin": relative, "frozen": name, "sha256": sha(harness)})
    authorities = []
    for relative in AUTHORITY_PATHS:
        data = (OPTIONS.root / relative).read_bytes()
        committed = git(OPTIONS.root, env, "show", f"{subject}:{relative}").stdout
        target = RUN / "authority-inputs" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        authorities.append({"path": relative, "frozen": target.relative_to(RUN).as_posix(),
                            "sha256": sha(data), "subject_blob_sha256": sha(committed)})
    LOCK = {"category": "pre-observation-fixture-lock", "base": base,
            "base_role": "historical-experiment-provenance",
            "subject_revision": subject,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "files": files, "original_authorities": authorities,
            "original_ids": list(ORIGINAL), "fixture_ids": LEAVES,
            "native_scenario": "not_run", "independent_review": "not_run"}
    (RUN / "experiment-lock.json").write_bytes(encoded(LOCK))
    assert_lock()
    for args in ([sys.executable, "--version"], [OPTIONS.git, "--version"],
                 [OPTIONS.bash, "--noprofile", "--norc", "--version"]):
        command(args, env=env, cwd=Path(env["LINTEL_REPO_ROOT"]))


SHELL_PREFIX = r"""
set -euo pipefail
if command -v cygpath >/dev/null 2>&1; then
  for key in LINTEL_SOURCE_ROOT LINTEL_REPO_ROOT LINTEL_HOME LINTEL_PACKS_DIR LINTEL_ACTIVE_PACK_FILE LINTEL_AUDIT_DIR LINTEL_STATE_DIR; do
    printf -v "$key" '%s' "$(cygpath -m "${!key}")"
    export "$key"
  done
fi
source "$LINTEL_SOURCE_ROOT/lib/copilot-env.sh"
"""


class Preparation(unittest.TestCase):
    maxDiff = 2000

    def setUp(self):
        assert_lock()
        self.saved_environment = dict(os.environ)
        self.base = RUN / "cases" / self._testMethodName
        self.base.mkdir(parents=True)
        self.target = self.base / "target"
        shutil.copytree(FIXTURES / "seed", self.target)
        self.env = environment(self.base, self.target)
        os.environ.clear()
        os.environ.update(self.env)
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/p14-synthetic")
        self.git("add", ".")
        self.git("commit", "-qm", "test: establish unchanged P14 synthetic seed")
        self.base_ref = self.git("rev-parse", "HEAD").stdout.decode().strip()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.saved_environment)
        assert_lock()

    def git(self, *args, expected=0):
        return git(self.target, self.env, *args, expected=expected)

    def shell(self, script, *, expected=0, env=None):
        return command([OPTIONS.bash, "--noprofile", "--norc", "-c", SHELL_PREFIX + script],
                       env=env or self.env, cwd=self.target, expected=expected)

    def select(self, name=None):
        if name:
            source = SAFETY.safe_path(SAFETY.checked_root(FIXTURES), "packs/" + name)
            destination = SAFETY.safe_path(SAFETY.checked_root(self.target), "packs/" + name)
            shutil.copytree(SAFETY.native_io_path(source), SAFETY.native_io_path(destination))
            self.write(".claude/profile-requirements.json",
                       encoded({"schema_version": 1, "required_pack": name}))
        result = self.shell(
            'lintel_copilot_env "$LINTEL_REPO_ROOT"\nprofile_context_json\n')
        self.profile = json.loads(result.stdout)
        self.reference = PROFILE.profile_reference(self.profile)
        self.policy = PROFILE.required_policy(self.profile)
        self.config = PROFILE.ProfileConfig(
            SOURCE, self.target, Path(self.env["LINTEL_HOME"]), Path(self.env["LINTEL_PACKS_DIR"]),
            Path(self.env["LINTEL_ACTIVE_PACK_FILE"]), context_id="p14-preparation",
        )
        return self.profile["profile"]["values"]

    def write(self, relative, data):
        SAFETY.atomic_write(SAFETY.checked_root(self.target), relative, data)

    def profile_sources(self):
        values = self.profile["profile"]["values"]
        sources = []
        for field, filename in (("opinions.source", "inventory.md"),
                                ("knowhow.source", "acceptance.md")):
            value = PROFILE.field_value(values, field)
            if value is None:
                continue
            origin = self.profile["profile"]["provenance"][field]
            directory = Path(origin["path"]).parent / value
            path = directory / filename
            relative = path.relative_to(self.target).as_posix()
            data = SAFETY.read_owned(SAFETY.checked_root(self.target), relative, 65536)[0]
            self.assertTrue(data.strip())
            sources.append({"field": field, "value": value, "origin": origin,
                            "path": relative, "sha256": sha(data),
                            "consumed_text": data.decode("utf-8")})
        return sources

    def context(self, *, work_map="work.json", package_id="P1", leaf_ids=LEAVES):
        sources = self.profile_sources()
        mapping = WORK["load_work_map"](self.target, Path(work_map))
        hooks = PROFILE.field_value(self.profile["profile"]["values"], "compliance.hooks")
        permitted = {"inventory-atomic-publication", "inventory-owned-recovery"}
        self.assertTrue(set(hooks) <= permitted, "unrecognized policy control must be reconciled")
        obligations = [("inventory-business", "tests", "spec.md")]
        if hooks:
            self.assertEqual(PROFILE.field_value(self.profile["profile"]["values"], "compliance.mode"), "hard")
            policy_path = next(item["path"] for item in sources if item["field"] == "opinions.source")
            obligations += [(name, "tests" if name.endswith("publication") else "check", policy_path)
                            for name in hooks]
        requirements = [{
            "id": name, "kind": kind, "requirement": "mandatory", "applicability": "applicable",
            "policy": {"source": source, "version": "p14-fixture-1",
                       "applicability": "This frozen synthetic inventory task",
                       "jurisdiction": None, "actor": None, "effective_date": None},
        } for name, kind, source in obligations]
        request = {
            "work_map": work_map, "package_id": package_id, "leaf_ids": list(leaf_ids),
            "acceptance_paths": [mapping["spec"], mapping["plan"], *[item["path"] for item in sources]],
            "base": self.base_ref, "selection": ["inventory.py", "plan.md", "data"],
            "record_path": ".claude/runtime/reviews/p14-future.json",
            "attempt_id": "p14-preparation-only", "builder": OWNER,
            "independence_required": True, "purpose": "verification_only",
            "profile": self.reference, "required_policy": self.policy,
            "required_controls": ["spec", "quality", *[item["id"] for item in requirements]],
            "qa_requirements": requirements,
        }
        self.expected = EVIDENCE["prepare"](self.target, request)
        REVIEW.verify_context(self.target, self.expected)
        return self.expected

    def test_c01_source_and_fixture_lock(self):
        self.assertEqual(LOCK["base"], "9f8885be132b5af0f579dd64019d32aef5501d45")
        self.assertEqual(WORK["SOURCE_ROOT"], SOURCE)
        self.assertEqual(Path(PROFILE.__file__).parent, SOURCE / "lib")
        isolated_copy = self.base / "tampered-copy"
        isolated_copy.mkdir()
        original = (RUN / LOCK["files"][0]["frozen"]).read_bytes()
        (isolated_copy / "probe").write_bytes(original + b"\n")
        with self.assertRaisesRegex(ValueError, "Frozen source/fixture drift"):
            verify_files(isolated_copy, [{"frozen": "probe", "sha256": sha(original)}])
        assert_lock()

    def test_c02_isolation_and_process_boundaries(self):
        inspect_environment(self.env, RUN, SOURCE, self.target)
        for key, value in (
            ("HOME", str(RUN.parent)), ("LINTEL_ACTIVE_PACK_FILE", str(RUN.parent / "active-pack")),
            ("LINTEL_STATE_DIR", str(RUN)), ("GH_TOKEN", "synthetic-denied"),
            ("LINTEL_SOURCE_ROOT", str(self.target)),
        ):
            with self.subTest(key=key), self.assertRaises(ValueError):
                inspect_environment({**self.env, key: value}, RUN, SOURCE, self.target)
        result = command([sys.executable, "-I", "-B", "-c",
                          "import os,pathlib; print(pathlib.Path.home()); print(os.environ['USERPROFILE'])"],
                         env=self.env, cwd=self.target)
        self.assertEqual(result.stdout.decode().splitlines(), [self.env["HOME"]] * 2)
        self.assertNotIn("LINTEL_PROFILE_REFERENCE", self.env)
        config_before = (self.target / ".git" / "config").read_bytes()
        self.git("config", "--local", "--get", "core.longpaths", expected=1)
        if os.name == "nt":
            scope = self.git("config", "--show-scope", "--get", "core.longpaths").stdout
            self.assertEqual(scope.decode().split(), ["command", "true"])
            with self.assertRaises(ValueError):
                inspect_environment({**self.env, "GIT_CONFIG_KEY_0": "core.hooksPath"},
                                    RUN, SOURCE, self.target)
            with self.assertRaises(ValueError):
                command([OPTIONS.git, "--version"], env=self.env, cwd=OPTIONS.root)
        self.assertEqual((self.target / ".git" / "config").read_bytes(), config_before)

    def test_c03_original_authority_and_identical_seed(self):
        original = WORK["work_context"](OPTIONS.root, Path(MAP))
        self.assertEqual(original["artifacts"]["tasks"], ".claude/plans/universal-implementation/plan.md")
        self.assertTrue(set((*ORIGINAL, "A23.4", "A23.5")) <= set(original["tasks"]))
        REVIEW.bind_work(
            OPTIONS.root, work_map=MAP, package_id="P14", leaf_ids=ORIGINAL,
            acceptance_paths=[original["artifacts"]["spec"], original["artifacts"]["plan"]])
        self.assertEqual(original, WORK["work_context"](OPTIONS.root, Path(MAP)))
        assert_lock()
        for name in ("neutral", "rapid-development", "strict-change"):
            destination = self.base / name
            shutil.copytree(FIXTURES / "seed", destination)
            for item in (FIXTURES / "seed").rglob("*"):
                if item.is_file():
                    self.assertEqual(item.read_bytes(), (destination / item.relative_to(FIXTURES / "seed")).read_bytes())
            work = WORK["work_context"](destination, Path("work.json"))
            self.assertEqual(work["incomplete_ids"], LEAVES)
            self.assertEqual(work["packages"]["P1"]["leaf_ids"], LEAVES)
            self.assertFalse(work["release_clearance"])
            self.assertFalse(set(ORIGINAL) & set(work["tasks"]))

    def test_c03_legitimate_progress_requirement_and_approval_controls(self):
        for item in LOCK["original_authorities"]:
            self.write(item["path"], (RUN / item["frozen"]).read_bytes())
        self.select()
        plan_path = ".claude/plans/universal-implementation/plan.md"
        original = (self.target / plan_path).read_bytes().decode("utf-8")
        classified = REVIEW.classify_markdown(original)
        spans = REVIEW._task_progress_spans(classified, ["A24.1"])
        self.assertEqual(len(spans), 1)
        span = next(iter(spans.values()))
        incomplete = original[:span.start] + " " + original[span.end:]
        self.write(plan_path, incomplete.encode("utf-8"))
        context = self.context(work_map=MAP, package_id="P14", leaf_ids=ORIGINAL)
        before = WORK["work_context"](self.target, Path(MAP))
        self.assertFalse(before["tasks"]["A24.1"]["complete"])
        completed = incomplete[:span.start] + "x" + incomplete[span.end:]
        self.write(plan_path, completed.encode("utf-8"))
        after = WORK["work_context"](self.target, Path(MAP))
        self.assertEqual(before["tasks"].keys(), after["tasks"].keys())
        self.assertTrue(after["tasks"]["A24.1"]["complete"])
        REVIEW.verify_context(self.target, context)
        self.assertEqual((self.target / plan_path).read_bytes(), completed.encode("utf-8"))
        line_end = completed.find("\n", span.end)
        self.assertGreater(line_end, span.end)
        if completed[line_end - 1] == "\r":
            line_end -= 1
        changed = completed[:line_end] + " Synthetic requirement change." + completed[line_end:]
        self.write(plan_path, changed.encode("utf-8"))
        with self.assertRaisesRegex(REVIEW.ContractError, "acceptance sources changed"):
            REVIEW.verify_context(self.target, context)
        self.write(plan_path, completed.encode("utf-8"))
        mapping = REVIEW.load_json((self.target / MAP).read_text(encoding="utf-8"))
        mapping["status"] = "DRAFT"
        self.write(MAP, encoded(mapping))
        with self.assertRaisesRegex(REVIEW.ContractError, "not approved"):
            REVIEW.verify_context(self.target, context)
        assert_lock()

    def test_c04_resolved_fields_and_consumed_policy_sources(self):
        observations = []
        for name in (None, "rapid-development", "strict-change"):
            if name is not None:
                profile_base = self.base / name
                self.target = profile_base / "target"
                shutil.copytree(FIXTURES / "seed", self.target)
                self.env = environment(profile_base, self.target)
                os.environ.clear()
                os.environ.update(self.env)
                self.git("init", "-q")
                self.git("add", ".")
                self.git("commit", "-qm", "test: establish identical P14 seed")
                self.base_ref = self.git("rev-parse", "HEAD").stdout.decode().strip()
            values = self.select(name)
            context = self.context()
            fields = ("compliance.mode", "compliance.hooks", "navigation.high_risk_workflows",
                      "opinions.source", "knowhow.source")
            effect = {field: {"value": PROFILE.field_value(values, field),
                              "provenance": self.profile["profile"]["provenance"][field]}
                      for field in fields}
            risk = self.shell(
                'lintel_copilot_env "$LINTEL_REPO_ROOT"\n'
                'source "$LINTEL_SOURCE_ROOT/lib/orientator-routing.sh"\n'
                'assess_risk plan "$(resolve_pack_field navigation.high_risk_workflows)"\n'
            ).stdout.decode()
            observations.append({
                "selection": name or "neutral", "reference": self.reference,
                "effects": effect, "plan_risk": risk, "sources": self.profile_sources(),
                "qa_requirements": context["qa_requirements"],
                "base_request_sha256": sha((self.target / "spec.md").read_bytes()),
                "seed_sha256": sha((self.target / "data" / "events.jsonl").read_bytes()),
                "category": "synthetic-preparation", "native_scenario": "not_run",
            })
        self.assertEqual([item["plan_risk"] for item in observations], ["high", "medium", "high"])
        self.assertEqual([len(item["qa_requirements"]) for item in observations], [1, 1, 3])
        self.assertEqual([len(item["sources"]) for item in observations], [0, 1, 2])
        self.assertEqual(len({item["base_request_sha256"] for item in observations}), 1)
        self.assertEqual(len({item["seed_sha256"] for item in observations}), 1)
        (RUN / "profile-effects.json").write_bytes(encoded(observations))

    def test_c04_required_missing_conflict_and_drift(self):
        self.write(".claude/profile-requirements.json",
                   encoded({"schema_version": 1, "required_pack": "missing"}))
        result = self.shell('lintel_copilot_env "$LINTEL_REPO_ROOT"\n', expected=2)
        self.assertIn(b"PROFILE_REQUIRED", result.stderr)
        self.select("strict-change")
        bad = {**self.env, "LINTEL_PROFILE_PACK": "rapid-development"}
        result = self.shell('lintel_copilot_env "$LINTEL_REPO_ROOT"\n', env=bad, expected=2)
        self.assertIn(b"PROFILE_", result.stderr)
        manifest = self.target / "packs" / "strict-change" / "pack.yaml"
        before = manifest.stat()
        manifest.write_bytes(manifest.read_bytes().replace(b"mode: hard", b"mode: advisory"))
        os.utime(manifest, ns=(before.st_atime_ns, before.st_mtime_ns))
        result = self.shell('lintel_copilot_env "$LINTEL_REPO_ROOT"\n', expected=2)
        self.assertIn(b"PROFILE_DRIFT", result.stderr)
        self.assertEqual(result.stdout, b"")

    def test_c05_fresh_process_verification_and_missing_pin(self):
        self.select("strict-change")
        self.write("profile-reference.json", encoded(self.reference))
        env = dict(self.env)
        env.pop("LINTEL_PROFILE_CONTEXT")
        script = ('source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
                  'verify_profile_context "$LINTEL_REPO_ROOT/profile-reference.json"\n')
        result = self.shell(script, env=env)
        self.assertEqual(json.loads(result.stdout), self.reference)
        current = PROFILE.context_path(self.config)
        SAFETY.native_io_path(current).unlink()
        result = self.shell(script, env=env, expected=2)
        self.assertIn(b"PROFILE_", result.stderr)
        self.assertFalse(SAFETY.native_io_path(current).exists())

    def test_c06_work_binding_and_policy_text_drift(self):
        self.select("strict-change")
        context = self.context()
        work = WORK["work_context"](self.target, Path("work.json"), package_id="P1",
                                    leaf_ids=LEAVES, acceptance_paths=context["work"]["acceptance_paths"])
        self.assertEqual(work["binding"], context["work"])
        with self.assertRaises(ValueError):
            WORK["work_context"](self.target, Path("work.json"), package_id="P1", leaf_ids=["T999"])
        path = self.profile_sources()[0]["path"]
        self.write(path, (self.target / path).read_bytes() + b"\nChanged policy text.\n")
        with self.assertRaisesRegex(REVIEW.ContractError, "acceptance sources changed"):
            REVIEW.verify_context(self.target, context)

    def test_c07_owned_read_and_snapshot_recovery(self):
        self.write("owned.txt", b"before\n")
        self.write("unrelated.txt", b"preserve me\n")
        root = SAFETY.checked_root(self.target)
        self.assertEqual(SAFETY.read_owned(root, "owned.txt", 1024)[0], b"before\n")
        with self.assertRaises(ValueError):
            SAFETY.read_owned(root, "../unrelated.txt")
        store = self.base / "recovery"
        store.mkdir()
        first = SNAPSHOT["create_snapshot"](root, store, ["owned.txt"])
        self.write("owned.txt", b"attributable change\n")
        SNAPSHOT["bind_result"](root, store, first["id"],
                                {"owned.txt": SAFETY.file_state(root, "owned.txt")})
        SNAPSHOT["restore_snapshot"](root, store, first["id"])
        self.assertEqual((root / "owned.txt").read_bytes(), b"before\n")
        second = SNAPSHOT["create_snapshot"](root, store, ["owned.txt"])
        self.write("owned.txt", b"second owned change\n")
        SNAPSHOT["bind_result"](root, store, second["id"],
                                {"owned.txt": SAFETY.file_state(root, "owned.txt")})
        self.write("owned.txt", b"unrelated late edit\n")
        with self.assertRaises(ValueError):
            SNAPSHOT["restore_snapshot"](root, store, second["id"])
        self.assertEqual((root / "owned.txt").read_bytes(), b"unrelated late edit\n")
        self.assertEqual((root / "unrelated.txt").read_bytes(), b"preserve me\n")

    def test_c08_typed_missing_zero_skipped_and_failed_evidence(self):
        self.select()
        context = self.context()
        requirement = context["qa_requirements"][0]
        self.write("mechanical-check.log", b"Synthetic control-validator input; not a native result.\n")
        control = {**deepcopy(requirement), "status": "pass",
                   "reason": "Deliberately incomplete synthetic negative control.",
                   "evidence": ["mechanical-check.log"], "observation": {
                       "command": "synthetic-declared-command-not-native", "executed": 0,
                       "failed": 0, "skipped": 0, "exit_code": 0,
                   }}
        for observation in (
            {}, {"executed": 0, "failed": 0, "skipped": 0, "exit_code": 0},
            {"executed": 1, "failed": 0, "skipped": 1, "exit_code": 0},
            {"executed": 1, "failed": 1, "skipped": 0, "exit_code": 1},
        ):
            item = deepcopy(control)
            item["observation"] = {"command": "synthetic-negative", **observation}
            result = REVIEW.evaluate_controls([item], required_policy=self.policy)
            self.assertTrue(result["blocked"])
        qa = {"schema_version": 2, "context_digest": REVIEW.content_digest(context),
              "controls": [deepcopy(control)],
              "evidence": REVIEW.evidence_manifest(self.target, [control])}
        qa["controls"][0]["kind"] = "check"
        with self.assertRaisesRegex(REVIEW.ContractError, "immutable fields"):
            REVIEW.verify_qa(self.target, qa, expected=context)
        (self.base / "expected.json").write_bytes(encoded(context))
        absent = EVIDENCE["read_gate"](argparse.Namespace(
            expected=self.base / "expected.json", log=self.base / "missing-review.jsonl",
            skill="review", corroboration=None, repo=self.target, days=None))
        self.assertFalse(absent["ok"])

    def test_c09_declared_host_is_not_execution_or_review(self):
        registry = CAPS.load_registry(SOURCE / "lib" / "cli-tiers.yaml")
        session = {
            "schema_version": 1, "session_id": OWNER["id"], "surface": "copilot-app",
            "host_version": None, "work_map": MAP, "profile_ref": None,
            "bindings": {
                "read": {"tool": "functions.view", "available": True, "permission": "allowed"},
                "edit": {"tool": "functions.apply_patch", "available": True, "permission": "allowed"},
                "shell": {"tool": "functions.powershell", "available": True, "permission": "allowed"},
                "delegate": {"tool": "functions.create_session", "available": True, "permission": "ask"},
            },
            "isolation": {"kind": "none", "attributable": False, "evidence": None},
        }
        result = CAPS.resolve(registry, session)
        self.assertFalse(result["executed"])
        self.assertEqual(result["execution_mode"], "approval-required")
        self.assertEqual(result["independent_review"], "outstanding")
        session["bindings"]["delegate"]["permission"] = "denied"
        self.assertEqual(CAPS.resolve(registry, session)["execution_mode"], "blocked")
        session["bindings"].pop("delegate")
        self.assertEqual(CAPS.resolve(registry, session)["execution_mode"], "manual-handoff")
        self.assertEqual(CAPS.describe(registry, "copilot-app")["operations"]["hooks"]["observed"]["status"], "not_run")

    def test_c10_mechanical_pause_resume_keeps_original_identity(self):
        self.select("strict-change")
        self.shell(
            'lintel_copilot_env "$LINTEL_REPO_ROOT"\n'
            'source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"\n'
            'workflow_begin p14-mechanical full work.json operation=build\n'
            'state_phase_begin PLAN next=BUILD\n')
        result = self.shell(
            'source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"\n'
            'workflow_resume p14-mechanical work.json\n')
        resumed = json.loads(result.stdout)
        self.assertEqual(resumed["phase"], "PLAN")
        self.assertEqual(resumed["profile"], self.reference)
        self.assertEqual(resumed["work_map"], "work.json")
        self.assertFalse(resumed["release_clearance"])
        self.write("different.json", (self.target / "work.json").read_bytes())
        result = self.shell(
            'source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"\n'
            'workflow_resume p14-mechanical different.json\n', expected=2)
        self.assertIn(b"different initiative", result.stderr)

    def test_c11_strict_domain_request_without_manufactured_result(self):
        self.select("strict-change")
        context = self.context()
        prefix = ".claude/runtime/state/domains/p14-inventory/i0001"
        request = {
            "schema_version": 1, "kind": "domain-request", "operation_id": "p14-inventory",
            "iteration": 1, "input_context": context, "advisory_preferences": {},
            "release_clearance": False, "domains": [{"id": "tq", "checkpoints": [{
                "id": "inventory-acceptance", "receiver": {"role": "TQ", "mode": "contract-test"},
                "control_ids": [item["id"] for item in context["qa_requirements"]],
                "artifacts": ["plan.md"],
                "start": {"path": prefix + "/start.json", "expected_state": None},
                "result": {"path": prefix + "/result.json", "expected_state": None},
            }]}],
        }
        self.assertEqual(DOMAIN.validate_request(request), request)
        changed = deepcopy(request)
        changed["domains"][0]["checkpoints"][0]["control_ids"].pop()
        with self.assertRaises(DOMAIN.DomainError):
            DOMAIN.validate_request(changed)
        self.write("domain-request.json", encoded(request))
        current = deepcopy(context)
        current["snapshot"] = REVIEW.snapshot(
            self.target, base=self.base_ref,
            selection=[*context["snapshot"]["selection"], "domain-request.json"],
            record_path=context["snapshot"]["record_path"])
        outcome = DOMAIN.verify_result(self.target, "domain-request.json",
                                       expected=current, profile_config=self.config)
        self.assertTrue(outcome["blocked"])
        self.assertIn("checkpoint evidence unavailable", " ".join(outcome["problems"]))
        self.assertFalse((self.target / prefix).exists())
        self.assertIsNone(REVIEW.select_latest([], skill="review", work_map="work.json", package_id="P1"))

    def oracle(self, group, program=None, expected=0):
        args = [sys.executable, "-I", "-B", FIXTURES / "acceptance.py", "--group", group,
                "--scratch", self.base / f"oracle-{group}-{len(COMMANDS):04d}"]
        if program:
            args += ["--program", program]
        result = command(args, env=self.env, cwd=self.target, expected=expected)
        observation = json.loads(result.stdout)
        self.assertGreater(observation["tests"], 0)
        self.assertEqual(observation["skipped"], 0)
        return observation

    def test_c12_oracle_self_checks_and_unimplemented_seed(self):
        observation = self.oracle("self")
        self.assertEqual(observation["tests"], 2)
        negative = self.oracle("business", self.target / "inventory.py", expected=1)
        self.assertEqual(negative["tests"], 11)
        self.assertGreater(negative["failures"] + negative["errors"], 0)
        self.assertEqual((self.target / "inventory.py").read_bytes(),
                         (FIXTURES / "seed" / "inventory.py").read_bytes())

    def test_c13_atomic_equivalent_is_not_business_success(self):
        toy = (
            "import argparse, os, pathlib, tempfile\n"
            "p=argparse.ArgumentParser(); p.add_argument('--input'); p.add_argument('--output')\n"
            "a=p.parse_args(); output=pathlib.Path(a.output)\n"
            "fd, name=tempfile.mkstemp(dir=output.parent)\n"
            "with os.fdopen(fd, 'wb') as f: f.write(b'P14 TOY, NOT INVENTORY\\n')\n"
            "os.replace(name, output)\n"
        )
        self.write("atomic-toy.py", toy.encode())
        positive = self.oracle("atomic", self.target / "atomic-toy.py")
        self.assertEqual(positive["tests"], 2)
        business = self.oracle("business", self.target / "atomic-toy.py", expected=1)
        self.assertGreater(business["errors"] + business["failures"], 0)
        self.write("direct-toy.py", toy.replace(
            "os.replace(name, output)", "output.write_bytes(pathlib.Path(name).read_bytes())").encode())
        negative = self.oracle("atomic", self.target / "direct-toy.py", expected=1)
        self.assertEqual(negative["failures"], 2)


def main() -> int:
    global OPTIONS, RUN, SOURCE, FIXTURES, SAFETY, PROFILE, REVIEW, CAPS, DOMAIN, WORK, EVIDENCE, SNAPSHOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--git", type=Path, required=True)
    parser.add_argument("--bash", type=Path, required=True)
    OPTIONS = parser.parse_args()
    OPTIONS.root, RUN = OPTIONS.root.resolve(), OPTIONS.run_root.resolve()
    if (RUN / "experiment-lock.json").exists():
        parser.error("Evidence root already used; retain it and select a new explicit root")
    inspect_environment(dict(os.environ), RUN, OPTIONS.root, Path(os.environ["LINTEL_REPO_ROOT"]))
    for executable in (OPTIONS.git, OPTIONS.bash, Path(sys.executable)):
        if not executable.is_absolute() or not executable.is_file():
            parser.error(f"Explicit inspected executable required: {executable}")
    SOURCE, FIXTURES = RUN / "source", RUN / "fixtures"
    freeze()
    outer = environment(RUN / "driver", RUN / "driver" / "target")
    os.environ.clear()
    os.environ.update(outer)
    sys.path.insert(0, str(SOURCE / "lib"))
    import context_safety
    import profile_context
    import review_contract
    import client_capabilities
    import domain_result
    SAFETY, PROFILE, REVIEW, CAPS, DOMAIN = (
        context_safety, profile_context, review_contract, client_capabilities, domain_result)
    WORK = runpy.run_path(str(SOURCE / "bin" / "li-work-artifacts.py"))
    EVIDENCE = runpy.run_path(str(SOURCE / "bin" / "li-review-evidence.py"))
    SNAPSHOT = runpy.run_path(str(SOURCE / "bin" / "li-snapshot.py"))
    started = time.monotonic()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Preparation)
    with (RUN / "preparation.log").open("x", encoding="utf-8") as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    sys.stderr.write((RUN / "preparation.log").read_text(encoding="utf-8"))
    assert_lock()
    summary = {
        "category": "synthetic-preparation", "tests": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "elapsed_seconds": time.monotonic() - started,
        "commands": len(COMMANDS), "nonzero_exits": [
            {"number": item["number"], "exit": item["exit"], "expected": item["expected_exit"]}
            for item in COMMANDS if item["exit"] != 0],
        "lock_sha256": sha((RUN / "experiment-lock.json").read_bytes()),
        "native_scenarios": "not_run", "independent_review": "not_run",
        "native_interventions": None, "native_rework": None, "native_elapsed": None,
        "native_usage": None, "release_clearance": False,
    }
    (RUN / "summary.json").write_bytes(encoded(summary))
    print(encoded(summary).decode())
    return 0 if result.testsRun and not result.skipped and result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
