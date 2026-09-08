<!-- Thanks for contributing to Lintel. Keep PRs atomic — one logical change. See CONTRIBUTING.md. -->

## Summary

<!-- What does this change and why? Link any issue: Closes #NNN -->

## Type of change

- [ ] Bug fix (a skill/hook/agent/lib that didn't work as intended)
- [ ] New skill / agent / hook
- [ ] Docs / scaffolding / templates
- [ ] Refactor / subtraction (no behavior change)
- [ ] Meta-infra (touches `skills/`, `agents/`, `hooks/`, `lib/`, `bin/_*.sh`, `packs/`, core templates)

## Verification

- [ ] `bash tests/runner/run-all.sh --require-all` is green on the committed tree
- [ ] For meta-infra: shape tests pass and `bin/li-compat-audit` is not RED
- [ ] Frontmatter contracts intact (skills: `layer` + `cli_support`; agents: `category` + `tier` + `cli_support`)

- [ ] Generated catalog, documentation and startup instructions are current
- [ ] Copilot changes: adapter init/check and consumer-clone tests pass; live-client evidence is stated separately

## Decisions & compatibility

- [ ] Non-trivial decision recorded as an ADR in `.claude/decisions/NNNN-*.md`
- [ ] Structural change to the harness recorded in `.claude/engineering/evolution/`
- [ ] Breaking change? If yes, describe the migration path below

## Notes

<!-- Anything reviewers should know: trade-offs, follow-ups, deliberate deferrals. -->
