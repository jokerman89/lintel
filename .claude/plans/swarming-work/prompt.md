# Cold-executor prompt: first-class swarming work

Read [spec.md](spec.md), [plan.md](plan.md), [design.md](design.md), and [work.json](work.json). BC2 is
the bootstrap lane that builds the validator: before BC2, use the recorded independent plan review
and coordinator scope inspection; after BC2 is integrated, validate the coordination contract before
selecting any later card. The operator authorized this feature through PR merge to `main`.

Preserve the nine-phase cycle and make swarming an opt-in PLAN/BUILD execution profile. The mapped
`tasks` artifact remains authoritative. Coordination artifacts may reference task IDs but must not
copy task prose, dependencies, or checkbox status into a second backlog.

Every worker follows the startup section in its complete card brief, owns only its declared paths,
and writes a separate report. The coordinator alone edits the plan index, plan checkboxes, runtime
job state, generated reducers, manifests, commits, and integration branch.

Use native parallel writer delegation only when every lane has an isolated worktree/patch or an
equivalent host-attributed scope boundary. Otherwise sequence writers, even on a native host.
On sequenced/no-subagent hosts, execute the same briefs serially and label review independence
honestly. Do not rely on hooks, persistent memory, chat history, a daemon, or a network service.

Run focused checks per card and one full suite only after reconciliation. Preserve unrelated user
changes. Stop on a scope breach or conflict; preserve evidence and re-plan rather than silently
resolving another lane's work.
