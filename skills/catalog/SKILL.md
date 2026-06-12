---
name: catalog
layer: foundation
description: Auto-generate skills/CATALOG.md from a frontmatter parse. Discoverability fix per Cohort 2 item 1.6 (REPLACED — never hand-curated).
color: yellow
tools: Read, Write, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `catalog` skill — auto-generates `skills/CATALOG.md` from a frontmatter parse of all `skills/*/SKILL.md`. Discoverability fix without a hand-maintenance burden.

## What this skill does

113 skills + 73 agents = a discoverability problem. Backlog 1.6 wanted a hand-curated catalog, but that rusts faster than the skills. **REPLACED:** auto-generated from `find skills/ -name SKILL.md` + a frontmatter parse, regenerated in CI on every push.

Outputs:
- `skills/CATALOG.md` (committed, read by the operator AND by future skills that want to see "all available")
- Organized by `layer:` (foundation / personal-advanced / ...) then alphabetically

Pairs with `/li:usage-log --report` for a usage overlay (trending vs cold).

## When to use

- **Auto from CI** — `.github/workflows/catalog.yml` calls this after every push to main → CATALOG.md is updated automatically
- **Solo regenerate** — `/li:catalog --regenerate` (before closing a PR if the operator wants to see a fresh catalog)
- **Search** — `/li:catalog --search <keyword>` filters on name/description match
- **Family view** — `/li:catalog --family generate` lists all generate-* skills

## When NOT to use

- Hand-editing `CATALOG.md` directly — this overwrites it. Edit the frontmatter instead, then regenerate.
- Single-skill lookup — `find skills/<name>/SKILL.md` is faster for a one-off

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

Order: foundation → personal-advanced → power-user → other

### Step 3 — Render CATALOG.md

```markdown
# Lintel Skill Catalog

Auto-generated from frontmatter. Regenerated on every push via `.github/workflows/catalog.yml`. A manual edit overrides — run `/li:catalog --regenerate` if an operator edit is needed.

Total: N skills

## Foundation layer (N skills)

| Skill | Description |
|---|---|
| `/li:catalog` | Auto-generate skills/CATALOG.md ... |
| `/li:lessons-surface` | Surface relevant lessons.md entries ... |
| ... | ... |

## Personal-advanced layer (N skills)

| Skill | Description |
|---|---|
| `/li:office-hours` | Generate a design doc from a problem statement ... |
| ... | ... |
```

### Step 4 — Optional `--trends` overlay

If `--trends`:
- Read `~/.lintel/audit/usage-*.jsonl` past 30 days
- For each skill: prepend usage-count
- Sort each layer-section by usage descending
- Add 🔥 emoji for top-5, ❄️ for bottom-N (rust candidates)

### Step 5 — Write to disk

`$REPO_ROOT/skills/CATALOG.md`. If CI mode (no operator), commit automatically. If solo mode, surface the diff + ask before committing.

## Integration

**Reads:**
- `skills/*/SKILL.md` (frontmatter parse)
- `~/.lintel/audit/usage-*.jsonl` (optional, for `--trends`)

**Writes:**
- `skills/CATALOG.md` (canonical output)

**Consumed by:**
- Operator (navigation aid)
- `/li:sense` (discovery before planning)
- `/li:plan` (knowing-what-exists)
- New teammates (onboarding)

## Anti-patterns

- **Hand-editing CATALOG.md** — this overwrites it. Always edit the source frontmatter.
- **Catalog-as-source-of-truth** — frontmatter is canonical. The catalog is a view.
- **CATALOG.md > 500 lines** — if that happens, paginate per layer or add sub-catalogs per family.

## Failure recovery

- Skill missing required frontmatter: skip + warn (verify.sh --frontmatter catches this separately)
- Duplicate skill names: surface conflict + use folder name as canonical
- Glob pattern fails (no skills found): write empty CATALOG.md with placeholder

## Recommended next steps after invocation

- Operator browses CATALOG.md for discoverability
- On frequent rust candidates: consider archiving or deprecating
- On a `--trends` overlay: feed into `/li:maintenance` for cleanup decisions

## CI integration

`.github/workflows/catalog.yml` (separate file):

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
