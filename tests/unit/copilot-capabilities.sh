#!/usr/bin/env bash
# tag: copilot onboarding cli-tiers
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT/lib/cli-tiers.sh"
for cli in copilot copilot-cli copilot-app copilot-vscode copilot-cloud copilot-coding-agent; do
  [ "$(cli_tier_normalize "$cli")" = copilot ]
  [ "$(cli_tier_field "$cli" subagents)" = native ]
  [ "$(cli_tier_field "$cli" hooks_supported)" = false ]
  [ "$(cli_tier_field "$cli" tier)" = supported ]
done
[ "$(cli_tier_normalize unknown-host)" = other ]
[ "$(cli_tier_field unknown-host hooks_supported)" = false ]
echo 'PASS: Copilot surface aliases expose native delegation without claiming Lintel hooks or live-validated full tier'
