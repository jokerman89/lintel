# ADR-0030: Owned installation without a Python prerequisite

**Status:** Accepted direction, 2026-09-20; implementation and review remain P10 gates.
**Authority:** A12 and the operator's explicit decision to keep installation without Python.

## Context

The native bare installers historically require Git and the host shell, not Python.
New profile and owned-snapshot helpers use Python. Reusing them for every installer
would add an installation prerequisite that the operator explicitly rejected.
Existing installers also need real ownership and interruption recovery, not an
unchecked tree copy or a success message after partial writes.

## Decision

Keep native Bash and PowerShell bare installation without Python. Share one documented,
versioned native receipt contract and the same behavioral fixtures across both hosts.
Use native SHA-256 and verified byte readback, preflight their availability, and never
install an interpreter or hashing dependency automatically.

Bind source, target, recovery store, old inventory, exact before/planned-after states
and per-file progress. Preflight all ownership and path boundaries. Publish file intent
before replacement and verified completion afterward; publish the inventory last.
Interruption stays incomplete. Recovery is explicit, refuses later user edits, preserves
unknown evidence and consumes write permission for restored paths. No whole-root deletion,
automatic rollback, lock stealing, multi-file atomicity or ACL/xattr guarantee.

Already Python-based repository/scaffold/migration operations may reuse the accepted
owned-snapshot APIs behind a small shared file-transaction primitive. Keep the existing
repository adapter's inventory, client/protocol-block and protected-file policies in
that adapter. The primitive does not decide that arbitrary current files are owned.
Do not make bare installation call the Python path.

This is an intentional native implementation split, not a new universal scheduler or
a duplicate repository adapter engine. Installation prerequisites and later operation
prerequisites remain separately documented and tested.

## Alternatives and trade-offs

1. One Python implementation everywhere: less duplicated host code, but violates the
   operator's selected installation boundary.
2. Preserve unchecked native copies and defer recovery: fewer changes, but fails A12
   ownership, interruption and preservation acceptance.
3. Selected: native performers share a contract and cross-host evidence; Python consumers
   share their existing mechanical helpers. More host-specific code is the explicit cost
   of retaining installation without Python.

## Verification and limits

Run actual no-Python native installs, repeat/update/conflict, interrupted publication,
explicit recovery, corrupt/foreign receipt and post-recovery replay cases in disposable
consumer roots. Preserve user config, profiles, packs, roles, hooks and unrelated files.
Test real supported host differences; do not claim unavailable PowerShell/Bash/OS/runtime
versions from syntax checks. P10 independently passes spec then quality; final combined
acceptance remains separate. No real global installation is authorized by this decision.
