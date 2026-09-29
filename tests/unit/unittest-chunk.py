# component: unittest-chunk-test
# implements: ADR-0041
# intent: .claude/decisions/0041-weighted-shards-kit-chunks-pr-cancellation.md
# constraints: temporary fixture modules; lists the Copilot kit's chunks through its real wrappers without running them
# last_intent_review: 2026-09-29
from __future__ import annotations

import importlib.util
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
HELPER = ROOT / "tests" / "runner" / "unittest_chunk.py"
INTEGRATION = ROOT / "tests" / "integration"
KIT = INTEGRATION / "copilot-kit.py"
SCOPES = ("unit", "behavior", "integration", "e2e", "shape")
VARIABLE = "LINTEL_TEST_CHUNK"

FIXTURE = '''import unittest


class Alpha(unittest.TestCase):
    def test_a(self):
        pass

    def test_b(self):
        pass

    def test_c(self):
        pass


class Beta(unittest.TestCase):
    def test_d(self):
        pass

    @unittest.skip("platform: windows-only; fixture")
    def test_e(self):
        pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
'''
FAILING = '''import unittest


class Gamma(unittest.TestCase):
    def test_1_passes(self):
        pass

    def test_2_fails(self):
        self.fail("planted failure")


if __name__ == "__main__":
    unittest.main(verbosity=2)
'''


def environment(chunk=None):
    env = {key: value for key, value in os.environ.items() if key != VARIABLE}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if chunk is not None:
        env[VARIABLE] = chunk
    return env


def run(arguments, chunk=None, cwd=None):
    return subprocess.run([sys.executable, str(HELPER), *map(str, arguments)], env=environment(chunk), cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8")


def listed(result):
    return [line for line in result.stdout.splitlines() if line.strip()]


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def short(test_id):
    """Drop the module component, which depends on how the module was loaded."""
    return test_id.split(".", 1)[1]


class HelperContract(unittest.TestCase):
    """The selector itself: exact partitions, unchanged unset behavior, explicit refusals."""

    @classmethod
    def setUpClass(cls):
        cls.sandbox = tempfile.TemporaryDirectory(prefix="lintel-unittest-chunk-")
        base = Path(cls.sandbox.name)
        cls.module = base / "fixture_mod.py"
        cls.module.write_text(FIXTURE, encoding="utf-8")
        cls.failing = base / "failing_mod.py"
        cls.failing.write_text(FAILING, encoding="utf-8")
        cls.ids = ["fixture_mod.Alpha.test_a", "fixture_mod.Alpha.test_b", "fixture_mod.Alpha.test_c",
                   "fixture_mod.Beta.test_d", "fixture_mod.Beta.test_e"]

    @classmethod
    def tearDownClass(cls):
        cls.sandbox.cleanup()

    def assert_refused(self, result, needle):
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(needle, result.stderr)
        self.assertNotIn("Ran ", result.stdout + result.stderr, "a refusal must not run any test")

    def test_list_without_a_chunk_prints_every_id_sorted(self):
        result = run([self.module, "--list"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(listed(result), self.ids)

    def test_chunks_are_the_sorted_ids_by_index_modulo(self):
        for count in range(1, 6):
            union = []
            for index in range(1, count + 1):
                with self.subTest(chunk=f"{index}/{count}"):
                    result = run([self.module, "--list"], chunk=f"{index}/{count}")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    expected = [test for position, test in enumerate(self.ids) if position % count == index - 1]
                    self.assertEqual(listed(result), expected)
                    union.extend(listed(result))
            self.assertEqual(sorted(union), self.ids, f"chunks of {count} must cover every test exactly once")

    def test_malformed_values_refuse_before_any_test_runs(self):
        for value in ("", "0/2", "3/2", "x", "1/0", "01/2", "1/02", "1/2/3", " 1/2", "1 /2", "1/2 ", "-1/2", "1-2"):
            with self.subTest(value=value):
                self.assert_refused(run([self.module], chunk=value), VARIABLE)
                self.assert_refused(run([self.module, "--list"], chunk=value), VARIABLE)

    def test_an_empty_chunk_refuses(self):
        self.assert_refused(run([self.module], chunk="6/6"), "is empty")
        self.assert_refused(run([self.module, "--list"], chunk="6/6"), "is empty")
        self.assertEqual(run([self.module, "--list"], chunk="5/6").returncode, 0)

    def test_a_chunk_runs_only_its_tests_through_the_verbose_text_runner(self):
        result = run([self.module], chunk="1/2")
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("Ran 3 tests", output)
        self.assertIn("OK (skipped=1)", output)
        self.assertIn("... skipped 'platform: windows-only; fixture'", output)
        self.assertEqual(sorted(re.findall(r"^(test_\w+) ", output, re.M)), ["test_a", "test_c", "test_e"])

    def test_without_a_chunk_the_module_runs_as_it_does_directly(self):
        through = run([self.module])
        direct = subprocess.run([sys.executable, str(self.module)], env=environment(), capture_output=True,
                                text=True, encoding="utf-8")
        for result in (through, direct):
            output = result.stdout + result.stderr
            with self.subTest(command=result.args):
                self.assertEqual(result.returncode, 0, output)
                self.assertIn("Ran 5 tests", output)
                self.assertIn("OK (skipped=1)", output)
        verdicts = [re.findall(r"^(test_\w+) .* \.\.\. (\w+)", r.stdout + r.stderr, re.M) for r in (through, direct)]
        self.assertEqual(verdicts[0], verdicts[1])

    def test_without_a_chunk_explicit_selectors_are_kept(self):
        result = run([self.module, "Alpha.test_b"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ran 1 test", result.stderr)
        self.assertIn("test_b", result.stderr)
        result = run([self.module, "-k", "test_d"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ran 1 test", result.stderr)
        self.assertIn("test_d", result.stderr)

    def test_a_chunk_is_never_narrowed_by_selectors_or_options(self):
        for extra in (["Alpha.test_b"], ["-k", "test_a"], ["-f"]):
            with self.subTest(extra=extra):
                self.assert_refused(run([self.module, *extra], chunk="1/2"), "cannot be combined")

    def test_list_takes_no_other_arguments(self):
        self.assert_refused(run([self.module, "--list", "Alpha.test_b"]), "--list takes no other arguments")
        self.assert_refused(run([self.module, "Alpha.test_b", "--list"], chunk="1/2"), "--list takes no other")

    def test_usage_errors_refuse(self):
        self.assert_refused(run([]), "usage:")
        self.assert_refused(run(["--list", self.module]), "usage:")
        self.assert_refused(run([self.module.with_name("missing.py")]), "no test module")

    def test_failures_keep_unittest_exit_status(self):
        failing = run([self.failing], chunk="2/2")
        self.assertEqual(failing.returncode, 1, failing.stdout + failing.stderr)
        self.assertIn("FAILED (failures=1)", failing.stderr)
        passing = run([self.failing], chunk="1/2")
        self.assertEqual(passing.returncode, 0, passing.stdout + passing.stderr)

    def test_loading_by_path_leaves_no_bytecode_beside_the_module(self):
        env = environment()
        env.pop("PYTHONDONTWRITEBYTECODE", None)
        result = subprocess.run([sys.executable, str(HELPER), str(self.module), "--list"], env=env,
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.module.parent / "__pycache__").exists())


class CopilotKitChunks(unittest.TestCase):
    """The kit's wrappers are one complete, disjoint cover of its tests, listed through the real entries."""

    @classmethod
    def setUpClass(cls):
        cls.wrappers = sorted(INTEGRATION.glob("copilot-kit-*.sh"))
        cls.chunks = {}
        for wrapper in cls.wrappers:
            text = wrapper.read_text(encoding="utf-8")
            found = re.findall(r"LINTEL_TEST_CHUNK=([1-9][0-9]*)/([1-9][0-9]*) ", text)
            cls.chunks[wrapper.name] = (text, found)

    def test_wrappers_are_exactly_one_to_n(self):
        counts, indexes = set(), []
        for name, (text, found) in self.chunks.items():
            with self.subTest(wrapper=name):
                self.assertEqual(len(found), 1, "each wrapper selects exactly one chunk")
                index, count = map(int, found[0])
                self.assertEqual(name, f"copilot-kit-{index}.sh")
                self.assertIn('"$ROOT/tests/runner/unittest_chunk.py" "$ROOT/tests/integration/copilot-kit.py"', text)
                self.assertIn("# TAGS: integration,codex-compatible\n", text)
                self.assertRegex(text, r"(?m)^# SHARD-WEIGHT: [1-9][0-9]*$")
                self.assertNotIn("export LINTEL_TEST_CHUNK", text)
                counts.add(count)
                indexes.append(index)
        self.assertEqual(len(counts), 1, f"every wrapper must use the same chunk count, got {sorted(counts)}")
        count = counts.pop()
        self.assertGreater(count, 1)
        self.assertEqual(sorted(indexes), list(range(1, count + 1)))

    def test_no_other_discovered_entry_runs_the_kit(self):
        self.assertFalse((INTEGRATION / "copilot-kit.sh").exists(), "the unchunked entry must not be discovered")
        runners = sorted(
            path.relative_to(ROOT).as_posix()
            for scope in SCOPES for path in (ROOT / "tests" / scope).rglob("*.sh")
            if "copilot-kit.py" in path.read_text(encoding="utf-8", errors="replace"))
        self.assertEqual(runners, [path.relative_to(ROOT).as_posix() for path in self.wrappers])

    def test_the_module_still_runs_every_test_directly(self):
        self.assertTrue(KIT.read_text(encoding="utf-8").endswith(
            '\n\nif __name__ == "__main__":\n    unittest.main(verbosity=2)\n'))

    def test_listed_chunks_are_a_complete_disjoint_cover_of_discovery(self):
        # Discover the module independently of the helper's own loader and selection.
        spec = importlib.util.spec_from_file_location("copilot_kit_contract_discovery", KIT)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        discovered = [short(test.id()) for test in flatten(unittest.TestLoader().loadTestsFromModule(module))]
        self.assertGreater(len(discovered), 0)
        self.assertEqual(len(discovered), len(set(discovered)))
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(bash, "bash is required to run the wrappers")
        seen = {}
        for wrapper in self.wrappers:
            result = subprocess.run([bash, wrapper.as_posix(), "--list"], env=environment(), capture_output=True,
                                    text=True, encoding="utf-8")
            with self.subTest(wrapper=wrapper.name):
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn("Ran ", result.stdout + result.stderr, "--list must not run tests")
                chunk = [short(test_id) for test_id in listed(result)]
                self.assertTrue(chunk, "every chunk must be non-empty")
                for test in chunk:
                    self.assertNotIn(test, seen, f"{test} is listed by both {seen.get(test)} and {wrapper.name}")
                    seen[test] = wrapper.name
        self.assertEqual(sorted(seen), sorted(discovered),
                         f"the {len(self.wrappers)} chunks must list exactly the {len(discovered)} discovered tests")


if __name__ == "__main__":
    unittest.main(verbosity=2)
