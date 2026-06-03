---
name: document-generate
layer: foundation
description: Generate documentation from code — engineering reference, customer guides, or onboarding tutorials.
color: green
tools: Read, Write, Bash, Glob, Grep
voice: mixed
cli_support: [claude-code, codex]
---

# /document-generate

Reads source code (or a directory of source files) and produces a target documentation artifact. Three voice tiers: `internal` (engineering reference), `customer` (pack-voiced guide, using the active pack's customer-facing voice tier), `tutorial` (step-by-step onboarding for newcomers).

Distinct from `DocWriter` subagent: that one detects drift + updates existing docs. This skill generates new docs from source.

## When to use

- New module/service needs a reference doc
- Customer-facing API needs a guide before launch
- New team-member onboarding needs a tutorial
- After significant refactor, re-generate engineering reference to replace stale prose

## When NOT to use

- Existing doc just needs an update — use `DocWriter` subagent
- Code itself is the documentation (well-named types + tests) — don't over-document
- Customer-facing content that needs craft, not generation — handwrite, don't generate

## Inputs

- Required `--source <path-or-glob>` — source files to document
- Required `--target <type>` — `reference` | `customer-guide` | `tutorial`
- Optional `--voice <internal|pack>` — voice tier (default: internal for reference/tutorial, the active pack's customer-facing tier for customer-guide)
- Optional `--out <path>` — output path (default: `docs/<source-stem>.md` for reference, `docs/guides/<source-stem>.md` for customer-guide, `docs/tutorials/<source-stem>.md` for tutorial)
- Optional `--depth <shallow|deep>` — shallow = function signatures + one-liners; deep = examples + edge cases + caveats

## Workflow

1. **Read sources.** Glob expansion, parse each file. For each: extract structure (classes, functions, types, exports).
2. **Read context.** Sibling tests (if present) for behavior examples. CHANGELOG / commit history for evolution notes.
3. **Generate per target type:**

   **`reference`** (engineering):
   - Module overview (1 paragraph)
   - Public API table (signature → description)
   - Per-public-export section (signature, description, parameters, return, examples, errors)
   - Internal helpers section (if `--depth deep`)
   - Cross-references to related modules

   **`customer-guide`** (pack-voiced when `--voice pack`):
   - Welcome paragraph (what's this tool for, what's the hidden value)
   - 3-5 "you can do this" sections (what becomes possible)
   - Optional "here's where teams get stuck" (common assumption broken)
   - "Next steps" CTA
   - Marked DRAFT — requires the active pack's compliance gates before distribution

   **`tutorial`** (step-by-step):
   - "By the end of this you'll have..." outcome statement
   - Prerequisites list
   - Numbered steps, each with: what + why + the command + expected output
   - Common errors and how to recover
   - "Where to go next"

4. **Compliance scan.** Layer 2 patterns on every section. Block on hit.
5. **Write.** Atomic write to `--out`.
6. **Report.**

## Report format

```
Document generate: src/lib/dlxClient.ts

Target: reference (depth: deep)
Voice: internal
Out: docs/dlxClient.md

## Generated structure
- Overview paragraph
- 7 public exports documented (signatures + examples extracted from tests/)
- 3 internal helpers documented
- 2 caveats called out from code comments
- Cross-refs to related modules: useCaseBrain, useAgentMode

Size: 4.2KB markdown
Sections: 14
Code examples: 9

## Validation
- All public exports have docstrings ✓
- No Layer 2 compliance hits ✓
- No AI-tell vocabulary detected (Tier 1 blocklist clean) ✓
- Cross-refs resolve to existing files ✓
```

## Compliance integration

- Layer 2 scan on every generated section before write.
- `--voice pack` output: marked DRAFT, gated behind the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default) before distribution.
- AI-tell vocabulary scan (generic Tier 1 blocklist, extended by the active pack's voice corpus if one is configured) for both internal and pack voice — keeps engineering docs from leaking into LLM-style prose.

## Voice tier note

`voice: mixed`. Reference + tutorial default to internal. Customer-guide defaults to the active pack's customer-facing tier (with DRAFT gating). Operator can override via `--voice`.

## Failure modes

- **Source not found:** report missing paths, bail.
- **No public exports detected in source:** ask whether to document internal helpers (operator may want a private-API doc).
- **Compliance scan hits:** STOP, surface which section + pattern, refuse to write.
- **Pack voice requested but no pack corpus configured:** WARN — generation will be best-effort against generic ground rules only. Recommend installing a voice pack before customer distribution.
- **Output path already exists:** ask via AskUserQuestion — overwrite, append, or write to alternative path with -v2 suffix.
- **Tests directory absent (reference target):** generate without example signal, mark as low-fidelity.

## Examples

**Engineering reference:**
```
> /document-generate --source src/lib/dlxClient.ts --target reference --depth deep
[Reads source + tests + comments]
✓ docs/dlxClient.md generated (4.2KB, 14 sections).
```

**Customer guide (DRAFT):**
```
> /document-generate --source src/api/billing/ --target customer-guide
[Generates pack-voice draft]
✓ docs/guides/billing.md DRAFT generated. Run the active pack's compliance gates before distribution.
```

**Newcomer tutorial:**
```
> /document-generate --source supabase/functions/intake-chat/ --target tutorial
[Step-by-step with prerequisites + recovery paths]
✓ docs/tutorials/intake-chat.md generated (6.1KB, 9 steps).
```

## See also

- `DocWriter` subagent — detects drift in existing docs (use post-generate to keep them fresh)
- The active pack's compliance gates — required gate for pack-voice output
- `/learn` — record any documentation patterns worth remembering
- The active pack's voice corpus (`resolve_pack_field voice.corpus`; none by default) — the calibration anchor for pack-voice output
