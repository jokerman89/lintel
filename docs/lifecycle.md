# Lifecycle operations

Lifecycle skills dispatch to source-owned helpers. A successful command describes an
observed local mutation, not host discovery, policy enforcement or a model run.

[Bare installation](native-installation.md) remains Python-free. The Python prerequisite
below belongs to later runtime/profile/repository operations, not to copying the harness.

## Separate roots

| Root | Meaning |
|---|---|
| `LINTEL_SOURCE_ROOT` / `--source` | Trusted code, templates and public metadata. Resolve helper paths here before selecting a target. |
| `LINTEL_REPO_ROOT` / `--repo` or `--target` | The exact working consumer. Never choose another repository by basename or change to the source to operate on it. |
| `LINTEL_HOME` / `--home` | Explicitly configured installed/operator data. Repository adapters default to target-local runtime storage, not a global installation. |
| `LINTEL_PACKS_DIR` / `--packs` | Configured pack store; precedes target `packs/`, then source `packs/`. |
| `LINTEL_ACTIVE_PACK_FILE` / `--pointer` | The actual active preference pointer; it need not live under the default home. |

Use Python 3.9+ where the installed helper/dependency versions support it (`python` if
that is the Python 3 command), and Bash for shell entry points. An unavailable interpreter
is an error before mutation, not permission to install dependencies or use a second
recipe. Local verification must name its actual interpreter and platform.

For profile/role commands, call the selected source explicitly:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" profile-status
```

Root flags precede the subcommand. The Bash entry passes configured roots as arguments,
including the MSYS/native Windows boundary. Native Python callers may invoke
`bin/li-lifecycle.py` directly with native path arguments; untranslated MSYS environment
paths are refused rather than redirected to another directory. Explicit flags override
configured roots; unspecified profile roots use the resolver's environment contract. No helper fetches a
source, imports executable code from the consumer, or publishes to a remote destination.

## Foundations, migration and two profile contexts

`li-scaffold check|init --target <consumer>` is the common initializer for ordinary,
internal-tool and MVP workflows. `--client <surface>` and the legacy `--copilot` alias
delegate to the existing repository adapter and its protected inventory. Legacy rendering
preferences cannot be combined with those adapter modes.
The old `--compliance` label is refused with a pack-policy migration instruction; it
does not configure controls and must not be reported as such.

The caller's working repository and explicit new target are distinct. A carried pin is
verified against the original caller source/home/repository. A required caller policy
remains an operation constraint: the target must resolve compatible, identical policy
source/content, not merely the same name. A target requirement is independently loaded;
conflict, missing history or caller drift fails before writes. The child remains unbound:
no parent reference is transplanted and no child generation is silently created.
The returned operation reference and private `operation-profile.json` beside a new
transaction retain that evidence; neither is host-policy enforcement or review clearance.

Existing foundation files remain user-owned. Legacy knowledge and hidden/nested runtime
files move only after a complete collision/path preflight. Redirect stubs remain available;
the layout marker publishes last. Git staging/index is not changed by the helper.

The lifecycle producer observes checked paths through the accepted native I/O boundary.
Missing-only outputs retain an explicit absent-state expectation; merges, redirects and
deletions retain the state captured with their original bytes. Publication must not
replace those expectations with a later snapshot of whatever is currently present.
A recoverable before-image is evidence for recovery, not permission to overwrite
consumer-owned content.

Unchanged planning inputs, such as an existing v5 layout marker, are separate admission
guards, not no-op writes. The consumer checks them immediately before handing the
original write-set expectations to the transaction. A guard change before that check
refuses without publication; a write-set change is also checked by the transaction.
An unchanged guard can still change after admission. It is not rewritten or locked by
the transaction, and no cross-file atomicity or post-admission guard protection is claimed.

`li-migrate-claude-home --dry-run --repo <target>` previews that same migration.
`--repair-pointer` changes only the local Claude memory pointer on an already migrated
v5 target, preserving other JSON fields/prose. `--no-memory-pointer` leaves this optional
client setting alone. A pointer does not prove actual host memory activation.
`li-pack-scaffold` validates an extension skeleton before publishing its files and refuses
existing README/config/manifest collisions; a skeleton is not an implemented extension.

## Repository Git verification

Repository adapter `init` and `check` verify the effective runtime ignore rule when the
target has a `.git` directory or linked-worktree file. Git exit 0 confirms the probe is
ignored; exit 1 means it is not ignored. `init` may add a missing literal rule after
either supported result, while `check` reports the missing rule. An existing rule that
is effectively negated is refused rather than overwritten. Plain folders without
`.git` metadata do not require Git.

Missing Git, a launch error or any other exit is a verification failure, not evidence
of conflicting ignore rules. The diagnostic retains the logical target and actual
exit/error context. Refusal precedes managed-file, inventory, receipt and recovery-store
writes, including fresh initialization before adding the rule. Explicit `inspect` and
`recover` operations keep their existing independent ownership checks.

Git for Windows 2.55.0.windows.3 failed this read-only operation with exit 128 in the
observed 256-character target / 261-character `.git` fixture, even though Python could
access the same files. These are observed fixture dimensions, not a universal cutoff.
The corresponding long linked-worktree positive case remains unverified. The adapter
does not change Git options, redirect the target or retry another path spelling.
Preserve the refused state and resolve the external Git operation limit before retrying;
Python native-path support alone does not establish Git compatibility.

## Python-runtime file transactions

The adapter retains its existing manifest, selected clients, managed blocks, line-ending
and protected-file policy. `lib/managed_transaction.py` receives only its exact
preflighted changes, expected original states, modes, label and final-publication paths.
It does not infer ownership or implement a second installer inventory.

The primitive stores a deterministic plan and per-file progress before mutation, reuses
P03's verified snapshot/result/restore APIs, and publishes completion only after expected
bytes verify. Failure leaves an incomplete transaction; another init cannot adopt it.
Recovery is explicit, preflights the entire owned set and refuses later edits or replay of
already consumed restoration permission.

While holding the operation lock, the runtime may retry only replacement of its owned
transaction journal on Windows errors 5, 32 or 33. At most four retries are reported on
stderr, delayed by 0.05, 0.1, 0.2 and 0.4 seconds. The journal must still match its saved
before-state (including absence for its first save); a changed journal is refused.
Within the same four-retry bound, a verification read of that owned journal whose own
identity samples disagree ("File changed while reading: journal.json") is repeated and
reported as `owned journal changed during a verification read`. This was observed when an
actor outside Lintel reset the just-replaced journal's timestamps to an earlier version's
values. Every accepted read is still internally stable, and a changed journal state is
still refused.
Other writes are not retried by this rule. Persistent or other errors remain failures,
retain incomplete evidence and require explicit recovery. This bounded handling does
not identify the cause of earlier access-denied failures or guarantee completion.

`--store`/`LINTEL_RECOVERY_STORE` is honored exactly. Runtime defaults use a reported
`.lintel-recovery-<full-root-digest>` sibling to avoid repeating a long target basename in
every snapshot path. The full resolved target remains bound in the store/receipt; same
basenames do not identify the same work. Existing foreign/colliding stores are refused,
not relocated. This name choice is not a guarantee for arbitrarily long parent paths.

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-managed-transaction.py" inspect "$id" \
  --root "$target" --store "$store"
python3 "$LINTEL_SOURCE_ROOT/bin/li-managed-transaction.py" recover "$id" \
  --root "$target" --store "$store"
```

The adapter also exposes `inspect|recover --transaction <id> --target <target> --store
<store>`. Keep a quiescent target and a separate private store. A retained lock is not
automatically stolen. Unknown, corrupt or old formats remain inspectable but cannot
authorize writes. Keep the receipt and its referenced snapshot together; do not prune
only the snapshot underneath a live transaction record. No recursive uninstall, host
rollback, automatic rollback, universal ACL/xattr preservation or multi-file atomicity
is claimed.

## Profiles and packs

`profile-status`, `pack-list`, `pack-validate <name>` and role/persona inventories are
read-only. An absent reference is reported as unbound. `profile-bind` is an explicit
initial bootstrap; existing pins are verified, not recreated or silently advanced.
Required repository/explicit packs never degrade to neutral success.

`pack-create <name> --scope repo|home` stages and validates a manifest before publishing.
`--extends <parent>` keeps inheritance instead of copying neutral overrides; `--from <pack>`
clones the manifest only. Referenced private corpora, extensions and credentials are not
copied or activated. Existing names in any resolution root are refused.

`pack-switch <name> --reason <text>` validates the requested pack, writes the configured
pointer and explicitly rebinds the selected context. It reports the effective result and
the complete versioned reference: schema_version, context_id, generation, digest, name,
version. Pack schema, pack release, product and capability versions remain separate.

The previous generation is retained. Old references intentionally stop matching; carry
the new reference only after this explicit change and replan/review affected work. A
pointer-only failure is `PROFILE_SWITCH_INCOMPLETE`, not activation. Preserve state and use
`profile-rebind --reason <text> [--pack <name>]` for deliberate recovery or accepted drift.
The shared profile API owns history and missing-context recovery. There is no automatic
rollback, deletion of pins or neutral error fallback.

## Roles and audience personas

`role-list` reads frontmatter only. `--include-private` requests private metadata; body
reads and activation of a private role separately need `--allow-private`. Pack-relative
`roles.source` and `persona.source` resolve at the defining manifest, including inherited
fields, not at the current directory. Links and path escapes are refused.

`role-set <id>` validates the role before changing `role_active` in the configured home's
`profile.yaml`; `role-off` clears only that preference. Comments and unrelated fields are
preserved. Duplicate keys or malformed preferences are errors, not a reason to replace
the file. Rotation is one validated set, never deactivate-then-hope.

`role-show <id>` returns only identity, voice, outcome lens and companion skills. `--deep`
loads the full expertise explicitly. `role-write <id> --file <reviewed-draft> --scope
private|public` checks required metadata/sections and publishes without activation or
sync. An update additionally requires the previously reviewed `--expected-sha256`.
Private storage is `LINTEL_PRIVATE_ROLES_DIR`, or `<home>/roles/private/`; public storage is
the configured pack role directory, otherwise `<home>/roles/`. Review the destination
before choosing public scope. Keep private drafts and evidence out of committed artifacts.

`persona-sources` lists configured pack and target persona resources. Audience rotation
is a current-conversation overlay; clearing it does not erase chat history. It never
rewrites durable working state or assumes delegates inherit private context.

## Host controls and historical recovery

`host-profile status --client <surface>` reports the activation boundary. No automatic
host enable/disable adapter ships in this helper: dormant/activate return unsupported
without marker files or configuration mutation. Use actual authorized host controls and
inspect the result in a new session before claiming activation.

The `profile-switch` snapshot/list/restore aliases use the accepted
[owned snapshot workflow](../skills/safe-install/SKILL.md). File recovery needs an exact
root, separate store, verified inventory and attributable postimages. It cannot undo host
permissions, credentials, external services or hook registration. Old backups and
historical migration stubs stay available for explicit inspection/recovery; age alone
never authorizes deletion.

`li-doctor --source <source> --target <consumer> --json` diagnoses local profile,
foundation/layout and adapter files without running host plugin commands. It compares
installed hook bytes where both roots exist, preserves operator extras, and labels cached
versions/historical audit logs as unverified activation evidence. `health` is a view of the
same result; source structure checks are separate from installation and live-host checks.

`li-lifecycle.py migrations [--all]` reads the source migration catalog. Open/overdue/
archived schedules are distinct from actual target observations. Missing catalogs and
malformed metadata are errors; absent detectors are unknown. `v4-migrate` remains an
opt-in historical inspection and explicit pack-switch route, not a neutral fallback.

Layout observations use checked, same-location native I/O for the marker, legacy files
and nested directories. Missing paths are distinguished from inspection failures;
malformed, unreadable or disappearing entries produce an explicit error instead.
This reader does not migrate files, create a transaction or alter retained stubs.
Canonical redirects count as retained stubs only when their mapped destination exists
with the required type and, for files, can be read. A missing destination remains
legacy work (`incomplete` with a current marker, otherwise `needs_migration`); wrong
types, links and inspection failures are errors. The historical ADR README directory
redirect takes precedence over its ordinary file redirect. Near-match prose is not a
redirect, and no destination is parsed from arbitrary user text.
