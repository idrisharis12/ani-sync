# ==============================================================================
# ani-sync Windows PowerShell Installer
# Stream anime in terminal and auto-sync progress to MyAnimeList
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host "        ani-sync Windows Installer           " -ForegroundColor Cyan
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
Write-Host "[1/4] Checking Python installation..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/ or via:" -ForegroundColor Yellow
    Write-Host "  winget install Python.Python.3.12" -ForegroundColor Cyan
    exit 1
}

# 2. Install Python dependencies
Write-Host "[2/4] Installing Python dependencies (requests, tqdm)..." -ForegroundColor Yellow
python -m pip install --quiet --upgrade requests tqdm

# 3. Check for mpv & yt-dlp
Write-Host "[3/4] Checking media player & acceleration tools..." -ForegroundColor Yellow
if (-not (Get-Command mpv -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  MPV not detected. Recommended for zero-buffering playback." -ForegroundColor DarkYellow
    Write-Host "You can install it with: winget install mpv.net (or scoop install mpv)" -ForegroundColor DarkGray
}
if (-not (Get-Command yt-dlp -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  yt-dlp not detected. Recommended for 64x turbo multi-connections." -ForegroundColor DarkYellow
    Write-Host "You can install it with: winget install yt-dlp (or scoop install yt-dlp)" -ForegroundColor DarkGray
}

# 4. Set up install directories
$InstallDir = "$env:LOCALAPPDATA\ani-sync"
$BinDir = "$env:USERPROFILE\.local\bin"

if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
}

$ScriptPath = "$InstallDir\ani_sync.py"
$CmdPath = "$BinDir\ani-sync.cmd"
$Ps1Path = "$BinDir\ani-sync.ps1"

Write-Host "[4/4] Installing ani-sync..." -ForegroundColor Yellow

# Copy or download ani_sync.py
if (Test-Path "$PSScriptRoot\ani_sync.py") {
    Copy-Item "$PSScriptRoot\ani_sync.py" -Destination $ScriptPath -Force
} else {
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/idrisharis12/ani-sync/main/ani_sync.py" -OutFile $ScriptPath
}

# Create CMD wrapper
$CmdContent = "@echo off`r`npython `"$ScriptPath`" %*"
Set-Content -Path $CmdPath -Value $CmdContent -Force

# Create PowerShell wrapper
$Ps1Content = "python `"$ScriptPath`" @args"
Set-Content -Path $Ps1Path -Value $Ps1Content -Force

# Add to User PATH if missing
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$BinDir", "User")
    $env:Path += ";$BinDir"
    Write-Host "✓ Added $BinDir to User PATH." -ForegroundColor Green
}

Write-Host ""
Write-Host "✓ Successfully installed ani-sync on Windows!" -ForegroundColor Green
Write-Host "Run 'ani-sync <anime name>' in CMD or PowerShell to start." -ForegroundColor Cyan
Write-Host "To link your MyAnimeList account: ani-sync auth" -ForegroundColor Cyan
Write-Host ""
