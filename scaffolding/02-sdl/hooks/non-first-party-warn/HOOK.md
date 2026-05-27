---
name: non-first-party-warn
tier: warn-only
event: PreToolUse (Edit | Write) on package.json / requirements.txt / pyproject.toml / Cargo.toml
fires_on: edit adds a known-3P dep with viable MS-1P alternative
override: pass --justify-non-first-party to invoking skill (logged)
audit: ~/.jstack/audit/hooks.jsonl
---

# non-first-party-warn

Warns when an Edit/Write on a manifest file appears to add a third-party dep that has a documented MS first-party alternative (per `~/.jstack/first-party-alternatives.yaml`).

## Detection

- Triggered on Edit/Write targeting package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod, pom.xml
- Diff the new payload against existing manifest (rough text diff)
- For each new dep added: cross-reference the alternatives YAML

## What it surfaces

- "Adding `@auth0/auth0-react`. First-party alternative: Microsoft Entra ID via @azure/msal-react. Justify in commit message or migrate."

## Why warn-only

First-party-first is a preference, not a rule. There are valid reasons to pick 3P (legacy compat, specific feature, customer mandate). Warn surfaces the choice for explicit decision.

## Companion: /first-party-check skill

This hook is the pre-action surface. The skill is the periodic audit. Both write to the same alternatives YAML.
