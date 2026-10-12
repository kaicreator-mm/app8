# SE11/SE15 LibreOffice official-release Execution Target identity (Issue #69)
# Requires PR #64 + PR #67 independently reviewed and merged BEFORE using -Install.
# With no -Install switch this downloads/verifies the MSI only; it changes no installed software.
# PowerShell 5.1-compatible. No hidden truth, evaluated fixtures, or UIA access.
[CmdletBinding()]
param(
    [switch]$Install,
    [string]$EvidenceRoot = (Join-Path $env:TEMP "app8-se11-lo-official")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Url = "https://download.documentfoundation.org/libreoffice/stable/26.8.1/win/x86_64/LibreOffice_26.8.1_Win_x86-64.msi"
$ExpectedSha = "C6298B10CFA1748BCBEDAD94C62CE771E240E5021BFD6D7A967CD571B04B5312"
$Version = "26.8.1.1"
$ProductCode = "{87B289F9-6172-4C3D-A091-EE36A40E1287}"
$VcRuntimeDisplayNameBases = @(
    "Microsoft Visual C++ 2015-2022 Redistributable (x64)",
    "Microsoft Visual C++ v14 Redistributable (x64)"
)
New-Item -ItemType Directory -Force -Path $EvidenceRoot | Out-Null
$msi = Join-Path $EvidenceRoot "LibreOffice_26.8.1_Win_x86-64.msi"
$state = "PACKAGE_DOWNLOADED_VERIFIED_NOT_INSTALLED"

function Get-OptionalPropertyValue {
    param(
        [Parameter(Mandatory=$true)]$Object,
        [Parameter(Mandatory=$true)][string]$Name
    )
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }
    return $property.Value
}

if (-not (Test-Path -LiteralPath $msi)) {
    Invoke-WebRequest -Uri $Url -OutFile $msi -UseBasicParsing
}
$actualSha = (Get-FileHash -LiteralPath $msi -Algorithm SHA256).Hash.ToUpperInvariant()
if ($actualSha -ne $ExpectedSha) {
    throw "MSI_SHA256_MISMATCH: expected=$ExpectedSha actual=$actualSha; DO NOT INSTALL OR SUBSTITUTE"
}
$signature = Get-AuthenticodeSignature -FilePath $msi

# winget provenance declares Microsoft.VCRedist.2015+.x64.
# This script does not install/substitute that dependency. It records the exact
# already-installed x64 VC runtime identity; Issue #69 freezes it into the final target.
$vcRuntime = @()
foreach ($registryRoot in @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
)) {
    if (Test-Path $registryRoot) {
        $vcRuntime += @(Get-ChildItem $registryRoot | ForEach-Object { Get-ItemProperty $_.PSPath } |
            Where-Object {
                $displayName = Get-OptionalPropertyValue $_ "DisplayName"
                $displayVersion = Get-OptionalPropertyValue $_ "DisplayVersion"
                $publisher = Get-OptionalPropertyValue $_ "Publisher"
                $productCode = Get-OptionalPropertyValue $_ "PSChildName"
                if ($null -eq $displayName -or $null -eq $displayVersion -or $null -eq $publisher -or $null -eq $productCode) {
                    return $false
                }
                $versionText = [string]$displayVersion
                $versionIsValid = $versionText -match "^[0-9]+(\.[0-9]+){1,3}$"
                $acceptedNameSuffixes = @($versionText)
                if ($versionIsValid) {
                    $versionParts = @($versionText -split "\.")
                    if ($versionParts.Count -eq 4 -and $versionParts[3] -eq "0") {
                        $acceptedNameSuffixes += (($versionParts[0..2]) -join ".")
                    }
                }
                $nameMatches = $false
                foreach ($baseName in $VcRuntimeDisplayNameBases) {
                    if ([string]$displayName -eq $baseName) {
                        $nameMatches = $true
                        break
                    }
                    foreach ($acceptedSuffix in $acceptedNameSuffixes) {
                        if ([string]$displayName -eq ($baseName + " - " + $acceptedSuffix)) {
                            $nameMatches = $true
                            break
                        }
                    }
                    if ($nameMatches) {
                        break
                    }
                }
                $nameMatches -and
                [string]$publisher -eq "Microsoft Corporation" -and
                $versionIsValid -and
                [string]$productCode -match "^\{[0-9A-Fa-f-]{36}\}$"
            } |
            Select-Object @{Name="DisplayName";Expression={ Get-OptionalPropertyValue $_ "DisplayName" }}, @{Name="DisplayVersion";Expression={ Get-OptionalPropertyValue $_ "DisplayVersion" }}, @{Name="PSChildName";Expression={ Get-OptionalPropertyValue $_ "PSChildName" }}, @{Name="Publisher";Expression={ Get-OptionalPropertyValue $_ "Publisher" }})
    }
}
if ($Install -and $vcRuntime.Count -ne 1) {
    throw "VC_RUNTIME_DEPENDENCY_AMBIGUOUS_OR_MISSING: expected exactly one supported Microsoft Visual C++ v14 x64 Redistributable registry identity, found $($vcRuntime.Count); DO NOT AUTO-INSTALL OR SUBSTITUTE"
}

if ($Install) {
    $who = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($who)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Installation requires an explicitly elevated PowerShell window (no auto-elevation)"
    }
    $installLog = Join-Path $EvidenceRoot "msi-install.log"
    $arguments = "/i `"$msi`" /qn /norestart /L*v `"$installLog`""
    $proc = Start-Process -FilePath "msiexec.exe" -ArgumentList $arguments -PassThru -Wait
    if ($proc.ExitCode -notin @(0, 3010)) {
        throw "MSI_INSTALL_FAILED exit=$($proc.ExitCode). Keep raw installer log."
    }
    $state = if ($proc.ExitCode -eq 3010) { "INSTALLED_REBOOT_REQUIRED" } else { "INSTALLED" }
}

$programDir = Join-Path $env:ProgramFiles "LibreOffice\program"
$soffice = Join-Path $programDir "soffice.com"
$executableList = @(
    "soffice.com", "soffice.exe", "swriter.exe", "scalc.exe", "simpress.exe"
)
$exeInfo = @()
if ($Install -and -not (Test-Path -LiteralPath $soffice)) {
    throw "LibreOffice soffice.com not found at expected Program Files location"
}
if ($Install) {
    foreach ($name in $executableList) {
        $path = Join-Path $programDir $name
        if (Test-Path -LiteralPath $path) {
            $item = Get-Item -LiteralPath $path
            $exeInfo += [ordered]@{
                name = $name
                path = $path
                sha256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
                file_version = $item.VersionInfo.FileVersion
                product_version = $item.VersionInfo.ProductVersion
            }
        }
    }
}
$uninstall = @()
foreach ($registryRoot in @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
)) {
    if (Test-Path $registryRoot) {
        $uninstall += @(Get-ChildItem $registryRoot | ForEach-Object { Get-ItemProperty $_.PSPath } |
            Where-Object {
                $displayName = Get-OptionalPropertyValue $_ "DisplayName"
                $null -ne $displayName -and [string]$displayName -like "LibreOffice*"
            } |
            Select-Object @{Name="DisplayName";Expression={ Get-OptionalPropertyValue $_ "DisplayName" }}, @{Name="DisplayVersion";Expression={ Get-OptionalPropertyValue $_ "DisplayVersion" }}, @{Name="PSChildName";Expression={ Get-OptionalPropertyValue $_ "PSChildName" }}, @{Name="InstallLocation";Expression={ Get-OptionalPropertyValue $_ "InstallLocation" }})
    }
}
$installed = @($uninstall | Where-Object { $_.DisplayVersion -eq $Version -and $_.PSChildName -eq $ProductCode })
if ($Install -and $installed.Count -eq 0) {
    throw "Exact LibreOffice package version/ProductCode not found in registry: $Version / $ProductCode"
}
$smoke = [ordered]@{ executed = $false; exit_code = $null; log = $null }
if ($Install -and $state -eq "INSTALLED") {
    $log = Join-Path $EvidenceRoot "smoke-version.log"
    $stderr = Join-Path $EvidenceRoot "smoke-version.stderr.log"
    & $soffice --headless --version 1> $log 2> $stderr
    $exitCode = $LASTEXITCODE
    $smoke = [ordered]@{ executed = $true; exit_code = $exitCode; log = $log; stderr_log = $stderr }
    if ($exitCode -ne 0) { throw "Non-evaluative version smoke failed with exit $exitCode" }
}
$os = Get-CimInstance Win32_OperatingSystem
$manifest = [ordered]@{
    schema_version = "app8-lo-execution-runtime-candidate-v1"
    stage = "OFFICIAL_EXECUTION_TARGET_IDENTITY_FREEZE"
    knowledge_source = "LibreOffice/core@016fd5d049256dc849111f60870f15201fcd1526"
    mapping_class = "OFFICIAL_RELEASE_MAPPED"
    source_relation = "DIVERGED"
    release_tag = "libreoffice-26.8.1.1"
    release_source_commit = "bf6ef2662401c7d6dce671ab4deb26ee0af3a7c1"
    official_url = $Url
    package_version = $Version
    product_code_expected = $ProductCode
    installer_sha256_expected = $ExpectedSha.ToLowerInvariant()
    installer_sha256_observed = $actualSha.ToLowerInvariant()
    publisher_signature_status = [string]$signature.Status
    windows_caption = $os.Caption
    windows_version = $os.Version
    windows_build = $os.BuildNumber
    machine_architecture = $env:PROCESSOR_ARCHITECTURE
    installation_policy = "DIRECT_OFFICIAL_MSI_ONLY"
    winget_install_allowed = $false
    vc_runtime_dependency_package = "Microsoft.VCRedist.2015+.x64"
    vc_runtime_registry_identity_policy = "MICROSOFT_V14_X64_EXACT_NAME_FAMILY_WITH_BOUNDED_ZERO_REVISION_SUFFIX_NORMALIZATION"
    vc_runtime_accepted_display_name_bases = @($VcRuntimeDisplayNameBases)
    vc_runtime_installed = @($vcRuntime)
    vc_runtime_exact_identity_frozen = ($vcRuntime.Count -gt 0)
    install_status = $state
    installed_registry = @($installed)
    executables = @($exeInfo)
    smoke = $smoke
    hidden_truth = "NOT_CREATED"
    evaluated_probes = "NOT_RUN"
    se15_binding = "NOT_RUN"
    product_freeze = "NO"
    l2_ready = "NO"
}
$manifestPath = Join-Path $EvidenceRoot "runtime-manifest.json"
[System.IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json -Depth 8), (New-Object System.Text.UTF8Encoding($false)))
Write-Host "OFFICIAL_MSI_SHA256=PASS"
Write-Host "STATUS=$state"
Write-Host "MANIFEST=$manifestPath"
Write-Host "NO_EVALUATED_PROBES=YES"
