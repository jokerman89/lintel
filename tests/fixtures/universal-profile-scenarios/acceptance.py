# component: p14-inventory-acceptance
# implements: ADR-0026, ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P14.md
# constraints: finite synthetic local oracle; no supplied implementation or native verdict
# last_intent_review: 2026-09-23
"""Frozen business oracle and policy-approved local publication-failure probe."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


SENTINEL = b"previous-output-must-survive\n"
SEED = Path(__file__).parent / "seed" / "data" / "events.jsonl"
SEED_RESULT = {
    "unique_events": 6,
    "stock": [
        {"sku": "BOLT", "quantity": 5},
        {"sku": "NUT", "quantity": -2},
        {"sku": "WASHER", "quantity": 0},
    ],
}
OPTIONS = None


def assert_stock(test: unittest.TestCase, data: bytes, expected: dict) -> None:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            test.assertNotIn(key, result, "duplicate output key")
            result[key] = value
        return result

    value = json.loads(data.decode("utf-8"), object_pairs_hook=unique)
    test.assertIsInstance(value, dict)
    test.assertEqual(set(value), {"unique_events", "stock"})
    test.assertIs(type(value["unique_events"]), int)
    test.assertIsInstance(value["stock"], list)
    for row in value["stock"]:
        test.assertIsInstance(row, dict)
        test.assertEqual(set(row), {"sku", "quantity"})
        test.assertIs(type(row["quantity"]), int)
    test.assertEqual(value, expected)


def assert_refusal(test: unittest.TestCase, result, output: bytes) -> None:
    test.assertNotEqual(result.returncode, 0)
    test.assertTrue(result.stderr.strip(), "refusal needs a useful diagnostic")
    test.assertEqual(output, SENTINEL, "refusal replaced existing output")


def lines(records) -> bytes:
    return b"".join((json.dumps(row, separators=(",", ":")) + "\n").encode()
                    for row in records)


ATOMIC_DRIVER = r"""
import hashlib, json, os, pathlib, runpy, sys
program, source, output, fault = sys.argv[1:]
destination = pathlib.Path(output).resolve()
replace = os.replace
def observed_replace(src, dst, *args, **kwargs):
    if pathlib.Path(dst).resolve() == destination:
        staged = pathlib.Path(src).read_bytes()
        print("P14_REPLACE " + json.dumps({
            "same_parent": pathlib.Path(src).resolve().parent == destination.parent,
            "bytes": len(staged), "sha256": hashlib.sha256(staged).hexdigest()
        }), file=sys.stderr, flush=True)
        if fault == "fail":
            raise OSError("P14 injected failure before replacement")
    return replace(src, dst, *args, **kwargs)
os.replace = observed_replace
sys.argv = [program, "--input", source, "--output", output]
runpy.run_path(program, run_name="__main__")
"""


class ProgramCase(unittest.TestCase):
    counter = 0

    def invoke(self, data: bytes, *, missing=False, alias=False, atomic=None):
        ProgramCase.counter += 1
        directory = OPTIONS.scratch / f"case-{ProgramCase.counter:03d}"
        directory.mkdir()
        source, output = directory / "events.jsonl", directory / "stock.json"
        if not missing:
            source.write_bytes(data)
        output.write_bytes(SENTINEL)
        if alias:
            output = source
        command = [sys.executable, "-I", "-B"]
        if atomic:
            command += ["-c", ATOMIC_DRIVER, str(OPTIONS.program), str(source),
                        str(output), atomic]
        else:
            command += [str(OPTIONS.program), "--input", str(source), "--output", str(output)]
        before = source.read_bytes() if source.exists() else None
        with (directory / "stdout.log").open("xb") as stdout, \
                (directory / "stderr.log").open("xb") as stderr:
            completed = subprocess.run(command, cwd=directory, env=dict(os.environ),
                                       stdout=stdout, stderr=stderr, timeout=30, check=False)
        result = subprocess.CompletedProcess(
            command, completed.returncode,
            (directory / "stdout.log").read_text(encoding="utf-8"),
            (directory / "stderr.log").read_text(encoding="utf-8"),
        )
        (directory / "exit.txt").write_text(str(result.returncode) + "\n", encoding="ascii")
        self.assertEqual(source.read_bytes() if source.exists() else None, before,
                         "input bytes changed")
        return result, output.read_bytes()

    def accepted(self, data, expected):
        result, output = self.invoke(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        assert_stock(self, output, expected)
        return output

    def rejected(self, data):
        result, output = self.invoke(data)
        assert_refusal(self, result, output)


class Business(ProgramCase):
    def test_seed(self):
        self.accepted(SEED.read_bytes(), SEED_RESULT)

    def test_order_independent_bytes(self):
        original = SEED.read_bytes()
        forward = self.accepted(original, SEED_RESULT)
        backward = self.accepted(b"\n".join(reversed(original.splitlines())) + b"\n", SEED_RESULT)
        self.assertEqual(forward, backward)

    def test_identical_repeat(self):
        self.accepted(SEED.read_bytes() * 3, SEED_RESULT)

    def test_conflicting_repeat(self):
        for row in (
            {"event_id": "evt-01", "sku": "BOLT", "delta": 9},
            {"event_id": "evt-01", "sku": "OTHER", "delta": 8},
        ):
            with self.subTest(row=row):
                self.rejected(SEED.read_bytes() + lines([row]))

    def test_malformed_json_and_duplicate_keys(self):
        for data in (b"{\n", b"[]\n",
                     b'{"event_id":"x","event_id":"y","sku":"A","delta":1}\n',
                     b'{"event_id":"x","sku":"A","delta":NaN}\n'):
            with self.subTest(data=data):
                self.rejected(data)

    def test_fields_and_integer_type(self):
        base = {"event_id": "valid", "sku": "A", "delta": 1}
        invalid = [{key: value for key, value in base.items() if key != missing}
                   for missing in base]
        invalid.append({**base, "extra": 1})
        invalid.extend({**base, "delta": value}
                       for value in (True, False, None, "1", 1.5, 1000001, -1000001))
        for row in invalid:
            with self.subTest(row=row):
                self.rejected(lines([row]))

    def test_identifiers(self):
        for key, values in (
            ("event_id", ("", "Bad", "has space", "x" * 33, 1)),
            ("sku", ("", "lower", "A B", "X" * 17, None)),
        ):
            for value in values:
                with self.subTest(key=key, value=value):
                    row = {"event_id": "valid", "sku": "A", "delta": 1, key: value}
                    self.rejected(lines([row]))

    def test_empty_and_blank(self):
        for data in (b"", b"\n", SEED.read_bytes() + b"\n"):
            with self.subTest(data=data):
                self.rejected(data)

    def test_inclusive_line_and_number_bounds(self):
        rows = [{"event_id": f"evt-{i}", "sku": "A", "delta": 1000000}
                for i in range(1000)]
        self.accepted(lines(rows), {
            "unique_events": 1000, "stock": [{"sku": "A", "quantity": 1000000000}],
        })
        self.rejected(lines(rows + [rows[0]]))
        self.accepted(lines([{"event_id": "evt-min", "sku": "Z", "delta": -1000000}]), {
            "unique_events": 1, "stock": [{"sku": "Z", "quantity": -1000000}],
        })

    def test_missing_input(self):
        result, output = self.invoke(b"", missing=True)
        assert_refusal(self, result, output)

    def test_input_output_alias(self):
        original = SEED.read_bytes()
        result, output = self.invoke(original, alias=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip())
        self.assertEqual(output, original)


class AtomicPublication(ProgramCase):
    def event(self, result):
        events = [json.loads(line.removeprefix("P14_REPLACE "))
                  for line in result.stderr.splitlines() if line.startswith("P14_REPLACE ")]
        self.assertEqual(len(events), 1, "exactly one observed output replacement required")
        self.assertIs(events[0]["same_parent"], True)
        self.assertGreater(events[0]["bytes"], 0)
        return events[0]

    def test_complete_sibling_publication(self):
        result, output = self.invoke(SEED.read_bytes(), atomic="observe")
        self.assertEqual(result.returncode, 0, result.stderr)
        event = self.event(result)
        self.assertNotEqual(output, SENTINEL)
        self.assertEqual(hashlib.sha256(output).hexdigest(), event["sha256"])
        self.assertEqual(len(output), event["bytes"])

    def test_failure_before_replace_preserves_prior_output(self):
        result, output = self.invoke(SEED.read_bytes(), atomic="fail")
        self.event(result)
        assert_refusal(self, result, output)


class OracleSelfChecks(unittest.TestCase):
    def test_output_shape_and_values_discriminate(self):
        assert_stock(self, json.dumps(SEED_RESULT).encode(), SEED_RESULT)
        wrong = [
            {**SEED_RESULT, "unique_events": 7},
            {**SEED_RESULT, "extra": "not allowed"},
            {"unique_events": 6, "stock": list(reversed(SEED_RESULT["stock"]))},
            {"unique_events": 6, "stock": [{"sku": "BOLT", "quantity": True}]},
        ]
        for value in wrong:
            with self.subTest(value=value), self.assertRaises(AssertionError):
                assert_stock(self, json.dumps(value).encode(), SEED_RESULT)
        with self.assertRaises(AssertionError):
            assert_stock(self, b'{"unique_events":6,"unique_events":6,"stock":[]}', SEED_RESULT)

    def test_refusal_needs_exit_diagnostic_and_preservation(self):
        good = subprocess.CompletedProcess(["synthetic-oracle-unit"], 2, "", "invalid record")
        assert_refusal(self, good, SENTINEL)
        for result, output in (
            (subprocess.CompletedProcess([], 0, "", "invalid"), SENTINEL),
            (subprocess.CompletedProcess([], 2, "", ""), SENTINEL),
            (good, b"clobbered"),
        ):
            with self.subTest(result=result, output=output), self.assertRaises(AssertionError):
                assert_refusal(self, result, output)


def main() -> int:
    global OPTIONS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--program", type=Path)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--group", choices=("self", "business", "atomic"), required=True)
    OPTIONS = parser.parse_args()
    root_value = os.environ.get("P14_ISOLATION_ROOT")
    if not root_value:
        parser.error("An inspected P14_ISOLATION_ROOT is required")
    root = Path(root_value).resolve()
    OPTIONS.scratch = OPTIONS.scratch.resolve()
    if root == Path(root.anchor) or not OPTIONS.scratch.is_relative_to(root):
        parser.error("scratch must be within the explicit synthetic root")
    for key in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP",
                "TMPDIR", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "LINTEL_HOME"):
        if not os.environ.get(key) or not Path(os.environ[key]).resolve().is_relative_to(root):
            parser.error(f"{key} must be explicitly synthetic")
    if OPTIONS.group != "self":
        if OPTIONS.program is None:
            parser.error("--program is required for program acceptance")
        OPTIONS.program = OPTIONS.program.resolve()
        if not OPTIONS.program.is_relative_to(root) or not OPTIONS.program.is_file():
            parser.error("program must be an existing synthetic-root file")
    OPTIONS.scratch.mkdir(exist_ok=False)
    case = {"self": OracleSelfChecks, "business": Business, "atomic": AtomicPublication}[OPTIONS.group]
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(case)
    with (OPTIONS.scratch / "oracle.log").open("x", encoding="utf-8") as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    sys.stderr.write((OPTIONS.scratch / "oracle.log").read_text(encoding="utf-8"))
    print(json.dumps({"category": "local-oracle", "group": OPTIONS.group,
                      "tests": result.testsRun, "failures": len(result.failures),
                      "errors": len(result.errors), "skipped": len(result.skipped),
                      "native_scenario": False}))
    return 0 if result.testsRun and not result.skipped and result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
