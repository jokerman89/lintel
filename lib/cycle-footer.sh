#!/usr/bin/env bash
# component: cycle-footer
# implements: ADR-0003
# intent: .claude/decisions/0003-cycle-position-footer.md
# last_intent_review: 2026-09-23
#
# lib/cycle-footer.sh — render the position footer that closes every official Lintel
# report, so an operator entering the cycle at any point always knows where they are
# and the single logical next action. Three tiers, one entry point:
#   • full     (default, in a cycle) — legend + stepper + you-are-here / next / say-this
#   • --compact (in a cycle)         — one muted line
#   • thin     (no active cycle)     — ambient one-liner for normal Q&A outside the cycle
# The tier auto-selects: an active cycle (a resolvable current phase) renders the cycle
# footer; no active cycle falls to the thin ambient line. Force a tier with
# --compact / --thin / --full. Emoji by default; --ascii or LINTEL_ASCII=1 renders an
# ASCII stepper for terminals that mangle glyphs (a convergent cross-platform lesson
# from superpowers #275 / spec-kit #1946). No jq/yq; CRLF-safe. Idempotent source.
#
# render_cycle_footer [--full|--compact|--thin] [--ascii] [--mode M] [--here P]
#                     [--next P] [--awaiting "<hint>"] [--state <file>]
#   With no --here, state is read from --state (default .claude/runtime/state/00-state.md,
#   falling back to the legacy .lintel/state/00-state.md on un-migrated repos):
#   the last `phase:` block is "here", its `next_recommended:` is "next", and the set
#   of prior `phase:` blocks are "done". --here/--next/--mode override the file.
command -v render_cycle_footer >/dev/null 2>&1 && return 0 2>/dev/null

_CYCLE_FOOTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
[ -f "$_CYCLE_FOOTER_DIR/cycle-modes.sh" ] && . "$_CYCLE_FOOTER_DIR/cycle-modes.sh"
# state_cycle_segment lives in state.sh — ONE ledger parser shared with the
# writer side (two parsers over one ledger is the shared-schema violation that
# caused the cross-cycle footer bug; launch register B4).
# shellcheck disable=SC1091
command -v state_cycle_segment >/dev/null 2>&1 || { [ -f "$_CYCLE_FOOTER_DIR/state.sh" ] && . "$_CYCLE_FOOTER_DIR/state.sh"; } || true

_cf_in_list() { case " $2 " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }

# first non-skipped phase AFTER <here> in canonical order ("" if <here> is terminal)
_cf_next_after() {
  local here="$1" skips="$2" seen=0 p
  for p in $(cycle_phases); do
    if [ "$seen" = "1" ]; then _cf_in_list "$p" "$skips" || { printf '%s' "$p"; return 0; }; fi
    [ "$p" = "$here" ] && seen=1
  done
}

# last `key: value` from the current-cycle segment on STDIN (CRLF-safe,
# ignores indentation)
_cf_state_last() {
  local key="$1"
  awk -v k="${key}:" '
    { sub(/\r$/,""); line=$0; sub(/^[ \t]+/,"",line)
      if (index(line,k)==1) { v=substr(line,length(k)+1); sub(/^[ \t]+/,"",v); sub(/[ \t]+$/,"",v); last=v } }
    END { print last }
  '
}

# every `phase:` value on STDIN, in ledger order — deliberately NOT
# de-duplicated: a loop-back re-entry (BUILD blocked → PLAN again) means the
# LAST canonical entry is the true position; first-occurrence de-dup froze a
# revisited phase at its first position (launch register B4).
_cf_phase_history() {
  awk '
    { sub(/\r$/,""); line=$0; sub(/^[ \t]+/,"",line)
      if (index(line,"phase:")==1) { v=substr(line,7); sub(/^[ \t]+/,"",v); sub(/[ \t]+$/,"",v)
        if (v!="") print v } }
  '
}

render_cycle_footer() {
  # v5 layout (ADR-0005): state lives in .claude/runtime/state/; the .lintel/
  # path is the pre-migration fallback (grace window to 2026-09-12).
  local _default_state
  _default_state="$(state_file 2>/dev/null)" || _default_state=""
  local tier="auto" ascii="${LINTEL_ASCII:-0}" awaiting="" mode="" here="" next="" state="$_default_state"
  local cycle_id="${LINTEL_CYCLE_ID:-}" status="" explicit_here=no explicit_next=no selected=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --compact) tier="compact"; shift ;;
      --thin)    tier="thin"; shift ;;
      --full)    tier="full"; shift ;;
      --ascii)   ascii="1"; shift ;;
      # shift the value only if one is actually present — a trailing value-flag with
      # no value must NOT `shift 2` (that fails without consuming → infinite loop).
      --awaiting) awaiting="${2:-}"; shift; [ $# -gt 0 ] && shift ;;
      --mode)    mode="${2:-}"; shift; [ $# -gt 0 ] && shift ;;
      --here)    here="${2:-}"; explicit_here=yes; shift; [ $# -gt 0 ] && shift ;;
      --next)    next="${2:-}"; explicit_next=yes; shift; [ $# -gt 0 ] && shift ;;
      --state)   state="${2:-}"; shift; [ $# -gt 0 ] && shift ;;
      --cycle)   cycle_id="${2:-}"; shift; [ $# -gt 0 ] && shift ;;
      *) shift ;;
    esac
  done

  # glyphs (nextmark + here-glyph also drive the text labels, so ASCII mode stays
  # emoji-free everywhere, not just in the stepper)
  local g_done g_skip g_here g_pend arrow legend nextmark
  if [ "$ascii" = "1" ]; then
    g_done="[x]"; g_skip="[~]"; g_here="[>]"; g_pend="[ ]"; arrow="  "; nextmark=">"
    legend="legend: [x] done · [~] skipped · [>] here · [ ] pending"
  else
    g_done="✅"; g_skip="⊘"; g_here="📍"; g_pend="▢"; arrow=" → "; nextmark="▶"
    legend="✅ done · ⊘ skipped · 📍 here · ▢ pending"
  fi

  # resolve from the CURRENT cycle's ledger segment (state_cycle_segment): a
  # prior cycle's cycle_complete / phase history / mode in the same append-only
  # file must not poison a new cycle. Non-canonical ledger entries
  # (CYCLE/RESUME orchestrator blocks, ADR-0008) carry metadata, not position —
  # filter them out of the history before resolving "here".
  local seg=""
  if [ -f "$state" ]; then
    if command -v state_cycle_segment >/dev/null 2>&1; then
      seg="$(state_cycle_segment "$state" "$cycle_id")" || {
        printf '> `li` · selected cycle not found — reconcile the work selection before resuming\n'
        return 0
      }
    else
      seg="$(cat "$state" 2>/dev/null)"
    fi
  fi
  local history; history="$(printf '%s\n' "$seg" | _cf_phase_history)"
  if [ -z "$here" ]; then
    local _h _cand=""
    while IFS= read -r _h; do
      [ -n "$_h" ] || continue
      cycle_phase_known "$(printf '%s' "$_h" | awk '{print toupper($1)}')" && _cand="$_h"
    done <<EOF_HIST
$history
EOF_HIST
    here="$_cand"
  fi
  [ -z "$next" ] && next="$(printf '%s\n' "$seg" | _cf_state_last next_recommended)"
  [ -z "$mode" ] && mode="$(printf '%s\n' "$seg" | _cf_state_last cycle_mode)"
  [ -z "$mode" ] && mode="$(printf '%s\n' "$seg" | _cf_state_last mode)"
  [ -z "$mode" ] && mode="${LINTEL_CYCLE_MODE:-}"
  local complete; complete="$(printf '%s\n' "$seg" | _cf_state_last cycle_complete)"

  # A cycle with a CYCLE STARTING block but no canonical phase closed yet is ACTIVE,
  # but `here` is empty. Without this, auto/full tier fell to the thin "no active
  # cycle" line at the exact moment a cycle kicks off — the compact tier already
  # handled this case (ADR-0003 follow-up, setup-hardening 2026-06-14).
  local started=0
  [ -z "$here" ] && [ "$complete" != "true" ] && [ -n "$history" ] && started=1

  # normalize phase tokens to first-word UPPER-CASE — consistent with cycle_mode_skips /
  # cycle_phase_known, since state or operator input may be lowercase or multi-word.
  here="$(printf '%s' "$here" | awk '{print toupper($1)}')"
  next="$(printf '%s' "$next" | awk '{print toupper($1)}')"
  if [ -n "$here" ] && [ -n "$seg" ]; then
    status="$(state_phase_record "$here" "$state" "$cycle_id" | state_field status)"
    status="$(printf '%s' "$status" | tr '[:lower:]' '[:upper:]')"
    selected="$(printf '%s\n' "$seg" | state_field phases_selected)"
    if [ -n "$selected" ] && [ "$explicit_next" = no ]; then
      case "$status" in DONE|DONE_WITH_CONCERNS) next="$(state_resume_phase "$state" "$cycle_id")" ;; esac
    fi
  fi

  # an explicitly-set-but-unknown `here` (typo) degrades VISIBLY, never to a silent
  # all-pending, here-less footer.
  if [ -n "$here" ] && ! cycle_phase_known "$here"; then
    printf '> `li` · cycle position unresolved (`%s` is not a known phase) — `/li:status` to re-sync\n' "$here"
    return 0
  fi

  local skips; skips="$(cycle_mode_skips "$mode")"
  if [ -n "$selected" ]; then
    for p in $(cycle_phases); do _cf_in_list "$p" "$selected" || skips="$skips $p"; done
  fi

  # derive `next` from canonical order when not supplied and `here` is mid-pipeline, so a
  # known-but-non-terminal position never mislabels itself "cycle complete".
  [ -z "$next" ] && [ -n "$here" ] && next="$(_cf_next_after "$here" "$skips")"

  # stepper position: a started-but-no-phase-closed cycle marks the first non-skipped
  # phase (SENSE in every shipping mode) so the stepper shows the here-glyph, not all-pending.
  local _mark="$here"
  if [ "$started" = "1" ] && [ -z "$here" ]; then
    _mark="$(printf '%s\n' "$seg" | state_field first_phase)"
    if [ -z "$_mark" ]; then
      for p in $(cycle_phases); do _cf_in_list "$p" "$skips" || { _mark="$p"; break; }; done
    fi
  fi

  # auto tier → thin only when there is genuinely no active cycle. A freshly STARTED
  # cycle (started=1) keeps the full footer instead of falling to thin.
  if [ "$tier" = "auto" ]; then
    if [ "$complete" = "true" ]; then tier="thin"
    elif [ -n "$here" ] || [ "$started" = "1" ]; then tier="full"
    else tier="thin"; fi
  fi

  # ── thin ambient footer (outside the cycle) ──
  if [ "$tier" = "thin" ]; then
    local pack=""
    if command -v verify_profile_context >/dev/null 2>&1 &&
        [ -n "${LINTEL_PROFILE_REFERENCE:-}" ]; then
      if verify_profile_context >/dev/null; then pack="$(get_loaded_pack)" || pack="unverified"
      else pack="unverified"; fi
    fi
    if [ -n "$pack" ]; then
      printf '> `li` · pack `%s` · no active cycle — `/li:cycle` for structured work · `/li:catalog` to browse\n' "$pack"
    else
      printf '> `li` · no active cycle — `/li:cycle <task>` for structured work · `/li:catalog` to browse\n'
    fi
    return 0
  fi

  # ── build the stepper (full + compact share it) ──
  # "done" is positional: a non-skipped phase BEFORE `here` in canonical order. This
  # matches the cycle's linear progression and works whether `here` came from state
  # history or an explicit --here. Skip takes precedence over done (a skipped phase
  # before `here` — e.g. SCOPE in research-dive — renders ⊘, not ✅).
  local here_idx=0 idx=0 p
  for p in $(cycle_phases); do idx=$((idx+1)); [ "$p" = "$_mark" ] && here_idx=$idx; done
  local stepper="" first=1 g done_phases
  done_phases="$(printf '%s\n' "$seg" | state_completed_phases)"
  idx=0
  for p in $(cycle_phases); do
    idx=$((idx+1))
    if   [ "$p" = "$_mark" ]; then g="$g_here"
    elif _cf_in_list "$p" "$skips"; then g="$g_skip"
    elif _cf_in_list "$p" "$done_phases"; then g="$g_done"
    elif [ -z "$seg" ] && [ "$explicit_here" = yes ] && [ "$here_idx" -gt 0 ] && [ "$idx" -lt "$here_idx" ]; then g="$g_done"
    else g="$g_pend"; fi
    if [ "$first" = 1 ]; then stepper="${p} ${g}"; first=0; else stepper="${stepper}${arrow}${p} ${g}"; fi
  done

  local nl; nl="$(printf '%s' "$next" | tr '[:upper:]' '[:lower:]')"
  local label
  case "$status" in
    DONE) label="done" ;;
    DONE_WITH_CONCERNS) label="done with concerns" ;;
    STARTING|IN_PROGRESS) label="in progress" ;;
    BLOCKED) label="blocked" ;;
    INCOMPLETE) label="incomplete" ;;
    UNTRUSTED) label="untrusted" ;;
    NEEDS_CONTEXT) label="needs context" ;;
    PAUSED|ABORTED) label="$(printf '%s' "$status" | tr '[:upper:]' '[:lower:]')" ;;
    *) label="status unknown" ;;
  esac

  # ── compact one-liner (in a cycle, short replies) ──
  if [ "$tier" = "compact" ]; then
    if [ -n "$awaiting" ]; then
      printf '> %s `%s` · **%s awaiting your answer:** %s\n' "$g_here" "${here:-?}" "$nextmark" "$awaiting"
    elif [ -z "$here" ] && [ "$complete" != "true" ]; then
      # cycle started (CYCLE STARTING ledger entry) but no phase has closed yet
      printf '> %s cycle starting%s → first phase **`%s`**.\n' "$g_here" "${mode:+ (mode \`$mode\`)}" "$_mark"
    elif [ -n "$status" ] && [ "$status" != DONE ] && [ "$status" != DONE_WITH_CONCERNS ]; then
      printf '> %s `%s` %s — reconcile/resume this phase with `/li:resume`; later-phase metadata is not completion.\n' "$g_here" "$here" "$label"
    elif [ -n "$next" ]; then
      printf '> %s `%s` %s → next **`%s`**. Say `go` or `/li:%s`, or `pause`.\n' "$g_here" "${here:-?}" "$label" "$next" "$nl"
    elif [ "$complete" = true ]; then
      printf '> %s `%s` %s — cycle complete.\n' "$g_here" "${here:-?}" "$label"
    else
      printf '> %s `%s` %s — next action unresolved; `/li:resume` to reconcile.\n' "$g_here" "${here:-?}" "$label"
    fi
    return 0
  fi

  # ── full block ──
  printf '> **Lintel cycle**'
  [ -n "$mode" ] && printf ' · mode `%s`' "$mode"
  printf ' · %s\n>\n' "$legend"
  printf '> `%s`\n>\n' "$stepper"

  if [ -n "$awaiting" ]; then
    printf '> **%s Awaiting your answer:** %s\n' "$nextmark" "$awaiting"
    return 0
  fi

  if [ "$started" = "1" ] && [ -z "$here" ]; then
    local _ml; _ml="$(printf '%s' "$_mark" | tr '[:upper:]' '[:lower:]')"
    printf '> **%s You are here:** `%s` (cycle starting)\n' "$g_here" "$_mark"
    printf '> **%s Next:** run `%s` — say `go` or `/li:%s`.\n' "$nextmark" "$_mark" "$_ml"
    return 0
  fi
  printf '> **%s You are here:** `%s` (%s)\n' "$g_here" "${here:-?}" "$label"
  if [ -n "$status" ] && [ "$status" != DONE ] && [ "$status" != DONE_WITH_CONCERNS ]; then
    printf '> **%s Next:** reconcile/resume `%s` via `/li:resume`; do not advance from an incomplete phase.\n' "$nextmark" "$here"
    return 0
  fi
  if [ -n "$next" ]; then
    printf '> **%s Next:** `%s`\n>\n' "$nextmark" "$next"
    printf '> | To do this | Say / type |\n> |---|---|\n'
    printf '> | Continue to %s | `go` or `/li:%s` |\n' "$next" "$nl"
    printf '> | Pause here | `pause` |\n'
  elif [ "$complete" = true ]; then
    printf '> **%s Next:** cycle complete.\n' "$nextmark"
  else
    printf '> **%s Next:** unresolved — `/li:resume` to reconcile completion and the next action.\n' "$nextmark"
  fi
}
