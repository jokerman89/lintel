# Behavioral verification of the native Windows installer, without Pester.
param(
    [switch]$PruningOnly,
    [ValidateSet('powershell', 'bash')][string]$PruningPerformer = 'powershell'
)
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

function Write-FixtureFile([string]$Root, [string]$Relative, [string]$Text) {
  $path = Join-Path $Root $Relative
  [IO.Directory]::CreateDirectory((Split-Path -Parent $path)) | Out-Null
  [IO.File]::WriteAllText($path, $Text, (New-Object Text.UTF8Encoding($false)))
}

function Get-FixtureSnapshot([string]$Root) {
  $rows = foreach ($file in Get-ChildItem -LiteralPath $Root -File -Recurse -Force | Sort-Object FullName) {
    $relative = $file.FullName.Substring($Root.Length)
    "$relative`t$((Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash)"
  }
  return $rows -join "`n"
}

function Invoke-PruningInstall([string]$Source, [string]$Target, [switch]$ExpectConflict, [switch]$Check) {
  # A negative subprocess must be observed, not promoted to the script verdict.
  $ErrorActionPreference = 'Continue'
  $extra = @()
  if ($Check) { $extra += '--check' }
  if ($PruningPerformer -eq 'bash') {
    $bash = (Get-Command bash -ErrorAction Stop).Source
    $output = & $bash -c 'set -euo pipefail; source "$1"; shift; lintel_native_main "$@"' `
      native-pruning (Join-Path $RepoRoot 'install\native.sh') --source $Source --home $Target `
      --store ($Target + '-recovery') @extra 2>&1
  } else {
    $output = & $ShellExe -NoProfile -NonInteractive -File (Join-Path $RepoRoot 'install\install.ps1') `
      -Source $Source -Home $Target -Store ($Target + '-recovery') @extra 2>&1
  }
  $code = $LASTEXITCODE
  $text = $output -join "`n"
  if ($ExpectConflict) {
    if ($code -eq 0 -or $text -notmatch 'Modified managed file' -or $text -match 'Install complete') {
      throw "Expected an explicit pre-write managed-edit refusal, got exit $code`: $text"
    }
  } elseif ($code -ne 0) {
    throw "Native pruning fixture failed with exit $code`: $text"
  }
  return $text
}

function Test-ManagedPruning {
  $source = Join-Path $TestRoot 'pruning-source'
  $target = Join-Path $TestRoot 'pruning-target'
  $store = $target + '-recovery'
  foreach ($directory in @('scaffolding', 'lib', 'bin', 'templates', 'skills', 'agents',
      'shims', 'docs', 'hooks', 'install', 'packs\_default', '.claude-plugin', 'config')) {
    [IO.Directory]::CreateDirectory((Join-Path $source $directory)) | Out-Null
  }
  foreach ($relative in @('LICENSE', 'AGENT-INSTRUCTIONS.md', 'README.md', 'SECURITY.md',
      'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md', 'CHANGELOG.md')) {
    Write-FixtureFile $source $relative "Synthetic native install fixture.`n"
  }
  Write-FixtureFile $source '.claude-plugin\plugin.json' "{}`n"
  Write-FixtureFile $source 'config\aliases.yaml' "version: 1`nskill_aliases: []`nenv_var_aliases: []`nplugin_slug_aliases: []`n"
  foreach ($relative in @('install\directories.txt', 'install\layer-config.yaml.example', 'packs\_default\pack.yaml')) {
    [IO.File]::Copy((Join-Path $RepoRoot $relative), (Join-Path $source $relative))
  }
  $header = "---`nname: {0}`ndescription: Use to exercise a synthetic install.`ncolor: green`n" +
    "tools: Read`nvoice: internal`nlayer: foundation`ncli_support: [copilot]`n---`n"
  Write-FixtureFile $source 'skills\prior-example\SKILL.md' ($header -f 'prior-example')
  Write-FixtureFile $source 'skills\current-example\SKILL.md' ($header -f 'current-example')
  Write-FixtureFile $source 'skills\prior-example\scripts\helper.sh' "echo inert fixture`n"
  Invoke-PruningInstall $source $target | Out-Null
  $oldReceipts = @{}
  foreach ($receipt in Get-ChildItem -LiteralPath $store -Directory) {
    $oldReceipts[$receipt.Name] = Get-FixtureSnapshot $receipt.FullName
  }
  if ($oldReceipts.Count -ne 1) { throw 'Initial installation did not retain exactly one transaction receipt.' }
  $custom = @{
    'skills\prior-example\operator-note.md' = "Keep this user file beside retired managed files.`n"
    'skills\operator-workflow\SKILL.md' = "User-owned workflow content.`n"
    'config.yaml' = "Operator configuration.`n"
    'profile.yaml' = "Operator profile.`n"
    'roles\private\operator.md' = "Synthetic private role.`n"
    'packs\_default\pack.yaml' = "Operator pack customization.`n"
    'hooks\operator-extra\run.sh' = "echo inert operator hook`n"
  }
  foreach ($entry in $custom.GetEnumerator()) { Write-FixtureFile $target $entry.Key $entry.Value }
  $retired = @('skills/prior-example/SKILL.md', 'skills/prior-example/scripts/helper.sh')
  $editedPath = Join-Path $target $retired[1]
  $managedBytes = [IO.File]::ReadAllBytes($editedPath)
  [IO.File]::WriteAllText($editedPath, 'User edit to a formerly managed file.')
  foreach ($relative in $retired) { [IO.File]::Delete((Join-Path $source $relative)) }
  Write-FixtureFile $source 'skills\current-example\SKILL.md' (($header -f 'current-example') + "Updated candidate.`n")
  $beforeRefusal = Get-FixtureSnapshot $TestRoot
  Invoke-PruningInstall $source $target -ExpectConflict | Out-Null
  if ((Get-FixtureSnapshot $TestRoot) -cne $beforeRefusal) {
    throw 'A rejected prune changed the source, installed files, inventory or receipt evidence.'
  }
  [IO.File]::WriteAllBytes($editedPath, $managedBytes)
  Invoke-PruningInstall $source $target | Out-Null
  $inventory = [IO.File]::ReadAllText((Join-Path $target '.lintel-install.tsv'))
  foreach ($relative in $retired) {
    if (Test-Path -LiteralPath (Join-Path $target $relative)) { throw "Owned retired file was not pruned: $relative" }
    if ($inventory.Contains("`t$relative`n")) { throw "Retired path remained in the managed inventory: $relative" }
  }
  foreach ($entry in $custom.GetEnumerator()) {
    if ([IO.File]::ReadAllText((Join-Path $target $entry.Key)) -cne $entry.Value) {
      throw "Pruning changed operator content: $($entry.Key)"
    }
  }
  if ($inventory.Contains('operator-note.md') -or $inventory.Contains('operator-workflow')) {
    throw 'Pruning claimed an unowned user file in the managed inventory.'
  }
  $kept = 'skills\current-example\SKILL.md'
  if ([IO.File]::ReadAllText((Join-Path $target $kept)) -cne [IO.File]::ReadAllText((Join-Path $source $kept))) {
    throw 'The retained workflow did not update with the pruned candidate.'
  }
  foreach ($name in $oldReceipts.Keys) {
    if ((Get-FixtureSnapshot (Join-Path $store $name)) -cne $oldReceipts[$name]) {
      throw 'A completed prior receipt was changed by pruning.'
    }
  }
  $newReceipts = @(Get-ChildItem -LiteralPath $store -Directory |
    Where-Object { -not $oldReceipts.ContainsKey($_.Name) })
  if ($newReceipts.Count -ne 1) { throw 'Pruning did not record exactly one new transaction.' }
  $receiptRoot = $newReceipts[0].FullName
  if ([IO.File]::ReadAllText((Join-Path $receiptRoot 'state')).Trim() -cne 'complete') {
    throw 'Pruning was not recorded as a completed transaction.'
  }
  $rows = [IO.File]::ReadAllLines((Join-Path $receiptRoot 'plan.tsv'))
  if ($rows[-1].Split("`t")[7] -cne '.lintel-install.tsv') { throw 'Inventory was not the final publication.' }
  foreach ($relative in $retired) {
    $deletionRows = @($rows | Where-Object { $_.Split("`t")[7] -ceq $relative })
    if ($deletionRows.Count -ne 1) { throw "Missing exact deletion receipt row: $relative" }
    $cells = $deletionRows[0].Split("`t")
    if ($cells[1] -ceq '-' -or $cells[4] -cne '-' -or
        [IO.File]::ReadAllText((Join-Path $receiptRoot "phase/$($cells[0])")).Trim() -cne 'applied') {
      throw "Deletion was not bound to its before state and verified applied phase: $relative"
    }
  }
  $stable = Get-FixtureSnapshot $TestRoot
  Invoke-PruningInstall $source $target | Out-Null
  $verified = Invoke-PruningInstall $source $target -Check
  if ($verified -notmatch 'Installed managed bytes verified' -or
      (Get-FixtureSnapshot $TestRoot) -cne $stable) { throw 'Repeat/check changed the pruned result or its receipts.' }
  Write-Host "PASS: $PruningPerformer managed pruning preserves edits, user files, inventory ownership and transaction receipts."
}

try {
  New-Item -ItemType Directory -Path $TestRoot | Out-Null
  if ($PruningOnly) {
    Test-ManagedPruning
    exit 0
  }
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
  Test-ManagedPruning
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
