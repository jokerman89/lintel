# C-01.blob-reads: Selected Git blob prefetch

**Status:** APPROVED within the bounded implementation grant of 2026-09-29.
**Base:** `0baa9a0c6e518dc619668aef03e2889ca599dab8`,
tree `c6026fd282c349d195873e6a77f4dc3d9725a604`.
**Authority:** original Deep C-01, blob-read subprocess overhead only.
**Plan:** [plan.md](plan.md).

## Contract

The existing P05 snapshot is authoritative. Preserve its complete JSON, serialized
order, digests, modes, selected paths, exclusions, working bytes and first
`ContractError` type/message/order. Never update an expected value to accommodate
this optimization. A semantic difference stops the affected work.

Add a private `_blob_digests(repo, oids)` cache prefetch. For nonempty selected
blob OIDs, use one `git --no-pager -C <repo> cat-file --batch` process with the
same environment as `_git`, including `GIT_OPTIONAL_LOCKS=0`. Empty input starts
no process. Deduplicate full hexadecimal OIDs; paths never enter this protocol.

For each OID, write it plus LF, flush, then read one complete response before
writing another. Require the same OID, `blob` type, decimal byte length, exactly
that many bytes streamed into SHA-256, and a trailing LF. No `--buffer`.
Retain only completely framed digests. On malformed/missing/nonblob/mismatched
responses, EOF, short body, bad trailer or `OSError`, stop prefetch and retain
its completed prefix. Close stdin and terminate/wait only the owned process.
Catch no broad exception and do not suppress interrupts.

Use a shared `_BLOB_MODES = ("100644", "100755", "120000")` for prefetch and
the unchanged strict `git_state` mode check. Collect OIDs only from the already
selection-filtered base/head/index tables, after the existing walk and selection
checks. Keep `git_state`'s per-object fallback and the entries loop unchanged:
uncached objects are read, validated or rejected at their original point.

## Acceptance

| ID | Required observation |
|---|---|
| R1 | Full snapshots and canonical JSON equal the original path with prefetch patched to `{}`. |
| R2 | The first exception type and message equal that same original path for every invalid fixture. |
| R3 | Staged/unstaged/untracked/deleted, `rm --cached`, base/head changes, executable and symlink Git modes, duplicate OIDs, Unicode/index-only names and newline-name error precedence retain behavior. |
| R4 | Empty, CRLF, binary/NUL, no-final-LF, 1 MiB + 1 byte and fake-header-containing blobs retain exact hashes. |
| R5 | Missing/nonblob objects, gitlinks, unmerged stages, process-start failure and truncated/malformed protocol responses preserve strict fallback and complete-prefix semantics. |
| R6 | At least twelve distinct selected blobs require exactly seven Git processes and zero individual blob calls on the normal path, versus six plus U on the original path; zero selected OIDs means zero batch processes. |
| R7 | Applicable existing review, MARS, adaptive and mandatory-control regressions retain their expected values. Independent implementation review is separate from the author. |

## Boundaries

Only `lib/review_contract.py`, `tests/unit/review_evidence.py` and this minimal
mapped initiative may change. Python 3.9 standard library and existing Git only.
The original Adaptive worktree, runtime, archives, other owners and global
settings remain untouched. No version, changelog, shared plan, schema, policy,
ignored-file, MARS or hook changes. No new actor or subagent.

C-01's MARS re-snapshot frequency, C-02's ignored-file semantics and filesystem
path cost remain OPEN and out of scope. Process counts are structural evidence,
not measured end-to-end speedup. Any optional timing is a small owned synthetic
fixture observation only after equality is established.
