# P09 data-core review of ea92df8

**Date:** 2026-09-22.
**Selected DATA-CORE SPEC: PASS. Subsequently eligible QUALITY: PASS.**
**Actionable findings: P1 0 / P2 0 / P3 0.**

This accepts only the released data-core second unit, not whole P09, original A09
parents, A17.5, module procedures, installed closure or live specialist behavior.
The accepted 69-role content review is reused, not broadly repeated or superseded.

## Immutable selection and reviewer

| Item | Identity |
|---|---|
| Data-core authority | `3ee602f026486da037844322428a7f1d50728d33`, complete P09 **Data-core second unit** and P09 interfaces section |
| Direct product base | `6581339c0442d11ea070ebf06a707291bbf6132b` |
| Product | `ea92df855bc1e0dfea5c9deb913bdcdf2e5faa8c` |
| Product tree | `b9e3314e32eb3fc2c92b25506923251d5f26aff5` |
| Reviewed report-only child | `53145bd762410cceaadde213fdb3dc435639be8d` |
| Reviewed tree | `c932abad217755d146580de134c408e2a999d66a` |
| Writer report Git blob | `506f6e9f1a21facce47aeeff2d10d56f8992d221` |
| Writer report Git-byte SHA-256 | `aa4b19a0b63fa4f7ddcf1a209a936825340085a2d7f17e649d9e4794c8d5d9c1` |
| Same independent reviewer session | `11c54845-42b2-4fa0-bdbd-16a2f160df05`, Universal specialist review |
| Coordinator | MasterSession, `a9a3c216-633c-43e8-b0c8-c297a7baef07` |
| Preserved prior review | `19eb776018de927691947beb84948347fd2c132d` on `jokerman-microsoft-universal-specialist-review` |
| Prior content integration, not new data-core integration | `4983af2693491d336be3ed9e036742c4589f0cfb` |

Before work, actual HEAD and the preserved branch matched `19eb776`; source/index
were clean. After checking local ancestry, target scope and inactive checkout hooks,
I used a clean **detached** continuation at exact `53145bd`. No branch reset, amend
or old-review overwrite occurred. The data product has the stated sole parent;
its report-only child changes only `reports\P09.md`. The earlier report's entire
319-line prefix is byte-identical. All new code/schema/reference/test bytes are
the frozen product's bytes, not a later working candidate.

This is the original distinct reviewer context, not the builder's self-review.
No nested actor was launched and no source repair was made. Only this report is a
repository deliverable; private synthetic evidence is kept separately. The report
does not fabricate a runtime v2 clearance record or independent-person proof from
actor strings, a model label, synthetic corroboration or a Git author.

## Scope and evidence read

The product changes exactly seven allowed paths: `lib\domain_result.py`,
`lib\domain-result-schema.json`, `bin\li-domain-result.py`,
`skills\full-engineering-pass\references\domain-handoff.md`,
`tests\integration\domain-result-handoff.py`, its `.sh` entry, and the P09 report
append. I read each in full, including all 39 test methods and the full new append.

The mapped requirements and accepted content review remain authoritative. I read
the new authority from immutable `3ee602f` blobs, rather than mistaking the older
P09 card in this deliberately older product branch for a release of P08. Copilot/
Universal review rules and relevant memory/ADRs were retained; ADR-0031 and the
actual accepted P03/P05/P07 implementations were read for the changed links.

The original roles, preservation map, five domain skills/references, shared provider
code/schemas, module/adjacent procedures, P08/core, installers, Swarm and generated
surfaces are unchanged. Selected P03/P05/P07 dependencies also match authority
`3ee602f`. A raw-byte seal covers **976 initially tracked files**, independently
of Git's CRLF projection; all those hashes remained unchanged through review.

## Stage 1: selected data-core SPEC

The rows below are review dimensions, not new work leaves or a competing ledger.
Each PASS is limited to this data unit's released requirement.

| Requirement | SPEC | Concrete source and observed boundary |
|---|---|---|
| One bounded wrapper contract, existing shared definitions | PASS | `lib\domain-result-schema.json:1-125`; `lib\domain_result.py:29-125,157-240`. Domain wrappers stay v1, P05 context/QA v2 and P07 reference v1. P05 objects use its definitions and validators; duplicate/nonfinite JSON and unsupported wrapper fields refuse. |
| Real accepted producer/consumer links | PASS | `tests\integration\domain-result-handoff.py:47-329,667-706,899-913` uses actual P07 context/reference/policy, P05 prepare, data CLI, fresh verification, `verify_qa`, QA CLI and the outer review writer/reader. Fixtures are synthetic; no P08 substitute or task-membership parser is introduced. |
| Original explicit publication preimage | PASS | `lib\domain_result.py:278-307`; `bin\li-domain-result.py:49-84`. The call argument is mandatory, must equal the request's original state, and is passed unchanged to P03's checked atomic writer. Absence is not late overwrite permission. |
| Safe paths, bounded reads and observed readback | PASS | `lib\domain_result.py:118-143,157-192,250-274,310-319`. Portable path checks, metadata/artifact collisions and P03 rooted no-link reads precede publication. Native dangling-link and directory-parent-link negatives preserve outside sentinels; injected readback mismatch is an error, not successful publication or automatic rollback. |
| Data receipts cannot claim verification or release | PASS | `bin\li-domain-result.py:75-84`; `lib\domain_result.py:305-307,362-422`. Syntax/publication receipts say `verification: not_performed`; fresh decisions keep `release_clearance: false` and `review: not_evaluated`. Producer flags and actor labels cannot supply independent acceptance. |
| Live P07 reference and actual required-policy bridge | PASS | `lib\domain_result.py:321-341`. Explicit target/source must match, P07 re-verifies the full reference without create/rebind, and its actual `required_policy` must equal the selected context. Same-mtime drift, missing pin and a forged non-required policy in both contexts refuse. |
| Caller-selected, noncircular final P05 context | PASS | `lib\domain_result.py:321-338`; `skills\full-engineering-pass\references\domain-handoff.md:104-130`. Final preparation is external and after outputs exist; non-snapshot work/profile/attempt/builder/policy/obligations remain equal, base and original selections are retained. Raw result data cannot choose a replacement expected context. |
| Full immutable QA obligations and grounded N/A | PASS | `lib\domain_result.py:157-240,395-410`. Every initial QA obligation is assigned once and immutable fields are compared; P05 evaluates the typed observations. Missing/retyped/downgraded requirements, ungrounded N/A and failed/error/unknown/zero/skipped mandatory observations block. |
| Fresh raw checkpoint/evidence composition | PASS | `lib\domain_result.py:344-422`. All expected checkpoints are enumerated; request/start/result/artifact/evidence bytes must match the final context and recorded digests. `summary` calls the fresh verifier instead of trusting a stored successful verdict. Missing domains/checkpoints cannot hide behind scores. |
| Receiver modes and preferences remain inert | PASS | `lib\domain_result.py:203-240`; reference `:78-102`. Receiver role/mode must match the request and start; both Migrator and ReleaseEngineer mode families remain representable. Neither mode, next-action text nor advisory preferences executes anything or grants authority. |
| Unmapped/advisory and outer review limits | PASS | `lib\domain_result.py:157-170,386-410`; actual P05 `verify_qa`. Unmapped domain data refuses; advisory-only observations cannot become accepted QA. Advisory failures remain visible without becoming mandatory. A later P05 rejection still blocks its outer reader while this helper explicitly does not evaluate review. |
| Preserved history and honest scope | PASS | Exact seven-path comparison, the unchanged 319-line prefix, source seal and separately run unchanged 12-method content checks. No installed, live-role, full-suite, minimum-runtime or parent-completion claim is inferred. |

**Selected DATA-CORE SPEC passed before the QUALITY decision.** This advances the
released data portion of A09.1 and checkpoint/mode evidence relevant to later
A09.2/.5/A17.5. It does not close those original dependency-bound leaves or parents.

## Stage 2: eligible QUALITY

**PASS; P1 0 / P2 0 / P3 0 actionable findings.** There is no source fix list for
this immutable unit.

The helper remains a data producer/consumer, not a scheduler, command runner,
task parser, preference migration or second acceptance authority. The thin CLI
delegates to the same schema/helper, and the helper consumes the accepted shared
validators rather than copying the work/profile/control interpretations. The small
shape reader only handles its declared wrapper subset; it is not presented as a
general-purpose JSON Schema engine.

The strongest boundaries were checked beyond positive test counts: the original
publication preimage survives the full P03 call; fresh verification checks current
P07 policy rather than matching only two supplied policy objects; every raw file is
bound to the caller-selected final context; and composition preserves absent,
negative and advisory observations rather than averaging scores. Errors remain
non-clearing, and source/record receipts do not claim actual domain execution.

Readback corruption and concurrent-stage edits were tested with deliberately
injected local faults. Those tests prove detection/preservation for the named fault,
not cross-process locking, an adversarial filesystem race proof or execution of a
real domain operation. The documented serialized-owner assumption remains explicit.

## Independently executed checks

Actual reviewer environment: Windows, Python **3.11.9**, Git
**2.53.0.windows.4**, Bash **5.3.15(1)-release**. This is not a substitution for the
builder's recorded Git 2.55.0 result or evidence of another OS.

All product execution, including in-process comparison cases, ran inside an
explicit allowlisted synthetic process. HOME/USERPROFILE, temporary/application/
XDG roots and Lintel locations were owned fixture paths; PATHEXT was retained.
Actual P07 configurations were explicit. Fixture Git discovery had owned ceilings;
source checks used separate per-command CRLF handling. Credentials, personal
configuration, shell startup and inherited Python redirects were not passed.
Streams were redirected before each child launch; exits were not taken from a
summary/tail pipeline.

| Check | Exact outcome | Evidence category |
|---|---|---|
| Actual Bash `tests\integration\domain-result-handoff.sh` | Exit 0; **39/39**, zero skips/failures; 175.172 seconds | Changed data core with real accepted providers and CLI/QA/review consumers, synthetic data and actors. |
| Private `adversarial_cases.py` | Exit 0; **9/9**, zero skips/failures; 53.995 seconds | Reviewer-designed cases below, using the actual accepted-producer fixture setup, not replacement validators. |
| Unchanged Bash `tests\behavior\agent-contract-scenarios.sh` | Exit 0; **12/12**, zero skips/failures | Separate documentary/toy content preservation; not native role behavior. |
| Syntax/identity guards | Exit 0 | Exact seven paths, sole parent/report-only child, unchanged providers/content, raw source seal, executable CLI/runner modes and `git diff --check`. |
| Python 3.9 grammar for helper/CLI/new Python test | Parsed on Python 3.11.9 | Grammar only; no actual Python 3.9 execution. |
| Owned fixture Git-discovery probe | Exit **128**, expected refusal; zero stdout | Isolation negative, not relabeled as exit 0. |

### Reviewer-designed additional cases

| Case | Observed result |
|---|---|
| R01: forge non-required policy identically in initial and final contexts | Fresh summary blocks on the **actual live P07 bridge**, with `review: not_evaluated` and no release clearance. |
| R02: unmapped request, then mapped advisory-only inventory | Unmapped validation refuses; advisory-only fresh composition cannot produce accepted QA because no required applicable validation exists. |
| R03: real symlinked publication **directory parent** | Publication refuses; the owned outside sentinel remains unchanged and no external result file is written. This supplements the supplied dangling-file-link case. |
| R04: inject corrupt bytes immediately after P03 publication | Readback raises an explicit error; corrupt observed bytes are preserved for inspection, no success receipt or automatic rollback, and no abandoned staging file. |
| R05: integer zero for false, Boolean iteration, nested duplicate keys, nested infinity | CLI exits 2 without success output, traceback or domain publication. |
| R06: unchanged N/A obligation but missing grounding evidence | Freshly prepared context does not make it grounded; required acceptance remains blocked. |
| R07: stale evidence plus embedded `expected`/`verified` fields in the result | Fresh summary cannot replace the separately selected caller context; no QA is returned, and that context's bytes remain unchanged. |
| R08: evidence larger than 16 MiB, with new recorded digest and fresh P05 preparation | Domain evidence byte bound still blocks; a refreshed context does not waive it. |
| R09: missing direct-API expected-state argument; then an intervening file and late-read state | The missing argument cannot publish; supplying the newly read state instead of the pinned original state refuses and preserves the intervening bytes. |

The supplied 39-method suite additionally exercised unchanged live neutral pin,
immutable QA kind/policy/applicability, missing extra checkpoints, high-score
mandatory failures, selected-file drift/additions, wrong profile target/generation,
lost pin without bootstrap, original owned-preimage replacement, atomic-stage
late edits, failed publication, wrong request/start/producer/mode and actual later
P05 rejection. Negative child exits are retained in their logs as refusals, not
represented as successful product actions.

## Persistent evidence and preservation

The private session artifact root is `files\p09-data-review\`; `logs` stores exact
argv, environment, timestamps, exits and stream hashes. Nine added cases retain
their child evidence under `adversarial-children`. The independently invoked
existing suite retained child logs under the owned gitignored
`.claude\runtime\p09-data-core\6abab81c194c`; that is not an installed consumer.

| Evidence artifact | SHA-256 |
|---|---|
| `source-seal.json` | `a30d4aff3ad0cf5493ae85bd60f10eb99b460a515006c5a1c62dae70821252f5` |
| `verification-ledger.json` | `492722138325f80f2b9066daec6c1c285dabe89c598f92b37c5c8ae6f2d807d1` |
| `adversarial_cases.py` | `7010d43deda057071c2e956ef35a11dda753a9a47200860e0b733769e558315f` |
| `data_review_runner.py` | `9eb796a64ed89d108736a9d0691a886c6d4727342ec5bd265ebd5ce7a61af26c` |
| `logs\data-core.stderr.log` | `f68cf078d76b70ba24b1b80fa9a552d1b65111106a7baf844a575f6bbc135460` |
| `logs\adversarial-v1.stderr.log` | `204f910068de95696b8e8ab3d4e31f76d5083d636aa2f737f78e5f78dbf128ab` |
| `logs\retained-content.stderr.log` | `2598f31ef42fcc539afe6be33fbd225184157d40deafac7e676596837052de2f` |
| `quality-guards.stdout.log` | `13e9214f45cb2dc44ecc8c6eb452c19bf01ae45086b0142731e8707acf63193d` |

The independently read Git bytes match the three core product hashes:

| Product path | SHA-256 |
|---|---|
| `lib\domain_result.py` | `3ccd4266ac597b57eb108dad78c9b466b9182faa848f07ef6a080218e2e2da61` |
| `lib\domain-result-schema.json` | `fef5937bdb52d3b54a7c75b57b19d19a5c863c35075ab8d775766b155e9a9bbd` |
| `bin\li-domain-result.py` | `357ba58c8f29f63af153ac74be6c7ef10c6eede890029c8447c11ef814e1ae7a` |

The writer's initial missing-CLI RED and `ProfileError.code`-wrapper failure remain
failed historical runs in its untouched append; its earlier 29/37-method runs are
not relabeled as the final 39. Prior content RED/private-launcher/EOL history and
both prior writer reports remain intact. No dependency was installed and no test
was skipped or replaced merely to obtain a pass.

## Deferred acceptance and handoff

The following boundaries remain open and are not waived:

- A09.1/.2/.5 and A17.5 original/dependency-bound acceptance; accepted P08 work
  identity/grouping/iteration/resume semantics and actual module/adjacent procedures.
- Actual installed-resource/preflight closure with coordinator/P10. Copied-source
  conflict/missing-helper tests prove that scoped refusal, not installation.
- Actual native role invocation, receiver behavior, independent-person review
  corroboration and semantic domain correctness. Role/mode/actor strings and
  synthetic P05 corroboration are data, not host or human identity proof.
- Full long-root Git/context or installed behavior. The actual 290-character
  publication/readback is only data I/O/syntax evidence at its original location.
- P11 design/browser and P12 document consumers; full suite, live hosts, other OSes
  and actual Python 3.9 runtime. No such result follows from this unit.

Recording stale-profile observations is explicitly **non-clearing storage**, not
permission to act on them. Fresh verification and the outer independent-review
gate are still required at their respective boundaries. A complete data summary
does not complete a phase/task, select a new policy, authenticate its producer or
authorize a release.

Accept the exact data-core unit for coordinator intake. No actionable repair is
requested; the original P09 builder remains the sole repair/continuation owner.
This report is the only new repository deliverable and is committed directly on
exact `53145bd`, with the required Copilot trailer. Its immutable commit/parent/
report hash and final clean/source-seal status are returned separately, avoiding
a self-hash. The old review branch/report remain preserved.

No source repair, shared-ledger/generator edit, personal/customer-data or actual-home
incident inspection/cleanup, global setting/policy change, authenticated/network
GitHub operation, push, PR, amend, reset or main action occurred. After the immutable
handoff, this reviewer stops read-only.

**Lifecycle position:** SENSE -> SCOPE -> DEFINE -> DISCOVER -> PLAN -> BUILD ->
REVIEW -> SHIP -> CAPTURE. This is selected data-core REVIEW; resume is a utility
and no broader lifecycle or delivery completion is implied.
