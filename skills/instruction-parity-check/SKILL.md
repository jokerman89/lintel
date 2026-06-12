---
name: instruction-parity-check
layer: foundation
description: Verifies substance-parity across 6 instruction files (root CLAUDE/AGENTS/GEMINI + shims). The multi-CLI promise's weak point per 6.2.
color: yellow
tools: Read, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `instruction-parity-check` skill — defender against drift between multi-CLI instruction files.

## What this skill does

Lintel ships 6 instruction files so different CLIs read the same Lintel rules:
- `CLAUDE.md` (claude-code root)
- `AGENTS.md` (codex root)
- `GEMINI.md` (gemini root)
- `.claude/AGENTS.md` (claude-code shim)
- `.codex/CLAUDE.md` (codex shim)
- `.github/copilot-instructions.md` (copilot)

Per v3.6 backlog 6.2: "They will drift — a Copilot colleague gets different rules than a Claude-Code colleague. This is the multi-CLI promise's weak point."

This skill compares substance-equivalence across the files + flags drift on 4 key sections:
1. **Compliance rules** (the active pack's compliance gates, data classification, customer-data block)
2. **Voice tier semantics** (internal vs the active pack's voice tier)
3. **Scaffolding principles** (L-001 + L-002 + L-003 reflected)
4. **Auto-mode boundaries** (what's OK without prompt, what needs auth)

## When to use

- **CI-integrated** — runs per push to main, flag if substance-drift > threshold
- **Pre-shipping multi-CLI feature** — verify all 6 files reflect change
- **Onboarding new CLI** — adding 7th instruction file: compare existing 6 first
- **Post-rename** — verify instructions follow Phase A / Phase B rename-discipline

## When NOT to use

- Hand-editing a single file — this skill READS, does not modify
- Diff-checking style/grammar — substance-comparison only
- Real-time live-comparison — this is a batch pass

## Workflow

### Step 1 — Locate all 6 instruction files

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
INSTR_FILES=(
  "$REPO_ROOT/CLAUDE.md"
  "$REPO_ROOT/AGENTS.md"
  "$REPO_ROOT/GEMINI.md"
  "$REPO_ROOT/.claude/AGENTS.md"
  "$REPO_ROOT/.codex/CLAUDE.md"
  "$REPO_ROOT/.github/copilot-instructions.md"
)

missing=0
for f in "${INSTR_FILES[@]}"; do
  [ -f "$f" ] || { echo "⚠ Missing: $f"; missing=$((missing+1)); }
done
[ "$missing" -gt 0 ] && echo "INCOMPLETE: $missing of 6 files missing"
```

### Step 2 — Extract key sections per file

For each file, parse section headers + canonical content:

```bash
extract_section() {
  local file="$1"
  local header_pattern="$2"
  awk -v pat="$header_pattern" '
    $0 ~ pat { capturing=1; print; next }
    /^## / && capturing { capturing=0 }
    capturing { print }
  ' "$file"
}

# Per-key-section extraction
for f in "${INSTR_FILES[@]}"; do
  compliance=$(extract_section "$f" "[Cc]ompliance|5\+7\+8")
  voice=$(extract_section "$f" "[Vv]oice [Tt]ier")
  scaffolding=$(extract_section "$f" "[Ss]caffolding|L-001|L-002|L-003")
  automode=$(extract_section "$f" "[Aa]uto.[Mm]ode|[Bb]oundaries")
  # Capture into per-section files for diff
done
```

### Step 3 — Cross-file substance-diff

For each of the 4 key sections:
1. Compute canonical form of text (lowercase + collapse whitespace + strip examples)
2. Pairwise diff: file A vs file B, A vs C, ..., E vs F
3. Score similarity (jaccard on 5-grams or equivalent)
4. Flag pairs with < 80% substance-similarity

### Step 4 — Surface drift report

```markdown
# Instruction Parity Report — <date>

## Summary
- 6/6 files present
- 4 key sections checked
- Drift detected: <N> pairs

## Section: Compliance rules
- CLAUDE.md ↔ AGENTS.md: 95% similarity ✓
- CLAUDE.md ↔ GEMINI.md: 76% similarity ⚠ DRIFT
  - GEMINI.md missing: 7+8 tier-explanation
  - GEMINI.md has extra: gemini-specific footer
- AGENTS.md ↔ GEMINI.md: 78% similarity ⚠
...

## Section: Voice tier semantics
[similar table]

## Section: Scaffolding principles (L-001/L-002/L-003)
- CLAUDE.md: all 3 lessons referenced
- AGENTS.md: only L-001 referenced ⚠ DRIFT
- GEMINI.md: none referenced ⚠ DRIFT

## Recommended actions
1. Update GEMINI.md compliance section — add 7+8 tier-explanation from CLAUDE.md
2. Add L-002 + L-003 references to AGENTS.md + GEMINI.md
3. ...
```

### Step 5 — Write report + return-code

```bash
REPORT=".claude/runtime/audit/instruction-parity-$(date +%Y%m%d).md"
mkdir -p "$(dirname "$REPORT")"
# Write report

# Return code reflects drift severity
# 0 = clean (no drift > threshold)
# 1 = warn (some drift but < major-threshold)
# 2 = fail (major drift, multi-CLI promise broken)
```

## Voice tier behavior

`voice: internal`. Operator-internal multi-CLI maintenance pass.

## Status protocol

- **DONE** — report rendered, all 6 files compared, no major drift
- **DONE_WITH_CONCERNS** — comparison done but warnings present (<major threshold)
- **BLOCKED** — multiple files missing OR can't read REPO_ROOT
- **NEEDS_CONTEXT** — invocation outside a git repo

## Pause-points

- 1+ files missing: surface + ask whether to proceed with partial-comparison
- Major drift detected on all key sections: surface aggressively, recommend halting the multi-CLI release

## Hop-in support

YES — solo-invocable + CI-integrated.

## Integration

**Reads:**
- All 6 instruction files in the repo
- (Optional) Previous parity-report for delta-comparison

**Writes:**
- `.claude/runtime/audit/instruction-parity-<date>.md` (report)
- stdout (summary)
- Return code (CI consumption)

**Consumed by:**
- Operator (pre-multi-CLI-release verification)
- CI workflow (`.github/workflows/instruction-parity.yml`, future)
- `/li:doctor --instruction-parity` (subcommand integration, future)

## Anti-patterns

- **Mass-overwrite for parity** — this skill REPORTS drift, doesn't auto-fix. Auto-fix risks losing CLI-specific necessary divergence.
- **Threshold == 100% similarity** — minor formatting drift OK; substance-drift is the issue. The 80% similarity threshold is heuristic-correct for v3.6.
- **Hidden-section drift** — extraction must cover ALL key sections; missing one defeats purpose.

## Failure recovery

- File unreadable: warn + skip, continue partial-comparison
- Section-extraction yields empty for required section: warn (section may have been removed or renamed)
- Substance-diff implementation absent: fall back to char-count diff with warning

## Recommended next steps after invocation

- Address each flagged drift individually (rarely auto-fixable; usually need operator-decision per section)
- After fix-pass: re-run `/li:instruction-parity-check` to verify
- Update `.github/workflows/instruction-parity.yml` to make this a hard CI-block if multi-CLI release is critical
