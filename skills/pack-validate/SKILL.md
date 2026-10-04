---
name: pack-validate
layer: foundation
description: Validate a pack before activation or after editing its manifest. Checks effective required fields and inheritance with the shared resolver, then reports schema and version compatibility limits.
color: green
tools: Read, Bash, Grep
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Pack validate

Retained read-only front door to [pack lifecycle: validate](../pack-switch/references/lifecycle.md#validate).
Follow its existing parser, effective-field/inheritance, schema/version,
required-policy, pattern-resource and result-reporting procedure.

An omitted name means the actual effective pack. A malformed manifest, stale reference
or failed required policy is not neutral success. Validation does not bind, activate,
synchronize, install a host plugin or prove that a control ran.
