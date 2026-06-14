# jokerman-lintel (Lintel) installer - PowerShell (Windows)
#
# Mirrors install.sh behavior for Windows operators. Honors Lintel architecture
# decisions:
# - A1/ADR-0008: this bare installer copies hooks to ~\.lintel\hooks\shared\ INERT
#   (bare install only). A PLUGIN install instead auto-registers them with zero
#   setup via the plugin's hooks/hooks.json. Canonical matrix:
#   docs/getting-started.md#how-hook-activation-works
# - A2: scaffolding lives at ~\.lintel\scaffolding\ (separate from ~\.claude\)
# - A3: layer config at ~\.lintel\config.yaml - per-layer enable
# - ADR-0006: lib/ + bin/ + templates/ are copied to ~\.lintel\ so hooks resolve
#   their helpers when no repo checkout is present
# - ADR-0008: identity (profile.yaml + packs/active-pack) is seeded explicitly
# - A6/C1: skill/agent frontmatter validated at install time
#
# Note: this file stays pure ASCII so Windows PowerShell 5.1 reads it correctly
# regardless of BOM/encoding heuristics.

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$LayerConfigExample = Join-Path $ScriptDir "layer-config.yaml.example"

$LintelHome = if ($env:LINTEL_HOME) { $env:LINTEL_HOME } else { Join-Path $HOME ".lintel" }
$LintelScaffolding = Join-Path $LintelHome "scaffolding"
$LintelHooks = Join-Path $LintelHome "hooks"
$LintelConfig = Join-Path $LintelHome "config.yaml"

function Hdr($t) { Write-Host "`n== $t ==" -ForegroundColor Cyan }
function Ok($t)  { Write-Host "[OK]   $t" -ForegroundColor Green }
function Warn($t){ Write-Host "[WARN] $t" -ForegroundColor Yellow }
function Fail($t){ Write-Host "[FAIL] $t" -ForegroundColor Red }
function Info($t){ Write-Host "       $t" -ForegroundColor Gray }

# Copy the CONTENTS of $src into $dst, replacing $dst first. PowerShell's
# Copy-Item nests a source dir INSIDE an existing same-named target dir on
# re-runs (unlike `cp -r src/* dst/`), so replace-then-copy is the only way to
# mirror install.sh semantics idempotently. Only used for harness-managed trees
# (never operator state); a full ~\.lintel\ backup is taken at install start,
# before any copy runs.
function Copy-TreeContents($src, $dst) {
  if (Test-Path $dst) { Remove-Item -Path $dst -Recurse -Force }
  New-Item -ItemType Directory -Path $dst -Force | Out-Null
  Copy-Item -Path (Join-Path $src "*") -Destination $dst -Recurse -Force
}

Hdr "Lintel installer (Windows)"
Info "Repo: $RepoRoot"
Info "Lintel home: $LintelHome"

# Preflight
try {
  $gitVersion = (& git --version) 2>&1
  Ok "git found ($gitVersion)"
} catch {
  Fail "git not found - install git and re-run"
  exit 1
}

# Backup existing
Hdr "Backing up existing ~\.lintel\ (if any)"
if (Test-Path $LintelHome) {
  $backup = "$LintelHome-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
  Copy-Item -Path $LintelHome -Destination $backup -Recurse -Force
  Ok "Backed up to $backup"
} else {
  Info "No existing ~\.lintel\ - nothing to back up"
}

# Create Lintel home structure
Hdr "Creating ~\.lintel\ structure"
$dirs = @(
  $LintelHome, $LintelScaffolding, $LintelHooks,
  "$LintelHome\audit", "$LintelHome\sessions", "$LintelHome\provenance",
  "$LintelHome\freeze", "$LintelHome\review-log", "$LintelHome\benchmarks",
  "$LintelHome\calibrations", "$LintelHome\browse-runs", "$LintelHome\scrape-runs",
  "$LintelHome\design-runs", "$LintelHome\design-html", "$LintelHome\design-shotgun",
  "$LintelHome\browser-profiles", "$LintelHome\quarantine",
  "$LintelHome\frontend-runs",
  "$LintelHome\brand", "$LintelHome\brand\design-patterns", "$LintelHome\brand\motion-libraries",
  "$LintelHome\brand\shader-snippets", "$LintelHome\brand\palettes", "$LintelHome\brand\fonts"
)
foreach ($d in $dirs) {
  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}
Ok "Lintel home structure created"

# Seed identity (ADR-0008: no silently-unconfigured identity layer).
# Every session before v5.0 ran the _default fallback because profile.yaml and
# packs/active-pack never existed. Seed them explicitly so identity is a stated
# fact, not a fallback. Never overwrite operator files.
# [System.IO.File]::WriteAllText writes UTF-8 without BOM; LF endings are joined
# explicitly so the bash-side pack resolver never sees CRLF.
$profilePath = Join-Path $LintelHome "profile.yaml"
if (-not (Test-Path $profilePath)) {
  $profileLines = @(
    "# Lintel operator profile (seeded by install.ps1 - edit freely)",
    "active_pack: _default",
    "default_mode: internal-tool",
    "role_active: none",
    ""
  )
  [System.IO.File]::WriteAllText($profilePath, ($profileLines -join "`n"))
  Ok "profile.yaml seeded (_default / internal-tool)"
}
$packsDir = Join-Path $LintelHome "packs"
if (-not (Test-Path $packsDir)) { New-Item -ItemType Directory -Path $packsDir | Out-Null }
$activePackPath = Join-Path $packsDir "active-pack"
if (-not (Test-Path $activePackPath)) {
  [System.IO.File]::WriteAllText($activePackPath, "_default")
  Ok "active-pack seeded (_default)"
}

# Copy scaffolding
Hdr "Copying scaffolding to ~\.lintel\scaffolding\"
Copy-TreeContents (Join-Path $RepoRoot "scaffolding") $LintelScaffolding
Ok "Foundation scaffolding copied"

# Shared runtime helpers (lib/ + bin/ + templates/) - the hooks installed under
# ~\.lintel\hooks resolve lib/memory.sh + bin/_jobs.sh here when no repo
# checkout is present (ADR-0006).
foreach ($d in @("lib", "bin", "templates")) {
  $src = Join-Path $RepoRoot $d
  if (Test-Path $src) { Copy-TreeContents $src (Join-Path $LintelHome $d) }
}
Ok "Runtime helpers copied (lib/ + bin/ + templates/)"

# v3.7 brand-seeds (idempotent) - copies canonical design-patterns from seeds/
$seedsBrand = Join-Path $RepoRoot "seeds\brand"
if (Test-Path $seedsBrand) {
  Hdr "Copying brand seeds to ~\.lintel\brand\ (idempotent - operator-extracted patterns preserved)"
  $seedPatterns = Get-ChildItem -Path (Join-Path $seedsBrand "design-patterns") -Directory -ErrorAction SilentlyContinue
  foreach ($sp in $seedPatterns) {
    $target = Join-Path "$LintelHome\brand\design-patterns" $sp.Name
    if (Test-Path $target) {
      Info "Pattern '$($sp.Name)' exists at $target - preserving operator state (idempotent)"
    } else {
      Copy-Item -Path $sp.FullName -Destination $target -Recurse -Force
      Ok "Seeded canonical pattern: $($sp.Name) -> $target"
    }
  }
}

# Config
Hdr "Layer config"
if (Test-Path $LintelConfig) {
  Info "Config exists at $LintelConfig - not overwriting"
} else {
  Copy-Item -Path $LayerConfigExample -Destination $LintelConfig
  Ok "Default config installed to $LintelConfig"
  Info "Edit $LintelConfig to enable/disable layers"
}

# Hooks: copy to ~\.lintel\hooks\shared\ (INERT - bare install only; ADR-0008)
Hdr "Hooks (inert - bare install only; plugin installs auto-register)"
$hookSource = Join-Path $RepoRoot "hooks\shared"
if (Test-Path $hookSource) {
  # shared/ layout (ADR-0008): matches the repo tree, the settings snippet
  # (hooks/claude-code/session-digest.settings.json), li-doctor's drift check,
  # and the scripts' BASH_SOURCE-relative ../_input.sh + ../../../bin lookups.
  $sharedDst = Join-Path $LintelHooks "shared"
  Copy-TreeContents $hookSource $sharedDst
  # Drop any pre-v5 flat copies (hooks\<name>\run.sh directly under hooks\)
  # so the layout is unambiguous
  Get-ChildItem -Path $LintelHooks -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -ne 'shared' -and (Test-Path (Join-Path $_.FullName 'run.sh')) } |
    Remove-Item -Recurse -Force
  Ok "Hooks copied to $sharedDst (Claude Code: auto-registered via the plugin's hooks/hooks.json)"
  Info "Other CLIs / non-plugin installs: register manually - see $sharedDst\README.md"
  # session-digest is REQUIRED (ADR-0002): auto-loads the memory snowball at SessionStart.
  if (Test-Path (Join-Path $sharedDst "session-digest\run.sh")) {
    Info "Non-plugin installs: merge $RepoRoot\hooks\claude-code\session-digest.settings.json"
    Info "into ~\.claude\settings.json. Verify with: li-doctor"
  }
  Info "Note: hook scripts are POSIX shell; they run via Git Bash or WSL"
} else {
  Warn "No hooks source found - skipping"
}

# Frontmatter validation (skills + agents)
Hdr "Frontmatter validation (skills + agents)"
$invalid = 0
$invalidFiles = @()

function Test-Frontmatter($file) {
  $content = Get-Content $file -ErrorAction SilentlyContinue
  if (-not (($content | Select-Object -First 1) -match '^---$')) {
    return @{ ok = $false; reason = "missing frontmatter start" }
  }
  $missing = @()
  foreach ($field in 'name', 'description', 'color', 'tools', 'voice', 'cli_support') {
    if (-not ($content -match "^${field}:")) { $missing += $field }
  }
  if ($missing.Count -gt 0) {
    return @{ ok = $false; reason = "missing fields: $($missing -join ', ')" }
  }
  return @{ ok = $true }
}

# v3: skills at repo root skills/, agents at agents/<category>/
# v2 fallback: scaffolding/*/skills/ and scaffolding/*/agents/ (mirrors install.sh)
$skillFiles = @()
foreach ($root in @((Join-Path $RepoRoot "skills"), (Join-Path $RepoRoot "scaffolding"))) {
  if (Test-Path $root) {
    $skillFiles += Get-ChildItem -Path $root -Recurse -Filter "SKILL.md" -File -ErrorAction SilentlyContinue
  }
}
$agentFiles = @()
foreach ($root in @((Join-Path $RepoRoot "agents"), (Join-Path $RepoRoot "scaffolding"))) {
  if (Test-Path $root) {
    $agentFiles += Get-ChildItem -Path $root -Recurse -Filter "*.md" -File -ErrorAction SilentlyContinue |
      Where-Object {
        $_.Name -ne 'README.md' -and
        ($_.Directory.Name -eq 'agents' -or ($_.Directory.Parent -and $_.Directory.Parent.Name -eq 'agents'))
      }
  }
}
$allFiles = @($skillFiles + $agentFiles | Sort-Object -Property FullName -Unique)

foreach ($f in $allFiles) {
  $result = Test-Frontmatter $f.FullName
  if (-not $result.ok) {
    $invalid++
    $invalidFiles += "$($f.FullName): $($result.reason)"
  }
}

if ($invalid -eq 0) {
  Ok "All skills + agents have valid frontmatter ($($allFiles.Count) files)"
} else {
  Warn "$invalid files have frontmatter issues:"
  foreach ($issue in $invalidFiles) { Info "  - $issue" }
}

# Summary
Hdr "Install complete"
Write-Host "Lintel installed at: $LintelHome"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Review config: notepad $LintelConfig"
Write-Host "  2. Hooks: a plugin install auto-registers them (zero setup);"
Write-Host "     bare installs merge the settings snippet - see $LintelHooks\shared\README.md"
Write-Host "  3. Verify: bash $ScriptDir\verify.sh --all (from WSL or Git Bash)"
Write-Host "  4. Read: type $RepoRoot\LAYERS.md"
Write-Host ""
Write-Host "v5 plugin install (zero-setup path, per CLI):"
Write-Host "  Claude Code:  /plugin marketplace add jokerman89/lintel"
Write-Host "                /plugin install li@jokerman-lintel"
Write-Host "  Codex CLI:    /plugins -> search lintel -> Install"
Write-Host "  Gemini CLI:   gemini extensions install https://github.com/jokerman89/lintel"
Write-Host ""
Write-Host "First commands to try (Git Bash): li-doctor, li-scaffold check"
Write-Host ""

if ($invalid -gt 0) { exit 1 }
exit 0
