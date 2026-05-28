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
