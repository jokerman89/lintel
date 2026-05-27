---
name: jstack-release-deploy-ev2
v1_alias: [jstack-land-and-deploy]
description: /release-ev2 + deploy. Adds post-merge deploy trigger. Requires explicit per-call auth.
color: red
tools: Read, Bash, Edit
voice: internal
cli_support: [claude-code, codex]
---

# /release-deploy-ev2

Extension of `/release-ev2` that also triggers a deploy after PR merges. Higher-stakes — production-adjacent. Per JStack Layer 2 compliance: deploy-pipeline triggers REQUIRE explicit per-call authorization, even in auto-mode.

## When to use

- Branch is feature-complete + reviewed + ready to merge AND deploy
- The deploy is non-blocking for downstream work (otherwise: ship first, deploy later)
- Operator has explicit per-call auth to trigger production deploy

## When NOT to use

- No deploy pipeline configured for the repo — use `/release-ev2` only
- Deploy needs human approval gate even after merge — use `/release-ev2`, trigger deploy manually
- Production data risk — re-evaluate scope before deploying

## Inputs

- `--target <name>` — deploy target (staging, prod, canary, etc.) — REQUIRED
- `--wait` — block until deploy completes (default: fire-and-forget after CI verifies)
- `--canary <percentage>` — partial rollout (default: full)

## Workflow

1. **Run /release-ev2** — full ship gauntlet (review check, sanity, squash, push, PR).
2. **Wait for PR merge** — block on `gh pr view <pr> --json mergedAt -q '.mergedAt'`. Default timeout 30 min. If PR isn't merged (reviewer pending): report + exit without deploy.
3. **Authorization check** — per Layer 2: deploy is per-call-auth. Even though `/release-deploy-ev2` was invoked with intent, surface "About to trigger `<target>` deploy. Confirm?" Operator confirms explicitly.
4. **Trigger deploy** — invoke the repo's configured deploy mechanism:
   - GitHub Actions: `gh workflow run deploy.yml --ref main --field target=<target>`
   - Azure DevOps: `az pipelines run --name deploy --branch main --variables target=<target>`
   - Custom: read from `~/.jstack/deploy-targets.yaml` (per-repo config)
5. **Optional wait** — if `--wait`: poll deploy status until complete or 30min timeout.
6. **Report deploy URL + status** to operator.

## Report format

```
Land & Deploy: <branch>

✓ Ship complete: PR #N opened + merged at <time>
✓ Authorization: explicit per-call confirmed
✓ Deploy triggered: GitHub Actions run #M
  Target: staging
  Canary: 100% (full rollout)
  Status: in_progress (1m 23s elapsed)
  URL: https://github.com/azureflipper/jokerman-session-setup/actions/runs/M

[--wait: blocks until status=completed]
```

## Compliance integration

- Deploy is a Layer 2 production-mutation. Per-call auth is **mandatory** — `/release-deploy-ev2` invocation alone is not auth. The Step 3 explicit confirmation IS the auth.
- For Layer 3 governance: log the deploy trigger to audit trail (`~/.jstack/audit/deploys.jsonl`).

## Voice tier note

`voice: internal`. Deploy ops is engineering-internal.

## Failure modes

- **Ship failed:** abort, don't deploy a broken state.
- **PR not merged after timeout:** report + exit. Deploy never runs.
- **Operator declines explicit auth at Step 3:** ship completed but no deploy. Report this clearly — partial state is OK here (PR merged, deploy deferred).
- **Deploy trigger fails (network, perms, workflow not found):** report failure mode, surface workflow URL for manual trigger.
- **`--wait` timeout:** report current status, exit. Operator monitors via URL.

## Examples

**Staging deploy:**
```
> /release-deploy-ev2 --target staging
[ship runs, PR merged]
> About to trigger staging deploy. Confirm?
[operator: yes]
✓ Deploy triggered: run #M, in_progress
```

**Production with canary:**
```
> /release-deploy-ev2 --target prod --canary 10
[ship runs, PR merged]
> About to trigger prod deploy at 10% canary. Confirm?
[operator: yes]
✓ Deploy triggered: 10% rollout, monitoring URL: <url>
```

**Operator declines:**
```
> /release-deploy-ev2 --target prod
[ship runs, PR merged]
> About to trigger prod deploy. Confirm?
[operator: no]
PR merged but deploy deferred. Operator owns the next step.
```

## See also

- `/release-ev2` — ship without deploy
- `/setup-ev2-targets` — configure deploy targets in `~/.jstack/deploy-targets.yaml`
- Layer 2 compliance — production-mutation auth requirement
