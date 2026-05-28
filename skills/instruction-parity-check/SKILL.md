---
name: instruction-parity-check
layer: foundation
description: Verifierar substance-parity över 6 instruktionsfiler (root CLAUDE/AGENTS/GEMINI + shims). Multi-CLI promise's weak point per 6.2.
color: yellow
tools: Read, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `instruction-parity-check` skill — defender mot drift mellan multi-CLI instruction files.

## What this skill does

Lintel ships 6 instruktionsfiler so different CLIs read same Lintel-rules:
- `CLAUDE.md` (claude-code root)
- `AGENTS.md` (codex root)
- `GEMINI.md` (gemini root)
- `.claude/AGENTS.md` (claude-code shim)
- `.codex/CLAUDE.md` (codex shim)
- `.github/copilot-instructions.md` (copilot)

Per v3.6 backlog 6.2: "De kommer driva — en Copilot-kollega får olika regler än en Claude-Code-kollega. Detta är multi-CLI-promise's weak point."

Detta skill kompararar substans-equivalens över filerna + flag drift på 4 key sections:
1. **Compliance rules** (5+7+8 tier, MS Business Data classification, customer-data block)
2. **Voice tier semantics** (internal vs trailblazer-draft)
3. **Scaffolding principles** (L-001 + L-002 + L-003 reflected)
4. **Auto-mode boundaries** (what's OK without prompt, what needs auth)

## When to use

- **CI-integrated** — kör per push till main, flag if substance-drift > threshold
- **Pre-shipping multi-CLI feature** — verify all 6 files reflect change
- **Onboarding new CLI** — adding 7th instruction file: compare existing 6 first
- **Post-rename** — verify instructions follow Phase A / Phase B rename-discipline

## When NOT to use

- Hand-editing single file — denna skill READS, ej modifies
- Diff-checking style/grammar — endast substance-comparison
- Real-time live-comparison — denna är batch-pass

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

För each file, parse sektion-headers + canonical-content:

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
  # Capture into per-section files för diff
done
```

### Step 3 — Cross-file substance-diff

För each of 4 key sections:
1. Compute canonical-form av text (lowercase + collapse whitespace + strip examples)
2. Pairwise diff: file A vs file B, A vs C, ..., E vs F
3. Score similarity (jaccard på 5-grams eller equivalent)
4. Flag pairs med < 80% substance-similarity

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
1. Update GEMINI.md compliance section — add 7+8 tier-explanation från CLAUDE.md
2. Add L-002 + L-003 references to AGENTS.md + GEMINI.md
3. ...
```

### Step 5 — Write report + return-code

```bash
REPORT="${HOME}/.lintel/audit/instruction-parity-$(date +%Y%m%d).md"
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
- **DONE_WITH_CONCERNS** — comparison klar but warns present (<major threshold)
- **BLOCKED** — multiple files missing OR can't read REPO_ROOT
- **NEEDS_CONTEXT** — invocation outside git repo

## Pause-points

- 1+ files missing: surface + ask if proceed med partial-comparison
- Major drift detected på all key sections: surface aggressively, recommend halt-multi-CLI-release

## Hop-in support

YES — solo-invocable + CI-integrated.

## Integration

**Reads:**
- All 6 instruction-files i repo
- (Optional) Previous parity-report för delta-comparison

**Writes:**
- `~/.lintel/audit/instruction-parity-<date>.md` (report)
- stdout (summary)
- Return code (CI consumption)

**Consumed by:**
- Operator (pre-multi-CLI-release verification)
- CI workflow (`.github/workflows/instruction-parity.yml`, future)
- `/li:doctor --instruction-parity` (subcommand integration, future)

## Anti-patterns

- **Mass-overwrite för parity** — denna skill REPORTS drift, doesn't auto-fix. Auto-fix risks losing CLI-specific necessary divergence.
- **Threshold == 100% similarity** — minor formatting drift OK; substance-drift is the issue. 80% similarity threshold is heuristic-correct för v3.6.
- **Hidden-section drift** — extraction must cover ALL key sections; missing one defeats purpose.

## Failure recovery

- File unreadable: warn + skip, continue partial-comparison
- Section-extraction yields empty for required section: warn (section may have been removed or renamed)
- Substance-diff implementation absent: fall back to char-count diff with warning

## Recommended next steps after invocation

- Address each flagged drift individually (rarely auto-fixable; usually need operator-decision per section)
- After fix-pass: re-run `/li:instruction-parity-check` to verify
- Update `.github/workflows/instruction-parity.yml` to make this a hard CI-block if multi-CLI release is critical
