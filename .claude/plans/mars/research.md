# MARS research and proposed design

> **Status 2026-09-24:** the operator renamed MMARS to **MARS** (Multi-Model Adversarial
> Review & Screening) and authorized building the canonical files on this session's own
> branch as new files only. See [status.md](status.md) for what is built, piloted and still
> to integrate. Text below is the original 2026-09-22 research/spec, kept for traceability.

**Date:** 2026-09-22
**Status:** Research complete; recommended design DRAFT for deferred coordinator review.
Implementation has not started.
**Owner:** MARS session `58d0e5e4-5ec9-4438-85d2-fbf06fbcaa9e`.
**Coordinator:** Finish work session `88aecc43-40f9-41d4-8947-6c2fb0a55481`.

## Outcome and authority

MARS means multi-model adversarial review and screening. It is a deliberately invoked,
bounded discussion of one problem or artifact, not a parallel implementation framework.
The user requested the capability, research and an implementation plan, but explicitly
ordered BUILD to wait until Finish work finishes its other jobs and coordinates this owner.

This packet is in the session artifact area, not the repository. The already-existing
session branch was renamed to `jokerman-microsoft-mars-development-plan` as required by
the session setup. No additional branch, child session, implementation commit, source
edit, installation or model panel has been created.

The feature is feasible with the current host's declared APIs. This session's `task`
schema exposes explicit per-child model selection and separate task contexts; its
`create_session` schema also exposes model selection and coordinated nested sessions.
The advertised choices include Astra, Opus, Grok, MAI and Gemini families. This is tool
schema evidence, NOT proof that every listed model is entitled, available, actually
routed or appropriate for repository data. No model catalog or preference is to be
hardcoded into Lintel.

## Repository evidence and moving-base warning

The clean local checkout is `28061e434be455ca02f135b73244eaf4f73f3a69`.
Finish work was busy when inspected. Its integration branch was sampled read-only at
`2cea48ec9a725ce2c5dba74d76971ff67d7e022b`. That is not an approved final build base.
Read-only Git object inspection was used; nothing in the coordinator's checkout was
modified. The coordinator's live work includes substantial Universal and Swarm changes.

| Evidence | What it establishes | Design consequence |
|---|---|---|
| Local `skills\define\SKILL.md`, Step 7 | Optional cross-model second opinion already exists, with host-specific Codex/Claude instructions. | Consolidate the optional path rather than invent a parallel review family. |
| Local `skills\review\SKILL.md`, Step 6 | Optional outside voice currently prompts for Codex and silently skips unavailable execution. | Replace this optional hook with capability-gated MARS and explicit requested-run failure reporting. |
| Local `skills\plan-eng-review\SKILL.md`, Optional outside voice | Engineering plan review has another independent challenge entry. | Route it to the same MARS offer/protocol. |
| Local `skills\code-review\SKILL.md` | Large-diff Codex review has distinct existing semantics. | Do not silently remove this required/legacy behavior; MARS is an additive optional offer. |
| ADR-0008 | New mechanisms require behavior evidence, not only prose-presence tests. | Gate, consent, bounded rounds, failure and resume need executable tests plus a separately labeled host pilot. |
| ADR-0026 | Short leaves retain authority; coherent packages share execution/review. | Keep one owner, serial build packages and independent spec then quality review. |
| Integration ADR-0027 | Swarm is an opted-in implementation profile with ownership/isolation/fan-in. | MARS must not set swarm fields, invoke swarm run, create implementation lanes or merge worker branches. |
| Integration ADR-0028 and `lib\client_capabilities.py` | Exact client surfaces and actual permitted bindings are distinct from documentation and installed files. | Reuse `delegate` and `model_control`; add per-run child-model evidence, not another client registry. |
| Integration ADR-0028 and `lib\review_contract.py` | Content-bound review, attributable context and later-rejection precedence already exist. | Reuse snapshots and inspection/evidence paths; panel agreement never supplies release clearance. |
| Integration ADR-0029 and `lib\profile_context.py` | Required policy and profile generation/content are verified and carried unchanged. | No new policy resolver or neutral fallback for a failed required pack. |
| Integration `lib\state.sh`, `lib\cycle-modes.sh`, `lib\workflow.sh` | Named-cycle route, selected work, profile and resume have shared providers. | Read the actual selected route; do not infer a full cycle from mode name or old ledger entries. |
| Integration `bin\li-copilot.py`, `bin\li-catalog.py`, `lib\capability-selections.json` | Adapter generation, dependency closure and discoverability are being centralized. | Extend their released forms; never fork an old installer or hand-edit generated wrappers. |
| L-001, L-002, L-015, L-022, L-025, L-029 | Avoid model catalogs, reuse prior art, coordinate writers, serialize full suites, fix generators, distinguish milestones from completion. | Session-only planning now; coordinator-selected base and real evidence before claiming the feature is done. |

No `docs\risks\` tree was present in the local baseline. The relevant accepted decisions,
provider constraints and failure scenarios in this packet are the identified risk inputs.
This research does not claim private-pack or live enterprise policy validation.

## Public client research

Primary sources were checked on 2026-09-22 by the read-only research task
`068f93cb-3fb8-45d7-b15f-9158ca7857dc`. No client installation, entitlement probe or
model invocation was performed. These are rolling documentation/source observations,
not certification of an installed release.

| Client | Documented primitives | Important limit or substitution risk |
|---|---|---|
| Copilot CLI | Separate custom-agent contexts, restricted tools, per-call/agent models and `/model` availability discovery. | Auto routing and subagent overrides can change the selected model. The reference documents fallback unless a supported `modelPolicy: required` prevents it. Do not invent that field in a tool that lacks it. |
| Copilot VS Code | `runSubagent` model selection, isolated/stateless contexts, tool configuration and sequential/parallel use. | Child cost-tier limits may refuse a selection; ordered model lists can choose the same fallback. Inspect the active harness, policy and model manager. |
| Claude Code | Per-child model aliases/IDs, non-forked independent contexts and scoped tools. | Multiple Claude models are not arbitrary provider-family mixing. Forced subagent configuration, allowed-model substitution and fallback chains can collapse diversity. |
| Codex CLI/local App | Separate threads, explicit child models and read-only custom-agent configuration. | Agent configuration can override a spawn request; parent permission overrides matter. Arbitrary cross-provider children and unavailable-model fallback were not established. |
| Gemini CLI | Custom/built-in subagent model configuration, isolated contexts and parallel calls. | Children cannot recursively delegate; fallback can be automatic. Different Gemini models do not imply native GPT/Claude/Gemini mixing. |
| OpenCode CLI/TUI | Per-agent `provider/model-id`, child contexts, permissions and configured-provider model discovery. | Development source records model/provider metadata, but installed-version behavior and gateway substitution still need live evidence. |
| Cursor | Fresh read-only subagents, explicit model IDs, foreground/background execution. | Admin/plan/legacy settings can substitute a compatible model or Composer. A configured pin is not effective identity proof. |
| Factory Droid | Fresh custom droids, pinned public/BYOK models, scoped tools and parallel use. | Blocked/unconfigured models fall back to the parent; no recursive children. Inherited MCP access needs inspection separately from a read-only tool label. |

Official sources:

- Copilot CLI: [custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli),
  [model policy reference](https://github.com/github/docs/blob/main/content/copilot/reference/copilot-cli-reference/cli-command-reference.md#L1215-L1228),
  [enterprise controls](https://docs.github.com/en/copilot/how-tos/copilot-cli/administer-copilot-cli-for-your-enterprise#model-selection).
- Copilot's [Rubber Duck](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/rubber-duck)
  is relevant precedent: a read-only complementary-model critic with availability checks.
  It is not evidence that an arbitrary panel is available, and Lintel should not duplicate
  or silently start it when the host already supplies it.
- VS Code: [subagents](https://code.visualstudio.com/docs/agents/run/subagents),
  [custom-agent configuration](https://code.visualstudio.com/docs/agent-customization/custom-agents#_custom-agent-file-structure),
  [language-model availability](https://code.visualstudio.com/docs/agent-customization/language-models).
- Claude Code: [child model selection](https://code.claude.com/docs/en/sub-agents#choose-a-model),
  [permissions](https://code.claude.com/docs/en/sub-agents#permission-modes),
  [fallback](https://code.claude.com/docs/en/sub-agents#api-errors-in-subagents).
- Codex: [subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
  [models](https://learn.chatgpt.com/docs/models),
  [workspace boundaries](https://learn.chatgpt.com/docs/enterprise/workspace-model-availability).
- Gemini: [subagent source documentation](https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md#L362-L394),
  [model selection](https://geminicli.com/docs/cli/model/),
  [routing and fallback](https://geminicli.com/docs/cli/model-routing/).
- OpenCode: [agents](https://opencode.ai/docs/agents/),
  [model discovery](https://opencode.ai/docs/cli/#models),
  [development task implementation](https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/tool/task.ts#L156-L218).
- Cursor: [subagents](https://cursor.com/docs/subagents),
  [model configuration/fallback](https://cursor.com/docs/subagents#model-configuration).
- Factory: [subagents](https://docs.factory.ai/harness/subagents).

Nesting depth is deliberately not hardcoded: even the inspected Copilot reference has
contradictory defaults, and Codex's V1/V2 settings differ. MARS does not need nested
reviewers. It uses a root controller with independent children and one bounded challenge.

The offer gate should require separate contexts, distinct currently available child-model
identities, actual permission/data-routing approval, and a means to observe effective
identity or enforce the exact selection. Unknown means no automatic offer. Runtime
substitutions must invalidate the distinct-model claim when identities collapse.
The present App schema proves selection primitives but not those remaining live facts.

## Research on debate value and failure modes

[Du et al., ICML 2024](https://proceedings.mlr.press/v235/du24e.html) motivates independent
candidates followed by mutual critique. It does not establish measured coding-review
benefits for this proposed Lintel feature.

[Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models?](https://arxiv.org/html/2508.17536v2)
distinguishes independent aggregation from debate and identifies subversion of correct
answers by peer influence. Its probabilistic assumptions and persona-heterogeneous
experiments are not proof about arbitrary cross-provider coding panels.

Therefore keep the blind first pass, require evidence/counterexamples, use one challenge
round, preserve dissent and avoid consensus-as-truth claims. Different model families
can diversify perspectives but do not prove statistically independent errors.

## Design alternatives

| Approach | Benefit | Cost or shortcoming | Recommendation |
|---|---|---|---|
| Prompt-only skill with manual panels | Smallest addition; useful discussion instructions. | Cannot reliably test consent, full-route detection, repeated offers, stale input or incomplete panels. | Insufficient for the user's gating requirement. |
| Canonical skill, small data-only gate/report helper, existing host/profile/evidence providers | Portable, bounded, testable; native host owns inference and permissions. | Requires focused integration and a live acceptance boundary. | Recommended. |
| Separate cross-provider API runner or session scheduler | Controls provider selection and execution directly. | Adds credentials, data-routing, billing, installation and lifecycle obligations; duplicates host tooling. | Outside this initiative. |

Extending Swarm with a special review topology is intentionally not proposed: it would
conflate implementation fan-out with a targeted epistemic check.

## Proposed experience

Standalone `/li:mars` (native Copilot `/li-mars`) accepts a scoped problem, plan,
specification, implementation, diff or existing review. It proposes a finite panel,
shows the actual available model identities and round/invocation limits, and uses only
the operator-approved roster. Direct invocation is deliberate intent, not permission
to invent unspecified models or budgets.

A full cycle may offer MARS once at its existing PLAN approval/pre-BUILD checkpoint,
when the plan/spec target is concrete. "Full" means the selected route includes all nine
canonical phases in order after mode, range, skip and SCOPE overrides, not merely that
the mode is called full. A resumed cycle may retain this eligibility only from its
verified original full route. This is a proposed interpretation of the user's wording,
not a requirement to wait until CAPTURE has already finished.

Standalone review/definition/plan-review callers may offer it for their concrete target.
Nested callers inherit the cycle's eligibility and offer decision: a partial cycle
cannot evade the full-run condition by prompting from REVIEW. A decline is remembered
for the current cycle/invocation; no repeated nudges. An explicit new MARS request can
start a new bounded attempt. Auto mode never supplies MARS consent.

Default proposal: two participants, with an operator-selectable roster of two to five,
one independent pass and at most one challenge/rebuttal pass. Two participants suffice
for the smallest authorized run. Distinct models are mandatory; different providers
are useful diversity when available but are not a universal prerequisite. Five names
in the user's example do not mandate five paid calls on every use.

## Discussion protocol

1. Freeze one scoped brief, source/target identity, acceptance references, input digest,
   host bindings, profile reference and the approved roster/limits.
2. Give every participant the same evidence packet and questions. No peer answers or
   the coordinator's preferred conclusion in the first pass. Participants can report
   missing context rather than guess.
3. Collect independently attributable findings with evidence and uncertainty.
4. Share a bounded claim/disagreement matrix only after every first pass is accounted
   for. Ask each participant to challenge evidence and revise or defend claims once.
5. The coordinator adjudicates against source evidence, preserves minority dissent,
   identifies unverified claims and proposes targeted checks or follow-up work.

The output separates agreement, disputed findings, missing evidence, rejected claims,
recommendations and the operator's unresolved decisions. Majority vote and confidence
averaging are not correctness proofs. No participant is permitted to implement fixes,
spawn more participants, trigger another MARS offer, modify shared state or approve SHIP.

Use native bounded subagents where possible; no branch/worktree is needed for read-only
review. A host's nested-session route is optional, must preserve the same boundaries and
requires authorization for any additional worktree/session side effects. Do not fork
the whole parent conversation and describe that as a blind independent first pass.

## Evidence and safety boundaries

The deterministic helper validates data and eligibility; it does not call providers,
launch sessions, grant permissions, mutate model settings or install clients.
Unavailable/unknown capability suppresses proactive offers. Explicit invocation gets
an actionable blocked/unsupported result rather than a single-model impersonation.

Model identity has separate requested and host-reported fields. A tool-request receipt
proves what was requested, not an unobservable backend route; a model's self-description
is not identity evidence. Reports state the evidence level, alias normalization and
any substitution, partial result or missing receipt. A failed participant is not silently
replaced, dropped, or represented as a successful independent reviewer.

Preflight must inspect overriding host configuration and fallback behavior, not only
requested IDs. Use an actual exact-model policy only where the installed host supports
it and the operator authorizes its use; never change global preferences to make a test
pass. A post-dispatch substitution is recorded and can invalidate the multi-model claim.

Scope content, evidence and required profile drift invalidate reuse. Cancellation stops
further dispatch; a timed-out/partial run remains partial. Native host permissions and
enterprise routing govern data transmission. No external CLI/API fallback bypasses them.

MARS remains inspection/advice (`release_clearance: false`). Existing independent
spec/quality/compliance and SHIP controls remain authoritative, including applicable
blocking findings discovered by the panel.

## Readiness and next action

The completed research packet and draft plan have been queued to Finish work without an
immediate interruption. Queued delivery is not acceptance. BUILD requires a message from
that coordinator identifying the released base, owned scope and start authorization after
earlier work. No polling loop, automatic worktree creation, source merge or implementation
should occur while waiting.
