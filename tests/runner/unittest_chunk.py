#!/usr/bin/env python3
# component: unittest-chunk
# implements: ADR-0041
# intent: .claude/decisions/0041-weighted-shards-kit-chunks-pr-cancellation.md
# constraints: Python 3.9+ standard library only; selects among a module's own tests and never adds, skips or rewrites one
# last_intent_review: 2026-09-29
"""Run or list one deterministic chunk of a unittest module's tests.

usage: python unittest_chunk.py MODULE.py [--list | unittest arguments ...]

Without LINTEL_TEST_CHUNK the module's tests run through unittest.main at verbosity 2 with the given
arguments, so test names and -k patterns work and the tests and results are those of
`python MODULE.py [arguments]`. The process is not identical to that direct run: the module is
imported under its file stem rather than as __main__ (test ids change accordingly), sys.argv starts
with this helper, sys.path also holds this helper's directory, and no bytecode is written.
`--list` prints every test id, sorted.

With LINTEL_TEST_CHUNK=K/N (1 <= K <= N) the module's tests are sorted by id, and the chunk holds the
tests at zero-based positions i with i mod N == K - 1. The chunk runs through the same unittest text
runner; `--list` prints its ids and runs nothing. A malformed value, an empty chunk, a chunk combined
with unittest arguments, or `--list` combined with anything else exits 2 before any test runs, so a
chunk never narrows silently.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import re
import sys
from typing import Iterator, NoReturn
import unittest

# Loading the module by path must not leave a __pycache__ beside it; running it directly does not.
sys.dont_write_bytecode = True
VARIABLE = "LINTEL_TEST_CHUNK"
USAGE = "usage: unittest_chunk.py MODULE.py [--list | unittest arguments ...]"
_CHUNK = re.compile(r"([1-9][0-9]*)/([1-9][0-9]*)")


def refuse(message: str) -> NoReturn:
    print(f"unittest_chunk: {message}", file=sys.stderr)
    raise SystemExit(2)


def parse_chunk(value: str) -> tuple[int, int]:
    match = _CHUNK.fullmatch(value)
    if match is None or int(match.group(1)) > int(match.group(2)):
        refuse(f"{VARIABLE} must be K/N with 1 <= K <= N and no leading zeros, got {value!r}")
    return int(match.group(1)), int(match.group(2))


def load_module(path: Path):
    """Import the module by path, with its directory first on sys.path as `python MODULE.py` has it."""
    name = re.sub(r"\W", "_", path.stem)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        refuse(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def flatten(suite: unittest.TestSuite) -> Iterator[unittest.TestCase]:
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


class ChunkLoader(unittest.TestLoader):
    """Load a module's tests, sorted by id, and keep only one chunk of them."""

    def __init__(self, index: int, count: int) -> None:
        super().__init__()
        self.index, self.count = index, count

    def loadTestsFromModule(self, module, *args, **kwargs):  # noqa: N802 - the unittest API name
        tests = sorted(flatten(super().loadTestsFromModule(module, *args, **kwargs)), key=lambda test: test.id())
        return self.suiteClass(test for position, test in enumerate(tests) if position % self.count == self.index - 1)


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments or arguments[0].startswith("-"):
        refuse(USAGE)
    path, rest = Path(arguments[0]), arguments[1:]
    if not path.is_file():
        refuse(f"no test module at {path}")
    listing = rest == ["--list"]
    if "--list" in rest and not listing:
        refuse("--list takes no other arguments")
    raw = os.environ.get(VARIABLE)
    chunk = None if raw is None else parse_chunk(raw)
    if chunk is not None and rest and not listing:
        refuse(f"{VARIABLE}={raw} cannot be combined with unittest arguments {rest}; a chunk is never narrowed further")
    path = path.resolve()
    module = load_module(path)
    loader = unittest.defaultTestLoader if chunk is None else ChunkLoader(*chunk)
    if chunk is not None or listing:
        selected = sorted(flatten(loader.loadTestsFromModule(module)), key=lambda test: test.id())
        if chunk is not None and not selected:
            total = sum(1 for _ in flatten(unittest.defaultTestLoader.loadTestsFromModule(module)))
            refuse(f"chunk {chunk[0]}/{chunk[1]} of {path.name} is empty; the module has {total} tests")
        if listing:
            for test in selected:
                print(test.id())
            return 0
    # unittest.main, as a direct run calls it: text runner, verbosity 2 and unittest's exit status.
    unittest.main(module=module, argv=[str(path), *([] if chunk else rest)], testLoader=loader, verbosity=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
