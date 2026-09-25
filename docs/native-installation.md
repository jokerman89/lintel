# Native installation and recovery

Bare installation stays **Python-free**. `install/install.sh` uses Bash and existing
native utilities on POSIX; on Windows it invokes the same native performer as
`install/install.ps1`. That performer uses PowerShell 5.1+ and .NET. Git is required.
The POSIX path needs an existing SHA-256 provider: `sha256sum`, `shasum` or OpenSSL.
Missing tools fail before mutation; nothing installs a dependency automatically.
The Bash performer starts several processes per file. On Windows that makes a
full-source install far slower than the PowerShell performer, which `install.sh` selects
there. The repository's Windows tests therefore exercise the Bash performer on a small,
labelled fixture and the full source through PowerShell.

Installation copies files, not live host capabilities. Later profile, repository-adapter,
scaffold and snapshot operations have their separately documented Python prerequisites.
No plugin, hook, credential, private-sync destination or model setting is activated.

## Choose source, destination and host

Run from an approved local source:

```bash
bash install/install.sh --home "$install_home" --store "$recovery_store"
```

The native PowerShell spelling is:

```powershell
.\install\install.ps1 -Home $InstallHome -Store $RecoveryStore
```

`--source`/`-Source` explicitly selects a different approved source tree. Otherwise source
is executable-relative, never guessed from the target's basename or an active project.
`LINTEL_HOME` is the destination. `--store` or `LINTEL_RECOVERY_STORE` wins over the
compatible, reported sibling default `<LINTEL_HOME>-recovery`.

Source, target and store cannot overlap. Links/reparse points, traversal, malformed
inventories and foreign/unowned stores are refused. Existing home/profile/config,
personal roles/packs, inert hooks, local extensions and brand customizations are not
permission to replace an entire tree.

On Windows, the Bash entry can use an explicitly selected executable path in
`LINTEL_POWERSHELL`. It is passed as one executable, never evaluated as a shell command.
An unavailable runtime or denied script execution returns the actual failure. There is
no automatic retry through another host, execution-policy override or policy change.
Choose a permitted runtime explicitly with the operator; a syntactically compatible
script is not evidence that PowerShell 5.1 ran on a particular machine.

## Install, update and check

The installer validates the source before publishing files. It compares existing managed
bytes with the previous inventory and refuses a locally edited managed file or unowned
collision before writes. Exact matching historical source files may be adopted; modified
unmanifested files are preserved for explicit reconciliation.

The native managed inventory is `.lintel-install.tsv`. Ordinary config/profile/packs/
roles/brand content is not in its managed namespace. The managed payload is the fixed
source components plus fixed root metadata, including the `config/aliases.yaml` registry
that resolves opt-in historical aliases; the source must contain every fixed path.
Missing seed files may be created,
but existing bytes are preserved. Updating removes only obsolete, unchanged files in the
previous managed inventory; files merely located in a managed directory are not owned.
The shared `install/directories.txt` contract retains the historical runtime and
brand-asset slots. Both performers preflight these directories, create only missing
slots and preserve existing assets; recovery may leave the empty directories behind.

```bash
bash install/install.sh --home "$install_home" --check
```

Check verifies known installed bytes. It does not claim host discovery or hook execution.
An incomplete transaction blocks another install; a new invocation must not silently
adopt a partially published tree.
Closed receipt labels must agree with the verified plan, blobs and per-file progress;
changing a label alone cannot clear an incomplete or corrupt operation.

## Receipt contract, version 1

Both native performers use the following UTF-8, LF, tab-separated contract. Tabs,
newlines/control characters and unsafe path spellings are not allowed in path fields.
Spaces and ordinary Unicode remain literal data. Receipts are never sourced or executed.

| File | Meaning |
|---|---|
| `.lintel-install.tsv` | `LINTEL-INSTALL<TAB>1`, then SHA-256, byte count and portable relative path per managed file |
| `<store>/.lintel-recovery-owner` | `LINTEL-RECOVERY<TAB>1`, then the exact normalized target root |
| `<store>/txn-<id>/meta.tsv` | `LINTEL-TRANSACTION<TAB>1`; root, source, store, id, platform and inventory_before records |
| `plan.tsv` | index, before hash/size/mode, planned-after hash/size/mode, relative path; eight fields per row |
| `before/<index>`, `after/<index>` | Verified original and staged replacement bytes where present |
| `receipt.sha256` | SHA-256 of the exact meta bytes, a space, SHA-256 of the exact plan bytes |
| `phase/<index>` | pending, applying, applied, restoring or restored |
| `state` | prepared, applying, complete, recovering or recovered |

The index is a zero-based, six-digit decimal string. `-` in all three state fields means
absent/deleted; it is not an empty file. Hashes are 64 lowercase hexadecimal characters.
`inventory_before` is its exact pre-operation hash or `-`. Inventory publication is last.
An inventory has exactly one header line; every following line, including a final line
without a newline, must be one well-formed record. A second header, malformed row or
unsupported path refuses before writes, and check does not report success. Each performer
parses one observed copy and binds its inventory write to that copy's hash.
The platform records the supported mode projection: `bash-mode` uses octal permission
bits; `powershell-readonly` records the Windows read-only attribute as `0`/`1`. A performer
refuses an unsupported projection instead of pretending it preserved ACLs or POSIX modes.
The two Windows entry points use the same PowerShell projection and recovery performer.

The store lock prevents concurrent cooperating operations. A crash can retain it; verify
that no operation is running before explicitly removing that exact lock. There is no
automatic lock stealing. Unknown files, old backups and incomplete/corrupt receipts are
preserved, not silently pruned or relabeled.

## Interrupted publication and explicit recovery

Intent is recorded before each replacement and completion after verified readback.
Replacements are file-atomic where the native filesystem supports them; a multi-file
operation is **not** all-or-nothing. Failure retains the receipt and returns nonzero,
without automatic rollback or completion prose.

```bash
bash install/install.sh --home "$install_home" --store "$recovery_store" \
  --recover "$transaction_id"
```

Use `-Recover $TransactionId` in PowerShell. Recovery checks the entire plan, blobs,
target/store identity and current files first. Only unchanged originals or the exact
attributable planned postimages are eligible. Later edits, links, foreign/corrupt
receipts and unknown progress refuse the whole recovery before file changes.

A restored file's write permission is consumed. Repeating recovery cannot overwrite a
new user edit even if its bytes equal the old installation postimage. Interrupted recovery
can resume from verified per-file progress. Empty directories may remain; snapshots and
receipts remain available for inspection.

On Windows, replacement can encounter a transient sharing/locking conflict. At most four
reported retries of the **same** replacement are allowed for sharing/locking errors,
rechecking original expected bytes each time. This does not clear access policy, change
file permissions or select another runtime. Other/persistent errors remain incomplete.

## Boundaries

There is no broad uninstall command. A verified pre-install receipt can reverse its
unchanged owned files; it does not remove unrelated files, deactivate a host, unregister
hooks or undo external services. Historical copy-based backups lack this ownership
contract and need explicit, reviewed file-level recovery.

Mode/readonly projection is recorded; ACLs, xattrs, power-loss durability, active
concurrent user edits and live-service rollback are not universal guarantees. Use a
quiescent, authorized target and retain independent host/platform acceptance. Local
Windows fixtures do not establish execution on POSIX, stock Bash 3.2 or a denied
PowerShell 5.1 host.
