# Lintel showcase

Single-file HTML system maps. Open directly in a browser.

| File | What it shows |
|---|---|
| [`lintel-the-harness.html`](lintel-the-harness.html) | Full Lintel system map: 8-phase cycle, skill families, 83 agents, voice tiers, layers, vault loop, intent → flow examples, gaps inventory, lesson quartet. Canonical-pattern dogfood (Fraunces + Inter + JetBrains Mono + CSS mesh-gradient). |

## Open

```bash
# macOS / Linux
open docs/showcase/lintel-the-harness.html

# Windows (PowerShell)
start docs\showcase\lintel-the-harness.html

# WSL
explorer.exe "$(wslpath -w docs/showcase/lintel-the-harness.html)"
```

## Why these files exist

System maps for visual onboarding — same job as the system diagram in PR #21 design doc, but rendered for human-eye scan rather than markdown-reader parse.

Each page is self-contained: zero JS dependencies, fonts via Google CDN, all interactivity inline. CSS mesh-gradient hero is the no-WebGL fallback path from the v3.7 canonical shader-snippet.

## L-001 trade-off (canonical dogfood)

These pages use the bundled `ultra-modern-lovable-style` canonical pattern as styling baseline:

- Typography: Fraunces (display) + Inter (body) + JetBrains Mono (labels/code)
- Motion: CSS scroll-driven + conic-gradient drift (Lenis/GSAP not loaded — single-file constraint)
- Component library: none (raw HTML/CSS — showcase = demonstration, not production)
- Shader: CSS conic-gradient mesh (Paper Shaders fallback path)
- prefers-reduced-motion: respected (drift animation disabled)

Per v3.7 L-001 trade-off explicit acknowledgment: this canonical content stays as schema-by-example. Re-evaluate after Fas D real-dogfood demonstrates 3+ operator-extracted patterns dominate vault → demote to docs/samples/.
