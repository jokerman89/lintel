# P11 browser Q1 recheck

**2026-09-22: SPEC PASS; separately staged QUALITY FAIL.** Q1 is closed, but a
new directly coupled **P2 Q2** blocks A16 acceptance: the replacement numeric
matcher stalls on a whitespace-only field. Open findings: **P1 0 / P2 1 / P3 0**.
No product fix, native rerun, platform investigation or A14 review was performed.

## Immutable scope

Same independent reviewer: app `d823e773-d8dc-4d02-9716-77506a7a260e`, CLI
`1f655ca9-eb2b-4325-9996-72ed8539c13b`; not original builder `f413bdcb`.
Authority: `d3f94dbc7eb017e44cee72676cc5d036312c80e3`, Q1 subsection.

| Input | Verified identity |
|---|---|
| Repair product | `14b419c378b82807a9abbfeb386c20f145636f7f` |
| Product parent | `043019ace7916170de9376c8bd8726c1cd5d4744` |
| Report / this review's exact parent | `68a6084f1c5d2d8bece32b3786a0800aeca08a07` |
| Builder report Git-byte SHA-256 | `8d14d3483eae2f4222e999dd8ba606d59ee4b45cf7cd11bd6d2ad133daf28dfe` |
| Preserved original independent review | `5504a2c2089621113eb284f968b7f5bb409808cf` |

Pinned before execution; clean detached continuation preserves the old review
branch/ref. The 785-line report retains its exact 717-line prefix; all 68 added
lines were read. Repair changes only `skills\scrape\scripts\extract.mjs`,
`skills\scrape\SKILL.md` and `tests\integration\browser-operations.test.mjs`.
All other original browser/shared blobs remain identical. No moving builder tip
or later design change was imported. This commit adds only this review report.

## Sequential stage results

| Leaf | SPEC | QUALITY |
|---|---|---|
| A16.1 | PASS: shared operations/four entry points retained; exact Q1 values, supported forms, unsupported errors, trim/text/multi/diff and prototype-like keys independently rechecked. | FAIL: Q1 closed; Q2 below prevents final extraction acceptance. |
| A16.2 | PASS: original actual-provider/P03 admission evidence preserved on unchanged source. | PASS: unchanged ownership/guards; original five-hop/sixth-hop and raw-Location probes pass again. |
| A16.3 | PASS: original real headless read/action/keyboard/motion/screenshot/print and 47-artifact proof remain attributed to `3115790`. | PASS for unchanged reviewed portion; no new native execution or reassignment of old observations. |
| A16.4 | PASS: unchanged user-chosen authentication/no-transfer/engine-availability boundary. | PASS for original reviewed scope; headed login/persistence remain unobserved. |

Affected SPEC and the retained static pipeline passed before QUALITY started.
The prior comprehensive eleven-file review remains applicable outside these
three paths. This is not whole-P11/A14 completion or strict v2 release clearance.

## Findings

**Q1 closed** at `skills\scrape\scripts\extract.mjs:29-34`: independent actual
`extractPage` calls now return `$.50 -> 0.5`, `-.50 -> -0.5`, `-$9.50 -> -9.5`,
each with `ok:true, errors:[]`. Complete-form refusal replaces partial parsing.
Ordinary signed amounts, explicit locale/multiple-value errors and preserved
field/diff behavior pass.

| ID | Severity | File:line | Concrete finding and fix | Confidence |
|---|---|---|---|---|
| Q2 | P2 - must fix | `skills\scrape\scripts\extract.mjs:29` | Adjacent whitespace repetitions separated by optional tokens permit combinatorial backtracking. Consume permitted whitespace/tokens deterministically, without ambiguous overlapping repetitions; retain complete signed/decimal recognition and explicit unsupported-form errors. Add the bounded malformed-field regression. | 10/10 |

Reproduction uses the actual module and injected selector state:

```javascript
await extractPage(
  { read: async () => ({
    url: 'https://app.example.test/empty-amount',
    elements: [{ text: ' '.repeat(4096) }],
  }) },
  { fields: [{ name: 'amount', selector: '#amount', transform: 'number_extract' }] },
);
```

Exact original `043019a` module returned `amount:null`, one field error and
`ok:false` in **0.694 ms**. The repair did not return within **5000 ms** and its
owned worker thread was terminated. A prior 1024-space probe completed in
306.6 ms. These are actual observations, not an extrapolated completion time.
4096 characters fit the existing 65536-character read bound; five seconds is the
probe cutoff, not a newly imposed performance specification. Synchronous matching
blocks extraction instead of promptly reporting an empty/invalid field.

## Actual checks and provenance

All commands used inspected per-process synthetic HOME/USERPROFILE/AppData/temp/
XDG/LINTEL and derived paths, explicit PATHEXT and fixture Git configuration/
ceilings. Product/report seals were equal before/after every run, including
the original-module comparison. No source was edited while executing.

| Command under the sealed wrapper | Outcome |
|---|---|
| `node --test --test-reporter=tap <private>\numeric-spec.test.mjs` | Exit 0; 4/4 affected SPEC tests. |
| `bash --noprofile --norc tests\integration\design-browser-pipeline.sh --pdf-reader pypdf` | Exit 0; 4 shared + 29 Node, zero failures/skips; `browser:not_run`, own run `a16-jeh1g3sw`. |
| `node --test --test-reporter=tap <prior>\quality.test.mjs <private>\numeric-quality.test.mjs` | Exit 0; original seven probes plus two new probes, 9/9. Includes 40 unsupported-decoration contrasts. |
| `node --test --test-reporter=tap <private>\numeric-bound.test.mjs` | Exit 1; original-versus-repair comparison above, 1 failed regression, no skips. Only two owned worker threads terminated. |

Private evidence remains in this CLI session's `files\p11-recheck\`, including
pin, pre-QUALITY SPEC checkpoint, scripts, command/environment/seal records and
full logs. Reproducer SHA-256:
`7348e247d23d8d2e698742dd5e49904e428e151f2e0823ea69924829ad087339`;
failure log SHA-256:
`892ca0bee3017ea432690f31e817e183ad4c83bf0a6b17e7a0819021473e4daf`.

## Limits and next action

Original headless observations and the independently checked 47-artifact proof
remain at `3115790`, not the repaired source. New evidence is browser-free.
The original measured 3.498:1 P05 contrast negative remains blocked in its own
context; profile references remain distinct. No whole-P11 or release clearance.

Retain all prior limitations: only the screen PNG was directly visible; two-image
visual clearance, PDF raster/glyph bounds, physical print, headed/login/
persistence, other OS/clients and installed consumers remain unobserved.
Earlier native failures, unknown background/lock effects, pdftotext crash and
policy-denied raster route remain history; no diagnostic or denied route repeated.

**Next:** coordinator releases only the original owner's bounded Q2 matcher/test
correction and obtains a new immutable pair for this same reviewer. Do not reopen
browser readiness, locale infrastructure or A14. No original required headless
observation is missing; the blocker is this concrete extraction regression.
