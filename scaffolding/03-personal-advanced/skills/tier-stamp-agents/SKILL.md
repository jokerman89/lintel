---
name: jstack-tier-stamp-agents
description: Stamp agents with license tier (permissive/restricted) — enforces 5-level precedence model.
color: orange
tools: Read, Write, Edit, Bash, Glob, Grep
voice: internal
cli_support: [claude-code, codex]
---

# /tier-stamp-agents

Scans agents in scope, classifies each by upstream license (permissive vs restricted), stamps the frontmatter accordingly, and verifies the 5-level precedence model integrity (Operator pin → Repo-level → Promoted/tier-stamped → User-global → Fallback).

The tier-stamp determines what an agent is allowed to do:
- **permissive**: MIT/Apache — safe to bundle into MS-internal MIT repos
- **restricted**: CC-BY-SA / no-license — safe to INVOKE, NOT safe to copy into MS-internal repos (attribution + share-alike implications)

## When to use

- Onboarding agents from upstream marketplace (gstack, wshobson, Trail of Bits, GSD, Anthropic-plugins) — stamp before activation
- Periodic audit — re-scan to catch agents added without stamping
- License-policy change — re-classify under new policy
- Pre-`/ship` for any release that bundles agents

## When NOT to use

- Agent written from scratch by operator — license is operator-controlled, no stamp needed
- Internal-tooling agent never distributed — stamp is for distribution scope
- Existing stamped agent with current source — re-stamp only on source change

## Inputs

- Optional `--scope <path>` — directory to scan (default: `~/.claude/agents/` + repo's `.claude/agents/`)
- Optional `--policy <yaml>` — license-policy override (default: `~/.jstack/license-policy.yaml`)
- Optional `--dry-run` — report what would be stamped, do not modify
- Optional `--strict` — fail-on-restricted: refuses agents that would be restricted-tier (use for MS-internal-bundled releases)

## Workflow

1. **Locate agents.** Glob `**/*.md` in scope dirs. Filter to files with agent frontmatter.
2. **Read license source.** For each agent, determine origin:
   - Check agent frontmatter for `source:` / `upstream:`
   - Cross-reference `~/.jstack/upstream-sources.yaml` (the 8 sources with SHA pins)
   - If no source: mark `origin: operator-authored`
3. **Classify per policy:**
   - MIT, Apache-2.0, BSD-2/3, ISC → **permissive**
   - CC-BY-SA-4.0, GPL-3.0, AGPL-3.0 → **restricted**
   - No-license, source-available, custom non-OSI → **restricted**
   - operator-authored (no upstream) → operator's `LICENSE` file determines (default: MIT in MS-internal repos)
4. **Stamp frontmatter.** Add or update:
   ```yaml
   tier: permissive | restricted
   tier_source: <upstream-url-or-operator>
   tier_stamped_at: <iso-timestamp>
   tier_stamped_by: jstack-tier-stamp-agents
   ```
5. **Precedence integrity check.** Walk the 5 levels (operator pin → repo → promoted → user-global → fallback). For each agent name with multiple definitions: verify precedence is honored.
6. **Strict-mode handling.** If `--strict` AND any restricted-tier agent in scope: exit non-zero, list the offenders.
7. **Audit log.** Every stamp event to `~/.jstack/audit/tier-stamp.jsonl`.
8. **Report.**

## Report format

```
Tier stamp: scope=~/.claude/agents/ + .claude/agents/

Policy: default (~/.jstack/license-policy.yaml — last updated 2026-05-15)
Mode: live (use --dry-run to preview)

## Scanned: 47 agents

## Stamping results
| Tier         | Count | Examples                                    |
|--------------|-------|---------------------------------------------|
| permissive   | 38    | CodeReviewer, SecurityAuditor, Architect... |
| restricted   | 6     | trail-of-bits/safe-code-review, ...         |
| operator     | 3     | jstack-custom-pair-agent, ...               |

## Precedence integrity
✓ 5-level walk clean — no shadow/override surprises
⚠ 1 name collision: "CodeReviewer" exists at user-global AND repo-level
   → repo-level wins per precedence; surfaced for awareness

## Strict-mode check (--strict not set)
6 restricted-tier agents in scope. Bundleable to MS-internal repo: NO (use --invoke-only).
For MIT-internal distribution: would need to drop the 6 OR convert to permissive sources.

## Audit
47 stamp events logged to ~/.jstack/audit/tier-stamp.jsonl
```

## Compliance integration

- Implements the 5-level precedence model from JStack design.
- A restricted-tier agent CANNOT be bundled into MS-internal MIT repos — `/ship` reads tier-stamp + license-class of repo + refuses on mismatch.
- Stamp + audit trail is load-bearing for external-distribution compliance review.

## Voice tier note

`voice: internal`. Tier-stamping is engineering-internal lifecycle.

## Failure modes

- **Agent has no upstream source declared:** mark `origin: operator-authored`, prompt operator to add `source:` frontmatter if it actually came from upstream.
- **License-policy YAML unreadable:** fall back to built-in defaults, warn.
- **Stamp would overwrite operator-set tier:** ask via AskUserQuestion. Do not auto-overwrite operator decisions.
- **Conflict in precedence (e.g. repo agent and user-global both call themselves "primary"):** surface conflict, name the winner per precedence, ask whether to rename one.
- **`--strict` exit non-zero:** suitable for CI; clearly identify offenders.

## Examples

**Full audit:**
```
> /tier-stamp-agents
[Scans all agent dirs, classifies, stamps]
✓ 47 agents stamped. 38 permissive, 6 restricted, 3 operator. 1 precedence collision noted.
```

**Dry run:**
```
> /tier-stamp-agents --dry-run
[Reports what would change without writing]
3 agents would be newly stamped. 2 would update existing stamps.
```

**Strict mode pre-release:**
```
> /tier-stamp-agents --strict --scope ./.claude/agents/
[Fails if any restricted in repo's bundled scope]
✗ 2 restricted-tier agents in scope. Bundle is not MS-internal-safe.
```

## See also

- `~/.jstack/license-policy.yaml` — operator-configurable policy
- `~/.jstack/upstream-sources.yaml` — the 8 upstream-source SHA-pinned origins
- 5-level precedence model — designed in JStack vision doc
- `/ship` — reads tier-stamp before bundle/release
- `/health` — verifies stamping is current
