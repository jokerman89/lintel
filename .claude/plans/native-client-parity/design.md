# Design: native client parity for the four supported client families

- **Status:** APPROVED direction (operator, 2026-09-28: "implement this richly for these clients,
  go 100% support or as far as possible ... Start with Copilot, then get that to main first, then
  the rest"). Increment 2 details are DRAFT until its research is reconciled.
- **Cycle:** `native-client-parity-20260928` (meta-infra, gates M1-M4 active)
- **Scope record:** `.claude/runtime/state/scope.md` (size XL, depth tree, route override none)
- **Families (ADR-0035):** GitHub Copilot, Claude, Codex, Cursor. Gemini and the other removed
  families stay removed.

## Context and goal

A `/li-cycle` session on Copilot (session `4125f187`, 2026-09-25) did not follow the Lintel method.
Its event log shows the native skill tool injected `.github/skills/li-cycle/SKILL.md`, a 518-byte
pointer. The agent then read lines 1-200 of the 489-line canonical `skills/cycle/SKILL.md` through the
`view` tool, which refuses single reads over about 20 KB. It never paged further, so it skipped cycle
identity, the phase chain, the pre-BUILD gate and the swarm hand-off, and it read no memory. A
`lintel-builder` subagent did the same with `skills/build/SKILL.md`.

The root cause is structural. Every non-Claude adapter `bin/li-copilot.py` generates is a pointer
that asks the model to read and adapt a large canonical file at runtime. Eight canonical skills
exceed 20 KB (`plan` is 42.7 KB). The Claude plugin works because Claude Code injects each skill
body natively.

**Goal:** each supported client runs Lintel through its own native, documented surfaces with the
same content and guardrails Claude Code gets: complete skills, the agent roles the skills name,
lifecycle hooks, instructions and an installable plugin. Where a client cannot match a behavior,
say so precisely in the registry and docs.

## Evidence (observed 2026-09-28 unless stated)

| Fact | Evidence |
|---|---|
| Copilot injects a whole 63 KB skill body; the model saw a marker at its end with only the `skill` tool available | Headless CLI session `11a955ee`, `skill.invoked` content 63,028 bytes |
| The earlier failure came from the `view` tool's ~20 KB cap, not a skill limit | Session `4125f187` events 14-36 |
| Copilot lists plugin skills by plain name (`li-build`, source `plugin`) and reads `.github/plugin/plugin.json` before `.claude-plugin/` | `copilot --plugin-dir <repo> skill list --json` |
| Copilot plugin hooks run with cwd = plugin root; env has `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_PROJECT_DIR` (and `COPILOT_*`/`PLUGIN_ROOT` aliases); payload `cwd` = workspace | Probe session `c7c549f1` |
| `sessionStart`/`postToolUse` top-level `additionalContext`, `userPromptTransformed` `modifiedTransformedPrompt`, and a PascalCase `PreToolUse` (Claude matcher `Bash` matching `powershell`) JSON deny all worked | Probe `c7c549f1` |
| Claude `hookSpecificOutput` works only for `PreToolUse` deny; for context events it is ignored; exit 2 denies without surfacing stderr | Probe 2 (CLI 1.0.89, `gpt-5-mini`) |
| Custom agents accept Claude tool names as aliases; body limit 30,000 chars; all 69 canonical agents are at most 11.4 KB | GitHub custom-agents reference; local inventory |
| VS Code Local harness uses Claude-style `hookSpecificOutput`, exit 2 + stderr, and its own tool names | VS Code hooks reference |
| Spec Kit renders complete `.github/skills/speckit-*/SKILL.md` bodies from templates; gstack generates complete per-host SKILL.md from `.tmpl` sources with per-host frontmatter allowlists and path/tool rewrites | `github/spec-kit` integrations; `garrytan/gstack` host config |

## Scope

**Increment 1 (this PR, to `main`): GitHub Copilot** (CLI, app, VS Code, cloud agent).

1. Generate a **self-contained native skill for every canonical skill** at `.github/skills/li-<name>/`,
   with deterministic transforms applied.
2. Generate **native custom agents** for all 69 canonical roles, and keep the three `lintel-*` role agents.
3. **Port the auto-registered hook bundle** through a Copilot host adapter. The plugin registers it
   by default and runs only the plugin's own tree (ADR-0008). Repository `.github/hooks/lintel.json`
   is an explicit opt-in (`li-copilot init --hooks`) for teams that accept repository-committed hook
   code, including cloud-agent jobs. Lintel itself does not enable repository hooks in increment 1,
   and dogfoods through the plugin.
4. Make the **Copilot plugin** the primary install route (CLI `copilot plugin install`, app plugin UI,
   cloud agent `enabledPlugins`), and keep the committed repository kit for teams that vendor.
5. Update the adapter contract, registry facts and observations, docs, catalog hints, ADR and migration
   guide, and add live acceptance evidence.

**Increment 2 (after increment 1 merges):** Claude, Codex, Cursor. Reuse the same generator host
profiles and the same hook adapter core for each client's native skill root, agent format, hook
config, rules and plugin manifest, once the research reports now in flight are reconciled.

**Out of scope:** trimming canonical skills (a later optional optimization; it would change Claude
behavior), new client families (ADR-0035), enterprise policy hooks, credentials, model settings, and
the 24 opt-in hooks. The adapter supports them, but only the nine auto-registered hooks are
registered.

## Constraints

- **Canonical content stays single-source.** `skills/`, `agents/` and `hooks/shared/` are authoritative.
  Native artifacts are generated, committed and drift-checked. Never hand-edit generated files.
- **Standard library only, no network, preflighted writes.** Keep the managed inventory, collision and
  recovery semantics of `li-copilot` (ADR-0024, ADR-0030/0031 path rules).
- **No new third-party packages (L-054).** Hooks stay Bash; no `jq` requirement. The Windows launcher
  uses the PowerShell that Copilot already runs.
- **Only `jokerman89` publishes (L-053).** New commits only, with no amend/reset/rebase (L-055, L-060).
  The plugin version bumps uniquely (L-020).
- **Keep product documentation host-neutral (L-030).** Separate documented, delivered and observed
  facts in `lib/cli-tiers.yaml`.
- **Hooks must never brick a session.** A crash in a Copilot `preToolUse` command hook denies the
  tool, so the adapter always exits 0 and expresses blocks only as JSON decisions.

## Decisions and alternatives

**D1: Skill delivery.**
- (A) Keep pointers with stronger prose. Rejected: the evidence shows that prose is not followed.
- (C) Trim canonical skills under 20 KB and keep pointers. Rejected as the fix: the indirection stays
  and Claude behavior changes.
- **(B) Selected:** generate complete native skills from canonical sources with host transforms
  (the Spec Kit and gstack pattern).

**D2: Native skill set.**
- (A) Core 15 only. Rejected: that is not 1:1 with the Claude plugin, which exposes every skill.
- (C) Only skills whose `cli_support` names Copilot. Rejected: stale hints would exclude core methods
  (`fix`, `adr-new`, `lessons-add`, the `ta`/`da`/`sc`/`dh`/`tq` modules).
- **(B) Selected:** expose every canonical skill, and update `cli_support` so the catalog shows the
  native Copilot delivery. Use `level: degraded` with a stated reason where a skill depends on a
  Claude-only facility.

**D3: Agents.**
- (A) Only the three pointer roles. Rejected: skills wake canonical roles by name.
- (C) Per-pack selection. Deferred.
- **(B) Selected:** generate all canonical agents with an allowlisted frontmatter (`name`,
  `description`, `tools`), keeping canonical names so skill references resolve unchanged, and keep
  `lintel-planner/builder/reviewer`.

**D4: Hooks.**
- (A) Do not port. Rejected: L-016 says continuity needs the deterministic substrate.
- (B) Rewrite the hooks per host. Rejected: duplicated logic and drift.
- **(C) Selected:** one host adapter that normalizes each client's payload, runs the unchanged
  canonical `run.sh` scripts, and translates their exit code, stderr, stdout and context into the
  client's documented output. On Copilot it emits top-level fields plus `hookSpecificOutput`, which
  covers CLI and VS Code Local.

**D5: Distribution.**
- (A) Repository kit only, or (B) plugin only.
- **(C) Selected:** the plugin is the intended Copilot route. The repository kit stays for vendored,
  offline and cloud-committed use. When both are present, both routes run, and a repository-origin
  run never suppresses the plugin (R2). Skills keep the same names.

**D6: Generator shape.**
- (A) More Copilot-specific branches in `li-copilot.py`, or (C) one script per host. Both rejected.
- **(B) Selected:** declarative host profiles (skill root, name pattern, frontmatter allowlist,
  invocation and tool rewrites, link-rebase root, agent format, hook adapter) consumed by one shared
  module. Increment 1 implements the Copilot profile and leaves the other surfaces' current output
  unchanged until increment 2.

## Copilot transforms (increment 1)

- **Frontmatter:** `name: li-<name>` plus the canonical `description` (the curated `WORKFLOWS` text for
  the core 15), 1024 characters at most.
- **Preamble:** a short Copilot block covering:
  - resource root, relative to the skill base directory: `../../..` in Lintel and the plugin,
    `../../lintel` in a vendored kit;
  - the one-line helper bootstrap;
  - the runtime tool map from GitHub's hook reference (`bash`/`powershell`, `view`, `create`, `edit`,
    `grep`, `glob`, `ask_user`, `task`, `web_fetch`);
  - the rule that each `/li-<name>` is a native skill to invoke, not a file to read.
- **Body:** the full canonical body, with:
  - `/li:<name>` rewritten to `/li-<name>`;
  - `AskUserQuestion` rewritten to `ask_user`;
  - relative Markdown links rebased so they resolve from the generated location;
  - `CLAUDE_PLUGIN_ROOT` prose kept, since Copilot plugin hooks export it and the preamble explains
    the root;
  - no other semantic edits.
- **Agents:** agents get the same body transforms and a shorter resource-root preamble. Dropped
  canonical fields (`memory`, `model`, `color`, `tier`, `voice`, `category`, `cli_support`) are
  recorded as documented degradations, not silently lost.
- **Links:**
  - A target inside the bundle stays relative from the generated file.
  - A target the vendored bundle excludes (`.claude/`, unbundled docs) uses the bundle's existing
    public-repository URL policy (`local_link`/`bundle_documentation`, `PUBLIC_SOURCE_NOTE`), so
    offline resolution of those few references is explicitly lost.
  - `verify_links` covers every generated skill and agent in both modes.

## Hook adapter (increment 1, revised after design review R1)

Registrations use **camelCase events with runtime tool-name matchers**: `bash|powershell` for shell,
and `edit|create|str_replace_editor|apply_patch` for edits. `create` is Copilot's Write, and there
is no runtime tool named `write`. This preserves the actual shell identity. The adapter exports
`LINTEL_HOOK_SHELL` from `toolName`.

The git gate (`hook_git_gate_content`) gains a **PowerShell dialect** tokenizer:

- backslashes are literal, the backtick is the escape character, and `'...'`/`"..."` quoting follows
  PowerShell rules;
- `$` expansion is rejected, except for a leading `$env:LINTEL_OVERRIDE_*='1';` override statement,
  so the audited overrides work on Windows;
- the POSIX dialect stays byte-for-byte unchanged for Bash and Claude.

`_input.sh` reads both the camelCase `toolArgs` payload and the snake_case `tool_input` payload.

**Event × surface output contract.** The adapter emits one JSON object, never exits non-zero after
launch, and reports warnings only on channels the event supports:

| Canonical outcome | `preToolUse` | `sessionStart`, `postToolUse` | `userPromptTransformed` | `agentStop` |
|---|---|---|---|---|
| Block (exit 2 + stderr) | `permissionDecision: deny` + reason, and `hookSpecificOutput` mirror | n/a (canonical hooks here never block) | never blocks (ADR-0023) | never blocks (L-016, ADR-0022) |
| Context (stdout text or `hookSpecificOutput.additionalContext`) | progress line (user-visible, as Claude transcript) | top-level `additionalContext` + `hookSpecificOutput` mirror | sentinel-wrapped append to `modifiedTransformedPrompt` | progress line + `systemMessage` (VS Code); cloud: audit only |
| Non-blocking stderr | progress line | progress line | ignored (audit) | progress line |

The `userPromptTransformed` splice uses a **top-level JSON tokenizer** (awk: depth- and string-aware,
not a regex). It extracts only the depth-1 `transformedPrompt` literal and appends escaped context
inside a `<lintel-context>` sentinel. It skips when the sentinel is already present (idempotent across
batched preceding messages and resume replay), caps the context at 4 KB, and skips prompts over 1 MB.
Any extraction doubt produces no output, so the prompt is unchanged.

**Fail-open scope.**

- After launch, the adapter traps its own errors and exits 0.
- The PowerShell launcher exits 0 when Git Bash is missing and emits one progress line.
- Launch failures of PowerShell itself are the host's documented fail-closed behavior, and are tested
  live on the CLI.
- Timeouts are fail-open by the host.
- `LINTEL_HOOKS_DISABLED=1` is an escape hatch the adapter checks before doing any work.

**Dedupe (revised R2): none across origins.** A repository-origin run must never suppress the trusted
plugin's enforcement. So when both routes are installed, both run. Duplicate denials are harmless,
and duplicated context is a documented cost of a double install. The migration guide and
`li-copilot init --hooks` output recommend a single route.

**PowerShell overrides (R2).** At `preToolUse` time a `$env:` assignment has not executed yet. So
for the PowerShell dialect the adapter parses a leading `$env:LINTEL_OVERRIDE_SECRET` /
`LINTEL_OVERRIDE_CUSTOMER_DATA` / `LINTEL_OVERRIDE_REASON` statement sequence from the command text.
It exports those values into the canonical hook's environment and passes the remaining command to
the gate. The existing audited override path then records it unchanged.

**Prompt splice (R2).**

- Inject at most once per batch: a per-session timestamp marker skips a second injection within
  5 s.
- Reject payloads with duplicate depth-1 keys.
- Escape every JSON control character in the added context.

### Original adapter sketch (superseded where the revision above differs)

The adapter is `hooks/adapters/copilot.sh <Event> <hook>...`. It:

- reads stdin once and runs `cd` into `CLAUDE_PROJECT_DIR`, falling back to the payload `cwd`;
- extends `_input.sh` for Copilot fields (`new_str`, `old_str`, `file_text`, `path`);
- runs each hook's `run.sh` with the payload and collects each exit code, stderr and stdout;
- maps the results:
  - exit 2 becomes `permissionDecision: deny` with stderr as the reason;
  - plain stdout becomes progress lines on tool events and `additionalContext` on context events;
  - `hookSpecificOutput.additionalContext` becomes top-level `additionalContext`;
  - for `userPromptTransformed`, the raw JSON-encoded `transformedPrompt` literal is spliced with the
    escaped context without decoding, and nothing is emitted when extraction is uncertain;
- always exits 0.

Launchers:

- **`bash` field:** `bash "<root>/hooks/adapters/copilot.sh" ... || true`.
- **`powershell` field:** an inline, execution-policy-independent launcher. It sets UTF-8 I/O and
  locates Git for Windows' `bash.exe` explicitly (never System32 WSL, per ADR-0032). It forwards
  stdin, relays stdout, and exits 0. If Bash is missing, it prints one progress line and allows the
  call.

Registered events:

- `SessionStart`: `session-digest`
- `PreToolUse` `Bash`: `secret-scan-block`, `customer-data-block`, `no-direct-main-push`
- `PreToolUse` `Edit|Write`: `no-secrets-in-edit`
- `PostToolUse` `Edit|Write`: `memory-budget-warn`
- `Stop`: `cycle-incomplete-warn`, warn-only (L-016), never `decision: block`
- `userPromptTransformed`: `cycle-position-inject`, `no-customer-data-in-message`

## Risks and mitigations

- **Crash or timeout denies tools.** Exit 0 always, `|| true` launchers, per-hook timeouts,
  fail-open tests.
- **Prompt corruption from splicing.** Strict JSON string-literal extraction, and no output on doubt.
  Tested with quotes, backslashes, Unicode and very large prompts.
- **Windows latency** (a PowerShell plus Bash spawn per matched tool call). Narrow matchers, one
  dispatcher per event; latency is measured and reported.
- **Double registration.** Both routes run, and a repository run never suppresses the plugin (R2).
  The docs recommend a single route.
- **Context growth.** About 96 skill descriptions and 72 agents, the same load the Claude plugin
  carries. Size is measured and reported, and descriptions stay within 1024 characters.
- **Generated churn.** Deterministic output, a `li-copilot check` drift gate in CI, and
  documentation in CONTRIBUTING.
- **Surface variance.** VS Code Local tool names differ, and the cloud agent is Bash-only with repo
  hooks. The registry records each as conditional or unverified until observed.

## Acceptance matrix (surface × route, R1)

| Surface | Plugin route | Vendored kit route | Evidence required in increment 1 |
|---|---|---|---|
| Copilot CLI | required live | required live (hooks opt-in) | headless sessions, event-log evidence |
| Copilot App | attempt live via an app session | attempt live | observation if run; otherwise `conditional`, not claimed |
| VS Code Local | not run | not run | documented `conditional`; tool names and formats may differ |
| Cloud agent | not run (`enabledPlugins` hook behavior unverified) | not run (repo hooks opt-in) | documented `conditional` |

**Measurement gates:**

- all generated skills and agents are discovered by CLI list commands;
- the largest skill is injected whole;
- matched-tool hook latency on Windows is at most 2 s (median of 5);
- the startup digest is at most 8 KB;
- the combined description metadata of native skills and agents (the per-turn discovery overhead)
  is at most 48 KB;
- vendored bundle growth is at most 2 MB;
- `li-copilot check` on Lintel takes at most 60 s.

If a gate fails, shorten the descriptions to curated forms, defer bulk agent exposure, or narrow
the matchers, and report it.

## Success criteria

- **AC1:** every canonical skill has a generated native skill with valid frontmatter (name equals
  directory; description within 1024 characters), the complete transformed body, no residual `/li:`
  references and resolving links. `li-copilot check` passes locally and in CI.
- **AC2:** 69 canonical agents and 3 role agents are generated with allowlisted frontmatter, each
  under 30,000 characters.
- **AC3:** hook adapter unit tests replay payloads for every registered event and tool shape. The
  payloads were recorded live where the host allowed (spec §Recorded payloads); camelCase `bash` is
  contract-derived and labeled. The tests check deny JSON, context JSON, progress-only warnings,
  exit 0 on every path and fail-open on internal errors. They pass on Ubuntu, macOS and Windows CI.
  The live `bash` payload observation stays open as `conditional`.
- **AC4:** the plugin `hooks.json` is generated and valid. The repository `.github/hooks/lintel.json`
  is generated only with `--hooks`, and is recorded in the inventory. These manifests bump together
  past the highest version on `main`, verified by a fresh check just before merge (0.13.0 unless
  `main` has moved):
  - `.claude-plugin/plugin.json`
  - `.claude-plugin/marketplace.json` (both fields)
  - `.github/plugin/plugin.json`
  - `.github/plugin/marketplace.json` (both fields)
  - `.codex-plugin/plugin.json`
  - `.cursor-plugin/plugin.json`
- **AC5:** a vendored kit in a temporary repository generates the same artifacts with `.github/lintel`
  roots, `check` passes and links resolve.
- **AC6:** live headless Copilot CLI acceptance runs cover both the plugin route (`--plugin-dir`) and
  a vendored kit with `--hooks` in a temporary consumer repository. They must show:
  - full `li-cycle` injection;
  - digest context visible;
  - a synthetic-secret commit denied with Lintel's reason, on the Windows PowerShell tool;
  - a PowerShell `$env:` override allowed and audited;
  - agents discovered;
  - the measurement gates met.

  Host versions and the Lintel revision are recorded as registry observations. App, VS Code Local
  and cloud agent follow the acceptance matrix.
- **AC7:** ADR-0038 is accepted before BUILD (done in DEFINE/PLAN). The adapter contract, docs,
  CHANGELOG, migration guide and evolution entry are updated. The compatibility audit and shape
  tests are green.
- **AC8:** the full CI matrix passes on the PR, and the PR is merged to `main`.

## Adoption and handoff

- **Plugin users:**
  - CLI: `copilot plugin install jokerman89/lintel`.
  - App: Customize → Plugins.
  - Cloud agent: `enabledPlugins` in `.github/copilot/settings.json`.
- **Kit users:** re-run `li-copilot init` to regenerate. The migration guide lists the new files and
  the hook activation boundary.
- **PLAN inputs:** this design, the scope record, the DISCOVER consumer map and the three research
  reports (increment 2).

## Review and approval

- **Approval:** the operator's direction on 2026-09-28 (quoted above) covers increment 1 end to end,
  including the merge to `main`.
- **Independent design review:** `review.md` in this directory.

### Design review R1 resolution (reviewer `ca6119f3`, rubber-duck; 1 Critical, 5 High, 4 Medium)

| # | Finding | Verified | Resolution |
|---|---|---|---|
| 1 | Repository hooks execute repository code (ADR-0008) | yes | Plugin-owned by default; repository hooks opt-in with `--hooks`, recorded in the inventory; Lintel does not enable them |
| 2 | Agent bodies not transformed | yes (45 `/li:`, 36 links) | Agents get body transforms, a preamble, link verification and recorded degradations |
| 3 | Links to unbundled targets | yes (`bin/li-copilot.py:60,71-74`) | Reuse the bundle's public-URL link policy; verify every generated file |
| 4 | PowerShell commands break the POSIX gate and overrides | yes (`_input.sh` tokenizer) | camelCase runtime-name matchers, `LINTEL_HOOK_SHELL`, PowerShell dialect, `$env:` override, dual-dialect tests |
| 5 | CLI-only acceptance | yes | Surface × route acceptance matrix; unrun surfaces stay `conditional` |
| 6 | Event output and fail-open scope | yes | Event × surface table; fail-open scoped to post-launch; launcher and escape-hatch tests |
| 7 | Prompt splice idempotency and parser | yes (host contract) | Top-level tokenizer, sentinel, size caps, batch/resume fixtures |
| 8 | File-presence dedupe; behavior change | yes | Superseded in R2: no cross-origin suppression (both routes run). The evolution entry is marked behavior-changing, with a migration guide |
| 9 | ADR and version timing | yes | ADR-0038 written and accepted in PLAN before BUILD; all four manifests bump to 0.13.0 together |
| 10 | No measurement thresholds | partly (claim was unmeasured) | Measurement gates above |
