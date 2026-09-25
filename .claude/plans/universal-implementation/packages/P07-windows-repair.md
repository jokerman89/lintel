# P07 Windows containment repair checkpoint

**Status:** APPROVED bounded re-plan, 2026-09-20.
**Task authority:** existing A07.3/A07.4; no new initiative or relaxed acceptance.
**Why re-plan:** three specification iterations exposed a legitimate native Windows
path-spelling race after the earlier policy-continuity findings were repaired.
Product `56981ed` remains unaccepted; reviewer report and exact native schedule are inputs.

## Boundary and decision

Keep P07's implementation owner and reviewer, no new worker. Only
`lib/profile_context.py`, owned profile tests, directly related profile docs and P07's
own report may change. No consumer, shared schema, global configuration or network access.

Resolve actual filesystem ancestors before checking containment. Compare against frozen
approved repo/home roots and the repo's lexical runtime boundary; never promote a
redirected runtime directory into a new authorization root.

Use one comparison-only identity operation for recognized ordinary/extended absolute
Windows drive and UNC filesystem spellings. Compare complete components, not string
prefixes. Reject unsupported device namespaces, unresolved traversal, ambiguous drive/
root-relative forms and alternate data streams. Do not rewrite actual I/O locations,
manifest provenance or digests merely to make comparisons pass. Do not collapse
distinct actual filesystem identities under a global case assumption.

POSIX behavior stays unchanged. An alias the helper cannot safely establish fails
explicitly; no default success, bypass flag, broad catch or retry hiding the defect.

Rejected alternatives: stripping arbitrary prefixes before resolution weakens the
boundary; a new Win32 handle-only runtime expands scope and cannot address every
not-yet-created leaf. If evidence shows a broader identity/digest contract change is
necessary, stop that part and return the concrete finding before implementing it.

## Short repair leaves

Checkboxes live only in plan.md. These are refinements of the existing A07 acceptance,
not an alternative backlog.

| Leaf | Dependency | Acceptance and verification |
|---|---|---|
| A07.3.w1 | Exact F04 report | Reproduce the native concurrent bootstrap failure and preserve trace without changing the tested code |
| A07.3.w2 | A07.3.w1 | Ordinary and recognized extended path spellings compare as the same approved filesystem location |
| A07.3.w3 | A07.3.w2 | Native drive/extended bootstrap and repeated concurrent triples succeed with unchanged reference/provenance semantics |
| A07.4.w1 | A07.3.w2 | Different roots/shares, sibling prefixes, device/ADS/traversal and real junction/symlink escapes remain rejected without writes |
| A07.4.w2 | A07.3.w3,A07.4.w1 | Original 43 lifecycle protections and nine preserved scripts pass on a frozen committed product |
| A07.4.w3 | A07.4.w2 | Same independent reviewer accepts the narrow repair, then performs the still-unrun whole-component quality stage |

Extend `tests/integration/universal-profile-context.sh` and its owned Python tests.
Run the exact native F04 schedule plus deterministic injected normal/extended drive
and UNC comparisons. UNC comparisons are not a live-share claim: no network share
setup or personal configuration is authorized. Label native, injected and grammar-only
evidence separately. Include source/target and no-write negative controls, not only a
positive spelling comparison.

Report exact new product/report commits, F01-F03 retained closures, F04 result and
remaining P05/P06/P08/P14 gates. No final P07 acceptance follows from implementer tests.

## Joined installed-source long-path repair

**Status:** APPROVED bounded integration repair, 2026-09-20. The earlier w1-w3
checkpoint is independently accepted at `a8de574` / report `3d8e715`. This new failure
does not rewrite that evidence, but reopens A07.3/A07.4 joined behavior.

Actual installed-source bootstrap with the default repository-local LINTEL_HOME fails
on native Windows even with a short `profile-consumer` fixture name. A direct call to
the installed `bootstrap_profile_context` reproduces the same error, excluding a
Bash argument-conversion explanation. `_retain_record -> _write_json -> os.replace`
fails with WinError 3: the temporary path is 220 characters and the history destination
is 274. A longer original fixture failed with a filename-too-long error. Shortening
the test again, overriding the documented default home, or treating this as a skip
would hide the observed consumer failure.

Same P07 owner, same independent reviewer; retain the ownership list above. Support
the actual default pinned-profile flow at long native Windows paths while retaining
ordinary stored roots/provenance/reference semantics. A recognized extended-length
filesystem spelling may be used for I/O to that SAME verified location; it must not
authorize another root, strip arbitrary device prefixes, follow redirected ancestry
or case-fold distinct directories. Validate the actual target before mutation. Do not
change system LongPathsEnabled, shorten or relocate the durable store, silently change
history naming, rebind policy, or alter source/target identity.

Alternatives: an explicit short home can work around the error but does not repair the
documented default; shortening history names changes a durable format unnecessarily.
Prefer a narrow Windows I/O adaptation that preserves the existing identity contract.
If that cannot be established safely, stop with evidence rather than relaxing guards.

Refinements in plan.md: A07.3.l1 preserves exact installed-source/default-home RED;
l2 repairs same-location long-path I/O without data/identity migration; l3 verifies
fresh-shell pin reuse, retained history, explicit rebind and same-mtime drift at paths
over 260 characters. A07.4.l1 retains native/injected outside-root, case-sensitive,
junction, namespace/ADS/traversal and lock/interruption refusals; l2 obtains independent
repair spec/quality before joined acceptance. Include paths whose parent/temp/lock also
exceed the legacy limit, not only the final filename. No live UNC share claim.

The coordinator owns the new installed-consumer regression in
`tests/integration/copilot-kit.py`. P07 adds focused cases to its own profile tests and
returns an immutable repair; the coordinator reruns the actual bundled consumer after
independent review. P05/P08/P10 and final A22.7/A24 remain separate.
