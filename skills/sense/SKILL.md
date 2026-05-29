---
name: sense
layer: foundation
description: Phase 1 of Lintel cycle — auto-detect operator intent, WorkProfile state, active role, mode recommendation, 00-state from prior session. Lightweight diagnostic, no gates.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the SENSE skill — Phase 1 of the Lintel cycle.

## What this skill does

Reads operator state silently and surfaces a one-screen diagnostic. NOT exploratory. NOT questioning. Pure read.

SENSE answers four things before the operator commits to a phase:
1. What's the operator's intent likely to be? (build / fix / review / research / ship / scaffold / unclear)
2. What's the current configuration? (WorkProfile on/off, role active, voice tier, Azure focus, mode default)
3. Where did the last session leave off? (00-state.md from cwd, if present)
4. What's the context budget? (current tokens used, headroom for warm-up)

Output: a SENSE report. Operator decides next move based on it.

## When to use

- Always at start of `/li:cycle` (auto-invoked)
- Standalone when entering a new repo / new session and need orientation
- After `/li:resume` to confirm state before continuing
- When operator says "where are we?" / "what's the state?" / "vad är läget?"

## When NOT to use

- For exploratory codebase mapping — use `/li:discover` (Phase 3)
- For clarifying problem definition — use `/li:define` (Phase 2)
- Mid-cycle (SENSE only runs once at cycle entry; don't re-invoke)

## Workflow

### Step 0a — Surface relevant lessons (v3.6 cohort 2 item 1.3)

Before reading configuration, invoke `/li:lessons-surface` so framtida session-arbete startar med relevanta lessons från `tasks/lessons.md`. Stänger L-001/L-002-loopen (lessons skrivs men läses aldrig utan denna step).

```bash
# Auto-invoke lessons-surface med current-context som keyword
# (branch name + recent commit subjects ger implicit topic)
~/.claude/skills/lessons-surface --auto-from-sense 2>/dev/null || true
```

Output (max 3 lessons) prepends till SENSE-rapport. Silent om no relevant matches. Aldrig blocker.

### Step 0b — Elephant-hint detection (v3.6 cohort 3 item 3.1)

Before reading configuration, scan operator's prompt for breadth-signals indicating a "swelling idea" — broad scope that historically glides out of control during plan-writing. Detection heuristics:

```bash
prompt_text="<operator's last message>"

# Count breadth-signals
elephant_score=0
echo "$prompt_text" | grep -qiE "entire|all|every|whole|full system|complete rewrite|across all" && elephant_score=$((elephant_score+2))
echo "$prompt_text" | grep -qiE "redesign|refactor everything|new architecture|from scratch" && elephant_score=$((elephant_score+2))
echo "$prompt_text" | grep -qiE "and also|while we're at it|maybe also|could we also" && elephant_score=$((elephant_score+1))
word_count=$(echo "$prompt_text" | wc -w)
[ "$word_count" -gt 80 ] && elephant_score=$((elephant_score+1))
```

If `elephant_score >= 3`: surface elephant-hint to operator (in SENSE-report only — never block):

```
⚠ Elephant detected (breadth-signal score: <N>/5)
   Three paths:
   A) Stycka elefanten now — focus on the smallest valuable slice first
   B) Kör ändå — proceed broad; specifics will emerge during planning
   C) Rough-plan first — let me sketch scope så du ser elefanten i text innan vi locks in arbete
   
   Operator picks via reply; defaulting to B (kör ändå) preserves momentum.
```

DEFINE phase offers the 3-path-execution if operator picks A or C. SENSE only detects + surfaces.

### Step 0c — Meta-infra mode auto-detection (v4.0)

Before reading configuration, check if cwd diff touches scaffolding paths. Meta-infra mode activates four extra gates (M1-M4) — operator should know up front so they can opt into the heavier path or override.

```bash
# Path-glob detection: which paths in working diff touch Lintel scaffolding?
meta_paths_changed=$(git diff --name-only HEAD 2>/dev/null | grep -cE '^(skills|agents|hooks|bin|lib|packs|install)/|^LAYERS\.md$|^bin/_.*\.sh$' || echo 0)
meta_staged=$(git diff --cached --name-only 2>/dev/null | grep -cE '^(skills|agents|hooks|bin|lib|packs|install)/|^LAYERS\.md$|^bin/_.*\.sh$' || echo 0)
meta_total=$((meta_paths_changed + meta_staged))

# Also detect intent from operator's last message
operator_signal=0
prompt_text="<operator's last message>"
echo "$prompt_text" | grep -qiE "skill|agent|hook|pack|scaffold|lintel itself|meta-infra|li-bin|install/" && operator_signal=1

if [ "$meta_total" -gt 0 ] || [ "$operator_signal" -eq 1 ]; then
  meta_infra_detected=true
fi
```

If `meta_infra_detected=true`: surface to operator in SENSE-report (never block):

```
⚙ Meta-infra mode detected
   Diff touches: <list of scaffolding paths>
   Recommendation: --mode meta-infra (activates Gates M1-M4)
   Override: --mode <other> if change is content-only or test-only
   Cap: 600k soft / 900k hard (heavier REVIEW + CAPTURE)
```

DEFINE phase reads `meta_infra_detected` from 00-state.md and pre-fills the structure-changes/<date>-<slug>.md template. Operator can still override via `--mode <other>`.

### Step 1 — Read configuration

```bash
LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
PROFILE="$LINTEL_HOME/profile.yaml"

if [ -f "$PROFILE" ]; then
  # Parse: workprofile, role_active, voice_tier_default, azure_focus, default_mode, etc
  workprofile=$(grep -E '^workprofile:' "$PROFILE" | awk '{print $2}')
  role_active=$(grep -E '^role_active:' "$PROFILE" | awk '{print $2}')
  default_mode=$(grep -E '^default_mode:' "$PROFILE" | awk '{print $2}')
  voice_default=$(grep -E '^voice_tier_default:' "$PROFILE" | awk '{print $2}')
  azure_focus=$(grep -E '^azure_focus:' "$PROFILE" | awk '{print $2}')
  proactive=$(grep -E '^proactive:' "$PROFILE" | awk '{print $2}')
else
  # First-run: profile missing. Surface prompt-on-first-run per D9.3.
  echo "FIRST_RUN_DETECTED"
fi
```

If profile missing → prompt operator via AskUserQuestion: "Lintel kan köras med eller utan MS-compliance-policies (WorkProfile). MS-internal operator → recommend ON. Non-MS → recommend OFF. Välj."

### Step 2 — Read prior 00-state.md

```bash
STATE_FILE=".lintel/state/00-state.md"
if [ -f "$STATE_FILE" ]; then
  # Parse: cycle_id, current_phase, next_recommended, phases_completed, intent_detected
  # Surface in report
else
  # First session in this repo, or state cleared
  echo "NO_PRIOR_STATE"
fi
```

### Step 3 — Detect intent from operator's last message + cwd

Heuristics (apply in order, first match wins):
- Operator message contains "fix" / "bug" / "broken" → intent: fix → recommend `mode=hotfix`
- Operator message contains "ship" / "release" / "deploy" → intent: ship → recommend hop to SHIP
- Operator message contains "review" / "audit" / "check" → intent: review → recommend `/li:review`
- Operator message contains "research" / "explore" / "understand" → intent: research → recommend `mode=research-dive`
- Operator message contains "scaffold" / "new project" / "new repo" → intent: scaffold → recommend `bin/li-scaffold init`
- Operator message contains "build" / "add" / "implement" → intent: build → recommend full cycle
- cwd has uncommitted changes + recent commits with WIP prefix → likely BUILD continuation
- cwd is freshly cloned (1 commit) → likely scaffolding-needed
- Otherwise → intent: unclear → recommend `/li:cycle --mode auto` or operator-decide

### Step 4 — Lightweight role load (if active)

If `role_active` is set in profile:
- Read role file IDENTITY section (~50-100 tokens, NEVER full file)
- Note voice tier from role (overrides mode default if set)
- Surface "Role active: <id> (deep-dive: /li:role-deep-dive)"

Do NOT load:
- COLD KNOWLEDGE section
- DECISION CRITERIA section
- OUTCOME LENS per phase
- ROLE-SPECIFIC INSIGHTS
- SENSITIVE CONTEXT

Those load on-demand via `/li:role-deep-dive <role-id>`.

### Step 5 — Read lessons + memory (light scan)

```bash
[ -f "tasks/lessons.md" ] && lessons_count=$(grep -c '^## ' tasks/lessons.md)
[ -f "tasks/memory.md" ] && memory_count=$(grep -c '^## ' tasks/memory.md)
```

Surface: "X lessons / Y memory entries available — invoke `/li:lessons` to filter for current intent."

Do NOT load the content. Just signal availability.

### Step 6 — Context budget snapshot

Approximate current context window utilization. If detectable from prior turns + loaded files. Report:
- Current ~tokens used / 1M
- Headroom for warm-up
- Recommend warm/cool if applicable

### Step 7 — Write 00-state.md entry + surface report

```bash
mkdir -p .lintel/state
cat >> .lintel/state/00-state.md <<EOF
---
phase: SENSE
ts: $(date -u +%Y-%m-%dT%H:%M:%SZ)
operator: $(whoami)
workprofile: $workprofile
mode_recommended: $recommended_mode
role: $role_active
voice_tier: $effective_voice_tier
azure_focus: $azure_focus
intent_detected: $intent
phases_completed: []
context_budget: $current_tokens / 1M
meta_infra_detected: $meta_infra_detected
meta_paths_changed: $meta_total
---
EOF
```

## Output format

```
LINTEL SENSE — <timestamp>

Operator: <whoami>
Mode: <recommended-or-default>
WorkProfile: <ON/OFF> — <implication if ON>
Role: <id active> | <none>
Voice tier: <effective>
Azure focus: <ON/OFF>

Intent detected: <classification>
Recommended phase: <next>
Alt recommendation: <alternative if confidence low>

Prior state: <found / none>
  Last session: <timestamp + phase>
  Resume available: <yes/no via /li:resume>

Resources surfaced (not loaded):
  Lessons: <count>
  Memory entries: <count>
  ADRs: <count>
  Related design docs: <count>

Context budget: <X> / 1M (<%>) — <headroom note>

Next options:
  • /li:cycle [--mode <preset>]   — full cycle from here
  • /li:<phase>                    — jump to specific phase
  • /li:resume                     — pick up where we left off
  • /li:skill-router "<intent>"    — semantic router if unsure (was /li:match — grace until 2026-08-29)
```

## Status protocol

- **DONE** — sense report written, recommended mode/phase surfaced
- **BLOCKED** — cannot read state files (permissions, missing dirs)
- **NEEDS_CONTEXT** — `~/.lintel/profile.yaml` malformed AND first run completion failed

## Pause-points

None. SENSE runs to completion silently or surfaces report.

Exception: first-run case where `profile.yaml` doesn't exist → AskUserQuestion to set up WorkProfile (per D9.3). This is a one-time setup pause, not a recurring SENSE behavior.

## Hop-in support

SENSE is **always first** in `/li:cycle`. When operator invokes any other phase standalone (e.g. `/li:plan`), that phase reads SENSE-equivalent context implicitly (lighter — only reads what's needed for that phase). 

If operator explicitly asks for the SENSE report mid-session, re-run is allowed but rarely useful.

## Integration

**Reads:**
- `~/.lintel/profile.yaml`
- `.lintel/state/00-state.md` in cwd (if present)
- recent `git log --oneline -10` (cheap)
- `tasks/lessons.md` (line count only)
- `tasks/memory.md` (line count only)
- role file IDENTITY section (if role active)
- `~/.lintel/scaffolding/` presence

**Writes:**
- `.lintel/state/00-state.md` (new SENSE entry, appends)

**Triggers (recommends, never auto-invokes):**
- Operator chooses next phase

## Anti-patterns

- **Loading full role-file content** — only IDENTITY summary (50-100 tokens)
- **Running expensive grep / glob** — that's DISCOVER's job
- **Asking questions** — SENSE is read-only (except first-run WorkProfile setup)
- **Auto-invoking next phase** — surface recommendation, operator decides
- **Re-running SENSE mid-cycle** — once per cycle entry, that's it
- **Skipping 00-state.md write** — every phase appends; this is the resumability mechanism

## Failure recovery

- **profile.yaml malformed**: warn but continue with defaults (workprofile=off, voice=internal, mode=auto). Recommend `/li:doctor` for diagnosis.
- **00-state.md unreadable**: continue without prior state, NO_PRIOR_STATE flag in report.
- **Permission errors on `.lintel/state/`**: warn, write to `/tmp/lintel-state-<ts>.md` instead, surface path.

## Voice tier behavior

`voice: internal`. SENSE report is operator-facing diagnostic. No customer-facing output.
