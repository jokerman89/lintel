# Lintel — Field guide

[Open the website](https://jokerman89.github.io/lintel/) · [Presentation](https://jokerman89.github.io/lintel/show/index.html) · [Technical reference](https://jokerman89.github.io/lintel/show/technical-reference.html)

A 50-minute level-200 presentation for developers and architects, with a separate six-minute product launch and 18-minute technical module. English slides and speaker notes, three themes (Neon, Paper and Fluent), 58 screens including optional material, and prepared browser demos.

## Use it

Open `index.html` in a browser, or run `python -m http.server 8000` from this directory and visit http://127.0.0.1:8000. The Pages site also offers a downloadable offline kit. Core presentation and synthetic dashboards need no API keys or backend. External source links require internet access.

Slide controls: arrows/Next/Previous, O for overview, N for notes, F for fullscreen. The Neon/Paper preference is stored in the browser. The two demo result apps retain their original design in both themes.

## Edit and publish

- `index.html`: homepage and handoff links. Core, the CAIP pack and Benchmark distribution links are intentionally pending.
- `show/content.js`: slide order, titles, notes and timing.
- `show/app.js`, `show/opening.js`, `show/technical.js`, `show/products.js`: diagrams and interactions.
- `assets/products/`: four standalone motifs in Neon and Paper variants. Click any artwork on the product-family slide to open that individual image.
- `site/portal.css`, `site/theme.css`, `site/theme.js`: homepage and themes.
- `show/technical-reference.html`: source-backed inventory and reader.
- `presenter/`: public delivery guides. Keep script/timings aligned when changing slides.
- `comparison/`: prepared same-prompt comparison and original browser implementations.
- `web/`: saved helper proof explorer; it does not execute a live agent.

Create a branch, make a focused change, then from the repository root run `python presentations/tech-shots-2026-09-25/tools/build.py` (or `python tools/build.py` from this directory). This validates internal links and the publication boundary, builds `_site/`, and refreshes the offline zip. Preview `_site/` and check both themes. Open a pull request; the same checks run there. Merging to main deploys the prepared `_site/` artifact via GitHub Pages.

`site-files.json` is the explicit publication allowlist. Add only reviewed public files. Nothing else in the repository or workstation is copied into the deployed site. Do not add raw transcripts, private packs, credentials, caches, nested Git trees or authoring work folders. The build fails on recognizable local workstation paths and credential signatures; human content review still matters.

## Keep the reference honest

The technical content is pinned to Lintel commit `275a35447c4ad271e05816ade43ac48f1acec24f`. See `site/version.json` and the per-item source links. Helpers in the saved proof explorer use a separately recorded revision. When Lintel or a client changes, review affected support claims and their evidence before updating this snapshot. Existence of a file is not proof that a client executes it.

The A/B exhibit contains one prepared run per arm, with the same task, data and stakeholder answers. It is not evidence of a general productivity gain. Public handoff excerpts replace recording-host executable paths with portable prerequisites; input hashes remain the original recording provenance.

This presentation lives in `presentations/tech-shots-2026-09-25/` inside the [Lintel repository](https://github.com/jokerman89/lintel). The Pages workflow publishes only the validated presentation output. Publishing the site does not release Lintel or bundle the planned product distributions.

## Attribution

Created by Johannes Åkerman. An independent open-source project. See `THIRD-PARTY-NOTICES.md` and the public Sources & evidence page for material provenance.

## Source availability

Revision 275a354 is an unreleased local development snapshot, not a publicly installable release. `reference-source/` contains only cited technical excerpts for changed files. Identical-file links resolve to public revision 28061e4. Source publication here does not publish or modify the Lintel development branch.

## Brand

Folded L is the selected primary logo, with restrained lime/violet surface shading. `site/mark.svg` is the website master and shared favicon. The same colors are retained in both themes. [Download the selected brand kit](downloads/lintel-brand-kit.zip) for SVG, transparent PNG and browser/app icon sizes.

## Visual themes

The Fluent theme takes inspiration from Microsoft Fluent 2 while retaining Lintel branding. [Theme design and maintenance](site/THEMES.md) describes the tokens, original artwork and checks. Select a theme in the header or share `show/index.html?theme=fluent`. Preferences stay in browser-local storage; no telemetry or remote font is added.
