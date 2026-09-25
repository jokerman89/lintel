# ADR-0037: Tier the pull request CI matrix by what the diff touches

- **Status:** Accepted direction, 2026-09-25; the draft PR's first hosted runs verify it
- **Date:** 2026-09-25
- **Deciders:** the operator ("reduce CI so PRs are faster"); design set by the PR-stabilization
  coordinator and implemented by its CI lane on `jokerman-microsoft-ci-pr-speedup`
- **Supersedes:** ADR-0032 in part (the operating systems of a pull request's suite matrix)
- **Superseded by:** —

## Context

ADR-0032 made the strict suite a matrix of three operating systems by seven parts. Every pull
request therefore starts 21 suite jobs, the syntax job and the separate catalog workflow, whatever
it changes.

With eight open pull requests, jobs queued for over an hour:

- A personal plan runs at most five macOS jobs at once, and each run asks for seven.
- A Windows shard takes up to about 22 minutes.
- One observed pull request run took 1 to 20 minutes per Ubuntu shard, 3 to 19 per macOS shard
  and 6 to 22 per Windows shard. Queueing stretched its total wall time to about 75 minutes.

Many open pull requests change only Markdown: plans, reviews, ADRs, guides and root entry files.
For them the macOS and Windows jobs repeat the Ubuntu result and hold the queue for code changes.

Two more facts bound the design:

- `pull_request` was filtered to `branches: [main]`, so a stacked pull request whose base is
  another feature branch got no CI at all.
- `main` has no branch protection, and its only ruleset is disabled, so job names are free to
  change.

## Decision

We chose a path-tiered matrix. A new `plan` job computes the suite matrix, and the `suite` job
reads it with `fromJSON`. `bin/li-ci-matrix.py` makes the choice. It uses only the Python 3
standard library and runs git read-only. `tests/unit/ci-matrix.sh` tests it.

- **Every run tests every part on Ubuntu.** The seven parts, shards, timeouts and `--require-all`
  steps of ADR-0032 are unchanged, so every discovered test runs strictly on at least one system
  on every pull request.
- **The full matrix (Ubuntu, macOS and Windows)** runs when any of these holds:
  - the event is a push to `main`, a `workflow_dispatch`, or anything else that is not a pull
    request;
  - the pull request carries the `ci:full-matrix` label;
  - the diff touches a platform-sensitive path (defined below);
  - the diff cannot be computed. A missing SHA, a failed git command, unparsable git output,
    unreadable labels, an empty diff and an unexpected planner error all fail safe to the full
    matrix.
- **The diff** runs from the merge base of the pull request's base and head SHAs to the head SHA.
  It lists both sides of a rename and includes deleted files. The `plan` job checks out with
  `fetch-depth: 0`, so both SHAs are present.
- **A platform-sensitive path** is any of these:
  - any path under `bin/`, `lib/`, `install/` or `.github/workflows/`;
  - any non-Markdown path under `tests/`, `hooks/` or `shims/`;
  - any file with the extension `.sh`, `.py`, `.ps1`, `.psm1`, `.psd1`, `.js`, `.mjs`, `.cjs`,
    `.ts`, `.json`, `.yaml`, `.yml`, `.toml`, `.cmd` or `.bat`;
  - any file without an extension, including dotfiles such as `.gitattributes`;
  - any file whose extension is not on the documentation allowlist. The allowlist is Markdown,
    HTML, text and common image formats. An unknown extension widens the matrix and never narrows
    it;
  - any file that is added, deleted, renamed (both sides), copied or changes type, whatever its
    extension, unless the path lies under `docs/`, `.claude/` or `presentations/`. Adding or
    removing a file changes the installed file set, where path length, letter case and reserved
    names differ per system. Nothing under those three trees is installed.
- **A documentation-only pull request** runs the suite on Ubuntu alone. It modifies Markdown, HTML,
  text or images anywhere outside the always-sensitive locations above, and adds, deletes or
  renames such files only under `docs/`, `.claude/` or `presentations/`. Modifying an existing
  `skills/x/SKILL.md` stays on Ubuntu; adding one runs the full matrix.
- **The log.** The `plan` job prints its decision, its reason and every path that caused it, and
  writes the same to the job summary.
- **Triggers.** `pull_request` has no branch filter in `ci.yml` or `catalog.yml`, so stacked pull
  requests get CI. `push` is limited to `main`, and `workflow_dispatch` is kept. Both workflows
  cancel an older run for the same ref.
- **`catalog.yml` stays.** It overlaps with the `other` part's `li-catalog.py --check` step, but it
  costs one short Ubuntu job, reports catalog drift in about ten seconds instead of after the
  `other` part, and `tests/unit/observation-spine-skills-present.sh` requires it. Removing it
  would save no macOS or Windows capacity, which is what the queue waits for.

## Alternatives considered

- **Keep the full matrix on every pull request.** Rejected: that is the measured problem. Seven
  macOS jobs per pull request cannot all run within five concurrent slots, and documentation
  pull requests wait behind code pull requests for results that rarely differ by system.
- **Run macOS and Windows only nightly or only on pushes to `main`.** Rejected: code pull requests
  would merge with no cross-system signal. ADR-0032's first hosted run found defects that appeared
  only on macOS or Windows, such as the macOS `/var` link and Windows choosing System32's WSL
  `bash.exe`. This option would let such defects land on `main` before anyone saw them.
- **Skip the workflow for documentation paths with `paths-ignore`, or select jobs with a
  third-party paths-filter action.** Rejected: `paths-ignore` would run no tests at all on a
  documentation pull request, and it cannot choose systems per job. A third-party action adds an
  unreviewed dependency where a small tested script is enough.
- **A path-tiered pull request matrix.** Selected, as described above.

## Consequences

- **Positive:**
  - A documentation-only pull request asks for no macOS or Windows jobs. Its suite finishes in
    about the time of the slowest Ubuntu shard, and it no longer holds the macOS slots that code
    pull requests need.
  - Code pull requests still run the full matrix, and every push to `main` does too.
  - Stacked pull requests get CI.
- **Negative:**
  - A documentation-only pull request gets no macOS or Windows signal. It changes no code and
    adds, deletes or renames files only in trees that are never installed, so a system-specific
    failure could only come from how code on one system reads changed content, for example an
    encoding or line-ending problem in an edited skill. The push to `main` runs the full matrix and
    catches such a failure at the latest after merge. Apply `ci:full-matrix` when an edit to
    installed documentation deserves cross-system evidence before merge.
  - The suite starts after the `plan` job, which adds its checkout time to every run. The planner
    also becomes part of the CI's trusted path. Its unit test and its fail-safe default contain
    that risk.
  - The label is read from the event payload. After adding it, push a commit, or close and reopen
    the pull request. "Re-run jobs" replays the original payload and does not see a new label.
    Dispatching the workflow on the branch always runs the full matrix.
- **Neutral:**
  - Job names are unchanged, so an Ubuntu-only run shows seven suite jobs instead of 21.
  - The matrix definition moves from `ci.yml` into `bin/li-ci-matrix.py`. The unit test pins the
    parts, shards and timeouts of ADR-0032.

## References

- ADR-0032 (the sharded strict suite, in part superseded here).
- `.github/workflows/ci.yml`, `.github/workflows/catalog.yml`, `bin/li-ci-matrix.py` and
  `tests/unit/ci-matrix.py`.
- `.claude/engineering/design-archive/TODOS-v2.md`, an earlier note proposing a documentation path
  filter for `ci.yml`.
