# Optional CAPTURE reports

This is the method owner for retrospective and release-summary views, including
the compatible Keep a Changelog output. Load only the selected section: an explicit
report request, an operator-selected substantial-cycle retrospective, or a
requested release summary. Do not run both views or the rest of CAPTURE by default.
The entrypoint retains all flags and its conversation-first/authorized-`--out`
contract. These views retain the original work/profile and do not grant approval.

### Step 8 — Retrospective (--retrospective)

Reflect on a concrete window using actual observations. Explicit `--since` wins; otherwise
`--scope day` means the prior 24 hours, `week` seven days, and `session` uses the latest
owned checkpoint timestamp when available, else a labelled 24-hour fallback. Validate
checkpoint provenance through `context_latest` / `context_checkpoint`, not a raw home scan.
A supplied revision is resolved to a real commit/time before reading history.

Gather only signals relevant to the selected work/window:

- Git commits and current task status, without calling local commits deployed or merged.
- Audit files named by `audit_read_files <category>` and read through `bin/li-events.py`
  with `--since`; retain diagnostics and name any additional legacy source not read.
- Recorded skill invocations in `usage-*.jsonl` under `audit_dir usage-skill`, when
  authorized and available. Recording is optional; absence is unobserved, not disuse.
- `state_cycle_segment` for the selected original cycle, not an unrelated ledger segment.

Report **delivered**, **stuck**, **surprises**, **what worked**, **friction** and
**patterns worth recording**, each with its actual evidence or uncertainty. Keep ledger
`BLOCKED`/`INCOMPLETE`/`UNTRUSTED` separate from a hook decision (`tier=BLOCK`,
`blocked="true"`, `check=performed|not_performed`). A hook block record is not evidence
of host enforcement. No commits does not mean no work; include observed uncommitted
progress without inventing delivery.

`--emit-lessons` proposes one to three useful patterns, with an existing-ID deduplication
check and explicit authorization per candidate before a write. Respect already explicit
approval of named candidates; do not demand a second approval for the same scope.
No durable pattern is a valid result. Audit failure leaves a degraded report with the
remaining real signals, not a healthy empty history.

During normal cycle CAPTURE, an authorized retrospective may be stored at
`.claude/memory/retros/<date>-<cycle-id>.md`. For standalone `--retrospective`, persist
only when `--out` was selected. Retain the compact observation shape:
```yaml
cycle_id: <id>
duration_human: <hours>
duration_cc: <minutes>
tokens_used: <approx>
usage_provenance: observed | estimated | unknown
# billing: <actual supplied billing evidence only; omit when unknown>

what_worked:
  - <thing>
what_friction:
  - <thing>
next_time:
  - <pattern to repeat>
  - <pattern to avoid>
```

Not always written — only if cycle was substantial enough that retro adds value (operator-driven).

### Step 8b — Release report (--release-summary)

Use the actual commit/tag window and delivery evidence to brief teammates or draft release
notes. Explicit `--since`/`--until` win; otherwise use the latest reachable tag to HEAD,
or a labelled seven-day window when no tag exists. Resolve revisions with
`git rev-parse --verify --end-of-options "<ref>^{commit}"`; pass the resulting full IDs
as quoted Git arguments. Pass time filters and optional literal path scope as separate
arguments too. Never evaluate report input as shell code, assume a `main` branch or
invent a release tag.

Gather commit subjects, scopes and actual changes. Local Git is sufficient for a local
change summary, not for claiming a merged PR or deployment. Read selected PR/delivery
evidence only through available authorized tools; absent authorization or tools means a
Git-only report with that limitation. No automatic network query follows from this mode.

Use Conventional Commit groups as a history index, not proof of delivered behavior
or a changelog category mapping. Keep other history visible rather than dropping it.
Preserve these sections when applicable:

- **Delivered work**: what verifiably landed, with commits/tags/PR evidence.
- **Features and fixes**: capabilities and corrected behavior, not just renamed files.
- **Migration notes**: replaced entry points, retained data/flags and operator actions.
- **Limitations and not shipped**: open original cards, unrun checks and unmet gates.
- **Statistics** (`--include-stats`): actual commit/file/change/contributor counts over
  the same window/scope; no invented PR count or personal contact details.

Default `--voice internal` is a concise engineering report. `--voice customer` produces
a **DRAFT**, preserving source fidelity and using the active pack's configured voice
policy and corpus. Missing corpus is uncalibrated; unavailable required review stays
unverified. The draft is not approved for distribution merely because it was rendered.
Before rendering, apply the actual applicable sensitive-data checks to ingested commit
and PR text. On a hit, name the source without repeating the sensitive payload and stop
that output; do not rewrite history or sanitize-and-publish as a workaround.

An empty selected window is reported as empty. Missing history, denied reads or unknown
delivery are limitations, not success. The report can feed SHIP's existing PR/release
documentation, but it creates no release, tag, commit, publication or approval.

#### Keep a Changelog output

Only when this format/output is requested, apply the following curation in the
current context. ChangelogMaintainer is the compatible format-specific view of
this method; do not dispatch it to repeat a report on unchanged release inputs.
This optional output does not invoke the other CAPTURE mutation steps.

1. **Detect format.** Read CHANGELOG.md, confirm Keep-a-Changelog. If absent: propose creating one.
2. **Find last release.** Reconcile the version section with the exact tag/commit
   and ancestry. Retain hand-authored entries and protected sections.
3. **Compare delivered behavior.** Select the approved baseline and candidate refs;
   inspect the release diff, relevant tests/docs and history to identify what users
   actually receive. Conventional Commit `!` or `BREAKING CHANGE` marks a breaking
   change, not an explicit deprecation. Verify compatibility impact and migration
   guidance against the delivered result. A `refactor` is not automatically a
   user-facing change; neither `feat` nor `fix` proves something shipped.
4. **Curate categories by meaning:**
   - Added: new delivered capability
   - Changed: changed user-visible behavior or supported contract
   - Deprecated: explicit deprecation with its announcement, replacement and any
     supported removal timeline; a breaking marker is not this evidence
   - Removed: capability actually removed in this release
   - Fixed: an evidenced delivered correction
   - Security: an evidenced security-relevant change, respecting disclosure limits
5. **Reconcile reverts and existing entries.** A feature added and fully reverted
   before release is not a shipped addition. A revert of previously released work
   can itself change delivered behavior; describe that effect in the appropriate
   category. For partial reverts retain only the final supported delta. Collapse
   duplicates/cancelled entries only with evidence and preserve curated wording;
   do not rewrite historical releases from a new interpretation of commit prefixes.
6. **Propose or persist the scoped entry.** Update Unreleased, or promote it to the
   explicitly requested version/date, only when authorized. Compare the final entry
   against the release diff and record omissions/uncertainty. Missing refs or behavior
   evidence require clarification, not an invented entry, date or successful write.

Examples:

```text
/li:capture --retrospective --scope day --emit-lessons
/li:capture --release-summary --since <verified-tag> --until HEAD --include-stats
/li:capture --release-summary --scope skills --voice customer --out <authorized-draft>
```
