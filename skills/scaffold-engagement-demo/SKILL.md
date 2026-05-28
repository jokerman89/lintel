---
name: li-scaffold-engagement-demo
layer: ms-team
v1_alias: [li-scaffold-customer-demo]
description: Initialize a customer-demo repo — sample data, script, slides, recording config, voice gates.
color: green
tools: Read, Write, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /scaffold-engagement-demo

Sets up a new customer-demo repo with the right structure: sanitized sample data, presentation script (trailblazer-voiced sections gated), slide outline, recording config, and pre-wired compliance + voice gates so it can't accidentally ship un-voice-checked.

Use for CAIP-SE customer engagements where the demo material needs to be reusable + auditable.

## When to use

- New customer engagement starting; need a demo workspace
- Productizing an existing one-off demo into a repeatable template
- Onboarding a new SE — give them a known-good demo scaffold to learn from

## When NOT to use

- One-off throwaway demo (5-min internal) — overkill
- Demo material already lives in a customer's own repo — scaffold theirs, not ours

## Inputs

- Required `--name <slug>` — kebab-case repo name (e.g. `azure-arc-hybrid-demo`)
- Optional `--path <dir>` — where to create the repo (default: cwd / `<name>`)
- Optional `--template <type>` — `data-flow | ai-feature | governance | infra` (default: data-flow)
- Optional `--target-audience <text>` — primary audience description (e.g. "mid-market public sector, IT leadership")

## Workflow

1. **Create repo structure:**
   ```
   <name>/
     README.md                   # internal overview, NOT shippable to customer
     CLAUDE.md                   # repo-level instructions (Boris template)
     .gitignore
     LICENSE                     # MIT or operator's choice
     demo/
       script.md                 # trailblazer-voice presentation script (DRAFT)
       slides/
         outline.md              # slide-by-slide structure
       sample-data/
         README.md               # what the data is, sanitization rules
         seed.sql                # sanitized seed data (placeholders)
       recording/
         config.yaml             # recording setup (resolution, regions, captions)
         takes/.gitkeep
     deliverables/
       handout-DRAFT.md          # customer takeaway (gated by /rais-customer-voice-check)
       follow-up-email-DRAFT.md  # post-demo email (gated)
     compliance/
       data-class.md             # MS Business Data class declaration
       provenance.yaml           # /provenance-track records land here
   ```
2. **Populate CLAUDE.md.** From `scaffolding/01-foundation/CLAUDE.md.template`, with project-specific frozen zones (recordings/takes/ contains potential customer audio — Layer 2 gate).
3. **Template-specific seeding.** Based on `--template`:
   - `data-flow`: sample-data has source-table + destination-table fixtures
   - `ai-feature`: pre-wires /onerai-submit-draft target + /rais-impact-assessment cross-ref
   - `governance`: pre-wires /onecs-check full-checklist call
   - `infra`: includes terraform/bicep stub directory
4. **Pre-wire compliance gates.** Create `compliance/data-class.md` skeleton. Add a pre-commit-hook reference (handled in Phase 5 hook setup).
5. **Pre-wire voice gates.** Mark `demo/script.md` + all `*-DRAFT.md` files with frontmatter `voice: trailblazer, status: requires-customer-voice-check`. Add to `.gitignore` an entry preventing `*-FINAL.md` artifacts without a passed `/rais-customer-voice-check`.
6. **Git init.** Initialize repo, set up `.gitignore`, first commit "chore: scaffold customer-demo via lintel".
7. **Report next steps.**

## Report format

```
Scaffold customer-demo: azure-arc-hybrid-demo

Path: /e/Workspace/azure-arc-hybrid-demo
Template: data-flow
Target audience: mid-market public sector, IT leadership

## Created
- Repo structure: 7 directories, 9 starter files
- CLAUDE.md populated from foundation template
- Compliance pre-wiring: data-class.md skeleton, provenance.yaml empty
- Voice pre-wiring: 3 DRAFT files gated for /rais-customer-voice-check

## Git
- git init'd, first commit ad8f...

## Next steps
1. Edit demo/sample-data/seed.sql — fill with sanitized realistic data
2. Edit demo/script.md (DRAFT) — write narrative with mode tags
3. Run /rais-customer-voice-check on script when ready
4. Edit deliverables/handout-DRAFT.md (trailblazer-voiced)
5. /onecs-check before sharing externally
6. /provenance-track each artifact before customer delivery
```

## Compliance integration

- Pre-wires Layer 2 gates: data-class declaration required, compliance checklist scaffolded, voice gates on customer-facing artifacts.
- Sample data path enforces sanitization rule (sanitization rules surface in sample-data/README.md).
- Hooks for `customer-data-block` (Phase 5) added to pre-commit reference list.

## Voice tier note

`voice: internal`. The skill itself is engineering-internal — it produces a scaffold. The SCAFFOLD CONTAINS trailblazer-voice templates that operator fills + gates.

## Failure modes

- **Path exists + not empty:** ask whether to merge into existing or pick new path.
- **Template name not recognized:** list valid templates, exit.
- **git not available:** create files but skip git init, surface manual git init command.
- **CLAUDE.md template missing:** fall back to inline minimal template, warn.

## Examples

**Data-flow demo:**
```
> /scaffold-engagement-demo --name azure-arc-hybrid-demo --template data-flow
✓ Scaffolded. Next: fill sample-data/seed.sql + /rais-customer-voice-check the script.
```

**AI-feature demo with audience:**
```
> /scaffold-engagement-demo --name copilot-for-legal --template ai-feature --target-audience "legal-tech CIOs"
✓ Scaffolded with /onerai-submit-draft + /rais-impact-assessment cross-refs pre-wired.
```

## See also

- `/scaffold-internal-tool` — when target is internal tooling, not customer demo
- `/scaffold-mvp` — for productizing into an MVP
- `/rais-customer-voice-check` — gates the trailblazer-voice DRAFT files
- `/demo-deliverable-gen` — generates the customer takeaway after demo
- `scaffolding/01-foundation/CLAUDE.md.template` — source for the project CLAUDE.md
