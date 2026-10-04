# Read-only PPTX source retention

Run the shipped standard-library checker on the actual saved `.pptx` and explicit
UTF-8 retention sources, without extracting files or calling an application:

```text
python <trusted-source>/skills/generate-ppt/scripts/check_pptx.py --artifact <saved-deck.pptx> --source <retained-source.txt>
```

Repeat `--source` for additional sources. Each non-empty, blank-line-separated
paragraph is a required literal fragment; whitespace is normalized, but Markdown
syntax is not silently removed. For a classified `content.md`/notes inventory,
the Python API `missing_content(parts, required)` accepts its actual complete
paragraphs, citations, limitations and table cells. Obtain `parts` through
`document_text(actual_pptx_path)`, not a generated summary. Retain the original
source and claim-to-output mapping; an excerpt inventory is not proof of complete
brief coverage. Detail intentionally delivered in a linked long-form artifact
needs that artifact's separate check, not a false pass from unlinked sidecar text.

`check_pptx(artifact, sources)` combines those operations and reports exact hashes.
Exit 0 means the supplied fragments survived this ZIP/XML inspection; exit 1
means missing source detail; exit 2 means invalid, unavailable or unsupported input.
None grants review or release clearance. Output is JSON on stdout, with no file
writer, repair, extraction, application launch or fallback destination.

The checker follows presentation order, local slide-to-notes relationships and
matching notes-to-slide backlinks. It refuses missing/malformed/external links,
duplicate IDs/links/members, aliased note parts and unsafe archive paths. Only
presented slides and their actual notes count; orphan parts cannot hide loss.
Formatted text runs join within a paragraph. Matching is literal coverage, not
semantic equivalence, table editability or verification that a qualifier appears
on the visible slide where it is needed.

Default bounds: 32 MiB compressed archive, 128 MiB declared total uncompressed,
16 MiB per member, 2 MiB per XML read, 2 MiB combined source input, 4,096 entries
and 200:1 per-member compression ratio. Limits are checked before decompression
and reads use a limit-plus-one bound. Only unencrypted stored/deflated ZIP and
UTF-8 transitional OOXML are supported; DTD/entity declarations are refused.
Oversize or unsupported files remain unverified, never silently truncated or
repaired. The API's `Limits` allows explicitly chosen positive bounded limits.

This is **ZIP/XML source-retention evidence only**. It is not native rendering,
an application reopen/editability test, every-client acceptance, complete layout
verification, or a PDF reader/renderer. Reopen/edit/readback and actual slide
rendering remain separate observations under the existing
[source-fidelity/P05 procedure](../../generate-write/references/fidelity-and-evidence.md).
