---
name: design-review
layer: foundation
description: 6-pillar visual review of frontend changes — screenshot via /browse, scored findings.
color: orange
tools: Read, Bash, Glob, Grep
voice: internal
cli_support: [claude-code]
---

# /design-review

The polish gate. Drives `/browse` to capture the current state of a frontend change, then evaluates against six pillars: visual polish, accessibility, motion, copy, layout/density, brand consistency. Output is a scored finding list with file:line + screenshot anchors.

Distinct from `/plan-design-review`: that one reviews a design doc *plan*. This one reviews the *built result*.

Voice tier note: the critique itself is internal (builder-to-builder). When the copy pillar fires on a customer-facing surface, this skill references the active pack's voice corpus as the standard, but does NOT produce pack-voice copy. Use a pack-provided voice-rewrite skill for that.

## When to use

- Frontend change is feature-complete; want a polish pass before the active pack's release gate
- A `/qa` run is clean but the UI "feels off"
- Pre-launch on a customer-facing surface — design review is non-negotiable
- After a design-system migration — verify pages still hold together

## When NOT to use

- Backend-only change, no UI touched — skip
- Pure copy change with no layout impact — use a pack-provided voice-rewrite skill directly
- Plan-stage review before any code is written — use `/plan-design-review`

## Inputs

- Required `--url <url>` — running app URL OR local dev server (e.g. `http://localhost:5173`)
- Optional `--routes <file>` — list of routes to review (default: just `/`)
- Optional `--viewport <list>` — viewports to capture (default: `1440x900,375x812`)
- Optional `--baseline <ref>` — git ref to diff against for changed-files context
- Optional `--include-copy-pillar` — explicit opt-in for copy critique (default: on for customer-facing routes per `~/.lintel/config.yaml`)

## Workflow

1. **Preflight.** Verify URL is live (`curl -I`). Verify managed Chromium installed.
2. **Capture phase.** For each route × each viewport: invoke `/browse` to load + screenshot + capture DOM + console log. Artifacts land in `~/.lintel/design-runs/<ts>/`.
3. **Six-pillar pass** — for each captured route:
   - **Visual polish:** alignment, spacing rhythm, hover/focus states present, no Lorem Ipsum, no broken images, no overflow.
   - **Accessibility:** contrast ratio per WCAG AA, semantic HTML in DOM, focus order, alt text on images, ARIA labels where needed.
   - **Motion:** if motion exists, does it respect `prefers-reduced-motion`? Are transitions consistent in duration/easing?
   - **Copy:** typos, voice/tone consistency, length appropriate to context. If customer-facing AND `--include-copy-pillar`: cross-reference against the active pack's voice corpus (modes + ground rules, if the pack defines them).
   - **Layout/density:** information density appropriate, viewport-responsive, no wasted whitespace at mobile, no cramped desktop.
   - **Brand consistency:** colors from token set, typography from token set, signature elements present where expected (per project CLAUDE.md).
4. **Score findings.** Each pillar gets a 1-10 score + finding list. Findings get P1/P2/P3 severity.
5. **Persist via the native `bin/li-review-log`** (legacy alias: gstack-review-log) with `skill: design-review`.
6. **Output** the structured report.

## Report format

```
Design Review: <branch>

URL: http://localhost:5173
Routes reviewed: 3 (/, /portal, /portal/cases/:id)
Viewports: 1440x900, 375x812
Baseline: main@7e7a021

## Pillar scores

| Pillar              | Score |
|---------------------|-------|
| Visual polish       | 8/10  |
| Accessibility       | 6/10  |
| Motion              | 9/10  |
| Copy                | 7/10  |
| Layout/density      | 8/10  |
| Brand consistency   | 9/10  |
Overall: 7.8/10

## Findings (5)

[P1] Accessibility — / hero CTA
   Contrast 3.2:1 on emerald-500 over wave-watermark. WCAG AA requires 4.5:1.
   Screenshot anchor: ~/.lintel/design-runs/.../landing-hero.png#cta
   Fix: darken emerald to -600 OR remove watermark overlap behind CTA.

[P2] Copy — /portal greeting (customer-facing)
   "Welcome back, friend" — too casual for the active pack's register.
   The pack voice corpus suggests a plainer line here ("Welcome back. Pick up where you left off.").
   Use a pack-provided voice-rewrite skill for the actual rewrite.

[P3] Visual polish — /portal/cases card
   3px misalignment between status chip and case title at 1440. Consistent at 375.

[P3] Layout/density — /portal at 375
   AreaCard subtitle wraps to 4 lines; truncate or shorten.

[P3] Brand consistency — /portal/cases/:id
   Section label uses `text-[10px]` instead of `eyebrow` utility. Per project CLAUDE.md frozen-zone token.
```

## Compliance integration

- `/browse` underlies this skill, so Layer 2 prod-host gate applies for the URL.
- Customer-data scan on captured DOM — if real customer data appears in the screenshot/DOM, the artifact is auto-quarantined to `~/.lintel/quarantine/` and the run is marked FAILED (no review possible on un-sanitized data).
- Brand consistency pillar reads from project CLAUDE.md's frozen-zone + token rules. Lintel does not opine on what brand consistency means — the repo does.

## Voice tier note

`voice: internal`. Critique-of-customer-facing content is still engineering-internal output. The copy pillar references the active pack's voice as a *standard to check against*, not voice this skill produces.

## Failure modes

- **URL unreachable:** report + exit. No partial review.
- **Chromium missing:** print install command, exit.
- **DOM capture contains customer-data patterns:** quarantine artifacts, BLOCK review, surface to operator. The review cannot proceed on un-sanitized data.
- **No routes specified + no project default in `~/.lintel/config.yaml`:** ask via AskUserQuestion which routes to review.
- **Copy pillar requested but no pack voice corpus configured:** skip copy pillar, surface "copy pillar deferred — no pack voice corpus installed". Other pillars still run.

## Examples

**Local dev server, default routes:**
```
> /design-review --url http://localhost:5173
[/browse runs 2 routes × 2 viewports = 4 captures]
Pillar scores: Polish 8/10, A11y 6/10, Motion 9/10, Copy 7/10, Layout 8/10, Brand 9/10
5 findings (1 P1, 1 P2, 3 P3). Fix P1 before the active pack's release gate.
```

**Multi-route staging:**
```
> /design-review --url https://staging.example.com --routes routes.txt
[8 routes × 2 viewports = 16 captures]
Pillar avg: 7.2/10. 12 findings, 2 P1.
```

**Skip copy pillar:**
```
> /design-review --url http://localhost:5173 --include-copy-pillar=false
5 pillars scored, copy skipped. 3 findings, all P3.
```

## See also

- `/browse` — the screenshot/DOM engine underneath
- `/plan-design-review` — plan-stage equivalent (use BEFORE code is written)
- A pack-provided voice-rewrite skill — actually rewrite copy to the pack's voice
- The active pack's compliance gates — gate for customer-facing artifacts before they leave
- The active pack's release gate — reads design-review log as part of clearance check
