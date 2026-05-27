# jokerman-session-setup (JStack) installer — PowerShell (Windows)
#
# Honors JStack architecture decisions A1, A2, A3, A6, C1.
# Mirrors install.sh behavior for Windows operators.

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SourcesFile = Join-Path $ScriptDir "upstream-sources.yaml"
$LayerConfigExample = Join-Path $ScriptDir "layer-config.yaml.example"

$JStackHome = if ($env:JSTACK_HOME) { $env:JSTACK_HOME } else { Join-Path $HOME ".jstack" }
$JStackScaffolding = Join-Path $JStackHome "scaffolding"
$JStackHooks = Join-Path $JStackHome "hooks"
$JStackConfig = Join-Path $JStackHome "config.yaml"

function Hdr($t) { Write-Host "`n== $t ==" -ForegroundColor Cyan }
function Ok($t)  { Write-Host "[OK]   $t" -ForegroundColor Green }
function Warn($t){ Write-Host "[WARN] $t" -ForegroundColor Yellow }
function Fail($t){ Write-Host "[FAIL] $t" -ForegroundColor Red }
function Info($t){ Write-Host "       $t" -ForegroundColor Gray }

Hdr "JStack installer (Windows)"
Info "Repo: $RepoRoot"
Info "JStack home: $JStackHome"

# Preflight
try {
  $gitVersion = (& git --version) 2>&1
  Ok "git found ($gitVersion)"
} catch {
  Fail "git not found - install git and re-run"
  exit 1
}

# Backup existing
Hdr "Backing up existing ~\.jstack\ (if any)"
if (Test-Path $JStackHome) {
  $backup = "$JStackHome-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
  Copy-Item -Path $JStackHome -Destination $backup -Recurse -Force
  Ok "Backed up to $backup"
} else {
  Info "No existing ~\.jstack\ - nothing to back up"
}

# Create JStack home structure
Hdr "Creating ~\.jstack\ structure"
$dirs = @(
  $JStackHome, $JStackScaffolding, $JStackHooks,
  "$JStackHome\audit", "$JStackHome\sessions", "$JStackHome\provenance",
  "$JStackHome\freeze", "$JStackHome\rai", "$JStackHome\dpia", "$JStackHome\dsb",
  "$JStackHome\entra", "$JStackHome\review-log", "$JStackHome\benchmarks",
  "$JStackHome\calibrations", "$JStackHome\browse-runs", "$JStackHome\scrape-runs",
  "$JStackHome\design-runs", "$JStackHome\design-html", "$JStackHome\design-shotgun",
  "$JStackHome\browser-profiles", "$JStackHome\quarantine"
)
foreach ($d in $dirs) {
  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}
Ok "JStack home structure created"

# Copy scaffolding
Hdr "Copying scaffolding to ~\.jstack\scaffolding\"
Copy-Item -Path (Join-Path $RepoRoot "scaffolding\*") -Destination $JStackScaffolding -Recurse -Force
Ok "Scaffolding copied (4 layers)"

# Config
Hdr "Layer config"
if (Test-Path $JStackConfig) {
  Info "Config exists at $JStackConfig - not overwriting"
} else {
  Copy-Item -Path $LayerConfigExample -Destination $JStackConfig
  Ok "Default config installed to $JStackConfig"
  Info "Edit $JStackConfig to enable/disable layers"
}

# Hooks (inert)
Hdr "Hooks (inert install - opt-in symlink to activate)"
$hookSource = Join-Path $RepoRoot "scaffolding\02-compliance\hooks"
if (Test-Path $hookSource) {
  Copy-Item -Path "$hookSource\*" -Destination $JStackHooks -Recurse -Force
  Ok "Hooks copied to $JStackHooks (INERT - symlink to activate)"
  Info "Windows symlink: New-Item -ItemType SymbolicLink -Path ~\.claude\hooks\<name>.sh -Target $JStackHooks\<name>\run.sh"
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
Write-Host "JStack installed at: $JStackHome"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Review config: notepad $JStackConfig"
Write-Host "  2. Activate hooks: see $JStackHooks\README.md"
Write-Host "  3. Verify: bash $ScriptDir\verify.sh --all (from WSL or Git Bash)"
Write-Host "  4. Read: type $RepoRoot\LAYERS.md"
Write-Host ""

if ($invalid -gt 0) { exit 1 }
exit 0
