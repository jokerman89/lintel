#!/usr/bin/env python3
# component: core-boundary-method-tests
# implements: ADR-0006, ADR-0007, ADR-0028, ADR-0029, ADR-0033
# intent: .claude/plans/v2-findings/plan.md
# constraints: source/caller/history contracts only; no model, writer, communication or promotion
# last_intent_review: 2026-10-03
"""Guard conditional method ownership; passing prose checks is not host efficacy."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
MAINTAINER = "skills/cycle/references/maintainer.md"
VAULT = "skills/capture/references/vault.md"
REPORTS = "skills/capture/references/reports.md"
CUSTOMER = "skills/ship/references/customer-delivery.md"
HISTORY = ".claude/memory/working-state-history-2026-10-03.md"


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def section(text, heading):
    """Select one named section; exclude headings inside fenced examples."""
    lines = text.splitlines()
    starts = [n for n, line in enumerate(lines) if line == heading]
    if len(starts) != 1:
        raise AssertionError(f"expected one {heading!r}, got {len(starts)}")
    start = starts[0]
    level = len(heading) - len(heading.lstrip("#"))
    fence = None
    for end in range(start + 1, len(lines)):
        line = lines[end]
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence:
            if re.fullmatch(rf" {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}[ \t]*", line):
                fence = None
        elif marker:
            fence = marker[1]
        elif re.match(rf"^#{{1,{level}}} ", line):
            return "\n".join(lines[start:end])
    return "\n".join(lines[start:])


class CoreBoundaryMethods(unittest.TestCase):
    def test_actual_vault_scan_recipe_never_promotes_failed_scans_to_export(self):
        base = Path(tempfile.mkdtemp(prefix="vault-scan-status-"))
        source = base / "trusted"
        helper = source / "hooks/shared/_patterns.sh"
        helper.parent.mkdir(parents=True)
        helper.write_text(
            '[ "${LOAD_FAIL:-0}" = 0 ] || return 2\n'
            'scan_secrets() { [ "$2" = "$EXPECTED_NOTE_BODY" ] || return 2; '
            'printf "%s" "${SECRET_HITS:-}"; return "${SECRET_RC:-0}"; }\n'
            'if [ "${MISSING_CUSTOMER:-0}" = 0 ]; then\n'
            '  scan_customer() { [ "$1" = "$EXPECTED_NOTE_BODY" ] || return 2; '
            'printf "%s" "${CUSTOMER_HITS:-}"; return "${CUSTOMER_RC:-0}"; }\n'
            'fi\n', encoding="utf-8",
        )
        note = base / "note.md"
        note.write_bytes(b"Synthetic fixture note.\n")
        dash_note = base / "-"
        dash_note.write_bytes(note.read_bytes())
        method = read(VAULT).split("**MANDATORY pre-write scan", 1)[1]
        recipe = re.search(r"```bash\n(.*?)\n```", method, re.S).group(1)
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(bash)
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("LINTEL_", "CLAUDE_", "BASH_FUNC_"))
               and key not in ("BASH_ENV", "ENV", "CDPATH")}
        env.update(LINTEL_SOURCE_ROOT=source.as_posix(), rendered_note=note.as_posix(),
                   EXPECTED_NOTE_BODY="Synthetic fixture note.")
        prefix = 'set -euo pipefail\naudit_log() { printf "AUDIT %s\\n" "$*"; }\n'
        cases = (
            ({"LOAD_FAIL": "1"}, False),
            ({"LINTEL_SOURCE_ROOT": ""}, False),
            ({"rendered_note": str(base / "absent.md")}, False),
            ({"MISSING_CUSTOMER": "1"}, False),
            ({"SECRET_RC": "2"}, False),
            ({"CUSTOMER_RC": "2"}, False),
            ({"SECRET_HITS": "fixture-pattern-label"}, False),
            ({"CUSTOMER_HITS": "fixture-pattern-label"}, False),
            ({}, True),
            ({"rendered_note": "-"}, True),
        )
        for overrides, ready in cases:
            with self.subTest(overrides=overrides):
                result = subprocess.run(
                    [bash, "-c", prefix + recipe +
                     '\nIFS= read -r remaining\nprintf "stdin_after=%s\\n" "$remaining"\n'
                     'printf "CAPTURE_CONTINUES\\n"\n'],
                    cwd=base, env={**env, **overrides}, capture_output=True,
                    input="bystander input\n", text=True, encoding="utf-8",
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"vault_scan_ready={str(ready).lower()}", result.stdout)
                self.assertIn("CAPTURE_CONTINUES", result.stdout)
                self.assertIn("stdin_after=bystander input", result.stdout)
                self.assertNotIn("AUDIT capture vault_sink_written", result.stdout)
                if not ready:
                    self.assertIn("WARN", result.stderr)
                    self.assertIn("vault_sink_skipped", result.stdout)
                self.assertEqual(note.read_text(encoding="utf-8"), "Synthetic fixture note.\n")
                self.assertEqual(dash_note.read_bytes(), b"Synthetic fixture note.\n")

    def require(self, text, *parts):
        for part in parts:
            self.assertIn(" ".join(part.split()), " ".join(text.split()))

    def link(self, caller, target):
        self.assertIn(f"]({target})", read(caller))
        path = (ROOT / caller).parent / target.split("#")[0]
        self.assertTrue(path.is_file(), (caller, target))
        return path.read_text(encoding="utf-8")

    def test_a06_maintainer_has_one_conditional_owner(self):
        cycle = read("skills/cycle/SKILL.md")
        method = self.link("skills/cycle/SKILL.md", "references/maintainer.md")
        self.require(cycle, "meta-infra", "only", "M1–M4", "required")
        self.require(method, "modifying Lintel itself", "SENSE Step 0c", "operator",
                     "not a new opt-in", "existing phase boundaries")
        self.assertNotIn("**M1 — Structure-impact assessment**", cycle)
        for gate in ("M1 — Structure-impact assessment", "M2 — Compatibility audit",
                     "M3 — Shape-tests", "M4 — Future-operator clarity"):
            self.assertEqual(method.count(f"**{gate}**"), 1)

    def test_a06_maintainer_preserves_required_steps_fields_and_failures(self):
        method = read(MAINTAINER)
        self.require(method, "(in DEFINE)", "(in REVIEW)", "(in CAPTURE)",
                     "backward-compat", "migration path", "forward-compat", "verification",
                     "rollback", ".claude/engineering/evolution/_TEMPLATE.md",
                     "bin/li-compat-audit", "GREEN/YELLOW/RED",
                     "REQUIRED_SKILL_FIELDS", "REQUIRED_AGENT_FIELDS",
                     "renamed or moved", "defaults", "signature", "lib/*.sh",
                     ".claude/engineering/compat-audits/<date>-<slug>.md",
                     "RED requires explicit override",
                     "bash tests/runner/run-all.sh --shape-only", "Any FAIL blocks SHIP",
                     "docs/migrations/_INDEX.md")
        cycle = read("skills/cycle/SKILL.md")
        self.require(cycle, "cap_soft: 600k", "cap_hard: 900k",
                     "gates_active: [M1_structure_impact, M2_compatibility_audit, M3_shape_tests, M4_future_operator_clarity]",
                     "detection: auto-detected by SENSE Step 0c", "operator can override")

    def test_a06_swarm_m4_is_conditional_without_weakening_swarm_evidence(self):
        capture = read("skills/capture/SKILL.md")
        method = self.link("skills/capture/SKILL.md", "../cycle/references/maintainer.md#m4-swarm-recap")
        self.require(capture, "Reaffirm swarm evidence", "Only the coordinator",
                     "final integrated REVIEW", "SHIP evidence", "mode=meta-infra")
        self.require(method, "native", "sequenced", "none", "concurrently",
                     "isolation/attribution", "deterministic integration order",
                     "lost attempts", "unverified host behavior", "same identity")
        self.assertNotIn("- the explicit opt-in fields and coordination path;", capture)

    def test_a06_capture_report_only_entry_retains_flags_and_no_mutation(self):
        capture = read("skills/capture/SKILL.md")
        self.require(capture, "--retrospective", "--release-summary", "--since <ref|time>",
                     "--until <ref|time>", "--scope <session|day|week>", "--scope <area>",
                     "--emit-lessons", "--include-stats", "--voice <internal|customer>",
                     "--out <owned-path>", "Return after the selected report",
                     "Report-only", "only the specifically authorized lessons")
        self.link("skills/capture/SKILL.md", "references/reports.md#step-8--retrospective---retrospective")
        self.link("skills/capture/SKILL.md", "references/reports.md#step-8b--release-report---release-summary")
        self.assertNotIn("Gather only signals relevant", capture)
        self.assertNotIn("Gather commit subjects", capture)

    def test_a06_vault_loading_keeps_default_off_and_separate_authority(self):
        capture = read("skills/capture/SKILL.md")
        self.link("skills/capture/SKILL.md", "references/vault.md")
        step = section(capture, "### Step 7b — Vault sink (session summary → knowledge vault)")
        self.require(step, "capture.vault_sink_enabled", "`true`", "Only", "do not load",
                     "authorized", "NEVER blocking")
        self.assertNotIn("sink_enabled=$(resolve_pack_field", capture)
        self.assertNotIn("created: YYYY-MM-DD", capture)

    def test_a06_vault_keeps_fresh_shell_root_and_audit_fix(self):
        vault = read(VAULT)
        self.require(vault, 'source_root="${LINTEL_SOURCE_ROOT:?select trusted source}"',
                     'source "$source_root/lib/pack-resolver.sh"',
                     'sink_enabled=$(resolve_pack_field capture.vault_sink_enabled)',
                     '[ "$sink_enabled" != "true" ]',
                     'disabled — no destination lookup or write',
                     '${LINTEL_REPO_ROOT:-}', 'source "$source_root/bin/_audit.sh"',
                     'capture_repo="$(lintel_repo_root)"', 'sink_dir="$capture_repo/$sink_path"',
                     "vault_sink_skipped", "reason=path_missing")
        self.assertNotIn('sink_dir="$REPO_ROOT/', vault)
        self.assertLess(vault.index('[ "$sink_enabled" != "true" ]'),
                        vault.index("sink_path=$(resolve_pack_field capture.vault_sink_path)"))

    def test_a06_vault_retains_schema_navigation_and_sensitive_data_boundary(self):
        vault = read(VAULT)
        self.require(vault, "exactly ONE file per session", "destination is already authorized",
                     "Do not create a destination", "created: YYYY-MM-DD", "tags: [session]",
                     "type: session", "repo: <repo-name>", "branch: <git-branch>",
                     "outcome: shipped | in-progress | blocked | exploration",
                     "session: <cycle-id-if-available>", "LOCKED flat schema",
                     "## What was done", "## Decisions", "## Open threads", "## Pointers", "## Links",
                     "Never overwrite an existing hub", "00-index.md", "truncate to 15",
                     "Keep frontmatter + intro intact", "one sanctioned vault read",
                     "working language", "scan_secrets all", "scan_customer",
                     "do NOT sanitize-and-ship", "vault_export_skip sensitive_content",
                     "vault_sink_written")

    def test_a06_reports_preserve_window_observation_and_delivery_rules(self):
        reports = read(REPORTS)
        self.require(reports, "Explicit `--since` wins", "prior 24 hours", "seven days",
                     "latest", "owned checkpoint", "labelled 24-hour fallback",
                     "context_latest", "context_checkpoint", "audit_read_files <category>",
                     "bin/li-events.py", "usage-*.jsonl", "state_cycle_segment",
                     "check=performed|not_performed", "absence is unobserved",
                     "no release, tag, commit, publication or approval",
                     "git rev-parse --verify --end-of-options", "seven-day window",
                     "literal path scope",
                     "No automatic network query", "DRAFT", "Missing corpus is uncalibrated",
                     "usage_provenance: observed | estimated | unknown",
                     "what_worked:", "what_friction:", "next_time:")

    def test_a06_changelog_compatibility_anchor_routes_without_reentering_capture(self):
        caller = read("skills/capture/SKILL.md")
        anchor = section(caller, "#### Keep a Changelog output")
        self.require(anchor, "references/reports.md#keep-a-changelog-output", "current context",
                     "not", "other CAPTURE")
        method = self.link("skills/capture/SKILL.md", "references/reports.md#keep-a-changelog-output")
        self.assertEqual(caller.count("#### Keep a Changelog output"), 1)
        self.assertNotIn("1. **Detect format.**", caller)
        self.require(method, "1. **Detect format.**", "6. **Propose or persist the scoped entry.**",
                     "hand-authored", "`!`", "explicit deprecation", "reverted",
                     "do not dispatch", "only when authorized")
        self.require(read("agents/engineering/ChangelogMaintainer.md"),
                     "../../skills/capture/SKILL.md#keep-a-changelog-output")
        self.require(read("skills/ship/SKILL.md"), "../capture/SKILL.md#keep-a-changelog-output")

    def customer_contract(self, method):
        self.require(method, "actual requested outcome", "selected applicable profile",
                     "available authorized", "selection metadata", "not permission",
                     "--list-selections", "--selection=", "customer-communication",
                     "agreed plan", "no agreed timing", "unagreed", "do not invent",
                     "independent review", "does not send", "owned")
        self.assertNotRegex(method, r"immediate\s*/\s*48hr\s*/\s*weekly")

    def test_f01_customer_method_uses_requested_outcome_profile_and_real_capability(self):
        method = self.link("skills/ship/SKILL.md", "references/customer-delivery.md")
        self.customer_contract(method)
        ship = read("skills/ship/SKILL.md")
        self.assertNotIn("CustomerEmpathyCheck", ship)
        self.assertNotIn("PostDemoFollowup", ship)
        self.assertNotIn("empathy_brief=$(mktemp)", ship)
        self.assertNotIn("followup_brief=$(mktemp)", ship)
        self.require(ship, "actual requested outcome", "selected applicable profile",
                     "do not load", "No customer request")

    def test_f01_missing_guard_mutations_are_rejected(self):
        method = " ".join(read(CUSTOMER).split())
        self.customer_contract(method)
        for part in ("actual requested outcome", "selected applicable profile", "not permission",
                     "available authorized", "agreed plan", "does not send"):
            with self.subTest(removed=part), self.assertRaises(AssertionError):
                self.customer_contract(method.replace(part, "[removed]"))

    def test_f01_customer_methods_retain_distinctive_capabilities_and_fields(self):
        method = read(CUSTOMER)
        self.require(method, "PPTNarrativeArchitect", "5-beat slide arc", "<name>.pptx",
                     "WordTechnicalEditor", "technical / customer-summary / transparency-note",
                     "WebExperienceCritic", "single-file HTML OR Next.js scaffold",
                     "DemoNarrativeArc", "DemoNarratorJunior", "CustomerEmpathyCheck",
                     "PostDemoFollowup", "ExecutiveBriefingDrafter", "ProposalDrafter",
                     "RFPResponseDrafter", "EmailCustomerDrafter", "BlogPostDrafter",
                     "LinkedInPostDrafter", "task:", "context_pointers:", "constraints:",
                     "acceptance:", "per-passage empathy verdict", "specific rewrite recommendations",
                     "questions asked", "follow-up requests", "decision-maker presence",
                     "30-day", "PoC", "workshop", "preserve substance")

    def test_f01_generation_and_publication_keep_all_existing_gates(self):
        ship = read("skills/ship/SKILL.md")
        method = read(CUSTOMER)
        self.require(ship, "li-review-evidence.py ship", "exact accepted `qa_requirements`",
                     "same context", "independent corroboration", "never `--repair` after review",
                     "../build/references/documentation-fidelity.md",
                     "mandatory fail/error/unverified", "publication permission")
        self.require(method, "voice.gates_active", "brand.templates", "Honest-limitations",
                     "Provenance", "mandatory", "advisory", "read-only QA",
                     "current claim-to-source", "newly verified context")

    def visio_contract(self, text):
        self.require(text, "no bundled writer", "actual requested format",
                     "available authorized writer", "editable reopen", "connectors", "labels",
                     "required inspection", "No image-as-VSDX", "does not install",
                     "Missing writer/editor operations", "blocks only that output",
                     "QA handoff is not", "staged template slot")
        self.assertNotRegex(text, r"python-vsdx|libvsx|~/\.lintel/brand/visio-templates")
        self.assertNotIn("AI generates fresh per invocation", text)
        self.assertNotRegex(text, r"\*\*DONE\*\*.*qa-handoff successful")

    def test_d02_visio_preflight_replaces_invention_without_promoting_stage(self):
        text = read("skills/generate-visio/SKILL.md")
        self.visio_contract(text)
        self.require(text, "name: generate-visio", "--from-pipeline <run-dir>",
                     "--output-format <vsdx|svg|png|drawio>", "--customer-share",
                     "no curated generation workflow is supplied",
                     "SystemArchitect", "SecurityAuditor", "mandatory pattern clause")
        self.assertNotIn("When to promote from slot to curated", text)

    def test_d02_missing_writer_format_and_inspection_guards_are_discriminating(self):
        text = " ".join(read("skills/generate-visio/SKILL.md").split())
        self.visio_contract(text)
        for part in ("no bundled writer", "actual requested format", "available authorized writer",
                     "editable reopen", "connectors", "labels", "required inspection",
                     "No image-as-VSDX", "QA handoff is not"):
            with self.subTest(removed=part), self.assertRaises(AssertionError):
                self.visio_contract(text.replace(part, "[removed]"))

    def test_d02_requested_format_is_not_silently_replaced_by_preview_or_suffix(self):
        text = read("skills/generate-visio/SKILL.md")
        self.require(text, "NEEDS_CONTEXT", "file extension", "SVG or PNG", "explicitly requested",
                     "native shapes", "endpoint", "read back", "owned copy", "save",
                     "same artifact", "DONE_WITH_CONCERNS", "mandatory")
        self.require(read("skills/generate/SKILL.md"), "no image-as-VSDX substitution",
                     "A missing required operation", "--auto-fix none")
        self.assertNotIn("`visio`", read("skills/generate/scripts/pipeline_inputs.py"))

    def test_d02_presence_guard_checks_behavior_not_empty_template_marker(self):
        guard = read("tests/unit/generate-skills-present.sh")
        self.assertNotIn("missing TEMPLATE ONLY marker", guard)
        self.require(guard, "no bundled writer", "editable reopen", "connectors", "labels",
                     "required inspection", "QA handoff is not")
        self.assertNotIn("pre-baking content violates L-001", guard)

    def test_ent05_hot_state_is_short_current_and_history_is_cold(self):
        state = read(".claude/memory/working-state.md")
        index = read(".claude/memory/MEMORY.md")
        self.assertLessEqual(len(state.splitlines()), 100)
        self.assertLessEqual(len(index.splitlines()), 70)
        self.require(state, "original 84 findings", "Source presence is not proof of review", "f9796bb8",
                     "0.13.7", "working-state-history-2026-10-03.md",
                     "not live instructions", "not measured compounding",
                     "native-hook", "ADR-drafting", "independent")
        self.assertNotIn("Universal implementation ACTIVE", index)
        self.assertNotIn("79/113", index)
        self.require(index, "universal-implementation/reports/final.md", "ADR-0033",
                     "109/109", "native-client-parity/review.md", "retrieval")
        self.require(read(HISTORY), "## Active - Complete original V2 findings (2026-10-03)",
                     "## Historical integration chronology", "## operator-only-remaining")

    def test_ent05_hot_memory_links_stay_local_resolvable_and_do_not_copy_runtime(self):
        for relative in (".claude/memory/MEMORY.md", ".claude/memory/working-state.md"):
            text = read(relative)
            for link in re.findall(r"\]\(([^)]+)\)", text):
                with self.subTest(path=relative, link=link):
                    self.assertNotRegex(link, r"^[a-z]+://|^[A-Za-z]:")
                    destination = (ROOT / relative).parent / link.split("#")[0]
                    self.assertTrue(destination.exists())
            self.assertNotIn(".copilot/session-state", text)
            self.assertNotIn(".claude/runtime/sessions", text)
        self.assertEqual((ROOT / HISTORY).parent, (ROOT / ".claude/memory/working-state.md").parent)

    def test_hot_index_defers_current_v2_status_to_its_working_state_owner(self):
        index = read(".claude/memory/MEMORY.md")
        note = index.split("**Original V2 programme remains open", 1)[1].split(
            "\n- **Universal delivery", 1)[0]
        self.assertIn("working-state.md", note)
        for stale in ("uncommitted WIP", "f9796bb8", "0.13.7"):
            self.assertNotIn(stale, note)

    def test_core_still_preserves_nine_phase_and_independence_boundaries(self):
        cycle = read("skills/cycle/SKILL.md")
        capture = read("skills/capture/SKILL.md")
        self.require(cycle, "SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE",
                     "ordinary sequential BUILD", "No state mutated", "actual permitted host bindings",
                     "dormant under ADR-0008", "workflow_begin", "state_phase_begin")
        self.require(capture, "lesson benefit and recurrence method", "unknown** benefit",
                     "Step 1b", "NOT part of the default", "behavior test", "cycle_complete=false",
                     "Never claim independent review", "selected status", "original tasks")


if __name__ == "__main__":
    unittest.main()
