# ADR-0008: the activation contract — shipped means fires, tested means behaved

**Status:** Accepted (2026-06-12)
**Decided by:** operator — approved the fit-audit P0 recommendation, 2026-06-12
**Implements:** .claude/engineering/audits/2026-06-12-fable5-fit-audit.md (P0 tracks 1-2)

## Context

The Fable 5 fit audit measured wired-vs-shipped: only ~3 of ~14 mechanism families ever fired
in real sessions. session-digest (ADR-0002) was never registered (manual merge nobody did, and
the snippet pointed at a wrong path); memory-budget-warn was never installed; the cycle state
machine had written ZERO entries across weeks of real cycles; profile.yaml/packs never existed
so every session silently ran the `_default` fallback; the shape tests asserted prose presence,
green forever. One root cause five ways: **activation was a manual step or a prose obligation,
and nothing verified behavior.**

## Decision

1. **Plugin hooks auto-register.** `hooks/hooks.json` ships with the plugin (Claude Code
   registers it on install — schema verified against the installed binary): session-digest
   (SessionStart: startup|resume|clear), the 4 safety hooks (PreToolUse), memory-budget-warn
   (PostToolUse Edit|Write). Shell-string form (`bash "${CLAUDE_PLUGIN_ROOT}/..."`) so Windows
   resolves bash via Claude Code's Git Bash discovery — exec-form `bash` needs bash.exe on the
   raw process PATH, which plain Windows lacks. Module warn-hooks remain opt-in. No manual
   merges in the activation path. The settings snippet remains only for non-plugin installs
   (path fixed). Auto-registered hooks source ONLY their own tree / `~/.lintel` — never
   repo-supplied code (they now run in every repo, including untrusted ones). The review also
   surfaced that the two block hooks exited 1 — which Claude Code treats as non-blocking — so
   "COMMIT BLOCKED" printed while the commit proceeded; they now exit 2 (the actual blocking
   code). **Firing on this platform is verified by li-doctor's proof-of-life check (a
   session_digest audit record), not assumed — final confirmation lands on the first session
   after the plugin updates to 5.0.0.**
2. **Identity is seeded, not fallen back to.** install.sh seeds `~/.lintel/profile.yaml` +
   `packs/active-pack` (`_default`) when missing. The fallback stays as a safety net, not as
   the permanent silent reality. li-doctor reports hook drift (installed vs shipped) and
   verifies the auto-registration manifest.
3. **The state ledger costs one line.** `lib/state.sh: state_append <PHASE> <STATUS> [next=X]
   [k=v...]` + `state_last [field]`. All 9 phase skills + cycle + resume now call the helper
   instead of hand-appending YAML blocks (source chain falls back to `~/.lintel/lib/state.sh`
   so the ledger works in consumer repos, not just this checkout; the footer skips
   non-canonical CYCLE/RESUME ledger entries when resolving position). If a discipline costs more than one command, it gets
   skipped under momentum — the audit proved it.
4. **Behavior over prose in tests.** `tests/integration/session-leaves-traces.sh` runs the
   real machinery hermetically and asserts the traces: digest envelope + audit record, ledger
   write/read/footer roundtrip, budget hook firing, hooks.json validity + every registered
   script present and 100755 in the index. New mechanisms must land with a behavior test, not
   only a prose-presence shape test.
5. Version: all 6 CLI manifests bump to 5.0.0 (the v5 layout shipped under a 4.9.0 manifest).

## Consequences

- A fresh `/plugin install` gets digest + safety + budget hooks live with zero setup. THIS
  operator must remove the 4 manual hook entries from `~/.claude/settings.json` to avoid
  double-fire (migration row in docs/migrations/_INDEX.md).
- The footer/resume read a ledger that actually exists from now on.
- Known dormant-by-decision (NOT activated here, awaiting evidence of need): brief-forge
  envelope construction, granularity calibration writes, jobs auto-spawn, 20+ module
  warn-hooks. They stay shipped-but-opt-in; activating them is a per-mechanism decision with
  its own behavior test, not a blanket switch-on.
- The prose-asserting shape tests stay as drift guards but no longer count as proof of life.
