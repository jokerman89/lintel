# Meta-infra discipline — gates that activate when you edit Lintel itself

**Last updated:** 2026-05-29 (v4.0 Phase 1)
**Status:** Concept doc — referenced by `skills/cycle/SKILL.md` (mode preset), `skills/sense/SKILL.md` (Step 0c), `bin/li-compat-audit`, `tests/shape/_README.md`, `.claude/engineering/evolution/_TEMPLATE.md`, `docs/migrations/_INDEX.md`

> Lintel is scaffolding. Changes to scaffolding ripple to every downstream cycle on every pack on every operator's machine. A skill rename breaks every workflow that referenced the old name. A frontmatter contract change breaks every skill that didn't update. A `_default` field change shifts behavior for every pack that didn't override. Meta-infra discipline is the **set of four mandatory gates that fire when changes touch scaffolding**, plus the mode envelope that makes them visible to the operator before BUILD starts.

## The problem

Editing Lintel-the-harness is qualitatively different from editing a project that uses Lintel:

- A project change affects the project. A Lintel change affects every project.
- A project bug surfaces in the next cycle. A Lintel bug surfaces in the next *thousand* cycles.
- A project review needs domain context. A Lintel review needs structural-impact context.
- A project ship gate verifies the change works. A Lintel ship gate must verify the change works **and** doesn't break anything that already worked.

Without meta-infra discipline, the operator on a Lintel edit gets the same lightweight REVIEW as a project bug fix. That is asymmetric to the blast radius.

## The model

```
SENSE Step 0c detects scaffolding paths in cwd diff
    │
    ├── meta-infra mode auto-recommended
    ▼
DEFINE writes Gate M1 structure-changes/<date>-<slug>.md
    │  (what changed, backward-compat, migration, forward-compat, verification, rollback)
    ▼
PLAN includes Gate M2 + M3 + M4 as explicit tasks
    │
    ▼
BUILD edits the scaffolding
    │
    ▼
REVIEW runs Gate M2 (bin/li-compat-audit) + Gate M3 (shape-tests)
    │  M2: 4-question GREEN/YELLOW/RED sweep → .claude/engineering/compat-audits/
    │  M3: 8 shape-tests via tests/runner/run-all.sh --shape-only
    ▼
SHIP blocked if M2=RED (without explicit override) or M3=FAIL
    │
    ▼
CAPTURE runs Gate M4 (future-operator clarity)
       updates docs/migrations/_INDEX.md if a migration ships
```

The four gates are mandatory inside meta-infra mode and absent in every other mode.

## The four gates

### Gate M1 — Structure-impact assessment (DEFINE)

**Trigger:** SENSE auto-detected scaffolding paths in diff, OR operator chose `--mode meta-infra`.

**Action:** Before merging the design, the operator writes a `.claude/engineering/evolution/<date>-<slug>.md` entry using `_TEMPLATE.md`. Required sections:

- **What changed:** specific files, lines, and fields
- **Backward-compat:** will existing workflows still function?
- **Migration path:** if no, what must downstream consumers do?
- **Forward-compat:** does the new shape leave room for known v4.x phases?
- **Verification:** how will REVIEW confirm the change holds?
- **Rollback:** if SHIP discovers a regression, what reverts?

**Output:** `.claude/engineering/evolution/<date>-<slug>.md`

**Why DEFINE and not PLAN:** if the structure change is wrong-shaped, the plan written against it will be wrong too. M1 forces the operator to think about ripple before tasks get cheap.

### Gate M2 — Compatibility audit (REVIEW)

**Trigger:** any cycle in meta-infra mode. Operator runs `bin/li-compat-audit` (or the orchestrator does it automatically during REVIEW).

**Action:** mechanical sweep across four questions:

1. **Frontmatter contracts** — did `REQUIRED_SKILL_FIELDS` or `REQUIRED_AGENT_FIELDS` change?
2. **Renames/moves** — were any skills, agents, or hooks renamed/relocated?
3. **New defaults** — did any existing field get a new default that changes behavior?
4. **Shared helpers** — did any signature in `lib/*.sh` change?

**Output:** `.claude/engineering/compat-audits/<date>-<slug>.md` with verdict:
- **GREEN** — no contract changes
- **YELLOW** — additive changes, backward-compatible
- **RED** — breaking changes, downstream must migrate

RED requires either: (a) a deprecated_aliases entry covering the rename, (b) a documented migration in `docs/migrations/_INDEX.md`, or (c) explicit operator override in the audit doc.

**Why mechanical and not LLM:** at v4.0 the contract surface is well-defined. A grep-based audit catches every actual change, never misses, never hallucinates. LLM review is reserved for the rationale, not the detection.

### Gate M3 — Shape-tests (REVIEW)

**Trigger:** any cycle in meta-infra mode. Operator runs `bash tests/runner/run-all.sh --shape-only` (or the orchestrator does it).

**Action:** 8 shape-tests run as a block. Each asserts a structural invariant. Any FAIL blocks SHIP. The current 8:

1. **workflow-root-has-navigation** — every `workflow_root: true` skill declares a navigation block
2. **brief-forge-handoffs-canonical** — no legacy `brief_forge:` field; only `brief_forge_handoffs:`
3. **frontmatter-lint-all** — every skill has required fields (`name`, `layer`, `description`, `color`, `tools`, `voice`, `cli_support`); every agent has required fields (`name`, `category`, `description`, `color`, `tools`, `voice`, `cli_support`)
4. **agents-categorized** — every `agents/<category>/<agent>.md` declares matching `category:`
5. **deprecated-aliases-resolve** — every `deprecated_aliases:` entry maps to a real new-name skill
6. **catalog-regenerates-clean** — CATALOG.md regenerates without diff (idempotent)
7. **pack-resolver-fallbacks** — 9 failure scenarios pass
8. **schema-versioned-contracts** — every contract JSON in `lib/` + `packs/` declares `schema_version`

**Output:** stdout PASS/FAIL summary; failures audited to `${LINTEL_HOME}/audit/shape-tests.jsonl`.

**Why shape-tests and not unit-tests:** shape-tests assert invariants that hold across the whole repo. A unit test verifies one function; a shape-test verifies that the repo's shape is still legal. Both exist; M3 is specifically the shape layer.

### Gate M4 — Future-operator clarity (CAPTURE)

**Trigger:** every cycle in meta-infra mode that reaches CAPTURE.

**Action:** CAPTURE writes a recap that a future operator (or future-you, six months from now) can use cold. Required surfaces:

- Every migration that future operators need to run → appended to `docs/migrations/_INDEX.md`
- Every new convention introduced → recorded in the cycle's CAPTURE doc with a pointer
- Every deprecated path with grace window → recorded in CAPTURE doc and migrations index

**Output:** updated `docs/migrations/_INDEX.md`; cycle CAPTURE doc.

**Why CAPTURE and not REVIEW:** REVIEW verifies the change works. CAPTURE verifies the change is teachable. Both matter, but M4 specifically is about transmission to the next operator.

## The mode envelope

`meta-infra` mode in `skills/cycle/SKILL.md`:

```yaml
meta-infra:
  phases: ALL_8  # heavier REVIEW + CAPTURE
  audience: operator + future-operator
  voice_tier: internal
  compliance: scaffolding-only  # skip customer-facing gates; activate Gates M1-M4
  cap_soft: 600k
  cap_hard: 900k
  gates_active: [M1, M2, M3, M4]
  use_when: change touches skills/, agents/, hooks/, bin/_*.sh, install/, docs/architecture.md, lib/, packs/, core templates
  detection: auto-detected by SENSE Step 0c
```

The cap (600k/900k) is heavier than `internal-tool` (25-50k) because meta-infra cycles run M1-M4 in addition to standard REVIEW. The operator can override with `--mode <other>` if the change is content-only (e.g., editing a concept doc) or test-only.

## Detection (SENSE Step 0c)

`skills/sense/SKILL.md` Step 0c runs a path-glob on the cwd diff:

```bash
meta_paths_changed=$(git diff --name-only HEAD 2>/dev/null \
  | grep -cE '^(skills|agents|hooks|bin|lib|packs|install)/|^LAYERS\.md$|^bin/_.*\.sh$' || echo 0)
```

Plus signal from the operator's prompt:

```bash
echo "$prompt_text" | grep -qiE "skill|agent|hook|pack|scaffold|lintel itself|meta-infra|li-bin|install/" && operator_signal=1
```

If either is positive, SENSE surfaces:

```
⚙ Meta-infra mode detected
   Diff touches: <list of scaffolding paths>
   Recommendation: --mode meta-infra (activates Gates M1-M4)
   Override: --mode <other> if change is content-only or test-only
   Cap: 600k soft / 900k hard
```

SENSE never blocks. The operator either accepts the recommendation or explicitly overrides.

## What activates meta-infra, what doesn't

**Activates:**
- Edits under `skills/<any>/SKILL.md` (workflow contracts)
- Edits under `agents/<category>/<agent>.md` (agent contracts)
- Edits under `hooks/shared/` or `hooks/<workflow>/` (cycle plumbing)
- Edits under `bin/_*.sh` (sourced helpers)
- Edits under `install/` (setup scripts)
- Edits under `lib/` (shared utilities)
- Edits under `packs/_default/pack.yaml` (neutral skeleton)
- Edits to `docs/architecture.md` (layer model)
- Edits to core templates (anything under `templates/` referenced by workflow_root skills)

**Does not activate:**
- Edits under `docs/` (documentation; no contract change)
- Edits under `tests/` only (test-only changes; verified by running the tests themselves)
- Edits under `packs/<non-default>/pack.yaml` (per-pack content)
- Project-scoped state under `.claude/runtime/`

For "edits-under-tests only" the operator can still opt in via `--mode meta-infra` if the test change reflects a shifted contract; SENSE just doesn't auto-recommend it.

## Override semantics

Every gate ships with explicit override. Per operator stance:

> "Every gate ships with override + audit. No paternalism. Defense through transparency, not blocking."

- **M1 override:** structure-changes entry can document "no compat impact — content-only" with reasoning
- **M2 override:** RED verdict overridden in the audit doc itself with explicit operator note
- **M3 override:** `--skip-shape-test <name>` flag with audit entry; CI blocks override on `main`
- **M4 override:** CAPTURE may declare "no migration required" — verified by future-operator on next read

Overrides audit to `${LINTEL_HOME}/audit/meta-infra-overrides.jsonl` so the trail survives.

## Why this matters

The cost of breaking Lintel-the-harness scales with adoption. At one operator, a break is annoying. At ten operators across three packs, a break is a coordination problem. Meta-infra discipline is the **mechanism that absorbs scaling cost upfront** — heavier per-cycle work, lighter cumulative regression.

The four gates are not bureaucratic. M1 forces structural thinking before tasks get cheap. M2 mechanically catches contract drift. M3 mechanically catches shape drift. M4 forces transmission to the next operator. Together they convert "I'll remember to check" into "the cycle checked."

## Integration points

**Reads:**
- `git diff --name-only HEAD` (SENSE Step 0c)
- Operator's last message (SENSE Step 0c heuristic)
- `.claude/engineering/evolution/_TEMPLATE.md` (M1)
- `tests/shape/*.sh` (M3)

**Writes:**
- `.claude/runtime/state/00-state.md` (`meta_infra_detected: true`)
- `.claude/engineering/evolution/<date>-<slug>.md` (M1)
- `.claude/engineering/compat-audits/<date>-<slug>.md` (M2)
- `docs/migrations/_INDEX.md` (M4 if migration ships)
- `${LINTEL_HOME}/audit/meta-infra-overrides.jsonl` (override trail)
- `${LINTEL_HOME}/audit/shape-tests.jsonl` (M3 failures)

**Triggers:**
- `bin/li-compat-audit` (M2 mechanical sweep)
- `bash tests/runner/run-all.sh --shape-only` (M3)

## Anti-patterns

- **Editing scaffolding outside meta-infra mode** — gates exist for a reason; opt out explicitly
- **Filing M1 after the fact** — the entry exists to shape the design, not to document a done thing
- **Treating M2 RED as a blocker only** — RED is information; override is allowed with operator note
- **Skipping M3 on local cycles** — shape-tests are cheap; CI runs them anyway; failures are easier to fix when small
- **Skipping M4 because "operator-only change"** — every change is read by a future operator; CAPTURE is the transmission
- **Adding new gate without structure-changes entry** — the gate itself is a contract change
