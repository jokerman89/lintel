---
name: sense
layer: foundation
description: Phase 1 of Lintel cycle — auto-detect operator intent, pack compliance mode, active role, mode recommendation, 00-state from prior session. Lightweight diagnostic, no gates.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: REQUIRED
gap_if_skipped: "Cycle runs with no intent detection, mode recommendation, prior-session state, or context-budget read; every downstream phase is mis-scoped and the operator gets no orientation screen."
---

You are the SENSE skill — Phase 1 of the Lintel cycle.

## What this skill does

Reads operator state silently and surfaces a one-screen diagnostic. NOT exploratory. NOT questioning. Pure read.

SENSE answers four things before the operator commits to a phase:
1. What's the operator's intent likely to be? (build / fix / review / research / ship / scaffold / unclear)
2. What's the current configuration? (pack compliance mode, role active, voice tier, mode default)
3. Where did the last session leave off? (00-state.md from cwd, if present)
4. What's the context budget? (current tokens used, headroom for warm-up)

Output: a SENSE report. Operator decides next move based on it.

## When to use

- Always at start of `/li:cycle` (auto-invoked)
- Standalone when entering a new repo / new session and need orientation
- After `/li:resume` to confirm state before continuing
- When operator says "where are we?" / "what's the state?"

## When NOT to use

- For sizing + disambiguating a request — use `/li:scope` (Phase 1.5); SENSE only pre-reads size, SCOPE owns the gate
- For exploratory codebase mapping — use `/li:discover` (Phase 3)
- For clarifying problem definition — use `/li:define` (Phase 2)
- Mid-cycle (SENSE only runs once at cycle entry; don't re-invoke)

## Workflow

### Step 0a — Surface relevant lessons (v3.6 cohort 2 item 1.3)

Before reading configuration, invoke `/li:lessons-surface` so future session work starts with relevant lessons from `.claude/memory/lessons.md`. Closes the L-001/L-002 loop (lessons are written but never read without this step).

Invocation: `/li:lessons-surface --auto-from-sense` — keyword derived from the branch name + recent commit subjects. (A skill call, portable across every CLI; the old `~/.claude/skills/...` path was Claude-Code-only and non-executable.)

The surfacing is MECHANICAL since v5 (ADR-0006): the skill runs `lessons_surface` from
`lib/memory.sh` (grep-rank, supersede-aware) — not a prose instruction the agent may skip.

Output (max 3 lessons) prepends to the SENSE report. Silent if no relevant matches. Never a blocker.

### Step 0b — Elephant-hint detection (v3.6 cohort 3 item 3.1)

Before reading configuration, scan operator's prompt for breadth-signals indicating a "swelling idea" — broad scope that historically glides out of control during plan-writing. The breadth score now comes from the **single source** (`lib/scale-estimator.sh`, decision 2A) so this hint and the scale gate (step 0e) can never disagree on how broad a request is:

```bash
prompt_text="<operator's last message>"

source "$LINTEL_REPO_ROOT/lib/scale-estimator.sh"
elephant_score=$(elephant_score "$prompt_text")   # single source (was inline; now lib/scale-estimator.sh detect_breadth)
```

If `elephant_score >= 3`: surface elephant-hint to operator (in SENSE report only — never block):

```
⚠ Elephant detected (breadth-signal score: <N>/5)
   Three paths:
   A) Slice the elephant now — focus on the smallest valuable slice first
   B) Proceed anyway — proceed broad; specifics will emerge during planning
   C) Rough-plan first — let me sketch scope so you see the elephant in text before we lock in work
   
   Operator picks via reply; defaulting to B (proceed anyway) preserves momentum.
```

DEFINE phase offers the 3-path-execution if operator picks A or C. SENSE only detects + surfaces.

### Step 0c — Meta-infra mode auto-detection (v4.0)

Before reading configuration, check if the change is **meta-infra** — i.e. it modifies the Lintel
harness *itself*. Meta-infra mode activates four extra gates (M1-M4) — operator should know up front
so they can opt into the heavier path or override.

> **H15 — gate on a Lintel-repo MARKER, not the path-glob alone.** `lib/`, `bin/`, `hooks/` are
> ordinary directories in a normal consumer repo; touching them there must **not** trigger meta-infra.
> The recommendation now requires that the repo *is the Lintel harness* (or a genuine fork). The
> path-glob is a **secondary** signal that sharpens the message — never the sole trigger.

```bash
# 1) PRIMARY GATE — is this repo the Lintel harness itself?
#    Marker A: a Lintel plugin manifest (name OR description/keywords mention "lintel").
#    Marker B (fallback for a renamed plugin): the pack-contract pair every Lintel repo has.
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
is_lintel_repo=false
if [ -f "$repo_root/.claude-plugin/plugin.json" ] && grep -qi 'lintel' "$repo_root/.claude-plugin/plugin.json"; then
  is_lintel_repo=true
elif [ -f "$repo_root/lib/pack-resolver.sh" ] && [ -d "$repo_root/packs/_default" ]; then
  is_lintel_repo=true
fi

# 2) SECONDARY SIGNAL — which paths in the working diff touch harness scaffolding?
#    (Used to sharpen the message + pre-fill the structure-changes template; NOT a trigger on its own.)
meta_paths_changed=$(git diff --name-only HEAD 2>/dev/null | grep -cE '^(skills|agents|hooks|bin|lib|packs|install)/|^LAYERS\.md$|^bin/_.*\.sh$' || echo 0)
meta_staged=$(git diff --cached --name-only 2>/dev/null | grep -cE '^(skills|agents|hooks|bin|lib|packs|install)/|^LAYERS\.md$|^bin/_.*\.sh$' || echo 0)
meta_total=$((meta_paths_changed + meta_staged))

# 3) Operator intent signal (explicit "lintel itself" / meta-infra language).
operator_signal=0
prompt_text="<operator's last message>"
echo "$prompt_text" | grep -qiE "skill|agent|hook|pack|scaffold|lintel itself|meta-infra|li-bin|install/" && operator_signal=1

# Recommend meta-infra ONLY in the Lintel repo AND when the diff/intent actually touches the harness.
# In a plain consumer repo (is_lintel_repo=false) editing lib/ or bin/ stays ordinary work — no M-gates.
if [ "$is_lintel_repo" = true ] && { [ "$meta_total" -gt 0 ] || [ "$operator_signal" -eq 1 ]; }; then
  meta_infra_detected=true
else
  meta_infra_detected=false
fi
```

If `meta_infra_detected=true` (Lintel-repo marker present **and** the diff/intent touches the
harness): surface to operator in the SENSE report (never block):

```
⚙ Meta-infra mode detected (this IS the Lintel harness — <plugin.json mentions lintel | pack-resolver+_default present>)
   Diff touches: <list of scaffolding paths>
   Recommendation: --mode meta-infra (activates Gates M1-M4)
   Override: --mode <other> if change is content-only or test-only
   Cap: 600k soft / 900k hard (heavier REVIEW + CAPTURE)
```

If `is_lintel_repo=false` (a plain consumer repo): meta-infra is **not** recommended even when the
diff touches `lib/`, `bin/`, or `hooks/` — those are ordinary directories there. SENSE stays silent
on meta-infra and the normal cap applies.

DEFINE phase reads `meta_infra_detected` from 00-state.md and pre-fills the structure-changes/<date>-<slug>.md template. Operator can still override via `--mode <other>`.

### Step 0d — Orientator invocation (v4.0 Phase 3)

Invoke the lightweight orientator agent to recommend a workflow based on operator's prompt + active pack's `navigation.*` block. Mechanical-first; LLM escalation only when mechanical confidence falls below pack's `escalation_threshold`. See [orientator concept doc](../../docs/concepts/orientator.md).

```bash
# Run only when operator didn't already specify --mode/--from explicitly
if [ -z "${flag_mode:-}" ] && [ -z "${flag_from:-}" ]; then
  source "$LINTEL_REPO_ROOT/lib/orientator-routing.sh"

  intent=$(classify_intent "$prompt_text")
  default_workflow=$(resolve_pack_field navigation.default_workflow)
  workflow=$(match_workflow "$intent" "$default_workflow")
  high_risk_csv=$(resolve_pack_field navigation.high_risk_workflows)
  risk=$(assess_risk "$workflow" "$high_risk_csv")
  confidence=$(score_confidence "$intent" "$workflow")
  budget_tokens=$(resolve_pack_field navigation.orientator_budget_tokens)
  budget_tokens="${budget_tokens:-2000}"
  escalation=$(resolve_pack_field navigation.escalation_threshold)
  escalation="${escalation:-medium}"

  # Audit
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  audit_path="${LINTEL_HOME:-$HOME/.lintel}/audit/orientator-decisions.jsonl"
  mkdir -p "$(dirname "$audit_path")"
  printf '{"ts":"%s","kind":"orientator_decision","intent":"%s","workflow":"%s","risk":"%s","confidence":"%s","operator":"%s"}\n' \
    "$ts" "$intent" "$workflow" "$risk" "$confidence" "$(whoami 2>/dev/null || echo unknown)" \
    >> "$audit_path"
fi
```

Surfaces in SENSE report (Step 7 output) as recommended workflow. Per auto-mode level (b): low-risk + high-confidence auto-starts (if pack `auto_mode_eligible: true`), high-risk always confirms.

### Step 0e — Scale pre-read (Slice 2 — design §3.2)

> **Slice 2 change:** the substantive scale **gate** (the clarifying AskUserQuestion + route-override + `scope.md` emit) has been **promoted to the first-class SCOPE phase** (`skills/scope/SKILL.md`), which runs between SENSE and DEFINE. SENSE step 0e is now a **light pre-read**: it surfaces the size in the SENSE report so the operator sees it early, and **delegates the gate + `scope.md` to SCOPE**. This keeps SENSE read-only and light (it never pauses), and gives the gate a testable home that can grow without bloating SENSE.

Runs **after** step 0d (so the orientator's route is available to surface alongside size). Mechanical only — no question is ever asked here.

```bash
source "$LINTEL_REPO_ROOT/lib/scale-estimator.sh"

scale_size=$(classify_size "$prompt_text")
scale_amb=$(scale_ambiguous "$prompt_text")
depth_schema=$(size_to_depth_schema "$scale_size")
```

**What SENSE does (pre-read only):**

- Surface `scale_size` + `depth_schema` in the SENSE report (Step 7 output) so the operator sees the request's size before committing to a phase.
- If `scale_amb=yes`, surface a one-line **flag** — "scale is bimodal; SCOPE will ask one clarifying question" — but **do not ask it here.** SENSE never pauses.
- If `scale_size` ∈ {L, XL}, note that PLAN will use a deeper `depth_schema`.

**What SENSE delegates to SCOPE (does NOT do here):**

- the clarifying gate (the AskUserQuestion that disambiguates a bimodal reading),
- the orientator route-override (`deploy→ship` → full cycle from DEFINE),
- emitting `scope.md`.

**Standalone SENSE still works.** When SENSE is run on its own (no SCOPE follows), the mechanical `scale_size` / `depth_schema` in the report are complete and correct — just un-disambiguated. The bimodal flag tells the operator a question is pending; running `/li:scope` (or `/li:cycle`) resolves it. SENSE never blocks on scale.

`depth_schema` flows downstream to PLAN: `flat` → flat task list, `phased` → phases + tasks, `tree` → phase→task→subtask (Slice 2). Time estimates stay out unless the operator asks (`--with-time`).

### Step 1 — Read configuration

```bash
LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
PROFILE="$LINTEL_HOME/profile.yaml"

if [ -f "$PROFILE" ]; then
  # Parse: role_active, default_mode, proactive from profile.
  role_active=$(grep -E '^role_active:' "$PROFILE" | awk '{print $2}')
  default_mode=$(grep -E '^default_mode:' "$PROFILE" | awk '{print $2}')
  proactive=$(grep -E '^proactive:' "$PROFILE" | awk '{print $2}')
else
  # First-run: profile missing. Surface prompt-on-first-run per D9.3.
  echo "FIRST_RUN_DETECTED"
fi

# Compliance + voice come from the active pack (neutral defaults if _default).
compliance_mode=$(resolve_pack_field compliance.mode)              # advisory by default
workprofile=$(resolve_pack_field compliance.workprofile_default)   # off by default
voice_default=$(resolve_pack_field voice.default_tier)             # internal by default
```

If profile missing → prompt operator via AskUserQuestion: "Lintel can run with or without compliance gates. The active pack drives this (`resolve_pack_field compliance.mode`); the `_default` pack is advisory + workprofile off. Pick a pack if you want stricter gates."

### Step 2 — Read prior 00-state.md

```bash
STATE_FILE=".claude/runtime/state/00-state.md"
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
- Surface "Role active: <id> (deep-dive: /li:role --deep-dive)"

Do NOT load:
- COLD KNOWLEDGE section
- DECISION CRITERIA section
- OUTCOME LENS per phase
- ROLE-SPECIFIC INSIGHTS
- SENSITIVE CONTEXT

Those load on-demand via `/li:role --deep-dive <role-id>`.

### Step 5 — Read lessons + memory (light scan)

```bash
[ -f ".claude/memory/lessons.md" ] && lessons_count=$(grep -c '^## ' .claude/memory/lessons.md)
[ -f ".claude/memory/working-state.md" ] && memory_count=$(grep -c '^## ' .claude/memory/working-state.md)
```

Surface: "X lessons / Y memory entries available — invoke `/li:lessons` to filter for current intent."

Do NOT load the content. Just signal availability.

### Step 6 — Context budget snapshot

Approximate current context window utilization. If detectable from prior turns + loaded files. Report:
- Current ~tokens used / 1M
- Headroom for warm-up
- Recommend warm/cool if applicable

### Step 7 — Write 00-state.md entry + surface report

Mechanical since v5.0 (ADR-0008) — one command, not a YAML obligation:

```bash
_sl="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}/lib/state.sh"
[ -f "$_sl" ] || _sl="$HOME/.lintel/lib/state.sh"; source "$_sl"   # installed by install.sh in consumer repos
state_append SENSE DONE next=SCOPE mode_recommended=$recommended_mode intent_detected="$intent" role=$role_active voice_tier=$effective_voice_tier compliance_mode=$compliance_mode meta_infra_detected=$meta_infra_detected meta_paths_changed=$meta_total
```

## Output format

```
LINTEL SENSE — <timestamp>

Operator: <whoami>
Mode: <recommended-or-default>
Compliance: <pack compliance.mode> (from active pack)
Role: <id active> | <none>
Voice tier: <effective>

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

Exception: first-run case where `profile.yaml` doesn't exist → AskUserQuestion to set the active pack (per D9.3). This is a one-time setup pause, not a recurring SENSE behavior.

## Hop-in support

SENSE is **always first** in `/li:cycle`. When operator invokes any other phase standalone (e.g. `/li:plan`), that phase reads SENSE-equivalent context implicitly (lighter — only reads what's needed for that phase). 

If operator explicitly asks for the SENSE report mid-session, re-run is allowed but rarely useful.

## Integration

**Reads:**
- `~/.lintel/profile.yaml`
- `.claude/runtime/state/00-state.md` in cwd (if present)
- `.claude-plugin/plugin.json` + `lib/pack-resolver.sh` + `packs/_default/` (Lintel-repo marker for meta-infra gating, Step 0c)
- recent `git log --oneline -10` (cheap)
- `.claude/memory/lessons.md` (line count only)
- `.claude/memory/working-state.md` (line count only)
- role file IDENTITY section (if role active)
- `~/.lintel/scaffolding/` presence

**Writes:**
- `.claude/runtime/state/00-state.md` (new SENSE entry, appends)

**Triggers (recommends, never auto-invokes):**
- SCOPE next in `/li:cycle` (sizes + disambiguates the request before DEFINE)
- Operator chooses next phase

## Anti-patterns

- **Loading full role-file content** — only IDENTITY summary (50-100 tokens)
- **Running expensive grep / glob** — that's DISCOVER's job
- **Asking questions** — SENSE is read-only (except first-run pack setup)
- **Auto-invoking next phase** — surface recommendation, operator decides
- **Re-running SENSE mid-cycle** — once per cycle entry, that's it
- **Skipping 00-state.md write** — every phase appends; this is the resumability mechanism

## Failure recovery

- **profile.yaml malformed**: warn but continue with defaults (workprofile=off, voice=internal, mode=auto). Recommend `/li:doctor` for diagnosis.
- **00-state.md unreadable**: continue without prior state, NO_PRIOR_STATE flag in report.
- **Permission errors on `.claude/runtime/state/`**: warn, write to `/tmp/lintel-state-<ts>.md` instead, surface path.

## Voice tier behavior

`voice: internal`. SENSE report is operator-facing diagnostic. No customer-facing output.

## Cycle-position footer

Close your report with the shared position footer so the operator always knows where they are in the
cycle and the one logical next action — whether this phase ran standalone or inside `/li:cycle`:

```bash
source "$LINTEL_REPO_ROOT/lib/cycle-footer.sh"   # fallback: "$(git rev-parse --show-toplevel)/lib/cycle-footer.sh"
render_cycle_footer                               # reads .claude/runtime/state/00-state.md; --compact for short replies
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
