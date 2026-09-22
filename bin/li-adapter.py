#!/usr/bin/env python3
# component: universal-repository-adapter-entry
# implements: ADR-0024, ADR-0025, ADR-0028
# intent: .claude/plans/universal-implementation/spec.md
# constraints: reuse the Copilot generator and ownership engine; repository-only
# last_intent_review: 2026-09-20
"""Repository-scoped Universal entry to the shared managed adapter installer."""
import importlib.util
from pathlib import Path
import sys


def main() -> None:
    path = Path(__file__).with_name("li-copilot.py")
    spec = importlib.util.spec_from_file_location("lintel_adapter", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load shared adapter generator: {path}")
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    adapter.main(universal=True)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
