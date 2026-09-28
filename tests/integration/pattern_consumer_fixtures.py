#!/usr/bin/env python3
# component: reusable-patterns-consumer-test-fixtures
# implements: ADR-0038
# intent: .claude/plans/reusable-patterns/plan.md
# constraints: synthetic temporary roots only; isolated HOME/USERPROFILE/LINTEL_HOME/TEMP/TMP/APPDATA/LOCALAPPDATA/XDG; no network, installs or real packs
# last_intent_review: 2026-09-28
"""Synthetic fixtures shared by the workflow (V09) and visual (V10, V11) pattern tests.

Catalog files are written the way a reviewed repository or pack would contain them; every
decision is then made by the real `lib/patterns.py` resolver, `bin/li-pattern.py` CLI and
`lib/pattern_visual.py` adapter. Nothing here re-implements validation or precedence.
"""
from __future__ import annotations

import datetime as dt
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
import patterns as p  # noqa: E402
import pattern_visual as pv  # noqa: E402

CLI = ROOT / "bin" / "li-pattern.py"
LAUNCHER = ROOT / "bin" / "li-pattern"
CONTRACT = ROOT / "skills" / "pattern" / "references" / "consumer-contract.md"
TODAY = dt.date(2026, 9, 28)
NOW = dt.datetime(2026, 9, 28, 1, 2, 3, tzinfo=dt.timezone.utc)
TS = "2026-09-01T00:00:00Z"


def statement(text="The operator stated this expectation."):
    return {"kind": "operator-statement", "ref": text, "root": "statement", "section": "",
            "observed_at": TS, "confidence": "confirmed", "reuse": "internal use"}


def clause(cid, level, setting=None, value=None, text=None):
    record = {"id": cid, "level": level, "text": text or f"{cid} text", "verify": f"check {cid}"}
    if setting is not None:
        record.update(setting=setting, value=value)
    return record


def make_pattern(pid, *, version="1.0.0", status="approved", applies_to=None, requirements=None,
                 sources=None, assets=(), summary=None, **extra):
    value = {"schema_version": 1, "id": pid, "version": version, "status": status,
             "summary": summary or f"Summary of {pid}", "owner": "platform team",
             "applies_to": {} if applies_to is None else applies_to, "includes": [],
             "sources": [statement()] if sources is None else sources,
             "requirements": [clause("R-1", "must")] if requirements is None else requirements,
             "guidance": "", "assets": list(assets)}
    if status != "draft":
        value["approval"] = {"by": "architecture board", "reference": "ADR-0038", "at": TS}
    value.update(extra)
    return value


def ctx(**facts):
    return {"schema_version": 1, "facts": dict(facts), "evidence": {key: "brief.md" for key in facts}}


def ref(source, pattern):
    return {"source": source, "id": pattern["id"], "version": pattern["version"],
            "sha256": p.content_digest(pattern)}


def binding(bid, uses, role="required", when=None):
    return {"id": bid, "when": when or {}, "use": uses, "role": role, "approved_by": "lead",
            "approval_ref": "decision-1"}


def codes(report, severity=None):
    return [item["code"] for item in report.get("diagnostics", [])
            if severity is None or item.get("severity") == severity]


def tree_digest(root: Path) -> dict:
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*")) if path.is_file()}


def cli_commands() -> set:
    """Subcommands the installed CLI actually accepts; missing ones are pending, never mocked."""
    return set(_cli_subparsers())


def cli_options(command: str) -> set:
    """Option strings a CLI subcommand accepts (for additive options that arrive with the core)."""
    parser = _cli_subparsers().get(command)
    return {option for action in parser._actions for option in action.option_strings} if parser else set()


def _cli_subparsers() -> dict:
    import importlib.util
    spec = importlib.util.spec_from_file_location("li_pattern_cli", CLI)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for action in module.build_parser()._actions:
        if getattr(action, "choices", None):
            return dict(action.choices)
    return {}


class Fixture:
    """Temporary repository, personal home and synthetic neutral pack, fully isolated."""

    def __init__(self, testcase: unittest.TestCase):
        self._tmp = tempfile.TemporaryDirectory(prefix="lintel-pattern-consumer-")
        testcase.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        self.repo = self.root / "repo with spaces"
        self.repo_patterns.mkdir(parents=True)
        self.home = self.root / "home"
        self.lintel_home = self.home / "lintel"
        for path in (self.lintel_home, self.home / "app", self.home / "local", self.root / "tmp"):
            path.mkdir(parents=True)
        self.packs = self.root / "packs"
        self.packs.mkdir()
        self.pack_context = self.neutral_context()
        self.launched_envelope = None

    # ---- roots
    def manifest(self, name):
        directory = self.packs / name
        directory.mkdir(parents=True, exist_ok=True)
        data = f"name: {name}\nversion: 1.0.0\n".encode("utf-8")
        (directory / "pack.yaml").write_bytes(data)
        return {"pack": name, "version": "1.0.0", "root": directory.as_posix(),
                "manifest_sha256": hashlib.sha256(data).hexdigest()}

    def neutral_context(self):
        return {"schema_version": 1, "status": "neutral", "identity": {"name": "_default", "version": "1.0.0"},
                "source": {"state": "absent", "value": None, "origin": None},
                "ancestry": [self.manifest("_default")], "diagnostics": []}

    def pack_source(self, name="team", source="patterns/catalog.json"):
        ancestor = self.manifest(name)
        self.pack_context = {"schema_version": 1, "status": "resolved", "identity": {"name": name, "version": "1.0.0"},
                             "source": {"state": "value", "value": source,
                                        "origin": f"{self.packs.as_posix()}/{name}/pack.yaml"},
                             "ancestry": [ancestor], "diagnostics": []}
        return self.packs / name / "patterns"

    @property
    def repo_patterns(self):
        return self.repo / ".claude" / "patterns"

    @property
    def personal_patterns(self):
        return self.lintel_home / "patterns"

    def envelope(self):
        if self.launched_envelope is not None:
            return self.launched_envelope
        return p.build_envelope(self.repo, self.lintel_home, self.pack_context)

    def use_launcher_roots(self):
        """Adopt the launcher's own envelope (the real ADR-0029 profile) for every later call.

        Direct-CLI and API comparisons then use exactly the roots the launcher sends, so no
        synthetic neutral record or digest is compared against the real one.
        """
        code, envelope, stderr = self.launcher("roots")
        if code != 0:
            raise AssertionError(f"launcher roots failed ({code}): {stderr}")
        p.parse_roots(envelope)
        self.launched_envelope = envelope
        return envelope

    def roots(self):
        return p.parse_roots(self.envelope())

    def envelope_file(self):
        return self.write_json("roots.json", self.envelope())

    # ---- sources
    def publish(self, directory, source_id, patterns, *, bindings=(), assets=None, lifecycle=(), revocations=None):
        """Write a catalog as a reviewed source would contain it; `assets` maps path -> bytes per pattern id."""
        directory = Path(directory)
        entries = []
        for pattern in patterns:
            relative = f"{pattern['id']}/{pattern['version']}/pattern.json"
            path = directory / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(pattern), encoding="utf-8")
            for asset_path, data in (assets or {}).get(pattern["id"], {}).items():
                target = path.parent / asset_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            entries.append({"id": pattern["id"], "version": pattern["version"], "path": relative,
                            "sha256": p.content_digest(pattern), "summary": pattern["summary"],
                            "status": pattern["status"], "applies_to": pattern["applies_to"]})
        catalog = {"schema_version": 1, "source_id": source_id, "entries": entries, "includes": [],
                   "bindings": list(bindings), "lifecycle": list(lifecycle)}
        if revocations is not None:
            catalog["revocations"] = list(revocations)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
        return catalog

    def repo_bindings(self, bindings):
        (self.repo_patterns / "bindings.json").write_text(
            json.dumps({"schema_version": 1, "bindings": bindings}), encoding="utf-8")

    def resolve(self, context, **kwargs):
        kwargs.setdefault("today", TODAY)
        reader = kwargs.pop("reader", None) or p.Reader()
        report = p.resolve(self.roots(), p.parse_context(context), reader=reader, **kwargs)
        return report, reader

    def write_json(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    # ---- processes
    def env(self):
        keep = ("SYSTEMROOT", "SystemRoot", "WINDIR", "PATH", "PATHEXT", "COMSPEC", "OS")
        env = {key: value for key, value in os.environ.items() if key in keep}
        env.update(HOME=str(self.home), USERPROFILE=str(self.home), LINTEL_HOME=str(self.lintel_home),
                   APPDATA=str(self.home / "app"), LOCALAPPDATA=str(self.home / "local"),
                   TEMP=str(self.root / "tmp"), TMP=str(self.root / "tmp"), TMPDIR=str(self.root / "tmp"),
                   XDG_CONFIG_HOME=str(self.home / "config"), XDG_DATA_HOME=str(self.home / "data"),
                   XDG_CACHE_HOME=str(self.home / "cache"), XDG_STATE_HOME=str(self.home / "state"),
                   LINTEL_SOURCE_ROOT=str(ROOT), LINTEL_REPO_ROOT=str(self.repo),
                   LINTEL_PACKS_DIR=str(self.lintel_home / "packs"),
                   LINTEL_ACTIVE_PACK_FILE=str(self.lintel_home / "packs" / "active-pack"),
                   GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0",
                   PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        return env

    def cli(self, *args, roots=True):
        """Run the real CLI with the roots envelope the launcher would supply."""
        command = [sys.executable, "-I", "-B", str(CLI), *map(str, args)]
        if roots:
            command[4:5] = [command[4], "--roots-file", str(self.envelope_file())]
        result = subprocess.run(command, capture_output=True, env=self.env(), cwd=self.repo, timeout=120)
        return result.returncode, json.loads(result.stdout.decode("utf-8")), result.stderr.decode("utf-8")

    def launcher(self, *args):
        """Run the real `bin/li-pattern` launcher (bash) with this fixture's synthetic environment."""
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        if bash is None:
            raise AssertionError("bash is required for launcher cases; it is a declared test prerequisite")
        if not LAUNCHER.is_file():
            raise AssertionError(f"{LAUNCHER} is missing; the launcher is part of the joined tree")
        result = subprocess.run([bash, LAUNCHER.as_posix(), *map(str, args)], capture_output=True, env=self.env(),
                                cwd=self.repo, timeout=180, stdin=subprocess.DEVNULL)
        return result.returncode, json.loads(result.stdout.decode("utf-8") or "{}"), result.stderr.decode("utf-8")


def visual_base_spec():
    """A minimal frontend-design-spec.json the shared design_contract validator accepts."""
    return {
        "schema_version": 1, "source": "frontend-design", "target_format": "single-file",
        "typography": {"schema_version": 1, "font_stacks": [
            {"role": "heading", "family": "Synthetic Serif", "fallback_stack": ["serif"]},
            {"role": "body", "family": "Synthetic Sans", "fallback_stack": ["sans-serif"]}],
            "size_scale": {"base_px": 16, "ratio": 1.25}},
        "motion": {"schema_version": 1, "mode": "library", "libraries": [{"name": "synthetic-scroll"}],
                   "key_animations": [], "perf_budget": {"fallback_for_prefers_reduced_motion": "no-animation"}},
        "shader": None, "component_libraries": [],
        "layout_grammar": {"max_width": "1152px"},
        "interaction_signature": {"scroll_smoothing": False, "page_transitions": "none"},
        "visual_thesis": "Synthetic profile-derived page", "voice_tier": "internal",
        "palette": {"tokens": {"ink": "#141413", "paper": "#faf9f5"}},
    }


def load_design_contract():
    sys.path.insert(0, str(ROOT / "skills" / "design-dna" / "scripts"))
    import design_contract
    return design_contract
