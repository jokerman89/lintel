# Lintel uniformity audit — Cohort 2: planner sub-chain

**Cohort:** 2 (planner sub-chain)
**Auditor pass:** uniformity, 14 dimensions, NO-CUT (uplift only)
**Date:** 2026-05-29
**Scale context:** 144 skills, 83 agents, 19 hooks, 1 pack. Mid v4.0 reframe.

## Components covered (7)

| Component | Path | Role in chain |
|---|---|---|
| office-hours | `skills/office-hours/SKILL.md` | design-doc generator (chain step 1) |
| plan-ceo-review | `skills/plan-ceo-review/SKILL.md` | strategy/scope (step 2) |
| plan-eng-review | `skills/plan-eng-review/SKILL.md` | arch + tests (step 3, REQUIRED gate) |
| plan-design-review | `skills/plan-design-review/SKILL.md` | UI/UX (step 4, conditional) |
| plan-devex-review | `skills/plan-devex-review/SKILL.md` | DX (step 5, opt-in) |
| plan-tune | `skills/plan-tune/SKILL.md` | per-question preference tuning (cross-cutting) |
| autoplan | `skills/autoplan/SKILL.md` | orchestrator of the chain |

**Not present in repo (named in cohort spec but absent / belong to other cohorts):**
- `plan` and `plan-and-build` exist but are Cohort 1 phase-core skills — excluded here.
- No other `plan-*` skills found beyond the seven above. The gstack marketplace `/plan-design-review`, `/plan-eng-review` etc. are *namesakes* — the Lintel versions audited here are the in-repo copies under `skills/`, not the gstack plugin skills.

---

## Architecture-level note (designed-not-built dimensions)

Per the v4.0 reframe these dimensions are **designed-not-built** across the whole repo. To avoid per-component spam they are recorded once here and marked `n/a-unbuilt` in each record:

- **D7 (pack / WorkProfile runtime influence):** pack-influence at runtime is DESIGNED-NOT-BUILT. No Cohort-2 skill declares a `pack` or `work_profile` frontmatter key or resolves one at runtime. Arch-level uplift: when D7 lands, every planner skill should declare which WorkProfile dimensions (e.g. rigor, scope-appetite) modulate its question set — e.g. plan-ceo-review's scope-expansion vs scope-reduction default should be pack-driven, not hardcoded.
- **D9 (Brief Forge):** DESIGNED-NOT-BUILT. The chain hand-offs (office-hours → ceo → eng → design/devex, and autoplan's aggregation step) are exactly the hand-off boundaries Brief Forge is meant to own. Today hand-off is "freshest design doc in projects dir" — implicit and fragile. Arch-level uplift: when Brief Forge lands, autoplan step transitions and each review's design-doc ingestion are the first call sites. This is the single highest-value future integration point in the cohort.
- **Envelope / wiki:** DESIGNED-NOT-BUILT; no records reference them.

These three are NOT re-litigated per component below.

---

## Finding records

### office-hours

```yaml
component: skills/office-hours/SKILL.md
kind: skill
cohort: 2
dimensions:
  D1_head:
    state: present
    nano: "SKILL.md:30-37 (Inputs + Workflow step 1)"
    macro: "first step of /autoplan chain; greenfield design"
    high: "explicit-entry promise — inputs declared + validated"
    finding: "uniform with cohort; strongest head in cohort (declares required + 3 optional flags w/ semantics)"
    proposed: "keep as bar; have peers match this Inputs depth"
    why: "office-hours sets the input-contract bar — achieve uniform input declaration by lifting peers to it"
  D2_tail:
    state: present
    nano: "SKILL.md:55-56 (Set status DRAFT; report path + next step)"
    macro: "hand-off to plan-ceo-review/eng-review"
    high: "explicit-exit promise (Status field + next-step report)"
    finding: "uniform; emits Status: DRAFT/APPROVED + explicit next-step"
    proposed: "add an explicit DONE/BLOCKED/STUCK status token to the report line to match phase-core status protocol"
    why: "phase-core skills (plan) use DONE/BLOCKED; aligning the tail token gives the chain one resume vocabulary"
  D3_objects:
    state: present
    nano: "SKILL.md:58-106 (Output structure block, full frontmatter + sections)"
    macro: "design doc is the shared object the whole chain reads"
    high: "shared-schema discipline — one schema, both sides import"
    finding: "strongest in-cohort: fully specifies output doc frontmatter + section order incl. the LAST-h2 GSTACK REVIEW REPORT contract"
    proposed: "extract the design-doc frontmatter into a shared schema doc the review skills cite, rather than each re-describing it"
    why: "two+ components communicate via this doc; per shared-schema rule the schema should live once and be imported, not redescribed in 5 skills"
  D4_entrypoints:
    state: present
    nano: "SKILL.md:22 (autoplan chain), 130-148 (direct invocation examples)"
    macro: "direct slash-command + autoplan step 1"
    finding: "uniform; both entry-points (direct, via autoplan) covered"
    proposed: "none"
    why: "n/a"
  D5_checkpoints:
    state: partial
    nano: "SKILL.md:54 (atomic write of doc) — no intermediate checkpoint"
    macro: "resume after interrupted intake interview"
    high: "checkpoint/resume promise"
    finding: "below bar: writes only the final doc; a 4-round intake interrupted mid-way has no checkpoint to resume from"
    proposed: "write intake answers to a scratch checkpoint (e.g. projects/<slug>/.intake-<ts>.json) after each AskUserQuestion so an interrupted interview resumes"
    why: "achieve resumable-intake; gstack context-save shows the scratch-state pattern — steal it for intake state"
  D6_recovery:
    state: present
    nano: "SKILL.md:118-124 (Failure modes — STUCK path, doc-exists path)"
    macro: "interrupted design generation"
    finding: "strongest recovery prose in cohort (5 named failure modes + operator-choice on doc-exists)"
    proposed: "keep as bar"
    why: "this is the recovery bar; lift peers to this enumerated-failure-mode depth"
  D7_pack:
    state: n/a-unbuilt
    nano: "frontmatter: no pack/work_profile key"
    finding: "see arch-level note (D7 designed-not-built)"
    proposed: "per arch note: --mode full|minimal should become pack-driven when D7 lands"
    why: "see arch note"
  D8_frontmatter:
    state: partial
    nano: "SKILL.md:1-9 (frontmatter)"
    macro: "frontmatter completeness floor for skills"
    high: "frontmatter-completeness promise"
    finding: "has name/layer/description/color/tools/voice/cli_support; MISSING necessity, brief_forge_handoffs, expected_inputs/outputs, navigation. NOTE office-hours is the ONLY cohort member with cli_support:[claude-code,codex] AND voice declared — already above peers on cli_support breadth"
    proposed: "add necessity (STRONGLY-RECOMMENDED), expected_inputs/outputs, gap_if_skipped; reserve brief_forge_handoffs for D9 landing"
    why: "achieve uniform frontmatter floor; expected_inputs/outputs are load-bearing because this doc IS the chain's shared object"
  D9_brief_forge:
    state: n/a-unbuilt
    nano: "no hand-off declaration"
    finding: "see arch note — office-hours→ceo-review hand-off is a prime Brief Forge call site"
    proposed: "per arch note"
    why: "see arch note"
  D10_lessons:
    state: absent
    nano: "not declared anywhere in body"
    macro: "design quality should improve across sessions"
    high: "cross-session-memory promise (lessons.md / knowhow tag-funnel)"
    finding: "below bar: a design-doc generator never consults lessons.md or knowhow despite being the ideal consumer (past design decisions, recurring premises)"
    proposed: "step 2 (Read context) should also read repo lessons.md + knowhow tags matching --scope, and surface relevant prior decisions in Premises"
    why: "the operator-relation thread (lessons accumulate AND are consulted) is dead here; office-hours is where consultation would compound most"
  D11_subagent:
    state: absent
    nano: "tools list has no Task; intake runs inline"
    macro: "main-context cleanliness during multi-round intake + section generation"
    finding: "below bar: full section generation (7 sections) runs inline in main context"
    proposed: "spawn a curated-brief subagent for section drafting (Architect-style), returning the doc body; keep intake in main context"
    why: "dedicated-vs-inline rule — 7-section generation is bulk work that should not fill main context; gstack does heavy generation in subagents"
  D12_failure:
    state: present
    nano: "SKILL.md:118-124"
    finding: "uniform/strong — STUCK + sanitize-and-retry are explicit"
    proposed: "none beyond D6 status-token alignment"
    why: "n/a"
  D13_observability:
    state: absent
    nano: "no review-log / usage-log / envelope write (unlike the 4 review skills which call gstack-review-log)"
    macro: "operator visibility into chain runs"
    high: "observability/jobs-visibility promise"
    finding: "below bar: office-hours writes NO telemetry, while every review peer persists a gstack-review-log line. The chain's first step is invisible to the run aggregator"
    proposed: "emit a review-log (or future envelope-log) line: {skill:office-hours, status, doc_path, sections_generated, mode, commit}"
    why: "autoplan step 8 'read all review-log entries from this run' silently misses step 1 today — observability must be uniform across all chain members"
  D14_necessity:
    state: absent
    nano: "frontmatter: no necessity field"
    finding: "below bar: no REQUIRED/RECOMMENDED/OPTIONAL declaration nor gap_if_skipped"
    proposed: "necessity: STRONGLY-RECOMMENDED; gap_if_skipped: 'review skills run against ad-hoc prose with no premise/decision structure'"
    why: "necessity is undeclared cohort-wide; office-hours is the load-bearing case (it produces the object peers consume)"
peer_comparison:
  strongest_peer_in_cohort: office-hours (D3 objects, D6 recovery) and plan-eng-review (D5/D12/observability gate)
  this_component_depth: above-bar on D1/D3/D6/D12; below-bar on D5/D10/D11/D13
  uplift_needed: add observability log, lessons consultation, subagent for generation, intake checkpoint
operator_decision_required: yes
priority: high
```

### plan-ceo-review

```yaml
component: skills/plan-ceo-review/SKILL.md
kind: skill
cohort: 2
dimensions:
  D1_head:
    state: present
    nano: "SKILL.md:32-35 (Inputs — auto-discovers latest design doc)"
    macro: "chain step 2"
    finding: "present but input path points at ~/.gstack/projects/ (line 33) — see D3 path-fragmentation finding"
    proposed: "normalize input discovery path to ~/.lintel/projects/"
    why: "office-hours WRITES to ~/.lintel/projects/ (office-hours:13) but ceo-review READS ~/.gstack/projects/ — the chain hand-off is broken at the directory level"
  D2_tail:
    state: present
    nano: "SKILL.md:48-71 (Report format incl. VERDICT SCOPE LOCKED/REVISE)"
    finding: "uniform; explicit VERDICT token"
    proposed: "align VERDICT vocabulary across all 4 reviews (LOCKED vs CLEARED vs scores) — see cohort summary"
    why: "autoplan aggregates verdicts; one verdict vocabulary makes aggregation lossless"
  D3_objects:
    state: partial
    nano: "SKILL.md:33,38 (~/.gstack/projects/<slug>)"
    macro: "reads office-hours design doc, appends CEO Review section"
    high: "shared-schema discipline + chain integrity"
    finding: "PATH FRAGMENTATION: reads ~/.gstack/projects/ while producer writes ~/.lintel/projects/. Output object (CEO Review section) location vs office-hours' LAST-h2 contract not reconciled"
    proposed: "single source the projects-dir constant; cite office-hours' shared design-doc schema"
    why: "highest-severity correctness issue in cohort — a literal broken hand-off path"
  D4_entrypoints:
    state: present
    nano: "SKILL.md:96-109 (examples), autoplan step 4"
    finding: "uniform"
    proposed: "none"
    why: "n/a"
  D5_checkpoints:
    state: absent
    nano: "no checkpoint write"
    macro: "interrupted 3-question + premise loop"
    finding: "below bar: a multi-question review interrupted mid-way restarts from zero"
    proposed: "persist answered-questions to review-log incrementally (it already calls gstack-review-log at end — make it per-question or write a resume marker)"
    why: "achieve resumable review; plan-eng-review's Exit-Plan-Mode gate is the only checkpoint discipline in cohort — generalize it"
  D6_recovery:
    state: present
    nano: "SKILL.md:86-90 (Failure modes)"
    finding: "present but thinner than office-hours (3 modes vs 5)"
    proposed: "add: design-doc path-not-found-but-stale, premise-loop-nontermination guard"
    why: "lift to office-hours recovery depth"
  D7_pack: { state: n/a-unbuilt, nano: "frontmatter", finding: "see arch note — scope-expansion vs reduction default is the prime pack-driven knob", proposed: "per arch note", why: "see arch note" }
  D8_frontmatter:
    state: partial
    nano: "SKILL.md:1-9"
    finding: "below bar: missing necessity, expected_inputs/outputs, gap_if_skipped (same gap as all peers)"
    proposed: "add necessity: RECOMMENDED + expected_inputs(design-doc path)/outputs(CEO Review section + review-log line)"
    why: "uniform frontmatter floor"
  D9_brief_forge: { state: n/a-unbuilt, nano: "n/a", finding: "see arch note", proposed: "per arch note", why: "see arch note" }
  D10_lessons:
    state: absent
    nano: "not consulted"
    macro: "founder-signal synthesis should learn operator's conviction patterns over time"
    finding: "below bar: step 5 'Founder signal synthesis' is the IDEAL lessons consumer (operator taste/agency patterns) but consults nothing"
    proposed: "read prior CEO-review founder-signal entries; surface 'last 3 times you said X about wedge' "
    why: "operator-relation thread should compound here more than anywhere — synthesis without memory is one-shot"
  D11_subagent:
    state: absent
    nano: "tools: Read,Bash,Grep,Glob (no Task)"
    finding: "below bar but lower priority — review is interactive Q&A, lighter than office-hours generation"
    proposed: "optional: spawn subagent only for the premise-extraction step (read design doc, return 3-5 premises)"
    why: "premise extraction is the one bulk-read step; rest is interactive and correctly inline"
  D12_failure:
    state: present
    nano: "SKILL.md:86-90"
    finding: "uniform"
    proposed: "none"
    why: "n/a"
  D13_observability:
    state: present
    nano: "SKILL.md:73-76 (gstack-review-log call)"
    macro: "run aggregation by autoplan"
    high: "observability promise"
    finding: "present BUT calls ~/.claude/skills/gstack/bin/gstack-review-log — a gstack-plugin binary path, not a Lintel-owned one. Brand + dependency fragmentation"
    proposed: "route through a Lintel-owned review-log binary (li-review-log) or document the gstack dependency explicitly"
    why: "Lintel claims first-party-first; depending on a gstack bin at a ~/.claude path couples the chain to an external plugin install"
  D14_necessity:
    state: partial
    nano: "SKILL.md:13 ('Optional but recommended')"
    finding: "stated in prose, not in frontmatter; no gap_if_skipped field"
    proposed: "necessity: RECOMMENDED + gap_if_skipped: 'scope/wedge assumptions reach eng review unchallenged'"
    why: "prose necessity exists — promote it to a declared field for uniform parsing"
peer_comparison:
  strongest_peer_in_cohort: office-hours / plan-eng-review
  this_component_depth: at-bar on D2/D4/D12/D13; below-bar on D3(path bug)/D5/D10
  uplift_needed: fix projects-dir path, add lessons-backed founder-signal memory, declare necessity
operator_decision_required: yes
priority: high
```

### plan-eng-review

```yaml
component: skills/plan-eng-review/SKILL.md
kind: skill
cohort: 2
dimensions:
  D1_head:
    state: present
    nano: "SKILL.md:32-35 (Inputs), 38 (Step 0 BLOCKING)"
    finding: "strongest head in cohort: declares a BLOCKING Step 0 gate before any work — explicit, validated entry"
    proposed: "keep as bar"
    why: "this is the head/gate bar; lift peers toward an explicit blocking-precondition pattern where applicable"
  D2_tail:
    state: present
    nano: "SKILL.md:111-119 (Exit Plan Mode Gate, BLOCKING)"
    finding: "strongest tail in cohort: explicit BLOCKING exit gate with 3 verifiable conditions + named contract-violation consequence"
    proposed: "keep as bar; generalize the 'last-h2 must be REPORT + log written + log read' exit-contract pattern to ceo/design/devex reviews"
    why: "this is the exit bar — uniform tail means every review verifies its own report landed before exit"
  D3_objects:
    state: present
    nano: "SKILL.md:78-105 (Report format + Required outputs incl. JSONL artifact)"
    finding: "richest output contract (table + VERDICT + JSONL via jq for autoplan aggregation)"
    proposed: "keep; the JSONL-for-autoplan pattern should be adopted by ceo/design/devex so autoplan aggregates uniformly"
    why: "only eng-review emits machine-readable task JSONL; uniform aggregation needs all reviews to"
  D4_entrypoints:
    state: present
    nano: "SKILL.md:153-157, autoplan step 5, release-ev2 dependency"
    finding: "uniform — direct, autoplan, AND consumed by release-ev2 gate"
    proposed: "none"
    why: "n/a"
  D5_checkpoints:
    state: partial
    nano: "SKILL.md:111-119 (exit gate is a checkpoint of sorts; no mid-review checkpoint)"
    finding: "below own-bar: long 4-section + Step-0 review has no mid-flight checkpoint"
    proposed: "write a planner-checkpoint after Step 0 resolves and after each section, so an interrupted review resumes at the section boundary"
    why: "eng-review is the longest review; interruption cost is highest — section-boundary checkpoints match its granularity discipline"
  D6_recovery:
    state: present
    nano: "SKILL.md:126-130 (Failure modes incl. jq-missing degrade)"
    finding: "uniform/strong — degrades gracefully (jq missing → markdown still primary)"
    proposed: "none"
    why: "n/a"
  D7_pack: { state: n/a-unbuilt, nano: "frontmatter", finding: "see arch note — granularity target (2-5min, LOCKED) + completeness 'lake not puddle' are candidate pack-modulated knobs", proposed: "per arch note", why: "see arch note" }
  D8_frontmatter:
    state: partial
    nano: "SKILL.md:1-9"
    finding: "below bar: missing necessity (despite being THE required gate), expected_inputs/outputs, gap_if_skipped"
    proposed: "necessity: REQUIRED (it IS the required gate per line 13) + gap_if_skipped: 'release-ev2 dashboard verdict cannot be issued'"
    why: "the most load-bearing necessity declaration in the entire cohort is undeclared in frontmatter"
  D9_brief_forge: { state: n/a-unbuilt, nano: "n/a", finding: "see arch note", proposed: "per arch note", why: "see arch note" }
  D10_lessons:
    state: absent
    nano: "not consulted"
    macro: "recurring arch/test gaps should be remembered"
    finding: "below bar: a regression-rule + reuse-map review never consults lessons.md for prior recurring failure modes"
    proposed: "Step 0 'What already exists' should also read lessons.md + knowhow for known-bad patterns in this repo"
    why: "the repo-relation thread (knowhow grows AND is consulted) belongs in the review that owns code quality"
  D11_subagent:
    state: present
    nano: "SKILL.md:74-76 (Outside voice — codex OR Claude subagent for independent challenge)"
    finding: "strongest delegation in cohort: explicitly spawns an outside-voice subagent (informational, not auto-applied)"
    proposed: "keep as bar; the curated-brief discipline (give the subagent the plan, not raw context) should be made explicit"
    why: "this is the delegation bar; only note is to specify the subagent gets a curated brief per Architect rule"
  D12_failure:
    state: present
    nano: "SKILL.md:126-130, REGRESSION RULE 72"
    finding: "uniform/strong"
    proposed: "none"
    why: "n/a"
  D13_observability:
    state: present
    nano: "SKILL.md:91-94 (gstack-review-log), 118 (log read verified at exit)"
    finding: "strongest observability: WRITES log AND verifies it was READ at exit gate (closed loop)"
    proposed: "keep as bar; same gstack-bin-path dependency caveat as ceo-review (D13)"
    why: "closed-loop write+read verification is the observability bar — but route through Lintel-owned bin"
  D14_necessity:
    state: partial
    nano: "SKILL.md:13 ('The required review')"
    finding: "stated REQUIRED in prose; not a frontmatter field"
    proposed: "promote to necessity: REQUIRED field"
    why: "prose↔frontmatter mismatch; the one skill where REQUIRED is unambiguous"
peer_comparison:
  strongest_peer_in_cohort: plan-eng-review (sets the bar on D1/D2/D3/D11/D13)
  this_component_depth: above-bar on most dims; below-bar only on D5 checkpoints, D10 lessons
  uplift_needed: section-boundary checkpoints, lessons consultation in Step 0, promote REQUIRED to frontmatter
operator_decision_required: no
priority: medium
```

### plan-design-review

```yaml
component: skills/plan-design-review/SKILL.md
kind: skill
cohort: 2
dimensions:
  D1_head:
    state: present
    nano: "SKILL.md:30-31 (Inputs), workflow conditional on UI scope"
    finding: "present; correctly self-gates (no UI scope → skip)"
    proposed: "make the UI-scope detection explicit as a Step 0 (eng-review has explicit Step 0; design-review detects implicitly)"
    why: "lift to eng-review's explicit-gate bar"
  D2_tail:
    state: present
    nano: "SKILL.md:50-65 (Report format, score table)"
    finding: "present; verdict is a SCORE delta not a CLEARED token — verdict-vocabulary fragmentation"
    proposed: "add a CLEARED/NOT-CLEARED verdict line alongside the score so autoplan aggregates uniformly"
    why: "autoplan final-verdict logic (line 43: 'any review NOT CLEARED') needs a token, not just a score"
  D3_objects:
    state: present
    nano: "SKILL.md:31,69 (~/.gstack/projects/), report appended to plan"
    finding: "same PATH FRAGMENTATION as ceo-review (reads ~/.gstack/projects/)"
    proposed: "normalize to ~/.lintel/projects/"
    why: "broken hand-off path — see ceo-review D3"
  D4_entrypoints:
    state: present
    nano: "SKILL.md:112-117, autoplan step 6 (UI-scope-conditional)"
    finding: "uniform"
    proposed: "none"
    why: "n/a"
  D5_checkpoints:
    state: absent
    nano: "no checkpoint"
    finding: "below bar: 6-pillar scoring loop has no resume point"
    proposed: "incremental review-log write per pillar"
    why: "match eng-review section-boundary checkpoint pattern"
  D6_recovery:
    state: present
    nano: "SKILL.md:87-91 (Failure modes — no-doc, no-UI-scope, skipped-question)"
    finding: "uniform (3 modes)"
    proposed: "lift toward office-hours' 5-mode depth"
    why: "recovery uniformity"
  D7_pack: { state: n/a-unbuilt, nano: "frontmatter", finding: "see arch note", proposed: "per arch note", why: "see arch note" }
  D8_frontmatter:
    state: partial
    nano: "SKILL.md:1-9 — NOTE cli_support:[claude-code] ONLY (no codex), unlike eng/ceo/devex/office-hours"
    finding: "below bar twice: (a) cli_support narrower than peers — codex omitted with no stated reason; (b) missing necessity/expected_io/gap_if_skipped"
    proposed: "either declare codex support or document why design review is claude-only; add necessity: CONDITIONAL (UI scope)"
    why: "cli_support breadth is a Lintel C1 promise; an unexplained narrowing is a uniformity gap"
  D9_brief_forge: { state: n/a-unbuilt, nano: "n/a", finding: "see arch note", proposed: "per arch note", why: "see arch note" }
  D10_lessons:
    state: absent
    nano: "not consulted"
    finding: "below bar: design-pillar scoring never consults prior design-review scores or DESIGN.md-style knowhow"
    proposed: "read prior design-review log entries + repo design knowhow before scoring"
    why: "repeated AI-slop / accessibility findings should be remembered, not rediscovered each plan"
  D11_subagent:
    state: partial
    nano: "SKILL.md:72-76 (design binary + outside voices, optional)"
    finding: "near-bar: invokes external design binary + outside voices, but binary is a gstack path (~/.claude/skills/gstack/design/dist/design)"
    proposed: "keep delegation; same first-party-bin concern as review-log"
    why: "delegation present; dependency-path concern only"
  D12_failure:
    state: present
    nano: "SKILL.md:87-91"
    finding: "uniform"
    proposed: "none"
    why: "n/a"
  D13_observability:
    state: present
    nano: "SKILL.md:67-70 (gstack-review-log)"
    finding: "present; same gstack-bin-path caveat"
    proposed: "route through Lintel-owned bin"
    why: "first-party-first"
  D14_necessity:
    state: partial
    nano: "SKILL.md:13 ('Optional — only fires when...')"
    finding: "prose-only necessity; no gap_if_skipped"
    proposed: "necessity: CONDITIONAL + gap_if_skipped: 'UI plan reaches build with unscored hierarchy/a11y/trust'"
    why: "promote to field; the conditional trigger is the load-bearing part"
peer_comparison:
  strongest_peer_in_cohort: plan-eng-review
  this_component_depth: at-bar on D4/D12/D13; below-bar on D3(path)/D5/D8(cli_support)/D10
  uplift_needed: fix projects path, add codex support or rationale, add CLEARED verdict token, lessons consultation
operator_decision_required: yes
priority: high
```

### plan-devex-review

```yaml
component: skills/plan-devex-review/SKILL.md
kind: skill
cohort: 2
dimensions:
  D1_head:
    state: present
    nano: "SKILL.md:28-33 (Inputs incl. --product-type)"
    finding: "present; richest input typing (--product-type drives baseline)"
    proposed: "make no-DX-scope detection an explicit Step 0 (currently implicit, example at 107-113 references a 'Step 0' not in workflow body)"
    why: "the example cites Step 0 but the Workflow has no Step 0 — internal inconsistency to reconcile"
  D2_tail:
    state: present
    nano: "SKILL.md:54-69 (Report format, score + TTHW)"
    finding: "present; score-delta verdict, same no-CLEARED-token gap as design-review"
    proposed: "add CLEARED/NOT-CLEARED token for autoplan aggregation"
    why: "autoplan verdict aggregation needs a token"
  D3_objects:
    state: present
    nano: "SKILL.md:31 (plan/design doc), report table"
    finding: "present; does NOT cite a projects-dir path (lighter input contract than peers) — paradoxically avoids the gstack/lintel path bug"
    proposed: "explicitly state input discovery path (and use ~/.lintel/projects/) for uniformity"
    why: "underspecified input path is its own gap even if it dodges the fragmentation"
  D4_entrypoints:
    state: present
    nano: "SKILL.md:115-119, autoplan step 7 (opt-in --include-devex)"
    finding: "uniform"
    proposed: "none"
    why: "n/a"
  D5_checkpoints:
    state: absent
    nano: "no checkpoint"
    finding: "below bar: 6-dimension measurement loop, some dims run commands (TTHW timing) — interruption loses measured data"
    proposed: "persist measured metrics incrementally to review-log"
    why: "measured data (TTHW timings) is expensive to recompute — checkpoint it"
  D6_recovery:
    state: present
    nano: "SKILL.md:84-88 (Failure modes)"
    finding: "uniform (3 modes)"
    proposed: "lift toward 5-mode office-hours depth"
    why: "recovery uniformity"
  D7_pack: { state: n/a-unbuilt, nano: "frontmatter", finding: "see arch note — TTHW stretch targets per product-type are a pack-candidate", proposed: "per arch note", why: "see arch note" }
  D8_frontmatter:
    state: partial
    nano: "SKILL.md:1-9"
    finding: "below bar: missing necessity/expected_io/gap_if_skipped (cli_support correctly includes codex)"
    proposed: "necessity: OPTIONAL (opt-in) + gap_if_skipped: 'DX regressions ship undetected; TTHW unmeasured'"
    why: "uniform frontmatter floor"
  D9_brief_forge: { state: n/a-unbuilt, nano: "n/a", finding: "see arch note", proposed: "per arch note", why: "see arch note" }
  D10_lessons:
    state: absent
    nano: "not consulted"
    finding: "below bar: two-week-smell-test history is exactly a lessons signal but is asked live each time"
    proposed: "consult prior devex-review logs for TTHW trend + past smell-test failures"
    why: "DX is explicitly a trend metric (line 64 'tracks trends') — trends require remembered prior runs"
  D11_subagent:
    state: absent
    nano: "no Task tool"
    finding: "below bar: measurement (running install.sh, timing TTHW) could be a subagent task"
    proposed: "spawn a subagent to run + time the cold-clone TTHW measurement, return metrics"
    why: "running install scripts in main context is noisy; isolate the measurement"
  D12_failure:
    state: present
    nano: "SKILL.md:84-88"
    finding: "uniform"
    proposed: "none"
    why: "n/a"
  D13_observability:
    state: present
    nano: "SKILL.md:71-74 (gstack-review-log, richest payload incl. tthw/persona/tier)"
    finding: "richest log payload in cohort; same gstack-bin-path caveat"
    proposed: "route through Lintel-owned bin"
    why: "first-party-first"
  D14_necessity:
    state: partial
    nano: "SKILL.md:13 ('Optional review tier')"
    finding: "prose-only"
    proposed: "promote to necessity: OPTIONAL field + gap_if_skipped"
    why: "field uniformity"
peer_comparison:
  strongest_peer_in_cohort: plan-eng-review (gate/log); plan-devex-review itself sets D13 payload-richness bar
  this_component_depth: at-bar on D4/D12; below-bar on D5/D10/D11; internal inconsistency (Step 0 cited but absent)
  uplift_needed: reconcile Step 0, add CLEARED token, lessons-backed trend, measurement subagent
operator_decision_required: yes
priority: medium
```

### plan-tune

```yaml
component: skills/plan-tune/SKILL.md
kind: skill
cohort: 2
dimensions:
  D1_head:
    state: present
    nano: "SKILL.md:29-36 (Inputs — flag-dispatched)"
    finding: "strongest input contract in cohort (5 explicit flags + no-arg behavior)"
    proposed: "keep as bar"
    why: "flag-dispatch input bar"
  D2_tail:
    state: present
    nano: "SKILL.md:46 (confirmation print incl. 'Active immediately')"
    finding: "present; explicit confirmation tail"
    proposed: "none"
    why: "n/a"
  D3_objects:
    state: present
    nano: "SKILL.md:39,146 (~/.lintel/question-preferences.jsonl)"
    finding: "strong: correctly uses ~/.lintel/ (NOT gstack) AND tombstone (append-only audit) discipline. The ONE cohort skill with correct Lintel paths throughout"
    proposed: "hold as the path-correctness exemplar — peers should match this"
    why: "plan-tune proves the ~/.lintel/ convention; ceo/design reviews diverged from it"
  D4_entrypoints:
    state: present
    nano: "SKILL.md:48-59 (inline tune: mechanism), direct invocation"
    finding: "strongest entry-point coverage: direct slash + inline tune: in chat, with profile-poisoning defense"
    proposed: "keep as bar"
    why: "inline-trigger + injection-defense is a pattern peers lack"
  D5_checkpoints:
    state: n/a-for-kind
    nano: "config skill — single atomic write, no long run"
    finding: "n/a — single-write config tool needs no checkpoint"
    proposed: "n/a"
    why: "appropriate to kind"
  D6_recovery:
    state: present
    nano: "SKILL.md:110-115 (corrupted-file → --reset-all recover path)"
    finding: "uniform/strong"
    proposed: "none"
    why: "n/a"
  D7_pack: { state: n/a-unbuilt, nano: "frontmatter", finding: "see arch note — though tuning IS the operator-preference layer pack would build on", proposed: "per arch note", why: "see arch note" }
  D8_frontmatter:
    state: partial
    nano: "SKILL.md:1-9 (cli_support:[claude-code] only)"
    finding: "below bar: missing necessity/expected_io; cli_support claude-only (AskUserQuestion-tuning may be claude-specific — likely justified, but unstated)"
    proposed: "add necessity: OPTIONAL; state the cli rationale (AskUserQuestion is the tuned object)"
    why: "frontmatter floor + justify the cli narrowing"
  D9_brief_forge: { state: n/a-for-kind, nano: "n/a", finding: "config skill has no hand-off boundary", proposed: "n/a", why: "appropriate to kind" }
  D10_lessons:
    state: partial
    nano: "SKILL.md:147 (questions.jsonl telemetry)"
    finding: "near-bar: writes question telemetry (the substrate for learning) but does not itself consult/recommend tunings from it"
    proposed: "add a --suggest mode: read questions.jsonl, recommend never-ask for questions answered identically N times"
    why: "the operator-relation thread is half-built — data flows IN (telemetry) but no consultation flows back OUT as a suggestion"
  D11_subagent:
    state: n/a-for-kind
    nano: "config skill, no bulk work"
    finding: "n/a"
    proposed: "n/a"
    why: "appropriate to kind"
  D12_failure:
    state: present
    nano: "SKILL.md:110-115"
    finding: "uniform/strong (4 modes incl. injection-rejection)"
    proposed: "none"
    why: "n/a"
  D13_observability:
    state: present
    nano: "SKILL.md:44 (tombstone audit trail), 147 (questions.jsonl)"
    finding: "uniform — append-only preference audit + telemetry"
    proposed: "none"
    why: "n/a"
  D14_necessity:
    state: absent
    nano: "frontmatter: no necessity"
    finding: "below bar: no necessity field (it's OPTIONAL infra)"
    proposed: "necessity: OPTIONAL + gap_if_skipped: 'every AskUserQuestion always asks; no keystroke savings'"
    why: "field uniformity"
peer_comparison:
  strongest_peer_in_cohort: plan-tune sets the bar on D3(paths)/D4(entry-points)/D6/D12
  this_component_depth: above-bar on D1/D3/D4; below-bar only on D10(half), D14
  uplift_needed: add --suggest mode (close the learning loop), declare necessity
operator_decision_required: no
priority: low
```

### autoplan

```yaml
component: skills/autoplan/SKILL.md
kind: skill
cohort: 2
dimensions:
  D1_head:
    state: present
    nano: "SKILL.md:28-35 (Inputs + step 1 mode/skip confirm)"
    finding: "present; confirms chain composition before running"
    proposed: "validate that each chained skill exists/installed at head (fail fast if a member is missing)"
    why: "orchestrator should verify its dependencies before starting a multi-step chain"
  D2_tail:
    state: present
    nano: "SKILL.md:43,46-63 (Final verdict READY/NOT READY + status report)"
    finding: "strong: aggregates member verdicts into one READY/NOT-READY"
    proposed: "depends on uniform member verdict tokens (see ceo/design/devex CLEARED-token findings)"
    why: "aggregation is only as clean as the member verdict vocabulary"
  D3_objects:
    state: present
    nano: "SKILL.md:36,54 (~/.gstack/projects/<slug>)"
    macro: "orchestrates the shared design doc across all members"
    high: "chain integrity"
    finding: "PATH FRAGMENTATION: step 2 expects office-hours output at ~/.gstack/projects/ but office-hours WRITES ~/.lintel/projects/. The orchestrator encodes the wrong path"
    proposed: "normalize to ~/.lintel/projects/ everywhere"
    why: "the orchestrator is the worst place for the path bug — it propagates the wrong location to every step"
  D4_entrypoints:
    state: present
    nano: "SKILL.md:91-120 (examples), release-ev2 follows"
    finding: "uniform"
    proposed: "none"
    why: "n/a"
  D5_checkpoints:
    state: partial
    nano: "SKILL.md:82-87 (Idempotency — detects existing artifacts)"
    finding: "near-bar: idempotency-via-artifact-detection is a de-facto checkpoint, but no explicit per-step checkpoint record of WHERE the chain is"
    proposed: "write a chain-state marker (e.g. .autoplan-state.json: {step: 3, completed:[office-hours,ceo]}) so resume is explicit, not inferred"
    why: "artifact-inference is fragile; an explicit chain cursor matches the planner-checkpoint pattern"
  D6_recovery:
    state: present
    nano: "SKILL.md:76-79 (Failure modes — per-step pause + re-run), 82-87 (idempotent re-run)"
    finding: "strongest recovery in cohort: per-step pause-and-resume + idempotent re-run + --rerun granularity"
    proposed: "keep as bar"
    why: "this is the recovery/resume bar for multi-step skills"
  D7_pack: { state: n/a-unbuilt, nano: "frontmatter", finding: "see arch note — chain composition (which reviews fire) is the prime pack-driven decision", proposed: "per arch note: pack should set default chain membership", why: "see arch note" }
  D8_frontmatter:
    state: partial
    nano: "SKILL.md:1-9 (cli_support:[claude-code] only)"
    finding: "below bar: cli_support claude-only despite chaining codex-capable members (office-hours/ceo/eng/devex all support codex); missing necessity/expected_io"
    proposed: "broaden cli_support or justify; add necessity: OPTIONAL (convenience orchestrator)"
    why: "an orchestrator narrower than its members is a coverage inversion — members work on codex but the chain doesn't"
  D9_brief_forge:
    state: n/a-unbuilt
    nano: "n/a"
    finding: "see arch note — autoplan's step-to-step transitions (step 8 'read all review-log entries') ARE the Brief Forge aggregation site"
    proposed: "per arch note — autoplan is the #1 Brief Forge call site in the cohort"
    why: "see arch note"
  D10_lessons:
    state: absent
    nano: "not consulted"
    finding: "below bar: orchestrator doesn't consult lessons to decide default chain (e.g. 'this repo always needs design-review')"
    proposed: "read lessons/knowhow to pre-select chain members per repo history"
    why: "chain composition is a learnable preference; tie to plan-tune's --suggest idea"
  D11_subagent:
    state: partial
    nano: "no Task tool; chains skills which themselves may spawn"
    finding: "near-bar: delegates by invoking sub-skills (a form of delegation) but runs aggregation (step 8) inline"
    proposed: "spawn a subagent for the synthesize step (read N review-logs, render unified report)"
    why: "aggregation read of all logs is bulk work; isolate from main context"
  D12_failure:
    state: present
    nano: "SKILL.md:76-79"
    finding: "uniform/strong — per-member failure handling + Layer-2 aggregation exit"
    proposed: "none"
    why: "n/a"
  D13_observability:
    state: partial
    nano: "SKILL.md:42 (reads members' review-logs) — but writes NO autoplan-level log line"
    finding: "below bar: autoplan READS member logs but emits no own run-level record; an autoplan run itself is invisible to the aggregator"
    proposed: "emit an autoplan-run log: {skill:autoplan, chain:[...], final_verdict, members_cleared, commit}"
    why: "the orchestrator's own runs should be observable, not just its members'"
  D14_necessity:
    state: absent
    nano: "frontmatter: no necessity"
    finding: "below bar: no necessity field"
    proposed: "necessity: OPTIONAL + gap_if_skipped: 'operator runs 4-5 review skills manually with no aggregated verdict'"
    why: "field uniformity"
peer_comparison:
  strongest_peer_in_cohort: autoplan sets the D6 recovery/resume bar; plan-eng-review the gate bar
  this_component_depth: above-bar on D6/D12; below-bar on D3(path)/D8(cli)/D13(own-log)
  uplift_needed: fix projects path, broaden cli_support, emit own run log, explicit chain-state cursor
operator_decision_required: yes
priority: high
```

---

## Cohort summary

### Strongest / weakest peers

- **Strongest peer: `plan-eng-review`.** Sets the bar on D1 (BLOCKING Step 0), D2 (closed BLOCKING exit gate), D3 (richest output contract + JSONL), D11 (explicit outside-voice subagent), D13 (write-AND-verify-read closed loop). It is the depth target for the cohort. `office-hours` is co-strongest on D3 (shared-object schema) and D6 (5 enumerated failure modes); `autoplan` is strongest on D6 resume/idempotency; `plan-tune` is strongest on path-correctness (D3) and entry-point coverage (D4).
- **Weakest peer: `plan-design-review`.** Below bar on the most dimensions simultaneously: D3 (gstack-path bug), D5 (no checkpoint), D8 (cli_support claude-only AND missing necessity/io), D10 (no lessons). It also depends on an external gstack design binary. Uplift to eng-review depth is the largest single delta in the cohort.

### Top findings (cohort-wide)

1. **PATH FRAGMENTATION (correctness, high).** `office-hours` writes design docs to `~/.lintel/projects/`, but `plan-ceo-review`, `plan-eng-review`, `plan-design-review`, and `autoplan` all read/expect `~/.gstack/projects/`. `plan-tune` correctly uses `~/.lintel/`. The chain hand-off is literally broken at the directory level. **Uplift:** single-source the projects-dir constant; normalize all to `~/.lintel/projects/`. (Affects D1/D3 of 5 components.)

2. **OBSERVABILITY GAPS at chain head and orchestrator (high).** `office-hours` (chain step 1) and `autoplan` (the orchestrator) emit NO review-log line, while all 4 review skills do. autoplan's step-8 "read all review-log entries from this run" therefore silently misses the first step and never records its own aggregate run. **Uplift:** both emit a log line; additionally the 4 reviews call `~/.claude/skills/gstack/bin/gstack-review-log` — an external gstack-plugin binary path, violating first-party-first. Route through a Lintel-owned `li-review-log`. (Affects D13 across the cohort.)

3. **NECESSITY + lessons consultation absent cohort-wide (high).** No component declares `necessity`/`gap_if_skipped` in frontmatter (only prose), even `plan-eng-review` which IS the required gate. Separately, NO component consults `lessons.md`/knowhow — including the three skills where memory would compound most (office-hours premises, ceo-review founder-signal synthesis, devex TTHW trend). The operator-relation and repo-relation learning threads are written-but-not-consulted. **Uplift:** add `necessity`+`gap_if_skipped` fields everywhere; wire lessons/knowhow reads into the context-loading step of each. (Affects D8/D10/D14.)

### Secondary findings

- **Verdict-vocabulary fragmentation (medium):** eng/ceo emit verdict tokens (CLEARED/LOCKED); design/devex emit only score deltas. autoplan's "any review NOT CLEARED" aggregation needs every member to emit a token.
- **cli_support inversions (medium):** `plan-design-review`, `plan-tune`, and `autoplan` declare `[claude-code]` only; office-hours/ceo/eng/devex include codex. autoplan being narrower than its codex-capable members is a coverage inversion.
- **plan-devex-review internal inconsistency (low-medium):** examples cite a "Step 0" that the Workflow section does not contain — reconcile.
- **No mid-flight checkpoints (medium):** only autoplan (via artifact-idempotency) and eng-review (exit gate) have any resume discipline; ceo/design/devex multi-question loops restart from zero on interruption.
- **plan-tune learning loop half-built (low):** writes question telemetry but offers no `--suggest` consult-back. Closing it would make the operator-relation thread bidirectional.

### Designed-not-built (recorded once, not per-component)

- **D7 pack/WorkProfile runtime influence** — no planner skill declares or resolves a pack. Prime future knobs: ceo scope-expansion-vs-reduction default, eng granularity/completeness targets, devex TTHW baselines, autoplan chain composition.
- **D9 Brief Forge** — every chain hand-off (office-hours→ceo→eng→design/devex) and autoplan's step-8 aggregation are the call sites. **autoplan is the #1 Brief Forge integration point in the cohort.**
- Envelope / wiki — not referenced by any cohort member.

### Operator decisions required: 5

`office-hours`, `plan-ceo-review`, `plan-design-review`, `plan-devex-review`, `autoplan` are marked `operator_decision_required: yes` (path normalization, first-party log binary, cli_support breadth, lessons wiring, verdict tokens). `plan-eng-review` (no — uplift is additive/non-controversial) and `plan-tune` (no — low-priority polish).
