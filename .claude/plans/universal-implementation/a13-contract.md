# A13 observation and learning contract

## Status and authority

This is the coordinator contract for P08. The P08 card section "A13 contract release"
releases A13.1.a, A13.2, A13.3 and A13.4.a. A13.1.b and A13.4.b stay gated until P10 is
accepted and integrated and the coordinator releases them. The parent items A13.1 and
A13.4, and the plan's A13 acceptance, stay open until the `.b` leaves pass.

- **Authority:** plan A13, the P08 card leaves A13.1–A13.4, and interfaces "P10
  installation and runtime boundaries".
- **Evidence base:** coordinator inventories of the integrated tree (recovery
  `b2909947`) and the P08 and P10 sources, read without execution.
- **Review:** an independent read-only review of the first draft returned 2 P1, 12 P2
  and 10 P3 findings. This revision resolves all of them.

This is the exact artifact the P08 card requires before its common audit/event and
learning/promotion changes. If P08 finds an ambiguity here, it asks the coordinator; it
does not settle the question by choosing silently. Deviations are recorded in the P08
A13 report with their reasons, for review.

## Decisions

### Event unification is reader-side

Three constraints come from the evidence:

- every JSONL record goes through `audit_log` with the envelope `ts, kind, operator,
  cycle_id` followed by string key/value pairs;
- P05's `auditEnvelope` for `reviews.jsonl` sets `additionalProperties:false`, so a new
  common envelope field would make every review line invalid;
- 41 `audit_log` calls in 30 hook files, plus other producers, already carry stable,
  test-asserted field names.

Three alternatives were weighed:

1. Extending the envelope breaks P05 and is rejected.
2. Rewriting producers to one vocabulary churns 41 calls and their tests for no reader
   benefit, and is rejected.
3. The selected approach is one versioned producer catalog plus one structured reader.
   Consumers move to that reader. Producer bytes change only where this contract names
   a defect.

### Lesson parsing has two entry points and one grammar

Reads run in auto-registered bash hooks, including memory-budget-warn on every Edit or
Write and session-digest at session start. A bare install must stay usable without
Python. Conditional atomic writes need Python.

The grammar below therefore has exactly two implementations:

- **awk in `lib/memory.sh`** serves surface, count, digest and budget reads.
- **One Python helper, `bin/li-lessons.py`,** serves allocation, by-ID retrieval, add,
  update, supersede and promotion.

Both must pass one shared fixture directory. Every other lesson parser is removed,
including the grep and awk copies in `sense`, `lessons-promote` and `session-digest`.
Without Python, writes refuse visibly and reads keep working.

### Freeze stays advisory

A13.3 keeps the reviewed advisory boundary and corrects its contradictions. No automatic
freeze consumer or write lock is added.

### No operator lessons sink is activated

The P08 card forbids activating a global destination. The default pack already sets
`lessons.operator_lessons: ~/.lintel/lessons.md`, and `~` would reach the real profile.
P08 therefore activates no global lessons sink:

- global-scope writes refuse with "operator lessons sink not activated";
- the configured sinks in this package are the resolved project store and the explicit
  promotion destination;
- activating an operator sink later is an operator decision, recorded as pending.

## A13.1.a Common event catalog, reader and consumers

### Catalog

Add `lib/event-catalog.json`, stdlib-readable JSON with `schema_version: 1`.

**Producer entries.** For every category, and every `kind` within it, the catalog
records:

- `producers`: the `path:function` or hook of each actual producer, or `instruction-only`
  with the skill path when only instructions produce it;
- `records_when`: the conditions under which the producer writes a record, from
  `always`, `start`, `end`, `finding`, `block`, `override`, `unavailable` and `failure`;
- `fields`: the exact key names after the envelope, all string-typed;
- `aliases`: the reader's normalized names, for example `target_path` from
  `file_edited | file | edit_target | artifact_dir` and `patterns` from
  `patterns | patterns_matched`;
- `rules`: an ordered list of `{when: {field: value | [values]}, class, check}` entries,
  followed by a default.

**Dynamic entries.** Kinds built at runtime get an explicit `dynamic` entry naming the
call site and the permitted pattern:

- `brief_forge_$decision` in `lib/brief-forge.sh`;
- `pack_resolver_${level}` in `lib/pack-resolver.sh`;
- the `_jobs_audit` wrapper in P08's `bin/_jobs.sh`.

**Non-recording hooks.** A `non_recording_hooks` list names every hook under
`hooks/shared/` that writes no record, with a reason. For example, context-bloat-warn
never logs. hooks-status reads this list instead of hardcoding it.

**Classification.** Every record gets two independent values, so a fail-closed block
whose check never ran is never confused with either a real block or a clean pass.

| Field | Values |
|---|---|
| `class` | `observation` (something ran or happened), `finding` (an advisory check matched), `block_decision` (a hook decided to block; enforcement depends on the host honoring the exit code), `override` (an operator override was recorded), `receipt` (a mandatory writer's record; only its own read-back verifies persistence) or `diagnostic` (resolver and alias warnings). |
| `check` | `performed`, `not_performed` (for example `reason` in `scanner-unavailable`, `collection-unavailable` or `scan-unavailable`) or `unknown`. |

For example, the unavailable-scanner records in `secret-scan-block` and
`customer-data-block` are `class: block_decision, check: not_performed`.

The `reviews` category is marked `delegated: li-review-read`. The generic reader counts
review lines but never classifies verdicts or parses review content.

**Coverage shape test** (`tests/shape/event-catalog-producers.sh`). It finds every
`audit_log` call and every declared wrapper call under `bin/`, `lib/` and `hooks/`,
including calls split across continuation lines. It fails if:

- a literal producer is missing from the catalog;
- a non-literal category, kind or field list does not match a `dynamic` entry;
- a catalog code producer no longer exists;
- a hook directory is neither a catalog producer nor in `non_recording_hooks`.

Field order is left to the round-trip tests. Instruction-only producers are exempt from
call extraction.

### Routing without side effects

1. Add one pure resolver to `bin/_audit.sh` that creates nothing. It exposes:
   - `audit_dir <category>`, which prints the write directory;
   - `audit_file <category>`, which prints the write file, with no fallback;
   - `audit_read_files <category>`, which prints the write file and then, when it
     differs, the legacy global file `$LINTEL_AUDIT_DIR/<category>.jsonl`, one per line,
     without checking whether either exists.

   `audit_log` writes only to `audit_file`. Readers keep today's first-existing rule over
   `audit_read_files`, name the file they read, and report on stderr any later listed
   file that also exists but was not read, so pre-migration history is never hidden
   silently. The resolver is the only routing implementation.
2. Sourcing `_audit.sh` and resolving paths create no directories. `audit_log` creates
   its directory immediately before writing. `_audit_out_dir` stays for
   `bin/li-review-log`. P08 finds every writer that relied on directories created at
   sourcing time and makes it create its own.
3. `audit_log` keeps its signature, envelope, escaping, destinations and advisory return
   code 0.
4. `lib/scale-estimator.sh` stops routing `granularity.jsonl` on its own and reads
   through `audit_read_files` with the same first-existing rule.
5. `usage-log` enumerates `usage-*.jsonl` in the resolver's global-scope directory.

### Structured reader

Add `bin/li-events.py`, stdlib only, with parsing shared through `lib/event_log.py` if
split.

- It sets `sys.dont_write_bytecode`.
- It uses `lib/native_paths.py` `native_io_path` for file I/O.
- It reads only explicit files and never writes.

**Commands.** `summary --file PATH [--category C] [--kind K] [--since ISO]` and
`records` with the same options.

**Summary output:**

```json
{
  "schema_version": 1,
  "catalog_version": 1,
  "source": {"path": "...", "state": "present | absent | unreadable"},
  "status": "observed | observed_with_diagnostics | unobserved | error",
  "records": {"lines": 0, "valid": 0, "selected": 0, "malformed": 0, "duplicate_key": 0,
              "unknown_kind": 0, "undated": 0, "incomplete_tail": false},
  "by_kind": {"<kind>": {"count": 0, "class": "...", "check": "...",
                         "first_ts": "...", "last_ts": "..."}},
  "diagnostics": [{"line": 1, "code": "...", "detail": "..."}],
  "evidence": "observed_records_only",
  "verification": "not_performed",
  "enforcement": "not_established"
}
```

**Records output** is JSONL:

- a valid record is `{"line", "category", "kind", "ts", "class", "check", "fields",
  "normalized"}`, where `fields` holds the raw strings and `normalized` holds the alias
  values;
- a line with a diagnostic is `{"line", "diagnostic", "detail"}`;
- under `--since`, undated records are emitted as `undated` diagnostic lines instead of
  records, so they are never silently kept or dropped.

**Diagnostic codes:**

- `malformed_json`;
- `duplicate_key`, detected with an object-pairs hook so a duplicate reserved key
  cannot silently replace `kind`;
- `missing_envelope` and `non_string_value`;
- `unknown_kind`;
- `undated`;
- `incomplete_tail`, for a final line without a newline, whether or not it parses.

**Exit codes, in order of precedence:**

| Exit | Meaning |
|---|---|
| 2 | Unreadable file, catalog load failure or usage error. |
| 4 | At least one line exists and at least one diagnostic was raised, including a file of only malformed lines or only a truncated tail, regardless of filters. |
| 3 | The file is absent or empty, or no record remains after filtering, with no diagnostic. |
| 0 | At least one selected valid record and no diagnostic. |

A read error is never reported as `unobserved`. Exits 3 and 4 are data outcomes: skill
snippets branch on them and must not run the reader under `set -e`.

**Forbidden verdicts.** The verdict-bearing values are `status`, `evidence`,
`verification`, `enforcement`, `class`, `check` and consumer-facing text. None of them
may contain the whole tokens `healthy`, `dead`, `firing`, `enforced` or `complete`.
This check does not apply to keys, diagnostic codes or catalog kind names such as
`cycle_complete`.

### Consumer migration (P08-owned)

**`audit_count`**

- It reads the first existing file from `audit_read_files` and reports a later existing
  file on stderr.
- When no listed file exists, it prints nothing on stdout, writes `unobserved:` with the
  listed paths on stderr and returns 3. An existing log prints its count and returns 0.
- Its comment must document it as an approximate bash line counter; `li-events` is the
  structured reader.
- Records a since filter excludes because they lack `ts` are reported on stderr.

**`hooks-status`**

- Read the first existing file from `audit_read_files hooks`, instead of a path relative
  to the working directory, name it, and read it through `li-events`.
- Use the producers' actual fields `hook`, `tier`, `blocked`, `reason` and string
  `override: "true"`, together with `class`, `check`, `records_when` and
  `non_recording_hooks`. There is no `hook_name`, `override_reason` or `run_id`.
- Replace `--dead` verdicts with "no observed record in window".
- Hooks that record only findings, blocks or failures, and non-recording hooks, are
  reported as such, never as dead.
- Registration, symlinks and settings are activation observations, not firing.
- The frontmatter description no longer says "active-vs-dead".

**`audit`**

- Take counts and diagnostics from the reader, and list malformed lines separately.
- "Nothing has been audit-logged" becomes "no records observed in <paths>; absence is
  not evidence that nothing ran".
- If a since date cannot be computed, say so instead of silently removing the filter.
- Use the writer's routing through `audit_file`.

**`usage-log`, `maintenance` and `retro`**

- Low or absent usage is reported as "unobserved/low observed usage", never as a dead
  or never-invoked verdict. This includes `maintenance`'s never-invoked grouping.
- `retro` reads `tier=BLOCK`, `blocked="true"` and `check` through `li-events`. It
  keeps them separate from the ledger's `BLOCKED` status.

**`jobs`**

- `job_action` is documented but never emitted. Remove it from the documentation, or
  list it as instruction-only.
- `job_stale_warn` is attributed to the job-stale-warn hook, not to `bin/_jobs.sh`.

**Documentation truthfulness**

- `bin/_audit.sh`'s comment "absence of a record means absence of an event" is
  corrected.
- `skills/capture/SKILL.md` ("silent by design") and `skills/usage-log/SKILL.md` must
  state the actual behavior: `audit_log` warns on stderr and returns 0, and some hooks
  discard that stderr.
- `hooks/shared/README.md:108` must say that findings, blocks, overrides and failures
  log, while clean passes and non-recording hooks do not. Absence is not non-execution,
  and a block record is not proof of host enforcement.
- The matching `docs/power-user.md` sentence about firing and dead hooks is corrected.

### Mandatory writers and failure propagation

`audit_log` stays advisory. These mandatory writers keep failure propagation:

- `li-review-log`;
- Brief Forge;
- envelope replay;
- domain results;
- `state_append`.

These gain it:

- the lesson store writes (A13.2);
- `bin/_jobs.sh` creation and update of `job.yaml`. A failed or short write returns
  non-zero with an explicit message instead of being ignored. The advisory
  `jobs.jsonl` line stays advisory.

`hooks/shared/job-begin/run.sh` must not print "Job started:" when `job_create` fails.

**Store-failure matrix.** Each store is made unwritable by replacing its path with a
regular file. chmod-based read-only directories are unreliable under Git Bash on NTFS.

| Unwritable path | Must still exit 0 | Must fail | Warning |
|---|---|---|---|
| The resolved audit write directory: an explicit `LINTEL_AUDIT_DIR` other than `$LINTEL_HOME/audit`, or a v5 repository's `.claude/runtime/audit` | Advisory producers, `state_append`, lesson add and job creation, because their audit lines are advisory. | `li-review-log`, Brief Forge and envelope replay, whose records live there. | Expected only where stderr is not discarded. The hooks that discard stderr (session-digest, cycle-incomplete-warn, cycle-position-inject) are asserted silent. |
| A writer's own store: state directory, lesson file or jobs directory | — | That writer, non-zero, with no success line. | — |

The matrix never replaces `$LINTEL_HOME/audit` itself. Twenty-one hooks, frozen-zone-warn
among them, run an unconditional `mkdir -p "$LINTEL_HOME/audit"` under
`set -euo pipefail`, so they exit 1 before warning when that path is not a directory. The
defect predates A13, is outside this release, and goes to the coordinator as a separate
finding.

### Ledger diagnoses

- **Unknown `entry_format`.** `state_cycle_segment` reports an unknown value as
  `state_diagnostic: unsupported entry format`. The block's status is reported as
  untrusted, never as a trusted DONE.
- **Legacy blocks.** Blocks without `entry_format` keep their status but carry
  `completeness: unknown (legacy entry)`.
- **Session-digest.** The digest renders ledger position through `render_cycle_footer`,
  or an equivalent shared status-grounded helper. A STARTING, INCOMPLETE or BLOCKED
  phase is never shown as a completed position. The ledger is Markdown, and no second
  ledger parser is added.

## A13.1.b P10 installer observation seam (gated)

This follows P10 acceptance and integration. The mapping below is **provisional**: P08
consumes P10's own fields rather than re-deriving them.

- Native installers stay free of Python and audit writers.
- A13 reads installer evidence only through P10's accepted surfaces: the native receipt
  check, `li-lifecycle` inspect/doctor JSON and `li-managed-transaction`. It never adds
  a second parser of `meta.tsv`, `plan.tsv`, `journal.json` or snapshot records.

| P10 state | Evidence |
|---|---|
| `prepared`, `applying`, `recovering` | Incomplete observation |
| `complete`, `recovered` | P10-verified terminal file state |
| `no_incomplete_operation` for an absent store | Unobserved |
| Host activation, hook execution, registration | `unverified` |
| Operation profile | Recorded input, not enforcement |

**Doctor acceptance.** The integrated doctor must derive no firing or not-firing verdict
from logs. P10's replacement doctor is expected to satisfy this at integration. Today's
`bin/li-doctor:246-260` does derive "has fired" and "never left an audit record"
verdicts.

**Fan-in items for the coordinator:**

- the `hooks/hooks.json` comment "li-doctor checks this";
- the catalog entry for `audit_log migration claude_home_migrated`, which P10 replaces
  with `li-lifecycle migrate`.

## A13.2 Lessons: IDs, retrieval, sinks and promotion

### Grammar

A lesson heading is `## L-<digits> — <title>`, outside fenced code blocks.

- Writers emit an em dash surrounded by spaces. Readers also accept ` - `.
- New IDs have at least three digits and are compared numerically.
- A block runs from its heading to the line before the next H2 heading outside a fence.
  This deliberately changes the current behavior, where a block ends only at the next
  `## L-` heading, and needs a fixture. CRLF is tolerated.
- The markers `superseded_by: L-NNN` and `supersedes: L-NNN` may appear on any block
  line, optionally behind `> `, and may carry trailing text such as a date. Writers
  place them on the first body line.
- `**Rule:**` is recommended, not required.

Readers report the following on stderr instead of silently skipping them:

- `## L-` headings with an unparseable ID;
- duplicate IDs;
- supersede targets that do not exist;
- dated `## YYYY-MM-DD` headings. In a project store these are unindexed legacy entries.

stdout of existing read functions keeps its current format.

### Stores

- **Project store.** It is always resolved by `lintel_lessons_file`. The hardcoded paths
  in `learn`, `capture`, `sense`, `lessons`, `lessons-surface`, `discover`,
  `session-digest` and `job-end` are replaced by that resolver.
- **Outside a repository.** The result is "no project lessons store (unobserved)",
  distinct from an existing empty store.
- **Unmigrated repositories.** When both `tasks/lessons.md` and
  `.claude/memory/lessons.md` exist, readers name the store they read and the one they
  ignore. Lessons in the ignored store are never hidden silently.
- **Missing store.** The helper creates a missing project store from the scaffolding
  template with the same conditional write. It refuses outside a repository.
- **Legacy operator lessons.** The existing read-only view of `~/.lintel/lessons.jsonl`
  stays, labelled "legacy operator lessons, not ID-managed". There is no import and no
  write to it.

### Writes

- **Allocation.** The next ID is one more than the maximum numeric ID in the store,
  including superseded and duplicate IDs. An empty store starts at `L-001`. IDs are
  never reused. Duplicates are diagnosed but do not block allocating a fresh ID.
- **Conditional write.**
  1. Take the existing mkdir lock convention: a timeout, and a lock that is never broken
     automatically (`bin/_jobs.sh:394-404`, `lib/profile_context.py:793-809`).
  2. Record the store's prior state (`file_state`, or absent) and build the new content
     from those bytes.
  3. Write through `lib/context_safety.py` `atomic_write` with `expected` set to that
     prior state and `check_expected=True`. The comparison runs immediately before
     `os.replace`. If the store changed, the write refuses with a retry message and
     replaces nothing. Pass the existing file's mode instead of the 0o600 default; a new
     store is created with mode 0o644.
- **Add** appends a new block at the end.
- **Update** rewrites only the selected block's body and keeps its ID. It refuses if the
  ID is absent or duplicated.
- **Supersede** adds a new block carrying `supersedes:` and stamps the old block with
  `superseded_by:`, in one conditional write.
- Nothing is deleted. `skills/lessons/SKILL.md`'s advice to delete lessons becomes
  advice to supersede them.
- After a successful store write, emit `audit_log lessons
  lesson_recorded|lesson_updated|lesson_superseded scope=… id=… classification=…`. This
  audit line is advisory.
- **Global scope.** Refuse with "operator lessons sink not activated". The pack field
  and its resolver stay untouched.

### Retrieval

`bin/li-lessons.py get --id L-NNN [--store FILE]` prints the exact block, including a
superseded block with its visible marker.

| Exit | Meaning |
|---|---|
| 0 | Found. |
| 1 | Absent. |
| 2 | The requested ID is duplicated or malformed. |

Diagnostics about other parts of the store go to stderr and do not change the exit.
`global:L-NNN` refuses as "not activated".

Other readers:

- `lessons_surface` and `lessons_count` keep excluding superseded blocks. Their stdout
  is unchanged, and diagnostics go to stderr.
- The digest shows the three active lessons with the highest numeric IDs through the
  awk entry point.
- `lessons-surface --id`, `skillify --from-lesson` and `sense`'s count use the two
  entry points only.

### Promotion (`bin/li-lessons-promote`, `skills/lessons-promote`)

The skill calls the bin; it has no separate Git recipe. Arguments are parsed before any
source resolution, so `--help` and usage errors never depend on the current directory
under `set -e`.

**Source**

- `--source FILE`, or the project resolver.
- The lesson is selected with `--id L-NNN`. Interactive selection lists every lesson by
  ID, not only the first 30 by position.

**Generalized text**

- Supplied with `--generalized-file FILE` for non-interactive use, or through `$EDITOR`.
- It must contain exactly one H2 heading. The bin rewrites that heading to the
  destination's next ID.

**Provenance.** The bin appends one comment:

```html
<!-- lintel-promotion: source_label=<label>; source_id=L-NNN; source_commit=<sha|unrecorded>; promoted_on=<YYYY-MM-DD> -->
```

- Non-interactive use requires an explicit `--source-label` matching
  `[A-Za-z0-9._-]{1,64}`, so a private or customer repository name is never copied
  implicitly. Interactive use proposes the source repository basename for explicit
  confirmation.
- `source_commit` is recorded only with `--record-source-commit`. The operator appears
  only through `--operator`.
- Output states that sensitivity is operator-attested unless an existing shared scanner
  actually ran.

**Destination**

- Either `--lintel-dir` or `LINTEL_DIR` is required. The script-parent and
  `$LINTEL_HOME` defaults are removed.
- The destination is any Git work tree, including a linked worktree.
  `scaffolding/01-foundation/.claude/memory/lessons.md` must exist in it.

**Duplicates.** An existing block with the same `source_label` and `source_id`, or the
same normalized title, stops with the existing ID and makes no write.

**Default mode.** Conditionally write only the target file, then print its diff and the
suggested commands. HEAD, the current branch, `refs/heads` and the index stay unchanged.

- Tests assert this with `git --no-optional-locks`, path-limited diffs,
  `ls-files -s`, `for-each-ref refs/heads` and `core.autocrlf=false` in fixture
  repositories.

**`--commit --expect-branch NAME`**

1. **Preconditions, checked before any write.** The current branch equals `NAME` and
   HEAD is not detached. Nothing is staged. The target has no uncommitted change.
2. **Commit.** Write, stage only the target, and commit only that path.
3. **Verify.** The new commit's parent is the old HEAD, the target is the only changed
   path, and no ref other than the current branch moved.
4. **If verification fails** (for example, a destination hook staged extra files, or
   HEAD moved concurrently), leave the commit in place. Print the old and new SHAs and
   the operator's remedy, and exit 11. Never reset automatically.
5. **If the commit fails**, restore the prior bytes only if the file still equals what
   the bin wrote, then unstage the target and exit 10. Otherwise exit 9 without
   touching the file.

Never `checkout`, `switch`, create a branch, push or open a PR.

**Exit codes**

| Exit | Meaning |
|---|---|
| 2 | Usage, including a missing destination, a missing `--source-label` in non-interactive use, or a generalized file without exactly one H2. |
| 3 | Source missing. |
| 4 | Destination is not a work tree. |
| 5 | Target missing. |
| 6 | Invalid or absent lesson ID. This keeps the existing "invalid lesson number" meaning. |
| 7 | Duplicate; already promoted. |
| 8 | Commit precondition failed. |
| 9 | Conditional-write conflict. |
| 10 | Commit failed and bytes restored. |
| 11 | Committed, but verification failed. |

**Documentation.** Update `CONTRIBUTING.md`, `docs/power-user.md` and `docs/faq.md`
where they describe promotion. The `job-end` hook text and
`docs/concepts/jobs-system.md:69` must state that the hook only suggests promotion; it
does not append job lessons.

**Scaffolding baseline.** `scaffolding/01-foundation/.claude/memory/lessons.md` keeps
its purpose and changes as follows:

- its format example becomes a description with no heading-shaped line, so no phantom
  or invalid lesson lands in new stores or the promotion destination;
- its dated-heading example and "most recent first" comment change to the L-NNN grammar
  and append-at-end allocation.

If P10's installed inventory pins that file, the coordinator reconciles it at fan-in.

## A13.3 Freeze: advisory boundary corrections

Keep P08's advisory `code-freeze` and `code-unfreeze` metadata and its existing test.
Fix these contradictions:

- `skills/code-freeze/SKILL.md` keeps a `--ignore-freeze` failure mode although it
  states no such flag exists, and still claims that `/help` shows frozen paths.
- `hooks/shared/frozen-zone-warn/HOOK.md` still offers `--ignore-freeze` and misstates
  the paths. It must describe the actual behavior:
  - the hook reads two sources: prefix matches from
    `$LINTEL_HOME/freeze/${LINTEL_SESSION_ID:-default}.yaml`, and substring matches
    from the current directory's `CLAUDE.md` "Frozen zones" section;
  - it is opt-in and warn-only, with no `/clean` enforcement and no glob list;
  - it does not read the advisory freeze metadata P08 records.
- The hook's message must name `/li:code-unfreeze` instead of `/unfreeze`.
- `docs/power-user.md` must no longer claim that other skills refuse, that freeze is
  enforced or that it expires. Its description of the two sources must match the hook.

P08 does not edit `skills/CATALOG.md`; the coordinator regenerates it at fan-in. No path
alignment, copying, hook activation or BUILD/QA consumer is added.

## A13.4 Tests

Extend the existing `tests/integration/observation-learning.{sh,py}`, which already has
two methods.

**Isolation.** Tests set synthetic `HOME`, `USERPROFILE`, `HOMEDRIVE`, `HOMEPATH`,
`APPDATA`, `LOCALAPPDATA`, `TEMP`, `TMP` and `LINTEL_*` values. They use Git ceiling
directories and fixture repositories only. They assert that every home-derived path
(`HOME`, `USERPROFILE`, `Path.home()`, `expanduser("~")` and `LINTEL_HOME`) resolves under
the synthetic root, and never read or stat the real profile.

### A13.4.a (released)

1. **Producers round trip.** Run each producer, read the result with `li-events`, and
   assert the catalog fields, aliases, `class` and `check`:
   - `secret-scan-block` with a finding, an override and a scanner-unavailable run
     (`block_decision`/`not_performed`);
   - frozen-zone-warn, session-digest, and the job begin, end and stale hooks;
   - one Brief Forge blocked record;
   - the alias producers dh-cost-budget-warn, frontend-design-surface and
     no-customer-data-in-screenshot.
2. **Review round trip.** `li-review-log` output read by `li-review-read`. `li-events`
   only counts the lines.
3. **Routing agreement.** Writer path equals reader path for:
   - an explicit `LINTEL_AUDIT_DIR`;
   - a v5 repository;
   - an unmigrated repository;
   - the Copilot environment (`lib/copilot-env.sh`).

   In a v5 repository where only the legacy global file exists, readers read it. Where
   both exist, they read the write file and report the global file on stderr.
   Read-only consumers create no `LINTEL_HOME`, audit directory or bytecode on a fresh
   synthetic home.
4. **Absence and malformed records.** Assert every row of the exit-precedence table:
   absent, empty, filtered to zero, only-malformed, truncated tail, duplicate `kind`,
   non-string value, unknown kind, and undated with `--since`. `audit_count` on an
   absent log returns 3 with empty stdout. The forbidden-token check applies to
   verdict-bearing values only.
5. **Failure propagation.** Both rows of the store-failure matrix.
6. **Ledger diagnoses.**
   - A truncated v1 block, an unknown `entry_format` (never a trusted DONE) and a
     legacy block each give their diagnosis.
   - The digest and footer show STARTING, INCOMPLETE and BLOCKED without implying
     completion.
7. **Lessons.** One shared fixture directory runs through both entry points. It covers:
   - allocation as maximum+1 across gaps, superseded entries and duplicates;
   - update keeping the ID, and supersede stamping both blocks;
   - `get` with `--store` for a found, an absent, a duplicate and a superseded lesson;
   - a dated heading, a fenced example and a marker with a trailing date;
   - the new block boundary and both separators;
   - a held lock or changed store refusing;
   - two-store reporting in an unmigrated repository;
   - writes refusing and reads working without Python;
   - global scope refusing, and the legacy JSONL view staying read-only.
8. **Promotion.**
   - Refusals:
     - destination not configured;
     - a non-interactive run without `--source-label` (which never writes the source
       name);
     - a generalized file with zero or two H2 headings;
     - `--source` from outside a repository.
   - Default mode leaves HEAD, `refs/heads` and the index unchanged, including in a
     linked-worktree destination.
   - `--commit` refuses, with no write, on a staged unrelated file, a dirty target, the
     wrong branch or a detached HEAD.
   - A valid `--commit` changes exactly one path on the expected branch.
   - Injected failures:
     - a commit failure restores the bytes (10);
     - a hook that stages an extra file exits 11 and leaves the commit;
     - a destination write conflict exits 9.
   - A rerun is idempotent (7).
   - The promoted lesson is retrievable by ID in the destination with its provenance
     fields.
9. **Freeze.** Keep the advisory metadata and warn-only legacy-hook scenario, and assert
   the corrected message.
10. **Consumer wording.** A shape test asserts that hooks-status, audit, usage-log, retro
    and maintenance, including hooks-status's description, issue no dead,
    never-invoked or "nothing ran" verdict.
11. **Catalog coverage.** The shape test described under A13.1.a.

### A13.4.b (gated with A13.1.b)

Through P10's accepted reader, cover a complete, an interrupted and an absent-store
transaction produced by the integrated P10 surface. Each is reported as verified file
state, incomplete or unobserved, with host activation `unverified`. Also assert that the
integrated doctor derives no firing verdict from logs.

### Retained and expected results

Keep these passing:

- the memory, audit, jobs and jobs-concurrency tests;
- the state-segment, context-ownership and enterprise-workflow tests;
- the review tests.

The integrated `universal-work-lifecycle.py` jobs `age-unknown` expectation is satisfied
by P08's `_jobs.sh` at integration.

`tests/shape/catalog-regenerates-clean.sh` is **expected to fail** in P08's tree after
the hooks-status, lessons-promote or code-freeze descriptions change. The coordinator
regenerates the catalog at fan-in. Record that failure with the regenerated diff; do not
edit `skills/CATALOG.md`.

## Write scope and limits

**Owned by the P08 card:**

- `bin/_audit.sh`, `bin/_jobs.sh`, `lib/memory.sh`, `lib/state.sh`,
  `lib/cycle-footer.sh`, `lib/scale-estimator.sh` and `bin/li-lessons-promote`;
- the observation and learning skills listed in the card, plus `capture`, `sense`,
  `discover` and `fix`;
- direct concept docs, including `docs/concepts/jobs-system.md`, and tests.

**New files:**

- `lib/event-catalog.json`, `bin/li-events.py`, and `lib/event_log.py` if split;
- `bin/li-lessons.py`;
- `tests/shape/event-catalog-producers.sh`, the consumer-wording shape test, and the
  shared lesson fixture directory.

**Explicitly released coordinated amendments:**

- `hooks/shared/session-digest/run.sh`: lesson and ledger display only;
- `hooks/shared/job-end/{run.sh,HOOK.md}`: resolver and truthful text;
- `hooks/shared/job-begin/run.sh`: the success message only;
- `hooks/shared/frozen-zone-warn/{HOOK.md,run.sh}`: documentation and message text only;
- `hooks/shared/README.md`: the audit statement;
- `docs/power-user.md`: its freeze, hooks-status and promotion paragraphs;
- `CONTRIBUTING.md` and `docs/faq.md`: promotion paragraphs;
- `skills/skillify/SKILL.md`: by-ID lookup;
- `scaffolding/01-foundation/.claude/memory/lessons.md`: the format example and grammar
  comments only;
- `hooks/shared/job-stale-warn/HOOK.md`: only the documentation of the emitted age field
  (`age_hours_str`). This coordinator decision accompanies the marker decision below.
  The emitted field stays unchanged, and a consumer that reads `age_hours` is reported
  rather than fixed by renaming;
- `bin/li-review-read`: exactly one `mkdir -p "$(dirname "$marker")"` immediately before
  the legacy-import marker append, and nothing else. This coordinator decision resolves
  item 2 of "Routing without side effects" against the P05-reader prohibition below:
  after the base resolver stopped creating the repository audit root, that append was
  the only direct write that relied on it. With `GSTACK_HOME` set, an empty legacy file
  and no audit directory, the command exited 1 instead of 0. `li-review-log`,
  `lib/brief-forge.sh` and `li-envelope-replay` need no change. A resolver exception was
  rejected. The line lands in its own commit with an A13-owned discriminating
  regression, and the A13 review assesses it as a cross-package change.

**Coordinator fan-in items (not P08 changes):**

- adding the new runtime files to the explicit installed-resource inventories
  (`bin/li-copilot.py` `ADAPTER_RESOURCES`, `lib/capability-selections.json`) with
  P07/P10;
- the `hooks/hooks.json` doctor comment;
- regenerating `skills/CATALOG.md`;
- the P10 migration producer entry;
- scaffolding inventory pinning.

**Not permitted:**

- changing the `audit_log` envelope or P05 review schemas and readers;
- P10 doctor, health, installers, transactions or migration skills;
- hook registration or activation, and generated catalogs;
- private sync, global destinations, auto-spawn or calibration writers;
- network or remote operations;
- editing real-home data.

Any other surface is reported as a proposed consumer amendment for the coordinator.

**Evidence.** The P08 A13 report records:

- the exact commits, file hashes and test commands with real exits;
- a RED run before implementation for the reader, allocation and promotion cases;
- the catalog coverage result and the expected catalog-regeneration failure;
- every deviation from this contract, with its reason.

Independent SPEC then QUALITY review uses this contract and the unchanged plan A13
acceptance: "absent telemetry cannot imply healthy/dead or successful enforcement".
