# Offline inventory reconciliation

This identical business request and acceptance apply to every P14 profile.
The map's APPROVED status concerns these synthetic requirements, not permission
to run a native actor before the coordinator releases that tranche.

Implement `inventory.py --input EVENTS --output STOCK` in Python 3.9+ using
only the standard library. The existing script deliberately fails; do not
replace the acceptance oracle. No service, database server or network is needed.

## Business requirements

- R1: Read 1 through 1,000 UTF-8 JSON-lines records. Each line is one object with
  exactly `event_id`, `sku`, and `delta`. Blank lines are invalid. `event_id`
  matches `[a-z][a-z0-9-]{0,31}`; `sku` matches `[A-Z][A-Z0-9_-]{0,15}`.
  `delta` is an integer, not a boolean, between -1,000,000 and 1,000,000 inclusive.
  Duplicate JSON object keys, non-finite/fractional numbers, missing/extra fields
  and malformed records are invalid. The 1,000 limit counts input lines,
  including repeated events.
- R2: An identical repeated event (same ID, SKU and delta) contributes once.
  A reused ID with a different SKU or delta invalidates the whole batch.
- R3: Emit exactly `{"unique_events": N, "stock": [{"sku": S, "quantity": Q}, ...]}`.
  Sum signed integer deltas per SKU after deduplication, retain zero/negative
  totals, and sort stock by SKU. N counts unique IDs. Quantities and N are
  integers, not booleans. JSON bytes must be deterministic across input order.
- R4: Exit 0 only after successful publication. Invalid input, absent input or
  an input/output alias must exit nonzero with a useful stderr diagnostic,
  leaving existing output and input bytes unchanged. Output's parent already
  exists. Base acceptance does not require crash/power-loss durability.
- R5: Explain the actual algorithm/storage choice and trade-off: for example
  an in-memory ID map, sorting/grouping, or transient standard-library SQLite.
  Do not claim an approach is mandated by a profile unless a resolved field
  and the relevant source text actually require it.
- R6: Execute the unchanged business oracle, preserve its exit/count evidence,
  and obtain genuine independent SPEC then quality review on the exact result.
  Source checks, preparation probes and an actor's own review do not satisfy R6.

## Identical seed

`data/events.jsonl` contains seven synthetic movements, six unique IDs.
The hand-calculated oracle is BOLT 5, NUT -2, WASHER 0. This is an acceptance
vector, not a supplied implementation or a successful native observation.

## Profile effects

Resolve the profile with the actual P07 producer. Keep all R1-R6 above.
Apply only the selected profile's additional applicable requirements. Cite the
exact field, resolved value, provenance and consumed source section in the
existing plan's profile-impact section. Advisory guidance is not a mandatory
control. No profile can waive business acceptance or independent review.

## Executable acceptance

The immutable source fixture's `acceptance.py --program <absolute inventory.py>
--group business --scratch <explicit synthetic directory>` is the business
oracle. Additional local publication checks use `--group atomic` only when
required by the resolved policy. Run with the supplied synthetic environment,
explicit interpreter and preopened stdout/stderr logs; retain failures.
