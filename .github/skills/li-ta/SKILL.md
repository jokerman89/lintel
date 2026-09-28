---
name: li-ta
description: Use for technical-architecture depth — service boundaries, API contracts, dependency graphs, scaling plans, complexity audits, and quality attributes. Reach for it when a design needs architectural rigor beyond what PLAN gives. Runs full, loop, or single-capability, dispatching to the architecture agents and scoring against a rubric.
---

> **Lintel on GitHub Copilot.** Generated from `skills/ta/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/ta/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/ta/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the TA (tech-architecture) module, invoked within the selected lifecycle phase.

## What this module does

Produces architecture-grade decisions and contracts when work has architectural depth. Three granularities — full pass for new projects, loop iteration for refinement, single action for targeted ops.

For invariant/topology choices, failure isolation, tail-latency composition and capacity
assumptions, read [architecture decision methods](../../../skills/ta/references/decision-methods.md).

| Entry | When | Outputs |
|---|---|---|
| `/li-ta full` | new project / major scope change | `system-arch.md` + ADR set + interface contracts + dependency graph + non-functional requirements |
| `/li-ta loop` | mid-cycle architecture iteration | revised ADRs + diff against prior decisions + impact analysis |
| `/li-ta <capability>` · `/li-ta single --action <capability>` | targeted operation (see Sub-capability dispatch) | one artifact per the dispatch table below |

## When to use

- New service, API, dependency restructure, cross-system boundary
- Operator wants explicit architectural decisions documented as ADRs
- The active workflow explicitly requests architectural depth; no automatic hook dispatch is implied
- Work requires architecture-grade artifacts

## When NOT to use

- Bug fix, small refactor, single-file change → use `/li-cycle --mode hotfix`
- Data-model work without architectural impact → use `/li-da` (v4.2)
- Pure observability/deployment work → use `/li-dh` (v4.4)

## Sub-capability dispatch

The seven capabilities remain direct entry points, not separate skills. Read the
named role from the trusted source and use the actual host's delegation operation
or an explicit serial handoff. The caller persists returned artifacts under the
selected attempt. Follow the [shared module procedure](../../../skills/full-engineering-pass/references/domain-handoff.md#module-caller-procedure).

| Capability | Dispatches to (agents) | Produces | Raise-help / notes |
|---|---|---|---|
| `api-design` | APIDesigner | REST/GraphQL/gRPC interface spec with versioning + breaking-change analysis | prefs: `api_style`, `versioning`; validation checklist below |
| `dependency-graph` | Explorer + Architect | module dependency map + `graph.dot`, circular-detection, layering audit | owns the shared language-detect heuristic (below) |
| `boundary-review` | BackendArchitect + Architect | bounded-context drift and failure-isolation report | reuse dependency evidence only when its relevant input identity is unchanged; request SystemArchitect explicitly for an invariant/NFR question |
| `complexity-audit` | Architect | per-component cyclomatic + cognitive scoring and refactor options | obtain actual project budgets or label exploratory measurements advisory; report tool/version and excluded files |
| `scaling-plan` | CapacityPlanner + BackendArchitect | capacity model, ranked bottlenecks and priced/qualitative projection | target and baseline come from the brief; missing measurements remain unknown, not default 3x growth |
| `contract-collision` | APIDesigner + Architect | impact across actual consumer versions and migration options | requires named interface/change; even one mandatory consumer break needs a decision; no universal deprecation window |
| `quality-attributes` | SystemArchitect + Architect | non-functional requirement spec + verification path per NFR | backs the `non_functionals_specified` checkpoint; dims: latency p50/p95/p99 per journey, throughput RPS, error-rate %, availability SLA, observability signals per component |

### api-design — validation checklist

- [ ] Each endpoint has method, path, request schema, response schema, error responses
- [ ] Versioning strategy applied consistently
- [ ] Breaking-change analysis present (if v2.x or higher)
- [ ] Authentication/authorization noted
- [ ] Rate-limit / quota notes per endpoint
- [ ] Example payload(s)
- [ ] OpenAPI/Protobuf/SDL artifact if applicable

### complexity-audit — per-language tools

go → `gocyclo -over <budget>` · python → `radon cc -n B -s` · rust → `cargo-complexity` ·
node → `npx eslintcc --rule complexity` · other → `lizard`

### dependency-graph — language detection (shared helper)

`package.json` → node · `go.mod` → go · `Cargo.toml` → rust ·
`pyproject.toml`/`requirements.txt` → python · `pom.xml`/`build.gradle` → jvm · `*.csproj`/`*.sln` → dotnet

## Workflow
1. Select `full`, an explicitly saved `loop`, or one named capability/`single --action`.
   Unknown capability or absent saved iteration is NEEDS_CONTEXT, not a new guessed run.
2. Follow shared **Select original work and live policy**: actual `work_context`/
   `workflow_inspect`, original package/leaves and verified P07 reference. Read
   `engineering.tech_architecture.*` only from the verified pack or explicit advisory
   invocation inputs. Preserve the existing API style/framework and accepted ADRs.
3. Prepare immutable P05 obligations and a domain request with the checkpoint table
   below. Record original output states before start. Supply actual role/mode/scope.
4. Perform the method with real available tools; persist design, consumer evidence and
   checks, then record the result. Explorer locates; Architect synthesizes/designs;
   independent reviewers assess, not repair. Lack of a measurement is unverified.
5. Freshly verify each required result, externally prepare the final P05 context and
   obtain independent spec then quality/QA. Only the original task owner updates status.
   Numeric rubrics are advice, never review or release clearance.

## Checkpoint ownership

| Checkpoint | Method and receiver | Artifact and observable acceptance |
|---|---|---|
| `discovery_complete` | Explorer evidence lookup, then Architect dependency synthesis | dependency graph + consumer registry; distinguish observed edges, dynamic unknowns and intentional cycles |
| `decision_documented` | Architect/BackendArchitect options; ADRDrafter proposed record | viable alternatives, invariant, decision owner and downside; proposed is not accepted |
| `contract_locked` | APIDesigner contract, actual consumer-version verification | OpenAPI/SDL/protobuf + migration/notification evidence where required; additive is consumer-specific |
| `complexity_within_budget` | Architect interprets actual analyzer output | measured scope/tool, applicable budget and bounded refactor recommendation; no metric-only rewrite |
| `non_functionals_specified` | SystemArchitect constraints, Architect fit | NFR/invariant spec with source, workload, boundary and verification path; no sum of component p99s |

For `loop`, compare the selected prior ADRs/contracts and changed dependencies; retain
old artifacts and revisit affected checkpoints with new input identity. Returning
to a checkpoint never restores source files. For single API design, do not perform
a capacity sweep unless its unresolved requirement truly depends on it.

### Advisory six-dimensional rubric

```
| Dimension | Score 0-100 |
|---|---|
| Decisions documented (ADR coverage) | <D1> |
| Contracts locked (interfaces signed + versioned) | <D2> |
| Complexity within budget | <D3> |
| Non-functionals specified | <D4> |
| Consumer impact analyzed | <D5> |
| Alternatives considered | <D6> |

Record each score's evidence and untested coverage. Any applicable mandatory
failure/error/unverified control blocks regardless of scores or operator preference.
```

Use the observable checkpoint criteria above, citing the actual artifact and missing
evidence. A checklist count alone is not calibrated architectural quality.

### Handoff and recovery

Return named architecture artifacts, exact original work/profile/attempt references,
control/evidence links, advisory scores, limitations and next owner. Use the shared
start/result publication and cold-continuation table. Interrupted/failed output stays
visible. An audit record is optional observation unless policy explicitly requires it;
then verify real persistence without claiming it grants acceptance.

## Status protocol

- **DONE** — selected results, required checks and independent acceptance complete
- **DONE_WITH_CONCERNS** — required gates pass; remaining concerns are advisory only
- **BLOCKED** — required checkpoint/evidence/policy/review failed or unavailable
- **NEEDS_CONTEXT** — unknown capability for single, OR no prior state for loop

## Integration

**Reads:**
- Original mapped artifacts and pinned pack fields; explicit advisory inputs, no automatic personal preference read
- `lib/pack-resolver.sh` for pack policy
- Existing arch agents: Architect, BackendArchitect, APIDesigner
- New agents: SystemArchitect, CapacityPlanner
- Existing ADRs in the repository's declared decision location

**Writes:**
- Selected `system-arch.md`, interface/ADR/NFR artifacts and iteration comparison;
  runtime start/result files under `.claude/runtime/state/domains/<operation>/iNNNN/`.
- Existing `state/ta/` artifacts remain usable only when explicitly selected and verified.
- Brief Forge only when explicitly invoked/configured; no automatic hook activation

**Triggered by:**
- Operator: `/li-ta {full|loop|single --action <name>}`
- BUILD phase: invokes as sub-module when architectural intent detected
- `/li-full-engineering-pass`: first module in the composition DAG

**Hooks** (dormant by decision, ADR-0008 — ship in `hooks/shared/` but are opt-in, not auto-registered):
- `hooks/shared/ta-arch-drift-warn/` (pre-edit on ADR-claimed files)
- `hooks/shared/ta-contract-collision-warn/` (pre-edit on interface files)
- `hooks/shared/ta-complexity-budget-warn/` (pre-commit)

## Anti-patterns

- **Skipping single granularity to "be safe"** — single is the operator's explicit choice; honor it
- **Treating checkpoint failure as terminal** — checkpoints surface, recover, continue
- **Inventing new agents when existing ones cover** — Architect/BackendArchitect/APIDesigner cover most TA work; new agents only for genuinely new capability
- **Hardcoding api_style / versioning** — use actual verified pack fields or explicit advisory inputs
- **Silent score-below-threshold** — surface to operator with dimension breakdown; never auto-pass
- **Confusing a warn-hook with policy** — advisory warnings are not enforced controls;
  applicable mandatory requirements still block independently of the warning mechanism
