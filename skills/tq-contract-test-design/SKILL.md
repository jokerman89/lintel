---
name: tq-contract-test-design
layer: foundation
description: TQ sub-skill — consumer-driven contract tests + schema-versioning tests. Dispatches to APIDesigner + ContractTestArchitect (NEW).
color: green
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are TQ-CONTRACT-TEST-DESIGN — the workflow that produces a contract test suite.

## What this skill does

Reads API design (from TA api-design or `dh-deployment-plan` cutover) + consumer registry. Spawns `APIDesigner` to enumerate contract surface and `ContractTestArchitect` (new in v4.5) to design consumer-driven tests + schema-versioning tests. Produces contract-test-suite covering consumer expectations, provider responses, schema-version compatibility, and Pact-style verification.

## When to use

- TQ full pass contract_tests_complete checkpoint
- Single action `/li:tq single --action contract-test-design`
- Pre-release contract verification
- New API consumer onboarding

## When NOT to use

- Single-endpoint contract test (write inline)
- Internal-only API without consumers (no contract concern)

## Workflow

### Step 1 — Read context

```bash
contract_test_framework="${framework:-${contract_test_framework:-pact}}"   # pact | consumer-driven-internal | none
api_design=$(find .lintel/state/ta -name "api-design-*.md" -mtime -30 2>/dev/null | sort | tail -1)
consumer_registry=".lintel/state/ta/consumer-registry.json"
```

### Step 2 — Spawn APIDesigner for contract surface

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Enumerate contract surface (endpoints + payloads + versions)
context_pointers:
  - $api_design
  - $consumer_registry (if present)
constraints:
  - per endpoint: request schema, response schema, error schemas, versions in flight
  - per consumer (if registry present): which contract version they use
acceptance:
  - structured contract enumeration
EOF

/li:brief-forge subagent_spawn tq-contract-test-design APIDesigner brief "$brief_file"
```

### Step 3 — Spawn ContractTestArchitect for test design

```bash
test_brief=$(mktemp)
cat > "$test_brief" <<EOF
task: Design consumer-driven contract tests using ${contract_test_framework}
context_pointers:
  - .lintel/state/tq/contract-surface.md
constraints:
  - per consumer-provider pair: consumer expectation + provider verification
  - schema-versioning tests: compatibility matrix across active versions
  - framework conventions: ${contract_test_framework} idioms
acceptance:
  - per-pair test spec + version compatibility matrix
EOF

/li:brief-forge subagent_spawn tq-contract-test-design ContractTestArchitect brief "$test_brief"
```

### Step 4 — Raise-help on active-consumer break

```bash
active_consumer_break=$(jq -r '.contracts[] | select(.breaks_active_consumer == true) | .name' .lintel/state/tq/contract-tests.json 2>/dev/null | wc -l)
if [ "$active_consumer_break" -gt 0 ]; then
  echo "RAISE_HELP: $active_consumer_break contract test(s) break against active consumer"
fi
```

### Step 5 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/tq/contract-test-suite-$ts.md"
{
  echo "# Contract test suite — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "## Framework: $contract_test_framework"
  echo ""
  echo "## Contract surface"
  cat .lintel/state/tq/contract-surface.md
  echo ""
  echo "## Tests + version matrix"
  cat .lintel/state/tq/contract-tests.md
} > "$out"

printf '{"ts":"%s","kind":"tq_contract_test_design","framework":"%s","contracts":%d,"breaks_active":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$contract_test_framework" "$contract_count" "$active_consumer_break" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/tq-decisions.jsonl"
```

## Status protocol

- **DONE** — suite emitted, all active consumers pass
- **DONE_WITH_CONCERNS** — emitted but 1-2 deprecated-version tests skipped
- **BLOCKED** — raise-help triggered (active-consumer break)

## Integration

**Reads:** TA api-design, consumer registry, profile preferences
**Writes:** `.lintel/state/tq/contract-test-suite-<ts>.md`, audit JSONL
**Dispatches to:** APIDesigner (surface), ContractTestArchitect (NEW, test design)
**Hook integration:** `tq-contract-break-warn` hook fires pre-commit on provider changes breaking consumer contracts

## Anti-patterns

- **Provider-only tests** — consumer-driven catches breaks the provider didn't expect
- **Single-version contract tests** — version compatibility matrix is what catches breaks
- **Hardcoding framework** — read from profile (pact | consumer-driven-internal | none)
- **Curating contract patterns** — agents reason from surface (L-001)
