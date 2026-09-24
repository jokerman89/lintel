---
name: health
layer: foundation
description: Inspect Lintel lifecycle health through doctor, with explicit installed-file, provenance and host-activation boundaries.
color: green
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Health

Retain install/update triage, structured output, layer/hook views and source provenance
inspection through [doctor](../doctor/SKILL.md). Do not maintain a second health engine.

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-doctor" \
  --source "$LINTEL_SOURCE_ROOT" --target "$LINTEL_REPO_ROOT" --json
```

Show only the requested view without discarding an actual diagnostic failure:

| Historical option | Current mapping |
|---|---|
| `--fast` | Doctor's `--quick`; local checks, no network |
| `--json` | Return actual doctor JSON and exit status |
| `--layers-only` | Source/foundation/adapter fields from that result |
| `--hooks-only` | Known hook-byte comparison plus unverified activation boundary |
| `--upstream-only` | Read installed-source `install/upstream-sources.yaml` and public provenance when present; declarations are not downloaded clones or verified current licenses |

If an installed portable bundle omits the upstream declaration, report that view as
unavailable, not "all upstreams healthy". `install/verify.sh`, when present in the approved
source, remains the separate source/frontmatter/structure check; it is not a proof of
installed ownership, live discovery, hook registration or policy enforcement.

For configured brand/voice assets, retain calibration and age inspection using actual
pack field provenance. Missing corpus/calibration is unverified or not configured, not a
fabricated pending count. Read-only diagnostics do not activate a profile, create a
legacy install manifest, repair files or call a remote API.

Report the requested view, real command/result, actionable local failures and missing
host evidence. Current schema, source product and pack release versions are distinct;
do not use historic internal release labels as today's support floor.
