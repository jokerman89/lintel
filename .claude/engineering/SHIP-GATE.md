# Ship gate

Use this checklist for a specific release candidate commit. It distinguishes repository
verification from acceptance in an organization's actual Copilot environment. A passing
local suite does not prove a marketplace listing, entitlement, tenant policy, or live agent run.

## 1. Candidate and authorization

Record the candidate commit, intended version, branch and supported Copilot surfaces in the
release evidence. Verify `git status --short` and review every staged file. Never include
operator-local settings, runtime logs, customer data or credentials. Confirm release/tag/push
authority from the current operator request; do not infer permission to deploy from a code merge.

Plugin versions must agree across the manifests, including `.github/plugin/`. A release tag must
point to the reviewed commit on the intended release branch. Do not publish every historical tag.

## 2. Required repository checks

Run from the candidate checkout with Bash, Git, Python 3.9+ and jq available. The full developer
suite needs modern Bash on macOS; the bare installer is separately checked with stock Bash 3.2.

```bash
bash install/verify.sh --all
bash tests/runner/run-all.sh --require-all
python3 bin/li-catalog.py --check
python3 bin/li-instructions.py check
bash bin/li-wiki-gen --check
bash bin/li-copilot check --target .
git diff --check
```

Every command must exit zero. `--require-all` rejects skipped tests or assertions; do not describe
missing dependencies as successful verification. Fix source generators and regenerate their output
when a drift check fails. Counts are discovered by the tools, never manually frozen in this checklist.

CI runs all test tiers on Ubuntu, macOS and Windows, plus shell/Python syntax checks. The macOS job
also runs the installer with `/bin/bash`. The Windows job runs the native installer and reinstalls
into an isolated home, checking runtime resources and preservation of operator state. The portable
end-to-end test installs the runtime and creates/checks a consumer Copilot repository from those
installed files. It does not require a Copilot subscription or make a model request.

## 3. Independent review and release contents

Review the candidate against its spec, then review correctness/security independently. Resolve
blocking findings, or document a deliberate scope reduction and retest the resulting behavior.
Inspect the public README, installation commands, support matrix, change log and upgrade behavior
against generated output and the current implementation.

Check generated custom-agent and instruction files for valid target-specific metadata. Ensure a
Copilot distribution does not register Claude Code hooks. Preserve company-pack customization and
repo-owned instructions during install/update. Exercise fresh install, repeated install, drift and
conflict refusal; the integration suite supplies repeatable local evidence for these cases.

## 4. Copilot acceptance in the intended environment

Record the actual client version and date separately for each surface being advertised:

- **VS Code:** open a fresh consumer repo, enable the intended Copilot agent features, discover
  the generated Lintel agents/instructions and complete a small spec-to-build-card-to-review task.
- **Copilot CLI:** install the explicit Copilot plugin or open the portable consumer repo, confirm
  discovered skills/agents, run a small task and resume it in a new session with preserved evidence.
- **Copilot cloud agent:** use an authorized test repository, verify that the required files and
  policies are available, and review the produced PR and evidence before merge.
- **Enterprise controls:** the organization's owner confirms entitlement, allowlists, data handling,
  extension policy, network policy and required branch checks in that environment.

Mark each result **verified**, **failed**, or **not executed**, with evidence. Local generation,
JSON parsing or CLI plugin discovery are useful checks but do not substitute for a live task.
Unexecuted surfaces must remain qualified in release notes and adopter guidance.

Lintel instructions and evidence are workflow support, not a substitute for GitHub policy, branch
protection or enforcement. Claude Code hook behavior must never be presented as a Copilot control.
Company packs have their own governance and release checks; no voice calibration or regulatory
certification is implied by releasing the neutral harness.

## 5. Publication and closure

After the authorized integration, inspect hosted CI for the exact pushed commit. Record URLs and
conclusions for every required check. A local Windows run cannot establish hosted Linux/macOS
success. Publish a release or marketplace listing only when explicitly authorized, with limitations
and supported-client evidence included. Save final build-card results, remaining acceptance work,
lessons and a cold-start handoff in the committed engineering records.
