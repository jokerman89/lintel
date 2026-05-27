---
name: jstack-scaffold-internal-tool
description: Initialize an internal-tooling repo — CI, README, MS compliance hooks, no customer surface.
color: green
tools: Read, Write, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /scaffold-internal-tool

Initializes an internal-tooling repo (CLI, dashboard, automation script, ops utility). Distinct from `/scaffold-customer-demo` (customer-bearing) and `/scaffold-mvp` (product-grade). Internal-tool scaffold is leaner — no customer-voice gates, but full compliance hooks.

## When to use

- New CLI / utility / automation script for the team
- Internal dashboard or monitoring tool
- One-off engineering helper that may evolve into something bigger
- Pre-MVP exploration before deciding whether to productize

## When NOT to use

- Customer-bearing artifact — use `/scaffold-customer-demo` or `/scaffold-mvp`
- Adding to existing repo — that's not scaffolding, that's a new module
- Test-only scratch project — overkill

## Inputs

- Required `--name <slug>` — kebab-case name
- Optional `--path <dir>` — where to create (default: cwd / `<name>`)
- Optional `--language <ts|py|go|rs>` — primary language (default: ts)
- Optional `--type <cli|service|dashboard|script>` — tool shape (default: cli)
- Optional `--ci <github|azure-devops|none>` — CI setup (default: github)

## Workflow

1. **Create base structure** (language + type dependent):
   - `cli`: `src/index.ts` + `bin/<name>.js` (or equivalent for other languages)
   - `service`: `src/server.ts` + Dockerfile + health endpoint stub
   - `dashboard`: `src/index.html` + minimal Vite/Next setup
   - `script`: single-file `<name>.{ts,py,go,rs}` + minimal config
2. **Standard files:**
   - `README.md` — purpose, install, usage, contributing
   - `CLAUDE.md` — Boris template, internal-tool defaults
   - `.gitignore`, `LICENSE` (MIT default)
   - `.editorconfig`
   - `tests/` directory with one starter test
3. **Language-specific:**
   - `ts`: `package.json` + `tsconfig.json` (strict) + `vitest.config.ts`
   - `py`: `pyproject.toml` + `ruff` config + `pytest.ini`
   - `go`: `go.mod` + standard layout
   - `rs`: `Cargo.toml` + `src/main.rs`
4. **CI setup** (if not `--ci none`):
   - `github`: `.github/workflows/ci.yml` with lint + test
   - `azure-devops`: `azure-pipelines.yml`
5. **Compliance pre-wiring:**
   - `compliance/data-class.md` — declares this is internal-tool (no customer-data surface by default)
   - First-party check baseline (no third-party SDKs pre-added)
6. **Git init + first commit.**
7. **Report.**

## Report format

```
Scaffold internal-tool: gstack-replay-checker

Path: /e/Workspace/gstack-replay-checker
Language: ts
Type: cli
CI: github

## Created
- src/index.ts, bin/gstack-replay-checker
- package.json (tsc strict, vitest)
- tsconfig.json (strict mode)
- tests/index.test.ts
- README.md (template populated)
- CLAUDE.md (internal-tool defaults)
- .github/workflows/ci.yml
- compliance/data-class.md (internal-tool default: Non-business)

## Next steps
1. Edit src/index.ts — implement the CLI entry
2. Run `npm install` (or your package manager)
3. Edit README.md to describe purpose + usage
4. First test: `npm test`
5. First push: feature branch + PR
```

## Compliance integration

- Pre-declares MS Business Data class as Non-business (internal-tool default — operator changes if the tool processes Business+ data).
- Pre-wires `first-party-first` baseline: no third-party SDKs added by default.
- No voice gates (this is internal-tool, no customer surface).

## Voice tier note

`voice: internal`. Skill produces internal-tooling scaffold — no trailblazer surface involved.

## Failure modes

- **Path exists + not empty:** ask whether to merge or pick new path.
- **Language not supported:** list supported, exit.
- **Type not supported:** list valid types, exit.
- **CI selected but template missing for that platform:** fall back to none + warn.
- **Package manager not installed:** create files, skip install, surface manual next steps.

## Examples

**TypeScript CLI:**
```
> /scaffold-internal-tool --name gstack-replay-checker --language ts --type cli
✓ Scaffolded. Run `npm install` then implement src/index.ts.
```

**Python script:**
```
> /scaffold-internal-tool --name daily-status-emitter --language py --type script --ci azure-devops
✓ Scaffolded with Azure Pipelines CI.
```

**Go service:**
```
> /scaffold-internal-tool --name metrics-aggregator --language go --type service
✓ Scaffolded with Dockerfile + health endpoint.
```

## See also

- `/scaffold-customer-demo` — for customer-bearing scaffolds
- `/scaffold-mvp` — for product-grade scaffolds
- `/setup-deploy` — wire deploy targets after scaffold
- `/health` — validate scaffolded structure post-creation
