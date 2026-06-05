# Todo — session-digest auto-load (v4.8, implementation)

**Initiative:** Implement the approved design
([docs/design/claude-md-capability-and-memory-surfacing.md](../docs/design/claude-md-capability-and-memory-surfacing.md)):
a SessionStart digest hook that auto-loads Lintel's snowball (pack/mode/role + recent lessons +
open jobs + recent ADRs), plus capability/state surfacing in CLAUDE.md + the template.

## Plan
- [x] ADR-0002 — session-digest auto-load decision
- [x] `hooks/shared/session-digest/` — HOOK.md + run.sh (≤~400-token digest; ~200 chars actual; graceful degrade)
- [x] Test run.sh: valid JSON via both jq + no-jq fallback; degrades to nothing in a fresh repo
- [x] Root CLAUDE.md: `## Skill routing`, `## Where state lives`, structured-comment-format, ritual note (hook + non-hook-CLI fallback)
- [x] `CLAUDE.md.template`: same sections (generic)
- [x] SessionStart wiring: `hooks/claude-code/session-digest.settings.json` + install.sh note
- [x] `bin/li-doctor`: session-digest present + wired check
- [x] Verify: bash -n clean; shape 19/19, unit 29/0; audit-helper contract satisfied (uses audit_log)

## Review

Built the approved design. The session-digest SessionStart hook auto-injects a ~200-char digest
(pack/mode/role/compliance + recent lessons L-004..L-006 + recent ADRs 0001/0002), validated as
JSON with and without jq, fail-open + graceful in a fresh repo. CLAUDE.md (root + template) now
surfaces skill routing, the state map, and structured-comments; the session-start ritual is the
non-hook-CLI fallback. li-doctor flags an un-wired digest. Caught + fixed a real contract break:
the hook initially wrote audit inline, violating the v4.0 audit-via-helper shape test — now routes
through `audit_log`.

**Deferred (design doc open questions):** pack-overridable digest budget; keyword-relevant (vs
recency) lesson selection; unifying ADR location with deeplex's `docs/06-decisions/`.
