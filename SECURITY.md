# Security Policy

## Reporting security issues

If you find a security issue in Lintel itself (the scaffolding repo), please report it privately by
**opening a private security advisory on the GitHub repository**
(`Security` tab → `Report a vulnerability`). This reaches the project maintainers without disclosing
the issue publicly.

If your active pack defines its own incident-response process, follow that as well.

Do not open public GitHub issues for security vulnerabilities.

## Scope

Lintel is **scaffolding** — markdown + bash scripts that an AI CLI loads as a plugin. The security surface is:

1. **Plugin manifest content.** Per-CLI plugin.json files point at skills/agents directories. A malicious modification could redirect to attacker-controlled content.
2. **Hook scripts** (`hooks/shared/*/run.sh`). Bash scripts that run with operator privileges. A malicious modification could execute arbitrary code.
3. **bin/ scripts** (`bin/li-*`). Bash utilities operators install in PATH. Same risk.
4. **install/install.sh + install/install.ps1.** Installer scripts run with operator privileges.

## What Lintel itself does NOT do (by design)

- ✗ No network calls in skill/agent execution (skill bodies are markdown instructions for the AI CLI, not network clients)
- ✗ No data exfiltration (Lintel writes only locally, to operator-owned paths)
- ✗ No credential capture (no auth flows in Lintel code)
- ✗ No telemetry sent externally (any usage logging is local-only and opt-in)

## What Lintel DOES do that operators should review

- ✓ Hook scripts can run shell commands when triggered by the agent CLI's hook system (Claude Code settings.json hooks)
- ✓ Install scripts modify ~/.lintel/, ~/.claude/, or per-CLI config dirs
- ✓ `bin/li-scaffold` writes to target repo paths
- ✓ `bin/li-lessons-sync` reads/writes a git repo the operator configures

## Compliance constraints

These constraints apply to the Lintel repo itself (a company pack may add stricter ones):

- **No customer data anywhere in Lintel repo.** Lessons learned must be sanitized before commit (no customer names, no project codenames, no PII).
- **No secrets in skill/agent bodies.** Examples use placeholders.
- **Authentication policy is pack-defined** — the neutral spine mandates none; a company pack may require SSO or vendor restrictions.
- **Only operator-authored content is vendored** — no restricted-tier upstream (CC-BY-SA-4.0, etc.); Lintel ships MIT throughout.

## Supported versions

| Version | Supported |
|---|---|
| 5.7.x | ✓ supported — current shipping line |
| < 5.7 | ⚠ best-effort — upgrade to the current line for fixes |
| ≤ 4.x | ✗ unsupported — upgrade to the current line |

## Response timeline

Security reports acknowledged within 3 business days. Fix timeline depends on severity:
- Critical (RCE, secret leak): 72 hours
- High (privilege escalation, data exposure): 7 days
- Medium / Low: 30 days

## Acknowledgments

Security researchers who report responsibly will be credited in CHANGELOG.md (unless they prefer anonymous).
