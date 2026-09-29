# Architecture enforcement claims

Status: APPROVED within the operator's report-driven remediation scope.
Original finding: DR-31; this slice is W1-9.claims, not the W3-6 publication guard.

| ID | Requirement | Observable acceptance |
|---|---|---|
| R1 | Describe the existing language check accurately | Architecture links to `tests/shape/no-swedish.sh` and describes selected Swedish letters/words, listed paths and explicit exemptions. |
| R2 | Remove unsupported enforcement guarantees | Neither the architecture prose nor the shape-tier table claims general detection of company identity or every non-English language. |
| R3 | Preserve the intended boundary and implementation | Company identity still belongs in external packs. No scanner, policy, hook, runtime, version or governance file changes. |

The existing check is the evidence source, not permission to broaden its scope.
Adding a publication guard, selecting its patterns and resolving existing public
content remain separate work. The broader W1-9 and W3-6 cards stay open.
