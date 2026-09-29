---
name: context-budget
layer: foundation
description: Use before a large read or handoff, or when context headroom and resource advice are needed; keep observed usage, source estimates and unknown limits distinct.
color: cyan
tools: Read, Bash, Grep
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Context budget

Report four different quantities separately: selected source size, currently active model
context, cumulative/billable usage and disk storage. They are not interchangeable.
There is no universal 1M window and a saved marker cannot change the host's limit.

Use before a large warm, to answer a resource question or to diagnose repeated/irrelevant
context. A checkpoint file on disk does not reset active usage. A new session may have
different host-reported capacity and preloaded instructions.

## Select one route

This is the single owner of budget observation, resource advice and selected-work
handoff sizing. The retained `perf-mode` and `handoff-size-check` names delegate
here; ordinary PLAN/CAPTURE work calls this owner directly, without a new subagent.

| Leading selector | Method | Provider |
|---|---|---|
| none | Observation | `context_budget` |
| `--advice` | Working-set and checkpoint advice | `context_perf` |
| `--handoff` | Explicit mapped-artifact budget | `li-work-artifacts.py --view budget` |
| `--watch` | Existing instruction-driven warning comparison | Watch section below; no daemon or configuration parser |

Choose one route before reading configuration or invoking a provider. Conflicting
or repeated selectors are errors. `--budget` means a positive integer in advice,
but a selected YAML configuration path in watch. `--mode soft|hard|both` remains
watch-only; legacy handoff `--plan` is a file selection, not an advice selector.

For observation, advice and mapped handoff, run the single
[routing reference](references/route.sh):

```bash
source_root="${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}"
bash "$source_root/skills/context-budget/references/route.sh" "$@"
```

It removes only its own leading advice/handoff selector and passes quoted arguments
to the existing provider. The reference locates helpers in its own source bundle,
not the target working directory or a home fallback. Output and errors remain the
provider's; it creates no profile, state, audit record or host setting.

Watch and legacy-plan selection are explicit workflow steps below. Sending their
raw flags to the routing reference returns a diagnostic, not a simulated result.

## Shared observation and interpretation

The helpers are read-only. With no observations, capacity, usage and headroom remain
unknown. `--bytes <N>` is the actual selected manifest's bytes; its `ceil(bytes / 4)`
input estimate is not measured active usage.

Only supply `--capacity <N> --capacity-source <observation>` for the current host/model
limit actually exposed by the client. Supply `--used <N> --usage-source <observation>`
for active usage; add `--usage-kind estimated` for a stated heuristic. `--reserve <N>`
reserves explicitly chosen output/tool headroom. A known over-capacity selection is
reported as such. An estimated fit is labeled estimated, never verified.

Read `.claude/runtime/state/context-budget.md` as a source/read history when present.
Do not infer the full conversation from it, sum repeated loads as exact active usage,
or treat absent telemetry/logs as an empty window. Report observation age and remeasure
before relying on earlier headroom.

| Admission | Meaning and next action |
|---|---|
| `within-reported-headroom` | The estimate fits supplied observations; not exact tokenizer or cost evidence |
| `estimated-fit` | Usage was estimated; retain that uncertainty |
| `over-capacity` | Split the handoff or narrow future reads before loading it |
| `unknown` | No fit or healthy verdict is possible without the missing observation |
| missing/malformed input | A nonzero provider exit is an incomplete check; repair the original selection |

An estimate or unknown headroom is advisory for PLAN/CAPTURE and does not halt
independent work. An explicitly required policy/task bound or actual host refusal
still blocks its affected load. A successful reader exit is not delivery clearance.

## Advice (`--advice`)

Routine small edits need no extra resource-advice plan.

Retain `--budget <N>`, `--ceiling <N>`,
`--decay-policy <prompt-operator|aggressive|conservative|retain-all>`,
`--cost-estimate` and `--off`. These are local advice, not model capacity or settings.
The observation flags above keep exactly the same meanings. `context_perf` reports
`host_settings_changed: false`; cost is unknown without actual billing/pricing.
`--off` ends advice, not a fictional active host mode. Historical perf-mode markers
are not activation evidence.

Use the result to improve the next decision:

1. Name the deliverable and the smallest useful evidence set. Read authoritative
   requirements first, current failures/relevant code next, optional history only
   when needed. Preserve original task IDs, paths, revisions and rejected hypotheses.
2. Preview bounded sources through context-warm; give each selection a reason and
   stop condition. Do not suggest a whole-repository load or infer capacity from a
   model name, preference or checkpoint.
3. Reserve verification/repair space. If reported headroom is insufficient, suggest
   a coherent checkpoint and fresh session, not deletion of already-sent context.
4. If pricing matters, require current source/date/currency and actual billable
   input/output/cache observations. Otherwise state unknown; do not invent runway.
5. Suggest host controls only when available and authorized. Ask only for unresolved
   material decisions, never merely to activate this advisory route.

## Handoff (`--handoff`)

Use the [shared work-map contract](../spec-kit/references/work-map.md).
Supply `--map <work.json>` explicitly or retain `LINTEL_WORK_MAP` from the verified
lifecycle. Before policy consumption, verify that lifecycle's saved profile through
`workflow_resume`; never bootstrap, rebind or adopt another work context to estimate
a handoff. Missing required policy stays blocked, not a neutral fallback.

The selected reader counts distinct map/spec/plan/tasks/prompt/constitution files
once. Preserve the original work, package and leaf identities. Add literal
`--warm-path` values from the actual bounded P03 selection. Warming omitted means
`not-supplied`, not a verified zero-byte workload. Use the observation flags above
only with their actual provenance. Repository and budget view cannot be replaced
by caller flags.

Do not infer newest work, sibling files, a second task list or available capacity.
Preserve `--skip-handoff-size-check` / `SKIP_HANDOFF_SIZE_CHECK=1` in PLAN/CAPTURE:
record **not run**, never a pass or a waiver of a required bound. Optional logging
remains a separate authorized producer; the routing reference writes nothing.

Do not silently cut authority files to fit a budget. Split coherent packages or
narrow optional reads while preserving required policy, pattern and acceptance inputs.

### Optional handoff observation

Only when separately authorized, the caller may opt-in to record an actual
handoff estimate. Set `budget_work_map` and `budget_admission` from the actual
reader result, retaining its verified work/profile context and approved audit roots:

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/bin/_audit.sh"
audit_log handoff-size-checks size_check \
  "work_map=${budget_work_map:?use the actual returned work map}" \
  "basis=estimated" "admission=${budget_admission:?use the actual returned admission}"
```

The read-only routing reference never calls this producer. No automatic telemetry
or calibration is enabled; a missing audit record stays unobserved.

### Legacy selected plan

For an explicit positional plan or `--plan <path>`, retain unmapped inspection.
Use the existing `context_select --path <literal-file>` reader; stop on its error.
The caller then passes the manifest's actual bytes to ordinary observation and
names the supplied original inputs. This is a manual join of existing readers,
not a new legacy-plan parser or a verified complete mapped handoff.

Missing spec/handoff/warming stays incomplete. Never guess siblings, fabricate a
map, silently drop `--plan`, or report that the routing reference executed this
manual step. A denied selection or required limit remains a refusal.

## Local thresholds and compatibility

`mode_envelopes` remain optional **local advisory workload thresholds**, not client limits
or automatically installed settings. Retain the historical examples for existing plans:

```yaml
mode_envelopes:
  hotfix:              { soft: 200k, hard: 300k }
  customer-engagement: { soft: 500k, hard: 750k }
  research-dive:       { soft: 750k, hard: 900k }
  demo-prep:           { soft: 300k, hard: 450k }
  internal-tool:       { soft: 400k, hard: 600k }
```

The former 500k soft / 750k hard figures are **not defaults for model capacity**.
No mode, company context or larger window is inferred when configuration is absent.
An operator may choose lower local warnings; a local threshold can never raise a host
limit. A policy-mandated admission bound stays mandatory and must name its policy source.
Synthetic vs real warming describes provenance only: **both** spend tokens when sent.
There is no synthetic-brief exemption.

## Watch mode (`--watch`)

Keep `--watch`, `--budget <yaml>`, `--quiet` and `--mode <soft|hard|both>` as skill inputs.
The skill reads the selected configuration as data and passes only actual observations
to the shared helper; it does not pass those skill-only flags to `context_budget`.

1. Read explicit watcher configuration, if authorized, and show its source. Existing
   `soft_token`, `hard_token`, `soft_tool_calls`, `hard_tool_calls` keys denote local warning
   thresholds. Missing keys may use labeled advisory examples (50000/80000 tokens and
   80/130 tool calls), never model capacity. Other clients' key shapes need adapter mapping.
2. Read available session telemetry. Mark each token/tool count observed, estimated or
   unknown and identify its source. Do not fabricate elapsed time or per-turn usage.
3. Compare known counts with selected thresholds: below soft, warning at soft, red at hard.
   Missing counts remain unknown; missing all telemetry cannot produce a healthy green.
4. With `--quiet`, suppress only a known below-threshold result. Still report unknown/error.
   In CI, report red/unknown as non-success if this check is required; zero observations
   are not a verified pass. This skill is not a background watcher or a registered hook.
5. Pass only derived, sourced observation arguments to the shared reader, not
   `--watch`, the YAML path, `--quiet` or the threshold `--mode`.
6. Recommend bounded retrieval, `/li:pause` and a fresh session where useful.
   Only suggest a host compaction control when that exact control is available and its
   result can be observed. `/clean` or disk archival alone cannot reclaim model context.

## Report

```text
Host capacity: unknown | <observed limit, source and time>
Active usage: unknown | <observed/estimated count, source and time>
Selected sources: <paths, bytes, estimated input tokens>
Headroom: unknown | <value, observed/estimated>
Local warning threshold: unset | <configured value and source>
Billable cumulative usage/cost: unknown unless separately observed
Disk cleanup: none performed
```

Never turn an advisory color/score into a policy clearance. Warming, cooling, save and
restore keep their own read/mutation boundaries and preserve the owner-aware checkpoints.

For handoff also name the selected map/artifacts, actual warming, incomplete inputs
and original work/profile references. For advice include local preferences and the
checkpoint recommendation. No extra agent is needed just to measure the payload.

For the retained handoff status vocabulary, DONE means an actual estimate was
reported; DONE_WITH_CONCERNS includes unknown headroom, omitted warming or advisory
excess. NEEDS_CONTEXT means missing selection/evidence. BLOCKED remains a required
limit, denied read or failed required input, not an ordinary advisory unknown.
