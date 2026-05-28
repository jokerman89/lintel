# jokerman-lintel (Lintel) installer — PowerShell (Windows)
#
# Honors Lintel architecture decisions A1, A2, A3, A6, C1.
# Mirrors install.sh behavior for Windows operators.

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SourcesFile = Join-Path $ScriptDir "upstream-sources.yaml"
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
  "$LintelHome\freeze", "$LintelHome\rai", "$LintelHome\dpia", "$LintelHome\dsb",
  "$LintelHome\entra", "$LintelHome\review-log", "$LintelHome\benchmarks",
  "$LintelHome\calibrations", "$LintelHome\browse-runs", "$LintelHome\scrape-runs",
  "$LintelHome\design-runs", "$LintelHome\design-html", "$LintelHome\design-shotgun",
  "$LintelHome\browser-profiles", "$LintelHome\quarantine"
)
foreach ($d in $dirs) {
  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}
Ok "Lintel home structure created"

# Copy scaffolding
Hdr "Copying scaffolding to ~\.lintel\scaffolding\"
Copy-Item -Path (Join-Path $RepoRoot "scaffolding\*") -Destination $LintelScaffolding -Recurse -Force
Ok "Scaffolding copied (4 layers)"

# Config
Hdr "Layer config"
if (Test-Path $LintelConfig) {
  Info "Config exists at $LintelConfig - not overwriting"
} else {
  Copy-Item -Path $LayerConfigExample -Destination $LintelConfig
  Ok "Default config installed to $LintelConfig"
  Info "Edit $LintelConfig to enable/disable layers"
}

# Hooks (inert)
Hdr "Hooks (inert install - opt-in symlink to activate)"
$hookSource = Join-Path $RepoRoot "scaffolding\02-compliance\hooks"
if (Test-Path $hookSource) {
  Copy-Item -Path "$hookSource\*" -Destination $LintelHooks -Recurse -Force
  Ok "Hooks copied to $LintelHooks (INERT - symlink to activate)"
  Info "Windows symlink: New-Item -ItemType SymbolicLink -Path ~\.claude\hooks\<name>.sh -Target $LintelHooks\<name>\run.sh"
  Info "Note: hook scripts are POSIX shell; activate from WSL or Git Bash"
}

# Frontmatter validation
Hdr "Frontmatter validation (skills + agents)"
$invalid = 0
$invalidFiles = @()

function Test-Frontmatter($file) {
  $content = Get-Content $file -TotalCount 50 -ErrorAction SilentlyContinue
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

$skillFiles = Get-ChildItem -Path (Join-Path $RepoRoot "scaffolding") -Recurse -Filter "SKILL.md" -ErrorAction SilentlyContinue
$agentFiles = Get-ChildItem -Path (Join-Path $RepoRoot "scaffolding") -Recurse -Filter "*.md" -ErrorAction SilentlyContinue | Where-Object { $_.Directory.Name -eq 'agents' -and $_.Name -ne 'README.md' }

foreach ($f in $skillFiles + $agentFiles) {
  $result = Test-Frontmatter $f.FullName
  if (-not $result.ok) {
    $invalid++
    $invalidFiles += "$($f.FullName): $($result.reason)"
  }
}

if ($invalid -eq 0) {
  Ok "All skills + agents have valid frontmatter ($($skillFiles.Count + $agentFiles.Count) files)"
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
Write-Host "  2. Activate hooks: see $LintelHooks\README.md"
Write-Host "  3. Verify: bash $ScriptDir\verify.sh --all (from WSL or Git Bash)"
Write-Host "  4. Read: type $RepoRoot\LAYERS.md"
Write-Host ""

if ($invalid -gt 0) { exit 1 }
exit 0
