# LAYERS — the 4-layer architecture manifest

JokermanStack (JStack) organizes everything into 4 layers. Each layer has its own purpose, change rate, and per-repo override rules.

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 4 — Power user (experimental, actively learning)     │
│  04-power-user/                                              │
│    hooks (inert by default), workflow templates,            │
│    memory protocols, multi-repo, skill activation rules     │
├─────────────────────────────────────────────────────────────┤
│  Layer 3 — Personal advanced (opinionated workflow)         │
│  03-personal-advanced/                                       │
│    voice tier (internal vs trailblazer),                    │
│    precedence model (5 levels),                             │
│    promoted-agents (tier-stamped)                            │
├─────────────────────────────────────────────────────────────┤
│  Layer 2 — Compliance (MS-policy-driven, non-negotiable)    │
│  02-compliance/                                              │
│    5 hard rules (always-on checklist at session-start)      │
│    7 on-demand rules (/compliance-check skill)              │
│    8 reference rules (operator can elevate per repo)        │
├─────────────────────────────────────────────────────────────┤
│  Layer 1 — Foundation (Boris-style discipline, stable)      │
│  01-foundation/                                              │
│    CORE-PRINCIPLES, EVOLUTION, EVOLUTION-LOG,               │
│    tasks/{lessons,memory,personas,todo},                    │
│    docs/adr/, .claude/agents/, CLAUDE.md.template           │
└─────────────────────────────────────────────────────────────┘
```

## Change rate per layer

| Layer | Change rate | Process to change |
|---|---|---|
| 1 Foundation | **Stable** | Goes through `EVOLUTION.md` process. CORE change = explicit decision + EVOLUTION-LOG entry. |
| 2 Compliance | **MS-policy-driven** | Quarterly review against MS internal SharePoint sources. Refresh on policy announcements. |
| 3 Personal advanced | **Opinionated** | PR-based, team review. No heavy EVOLUTION process but team-vetted. |
| 4 Power user | **Experimental** | Free adaptation. Promotion to Layer 3 via PR when a pattern proves out. Archive in `EVOLUTION-LOG.md` when it doesn't. |

## Read order (canonical session-start)

1. Layer 1 — `CORE-PRINCIPLES.md` (the 10 load-bearing rules)
2. Layer 2 — `SESSION-START-CHECK.md` (the 5-step compliance checklist)
3. Layer 1 — `tasks/personas.md` (operator calibration)
4. Layer 1 — `tasks/memory.md` (long-running state)
5. Layer 1 — recent `tasks/lessons.md` entries
6. Layer 1 — relevant ADRs in `docs/adr/`
7. Layer 3 — `precedence/README.md` (when delegating)
8. Layer 4 — only when the task explicitly needs a Layer 4 pattern

## Per-repo override mechanism

Each scaffolded repo can override layer behavior via:

- `<repo>/CLAUDE.md` — repo-specific rules ALWAYS override JStack defaults. Per-repo wins.
- `<repo>/.claude/agents/` — repo-level subagents override user-global with same name (Layer 3 precedence rule 2).
- `~/.jstack/config.yaml` — operator-global overrides for Layer 2 tier elevation, Layer 4 hook activation, Layer 3 voice tier defaults, etc.

## What each layer DOES NOT do

- **Layer 1 does NOT enforce.** It documents discipline. Agents read it at session-start; no runtime check.
- **Layer 2 does NOT auto-verify.** "No customer data" is operator-confirmed at session-start, not pattern-matched. The hooks in Layer 4 add specific automated checks for specific failure modes.
- **Layer 3 does NOT route at runtime in v1.** The 5-level precedence is enforced by skill instructions only (agents reading the canonical instructions follow the rule). Runtime policy engine deferred to v1.1.
- **Layer 4 does NOT auto-activate.** Hook files install but are inert until operator symlinks them.

## Why 4 layers, not 3 or 5?

- **Compliance separation** is non-negotiable for MS employees — must live at Layer 2.
- **Foundation vs personal-advanced** separation lets compliance sit at the top without burying personal workflow.
- **Power-user separation** lets experimental patterns live without polluting load-bearing foundation.
- 5-layer model was considered; rejected because the 4 categories above naturally cluster.

## Provenance

The 4-layer architecture model is from the operator's internal wiki ("My Claude Code Setup (experimental)" — Layer 1 Universal foundation / Layer 2 Compliance / Layer 3 Personal advanced / Layer 4 Power user). JStack v1 operationalizes that wiki vision into installable + verifiable infrastructure.
