#!/usr/bin/env python3
# component: continuity-consolidation-tests
# implements: ADR-0005, ADR-0006, ADR-0028, ADR-0031
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: data-only parent; product calls in synthetic fixtures, no real host activation
# last_intent_review: 2026-09-25
"""Exercise canonical caller blocks and the shared advisory freeze producer/consumer."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[2]
GIT = shutil.which("git")
GIT_BASH = Path(GIT).resolve().parent.parent / "bin/bash.exe" if GIT else None
BASH = (str(GIT_BASH) if os.name == "nt" and GIT_BASH and GIT_BASH.is_file()
        else shutil.which("bash"))


def body(skill: str) -> str:
    return (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")


def bash_block(text: str, heading: str) -> str:
    """Select one Bash fence inside the named heading, never a global first fence."""
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError as error:
        raise AssertionError(f"Missing heading: {heading}") from error
    level = len(heading) - len(heading.lstrip("#"))
    captured = []
    inside = False
    for line in lines[start + 1:]:
        if inside:
            if re.fullmatch(r" {0,3}```", line):
                return textwrap.dedent("\n".join(captured) + "\n")
            captured.append(line)
        elif re.fullmatch(r" {0,3}```bash", line):
            inside = True
        elif re.match(rf"^#{{1,{level}}} ", line):
            break
    raise AssertionError(f"No complete Bash block under {heading}")


class ContinuityContracts(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(BASH, "Bash is required for the real caller blocks")
        self.base = Path(tempfile.mkdtemp(prefix="w3-", dir=os.environ.get("TEMP"))).resolve()
        self.repo = self.base / "repo"
        self.cwd = self.base / "different-cwd"
        self.repo.mkdir()
        self.cwd.mkdir()
        self.env = {key: value for key, value in os.environ.items() if key.upper() in {
            "PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "SYSTEMDRIVE",
            "OS", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS",
        }}
        for key, name in {
            "HOME": "home", "USERPROFILE": "home", "APPDATA": "app", "LOCALAPPDATA": "local",
            "TEMP": "temp", "TMP": "temp", "TMPDIR": "temp",
            "XDG_CONFIG_HOME": "config", "XDG_CACHE_HOME": "cache",
            "XDG_DATA_HOME": "data", "XDG_STATE_HOME": "state",
            "LINTEL_HOME": "lintel", "LINTEL_PACKS_DIR": "lintel/packs",
        }.items():
            path = self.base / name
            path.mkdir(parents=True, exist_ok=True)
            self.env[key] = path.as_posix()
        self.env.update(
            LINTEL_SOURCE_ROOT=ROOT.as_posix(), LINTEL_REPO_ROOT=self.repo.as_posix(),
            LINTEL_ACTIVE_PACK_FILE=(self.base / "lintel/packs/active-pack").as_posix(),
            LINTEL_AUDIT_DIR=(self.base / "audit").as_posix(),
            LINTEL_JOBS_DIR=(self.base / "jobs").as_posix(),
            LINTEL_JOBS_REGISTRY=(self.base / "lintel/jobs/_active.md").as_posix(),
            LINTEL_PYTHON=Path(sys.executable).as_posix(),
            python_cmd=Path(sys.executable).as_posix(),
            LINTEL_SESSION_ID="w3-fixture", LINTEL_OPERATOR="fixture",
            GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=(self.base / "home/.gitconfig").as_posix(),
            GIT_CEILING_DIRECTORIES=self.base.as_posix(), GIT_TERMINAL_PROMPT="0",
            PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
        )
        self.write(".claude/lintel-layout.yaml", "layout_version: 5\n")
        self.write("docs/one note.md", "memory architecture\n")
        self.write("docs/two.md", "memory memory memory memory memory\n")
        self.run_command(["git", "-C", str(self.repo), "init", "-q"])
        self.run_command(["git", "-C", str(self.repo), "symbolic-ref", "HEAD", "refs/heads/shared"])
        self.addCleanup(self.cleanup)

    def cleanup(self):
        # Leave a root backing the shared MSYS mount intact (L-049).
        observed = subprocess.run([BASH, "--noprofile", "--norc", "-c", "mount"],
                                  env=self.env, capture_output=True, text=True, check=False)
        mount = next((line for line in observed.stdout.splitlines() if " on /tmp " in line), "")
        if observed.returncode or str(self.base).replace("\\", "/").casefold() in mount.replace("\\", "/").casefold():
            print(f"Retained synthetic root backing an unknown/selected MSYS mount: {self.base}",
                  file=sys.stderr)
        else:
            self.assertTrue(self.base.name.startswith("w3-"))
            shutil.rmtree(self.base)

    def write(self, relative: str, text: str) -> Path:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_command(self, command: list[str], *, expected: int = 0):
        result = subprocess.run(command, cwd=self.cwd, env=self.env, capture_output=True,
                                text=True, encoding="utf-8", check=False)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def shell(self, script: str, *args: str, expected: int = 0):
        # Quote the literal argv after MSYS startup, including globs and spaced paths.
        self.env["W3_SCRIPT"] = script
        for index, arg in enumerate(args):
            self.env[f"W3_ARG_{index}"] = arg
        operands = " ".join(f'"$W3_ARG_{index}"' for index in range(len(args)))
        return self.run_command(
            [BASH, "--noprofile", "--norc", "-c", f'bash -c "$W3_SCRIPT" caller {operands}'],
            expected=expected,
        )

    def recipe(self, skill: str, heading: str, *args: str, expected: int = 0):
        return self.shell(bash_block(body(skill), heading), *args, expected=expected)

    def freeze(self, *args: str, expected: int = 0):
        return self.recipe("code-freeze", "## Run the selected operation", *args, expected=expected)

    def hook(self, target: str):
        return self.shell(
            'bash "$LINTEL_SOURCE_ROOT/hooks/shared/frozen-zone-warn/run.sh" "$1" </dev/null',
            target,
        )

    def state_file(self) -> Path:
        return self.repo / ".claude/runtime/state/code-freeze/w3-fixture.yaml"

    def test_heading_selection_does_not_take_an_unrelated_first_fence(self):
        document = "## Unrelated\n```bash\nexit 19\n```\n\n" + body("context-warm")
        selected = bash_block(document, "## Related mode")
        self.assertNotIn("exit 19", selected)
        self.assertIn('--topic "$topic"', selected)
        with self.assertRaises(AssertionError):
            bash_block("## Empty\n## Next\n```bash\nexit 0\n```\n", "## Empty")
        self.assertEqual(bash_block("## Nested\n   ```bash\n   echo yes\n   ```\n", "## Nested"),
                         "echo yes\n")

    def test_retired_entries_have_live_replacements_not_duplicate_wrappers(self):
        for name in ("pause", "resume", "context-warm", "lessons-add", "lessons-surface",
                     "skill-new", "capture", "doctor", "code-freeze"):
            self.assertIn(f"name: {name}\n", body(name))
        for retired in ("context-save", "context-restore", "context-warm-related",
                        "context-warm-adrs", "context-warm-sessions", "learn", "lessons",
                        "skillify", "retro", "landing-report", "health", "code-unfreeze"):
            self.assertFalse((ROOT / "skills" / retired / "SKILL.md").exists(), retired)
        self.assertNotIn("v1_alias:", body("context-budget"))
        self.assertNotIn("v1_alias:", body("code-freeze"))

    def test_related_selection_retains_ranking_limits_and_cooling(self):
        result = self.recipe("context-warm", "## Related mode", "memory",
                             "--glob", "docs/*.md", "--limit", "1")
        manifest = json.loads(result.stdout)
        self.assertEqual([item["path"] for item in manifest["files"]], ["docs/two.md"])
        self.assertEqual(manifest["omitted_count"], 1)
        self.assertEqual(Path(manifest["source_root"]), self.repo)
        self.recipe("context-cool", "## Workflow", "--path", "docs/two.md")
        cooled = json.loads(self.recipe("context-warm", "## Related mode", "memory",
                                       "--glob", "docs/*.md").stdout)
        self.assertEqual([item["path"] for item in cooled["files"]], ["docs/one note.md"])
        self.assertIn("docs/two.md", cooled["excluded"])
        self.recipe("context-warm", "## Related mode", "memory", expected=2)
        self.recipe("context-warm", "## Related mode", "memory",
                    "--path", "../outside.md", expected=2)

    def test_adr_modes_retain_unknown_status_and_legacy_directory(self):
        self.write(".claude/decisions/0001-a.md", "# Architecture\n**Status:** Accepted (2020-01-01)\n")
        self.write(".claude/decisions/0002-b.md", "# Architecture\n**Status:** Superseded\n")
        self.write(".claude/decisions/0003-c.md", "# Architecture\nNo status yet.\n")
        selected = json.loads(self.recipe("context-warm", "## ADR mode", "architecture",
                                         "--accepted-only").stdout)
        self.assertEqual({item["adr"]["status"] for item in selected["files"]}, {"accepted", "unknown"})
        all_adrs = json.loads(self.recipe("context-warm", "## ADR mode", "architecture",
                                         "--include-deprecated").stdout)
        self.assertEqual(len(all_adrs["files"]), 3)
        self.recipe("context-warm", "## ADR mode", "architecture", "--wrong", expected=2)
        (self.repo / ".claude/lintel-layout.yaml").unlink()
        self.write("docs/adr/0001-legacy.md", "# Architecture\n- **Status:** Accepted\n")
        legacy = json.loads(self.recipe("context-warm", "## ADR mode", "architecture").stdout)
        self.assertEqual([item["path"] for item in legacy["files"]], ["docs/adr/0001-legacy.md"])

    def test_pause_and_resume_keep_old_suffix_owned_discovery_and_relative_target(self):
        save = bash_block(body("pause"), "## Workflow")
        manifest = json.loads(self.shell(save + '\nprintf "owned checkpoint\\n" > "$path"\n'
                                        'context_checkpoint "$path"\n').stdout)
        relative = manifest["files"][0]["path"]
        self.assertTrue(relative.endswith("-context-save.md"))
        path = Path(manifest["source_root"]) / relative
        selected = path.relative_to(self.repo).as_posix()
        for spelling in (selected, "./" + selected, selected.replace("/", "\\")):
            restored = self.recipe("resume", "### Step 1b — Read a selected checkpoint", spelling)
            self.assertEqual(json.loads(restored.stdout)["files"][0]["sha256"],
                             manifest["files"][0]["sha256"])
        old = self.write(".claude/runtime/sessions/shared/20990101-000000-old-context-save.md",
                         "old local checkpoint\n")
        discovery = bash_block(body("context-warm"), "## Sessions mode") + '\nprintf "%s\\n" "$candidates"\n'
        output = self.shell(discovery, "1").stdout
        self.assertIn(old.name, output)
        self.shell(discovery, "6", expected=2)
        self.shell(discovery, "0", expected=2)
        self.shell(discovery, "1", "extra", expected=2)
        external = self.base / "shared.md"
        external.write_text("authorized fixture handoff", encoding="utf-8")
        self.recipe("resume", "### Step 1b — Read a selected checkpoint",
                    external.as_posix(), expected=1)
        self.recipe("resume", "### Step 1b — Read a selected checkpoint",
                    external.as_posix(), "--explicit")
        self.recipe("resume", "### Step 1b — Read a selected checkpoint", "", expected=2)
        self.assertEqual(external.read_text(encoding="utf-8"), "authorized fixture handoff")

    def test_resume_retains_selected_work_profile_and_job_contract(self):
        text = body("resume")
        self.assertLess(text.index("First honor an operator-selected work map"), text.index("checkpoints="))
        for contract in ("--job <id>", "--from <phase|step>", "--from <step>", "./BUILD",
                         "LINTEL_SCOPE_PATH", "job_resume_point", "job_can_start",
                         "workflow_resume <original-cycle-id> <selected-map>",
                         "state_resume_phase", "actual latest reader", "source-byte"):
            self.assertIn(contract, text)
        preferences = (ROOT / "skills/build/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("checkpoint_mode", preferences)

    def test_lessons_lookup_preserves_supersession_id_and_missing_diagnostics(self):
        store = self.write(".claude/memory/lessons.md",
                           "# Lessons\n\n## L-001 - Original memory rule\n"
                           "superseded_by: L-002 (2020-01-01)\nOld memory guidance.\n\n"
                           "## L-002 - Current memory rule\n**Rule:** Keep memory grammar.\n")
        before = store.read_bytes()
        ranked = self.recipe("lessons-surface", "## Read the selected store",
                             "--keyword", "memory").stdout
        self.assertNotIn("L-001", ranked)
        self.assertIn("L-002", ranked)
        indexed = self.recipe("lessons-surface", "## Read the selected store", "--all").stdout
        self.assertIn("L-001 - Original memory rule (superseded)", indexed)
        exact = self.recipe("lessons-surface", "## Read the selected store", "--id", "L-001").stdout
        self.assertIn("superseded_by: L-002", exact)
        self.recipe("lessons-surface", "## Read the selected store", "--id", "L-999", expected=1)
        self.recipe("lessons-surface", "## Read the selected store", "--keyword", expected=2)
        self.assertEqual(before, store.read_bytes())
        for writer in ("lessons_helper add", "lessons_helper update", "lessons_helper supersede",
                       "skillify-candidate", "--scope global"):
            self.assertIn(writer, body("lessons-add"))

    def test_skill_new_keeps_exact_draft_validation_and_no_activation(self):
        draft = self.write("drafts/example/SKILL.md",
                           "---\nname: example\nlayer: foundation\ndescription: A draft\n"
                           "color: blue\ntools: Read\nvoice: internal\ncli_support: []\n---\n"
                           "# Example\nDraft method only.\n")
        self.env["draft"] = draft.as_posix()
        result = self.recipe("skill-new", "### Validate the exact draft")
        self.assertIn("DRAFT:", result.stdout)
        draft.write_text("---\nname: example\n---\n", encoding="utf-8")
        self.recipe("skill-new", "### Validate the exact draft", expected=1)
        self.assertIn("li-catalog.py", bash_block(body("skill-new"), "### Check name and destination"))
        self.assertIn("refusing overwrite", body("skill-new"))

    def test_doctor_views_run_real_helper_and_preserve_failure(self):
        for options in (("--json",), ("--fast", "--hooks-only", "--json"),
                        ("--layers-only",), ("--upstream-only",)):
            with self.subTest(options=options):
                result = self.recipe("doctor", "## Run the owned diagnostic", *options, expected=1)
                report = json.loads(result.stdout)
                self.assertEqual(Path(report["source"]), ROOT)
                self.assertEqual(Path(report["target"]), self.repo)
                self.assertEqual(report["host_activation"], "unverified")
                self.assertEqual(report["hook_execution"], "unverified")
                self.assertTrue(report["foundation_missing"])
                self.assertTrue(report["issues"])
        self.recipe("doctor", "## Run the owned diagnostic", "--unknown", expected=2)
        self.recipe("doctor", "## Run the owned diagnostic", "--hooks-only", "--layers-only", expected=2)

    def test_freeze_state_reaches_hook_and_lift_list_preserve_unmatched_entries(self):
        self.write("src/frozen/file.txt", "unchanged\n")
        initial = json.loads(self.freeze("src/frozen/", "src/other", "--reason", "fixture",
                                         "--until", "2000-01-01").stdout)
        self.assertEqual(len(initial["frozen"]), 2)
        original = self.state_file().read_bytes()
        self.freeze("--list")
        self.assertEqual(self.state_file().read_bytes(), original)
        warning = self.hook(str(self.repo / "src/frozen/file.txt"))
        self.assertIn("warn-only", warning.stdout)
        self.assertIn("/li:code-freeze --list", warning.stdout)
        self.assertEqual(self.hook("src/frozen-other/file.txt").stdout, "")
        hooks = [json.loads(line) for line in (self.base / "audit/hooks.jsonl").read_text().splitlines()]
        self.assertEqual(len(hooks), 1)
        self.assertEqual((hooks[0]["kind"], hooks[0]["tier"], hooks[0]["source"]),
                         ("frozen_zone_warn", "warn", "session-freeze"))
        lifted = json.loads(self.freeze("--lift", "src/frozen", "--reason", "scope changed").stdout)
        self.assertEqual([entry["path"] for entry in lifted["frozen"]], ["src/other"])
        self.assertEqual(lifted["frozen"][0], initial["frozen"][1])
        self.assertEqual(self.hook("src/frozen/file.txt").stdout, "")
        remaining = self.state_file().read_bytes()
        absent = json.loads(self.freeze("--lift", "src/absent").stdout)
        self.assertEqual(absent["not_frozen"], ["src/absent"])
        self.assertEqual(remaining, self.state_file().read_bytes())
        self.freeze("--lift", "--all")
        self.assertEqual(json.loads(self.freeze("--list").stdout)["frozen"], [])
        self.assertEqual((self.repo / "src/frozen/file.txt").read_text(), "unchanged\n")
        events = [json.loads(line) for line in (self.base / "audit/code-freeze.jsonl").read_text().splitlines()]
        self.assertEqual([row["kind"] for row in events], ["freeze", "freeze", "unfreeze", "unfreeze"])

    def test_freeze_legacy_is_read_only_and_empty_repo_state_takes_precedence(self):
        legacy = self.base / "lintel/freeze/w3-fixture.yaml"
        legacy.parent.mkdir(parents=True)
        legacy.write_text("frozen:\n  - path: src/legacy/\n    reason: old scope\n", encoding="utf-8")
        before = legacy.read_bytes()
        listed = json.loads(self.freeze("--list").stdout)
        self.assertEqual(listed["source"], "legacy-read-only")
        self.assertIn("warn-only", self.hook("src/legacy/file.txt").stdout)
        self.freeze("--lift", "--all", expected=2)
        self.assertEqual(legacy.read_bytes(), before)
        self.assertFalse(self.state_file().exists())
        self.write(".claude/runtime/state/code-freeze/w3-fixture.yaml", "advisory: true\nfrozen: []\n")
        self.assertEqual(self.hook("src/legacy/file.txt").stdout, "")
        self.assertEqual(json.loads(self.freeze("--list").stdout)["frozen"], [])
        self.assertEqual(legacy.read_bytes(), before)

    def test_freeze_glob_expands_to_literal_files_before_native_path_checks(self):
        self.write("src/frozen/first.txt", "one\n")
        self.write("src/frozen/second.txt", "two\n")
        self.write("src/frozen/keep.md", "not selected\n")
        self.write("src/frozen-other/third.txt", "different directory\n")
        frozen = json.loads(self.freeze("src/frozen/*.txt", "--reason", "bounded glob").stdout)
        self.assertEqual([row["path"] for row in frozen["frozen"]],
                         ["src/frozen/first.txt", "src/frozen/second.txt"])
        self.assertIn("warn-only", self.hook("src/frozen/first.txt").stdout)
        self.assertEqual(self.hook("src/frozen/keep.md").stdout, "")
        self.assertEqual(self.hook("src/frozen-other/third.txt").stdout, "")
        state = self.state_file().read_bytes()
        self.freeze("--lift", "src/frozen/*.txt", expected=2)
        self.freeze("missing/*.txt", expected=2)
        self.freeze("../outside/*.txt", expected=2)
        self.assertEqual(self.state_file().read_bytes(), state)

    def test_freeze_refuses_bad_state_and_paths_without_silent_reset(self):
        self.freeze("../outside", expected=2)
        self.freeze("--all", expected=2)
        self.freeze("missing/*.py", expected=2)
        self.assertFalse(self.state_file().exists())
        self.freeze("src/future", "--reason", 'literal "quotes" and spaces')
        state = self.state_file().read_bytes()
        self.freeze("--lift", "src/*", expected=2)
        self.assertEqual(self.state_file().read_bytes(), state)
        self.state_file().write_text("frozen: not-a-list\n", encoding="utf-8")
        malformed = self.state_file().read_bytes()
        self.freeze("--list", expected=2)
        self.freeze("--lift", "--all", expected=2)
        warning = self.hook("src/future/file.txt")
        self.assertIn("could not be read", warning.stdout)
        self.assertEqual(self.state_file().read_bytes(), malformed)

    def test_capture_views_preserve_observations_and_do_not_complete_a_cycle(self):
        capture = body("capture")
        for contract in ("--retrospective", "--release-summary", "--since", "--until",
                         "--include-stats", "--emit-lessons", "audit_read_files", "bin/li-events.py",
                         "check=performed|not_performed", "Migration notes", "DRAFT",
                         "Return after the selected report", "cycle_complete=false"):
            self.assertIn(contract, capture)
        self.assertIn("Step 8b", capture)
        self.assertIn("no release, tag, commit, publication or approval", capture)

class RetrospectiveWordingContracts(unittest.TestCase):
    def test_retrospective_wording_guard_checks_only_the_preserved_section(self):
        guard = (ROOT / "tests/shape/observation-consumer-wording.sh").read_text(encoding="utf-8")
        function = re.search(r"(?ms)^retrospective_text\(\) \{\n.*?^\}\n", guard)
        self.assertIsNotNone(function)
        verdict = re.search(r"(?m)^VERDICT='([^']+)'$", guard)
        self.assertIsNotNone(verdict)
        script = (function[0] + "\nVERDICT='" + verdict[1] + "'\n"
                  'section="$(retrospective_text "$1")" || exit $?\n'
                  '[ -n "$section" ] || exit 2\n'
                  'if printf "%s\\n" "$section" | grep -qiE "$VERDICT"; then exit 1; fi\n')
        heading = "### Step 8 — Retrospective (--retrospective)\n"
        ending = "\n### Step 8b — Release report\nHistorical dead write outside this method.\n"
        self.assertIsNotNone(BASH)
        with tempfile.TemporaryDirectory(prefix="retrospective-wording-") as temporary:
            path = Path(temporary) / "retrospective.md"
            for text, expected in (
                    (heading + "Absence remains unobserved.\n" + ending, 0),
                    (heading + "Nothing ran.\n" + ending, 1),
                    ("### Different section\nAbsence remains unobserved.\n", 2),
                    (heading + "One.\n" + heading + "Two.\n", 2)):
                with self.subTest(expected=expected):
                    path.write_text(text, encoding="utf-8")
                    result = subprocess.run(
                        [BASH, "--noprofile", "--norc", "-c", script, "wording-fixture", path.as_posix()],
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(result.returncode, expected, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
