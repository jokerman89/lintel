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

    def test_current_html_and_htm_routing_is_not_excluded_by_extension(self):
        for suffix in ("html", "htm"):
            relative = "docs/current." + suffix
            with self.subTest(suffix=suffix):
                self.assertEqual(self.findings("<p>Use /li:verify.</p>\n", relative), [])
                self.assertTrue(self.findings("<p>Use /li:qa.</p>\n", relative))
                self.assertTrue(self.findings(
                    '<script type="module">import "../skills/web-session/scripts/missing.mjs";</script>\n',
                    relative))
                (self.root / relative).unlink()

    def test_html_inert_evidence_field_is_visible_but_current_routing_still_fails(self):
        relative = "docs/evidence.html"
        record = json.dumps({
            "schema_version": 2, "skill": "qa", "status": "unverified",
            "timestamp": "fixture", "context": {}, "reviewer": {},
            "provenance": "declared", "controls": [], "coverage": [], "evidence": [],
        })
        inert = '<script type="application/json">' + record + "</script>\n"
        self.write(relative, inert)
        exemptions = []
        self.assertEqual(guard.scan(self.root, exemptions=exemptions), [])
        self.assertTrue(any(item.get("path") == relative
                            and item.get("field", "").endswith("/skill")
                            and item.get("classification") == "OBSERVATION"
                            for item in exemptions))
        self.assertTrue(self.findings(inert + "<p>Use /li:qa.</p>\n", relative))
        self.assertTrue(self.findings(
            inert + '<script type="module">import "../skills/qa/SKILL.md";</script>\n', relative))
        self.assertTrue(self.findings(
            '<script type="text/javascript">' + record + "</script>\n", relative))
        self.assertTrue(self.findings(
            '<script type="application/json" src="active.js">' + record + "</script>\n", relative))

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

    def test_status_skill_sentence_is_not_a_binding_but_literal_fields_are(self):
        self.assertEqual(self.findings("You are the `status` skill: read the recorded work.\n"), [])
        for text in ('skill:qa\n', 'skill: qa\n', 'Use `skill:qa`.\n', '{"skill": "qa"}\n'):
            with self.subTest(text=text):
                self.assertTrue(self.findings(text))

    def comparison(self):
        return {
            "schemaVersion": 1, "scenario": "Synthetic recorded comparison", "attempt": 2,
            "provenance": {"sourceRevision": "275a35447c4ad271e05816ade43ac48f1acec24f",
                           "frozenAt": "2026-09-20T13:04:10Z"},
            "artifacts": {"with-lintel/workflow-context.md": "# Recorded input\nRun /li:qa.\n"},
        }

    def test_reserved_comparison_result_field_does_not_exempt_current_selection(self):
        path = "presentations/tech-shots-2026-09-25/comparison/results.json"
        record = self.comparison()
        findings, observations = self.observations(json.dumps(record, indent=2), path)
        self.assertEqual(findings, [])
        self.assertTrue(any(item["field"] == "/artifacts/with-lintel~1workflow-context.md"
                            and item["category"] == "recorded comparison input" for item in observations))
        self.assertTrue(all("275a35447c4ad271e05816ade43ac48f1acec24f" in item["reason"]
                            and "not cryptographic binding" in item["reason"] for item in observations))
        record["selection"] = {"members": ["skill:qa"], "resources": ["skills/qa/SKILL.md"]}
        self.assertTrue(self.findings(json.dumps(record), path))
        del record["selection"]
        record["artifacts"]["new-current-instruction"] = "Use /li:qa."
        self.assertTrue(self.findings(json.dumps(record), path))

    def test_serialized_comparison_literal_does_not_hide_javascript_imports_beside_it(self):
        path = "presentations/tech-shots-2026-09-25/comparison/data.js"
        text = "window.COMPARISON_DATA = " + json.dumps(self.comparison()) + ";\n"
        findings, observations = self.observations(text, path)
        self.assertEqual(findings, [])
        self.assertTrue(any(item["field"] == "window.COMPARISON_DATA/artifacts/with-lintel~1workflow-context.md"
                            and item["line"] == 1 for item in observations))
        for statement in ('import old from "skills/qa/SKILL.md";',
                          'import reader from "skills/web-session/scripts/missing.mjs";',
                          'const selection = "skill:qa";'):
            with self.subTest(statement=statement):
                self.assertTrue(self.findings(text.rstrip() + statement + "\n", path))
        self.assertTrue(self.findings(text.replace("window.COMPARISON_DATA", "window.CURRENT_ROUTES"), path))

    def test_standalone_original_prompt_requires_the_exact_recorded_copy(self):
        root = "presentations/tech-shots-2026-09-25/comparison/"
        record = self.comparison()
        self.write(root + "results.json", json.dumps(record))
        prompt = record["artifacts"]["with-lintel/workflow-context.md"]
        path = root + "with-lintel/workflow-context.md"
        findings, observations = self.observations(prompt, path)
        self.assertEqual(findings, [])
        self.assertTrue(any(item["path"] == path and item["line"] == 1
                            and item["field"] == "original prompt copied from results.json/artifacts/with-lintel~1workflow-context.md"
                            for item in observations))
        self.assertTrue(self.findings(prompt + "\nImport `skills/qa/SKILL.md` now.\n", path))
        self.write(path, prompt)
        (self.root / root / "results.json").unlink()
        self.assertTrue(guard.scan(self.root))

    def test_snapshot_classification_is_not_a_presentation_or_schema_wide_exemption(self):
        record = self.comparison()
        unrelated = "presentations/new/results.json"
        self.assertTrue(self.findings(json.dumps(record), unrelated))
        (self.root / unrelated).unlink()
        path = "presentations/tech-shots-2026-09-25/comparison/results.json"
        record["provenance"]["sourceRevision"] = "7654321"
        self.assertTrue(self.findings(json.dumps(record), path))
        record = self.comparison()
        del record["provenance"]["frozenAt"]
        self.assertTrue(self.findings(json.dumps(record), path))

    def inventory(self):
        return {"baseline": "1234567890abcdef1234567890abcdef12345678", "files": [{
            "path": "skills/qa/SKILL.md", "group": "skills", "bytes": 21, "lines": 3,
            "skill_refs": ["qa", "/li:context-save"], "tool_terms": ["Read"],
        }]}

    def audit_review(self):
        return {
            "scope": {"kind": "audit-only"}, "baseline": {"commit": "1234567"},
            "coverage": [{
                "name": "qa", "path": "skills/qa/SKILL.md", "lines_read": 3,
                "quality": "mixed", "action": "refine", "reason": "The /li:qa source was inspected.",
                "evidence": [{"path": "skills/qa/SKILL.md", "line": 2}],
            }],
            "findings": [{
                "id": "F01", "priority": "P2", "title": "Original diagnosis",
                "problem": "The /li:qa route was redundant.", "impact": "Source ambiguity",
                "recommendation": "Merge /li:qa-only into /li:qa.",
                "evidence": [{"path": "skills/qa/SKILL.md", "line": 2}],
                "verification": "Original source read.", "confidence": "high",
            }],
            "interactions": [{"journey": "Original route", "observation": "Use of /li:qa was recorded.",
                              "related_findings": ["F01"]}],
            "limitations": ["No /li:qa execution."],
        }

    def observations(self, text, relative):
        self.write(relative, text)
        records = []
        findings = guard.scan(self.root, exemptions=records)
        return findings, [item for item in records if item.get("classification") == "OBSERVATION"]

    def test_inventory_fields_are_located_observations_not_current_routes(self):
        text = json.dumps(self.inventory(), indent=2)
        path = ".claude/engineering/audits/sample/inventory.json"
        findings, observations = self.observations(text, path)
        self.assertEqual(findings, [])
        source = next(item for item in observations if item["field"] == "/files/0/path")
        self.assertEqual(source["path"], path)
        self.assertEqual(source["line"], next(i for i, line in enumerate(text.splitlines(), 1)
                                             if '"path":' in line))
        self.assertEqual(source["category"], "source-era inventory")
        self.assertIn("not verified", source["reason"])
        record = self.inventory()
        record["selection"] = {"members": ["skill:qa"], "resources": ["skills/qa/SKILL.md"]}
        self.assertTrue(self.findings(json.dumps(record), path))
        del record["selection"]
        record["files"][0]["current_route"] = "skill:qa"
        self.assertTrue(self.findings(json.dumps(record), path))

    def test_inventory_shape_requires_a_declared_baseline_and_source_measurements(self):
        path = "docs/inventory.json"
        for key in ("baseline", "files"):
            record = self.inventory()
            del record[key]
            record["route"] = "/li:qa"
            self.assertTrue(self.findings(json.dumps(record), path))
        record = self.inventory()
        del record["files"][0]["bytes"]
        self.assertTrue(self.findings(json.dumps(record), path))

    def test_historical_review_fields_preserve_original_recommendations(self):
        record = self.audit_review()
        path = ".claude/engineering/audits/sample/review.json"
        findings, observations = self.observations(json.dumps(record, indent=2), path)
        self.assertEqual(findings, [])
        self.assertTrue(any(item["field"] == "/findings/0/recommendation" for item in observations))
        self.assertTrue(any(item["field"] == "/coverage/0/evidence/0/path" for item in observations))
        record["imports"] = ["skills/qa/SKILL.md"]
        self.assertTrue(self.findings(json.dumps(record), path))
        del record["imports"]
        record["coverage"][0]["selection"] = "skill:qa"
        self.assertTrue(self.findings(json.dumps(record), path))

    def test_runtime_audit_variant_keeps_its_findings_but_not_added_selection(self):
        record = self.audit_review()
        record["baseline"] = "1234567"
        record["coverage"] = {"bin": {"mode": "All files read", "files": {"example.py": 12}}}
        record["interactions"] = ["Recorded /li:qa interaction.", {
            "subsystem": "Original workflows", "current": "The recorded /li:qa route.",
            "target": "Original recommendation about /li:qa-only.", "findings": ["F01"],
        }]
        path = "docs/runtime-review.json"
        findings, observations = self.observations(json.dumps(record, indent=2), path)
        self.assertEqual(findings, [])
        self.assertTrue(any(item["field"] == "/interactions/1/target" for item in observations))
        record["coverage"]["selection"] = {"members": ["skill:qa"]}
        self.assertTrue(self.findings(json.dumps(record), path))

    def test_current_selection_cannot_borrow_an_audit_baseline(self):
        path = "lib/capability-selections.json"
        record = {"baseline": "1234567", "scope": {}, "coverage": [],
                  "members": ["skill:qa"], "resources": ["skills/qa/SKILL.md"]}
        self.assertTrue(self.findings(json.dumps(record), path))
        record.update(findings=[], interactions=[], limitations=[])
        self.assertTrue(self.findings(json.dumps(record), path))

    def test_observation_spans_preserve_same_line_current_fields_and_escaped_values(self):
        record = self.inventory()
        record["files"][0]["path"] = "skills\\qa\\SKILL.md"
        text = json.dumps(record, separators=(",", ":"))
        findings, observations = self.observations(text, "docs/inventory.json")
        self.assertEqual(findings, [])
        self.assertTrue(all(item["line"] == 1 and item["field"] and item["reason"]
                            for item in observations))
        record["current"] = "Use /li:qa."
        findings = self.findings(json.dumps(record, separators=(",", ":")), "docs/inventory.json")
        self.assertTrue(any(item.line == 1 and item.code == "retired-command" for item in findings))

    def test_duplicate_json_keys_do_not_acquire_observation_status(self):
        text = json.dumps(self.inventory()).rstrip("}") + ', "files": [{"path":"skills/qa/SKILL.md"}]}'
        findings, observations = self.observations(text, "docs/inventory.json")
        self.assertTrue(findings)
        self.assertEqual(observations, [])

    def test_coordination_ownership_does_not_hide_current_routing_fields(self):
        record = {
            "schema_version": 1, "initiative": "sample", "work_map": ".claude/plans/sample/work.json",
            "charter": ".claude/plans/sample/swarm/charter.md",
            "scope_rules": {"worker": "write_scope+own_report", "reviewer": "own_review",
                            "reducers": "coordinator-only"},
            "coordinator_paths": ["skills/qa/SKILL.md"],
            "lanes": [{"task_id": "W1", "write_scope": ["skills/qa", "skills/qa-only"]}],
        }
        path = ".claude/plans/sample/swarm/coordination.json"
        findings, observations = self.observations(json.dumps(record, indent=2), path)
        self.assertEqual(findings, [])
        self.assertTrue(any(item["field"] == "/lanes/0/write_scope/0" for item in observations))
        record["lanes"][0]["skill"] = "qa"
        self.assertTrue(self.findings(json.dumps(record), path))
        del record["lanes"][0]["skill"]
        record["selection"] = {"resources": ["skills/qa/SKILL.md"]}
        self.assertTrue(self.findings(json.dumps(record), path))
        self.assertTrue(self.findings('{"write_scope":["skills/qa/SKILL.md"]}\n', path))

    def test_source_era_table_cells_do_not_exempt_new_current_use_columns_or_prose(self):
        path = "docs/record.md"
        text = ("Baseline: main `1234567`, 2026-09-20.\n\n"
                "| Original source | Original recommendation | Evidence |\n|---|---|---|\n"
                "| [qa](../skills/qa/SKILL.md) | Merge /li:qa-only | skills/qa/SKILL.md:2 |\n")
        findings, observations = self.observations(text, path)
        self.assertEqual(findings, [])
        self.assertTrue(any(item["line"] == 5 and "Original source" in item["field"]
                            for item in observations))
        self.assertTrue(self.findings(text + "\nUse /li:qa now.\n", path))
        self.assertTrue(self.findings(text.replace(" | Evidence |", " | Current route |"), path))
        self.assertTrue(self.findings(text.split("\n\n", 1)[1], path))

    def test_inspected_multilingual_inventory_table_is_source_era_not_translation(self):
        path = "docs/inventory.md"
        text = ("Baseline: main `1234567`, 2026-09-20.\n\n"
                "| Namn | Kvalitet | Åtgärd | Motivering | Belägg |\n|---|---|---|---|---|\n"
                "| [qa](../skills/qa/SKILL.md) | Mixed | Refine | Original /li:qa rationale | skills/qa/SKILL.md:2 |\n")
        findings, observations = self.observations(text, path)
        self.assertEqual(findings, [])
        self.assertTrue(observations)
        self.assertTrue(self.findings(text + "\nImport `skills/qa/SKILL.md`.\n", path))

    def test_dated_component_table_is_not_a_blanket_audit_exemption(self):
        path = "docs/audit.md"
        text = ("**Auditor pass date:** 2026-09-20\n\n"
                "| Component | Path | Role in chain |\n|---|---|---|\n"
                "| qa-only | skills/qa-only/SKILL.md | Original verification |\n")
        findings, observations = self.observations(text, path)
        self.assertEqual(findings, [])
        self.assertTrue(any(item["field"] == "table column: Path" for item in observations))
        self.assertTrue(self.findings(text + "\nUse /li:qa-only.\n", path))
        self.assertTrue(self.findings(text.replace("2026-09-20", "unspecified"), path))

    def test_pinned_preservation_table_keeps_current_instructions_outside_its_record(self):
        path = "docs/preservation.md"
        text = ("Historical source comparison at `1234567`.\n\n"
                "| Original and current source | Original recommendation; source state | Responsible package and acceptance | Retained method and output | Change or grounded retention rationale | Worked example and evidence | Remaining boundary |\n"
                "|---|---|---|---|---|---|---|\n"
                "| [qa](../skills/qa/SKILL.md) | Refine | Original W1 | Recorded /li:qa method | Original rationale | Run /li:qa in the original case | Not current clearance |\n")
        findings, observations = self.observations(text, path)
        self.assertEqual(findings, [])
        self.assertTrue(any(item["field"] == "table column: Worked example and evidence" for item in observations))
        self.assertTrue(self.findings(text + "\nCurrent selection: /li:qa.\n", path))
        self.assertTrue(self.findings(text.replace("| Remaining boundary |", "| Remaining boundary | Current route |")
                                     .replace("|---|\n", "|---|---|\n")
                                     .replace("| Not current clearance |", "| Not current clearance | /li:qa |"), path))

    def test_snapshot_table_requires_actual_metadata_fields_not_a_heading_only(self):
        path = "docs/report.md"
        text = ("| Path | Status | Mode | Bytes (Git LF) | SHA-256 (Git LF blob) | Commits |\n"
                "|---|---|---|---|---|---|\n"
                "| `skills/qa/SKILL.md` | D | 100644 | 42 | `" + "a" * 64 + "` | 1234567 |\n")
        findings, observations = self.observations(text, path)
        self.assertEqual(findings, [])
        self.assertTrue(any(item["line"] == 3 and item["field"] == "table column: Path" for item in observations))
        self.assertTrue(self.findings(text.replace("100644", "unknown"), path))
        self.assertTrue(self.findings(text.replace("`skills/qa/SKILL.md`", "Use /li:qa."), path))
        self.assertTrue(self.findings(text + "\nImport `skills/qa/SKILL.md`.\n", path))

    def test_deleted_path_list_is_data_but_its_heading_does_not_authorize_execution(self):
        path = "docs/report.md"
        text = ("### Actual deleted paths\n\n"
                "Observed with `git diff --name-only --diff-filter=D`.\n\n"
                "```text\nskills/qa/SKILL.md\nskills/web-session/scripts/removed.py\n```\n")
        findings, observations = self.observations(text, path)
        self.assertEqual(findings, [])
        self.assertTrue(any(item["line"] == 6 and item["category"] == "deleted-path record"
                            for item in observations))
        self.assertTrue(self.findings(text + "\nUse /li:qa.\n", path))
        self.assertTrue(self.findings(text.replace("```text", "```bash"), path))
        self.assertTrue(self.findings(text.replace("skills/qa/SKILL.md", "Use /li:qa."), path))

    def test_changelog_removed_resource_is_visible_but_current_use_is_not_exempt(self):
        path = "CHANGELOG.md"
        text = ("## 0.11.0 - unreleased\n\n### Removed\n\n"
                "- The retired reader (`skills/web-session/scripts/removed.py`) and its tests.\n")
        findings, observations = self.observations(text, path)
        self.assertEqual(findings, [])
        self.assertTrue(any(item["line"] == 5 and "Removed" in item["field"] for item in observations))
        self.assertTrue(self.findings(text + "- Use `skills/web-session/scripts/removed.py` now.\n", path))
        self.assertTrue(self.findings(text.replace("### Removed", "### Added"), path))
        self.assertTrue(self.findings(text.replace(" and its tests.", "; import `skills/web-session/scripts/removed.py`."), path))

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
        self.assertTrue(any(item["field"] == "lintel-swarm-evidence:v2/checks" for item in exemptions))
        self.assertTrue(all(item["line"] > 1 for item in exemptions))
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
        self.assertTrue(any(item["field"] == "/skill" for item in exemptions))
        self.assertTrue(all(item["line"] == 1 for item in exemptions))
        self.assertTrue(self.findings('{"schema_version": 2, "routing": "skill:qa"}\n', path))

    def test_recorded_v2_fields_never_exempt_an_unknown_current_route(self):
        path = "docs/decision.json"
        record = {
            "schema_version": 2, "skill": "skill:qa", "status": "PASS", "timestamp": "fixture",
            "context": {}, "reviewer": {}, "provenance": "declared",
            "controls": [], "coverage": [], "evidence": ["skills/qa/SKILL.md"],
            "current_route": "skill:qa-only",
        }
        findings, observations = self.observations(json.dumps(record, indent=2), path)
        self.assertTrue(any(item.code == "retired-command" and "qa-only" in item.message for item in findings))
        self.assertFalse(any(item["field"] == "/current_route" for item in observations))
        self.assertTrue(all("not verified" in item["reason"] for item in observations))

    def test_cli_observations_are_located_visible_and_do_not_mutate_the_source_record(self):
        path = self.write("docs/inventory.json", json.dumps(self.inventory(), indent=2))
        original = path.read_bytes()
        for flags in ([], ["--json"]):
            result = subprocess.run([sys.executable, "-B", str(GUARD), "--root", str(self.root), *flags],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            if flags:
                data = json.loads(result.stdout)
                observations = [item for item in data["exemptions"]
                                if item.get("classification") == "OBSERVATION"]
                self.assertTrue(observations)
                for item in observations:
                    self.assertEqual(item["path"], "docs/inventory.json")
                    self.assertGreater(item["line"], 0)
                    self.assertGreaterEqual(item["end_line"], item["line"])
                    self.assertTrue(item["field"] and item["category"] and item["reason"])
            else:
                self.assertIn("OBSERVATION docs/inventory.json:5 [/files/0/path]", result.stdout)
            self.assertEqual(path.read_bytes(), original)

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
