# A08.1 - Requested operation before subject

Implementer: MasterSession. Base: `3f584c8`.
Scope: `lib/orientator-routing.sh`, `tests/unit/intent-operation-boundary.sh` and
the directly related mechanical-routing section of `docs/concepts/orientator.md`.
Independent package review remains pending under P08; no A08 completion claimed.

## Reproduction and result

The audited requests reproduced on the baseline: review-the-fix became fix,
research-deployment became deploy, and review-release-plan became ship. The new
test initially ran 25 assertions with 15 failures, without executing any recommended
workflow or modifying a fixture repository.

The correction identifies an explicit requested operation before matching symptom-only
topics, skips negated operations and preserves direct fix/build/deploy/ship/scaffold/
resume routes. It remains a deterministic recommendation, never action authorization.
Follow-up fixtures cover question forms, symptom-only build descriptions and whitespace.

Verification commands:

- `bash tests/unit/intent-operation-boundary.sh`
- `bash tests/unit/orientator-mechanical-routing.sh`

Initial execution: **30 assertions, zero failures**, and all existing mechanical-routing
scenarios passed. `git diff --check` passed. Natural-language routing remains heuristic;
compound/ambiguous requests still
require the host's intent/scope judgment rather than permission inferred from keywords.

Coordinator follow-up found the new word splitter inherited a caller's nonstandard IFS.
Three added cases reproduced review-to-fix and research/build-to-unclear misrouting with
`IFS=:`. The reader now sets its separator only for the read operation, preserving the
caller's environment. The extended **33 assertions passed with zero failures**, alongside all existing
mechanical-routing scenarios. Independent P08 package acceptance remains pending.
