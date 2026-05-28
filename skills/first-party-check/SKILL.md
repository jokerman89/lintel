---
name: jstack-first-party-check
layer: ms-team
description: Scan for non-first-party dependencies and surface MS alternatives — "first-party first" enforcement.
color: yellow
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /first-party-check

Scans the repo (or a specific diff) for third-party dependencies that have a viable Microsoft first-party alternative. Surfaces them, names the MS equivalent, and asks whether the choice was deliberate. The rule isn't "always pick MS"; it's "never pick non-MS without considering MS".

Implements one of the 7 on-demand compliance items (Item 2). Run by `/onecs-check` automatically; also runnable standalone.

## When to use

- Pre-`/release-ev2` on a diff that adds new dependencies
- After a 3rd-party SDK integration — verify MS alternative was at least considered
- Periodic project hygiene (quarterly review of `package.json` / `requirements.txt`)
- New module setup — surface MS options early

## When NOT to use

- Engineering-internal tooling that has no first-party MS option — skip
- Diff that doesn't change dependencies — wasted cycles
- After conscious documented decision to use non-MS — re-running surfaces noise

## Inputs

- Optional `--scope <path>` — restrict scan to a subdirectory
- Optional `--diff <ref>` — restrict to deps added since ref (default: full scan)
- Optional `--strict` — exit non-zero if any flagged dependency lacks documented justification

## Workflow

1. **Detect manifest files.** `package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`. For each: list dependencies.
2. **Cross-reference MS-alternative table.** Built-in mapping for common dependencies:
   - `@auth0/auth0-react` → Microsoft Entra ID (formerly Azure AD)
   - `firebase-admin` → Azure Cosmos DB / Functions / Identity
   - `aws-sdk` → Azure SDK (depends on service)
   - `openai` → Azure OpenAI
   - `anthropic` → Azure AI Foundry (in MS-CAIP context)
   - `stripe` → for MS-internal: depends on use case; for product code consider MS commerce
   - `datadog`, `new-relic` → Azure Monitor / Application Insights
   - `sentry` → Azure Application Insights
   - `pagerduty` → Azure Service Health / Microsoft Graph alerts
   - `slack-api` → Microsoft Teams / Graph
   - `mailgun`, `sendgrid` → Azure Communication Services
   - `cloudflare` → Azure Front Door / CDN
   - (More in `~/.jstack/first-party-alternatives.yaml`, operator-extendable)
3. **For each flag:** check git history / repo docs for a documented decision (commit message rationale, ADR, README note). If absent: mark NEEDS_JUSTIFICATION.
4. **Compliance gate hint:** if running inside `/onecs-check`: emit structured output for aggregation.
5. **Report.**

## Report format

```
First-party check: jokerman-session-setup

Scope: full repo, all manifests
Scan duration: 0.6s
Manifests checked: package.json (none — this is a docs repo)

## Flagged dependencies (0)
[No flagged deps in this repo — it's a documentation scaffolding, no runtime deps]

---

Example output on a real codebase:

## Flagged dependencies (3)

[NEEDS_JUSTIFICATION] @auth0/auth0-react ^2.2.4 (package.json:dependencies)
   First-party alternative: Microsoft Entra ID via @azure/msal-react
   Decision documented: no
   Recommendation: either justify in commit message / ADR, or migrate

[DOCUMENTED] firebase-admin ^11.5.0 (package.json:dependencies)
   First-party alternative: Azure Cosmos DB SDK + Azure Functions
   Decision documented: yes (commit f19d388 — "firebase chosen for legacy mobile client compat, migration to Azure planned Phase 2")
   No action — decision tracked

[NEEDS_JUSTIFICATION] sentry @sentry/node ^7.30.0 (package.json:dependencies)
   First-party alternative: Azure Application Insights
   Decision documented: no
   Recommendation: justify or migrate

## Verdict
2 NEEDS_JUSTIFICATION dependencies. Document decision OR migrate.
```

## Compliance integration

- Implements Item 2 of the 7 on-demand compliance items.
- A NEEDS_JUSTIFICATION dep in `--strict` mode + downstream `/release-ev2`: BLOCKS until documented.
- Output structured-emitted to `/onecs-check` when run as part of aggregate check.
- Operator can add to `~/.jstack/first-party-alternatives.yaml` for project-specific mappings.

## Voice tier note

`voice: internal`. Compliance scan is engineering-internal.

## Failure modes

- **No manifest files found:** report scope is non-applicable, exit cleanly.
- **Manifest unparseable:** report which file + line, skip, continue with others.
- **Alternative mapping out of date:** mappings are heuristic. Operator can override via `~/.jstack/first-party-alternatives.yaml`. WARN when the built-in mapping is stale.
- **`--strict` mode + open NEEDS_JUSTIFICATION:** non-zero exit. Suitable for CI use.

## Examples

**Repo scan:**
```
> /first-party-check
[3 flagged, 1 documented, 2 NEEDS_JUSTIFICATION]
Document or migrate the 2 flagged. Add justification commit or ADR.
```

**Diff-scoped:**
```
> /first-party-check --diff main
[Scans only deps added since main]
1 new flagged dep (sentry). Justify before /release-ev2.
```

**Strict CI mode:**
```
> /first-party-check --strict
[Exits 1 if NEEDS_JUSTIFICATION present]
Use in CI to enforce first-party-first.
```

## See also

- `/onecs-check` — runs this skill as Item 2 of the 7
- `~/.jstack/first-party-alternatives.yaml` — operator-extendable mappings
- Item 2 in ON-DEMAND-RULES.md (Phase 6) — the source rule
- `/learn` — record a documented decision so future scans pick it up
