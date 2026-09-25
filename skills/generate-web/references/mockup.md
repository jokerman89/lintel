# Mockup mode

Use `/generate-web --mode mockup --brief <text-or-file> --out <file.html>` for
a portable static sketch before a framework decision. This mode implies
`--variant single-file`; reject a conflicting variant or input mode.
The ordinary pipeline and frontend-design renderer routes remain unchanged.

## Inputs

- `--brief <path|inline>`: target surface, primary user task, content, layout
  direction and constraints. Retain the complete input rather than a summary.
- `--reference <file|url>`: optional visual anchor. Read a local reference as
  data; use `web-session --mode browse` for an authorized URL.
- `--tokens <file>`: explicit design tokens. Unreadable or invalid selection
  blocks; do not silently substitute a default.
- `--inherit-project`: read the repository's declared design-system location
  and existing components, not a hardcoded product directory or personal vault.
- `--copy-tier <internal|placeholder|pack-voice>`: default `internal`.
  Internal copy is clearly labeled synthetic copy or `[TODO: real copy]`.
  Placeholder copy describes its purpose, such as `[Headline: user benefit]`.
  Pack-voice copy follows the verified configured corpus and remains DRAFT until
  actual customer-share requirements are met. No synthetic copy is a real claim.
- `--out <path>`: required new owned HTML file, or an explicitly authorized
  replacement with its original preimage retained.
- `--preview`: opt-in rendered preview. File generation alone never opens a
  browser, installs a server/framework, or publishes the page.

## Render procedure

1. Read the complete brief, selected references and project tokens. Separate
   existing facts from mock data. If a selected reference is denied or missing,
   report the affected work rather than silently generating a different design.
2. Use the `frontend-design` decision method and design-DNA retrieval to resolve
   a single-file design without recursively starting another renderer.
   Preserve brief > verified profile > corpus precedence, mandatory policy and
   current project constraints. Record explicit token/reference choices as
   selected evidence and brief-backed overrides, not a new private schema.
3. Load the bound `frontend-design-spec.json` with `design_contract.load_design`
   and the external P05/current P07 context. The same `schema_version: 1` and
   `source: frontend-design` contract applies. Do not pretend a raw token file,
   screenshot or missing binding is a resolved render-ready spec.
4. Actually write one HTML document with a doctype, language, charset, viewport,
   meaningful title, semantic landmarks and accessible controls. Put CSS in
   `<style>` and only necessary demonstration interactions in `<script>`.
   There is no build step, framework scaffold, package manifest or new library.
   None/CSS motion and no-shader are normal outcomes. Use authorized embedded
   assets or declared system fallbacks; do not introduce undisclosed remote
   fonts, tracking, form submission or other network activity.
5. Preserve source meaning, tables, units and limitations. Mockup brevity is
   not permission to discard a supplied requirement or qualify it only in an
   undelivered sidecar. Label nonfunctional controls, fake data and placeholders.
6. Validate the actual HTML using the existing mechanical validator with the
   resolved palette. Keep errors and warnings separate. Review through
   `frontend-design-review`; static checks cannot establish keyboard behavior,
   responsiveness, font rendering or reduced-motion measurements.
7. Publish atomically to `--out` within its authorized ownership boundary and
   read back the file. Preserve the original brief/design/evidence alongside
   the run. A file size is not acceptance.
8. If `--preview` is authorized, serve the selected file and its authorized
   assets over owned loopback, observe a health response, and admit that exact
   scheme/host/port before `web-session --mode open` or `--mode browse`.
   Inspect the actual result and stop only the owned server/context. Never
   generate a `file://` navigation recipe. If no safe provider exists, retain
   a manual preview task and mark browser inspection unverified.

## Handoff

Report exact source/reference/token/output paths, copy tier, resolved design,
actual render/validation operations, preview state and missing observations.
This is a mockup, not a production component or deployment.

Use `frontend-design --mode variants --seed <file.html>` to explore another
direction, `frontend-design-review` to critique the built result, and `make-pdf`
for retained print choices. The frozen PDF join does not block HTML creation;
it does leave any unavailable PDF inspection unverified.
