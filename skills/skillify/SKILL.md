---
name: jstack-skillify
layer: foundation
description: Turn a recurring task or pattern into a new JStack skill — scaffolds SKILL.md from TEMPLATE.
color: green
tools: Read, Write, Edit, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /skillify

Promotes a recurring task into a first-class JStack skill. Reads the operator's description (or a `/learn` entry marked `skillify-candidate`), scaffolds a new `SKILL.md` following `TEMPLATE-skill.md`, places it in the right scaffolding layer, and validates frontmatter.

The output is NOT a deployed skill yet — operator iterates on the draft, then runs `/health` to validate before symlinking into `~/.claude/skills/` (or repo's `.claude/skills/`).

## When to use

- A `/learn` entry tagged `skillify-candidate` is mature enough to formalize
- A repeating multi-step task has emerged in 3+ sessions
- Team-shared workflow needs a single command instead of step-by-step prose
- After a `/retro` flagged a workflow worth standardizing

## When NOT to use

- One-time task — overhead of skill authoring exceeds value
- Workflow that's still in flux — wait until shape stabilizes (3+ runs)
- Skill name conflicts with existing JStack or upstream skill — resolve naming first

## Inputs

- Required: name (kebab-case) + one-line description
- Optional `--from-lesson <id>` — read a `/learn` entry by id, use it as seed
- Optional `--layer <01-foundation|02-compliance|03-personal-advanced|04-power-user>` — which scaffolding layer (default: 03-personal-advanced for new skills)
- Optional `--voice <internal|trailblazer|mixed>` — voice tier (default: internal)
- Optional `--cli <list>` — CLIs supported (default: `claude-code,codex`)
- Optional `--tools <list>` — tools the skill needs (default: `Read, Bash`)

## Workflow

1. **Name validation.** Check name doesn't conflict with existing skill (search scaffolding tree + `~/.claude/skills/`). Must start with `jstack-`. Kebab-case.
2. **Read template.** Load `scaffolding/01-foundation/TEMPLATE-skill.md`.
3. **Read seed (if `--from-lesson`).** Pull lesson body, source, type to use as seed material.
4. **Generate frontmatter.** Fill required fields per inputs + sensible defaults.
5. **Generate body.** Scaffold sections:
   - What this skill does — derived from description + seed
   - When to use / When NOT to use — placeholder bullets with TODO markers
   - Inputs — `TODO: declare flags`
   - Workflow — numbered placeholder steps (operator fills with real logic)
   - Report format — placeholder code block
   - Compliance integration — placeholder note
   - Voice tier note — auto-populated from --voice
   - Failure modes — placeholder bullets
   - Examples — placeholder
   - See also — auto-link related skills based on name similarity
6. **Write to layer.** `scaffolding/<layer>/skills/<name-without-jstack->/SKILL.md`.
7. **Validate frontmatter.** Run `verify.sh --frontmatter <new-file>` (or inline equivalent). Surface any errors.
8. **Report path + next steps.**

## Report format

```
Skillify: jstack-regen-mocks

Layer: 03-personal-advanced
Path: scaffolding/03-personal-advanced/skills/regen-mocks/SKILL.md
Voice: internal
CLI support: claude-code, codex
Tools: Read, Bash, Edit, Glob

## Frontmatter validation
✓ name format (kebab-case, jstack- prefix)
✓ description present, < 120 chars
✓ color valid (green)
✓ tools listed
✓ voice tier valid
✓ cli_support is array

## Body status
- Scaffold sections present with TODO markers
- Workflow steps placeholder — operator fills with concrete logic
- Examples placeholder — operator adds at least 2

## Next steps
1. Edit the SKILL.md to fill TODOs (workflow, examples)
2. Run /health to validate after edits
3. Symlink to ~/.claude/skills/regen-mocks/SKILL.md (or repo-local) to activate
4. Test in a new session
```

## Compliance integration

- New skill file goes through Layer 2 sanity-scan on save (paranoid: a skill spec might inadvertently include a secret pattern).
- Layer assignment: 01-foundation is RESERVED for stable skills — skillify defaults to 03-personal-advanced, requires explicit `--layer 01-foundation` to write there, and surfaces "are you sure?" gate.

## Voice tier note

`voice: internal`. Skill authoring is engineering-internal. The new skill's OUTPUT voice is determined by its own `voice:` frontmatter, not this skill's.

## Failure modes

- **Name collides:** report existing skill path, exit. Do not auto-rename.
- **Layer is 01-foundation but operator did not confirm:** AskUserQuestion gate — refuses by default.
- **Template missing or corrupted:** report + exit. Do not silently generate without template.
- **Frontmatter validation fails:** write file anyway BUT mark it INVALID in report. Operator must fix before activation.
- **Lesson id (`--from-lesson`) not found:** report + ask operator to supply lesson body inline.

## Examples

**From a lesson:**
```
> /skillify --name regen-mocks --from-lesson LESSON-042
[Reads lesson body, scaffolds SKILL.md]
✓ Skill draft at scaffolding/03-personal-advanced/skills/regen-mocks/SKILL.md
  Next: fill workflow + examples, then /health
```

**Inline:**
```
> /skillify --name standup-brief --voice mixed --cli claude-code,codex
[Description: "Generate a 3-bullet morning standup from yesterday's commits + open PRs"]
✓ Skill draft scaffolded. 12 TODO markers remain in body.
```

**Foundation-layer (rare):**
```
> /skillify --name custom-foundation-helper --layer 01-foundation
[AskUserQuestion: 01-foundation is reserved for stable skills. Confirm?]
[Operator: yes, with reason]
✓ Skill scaffolded in 01-foundation. Audit logged.
```

## See also

- `TEMPLATE-skill.md` — the scaffold this skill uses
- `/learn` — produces skillify-candidate lessons
- `/health` — validates a new skill draft
- `/retro` — surfaces skillify candidates from session activity
