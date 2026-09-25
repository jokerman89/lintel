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

## Run the owned diagnostic

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-doctor" \
  --source "$LINTEL_SOURCE_ROOT" --target "$LINTEL_REPO_ROOT" --json
```

Omit `--json` for readable sections; `--verbose` and `--quick` remain accepted entry
points. No argument executes native plugin-list/update commands or fetches remote data.
Exit 0 means the reported local checks passed, 1 means local issues need attention, and
2 means the invocation or required diagnostic could not run. Preserve the actual code.

The helper reports source product metadata, exact source/target/data roots, executable
availability, effective profile/reference or error, foundation/layout state and actual
repository-adapter check results. It compares known installed hook **bytes**, not
directory counts. Consumer-added files remain visible and untouched.

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
boundaries. `/li:health` is the same diagnostic entry point with optional views.
