# Cohort 5 findings — Hooks (19) + override mechanics

status: complete
cohort: 5
scope: all 19 hooks at `hooks/shared/<name>/` (HOOK.md + run.sh), `bin/_audit.sh` override-audit infra
auditor_pass: read every run.sh AND every HOOK.md (not frontmatter-only)
motto: kraftfullt från start, ständigt evolverande — NO-CUT. Uplift thin hooks to strongest-peer depth.

---

## Per-kind floor (the bar this cohort is judged against)

Hooks are not skills. Several uniformity dimensions are **n/a-for-kind** and are NOT flagged as gaps:

| Kind | members | floor expectations |
|---|---|---|
| **justified-block** | secret-scan-block, customer-data-block | D1 explicit fire, D3 in/out contract, D6 override-recovery path REQUIRED, D12 block, D13 audit REQUIRED |
| **warn-only** | 12 (see README) | D1 explicit fire, D12 warn, D13 audit. D6 recovery n/a (no state to recover). D5 checkpoint n/a. |
| **surface-only / lifecycle** | frontend-design-surface, job-begin, job-end, job-stale-warn | D1 explicit fire, D13 audit. job-begin/end DO manage state (D5/D6 apply); the 3 warn-style surfacers do not. |

A warn-only hook missing D6 recovery is **n/a-for-kind**, not a finding. A justified-block hook missing D6 override IS a finding.

---

## The 19 hooks (verified by glob `hooks/shared/*/HOOK.md`)

customer-data-block, secret-scan-block, no-customer-data-in-message, no-secrets-in-edit, no-customer-data-in-screenshot, no-direct-main-push, no-merge-without-review, frozen-zone-warn, context-bloat-warn, stale-calibration-warn, non-first-party-warn, no-trailblazer-without-corpus, no-en-vocab-in-trailblazer, no-production-mutation-without-auth, brand-staleness-warn, job-begin, job-end, job-stale-warn, frontend-design-surface.

(README.md says "14 hooks" — it predates the 5 newer hooks: the 3 job-* lifecycle hooks + frontend-design-surface + no-production-mutation-without-auth. **README is stale — finding C5-DOC1.**)

---

## D7 pack-drivability table (PLAN SPECIAL ATTENTION)

The plan asks: do packs/WorkProfile change WHICH hooks activate, and which hooks hardcode MS-specific patterns that v4.0 says should be `pack.compliance.hooks`-driven?

**Grep result: ZERO hooks reference any of `pack`, `compliance.hooks`, `pack-resolver`, `WorkProfile`, `work_profile`.** No hook resolves an active pack. Activation is 100% operator-symlink (README A1 model) + a few per-hook env/marker escape hatches. The pack layer is entirely absent from the hook tier.

| Hook | hardcodes MS/first-party/Trailblazer-specific behavior? | should be pack-driven (v4.0)? | nano evidence |
|---|---|---|---|
| no-en-vocab-in-trailblazer | YES — Tier1 EN-vocab list inlined; `voice: trailblazer` gate | YES → `pack.voice.tier1_vocab` + `pack.voice.enabled` | run.sh:18-23 (hardcoded array), run.sh:13 |
| no-trailblazer-without-corpus | YES — TRAILBLAZER-CALIBRATION path + `voice: trailblazer` gate | YES → `pack.voice.calibration_path` | run.sh:13, run.sh:19-24 |
| stale-calibration-warn | YES — TRAILBLAZER-CALIBRATION 30-day rule | YES → `pack.voice.calibration_max_age_days` | run.sh:13-22, run.sh:36 |
| non-first-party-warn | YES — "MS first-party alternative" framing | YES → `pack.compliance.first_party_map` | HOOK.md:22, run.sh:21 (`first-party-alternatives.yaml`) |
| customer-data-block | PARTIAL — Swedish personnummer + `ärende`/`kase` case-id regex | YES → `pack.compliance.pii_patterns` | run.sh:34-35 |
| no-customer-data-in-message | PARTIAL — personnummer + Swedish case-id | YES → `pack.compliance.pii_patterns` | run.sh:28-34 |
| no-customer-data-in-screenshot | PARTIAL — personnummer | YES → `pack.compliance.pii_patterns` | run.sh:21 |
| no-production-mutation-without-auth | PARTIAL — az/kubectl/terraform; operator-extendable txt | PARTIAL → `pack.compliance.prod_mutation_patterns` (txt file is a half-step) | run.sh:14-31 |
| brand-staleness-warn | PARTIAL — "MS portal" framing, 90-day rule | YES → `pack.brand.max_age_days` | run.sh:27, HOOK.md:36 |
| secret-scan-block | NO — secret patterns are universal | optional → `pack.compliance.secret_patterns` for extension | run.sh:34-40 |
| no-secrets-in-edit | NO — universal secret patterns | optional → same | run.sh:17-32 |
| no-direct-main-push | NO — git-universal | NO (git semantics universal) | run.sh:16-24 |
| no-merge-without-review | NO — git + review-log universal | low — `pack.workflow.review_window_days` (7d hardcoded) | run.sh:18 |
| frozen-zone-warn | NO — operator/session policy | NO | run.sh (session+CLAUDE.md sources) |
| context-bloat-warn | NO — thresholds in config.yaml | NO (already config-driven) | run.sh:22-31 |
| job-begin / job-end / job-stale-warn | NO — lifecycle infra | NO | — |
| frontend-design-surface | NO — extension-bucket match | low — `pack.frontend.surface_extensions` | run.sh:20-23 |

**D7 verdict:** 9 of 19 hooks (5 full + 4 partial) carry MS/Sweden/Trailblazer-specific logic inlined that v4.0's pack model says belongs in `pack.compliance.*` / `pack.voice.*` / `pack.brand.*`. Today a non-MS operator who installs Lintel gets Swedish personnummer regex and EN-vocab Trailblazer gates with no pack switch to turn them off or swap them — only crude per-hook env/marker escape hatches. This is the single largest cohort-wide uniformity gap. The 6 universal hooks (secrets×2, main-push, merge, frozen, context-bloat) and the 4 infra hooks (job×3, frontend) are correctly pack-agnostic.

---

## D13 audit-consumption finding (PLAN SPECIAL ATTENTION)

The plan asks: does the override audit log EXIST and is it CONSUMED?

**Two parallel, non-converging audit systems exist:**

1. **`hooks.jsonl` / `jobs.jsonl`** — written by **raw inline `printf`** inside each run.sh. 17 of 19 hooks write here directly. **CONSUMED:** `hooks.jsonl` is read by `/li:hooks-status` (skills/hooks-status/SKILL.md:15 — "ingenting läser den" → this skill closes the loop, surfaces trigger-counts + override-patterns + dead hooks). `jobs.jsonl` is read by the jobs skill + `job-stale-warn`. **This loop is closed. Good.**

2. **`bin/_audit.sh` → category `.jsonl`** (meta-infra-overrides, orientator-override, brief-forge-override, pack-resolver, migration) — the v4.0 "unified audit writer." **NO hook calls `_audit.sh`.** Override events from the 2 justified-block hooks (the highest-stakes overrides in the whole system) are written by hand-rolled printf to `hooks.jsonl`, NOT through `_audit.sh`, and are therefore NOT in the unified override trail. `_audit.sh`'s own header (bin/_audit.sh:6-10) lists its writers — hooks are absent.

**Consumption of `_audit.sh` category logs:** `meta-infra-overrides.jsonl` and `pack-resolver.jsonl` are documented as consumed (docs/concepts/meta-infra-discipline.md:198-220; docs/concepts/pack-resolver.md:92-120) and `/li:uniformity` writes to `uniformity.jsonl` via `_audit.sh`. But **no skill grep-reads `meta-infra-overrides.jsonl` or `brief-forge-override.jsonl`** — they are write-only today (write side exists, read side is design-doc-only). `hooks-status` reads `hooks.jsonl` but is unaware of the `_audit.sh` category logs.

**D13 verdict:**
- Override audit **EXISTS** for all 17 logging hooks (block + warn) via `hooks.jsonl`. **CONSUMED** via `/li:hooks-status`. ✓
- But there are **two divergent writers** (raw printf vs `_audit.sh`) and **two divergent readers** (`hooks-status` vs the meta-infra/pack-resolver design docs) that never meet. The unified-audit promise of `_audit.sh` is not upheld by the hook tier — the most security-relevant overrides bypass it.
- **2 hooks do not audit at all:** `context-bloat-warn` (HOOK.md:7 "not logged — high-volume noise" — defensible, but means no observability of how often operators blow the budget) and the surface line in some warn hooks. **finding C5-D13a.**

**Proposed uplift (NO-CUT):** route every hook's audit through `bin/_audit.sh audit_log hooks <tier> ...` so block-overrides land in BOTH `hooks.jsonl` (for hooks-status) and the unified trail; teach `hooks-status` to read the `_audit.sh` schema (it already shares the `ts/kind` shape). Keep `context-bloat-warn` audit but at sampled rate (every Nth fire) rather than zero — restores observability without noise.

---

## Per-hook records

### secret-scan-block — STRONGEST HOOK
```yaml
component: hooks/shared/secret-scan-block
kind: hook
cohort: 5
sub_kind: justified-block
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 event PreToolUse(Bash) git commit/push; run.sh:15 regex gate", finding: "explicit + scoped — only fires on git commit|push", proposed: "uniform", why: "tightest fire-scope in cohort" }
  D2_tail: { state: present, nano: "run.sh:51 exit 1 (blocked) / :54 exit 0", finding: "explicit terminal states block vs pass", proposed: uniform }
  D3_objects: { state: present, nano: "in=$1 CMD string; out=exit code + audit record; HOOK.md:35-38 documents jsonl shape", finding: "in/out contract written down", proposed: uniform }
  D4_entrypoints: { state: present, nano: "PreToolUse Bash matcher", finding: "single correct entry-point", proposed: uniform }
  D5_checkpoints: { state: n/a-for-kind, nano: "stateless scan", finding: "n/a — no multi-step state", proposed: none }
  D6_recovery: { state: present, nano: "run.sh:20-27 override env-var path LINTEL_OVERRIDE_SECRET=1 + reason", finding: "override IS the recovery point; required for block tier and present", proposed: uniform }
  D7_pack: { state: absent, nano: "run.sh:34-40 hardcoded patterns", finding: "universal patterns — pack-extension optional not required", proposed: "optional pack.compliance.secret_patterns append", priority: low }
  D8_frontmatter: { state: present, nano: "HOOK.md:1-8 name/tier/event/fires_on/override/audit all set", finding: "fullest frontmatter in cohort", proposed: uniform }
  D9_briefforge: { state: n/a-for-kind, finding: "hooks are not hand-off points", proposed: none }
  D10_lessons: { state: absent, nano: "no lessons consult", finding: "could log repeat-false-positive patterns to lessons", proposed: "optional: surface 'this placeholder overridden 3×, add to allowlist'", priority: low }
  D11_subagent: { state: n/a-for-kind, finding: "hooks run inline by design", proposed: none }
  D12_failure: { state: present, nano: "run.sh:5 set -euo; git diff failure tolerated :30 || true", finding: "block tier, fail-safe on git-diff error", proposed: uniform }
  D13_observability: { state: present, nano: "run.sh:22-24 (override) + :44-46 (block) → hooks.jsonl; consumed by hooks-status", finding: "audits both block AND override; CONSUMED", proposed: "route through _audit.sh too (see D13 section)" }
  D14_necessity: { state: partial, nano: "HOOK.md:14-16 'why justified-block' = de-facto necessity", finding: "rationale present but no REQUIRED/RECOMMENDED/OPTIONAL stamp nor gap-if-skipped", proposed: "add necessity: REQUIRED + gap_if_skipped", priority: medium }
peer_comparison: { strongest_peer_in_cohort: self, this_component_depth: at-bar, uplift_needed: "D14 necessity stamp; optional pack-extensible patterns" }
operator_decision_required: no
priority: low
```

### customer-data-block
```yaml
component: hooks/shared/customer-data-block
kind: hook
sub_kind: justified-block
dimensions:
  D1_head: { state: present, nano: "run.sh:14 git commit|push gate" }
  D6_recovery: { state: present, nano: "run.sh:19-26 LINTEL_OVERRIDE_CUSTOMER_DATA=1 + reason" }
  D7_pack: { state: absent, nano: "run.sh:34-35 Swedish personnummer + ärende/kase regex hardcoded", finding: "MS/Sweden-specific PII patterns inlined — should be pack-driven", proposed: "pack.compliance.pii_patterns", why: "non-SE operator gets personnummer regex with no swap", priority: high }
  D13_observability: { state: present, nano: "run.sh:21-23 + :40 → hooks.jsonl; consumed", finding: "audits override+block; bypasses _audit.sh unified trail" }
  D14_necessity: { state: partial, nano: "HOOK.md:14-17 rationale; no stamp" }
  others: { state: "mirror secret-scan-block (strongest peer); at-bar except D7" }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: at-bar, uplift_needed: "D7 pack-driven PII patterns; D14 stamp" }
operator_decision_required: yes
priority: high
note: "D7 PII-pack uplift is operator-decision because it changes default behavior for non-SE packs."
```

### no-secrets-in-edit
```yaml
component: hooks/shared/no-secrets-in-edit
kind: hook
sub_kind: warn-only
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 PreToolUse(Edit|Write); run.sh:8 PAYLOAD=$1" }
  D3_objects: { state: present, nano: "in=payload string; out=stderr warn + audit" }
  D6_recovery: { state: n/a-for-kind, finding: "warn-only, no state — companion secret-scan-block is the block gate" }
  D7_pack: { state: absent, finding: "universal secret patterns", proposed: "optional pack append", priority: low }
  D8_frontmatter: { state: present, nano: "HOOK.md:1-8 override:'not applicable (warn only)' explicit" }
  D12_failure: { state: present, nano: "warn, never blocks; run.sh:5 set -euo" }
  D13_observability: { state: present, nano: "run.sh:34-38 → hooks.jsonl tier:warn; consumed" }
  D14_necessity: { state: absent, finding: "no necessity stamp", proposed: "necessity: STRONGLY RECOMMENDED + gap (secret reaches commit before block fires)", priority: medium }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: at-bar-for-kind }
operator_decision_required: no
priority: low
```

### no-customer-data-in-message
```yaml
component: hooks/shared/no-customer-data-in-message
kind: hook
sub_kind: warn-only
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 UserPromptSubmit — only hook on this event", finding: "explicit; note: distinct entry-point from rest of cohort" }
  D7_pack: { state: absent, nano: "run.sh:28-34 personnummer + Swedish case-id", finding: "SE-PII inlined", proposed: "pack.compliance.pii_patterns", priority: high }
  D13_observability: { state: present, nano: "run.sh:40 hooks.jsonl; HOOK.md:38 deliberately does NOT log prompt content (anti-leak) — good discipline", finding: "best privacy-aware audit in cohort" }
  D14_necessity: { state: absent, proposed: "necessity stamp", priority: medium }
  others: { state: "at-bar-for-kind" }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: at-bar-for-kind, uplift_needed: "D7 pack PII" }
operator_decision_required: yes
priority: high
note: "shares D7 pack-PII decision with customer-data-block."
```

### no-customer-data-in-screenshot
```yaml
component: hooks/shared/no-customer-data-in-screenshot
kind: hook
sub_kind: warn-only (post-fact)
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 PostToolUse(Bash|Skill /browse); run.sh:5 ARTIFACT_DIR=$1" }
  D3_objects: { state: partial, nano: "run.sh:13 reads dom.html in artifact dir — assumes /browse layout, not a written contract", finding: "in-contract is implicit on browse-run dir structure", proposed: "document expected dom.html contract in HOOK.md", priority: low }
  D7_pack: { state: absent, nano: "run.sh:21 personnummer", finding: "SE-PII inlined (subset of the 3 customer-data hooks)", proposed: "pack.compliance.pii_patterns (shared)", priority: high }
  D12_failure: { state: present, nano: "run.sh:7,14 missing dir/dom.html → exit 0 silent (fail-safe)" }
  D13_observability: { state: present, nano: "run.sh:26 hooks.jsonl incl artifact_dir; consumed" }
  D14_necessity: { state: absent }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: below-bar-for-kind, uplift_needed: "D3 documented dom.html contract; D7 shared PII pack; D14 stamp" }
operator_decision_required: yes
priority: medium
note: "weakest of the 3 customer-data hooks — only catches DOM text, HOOK.md:13 admits OCR-lite gap (image text unscannable)."
```

### no-direct-main-push
```yaml
component: hooks/shared/no-direct-main-push
kind: hook
sub_kind: warn-only
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 PreToolUse(Bash); run.sh:16-24 three push-pattern detectors" }
  D6_recovery: { state: n/a-for-kind, nano: "HOOK.md:30-32 override = in-conversation auth (no flag)", finding: "honest: warn fires either way, auth is conversational" }
  D7_pack: { state: absent, finding: "git-universal", proposed: none }
  D12_failure: { state: present, nano: "warn-only" }
  D13_observability: { state: present, nano: "run.sh:28 hooks.jsonl incl cmd_preview (120 char cap); consumed" }
  D14_necessity: { state: absent, proposed: "necessity stamp + 'gap: unreviewed main push'", priority: low }
  others: { state: "at-bar-for-kind; HOOK.md:34-36 correctly notes this is NOT a substitute for server-side branch protection — good honesty" }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: at-bar-for-kind }
operator_decision_required: no
priority: low
```

### no-merge-without-review
```yaml
component: hooks/shared/no-merge-without-review
kind: hook
sub_kind: warn-only
dimensions:
  D1_head: { state: present, nano: "run.sh:13 gh pr merge|git merge main gate" }
  D3_objects: { state: present, nano: "run.sh:15 reads review-log/entries.jsonl, cross-refs HEAD commit + CLEARED status — only hook that consults another log to decide", finding: "richest input-contract among warn hooks" }
  D7_pack: { state: absent, nano: "run.sh:18 7-day window hardcoded", finding: "near-universal; window could be pack.workflow.review_window_days", priority: low }
  D10_lessons: { state: absent }
  D13_observability: { state: present, nano: "run.sh:28 hooks.jsonl; consumed" }
  D14_necessity: { state: absent, proposed: stamp, priority: low }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: at-bar-for-kind, uplift_needed: "D7 configurable window; D14 stamp" }
operator_decision_required: no
priority: low
note: "exemplary D3 — should be the model for review-log-aware hooks."
```

### frozen-zone-warn
```yaml
component: hooks/shared/frozen-zone-warn
kind: hook
sub_kind: warn-only
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 PreToolUse(Edit|Write); run.sh:7 TARGET_PATH=$1" }
  D3_objects: { state: present, nano: "run.sh:15-56 two freeze sources (session yaml + project CLAUDE.md ## Frozen zones)", finding: "dual-source resolve documented" }
  D7_pack: { state: absent, finding: "operator/session policy, not pack", proposed: none }
  D12_failure: { state: present, nano: "run.sh:22 admits 'full YAML parser would be better' — grep heuristic; fail-open", finding: "self-flagged parsing fragility", proposed: "harden YAML parse (acknowledged tech-debt)", priority: low }
  D13_observability: { state: present, nano: "run.sh:69 hooks.jsonl incl source field; consumed" }
  D14_necessity: { state: absent }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: at-bar-for-kind }
operator_decision_required: no
priority: low
```

### context-bloat-warn
```yaml
component: hooks/shared/context-bloat-warn
kind: hook
sub_kind: warn-only
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 PreToolUse(any); run.sh reads session token/call counters" }
  D3_objects: { state: present, nano: "run.sh:9-11 reads sessions/<id>/tokens.txt + tool-calls.count; thresholds from config.yaml :22-31", finding: "config-driven thresholds — already pack-agnostic-correct" }
  D7_pack: { state: absent, finding: "config-driven, not pack-relevant", proposed: none }
  D12_failure: { state: present, nano: "run.sh:42-43 rate-limit 1/5-calls anti-spam — good" }
  D13_observability: { state: absent, nano: "HOOK.md:7,24-26 'not logged — high-volume noise'", finding: "ONLY hook with zero audit — operator can never see how often budget blown", proposed: "sampled audit (every Nth fire) to restore observability without noise", why: "self-observation spine wants this signal; noise solvable by sampling", priority: medium }
  D14_necessity: { state: absent }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: below-bar-for-kind, uplift_needed: "D13 sampled audit; D14 stamp" }
operator_decision_required: no
priority: medium
note: "the one D13 outlier — see audit-consumption section."
```

### stale-calibration-warn
```yaml
component: hooks/shared/stale-calibration-warn
kind: hook
sub_kind: warn-only
dimensions:
  D1_head: { state: partial, nano: "HOOK.md:4 'PreToolUse when target involves trailblazer-content' but run.sh has NO content gate — fires on calibration-age alone whenever invoked", finding: "frontmatter claims content-conditional fire; run.sh:24 fires purely on file age — mismatch between declared and actual head", proposed: "either add the trailblazer-content gate run.sh promises, OR fix frontmatter to match", why: "D1 explicitness broken by doc/impl divergence", priority: medium }
  D7_pack: { state: absent, nano: "run.sh:13-16 TRAILBLAZER-CALIBRATION path; run.sh:36 30-day hardcoded", finding: "Trailblazer/voice-specific — pack.voice", proposed: "pack.voice.calibration_path + max_age_days", priority: high }
  D12_failure: { state: present, nano: "run.sh:24 no calib file → exit 0 (not this hook's job)" }
  D13_observability: { state: present, nano: "run.sh:38 hooks.jsonl; consumed" }
  D14_necessity: { state: absent }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: below-bar-for-kind, uplift_needed: "D1 doc/impl reconcile; D7 pack.voice" }
operator_decision_required: yes
priority: high
note: "D1 divergence is a concrete bug, not just a uniformity gap."
```

### non-first-party-warn
```yaml
component: hooks/shared/non-first-party-warn
kind: hook
sub_kind: warn-only
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 Edit|Write on manifests; run.sh:16-19 manifest-extension gate" }
  D3_objects: { state: present, nano: "run.sh:21 reads first-party-alternatives.yaml; payload diff" }
  D7_pack: { state: absent, nano: "HOOK.md:22 'MS first-party alternative' framing; run.sh:21 alt-map yaml", finding: "MS-first-party concept inlined", proposed: "pack.compliance.first_party_map (MS pack ships the map; default pack ships empty)", priority: high }
  D12_failure: { state: present, nano: "run.sh:22 no alt-file → exit 0 silent" }
  D13_observability: { state: present, nano: "run.sh:41 hooks.jsonl incl hits; consumed" }
  D14_necessity: { state: absent }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: below-bar-for-kind, uplift_needed: "D7 pack.compliance.first_party_map; D14 stamp" }
operator_decision_required: yes
priority: high
```

### no-trailblazer-without-corpus
```yaml
component: hooks/shared/no-trailblazer-without-corpus
kind: hook
sub_kind: warn-only
dimensions:
  D1_head: { state: present, nano: "run.sh:13 voice: trailblazer frontmatter gate on payload" }
  D7_pack: { state: absent, nano: "run.sh:13 trailblazer gate; run.sh:19-24 CALIBRATION path", finding: "Trailblazer/voice-specific", proposed: "pack.voice.enabled + calibration_path", priority: high }
  D12_failure: { state: present, nano: "warn-only; run.sh:26 uncalibrated → warn" }
  D13_observability: { state: present, nano: "run.sh:35 hooks.jsonl (minimal — only ts, no payload); consumed" }
  D14_necessity: { state: absent }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: below-bar-for-kind, uplift_needed: "D7 pack.voice; D14 stamp" }
operator_decision_required: yes
priority: high
```

### no-en-vocab-in-trailblazer
```yaml
component: hooks/shared/no-en-vocab-in-trailblazer
kind: hook
sub_kind: warn-only
dimensions:
  D1_head: { state: present, nano: "run.sh:13 voice: trailblazer gate" }
  D7_pack: { state: absent, nano: "run.sh:18-23 Tier1 EN-vocab array fully inlined", finding: "vocab list hardcoded in script — most-inlined pack-data in cohort", proposed: "pack.voice.tier1_vocab (read from pack file)", why: "vocab evolves with Our Voice guide; editing a shell array is wrong layer", priority: high }
  D10_lessons: { state: absent, finding: "could pull new tells from lessons/corpus", proposed: "read tier1 from corpus file not inline array", priority: medium }
  D12_failure: { state: present, nano: "warn-only" }
  D13_observability: { state: present, nano: "run.sh:36 hooks.jsonl incl tier1_hits; consumed" }
  D14_necessity: { state: absent }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: below-bar-for-kind, uplift_needed: "D7 pack.voice.tier1_vocab; D14 stamp" }
operator_decision_required: yes
priority: high
```

### no-production-mutation-without-auth
```yaml
component: hooks/shared/no-production-mutation-without-auth
kind: hook
sub_kind: warn-only
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 PreToolUse(Bash); run.sh:14-18 cloud-verb heuristics" }
  D3_objects: { state: present, nano: "run.sh:21-31 operator-extendable production-mutation-patterns.txt", finding: "half-step toward pack-drivability via txt file" }
  D7_pack: { state: partial, nano: "run.sh:14-18 az/kubectl/terraform/gh/psql hardcoded; txt extends but cannot replace", finding: "extensible-not-swappable; pack should own the base set", proposed: "pack.compliance.prod_mutation_patterns (the txt file is the prototype)", priority: medium }
  D12_failure: { state: present, nano: "warn-only; HOOK.md:23-25 incident-response rationale" }
  D13_observability: { state: present, nano: "run.sh:35 hooks.jsonl incl pattern + cmd_preview; consumed" }
  D14_necessity: { state: absent }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: at-bar-for-kind, uplift_needed: "D7 promote txt→pack; D14 stamp" }
operator_decision_required: no
priority: medium
note: "best-architected extensibility (txt file) of the warn hooks — model for migrating others to pack."
```

### brand-staleness-warn
```yaml
component: hooks/shared/brand-staleness-warn
kind: hook
sub_kind: warn-only
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 PreToolUse(Skill /generate-*); run.sh:8 brand-version.txt" }
  D7_pack: { state: absent, nano: "run.sh:27 90-day hardcoded; HOOK.md:36 'MS portal'", finding: "brand-age rule + MS-portal framing", proposed: "pack.brand.max_age_days + portal label", priority: medium }
  D12_failure: { state: present, nano: "run.sh:12,16 no brand file/malformed → exit 0" }
  D13_observability: { state: present, nano: "run.sh:32 hooks.jsonl incl brand_age_days + skill_invoked; consumed", finding: "richest audit payload of the staleness hooks" }
  D14_necessity: { state: absent }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block, this_component_depth: at-bar-for-kind, uplift_needed: "D7 pack.brand; D14 stamp" }
operator_decision_required: no
priority: low
note: "HOOK.md:28-33 has explicit 'what's NOT in scope' — best scope-boundary doc in cohort; should be template for all HOOK.md."
```

### job-begin
```yaml
component: hooks/shared/job-begin
kind: hook
sub_kind: lifecycle
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 PreToolUse(Skill workflow_root:true); run.sh:23 grep workflow_root gate" }
  D2_tail: { state: present, nano: "run.sh:48 surface 'Job started'; companion job-end is the tail" }
  D3_objects: { state: present, nano: "in=skill_path+mode; out=~/.lintel/jobs/<id>/ dir + _active.md" }
  D5_checkpoints: { state: present, nano: "run.sh:45 job_create writes 00-state.md — IS a checkpoint", finding: "only hooks that manage checkpoints (job-begin/end)" }
  D6_recovery: { state: present, nano: "job dir + 00-state.md is resume point; job-stale-warn surfaces it", finding: "full lifecycle recovery — strongest D5/D6 in cohort" }
  D7_pack: { state: absent, finding: "lifecycle infra, pack-agnostic-correct", proposed: none }
  D12_failure: { state: present, nano: "run.sh:7 set -uo (no -e — tolerant); :18-19 .jobs-disabled/NO_JOB escape; missing helper → exit 0", finding: "fail-open never blocks skill" }
  D13_observability: { state: present, nano: "HOOK.md:22 jobs.jsonl job_begin; consumed by jobs skill + stale-warn", finding: "but writes jobs.jsonl via _jobs.sh, again NOT _audit.sh" }
  D14_necessity: { state: present, nano: "HOOK.md 'jobs are single source of truth for flows in flight' = de-facto REQUIRED for workflow_root", finding: "closest to a necessity declaration in cohort" }
peer_comparison: { strongest_peer_in_cohort: self (for lifecycle), this_component_depth: at-bar, uplift_needed: "route audit via _audit.sh; explicit necessity stamp" }
operator_decision_required: no
priority: low
note: "strongest non-block hook; only one with real D5/D6. Newer (v3.8) than README's 14."
```

### job-end
```yaml
component: hooks/shared/job-end
kind: hook
sub_kind: lifecycle
dimensions:
  D2_tail: { state: present, nano: "HOOK.md:4 PostToolUse(status DONE/ABORTED); run.sh:74 job_archive + :76 surface", finding: "explicit terminal protocol DONE|ABORTED|FAILED — best D2 in cohort" }
  D3_objects: { state: present, nano: "run.sh:41-64 promotes plan/spec/prompt/adr/lessons to durable homes" }
  D5_checkpoints: { state: present, nano: "reads job.yaml cleanup_policy; archives to _archive/<date>/" }
  D6_recovery: { state: present, nano: "HOOK.md:35-36 operator can mv from _archive/ back to jobs/ to revive" }
  D7_pack: { state: absent, proposed: none }
  D12_failure: { state: present, nano: "run.sh:7 set -uo; every cp ':46 || true' tolerant; missing helper exit 0", finding: "promotion failures non-fatal — fail-open" }
  D13_observability: { state: present, nano: "HOOK.md:26 jobs.jsonl job_end + result; consumed" }
  D14_necessity: { state: present, nano: "HOOK.md:12-14 'removes abandoned-plan-files failure mode' = de-facto necessity" }
peer_comparison: { strongest_peer_in_cohort: self/job-begin, this_component_depth: at-bar, uplift_needed: "route audit via _audit.sh; necessity stamp" }
operator_decision_required: no
priority: low
note: "richest D3 output-contract (artifact promotion) of any hook."
```

### job-stale-warn
```yaml
component: hooks/shared/job-stale-warn
kind: hook
sub_kind: surface-only
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 SessionStart; run.sh:40 stale_jobs(hours)" }
  D3_objects: { state: present, nano: "in=_active.md; out=per-job surface line + jobs.jsonl" }
  D6_recovery: { state: present, nano: "run.sh:47 surfaces continue/abort/branch options — IS the recovery prompt", finding: "turns stale state into actionable recovery" }
  D7_pack: { state: absent, nano: "run.sh:19-24 threshold from profile.yaml/env — config-driven", proposed: none }
  D12_failure: { state: present, nano: "run.sh:15-16 disabled-marker/NO_STALE_WARN; missing helper exit 0" }
  D13_observability: { state: present, nano: "run.sh:50 jobs.jsonl job_stale_warn incl age + threshold; consumed", finding: "has explicit budget:<100ms in frontmatter (HOOK.md:8) — only hook with perf budget besides frontend-surface" }
  D14_necessity: { state: present, nano: "HOOK.md:13 closes 'Tappad tråd' failure mode" }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block (for warn-quality), this_component_depth: at-bar-for-kind }
operator_decision_required: no
priority: low
```

### frontend-design-surface
```yaml
component: hooks/shared/frontend-design-surface
kind: hook
sub_kind: surface-only
dimensions:
  D1_head: { state: present, nano: "HOOK.md:4 PreToolUse(Read|Edit|Write on frontend ext); run.sh:20-23 ext gate" }
  D3_objects: { state: present, nano: "in=target_file; reads design-patterns/ vault (pattern.json + component-imports.json); out=1-line surface" }
  D5_checkpoints: { state: partial, nano: "run.sh:34-45 throttle marker per-session per-file — state, but not a resume-checkpoint", finding: "throttle-state ≈ light checkpoint" }
  D7_pack: { state: absent, nano: "run.sh:20 extensions hardcoded", finding: "low pack relevance; surface_extensions could be pack.frontend", priority: low }
  D12_failure: { state: present, nano: "run.sh:7 set -uo; empty vault/no match → silent exit; :30-32 disabled markers" }
  D13_observability: { state: present, nano: "run.sh:105 hooks.jsonl incl patterns[] + vault_size; consumed by hooks-status", finding: "richest structured audit (JSON array) of cohort" }
  D14_necessity: { state: present, nano: "HOOK.md frames as OPTIONAL surface; 'NOT in scope' section explicit", finding: "has scope-boundary doc like brand-staleness" }
  perf: { state: present, nano: "HOOK.md:9 budget <200ms + degradation note — exemplary perf-awareness" }
peer_comparison: { strongest_peer_in_cohort: secret-scan-block (frontmatter completeness), this_component_depth: at-bar-for-kind, uplift_needed: "explicit necessity stamp (OPTIONAL)" }
operator_decision_required: no
priority: low
note: "fullest frontmatter + best perf-budget doc; mixed SV/EN prose in HOOK.md (minor style)."
```

---

## Cohort summary

### Strongest hook: secret-scan-block
Fullest frontmatter, tightest fire-scope, required override-recovery present and audited, both block AND override logged, clearest justified-block rationale. The bar for the block tier. (job-begin/job-end are strongest for *lifecycle* depth — only hooks with real D5 checkpoints + D6 recovery.)

### Weakest hook: no-customer-data-in-screenshot
Below-bar-for-kind on three axes: D3 in-contract (dom.html layout) is implicit not documented; D7 inlines SE-PII like its siblings; HOOK.md:13 self-admits it cannot scan image text (OCR-lite gap) so it is the least-effective of the 3 customer-data hooks; no necessity stamp. (Runner-up weakest: stale-calibration-warn, whose D1 frontmatter claims a content-gate its run.sh does not implement — a concrete doc/impl bug.)

### Cohort-wide uniformity gaps

1. **D7 — no hook is pack-driven (HIGHEST LEVERAGE).** 9/19 hooks inline MS/Sweden/Trailblazer-specific data (PII regex, EN-vocab array, first-party map, calibration paths, brand-portal). v4.0's `pack.compliance.*` / `pack.voice.*` / `pack.brand.*` model is entirely absent from the hook tier. A non-MS operator gets Swedish personnummer detection and Trailblazer voice gates with only crude env/marker off-switches, no swap. `no-production-mutation-without-auth` (txt-extensible) is the prototype for how to fix this.

2. **D13 — two divergent audit systems; block-overrides bypass the unified trail.** All 17 logging hooks write to `hooks.jsonl`/`jobs.jsonl` via raw inline printf, CONSUMED by `/li:hooks-status` (loop closed ✓). But `bin/_audit.sh` — the declared v4.0 unified override writer — is called by NO hook. The 2 highest-stakes overrides (secret + customer-data block overrides) never reach the unified trail. `meta-infra-overrides.jsonl` / `brief-forge-override.jsonl` are write-side-design-only, no skill reads them. `context-bloat-warn` audits nothing at all.

3. **D14 — necessity declarations near-universally absent.** Only the 4 newest hooks (job×3, frontend-surface) carry de-facto necessity framing; the 15 older hooks have rationale prose but no REQUIRED/STRONGLY-RECOMMENDED/OPTIONAL stamp or `gap_if_skipped`. Uniform uplift: add `necessity` + `gap_if_skipped` frontmatter to every HOOK.md (brand-staleness + frontend-surface "NOT in scope" sections are the template).

### Secondary findings
- **C5-DOC1:** `hooks/shared/README.md` says "14 hooks" — stale by 5 (job×3, frontend-design-surface, no-production-mutation-without-auth). Update count + taxonomy (now 14 warn + 2 block + 3 lifecycle + 2 surface = mix).
- **C5-D13a:** `context-bloat-warn` is the only zero-audit hook — uplift to sampled audit.
- **stale-calibration-warn D1 bug:** frontmatter promises trailblazer-content-conditional fire; run.sh fires on age alone. Reconcile.
- Mixed SV/EN prose in several HOOK.md bodies (frontend-design-surface, hooks-status) — minor style uniformity.

### Counts
- hooks audited: **19**
- operator_decision_required = yes: **7** (customer-data-block, no-customer-data-in-message, no-customer-data-in-screenshot, stale-calibration-warn, non-first-party-warn, no-trailblazer-without-corpus, no-en-vocab-in-trailblazer) — all D7 pack-PII / pack-voice defaults-change decisions.
- priority high: 7 · medium: 4 · low: 8
