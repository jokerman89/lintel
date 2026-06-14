# Agent instructions — Lintel canonical navigation pointer

Read this file at session start. Every supported agent CLI (see `lib/cli-tiers.yaml`) reaches it through its root entry file (CLAUDE.md / AGENTS.md / GEMINI.md) or a shim under `shims/` that points here.

This file is **navigation, not content.** Load-bearing content lives in the layer files below. Follow the order; each layer file is short and authoritative.

---

## Order of operations at session start

Walk these in order. Each step references the authoritative layer file.

### 1. Read principles

**Layer 1 — `scaffolding/01-foundation/CORE-PRINCIPLES.md`** — 10 load-bearing rules. Authoritative. Plan before code. Subagents for parallel work. Self-improvement loop. Verify before done. Deviation flagging. Auto-mode bounds. Cleanup when bound crossed. Shared schema discipline. Simplicity first. Documented change beats silent change.

Do NOT re-state the rules inline here. They live in CORE-PRINCIPLES.md and change rarely. Read once, hold them as load-bearing for the session.

### 2. Run the compliance checklist

**Compliance — pack-driven.** The active pack declares its compliance posture (`resolve_pack_field compliance.mode|compliance.hooks`). The neutral `_default` pack enforces only the baseline below; a company pack (e.g. lintel-caip-pack) adds tiered gates.

A clean pass on the neutral baseline is the floor for any non-trivial action. Trivial actions (typo fix, doc edit, question) can skip. The baseline steps:

1. Authority scope
2. Customer-data check
3. Production-mutation check
4. Secrets check
5. The active pack's compliance gates (none in `_default`)

This is an operator-confirmed checklist, NOT automated enforcement. The harness surfaces the items; the operator confirms.

### 3. Load personas

**Layer 1 — `.claude/memory/personas.md`** in the active repo (scaffolded from `scaffolding/01-foundation/.claude/memory/personas.md`).

Calibrates communication style for the operator. Read once per session.

### 4. Load memory

**Layer 1 — `.claude/memory/working-state.md`** in the active repo.

Long-running state. Operator profile, project context, feedback patterns, external references.

### 5. Recent lessons

**Layer 1 — `.claude/memory/lessons.md`** in the active repo — read the most recent 10-15 entries. Older entries are reference material.
> Un-migrated repos: no `.claude/lintel-layout.yaml` marker means the repo still uses the legacy
> locations (`tasks/*`, `docs/adr/`, `.lintel/state/`) — use those there and suggest
> `bin/li-migrate-claude-home` (grace window to 2026-09-12).


### 6. ADR scan

**Layer 1 — `.claude/decisions/`** in the active repo — list filenames first, read full content only for ADRs whose title is relevant to the current task.

### 7. Agent selection precedence

5-level agent-selection precedence:

1. Operator pin (named in prompt)
2. Repo-level override (`.claude/agents/<Name>.md`)
3. Pack-promoted agents (from the active pack, if any)
4. User-global (`~/.claude/agents/`)
5. Fallback (main agent, no delegation)

This precedence is enforced by skill instructions — no runtime policy engine. Agents reading this file follow the rule.

---

## Layer index

| Source | Path | Change rate | When to read |
|---|---|---|---|
| Foundation | `scaffolding/01-foundation/` | Stable (EVOLUTION.md process) | Every session-start |
| Active pack | `packs/<name>/pack.yaml` (resolved) | Pack-driven | Every session-start (compliance + voice + persona) |
| Neutral baseline | `packs/_default/pack.yaml` | Stable | Fallback when no company pack is active |

Full architecture rationale in [`LAYERS.md`](LAYERS.md).

---

## Voice tier (pack-driven)

Voice is supplied by the active pack. The neutral `_default` pack uses `voice: internal` and enforces nothing. A company pack may declare a customer-facing tier and a calibrated voice corpus.

If this session generates customer-facing or official-communication content: the agent declares its voice tier in frontmatter, and output is checked against the active pack's voice gates (`resolve_pack_field voice.gates_active`; none by default) and voice corpus (`resolve_pack_field voice.corpus`).

If the session is internal dev work (code review, planning, tests, install): `voice: internal` — direct, builder-talking-to-builder.

Voice tier is the per-agent honest split between external voice (for customers) and engineering voice (for the team). The Microsoft CAIP-SE Trailblazer corpus ships in the lintel-caip-pack example.

---

## Self-maintenance — context-bloat watchers (opt-in)

If activated (operator symlinks from `~/.lintel/hooks/` to `~/.claude/hooks/`), the watchers print soft warnings when:

- Token count hits 50k (warn) or 80k (escalate)
- Tool-call count hits 80 (warn) or 130 (escalate)

The watchers do NOT auto-compact — Claude can't compact its own conversation. They surface the right move (`/context-save` + restart in a fresh session) before bloat hits productivity.

Configure thresholds in `~/.lintel/config.yaml`.

---

## Per-CLI capability matrix

Lintel ships with honest degradation. Not every skill works on every CLI.

The per-CLI truth is `lib/cli-tiers.yaml` (the single source); the README's capability table is
generated from it. Run `/li:welcome` for your CLI's live tier. Every skill / agent declares
`cli_support` in YAML frontmatter; `install/verify.sh` prints counts — the per-CLI table lives in
the README, generated from `lib/cli-tiers.yaml`.

---

## Auto-mode bounds (always apply)

OK without prompt: file edits, feature-branch commits/pushes, local tests/builds/lints, subagent invocations.

Requires explicit per-call authorization: production mutations, secrets, role/policy changes, DDL against live DB, container push to live registry, deploy triggers, `git push` to `main`.

Borderline (ask first): production audit events, production data access even read-only, branch builds wired to live deploys.

When in doubt: ask. Asking has small cost. Acting outside authorization has large cost.

---

## Cleanup pattern when a boundary has been crossed

1. Stop immediately. Do not push through.
2. Verify state with read-only checks.
3. Report honestly — what was done, current state, risks.
4. Propose options with trade-offs.
5. Wait for explicit authorization.

---

## When this file conflicts with a more specific source

Precedence order:

1. **Per-repo `CLAUDE.md`** — wins for that repo
2. **This file (`AGENT-INSTRUCTIONS.md`)** — cross-CLI canonical pointer
3. **CLI shim under `shims/`** — CLI-specific tips, never overrides core
4. **User-global `~/.claude/CLAUDE.md`** — fallback when no repo rule

If two sources conflict: surface to operator before acting. Do not silently choose.

---

## End of session

A clean end:

- `.claude/plans/todo.md` has a Review section or is cleared for the next task.
- Any new lessons in `.claude/memory/lessons.md`.
- Any new memory in `.claude/memory/working-state.md`.
- Any new ADRs in `.claude/decisions/`.
- Commits are atomic, no WIP debris.

If session ended mid-task: `.claude/plans/todo.md` makes the next session able to pick up cold.

---

## Lintel cycle — the structured path (v3.5)

For non-trivial work, the Lintel cycle provides an explicit 9-step pipeline (8 core phases + SCOPE). Each phase is its own skill; composed cycles run via orchestrator.

**Canonical invocation:**
- `/li:cycle` — full cycle SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE (8 core phases + the light, skippable SCOPE phase between SENSE and DEFINE)
- `/li:cycle --mode <preset>` — apply preset. Neutral spine presets: hotfix / internal-tool / research-dive / meta-infra. Pack-contributed presets (customer-engagement, demo-prep) are supplied by an active pack (e.g. lintel-caip-pack), not by the neutral spine.
- `/li:cycle --from <phase> --to <phase>` — custom subset
- `/li:resume` — pick up at next phase based on `.claude/runtime/state/00-state.md`

**Composite shortcuts:**
- `/li:fix` — SENSE+BUILD+REVIEW+SHIP (hotfix)
- `/li:research` — SENSE+DEFINE+DISCOVER (no build)
- `/li:plan-and-build` — PLAN+BUILD (split-session)
- `/li:review-and-ship` — REVIEW+SHIP+CAPTURE (close out)

**Individual phase invocation:** `/li:sense`, `/li:define`, etc. Each phase has hop-in support.

**Phase gates (always enforced):**
- Cost-estimate gate before BUILD (token-heavy phase)
- Founder approval gate at end of PLAN (MANDATORY pause)
- 3-stage review in REVIEW (spec compliance → quality → compliance)
- Compliance hard-stop in SHIP (if the active pack's compliance mode is `hard`)
- Two-stage subagent review per BUILD task (spec then quality)

See [docs/design/lintel-v3.5-cycle-and-roles.md](docs/design/lintel-v3.5-cycle-and-roles.md) for the full cycle specification.

---

## Role-lifting (v3.5)

Expert personas as lightweight session context layers. Voice + outcome-lens + decision-criteria + cold-knowledge influence cycle without bloating session-start.

**Lightweight load (~500 tokens) at activation:**
- `/li:role <role-id>` — load IDENTITY + VOICE + OUTCOME-LENS summary
- Role overlay applies to subsequent phases (DEFINE, SHIP, CAPTURE most affected)

**Deep-dive on-demand (~2-3k tokens):**
- `/li:role --deep-dive <role-id>` — load full role-file (COLD KNOWLEDGE, DECISION CRITERIA, INSIGHTS)

**Roles load from the active pack** (`resolve_pack_field roles.source`; none in `_default`). A company pack supplies its own role set — e.g. the lintel-caip-pack example ships `field-cto`, `solution-architect`, `engineering-manager`.

**Private roles:** Operator can scaffold custom roles via `/li:role-new`. Private roles store at `~/.lintel/roles/private/` (gitignored). Sync via `bin/li-roles-sync` to operator's private repo (never team-wide, never public marketplace).

**Session-start awareness (lightweight):** SENSE reads `~/.lintel/profile.yaml` `role_active` field; if set, loads role IDENTITY + VOICE summary (~500 tokens). Full deep-dive only on operator command.

---

## Context warming (v3.5)

On-demand 1M-context utilization beyond session-start. Default session-start stays lightweight (~5-15k tokens); operator explicitly warms when work benefits.

- `/li:context-warm <files-or-globs>` — explicit file load with budget tracking
- `/li:context-warm-related <topic>` — heuristic load by keyword
- `/li:context-warm-sessions [N]` — load last N session saves on branch
- `/li:context-warm-adrs <topic>` — load topic-relevant ADRs
- `/li:context-warm-customer <engagement>` — customer-repo state (audit-logged)
- `/li:context-warm-from-url <url>` — WebFetch + dump (URL gate when pack compliance mode is `hard`)
- `/li:context-budget` — utilization visibility
- `/li:context-save [--label <name>]` — checkpoint (named saves covered by --label; the former snapshot/dump skills are aliases since v5, ADR-0006)
- `/li:context-restore [path]` — load latest or specific prior session save
- `/li:context-cool` — selective IGNORE marker

For >20k token loads: explicit budget confirmation required.

---

## Compliance mode (pack-driven)

Compliance posture is declared by the active pack (`resolve_pack_field compliance.mode`), not a separate env toggle. The neutral `_default` pack is `advisory`. A company pack can set `hard`.

**When the active pack is `hard`:**
- The pack's compliance gates (`compliance.hooks`) are ENFORCED (not advisory)
- The pack's voice tier auto-applies on customer-facing output
- Customer-repo loads + URL fetches audit-logged

**When `advisory` (default):**
- Compliance hooks are advisory only
- `voice.default_tier`: internal
- Operator-driven gates only

The lintel-caip-pack example sets `hard` mode with the Microsoft CAIP-SE ruleset (SSO policy, first-party preference, RAIS/OneCS/SDL gates, Trailblazer voice).

**Profile fields:**
```yaml
active_pack: <name> | _default
role_active: <id> | null
default_mode: internal-tool | hotfix | research-dive | meta-infra   # plus pack-contributed modes
checkpoint_mode: explicit | continuous
context_warmup_default: minimal | standard | aggressive
proactive: true | false
```
