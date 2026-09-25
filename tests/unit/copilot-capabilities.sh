#!/usr/bin/env bash
# tag: copilot onboarding cli-tiers
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT/lib/cli-tiers.sh"
for cli in copilot-cli copilot-app copilot-vscode copilot-cloud; do
  [ "$(cli_tier_normalize "$cli")" = "$cli" ]
  [ "$(cli_tier_field "$cli" hooks_supported)" = false ]
  [ "$(cli_tier_field "$cli" tier)" = supported ]
done
[ "$(cli_tier_normalize copilot)" = copilot-cli ]
[ "$(cli_tier_normalize copilot-coding-agent)" = copilot-cloud ]
[ "$(cli_tier_field copilot-cli subagents)" = sequenced ]
[ "$(cli_tier_field copilot-cloud subagents)" = none ]
[ "$(cli_tier_normalize unknown-host)" = other ]
[ "$(cli_tier_field unknown-host hooks_supported)" = false ]
echo 'PASS: Copilot surfaces stay separate; compatibility hints never claim live delegation, installed hooks or full validation'
