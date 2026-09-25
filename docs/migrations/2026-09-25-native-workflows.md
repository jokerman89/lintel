---
slug: native-workflow-consolidation
started_at: 2026-09-25
grace_until: none
removal_at: none
old_shape: separate entrypoints for related workflow methods
new_shape: native methods with explicit modes and preserved capabilities
risk_class: medium
detect_pattern: inspect the selected installed catalog and owned inventory
---

# Native workflow migration

This change consolidates entrypoints, not working capabilities. Keep the nine-phase
cycle, engineering modules, useful agent roles, browser/document providers and existing
acceptance requirements. Former names below identify migration sources; they are not
promises of executable aliases. Counts and historical removal schedules are not targets.

Commands use the canonical `/li:<name>` notation. Use the actual host's native `li-*`
wrapper when discovered, or read the canonical skill from the trusted source bundle.
An installed file is not evidence of native discovery or a completed client test.

## Capability replacements

| Former entries | Current route and retained behavior |
|---|---|
| `office-hours`, `plan-ceo-review` | `/li:define` for task-relevant requirements, rough ideas and scope challenge. Engineering is the default lens; `--lens strategy` is explicit. `--mode minimal` does not skip mandatory risk, authority or review. |
| `plan-eng-review`, `plan-design-review`, `plan-devex-review`, `devex-review` | `/li:inspect --target plan\|repo --lens engineering\|design\|devex`. Repeat `--lens` for applicable perspectives. Keep original map/leaf IDs, short-leaf checks and the shared evidence procedure. |
| `plan-tune`, `autoplan` | `/li:cycle --to PLAN`, then actual operator decisions and the existing approval gate. No dormant auto-approval route replaces it. |
| `qa`, `qa-only` | `/li:verify`, read-only by default. `--repair` requests authorized repairs; `--max-iterations` requires that mode (default 3 cycles). `--no-fix` conflicts with `--repair`; report and JSON consumers retain their contracts. |
| `investigate` | `/li:diagnose <failure-or-selected-QA-result>`, retaining scoped investigation, owned bisect/recovery and the caller's state. Optional `--cross-check [--reviewer <name>]` selects an actual additional reviewer. |
| `codex` skill | `/li:cross-check` selects exactly one of `--diff`, `--plan <file>`, `--code <file>` or `--hypothesis <text>`, with optional `--reviewer <name>`. Codex client support remains; a vendor or role label alone does not establish independence. |
| `learn`, `lessons` | `/li:lessons-add` for additions and `/li:lessons-surface` for lookup. Preserve `L-NNN` grammar, update-before-append, deduplication and supersession. |
| `skillify` | `/li:skill-new`, retaining owned scaffold targets and frontmatter validation. Historical candidate preference/type values remain compatible. |
| `document-generate` | `/li:generate-docs --source <path> --target reference\|customer-guide\|tutorial`, retaining source fidelity, voice, depth and output selection. |
| `context-save`, `context-restore` | `/li:pause [label]` or `--label <label>`, and `/li:resume --from <checkpoint>`. Ordinary resume keeps selected-work/ledger/job precedence. |
| `context-warm-related`, `context-warm-adrs`, `context-warm-sessions` | `/li:context-warm --related <topic>`, `--adrs <topic>` or `--sessions [N]`, alongside retained `--path`, `--glob` and `--pattern` selection. |
| `browse`, `scrape`, `open-managed-browser`, `setup-browser-cookies` | `/li:web-session --mode browse\|scrape\|open\|cookies`, preserving each mode's inputs, provider, URL admission, lifecycle and cookie-consent boundaries. |
| `design-consultation`, `design-shotgun` | `/li:frontend-design --mode advice\|variants`; ordinary design remains the default. Variants retain axes, scoped output and actual authorized rendering. |
| `design-html` | `/li:generate-web --mode mockup --brief <path> --out <path>` for a single-file mockup. Default mode remains `artifact`; existing variants and pipeline inputs remain. |
| `design-review` | `/li:frontend-design-review`, retaining the six-dimension `design-review.json` contract and built-UI inputs. An operator-built page can use the existing standalone snapshot/inspection path; do not invent a design spec to review it. |
| `retro`, `landing-report` | `/li:capture --retrospective` and `--release-summary`, alongside SHIP's delivery summary. Preserve selected windows, outputs, voice and evidence; no publication is inferred. |
| `health` | `/li:doctor`, including `--fast` as a quick view and layer/hook/source-registry views of the actual helper result, not invented remote checks. |
| `code-unfreeze` | `/li:code-freeze --lift <exact-path...>`, `--lift --all` or `--list`. Freeze metadata and its optional warning hook remain advisory, not a filesystem lock. |
| `pair-agent`, `careful` | Actual native delegation or an approved swarm, with bounded ownership, explicit confirmation at authority boundaries and owned recovery. Without safe isolation, serialize; without independent review, keep that gate open. |
| `research`, `plan-and-build`, `review-and-ship` | `/li:cycle --mode research-dive`, `--from PLAN --to BUILD`, or `--from REVIEW --to CAPTURE`. Preserve continuity and phase gates. |
| `help`, `v4-migrate` | `/li:catalog` or `/li:welcome` for navigation; `/li:migrations` for historical inspection and explicitly authorized apply/rebind guidance. |
| `personas-rotate` | `/li:role --audience [name]` and `--clear-audience`, using configured persona sources. This is a conversation overlay, not a change to the persistent working role. |

The PDF writer and all direct print options now belong to `/li:generate-pdf`:
input/output, A4/letter/custom paper, portrait/landscape, header/footer, print CSS and
background selection. Its actual preparation and canonical browser-print consumers
remain. ADR-0033 removed the reader, so produced PDF text, pages and visual inspection
remain unverified without a separately authorized observer. Workbook, slide, Word and
other format providers are not an optional cleanup quota.

`verify --json` retains compatible reporting fields (`runner`, `passes`, `failures`,
`skipped`, `exit`, `failures_list`). That summary is not the separate strict v2 QA artifact
consumed by the shared acceptance and SHIP gates.

For additional code-review/diagnosis checks, use `--cross-check --reviewer codex`
when that specific available reviewer is authorized, or `--cross-check` for actual
host selection. This replaces vendor-named review switches without removing Codex
client support. `--no-cross-check` retains the explicit opt-out for optional checks;
it cannot waive required independent review.

## Preserve saved work and evidence

`pause` still writes the compatible `*-context-save.md` checkpoint grammar. Old saves,
including earlier historical formats, remain discoverable and readable. Do not rename,
expire or delete checkpoints to make an entrypoint scan pass. An explicit shared or
historical checkpoint needs its existing authorization before `resume --from` uses
`--explicit`; selection does not create new read permission.

The existing `resume --from <step>` route is also retained. A recognized cycle phase or
exact step ID in the selected job keeps the existing override and readiness checks;
otherwise `--from` selects a checkpoint path. Use an explicit relative/absolute path
when a checkpoint name collides with a step (for example `.\BUILD` on Windows).
`--explicit` is only for authorized shared checkpoint reads, not a readiness override.

Related-context searches still require bounded selectors. Decision loading retains
accepted/deprecated selection; session loading uses 1-5 checkpoints, default 3.
Budget estimates and heading-scoped extraction do not become permission to read an
entire home, private pack or unrelated repository.

Historical records keep their IDs, dates, rationale, failed attempts and original
outcomes. A normalized workflow name is navigation, not a rerun of the historical
check. Retain raw evidence paths, saved schemas and required third-party notices.
Current clearance still binds exact work, acceptance, content, attempt and profile,
consumes the latest applicable independent decision, and requires the original QA.
Report headings, role labels, source rewrites and a previous PASS cannot replace it.

## Update an owned installation

Use the reviewed source and the installation route already selected for the consumer.
For repository kits, run the corresponding adapter `init --target <consumer>` update
and `check --target <consumer>` with its documented client selection. For bare installs,
follow [native installation](../native-installation.md). Installation prerequisites stay
unchanged: bare installation does not gain a Python requirement.

The managed inventory may prune retired source it owns, after conflict preflight.
It must preserve user-created files, local edits, profiles, packs, hooks, private data
and transaction/recovery receipts. Keep receipts with their snapshots. Do not delete
an entire installation or home to force an update, silently resolve a conflict, reuse
a denied tool, or activate a host integration as part of a documentation migration.

Regenerate catalogs, wiki, showcase and native wrappers from their source after the
capability owners are integrated; do not patch generated output by hand. Inspect native
discovery in a new session and record the actual client result separately from static
reference checks. Unavailable host validation or an incomplete provider join remains
explicitly unverified.

See [lifecycle operations](../lifecycle.md), [the cycle](../the-cycle.md),
[client adapters](../client-adapters.md) and [provenance](../provenance.md).
