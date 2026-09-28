# Cold-Executor Prompt: native client parity, increment 1 (GitHub Copilot)

This file is a SELF-CONTAINED prompt. A fresh AI session reading only this prompt + the linked
spec.md + plan.md should be able to re-execute or extend this work without prior context.

## Context

Lintel is a company-neutral session harness: canonical Markdown skills and agents, Bash hooks and
standard-library Python tools. It ships natively to Claude Code as a plugin. On GitHub Copilot it
used to ship 518-byte pointer skills that asked the model to read large canonical files, which models
skipped. Live probes on Copilot CLI 1.0.87/1.0.89 proved three things:

- Copilot injects whole skill bodies (63 KB tested).
- Plugin hooks receive `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA`/`CLAUDE_PROJECT_DIR`, with the
  plugin root as cwd.
- Top-level `additionalContext`, `modifiedTransformedPrompt` and JSON `permissionDecision: deny`
  take effect.

This increment makes Copilot run Lintel like Claude Code does:

- complete generated native skills (all 96) and agents (69 canonical plus 3 roles);
- the nine auto-registered hooks through a plugin-owned host adapter, with repository hooks as an
  explicit opt-in;
- honest registry facts, docs and migration notes;
- live CLI acceptance evidence;
- delivery to `main`.

Increment 2 (Codex, Cursor, Claude) follows in a separate cycle, using `research/` and the same
generator and adapter core.

## Constraints

- **Must respect:** [spec.md](spec.md) §Constraints; ADR-0038; the plan's work-package boundaries
  and the exact contracts in spec.md.
- **Must NOT:** hand-edit generated files, change canonical skill or agent bodies, add packages,
  enable repository hooks by default, record environment values, rewrite Git history, or push
  `main` directly.
- **Compliance:** active pack `_default` (advisory; no compliance hooks declared).
- **Voice tier:** internal.
- **Publishing identity:** only `jokerman89` (L-053). Never read or probe credentials.

## Acceptance criteria (verify)

- [ ] R1-R23 in spec.md, each with the evidence named in plan.md's leaf acceptance lines. In
      particular:
      - R21: both-routes tests 2.5.d and 3.4.e;
      - R22: `bin/li-run` journeys 1.5.b;
      - R23: the SHIP "identity gate" control before any push, and the SHIP "fresh version-collision check" control.
- [ ] `python bin/li-copilot.py check --target . --source .`, `python bin/li-catalog.py --check`
      and `bash bin/li-wiki-gen --check` pass on the final tree.
- [ ] `evidence/copilot-acceptance.md` shows every live check in plan 6.2 and 6.3, with the
      measurement gates.
- [ ] The PR's CI is green on Ubuntu, macOS and Windows. The PR is merged to `main`
      (operator-authorized, 2026-09-28).

## Deliverables

- Code: `bin/li-copilot.py`, `bin/li-run`, `hooks/adapters/**`, `hooks/shared/_input.sh`.
- Generated: `.github/skills/**`, `.github/agents/**`, `.github/plugin/hooks.json`, instructions,
  catalog and wiki.
- Tests named in plan phases 1-5.
- Docs, registry, CHANGELOG, migration guide and manifests (phase 5).
- The evidence file and registry observations (phase 6).

## How to re-execute

1. Read spec.md, then plan.md. Check `.claude/runtime/state/00-state.md` (cycle
   `native-client-parity-20260928`) and `.claude/plans/native-client-parity/build-log.md` for the
   package pointer.
2. Resume with `/li-resume`, or with `/li-cycle --from BUILD` using this work map
   (`.claude/plans/native-client-parity/work.json`).
3. Execute the packages in order P1 → P6. Each gets one implementer and one dedicated two-stage
   review (spec, then quality) by a separate reviewer.
4. Verify without edits (`/li-verify`), then `/li-review`, `/li-ship` and `/li-capture`.
5. Increment 2 is not built from this plan. Start a new cycle at DEFINE: reconcile `research/*.md`,
   then DISCOVER and PLAN P7-P9 with their own reviews. Amend ADR-0038 before BUILD.

## What you DON'T need to know

- The probe transcripts. Their facts are summarized in design.md's Evidence table and in the
  session research notes.
- The full conversation history that produced this plan.

This prompt is the IRREDUCIBLE handoff. Everything needed is here or in the linked files.
