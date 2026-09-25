# Variants mode

Use `/frontend-design --mode variants` to compare bounded directions around an
existing HTML seed. The director chooses the differences; `generate-web` renders
each selected design. A generated file is not evidence of browser inspection.

## Inputs

- `--seed <path>`: required readable HTML, including a hand-written seed or one
  produced by `generate-web --mode mockup`.
- `--axis <palette|layout|density|motion-language|type-system>`: required single
  axis; "make it better" is not an axis.
- `--count <N>`: integer 2-8, default 4. Refuse values outside that range.
- `--brief <path>`: optional additional constraints, not permission to discard
  seed content, project technology or mandatory policy.
- `--out <dir>`: explicit owned output directory.
- `--only <axis-rule>`: resume one previously recorded failed or missing variant
  from the same seed, axis, rule map, profile and brief. Refuse an unknown rule or
  changed inputs; re-plan changed constraints rather than silently reusing output.

## Procedure

1. Read the seed as data; validate the selected path and useful HTML structure
   before producing variants. Retain its exact bytes, all substantive copy,
   components and the brief. Do not execute arbitrary scripts or fetch its
   external assets while discovering the input.
2. Resolve the same project/profile and design-DNA constraints as design mode.
   Define a concrete rule for each variant, varying only the chosen axis.
   Examples are suggestions, not exceptions to the brief:

   | Axis | Possible rules |
   |---|---|
   | palette | cool-mono, warm-mono, cool-accent, warm-accent, high-contrast, duotone, pastel, jewel-tone |
   | layout | hero-heavy, dense-grid, split-screen, centered-narrow, sidebar-led, magazine |
   | density | spacious, balanced, compact, information-dense |
   | motion-language | static, subtle, expressive, playful |
   | type-system | restrained, expressive, serif-led, sans-led, condensed, wide |

   Filter incompatible rules against the brief before generation. If fewer
   valid directions remain than requested, report the conflict instead of
   producing duplicate variants or relaxing constraints.
3. For each rule, produce its own `frontend-design-spec.json` with
   `schema_version: 1`, `source: frontend-design`, the original bound inputs and
   explicit brief-backed overrides. Keep the full P07 reference; a profile name
   alone is not a binding. None/CSS motion and null/no-shader are complete choices
   needing no library. Retain selected font/library provenance.
4. Pass each spec through `design_contract.load_design` and `renderer-args`,
   then actually invoke `generate-web --from-frontend-design <variant-run>
   --variant single-file --out <variant-N-rule.html>`. Never label a copied
   unmodified seed or a written command as a generated direction.
5. Generate concurrently only with available native delegation, attributable
   isolation and disjoint output ownership. Otherwise generate serially.
   Preserve completed files if a worker or renderer fails; record each failed
   rule and its exact error. Resume with `--only` only after checking current
   inputs and existing output preimages. Never overwrite a successful variant
   without authorization.
6. Run the mechanical validator and `frontend-design-review` on each result.
   Variants inherit requirements, not the seed's pass results. Each changed
   output needs its own P05 observations; one good variant or average cannot
   clear another failed/unverified variant.
7. Write `index.html` with labeled side-by-side iframes, relative links and a
   one-line description of each design move. Preserve a visible failed/pending
   slot rather than implying all requested variants completed. If total embedded
   payload exceeds 50MB, use actual screenshots from `web-session --mode browse`
   instead. Missing screenshots remain missing; linked files are not a claimed
   rendered comparison. The single-page local provider may refuse iframe targets:
   capture variants individually or choose a proven authorized multi-frame host.
8. When preview is authorized, serve the selected output on owned loopback,
   observe health and admit the exact origin before opening with
   `web-session --mode open`. Close only owned contexts/servers.

## Report

Return seed/profile/brief identity, axis and the assigned rule map, requested and
completed counts, actual serial/parallel execution, per-variant files/review
results, index path and failures. Recommend a direction with a reason, clearly
advisory. Keep chosen output distinct from delivery clearance and from any
unperformed browser, customer-share or PDF inspection.
