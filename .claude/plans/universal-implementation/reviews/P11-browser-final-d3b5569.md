# P11 browser Q2 final review

**2026-09-22: complete scoped A16 SPEC PASS, then independent QUALITY PASS.**
Q1 and Q2 are closed. Open findings: **P1 0 / P2 0 / P3 0**.
The browser-only A16.1-A16.4 component is accepted for coordinator integration;
this is not A14, whole-P11, integrated release or strict v2 SHIP clearance.

## Exact source and reviewer

Same independent reviewer: app `d823e773-d8dc-4d02-9716-77506a7a260e`, CLI
`1f655ca9-eb2b-4325-9996-72ed8539c13b`, distinct from original builder `f413bdcb`.
Prior reports `5504a2c` and `4cf84d0` and their refs remain preserved.
No product edit, additional reviewer or builder was created.

| Input | Verified identity |
|---|---|
| Q2 product | `d3b5569c92ce2b0b6f3d2eaf189070f226460513` |
| Product parent | `7aea8480dbad1a0b977dc10422b8ebc64ba27b44` |
| Builder report / this review's exact parent | `336513e0178a1e9df39286ac7a69de5989f7a5ef` |
| Builder report Git-byte SHA-256 | `cabe3a0e6319178ad7b01fd20301248f106faa1a31ab5e86d3e33976e3daaf10` |
| Q2 authority | `b8f0cf7b3e827a90f5afc0c2eacc3a809adbd804` |

Pinned before execution. The 852-line report retains the exact 785-line prefix;
all 67 added lines were read. Parent `7aea848` is the authorized P09 merge of
`68a6084f1c5d2d8bece32b3786a0800aeca08a07` and
`ea92df855bc1e0dfea5c9deb913bdcdf2e5faa8c`; every browser/report blob and selected
shared dependency is unchanged across that merge.

The repair changes only `skills\scrape\scripts\extract.mjs`,
`skills\scrape\SKILL.md`, and `tests\integration\browser-operations.test.mjs`.
Reviewed the full correction against the earlier complete eleven-file review,
not the builder's moving tip. No separate A14 WIP was read/imported. This commit
adds only this report on a clean detached continuation.

## Per-leaf staged verdict

Affected SPEC and retained static checks passed before QUALITY began.

| Leaf | SPEC | QUALITY / preserved evidence |
|---|---|---|
| A16.1 | PASS | PASS: four entry points/shared operations and rich scrape methods retained; corrected signed/decimal values, whole-form refusal, trim/text/multi/diff/prototype-like keys and deterministic full-bound parsing independently verified. |
| A16.2 | PASS | PASS: unchanged actual provider/ownership/P03 URL and redirect boundaries; original five-hop/sixth-hop and raw/duplicate/missing/foreign Location probes pass again. |
| A16.3 | PASS | PASS: original real headless read/action/keyboard/motion/screenshot/print evidence and independently checked 47-artifact proof remain attributed to `3115790`; no new browser execution is claimed. |
| A16.4 | PASS | PASS: unchanged user-chosen authentication/no-transfer and profile-versus-engine boundary; actual original password-fill/HTTP-auth refusals retained, not a claim of real login/persistence. |

**Q1 closed:** `extract.mjs:26-79` still returns `$.50 -> 0.5`,
`-.50 -> -0.5`, `-$9.50 -> -9.5`, with successful records and no errors.
Unsupported grouping, multiple numbers, repeated signs, malformed decimals and
decoration produce explicit field errors rather than partial numeric values.

**Q2 closed:** the same code now consumes tokens with a forward-only cursor.
Each loop advances it; regex tests inspect only one character/code point.
There is no field-wide overlapping whitespace regex or rewind. The exact
4096-space counterexample returns null/one field error instead of stalling.
In the independent original-versus-current probe, the original returned in
0.518 ms and this repair in 2.891 ms, both below the retained 5000-ms test cutoff.
The separate bound suite observed 65536 spaces rejected in 2.258 ms.
These are local measurements, not a cross-platform guarantee or a new SLA.

## Actual reviewer verification

| Sealed command | Outcome |
|---|---|
| `node --test --test-reporter=tap <prior>\numeric-spec.test.mjs <private>\q2-boundary.test.mjs` | Exit 0; 5/5 tests. Includes 42 actual valid/invalid cases of exactly 1024, 4096 and 65536 characters; Q1/error/text/multi/diff/key preservation passes. |
| `bash --noprofile --norc tests\integration\design-browser-pipeline.sh --pdf-reader pypdf` | Exit 0; 4 shared + 30 Node, zero failures/skips; explicitly `browser:not_run`, own run `a16-vm9onmuo`. |
| `node --test --test-reporter=tap <original>\quality.test.mjs <prior>\numeric-quality.test.mjs <private>\q2-quality.test.mjs` | Exit 0; 10/10 tests, zero skips: original seven probes, 40 decoration contrasts, 1024-space rejection and exact Q2 original/current comparison. |

All product calls/imports and outer comparisons used inspected per-process
allowlisted synthetic HOME/USERPROFILE/AppData/LocalAppData/temp/XDG/LINTEL and
derived paths, explicit PATHEXT and fixture Git configuration/ceilings. Source/
report seals remained equal before/after each command. True exits and logs are
retained. Malformed-input probes used only owned worker threads with bounded
cleanup. No personal startup, dependency install, source mutation, browser,
server, native-location query, policy change or platform exploration occurred.

Private pin, stage checkpoint, command/environment/seal records and probes remain
in this CLI session's `files\p11-q2-review\`. QUALITY log SHA-256:
`68ac4c38c34d522cc23e78b78be1bc5ae87d82217d317d720679a3bc4ed8439e`.
Detailed inventories stay private. The unchanged neutral policy/control
boundaries remain: this run has its own profile context; earlier references and
mandatory negative results were not rebound or relabelled.

## Retained observation limits and next action

Original live evidence is still `311579071100bfaaa0f1762d4672939c643d7129`,
run `a16-awm92xgk`: 4 shared + 23 Node + 8 actual headless scenarios, count 2,
price 101.5, real PNG pixels, two printed PDF pages/text/origins and owned cleanup.
The prior independent 47-artifact hash proof is reused, not presented as new
execution on the repaired extraction source.

Only the screen PNG was directly visible; direct two-image visual clearance,
PDF raster/full glyph bounds, physical print, headed/login/persistence, other
OS/clients, minimum runtimes and installed consumers remain unobserved. Earlier
native failures, unknown background/locking effects, pdftotext crash and denied
raster route remain history. The measured 3.498:1 P05 contrast negative stays
blocked in its own context. No denied route or consumed diagnostic was repeated.

**Next:** coordinator may integrate this exact accepted A16 component and review
evidence. Separate design/artifact work requires its own authorized source,
observations and review; neither A14 nor all P11 is closed here.
