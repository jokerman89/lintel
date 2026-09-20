# P04 Swarming preservation

## Source and checkpoint

Source: `codex/swarming-work`, `275a35447c4ad271e05816ade43ac48f1acec24f`.
Delta base: `e9911fcd448dc632bf2752c69304d2be80b7aa65`.
Target first parent: `21261f1ff76be994246060a7817924f2893f2454`, which contains main
`28061e434be455ca02f135b73244eaf4f73f3a69` and the authorized Universal plan.

The historical checkpoint is a real two-parent merge, not copied history or a squash.
Its exact SHA and subsequent P04 commits are recorded in [P04.md](P04.md). No source
worktree, source branch, default branch or remote is modified. Historical evidence
describes its original attempt only; it is not evidence for this reconciled tree.

The inventory below is exhaustive for `git diff --name-only e9911fc 275a354`: 76 paths.
**Same** means the exact path in the first column remains the destination. **I** means
source-identical text at the historical checkpoint (LF normalization only); **R** means
reconciled with current main or updated decision references, with the retained intent
specified. **G** additionally marks an imported generated artifact whose final
regeneration belongs to MasterSession. Later P04 repairs change only the owned runtime,
templates, skill, docs and tests; their acceptance is recorded separately in P04.md.

## Complete delta map

| # | Source path | Retained destination and intent | Checkpoint evidence |
|---|---|---|---|
| 1 | `.claude/SUBAGENT-GUIDE.md` | Same; bounded lanes and ownership guidance | I |
| 2 | `.claude/decisions/0026-first-class-swarming.md` | `.claude/decisions/0027-first-class-swarming.md`; original decision plus explicit hybrid reconciliation | R; original body and Git origin retained; main ADR0026 unchanged |
| 3 | `.claude/engineering/evolution/2026-09-08-swarming-work.md` | Same; historical structural intent | I |
| 4 | `.claude/plans/swarming-work/design.md` | Same; historical design, corrected ADR destination only | R; no outcome rewritten |
| 5 | `.claude/plans/swarming-work/discover.md` | Same; historical discovery | I |
| 6 | `.claude/plans/swarming-work/plan.md` | Same; original cards and completion record | I |
| 7 | `.claude/plans/swarming-work/prompt.md` | Same; original cold handoff | I |
| 8 | `.claude/plans/swarming-work/spec.md` | Same; original requirements | I |
| 9 | `.claude/plans/swarming-work/swarm/briefs/BC2.md` | Same; original contract worker brief | I |
| 10 | `.claude/plans/swarming-work/swarm/briefs/BC3.md` | Same; original workflow worker brief | I |
| 11 | `.claude/plans/swarming-work/swarm/briefs/BC4.md` | Same; original adapter worker brief | I |
| 12 | `.claude/plans/swarming-work/swarm/briefs/BC5.md` | Same; original documentation worker brief | I |
| 13 | `.claude/plans/swarming-work/swarm/charter.md` | Same; historical coordinator authority | I |
| 14 | `.claude/plans/swarming-work/swarm/coordination.json` | Same; historical lane topology | I |
| 15 | `.claude/plans/swarming-work/swarm/reports/.gitkeep` | Same; report directory | I |
| 16 | `.claude/plans/swarming-work/swarm/reports/BC2.md` | Same; historical contract evidence, not re-certified | I |
| 17 | `.claude/plans/swarming-work/swarm/reports/BC3.md` | Same; historical workflow evidence, not re-certified | I |
| 18 | `.claude/plans/swarming-work/swarm/reports/BC4.md` | Same; historical adapter evidence, not re-certified | I |
| 19 | `.claude/plans/swarming-work/swarm/reports/BC5.md` | Same; historical documentation evidence, not re-certified | I |
| 20 | `.claude/plans/swarming-work/swarm/reviews/.gitkeep` | Same; review directory | I |
| 21 | `.claude/plans/swarming-work/swarm/reviews/BC2.md` | Same; original review only | I |
| 22 | `.claude/plans/swarming-work/swarm/reviews/BC3.md` | Same; original review only | I |
| 23 | `.claude/plans/swarming-work/swarm/reviews/BC4.md` | Same; original review only | I |
| 24 | `.claude/plans/swarming-work/swarm/reviews/BC5.md` | Same; original review only | I |
| 25 | `.claude/plans/swarming-work/swarm/reviews/plan.md` | Same; original plan review only | I |
| 26 | `.claude/plans/swarming-work/work.json` | Same; original explicit work map | I |
| 27 | `.claude/plans/todo.md` | Same; Swarming links retained as historical, Universal remains current | R; no old permission reactivated |
| 28 | `.github/lintel/manifest.json` | Same; managed swarm adapter inventory | I, G; regenerate from `bin/li-copilot.py` |
| 29 | `.github/skills/li-swarm/SKILL.md` | Same; native Copilot swarm entry | I, G; generator retains workflow |
| 30 | `AGENTS.md` | Same; complete session protocol plus swarm ownership | I, G; source block equality checked |
| 31 | `CLAUDE.md` | Same; complete session protocol plus swarm ownership | I, G; source block equality checked |
| 32 | `README.md` | Same; discoverable swarm entry and honest execution fallback | I |
| 33 | `bin/li-copilot.py` | Same; swarm packaging/preflight added to existing adapter | R; ADR reference only beyond imported helper |
| 34 | `bin/li-scaffold` | Same; swarm resources available to fresh consumers | I |
| 35 | `bin/li-swarm` | Same; interpreter-explicit shell entry | I |
| 36 | `bin/li-swarm.py` | Same; read-only validate/wave/scope/status/verify CLI | R; ADR0027 annotation |
| 37 | `bin/li-work-artifacts.py` | Same; optional atomic swarm fields, original work-map API retained | R; shared parser import plus ADR0027 annotation |
| 38 | `docs/GLOSSARY.md` | Same; swarm terminology | I |
| 39 | `docs/README.md` | Same; both enterprise and Swarming navigation | R; additive merged links |
| 40 | `docs/architecture.md` | Same; existing enterprise boundary plus swarm mechanics | R; additive sections |
| 41 | `docs/concepts/brief-forge.md` | Same; explicit rather than fictional automatic invocation | I |
| 42 | `docs/concepts/swarming-work.md` | Same; operation, recovery and degradation guide | I |
| 43 | `docs/faq.md` | Same; discoverable opt-in and host limitations | I |
| 44 | `docs/multi-cli.md` | Same; native/sequenced/no-subagent workflow | I |
| 45 | `docs/showcase/lintel-the-harness.html` | Same; Swarming public entry | I |
| 46 | `docs/the-cycle.md` | Same; hybrid package BUILD plus optional swarm execution | R; both conflicting intents retained |
| 47 | `docs/wiki/README.md` | Same; generated concept discovery | I, G; `bin/li-wiki-gen` |
| 48 | `docs/wiki/skills.md` | Same; generated swarm skill discovery | I, G; `bin/li-wiki-gen` |
| 49 | `lib/swarm-schema.json` | Same; shared topology schema | I |
| 50 | `lib/swarm_contract.py` | Same; strict read-only parser, ownership and evidence gates | R; ADR0027 annotation |
| 51 | `scaffolding/01-foundation/.claude/SUBAGENT-GUIDE.md` | Same; downstream ownership discipline | I |
| 52 | `scaffolding/01-foundation/AGENTS.md.template` | Same; fresh-host complete protocol and swarm text | I, G; canonical protocol source |
| 53 | `scaffolding/01-foundation/CLAUDE.md.template` | Same; fresh-host complete protocol and swarm text | I, G; canonical protocol source |
| 54 | `scaffolding/01-foundation/SESSION-PROTOCOL.md` | Same; canonical shared swarm ownership and recovery | I |
| 55 | `scaffolding/01-foundation/templates/swarm/agent-brief.template.md` | Same; rich human-readable worker handoff | I |
| 56 | `scaffolding/01-foundation/templates/swarm/agent-report.template.md` | Same; structured worker evidence destination | I |
| 57 | `scaffolding/01-foundation/templates/swarm/agent-review.template.md` | Same; separate reviewer evidence destination | I |
| 58 | `scaffolding/01-foundation/templates/swarm/charter.template.md` | Same; coordinator authority and limits | I |
| 59 | `scaffolding/01-foundation/templates/swarm/coordination.template.json` | Same; opt-in topology without duplicated backlog | I |
| 60 | `skills/CATALOG.md` | Same; both hybrid BUILD description and swarm discovery | R, G; regenerate frontmatter through `bin/li-catalog.py` |
| 61 | `skills/brief-forge/SKILL.md` | Same; explicit opt-in handoff and evaluator policy | I |
| 62 | `skills/build/SKILL.md` | Same; package discipline plus isolated candidate-wave entry | R; main's full hybrid rules retained |
| 63 | `skills/capture/SKILL.md` | Same; durable swarm evidence closeout | I |
| 64 | `skills/cycle/SKILL.md` | Same; opt-in profile, not a tenth phase | I |
| 65 | `skills/full-engineering-pass/SKILL.md` | Same; DA/SC candidate parallelism with failure/fallback handling | I |
| 66 | `skills/plan/SKILL.md` | Same; packages and explicit optional swarm planning | R; original leaf/package authority retained |
| 67 | `skills/resume/SKILL.md` | Same; current work-map/source boundaries plus swarm recovery | R; neither initiative guessing nor old helper restored |
| 68 | `skills/review/SKILL.md` | Same; integrated-tree close gate after lane evidence | I |
| 69 | `skills/spec-kit/references/work-map.md` | Same; additive pointer over original Spec Kit artifacts | I |
| 70 | `skills/swarm/SKILL.md` | Same; init/run/status/resume/verify entry points | I |
| 71 | `tests/integration/copilot-kit.py` | Same; swarm resource preflight and consumer coverage | I |
| 72 | `tests/integration/swarm-workflow.py` | Same; actual CLI fixture workflow | I |
| 73 | `tests/integration/swarm-workflow.sh` | Same; discovered focused-suite wrapper | I |
| 74 | `tests/shape/swarm-contract.sh` | Same; source/entry/authority drift assertions | I |
| 75 | `tests/unit/brief-forge-evaluator-runs.sh` | Same; nested policy and unknown-evaluator regressions | I |
| 76 | `tests/unit/swarm-contract.py` | Same; existing parser, scope and recovery regression intent | I |

## Checkpoint verification and remaining work

Before the merge commit, a Python/Git comparison enumerated the exact 76-path delta,
resolved the ADR destination, required every destination to exist, and compared source
bytes after LF normalization. Every historical swarm brief/report/review/charter stayed
source-identical. Current MEMORY, lessons, working-state and main ADR0026 stayed identical
to `21261f1`. The historical design's ADR link is the sole plan-document correction.

Executed: `python tests/unit/swarm-contract.py` (20 tests PASS);
`python tests/integration/swarm-workflow.py` (PASS);
`python bin/li-instructions.py check` (4 synchronized entry files PASS);
`bash tests/shape/adr-numbers-unique.sh` (27 unique ADRs PASS);
`bash tests/shape/build-workflow-contract.sh` (PASS).
These preserve baseline behavior, not acceptance of the known SW-01..06 defects.

No historical report is fabricated or amended to claim these checks. The P04 fixes need
new negative and boundary tests. A22.7 shared P05/P08/P09 binding, independent package
review, stable combined-tree regeneration and final integrated verification remain open.
MasterSession owns common generated outputs; this lane reports their inputs rather than
regenerating them after the checkpoint.
