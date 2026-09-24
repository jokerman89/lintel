# Three visual themes, one field guide

Neon is expressive, Paper is editorial, and Fluent is a light product-interface interpretation. All three share the same content, navigation, evidence and timings.

## Fluent design basis

Studied against Microsoft's public Fluent 2 guidance on 24 September 2026:

- [Typography](https://fluent2.microsoft.design/typography): Segoe UI and native system fallbacks, readable hierarchy. This presentation retains large projected type rather than using application-size body text.
- [Color](https://fluent2.microsoft.design/color) and [tokens](https://fluent2.microsoft.design/design-tokens): neutral surfaces, a restrained brand palette and separate colors for text, surfaces, borders and feedback.
- [Elevation](https://fluent2.microsoft.design/elevation): subtle key and ambient shadows distinguish panels and overlays.
- [Layout](https://fluent2.microsoft.design/layout): consistent spacing, responsive reflow and clear grouping.
- [Motion](https://fluent2.microsoft.design/motion): brief purposeful transitions and a reduced-motion equivalent.

This is a Fluent-inspired Lintel theme, not a Microsoft product or a claim of formal Fluent conformance. Lintel's Folded L remains the identity. The gateway and four product motifs are original SVG illustrations; no Microsoft logo, proprietary font file, Mica effect or remote runtime dependency is included. Segoe is used only when installed, with local system-font fallbacks.

## Implementation

`fluent.css` owns prefixed design tokens and theme-specific presentation rules. `theme.js` maps the existing authored color families into separate Paper and Fluent light palettes. The Paper palette is retained. Theme-specific selectors stay outside that adapter, so meaningful highlights, chart marks and selected states can be defined explicitly.

Choose **Fluent** in the header, or link to `show/index.html?theme=fluent`. A theme click updates the current URL and saves a local preference. A valid theme in an incoming URL also saves that preference; embedded viewers receive the effective theme in their URL even if storage is unavailable. The setting is also available to the same-origin embedded reference and helper viewers. The prepared A/B result applications retain their original appearance, so theming cannot rewrite the visual evidence.

The initial deck still defaults to Neon. A URL theme overrides a saved preference. Theme choice never changes the current slide, demo state or source data.

## Maintenance checks

When adding slides or UI, verify all three palettes, selected/hover/focus states, readable muted text, graphical marks and overlays. Keep original screenshots unfiltered. Inspect dense diagrams and long headings at desktop and mobile sizes, including 320px. Check keyboard navigation, the theme query, preference persistence, reduced motion, and the offline download. Compare the original themes before publishing changes to the shared adapter.

Build the public allowlist with `python3 presentations/tech-shots-2026-09-25/tools/build.py` from the repository root. The build includes the CSS, SVG motifs and this guide in the downloadable offline site.

Section navigation shows incremental fill in all three themes. Progress is calculated within each section, including the optional product and technical chapters; backward navigation reduces that section’s fill. Completed and upcoming sections remain visually distinct.
