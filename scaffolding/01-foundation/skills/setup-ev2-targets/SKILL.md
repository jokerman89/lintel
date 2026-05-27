---
name: jstack-setup-ev2-targets
v1_alias: [jstack-setup-deploy]
description: Configure deploy targets for /release-deploy-ev2 — write targets, validate, register.
color: orange
tools: Read, Write, Edit, Bash
voice: internal
cli_support: [claude-code, codex, copilot]
---

# /setup-ev2-targets

One-time configuration skill for `/release-deploy-ev2`. Writes `~/.jstack/deploy-targets.yaml` declaring the named targets (staging, prod, canary, etc.) along with their trigger mechanism (GitHub Actions, Azure DevOps, custom script, manual link).

CLI-agnostic: this is config-writing only, no runtime browser or per-CLI dependency.

## When to use

- New repo where deploy hasn't been wired up to JStack yet
- Adding a new target (e.g. ramping from "staging only" to "staging + canary + prod")
- Migrating from one CI system to another (re-point targets)
- Validate existing config — `--check` runs without changes

## When NOT to use

- Deploy is one-time / manual / undocumented — JStack doesn't replace your CI; it triggers an existing pipeline
- You want to actually run a deploy — use `/release-deploy-ev2` (this skill just configures)

## Inputs

- Optional `--target <name>` — add or update a single target by name
- Optional `--check` — validate existing config, do not modify
- Optional `--from-repo` — try to detect deploy mechanism by reading `.github/workflows/`, `azure-pipelines.yml`, etc., and propose initial config

## Workflow

1. **Locate config file.** `~/.jstack/deploy-targets.yaml`. If absent: create with empty stub.
2. **Detection (if `--from-repo`).** Scan repo for known CI patterns:
   - `.github/workflows/deploy.yml` → propose `github_actions` mechanism
   - `azure-pipelines.yml` with `deploy` stage → propose `azure_devops`
   - `vercel.json`, `netlify.toml`, `fly.toml`, `render.yaml` → propose platform-specific
   - Custom shell script → propose `custom_command`
3. **Per-target interview.** For each target being added/updated, ask via AskUserQuestion:
   - Trigger mechanism (github_actions, azure_devops, vercel, netlify, fly, render, custom_command, manual_link)
   - Trigger details (workflow name, pipeline name, hook URL, command)
   - Health-check endpoint (for `/safe-deploy-ring` integration)
   - Auth requirement (always-confirm, per-batch, never-prompt)
4. **Validate.** Confirm the trigger mechanism is reachable (e.g. `gh workflow list` for GitHub Actions, network ping for hook URLs). Do NOT actually trigger anything.
5. **Write config.** Atomic write to `~/.jstack/deploy-targets.yaml`.
6. **Report registered targets.**

## Config schema

```yaml
# ~/.jstack/deploy-targets.yaml
version: 1
targets:
  staging:
    mechanism: github_actions
    workflow: deploy.yml
    workflow_inputs:
      target: staging
    health_check_url: https://staging.example.com/health
    auth: per-call    # always-confirm | per-call | per-batch | never-prompt
  prod:
    mechanism: github_actions
    workflow: deploy.yml
    workflow_inputs:
      target: prod
    health_check_url: https://app.example.com/health
    auth: always-confirm
  fly-staging:
    mechanism: custom_command
    command: "fly deploy --app myapp-staging"
    health_check_url: https://myapp-staging.fly.dev/health
    auth: per-call
```

## Report format

```
Setup deploy: ~/.jstack/deploy-targets.yaml

Detected from repo: GitHub Actions workflow `deploy.yml`
Targets registered: 2

| Target  | Mechanism       | Workflow    | Health check                     | Auth          |
|---------|-----------------|-------------|----------------------------------|---------------|
| staging | github_actions  | deploy.yml  | https://staging.example.com/...  | per-call      |
| prod    | github_actions  | deploy.yml  | https://app.example.com/...      | always-confirm|

Validation:
- staging workflow exists ✓ (gh workflow list)
- prod workflow exists ✓ (gh workflow list)
- staging health endpoint reachable ✓
- prod health endpoint reachable ✓

Ready: /release-deploy-ev2 --target staging | --target prod
```

## Compliance integration

- Config file itself is not sensitive (no secrets), but health-check URLs may reveal internal infra — file permissions chmod 600.
- Validation step makes READ-ONLY queries against CI systems. Per Layer 2 auto-mode rules: read queries are allowed.
- The actual deploy trigger is `/release-deploy-ev2`'s job, not this skill's. This skill only writes config.

## Voice tier note

`voice: internal`. Setup ops are engineering-internal.

## Failure modes

- **Config file unwriteable:** report exact path + permission issue.
- **Detection finds multiple plausible mechanisms:** ask via AskUserQuestion which one to use. Do not silently pick.
- **Validation can't reach health-check URL:** WARN, save config anyway (operator may be offline; URL valid for prod). Mark in report.
- **`gh` or `az` CLI not installed but a mechanism requires it:** report missing CLI + suggested install, save config anyway.
- **Target name conflicts with existing entry + `--target` not specified:** ask whether to overwrite. Do not auto-merge.

## Examples

**First-time setup from repo:**
```
> /setup-ev2-targets --from-repo
Detected: .github/workflows/deploy.yml
[AskUserQuestion: confirm mechanism per target]
✓ 2 targets registered: staging, prod. Validation passed.
```

**Add canary target to existing config:**
```
> /setup-ev2-targets --target canary
[Reads existing config. Interviews for canary specifics.]
✓ canary added. Total: 3 targets.
```

**Validate existing:**
```
> /setup-ev2-targets --check
✓ 3 targets, 3 workflows present, 3 health endpoints reachable.
```

## See also

- `/release-deploy-ev2` — uses the config written here
- `/safe-deploy-ring` — uses health_check_url from per-target config
- Layer 2 compliance — auth modes per target
