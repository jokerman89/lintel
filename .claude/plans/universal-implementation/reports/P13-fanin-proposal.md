# P13 fan-in preparation and version proposal

**Rebased onto the authorized local P08 integration; not final selected P08 or release acceptance.**
Original preparation authority: `5b6479b52cde51af2003232c58940af9b0604d4c`;
current authority is coordinator88's 2026-09-24 fan-in rebase release.
Exact base: `ad1045b8b10a56fa3bcc5c310a8cad84f7ccf2c4`,
local `jokerman-microsoft-p08-integration`.
Original P13 owner: `c4e9de1c-1c81-4897-ba82-019d58b635d7`.
Preparation branch: `jokerman-microsoft-p13-final-fanin-0924`.

## Prepared source input

The [current preservation view](P13-skills-preservation.md#p08-integrated-fan-in-map)
joins all 46 workflow and 80 capability audit records at original
`28061e434be455ca02f135b73244eaf4f73f3a69`. Every row retains the original
recommendation, useful method/output, canonical path, applicable aliases and
arguments, owner/leaf, disposition rationale, worked/recheck example and evidence
limit. Original-to-preview identity is 118 changed / 8 unchanged original files,
with Swarm separately attributed. This is not 126 newly executed workflows.
Only `hooks-status` changed as a canonical skill body since the prior preview:
its method now includes optional doctor JSON via `li-events.py installer`,
without treating installed bytes as hook execution.

All prior map tables remain historical evidence. The original
[69-role map](P09-agent-preservation.md), [76-path Swarm inventory](../../../engineering/audits/2026-09-20-universal-quality/swarm-preservation.md)
and [P04 preservation](P04-preservation.md) are unchanged. Historical merge,
retire, pack and staged recommendations are not deletion or activation authority.
General maturity stays unknown; PDF/XLSX source methods are available, while
Visio retains its actual staged source evidence.

The status change keeps original map/cycle/profile observations first and adds
the trusted `bin/_jobs.sh` readers `list_jobs --read-only` and `stale_jobs 24`.
No-init and explicit repository-local directory/registry/archive selectors
prevent inherited home paths from widening the display, including repositories
without the v5 marker. Blocked, stale, unknown and partial-error output remains
visible; an absent registry is unobserved, not idle. The provider, state/profile
readers and already-integrated welcome body are unchanged.
The integration now includes A13.1.b/.4.b and reconciliation 6: the adapter
preflights `bin/li-events.py`, `lib/event-catalog.json` and `bin/li-lessons.py`,
and every capability selection retains the added core `bin/li-lessons.py`
resource. P13 changes none of those provider/descriptor bytes.

Four new status regressions first failed on the old caller; all 18 selected
status tests then passed after the bounded change. These are actual fixture
caller checks, not a live model/client run or full P08 acceptance.

## Generated surfaces

The actual canonical invocations were:

```text
python -I -B bin\li-catalog.py
bash --noprofile --norc bin\li-wiki-gen --wiki-only
```

The original preparation regenerated `skills/CATALOG.md`, the five wiki outputs
and the README capability section with passing checks and deterministic bytes.
The integrated input is rechecked separately; any new drift is regenerated only
through these generators and committed separately from source and N2. Raw
generator output and Git-LF identity remain distinct. No output is hand-edited,
no generator implementation changes, and the showcase stays outside write scope.

## One proposed deployable version

**Propose `0.11.0` for the final integrated Lintel distribution.**
This is a proposal only: the coordinator agrees the version after actual
integration and outstanding acceptance. No manifest, tag, release or publication
was changed here.

The current canonical product identity is `0.10.0`. A new pre-1.0 minor marks
the integrated Universal behavior/contract changes without asserting stable
1.0 maturity or reusing the existing distribution identity. Historical v3.x
development tags are retained history, not the current canonical version line.

| Existing product manifest | Final proposed field values |
|---|---|
| `.claude-plugin/plugin.json` | `version: 0.11.0` |
| `.claude-plugin/marketplace.json` | `metadata.version: 0.11.0`; `plugins[name=li].version: 0.11.0` |
| `.codex-plugin/plugin.json` | `version: 0.11.0` |
| `.cursor-plugin/plugin.json` | `version: 0.11.0` |
| `.github/plugin/plugin.json` | `version: 0.11.0` |
| `.github/plugin/marketplace.json` | `metadata.version: 0.11.0`; `plugins[name=li].version: 0.11.0` |
| `gemini-extension.json` | `version: 0.11.0` |

These are the seven product identity surfaces used by the existing
`tests/shape/manifest-identity.sh`; all currently declare `0.10.0`, including
both marketplace entries. The checked-in `.github/lintel/manifest.json` is a
schema-version-1 managed-file inventory, not another product version to bump.
Any final regenerated kit's copied canonical metadata must carry the one agreed
product version, while ownership/schema fields retain their own contracts.
Pack, feature, selection/schema and upstream dependency versions are **not**
automatically changed with the product stamp.

Neither `0.11.0` nor `v0.11.0` occurs in the observed local tag set. Remote
tag/registry uniqueness was not queried: it remains a final coordinator check
under publication authority, not a reason to access the network now. Final
version-parity checking must include nested marketplace entries; do not accept
a skipped jq branch as proof. No denied jq binary was executed or copied.

## Held integration and review gates

- This input includes A13.1.b/.4.b, but the F06 report appendix and final
  selected P08 SPEC remain outstanding. Recovery has not merged this local
  integration; no broader P08 acceptance is inferred.
- Installed closure is now independently accepted in
  [review d0eb793e](../reviews/P13-installed-5c77a98.md), integrated at
  `1e41deb0`; coordinator `371343eb` closes A18.3/.4 at their reviewed scope.
  The old IC-F01 failed fixture and all original reports remain untouched.
  Advisory N1 feeds the final CI-budget decision; N2's fixture-root ordering is
  corrected and discriminatingly tested in a separate commit, without a producer change.
- Reviewer `30146eab-ddeb-467e-8f1b-8da575256ba2` owns this integrated fan-in's
  SPEC then eligible QUALITY under the required Opus 5.5/max/long-context
  configuration. The earlier 486/447 holds and their prior reviews remain
  history; this owner creates no replacement/helper or independent verdict.
- Native-format/visual, required-policy/global P05, full installed consumer,
  original-parent, final-version and delivery gates remain their original
  separately owned decisions. No push, tag or remote publication is authorized
  by this proposal.

See the append-only [P13 execution report](P13.md) and its exact source/evidence
handoff for commit identities, raw-versus-Git hashes and actually executed checks.
