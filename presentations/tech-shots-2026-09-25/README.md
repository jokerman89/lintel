# Lintel — Field guide

[Open the website](https://jokerman89.github.io/lintel/) · [Presentation](https://jokerman89.github.io/lintel/show/index.html) · [Technical reference](https://jokerman89.github.io/lintel/show/technical-reference.html)

A 50-minute level-200 presentation for developers and architects, with a separate six-minute product launch and 18-minute technical module. English and Swedish slides and speaker notes, three themes (Neon, Paper and Fluent), 50 screens: an untimed welcome, a 50-minute main story in six sections, and two separate optional modules, and a three-arm kitchen-test guide.

## Use it

Open `index.html` in a browser, or run `python -m http.server 8000` from this directory and visit http://127.0.0.1:8000. The Pages site also offers a downloadable offline kit. Slides and the protocol guide need no backend. The kitchen guide is a protocol walkthrough. A separate local harness is required for measured runs; no completed controlled three-arm comparison is published. External source links require internet access.

Slide controls: arrows/Next/Previous, O for overview, N for notes, F for fullscreen. The discreet UK/Sweden flags select English (the default) or Swedish for the homepage, slides and synchronized popup notes. The language preference stays in this browser; a shared `?lang=en` or `?lang=sv` link takes precedence. Switching preserves the current slide and interaction state. Code, commands, archived evidence, technical reference and standalone presenter guides retain their original English content. No translation service is contacted. The Neon/Paper/Fluent preference is stored in the browser. The kitchen guide uses all three themes. Presenter notes follow the current slide; the overview groups the main story into six sections.

## Edit and publish

- After editing `show/content.js`, run `python tools/sync-guides.py` to refresh the four presenter guides before building.
- `index.html`: homepage and handoff links. Core, the CAIP pack and Benchmark distribution links are intentionally pending.
- `show/content.js`: slide order, titles, notes and timing.
- `show/app.js`, `show/opening.js`, `show/refresh.js`, `show/technical.js`, `show/products.js`: navigation, diagrams and interactions. `show/story.css` holds the current story layouts.
- `assets/products/`: four standalone motifs in Neon and Paper variants. Click any artwork on the product-family slide to open that individual image.
- `site/portal.css`, `site/theme.css`, `site/theme.js`: homepage and themes.
- `site/language.js`, `site/language.css`, `site/language-sv.js`: local language control and authored Swedish catalogue. Exact English rendered text is the translation key; update both when changing copy. Preserve technical identifiers and verify both languages in all themes. The catalogue loads as a local script so the offline kit works without a network request.
- `show/technical-reference.html`: source-backed inventory and reader.
- `show/field-guide.html`, `show/story-map.html`: beginner orientation and the six-section story map.
- `presenter/`: public delivery guides. Keep script/timings aligned when changing slides.
- `comparison/index.html`: Service House protocol v2, exact prompt, brief, runtime contract and public provenance. Old comparison source remains archived in Git but is excluded from the public allowlist.
- `web/`: saved helper proof explorer; it does not execute a live agent.

Create a branch, make a focused change, then from the repository root run `python presentations/tech-shots-2026-09-25/tools/build.py` (or `python tools/build.py` from this directory). This validates internal links and the publication boundary, builds `_site/`, and refreshes the offline zip. Preview `_site/` and check all three themes. Open a pull request; the same checks run there. Merging to main deploys the prepared `_site/` artifact via GitHub Pages.

`site-files.json` is the explicit publication allowlist. Add only reviewed public files. Nothing else in the repository or workstation is copied into the deployed site. Do not add raw transcripts, private packs, credentials, caches, nested Git trees or authoring work folders. The build fails on recognizable local workstation paths and credential signatures; human content review still matters.

## Keep the reference honest

The current technical content is pinned to Lintel commit `49f2d15260f096213086f02dfeb1fae6cbe62d45` on the **0.12.0 unreleased** development line, inspected 28 September 2026. See `site/version.json` and the per-item source links. Helpers in the saved proof explorer use a separately recorded revision. When Lintel or a client changes, review affected support claims and their evidence before updating this snapshot. Existence of a file is not proof that a client executes it.

Kitchen protocol v2 compares Naked Copilot, Lintel serial and Lintel + Swarming on 32 frozen requirements. Its source is `e31f80ac411b6a0a6bea6de2afb5bd1d7199f1ed`. No completed controlled three-arm results or verified native v2 rehearsal are published. An earlier timeout and uncontrolled demonstrations are not comparable results. Reference/control scores are historical harness calibration only. The exact input bytes and hashes are recorded in `comparison/kitchen-provenance.json`; `runtime-v2.md` overrides only the brief’s server-start and free-technology paragraphs. The separate harness, private trial metadata and billing/session records are not bundled.

This presentation lives in `presentations/tech-shots-2026-09-25/` inside the [Lintel repository](https://github.com/jokerman89/lintel). The Pages workflow publishes only the validated presentation output. Publishing the site does not release Lintel or bundle the planned product distributions.

## Attribution

Created by Johannes Åkerman. An independent open-source project. See `THIRD-PARTY-NOTICES.md` and the public Sources & evidence page for material provenance.

## Source availability

Current source contains **96 canonical skills, 69 agent roles and 33 hook scripts**. The adapter catalogue names **four supported client families, 13 named surfaces and an explicit manual `other` route**. Fifteen core workflow wrappers expose the starter working set; this is not 96 native wrappers or verified feature parity across every surface. Consolidation retains useful methods; a skill-count target is not a quality measure.

The shared Review Method produces a bounded review packet. MARS adds optional, consented multi-model review where the host can select and verify distinct model identities. Standalone MARS is advisory and grants no REVIEW, QA or SHIP clearance. A REVIEW panel can supply evidence for REVIEW's own content-bound decision. No live MARS panel was executed for this presentation.

Historical excerpts in `reference-source/` retain their original pins. The saved helper explorer keeps its own `28061e434be455ca02f135b73244eaf4f73f3a69` evidence; older technical excerpts retain `275a35447c4ad271e05816ade43ac48f1acec24f`. Updating the presentation does not rerun those demonstrations. See `presenter/sources.html` for the evidence boundaries.

## Brand

Folded L is the selected primary logo, with restrained lime/violet surface shading. `site/mark.svg` is the website master and shared favicon. The same colors are retained in all three themes. [Download the selected brand kit](downloads/lintel-brand-kit.zip) for SVG, transparent PNG and browser/app icon sizes.

## Visual themes

The Fluent theme takes inspiration from Microsoft Fluent 2 while retaining Lintel branding. [Theme design and maintenance](site/THEMES.md) describes the tokens, original artwork and checks. Select a theme in the header or share `show/index.html?theme=fluent`. Preferences stay in browser-local storage; no telemetry or remote font is added.

## Before the room joins

Open `show/index.html#welcome` for the silent looping portal. Choose **Begin** when ready; the original opening is slide 2 at `#three-hours`. The 50-minute story starts there. **Pause motion** keeps a still frame; reduced-motion settings start with the poster. The supplied clip and fallback poster are included in the offline kit.

## Speaker notes on a second screen

Choose **Notes** (or press **N**) in the presentation to open a resizable presenter window. Drag it to your second monitor. The current script, SAY / DO / THEN cues, planned timing and next slide follow slide changes automatically, including overview and section jumps. You can also use the popup's Previous / Next buttons or arrow keys. A− / A+ changes the reading size.

Share only the presentation window with the audience. Choosing Notes again focuses the existing window; closing it leaves the talk running. If your browser blocks the popup, allow pop-ups for this site and choose Notes again. Some browsers open it as a tab; detach that tab into its own window. Notes reconnect after a presentation reload and show a disconnected status if the presentation is closed. No notes are sent to an external service.

For synchronized notes in the offline kit, serve the extracted folder locally with `python -m http.server 8000` and open http://127.0.0.1:8000. Browsers restrict communication between separate `file://` windows; the slides and video still open directly from disk.

Presenter integration check (requires Playwright and Chromium): serve `_site/`, set `LINTEL_PREVIEW_URL` to that local URL, then run `node tools/verify-presenter.mjs`. This tests two real windows, navigation, reconnect, separate decks and popup blocking.

## Story structure

The main story moves through **Meet Lintel → The method → Make it last → Scale the work → Test the value → Make it yours**. Deeper detail lives in the technical module and reference, without a duplicate Backup section. Twelve retired slide anchors resolve to their current equivalent in `show/app.js` so previously shared links keep working. Product and technical timing are separate from the 50-minute main session. The holding screen is untimed.

Language integration check (same Playwright setup): `node tools/verify-language.mjs`. It checks the default, keyboard flags, Swedish content, exact English restoration, interactive state, stored/link preferences, storage failure and the actual notes popup. Also inspect translated slides in all themes and narrow viewports after copy changes.
