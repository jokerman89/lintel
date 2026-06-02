---
name: sc-auth-flow
layer: foundation
description: SC sub-skill — auth design with security review verdict. Dispatches to JWTSecurityReviewer + SecurityAuditor agents.
color: red
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are SC-AUTH-FLOW — the workflow that produces an auth design + security review.

## What this skill does

Reads auth intent (login / SSO integration / service-to-service / API key flow). Spawns `JWTSecurityReviewer` (when JWT-shaped) or `SecurityAuditor` (otherwise) for the design + review. Produces auth-flow document with sequence diagram, token lifetimes, refresh strategy, revocation path, MFA posture.

## When to use

- SC full pass auth_flow_locked checkpoint
- Single action `/li:sc single --action auth-flow`
- New auth integration (OAuth2/OIDC/SAML/etc.)
- Pre-customer-engagement auth posture review

## When NOT to use

- Pure password reset / forgot-password (existing auth, no flow change)
- Service-to-service mTLS at infrastructure level — that's `/li:dh` (v4.4)

## Workflow

### Step 1 — Read auth intent

```bash
auth_intent="${1:-${AUTH_INTENT:-from .lintel/state/sc/auth-intent.md}}"
auth_kind=$(detect_auth_kind "$auth_intent")  # jwt | oauth2 | oidc | saml | api-key | mtls
```

### Step 2 — Spawn agent based on auth_kind

```bash
case "$auth_kind" in
  jwt)
    primary_agent="JWTSecurityReviewer"
    ;;
  *)
    primary_agent="SecurityAuditor"
    ;;
esac

brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Design ${auth_kind} auth flow for declared intent + produce security review
context_pointers:
  - $auth_intent
  - existing auth files (if present)
constraints:
  - sequence diagram per flow (login / refresh / revoke / step-up MFA)
  - token lifetimes documented + justified
  - refresh strategy + revocation path
  - MFA posture per role
  - per-step security check (rate limit, replay protection, session fixation)
acceptance:
  - auth-flow design + security review verdict (PASS | PASS_WITH_CONCERNS | FAIL)
  - per-finding remediation per FAIL or CONCERN
EOF

/li:brief-forge subagent_spawn sc-auth-flow "$primary_agent" brief "$brief_file"
```

### Step 3 — Cross-check with general SecurityAuditor (always)

```bash
if [ "$primary_agent" != "SecurityAuditor" ]; then
  cross_brief=$(mktemp)
  cat > "$cross_brief" <<EOF
task: Cross-check auth flow design for non-${auth_kind}-specific concerns
context_pointers:
  - .lintel/state/sc/auth-flow-design.md
constraints:
  - rate limiting + lockout policy
  - audit-log coverage of auth events
  - cross-site request forgery posture
acceptance:
  - per-concern verdict
EOF
  /li:brief-forge subagent_spawn sc-auth-flow SecurityAuditor brief "$cross_brief"
fi
```

### Step 4 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/sc/auth-flow-$ts.md"
{
  echo "# Auth flow — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Kind: $auth_kind"
  echo ""
  echo "## Design"
  cat .lintel/state/sc/auth-flow-design.md
  echo ""
  echo "## Security review"
  cat .lintel/state/sc/auth-security-review.md
} > "$out"

printf '{"ts":"%s","kind":"sc_auth_flow","auth_kind":"%s","review_verdict":"%s","operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$auth_kind" "$verdict" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/sc-decisions.jsonl"
```

## Status protocol

- **DONE** — design + review verdict PASS
- **DONE_WITH_CONCERNS** — verdict PASS_WITH_CONCERNS (operator accepts)
- **BLOCKED** — verdict FAIL (must re-loop)
- **NEEDS_CONTEXT** — auth intent unclear

## Integration

**Reads:** auth intent, existing auth files
**Writes:** `.lintel/state/sc/auth-flow-<ts>.md`, audit JSONL
**Dispatches to:** JWTSecurityReviewer (JWT) OR SecurityAuditor (else), cross-checks with SecurityAuditor

## Anti-patterns

- **Skipping the cross-check** — JWT-specific review is necessary but insufficient
- **Single sequence diagram (login only)** — refresh, revoke, MFA step-up all need diagrams
- **Hardcoding token lifetime** — justify per threat model
- **Curating auth patterns** — agents produce, this skill orchestrates (L-001)
