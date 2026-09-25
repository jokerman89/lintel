# ADR-0028: Universal operations and attributable acceptance

**Status:** Accepted direction for the authorized 2026-09-20 Universal implementation.
**Implementation status:** see `.claude/plans/universal-implementation/work.json`;
this decision is not evidence that every adapter or consumer already implements it.
**Scope:** A02/A03/A05/A06/A09/A17/A22/A23.

## Context

The whole-system audit found host-specific assumptions in shared workflows, mixed
vendor/integration/live capability claims, and positive review records that can outlive
changed content or a later rejection. The operator selected a Universal core with real
adapters, preservation of existing value and independent review of substantive packages.
ADR-0026's short leaves and package execution remain authoritative.

## Decision

Retain canonical workflows and small mechanical helpers. Define semantic operations
once and bind them to actual host tools/permissions in an adapter. Distinguish CLI,
desktop, IDE and cloud even within one product family. Documented vendor capability,
shipped Lintel integration and observed version-specific execution are separate facts.
Neither a plugin manifest nor a worktree is proof of permission or a security boundary.

Questions use the host's actual question channel; ordinary conversation is the fallback
only when that host has no question tool. Missing safe concurrent isolation selects
serial work. Missing delegation selects durable external/manual handoff, preserving
planning, briefs, status and recovery. Missing independent review keeps that requirement
open; role-play or a model name cannot substitute for a separately attributable reviewer.

Shared core instructions express role requirements, not mandatory vendor tool/model IDs.
Preserve Claude-native optional memory and model configuration through its adapter where
supported, without making them a cross-host guarantee. This supersedes only ADR-0012's
assumption that a fixed model/memory mechanism defines the portable role. Its intent of
useful accumulated knowledge and proportional resource choice is retained.

Acceptance has two separate representations: policy control outcomes and content-bound
review evidence. Mandatory applicable failure, error or missing evidence blocks. Advisory
scores remain advisory. Not-applicable requires a grounded reason; unknown policy is not
an automatic exemption. A zero-test run or unavailable browser is not verified success.

A review identifies the chosen work map, package and unchanged leaf IDs, acceptance
source, attempt, builder/reviewer context and exact attributable result. A snapshot binds
base/revision, selected tracked/staged/unstaged/new files, deletions and relevant file
types/content. Selection is explicit and its manifest part of the identity. Only the
review record's own storage is excluded to avoid a self-hash; do not blanket-exclude all
plans, configuration or `.claude/` content from evidence.

Choose the latest applicable review decision before evaluating its exact status.
A later rejection/error revokes earlier clearance; malformed, unbound or stale evidence
cannot silently restore it. Unchanged relevant inputs can reuse evidence; age alone
cannot prove validity. SHIP verifies the same snapshot and acceptance that were reviewed.
Any mechanically unobservable independence claim remains a declared claim requiring host
or human corroboration, not cryptographic proof from two different strings.

One shared result/evidence implementation serves producer and consumer. Swarming consumes
it rather than introducing another completion truth. Historic review records remain
readable as history; strict clearance requires sufficient evidence. Verification-only
packages explicitly support no product change, not fabricated filenames.

## Alternatives

1. Documentation-only cleanup leaves the observed false-clearance and profile/work
   boundaries unreliable.
2. A new universal scheduler/runtime would impose a large migration before proving value.
3. **Selected:** preserve existing helpers, maps and adapters; repair shared contracts
   with discriminating integration tests and honest host fallbacks.

## Consequences and verification

Update old tests when they assert superseded success semantics; preserve meaningful
negative/regression coverage and name the intentional behavior shift. Test latest-pass/
later-fail, changed dirty/new/config/task content, absent mandatory evidence, manual review
handoff, and package-to-leaf coverage. Real client/model runs remain a distinct evidence
category. No dormant hook, private synchronization or external control is activated here.
