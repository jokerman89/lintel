---
name: li-plan
description: Use to turn a design into a requirement-traced spec, dependency-ordered build cards and a cold-executor prompt.
---

# Lintel plan

Read the [Copilot adapter contract](../../../shims/copilot/COPILOT.md) first, then execute the
[canonical plan workflow](../../../skills/plan/SKILL.md) for the user's request.
Resolve source resources relative to that canonical file; write outputs to the working
repository. Follow the adapter's tool mapping, authorization and verification rules.
