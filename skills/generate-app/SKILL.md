---
name: generate-app
layer: foundation
description: Full-app scaffold-orchestrator. Reads frontend-design-spec.json + generates vite-react/next-app/svelte-kit project skeleton with motion/shader/typography wired up. Sister till generate-web — same family (rendering-engine), larger scope.
color: green
tools: Read, Write, Bash, Glob
voice: mixed
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: auto-pick-recommended
license_note: produces customer-bound output if --customer-share flag set
---

You are the `generate-app` orchestrator skill — full-app scaffold for v3.7 generate-* family (Fas B — resolves M-2 från /plan-eng-review per design-director vs rendering-engine separation).

## What this skill does

Reads `frontend-design-spec.json` (from `/li:frontend-design` orchestrator output) → generates a **working repo skeleton** the operator can `npm install && npm run dev`. Spans single-page-app territory beyond what generate-web's `single-file` eller `nextjs-scaffold`-variants cover.

**Why separate from generate-web** (M-2 resolution): generate-web targets pitch-artifacts (single-file landing + Next.js scaffold). generate-app targets production-grade app skeletons (multi-route, state, API stubs, deploy-config). Same rendering-engine family, different scope.

L-001-discipline: skill body är contract (what scaffolds get generated). Agent at invocation produces actual file-content. Don't pre-bake "the best React structure" — let agent decide based on stack + brief.

## When to use

- "Customer wants a full Next.js app POC, not just a landing page"
- Vite-React production-grade starter with motion + shader wired up
- SvelteKit multi-route app skeleton
- Engagement-deliverable that operator will commit to a customer repo

## When NOT to use

- Single-file landing page → use `/li:generate-web --variant single-file`
- Next.js scaffold (basic 1-3 route) → use `/li:generate-web --variant nextjs-scaffold`
- Pure backend (no frontend) → not in this skill's scope
- Operator already has a repo + just needs design integration → use `/li:frontend-design` solo + manual integration

## Inputs

- Required `--from-frontend-design <run-dir>` — frontend-design output dir (must contain `frontend-design-spec.json`)
- Required `--stack <next-app|vite-react|svelte-kit>` — framework choice
- Optional `--brief <path>` — additional content brief beyond what frontend-design captured
- Optional `--routes <comma-list>` — explicit route list (default: home + about + contact)
- Optional `--with-api-stubs` — generate api/ folder with placeholder routes
- Optional `--with-auth-stubs` — placeholder auth (next-auth / clerk-stub / lucia-stub)
- Optional `--out <path>` — output dir (default: `~/.lintel/generate-runs/<run-id>/app/`)
- Optional `--customer-share` — triggers compliance-gate

## Workflow

### Step 1 — Parse + validate

```bash
from_frontend_design="${FROM_FRONTEND_DESIGN:-}"
stack="${STACK:-}"
brief="${BRIEF:-}"
routes="${ROUTES:-home,about,contact}"
out_dir="${OUT:-$HOME/.lintel/generate-runs/$(date +%Y%m%d-%H%M%S)-${RANDOM}/app}"

[ -z "$from_frontend_design" ] && { echo "Required: --from-frontend-design <dir>"; exit 2; }
[ -f "$from_frontend_design/frontend-design-spec.json" ] || { echo "frontend-design-spec.json not found"; exit 2; }
[ -z "$stack" ] && { echo "Required: --stack <next-app|vite-react|svelte-kit>"; exit 2; }

mkdir -p "$out_dir"
```

### Step 2 — Schema-version handshake (M-1 + M-5)

```bash
spec="$from_frontend_design/frontend-design-spec.json"
sv=$(jq -r '.schema_version' "$spec")
source=$(jq -r '.source' "$spec")
[ "$sv" = "1" ] || { echo "Unsupported schema_version: $sv"; exit 1; }
[ "$source" = "frontend-design" ] || { echo "Wrong source: $source"; exit 1; }
```

### Step 3 — Stack-specific scaffold

**For `--stack next-app`:**

1. Use `create-next-app` template (or in-repo template at `~/.lintel/brand/web-templates/next-app/`)
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
   tailwind.config.ts   — fontFamily med stacks från typography.json
   ```

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

- **layout.tsx / +layout.svelte:** inject `<link>` tags from `typography.font_stacks[].loading_strategy`, wrap children with LenisProvider om `interaction_signature.scroll_smoothing`, set up fontFamily classNames
- **page.tsx / +page.svelte:** apply `visual_thesis` to hero copy + structure
- **tailwind.config:** map `typography.size_scale.scale` + `typography.line_heights` + `layout_grammar.max_width` to Tailwind tokens
- **components/motion/*.tsx:** GSAP setup with prefers-reduced-motion gating per `motion.perf_budget.fallback_for_prefers_reduced_motion`
- **components/hero/HeroShader.tsx:** om `shader != null` → emit Paper Shaders component eller OGL canvas-mount

### Step 5 — Generate `package.json`

```json
{
  "name": "<inferred-from-brief>",
  "version": "0.1.0",
  "dependencies": {
    "next": "^15.x" | "react": "^18.x" + "react-dom" | "svelte": "^4.x",
    "gsap": "^3.12.x",
    "@studio-freight/lenis": "^1.0.x",
    "@paper-design/shaders-react": "^0.x"  // only if shader.present
  },
  "devDependencies": {
    "typescript": "^5.x",
    "tailwindcss": "^3.x"
  },
  "scripts": {
    "dev": "next dev | vite | vite dev",
    "build": "next build | vite build | vite build",
    "start": "next start"
  }
}
```

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
  - GSAP Club plugins? See: $out_dir/README.md "Motion notes"
```

### Step 7 — 4-gate quality pipeline

Same as generate-web (per existing v3.5 pattern):
1. Build-test: `npm run build` smoke-test
2. WebExperienceCritic agent: layout/hierarchy/accessibility review
3. DesignSystemAuditor (Fas A2) optional: 6-dimension audit if `--review` flag
4. Voice-gate via the active pack's voice gate (`resolve_pack_field compliance.hooks`; none by default) om customer-share

## Voice tier behavior

`voice: mixed`. Default `internal`. `--customer-share` triggers compliance-gate + voice-gate.

## Status protocol

- **DONE** — app skeleton generated, npm install + npm run dev succeed in smoke-test
- **DONE_WITH_CONCERNS** — build succeeds but design-review yellow (om --review)
- **BLOCKED** — frontend-design-spec.json invalid schema, OR build fails, OR customer-share voice-fail
- **NEEDS_CONTEXT** — stack-choice missing eller frontend-design-spec absent

## Pause-points

- Schema-version handshake fail: BLOCKED hard
- Build smoke-test fail: surface diagnostic + offer retry
- Customer-share + voice-gate fail: BLOCKED för operator-review

## Hop-in support

YES — solo-invocable (given an existing frontend-design-spec.json).

## Integration

**Reads:**
- `<from-frontend-design>/frontend-design-spec.json` (mandatory)
- `~/.lintel/brand/web-templates/<stack>/` (templates if exist, else use cli scaffold tools)
- `~/.lintel/brand/design-patterns/<name>/` (om frontend-design ran with --pattern)
- `~/.lintel/profile.yaml` (mode → voice-tier)

**Writes:**
- `<out_dir>/` — full repo skeleton
- Audit-log: `~/.lintel/audit/generate-app-runs.jsonl`

**Calls into:**
- `agents/doc-gen/WebExperienceCritic.md` (existing — design-pass review)
- `agents/frontend/DesignSystemAuditor.md` (Fas A2 — optional 6-dimension audit if --review)
- the active pack's voice gate (`resolve_pack_field compliance.hooks`; none by default — om customer-share)
- `/li:compliance-gate` (om customer-share)

**Boundary med frontend-* family (L-002):**

generate-app är **rendering-engine** — produces files. frontend-design är **design-director** — produces spec. generate-app does NOT make design-decisions; it READS them from spec + scaffolds accordingly. Same role as generate-web but larger-scope output.

| Concern | generate-web | generate-app |
|---|---|---|
| Output | single .html OR Next.js scaffold (basic) | Full vite/next/svelte project skeleton |
| Use case | Pitch artifact, landing page | Production-grade app POC |
| Routes | 1-3 | Multi (configurable) |
| Build-system | Embedded eller npm-init | Full package.json + npm-build |
| API stubs | No | Optional via --with-api-stubs |
| Auth stubs | No | Optional via --with-auth-stubs |

## Anti-patterns

- **Making design-decisions in generate-app** — wrong layer. Read them från frontend-design-spec.json.
- **Bundling specific component-library versions** — let operator's npm install resolve. Skill body documents version-min, doesn't pin.
- **Generating without schema-version handshake** — M-1 + M-5 violation.
- **Skipping prefers-reduced-motion handling** — accessibility-fail. Mandatory.
- **Inventing routes not in `--routes` flag** — operator decides scope.

## Failure recovery

- Schema-version handshake fail: BLOCKED + diagnostic
- npm install fails in smoke-test: surface error + offer `--skip-smoke-test` retry
- Stack-template missing eller cli scaffold tool unavailable: BLOCKED with install-instruction

## Recommended next steps after invocation

- `cd $out_dir && npm install && npm run dev` — operator validates locally
- `/li:frontend-design-review $out_dir` — Fas A2 6-dimension audit (om not already auto-run)
- Operator commits till customer-repo om customer-share
- Pair med `/li:compliance-gate` för final ship-gate
