# Consumer map for the current Copilot adapter behavior

All paths below are absolute under `C:\Users\jokerman\reference-repos\copilot-worktrees\jokerman-session-setup\jokerman-microsoft-literate-fortnight`. No files were modified.

## 1. Tests

### Direct generator and generated-file coverage

- `tests/integration/copilot-kit.py:54,71,105,160,233,269,287,396,615,1291-1315,1530-1563` — imports/runs `bin/li-copilot.py` for local and vendored initialization, check, recovery and collision behavior. Update expected generated skill bodies, full skill/agent inventories, hooks, bundle contents and manifest semantics.
- `tests/integration/copilot-kit.py:482-488` — treats `.github/skills/li-sense/SKILL.md` as a pointer and checks rewritten/missing generated links. Replace pointer assertions with canonical full-body assertions while retaining link-safety coverage where relevant.
- `tests/integration/copilot-kit.py:1357-1433` — manages `.github/lintel/START.md`, inventory and `hooks_installed == False`. Update START expectations and change inventory/hook assertions to the new installed-hook state.
- `tests/integration/copilot-kit.py:1438-1450` — checks generated wrapper behavior and `.github/skills/li-swarm`. Update native skill expectations.
- `tests/integration/copilot-kit.py:1625-1682` — protects existing `copilot-instructions.md`, checks `.github/skills/li-plan`, and collision handling for `.github/agents/lintel-builder.agent.md`. Preserve ownership/collision behavior but expand generated native surfaces.
- `tests/integration/copilot-kit.py:1718` — validates unsafe generated paths including `.github/skills/li-plan`. Keep path validation for the expanded native inventory.
- `tests/integration/copilot-kit.py:1755` — expects a relative canonical `skills/plan/SKILL.md` link in a local wrapper. This is obsolete for full-body native skills and must be replaced.
- `tests/integration/universal-adapters.py:35,67-113,159,195,263,279,317,354,363,414,436,468,534,578` — exercises `li-adapter.py`, inventory, START routes, Copilot wrapper byte preservation, bundle manifest and check/recovery. Update Copilot native-body and hook expectations.
- `tests/integration/universal-adapters.py:69,106,113,195,263,279,317,354,363,578` — explicitly expects `manifest["hooks_installed"]` false or inspects manifest files. Change to the new hook registration/install contract.
- `tests/integration/catalog-installed.py:167,207` — verifies bundled script identity and `hooks_installed == False`. Update manifest expectation.
- `tests/e2e/harness-critical-path.sh:115-127` — downstream Copilot `init` and `check` from installed assets. Add/adjust assertions for full native skills, agents and hooks.
- `tests/runner/check-install.ps1:252` — installed-file smoke list includes `bin/li-copilot`, `skills/cycle/SKILL.md`, `shims/copilot/COPILOT.md`; extend if the generated hook adapter or other required source files become install prerequisites.
- `tests/unit/adapter-navigation.py:10,108` — imports `bin/li-copilot.py` and checks Markdown reference preservation. Keep navigation checks but revise pointer-specific expectations.
- `tests/unit/cohort6-fas3-skills-present.sh:48` — runs vendored `bin/li-adapter.py check`; retain, with expanded generated output.
- `tests/unit/native-command-surface.py:1281,1315,1325` — fixtures and prose refer to `.github/skills/li-*` wrappers. Update fixture semantics from wrappers to native generated skills.

### Counts/catalog

- `skills/CATALOG.md:8-10` — generated catalog says `Total skills: 96`; this remains the canonical skill count but should be reused by generator/tests rather than hard-coded separately.
- `docs/architecture.md:51` — says the tree holds 96 skill entries.
- `docs/showcase/lintel-the-harness.html:38,42` — displays 96 skills and 69 agents; update only if canonical counts change.
- `tests/shape/uniformity-coverage.sh:82` — reports enumerated skill/agent/hook/pack counts dynamically; likely no fixed count change, but ensure generated native files are not mistaken for canonical files.
- `tests/unit/ci-matrix.py:86-113` — fixture path lists include `shims/copilot/COPILOT.md` and a synthetic `li-x` skill fixture path under the Copilot skill root; update expected generated surface fixtures if their classification changes.

## 2. CI workflows and runner coverage

- `.github/workflows/ci.yml:144` — runs `python3 bin/li-catalog.py --check`; adding `copilot` to skill `cli_support` must keep catalog generation/check output synchronized.
- `.github/workflows/ci.yml:150` — runs `python3 bin/li-copilot.py check --target . --source .`; this becomes the primary generated native skills/agents/hooks verification.
- `.github/workflows/ci.yml:153` — runs `bash bin/li-wiki-gen --check`; generated wiki skill/agent counts and `cli_support` projections may change.
- `.github/workflows/catalog.yml:30` — independently runs `python3 bin/li-catalog.py --check`.
- `.github/workflows/presentation-pages.yml:8,12` — only watches/builds presentation-page paths; no direct Copilot generator dependency.
- `tests/runner/run-all.sh:52-56` — selectable suites are `unit`, `behavior`, `integration`, `e2e`, `shape`, or `all`; there are no named “parts/shards” for Copilot. Relevant coverage is in the `integration`, `e2e`, `unit`, and `shape` selections.
- `tests/runner/run-all.sh:108-110` — hook tests consume stdin and need `/dev/null` isolation; new Copilot hook tests must follow this runner constraint.

## 3. Adapter entry points and client root selection

- `bin/li-adapter.py:15-21` — dynamically loads `bin/li-copilot.py` and calls `adapter.main(universal=True)`. Any generator behavior change affects every Universal adapter route.
- `bin/li-copilot.py:675` — `generate(source, target, clients=("copilot-cli",))` is the shared generator.
- `bin/li-copilot.py:679-682` — loads `lib/cli-tiers.yaml`, resolves aliases and detects Copilot surfaces by `discovery.kind == "copilot"`.
- `bin/li-copilot.py:690-704` — vendored `COMPONENTS` bundle currently excludes `hooks`; add `hooks` here.
- `bin/li-copilot.py:747-765` — currently creates 15 pointer skills from `WORKFLOWS`, using “Read the [Copilot adapter contract]” and canonical-file links. Replace with all canonical skill bodies.
- `bin/li-copilot.py:766-779` — currently creates only three `lintel-{planner,builder,reviewer}` pointer agents. Extend to every canonical agent plus these three roles.
- `bin/li-copilot.py:780-802` — emits `.github/instructions/lintel-session.instructions.md` and `.github/copilot-instructions.md`; retain but update references from pointer fallback wording where appropriate.
- `bin/li-copilot.py:803-810` — removes Copilot files when no selected record is Copilot; preserve.
- `bin/li-copilot.py:814-836` — emits skill roots selected from registry. `.github/skills` is selected for `copilot-*`; `.claude/skills`, `.agents/skills`, `.cursor/skills` remain pointer-wrapper roots for their respective `kind == "skills"` records.
- `bin/li-copilot.py:837-856` — START route describes selected roots and currently says “No hooks ... were installed.” Update for Copilot hook registration.
- `bin/li-copilot.py:873+` and inventory logic around `bin/li-copilot.py:900-940` — managed inventory allows `.github/lintel`, native skill paths, `.github/agents/lintel-*`, instructions and Copilot instructions. Expand allowed managed paths for all generated native agents and hook files.
- `bin/li-copilot.py:1004` — `--client` is repeatable; routes are selected by exact surface ID or alias.
- `bin/li-copilot.py:1045` — calls `generate(source, target, tuple(clients))`.
- `bin/li-lifecycle.py:933-941` — chooses `bin/li-copilot.py` for `--copilot` and `--client`, then passes selected clients.
- Registry roots in `lib/cli-tiers.yaml`: Copilot surfaces (`copilot-cli`, `copilot-app`, `copilot-vscode`, `copilot-cloud`) use `.github/skills`; Claude uses `.claude/skills`; Codex uses `.agents/skills`; Cursor uses `.cursor/skills`; manual surfaces have no root.

## 4. Registry schema and validator

- `lib/client_capabilities.py:50-91` — validates registry schema version 2, operation IDs, sources, surface names, discovery kinds/roots, `preserved`, `hook_adapter`, vendor claims and observations.
- `lib/client_capabilities.py:72-78` — non-manual discovery roots must match `\.[a-z][a-z0-9-]*/skills`; Copilot discovery must specifically use `.github/skills`.
- `lib/client_capabilities.py:81-84` — `preserved` must be a list of non-empty paths.
- `lib/client_capabilities.py:85-88` — `hook_adapter`, if present, must be an object whose `path` is listed in `preserved` and whose `activation` is non-empty. To support `.github/plugin/hooks.json` as a generated adapter, decide whether this validator must permit a generated/non-preserved adapter or change the registry model.
- `lib/client_capabilities.py:89-96` — vendor claims must use operation IDs and `{status: documented|conditional|unsupported, source: known source}`.
- `lib/client_capabilities.py:93-108` — observation keys must be operation IDs; each record allows `status: observed|partial|failed`, `scenario`, `host_version`, `lintel_revision`, `checked`, `evidence`, and for non-observed records `limitations`. Observed records require non-empty `host_version` and a 40-hex `lintel_revision`; all require non-empty scenario/date/evidence.
- `lib/cli-tiers.yaml:83-88` — `copilot-cli` currently preserves `.github/plugin/plugin.json` and has vendor claims including hooks, but no `hook_adapter`.
- `lib/cli-tiers.yaml:88-121` — other Copilot surfaces use `.github/skills`; `copilot-app` has observations for question/delegate/isolate, while Copilot CLI currently has none.
- `tests/unit/client-capabilities.py:103+` — mutates/validates observation records; update only if the hook adapter or observation schema changes.
- `tests/unit/cli-tiers.sh:20-47` — currently asserts only Claude supports hooks and explicitly expects Copilot/non-Claude hooks unsupported. These assertions must change if Copilot becomes a registered hook surface.
- `tests/unit/copilot-capabilities.sh:17` — states Copilot compatibility hints do not claim installed hooks or full validation. Must be revised.
- `bin/li-client-capabilities.py:24-30` — exposes `--client` registry selection and is a consumer of the same schema.

## 5. Documentation and generated reference surfaces

### Copilot/universal adapter contracts

- `shims/copilot/COPILOT.md:23-24` — says only `.github/skills/li-*` are native entry points and not every catalog workflow is validated. Update to all generated canonical skills and native agents.
- `shims/copilot/COPILOT.md:83-84` — documents `/li:<name>` mapping to `/li-<name>` wrappers or canonical reads. Replace fallback language with native skill behavior.
- `shims/copilot/COPILOT.md:107-110` — says Claude hooks differ and Copilot does not install/activate them. Document the new Copilot adapter registration and its limits.
- `shims/universal/ADAPTER.md:34-37` — distinguishes plugin `/li:<skill>`, generated `li-*` wrappers and manual canonical reads. Update Copilot route.
- `shims/universal/ADAPTER.md:76-82` — describes discovery and hooks as separately activated/not installed. Update Copilot hook route.
- `docs/copilot.md:4,58,66-77,100-114,159-176` — describes native core workflow skills, three custom profiles, Copilot CLI/cloud routes, hooks reference and validation limits. Replace “core/three” counts and no-hook claims.
- `docs/multi-cli.md` — search hits include Copilot kit and adapter route material; update any `.github/skills` pointer/root and hook statements.
- `docs/client-adapters.md:33-42` — says every native route generates `li-<skill>` wrappers and Copilot selects existing `.github/skills` plus custom-agent kit. Update to full canonical skill and full agent generation.
- `docs/getting-started.md:52,68-71,108-125` — says wrappers are `li-*`, `.github/lintel` is a bundle, and portable adapters install no hooks. Update skill/agent/hook table.
- `docs/architecture.md:68` — catalog is generated from frontmatter by push/CI; preserve.
- `docs/architecture.md:330-336` — says Copilot retains `.github/skills/li-*`, three agents, and cannot activate/adapt hooks. Update directly.
- `hooks/shared/README.md:3-10` — says `.github/plugin/hooks.json` registers none and portable adapters do not register/run hooks. This is the most important hook documentation change.
- `README.md:114` — documents `bash bin/li-copilot init --target .`; retain, but generated-result expectations elsewhere must change.
- `CONTRIBUTING.md:14,226+` — identifies canonical content and generators as deliverables and points to the Copilot guide; update generator/test/documentation scope.
- `.github/copilot-instructions.md:4,9-10` — tells Copilot to read the contract and use `.github/skills/li-<name>/SKILL.md` when slash discovery is unavailable. Update wording to native full-body skills and generated agents.
- `AGENTS.md:44,63,145,163,222` and corresponding `CLAUDE.md` protocol blocks — describe preserved plugin routes, actual agent discovery, and no assumptions about registration. Keep the general honesty rules; update Copilot-specific statements where present.
- `skills/CATALOG.md:8,10,113` — says total is 96 and generated by `python3 bin/li-catalog.py`; do not hand-edit. Adding `copilot` support changes generated metadata but not necessarily the total.

### Generated wiki/showcase

- `docs/wiki/README.md:1,3,46,48` — generated wiki; regenerated by `bin/li-wiki-gen`; CI checks with `bin/li-wiki-gen --check`.
- `docs/wiki/agents.md:1,3` — generated by `bin/li-wiki-gen`; agent inventory/count changes.
- `docs/wiki/skills.md:1,3` — generated by `bin/li-wiki-gen`; skill `cli_support` changes will appear here.
- `docs/wiki/packs.md:1,3` and `docs/wiki/schemas.md:1,3` — also generated by `bin/li-wiki-gen`, though not directly affected.
- `docs/concepts/wiki-generation.md:11-12` — maps skill frontmatter to `docs/wiki/skills.md` and agent frontmatter to `docs/wiki/agents.md`.
- `docs/showcase/lintel-the-harness.html:38,42` — generated/showcase numbers 96 skills and 69 agents; update if counts are sourced or displayed differently.

## 6. Hook-related tests

- `tests/unit/hook-input-adapter.sh:3,11` — regression test for `hooks/shared/_input.sh`; unaffected internally, but new Copilot hook registrations must use compatible input expectations.
- `tests/unit/hook-gate-content.sh:3,22,91` and `tests/unit/hook-push-history.sh:20,159,216` — source `_input.sh` and assert audit behavior; preserve.
- `tests/unit/universal-trusted-tools.py:163-164,700-707` — treats `hooks/shared/_input.sh` and `hooks/hooks.json` as trusted source files and verifies `hooks/hooks.json` immutability. Extend trusted-source assertions for `hooks/adapters/` if required.
- `tests/shape/hooks-registration-safe.sh:3,22-44` — validates `hooks/hooks.json` registration and commands; add equivalent validation for `.github/plugin/hooks.json` and `.github/hooks/lintel.json`.
- `tests/unit/cycle-continuity.sh:118-120` — asserts Claude `hooks/hooks.json` registrations; keep separate from Copilot.
- `tests/integration/session-leaves-traces.sh:70-78` — validates `hooks/hooks.json`; add Copilot registration coverage separately.
- `tests/integration/copilot-kit.py:1427` and `tests/integration/universal-adapters.py:69,106,113,195,263,279,317,354,363,578` — assert `hooks_installed` false. These are direct current-behavior failures after the change.
- `tests/unit/copilot-capabilities.sh:17` — explicitly asserts no installed hooks; must be changed.
- No search result found for a test asserting `.github/plugin/hooks.json` specifically has no hooks beyond the general `hooks_installed`/Copilot-capability assertions. The current empty/absence semantics are primarily documented in `hooks/shared/README.md` and represented by the inventory field.

## 7. `.gitattributes` and `.gitignore`

- `.gitattributes:28-34` — marks `.github/lintel/**`, `.github/skills/li-*/**`, `.github/agents/lintel-*.agent.md`, instructions and Copilot instructions as generated portable-kit paths. Expand patterns for all native generated `.github/agents/*.agent.md` and `.github/plugin/hooks.json`, `.github/hooks/lintel.json`, plus any `hooks/adapters`-derived files if tracked/generated.
- `.gitignore:106` — ignores `.claude/runtime/`; retain. The Copilot generator explicitly excludes runtime/customer material from bundles, so do not broaden this to generated `.github` paths unless repository policy changes.

## 8. Plugin manifests and versions

Current versions:

- `.claude-plugin/plugin.json:4` — `0.12.0`.
- `.claude-plugin/marketplace.json:9,16` — `0.12.0` in marketplace and plugin entry.
- `.github/plugin/plugin.json:3` — `0.12.0`.
- `.github/plugin/marketplace.json:6,12` — `0.12.0`.
- `.codex-plugin/plugin.json:3` — `0.12.0`.
- `.cursor-plugin/plugin.json:5` — `0.12.0`.
- `.github/plugin/hooks.json:2` — hook schema `"version": 1`, not the plugin version.

No direct repository test was found asserting version equality across all plugin manifests. Search only identified the manifest version fields themselves. The new generated `.github/plugin/hooks.json` should preserve hook schema versioning independently from plugin versioning.

## 9. Skill-body agent references and naming convention

Representative canonical references:

- `skills/cycle/SKILL.md:199-203` — `agents-wake: ... DesignReviewer`, `ArchitectureScout`, `PlanReviewer`, `CostAnalyzer`.
- `skills/swarm/SKILL.md:150,157,166-168` — `subagent_spawn`, native subagent host, reviewer identity and reviewer-only artifact.
- `skills/ship/SKILL.md:251,265` — dispatch names `CustomerEmpathyCheck` and `PostDemoFollowup`.
- `skills/diagnose/SKILL.md:177` — `DebugForensics` subagent.
- `skills/perfbench/SKILL.md:16,27,142` — `PerformanceAnalyzer` subagent.
- Additional naming examples: `skills/review/SKILL.md:391` uses `CodeReviewer`; `skills/build/SKILL.md:451` recommends `CodeReviewer`.

Naming is canonical display/name-field convention, generally PascalCase and not `lintel-<name>`. Generated Copilot `.agent.md` files must preserve canonical agent names in frontmatter/body while likely using a filesystem-safe native filename; the three adapter roles remain separately named `lintel-planner`, `lintel-builder`, and `lintel-reviewer`.

## 10. Frontmatter parsing and reusable generators

- `bin/li-catalog.py:48-72` — reads bounded YAML-like frontmatter and scalar fields without external YAML dependencies.
- `bin/li-catalog.py:102-113` — generates catalog from skill frontmatter and records generated-source provenance.
- `bin/li-catalog.py:176-190` — parses/validates `cli_support` as a list, validates declarations and rejects duplicate surfaces.
- `bin/li-catalog.py:248-286` — parses skill/agent metadata and emits normalized catalog entries including `cli_support`.
- `bin/li-catalog.py:544-586` — CLI generation/check modes; `--check` compares generated catalog output.
- `lib/frontmatter.sh:4-17` — shell validator requiring skill fields `name description color tools voice cli_support`, and corresponding agent fields through its `skill|agent` mode.
- `lib/markdown_source.py:313` — `classify_markdown()` identifies Markdown structural boundaries; useful for body-preservation/rewriting checks, but it is not a YAML frontmatter parser.
- `lib/uniformity-coverage.sh:12-24,40,66-67` — parses frontmatter field presence and skill kind.
- `lib/wiki-gen.sh:82-97` — parses frontmatter scalars and `workflow_root`.
- `skills/CATALOG.md:113` — confirms `python3 bin/li-catalog.py` is the source-of-truth generation command.

## Surprises or risks

- The registry currently requires a `hook_adapter.path` to appear in `preserved`; generated Copilot hooks may require a schema/model change rather than only adding YAML.
- `copilot-cli` already declares a vendor `hooks` capability, while tests and docs still assert that only Claude supports hooks; registry, tests and docs are inconsistent before implementation.
- `COMPONENTS` excludes `hooks`, but `ADAPTER_RESOURCES`/trusted-source logic may independently require hook-related files; adding `hooks` can substantially enlarge vendored bundles and expose paths that current link rewriting does not expect.
- Inventory validation currently permits only `.github/agents/lintel-*`; all 69 canonical native agents need an explicit managed-path rule.
- The 96/69 figures are repeated in architecture, catalog and showcase surfaces; generated wiki files may add further derived counts not found by the narrow search.
- Canonical agent references use PascalCase names such as `DesignReviewer` and `CodeReviewer`, while the current adapter’s generated files use `lintel-*`; careless normalization could break dispatch documentation.
- `.github/plugin/hooks.json` currently exists with schema version 1, but current documentation describes it as registering no hooks; the implementation must distinguish an empty plugin manifest from the new generated registration and avoid conflating plugin version with hook schema version.