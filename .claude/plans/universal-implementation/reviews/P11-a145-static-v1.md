# A14.5 static single-03 independent artifact review, phase 1

**Disposition: static SPEC PASS, 8 of 8 required static controls, including V1, which I observed
directly. Whole static QUALITY PASS: P0 0, P1 0, P2 0, P3 1 (cosmetic).** This clears the static
half's independent artifact gate for the frozen single-03 evidence only. It does not accept A14.5,
P11 or the parent initiative. Aggregate P05 correctly remains `error`/blocked on the three framework
controls, which Phase 2 covers.

## Reviewer, capability and independence

| Item | Evidence |
|---|---|
| Reviewer | Session `aba328fd-4d55-49fb-96fe-777e09849511`, project session `e65586e4-8ba6-4d08-bdae-9449789ce731`, assigned by coordinator `88aecc43-40f9-41d4-8947-6c2fb0a55481`. No role in P11; distinct from builder `f413bdcb` and SAME reviewer `1f655ca9`. |
| Model | Own `events.jsonl` line 1, `session.start`: `selectedModel` `claude-opus-5.5`, `reasoningEffort` `max`, `contextTier` `long_context`. The `assistant.message` events carry `claude-opus-5.5`. The log also holds `gpt-5.5` calls (`reasoningEffort` `none`), each run just before a `permission.requested` event: the host's tool-permission assessor, not the reviewer. |
| Pixel visibility | Blind control. A PowerShell 7 System.Drawing script drew a random five-digit number, shape, colour and quadrant (PNG SHA-256 `7a735914726186b8bdd8a2ca2e62461ce042e29db0e14b1d289b020d19d4ce57`) and wrote the truth to a file I had not opened. After `view` I recorded "41849 top-right; green square bottom-left", then opened the truth: `digits=41849`, `shape=square`, `color=green`, `shape_quadrant=bottom-left`, `digits_quadrant=top-right`. 5/5 match: `view` returns model-visible pixels here. |

## Exact target

| Identity | Value |
|---|---|
| Context branch | `jokerman-microsoft-mastersession-recovery` at `b5413ac5abfce476b88e59aeede95d52d884797a`; `cf483bc89f387857d3c56982bb18a9480c5b04d3` is an ancestor (`merge-base --is-ancestor` exit 0). Re-checked before delivery: the branch is now at `02edb55685c4e699ba73cac6af9ebbc16b54417e`. Its only change adds the P11.md 19:47 redirect decision for the framework restore (blob `887d97a1c020176a571fe6ce841bf5a7c42b48f9`). That does not affect this static review; I will follow its SAS-URL handling in Phase 2. |
| Context blobs read, `git hash-object` equal | `packages/P11.md` `82b425cd8c4fd5526d6facacdcda2dfbe41b549c`, lines 273-308, 373-411 and 412-468; `plan.md` `13c63e913ab636da0443703d61f2578c62e5859d`, A14 at 434-446; `reviews/P11-static-single-03.md` `57c01bf10b17c6d27217a983761363c2114a13ec`, all 123 lines; `reports/P11.md` `57abdbe21a41866fc5ee48c77862823a8ddd00a4`, 977-1090 and 1256-1396. |
| Frozen runtime `R` | Owner worktree `jokerman-microsoft-crispy-bassoon\.claude\runtime\p11-a145\single-03`, 69 files copied privately. Each original hashed identically before and after its copy; every copy equals its original. |
| Checkpoint | `evidence\static-completion-checkpoint.json` `4062fc547a9fd811c89b3bc5f841c43a94febb7be3e1f5583ebfadb7ab9aed0a`. All 67 `inputs_sha256` bindings match; the only unbound files are the checkpoint itself and `evidence\final-intake.json`. |
| Artifact | `artifact\release-notebook.html` = `serve\index.html` `9d76ab47dfa9148b1614a79aa1730e9984af79510e8a1adffce3368eda6abd49`; source `a1b3a45e532ef756f8837cc182064a5f88b375a6`; authority `b1ca886c37f469d705603638632eda6bb7f25831`. |
| Observations | `evidence\observations.json` `df30b77a26065c715666ac01b0217bda210f06486382c167f5c71c21ad6cdb1b`. |
| Profile | P07 `_default` 1.0.0, generation 1, context `0517db27-55b8-43a3-a31f-39d0d6d24d74`, `sha256:85cb821bf2b9d87a894328c9d5904a8c50d191a2ec2e8e2c3d12af6c1be0c119`; design asset `anthropic-default` `1850547864ea41c280e583e2cf315c276f308682a12f81f69c382b5a6aa80c2b`. The same reference is in `profile.json`, the design-spec binding, `results.json`, observations and the checkpoint. |

Images, each hash-verified before any view. The recorded values are in `reports/P11.md:1354-1357`
for the three full-page captures and the sheet, and in the checkpoint `inputs_sha256` for the rest.

| Image | SHA-256 | PNG header |
|---|---|---|
| `browser\browse-N5cNsp\single-1440-full.png` | `fe6274b12405aa5aec85c3f41dcce115d15b3ce38624d4a7f5af52ea4874e10c` | 1440x995, RGB 8-bit |
| `browser\browse-N5cNsp\single-768-full.png` | `9a757d7f00f05f9a4ced187d3e72c4a6055ce76afe8abba2be848d1431c80ece` | 768x1024 |
| `browser\browse-N5cNsp\single-390-full.png` | `1b9a13d130eb7748a203d4e5b3bdad52037c4d37f3983dcd01587f62fcbe6f8f` | 390x1445 |
| `browser\browse-N5cNsp\single-1440-focused.png` | `874f1b2620f7351749aa336662490d34d8140612bd497f31277a49186f194c12` | 1440x900 |
| `browser\browse-N5cNsp\single-768-focused.png` | `1f9a1f5ad8a7f0ba12fed10580f12c032b93e68735874970e6cd21f7bbaab245` | 768x1024 |
| `browser\browse-N5cNsp\single-390-focused.png` | `adca9748ccb0f0e7b212f646f9787354fa9553ae8168f3206ef0fe5a99f012df` | 390x844 |
| `browser\browse-N5cNsp\single-negative.png` | `93236e43b2b05d0210d269b686f4e6f2014ce3dd1373b004e14c8ed8d9ceef99` | 390x844 |
| `evidence\three-viewports.png` | `007188fbd4bf36877357e03b40bb2ba660cbfcb212fc7e5287a25a2709c6f1e2` | 2662x1517 |

## V1: direct image observation

I viewed the seven captures with `view`, each from its hash-verified private copy, before reading
any DOM record or the artifact HTML. I had read only the owner's short prose account
(`reports/P11.md:1331-1350`) beforehand, and I viewed the contact sheet last. The descriptions are
what I saw. Afterwards I checked them against the recorded DOM and contrast data and against my own
pixel analysis. The viewer may resample a large image for display, so I confirmed geometry of 1-3px
with pixel scans rather than by eye.

### Desktop, 1440x900 viewport, full page 1440x995, initial state

- Warm off-white page and near-black text. One centred 1152px column with equal 144px margins. No
  scrollbar.
- The masthead is a single line: bold sans "Lintel / local specimen" at left and regular serif
  "Synthetic data. Nothing is published." at right, with a 1px rule below.
- A heavy, tightly tracked sans heading of about 64px runs on two lines: "A clear record." / "A
  deliberate next step." Below it, a two-line serif paragraph reads "A release notebook for keeping
  the work, its evidence and its next action together." / "This specimen stays on this device."
- A rule opens the two-column workspace: two 544px columns with a 64px gutter.
- The left column holds, in order:
  - the sans heading "Make a local entry";
  - a two-line serif instruction, "Give the synthetic draft a name, then add a check. These actions
    change only this page.";
  - the bold label "Draft name";
  - a full-width input with a thin ink border, small radius and paper fill, showing "Synthetic
    release";
  - a full-width solid near-black button, with bold paper-coloured "Add check" at left and "+" at
    right;
  - bold "0 checks added";
  - serif "Current draft: **Synthetic release**".
- The right column has the heading "What stays in view" and three entries divided by 1px rules:
  "Clear scope" / "One named, synthetic task."; "Visible evidence" / "Observe the result, not just
  the intention."; "Owned next action" / "Keep the next step and its boundary explicit." Below them,
  a pale warm-grey panel reads "No account. No credentials. No remote page."
- The footer rule has "Static HTML specimen" at left and "Same profile. Same design. Local only." at
  right.
- Nothing overlaps or is clipped, all text is crisp and readable, and the page ends 36px below the
  footer text.

### Tablet, 768x1024 viewport, full page 768x1024, initial state

- The same composition with 32px margins; the masthead stays on one line.
- The heading shrinks to about 36px on two lines. The summary keeps two lines.
- Both columns remain, each 320px, as designed above the 760px breakpoint.
  - The left instruction wraps as "Give the synthetic draft a name, then add a" / "check. These
    actions change only this page." The input, button, "0 checks added" and "Current draft:
    Synthetic release" follow.
  - On the right, "Keep the next step and its boundary" / "explicit." wraps, and the panel wraps as
    "No account. No credentials. No remote" / "page."
- The footer stays in one row. The document fits the 1024px viewport, so there is no scrollbar.
- Nothing crosses the right margin and nothing overlaps.

### Narrow, 390x844 viewport, full page 390x1445, initial state

- One column with 20px margins. The masthead stacks the wordmark above the scope note.
- The heading runs to three lines: "A clear record." / "A deliberate next" / "step." The summary
  runs to three lines.
- The entry section follows: a two-line instruction, the label, a full-width "Synthetic release"
  input, a full-width "Add check" button, "0 checks added" and "Current draft: Synthetic release".
- "What stays in view" and its three ruled entries stack below it, then the panel on one line. The
  footer stacks two lines.
- Controls fit the width with no horizontal clipping. The last footer line ends 36px above the
  bottom edge.

### Interaction states: focused captures after the operations

- **1440x900.** The page is scrolled 95px, so the masthead is out of view, and a 15px classic
  scrollbar sits at the right edge. The input reads "Synthetic keyboard check", with "2 checks
  added" and "Current draft: Synthetic keyboard check" below. "Add check" shows a clear focus ring:
  a solid near-black outline, a paper-coloured gap, then a thin coral inner border (hover) around
  the black button.
- **768x1024.** No scrollbar. The same post-action text, ring and coral border.
- **390x844.** Scrolled 216px, so the viewport edge cuts the heading's top line; that is scroll, not
  layout. A scrollbar is at the right. The input, count and draft show the post-action values. The
  button carries the near-black ring and gap, but its border is ink with no coral: the pointer is
  no longer over it.

### Negative control, 390x844

White page. A bold sans heading, "Deliberate negative control", runs on two lines, followed by the
dark paragraph "This separate synthetic fixture must fail the mandatory normal-text contrast
control." Below it, an indented mid-grey line, "Low-contrast normal text: this is not an accepted
design.", is visibly faint against the white.

### Contact sheet

`three-viewports.png` shows the three full-page captures side by side on a grey-blue ground, under
the labels "1440px/768px/390px original full-page screenshot". Its three regions equal the originals
pixel for pixel: 0 mismatches at (16,56), (1472,56) and (2256,56), as mapped by
`three-viewports-map.json`. This independently confirms the owner's exact-copy claim, which the
prior review left attributed.

### Consistency with the recorded DOM and measurements

| Check | Recorded | Observed in pixels |
|---|---|---|
| Text and state | `results.json` counts go 0, 1, 1, 2 at each width. Final DOM draft "Synthetic keyboard check"; `activeElement` is `add-check`. | The same visible strings appear in every capture. |
| Size and overflow | `scrollHeight` 995/1024/1445; `scrollWidth` equals `clientWidth` (1425/768/375) in every state. | PNG heights are 995/1024/1445. Zero non-paper pixels right of the CSS content box (x>1295, >735, >369) at every width, and the last 8 rows are empty. The left edge has only 3-7 antialiasing fringe pixels, one column outside the box. |
| Heading boxes | [136,131,785,270], [32,131,413,210], [20,147,355,265] | [143,141,785,269], [31,136,392,207], [19,152,294,262]: enclosed, within 1px of antialiasing (see O2). |
| Focus geometry | `add-check` box x 136.5, y 574.42, 544x48; outline solid 3px `rgb(20, 20, 19)`, offset 3px. | At 1440, row 598: x131-133 ink, 134-136 paper, 137-138 border, then ink. Column 400: y568-570 ink, 571-573 paper, 574-575 border. The same 3/3/2 pattern holds at 768 (x26-33) and 390 (x14-21). |
| Contrast | Minimum 14.732440790112804:1; heading and focus 17.497722780575504:1; negative 3.498154318627802:1. | From exact glyph-core pixels: ink `#141413` on paper `#faf9f5` gives 17.497722780575504; ink on panel `#e8e6dc` gives 14.732440790112804; paper text on the ink button gives 17.497722780575504; negative `#898989` on `#ffffff` gives 3.498154318627802. |
| Interaction diff, 768 | Input, pointer, Tab and Enter operations. | Initial versus focused capture: 5397 changed pixels in exactly four regions. These are the input value suffix (x112-231, y560-583), the button ring and border (x24-359, y600-663), the count digit (x32-47, y688-703) and the draft value suffix (x184-303, y736-759). No other pixel changed. |

**V1 verdict: PASS (confidence 9/10).** At each width the captures render the selected content, the
profile palette, the heading and body type roles, and the declared layout grammar: two columns at
1440 and 768, one column at 390, and a maximum width of 1152px. There is no overflow, clipping or
overlap, and the text is readable. The focus and hover states are visible, and the images agree
with the recorded DOM and contrast measurements. The remaining point reflects the limits listed
below.

## SPEC, before QUALITY

| Required static control | Verdict | Evidence checked in this review |
|---|---|---|
| `a145-static-browser` | PASS | `results.json` holds initial, pointer, focus and reduced states at each width: count 0, 1, 1, 2, a changed draft, and final active element `add-check`. The console has three `info` "A14.5 static specimen ready" messages and no error or warning. Chrome 153.0.8010.53, CDP 1.3, headless, with the owned profile under `R`. |
| `a145-static-contrast` | PASS, measured scope | The pixel-derived ratios above equal the recorded ones; the minimum is 14.732440790112804:1, for boundary text on the panel. The negative's 3.498154318627802:1 is P05 `effective_status` `fail` with `blocked` true, despite advisory 100 (`negative-control.json`). |
| `single03-standalone-html` | PASS | I read the full HTML: two inline `<style>` blocks (lines 12 and 68, token CSS then page CSS) and one classic inline `<script>` after the footer (line 157). There is no `src`, `url(`, `@import`, `<link>`, module, `http(s)` or fetch; the only `href` is `#main`. `serve\` holds only `index.html`, byte-identical. I did not repeat the prior byte reconstruction from the original assets. |
| `single03-requests` | PASS | `server-lifecycle.json`: a `/health` 200 per server and the old `style.css`, `design-tokens.css` and `site.js` 404 preflights come before any page request. Then three positive `index.html` 200 at 8767 bytes (the artifact size), three `favicon.ico` 204 at 0 bytes, and the negative page at 661 bytes. Every entry has `authorization_supplied` false, and the proxy refusals are 403 with none forwarded. `externalReferences` is empty in all 13 recorded states. |
| `single03-keyboard-focus` | PASS, measured scope | The reduced-state DOM and the pixel scans agree: a 3px ink outline at a 3px offset, 17.5:1 against paper, on a 544x48 button. The input and button declare `min-height: 48px` (HTML lines 98 and 100). |
| `single03-responsive` | PASS, emulated | No horizontal overflow in any recorded state or in pixels, as shown above. The images confirm the layout change at the 760px breakpoint. |
| `single03-reduced-motion` | PASS | In the reduced state `reducedMotion` is true, and every measured element has `animationName` `none` and `transitionDuration` `0s`; `add-check` is `0.15s` before emulation. The reduce block is at HTML line 118. See O1. |
| `single03-direct-images` | PASS | This reviewer's direct observation, V1 above. |

**Static SPEC: PASS, 8 of 8.** All eleven P05 controls remain mandatory and applicable. The aggregate
`qa-result.json` stays `error`/`blocked`: `a145-app-build` is `error`, and `a145-app-browser` and
`a145-app-contrast` are `unverified`. This review does not alter those records.

## QUALITY: whole static artifact

**Q1 - P3 - the narrow display heading leaves a one-word last line (confidence 8/10 for the
observation; cause not verified).** At 390px the heading reads "A clear record." / "A deliberate
next" / "step." (`single-390-full.png`, heading pixels x19-294, y152-262). HTML line 91 requests
`text-wrap: balance`, which should avoid a lone last word. The forced `<br>` at line 132 is the
likely reason the engine does not balance the second sentence; I did not test that. The effect is
cosmetic, and the heading stays readable and in bounds. An optional repair would render the two
sentences without a forced break, or accept the wrap. Not blocking.

There is no P0, P1 or P2 defect. The artifact is soundly built:

- Skip link, landmarks, `label for`, `aria-describedby`, a polite live `output` and an
  `aria-hidden` "+".
- Large contrast margins, and a focus ring in ink rather than the 2.96:1 accent.
- Hover changes only a decorative border, which retires the earlier 3.209811300373285:1 failure.
- `overflow-wrap: anywhere` for long drafts, and a fallback when the draft is empty.
- No external dependency, and a readable measure at every width.

## Observations without severity

- **O1 - the focused images caught a transition still running.** The coral border pixels are
  `#cf7254` at 1440 and `#cd7153` at 768, not the token `#d97757`: about 95% and 94% of the way from
  ink to accent. The pointer and focus states record `transitionDuration` 0.15s with
  `reducedMotion` false, before emulation. The focus ring itself is settled and exact.
  Reduced-motion compliance therefore rests on the computed-style records, not on the images. If
  Phase 2 images must show settled or reduced-motion states, capture after the transition ends or
  emulate reduced motion before the pointer step.
- **O2 - the owner's image bounds come from the scrollbar layout.** They use x 136.5 at 1440 and
  335px content at 390, but the full-page captures have no scrollbar: x 144 and 350px. The recorded
  boxes still enclose the actual heading pixels, so the owner's region checks hold.
- **O3 - text uses LCD subpixel antialiasing,** with coloured fringes such as `#75bbf5`, `#145296`
  and `#dcf9f5`. The contrast figures use exact glyph-core pixels, so this does not affect them.
- **O4 - Phase 2 watch item, outside this artifact.** The generated token CSS defines
  `--color-focus-ring: #d97757` at line 51. At line 64 the component `--focus-ring` references the
  undefined `--color-focus` and falls back to the same accent. The static page uses neither token.
  An app that used the profile focus token on paper would show a 2.96:1 indicator, so I will measure
  the app's actual ring. I have not re-audited accepted source `edecfdf`.

## Limits

- All captures come from one headless Chrome 153 run on Windows with emulated viewports. They are
  not physical-device, other-engine, headed or login, print or raster results.
- Only the initial and post-action focused states were imaged. Input focus, the skip link, hover
  without focus and other states were not.
- For the seven data-backed controls I ran the targeted independent checks listed above. I did not
  repeat the prior reviewer's ten-test data suite, the HTML byte reconstruction or its 96-sample
  recomputation.
- Compliance stays UNVERIFIED without a resolved required-policy source (`profile.json` records
  `not_required`, bundled neutral). This is not a finding.

## Execution record and boundaries

Every worker ran as `pwsh.exe -NoProfile -NonInteractive` (PowerShell 7.6.6) with an environment
that was synthetic from process birth. `env.ps1` set HOME, USERPROFILE, HOMEDRIVE, HOMEPATH,
APPDATA, LOCALAPPDATA, TEMP, TMP, TMPDIR and XDG_CONFIG/DATA/STATE/CACHE/RUNTIME under
`%LOCALAPPDATA%\Temp\a145v` in the real profile, plus `GIT_OPTIONAL_LOCKS=0` and
`GIT_TERMINAL_PROMPT=0`. No `LINTEL_*` variable was present or set.

The host's own tool shell, the parent of each worker, started with the real environment and
dot-sourced `env.ps1` before launching a worker. Tool-shell commands that launched no worker did
only in-process work and spawned no child. That work was reads of `$PSVersionTable`, environment
names, my own `events.jsonl`, the private copies and the intake manifest, plus `Test-Path` and the
creation of the `a145v` directories. Nothing was deleted, and the `/tmp` backing directory was not
touched.

| Step | Script SHA-256 | Result |
|---|---|---|
| Blind control | `control.ps1` `42df499458f6f4476999adb451292c365777467de33826f2333877087c915d76` | exit 0 |
| Git reads | inline | `rev-parse`, `merge-base`, `log`, `ls-tree`, `cat-file` and `hash-object` without `-w`; exit 0 |
| Intake | `intake.ps1` `734582ef0c291cafaf1bdfb0b1f654f3fc6300a3284034371c409d863cb8b9fb` | exit 0: 69 files, copies equal, originals stable |
| Bindings and PNG headers | `verify.ps1` `2471daf6ca8f775252cb82d056ef4214c10388c64d75998920c7b238b0fc10ee` | Run 1 exit 1: after 67/67 had printed, my header parser used a ByRef-like type. Fixed; run 2 exit 0. |
| Pixel analysis | `pixels.ps1` `f6fd4bd3fed81def82928bf668b365b8c79b70cfb82e68f9988b2bd163400633` | Runs 1-2: my in-process C# compile lacked references. Run 3 exit 0. |

I made no repository mutation: no branch, rename, commit, stash, fetch, push or git config write.
Under L-052 I declined the host's automatic branch-rename request. There was no browser, server,
network or installation activity, and no product or owner file changed.

Supplementary evidence is in session files `a145-phase1-evidence\`. The scripts are byte-exact
copies of what executed, with CRLF line endings; the JSON and text files use LF.

- `pixel-control.png` `7a735914726186b8bdd8a2ca2e62461ce042e29db0e14b1d289b020d19d4ce57`
- `pixel-control-truth.txt` `e8b0a5ad6fe04bce6d345a07f14f9c08acd15871096a6b8f20682f09cc43c494`
- `s03-intake.json` `ee373d8318b07be5ccede84bda47c1ac1a5751ec7c73a601d6cb77df0539e107`
- `pixel-analysis.json` `f524a02588f1a597ff45054fdf46d9c98d660094e906400e1f9de0e4542afb79`
- `env.ps1` `d5ef9698e7bd889c82efda70aea9f69c6ed21e1a7df1587fe108a8d8abe94316`

Next action: the coordinator's disposition. Phase 2 starts when the frozen framework-app handoff
arrives.
