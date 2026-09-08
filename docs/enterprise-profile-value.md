# Make an enterprise pack change the work

A company pack is useful when a requirement changes a decision, a task, a check or a
delivered artifact. A company name, a different tone or a longer startup message alone
does not establish engineering value.

Lintel separates personal session preferences from the company pack. The pack resolver
selects the `packs/active-pack` pointer and caches the resolved manifest for the session.
`pack-switch` changes that machine-global pointer for subsequent sessions. Confirm the
**loaded** pack before starting work in another company context; do not infer it from a
stale `active_pack` line in a personal profile. Pack activation does not install an
extension plugin or configure enterprise platform policies.

## Use the existing fields deliberately

| Pack input | Expected effect | Evidence to retain |
|---|---|---|
| `compliance.mode` and `compliance.hooks` | Identify applicable controls and their failure handling | Requested control, available host implementation, command/result or missing capability |
| `navigation.high_risk_workflows` | Raise the matching route's risk | Resolved workflow and risk classification |
| `voice.corpus` and `voice.gates_active` | Supply task-relevant wording rules and output review | Applicable source and review against the actual deliverable |
| `brand.templates` / `color_tokens` | Supply the selected format's visual constraints | Selected template/token source and rendered-artifact review |
| `roles.source`, `knowhow.source`, `opinions.source` | Make relevant expertise available to the agent | Which source was actually read and what decision it changed; availability alone is not consumption |
| `extension.*` | Declare a pack's additional capabilities | Host discovery of the installed plugin and the requested workflow |

Field resolution and route classification are executable helpers. PLAN's requirement
traceability and output review are agent instructions. Automatic Lintel hook execution
requires its compatible Claude Code registration; another host needs its own verified
controls. A `hard` label is not proof that a check ran. Dormant handoff gates remain opt-in
under ADR-0008; resolving their configuration does not activate them.

## Preserve organization requirements when making team packs

The organization owns the shared pack. A team pack declares only intentional differences:

```yaml
schema_version: "1"
name: platform-team
version: 1.0.0
extends: organization-base
brand:
  templates: templates
```

The omitted `compliance` block inherits from the organization. An explicit child block
replaces the **whole** parent block. Copying `_default` into this child would explicitly
replace the organization's controls with neutral values. `pack-create --extends` therefore
starts with identity and ancestry only. Validate the resulting chain before activation.

## Put the effect in the plan

PLAN records the loaded pack and maps each applicable requirement to existing task IDs,
acceptance criteria and evidence. It cites the source rather than copying a policy manual.
Use the canonical plan template; do not create another task backlog.

For a synthetic example, consider the same change under `_default` and an organization
pack that requests `secret-scan-block` and marks `cycle` as high risk:

| Question | Neutral baseline | Organization pack |
|---|---|---|
| Requested company controls | None | The named control is present in the resolved list |
| Team inheritance | Neutral values | The child retains the parent's control and mode |
| Required planning evidence | Task acceptance and verification | Also map the applicable control to the task/check and record actual host support |
| Completion statement | Report the checks performed | Report the requested control's result, or explicitly retain the unmet requirement |

This is a test of configuration and requirement flow. It does not establish that a
production platform is protected, or that generated plans are better. Hermetic tests
exercise the real resolver, risk classifier, digest and skill snippets with synthetic packs:

```bash
bash tests/integration/enterprise-pack-impact.sh
bash tests/integration/enterprise-workflow-snippets.sh
```

## Keep planning proportional and measure its benefit

Use flat plans for XS/S work, phases for M and milestone trees for L/XL. Leaf cards need
an owner/edit boundary, requirement IDs, dependencies, observable acceptance and a concrete
verification method. Decompose at a meaningful boundary; splitting a command into several
administrative cards adds no deliverable. The approved hybrid model keeps 2–5 minute leaves,
while one owner executes a bounded package and two review stages cover all member leaves
and their integration (ADR-0026). Assess review depth from the whole package's risk.

Token priors describe a **whole cycle**, so use the prior once, with its basis and sample
count. Do not multiply it by every leaf. Uncalibrated estimates are planning assumptions;
no dollar cost follows without pricing and measured usage. Wall-clock estimates are optional.

Pilot the pack on representative tasks using comparable repositories and host capabilities.
Agree the success thresholds before running. Compare:

- Accepted requirements covered by executable checks or reviewed artifact evidence.
- Missed policy requirements and defects found after the first review.
- Operator interventions, rework and successful cold-session handoffs.
- Actual elapsed time and measured tokens per accepted deliverable, including planning and review overhead.

Record task difficulty and model/host conditions. Keep the pack only where it improves the
agreed outcomes without unacceptable overhead. The model-level eval harness in ADR-0021
is still staged; shape-test success is not a productivity measurement.
