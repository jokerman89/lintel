---
name: skillify
layer: foundation
description: Turn a recurring task or pattern into a new Lintel skill — scaffolds SKILL.md from TEMPLATE.
color: green
tools: Read, Write, Edit, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /skillify

Turn an authorized recurring task or selected `L-NNN` lesson into a useful skill draft,
using the existing `scaffolding/01-foundation/TEMPLATE-skill.md` from the trusted source.
The draft belongs to an explicitly owned path in the working target, not automatically
to Lintel's source bundle, a personal skill tree or a native discovery directory.

Drafting does not install, symlink, register or activate a skill. A bare canonical name
such as `regen-mocks` is distinct from a host wrapper such as `li-regen-mocks` or plugin
spelling `/li:regen-mocks`; do not silently strip or add a prefix.

## When to use

- A `/learn` entry tagged `skillify-candidate` is mature enough to formalize
- A repeating multi-step task has emerged in 3+ sessions
- Team-shared workflow needs a single command instead of step-by-step prose
- After a `/retro` flagged a workflow worth standardizing

## When NOT to use

- One-time task — overhead of skill authoring exceeds value
- Workflow that's still in flux — wait until shape stabilizes (3+ runs)
- Skill name conflicts with existing Lintel or upstream skill — resolve naming first

## Inputs

- Required: bare canonical name (kebab-case), one-line description and authorized target directory
- Optional `--from-lesson <id>` — read a `/learn` entry by id, use it as seed
- `--dir <subdir>` — explicit repository-relative draft directory; no implicit personal destination
- Optional `--voice <tier>` — declared voice tier (default: internal; project/pack constraints still apply)
- Optional `--cli <list>` — source declarations using the accepted registry; default empty/unknown, not claimed host support
- Optional `--tools <list>` — tools the skill needs (default: `Read, Bash`)

## Workflow

1. **Check scope and identity.** Select the trusted source and working target separately.
   Use the catalog name/alias query below, not a private-tree scan or second inventory.
   Inspect only explicitly selected project-local draft/registration paths for additional
   collisions. A catalog miss covers that source namespace, not every installed plugin.
2. **Read the existing template** and, only if requested, the exact `L-NNN` lesson from the
   target's documented memory file. A missing seed is an unresolved input, not invented history.
3. **Instantiate a valid opening header.** Fill name, layer, description, color, tools,
   voice and cli_support. Keep declarations distinct from host observation and permissions.
   Use proper YAML quoting for supplied text; do not interpolate it into executable code.
4. **Retain the method.** Turn the selected lesson into inputs, ordered steps, exclusions,
   expected output, failure/recovery behavior and at least two worked examples, including
   a negative case. Use actual available operations or explicit manual fallback. Leave
   unresolved logic marked TODO/DRAFT rather than promising it works. Query related names
   through the existing catalog and read only a genuinely selected reference.
5. **Write only the authorized new draft.** Recheck destination ownership/nonexistence
   immediately before the host's file-edit operation. Refuse overwrite; an existing draft
   needs explicit revision authority. Do not run activation, global installation or symlinks.
6. **Validate that exact file** with the existing validator below. Report its real scope,
   any invalid fields and remaining TODOs; inspect/test the method separately before adoption.

### Check name and destination

Set `skill_name` to the literal canonical name and `draft_relative` to the explicitly
authorized target-relative `.../SKILL.md`. This preflight performs no writes.

```bash
set -euo pipefail
source_root="${LINTEL_SOURCE_ROOT:?select the trusted Lintel source}"
repo="${LINTEL_REPO_ROOT:?select the working target}"
: "${skill_name:?supply a nonempty canonical name}"
: "${draft_relative:?supply the owned target-relative SKILL.md path}"
python_cmd="${python_cmd:-python3}"
metadata=$("$python_cmd" -B "$source_root/bin/li-catalog.py" \
  --json --kind=skill --name="$skill_name")
printf '%s' "$metadata" | "$python_cmd" -I -B -c '
import json, sys
result = json.load(sys.stdin)
if result["matched"]:
    for entry in result["entries"]:
        print("COLLISION: " + entry["id"] + " at " + entry["path"], file=sys.stderr)
    sys.exit(2)
'
if [[ ! "$skill_name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || [[ "$skill_name" == li-* ]]; then
  printf 'INVALID: use a bare canonical kebab-case name, not a host wrapper; no automatic rename\n' >&2
  exit 2
fi
"$python_cmd" -I -B - "$source_root/lib" "$repo" "$draft_relative" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from context_safety import checked_root, safe_path
try:
    draft = safe_path(checked_root(Path(sys.argv[2])), sys.argv[3])
    if draft.name != "SKILL.md" or draft.exists():
        raise ValueError("target must be a new owned SKILL.md; refusing overwrite")
except (OSError, ValueError) as error:
    print(f"INVALID destination: {error}", file=sys.stderr)
    raise SystemExit(2)
print(draft)
PY
```

This uses the accepted source identity/alias and path contracts, not a new parser.
It does not grant ownership or make a later edit atomic; the host must still honor
permissions and refuse a destination that appeared or changed before writing.

### Validate the exact draft

Set `draft` to the file actually written, not the template or a whole installation.

```bash
set -euo pipefail
: "${LINTEL_SOURCE_ROOT:?select the trusted source}"
: "${draft:?select the actual draft file}"
source "$LINTEL_SOURCE_ROOT/lib/frontmatter.sh"
if validate_lintel_frontmatter "$draft" skill; then
  printf 'DRAFT: opening frontmatter required fields present; method and semantic validation remain\n'
else
  result=$?
  printf 'INVALID draft: repair the reported frontmatter failures; no activation performed\n' >&2
  exit "$result"
fi
```

The shared check verifies the opening block and required field **presence**, including
`layer`. It does not certify YAML types, allowed values, name uniqueness, executable
behavior or host compatibility. Those require their actual source checks and review.
`install/verify.sh --frontmatter` scans an installation; an extra filename does not
turn it into this per-draft check. If the helper is unavailable, leave validation unrun.

## Report format

```
Skillify: regen-mocks

Path: <authorized target>/drafts/regen-mocks/SKILL.md
Voice: internal
CLI declarations: <supplied registry IDs, or empty/unknown>
Tools: <declared operations, not proof of available bindings>

## Frontmatter validation
Catalog name/alias collision check: <actual result and source>
Opening-block required-field check: <actual command, exit and diagnostics>
Semantic metadata/method checks: <actual evidence, or NOT RUN>

## Body status
<remaining TODOs, unresolved inputs, worked and negative examples>

## Next steps
Review/test the draft's actual method in an owned fixture.
Adoption/discovery is a separately authorized adapter action, not performed here.
```

## Failure modes

- **Name/alias collides or metadata query fails:** report the existing path or actual error,
  stop before writing. Do not auto-rename, drop an alias or replace failure with zero matches.
- **Template missing or corrupted:** report + exit. Do not silently generate without template.
- **Destination exists, escapes the target or is not owned:** refuse without changing it.
- **Frontmatter validation fails after drafting:** retain the owned draft as INVALID, with
  actual diagnostics; do not delete it, overwrite other work or advertise activation.
- **Lesson id not found:** report the missing input; use the real question channel if needed.

## Examples

**From a lesson:**
```
> /li:skillify --name regen-mocks --from-lesson L-042 --dir drafts/regen-mocks
[When that selected lesson exists and the target path is authorized]
Draft: drafts/regen-mocks/SKILL.md
Inputs: existing mock schema and explicit output directory.
Method: inspect the current generator, reproduce the drift, regenerate only owned mocks,
then compare the fixture and document failure recovery. Unknown tool bindings remain TODO.
Negative example: an absent schema stops before output; no empty "successful" mock set.
Validation: report the actual exact-file check; method not executed by this example.
```

**Inline:**
```
> /li:skillify --name standup-brief --voice mixed --dir drafts/standup-brief
Description: "Summarize explicitly supplied commits and approved issue data."
Draft preserves input citations and separates completed work from blockers.
No network query or customer-data export follows from authoring the draft.
> /li:skillify --name match --dir drafts/match
COLLISION: skill:skill-router; keep the retained alias. No file written.
```

## See also

- `TEMPLATE-skill.md` — the scaffold this skill uses
- `/learn` — produces skillify-candidate lessons
- `/health` — broader diagnostics when explicitly selected, not a substitute for exact-file validation
- `/retro` — surfaces skillify candidates from session activity
