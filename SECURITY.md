# Security policy

Lintel is a public beta. Its instructions and local utilities run inside the agent environment
you choose, with that environment's permissions. Review both the installed resources and the
client's access policies before adoption.

## Reporting a vulnerability

Report a vulnerability privately through the repository's
[security reporting page](https://github.com/jokerman89/lintel/security/advisories/new).
If private reporting is unavailable, contact the maintainer at
[johannes.akerman@gmail.com](mailto:johannes.akerman@gmail.com) to arrange a private channel.
Do not post a vulnerability, live credential or sensitive customer material in a public issue.

Include the affected Lintel revision, client/version, installation route, impact and a sanitized
reproduction. Use synthetic fixtures. If the finding affects a company pack, follow its owner's
incident-response process as well.

## Supported release line

The current public line is **0.9.0 beta**. Earlier 3.x–5.x version labels describe pre-public
engineering iterations; they are not maintained parallel release lines. Check the
[changelog](CHANGELOG.md) and [releases](https://github.com/jokerman89/lintel/releases) for published
fixes and upgrade notes.

Maintainers handle reports on a best-effort basis, prioritize by impact, and coordinate disclosure
with the reporter. There is no contracted response or remediation SLA. Do not wait for an upstream
fix to revoke an exposed credential or contain an incident in your own environment.

## Reviewable attack surface

| Surface | Why it matters |
|---|---|
| Instructions, skills and agent profiles | Influence which files and tools the agent uses and which actions it proposes |
| Plugin manifests and generated repository kit | Determine which resources the host discovers |
| `hooks/shared/` | Execute shell commands with the host process's privileges when registered |
| `bin/`, `lib/` and skill scripts | Read and write local files and may invoke external tools |
| Installers | Create or update machine-level resources or repository-managed files |
| Packs and optional synchronization | Introduce external context, executable content or configured destinations |

The Copilot repository installer is local and does not fetch dependencies. It preserves unowned
files and refuses conflicting managed-file edits. That behavior does not make an unreviewed
source checkout trustworthy. Pin and review the source, inspect the adoption diff, and run the
installation checks before enabling it for a team.

## Controls and limits

Lintel's Claude Code plugin registers selected hooks. Its secret and customer-data scanners use
patterns over selected Git content when recognized agent tool calls occur. They can miss novel
formats, do not inspect every way of executing Git, and support explicit overrides. They are not
repository-wide data-loss prevention. See [the exact boundary](docs/compliance.md).

**The Copilot kit does not install Lintel hooks.** Copilot has a different hook protocol; Lintel's
Claude Code hook bundle is not a compatible Copilot security gate. Workflow approvals, policy
references and review steps remain cooperative agent instructions on this route.

For mandatory protections, use independently configured repository policies, CI, access controls
and secret scanning. Local audit records are ordinary editable files, not tamper-evident evidence.
A declared pack compliance mode or data-residency field does not configure model hosting,
network isolation or platform authorization.

## Data and external activity

Lintel has no central service collecting session telemetry. The agent client and connected tools
retain their own data-handling behavior. Invoked workflows can browse, download dependencies,
use APIs, synchronize a configured Git repository or push authorized changes. Lintel does not
provide network egress control or guarantee that no data leaves the environment.

Keep credentials in approved secret mechanisms. Do not commit customer data, private policy
corpora or live secrets to this public repository. Sanitize examples, issue reports and lessons.
Review optional exports and private pack distribution separately from the core installation.

## Third-party resources

Lintel's original code is MIT. The bundled design resources retain MIT and Apache-2.0 notices in
[design-dna attribution](skills/design-dna/ATTRIBUTION.md) and its linked license files.
Preserve those notices when redistributing the affected resources. A company pack's own contents
and dependencies need their own review.

## Coordinated disclosure

Agree on publication timing with maintainers while affected users can mitigate the issue.
Researchers may be credited in release notes with their consent. For adoption and operational
ownership, see [enterprise adoption](docs/enterprise-adoption.md).
