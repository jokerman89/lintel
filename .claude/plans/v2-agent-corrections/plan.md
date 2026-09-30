# Plan: V2 agent-method corrections

**Status:** APPROVED within the precise compatible thirteen-item grant.
**Specification:** [spec.md](spec.md). **Work map:** [work.json](work.json).

## Scope and profile

One existing writer, thirteen original mapped items, one package; phases are
source correction, scoped verification and frozen implementation handoff.
The M whole-cycle default prior is 30,000 tokens, uncalibrated, not measured cost.
No new actor, model or factory is planned.

A new target-local P07 resolves the actual neutral `_default` 1.0.0:
required policy `not_required`, source `bundled-neutral`, applicability
`not_applicable`, advisory compliance and no hooks. Literal roots and full
reference are private evidence; no previous profile or clearance is reused.

## Work package

| Package ID | Outcome | Leaf IDs (dependency order) | Owner / edit boundary | Dependencies | Acceptance evidence | Review |
|---|---|---|---|---|---|---|
| V2-agent-methods | Compatible, evidence-bounded methods for the exact original agent items | V2A01, V2A02, V2A03, V2A04, V2A05, V2A06, V2A07, V2A08, V2A09, V2A10, V2A11, V2A12, V2A13 | existing writer; agents/engineering/AccessibilityChecker.md, agents/engineering/APIDesigner.md, agents/engineering/CodeReviewer.md, agents/engineering/DatabaseDesigner.md, agents/engineering/DebugForensics.md, agents/engineering/SanityChecker.md, agents/security/PrivacyBoundaryAudit.md, agents/security/SecretsScanReviewer.md, agents/security/SecurityAuditor.md, agents/security/ThreatModelDrafter.md, agents/devops/DevOpsToolchain.md, agents/devops/K8sManifestReviewer.md, agents/devops/TerraformReviewer.md, tests/behavior/v2-agent-methods.py, tests/behavior/v2-agent-methods.sh | none | per-item source clauses, discriminating inert fixtures and frozen hashes | substantive |

## Original-item progress

- [x] V2A01 Require scoped accessibility observation.
- [x] V2A02 Discover actual API consumers.
- [x] V2A03 Bind review to original acceptance.
- [x] V2A04 Separate schema design and migration sequencing.
- [x] V2A05 Preserve forensic handoff state.
- [x] V2A06 Bound and prioritize cross-component review.
- [x] V2A07 Ground privacy findings in supplied flows and policy.
- [x] V2A08 Keep secret triage inert and redacted.
- [x] V2A09 Add defensive authorization and agent-tool review methods.
- [x] V2A10 Assign threat dispositions, owners and verification.
- [x] V2A11 Keep infrastructure implementation target-specific.
- [x] V2A12 Review selected PSS and workload permissions.
- [x] V2A13 Review resource-address transitions statically.

## Card detail

Each leaf maps to its original path/index and acceptance row in spec.md. The same
writer owns its named agent file and the corresponding cases in the two new
fixture files; no shared test harness changes. All are independent within this
sequential package. Verification is the matching case in the new wrapper, plus
metadata/notice/ownership checks. A source read alone never completes a leaf.

### V2A01: Accessibility
**Files:** `agents/engineering/AccessibilityChecker.md`
**Dependencies:** none
**Acceptance:** spec V2A01; failed static semantics/alpha contrast do not imply executed keyboard or AT coverage.
**Verification:** `AgentMethodCases.test_accessibility` passed in the scoped documentary run.

### V2A02: API
**Files:** `agents/engineering/APIDesigner.md`
**Dependencies:** none
**Acceptance:** spec V2A02; strict/tolerant consumers retain separate version-specific outcomes.
**Verification:** `AgentMethodCases.test_api_consumers` passed in the scoped documentary run.

### V2A03: Code review
**Files:** `agents/engineering/CodeReviewer.md`
**Dependencies:** none
**Acceptance:** spec V2A03; verification-only work remains incomplete without actual acceptance evidence.
**Verification:** `AgentMethodCases.test_code_review` passed in the scoped documentary run.

### V2A04: Database
**Files:** `agents/engineering/DatabaseDesigner.md`
**Dependencies:** none
**Acceptance:** spec V2A04; large-table NOT NULL work retains reader/writer, lock, backfill and sequencing obligations.
**Verification:** `AgentMethodCases.test_database` passed in the scoped documentary run.

### V2A05: Forensics
**Files:** `agents/engineering/DebugForensics.md`
**Dependencies:** none
**Acceptance:** spec V2A05; prior observations and an interrupted owned trial survive a fresh-context handoff.
**Verification:** `AgentMethodCases.test_forensics` passed in the scoped documentary run.

### V2A06: Sanity
**Files:** `agents/engineering/SanityChecker.md`
**Dependencies:** none
**Acceptance:** spec V2A06; material cross-component mismatch outranks naming preference and sampling is explicit.
**Verification:** `AgentMethodCases.test_sanity` passed in the scoped documentary run.

### V2A07: Privacy
**Files:** `agents/security/PrivacyBoundaryAudit.md`
**Dependencies:** none
**Acceptance:** spec V2A07; policy P-7 plus forbidden telemetry is a source gap, unknown backup and provider brand are not confirmed leaks.
**Verification:** `AgentMethodCases.test_privacy` passed in the scoped documentary run.

### V2A08: Secrets
**Files:** `agents/security/SecretsScanReviewer.md`
**Dependencies:** none
**Acceptance:** spec V2A08; report contains no value/fragment and lacks live-validation/history-rewrite advice.
**Verification:** `AgentMethodCases.test_secrets` passed in the scoped documentary run.

### V2A09: Security
**Files:** `agents/security/SecurityAuditor.md`
**Dependencies:** none
**Acceptance:** spec V2A09; static evidence distinguishes constants from untrusted flow and covers tenant/tool authority with repair-oriented controls.
**Verification:** `AgentMethodCases.test_security` passed in the scoped documentary run.

### V2A10: Threats
**Files:** `agents/security/ThreatModelDrafter.md`
**Dependencies:** none
**Acceptance:** spec V2A10; every boundary threat has evidence, disposition, owner and verification; no unsupported risk multiplication.
**Verification:** `AgentMethodCases.test_threats` passed in the scoped documentary run.

### V2A11: DevOps
**Files:** `agents/devops/DevOpsToolchain.md`
**Dependencies:** none
**Acceptance:** spec V2A11; authorized artifact diffs do not authorize workflow triggers, credentials or provider choices.
**Verification:** `AgentMethodCases.test_devops` passed in the scoped documentary run.

### V2A12: Kubernetes
**Files:** `agents/devops/K8sManifestReviewer.md`
**Dependencies:** none
**Acceptance:** spec V2A12; supplied PSS/RBAC and resource semantics drive findings rather than an invented quartet or ratio.
**Verification:** `AgentMethodCases.test_kubernetes` passed in the scoped documentary run.

### V2A13: Terraform
**Files:** `agents/devops/TerraformReviewer.md`
**Dependencies:** none
**Acceptance:** spec V2A13; address rename risk is visible, tested module minimum constraint is not automatically a defect, and no live command is run.
**Verification:** `AgentMethodCases.test_terraform` passed in the scoped documentary run.

## Review and handoff

Independent review is assigned by Master after implementation freezes; no actor
is spawned by this lane. Capture a per-item correction/already-satisfied-clause
matrix and exclusions, exact source/test hashes, actual fixture receipts and
current P07. An ordinary local commit is allowed after scoped checks, using the
normal configured Git identity outside the synthetic test environment. No amend,
reducers, publication, broad-program closure or old-worktree mutation.

### Local implementation evidence

All thirteen compatible source corrections are implemented. The single new
`tests/behavior/v2-agent-methods.sh` wrapper ran 15 tests with zero failures or
skips: thirteen method/report-example cases and two metadata/link checks.
Each worked report is checked against its specific fixture outcome and against
mutations that overclaim a pass, omit coverage or omit evidence. Contrast and
inert-value redaction are also checked mechanically. These are documentary and
synthetic report contracts, not generated model replies or live detection tests.

The initial thirteen-item red result and a subsequent case-sensitive heading
match failure are retained. The clause matcher was made case-insensitive; no
expected disposition or acceptance value was weakened.

The source check verified original item/index mapping, all names/tools/model/
memory/discovery fields, scoped relative links, original notice retention,
Python 3.9 syntax and a current distinct P07 with unchanged policy/home.
Only the two authorized trigger descriptions changed in frontmatter.
The other lane's shared behavior harness and review-method tests are byte-unchanged.

Private evidence under `.claude/runtime/v2-agent-corrections/` contains exact
commands, log/source hashes, the unchanged original selection, item-specific
implemented/already-satisfied clauses and explicit exclusions. In particular,
the REVIEW skill's privacy versus object/tenant authorization routing was
already correct on the base and was not edited.

### Review boundary

The implementer checked scope, source contracts and results; this is self-review,
not an independent decision. Master assigns the existing independent reviewer
to the frozen implementation. Generated native adapters/catalog/wiki and final
suite-count reduction remain Master-owned; no native consistency or hosted PASS
is claimed before those steps. Runtime verification here is Windows/Python
3.11.9, with Python 3.9 syntax only. All broader V2, release and policy gates remain
open outside these completed implementation checkboxes.
