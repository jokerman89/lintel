---
slug: launch-readiness
date: 2026-06-13
cycle_id: launch-readiness-20260612
operator: jokerman
affected_paths:
  - hooks/shared/{_input.sh,secret-scan-block,customer-data-block}/run.sh (ADR-0013, newline-class closures)
  - lib/state.sh, lib/cycle-footer.sh, bin/_audit.sh (current-cycle ledger segment, register B4)
  - lib/pack-resolver.sh, lib/cli-tiers.sh (sourced-set leak, cache key, id-normalization)
  - install/install.ps1, install/verify.sh, bin/li-doctor (Windows + bash-3.2 parity)
  - .copilot-plugin/, .droid-plugin/ (deleted — interop), 5 asserting surfaces
  - ~40 docs + skills (truth sweep, dormancy honesty, mechanism honesty)
  - tests/{unit,shape}/* (4 new behavior tests + multi-cycle + no-swedish scope + CATALOG generator)
risk_class: high
breaking_change: true
---

# Structure change: launch-readiness

> Gate M1 artifact. The v5.x "old-school ready" drive: an 8-audit launch-readiness register
> (docs/audit/2026-06-12-launch-readiness-register.md) + the remediation it found, executed as
> waves 0–7. ADRs 0013 (fail-closed gates) + the staged 0015/0016/0017. Builds on the v5.3
> in-flight craft raise (ADR-0014).

## What changed (shape)

**Security (ADR-0013):** block hooks fail-closed (no `set -e`) and the newline-class bypasses are
closed (line-continuation matcher evasion + newline-forged `-m` override), each with an adversarial
regression test; gate diffs are textconv-safe; `git push` scans the outgoing range; macOS bash-3.2
`read -t` fallback. **State (register B4):** `state_cycle_segment` scopes every ledger reader (footer,
resume, audit cycle_id) to the current cycle — append-only multi-cycle ledgers no longer poison
position/mode/completeness. **Multi-CLI:** two fabricated manifests deleted + propagated to all five
asserting surfaces; `lintel@`→`li@` everywhere; install.ps1 reaches identity-seed + lib/bin copy +
`shared/` hook parity; li-doctor is bash-3.2-safe; `.opencode/INSTALL.md` rewritten neutral.
**Honesty:** docs truth sweep across ~30 files (stale v3-plan/`tasks/`/`docs/adr`/gstack/version
refs), dormancy qualifiers at point of sale, usage-log + cycle telemetry + compliance prose streams
converted to real `audit_log` calls or labeled dormant. **Hygiene:** `no-swedish.sh` covers docs +
README (historical/generated/functional exempt); CATALOG generator is character-safe; exec bits
corrected on 5 scripts.

## Backward-compat

Mostly additive or alias-covered. The two BREAKING items: `.copilot-plugin/` + `.droid-plugin/` no
longer ship (those CLIs install via the `.claude-plugin/` marketplace entry through interop — README
+ getting-started document the path); Cursor stays tier `full` per operator override. New frontmatter
and audit categories are optional. No shared-helper signature dropped — `state_cycle_segment` is
additive; `_cf_state_last`/`_cf_phase_history` changed from file-arg to stdin (internal to
cycle-footer.sh, no external caller).

## Migration path

No new operator migration rows — security auto-applies via plugin update; the v5.1 alias removal-date
conflict was reconciled to the operative `config/aliases.yaml` (2026-09-12). The dated public-launch
follow-ups (real git-hook install, ADR-0019/0016/0017, H17/H18) live in the launch register §3-B, not
the migration index (they are forward work, not deprecations).

## Verification

Full suite green on the committed tree (L-010). New behavior tests: hook-gate newline/​push cases,
customer-data gate wrapper, context-checkpoint roundtrip, li-doctor smoke, multi-cycle footer +
loop-back. `no-swedish.sh` + `catalog-regenerates-clean.sh` (flake fixed) + `frontmatter-lint-all.sh`
green. Independent review (L-007) ran on the real diff before SHIP.

## Rollback

`git revert` per wave (commits are wave-atomic). Manifest deletion reverts by restoring the two JSON
files + the five assertions. Frontmatter/audit-category additions are optional. The ledger-segment
helper is backward-compatible with single-cycle fixtures (whole-file when no `CYCLE` block exists).

## Planned (not in this change — own ADRs, dated in the launch register §3-B)

Real git pre-commit/pre-push install (supersedes the command-string matcher, by 2026-07-15) ·
ADR-0019 AGENTS.md-primary execution · ADR-0020 lintel-state MCP · ADR-0021 eval-harness ·
H17 pack provenance · H18 plugin pinning · full-surface description→trigger sweep.
