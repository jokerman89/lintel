# Handoff: W1-6 wiki output isolation

Read [spec.md](spec.md), [plan.md](plan.md) and [work.json](work.json).
Keep original scope W1-6 / BIN-02; this is only its wiki-generator slice.

Implement truthful `--wiki-only` and `--showcase-only` behavior, including selected
`--check`. Default output remains wiki, showcase and README. Preserve unrelated
files/directories; refuse conflicting selectors and missing output operands before
writes. Reuse existing renderers, schema validation and tests.

Use only this isolated worktree and owned synthetic outputs. The master W1-1 tree
is frozen separately. No reset, rebase, history rewrite, new renderer/dependency,
profile bootstrap in another context, remote action or cleanup is permitted.
The old partial-output observation and metadata-guard refusal remain history.
Report actual targeted checks, then obtain independent review and current
delivery evidence rather than marking the parent W1-6 card complete.
