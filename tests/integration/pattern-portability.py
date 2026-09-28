#!/usr/bin/env python3
# component: reusable-patterns-portability-test
# implements: ADR-0038, ADR-0024, ADR-0030
# intent: .claude/plans/reusable-patterns/plan.md
# constraints: synthetic temporary roots only; builds its environment from scratch; per-command Git config only
# last_intent_review: 2026-09-28
"""V12/RN-13: the installed kit runs the pattern workflow from a separate source bundle.

A fresh target (path with spaces and shell metacharacters) receives the Copilot kit from
`bin/li-copilot.py init`. Every check then runs the kit's own launcher and modules, never this
checkout's, with synthetic HOME/USERPROFILE/LINTEL_HOME/TEMP/APPDATA/XDG roots. The Git cases
commit real CRLF asset bytes and read them back from a fresh clone.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "unit"))
import pattern_pack_harness as harness  # noqa: E402

sys.path.insert(0, str(ROOT / "bin"))
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("li_copilot_for_patterns", ROOT / "bin" / "li-copilot.py")
generator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(generator)

sys.path.insert(0, str(ROOT / "lib"))
from native_paths import native_io_path  # noqa: E402


def native(path: Path) -> Path:
    """Deep kit paths can exceed Windows MAX_PATH; read and copy through the long-path spelling."""
    return native_io_path(Path(path).resolve())


GIT_IDENTITY = ("-c", "user.name=Pattern Test", "-c", "user.email=pattern-test@example.invalid",
                "-c", "core.autocrlf=false", "-c", "commit.gpgsign=false")
CRLF_GUIDE = b"# Guide\r\n\r\nFilters stay visible.\r\nExports match the visible rows.\r\n"


class KitFixture:
    """One generated kit per test class; each test gets its own working repository."""

    def __init__(self, testcase):
        self.h = harness.Harness(testcase, git=False)
        self.kit_repo = self.h.root / "kit target"
        self.kit_repo.mkdir()
        self.git("init", "-q", cwd=self.kit_repo)
        env = self.h.env()
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(ROOT / "bin" / "li-copilot.py"), "init", "--source", str(ROOT),
             "--target", str(self.kit_repo), "--client", "copilot-cli", "--store", str(self.h.root / "kit store")],
            env=env, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            raise AssertionError(f"kit init failed: {result.stdout}\n{result.stderr}")
        self.bundle = self.kit_repo / ".github" / "lintel"
        self.launcher = self.bundle / "bin" / "li-pattern"

    def git(self, *args, cwd):
        return subprocess.run(["git", *GIT_IDENTITY, *args], cwd=cwd, env=self.h.env(), check=True,
                              capture_output=True, text=True, timeout=120)

    def launch(self, *args, repo=None, cwd=None, **env):
        command = [harness.bash_executable(), str(self.launcher)]
        if repo is not None:
            command += ["--repo", str(repo)]
        result = subprocess.run([*command, *map(str, args)], cwd=cwd or self.h.root,
                                env=self.h.env(LINTEL_SOURCE_ROOT=str(self.bundle), **env),
                                capture_output=True, timeout=300)
        stdout, stderr = result.stdout.decode("utf-8"), result.stderr.decode("utf-8")
        report = json.loads(stdout) if stdout.strip().startswith("{") else None
        return result.returncode, report, stderr

    def kit_python(self, script, *args, **env):
        """Run code against the kit's own lib/patterns.py (the installed module, not this checkout)."""
        result = subprocess.run([sys.executable, "-I", "-B", "-c", script, str(self.bundle / "lib"), *map(str, args)],
                                env=self.h.env(**env), capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise AssertionError(result.stderr)
        return json.loads(result.stdout)


PRELUDE = "import json, sys; sys.path.insert(0, sys.argv[1]); import patterns as p\n"


class PatternPortabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._holder = unittest.TestCase()
        cls.kit = KitFixture(cls._holder)

    @classmethod
    def tearDownClass(cls):
        cls._holder.doCleanups()

    def work_repo(self, name, *, git=True):
        repo = self.kit.h.root / name
        repo.mkdir()
        if git:
            self.kit.git("init", "-q", cwd=repo)
        return repo

    def test_kit_ships_the_complete_pattern_closure(self):
        for relative in generator.PATTERN_RESOURCES:
            with self.subTest(relative=relative):
                self.assertEqual(native(self.kit.bundle / relative).read_bytes(),
                                 generator.source_bytes(ROOT / relative), relative)
                if "/templates/pattern/example/" in relative:
                    self.assertEqual(native(self.kit.bundle / relative).read_bytes(), (ROOT / relative).read_bytes(),
                                     "byte-bound example files ship raw, unchanged by kit normalization")
        wrapper = (self.kit.kit_repo / ".github" / "skills" / "li-pattern" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("../../lintel/skills/pattern/SKILL.md", wrapper)
        skill = (self.kit.bundle / "skills" / "pattern" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/consumer-contract.md", skill)
        self.assertTrue((self.kit.bundle / "skills" / "pattern" / "references" / "consumer-contract.md").is_file())
        result = subprocess.run([sys.executable, "-I", "-B", str(self.kit.bundle / "bin" / "li-copilot.py"), "check",
                                 "--target", str(self.kit.kit_repo)], env=self.kit.h.env(), capture_output=True,
                                text=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_no_sources_explicit_non_git_root_and_personal_only(self):
        plain = self.work_repo("plain dir (no git)", git=False)
        code, report, stderr = self.kit.launch("list", repo=plain)
        self.assertEqual((code, report["status"], report["entries"]), (0, "ok", []), stderr)
        code, report, stderr = self.kit.launch("list", cwd=plain)
        self.assertEqual((code, report["status"]), (0, "ok"), stderr)
        code, envelope, _ = self.kit.launch("roots", cwd=plain)
        self.assertEqual((code, envelope["repository"]), (0, None), "outside Git there is no repository root")

    def test_missing_runtime_is_pattern_check_unavailable(self):
        empty = self.kit.h.root / "no python here"
        empty.mkdir()
        script = ('dirname() { case "$1" in */*) printf "%s\\n" "${1%/*}";; *) printf ".\\n";; esac; }; '
                  'export -f dirname; exec "$BASH" "$0" list')
        env = {"PATH": str(empty), "HOME": str(self.kit.h.user), "LINTEL_HOME": str(self.kit.h.home)}
        result = subprocess.run([harness.bash_executable(), "-c", script, str(self.kit.launcher)], env=env,
                                capture_output=True, timeout=120)
        stderr = result.stderr.decode("utf-8")
        self.assertEqual(result.returncode, 5, stderr)
        self.assertIn("pattern check unavailable", stderr)
        self.assertIn('not a "no patterns" result', stderr)
        self.assertEqual(result.stdout, b"", "no report is synthesized without the runtime")

    def test_canonical_example_resolves_locks_and_reads_its_asset(self):
        repo = self.work_repo("example repo")
        shutil.copytree(native(self.kit.bundle / "scaffolding/01-foundation/templates/pattern/example"),
                        native(repo / ".claude" / "patterns"))
        code, report, stderr = self.kit.launch("check", repo=repo)
        self.assertEqual((code, report["status"]), (0, "ok"), stderr)
        context = self.kit.h.inputs / "dashboard.json"
        context.write_text(json.dumps({"schema_version": 1, "facts": {"artifact": "dashboard", "audience": "internal"},
                                       "evidence": {"artifact": "brief.md", "audience": "brief.md"}}), encoding="utf-8")
        lock = repo / ".claude" / "plans" / "dash" / "patterns.lock.json"
        lock.parent.mkdir(parents=True)
        code, report, stderr = self.kit.launch("resolve", "--context", context, "--lock", lock, repo=repo)
        self.assertEqual((code, report["status"]), (0, "ready"), stderr)
        self.assertEqual([item["ref"]["id"] for item in report["selected"]], ["example.internal-dashboard"])
        self.assertEqual(sorted(item["clause"].split("#")[1] for item in report["requirements"]
                                if item["state"] == "mandatory"), ["DASH-01", "DASH-02"])
        code, verified, stderr = self.kit.launch("verify-lock", "--lock", lock, "--context", context, repo=repo)
        self.assertEqual((code, verified["status"]), (0, "ok"), stderr)
        code, envelope, _ = self.kit.launch("roots", repo=repo)
        result = self.kit.kit_python(PRELUDE + (
            "roots = p.parse_roots(json.loads(sys.argv[2]))\n"
            "lock = json.loads(open(sys.argv[3], encoding='utf-8').read())\n"
            "context = p.parse_context(json.loads(open(sys.argv[4], encoding='utf-8').read()))\n"
            "verified = p.verify_lock(roots, lock, context)\n"
            "data = p.read_asset(roots, p.asset_refs(lock)[0], selection=lock)\n"
            "print(json.dumps({'verified': verified['status'], 'bytes': len(data), 'head': data[:26].decode()}))\n"),
            json.dumps(envelope), lock, context)
        self.assertEqual((result["verified"], result["head"]), ("ok", "# Internal dashboard guide"))
        backend = self.kit.h.inputs / "backend.json"
        backend.write_text(json.dumps({"schema_version": 1, "facts": {"artifact": "api-change"},
                                       "evidence": {"artifact": "brief.md"}}), encoding="utf-8")
        code, report, stderr = self.kit.launch("resolve", "--context", backend, repo=repo)
        self.assertEqual((code, report["status"], report["metrics"]["asset_reads"], report["metrics"]["pattern_reads"]),
                         (0, "empty", 0, 0), "an unrelated backend change reads no pattern body or asset")

    def _commit_and_clone(self, repo, name):
        self.kit.git("add", "-A", cwd=repo)
        self.kit.git("commit", "-q", "-m", "patterns", cwd=repo)
        clone = self.kit.h.root / name
        self.kit.git("clone", "-q", str(repo), str(clone), cwd=self.kit.h.root)
        return clone

    def _capture_crlf_pattern(self, repo):
        inputs = self.kit.h.root / f"{repo.name} inputs"
        inputs.mkdir()
        (inputs / "guide.md").write_bytes(CRLF_GUIDE)
        draft = harness.make_pattern("team.crlf", version="0.1.0", status="draft")
        draft["assets"] = [{"path": "guide.md", "kind": "guide", "sha256": __import__("hashlib").sha256(CRLF_GUIDE).hexdigest()}]
        (inputs / "draft.json").write_text(json.dumps(draft), encoding="utf-8", newline="\n")
        code, report, stderr = self.kit.launch("capture", "--input", inputs / "draft.json", "--scope", "repo",
                                               "--name", "team.crlf", "--source-id", "team.repo", repo=repo)
        self.assertEqual(code, 0, stderr)
        approval = inputs / "approval.json"
        approval.write_text(json.dumps({"by": "reviewer", "reference": "REV-1", "at": "2026-09-28T00:00:00Z"}),
                            encoding="utf-8")
        digest = self.kit.kit_python(PRELUDE + "print(json.dumps(p.content_digest(json.load(open(sys.argv[2])))))",
                                     inputs / "draft.json")
        code, report, stderr = self.kit.launch(
            "approve", "--path", repo / ".claude/patterns/team.crlf/0.1.0/pattern.json", "--version", "1.0.0",
            "--approval", approval, "--expected-digest", digest, repo=repo)
        self.assertEqual(code, 0, stderr)
        return report["ref"]

    def test_repository_source_keeps_crlf_asset_bytes_through_git_only_with_source_attributes(self):
        for protected in (False, True):
            with self.subTest(source_local_gitattributes=protected):
                repo = self.work_repo(f"crlf repo {'protected' if protected else 'plain'}")
                (repo / ".gitattributes").write_bytes(b"*.md text eol=lf\n*.json text eol=lf\n")
                ref = self._capture_crlf_pattern(repo)
                if protected:
                    shutil.copyfile(native(self.kit.bundle / "scaffolding/01-foundation/templates/pattern/example/.gitattributes"),
                                    native(repo / ".claude" / "patterns" / ".gitattributes"))
                clone = self._commit_and_clone(repo, f"crlf clone {'protected' if protected else 'plain'}")
                stored = native(clone / ".claude/patterns/team.crlf/1.0.0/guide.md").read_bytes()
                code, report, stderr = self.kit.launch("check", repo=clone)
                if not protected:
                    self.assertNotEqual(stored, CRLF_GUIDE, "the repository policy rewrote the asset (the hazard)")
                    self.assertEqual((code, report["status"]), (5, "unavailable"), stderr)
                    self.assertIn("declared_file_changed", harness.codes(report, "error"))
                    continue
                self.assertEqual(stored, CRLF_GUIDE, "source-local `* -text` keeps the raw bytes")
                self.assertEqual((code, report["status"]), (0, "ok"), stderr)
                code, envelope, _ = self.kit.launch("roots", repo=clone)
                result = self.kit.kit_python(PRELUDE + (
                    "roots = p.parse_roots(json.loads(sys.argv[2]))\n"
                    "ref = json.loads(sys.argv[3])\n"
                    "shown = p.show_pattern(roots, f\"{ref['source']}:{ref['id']}@{ref['version']}\")\n"
                    "asset = dict(shown['pattern']['assets'][0], pattern=ref)\n"
                    "print(json.dumps(p.read_asset(roots, asset).hex()))\n"), json.dumps(envelope), json.dumps(ref))
                self.assertEqual(bytes.fromhex(result), CRLF_GUIDE)

    def test_pack_source_keeps_crlf_asset_bytes_through_git(self):
        repo = self.work_repo("crlf pack repo")
        (repo / ".gitattributes").write_bytes(b"*.md text eol=lf\n*.json text eol=lf\n")
        pack = repo / "packs" / "team"
        (pack / "patterns").mkdir(parents=True)
        (pack / "pack.yaml").write_text("name: team\nversion: 1.0.0\nextends: _default\npatterns:\n"
                                        "  source: patterns/catalog.json\n", encoding="utf-8", newline="\n")
        shutil.copyfile(native(self.kit.bundle / "scaffolding/01-foundation/templates/pattern/example/.gitattributes"),
                        native(pack / "patterns" / ".gitattributes"))
        built = self.kit.kit_python(PRELUDE + (
            "import hashlib, pathlib\n"
            "root = pathlib.Path(sys.argv[2])\n"
            "guide = bytes.fromhex(sys.argv[3])\n"
            "value = {'schema_version': 1, 'id': 'team.pack-crlf', 'version': '1.0.0', 'status': 'approved',\n"
            "  'summary': 'Pack CRLF asset', 'owner': 'team', 'applies_to': {}, 'includes': [],\n"
            "  'sources': [{'kind': 'operator-statement', 'ref': 'stated', 'root': 'statement', 'section': '',\n"
            "    'observed_at': '2026-09-01T00:00:00Z', 'confidence': 'confirmed', 'reuse': 'internal'}],\n"
            "  'requirements': [{'id': 'R-1', 'level': 'default', 'text': 'Use the guide.', 'verify': 'Read it.'}],\n"
            "  'guidance': '', 'assets': [{'path': 'guide.md', 'kind': 'guide', 'sha256': hashlib.sha256(guide).hexdigest()}],\n"
            "  'approval': {'by': 'reviewer', 'reference': 'REV', 'at': '2026-09-01T00:00:00Z'}}\n"
            "pattern = p.parse_pattern(value)\n"
            "folder = root / 'team.pack-crlf' / '1.0.0'\n"
            "folder.mkdir(parents=True)\n"
            "(folder / 'pattern.json').write_bytes(p.emit_json(value).encode())\n"
            "(folder / 'guide.md').write_bytes(guide)\n"
            "ref = {'source': 'team.patterns', 'id': value['id'], 'version': '1.0.0', 'sha256': pattern.digest}\n"
            "catalog = {'schema_version': 1, 'source_id': 'team.patterns', 'lifecycle': [], 'includes': [],\n"
            "  'entries': [{'id': value['id'], 'version': '1.0.0', 'path': 'team.pack-crlf/1.0.0/pattern.json',\n"
            "    'sha256': pattern.digest, 'summary': value['summary'], 'status': 'approved', 'applies_to': {}}],\n"
            "  'bindings': [{'id': 'b', 'when': {}, 'use': [ref], 'role': 'default', 'approved_by': 'lead',\n"
            "    'approval_ref': 'D-1'}]}\n"
            "p.parse_catalog(catalog)\n"
            "(root / 'catalog.json').write_bytes(p.emit_json(catalog).encode())\n"
            "print(json.dumps(ref))\n"), pack / "patterns", CRLF_GUIDE.hex())
        clone = self._commit_and_clone(repo, "crlf pack clone")
        self.assertEqual(native(clone / "packs/team/patterns/team.pack-crlf/1.0.0/guide.md").read_bytes(), CRLF_GUIDE)
        code, report, stderr = self.kit.launch("check", repo=clone, LINTEL_PROFILE_PACK="team")
        self.assertEqual((code, report["status"]), (0, "ok"), stderr)
        self.assertEqual([(item["source_id"], item["scope"]) for item in report["sources"]], [("team.patterns", "pack")])
        code, envelope, _ = self.kit.launch("roots", repo=clone, LINTEL_PROFILE_PACK="team")
        result = self.kit.kit_python(PRELUDE + (
            "roots = p.parse_roots(json.loads(sys.argv[2]))\n"
            "context = p.parse_context({'schema_version': 1, 'facts': {}, 'evidence': {}})\n"
            "report = p.resolve(roots, context)\n"
            "data = p.read_asset(roots, p.asset_refs(report)[0], selection=report, context=context)\n"
            "print(json.dumps({'status': report['status'], 'scope': report['selected'][0]['scope'], 'hex': data.hex()}))\n"),
            json.dumps(envelope))
        self.assertEqual((result["status"], result["scope"], bytes.fromhex(result["hex"])),
                         ("ready", "pack", CRLF_GUIDE))
        self.assertEqual(built["source"], "team.patterns")


if __name__ == "__main__":
    unittest.main(verbosity=2)
