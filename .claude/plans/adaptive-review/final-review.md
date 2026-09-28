# Adaptive review: bounded final source re-review (recovery)

**Verdict at the current freeze `f01294db`: LOCAL SOURCE only. SPEC PASS. QUALITY PASS.
No open P1, P2 or P3.** At the earlier freeze `17f70f52`, the verdict was SPEC PASS and
QUALITY PASS with one P3 (P3-1, now fixed; see the recheck below).
This is not P05 shared clearance, QA, current-main acceptance, native1a acceptance,
patterns-stack acceptance or release clearance (`release_clearance: false`).

## Scope and identity

- **Exact freeze:** `f01294db59f4d6ca13d9c43745ef0df6c014f983`, a successor to
  `17f70f52c38fad751bc61e651f02fbe8e5cb2b41`, on branch
  `jokerman-microsoft-adaptive-review`. Original baseline `49f2d152`.
  - The first pass reviewed `d8dd2d57..17f70f52` (9 files, +219/-22) and the APIs
    around it.
  - The recheck reviewed only `17f70f52..f01294db` (3 files, +17/-1).
  - `git diff --quiet f01294db -- bin lib skills tests .claude/decisions` returned 0,
    so the product files match the freeze exactly.
  - The only local changes are the coordinator's uncommitted
    `.claude/memory/working-state.md` and `plan.md`, plus untracked plan and evidence
    files.
- **Coordinator:** `d9057650-8028-439a-85da-5849b5470136`.
- **Reviewer context, as far as I can observe it:** a Copilot CLI session started
  for this bounded recovery check, working in the `jokerman-microsoft-vigilant-waddle`
  worktree checkout of the branch above. I cannot see my own host session ID from
  inside this context. The handoff names `010f0e08-076c-4683-8b28-1146251104be` as the
  recovery reviewer, but I can't confirm from here that this session is that ID. This
  context did not write `17f70f52`, `f01294db` or any product file, and it edited nothing except
  this report. That makes this pass independent of the implementer only to the extent
  the host's session separation holds, and the human review gate stays in place.
- **History I am replacing, not inheriting:** final reviewer
  `08b772fd-f505-45b0-b12f-16ef18ee9378` gave SPEC PASS for the T7-T12 source and
  QUALITY CHANGES REQUESTED with one P2: a saved MARS method replaced with
  legacy v1, deleted or non-dict metadata could skip the mandatory inventory. Its
  recheck was interrupted, the agent is no longer found, and it wrote no file. I
  carry over no PASS from it. That P2 is recorded below as **fixed at `17f70f52`**,
  and the history is kept.
- **Not re-audited, by instruction:** the P1 source (`0993b682`, `c849f9a7`,
  independent: 35 tests, spec/quality PASS), the P2 source (`d6c6f277`, independent:
  38 tests, spec/quality PASS after the malformed-ID fix), benchmark, provider,
  native and remote work.

## Findings

| Severity | Count | Status |
|---|---|---|
| P1 | 0 | none |
| P2 | 0 open (1 historical, **fixed** at `17f70f52`) | Prior MARS metadata downgrade, closed below |
| P3 | 0 open (1 historical, **fixed** at `f01294db`) | P3-1 was found at `17f70f52` and fixed by the coordinator, not by this reviewer |

### P3-1 (FIXED at `f01294db`; original finding at `17f70f52` kept below): `panel origin --subject-ref` is silently ignored for panels created with a relative brief

`lib/mars_contract.py:283-284` now stores `brief_path` as an absolute path, but the
default `ref` is still the brief path exactly as the caller supplied it. The override
guard at `bin/li-mars.py:179` compares `ref` against the absolute `brief_path`. For a
new panel created with a relative `--brief` and no `--subject-ref`, a later
`panel origin --subject-ref X` exits 0 and leaves `ref` unchanged.

Synthetic probe, same commands at each revision:

- `49f2d152`: `ref=docs/real-subject`
- `17f70f52`: `ref=brief.md`

The only effect is that `subject_ref` in request and synthesis headers shows the
brief path instead of the intended subject. Integrity, obligations and clearance
are unaffected. Workarounds: pass `--subject-ref` at init, or use an absolute
`--brief`. A possible fix, which I have not applied, is to also accept
`ref == Path(brief_path).name`-style defaults, or to record whether the default `ref`
was used.

**Recheck at `f01294db` (bounded to the delta `17f70f52..f01294db`): FIXED.**

- `new_panel` (`lib/mars_contract.py:284`) adds one display-only field,
  `subject.brief_ref`: the brief spelling exactly as supplied. `brief_path` stays
  absolute and `brief_sha256` is unchanged.
- The origin guard (`bin/li-mars.py:179-181`) treats a `ref` that is absent, equal to
  `brief_path` or equal to `brief_ref` as the initial default. It keeps any other,
  explicit ref.
- Nothing reads `brief_ref` apart from that guard. Brief reading, digest checks and
  method verification still use only `brief_path`.

Temp-dir synthetic probes on the committed bytes:

| Case | Result |
|---|---|
| Relative brief, then `origin --subject-ref docs/real-subject` | `ref=docs/real-subject` (baseline behaviour restored) |
| Second, different `origin --subject-ref` | Ignored with exit 0; `ref` stays `docs/real-subject` |
| Explicit `--subject-ref` at init | Kept after a later origin call |
| Older panel with no `brief_ref`, where `ref` equals the absolute path | Override still works; `summary` exits 0 |
| Tampered `brief_ref` pointing at a missing file | Has no effect; `summary` still reads and verifies `brief_path` (exit 0) |
| Brief deleted | `close-plan` by the owner exits 0; `summary` exits 2 without a traceback |

Regression test: `tests/unit/adaptive_review.py:245-258`, part of the existing
relative-brief/cross-cwd/cleanup test.

Residual, not a finding: an init `--subject-ref` spelled exactly like the brief
cannot be told apart from the default, so it can still be replaced. That matches the
baseline semantics.

Line references in the closure evidence below are at `17f70f52`. At `f01294db`,
`lib/mars_contract.py` lines after 283 shift by +1.

## Closure evidence for the open final items

1. **Fixed: legacy/deleted/non-dict method downgrade (prior P2).**
   `_validate_panel_method` (`lib/mars_contract.py:290-311`) does four things:
   - requires `subject` and `method` to be objects;
   - reads the original brief from its own `brief_path` and requires its SHA-256 to
     equal the frozen `brief_sha256`;
   - requires `schema_version == 2` and `version == "2"` whenever the frozen body
     starts with the v2 marker (`:301`), no matter what the stored method claims;
   - then runs `rm.validate_meta` and checks method/brief digest equality (`:309`).

   The check runs from `validate_panel` (`:314`), from init after attach
   (`bin/li-mars.py:162`), and from every non-cleanup action (`bin/li-mars.py:170`).
   Probes against a v2 panel whose method was replaced with legacy v1 were all
   refused with exit 2 and no traceback: `summary`, `synthesis-header`,
   `verify-input`, `brief`, `add`, `record` and `inspection`. These rewrites were
   also refused:
   - emptied `required_questions`;
   - `version:"1"` with `schema_version:2`;
   - float `2.0`;
   - `schema_version:1` with the inventory kept;
   - init on a v2 brief without `--method-meta`.

   Rewriting the brief to v1 fails the frozen digest. Regression coverage:
   `tests/unit/adaptive_review.py:201` covers legacy, `None`, `{}`, `[]` and string
   methods for both `validate_panel` and `summary`.
2. **Absolute brief path and owned cleanup.** New panels store an absolute
   `brief_path` (`lib/mars_contract.py:284`). An old panel whose relative brief is
   missing gets a readable error ("original panel brief unavailable…", exit 2, no
   traceback). Only `close-plan` and `mark-closed` skip method verification
   (`bin/li-mars.py:170`, `lib/mars_contract.py:462`). They still do structural
   validation, and their owner checks are unchanged: a non-owner `close-plan` or
   `mark-closed` is refused. They return no findings or clearance. Tested at
   `tests/unit/adaptive_review.py:223`; I probed these paths again from a different
   working directory.
3. **Strict JSON.** `_json_object` (`lib/review_method.py:65-88`) re-raises
   `MethodError` and turns `ValueError`/`RecursionError` into `MethodError`. It
   rejects NaN and ±Infinity through `parse_constant`, and ±`1e999` through
   `parse_float`/`isfinite`. It is used by both `read_json` and the body inventory
   (`:287`). MARS `read_json` (`lib/mars_contract.py:51-58`) maps
   `ValueError`/`RecursionError` explicitly and re-raises `ContractError`. Neither
   has a broad fallback that reports success.

   Probes: 5000-digit integers, 5000-deep nesting, duplicate keys and `-1e999` all
   gave a readable error. `1e308` is accepted as finite. `check_report`
   (`:610-632`) behaves as follows:
   - v2 requires the original body, including its inventory and exact bytes
     (`:379-386`).
   - Legacy metadata cannot consume a v2 body (`:384`).
   - v1 stays readable with `legacy_metadata: true`, an explicit limitation and
     `release_clearance: false` (`:628-632`).

   This is intended compatibility. It never provides current mandatory clearance.
4. **Pattern-context question tags.** `bin/li-review-packet.py:146-149` sets
   `question_tags=["pattern-context"]` only when status is `ok`/`ready`/`review-unmet`
   **and** the provider projection, which `review_context.prepare_pattern_review` fills
   only after a successful `verify_lock`, has clauses or settings. It adds no second
   resolver, scanner or asset read. `adaptive.md:134` sends the tags to `--tags`.

   I ran the documented command locally:
   `questions --kind implementation --stage quality --tags pattern-context` selects
   SQ-CONTEXT-01, and it is absent without the tag. With the provider missing, the
   result was exit 5, `unavailable`, `question_tags: []`. The real-provider join
   (`tests/integration/adaptive-patterns.py:165,180`) is **not** re-observed here
   (see Limitations).
5. **Visible metadata.** `_visible_metadata` (`lib/review_method.py:288`) escapes the
   nine explicit bidi embedding/override/isolate controls, C0 except `\n`/`\t`, DEL
   and C1. It is applied to the reused P1 `render_assessment` output (`:338`), and the
   inventory line stays `ensure_ascii`. The CLI's `_assessment` builds depth only from
   the raw 6-axis `--risk-file` facts through `assess_depth`; there is no path that
   accepts a supplied assessment. Regression: `tests/unit/adaptive_review.py:305`.
6. **Question cost and bounds.** The core catalog went from 37 (`49f2d152`) to 51,
   and no existing question changed. SQ-U11 is the single new trigger-less
   (universal) row, applying to implementation/code-review. The other 13 are
   trigger-gated: tenant/auth, network, crypto, memory-unsafe, limits,
   agent-tools/input/memory, release/production, deep-review/security-critical,
   risk-unknown and pattern-context. None is marked mandatory. The cost is recorded
   in ADR-0040 "Proportionate cost" (lines 55-67). Review reference sizes are
   8434/5636/18493/10706/4611/4790 bytes, all under 20 KB. `49f2d152..17f70f52`
   touches no P05/P07 schema, MARS defaults/schema, mandatory-panel field or new
   pack field.

## Checks actually run

These ran on Windows with Python 3.11.9, using synthetic data only.

First pass, at `17f70f52`:

| Check | Result |
|---|---|
| `python -B tests/unit/adaptive_review.py` | 17 tests OK |
| `python -B tests/unit/review_method.py` | 21 tests OK |
| `python -B tests/unit/mars_contract.py` | 41 tests OK |
| `python -B tests/integration/adaptive-patterns.py` | 1 test OK; provider not installed, so only the unavailable boundary was checked |
| Temp-dir probes (CLI and in-process) | Findings and closures listed above |

Recheck, at `f01294db`:

| Check | Result |
|---|---|
| `python -B tests/unit/adaptive_review.py` | 17 tests OK (includes the extended regression) |
| `python -B tests/unit/mars_contract.py` | 41 tests OK; rerun because `new_panel` gained a field and none of these tests asserts the exact keys |
| Temp-dir origin/brief_ref probes | Results in the P3-1 recheck above |

`review_method.py` and the integration check were not rerun for the recheck because
their files are unchanged in this delta.

I did not run the 117-case P05 entry, the full-repo suites, `mars_hooks.py`, or any
live host, network or model call.

## Limitations

- The unchanged P05 regression (shell 77) was interrupted after about 53 observed
  passes, with **no 117-suite verdict**. I did not duplicate it, and there is no
  suite PASS. The required 117-case hosted/P05 gate is still outstanding at
  `f01294db`.
- The real-provider 5/5 at frozen `64338b6c`, including the new question-tag
  assertions, is the coordinator's reported observation. I did not reproduce it
  because the provider is absent on this branch.
- `mc.read_json` still accepts NaN/Infinity in MARS state files. That was out of
  scope for this fix. Method inventory comparison still refuses mismatched metadata.
- `_visible_metadata` does not escape the implicit marks LRM, RLM and ALM, or
  zero-width characters. The explicit override set (the CVE-2021-42574 class) is
  covered.
- Panel JSON remains unsigned local state. A rewrite of the whole panel (both
  `brief_path` and `brief_sha256`) is outside this fix. Reports stay bound to the
  original digest.
- Legacy v1 `check` without `--body` stays usable but labeled legacy, with no
  clearance. This is intended.
- Items not verified here: current main (`c3ffa153`), native1a regeneration,
  patterns-stack acceptance, Linux/macOS or hosted CI, and publication. Those
  belong to the integration owner.
