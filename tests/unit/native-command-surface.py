#!/usr/bin/env python3
"""Synthetic positive and negative cases for the current command-surface guard."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / "tests" / "shape" / "native-command-surface.py"
SPEC = importlib.util.spec_from_file_location("native_command_surface", GUARD)
guard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = guard
SPEC.loader.exec_module(guard)


class CommandSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lintel-command-surface-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for name in ("verify", "diagnose", "cross-check", "web-session", "plan", "review"):
            self.skill(name)
        self.write("config/aliases.yaml", "version: 1\nskill_aliases: []\n"
                   "env_var_aliases: []\nplugin_slug_aliases: []\n")

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def skill(self, name, extra=""):
        return self.write(f"skills/{name}/SKILL.md",
                          f"---\nname: {name}\ndescription: Use to run a synthetic check.\n"
                          f"{extra}---\n# Synthetic workflow\n")

    def findings(self, text, relative="README.md"):
        self.write(relative, text)
        return guard.scan(self.root)

    def test_current_commands_and_paths_resolve(self):
        self.assertEqual(self.findings(
            "Use /li:verify, /li-diagnose and `li-cross-check`.\n"
            "Read [the plan](skills/plan/SKILL.md) and `skills/review/SKILL.md`.\n"), [])

    def test_every_retired_command_is_rejected_in_explicit_namespaces(self):
        for name in sorted(guard.RETIRED_COMMANDS):
            for prefix in ("/li:", "/li-", "skill:"):
                with self.subTest(name=name, prefix=prefix):
                    findings = self.findings(f"Use {prefix}{name}.\n")
                    self.assertTrue(any(item.code == "retired-command" for item in findings), findings)

    def test_native_and_bare_slash_retired_invocations_are_rejected(self):
        for spelling in ("`li-qa`", "`/qa --json`", "`/codex`", "the `codex` skill"):
            with self.subTest(spelling=spelling):
                self.assertTrue(self.findings(f"Run {spelling}.\n"))

    def test_retired_distinctive_plain_names_are_not_hidden(self):
        for spelling in ("plan-eng-review", "Office-Hours", "context-save", "design-shotgun"):
            with self.subTest(spelling=spelling):
                self.assertTrue(self.findings(f"Use {spelling} for this task.\n"))

    def test_routing_fields_and_method_prose_are_not_generic_storage_names(self):
        path = "lib/selection.json"
        self.assertTrue(self.findings('{"skill": "codex"}\n', path))
        self.assertTrue(self.findings('{"description": "Use the document-generate method."}\n', path))
        self.assertEqual(self.findings('{"client": "codex", "run_directory": "design-html"}\n', path), [])

    def test_generic_words_and_vendor_commands_are_not_skill_identities(self):
        self.assertEqual(self.findings(
            "Review and ship after research; health checks help us learn.\n"
            "Be careful when you browse, scrape or match data. QA is a quality discipline.\n"
            "Codex CLI and Codex App remain supported. Run `codex exec --help`.\n"
            "The HTTP `/health` endpoint is not a workflow invocation.\n"
            "The review command and the code-freeze policy remain useful.\n"
            "Preserve `.lintel/design-html` and `browse-runs` user data.\n"), [])

    def test_existing_utility_is_not_a_retired_workflow_invocation(self):
        self.write("bin/li-lessons.py", "print('li-lessons: source diagnostic')\n")
        self.assertEqual(self.findings("Use `li-lessons.py --help`; li-lessons: diagnostic.\n"), [])
        self.assertTrue(self.findings("Use /li:lessons.\n"))

    def test_python_annotation_does_not_hide_literal_routing(self):
        path = "lib/example.py"
        self.assertEqual(self.findings("def read(skill: str):\n    return skill\n", path), [])
        self.assertTrue(self.findings('choice = {"skill": "qa"}\n', path))
        self.assertTrue(self.findings('skill = "qa"\n', path))

    def test_negative_absence_assertion_does_not_hide_real_resource_dependency(self):
        path = "tests/unit/absent-reader.py"
        missing = "skills/web-session/scripts/removed.py"
        self.assertEqual(self.findings(
            'self.assertFalse((ROOT / "' + missing + '").exists())\n', path), [])
        self.assertTrue(self.findings('resource = ROOT / "' + missing + '"\n', path))
        self.assertTrue(self.findings('self.assertTrue((ROOT / "' + missing + '").exists())\n', path))

    def test_longer_surviving_names_do_not_match_retired_suffixes(self):
        self.skill("generate-style-learn")
        self.skill("frontend-design-review")
        self.assertEqual(self.findings(
            "Use /li:generate-style-learn and frontend-design-review.\n"), [])

    def test_unknown_explicit_command_is_a_dead_reference(self):
        findings = self.findings("Use /li:missing-workflow.\n")
        self.assertTrue(any(item.code == "missing-command" for item in findings), findings)

    def test_documented_format_placeholder_does_not_exempt_real_missing_names(self):
        self.assertEqual(self.findings("The /li:generate-X template denotes a format family.\n"), [])
        self.assertTrue(self.findings("Run /li:generate-missing.\n"))

    def test_retired_definition_fails_even_if_it_still_exists(self):
        self.skill("qa")
        self.assertTrue(any(item.code == "retired-entry" for item in guard.scan(self.root)))

    def test_generated_retired_wrapper_is_not_exempt(self):
        self.write(".github/skills/li-qa/SKILL.md", "---\nname: li-qa\n---\n")
        self.assertTrue(any(item.code == "retired-entry" for item in guard.scan(self.root)))

    def test_missing_skill_file_and_nested_asset_are_reported(self):
        for reference in ("skills/absent/SKILL.md", "skills/web-session/scripts/missing.mjs"):
            with self.subTest(reference=reference):
                findings = self.findings(f"Read `{reference}`.\n")
                self.assertTrue(any(item.code == "missing-path" for item in findings), findings)

    def test_synthetic_literals_are_not_source_dependencies_but_root_consumers_are(self):
        path = "tests/unit/example.py"
        self.assertEqual(self.findings(
            'self.write("skills/example/SKILL.md", "fixture")\n'
            'identity = "skill:example"\n', path), [])
        self.assertTrue(self.findings('path = ROOT / "skills/missing/SKILL.md"\n', path))
        self.assertTrue(self.findings('self.write("skills/qa/SKILL.md", "fixture")\n', path))

    def test_windows_skill_path_is_checked(self):
        findings = self.findings(r"Read `skills\missing\SKILL.md`." + "\n")
        self.assertTrue(any(item.code == "missing-path" for item in findings), findings)

    def test_invocation_spelling_is_not_a_canonical_directory(self):
        findings = self.findings("Read `skills/li:plan/SKILL.md`.\n")
        self.assertTrue(any(item.code == "missing-path" for item in findings), findings)
        findings = self.findings("Read `skills/li:qa/SKILL.md`.\n")
        self.assertTrue(any(item.code == "retired-command" for item in findings), findings)

    def test_local_markdown_links_use_the_containing_file(self):
        self.write("docs/guide.md", "See [plan](../skills/plan/SKILL.md#workflow).\n")
        self.assertEqual(guard.scan(self.root), [])
        self.write("docs/guide.md", "See [missing](../skills/plan/references/absent.md).\n")
        self.assertTrue(any(item.code == "missing-path" for item in guard.scan(self.root)))

    def test_native_relative_links_resolve_at_the_discovery_root(self):
        self.write(".github/skills/li-plan/SKILL.md", "---\nname: li-plan\n---\n")
        self.assertEqual(self.findings("Use [plan](../skills/li-plan/SKILL.md).\n",
                                      ".github/agents/planner.md"), [])

    def test_external_urls_templates_and_generic_host_commands_are_not_local_paths(self):
        self.assertEqual(self.findings(
            "See https://example.invalid/skills/qa/SKILL.md and "
            "[external](https://example.invalid/skills/qa/SKILL.md).\n"
            "Use `skills/<name>/SKILL.md`, `/skills reload`, and `/help` in the host UI.\n"
            "The helper is `${SOURCE}/skills/${name}/SKILL.md`.\n"
            "Generate `.github/skills/li-*` wrappers from canonical skills/agents.\n"
            "Keep the skills/agents/hooks interfaces consistent.\n"
            "An example utility can be named `li-example`.\n"), [])

    def test_registered_legal_text_is_preserved_with_an_explicit_exception(self):
        path = "skills/design-dna/LICENSES/MIT-next-level-builder.txt"
        self.write(path, "Required legal text mentioning /li:qa.\n")
        exemptions = []
        self.assertEqual(guard.scan(self.root, exemptions=exemptions), [])
        self.assertTrue(any(item["path"] == path and item["reason"] for item in exemptions))

    def test_historical_directories_do_not_exempt_ordinary_narrative(self):
        for path in (".claude/decisions/0001-record.md", ".claude/memory/lessons.md",
                     ".claude/plans/old/plan.md", ".claude/engineering/audits/old.md", "CHANGELOG.md"):
            with self.subTest(path=path):
                self.assertTrue(self.findings("Use /li:qa.\n", path))

    def test_bound_payload_is_preserved_but_surrounding_narrative_is_checked(self):
        path = ".claude/plans/old/report.md"
        record = {
            "schema_version": 2, "artifact_kind": "swarm-report",
            "work_map": ".claude/plans/old/work.json", "package_id": "W1",
            "leaf_ids": ["1.a"], "attempt_id": "synthetic", "acceptance_digest": "fixture",
            "result_digest": "fixture", "checks": [{"name": "Historical /li:qa observation"}],
        }
        block = "<!-- lintel-swarm-evidence:v2\n" + json.dumps(record, indent=2) + "\n-->\n"
        self.write(path, block)
        exemptions = []
        self.assertEqual(guard.scan(self.root, exemptions=exemptions), [])
        self.assertEqual(exemptions[0]["path"], path)
        self.assertEqual(exemptions[0]["field"], "lintel-swarm-evidence:v2")
        self.assertTrue(self.findings(block + "\nRun /li:qa now.\n", path))

    def test_bound_json_decision_is_not_renamed_into_current_evidence(self):
        path = ".claude/plans/old/decision.json"
        self.write(path, json.dumps({
            "schema_version": 2, "skill": "skill:qa", "status": "PASS", "timestamp": "fixture",
            "context": {}, "reviewer": {}, "provenance": "declared",
            "controls": [], "coverage": [], "evidence": ["skills/qa/SKILL.md"],
        }))
        exemptions = []
        self.assertEqual(guard.scan(self.root, exemptions=exemptions), [])
        self.assertEqual(exemptions[0]["field"], "$")
        self.assertTrue(self.findings('{"schema_version": 2, "routing": "skill:qa"}\n', path))

    def test_arbitrary_notice_named_file_is_not_an_unreviewed_exemption(self):
        self.assertTrue(self.findings("Run /li:qa.\n", "docs/NOTICE.md"))

    def test_migration_table_exempts_only_the_former_entry_column(self):
        path = "docs/migrations/commands.md"
        self.assertEqual(self.findings(
            "| Former entry | Replacement |\n|---|---|\n"
            "| `/li:qa` | `/li:verify` |\n", path), [])
        self.assertTrue(self.findings(
            "| Former entry | Replacement |\n|---|---|\n"
            "| `/li:qa` | `/li:qa-only` |\n", path))
        self.assertTrue(self.findings(
            "| Former entry | Replacement |\n|---|---|\n"
            "| `/li:qa` | `/li:verify` |\n\nRun /li:qa now.\n", path))
        self.assertEqual(self.findings(
            "| Former entries | Current route |\n|---|---|\n"
            "| `qa-only`, `codex` skill | `/li:verify --scope one\\|two` |\n", path), [])
        self.assertTrue(self.findings(
            "| Former entries | Current route |\n|---|---|\n"
            "| `qa-only` | `/li:qa --scope one\\|two` |\n", path))

    def test_required_skill_tree_cannot_be_missing_or_empty(self):
        for path in (self.root / "skills").glob("*/SKILL.md"):
            path.unlink()
        findings = guard.scan(self.root)
        self.assertTrue(any(item.code == "missing-skill-tree" for item in findings), findings)

    def test_canonical_name_is_checked_in_frontmatter_not_body(self):
        self.write("skills/plan/SKILL.md", "---\ndescription: Use to plan.\n---\nname: plan\n")
        self.assertTrue(any(item.code == "invalid-name" for item in guard.scan(self.root)))

    def test_folder_mismatch_and_native_prefix_are_invalid_canonical_names(self):
        for name in ("review", "li-plan"):
            with self.subTest(name=name):
                self.write("skills/plan/SKILL.md", f"---\nname: {name}\n---\n")
                self.assertTrue(any(item.code == "invalid-name" for item in guard.scan(self.root)))

    def test_retired_alias_metadata_does_not_reintroduce_a_command(self):
        for field in ("deprecated_aliases", "v1_alias"):
            with self.subTest(field=field):
                self.skill("verify", f"{field}: [qa]\n")
                self.assertTrue(any(item.code == "retired-alias" for item in guard.scan(self.root)))

    def test_neutral_frontmatter_aliases_need_no_duplicate_central_registration(self):
        self.skill("verify", "deprecated_aliases: [previous-entry]\n")
        self.assertEqual(guard.scan(self.root), [])

    def test_guard_cli_returns_nonzero_and_machine_readable_locations(self):
        self.write("README.md", "First line.\nUse /li:qa.\n")
        result = subprocess.run(
            [sys.executable, "-B", str(GUARD), "--root", str(self.root), "--json"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        data = json.loads(result.stdout)
        self.assertFalse(data["ok"])
        self.assertTrue(any(item["path"] == "README.md" and item["line"] == 2
                            for item in data["findings"]))
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
