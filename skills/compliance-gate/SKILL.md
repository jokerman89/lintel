---
name: compliance-gate
layer: foundation
description: Compliance-gate aggregator — runs all gates the active pack declares (compliance.hooks) as ONE green/red verdict. Embarrassment protection for compliance (6.10).
color: red
tools: Read, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

# Compliance gate

Resolve the applicable pack controls, preserve per-control evidence, and evaluate
them through `lib/review_contract.py`. A single applicable mandatory failure,
execution error or unverified result blocks its affected action. Counts and
advisory scores never downgrade it. Advisory deviations never become mandatory
merely because they are numerous.

## When to use

- Before an authorized customer-share, release or merge.
- To assess a selected artifact or engagement against the applicable policy.
- For preparation or CI feedback, with the actual enforcement layer stated.

This skill is not an installed enforcement mechanism. Compatible hooks, branch
rules and enterprise controls need separate configuration and observed execution.
No hook is activated by reading this file.

## Resolve policy before controls

Use the trusted source bundle and the working repository's selected profile.
Preserve the P07 effective profile reference and `required_policy` result through
review and delivery. A required profile declaration is external to the potentially
broken manifest; missing/invalid required policy cannot silently become `_default`.
`PROFILE_REQUIRED` or `PROFILE_DRIFT` remains a nonzero unresolved requirement.

Gates and their mandatory/advisory requirements come from actual policy and scope,
not a built-in list of favored gate names. Record source, version and applicability.
If those are unknown, keep the affected mandatory requirement unverified.
Neutral first use with no requested organization policy and no applicable controls
is a valid **no-applicable-controls** result, not verified compliance.

## Run and record

For each declared control, use an available compatible execution path. A tool name,
pack label, hook file or delegated role is not evidence that it ran. Independent
controls may run concurrently only when the host can safely do so; otherwise run
them sequentially. Missing capability blocks its mandatory acceptance, while
independent authorized preparation may continue.

Use the [shared result/evidence contract](../review/references/evidence.md):

| Field | Meaning |
|---|---|
| `requirement` | `mandatory` or `advisory`, derived from policy |
| `applicability` | `applicable`, `not_applicable` or `unknown` |
| `status` | exactly `pass`, `fail`, `unverified` or `error` |
| `reason` | finding, limitation or grounded exclusion |
| `policy` | source/version/scope; regulatory jurisdiction, actor and effective date |
| `evidence` | actual local report/command-output references, later content-hashed |
| `observation` | actual test counts, browser states, measured contrast or other check inputs |

Not-applicable needs a grounded source/version, reason and evidence. Uncertainty is
not an exemption. Do not relabel a failure as N/A to evade a required control.
Regulatory conclusions inform qualified legal review, not certification.

## Aggregate through the shared implementation

Prepare a JSON object containing `controls` and `required_policy`, then run:

```bash
src="${LINTEL_SOURCE_ROOT:?set the trusted installed source root}"
python="${LINTEL_PYTHON:-python3}"
"$python" "$src/bin/li-review-evidence.py" controls \
  --input "${control_input:?set actual observed control results}"
```

The return is a structured result with exact `status`, `blocked`, `blockers`,
`advisories`, `assurance` and all effective per-control outcomes. Exit 3 means
blocked; malformed input exits 1. Exit 0 alone is not proof of compliance:
`assurance: no_applicable_controls` explicitly means no applicable controls were
verified. Preserve the result rather than translating it back into a failure-count
rule or average.

The evaluator also rejects false positive observations: normal-text 3.5:1 contrast
fails AA; zero executed tests, missing browser evidence and unknown policy remain
unverified. Static inspection cannot establish runtime accessibility or rendering.

## Report and integrate

Keep the human-readable report:

```text
Compliance assessment: <selected artifact and scope>
Policy source/version: <verified reference or unresolved>
Assurance: observed_controls | no_applicable_controls
Blocked: true | false
Mandatory findings: <control ID, status, evidence, next repair>
Advisory findings: <control ID, status, suggestion>
Not applicable: <control ID, grounded reason/evidence>
Unavailable/unverified: <exact observation still needed>
```

Feed the same controls into the content-bound review decision, binding its
package/leaves, acceptance, profile, attempt and result. Persist through
`bin/li-review-log`; SHIP consumes `li-review-read` and same-context QA. A prose
GREEN, empty error list or audit event is not standalone clearance.

An operator note does not bypass mandatory policy. A permitted exception needs the
actual policy source, scope and authorization; the owner must revise the selected
requirements and obtain new affected review. Keep the original failed observation
in history. This skill has no magic `--override` success path.

Optional summary telemetry still uses the unified source helper, never an inline
audit writer:

```bash
source "${LINTEL_SOURCE_ROOT:?set source root}/bin/_audit.sh"
audit_log compliance-gates verdict \
  "status=${control_status:?set evaluated status}" \
  "blocked=${controls_blocked:?set evaluated boolean}" \
  "evidence=${review_record:?set bound decision path}"
```

## Status and recovery

- **DONE**: all applicable mandatory controls verified; distinguish a neutral
  no-applicable-controls assessment from verified compliance.
- **DONE_WITH_CONCERNS**: no mandatory blocker; advisory findings remain visible.
- **BLOCKED**: any mandatory failure/error/unverified, missing required policy or
  stale supporting content. Repair and re-run the affected checks.
- **NEEDS_CONTEXT**: scope is not established; this is not clearance.

If a gate crashes, retain `error` and its diagnostic. If a renderer/browser/tool is
unavailable, retain `unverified`. Continue unaffected authorized checks, not the
blocked delivery. Sanitize evidence and do not copy credentials or customer data.
