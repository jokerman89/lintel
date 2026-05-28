---
name: jstack-provenance-track
layer: ms-team
description: Track artifact provenance — source, transforms, voice tier, calibration state, distribution path.
color: blue
tools: Read, Write, Bash
voice: internal
cli_support: [claude-code, codex]
---

# /provenance-track

Records what an artifact is, where it came from, what voice tier applied, what calibration state backed the voice gate, and where the artifact ended up. Audit-trail for customer-bearing outputs.

Not a generation skill. A tracking skill. Run after `/document-generate`, `/msvoice-rewrite`, `/landing-report`, `/rais-customer-voice-check` to consolidate the artifact's "story" into one queryable record.

## When to use

- After a customer-bearing artifact lands — record provenance for compliance recall
- Before distribution — produce a provenance summary to attach to the artifact
- Post-incident — query "what went into this artifact" if a customer flagged it
- Periodic audit — verify all distributed artifacts have provenance records

## When NOT to use

- Engineering-internal artifacts — overkill (audit logs already exist per-skill)
- Single-step artifact (one skill produced it, never transformed) — its audit log suffices
- Pre-distribution dry-run (not yet sent anywhere) — wait until the artifact stabilizes

## Inputs

- Required `--artifact <path>` — the artifact to track
- Optional `--source-chain <list>` — explicit list of source files / generator skills if auto-detect insufficient
- Optional `--destination <text>` — where the artifact is going (customer name placeholder, channel, audience)
- Optional `--query <id>` — read existing provenance record by ID

## Workflow

1. **Locate artifact.** Read `--artifact`. Compute content hash (SHA256).
2. **Auto-detect source chain:**
   - Frontmatter `source:` or `generated_by:` fields
   - Frontmatter `voice:` for tier
   - Adjacent `~/.jstack/audit/*.jsonl` entries within 24h that reference the artifact path
3. **Calibration state.** If voice tier is trailblazer: read OurVoice-calibration.md, capture per-cell accuracy snapshot at time of artifact generation.
4. **Compose record:**
   ```yaml
   id: PROV-<hash-prefix>
   artifact: <path>
   content_hash_sha256: <hash>
   recorded_at: <iso-timestamp>
   voice_tier: <internal | trailblazer | mixed>
   calibration_at_generation:
     status: CALIBRATED | UNCALIBRATED | NOT_APPLICABLE
     per_cell_accuracy: { R1: 0.92, R2: 0.91, ... }
     snapshot_id: <CALIBRATION-NNN>
   source_chain:
     - skill: jstack-document-generate
       input: src/lib/dlxClient.ts
       at: 2026-05-27T15:23:11Z
     - skill: jstack-msvoice-rewrite
       at: 2026-05-27T15:34:02Z
     - skill: jstack-customer-voice-check
       verdict: PASS
       score: 88
       at: 2026-05-27T15:42:18Z
   compliance_gates_passed:
     - 5-always-on: at 2026-05-27T15:42:18Z
     - 7-on-demand: 6 PASS / 1 NEEDS_ACTION (resolved)
   destination: customer-A nordic-finserv quarterly-deck
   distributed_at: <iso-timestamp or null>
   ```
5. **Write to provenance store.** `~/.jstack/provenance/PROV-<hash>.yaml`. Also append index entry to `~/.jstack/provenance/index.jsonl`.
6. **Report.** Confirm record ID + summary.

## Report format

```
Provenance: PROV-7a8b3c2f

Artifact: docs/customer-demo-001-trailblazer.md
Content hash: 7a8b3c2fd9e1...
Voice tier: trailblazer
Calibration: CALIBRATED (11/12 cells ≥90%, snapshot CALIBRATION-2026-05-27)

Source chain:
1. /document-generate (input: src/api/billing/, at 15:23)
2. /msvoice-rewrite (at 15:34)
3. /rais-customer-voice-check (PASS 88/100, at 15:42)

Compliance:
- 5 always-on ✓
- 7 on-demand: 6 PASS, 1 NEEDS_ACTION (Item 3 data class — resolved by sanitization)

Destination: customer-A nordic-finserv quarterly-deck
Distributed: not yet (record pending)

Stored: ~/.jstack/provenance/PROV-7a8b3c2f.yaml
```

## Compliance integration

- Provenance records are append-only — never modified, only superseded with a new record if the artifact changes.
- Records contain calibration snapshot AT TIME OF GENERATION — even if calibration later drifts, the record reflects the state when the artifact was made.
- For trailblazer-voice artifacts: record is REQUIRED before distribution. Downstream `/release-ev2` for customer-bearing artifacts refuses without a provenance record.
- Records do NOT contain customer-data — destination uses placeholder format (customer name → "customer-A nordic-finserv").

## Voice tier note

`voice: internal`. Provenance records are engineering-internal — structured, queryable, append-only.

## Failure modes

- **Source chain auto-detect comes up empty:** ask operator to supply `--source-chain` explicitly. Do not fabricate.
- **Content hash mismatch on re-record:** create a NEW record (PROV-<new-hash>), do not overwrite. Old record retains.
- **Provenance store unwriteable:** treat as compliance failure for trailblazer-voice artifacts; refuse to confirm record. Internal artifacts: WARN but allow.
- **Calibration file missing for trailblazer artifact:** record marked UNCALIBRATED. Downstream `/release-ev2` will refuse.
- **Operator queries non-existent record by ID:** report not found, suggest `--query` against index.

## Examples

**Standard record:**
```
> /provenance-track --artifact docs/customer-demo-001-trailblazer.md --destination "customer-A nordic-finserv quarterly-deck"
✓ PROV-7a8b3c2f recorded.
```

**Query existing:**
```
> /provenance-track --query PROV-7a8b3c2f
[Prints record YAML]
```

**Pre-distribution check:**
```
> /provenance-track --artifact docs/draft.md
[Records as not-yet-distributed]
Ready to share. Re-run with --destination after sending to update.
```

## See also

- `~/.jstack/provenance/` — record store
- `~/.jstack/provenance/index.jsonl` — queryable index
- `/rais-customer-voice-check` — produces a verdict that lands in provenance
- `/release-ev2` — refuses customer-bearing without provenance record
- `/onecs-check` — produces compliance snapshot embedded in provenance
