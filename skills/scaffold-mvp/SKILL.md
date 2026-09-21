---
name: scaffold-mvp
layer: foundation
description: Initialize an MVP around its real users and first working journey, sharing the owned foundation helper and explicit policy, evaluation and deployment boundaries.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

# Scaffold an MVP

Retain the product/MVP intent, user framing, evaluation methodology, reviewable policy
artifacts and deployment preparation. An MVP must do the first requested job for its
users; a large directory tree or a deploy stub is not that outcome.

## Scope the deliverable

Use `--name`, `--target-users`, `--path`, `--stack`, `--has-ai` and `--deploy` as explicit
intent inputs. Ask only for missing decisions. Do not assume TypeScript/Vite/Supabase,
AI usage, a license, a production destination or GitHub CI. Existing architecture,
manifests, data boundaries and accepted decisions remain authoritative.

Define the smallest complete user journey, persisted state/API contract where needed,
access and failure cases, and the evidence that makes it usable. Record deliberate
stubs with their owner and follow-up phase; do not let them satisfy acceptance.

## Reuse the safe foundation

Create the authorized target with the chosen framework/toolchain, then run:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-scaffold" init \
  --target "$target" --name "$name" --mode mvp
```

Follow [scaffold](../scaffold/SKILL.md) and its actual source/target/profile/transaction
contract. Do not independently create legacy ADR or memory paths. Use
`.claude/decisions/` and the selected work map. Preserve project prose, finalized
evidence and existing configuration. Required caller policy cannot be erased by a new
neutral target; child profile binding remains a separate explicit startup operation.

## Build the meaningful product surface

Implement the selected stack's real entry, domain/API/UI boundaries, unit/integration
tests and the first end-to-end flow. Preserve the original specialist concerns:

- Data classification and provenance must describe actual inputs, retention and ownership.
  Draft artifacts are not a completed compliance review.
- For AI features, define sanitized golden and adversarial cases, expected outcomes and
  reproducible evaluation commands. Protect approved golden cases from casual edits.
- Customer-facing guidance uses the actual pack's voice/corpus where configured, without
  inventing calibration or copying private material into public files.
- CI must run actual tools and policy-supported controls; no-op checks or slash-command
  text are not enforcement. Report missing mandatory controls as unresolved.
- Deployment preparation identifies explicit environments, configuration/secrets boundaries,
  observability and rollback. A target file or container build is not a deployment.

Use existing package managers and project conventions. Do not automatically install
dependencies, register hooks, activate external destinations, push a registry image or
trigger staging/production. Those operations need their real authority and host support.

## Verify and hand off

Exercise the actual user journey and its failure/access cases; run relevant build,
type, lint and evaluation checks. Report every placeholder and unrun environment
separately. Keep the exact foundation transaction identity, profile context and
requirements with the selected work evidence, not a competing backlog.

Deliver a reviewable working increment. Independent specification/quality review and
actual deployment/host acceptance remain distinct gates. The internal-tool alias uses
the same initializer for a smaller audience and operational scope.
