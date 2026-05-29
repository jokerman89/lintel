# Shape-tests (Gate M3)

Per v4.0 design Chapter 4 §5.4 — Gate M3 of meta-infra mode.

Shape-tests verify the STRUCTURE of the repo, not the behavior of individual skills. They fire during REVIEW when a structural change is proposed (meta-infra mode) and as part of the standard test-suite to catch shape-drift over time.

## The 8 initial shape-tests (v4.0 Phase 1)

| Test | What it asserts |
|---|---|
| `frontmatter-lint-all.sh` | Every SKILL.md + agent .md has required frontmatter fields |
| `agents-categorized.sh` | Every agent declares matching `category:` field |
| `catalog-regenerates-clean.sh` | CATALOG.md regenerates idempotently |
| `deprecated-aliases-resolve.sh` | Every `deprecated_aliases` entry maps to a real new-name skill |
| `workflow-root-has-navigation.sh` | NEW v4.0: every `workflow_root: true` skill declares `navigation:` block |
| `brief-forge-handoffs-canonical.sh` | NEW v4.0: only `brief_forge_handoffs:` canonical name; no legacy `brief_forge:` |
| `pack-resolver-fallbacks.sh` | The 9-scenario harness from design §2.2 (delegates to tests/unit/) |
| `schema-versioned-contracts.sh` | Every contract JSON in `lib/`/`packs/` declares `schema_version` |

## How they fire

- **In standard test runner:** `bash tests/runner/run-all.sh --scope shape`
- **In meta-infra REVIEW:** Gate M3 invokes the suite when cycle mode = `meta-infra`
- **Pre-commit (optional):** operators can wire shape-tests into a pre-commit hook for the v4.x/ paths

## Adding a new shape-test

1. Create `tests/shape/<test-name>.sh` following the pattern below
2. Document what it asserts in this README
3. Reference it from the meta-infra Gate M3 spec

## Pattern

```bash
#!/usr/bin/env bash
# tests/shape/<test-name>.sh
# Asserts: <one-line description>
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/<test-name>.sh"
echo "============================"

# ... assertions ...

if [ "$FAILED" -eq 0 ]; then
  echo "All <test-name> assertions PASSED"
  exit 0
else
  echo "Some <test-name> assertions FAILED"
  exit 1
fi
```
