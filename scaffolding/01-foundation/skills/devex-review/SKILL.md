---
name: jstack-devex-review
description: Review the built developer experience — scripts, onboarding, error messages, time-to-hello-world.
color: yellow
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /devex-review

The DX critique for what's actually built (scripts, CLIs, error messages, README, onboarding flow). Distinct from `/plan-devex-review` which reviews a design doc's *plan* for DX. This one runs the developer journey and scores the friction.

Six dimensions: time-to-hello-world, error message quality, script ergonomics, doc accuracy, test loop speed, recovery from broken state.

## When to use

- Pre-1.0 ship of a CLI or framework
- Onboarding a new team member; want to identify friction points proactively
- After significant DX changes (new scripts, CI rework, doc reorg)
- A teammate complained about "slow tests" or "confusing setup" — instrument the complaint

## When NOT to use

- Pure UI work — use `/design-review`
- Plan-stage DX review before code exists — use `/plan-devex-review`
- Reviewing a third-party tool's DX — out of scope (we don't fix what we don't own)

## Inputs

- Optional `--scope <area>` — narrow to a sub-area (e.g. just the test loop, just CLI ergonomics)
- Optional `--fresh-clone` — perform the review starting from a fresh clone in a temp dir (most accurate but slowest)
- Optional `--baseline <ref>` — compare DX metrics against an earlier commit
- Optional `--time-budget <minutes>` — cap the review (default: 15min — beyond that, escalate to a multi-session manual review)

## Workflow

1. **Locate the developer journey.** Read README, CONTRIBUTING, package.json scripts, makefile, justfile, setup script. Identify the documented "first 10 minutes" path.
2. **Time-to-hello-world.** Execute the documented setup steps (in `--fresh-clone` mode if requested). Time each step. Note any step that requires undocumented action.
3. **Six-dimension pass:**
   - **TTHW (time-to-hello-world):** minutes from `git clone` to "running locally with expected behavior".
   - **Error messages:** intentionally trigger 3-5 common errors (missing dep, wrong node version, missing env var). Score message clarity 1-10.
   - **Script ergonomics:** all package.json/justfile scripts: are names predictable? Do they composite well? Any hidden globals required?
   - **Doc accuracy:** does the README's stated setup actually work? Are any commands stale, removed, or renamed?
   - **Test loop speed:** single-file test, full suite. Score on perceived feedback latency for a TDD-style cycle.
   - **Recovery:** intentionally break state (delete node_modules, corrupt a lockfile). Does the project guide you back, or fail mysteriously?
4. **Score + findings.** Each dimension gets 1-10 + a P1/P2/P3 finding list.
5. **Persist via gstack-review-log** with `skill: devex-review`.
6. **Report.**

## Report format

```
DevEx Review: <repo>

Scope: full journey
Mode: in-place (no fresh clone)
Time spent: 12 min / 15 budget

## Dimension scores

| Dimension          | Score |
|--------------------|-------|
| TTHW               | 6/10  |
| Error messages     | 5/10  |
| Script ergonomics  | 8/10  |
| Doc accuracy       | 9/10  |
| Test loop speed    | 4/10  |
| Recovery           | 7/10  |
Overall: 6.5/10

## Findings (5)

[P1] Test loop speed
   Full suite: 4m 17s. Single-file watch mode: 11s to first feedback.
   Bottleneck: TypeScript project references rebuild on every test invocation.
   Recommendation: enable `tsc --build --watch` separately, OR vitest-native ts handling.

[P2] Error messages — missing LOVABLE_API_KEY
   App crashes with "TypeError: Cannot read properties of undefined". No mention of env var.
   Fix: validate env at boot, exit with named message "Missing required env var: LOVABLE_API_KEY".

[P2] TTHW — undocumented Supabase CLI requirement
   README says `npm install && npm dev`. Actually requires `supabase` CLI installed globally first.
   Fix: add preflight check OR document.

[P3] Recovery — deleted node_modules
   `npm install` recovers correctly. ✓
   But: deleted `.next` cache results in obscure webpack error. Document or auto-clean.

[P3] Script ergonomics — `npm run dev:full`
   Composite name, no documentation. What does ":full" add over `npm run dev`?
   Fix: rename or document.

## Recommendation
P1 test-loop fix has highest impact (4 min × N runs/day per developer). Address before next sprint.
```

## Compliance integration

- Review may run actual setup scripts in `--fresh-clone` mode — those scripts touch the filesystem in a sandboxed dir. No production mutation.
- If setup script calls a network resource: Layer 2 reads-from-internet is fine; writes (e.g. token register) would gate.
- Recovery dimension intentionally breaks state — only in `--fresh-clone` mode. Refuses to break state in the operator's working tree.

## Voice tier note

`voice: internal`. DX critique is engineering-internal.

## Failure modes

- **Fresh-clone mode but no clean clone target:** create `~/.jstack/devex-runs/<ts>/` clone dir. If permissions fail: report + fall back to in-place review with warning.
- **Setup script hangs:** time-budget enforces termination. Report which step hung.
- **Test suite takes longer than time-budget:** measure first-N tests as a sample, extrapolate, flag as estimated.
- **No documented setup steps found:** that IS the finding. Report TTHW = "undefined" + P1 doc gap.

## Examples

**Quick in-place pass:**
```
> /devex-review --scope test-loop
[Times single-file watch + full suite]
Dimension: test loop speed 4/10. P1 finding: ts-build bottleneck.
```

**Full fresh-clone audit:**
```
> /devex-review --fresh-clone --time-budget 30
[Clones into ~/.jstack/devex-runs/, runs full journey]
6 dimensions scored. 5 findings (1 P1, 2 P2, 2 P3). Overall 6.5/10.
```

**Baseline diff:**
```
> /devex-review --baseline main@v1.0.0
[Compares current vs v1.0.0]
TTHW improved 8m → 5m. Error messages improved 4/10 → 7/10. Test loop regressed 6 → 4 (P1).
```

## See also

- `/plan-devex-review` — plan-stage equivalent
- `/design-review` — UI critique (sister skill)
- `/review` — diff-scoped code review (DX is broader than diff)
- `/ship` — reads devex-review log as advisory signal (not blocking)
