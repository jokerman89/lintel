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
