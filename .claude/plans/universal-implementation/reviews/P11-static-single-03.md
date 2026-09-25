# P11 single-03 static artifact review

**Disposition: seven data-backed static SPEC controls pass; the required independent
direct-image observation is unverified. Complete static SPEC acceptance is blocked.
Whole static QUALITY is not eligible and was not run.** This freezes the commissioned
review checkpoint, not A14.5, P11 or parent-initiative acceptance.

## Exact target and independence

| Identity | Frozen value |
|---|---|
| Accepted product | `a1b3a45e532ef756f8837cc182064a5f88b375a6` |
| Product tree | `2ab9e1bea3cd475d658080ea877bf3a7d4ea22ba` |
| Owner execution checkout | `683db6ab45416d321b5bc2e4183024bab6aa47c8` |
| Reviewed report / this report's parent | `d7139b5e99d189e71fb14d90fd8b80c8272efbcc` |
| Owner report Git SHA-256 | `a7c402910c57abfe6dd1825f7869dabcf8af4a45a39088d9b2b0b26ed7e067a9` |
| Artifact authority | `b1ca886c37f469d705603638632eda6bb7f25831` |
| Prior source acceptance, unchanged | `edecfdf9582f2dc442bee22bee2fc2107a1b5ab0` |
| Artifact SHA-256 | `9d76ab47dfa9148b1614a79aa1730e9984af79510e8a1adffce3368eda6abd49` |
| Evidence checkpoint SHA-256 | `4062fc547a9fd811c89b3bc5f841c43a94febb7be3e1f5583ebfadb7ab9aed0a` |
| Observations SHA-256 | `df30b77a26065c715666ac01b0217bda210f06486382c167f5c71c21ad6cdb1b` |

SAME distinct reviewer `1f655ca9-eb2b-4325-9996-72ed8539c13b`, project session
`d823e773-d8dc-4d02-9716-77506a7a260e`; original builder `f413bdcb` did not perform
this review. Results go only to recovery coordinator `88aecc43-40f9-41d4-8947-6c2fb0a55481`.
No additional actor was created. No product, owner artifact, P05 decision, policy,
plan or memory file was edited. The sole tracked output is this report.

The complete 142-line appendix and authority were read. Exact report ancestry,
1396 lines, the unchanged 1254-line prefix and report-only scope were verified.
The prior review ref remains preserved. Accepted A16 and A14.1-.4 source was not
re-audited or promoted into artifact acceptance.

Here `R` means the frozen owner runtime `.claude\runtime\p11-a145\single-03`.
Artifact checks used verified private copies, with read-only comparisons against
original-file and source seals. The reviewed artifact is
`R\artifact\release-notebook.html`; `R\serve\index.html` has identical bytes.

## SPEC, before QUALITY

| Required static control | Independent verdict | Evidence actually checked |
|---|---|---|
| `a145-static-browser` | PASS | Raw `browser\results.json`, operation log, three final DOM records and actual provider/context bind the selected artifact. Recorded input changes the draft; pointer gives count 1, Tab/Enter count 2. Three ready console messages, no recorded console errors. |
| `a145-static-contrast` | PASS, measured scope | Independently recomputed 96 opaque-RGB text samples: eight selected elements, four states, three widths. Minimum `14.732440790112804:1`. Separate negative remains `3.498154318627802:1`, mandatory fail/blocked despite advisory 100. Not every glyph/element/state is certified. |
| `single03-standalone-html` | PASS | Independently reconstructed the exact bytes from the sealed corrected HTML plus original token CSS, page CSS and JS. Two inline styles in original order; identical script after footer; identical parsed visible text. No required external reference, CSS import/URL or module. The isolated serving directory contains only `index.html`. |
| `single03-requests` | PASS | Raw admitted request/response trace and server byte counts agree: three positive HTML loads and three zero-byte optional favicon responses; no required asset fetch. Original CSS/JS endpoints returned 404. Recorded readiness checks preceded the one launch. |
| `single03-keyboard-focus` | PASS, measured scope | Actual operation records and state transitions agree. Focus reaches `add-check`; solid outline/offset are at least 3px, computed outline contrast exceeds 3:1, input/button boxes meet 44px. Final DOM retains the entered draft and count 2. No pixel-based focus clearance is inferred. |
| `single03-responsive` | PASS, measured scope | Recorded 1440x900, 768x1024 and 390x844 document/element widths show no horizontal overflow or off-page measured boxes. PNG headers/hashes agree with full-document sizes 1440x995, 768x1024 and 390x1445. These are emulated viewport results, not physical devices or independent visual layout inspection. |
| `single03-reduced-motion` | PASS | Recorded reduced-motion media is true after keyboard activation; measured animation names are `none` and transition durations are zero. Existing CSS mode/null shader is retained; no added motion dependency. |
| `single03-direct-images` | UNVERIFIED, required | Allowed existing-image file reads returned success text without model-visible pixels in this reviewer context. Image hashes, PNG dimensions, region metadata, owner inspection and DOM cannot supply the missing independent visual observation. |

P07 remains the exact generation-1 `_default` reference:
`sha256:85cb821bf2b9d87a894328c9d5904a8c50d191a2ec2e8e2c3d12af6c1be0c119`.
The design JSON and selected brief/retrieval/provenance hashes remain bound.
Initial/final P05 snapshot and context digests were recomputed. Every selected
snapshot file was hash-checked. All five original mandatory controls/policies
match the old sealed QA record; six static controls are added, not substituted.
All eleven remain mandatory/applicable. Aggregate P05 remains blocked:
`a145-app-build` is `error`; `a145-app-browser` and `a145-app-contrast` are
`unverified`. This review does not alter those records.

## Required observation gap and QUALITY gate

**V1 - required observation unavailable, not a demonstrated product defect
(confidence 10/10).** `R\qa.json:247-276` declares the direct-images obligation.
The owner account in `reports\P11.md:1344-1350` is attributable to the owner;
it is not this reviewer's observation. Both attempted views of the existing
combined image exposed no pixels here. No new image/rendering route was used.

The exact existing contact sheet has SHA-256
`007188fbd4bf36877357e03b40bb2ba660cbfcb212fc7e5287a25a2709c6f1e2`.
Its encoded dimensions and all three original PNG hashes/map references checked.
This reviewer did not independently decode/compare its pixel regions and did not
visually clear any panel. The owner-recorded region comparison remains attributed.

Resolution requires this independent reviewer actually seeing the already frozen
image through an allowed, model-visible image surface. Neither coordinator
inspection nor another native batch is a substitute. No workaround, new renderer,
installation or new artifact attempt is authorized. Preserve the block until an
authorized continuation can supply that observation.

Confirmed new product/artifact defects in the completed SPEC work: **P1 0,
P2 0, P3 0**. These counts do not claim a completed QUALITY pass. Whole static
QUALITY is **NOT RUN / NOT ELIGIBLE** because complete required SPEC is not clear.

## Actual independent checks and immutable history

Private evidence is under session-files `p11-static-single-03-review`.
Absolute argv, explicit allowlisted environments, true exits and hashes are
retained in `pin.json`, `data-check-command.json`, `data-check.log`,
`data-check-results.json`, `history-seals.json` and the commit receipt.

| Invocation | Actual result |
|---|---|
| Installed `python.exe -I -B <private-root>\review_driver.py pin` | Two private intake attempts exited 1: missing union-inventory entry, then cross-checkout LF/CRLF comparison. Corrected only the stopped private intake; both failures preserved. Final pin exited 0 with 64 source seals and 80 copied evidence files. No product/native failure was concealed. |
| Installed `python.exe -I -B <private-root>\review_driver.py data-check` | Exit 0; **10/10 independent data-only tests**, zero failures/errors/skips, runner time 0.292s. All 64 source seals, original 80 evidence seals and executing private scripts unchanged before/after. Another 22 explicitly referenced history files were copied, hash-checked and unchanged before/after. |
| Allowed `functions.view` on the frozen contact sheet, two attempts | Textual success without reviewer-visible image content; **not** a visual pass. |

The wrappers re-executed under verified synthetic HOME/USERPROFILE/AppData/
LOCALAPPDATA/Temp/XDG/LINTEL roots, explicit PATHEXT and derived profile/jobs/audit
paths, fixture Git ceilings/configuration and disabled personal startup/hooks.
There were **zero product imports, browser/server/native/UI calls, network calls,
dependency installs or fresh process investigations** in these independent tests.
Data checks of existing native evidence are not new native execution.

The recorded owner run remains one Chrome `153.0.8010.53` / CDP `1.3` / Node
`v24.16.0` batch, `2026-09-22T21:31:27.353665+00:00` through
`21:31:47.125544+00:00`, true exit 0. Raw lifecycle and subsequent recorded
readback agree on context disposal, browser exit 0, removed owned profile,
empty cleanup errors and absent PIDs 52004/62484/25860. Owned server threads
stopped; proxy recorded 32 non-forwarding 403s. No all-descendant/OS-wide
isolation claim follows from those records.

The original two artifact batches remain on `f72f316`; their sealed records
retain the first hover contrast failure `3.209811300373285:1`, corrected static
result and both mandatory negative failures. The missing-Vite build exit 1 and
registry TLS failure were verified from retained logs, not retried or waived.

The framework build/runtime/contrast, other OS/minimum-runtime, headed/login,
physical device, installed consumer, all-glyph/all-state, PDF/raster and physical
print observations remain outside or unverified. No A14.5/P11 acceptance is issued.
Next action is the coordinator's bounded disposition of V1; the original owner
alone owns any later authorized artifact repair.
