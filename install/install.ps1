#requires -Version 7.0
<#
.SYNOPSIS
  jokerman-session-setup installer (PowerShell 7+ / Windows).

.DESCRIPTION
  Reads upstream-sources.yaml and installs each source from its upstream repo.
  Does NOT bundle any external code — every source is cloned from its public origin
  at install time.

  Requires:
    - PowerShell 7+
    - git on PATH
    - powershell-yaml module (auto-installed for current user if missing)
#>

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot    = Split-Path -Parent $ScriptDir
$SourcesFile = Join-Path $ScriptDir 'upstream-sources.yaml'

# ----- helpers ---------------------------------------------------------------

function Write-Section($text)  { Write-Host "`n== $text ==" -ForegroundColor White }
function Write-Ok($text)       { Write-Host "✓ $text" -ForegroundColor Green }
function Write-Warn2($text)    { Write-Host "⚠ $text" -ForegroundColor Yellow }
function Write-Fail($text)     { Write-Host "✗ $text" -ForegroundColor Red }
function Write-Info($text)     { Write-Host "· $text" -ForegroundColor Cyan }
function Write-Dim($text)      { Write-Host "  $text" -ForegroundColor DarkGray }

function Expand-HomePath($path) {
  if ($path -like '~*') {
    return (Join-Path $HOME ($path.Substring(1).TrimStart('/','\')))
  }
  return $path
}

# ----- pre-flight ------------------------------------------------------------

Write-Section 'jokerman-session-setup installer (PowerShell)'
Write-Dim "Sources file: $SourcesFile"

# git
try {
  $gitVersion = (& git --version) 2>&1
  Write-Ok "git found ($gitVersion)"
} catch {
  Write-Fail 'git not found — install git and re-run (https://git-scm.com/download/win)'
  exit 1
}

# powershell-yaml
if (-not (Get-Module -ListAvailable -Name 'powershell-yaml')) {
  Write-Info 'powershell-yaml module not found — installing for current user'
  try {
    Install-Module -Name 'powershell-yaml' -Scope CurrentUser -Force -AllowClobber -ErrorAction Stop
    Write-Ok 'powershell-yaml installed'
  } catch {
    Write-Fail "Failed to install powershell-yaml: $_"
    Write-Dim 'Try manually: Install-Module powershell-yaml -Scope CurrentUser'
    exit 1
  }
}
Import-Module 'powershell-yaml' -ErrorAction Stop
Write-Ok 'powershell-yaml ready'

if (-not (Test-Path $SourcesFile)) {
  Write-Fail "Sources file missing: $SourcesFile"
  exit 1
}
Write-Ok 'Sources file found'

# ----- backup ~/.claude/ -----------------------------------------------------

Write-Section 'Backing up existing ~/.claude/ (if any)'

$ClaudeDir = Join-Path $HOME '.claude'
if (Test-Path $ClaudeDir) {
  $stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
  $backup = Join-Path $HOME ".claude-backup-$stamp"
  Copy-Item -Path $ClaudeDir -Destination $backup -Recurse -Force
  Write-Ok "Backed up to $backup"
} else {
  Write-Info "No existing ~/.claude/ — nothing to back up"
}

# ----- copy scaffolding ------------------------------------------------------

Write-Section 'Installing scaffolding'

$ScaffoldingDest = Join-Path $HOME '.claude-scaffolding'
New-Item -ItemType Directory -Force -Path $ScaffoldingDest | Out-Null
Copy-Item -Path (Join-Path $RepoRoot 'scaffolding/*') -Destination $ScaffoldingDest -Recurse -Force
Write-Ok "Scaffolding copied to $ScaffoldingDest"

# Canonical AGENT-INSTRUCTIONS.md — copy (Windows symlinks need admin or dev mode)
Copy-Item -Path (Join-Path $RepoRoot 'AGENT-INSTRUCTIONS.md') `
          -Destination (Join-Path $ScaffoldingDest 'AGENT-INSTRUCTIONS.md') -Force
Write-Ok "AGENT-INSTRUCTIONS.md available at $ScaffoldingDest"

# ----- install upstream sources ---------------------------------------------

Write-Section 'Installing upstream sources'

$yaml    = Get-Content $SourcesFile -Raw | ConvertFrom-Yaml
$sources = $yaml.sources

$installed = 0
$skipped   = 0
$warned    = 0

foreach ($name in $sources.Keys) {
  $s            = $sources[$name]
  $repo         = $s.repo
  $installPath  = Expand-HomePath $s.install_path
  $installType  = $s.install_type
  $license      = $s.license
  $tier         = $s.tier
  $description  = $s.description

  Write-Host ''
  Write-Host "$name " -ForegroundColor White -NoNewline
  Write-Host "($license, $tier)" -ForegroundColor DarkGray
  Write-Dim $description
  Write-Dim "→ $installPath"

  if ($installType -eq 'reference-only') {
    Write-Info 'Reference-only (see docs/promoted-agents.md). Not cloning.'
    $skipped++
    continue
  }

  if (Test-Path (Join-Path $installPath '.git')) {
    Write-Info 'Already cloned — pulling latest'
    Push-Location $installPath
    try {
      & git pull --ff-only --quiet 2>&1 | Out-Null
      if ($LASTEXITCODE -eq 0) {
        Write-Ok "Updated $name"
        $installed++
      } else {
        Write-Warn2 "git pull failed for $name — leaving as is"
        $warned++
      }
    } finally { Pop-Location }
    continue
  }

  # Fresh clone
  $parent = Split-Path -Parent $installPath
  if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }

  & git clone --depth 1 $repo $installPath 2>&1 | Out-Null
  if (-not (Test-Path (Join-Path $installPath '.git'))) {
    Write-Fail "Clone failed for $name (from $repo)"
    $warned++
    continue
  }

  if ($installType -eq 'git-clone-and-setup' -and $s.post_install) {
    $postInstall = $s.post_install
    Write-Info "Running post-install: $postInstall"
    Push-Location $installPath
    try {
      # post_install is typically a shell command. On Windows we run via bash if available
      # (Git for Windows ships with bash). Fallback: try direct invoke.
      if (Get-Command bash -ErrorAction SilentlyContinue) {
        & bash -c "$postInstall" 2>&1 | Out-Null
      } else {
        Invoke-Expression $postInstall 2>&1 | Out-Null
      }
      if ($LASTEXITCODE -eq 0) {
        Write-Ok 'Post-install complete'
      } else {
        Write-Warn2 "Post-install failed for $name — clone is in place but setup incomplete"
        $warned++
      }
    } finally { Pop-Location }
  }

  if ($tier -eq 'restricted' -and $s.license_note) {
    $note = ($s.license_note -replace '\s+', ' ').Trim()
    Write-Warn2 "License note: $note"
  }

  Write-Ok "Installed $name"
  $installed++
}

# ----- summary --------------------------------------------------------------

Write-Section 'Summary'

Write-Host "  Installed/updated: " -NoNewline; Write-Host $installed -ForegroundColor Green
Write-Host "  Skipped (reference-only): " -NoNewline; Write-Host $skipped -ForegroundColor DarkGray
Write-Host "  Warnings: " -NoNewline; Write-Host $warned -ForegroundColor Yellow
Write-Host ''
Write-Host 'Next steps:'
Write-Host '  1. Run verify.sh (or verify.ps1 once added)'
Write-Host "       bash $ScriptDir\verify.sh"
Write-Host '  2. Per-CLI shim setup — see docs/getting-started.md'
Write-Host "       Claude Code: scaffolding at $ScaffoldingDest"
Write-Host '       Copilot:     copy shims/copilot-instructions.md to .github/copilot-instructions.md in each repo'
Write-Host '       Codex:       copy shims/AGENTS.md to AGENTS.md in each repo'
Write-Host ''
Write-Ok 'Install complete.'
