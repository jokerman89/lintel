# Lintel — Field guide

[Open the website](https://jokerman89.github.io/lintel/) · [Presentation](https://jokerman89.github.io/lintel/show/index.html) · [Technical reference](https://jokerman89.github.io/lintel/show/technical-reference.html)

A 50-minute level-200 presentation for developers and architects, with a separate six-minute product launch and 18-minute technical module. English slides and speaker notes, three themes (Neon, Paper and Fluent), 60 screens including an untimed video welcome and optional material, and a three-arm kitchen-test guide.

## Use it

Open `index.html` in a browser, or run `python -m http.server 8000` from this directory and visit http://127.0.0.1:8000. The Pages site also offers a downloadable offline kit. Slides and the protocol guide need no backend. The new kitchen dashboard runs from its separately supplied local harness. External source links require internet access.

Slide controls: arrows/Next/Previous, O for overview, N for notes, F for fullscreen. The Neon/Paper/Fluent preference is stored in the browser. The new kitchen chapter uses all three themes; the separate local dashboard has its own design.

## Edit and publish

- `index.html`: homepage and handoff links. Core, the CAIP pack and Benchmark distribution links are intentionally pending.
- `show/content.js`: slide order, titles, notes and timing.
- `show/app.js`, `show/opening.js`, `show/technical.js`, `show/products.js`: diagrams and interactions.
- `assets/products/`: four standalone motifs in Neon and Paper variants. Click any artwork on the product-family slide to open that individual image.
- `site/portal.css`, `site/theme.css`, `site/theme.js`: homepage and themes.
- `show/technical-reference.html`: source-backed inventory and reader.
- `presenter/`: public delivery guides. Keep script/timings aligned when changing slides.
- `comparison/index.html`: new three-arm Service House protocol, prompt and brief. Old comparison source remains archived in Git but is excluded from the public allowlist.
- `web/`: saved helper proof explorer; it does not execute a live agent.

Create a branch, make a focused change, then from the repository root run `python presentations/tech-shots-2026-09-25/tools/build.py` (or `python tools/build.py` from this directory). This validates internal links and the publication boundary, builds `_site/`, and refreshes the offline zip. Preview `_site/` and check all three themes. Open a pull request; the same checks run there. Merging to main deploys the prepared `_site/` artifact via GitHub Pages.

`site-files.json` is the explicit publication allowlist. Add only reviewed public files. Nothing else in the repository or workstation is copied into the deployed site. Do not add raw transcripts, private packs, credentials, caches, nested Git trees or authoring work folders. The build fails on recognizable local workstation paths and credential signatures; human content review still matters.

## Keep the reference honest

The technical content is pinned to Lintel commit `80002ed4aaa8697ff658f50902a469c80e14856d`. See `site/version.json` and the per-item source links. Helpers in the saved proof explorer use a separately recorded revision. When Lintel or a client changes, review affected support claims and their evidence before updating this snapshot. Existence of a file is not proof that a client executes it.

The new kitchen test compares Naked Copilot, Lintel serial and Lintel + Swarming on32frozen requirements. No completed three-arm results are published. Reference/control scores are harness calibration only. The separate harness, private trial metadata and billing/session records are not bundled.

This presentation lives in `presentations/tech-shots-2026-09-25/` inside the [Lintel repository](https://github.com/jokerman89/lintel). The Pages workflow publishes only the validated presentation output. Publishing the site does not release Lintel or bundle the planned product distributions.

## Attribution

Created by Johannes Åkerman. An independent open-source project. See `THIRD-PARTY-NOTICES.md` and the public Sources & evidence page for material provenance.

## Source availability

Current reference uses merged80002ed4 on the0.11.0 beta development line. Historical excerpts in `reference-source/` retain their original pins and are labelled historical. Main/technical slides distinguish delivered adapters from observed host execution.127skills remain current; approximately80is a future consolidation target.

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
