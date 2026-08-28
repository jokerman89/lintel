# Cohort 7 — pack lifecycle skills + role/profile mechanics + WorkProfile logic

**Audit date:** 2026-05-29
**Branch:** v4.0-phase1-meta-infra-spine
**Auditor:** uniformity auditor (cohort 7)
**Scope:** all role/profile mechanics that exist today, WorkProfile resolution, pack-resolver consumer consistency, and an arch-level note on the designed-not-built pack lifecycle skills.

---

## Components covered

| Component | Kind | State |
|---|---|---|
| `skills/role-activate/SKILL.md` | skill | present |
| `skills/role-rotate/SKILL.md` | skill | present |
| `skills/role-deactivate/SKILL.md` | skill | present |
| `skills/role-frame/SKILL.md` | skill | present |
| `skills/role-deep-dive/SKILL.md` | skill | present |
| `skills/role-new/SKILL.md` | skill | present |
| `skills/role-update/SKILL.md` | skill | present |
| `skills/roles-list/SKILL.md` | skill | present |
| `roles/field-cto.md` | role-file | present |
| `roles/solution-architect.md` | role-file | present |
| `roles/engineering-manager.md` | role-file | present |
| `lib/pack-resolver.sh` | lib | present |
| `packs/_default/pack.yaml` | pack | present |
| `pack-new/switch/edit/remove/list/validate/export/import` | skill | **designed-not-built** |
| `skills/workprofile-toggle` | skill | **referenced-not-built** |

**Verified count:** 8 role skills (7 `role-*` + `roles-list`), 3 role files, 1 pack, 1 resolver lib. NOT 7 — the prompt's "glob role-*" missed `roles-list` (named `roles-` not `role-`), which IS the 8th role skill and IS the one all three locator skills depend on.

**Strongest in cohort:** `roles/*.md` (the three role files) — perfectly uniform schema, all six declared sections present in all three, frontmatter identical in shape. The role-file layer is the depth bar for this cohort.

**Weakest in cohort:** `lib/pack-resolver.sh` as an *interface* — not because the code is thin (it is the most engineered artifact here) but because it has **zero consumers**. The strongest-built component in the cohort is the one nothing uses. That is the cohort's central finding.

---

## Role-skill finding records

### component: skills/role-activate/SKILL.md

```yaml
component: skills/role-activate/SKILL.md
kind: skill
cohort: 7
dimensions:
  D1_head:
    state: present
    nano: "frontmatter:name + body 'You are the role-activate skill'"
    macro: role-overlay subsystem, fires pre-engagement or mid-cycle
    high: explicit-invocation promise
    finding: uniform with cohort — explicit slash-invocation, $1 role-id input
    proposed: none
    why: at-bar
  D2_tail:
    state: present
    nano: "SKILL.md:127 Status protocol DONE/BLOCKED/NEEDS_CONTEXT"
    macro: writes profile.yaml + 00-state event
    high: explicit-exit promise
    finding: uniform — three-state status protocol, all role skills share it
    proposed: none
    why: at-bar
  D3_objects:
    state: present
    nano: "SKILL.md:36 ROLE_ID=$1 in; profile.yaml + context block out"
    macro: input is role-id string, output is ~500-token context injection
    high: in/out contract
    finding: contract is documented in body but not in frontmatter (no expected_inputs/outputs field)
    proposed: add expected_inputs/expected_outputs frontmatter to match the cohort-1 phase-skill standard
    why: achieve declared contract at frontmatter level; pack.yaml + design doc already model declared I/O — roles should match. gstack skills declare args in frontmatter; steal that.
  D4_entrypoints:
    state: present
    nano: "SKILL.md:138 Hop-in support: YES"
    macro: invokable anytime; also chained-to by role-rotate (delegates here)
    high: entry-point coverage
    finding: uniform — hop-in declared; reachable directly and via role-rotate Step 5
    proposed: none
    why: at-bar
  D5_checkpoints:
    state: present
    nano: "SKILL.md:118 Step 5 — 00-state.md append (role_activated event)"
    macro: 00-state is the resume substrate
    high: cross-session memory promise
    finding: uniform — all 8 role skills append a typed 00-state event
    proposed: none
    why: at-bar — role skills are actually MORE consistent on D5 than some phase skills
  D6_recovery:
    state: present
    nano: "SKILL.md:161 Failure recovery (role file not found / profile malformed / shared machine)"
    macro: recovery falls back to roles-list + prompt
    high: stub-and-continue / operator-choice
    finding: uniform and strong — three named recovery branches
    proposed: none
    why: above-bar; this is the recovery model other cohorts should copy
  D7_pack:
    state: absent
    nano: "SKILL.md:75 sed profile.yaml role_active; no pack-resolver source"
    macro: role activation should respect pack.roles.default_role + pack.roles.source
    high: PACK-DRIVEN-BEHAVIOR promise — THE center of this cohort
    finding: role-activate ignores the pack entirely. pack.yaml declares roles.source + roles.default_role (pack.yaml:31-33) but role-activate hardcodes the role search path (roles/, $LINTEL_HOME/roles/private/, $LINTEL_HOME/roles/) and never consults the active pack. A pack that ships its own roles dir or sets default_role has no effect.
    proposed: source lib/pack-resolver.sh; resolve roles.source for the search path and roles.default_role when $1 omitted. Keep the hardcoded triple as final fallback (NO-CUT).
    why: the v4.0 design makes the pack the single source of identity-bound state; roles are identity-bound. A pack-scoped role library is the whole point of packs. Most elegant form: one resolve_pack_field call prepended to the existing search loop — additive, not a rewrite.
  D8_frontmatter:
    state: partial
    nano: "frontmatter lines 1-9: name/layer/description/color/tools/voice/cli_support present"
    macro: frontmatter completeness standard from D8
    high: declared-metadata promise
    finding: missing necessity, expected_inputs/outputs, brief_forge_handoffs, navigation. cli_support uses short-list form [claude-code, codex] while profile-switch uses long object form — inconsistent within the same cohort.
    proposed: add necessity (OPTIONAL), expected_inputs/outputs; normalize cli_support to ONE form repo-wide
    why: uniform frontmatter is the audit's core promise; cli_support form-drift is a concrete X-cohort inconsistency
  D9_brief_forge:
    state: absent
    nano: "not declared anywhere in SKILL.md"
    macro: role-activate injects context that subagents inherit (SKILL.md:151)
    high: BRIEF-FORGE-AT-HANDOFFS promise
    finding: role-activate's whole job is injecting a role brief that downstream subagents inherit — this IS a hand-off, and pack.yaml:67 declares brief_forge on_subagent_spawn enabled, but role-activate never invokes it. The injected role context is not Brief-Forge-evaluated.
    proposed: declare brief_forge_handoffs in frontmatter; on context-injection, route through the on_subagent_spawn evaluators (security, stale) per pack default
    why: the pack already promises Brief Forge fires on subagent spawn; role overlay propagation to subagents is exactly that path. Flag as should-fire-doesn't.
  D10_knowledge:
    state: absent
    nano: "no lessons.md or knowhow consultation in workflow"
    macro: role activation could consult role-specific lessons
    high: KNOWLEDGE-TAG-FUNNEL promise
    finding: role-activate doesn't consult lessons even though role-update WRITES role learnings — the write side exists, the read side doesn't close the loop
    proposed: on activate, surface any lessons tagged with this role-id (operator-relation evolution thread)
    why: X3 (operator-relation evolution) requires the lessons loop to be bidirectional; role-update writes, nothing reads
  D11_subagent:
    state: implicit
    nano: "SKILL.md:151 'context that subagents inherit'"
    macro: role context is meant to propagate to spawned subagents
    high: dedicated-vs-inline rule
    finding: role-activate is correctly inline (lightweight, no spawn) — appropriate. But it relies on subagents inheriting context without a curated brief (tie to D9).
    proposed: none for spawn; see D9 for brief curation
    why: at-bar — inline is correct here
  D12_failure:
    state: present
    nano: "SKILL.md:128 BLOCKED on file-not-found/malformed; SKILL.md:161 recovery"
    macro: failure halts activation, lists alternatives
    high: consistent-failure-mode
    finding: uniform — ask-operator/list-alternatives, no silent failure
    proposed: none
    why: at-bar
  D13_observability:
    state: partial
    nano: "SKILL.md:119 00-state event written"
    macro: 00-state is operator-visible; no usage-log / hooks.jsonl write
    high: OBSERVABILITY promise
    finding: writes 00-state but not the usage log. pack-resolver writes pack-resolver.jsonl (resolver:43); role skills have no equivalent audit stream. Operator can see role activated in 00-state but not in a queryable usage log.
    proposed: emit a usage-log line on activation (and rotation/deactivation) like pack-resolver does
    why: pack-resolver sets the observability bar (jsonl audit); role skills should match it
  D14_necessity:
    state: absent
    nano: "no necessity field in frontmatter"
    macro: role overlay is OPTIONAL within cycle
    high: NECESSITY-DECLARATION promise
    finding: no necessity / gap_if_skipped declared. Implicitly OPTIONAL (the When-NOT-to-use lists solo-engineering) but not formally stated.
    proposed: necessity: OPTIONAL; gap_if_skipped "customer-facing artifacts ship in operator's raw voice without role calibration"
    why: X5 — necessity is load-bearing for the orientator's workflow recommendations
peer_comparison:
  strongest_peer_in_cohort: roles/field-cto.md (role-file layer)
  this_component_depth: at-bar on lifecycle dims (D1/D2/D5/D6/D12), below-bar on pack-influence (D7) and brief-forge (D9)
  uplift_needed: wire pack-resolver (D7) + brief-forge (D9) + necessity (D14) — raise to the pack-driven bar the design promises
operator_decision_required: yes
priority: high
```

### component: skills/role-rotate / role-deactivate / role-frame / role-deep-dive / role-update / roles-list (shared record)

These six share role-activate's dimensional profile almost exactly. Recording deltas only.

```yaml
component: skills/role-rotate/SKILL.md
kind: skill
cohort: 7
shared_with_role_activate: D1,D2,D4,D5,D6,D8,D10,D12,D13,D14 (same state + same gaps)
deltas:
  D3_objects: present — in: new-role-id; verifies new role exists BEFORE deactivating current (rotate:44) — strongest atomicity in cohort
  D7_pack: absent — hardcodes same role-path triple (rotate:49-54); same pack-blindness as role-activate
  D9_brief_forge: absent — sensitivity transition (rotate:64) is a hand-off boundary where stale/security evaluators SHOULD fire
  D11_subagent: present-warning — anti-pattern flags >3 rotations cause "context jitter, confuses subagents" (rotate:129) — only skill in cohort that reasons about subagent context hygiene
peer_comparison:
  this_component_depth: at-bar; verify-before-destroy (rotate:44) is above-bar atomicity
  uplift_needed: pack-resolver for role-path (D7); brief-forge on sensitivity transition (D9)
operator_decision_required: yes
priority: medium
```

```yaml
component: skills/role-deactivate/SKILL.md
kind: skill
cohort: 7
shared_with_role_activate: D1,D2,D4,D5,D6,D8,D10,D11,D12,D13,D14
deltas:
  D2_tail: present + extra — declares DONE_WITH_CONCERNS for "sensitive context may still be in conversation history" (deactivate:79) — most honest tail-state in cohort
  D7_pack: absent — reverts voice to "mode_default OR profile.voice_tier_default" (deactivate:58) instead of pack voice.default_tier. Should revert to pack-resolved voice.default_tier.
  cross_ref: references /li:workprofile-toggle indirectly via the WorkProfile/profile-switch boundary; workprofile-toggle is NOT built (see designed-not-built note)
peer_comparison:
  this_component_depth: at-bar; DONE_WITH_CONCERNS honesty is above-bar
  uplift_needed: revert voice to pack.voice.default_tier not profile default (D7)
operator_decision_required: yes
priority: medium
```

```yaml
component: skills/role-frame/SKILL.md
kind: skill
cohort: 7
shared_with_role_activate: D1,D2,D5,D6,D8,D12,D14
deltas:
  D3_objects: present + strongest — in: artifact-path; out: structured findings block (strengths/gaps/voice-misalignment/decision-criteria-fit/prioritized-edits) (frame:62-92). Richest output contract in cohort.
  D4_entrypoints: present + chain — declares it could chain into /li:rais-customer-voice-check (frame:151)
  D7_pack: absent — applies role lens but doesn't check pack.voice.enforce; a pack with enforce:customer_facing should make role-frame's voice findings BLOCKING not advisory
  D9_brief_forge: absent — frame output is operator-internal but for private roles writes role-lens-notes (frame:99); a hand-off candidate
  D11_subagent: implicit — large-artifact path (frame:163 caps at top-N sections) is a candidate for subagent delegation (read big artifact off-context) but runs inline
peer_comparison:
  this_component_depth: above-bar on D3 output richness; below-bar on D7/D11
  uplift_needed: honor pack.voice.enforce for blocking severity (D7); delegate large-artifact read to subagent (D11)
operator_decision_required: yes
priority: medium
```

```yaml
component: skills/role-deep-dive/SKILL.md
kind: skill
cohort: 7
shared_with_role_activate: D1,D2,D4,D5,D6,D8,D10,D12,D14
deltas:
  D3_objects: present — in: role-id (defaults to active); out: full ~2-3k role content + cost note
  D7_pack: absent — same role-path triple (deep-dive:50); ignores pack roles.source
  D13_observability: present + best-in-cohort — emits token-cost note (deep-dive:71) AND budget-impact line. Only role skill that reports its own cost. This is the observability bar the others should meet.
  D11_subagent: anti-pattern-aware — explicitly warns NOT to deep-dive at session start (too heavy) (deep-dive:120); cost-conscious design
peer_comparison:
  this_component_depth: above-bar on cost-observability (D13); below-bar on D7
  uplift_needed: pack roles.source (D7)
operator_decision_required: yes
priority: medium
```

```yaml
component: skills/role-new/SKILL.md
kind: skill
cohort: 7
shared_with_role_activate: D1,D2,D5,D6,D8,D12,D14
deltas:
  D3_objects: present + strongest-template — renders a full role file matching the exact 6-section schema of roles/*.md (new:85-132). This skill is the SOURCE of role-file uniformity — that the three files match is because this template enforces it.
  D7_pack: absent — saves to roles/<id>.md (public) or $LINTEL_HOME/roles/private/ (new:135-141); should save to active pack's roles.source when a pack scopes roles
  D9_brief_forge: n/a — pure creation, no hand-off
  D11_subagent: implicit — 13-step interview runs inline (correct; operator-interactive)
  pii_discipline: present + strong — soft-refuses PII in COLD KNOWLEDGE (new:199); sensitivity-first
peer_comparison:
  this_component_depth: at-bar; template-as-schema-enforcer is above-bar (it is WHY the role files are uniform)
  uplift_needed: pack-scoped save location (D7)
operator_decision_required: yes
priority: low
```

```yaml
component: skills/role-update/SKILL.md
kind: skill
cohort: 7
shared_with_role_activate: D1,D2,D5,D6,D8,D12,D14
deltas:
  D7_pack: absent — same path resolution; ignores pack
  D10_knowledge: present (write-side) — this is the ONLY role skill that closes a learning loop: captures engagement learnings back into the role file (update:14-22). The operator-relation evolution thread (X3) is half-built here: writes exist, reads (role-activate consulting these) don't.
  D13_observability: present — 00-state role_updated event with update_type; plus optional bin/li-roles-sync push (update:106)
  integrity_check: present + unique — re-reads file post-edit to verify frontmatter still parses (update:98), reverts on corruption. Only role skill with post-write integrity verification.
peer_comparison:
  this_component_depth: at-bar; post-write integrity check (update:98) is above-bar
  uplift_needed: pack-scoped target (D7); ensure role-activate reads what this writes (D10 loop closure)
operator_decision_required: yes
priority: medium
```

```yaml
component: skills/roles-list/SKILL.md
kind: skill
cohort: 7
shared_with_role_activate: D1,D2,D4,D8,D12
deltas:
  role_in_cohort: this is the keystone — role-activate:50, role-rotate:58, role-deep-dive:42, role-update:43 ALL fall back to /li:roles-list on not-found. If roles-list were missing, four skills' recovery paths would dangle. It exists, so the cohort is internally coherent.
  D5_checkpoints: present-light — 00-state event marked "(light, optional)" (roles-list:80) — only role skill that downgrades its own checkpoint
  D6_recovery: n/a — pure query
  D7_pack: absent — globs roles/, $LINTEL_HOME/roles/, $LINTEL_HOME/roles/private/ (roles-list:36-44); does NOT list pack-scoped roles.source. A pack shipping roles would have invisible roles.
  D9_brief_forge: n/a
  D11_subagent: n/a — inline query, correct
peer_comparison:
  this_component_depth: at-bar
  uplift_needed: include pack roles.source in enumeration (D7)
operator_decision_required: no
priority: low
```

---

## Role-file schema-uniformity table

All three role files declare the SAME six body sections plus uniform frontmatter. **The role-file layer is the most uniform component family in the entire audit so far.**

| Section / field | field-cto | solution-architect | engineering-manager | uniform? |
|---|---|---|---|---|
| frontmatter: role_id | yes | yes | yes | ✅ |
| frontmatter: display_name | yes | yes | yes | ✅ |
| frontmatter: scope | yes | yes | yes | ✅ |
| frontmatter: audience | yes | yes | yes | ✅ |
| frontmatter: voice_tier | trailblazer | mixed | internal | ✅ (all present) |
| frontmatter: sensitivity | public | public | public | ✅ |
| frontmatter: last_updated | 2026-05-28 | 2026-05-28 | 2026-05-28 | ✅ |
| frontmatter: applies_to_phases | 5 phases | 5 phases | 6 phases | ✅ (all present) |
| frontmatter: companion_agents | yes | yes | yes | ✅ |
| body: IDENTITY | yes | yes | yes | ✅ |
| body: COLD KNOWLEDGE (top 10) | 10 items | 10 items | 10 items | ✅ |
| body: DECISION CRITERIA | yes (4 stances) | yes (4 stances) | yes (4 stances) | ✅ |
| body: VOICE + COMMUNICATION | yes | yes | yes | ✅ |
| body: OUTCOME LENS (8 phases) | 8 | 8 | 8 | ✅ |
| body: ROLE-SPECIFIC INSIGHTS | yes | yes | yes | ✅ |
| body: COMPANION SKILLS | yes | yes | yes | ✅ |
| body: SENSITIVE CONTEXT | n/a (public) | n/a (public) | n/a (public) | ✅ (template-optional, all 3 public) |

**Schema uniformity verdict:** the prompt's hypothesis ("do all 3 declare the same sections including COMPANION SKILLS?") is confirmed YES on all six named sections. The uniformity is not accidental — `role-new/SKILL.md:85-132` renders this exact template, so every role created through the harness inherits the schema. This is the cohort's model for how uniformity SHOULD be enforced: a generator that bakes the schema in.

**Are 8 skills for 3 roles proportionate?** — Yes, and here is why it is NOT over-engineering:
- The 8 skills are a complete *lifecycle*, not 8 variations on activation: create (role-new), list (roles-list), load-light (role-activate), load-heavy (role-deep-dive), swap (role-rotate), clear (role-deactivate), apply (role-frame), evolve (role-update).
- The skill count scales with *operators creating their own roles* (role-new is for customer-specific private personas), not with the 3 shipped public roles. 3 is the seed; the design intends operator-grown role libraries.
- Compare to pack lifecycle: the same CRUD-plus-lifecycle shape is DESIGNED for packs (8 pack-* skills) but not built. Roles are the *proof* that the lifecycle shape is the right one — packs should follow it.
- The one redundancy worth flagging: role-rotate is role-deactivate + role-activate composed (rotate:69-80 literally delegates to role-activate). That is acceptable composition (a named convenience for the common mid-session swap), not duplication — it adds the atomicity guarantee (verify-new-before-drop-current) the two-step manual sequence lacks.

**Verdict: proportionate.** No cut. If anything the cohort under-delivers on D7 (pack influence), not on skill count.

---

## pack-resolver consumer-consistency finding — CENTER OF COHORT (D7)

```yaml
finding_id: C7-PACK-RESOLVER-ZERO-CONSUMERS
kind: architectural / D7
severity: high
state: FRAGMENTED — but in a specific way: not "some use it, some hardcode" but "NONE use it; ALL hardcode"
```

**The verified fact.** `lib/pack-resolver.sh` documents itself (line 2) as "a critical-path interface used by 30+ skills." Grep of `skills/` for `pack-resolver`, `resolve_pack_field`, `pack_field_is_true`, `get_loaded_pack`, `get_active_pack_name`, `source.*pack-resolver`, `lib/pack-resolver` returns **zero matches**. Grep of `skills/` for `pack.yaml` or `active-pack` also returns **zero matches**. The resolver's only references repo-wide are: itself, its two test files (`tests/unit/pack-resolver-fallbacks.sh`, `tests/shape/pack-resolver-fallbacks.sh`), `bin/_audit.sh`, and design/concept docs.

**So the consistency answer is unambiguous:** the pattern is NOT consistent across consumers, because there are no consumers. The interface exists, is well-engineered (explicit failure semantics, per-session cache, cycle-detection on `extends:`, jsonl audit, hardcoded last-resort fallbacks at resolver:174-185, a self-test harness), and is consumed by exactly nothing in the skill layer. The "30+ skills" in the header is a *forward-looking design assertion*, not a description of today.

**How the gap manifests instead.** Skills that NEED pack-bound state get it the OLD way — direct grep of `~/.lintel/profile.yaml`:
- `skills/sense/SKILL.md:122` — `workprofile=$(grep -E '^workprofile:' "$PROFILE" | awk '{print $2}')`
- `skills/context-warm-from-url/SKILL.md:43` — `workprofile=$(grep '^workprofile:' "$LINTEL_HOME/profile.yaml" | awk '{print $2}')`
- `skills/role-activate/SKILL.md:75` — `sed -i "s/^role_active:.*/..." profile.yaml` (and all 8 role skills read role_active the same grep-profile.yaml way)
- `skills/compliance-gate/SKILL.md:155` — reads `~/.lintel/profile.yaml` for WorkProfile

So there ARE two parallel state-resolution patterns in the repo today: (1) the NEW pack-resolver reading `pack.yaml` via dotted-path, with nobody calling it; (2) the OLD direct-grep of `profile.yaml`, used by everybody who needs state. They resolve DIFFERENT files for the SAME logical values (e.g. WorkProfile lives in `compliance.workprofile_default` in pack.yaml AND in `workprofile:` in profile.yaml).

**proposed (NO-CUT):** keep both files (profile.yaml is operator-mutable session state; pack.yaml is pack-shipped defaults — they are not redundant), but make the resolver the single read path. Skills call `resolve_pack_field`, and the resolver internally layers profile.yaml overrides on top of pack.yaml defaults (operator override > pack default > hardcoded fallback). Migrate consumers one at a time starting with sense (the documented "parse once at SENSE Step 1" entry the resolver header already assumes at resolver:11). The resolver is BUILT and TESTED; the work is wiring, not authoring.

**why this specifically:** the v4.0 design's whole thesis is "the pack is the single source of identity-bound state." That promise is currently 0% upheld at the consumer layer despite the interface being 100% built. This is the single highest-leverage finding in the cohort: one well-tested lib, zero adoption. The elegant move is not to write more resolver code — it is to delete the duplicate grep-profile.yaml lines in 5+ skills and replace each with one `resolve_pack_field` call, which is subtraction (fewer parsing patterns) in service of the pack promise. gstack/speckit precedent: a config-resolver that every command sources at head is the standard; the resolver already mirrors that shape — it just needs the `source` lines added at each skill head.

---

## WorkProfile finding (D7)

```yaml
finding_id: C7-WORKPROFILE-DUAL-LOCATION
kind: architectural / D7 / schema-discipline
severity: high
state: INCONSISTENT — value lives in TWO schemas with no single read path
```

**The verified fact.** WorkProfile exists in two places:
1. NEW: `packs/_default/pack.yaml:23` — `compliance.workprofile_default: off`, with the inline comment "was a separate concept; now a pack field." The resolver knows it: `resolve_pack_field compliance.workprofile_default` has a hardcoded fallback `off` at `lib/pack-resolver.sh:178`.
2. OLD: `~/.lintel/profile.yaml` top-level `workprofile:` — which is what every skill actually reads (sense:122, context-warm-from-url:43, compliance-gate:155, ship/review/plan/fix/capture all branch on "if WorkProfile=on").

**No skill reads `compliance.workprofile_default`.** Every WorkProfile consumer (12 skill files: sense, cycle, review, plan, compliance-gate, capture, ship, plan-and-build, fix, context-warm, context-warm-from-url, context-warm-customer, context-snapshot) branches on the profile.yaml value via direct grep. The pack field is declared, defaulted, and resolver-supported — and dead.

**Consistency within the OLD pattern:** the profile.yaml read is itself *internally* consistent — all consumers grep `^workprofile:` and compare to `"on"`. So the OLD mechanism works uniformly. The problem is purely that the v4.0 migration (workprofile → compliance.workprofile_default) was declared in the pack and the resolver but never propagated to consumers, leaving the canonical value in the about-to-be-legacy location.

**proposed (NO-CUT):** route WorkProfile through `resolve_pack_field compliance.workprofile_default`, with the resolver layering the operator's profile.yaml `workprofile:` value as an override on top of the pack default (so an operator can still toggle per-session without editing the pack). This preserves BOTH files' roles. The `/li:workprofile-toggle` skill referenced at profile-switch:39 (and implied by role-deactivate's voice-revert) is NOT BUILT — it should be the operator-facing front door that writes the profile.yaml override the resolver reads. Build it as part of this migration.

**why:** shared-schema discipline (one definition, both sides import) is violated — WorkProfile is defined in two schemas and reinterpreted independently. The design already chose the pack as canonical ("now a pack field"); finishing the migration is upholding a decision already made, not making a new one. Most elegant: the toggle skill writes one line to profile.yaml, the resolver merges it over the pack default, every consumer calls one resolver function. Three moving parts replace twelve grep sites.

---

## Designed-not-built lifecycle note (arch-level, single finding — not per-skill spam)

```yaml
finding_id: C7-PACK-LIFECYCLE-DESIGNED-NOT-BUILT
kind: architectural / contract-ahead-of-implementation
severity: medium (expected per v4.0 Ch.1 FR-B phasing)
state: CONTRACT-PRESENT, IMPLEMENTATION-PENDING
```

The pack lifecycle skills — **pack-new, pack-switch, pack-edit, pack-remove, pack-list, pack-validate, pack-export, pack-import** — are designed in v4.0 Ch.1 FR-B but not built. Glob `skills/pack-*` returns nothing. What EXISTS today: the `_default` pack (`packs/_default/pack.yaml`), the resolver (`lib/pack-resolver.sh`) which already implements `validate_pack` (the pack-validate engine, resolver:86) and `get_active_pack_name` / active-pack file handling (the pack-switch substrate, resolver:57), and fallback tests.

**This is NOT 8 separate findings.** The contract is coherent and ahead of the skills:
- `pack-validate`'s logic is ALREADY in the resolver (`validate_pack`, including the three failure modes: missing file, missing required field, `extends:` cycle). The skill would be a thin operator-facing wrapper.
- `pack-switch`'s substrate (active-pack file, cache-clear semantics at resolver:256 `clear_pack_cache`) is built.
- `pack-list` would mirror `roles-list` exactly (which IS built — a ready template).
- `pack-new` would mirror `role-new` (built — the interview-to-render pattern is proven).
- `pack-export`/`pack-import` map to the `shareable:` field (pack.yaml:11) and `requires_lintel:` compat gate (pack.yaml:89).

**Observation worth surfacing:** the role lifecycle (8 skills, BUILT) and the pack lifecycle (8 skills, DESIGNED) are the same lifecycle shape. Roles are the working proof-of-pattern. The cleanest path to the pack skills is to *port the role lifecycle skills* — they are structurally identical (locate by id across home/repo paths, frontmatter-parse, render-from-template, sensitivity-aware, 00-state events). The resolver already supplies the engine the role skills lacked. **proposed (NO-CUT):** when building the 8 pack-* skills, generate them from the role-* skills as templates + wire each to the resolver functions that already exist. This is additive and reuses proven shape.

**why this specifically:** the audit's NO-CUT rule applies — nothing here is cut. The note records that the contract (pack.yaml + resolver + design doc) is built ahead of the operator-facing skills, which is correct phasing, and that the build path is "port roles + wire resolver," the most elegant route because both halves already exist.

---

## Cohort 7 summary

- **Strongest:** `roles/*.md` (role-file layer) — perfect six-section schema uniformity across all three, enforced by the `role-new` generator template. The model for how uniformity should be guaranteed (generator bakes the schema).
- **Weakest:** `lib/pack-resolver.sh` *as an interface* — the best-engineered, best-tested artifact in the cohort, with zero consumers. Strongest code, weakest adoption.
- **Center (D7) verdict:** pack influence on this cohort's components is ~0%. Every role skill hardcodes its role-path triple and ignores pack `roles.source`/`roles.default_role`. WorkProfile is read from legacy profile.yaml, not the canonical `compliance.workprofile_default`. The pack-driven-behavior promise is declared everywhere and upheld nowhere at the consumer layer.
- **Proportionality:** 8 role skills for 3 seed roles is proportionate — it is a complete lifecycle sized for operator-grown role libraries, and it is the working proof-of-pattern for the not-yet-built pack lifecycle.
- **operator_decision_required count: 7** (role-activate, role-rotate, role-deactivate, role-frame, role-deep-dive, role-new, role-update — each needs the pack-resolver wiring decision; roles-list = no).

### Top 3 cohort findings (ranked by leverage)

1. **C7-PACK-RESOLVER-ZERO-CONSUMERS (high)** — built, tested, 30+-skill-critical-path interface with zero callers; every skill hardcodes profile.yaml grep instead. Highest leverage: wiring already-built code, deleting duplicate parse sites (subtraction).
2. **C7-WORKPROFILE-DUAL-LOCATION (high)** — canonical value migrated to `compliance.workprofile_default` in pack + resolver, but all 12 consumers still read legacy `profile.yaml:workprofile`. Shared-schema discipline violated; finish a migration already decided. (`workprofile-toggle` skill referenced but not built — build as the front door.)
3. **C7-ROLE-PACK-BLINDNESS (high)** — all 8 role skills hardcode the role-path triple and never consult pack `roles.source`/`roles.default_role`, so a pack that ships its own role library or default role has no effect; the per-skill D7 records aggregate to this one architectural gap.
```
