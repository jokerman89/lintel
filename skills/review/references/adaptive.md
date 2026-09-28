# Adaptive review depth

Use the existing [Review Method](method.md) and [release evidence](evidence.md).
Depth selects effort and additional questions; it does not approve a change,
change host permissions, choose models, activate scanners or consent to MARS.
Read [security evidence](security.md) only when that surface is relevant.

## Commands and defaults

Canonical workflow inputs:

- `/li:review --depth auto` chooses a consequence-based floor; this is the default.
- `/li:review --depth lean` requests the cheap path and refuses an evidenced higher floor.
- `/li:review --depth deep` requests additional assurance without automatically spawning a panel.
- `/li:code-review --depth auto` uses the same method on the selected diff.
- `/li:sc threat-model` or `/li:sc auth-flow` requests existing specialist depth.
- `/li:mars` explicitly requests a bounded panel under its existing consent and host gates.

Native adapters use their `li-*` spelling. These are workflow inputs, not flags
to forward to an unrelated client. The executable helper is
`python3 "$LINTEL_SOURCE_ROOT/bin/li-review-packet.py"`.

| Depth | Typical evidence | Additional work |
|---|---|---|
| lean | Known local/internal, contained, reversible mechanical change with no behavior or security-boundary change | Existing universal and applicable questions; no depth-only lenses or automatic extra reviewer |
| standard | Known noncritical behavioral change, or unassessed context | Existing subject/tag questions; unknown facts stay `needs-context`, never a low-risk claim |
| deep | Production, untrusted exposure, sensitive/irreversible consequence, changed security boundary or shared blast radius; explicit escalation | Additional assurance/recovery questions plus applicable surface questions and stronger targeted evidence |

Keep the existing substantive independent-review obligation at every depth.
One line of authorization code can need deep review; a large prose-only edit
need not. Keywords suggest surfaces; they never establish consequence or permission.
Neither a deep label nor a longer report proves that the reviewer did the work.

## Evidence once, reuse within the same selection

Derive facts from the accepted task, deployment declaration, code and actual
configuration. Do not ask a six-question interview when those sources settle
them. Ask only unresolved material facts or authority; otherwise preserve unknowns.
Save the compact assessment input in the selected run, not a new backlog:

```json
{
  "schema_version": 1,
  "asserted_by": {"actor": "coordinator-context", "reference": "accepted task reference"},
  "facts": {
    "deployment": "internal",
    "exposure": "trusted",
    "impact": "reversible",
    "behavior_change": true,
    "security_boundary": false,
    "blast_radius": "contained"
  },
  "evidence": {
    "deployment": "spec.md: deployment scope",
    "exposure": "design.md: caller boundary",
    "impact": "spec.md: recovery requirement",
    "behavior_change": "tasks.md: selected acceptance",
    "security_boundary": "design.md: unchanged authority",
    "blast_radius": "reviewed consumer inventory"
  }
}
```

Example references are not observations. Omit unknown facts or use `unknown`;
known facts require actual references. Bind the fact file, referenced evidence
and applicable configuration in the existing content-bound selection.
The helper validates declarations, not their truth or the asserter's authority.
A reviewer contests unsupported facts through the existing contract/boundary
questions; stop the affected decision and reassess rather than retaining a
convenient lean result.

```bash
pkt="$LINTEL_SOURCE_ROOT/bin/li-review-packet.py"
python3 "$pkt" depth --risk-file "$run/risk.json"
python3 "$pkt" tags --paths <selected paths> --text-file "$run/subject.md"
python3 "$pkt" render --kind implementation --stage quality \
  --depth auto --risk-file "$run/risk.json" --tags <confirmed surface tags> \
  --require-question SQ-U04 --subject-file "$run/subject.md" --subject-ref "<selected result>" \
  --body-out "$run/inputs/brief.md" --meta-out "$run/inputs/method.json"
python3 "$pkt" check --report "$run/reply.md" --meta "$run/inputs/method.json" \
  --body "$run/inputs/brief.md"
```

Select required questions from accepted requirements and control obligations,
not from their answers. The example assumes the trust-boundary question is an
accepted obligation. Catalog defaults are advisory; depth never upgrades them.
Required IDs not selected by kind/stage/tags are refused: correct the selection,
do not drop the obligation. The spec stage remains acceptance-only.

## Non-negotiables

Selected spec/leaf coverage, applicable mandatory controls, verified required
policy, correct content identity and genuinely attributable required independent
review stay intact at every depth. Missing, failed or unverified mandatory
evidence cannot be averaged away. An older pass cannot override a later rejection.
Neither a scorer result nor an inspection packet clears SHIP.

Question coverage and policy applicability are different. A genuinely irrelevant
question can have a grounded N/A explanation. That answer does not change an
applicable control's inventory or excuse a required pattern clause. Explained
advisory `not-checked` is visible; mandatory `not-checked` is incomplete.

For high-consequence work, inspect the actual trust boundaries and failure paths,
use existing authorized checks and obtain the required independent challenge.
Invoke additional specialists only for an identified evidence gap. Stop at a
bounded unresolved result rather than launching repeated panels hoping for agreement.
MARS remains opt-in and its adjudication preserves dissent.

## Established company and repository patterns

Do not build another policy lookup. When the installed source includes reusable
patterns, follow that installed pattern skill's consumer contract. Preserve the
original artifact/target/audience facts and selected lock. An absent lock or empty
old pack accessor is not proof that no patterns apply.

Use the existing profile/pattern launcher for a current roots envelope. For a
known lock, verify before projecting the original package/leaf clauses. A thin
context adapter is available:

```bash
python3 "$pkt" pattern-context --roots "$run/pattern-roots.json" \
  --lock "$lock" --context "$pattern_context" --task-map "$pattern_task_map" \
  --package "$package_id" --coverage "$pattern_evidence"
```

It calls the trusted sibling provider's own parse, verify, project and coverage
functions. It carries full requirements, settings and waivers, not a top-N
replacement. Assets are metadata only. When an internal document is needed,
use that provider's `asset_refs` and `read_asset` for the selected review-domain
asset after verification; never load a whole company knowledge base, fetch a
private URL automatically or execute asset contents.

Include the result as data in the packet's existing `--context-file`. Pass its
returned `question_tags` with the confirmed surface tags (`--tags pattern-context,...`)
when applicable clauses or settings were projected; this selects SQ-CONTEXT-01.
Bind
the actual lock, context, mapping, profile and evidence inputs in ADR-0028.
The provider's coverage result remains a supplemental control, always
`release_clearance: false`; it cannot clear the main review by itself.

The optional provider is an explicit installation dependency. Missing helper,
unsupported runtime, failed profile, stale lock or non-JSON result is unavailable,
not empty. Known lock/explicit reference/configured pattern/required-policy
dependencies block their affected action. Unrelated review may continue with the
limitation stated only when no known obligation depends on it. Only a current
successful provider list/resolve establishes no applicable patterns.

## Keep the default cheap

No network, scanner, model or panel is called by the depth/packet helpers. Reuse
unchanged accepted context; rerun affected checks when content or policy changes.
Load only the selected question set and needed references. Keep calibration
opt-in through the existing outcome log and [offline evaluator](evaluation.md).
Proposals need source evidence and an owner; they never rewrite policy themselves.
