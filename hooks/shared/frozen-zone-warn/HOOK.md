---
name: frozen-zone-warn
tier: warn-only
event: PreToolUse (Edit | Write)
fires_on: edit target matching selected session freeze state or a project Frozen zones bullet
override: none; the hook only warns
audit: .claude/runtime/audit/hooks.jsonl (resolved by bin/_audit.sh)
---

# Frozen zone warning

Optional and warn-only. A match reports the path/source and records a `frozen_zone_warn`
observation through the existing advisory audit writer. The hook always exits zero;
it neither prevents an edit nor installs a host write lock.

## Sources

The selected working repository is `LINTEL_REPO_ROOT`, with the existing Git-root fallback.
Use a real `LINTEL_SESSION_ID`, host `CLAUDE_SESSION_ID` or retained `LINTEL_CYCLE_ID`;
no guessed `default` session is read.

1. `$(lintel_state_dir)/code-freeze/<session-id>.yaml`: the state written by
   `/li:code-freeze`, parsed by its shared `scripts/freeze.py` reader. Exact file or
   directory-boundary matching handles both repository-relative and absolute targets.
2. Only if that file is absent, the same explicit session's legacy
   `$LINTEL_HOME/freeze/<session-id>.yaml`, read-only. An empty repository list takes
   precedence. Nothing migrates, edits or clears legacy state implicitly.
3. The selected repository's `CLAUDE.md` Frozen zones section, using the retained
   heuristic bullet reader. This is a project-rule warning, not runtime scope.

A missing/failed Python reader or malformed session file is reported as unknown scope,
not an empty unfrozen state. It still does not block. Without a session ID, only the
project-rule source is inspected.

## Authority and evidence

The message recommends `/li:code-freeze --list` and an explicitly authorized `--lift`
for runtime scope changes. A project rule requires its own exception; `--lift` cannot
override it. The audit retains `source=session-freeze|project-claude-md`, frozen path
and edit target. A warning/audit proves only that this invocation matched and warned.

No registration, model control, permission override or automatic expiry is added.
Compatible host activation remains a separate operator-controlled action.
