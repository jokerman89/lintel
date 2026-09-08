# Release-readiness audit — 2026-09-08

**Scope:** installation, packaging resources, CI, test-runner honesty, generated catalog,
Windows runtime behavior and release acceptance. **Build card:** BC5; requirements R1/R3/R8.
**Branch:** `codex/copilot-enterprise-launch`. **Evidence status:** targeted remediation verified;
final stable-tree aggregate and hosted checks are recorded by BC6, not inferred here.

## Findings and remediation

| Finding | Impact | Disposition and evidence |
|---|---|---|
| CI ran unit/shape and one filtered e2e, but omitted integration and behavior tiers; cross-CLI job was disabled | Security/runtime regressions could merge without executing their tests | Full all-tier Ubuntu/macOS/Windows matrix; strict skip handling; committed adapter, protocol, catalog and wiki drift checks |
| Windows job piped `Test-Path` into Pester `Should` without a Pester setup | Installer verification depended on an undeclared framework | Native `tests/runner/check-install.ps1`, with real install/reinstall and state-preservation assertions |
| Bare installers seeded `_default` identity but did not copy its pack manifest | Installed-only pack resolution failed; old e2e hid this by reading the checkout | Copy the neutral pack only when absent; e2e now sources installed helpers, resolves a field with no hardcoded fallback, and creates/checks an installed Copilot consumer |
| Runtime source trees required by the Copilot adapter were absent from bare installs | Installed adapter could not create a self-contained repository | Copy skills, agents, shims, docs and source metadata alongside bin/lib/templates/scaffolding |
| Bash installer suppressed essential copy failures | Partial install could announce success | Required copies fail visibly; `tests/behavior/install-fail-closed.sh` injects an actual copy failure |
| Required metadata was searched across entire markdown files | Body examples could satisfy missing frontmatter keys | Shared bounded one-pass `lib/frontmatter.sh` plus equivalent PowerShell validation; negative boundary tests |
| Bash installer used `mapfile` despite stock macOS Bash support | Optional upstream listing failed on Bash 3.2 | Portable read loop; full developer suite explicitly uses modern Bash and CI separately exercises installer with `/bin/bash` |
| Installers accepted their source checkout as a destination; Windows replaced managed directories before copying | An accidental self-install could modify or delete source scaffolding | Both installers reject source/ancestor/descendant destinations before writes; Bash canonicalizes nearest existing parents and lexical traversal |
| Existing destination links could redirect copy, seed or permission writes outside the chosen home | Reinstall could overwrite unrelated files through a directory, nested file or dangling profile link | Both installers refuse linked install trees before backups/writes; real native-link regressions assert preserved outside sentinels |
| Installers removed unknown legacy hook directories | Operator custom hooks could be deleted | Preserve legacy/custom inert directories; replace only known managed tree on Windows |
| Runner counted whitespace-prefixed skips as passes, trusted inconsistent per-test tag handling, and ignored invalid flags | Missing coverage or a typo could produce a misleading green run | Central exact tag filtering, malformed-flag failure, empty/all-skipped failure, shell and unittest skip accounting, strict `--require-all`; real runner fixture regressions |
| Catalog workflow wrote timestamped bot commits to main | Non-deterministic output and unreviewed generated commits complicated protected branches | Deterministic stdlib generator with source links and escaping; read-only PR drift checks; source metadata remains authoritative |
| Native Git paths and native jq CRLF crossed into Git Bash consumers | State/audit writes failed on native temp paths; extracted paths and equality tests acquired CR bytes | Normalize native roots in the shared path resolver and use it for auditing; documented `jq -b` in actual consumers; session-trace and hook-input regression passes with official native jq |
| Ship checklist carried obsolete release lines, counts and client acceptance claims | Maintainers could mistake missing client/tenant evidence for release certification | Rewritten checklist uses executable current commands and explicit verified/failed/not-executed acceptance states |

The public scripts are unchanged in identity/version; the package remains a beta. Claude hook
registration remains separate from Copilot. No organization policies, deployments, releases or
marketplace listings were changed by this audit.

## Local verification evidence

Environment: Windows, Git Bash, bundled Python 3.12.14, official jq 1.8.1. jq was downloaded only
into ignored task runtime storage and checked against the upstream SHA256 manifest:
`23cb60a1354eed6bcc8d9b9735e8c7b388cd1fdcb75726b93bc299ef22dd9334`.

Verified targeted checks:

- `tests/runner/check-install.ps1`: install/reinstall, source-checkout refusal, preserved custom
  profile/neutral pack/hook, required installed Copilot assets and dangling-profile-link refusal.
- `tests/behavior/install-target-boundaries.sh`: self/nested/ancestor/root refusal and actual
  native directory, nested-file and dangling-profile symlinks, with no mutation before refusal.
- `tests/e2e/harness-critical-path.sh`: installed-only pack/footer and installed Copilot init/check.
- `tests/unit/test-runner-contract.sh`: malformed input, empty suite, exact tags, shell skips,
  unittest skips and failure propagation.
- `tests/unit/frontmatter-boundaries.sh`, `tests/behavior/install-fail-closed.sh`,
  `install/verify.sh --frontmatter`: bounded metadata and visible incomplete-copy failure.
- `tests/unit/catalog-generator.sh` and `bin/li-catalog.py --check`: deterministic output,
  Unicode, pipe escaping, source links, drift and malformed metadata.
- `tests/integration/session-leaves-traces.sh`, `tests/unit/hook-input-adapter.sh`,
  `tests/integration/security-controls-fire.sh`: state/audit traces, native JSON extraction and
  fail-closed hook behavior after the Windows boundary fixes.

The first attempted baseline was invalidated by editing its executing runner; it supplies no pass
claim. A subsequent intermediate all-tier run discovered 96 scripts: 94 passed, 2 failed. Its
failures were `wiki-gen-idempotency` while that source was still being changed and a reproducible
Windows native-path failure in `session-leaves-traces`. The latter was fixed and reverified above;
BC6 records the stable generator and final aggregate. New tests added during that run are not
included in its count. It is explicitly not final release evidence.

## Remaining acceptance boundary

Required before claiming the complete release verified: run the final stable tree with
`--require-all`, verify generated artifacts after all source edits, inspect hosted CI for the
exact pushed commit, and attach the result in BC6. This Windows environment cannot establish
hosted Ubuntu/macOS success.

Authenticated VS Code, Copilot CLI and cloud-agent work, tenant entitlement, client discovery,
organization policy and marketplace acceptance require separately recorded evidence. Parser or
local plugin-discovery checks may be recorded separately; no paid live-model task or enterprise
policy verification occurred in this audit.

## Source verification

Action revisions were resolved from official releases: [checkout v6.0.2](https://github.com/actions/checkout/releases/tag/v6.0.2)
and [setup-python v6.1.0](https://github.com/actions/setup-python/releases/tag/v6.1.0).
Native jq behavior follows the [jq manual's binary-output option](https://jqlang.org/manual/#invoking-jq);
the local binary came from the [official jq 1.8.1 release](https://github.com/jqlang/jq/releases/tag/jq-1.8.1).
