# Universal operation adapter

Use this contract with the selected canonical workflow. Its operations describe intent,
not mandatory tool names. The host's actual APIs, repository authority, operator scope
and permissions remain authoritative. A capability record never grants permission.

## Start from the task

Read project AGENTS.md and CLAUDE.md, the shared session protocol, relevant memory and
accepted decisions. Keep the requested operation: an investigation or review does not
authorize edits. Use an existing selected work map and its original spec, plan, task IDs
and handoff. Small fixes need proportionate planning; maintenance does not need a venture
interview. Company policies, retention, technology preferences and audience lenses come
from the project or an explicitly selected pack, never from the client brand.

The trusted source is the directory containing this adapter plus bin/, lib/, skills/
and scaffolding/, normally `.github/lintel/` in a consumer. In the Lintel source checkout
it is the repository root. Resolve it from the loaded wrapper, not an arbitrary working
directory or another user's home. Set `LINTEL_SOURCE_ROOT` to that explicit source and
`LINTEL_REPO_ROOT` to the working project. Invoke Python helpers with Python 3.9+ (`python3`
or `python`) and shell helpers with Bash (Git Bash on Windows); executable bits are optional
when an interpreter is supplied. Do not write project outputs into the source bundle.

For bundled shell helpers, source `lib/copilot-env.sh` from that trusted bundle and call
`lintel_copilot_env` with the working repository. The historic name is retained for the
shared source/target bootstrap; it does not select a Copilot client. Preserve an actual
host-provided session ID or explicitly selected stable work-context ID across fresh shells
and handoffs. Never create a new identity from a shell PID, current time or model name.
Pass the effective profile helper's reference unchanged to children and recovery; do not
invent or reinterpret profile evidence. Missing required policy blocks its affected action.

## Bind the current session

Invocation differs per route: the Claude Code plugin uses `/li:<skill>`; generated native
wrappers use `li-<skill>` through the host's own skill mechanism; a manual route reads
`START.md` and the canonical `skills/<skill>/SKILL.md` explicitly. Canonical references to
`/li:<skill>` in workflows name the skill, not a required syntax.

Read `lib/cli-tiers.yaml` through `bin/li-client-capabilities.py show --client <surface>`.
Choose the exact CLI, desktop, IDE or cloud surface. Legacy aliases select one explicit
surface, not an entire product family. Unidentified hosts can use `other` for manual
handoff. Vendor documentation, delivered files and observed execution are separate fields.
Source-only capabilities remain `not_run`; an installed file is not discovery evidence.

Inspect the host's real tool schemas and permission status. If a deferred tool needs
discovery, use that host's discovery API before naming a binding. Do not probe credentials
or personal settings to fingerprint a client. An optional local session file may record:

```json
{
  "schema_version": 1,
  "session_id": "actual-host-session-or-explicit-work-context",
  "surface": "other",
  "host_version": null,
  "work_map": ".claude/plans/example/work.json",
  "profile_ref": null,
  "bindings": {
    "question": {"tool": "actual.question.channel", "available": true, "permission": "allowed"}
  },
  "isolation": {"kind": "none", "attributable": false, "evidence": null}
}
```

This is an illustrative shape, **not a binding to copy as observed fact**. Fill only actual
inspected tools. Store local declarations under gitignored runtime storage if needed.
Run `python3 <source>/bin/li-client-capabilities.py resolve --session <file>` to check
selection. The helper does not invoke tools, execute work, clear review or prove permission.
Its `declared-session-bindings` result must not be published as a live acceptance result.

## Operations and fallbacks

| Operation | Binding and fallback |
|---|---|
| question | Use the actual question tool, regardless of its name. Only if no such tool exists, ask in conversation. Denial or pending approval is not permission to switch channels. |
| plan | Use native planning UI when present; otherwise create/review the same artifact plan through approved tools. Keep an existing map authoritative. |
| instructions / skills | Discover only from the documented selected surface root. If absent or disabled, explicitly read the canonical file when permitted; never assert native activation. |
| read / edit / shell | Map to available permitted tools and their real schemas. Missing execution tools block the dependent step; a written recipe is not a completed action. |
| browser | Use the actual browser/session tool and record its output. Without one, retain a manual evidence task; search, a profile file or a fictitious daemon is not browser validation. |
| delegate | Use a real separate host context with bounded inputs, ownership and report. Without delegation, execute allowed work serially or export the same package brief for an external actor. |
| isolate | Concurrent writers require disjoint scopes and attributable worktrees, patches or host-scoped writes. Otherwise serialize. A Git worktree is not a security sandbox. |
| memory / resume | Read committed knowledge, the selected work map, reports and unfinished cards. Write target state through approved tools. Optional host memory supplements, never replaces these files. |
| hooks | The existing Claude plugin adapter is optional and separately activated. The portable kit installs none. No file-presence or vendor hook claim proves registration or enforcement. |
| plugin_control / model_control | Use only a documented, available, authorized host API. If absent, report unsupported. Never create `.disabled` files, invent enablement commands or infer model availability from a role. |

Permission `denied` blocks; `ask` or `unknown` requires the real permission path. No fallback
bypasses a denial. Operation selection is not a replacement for host policy.

## Durable manual and serial work

Preserve useful planning, briefs, status, reports and restart even without subagents.
Prepare a package handoff containing the selected work map, exact original leaf text,
acceptance, trusted source, profile reference, base/revision, owned paths, actual checks,
unresolved questions and the next action. Use the installed swarm brief/report templates
when that plan opted in; do not introduce a second task ledger or enable a swarm implicitly.

An independent reviewer must be a separately attributable actor/context with the permitted
scope. The implementer may self-review but cannot clear an independent-review requirement.
Export the review handoff and leave it outstanding until real evidence arrives. Distinct
role labels, model names or two strings in a JSON file do not prove independence.

## Verify the correct layer

`li-adapter init|check` verifies repository files, links, managed ownership and source drift.
It preserves project prose and refuses conflicting edits before writing. It installs no
clients, hooks, MCP servers, credentials, global settings, model settings or permissions.
The source bundle location `.github/lintel/` and knowledge home `.claude/` are compatibility
paths shared by hosts, not evidence that either vendor runs this session.

For live acceptance, record the actual client/version and Lintel revision, discovery,
question path, one authorized plan/build/review task, actual browser evidence if required,
and a fresh-session resume of the same work map. State unrun cases. Public vendor
documentation and local generator tests cannot substitute for this evidence.
