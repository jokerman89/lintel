# Optional CAPTURE vault export

This owns the complete Step 7b procedure. Load it only when the current verified
profile enables `capture.vault_sink_enabled`. Enabling the sink is not destination
or data-transfer permission; the existing destination must also be authorized.
An absent, disabled or unavailable sink does not activate any other CAPTURE step.

### Step 7b — Vault sink (session summary → knowledge vault)

Config-gated, optional, NEVER blocking. Writes a short human-readable session summary to an
external knowledge vault (e.g. an Obsidian vault) so the vault becomes the cross-repo memory
layer. The repo's own capture artifacts (Steps 1–7) are unaffected — this is an additional
sink, not a move. Nothing is ever read back from the vault into the repo.

```bash
source_root="${LINTEL_SOURCE_ROOT:?select trusted source}"
sink_dir=""
if ! source "$source_root/lib/pack-resolver.sh"; then
  echo "[lintel/capture] WARN: vault policy helper unavailable — export not performed" >&2
elif ! sink_enabled=$(resolve_pack_field capture.vault_sink_enabled); then
  echo "[lintel/capture] WARN: vault policy unresolved — export not performed" >&2
elif [ "$sink_enabled" != "true" ]; then
  : # disabled — no destination lookup or write
elif [ -z "${LINTEL_REPO_ROOT:-}" ]; then
  echo "[lintel/capture] WARN: working repository is not selected — export not performed" >&2
elif ! source "$source_root/bin/_audit.sh"; then
  echo "[lintel/capture] WARN: vault audit writer unavailable — export not performed" >&2
elif ! sink_path=$(resolve_pack_field capture.vault_sink_path); then
  echo "[lintel/capture] WARN: vault destination unresolved — export not performed" >&2
else
  capture_repo="$(lintel_repo_root)"
  if [ -n "$sink_path" ]; then
    case "$sink_path" in
      /*|[A-Za-z]:*) sink_dir="$sink_path" ;;
      *) sink_dir="$capture_repo/$sink_path" ;;
    esac
  fi
  if [ -z "$sink_dir" ] || [ ! -d "$sink_dir" ]; then
    echo "[lintel/capture] WARN: vault_sink path not found: $sink_path — skipping vault export" >&2
    audit_log capture vault_sink_skipped "reason=path_missing" "path=$sink_path"
    sink_dir=""
  fi
fi
# A missing or disabled vault must NEVER fail CAPTURE — one-line warn, then move on.
```

Only when `sink_dir` is nonempty and this destination is already authorized, write
exactly ONE file per session at `<sink_dir>/YYYY-MM-DD-<repo>-<short-slug>.md`.
Do not create a destination, search a personal vault, or depend on dormant
calibration initializing shell variables:

```markdown
---
created: YYYY-MM-DD
tags: [session]
type: session
repo: <repo-name>
branch: <git-branch>
outcome: shipped | in-progress | blocked | exploration
session: <cycle-id-if-available>
---
# <one-line session title>

## What was done
<3–8 lines, plain language, no code dumps>

## Decisions
<decisions taken, one line each; "None" if none>

## Open threads
<unfinished items / next steps; "None" if none>

## Pointers
- <repo-relative paths to the key files/PRs touched>

## Links
- [[<repo-name>]] <- the repo hub note (backlinks = per-repo session history)
- [[<previous session note name>]] <- predecessor, if one exists for this repo
```

The frontmatter is a LOCKED flat schema (ADR-0007) — `sessions.base` (the Bases dashboard
installed by `bin/li-vault-init`) and the vault's own skills query these exact properties.
`outcome` uses the controlled vocabulary above, nothing else.

**After writing the note, maintain the two navigation surfaces (same sink dir):**
1. **Hub note** `<sink_dir>/<repo-name>.md` — create a minimal one if missing (frontmatter:
   `created:`, `tags: [hub]`, `type: repo-hub`, `repo:`; one line of prose — same shape
   bin/li-vault-init writes). Never overwrite an existing hub.
2. **Index** `<sink_dir>/00-index.md` — create it if missing (frontmatter `type: session-index`
   + one intro line), then maintain the list under its heading: carry the existing entries
   forward, PREPEND this session's line, truncate to 15:
   `- [[<note-name>]] - <one-line title> (<repo>)`. Keep frontmatter + intro intact; touch only
   the list. (Carrying forward the index's own lines is the one sanctioned vault read — never
   read other notes back.)

Source the content from the Step 1 cycle aggregation. **Hard rules:** no secrets or tokens, no
customer or employer-internal data, no full file contents — repo-relative pointers instead of
payloads. Render the headings AND body in the session's working language (the template above is
the canonical English form — translate it wholesale when the session ran in another language).
Frontmatter must parse.

**MANDATORY pre-write scan (battletest K4 — the vault note lands OUTSIDE the repo, where no
git-commit hook sees it).** The "hard rules" above are not enough on their own — scan the
rendered note body programmatically before writing, and ABORT the export (warn, never fail
CAPTURE) on any hit, failed load/read or unavailable scanner:

```bash
vault_scan_ready=false
vault_export_skip() {
  local reason="$1"
  shift
  printf '[lintel/capture] WARN: vault export skipped (%s); no clean scan inferred.\n' "$reason" >&2
  if command -v audit_log >/dev/null 2>&1; then
    audit_log capture vault_sink_skipped "reason=$reason" "$@" ||
      printf '[lintel/capture] WARN: skip audit was not recorded.\n' >&2
  else
    printf '[lintel/capture] WARN: skip audit writer unavailable.\n' >&2
  fi
}
if [ -z "${LINTEL_SOURCE_ROOT:-}" ] ||
   ! source "$LINTEL_SOURCE_ROOT/hooks/shared/_patterns.sh"; then
  vault_export_skip scanner_load_failed
elif [ -z "${rendered_note:-}" ] || ! note_body="$(cat < "$rendered_note")"; then
  vault_export_skip note_read_failed
elif ! command -v scan_secrets >/dev/null 2>&1 ||
     ! command -v scan_customer >/dev/null 2>&1; then
  vault_export_skip scanner_unavailable
elif ! sec_hits="$(scan_secrets all "$note_body")"; then
  vault_export_skip secret_scan_failed
elif ! pii_hits="$(scan_customer "$note_body")"; then
  vault_export_skip customer_scan_failed
elif [ -n "$sec_hits$pii_hits" ]; then
  vault_export_skip sensitive_content "secrets=$sec_hits" "pii=$pii_hits"
else
  vault_scan_ready=true
fi
printf 'vault_scan_ready=%s\n' "$vault_scan_ready"
```

Only `vault_scan_ready=true` permits the separately authorized note publication.
This is scan readiness, not a file-write receipt or complete content-safety
guarantee. Publish only the same rendered content that was scanned; changed
content requires a new scan. On a hit, do NOT sanitize-and-ship.
After the actual owned write and successful readback, record
`audit_log capture vault_sink_written "file=<actual-filename>"`; never emit that
event merely because the scans ran. A false result skips the optional export
and leaves the independent repository CAPTURE work available.
