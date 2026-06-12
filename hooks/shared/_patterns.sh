#!/usr/bin/env bash
# hooks/shared/_patterns.sh — detection patterns defined once, composed per hook.
#
# The secret + customer-data hooks previously each inlined their own copy of the
# same regexes (the audit's "dedupe" finding). Defining each regex once here
# removes that duplication WITHOUT flattening the deliberate tier difference:
#   - BLOCK hooks (secret-scan-block, customer-data-block) gate commits, so the
#     secret set uses only `tier1` — high-confidence patterns safe to block on.
#   - WARN hooks (no-secrets-in-edit, ...) use `all` — tier1 plus heuristics
#     (hardcoded-password, azure-shared-key) that can false-positive and so must
#     never block.
# Customer-PII uses one set everywhere, taking the STRONGEST variant of each
# regex (raise-the-weak-to-the-strong) — e.g. the name+case-id pattern now
# matches `case-id` and Swedish `ärende` for every consumer.
#
# NOTE: the customer patterns intentionally contain Swedish PII tells
# (`ärende` = case/ticket, `personnummer`, `ÅÄÖ` name letters) — functional
# detection of Swedish customer data, not prose. This file is allowlisted in
# tests/shape/no-swedish.sh for exactly that reason.
#
# Idempotent source. Safe under `set -euo pipefail`.
command -v scan_secrets >/dev/null 2>&1 && return 0 2>/dev/null

# ── secret patterns (name<TAB>regex) ─────────────────────────────────────────
# tier1 = high-confidence, safe to BLOCK on.  all = tier1 + WARN-only heuristics.
_secret_pats() {
  cat <<'P'
github-token	gh[opur]_[A-Za-z0-9]{36}
github-pat	github_pat_[A-Za-z0-9_]{22,}
openai-key	sk-(proj-)?[A-Za-z0-9_-]{20,}
anthropic-key	sk-ant-[A-Za-z0-9_-]{24,}
slack-token	xox[abposr]-[A-Za-z0-9-]{10,}
aws-access-key	(AKIA|ASIA)[0-9A-Z]{16}
google-api-key	AIza[0-9A-Za-z_-]{35}
stripe-key	sk_(live|test)_[A-Za-z0-9]{20,}
gitlab-pat	glpat-[A-Za-z0-9_-]{20,}
azure-account-key	AccountKey=[A-Za-z0-9+/=]{40,}
private-key	\-+BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY\-+
P
  [ "${1:-all}" = "all" ] && cat <<'P'
azure-shared-key	SharedAccessKey=
hardcoded-password	password\s*[=:]\s*"[^"]{8,}"
P
  return 0
}

# ── customer-PII patterns (name<TAB>regex) ───────────────────────────────────
_customer_pats() {
  cat <<'P'
email	\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b
phone	\+?[0-9]{1,3}[ -]?\(?[0-9]{2,4}\)?[ -]?[0-9]{3,4}[ -]?[0-9]{3,4}
personnummer	\b[0-9]{6}[-+][0-9]{4}\b
name-with-case-id	\b[A-ZÅÄÖ][a-zåäö]+ [A-ZÅÄÖ][a-zåäö]+,?\s+(case|kase|case-id|ärende)\s*#?[0-9]+
P
  return 0
}

# _scan_pats <pattern-lines> <text> → comma-joined names of patterns that hit.
_scan_pats() {
  local pats="$1" text="$2" name re; local -a hits=()
  while IFS=$'\t' read -r name re; do
    [ -z "$name" ] && continue
    printf '%s' "$text" | grep -qE "$re" && hits+=("$name")
  done <<< "$pats"
  [ "${#hits[@]}" -eq 0 ] && return 0
  local IFS=,; printf '%s' "${hits[*]}"
}

# scan_secrets <tier> <text>  → comma-joined secret hits (tier: tier1 | all)
scan_secrets() { _scan_pats "$(_secret_pats "${1:-all}")" "${2:-}"; }
# scan_customer <text>        → comma-joined customer-PII hits
scan_customer() { _scan_pats "$(_customer_pats)" "${1:-}"; }
