---
name: li-sense
description: Use at session start to load relevant memory, inspect repository state and scope the request.
---

# Lintel sense

Read the [Copilot adapter contract](../../../shims/copilot/COPILOT.md) first, then execute the
[canonical sense workflow](../../../skills/sense/SKILL.md) for the user's request.
Resolve source resources relative to that canonical file; write outputs to the working
repository. Follow the adapter's tool mapping, authorization and verification rules.
