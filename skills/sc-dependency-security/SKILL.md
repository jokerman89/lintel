---
name: sc-dependency-security
layer: foundation
description: SC sub-skill — SCA + license + vulnerability gates. Dispatches to DependencyAuditor + SBOMAuditor agents.
color: red
tools: Read, Write, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are SC-DEPENDENCY-SECURITY — the workflow that produces a dependency security audit.

## What this skill does

Runs SCA (Software Composition Analysis) via `DependencyAuditor` and generates SBOM via `SBOMAuditor`. Combines results into a report covering CVEs (with severity + exploitability), license compatibility, abandoned/unmaintained dependencies, and supply-chain integrity (signed releases, lockfile integrity).

## When to use

- SC full pass (parallel to other checkpoints — runs anytime)
- Single action `/li:sc single --action dependency-security`
- After dependency update PR
- Pre-release security gate
- Periodic (weekly/monthly) sweep

## When NOT to use

- Single-package upgrade (use package manager directly)
- Runtime dependency monitoring (use runtime observability — `/li:dh` v4.4)

## Workflow

### Step 1 — Detect ecosystem(s)

```bash
ecosystems=()
[ -f package.json ] && ecosystems+=("npm")
[ -f go.mod ] && ecosystems+=("go")
[ -f Cargo.toml ] && ecosystems+=("cargo")
[ -f requirements.txt ] || [ -f pyproject.toml ] && ecosystems+=("python")
[ -f pom.xml ] || [ -f build.gradle ] && ecosystems+=("jvm")
ls *.csproj 2>/dev/null && ecosystems+=("dotnet")
```

### Step 2 — Spawn DependencyAuditor per ecosystem

```bash
for eco in "${ecosystems[@]}"; do
  brief_file=$(mktemp)
  cat > "$brief_file" <<EOF
task: SCA for ${eco} ecosystem — CVEs + license + maintenance state
context_pointers:
  - dependency manifest + lockfile for ${eco}
constraints:
  - per dependency: cves (with cvss + exploitability), license, last-commit, maintained:yes|no|abandoned
  - flag transitive vulnerabilities separately from direct
acceptance:
  - structured per-dependency report
EOF
  /li:brief-forge subagent_spawn sc-dependency-security DependencyAuditor brief "$brief_file"
done
```

### Step 3 — Spawn SBOMAuditor for supply-chain integrity

```bash
sbom_brief=$(mktemp)
cat > "$sbom_brief" <<EOF
task: Generate SBOM + assess supply-chain integrity
context_pointers:
  - dependency manifests across ecosystems: ${ecosystems[@]}
constraints:
  - SBOM format: SPDX or CycloneDX
  - signed-release verification per dependency (when applicable)
  - lockfile integrity (no unpinned versions in deps tree)
acceptance:
  - SBOM file + per-dependency signed/lockfile-pinned verdict
EOF

/li:brief-forge subagent_spawn sc-dependency-security SBOMAuditor brief "$sbom_brief"
```

### Step 4 — Verdict aggregation

```bash
# RED = high-severity exploitable CVE OR license-incompatible
# YELLOW = medium-severity CVE OR abandoned maintainer
# GREEN = no issues
verdict=$(aggregate_dependency_verdict)
```

### Step 5 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".claude/runtime/state/sc/dependency-security-$ts.md"
{
  echo "# Dependency security — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Ecosystems: ${ecosystems[*]}"
  echo "## Verdict: $verdict"
  echo ""
  echo "## CVE findings"
  cat .claude/runtime/state/sc/cve-findings.md
  echo ""
  echo "## License compatibility"
  cat .claude/runtime/state/sc/license-report.md
  echo ""
  echo "## SBOM"
  cat .claude/runtime/state/sc/sbom-summary.md
} > "$out"

printf '{"ts":"%s","kind":"sc_dependency_security","ecosystems":"%s","verdict":"%s","cves_high":%d,"cves_medium":%d,"operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${ecosystems[*]}" "$verdict" "$cves_high" "$cves_medium" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/sc-decisions.jsonl"
```

## Status protocol

- **DONE** — verdict GREEN
- **DONE_WITH_CONCERNS** — verdict YELLOW (operator accepts or schedules remediation)
- **BLOCKED** — verdict RED (must remediate or explicit override)

## Integration

**Reads:** dependency manifests + lockfiles
**Writes:** `.claude/runtime/state/sc/dependency-security-<ts>.md`, SBOM file, audit JSONL
**Dispatches to:** DependencyAuditor (per ecosystem), SBOMAuditor (supply chain)

## Anti-patterns

- **Single ecosystem when repo is polyglot** — scan all
- **CVE list without exploitability assessment** — high-CVSS unexploited is different from medium-CVSS RCE
- **Ignoring transitive vulnerabilities** — most CVEs are transitive
- **License audit only at release** — license incompatibility caught early is cheaper to fix
