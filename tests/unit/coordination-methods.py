#!/usr/bin/env python3
# component: coordination-method-regressions
# implements: ADR-0008, ADR-0026, ADR-0029, ADR-0034, ADR-0036
# intent: skills/scope/references/method.md
# constraints: local source/data checks; no models, network, profile binding or cleanup
# last_intent_review: 2026-10-03
"""Actual helper regressions plus documentary guards, not agent-efficacy evidence."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
import envelope_contract as envelope
import profile_context as profile
from native_paths import native_io_path

BASH = os.environ.get("LINTEL_TEST_BASH") or (
    r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt" else shutil.which("bash")
)


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def section(relative, heading):
    text = read(relative).split(heading, 1)[1]
    # These selected method sections use level 2/3 headings. A single '#'
    # inside the actual Bash/YAML examples is not a section delimiter.
    return re.split(r"\n#{2,3} ", text, maxsplit=1)[0]


def bash_block(relative, heading):
    return re.search(r"```bash\n(.*?)\n```", section(relative, heading), re.S)[1]


def hashes(root):
    io_root = native_io_path(root)
    return {p.relative_to(io_root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in io_root.rglob("*") if p.is_file()}


class Sources(unittest.TestCase):
    def test_shared_planning_receiver_and_role_debrief_have_one_current_owner(self):
        shared = read("skills/full-engineering-pass/references/domain-handoff.md")
        self.assertNotIn("ReleaseEngineer gets planning-only", shared)
        self.require(shared, "DeploymentEngineer gets planning-only", "readable history",
                     "not instructions to dispatch new planning")
        debrief = section("skills/capture/SKILL.md", "### Step 7 — Role debrief")
        self.assertNotIn("~/.lintel/roles/private", debrief)
        self.require(debrief, "../role/references/lifecycle.md", "resolved destination",
                     "reviewed digest", "explicit consent", "proposal")

    def test_actual_lesson_lookup_uses_trusted_source_not_target_code(self):
        base = Path(tempfile.mkdtemp(prefix="lookup-source-"))
        target, home = base / "target", base / "home"
        (target / ".claude/memory").mkdir(parents=True)
        home.mkdir()
        (target / ".claude/lintel-layout.yaml").write_text("layout_version: 5\n", encoding="utf-8")
        (target / ".claude/memory/lessons.md").write_text(
            "# Lessons\n\n## L-001 — Fixture source\n**Rule:** fixture lookup remains owned.\n",
            encoding="utf-8",
        )
        (target / "lib").mkdir()
        marker = target / "wrong-helper"
        (target / "lib/memory.sh").write_text(
            'printf wrong > "$LINTEL_REPO_ROOT/wrong-helper"\n', encoding="utf-8",
        )
        update = read("skills/lessons-add/SKILL.md").split("2b. **Update-phase", 1)[1].split(
            "3. **Format", 1)[0]
        recipe = re.search(r"```bash\n(.*?)\n\s*```", update, re.S).group(1)
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("LINTEL_", "CLAUDE_", "BASH_FUNC_"))
               and key not in ("BASH_ENV", "ENV", "CDPATH")}
        env.update(HOME=str(home), USERPROFILE=str(home), LINTEL_HOME=str(home),
                   LINTEL_SOURCE_ROOT=ROOT.as_posix(), LINTEL_REPO_ROOT=target.as_posix(),
                   keywords="fixture")
        result = subprocess.run([BASH, "-c", recipe], cwd=target, env=env,
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("L-001", result.stdout)
        self.assertFalse(marker.exists())
        env.pop("LINTEL_SOURCE_ROOT")
        refused = subprocess.run([BASH, "-c", recipe], cwd=target, env=env,
                                 capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(refused.returncode, 0)
        self.assertFalse(marker.exists())

    def require(self, text, *terms):
        normalized = " ".join(text.split())
        for term in terms:
            self.assertIn(term, normalized)

    def test_scope_and_plan_share_work_based_interpretation(self):
        method = read("skills/scope/references/method.md")
        self.require(method, "owners and interfaces", "uncertainty", "rollback",
                     "two plausible readings", "any", "keyword miss", "existing answers",
                     "flat", "phased", "tree", "2–5 minute", "nine", "dormant")
        scope = read("skills/scope/SKILL.md")
        plan = read("skills/plan/SKILL.md")
        self.assertIn("(references/method.md)", scope)
        self.assertIn("(../scope/references/method.md)", plan)
        self.assertNotIn("**If `scale_amb=no`** (clear): **no question.**", scope)
        self.assertNotIn("default `depth_schema: flat`", plan)
        self.require(scope, "even if the helper said `no`", "without another question")

    def test_plan_has_one_decision_not_two_permission_scripts(self):
        plan = read("skills/plan/SKILL.md")
        signals = section("skills/plan/SKILL.md", "### Step 7 —")
        self.assertNotIn("complete code", plan)
        self.assertNotIn("A) Approve and proceed", signals)
        self.require(signals, "neither measured usage", "Step 10", "dormant", "whole-cycle")
        self.require(plan, "interfaces/contracts", "actual retained authorization",
                     "approval source and scope", "does not replace required review evidence",
                     "one approval decision", "2-5 minutes", "qa_requirements")
        cycle = section("skills/cycle/SKILL.md", "### Step 5 —")
        self.assertNotIn("Proceed with BUILD?", cycle)
        self.require(cycle, "Do not re-present unchanged signals", "never makes, repeats")
        self.require(read("skills/inspect/SKILL.md"), "Granularity hard check", "2-5 minutes")
        self.require(read("skills/build/SKILL.md"), "2–5 minute", "independent review")

    def test_resume_table_does_not_replace_modes_or_evidence(self):
        text = read("skills/resume/SKILL.md")
        self.require(text, "Resume decision table (map first)", "No committed selection",
                     "Several committed initiatives", "baseline unrun", "exact command",
                     "seven days", "LINTEL_SCOPE_PATH", "workflow_resume",
                     "context/generation/digest", "--job", "--from", "--explicit",
                     "context_checkpoint", "context_select", "STARTING/BLOCKED/",
                     "source rollback remains a separate")
        recovery = read("skills/resume/references/state-and-job-recovery.md")
        self.require(recovery, "same card", "Runtime loss cancels attempts",
                     "job_can_start", "blocked_until", "job_resume_point", "1.1.a",
                     "current_step", "shared jobs parent")
        for owner in (text, recovery):
            self.assertNotIn("Test suite passes baseline", owner)
            self.assertNotIn("What's your choice?", owner)
            self.assertNotIn(">30 days", owner)
            self.assertNotIn("ignoring prior state", owner)

    def test_resume_swarm_recovery_uses_its_complete_owned_reference(self):
        main = section("skills/resume/SKILL.md", "#### Swarm-aware committed resume")
        self.assertIn("references/state-and-job-recovery.md#swarm-aware-committed-resume", main)
        self.require(main, "Read", "before", "Runtime loss cancels attempts", "same card")
        self.assertNotIn("```bash", main)
        reference = section("skills/resume/references/state-and-job-recovery.md",
                            "## Swarm-aware committed resume")
        self.require(reference, "Inputs", "Step 1c", "selected_map", "coordination",
                     "LINTEL_SOURCE_ROOT", "CLAUDE_PLUGIN_ROOT", "NEEDS_CONTEXT",
                     "Runtime loss cancels attempts", "check-scope", "same card")
        for forbidden in ("${LINTEL_SOURCE_ROOT:-$repo}", ">30 days",
                          "ignoring prior state", "Test suite passes baseline", "What's your choice?"):
            self.assertNotIn(forbidden, read("skills/resume/SKILL.md"))
            self.assertNotIn(forbidden, read("skills/resume/references/state-and-job-recovery.md"))

    def test_resume_integrity_requires_declared_same_shell_inputs(self):
        main = section("skills/resume/SKILL.md", "### Step 1.5 —")
        self.assertIn("references/state-and-job-recovery.md#ledger-integrity", main)
        self.assertNotIn("```bash", main)
        reference = section("skills/resume/references/state-and-job-recovery.md",
                            "## Ledger integrity")
        self.require(reference, "Inputs from Step 1", "STATE_FILE", "resume_working_repo",
                     "same Bash invocation", "state_cycle_segment", "branch-drift",
                     "commit-unreachable", "staleness (warn if >7 days)", "age-only warning",
                     "An unresolved mismatch blocks")

    def test_resume_job_recovery_uses_the_selected_job_reference(self):
        main = section("skills/resume/SKILL.md", "### Step 2.5 —")
        self.assertIn("references/state-and-job-recovery.md#tree-and-job-resume", main)
        self.assertNotIn("```bash", main)
        reference = section("skills/resume/references/state-and-job-recovery.md",
                            "## Tree and job resume")
        self.require(reference, "Inputs", "JOB_ID", "LINTEL_SCOPE_PATH",
                     "LINTEL_REPO_ROOT", "job_resume_point", "job_can_start",
                     "blocked_until", "current_step", "shared jobs parent",
                     "selected scope is missing or empty", "1.1.a")

    def test_snippet_extractor_never_falls_through_to_another_section(self):
        source = read("tests/integration/enterprise-workflow-snippets.sh")
        function = re.search(r"(?ms)^extract_step\(\) \{\n.*?^\}", source)
        self.assertIsNotNone(function)
        cases = (
            ("### Selected\n\n```bash\n# A shell comment\nprintf selected\n```\n"
             "### Following\n```bash\nprintf wrong\n```\n", True,
             "# A shell comment\nprintf selected\n"),
            ("### Selected\nNo Bash block here.\n\n"
             "### Following\n```bash\nprintf wrong\n```\n", False, ""),
            ("### Unrelated\n```bash\nprintf wrong\n```\n", False, ""),
        )
        with tempfile.TemporaryDirectory(prefix="extract-owner-") as temporary:
            base = Path(temporary)
            for index, (text, passes, expected) in enumerate(cases):
                with self.subTest(case=index):
                    path, output = base / f"case-{index}.md", base / f"case-{index}.sh"
                    path.write_text(text, encoding="utf-8")
                    result = subprocess.run(
                        [BASH, "--noprofile", "--norc", "-c",
                         function[0] + '\nextract_step "$1" "### Selected" "$2"\n',
                         "extractor-fixture", path.as_posix(), output.as_posix()],
                        capture_output=True, text=True, encoding="utf-8", check=False,
                    )
                    if passes:
                        self.assertEqual(result.returncode, 0, result.stderr)
                    else:
                        self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(output.read_text(encoding="utf-8"), expected)

    def test_contract_names_link_to_existing_owners(self):
        reference = read("skills/swarm/references/evidence.md")
        for code in ("P03", "P04", "P05", "P07", "P08", "P09", "A22.7"):
            self.assertIn(f"| {code} |", reference)
        for path in re.findall(r"`((?:lib|bin)/[^`]+)`", reference):
            self.assertTrue((ROOT / path).is_file(), path)
        self.require(reference, "context_id", "generation", "digest", "required_policy",
                     "immutable QA", "corroboration", "not a duplicate pipeline")
        for name in ("swarm", "resume", "brief-forge", "handoff-size-check"):
            text = read(f"skills/{name}/SKILL.md")
            self.assertIn("references/evidence.md", text)
        self.require(read("skills/swarm/SKILL.md"), "## Shared-evidence consumer",
                     "references/evidence.md#shared-evidence-consumer")
        self.require(reference, "verify_profile_reference", "verify_qa",
                     "log-backed `li-review-read`")
        for owner in (read("skills/swarm/SKILL.md"), reference):
            self.assertNotIn("${LINTEL_SOURCE_ROOT:-$repo}", owner)

    def test_swarm_shared_acceptance_has_one_reference_owner(self):
        main = section("skills/swarm/SKILL.md", "## Shared-evidence consumer")
        self.assertIn("references/evidence.md#shared-evidence-consumer", main)
        self.require(main, "Read", "before", "shared acceptance")
        self.assertNotIn("1. Before observations", main)
        reference = read("skills/swarm/references/evidence.md")
        self.assertIn("## Shared-evidence consumer", reference)
        self.assertNotIn("../SKILL.md#shared-evidence-consumer", reference)
        method = section("skills/swarm/references/evidence.md", "## Shared-evidence consumer")
        self.require(method, "work_context", "never `LINTEL_WORK_MAP`",
                     "verify_profile_reference", "required_policy", "verify_qa",
                     "log-backed `li-review-read`", "Later applicable rejection",
                     "Missing/retyped/downgraded obligations", "same non-snapshot fields",
                     "full coordination, charter and brief", "domain_request",
                     "not_evaluated", "Verification-only", "real host/human corroboration",
                     "raw base/HEAD/index/worktree", "Do not alias",
                     "--profile-home", "--profile-packs", "--profile-pointer")
        self.assertNotIn("arguments above", method)
        for owner in (read("skills/swarm/SKILL.md"), reference):
            self.assertNotIn("${LINTEL_SOURCE_ROOT:-$repo}", owner)

    def test_forge_method_does_not_call_diagnostics_measured_quality(self):
        self.require(read("skills/brief-forge/SKILL.md"),
                     "70 with FAIL", "not measured", "fixed", "not graded readiness",
                     "remote pointers", "Structural completeness", "custom evaluators",
                     "testable", "audit receipt", "baseline security check cannot be disabled")

    def test_mars_offer_uses_observed_roster_and_reference_dispatch(self):
        text = read("skills/mars/SKILL.md")
        offer = section("skills/mars/SKILL.md", "## Offer text")
        self.require(offer, "actual", "li-mars.py roster", "missing_families",
                     "eligible", "effort", "context_tier", "downgraded",
                     "selected distinct models", "Silence is")
        self.assertNotRegex(text, r"claude-opus-\d|GPT-\d|Grok \d|Claude Opus \d")
        self.assertNotIn("kickoff.model", text)
        self.require(read("skills/mars/references/integration.md"),
                     "kickoff.model", "assistant_usage_events.model", "actual tools",
                     "no observation means unverified")
        self.require(text, "`xhigh`", "`long_context`", "blind pass",
                     "only if contested", "close-plan", "new consent")

    def test_lesson_methods_share_benefit_recurrence_and_unknown(self):
        method = read("skills/lessons-add/references/benefit.md")
        self.require(method, "Observed benefit", "Recurrence", "Unknown", "dated instance",
                     "causal guess", "no-op", "update", "supersede", "merging",
                     "preserving IDs/history", "No schema", "automatic promotion")
        for name in ("capture", "lessons-add", "lessons-promote"):
            text = read(f"skills/{name}/SKILL.md")
            self.assertIn("references/benefit.md", text)
            self.assertIn("unknown", text.lower())
            self.assertNotIn("frequency-of-reference", text)
        self.require(read("skills/lessons-add/SKILL.md"), "held lock", "exit 9",
                     "Content-safety", "mandatory evidence blocks")

    def test_preference_hints_are_not_schema_and_callers_keep_controls(self):
        for module in ("ta", "da", "sc", "dh", "tq"):
            text = read(f"skills/{module}/SKILL.md")
            self.require(text, "Legacy discovery hint, not a validated pack-schema field",
                         "preferences_root", "references/preferences.md", "validated pack interface",
                         "shared module caller procedure", "full", "loop", "single")
        self.require(read("skills/da/references/preferences.md"), "whole-block inheritance",
                     "not a validated pack interface", "Missing advice remains missing",
                     "data_architecture.migration_glob", "security_compliance.auth_flow_glob",
                     "not typed")

    def test_scaffold_owns_acceptance_and_aliases_only_delegate(self):
        owner = read("skills/scaffold/SKILL.md")
        self.require(owner, "one owner", "principal failure case", "golden and adversarial",
                     "protect approved golden cases", "no-op gates", "no automatic",
                     "never install automatically", "required caller policy",
                     "profile generation", "transaction", "independent")
        for mode, flags in (
            ("internal-tool", ("--name", "--path", "--language", "--type", "--ci")),
            ("mvp", ("--name", "--target-users", "--path", "--stack", "--has-ai", "--deploy")),
        ):
            alias = read(f"skills/scaffold-{mode}/SKILL.md")
            self.require(alias, "Delegate to [scaffold]", f"--mode {mode}",
                         "existing answers" if mode == "mvp" else "existing acceptance answers",
                         "no-install", *flags)
            self.assertIn("application-mode-acceptance-one-owner", alias)
            self.assertNotIn("```bash", alias)
            self.assertNotIn("strict TypeScript", alias)


class Helpers(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="cm-"))
        self.env = os.environ.copy()
        for key in list(self.env):
            if key.startswith("LINTEL_") or key in ("CLAUDE_SESSION_ID", "CYCLE_ID", "PACK_CACHE_FILE"):
                self.env.pop(key)
        for key in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME",
                    "XDG_CACHE_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_RUNTIME_DIR",
                    "TEMP", "TMP", "TMPDIR"):
            directory = self.root / key.lower()
            directory.mkdir()
            self.env[key] = directory.as_posix()
        self.env.update({
            "LINTEL_SOURCE_ROOT": ROOT.as_posix(), "LINTEL_REPO_ROOT": self.root.as_posix(),
            "LINTEL_HOME": (self.root / "home/.lintel").as_posix(),
            "LINTEL_AUDIT_DIR": (self.root / "audit").as_posix(),
            "LINTEL_JOBS_DIR": (self.root / "jobs").as_posix(),
            "LINTEL_JOBS_NO_INIT": "1", "PYTHONDONTWRITEBYTECODE": "1",
            "GIT_PAGER": "cat",
        })

    def command(self, argv, *, expected=0):
        result = subprocess.run(argv, cwd=self.root, env=self.env, input="",
                                text=True, capture_output=True, timeout=90)
        print(json.dumps({"argv": argv, "cwd": str(self.root), "exit": result.returncode,
                          "stdout": result.stdout, "stderr": result.stderr}))
        self.assertEqual(result.returncode, expected, result.stderr)
        return result.stdout

    def bash(self, script, *args, expected=0):
        return self.command([str(BASH), "--noprofile", "--norc", "-c", script, "fixture", *args],
                            expected=expected)

    def put(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_lexical_miss_and_uncalibrated_prior_remain_only_hints(self):
        output = self.bash(
            'source "$LINTEL_SOURCE_ROOT/lib/scale-estimator.sh"; '
            'classify_size "$1"; printf "|"; scale_ambiguous "$1"; printf "|"; '
            'scale_confidence "$1"; printf "|"; scale_escalate "$1" medium; printf "\\n"; '
            'scale_token_estimate XL', "reconcile records")
        self.assertEqual(output, "S|no|high|no\n120000 uncalibrated 0")

    def candidate(self, pointers=()):
        path = self.put("brief.json", json.dumps({
            "content": {"task": "Inspect an inert example",
                        "constraints": ["No execution or dispatch"],
                        "acceptance": ["Report the observed fixture value"]},
            "context_pointers": list(pointers)}))
        return {"head": envelope.head_for("subagent_spawn", "BUILD", "fixture"),
                "body": envelope.body_for("brief", path),
                "tail": {"completeness_score": 100, "evaluators_run": [],
                         "escape_hatches": envelope.escape_hatches("brief", "BUILD"),
                         "audit_pointer": str(self.root / "not-a-receipt.jsonl")}}

    def test_builtin_completeness_is_structural_and_budget_is_fixed(self):
        candidate = self.candidate()
        # Semantically weak but structurally nonempty acceptance still validates.
        candidate["body"]["content"]["acceptance"] = ["Looks fine"]
        result = envelope.evaluator("completeness", candidate, self.root)
        self.assertEqual((result["score"], result["status"], result["budget_used"]), (100, "PASS", 30))
        candidate["body"]["content"]["acceptance"] = []
        failed = envelope.evaluator("completeness", candidate, self.root)
        self.assertEqual((failed["score"], failed["status"], failed["budget_used"]), (0, "FAIL", 30))
        checked = envelope.evaluator("security", {"text": "inert documentation"}, self.root)
        self.assertEqual((checked["score"], checked["budget_used"]), (100, 50))
        print(json.dumps({"completeness": result, "missing_acceptance": failed, "security": checked}))

    def test_one_missing_pointer_is_70_fail_and_cannot_finalize(self):
        candidate = self.candidate(["missing.txt"])
        stale = envelope.evaluator("stale", candidate, self.root)
        self.assertEqual((stale["score"], stale["status"], stale["budget_used"]), (70, "FAIL", 40))
        results = {"security": envelope.evaluator("security", candidate, self.root), "stale": stale}
        with self.assertRaisesRegex(envelope.EnvelopeError, "Evaluator failed"):
            envelope.finalize(candidate, results, 100, self.root)
        self.assertFalse((self.root / "brief-forge.jsonl").exists())
        print(json.dumps({"stale": stale, "release": "refused; no receipt written"}))

    def test_existing_pointer_is_not_freshness_and_remote_is_not_fetched(self):
        self.put("old-notes.txt", "Historical text\n")
        candidate = self.candidate(["old-notes.txt", "https://example.invalid/not-fetched"])
        result = envelope.evaluator("stale", candidate, self.root)
        self.assertEqual((result["score"], result["status"]), (100, "PASS"))
        self.assertIn("remote pointers not checked: 1", result["notes"])
        custom = {"score": 55, "budget_used": 7, "notes": "Trusted fixture diagnostic", "status": "PASS"}
        self.assertEqual(envelope.checked_result(custom), custom)
        with self.assertRaises(envelope.EnvelopeError):
            envelope.checked_result({**custom, "score": "55"})
        print(json.dumps({"stale": result, "custom_protocol": custom}))

    def test_actual_resume_classifier_retains_phase_step_and_literal_path(self):
        script = bash_block("skills/resume/SKILL.md", "### Step 1a —")
        for operand, expected in (("BUILD", "phase"), ("1.1.a", "step"), ("./BUILD", "checkpoint")):
            self.assertEqual(self.bash(script, operand, "1.1.a").strip(), expected)

    def test_actual_tree_recipe_keeps_blocked_leaf_and_flat_fallback(self):
        self.put("jobs/example/job.yaml", """current_step: BUILD
steps:
  - name: 1.1.a
    status: PENDING
    blocked_until: 1.2.a.status == DONE
  - name: 1.2.a
    status: PENDING
""")
        scope = self.put("jobs/example/scope.md", "depth_schema: tree\n")
        self.env["JOB_ID"] = "example"
        script = bash_block("skills/resume/references/state-and-job-recovery.md",
                            "## Tree and job resume")
        before = hashes(self.root / "jobs")
        self.assertEqual(self.bash(script + '\nprintf "%s" "$resume_target"'), "1.2.a")
        self.assertEqual(hashes(self.root / "jobs"), before)
        scope.write_text("depth_schema: flat\n", encoding="utf-8")
        self.assertEqual(self.bash(script + '\nprintf "%s" "$resume_target"'), "BUILD")
        self.assertEqual(self.bash('source "$LINTEL_SOURCE_ROOT/bin/_jobs.sh"; '
                                   'job_can_start example 1.1.a', expected=1).strip(), "no")

    def test_optional_preferences_survive_with_whole_block_inheritance(self):
        parent = {"name": "parent", "version": "1.0.0", "extends": "_default",
                  "engineering": {"data_architecture": {"store": "fixture-parent", "window": "manual"}},
                  "data_architecture": {"migration_glob": "changes/*.sql"}}
        child = {"name": "child", "version": "1.0.0", "extends": "parent",
                 "engineering": {"data_architecture": {"store": "fixture-child"}}}
        self.put("packs/parent/pack.yaml", """name: parent
version: 1.0.0
extends: _default
engineering:
  data_architecture:
    store: fixture-parent
    window: manual
data_architecture:
  migration_glob: changes/*.sql
""")
        self.put("packs/child/pack.yaml", """name: child
version: 1.0.0
extends: parent
engineering:
  data_architecture:
    store: fixture-child
""")
        config = profile.ProfileConfig(ROOT, self.root, self.root / "home",
                                       self.root / "packs", self.root / "absent-pointer",
                                       explicit_pack="child")
        resolved = profile.resolve_profile(config)
        values = resolved["values"]
        self.assertEqual(values["engineering"], child["engineering"])
        self.assertNotIn("window", values["engineering"]["data_architecture"])
        self.assertEqual(values["data_architecture"], parent["data_architecture"])
        self.assertFalse((self.root / ".claude/runtime/profiles").exists())
        print(json.dumps({"optional_values": values["engineering"],
                          "inherited_other_block": values["data_architecture"], "binding": "not performed"}))

    def test_scaffold_modes_preview_actual_helper_and_preserve_target(self):
        # A byte-identical source mirror makes source, target and planned recovery
        # store disjoint inside the test root. No installation or publication runs.
        source = self.root / "source"
        for folder in ("lib", "packs/_default"):
            shutil.copytree(ROOT / folder, native_io_path(source / folder),
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        foundation = (
            "CLAUDE.md.template", "AGENTS.md.template", "CORE-PRINCIPLES.md",
            "SESSION-PROTOCOL.md", "EVOLUTION.md", "EVOLUTION-LOG.md",
            "TEMPLATE-skill.md", "TEMPLATE-agent.md", ".claude/memory/lessons.md",
            ".claude/memory/working-state.md", ".claude/memory/personas.md",
            ".claude/memory/personas-example.md", ".claude/plans/todo.md",
            ".claude/decisions/README.md", ".claude/decisions/TEMPLATE.md",
            ".claude/SUBAGENT-GUIDE.md",
        )
        swarm = ("charter.template.md", "coordination.template.json", "agent-brief.template.md",
                 "agent-report.template.md", "agent-review.template.md")
        resources = [
            "bin/li-scaffold", "bin/li-lifecycle", "bin/li-lifecycle.py",
            "bin/li-snapshot.py", ".claude-plugin/plugin.json",
            *("scaffolding/01-foundation/" + name for name in foundation),
            *("scaffolding/01-foundation/templates/swarm/" + name for name in swarm),
        ]
        for relative in resources:
            destination = native_io_path(source / relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
            self.assertEqual(destination.read_bytes(), (ROOT / relative).read_bytes())
        source_before = hashes(source)
        target = self.root / "target"
        target.mkdir()
        self.put("target/AGENTS.md", "Existing user-owned instructions\n")
        before = hashes(target)
        self.env.update({
            "LINTEL_SOURCE_ROOT": source.as_posix(), "LINTEL_REPO_ROOT": target.as_posix(),
            "LINTEL_PACKS_DIR": (source / "packs").as_posix(),
            "LINTEL_ACTIVE_PACK_FILE": (self.root / "absent-pointer").as_posix(),
        })
        for mode in ("internal-tool", "mvp"):
            output = self.command([str(BASH), "--noprofile", "--norc",
                                   (source / "bin/li-scaffold").as_posix(), "check",
                                   "--target", target.as_posix(), "--name", "fixture", "--mode", mode,
                                   "--no-memory-pointer", "--store", (self.root / "recovery").as_posix()])
            result = json.loads(output)
            self.assertEqual(result["state"], "preview")
            self.assertEqual(result["preferences"]["MODE"], mode)
            self.assertIn("AGENTS.md", result["preserved"])
            self.assertEqual(result["host_activation"], "not performed")
            self.assertIsNone(result["target_profile_reference"])
            self.assertEqual(hashes(target), before)
        self.assertEqual(hashes(source), source_before)
        self.assertFalse((self.root / "recovery").exists())


if __name__ == "__main__":
    print("Source-contract and inert helper checks only; no model efficacy or independent review.", flush=True)
    unittest.main(verbosity=2)
