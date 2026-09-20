# component: context-safety-test
# implements: ADR-0006, ADR-0010
# intent: .claude/plans/universal-implementation/packages/P03.md
# constraints: stdlib, synthetic files and local Git only
# last_intent_review: 2026-09-20
import json
from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SOURCE / "lib"))
import context_safety as safety


class ContextSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lintel-context-safety-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "project with spaces"
        self.root.mkdir()
        (self.root / "docs").mkdir()
        (self.root / "docs" / "one file.md").write_text("architecture one")
        (self.root / "docs" / "two.md").write_text("architecture two")
        (self.root / "unrelated.txt").write_text("keep this")

    def test_literal_spaces_and_execution_text_are_data(self):
        hostile = "$(touch injected); echo not-code.md"
        (self.root / hostile).write_text("literal")
        result = safety.select_files(self.root, paths=["docs/one file.md", hostile])
        self.assertEqual({f["path"] for f in result["files"]}, {"docs/one file.md", hostile})
        self.assertFalse((self.root / "injected").exists())
        self.assertEqual(result["source_root"], str(self.root))
        self.assertEqual(result["estimated_tokens"], (result["bytes"] + 3) // 4)

    def test_globs_are_scoped_and_missing_is_visible(self):
        (self.root / "docs" / "nested").mkdir()
        (self.root / "docs" / "nested" / "three.md").write_text("third")
        direct = safety.select_files(self.root, patterns=["docs/*.md"])
        recursive = safety.select_files(self.root, patterns=["docs/**/*.md"])
        self.assertEqual(len(direct["files"]), 2)
        self.assertEqual(len(recursive["files"]), 3)
        missing = safety.select_files(self.root, paths=["not here.md"])
        self.assertEqual(missing["status"], "empty")
        self.assertEqual(missing["unmatched"], ["not here.md"])
        with self.assertRaises(ValueError):
            safety.select_files(self.root, patterns=["docs/**/*.md"], max_files=2)
        with self.assertRaises(ValueError):
            safety.select_files(self.root, paths=["docs/two.md"], max_bytes=1)

    def test_glob_with_file_prefix_never_selects_the_nonmatching_prefix(self):
        for pattern in ("docs/two.md/*.txt", "docs/two.md/**/notes.md", "docs/two.md/**"):
            with self.subTest(pattern=pattern):
                result = safety.select_files(self.root, patterns=[pattern])
                self.assertEqual(result["files"], [])
                self.assertEqual(result["status"], "empty")
                self.assertEqual(result["unmatched"], [pattern])
                run = subprocess.run(
                    [sys.executable, "-B", str(SOURCE / "lib/context_safety.py"),
                     "select", "--root", str(self.root), "--glob", pattern],
                    capture_output=True, text=True)
                self.assertEqual(run.returncode, 1, run.stderr)
                self.assertEqual(json.loads(run.stdout)["files"], [])
        exact = safety.select_files(self.root, patterns=["docs/two.md"])
        self.assertEqual([f["path"] for f in exact["files"]], ["docs/two.md"])
        self.assertEqual(len(safety.select_files(self.root, patterns=["docs/*.md"])["files"]), 2)

    def test_globstar_comparisons_are_bounded_by_distinct_states(self):
        parts = [f"level{number}" for number in range(20)] + ["leaf.txt"]
        path = "/".join(parts)
        for pattern, expected, comparisons in (
                ("**/" * 12 + "missing.txt", False, len(parts)),
                ("**/" * 12 + "leaf.txt", True, len(parts)),
                ("**/*/" * 12 + "missing.txt", False, len(parts) * 13),
                ("**/*/" * 12 + "leaf.txt", True, len(parts) * 13)):
            with self.subTest(pattern=pattern):
                count = 0
                compare = safety.fnmatchcase

                def bounded_compare(part, rule):
                    nonlocal count
                    count += 1
                    self.assertLessEqual(count, comparisons,
                                         "a path/rule state was compared repeatedly")
                    return compare(part, rule)

                with patch.object(safety, "fnmatchcase", side_effect=bounded_compare):
                    self.assertEqual(safety.matches(path, pattern), expected)
                self.assertGreater(count, 0)

    def test_globstar_long_paths_and_rules_do_not_use_python_recursion(self):
        path = "/".join(["level"] * 1500 + ["leaf.txt"])
        for pattern, expected in (
                ("**/leaf.txt", True),
                ("**/missing.txt", False),
                ("**/" * 1500 + "leaf.txt", True),
                ("**/" * 1500 + "missing.txt", False),
                (path, True),
                (path + "/child", False)):
            with self.subTest(pattern_length=len(pattern), expected=expected):
                self.assertEqual(safety.matches(path, pattern), expected)
        self.assertTrue(safety.matches("leaf.txt", "**/" * 1500 + "leaf.txt"))

    def test_separated_globstar_states_are_compared_at_most_once(self):
        parts = [f"level{number}" for number in range(20)] + ["leaf.txt"]
        rules = ["level*", "le?el*", "l*vel*", "[l]evel*", "level[0-9]*", "leve?*", "missing.txt"]
        pattern = "**/" + "/**/".join(rules)
        compared = set()
        compare = safety.fnmatchcase

        def unique_state(part, rule):
            state = (part, rule)
            self.assertNotIn(state, compared, "distinct spellings identify a repeated matcher state")
            compared.add(state)
            return compare(part, rule)

        with patch.object(safety, "fnmatchcase", side_effect=unique_state):
            self.assertFalse(safety.matches("/".join(parts), pattern))
        self.assertLessEqual(len(compared), len(parts) * len(rules))

    def test_globstar_normalization_preserves_whole_path_matching(self):
        cases = (
            ("leaf.txt", "**/leaf.txt", True),
            ("leaf.txt", "**/**/leaf.txt", True),
            ("a/b/leaf.txt", "**/**/leaf.txt", True),
            ("a/b/leaf.txt", "*/leaf.txt", False),
            ("a/b/leaf.txt", "*/*/leaf.txt", True),
            ("a/b/leaf.txt", "a/**/b/**/leaf.txt", True),
            ("a/b/leaf.txt", "a/**/**/b/**/**/missing.txt", False),
            ("a/b/leaf.txt", "**/[ab]/**/leaf.?xt", True),
            ("a/b/leaf.txt", "**/[!ab]/**/leaf.txt", False),
            ("a/b/leaf.txt", "**/a/**/a/**/leaf.txt", False),
            ("a/a/leaf.txt", "**/a/**/a/**/leaf.txt", True),
            ("a/b/leaf.txt", "**/**", True),
            ("a/b/leaf.txt", "a/**/**", True),
            ("a/b/leaf.txt", "a/**/**/b", False),
            ("a/b/leaf.txt", "**/leaf.txt/**", True),
            ("a/b/leaf.txt", "a/***/leaf.txt", True),
            ("a/x/y/leaf.txt", "a/***/leaf.txt", False),
            ("a/b/leaf.txt", "**/leaf.txt/**/child", False),
            ("a/leaf.txt", "**/LEAF.TXT", False),
        )
        for path, pattern, expected in cases:
            with self.subTest(path=path, pattern=pattern):
                self.assertEqual(safety.matches(path, pattern), expected)

    def _deep_glob_fixture(self):
        root = self.base / "bounded-loader"
        root.mkdir()
        directory = root
        for _ in range(20):
            directory /= "d"
            directory.mkdir()
        file = directory / "leaf.txt"
        file.write_bytes(b"x")
        return root, file.relative_to(root).as_posix()

    def test_globstar_selector_finishes_with_subprocess_timeout_backstop(self):
        root, relative = self._deep_glob_fixture()
        for pattern, expected in (("**/missing.txt", False),
                                  ("**/" * 12 + "missing.txt", False),
                                  ("**/" * 12 + "leaf.txt", True),
                                  ("**/*/" * 12 + "missing.txt", False)):
            with self.subTest(pattern=pattern):
                run = subprocess.run(
                    [sys.executable, "-B", str(SOURCE / "lib/context_safety.py"),
                     "select", "--root", str(root), "--glob", pattern,
                     "--max-files", "1", "--max-bytes", "1"],
                    capture_output=True, text=True, timeout=5)
                self.assertEqual(run.returncode, 0 if expected else 1, run.stderr)
                result = json.loads(run.stdout)
                self.assertEqual([f["path"] for f in result["files"]], [relative] if expected else [])
                self.assertEqual(result["unmatched"], [] if expected else [pattern])

    def test_persisted_cooling_globstars_are_bounded_on_every_selection(self):
        root, relative = self._deep_glob_fixture()
        ignore = root / ".claude/runtime/state/context-ignore.json"
        missing = "**/" * 12 + "missing.txt"
        safety.update_exclusions(root, ignore, [], [missing])
        before = ignore.read_bytes()
        for _ in range(3):
            count = 0
            compare = safety.fnmatchcase

            def bounded_compare(part, rule):
                nonlocal count
                count += 1
                self.assertLessEqual(count, 2 * len(relative.split("/")))
                return compare(part, rule)

            with patch.object(safety, "fnmatchcase", side_effect=bounded_compare):
                result = safety.select_files(root, paths=[relative], exclude_file=ignore, max_bytes=1)
            self.assertEqual([f["path"] for f in result["files"]], [relative])
            self.assertEqual(ignore.read_bytes(), before)
        for pattern, expected in ((missing, True), ("**/" * 12 + "leaf.txt", False)):
            safety.update_exclusions(root, ignore, [], [pattern])
            run = subprocess.run(
                [sys.executable, "-B", str(SOURCE / "lib/context_safety.py"),
                 "select", "--root", str(root), "--path", relative, "--exclude-file", str(ignore)],
                capture_output=True, text=True, timeout=5)
            self.assertEqual(run.returncode, 0 if expected else 1, run.stderr)
            self.assertEqual([f["path"] for f in json.loads(run.stdout)["files"]], [relative] if expected else [])
        self.assertEqual((root / relative).read_bytes(), b"x")

    def test_matching_failure_is_not_reported_as_an_empty_selection(self):
        error = ValueError("synthetic matching work bound exceeded")
        with patch.object(safety, "matches", side_effect=error), self.assertRaisesRegex(ValueError, "work bound"):
            safety.select_files(self.root, patterns=["**/*.md"])
        stdout, stderr = io.StringIO(), io.StringIO()
        args = ["context_safety.py", "select", "--root", str(self.root), "--glob", "**/*.md"]
        with patch.object(safety, "matches", side_effect=error), patch.object(sys, "argv", args), \
                redirect_stdout(stdout), redirect_stderr(stderr):
            status = safety.main()
        self.assertEqual(status, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("work bound", stderr.getvalue())

    def test_traversal_aliases_and_links_are_refused(self):
        for bad in ("../outside", "/outside", "C:/outside", "docs/../unrelated.txt",
                    "docs/two.md.", "docs/two.md ", "CON.txt", "docs/bad\tname"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                safety.select_files(self.root, paths=[bad])
        outside = self.base / "outside.md"
        outside.write_text("not authorized")
        link = self.root / "linked.md"
        try:
            link.symlink_to(outside)
        except OSError:
            # Windows without symlink privilege still exercises reparse refusal.
            from unittest.mock import patch
            with patch.object(safety, "is_link", side_effect=lambda p: p.name == "two.md"):
                with self.assertRaises(ValueError):
                    safety.select_files(self.root, paths=["docs/two.md"])
            print("NOTE: file symlink privilege unavailable; reparse predicate injected for this case.")
        else:
            with self.assertRaises(ValueError):
                safety.select_files(self.root, paths=["linked.md"])
            self.assertNotIn("linked.md", [f["path"] for f in
                             safety.select_files(self.root, patterns=["**/*.md"])["files"]])
            print("PASS: native file symlink escape refused.")

    def test_cool_exclusions_have_a_real_consumer_and_no_reclamation(self):
        ignore = self.root / ".claude/runtime/state/context-ignore.json"
        result = safety.update_exclusions(self.root, ignore, ["docs/one file.md"], ["docs/two.*"])
        self.assertEqual(result["tokens_removed_from_context"], 0)
        self.assertEqual(result["disk_bytes_removed"], 0)
        selected = safety.select_files(self.root, patterns=["docs/*.md"], exclude_file=ignore)
        self.assertEqual(selected["files"], [])
        self.assertEqual(len(selected["excluded"]), 2)
        self.assertTrue((self.root / "docs" / "one file.md").is_file())
        safety.update_exclusions(self.root, ignore, [], [], clear=True)
        self.assertEqual(len(safety.select_files(self.root, patterns=["docs/*.md"],
                                               exclude_file=ignore)["files"]), 2)
        ignore.write_text("{broken")
        with self.assertRaises(ValueError):
            safety.select_files(self.root, patterns=["docs/*.md"], exclude_file=ignore)

    def test_cooling_exclusions_cover_native_case_aliases_without_hiding_distinct_files(self):
        ignore = self.root / ".claude/runtime/state/context-ignore.json"
        upper = self.root / "DOCS" / "TWO.MD"
        aliases = upper.exists() and upper.samefile(self.root / "docs" / "two.md")
        if not aliases:
            upper.parent.mkdir(exist_ok=True)
            upper.write_text("distinct case-sensitive source")
        for paths, patterns in ((["docs/two.md"], []), ([], ["docs/*.md"])):
            with self.subTest(paths=paths, patterns=patterns):
                safety.update_exclusions(self.root, ignore, [], [], clear=True)
                safety.update_exclusions(self.root, ignore, paths, patterns)
                selected = safety.select_files(self.root, paths=["DOCS/TWO.MD"], exclude_file=ignore)
                self.assertEqual(len(selected["files"]), 0 if aliases else 1)
                self.assertEqual(selected["excluded"], ["DOCS/TWO.MD"] if aliases else [])
        safety.update_exclusions(self.root, ignore, [], [], clear=True)
        safety.update_exclusions(self.root, ignore, ["DOCS/TWO.MD"], [])
        selected = safety.select_files(self.root, patterns=["docs/*.md"], exclude_file=ignore)
        self.assertEqual([f["path"] for f in selected["files"]],
                         ["docs/one file.md"] if aliases else ["docs/one file.md", "docs/two.md"])
        self.assertTrue(upper.is_file())
        print("PASS: native case-alias exclusion" if aliases else "PASS: distinct case-sensitive sources retained")

    def test_glob_exclusions_do_not_assume_every_windows_directory_is_case_insensitive(self):
        from unittest.mock import patch
        ignore = self.root / ".claude/runtime/state/context-ignore.json"
        safety.update_exclusions(self.root, ignore, [], ["DOCS/*.MD"])
        # A case-sensitive directory reports different identities for a case variant.
        with patch.object(Path, "samefile", return_value=False):
            selected = safety.select_files(self.root, paths=["docs/two.md"], exclude_file=ignore)
        self.assertEqual([f["path"] for f in selected["files"]], ["docs/two.md"])

    def test_capacity_unknown_estimated_and_observed_are_distinct(self):
        unknown = safety.context_budget(400, used_tokens=80, usage_kind="estimated",
                                        usage_source="fixture heuristic")
        self.assertIsNone(unknown["capacity_tokens"])
        self.assertIsNone(unknown["headroom_tokens"])
        self.assertEqual(unknown["admission"], "unknown")
        measured = safety.context_budget(400, capacity_tokens=150, used_tokens=80,
                                         capacity_source="fixture host", usage_source="fixture host")
        self.assertEqual(measured["admission"], "over-capacity")
        self.assertEqual(measured["headroom_tokens"], 70)
        estimate = safety.context_budget(40, capacity_tokens=150, used_tokens=80,
                                         usage_kind="estimated", capacity_source="fixture host",
                                         usage_source="fixture heuristic")
        self.assertEqual(estimate["headroom_kind"], "estimated")
        with self.assertRaises(ValueError):
            safety.context_budget(40, capacity_tokens=150)
        overused = safety.context_budget(0, capacity_tokens=100, used_tokens=101,
                                        capacity_source="fixture host", usage_source="fixture host")
        self.assertEqual(overused["admission"], "over-capacity")

    def test_perf_flags_only_change_advice(self):
        before = sorted(str(p) for p in self.root.rglob("*"))
        report = safety.perf_advice(safety.context_budget(400), budget=800000,
                                    ceiling=1000000, decay_policy="aggressive")
        self.assertIsNone(report["capacity_tokens"])
        self.assertEqual(report["local_working_set_budget"], 800000)
        self.assertFalse(report["host_settings_changed"])
        self.assertIsNone(report["cost_estimate"])
        self.assertFalse(safety.perf_advice(safety.context_budget(0), off=True)["advice_active"])
        observed = safety.context_budget(0, capacity_tokens=150, used_tokens=80,
                                         capacity_source="fixture host", usage_source="fixture host")
        self.assertEqual(safety.perf_advice(observed, budget=800000)["requested_working_set_fit"],
                         "exceeds-headroom")
        self.assertEqual(before, sorted(str(p) for p in self.root.rglob("*")))

    def test_markdown_yaml_and_unknown_adr_metadata_remain_visible(self):
        adrs = self.root / "decisions"
        adrs.mkdir()
        fixtures = {
            "0001-a.md": "# ADR-0001: Architecture\n\n**Status:** Accepted (2026-06-12)\n",
            "0002-b.md": "# ADR-0002: Architecture\n\n- **Status:** Accepted\n- **Date:** 2026-09-08\n",
            "0003-c.md": "---\nstatus: Proposed\ndate: 2026-09-20\n---\n# Architecture\n",
            "0004-d.md": "# Architecture\nUnrecognized status metadata\n",
            "0005-e.md": "# Architecture\n**Status:** Superseded\n",
        }
        for name, text in fixtures.items():
            (adrs / name).write_text(text)
        result = safety.select_files(self.root, patterns=["decisions/*.md"],
                                     topic="architecture", adr_status="active")
        self.assertEqual(len(result["files"]), 4)
        self.assertIn("unknown", {f["adr"]["status"] for f in result["files"]})
        self.assertEqual(safety.adr_metadata(fixtures["0001-a.md"])["date"], "2026-06-12")
        self.assertEqual(safety.adr_metadata(fixtures["0002-b.md"])["status"], "accepted")

    def test_warm_recipe_executes_selector_not_shell_input(self):
        body = (SOURCE / "skills/context-warm/SKILL.md").read_text(encoding="utf-8")
        script = self.base / "warm.sh"
        script.write_text(re.search(r"```bash\n(.*?)\n```", body, re.S)[1], encoding="utf-8")
        env = dict(os.environ, LINTEL_SOURCE_ROOT=str(SOURCE), LINTEL_REPO_ROOT=str(self.root),
                   LINTEL_HOME=str(self.base / "home"), PYTHONDONTWRITEBYTECODE="1")
        outcome = subprocess.run(["bash", str(script), "--path", "docs/one file.md"],
                                 env=env, capture_output=True, text=True)
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        self.assertEqual(json.loads(outcome.stdout)["files"][0]["path"], "docs/one file.md")
        rejected = subprocess.run(["bash", str(script), "--glob", "$(touch injected);*.md"],
                                  env=env, capture_output=True, text=True)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertFalse((self.root / "injected").exists())

    def test_budget_perf_and_cool_recipes_invoke_the_actual_reader(self):
        env = dict(os.environ, LINTEL_SOURCE_ROOT=str(SOURCE), LINTEL_REPO_ROOT=str(self.root),
                   LINTEL_HOME=str(self.base / "home"), PYTHONDONTWRITEBYTECODE="1")
        for name, args in (("context-budget", ["--bytes", "400"]),
                           ("perf-mode", ["--budget", "800000", "--cost-estimate"]),
                           ("context-cool", ["--path", "docs/two.md"])):
            with self.subTest(name=name):
                body = (SOURCE / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                script = self.base / (name + ".sh")
                script.write_text(re.search(r"```bash\n(.*?)\n```", body, re.S)[1], encoding="utf-8")
                run = subprocess.run(["bash", str(script), *args], env=env, capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                result = json.loads(run.stdout)
                if name == "context-cool":
                    self.assertEqual(result["tokens_removed_from_context"], 0)
                    self.assertEqual(safety.select_files(self.root, paths=["docs/two.md"],
                                     exclude_file=self.root / ".claude/runtime/state/context-ignore.json")["files"], [])
                else:
                    self.assertIsNone(result["capacity_tokens"])
                    self.assertIsNone(result["headroom_tokens"])

    def test_adr_and_related_recipes_preserve_scoped_selection(self):
        adrs = self.root / ".claude/decisions"
        adrs.mkdir(parents=True)
        (adrs / "0001-design notes.md").write_text("# ADR: Architecture\n**Status:** Accepted\n")
        env = dict(os.environ, LINTEL_SOURCE_ROOT=str(SOURCE), LINTEL_REPO_ROOT=str(self.root),
                   LINTEL_HOME=str(self.base / "home"), PYTHONDONTWRITEBYTECODE="1")
        for name, args in (("context-warm-related", ["architecture", "docs/*.md", "1"]),
                           ("context-warm-adrs", ["architecture", "accepted"])):
            body = (SOURCE / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            script = self.base / (name + ".sh")
            script.write_text(re.search(r"```bash\n(.*?)\n```", body, re.S)[1], encoding="utf-8")
            # Quote globs inside Bash; native Windows -> MSYS startup can expand raw argv.
            env.update(FIXTURE_SCRIPT=str(script), FIXTURE_TOPIC=args[0],
                       FIXTURE_PATTERN=args[1], FIXTURE_LIMIT=args[2] if len(args) > 2 else "10")
            run = subprocess.run(["bash", "-c",
                                  'bash "$FIXTURE_SCRIPT" "$FIXTURE_TOPIC" "$FIXTURE_PATTERN" "$FIXTURE_LIMIT"'],
                                 env=env, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(run.stdout)
            self.assertEqual(len(result["files"]), 1)
            self.assertEqual(result["source_root"], str(self.root))

    def test_partial_migration_gate_does_not_auto_undo_unknown_states(self):
        body = (SOURCE / "agents/engineering/Migrator.md").read_text(encoding="utf-8")
        recipe = re.search(r"```bash\n(# lintel-migration-recovery-gate.*?)\n```", body, re.S)
        self.assertIsNotNone(recipe)
        script = self.base / "migration-gate.sh"
        script.write_text(recipe[1] + '\nmigration_recovery_allowed "$@"\n', encoding="utf-8")
        target = self.root / "b-partial.txt"
        target.write_text("partial local migration; user state retained")
        for args, allowed in (
                (["step-2", "step-2", "verified", "exact-scope", "none"], True),
                (["step-2", "unknown", "verified", "exact-scope", "none"], False),
                (["step-2", "step-2", "unverified", "exact-scope", "none"], False),
                (["step-2", "step-2", "verified", "other-target", "none"], False),
                (["step-2", "step-2", "verified", "exact-scope", "possible-live-write"], False)):
            result = subprocess.run(["bash", str(script), *args], capture_output=True)
            self.assertEqual(result.returncode == 0, allowed)
            self.assertEqual(target.read_text(), "partial local migration; user state retained")
        self.assertEqual((self.root / "unrelated.txt").read_text(), "keep this")

    def test_isolated_bisect_recipe_preserves_dirty_source_on_success_and_error(self):
        env = dict(os.environ, HOME=str(self.base), GIT_CONFIG_NOSYSTEM="1",
                   GIT_CONFIG_GLOBAL=str(self.base / "no-global-config"))

        def git(*args):
            result = subprocess.run(["git", "-C", str(self.root), *args], env=env,
                                    capture_output=True, check=True)
            return result.stdout

        git("init", "-q")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        git("config", "core.hooksPath", str(self.base / "no-hooks"))
        git("config", "core.autocrlf", "false")
        target = self.root / "value.txt"
        target.write_text("good\n")
        git("add", "value.txt")
        git("commit", "-qm", "good")
        good = git("rev-parse", "HEAD").decode().strip()
        target.write_text("bad\n")
        git("commit", "-qam", "bad")
        bad = git("rev-parse", "HEAD").decode().strip()
        target.write_text("user staged\n")
        git("add", "value.txt")
        target.write_text("user unstaged\n")
        before = (git("status", "--porcelain=v1", "-z"), git("diff", "--binary"),
                  git("diff", "--cached", "--binary"), git("rev-parse", "HEAD"))
        body = (SOURCE / "agents/engineering/RegressionDetective.md").read_text(encoding="utf-8")
        recipe = re.search(r"```bash\n(# lintel-isolated-bisect.*?)\n```", body, re.S)
        self.assertIsNotNone(recipe)
        script = self.base / "bisect.sh"
        script.write_text(recipe[1], encoding="utf-8")
        repro = self.base / "repro.sh"
        repro.write_text('test "$(cat value.txt)" = good\n')
        for name, command, expected in (("success", repro, 0), ("failure", self.base / "missing", 1)):
            trial = self.base / ("trial-" + name)
            result = subprocess.run(["bash", str(script), str(self.root), bad, good,
                                     str(command), str(trial)], env=env, capture_output=True)
            self.assertEqual(result.returncode == 0, expected == 0, result.stderr)
            self.assertTrue(trial.is_dir(), "trial evidence is retained, not force-removed")
            trial_head = subprocess.run(["git", "-C", str(trial), "rev-parse", "HEAD"],
                                        env=env, capture_output=True, check=True).stdout
            self.assertEqual(trial_head.decode().strip(), bad)
            for name in ("BISECT_START", "BISECT_LOG"):
                path = subprocess.run(["git", "-C", str(trial), "rev-parse", "--git-path", name],
                                      env=env, capture_output=True, check=True).stdout.decode().strip()
                self.assertFalse(Path(path).exists(), f"bisect state not cleared: {name}")
            refs = subprocess.run(["git", "-C", str(trial), "for-each-ref", "refs/bisect"],
                                  env=env, capture_output=True, check=True)
            self.assertEqual(refs.stdout, b"")
            self.assertEqual(before, (git("status", "--porcelain=v1", "-z"), git("diff", "--binary"),
                                      git("diff", "--cached", "--binary"), git("rev-parse", "HEAD")))
            self.assertEqual((self.root / "unrelated.txt").read_text(), "keep this")
            git("worktree", "remove", str(trial))


if __name__ == "__main__":
    unittest.main(verbosity=2)
