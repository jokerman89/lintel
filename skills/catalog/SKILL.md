---
name: catalog
layer: foundation
description: Auto-generate skills/CATALOG.md från frontmatter-parse. Discoverability-fix per Cohort 2 item 1.6 (REPLACED — aldrig hand-curerad).
color: yellow
tools: Read, Write, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `catalog` skill — auto-generates `skills/CATALOG.md` från frontmatter-parse av alla `skills/*/SKILL.md`. Discoverability-fix utan hand-maintenance-burden.

## What this skill does

113 skills + 73 agents = discoverability-problem. Backlog 1.6 ville hand-curerad catalog men det rostar fortare än skillsen. **REPLACED:** auto-generated från `find skills/ -name SKILL.md` + frontmatter-parse, regenerated i CI per push.

Outputs:
- `skills/CATALOG.md` (commit:ad, läses av operator OCH framtida skills som vill se "all available")
- Organiserad per `layer:` (foundation / ms-team / sdl / ...) sen alfabetiskt

Pairs med `/li:usage-log --report` för usage-overlay (trending vs cold).

## When to use

- **Auto från CI** — `.github/workflows/catalog.yml` calls denna efter every push till main → CATALOG.md uppdateras automatisk
- **Solo regenerate** — `/li:catalog --regenerate` (innan PR-stäng om operator vill se färsk catalog)
- **Search** — `/li:catalog --search <keyword>` filter:ar på name/description match
- **Family view** — `/li:catalog --family generate` listar alla generate-* skills

## When NOT to use

- Hand-edit `CATALOG.md` direkt — denna skriver-över. Edit frontmatter istället, regenerate.
- Single-skill-lookup — `find skills/<name>/SKILL.md` är snabbare för one-off

## Workflow

### Step 1 — Scan + parse

```bash
SKILLS_DIR="${REPO_ROOT}/skills"
find "$SKILLS_DIR" -name 'SKILL.md' -not -path '*/.*' | while read -r f; do
  name=$(grep -m1 '^name:' "$f" | sed 's/^name:[ ]*//' | tr -d '\r')
  layer=$(grep -m1 '^layer:' "$f" | sed 's/^layer:[ ]*//' | tr -d '\r')
  description=$(grep -m1 '^description:' "$f" | sed 's/^description:[ ]*//' | tr -d '\r')
  echo "$layer|$name|$description"
done | sort
```

### Step 2 — Group by layer

Order: foundation → ms-team → sdl → personal-advanced → other

### Step 3 — Render CATALOG.md

```markdown
# Lintel Skill Catalog

Auto-generated från frontmatter. Regenerated per push via `.github/workflows/catalog.yml`. Manuell edit overrides — kör `/li:catalog --regenerate` om operator-edit needed.

Total: N skills

## Foundation layer (N skills)

| Skill | Description |
|---|---|
| `/li:catalog` | Auto-generate skills/CATALOG.md ... |
| `/li:lessons-surface` | Surface relevanta lessons.md-entries ... |
| ... | ... |

## MS-team layer (N skills)

| Skill | Description |
|---|---|
| `/li:az-tldr` | Comprehensive on-demand rundown ... |
| ... | ... |

## SDL layer (N skills)

| Skill | Description |
|---|---|
...
```

### Step 4 — Optional `--trends` overlay

Om `--trends`:
- Read `~/.lintel/audit/usage-*.jsonl` past 30 days
- For each skill: prepend usage-count
- Sort each layer-section by usage descending
- Add 🔥 emoji för top-5, ❄️ för bottom-N (rust candidates)

### Step 5 — Write to disk

`$REPO_ROOT/skills/CATALOG.md`. If CI mode (no operator), commit automatic. If solo mode, surface diff + ask för commit.

## Voice tier behavior

`voice: internal`. Catalog är operator-internal navigation aid.

## Status protocol

- **DONE** — CATALOG.md regenerated, N skills listed
- **DONE_WITH_CONCERNS** — regenerated men some skills had missing frontmatter (now caught by verify.sh --frontmatter post-Cohort-1)
- **BLOCKED** — skills/ dir not present or unreadable
- **NEEDS_CONTEXT** — `--search` mode utan keyword

## Hop-in support

YES — solo-regenerate any time + CI-automation.

## Integration

**Reads:**
- `skills/*/SKILL.md` (frontmatter parse)
- `~/.lintel/audit/usage-*.jsonl` (optional, för `--trends`)

**Writes:**
- `skills/CATALOG.md` (canonical output)

**Consumed by:**
- Operator (navigation aid)
- `/li:sense` (discovery before planning)
- `/li:plan` (knowing-what-exists)
- New CAIP-SE teammates (onboarding)

## Anti-patterns

- **Hand-editing CATALOG.md** — denna skriver-över. Always edit source frontmatter.
- **Catalog-as-source-of-truth** — frontmatter är canonical. Catalog är view.
- **CATALOG.md > 500 rader** — om så händer, paginate per layer eller add sub-catalogs per family.

## Failure recovery

- Skill missing required frontmatter: skip + warn (verify.sh --frontmatter fångar detta separately)
- Duplicate skill names: surface conflict + use folder name as canonical
- Glob pattern fails (no skills found): write empty CATALOG.md with placeholder

## Recommended next steps after invocation

- Operator browses CATALOG.md för discoverability
- Vid frequent rust-candidates: consider archive eller deprecate
- Vid `--trends` overlay: feed into `/li:maintenance` för cleanup-decisions

## CI integration

`.github/workflows/catalog.yml` (separat fil):

```yaml
name: catalog-regenerate
on: { push: { branches: [main] } }
jobs:
  regenerate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash skills/catalog/bin/regenerate.sh
      - name: Commit if diff
        run: |
          git config user.name "lintel-catalog-bot"
          git config user.email "bot@lintel.local"
          git add skills/CATALOG.md
          git diff --staged --quiet || git commit -m "chore(catalog): auto-regenerate"
          git push
```

Bin-script implementation lives at `skills/catalog/bin/regenerate.sh` — created separately at impl-time.
