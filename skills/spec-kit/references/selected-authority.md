# Selected external authority

This is the Spec Kit bridge's shared procedure for ANALYZE, DEFINE, DIAGNOSE,
FIX and REVIEW. It uses the existing [work map](work-map.md), bounded input
selection (P03) and [content-bound evidence](../../review/references/evidence.md)
(P05). No Spec Kit installation or command execution is needed to consume
existing artifacts. This procedure is model-instructed; the named local helpers
validate their inputs on invocation, not host discovery or workflow obedience.

## Select originals before comparing work

1. Retain the explicitly selected feature/map and original spec, plan, tasks,
   prompt and constitution. Read full relevant task text, dependencies and
   acceptance, not just checkbox state.
2. Select original analysis, converge, bug assessment/test and assessment
   reports only from the operator's selection, the existing handoff's explicit
   links or inspected project configuration. Record their literal paths,
   source/version when known, original finding/task IDs, covered scope and
   unresolved verdicts in that handoff. A conventional directory name is not
   selection; do not choose a newer report or fabricate missing files.
3. The mapped original `tasks.md` remains the **only task source**, including
   converge-appended IDs and phases. Reports provide inputs, acceptance or
   evidence, not another task list. Do not copy tasks into a Lintel plan,
   renumber them or translate report findings into a parallel analysis backlog.
   A newly accepted gap goes through the authorized owner into that same
   original task source; an unaccepted gap remains a cited finding.
4. A report does not supersede the constitution, approved requirements or the
   original task source merely by claiming completion. Conflicting scope,
   owners, verdicts or IDs need a decision before the affected action. If a
   selected bug/assessment workflow has no agreed task mapping, preserve its
   report and resolve that mapping, not a second native defect backlog.

## Observe capability overlap, do not infer installation

Inspect only supplied/authorized host registration or known configuration for
the selected project and client version. Record each relevant command, workflow
gate or hook in the existing handoff, with these separate facts:

| Observation | What must be retained |
|---|---|
| Capability and source | Exact registered name or configured step/event, host/surface, source reference and version; unknown if unavailable |
| Activation | Registered and enabled, disabled, absent from the inspected inventory, or unknown; distinguish configuration from observed execution |
| Coverage | Which selected check, artifact and original task IDs it covers |
| Ownership | The existing authorized check owner, evidence path and any unresolved overlap |

Do not infer a command from a filename, a repository's upstream comparison pin,
an extension directory or a pack label. Do not guess extension manifest layouts
or parse an unsupported version as if its grammar were known. Report unsupported
configuration/version and unknown enablement explicitly. A disabled hook is not
an active second executor; its old report can still be a selected historical
input. Presence in known configuration does not prove registration, execution,
permissions or a passing control on this host.

Compare observed coverage with the check Lintel is about to perform:

| Selected external check | Reuse and overlap decision |
|---|---|
| Analysis / consistency | Consume the original findings and coverage; ANALYZE checks only uncovered Lintel-specific traceability or changed-input gaps |
| Converge / post-implementation audit | Retain the original intent-vs-code findings and appended task IDs; do not run a second gap-list writer for the same scope |
| Clarification / checklist | Reuse answered questions and reviewer-owned acceptance; an implementer cannot self-approve the checklist |
| Bug assessment, fix or test | DIAGNOSE reuses the original repro/hypotheses; FIX retains the chosen repair owner; REVIEW consumes the original test verdict and evidence without upgrading partial/failed to verified |
| Assessment | DEFINE retains the original go / needs-clarification / kill decision and evidence; it does not create a competing design or infer BUILD permission |
| Workflow gate / enabled before or after hook | Identify the exact selected step/event and its owner; paused/failed state is unresolved, not completion or permission to resume it |
| Native host planning/checking | Use only actually observed host coverage; a plan-mode label alone supplies neither review evidence nor execution authority |

When both workflows cover the same check, retain **one owner** for that check
under the current authorization. Ask only for an unresolved choice; do not
automatically run both, disable a hook, resume an external run or install an
extension. Missing/ambiguous observation blocks only the dependent ownership
decision or required check; independently authorized work can continue.
Lintel's content binding and required independent review are distinct obligations,
not reasons to recreate an already-owned analysis. No external verdict waives them.

## Bind the selected reports through existing interfaces

For read-only intake or DRAFT work, add each selected report/configuration as an
explicit `--warm-path` to `li-work-artifacts.py --view context` or `--view budget`.
Warming is a bounded read, **not** acceptance identity or approval.

For approved mapped acceptance, pass the original package/leaf IDs and repeat
`--acceptance` for the selected reports. These sources enter P03's deduplicated
manifest and byte budget as full files; file/byte limits and missing files fail
visibly. P05 `bind_work` owns acceptance identity, including any API-supplied
excerpts and the existing original-task progress normalization.

```bash
python="${LINTEL_PYTHON:-python3}"
"$python" "${LINTEL_SOURCE_ROOT:?select trusted source}/bin/li-work-artifacts.py" \
  --repo "${LINTEL_REPO_ROOT:?select working repo}" \
  --map "${LINTEL_WORK_MAP:?select original map}" --view context \
  --package "${package_id:?original package}" --leaf "${task_id:?original leaf}" \
  --acceptance "${selected_report:?literal original repo-relative report}"
```

Repeat `--leaf` for all selected original IDs and `--acceptance` for all applicable
original reports; do not fill the example with presumed paths. The work-map schema
and its roles are unchanged. Reports/configuration that determine acceptance or
check ownership must also be in the P05 prepare request's `acceptance_paths` (or
its explicit product `selection`), not solely a warming manifest. Record links
in the existing prompt/handoff; do not add report/capability keys to `work.json`.

Before review, declare `required_controls` and immutable `qa_requirements` from
accepted work/policy, not from whichever reports or hooks happen to be present.
Use original evidence paths in observed controls where applicable. A report's
`verified`, `go` or `pass` word is not a typed test observation, authentication
of its author, independently corroborated review or permission to publish.
Verify and carry the original P07 reference and required-policy result unchanged.

On resume, reselect the same paths and verify current bytes/IDs with P05.
Report drift, changed acceptance, new converge-appended tasks or changed selected
registration/configuration invalidates affected evidence. Checkbox progress alone
does not prove completion. The helper never rewrites the originals and its
`release_clearance` remains false. Record only new, attributable Lintel checks
and unresolved coverage, linking originals instead of reproducing their findings.

## Keep approval, review and publication distinct

Retain the actual owner/revision and decision for **source approval** separately
from the map's scope authorization. Preserve the original assessment/verdict as
an input, the actual independent review and control evidence as another fact,
and permission for publication as a separate operation. Selecting, loading or
pinning an artifact/policy supplies none of the other facts. An unknown source
approval or unavailable mandatory review remains open; do not manufacture it
by selecting another report or changing an evidence label.
