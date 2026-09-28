# Brief pointer: PACK

This is not a Brief Forge envelope, and not a copy of the dispatch prompt. The lane was started by
the pack lane session dispatched by the parent (host id per the parent record: 5108bc3b) from R2 head ae9d6df7, before these swarm artifacts existed (see ../charter.md,
"Chronology"). The parent holds the actual dispatch text.

- Package and member leaves: the "Swarm execution packages" table and leaf items in
  [plan.md](../../plan.md). They are authoritative and are not copied here.
- Write scope: `write_scope` of lane PACK in [coordination.json](../coordination.json). The parent's
  original kickoff fixed six paths and allowed narrowly named new pack/roots tests and fixtures. The
  lane's reported literal additions (tests/unit/pattern-pack-origins.py, pattern-launcher-roots.sh/.py
  and the shared hermetic helper tests/unit/pattern_pack_harness.py) are listed; no fixture directories. `lib/profile_context.py`
  is CONDITIONAL and not in the scope: only a strictly necessary small adapter change, reported to the
  parent before editing, never a parser or cache rewrite.
- Frozen interface: [contract.md](../../contract.md) (revisions R1-R3). Topology and pending-join
  rules: [topology.md](../../topology.md).
- Startup: repository AGENTS.md, the Copilot adapter, memory, relevant ADRs and li-build.
- Report: `reports/PACK.md`, written by the worker. Review: `reviews/PACK.md`, written
  by an independent reviewer only.