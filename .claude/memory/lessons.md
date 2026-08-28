# Lessons learned — Lintel

Durable rules accumulated from corrections. Review at session start; add after any correction.

> Format per entry: short rule first, then `Why:` (the incident or principle), then `How to apply:` (when this kicks in). Link related lessons with `[[name]]`.
>
> Supersede, don't delete: entries are never edited away — a contradicted lesson gets `superseded_by: L-NNN (YYYY-MM-DD)` as its first body line and is then skipped by surfacing (`lib/memory.sh`).

---

## L-001 — Lintel is scaffolding, not curated content

**Rule:** Lintel ships structure (templates, tests, agent-mapping, invocation skills) and **one** canonical deep example per pattern. Operator + AI generate the rest of the content at invocation time. Pre-building a catalog of curated content in the repo is anti-pattern.

**Why:** During v3.5 az-tldr build I shipped `azure-openai.md` (268 lines, 15 sections + §16) as a "2nd weapon" after `expressroute.md`. Operator caught it: *"Behöver inte göra fler services, endast för mall och exempel … vi är scaffolding och ett system, vi är Lintel som skapar struktur så att ordning kan uppstå nedanför."* Pre-built content rots (model catalog moves in months, pricing in weeks), bloats the repo, and does the AI's job ahead of time — duplicating work that should happen at the moment of customer engagement.

**How to apply:**
- For any new toolbox (`az-tldr`, future siblings): ship template + structural test + **one** deep example (dogfood) + agent-mapping skeleton. Stop there.
- If tempted to build a "2nd weapon" to "prove the pattern scales": instead write a one-paragraph note in the catalog README explaining how to add one. The pattern is proven by the *template + test + agent-mapping*, not by content count.
- Content lives in two places, both NOT the repo: (a) operator's private notes (~/.lintel/private/), (b) generated fresh per invocation by agents reading current MS Learn / RAI standards / pricing pages.
- Catalog README's `⚠ template only` rows are a feature, not a gap — they signal that the slot exists and what agent dispatch it would use, without pre-paying the curation cost.
- Same principle applies to any future "weapons catalog" pattern: roles, modes, voice cells, compliance gates. Ship the structure + one example.

Related: scaffolding-vs-content principle is the v3.5 lake-of-bloat avoidance rule — every "let me add one more example" instinct is the lake refilling.

---

## L-002 — Grep existing skills before designing a new family

**Rule:** Before architecting a new skill family or major addition, enumerate existing `skills/` for prior infrastructure that touches the same domain. Don't trust assumed greenfield. Use `ls skills/` + `grep` for related verbs/nouns in SKILL.md frontmatter — at minimum 30 seconds of investigation before locking design premises.

**Why:** During /office-hours design session for the doc-gen "forge" family, I locked four design decisions (D1-D4) before discovering that `skills/generate-ppt/`, `skills/generate-web/`, and `skills/generate-word/` already existed with 4-gate quality pipelines + brand-template-pulls + voice-gating. Operator had to redirect the entire design at D5 from "forge from scratch" to "evolve generate-namespace + refactor existing." If I had run `ls skills/ | grep generate` at Phase 1 (Context Gathering), the discovery would have shaped D1-D4 differently from the start, avoiding the design backtrack.

**How to apply:**
- In any /office-hours or design-mode invocation: Phase 1 includes `ls skills/ | head -50` + `grep -l "<domain-keyword>" skills/*/SKILL.md` as mandatory steps, not optional. Apply even if you "know" the repo.
- When user gives an inspiration doc (DECKFORGE-style), grep the repo for any of the inspiration's verbs/nouns (here: `generate`, `ppt`, `doc`, `web`, `pdf`) before mapping inspiration to design.
- If discovery surfaces existing infrastructure: explicitly state "premise reset" before re-asking design questions. Don't paper over.
- The cost of 30 seconds of investigation is always less than the cost of re-designing after operator catches the gap.

Related: [[scaffolding-not-content]] — both lessons are about respecting what already exists before adding more. L-002 catches the case where "what exists" was infrastructure I missed; L-001 catches the case where "what doesn't need to exist" was content I shouldn't have added.

---

## L-003 — Verify counts before applying "truth-fix" from external docs

**Rule:** When an external document (backlog, audit report, third-party analysis) claims a specific count or fact about the codebase ("78 agents", "5 hooks", "12 compliance skills"), VERIFY the count via tool (`find | wc -l`, `grep -c`, `ls`) BEFORE applying any "fix" to docs. The external document may itself be wrong — applying its claimed-correct value as a fix would introduce the bug.

**Why:** v3.6 backlog (Cohort 1 item 0.1) claimed "Agent count is 73, not 78. The '78' in README is wrong. Correct everywhere." I ran `find agents -name '*.md' | grep -v README | wc -l` before "fixing" the README and discovered the actual count was **78** — exactly what the README already said. Per-category sum confirmed: 5+6+8+7+3+25+15+8+1 = 78. The backlog-author miscounted (possibly stale tree at compile-time). If I had applied 78→73 mechanically, I would have introduced the bug the docs were correctly avoiding. Caught by `find`-verification before edit.

**How to apply:**
- For ANY "fact-fix" from external doc: run a verification command BEFORE the edit. Cost: 30 seconds. Benefit: prevents introducing bugs from miscounted external claims.
- Document the verification command + result in the PR description (so reviewers can re-verify): `Verified via: find agents -name '*.md' | wc -l = 78. Backlog's claim of 73 is wrong. SKIPPING 0.1.`
- Pattern applies to: file counts, line counts, version numbers, configuration values, metric claims. Any claim that can be tool-verified.
- The same principle generalizes: external documents are inputs to think with, not commands to execute mechanically. Even your own past output (compiled backlog) is an external document that may have been wrong at compile-time.

Related: [[L-002]] grep-first-before-design — L-002 says grep existing infrastructure before designing; L-003 says grep external claims before believing. Both apply the same skepticism in different directions. The trio L-001/L-002/L-003 form a discipline: respect what exists, respect what doesn't exist, and verify claims about what exists.

---

## L-004 — Separate decision-layer from rendering-layer when both could plausibly own the scope (v3.7)

**Rule:** When designing a new skill family that could plausibly extend an existing family OR stand alone, decide by asking: "does this make decisions, or does it execute decisions?" Split by decision vs execution, not by feature-coverage. Decisions live in one family; execution lives in another. The schema between them IS the boundary contract.

**Why:** During v3.7 frontend-design-system design, operator picked option B (new `frontend-*` family) over my recommended A (extend `generate-*`). Initial instinct: A is simpler (fewer families). But A would have mixed decisions (typography choice, motion language) with execution (HTML file-output), making both harder to evolve. B with explicit separation — frontend-* owns design-director-decisions, generate-* owns rendering-engine-execution, `frontend-design-spec.json` is the contract — let each family grow independently. `frontend-shader` + `frontend-style-extract` (A2) + `generate-app` (B, new) all land cleanly without touching the other family. /plan-eng-review caught a near-collision (M-1: `design-spec.json` filename in both modes) precisely because the boundary was explicit; without the boundary, the collision would have been silent.

**How to apply:**
- When operator picks "B = separate family" over "A = extend existing": don't argue, design B properly. Build the explicit boundary table (which concern lives in which family) as part of the design doc.
- The boundary contract is the schema. Both families version the schema (M-5 `schema_version: 1`) + use source-discriminator (M-1 `source: "frontend-design"` vs `source: "pipeline"`).
- New sub-skills in either family must respect the boundary. If a sub-skill straddles (v3.7's original `frontend-app-scaffold`), rename it into the correct family (became `generate-app` in generate-* per M-2).
- Pre-existing infrastructure check: enumerate existing schemas/filenames that the new family will write or read. If filename collision possible, differentiate proactively (`frontend-design-spec.json` ≠ `design-spec.json`).

**Why this is durable, not v3.7-specific:** any future feature that "could be part of X or could be its own thing" should follow the decision/execution split. Examples ahead: a future `personalize-*` family might split into `personalize-decision` (audience-targeting, channel-pick) vs `generate-*` (delivery). Same pattern.

Related: [[L-001]] scaffolding-not-content (frontend-* family ships scaffolding + 1 canonical pattern, agents produce content at invocation), [[L-002]] grep-first (boundary table proved generate-* already existed + needed respect), [[L-003]] verify counts (M-1 collision caught via grep of generate-web SKILL.md before merge). The lesson-quartet now: respect existing, respect non-existing, verify claims, separate decisions from execution.

---

## L-005 — A removal/de-bias sweep is only as complete as its widest token set (v4.7)

**Rule:** When grepping to find everything that references content you're extracting or genericizing, the FIRST grep must enumerate every shape the reference can take: lowercase skill-folder names AND their `RAIS`-style uppercase tokens AND bare agent/class names AND path strings. A token set that only has the "obvious" tokens will silently miss a whole class of callsites, and you'll discover them only when tests fail or a second sweep runs.

**Why:** During the v4.7 CAIP extraction, my first sweep used tokens like `RAIS`, `Trailblazer`, `WorkProfile`, `first-party`. It matched ~437 lines across ~130 files — but `RAIS` is case-sensitive, so lowercase skill refs `/li:rais-customer-voice-check` did NOT match, and bare agent names like `AzureArchitect`/`FirstPartyMigrator` weren't in the set at all. ~25 files (more `generate-*`, all `frontend-*`, `discover`, `install.sh`, AGENT-INSTRUCTIONS Layer refs) were never assigned to a de-bias batch. A second, broader sweep (lowercase skill names + every removed agent name + paths) found them. This is L-003 applied to my own search: verify the search is complete before trusting "0 results."

**How to apply:**
- Build the token set from the actual removed inventory: for every removed skill, add both `skill-folder-name` and any in-prose token; for every removed agent, add the exact `CamelCaseName`; for every removed dir, add the path.
- Run the sweep case-insensitively (`grep -i`) OR include both cases explicitly.
- After the de-bias, re-run the WIDEST sweep and require 0 hits (excluding intentional mentions) before committing — don't trust the first sweep's file list as the full scope.
- Let tests be the backstop, not the discovery mechanism: tests that assert presence of removed content (layer values, alias entries, file existence) will fail and reveal residue — but finding it via grep first is cheaper than via a red test suite.

Related: [[L-003]] verify-counts-before-fact-claims — L-003 says verify external claims; L-005 says verify your own search's completeness. Both are "don't trust the first number." [[L-002]] grep-first — L-002 greps before designing; L-005 greps comprehensively before declaring a sweep done.

---

## L-006 — The factory must run on itself: dogfood your own tooling (v4.8)

**Rule:** When a repo's purpose is to produce tooling/discipline for OTHER repos (scaffolding, a harness,
a generator), it must ALSO apply that tooling to itself. If it doesn't, the gap stays invisible until
someone notices the cobbler's children have no shoes.

**Why:** Lintel ships `scaffolding/01-foundation/` (CLAUDE.md template, `.claude/agents/`, `docs/adr/`,
CORE-PRINCIPLES) to install into other repos — but never ran `li-scaffold` on itself. So Lintel's own
root had no `.claude/`, no `docs/adr/`, and a thin v3 CLAUDE.md. Throughout the large v4.7 CAIP
extraction I produced a structure-change doc + lessons + todo but **zero ADRs** for major decisions
(pack-on-top vs fork, aggressive de-MS, clean-copy vs filter-repo), because the repo had no ADR
infrastructure and CLAUDE.md didn't enforce the ritual. The operator caught it. The factory works in
sister repos (deeplex has scaffolded CLAUDE.md + living lessons + decisions) — it just never ran here.

**How to apply:**
- When working in a repo whose job is to generate scaffolding/tooling/discipline, check at session start:
  does THIS repo carry its own output? If `li-doctor` (or equivalent) reports "missing its own
  scaffolding," fix that before anything else.
- Before executing a multi-step initiative, verify the decision/lesson infrastructure exists (`docs/adr/`,
  `tasks/lessons.md`). If it's absent, FLAG it — don't silently skip ADRs because there's nowhere to put
  them.
- Add a self-check to the tooling so the failure is caught for every adopter, not just the maintainer:
  `li-doctor` now warns when a repo using Lintel lacks its own `.claude/`/`docs/adr/`/scaffolded CLAUDE.md.

Related: [[L-003]] verify before acting — here, verify the meta-process infrastructure exists before
relying on it. The discipline only compounds across sessions if the snowball (lessons + ADRs) has a
place to accumulate.

---

## L-007 — REVIEW via an independent subagent, but verify the reviewer too (v4.10)

**Rule:** For any meta-infra change, run REVIEW as an *independent* CodeReviewer subagent on the real
diff before SHIP — self-testing systematically misses a class of bugs. AND treat the reviewer's report
as an input to verify, not a verdict to execute: trace each finding to the actual code/contract before
acting. The reviewer can both over-state (a "collision" that isn't) and under-state (its claim leads you
to a *deeper* real bug).

**Why:** Building the cycle-position footer (v4.10), my own 30-assertion unit suite was green and I was
ready to ship. An independent CodeReviewer subagent found a **P0 hang** I'd missed entirely: a trailing
value-flag (`render_cycle_footer --mode`) made `shift 2` fail-without-consuming → infinite loop in the
closing footer of *every* report. Self-testing missed it because I only ever tested well-formed calls.
But the same review's P1-C ("rename collides with Phase-6 review's log entries") was *overstated* — when
I traced the contract, the merge-hook keys on `commit`+`status:CLEARED`, NOT the skill tag, and Phase-6
`/review` doesn't log at all, so there was no live collision. Tracing it, however, surfaced a *genuine*
pre-existing bug the reviewer hadn't framed: the hook read `~/.lintel/review-log/entries.jsonl` while the
logger writes `~/.lintel/audit/reviews.jsonl` (and matched full-vs-short sha) — the gate was dead. So the
reviewer was simultaneously wrong about the stated risk and pointing at a real one.

**How to apply:**
- Meta-infra diff → spawn an independent reviewer (one task, read-only, structured severity report) before
  SHIP. Don't review your own work in-context; you share its blind spots.
- Make the reviewer adversarial and feed it a REAL diff (a no-op tree lets a reviewer rubber-stamp — the
  superpowers #1701 failure mode). Fail closed on "nothing changed."
- For EACH finding: open the cited code/contract and confirm before acting. Downgrade overstated ones,
  and follow the thread — an overstated finding often sits next to a real one.
- Close the gap between asserted and tested: when an ADR claims a property ("fail-open, never errors"),
  add the tests that prove it. The reviewer's value is partly in exposing claims you never tested.

Related: [[L-003]] verify-counts-before-fact-claims — L-003 says verify external claims before believing;
L-007 extends it to a reviewer's claims ("subagent reports, main agent decides"). Both: don't execute an
external document mechanically. [[L-006]] dogfood — the footer feature was itself built by running the
cycle (SENSE→…→REVIEW) on Lintel, and REVIEW is where the discipline paid off.

## L-008 — Dogfood the footer: every report in Lintel work ends with the position footer (v4.11)

**Rule:** When working in (or on) Lintel, close every substantive report to the operator with the
cycle-position footer — `render_cycle_footer` (lib/cycle-footer.sh), explicit `--here/--mode` flags
when working ad-hoc outside a skill-driven cycle. The convention shipped in v4.10 applies to the
agent's own reports, not just skill output.

**Why:** Operator correction (2026-06-10): mid-v4.11 I reported progress repeatedly with no footer —
the exact "big report, no position, no next action" gap the v4.10 feature was built to close. The
factory must run on itself ([[L-006]]); a convention we ship but don't follow reads as dead on arrival.

**How to apply:** At the end of any status/progress/completion message in this repo: where are we,
what's next, what to say to proceed. Use the real helper, not a hand-typed imitation, so drift in the
helper surfaces immediately.

## L-009 — Never pipe a test runner through tail/head: the pipeline eats the exit code (v4.11)

**Rule:** Run suites as `rc=0; runner > out.txt 2>&1 || rc=$?` and inspect the file — never
`runner | tail -N`. A pipeline's exit status is the LAST command's; `| tail` reports success even
when the suite failed, and `-N` can clip the summary block that says FAILED.

**Why:** v4.11 Phase A: the full suite FAILED (phase-a-naming-migration expected the removed
context-budgetwatch) but my `| tail -6` invocation returned rc=0 and clipped the summary — I reported
"green" on a red tree and nearly committed it. Same family as the runner's own fail-closed fix shipped
in this very phase: silence is not success ([[L-003]]).

**How to apply:** Capture to a file, echo `$rc` explicitly, read the summary from the file. In CI
scripts, `set -o pipefail` if a pipe is unavoidable.

## L-010 — Green is measured on the committed tree, not the working tree (v5.0)

**Rule:** Before claiming "suite green" for a commit/PR, run the suite AFTER the commit (or
verify the index state explicitly for mode-bit/path-sensitive checks). A working-tree run can
pass while the committed tree fails — file modes (`git ls-files -s` vs `chmod`), untracked
files that tests skip, and CRLF normalization all differ between the two.

**Why:** v5.0 Phase C: `bin/li-vault-init` was chmod +x in the working tree, so my pre-commit
suite run was 74/74 green — but the file was committed 100644 and `bin-scripts-executable.sh`
fails exactly that. The independent reviewer's post-commit run caught the red suite that my
own "green" claim missed. Same family as [[L-009]] (a verification step that reports success
while measuring the wrong thing).

**How to apply:**
- After committing, re-run at least the shape suite on the committed state — or use
  `git update-index --chmod=+x` at creation time for every new executable.
- For stacked PRs: the suite that counts is the one on the pushed HEAD.
- Reviewers: always run the suite yourself on the actual commits (this is what caught it).

Related: [[L-009]] silence-is-not-success, [[L-007]] independent review catches self-test blind spots.

## L-011 — Structural metrics give subtraction CEILINGS, not targets (v5.1)

**Rule:** When an audit estimates removable surface from structural metrics (line counts of
boilerplate-shaped sections, duplication counts), treat the number as a ceiling. The actual
cut is decided by a judgment pass per file — and will land meaningfully lower, because
sections that pattern-match "ceremony" often carry real gates.

**Why:** The v5.1 subtraction: the fit audit measured ~30-38% (5.4-8.2k lines) of ceremony;
the judgment-applied diet removed ~700 lines of it — the rest was customer-data gates,
license confirms, verdict taxonomies and operator pause-gates wearing boilerplate headings.
Total release still cut 23% (6.2k lines) because the FILE-level cuts (35 single-caller
sub-skills, role CRUD) delivered what the SECTION-level diet could not. Plan subtraction
around structural units (files with one caller, zero refs), not prose-shaped estimates.

**How to apply:**
- Audit phase: report both numbers — the structural ceiling AND a sampled judgment estimate.
- Execution: give diet agents keep-by-exception rules and require per-file justification for
  keeps; the exceptions list is the real finding.
- Don't chase the ceiling: stopping at "everything left deviates from the default" IS done.

Related: [[L-003]] verify counts — same family: a measured number is an input to judgment,
not a commitment.

## L-012 — A security fix that re-opens a forgeable hole is worse than the gap it closed (v5.2)

**Rule:** When hardening a control, the fix must not introduce a NEW bypass that's easier or
more deniable than the original. Especially: never let attacker-influenced text (a commit
message, a branch name, an LLM-generated arg) flip a control off. After any security edit,
write the NEGATIVE test — prove the thing you think you blocked is still blocked AND that the
new code can't be talked around — before claiming it closed.

**Why:** v5.2 battletest. Closing H8 (inline override left no audit) I made the block hooks
honor `LINTEL_OVERRIDE_SECRET=1` found ANYWHERE in the command string. The independent reviewer
showed `git commit -m "see LINTEL_OVERRIDE_SECRET=1"` then suppressed a real secret block —
prose in a commit message defeated the gate, and the audit recorded a legitimate-looking
override. That is strictly worse than the pre-fix state: it READS as enforced. The green suite
missed it because it only tested the legitimate override path, never the forgery. Fix: honor
the token only as a leading env-assignment prefix (never inside a quoted arg) + a negative
regression assertion.

**How to apply:**
- For every control edit, add both a positive (blocks the bad thing) AND a negative (can't be
  trivially talked around) behavior assertion. The negative test is the one that matters.
- Treat any string the agent/attacker can influence (commit message, branch, filename, arg) as
  hostile input to a control — never a trust signal.
- "Fail-safe direction" (over-block) is acceptable; "fail-open via forgeable input" is not.

Related: [[L-007]] verify the reviewer's claim — here the reviewer was exactly right and live-
verified the exploit; [[L-010]] green-on-committed-tree — the suite was green AND wrong because
it tested the happy path only. Behavior tests must include the adversarial path.

## L-013 — "Make it ours" means reinvent the substance, not remove the attribution word

**Rule:** When the operator says "make it ours / go all in / live up to the name," that is an
instruction to REINVENT — rewrite the content end-to-end in Lintel's own voice, structure, and
model so the result would stand on its own with no ancestor. Deleting the word "gstack" (or
"heavily inspired by X") from prose is de-heritage, NOT reinvention. They are different jobs and
the small one masquerades as the big one.

**Why:** v5.3 lineage cleanup. I removed gstack references and reported the spine "ours." The
operator caught it cold — "did you for example look at all gstack skills and rewrote everything
end to end to make it ours?" — then escalated: "Everything should be done, we dont half-ass
anything … Do the full engaged refactor … go all in here and do this the best way." I had done
a find-and-replace and called it ownership. The actual work was reinventing 12 spine skills in
Lintel's own idiom (ADR-0013). De-heritage is cheap and invisible; reinvention is the deliverable.

**How to apply:**
- Hear "make it ours / our vision / live up to the name" as a REINVENT verb. Scope the full
  rewrite, not a terminology sweep. If unsure which is wanted, ask — but default to the larger.
- Test your own output: "would this stand on its own with the ancestor deleted, or does it just
  avoid naming the ancestor?" If only the name is gone, you de-heritaged; you did not reinvent.
- "Heavily inspired by X" in our own README is a smell: either earn the independence or keep the
  honest attribution. Don't quietly drop the credit while keeping the borrowed substance.

Related: [[L-001]] scaffolding-not-content — both are about doing the real work, not the
work-shaped gesture. L-001 catches doing too much (pre-building content); L-013 catches doing
too little (a rename dressed as a reinvention).

## L-014 — Illustrative bash in a skill is shipped code; never dereference an unbound var

**Rule:** Bash shown inside a SKILL.md (gates, examples, "run this") is read as authoritative and
gets copy-run. Hold it to the same bar as committed code: every variable is derived or guarded
before use, no `$slug`/`$dir` appears from nowhere. A `set -u` script dies on an unbound var; a
non-`-u` one silently expands to empty and checks the wrong path — worse, because it passes quietly.

**Why:** Recurs across reviews. The v5.2 own-patterns review caught an undefined var in
define/office-hours; the v5.3 review caught the identical class in PLAN's Step 11a trio gate —
`$slug` was never assigned, so the completeness check ran against the empty path and would have
passed a missing trio. Same mistake, second cycle running. Fix pattern: derive from an env var
or a deterministic source and BLOCK if it's empty —
`slug_dir="${LINTEL_PLAN_DIR:-$(ls -dt .claude/plans/*/ 2>/dev/null | head -1)}"; [ -n "$slug_dir" ] || { echo BLOCKED; exit 1; }`.

**How to apply:**
- Before shipping any skill, scan its bash for variables: every one must be assigned above its
  first use or be a documented input. Treat a bare `$var` with no origin as a bug, not a sketch.
- Prefer `${VAR:-<fallback>}` + an empty-guard over assuming the caller set something.
- When a reviewer flags an unbound var, grep the WHOLE surface for the same pattern — it is never
  a one-off (it wasn't in v5.2, it wasn't in v5.3).

Related: [[L-007]] independent review before SHIP — both reviews earned their keep by catching
exactly this; the lesson is to stop manufacturing the finding for them.

## L-015 — Two agent sessions on one repo: isolate in a worktree, reconcile by merge, never force

**Rule:** When a second agent session is concurrently editing the same repo (mtimes moving under
you, files you didn't write appearing), do NOT race it on a shared index. Isolate your work in a
git worktree pinned to a shared base commit, build there, and reconcile with a **merge** — never a
force-push over the other session's branch. If neither session rewrites the other's commits, the
convergence is clean: git auto-merges non-overlapping changes, and files both sides touched combine
correctly *because both built on the same base*.

**Why:** The v5.3 launch-readiness cycle ran alongside a second session on `feat/v5.3-cli-and-craft`.
Detected twice via fresh mtimes; the first instinct (drive the shared tree) would have produced
interleaved half-commits and lost work. Instead: a worktree (`launch-waves`) pinned to the other
session's tip, all 7 waves built + committed there, then `git merge origin/feat/v5.3` — **zero
conflicts**. The other session had independently merged my waves 1–2 and run its own L-007 review;
its refined fail-closed hook positioning and my `CMD_FLAT` flattening combined into a strictly better
hook because both descended from the shared `e1fec0e`. The push was a fast-forward; PR #73 absorbed
everything. Two independent reviews (theirs + mine) made the result stronger than either alone.

**How to apply:**
- First sign of a concurrent writer (unexplained mtimes, `git status` files you didn't create):
  `EnterWorktree` (or `git worktree add`) off the current shared tip; work there.
- Commit wave-atomically so a later merge has clean seams; keep each file's changes in one logical
  commit (the merge of `CODEOWNERS`/`plan` auto-resolved precisely because edits were localized).
- Reconcile with `git merge origin/<branch>` and verify `git merge-base --is-ancestor` before any
  push (fast-forward only — a force-push is how you delete the other session's review fixes).
- Re-run the FULL suite on the *merged* tree (L-010): the merge adds tests/behaviour neither branch
  tested alone (here, their `auto-decide.sh` → 81→82).
- A guard you extend can catch your own prose: my `no-swedish` scope-widening flagged the literal
  `å` in my own explanatory comment. Write guard rationale without trigger examples.

Related: [[L-010]] green-on-committed-tree — the gate is the merged tree, not either parent;
[[L-007]] independent review — two parallel sessions yield two independent reviews, a feature not a
bug if you merge rather than overwrite.

## L-016 — A harness convention the model must remember is no convention: enforce continuity with hooks, not prose

**Rule:** When a harness needs something to happen reliably across a long session (render the
position footer, append state, continue to the next phase), it cannot live only as SKILL.md prose
the model chooses to execute. Across long BUILDs, subagent returns, and context compaction, that
adherence decays and the turn ends silently. Put the load-bearing guarantee in the deterministic
substrate — a hook — and keep the prose thin.

**Why:** The operator reported a recurring "did a lot of work, then total silence, no footer, as if
the session forgot it was mid-cycle" across many sessions. A 7-agent diagnosis + adversarial verify
found: the footer renderer works fine (a live BUILD/STARTING cycle was frozen on disk) — but
*nothing invoked it*. Only SessionStart/Pre/PostToolUse hooks existed; no Stop hook, no PreCompact
hook. ADR-0003 even cited "invisible discipline is indistinguishable from no discipline," then
shipped a footer whose content was visible but whose invocation was invisible. The fix (ADR-0022):
a warn-only Stop hook surfaces the footer at turn end; the digest re-injects cycle position; the
renderer handles a just-started cycle. Stricter prose was explicitly rejected — it is what already
failed.

**How to apply:**
- Claude Code reality (verify, don't assume): there is NO PreCompact hook (compaction is
  non-hookable); a Stop hook can warn (stdout, exit 0) or block (exit 2) but CANNOT inject context
  to resume. Project-root CLAUDE.md + auto-memory ARE re-injected after compaction — so durable
  recovery state goes there + in `.claude/memory/`, and a SessionStart digest re-injects it.
- A Stop hook that enforces continuity must be warn-only (stdout + exit 0), never a block decision
  (forcing continuation can infinite-loop), and silent when there is nothing to surface.
- Honest scope: hooks are Claude-Code-only. Other CLIs keep the prose convention as fallback — so
  the prose can't be deleted, only demoted to the non-enforced path.

Related: [[L-008]] dogfood-the-footer (the convention shipped but wasn't followed — because nothing
enforced it); [[L-012]] the negative test matters (the Stop hook's "silent when not in a cycle" path
is the one that keeps it from being a per-turn nuisance).

## L-017 — The inline secret/PII override must be the LEADING token of the command, not after `cd … &&`

**Rule:** The block hooks honor the inline override only as a *leading* env-assignment prefix of the
command string (the L-012 anti-forgery property). So a command that starts with `cd /repo && ` and
only THEN has the override does NOT override — the leading token is `cd`. Put the override first and
use the directory flag (`-C <repo>`) instead of a `cd` prefix.

**Why:** During the setup-hardening ship, the customer-data hook fired on a verified false positive
(the loose phone regex matched a generated audit filename's numeric timestamp suffix). The override
kept being ignored until I read the hook: its override regex is anchored to the start of the command
(`^[[:space:]]*(VAR=val )*LINTEL_OVERRIDE_…=1`), so a `cd … &&` prefix breaks the anchor. With the
override leading and the directory flag, it worked. Two follow-ups surfaced: the phone regex
over-matches numeric date/timestamp strings (false-positives on audit/compat filenames), and the
block hook's git-command matcher fires when ordinary text merely CONTAINS the words "git push/commit"
— so a lesson documenting the override can itself trip the hook (write such text via the Edit tool,
not a Bash heredoc).

**How to apply:** Override pushes/commits with the env-assignment as the absolute first token, no
`cd` prefix. Always verify the match is genuinely benign first (grep the diff for the regex) and
record the specific benign string in the reason — never override blind.

Related: [[L-012]] the override is honored only as a leading prefix precisely so attacker-influenced
text can't forge it — the same property that makes a `cd &&` prefix fail.
## L-018 — Running /li:cycle means running its machinery, not just its work

**Rule:** When you invoke `/li:cycle` (or any cycle), instantiate it in the state ledger at the
START — `state_append CYCLE STARTING cycle_id=… cycle_mode=…` — and render `render_cycle_footer`
at every phase/wave boundary and gate, with explicit `[N/M] PHASE → next` hand-offs. Doing the
cycle's *work* (explore, decide, build) without its *machinery* (ledger segment + footer +
hand-offs) leaves the operator blind to position and breaks `/li:resume`.

**Why:** During the S4L build I drove SENSE→…→BUILD directly and never wrote a `CYCLE STARTING`
marker. The ledger still showed the previous cycle `cycle_complete:true`, so `render_cycle_footer`
found no active segment and fell to the thin "no active cycle" line — the operator asked why there
was no footer / no clear hand-off. The footer was not broken; I never started the cycle in the
ledger. Reinforced by the ledger-segment scoping fix — the footer needs a CYCLE STARTING marker to
define the segment.

**How to apply:**
- First action of any cycle: `source lib/state.sh && state_append CYCLE STARTING cycle_id=<id> cycle_mode=<mode> branch=… commit=…`.
- Append a per-phase ledger entry at each boundary; render the footer at gates + completion.
- For long multi-wave BUILDs, treat each wave as a hand-off boundary: render the footer + name the next wave.
- "Did the work" ≠ "ran the cycle." The ceremony is the operator's visibility + the resume contract.

Related: [[L-013]] (do the real work, not the work-shaped gesture) — here the inverse: I did the
substance but skipped the visible contract; and [[L-016]] (enforce continuity with hooks, not prose)
— the deeper, hook-based fix for the same silent-mid-cycle failure.

## L-019 — Consume the source's KNOW-HOW; produce the user's VALUE — never port its mechanism

**Rule:** When converting an external system (a course, a Notion/spreadsheet "system", a prompt
pack) into a Lintel pack, take the *expertise* (frameworks, copy logic, psychology, the prompts'
reasoning) and deliver it as skills that GENERATE the actual deliverables the user wants. Do NOT
replicate the source's internal plumbing — its bookkeeping objects, setup tabs, "command center",
copy-paste hand-off blocks — as if those were features. Those are how a humans-in-a-spreadsheet
system carried state; an agentic skill pack carries state natively (session + real artifacts in the
user's project + the ledger/memory).

**Why:** Building the S4L pack I designed the cycle around faithfully reproducing the source's "28
Vault Objects", the Command Center, and AI-Stack-Setup tabs. The operator stopped it: "vi skiter i
vault objects och command center … målet är innehållet som genereras … värdet som användaren får
ut." The vault-object paste-chain was the source's mechanism for manual state transfer; porting it
would have produced object-shaped ceremony instead of sales pages, VSLs, emails, and offers. The
goal is the generated content (the value), not artifacts that mirror the source's tooling.

**How to apply:**
- Frame every phase/skill by the DELIVERABLE it produces ("a sales page", "a 7-email sequence"),
  not by a source step name or an intermediate object schema.
- State compounds "our way": skills write real artifacts to the user's workspace and read prior
  ones; the cycle tracks progress in the Lintel ledger. No paste-block objects.
- Keep ALL the know-how (every framework/formula/example) in skills + knowhow; drop the form.
- Consolidate many source prompts into fewer capable skills (e.g. 13 ad-story prompts → one
  `/s4l:ads` that can produce any of them), backed by the full reference — subtraction bias.

Related: [[L-013]] (make-it-ours = reinvent the substance) — L-019 is the sharp instance: reinvent
toward the OUTCOME, and explicitly discard the source's mechanism rather than dignifying it as a feature.

## L-020 — A plugin version must bump for EVERY deployable change; never reuse a version a parallel PR already shipped

**Rule:** When a fix must reach installed sessions (a hook, a plugin-loaded skill/agent), its PR MUST
carry a UNIQUE version bump in `.claude-plugin/plugin.json` + `marketplace.json`. If a parallel/earlier
PR already bumped to that version, your change needs a FURTHER bump (5.7.0 → 5.7.1), not the same one.
Plugin/marketplace updates are version-gated: reusing an already-shipped version means the installed
plugin never re-pulls your change — the code is on main, but the operator still can't get it.

**Why:** The cycle-continuity hook (ADR-0023, PR #80) bumped 5.6.0→5.7.0 — but PR #79 had ALREADY
shipped 5.7.0 (extension-pack delivery) before #80 landed. When the operator ran `/plugin marketplace
update`, the cache held a 5.7.0 that predated #80 → no `cycle-position-inject` hook. main had the hook
at 5.7.0, but the version string couldn't distinguish #79's 5.7.0 from #80's, so no re-pull fired.
li-doctor's new staleness check (presence of the capability in the installed cache, not the version
string) caught it. This is the ADR-0022/L-016 deployment trap recurring — "the fix is worthless
uninstalled," and a same-version overwrite is a silent way to stay uninstalled. Fixed with 5.7.1.

**How to apply:**
- Every PR touching plugin-loaded surface (hooks.json, hooks/, skills/, agents/) ends with a UNIQUE
  version bump. Before merge, confirm the version isn't already taken by a recently-merged/parallel PR
  (check `marketplace.json` on main / the merged PR list); if taken, bump PAST it.
- Trust a capability-presence check (does the installed cache contain the new hook/skill?) over the
  version string — li-doctor's staleness probe is the backstop.

Related: [[L-016]] enforce continuity with hooks — but a hook only fires once deployed; ADR-0022 /
ADR-0023 both make deployment part of the fix.

## L-021 — `git commit` after `git rm --cached` sweeps the staged deletions; partial-pathspec commits re-add on-disk files

**Why:** During launch-readiness I ran `git rm -r --cached .claude/engineering/audits …` (staged 31 deletions), then
later `git add <test>` + `git commit` — the commit swept in the 31 staged deletions, producing a
non-atomic "test" commit. I split it with `git reset --soft HEAD~1`, then committed the move with
`git commit -- <paths>` — but a partial-pathspec commit RE-READS the working tree for those paths,
and since `git rm --cached` left the files on disk, git saw them as PRESENT and committed them as
present (the staged deletion was lost). Net: the "public-tree move" commit changed only `.gitignore`;
the docs stayed tracked. The adversarial review (not my own check) caught it.

**How to apply:**
- `git commit` (no pathspec) commits the ENTIRE index — never assume a preceding `git add X` scopes it.
- After staging deletions, verify with `git show --stat HEAD` (or `git status` before commit) that the
  commit's contents match intent.
- To untrack-but-keep-on-disk: `git rm --cached <files>` then a PLAIN `git commit` with a clean index
  — do NOT use `git commit -- <pathspec>` (it re-reads the working tree and un-stages the deletion).

Related: [[L-010]] verify on the committed tree, not the working tree.

## L-022 — Never run two full test suites concurrently; they share `.claude/runtime/state/00-state.md`

**Why:** I launched several `tests/runner/run-all.sh` runs in parallel to "save time." The
cycle-footer + cycle-continuity tests `cp` fixtures into the live `.claude/runtime/state/00-state.md`
and restore it — concurrent runs clobbered each other's live-state manipulation, producing a spurious
`cycle-footer: FAILURES` in one run while a solo run of the same test was `ALL PASS`. Hours lost
chasing a "regression" that was a test-harness race. Compounded by Windows Git Bash being ~30x slower
under host memory pressure (≈6 GB free), so the aggregate suite timed out even though every test
passed individually.

**How to apply:**
- Run the suite SOLO. One `run-all.sh` at a time. If you need a fast signal, run `--scope unit` or a
  single test file, not a second full suite.
- When the aggregate is slow/times out under load, verify correctness per-test (each file passes
  individually) rather than trusting/distrusting the timed-out aggregate.
- Tests that touch shared live state (`00-state.md`, audit files) are not concurrency-safe.

## L-023 — Untracking a docs dir needs a live-dependency + `# intent:`-header check first

**Why:** The plan was to move internal docs (`.claude/engineering/audits/`) out of the public tree. The adversarial
review found `.claude/engineering/audits/uniformity-matrix.md` is a LIVE dependency (`bin/li-uniformity` writes it;
`skills/uniformity` + `tests/shape/uniformity-coverage.sh` read it) and two audit records are cited by
`# intent:` structured-comment headers in `lib/state.sh` + `lib/auto-decide.sh`. Untracking the dir
would 404 the dashboard on a fresh clone and break intent-resolution — invisible to a check that only
greps for markdown links. Reverted; kept docs tracked; cleaned residue in place instead.

**How to apply:**
- Before untracking/moving any file, grep the whole repo (code + `# intent:`/`# constraints:` headers +
  tests) for references, not just doc links. A generated/consumed artifact in a "docs" dir is still a
  runtime dependency.
- A content-filter aside from the same cycle: generating the full Contributor-Covenant CoC text trips
  output content-filtering (it enumerates harassment/abuse terms) — adopt the Covenant by reference.

Related: [[L-019]] produce value, not the source's mechanism.
