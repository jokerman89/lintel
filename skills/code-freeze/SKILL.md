---
name: code-freeze
layer: foundation
description: Use to add, list or lift advisory session freeze paths; preserves project policy and never grants or removes host write permission.
color: red
tools: Read, Edit, Bash
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Code freeze

Record advisory do-not-modify scope for the explicitly selected session or cycle.
The state is `.claude/runtime/state/code-freeze/<session-id>.yaml` on the v5 layout;
`lintel_state_dir` retains the repository's legacy path resolution. This metadata is
not a filesystem lock, host permission or project-policy exception.

## Inputs

- One or more repository-relative paths: add or update exact scope. Bounded globs
  expand to existing files through the shared safe selector.
- `--reason <text>`: a recorded reason; omitted reasons preserve existing entries.
- `--until <intent>`: requested expiry such as `session`, `eod`, `1h` or a timestamp.
  It is a reminder, not a timer. Nothing automatically removes an expired entry.
- `--list`: read recorded state without writing.
- `--lift <path...>`: remove exact recorded paths only; no glob expansion.
- `--lift --all`: remove all entries from this selected session's repository file.

Choose one operation. `--all` without `--lift`, conflicting modes, missing operands,
unsafe paths and malformed state fail visibly without replacing the old file. A
nonexistent literal future path may be frozen and is reported as prospective scope.
An unmatched glob is not permission to freeze its parent or an entire repository.

## Run the selected operation

Carry an actual host session ID or retained cycle ID in the existing environment.
Never invent a PID/default identity or scan other sessions. Pass operands as an array:

```bash
source_root="${LINTEL_SOURCE_ROOT:?select the trusted source}"
source "$source_root/lib/paths.sh"
repo="$(lintel_repo_root)" || exit 1
state_dir="$(lintel_state_dir)" || exit 1
session_id="${LINTEL_SESSION_ID:-${CLAUDE_SESSION_ID:-${LINTEL_CYCLE_ID:-}}}"
[ -n "$session_id" ] || { echo 'Select the actual session or retained cycle ID.' >&2; exit 2; }
python_cmd="${LINTEL_PYTHON:-python3}"
"$python_cmd" -B "$source_root/skills/code-freeze/scripts/freeze.py" \
  --repo "$repo" --state-dir "$state_dir" --session "$session_id" \
  --legacy-file "$LINTEL_HOME/freeze/$session_id.yaml" "$@"
```

The shared producer/reader validates paths with `context_safety.py`, conditionally
replaces only the selected state file and verifies its read-back. It does not change
the context/recovery helper, source files, profile, Git configuration or host policy.
A changed/unreadable/corrupt file is not reset to apparently unrestricted state.

The existing YAML shape stays readable:

```yaml
advisory: true
frozen:
  - path: src/landing/
    reason: keep this area unchanged during the current task
    added_at: 2026-09-25T08:00:00Z
    expires: session
```

Lift preserves unmatched entries and their metadata; absent paths are explicit no-ops.
After an actual change, the existing advisory audit writer records `code-freeze`
`freeze` or `unfreeze` once per changed path. Audit failure is reported separately from
state persistence. List/no-op operations neither rewrite state nor manufacture events.

## Hook consumption and compatibility

The optional `frozen-zone-warn` hook reads this same repository state through the same
reader. It compares a file or directory boundary, not a misleading string prefix.
Only a configured compatible hook invocation produces a warning; this skill does not
register it, and the hook remains **warn-only**, never a write lock.
There is no universal automatic freeze consumer: clients that do not run that
explicitly configured compatible hook receive no automatic warning. A recorded
scope or discovered skill file does not prove host activation or prevent a write.

When repository state is absent, an explicitly identified legacy
`$LINTEL_HOME/freeze/<session-id>.yaml` remains a read-only list/warning source. Do not
copy or mutate it implicitly. A mutation reports that this legacy source needs explicit
reconciliation; an existing repository file, including an empty list, takes precedence
and does not resurrect old entries after lift.

Static project frozen-zone rules remain independent. Lifting a runtime reminder
does not override those rules, enterprise policy or permissions. Before an exception,
obtain its actual scoped authority. There is no universal `--ignore-freeze` flag.

## Report and recovery

Show the exact state path/source, current entries, changed paths, prospective paths and
unmatched lift requests. State persistence and hook observation are separate evidence:
report **advisory scope recorded**, not **writes blocked**. Missing Python or a failed
reader leaves the operation unverified; preserve the file and do not switch to a
weaker parser. An unknown hook read warns about unknown scope and still does not block.

## Failure modes

- Missing Python or required reader: report the operation unverified; retain the
  original state and do not substitute a weaker parser.
- Malformed, linked or foreign state: refuse mutation, preserve the original bytes
  and report unknown scope. An optional hook may warn, but never invent clearance.
- Unmatched or excessive glob: fail the bounded selection without widening to a
  parent directory. Lift accepts only exact recorded paths or the explicit all mode.
- Audit failure after an owned write: state persistence and missing audit evidence
  are separate facts; report both, with no successful audit claim or blind rollback.
- Host without the configured warning hook: disclose that no automatic warning was
  observed. Project policy and permissions still apply independently of this reminder.

```text
/li:code-freeze src/landing --reason "work is limited to src/portal"
/li:code-freeze --list
/li:code-freeze --lift src/landing --reason "scope change authorized"
/li:code-freeze --lift --all --reason "session scope completed"
```

Use `/li:pause` and `/li:resume --from <checkpoint>` for continuity notes. Neither
operation automatically copies or clears freeze metadata.
