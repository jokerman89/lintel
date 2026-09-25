# P13 compact discovery first-unit final review

**Date:** 2026-09-22. **Complete first-unit SPEC: PASS. First whole first-unit QUALITY: PASS.**
**Open findings:** P1: 0 / P2: 0 / P3: 0. Historical F01 and F02 are closed on the exact repair.
This accepts the released source-discovery first unit, not whole P13, installation or SHIP.

## Exact inputs and scope

| Input | Identity |
|---|---|
| Original first-unit base | `4b98a4d88e8b58ed5b83d49459a076dfe6bac191` |
| Original product / report | `2a4ba255f989f0a411bddaedc2738a6b6b7604d1` / `e20588d5cfd914cc1bc861143fc9d1a4b39bcaca` |
| Repair authority | `c2f485c7a6a749f9683703ecf242edc481f231aa`, complete P13 card, F01/F02 subsection |
| Reviewed repair product | `b1d4caf34227d147a428050debf0f81827e43938`; sole parent `e20588d5cfd914cc1bc861143fc9d1a4b39bcaca` |
| Report-only checkpoint / this review's required parent | `204ea7253b18fb1849fa6de94e1b283b098039b5`; sole parent `b1d4caf34227d147a428050debf0f81827e43938` |
| Builder report Git SHA-256 | `64adc40fcd41cd732b17dbf9016be481ab089c1cc4aa1276947f40cb2684cb6e` |
| Preserved rejection | `466a454b685d35d78671bd917ea50e80eed9cc1a`, retained by `jokerman-microsoft-universal-discovery-review` |
| Same independent reviewer | CLI `4865e4f7-240b-4721-a64d-ce6df9a75a9c`; project `d22ed027-438e-49e9-8063-9501d5c56aca` |
| Builder / recovery coordinator | `c4e9de1c-1c81-4897-ba82-019d58b635d7` / `88aecc43-40f9-41d4-8947-6c2fb0a55481` |

Verified the clean detached checkpoint, sole-parent links, three-path repair and all
three product hashes. Read the entire 341-line builder report, including its unchanged
198-line historical prefix and 143-line append, and the complete authority card.
Startup/Copilot/Universal contracts, accepted ADR-0028/0029, selected work map/spec/
plan/action acceptance and relevant memory remain the authority loaded for this review.

The whole first-unit selection remains exactly eight product paths:
`bin/li-catalog.py`, `install/upstream-sources.yaml`, `skills/catalog/SKILL.md`,
`skills/catalog/references/metadata.md`, `skills/help/SKILL.md`,
`skills/skill-router/SKILL.md`, `tests/unit/catalog-metadata.py` and
`tests/unit/catalog-metadata.sh`. The repair changes only:

| Repair path | Git-byte SHA-256 |
|---|---|
| `bin/li-catalog.py` | `7c78c69ad5152da96068e51457d736c900f59ad0b10ab59250481bc100a0269f` |
| `skills/catalog/references/metadata.md` | `a784f80131059561af853bd6ba2e2d612bdd13b2082883f27ca5892ec01601da` |
| `tests/unit/catalog-metadata.py` | `269fcb0d671ea86b929e64ac76f5d4aa43fd6c82ba9de0c9577a7b1722b8ff32` |

Acceptance covers the released A18.3/A19.1/.2/.4/A20.1/.2 contributions, not their
larger original leaves. No A+B descriptor, installer, generated output, version,
corpus, shared state or underlying parser/registry was imported or repaired here.

## Stage 1: complete first-unit SPEC

SPEC PASS was recorded at **15:25:39 UTC**, before QUALITY began. Prior unmodified
source evidence was reused only after raw-byte identity checks; affected behavior and
the original independent probes were actually rerun, not inferred from builder results.

| Control | Result | Evidence |
|---|---|---|
| Exact authority/selection/preservation | PASS | Chain, hashes, complete reports; all 196 canonical prompt files retain pre-repair raw bytes |
| Same generator and canonical readers | PASS | Existing generator; unchanged accepted envelope loader and P06 registry reader; no duplicate parser |
| Canonical source inventory | PASS | 127 skills, 69 agents, 46 retained skill aliases; full descriptions, source paths and unknown maturity |
| Opening-frontmatter-only reads | PASS | Original guarded-reader/invalid-body probes and retained BOM/CRLF/header-ceiling cases |
| Literal search and composed filters | PASS | Query/search/family/name/category/voice/kind/surface; hostile literals and valid zero matches |
| Invalid inventory/input/helper/parser refusal | PASS | Complete requested-kind validation before filtering; missing/malformed/duplicate/tag/anchor cases; no partial JSON |
| F01 agent alias ambiguity | PASS, closed | Alias/name in both orders, alias/alias, case variants, self-alias and canonical duplicates; `agent`/`all`, unfiltered/exact/unmatched queries |
| Distinct identity namespaces | PASS | Same name or alias across skill/agent kinds remains valid, with separate IDs and retained values |
| F02 generation/check ambiguity | PASS, closed | Duplicate/case-equivalent names across folders/layers refuse before writes; good catalog preserved; existing ambiguous catalog cannot pass `--check` |
| Default compatibility and dependency floor | PASS | Exact original valid bytes/messages/exits/platform endings; plain generation/check work with `-I -S` |
| Executable versus data/target roots | PASS | Trusted readers remain script-bound; data/target Python decoys do not execute or replace missing helpers |
| Query source/target preservation | PASS | Original no-write snapshots and fresh source-before/after seals; fixture generation is explicit and isolated |
| Three metadata-first consumers | PASS, structural | Catalog/help/router use one metadata view; listing reads no bodies; router selects at most three before body reads |
| Declared capability and fallback honesty | PASS, structural | Templates/staged descriptions retained; no live capability/model/tool claim; missing parser has explicit skills-only snapshot fallback |
| Provenance and inherited notices | PASS, source only | Eight references/two adaptations unchanged after parsing; notices/attribution retained; unknown import commits and declaration-only installer comments preserved |

**F01 closure:** `bin/li-catalog.py:194-232,288-289` generalizes the existing ownership
routine per namespace and collects all canonical names before aliases. Validation precedes
every filter. Tests at `tests/unit/catalog-metadata.py:458-504`, plus the unchanged original
reviewer collision probes, pass. Confidence in closure: **10/10**.

**F02 closure:** `bin/li-catalog.py:88-106,340-350` shares stdlib identity registration
between metadata and generation before opening/certifying output. Tests at
`tests/unit/catalog-metadata.py:506-549` and the original pre-write probe pass.
This remains a corrected **retained-baseline acceptance gap**, not a retrospectively
invented new regression. Confidence in closure: **10/10**.

## Stage 2: first whole first-unit QUALITY

QUALITY began only after the recorded SPEC PASS and completed **15:28:07 UTC**.
It covered all eight first-unit paths and their existing readers, not only the repair.
The reviewer made no product edits and used no nested/fourth reviewer.

| Dimension | Verdict and basis |
|---|---|
| Correctness | PASS: order-independent canonical/alias ownership, full validation before selection/publication, namespace positives and deterministic valid output |
| Trust/error boundaries | PASS: source-bound helpers, data-only selectors, accepted strict parsing, visible refusals and no false execution/permission claims |
| Resource use | PASS: bounded opening headers and two cached readers; dictionary/set identity checks; whole-inventory validation is deliberate, not full-body prompt loading |
| Maintainability | PASS: generalized existing alias logic plus one small shared identity helper; no new parser, inventory, service or installation dependency |
| Tests/documentation | PASS: original 24 method ASTs exact, seven focused additions, independent repros close both gaps; contracts/fallbacks and platform limits match exercised behavior |

No actionable P1/P2/P3 finding remains within this first-unit selection. These are
independent scoped SPEC/QUALITY verdicts, not model-behavior or enterprise-policy proof.

## Actual checks and retained evidence

| Check actually rerun on the frozen repair | Result |
|---|---|
| Git Bash `tests/unit/catalog-metadata.sh` | Exit 0; **31 methods**, no skips; original 24 unchanged by AST plus seven additions |
| `tests/unit/client-capabilities.py` | Exit 0; **16 methods**, no skips |
| Exact original reviewer `adversarial.py` bytes, new private fixture root | Exit 0; **10 methods**, no skips; both formerly failing methods now pass |
| Prior/repaired valid metadata comparison | Exit 0; **18 kind/filter selections** preserve exact values and compact JSON bytes |
| Original/repaired generation comparison | PASS; canonical and original varied valid fixtures retain bytes, stdout/stderr, exits and stdlib-only behavior |
| Existing catalog unit, catalog drift, alias shape and frontmatter boundaries | Each exit 0; actual drift `--check`, no source regeneration |
| Whole first-unit `git diff --check` | Exit 0 |
| Source seals and repair hashes | PASS; no source changes during any verification command |

Canonical Markdown SHA-256 remains
`adc2232421ac2b60b44aba37fa39d6a439c199ba936f419c159f1f2bc34af181`.
Fresh logs are in this reviewer's private `files/p13-discovery-final-review/`;
`spec-pass.json` and `quality-pass.json` bind the stage order. The evidence manifest
SHA-256 is `133c123ed4a9aad4f5f602a21bb0572e8541ba45561ade0fc0ede2bfd6d170a5`.
The earlier rejection and failed probes remain unchanged in `files/p13-discovery-review/`.
The builder's appended 50-assertion RED remains historical builder evidence, not a
new reviewer execution. No failed history has been relabeled.

## Isolation, limits and next action

All product calls/imports, including outer comparisons, run after inspected synthetic
HOME/USERPROFILE/AppData/temp/Lintel/source/target/derived-root checks, environment
allowlisting, explicit PATHEXT and fixture Git ceilings. Source Git-byte/EOL handling
is separate from fixture configuration; no source normalization or global setting changed.
The sole checkout transition was the authorized clean detach, preserving the rejection ref.

Actual runtime: Windows, existing Python **3.11.9** and PyYAML **6.0.3**, Git Bash.
Python 3.9 remains grammar-only; Linux/macOS, native symlink/junction behavior and live
model/client acceptance were not exercised. Structural consumer checks are not model
behavior. No full suite, installation, new dependency, personal-home inspection,
network/GitHub action, policy change, hook activation or strict-reader SHIP clearance.

Recovery can use this **actual first-unit PASS** to release original owner `c4e9de1c`
for the already approved conditional A+B work. Installed selection/dependency/notice
closure remains coordinator/P10-owned; final maturity/version, generated fan-in and
whole-P13/integration acceptance remain separate. No shared checkbox is closed here.

**Position:** first-unit REVIEW PASS -> coordinator's gated continuation; no SHIP.
