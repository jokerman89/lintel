# Compliance and control boundaries

Lintel provides workflow instructions and a small set of local checks. Organisation-specific
policy references and gates belong in an installed pack. Lintel itself asserts no regulatory
posture and provides no certification, attestation or data-loss-prevention guarantee.

## Neutral baseline

The shared instructions establish three basic rules:

1. Keep customer and sensitive personal information out of this public tooling repository.
2. Keep credentials out of code, logs, commits and shared prompts; use approved secret mechanisms.
3. Obtain the required authorization before production mutations or changes to shared access.

A downstream project must add its own data classification, authority and handling rules. The
neutral `_default` pack uses `compliance.mode: advisory` and no company-specific gate list.
That is a starting point, not a substitute for the organisation's policy.

## Instructions versus controls

| Mechanism | Behavior | Activation and limitation |
|---|---|---|
| Session checklist | Agent checks authority, sensitive data, production impact and secrets | Instruction-driven; not a tool permission system |
| Pack gate list | Workflow resolves declared checks and reports their outcomes | Pack must supply usable checks; invocation depends on the workflow |
| Claude Code secret/customer-data hooks | Pattern scans recognized Git commit/push tool calls | Selected hooks registered by Claude plugin; limited coverage and explicit overrides |
| Claude Code warning/context hooks | Surface edits, prompts, state and workflow warnings | Warning does not block; not every hook is registered by default |
| Copilot repository kit | Native workflow skills and specialist agent profiles | No Lintel hook adapter installed |
| Repository protection and CI | Team-owned merge, test and access controls | Configure and validate independently of Lintel |

Copilot supports native hooks, but Lintel's existing Claude Code hook bundle is not translated to
that API in this release. See [Copilot](copilot.md#hooks-and-security-controls). Other clients'
actual Lintel integration is described by the generated
[capability table](../README.md#multi-cli-support).

## Claude Code block hooks

`secret-scan-block` and `customer-data-block` run on the Claude Code `PreToolUse` Bash event.
They recognize command strings containing Git commit/push operations, including selected `git -C`
and selected literal wrappers. Commit inspection scans added lines from staged and unstaged
tracked changes. Push inspection scans every commit in each selected source ref's ancestry,
including additions later deleted and merge resolutions. It does not trust local tracking refs
as proof of remote history and ignores local replacement objects, as Git transfer does. There is
no commit-count cutoff. The implementation is in `hooks/shared/_input.sh` and `_patterns.sh`.

The scanners use regular expressions for selected token and personal-data formats. They do not
inspect binary content or commit/tag messages, provide entropy detection, or universally recognize private data.
Novel credential formats may pass, and benign contact details may trigger the customer-data
scanner. Scanner or Git collection failure blocks recognized Git operations unless explicitly
overridden. Unknown wrappers, dynamic shell syntax and unsupported refspec forms also block;
split them into supported literal commands for inspection. Input is never evaluated as shell code.

Full ancestry is rescanned for each selected source and each hook. Large histories may therefore
be expensive; no enterprise-scale latency result or remote-aware cache is claimed.

These are agent tool-call interceptors, not installed Git pre-commit/pre-push hooks. Direct human
terminal commands, IDE operations and indirect command execution may bypass them. The hook's
exit code is meaningful in Claude Code's protocol; copying the script to another client's hook
configuration does not establish equivalent behavior.

## Overrides and local evidence

A permitted exception can use the hook's explicit override flag, for example:

```bash
LINTEL_OVERRIDE_SECRET=1 LINTEL_OVERRIDE_REASON="synthetic test fixture" git commit -m "test: add fixture"
```

The customer-data equivalent is `LINTEL_OVERRIDE_CUSTOMER_DATA=1`. Overrides can be supplied in
the hook environment or a leading command assignment; a token in a commit-message argument
must not count as authorization. The hook attempts to append an override event to its local
audit file. Reasons are useful context but are not a required mechanical precondition.

Audit records live under `.claude/runtime/audit/` for the current repository layout, with a
machine-global fallback under `~/.lintel/audit/`. They are ordinary files: an owner can edit them,
and a failed write can leave an action unrecorded. Use `/li:audit` or `/li:hooks-status` on a
supported full catalog installation to inspect evidence; do not treat absence of a record as
proof that an operation did not happen.

## Hook activation

The authoritative Claude Code registrations are in `hooks/hooks.json`. A Claude plugin install
registers those selected hooks. Other hook directories are opt-in and need both a reachable
script and host registration. The bare installer copies hook resources without automatically
merging the operator's settings. The Copilot repository kit installs no hook configuration.
[Getting started](getting-started.md#how-hook-activation-works) compares the routes.

Neither installing a pack nor selecting `compliance.mode: hard` automatically ports or registers
an executable hook. Pack compliance configuration and host hook activation are separate layers.

## Pack compliance fields

The schema of record is `lib/pack-schema.yaml`. A pack can declare a compliance mode, named gates,
audit-related settings and data-residency metadata. Resolve values using `resolve_pack_field`
instead of duplicating policy defaults in skills.

- `advisory` asks the workflow to surface gate outcomes without making them delivery blockers.
- `hard` asks the workflow to stop on a failing declared compliance gate.
- `off` turns off the pack's compliance workflow; it does not disable separately activated hooks.

The current baseline block scripts do not change their behavior based on the active pack's mode.
A data-residency label describes intent; it does not configure the model endpoint, provider
retention, region or network access. A strict requirement needs a corresponding control that
security/platform owners can verify outside the agent's prose.

An extension pack may include executable hooks or tools. Review their source, licenses,
permissions, host compatibility and failure behavior before enabling them. See
[pack defaults](concepts/pack-defaults.md) and [pack resolution](concepts/pack-resolver.md).

## Before a non-trivial action

The canonical session checklist in [AGENT-INSTRUCTIONS.md](../AGENT-INSTRUCTIONS.md) asks the
agent to establish task authority, customer-data handling, production impact, secrets exposure
and active pack requirements. Existing explicit authorization applies to its stated scope;
resolve a material uncertainty before the dependent action.

For Copilot, keep concise repository guidance in `.github/copilot-instructions.md` and relevant
path-scoped instructions. Other clients use their own entry files. Reconcile shared Lintel
workflow rules with the host's actual loading behavior; see [precedence](precedence.md).

## Incident handling

If sensitive material is exposed, stop further publication and follow your organisation's
incident process. Revoke or rotate exposed credentials through the authorized process, preserve
needed evidence, and make any history rewrite an explicit coordinated action. A local deletion
alone does not retract material already shared.

For a vulnerability in Lintel, use [SECURITY.md](../SECURITY.md). Capture a sanitized lesson and
review why the existing checks missed the problem.

## Enterprise evaluation

Review which requirements rely on agent cooperation, which have executable checks and which are
owned by platform controls. Test the actual Copilot client and environment; a passing installation
check does not prove compliant execution. Keep project-specific data handling, customer work and
private pack content in their approved environments.

Lintel does not provide egress filtering, secret rotation, immutable audit storage, platform role
management or incident response. Bundled third-party resources have retained notices in
[design-dna attribution](../skills/design-dna/ATTRIBUTION.md). See
[enterprise adoption](enterprise-adoption.md) for rollout evidence and ownership.
