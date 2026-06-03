#!/usr/bin/env bash
# no-secrets-in-edit — Lintel warn-only hook
# Scans Edit/Write tool payload for secret patterns.

set -euo pipefail

PAYLOAD="${1:-}"
[ -z "$PAYLOAD" ] && exit 0

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

patterns_hit=()

# GitHub tokens
echo "$PAYLOAD" | grep -qE 'gh[opur]_[A-Za-z0-9]{36}' && patterns_hit+=("github-token")
# OpenAI
echo "$PAYLOAD" | grep -qE 'sk-[A-Za-z0-9]{32,}' && patterns_hit+=("openai-key")
# Slack
echo "$PAYLOAD" | grep -qE 'xox[abposr]-[A-Za-z0-9-]{10,}' && patterns_hit+=("slack-token")
# AWS
echo "$PAYLOAD" | grep -qE 'AKIA[0-9A-Z]{16}' && patterns_hit+=("aws-access-key")
# Azure connection strings
echo "$PAYLOAD" | grep -qE 'AccountKey=[A-Za-z0-9+/=]{40,}' && patterns_hit+=("azure-account-key")
echo "$PAYLOAD" | grep -qE 'SharedAccessKey=' && patterns_hit+=("azure-shared-key")
# Anthropic
echo "$PAYLOAD" | grep -qE 'sk-ant-[A-Za-z0-9-]{30,}' && patterns_hit+=("anthropic-key")
# Private keys
echo "$PAYLOAD" | grep -qE '\-+BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY\-+' && patterns_hit+=("private-key")
# Hardcoded password (heuristic, double-quoted)
echo "$PAYLOAD" | grep -qE 'password\s*[=:]\s*"[^"]{8,}"' && patterns_hit+=("hardcoded-password")

if [ ${#patterns_hit[@]} -gt 0 ]; then
  joined=$(IFS=,; echo "${patterns_hit[*]}")
  audit_log "hooks" "no_secrets_in_edit" "hook=no-secrets-in-edit" "tier=warn" "patterns_matched=$joined"
  echo "WARN [Lintel hook]: secret pattern detected in payload — $joined"
  echo "WARN: If this is a real secret, abort + use env var or secret manager. (warn-only; secret-scan-block fires at commit.)"
fi

exit 0
