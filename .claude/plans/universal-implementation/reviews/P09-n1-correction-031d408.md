# P09 N1 correction review

## Frozen scope and verdict

Independent SAME447 artifact review: **selected N1 SPEC PASS, then eligible
QUALITY PASS**. New findings: **P1 0 / P2 0 / P3 0**. This accepts the corrected
safety quantifier and its finite evidence, not a fulfillment implementation,
the historical TA draft, the separate DA obligation or a compound P09 parent.
The reviewer did not draft or repair the correction.

Anchor `031d408a3e3c85e82521ed4e5c8e7c9de05ae243` is directly on authorized
`477d3fceebe483329bebcf1154545f838f43cf6e`. Its only changed path is
`reports/P09.md`; the prior 813-line prefix is exact and the frozen report has
871 LF lines, SHA-256
`09f589e262243f2503bf2b3ce420db4ade4b8a82dcc4a763122505db97537b6c`.
Reviewed appendix: lines 814-871; authority: `packages/P09.md:147-170`.
Previously accepted content, core and module product are not broadly re-reviewed.

Packet `finite-packets/n1-correction-v2.zip`:
`3249f7f3a2809e43ec79534c1fb8d50fd81a6dab8cbe9ec5570a379e4fb09208`.
All 125 members were read/CRC-checked, and the six sidecar-selected live files
matched. Before independent execution, 124 members remained byte-exact; the only
other difference was the caller's log counter 17 -> 18. It changed no request,
profile, obligation or evidence. All 125 named live files were then sealed and
remained unchanged across the independent checks.

## SPEC, followed by QUALITY

| Selected boundary | SPEC result and substantive evidence | Eligible QUALITY |
|---|---|---|
| Guarantee and derivation | PASS. Corrected `.claude/runtime/artifacts/n1-correction.md:15-35,60-68` counts distinct committed effects per paid-order identity cumulatively across retries/restarts. Zero is permitted; neither eventual delivery nor an exactly-one lower bound is introduced. | PASS. Commit boundary, stable identities, incomplete coverage and finite-observation limits are explicit rather than presumed capabilities. |
| Oracle and counterexample | PASS. Draft lines 37-58 and `checks/n1-safety-oracle.py` distinguish zero/one, two same-order effects, independent orders, duplicate observations and restart accumulation. Unknown coverage is unverified. The original exactly-one oracle's rejection of zero is retained as a counterexample. | PASS. Inspected live oracle passed its 10 stdlib cases; an independently written enumerator passed 1,555 traces and 3,110 known/unknown-coverage comparisons. These establish the finite quantifier only. |
| Original work and historical failure | PASS. Eight original input copies and the old TA artifact were compared; P09/T014/T001 and the original R1 remain. The new TA-only correction does not satisfy or erase DA/R2. | PASS. Original 83-member archive remains `83a92029589aaacb6b5283f6d5285cbd7ca0c4b4838b262bfd7de1912d53c716`. Historical TA semantic SPEC remains FAIL; this new corrected artifact resolves its N1 wording without rewriting history. |
| Actual publication and current data | PASS. Inspected original preimages/start/result, immutable request/QA inventory, fresh P07 pin and externally prepared noncircular final P05 context. Fresh read-only P09 summary and P05 QA both exit 0 and agree. | PASS. Current inputs/evidence verify; summary still says `review:not_evaluated` and `release_clearance:false`. Producer strings and schema validity are not independent semantic approval. |
| Review boundary and measured claims | PASS. At the actual `audit/reviews.jsonl` path, fresh P05 reader provider exits 3 with `No applicable review decision`; no decision/corroboration was authored. Original builder Bash-reader exit 3 was separately verified from its receipt and streams. | PASS. Draft lines 70-91 keep p99/throughput as given, unmeasured targets, reject summing component p99s, and disclose the absence of live service, DB or new-model execution. |

## Exact context evaluated

Checks used the original live target
`.claude/runtime/p09-depth/native-n1-i0002/target` in the original owner's
`jokerman-microsoft-automatic-system` worktree, not a relocated archive.
Real P07 reference: `p09-n1-fresh`, generation 1,
`sha256:985fdba07417d15297d8af654cfda1c0643c675966a59558ef26a4c18e660ea9`.
Attempt `p09-n1-correction-2`, operation `native-n1`, iteration 2; receiver mode
`source-guided-owner-correction`. No new actor or model was used.

| Evaluated object | SHA-256 |
|---|---|
| Corrected draft | `13f028c1a026c478140ebc15db41e53e0b1c6b1bd28c18f59ec1a44f3b9f4d65` |
| Immutable request | `0c531f070cbe7a4e932c0d3e00755dfa1f13c044a720274f4d1f0887c7c1d7a4` |
| External final context | `28b2b56b24b78408a26417ee4a750b2215f12ebd102255645a7fe832f06eede4` |

Only that exact, freshly verified N1 context can potentially consume this scoped
independent review through the existing authorized review process. This report
is not a P05 decision receipt or host/human corroboration. It confers no approval
on older attempts, DA, mode probes or a later changed context.

## Independent evidence and retained limitations

Private evidence is in reviewer session `447d97f5` under `files/p09-n1-review`:
`intake-receipt.json`, `metadata-receipt.json`, `live-checks-receipt.json`, and
the exact-exit/hash receipts and streams under `logs/`.
`metadata-2` verified all 17 archived child receipts, immutable obligations and
the failed first long-path packet operation; `live-checks-2` ran the checks above.
Every product child used allowlisted synthetic HOME/USERPROFILE/derived
AppData/XDG/temp/Lintel paths, PATHEXT and fixture Git ceilings; source checks
were separate. No archived code was executed.

Three stopped reviewer guards remain recorded: checkout's initial fsmonitor
assumption, whole-packet equality before identifying the log counter, and the
source-byte comparison before identifying a CLI CRLF/LF difference, plus their
successful bounded continuations. These were reviewer assumptions, not product
failures. Thirteen execution dependencies were byte-identical to the frozen
checkout; `bin/li-domain-result.py` differed only by 106 CRLF/LF line endings.
All owner dependency raw hashes and all 1,024 original reviewer tracked-file
hashes remained unchanged. The failed original `n1-packet-freeze` and successful
V2 remain distinct; V2's native I/O spelling is not whole installed long-root proof.

This report is the sole authored repository change. No source/target/pin/receipt
mutation, cleanup, installation, new actor, paid benchmark, service/DB execution,
remote operation or full-suite run occurred. Installed A09.5, full A17.5, P10/B01,
finite-mode review and compound-parent acceptance remain outside this verdict.
