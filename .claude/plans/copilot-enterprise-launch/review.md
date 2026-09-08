# Review: Copilot enterprise launch

**Candidate scope:** all changes on `codex/copilot-enterprise-launch` after `6b10a84`.
**Stage 1 — specification:** PASS after corrections.
**Stage 2 — correctness/security:** PASS after corrections.
**Ship readiness:** local candidate PASS; ready for feature push and PR checks. Main integration waits for hosted checks.

## Review coverage and resolved findings

Runtime, workflow/distribution, public documentation and release tooling received independent
specification review followed by correctness/security review. The review artifacts preserve the
original findings and the evidence that closed them:

- [Copilot adapter](../../engineering/audits/2026-09-08-copilot-runtime.md): portable source,
  safe inventory/ownership, path boundaries, complete startup protocol and no-executable-bit consumers.
- [Specification review](../../engineering/audits/2026-09-08-copilot-spec-review.md): original
  Spec Kit task ownership, explicit work mapping, fresh-clone resume and effective runtime ignore.
- [Release tooling](../../engineering/audits/2026-09-08-release-readiness.md): fail-closed installers,
  source/destination and symlink boundaries, runtime resources, skip accounting and CI coverage.
- [Public surface](../../engineering/audits/2026-09-08-public-surface.md): truthful capability,
  install, security and enterprise-adoption claims; 264 local file links and 15 heading links verified.
- [Protocol coverage](../../engineering/audits/2026-09-08-session-protocol-coverage.md): every
  personal startup section has an explicit reusable or personal-only disposition; no personal machine
  state or marketplace grants were copied into shared policy.
- [Workflow contracts](../../engineering/audits/2026-09-08-workflow-contracts.md): native plugin
  metadata, source/project path separation, deterministic generators and committed work mapping.

The compatibility-audit tool itself was repaired after review showed that staged or committed
frontmatter changes could be missed. One comparison range now drives all questions; invalid/empty
refs and output traversal fail before producing a report. Real Git fixtures cover these cases.
[Mechanical M2 and reviewed disposition](../../engineering/compat-audits/2026-09-08-copilot-enterprise-launch.md)
retain the detector's raw result rather than presenting broad shared-helper changes as unexamined green.

## Candidate evidence

- Copilot adapter integration: 19 tests passed, zero skipped; root inventory check: 18 managed files.
- Startup protocol parity: four entry files checked; empty-home consumer and surrounding-content preservation tested.
- Native PowerShell install/reinstall, Bash source/link boundaries and installed-only consumer tests passed.
- Repository structure `install/verify.sh --all`: PASS.
- Staged diff whitespace check: PASS. Added-line credential-pattern scan: no findings; staged paths
  exclude runtime storage and the pre-existing local settings file. This is a scoped check, not certification.
- Complete stable suite: `bash tests/runner/run-all.sh --require-all` — **101/101 passed, 0 skipped, 0 failed, 0 partial**. Catalog, protocol, adapter and wiki drift checks, plus Bash/Python syntax, passed. Exact-commit hosted CI is recorded below after execution.

## Acceptance boundary

GitHub Copilot CLI 1.0.83 locally loaded the explicit native plugin format and discovered all 13
project skills. This is parser/discovery evidence, not an authenticated workflow test. A proposed
read-only model smoke test has not executed; it requires explicit authorization for transfer of the
generated test-project instructions to GitHub Copilot. VS Code, cloud-agent and enterprise-tenant
acceptance remain not executed. See the public rollout checklist for those environment-specific checks.

The release remains version 0.9.0 beta. No release/tag, marketplace listing, production deployment,
organization-policy change or formal compliance claim is included. Main integration and repository
presentation updates are explicitly authorized by the operator's initiative request.
