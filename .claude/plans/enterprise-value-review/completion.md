# Complete the enterprise review and land it

Status: ACTIVE. Operator instruction on 2026-09-08: complete all remaining work and get it
to main. This authorizes integrating current main, fixing the review findings, verification,
feature pushes and merging PR #84. Preserve accepted architecture and production boundaries.

## Acceptance

- Reassess every F01–F22 finding against the combined tree; close it with code/tests or a
  precise correction of an unsupported claim. Do not count an unverified separate fix as done.
- Preserve the Copilot source/target and authoritative work-artifact contracts while retaining
  hybrid execution, requirement traceability and corrected pack semantics.
- Resolve conflicts and generated-file drift, including release version parity.
- Verify the integrated tree locally and through required CI; independently review substantive
  repairs. Record environmental skips and outstanding architectural choices honestly.
- Merge PR #84 to main and verify the remote merge commit. The other checkout stays untouched.

## Work packages

- [x] C1 — integrate current main; resolve conflicts by file ownership and reconcile contracts.
- [x] C2 — close remaining pack/routing/planning findings with regression evidence (after C1).
- [x] C3 — close Git collection and continuity/registry defects (after C1).
- [x] C4 — reconcile truth claims, report every finding, regenerate adapters/catalogues and
  release metadata (after C2/C3).
- [ ] C5 — independent review, integrated local checks, then CI (after C4).
- [ ] C6 — merge the verified PR and record the actual main commit (after C5).

The coordinator owns this ledger and release metadata. Implementers own only assigned
files; reviewers do not repair their own findings. Prefer existing mechanisms over new
schedulers, governance rules or a duplicate model-evaluation framework.

## Review

Implementation and generated integration are complete. Independent review closed five P2
source/target, ownership and registry issues, two P1 Git-collection bypasses and a final scanner
failure-propagation defect. Local strict verification passed 109/109 scripts with zero skips
or partial assertions; final scanner regressions and native PowerShell installation passed.
Hosted CI and merge remain pending; C5/C6 stay open until evidenced. See the completion audit.
