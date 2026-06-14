#!/usr/bin/env bash
# lintel verify.sh — install + structure diagnostic
#
# Subcommands:
#   --frontmatter   validate skill + agent frontmatter
#   --cli-matrix    per-skill/agent cli_support matrix (root skills/ + agents/)
#   --layers        validate scaffolding structure
#   --hooks         check hook activation state (symlinks)
#   --upstream      check upstream-sources.yaml
#   --counts        summary counts (skills/agents/hooks)
#   --tier-stamps   check agent tier-stamping
#   --all           run everything + aggregate verdict
#
# Default (no flag) is --counts.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCES_FILE="$SCRIPT_DIR/upstream-sources.yaml"
LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"

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
    # v3.6 cohort 1 item 6.4: lock layer-field discipline (SKILL.md only — agents don't carry layer)
    if [[ "$file" == *SKILL.md ]]; then
      grep -q '^layer:' "$file" || missing+=("layer")
    fi
    if [ ${#missing[@]} -gt 0 ]; then
      fail "$file: missing ${missing[*]}"
      return 1
    fi
    return 0
  }

  # v3: check skills/ and agents/<category>/ at repo root
  # v2 fallback: scaffolding/*/skills/ and scaffolding/*/agents/
  local search_paths=()
  [ -d "$REPO_ROOT/skills" ] && search_paths+=("$REPO_ROOT/skills")
  [ -d "$REPO_ROOT/agents" ] && search_paths+=("$REPO_ROOT/agents")
  # v2 fallback for any leftover files
  [ -d "$REPO_ROOT/scaffolding" ] && search_paths+=("$REPO_ROOT/scaffolding")

  for path in "${search_paths[@]}"; do
    while IFS= read -r f; do
      validate "$f" || invalid=$((invalid + 1))
    done < <(find "$path" \( -name 'SKILL.md' -o \( -path '*/agents/*.md' \) -o \( -path '*/agents/*/*.md' \) \) 2>/dev/null | grep -v README)
  done

  if [ "$invalid" -eq 0 ]; then
    ok "All frontmatter valid"
  else
    fail "$invalid files invalid"
    EXIT_CODE=1
  fi
}

# ===== Subcommand: --cli-matrix ==============================================
# Per-skill/agent cli_support aggregator over repo-root skills/ + agents/
# (scaffolding/ only as v2 fallback). Frontmatter ships in two styles, both
# parsed (the old single-line grep missed the block style entirely):
#   inline:  cli_support: [claude-code, codex]
#   block:   cli_support:
#              - cli: claude-code
#                level: full

cmd_cli_matrix() {
  hdr "CLI support matrix (declared cli_support per skill/agent)"

  local search_paths=()
  [ -d "$REPO_ROOT/skills" ] && search_paths+=("$REPO_ROOT/skills")
  [ -d "$REPO_ROOT/agents" ] && search_paths+=("$REPO_ROOT/agents")
  if [ "${#search_paths[@]}" -eq 0 ] && [ -d "$REPO_ROOT/scaffolding" ]; then
    search_paths+=("$REPO_ROOT/scaffolding")
  fi
  if [ "${#search_paths[@]}" -eq 0 ]; then
    warn "no skills/ or agents/ (or scaffolding/) found — nothing to aggregate"
    return
  fi

  printf "%-44s | %s\n" "skill/agent" "cli_support"
  printf "%-44s-+-%s\n" "$(printf '%.0s-' {1..44})" "$(printf '%.0s-' {1..30})"

  local f name clis
  while IFS= read -r f; do
    name=$(grep -m1 '^name:' "$f" | sed 's/^name:[ ]*//' | tr -d '\r')
    clis=$(awk '
      { sub(/\r$/, "") }
      NR == 1 && /^---[ \t]*$/ { fm = 1; next }
      fm && /^---[ \t]*$/ { exit }                 # frontmatter only
      fm && /^cli_support:/ {
        rest = $0; sub(/^cli_support:[ \t]*/, "", rest)
        if (rest != "") { inline = rest } else { blk = 1 }
        next
      }
      blk && /^[A-Za-z_-]+:/ { blk = 0 }           # next top-level key ends the block
      blk {
        line = $0
        if (match(line, /-[ \t]*cli:[ \t]*/)) {
          v = substr(line, RSTART + RLENGTH)
          sub(/[ \t].*$/, "", v); gsub(/[",]/, "", v)
          if (v != "") out = out (out == "" ? "" : ", ") v
        }
      }
      END {
        if (inline != "") {
          gsub(/[]["]/, "", inline)
          gsub(/,[ \t]*/, ", ", inline)
          print inline
        } else {
          print out
        }
      }
    ' "$f")
    printf "%-44s | %s\n" "$name" "${clis:--}"
  done < <(find "${search_paths[@]}" \( -name 'SKILL.md' -o -path '*/agents/*.md' -o -path '*/agents/*/*.md' \) 2>/dev/null | grep -v README | sort)
}

# ===== Subcommand: --layers ==================================================

cmd_layers() {
  hdr "Layer structure validation"
  local missing=0
  # v4: scaffolding reduced to 01-foundation (foundation templates copied into target repos).
  for layer in 01-foundation; do
    if [ -d "$REPO_ROOT/scaffolding/$layer" ]; then
      ok "Layer present: $layer"
    else
      fail "Layer missing: $layer"
      missing=$((missing + 1))
    fi
  done
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

  # v3: also check skills/ + agents/ + hooks/ + 7 plugin manifests at repo root
  if [ -d "$REPO_ROOT/skills" ] && [ -d "$REPO_ROOT/agents" ] && [ -d "$REPO_ROOT/hooks" ]; then
    ok "v3 plugin-manifest layout present (skills/ + agents/ + hooks/ at repo root)"
  else
    info "v3 plugin-manifest layout not yet present (skills/agents/hooks/ at root)"
  fi
}

# ===== Subcommand: --hooks ===================================================

cmd_hooks() {
  hdr "Hook activation state"
  local total=0
  local activated=0

  if [ ! -d "$LINTEL_HOME/hooks" ]; then
    warn "$LINTEL_HOME/hooks/ not present — run install.sh first"
    return
  fi

  for dir in "$LINTEL_HOME/hooks/"*/; do
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

# ===== Subcommand: --context-engine (NEW for v2) =============================

cmd_context_engine() {
  hdr "Context engine state"
  ROOT_DOC=""
  for candidate in \
    "$REPO_ROOT/docs/design/CONTEXT-ENGINE.md" \
    "$REPO_ROOT/CONTEXT-ENGINE.md"; do
    [ -f "$candidate" ] && { ROOT_DOC="$candidate"; break; }
  done
  [ -n "$ROOT_DOC" ] && ok "CONTEXT-ENGINE.md present ($ROOT_DOC)" || { fail "CONTEXT-ENGINE.md missing"; EXIT_CODE=1; }

  # skills at repo root skills/<name>/SKILL.md
  for skill in context-budget context-warm perf-mode; do
    found=""
    for path in \
      "$REPO_ROOT/skills/$skill/SKILL.md" \
      "$REPO_ROOT/scaffolding/01-foundation/skills/$skill/SKILL.md"; do
      [ -f "$path" ] && { found="$path"; break; }
    done
    [ -n "$found" ] && ok "skill: $skill" || { fail "skill missing: $skill"; EXIT_CODE=1; }
  done

  # (context-budgetwatch removed 2026-06-10 — consolidated into context-budget --watch;
  #  the old name resolves via config/aliases.yaml until 2026-09-10)

  # ContextBudgetAdvisor at agents/engineering/
  if [ -f "$REPO_ROOT/agents/engineering/ContextBudgetAdvisor.md" ]; then
    ok "agent: ContextBudgetAdvisor"
  else
    fail "agent missing: ContextBudgetAdvisor"; EXIT_CODE=1
  fi
}

# ===== Subcommand: --portability (NEW for v2; v3 keeps for compat) ===========

cmd_portability() {
  hdr "Portability shim (v2 legacy / v3 plugin-manifest)"
  # v3: schema moved to docs/design/
  SCHEMA=""
  for candidate in \
    "$REPO_ROOT/docs/design/CLI-SUPPORT-V2-SCHEMA.md" \
    "$REPO_ROOT/scaffolding/01-foundation/CLI-SUPPORT-V2-SCHEMA.md"; do
    [ -f "$candidate" ] && { SCHEMA="$candidate"; break; }
  done
  [ -n "$SCHEMA" ] && ok "CLI-SUPPORT-V2-SCHEMA.md present" || warn "CLI-SUPPORT-V2-SCHEMA.md missing (v2 doc, optional in v3)"

  # v3: skill at skills/li:cli-fingerprint/SKILL.md
  CLI_FINGERPRINT=""
  for candidate in \
    "$REPO_ROOT/skills/li:cli-fingerprint/SKILL.md" \
    "$REPO_ROOT/scaffolding/01-foundation/skills/li:cli-fingerprint/SKILL.md"; do
    [ -f "$candidate" ] && { CLI_FINGERPRINT="$candidate"; break; }
  done
  [ -n "$CLI_FINGERPRINT" ] && ok "skill: li-cli-fingerprint" || warn "skill missing: li-cli-fingerprint (use bin/li:doctor for v3 runtime)"

  # Validate cli_support fields on skills (v3 path + v2 fallback)
  with_cli_support=0
  search_paths=()
  [ -d "$REPO_ROOT/skills" ] && search_paths+=("$REPO_ROOT/skills")
  [ -d "$REPO_ROOT/scaffolding" ] && search_paths+=("$REPO_ROOT/scaffolding")
  for path in "${search_paths[@]}"; do
    while IFS= read -r f; do
      grep -q '^cli_support:' "$f" && with_cli_support=$((with_cli_support + 1))
    done < <(find "$path" -name 'SKILL.md' 2>/dev/null)
  done
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
    # while-read instead of mapfile: stock macOS bash 3.2 has no mapfile
    # (same portability rule as bin/li-uniformity's mapfile_compat).
    sources=()
    while IFS= read -r _s; do
      [ -n "$_s" ] && sources+=("$_s")
    done < <(yq '.sources | keys | .[]' "$SOURCES_FILE" 2>/dev/null)
    ok "${#sources[@]} upstream sources declared"
    # guard the expansion: "${sources[@]}" on an empty array is a set -u error on bash < 4.4
    if [ "${#sources[@]}" -gt 0 ]; then
      for s in "${sources[@]}"; do
        info "  · $s"
      done
    fi
  else
    warn "yq not available — listing skipped"
  fi
}

# ===== Subcommand: --counts ==================================================

cmd_counts() {
  hdr "Counts"
  # v3: skills at root, agents at root organized per category
  # backward-compat: also check v2 scaffolding paths
  skills_v3=0
  agents_v3=0
  hooks_v3=0
  [ -d "$REPO_ROOT/skills" ] && skills_v3=$(find "$REPO_ROOT/skills" -name 'SKILL.md' 2>/dev/null | wc -l | tr -d ' ')
  [ -d "$REPO_ROOT/agents" ] && agents_v3=$(find "$REPO_ROOT/agents" -name '*.md' 2>/dev/null | grep -cv README || echo 0)
  [ -d "$REPO_ROOT/hooks/shared" ] && hooks_v3=$(find "$REPO_ROOT/hooks/shared" -name 'HOOK.md' 2>/dev/null | wc -l | tr -d ' ')

  # v2 fallback if v3 not present
  skills_v2=$(find "$REPO_ROOT/scaffolding" -path '*/skills/*/SKILL.md' 2>/dev/null | wc -l | tr -d ' ')
  agents_v2=$(find "$REPO_ROOT/scaffolding" -path '*/agents/*.md' 2>/dev/null | grep -cv README || echo 0)
  hooks_v2_dir=""
  hooks_v2=0
  [ -n "$hooks_v2_dir" ] && hooks_v2=$(find "$hooks_v2_dir" -name 'HOOK.md' 2>/dev/null | wc -l | tr -d ' ')

  if [ "$skills_v3" -gt 0 ] || [ "$agents_v3" -gt 0 ]; then
    info "v3 paths detected"
    printf "%-20s %s\n" "Skills (v3):" "$skills_v3"
    printf "%-20s %s\n" "Agents (v3):" "$agents_v3"
    printf "%-20s %s\n" "Hooks (v3):" "$hooks_v3"
    if [ "$skills_v2" -gt 0 ] || [ "$agents_v2" -gt 0 ]; then
      info "(also: v2 paths still have $skills_v2 skills + $agents_v2 agents — migration incomplete?)"
    fi
  else
    info "v2 paths detected (no v3 yet)"
    printf "%-20s %s\n" "Skills (v2):" "$skills_v2"
    printf "%-20s %s\n" "Agents (v2):" "$agents_v2"
    printf "%-20s %s\n" "Hooks (v2):" "$hooks_v2"
  fi
}

# ===== Subcommand: --tier-stamps =============================================

cmd_tier_stamps() {
  hdr "Agent tier-stamps"
  local missing=0
  local agent_paths=()
  # agents/ at repo root, organized per category
  [ -d "$REPO_ROOT/agents" ] && agent_paths+=("$REPO_ROOT/agents")

  for path in "${agent_paths[@]}"; do
    while IFS= read -r f; do
      if ! grep -q '^tier:' "$f"; then
        # security / compliance / customer categories require tier (operator IP)
        # engineering category may omit tier (defaults to permissive)
        local category=""
        [[ "$f" == *"/security/"* ]] && category="security"
        [[ "$f" == *"/compliance/"* ]] && category="compliance"
        if [ -n "$category" ]; then
          fail "$f: missing tier (required for $category category)"
          missing=$((missing + 1))
        else
          info "$f: tier not stamped (defaults to permissive)"
        fi
      else
        ok "$(basename "$f"): tier-stamped"
      fi
    done < <(find "$path" -name '*.md' 2>/dev/null | grep -v README)
  done
  if [ "$missing" -gt 0 ]; then EXIT_CODE=1; fi
}

# ===== Subcommand: --plugin-manifests (v3) ===================================

cmd_plugin_manifests() {
  hdr "Plugin manifests"
  local manifests=(
    ".claude-plugin/plugin.json"
    ".claude-plugin/marketplace.json"
    ".codex-plugin/plugin.json"
    ".cursor-plugin/plugin.json"
    "gemini-extension.json"
    ".opencode/INSTALL.md"
  )
  local missing=0
  for m in "${manifests[@]}"; do
    if [ -f "$REPO_ROOT/$m" ]; then
      # Validate JSON files (not markdown)
      if [[ "$m" == *.json ]]; then
        if command -v python3 >/dev/null 2>&1; then
          if python3 -c "import json,sys;json.load(open(sys.argv[1]))" "$REPO_ROOT/$m" 2>/dev/null; then
            ok "$m (valid JSON)"
          else
            fail "$m (INVALID JSON)"
            missing=$((missing + 1))
          fi
        elif command -v jq >/dev/null 2>&1; then
          if jq empty "$REPO_ROOT/$m" 2>/dev/null; then
            ok "$m (valid JSON)"
          else
            fail "$m (INVALID JSON)"
            missing=$((missing + 1))
          fi
        else
          ok "$m (present, JSON syntax not checked — no python3/jq)"
        fi
      else
        ok "$m"
      fi
    else
      fail "$m MISSING"
      missing=$((missing + 1))
    fi
  done

  # Also check root entrypoint files
  hdr "Root entrypoint files (v3)"
  for f in CLAUDE.md AGENTS.md GEMINI.md; do
    if [ -f "$REPO_ROOT/$f" ]; then
      ok "$f"
    else
      fail "$f MISSING (entrypoint for $(echo $f | sed 's/.md//') CLI)"
      missing=$((missing + 1))
    fi
  done

  if [ "$missing" -gt 0 ]; then EXIT_CODE=1; fi
}

# ===== Subcommand: --agents-categorized (v3) =================================

cmd_agents_categorized() {
  hdr "Agents categorization (v3)"
  if [ ! -d "$REPO_ROOT/agents" ]; then
    warn "agents/ directory not found at repo root — v3 not yet applied"
    return
  fi

  local missing=0
  local total=0
  for f in $(find "$REPO_ROOT/agents" -name '*.md' 2>/dev/null | grep -v README); do
    total=$((total + 1))
    if grep -q '^category:' "$f"; then
      ok "$(basename "$f"): category present"
    else
      fail "$(basename "$f"): missing category frontmatter"
      missing=$((missing + 1))
    fi
  done

  # Per-category counts
  hdr "Per-category counts"
  for d in "$REPO_ROOT/agents"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    count=$(find "$d" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
    printf "%-20s %s\n" "$name:" "$count"
  done
  printf "%-20s %s\n" "TOTAL:" "$total"

  if [ "$missing" -gt 0 ]; then EXIT_CODE=1; fi
}

# ===== Subcommand: --scaffolding-coherence (v3) ==============================

cmd_scaffolding_coherence() {
  hdr "Scaffolding coherence (v5 .claude/ home layout — ADR-0005)"
  local missing=0
  # What 01-foundation actually ships post-ADR-0005: knowledge templates under
  # .claude/ (memory/, decisions/, plans/, agents/) — the old tasks/* and
  # docs/adr/* template paths were removed in the v5 migration.
  local required=(
    "scaffolding/01-foundation/CORE-PRINCIPLES.md"
    "scaffolding/01-foundation/EVOLUTION.md"
    "scaffolding/01-foundation/EVOLUTION-LOG.md"
    "scaffolding/01-foundation/CLAUDE.md.template"
    "scaffolding/01-foundation/.claude/memory/lessons.md"
    "scaffolding/01-foundation/.claude/memory/working-state.md"
    "scaffolding/01-foundation/.claude/memory/personas.md"
    "scaffolding/01-foundation/.claude/plans/todo.md"
    "scaffolding/01-foundation/.claude/decisions/README.md"
    "scaffolding/01-foundation/.claude/decisions/TEMPLATE.md"
    "scaffolding/01-foundation/TEMPLATE-skill.md"
    "scaffolding/01-foundation/TEMPLATE-agent.md"
  )
  for f in "${required[@]}"; do
    if [ -f "$REPO_ROOT/$f" ]; then
      ok "$f"
    else
      fail "$f MISSING (scaffolding template gap)"
      missing=$((missing + 1))
    fi
  done

  if [ "$missing" -gt 0 ]; then EXIT_CODE=1; fi
}

# ===== Subcommand: --all =====================================================

cmd_all() {
  cmd_layers
  cmd_counts
  cmd_frontmatter
  cmd_hooks
  cmd_upstream
  cmd_tier_stamps
  # v2 additions
  cmd_portability
  cmd_context_engine
  # v3 additions
  cmd_plugin_manifests
  cmd_agents_categorized
  cmd_scaffolding_coherence
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
  --upstream)     cmd_upstream ;;
  --counts)         cmd_counts ;;
  --tier-stamps)    cmd_tier_stamps ;;
  --portability)    cmd_portability ;;
  --context-engine) cmd_context_engine ;;
  --plugin-manifests)     cmd_plugin_manifests ;;
  --agents-categorized)   cmd_agents_categorized ;;
  --scaffolding-coherence) cmd_scaffolding_coherence ;;
  --all)            cmd_all ;;
  -h|--help)
    cat <<HELP
lintel verify.sh — install + structure diagnostic

Usage: verify.sh [--subcommand]

Subcommands:
  --frontmatter   validate skill + agent frontmatter
  --cli-matrix    per-skill/agent cli_support matrix (root skills/ + agents/)
  --layers        validate scaffolding structure
  --hooks         check hook activation state (symlinks)
  --upstream      check upstream-sources.yaml
  --counts         summary counts (default)
  --tier-stamps    check agent tier-stamping
  --portability    (v2) CLI-SUPPORT-V2-SCHEMA + li-cli-fingerprint
  --context-engine (v2) CONTEXT-ENGINE.md + context-budget/warmup/perf-mode
  --plugin-manifests       (v3) validate JSON + presence of per-CLI plugin manifests
  --agents-categorized     (v3) verify all agents have category frontmatter
  --scaffolding-coherence  verify foundation templates present (v5 .claude/ layout)
  --all            run everything + aggregate verdict
HELP
    ;;
  *)
    fail "Unknown subcommand: $1 (use --help)"
    exit 2
    ;;
esac

exit "$EXIT_CODE"
