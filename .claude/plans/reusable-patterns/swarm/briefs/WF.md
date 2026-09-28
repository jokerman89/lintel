# Brief pointer: WF

This is not a Brief Forge envelope, and not a copy of the dispatch prompt. The lane was started by
the workflow/visual lane session dispatched by the parent (host id per the parent record: a2f55ec5) from R2 head ae9d6df7, before these swarm artifacts existed (see ../charter.md,
"Chronology"). The parent holds the actual dispatch text.

- Package and member leaves: the "Swarm execution packages" table and leaf items in
  [plan.md](../../plan.md). They are authoritative and are not copied here.
- Write scope: `write_scope` of lane WF in [coordination.json](../coordination.json).
- Scope note: the parent approved one narrow addition, the shared synthetic fixture
  `tests/integration/pattern_consumer_fixtures.py`. No shared schema, validator or helper source
  extension is authorized or needed.
- Frozen interface: [contract.md](../../contract.md) (revisions R1-R3). Topology and pending-join
  rules: [topology.md](../../topology.md).
- Startup: repository AGENTS.md, the Copilot adapter, memory, relevant ADRs and li-build.
- Report: `reports/WF.md`, written by the worker. Review: `reviews/WF.md`, written
  by an independent reviewer only.