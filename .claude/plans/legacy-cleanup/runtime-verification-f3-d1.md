# Runtime verification of f3a24d52 and d1f2f758 (targeted, read-only)

Verifier: coordinator88 (session 88aecc43-40f9-41d4-8947-6c2fb0a55481), for integration
e9c20b62 and parent f4584b03. Runtime evidence only; not review clearance.

## Subjects

- f3a24d52aa1343bd2fb0e3c3301df77366a99e1c, tree 75f281b968ef8b98b9e2fea52cad0f197dd66bb5
- d1f2f75831fa23ed85f79e0a21f7a67451ea1c7e, tree 965a54b0ef879dd1117d87bb97f60b7293aa8db7;
  sole parent f3a24d52; changes only skills/code-freeze/SKILL.md and
  tests/integration/observation-learning.py

Checkouts: clean detached `git worktree add --detach` under %LOCALAPPDATA%\Temp
(c104v, c104x) on Windows; WSL clones of `git bundle` HEAD (~/ci93/v5, ~/ci93/v6).
No source edits, installs, private environment, credentials, profile borrowing or
denied launchers.

## Hosts

- W: Windows, Python 3.11.9, Git Bash, pwsh 7.6.6; launcher run-suite-clean.py with
  per-entry synthetic HOME/USERPROFILE/APPDATA/LOCALAPPDATA/TEMP and no LINTEL_* except
  the PowerShell 7 selector.
- L: WSL Ubuntu-24.04, Python 3.12.3, PyYAML 6.0.1, synthetic HOME/TEMP, python shim;
  no pwsh, no node.

## Results on f3a24d52

| Target | W | L |
|---|---|---|
| observation-learning.sh FailurePropagationTests.test_unwritable_resolved_audit_directory + ObservationPreservation.test_freeze_records_are_advisory_and_repository_state_wins_over_legacy | exit 1, Ran 2, FAILED (failures=1), 110 s | exit 1, Ran 2, FAILED (failures=1), 11 s |
| catalog-installed.sh InstalledDiscovery.test_all_methods_aliases_and_worked_examples_survive_installation + InstalledDiscovery.test_optional_family_closure | exit 0, Ran 2, OK, 834 s | exit 0, 94 s |
| copilot-kit.py CopilotKit.test_optional_family_closures_survive_portable_clone (run directly with LINTEL_TEST_BASH, as copilot-kit.sh does; the entry forwards no selectors) | exit 0, Ran 1, OK, 484 s | exit 0, 38 s |
| universal-lifecycle.sh MigrationInventory | exit 0, Ran 15, OK, 304 s | exit 0, 63 s |
| check-install.ps1 -SnapshotOnly | exit 0, 4 s | NOTRUN (no pwsh) |
| check-install.ps1 -PruningOnly -PruningPerformer powershell | exit 0, 20 s | NOTRUN (no pwsh) |
| check-install.ps1 -PruningOnly -PruningPerformer bash | exit 0, 197 s | NOTRUN (no pwsh) |

The observation-learning failure on both hosts: test_unwritable_resolved_audit_directory
passes (variants explicit and v5); test_freeze_records_are_advisory_and_repository_state_wins_over_legacy
fails at tests/integration/observation-learning.py:247 (`'no universal automatic freeze
consumer' not found` in skills/code-freeze/SKILL.md). The phrase is present at 77cb8d3f and
absent at a7a1df33 and f3a24d52 (rewritten in 2f158a0c); :248 would next have split on a
missing `## Failure modes` section.

## Results on d1f2f758

| Target | W | L |
|---|---|---|
| observation-learning.sh, the same two selectors | exit 0, Ran 2, OK, 86 s | exit 0, Ran 2, OK, 22 s |

The f3a24d52 failure is kept as a separate observation; nothing was rerun over it.

## Limits

- Windows used Python 3.11.9, not CI's 3.12; WSL used PyYAML 6.0.1, not 6.0.3.
- Only the targeted selectors ran; no full or strict suite.
- check-install.ps1 is unverified on POSIX.

## Evidence files (SHA-256, bytes)

- `be1811695b64b79b659489125c6e766563a613ec078b4dcb059e57a9a4299ae2` 6011 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\verification\rv104w\00-tests__integration__observation-learning.sh.log`
- `95172e6989b9dcc9da111904a9fe93e43f9e3dc91a2ff5c0c0fa5bdcd92cbd94` 461 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\verification\rv104w\01-tests__integration__catalog-installed.sh.log`
- `127ffb9bdf7481b6c0a05420adeca685f278327544acefc8f3a0295777d3b78c` 240 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\verification\rv104w\02--c.log`
- `0dee89e9bda30391b54ee3207d01c0b36ae6703e9c380ef367b8ea8bb452ce59` 22864001 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\verification\rv104w\03-tests__integration__universal-lifecycle.sh.log`
- `77ca17ba337345f445f08a39f1e49fe2b447a82b1ef8e384ccc3d802ccfaafe0` 113 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\verification\rv104w\04--c.log`
- `776c2c0afe736be33351142dfe86f90d8163e6993b0b72ce803e915a3ff6ba8d` 222 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\verification\rv104w\05--c.log`
- `f7a6a5ca4151d1dc0d1be5c2170da526e039ad6e1f78cc5fffca129a93ea253a` 216 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\verification\rv104w\06--c.log`
- `29d59cde5a7441842c9a7be7237dabe53a3e5c61d1af930da788a5e6638b6962` 3945 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\verification\rv104w\preflight.json`
- `5afb50c557cfb634c92c368b026746e5f6833314c2ced3b98517cc6fb266d7c2` 2169 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\verification\rv104w\results.json`
- `bc69fe1d87ac615bef1f7e0b310f3a709f771e4eafbdd19d4be5787feb653bc6` 106 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\verification\rv104b\00-tests__integration__observation-learning.sh.log`
- `3978a50ab3571df139ea1c7e37e41d4a2a37c7b43d303df68400b5b241758d82` 3032 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\verification\rv104b\preflight.json`
- `adbcaf4aaaacc29eee826eda861f49bcb87651e219d420d269c56ef4f1b75f8e` 444 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\verification\rv104b\results.json`
- `59ee25fabf39f8b81e5c8991c8c3939c221006de1bc3fa45003dfbc5031b4bdb` 5968 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\ci104\wsl\rv104\00-observation-learning.sh.log`
- `c3a58f065ab3ca748fbab1647283fc6b7b65fac6f391b0d7efc9f0e877951a4b` 213 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\ci104\wsl\rv104\00-observation-learning.sh.rc`
- `838558d6d0c1e2068c3275a8d2f56955ee694e48204af7abd05f7cde25cab78e` 422 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\ci104\wsl\rv104\01-catalog-installed.sh.log`
- `5f3d83f8a9a8268df2ed40a1d0676702c6bc6be7f0c187e0b0747cfe8d87c8a7` 183 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\ci104\wsl\rv104\01-catalog-installed.sh.rc`
- `3fd501fef7a0a0a24ee50061f36a31137790d6a15c6ffc7bd7033475d30de32e` 233 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\ci104\wsl\rv104\02-copilot-kit.py.log`
- `74495198164724eb358e0349e4d802e5b3331eddb967135458b24d98951f8b4b` 146 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\ci104\wsl\rv104\02-copilot-kit.py.rc`
- `b574efa83756ccbbd76331fc825b4d66d6ee757e14c7db0f441d414708ca8803` 20902061 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\ci104\wsl\rv104\03-universal-lifecycle.sh.log`
- `36eaf8c27d7919166a0f8e938ada04069e81911cacfe050307a0928870374dbe` 71 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\ci104\wsl\rv104\03-universal-lifecycle.sh.rc`
- `16a82e265660099dcb4dbebd8c12ceb77e2046822292ca00dad1a6bc84f9f0a1` 101 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\ci104\wsl\rv104b\00-observation-learning.sh.log`
- `3989248f87018c6d51ebda83bf878895983f41cd0a402b0eddb069affdc8eb52` 213 `C:\Users\jokerman\.copilot\session-state\88aecc43-40f9-41d4-8947-6c2fb0a55481\files\ci104\wsl\rv104b\00-observation-learning.sh.rc`
