---
name: codex
layer: foundation
description: Use for an explicitly authorized Codex outside opinion on a diff, plan, code or hypothesis, retaining actual actor and content-bound review evidence.
color: purple
tools: Bash, Read
voice: internal
cli_support: [claude-code, codex, copilot, cursor, gemini, opencode, droid]
---

# Outside opinion with Codex

Preserve the useful second-opinion method: a separate context challenges a scoped diff,
plan or hypothesis and reports agreement, disagreement and new findings. Any host with
an authorized execution or external handoff path can coordinate it; it is not Claude-only.
The name retains the Codex route, not a requirement to change the current session's model.

## When to use

Use for a consequential diff, contested root cause or design decision that benefits from
separate reasoning. For a trivial task, avoid unnecessary external cost. If two rounds
produce unresolved disagreement on the same content, retain the disagreement and escalate
to a human decision rather than repeating the same framing.

## Inputs

- Target: `--diff`, `--plan <file>`, `--code <file>` or `--hypothesis <text>`.
- Optional review style: strict defect-finding or exploratory alternatives.
- Optional budget: an operator constraint, not an invented token-limit CLI flag.
- For mapped delivery: the original work map, package/leaf IDs, acceptance and effective
  profile reference. A genuine ad-hoc inspection does not require a new plan or backlog.

These are workflow inputs, not a claim that Codex accepts identically named flags.

## Procedure

1. **Establish authority.** A subprocess can transmit code and spend credits. Verify the
   requested client, destination, scope and allowed data before any invocation. Do not
   install a client, read credentials or silently substitute a paid provider.
2. **Inspect the real API.** When authorized, inspect the installed `codex --help` and
   `codex exec --help`, exact version, permission/sandbox settings and supported output
   options. Do not use guessed `--prompt-file`, `--output json`, `--quiet` or model flags.
   Native host delegation is an alternative only if it supplies the requested separate
   context and the operator's selection permits it.
3. **Prepare the scope and identity.** Freeze the reviewed selection and read the shared
   `lib/review-schema.json` from the trusted source. Form the request from that schema,
   not a second skill-specific JSON contract. For mapped delivery, the shared command is:

   ```bash
   python3 "$LINTEL_SOURCE_ROOT/bin/li-review-evidence.py" prepare \
     --repo "$LINTEL_REPO_ROOT" --request "$request_file"
   ```

   Retain its immutable context JSON as the expected identity. Include full original
   acceptance and selected paths/revision, not the author's preferred conclusion.
   If the evidence helper/schema is unavailable in this source version, report the
   review handoff as unverified; do not manufacture clearance with a legacy positive string.

   For an ad-hoc diff, code or hypothesis inspection without a work map, use the shared
   `snapshot --repo --base --select` contract from the installed helper's help/schema.
   Then `inspect --repo --snapshot <snapshot.json> --input <inspection-input.json>` binds
   controls, required-policy observations and evidence. Its result has
   `purpose: inspection` and `release_clearance: false`. Do not create a synthetic work
   map or promote that inspection into release clearance. Exact selection and input
   shapes belong to the shared implementation, not this skill.
4. **Run the authorized review or hand it off.** Give the external actor read-only scope,
   separate context, the content selection and a severity/location/evidence report
   contract. Capture actual stdout, stderr and exit status. Missing client/tools leave a
   replayable manual brief; main-agent role-play is not a substitute. Do not let the
   reviewer repair its own findings or run concurrent writers against shared files.
5. **Compare findings.** Cite reviewed files and evidence. Separate agreement, disagreement
   and new findings; follow disputed claims to the actual code. Out-of-scope references
   need clarification, not automatic suppression. Measured usage is recorded only if the
   host supplies it; a requested budget is not proof it was enforced.
6. **Record through the shared evidence interface.** Preserve ad-hoc inspection output as
   non-release evidence. For mapped delivery, populate the decision record according
   to the shared schema, preserving actor/context, attempt, work and exact result identity.
   Structural `validate --record` checks shape only. With `LINTEL_REPO_ROOT` set:

   ```bash
   bash "$LINTEL_SOURCE_ROOT/bin/li-review-log" --file "$decision_file"
   bash "$LINTEL_SOURCE_ROOT/bin/li-review-read" --skill codex \
     --expected "$expected_context" --corroboration "$actual_receipt" --gate-json
   ```

   The latest applicable log decision, not an arbitrary old pass, governs clearance.
   The expected context and corroboration must be actual retained artifacts, not invented
   strings. Missing real host/human corroboration blocks required independent review.
   `--json` is history only; direct `verify` of one record cannot establish latest-log
   status. The reader's exit status and exact result remain authoritative.
7. **Report and hand back.** Summarize actual actor/client/version, target identity,
   findings by severity, agreements/disagreements, commands run, unrun checks and limits.
   A changed acceptance, configuration or selected content requires re-evaluation.
   QA/evidence preparation does not run tests, and SHIP evidence does not push or deploy.

## Failure and data handling

Missing authorization, unavailable client, nonzero exit, malformed result, changed content
or absent corroboration remains explicit. Preserve useful partial findings without labeling
them verified clearance. Do not log raw sensitive prompts or tool output into public artifacts.
A read-only flag is a requested scope, not proof that the external host enforced it.

For manual recovery of mapped work, retain the work map, original leaf text, acceptance, trusted source,
effective profile reference, exact reviewed selection, next action and outstanding independent
review. For an ad-hoc inspection, retain its selected snapshot, scope, findings and limitations
without inventing work identity. No background process or special model is required.

## Examples

`codex --diff` requests an authorized outside opinion on the selected diff. A hypothesis
request asks the separate actor to test the claim against evidence, not merely agree.
A code-only exploratory request can identify alternatives without authorizing edits.
In every case, actual command syntax comes from the installed host and shared evidence
schema, not from this workflow-input shorthand.

See `review`, `investigate`, `plan-eng-review` and `ship` for the surrounding canonical
workflows and [the Universal adapter](../../shims/universal/ADAPTER.md) for host fallbacks.
