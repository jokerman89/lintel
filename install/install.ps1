# Native bare installation; Python-based runtime operations remain separate.
$ErrorActionPreference = 'Stop'
try {
    if ($PSVersionTable.PSVersion -lt [version]'5.1') { throw 'PowerShell 5.1 or newer is required.' }
    $scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
    . (Join-Path $scriptDirectory 'native.ps1')
    Invoke-NativeInstall -Arguments @($args) -ExecutableSource (Split-Path -Parent $scriptDirectory)
    exit 0
} catch {
    [Console]::Error.WriteLine("ERROR: $($_.Exception.Message)")
    exit 1
}
