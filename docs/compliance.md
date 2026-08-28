# Compliance

Lintel ships a **small neutral baseline**: three rules, two of which are enforced mechanically. Everything
stricter — regulated-industry gates, data-residency rules, voice enforcement — comes from an installed
**pack**, not from the harness. The harness itself is company-neutral and asserts no regulatory posture.

Read this page as a description of a mechanism, not as a compliance claim. Lintel is not a certification,
an attestation, or a data-loss-prevention system. It is a set of narrow, auditable checks that make the
common mistakes harder to make by accident.

---

## The neutral baseline

Three rules apply on every install, with no pack and no configuration:

1. **No customer data in the repo.** Anything tied to a named customer, tenant, or end user stays out of
   source control. Synthetic and public-domain data is fine.
2. **No secrets in code, logs, commits, or chat.** API keys, tokens, connection strings with credentials,
   private keys. Use an environment variable that resolves from a secret store.
3. **Production mutations need explicit per-call authorization.** Live database changes outside the
   migrations pipeline, deploy-pipeline triggers, image pushes to a live registry, role and firewall
   changes. Auto-mode covers local work; it does not cover these.

That is the whole baseline. It is deliberately short — a longer neutral list would be guessing at
constraints Lintel cannot know.

---

## What is enforced, and what is only advice

| Baseline rule | Mechanism | Effect |
|---|---|---|
| No customer data | `customer-data-block` hook | **Blocks** `git commit` / `git push` |
| No secrets | `secret-scan-block` hook | **Blocks** `git commit` / `git push` |
| No secrets (earlier) | `no-secrets-in-edit` hook | Warns at `Edit` / `Write`, does not block |
| No customer data (earlier) | `no-customer-data-in-message` hook | Warns on your prompt text, does not block |
| Production mutations | none auto-registered | **Advice only.** A warn-only hook exists but is opt-in |

The honest summary: rules 1 and 2 have teeth at the commit boundary. Rule 3 is a checklist item the agent
is instructed to respect. An opt-in hook, `no-production-mutation-without-auth`, pattern-matches a handful
of shapes — a `kubectl` call against a production namespace, `terraform apply` against a production
workspace, a production database client — and warns. It never blocks, and it is off unless you arm it.

**Hooks fire on Claude Code only.** `lib/cli-tiers.yaml` is the source of truth, and Claude Code is the one
CLI with `hooks_supported: true`. On Codex, Cursor, Gemini CLI, OpenCode, GitHub Copilot CLI, Factory
Droid, and everything else, the baseline is instruction text the agent is asked to follow — nothing
intercepts a command. See [multi-CLI support](multi-cli.md) for the full degradation table.

---

## How the two block hooks work

Both run as a `PreToolUse` hook on the `Bash` tool and exit non-zero to stop the call.

**When they fire.** Only when the command contains a `git` invocation with `commit` or `push`. The match
is word-boundary based and survives `git -C some/path commit`, an absolute path to the binary, a
`cd x && git commit` chain, and a newline continuation between `git` and the subcommand.

**What they read.** The added lines of the staged diff plus unstaged changes to tracked files, in the
working directory and in every `git -C` target named on the command line. Not the whole repo, and not
history — a secret already sitting in an earlier commit is not detected.

**What they look for.** Fixed regular expressions, defined once in `hooks/shared/_patterns.sh`:

- Secrets, high-confidence set only: GitHub tokens and fine-grained personal access tokens, OpenAI and
  Anthropic keys, Slack tokens, AWS access key ids, Google API keys, Stripe keys, GitLab personal access
  tokens, storage account keys, and PEM private-key headers.
- Customer data: email addresses, phone numbers, national identity numbers, and a
  person-name-plus-case-id shape.

The warn-only edit hook uses a broader set that adds two heuristics — a hardcoded-password shape and a
shared-access-key prefix. Those are excluded from the blocking hooks on purpose: they false-positive often
enough that blocking on them would be worse than useless.

**What they miss.** There is no entropy scanning and no model in the loop. A credential that does not match
one of those shapes — a bespoke internal token format, a password in an unusually named field — passes
through. Equally, the email pattern is broad: any address in a diff trips the customer-data block,
including a maintainer address in a changelog. Expect to override that one.

**They fail closed.** If the pattern library fails to load while a commit is in flight, the hooks block
rather than allow, and the error message names the override you need.

**They do not see commits you make yourself.** The hook intercepts the agent's `Bash` tool calls. A commit
typed in your own terminal, made from an IDE, or made inside a script the agent merely launches is never
inspected. This is a guardrail on the agent, not on the repository.

---

## Overriding a block

An override is one environment flag on the command, plus a reason, plus an audit record:

```bash
LINTEL_OVERRIDE_SECRET=1 LINTEL_OVERRIDE_REASON="known test fixture, not a live key" git commit -m "test: add fixture"

LINTEL_OVERRIDE_CUSTOMER_DATA=1 LINTEL_OVERRIDE_REASON="maintainer address in changelog" git commit -m "docs: changelog"
```

Three things worth knowing:

- **The flag must be a leading environment assignment**, or already set in the hook's own environment. The
  same token appearing inside a quoted argument — a commit message, for instance — does not count. That
  was a real bypass, and closing it was deliberate.
- **The reason is recorded, not required.** Omit `LINTEL_OVERRIDE_REASON` and the audit record reads
  `no-reason-given`. The flag alone unblocks; the reason is what makes the record useful later.
- **The override is checked before the scan**, so an override always leaves a record — including when the
  content would not have tripped a pattern anyway.

Every fire and every override appends a JSON line to `hooks.jsonl` in the audit trail:
`<repo>/.claude/runtime/audit/` on a repo using the current layout, otherwise `~/.lintel/audit/`. Read it
with `/li:audit` for raw records, or `/li:hooks-status` for the roll-up of which hooks are firing and how
often they are overridden.

The audit trail is an append-only local file. It is not tamper-evident and it is not shipped anywhere:
anyone who can write to the repo can edit it. Writes fail open — a full disk produces a warning on stderr
rather than a failed commit — so absence of a record is weaker evidence than presence of one.

---

## Which hooks are on by default

The repo carries **33 hooks**. On a plugin install, **9 auto-register** through `hooks/hooks.json` with no
setup on your part:

| Hook | Trigger | Kind |
|---|---|---|
| `secret-scan-block` | Bash | **block** |
| `customer-data-block` | Bash | **block** |
| `no-direct-main-push` | Bash | warn |
| `no-secrets-in-edit` | Edit / Write | warn |
| `no-customer-data-in-message` | your prompt | warn |
| `cycle-incomplete-warn` | turn end | warn |
| `memory-budget-warn` | Edit / Write | warn |
| `session-digest` | session start | context |
| `cycle-position-inject` | your prompt | context |

The other 24 ship inert — including `no-production-mutation-without-auth`, `no-merge-without-review`,
`frozen-zone-warn`, and the per-module warning hooks for architecture, data, security, devops, and
testing. Arm one by symlinking its `run.sh` into your hooks directory and adding a matching entry to your
CLI settings. Nothing edits your settings file for you.

A bare install from `install/install.sh` copies every hook inert; **nothing auto-registers on that path**.
[How hook activation works](getting-started.md#how-hook-activation-works) is the canonical explanation and
wins over any other description, including this one.

---

## Advisory and hard mode

The active pack declares a compliance posture in one field, `compliance.mode`, with three values:
`advisory`, `hard`, or `off`. The neutral `_default` pack is `advisory`.

**Advisory** — what you get out of the box. SENSE reports the mode at the start of a cycle. The pack's
gates, if it declares any, are surfaced but not blocking. `_default` declares none, so
`/li:compliance-gate` returns green with a note that no compliance pack is active.

**Hard** — only reachable by installing a pack that sets it. The pack's declared gates become enforced
rather than advisory; SHIP runs them as a stop the cycle will not proceed past; the pack's voice tier
applies automatically to customer-facing output; and customer-repo context loads and URL fetches are
audit-logged.

**One thing the mode does not change: the two block hooks.** No hook reads the active pack. They block
under `advisory`, under `hard`, and under `off` alike. Hook activation is an install-time and
settings-level decision, entirely separate from pack compliance mode. Making hook behaviour pack-driven is
a known open gap, not a shipped feature — do not plan around it.

---

## What a pack can add

Compliance fields available to a pack manifest, from the schema of record in `lib/pack-schema.yaml`:

| Field | Required | Meaning |
|---|---|---|
| `mode` | yes | `hard` / `advisory` / `off` |
| `hooks` | no | Named gates the pack contributes. `_default` declares an empty list |
| `audit_paths` | no | Where the pack's compliance audits are written |
| `data_residency` | no | `us` / `eu` / `apac` / `none` — default `none` |
| `workprofile_default` | no | `on` / `off`. A legacy carry-over: SENSE surfaces it, nothing in the neutral spine acts on it. A pack that sets it defines what it means |

`compliance.hooks` is the main extension point. `/li:compliance-gate` resolves that list and runs all of it
as one green-or-red verdict, so you do not have to remember which gates apply to a given artifact. No gate
names are built into Lintel; each pack owns its own list.

A pack is also a plugin, so an extension pack can ship its own `hooks/` tree that the host CLI registers
alongside Lintel's — that is how a pack adds genuine enforcement rather than instructions.

What a pack **cannot** do: switch off the two baseline block hooks, or make anything fire on a CLI that
does not run hooks. See [pack defaults](concepts/pack-defaults.md) for the full neutral baseline and
[pack resolver](concepts/pack-resolver.md) for how a field is looked up.

---

## The session-start check

Separate from the hooks, and applying on every CLI: the agent is instructed to walk a short checklist
before any non-trivial action. It is operator-confirmed, not automated — the harness surfaces the items,
you confirm them.

1. **Authority scope** — is this work inside what the repo's instruction file or the operator authorized?
   If unclear, ask. Scope does not silently extend to adjacent repos.
2. **Customer data** — could anything here be customer data? If yes: stop, do not read further, escalate.
3. **Production mutation** — will this change a shared or live system? If yes: get per-call authorization.
4. **Secrets** — is a secret entering code, logs, a commit message, or shared chat? If yes: stop and ask
   for a secret-store reference instead.
5. **The active pack's gates** — none under `_default`.

Trivial work — a typo fix, a question, a documentation edit — skips it.
[AGENT-INSTRUCTIONS.md](../AGENT-INSTRUCTIONS.md) is the canonical form of this ritual.

---

## When a rule has been broken

The same cleanup pattern the core principles apply to any crossed boundary:

1. Stop. Do not push on hoping the next step undoes it.
2. Verify current state with read-only checks.
3. Report honestly — what was done, the state now, the risks.
4. Propose concrete options with trade-offs. Do not ask for absolution.
5. Wait for explicit authorization before rolling back or continuing.

---

## Adding rules for your own repo

Repo-specific rules go in that repo's own `CLAUDE.md`, or as a path-scoped rule under `.claude/rules/` when
they apply only to a subtree. They **add** to the baseline; they do not subtract from it. Where two
instruction sources disagree, [precedence](precedence.md) decides.

Traceability is what makes the rest reviewable: atomic commits, a decision record in `.claude/decisions/`
for anything non-obvious, and corrections captured in `.claude/memory/lessons.md`. A reviewer should be
able to reconstruct the reasoning without asking you.

---

## What Lintel does not do

Stated plainly, because these are the questions a skeptical evaluator asks:

- **No third-party code is installed, vendored, or updated.** Lintel ships only its own content. The
  installer clones nothing — `install/upstream-sources.yaml` is a declaration file that the installer
  reads and counts, and the installer's own output says so. There is consequently no upstream update
  workflow, no re-verification schedule, and no third-party license obligation passed on to you beyond
  Lintel's own `LICENSE`.
- **No uninstall script.** Removing a bare install means deleting `~/.lintel/` and any hook symlinks you
  created yourself.
- **No network egress control.** Nothing stops an agent from calling an external service with data it
  should not send. Rules 1 and 2 are checked at the commit boundary, not at the socket.
- **No enforcement outside Claude Code.** Repeated because it is the single most important limitation.
- **No secret rotation and no incident response.** If a secret does reach a remote, treat it as compromised
  and rotate it. [SECURITY.md](../SECURITY.md) covers reporting a vulnerability in Lintel itself.

---

## Reviewing this baseline

Revisit it when a new policy lands that affects agent-based development, when an incident reveals a missing
rule, or when a rule has been overridden repeatedly — a frequently overridden rule is usually wrong rather
than usefully strict. `/li:hooks-status` gives you the override counts to make that call on evidence.

Changes to the baseline are load-bearing: record them in `scaffolding/01-foundation/EVOLUTION-LOG.md` as a
`CORE` entry, since that log travels with the scaffolding into every repo it has been installed in.

---

Related: [architecture](architecture.md) for where hooks sit in the system ·
[the cycle](the-cycle.md) for where the gates fall in a run · [documentation index](README.md).
