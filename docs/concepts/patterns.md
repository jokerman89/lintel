# Reusable patterns

Reusable patterns let a repository, a team pack or a person state recurring expectations once
and apply them to named work: a deployment baseline, dashboard behavior, a document's required
sections, a visual language. A pattern is data. It never executes, fetches or installs anything,
and it grants no authority. The decision record is [ADR-0038](../../.claude/decisions/0038-reusable-patterns.md).

## What a pattern holds

- **Clauses.** Each clause has a level: `must`, `default` or `recommendation`. It can carry an
  optional structured setting (for example `visual.layout.max-width`).
- **A selector.** Exact fact keys and values, such as `artifact: [dashboard]` and
  `audience: [internal]`, that decide where the pattern applies.
- **Sources.** The operator statements, standards or observations the clauses came from, each
  with its confidence and reuse limits.
- **Optional local assets.** For example, a guide or tokens file, each pinned by sha256.
- **Optional exact includes.** A pattern that mostly includes others is a blueprint.

Catalogs publish immutable versions and record deprecation, retirement and revocation events.
Bindings say which patterns a context requires or defaults to.

## Scopes and precedence

| Scope | Source | Activation |
| --- | --- | --- |
| Repository | `.claude/patterns/` | Repository and catalog bindings apply at repository scope |
| Active pack | `patterns.source` in the effective pack manifest | Pack bindings apply at pack scope |
| Personal | `$LINTEL_HOME/patterns/` | Never automatic; only an explicit reference or a repository binding |

For defaults, precedence runs from strongest to weakest:

1. an explicit authorized task choice;
2. the repository;
3. the active pack;
4. an explicitly selected personal pattern;
5. the existing corpus or model fallback.

A `must` clause is mandatory only when it is reached from a required binding or reference. With no
selected pattern, behavior is unchanged, including Design DNA's brief > profile > corpus order.

## How work uses patterns

The [pattern workflow](../../skills/pattern/SKILL.md) covers the full lifecycle: capturing drafts
from authorized sources, approving new versions, updating, deprecating, retiring or revoking them,
changing bindings, attesting sources, and exporting and importing local bundles.

Phase, document, engineering and frontend workflows follow one shared
[consumer contract](../../skills/pattern/references/consumer-contract.md):

- **Resolve before deciding.** Resolution reads metadata first. Unbound suggestions are advisory
  only, and a missing fact is `needs-context`, never a guess.
- **Lock at PLAN.** The lock is a portable record of the exact selection beside the initiative. It
  maps clauses to existing task IDs and projects each package's clauses.
- **Verify when continuing.** `verify-lock` fails closed on:
  - changed bytes;
  - retired or revoked pins;
  - a changed context;
  - a changed mandatory or default baseline, which forces a re-plan.
- **Review clause evidence.** `review` exits 7 when mandatory coverage is missing or failed. It
  supplements the ADR-0028 review contract and never clears missing or stale independent review.
- **Read assets only through `read_asset`.** Bind the read to a verified lock, or to a fresh
  in-process report together with its context.

## Limits and notices

- **Not enforcement.** A repository can forge a binding. Patterns do not prove source
  authenticity, approver authority, prose agreement or the truth of cited evidence. They do not
  replace enterprise controls, branch protection or required review. Digests detect edits; they
  authenticate no one.
- **Optional runtime.** Pattern operations need Python 3.10+. Bare installation does not require
  or install it. Without the runtime, the launcher reports "pattern check unavailable" (exit 5).
  That is never "no patterns":
  - Ordinary unrelated work may continue with the limitation stated.
  - Locks, explicit references, known pattern work and required policy controls block their
    dependent action.
  - A degraded run grants no pattern evidence or release clearance.
- **Linked roots are refused.** A repository or `LINTEL_HOME` that is itself a link or junction is
  `invalid_roots` (exit 2). Pass the real path. Consumers report this; they never treat it as
  "no patterns".
- **Upgrade notice.** Adding the neutral `patterns.source: null` field changes the neutral pack
  manifest. Every bound profile context, including ones used only by unrelated callers, reports
  drift until you rebind it explicitly with a reason. Then re-plan dependent work. There is no
  data migration and no automatic rebind.
- **Stricter `check`.** `check` verifies each registered version's declared files: its assets and
  pinned `root: pattern` sources. An entry approved without those files, or a pack that declares
  a source it does not ship, reports `unavailable`.
  - In a repository, fix it with `update --files-from <dir>`, then `approve`.
  - In a pack, ship the file.
  - `list` and ordinary resolution stay metadata-first.
  - `check` also rejects a previously published or pack entry whose declared files collide on a
    portable filesystem, for example `guide.md` and `Guide.md`, as `destination_conflict`.
    Metadata resolution is unchanged. Publish a corrected version or layout; re-running `check`
    or reindexing does not accept the old entry.
- **Windows path length.** The runtime opens pattern files with ordinary paths. Without Windows
  long-path support, a pattern file whose full path exceeds about 260 characters is reported
  missing: fail-closed, never success.
  - The kit's deepest path is the example asset directory. So on Windows PowerShell 5.1 with
    `LongPathsEnabled=0`, the bare installer needs a correspondingly short Lintel home.
  - A home of about 108 characters was observed to work, and about 134 to fail recoverably with
    `-Recover`. The exact budget depends on the host.
  - Keep pattern sources and the Lintel home at ordinary depths, or enable long paths. Full
    long-path support is not claimed.
- **Byte-exact sources through Git.** Asset digests cover raw bytes. Keep `* -text` in a
  source-local `.gitattributes` beside the pattern catalog, so line-ending conversion cannot
  rewrite assets. `-text` does not disable filters, LFS, `working-tree-encoding` or `ident`, and it
  never overrides an authoritative repository policy. See the
  [pattern template](../../scaffolding/01-foundation/templates/pattern/README.md).

## Getting started

Copy the [pattern template](../../scaffolding/01-foundation/templates/pattern/README.md), capture a
draft, review it with the owner of the expectation, and approve a new version. Start a session
with `li-pattern list`; with no configured sources it reports no entries and changes nothing.
