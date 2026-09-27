# Cold-executor prompt — supported clients: Copilot, Claude, Codex and Cursor

This prompt, [spec.md](spec.md) and [plan.md](plan.md) are enough to resume or extend the
work without the originating conversation.

## Context

Lintel's Universal initiative registered 38 client surfaces across 14 families. The
operator decided on 2026-09-25 that Copilot, Claude, Codex and Cursor are enough for now,
to reduce friction and CI time. Support is registry-driven (`lib/cli-tiers.yaml`), so the
cleanup removes records, the Gemini/OpenCode entry routes, two update routes, metadata
hints, tests that named removed clients and the matching documentation. The `other`
manual route and the Universal operation contract stay.

## Constraints

- Must respect: L-045 and L-053 (no push, PR or CI dispatch without an explicit request;
  only `jokerman89` publishes), L-049 and L-051 (run every test through a synthetic
  HOME/USERPROFILE/APPDATA/LOCALAPPDATA/TEMP/TMP/TMPDIR/XDG; never delete a synthetic
  temp that backs the MSYS `/tmp` mount), L-054 (no new packages), L-055 (no history
  rewrites; add commits).
- Must NOT: edit historical records (older ADRs, `.claude/engineering/**`, earlier
  plans/reports, the dated presentation deck), change the registry schema, installer
  semantics or CI matrix, or remove `other`.
- Compliance: neutral `_default` pack; none. Voice tier: internal.
- Parallel work: PR #104 (legacy cleanup) and the documentation-modernization sessions
  edit some of the same files. Merge `main` into this branch rather than rebasing when
  they land; keep removed files deleted when a modify/delete conflict appears.

## Acceptance criteria (verify)

- [ ] `python3 bin/li-client-capabilities.py list` prints the 13 kept surfaces and `other`.
- [ ] No live path names a removed client (scan excludes history and the presentation deck).
- [ ] Targeted tests, `li-catalog --check`, `li-instructions check`, `li-copilot check`,
      `li-wiki-gen --check`, the shape tier and `install/verify.sh --all` pass.
- [ ] The compatibility audit and an independent review have no unresolved blocker.

## How to re-execute

1. Read spec.md and plan.md; check which leaves [review.md](review.md) marks verified.
2. Continue from the first unverified leaf on branch `jokerman-microsoft-trim-supported-clients`.
3. Re-run the targeted verification list in review.md under an isolated launcher.
4. Obtain an independent review before any delivery request.

## What you don't need

The originating conversation, earlier Universal package history, or live client sessions:
no model or client acceptance is claimed by this change.
