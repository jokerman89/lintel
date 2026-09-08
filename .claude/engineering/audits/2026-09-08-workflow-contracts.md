# Workflow and distribution audit — 2026-09-08

Scope: canonical skills, capability metadata, plugin descriptors, planning templates, generated
reference material and GitHub public repository metadata. Build card BC3; voice: internal.

## Findings and changes

| Severity | Finding | Implemented resolution |
|---|---|---|
| P1 | Copilot metadata claimed no subagents; nearly all core skills omitted Copilot support. | Native delegation capability, host alias normalization and reviewed core skill declarations; full tier withheld pending live acceptance. |
| P1 | Claude plugin fallback would expose incompatible hook configuration and non-native role formats to Copilot. | Explicit .github/plugin manifest targeting native adapters, plus a versioned empty Copilot hook configuration. |
| P1 | Canonical BUILD asserted hooks fire without checking the host and assumed exact Claude tools/models. | Conditional controls and explicit host operation/model mapping; no fabricated hook enforcement or delegation. |
| P2 | Spec Kit had no ownership bridge into Lintel execution. | Native li-spec-kit adapter and canonical bridge keep original spec/plan/tasks authoritative, with path references and task evidence. |
| P2 | Plan template requested invented dollar estimates despite the planner prohibiting them. | Phase/task/token signals with explicit calibrated/uncalibrated basis. |
| P2 | Repeated approval prompts ignored existing user authorization. | Record scope authorization, surface reviewable plan, ask only for a new material decision or authority boundary. |
| P2 | Public descriptors advertised eight steps, fixed context size and a neutral-pack mode that did not exist. | Nine-step descriptions, model-budget wording and a valid internal-tool example. |
| P1 | Wiki --check compared mismatched absolute roots, used live timestamps and could not enforce advertised drift guarantees. | Stable generated headers, temporary output comparison, read-only drift result, CRLF-safe frontmatter parsing and real regression coverage. |
| P2 | README capability-table generation was promised but not implemented in the wiki generator. | Generator now writes the marked section from lib/cli-tiers.yaml; integrity test rejects drift. |
| P2 | Structured CLI metadata produced blank support columns in generated references. | Parse both inline and structured cli_support declarations. |
| P2 | GitHub About still included company-specific legacy positioning. | Applied and read back the neutral Copilot-first About description and five relevant discovery topics on GitHub. |

## Client evidence

GitHub's official npm package `@github/copilot@1.0.83` was installed in isolated, gitignored
local test storage. Node version: 24.16.0. No user-global Copilot installation or credentials
were modified. COPILOT_HOME and COPILOT_CACHE_HOME pointed at isolated test directories;
auto-update was disabled.

Commands and observed output:

```text
copilot --version
GitHub Copilot CLI 1.0.83.

copilot --plugin-dir . plugin list
External Plugins (via --plugin-dir):
  • li
```

This proves local external-plugin loading by that client. It does not prove authenticated
model execution, native skill invocation, tenant policy, VS Code UI or cloud-agent behavior.
The release checklist keeps those acceptance categories separate.

## Verification

Targeted Copilot alias/capability test passed. The strengthened existing wiki idempotency test
covers stable regeneration, deliberate drift, no rewriting during check, CRLF source metadata,
structured CLI declarations and generated Copilot capabilities. Final full-suite and independent
review outcomes are recorded in the launch plan review rather than predicted here.

## Findings resolved during independent review

The first spec review rejected a prose-only Spec Kit bridge: canonical BUILD still required native plan approval/headings and task storage. The repaired workflow uses a committed work.json with one validated spec/design/tasks/handoff mapping. PLAN, BUILD and REVIEW consume original Spec Kit artifacts; RESUME selects committed work when local runtime state is absent. The helper rejects missing and escaping paths. Native plans use the same map without a second task file. A focused test exercises both modes without a local ledger.

Canonical source-helper examples now prefer LINTEL_SOURCE_ROOT for bin/lib reads while preserving LINTEL_REPO_ROOT for project output. This removes the need for a first-time Copilot session to reinterpret a broken literal source path.
