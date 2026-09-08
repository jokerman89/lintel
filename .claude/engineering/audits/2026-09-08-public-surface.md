# Public surface audit — GitHub Copilot adoption

Date: 2026-09-08. Scope: README, public docs, contribution/security/community policies,
release notes and generated showcase/reference surfaces. Voice: internal.

## Findings before changes

| Priority | Finding | Resolution |
|---|---|---|
| P1 | README and onboarding center Claude Code; Copilot IDE is explicitly excluded. | Copilot-first portable repository onboarding, with a separate optional CLI plugin path. |
| P1 | Copilot is described as lacking skills, custom agents or hook capability in multiple public pages. | Distinguish current host capabilities from Lintel's actual adapters; native repository skills/agents, no claimed Lintel hook port. |
| P1 | Guaranteed secret prevention, unavoidable workflow gates and no-network claims exceed implementation. | Describe pattern scanning, cooperative workflow instructions, opt-in execution, bypass boundaries and external controls. |
| P1 | SECURITY.md calls 5.7.x current and promises fix SLAs without operational evidence. | Match beta version and best-effort maintenance; direct private reporting route. |
| P1 | “Only original code/no third-party licenses” contradicts design-dna attribution and vendored assets. | Preserve MIT core and link retained third-party notices. |
| P2 | No enterprise pilot, ownership, change management, rollback or evidence criteria. | Dedicated enterprise adoption guide with a measurable pilot and reviewable repository rollout. |
| P2 | No Spec Kit workflow contract; running both planners can produce divergent task state. | Optional interoperability bridge; existing Spec Kit artifacts remain authoritative, one executor. |
| P2 | Duplicate manually maintained capability tables and inventory counts drift. | Link the single generated README table/catalog; avoid repeating changing totals in prose. |
| P2 | Showcase documentation claims an older date/count than the committed generated HTML. | Describe generation contract without hardcoded snapshots; regenerate via owning generator. |

## Primary-source verification

Checked on 2026-09-08; these are host capabilities, not evidence of a live Lintel session:

- [GitHub agent skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills): repository skill discovery includes `.github/skills`; names are lowercase hyphenated identifiers.
- [GitHub CLI customization](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/overview): custom agents and skills are supported.
- [GitHub hooks](https://docs.github.com/en/copilot/concepts/agents/hooks): CLI/cloud hooks exist; their JSON contract is separate from Claude Code's contract.
- [Spec Kit core](https://github.github.com/spec-kit/reference/core.html): current initialization uses `--integration copilot`; inspect installed `--help` for version compatibility.
- [Spec Kit integrations](https://github.com/github/spec-kit/blob/main/docs/reference/integrations.md): Copilot defaults to skills under `.github/skills/speckit-*`; command layout is an explicit integration option.

## Delivery contract

Copilot repository kit: `bash bin/li-copilot init|check --target PATH [--source PATH]`;
portable resources under `.github/lintel/`; generated native `li-*` skills and custom
agent profiles; preserve existing files and require reviewed diffs for adoption. Lintel
Claude hooks are not advertised as Copilot hooks. Keep 0.9.0 beta positioning until
release evidence warrants a different status. Existing historical release notes stay intact.

Validation is reported in the build plan/review record by the parent workstream. Static
checks and hermetic integration tests must not be described as an authenticated Copilot pilot.

## Completed verification

- Public Markdown local-link scan: 244 existing local targets checked, zero missing (before the additive session-protocol documentation changes).
- `tests/shape/no-swedish.sh`: PASS with complete Git Bash coreutils PATH. An earlier invocation without coreutils was discarded as invalid evidence.
- Session protocol generator parity and mutation-boundary tests: PASS; full-source and consumer reviews remain separate.

## Final public-surface review

Reviewed the latest installer, native entry points, protocol factory and explicit work-map
contract against the public guides. Corrected the checkout-local `li-scaffold --copilot`
prerequisite, documented additive scoped instructions and managed protocol blocks, and
replaced one obsolete historical changelog navigation target without rewriting history.
No generated files or implementation scripts changed during this final pass.

- Public documentation and startup-entry link check: 264 local file targets and 15 heading
  targets, zero unresolved targets.
- In-memory consumer factory: all generated resource links resolve; both startup entries
  contain the complete canonical protocol without personal-machine links. Both scaffold
  templates use supported render tokens. This checks generated content, not a live client.
- `bin/li-instructions.py check`: PASS in all four maintained startup entries.
- Parent-observed GitHub Copilot CLI 1.0.83 discovery: `--plugin-dir .` enumerated all 13
  project skills. A native-format-only fixture also discovered its probe skill without a
  Claude plugin manifest. This establishes local parser/discovery compatibility only.
- Authenticated model task execution was not performed in this review. IDE discovery,
  agent behavior, organization policy and tenant-specific acceptance remain pilot evidence.

No remaining actionable documentation mismatch was found in this pass. The live-client
acceptance checklist is maintained in [the Copilot guide](../../../docs/copilot.md#live-client-acceptance-before-rollout):
record client/version/policy/revision, verify discovery, run one bounded plan/build/review,
resume from committed artifacts in a fresh session, and verify the intended platform
controls. The documented release remains 0.9.0 beta; local contract checks and CLI discovery
do not establish an enterprise compliance guarantee or completion of a 1.0 launch.
