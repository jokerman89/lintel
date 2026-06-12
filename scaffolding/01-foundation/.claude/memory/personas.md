# Personas

Operator-facing personas active in this project. Loaded at session start so the assistant knows who it is collaborating with and how to communicate.

Different from `working-state.md → Operator profile`: that is a free-form notepad. This file is structured per-persona, and gets loaded as authoritative context.

---

## How to use this file

For each active operator persona, add a `## Persona: <name>` section below. Use the structure shown in [personas-example.md](personas-example.md) as a reference.

A persona is worth writing when:

- The operator has a distinct role (CEO vs IC vs SRE) that changes how the assistant should respond.
- The operator has communication preferences strong enough that mistakes cost trust.
- Multiple humans share the project and the assistant needs to know who is in front of it.

If only one operator works with this repo, one persona is enough. Do not write personas for hypothetical users.

---

## Active personas

<!-- Add `## Persona: <name>` sections here. See personas-example.md for the structure. -->

---

## When personas change

Personas are not static. When a role shifts (new responsibilities, new team, new project phase), update the persona file. Do not delete the old version — date the section as `<name> — superseded YYYY-MM-DD` and keep it below the active section. Old context is sometimes needed to interpret old lessons.
