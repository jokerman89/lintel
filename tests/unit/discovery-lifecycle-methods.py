#!/usr/bin/env python3
# component: discovery-lifecycle-method-tests
# implements: ADR-0029, ADR-0034
# intent: .claude/plans/v2-findings/spec.md
# constraints: local source/helper checks; no network, model, profile binding or publication
# last_intent_review: 2026-10-03
"""Regressions for the retained discovery and lifecycle front doors."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def source(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def linked_method(case, caller, owner):
    text = source(caller)
    links = re.findall(r"\]\(([^)]+)\)", text)
    matches = [
        link for link in links
        if (ROOT / caller).parent.joinpath(link.split("#")[0]).resolve() == ROOT / owner
    ]
    case.assertTrue(matches, f"{caller} must delegate to {owner}")
    case.assertTrue((ROOT / owner).is_file(), f"missing shared owner: {owner}")
    return source(owner)


class DiscoveryMethods(unittest.TestCase):
    def test_catalog_is_the_single_intent_method_owner(self):
        owner = "skills/catalog/references/intent.md"
        for name in ("catalog", "skill-router", "orientator", "welcome", "sense"):
            with self.subTest(name=name):
                method = linked_method(self, f"skills/{name}/SKILL.md", owner)
                for required in ("at most three", "literal", "source_root", "unavailable",
                                 "not a new routing engine", "customer data"):
                    self.assertIn(required, method)
                self.assertNotIn("- For agent selection", method)
                self.assertIn("shortlist agent metadata", method)
        for name in ("skill-router", "orientator", "welcome"):
            text = source(f"skills/{name}/SKILL.md")
            self.assertNotIn('li-catalog.py" --json --query', text)
            self.assertNotIn("Shortlist at most three skills", text)

    def test_orientation_keeps_sense_control_not_an_escalation_claim(self):
        orientation = source("skills/orientator/SKILL.md")
        self.assertNotIn("80%", orientation)
        self.assertNotIn("invoke_llm_orientation", orientation)
        self.assertNotIn("escalated=", orientation)
        self.assertIn("SENSE", orientation)
        self.assertIn("high-risk", orientation)
        self.assertIn("host", orientation)
        sense = source("skills/sense/SKILL.md")
        for operation in ("verify_profile_context", "classify_intent", "assess_risk",
                          "audit_log orientator-decisions", "high-risk always confirms"):
            self.assertIn(operation, sense)

    def query(self, *arguments, expected=0):
        catalog = ROOT / "skills/CATALOG.md"
        before = hashlib.sha256(catalog.read_bytes()).hexdigest()
        result = subprocess.run(
            [sys.executable, "-B", ROOT / "bin/li-catalog.py", "--json", *arguments],
            cwd=ROOT, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, expected, result.stderr.decode("utf-8"))
        self.assertEqual(hashlib.sha256(catalog.read_bytes()).hexdigest(), before)
        return json.loads(result.stdout) if expected == 0 else result

    def test_catalog_queries_remain_literal_read_only_metadata(self):
        result = self.query("--kind=all", "--query=role")
        self.assertFalse(result["executed"])
        self.assertTrue(result["entries"])
        self.assertTrue(all(entry["maturity"] == "unknown" for entry in result["entries"]))
        for literal in ("$(touch forbidden-marker)", "[$.*]", "--check"):
            with self.subTest(literal=literal):
                self.assertEqual(self.query("--query=" + literal)["entries"], [])

    def test_unsupported_flags_and_invalid_kinds_remain_parser_errors(self):
        self.query("--trends", expected=2)
        self.query("--kind=not-a-kind", expected=2)


class RoleMethods(unittest.TestCase):
    def test_all_role_front_doors_share_one_complete_lifecycle(self):
        for name in ("role", "role-new", "roles-list"):
            with self.subTest(name=name):
                method = linked_method(
                    self, f"skills/{name}/SKILL.md", "skills/role/references/lifecycle.md",
                )
                for clause in (
                    "role-list", "role-show", "role-set", "role-off", "role-write",
                    "persona-sources", "--include-private", "--allow-private",
                    "--expected-sha256", "--audience", "--frame", "--deep-dive",
                    "COLD KNOWLEDGE", "DECISION CRITERIA", "OUTCOME LENS",
                    "SENSITIVE CONTEXT", "previous preference", "malformed",
                    "synchronization", "current conversation",
                ):
                    self.assertIn(clause, method)
                self.assertNotIn("```bash", source(f"skills/{name}/SKILL.md"),
                                 "CLI procedure must live at the shared owner")

    def test_original_names_and_flag_sets_are_retained(self):
        self.assertIn("name: role-new\n", source("skills/role-new/SKILL.md"))
        self.assertIn("--update", source("skills/role-new/SKILL.md"))
        self.assertIn("name: roles-list\n", source("skills/roles-list/SKILL.md"))
        for flag in ("--off", "--rotate", "--frame", "--deep-dive", "--audience",
                     "--clear-audience"):
            self.assertIn(flag, source("skills/role/SKILL.md"))


class LifecycleOwnerMethods(unittest.TestCase):
    def test_pack_front_doors_share_one_lifecycle_without_a_new_public_pack_command(self):
        for name in ("pack-create", "pack-list", "pack-validate", "pack-switch"):
            with self.subTest(name=name):
                method = linked_method(self, f"skills/{name}/SKILL.md",
                                       "skills/pack-switch/references/lifecycle.md")
                for token in ("pack-create", "pack-list", "pack-validate", "pack-switch",
                              "--scope", "--extends", "--from", "--reason",
                              "PROFILE_SWITCH_INCOMPLETE", "shadowed", "read-only",
                              "profile-rebind", "generation", "manifest only"):
                    self.assertTrue(token.lower() in method.lower(), f"{name}: missing {token}")
                self.assertNotIn("```bash", source(f"skills/{name}/SKILL.md"))
        self.assertFalse((ROOT / "skills/pack/SKILL.md").exists())

    def test_audit_and_hooks_share_reader_and_preserve_observation_boundaries(self):
        for name in ("audit", "hooks-status"):
            with self.subTest(name=name):
                method = linked_method(self, f"skills/{name}/SKILL.md",
                                       "skills/audit/references/method.md")
                for token in ("read.sh", "li-events.py", "audit_read_files",
                              "--records", "--overrides", "--unobserved", "not_performed",
                              "non_recording_hooks", "unobserved", "cycle_id", "diagnostic"):
                    self.assertIn(token, method)
        reader = source("skills/audit/references/read.sh")
        self.assertIn("audit_read_files", reader)
        self.assertIn("li-events.py", reader)
        self.assertNotRegex(reader, r"\baudit_log\b")

    def test_doctor_owns_instructions_and_migration_inspection_not_implicit_repairs(self):
        for name in ("doctor", "instruction-parity-check", "migrations"):
            with self.subTest(name=name):
                method = linked_method(self, f"skills/{name}/SKILL.md",
                                       "skills/doctor/references/inspection.md")
                for token in ("li-doctor", "li-instructions.py", "li-adapter.py",
                              "migrations", "--all", "--dry-run", "read-only",
                              "malformed", "unknown", "archived", "project prose",
                              "host", "pack-switch/references/lifecycle.md"):
                    self.assertIn(token, method)

    def test_maintenance_retains_four_flags_and_only_real_owner_routes(self):
        text = source("skills/maintenance/SKILL.md")
        for name in ("context-budget", "doctor", "audit"):
            self.assertIn(f"../{name}/", text)
        for flag in ("--force-compact", "--monitor-paths", "--simulate-tokens", "--rust-report"):
            self.assertIn(flag, text)
        for stale in ("mode_envelopes", "--trends", "load-bearing_paths:",
                      "scale_token_estimate", "keep recent state for 30 days minimum"):
            self.assertNotIn(stale, text)
        self.assertIn("unobserved", text)
        self.assertIn("No implicit cleanup", text)


class OwnedLifecycleFixture(unittest.TestCase):
    """Use actual CLI readers/writers, but never create or rebind a profile context."""

    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="discovery-lifecycle-", dir=os.environ["TEMP"])).resolve()
        self.repo, self.home = self.base / "repo", self.base / "home"
        self.repo.mkdir()
        self.home.mkdir()
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("LINTEL_", "CLAUDE_"))}
        self.env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
        self.command = [
            sys.executable, "-B", str(ROOT / "bin/li-lifecycle.py"),
            "--source", str(ROOT), "--repo", str(self.repo), "--home", str(self.home),
            "--packs", str(self.base / "packs"), "--pointer", str(self.home / "active-pack"),
        ]

    def tearDown(self):
        # Retain the exact small fixture for inspection; no tree deletion is needed.
        self.assertFalse(list(self.base.rglob("current-profile.json")))
        self.assertFalse(list(self.base.rglob("selected.json")))
        print(f"Retained owned fixture: {self.base}")

    def helper(self, *arguments, expected=0):
        result = subprocess.run(
            [*self.command, *map(str, arguments)], env=self.env, cwd=self.repo,
            capture_output=True, timeout=30, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout) if expected == 0 else result

    def write(self, relative, text):
        path = self.base / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def snapshot(self):
        return {p.relative_to(self.base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.base.rglob("*") if p.is_file()}

    @staticmethod
    def role_text(name="advisor", sensitivity="public"):
        return (
            f"---\nrole_id: {name}\ndisplay_name: Synthetic advisor\nscope: engineering\n"
            f"audience: maintainers\nvoice_tier: internal\nsensitivity: {sensitivity}\n"
            "last_updated: 2026-10-03\n---\n"
            "# IDENTITY\nReview the original requirements.\n"
            "# COLD KNOWLEDGE\nnot-in-light-summary\n"
            "# DECISION CRITERIA\nEvidence before conclusions.\n"
            "# VOICE + COMMUNICATION\nPrecise.\n"
            "# OUTCOME LENS\n- BUILD: verified behavior.\n"
            "# ROLE-SPECIFIC INSIGHTS\nKeep host authority separate.\n"
            "# COMPANION SKILLS\n- review\n"
            "# SENSITIVE CONTEXT\nnot-in-light-summary-either\n"
        )


class RoleHelpers(OwnedLifecycleFixture):
    def test_private_inventory_body_consent_and_light_deep_boundaries(self):
        self.write("home/roles/advisor.md", self.role_text())
        self.write("home/roles/private/private-advisor.md", self.role_text("private-advisor", "private"))
        before = self.snapshot()
        public = self.helper("role-list")
        self.assertEqual([row["role_id"] for row in public["roles"]], ["advisor"])
        self.assertIsNone(public["profile_reference"])
        private = self.helper("role-list", "--include-private")
        self.assertEqual(len(private["roles"]), 2)
        self.assertNotIn("not-in-light-summary", json.dumps(private))
        failure = self.helper("role-show", "private-advisor", expected=2)
        self.assertIn("PRIVATE_ROLE_CONFIRMATION", failure.stderr)
        light = self.helper("role-show", "private-advisor", "--allow-private")
        self.assertNotIn("not-in-light-summary", json.dumps(light))
        deep = self.helper("role-show", "private-advisor", "--allow-private", "--deep")
        self.assertIn("not-in-light-summary", deep["content"])
        self.assertEqual(self.snapshot(), before)


class InspectionHelpers(OwnedLifecycleFixture):
    def test_budget_routes_keep_unknown_observations_and_reject_missing_map(self):
        env = dict(self.env, LINTEL_REPO_ROOT=self.repo.as_posix(),
                   LINTEL_SOURCE_ROOT=ROOT.as_posix(), LINTEL_HOME=self.home.as_posix())
        command = [r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt" else "bash",
                   ROOT / "skills/context-budget/references/route.sh"]
        before = self.snapshot()
        result = subprocess.run([*command, "--advice", "--bytes", "16"], cwd=self.repo,
                                env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        advice = json.loads(result.stdout)
        self.assertFalse(advice["host_settings_changed"])
        self.assertIn("unknown", result.stdout)
        result = subprocess.run([*command, "--handoff", "--map", "missing.json"], cwd=self.repo,
                                env=env, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_pack_list_validation_and_refusals_use_existing_cli_without_binding(self):
        before = self.snapshot()
        listing = self.helper("pack-list")
        self.assertEqual(listing["effective_pack"], "_default")
        validated = self.helper("pack-validate")
        self.assertEqual(validated["name"], "_default")
        self.assertIsNone(validated["profile_reference"])
        self.assertEqual(self.snapshot(), before)
        for args in (
            ("pack-create", "_default", "--scope", "repo"),
            ("pack-create", "child", "--scope", "repo", "--extends", "missing"),
            ("pack-create", "child", "--scope", "repo", "--extends", "_default", "--from", "_default"),
            ("pack-switch", "_default", "--reason", ""),
            ("pack-validate", "--unknown"),
        ):
            with self.subTest(args=args):
                self.helper(*args, expected=2)
                self.assertEqual(self.snapshot(), before)

    def test_required_profile_failure_is_not_neutral_success(self):
        self.write("repo/.claude/profile-requirements.json",
                   '{"schema_version":1,"required_pack":"missing"}')
        before = self.snapshot()
        for args in (("pack-validate",), ("pack-list",), ("pack-switch", "_default", "--reason", "test")):
            with self.subTest(args=args):
                self.assertIn("PROFILE_REQUIRED", self.helper(*args, expected=2).stderr)
                self.assertEqual(self.snapshot(), before)

    def test_real_doctor_and_migrations_are_observations_not_repairs(self):
        self.write("repo/tasks/lessons.md", "Synthetic legacy content.\n")
        before = self.snapshot()
        failed = self.helper("doctor", "--json", "--store", self.base / "recovery",
                             "--native-store", self.base / "native-recovery", expected=1)
        diagnostic = json.loads(failed.stdout)
        self.assertEqual(diagnostic["host_activation"], "unverified")
        self.assertEqual(diagnostic["hook_execution"], "unverified")
        self.assertEqual(diagnostic["layout"]["observation"], "needs_migration")
        self.assertTrue(diagnostic["foundation_missing"])
        rows = self.helper("migrations", "--all", "--today", "2026-10-03")
        self.assertTrue(rows)
        self.assertEqual(self.snapshot(), before)
        self.helper("doctor", "--instructions", expected=2)
        self.helper("migrations", "--apply", expected=2)
        self.assertEqual(self.snapshot(), before)

    def test_uniformity_missing_trusted_floor_never_runs_target_code(self):
        text = source("skills/uniformity/SKILL.md")
        script = re.search(r"```bash\n(.*?)```", text, re.S).group(1)
        self.write("repo/tests/shape/uniformity-coverage.sh", "touch TARGET_CODE_EXECUTED\n")
        trusted = self.base / "trusted-without-tests"
        trusted.mkdir()
        env = dict(self.env, LINTEL_SOURCE_ROOT=trusted.as_posix())
        before = self.snapshot()
        result = subprocess.run(
            [r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt" else "bash", "-c", script],
            env=env, cwd=self.repo, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("UNAVAILABLE", result.stderr)
        self.assertIn("source floor helper missing", result.stderr)
        self.assertEqual(self.snapshot(), before)


class AuditHelpers(OwnedLifecycleFixture):
    def read_audit(self, *arguments, expected=0):
        env = dict(self.env, LINTEL_SOURCE_ROOT=ROOT.as_posix(),
                   LINTEL_REPO_ROOT=self.repo.as_posix(), LINTEL_HOME=self.home.as_posix())
        before = self.snapshot()
        result = subprocess.run(
            [r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt" else "bash",
             ROOT / "skills/audit/references/read.sh", *arguments],
            env=env, cwd=self.repo, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)
        return result

    def test_argument_and_missing_log_failures_do_not_drop_filters(self):
        self.write("repo/.claude/lintel-layout.yaml", "layout_version: 5\n")
        for args in (("--since",), ("--since", "bad"), ("--category",),
                     ("--category", "../escape"), ("--limit", "0"), ("--unknown",)):
            with self.subTest(args=args):
                self.read_audit(*args, expected=2)
        missing = self.read_audit("--category", "hooks", expected=3)
        self.assertIn("unobserved", missing.stdout)

    def test_real_reader_preserves_diagnostics_counts_and_legacy_log_notice(self):
        self.write("repo/.claude/lintel-layout.yaml", "layout_version: 5\n")
        record = '{"ts":"2026-10-03T10:00:00Z","kind":"hook_ran","hook":"fixture"}\n'
        # Unknown-kind and malformed lines must not become ordinary records or be hidden.
        self.write("repo/.claude/runtime/audit/hooks.jsonl", record + "{not-json}\n")
        self.write("home/audit/hooks.jsonl", "legacy source not selected\n")
        result = self.read_audit("--category", "hooks", "--limit", "1", expected=4)
        self.assertIn("also present, not read", result.stderr)
        self.assertIn("malformed_json", result.stdout)
        self.assertIn("unknown_kind", result.stdout)
        self.assertIn("observed_with_diagnostics", result.stdout)
        self.assertNotIn("legacy source not selected", result.stdout)


class RoleMutationHelpers(OwnedLifecycleFixture):
    def test_rotation_and_malformed_preferences_fail_without_losing_prior_selection(self):
        self.write("home/roles/advisor.md", self.role_text())
        self.write("home/roles/private/private-advisor.md", self.role_text("private-advisor", "private"))
        preference = self.write("home/profile.yaml", "# keep\nrole_active: advisor # keep too\nother: 42\n")
        before = self.snapshot()
        self.assertIn("current role is unchanged", self.helper("role-set", "missing", expected=2).stderr)
        self.assertIn("PRIVATE_ROLE_CONFIRMATION", self.helper("role-set", "private-advisor", expected=2).stderr)
        self.assertEqual(self.snapshot(), before)
        same = self.helper("role-set", "advisor")
        self.assertFalse(same["changed"])
        self.assertEqual(self.snapshot(), before)
        preference.write_text("role_active: advisor\nrole_active: other\n", encoding="utf-8")
        before = self.snapshot()
        self.helper("role-off", expected=2)
        self.assertEqual(self.snapshot(), before)

    def test_role_write_and_digest_guard_keep_original_and_scope(self):
        draft = self.write("draft.md", self.role_text())
        created = self.helper("role-write", "advisor", "--file", draft, "--scope", "public")
        self.assertFalse(created["activated"])
        self.assertFalse(created["synchronized"])
        path = Path(created["path"])
        self.assertEqual(path.read_bytes(), draft.read_bytes())
        draft.write_text(self.role_text().replace("Precise.", "Precise and concise."), encoding="utf-8")
        before = self.snapshot()
        for digest in (None, "0" * 64):
            args = [] if digest is None else ["--expected-sha256", digest]
            self.helper("role-write", "advisor", "--file", draft, "--scope", "public", *args, expected=2)
            self.assertEqual(self.snapshot(), before)
        updated = self.helper("role-write", "advisor", "--file", draft, "--scope", "public",
                              "--expected-sha256", created["sha256"])
        self.assertEqual(updated["status"], "updated")
        self.assertNotEqual(updated["sha256"], created["sha256"])
        before = self.snapshot()
        self.helper("role-write", "advisor", "--file", draft, "--scope", "private",
                    "--expected-sha256", updated["sha256"], expected=2)
        self.assertEqual(self.snapshot(), before)

    def test_incomplete_role_and_audience_reads_never_publish_or_activate(self):
        draft = self.write("incomplete.md", self.role_text().replace("# DECISION CRITERIA", "# OTHER"))
        before = self.snapshot()
        self.helper("role-write", "advisor", "--file", draft, "--scope", "public", expected=2)
        self.assertEqual(self.snapshot(), before)
        self.write("repo/.claude/memory/personas.md", "# maintainer\nSynthetic purpose.\n")
        before = self.snapshot()
        audience = self.helper("persona-sources")
        self.assertEqual(audience["lifetime"], "current conversation only")
        self.assertEqual(len(audience["sources"]), 1)
        self.assertIsNone(audience["profile_reference"])
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.helper("role-off")["changed"])
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
