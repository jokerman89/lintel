---
name: doctor
layer: foundation
description: Use to diagnose source, target, profile and installed-file integrity while keeping actual host activation explicitly unverified.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Doctor

Use for onboarding, failed discovery, suspected drift, update diagnosis and local health
checks. The skill is a front door to the actual helper, not a second set of speculative
client probes. [Lifecycle paths](../../docs/lifecycle.md) define the roots.

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

Instruction parity remains a useful separate check via
[instruction-parity-check](../instruction-parity-check/SKILL.md) when its relevant
source/target files exist. Brand/corpus calibration and provenance/license freshness
remain read-only follow-ups against actual configured files and dated metadata, not
fixed counts, assumed upstream clones or invented calibration.

Report checks actually performed, diagnostics, preserved files and unverified host
boundaries. Source product, pack release and schema versions remain distinct.
