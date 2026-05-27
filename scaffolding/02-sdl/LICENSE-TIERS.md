# License Tiers — permissive vs restricted

JStack tier-stamps every bundled or installed agent (and skill where applicable) with a license tier. The tier determines what the operator can do with the content.

## The two tiers

### Permissive

**License families:** MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, MPL-2.0 (file-scope copyleft).

**Operator can:**
- Bundle the content into MS-internal MIT repos
- Copy-paste excerpts into derivative work
- Modify and redistribute under the same or compatible license

**Bundle into MS-internal repos:** YES

**Examples in JStack:**
- All operator-authored JStack content (MIT)
- gstack/ECC/AgentShield/GSD Redux (MIT)
- Anthropic skills with Apache-2.0 (e.g. some `anthropics/skills` items)

### Restricted

**License families:** CC-BY-SA-4.0, GPL-3.0, AGPL-3.0, source-available, no-license, custom non-OSI.

**Operator can:**
- INVOKE the content from its installed location (e.g. via subagent invocation)
- Reference and learn from the content

**Operator CANNOT:**
- Copy-paste content into MS-internal MIT repos
- Bundle into a derivative MIT product
- Distribute modifications under a permissive license (license-incompatible)

**Bundle into MS-internal repos:** NO

**Examples in JStack:**
- Trail of Bits skills (CC-BY-SA-4.0) — invoke yes, copy no
- Trail of Bits claude-code-config (no license declared) — invoke yes, copy no
- Anthropic plugins-official (no license declared) — invoke yes, copy no

## How tier-stamp works

`/agt-tier-stamp` skill scans agents in scope, reads upstream license (or operator-authored MIT default), stamps frontmatter:

```yaml
---
name: SomeAgent
tier: permissive          # or restricted
tier_source: <url>        # upstream URL if applicable
tier_stamped_at: 2026-05-27T18:00:00Z
license_note: <required for restricted>
---
```

For restricted-tier agents, an explicit `license_note` field documents the restrictions.

## How JStack enforces tiers

- **/release-ev2 skill** reads tier-stamp before bundling a release. If any restricted-tier agent in scope: refuses or moves to install-only mode.
- **`OneCSAuditor` agent** flags any unstamped or mismatched agents.
- **CI in scaffold-mvp template** runs `/agt-tier-stamp --strict` on PRs touching agent directories.

## What happens on tier mismatch

If `/release-ev2` is preparing to bundle a release into an MS-internal MIT repo and finds a restricted-tier agent:

1. STOP
2. Surface: "Cannot bundle. restricted-tier agents in scope: <list>"
3. Operator options:
   - Remove the restricted agent from the release
   - Convert it to permissive (only if you authored it OR upstream offers a permissive variant)
   - Distribute as install-only (operator installs from upstream + invokes; no copy-paste)
4. After resolution: rerun `/release-ev2`.

## Why this matters

License-incompatible bundling is a serious issue:
- CC-BY-SA-4.0 contamination forces derivative to be CC-BY-SA — incompatible with MIT
- GPL-3.0 contamination forces derivative to be GPL — incompatible with internal proprietary
- No-license = no permission granted — assume restricted

The tier-stamp model lets the operator USE third-party work that JStack can't BUNDLE, by installing-from-upstream + invoking-as-tool.

## Operator-authored agents

Agents written by the operator (not ported from upstream) default to `permissive` (MIT) for MS-internal scope. Operator can override:

```yaml
tier: restricted
tier_source: operator-authored
license_note: "This agent reuses concept from upstream-X (CC-BY-SA-4.0); flagged restricted out of caution even though the implementation is original."
```

## See also

- `/agt-tier-stamp` skill
- `OneCSAuditor` agent
- `~/.jstack/upstream-sources.yaml` — the 8 SHA-pinned upstreams + their license tiers
- `/release-ev2` skill — refuses restricted-tier bundles into permissive repos
