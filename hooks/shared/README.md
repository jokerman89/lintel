# Lintel Hooks

33 hooks. **9 auto-register on a plugin install** via `hooks/hooks.json` — the session digest, the
two block gates (secrets, customer data), the secret warn-on-edit, the direct-push warn, the memory
budget warn, the two cycle-continuity hooks, and the prompt-scan. The remaining 24 — including all
the module warn-hooks — ship inert and are opt-in.

## Activation model (per A1 design decision)

Hooks ship INERT at `~/.lintel/hooks/`. They are NOT auto-installed into `~/.claude/hooks/` — operator manually symlinks each one to opt in:

```bash
ln -s ~/.lintel/hooks/<hook-name>/run.sh ~/.claude/hooks/<hook-name>.sh
```

Then register in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/<hook-name>.sh" }] }
    ]
  }
}
```

This honest-opt-in model means hooks never surprise the operator. The files in this directory are TEMPLATES + DOCUMENTATION; activation is intentional.

## Hook taxonomy

### Warn-only (27)

These hooks emit a warning to the conversation but do NOT block the tool call. Use when the operator should see something but the override is acceptable.

Cross-cutting:

1. `no-customer-data-in-message` — scans operator prompts for customer-data patterns
2. `no-secrets-in-edit` — scans Edit/Write payloads for secret patterns
3. `frozen-zone-warn` — warns when about to edit a frozen-zone path
4. `context-bloat-warn` — surfaces at the token / tool-call soft threshold
5. `no-direct-main-push` — warns on `git push` to `main` (requires per-batch auth)
6. `no-merge-without-review` — warns on PR merge without a current content-bound review decision
7. `no-customer-data-in-screenshot` — scans selected web-session artifacts for customer-data tells
8. `no-production-mutation-without-auth` — warns on prod-mutation Bash commands without explicit auth
9. `frontend-design-surface` — surfaces brand design patterns on frontend edits

Jobs:

10. `job-begin` — records workflow_root invocation
11. `job-end` — records workflow_root terminal status or abort
12. `job-stale-warn` — warns on jobs untouched beyond N hours

Data / persistence (da-):

13. `da-migration-irreversible-warn` — migration lacks a down-migration or has undocumented destructive ops
14. `da-retention-violation-warn` — edit reads retention-bound data without honoring the retention filter
15. `da-schema-drift-warn` — edit to a schema-ADR-referenced file or migration

DevOps / hosting (dh-):

16. `dh-cost-budget-warn` — commit pushes projected cloud cost above threshold
17. `dh-deploy-without-rollback-warn` — deploy/infra change without a rollback declaration
18. `dh-observability-gap-warn` — service entry-point change without instrumentation

Security / compliance (sc-):

19. `sc-auth-bypass-warn` — high-risk patterns in an auth-flow surface
20. `sc-compliance-gap-warn` — regulated-path edit with missing/gapped compliance evidence
21. `sc-threat-coverage-warn` — threat-surface edit not covered by a recent threat model

Tech architecture (ta-):

22. `ta-arch-drift-warn` — edit to a file pinned by an ADR's decisions block
23. `ta-complexity-budget-warn` — edited file exceeds the complexity budget
24. `ta-contract-collision-warn` — edit to an interface with declared consumers

Testing / QA (tq-):

25. `tq-contract-break-warn` — provider edit without a paired contract-test update
26. `tq-coverage-drop-warn` — commit drops coverage below threshold
27. `tq-perf-regression-warn` — edit to a perf-critical path

### Justified-block (2)

These hooks BLOCK the tool call. Override requires explicit operator argument + audit-logged reason.

13. `secret-scan-block` — BLOCKS commit/push when Tier 1 secret pattern detected in payload
14. `customer-data-block` — BLOCKS commit/push when Tier 1 customer-data pattern detected

Justified-block hooks are blocking because the cost of going through is far higher than the cost of stopping (committed secrets, customer-data in repo). The 2 selected are minimum-set; operator can promote warn-only → block via local settings.

## Per-hook structure

Each subdirectory contains:
- `HOOK.md` — what the hook does, when it fires, override path, audit log location
- `run.sh` — the actual script (POSIX shell)

## Install workflow

1. Choose hooks to activate (per project / per operator preference)
2. Symlink chosen hooks into `~/.claude/hooks/` (or repo-local `.claude/hooks/`)
3. Register in `~/.claude/settings.json` per the example above
4. Test in a sandbox session before relying on the hook in real work

## Audit

Hooks record findings, blocks, overrides and failures (such as an unavailable scanner) through the
shared advisory writer into `hooks.jsonl` (repo-scoped `.claude/runtime/audit/` on the v5 layout,
resolved by `bin/_audit.sh`). Clean passes and non-recording hooks (`context-bloat-warn`) write
nothing, a failed write only warns, and some hooks discard that warning. An absent record is
therefore not evidence that a hook did not run, and a block record is not proof that the host
honored the block. `lib/event-catalog.json` lists what each hook records and when; read the log
with `bin/li-events.py` or `/li:hooks-status`.

## See also

- The active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default) — hooks are an implementation layer for some of these
- `packs/_default/pack.yaml` — neutral defaults (compliance mode `advisory`, no gates)
