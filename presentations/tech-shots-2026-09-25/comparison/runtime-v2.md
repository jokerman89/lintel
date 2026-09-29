# Shared runtime contract

This is protocol v2. It applies equally to naked, serial Lintel and Lintel with swarming.
The 32 product requirements and 100-point rubric in BRIEF.md are unchanged. This file
supersedes only BRIEF.md's server-start and free-technology paragraphs.

## Environment

- Build the client application in `public/`, using vanilla HTML/CSS/JavaScript modules.
- Read initial data from `/fixture.json`. No backend, accounts or external services.
- The controller serves the site at the URL in `BENCHMARK-RUNTIME.json`.
  Do not start another server or modify server/configuration infrastructure.
- No `.env` file is needed. Runtime configuration is public, nonsecret JSON.
- Host permissions are unchanged. No benchmark tool-intercepting hooks are installed.
- Playwright 1.63.0 is a pinned development dependency. `npm ci --offline` uses the
  preflighted package cache. Use explicit `headless: true`, not visible browser tools.
- You may add local tests and the planning/review artifacts your selected workflow
  requires. Do not access previous attempts, other sessions or private grader material.

## Tool transport

Keep each tool request below 4096 UTF-8 bytes of arguments. This is operating guidance,
not a benchmark permission interceptor. Use small patches,
concise path-based handoffs and incremental checks. A larger file can be assembled with
multiple small edits. Do not retry a denied operation through another mechanism. Ordinary host approval
remains in effect. Workspace separation is not an OS sandbox.

## Completion and measurement

All AI planning, implementation and review after the first actual prompt are inside the
build window. The controller reads the actual first matching native user-message
journal timestamp, not a reconstructed or backdated timer.
The nominal window is stated in `BENCHMARK-RUNTIME.json`; a timeout is not completion.
Independent grading runs against a frozen site snapshot, never against later edits.
The controller observes submission and deadline externally; it does not intercept
tools or enforce an operating-system write lock. Stop all writers on submission.

After the complete site and all required reviews are ready, run:

```powershell
node BENCHMARK-SUBMIT.mjs
```

This publishes the one-way ready marker. It does not award points or claim your app is
correct. Do not publish it while workers are still modifying code. Do not edit after
submission; the external grader decides correctness. If something is genuinely blocked,
report that instead. Host faults are retained as infrastructure failures, not disguised
as product scores.
