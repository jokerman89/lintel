---
name: scaffold-mvp
layer: foundation
description: Use for the retained MVP scaffold entry; delegates real-user and first-journey intent to scaffold's owned method in mvp mode, preserving evaluation and deployment boundaries.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Scaffold an MVP

Delegate to [scaffold](../scaffold/SKILL.md#application-mode-acceptance-one-owner)
with the existing `--mode mvp`. Preserve supplied `--name`, `--target-users`,
`--path`, `--stack`, `--has-ai`, `--deploy`, existing answers, selected work/profile
and authority. These are intent inputs, not new flags for the initializer.

Scaffold owns the first-journey success/failure questions, sanitized golden and
adversarial evaluation method, data/policy/voice concerns and actual
`bin/li-scaffold init` operation. Do not repeat its interview or foundation recipe.
Keep user framing and deployment preparation distinct from actual deployment.

Follow that owner's source/target, collision, profile and recovery checks,
no-install without authority, actual journey verification and independent
review/host handoff gates. A directory tree or deploy stub is not a working MVP.
