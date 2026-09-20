#!/usr/bin/env python3
# component: universal-trusted-tools-fixtures
# implements: ADR-0005, ADR-0007, ADR-0008
# intent: .claude/plans/universal-implementation/packages/P01.md
# constraints: no personal state, network, hook registration or real CLI updates
# last_intent_review: 2026-09-20
"""Behavioral acceptance for P01, including hostile target code and preserved policy."""

from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
BASH = str(Path(sys.argv.pop(1)).resolve())
GIT = shutil.which("git")
HOOKS = {
    "da-migration-irreversible-warn": "data_architecture.migration_glob",
    "dh-cost-budget-warn": "devops_hosting.iac_glob",
    "dh-deploy-without-rollback-warn": "devops_hosting.deploy_path_glob",
    "dh-observability-gap-warn": "devops_hosting.service_entry_glob",
    "sc-auth-bypass-warn": "security_compliance.auth_flow_glob",
    "sc-compliance-gap-warn": "security_compliance.regulated_path_glob",
    "sc-threat-coverage-warn": "security_compliance.threat_surface_glob",
    "ta-contract-collision-warn": "tech_architecture.interface_glob",
    "tq-contract-break-warn": "testing_qa.provider_glob",
    "tq-perf-regression-warn": "testing_qa.perf_path_glob",
}
CUSTOM_PATH = "custom/change.txt"
RISK_CONTENT = "DROP TABLE fixture_records;\nreplicas: 8\nskipAuth = true\n"
HOSTILE_RESOLVER = """\
printf 'target code executed\\n' > "$LINTEL_REPO_ROOT/target-resolver-ran"
resolve_pack_field() { printf ''; }
"""
UPDATE_STUB = """\
#!/usr/bin/env bash
set -eu
tool="${0##*/}"
printf '%s\\t%s\\t%s\\n' "$tool" "$PWD" "$*" >> "$STUB_LOG"
case "$tool:$*" in
  "git:fetch -q origin") exit "${FETCH_STATUS:-0}" ;;
  "git:pull --ff-only -q") exit "${PULL_STATUS:-0}" ;;
  "gemini:extensions list")
    printf '%s\\n' "${GEMINI_LIST_TEXT:-li}"
    exit "${GEMINI_LIST_STATUS:-0}" ;;
  "copilot:plugin list")
    printf '%s\\n' "${COPILOT_LIST_TEXT:-li}"
    exit "${COPILOT_LIST_STATUS:-0}" ;;
  "droid:plugin list")
    printf '%s\\n' "${DROID_LIST_TEXT:-li}"
    exit "${DROID_LIST_STATUS:-0}" ;;
  "gemini:extensions update li") exit "${GEMINI_STATUS:-0}" ;;
  "copilot:plugin update li@jokerman-lintel") exit "${COPILOT_STATUS:-0}" ;;
  "copilot:plugin install li@jokerman-lintel --force")
    [ "${INSTALL_STATUS:-0}" = 0 ] || exit "$INSTALL_STATUS"
    printf 'installed\\n' > "$STUB_INSTALL_MARKER" ;;
  "droid:plugin update li") exit "${DROID_STATUS:-0}" ;;
  *) printf 'ERROR: unexpected stub invocation: %s %s\\n' "$tool" "$*" >&2; exit 99 ;;
esac
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def snapshot(path: Path) -> dict[str, bytes]:
    return {
        str(item.relative_to(path)): item.read_bytes()
        for item in path.rglob("*")
        if item.is_file()
    }


class Fixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="lintel-p01-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "trusted source"
        self.target = self.base / "target project"
        self.home = self.base / "synthetic home"
        self.lintel_home = self.home / ".lintel"
        self.marker = self.target / "target-resolver-ran"
        self.vault = self.base / "synthetic vault" / "sessions"
        for path in (self.target, self.lintel_home, self.vault):
            path.mkdir(parents=True)
        self.env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith(("LINTEL_", "CLAUDE_", "COPILOT_", "GIT_", "BASH_FUNC_"))
            and key not in ("BASH_ENV", "ENV", "CDPATH")
        }
        self.env.update(
            HOME=self.home.as_posix(),
            USERPROFILE=self.home.as_posix(),
            XDG_CONFIG_HOME=(self.home / ".config").as_posix(),
            LINTEL_HOME=self.lintel_home.as_posix(),
            LINTEL_REPO_ROOT=self.target.as_posix(),
            LINTEL_AUDIT_DIR=(self.base / "audit").as_posix(),
            LINTEL_OPERATOR="synthetic-fixture",
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=(self.home / "empty.gitconfig").as_posix(),
            GIT_CONFIG_COUNT="2",
            GIT_CONFIG_KEY_0="core.hooksPath",
            GIT_CONFIG_VALUE_0=(self.home / "no-hooks").as_posix(),
            GIT_CONFIG_KEY_1="commit.gpgsign",
            GIT_CONFIG_VALUE_1="false",
            GIT_TERMINAL_PROMPT="0",
            GIT_AUTHOR_NAME="Lintel fixture",
            GIT_AUTHOR_EMAIL="fixture@example.invalid",
            GIT_COMMITTER_NAME="Lintel fixture",
            GIT_COMMITTER_EMAIL="fixture@example.invalid",
        )
        write(self.home / "empty.gitconfig", "")
        (self.home / "no-hooks").mkdir()
        self.copy_source()
        self.git("init", "-q", ".")
        self.git("commit", "--allow-empty", "-q", "-m", "fixture baseline")
        write(self.target / ".claude/lintel-layout.yaml", "layout_version: 5\n")
        write(self.target / "lib/pack-resolver.sh", HOSTILE_RESOLVER)
        write(self.target / CUSTOM_PATH, RISK_CONTENT)
        write(self.lintel_home / "packs/active-pack", "fixture\n")
        self.set_policy(CUSTOM_PATH)
        self.sequence = 0

    def copy_source(self) -> None:
        paths = [
            "bin/_audit.sh",
            "bin/li-adr-new",
            "bin/li-update",
            "bin/li-vault-init",
            "lib/pack-resolver.sh",
            "lib/paths.sh",
            "packs/_default/pack.yaml",
            "templates/obsidian/sessions.base",
            "hooks/shared/_input.sh",
            "hooks/hooks.json",
        ]
        paths.extend(f"hooks/shared/{hook}/run.sh" for hook in HOOKS)
        for relative in paths:
            dest = self.source / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, dest)

    def set_policy(
        self, pattern: str, *, installed: bool = False, vault_path: str | None = None
    ) -> None:
        lines = [
            "name: fixture",
            "version: 1.0.0",
            "voice: {default_tier: internal}",
            "compliance: {mode: advisory}",
            "navigation: {default_workflow: cycle}",
        ]
        sections: dict[str, list[str]] = {}
        for field in HOOKS.values():
            section, key = field.split(".")
            sections.setdefault(section, []).append(f"  {key}: '{pattern}'")
        for section, fields in sections.items():
            lines.extend([f"{section}:", *fields])
        lines.extend(
            [
                "capture:",
                "  vault_sink_enabled: true",
                f"  vault_sink_path: '{vault_path or '../synthetic vault/sessions'}'",
            ]
        )
        root = self.lintel_home if installed else self.target
        write(root / "packs/fixture/pack.yaml", "\n".join(lines) + "\n")

    def install_resolver_fallback(self) -> None:
        (self.source / "lib/pack-resolver.sh").unlink()
        for relative in ("lib/pack-resolver.sh", "lib/paths.sh", "bin/_audit.sh",
                         "packs/_default/pack.yaml"):
            dest = self.lintel_home / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, dest)

    def git(self, *args: str) -> str:
        if not GIT:
            self.fail("git is required; no acceptance checks may be skipped")
        result = subprocess.run(
            [GIT, *args], cwd=self.target, env=self.env, capture_output=True,
            text=True, encoding="utf-8", timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def bash(
        self, script: Path | str, *args: str, cwd: Path | None = None,
        extra: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        self.sequence += 1
        env = dict(self.env, LINTEL_SESSION_ID=f"fixture-{self.sequence}")
        env.update(extra or {})
        script_arg = script.as_posix() if isinstance(script, Path) else script
        return subprocess.run(
            [BASH, "--noprofile", "--norc", script_arg, *args],
            cwd=cwd or self.target, env=env, input="", capture_output=True,
            text=True, encoding="utf-8", timeout=120,
        )

    def hook(self, hook: str, file: str = CUSTOM_PATH) -> str:
        if self.marker.exists():
            self.marker.unlink()
        result = self.bash(self.source / f"hooks/shared/{hook}/run.sh", file)
        self.assertFalse(self.marker.exists(), f"{hook} executed target resolver code")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout


class TrustedHooks(Fixture):
    def test_hostile_target_is_never_executed_by_any_resolver_caller(self) -> None:
        for hook in HOOKS:
            with self.subTest(hook=hook):
                self.assertIn(f"WARN [Lintel hook {hook}]", self.hook(hook))

    def test_target_policy_is_data_and_changes_each_domain_decision(self) -> None:
        (self.target / "lib/pack-resolver.sh").unlink()
        for hook in HOOKS:
            for selected in (False, True):
                with self.subTest(hook=hook, selected=selected):
                    self.set_policy(CUSTOM_PATH if selected else "unselected/*")
                    output = self.hook(hook)
                    self.assertEqual("WARN [Lintel hook" in output, selected, output)

    def test_trusted_home_fallback_keeps_installed_pack_precedence(self) -> None:
        self.install_resolver_fallback()
        self.set_policy("unselected/*")
        self.set_policy(CUSTOM_PATH, installed=True)
        for hook in HOOKS:
            with self.subTest(hook=hook):
                self.assertIn(f"WARN [Lintel hook {hook}]", self.hook(hook))

    def test_own_resolver_precedes_home_and_stale_source_environment(self) -> None:
        write(self.lintel_home / "lib/pack-resolver.sh", HOSTILE_RESOLVER)
        write(self.target / "bin/_audit.sh", HOSTILE_RESOLVER)
        self.env["LINTEL_SOURCE_ROOT"] = self.target.as_posix()
        for hook in HOOKS:
            with self.subTest(hook=hook):
                self.assertIn(f"WARN [Lintel hook {hook}]", self.hook(hook))

    def test_missing_trusted_resolver_preserves_heuristics_and_budget_data(self) -> None:
        (self.source / "lib/pack-resolver.sh").unlink()
        defaults = {
            "da-migration-irreversible-warn": "db/migrations/change.sql",
            "dh-cost-budget-warn": "infra/change.tf",
            "dh-deploy-without-rollback-warn": "infra/change.tf",
            "dh-observability-gap-warn": "src/api/change.ts",
            "sc-auth-bypass-warn": "src/login.ts",
            "sc-compliance-gap-warn": "src/payment.ts",
            "sc-threat-coverage-warn": "src/api/change.ts",
            "ta-contract-collision-warn": "schema/change.proto",
            "tq-contract-break-warn": "src/api/change.ts",
            "tq-perf-regression-warn": CUSTOM_PATH,
        }
        write(
            self.target / ".claude/runtime/state/tq/perf-budget-fixture.md",
            f"journey: checkout\npath: {CUSTOM_PATH}\np95_ms: 120\n",
        )
        for hook, file in defaults.items():
            with self.subTest(hook=hook):
                write(self.target / file, RISK_CONTENT)
                output = self.hook(hook, file)
                self.assertIn(f"WARN [Lintel hook {hook}]", output)
                if hook == "tq-perf-regression-warn":
                    self.assertIn("journey: checkout", output)
                    self.assertIn("p95 budget 120ms", output)

    def test_existing_remediation_and_evidence_still_suppress_warnings(self) -> None:
        remediation = {
            "da-migration-irreversible-warn": "DROP TABLE fixture_records;\n-- down\n",
            "dh-cost-budget-warn": "replicas: 2\n",
            "dh-deploy-without-rollback-warn": "# rollback: previous fixture\n",
            "dh-observability-gap-warn": "logger.info('fixture');\n",
            "sc-auth-bypass-warn": "skipAuth = false\n",
        }
        for hook, content in remediation.items():
            with self.subTest(hook=hook):
                write(self.target / CUSTOM_PATH, content)
                self.assertNotIn("WARN [Lintel hook", self.hook(hook))
        write(self.target / CUSTOM_PATH, RISK_CONTENT)
        for framework in ("soc2", "gdpr"):
            write(
                self.target / f".claude/runtime/state/sc/compliance-evidence-{framework}.md",
                "verdict: pass\n",
            )
        self.assertNotIn("WARN [Lintel hook", self.hook("sc-compliance-gap-warn"))
        write(
            self.target / ".claude/runtime/state/sc/threat-model-fixture.md",
            f"Covered path: {CUSTOM_PATH}\n",
        )
        self.assertNotIn("WARN [Lintel hook", self.hook("sc-threat-coverage-warn"))
        write(self.target / "tests/contract-fixture.ts", "// synthetic contract test\n")
        self.git("add", "tests/contract-fixture.ts")
        self.assertNotIn("WARN [Lintel hook", self.hook("tq-contract-break-warn"))

    def test_consumer_registry_still_warns_outside_the_pack_glob(self) -> None:
        self.set_policy("unselected/*")
        write(
            self.target / ".claude/runtime/state/ta/consumer-registry.json",
            '[\n{"interface":"custom/change.txt","consumer":"one"},\n'
            '{"interface":"custom/change.txt","consumer":"two"}\n]\n',
        )
        self.assertIn("2 consumer(s)", self.hook("ta-contract-collision-warn"))

    def test_performance_glob_without_optional_budget_metadata_warns(self) -> None:
        output = self.hook("tq-perf-regression-warn")
        self.assertIn("perf-budget-bound path", output)
        self.assertNotIn("p95 budget", output)

    def test_performance_metadata_absence_and_presence_are_distinct(self) -> None:
        budget = self.target / ".claude/runtime/state/tq/perf-budget-fixture.md"
        for content, suffix in (
            ("Unrelated budget notes.\n", ""),
            (f"path: {CUSTOM_PATH}\n", ""),
            (f"journey: checkout\npath: {CUSTOM_PATH}\np95_ms: 120\n",
             " (journey: checkout), p95 budget 120ms"),
        ):
            with self.subTest(content=content):
                write(budget, content)
                output = self.hook("tq-perf-regression-warn")
                self.assertIn(f"WARN: perf-budget-bound path{suffix}\n", output)

    def test_invalid_present_performance_metadata_is_an_explicit_error(self) -> None:
        write(
            self.target / ".claude/runtime/state/tq/perf-budget-fixture.md",
            f"journey: checkout\npath: {CUSTOM_PATH}\np95_ms: invalid\n",
        )
        result = self.bash(self.source / "hooks/shared/tq-perf-regression-warn/run.sh",
                           CUSTOM_PATH)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("invalid p95_ms budget metadata", result.stderr)
        self.assertNotIn("WARN: perf-budget-bound path", result.stdout)
        self.assertFalse(self.marker.exists())

    def test_performance_metadata_read_failure_is_not_empty_success(self) -> None:
        budget = self.target / ".claude/runtime/state/tq/perf-budget-fixture.md"
        write(budget, f"path: {CUSTOM_PATH}\np95_ms: 120\n")
        real_grep = shutil.which("grep", path=str(Path(BASH).parent)) or shutil.which("grep")
        self.assertIsNotNone(real_grep, "grep is required; no checks may be skipped")
        stub = self.base / "read failure commands" / "grep"
        write(
            stub,
            '#!/usr/bin/env bash\n'
            'if [ "${1:-}" = "-B1" ]; then\n'
            '  echo "synthetic metadata read failure" >&2; exit 2\n'
            'fi\n'
            'exec "$REAL_GREP" "$@"\n',
        )
        stub.chmod(0o755)
        result = self.bash(
            self.source / "hooks/shared/tq-perf-regression-warn/run.sh", CUSTOM_PATH,
            extra={
                "PATH": str(stub.parent) + os.pathsep + self.env["PATH"],
                "REAL_GREP": Path(real_grep).as_posix(),
            },
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("cannot read budget metadata", result.stderr)
        self.assertNotIn("WARN: perf-budget-bound path", result.stdout)
        self.assertFalse(self.marker.exists())

    def test_registration_is_unchanged_and_domain_hooks_remain_dormant(self) -> None:
        registration = ROOT / "hooks/hooks.json"
        before = registration.read_bytes()
        commands = json.dumps(json.loads(before))
        for hook in HOOKS:
            self.assertNotIn(f"hooks/shared/{hook}/run.sh", commands)
            self.hook(hook)
        self.assertEqual(registration.read_bytes(), before)
        self.assertEqual((self.source / "hooks/hooks.json").read_bytes(), before)


class Vault(Fixture):
    def test_hostile_target_dry_run_uses_pack_data_without_destination_writes(self) -> None:
        write(self.vault / "operator-note.md", "Preserve this note.\n")
        before = snapshot(self.vault)
        result = self.bash(self.source / "bin/li-vault-init", "--dry-run")
        self.assertFalse(self.marker.exists(), "vault path discovery executed target code")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("synthetic vault/sessions", result.stdout)
        self.assertIn("[dry-run] install sessions.base", result.stdout)
        self.assertEqual(snapshot(self.vault), before)

    def test_relative_helper_and_repo_flag_keep_source_target_separate(self) -> None:
        result = self.bash(
            "bin/li-vault-init", "--repo", self.target.as_posix(), "--dry-run",
            cwd=self.source, extra={"LINTEL_REPO_ROOT": self.source.as_posix()},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.marker.exists())
        self.assertIn("[dry-run] create hub note: target project.md", result.stdout)
        self.assertEqual(snapshot(self.vault), {})

    def test_own_vault_resolver_precedes_home_and_stale_source_environment(self) -> None:
        write(self.lintel_home / "lib/pack-resolver.sh", HOSTILE_RESOLVER)
        write(self.target / "bin/_audit.sh", HOSTILE_RESOLVER)
        result = self.bash(
            self.source / "bin/li-vault-init", "--dry-run",
            extra={"LINTEL_SOURCE_ROOT": self.target.as_posix()},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.marker.exists())
        self.assertEqual(snapshot(self.vault), {})

    def test_real_fixture_install_and_idempotency_preserve_every_vault_file(self) -> None:
        script = self.source / "bin/li-vault-init"
        first = self.bash(script)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertFalse(self.marker.exists())
        self.assertEqual(
            (self.vault / "sessions.base").read_bytes(),
            (self.source / "templates/obsidian/sessions.base").read_bytes(),
        )
        self.assertIn("type: repo-hub", (self.vault / "target project.md").read_text())
        self.assertIn("type: session-index", (self.vault / "00-index.md").read_text())
        for path in self.vault.iterdir():
            with path.open("a", encoding="utf-8") as handle:
                handle.write("\nOperator customization.\n")
        write(self.vault / "unrelated.md", "Unrelated vault content.\n")
        before = snapshot(self.vault)
        again = self.bash(script)
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertEqual(snapshot(self.vault), before)
        self.assertEqual(again.stdout.count("skip "), 3)

    def test_trusted_home_resolver_fallback_preserves_vault_configuration(self) -> None:
        self.install_resolver_fallback()
        self.set_policy(CUSTOM_PATH, installed=True)
        result = self.bash(self.source / "bin/li-vault-init", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.marker.exists())
        self.assertIn("[dry-run] install sessions.base", result.stdout)
        self.assertEqual(snapshot(self.vault), {})

    def test_vault_template_fallback_keeps_explicit_destination_support(self) -> None:
        relative = "templates/obsidian/sessions.base"
        expected = (self.source / relative).read_bytes()
        dest = self.lintel_home / relative
        dest.parent.mkdir(parents=True)
        shutil.copyfile(self.source / relative, dest)
        (self.source / relative).unlink()
        result = self.bash(
            self.source / "bin/li-vault-init", "--vault", self.vault.as_posix()
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.vault / "sessions.base").read_bytes(), expected)
        self.assertFalse(self.marker.exists())

    def test_explicit_vault_and_missing_configuration_remain_distinct(self) -> None:
        self.set_policy(CUSTOM_PATH, vault_path="missing-vault")
        script = self.source / "bin/li-vault-init"
        explicit = self.bash(script, "--vault", self.vault.as_posix(), "--dry-run")
        self.assertEqual(explicit.returncode, 0, explicit.stdout + explicit.stderr)
        missing = self.bash(script, "--dry-run")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("vault sessions dir not found", missing.stderr)
        self.assertFalse(self.marker.exists())
        self.assertEqual(snapshot(self.vault), {})


class Adr(Fixture):
    def prepare_store(self, *, legacy: bool = False, template: str | None = None) -> Path:
        if legacy:
            (self.target / ".claude/lintel-layout.yaml").unlink()
        directory = self.target / ("docs/adr" if legacy else ".claude/decisions")
        if template is None:
            template = (
                ROOT / "scaffolding/01-foundation/.claude/decisions/TEMPLATE.md"
            ).read_text(encoding="utf-8")
        write(directory / "TEMPLATE.md", template)
        return directory

    def test_documented_title_creates_first_stock_adr_and_local_commit(self) -> None:
        directory = self.prepare_store()
        result = self.bash(self.source / "bin/li-adr-new", "Choose a fixture")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        path = directory / "0001-choose-a-fixture.md"
        content = path.read_text(encoding="utf-8")
        self.assertIn("# ADR-0001: Choose a fixture", content)
        self.assertIn("- **Status:** Proposed", content)
        self.assertIn(f"- **Date:** {datetime.date.today().isoformat()}", content)
        self.assertIn("## Alternatives considered", content)
        self.assertEqual(self.git("branch", "--show-current"), "adr-0001-choose-a-fixture")
        self.assertEqual(self.git("log", "-1", "--format=%s"), "adr: 0001 Choose a fixture")
        self.assertEqual(
            self.git("show", "HEAD:.claude/decisions/0001-choose-a-fixture.md"),
            content.strip(),
        )

    def test_existing_store_numbers_are_decimal_unique_and_status_is_parsed(self) -> None:
        directory = self.prepare_store()
        write(directory / "0007-old.md", "Keep seven.\n")
        write(directory / "0009-later.md", "Keep nine.\n")
        write(directory / "123draft-not-an-id.md", "Keep non-ADR notes.\n")
        for number, args, title, status in (
            ("0010", ("Accepted choice", "--status", "accepted"), "Accepted choice", "Accepted"),
            ("0011", ("--status", "proposed", "Next choice"), "Next choice", "Proposed"),
        ):
            with self.subTest(number=number):
                result = self.bash(self.source / "bin/li-adr-new", *args)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                paths = list(directory.glob(f"{number}-*.md"))
                self.assertEqual(len(paths), 1)
                content = paths[0].read_text(encoding="utf-8")
                self.assertIn(f"# ADR-{number}: {title}", content)
                self.assertIn(f"- **Status:** {status}", content)
        self.assertEqual((directory / "0007-old.md").read_text(), "Keep seven.\n")
        self.assertEqual((directory / "0009-later.md").read_text(), "Keep nine.\n")

    def test_custom_template_and_hostile_title_are_literal_data(self) -> None:
        directory = self.prepare_store(
            template="# ADR-{{NNNN}}: {{TITLE}}\nStatus: {{STATUS}}\n"
            "Date: {{DATE}}\n\nKeep custom context & syntax.\n"
        )
        title = r"Choice & pipe | $(touch title-marker) `touch backtick-marker` \e {{STATUS}}"
        result = self.bash(self.source / "bin/li-adr-new", title, "--status", "accepted")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        paths = list(directory.glob("0001-*.md"))
        self.assertEqual(len(paths), 1)
        content = paths[0].read_text(encoding="utf-8")
        self.assertIn(f"# ADR-0001: {title}", content)
        self.assertIn("Status: accepted\n", content)
        self.assertIn("Keep custom context & syntax.", content)
        self.assertFalse((self.target / "title-marker").exists())
        self.assertFalse((self.target / "backtick-marker").exists())

    def test_invalid_arguments_fail_explicitly_without_writing(self) -> None:
        directory = self.prepare_store()
        before = snapshot(directory)
        head = self.git("rev-parse", "HEAD")
        for args in (
            (), ("--status",), ("Title", "--status"), ("Title", "--status", ""),
            ("Title", "--status", "--help"), ("Title", "--status", "unsupported"),
            ("Title", "--status", "$(touch status-marker)"), ("--unknown",),
            ("Title", "extra title"),
        ):
            with self.subTest(args=args):
                result = self.bash(self.source / "bin/li-adr-new", *args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertTrue(result.stderr.strip())
                self.assertNotIn("unbound variable", result.stderr)
                self.assertEqual(snapshot(directory), before)
        self.assertFalse((self.target / "status-marker").exists())
        self.assertEqual(self.git("rev-parse", "HEAD"), head)

    def test_help_does_not_require_a_working_repository(self) -> None:
        result = self.bash(
            self.source / "bin/li-adr-new", "--help", cwd=self.home,
            extra={"LINTEL_REPO_ROOT": ""},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Usage:", result.stdout)

    def test_legacy_decisions_location_is_retained(self) -> None:
        directory = self.prepare_store(legacy=True)
        result = self.bash(self.source / "bin/li-adr-new", "Legacy fixture")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "# ADR-0001: Legacy fixture",
            (directory / "0001-legacy-fixture.md").read_text(),
        )
        self.assertFalse((self.target / ".claude/decisions").exists())


class Updater(Fixture):
    def setUp(self) -> None:
        super().setUp()
        self.stubs = self.base / "stub commands"
        self.log = self.base / "update-calls.txt"
        self.install_marker = self.base / "fallback-installed"
        for tool in ("git", "gemini", "copilot", "droid", "claude", "codex", "cursor"):
            path = self.stubs / tool
            write(path, UPDATE_STUB)
            path.chmod(0o755)
        (self.lintel_home / ".git").mkdir()
        self.update_env = {
            "PATH": str(self.stubs) + os.pathsep + self.env["PATH"],
            "STUB_LOG": self.log.as_posix(),
            "STUB_INSTALL_MARKER": self.install_marker.as_posix(),
        }

    def update(self, *args: str, **statuses: str) -> subprocess.CompletedProcess[str]:
        if self.log.exists():
            self.log.unlink()
        return self.bash(
            self.source / "bin/li-update", *args, extra=dict(self.update_env, **statuses)
        )

    def calls(self) -> list[str]:
        return [
            f"{tool} {args}"
            for tool, _, args in (
                line.split("\t") for line in self.log.read_text().splitlines()
            )
        ]

    def assert_other_hosts_run(self) -> None:
        for command in (
            "gemini extensions update li", "copilot plugin update li@jokerman-lintel",
            "droid plugin update li",
        ):
            self.assertIn(command, self.calls())

    def test_success_preserves_all_hosts_and_operator_guidance(self) -> None:
        result = self.update()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.calls()[:2], ["git fetch -q origin", "git pull --ff-only -q"])
        self.assert_other_hosts_run()
        for guidance in ("claude code:", "codex:", "cursor:", "li-doctor"):
            self.assertIn(guidance, result.stdout)
        for line in self.log.read_text().splitlines():
            tool, cwd, _ = line.split("\t")
            expected = "/synthetic home/.lintel" if tool == "git" else "/target project"
            self.assertTrue(cwd.endswith(expected), line)

    def test_fetch_failure_stops_pull_but_not_independent_hosts(self) -> None:
        result = self.update(FETCH_STATUS="17")
        self.assertEqual(result.returncode, 17, result.stdout + result.stderr)
        self.assertNotIn("git pull --ff-only -q", self.calls())
        self.assert_other_hosts_run()
        self.assertNotIn("updated", result.stdout)
        self.assertIn("failed", result.stderr.lower())

    def test_pull_failure_is_reported_and_hosts_continue(self) -> None:
        result = self.update(PULL_STATUS="18")
        self.assertEqual(result.returncode, 18, result.stdout + result.stderr)
        self.assert_other_hosts_run()
        self.assertNotIn("updated", result.stdout)

    def test_gemini_failure_cannot_become_success(self) -> None:
        result = self.update(GEMINI_STATUS="21")
        self.assertEqual(result.returncode, 21, result.stdout + result.stderr)
        self.assert_other_hosts_run()
        self.assertIn("failed", result.stderr.lower())

    def test_copilot_failure_runs_and_verifies_install_fallback(self) -> None:
        result = self.update(COPILOT_STATUS="22")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("copilot plugin install li@jokerman-lintel --force", self.calls())
        self.assertEqual(self.install_marker.read_text(), "installed\n")
        self.assert_other_hosts_run()

    def test_copilot_failed_fallback_is_not_success(self) -> None:
        result = self.update(COPILOT_STATUS="22", INSTALL_STATUS="23")
        self.assertEqual(result.returncode, 23, result.stdout + result.stderr)
        self.assertFalse(self.install_marker.exists())
        self.assert_other_hosts_run()

    def test_droid_failure_is_not_discarded(self) -> None:
        result = self.update(DROID_STATUS="24")
        self.assertEqual(result.returncode, 24, result.stdout + result.stderr)
        self.assertIn("failed", result.stderr.lower())

    def test_first_unrecovered_failure_survives_later_results(self) -> None:
        result = self.update(FETCH_STATUS="17", GEMINI_STATUS="21", DROID_STATUS="24")
        self.assertEqual(result.returncode, 17, result.stdout + result.stderr)
        self.assert_other_hosts_run()

    def test_failed_host_discovery_is_explicit_and_other_hosts_continue(self) -> None:
        for host in ("GEMINI", "COPILOT", "DROID"):
            with self.subTest(host=host):
                result = self.update(**{f"{host}_LIST_STATUS": "25"})
                self.assertEqual(result.returncode, 25, result.stdout + result.stderr)
                self.assertIn("failed", result.stderr.lower())
                updates = [call for call in self.calls() if " update " in call]
                self.assertEqual(len(updates), 2, self.calls())
                self.assertFalse(any(call.startswith(host.lower()) for call in updates))

    def test_absent_plugins_are_skipped_without_invented_updates(self) -> None:
        result = self.update(
            GEMINI_LIST_TEXT="example", COPILOT_LIST_TEXT="example", DROID_LIST_TEXT="example"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(any(" update " in call for call in self.calls()))

    def test_dry_run_never_invokes_mutating_commands(self) -> None:
        result = self.update(
            "--dry-run", FETCH_STATUS="17", GEMINI_STATUS="21",
            COPILOT_STATUS="22", DROID_STATUS="24",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            self.calls(),
            ["gemini extensions list", "copilot plugin list", "droid plugin list"],
        )
        self.assertIn("[dry-run]", result.stdout)
        self.assertFalse(self.install_marker.exists())

    def test_non_git_scaffolding_keeps_independent_host_updates(self) -> None:
        (self.lintel_home / ".git").rmdir()
        result = self.update()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("git fetch -q origin", self.calls())
        self.assertIn("not a git repo", result.stdout)
        self.assert_other_hosts_run()


if __name__ == "__main__":
    unittest.main(verbosity=2)
