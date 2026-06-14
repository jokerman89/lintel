# Capture vault sink

CAPTURE (Phase 8) can additionally write a short, human-readable session summary to an external
knowledge vault — e.g. an Obsidian vault — so the vault becomes the cross-repo memory layer (L6).
The repo's own capture artifacts (lessons, ADRs, cold-executor trio, retros) are unchanged: the
sink is **additive and write-only**. Nothing is ever read from the vault back into a repo by this
mechanism.

## Config

Pack config (`packs/_default/pack.yaml`; override in your active pack):

```yaml
capture:
  vault_sink_enabled: true                        # set false to disable
  vault_sink_path: ../jokerman-vault/50-sessions  # relative to repo root
```

Both fields resolve via `resolve_pack_field` (flat two-level keys — the resolver does not support
deeper nesting). Disable by setting `vault_sink_enabled: false` in the active pack.

## Behavior

- One file per session: `<path>/YYYY-MM-DD-<repo>-<short-slug>.md`, frontmatter + four sections
  (What was done / Decisions / Open threads / Pointers). Full template in `skills/capture/SKILL.md`
  Step 7b.
- **A missing vault never fails a session.** If the path does not exist at runtime, CAPTURE logs
  one WARN line, writes `vault_sink_skipped` to `.claude/runtime/audit/`, and moves on.
- Successful writes are audit-logged as `vault_sink_written`.

## Hard rules for summary content

No secrets or tokens. No customer or employer-internal data. No full file contents — repo-relative
pointers instead of payloads. Swedish or English, matching the session's working language. If the
session contains material that must not leave the repo, skip the export rather than sanitize it.

Navigation patterns on top of the sink (schema, dashboard, hub wikilinks, index):
see [obsidian-integration.md](obsidian-integration.md) (ADR-0007).
