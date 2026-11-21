# Build helper for Windows PowerShell.
#
#   ./build.ps1
#   ./build.ps1 -ToolchainPath "C:/Tools/arm-none-eabi" -BuildDir build
#
# The script only uses CMake and Ninja; it does not modify PATH globally.

param(
    [string]$ToolchainPath = "",
    [string]$BuildDir = "build",
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Find-Toolchain {
    param([string]$explicit)
    if ($explicit) {
        if (Test-Path (Join-Path $explicit "bin/arm-none-eabi-gcc.exe")) { return $explicit }
        if (Test-Path (Join-Path $explicit "arm-none-eabi-gcc.exe")) { return (Split-Path $explicit) }
        throw "arm-none-eabi-gcc not found under $explicit"
    }

    $onPath = Get-Command arm-none-eabi-gcc -ErrorAction SilentlyContinue
    if ($onPath) { return (Split-Path (Split-Path $onPath.Source)) }

    $candidates = @(
        "$env:USERPROFILE\.platformio\packages\toolchain-gccarmnoneeabi",
        "C:\Program Files (x86)\GNU Arm Embedded Toolchain",
        "C:\Program Files\GNU Arm Embedded Toolchain",
        "$root\tools\arm-none-eabi"
    )
    foreach ($c in $candidates) {
        if (-not (Test-Path $c)) { continue }
        $gcc = Get-ChildItem -Path $c -Recurse -Filter arm-none-eabi-gcc.exe -ErrorAction SilentlyContinue |
               Select-Object -First 1
        if ($gcc) { return (Split-Path $gcc.FullName) }
    }
    throw "arm-none-eabi-gcc not found. Install GNU Arm Embedded and pass -ToolchainPath."
}

$tc = Find-Toolchain -explicit $ToolchainPath
Write-Host "Toolchain: $tc"

$cmakeExe = $null
$ninjaExe = $null

$cmakeCmd = Get-Command cmake -ErrorAction SilentlyContinue
if ($cmakeCmd) { $cmakeExe = $cmakeCmd.Source }
$ninjaCmd = Get-Command ninja -ErrorAction SilentlyContinue
if ($ninjaCmd) { $ninjaExe = $ninjaCmd.Source }

if (-not $cmakeExe -or -not $ninjaExe) {
    $pyScripts = (& python -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>$null)
    if ($pyScripts) {
        if (-not $cmakeExe -and (Test-Path (Join-Path $pyScripts "cmake.exe"))) {
            $cmakeExe = Join-Path $pyScripts "cmake.exe"
        }
        if (-not $ninjaExe -and (Test-Path (Join-Path $pyScripts "ninja.exe"))) {
            $ninjaExe = Join-Path $pyScripts "ninja.exe"
        }
    }
}

if (-not $cmakeExe) { throw "cmake not found" }
if (-not $ninjaExe) { throw "ninja not found" }

if (-not [System.IO.Path]::IsPathRooted($BuildDir)) {
    $BuildDir = Join-Path $root $BuildDir
}

Write-Host "CMake: $cmakeExe"
Write-Host "Ninja: $ninjaExe"

if ($Clean -and (Test-Path $BuildDir)) { Remove-Item -LiteralPath $BuildDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

$configure = @("-S", $root, "-B", $BuildDir, "-G", "Ninja",
               "-DARM_TOOLCHAIN_PATH=$($tc -replace '\\','/')",
               "-DCMAKE_MAKE_PROGRAM=$ninjaExe",
               "-DCMAKE_BUILD_TYPE=Release")

& $cmakeExe @configure
if ($LASTEXITCODE -ne 0) { throw "CMake configure failed" }

& $cmakeExe --build $BuildDir
if ($LASTEXITCODE -ne 0) { throw "Build failed" }
