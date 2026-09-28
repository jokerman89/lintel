#!/usr/bin/env python3
# component: reusable-patterns-pack-test-harness
# implements: ADR-0038, ADR-0029
# intent: .claude/plans/reusable-patterns/contract.md
# constraints: synthetic temporary roots only; the environment is built from scratch, never the real home
# last_intent_review: 2026-09-28
"""Hermetic fixture for launcher and pack-origin tests (pack lane, cards 2.1.a-2.1.d).

Every run copies the trusted source files into a directory whose name contains spaces
and shell metacharacters, and runs `bin/li-pattern` there with synthetic HOME,
USERPROFILE, LINTEL_HOME, TEMP/TMP/TMPDIR, APPDATA, LOCALAPPDATA and XDG roots.
Fixture digests use the module's own `content_digest`; they are never recomputed here.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
import patterns as p  # noqa: E402

AWKWARD = "roots it's $x (y) & z"
SOURCE_FILES = (
    "lib/patterns.py", "lib/profile_context.py", "lib/native_paths.py", "lib/context_safety.py",
    "lib/pack-resolver.sh", "lib/paths.sh", "lib/pack-schema.yaml", "lib/profile-context-schema.json",
    "bin/li-pattern", "bin/li-pattern.py", "bin/_audit.sh", "packs/_default/pack.yaml",
    ".claude-plugin/plugin.json",
)
HOST_KEYS = ("PATH", "PATHEXT", "SYSTEMROOT", "SystemRoot", "WINDIR", "COMSPEC", "LANG", "LC_ALL")
TS = "2026-09-01T00:00:00Z"
BASE_MANIFEST = ("name: {name}\nversion: 1.0.0\n{extends}voice: {{default_tier: internal}}\n"
                 "compliance: {{mode: advisory}}\nnavigation: {{default_workflow: cycle}}\n{extra}")


def bash_executable() -> str:
    candidate = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
    if not candidate:
        raise RuntimeError("bash is required for launcher tests")
    return candidate


def tree_digest(root: Path) -> dict:
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*")) if path.is_file()}


def make_pattern(pid, version="1.0.0", status="approved", requirements=None, includes=()):
    value = {
        "schema_version": 1, "id": pid, "version": version, "status": status,
        "summary": f"Summary of {pid}", "owner": "platform team", "applies_to": {},
        "includes": list(includes),
        "sources": [{"kind": "operator-statement", "ref": "stated", "root": "statement", "section": "",
                     "observed_at": TS, "confidence": "confirmed", "reuse": "internal use"}],
        "requirements": [{"id": "R-1", "level": "must", "text": f"{pid} rule", "verify": "Inspect it."}]
        if requirements is None else requirements,
        "guidance": "", "assets": [],
    }
    if status != "draft":
        value["approval"] = {"by": "architecture board", "reference": "ADR-0038", "at": TS}
    return value


def ref(source, pattern):
    return {"source": source, "id": pattern["id"], "version": pattern["version"],
            "sha256": p.content_digest(pattern)}


def binding(bid, uses, role="required"):
    return {"id": bid, "when": {}, "use": uses, "role": role, "approved_by": "lead", "approval_ref": "decision-1"}


def codes(report, severity=None):
    return [item["code"] for item in report.get("diagnostics", [])
            if severity is None or item.get("severity") == severity]


def _remove_tree(path: Path) -> None:
    """Windows may briefly hold just-written files (indexing/scanning); retry, then fail loudly."""
    for attempt in range(20):
        try:
            shutil.rmtree(path)
            return
        except FileNotFoundError:
            return
        except OSError:
            if attempt == 19:
                raise
            time.sleep(0.25)


def posix_spelling(path: Path) -> str:
    """The launcher shell's own spelling: /c/... under MSYS, else native (asked of that bash, not PATH)."""
    body = 'if command -v cygpath >/dev/null 2>&1; then cygpath -u -- "$1"; else printf "%s\\n" "$1"; fi'
    return subprocess.run([bash_executable(), "-c", body, "spelling", str(path)], capture_output=True, check=True,
                          timeout=30, stdin=subprocess.DEVNULL).stdout.decode("utf-8").rstrip("\n")


class Harness:
    def __init__(self, testcase, *, git=True, root_name=AWKWARD):
        base = Path(tempfile.mkdtemp(prefix="lintel-pack-lane-")).resolve()
        testcase.addCleanup(_remove_tree, base)
        self.root = base / root_name
        self.source = self.root / "installed source"
        for relative in SOURCE_FILES:
            target = self.source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        self.user = self.root / "user profile"
        self.home = self.user / ".lintel"
        self.packs = self.home / "packs"
        self.temp = self.root / "temp"
        for directory in (self.packs, self.temp, self.user / "AppData" / "Roaming",
                          self.user / "AppData" / "Local", self.user / "xdg"):
            directory.mkdir(parents=True, exist_ok=True)
        self.repo = self.root / "work repo"
        self.repo.mkdir()
        self.inputs = self.root / "inputs"
        self.inputs.mkdir()
        self.session = None
        self.extra_env: dict[str, str] = {}
        if git:
            self.git("init", "-q", cwd=self.repo)

    # -- environment
    def env(self, **extra) -> dict:
        env = {key: value for key, value in os.environ.items() if key in HOST_KEYS}
        env.update(HOME=str(self.user), USERPROFILE=str(self.user), LINTEL_HOME=str(self.home),
                   TEMP=str(self.temp), TMP=str(self.temp), TMPDIR=self.temp.as_posix(),
                   APPDATA=str(self.user / "AppData" / "Roaming"), LOCALAPPDATA=str(self.user / "AppData" / "Local"),
                   XDG_CONFIG_HOME=str(self.user / "xdg" / "config"), XDG_DATA_HOME=str(self.user / "xdg" / "data"),
                   XDG_CACHE_HOME=str(self.user / "xdg" / "cache"), XDG_STATE_HOME=str(self.user / "xdg" / "state"),
                   GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(self.root / "gitconfig"))
        if self.session:
            env["LINTEL_SESSION_ID"] = self.session
        env.update(self.extra_env)
        env.update(extra)
        return {key: value for key, value in env.items() if value is not None}

    def git(self, *args, cwd):
        subprocess.run(["git", *args], cwd=cwd, env=self.env(), check=True, capture_output=True, timeout=60)

    # -- packs
    def pack(self, name, *, extends=None, extra=""):
        directory = self.packs / name
        directory.mkdir(parents=True, exist_ok=True)
        text = BASE_MANIFEST.format(name=name, extends=f"extends: {extends}\n" if extends else "", extra=extra)
        (directory / "pack.yaml").write_text(text, encoding="utf-8", newline="\n")
        return directory

    def select(self, name):
        (self.packs / "active-pack").write_text(name + "\n", encoding="utf-8", newline="\n")

    def legacy_neutral(self):
        """The bundled neutral manifest as it was before `patterns.source: null` existed."""
        manifest = self.source / "packs/_default/pack.yaml"
        text = manifest.read_text(encoding="utf-8")
        start = text.index("# ─── Reusable patterns")
        end = text.index("\n", text.index("  source: null", start)) + 1
        manifest.write_text(text[:start] + text[end:], encoding="utf-8", newline="\n")
        return manifest

    # -- catalogs
    def publish(self, directory, source_id, patterns, bindings=(), includes=(), name="catalog.json"):
        directory = Path(directory)
        entries = []
        for pattern in patterns:
            relative = f"{pattern['id']}/{pattern['version']}/pattern.json"
            path = directory / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(pattern), encoding="utf-8")
            entries.append({"id": pattern["id"], "version": pattern["version"], "path": relative,
                            "sha256": p.content_digest(pattern), "summary": pattern["summary"],
                            "status": pattern["status"], "applies_to": pattern["applies_to"]})
        catalog = {"schema_version": 1, "source_id": source_id, "entries": entries, "includes": list(includes),
                   "bindings": list(bindings), "lifecycle": []}
        directory.mkdir(parents=True, exist_ok=True)
        (directory / name).write_text(json.dumps(catalog), encoding="utf-8")
        return catalog

    @property
    def repo_patterns(self):
        return self.repo / ".claude" / "patterns"

    def write_input(self, name, value):
        path = self.inputs / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def context(self, **facts):
        return self.write_input("context.json", {"schema_version": 1, "facts": facts,
                                                 "evidence": {key: "brief.md" for key in facts}})

    # -- execution
    def launch(self, *args, cwd=None, **env):
        """Run the copied launcher; returns (exit code, parsed stdout or None, stderr)."""
        result = subprocess.run([bash_executable(), (self.source / "bin/li-pattern").as_posix(), *map(str, args)],
                                cwd=cwd or self.repo, env=self.env(**env), capture_output=True, timeout=120,
                                stdin=subprocess.DEVNULL)
        out = result.stdout.decode("utf-8")
        try:
            parsed = json.loads(out) if out.strip() else None
        except ValueError:
            parsed = None
        return result.returncode, parsed, result.stderr.decode("utf-8", "replace")

    def cli(self, *args, cwd=None):
        """The core CLI directly, for explicit --roots-file checks."""
        result = subprocess.run([sys.executable, "-I", "-B", str(self.source / "bin/li-pattern.py"), *map(str, args)],
                                cwd=cwd or self.root, env=self.env(), capture_output=True, timeout=120,
                                stdin=subprocess.DEVNULL)
        return result.returncode, json.loads(result.stdout.decode("utf-8")), result.stderr.decode("utf-8", "replace")

    def accessor(self, script, *args, repo=None):
        """Run an existing pack-resolver.sh accessor against the copied source."""
        return self.shell('source "$1/lib/pack-resolver.sh" || exit 9; shift; ' + script, *args, repo=repo)

    def shell(self, body, *args, repo=None, **env):
        """Run a Bash snippet with $1 = the copied source root and explicit roots."""
        result = subprocess.run([bash_executable(), "-c", body, "harness", self.source.as_posix(), *map(str, args)],
                                cwd=self.root, capture_output=True, timeout=120, stdin=subprocess.DEVNULL,
                                env=self.env(LINTEL_SOURCE_ROOT=self.source.as_posix(),
                                             LINTEL_REPO_ROOT=(repo or self.repo).as_posix(), **env))
        return result.returncode, result.stdout.decode("utf-8"), result.stderr.decode("utf-8", "replace")
