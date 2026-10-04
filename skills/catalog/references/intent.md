# Intent narrowing

Catalog owns this metadata-first method. `skill-router`, `orientator`, `welcome`
and SENSE's discovery follow-up delegate here; none owns a second selection recipe.
This produces a shortlist, not execution, a model policy or a replacement for native
host discovery. SENSE separately owns its existing pack-configured high-risk control.

## When to use

- Operator doesn't remember exact skill name
- New Lintel user exploring capabilities
- Ambiguous intent — multiple skills might apply, want disambiguation

## When NOT to use

- Operator already knows the skill — wastes a turn
- To select or activate a runtime actor: this method can shortlist agent metadata,
  but the actual delegation binding and authority belong to the host.

## Workflow

1. **Read operator intent.** Use the supplied request. Ask only for a missing decision
   through the current host's available question tool; conversation is a fallback only
   when there is no question tool, never when permission was denied.

2. **Query compact metadata first.** Resolve `LINTEL_SOURCE_ROOT` from the loaded trusted
   adapter or explicitly selected Lintel source, separately from the working project.
   Use an available permitted shell and Python 3.9+:

   ```bash
   # lintel-catalog-intent
   : "${LINTEL_SOURCE_ROOT:?select the trusted Lintel source}"
   : "${keyword:?select a nonempty keyword from the supplied intent}"
   "${python_cmd:-python3}" -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" \
     --json --kind=all --query="$keyword"
   ```

   Select a nonempty keyword from the intent, not a fabricated regex or shell fragment.
   Pass it as one quoted literal argument; never use `eval` or interpolate a command.
   Use `python` if that is the Python 3 command. If a keyword is too narrow, broaden it
   or request `--json` without filters: that still returns metadata, not prompt bodies.
   Use the [single metadata contract](metadata.md); do not glob
   and parse the corpus separately.

   If the request already names a capability selection, use its existing projection:

   ```bash
   python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection="$selection"
   ```

   `selection` is an exact nonempty ID from `--json --list-selections`, not an inferred
   installation or policy choice. Keep ordinary routing unchanged without it. Follow
   the [selection contract](selections.md); do not turn its
   closure into a second routing graph or read every dependency body. A role-oriented
   selection such as `demo-script` uses catalog's agent metadata rather than
   relabeling roles as skills. Invalid selection data stops the affected discovery.

3. **Shortlist at most three candidates.** Match names, descriptions, families and existing
   aliases. This is model judgment over source metadata, not a new routing engine or a
   measured confidence score. Preserve staged/template warnings. A `full` hint does not
   establish maturity, implemented formats, permission or live host support.

4. **Read only selected candidates.** Read the shortlisted canonical bodies (at most
   three) via their returned paths under the same trusted `source_root`. Check their
   actual when-to-use, exclusions, prerequisites and failure behavior before recommending
   a method. Preserve alias notes and arguments; do not invent an alias rewrite or silently
   retire an alias because its recorded date passed. Never load all skill/role bodies.

5. **Present up to three recommendations.** Explain fit, important limitations and the
   actual invocation/fallback. Native wrapper and agent registration require current host
   evidence; use explicit canonical-file reading when permitted instead of made-up tools.
   Recommendation alone does not execute the selected workflow or authorize new work.

## Output format

```
MATCH: <operator intent quoted>

Top match (qualitative fit, not measured confidence):
  <canonical name, retained alias if used>
  → <one-line why, plus source/body limitations>
  → Invocation: <verified host entrypoint or explicit canonical-file path>

Alternative #2:
  <canonical name>
  → <rationale>
  → When this is better: <condition>

Alternative #3:
  <canonical name>
  → <rationale>
  → When this is better: <condition>

If none of these fit, your intent might need:
- A new skill (`/li:skill-new`, if authoring is authorized)
- An agent instead (see agents/<category>/)
- A direct conversation (no skill needed)
```

## Edge cases

- **No good match** — broaden the metadata query before suggesting new authoring or direct conversation.
- **Match is an agent, not a skill** — query `--json --kind=agent` through the same helper,
  then read only the selected role. Use actual host delegation or an honest serial/manual
  handoff; a role file is not a registered agent or independent reviewer.
- **Intent is multi-step workflow** — consider the existing `/li:cycle` and its authorized
  entry phase. The nine phases remain SENSE, SCOPE, DEFINE, DISCOVER, PLAN, BUILD, REVIEW,
  SHIP and CAPTURE. Resume is a utility returning to saved work, not another phase.
- **Secrets or customer data in intent** — omit them from the discovery query and report;
  flag the handling boundary without repeating the sensitive content.
- **Invalid source or helper/parser failure** — report the failure, not an empty success.
  Do not regenerate, install, activate, change roots or skip malformed entries.
- **Execution unavailable** — the trusted `skills/CATALOG.md` is a disclosed skills-only
  snapshot fallback. Read only selected canonical files afterward, through permitted tools.
  Missing source or denied reads block the affected work.

## Discovery cost

Selection uses one maintained metadata inventory before any candidate prompt reads.
No personal telemetry is consulted. Metadata tests establish this file/query behavior,
not a measured improvement in model accuracy or time to first use.
The catalog's query is literal substring filtering, not semantic ranking; the shortlist
is the current actor's judgment. Do not call it an additional LLM escalation, invent
success percentages or report a configured token budget as consumed tokens.

## Privacy note

The helper performs local data reads and no network calls. Model processing still follows
the actual host's service and policy; do not promise offline processing or that intent
never leaves the machine. Keep secrets and customer data out of queries and reports.
