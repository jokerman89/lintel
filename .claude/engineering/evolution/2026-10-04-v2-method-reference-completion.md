---
slug: v2-method-reference-completion
date: 2026-10-04
cycle_id: null
work_map: .claude/plans/v2-findings/work.json
packages: [P10, P9]
operator: delegated-master-coordinator
affected_paths:
  - scaffolding/01-foundation/templates/plan/spec.template.md
  - skills/plan/SKILL.md
  - skills/resume/SKILL.md
  - skills/resume/references/state-and-job-recovery.md
  - skills/swarm/SKILL.md
  - skills/swarm/references/evidence.md
  - lib/capability-selections.json
  - bin/li-copilot.py
risk_class: medium
breaking_change: false
---

# Structure change: V2 method reference completion

This M1 record covers the original A-07, B-09 and B-11 continuation, not a new
governance decision or a claim that the entire V2 programme is complete.
It is a standalone continuation of the original mapped work; no job/cycle
identifier is invented.

## What changed

The native spec has a separate conditional material-premise table using DEFINE's
existing vocabulary. It is not another requirement table or a new runtime schema.
The original six requirement columns, DRAFT-first lifecycle and approval owner
remain.

Resume retains its primary decision/input/acceptance flow and public headings.
The complete swarm, ledger and job/tree procedures have one named reference,
with declared producing steps and same-shell inputs. Swarm's complete shared
consumer moves alongside the existing provider-name table. Main methods require
the relevant reference read before using those conditional procedures.

Core capability and native dependency inventories include the recovery reference.
Native skills remain complete translations of the canonical bodies, with real
installed resources, not pointer-only adapters or a hard size-limit workaround.

## Backward compatibility

Public skill names, flags, heading anchors, task/requirement IDs and helper APIs
are retained. Recovery recipes are preserved in full. The Swarm consumer differs
only in its reference context and explicit names for existing profile arguments.
Required work/profile/QA/review/corroboration rules are not relaxed.

Source-contract tests follow each actual owner. Negative guards scan both files,
and the snippet extractor refuses a later section's code rather than silently
executing it. That test-helper correction preserves all existing positive chains.

## Migration path

There is no stored-data or public-interface migration. Update managed native
resources through the existing adapter. A version change to 0.13.9 requires the
existing explicitly reasoned target-local profile rebind before fresh source
acceptance; prior generations and review records remain history.
Do not remove the reference independently of its callers and resource inventory.

## Forward compatibility

Future edits have one procedure owner and a documented input boundary. Reference
availability is verified in installed consumers. Further procedure changes still
need actual affected tests and independent review; reference structure does not
prove a model read it or that a host enforces permissions.

## Verification

Existing planning/coordination/continuity/core tests cover the new template shape,
reasoned N/A, owner-aware guards, real joined setup/integrity behavior and blocked
job/flat fallback. Preimage evidence checks the complete moved procedures.
Installed-kit tests cover rebased links and missing-source refusal without target
mutation. The existing Swarm shape test includes the new owner.

Current native/catalog/wiki checks, both installation consumers, full shape and
exact-head CI, M2 and independent source review remain required. A planned test
is not a passing observation. Documentary fixtures are not model-efficacy proof.

## Rollback procedure

Use verified baseline `19fd4dccc44c1d7de37f5e89afca7e3c69361435` for comparison.
If correction or reversal is needed, prepare a scoped ordinary change restoring
callers, reference ownership, inventories and tests together; regenerate native
artifacts and obtain fresh applicable evidence before publication. Do not reset
a working tree, discard unrelated work, delete preserved evidence, or reuse stale
review/profile acceptance after reverting.
