#!/usr/bin/env bash
# jstack verify.sh — install + structure diagnostic
#
# 10 subcommands:
#   --frontmatter   validate skill + agent frontmatter
#   --cli-matrix    print CLI support matrix
#   --layers        validate 4-layer scaffolding structure
#   --hooks         check hook activation state (symlinks)
#   --voice         check voice corpus + calibration state
#   --compliance    check compliance docs present
#   --upstream      check upstream-sources.yaml + tier-stamp state
#   --counts        summary counts (skills/agents/hooks)
#   --tier-stamps   check agent tier-stamping
#   --all           run everything + aggregate verdict
#
# Default (no flag) is --counts.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCES_FILE="$SCRIPT_DIR/upstream-sources.yaml"
JSTACK_HOME="${JSTACK_HOME:-$HOME/.jstack}"

c_reset='\033[0m'; c_bold='\033[1m'; c_dim='\033[2m'
c_green='\033[32m'; c_yellow='\033[33m'; c_red='\033[31m'

ok()   { printf "${c_green}✓${c_reset} %s\n" "$1"; }
warn() { printf "${c_yellow}⚠${c_reset} %s\n" "$1"; }
fail() { printf "${c_red}✗${c_reset} %s\n" "$1"; }
info() { printf "${c_dim}·${c_reset} %s\n" "$1"; }
hdr()  { printf "\n${c_bold}== %s ==${c_reset}\n" "$1"; }

EXIT_CODE=0

# ===== Subcommand: --frontmatter =============================================

cmd_frontmatter() {
  hdr "Frontmatter validation"
  local invalid=0

  validate() {
    local file="$1"
    local missing=()
    head -1 "$file" | grep -q '^---$' || { fail "$file: missing frontmatter start"; return 1; }
    grep -q '^name:' "$file" || missing+=("name")
    grep -q '^description:' "$file" || missing+=("description")
    grep -q '^color:' "$file" || missing+=("color")
    grep -q '^tools:' "$file" || missing+=("tools")
    grep -q '^voice:' "$file" || missing+=("voice")
    grep -q '^cli_support:' "$file" || missing+=("cli_support")
    if [ ${#missing[@]} -gt 0 ]; then
      fail "$file: missing ${missing[*]}"
      return 1
    fi
    return 0
  }

  while IFS= read -r f; do
    validate "$f" || invalid=$((invalid + 1))
  done < <(find "$REPO_ROOT/scaffolding" \( -path '*/skills/*/SKILL.md' -o -path '*/agents/*.md' \) 2>/dev/null | grep -v README)

  if [ "$invalid" -eq 0 ]; then
    ok "All frontmatter valid"
  else
    fail "$invalid files invalid"
    EXIT_CODE=1
  fi
}

# ===== Subcommand: --cli-matrix ==============================================

cmd_cli_matrix() {
  hdr "CLI support matrix"
  printf "%-50s | %-12s | %-7s | %-8s\n" "skill/agent" "claude-code" "codex" "copilot"
  printf "%-50s-+-%-12s-+-%-7s-+-%-8s\n" "$(printf '%.0s-' {1..50})" "$(printf '%.0s-' {1..12})" "$(printf '%.0s-' {1..7})" "$(printf '%.0s-' {1..8})"

  while IFS= read -r f; do
    name=$(grep -m1 '^name:' "$f" | sed 's/^name:[ ]*//' | tr -d '\r')
    cli_line=$(grep -m1 '^cli_support:' "$f" | sed 's/^cli_support:[ ]*//' | tr -d '\r')
    cc="no"; cx="no"; cp="no"
    [[ "$cli_line" == *"claude-code"* ]] && cc="yes"
    [[ "$cli_line" == *"codex"* ]] && cx="yes"
    [[ "$cli_line" == *"copilot"* ]] && cp="yes"
    printf "%-50s | %-12s | %-7s | %-8s\n" "$name" "$cc" "$cx" "$cp"
  done < <(find "$REPO_ROOT/scaffolding" \( -path '*/skills/*/SKILL.md' -o -path '*/agents/*.md' \) 2>/dev/null | grep -v README | sort)
}

# ===== Subcommand: --layers ==================================================

cmd_layers() {
  hdr "Layer structure validation"
  local missing=0
  # v2: layer 2 renamed from 02-compliance/ to 02-sdl/; accept either
  for layer in 01-foundation 03-personal-advanced 04-power-user; do
    if [ -d "$REPO_ROOT/scaffolding/$layer" ]; then
      ok "Layer present: $layer"
    else
      fail "Layer missing: $layer"
      missing=$((missing + 1))
    fi
  done
  # Layer 2 with backward-compat
  if [ -d "$REPO_ROOT/scaffolding/02-sdl" ]; then
    ok "Layer present: 02-sdl (v2)"
  elif [ -d "$REPO_ROOT/scaffolding/02-compliance" ]; then
    ok "Layer present: 02-compliance (v1, pre-rename)"
  else
    fail "Layer 2 missing: neither 02-sdl/ nor 02-compliance/ present"
    missing=$((missing + 1))
  fi
  if [ "$missing" -gt 0 ]; then EXIT_CODE=1; fi

  # Required files per layer
  for f in LAYERS.md AGENT-INSTRUCTIONS.md; do
    if [ -f "$REPO_ROOT/$f" ]; then
      ok "Root file present: $f"
    else
      fail "Root file missing: $f"
      EXIT_CODE=1
    fi
  done
}

# ===== Subcommand: --hooks ===================================================

cmd_hooks() {
  hdr "Hook activation state"
  local total=0
  local activated=0

  if [ ! -d "$JSTACK_HOME/hooks" ]; then
    warn "$JSTACK_HOME/hooks/ not present — run install.sh first"
    return
  fi

  for dir in "$JSTACK_HOME/hooks/"*/; do
    [ -d "$dir" ] || continue
    name=$(basename "$dir")
    [ "$name" = "README.md" ] && continue
    total=$((total + 1))
    if [ -L "$HOME/.claude/hooks/${name}.sh" ]; then
      ok "Activated: $name"
      activated=$((activated + 1))
    else
      info "Inert: $name (symlink ~/.claude/hooks/${name}.sh to activate)"
    fi
  done
  echo ""
  ok "$activated / $total hooks activated"
}

# ===== Subcommand: --voice ===================================================

cmd_voice() {
  hdr "Voice corpus + calibration state"
  # v2: renamed from TRAILBLAZER-* to OurVoice-*; check both for backward compat
  CORPUS_V2="$REPO_ROOT/scaffolding/03-personal-advanced/voice/OurVoice-corpus.md"
  CORPUS_V1="$REPO_ROOT/scaffolding/03-personal-advanced/voice/TRAILBLAZER-CORPUS.md"
  CORPUS=""
  [ -f "$CORPUS_V2" ] && CORPUS="$CORPUS_V2"
  [ -f "$CORPUS_V1" ] && CORPUS="$CORPUS_V1"

  TEST_V2="$REPO_ROOT/scaffolding/03-personal-advanced/voice/OurVoice-test.md"
  TEST_V1="$REPO_ROOT/scaffolding/03-personal-advanced/voice/TRAILBLAZER-TEST.md"
  TEST=""
  [ -f "$TEST_V2" ] && TEST="$TEST_V2"
  [ -f "$TEST_V1" ] && TEST="$TEST_V1"

  CALIB_V2="$REPO_ROOT/scaffolding/03-personal-advanced/voice/OurVoice-calibration.md"
  CALIB_V1="$REPO_ROOT/scaffolding/03-personal-advanced/voice/TRAILBLAZER-CALIBRATION.md"
  CALIB=""
  [ -f "$CALIB_V2" ] && CALIB="$CALIB_V2"
  [ -f "$CALIB_V1" ] && CALIB="$CALIB_V1"

  [ -n "$CORPUS" ] && ok "Voice corpus present: $(basename "$CORPUS")" || { fail "Voice corpus missing"; EXIT_CODE=1; }
  [ -n "$TEST" ] && ok "Voice test rubric present: $(basename "$TEST")" || { fail "Voice test rubric missing"; EXIT_CODE=1; }
  [ -n "$CALIB" ] && ok "Voice calibration present: $(basename "$CALIB")" || warn "Voice calibration missing — run /jstack-eval"

  if [ -f "$CORPUS" ]; then
    populated=$(grep -c '^- id: ' "$CORPUS" 2>/dev/null || echo 0)
    if [ "$populated" -ge 24 ]; then
      ok "Corpus populated: $populated paragraphs (≥24 floor)"
    else
      warn "Corpus has $populated paragraphs — operator should add more (≥24 floor)"
    fi
  fi

  if [ -f "$CALIB" ]; then
    if grep -qE 'status:\s*CALIBRATED' "$CALIB" 2>/dev/null; then
      ok "Calibration: CALIBRATED"
    else
      warn "Calibration: NOT CALIBRATED — run /jstack-eval"
    fi
  fi
}

# ===== Subcommand: --compliance ==============================================

cmd_compliance() {
  hdr "Compliance docs (SDL)"
  # v2: directory renamed 02-compliance/ → 02-sdl/; check both for backward compat
  COMP_DIR=""
  [ -d "$REPO_ROOT/scaffolding/02-sdl" ] && COMP_DIR="$REPO_ROOT/scaffolding/02-sdl"
  [ -d "$REPO_ROOT/scaffolding/02-compliance" ] && COMP_DIR="$REPO_ROOT/scaffolding/02-compliance"
  if [ -z "$COMP_DIR" ]; then
    fail "Compliance directory missing (expected 02-sdl/ or 02-compliance/)"; EXIT_CODE=1
    return
  fi
  for f in COMPLIANCE-OVERVIEW.md HARD-RULES.md ON-DEMAND-RULES.md REFERENCE-RULES.md DATA-CLASSES.md LICENSE-TIERS.md AGT-OVERVIEW.md; do
    [ -f "$COMP_DIR/$f" ] && ok "$f" || { fail "$f missing"; EXIT_CODE=1; }
  done
}

# ===== Subcommand: --context-engine (NEW for v2) =============================

cmd_context_engine() {
  hdr "Context engine state (v2)"
  ROOT_DOC="$REPO_ROOT/CONTEXT-ENGINE.md"
  [ -f "$ROOT_DOC" ] && ok "CONTEXT-ENGINE.md present" || { fail "CONTEXT-ENGINE.md missing"; EXIT_CODE=1; }

  for skill in context-budget context-warmup perf-mode; do
    path="$REPO_ROOT/scaffolding/01-foundation/skills/$skill/SKILL.md"
    [ -f "$path" ] && ok "skill: $skill" || { fail "skill missing: $skill"; EXIT_CODE=1; }
  done

  # Renamed context-budgetwatch (was context-tokenwatch)
  for skill in context-budgetwatch context-tokenwatch; do
    path="$REPO_ROOT/scaffolding/03-personal-advanced/skills/$skill/SKILL.md"
    [ -f "$path" ] && ok "skill: $skill" && break
  done

  agent="$REPO_ROOT/scaffolding/04-power-user/agents/ContextBudgetAdvisor.md"
  [ -f "$agent" ] && ok "agent: ContextBudgetAdvisor" || { fail "agent missing: ContextBudgetAdvisor"; EXIT_CODE=1; }
}

# ===== Subcommand: --brand (NEW for v2) ======================================

cmd_brand() {
  hdr "Brand integration state (v2)"
  ROOT_DOC="$REPO_ROOT/BRAND-INTEGRATION.md"
  [ -f "$ROOT_DOC" ] && ok "BRAND-INTEGRATION.md present" || { fail "BRAND-INTEGRATION.md missing"; EXIT_CODE=1; }

  DEFAULTS_DIR="$REPO_ROOT/scaffolding/03-personal-advanced/doc-gen/default-templates"
  if [ -d "$DEFAULTS_DIR" ]; then
    for f in default-ppt-template.json default-word-template.json default-web-template.html; do
      [ -f "$DEFAULTS_DIR/$f" ] && ok "default template: $f" || { fail "default template missing: $f"; EXIT_CODE=1; }
    done
  else
    fail "default-templates/ dir missing"
    EXIT_CODE=1
  fi

  for skill in brand-update asset-search generate-ppt generate-word generate-web; do
    path="$REPO_ROOT/scaffolding/03-personal-advanced/skills/$skill/SKILL.md"
    [ -f "$path" ] && ok "skill: $skill" || { fail "skill missing: $skill"; EXIT_CODE=1; }
  done

  for agent in PPTNarrativeArchitect WordTechnicalEditor WebExperienceCritic; do
    path="$REPO_ROOT/scaffolding/03-personal-advanced/agents/$agent.md"
    [ -f "$path" ] && ok "agent: $agent" || { fail "agent missing: $agent"; EXIT_CODE=1; }
  done

  # Brand-staleness hook
  HOOKS_DIR=""
  [ -d "$REPO_ROOT/scaffolding/02-sdl/hooks" ] && HOOKS_DIR="$REPO_ROOT/scaffolding/02-sdl/hooks"
  [ -d "$REPO_ROOT/scaffolding/02-compliance/hooks" ] && HOOKS_DIR="$REPO_ROOT/scaffolding/02-compliance/hooks"
  [ -d "$HOOKS_DIR/brand-staleness-warn" ] && ok "hook: brand-staleness-warn" || warn "hook brand-staleness-warn missing (optional)"
}

# ===== Subcommand: --portability (NEW for v2) ================================

cmd_portability() {
  hdr "Portability shim (v2)"
  SCHEMA="$REPO_ROOT/scaffolding/01-foundation/CLI-SUPPORT-V2-SCHEMA.md"
  [ -f "$SCHEMA" ] && ok "CLI-SUPPORT-V2-SCHEMA.md present" || { fail "CLI-SUPPORT-V2-SCHEMA.md missing"; EXIT_CODE=1; }

  CLI_FINGERPRINT="$REPO_ROOT/scaffolding/01-foundation/skills/jstack-cli-fingerprint/SKILL.md"
  [ -f "$CLI_FINGERPRINT" ] && ok "skill: jstack-cli-fingerprint" || { fail "skill missing: jstack-cli-fingerprint"; EXIT_CODE=1; }

  # Validate cli_support fields on a sample of skills (full validation in --frontmatter)
  with_cli_support=0
  while IFS= read -r f; do
    grep -q '^cli_support:' "$f" && with_cli_support=$((with_cli_support + 1))
  done < <(find "$REPO_ROOT/scaffolding" -path '*/skills/*/SKILL.md' 2>/dev/null)
  ok "$with_cli_support skills declare cli_support"
}

# ===== Subcommand: --upstream ================================================

cmd_upstream() {
  hdr "Upstream sources"
  if [ ! -f "$SOURCES_FILE" ]; then
    fail "upstream-sources.yaml missing"
    EXIT_CODE=1
    return
  fi
  if command -v yq >/dev/null 2>&1; then
    mapfile -t sources < <(yq '.sources | keys | .[]' "$SOURCES_FILE" 2>/dev/null)
    ok "${#sources[@]} upstream sources declared"
    for s in "${sources[@]}"; do
      info "  · $s"
    done
  else
    warn "yq not available — listing skipped"
  fi
}

# ===== Subcommand: --counts ==================================================

cmd_counts() {
  hdr "Counts"
  skills=$(find "$REPO_ROOT/scaffolding" -path '*/skills/*/SKILL.md' 2>/dev/null | wc -l | tr -d ' ')
  agents=$(find "$REPO_ROOT/scaffolding" -path '*/agents/*.md' 2>/dev/null | grep -cv README || echo 0)
  # v2: dir renamed to 02-sdl/; check both for backward compat
  hooks_dir=""
  [ -d "$REPO_ROOT/scaffolding/02-sdl/hooks" ] && hooks_dir="$REPO_ROOT/scaffolding/02-sdl/hooks"
  [ -d "$REPO_ROOT/scaffolding/02-compliance/hooks" ] && hooks_dir="$REPO_ROOT/scaffolding/02-compliance/hooks"
  hooks=0
  [ -n "$hooks_dir" ] && hooks=$(find "$hooks_dir" -name 'HOOK.md' 2>/dev/null | wc -l | tr -d ' ')

  printf "%-20s %s\n" "Skills:" "$skills"
  printf "%-20s %s\n" "Agents:" "$agents"
  printf "%-20s %s\n" "Hooks:" "$hooks"
}

# ===== Subcommand: --tier-stamps =============================================

cmd_tier_stamps() {
  hdr "Agent tier-stamps"
  local missing=0
  while IFS= read -r f; do
    if ! grep -q '^tier:' "$f"; then
      # Promoted (Layer 3) agents must have tier; Layer 4 may omit (defaults to permissive per upstream)
      if [[ "$f" == *"03-personal-advanced"* ]]; then
        fail "$f: missing tier (required for Layer 3 promoted)"
        missing=$((missing + 1))
      else
        info "$f: tier not stamped (Layer 4; default permissive)"
      fi
    else
      ok "$(basename "$f"): tier-stamped"
    fi
  done < <(find "$REPO_ROOT/scaffolding" -path '*/agents/*.md' 2>/dev/null | grep -v README)
  if [ "$missing" -gt 0 ]; then EXIT_CODE=1; fi
}

# ===== Subcommand: --all =====================================================

cmd_all() {
  cmd_layers
  cmd_counts
  cmd_frontmatter
  cmd_compliance
  cmd_voice
  cmd_hooks
  cmd_upstream
  cmd_tier_stamps
  # v2 additions
  cmd_portability
  cmd_context_engine
  cmd_brand
  hdr "Final verdict"
  if [ "$EXIT_CODE" -eq 0 ]; then
    ok "ALL CHECKS PASSED"
  else
    fail "SOME CHECKS FAILED (exit $EXIT_CODE)"
  fi
}

# ===== Dispatch ==============================================================

case "${1:---counts}" in
  --frontmatter)  cmd_frontmatter ;;
  --cli-matrix)   cmd_cli_matrix ;;
  --layers)       cmd_layers ;;
  --hooks)        cmd_hooks ;;
  --voice)        cmd_voice ;;
  --compliance)   cmd_compliance ;;
  --upstream)     cmd_upstream ;;
  --counts)         cmd_counts ;;
  --tier-stamps)    cmd_tier_stamps ;;
  --portability)    cmd_portability ;;
  --context-engine) cmd_context_engine ;;
  --brand)          cmd_brand ;;
  --all)            cmd_all ;;
  -h|--help)
    cat <<HELP
jstack verify.sh — install + structure diagnostic

Usage: verify.sh [--subcommand]

Subcommands:
  --frontmatter   validate skill + agent frontmatter
  --cli-matrix    print CLI support matrix
  --layers        validate 4-layer scaffolding structure
  --hooks         check hook activation state (symlinks)
  --voice         check voice corpus + calibration state
  --compliance    check compliance docs present
  --upstream      check upstream-sources.yaml
  --counts         summary counts (default)
  --tier-stamps    check agent tier-stamping
  --portability    (v2) CLI-SUPPORT-V2-SCHEMA + jstack-cli-fingerprint
  --context-engine (v2) CONTEXT-ENGINE.md + context-budget/warmup/perf-mode
  --brand          (v2) BRAND-INTEGRATION.md + default-templates + brand-update/asset-search
  --all            run everything + aggregate verdict
HELP
    ;;
  *)
    fail "Unknown subcommand: $1 (use --help)"
    exit 2
    ;;
esac

exit "$EXIT_CODE"
