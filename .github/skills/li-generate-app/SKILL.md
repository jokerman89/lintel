---
name: li-generate-app
description: Use when a resolved frontend design needs a Next.js, Vite-React or SvelteKit application scaffold that preserves the selected stack and dependency choices.
---

> **Lintel on GitHub Copilot.** Generated from `skills/generate-app/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/generate-app/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/generate-app/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the `generate-app` skill for full-app scaffolds, preserving the design-director versus rendering-engine separation.

## What this skill does

Reads `frontend-design-spec.json` (from `/li-frontend-design` orchestrator output) → generates a **working repo skeleton** the operator can `npm install && npm run dev`. Spans single-page-app territory beyond what generate-web's `single-file` or `nextjs-scaffold` variants cover.

**Why separate from generate-web** (M-2 resolution): generate-web targets pitch-artifacts (single-file landing + Next.js scaffold). generate-app targets production-grade app skeletons (multi-route, state, API stubs, deploy-config). Same rendering-engine family, different scope.

L-001-discipline: skill body is the contract (what scaffolds get generated). Agent at invocation produces actual file-content. Don't pre-bake "the best React structure" — let agent decide based on stack + brief.

Use the [shared direct design contract](../../../skills/design-dna/references/design-contract.md)
for validation and renderer arguments. Respect existing project technology; no
library, framework migration, dependency installation or deployment is implicit.

## When to use

- "Customer wants a full Next.js app POC, not just a landing page"
- Vite-React production-grade starter with motion + shader wired up
- SvelteKit multi-route app skeleton
- Engagement-deliverable that operator will commit to a customer repo

## When NOT to use

- Single-file landing page → use `/li-generate-web --variant single-file`
- Next.js scaffold (basic 1-3 route) → use `/li-generate-web --variant nextjs-scaffold`
- Pure backend (no frontend) → not in this skill's scope
- Operator already has a repo + just needs design integration → use `/li-frontend-design` solo + manual integration

## Inputs

- Required `--from-frontend-design <run-dir>` — frontend-design output dir (must contain `frontend-design-spec.json`)
- Required `--stack <next-app|vite-react|svelte-kit>` — framework choice
- Optional `--brief <path>` — additional content brief beyond what frontend-design captured
- Optional `--routes <comma-list>` — explicit route list (default: home + about + contact)
- Optional `--with-api-stubs` — generate api/ folder with placeholder routes
- Optional `--with-auth-stubs` — placeholder auth (next-auth / clerk-stub / lucia-stub)
- Required `--out <path>` — explicitly owned repository-relative application output directory
- Optional `--customer-share` — triggers compliance-gate
- Optional `--review` — explicitly request the shared post-generation review;
  this does not add a second reviewer or waive required review when omitted

## Workflow

### Step 1 — Parse + validate

```bash
from_frontend_design="${FROM_FRONTEND_DESIGN:-}"
stack="${STACK:-}"
brief="${BRIEF:-}"
routes="${ROUTES:-home,about,contact}"
out_dir="${OUT:?select an owned repository-relative output directory}"

[ -z "$from_frontend_design" ] && { echo "Required: --from-frontend-design <dir>"; exit 2; }
[ -f "$from_frontend_design/frontend-design-spec.json" ] || { echo "frontend-design-spec.json not found"; exit 2; }
[ -z "$stack" ] && { echo "Required: --stack <next-app|vite-react|svelte-kit>"; exit 2; }

```
Reject unknown, duplicate or conflicting options before output. Validate the
selected design and project manifests before scaffolding; do not create directories
merely because two required strings are nonempty.
Follow [owned source and output selection](../../../skills/design-dna/references/design-contract.md#owned-source-and-output-selection).
Missing or unwritable output fails visibly; no current-directory, personal-home
or neighboring-run fallback is permitted. Preserve original source/manifest bytes
and require explicit replacement authorization before touching existing output.

### Step 2 — Schema-version handshake (M-1 + M-5)

Call `design_contract.load_design` using the external prepared P05 context and
explicit P07 configuration. Consume `renderer_args` rather than reimplementing
variant/stack mapping. Legacy readable inputs need explicit resolution; missing
policy/assets and profile drift block, without rebinding.
The shared reader enforces the existing `schema_version: 1` and
`source: frontend-design` handshake as well as the complete bound design.

### Step 2b — Stack-guidance pass (ADR-0015 — retrieval before rendering)

```bash
case "$stack" in
  next-app)   dna_stack=nextjs ;;
  vite-react) dna_stack=react ;;
  svelte-kit) dna_stack=svelte ;;
  *)          echo "Unsupported stack '$stack'; preserve the project technology" >&2; exit 2 ;;
esac
python3 "${LINTEL_SKILLS_DIR:-skills}/design-dna/scripts/search.py" "<routes/features keywords>" --stack "$dna_stack"
```

Apply the returned Do/Don't/Severity rules while scaffolding. python3 absent → Read
`design-dna/data/stacks/$dna_stack.csv` (same root) directly.

### Step 3 — Stack-specific scaffold

**For `--stack next-app`:**

1. Use an already available `create-next-app` template or an explicitly selected
   owned template, including an actual verified configured template path.
   Record which source was used. A missing selected template/dependency is a
   reported boundary, not an automatic download, home scan, tool fallback or
   reason to replace a project. A different scaffold needs explicit selection.
2. Generate dir structure:
   ```
   app/
   ├── layout.tsx       — wires up LenisProvider + fonts + global CSS
   ├── page.tsx         — home route, applies visual_thesis
   ├── about/page.tsx
   ├── contact/page.tsx
   └── globals.css      — typography + layout_grammar tokens
   components/
   ├── ui/              — shadcn primitives (init via skill body)
   ├── motion/          — GSAP-tied components
   └── hero/            — uses shader-snippets if shader != null
   lib/
   ├── motion.ts        — Lenis init + GSAP setup
   └── typography.ts    — variable-axes utilities
   public/
   └── (operator-licensed fonts dropped here if Pangram etc)
   package.json         — gsap + lenis + (paper-shaders if applicable) + shadcn + (Aceternity reference)
   next.config.js
   tsconfig.json
   tailwind.config.ts   — fontFamily with stacks from typography.json
   ```
   This is a library-enabled example, not a required dependency tree. For no-motion
   or CSS-only output omit Lenis/GSAP providers, motion modules and dependencies;
   for no-shader omit the canvas/GPU module. Use only libraries actually selected
   with project-compatible source/version/license evidence.

**For `--stack vite-react`:**

1. Use Vite + React-TS template
2. Similar structure adapted to Vite paradigm
3. React-Router for multi-route
4. Apply same typography + motion + shader integration

**For `--stack svelte-kit`:**

1. Use SvelteKit + TypeScript template
2. Similar structure, Svelte syntax for components
3. SvelteKit routes-based file routing

### Step 4 — Apply design-spec to generated files

For each file generated, apply transforms from `frontend-design-spec.json`:

- **layout.tsx / +layout.svelte:** apply the selected authorized font-loading
  strategy and font-family classes. If `interaction_signature.scroll_smoothing`
  is true, integrate the actual bound motion runtime in a framework-compatible
  way. `LenisProvider` is only an example when Lenis was explicitly selected;
  do not introduce it for a different runtime or native scrolling.
- **page.tsx / +page.svelte:** apply `visual_thesis` to hero copy + structure
- **tailwind.config:** map `typography.size_scale.scale` + `typography.line_heights` + `layout_grammar.max_width` to Tailwind tokens
- **Motion:** none means no animation imports; CSS-only uses CSS, not a JS library
  added for media queries. Library mode implements only selected effects with cleanup
  and reduced-motion handling.
- **Shader:** emit a GPU component only for an active non-`none` shader decision;
  `shader: null` and `visual_thesis: none` produce no shader dependency.

### Step 5 — Generate `package.json`

Retain the project's manifest/lockfile and package manager. For a new authorized
scaffold, select exact compatible framework/tool releases from their official
sources; record version/license and rationale in the shared binding. Write only
the dependencies the chosen design needs, plus the selected framework/build tools.
No guessed `latest`, stale version ranges or universal GSAP/Lenis/Tailwind bundle.
Use actual framework scripts and preserve the lockfile. Run installation only
inside the separately authorized scope after a manifest change or missing-tool
failure; never silently skip the failed build and claim smoke-test success.

### Step 6 — Operator-instructions emit

```
GENERATE-APP COMPLETE
══════════════════════════════════════════════════════════════════

Stack:              <next-app | vite-react | svelte-kit>
Output dir:         $out_dir

Files generated:
  - $route_count routes
  - $component_count components
  - typography + motion + (shader) wired up

Next steps:
  cd $out_dir
  npm install
  npm run dev
  open http://localhost:3000

Operator-licensed items (per frontend-design-spec.json):
  - Pangram font? See: $out_dir/public/README-fonts.md
  - Any selected runtime/editor/asset terms? See the source-bound dependency notes.
```

### Step 7 — Required checks and one review owner

Run the existing mechanical validator on actual produced HTML using the verified
profile; source JSX is not rendered HTML. Retain its errors and warnings, then
run the declared build smoke-test. A failure remains a failure.

Follow [review ownership and reuse](../../../skills/frontend-design-review/references/built-review.md#review-ownership-and-reuse).
In an enclosing frontend-design run, return artifact paths, current input identity
and observed checks to that owner for its Step 7 review. For standalone use,
the current app workflow owns the same `frontend-design-review` handoff.
`--review` requests that review, not an extra DesignSystemAuditor pass after
WebExperienceCritic. Reuse only applicable current P05/QA and independent evidence.

Resolve actual `voice.gates_active` separately from compliance hooks when the
brief/profile requires voice review. No configured voice gate is different from
an unavailable required one; missing mandatory observations keep delivery blocked.
An otherwise valid generated artifact can be handed to its owner for outstanding
review without regenerating it or treating the unperformed review as passed.

## Voice tier behavior

`voice: mixed`. Default `internal`. `--customer-share` triggers compliance-gate + voice-gate.

## Reusable patterns

Follow the [reusable pattern consumer contract](../../../skills/pattern/references/consumer-contract.md).
Before scaffolding, `verify-lock` the lock handed over by the design step against the current
context, then check the spec's `pattern_context` with `validate_visual` against it (never a
stored report). Loading through `design_contract` with `--pattern-lock` does both. A stale context,
mismatched setting or unusable selection blocks instead of being corrected here. Apply the
projected values; generate-app still makes no design decisions. When the runtime reports no
patterns, scaffolding is unchanged.

## Status protocol

- **DONE** — app output and all applicable required build, inspection and review controls are verified
- **DONE_WITH_CONCERNS** — required controls are satisfied; advisory concerns remain explicit
- **BLOCKED** — invalid design, failed build, or any required failed/unverified control; hand valid produced output to the selected owner for an outstanding review
- **NEEDS_CONTEXT** — stack-choice missing or frontend-design-spec absent

## Pause-points

- Schema-version handshake fail: BLOCKED hard
- Build smoke-test fail: surface diagnostic + offer retry
- Customer-share + voice-gate fail: BLOCKED for operator-review

## Integration

**Reads:**
- `<from-frontend-design>/frontend-design-spec.json` (mandatory)
- Explicitly selected owned or verified configured template source for the selected stack
- The exact selected pattern/lock references carried by the bound design
- The unchanged verified P07 profile reference and its actual voice requirements;
  do not read a personal profile YAML directly

**Writes:**
- `<out_dir>/` — full repo skeleton
- Audit-log: `.claude/runtime/audit/generate-app-runs.jsonl`

**Calls into:**
- `/li-frontend-design-review` through the single selected owner; the retained
  WebExperienceCritic/DesignSystemAuditor methods are not two default passes
- the active pack's actual voice requirements (`resolve_pack_field voice.gates_active`;
  none by default, independent of compliance hooks)
- `/li-compliance-gate` (if customer-share)

**Boundary with frontend-* family (L-002):**

generate-app is the **rendering-engine** — produces files. frontend-design is the **design-director** — produces spec. generate-app does NOT make design-decisions; it READS them from spec + scaffolds accordingly. Same role as generate-web but larger-scope output.

| Concern | generate-web | generate-app |
|---|---|---|
| Output | single .html OR Next.js scaffold (basic) | Full vite/next/svelte project skeleton |
| Use case | Pitch artifact, landing page | Production-grade app POC |
| Routes | 1-3 | Multi (configurable) |
| Build-system | Embedded or npm-init | Full package.json + npm-build |
| API stubs | No | Optional via --with-api-stubs |
| Auth stubs | No | Optional via --with-auth-stubs |

## Anti-patterns

- **Making design-decisions in generate-app** — wrong layer. Read them from frontend-design-spec.json.
- **Letting an unpinned install choose design dependencies** — retain project
  versions/lockfile and record exact sourced choices before an authorized change.
- **Generating without schema-version handshake** — M-1 + M-5 violation.
- **Skipping prefers-reduced-motion handling** — accessibility-fail. Mandatory.
- **Inventing routes not in `--routes` flag** — operator decides scope.

## Failure recovery

- Schema-version handshake fail: BLOCKED + diagnostic
- Dependency/build failure: retain the exact diagnostic and unverified artifact
  outcome; skipping a smoke test does not make the requested app runnable.
- Output missing/unwritable: BLOCKED with the actual error and selected path;
  retain partial owned output and never retry at an unselected destination
- Stack-template missing or cli scaffold tool unavailable: BLOCKED with install-instruction

## Recommended next steps after invocation

- `cd $out_dir && npm install && npm run dev` — operator validates locally
- `/li-frontend-design-review $out_dir` — Phase A2 6-dimension audit (if not already auto-run)
- Operator commits to customer-repo if customer-share
- Pair with `/li-compliance-gate` for final ship-gate
