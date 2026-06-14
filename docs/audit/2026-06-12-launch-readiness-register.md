# Launch-readiness register — v5.x "old-school ready"

> 2026-06-12/13 · cycle `launch-readiness-20260612` (meta-infra) · operator directive: *"a complete
> list of everything that's needed in order to comfortably, in every possible aspect, say that
> we're ready for launch — every i dotted, every aspect tested."*
>
> Bar locked by operator: **v5.x-solid** — the current shape made bulletproof. Public-launch
> items (pack provenance H17, plugin pinning H18, eval-harness, marketplace) are captured with
> dates in §3-B, not blocking. Evidence: eight parallel audit agents (A1 test-truth · A2
> mechanism-activation · A3 install · A4 docs-truth · A5 security-regression · A6 obligations ·
> A7 spine code · A8 multi-CLI); full reports in the cycle transcript. Every count below is
> tool-verified (L-003). Predecessors: battletest synthesis (2026-06-12), cli-issues-craft
> synthesis (2026-06-13).

## §0 — Snapshot at audit time

HEAD `754de5a` = v5.2.0 baseline, suite green there. The worktree carries the **uncommitted v5.3
in-flight change** (~86 entries: craft raise on 43 skills + 20 agents, manifest subtraction,
ADRs 0014–0017) from a session that died at the session limit. Its Wave A (the I1 security fix
+ 2 promised test files + `lib/auto-decide.sh`) is NOT in the worktree — it lives on the
unmerged branch **`fix/hook-gate-added-lines` (713388d, child of HEAD, pushed to origin)**.
Suite on the worktree: **73/76** — all 3 failures trace to the in-flight state (2 real, 1
concurrency flake).

## §1 — The bar (DEFINE)

"Ready" means every criterion below holds and is **tool-verified**, not asserted.

| # | Criterion | Verdict today |
|---|---|---|
| C1 | Every mechanism FIRES / DORMANT-by-ADR / CUT — none wired-but-unproven | 🔴 3 DEAD sold as live, 33 prose-obligated streams |
| C2 | Suite green on committed tree; behavior tests incl. negative paths for every control | 🔴 73/76 dirty; 26/76 behavior; I1 untested |
| C3 | Install + first hour: zero-setup plugin path, sh/ps1 parity, upgrade+uninstall documented | 🔴 ps1 3×P1; no uninstall; opencode toxic |
| C4 | Multi-CLI claims match tested reality | 🔴 1 FULL / 4 UNTESTED / 2 VAPOR; broken install strings |
| C5 | Docs tell the truth (counts, paths, claims) | 🔴 CHANGELOG 5.3.0 materially false; README v5.0 |
| C6 | Security closures regression-tested ± ; staged items dated | 🟡 ADR-0010 holds+tested; I1 stranded; 2 new P1 bypasses |
| C7 | Every obligation done / dated / cut | 🟡 46-row inventory exists; 10 block; key items undated |
| C8 | Release engineering coherent (version, CHANGELOG, tag, migrations, rollback) | 🔴 CHANGELOG untrue; SHIP-GATE red on own gate |
| C9 | Pride pass: zero known bugs, hygiene current, identity whole | 🔴 footer P0; CAIP leak; stale working-state |

**Overall: NOT READY — but nothing is structurally unsound.** The kernel (4 safety hooks'
ADR-0010 closures, pack resolver, state ledger, lessons/memory, capture) is verified live.
The distance to ready is: **6 P0 clusters · ~25 P1 · ~30 P2**, all mechanical, organized into
waves in §4.

## §2 — Evidence highlights (DISCOVER)

**C1 Mechanisms (A2):** 9 families FIRE with traces (digest, 4 safety hooks, ledger, pack
resolver, vault sink, capture). 4 DORMANT correctly per ADR-0008. 3 DEAD-but-sold-as-live:
`usage-log` (default-on writer calling a script that exists nowhere — P0 honesty), cycle
telemetry (`cycle-runs.jsonl` zero records across 4 real cycles; sold as unconditional write at
cycle:405), ~40 advertised per-skill jsonl streams of which **3 exist** (7% of advertised
observability). 33 skills carry prose-only write obligations; 6 bespoke `>>` writers bypass
`_audit.sh`. Jobs: readers shipped, no writer has ever run. Operator's `~/.claude/settings.json`
still carries the 4 manual hook entries → **every safety hook fires twice** (ADR-0008
consequence not executed).

**C2 Tests (A1):** 76 tests: 26 BEHAVIOR / 50 PROSE. Coverage: 10 mechanisms covered (several
adversarial ±), 3 partial, 4 MISSING (customer-data-block wrapper execution,
no-secrets-in-edit, no-direct-main-push, li-doctor; + footer multi-cycle case). The I1
fail-open path (8 hooks run `set -euo pipefail`; any internal nonzero exits 1 = warn-and-
proceed) is exercised by NO test anywhere; the fix + `hook-gate-content.sh` +
`skill-descriptions-trigger.sh` are stranded on 713388d.

**C6 Security (A5):** Every ADR-0010 closure verified closed at the cited lines, most with
positive+negative tests — the v5.2 work holds. NEW findings: **(1)** the git matcher is
line-oriented — a shell line-continuation (`git -C /repo \` ⏎ `commit -am`) makes both BLOCK
hooks exit 0 with no scan and no audit (P1, fires even without adversarial intent); **(2)** the
override token is forgeable via newline injection in a commit message (second line starting
`LINTEL_OVERRIDE_SECRET=1` matches the `^`-anchored grep) — the L-012 class again (P1; audited
but committed). One-line shared fix: flatten `$CMD` newlines before matcher+override greps +
two negative tests. Also: push-path scan is a no-op for already-committed secrets (P2), the
gate's own `git diff` honors hostile textconv/ext-diff drivers (P2 — add `--no-ext-diff
--no-textconv`), and `_input.sh:27` `read -t 0.2` fails open on macOS stock bash 3.2 (P1).

**C9/C2 Spine (A7):** **Footer P0 confirmed live**: `_cf_state_last`/`_cf_phase_history` parse
the whole multi-cycle ledger → a prior cycle's `cycle_complete: true` forces the thin "no
active cycle" footer for every later cycle, and `--here` doesn't escape; "here" also resolves
wrong (first-occurrence de-dup). Same class: resume integrity greps FIRST match (oldest cycle)
and keys on `branch:`/`commit:` nothing ever writes; `_audit.sh` reads `cycle_id` from env
nothing sets → **22/22 of today's audit records say `cycle_id:"unknown"`**. macOS bash 3.2
kills li-doctor (`declare -A`) and verify.sh (`mapfile`). Exec bits: install.sh, verify.sh, 3
runners committed 100644. pack-resolver cache key collapses to a constant (PPID=1) and its
sourced `set -uo pipefail` leaks into every caller.

**C3 Install (A3):** install.ps1 vs install.sh — **Windows bare-install is broken in three P1
ways**: no identity seeding (profile.yaml/active-pack — the migration row even says "re-run
install.sh", impossible on Windows), no lib/bin/templates copy (hooks can't resolve helpers),
flat hook layout (breaks settings snippet, li-doctor, welcome). `.opencode/INSTALL.md` is
frozen at v3 **with Microsoft-CAIP identity** (RAIS/Trailblazer, deleted paths, wrong counts)
and getting-started routes users to it. No uninstall path exists; upgrade story exists but is
unlinked from README/getting-started; three mutually inconsistent `~/.lintel` provisioning
models (copy vs symlink vs git-clone). Both installers claim "(4 layers)" — 1 exists.

**C4 Multi-CLI (A8):** Honest tiers: **FULL 1** (Claude Code — the only CLI ever verified
live) · **UNTESTED 4** (Codex, Cursor — `full` claim with zero artifacts beyond one manifest —
Gemini, Copilot) · **VAPOR-leaning 2** (Droid, OpenCode — actively broken) · best-effort bucket
honest. The flagship install string `lintel@jokerman-lintel` is wrong (plugin is `li`) in
cli-tiers:26,68 + SHIP-GATE:71,244. Fingerprint vocabulary can only produce 4 of 8 tier keys →
welcome's honest-tier display can't work on 4 CLIs. Manifest deletion not propagated to 5
contract surfaces (tests/verify/SHIP-GATE/README/cli-tiers). ADR-0019 (AGENTS.md-primary) is
right and staged; real scope quantified: 3 competing canonicals, 775 lines across 7 files, 10
factual drifts listed.

**C5 Docs (A4):** CHANGELOG 5.3.0 **claims the unshipped I1 fix, two phantom artifacts, and
"suite green" while red** (P0 — release notes lying about security). README says v5.0, ships
deleted manifests at :27, promises per-CLI guides that don't exist. `AGENTS.md`/`GEMINI.md`
call a v3 plan "current architecture" — and AGENTS.md is about to become primary.
state-of-the-harness (the "full mental model" link) teaches the deleted 4-layer model + dead
paths. CATALOG has 2 invalid-UTF-8 rows (generator byte-truncation) making its own guard
flaky. Swedish in 3 live concept docs; `no-swedish.sh` doesn't scan docs/ or README. 12 honest
counts verified exact (124 skills / 69 agents / 31 hooks / hook-matrix / 4-root map).

**C7 Obligations (A6):** 46-row consolidated inventory (see agent report): 10 block-launch
rows (all cheap; the two expensive-looking ones are already built and need landing), earliest
hard date 2026-06-28 (JSTACK alias removal), heaviest cluster 2026-09-12 (44 aliases +
post-grace sweeps + operator migrations; one date conflict 09-12 vs 12-12 to reconcile),
largest undated security promise = real git pre-commit/pre-push install. ADR numbering gap:
0012 → 0014. TODOS-v2.md needs a disposition pass (live skills still reference it).

## §3 — The register

### §3-A — Launch blockers (fix now, this cycle)

| # | Cluster | What | Source |
|---|---|---|---|
| B1 | **Land the stranded security fix** | Merge/cherry-pick `713388d`: I1 fail-closed hooks (drop `set -e` + guard), `hook-gate-content.sh`, `skill-descriptions-trigger.sh` (ADR-0014's promised guard), `lib/auto-decide.sh` (I3 one-way-door guard), added-lines/`-C` fixes | A1, A6 |
| B2 | **Land the v5.3 in-flight work honestly** | Propagate manifest deletion to 5 surfaces (plugin-manifests-valid.sh, verify.sh:330, manifest-identity.sh:49-69, SHIP-GATE:20, README:27, cli-tiers rows); rewrite CHANGELOG 5.3.0 to truth; write **ADR-0013** (fills the gap: the I1/hook-gate security decision); atomic commits; **suite green on committed tree** (L-010) | A1, A4, A8 |
| B3 | **New hook bypasses (L-012 class)** | Flatten `$CMD` newlines before matcher+override greps in both BLOCK hooks + negative tests (line-continuation, multiline override forgery); `git diff --no-ext-diff --no-textconv`; push-path outgoing-commit scan; `read -t` integer fallback (macOS fail-open); audit record on scanner-unavailable exit | A5, A7 |
| B4 | **Footer/state cross-cycle class** | `state_cycle_segment` helper in lib/state.sh; footer consumes it (fixes thin-tier P0 + wrong here/done/mode); `audit_log` derives cycle_id from ledger; resume integrity last-match + CYCLE block writes branch/commit; multi-cycle regression tests | A7, A1 |
| B5 | **Windows + portability floor** | install.ps1: seed identity + copy lib/bin/templates + `shared/` hook layout + real validation scope; li-doctor bash-3.2 + stale-path fixes; verify.sh mapfile + scaffolding-coherence repoint + cli-matrix repoint-or-delete; `lintel@`→`li@` ×4; Cursor tier demote; fingerprint↔tiers normalization; `.opencode/INSTALL.md` rewrite-or-demote (CAIP leak); exec bits +x; GEMINI.md slug/name | A3, A7, A8 |
| B6 | **Docs truth sweep** | README (v5.0→5.3.0, manifests, per-cli promise, missing rows); getting-started (role-activate, opencode pointer); AGENTS/GEMINI v3-plan + lessons-path + codex-subagents contradiction; shims (tasks/ paths, gstack rec); AGENT-INSTRUCTIONS matrix→cli-tiers pointer; state-of-the-harness + multi-cli.md rewrite-or-banner; LAYERS lists; MS-Layer language ×2; GLOSSARY/ta/tq dormancy qualifiers; Swedish ×3 + no-swedish covers docs+README; CATALOG UTF-8 generator fix | A4, A8, A6 |
| B7 | **Mechanism honesty** | usage-log demote (P0); cycle-runs telemetry → one `audit_log` line in cycle Step 8; granularity contradiction → one truth (dormant note in capture); jobs registry claims demoted until a writer fires; 7 compliance-flavored prose streams → `audit_log` one-liners or deleted; 6 bespoke `>>` writers → helper; pack-resolver cache key + sourced set -u leak; `_audit.sh` C0 catch-all + audit_count + append-warn; state.sh phase/key strip; li-doctor smoke + customer-data-block/warn-hooks execution tests | A2, A1, A7 |
| B8 | **Release close + hygiene** | "Upgrading & uninstalling" section (reconcile 3 provisioning models); migration-index date conflict + version-pinned labels → dates; working-state/MEMORY stale entries (PRs merged, v4.0-reframe closed); TODOS-v2 disposition; scaffolding `tasks/` template leftovers; M1 structure-changes entry + M2 compat audit + M4 recap for this cycle | A3, A6, A2 |

### §3-B — Deferred with date (not blocking v5.x-solid)

| Item | ADR/source | Date |
|---|---|---|
| Real git pre-commit/pre-push install (structural close for ALL matcher residuals) | ADR-0010 staged → needs ADR stub | **stub this cycle; build by 2026-07-15** |
| ADR-0019 AGENTS.md-primary execution (the inversion, scaffold side, parity collapse) | ADR-0019 | 2026-07-15 |
| ADR-0021 eval-harness (the recurring "real unlock"; gates I5, v6 question) | ADR-0021 | 2026-07-31 |
| ADR-0020 lintel-state MCP server | ADR-0020 | 2026-08-15 |
| H17 pack provenance + H18 plugin pinning (public-launch tier) + append-only audit sink | ADR-0010 staged | 2026-08-31 |
| Full-surface description→trigger sweep + aggressive-language dial-back | ADR-0014 follow-ups | 2026-07-31 |
| Per-CLI command-stub generator (Gemini/Cursor/Codex `skills_native`) | craft synthesis | with ADR-0019 |
| JSTACK env-alias removal | aliases.yaml:8 | **2026-06-28** |
| match→skill-router alias (08-29) · context-budgetwatch (09-10) · 44 aliases + post-grace v5 sweep + dual-accept removal | aliases.yaml, ADR-0005/0009/0011 | 2026-09-12 → removal sweep 2026-12-12 |
| I7 Subtraction-Bias data-modeling exception ADR · J9 jsonl-vs-OTel · J10 plan-mode | syntheses | 2026-08-31 or cut |
| v6 shrink-to-kernel / packs-as-product decision | battletest verdict | decision point: after eval-harness ships |
| **Operator actions:** remove 4 manual hook entries + li-doctor proof-of-life (~10 min, closes double-fire) · vault-sink personal re-enable · li-migrate other repos (by 09-12) · m-2 YAGNI call · T0 voice calibration · real-engagement dogfood (post-launch proof) · marketplace (post MS legal) | ADR-0008, working-state | first session after landing |

### §3-C — Dormant-by-decision (correct, re-affirmed) / cut

Brief-forge envelope construction · granularity calibration writes · jobs auto-spawn · 19
module warn-hooks — all stay dormant per ADR-0008 with activation conditions; B7 makes every
point-of-sale doc say so. Cut: basic-memory index (condition stated), `--keep-runs` YAGNI,
context-save machinery stays (wired-unproven acceptable for an explicit operator command —
gains a roundtrip test in B7).

## §4 — Remediation waves (BUILD)

| Wave | Content | Est. |
|---|---|---|
| 0 | B1+B2 — land 713388d + propagate deletions + ADR-0013 + truthful CHANGELOG + atomic commits, suite green committed | ~50k |
| 1 | B3 — security closures + negative tests | ~45k |
| 2 | B4 — footer/state class + regression tests | ~45k |
| 3 | B5 — Windows/portability floor | ~60k |
| 4 | B6 — docs truth sweep | ~70k |
| 5 | B7 — mechanism honesty | ~55k |
| 6 | B8 — release close, M1/M2/M4 gates, hygiene | ~40k |
| 7 | L-007 independent review (real diff, adversarial) → fixes → ship gate → PR | ~60k |

Single-writer rule: the dead v5.3 session must NOT be resumed while BUILD runs.
