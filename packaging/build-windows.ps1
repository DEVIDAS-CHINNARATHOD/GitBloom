$ErrorActionPreference = "Stop"

# Build this script on Windows x64. PyInstaller builds for the OS it runs on.
$projectRoot = Split-Path -Parent $PSScriptRoot
$version = [regex]::Match((Get-Content (Join-Path $projectRoot "gitbloom\__init__.py") -Raw), '__version__\s*=\s*"([^"]+)"').Groups[1].Value
if ([string]::IsNullOrWhiteSpace($version)) { throw "Could not read the GitBloom version." }
$releaseDir = Join-Path $projectRoot "release\v$version"
$buildDir = Join-Path $projectRoot "build\windows-x64"
$iconPath = Join-Path $projectRoot "packaging\icons\GitBloom.ico"

New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
python -m pip install --upgrade pyinstaller
python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "GitBloom-Windows-x64" `
    --icon $iconPath `
    --add-data "$projectRoot\packaging\icons\GitBloom.png;packaging/icons" `
    --paths $projectRoot `
    --distpath $releaseDir `
    --workpath $buildDir `
    --specpath $buildDir `
    (Join-Path $projectRoot "gitbloom\__main__.py")

Write-Host "Created $releaseDir\GitBloom-Windows-x64.exe (version $version)"
