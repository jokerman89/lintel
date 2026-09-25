---
name: welcome
layer: foundation
description: Use on first run to choose a useful task, inspect the actual client surface and take a proportionate plan, build, review or resume path.
color: green
tools: Read, Bash
voice: internal
cli_support: [claude-code, codex, copilot, cursor, gemini, opencode, droid]
necessity: OPTIONAL
gap_if_skipped: "The operator has no guided first task or clear distinction between installed resources, host capabilities and observed execution."
navigation:
  primary_intent: task-first onboarding with truthful client boundaries
  triggers:
    - operator just installed Lintel
    - operator asks how to start
  sibling_workflows:
    - /li:cli-fingerprint
    - /li:cycle
    - /li:doctor
  risk_level: low
  auto_mode_eligible: false
  estimated_tokens: 2000
---

# Welcome

Start with what the operator wants to accomplish, not a vendor, installation ceremony or
catalog tour. Show how a bounded task leaves acceptance evidence and a useful next-session
handoff. Reuse the canonical workflows and capability reader; do not implement a second
onboarding runtime.

## 1. Identify the useful next task

Retain the stated request and existing authorization. Ask only for missing decisions using
the host's actual question tool; use conversation only where no question tool exists.
Maintenance, migration, research and reviews do not require venture or customer-engagement
framing. Company standards and optional audience lenses come from the project or selected pack.

Read the repository's instructions, relevant decisions, memory and active work map first.
If a task is already planned, offer its next authorized card rather than producing a new plan.
If the operator only wants orientation, do not create jobs, plans or runtime files.

## 2. Identify the exact surface and available operations

Use `/li:cli-fingerprint` and the Universal adapter. CLI, desktop, IDE and cloud are distinct
even when a product shares an engine. The canonical source is `lib/cli-tiers.yaml`.

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-client-capabilities.py" show --client "$surface"
```

Set the trusted source and actual surface before running the example; `python` is valid
when that is the installed Python 3 command. `cli_tier_field` in `lib/cli-tiers.sh` remains a
conservative compatibility view for old consumers, not proof that an operation is available.

Show three separate facts: dated vendor documentation; the delivered discovery/binding or
manual route; and version-specific observed evidence. Default unrun scenarios to `not_run`.
Inspect available tool schemas and permissions rather than inferring them from a model,
process name or plugin manifest. Unknown surface means an explicit manual route, not failure
of the common workflow.

Native discovery can expose `li-plan`, `li-build`, `li-review` and `li-resume`. Invoke the
names the client actually lists. If discovery is absent, explicitly read the canonical
SKILL.md through `.github/lintel/START.md` in a portable kit. Do not promise every specialist
workflow was tested in that host because its source is bundled.

## 3. Discover the selected method

Use the accepted catalog before opening a specialist body. Resolve the trusted source
from the loaded adapter, independently of the working target. Select a nonempty keyword
from the actual task; do not scan personal skill trees or load all prompts for orientation.

```bash
: "${LINTEL_SOURCE_ROOT:?select the trusted Lintel source}"
: "${keyword:?select a nonempty task keyword}"
"${python_cmd:-python3}" -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" \
  --json --kind=all --query="$keyword"
```

The keyword is one quoted literal argument. A valid zero-match result calls for a broader
keyword, not a made-up capability. For an explicitly requested demo-script exploration,
use the existing projection instead:

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=demo-script
```

Present the returned method, alias, source-relative path and unknown/staged limitations.
Read only the selected body under that same trusted source. Retain shared dependency and
notice obligations without warming all resource bodies. Metadata is not native discovery,
permission or execution; actual host facts still come from step 2. No selection preserves
normal task-first onboarding. See [metadata](../catalog/references/metadata.md) and
[selections](../catalog/references/selections.md).

If execution is unavailable, disclose the committed `skills/CATALOG.md` as a skills-only
snapshot, or read a specifically selected canonical file through a permitted file tool.
An invalid source/parser is an error, not an empty success or an instruction to regenerate.
This orientation creates no work map, profile, cycle, draft or registration.

## 4. Walk through the method without implying execution

For orientation, `/li:cycle --dry-run` describes the phases without running them. Treat that
as a workflow preview, not a measured host test, successful build or hook demonstration.
Keep it read-only and verify no state was changed if claiming a no-mutation preview.

For an already authorized real task, follow the selected workflow instead of replacing it
with a throwaway demo. The shape is SENSE, SCOPE, DEFINE, DISCOVER, PLAN, BUILD, REVIEW, SHIP,
CAPTURE; small work can use a shorter route.

## 5. Explain controls and honest fallback

The shipped hook adapter is a Claude Code mechanism, separate from the common workflow.
Claude plugin installation can register selected hooks; bare hook files are inert until
registered. The portable repository kit installs no hooks on any client. File presence,
vendor documentation and `hooks_supported` are not proof that a hook fired.

Do not auto-edit settings, activate hooks, invoke paid clients or send project content to
demonstrate onboarding. Only run a control demo when specifically authorized and using an
isolated non-sensitive fixture; capture the actual registration, input, outcome and limits.
Otherwise explain the boundary and keep required unverified controls outstanding. Preserve
the optional [Claude hook path](../../docs/claude-code.md) without requiring it.

Use actual delegation when available. Without attributable isolated writes, serialize.
Without delegation, retain scoped package briefs, reports and restart for manual/external
work. An implementer's self-review never clears a requirement for independent review.
No browser tool means browser evidence remains missing, not a fabricated successful demo.

## 6. Choose the proportionate path

| Need | Canonical workflow |
|---|---|
| Small authorized fix | `fix`, or direct scoped work with verification |
| Find why something fails | `investigate` |
| Substantial change | `plan` / `cycle`, then authorized `build` |
| Verify behavior | `qa` |
| Review only | `review`, with no write escalation |
| Continue work | `resume`, preserving the original map and IDs |
| Diagnose installation | `doctor` plus the installed adapter's `check` |
| Explore specialist methods | `catalog` metadata, then only selected bodies |

Close with the actual next action and any missing tool, control or review. The catalog's
size does not establish token cost or productivity. Do not quote an unmeasured time saving.
See [getting started](../../docs/getting-started.md) and [client adapters](../../docs/client-adapters.md).

## Failure recovery

Missing source or malformed registry: report the exact error; do not fabricate a capability
tier. Missing native API: use the explicit permitted fallback. Denied permission: stop the
affected action. Missing independent actor: leave a usable review handoff outstanding.

## Cycle-position footer

Use the shared `lib/cycle-footer.sh` from the trusted source when available. Do not invent
state or claim completion from a position label.

```bash
footer_source="${LINTEL_SOURCE_ROOT:?approved installed Lintel source is required}"
: "${LINTEL_REPO_ROOT:?select the working repository before reading its state}"
if [ -f "$footer_source/lib/cycle-footer.sh" ]; then
  source "$footer_source/lib/cycle-footer.sh" || exit $?
  render_cycle_footer
else
  printf '%s\n' "UNVERIFIED: shared cycle-position footer is unavailable" >&2
fi
```

This reads existing state only. Do not create a cycle or profile merely to render
an orientation footer. A thin footer describes the recorded cycle, not proof that no
original mapped tasks remain; use the read-only `status` consumer for that distinction.
