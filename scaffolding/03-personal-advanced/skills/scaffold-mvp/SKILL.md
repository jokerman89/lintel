---
name: jstack-scaffold-mvp
description: Initialize a product-MVP repo — full compliance + voice + RAI + deploy wiring.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /scaffold-mvp

Initializes a product-grade MVP repo with the full JStack treatment: compliance hooks, RAI assessment placeholders, voice gates on customer-facing surfaces, deploy targets stubbed, eval suite skeleton. Heavier than `/scaffold-internal-tool`, more product-ready than `/scaffold-customer-demo`.

Use when the thing being built is intended to ship to real users, not just demo to them.

## When to use

- Greenfield product / feature MVP
- Pre-launch initiative with budget + timeline
- Spin-off from a successful demo into a productized version
- Operator promotion of an internal-tool to product-status

## When NOT to use

- Customer demo (one-time) — `/scaffold-customer-demo`
- Internal utility — `/scaffold-internal-tool`
- Existing repo — this is greenfield; adding to existing is a refactor

## Inputs

- Required `--name <slug>` — product/feature slug
- Required `--target-users <text>` — who's the product for
- Optional `--path <dir>` — where to create (default: cwd / `<name>`)
- Optional `--stack <text>` — tech stack (default: ts + vite + supabase per current MS-internal patterns)
- Optional `--has-ai <yes|no>` — pre-wires AI-specific scaffolding (RAI files, eval suite) if yes (default: yes)
- Optional `--deploy <staging,prod>` — pre-wire deploy targets via /setup-deploy stubs

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
       fixtures/      # sanitized only — Layer 2 rule
     compliance/
       data-class.md
       provenance.yaml
       sensitive-use-DRAFT.md      # via /sensitive-use-report
       rai-impact-DRAFT.md         # via /rai-impact-assessment (if --has-ai)
       onerai-DRAFT.md             # if --has-ai
       dpia-DRAFT.md               # if processes personal data
       transparency-note-DRAFT.md  # via /transparency-doc-gen
     eval/                         # if --has-ai
       suite/
         README.md                 # eval set construction methodology
         golden/                   # known-good fixtures
         adversarial/              # known-failure fixtures
       runs/.gitkeep
     deploy/
       targets.yaml                # /setup-deploy populates
     docs/
       design/
         INDEX.md                  # /office-hours docs land here
       adr/                        # architectural decisions
       guides/                     # customer-facing (voice-gated)
     .github/workflows/
       ci.yml
       compliance-check.yml        # runs /compliance-gate in CI
     CHANGELOG.md
   ```
2. **CLAUDE.md.** Full Boris template with frozen zones for `compliance/*-FINAL.md` (never overwrite finalized review artifacts) and `eval/suite/golden/` (golden set is signed off, edits gated).
3. **AI-specific seeding (if `--has-ai yes`):**
   - Pre-create `compliance/rai-impact-DRAFT.md`, `compliance/sensitive-use-DRAFT.md`, `compliance/onerai-DRAFT.md` as stubs to be filled via the respective skills.
   - Pre-create `eval/suite/README.md` with eval methodology guidance + 12-cell voice rubric reference if customer-facing.
4. **Compliance pre-wiring:**
   - `compliance/data-class.md` template
   - `compliance/provenance.yaml` empty
   - `.github/workflows/compliance-check.yml` runs `/compliance-gate --strict` on PRs
5. **Voice pre-wiring** (if customer-facing surface detected via `--target-users`):
   - `docs/guides/` flagged as voice-gated zone
   - `transparency-note-DRAFT.md` stub
6. **Deploy stub.** If `--deploy` provided: pre-fill `deploy/targets.yaml` with the named targets (operator runs `/setup-deploy` to validate).
7. **Git init + first commit.**
8. **Report.**

## Report format

```
Scaffold MVP: case-analysis-ai

Path: /e/Workspace/case-analysis-ai
Target users: Swedish legal-tech end users (consumers + SMB)
Stack: ts + vite + supabase
Has AI: yes
Deploy targets: staging, prod (stub written, run /setup-deploy to validate)

## Created
- Full repo structure: 15 directories, 22 starter files
- CLAUDE.md populated with frozen-zones for compliance + eval/golden
- AI compliance pre-wiring:
  - compliance/sensitive-use-DRAFT.md (run /sensitive-use-report to fill)
  - compliance/rai-impact-DRAFT.md (run /rai-impact-assessment to fill)
  - compliance/onerai-DRAFT.md (run /onerai-prep when above are done)
  - compliance/dpia-DRAFT.md (run /dpia-prep — likely required for legal-tech)
  - compliance/transparency-note-DRAFT.md (customer-facing, voice-gated)
- eval/suite/README.md with methodology + 12-cell rubric reference
- .github/workflows/compliance-check.yml — runs /compliance-gate on PRs

## Next steps (suggested order)
1. /office-hours to draft the design doc (lands in docs/design/)
2. /sensitive-use-report --feature case-analysis-ai
3. /rai-impact-assessment --feature case-analysis-ai --sensitive-use-report ...
4. /onerai-prep --feature case-analysis-ai
5. /dpia-prep --system case-analysis-ai
6. /setup-deploy --check (validate stub)
7. /transparency-doc-gen for customer disclosure
8. First feature implementation; then /qa + /review + /ship
```

## Compliance integration

- Pre-wires ALL relevant compliance gates as DRAFT stubs ready for the corresponding skills.
- `.github/workflows/compliance-check.yml` enforces compliance-gate on every PR (CI-level enforcement, not just operator discipline).
- Eval suite directory with 12-cell rubric reference for AI features.
- Frozen zones in CLAUDE.md prevent accidental overwrite of finalized review artifacts.

## Voice tier note

`voice: internal`. Skill produces engineering scaffold. The scaffold CONTAINS gated voice-bearing artifact stubs.

## Failure modes

- **`--has-ai yes` but stack doesn't typically include AI:** ask via AskUserQuestion — operator may have non-obvious AI use.
- **`--target-users` empty:** require it — every product has users; saying so shapes voice + RAI scope.
- **Path exists:** ask whether to merge or pick new path.
- **Deploy targets specified but `/setup-deploy` not runnable:** stub files written, skill surfaces manual setup steps.
- **Stack unrecognized:** fall back to ts + minimal, warn.

## Examples

**AI MVP with full pipeline:**
```
> /scaffold-mvp --name case-analysis-ai --target-users "Swedish legal-tech consumers + SMB" --has-ai yes --deploy staging,prod
[Creates 15 dirs, 22 files, 5 compliance stubs, eval skeleton, deploy stubs]
✓ Scaffolded. Suggested next: /office-hours.
```

**Non-AI MVP:**
```
> /scaffold-mvp --name billing-portal --target-users "mid-market SMB CFOs" --has-ai no --deploy staging
[Skips AI-specific files]
✓ Scaffolded. Lighter compliance surface — DPIA only if personal data.
```

## See also

- `/scaffold-customer-demo` — lighter, demo-focused
- `/scaffold-internal-tool` — lightest, no customer surface
- `/office-hours` — first design doc lands in docs/design/
- All Phase 3 RAI skills — fill the DRAFT stubs this scaffold creates
- `/setup-deploy` — validate the deploy stubs
