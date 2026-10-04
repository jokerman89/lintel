# Local inspection

Doctor owns these shared read-only procedures for `doctor`, `instruction-parity-check`,
`migrations` and maintenance's path view. Use the existing lifecycle/instruction/adapter
helpers; no new doctor subcommands, detectors or policy engine are implied. Mutation
and recovery are separate authorized operations, never a diagnostic side effect.

Use for onboarding, failed discovery, suspected drift, update diagnosis and local health
checks. The skill is a front door to the actual helper, not a second set of speculative
client probes. [Lifecycle paths](../../../docs/lifecycle.md) define the roots.

## Inputs and health views

| Option | Behavior |
|---|---|
| No option | Readable local diagnosis of the selected source and target |
| `--json` | Return the actual complete helper JSON and its exit status |
| `--quick` / `--fast` | Pass `--quick` to the existing local diagnostic |
| `--verbose` | Pass the existing verbose option |
| `--layers-only` | Present source, foundation, layout and adapter fields |
| `--hooks-only` | Present known hook-byte comparisons and unverified activation |
| `--upstream-only` | Inspect declared installed-source provenance, if present |

Select at most one filtered view. Filtering presentation never discards an issue from
another section or changes the helper's exit code. `--json` preserves the full schema
even with a view request; do not invent a second health response format.

## Run the owned diagnostic

This block receives the selected skill flags as literal arguments. It obtains complete
JSON for interpretation; render the requested human view afterward unless `--json` was
requested. Source and target are the explicit trusted/working roots.

```bash
doctor_args=(--source "${LINTEL_SOURCE_ROOT:?select the trusted source}" \
  --target "${LINTEL_REPO_ROOT:?select the working target}" --json)
doctor_view=all
for option in "$@"; do
  case "$option" in
    --json) ;;
    --quick|--fast) doctor_args+=(--quick) ;;
    --verbose) doctor_args+=(--verbose) ;;
    --layers-only|--hooks-only|--upstream-only)
      [ "$doctor_view" = all ] || { echo 'Select one diagnostic view.' >&2; exit 2; }
      doctor_view="$option" ;;
    *) echo "Unknown doctor option: $option" >&2; exit 2 ;;
  esac
done
doctor_status=0
bash "$LINTEL_SOURCE_ROOT/bin/li-doctor" "${doctor_args[@]}" || doctor_status=$?
exit "$doctor_status"
```

For a direct helper invocation, omit `--json` for its readable sections. No argument
executes native plugin-list/update commands or fetches remote data.
Exit 0 means the reported local checks passed, 1 means local issues need attention, and
2 means the invocation or required diagnostic could not run. Preserve the actual code.

The helper reports source product metadata, exact source/target/data roots, executable
availability, effective profile/reference or error, foundation/layout state and actual
repository-adapter check results. It compares known installed hook **bytes**, not
directory counts. Consumer-added files remain visible and untouched.

## Provenance and configured assets

For `--upstream-only`, read the approved source's `install/upstream-sources.yaml` and
public provenance when present. A portable bundle may omit that declaration; report
the view as unavailable, not healthy. Declared repositories and license names are
not downloaded clones, fresh remote checks or legal clearance. Do not invent an
upstream execution path or fetch/install anything during diagnosis.

When explicitly requested, inspect configured brand/voice assets and dated calibration
through the actual pack field provenance. Missing corpus/calibration is unverified or
not configured, not a fabricated pending count. `install/verify.sh`, when available in
the approved source, remains a separate source/frontmatter/structure check; it does not
prove installed ownership, discovery or policy enforcement.

## Interpret evidence honestly

Cached plugin versions are candidates, never proof of the active version. A binary in
PATH is not a discovered plugin. Hook files, settings declarations and historical audit
logs are not evidence that a hook ran in this session. The helper reports activation and
current hook execution as unverified; it never guesses a plugin directory, substring
identity, marker convention or desktop/CLI equivalence.

For a real host question, inspect that surface's actual discovery/settings using its
available authorized tools. Name the exact host/version, operation, observed result and
permission limits. Do not run an external command just because its spelling appears in
an old skill or cache. Existing `li-update` retains its real child-failure semantics;
updates are separate authorized operations, not a diagnostic side effect.

## Route repairs, do not perform them implicitly

- Missing foundation: `/li:scaffold` calls the owned helper for the selected target.
- Profile drift or failed required policy: preserve the pin/history; explicitly rebind
  and replan only when authorized. Never choose neutral to make health look green.
- Layout conflict or interruption: use the migration/install receipt's explicit recovery
  path. Do not stamp a marker, move repositories, copy whole trees or roll back on sight.
- Hook/host concerns: preserve optional hooks; installation does not register them.

Instruction parity and migration inspection follow the procedures below when their
source/target files exist. Reuse an actual doctor `adapter` or `layout` result from
the same input snapshot rather than running a duplicate consumer check. A stale,
missing or changed result must be refreshed, not assumed current.
Brand/corpus calibration and provenance/license freshness
remain read-only follow-ups against actual configured files and dated metadata, not
fixed counts, assumed upstream clones or invented calibration.

Report checks actually performed, diagnostics, preserved files and unverified host
boundaries. Source product, pack release and schema versions remain distinct.

## Instruction parity

`instruction-parity-check` retains this read-only verification method. Under ADR-0025,
`scaffolding/01-foundation/SESSION-PROTOCOL.md` is the complete shared source. Marked
blocks in root AGENTS.md, CLAUDE.md and both foundation templates must match it exactly.
Short client pointers intentionally differ: verify links to authority, not six similar
files or a fuzzy word-similarity target. Preserve all client-specific/project prose.

1. Identify the exact working repository and trusted source bundle. Read actual entry
   files, the adapter inventory and referenced source. Keep requirements, ownership,
   human approvals, original work IDs and host permission boundaries separate.
2. In a contributor source checkout, run its real checker from that root:

   ```bash
   : "${LINTEL_SOURCE_ROOT:?select trusted source}"
   [ -f "$LINTEL_SOURCE_ROOT/bin/li-instructions.py" ] || {
     echo 'UNAVAILABLE: trusted source instruction checker is missing.' >&2; exit 2;
   }
   (cd "$LINTEL_SOURCE_ROOT" && python3 -B bin/li-instructions.py check)
   ```

   Exact block comparisons, malformed-marker failures and preservation tests implement
   synchronization. A missing checker or failed command is unverified, not replaced
   by character counts. This checks contributor source, not arbitrary target prose.
3. For an installed consumer, reuse doctor's actual `adapter` check when its input
   snapshot is still current. Otherwise invoke the existing trusted adapter directly:

   ```bash
   : "${LINTEL_SOURCE_ROOT:?select trusted source}"
   : "${LINTEL_REPO_ROOT:?select working target}"
   [ -f "$LINTEL_SOURCE_ROOT/bin/li-adapter.py" ] || {
     echo 'UNAVAILABLE: trusted repository adapter is missing.' >&2; exit 2;
   }
   python3 -B "$LINTEL_SOURCE_ROOT/bin/li-adapter.py" check \
     --source "$LINTEL_SOURCE_ROOT" --target "$LINTEL_REPO_ROOT"
   ```

   In a portable kit this source is `.github/lintel`, not an arbitrary target helper.
   The preserved `li-copilot.py check` entry remains compatible. Check every selected
   surface's records; installed files do not prove host discovery.
4. Read the remaining short pointers and host notes for contradictions in authority,
   data handling, permissions, independent review, source/target roots and hook claims.
   Cite actual file:line. This judgment is not a claim that CI ran it.
5. Report exact commands/exits, mismatched blocks/links, preserved project prose and
   live-host limits. No missing or unreadable entry lowers the check to a clean partial
   pass; keep independent review separate from the implementer's self-check.

Propose repairs at canonical source. `li-instructions.py sync` and adapter regeneration
require their own write authority; the coordinator owns shared generated outputs in
coordinated work. Never manually patch a generated protocol block or erase local edits
to pass `check`. Existing `tests/shape/session-protocol-parity.sh` and adapter integration
tests remain the evidence sources, not an invented `li-doctor --instructions` flag.

## Migrations

The retained `migrations` front door uses the real source catalog reader:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" migrations
```

Add `--all` to include archived records. Read trusted `docs/migrations/_INDEX.md`,
not a same-named target catalog. The accepted Markdown provider excludes examples and
quoted rows and never executes `detect_pattern`, shell fragments or catalog prose.

Keep the schedule (`open`, `overdue`, `archived`) separate from target observations
(`current`, `needs_migration`, `incomplete`, `not_applicable`, `unknown`). The shared
layout reader checks actual marker, legacy files and retained redirect stubs. Where
doctor already returned that same current observation, reuse it rather than a second
handwritten path manifest. No detector means unknown plus a guide, not complete.
Missing/malformed catalogs are errors, not an empty migration backlog.

An expired grace period never removes unresolved migrations, aliases or backups.
Archived schedule means history, not target completion; v4/v5 engineering names do
not identify the public product version.

### Explicit execution and recovery

For v5 layout, first inspect the existing source-owned
`bin/li-migrate-claude-home --dry-run --repo <target>`. Apply only the authorized
helper operation, retain its receipt and use explicit recovery if interrupted.
Do not replace it with shell moves/copies, stamp a marker over stranded data or
delete retained stubs by date.

### Historical identity migration

Use `migrations --all` and `profile-status` for the explicitly selected target.
Signals include authorized local preferences with old `workprofile`/compliance
fields, old voice/hook declarations, retained `.lintel/state/` or pre-v5 knowledge,
and availability of the chosen company pack. Record concrete sources, not private
contents. No personal audit/profile search or neutral fallback from absent signals.
Old preference fields cannot override repository-required policy.

An actual identity change follows [pack lifecycle: switch](../../pack-switch/references/lifecycle.md#switch)
with a selected pack and nonempty migration reason. That owner retains validation,
generation-bound references, incomplete-switch recovery and explicit rebind. Missing/
invalid required policy stays blocked; identity is not plugin installation or hook
activation. Preserve old logs, preferences, backups and stubs. Layout migration is
a separate owned operation, never a side effect of identity change.

Report each row's evidence, action and limitation. Listing needs no audit/schema
mutation, private-home scan, network request or automatic migration.

If the operator separately requests recording this observation, retain the
existing `migration/surfaced` event through
`audit_log migration surfaced "active_count=$active_count"` from the trusted
`bin/_audit.sh`. Use an actual inspected count and an explicitly authorized
writer destination; missing counts remain unverified. Confirm the record
persisted before claiming it was written. This optional recording action is
not part of read-only listing and does not establish migration completion.

## Contributor-only structure

`uniformity` owns its existing source floor/dashboard procedure. It is for contributors
and CI, not a consumer installation-health test. Missing trusted source tests/matrix
are a visible unavailable result; never run a same-named target test as fallback.
Doctor's local inspection cannot turn source adoption percentages into host maturity.
