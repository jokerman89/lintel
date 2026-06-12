# ADR-0010: security hardening — controls at the action boundary, fail-toward-safe

**Status:** Accepted (2026-06-12)
**Decided by:** operator (battletest — security persona, "är en tjänst inte försvarbar då måste vi … överkomma")
**Implements:** docs/audit/2026-06-12-battletest-synthesis.md (Wave S: K1-K4, H8, H16)

## Context

The security battletest live-confirmed (in /tmp sandboxes) that every Lintel "control" was
advisory by construction: the block hooks matched the agent's *command string* with a `^git`
anchor (bypassed by `git -C`, abs paths, `&&` chains) and scanned `git diff --cached` only
(bypassed by `git commit -am`, which stages after the PreToolUse hook); the BLOCK secret set
missed modern token formats (`sk-proj-`, `github_pat_`, `AIza`, `sk_live_`); the vault sink
wrote session content OUTSIDE the repo where no hook scanned it, with prose-only privacy; the
audit log was newline-injectable (forge/hide records); inline override left no audit; and
`li-scaffold` spliced a repo/dir name into GNU `sed s///e` → operator-priv RCE.

## Decision

Close the demonstrated exploits now; stage the structural ones (real git-hook install, plugin
pinning, pack provenance) with their own ADRs.

1. **K1 — kill the sed RCE.** `li-scaffold` renders the CLAUDE.md template via pure-bash literal
   parameter expansion, never `sed s///` (whose `e` flag executes shell).
2. **K2 — broaden the matcher + scan the worktree.** Both block hooks match `git … (commit|push)`
   by word boundary (catches `-C`, abs paths, `&&`/`cd` chains) and scan staged **union**
   unstaged-tracked changes (covers `commit -am`). The deeper fix — installing the scanner as a
   real `core.hooksPath` pre-commit/pre-push gate that fires regardless of how the agent phrased
   the command — is staged as a follow-up; this pass closes the proven bypasses.
3. **K3 — modern token formats.** tier1 secret set gains github_pat_, sk-proj-, AIza (Google),
   sk_live_/sk_test_ (Stripe), glpat- (GitLab), ASIA (AWS STS), broadened openai/anthropic.
4. **K4 — programmatic vault scan.** CAPTURE Step 7b runs `scan_secrets all` + `scan_customer`
   over the rendered note BEFORE the external write and aborts the export on any hit (warn,
   never sanitize-and-ship, never fail CAPTURE) — the one place customer PII could leave the
   repo unscanned.
5. **H8 — honest override + tamper-resistant audit.** Override is checked BEFORE the matcher and
   honors env OR the command-string token, so an override always audits. `_audit_escape` now
   escapes CR/LF (one JSON object per line is an invariant readers depend on); `state_append`
   strips CR/LF from values (no forged ledger blocks).
6. **H16 — fail toward safe.** Block hooks treat empty-content as "nothing to block" only after
   the matcher fires; the union scan and broadened matcher shrink the fail-open surface. Full
   fail-closed-on-parse-miss for BLOCK tier rides with the real-git-hook follow-up.

## Consequences

- The four live-verified bypasses (sed RCE, `git -C`/`&&` matcher evasion, `commit -am`
  worktree gap, modern-token miss) are closed; `tests/integration/security-controls-fire.sh`
  asserts each stays closed.
- Override is no longer a silent hole; the audit trail resists newline forgery.
- Staged (own ADRs, dated): real git pre-commit/pre-push install (supersedes the command-string
  match entirely), plugin content-pinning on update (H18), pack provenance + posture-change
  warnings (H17), append-only/tamper-evident audit sink.
- Accepted residual: the command-string match is still defeatable by an adversary who controls
  the exact invocation AND avoids the override token AND the worktree scan (e.g. a bare-tree
  `git hash-object`/plumbing write) — which is why the real git-hook install is the committed
  next step, not a maybe. Documented, not hidden.
