# Tests

Lintel is markdown and bash, so its tests answer two different questions: *is the structure still
what everything else assumes?* and *does the mechanism actually fire?*

```bash
bash tests/runner/run-all.sh                 # everything
bash tests/runner/run-all.sh --shape-only    # structural contracts only — fast
bash tests/runner/run-all.sh --scope unit    # one tier
bash tests/shape/no-swedish.sh               # one test directly
```

Every test is a standalone bash script that exits non-zero on failure. There is no framework and no
build step. `tests/conventions/bash-test-template.sh` is the starting point for a new one.

## The tiers

| Tier | Count | What it asserts |
|---|---|---|
| `shape/` | 36 | Structural contracts. Required frontmatter on every skill and agent, hook registration, canonical paths, decision-record number uniqueness, generated tables matching their source, no non-English text on the public surface. |
| `unit/` | 48 | Helper behaviour in isolation — state ledger segmenting, memory operations, pack resolution and inheritance, one-way-door detection, alias resolution. |
| `integration/` | 4 | Two or more components across a real boundary. |
| `behavior/` | 1 | A mechanism exercised hermetically, to prove it *fires* rather than merely exists. |
| `e2e/` | 1 | A full path through the harness. |

## Why the shape tier carries the most weight

The failure this project actually suffers is not a broken function — it is **drift between the
system and its own description**. A count in the README goes stale, a hook ships but is never
registered, a skill is renamed and six documents keep the old name, a generated table is hand-edited.
None of that breaks a unit test. All of it breaks trust.

So the shape tier asserts the things prose cannot be trusted to hold:

- `cli-tiers-sync.sh` — the README capability table must match `lib/cli-tiers.yaml` exactly. It is
  the anti-drift guard on the project's own honesty claim.
- `claude-home-paths.sh` — no tooling hardcodes a legacy knowledge path, and this repo carries its
  own layout marker. The factory has to pass its own inspection.
- `adr-numbers-unique.sh` — written after two parallel branches each claimed the same decision
  number and the merge kept both.
- `bin-scripts-executable.sh` — a non-executable commit passes on Windows, where the filesystem has
  no execute bit, and fails on Linux CI. Written after exactly that.
- `no-swedish.sh` — Lintel ships English-only. The one allowlisted file carries functional
  non-English text: regexes that detect Swedish personal data, which translating would break.
- `uniformity-coverage.sh` — a deliberately small enforced floor, with adoption above it reported
  rather than failed. Publishing the real number is the point.

Several of these exist because something went wrong first. The header comment on each names the
incident.

## CI

`.github/workflows/ci.yml` runs the suite on Ubuntu and Windows. Both must be green before a
release.

## Adding a test

1. Copy `tests/conventions/bash-test-template.sh`.
2. Put it in the tier that matches the question it answers — structural contract, helper behaviour,
   cross-component, does-it-fire, or full path.
3. Write a header comment saying *why* it exists. If it is guarding against a specific past failure,
   name that failure.
4. Make it exit non-zero on failure and print enough to diagnose without re-running by hand.
5. On Windows, commit it with the executable bit set (`git update-index --chmod=+x`) — Linux CI
   depends on it.
