# P13 skill preservation and disposition

## Boundaries and evidence key

This source map retains the released P13 A+B preservation work and its accepted-current
delta, not a second task ledger. **No original leaf is completed** by a row, a count, an unchanged file or a
source-selection test. Current package status remains in the coordinator's selected
[work map](../work.json), [plan](../plan.md) and [handoff](../handoff.md).

The original set is exactly the 46 records in the
[workflow audit](../../../engineering/audits/2026-09-20-universal-quality/reviews/workflow.json)
plus 80 in the
[capability audit](../../../engineering/audits/2026-09-20-universal-quality/reviews/capabilities.json),
cross-checked against the original
[inventory](../../../engineering/audits/2026-09-20-universal-quality/inventory.json)
at `28061e434be455ca02f135b73244eaf4f73f3a69`. Its
[human-readable recommendations](../../../engineering/audits/2026-09-20-universal-quality/skills-inventory.md)
are proposals, not deletion authority or current readiness labels.

The historical A+B source comparison below remains pinned to accepted first-unit checkpoint
`204ea7253b18fb1849fa6de94e1b283b098039b5`, product `b1d4caf`. All 126 original
canonical paths/names remain. Swarm is the one separate addition, for 127 current skills.
Every source link below is the current canonical path; no entry is moved or replaced
by this unit. The descriptor does not change any canonical skill or role body.

The **accepted-current comparison** is
`42abfcba39ac80a271ff57e838ffccb1d7f6ed7c`. Since the historical pin, 43 original
skill bodies plus Swarm changed. Compared with the original `28061e4` inventory,
**73 original skills are changed and 53 remain byte-identical**: 33 old U rows
became C, ten old C rows changed again, and Swarm remains a separate addition.
The [accepted-source delta](#accepted-source-delta) supersedes historical pending
statements for those rows at its stated evidence layer. It is not a new corpus audit.

Historical evidence labels used in the retained 126-row table:

- **U**: original/204ea725 Git blob bytes are identical (86 skills at that checkpoint). The original audit's
  full-reading method assessment is retained, not relabeled as a new full-body review.
- **C**: source changed before A+B (40 skills at that checkpoint). The row identifies its retained method
  and relevant accepted component evidence; integration boundaries are still explicit.
- **D**: exact per-path original/current bytes, headings and inventory comparison recorded
  in builder `ab-preservation-baseline.*`; see [P13 evidence](P13.md). This proves source
  retention, not that a model followed the procedure.
- **S**: [source-selection checks](../../../../tests/unit/catalog-selection.py) validate
  original-key coverage, links, descriptor/closure/refusal and source data. They are
  structural/metadata evidence, not 127 executed workflows.
- **C01**: [P01 final review](../reviews/P01-final.md), helper acceptance only.
- **C03**: [P03 final review](../reviews/P03-final.md) and
  [joined-path final](../reviews/P03-joined-path-final.md), owned context/recovery only.
- **C04**: historical [P04 component final](../reviews/P04-final.md) and
  [preservation map](P04-preservation.md); current A22.7 evidence is J04 below.
- **C05**: [P05 excerpt/context final](../reviews/P05-excerpt-context-final.md), content-bound
  control/review consumers, not all downstream invocation paths.
- **C06**: [P06 provider/component final](../reviews/P06-provider-repair-final.md), source
  adapters and recorded host boundaries, not blanket live-client parity.
- **C07**: [P07 long-path final](../reviews/P07-long-path-final.md), profile contract and
  resolver evidence, not every lifecycle wrapper.
- **C09**: historical [P09 content review](../reviews/P09-content-4a9b946.md) and the existing
  [69-role preservation map](P09-agent-preservation.md), knowledge-layer evidence;
  later source/module/mode evidence is J09 below.
- **C13**: exact independent first-unit SPEC then QUALITY PASS at
  `09a3c6ec3c3fa2c3232e921f52accc9262088e8b`, SHA-256
  `695e934d0b393e1c8c3a34644db0bb67964344d62830527de40f7c071fb3de58`;
  this is first-unit source discovery, not later selection/consumer acceptance.
  Current evidence is J13 below. See [P13 evidence](P13.md).

Examples below are source-grounded **worked/recheck scenarios**, not fresh execution
claims. C-labels reuse only the narrower accepted evidence they actually name. U rows
deliberately preserve the original useful method and its known gaps while their owner
works on a separate release. Names such as P08/P10/P11/P12 identify accountable existing
packages, not imported WIP or newly granted write scope. Coordinator assignment is
explicit where an entrypoint crosses package ownership.

Historical `merge`, `retire`, `pack` and `staged` recommendations remain visible.
No physical pruning, relocation or automatic alias retirement is performed. General
maturity remains unknown. Only Visio retains current explicit `TEMPLATE ONLY`
evidence. Accepted PDF/XLSX source methods use unknown/null stage records after
coordinator reconciliation `678ae22`; this does not make those methods absent.
See [source selections](../../../../lib/capability-selections.json). Old audit labels
do not upgrade or demote changed producers automatically.

## All 126 original skills (historical source comparison)

The recommendations, retained method/argument value and historical evidence below
are preserved. U/C and pending wording in this table describe `204ea725`, not an
assertion that subsequent accepted work is missing. The current delta follows it.

| Original and current source | Original recommendation; source state | Responsible package and acceptance | Retained method and output | Change or grounded retention rationale | Worked example and evidence | Remaining boundary |
|---|---|---|---|---|---|---|
| [adr-new](../../../../skills/adr-new/SKILL.md) | refine; U, same path | Coordinator entry; P01 A04 | Numbered decision record with title, status and context. | Keep focused authoring; P01 repaired its actual helper rather than replacing the skill. | Create a titled ADR in a synthetic empty repo; D, C01. | Helper acceptance is not evidence of every skill invocation or authority choice. |
| [analyze](../../../../skills/analyze/SKILL.md) | refine; U, same path | P08 A08.3 | Requirements/design/build consistency findings with evidence gaps. | Preserve three analysis legs; do not substitute a newly guessed initiative. | Two selected maps must not share a newest-file result; D, S. | P08 work-map/semantic integration is not accepted by this row. |
| [audit](../../../../skills/audit/SKILL.md) | refine; U, same path | P08 A13.1/.4 | Filter and summarize recorded audit events without mutation. | Preserve the read-only view; existing inline parsing remains owned follow-up. | A malformed event must remain an error, not healthy history; D. | Unified event coverage is not established here. |
| [autoplan](../../../../skills/autoplan/SKILL.md) | merge; U, same path | P08 A10.3 | Convenient intake-to-planning handoff. | Retain familiar entry; no merger until approved-work-map semantics match. | A DRAFT intake must not become BUILD approval; D. | Original producer/status mismatch is not silently cleared. |
| [brief-forge](../../../../skills/brief-forge/SKILL.md) | staged; C, same path | P04 A21/A22 | Explicit envelope construction, validation and bounded receiver handoff. | Retain optional invocation and actual shared validator; no automatic activation. | Malformed/forbidden payload must fail before audit/output; D, C04. | Component checks are not dormant-hook activation or A22.7 completion. |
| [browse](../../../../skills/browse/SKILL.md) | rebuild; U, same path | P11 A16 | Inspect/read/interact/screenshot intent and evidence report. | Preserve useful browser operations; do not import a pending provider or daemon. | Request a screenshot through an actual discovered provider; D. | This source is not proof of a working managed browser or live acceptance. |
| [build](../../../../skills/build/SKILL.md) | refine; C, same path | P08 A08.2/.3; P04 A22 | Short leaves in coherent packages, per-leaf evidence and SPEC before QUALITY. | Keep ADR-0026 discipline and mapped Swarm opt-in additions. | Failed package retains original leaf IDs for restart; D, C04. | Wider lifecycle/semantic execution is not inferred from source additions. |
| [capture](../../../../skills/capture/SKILL.md) | rebuild; C, same path | P08 A08.3/A13.2 | Reconcile delivered work, durable lessons and next-session handoff. | Retain knowledge capture and work-map preservation additions. | No measured usage stays unknown; optional export needs an approved destination; D. | Learning/event/export integration is not verified here. |
| [careful](../../../../skills/careful/SKILL.md) | refine; C, same path | P06 A06.3/.4 | Opt-in caution around actual high-impact actions. | Host-specific hook assurances became explicit available-control checks. | Missing host control stays unavailable, not an active guard; D, C06. | Advisory caution is not enforced host policy. |
| [catalog](../../../../skills/catalog/SKILL.md) | keep; C, same path | P13 A19.1/.2 | Deterministic catalog generation and metadata-first source discovery. | Strong thin dispatcher retained; compact query added without changing its frontmatter. | `--json --name=match` resolves the same canonical router; D, C13, S. | Source discovery is not installed selection or live invocation. |
| [clean](../../../../skills/clean/SKILL.md) | merge; U, same path | P08 A08.3/A13 | Checkpoint and fresh-session context guidance. | Preserve honest chat-history limits; consolidate only through a verified context consumer. | Save needed state rather than claim messages were deleted; D. | Watcher/configuration convergence is not completed here. |
| [cli-fingerprint](../../../../skills/cli-fingerprint/SKILL.md) | rebuild; C, same path | P06 A06.1-.3 | Explicit surface and actual binding description. | Replace guessed vendor-wide capability with the accepted registry contract. | Copilot App and CLI remain distinct; D, C06. | A declaration is not permission or observed execution. |
| [code-freeze](../../../../skills/code-freeze/SKILL.md) | rebuild; U, same path | P08 A13.3 | Cooperative frozen-path declaration and audit intent. | Preserve scoped coordination use; never invent universal enforcement. | An unintegrated writer remains an enforcement gap; D. | Advisory state is not a tested write barrier. |
| [code-review](../../../../skills/code-review/SKILL.md) | merge; C, same path | P05 A03 | Lightweight diff review consuming the shared evidence contract. | Preserve ad hoc entry without a second review truth. | Dirty/untracked selected content must bind the review; D, C05. | Source checks are not independent actors or every review invocation. |
| [code-unfreeze](../../../../skills/code-unfreeze/SKILL.md) | merge; U, same path | P08 A13.3 | Explicit scoped removal of a cooperative freeze. | Keep lifecycle counterpart; no silent permission restoration claim. | Remove only the named freeze scope after authorization; D. | Writer-wide enforcement remains not established here. |
| [codex](../../../../skills/codex/SKILL.md) | rebuild; C, same path | P06 A06.3/.4 | Independent outside-opinion handoff using real available tools. | Keep second-opinion value without fabricated CLI flags/model access. | Missing provider yields a durable manual handoff; D, C06. | A named tool/model is not proof of independent review. |
| [compliance-gate](../../../../skills/compliance-gate/SKILL.md) | rebuild; C, same path | P05 A02 | Applicable mandatory/advisory controls with explicit outcomes. | A mandatory unknown/failure now dominates advisory scores. | One required unknown blocks despite many passes; D, C05. | A pack label is not enterprise enforcement or certification. |
| [context-budget](../../../../skills/context-budget/SKILL.md) | rebuild; C, same path | P03 A11 | Observed capacity/usage, labelled byte estimates and local watch thresholds. | Remove invented context capacity; keep `--watch` as a skill input. | No telemetry reports unknown rather than green; D, C03. | An estimate is not measured active or billable usage. |
| [context-cool](../../../../skills/context-cool/SKILL.md) | merge; C, same path | P03 A01/A11 | Future-read exclusions consumed by the shared selector. | Preserve useful retrieval control, not claims of erasing sent messages. | Exclude an owned file then verify subsequent selection omits it; D, C03. | Cooling is not memory reclamation or disk cleanup. |
| [context-restore](../../../../skills/context-restore/SKILL.md) | refine; C, same path | P03 A01/A11 | Owner-checked checkpoint reading and bounded restart references. | Strong recovery method retains historic owned records and explicit sharing boundary. | Foreign same-basename checkpoint must refuse implicit restore; D, C03. | Notes do not restore model hidden state or authorize referenced actions. |
| [context-save](../../../../skills/context-save/SKILL.md) | refine; C, same path | P03 A11 | Collision-safe owned checkpoint with task, decisions and next action. | Keep strong concrete output; shared helper owns names and reservation. | Empty reservation is not a discoverable completed checkpoint; D, C03. | Saved notes are not a full transcript or reset capacity. |
| [context-warm](../../../../skills/context-warm/SKILL.md) | rebuild; C, same path | P03 A01 | Literal scoped selection, byte preview and bounded file reads. | Replace evaluated selectors with trusted-source mechanics. | Metacharacters remain literal and cannot run a command; D, C03. | File selection is not authority to export private data. |
| [context-warm-adrs](../../../../skills/context-warm-adrs/SKILL.md) | merge; C, same path | P03 A01/A11 | Relevant decision-record selection with status provenance. | Retain focused entry through shared context mechanics. | Markdown accepted-status metadata must remain discoverable; D, C03. | Retrieval does not supersede architecture or accept a proposed ADR. |
| [context-warm-customer](../../../../skills/context-warm-customer/SKILL.md) | pack; C, same path | P03 A01; P13 A18 boundary | Explicitly authorized customer-context selection and classification. | Retain use case; no inferred account, repo or export destination. | Reject an unapproved outside/customer path; D, C03. | Optional classification is not consent to read customer material. |
| [context-warm-from-url](../../../../skills/context-warm-from-url/SKILL.md) | rebuild; C, same path | P03 A01.5; P11 A16 | Parsed URL admission, redirect revalidation and bounded extraction. | Preserve retrieval while fixing exact versus wildcard hosts. | Allowed initial host cannot authorize a redirected disallowed host; D, C03. | Synthetic policy tests are not live transport/browser acceptance. |
| [context-warm-related](../../../../skills/context-warm-related/SKILL.md) | merge; C, same path | P03 A01/A11 | Bounded related-source hints with explicit paths and sizes. | Retain retrieval strategy without making similarity an authority signal. | A matching archive remains historical, not an accepted decision; D, C03. | Ranking is not correctness or freshness. |
| [context-warm-sessions](../../../../skills/context-warm-sessions/SKILL.md) | merge; C, same path | P03 A11 | Small owner-filtered checkpoint history selection. | Preserve strong selector and bounded history instead of duplicating checkpoint storage. | Request two owned prior sessions, not unrelated same-name files; D, C03. | Historical notes are not current work approval. |
| [cycle](../../../../skills/cycle/SKILL.md) | refine; C, same path | P08 A08; P04 A22 | Nine-phase orchestration, presets and explicit mapped execution. | Preserve all phases and Swarm opt-in without a tenth phase. | Research/review intent must not become BUILD/SHIP; D, C04. | Source structure is not complete lifecycle/semantic execution evidence. |
| [da](../../../../skills/da/SKILL.md) | refine; C, same path | P09 A09 | Schema, migration, query, retention and analytics decision dispatch. | Retain seven methods; accepted decision reference adds depth without replacing runtime. | Replayed event must not double-count a sink result; D, C09. | Knowledge acceptance is not module/checkpoint integration. |
| [define](../../../../skills/define/SKILL.md) | rebuild; U, same path | P08 A10.1/.2 | Requirements, alternatives and explicit design decision. | Preserve requirements craft; missing decisions cannot trigger an unrelated venture interview. | Bounded maintenance needs scope, not founder profiling; D. | Adaptive intake behavior is not verified by unchanged source. |
| [design-consultation](../../../../skills/design-consultation/SKILL.md) | merge; U, same path | P11 A14 | Evidence-led critique and bounded design alternatives. | Keep consultation value; no premature collapse into another entry. | Compare two relevant options on the user's actual criterion; D. | Shared-design/profile integration is not complete here. |
| [design-dna](../../../../skills/design-dna/SKILL.md) | refine; U, same path | P11 A14; P13 A20 | Local design retrieval, token doctrine, profiles and validation methods. | Strong corpus/search method and actual attribution remain intact. | Select a palette from explicit profile and retained source evidence; D. | Static retrieval is not rendered accessibility or complete notice distribution. |
| [design-html](../../../../skills/design-html/SKILL.md) | merge; U, same path | P11 A14 | Self-contained design preview artifact. | Keep fast-preview use case; shared renderer must preserve real supplied content. | Preview a real brief rather than placeholder copy; D. | Source preview recipe is not rendered acceptance. |
| [design-review](../../../../skills/design-review/SKILL.md) | merge; U, same path | P11 A14; P05 control seam | Screenshot/source-based visual findings. | Preserve critique dimensions while the shared result contract is reconciled. | Unavailable keyboard observation remains unverified; D. | A screenshot score is not runtime accessibility evidence. |
| [design-shotgun](../../../../skills/design-shotgun/SKILL.md) | merge; U, same path | P11 A14 | Controlled variants and comparison index. | Retain single-axis exploration rather than rename/delete it. | Vary density while holding content and hierarchy fixed; D. | Variant/retry contract is not validated by this map. |
| [devex-review](../../../../skills/devex-review/SKILL.md) | keep; U, same path | P09 A09.3/.4 | Fresh-clone developer-journey friction report. | Strong reproducible onboarding lens remains distinct from generic code review. | A missing setup command is reported with actual step and error; D. | No fresh-clone workflow was executed for this row. |
| [dh](../../../../skills/dh/SKILL.md) | refine; C, same path | P09 A09 | Deployment, observability, capacity, SLO and recovery decisions. | Retain dispatch methods and accepted operations reference. | v2-only persisted data prevents an assumed safe v1 traffic rollback; D, C09. | Reference knowledge is not deployment or module orchestration evidence. |
| [discover](../../../../skills/discover/SKILL.md) | refine; U, same path | P08 A08.3/.4 | Bounded repo/ADR/reusable-component map. | Preserve architecture discovery; source roots and selected work stay explicit. | Existing helper is found before designing a replacement; D. | Full mapped downstream consumption is not claimed. |
| [doctor](../../../../skills/doctor/SKILL.md) | merge; U, same path | P10 A12 | Unified installation/health diagnosis entry. | Retain familiar diagnostic front door, not another installer. | Missing helper is a diagnostic failure rather than healthy output; D. | The legacy prose is not actual installed/runtime acceptance. |
| [document-generate](../../../../skills/document-generate/SKILL.md) | refine; U, same path | P12 A15 | Source-grounded repository/reference documentation. | Preserve traceability and specialist writing distinct from slide generation. | A command claim must cite current code or an executed example; D. | Document fidelity/rendered output is not demonstrated by source retention. |
| [eval](../../../../skills/eval/SKILL.md) | pack; U, same path | P13 A18/A19 | Optional pack-voice corpus calibration. | Preserve its narrow voice purpose instead of advertising general model evaluation. | No configured corpus yields a clear missing-input result; D. | Voice scores are not general workflow quality or compliance clearance. |
| [fix](../../../../skills/fix/SKILL.md) | keep; U, same path | P08 A08/A10.3 | Short known-defect entry through existing lifecycle stages. | Retain convenience without a competing plan/status contract. | A bounded bug still needs valid BUILD acceptance; D. | Shortcut/source presence is not tested phase execution. |
| [frontend-design](../../../../skills/frontend-design/SKILL.md) | rebuild; U, same path | P11 A14 | Design-direction synthesis across typography, motion and shader choices. | Keep thesis and specialist methods; no imported unfinished shared schema. | A static form can choose no motion/no shader; D. | Complete renderer dispatch is not accepted from this legacy source. |
| [frontend-design-review](../../../../skills/frontend-design-review/SKILL.md) | rebuild; U, same path | P11 A14 | Multi-dimension design findings and mandatory evidence separation. | Preserve useful dimensions while owner reconciles schema/measurement gaps. | Missing runtime evidence must not become a high average pass; D. | Scoring/source checks are not live accessibility or performance validation. |
| [frontend-motion](../../../../skills/frontend-motion/SKILL.md) | refine; U, same path | P11 A14 | Motion hierarchy, reduced-motion and performance decisions. | Retain craft, including CSS-only/no-motion alternatives. | Reduced-motion request should stop unnecessary motion; D. | Planned budget is not measured frame/device performance. |
| [frontend-shader](../../../../skills/frontend-shader/SKILL.md) | refine; U, same path | P11 A14 | Deliberate shader/no-shader decision and fallback design. | Keep useful restraint and graceful degradation. | No shader is valid when it adds no user value; D. | Shader-loop stopping and device acceptance are not exercised here. |
| [frontend-style-extract](../../../../skills/frontend-style-extract/SKILL.md) | merge; U, same path | P11 A14 | Observed/inferred style extraction and profile handoff. | Preserve confidence distinctions instead of duplicating unsupported emitters. | An inferred font stays inferred until asset evidence exists; D. | Profile roundtrip and unsupported flags are not fixed by this map. |
| [frontend-typography](../../../../skills/frontend-typography/SKILL.md) | refine; U, same path | P11 A14 | Font roles, axes, licensing, loading and fallbacks. | Retain substantive type decisions, not a fashionable font default. | Missing weight/axis evidence requires a fallback; D. | Local recipe is not font-license or rendered-layout acceptance. |
| [full-engineering-pass](../../../../skills/full-engineering-pass/SKILL.md) | rebuild; C, same path | P09 A09.1/.5 | Cross-domain result reconciliation and handoff. | Retain composition purpose and accepted mandatory-control boundary additions. | One failed required domain cannot hide in an average; D, C05/C09. | Shared domain/workflow execution is not complete here. |
| [generate](../../../../skills/generate/SKILL.md) | rebuild; U, same path | P12 A15 | One factual brief routed to artifact-specific outputs. | Preserve common facts without assuming a universal lossy renderer contract. | Word reasoning must not be truncated to slide-sized prose; D. | Pending format work is not imported or advertised complete. |
| [generate-app](../../../../skills/generate-app/SKILL.md) | merge; U, same path | P11 A14; P10 scaffold seam | Application skeleton with install/build failure handling. | Keep real runnable-project intent before any verified consolidation. | Failed dependency setup is not a working app; D. | Framework/runtime flows are not validated by source identity. |
| [generate-design](../../../../skills/generate-design/SKILL.md) | rebuild; U, same path | P11 A14; P12 A15 consumer | Shared design choices mapped to output formats. | Preserve mappings; do not fork an unfinished design schema. | Document palette should consume the selected profile, not a parallel default; D. | Shared renderer/profile wiring is not complete here. |
| [generate-outline](../../../../skills/generate-outline/SKILL.md) | refine; U, same path | P12 A15.2 | Narrative outline with key messages and source-content identity. | Keep reusable authoring structure and concise complete briefs. | A short complete brief should not fail an arbitrary word threshold; D. | The owner’s content repair is not present in this frozen source. |
| [generate-pdf](../../../../skills/generate-pdf/SKILL.md) | staged; U, same path | P12 A15.4 | Preserved PDF strategy slot and future page/font/source-fidelity requirements. | Current explicit TEMPLATE ONLY warning is retained and digest-bound. | Select source-format export only with an actual writer; D, S. | Staged declaration is not a working PDF pipeline. |
| [generate-ppt](../../../../skills/generate-ppt/SKILL.md) | rebuild; U, same path | P12 A15.3 | Narrative/layout retrieval and editable presentation intent. | Preserve format craft while actual render/reopen evidence is separately owned. | Overflow must be observed slide by slide, not inferred from file existence; D. | New native-artifact results are not assumed here. |
| [generate-qa](../../../../skills/generate-qa/SKILL.md) | rebuild; U, same path | P12 A15; P05 A02 seam | Artifact-specific QA report and explicit unavailable checks. | Keep report purpose; zero errors cannot substitute for required coverage. | No render check means no rendered-layout pass; D. | Format/policy integration is not verified by this inventory. |
| [generate-style-learn](../../../../skills/generate-style-learn/SKILL.md) | merge; U, same path | P11 A14 | Palette/font learning and reusable style artifact. | Preserve extraction value pending shared-profile roundtrip. | Unknown font source stays unknown in the learned profile; D. | Existing palette/STYLE outputs are not new schema acceptance. |
| [generate-visio](../../../../skills/generate-visio/SKILL.md) | staged; U, same path | P12 A15.4 | Editable diagram slot with connector/layout/reopen goals. | Keep explicit template warning and future implementation path. | SVG preview alone cannot prove editable VSDX reopening; D, S. | No diagram writer or renderer is claimed implemented. |
| [generate-web](../../../../skills/generate-web/SKILL.md) | merge; U, same path | P11 A14 | Single-file/framework web rendering with source design input. | Retain preview and app use cases until verified unification. | A static lint pass cannot establish interactive behavior; D. | Rendered/runtime acceptance is not supplied here. |
| [generate-word](../../../../skills/generate-word/SKILL.md) | rebuild; U, same path | P12 A15.3 | Document/template writing with headings, tables and source fidelity. | Preserve actual prose needs rather than slide-shaped constraints. | Multi-paragraph reasoning and citations survive DOCX composition; D. | Native layout/render evidence is not imported from WIP. |
| [generate-write](../../../../skills/generate-write/SKILL.md) | refine; U, same path | P12 A15.2 | Evidence-led content draft for selected format/audience. | Preserve full reasoning and uncertainty rather than universal short sections. | Long technical caveat remains in source even for a shorter slide view; D. | Content-preservation repair is not verified by this unchanged file. |
| [generate-xlsx](../../../../skills/generate-xlsx/SKILL.md) | staged; U, same path | P12 A15.4 | Spreadsheet slot with table/formula/recalculation goals. | Preserve explicit template warning, not a fabricated ready renderer. | Reopen and recalculate formulas before claiming workbook correctness; D, S. | No actual recalculation or Excel execution is claimed. |
| [handoff-size-check](../../../../skills/handoff-size-check/SKILL.md) | rebuild; U, same path | P08 A08.3; P03 admission seam | Bounded selected-artifact size/admission check. | Keep warning intent; use real selected map and observations. | Missing host limit stays unknown rather than assumed capacity; D. | Complete artifact-consumer/budget wiring is not accepted here. |
| [health](../../../../skills/health/SKILL.md) | merge; U, same path | P10 A12 | Installation/version/provenance diagnostic view. | Keep health use case under one future verified doctor path. | Unsupported upstream checking must be disclosed as unrun; D. | Stale clone/layout recipes are not live health evidence. |
| [help](../../../../skills/help/SKILL.md) | merge; C, same path | P13 A19.1/.2 | Shared metadata listing by kind/category/voice/surface. | Preserve familiar help entry; remove independent corpus parsing and invented hook counts. | Source role entry is not a registered host agent; D, C13, S. | Listings are not native discovery or invocation acceptance. |
| [hooks-status](../../../../skills/hooks-status/SKILL.md) | rebuild; U, same path | P08 A13.1/.4 | Hook observation report with actual event coverage. | Preserve diagnostics but do not equate no log with no execution. | Missing success records remain unobserved; D. | Event-field reconciliation and real registration are not claimed. |
| [instruction-parity-check](../../../../skills/instruction-parity-check/SKILL.md) | merge; C, same path | P06 A05.4 | Deterministic shared-protocol comparison and explicit host limits. | Replace text-similarity proxy with real synchronized-source checks. | Changed protocol block should produce drift; D, C06. | Structural parity is not identical client/model behavior. |
| [investigate](../../../../skills/investigate/SKILL.md) | keep; U, same path | P09 A09.3/.4 | Reproduction, competing hypotheses and causal evidence report. | Strong report-first method retained, without forced implementation. | Removing one suspected cause must change the symptom before claiming root cause; D. | No actual incident reproduction is implied. |
| [jobs](../../../../skills/jobs/SKILL.md) | refine; U, same path | P08 A08/A13 | Repository-owned job listing and lifecycle handoff. | Retain useful helper-backed records and dormant auto-spawn boundary. | Two repos with one basename must not share job ownership; D. | Full lifecycle observation is not established here. |
| [landing-report](../../../../skills/landing-report/SKILL.md) | refine; U, same path | P08 A13 | Source-grounded delivered-work report, with empty evidence explicit. | Strong distinct reporting method retained rather than inventing customer impact. | No matching shipped commits yields no demonstrated shipped outcome; D. | Report generation is not publication or measured business value. |
| [learn](../../../../skills/learn/SKILL.md) | refine; U, same path | P08 A13.2 | Add/update/supersede L-NNN lessons through shared memory mechanics. | Preserve grammar and historical knowledge, not arbitrary deletion. | A corrected lesson supersedes its predecessor; D. | Concurrent learning/event integration is not exercised here. |
| [lessons](../../../../skills/lessons/SKILL.md) | merge; U, same path | P08 A13.2 | Friendly lessons presentation and retrieval entry. | Retain name while avoiding another removal/retrieval policy. | Superseded lesson stays historical rather than active advice; D. | Planned consolidation is not implemented by this map. |
| [lessons-promote](../../../../skills/lessons-promote/SKILL.md) | rebuild; U, same path | P08 A13.2; P02 destination seam | Explicit generalized-lesson promotion with provenance. | Keep value transfer but no guessed personal repo or branch switch. | Missing configured destination blocks publication; D. | Promotion grammar/destination acceptance is not supplied here. |
| [lessons-surface](../../../../skills/lessons-surface/SKILL.md) | keep; U, same path | P08 A13.2 | Small relevance-ranked non-superseded lesson set. | Strong bounded retrieval remains the shared method. | No relevant lesson emits no invented advice; D. | Retrieval source retention is not every host/session invocation. |
| [maintenance](../../../../skills/maintenance/SKILL.md) | rebuild; U, same path | P08 A13; P10 storage seam | Installation/storage diagnosis and bounded context advice. | Preserve operations while separating disk cleanup from model context. | A manual usage record is not a complete invocation census; D. | Storage/archive and fake-compaction corrections are not complete here. |
| [make-pdf](../../../../skills/make-pdf/SKILL.md) | merge; U, same path | P12 A15.4 | HTML/Markdown-to-PDF conversion mode. | Retain concrete conversion entry until full PDF mode preservation is verified. | Nonempty output still needs page and source-content checks; D. | File size is not rendered PDF correctness. |
| [migrations](../../../../skills/migrations/SKILL.md) | refine; U, same path | P10 A12 | Read-only migration/overdue-state discovery. | Retain old recovery visibility beyond grace dates. | Overdue unresolved migration remains visible; D. | Missing catalog is not proof that migration completed. |
| [office-hours](../../../../skills/office-hours/SKILL.md) | merge; U, same path | P08 A10 | Structured exploration into reviewable requirements. | Preserve useful questioning as a scoped intake mode. | No implementation follows a merely DRAFT interview result; D. | Legacy global store/intake wiring is not cleared here. |
| [open-managed-browser](../../../../skills/open-managed-browser/SKILL.md) | merge; U, same path | P11 A16 | Explicit browser-launch/check mode. | Keep simple operator intent but require a real provider. | Unavailable launch API yields blocked evidence, not a fictional daemon; D. | Source launcher is not installed browser capability. |
| [orientator](../../../../skills/orientator/SKILL.md) | refine; U, same path | P08 A08.1 | Task/phase recommendation with explicit uncertainty. | Keep cheap routing; do not promote historic staged escalation into execution. | Ambiguous compound intent requests clarification rather than writes; D. | Unchanged skill text is not current P08 classifier acceptance. |
| [pack-create](../../../../skills/pack-create/SKILL.md) | refine; U, same path | P10 A12; P07 A07 | Authorized pack authoring and validation. | Preserve identity/policy ownership rather than generate company policy unsolicited. | Missing required input remains a question, not default enterprise rules; D. | Pack scaffold/lifecycle acceptance is not shown here. |
| [pack-list](../../../../skills/pack-list/SKILL.md) | refine; U, same path | P10 A12; P07 A07 | Distinguish discovered, valid and active packs. | Retain read-only discovery through the established resolver boundary. | Discovered directory is not an active/valid pack; D. | No personal store or active profile was inspected. |
| [pack-switch](../../../../skills/pack-switch/SKILL.md) | refine; U, same path | P10 A12; P07 A07.3/.4 | Explicit validated profile transition and drift visibility. | Preserve switching intent without a second hardcoded pointer. | Failed required pack must not silently become neutral; D, C07. | Accepted resolver is not this wrapper's mutation acceptance. |
| [pack-validate](../../../../skills/pack-validate/SKILL.md) | refine; C, same path | P07 A07/A20; P10 wrapper seam | Shared manifest/schema/product/feature compatibility checks. | Strong bounded validation entry now consumes the accepted shared parser. | Unknown required capability version refuses; D, C07. | Schema compatibility is not live company-policy enforcement. |
| [pair-agent](../../../../skills/pair-agent/SKILL.md) | rebuild; C, same path | P06 A06.3 | Scoped specialist collaboration with actual delegation or serial fallback. | Keep collaboration without hardcoded vendor exclusion or imaginary sandbox. | No isolated writers means sequential work; D, C06. | A role prompt is not filesystem confinement or independent evidence. |
| [perf-mode](../../../../skills/perf-mode/SKILL.md) | retire; C, same path | P03 A11 | Heavy-task planning/admission guidance under real host limits. | Preserve useful planning while removing fictitious context/model control. | A marker cannot enlarge context capacity; D, C03. | Retained entry is not a performance or pricing control. |
| [perfbench](../../../../skills/perfbench/SKILL.md) | refine; U, same path | P09 A09.4 | Comparable before/after workload and uncertainty report. | Keep performance evidence method, not a decorative small-sample benchmark. | Different workload mixes invalidate a claimed latency gain; D. | No paid/live benchmark was run for this row. |
| [personas-rotate](../../../../skills/personas-rotate/SKILL.md) | merge; U, same path | P10 A12 | Scoped audience/tone overlay with reset semantics. | Preserve audience perspective, distinct from persistent role activation. | A temporary audience lens must not silently alter company identity; D. | Existing persistence behavior is not verified here. |
| [plan](../../../../skills/plan/SKILL.md) | refine; C, same path | P08 A08/A10; P04 A22 | Approved map/trio, short leaves, coherent packages and reviewable handoff. | Preserve strong planning contract plus optional Swarm topology. | External task IDs remain authoritative through package grouping; D, C04. | Source plan additions are not downstream semantic/lifecycle acceptance. |
| [plan-and-build](../../../../skills/plan-and-build/SKILL.md) | merge; U, same path | P08 A10.3 | Named PLAN-to-BUILD convenience range. | Retain entry without silently creating another status or approval ledger. | BUILD receives the same approved map selected by PLAN; D. | Range consistency is not tested here. |
| [plan-ceo-review](../../../../skills/plan-ceo-review/SKILL.md) | pack; U, same path | P08 A10.2 | Optional premise/demand/strategy lens. | Preserve business reasoning without making venture framing universal. | Maintenance scope does not need a founder interview; D. | Optional strategy lens is not a mandatory neutral-core gate. |
| [plan-design-review](../../../../skills/plan-design-review/SKILL.md) | refine; U, same path | P11 A14; P08 selection seam | Planned UI states, accessibility and interaction review. | Retain UI-specific criteria only when UI is in scope. | Backend-only plan marks design review inapplicable with reason; D. | Planned criteria are not rendered UI acceptance. |
| [plan-devex-review](../../../../skills/plan-devex-review/SKILL.md) | refine; U, same path | P08 A10; P09 devex seam | Review planned developer workflows and friction. | Keep distinct developer-journey lens with repository-grounded criteria. | Missing first-run setup in a plan is a concrete gap; D. | No developer-journey execution is claimed. |
| [plan-eng-review](../../../../skills/plan-eng-review/SKILL.md) | refine; U, same path | P08 A10.3 | Architecture/tests/performance and package-boundary scrutiny. | Preserve engineering decisions without newest-global-context assumptions. | Shared-file packages cannot pretend independent writers; D. | Source scoring is not independent plan approval. |
| [plan-tune](../../../../skills/plan-tune/SKILL.md) | staged; U, same path | P08 A10.4 | Preference-learning intent with explicit consumer prerequisite. | Retain future utility; historic staged recommendation is not current capability evidence. | A preference file without a reader cannot alter decisions; D. | No activation or conflict-reconciliation engine is inferred. |
| [profile-switch](../../../../skills/profile-switch/SKILL.md) | rebuild; U, same path | P10 A12; P06 host seam | Authorized host/profile transition and owned recovery intent. | Preserve need while unsupported marker toggles remain an owned gap. | No supported host API means no plugin enablement claim; D. | This source is not permission for private/global configuration changes. |
| [qa](../../../../skills/qa/SKILL.md) | refine; C, same path | P05 A03 | Scoped test-and-repair with real failure evidence and review invalidation. | Retain active repair mode distinct from read-only shipping verification. | Product changed after review requires fresh affected evidence; D, C05. | Passing a rewritten baseline is not regression proof. |
| [qa-only](../../../../skills/qa-only/SKILL.md) | refine; C, same path | P05 A02/A03 | Non-mutating test execution and explicit failure/unverified outcomes. | Keep verification-only contract and zero-test distinction. | Zero matched required tests yields no evidence; D, C05. | A runner exit alone is not test coverage or SHIP clearance. |
| [research](../../../../skills/research/SKILL.md) | rebuild; U, same path | P08 A08.1/A10 | Sourced findings/options under read-only intent. | Preserve research before design approval rather than forcing BUILD. | Information inquiry cannot authorize deployment; D. | Wrapper intent propagation is not accepted by this row. |
| [resume](../../../../skills/resume/SKILL.md) | refine; C, same path | P08 A08.3/.5; P03/P04 seams | Artifact-based recovery of original map, unfinished work and review gates. | Strong continuation method retains owned checkpoint and Swarm paths. | Missing independent review stays outstanding on restart; D, C03/C04. | Resume is not a tenth phase or full lifecycle acceptance. |
| [retro](../../../../skills/retro/SKILL.md) | merge; U, same path | P08 A13.2 | Signal-based reflection and optional durable learning. | Keep useful no-lesson result rather than mandatory ceremony. | No new durable lesson is a valid outcome; D. | Consolidated CAPTURE consumption is not completed here. |
| [review](../../../../skills/review/SKILL.md) | refine; C, same path | P05 A03; P04 A22 | SPEC then independent QUALITY with content-bound required controls. | Preserve strong staged review and exact selected result identity. | Later relevant rejection revokes older PASS; D, C05. | A heading or model label is not independent clearance. |
| [review-and-ship](../../../../skills/review-and-ship/SKILL.md) | merge; U, same path | P08 A10.3; P05 consumer | Convenient REVIEW-to-SHIP range. | Retain name while inheriting one scope and publication boundary. | Current review evidence must match the shipped content; D, C05. | Underlying evidence acceptance is not this wrapper's complete integration. |
| [role](../../../../skills/role/SKILL.md) | refine; U, same path | P10 A12; P07 overlay seam | Light activation, off/rotate/frame/deep-dive role modes. | Preserve each mode and sensitivity boundary; no alias removal. | A private deep-dive requires explicit source permission; D. | Existing sed/persistence recipes are not accepted mutation behavior here. |
| [role-new](../../../../skills/role-new/SKILL.md) | refine; U, same path | P10 A12 | Structured role creation and targeted `--update`. | Keep responsibility/cold-knowledge capture without forced global publication. | Update one approved role while retaining sensitivity; D. | No private role or destination was created or inspected. |
| [roles-list](../../../../skills/roles-list/SKILL.md) | merge; U, same path | P10 A12; P07 resolver seam | Frontmatter-only role discovery without deep private context. | Strong bounded list view remains useful and distinct from activation. | List metadata, then request permission before private body load; D. | Listing is not native registration or a policy switch. |
| [safe-install](../../../../skills/safe-install/SKILL.md) | rebuild; C, same path | P03 A01; P10 A12 consumer | Owned snapshot/restore dispatch with late-change refusal. | Replace destructive backup recipes without silently taking user ownership. | Later edited file blocks restore rather than being overwritten; D, C03. | Snapshot acceptance is not full installer/default-path acceptance. |
| [sc](../../../../skills/sc/SKILL.md) | refine; C, same path | P09 A09.4; P05 control seam | Threat/auth/secrets/evidence/incident decision methods. | Retain seven specialist methods and accepted decision reference. | Framework applicability and required policy must be sourced; D, C09. | Generic old defaults are not live regulatory requirements or clearance. |
| [scaffold](../../../../skills/scaffold/SKILL.md) | rebuild; U, same path | P10 A12 | Safe reusable project-foundation initialization. | Keep interactive intent; avoid a second manual copy installer. | Existing user prose must survive repeated init; D. | Original recipe is not P10 preservation acceptance. |
| [scaffold-internal-tool](../../../../skills/scaffold-internal-tool/SKILL.md) | merge; U, same path | P10 A12 | Internal-tool scope/flavor and working-flow handoff. | Preserve project intent without imposed stack/CI choices. | Existing repository conventions take precedence over a template; D. | A generated skeleton is not a verified internal workflow. |
| [scaffold-mvp](../../../../skills/scaffold-mvp/SKILL.md) | merge; U, same path | P10 A12 | MVP scope, honest stubs and implementation handoff. | Retain fast-start value without erasing project authority. | Unsupported flow is marked a stub, not working production behavior; D. | No application or installer was run here. |
| [scope](../../../../skills/scope/SKILL.md) | refine; U, same path | P08 A08/A10 | Concise boundaries, dependencies and planning-depth choice. | Strong proportional disambiguation retained. | Larger estimated work cannot authorize more scope; D. | Routing/DEFINE handoff is not verified by unchanged source. |
| [scrape](../../../../skills/scrape/SKILL.md) | merge; U, same path | P11 A16 | Schema-shaped extraction with partial-failure provenance. | Keep useful extraction controls under a real browser/retrieval adapter. | A malformed extracted record is not silently accepted; D. | No remote page, robots policy or browser run is claimed. |
| [sense](../../../../skills/sense/SKILL.md) | merge; U, same path | P08 A08.1/.2 | Cheap orientation using repo memory, work and real host limits. | Preserve starting context without duplicated scope/state authority. | Establish cycle identity before phase writes; D. | Start-of-session prose is not observed lifecycle behavior. |
| [setup-browser-cookies](../../../../skills/setup-browser-cookies/SKILL.md) | merge; U, same path | P11 A16.4 | User-owned authentication surface setup and explicit verification. | Preserve credential avoidance; do not copy cookies into prompts or fixtures. | User chooses login surface; absent provider stays blocked; D. | No authentication or personal browser data was accessed. |
| [ship](../../../../skills/ship/SKILL.md) | rebuild; C, same path | P05 A02/A03; coordinator delivery | Exact reviewed content, non-mutating QA and explicit publication authority. | Retain delivery intent with shared latest-evidence gate. | Changed selected file or failed required QA blocks delivery; D, C05. | Local review checks are not remote merge/deploy authorization. |
| [skill-router](../../../../skills/skill-router/SKILL.md) | merge; C, same path | P13 A19.1/.2 | Literal compact discovery followed by at most three candidate bodies. | Retain `match` and semantic judgment without whole-corpus prompt loading. | Hostile literal query returns data/no-match, never a command; D, C13, S. | Structural caller checks are not measured model-routing quality. |
| [skillify](../../../../skills/skillify/SKILL.md) | rebuild; U, same path | P13 A19 | Turn demonstrated repeated work into a useful skill. | Preserve authoring intent; obsolete output/activation path remains future work. | A TODO-only template is not an outcome-changing workflow; D. | No new canonical authoring pipeline is delivered by A+B. |
| [spec-kit](../../../../skills/spec-kit/SKILL.md) | refine; U, same path | P08 A08.3; P04 mapped contract | External spec/plan/tasks remain authoritative through one map. | Strong adapter retained; shared reference changed without rewriting this entry. | External task IDs must survive BUILD/REVIEW/RESUME; D, C04. | All downstream consumers are not proven by the source entry alone. |
| [status](../../../../skills/status/SKILL.md) | merge; U, same path | P08 A08/A13; later P13 view | Everyday view of current job/cycle evidence. | Preserve useful name without inventing activity from missing dormant logs. | No log means unobserved, not automatically idle/complete; D. | Status/welcome integration is not in this unit. |
| [ta](../../../../skills/ta/SKILL.md) | refine; C, same path | P09 A09.3 | API/boundary/NFR/dependency/scaling/complexity dispatch. | Preserve seven methods and accepted architecture decision reference. | Idempotency may need a unique constraint, not a new service; D, C09. | Knowledge is not module runtime or measured capacity. |
| [tq](../../../../skills/tq/SKILL.md) | refine; C, same path | P09 A09.4 | Coverage, contracts, regression, performance and reliability decisions. | Retain seven focused methods and accepted testing reference. | A closed enum consumer rejects a new value despite additive schema; D, C09. | Toy/structural examples are not full product test acceptance. |
| [uniformity](../../../../skills/uniformity/SKILL.md) | refine; U, same path | P13 A19 | Maintainer structural-consistency diagnostics. | Preserve its honest floor, not a surrogate for skill usefulness. | A consistent header does not prove a workflow delivers; D. | New uniformity integration is not part of A+B. |
| [usage-log](../../../../skills/usage-log/SKILL.md) | refine; U, same path | P08 A13.1/.4 | Explicit manual usage events and labelled estimates. | Retain provenance rather than fabricate comprehensive telemetry. | Missing tokens stay unknown rather than zero; D. | Optional events are not a full invocation or cost census. |
| [v4-migrate](../../../../skills/v4-migrate/SKILL.md) | retire; U, same path | P10 A12 | Historical version-specific migration/recovery entry. | Keep recoverability until verified replacement and explicit archival. | An overdue migration remains actionable, not erased by date; D. | No old recipe is endorsed as current universal installation. |
| [welcome](../../../../skills/welcome/SKILL.md) | refine; C, same path | P06 A05/A06; later P13 view | Task-first onboarding with actual tools and honest fallback. | Retain concise entry and accepted surface distinction. | A native-format wrapper still needs live discovery evidence; D, C06. | No status/welcome change or live onboarding claim follows from A+B. |

## Accepted-source delta

This is the exact 43-original-plus-Swarm changed-path set from `204ea725` to
`42abfcba39ac80a271ff57e838ffccb1d7f6ed7c`. The historical recommendations above
are not changed by this table. Current C means changed original bytes; it is not
semantic acceptance. The 83 originals outside this delta keep their historical
U/C identity (53 U and 30 C). New descriptor rows still need this unit's independent
review; these evidence keys cover only already accepted predecessors.

- **J04**: [final joined Swarm review](../reviews/P04-final-08879e9.md), product
  `08879e9`, review `8a3a35c`, integration `6e32d1f`. Bounded A22.7 closes at its
  contract/fixture level, not live-person, policy or whole-initiative acceptance.
- **J09**: [module source review](../reviews/P09-modules-5c99612.md), product
  `5c99612` / review `114ddfe3`, integration `2d789a4`; later
  [N1 correction](../reviews/P09-n1-correction-031d408.md) and
  [finite mode evidence](../reviews/P09-modes-1b75264.md) stay separately attributed.
  This does not establish every role's native registration or all domain executions.
- **J11**: [direct design source](../reviews/P11-a14-a1b3a45.md), `a1b3a45` /
  `edecfdf`, integration `e1cb9d2`; [browser source/observations](../reviews/P11-browser-final-d3b5569.md),
  `d3b5569` / `3049811`, integration `7cb3812`. Current
  [static artifact review](../reviews/P11-static-single-03.md) retains unverified V1;
  framework TLS/build and A14.5 remain open.
- **J12**: [common/Word/PPT source](../reviews/P12-common-source-32dac88.md),
  `32dac88` / `f2c1d09`; [PDF source](../reviews/P12-pdf-1ba9f9b.md),
  `1ba9f9b` / `ae793d39`; [workbook source](../reviews/P12-workbook-839e6df.md),
  `839e6df` / `21e5228`, integrated through `751af6c`/`81c5b01`.
  The [P12 pipeline candidate](../reviews/P12-pipeline-binding-d4e9188.md) is
  SPEC FAIL, P2 B01, QUALITY not started; rejected source was not integrated.
- **J13**: [A+B selection review](../reviews/P13-selection-72253ed.md),
  `72253ed` / `7bf3f253`, integration `895bb35`; [consumer review](../reviews/P13-consumers-4922a6b.md),
  `4922a6b` / `9f58aa8`, integration `991ca73`; current format stage reconciliation
  `678ae22`. The accepted-P06-engine pilot at `ad605de`/`a5d77f9` covers its actual
  alias/resource/notice cases, not new-family or new-P10 acceptance.

| Skill | Current identity | Owner/evidence and retained current method | Remaining boundary |
|---|---|---|---|
| `browse` | C; was U | P11 A16, J11: actual provider operations and evidence, not a fictional daemon. | Exact prior native observations are not a fresh browser/client run. |
| `catalog` | C; was C | P13 A19, J13: one deterministic generator and metadata/selection-first discovery. | New family descriptions and closure are not installed/native acceptance. |
| `da` | C; was C | P09 A09, J09: seven data methods with accepted checkpoint/result consumption. | Recorded planning/execution cases are not every migration or database outcome. |
| `design-dna` | C; was U | P11 A14/P13 A20, J11: retrieval, profile/asset binding, tokens and shared contract. | Notice/source identity and unknown maturity do not certify rendering or licenses. |
| `design-html` | C; was U | P11 A14, J11: owned static preview and explicit selected-token errors. | A14.5 V1 visual gap remains; legacy example paths are not fresh authority. |
| `design-review` | C; was U | P11 A14/P05, J11: shared dimensions and mandatory evidence before advisory scores. | Missing keyboard/visual observation stays unverified. |
| `design-shotgun` | C; was U | P11 A14, J11: literal variant input and attributable or serial exploration. | Parallel instructions are not actual independent actors or rendered acceptance. |
| `devex-review` | C; was U | P09 A09, J09: retained developer-journey method and N1 safety quantifier correction. | No blanket fresh-clone/CI or external-operation permission follows. |
| `dh` | C; was C | P09 A09, J09: seven operations methods with current evidence-bound results. | A deployment/rollback plan is not production execution. |
| `eval` | C; was U | P13 A19, J13: per-cell good/bad comparison, explicit inputs and partial/unrun outcomes. | No model evaluator, audit writer or automatic ship clearance is invented. |
| `frontend-design-review` | C; was U | P11 A14, J11: canonical dimensions and exact design/profile/P05 obligations. | Mandatory visual gaps cannot become PASS from a populated JSON result. |
| `frontend-design` | C; was U | P11 A14, J11: accepted director/renderer mapping and bound source inputs. | Static V1/framework/native gates remain; source decisions are not a rendered page. |
| `frontend-motion` | C; was U | P11 A14, J11: validated none/CSS/library fragments and explicit output mode. | Named libraries need actual sourced suitability and permission. |
| `frontend-shader` | C; was U | P11 A14, J11: validated no-shader or active-shader/fallback choices. | No GPU dependency or measured performance is implied by metadata. |
| `frontend-style-extract` | C; was U | P11 A14, J11: retained pattern extraction with actual palette argument mapping. | Existing artifact/private-vault reads still require explicit authority. |
| `frontend-typography` | C; was U | P11 A14, J11: validated type decisions with brief/profile/source evidence. | Font source/license fields are not measured readability or blanket usage rights. |
| `full-engineering-pass` | C; was C | P09 A09, J09: original domain methods and accepted composed result boundaries. | Finite mode evidence is not universal domain or host execution. |
| `generate-app` | C; was U | P11 A14, J11: literal supported-stack mapping preserving existing manifests. | Framework TLS/build remains blocked; no replacement stack is inferred. |
| `generate-design` | C; was U | P11 A14/P12 A15, J11: shared design vocabulary and exact sibling-content binding. | Rejected P12 serialized input join is not accepted by this source. |
| `generate-outline` | C; was U | P12 A15, J12: original source inventory, sections, language and advisory slide pacing. | Source preparation is not native artifact or pipeline acceptance. |
| `generate-pdf` | C; was U | P12 A15.4, J12: implemented preparation/print/reader and physical-page checks. | Unknown/null stage is not absent method; required visual/full-format gates remain. |
| `generate-ppt` | C; was U | P12 A15.3, J12: editable slide method, full notes and format-specific inspection. | Selected native PPT verdict is scoped; shared serialization remains blocked. |
| `generate-qa` | C; was U | P12 A15, J12: actual fidelity/format obligations and evidence invalidation after edits. | Scores cannot clear missing render or required policy evidence. |
| `generate-web` | C; was U | P11 A14, J11: exact frontend/pipeline argument mapping and source constraints. | Renderer source acceptance does not resolve A14.5 visual/framework gates. |
| `generate-word` | C; was U | P12 A15.3, J12: standalone three-variant/template/default and editable-content method. | Word page-layout permission remains blocked; no shared-pipeline PASS. |
| `generate-write` | C; was U | P12 A15, J12: full Body/Bullets/tables/citations and actual speaker-note content. | Word/PPT presentation choices cannot truncate the canonical source. |
| `generate-xlsx` | C; was U | P12 A15.4, J12: implemented workbook composition and typed saved-integrity checker. | Live calculation does not clear failed/missing persisted caches or layout. |
| `generate` | C; was U | P12 A15, J12: retained common preparation and standalone choices with explicit gates. | P12 B01 shared join rejected; do not advertise serialized completion. |
| `help` | C; was C | P13 A19, J13: shared literal catalog/selection metadata before selected bodies. | Source declarations are not tools registered or permitted by the host. |
| `investigate` | C; was U | P09 A09, J09: hypothesis-led bounded diagnosis and N1 safety clarification. | A plausible diagnosis is not tested remediation or wider authority. |
| `make-pdf` | C; was U | P12 A15.4, J12: retained conversion entry over actual PDF/browser methods. | A nonempty PDF or page count is not complete rendered/fidelity acceptance. |
| `open-managed-browser` | C; was U | P11 A16, J11: explicitly owned real session launch/check. | No personal browser, cookie or login authority follows from discovery. |
| `perfbench` | C; was U | P09 A09, J09: comparable workload/evidence method and N1 boundary. | No paid benchmark or unmeasured improvement is claimed by this row. |
| `sc` | C; was C | P09 A09/P05, J09: threat/auth/secrets/compliance methods with shared controls. | Optional framework selection cannot remove generic security/required policy. |
| `scrape` | C; was U | P11 A16, J11: actual structured extraction and explicit partial/error outcomes. | No remote source or new network authorization is implied. |
| `setup-browser-cookies` | C; was U | P11 A16, J11: chosen login surface and no-cookie-copy boundary. | Source capability does not establish signed-in state or authorize credentials. |
| `skill-router` | C; was C | P13 A19, J13: literal metadata and at-most-three selected skill bodies; match retained. | Structural guidance is not measured model context or routing behavior. |
| `skillify` | C; was U | P13 A19, J13: literal name/alias checks, owned draft and native existing-path refusal. | A header check is not semantic method validation or activation. |
| `status` | C; was U | P13/P08 read-only seam, J13: original map/cycle/profile observations before optional jobs. | Missing logs are not idle/completed work; providers/native704 remain separate. |
| `swarm` | Separate addition; changed | P04 A22, J04: final joined evidence, original leaves, attributable fan-in and recovery. | Preserve 76 destinations/17 artifacts; no whole-initiative or live-person clearance. |
| `ta` | C; was C | P09 A09, J09: seven architecture methods and actual accepted result contracts. | No universal capacity or deployment result follows from source methods. |
| `tq` | C; was C | P09 A09, J09: seven testing methods with bound evidence and retained failures. | Model/host/product outcomes remain their actual selected scenarios. |
| `uniformity` | C; was U | P13 A19, J13: trusted-source floor and distinct missing/error/stale observations. | Consistency/adoption is not skill usefulness or runtime maturity. |
| `welcome` | C; was C | P06/P13, J13: task-first metadata and actual surface facts without state creation. | A native-format wrapper or source tour is not live onboarding acceptance. |

## Frontend role evidence alongside the preserved role map

The [69-role map](P09-agent-preservation.md) remains intact. These five role blobs
changed after the historical `204ea725` pin and now point to J11's accepted
`a1b3a45` direct-design source. This updates attribution, not the role count,
names, registration or an independent actor claim.

| Existing role | Retained method and current evidence |
|---|---|
| [DesignSystemAuditor](../../../../agents/frontend/DesignSystemAuditor.md) | Canonical dimensions, validator-first and actual mandatory outcomes; J11. |
| [FrontendArchitect](../../../../agents/frontend/FrontendArchitect.md) | Bound design synthesis with director/render separation and retained Apache notice; J11. |
| [MotionDirector](../../../../agents/frontend/MotionDirector.md) | None/CSS/library motion choice and reduced-motion limits; J11. |
| [ShaderEngineer](../../../../agents/frontend/ShaderEngineer.md) | No-shader or evidenced GPU/fallback decision; J11. |
| [TypographyCurator](../../../../agents/frontend/TypographyCurator.md) | Type/profile/source decisions through the shared contract; J11. |

## Separately attributed Swarm addition

| Original and current source | Original recommendation; source state | Responsible package and acceptance | Retained method and output | Change or grounded retention rationale | Worked example and evidence | Remaining boundary |
|---|---|---|---|---|---|---|
| [swarm](../../../../skills/swarm/SKILL.md) | addition; separate from original126 | P04 A22/A21 | Explicit mapped coordination, briefs, scope checks, evidence and serial/manual fallback. | Preserve `275a35447c4ad271e05816ade43ac48f1acec24f` history and reconciled component, not a tenth phase. | Same briefs survive loss of parallel isolation; D, C04. | Component acceptance is not final A22.7/domain/workflow integration. |

The row above retains its historical A+B wording; J04 and the current delta now
record bounded A22.7 acceptance without rewriting the old component verdict.
The [original 76-path record](../../../engineering/audits/2026-09-20-universal-quality/swarm-preservation.md)
and [P04 preservation map](P04-preservation.md) retain the full history, plans, tests,
briefs and review evidence. This +1 row supplements them; it does not reduce that
initiative to the single skill file. No old report or branch is replaced.

## Alias and argument preservation

The [existing alias registry](../../../../config/aliases.yaml) remains unchanged: 46
skill aliases, plus its separate environment aliases. Names are not expired by date.
The metadata helper returns canonical IDs and recorded migration notes, not executable
rewrite rules. The following mappings are read from actual current target methods:

| Retained names | Current method/arguments | Source and evidence limit |
|---|---|---|
| `match` | `skill-router` with supplied intent | Router frontmatter and registry agree; no actual host alias registration is claimed. |
| `context-budgetwatch` | `context-budget --watch`; watcher flags stay skill inputs, not shared helper flags | [Budget watch mode](../../../../skills/context-budget/SKILL.md); C03 source only. |
| `context-snapshot` | `context-save` with existing label/`--label` intent | [Save inputs](../../../../skills/context-save/SKILL.md); an alias does not restore source files. |
| `context-dump` | `context-restore` with optional owned checkpoint path | [Restore inputs](../../../../skills/context-restore/SKILL.md); preserve explicit shared-read authorization. |
| `context-warmup` | `context-warm` with the existing literal path/glob selector arguments | [Warm contract](../../../../skills/context-warm/SKILL.md); no shell expansion is introduced. |
| `role-activate`, `role-deactivate`, `role-rotate`, `role-frame`, `role-deep-dive` | `role <id>`, `role --off`, `role --rotate <id>`, `role --frame <artifact>`, `role --deep-dive [id]`, respectively | [Role actions](../../../../skills/role/SKILL.md); P10 persistence/sensitivity acceptance remains open, not a tested dispatch rewrite. |
| `role-update` | `role-new --update <id>` | [Role update mode](../../../../skills/role-new/SKILL.md); no private role is loaded by discovery. |
| `ta-api-design`, `ta-boundary-review`, `ta-complexity-audit`, `ta-contract-collision`, `ta-dependency-graph`, `ta-quality-attributes`, `ta-scaling-plan` | `ta` plus the exact suffix after `ta-` as the documented sub-capability; retain remaining caller arguments | [TA dispatch rows](../../../../skills/ta/SKILL.md); all seven names exist, no module runtime acceptance implied. |
| `da-analytics-readiness`, `da-data-contract-collision`, `da-migration-plan`, `da-query-pattern-audit`, `da-retention-policy`, `da-schema-design`, `da-sharding-plan` | `da` plus the exact suffix after `da-`; preserve remaining arguments | [DA dispatch rows](../../../../skills/da/SKILL.md); accepted reference knowledge is distinct from migration execution. |
| `sc-audit-path`, `sc-auth-flow`, `sc-compliance-evidence`, `sc-dependency-security`, `sc-incident-runbook`, `sc-secret-management`, `sc-threat-model` | `sc` plus the exact suffix after `sc-`; preserve remaining arguments | [SC dispatch rows](../../../../skills/sc/SKILL.md); no blanket framework/retention obligation inferred. |
| `dh-capacity-headroom`, `dh-cost-projection`, `dh-deployment-plan`, `dh-observability-spec`, `dh-on-call-playbook`, `dh-rollback-strategy`, `dh-sli-slo-spec` | `dh` plus the exact suffix after `dh-`; preserve remaining arguments | [DH dispatch rows](../../../../skills/dh/SKILL.md); no deploy or rollback authority inferred. |
| `tq-chaos-plan`, `tq-contract-test-design`, `tq-coverage-audit`, `tq-flaky-quarantine`, `tq-perf-budget-spec`, `tq-regression-suite`, `tq-test-pyramid-review` | `tq` plus the exact suffix after `tq-`; preserve remaining arguments | [TQ dispatch rows](../../../../skills/tq/SKILL.md); selected scenario execution still requires actual evidence. |

## Selection and provenance disposition

The additive [source selections](../../../../lib/capability-selections.json) keep the
existing core and demo-script definitions unchanged. The demo-script selection keeps the
three accepted role methods, all receiver modes and plan/draft/separate-critique sequence.
The existing [69-role map](P09-agent-preservation.md) remains authoritative content
preservation evidence; no role is relocated, reauthored or newly registered by P13.
Core lifecycle/security/profile/review remain shared, company identity remains an explicit
P07 overlay, and the full bundle/default access remains unchanged.

The [source registry](../../../../install/upstream-sources.yaml),
[provenance guidance](../../../../docs/provenance.md) and
[design-dna attribution](../../../../skills/design-dna/ATTRIBUTION.md) retain original
source names, known release/unknown historical imports and actual
[MIT notice](../../../../skills/design-dna/LICENSES/MIT-next-level-builder.txt) /
[Apache notice](../../../../skills/design-dna/LICENSES/Apache-2.0-anthropic.txt).
Selection resource checks preserve those recorded obligations, not legal sufficiency
or selected-package delivery. No similarity threshold, synonym rewrite, license rewrite,
private export or new upstream content is used.

The earlier missing `config/aliases.yaml` bundle seam was corrected and actually
exercised by the accepted-P06-engine pilot at `ad605de`/`a5d77f9`. That evidence is
not acceptance of the new P10 engine or installed closure for every new family.
The new-P10 B01 linked-init positive remains blocked, with QUALITY not started.
Native Word/Excel/PDF, static V1/TLS, jq/CI and denied record routes remain their
separate gates. Future accepted producer changes require another explicit
map/evidence delta; no WIP or frontmatter hint anticipates their acceptance.

## Optional family disposition

These are additive views, not relocations or changes to original recommendations.
No selection changes on-disk access or the nine phases; resume stays a utility.
Canonical member IDs and exact resource/provenance closure live only in the existing
descriptor. The [worked examples](../../../../skills/catalog/references/selections.md#optional-family-projections)
name source inputs, useful output, negative behavior and execution limits.

| Selection | Retained method / source owner | Current source boundary |
|---|---|---|
| `design-knowledge` | P11 retrieval/tokens/consultation; P13 accurate provenance | Unknown maturity; both actual notices and null historical imports retained. |
| `frontend-design` | P11 design decisions/render/review, existing real browser method | J11 source available; A14.5 V1/TLS/native gates unchanged. |
| `document-content` | P12 outline/full content/QA and repository documentation; P11 design seam | Accepted standalone source; rejected P12 B01 serialization not included. |
| `document-word` | P12 standalone editable Word and WordTechnicalEditor | Core only; required page observation still blocked. |
| `document-ppt` | P12 editable slides/full notes; actual Design DNA retrieval | Depends on design knowledge, not all frontend roles; prior native verdict stays scoped. |
| `document-pdf` | P12 prepare/print/check plus accepted browser source | Core only; implemented method/unknown maturity, remaining visual evidence explicit. |
| `document-xlsx` | P12 workbook/integrity with real P09 cost/capacity methods | Core only; live values cannot clear saved-cache/layout failures. |
| `document-visio` | P12 retained topology/diagram slot | Exact staged proof; no writer or fictitious NetworkArchitect. |
| `customer-communication` | P09 distinct draft/empathy methods; P13 explicit voice eval | No sending/private policy; demo-script is an explicit optional union. |
| `regulatory-review` | P05/P09 scoped legal/framework evidence methods | Optional expertise never makes generic security or required policy optional. |

Source-ready A18 metadata, A19 discovery/examples and A20 provenance work do not
require a fictional native PASS. Conversely, records and identity counts cannot
close original consumer/distribution/model/parent acceptance. Coordinator alone
reconciles the authoritative plan; the new family unit remains subject to SAME486
SPEC then QUALITY.
