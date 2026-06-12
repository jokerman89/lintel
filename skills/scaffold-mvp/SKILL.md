---
name: scaffold-mvp
layer: foundation
description: Initialize a product-MVP repo — full structure + pack-driven compliance/voice/deploy wiring.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /scaffold-mvp

Initializes a product-grade MVP repo with the full Lintel treatment: structure, eval-suite skeleton, deploy targets stubbed, and **pack-driven** compliance + voice wiring (whatever the active pack declares; nothing in `_default`). Heavier than `/scaffold-internal-tool`.

Use when the thing being built is intended to ship to real users, not just demo to them.

## When to use

- Greenfield product / feature MVP
- Pre-launch initiative with budget + timeline
- Spin-off from a successful prototype into a productized version
- Operator promotion of an internal-tool to product-status

## When NOT to use

- Internal utility — `/scaffold-internal-tool`
- Existing repo — this is greenfield; adding to existing is a refactor

## Inputs

- Required `--name <slug>` — product/feature slug
- Required `--target-users <text>` — who's the product for
- Optional `--path <dir>` — where to create (default: cwd / `<name>`)
- Optional `--stack <text>` — tech stack (default: ts + vite + supabase)
- Optional `--has-ai <yes|no>` — pre-wires AI-specific scaffolding (eval suite + the active pack's AI-compliance stubs) if yes (default: yes)
- Optional `--deploy <staging,prod>` — pre-wire deploy target stubs

## Workflow

1. **Create extensive structure:**
   ```
   <name>/
     README.md
     CLAUDE.md
     LICENSE
     .gitignore
     .editorconfig
     src/
       index.ts (or stack-appropriate entry)
       lib/
       components/  (if UI)
       api/         (if backend)
     tests/
       unit/
       e2e/
       fixtures/      # sanitized only — privacy baseline
     compliance/
       data-class.md
       provenance.yaml
       # + the active pack's compliance-gate DRAFT stubs (none in _default)
     eval/                         # if --has-ai
       suite/
         README.md                 # eval set construction methodology
         golden/                   # known-good fixtures
         adversarial/              # known-failure fixtures
       runs/.gitkeep
     deploy/
       targets.yaml                # deploy targets (pack CI/deploy gate validates)
     docs/
       design/
         INDEX.md                  # /office-hours docs land here
       adr/                        # architectural decisions
       guides/                     # customer-facing (voice-gated if pack sets a tier)
     .github/workflows/
       ci.yml
       compliance-check.yml        # runs the active pack's compliance gates in CI
     CHANGELOG.md
   ```
2. **CLAUDE.md.** Full template with frozen zones for `compliance/*-FINAL.md` (never overwrite finalized review artifacts) and `eval/suite/golden/` (golden set is signed off, edits gated).
3. **AI-specific seeding (if `--has-ai yes`):**
   - Pre-create the active pack's AI-compliance DRAFT stubs (`resolve_pack_field compliance.hooks`; none in `_default`) to be filled via the pack's compliance skills.
   - Pre-create `eval/suite/README.md` with eval methodology guidance + the active pack's voice rubric reference if customer-facing.
4. **Compliance pre-wiring:**
   - `compliance/data-class.md` template
   - `compliance/provenance.yaml` empty
   - `.github/workflows/compliance-check.yml` runs the active pack's compliance gates on PRs (no-op if `_default`)
5. **Voice pre-wiring** (if customer-facing surface detected via `--target-users` AND the active pack declares a voice tier):
   - `docs/guides/` flagged as voice-gated zone
6. **Deploy stub.** If `--deploy` provided: pre-fill `deploy/targets.yaml` with the named targets (the pack's CI/deploy gate validates).
7. **Git init + first commit.**
8. **Report.**

## Report format

```
Scaffold MVP: case-analysis-ai

Path: /e/Workspace/case-analysis-ai
Target users: legal-tech end users (consumers + SMB)
Stack: ts + vite + supabase
Has AI: yes
Active pack: _default (no compliance/voice gates) | <company-pack>
Deploy targets: staging, prod (stub written)

## Created
- Full repo structure: 15 directories, 22 starter files
- CLAUDE.md populated with frozen-zones for compliance + eval/golden
- AI eval skeleton: eval/suite/{golden,adversarial}/
- Compliance pre-wiring: the active pack's gates (none in _default)
- .github/workflows/compliance-check.yml — runs the active pack's compliance gates on PRs

## Next steps (suggested order)
1. /office-hours to draft the design doc (lands in docs/design/)
2. Fill the active pack's compliance DRAFT stubs, if any (/li:compliance-gate lists them)
3. First feature implementation; then /qa + /review + /ship
```

## Compliance integration

- Pre-wires the active pack's compliance gates as DRAFT stubs ready for the corresponding skills (none in `_default`).
- `.github/workflows/compliance-check.yml` runs `/li:compliance-gate` on every PR (CI-level enforcement; no-op when no compliance pack is active).
- Eval suite directory with the active pack's voice rubric reference for AI features.
- Frozen zones in CLAUDE.md prevent accidental overwrite of finalized review artifacts.

## Failure modes

- **`--has-ai yes` but stack doesn't typically include AI:** ask via AskUserQuestion — operator may have non-obvious AI use.
- **`--target-users` empty:** require it — every product has users; saying so shapes voice + compliance scope.
- **Path exists:** ask whether to merge or pick new path.
- **Stack unrecognized:** fall back to ts + minimal, warn.

## Examples

**AI MVP with full pipeline:**
```
> /scaffold-mvp --name case-analysis-ai --target-users "legal-tech consumers + SMB" --has-ai yes --deploy staging,prod
[Creates 15 dirs, 22 files, eval skeleton, deploy stubs, + active pack's compliance stubs]
✓ Scaffolded. Suggested next: /office-hours.
```

**Non-AI MVP:**
```
> /scaffold-mvp --name billing-portal --target-users "mid-market SMB CFOs" --has-ai no --deploy staging
[Skips AI-specific files]
✓ Scaffolded. Lighter compliance surface.
```

## See also

- `/scaffold-internal-tool` — lighter, no customer surface
- `/office-hours` — first design doc lands in docs/design/
- `/li:compliance-gate` — runs the active pack's compliance gates
- `/pack-switch` — activate a company pack for compliance/voice wiring
