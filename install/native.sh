#!/usr/bin/env bash
# component: native-owned-installation
# implements: ADR-0010, ADR-0028
# intent: .claude/plans/universal-implementation/packages/P10.md
# constraints: Bash 3.2; no Python, network, host activation or whole-root replacement
# last_intent_review: 2026-09-20

native_die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

native_canonical() {
  local path="$1" suffix="" parent part
  local -a components=() raw=()
  case "$path" in [A-Za-z]:*)
    command -v cygpath >/dev/null 2>&1 && path="$(cygpath -u "$path")" ;;
  esac
  case "$path" in /*) ;; *) path="$PWD/$path" ;; esac
  IFS=/ read -r -a raw <<< "$path"
  for part in "${raw[@]}"; do
    case "$part" in
      ''|.) ;;
      ..) [ ${#components[@]} -eq 0 ] || unset "components[$((${#components[@]} - 1))]" ;;
      *) components+=("$part") ;;
    esac
  done
  path="$(IFS=/; printf '/%s' "${components[*]}")"
  while [ ! -d "$path" ]; do
    [ ! -e "$path" ] && [ ! -L "$path" ] || native_die "Directory required: $path"
    suffix="/$(basename "$path")$suffix"
    parent="$(dirname "$path")"
    [ "$parent" != "$path" ] || return 1
    path="$parent"
  done
  printf '%s%s' "$(cd "$path" && pwd -P)" "$suffix"
}

native_identity() {
  case "${OSTYPE:-}" in
    msys*|cygwin*) cygpath -m "$1" ;;
    *) printf '%s\n' "$1" ;;
  esac
}

native_unlinked() {
  local path="$1" cursor="$1" linked
  case "$path" in [A-Za-z]:*|\\\\*)
    path="$(cygpath -u "$path")"; cursor="$path" ;;
  esac
  case "$cursor" in /*) ;; *) cursor="$PWD/$cursor" ;; esac
  local parent
  while [ "$cursor" != / ] && [ -n "$cursor" ]; do
    [ ! -L "$cursor" ] || native_die "Linked path refused: $cursor"
    parent="${cursor%/*}"; parent="${parent:-/}"
    [ "$parent" != "$cursor" ] || break
    cursor="$parent"
  done
  if [ -d "$path" ]; then
    linked="$(find "$path" -type l -print -quit)"
    [ -z "$linked" ] || native_die "Linked install entry refused before writes: $linked"
  fi
}

native_separate() {
  local first="${1%/}/" second="${2%/}/"
  case "${OSTYPE:-}" in msys*|cygwin*)
    first="$(printf '%s' "$first" | tr '[:upper:]' '[:lower:]')"
    second="$(printf '%s' "$second" | tr '[:upper:]' '[:lower:]')" ;;
  esac
  case "$first" in "$second"*) return 1 ;; esac
  case "$second" in "$first"*) return 1 ;; esac
}

native_relative() {
  case "$1" in
    ''|/*|*\\*|*:*|*$'\t'*|*$'\r'*|*$'\n'*|*//*|*/../*|../*|*/..|*/./*|./*|*/.|*/|.git|.git/*|*/.git/*)
      native_die "Unsafe managed path: $1" ;;
  esac
  [[ "$1" != *[[:cntrl:]]* ]] || native_die "Control character in managed path"
  local rest="$1" part stem
  while [ -n "$rest" ]; do
    part="${rest%%/*}"
    case "$part" in *' '|*.) native_die "Nonportable managed path: $1" ;; esac
    stem="${part%%.*}"
    case "$stem" in [cC][oO][nN]|[pP][rR][nN]|[aA][uU][xX]|[nN][uU][lL]|[cC][oO][mM][1-9]|[lL][pP][tT][1-9])
      native_die "Reserved managed path: $1" ;; esac
    case "$rest" in */*) rest="${rest#*/}" ;; *) rest="" ;; esac
  done
}

native_allowed() {
  native_relative "$1"
  case "$1" in
    bin/*|lib/*|templates/*|scaffolding/*|skills/*|agents/*|shims/*|docs/*|hooks/*|install/*|.claude-plugin/plugin.json|LICENSE|AGENT-INSTRUCTIONS.md|README.md|SECURITY.md|CONTRIBUTING.md|CODE_OF_CONDUCT.md|CHANGELOG.md)
      return 0 ;;
    *) native_die "Inventory path outside managed namespaces: $1" ;;
  esac
}

native_safe_file() {
  local root="$1" relative="$2" cursor part rest="$2"
  native_relative "$relative"
  native_unlinked_ancestors "$root"
  cursor="$root"
  while [ -n "$rest" ]; do
    part="${rest%%/*}"; cursor="$cursor/$part"
    [ ! -L "$cursor" ] || native_die "Linked managed path refused: $cursor"
    case "$rest" in
      */*) [ ! -e "$cursor" ] || [ -d "$cursor" ] || native_die "Parent is not a directory: $cursor"
           rest="${rest#*/}" ;;
      *) [ ! -e "$cursor" ] || [ -f "$cursor" ] || native_die "Not a regular file: $cursor"; rest="" ;;
    esac
  done
}

native_unlinked_ancestors() {
  local cursor="$1" parent
  case "$cursor" in [A-Za-z]:*|\\\\*) cursor="$(cygpath -u "$cursor")" ;; esac
  case "$cursor" in /*) ;; *) cursor="$PWD/$cursor" ;; esac
  while [ "$cursor" != / ] && [ -n "$cursor" ]; do
    [ ! -L "$cursor" ] || native_die "Linked path refused: $cursor"
    [ ! -e "$cursor" ] || [ -d "$cursor" ] || native_die "Directory required: $cursor"
    parent="${cursor%/*}"; parent="${parent:-/}"
    [ "$parent" != "$cursor" ] || break
    cursor="$parent"
  done
}

native_directory() {
  native_relative "$2"
  local path="$1/$2"
  native_unlinked_ancestors "$path"
}

native_hash() {
  local value
  case "$NATIVE_HASH" in
    sha256sum) value="$(sha256sum "$1")"; printf '%s\n' "${value%% *}" ;;
    shasum) value="$(shasum -a 256 "$1")"; printf '%s\n' "${value%% *}" ;;
    openssl) value="$(openssl dgst -sha256 "$1")"; printf '%s\n' "${value##* }" ;;
  esac
}

native_size() { local value; value="$(wc -c < "$1")"; printf '%s\n' "${value//[[:space:]]/}"; }
native_mode() { stat -c '%a' "$1" 2>/dev/null || stat -f '%Lp' "$1"; }

native_state() {
  if [ -f "$1" ]; then
    printf '%s\t%s\t%s\n' "$(native_hash "$1")" "$(native_size "$1")" "$(native_mode "$1")"
  else
    [ ! -e "$1" ] && [ ! -L "$1" ] || native_die "Not a regular file: $1"
    printf -- '-\t-\t-\n'
  fi
}

native_match() {
  local path="$1" hash="$2" size="$3" mode="$4" blob="${5:-}"
  if [ "$hash" = - ]; then [ ! -e "$path" ] && [ ! -L "$path" ]; return; fi
  [ -f "$path" ] && [ ! -L "$path" ] &&
    [ "$(native_size "$path")" = "$size" ] &&
    [ "$(native_mode "$path")" = "$mode" ] &&
    [ "$(native_hash "$path")" = "$hash" ] || return 1
  [ -z "$blob" ] || cmp -s "$path" "$blob"
}

native_inventory() {
  local path="$1" hash size relative extra
  [ -f "$path" ] || { [ ! -e "$path" ] || native_die "Inventory is not a file"; return 0; }
  [ "$(head -n 1 "$path")" = $'LINTEL-INSTALL\t1' ] || native_die "Unknown native install inventory; preserve it"
  while IFS=$'\t' read -r hash size relative extra; do
    [ "$hash" != LINTEL-INSTALL ] || continue
    [ -z "$extra" ] && [[ "$hash" =~ ^[a-f0-9]{64}$ ]] && [[ "$size" =~ ^[0-9]+$ ]] ||
      native_die "Malformed native install inventory"
    native_allowed "$relative"
  done < "$path"
  awk -F '\t' 'NR>1 { key=tolower($3); if(seen[key]++) exit 1 }' "$path" ||
    native_die "Duplicate/aliased inventory path"
}

native_cleanup() {
  local rc=$?
  if [ "${NATIVE_LOCKED:-0}" = 1 ]; then rmdir "$NATIVE_STORE/.operation-lock" || rc=1; fi
  if [ -n "${NATIVE_WORK:-}" ] && [ -d "$NATIVE_WORK" ]; then
    case "$(basename "$NATIVE_WORK")" in lintel-install-preflight.*)
      [ "$(cd "$NATIVE_WORK" && pwd -P)" = "$NATIVE_WORK" ] && rm -rf -- "$NATIVE_WORK" ;;
    esac
  fi
  if [ "$rc" -ne 0 ] && [ -n "${NATIVE_TX:-}" ]; then
    printf 'INCOMPLETE: preserve receipt %s; explicit --recover %s --store %s is required.\n' \
      "$NATIVE_TX" "$(basename "$NATIVE_TX")" "$NATIVE_STORE" >&2
  fi
  exit "$rc"
}

native_store_check() {
  local expected="$NATIVE_WORK/owner" file state
  printf 'LINTEL-RECOVERY\t1\n%s\n' "$(native_identity "$NATIVE_TARGET")" > "$expected"
  native_unlinked "$NATIVE_STORE"
  if [ -d "$NATIVE_STORE" ]; then
    [ -f "$NATIVE_STORE/.lintel-recovery-owner" ] &&
      cmp -s "$expected" "$NATIVE_STORE/.lintel-recovery-owner" ||
      native_die "Unowned or foreign recovery store; preserved: $NATIVE_STORE"
  fi
  [ ! -e "$NATIVE_STORE/.operation-lock" ] ||
    native_die "Recovery store locked; verify no process is running before removing that exact empty lock"
  if [ "$NATIVE_COMMAND" != recover ]; then
    local saved_tx="$NATIVE_TX"
    for file in "$NATIVE_STORE"/txn-*; do
      [ -e "$file" ] || continue
      [ -d "$file" ] && [ -f "$file/state" ] || native_die "Unknown/incomplete transaction: $file"
      state="$(cat "$file/state")"
      case "$state" in complete|recovered) ;; *)
        native_die "Incomplete transaction $(basename "$file"); inspect and recover explicitly" ;;
      esac
      NATIVE_TX="$file"
      native_receipt_check evidence-only
    done
    NATIVE_TX="$saved_tx"
  fi
}

native_lock() {
  if [ ! -d "$NATIVE_STORE" ]; then
    mkdir -p "$NATIVE_STORE"
    cp "$NATIVE_WORK/owner" "$NATIVE_STORE/.lintel-recovery-owner"
  fi
  mkdir "$NATIVE_STORE/.operation-lock" || native_die "Recovery store locked; no automatic lock stealing"
  NATIVE_LOCKED=1
}

native_atomic() {
  local blob="$1" relative="$2" mode="$3" temp
  native_safe_file "$NATIVE_TARGET" "$relative"
  mkdir -p "$(dirname "$NATIVE_TARGET/$relative")"
  temp="$(mktemp "$(dirname "$NATIVE_TARGET/$relative")/.lintel-install-write.XXXXXX")"
  cp "$blob" "$temp"
  cmp -s "$blob" "$temp" || native_die "Staged replacement did not verify: $relative"
  chmod "$mode" "$temp"
  native_safe_file "$NATIVE_TARGET" "$relative"
  mv -f "$temp" "$NATIVE_TARGET/$relative"
}

native_record() {
  local temp
  temp="$(mktemp "$(dirname "$1")/.lintel-progress.XXXXXX")"
  printf '%s\n' "$2" > "$temp"
  mv -f "$temp" "$1"
}

native_receipt_check() {
  local key value extra version="" root="" store="" source="" id="" platform="" old=""
  local index bh bs bm ah as am relative phase expected_index=0
  local state evidence_only="${1:-}"
  native_unlinked "$NATIVE_TX"
  [ -d "$NATIVE_TX" ] || native_die "Receipt does not exist"
  [ "$(cat "$NATIVE_TX/receipt.sha256")" = "$(native_hash "$NATIVE_TX/meta.tsv") $(native_hash "$NATIVE_TX/plan.tsv")" ] ||
    native_die "Receipt identity failed; preserve corrupt or unsupported evidence"
  while IFS=$'\t' read -r key value extra; do
    [ -z "$extra" ] || native_die "Malformed receipt metadata"
    case "$key" in
      LINTEL-TRANSACTION) version="$value" ;; root) root="$value" ;; source) source="$value" ;;
      store) store="$value" ;; id) id="$value" ;; platform) platform="$value" ;; inventory_before) old="$value" ;;
      *) native_die "Unknown receipt metadata" ;;
    esac
  done < "$NATIVE_TX/meta.tsv"
  [ "$(wc -l < "$NATIVE_TX/meta.tsv" | tr -d '[:space:]')" = 7 ] &&
    [ "$version" = 1 ] && [ "$root" = "$(native_identity "$NATIVE_TARGET")" ] &&
    [ "$store" = "$(native_identity "$NATIVE_STORE")" ] &&
    [ "$id" = "$(basename "$NATIVE_TX")" ] && [ "$platform" = bash-mode ] && [ -n "$source" ] &&
    { [ "$old" = - ] || [[ "$old" =~ ^[a-f0-9]{64}$ ]]; } ||
      native_die "Foreign/unsupported receipt roots, version or mode projection"
  awk -F '\t' 'NF!=8 {exit 1} {key=tolower($8); if(seen[key]++) exit 1}' "$NATIVE_TX/plan.tsv" ||
    native_die "Malformed or aliased transaction plan"
  state="$(cat "$NATIVE_TX/state")"
  case "$state" in prepared|applying|complete|recovering|recovered) ;; *) native_die "Unknown transaction state" ;; esac
  while IFS=$'\t' read -r index bh bs bm ah as am relative; do
    [ "$index" = "$(printf '%06d' "$expected_index")" ] || native_die "Invalid transaction index"
    expected_index=$((expected_index+1))
    native_relative "$relative"
    [ "$evidence_only" = evidence-only ] || native_safe_file "$NATIVE_TARGET" "$relative"
    case "$relative" in .lintel-install.tsv|config.yaml|profile.yaml|packs/active-pack|packs/_default/*|brand/design-patterns/*) ;;
      *) native_allowed "$relative" ;;
    esac
    for key in before after; do
      if [ "$key" = before ]; then value="$bh"; size="$bs"; mode="$bm"; else value="$ah"; size="$as"; mode="$am"; fi
      if [ "$value" = - ]; then
        [ "$size" = - ] && [ "$mode" = - ] && [ ! -e "$NATIVE_TX/$key/$index" ] ||
          native_die "Unexpected absent-file blob"
      else
        [[ "$value" =~ ^[a-f0-9]{64}$ ]] && [[ "$size" =~ ^[0-9]+$ ]] && [[ "$mode" =~ ^[0-7]{3,4}$ ]] ||
          native_die "Invalid planned file state"
        [ -f "$NATIVE_TX/$key/$index" ] &&
          [ "$(native_hash "$NATIVE_TX/$key/$index")" = "$value" ] &&
          [ "$(native_size "$NATIVE_TX/$key/$index")" = "$size" ] || native_die "Receipt blob failed verification: $relative"
      fi
    done
    phase="$(cat "$NATIVE_TX/phase/$index")"
    case "$phase" in pending|applying|applied|restoring|restored) ;; *) native_die "Unknown file progress" ;; esac
    case "$state:$phase" in
      prepared:pending|applying:pending|applying:applying|applying:applied|complete:applied|recovering:*|recovered:restored) ;;
      *) native_die "Transaction state contradicts per-file progress" ;;
    esac
  done < "$NATIVE_TX/plan.tsv"
  [ "$expected_index" -gt 0 ] || native_die "Empty transaction receipt"
  value="$(awk -F '\t' '$8==".lintel-install.tsv" {print $2}' "$NATIVE_TX/plan.tsv")"
  if [ -n "$value" ]; then
    [ "$value" = "$old" ] || native_die "Inventory identity differs from the snapshot plan"
    [ "$(tail -n 1 "$NATIVE_TX/plan.tsv" | awk -F '\t' '{print $8}')" = .lintel-install.tsv ] ||
      native_die "Inventory must be published last"
  elif [ "$evidence_only" != evidence-only ]; then
    value=-
    [ ! -f "$NATIVE_TARGET/.lintel-install.tsv" ] || value="$(native_hash "$NATIVE_TARGET/.lintel-install.tsv")"
    [ "$value" = "$old" ] || native_die "Inventory changed outside this transaction"
  fi
}

native_recover() {
  local index bh bs bm ah as am relative phase
  native_receipt_check
  while IFS=$'\t' read -r index bh bs bm ah as am relative; do
    phase="$(cat "$NATIVE_TX/phase/$index")"
    if native_match "$NATIVE_TARGET/$relative" "$bh" "$bs" "$bm" "$NATIVE_TX/before/$index"; then
      continue
    fi
    case "$phase" in pending|restored) native_die "Recovery permission absent/consumed; current bytes preserved: $relative" ;; esac
    native_match "$NATIVE_TARGET/$relative" "$ah" "$as" "$am" "$NATIVE_TX/after/$index" ||
      native_die "Recovery conflict; current bytes preserved: $relative"
  done < "$NATIVE_TX/plan.tsv"
  native_lock
  native_record "$NATIVE_TX/state" recovering
  while IFS=$'\t' read -r index bh bs bm ah as am relative; do
    native_safe_file "$NATIVE_TARGET" "$relative"
    if ! native_match "$NATIVE_TARGET/$relative" "$bh" "$bs" "$bm" "$NATIVE_TX/before/$index"; then
      phase="$(cat "$NATIVE_TX/phase/$index")"
      [ "$phase" != restored ] && [ "$phase" != pending ] &&
        native_match "$NATIVE_TARGET/$relative" "$ah" "$as" "$am" "$NATIVE_TX/after/$index" ||
        native_die "Recovery conflict after preflight: $relative"
      native_record "$NATIVE_TX/phase/$index" restoring
      if [ "$bh" = - ]; then rm "$NATIVE_TARGET/$relative"; else native_atomic "$NATIVE_TX/before/$index" "$relative" "$bm"; fi
    fi
    native_match "$NATIVE_TARGET/$relative" "$bh" "$bs" "$bm" "$NATIVE_TX/before/$index" ||
      native_die "Restored file did not verify: $relative"
    native_record "$NATIVE_TX/phase/$index" restored
  done < "$NATIVE_TX/plan.tsv"
  while IFS=$'\t' read -r index bh bs bm ah as am relative; do
    native_safe_file "$NATIVE_TARGET" "$relative"
    native_match "$NATIVE_TARGET/$relative" "$bh" "$bs" "$bm" "$NATIVE_TX/before/$index" ||
      native_die "Restored set changed before completion: $relative"
  done < "$NATIVE_TX/plan.tsv"
  native_record "$NATIVE_TX/state" recovered
  printf 'Recovery verified: %s. Empty created directories and receipt evidence were retained.\n' "$(basename "$NATIVE_TX")"
}

native_plan_file() {
  local relative="$1" candidate="$2" old_hash="$3" kind="$4"
  local bh bs bm ah=- as=- am=- index path="$NATIVE_TARGET/$1"
  native_safe_file "$NATIVE_TARGET" "$relative"
  IFS=$'\t' read -r bh bs bm <<< "$(native_state "$path")"
  if [ "$candidate" != - ]; then
    ah="$(native_hash "$candidate")"; as="$(native_size "$candidate")"
    am="$bm"; [ "$am" != - ] || am="$(native_mode "$candidate")"
  fi
  if [ "$kind" = managed ]; then
    if [ "$old_hash" != - ] && [ "$bh" != - ] && [ "$bh" != "$old_hash" ]; then
      native_die "Modified managed file (preserved): $relative"
    fi
    if [ "$old_hash" = - ] && [ "$bh" != - ] && [ "$bh" != "$ah" ]; then
      native_die "Unmanaged collision (preserved): $relative"
    fi
  elif [ "$kind" = seed ] && [ "$bh" != - ]; then
    return 0
  fi
  [ "$bh" != "$ah" ] || return 0
  index="$(printf '%06d' "$NATIVE_COUNT")"; NATIVE_COUNT=$((NATIVE_COUNT+1))
  if [ "$bh" != - ]; then cp "$path" "$NATIVE_WORK/receipt/before/$index"; cmp -s "$path" "$NATIVE_WORK/receipt/before/$index"; fi
  if [ "$ah" != - ]; then cp "$candidate" "$NATIVE_WORK/receipt/after/$index"; cmp -s "$candidate" "$NATIVE_WORK/receipt/after/$index"; fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$index" "$bh" "$bs" "$bm" "$ah" "$as" "$am" "$relative" >> "$NATIVE_WORK/receipt/plan.tsv"
  printf 'pending\n' > "$NATIVE_WORK/receipt/phase/$index"
}

native_install() {
  local component file relative hash size old_hash kind index bh bs bm ah as am
  local inventory="$NATIVE_TARGET/.lintel-install.tsv" old_inventory=-
  source "$NATIVE_EXEC_SOURCE/lib/frontmatter.sh"
  [ -s "$NATIVE_SOURCE/install/directories.txt" ] || native_die "Native directory-slot contract is missing/empty"
  while IFS= read -r relative; do native_directory "$NATIVE_TARGET" "$relative"; done < "$NATIVE_SOURCE/install/directories.txt"
  for component in scaffolding lib bin templates skills agents shims docs hooks install packs/_default; do
    [ -d "$NATIVE_SOURCE/$component" ] || native_die "Missing source component: $component"
    native_unlinked "$NATIVE_SOURCE/$component"
  done
  for file in LICENSE AGENT-INSTRUCTIONS.md README.md SECURITY.md CONTRIBUTING.md CODE_OF_CONDUCT.md CHANGELOG.md .claude-plugin/plugin.json install/layer-config.yaml.example; do
    [ -f "$NATIVE_SOURCE/$file" ] && [ ! -L "$NATIVE_SOURCE/$file" ] || native_die "Missing/linked required source: $file"
  done
  while IFS= read -r -d '' file; do
    kind=agent; case "$file" in */SKILL.md) kind=skill ;; */README.md) continue ;; esac
    validate_lintel_frontmatter "$file" "$kind" || native_die "Invalid source frontmatter: $file"
  done < <(find "$NATIVE_SOURCE/skills" "$NATIVE_SOURCE/agents" "$NATIVE_SOURCE/scaffolding" \
    \( -name SKILL.md -o -path '*/agents/*.md' -o -path '*/agents/*/*.md' \) -type f -print0)
  native_safe_file "$NATIVE_TARGET" .lintel-install.tsv
  native_inventory "$inventory"
  [ ! -f "$inventory" ] || old_inventory="$(native_hash "$inventory")"
  mkdir -p "$NATIVE_WORK/receipt/before" "$NATIVE_WORK/receipt/after" "$NATIVE_WORK/receipt/phase"
  : > "$NATIVE_WORK/receipt/plan.tsv"; : > "$NATIVE_WORK/files"
  for component in scaffolding lib bin templates skills agents shims docs hooks install; do
    while IFS= read -r -d '' file; do
      relative="${file#"$NATIVE_SOURCE/"}"
      case "$relative" in */__pycache__/*|*.pyc) continue ;; esac
      native_allowed "$relative"
      printf '%s\n' "$relative" >> "$NATIVE_WORK/files"
    done < <(find "$NATIVE_SOURCE/$component" -type f -print0)
  done
  printf '%s\n' LICENSE AGENT-INSTRUCTIONS.md README.md SECURITY.md CONTRIBUTING.md CODE_OF_CONDUCT.md CHANGELOG.md .claude-plugin/plugin.json >> "$NATIVE_WORK/files"
  LC_ALL=C sort -u "$NATIVE_WORK/files" > "$NATIVE_WORK/sorted"
  awk '{key=tolower($0); if(seen[key]++) exit 1}' "$NATIVE_WORK/sorted" || native_die "Aliased source paths"
  printf 'LINTEL-INSTALL\t1\n' > "$NATIVE_WORK/new-inventory"
  NATIVE_COUNT=0
  while IFS= read -r relative; do
    old_hash=-
    if [ -f "$inventory" ]; then old_hash="$(awk -F '\t' -v p="$relative" '$3==p {print $1}' "$inventory")"; old_hash="${old_hash:--}"; fi
    hash="$(native_hash "$NATIVE_SOURCE/$relative")"; size="$(native_size "$NATIVE_SOURCE/$relative")"
    printf '%s\t%s\t%s\n' "$hash" "$size" "$relative" >> "$NATIVE_WORK/new-inventory"
    native_plan_file "$relative" "$NATIVE_SOURCE/$relative" "$old_hash" managed
  done < "$NATIVE_WORK/sorted"
  if [ -f "$inventory" ]; then
    while IFS=$'\t' read -r hash size relative; do
      [ "$hash" != LINTEL-INSTALL ] || continue
      if ! grep -Fxq "$relative" "$NATIVE_WORK/sorted"; then native_plan_file "$relative" - "$hash" managed; fi
    done < "$inventory"
  fi
  printf '# Lintel operator preferences; edit freely\nactive_pack: _default\ndefault_mode: internal-tool\nrole_active: none\n' > "$NATIVE_WORK/profile"
  printf '_default\n' > "$NATIVE_WORK/pointer"
  native_plan_file config.yaml "$NATIVE_SOURCE/install/layer-config.yaml.example" - seed
  native_plan_file profile.yaml "$NATIVE_WORK/profile" - seed
  native_plan_file packs/active-pack "$NATIVE_WORK/pointer" - seed
  while IFS= read -r -d '' file; do
    relative="${file#"$NATIVE_SOURCE/"}"
    native_plan_file "$relative" "$file" - seed
  done < <(find "$NATIVE_SOURCE/packs/_default" -type f -print0)
  if [ -d "$NATIVE_SOURCE/seeds/brand/design-patterns" ]; then
    native_unlinked "$NATIVE_SOURCE/seeds/brand"
    while IFS= read -r -d '' file; do
      relative="${file#"$NATIVE_SOURCE/seeds/"}"
      native_plan_file "$relative" "$file" - seed
    done < <(find "$NATIVE_SOURCE/seeds/brand/design-patterns" -type f -print0)
  fi
  native_plan_file .lintel-install.tsv "$NATIVE_WORK/new-inventory" "$old_inventory" inventory
  if [ "$NATIVE_COUNT" = 0 ]; then
    while IFS= read -r relative; do
      native_directory "$NATIVE_TARGET" "$relative"
      mkdir -p "$NATIVE_TARGET/$relative"
    done < "$NATIVE_SOURCE/install/directories.txt"
    printf 'Install complete: managed bytes and directory slots verified; customizations preserved.\n'
    return 0
  fi
  native_lock
  local identifier="txn-$(date -u +%Y%m%dT%H%M%S)-$RANDOM-$RANDOM"
  [ ! -e "$NATIVE_STORE/$identifier" ] || native_die "Receipt ID collision"
  NATIVE_TX="$NATIVE_STORE/$identifier"
  printf 'LINTEL-TRANSACTION\t1\nroot\t%s\nsource\t%s\nstore\t%s\nid\t%s\nplatform\tbash-mode\ninventory_before\t%s\n' \
    "$(native_identity "$NATIVE_TARGET")" "$(native_identity "$NATIVE_SOURCE")" "$(native_identity "$NATIVE_STORE")" \
    "$identifier" "$old_inventory" > "$NATIVE_WORK/receipt/meta.tsv"
  printf '%s %s\n' "$(native_hash "$NATIVE_WORK/receipt/meta.tsv")" "$(native_hash "$NATIVE_WORK/receipt/plan.tsv")" > "$NATIVE_WORK/receipt/receipt.sha256"
  printf 'prepared\n' > "$NATIVE_WORK/receipt/state"
  mv "$NATIVE_WORK/receipt" "$NATIVE_TX"
  native_receipt_check
  while IFS=$'\t' read -r index bh bs bm ah as am relative; do
    native_match "$NATIVE_TARGET/$relative" "$bh" "$bs" "$bm" "$NATIVE_TX/before/$index" ||
      native_die "Target changed after preflight: $relative"
  done < "$NATIVE_TX/plan.tsv"
  mkdir -p "$NATIVE_TARGET"
  native_record "$NATIVE_TX/state" applying
  while IFS= read -r relative; do
    native_directory "$NATIVE_TARGET" "$relative"
    mkdir -p "$NATIVE_TARGET/$relative"
  done < "$NATIVE_SOURCE/install/directories.txt"
  while IFS=$'\t' read -r index bh bs bm ah as am relative; do
    native_safe_file "$NATIVE_TARGET" "$relative"
    native_match "$NATIVE_TARGET/$relative" "$bh" "$bs" "$bm" "$NATIVE_TX/before/$index" ||
      native_die "Target changed before mutation: $relative"
    native_record "$NATIVE_TX/phase/$index" applying
    if [ "$ah" = - ]; then rm "$NATIVE_TARGET/$relative"; else native_atomic "$NATIVE_TX/after/$index" "$relative" "$am"; fi
    native_match "$NATIVE_TARGET/$relative" "$ah" "$as" "$am" "$NATIVE_TX/after/$index" ||
      native_die "Published file failed verification: $relative"
    native_record "$NATIVE_TX/phase/$index" applied
  done < "$NATIVE_TX/plan.tsv"
  while IFS=$'\t' read -r index bh bs bm ah as am relative; do
    native_safe_file "$NATIVE_TARGET" "$relative"
    native_match "$NATIVE_TARGET/$relative" "$ah" "$as" "$am" "$NATIVE_TX/after/$index" ||
      native_die "Installed result changed before completion: $relative"
  done < "$NATIVE_TX/plan.tsv"
  native_record "$NATIVE_TX/state" complete
  printf 'Install complete: verified %s file mutations at %s.\nRecovery receipt: %s\nNo hooks or host plugins were activated.\n' "$NATIVE_COUNT" "$NATIVE_TARGET" "$NATIVE_TX"
}

lintel_native_main() {
  NATIVE_EXEC_SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
  NATIVE_SOURCE="$NATIVE_EXEC_SOURCE"; NATIVE_TARGET="${LINTEL_HOME:-$HOME/.lintel}"
  NATIVE_STORE="${LINTEL_RECOVERY_STORE:-}"; NATIVE_COMMAND=install; NATIVE_ID=""
  NATIVE_WORK=""; NATIVE_TX=""; NATIVE_LOCKED=0; NATIVE_HASH=""
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --source|--home|--store|--recover)
        [ -n "${2:-}" ] || native_die "$1 requires a value"
        case "$1" in --source) NATIVE_SOURCE="$2" ;; --home) NATIVE_TARGET="$2" ;;
          --store) NATIVE_STORE="$2" ;; --recover) NATIVE_ID="$2"; NATIVE_COMMAND=recover ;; esac
        shift 2 ;;
      --check) NATIVE_COMMAND=check; shift ;;
      --help|-h) printf 'Usage: install.sh [--source PATH] [--home PATH] [--store PATH] [--check | --recover ID]\nNative install/recovery needs Git, Bash and SHA-256, not Python. No automatic host activation.\n'; return ;;
      *) native_die "Unknown argument: $1" ;;
    esac
  done
  command -v git >/dev/null 2>&1 || native_die "git is required"
  for candidate in sha256sum shasum openssl; do
    if command -v "$candidate" >/dev/null 2>&1; then NATIVE_HASH="$candidate"; break; fi
  done
  [ -n "$NATIVE_HASH" ] || native_die "SHA-256 utility unavailable; no files changed"
  case "$NATIVE_SOURCE$NATIVE_TARGET$NATIVE_STORE" in *$'\t'*|*$'\r'*|*$'\n'*) native_die "Control character in roots" ;; esac
  native_unlinked_ancestors "$NATIVE_TARGET"
  NATIVE_SOURCE="$(native_canonical "$NATIVE_SOURCE")"
  NATIVE_TARGET="$(native_canonical "$NATIVE_TARGET")"
  [ "$NATIVE_TARGET" != / ] && [ "$NATIVE_TARGET" != "$(native_canonical "$HOME")" ] ||
    native_die "Target must not be a filesystem/user-home root or overlap the source checkout"
  if [ "$NATIVE_COMMAND" = install ]; then
    native_separate "$NATIVE_SOURCE" "$NATIVE_TARGET" || native_die "LINTEL_HOME must be separate from the source checkout"
  fi
  NATIVE_STORE="${NATIVE_STORE:-$NATIVE_TARGET-recovery}"
  native_unlinked_ancestors "$NATIVE_STORE"
  NATIVE_STORE="$(native_canonical "$NATIVE_STORE")"
  native_separate "$NATIVE_TARGET" "$NATIVE_STORE" && native_separate "$NATIVE_SOURCE" "$NATIVE_STORE" ||
    native_die "Recovery store must be separate from source and target"
  native_unlinked "$NATIVE_TARGET"
  umask 077
  NATIVE_WORK="$(mktemp -d "${TMPDIR:-/tmp}/lintel-install-preflight.XXXXXX")"
  NATIVE_WORK="$(cd "$NATIVE_WORK" && pwd -P)"
  trap native_cleanup EXIT
  native_store_check
  printf 'Source: %s\nInstalled data: %s\nRecovery store: %s\n' "$NATIVE_SOURCE" "$NATIVE_TARGET" "$NATIVE_STORE"
  case "$NATIVE_COMMAND" in
    install) native_install ;;
    recover)
      [[ "$NATIVE_ID" =~ ^txn-[A-Za-z0-9-]+$ ]] || native_die "Unsupported receipt ID; historical copies require manual recovery"
      NATIVE_TX="$NATIVE_STORE/$NATIVE_ID"
      native_recover ;;
    check)
      [ -f "$NATIVE_TARGET/.lintel-install.tsv" ] || native_die "Native inventory missing; installation is unverified"
      native_inventory "$NATIVE_TARGET/.lintel-install.tsv"
      while IFS=$'\t' read -r hash size relative; do
        [ "$hash" != LINTEL-INSTALL ] || continue
        native_safe_file "$NATIVE_TARGET" "$relative"
        [ -f "$NATIVE_TARGET/$relative" ] && [ "$(native_hash "$NATIVE_TARGET/$relative")" = "$hash" ] &&
          [ "$(native_size "$NATIVE_TARGET/$relative")" = "$size" ] || native_die "Managed-file drift: $relative"
      done < "$NATIVE_TARGET/.lintel-install.tsv"
      printf 'Installed managed bytes verified. Host activation remains unverified.\n' ;;
  esac
}
