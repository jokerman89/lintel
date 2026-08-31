# Lintel battletest — six-persona adversarial synthesis + remediation plan

> 2026-06-12. Operator directive: attack everything; every undefensible service is replaced,
> integrated, or overcome in delivery; never lose functionality, never make anything worse;
> no retreat except planned. Six personas (grumpy veteran · security attacker · noob · hype
> early-adopter · pragmatic daily-driver · competitor analyst) + a gstack de-heritage inventory.
> This is the authoritative findings register. Status column tracked to closure.

## The one truth all six personas hit

Lintel's value is real but **concentrated in a ~2k-line kernel** (4 safety hooks, pack
resolver, lessons/memory, capture discipline). Everything around it is either (a) shipped but
inert, (b) prose that tells the model to be smart instead of making smartness structural, or
(c) ceremony/breadth that has already rotted once. Two meta-failures cause most findings:
**nothing measures whether a mechanism fires or helps**, and **tests assert documentation, not
behavior**. The maintainer's own fit audit predicted this; the battletest confirms it from six
angles and adds a security dimension the fit audit missed entirely.

## Severity register (KO = indefensible as-is · HARD = real damage · JAB = improvable)

### KO — indefensible, fix or replace now

| # | Finding | Persona | Disposition |
|---|---|---|---|
| K1 | **`li-scaffold` sed templating = operator-priv RCE** — `$NAME` spliced into GNU `sed s///`; a repo dir named `x/;e touch …` executes shell | security | **FIX NOW** (Wave S) |
| K2 | **Block hooks bypassable** — `^git` anchor (`true && git commit`, `git -C .`), `commit -am` stages after PreToolUse, staged-vs-worktree gap | security | **FIX NOW** (Wave S) — move to real git pre-commit/pre-push + broaden matcher + fail-closed |
| K3 | **Modern secret formats slip the BLOCK tier** — `sk-proj-`, `github_pat_`, `AIza`, `sk_live_` unmatched | security | **FIX NOW** (Wave S) — adopt maintained ruleset patterns |
| K4 | **Vault sink leaks PII** — writes session content outside repo; privacy is prose; no hook sees the Write; customer-PII never scanned | security | **FIX NOW** (Wave S) — programmatic scan_secrets+scan_customer before vault write |
| K5 | **resume ⇄ context-save mutually blind** — resume reads only 00-state/jobs, never the checkpoint that exists; misdirects to /li:cycle | daily-driver | **FIX NOW** (Wave H) |
| K6 | **Cost gates approve invented numbers** — `$<X>` with no pricing table; `tokens_est_typical` declared by zero skills → 3k default; estimator never calibrated | grumpy, daily-driver | **FIX NOW** (Wave H) — replace fiction with honest task-count + "uncalibrated" label |

### HARD — real damage, fixed or planned-with-date

| # | Finding | Persona | Disposition |
|---|---|---|---|
| H1 | Tests assert text, not behavior (37/75 grep-only; `behavior/` has one soup test) | grumpy, early-adopter, competitor | **PLAN** → eval-harness ADR + behavior tests per mechanism |
| H2 | Cycle state machine never completes a real cycle (only an abandoned half) | grumpy | **FIX via dogfood** — this very cycle runs the ledger end-to-end |
| H3 | `bin/` happy paths broken & unexercised (li-adr-new exits 2; audit_count `0\n0`) | grumpy | **FIX NOW** (Wave B) + bin smoke test |
| H4 | No agent `memory:` frontmatter — the brand is memory, 0/69 agents have it | early-adopter | **FIX NOW** (Wave M) — reviewer/auditor/test agents get `memory: project` |
| H5 | No prompt evals in CI for a 20.7k-line prompt product | early-adopter, competitor | **PLAN** → eval-harness ADR (with H1) |
| H6 | DEFINE interrogates feature work like a startup founder; ignores scope.md size | daily-driver | **FIX NOW** (Wave H) — feature fast-path keyed off scope size |
| H7 | CAPTURE back-loads 4-9 questions → fatigue kills the capture loop | daily-driver | **FIX NOW** (Wave H) — batch into one multi-select |
| H8 | Override+audit theater — inline override bypasses with no audit; audit log newline-injectable; self-owned | security | **FIX NOW** (Wave S) |
| H9 | BUILD bans parallel fan-out (platform shipped Agent Teams/Dynamic Workflows) | early-adopter | **PLAN** → BUILD-parallelism ADR (A/B first) |
| H10 | Engineering-module YAML control surface parsed by nothing (enforcement cosplay) | grumpy | **PLAN** → either a checkpoint ledger or honest reframe as guidance |
| H11 | Zero MCP story; jobs/lessons/state beg to be MCP resources | early-adopter, competitor | **PLAN** → lintel-state MCP server ADR |
| H12 | Prose-only model routing — Haiku-tier work bills flagship; 0 agents declare `model:` | early-adopter | **FIX NOW** (Wave M) — `model:` on mechanical agents |
| H13 | 8-CLI portability is mostly manifests; AGENTS.md commoditized it | early-adopter, competitor | **PLAN** → portability-collapse ADR (AGENTS.md primary) |
| H14 | scaffold commits .claude/memory noise into every feature PR | daily-driver | **FIX NOW** (Wave H) — gitignore churny memory, move 5 root files under .claude/ |
| H15 | SENSE flags ordinary repos (lib/ bin/ hooks/) as meta-infra | daily-driver | **FIX NOW** (Wave H) — require a Lintel-repo marker |
| H16 | Block hooks fail OPEN on input-parse miss (0.2s read, no-jq sed) | security | **FIX NOW** (Wave S) — fail-closed for BLOCK tier |
| H17 | Unsigned pack flips compliance posture / shadows _default / redirects writes | security | **PLAN** → pack-provenance ADR |
| H18 | Plugin auto-exec across every repo on update, no pinning | security | **PLAN** → plugin-pin ADR (document trust model now) |

### JAB — improvable

J1 noob: contradictory hook story ×4 sites · J2 welcome "168 skills" (real 124) · J3 four
state homes, CLAUDE.md points at moved docs/adr · J4 CATALOG is one flat "foundation" bucket,
changelog-speak descriptions · J5 install.sh ghosts (/tier-stamp-agents, entra/, upstream stub)
· J6 cycle dry-run names nonexistent agents + /li:hotfix · J7 plan/review prose claims more
pauses than exist · J8 review vs code-review overlap unreconciled · J9 jsonl vs OTel · J10 no
plan-mode integration. **All FIX NOW (Wave D, docs)** except J9/J10 (PLAN).

## gstack de-heritage (operator-demanded "true refactor")

73 mentions / 38 files, classified: **20 attribution** (rewrite to native rationale),
**17 live couplings** (3 with flagged loss-risk + mitigation), **3 prompt-patterns to reinvent**.
Executed as Waves 1-5 (see worklist below). Never lose functionality: B12 (REVIEW REPORT
heading) dual-accepts during grace; B10 (hook disable-file) migrates; B11 (legacy review log)
imports once. B15 (maintenance marker cleanup) is functionality already lost — the refactor
restores it. gbrain already pruned (ADR-0009); `setup-browser-cookies` gstack ref de-heritaged.

## Execution waves (this cycle)

- **Wave S (security)** — K1-K4, H8, H16: the genuinely dangerous set. ADR-0010.
- **Wave G (gstack)** — Waves 1-2 (attribution + broken-path repairs) now; 3-5 (contract/supply/design) staged with grace windows. ADR-0011.
- **Wave M (model+memory)** — H4, H12: agent `memory:` + `model:` frontmatter. ADR-0012.
- **Wave H (friction)** — K5, K6, H6, H7, H14, H15: the daily-driver KO/HARD set.
- **Wave B (bin)** — H3 + bin smoke test.
- **Wave D (docs)** — all JABs: hook-activation matrix, live counts, GLOSSARY, state-home map, dead-ref sweep, CATALOG categories.
- **Planned (next cycles, ADR each)** — H1/H5 eval-harness · H9 BUILD parallelism · H10 module enforcement · H11 MCP server · H13 portability collapse · H17 pack provenance · H18 plugin pinning · the strategic "shrink-to-kernel + packs-as-product" positioning.

## The strategic verdict (competitor + grumpy, for the operator)

The moat is the pack contract + the accumulated corpus, not the 124 skills. The evidence-backed
direction: **shrink core toward the kernel, make packs the product, AGENTS.md the portability
layer, and build the eval that lets usage — not feel — decide what survives.** This is not a
retreat; it is the planned consolidation the operator's own rule demands. Tracked as the v6
positioning question, opened here, decided after the eval-harness exists.
