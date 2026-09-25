---
name: inspect
layer: foundation
description: Use to inspect a selected plan or repository through engineering, design and developer-experience lenses. Preserve original work and short-leaf acceptance, report concrete findings, and use shared content-bound evidence without treating scores as clearance.
color: red
tools: Read, Write, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
necessity: RECOMMENDED
gap_if_skipped: "Architecture, interaction and contributor-workflow gaps lack a structured inspection before work proceeds; required review remains outstanding."
---

# Inspect

One inspection workflow with distinct plan and repository targets. It is read-only
on the inspected source. Writing an agreed report/evidence artifact is separate
from permission to repair product code or change a plan. The owning planner or
implementer fixes findings; an independent reviewer never fixes its own findings.

Follow [task-relevant intake](../define/references/intake.md), the
[work-map contract](../spec-kit/references/work-map.md) and the
[shared v2 evidence contract](../review/references/evidence.md). Use actual host
tools and permissions, with no model mandate or inferred agent availability.
`cli_support` describes portability, not observed client acceptance.

## Inputs

```text
/li:inspect [<path>] [--target plan|repo] [--lens engineering|design|devex ...]
  [--map <work.json>] [--scope <area|diff>] [--baseline <ref>]
  [--product-type cli|library|service|sdk|harness]
  [--fresh-clone] [--time-budget <minutes>]
```

- `--target`: default: plan. Never silently switch a missing plan to repository review.
- `--lens`: repeatable; default: engineering. Multiple lenses share the same input
  selection and report, with separate applicability, findings and evidence.
- `<path>` / `--map`: explicit target or original work map. Conflicting selections
  require resolution; missing selection never means the newest design.
- `--scope`: a named area, or `diff` for a repository change. It narrows inspected
  input without discarding required acceptance.
- `--baseline`: an explicit Git ref for comparison. Verify it locally before use.
- `--product-type`: informs developer-experience expectations, not mandatory targets.
- `--fresh-clone`: request a disposable local copy for authorized repository journey
  checks. It does not authorize fetching, installing dependencies or running setup.
- `--time-budget`: positive minutes for the inspection. The repository journey
  retains a 15-minute default when no limit is supplied; report actual elapsed time
  only when measured. A budget is not a timeout mechanism or a completeness claim.

Reject invalid values and unsupported combinations visibly. `--fresh-clone` and
`--scope diff` require the repository target. A path outside the authorized area,
an unresolvable baseline or denied tool blocks the affected action, not a guessed
fallback. An existing approved design needs no repeated intake interview.

## Select the work and evidence

Validate the explicit work map with `bin/li-work-artifacts.py --view context`.
Keep its original spec, plan, tasks, prompt, constitution and package/leaf IDs.
Mapped Spec Kit plans do not need a Lintel approval heading or another task list.
Before consuming policy in an existing cycle, use `workflow_resume` and carry the
verified P07 reference and `required_policy` unchanged. Missing/drifted required
policy remains blocked; never replace it with a neutral label.

Read current instructions, relevant accepted decisions, selected prior reports and
code. Prior reports are leads, not current clearance. Establish the builder,
reviewer, attempt, write boundary and actual separate-context availability before
claiming independence. A read-only inspection needs no new cycle or work map.

### Plan target

Inspect the explicitly selected design/plan and original requirements, leaf
acceptance and linked code. A draft or unmapped plan is valid input for useful
findings; report its draft/unmapped status. Do not approve it by inspecting it,
generate a competing backlog, or edit its tasks from the reviewer context.

Evaluate proposed behavior and proposed verification. A command written in a
plan is not an executed check, a performance estimate is not a measurement, and a
mockup is not evidence that the implemented UI works.

### Repository target

Inspect actual selected source and behavior. With `--scope diff`, include the
explicit baseline plus committed, staged, dirty tracked and untracked changes,
deletions and relevant configuration. A `base...HEAD` view alone omits working
changes. Without `diff`, inspect the selected repository area and its documented
journeys rather than assuming only changed files matter.

Keep source/configuration edits out of the pass. Inspect commands and their side
effects before any execution. Browser or executable checks need real permitted
tools and an authorized target; otherwise record unrun observations and preserve
the manual handoff. A Git copy provides attribution, not a security sandbox.

## Apply the selected lenses

### Engineering lens

Start with scope and reuse, then inspect four dimensions:

- **Architecture:** dependency graph, data flow, ownership, interfaces, scaling and
  security boundaries. Include a diagram where it clarifies the actual design.
- **Code quality:** error handling, visible failures, duplication, complexity and
  under/over-engineering. Prefer existing helpers over parallel interpretations.
- **Tests:** trace each changed behavior to acceptance and a verification procedure.
  Show a coverage map distinguishing unit, integration, end-to-end and model
  evaluation evidence. Mark covered, missing and unobservable cases separately.
- **Performance:** query count, memory, caching, concurrency and slow paths.
  Ground claims in actual measurements or label them estimates/unknown.

For plans, perform a **Granularity hard check** on every leaf, including those
inside packages: target **2-5 minutes** of bounded implementation with enough
context for a cold executor. A larger leaf requires **Decompose now** or
**Accept with concern** under explicit operator authority; do not ask again if
that exact exception was already accepted. Time is a planning estimate, not
measured implementation evidence. Do not fabricate shorter estimates to clear it.

Each work package needs one outcome, one write owner, a compatible edit/approval/
rollback boundary, dependencies and evidence for every unchanged leaf. Review
depth follows aggregate risk, not the size of its smallest leaf. Substantive work
requires spec review followed by separate quality review; missing evidence keeps
the leaf/package open. Ungrouped work retains singleton packages.

Required engineering report content:

- **What already exists:** reusable components and why they fit.
- **Not in scope:** explicit exclusions, deferred requirements and their owners.
- **Failure modes:** realistic failure, visible handling, recovery and test for
  every changed path. Uncovered changed behavior needs a regression-test proposal
  tied to the original leaf, not an untasked shortcut.
- **Distribution:** packaging, installation and CI/CD changes or explicit deferrals.
- **Execution boundaries:** package dependencies, safe ordering, overlap/conflict
  risks and actual attributable isolation before any parallel implementation.
- **Interface metadata:** new skill/agent `cli_support`, applicable `voice`, shared
  schema ownership and required policy controls.

Complexity counts are prompts to inspect simpler alternatives, not automatic
scope-reduction gates or permission to weaken an approved large initiative.

### Design lens

Apply when the selected plan or repository has a rendered/interactive surface.
If no such surface is in scope, record grounded not-applicable, not a successful
visual check. Preserve these six pillars:

1. **Information hierarchy:** order, visual weight and the primary task.
2. **Interaction states:** loading, empty, error, success, partial, hover, focus
   and disabled states.
3. **Edge cases:** long content, zero/large result sets, slow/offline connections,
   stale data, double activation and navigation during an operation.
4. **Subtraction:** unnecessary choices, duplicate elements and avoidable friction.
5. **Trust:** truthful feedback, data sensitivity, predictable recovery and copy.
6. **Accessibility:** contrast, keyboard access, screen-reader semantics, focus
   management and reduced motion.

Scores, when useful, are advisory with a source and rationale; no finding quota
or arithmetic average clears a mandatory control. A plan's specified contrast is
not a measured ratio. A source read is not browser evidence. For a repository UI
use actual tool observations and required validation, or leave those checks open.
An authorized built-UI pass can reuse `/li:frontend-design-review` and its existing
artifact/schema contracts; do not create a second design-spec format.

Optional sketches use `/li:generate-web` mockup mode or `/li:frontend-design`
variants after the caller authorizes generation. They are design exploration,
not implementation acceptance. Apply verified voice and sensitivity requirements
to any customer-facing copy or displayed data.

### Developer-experience lens

**Plan:** inspect time-to-hello-world, Test loop latency, Deploy steps, Local
fidelity, Error message quality and Documentation freshness. Trace proposed
improvements to original tasks and acceptance. Product type, team constraints and
verified policy determine relevant targets; arbitrary elapsed-time targets,
document age or a competitive rank are not universal release requirements.

**Repository:** locate the documented journey in README, CONTRIBUTING and actual
setup/script manifests. Inspect six dimensions: time-to-hello-world, Error
messages, Script ergonomics, Documentation accuracy, Test loop feedback and
Recovery. Include plan-dimension deployment/fidelity concerns when relevant.
Time actual stages only; distinguish measured, estimated and unknown values.
Missing baseline means no comparison, not zero regressions.

Execution requires a specifically authorized disposable target, with verified
synthetic HOME, USERPROFILE, application-data, XDG, temp, profile and audit paths
for parent and child processes. A fresh clone is not permission to execute its
scripts, access credentials, reach live services or alter global configuration.
Inspect each command first and retain its actual output.

Trigger common missing-dependency/version/configuration failures only in that
owned fixture. Recovery perturbations require `--fresh-clone` and recorded
original state: do not fall back to in-place mutation or delete the caller's
dependencies/lockfiles. If setup hangs or reaches the time budget, use the actual
process handle and timeout, report what stopped or remains running and label
remaining stages unrun. A first-N test subset cannot establish full-suite success
or duration. Never invent onboarding measurements from source inspection.

For mapped developer-experience or engineering-module work, use the
[shared original-work procedure](../full-engineering-pass/references/domain-handoff.md#module-caller-procedure)
for original map/package/leaf admission and caller-owned request, start, result and
checkpoint evidence. Preserve the verified profile, external P05 preparation,
immutable controls, actual QA and independently corroborated review. A bare score
is not a domain result or recorded decision. Standalone/unmapped inspection keeps
the non-clearing snapshot/inspect route below; it does not manufacture a domain map.

## Report and reconcile

Use a selected report path or return the report in the conversation when writes
are not authorized. Keep external plan structure intact; an authorized native
plan may link or append the report. No last-heading convention is a gate.

```markdown
## Inspection report

Target: <plan|repo and exact selected paths/base>
Work: <original map, package and leaf IDs, or explicitly unmapped>
Actor: <actual reviewer/context; independent or self-review>
Evidence: <prepared context/QA references, or non-clearing inspection>

| Lens | Applicability and source | Runs | Status | Findings |
|---|---|---|---|---|
| <selected lens> | <why applicable/not applicable> | <actual> | <actual> | <counts> |

| ID | Severity | Requirement / leaf | File:line or observation | Finding and remedy |
|---|---|---|---|---|

Unresolved decisions: <only material missing decisions>
Verification: <exact commands, results, counts and unrun obligations>
Verdict: <pass|fail|unverified|error for this scope, not a release grant>
Next action: <owning planner/implementer, review or precise blocker>
```

P1 findings are critical correctness/authority risks, P2 are material acceptance
or behavior gaps, and P3 are nonblocking improvements. Ground severity in impact
and obligations, not a score threshold. Report zero findings explicitly and do
not mistake missing coverage for a clean review.

The owner reconciles findings in the original artifacts. Ask only unresolved
material choices; do not ask once per finding or reopen existing authorization.
Rerun affected checks after fixes. ANALYZE remains the separate cross-artifact
consistency workflow; inspection quality does not replace it or BUILD/REVIEW.

### Persist via first-party

For mapped acceptance, first use the shared `prepare` procedure with exact
selection, original package/leaf coverage, verified profile/required policy and
immutable `qa_requirements`. Required test/browser/contrast/policy observations
stay typed and mandatory as declared. An inspection score cannot downgrade them.

Bind the requested target and required lenses through that existing contract:
select the actual plan or repository inputs, and declare target-specific review
check IDs in `required_controls`, such as `inspect-plan-engineering` or
`inspect-repo-devex`. Derive them from the accepted request and original
requirements before observing results; every selected leaf covers every required
ID. Record applicability and source in the existing control fields. Required
design and developer-experience judgments each retain their own check, rather than
sharing a generic score. These are ordinary review-only `check` controls, not
substitutes for typed QA. A different target/lens obligation needs a newly prepared
context; a narrower prior inspection cannot clear it. Do not add a lens schema,
rewrite prior records or alter the work-map version.

Obtain actual review and write a v2 decision with `skill: inspect`. If several
lenses apply to this same context, the decision covers all required lens findings;
do not let a final lens-only pass mask an earlier required failure. Record each
observed result, including fail/unverified/error. A separately attributable
reviewer and caller-supplied host/human corroboration are required where declared.
Different actor strings, self-review or a missing receipt do not prove independence.

```bash
review_source="${LINTEL_SOURCE_ROOT:?select trusted source}"
python="${LINTEL_PYTHON:-python3}"
"$python" "$review_source/bin/li-review-evidence.py" validate \
  --record "${review_record:?set actual v2 decision}" || exit $?
bash "$review_source/bin/li-review-log" --file "$review_record" || exit $?
bash "$review_source/bin/li-review-read" --skill inspect \
  --expected "${review_context:?set prepared context}" \
  --corroboration "${corroboration:?set actual independent receipt}" --gate-json
```

The writer/read sequence consumes the latest applicable decision, not the latest
passing one. A later rejection, malformed relevant decision, changed selected
content, new attempt or profile drift prevents reuse of an older pass. Direct
`verify` alone does not establish latest-log precedence. Use the same context for
actual QA and any separately authorized SHIP operation, with explicit
`--skill inspect`; a shared helper's older default is not this selection.

For draft/unmapped or advisory-only inspection use shared `snapshot` then
`inspect` with actual controls and required policy. Retain
`release_clearance: false`; its envelope has its own format, not a new v2 review
schema. No duplicate map is needed. Missing Git/snapshot capability permits a
clearly unbound prose review, never a fabricated content-bound result.

## Failure and continuation

Missing selection, denied tools, missing policy, incomplete evidence or failed
persistence remain explicit blockers. Continue independent read-only lenses
when valid. An unavailable independent reviewer leaves a durable manual handoff;
do not report required review complete. Changed source or decisions require fresh
affected review/QA, not an edited historical verdict.

When no plan exists, use DEFINE for an authorized design request, or select
`--target repo` explicitly for repository inspection. Neither fallback is silent.
PLAN owns planning corrections; BUILD owns implementation corrections; REVIEW
still assesses the reconciled candidate before separate delivery authorization.

## Cycle-position footer

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/cycle-footer.sh"
render_cycle_footer
```
