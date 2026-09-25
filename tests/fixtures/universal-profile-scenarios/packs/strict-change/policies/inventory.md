# Strict-change requirements (synthetic policy 1.0.0)

## SC1: Publication boundary

Keep base R1-R6. Additionally prepare the complete output in a sibling temporary
file and publish with standard-library os.replace. A publication failure before
replacement must preserve prior output byte-for-byte and exit nonzero.
Document the validation/staging/publication boundary, compare two viable
algorithm/storage choices in T001, and explain the chosen failure behavior.
This is local process-failure safety, not power-loss durability or enterprise
certification. No database choice is mandated.

## SC2: Owned recovery readiness

Before native BUILD, use accepted P03 owned snapshot APIs on explicitly owned
inventory.py bytes and a non-overlapping recovery store. On an isolated rehearsal
copy, bind the exact attributable changed state, restore it, and demonstrate
that an unrelated late edit is refused and preserved. Never roll back arbitrary
target or source files. Retain actual commands, file hashes and refusal evidence.
This control adds recovery preparation, not a production rollback service.

## SC3: Accepted local equivalent and review

The compliance.hooks names above request outcomes; this pack installs no hook.
For this synthetic experiment, policy explicitly accepts the immutable local
atomic oracle (success and injected-before-replace failure) as the equivalent
for inventory-atomic-publication, and the real P03 rehearsal as the equivalent
for inventory-owned-recovery. Demonstrate both; a declaration alone is not
enforcement. Missing/error/zero-run evidence blocks the affected acceptance.

Bind business, publication and recovery obligations in the existing P05 v2
context before observations. Consume the selected quality guidance and retain
its P09 TQ result boundary without inventing another result schema. A genuinely
distinct reviewer must cover T001-T003, SC1-SC3 and the exact delivered bytes.
