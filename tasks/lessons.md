# Lessons learned — Lintel

Durable rules accumulated from corrections. Review at session start; add after any correction.

> Format per entry: short rule first, then `Why:` (the incident or principle), then `How to apply:` (when this kicks in). Link related lessons with `[[name]]`.

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
