# ==============================================================================
# ani-sync Windows Universal Auto-Installer (PowerShell)
# Automatically installs ani-sync, FZF, MPV, yt-dlp, FFmpeg & Python dependencies
# ==============================================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host "        ani-sync Windows Universal Installer  " -ForegroundColor Cyan
Write-Host "     Stream Anime & Auto-Sync Watch Progress  " -ForegroundColor Cyan
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host ""

# Target Directories
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
$PyCmd = "python"
$HasPython = $false
try {
    $out = & python --version 2>&1
    if ($out -match "Python 3\.") { $HasPython = $true }
} catch {}

if (-not $HasPython) {
    try {
        $out = & py --version 2>&1
        if ($out -match "Python 3\.") { $HasPython = $true; $PyCmd = "py" }
    } catch {}
}

if (-not $HasPython) {
    Write-Host "Python 3 not detected. Attempting automatic installation via winget..." -ForegroundColor Yellow
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
        Write-Host "✅ Python was installed! Refreshing environment variables..." -ForegroundColor Green
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        $HasPython = $true
        $PyCmd = "python"
    } else {
        Write-Host "❌ Python is not installed. Please install Python from https://www.python.org/downloads/" -ForegroundColor Red
        throw "Installation aborted."
    }
}

# 2. Install Python dependencies
Write-Host "[2/5] Installing Python packages (requests, tqdm, yt-dlp, Pillow)..." -ForegroundColor Yellow
& $PyCmd -m pip install --quiet --upgrade requests tqdm yt-dlp Pillow 2>$null

# 3. Check and Auto-Install FZF (Interactive Fuzzy Search)
Write-Host "[3/5] Setting up FZF fuzzy search..." -ForegroundColor Yellow
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

# 4. Check for MPV & FFmpeg
Write-Host "[4/5] Checking media player & stream codecs (MPV, FFmpeg)..." -ForegroundColor Yellow
if (-not (Get-Command mpv -ErrorAction SilentlyContinue)) {
    Write-Host "  MPV not detected. Attempting install via winget..." -ForegroundColor DarkGray
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install --exact --id mpv.net --source winget --silent --accept-source-agreements --accept-package-agreements 2>$null
    }
    if (-not (Get-Command mpv -ErrorAction SilentlyContinue)) {
        Write-Host "  ⚠️ MPV recommended for zero-buffering playback. Install with: winget install --exact --id mpv.net --source winget" -ForegroundColor DarkYellow
    }
} else {
    Write-Host "  ✓ MPV detected." -ForegroundColor Green
}

# 5. Install ani-sync scripts and wrappers
Write-Host "[5/5] Installing ani-sync..." -ForegroundColor Yellow

if (Test-Path "$PSScriptRoot\ani_sync") {
    Write-Host "  Copying ani_sync package from local directory..." -ForegroundColor Yellow
    Copy-Item "$PSScriptRoot\ani_sync" -Destination "$InstallDir\ani_sync" -Recurse -Force
} else {
    Write-Host "  Installing ani-sync via pip..." -ForegroundColor Yellow
    & $PyCmd -m pip install "https://github.com/idrisharis12/ani-sync/archive/refs/heads/main.zip"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install ani-sync via pip." -ForegroundColor Red
        throw "Installation aborted."
    }
}

# Retrieve the pip Scripts installation directory dynamically
$ScriptsPath = & $PyCmd -c "import sysconfig; print(sysconfig.get_path('scripts'))"
if (-not $ScriptsPath) { $ScriptsPath = "$env:USERPROFILE\AppData\Local\Programs\Python\Python312\Scripts" }

# Add Python Scripts, InstallDir, and BinDir to User PATH if missing
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$ScriptsPath*") {
    $UserPath = "$UserPath;$ScriptsPath"
    Write-Host "✓ Added Python Scripts to User PATH." -ForegroundColor Green
}
if ($UserPath -notlike "*$BinDir*") {
    $UserPath = "$UserPath;$BinDir"
    Write-Host "✓ Added $BinDir to User PATH." -ForegroundColor Green
}
if ($UserPath -notlike "*$InstallDir*") {
    $UserPath = "$UserPath;$InstallDir"
    Write-Host "✓ Added $InstallDir to User PATH." -ForegroundColor Green
}
[Environment]::SetEnvironmentVariable("Path", $UserPath, "User")
$env:Path = "$ScriptsPath;$BinDir;$InstallDir;" + $env:Path

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "           ✓ Successfully installed ani-sync!               " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Quick Start:" -ForegroundColor Yellow
Write-Host "  ani-sync                     Interactive anime search & launcher" -ForegroundColor Cyan
Write-Host "  ani-sync `"`"frieren`"`"           Search and stream specific anime" -ForegroundColor Cyan
Write-Host "  ani-sync -c                  Continue watching next episode" -ForegroundColor Cyan
Write-Host "  ani-sync history             Browse watch history with interactive FZF" -ForegroundColor Cyan
Write-Host "  ani-sync auth                Connect MyAnimeList / AniList / Kitsu" -ForegroundColor Cyan
Write-Host "  ani-sync doctor              Verify dependencies and system health" -ForegroundColor Cyan
Write-Host ""
