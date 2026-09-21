#!/usr/bin/env python3
# component: owned-file-transaction-entry
# implements: ADR-0030
# intent: .claude/plans/universal-implementation/packages/P10.md
# constraints: inspect/recover explicit owned receipts; never used by bare installation
# last_intent_review: 2026-09-20
"""Inspect or explicitly recover an owned Python-runtime file transaction."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from managed_transaction import inspect_transaction, recover_transaction


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("inspect", "recover"))
    parser.add_argument("id")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--store", type=Path, required=True)
    args = parser.parse_args()
    try:
        operation = inspect_transaction if args.operation == "inspect" else recover_transaction
        print(json.dumps(operation(args.root, args.store, args.id), indent=2))
        return 0
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(f"li-managed-transaction: {error}. Preserve the target and recovery evidence.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
