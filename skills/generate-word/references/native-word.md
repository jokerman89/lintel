# Native Word authoring

This is an observed Copilot Word-canvas procedure, not a universal Office API.
Discover the current schema and permissions first. It is an alternative to the
existing declared Node-library route, not a requirement to install Node.

## Create and compose

1. Call `list_canvas_capabilities` with `canvasId: "word"`. Check that create/open,
   paragraph, table and readback operations exist. Record unavailable operations.
2. Select a **new owned** `.docx` path. Call `open_canvas` with `canvasId: "word"`,
   a stable caller-chosen `instanceId`, and:

   ```json
   {
     "artifact": {
       "scope": "workspace",
       "path": "owned-run/document.docx",
       "mediaType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
     },
     "initialize": true
   }
   ```

   `artifact.path` is nested and relative to its scope. Use the host's native path
   spelling. `workspace` selects session artifacts; `repo` selects the repository.
   Do not set `overwrite` for an existing file without replacement authority.
3. Invoke `get_model` on that instance. Read `artifactVersion`, top-level paragraph
   indices, table indices, available styles and section dimensions. Do not assume
   a template has the same paragraph indices as a blank document.
4. Use `batch` for related edits. Its `actions` is an ordered array of objects
   containing `action` plus that operation's arguments. For example, on an
   inspected blank document whose initial paragraph is index 0:

   ```json
   {
     "actions": [
       {"action": "set_paragraph_text", "paragraph": 0, "text": "Technical title"},
       {"action": "set_paragraph_style", "paragraph": 0, "style": "Title"},
       {"action": "insert_paragraph", "after": 0, "text": "Context", "style": "Heading1"},
       {"action": "insert_paragraph", "after": 1, "text": "<complete source paragraph>"},
       {"action": "insert_table", "rows": 2, "cols": 2},
       {"action": "set_table_cell", "table": 0, "row": 0, "col": 0, "text": "Claim"},
       {"action": "set_table_cell", "table": 0, "row": 0, "col": 1, "text": "Evidence"},
       {"action": "set_table_cell", "table": 0, "row": 1, "col": 0, "text": "<scoped claim>"},
       {"action": "set_table_cell", "table": 0, "row": 1, "col": 1, "text": "<source and limitation>"}
     ]
   }
   ```

   Insert every body paragraph without truncation. Table indices are separate
   from paragraph indices. Omit `after` on `insert_table` to append; preserve
   source order when placing tables. Use `set_section` only for requested page
   dimensions/margins; inspect the current values instead of assuming units.
5. Re-read after each batch. The observed `expectedVersion` on structured edits
   is **advisory**, not a stale-write rejection guarantee. Reinspect changed
   content and do not overwrite concurrent user edits.

## Reopen, edit and inspect

Open the saved artifact without `initialize`. Read it with
`get_model`; make one scoped paragraph or cell edit, verify it persisted, then
restore the verification marker if appropriate and read again. This demonstrates
editability through this host API, not a Microsoft Word desktop acceptance run.
The host may deduplicate a same-path open onto its original handle. If a second
handle is not actionable, record that failure; use a hash-verified byte-identical
copy at a new owned path for a distinct reopen check, not an asserted second session.

The observed schema provides `inspect_document`, `list_package_entries`,
`read_package_entry`, `get_model`, paragraph/table edits, headers/footers, section
settings, images and comments. Inspect package warnings without executing macros.
Do not assume every field, tracked change, footnote or template feature is editable.

It does **not** expose a page-render action. `get_model` returns a document model
and projection (styles, dimensions, text, tables), not images of laid-out pages.
Keep rendered pagination, clipping and table-break inspection unverified until a
real available page-render/application operation is run on this exact saved file.
Do not rename model inspection "rendered inspection" or substitute ZIP validity.

Retain source and evidence using the
[P05/P07 procedure](../../generate-write/references/fidelity-and-evidence.md).
Log paths, source/output hashes, instance/action identifiers, edit/readback result,
tool errors and remaining page-render gate separately from documentary tests.
