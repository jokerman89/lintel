# TODOS

Deferred work, ordered by priority. Each item has the context needed to pick it up cold.

Source: design doc `jokerman-main-design-20260526-225146.md` (deferred items) + this `/plan-eng-review` session (new items surfaced).

---

## v1.1.0 — Power user activation

### T-101: Layer 4 hook activation mechanism

**What:** Implement the mechanism for `layer-config.yaml: hooks.<name>.enabled: true|false`. v1 ships hook FILES but no activation. v1.1.0 wires them up.

**Why:** Without activation, Layer 4 hooks are reference scripts only. Operators who want them have to manually symlink, which defeats the "install + go" promise.

**Pros:** Compliance hooks become enforceable (secret-scan blocks bad commits; data-classification surfaces sensitive content; ms-policy-refresh keeps SharePoint guidance current; repo-clean-state catches accidental customer-data). Layer 4 graduates from "patterns to try" to "patterns in use."

**Cons:** Editing user's Claude Code config (via symlink into `~/.claude/hooks/` or settings.json modification) has side-effects. Risk of breaking existing hook setup.

**Context:** Resolved A1 in `/plan-eng-review` 2026-05-26 — three implementation paths considered (symlink, settings.json, manual). All deferred to v1.1.0 pending more usage data on which hooks are actually useful.

**Depends on:** v1.0.0 ships + at least 2 SEs use Layer 4 hooks manually for ~30 days. Real usage data informs which path.

---

### T-102: `mcp-orchestration.md`

**What:** Write the per-repo MCP allowlist policy doc + enforcement mechanism. Charter-aware repos disable external MCP. Customer-product repos allowlist specific MCPs read-only. Meta-scaffolding repos have no MCP.

**Why:** MCP exposure is part of compliance (Layer 2 concern). Without explicit per-repo allowlist, an MCP misconfiguration could exfiltrate customer data through a session.

**Pros:** Compliance posture per-repo becomes explicit + auditable. Reduces blast radius of any MCP misconfiguration.

**Cons:** Requires a session-start check that reads per-repo `mcp-allowlist.yaml` and verifies against active MCP connections. Implementation cost ~2-3 hours.

**Context:** Listed in design doc Layer 4. Deferred per Effort-vs-Scope trade ("no team-shared MCP need yet"). When the team starts using MCPs in customer-engagement repos, promote to v1.2.0.

---

### T-103: `lessons-tagging.md` + quarterly synthesis ritual

**What:** Define the tag schema for `tasks/lessons.md` entries (`#security`, `#agent-selection`, `#adr-drift`, etc.) + a documented quarterly process to scan lessons by tag, identify recurring patterns, and lift them into `CORE-PRINCIPLES.md` via `EVOLUTION.md`.

**Why:** At scale (50+ lessons), lessons.md gets hard to scan. Tagging + synthesis turns lessons from a journal into load-bearing infrastructure.

**Pros:** Recurring patterns surface earlier. CORE-PRINCIPLES.md evolution is grounded in actual incidents, not abstract reasoning.

**Cons:** Requires discipline (quarterly time block, write-up of synthesis outcome). Without that discipline, the tag schema becomes noise without payoff.

**Context:** Listed in design doc Layer 4. Deferred per Effort-vs-Scope ("manual quarterly synthesis works for v1"). Revisit at v1.1.0 if lessons.md exceeds 30 entries.

---

### T-104: `deliverable-provenance.md` template + schema

**What:** Schema (YAML frontmatter + markdown body) for tracking AI-generated vs human-written content in customer-bound demo deliverables. Per-customer-demo `DELIVERABLE-PROVENANCE.md` updated as content lands.

**Why:** Customer-bound output needs auditable origin for IP attribution + customer trust. Pre-sales demos that get handed off to customers need this if there's IP question downstream.

**Pros:** Compliance posture for customer engagement strengthens. Provenance becomes part of the demo deliverable itself, not an afterthought.

**Cons:** Manual updates per content block. Requires SE discipline. Automation (parse git log + claude session log) is non-trivial.

**Context:** Listed in design doc Layer 4 + Open Question 1. Schema recommended in design doc resolution: YAML frontmatter (`source`, `timestamp`, `modifications`, `license_risk`, `verification`) + markdown body. Implementation requires defining the schema THEN integrating with the demo-repo workflow templates (T-105).

---

### T-105: `frontend-mvp.md` + `backend-mcp.md` workflow templates

**What:** Add the two deferred workflow templates to `04-power-user/workflow-templates/`. v1 ships only `customer-demo.md`, `internal-tool.md`, `wiki-content.md`.

**Why:** SEs who do frontend MVPs or MCP server builds repeatedly will benefit from a starting template that pre-fills the PROJECT:START block with the right subagent set + suggested harness.

**Pros:** 15-20 min saved per new repo of that shape. Consistency across SEs doing similar work.

**Cons:** Two more files to keep current. Operator hasn't personally validated these two shapes (per design doc Effort-vs-Scope) so the templates risk being out-of-touch with actual workflow.

**Context:** Listed in design doc migration step 3. Defer until operator has used both shapes at least twice himself (so the template reflects real workflow, not theory).

---

### T-106: Atomic install via staging dir

**What:** Replace the current "leave partial state on failure" install.sh behavior (per C1) with stage-to-temp-then-swap.

**Why:** Eliminates "half-installed" UX completely. If clone of upstream 5/8 fails, ~/.claude-scaffolding/ never gets created from this run.

**Pros:** Cleaner failure mode. No "is my install OK?" debugging.

**Cons:** ~30 LOC of careful filesystem handling. Risk of bugs in the swap logic itself. May not be worth it if partial-state-on-fail is rare in practice.

**Context:** Surfaced as C1 alternative in `/plan-eng-review`. Resolved as "leave partial state + document recovery" for v1. Revisit if partial-install reports become common.

---

### T-107: `yq` auto-bootstrap

**What:** install.sh detects missing `yq` and auto-downloads a pinned binary from upstream releases.

**Why:** Removes the "install yq first" friction. SE on a fresh corp Windows machine without scoop can't get yq quickly; this would unblock them.

**Pros:** One-command install. Truly fresh-machine ready.

**Cons:** Supply chain risk (running an un-pinned curl install). v1 explicitly rejects this for that reason — `install.sh` prompts the user with install commands instead. Revisit only if there's a way to pin + verify yq's hash before execution.

**Context:** Surfaced in design doc Dependencies. Deferred to v1.1.0 with the requirement that any auto-bootstrap include hash verification (matching the `gstack-browse` setup pattern that already does this for bun).

---

### T-108: `scaffold-workspace.sh` for multi-repo workspaces

**What:** Install support for the parent-level CLAUDE.md + symlinked memory.md pattern across child repos.

**Why:** SEs working across multiple related repos (e.g., backend + frontend pair) currently get scaffolding per-repo, losing cross-repo context. A workspace-level scaffold would aggregate insights.

**Pros:** Cross-repo memory accumulates in one place. Single session can navigate parent and reason about children.

**Cons:** Workspace-level files need careful path-resolution. Conflict with per-repo `CLAUDE.md` precedence rules needs spec.

**Context:** Listed in design doc Layer 4 as `multi-repo-workspace.md` (docs-only in v1). T-108 promotes it to install support.

---

## Governance + operational

### T-201: CODEOWNERS for `promoted-agents.md` PRs

**What:** Add `.github/CODEOWNERS` that requires ≥1 CAIP-SE team-member review for any PR touching `scaffolding/03-personal-advanced/promoted-agents.md`.

**Why:** Promoted agents have routing power (Level 2 precedence). An accidental or malicious promotion of a wrong agent could affect every CAIP SE on the team. CODEOWNERS gate prevents single-person promotions.

**Pros:** Promotion process from design doc becomes enforceable, not just documented.

**Cons:** Requires the repo to be in MS-internal GitHub Enterprise with CODEOWNERS support active. Slows velocity for the operator's own promotions.

**Context:** Surfaced as Open Question 2 in design doc. Recommendation: confirm.

---

### T-202: Quarterly upstream re-verify checklist

**What:** Document a quarterly process (calendar reminder, PR template) to re-verify the 8 upstream sources:
- Check that each repo still exists + is public
- Check license hasn't changed
- Update `last_verified: YYYY-MM-DD` field in `upstream-sources.yaml`
- Consider bumping pinned SHA if upstream has had meaningful updates

**Why:** Without a documented cadence, the `last_verified` field becomes lies. Stale upstream-sources is a license-violation footgun.

**Pros:** Manual but rock-solid. Doesn't require automation infrastructure.

**Cons:** Requires discipline (calendar reminder). Easy to skip.

**Context:** Surfaced in design doc Distribution Plan + Open Question. Weekly CI freshness-check already lands in v1; T-202 is the manual review on top.

---

### T-203: CI path-filter for docs-only changes

**What:** Add path-filter to `.github/workflows/ci.yml` so docs-only PRs (only `docs/`, `*.md` changes outside scaffolding/install) skip the full ubuntu+windows matrix.

**Why:** CI matrix runs ~10 min per PR. For a doc fix, that's a lot of wall-clock. Path filter skips matrix on docs-only.

**Pros:** Faster iteration on doc-mostly PRs.

**Cons:** Adds CI complexity. A PR that "looks like docs only" but accidentally touches install logic should still get full matrix — paths need to be carefully scoped.

**Context:** Surfaced in `/plan-eng-review` Performance review. Not v1 blocker — minor optimization.

---

## Notes

- Each TODO has `T-NNN` prefix. v1.1.0 items are T-101 through T-199. Governance/ops items are T-201+. Future categories (T-301+) can be added as discovered.
- When picking up a TODO: read the **Context** line first. It explains WHY this was deferred. If the context has stale assumptions, the TODO may need re-spec.
- Closed TODOs move to `EVOLUTION-LOG.md` with a 1-line "delivered as ..." note.
