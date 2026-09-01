# ==============================================================================
# ani-sync Windows Universal Auto-Installer
# Automatically installs ani-sync, FZF fuzzy search, yt-dlp, MPV, and Python dependencies
# ==============================================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host "        ani-sync Windows Universal Installer  " -ForegroundColor Cyan
Write-Host "     Stream Anime & Auto-Sync Watch Progress  " -ForegroundColor Cyan
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host ""

# Directories
$InstallDir = "$env:LOCALAPPDATA\ani-sync"
$BinDir = "$env:USERPROFILE\.local\bin"

if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
}

# 1. Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
$HasPython = (Get-Command python -ErrorAction SilentlyContinue) -or (Get-Command py -ErrorAction SilentlyContinue)
if (-not $HasPython) {
    Write-Host "Python not found. Attempting automatic installation via winget..." -ForegroundColor Yellow
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
    } else {
        Write-Host "❌ Python is not installed. Please install Python from https://www.python.org/downloads/" -ForegroundColor Red
        exit 1
    }
}

# 2. Install Python dependencies
Write-Host "[2/5] Installing Python dependencies (requests, tqdm, yt-dlp)..." -ForegroundColor Yellow
python -m pip install --quiet --upgrade requests tqdm yt-dlp Pillow 2>$null

# 3. Check and Auto-Install FZF (Interactive Fuzzy Search)
Write-Host "[3/5] Setting up interactive FZF fuzzy search..." -ForegroundColor Yellow
$HasFzf = (Get-Command fzf -ErrorAction SilentlyContinue) -or (Test-Path "$BinDir\fzf.exe") -or (Test-Path "$InstallDir\fzf.exe")
if (-not $HasFzf) {
    $FzfInstalled = $false
    # Try Winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "  Installing FZF via winget..." -ForegroundColor DarkGray
        winget install junegunn.fzf --silent --accept-source-agreements --accept-package-agreements 2>$null
        if (Get-Command fzf -ErrorAction SilentlyContinue) { $FzfInstalled = $true }
    }
    # Try Scoop
    if (-not $FzfInstalled -and (Get-Command scoop -ErrorAction SilentlyContinue)) {
        Write-Host "  Installing FZF via scoop..." -ForegroundColor DarkGray
        scoop install fzf 2>$null
        if (Get-Command fzf -ErrorAction SilentlyContinue) { $FzfInstalled = $true }
    }
    # Direct GitHub binary download fallback
    if (-not $FzfInstalled) {
        Write-Host "  Downloading standalone FZF binary from GitHub releases..." -ForegroundColor DarkGray
        try {
            $FzfZip = "$env:TEMP\fzf_win.zip"
            $FzfUrl = "https://github.com/junegunn/fzf/releases/download/v0.60.3/fzf-0.60.3-windows_amd64.zip"
            Invoke-WebRequest -Uri $FzfUrl -OutFile $FzfZip -UseBasicParsing
            Expand-Archive -Path $FzfZip -DestinationPath $BinDir -Force
            Copy-Item "$BinDir\fzf.exe" -Destination "$InstallDir\fzf.exe" -Force -ErrorAction SilentlyContinue
            Remove-Item $FzfZip -Force -ErrorAction SilentlyContinue
            $FzfInstalled = $true
            Write-Host "  ✓ Standalone FZF installed to $BinDir\fzf.exe" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️ Could not auto-download FZF. Numbered menus will be used as fallback." -ForegroundColor DarkYellow
        }
    }
} else {
    Write-Host "  ✓ FZF is already installed." -ForegroundColor Green
}

# 4. Check for MPV & yt-dlp
Write-Host "[4/5] Checking media player & stream acceleration..." -ForegroundColor Yellow
if (-not (Get-Command mpv -ErrorAction SilentlyContinue)) {
    Write-Host "  MPV not detected. Attempting install via winget..." -ForegroundColor DarkGray
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install mpv.net --silent --accept-source-agreements --accept-package-agreements 2>$null
    }
    if (-not (Get-Command mpv -ErrorAction SilentlyContinue)) {
        Write-Host "  ⚠️  MPV recommended for zero-buffering playback. Install with: winget install mpv.net" -ForegroundColor DarkYellow
    }
}

# 5. Install ani-sync scripts and wrappers
Write-Host "[5/5] Installing ani-sync..." -ForegroundColor Yellow

$CmdPath = "$BinDir\ani-sync.cmd"
$Ps1Path = "$BinDir\ani-sync.ps1"

# Copy or download ani-sync package
if (Test-Path "$PSScriptRoot\ani_sync") {
    Write-Host "  Copying ani_sync package from current directory..." -ForegroundColor Yellow
    Copy-Item "$PSScriptRoot\ani_sync" -Destination "$InstallDir\ani_sync" -Recurse -Force
} else {
    Write-Host "  Installing ani-sync via pip..." -ForegroundColor Yellow
    & pip install "git+https://github.com/idrisharis12/ani-sync.git"
}

# Create a batch file launcher
Write-Host "  Creating launcher in $InstallDir..." -ForegroundColor Cyan
$LauncherScript = @"
@echo off
set "PATH=$InstallDir;%PATH%"
set "PYTHONPATH=$InstallDir;%PYTHONPATH%"
python -m ani_sync %*
"@
Set-Content -Path "$InstallDir\ani-sync.bat" -Value $LauncherScript -Encoding ASCII

# Create PowerShell wrapper
$Ps1Content = "`$env:PATH = `"$InstallDir;`$env:PATH`"`r`n`$env:PYTHONPATH = `"$InstallDir;`$env:PYTHONPATH`"`r`npython -m ani_sync @args"
Set-Content -Path $Ps1Path -Value $Ps1Content -Force

# Add to User PATH if missing
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$BinDir", "User")
    $env:Path = "$BinDir;$env:Path"
    Write-Host "✓ Added $BinDir to User PATH." -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "           ✓ Successfully installed ani-sync!               " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Run 'ani-sync <anime name>' or 'ani-sync' to start." -ForegroundColor Cyan
Write-Host "To link your tracking accounts: ani-sync auth" -ForegroundColor Cyan
Write-Host "To check system status:         ani-sync doctor" -ForegroundColor Cyan
Write-Host ""
