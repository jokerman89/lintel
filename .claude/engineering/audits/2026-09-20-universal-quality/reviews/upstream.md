# Selected upstream semantic comparison

Audit date: 2026-09-20. Lintel baseline: 28061e4. Scope: selected implementation patterns in gstack, Superpowers, current GSD Core, and ECC. This is a read-only design comparison, not an exhaustive upstream audit, a benchmark, or evidence of historical regression.

The recommendation is to keep Lintel's neutral orchestration, repository authority, existing task IDs, pack boundaries and ADR-0026 hybrid execution. Strengthen the evidence carried between its workflows. Borrow narrow contracts and examples from upstream; do not absorb four complete harnesses.

## Revisions and method

| Source | Inspected revision | Provenance |
| --- | --- | --- |
| gstack | a6b3a57512ca6d5c6aa5b68f74f736195021f96e | [Pinned tree](https://github.com/garrytan/gstack/tree/a6b3a57512ca6d5c6aa5b68f74f736195021f96e) |
| Superpowers | 5bf4e78011075bcfc0dc295f0724994cd123ee71 | [Pinned tree](https://github.com/obra/superpowers/tree/5bf4e78011075bcfc0dc295f0724994cd123ee71) |
| Archived GSD checkout | bdcaab2c752d9a33a1a1ca9acf3a3c81fb991815 | Its README.md:3–12 says development moved to open-gsd/gsd-core; it is not the current implementation comparison target. |
| Current GSD Core, cloned through get-shit-done-redux redirect | 88b5775dc8e32ffe8d50fe4db01677650e219ed2 | [Pinned tree](https://github.com/open-gsd/gsd-core/tree/88b5775dc8e32ffe8d50fe4db01677650e219ed2), local branch next |
| ECC | 934195f955cf0da847d59fcd6f68856bce112d8b | [Pinned tree](https://github.com/affaan-m/ECC/tree/934195f955cf0da847d59fcd6f68856bce112d8b) |

All five revisions were verified from the local checkout refs. The sources reside under ignored .claude/runtime/upstream-* directories. Sources and their license files were read; no upstream program, installer, test, hook or dependency was executed. Source links below are revision-pinned and were assessed from these local source contents on the audit date.

Comparison criteria: what decision the instruction enables, what input it requires, how it handles uncertainty and failure, what proves the result, and whether the mechanism survives a different host. File size and string similarity are not quality measures. “Gap” means a difference observed at the pinned current revisions; it does not mean Lintel once imported and then lost that behavior. Establish an actual import baseline before making that historical claim.

## UP-01 — Review needs concrete defect mechanisms and a finding verification gate

**Keep:** Lintel separates review from repair. CodeReviewer explicitly reports without editing (agents/engineering/CodeReviewer.md:37–39), uses severity, confidence and citations (:65), and starts with the changed code plus necessary context (:31). These are sound boundaries.

**Borrow:** gstack's checklist teaches actual failure mechanisms, including atomic state transitions and tracing a new enum through every consumer, rather than only naming “correctness” or “security.” Its pre-emit gate requires the motivating code lines before promoting a finding. See [checklist.md:40–68](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/review/checklist.md#L40) and [review/SKILL.md:720](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/review/SKILL.md#L720). Lintel's central checklist is largely category-level (agents/engineering/CodeReviewer.md:58–64); some output examples elevate harmless duplication or an unnamed constant without showing a real effect (:78–82).

**Adapt:** create a compact shared defect library with triggering conditions, a counterexample, a focused verification action and a false-positive suppression rationale. Load only the relevant domain. Use specialist roles when their reasoning differs, not merely to repeat the same checklist. The API and data-migration upstream specialists illustrate bounded domain questions, but their heuristics still require project-specific interpretation.

**Avoid:** importing gstack's automatic review fixes, “skip all specialists below 50 lines,” silently skipped failed red-team review, or additive numerical quality score as a release gate. These are visible in [review-army.md:42–62, 118–157, 226](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/review/sections/review-army.md#L42). A two-line authorization defect can deserve independent review, and missing required review is unknown rather than clean.

**Acceptance:** seed real defects plus harmless lookalikes; require correct trigger, impact, source location and uncertainty. Confirm reviewers do not mutate source and a missing required specialist cannot produce PASS.

## UP-02 — Browser QA is a capability with observable evidence, not another test-runner label

Lintel's /qa currently detects and repairs test-suite failures (skills/qa/SKILL.md:13, :35–45). Its report contains test counts and failure locations (:47–68). This is useful, but does not demonstrate a rendered page or user journey. The agent audit separately identifies false-green visual verdict risks in DesignSystemAuditor and WebExperienceCritic.

gstack's selected QA workflow captures page screenshots, console errors, interaction results and snapshot differences; interactive defects carry before/action/after evidence and reproduction steps. Its report binds a run to URL, branch, commit and tested scope. See [qa-patterns.md:40–47, 135–172](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/qa/sections/qa-patterns.md#L40) and [QA report template:3–16, 54–100](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/qa/templates/qa-report-template.md#L3).

The capability is substantive: browse/src/browser-manager.ts imports Playwright and launches Chromium, while read-commands.ts implements an ARIA snapshot operation. See [browser-manager.ts:18, 528](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/browse/src/browser-manager.ts#L528) and [read-commands.ts:376](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/browse/src/read-commands.ts#L376). However, the selected current QA recipes invoke Aside. The existence of the browse driver does not prove those recipes invoke it or that Lintel has any browser provider installed.

**Borrow:** an optional web-QA bundle with a provider contract: discover available browser, identify the actual target/build, scope permitted interactions, render and inspect, record evidence, distinguish pass/fail/unknown/not-applicable, and retain explicit untested coverage. Resolve the host's real browser API before selecting an implementation.

**Avoid:** making a browser daemon, persistent user profile, cookie import, anti-detection behavior, automatic installation or one browser vendor part of the neutral core. Do not copy scoring averages that hide a failed required criterion. Preserve Lintel's suite-repair mode as a separate operation.

**Acceptance:** a deliberately broken interactive journey, console-only failure, narrow viewport issue and unavailable browser must yield reproducible evidence or explicit unknown; none may receive a visual PASS from source inspection alone.

## UP-03 — Preserve premise testing; make startup and presentation styles optional

Lintel already retains much of the substantive office-hours behavior: demand/status-quo questions, contested premises, real alternatives and role lenses (skills/define/SKILL.md:138–172, :187–216). Its feature fast path avoids repeating the full diagnostic (:92–99). This is retained capability, not a reason to restore a larger upstream prompt.

gstack adds useful examples of distinguishing observed behavior from hypothetical demand, naming a hidden assumption, and stating what evidence would change the recommendation. It separately offers a builder mode aimed at concrete next build steps. See [startup diagnostic:37–42, 81–94](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/office-hours/sections/phase-2a-startup-diagnostic.md#L37) and [builder brainstorm:23–39](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/office-hours/sections/phase-2b-builder-brainstorm.md#L23).

**Borrow:** concise worked examples of an unsupported premise, a testable counterclaim and the smallest experiment that resolves it. Record evidence, unknowns and the decision, rather than treating user agreement as factual proof.

**Avoid:** importing “push until uncomfortable,” forced enthusiasm, startup revenue assumptions, fixed question counts, or repeated confirmation after existing authorization already settles a choice. Lintel still repeats startup/founder framing in plan-ceo-review (skills/plan-ceo-review/SKILL.md:39–45). Put those lenses in an optional product-discovery pack; core discovery should equally handle maintenance, internal tools, research, accessibility and public-service work.

**Acceptance:** the same core workflow should produce a useful decision for a startup idea, an existing-product feature and a bounded infrastructure change without requiring a customer/payer fiction.

## UP-04 — ADR-0026 already captures the right task-versus-step distinction

Current Superpowers defines a task as an independently testable deliverable worth a fresh review gate; each step inside it remains a 2–5 minute action. It folds setup and documentation into their owning deliverable and carries global constraints and exact consumed/produced interface signatures. See [writing-plans/SKILL.md:36–52, 69–108](https://github.com/obra/superpowers/blob/5bf4e78011075bcfc0dc295f0724994cd123ee71/skills/writing-plans/SKILL.md#L36).

Lintel already preserves leaf IDs and acceptance evidence while grouping leaves into bounded packages (skills/plan/SKILL.md:114–134, :314; skills/build/SKILL.md:109–153). Retain this accepted hybrid. The comparison supports it; it does not support returning to a new context and review for every checkbox.

**Borrow:** require explicit inter-package interface contracts where they matter and a short “review focus” list for uncovered input classes. Attach these to existing canonical plan/work-map artifacts. Do not create a second backlog or paste a full implementation into every plan by default.

**Avoid:** fixed model selections, a mandatory full test suite after every minor task, or a fresh approval ceremony when scope and execution are already authorized. The upstream handoff and prompt templates contain those prescriptions; Lintel's host-aware package configuration is more suitable for Universal use (skills/build/SKILL.md:127–130).

**Acceptance:** a cold worker implements a multi-leaf package from its brief without losing a requirement or inventing an interface, while every original leaf retains its ID and evidence.

## UP-05 — Make review packets and repair rounds explicit, with durable recovery

Superpowers' task reviewer receives the brief, global constraints, implementation report, base/head references and a review diff. It treats implementation claims as unverified, allows focused call-site inspection for a named risk, and returns separate spec and quality judgments. Its repair review verifies each prior finding plus new breakage in the fix. See [task-reviewer-prompt.md:21–90](https://github.com/obra/superpowers/blob/5bf4e78011075bcfc0dc295f0724994cd123ee71/skills/subagent-driven-development/task-reviewer-prompt.md#L21) and [re-review-prompt.md:55–100](https://github.com/obra/superpowers/blob/5bf4e78011075bcfc0dc295f0724994cd123ee71/skills/subagent-driven-development/re-review-prompt.md#L55).

This is partly executable: [review-package:22–28](https://github.com/obra/superpowers/blob/5bf4e78011075bcfc0dc295f0724994cd123ee71/skills/subagent-driven-development/scripts/review-package#L22) checks valid references, ancestry and a nonempty range. Lintel already records start_ref, acceptance evidence and review mode (skills/build/SKILL.md:253–260), requires an attributable package diff (:114–120), and keeps substantive work open when independent review is unavailable (:380–382).

**Borrow:** one compact packet schema and per-finding repair verdicts, mapping every observation to original task IDs. Support both commit ranges and an explicitly owned uncommitted patch; a commit-only packet must not silently omit working-tree changes. Preserve the independent final integration review and don't let a scoped repair pass silently waive a serious newly discovered risk.

**Avoid:** rigid “diff only” blindness; automatic deletion of all evidence after completion; or the upstream inline executor's claim that passing tests make a second review of every final fix unnecessary. Its current executing-plans workflow prescribes that shortcut and workspace deletion ([executing-plans/SKILL.md:277–302](https://github.com/obra/superpowers/blob/5bf4e78011075bcfc0dc295f0724994cd123ee71/skills/executing-plans/SKILL.md#L277)). Lintel's durable committed handoff and acceptance evidence are useful differentiation.

**Acceptance:** interrupt after a multi-commit package, remove runtime state, recover from committed artifacts, and verify the correct complete change. A wrong branch, empty packet or unresolved finding must keep the package open.

## UP-06 — Bind verification reuse to content and environment, not elapsed minutes

Superpowers clearly distinguishes evidence for “build,” “bug fixed,” “tests pass” and “requirements met” ([verification-before-completion/SKILL.md:24–48](https://github.com/obra/superpowers/blob/5bf4e78011075bcfc0dc295f0724994cd123ee71/skills/verification-before-completion/SKILL.md#L24)). Its literal same-message rerun rule (:20) is unnecessarily expensive for evidence already tied to unchanged inputs.

gstack provides a better reuse primitive: command hash, child exit, log path and working-tree fingerprint. Its implementation checks that content did not change during execution, then treats missing or malformed fingerprints and changed commands as stale. See [bin/gstack-evidence:20–28, 393–403, 474–508](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/bin/gstack-evidence#L393). Its ship workflow consumes this ledger instead of repeating unchanged runs ([ship/sections/tests.md:195–218](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/ship/sections/tests.md#L195)).

Lintel's package log already has source and evidence anchors, but role shortcuts still use “within 10 minutes” or “within 24h with no new commits” (agents/engineering/TestRunner.md:49; agents/engineering/CodeReviewer.md:51). Those can miss an uncommitted change.

**Borrow and improve:** a common evidence receipt with content/patch identity, command and selected test scope, dependency/environment identity, exit/result, log or artifact location, verifier and limitations. Allow reuse only when those inputs remain applicable. A source fingerprint alone cannot validate changing external services or vulnerability feeds.

**Acceptance:** unchanged content after commit may reuse evidence; an untracked source file, changed test command, changed dependency, unavailable log or edited file during the run invalidates reuse. Record skipped checks honestly without automatic repeated full-suite runs.

## UP-07 — Test skill behavior with adversarial scenarios, not only document shape

Superpowers explicitly runs a task without a skill, captures the observed failure, adds the skill, and repeats pressure scenarios. It distinguishes acting under realistic constraints from reciting rules. See [testing-skills-with-subagents.md:30–55, 96–150](https://github.com/obra/superpowers/blob/5bf4e78011075bcfc0dc295f0724994cd123ee71/skills/writing-skills/testing-skills-with-subagents.md#L30). gstack's ship instructions also map changed prompt sources to relevant eval suites ([ship/sections/tests.md:332–368](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/ship/sections/tests.md#L332)).

Lintel already accepted the direction, explicitly staged, in .claude/decisions/0021-eval-harness.md:6–21. This is not an undisclosed implementation regression or evidence that behavior evals already exist. Frontmatter/shape tests remain useful for their actual purpose.

**Borrow:** promote a small risk-ranked evaluation slice before rewriting many skills or retiring roles. Start from this audit's failures: stale evidence, false visual PASS, lost original task IDs, wrong authority, missing independent review and unavailable host capability. Compare old and proposed versions with positive and negative cases; use deterministic evidence where possible and blinded independent grading for judgment tasks.

**Avoid:** evaluating obedience to a particular phrase as quality, or importing examples that require deleting good work solely because it was written before a test. Those upstream examples optimize a rigid doctrine, not necessarily user outcomes. Don't label one green scenario “bulletproof.”

**Acceptance:** publish per-scenario result, host/model configuration, cost/latency, authority handling and task outcome. A shorter prompt or fewer roles is an improvement only if decision quality survives.

## UP-08 — Extend artifact reconciliation without adding another state authority

Current GSD's resume workflow distinguishes incomplete initialization, missing state, interrupted agents, structured handoff, incomplete plan and external jobs awaiting reconciliation. It compares recorded uncommitted files to Git state. A completed-unverified job requires artifact verification before completion, and an existing external-job manifest excludes fresh dispatch. See [resume-project.md:30–35, 107–116, 177–198](https://github.com/open-gsd/gsd-core/blob/88b5775dc8e32ffe8d50fe4db01677650e219ed2/gsd-core/workflows/resume-project.md#L30) and [planning-artifacts.md:227–262](https://github.com/open-gsd/gsd-core/blob/88b5775dc8e32ffe8d50fe4db01677650e219ed2/docs/reference/planning-artifacts.md#L227).

The artifact contract also distinguishes source presence from behavior verification ([planning-artifacts.md:203–209](https://github.com/open-gsd/gsd-core/blob/88b5775dc8e32ffe8d50fe4db01677650e219ed2/docs/reference/planning-artifacts.md#L203)). Implemented state consistency rules compare canonical status vocabulary and roadmap completion rather than maintain another token list ([state-consistency.cts:233–258](https://github.com/open-gsd/gsd-core/blob/88b5775dc8e32ffe8d50fe4db01677650e219ed2/src/health-diagnostic-rules/state-consistency.cts#L233)). Its small state.json publisher derives values from existing owners ([state-contract.cts:2–42, 72–118](https://github.com/open-gsd/gsd-core/blob/88b5775dc8e32ffe8d50fe4db01677650e219ed2/src/state-contract.cts#L2)).

**Keep:** Lintel already prioritizes an explicitly selected committed work map over local runtime hints, preserves Spec Kit's task authority, validates the map, and checks code/evidence before reconstructing runtime state (skills/resume/SKILL.md:39–49, :108–127). That is a stronger fit than introducing a competing .planning tree.

**Borrow:** typed reconciliation outcomes and validators for missing artifact, wrong revision, stale evidence, awaiting external result and verified completion. If a future UI needs a compact state view, derive it from the existing authority. Never promote a checkbox, process completion or a file's mere presence into behavioral verification.

**Avoid:** global fixed context-window sizes or assertions that all subagents have the same isolation behavior; the selected GSD context explanation contains those assumptions. Do not add async infrastructure before an actual adapter needs it. Treat manifest commands as data and preserve existing authorization boundaries.

**Acceptance:** cold clone, missing runtime state, stale handoff, partially initialized initiative and completed-unverified external job fixtures all resolve deterministically without repeating verified work or creating a second task list.

## UP-09 — Borrow ECC's adapter contract discipline, not its dated capability verdicts

ECC separates loader-valid hook configuration from stable metadata and fingerprints so a reorder cannot silently attach the wrong ID. It documents verification of the two files together ([hooks/README.md:19–24](https://github.com/affaan-m/ECC/blob/934195f955cf0da847d59fcd6f68856bce112d8b/hooks/README.md#L19)). Its input reader bounds bytes, preserves UTF-8 decoding and marks early close/errors as incomplete ([hook-input.js:27–61](https://github.com/affaan-m/ECC/blob/934195f955cf0da847d59fcd6f68856bce112d8b/scripts/hooks/hook-input.js#L27)). Its adapter records require supported assets, unsupported surfaces, verification commands, owner, source docs and last-verified date, and generate documentation from those records ([harness-adapter-compliance.js:9–28, 386–473](https://github.com/affaan-m/ECC/blob/934195f955cf0da847d59fcd6f68856bce112d8b/scripts/lib/harness-adapter-compliance.js#L9)).

Lintel already generates its CLI table from one source, but the record shape is a broad tier plus a few booleans (lib/cli-tiers.yaml:1–17), and Codex CLI/App share one row (:27–33). The coordinator's independently verified host matrix should determine actual supported surfaces.

**Borrow:** per-surface adapter records, fixture-based event/schema conformance, install ownership, registration evidence, explicit warning-versus-blocking behavior, and unknown when an event cannot be verified. Keep policy logic shared; host adapters translate input and output contracts. Preserve user settings and make optional automation inspectable.

**Avoid:** accepting ECC as the authority for current clients. Its Codex registry row is dated 2026-05-12 and labels the adapter instruction-backed, while its pinned codex-hooks.json carries a specific SessionStart registration. That is evidence to verify each surface, not proof of broad host parity or broad hook absence. Do not copy ECC's full rule/skill inventory or auto-formatting behavior into Lintel core.

**Acceptance:** supported event fixtures dispatch once with the correct normalized fields; unsupported or malformed inputs cannot silently report a protected action as enforced. Discovery, registration and live enforcement must be reported separately.

## UP-10 — De-heritage and provenance are separate decisions

Accepted ADR-0011 removes broken upstream couplings and reinvents inherited behavior without losing capability (.claude/decisions/0011-gstack-de-heritage.md:18–36). That remains a useful architectural decision. It is not a method for deciding notice obligations.

The archived UPSTREAM-SIMILARITY.md explicitly calls itself an unbuilt placeholder (:3, :66), proposes a cosine threshold (:27–43), and even suggests changing vocabulary/ordering to fall below it (:53–61). Do not revive this as a quality or licensing release gate. The document itself acknowledges license questions are orthogonal (:49).

Current install/upstream-sources.yaml is a declaration-only reference list (:1–6), with a “last_full_review” from May (:26), old project descriptions and the redirected GSD URL (:32–40). It also claims exclusively operator-authored content (:5), while the explicit design-dna attribution records consumed and modified third-party material (skills/design-dna/ATTRIBUTION.md:3–24, :28–43). These statements need reconciliation as provenance maintenance; this audit does not conclude infringement or reconstruct historical copying.

The inspected upstream top-level licenses are MIT and retain a notice condition for copies or substantial portions. See pinned licenses for [gstack](https://github.com/garrytan/gstack/blob/a6b3a57512ca6d5c6aa5b68f74f736195021f96e/LICENSE#L12), [Superpowers](https://github.com/obra/superpowers/blob/5bf4e78011075bcfc0dc295f0724994cd123ee71/LICENSE#L12), [GSD Core](https://github.com/open-gsd/gsd-core/blob/88b5775dc8e32ffe8d50fe4db01677650e219ed2/LICENSE#L12), and [ECC](https://github.com/affaan-m/ECC/blob/934195f955cf0da847d59fcd6f68856bce112d8b/LICENSE#L12). A top-level license does not replace a component-level provenance review.

**Recommendation:** keep the registry reference-only unless an explicit import is approved. Record component, origin revision/path, copied/adapted/inspired status, modifications, license/notice location and verification date. Use design-dna's scoped attribution as the pattern. If implementing a borrowed mechanism, preserve required notices where applicable regardless of rewritten wording. Obtain qualified review for an unresolved rights question.

**Acceptance:** every distributed third-party component resolves to its source and notices; current descriptions distinguish author-written integration from adapted material. Similarity scores cannot waive a notice or block a sound independently implemented behavior.

## Lean product shape

| Placement | Retain or add | Avoid |
| --- | --- | --- |
| Neutral core | Authority and existing-artifact resolution; bounded plan/build/review/recovery; original leaf IDs; common result and evidence contracts; actual capability discovery | Vendor-specific tool names and model identities as workflow truth; mandatory business persona; duplicate state stores |
| Engineering bundle | On-demand defect checklists, API/data/migration reasoning, focused QA and review packet helpers | Always dispatching the whole specialist catalog; fixed line-count risk thresholds |
| Web/design bundle | Provider-neutral browser QA, rendered visual/accessibility evidence, versioned design profiles | Bundling a complete browser daemon or making profile/session ownership implicit |
| Product/discovery bundle | Demand tests, experiment design, builder exploration, optional narrative roles | Requiring startup economics or forced questioning for routine engineering |
| Host adapters | Tested discovery/install/event/output translation per CLI or desktop surface | “Full tier” as a substitute for evidence; duplicating shared policy in each adapter |
| Maintainer evaluation bundle | Small behavioral regression set, change-to-eval mapping, provenance checks | Copying upstream score formulas, unverified benchmark claims or entire catalogs |

Execution order: first standardize result/evidence and host capability contracts; then build a small behavioral evaluation slice; then improve review/recovery and rendered QA against those tests; finally merge or move roles while proving that the retained capability still works. This extends ADR-0026 and the accepted staged ADR-0021 direction. It does not authorize implementation or replace the coordinator's final action plan.

## Evidence limits

- Selected substantive files and implementation sections were inspected. This is not full coverage of any upstream repository and does not rank whole projects.
- Some large inventory/read batches exceeded output limits. Conclusions use the cited sections subsequently read in bounded form; no claim is made that truncated unrelated material was reviewed.
- No upstream tests, installers, hooks, browser drivers or agent workflows ran. Code presence and documented contracts are not proof of successful execution in the user's environment.
- No import baseline was reconstructed. “Borrow,” “keep” and “gap” are current semantic comparisons, not claims of lost historical behavior.
- Exact client capability facts belong to the coordinator's official-source/live-capability assessment. Upstream host labels and hardcoded model assumptions were treated as claims to verify.
- No product fixes, installs, external messages, private-profile inspection or Git mutation occurred. The only tracked output of this comparison is this report.


## Preservation requirement

Retain valuable functionality, knowledge and use cases while fixing, optimizing and enriching their implementation. Merge means shared ownership with specialist depth and compatible entry points or aliases preserved. An optional bundle remains discoverable, maintained and supported; it is not a route to disappearance. Staged work requires an owner, a completion path and acceptance evidence. Retire only after proving there is no unique value or verifying a complete replacement, including uncommon workflows. None of these proposals authorizes deleting source features.
