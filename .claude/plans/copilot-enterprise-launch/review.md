# Review: Copilot enterprise launch

**Candidate scope:** all changes on `codex/copilot-enterprise-launch` after `6b10a84`.
**Stage 1 — specification:** PASS after corrections.
**Stage 2 — correctness/security:** PASS after corrections.
**Repository delivery:** COMPLETE — exact-head hosted CI passed; PR #83 merged to main on 2026-09-08. Environment-specific beta acceptance remains bounded below.

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
- Complete stable suite: `bash tests/runner/run-all.sh --require-all` — **101/101 passed, 0 skipped, 0 failed, 0 partial**. Catalog, protocol, adapter and wiki drift checks, plus Bash/Python syntax, passed.

## Hosted verification and integration

The reviewed implementation head is `da938538972e49d214a7188e99cbc2c159bbefa5`.
[CI run 34231756229](https://github.com/jokerman89/lintel/actions/runs/34231756229) and
[catalog run 34231756018](https://github.com/jokerman89/lintel/actions/runs/34231756018)
both completed successfully for that exact commit before integration.

| Platform | Complete suite | Installation and generated artifacts |
|---|---|---|
| [Ubuntu](https://github.com/jokerman89/lintel/actions/runs/34231756229/job/102079379676) | 101 passed; 0 skipped, failed or partial | All checks passed |
| [macOS](https://github.com/jokerman89/lintel/actions/runs/34231756229/job/102079379544) | 101 passed; 0 skipped, failed or partial | Stock Bash 3.2 install and all drift checks passed |
| [Windows](https://github.com/jokerman89/lintel/actions/runs/34231756229/job/102079379671) | 101 passed; 0 skipped, failed or partial | Native PowerShell install/reinstall and all drift checks passed |

Shell/Python syntax also passed. Hosted testing exposed locale-dependent wiki ordering and
Windows test subprocess selection; both were repaired and independently reviewed before this
final green run. No assertions were removed or skips introduced to close those findings.

[PR #83](https://github.com/jokerman89/lintel/pull/83) merged on 2026-09-08 at 13:36 UTC as
`52c7b3857f86fb7d118c9f2811cc914f667b1150`; local main fast-forwarded to the remote merge.
The two pre-existing local commits `017dc24` and `6b10a84` remain in its ancestry unchanged.
All seven build cards and 31 leaves are complete. This documentation closure records the
verified implementation and merge; subsequent documentation commits receive normal main CI.

GitHub About and topics now reflect the Copilot-first session workflow. Public documentation,
enterprise rollout guidance, security boundaries and the complete startup protocol were updated
with the code. Historical plans and old publication instructions are explicitly superseded as
current assignments; the completed work map must not trigger another execution of this batch.

## Acceptance boundary

GitHub Copilot CLI 1.0.83 locally loaded the explicit native plugin format and discovered all 13
project skills. This is parser/discovery evidence, not an authenticated workflow test. A proposed
read-only model smoke test has not executed: automatic approval review blocked transfer of the
generated test-project instructions to GitHub Copilot pending specific operator authorization.
The optional approval question remains unanswered. VS Code, cloud-agent and enterprise-tenant
acceptance remain not executed. See the public rollout checklist for those environment-specific checks.

The release remains version 0.9.0 beta. No release/tag, marketplace listing, production deployment,
organization-policy change or formal compliance claim is included. Main integration and repository
presentation updates are explicitly authorized by the operator's initiative request.
