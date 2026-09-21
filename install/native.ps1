# component: native-owned-installation
# implements: ADR-0030
# intent: .claude/plans/universal-implementation/packages/P10.md
# constraints: PowerShell 5.1/.NET; no Python, network or host activation
# last_intent_review: 2026-09-20

$script:NativeEncoding = New-Object System.Text.UTF8Encoding($false, $true)

function Get-NativeItem([string]$Path) {
    try { $attributes = [IO.File]::GetAttributes($Path) }
    catch [IO.FileNotFoundException] { return $null }
    catch [IO.DirectoryNotFoundException] { return $null }
    $item = if ($attributes -band [IO.FileAttributes]::Directory) {
        New-Object IO.DirectoryInfo($Path)
    } else { New-Object IO.FileInfo($Path) }
    $item.Refresh()
    return $item
}

function Assert-NativeAncestry([string]$Path) {
    $cursor = [IO.Path]::GetFullPath($Path)
    while ($cursor) {
        $item = Get-NativeItem $cursor
        if ($item -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Linked path refused: $cursor"
        }
        $parent = Split-Path -Parent $cursor
        if ($parent -eq $cursor) { break }
        $cursor = $parent
    }
}

function Assert-NativeTree([string]$Path) {
    Assert-NativeAncestry $Path
    $item = Get-NativeItem $Path
    if (-not $item) { return }
    if ($item -isnot [IO.DirectoryInfo]) { throw "Directory required: $Path" }
    $pending = New-Object 'System.Collections.Generic.Stack[string]'
    $pending.Push($Path)
    while ($pending.Count) {
        foreach ($child in Get-ChildItem -LiteralPath $pending.Pop() -Force) {
            if ($child.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Linked install entry refused before writes: $($child.FullName)"
            }
            if ($child.PSIsContainer) { $pending.Push($child.FullName) }
        }
    }
}

function Get-NativeRoot([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path) -or $Path -match '[\x00-\x1f\x7f]') {
        throw 'An explicit root without control characters is required.'
    }
    Assert-NativeAncestry $Path
    $resolved = [IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
    if ($resolved -eq [IO.Path]::GetPathRoot($resolved).TrimEnd('\', '/')) {
        throw 'Destination must be separate from the source checkout and cannot be a filesystem root.'
    }
    return $resolved
}

function Get-NativeIdentity([string]$Path) { return $Path.Replace('\', '/') }

function Assert-NativeSeparate([string]$First, [string]$Second) {
    $a = (Get-NativeIdentity $First).TrimEnd('/') + '/'
    $b = (Get-NativeIdentity $Second).TrimEnd('/') + '/'
    if ($a.StartsWith($b, [StringComparison]::OrdinalIgnoreCase) -or
        $b.StartsWith($a, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Installed data must be separate from the source checkout and recovery store (no overlapping roots).'
    }
}

function Assert-NativeRelative([string]$Relative) {
    if (-not $Relative -or $Relative -match '[\\:\x00-\x1f\x7f]' -or
        $Relative.StartsWith('/') -or $Relative.EndsWith('/')) { throw "Unsafe managed path: $Relative" }
    foreach ($part in $Relative.Split('/')) {
        if (-not $part -or $part -eq '.' -or $part -eq '..' -or $part -ieq '.git' -or
            $part -match '[ .]$' -or $part.Split('.')[0] -match '^(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])$') {
            throw "Nonportable managed path: $Relative"
        }
    }
}

function Assert-NativeAllowed([string]$Relative, [switch]$Receipt) {
    Assert-NativeRelative $Relative
    if ($Relative -cmatch '^(bin|lib|templates|scaffolding|skills|agents|shims|docs|hooks|install)/' -or
        $Relative -cin @('.claude-plugin/plugin.json', 'LICENSE', 'AGENT-INSTRUCTIONS.md', 'README.md',
                         'SECURITY.md', 'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md', 'CHANGELOG.md')) { return }
    if ($Receipt -and ($Relative -cin @('.lintel-install.tsv', 'config.yaml', 'profile.yaml', 'packs/active-pack') -or
        $Relative.StartsWith('packs/_default/') -or $Relative.StartsWith('brand/design-patterns/'))) { return }
    throw "Inventory path outside managed namespaces: $Relative"
}

function Get-NativePath([string]$Root, [string]$Relative) {
    Assert-NativeRelative $Relative
    $path = Join-Path $Root $Relative.Replace('/', [IO.Path]::DirectorySeparatorChar)
    Assert-NativeAncestry $path
    $cursor = Split-Path -Parent $path
    while ($cursor.Length -ge $Root.Length) {
        $parent = Get-NativeItem $cursor
        if ($parent -and $parent -isnot [IO.DirectoryInfo]) { throw "Parent is not a directory: $cursor" }
        $next = Split-Path -Parent $cursor
        if ($next -eq $cursor) { break }
        $cursor = $next
    }
    $item = Get-NativeItem $path
    if ($item -is [IO.DirectoryInfo]) { throw "Not a regular file: $path" }
    return $path
}

function Get-NativeDirectory([string]$Root, [string]$Relative) {
    Assert-NativeRelative $Relative
    Assert-NativeAncestry $Root
    $path = $Root
    foreach ($part in $Relative.Split('/')) {
        $path = Join-Path $path $part
        $item = Get-NativeItem $path
        if ($item -and ($item -isnot [IO.DirectoryInfo] -or
            ($item.Attributes -band [IO.FileAttributes]::ReparsePoint))) {
            throw "Unsafe directory slot (preserved): $Relative"
        }
    }
    return $path
}

function Get-NativeHash([byte[]]$Bytes) {
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($algorithm.ComputeHash($Bytes)).Replace('-', '').ToLowerInvariant() }
    finally { $algorithm.Dispose() }
}

function Test-NativeBytes([byte[]]$First, [byte[]]$Second) {
    return $First.Length -eq $Second.Length -and
        [Convert]::ToBase64String($First) -ceq [Convert]::ToBase64String($Second)
}

function Get-NativeState([string]$Path) {
    Assert-NativeAncestry $Path
    $item = Get-NativeItem $Path
    if (-not $item) { return $null }
    if ($item -is [IO.DirectoryInfo]) { throw "Not a regular file: $Path" }
    $bytes = [IO.File]::ReadAllBytes($Path)
    $after = Get-NativeItem $Path
    if ($item.Length -ne $after.Length -or $item.LastWriteTimeUtc -ne $after.LastWriteTimeUtc) {
        throw "File changed during inspection: $Path"
    }
    return @{ hash = Get-NativeHash $bytes; size = $bytes.Length
        mode = $(if ($item.Attributes -band [IO.FileAttributes]::ReadOnly) { '1' } else { '0' }); bytes = $bytes }
}

function Test-NativeState([string]$Path, $Expected) {
    $actual = Get-NativeState $Path
    if ($null -eq $Expected) { return $null -eq $actual }
    return $null -ne $actual -and $actual.hash -ceq $Expected.hash -and
        $actual.size -eq $Expected.size -and $actual.mode -ceq $Expected.mode -and
        (Test-NativeBytes $actual.bytes $Expected.bytes)
}

function Write-NativeData([string]$Path, [byte[]]$Bytes) {
    [IO.Directory]::CreateDirectory((Split-Path -Parent $Path)) | Out-Null
    [IO.File]::WriteAllBytes($Path, $Bytes)
    if (-not (Test-NativeBytes $Bytes ([IO.File]::ReadAllBytes($Path)))) {
        throw "Written bytes did not verify: $Path"
    }
}

function Write-NativeRecord([string]$Path, [string]$Value) {
    $before = Get-NativeState $Path
    $temporary = Join-Path (Split-Path -Parent $Path) ('.lintel-progress-' + [guid]::NewGuid().ToString('N'))
    Write-NativeData $temporary ($script:NativeEncoding.GetBytes($Value + "`n"))
    if ($null -ne $before) { Invoke-NativeReplace $temporary $Path $before }
    else { [IO.File]::Move($temporary, $Path) }
}

function Invoke-NativeReplace([string]$Temporary, [string]$Destination, $Expected) {
    for ($attempt = 0; $attempt -lt 5; $attempt++) {
        if (-not (Test-NativeState $Destination $Expected)) { throw "Replacement conflict: $Destination" }
        try {
            [IO.File]::Replace($Temporary, $Destination, [NullString]::Value)
            return
        } catch [IO.IOException] {
            $failure = $_.Exception
            while ($failure.InnerException) { $failure = $failure.InnerException }
            $errorCode = $failure.HResult -band 0xffff
            if ($errorCode -notin @(32, 33, 1175) -or $attempt -eq 4 -or -not [IO.File]::Exists($Temporary)) { throw }
            [Console]::Error.WriteLine("Native sharing conflict ($errorCode); retry $($attempt + 1)/4 against unchanged expected bytes.")
            Start-Sleep -Milliseconds (50 * [math]::Pow(2, $attempt))
        }
    }
}

function Write-NativeAtomic([string]$Root, [string]$Relative, $Expected, $After) {
    $path = Get-NativePath $Root $Relative
    if (-not (Test-NativeState $path $Expected)) { throw "Target changed before mutation: $Relative" }
    if ($null -eq $After) { [IO.File]::Delete($path); return }
    $parent = Split-Path -Parent $path
    [IO.Directory]::CreateDirectory($parent) | Out-Null
    $temporary = Join-Path $parent ('.lintel-install-write-' + [guid]::NewGuid().ToString('N'))
    Write-NativeData $temporary $After.bytes
    if ($After.mode -eq '1') { [IO.File]::SetAttributes($temporary, [IO.FileAttributes]::ReadOnly) }
    Get-NativePath $Root $Relative | Out-Null
    if (-not (Test-NativeState $path $Expected)) { throw "Target changed while staging replacement: $Relative" }
    if ($null -eq $Expected) { [IO.File]::Move($temporary, $path) }
    else { Invoke-NativeReplace $temporary $path $Expected }
}

function Read-NativeInventory([string]$Root) {
    $path = Get-NativePath $Root '.lintel-install.tsv'
    $result = @{}
    if (-not [IO.File]::Exists($path)) { return $result }
    $lines = [IO.File]::ReadAllLines($path, $script:NativeEncoding)
    if ($lines.Count -lt 1 -or $lines[0] -cne "LINTEL-INSTALL`t1") { throw 'Unsupported native install inventory; preserve it.' }
    foreach ($line in $lines | Select-Object -Skip 1) {
        $cells = $line.Split("`t")
        if ($cells.Count -ne 3 -or $cells[0] -cnotmatch '^[a-f0-9]{64}$' -or $cells[1] -notmatch '^[0-9]+$') {
            throw 'Malformed native install inventory.'
        }
        Assert-NativeAllowed $cells[2]
        if ($result.ContainsKey($cells[2])) { throw 'Duplicate/aliased inventory path.' }
        $result[$cells[2]] = $cells[0]
    }
    return $result
}

function Assert-NativeFrontmatter([byte[]]$Bytes, [string]$Relative) {
    $kind = ''
    if ($Relative.EndsWith('/SKILL.md')) { $kind = 'skill' }
    elseif ($Relative -match '(^|/)agents/.*\.md$' -and -not $Relative.EndsWith('/README.md')) { $kind = 'agent' }
    if (-not $kind) { return }
    $lines = $script:NativeEncoding.GetString($Bytes).Replace("`r`n", "`n").Split("`n")
    if ($lines[0] -cne '---') { throw "Missing frontmatter start: $Relative" }
    $seen = @{}; $closed = $false
    foreach ($line in $lines | Select-Object -Skip 1) {
        if ($line -ceq '---') { $closed = $true; break }
        if ($line -cmatch '^([A-Za-z_][A-Za-z_0-9-]*):') { $seen[$Matches[1]] = $true }
    }
    if (-not $closed) { throw "Missing frontmatter end: $Relative" }
    $required = @('name', 'description', 'color', 'tools', 'voice', 'cli_support')
    if ($kind -eq 'skill') { $required += 'layer' }
    foreach ($field in $required) {
        if (-not $seen.ContainsKey($field)) { throw "Missing frontmatter field $field`: $Relative" }
    }
}

function Add-NativeChange($Changes, [string]$Root, [string]$Relative, $After, [string]$OldHash, [string]$Kind) {
    $before = Get-NativeState (Get-NativePath $Root $Relative)
    if ($Kind -eq 'seed' -and $null -ne $before) { return }
    if ($Kind -eq 'inventory') {
        $actual = if ($null -eq $before) { '-' } else { $before.hash }
        if ($actual -cne $OldHash) { throw 'Inventory changed after ownership preflight.' }
    } elseif ($Kind -eq 'managed') {
        if ($OldHash -ne '-' -and $null -ne $before -and $before.hash -cne $OldHash) {
            throw "Modified managed file (preserved): $Relative"
        }
        if ($OldHash -eq '-' -and $null -ne $before -and
            ($null -eq $After -or $before.hash -cne $After.hash)) { throw "Unmanaged collision (preserved): $Relative" }
    }
    if ($null -ne $After -and $null -ne $before) { $After.mode = $before.mode }
    if (($null -eq $before -and $null -eq $After) -or
        ($null -ne $before -and $null -ne $After -and (Test-NativeBytes $before.bytes $After.bytes))) { return }
    $Changes.Add(@{ path = $Relative; before = $before; after = $After })
}

function New-NativeValue([byte[]]$Bytes, [string]$Mode = '0') {
    return @{ hash = Get-NativeHash $Bytes; size = $Bytes.Length; mode = $Mode; bytes = $Bytes }
}

function Get-NativePlan([string]$Source, [string]$Root) {
    $old = Read-NativeInventory $Root
    $inventory = Get-NativeState (Get-NativePath $Root '.lintel-install.tsv')
    $managed = @{}; $seeds = @{}
    $directories = [IO.File]::ReadAllLines((Get-NativePath $Source 'install/directories.txt'), $script:NativeEncoding)
    if (-not $directories.Count) { throw 'Native directory-slot contract is empty.' }
    foreach ($directory in $directories) { Get-NativeDirectory $Root $directory | Out-Null }
    foreach ($component in @('scaffolding', 'lib', 'bin', 'templates', 'skills', 'agents', 'shims', 'docs', 'hooks', 'install', 'packs/_default')) {
        $directory = Join-Path $Source $component
        if (-not [IO.Directory]::Exists($directory)) { throw "Missing source component: $component" }
        Assert-NativeTree $directory
        foreach ($file in Get-ChildItem -LiteralPath $directory -Recurse -File -Force) {
            $relative = $file.FullName.Substring($Source.Length + 1).Replace('\', '/')
            if ($relative -match '(^|/)__pycache__/|\.pyc$') { continue }
            $value = Get-NativeState $file.FullName
            Assert-NativeFrontmatter $value.bytes $relative
            if ($component -eq 'packs/_default') { $seeds.Add($relative, $value) }
            else { Assert-NativeAllowed $relative; $managed.Add($relative, $value) }
        }
    }
    foreach ($relative in @('LICENSE', 'AGENT-INSTRUCTIONS.md', 'README.md', 'SECURITY.md', 'CONTRIBUTING.md',
                            'CODE_OF_CONDUCT.md', 'CHANGELOG.md', '.claude-plugin/plugin.json')) {
        $value = Get-NativeState (Get-NativePath $Source $relative)
        if ($null -eq $value) { throw "Required source missing: $relative" }
        $managed.Add($relative, $value)
    }
    $config = Get-NativeState (Get-NativePath $Source 'install/layer-config.yaml.example')
    if ($null -eq $config) { throw 'Layer configuration seed is missing.' }
    $seeds.Add('config.yaml', $config)
    $seeds.Add('profile.yaml', (New-NativeValue $script:NativeEncoding.GetBytes(
        "# Lintel operator preferences; edit freely`nactive_pack: _default`ndefault_mode: internal-tool`nrole_active: none`n")))
    $seeds.Add('packs/active-pack', (New-NativeValue $script:NativeEncoding.GetBytes("_default`n")))
    $brand = Join-Path $Source 'seeds/brand/design-patterns'
    if ([IO.Directory]::Exists($brand)) {
        Assert-NativeTree $brand
        foreach ($file in Get-ChildItem -LiteralPath $brand -Recurse -File -Force) {
            $relative = 'brand/design-patterns/' + $file.FullName.Substring($brand.Length + 1).Replace('\', '/')
            $seeds.Add($relative, (Get-NativeState $file.FullName))
        }
    }
    $changes = New-Object 'System.Collections.Generic.List[object]'
    $lines = New-Object 'System.Collections.Generic.List[string]'
    $lines.Add("LINTEL-INSTALL`t1")
    [string[]]$keys = @($managed.Keys); [Array]::Sort($keys, [StringComparer]::Ordinal)
    foreach ($relative in $keys) {
        $value = $managed[$relative]
        $lines.Add("$($value.hash)`t$($value.size)`t$relative")
        $previous = if ($old.ContainsKey($relative)) { $old[$relative] } else { '-' }
        Add-NativeChange $changes $Root $relative $value $previous managed
    }
    foreach ($relative in $old.Keys) {
        if (-not $managed.ContainsKey($relative)) { Add-NativeChange $changes $Root $relative $null $old[$relative] managed }
    }
    [string[]]$keys = @($seeds.Keys); [Array]::Sort($keys, [StringComparer]::Ordinal)
    foreach ($relative in $keys) { Add-NativeChange $changes $Root $relative $seeds[$relative] '-' seed }
    $newInventory = New-NativeValue $script:NativeEncoding.GetBytes(($lines -join "`n") + "`n")
    $oldHash = if ($null -eq $inventory) { '-' } else { $inventory.hash }
    Add-NativeChange $changes $Root '.lintel-install.tsv' $newInventory $oldHash inventory
    return @{ changes = $changes.ToArray(); inventory_before = $oldHash; directories = $directories }
}

function Assert-NativeStore([string]$Root, [string]$Store, [string]$Command) {
    Assert-NativeTree $Store
    $owner = $script:NativeEncoding.GetBytes("LINTEL-RECOVERY`t1`n$(Get-NativeIdentity $Root)`n")
    $marker = Join-Path $Store '.lintel-recovery-owner'
    if ([IO.Directory]::Exists($Store) -and
        (-not [IO.File]::Exists($marker) -or -not (Test-NativeBytes $owner ([IO.File]::ReadAllBytes($marker))))) {
        throw "Unowned or foreign recovery store (preserved): $Store"
    }
    if (Get-NativeItem (Join-Path $Store '.operation-lock')) { throw 'Recovery store locked; no automatic lock stealing.' }
    if ($Command -ne 'recover' -and [IO.Directory]::Exists($Store)) {
        foreach ($receipt in Get-ChildItem -LiteralPath $Store -Force | Where-Object { $_.Name.StartsWith('txn-') }) {
            $state = Join-Path $receipt.FullName 'state'
            if (-not $receipt.PSIsContainer -or -not [IO.File]::Exists($state) -or
                [IO.File]::ReadAllText($state).Trim() -cnotin @('complete', 'recovered')) {
                throw "Incomplete/unknown transaction $($receipt.Name); inspect and recover explicitly."
            }
            Read-NativeReceipt $Root $Store $receipt.Name -EvidenceOnly | Out-Null
        }
    }
    return ,$owner
}

function New-NativeReceipt([string]$Root, [string]$Source, [string]$Store, $Plan) {
    $id = 'txn-' + [guid]::NewGuid().ToString('N')
    $folder = Join-Path $Store $id
    [IO.Directory]::CreateDirectory($folder) | Out-Null
    $lines = New-Object 'System.Collections.Generic.List[string]'
    $index = 0
    foreach ($change in $Plan.changes) {
        $number = '{0:d6}' -f $index; $index++
        $fields = New-Object 'System.Collections.Generic.List[string]'
        $fields.Add($number)
        foreach ($side in @('before', 'after')) {
            $value = $change[$side]
            if ($null -eq $value) { $fields.Add('-'); $fields.Add('-'); $fields.Add('-') }
            else {
                $fields.Add($value.hash); $fields.Add([string]$value.size); $fields.Add($value.mode)
                Write-NativeData (Join-Path $folder "$side/$number") $value.bytes
            }
        }
        $fields.Add($change.path); $lines.Add($fields -join "`t")
        Write-NativeData (Join-Path $folder "phase/$number") $script:NativeEncoding.GetBytes("pending`n")
    }
    $meta = "LINTEL-TRANSACTION`t1`nroot`t$(Get-NativeIdentity $Root)`nsource`t$(Get-NativeIdentity $Source)`n" +
            "store`t$(Get-NativeIdentity $Store)`nid`t$id`nplatform`tpowershell-readonly`ninventory_before`t$($Plan.inventory_before)`n"
    $metaBytes = $script:NativeEncoding.GetBytes($meta)
    $planBytes = $script:NativeEncoding.GetBytes(($lines -join "`n") + "`n")
    Write-NativeData (Join-Path $folder 'meta.tsv') $metaBytes
    Write-NativeData (Join-Path $folder 'plan.tsv') $planBytes
    Write-NativeData (Join-Path $folder 'receipt.sha256') $script:NativeEncoding.GetBytes(
        "$(Get-NativeHash $metaBytes) $(Get-NativeHash $planBytes)`n")
    Write-NativeRecord (Join-Path $folder 'state') prepared
    return $folder
}

function Read-NativeReceipt([string]$Root, [string]$Store, [string]$Id, [switch]$EvidenceOnly) {
    if ($Id -cnotmatch '^txn-[A-Za-z0-9-]+$') { throw 'Unsupported receipt ID; retain historical backups for manual recovery.' }
    $folder = Join-Path $Store $Id
    Assert-NativeTree $folder
    $metaBytes = [IO.File]::ReadAllBytes((Join-Path $folder 'meta.tsv'))
    $planBytes = [IO.File]::ReadAllBytes((Join-Path $folder 'plan.tsv'))
    $checksum = [IO.File]::ReadAllText((Join-Path $folder 'receipt.sha256'), $script:NativeEncoding).Trim()
    if ($checksum -cne "$(Get-NativeHash $metaBytes) $(Get-NativeHash $planBytes)") { throw 'Receipt identity failed; preserve corrupt evidence.' }
    $meta = @{}
    foreach ($line in $script:NativeEncoding.GetString($metaBytes).TrimEnd("`n").Split("`n")) {
        $cells = $line.Split("`t")
        if ($cells.Count -ne 2 -or $meta.ContainsKey($cells[0])) { throw 'Malformed receipt metadata.' }
        $meta.Add($cells[0], $cells[1])
    }
    if ($meta.Count -ne 7 -or $meta['LINTEL-TRANSACTION'] -cne '1' -or $meta.root -cne (Get-NativeIdentity $Root) -or
        $meta.store -cne (Get-NativeIdentity $Store) -or $meta.id -cne $Id -or -not $meta.source -or
        $meta.platform -cne 'powershell-readonly' -or $meta.inventory_before -cnotmatch '^(-|[a-f0-9]{64})$') {
        throw 'Foreign/unsupported receipt roots, version or mode projection.'
    }
    $rows = New-Object 'System.Collections.Generic.List[object]'
    $seen = @{}; $index = 0
    foreach ($line in $script:NativeEncoding.GetString($planBytes).TrimEnd("`n").Split("`n")) {
        $cells = $line.Split("`t")
        if ($cells.Count -ne 8 -or $cells[0] -cne ('{0:d6}' -f $index)) { throw 'Malformed transaction index/row.' }
        $index++
        $relative = $cells[7]; Assert-NativeAllowed $relative -Receipt
        if (-not $EvidenceOnly) { Get-NativePath $Root $relative | Out-Null }
        if ($seen.ContainsKey($relative)) { throw 'Aliased transaction path.' }
        $seen.Add($relative, $true)
        $row = @{ path = $relative; index = $cells[0] }
        foreach ($side in @('before', 'after')) {
            $offset = if ($side -eq 'before') { 1 } else { 4 }
            $blob = Join-Path $folder "$side/$($cells[0])"
            if ($cells[$offset] -ceq '-') {
                if ($cells[$offset+1] -cne '-' -or $cells[$offset+2] -cne '-' -or (Get-NativeItem $blob)) {
                    throw 'Malformed absent-file state.'
                }
                $row[$side] = $null
            } else {
                if ($cells[$offset] -cnotmatch '^[a-f0-9]{64}$' -or $cells[$offset+1] -notmatch '^[0-9]+$' -or
                    $cells[$offset+2] -cnotmatch '^[01]$') { throw 'Invalid planned file state.' }
                $bytes = [IO.File]::ReadAllBytes($blob)
                if ((Get-NativeHash $bytes) -cne $cells[$offset] -or $bytes.Length -ne [long]$cells[$offset+1]) {
                    throw "Receipt blob failed verification: $relative"
                }
                $row[$side] = New-NativeValue $bytes $cells[$offset+2]
            }
        }
        $row.phase = [IO.File]::ReadAllText((Join-Path $folder "phase/$($row.index)")).Trim()
        if ($row.phase -cnotin @('pending', 'applying', 'applied', 'restoring', 'restored')) { throw 'Unknown file progress.' }
        $rows.Add($row)
    }
    if (-not $rows.Count) { throw 'Empty transaction receipt.' }
    $state = [IO.File]::ReadAllText((Join-Path $folder 'state')).Trim()
    if ($state -cnotin @('prepared', 'applying', 'complete', 'recovering', 'recovered')) { throw 'Unknown transaction state.' }
    foreach ($row in $rows) {
        if (($state -ceq 'prepared' -and $row.phase -cne 'pending') -or
            ($state -ceq 'complete' -and $row.phase -cne 'applied') -or
            ($state -ceq 'recovered' -and $row.phase -cne 'restored') -or
            ($state -ceq 'applying' -and $row.phase -cin @('restoring', 'restored'))) {
            throw 'Transaction state contradicts its per-file progress.'
        }
    }
    if ($seen.ContainsKey('.lintel-install.tsv')) {
        $last = $rows[$rows.Count - 1]
        $old = if ($null -eq $last.before) { '-' } else { $last.before.hash }
        if ($last.path -cne '.lintel-install.tsv' -or $old -cne $meta.inventory_before) { throw 'Inventory must be bound and published last.' }
    } elseif (-not $EvidenceOnly) {
        $current = Get-NativeState (Get-NativePath $Root '.lintel-install.tsv')
        $currentHash = if ($null -eq $current) { '-' } else { $current.hash }
        if ($currentHash -cne $meta.inventory_before) { throw 'Inventory changed outside this transaction.' }
    }
    return @{ path = $folder; rows = $rows.ToArray() }
}

function Invoke-NativeRecovery([string]$Root, $Receipt) {
    foreach ($row in $Receipt.rows) {
        $path = Get-NativePath $Root $row.path
        if (Test-NativeState $path $row.before) { continue }
        if ($row.phase -cin @('pending', 'restored') -or -not (Test-NativeState $path $row.after)) {
            throw "Recovery conflict or consumed permission; current bytes preserved: $($row.path)"
        }
    }
    Write-NativeRecord (Join-Path $Receipt.path 'state') recovering
    foreach ($row in $Receipt.rows) {
        $path = Get-NativePath $Root $row.path
        if (-not (Test-NativeState $path $row.before)) {
            Write-NativeRecord (Join-Path $Receipt.path "phase/$($row.index)") restoring
            Write-NativeAtomic $Root $row.path $row.after $row.before
        }
        if (-not (Test-NativeState $path $row.before)) { throw "Restored file did not verify: $($row.path)" }
        Write-NativeRecord (Join-Path $Receipt.path "phase/$($row.index)") restored
    }
    foreach ($row in $Receipt.rows) {
        if (-not (Test-NativeState (Get-NativePath $Root $row.path) $row.before)) { throw 'Restored set changed before completion.' }
    }
    Write-NativeRecord (Join-Path $Receipt.path 'state') recovered
}

function Invoke-NativeInstall([string[]]$Arguments, [string]$ExecutableSource) {
    $source = $ExecutableSource
    $root = if ($env:LINTEL_HOME) { $env:LINTEL_HOME } else { Join-Path $HOME '.lintel' }
    $store = $env:LINTEL_RECOVERY_STORE
    $command = 'install'; $id = ''
    for ($i=0; $i -lt $Arguments.Count; $i++) {
        $arg = $Arguments[$i].TrimStart('-').ToLowerInvariant()
        if ($arg -in @('source', 'home', 'store', 'recover')) {
            if ($i + 1 -ge $Arguments.Count -or -not $Arguments[$i+1]) { throw "$arg requires a value." }
            $i++
            switch ($arg) {
                source { $source = $Arguments[$i] } home { $root = $Arguments[$i] }
                store { $store = $Arguments[$i] } recover { $command = 'recover'; $id = $Arguments[$i] }
            }
        } elseif ($arg -eq 'check') { $command = 'check' }
        elseif ($arg -in @('h', 'help')) {
            Write-Host 'Usage: install.ps1 [-Source PATH] [-Home PATH] [-Store PATH] [-Check | -Recover ID]'
            Write-Host 'Native installation/recovery uses Git and .NET, not Python. No host activation.'
            return
        } else { throw "Unknown argument: $($Arguments[$i])" }
    }
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'git is required.' }
    Get-NativeHash ([byte[]]@()) | Out-Null
    $source = Get-NativeRoot $source; $root = Get-NativeRoot $root
    if ($root -ieq [IO.Path]::GetFullPath($HOME).TrimEnd('\', '/')) { throw 'Installation target must not be the user-home root.' }
    if ($command -eq 'install') { Assert-NativeSeparate $source $root }
    if (-not $store) { $store = $root + '-recovery' }
    $store = Get-NativeRoot $store
    Assert-NativeSeparate $root $store; Assert-NativeSeparate $source $store
    Assert-NativeTree $root
    $owner = Assert-NativeStore $root $store $command
    Write-Host "Source: $source`nInstalled data: $root`nRecovery store: $store"
    if ($command -eq 'check') {
        if (-not [IO.File]::Exists((Join-Path $root '.lintel-install.tsv'))) { throw 'Native inventory missing; installation is unverified.' }
        $inventory = Read-NativeInventory $root
        foreach ($relative in $inventory.Keys) {
            $state = Get-NativeState (Get-NativePath $root $relative)
            if ($null -eq $state -or $state.hash -cne $inventory[$relative]) { throw "Managed-file drift: $relative" }
        }
        Write-Host 'Installed managed bytes verified. Host activation remains unverified.'
        return
    }
    $receipt = $null
    if ($command -eq 'install') {
        $plan = Get-NativePlan $source $root
        if (-not $plan.changes.Count) {
            foreach ($directory in $plan.directories) {
                [IO.Directory]::CreateDirectory((Get-NativeDirectory $root $directory)) | Out-Null
            }
            Write-Host 'Install complete: managed bytes and directory slots verified; customizations preserved.'
            return
        }
    } else { $receipt = Read-NativeReceipt $root $store $id }
    if (-not [IO.Directory]::Exists($store)) {
        [IO.Directory]::CreateDirectory($store) | Out-Null
        Write-NativeData (Join-Path $store '.lintel-recovery-owner') $owner
    }
    $lockPath = Join-Path $store '.operation-lock'
    $lock = New-Object IO.FileStream($lockPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    $lockToken = $script:NativeEncoding.GetBytes([guid]::NewGuid().ToString('N'))
    $lock.Write($lockToken, 0, $lockToken.Length); $lock.Flush()
    try {
        if ($command -eq 'recover') {
            Invoke-NativeRecovery $root $receipt
            Write-Host "Recovery verified: $id. Empty created directories and receipt evidence were retained."
            return
        }
        $folder = New-NativeReceipt $root $source $store $plan
        $receipt = Read-NativeReceipt $root $store (Split-Path -Leaf $folder)
        foreach ($row in $receipt.rows) {
            if (-not (Test-NativeState (Get-NativePath $root $row.path) $row.before)) { throw "Target changed after preflight: $($row.path)" }
        }
        Write-NativeRecord (Join-Path $folder 'state') applying
        foreach ($directory in $plan.directories) {
            [IO.Directory]::CreateDirectory((Get-NativeDirectory $root $directory)) | Out-Null
        }
        foreach ($row in $receipt.rows) {
            Write-NativeRecord (Join-Path $folder "phase/$($row.index)") applying
            Write-NativeAtomic $root $row.path $row.before $row.after
            if (-not (Test-NativeState (Get-NativePath $root $row.path) $row.after)) { throw "Published file failed verification: $($row.path)" }
            Write-NativeRecord (Join-Path $folder "phase/$($row.index)") applied
        }
        foreach ($row in $receipt.rows) {
            if (-not (Test-NativeState (Get-NativePath $root $row.path) $row.after)) { throw 'Installed set changed before completion.' }
        }
        Write-NativeRecord (Join-Path $folder 'state') complete
        Write-Host "Install complete: verified $($receipt.rows.Count) file mutations at $root."
        Write-Host "Recovery receipt: $folder`nNo hooks or host plugins were activated."
    } catch {
        if ($receipt) { Write-Host "INCOMPLETE: preserve receipt $($receipt.path); explicit -Recover is required." }
        throw
    } finally {
        $lock.Dispose()
        if (Test-NativeBytes $lockToken ([IO.File]::ReadAllBytes($lockPath))) { [IO.File]::Delete($lockPath) }
        else { throw 'Owned lock was replaced; preserve it for inspection.' }
    }
}
