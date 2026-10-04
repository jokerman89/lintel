---
name: maintenance
layer: foundation
description: Use for on-demand storage/context guidance, scoped path diagnostics and labeled usage estimates without treating partial logs as health or claiming model compaction.
color: yellow
tools: Read, Write, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
  - cli: copilot
    level: full
---

# Maintenance

Retained compatibility front door for four on-demand routes. Choose one requested
mode, then follow its existing owner in full; do not run another path manifest,
token predictor, event parser or cleanup procedure here.

| Retained mode | Owner and supported invocation | Meaning |
|---|---|---|
| `--force-compact` | [Context budget](../context-budget/SKILL.md): `/li:context-budget --advice` | Working-set/storage advice, not compaction |
| `--monitor-paths` | [Doctor inspection](../doctor/references/inspection.md): `/li:doctor --layers-only` | Actual source/foundation/layout/adapter observations |
| `--simulate-tokens <workflow>` | [Context budget](../context-budget/SKILL.md): observation, or `--handoff --map <selected work.json>` for explicit mapped inputs | Selected-input estimate, not a workflow-cost prediction |
| `--rust-report` | [Audit observations](../audit/references/method.md): `/li:audit --category usage-skill --since 30` | Recorded usage samples, not a disuse verdict |

The skill names above are workflow routes. Doctor's filtered view is presentation,
not a `--layers-only` argument to `bin/li-doctor`; its owner supplies the real helper
arguments and preserves the complete diagnostic exit. Audit maps its filters to the
existing event reader. Use native entrypoints actually available on the host, or the
same trusted owner through a permitted file handoff; never bypass a denied operation.

## Context and estimates

`--force-compact` cannot clear a conversation, enable a watcher or invoke an unavailable
host control. Follow context-budget's advice and, if useful and authorized, its
pause/fresh-session/resume route. Retain the same original map, verified profile and
required policy; do not select a newer basename as the current task.

For `--simulate-tokens`, retain the supplied workflow name as a report label only.
Do not pass it as a size or unsupported provider flag. Use actual selected bytes with
the owner's `--bytes` observation, or explicitly selected mapped artifacts through
`--handoff --map`. Pass `--capacity`, `--capacity-source`, `--used`, `--usage-source`
and other owner-supported observation arguments only when those facts exist.
No selected inputs or compatible measurements means **unknown**, not a stock token range.
Selected input size, active context, cumulative usage and disk bytes remain separate.
No billing/cost or p95 precision can be inferred from a few optional manual entries.

## Path and usage results

`--monitor-paths` returns doctor's actual results. A missing/failed required observation
is incomplete, not a successful partial health check. Repairs, migration and profile
changes require separate scoped authority; file presence is not host activation.

`--rust-report` uses only explicitly authorized log roots. If requested, inspect other
actual `usage-*` categories through audit too. Count **recorded** invocations in the
named source/window; the historical fewer-than-two samples threshold is only a review
prompt for observed rows. An absent name/log is **unobserved/coverage unknown**, not
unused or safe to delete. Preserve malformed-line diagnostics and preview limitations.
Use catalog's ordinary metadata separately if an explicit join was requested, not a
different catalog feature or an implicit personal telemetry scan.

## No implicit cleanup

All four routes are read-only/advisory. Age and partial usage never authorize archiving,
deletion, profile changes or a global sink. Any later disk operation must name exact
owned paths and destination, preserve unrelated content, and use the existing owned
snapshot/recovery method under separate authority. Report storage changed only after
observing it; active-context reclamation remains unestablished without actual host evidence.

Return the selected owner, actual command/result, observations, limitations and one
appropriate next step. Missing tools, denied reads and parser failures remain explicit;
there is no automatic fallback estimator, background monitor or maintenance daemon.
