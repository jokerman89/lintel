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
