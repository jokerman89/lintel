---
name: handoff-size-check
layer: foundation
description: Use before handoff to estimate the selected work-map artifacts and actual warming inputs against reported host headroom, keeping unknown capacity and advisory limits explicit.
color: yellow
tools: Read, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

# Handoff-size check

Keep the two-ended scope check: SENSE's elephant hint catches broad work before
planning; this reader measures the actual handoff after PLAN and after CAPTURE.
It is a batch payload estimate, not monitoring, context compaction or host control.

## Select the payload

Use the [shared work-map contract](../spec-kit/references/work-map.md) and its
`bin/li-work-artifacts.py` reader. Select `--map <work.json>` explicitly or retain
`LINTEL_WORK_MAP` from the verified lifecycle. No runtime/state/plan.md default,
newest initiative, guessed sibling spec/prompt or second task store is allowed.
For a legacy explicit plan (`<plan.md>` or `--plan <path>`), preserve that entry as
an unmapped inspection: use P03 `context_select --path <literal-file>` and
`context_budget` on its returned bytes. Name exactly which original linked inputs
were supplied. Missing spec/handoff/warming remains incomplete; never guess siblings
or create a competing backlog merely to estimate a file. Mapped lifecycle handoffs
use the common map command below.

Before policy consumption, verify the saved P07 reference through `workflow_resume`.
Add literal `--warm-path` arguments from P03's actual context selection. Keep those
paths bounded and preserve source/target separation. No warming input supplied
means **not supplied**, not a verified zero-byte warming workload.

```bash
python="${LINTEL_PYTHON:-python3}"
"$python" "${LINTEL_SOURCE_ROOT:?select trusted source}/bin/li-work-artifacts.py" \
  --repo "${LINTEL_REPO_ROOT:?select target}" \
  --map "${LINTEL_WORK_MAP:?select work.json}" --view budget
```

The reader includes distinct map/spec/plan/tasks/prompt/constitution files once.
It uses P03 `select_files` and `context_budget`; it does not infer token usage
from optional/manual event counters. Append known inputs only when their source
is actually available:

```text
--warm-path docs/selected-adr.md
--capacity <host-reported tokens> --capacity-source <actual host source>
--used <tokens> --usage-source <actual source> --usage-kind observed|estimated
--reserve <output reserve>
```

## Interpret the result

Report the original artifact paths, selected bytes, byte/4 token estimate and
its limitations, warming selection, capacity/usage source and admission result.

| Result | Meaning and next action |
|---|---|
| within-reported-headroom | Estimate fits supplied observations; not exact tokenizer or cost evidence |
| estimated-fit | Headroom also depends on estimated usage; retain that uncertainty |
| over-capacity | Split the handoff or reduce future selected reads before that load |
| unknown | Capacity or usage was not supplied; no fit/healthy verdict is possible |
| missing/malformed input | Incomplete check with nonzero helper exit; repair selection |

The shared policy is **advisory** for PLAN and CAPTURE. An estimate/unknown result
does not itself pause their independent work. An explicitly required task limit or
an actual host refusal still blocks the affected load; record that source instead
of inventing a universal 500k cap. Mode changes, disk cleanup and future exclusions
cannot reclaim already-sent conversation context.

## Retained choices and limits

- For a broad handoff, propose splitting coherent packages, narrowing warming
  inputs or checkpointing and restarting. Do not silently cut authority files.
- Preserve `--skip-handoff-size-check`/`SKIP_HANDOFF_SIZE_CHECK=1` as an advisory
  caller opt-out; record **not run**, never a green result or a required-policy bypass.
- Optional observation uses the existing writer, for example
  `audit_log handoff-size-checks size_check "work_map=$LINTEL_WORK_MAP"
  "basis=estimated" "admission=unknown"` with actual returned values. No automatic
  global logging or calibration is enabled.
- Exit 0 from the mechanical reader means the estimate was computed, not that
  capacity is known or delivery is cleared. Malformed/unreadable selections fail.

## Status and recovery

DONE means a reported estimate was produced; DONE_WITH_CONCERNS includes unknown
headroom, omitted warming or an advisory excess. NEEDS_CONTEXT means missing
selection/evidence. BLOCKED is reserved for a real required limit, denied read or
failed required input. Keep the current map and repair that input, never silently
fall back to another initiative or a mode-specific capacity guess.

PLAN, CAPTURE and standalone callers use this same interpretation. For deeper
resource advice use `/li:context-budget`; it does not change the model window.
