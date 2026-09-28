# ADR-0040: Adaptive depth within the shared Review Method

**Status:** Accepted within the operator-authorized adaptive-review initiative, 2026-09-28.
**Scope:** [Adaptive review spec](../plans/adaptive-review/spec.md).

## Context

The operator requested tougher security/correctness questions and production
review, while keeping small changes cheap and integrating ongoing patterns and
native-client work with minimal conflicts. One shared Review Method, content-bound
release evidence and opt-in MARS already exist. A new scanning engine would
duplicate those contracts and make the requested low overhead harder to achieve.

## Decision

Extend the existing packet with evidenced lean/standard/deep depth, triggered
security questions and an explicit mandatory-question inventory. Preserve
optional exploration and grounded N/A, but do not pass explicitly selected
mandatory unverified questions. Catalog defaults are advisory, and depth never
promotes them. The same version-2 method metadata, packet and assessment feed
single review and MARS; the original body verifies its obligation inventory.

Reuse the optional patterns provider for exact lock verification, task projection
and coverage. Load only selected context; no second resolver, policy parser or
automatic reading of internal sources. Missing required inputs stay unavailable.

Add offline evaluation of supplied observations. It neither performs attacks nor
runs a model, and it cannot claim benchmark placement or production clearance.
Calibration remains opt-in recommendations reviewed by a human; rare severe
checks are not automatically retired by a low observed yield.

## Alternatives

1. Documentation-only questions: smallest change, but cannot discriminate missing
   mandatory coverage or prove single/panel parity.
2. Always-on multi-agent scanner: broader autonomous execution and costly
   orchestration; conflicts with Lintel's host-owned and lightweight architecture.
3. Selected: additive method/context helpers and bounded references using existing
   policy, pattern, review and consent boundaries.

## Compatibility and verification

Do not change P05/P07 schemas, MARS defaults or consent. All question catalogs
default their new requirement field to advisory; explicit current requirements
remain separate and mandatory. Method metadata version 2 requires the selected
inventory, verified against the original body; v1 remains readable as legacy data.
Test downgrade refusal, unknown facts, mandatory/optional coverage, actual packet
parity, provider-unavailable and a frozen-provider join. Imported fixture metrics
prove scorer behavior only, never model superiority.

Native-client-parity owns adapter generation and its version increment. Reusable
patterns is a separate, unmerged dependency. This decision grants neither stack
acceptance nor authority to reopen held unrelated review remediation.

## Proportionate cost

One additional universal question, SQ-U11, compares an existing sibling's
invariant. Its small per-implementation cost is intentional within this design:
reuse and inconsistent implementations are central to the requested improvement.
The other thirteen additions are selected by surface or depth. All remain
advisory unless accepted obligations explicitly require them; no extra model
call, whole-repository scan or mandatory panel follows from the added question.

Legacy method metadata stays readable with an explicit limitation. It cannot
stand in for current v2 obligation coverage. A v2 MARS brief cannot be relabeled
with legacy metadata; only owned-session cleanup can proceed without the lost
brief, and that operation grants no review or release clearance.
