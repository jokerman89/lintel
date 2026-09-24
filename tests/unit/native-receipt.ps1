# Native receipt primitives, with only a newly allocated owned fixture.
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
. (Join-Path $Root 'install\native.ps1')
$Fixture = Join-Path ([IO.Path]::GetTempPath()) ('lintel-ps-receipt-' + [guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($Fixture) | Out-Null
try {
    $record = Join-Path $Fixture 'state'
    Write-NativeRecord $record prepared
    Write-NativeRecord $record applying
    if ([IO.File]::ReadAllText($record) -cne "applying`n") { throw 'Receipt update did not replace exact bytes.' }
    $before = New-NativeValue ([Text.Encoding]::UTF8.GetBytes('before'))
    $after = New-NativeValue ([Text.Encoding]::UTF8.GetBytes('after'))
    Write-NativeAtomic $Fixture 'payload.txt' $null $before
    Write-NativeAtomic $Fixture 'payload.txt' $before $after
    if (-not (Test-NativeState (Join-Path $Fixture 'payload.txt') $after)) { throw 'Payload replacement did not verify.' }
    $refused = $false
    try { Write-NativeAtomic $Fixture 'payload.txt' $before $null }
    catch { $refused = $true }
    if (-not $refused) { throw 'Stale expected bytes were accepted.' }
    if (-not (Test-NativeState (Join-Path $Fixture 'payload.txt') $after)) { throw 'Stale refusal altered user bytes.' }
    $inventoryHome = Join-Path $Fixture 'home'
    [IO.Directory]::CreateDirectory($inventoryHome) | Out-Null
    $inventoryPath = Join-Path $inventoryHome '.lintel-install.tsv'
    $observedInventory = "LINTEL-INSTALL`t1`n" + ('a' * 64) + "`t1`tdocs/planned-row.md`n"
    [IO.File]::WriteAllBytes($inventoryPath, [Text.Encoding]::UTF8.GetBytes($observedInventory))
    $parseInventory = ${function:Read-NativeInventory}
    function Read-NativeInventory {
        $records = & $parseInventory @args
        [IO.File]::WriteAllBytes($inventoryPath, [Text.Encoding]::UTF8.GetBytes("LINTEL-INSTALL`t1`n"))
        return $records
    }
    $refusal = ''
    try { Get-NativePlan $Root $inventoryHome | Out-Null } catch { $refusal = $_.Exception.Message }
    if ($refusal -cne 'Inventory changed after ownership preflight.') {
        throw "Inventory rewritten after its parsed observation was not refused: '$refusal'"
    }
    Write-Output 'PASS: native receipt publication, replacement, stale-state and inventory-observation refusal.'
} finally {
    foreach ($file in @('state', 'payload.txt', 'home\.lintel-install.tsv')) {
        $path = Join-Path $Fixture $file
        if ([IO.File]::Exists($path)) { [IO.File]::Delete($path) }
    }
    if ([IO.Directory]::Exists((Join-Path $Fixture 'home'))) { [IO.Directory]::Delete((Join-Path $Fixture 'home')) }
    [IO.Directory]::Delete($Fixture)
}
