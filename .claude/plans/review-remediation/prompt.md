# Handoff: original remediation card W1-1

Read [spec.md](spec.md), [plan.md](plan.md), the Universal adapter and ADR-0028/
ADR-0031. The selected map is [work.json](work.json); preserve original ID W1-1.

Implement the known helper-source selection correction, not a new audit. Source
scope is the canonical `review`, `ship`, `usage-log`, `orientator` and
`frontend-style-extract` workflows, focused tests and their generated native
artifacts. Keep source code separate from target state and preserve data paths,
permissions, policy and independent-review semantics.

Explicit trusted source takes precedence. A documented plugin root may supply the
trusted binding when absent; Git cwd, target repo and personal home may not.
Required helper loading must fail visibly on missing/invalid inputs. The optional
footer may report unverified/unavailable without loading another source.

Use inert owned fixtures, not exploitation demonstrations. Start with static
regression assertions, then exercise only the corrected examples. Run existing
source/target, footer and native-drift checks. Regenerate with `bin/li-copilot.py`.
Retain unsuccessful observations rather than converting them into passes.

The operator explicitly requires real implementation of review findings. This
single card does not authorize a portfolio deletion quota, governance rewrite,
hook activation, external publication changes or removal of preserved branches.
Do not touch other actors' worktrees or the byte-bound historical todo file.
Leave W1-1 open until implementation and current independent review/QA are real.
