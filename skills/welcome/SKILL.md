---
name: welcome
layer: foundation
description: First-run guided onboarding — detect the CLI, show its honest capability tier, run a dry-run cycle, and demonstrate a safety hook. The 5-minute "see the harness work" path.
color: green
tools: Read, Bash
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: full
necessity: OPTIONAL
gap_if_skipped: "A first-time operator meets the full skill set with no guided entry — they read docs instead of feeling the harness work, and never learn their CLI's honest capability tier (e.g. that the enforcement hooks only fire on Claude Code)."
navigation:
  primary_intent: guided first-run onboarding — see the harness work in five minutes
  triggers:
    - operator just installed Lintel and runs /li:welcome
    - operator asks "how do I start" / "getting started"
    - the README quickstart + the installer's completion message point here
  sibling_workflows:
    - /li:cli-fingerprint — the CLI detection this skill delegates to
    - /li:cycle — the guided demo (invoked with --dry-run)
    - /li:doctor — the deeper cross-CLI health check
  risk_level: low
  auto_mode_eligible: false
  estimated_tokens: 2000
---

You are the WELCOME skill — Lintel's first-run guided onboarding.

## What this skill does

A new operator just installed Lintel and is staring at the full skill set. Your job is to make
them *feel* the harness work in five minutes, honestly, on whichever CLI they are running:

1. Detect the active CLI.
2. Show that CLI's **honest** capability tier — including what does NOT work here.
3. Run one guided cycle in dry-run so they see the 9-step discipline without mutating anything.
4. Demonstrate a safety hook (or honestly explain why it can't fire on their CLI).
5. Point them at the next step.

This skill is a **thin orchestrator** — it reuses `/li:cli-fingerprint`, `lib/cli-tiers.sh`,
and `/li:cycle --dry-run`. It never rebuilds detection and never hardcodes the tier table
(that lives once in `lib/cli-tiers.yaml`).

## When to use

- Right after installing Lintel, on any supported CLI.
- When an operator asks "how do I get started" or "what can this do".

## When NOT to use

- Returning operators who already know the harness — point them at `/li:catalog` instead.
- As a step inside `/li:cycle` — welcome is a standalone first-run experience.

## Workflow

### Step 1 — Detect the active CLI

Invoke `/li:cli-fingerprint` to resolve which CLI is running Lintel (env-var → process →
tool-probe → config fallback). Capture the result as `$cli` (e.g. `claude-code`, `codex`,
`gemini`, …). If detection is uncertain, default `$cli=other` and say so — never guess a
capability you can't confirm.

### Step 2 — Show the honest capability tier

Read the tier from the single source (`lib/cli-tiers.yaml` via its lookup helper) and print
a short, honest banner. Do NOT hardcode any of these values:

```bash
source "$LINTEL_REPO_ROOT/lib/cli-tiers.sh" 2>/dev/null \
  || source "$(git rev-parse --show-toplevel 2>/dev/null)/lib/cli-tiers.sh"

cli="${cli:-other}"
label=$(cli_tier_field "$cli" label)
tier=$(cli_tier_field "$cli" tier)
hooks=$(cli_tier_field "$cli" hooks_supported)
subagents=$(cli_tier_field "$cli" subagents)
skills_native=$(cli_tier_field "$cli" skills_native)
```

Then surface (fill in the values):

```
Lintel — first run on <label>

  Tier:      <tier>            (full / supported / best-effort)
  Skills:    <native | manual> — how you invoke /li:<skill>
  Subagents: <native | sequenced | none>
  Hooks:     <on | OFF here>  — the enforcement layer (secret/customer-data blocks,
                                no-direct-push) fires ONLY on Claude Code.
```

Be direct about the gaps. If `tier != full`, say plainly what degrades. This honesty is the
whole point — an operator who learns the limits up front trusts the rest.

### Step 3 — Guided cycle, dry-run (no mutation)

Run the 9-step cycle in dry-run so they see the discipline without creating a job, a plan,
or any state in their repo:

Invocation: `/li:cycle --dry-run "add a hello endpoint"` (a throwaway prompt — dry-run shows
the phase plan + token forecast + which hooks *would* fire, and mutates **nothing**).

Walk them through what they see: SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW →
SHIP → CAPTURE, and the gate at each. One sentence each; this is the "way of working" pillar.

### Step 4 — Demonstrate a safety hook (honest per-CLI degradation)

The enforcement hooks are Claude-Code-only. How they activate depends on the install path — a
**plugin install auto-registers** them (zero-setup, via the plugin's `hooks/hooks.json`); a
**bare install** ships them inert (bare install only) until the operator symlinks + merges the
snippet. This is the canonical truth (ADR-0008); the full matrix lives in
`docs/getting-started.md#how-hook-activation-works` — point the operator there, never restate it
differently. Branch on `$hooks` and the install state:

- **`hooks == true` AND a hook is already firing** (plugin install — auto-registered; or a bare
  install where the operator already symlinked into `~/.claude/hooks/`): trigger one live. Show
  `no-secrets-in-edit` catching a fake key — e.g. narrate writing `AKIA0000000000000000` and the
  WARN it emits. This is the "whoa". On a plugin install this just works with no setup.

- **`hooks == true` but NO hook firing yet** (Claude Code, **bare install**, not yet armed): do NOT
  auto-edit `~/.claude/settings.json`. PRINT the exact opt-in for the operator to run, then they
  re-run this step to see it fire:

  ```bash
  ln -s ~/.lintel/hooks/shared/no-secrets-in-edit/run.sh ~/.claude/hooks/no-secrets-in-edit.sh
  # then add to ~/.claude/settings.json under PreToolUse(Edit|Write):
  #   { "hooks": [{ "type": "command", "command": "~/.claude/hooks/no-secrets-in-edit.sh" }] }
  ```

  Say: "On a bare install hooks ship inert (bare install only) — Lintel never edits your settings
  behind your back. Run the two lines above to arm the secret-scan hook, then `/li:welcome` again to
  watch it fire. (A plugin install would have armed them automatically — see
  docs/getting-started.md#how-hook-activation-works.)"

- **`hooks == false`** (every CLI except Claude Code): do NOT pretend. Narrate it:
  "The enforcement layer (secret-scan, customer-data block, no-direct-push) is a Claude Code
  mechanism — it does not fire on <label>. Here's what it would catch on Claude Code: a
  commit containing `AKIA…` or a customer email is blocked before it lands. On <label> you
  still get the skills, the cycle discipline, and the pack-driven knowledge — just not the
  live hook gate."

### Step 5 — Point at the next step

- `/li:catalog` — browse all skills.
- `/li:cycle` — run a real cycle on your own task (this time for real).
- `docs/getting-started.md` — the per-CLI install + first-task walkthrough.
- `/li:pack-list` / `/li:pack-switch` — switch identity/compliance per repo (corp vs private).

## Voice

Internal. Honest over impressive — the value of this skill is that it tells the operator the
truth about their CLI on the first screen. Never over-claim a capability the tier says is off.

## Anti-patterns

- **Hardcoding the tier table** — it lives once in `lib/cli-tiers.yaml`; read it, never inline it.
- **Auto-installing hooks / editing the operator's settings.json** — print the command, let them run it.
- **Running a real (non-dry-run) cycle that writes state into their repo on first run** — always `--dry-run` here.
- **Claiming hooks/subagents work where the tier says they don't** — degrade honestly.

## Failure recovery

- CLI detection uncertain → default to `other`/best-effort and say so; never over-claim.
- `lib/cli-tiers.yaml` unreadable → `cli_tier_field` returns safe defaults (best-effort, hooks off); proceed, degraded-but-honest.

## Cycle-position footer

Close your report with the shared position footer. Outside an active cycle it renders the thin
ambient line; inside one it shows the operator's position + next step:

```bash
source "$LINTEL_REPO_ROOT/lib/cycle-footer.sh"   # fallback: "$(git rev-parse --show-toplevel)/lib/cycle-footer.sh"
render_cycle_footer                               # auto: thin when no cycle, full/--compact when in one
```

See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
