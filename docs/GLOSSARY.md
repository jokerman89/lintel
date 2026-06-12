# Glossary

The load-bearing terms a Lintel newcomer meets before they are defined. One screen; skim it once,
refer back as needed. Fuller treatment lives in [docs/concepts/](concepts/) and the ADRs under
[.claude/decisions/](../.claude/decisions/).

| Term | What it means |
|---|---|
| **pack** | The installable identity layer — voice, compliance gates, personas, brand, roles. Nothing is hardcoded; everything is resolved from the active pack via `resolve_pack_field` (`lib/pack-resolver.sh`). Lintel ships only the neutral `_default` pack, which enforces nothing. Switch with `/li:pack-switch`. |
| **spine** | The company-neutral core of Lintel — the skills, agents, hooks, and lib helpers that carry no company identity. The opposite of a pack: the spine is what stays the same no matter which pack you load. |
| **cycle** | The main workflow: **the 9-step cycle (8 core phases + SCOPE)**, run by `/li:cycle`. Turns a raw request into shipped, captured work. |
| **the 9 phases** | The cycle steps, in order: **SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE**. SCOPE (phase 1.5) sizes the request; the other 8 are the core. Each phase has a gate (e.g. a cost estimate before BUILD, a founder-approval pause at the end of PLAN). |
| **workflow_root** | A skill that owns a job and can spawn sub-work — the top of a hand-off tree (`/li:cycle`, `/li:plan` standalone). Marked `workflow_root: true` in frontmatter; hand-offs out of it pass through the Brief Forge envelope (`lib/envelope-schema.yaml`). |
| **trio** | The cold-executor hand-off set born together in PLAN: **plan.md + spec.md + prompt.md** (under `.claude/plans/<slug>/`). Lets a fresh agent execute a task with no prior context. |
| **scope.md** | The sized, disambiguated scope that SCOPE (phase 1.5) emits — the wedge + size signal that DEFINE and PLAN inherit. Written by `/li:scope`. |
| **lessons (L-NNN)** | Numbered lessons recorded after any correction, in `.claude/memory/lessons.md`. Surfaced mechanically at SENSE and read at session start — the mechanism that compounds learning across fresh sessions. |
| **ADR** | Architecture Decision Record — one markdown file per non-trivial decision, in `.claude/decisions/NNNN-short-title.md`. Start one with `/li:adr-new`. |
| **meta-infra** | Changes to the harness's own structure (`skills/`/`agents/`/`hooks/`/`lib/`, frontmatter contracts). Held to a stricter discipline — an ADR **plus** an evolution-log entry under `docs/v4.x/structure-changes/`. See [docs/concepts/meta-infra-discipline.md](concepts/meta-infra-discipline.md). |
| **Gate M1–M4** | The four checkpoints a meta-infra change passes: **M1** structure-change entry, **M2** compatibility audit, **M3** shape tests green, **M4** ADR. They keep changes to the spine reversible and documented. |
| **the `.claude/` home** | Everything Lintel generates for a repo, under one root (ADR-0005). Committed knowledge — `.claude/memory/`, `.claude/decisions/`, `.claude/plans/`, `.claude/agents/`. Gitignored runtime — `.claude/runtime/` (cycle state, jobs, sessions, audit). See the "Where things live" map in the [README](../README.md) or [getting-started](getting-started.md). |
