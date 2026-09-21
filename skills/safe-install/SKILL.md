---
name: safe-install
layer: foundation
description: Protect explicitly owned installation files with verified snapshots and conflict-preserving restore; announce recovery paths and refuse unowned rollback.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

# Safe install

Retain backup-before-change, visible restore points, update-source choice, listing,
retention and uninstall/recovery entry points. Execute file recovery through the tested
`bin/li-snapshot.py`, never by removing/replacing an installation tree or interpreting
directory-listing text as deletion targets.

This is a local file safeguard, not a universal transactional installer. Production
services, external hooks, credentials, databases and host settings need their own approved
plans. A file snapshot cannot undo their side effects.

Windows file operations use the trusted shared `lib/native_paths.py` representation
helper after P03's ownership, containment and link checks. Reads, metadata, parents,
temporary files, both publication operands, locks and owned cleanup use the same-location
native spelling; this is not a shorter store or a host-policy change. The logical roots,
filenames, manifest/result/restore formats and explicit caller-selected spellings remain
unchanged. A missing or linked source helper is an error before mutation, never a reason
to load code from the target or `PYTHONPATH`. Other installers and their direct I/O need
their own verified integration; this helper does not establish blanket default-install support.

## Preflight and ownership

1. Resolve the trusted Lintel **source** bundle and the separately authorized **target**
   installation. No operation implicitly uses the user's home or enables private sync.
2. Read the actual installer's managed-file inventory and current diff. Identify each
   owned relative file and any planned new file. Consumer customizations are not owned.
   Stop if ownership or the mutation set is unknown; do not substitute a whole-tree copy.
3. Choose an explicit, existing backup store separate from the target. Keep it private
   to the authorized operator. Verify disk availability and a quiescent/isolated target.
   Symlinks, reparse points, traversal, aliases and Git metadata are refused.
4. Obtain any required mutation authorization before installation, restore, uninstall
   or pruning. Previously authorized scope need not be asked again.

## Snapshot and result binding

Use Python 3.9+ (`python` where that is the Python 3 command) for these snapshot
operations. This is not a prerequisite for native bare installation. All paths below
are quoted argument values; never paste untrusted strings into shell source.

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-snapshot.py" \
  --root "$install_root" --store "$backup_store" create \
  --path 'config/settings.json' --path 'bin/tool' --absent 'bin/new-tool'
```

Replace the sample paths with the approved ownership list. The helper records exact
normalized paths, root identity, sizes, modes and SHA-256. It copies and verifies bytes,
rechecks the source, then atomically activates a uniquely identified snapshot directory.
An incomplete `.pending-*` copy is not a valid snapshot and is not automatically removed.
Announce the returned exact ID/path and verified file/byte count before proceeding.
Windows sharing/access errors during the unique directory's activation get at most four
reported retries; the result includes the actual retry count. Persistent errors remain
failures with the pending copy retained. Source-file restore conflicts are never retried
as permission to overwrite a changed file.

The authorized operation must record its **own post-images** as it changes the files.
Use `file_state` only on outputs just produced by that operation in the quiescent target.
Do not take a later arbitrary scan of user files and call those changes yours.
Bind the complete path-to-state JSON with:

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-snapshot.py" \
  --root "$install_root" --store "$backup_store" bind "$snapshot_id" \
  --expected "$owned_result_json"
```

Each state is `{"sha256":"<64 hex>","size":<bytes>,"mode":<integer>}` or `null` for an
attributable deletion. The shared `file_state` function produces this shape; do not
invent hashes. Binding verifies the current bytes and exact ownership set, pins the
manifest identity and cannot be overwritten to absorb later changes.

## Operation dispatch

| Entry point | Verified behavior and boundary |
|---|---|
| `--backup-only` | Run `create`, verify the result, announce exact ID/path; no installation mutation |
| `--list-backups` | Run `list`; show protected/eligible IDs and unsupported retained content |
| `--restore <id>` | Run `verify`, review owner/result identity, then explicitly authorized `restore <id>` |
| `--update` | Snapshot owned files, run the actual trusted installer at the explicitly selected local source/ref, record its result and verify; no implicit pull/network or shell command string |
| `--uninstall` | Use a verified installer's owned removal plan or the matching pre-install snapshot/result receipt; never delete the whole target root |

`restore` preflights **all** owned paths and snapshot blobs before changing any source
file. Unchanged originals are left alone. Only bytes matching the bound operation result
may be replaced or removed. Unrelated files, later user edits and foreign snapshots are
preserved. If a conflict exists, report it; there is no force/clobber option.

Restored files are individually atomic and verified. A durable `restore.json` remains
`in-progress` until the entire owned set verifies; a multi-file restore is **not** an
all-or-nothing filesystem transaction. Its version-2 per-file journal records `pending`,
`applying` and `restored` progress, content digests and filesystem observations. Intent
is saved before each mutation and verified completion afterward. A restored file's write
permission is consumed: resuming cannot reuse the old operation receipt to overwrite a
later edit, even when the user saves bytes identical to that old operation's output.

Rerun the same ID after an interruption: every recorded file is preflighted before any
remaining mutation. An unfinished file must retain its recorded identity/state. If the
replacement succeeded before its completion record was saved, an already verified original
can be recognized without rewriting it; ambiguous changed states fail closed. An earlier
aggregate-only version-1 journal cannot establish this ownership and is refused for
automatic resume; preserve it and the verified snapshot for explicit manual recovery.
Snapshots and result receipts retain their existing formats.

A process crash may leave `.operation-lock`;
verify that no operation is running before an operator removes that exact empty lock.
Never automatically steal a lock or roll back the rollback.

An installer without an exact ownership/result contract cannot promise automatic
rollback or uninstall. Stop that mutation and report the missing integration explicitly;
the installer lifecycle owns completing it. Keep the snapshot and original error.
In particular, unmanaged historical installations do not become safely uninstallable
merely because this skill was invoked.

## Retention and historical backups

`list` computes the **union** of the newest five verified snapshots and every snapshot
from the last thirty days. An in-progress/locked or unsupported-journal restore is also protected. Only IDs
outside that union are eligible. It never deletes while listing.

After specific deletion authorization, pass exact eligible IDs to `prune`. The helper
revalidates ownership, hashes and the known file inventory before targeted deletion.
Unexpected files/directories block pruning; there is no wildcard or recursive root
removal. Failed/unsupported backups stay visible and untouched.

Old timestamped `cp -r` backups lack the ownership/digest contract. They remain available
for explicit read-only inspection and comparison, but automatic restore/prune refuses
them. An operator can authorize a separately reviewed file-level recovery after comparing
the historical bytes and current edits. Never auto-select "latest", fall back to an older
snapshot after corruption, or relabel an old backup as verified.

## Report

Record the selected operation, trusted source, target/owned paths, exact snapshot ID,
copy/restore evidence, conflicts, interrupted state and unresolved host side effects.
Report success only when the actual selected operation and its post-check succeeded.
Backup creation alone does not prove update or uninstall completion.
