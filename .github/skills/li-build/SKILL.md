---
name: li-build
description: Use to implement an authorized plan card by card with spec and quality review and verification evidence.
---

# Lintel build

Read the [Copilot adapter contract](../../../shims/copilot/COPILOT.md) first, then execute the
[canonical build workflow](../../../skills/build/SKILL.md) for the user's request.
Resolve source resources relative to that canonical file; write outputs to the working
repository. Follow the adapter's tool mapping, authorization and verification rules.
