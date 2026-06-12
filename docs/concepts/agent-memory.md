# Agent memory and model routing

Two optional agent frontmatter keys, Claude-Code-honored, degrading to nothing on other CLIs
(see [ADR-0012](../../.claude/decisions/0012-agent-memory-and-model.md)).

## `memory: project`

Claude Code reads `memory: project` and writes per-subagent persistent memory to
`<repo>/.claude/agent-memory/<name>/`, auto-injecting that agent's `MEMORY.md` on every
invocation. `project` scope is committed, shareable, visible.

Carried by agents whose value **compounds with repo-specific knowledge** across sessions — a
reviewer should remember prior findings in *this* repo ("third off-by-one in this parser").
23 agents: the engineering reviewers (CodeReviewer, TestRunner, SanityChecker,
RegressionDetective, DebugForensics), the full security fleet (SecurityAuditor,
DependencyAuditor, ThreatModelDrafter, ComplianceOfficer, JWT/OAuth/SecretsScan reviewers,
PrivacyBoundaryAudit, SBOMAuditor), the compliance reviewers (EUAIAct, GDPR, SOC2), the
devops config reviewers (GHActions, K8sManifest, Terraform), and the output critics
(WebExperienceCritic, WordTechnicalEditor, DesignSystemAuditor).

### Read-only exclusion rule

`memory:` auto-enables Read/Write/Edit for the agent (platform behavior). We do **not** add it to
agents contracted read-only-and-stateless where memory would mislead — Explorer and ReadOnly are
pure search and stay stateless. Voice critics whose conventions live in the pack (not accumulated
repo memory), e.g. SlideNarrationCritic, are likewise excluded.

### CAPTURE as librarian

At cycle close, CAPTURE (Phase 8) may prune or supersede an agent's `MEMORY.md` the same way it
curates lessons — the curation discipline Lintel already owns. See
[memory-v2](memory-v2.md) for the wider memory map.

## `model: <id>`

Routes a subagent to a specific model instead of inheriting the orchestrator's flagship. Carried by
4 **mechanical** fetch/run/format agents that don't need flagship reasoning, set to the cheaper
`claude-haiku-4-5-20251001`: Explorer and ReadOnly (search), ChangelogMaintainer (format git
history), DocWriter (generate docs from code). Architecture, security, design, and review agents
carry no `model:` and stay on the inherited flagship. A memory-bearing reviewer is never
downgraded — reasoning is the point of giving it memory.
