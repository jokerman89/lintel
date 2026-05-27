# Security Policy

## Reporting security issues

If you find a security issue in JStack itself (the scaffolding repo), please report it privately to:

**johannes.akerman@microsoft.com** (operator + JStack maintainer)

For MS-internal security issues, follow Microsoft's internal SDL incident response process.

Do not open public GitHub issues for security vulnerabilities.

## Scope

JStack is **scaffolding** — markdown + bash scripts that an AI CLI loads as a plugin. The security surface is:

1. **Plugin manifest content.** Per-CLI plugin.json files point at skills/agents directories. A malicious modification could redirect to attacker-controlled content.
2. **Hook scripts** (`hooks/shared/*/run.sh`). Bash scripts that run with operator privileges. A malicious modification could execute arbitrary code.
3. **bin/ scripts** (`bin/jstack-*`). Bash utilities operators install in PATH. Same risk.
4. **install/install.sh + install/install.ps1.** Installer scripts run with operator privileges.

## What JStack itself does NOT do (by design)

- ✗ No network calls in skill/agent execution (skill bodies are markdown instructions for the AI CLI, not network clients)
- ✗ No data exfiltration (JStack writes only locally, to operator-owned paths)
- ✗ No credential capture (no auth flows in JStack code)
- ✗ No telemetry sent externally (v3 telemetry is local-only, opt-in)

## What JStack DOES do that operators should review

- ✓ Hook scripts can run shell commands when triggered by the agent CLI's hook system (Claude Code settings.json hooks)
- ✓ Install scripts modify ~/.jstack/, ~/.claude/, or per-CLI config dirs
- ✓ `bin/jstack-scaffold` writes to target repo paths
- ✓ `bin/jstack-lessons-sync` reads/writes a git repo the operator configures

## Compliance constraints

JStack is for Microsoft Sweden CAIP-SE. These constraints apply:

- **No customer data anywhere in JStack repo.** Lessons learned must be sanitized before commit (no customer names, no project codenames, no PII).
- **No secrets in skill/agent bodies.** Examples use placeholders.
- **MS SSO authentication only** for any external service touched by JStack-invoked workflows.
- **Restricted-tier upstream content** (CC-BY-SA-4.0, etc.) is not vendored. v3 ships only operator-authored MIT content.

## Supported versions

| Version | Supported |
|---|---|
| v3.x | ✓ active development on `v3-dev` |
| v2.x | ✓ security fixes only |
| v1.x | ✗ unsupported — upgrade to v2 |

## Response timeline

Security reports acknowledged within 3 business days. Fix timeline depends on severity:
- Critical (RCE, secret leak): 72 hours
- High (privilege escalation, data exposure): 7 days
- Medium / Low: 30 days

## Acknowledgments

Security researchers who report responsibly will be credited in CHANGELOG.md (unless they prefer anonymous).
