# Path-scoped rules

One rule per file. Claude Code loads PROJECT-level rules (`./.claude/rules/`) conditioned on
`paths:` frontmatter — globs MUST be quoted (`"src/api/**"`, unquoted globs fail silently) and
user-level (`~/.claude/rules/`) path-scoping is broken as of mid-2026. Other CLIs see the rule
titles in the session digest and read on demand.

```markdown
---
paths:
  - "src/api/**"
---
The API layer never throws raw exceptions across the boundary — wrap in ApiError.
```

Promote a lesson here when it is path-specific (cheaper than loading it every session).
