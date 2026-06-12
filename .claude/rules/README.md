# Path-scoped rules

One rule per file. Claude Code loads a rule only when files matching its `paths:` globs are
touched; other CLIs see the rule titles in the session digest and read on demand.

```markdown
---
paths:
  - "src/api/**"
---
The API layer never throws raw exceptions across the boundary — wrap in ApiError.
```

Promote a lesson here when it is path-specific (cheaper than loading it every session).
