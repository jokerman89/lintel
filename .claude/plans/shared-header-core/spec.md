# Spec: DR-36.header-core

**Status:** APPROVED within the bounded coordinator grant of 2026-09-30.
**Original recommendation:** DR-36 / LIB-04, shared header implementation.
**Base:** `a017e548cf7870b4043f5d896d8f5df296bbbae1`,
tree `914e5367e4daa879e28e2f21ad79a563756276a2`.
**Plan:** [plan.md](plan.md). **Work map:** [work.json](work.json).

## Architecture and contract

Extract only common fenced-header parsing and schema-driven validation from
`lib/review_method.py` and `lib/mars_contract.py` into the pure stdlib sibling
`lib/review_headers.py`. Both existing public functions remain family adapters.
Pass the original family `require` callback so error identity and diagnostics
remain owned by their original modules. Keep the original input normalization
and family opener construction order in those adapters.

The helper owns neither family schema nor value conversion, rendering, metadata,
policy, review acceptance or dispatch. Consumers load this exact trusted sibling,
not a module supplied by the target, working directory, home or module cache.
Keep `HEADER_KEY` exposed and preserve the original Python 3.9 interface floor.
The portable MARS resource declaration must include the new required helper.

## Acceptance from the released slice

| ID | Requirement | Original leaf | Observable outcome |
|---|---|---|---|
| R1 | One common parser/validator, unchanged public behavior | DR-36.header-core.1 | Identical signatures, successful values/order/returned identity, family exceptions/messages/first-error order, custom-schema behavior and rendered bytes. |
| R2 | Exact differential and consumer proof | DR-36.header-core.2 | Frozen original parser/validator/rendering oracles agree on valid and invalid fixtures; existing assertions remain unchanged; both real entry points and an installed closure work. |
| R3 | Attributable source, profile, verification and review | DR-36.header-core.3 | Only named files change; a distinct local P07 and exact hashes/commands/observations accompany an independent SPEC then QUALITY review. |
| R4 | Only this slice closes | DR-36.header-core.3 | Parent DR-36/LIB-04, distinct schemas, registry expiry and MARS governance remain outside scope; no timing, release or total-program claim. |

The differential matrix covers LF/CRLF, BOM and leading whitespace, blank lines,
colon-containing values, duplicate/malformed keys, missing/open/close fences,
required and unknown fields, family/version, enum and integer formats, competing
errors and custom schemas. Preserve existing quirks rather than hardening them.
REVIEW's empty-list conversion and MARS's double conversion remain distinct.
An expected-value, wire-byte, schema or authority change stops the affected work.

## Boundaries

Permitted source: `lib/review_headers.py`, `lib/review_method.py`,
`lib/mars_contract.py`, existing `tests/unit/review_method.py` and/or
`tests/unit/mars_contract.py`, only the needed MARS resource declaration in
`bin/li-copilot.py`, and one ownership note in
`skills/review/references/method.md` outside the rendered reviewer sections.
Only this initiative's minimal mapped artifacts and private runtime evidence are
additional writes.

No schemas, converters, renderers, defaults, consent, offer rules, metadata
versions, policy, QA, other helpers, shared plan, versions or changelog change.
No held work, old worktree/evidence mutations, new actor/model, dependency,
remote operation, whole local matrix or cleanup. The existing Deep reviewer
reports but does not repair. Master owns aggregate, hosted and delivery gates.
