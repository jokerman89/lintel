#!/usr/bin/env python3
# component: catalog-metadata-tests
# implements: ADR-0028
# intent: skills/catalog/references/metadata.md
# constraints: synthetic sources and homes; metadata evidence, not live client acceptance
# last_intent_review: 2026-09-22
"""Exercise the catalog's read-only discovery contract and retained Markdown output."""
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "bin" / "li-catalog.py"
sys.dont_write_bytecode = True


@contextlib.contextmanager
def isolated_environment():
    original = dict(os.environ)
    with tempfile.TemporaryDirectory(prefix="catalog-metadata-") as temporary:
        base = Path(temporary).resolve()
        for key in tuple(os.environ):
            if key.startswith(("LINTEL_", "GIT_", "GH_", "GITHUB_", "CLAUDE_", "COPILOT_", "XDG_", "PYTHON")):
                del os.environ[key]
        for key in ("BASH_ENV", "ENV", "CDPATH", "NODE_OPTIONS"):
            os.environ.pop(key, None)
        for key, suffix in {
            "HOME": "home", "USERPROFILE": "home", "APPDATA": "app",
            "LOCALAPPDATA": "local", "TEMP": "tmp", "TMP": "tmp", "TMPDIR": "tmp",
            "XDG_CONFIG_HOME": "xdg-config", "XDG_CACHE_HOME": "xdg-cache",
            "XDG_DATA_HOME": "xdg-data", "CLAUDE_CONFIG_DIR": "claude",
            "COPILOT_HOME": "copilot", "LINTEL_HOME": "lintel",
            "LINTEL_PACKS_DIR": "lintel/packs", "LINTEL_AUDIT_DIR": "lintel/audit",
            "LINTEL_REPO_ROOT": "target",
        }.items():
            path = base / suffix
            path.mkdir(parents=True, exist_ok=True)
            assert path.resolve().is_relative_to(base) and not path.is_symlink()
            os.environ[key] = str(path)
        os.environ.update(
            LINTEL_SOURCE_ROOT=str(ROOT), LINTEL_PROFILE_FILE=str(base / "lintel" / "profile.yaml"),
            LINTEL_JOBS_REGISTRY=str(base / "lintel" / "jobs.json"),
            GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(base / "home" / ".gitconfig"),
            GIT_CEILING_DIRECTORIES=str(base), GIT_TERMINAL_PROMPT="0",
            PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
        )
        if os.name == "nt":
            os.environ["HOMEDRIVE"] = base.drive
            os.environ["HOMEPATH"] = str(base / "home")[len(base.drive):]
        try:
            yield base
        finally:
            os.environ.clear()
            os.environ.update(original)


def load_catalog():
    spec = importlib.util.spec_from_file_location("catalog_under_test", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def files_snapshot(root):
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


class CatalogMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=os.environ["TEMP"], prefix="case-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.source = self.base / "source"
        self.target = self.base / "target"
        self.target.mkdir()
        (self.source / "lib").mkdir(parents=True)
        shutil.copyfile(ROOT / "lib" / "cli-tiers.yaml", self.source / "lib" / "cli-tiers.yaml")
        self.write("config/aliases.yaml", "version: 1\nskill_aliases: []\n")
        self.skill("alpha", description="Alpha literal [$.*] and --check; not yet implemented.")
        self.skill("alpha-tools", description="Alpha tools", voice="customer")
        self.skill("plan-check", description="Plan a check", cli_support="[copilot-app]")
        self.write("agents/engineering/Analyst.md", (
            "---\nname: Analyst\ncategory: engineering\ndescription: Analyze bounded decisions\n"
            "voice: internal\ncli_support: [codex]\n---\nAGENT BODY MUST NOT ESCAPE\n"
        ))
        (self.source / "skills" / "CATALOG.md").write_text("KEEP GOOD CATALOG\n", encoding="utf-8")
        (self.target / "sentinel").write_text("KEEP TARGET\n", encoding="utf-8")

    def write(self, relative, text):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def skill(self, name, *, description="Example", voice="internal",
              cli_support="[claude-code, codex, copilot]", extra="", body="BODY MUST NOT ESCAPE"):
        return self.write("skills/" + name + "/SKILL.md", (
            f"---\nname: {name}\nlayer: foundation\ndescription: {description}\n"
            f"voice: {voice}\ncli_support: {cli_support}\n{extra}---\n{body}\n"
        ))

    def run_cli(self, *args, tool=TOOL, no_site=False, source=True):
        command = [sys.executable, "-X", "utf8"]
        if no_site:
            command += ["-I", "-S"]
        command += [str(tool), *args]
        if source:
            command += ["--source-root", str(self.source)]
        result = subprocess.run(command, cwd=self.target, capture_output=True, check=False)
        return result

    def assert_failed_without_writes(self, *args, **kwargs):
        before = files_snapshot(self.base)
        result = self.run_cli(*args, **kwargs)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertTrue(result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(files_snapshot(self.base), before)
        return result

    def test_default_markdown_fixture_is_byte_exact(self):
        root = self.base / "legacy"
        path = root / "skills" / "example" / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            "---\nname: example\nlayer: foundation\ndescription: Use Unicode \u2192 and a pipe | safely\n---\nBody\n",
            encoding="utf-8",
        )
        expected = (
            "# Lintel Skill Catalog\n\n"
            "Generated from skill frontmatter. Run `python3 bin/li-catalog.py` after changing a skill.\n"
            "CI checks this file for drift; edit the source SKILL.md to change a description.\n\n"
            "Use `/li:<name>` in a Lintel plugin, or ask Copilot to run the named Lintel skill.\n\n"
            "Total skills: 1\n\n## foundation layer (1 skills)\n\n"
            "| Skill | Description |\n|---|---|\n"
            "| [`/li:example`](example/SKILL.md) | Use Unicode \u2192 and a pipe \\| safely |\n"
        )
        self.assertEqual(self.catalog.generate(root).encode(), expected.encode())

    def test_canonical_default_matches_committed_catalog(self):
        expected = (ROOT / "skills" / "CATALOG.md").read_text(encoding="utf-8")
        self.assertEqual(self.catalog.generate(ROOT), expected)
        result = self.run_cli("--check", source=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, ("Catalog matches skill frontmatter." + os.linesep).encode())

    def test_canonical_identities_aliases_and_descriptions(self):
        result = self.catalog.metadata(ROOT, kind="all")
        skills = {item["name"]: item for item in result["entries"] if item["kind"] == "skill"}
        agents = {item["name"]: item for item in result["entries"] if item["kind"] == "agent"}
        self.assertEqual(len(skills), len(list((ROOT / "skills").glob("*/SKILL.md"))))
        self.assertEqual(len(agents), len(list((ROOT / "agents").glob("*/*.md"))))
        aliases = self.catalog.load_text((ROOT / "config" / "aliases.yaml").read_text(encoding="utf-8"))["skill_aliases"]
        for alias in aliases:
            entries = skills[alias["new"]]["aliases"]
            self.assertIn({"name": alias["old"], "source": "config/aliases.yaml", "note": alias["reason"]}, entries)
        for record in result["entries"]:
            path = ROOT / record["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(record["id"], record["kind"] + ":" + record["name"])
            with path.open(encoding="utf-8-sig") as handle:
                self.assertEqual(handle.readline().strip(), "---")
                lines = []
                for line in handle:
                    if line.strip() == "---":
                        break
                    lines.append(line)
            original = self.catalog.load_text("".join(lines))
            self.assertEqual(record["description"], original["description"])
            self.assertEqual(record["maturity"], "unknown")
        self.assertEqual(result["evidence_level"], "source-metadata")
        self.assertFalse(result["executed"])

    def test_template_and_full_hints_are_not_maturity_or_execution(self):
        result = self.catalog.metadata(ROOT, name="generate-pdf")
        self.assertEqual(result["matched"], 1)
        record = result["entries"][0]
        self.assertIn("TEMPLATE ONLY", record["description"])
        self.assertTrue(any(hint["level"] == "full" for hint in record["cli_support"]))
        self.assertEqual(record["maturity"], "unknown")
        self.assertFalse(result["executed"])
        self.assertNotIn("capabilities", record)

    def test_metadata_is_deterministic_compact_and_read_only(self):
        before = files_snapshot(self.base)
        first = self.run_cli("--json", "--kind=all")
        second = self.run_cli("--json", "--kind=all")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stdout.count(b"\n"), 1)
        self.assertNotIn(b"BODY MUST NOT ESCAPE", first.stdout)
        decoded = json.loads(first.stdout)
        self.assertEqual(decoded["source_root"], str(self.source))
        self.assertEqual((decoded["total"], decoded["matched"]), (4, 4))
        self.assertEqual(files_snapshot(self.base), before)

    def test_literal_queries_never_run_or_expand(self):
        for query, count in (("[$.*]", 1), ("ALPHA", 2), ("--check", 1), ("alpha*", 0),
                             ("$(touch p13-marker)", 0), ("'; exit 0; #", 0), ("../", 0)):
            with self.subTest(query=query):
                result = self.run_cli("--json", "--query=" + query)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["matched"], count)
        self.assertFalse((self.target / "p13-marker").exists())
        search = self.run_cli("--json", "--search=[$.*]")
        self.assertEqual(search.returncode, 0, search.stderr)
        self.assertEqual(json.loads(search.stdout)["matched"], 1)

    def test_family_is_literal_and_filters_compose(self):
        result = self.catalog.metadata(self.source, family="alpha", voice="customer", cli="copilot")
        self.assertEqual([entry["name"] for entry in result["entries"]], ["alpha-tools"])
        self.assertEqual(self.catalog.metadata(self.source, family="alpha*")["matched"], 0)
        self.assertEqual(self.catalog.metadata(self.source, family=".*")["matched"], 0)
        agents = self.catalog.metadata(self.source, kind="agent", family="engineer", category="engineering")
        self.assertEqual([entry["name"] for entry in agents["entries"]], ["Analyst"])
        self.assertEqual(self.catalog.metadata(self.source, category="plan")["matched"], 1)

    def test_registry_alias_does_not_collapse_neighboring_surfaces(self):
        cli = self.catalog.metadata(self.source, cli="copilot")["entries"]
        app = self.catalog.metadata(self.source, cli="copilot-app")["entries"]
        self.assertEqual([item["name"] for item in cli], ["alpha", "alpha-tools"])
        self.assertEqual([item["name"] for item in app], ["plan-check"])
        hint = next(h for h in cli[0]["cli_support"] if h["cli"] == "copilot")
        self.assertEqual(hint, {"cli": "copilot", "surface": "copilot-cli", "level": None})
        self.assert_failed_without_writes("--json", "--cli=made-up-client")

    def test_aliases_keep_identity_and_guidance_without_expiring(self):
        self.skill("alpha", extra="deprecated_aliases: [old-alpha]\n")
        self.write("config/aliases.yaml", (
            "version: 1\nskill_aliases:\n  - old: old-alpha\n    new: alpha\n"
            "    removal_at: 2000-01-01\n    reason: Use alpha with the original arguments\n"
        ))
        result = self.catalog.metadata(self.source, name="old-alpha")
        self.assertEqual(result["matched"], 1)
        record = result["entries"][0]
        self.assertEqual(record["id"], "skill:alpha")
        self.assertEqual(record["path"], "skills/alpha/SKILL.md")
        self.assertEqual(record["aliases"], [{
            "name": "old-alpha", "source": "config/aliases.yaml",
            "note": "Use alpha with the original arguments",
        }])
        self.assertEqual(self.catalog.metadata(self.source, family="old-")["matched"], 1)

    def test_frontmatter_only_alias_and_source_relative_folder(self):
        path = self.skill("alpha", extra="deprecated_aliases: [old-alpha]\n")
        new = path.parent.with_name("different-folder")
        path.parent.rename(new)
        result = self.catalog.metadata(self.source, name="old-alpha")["entries"][0]
        self.assertEqual(result["path"], "skills/different-folder/SKILL.md")
        self.assertEqual(result["aliases"][0]["source"], "skills/different-folder/SKILL.md")

    def test_metadata_stops_at_frontmatter_even_with_invalid_body_bytes(self):
        path = self.source / "skills" / "alpha" / "SKILL.md"
        frontmatter = path.read_bytes().split(b"\n---\n", 1)[0] + b"\n---\n"
        path.write_bytes(b"\xef\xbb\xbf" + frontmatter.replace(b"\n", b"\r\n") + b"\xff" * 100000)
        original = Path.read_text
        def guarded(selected, *args, **kwargs):
            if selected.name == "SKILL.md" or "agents" in selected.parts:
                raise AssertionError("whole prompt read")
            return original(selected, *args, **kwargs)
        with mock.patch.object(Path, "read_text", guarded):
            self.assertEqual(self.catalog.metadata(self.source, name="alpha")["matched"], 1)
        self.assertIn("alpha", self.catalog.generate(self.source))

    def test_missing_malformed_and_empty_sources_refuse_before_output(self):
        path = self.source / "skills" / "alpha" / "SKILL.md"
        original = path.read_bytes()
        for text in (
            "", "name: alpha\n", "---\nname: alpha\n",
            "---\nname: alpha\n---\nlayer: foundation\ndescription: Body decoy\n",
            "---\nname: alpha\nname: duplicate\nlayer: foundation\ndescription: X\nvoice: internal\ncli_support: []\n---\n",
            "---\nname: alpha\nlayer: foundation\ndescription: ''\nvoice: internal\ncli_support: []\n---\n",
            "---\nname: alpha\nlayer: foundation\ndescription: [wrong]\nvoice: internal\ncli_support: []\n---\n",
            "---\nname: alpha\nlayer: foundation\ndescription: 'unterminated\n---\n",
            "---\nname: alpha\nlayer: foundation\ndescription: !!python/object:bad {}\n---\n",
        ):
            with self.subTest(text=text):
                path.write_text(text, encoding="utf-8")
                self.assert_failed_without_writes("--json", "--query=unmatched")
        path.write_bytes(original)
        for prompt in self.source.glob("skills/*/SKILL.md"):
            prompt.unlink()
        self.assert_failed_without_writes("--json")

    def test_empty_arguments_and_write_mode_combinations_refuse(self):
        for args in (
            ("--json", "--query="), ("--json", "--family= "),
            ("--json", "--name="), ("--json", "--category="), ("--json", "--voice="),
            ("--json", "--cli="), ("--json", "--check"), ("--family=alpha",),
            ("--source-root", "."), ("--json", "--source-root", "."), ("--kind=all",),
        ):
            with self.subTest(args=args):
                self.assert_failed_without_writes(*args, source=False)

    def test_duplicate_identity_alias_conflicts_and_missing_targets_refuse(self):
        original = (self.source / "config" / "aliases.yaml").read_text()
        for aliases in (
            "  - old: alpha\n    new: alpha-tools\n",
            "  - old: ALPHA\n    new: alpha-tools\n",
            "  - old: old\n    new: missing\n",
            "  - old: old\n    new: alpha\n  - old: old\n    new: alpha-tools\n",
            "  - old: old\n    new: alpha\n  - old: old\n    new: alpha\n",
            "  - old: '../escape'\n    new: alpha\n",
        ):
            self.write("config/aliases.yaml", "version: 1\nskill_aliases:\n" + aliases)
            self.assert_failed_without_writes("--json")
        self.write("config/aliases.yaml", original)
        self.write("skills/duplicate/SKILL.md", (self.source / "skills" / "alpha" / "SKILL.md").read_text())
        self.assert_failed_without_writes("--json")

    def test_malformed_registry_and_hint_fail_without_fallback(self):
        path = self.source / "lib" / "cli-tiers.yaml"
        original = path.read_bytes()
        for data in ("{}", '{"schema_version":2,"schema_version":2}', ""):
            path.write_text(data)
            self.assert_failed_without_writes("--json")
        path.write_bytes(original)
        for hints in ("false", "[made-up-host]", "[3]", "{copilot: full}"):
            self.skill("alpha", cli_support=hints)
            self.assert_failed_without_writes("--json")

    def test_alias_metadata_and_overlong_headers_fail_visibly(self):
        for aliases in ("null", "{}", "[3]", "[old, old]", "[old, OLD]"):
            self.skill("alpha", extra="deprecated_aliases: " + aliases + "\n")
            self.assert_failed_without_writes("--json")
        self.skill("alpha")
        self.write("config/aliases.yaml", "version: 1\nskill_aliases: null\n")
        self.assert_failed_without_writes("--json")
        self.write("config/aliases.yaml", "version: 1\nskill_aliases: []\n")
        self.write("skills/alpha/SKILL.md", "---\n" + "#" * (64 * 1024) + "\n---\n")
        self.assert_failed_without_writes("--json")

    def test_absent_helpers_and_sources_do_not_use_target_fallbacks(self):
        tool = self.source / "bin" / "li-catalog.py"
        tool.parent.mkdir()
        shutil.copyfile(TOOL, tool)
        self.assert_failed_without_writes("--json", tool=tool, source=False)
        for path in (self.source / "config" / "aliases.yaml", self.source / "lib" / "cli-tiers.yaml"):
            original = path.read_bytes()
            path.unlink()
            self.assert_failed_without_writes("--json")
            path.write_bytes(original)
        self.assert_failed_without_writes("--json", "--source-root", str(self.base / "absent"), source=False)

    def test_staged_descriptions_and_ungraded_hints_remain_declarations(self):
        self.skill("alpha", description="Staged method; no renderer is implemented",
                   cli_support="\n  - cli: copilot\n    level: full")
        item = self.catalog.metadata(self.source, name="alpha")["entries"][0]
        self.assertEqual(item["description"], "Staged method; no renderer is implemented")
        self.assertEqual(item["cli_support"], [{"cli": "copilot", "surface": "copilot-cli", "level": "full"}])
        self.assertEqual(item["maturity"], "unknown")
        self.skill("alpha", extra="maturity: mature\n")
        self.assertEqual(self.catalog.metadata(self.source, name="alpha")["entries"][0]["maturity"], "unknown")

    def test_source_provenance_records_keep_actual_notices_and_unknown_revisions(self):
        registry_path = ROOT / "install" / "upstream-sources.yaml"
        text = registry_path.read_text(encoding="utf-8")
        registry = self.catalog.load_text(text)
        self.assertEqual(len(registry["sources"]), 8)
        self.assertEqual(len(registry["bundled_materials"]), 2)
        for record in registry["bundled_materials"].values():
            self.assertIsNone(record["import_commit"])
            self.assertEqual(record["relationship"], "adapted")
            self.assertTrue(record["source"].startswith("https://github.com/"))
            self.assertTrue(record["modifications"])
            for relative in [*record["local_paths"], record["notice"], record["attribution"]]:
                path = (ROOT / relative).resolve()
                self.assertTrue(path.is_relative_to(ROOT) and path.exists(), relative)
            self.assertGreater((ROOT / record["notice"]).stat().st_size, 0)
        self.assertIn("not import provenance", registry["method_comparisons"]["scope"])
        guidance = (ROOT / "docs" / "provenance.md").read_text(encoding="utf-8")
        self.assertIn("explicitly unknown", guidance)
        self.assertIn("Do not use similarity thresholds", guidance)
        self.assertNotIn("`~` expanded by the installer", text)
        self.assertNotIn("command to run inside install_path after clone", text)

    def test_data_roots_cannot_supply_executable_helpers(self):
        trap = "from pathlib import Path\nPath('executed-decoy').write_text('BAD')\nraise RuntimeError('decoy')\n"
        for directory in (self.source / "lib", self.target):
            for name in ("client_capabilities.py", "envelope_contract.py", "li-catalog.py"):
                (directory / name).write_text(trap)
        before = files_snapshot(self.base)
        result = self.run_cli("--json", "--name=alpha")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["source_root"], str(self.source))
        self.assertEqual(files_snapshot(self.base), before)

    def test_linked_source_records_are_refused_before_opening(self):
        path = self.source / "skills" / "alpha" / "SKILL.md"
        original = Path.lstat
        def linked(selected):
            result = original(selected)
            if selected == path:
                return mock.Mock(st_file_attributes=0x400, st_mode=result.st_mode)
            return result
        with mock.patch.object(Path, "lstat", linked):
            with self.assertRaisesRegex(ValueError, "[Ll]ink|[Rr]eparse"):
                self.catalog.metadata(self.source)

    def test_normal_cli_stays_dependency_free_and_bad_input_keeps_good_catalog(self):
        tool = self.source / "bin" / "li-catalog.py"
        tool.parent.mkdir()
        shutil.copyfile(TOOL, tool)
        result = self.run_cli(tool=tool, no_site=True, source=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith(b"Generated "))
        result = self.run_cli("--check", tool=tool, no_site=True, source=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.write("skills/alpha/SKILL.md", "---\nname: alpha\n---\n")
        self.assert_failed_without_writes(tool=tool, no_site=True, source=False)
        self.assert_failed_without_writes("--check", tool=tool, no_site=True, source=False)

    def test_json_dependency_failure_is_visible_not_an_empty_success(self):
        result = self.assert_failed_without_writes("--json", no_site=True)
        self.assertIn(b"PyYAML", result.stderr)

    def test_selected_callers_use_one_query_before_loading_bodies(self):
        for name in ("catalog", "help", "skill-router"):
            body = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("li-catalog.py", body)
            self.assertIn("--json", body)
            self.assertIn("selected", body)
            self.assertIn("LINTEL_SOURCE_ROOT", body)
        help_body = (ROOT / "skills" / "help" / "SKILL.md").read_text()
        router = (ROOT / "skills" / "skill-router" / "SKILL.md").read_text()
        self.assertNotIn('Glob `"$root"/', help_body)
        self.assertNotIn("Read all `skills/*/SKILL.md`", router)
        self.assertNotIn("~/.lintel/telemetry/", router)


if __name__ == "__main__":
    with isolated_environment():
        unittest.main()
