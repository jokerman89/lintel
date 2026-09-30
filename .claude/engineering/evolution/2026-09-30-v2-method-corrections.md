---
slug: v2-method-corrections
date: 2026-09-30
cycle_id: v2-method-corrections-20260930
operator: current operator
affected_paths:
  - agents/
  - skills/
  - bin/li-catalog.py
  - bin/li-run
  - lib/capability-selections.json
  - .github/agents/
  - .github/skills/
  - tests/
risk_class: high
breaking_change: false
---

# Structure change: V2 method corrections

## What changes

Correct the explicitly mapped original review items without retiring entrypoints,
moving domain capabilities to an unselected pack or changing host permissions.
Engineering modules reuse the existing admission owner and have an explicit
catalog selection. Role and workflow outputs retain evidence, uncertainty,
applicability and authority instead of unconditional success or style rules.

The original maps remain authoritative:
[core corrections](../../plans/remaining-corrections/work.json),
[routine corrections](../../plans/v2-routine-corrections/work.json),
[agent methods](../../plans/v2-agent-corrections/work.json) and
[skill methods](../../plans/v2-skill-corrections/work.json).
This record does not replace their task IDs or introduce another backlog.

## Backward and forward compatibility

Keep current skill/agent names, tools, optional model/memory metadata, profile and
review schemas, stored filenames and required independent controls. The catalog
adds one ordinary engineering selection; existing selections and core stay
intact. A valid generated artifact is not proof of native activation, entitlement,
policy enforcement or model behavior. Source size is not a hard client limit.

No old evidence is rewritten. Native adapters, catalog and wiki are regenerated
through their existing owners after source integration. No hook registration,
live provider, private pack export, licence change or release publication follows
from this source change.

## Verification

Original source writers used bounded synthetic checks, with failures preserved
and specification then quality review on each subject. A capacity-stopped writer
was recovered from exact persisted files into a separate owned target and
verified there; its old profile was not transferred. The maps distinguish those
observations from subsequent integration.

The final candidate requires actual joined checks, regenerated-output checks,
the unchanged strict hosted matrix and content-bound integrated review/QA/SHIP.
Documentary fixtures do not establish live-model efficacy or universal client
acceptance. Remaining source-test limitations are recorded, not called passes.

## Rollback

Use ordinary revert commits for the selected integration changes after checking
their consumers. Preserve original source/review histories, user state and
compatibility names. Do not reset a shared checkout, rewrite history, downgrade
mandatory controls or reuse a published product version.
