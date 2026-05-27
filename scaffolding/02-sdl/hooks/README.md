# JStack Hooks

14 hooks: 12 warn-only + 2 justified-block.

## Activation model (per A1 design decision)

Hooks ship INERT at `~/.jstack/hooks/`. They are NOT auto-installed into `~/.claude/hooks/` — operator manually symlinks each one to opt in:

```bash
ln -s ~/.jstack/hooks/<hook-name>/run.sh ~/.claude/hooks/<hook-name>.sh
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

This honest-opt-in model means hooks never surprise the operator. The 14 files in this directory are TEMPLATES + DOCUMENTATION; activation is intentional.

## Hook taxonomy

### Warn-only (12)

These hooks emit a warning to the conversation but do NOT block the tool call. Use when the operator should see something but the override is acceptable.

1. `no-customer-data-in-message` — scans operator prompts for customer-data patterns
2. `no-secrets-in-edit` — scans Edit/Write payloads for secret patterns
3. `frozen-zone-warn` — warns when about to edit a frozen-zone path
4. `context-bloat-warn` — surfaces at 50k token / 80 tool-call soft threshold
5. `stale-calibration-warn` — warns when TRAILBLAZER-CALIBRATION is >30 days old
6. `non-first-party-warn` — warns on new 3P dep without justification
7. `no-direct-main-push` — warns on `git push origin main` (requires per-batch auth)
8. `no-merge-without-review` — warns on PR merge without /review or /plan-eng-review record
9. `no-trailblazer-without-corpus` — warns on trailblazer-tagged output before T0 calibration
10. `no-customer-data-in-screenshot` — scans /browse screenshots for customer-data tells
11. `no-en-vocab-in-trailblazer` — Tier 1 AI-tell vocab detection in trailblazer-tagged files
12. `no-production-mutation-without-auth` — warns on prod-mutation Bash commands without explicit auth

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

Every hook fire (warn or block) logs to `~/.jstack/audit/hooks.jsonl`. Append-only.

## See also

- `scaffolding/02-sdl/HARD-RULES.md` (Phase 6) — the 5 always-on rules; hooks are an implementation layer for some of these
- `scaffolding/02-sdl/ON-DEMAND-RULES.md` (Phase 6) — the 7 on-demand items
- `/onecs-check` skill — operator-driven checklist that complements (not replaces) hooks
