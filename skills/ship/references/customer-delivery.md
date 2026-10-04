# Requested customer delivery

This is SHIP's single method owner for customer artifacts, demo handoff, empathy
review and follow-up planning. Load only the part needed by the actual requested
outcome and selected applicable profile. A customer audience, mode, role name,
capability selection or available tool alone does not request these procedures.
Ordinary code/PR delivery does not load them. This method does not send, publish,
schedule a meeting or make a customer commitment.

## Select the outcome and available capability

1. Retain the original requested outcome: an artifact, a demo script, review of
   supplied customer copy, a post-demo plan, or a specifically requested
   engagement/communication draft. Do not turn technical handoff into sales
   expansion or generate another artifact merely because an audience is customer.
2. Verify the selected applicable profile through the same P07/work context used
   by SHIP. Keep its actual voice, brand, compliance and provenance requirements,
   their mandatory/advisory classification and source precedence. Missing required
   policy blocks the affected output; no implicit profile switch or rebind.
3. Discover source candidates with the existing
   [catalog selection method](../../catalog/SKILL.md#select-a-capability-without-changing-installation):

   ```bash
   : "${LINTEL_SOURCE_ROOT:?select the trusted Lintel source}"
   "${python_cmd:-python3}" -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --list-selections
   ```

   Choose only an existing ID matching the requested outcome. For example,
   `customer-communication` contains customer-copy/follow-up views; `demo-script`
   is a separate selection only when narration is wanted. Document production
   uses the selected format family (`document-ppt`, `document-word`, or the
   applicable existing web selection), not all customer roles. Then query:

   ```bash
   : "${LINTEL_SOURCE_ROOT:?select the trusted Lintel source}"
   : "${selection:?select a nonempty applicable capability ID}"
   "${python_cmd:-python3}" -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" \
     --json --selection="$selection"
   ```

   Read only the relevant returned body at its trusted source path. Retain the
   returned dependencies, stage warnings, limitations and unknown maturity.
   Source selection metadata is not permission, profile applicability, native
   registration or live availability; selecting it installs and activates nothing.
4. Inspect the actual host bindings and current authority for the required
   operation. Select an available authorized role/tool for that one outcome, not
   an automatic persona chain. A canonical role file is not a registered actor;
   a source closure is not an installed writer or a review receipt. If a binding
   is unavailable, return a labelled manual/current-context draft or a precise
   blocked handoff only where the task permits it. Self-review cannot satisfy
   required independent review; an unavailable mandatory reviewer stays open.
5. Retain the explicit source inputs, output owner and owned destination. Use
   BUILD's [documentation-fidelity method](../../build/references/documentation-fidelity.md)
   for current claim-to-source coverage, qualifications, migration notes and
   unrun examples. Do not edit a reviewed artifact as a SHIP shortcut. New or
   changed content needs a newly verified context, affected review and read-only QA
   through SHIP's existing content-bound gate before delivery.

No customer request means no customer handoff/follow-up. A delayed customer
deliverable may remain open while an independently ready authorized PR completes;
report the two outcomes separately.

## Format generation and gates

Only when the requested `artifact_kind=customer-deliverable` needs production,
use the applicable `/li:generate-ppt` / `-word` / `-web` method with its actual
writer, template/input preflight and explicit owned output. Reuse a current
reviewed deliverable instead of regenerating it by default.

The existing four gate categories remain:
1. Voice gate (`resolve_pack_field voice.gates_active`; none by default)
2. Brand-conformance (`resolve_pack_field brand.templates`; default-fallback if null)
3. Honest-limitations (AI-disclaimer present?)
4. Provenance (AI-assistance logged?)

A neutral/default template still needs the format owner's explicit applicable
choice and real available source; no personal-home search or required-brand
waiver follows from a null field. All applicable mandatory controls must pass
for customer-shippable. Grounded N/A and advisory findings retain their actual
policy classification; configured advisory scores do not become blocking
acceptance by appearing in this list.

Retained format capabilities, not automatic role dispatch:

| Requested format | Existing method and capability |
|---|---|
| PPT | `/li:generate-ppt`; PPTNarrativeArchitect's 5-beat slide arc when needed, plus the selected voice gate. Output: `<name>.pptx`. Brand comes from `brand.templates` or the explicitly selected applicable default. |
| Word | `/li:generate-word`; WordTechnicalEditor when that review is requested/required. Variants: technical / customer-summary / transparency-note. |
| Web | `/li:generate-web`; WebExperienceCritic when that review is requested/required. Variants: single-file HTML OR Next.js scaffold. |

Every produced format retains the format owner's source fidelity, reopen/render
inspection and QA requirements. A format label or successful handoff to QA is
not verified artifact evidence. Missing mandatory observations block that
deliverable, without granting another format or publication.

For `ship_path=demo`, prepare only the requested artifact or script, pass its
applicable gates, and return it to the operator for distribution through the
approved channel with the existing provenance record. Preparation is not sending.

## Empathy review before an authorized handoff

Only when review of customer-facing demo handout/follow-up copy is requested or
required by the applicable profile, select the actual available authorized review
capability. CustomerEmpathyCheck remains a compatible named view, not a default
spawn. Use the existing Brief Forge handoff only for an actual permitted delegation,
with the selected binding rather than a hardcoded recipient. Keep the complete
brief in an explicit owned location; missing Forge/transport remains a recorded
limitation, not a fabricated evaluation or independent review.

Preserve the original brief fields and purpose:

```yaml
task: Empathy-review the supplied customer-facing demo handout / follow-up comms
context_pointers:
  - <explicit authorized demo comms draft path>
constraints:
  - flag transactional / corporate / dismissive phrasing
  - preserve substance, add humanity
  - retain source facts, consent boundaries and applicable profile controls
acceptance:
  - per-passage empathy verdict + specific rewrite recommendations
  - actual reviewer identity, evidence and limitations; proposed edits are not publication
```

## Follow-up from an agreed plan

Only when post-demo advice is requested, select the actual available authorized
follow-up capability. PostDemoFollowup remains a compatible named view. Read the
sanitized observed demo signal: questions asked, follow-up requests,
decision-maker presence and exact commitments. Separate observation from
inferred interest; neither attendance nor silence establishes buying authority.

Derive timing and channel from the agreed plan and contact preferences, preserving
its source, owner, agreed date/time zone where supplied and dependencies. If there
is no agreed timing, record it as **unagreed** and ask only for the missing
decision when needed; do not invent deadlines, meeting invitations or commitments.
Any requested options remain proposals until agreed. An example in a selected role
is not a customer agreement or a default cadence.

Retain expansion advice (next demo / PoC / workshop) and the next 30-day planning
view when requested. A planning horizon is not a promised delivery date. Answer
the actual technical follow-up first; do not impose commercial expansion on a
technical-only outcome.

```yaml
task: Advise the requested post-demo follow-up — what to send, agreed timing and applicable expansion paths
context_pointers:
  - <authorized demo signal: questions asked, follow-up requests, decision-maker presence>
  - <agreed plan, contact preferences and actual commitments; or explicitly unagreed>
constraints:
  - timing comes from the agreed plan; unresolved timing stays unagreed
  - shape the requested planning horizon and expansion paths, not invented promises
  - use observed facts and preserve authority, consent and profile controls
acceptance:
  - follow-up plan with evidence-backed cadence or an explicit timing question
  - requested expansion paths with rationale, dependencies and open decisions
  - drafts only; no external communication, scheduling or commitment made
```

Return the actual result to SHIP. Any subsequent draft generation, review,
distribution or scheduling has its own output/authority boundary; advice does
not satisfy those operations or make an unperformed handoff complete.

## Compatible capability views

These public names and distinctive purposes remain available for discovery,
subject to the actual requested outcome, profile and host binding above. They
are not a list to load or spawn:

- DemoNarrativeArc — requested demo narrative arc.
- DemoNarratorJunior — requested narration after its actual arc approval.
- CustomerEmpathyCheck — empathy review of the selected customer copy.
- PostDemoFollowup — post-demo cadence/expansion advice from the agreed plan.
- ExecutiveBriefingDrafter / ProposalDrafter / RFPResponseDrafter — requested
  executive briefing, proposal or RFP response.
- EmailCustomerDrafter — requested announcement or customer email draft.
- BlogPostDrafter / LinkedInPostDrafter — requested public-post draft.
- PPTNarrativeArchitect / WordTechnicalEditor / WebExperienceCritic — the
  applicable format/narrative review above.

All normal SHIP review, voice/compliance/provenance, PR, CI/deployment and
publication checks still apply. This reference neither approves an artifact nor
supplies independent review, live tools or external-communication authority.
