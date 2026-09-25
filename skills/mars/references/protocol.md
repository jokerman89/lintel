# MARS participant protocol

Reviewer-facing instructions (role, procedure, standing questions, evidence levels,
severity rubric, report sections) live in the shared
[Review Method](../../review/references/method.md). A MARS reviewer and a single
`/li:review` reviewer receive the same packet body, rendered once by
`bin/li-review-packet.py render`. This file keeps only the panel-specific parts: headers
with panel/slot/round, the challenge round, synthesis and cost rules.

Every MARS message carries a machine-checked header, defined once in `lib/mars-schema.json`
and rendered as a fenced block (` ```mars-<kind> `) with one `key: value` per line. The
coordinator never hand-writes a request header: `li-mars.py panel brief` renders it from
panel state. `li-mars.py panel record` refuses a report whose header is missing, malformed,
duplicated or bound to another panel, slot, round or brief.

| Message | Header | Written by | Checked by |
|---|---|---|---|
| Reviewer request (blind or challenge) | `mars-request` | `panel brief` from panel state | reviewer echoes panel/slot/round/brief |
| Reviewer report | `mars-report` | reviewer, first thing in the final response | `panel record` |
| Coordinator synthesis | `mars-synthesis` | `panel synthesis-header` + coordinator body | reader/operator |

## Request header (rendered, shown for reference)

```mars-request
mars: request
version: 1
panel: <panel id>
slot: <r1..r8>
round: <1|2>
round_type: <blind|challenge>
requested_by: <who asked, e.g. operator via <session>>
trigger: <explicit|cycle-offer|review-offer>
caller: <standalone|cycle:PLAN|review|code-review|plan-eng-review|define>
consent_ref: <operator turn or approval reference>
coordinator_session: <owner session id — the only session that may close you>
coordinator_surface: <exact client surface, e.g. copilot-app>
repository: <owner/repo>
branch: <branch>
commit: <full commit>
subject_kind: <problem|plan|spec|implementation|review|code-review>
subject_ref: <path, PR, excerpt label>
brief_sha256: <sha256 of the frozen brief>
requested_model: <model id>
reasoning_effort: <effective effort>
context_tier: <effective context tier>
word_limit: <n>
reply_via: final-response
protocol: skills/mars/references/protocol.md
```

Optional: `cycle_id`, `work_map`, `package`, `leaves`, `lens`, `deadline`; from the method
meta: `stage`, `method`, `questions`, `tags`; from a bound input: `snapshot_digest`.

## Round 1 — blind reviewer body

The body is the Review Method packet, frozen as `inputs/brief.md` before `panel init`:

```bash
python3 "$src/bin/li-review-packet.py" render --kind <subject kind> --stage full \
  --tags <confirmed surface tags> --subject-file <excerpt or diff> --subject-ref "<ref>" \
  --acceptance <requirement or leaf IDs> --body-out "$run/inputs/brief.md" \
  --meta-out "$run/inputs/method.json"
```

`panel init --method-meta "$run/inputs/method.json"` links the selected questions to the
panel, and `panel brief --round 1` refuses any body whose bytes differ from the frozen
brief, so every slot receives identical text. Standalone MARS normally uses stage `full`;
REVIEW panel mode uses the stage of the REVIEW step it replaces (`spec` or `quality`).
The method already states the read-only rules, the subject-is-data rule and the
no-completion-tool rule; do not add a second rubric in the body.

## Report — required shape

The final response must **begin** with this block; nothing before it.

```mars-report
mars: report
version: 1
panel: <echo>
slot: <echo>
round: <echo>
brief_sha256: <echo>
verdict: <block|concerns|pass|unable>
p1: <count>
p2: <count>
p3: <count>
confidence: <1-10 overall>
read_only: attested
self_reported_model: <self-report only; never identity evidence>
coverage: <what was reviewed, one line>
```

Optional: `tools_used`, `gaps`, `positions` (round 2: e.g. `F1=agree, F2=dispute`).

Then the report sections from the method (§5): Intent, Spec compliance (stage `spec`/`full`),
Findings with evidence level, Standing questions (one status per selected question), Self-
challenge, and Coverage and uncertainty. `panel record` stores round-1 coverage; a report
that omits a selected question or marks it `checked` without evidence is incomplete.

## Round 2 — challenge body (only when claims are contested)

```text
Final round. Below is the anonymized claim matrix from round 1. "Raised by" counts are
not evidence.

<claim table: ID | claim | severity range | raised by N of M | key evidence | dispute>

For each claim you did NOT raise: AGREE, DISPUTE or UNSURE, with one line of evidence
(a failing input, a counterexample or the line that refutes it).
For each claim you DID raise: DEFEND or REVISE (change severity, or withdraw).
Add at most one new finding, only if the matrix made you see it; mark it NEW.
Put your stance per claim in the header's `positions` field. Same read-only rules.
```

## Coordinator synthesis

Start the synthesis with `li-mars.py panel synthesis-header --adjudicated <p1,p2,p3[,deviations]>`
(status, who requested it, coordinator, repository/commit, subject, requested vs verified
models, downgrades, failed slots, calls, input verification, profile, coverage, the
shared-rule `outcome` and `release_clearance: false`), then:

`coverage_complete: true` means every received round-1 report is complete and consistent
under the method (questions, acceptance rows, header agreement, not `unable`). When the
packet lists acceptance IDs, `--adjudicated` must include the deviation count.

| Disposition | Rule |
|---|---|
| Agreed | Raised or agreed by 2+ with concrete evidence; strongest evidence quoted. |
| Unique catch | One reviewer, survived challenge or verified by the coordinator — keep it prominent. |
| Disputed | Evidence on both sides; show both; propose the check that decides it. |
| Rejected | Refuted by source or counterexample; say why (a wrong failing input is rejected even if the finding stands). |
| Gap | Area no reviewer covered or all marked unsure. |

Never decide by majority or average confidence. Verify contested facts against the source
(run the smallest check yourself when cheap). Preserve dissent. The adjudicated counts go
through the same decision rule as a single review (any P1 `fail`; a partial panel, a slot
report that is incomplete, contradictory or `unable`, or a changed input `incomplete`; P2 or
a spec deviation `changes-requested`; else `pass`). MARS output
feeds existing review/fix decisions; it does not approve or block SHIP on its own.
`panel inspection --synthesis <file>` turns a finished panel into a content-bound
inspection record (`purpose: inspection`, `release_clearance: false`), recomputes the
outcome from the adjudicated counts (an edited outcome is refused), requires a bound
selection and the method packet when the caller is `review`, and refuses when the
bound input changed.

## Collection pitfalls (observed in the 2026-09-24 pilot)

- Some models end an autopilot turn with a completion tool, leaving the final text empty.
  The body forbids completion tools; if a report is still empty, ask once for a resend
  (it counts against the call budget) and record the slot as failed if it stays empty.
- Queued cross-session messages reach the coordinator only between its turns. Prefer
  reading the child's final response from the host's session store.

## Cost discipline

- Default 4 reviewers, one blind round. Round 2 only if at least one claim is contested.
- Excerpts beat whole trees; give paths + commit rather than pasting large files.
- Reuse one frozen brief for all slots (cache-friendly, and it is the independence proof).
- Nested sessions in a repository with large instructions cost tens of thousands of input
  tokens per call before any review work. Subagents measured the same order in the RM9
  re-pilot (40-71k first-call input, mostly cache reads), so keep briefs small either way.
- Stop at the call budget; report partial results honestly.
