# Native PowerPoint authoring and rendering

Discover the current `powerpoint` canvas with `list_canvas_capabilities` before
using this observed Copilot procedure. It is a host binding, not a new design
schema or proof that every client supports these operations.

## Create an editable presentation view

1. Choose an explicit **new owned** `.pptx` path. Call `open_canvas` with
   `canvasId: "powerpoint"`, a stable caller-chosen `instanceId`, and:

   ```json
   {
     "artifact": {
       "scope": "workspace",
       "path": "owned-run/deck.pptx",
       "mediaType": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
     },
     "initialize": true
   }
   ```

   Use the host's native path spelling. Omit `overwrite`; an existing template or
   output must have explicit replacement authority. Reopening uses no initialize.
2. Invoke `get_model`. Read slide size, actual slide/shape indices and layouts.
   Do not assume 16:9 or that initialization produced zero slides. The observed
   blank canvas starts with one empty 9144000 x 6858000 EMU slide (4:3).
3. Use `batch` with ordered `actions`. Coordinates/extents are EMU; 914400 is
   one inch. On an inspected blank slide at index 0, for example:

   ```json
   {
     "actions": [
       {"action": "add_text_box", "slide": 0, "x": 457200, "y": 457200,
        "cx": 8229600, "cy": 914400, "text": "One scoped decision"},
       {"action": "set_run_format", "slide": 0, "shape": 0, "paragraph": 0,
        "run": 0, "sizePt": 30, "bold": true, "color": "172033"},
       {"action": "add_text_box", "slide": 0, "x": 457200, "y": 1600200,
        "cx": 8229600, "cy": 3657600, "text": "<readable visible claim with its material boundary>"},
       {"action": "add_slide"}
     ]
   }
   ```

   Never pass a placeholder as actual source content. Use `add_table` with rows, cols,
   x/y/cx/cy and `cells` for editable tabular content. Inspect the actual table
   rendering and read cells back through the actual package/renderer operation.
   The observed `get_model` identifies table shapes and bounds but returns no
   cell text; use `read_package_entry` on that slide's XML or `render_slide` to
   verify a cell edit. Do not flatten required editable content into an image.
4. **Create notes in separate serialized calls after composing the slides.**
   Invoke `set_notes` once per slide with `slide` and complete `text`;
   newline-separated paragraphs are supported. Read the saved notes back and
   confirm each slide still has its own intended content before proceeding.

   A native observation on 2026-09-22 found that creating multiple notes parts
   inside one `batch` aliased slide relationships to the same part: the last note
   replaced the others despite a successful response. Separate `set_notes` calls
   preserved distinct notes in the two-slide discriminating probe. Do not rely
   on `opsApplied` or a sidecar to prove retention. If existing notes are already
   aliased, preserve the failed artifact and rebuild a new owned deck with the
   serialized procedure; repeatedly overwriting the shared part is not a repair.

   Preserve all long-form detail in notes/appendix or a delivered linked document,
   retaining the original content.md and speaker-notes.md. Keep citations and
   material limitations on visible slides when needed to qualify their claims.
   Full technical notes are not all spoken talk-track; keep pacing separate.
5. Re-read after batches. Structured edits' observed `expectedVersion` is advisory,
   not a concurrency lock. Inspect before changing existing text or shape indices.

## Reopen and inspect

Open the saved file, call `get_model`, make a small scoped
`set_text` or table-cell edit, read it back, and restore a test marker if used.
Read the actual notes from the reopened artifact, not only the sidecar.
This verifies this API's edit path, not Microsoft PowerPoint desktop behavior.
The host may deduplicate another open of the same path onto its original instance;
an open response alone does not prove a second handle is actionable. For a distinct
reopen check, create a byte-identical copy at another explicit owned path, verify
both hashes and open that file. Record the copy path and actual successful actions.

Invoke `render_slide` with an inspected slide index, or omit `slide` to render the
deck. The observed operation returns SVG rendering. Inspect every returned slide:
visible text, wrapping, clipping/overflow, overlap, table cells, contrast/legibility
and any assets. Compare with the model and source; a successful renderer call
alone is not a visual PASS. Fix layout through native operations and render again.
Store actual returned output when the host makes it available; never fabricate
screenshots or render files from a recreated approximation.

SVG is evidence for that renderer. Explicitly disclose unsupported typography,
tables, effects, animations or image behavior, and any inability to obtain visual
inspection. Shape bounds are useful diagnostics, not proof that text fits.
Missing render capability/coverage leaves the affected requirement unverified.

Use the existing [P05/P07 procedure](../../generate-write/references/fidelity-and-evidence.md)
to bind source, profile and final artifacts. Record provider, tool IDs, instances,
actions, exact paths/hashes, render/reopen results and limitations separately from
source tests and ZIP/model inspection. No upload, macro or global installation is
needed for this local route; a host API is not an OS sandbox.
