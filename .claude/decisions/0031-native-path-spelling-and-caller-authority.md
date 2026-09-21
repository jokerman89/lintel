# ADR-0031: Native path spelling without changing caller authority

**Status:** Accepted implementation direction, 2026-09-21; repair acceptance is pending.
**Scope:** Existing A01/A11/A23 Windows integration requirements, not new host permissions.

## Context

The immutable investigation `990b0daa` separates three observed boundaries: ordinary
Python checkpoint/snapshot I/O fails at long Windows paths; Git's own bisect ref
handling has a separate process option; external fixture cleanup can fail even when
the accepted P07 producer/verifier succeeds. Same-location diagnostics succeeded
without shortening names or changing global settings, but are not shipped fixes.

## Decision

Preserve the actual default roots, names, hashes and owned recovery behavior. Extract
the accepted P07 representation logic into a small stdlib `lib/native_paths.py` with
two exports: `path_identity(PurePath) -> tuple[str, ...]` and
`native_io_path(Path) -> Path`. Representation errors are `ValueError`.

The module only recognizes filesystem spellings. It performs no I/O, root selection,
resolution, state mutation or authorization. Preserve component case and reject
unsupported device namespaces, ADS, unresolved traversal and ambiguous components.
POSIX remains a passthrough for I/O spelling. A native spelling never authorizes a path.

P03 retains its stricter symlink/reparse, relative-path, regular-file, byte-bound and
owned-root rules. P07 retains its existing runtime containment and permitted in-root
link policy, with compatibility wrappers translating errors to `PROFILE_IO`.
Separate logical paths from I/O operands. Newly introduced native aliases must not
change persisted roots, provenance, profile references/digests, snapshot owners,
formats, history names or default-store hashes.

Cover reads, metadata/ancestry checks, creation, iteration, temporary files, both
publication operands, locks and owned recovery—not only the failed write. Missing
trusted helper code must fail before mutation rather than import a target substitute.
No third-party runtime dependency or Python requirement for native installation.

Git handling is a separate bounded Windows subcase: a per-invocation
`-c core.longpaths=true` may be used only in the attributable owned bisect trial/admin
flow, including error cleanup. Never write global/local persistent Git configuration
or change unrelated caller operations. Preserve caller HEAD/index/config and all
staged/unstaged/untracked content. Fixture cleanup is another separate, fixture-owned
subcase, limited to the exact proven temporary root.

## Alternatives and trade-offs

1. **Selected:** checked same-location Python I/O, separate Git process handling and
   faithful fixture cleanup. More integration work, but preserves requested defaults.
2. Conservative path rejection plus operator-selected shorter roots. Useful as a
   diagnostic/failure boundary, but does not satisfy the required default scenarios.
3. Require host/runtime configuration changes. Adds environmental prerequisites and
   needs separate authority; it cannot justify changing OS/global Git settings here.

## Sequencing and verification

One P03 writer implements the core/extraction and narrowly assigned fixture plumbing.
P10's original owner integrates the independently reviewed dependency afterward and
owns any separately released direct installer/runtime I/O changes. Do not edit its
rejected/frozen candidate concurrently. P08 routing and gated A13 remain separate.

Use unchanged-length real consumers, old-record byte compatibility, containment/
namespace/case/link negatives, late-user-edit and interruption/replay controls.
Synthetic environment preflight is mandatory. Existing failed evidence stays failed;
source/runtime/platform and injected evidence remain distinct. Independent spec then
quality and final joined checks precede acceptance. No global policy/configuration,
real-home inspection/rollback, silent relocation or broad deletion is authorized.
