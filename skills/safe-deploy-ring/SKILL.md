---
name: li-safe-deploy-ring
layer: foundation
v1_alias: [li-canary]
description: Gate a deployed feature behind a percentage rollout — ramp up, monitor, abort safe.
color: orange
tools: Read, Bash, Edit
voice: internal
cli_support: [claude-code, codex]
---

# /safe-deploy-ring

Manage a percentage-based rollout of a feature already shipped behind a flag. Ramps from 0% → 1% → 10% → 50% → 100% across explicit operator approval gates, with health checks between steps.

Distinct from `/release-deploy-ev2 --canary`: that one is a one-shot deploy at a fixed percentage. This skill is the multi-step ramp lifecycle.

Per Layer 2: every percentage change is a production-mutation requiring explicit per-call auth.

## When to use

- Feature is behind a flag in production, want to expand exposure carefully
- A `/release-deploy-ev2 --canary` landed at 10%; now you want to ramp
- Suspected risk — gradual expansion is safer than instant 100%
- Rollback dry-run — start at 100%, ramp DOWN to test recovery path

## When NOT to use

- Feature isn't flagged in code — `/safe-deploy-ring` operates on flags, not infrastructure
- Single-tenant deploy with no traffic split capability — use `/release-deploy-ev2` directly
- Emergency rollback — use a direct flag-set command, not the ramped lifecycle

## Inputs

- Required `--flag <name>` — feature flag identifier in the repo's flag system
- Required `--target <percentage>` — desired final exposure (e.g. 100, 50, 0)
- Optional `--start <percentage>` — current exposure (skill auto-detects from flag system if omitted)
- Optional `--steps <list>` — explicit ramp steps (default: `1,10,50,100` clipped to target)
- Optional `--health-check <cmd>` — command to verify health between steps (default: read from `~/.lintel/safe-deploy-ring.yaml`)
- Optional `--soak-minutes <N>` — wait N minutes between ramp steps (default: 15)

## Workflow

1. **Flag system detection.** Read repo for flag library (GrowthBook, LaunchDarkly, ConfigCat, in-house). Locate the named flag.
2. **Compliance gate.** Layer 2 per-call auth confirmation: "About to ramp <flag> from <X>% to <step>%. Confirm?" Operator confirms FOR EACH STEP — auth does not extend across steps.
3. **Set flag to next step.** Via flag-system CLI/API.
4. **Soak.** Wait `--soak-minutes`. During soak, log health-check output every minute to audit.
5. **Health check.** Run `--health-check` command. Default checks: error rate, p95 latency, key business metric (configurable per repo).
6. **Decision gate.** If health passes: advance to next step (return to step 2). If fails: AUTO-ROLLBACK to previous step, surface failure.
7. **Loop until target reached.** Or until operator aborts.
8. **Report.** Full ramp timeline, health metrics per step, final state.

## Report format

```
Canary: feature-new-billing

Flag system: GrowthBook
Initial state: 10% (set by /release-deploy-ev2 at 14:22)
Target: 100%
Ramp plan: 10% → 50% → 100%
Soak: 15min between steps

## Ramp timeline

[14:22] Step 0: 10% (initial state)
[14:23] Health check: error_rate 0.4%, p95 234ms. PASS.
[14:38] Operator confirmed 50% advance.
[14:38] Step 1: 50% (set via gb-cli)
[14:39] Health check: error_rate 0.4%, p95 241ms. PASS.
[14:54] Operator confirmed 100% advance.
[14:54] Step 2: 100% (set via gb-cli)
[14:55] Health check: error_rate 0.5%, p95 248ms. PASS.

## Final state
Flag: feature-new-billing = 100%
Duration: 33 min total
Audit: ~/.lintel/audit/canary-feature-new-billing-20260527.jsonl
```

## Compliance integration

- Layer 2 production-mutation: per-call auth for EVERY step. Confirmation in chat is the auth; logged to audit.
- Health-check failure auto-rollback IS allowed without re-auth (rollback is the safe direction).
- Flag-system credentials read from `~/.lintel/secrets/<system>.env` or env vars — never from prompt.
- Audit trail written to `~/.lintel/audit/canary-<flag>-<date>.jsonl`. Tamper-evident: append-only, one event per ramp step + health check.

## Voice tier note

`voice: internal`. Production ops are engineering-internal.

## Failure modes

- **Flag system not detected:** report + ask operator to configure `~/.lintel/safe-deploy-ring.yaml`. Do not proceed.
- **Health check command not configured:** STOP — refuse to ramp without a health signal. Surface what to configure.
- **Health check fails at step N:** AUTO-ROLLBACK to step N-1. Report failure with metrics. Do not auto-advance again.
- **Operator declines mid-ramp at a step gate:** stop cleanly at current step. Flag stays where it is. Report partial-ramp state explicitly.
- **Flag-system API unreachable:** retry once. Persistent failure: stop at current step. Operator owns next move (manual via console).
- **Soak interrupted (machine sleep, ctrl-c):** report partial state. Re-running `/safe-deploy-ring` from current step is safe (idempotent — reads current flag value).

## Examples

**Standard ramp to 100%:**
```
> /safe-deploy-ring --flag feature-new-billing --target 100
[Per-step confirmation. 33 min elapsed.]
✓ Flag at 100%. No rollbacks needed.
```

**Ramp down (rollback rehearsal):**
```
> /safe-deploy-ring --flag feature-new-billing --target 0 --steps 100,50,10,0
[Per-step confirmation, soak 5min for rehearsal]
✓ Flag at 0%. Rollback path validated.
```

**Aborted at 50%:**
```
> /safe-deploy-ring --flag feature-new-billing --target 100
[Step 50% confirmed. Step 100% declined by operator.]
✗ Stopped at 50%. Flag stable. Re-run /safe-deploy-ring to continue when ready.
```

**Health failure auto-rollback:**
```
> /safe-deploy-ring --flag feature-new-billing --target 100
[Step 50% set. Health check 5 minutes in: error_rate spiked to 2.3%.]
✗ AUTO-ROLLBACK to 10%. Operator: investigate before retry.
```

## See also

- `/release-deploy-ev2 --canary <pct>` — initial deploy with canary
- `/investigate` — when health fails and rollback triggers
- `/qa-only` — pre-canary verification
- Layer 2 compliance — production-mutation per-call auth requirement
