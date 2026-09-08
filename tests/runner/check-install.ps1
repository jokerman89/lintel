# Behavioral verification of the native Windows installer, without Pester.
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$TestRoot = Join-Path ([IO.Path]::GetTempPath()) ("lintel-install-" + [guid]::NewGuid().ToString('N'))
$oldLintelHome = $env:LINTEL_HOME
$ShellExe = Join-Path $PSHOME $(if ($PSVersionTable.PSEdition -eq 'Core') { 'pwsh.exe' } else { 'powershell.exe' })

function Assert-Exists($relative) {
  if (-not (Test-Path -LiteralPath (Join-Path $env:LINTEL_HOME $relative))) {
    throw "Installed artifact missing: $relative"
  }
}
function Invoke-Installer {
  & $ShellExe -NoProfile -File (Join-Path $RepoRoot 'install/install.ps1')
  if ($LASTEXITCODE -ne 0) { throw "Installer failed: $LASTEXITCODE" }
}

try {
  New-Item -ItemType Directory -Path $TestRoot | Out-Null
  # An accidental destination equal to the checkout must fail before replacing
  # scaffolding (the previous replace-then-copy path could delete its own source).
  $env:LINTEL_HOME = $RepoRoot
  & $ShellExe -NoProfile -File (Join-Path $RepoRoot 'install/install.ps1') 2>&1 | Out-Null
  if ($LASTEXITCODE -eq 0) { throw 'Installer accepted the source checkout as its destination' }
  if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot 'scaffolding/01-foundation/CORE-PRINCIPLES.md'))) {
    throw 'Rejected self-install altered source scaffolding'
  }
  $env:LINTEL_HOME = Join-Path $TestRoot 'lintel home'
  Invoke-Installer
  foreach ($path in @('scaffolding/01-foundation/.claude/memory/lessons.md',
      'hooks/shared/session-digest/run.sh', 'config.yaml', 'profile.yaml',
      'packs/_default/pack.yaml', 'lib/pack-resolver.sh', 'bin/li-scaffold',
      'bin/li-copilot', 'skills/cycle/SKILL.md', 'shims/copilot/COPILOT.md')) {
    Assert-Exists $path
  }

  $profile = Join-Path $env:LINTEL_HOME 'profile.yaml'
  $customProfile = "active_pack: team`ndefault_mode: hotfix`n"
  [IO.File]::WriteAllText($profile, $customProfile)
  $pack = Join-Path $env:LINTEL_HOME 'packs/_default/pack.yaml'
  $customPack = [IO.File]::ReadAllText($pack) + "`n# local pack customization`n"
  [IO.File]::WriteAllText($pack, $customPack)
  $customHook = Join-Path $env:LINTEL_HOME 'hooks/operator-custom'
  New-Item -ItemType Directory -Path $customHook | Out-Null
  [IO.File]::WriteAllText((Join-Path $customHook 'run.sh'), 'echo operator hook')

  Invoke-Installer
  if ([IO.File]::ReadAllText($profile) -ne $customProfile) { throw 'Reinstall overwrote operator profile' }
  if ([IO.File]::ReadAllText($pack) -ne $customPack) { throw 'Reinstall overwrote operator pack' }
  Assert-Exists 'hooks/operator-custom/run.sh'
  Assert-Exists 'scaffolding/01-foundation/.claude/memory/lessons.md'
  if (Test-Path -LiteralPath (Join-Path $env:LINTEL_HOME 'scaffolding/scaffolding')) {
    throw 'Reinstall nested scaffolding instead of replacing its contents'
  }
  $linkedHome = Join-Path $TestRoot 'linked-home'
  New-Item -ItemType Directory -Path $linkedHome | Out-Null
  $outsideProfile = Join-Path $TestRoot 'outside-profile.yaml'
  New-Item -ItemType SymbolicLink -Path (Join-Path $linkedHome 'profile.yaml') -Target $outsideProfile | Out-Null
  $env:LINTEL_HOME = $linkedHome
  & $ShellExe -NoProfile -File (Join-Path $RepoRoot 'install/install.ps1') 2>&1 | Out-Null
  if ($LASTEXITCODE -eq 0) { throw 'Installer accepted a dangling profile symlink' }
  if (Test-Path -LiteralPath $outsideProfile) { throw 'Installer seeded outside its home through a symlink' }
  if (Test-Path -LiteralPath (Join-Path $linkedHome 'scaffolding')) { throw 'Linked install wrote before refusal' }
  Write-Host 'PASS: PowerShell install/reinstall preserves operator state, includes Copilot assets and rejects linked homes.'
} finally {
  $env:LINTEL_HOME = $oldLintelHome
  if (Test-Path -LiteralPath $TestRoot) {
    $resolved = (Resolve-Path -LiteralPath $TestRoot).Path
    $expected = [IO.Path]::GetFullPath($TestRoot)
    if ($resolved -ne $expected -or -not (Split-Path -Leaf $resolved).StartsWith('lintel-install-')) {
      throw "Refusing cleanup of unexpected path: $resolved"
    }
    Remove-Item -LiteralPath $resolved -Recurse -Force
  }
}
# The final subprocess deliberately failed (negative case). Clear its status so
# GitHub Actions does not treat the expected refusal as the script's verdict.
exit 0
