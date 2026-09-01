import re

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Badges to 'for-the-badge' style for a cooler look
badge_old = r"""<p align="center">
  <a href="https://github.com/idrisharis12/ani-sync/stargazers"><img src="https://img.shields.io/github/stars/idrisharis12/ani-sync\?style=flat-square&logo=github&color=gold" alt="GitHub Stars" /></a>
  <a href="https://github.com/idrisharis12/ani-sync/releases"><img src="https://img.shields.io/github/v/release/idrisharis12/ani-sync\?style=flat-square&color=brightgreen" alt="Release" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue\.svg\?style=flat-square" alt="License: MIT" /></a>
  <a href="https://www\.python\.org/"><img src="https://img.shields.io/badge/Python-3\.8\+-3776AB\?style=flat-square&logo=python&logoColor=white" alt="Python 3\.8\+" /></a>
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey\?style=flat-square" alt="Platform" />
  <img src="https://img.shields.io/badge/Speed-64x%20Turbo-00C853\?style=flat-square" alt="64x Turbo Speed" />
  <img src="https://img.shields.io/badge/AniSkip-Frame--Accurate-FF6F00\?style=flat-square" alt="AniSkip Frame-Accurate" />
  <img src="https://img.shields.io/badge/Party-Syncplay-00E5FF\?style=flat-square" alt="Syncplay Watch Together" />
  <img src="https://img.shields.io/badge/Tracking-MAL%20%7C%20AniList%20%7C%20Kitsu-7C4DFF\?style=flat-square" alt="Multi-Platform Tracking" />
</p>"""

badge_new = """<p align="center">
  <a href="https://github.com/idrisharis12/ani-sync/stargazers"><img src="https://img.shields.io/github/stars/idrisharis12/ani-sync?style=for-the-badge&logo=github&color=FFD700" alt="GitHub Stars" /></a>
  <a href="https://github.com/idrisharis12/ani-sync/releases"><img src="https://img.shields.io/github/v/release/idrisharis12/ani-sync?style=for-the-badge&color=00E676&logo=rocket" alt="Release" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-0088FF.svg?style=for-the-badge&logo=opensourceinitiative" alt="License: MIT" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+" /></a><br>
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-2D3748?style=for-the-badge&logo=linux" alt="Platform" />
  <img src="https://img.shields.io/badge/Speed-64x%20Turbo-00C853?style=for-the-badge&logo=codeforces" alt="64x Turbo Speed" />
  <img src="https://img.shields.io/badge/AniSkip-Frame--Accurate-FF6F00?style=for-the-badge&logo=fastforward" alt="AniSkip Frame-Accurate" />
  <img src="https://img.shields.io/badge/Party-Syncplay-00E5FF?style=for-the-badge&logo=wechat" alt="Syncplay Watch Together" />
  <img src="https://img.shields.io/badge/Tracking-MAL%20%7C%20AniList%20%7C%20Kitsu-7C4DFF?style=for-the-badge&logo=graphql" alt="Multi-Platform Tracking" />
</p>"""
content = re.sub(badge_old, badge_new, content)

# 2. Make Changelogs Interactive
changelog_old = r"""## 📦 What's New in v2\.10\.4

- \*\*🐛 Fixed Configuration NameError Bug\*\* — Fixed `NameError: name 'CONFIG' is not defined` when initializing volume options in `main\(\)`\.
- \*\*🔊 Complete Volume Parameter Propagation\*\* — Full end-to-end parameter passing for `-v` / `--volume` and configuration variables through `play_loop`, `turbo_play`, and `launch_player`\.
- \*\*💬 Expanded Discord IPC Socket Discovery\*\* — Expanded Linux IPC socket paths to automatically detect \*\*Vesktop\*\*, \*\*Discord Canary\*\*, \*\*Discord PTB\*\*, \*\*Snap\*\*, and \*\*Flatpak\*\* instances\.
- \*\*🔄 Single Consolidated CI/CD Pipeline\*\* — Consolidated multi-stage GitHub Actions workflows into a single `\.github/workflows/workflow\.yml` file\.
- \*\*🧹 Lint & Quality Audit\*\* — Cleaned up all unused imports, fixed missing f-string placeholders, and added unit tests for player parameter signatures\.

---

## 📦 What's New in v2\.10\.2

- \*\*🎮 Fixed Discord Rich Presence\*\* — Repaired the zero-dependency Discord IPC module to successfully detect Unix sockets across Flatpak, Snap, and native Discord installations\.
- \*\*🔊 MPV Volume Control\*\* — Added a native `-v` / `--volume` flag and config setting to explicitly control MPV's launch volume\.
- \*\*⚡ Background Auto-Update Fix\*\* — Solved a critical bug where the invisible background updater would unexpectedly run the interactive shell installer and crash the terminal\.

---

## 📦 What's New in v2\.10\.0

- \*\*🚀 Massive Architecture Overhaul\*\* — The 4,000\+ line monolithic script has been successfully refactored into the `ani_sync` Python package, fixing namespace collisions and enabling better programmatic usage\.
- \*\*🛡️ Security Hardened Installers\*\* — The universal install script \(`install\.sh`\) no longer uses `--break-system-packages`, drops unrelated dependencies, and removes the stealth APT auto-update hook\.
- \*\*🧵 Thread-Safe Prefetching\*\* — Implementing a threading lock to prevent cache file corruption when rapidly skipping episodes\.
- \*\*🐛 Transparent Error Logging\*\* — Replaced silent failures with a standard `logging` framework, logging exceptions to debug so failures are no longer invisible\.
- \*\*🧹 Cleaned Packaging\*\* — Resolved duplicate Homebrew formulas and PKGBUILDs\. Switched CI/CD testing to `pytest` with `black` format enforcement\."""

changelog_new = """## 📦 Changelog & Recent Updates

<details>
<summary><b>✨ What's New in v2.10.x (Click to expand)</b></summary>

### v2.10.4
- **🐛 Fixed Configuration NameError Bug** — Fixed `NameError: name 'CONFIG' is not defined` when initializing volume options in `main()`.
- **🔊 Complete Volume Parameter Propagation** — Full end-to-end parameter passing for `-v` / `--volume` and configuration variables through `play_loop`, `turbo_play`, and `launch_player`.
- **💬 Expanded Discord IPC Socket Discovery** — Expanded Linux IPC socket paths to automatically detect **Vesktop**, **Discord Canary**, **Discord PTB**, **Snap**, and **Flatpak** instances.
- **🔄 Single Consolidated CI/CD Pipeline** — Consolidated multi-stage GitHub Actions workflows into a single `.github/workflows/workflow.yml` file.
- **🧹 Lint & Quality Audit** — Cleaned up all unused imports, fixed missing f-string placeholders, and added unit tests for player parameter signatures.

### v2.10.2
- **🎮 Fixed Discord Rich Presence** — Repaired the zero-dependency Discord IPC module to successfully detect Unix sockets across Flatpak, Snap, and native Discord installations.
- **🔊 MPV Volume Control** — Added a native `-v` / `--volume` flag and config setting to explicitly control MPV's launch volume.
- **⚡ Background Auto-Update Fix** — Solved a critical bug where the invisible background updater would unexpectedly run the interactive shell installer and crash the terminal.

### v2.10.0
- **🚀 Massive Architecture Overhaul** — The 4,000+ line monolithic script has been successfully refactored into the `ani_sync` Python package, fixing namespace collisions and enabling better programmatic usage.
- **🛡️ Security Hardened Installers** — The universal install script (`install.sh`) no longer uses `--break-system-packages`, drops unrelated dependencies, and removes the stealth APT auto-update hook.
- **🧵 Thread-Safe Prefetching** — Implementing a threading lock to prevent cache file corruption when rapidly skipping episodes.
- **🐛 Transparent Error Logging** — Replaced silent failures with a standard `logging` framework, logging exceptions to debug so failures are no longer invisible.
- **🧹 Cleaned Packaging** — Resolved duplicate Homebrew formulas and PKGBUILDs. Switched CI/CD testing to `pytest` with `black` format enforcement.

</details>"""
content = re.sub(changelog_old, changelog_new, content)

# 3. Add cool UI mockups/ascii art representation of the CLI UI
ui_old = r"""```text
  📺 ani-sync ❯ 🔍 Search: frieren
  ┌────────────────────────────────────────────────────────────────────────┐
  │ ▶  1\. Frieren: Beyond Journey's End \(28 Episodes\) \[720p/1080p\]         │
  │    2\. Frieren: Beyond Journey's End Season 2                           │
  │    3\. Sousou no Frieren \(Special Mini Anime\)                           │
  └────────────────────────────────────────────────────────────────────────┘
  ⚡ \[Turbo Swarm: 64 Sockets Active\] ──► \[RAM-Disk: /dev/shm\] ──► \[MPV: 0\.00s Delay\]
  ⏩ \[AniSkip: OP 01:25 - 02:55 Jump\] ──► \[Theme: TokyoNight TrueColor\]
  🔄 \[Cloud Sync: MAL ✓ \| AniList ✓ \| Kitsu ✓\] ──► \[Discord Presence: Active 🎮\]
```"""

ui_new = """<div align="center">
<pre><code>
  📺 <b style="color: #00E676;">ani-sync</b> ❯ 🔍 Search: <i style="color: #FFD700;">frieren</i>
  ╭────────────────────────────────────────────────────────────────────────╮
  │ <span style="color: #00E676;">▶</span>  1. Frieren: Beyond Journey's End (28 Episodes) [720p/1080p]         │
  │    2. Frieren: Beyond Journey's End Season 2                           │
  │    3. Sousou no Frieren (Special Mini Anime)                           │
  ╰────────────────────────────────────────────────────────────────────────╯
  ⚡ <b style="color: #00E676;">[Turbo Swarm: 64 Sockets Active]</b> ──► [RAM-Disk: /dev/shm] ──► <b style="color: #FFD700;">[MPV: 0.00s Delay]</b>
  ⏩ <b style="color: #FF6F00;">[AniSkip: OP 01:25 - 02:55 Jump]</b> ──► [Theme: TokyoNight TrueColor]
  🔄 <b style="color: #7C4DFF;">[Cloud Sync: MAL ✓ | AniList ✓ | Kitsu ✓]</b> ──► [Discord Presence: Active 🎮]
</code></pre>
</div>"""
content = re.sub(ui_old, ui_new, content)

# 4. Make Installation Section Interactive
install_regex = r"### 🪟 Windows \(One-Line PowerShell / Winget\).*?### ⚡ Standalone Pre-Compiled Binaries.*?\| 📦 \*\*Debian / Ubuntu\*\*.*?\n"
install_new = """### 🚀 Universal Installation

The installer scripts automatically detect your system package manager and install **ani-sync, FZF fuzzy search, MPV, yt-dlp, and Python dependencies** out of the box!

<details open>
<summary><b>🐧 Linux & 🍎 macOS (One-Line Universal Installer)</b></summary>
<br>

Run this single command in your terminal:
```bash
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | bash
```

To install system-wide into `/usr/local/bin`:
```bash
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | sudo bash
```
</details>

<details>
<summary><b>🪟 Windows (PowerShell / Winget)</b></summary>
<br>

Run this single command in **PowerShell** (Run as Administrator or standard User):
```powershell
irm https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.ps1 | iex
```
*Or install dependencies via Winget:*
```powershell
winget install Python.Python.3.12 junegunn.fzf mpv.net yt-dlp
```
</details>

<details>
<summary><b>📱 Android (Termux)</b></summary>
<br>

`ani-sync` runs natively on Android inside **Termux**! It automatically launches streaming video via MPV or the native Android MPV/VLC app:
```bash
# 1. Update Termux & install dependencies
pkg update && pkg install -y python mpv yt-dlp fzf curl git termux-api

# 2. Install ani-sync
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | bash

# 3. Stream in low-memory mobile mode
ani-sync "frieren" --lite
```
</details>

<details>
<summary><b>📦 Linux Package Managers (AUR, .deb, .rpm)</b></summary>
<br>

**Arch Linux (AUR):**
```bash
yay -S ani-sync
```

**Debian / Ubuntu (.deb):**
```bash
curl -LO https://github.com/idrisharis12/ani-sync/releases/latest/download/ani-sync_2.7.0_all.deb
sudo apt install -y ./ani-sync_2.7.0_all.deb
```

**Fedora / RHEL / openSUSE:**
```bash
sudo dnf install -y python3 python3-requests python3-tqdm mpv yt-dlp fzf curl
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | sudo bash
```
</details>

<details>
<summary><b>⚡ Standalone Pre-Compiled Binaries (No Python Required)</b></summary>
<br>

| OS / Architecture | Standalone Executable | One-Line Install Command |
| :--- | :--- | :--- |
| 🐧 **Linux (x86_64)** | [`ani-sync-linux-x86_64`](https://github.com/idrisharis12/ani-sync/releases/latest/download/ani-sync-linux-x86_64) | `sudo curl -fsSL https://github.com/idrisharis12/ani-sync/releases/latest/download/ani-sync-linux-x86_64 -o /usr/local/bin/ani-sync && sudo chmod +x /usr/local/bin/ani-sync` |
| 🪟 **Windows (x64)** | [`ani-sync-windows-x86_64.exe`](https://github.com/idrisharis12/ani-sync/releases/latest/download/ani-sync-windows-x86_64.exe) | `irm https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.ps1 \| iex` |
| 🍎 **macOS (Apple Silicon)** | [`ani-sync-macos-arm64`](https://github.com/idrisharis12/ani-sync/releases/latest/download/ani-sync-macos-arm64) | `sudo curl -fsSL https://github.com/idrisharis12/ani-sync/releases/latest/download/ani-sync-macos-arm64 -o /usr/local/bin/ani-sync && sudo chmod +x /usr/local/bin/ani-sync` |
</details>
"""
content = re.sub(install_regex, install_new, content, flags=re.DOTALL)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

print("README updated successfully.")
