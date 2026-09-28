---
name: pattern
layer: foundation
description: Use when recurring expectations (deployment baselines, dashboard behavior, document structure, visual language) should be captured, reviewed, versioned, shared or applied to named work as data-only patterns with explicit applicability, provenance and review traceability.
color: teal
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
necessity: OPTIONAL
gap_if_skipped: "Established team expectations stay implicit; work is planned and reviewed without an evidenced, versioned baseline."
---

# Pattern: reusable, data-only expectations

A pattern records expectations as clauses (`must`, `default`, `recommendation`). Each pattern
also has a selector saying where it applies, the sources it came from, and optional hashed local
assets. A blueprint is a pattern that includes other patterns by exact reference. Bindings state
which patterns a context requires or defaults to.

Patterns complement accepted policy. They grant no authority and never execute, fetch or install
anything.

This skill drives the reasoning: which sources to read, what the operator actually confirmed, and
what needs review. The deterministic work is done only by `bin/li-pattern.py` over
`lib/patterns.py`: validation, resolution, locking and safe persistence. Never re-implement
validation, hashing or precedence in prose or in another script. The frozen interface is
`.claude/plans/reusable-patterns/contract.md` in the Lintel source; the decision is ADR-0038.

## When to use

- The operator states an expectation that should hold for future work of a given kind or target.
- A repository, team pack or person wants to reuse a known-good structure across work, such as a
  dashboard, a report, a deployment topology or a visual language.
- Work must show which expectations applied, at which version, and whether review covered them.
- An existing pattern needs an update, deprecation, retirement, revocation, export or import.

## When not to use

- One-off preferences for the current task. State them in the brief instead.
- Enterprise enforcement. A repository can forge a binding, so patterns are advisory structure
  under host policy and branch rules, not a control.
- Inferring an organization's policy from generic public guidance, such as cloud landing-zone
  recommendations. An inaccessible mandatory source stays unknown; it is never guessed.

## Scopes and roots

| Scope | Catalog | Activation |
| --- | --- | --- |
| Repository | `.claude/patterns/catalog.json`, with bindings in `.claude/patterns/bindings.json` | Bindings and catalog bindings apply at repository scope |
| Active pack | The effective pack's `patterns.source` and its pinned includes | Pack catalog bindings apply at pack scope |
| Personal | `$LINTEL_HOME/patterns/catalog.json` | Never automatic; selected only by an explicit reference or a repository binding |

Default precedence runs in this order:

1. Explicit authorized task choice
2. Repository
3. Active pack
4. Explicitly selected personal pattern
5. The existing corpus/model fallback

Mandatory clauses constrain the whole chain. With no selected pattern, existing behavior is
unchanged, including Design DNA's brief > profile > corpus order.

A linked (junction or symlink) home, repository, `.claude` or pattern root is refused. Pass the
real path instead.

## Running the helper

The launcher builds a roots envelope from the ADR-0029 profile record and passes it on stdin.
Without the launcher, build the envelope explicitly:

```bash
source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"
profile_context_json | python3 "$LINTEL_SOURCE_ROOT/bin/li-pattern.py" envelope \
  --personal "$LINTEL_HOME" --repository "$LINTEL_REPO_ROOT" --profile-record - > "$envelope"
python3 "$LINTEL_SOURCE_ROOT/bin/li-pattern.py" list --roots-file "$envelope"
```

Every command prints one JSON report on stdout and its error diagnostics on stderr. Act on the
reported status; do not only check whether the exit code is zero:

| Exit | Status | Meaning for the workflow |
| --- | --- | --- |
| 0 | `ok`, `ready`, `empty` | Proceed. `empty` means no pattern applies and behavior is unchanged |
| 2 | `invalid` | Fix the input; nothing was written |
| 3 | `needs-context` | Ask for or cite the missing facts; do not guess them |
| 4 | `conflict` | Resolve the named conflict: settings, applicability or mandatory baseline |
| 5 | `unavailable` | A configured source is missing, changed, revoked, retired or unverified. Dependent work stops |
| 6 | `collision` | Another writer, or a stale digest. Re-read and retry deliberately |
| 7 | `review-unmet` | Mandatory clause evidence is missing or failing |

## Operations

| Command | Use it to | Notes |
| --- | --- | --- |
| `list`, `show --ref <source:id@version>`, `check` | Inspect catalogs or one pattern; validate a document or all sources | `list` reads no pattern bodies |
| `resolve`, `explain` (`--context`, optional `--refs`, `--overrides`, `--exceptions`, `--preview-draft`) | Select the patterns that apply to evidenced context facts | Advisory candidates are never requirements. `explain` adds the binding decisions |
| `resolve --lock <path>` | Freeze a ready or empty selection beside the initiative | Never overwrites an existing lock. Conflicts and unknown context never lock |
| `verify-lock --lock --context` | Check pins, lifecycle, revocations and the mandatory baseline before continuing | Never upgrades a pin silently |
| `map`, `project` | Map clauses to existing task IDs, and project one package's clauses | Regrouping never changes the selection |
| `capture --input --scope repo\|personal --name` | Register a new draft | Drafts are never selected for execution |
| `index --source-root` | Re-check registered entries and regenerate their metadata | Never discovers or blesses unregistered files |
| `approve --path --version --approval --expected-digest` | Publish a reviewed, strictly newer approved version | The draft stays unchanged, and every dependency must be approved |
| `update --path --input --expected-digest [--write]` | Create a strictly newer draft of the same pattern | Previews the clause diff and dependents; the old version and current pins stay unchanged |
| `deprecate`, `retire`, `revoke --ref --record [--write]` | Record a lifecycle event with its impact | Deprecated pins warn; retired and revoked pins block; there is no un-revoke |
| `apply --change [--write]` | Add, replace or remove one repository binding | Shows the reduced mandatory baseline before a required binding is weakened |
| `remove --ref [--write]` | Unregister an entry nothing references | Files and history are never deleted |
| `resolve`/`verify-lock --attestations` | Supply reviewed source attestations | Needed for URL sources of required patterns and for overdue patterns; renewal never changes the selection |
| `export --refs --out`, `import --bundle --scope --destination-source --version-map [--write]` | Share patterns as a local bundle | Import stages drafts with inert provenance; approve children first after review |
| `review --lock --context --evidence` | Check per-clause evidence coverage after verifying the lock | Exit 7 on unmet mandatory coverage; never a pass or release clearance |

Every write follows the same rules: explicit inputs, previews before writes, compare-and-swap
digests, and no silent change to active work.

## Capture procedure

1. Read only the sources the operator authorized: documents, policy exports, code, screenshots or
   an interview. Record each one as a source with its `kind`, `root`, `section`, `observed_at`,
   `confidence` and reuse limits. A URL is provenance, not a fetch instruction.
2. Separate what the operator confirmed from what you observed or inferred. Confirmed sources are
   `operator-statement` or `approved-standard` with confidence `confirmed`. Observed or inferred
   ones are `observation` or `inferred`. Observations become `default` or `recommendation`
   clauses unless the operator confirms a `must`.
3. Write a narrow selector from evidenced facts. An empty selector means "everywhere" and must be
   deliberate. Give each clause a `verify` statement that a reviewer can actually check.
4. Capture the pattern as a draft, and show the operator its clauses and provenance. Approve only
   after review, with a new version and an approval reference. Approval records provenance; it
   does not prove the approver's authority.
5. Keep each declared asset, and any `root: pattern` source, next to the draft file you capture,
   or pass `--files-from <dir>`. Every version carries exactly those files, digest-checked. Nothing
   else is copied, and a missing or changed file stops publication.
6. Never copy credentials, private source documents or absolute home paths into a pattern, lock
   or export.

## Workflow consumers

Phase and generation workflows consume patterns through the shared consumer contract in this
skill's `references/` directory, which is delivered by the workflow integration.

- Without configured patterns, those workflows behave exactly as before, and no prompts or files
  are added.
- Direct entry into any phase either resolves the current context or verifies an explicitly
  supplied lock.
- Assets are read with `read_asset`, bound to that selection.
- Pattern clause coverage is supplemental evidence inside the ADR-0028 review contract, never a
  separate pass.
