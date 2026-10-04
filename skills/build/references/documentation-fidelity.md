# Documentation fidelity

Use this method for a documentation leaf or a change to documented behavior.
BUILD owns the method; SHIP consumes its actual document-check evidence through
the existing review path. `DocWriter` and `generate-docs` apply it directly,
without delegating to one another. It adds no role, document schema or clearance
mechanism.

## Scope and intent before edits

1. Retain the original task, accepted documentation/specification/architecture,
   selected code and tests, output ownership, verified profile and required
   controls. Expand source globs to an exact file set before reading/writing.
   Read complete selected files and relevant imports/types/exports/callers through
   rooted, no-link reads. Missing/unreadable source is a gap, not an empty module.
   Do not execute imported code merely to document it.
2. Treat accepted documentation as **intent** and implementation as an
   observation. A discrepancy may be a code defect, not permission to rewrite the
   contract to match a bug. Identify the controlling requirement and stop that
   correction when the intended behavior or authority is unresolved; report the
   divergence and continue only independent authorized work.
3. Honor frozen paths and existing content. A frozen document can have a reported
   finding, never a silent edit. An existing output needs explicit replacement/
   append authority or an explicitly chosen alternate path; no fallback write.
   Stay within the doc's voice and intended audience unless a change is authorized.

## Source inventory

Record source locations and exact content identities/revisions for:

- Public exports, signatures, parameters and defaults, return values/types.
- Errors/refusals, side effects, authorization, platform/version constraints.
- Callers, tests, accepted intent and evidence supporting behavior claims.
- Required data, units, citations, assumptions, limitations and recovery paths.
- Referenced files/links and examples, including expected output and its basis.

Distinguish observed implementation, comments, proposed behavior and assumptions.
A test's source is not proof that it ran; an illustrative response is not a
guaranteed API response. Shallow depth may omit internal detail with a scope
reason, not public behavior or material qualifications. Deep depth adds relevant
internals, edge cases and caveats without inventing unsupported claims.

For a removed option or path, retain its supported replacement, migration steps,
or explicit deprecation decision and source. Do not delete the only explanation
and leave users with an unexplained broken command. If no replacement/decision
exists, report the unresolved migration instead of inventing an option.

## Claim-to-source coverage and examples

Map every in-scope public export and material claim to its documentation section
and source/evidence location. Check both directions: unsupported document claims
and missing source obligations. Preserve code, table cells, units, citations,
reasoning and limitations; presentation length is not a license to discard them.

Keep a **claim-to-source coverage record** in the caller's existing owned report,
not a new interchange file or schema. A useful table contains:

| Claim / public behavior | Intent and source location + identity | Doc section | Check / example command | Result and limits |
|---|---|---|---|---|
| Actual selected claim, not a stock example | Exact file:line, revision/hash and relevant intent | Actual destination | Performed inspection or command; otherwise unrun | checked, unrun or divergent, with evidence and remaining scope |

- **checked** means the named source/document check was actually performed.
  It does not imply that an example executed or a native application was tested.
- **unrun** identifies an example/test or required observation not executed,
  with its reason and affected claim. Never manufacture successful output.
- **divergent** retains the precise doc/implementation/intent discrepancy,
  severity, proposed correction and any unresolved decision.

Run safe requested examples/tests only inside the task's actual authority and
isolated fixture scope. Inspect side effects first. Record the exact command,
input/source version, exit, assertions/coverage and logs. A read/edit-only role
hands that precise execution request to its authorized caller; absent execution
stays unrun. Neither a link check nor source inspection proves a runnable example.

## Refresh, publish and consume

Re-read identities before publication and evidence consumption. Any changed source,
template/config, documented output or required control invalidates the affected
coverage: refresh those rows, dependent examples and review evidence. Do not reuse
stale hashes or edit a hash merely to make an old report look current.

Publish only to the selected owned path, preserving any authorized preimage.
Use rooted atomic publication and read it back; a partial or failed readback is
not completed documentation. Apply the actual configured data/voice/distribution
requirements. Customer-guide/pack-voice output stays DRAFT until its applicable
controls are observed; neutral mode adds no invented vocabulary or license gate.
Generation does not upload or distribute anything.

For BUILD, attach the coverage and actual checks to each affected original leaf.
For SHIP's existing mandatory document check, consume those exact current source,
document and observation bytes through the
[P05 content-bound evidence path](../../review/references/evidence.md).
Preserve the original `qa_requirements`, applicability, policy and profile; use
the existing `check` kind when appropriate, not a new control schema. Record
actual pass/fail/error/unverified outcomes. Required missing or divergent evidence
blocks its affected acceptance regardless of a polished document or empty issue
list. A docs-only tests-N/A rationale cannot waive applicable executable tests,
and this report cannot replace required independent review.

For generated formats, this document check establishes source/document coverage
only. Word/PPT/web composition, saved notes, workbook recalculation/caches and
PDF production/absent-reader limits remain with their format methods. Preserve
`generate-docs` reference/customer-guide/tutorial targets and their depth/voice
choices; do not collapse them into a different artifact or claim that a Markdown
file proves another format's fidelity.
