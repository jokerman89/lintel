# Spec: isolate partial wiki output

**Status:** APPROVED for original W1-6 / BIN-02 only.
**Authority:** the operator's report-driven implementation request.
**Plan:** [plan.md](plan.md).

`li-wiki-gen` documents `--wiki-only` and `--showcase-only`, but unconditionally
regenerates README after either mode. Its check path also ignores these selectors
and creates directories in the baseline. Correct the selected-output behavior
without changing rendered content, source data or default generation.

| ID | Acceptance |
|---|---|
| R1 | Wiki-only generation writes only the five wiki files; showcase-only writes only its existing HTML file. README and unrelated output trees remain untouched. |
| R2 | With neither selector, generation/checking still covers the same seven artifacts, including the README capability table. |
| R3 | `--check` checks only selected artifacts and never changes the supplied baseline, including when selected artifacts are missing. |
| R4 | Conflicting selectors and missing/empty `--output` arguments visibly fail with exit 2 before output writes. |
| R5 | Schema validation remains fail-closed for outputs that consume the schemas; existing determinism, drift and preservation checks stay intact. |

Use the existing generator and unit/shape checks. Add no new generator engine,
renderer, package, profile operation, hook or external service. This slice does not
close the other W1-6 helper findings.
