<p align="center">
  <img src="assets/ani-sync_logo.jpeg" alt="ani-sync logo" width="280" />
</p>

<h1 align="center">ani-sync</h1>

<p align="center">
  <b>Stream anime from your terminal with 64x multi-connection turbo speed and automatically sync watch progress to MyAnimeList.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/Speed-64x%20Turbo-brightgreen" alt="64x Turbo Speed" />
  <img src="https://img.shields.io/badge/Buffer-Zero--Buffering-success" alt="Zero Buffering" />
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-informational" alt="Platform" />
</p>

---

## 📖 Table of Contents
- [✨ Core Features](#-core-features)
- [⚡ How It Works: The Turbo Speed Architecture](#-how-it-works-the-turbo-speed-architecture)
- [📦 Installation](#-installation)
  - [🪟 Windows (PowerShell / Winget / Scoop)](#-windows-powershell--winget--scoop)
  - [🐧 Linux & 🍎 macOS (One-Line Curl Installer)](#-linux--macos-one-line-curl-installer)
  - [🏹 Arch Linux (AUR / PKGBUILD)](#-arch-linux-aur--pkgbuild)
  - [📦 Debian / Ubuntu (`.deb`)](#-debian--ubuntu-deb)
  - [🐍 Python Pip (Cross-Platform)](#-python-pip-cross-platform)
  - [Prerequisites & System Dependencies](#prerequisites--system-dependencies)
- [🚀 Detailed Usage & Feature Guide](#-detailed-usage--feature-guide)
  - [1. Search & Stream by Anime Name](#1-search--stream-by-anime-name)
  - [2. ⏪ Smart Resume & Continue Watching (`-c`)](#2--smart-resume--continue-watching--c)
  - [3. 🔥 Top Airing & Trending Anime (`-t`)](#3--top-airing--trending-anime--t)
  - [4. 📺 View & Manage Watch History](#4--view--manage-watch-history)
  - [5. 🎬 Seasons, Movies & Episode Selection](#5--seasons-movies--episode-selection)
  - [6. 🎯 Multi-Resolution Quality Selection (1080p, 720p, etc.)](#6--multi-resolution-quality-selection-1080p-720p-etc)
  - [7. 🎙️ Japanese Subtitles vs English Dub (`--dub`)](#7-️-japanese-subtitles-vs-english-dub---dub)
  - [8. 📥 High-Speed Offline Download Mode (`-d`)](#8--high-speed-offline-download-mode--d)
  - [9. 🎮 Interactive Post-Playback Controls](#9--interactive-post-playback-controls)
  - [10. 🎧 Custom Media Player Support](#10--custom-media-player-support)
  - [11. 💬 Discord Rich Presence Integration](#11--discord-rich-presence-integration)
- [📋 CLI Cheat Sheet & Flag Reference](#-cli-cheat-sheet--flag-reference)
- [🔄 Universal Auto-Updates](#-universal-auto-updates)
- [🔑 Step-by-Step MyAnimeList API Setup](#-step-by-step-myanimelist-api-setup)
- [💖 Credits & Acknowledgements](#-credits--acknowledgements)
- [📄 License](#-license)

---

## ✨ Core Features

| Feature | Description |
| :--- | :--- |
| ⚡ **64x Turbo Swarm Engine** | Requests **64 video fragments simultaneously in parallel**, downloading full episodes in **~3–5 seconds** and saturating your full Wi-Fi/fiber line speed. |
| 🚀 **100% Zero-Buffering Playback** | Plays from local fast storage — eliminates all stutter, mid-video pauses, and 30-second buffering freezes. |
| 💾 **RAM-Disk Caching (`/dev/shm`)** | Automatically utilizes Linux tmpfs shared memory at **10,000+ MB/s** for 0ms seek latency and 0 SSD wear. |
| ⏩ **Dual-Episode Pre-Fetching** | Silently preloads Episodes N+1 and N+2 in the background so next episodes start in **0.00s instantly**. |
| 🔄 **Automatic MyAnimeList Sync** | Automatically updates and increments your watched episode count on **MyAnimeList** via the official OAuth2 API upon finishing an episode. |
| ⏪ **Smart Continue Watching** | Run `ani-sync continue` to resume right where you left off. |
| 🔥 **Trending & Airing Browser** | Run `ani-sync trending` to instantly pick from the top currently airing and popular anime. |
| 🎬 **Seasons, OVAs & Movies** | Seamlessly navigate through multiple seasons, spin-offs, and movies in a single franchise. |
| 🎯 **Multi-Resolution Picker** | Choose between 720p HD (instant zero-buffer default), 1080p Full HD, 480p, and 360p. |
| 📥 **Offline Download Mode** | Pass `-d` / `--download` to save complete episodes locally without opening the player. |
| 🪟 **Cross-Platform Native Support** | Works out of the box on **Windows (PowerShell/CMD)**, **Linux**, and **macOS**. |
| 💬 **Discord Rich Presence** | Automatically broadcasts what anime and episode you are enjoying to your Discord profile in real-time. |
| 🔒 **100% Privacy & Security** | Zero telemetry, zero external trackers, and your API credentials remain strictly on your local machine. |

---

## ⚡ How It Works: The Turbo Speed Architecture

Traditional web scrapers and terminal anime players stream video sequentially using a single HTTP connection. When remote anime CDN servers throttle single-thread speeds to ~50 KB/s, playback freezes every 2–3 seconds.

`ani-sync` solves this with a **4-tier acceleration pipeline**:

```
[ Remote HLS Stream ]
       │
       ▼  (64 Parallel Concurrent Sockets — Max Network Pipe Saturation)
[ ⚡ Turbo Multi-Thread Swarm Engine ]
       │
       ▼  (10,000+ MB/s RAM-to-RAM Bus Transfer)
[ 💾 RAM Disk (/dev/shm) / Local Cache ] ◄── (Silent Pre-fetch of Next 2 Episodes in Background)
       │
       ▼  (GPU Hardware Acceleration: Intel VAAPI / AMD / NVDEC)
[ 🎬 MPV Player / Smooth Zero-Buffering Playback ]
       │
       ▼  (On Finished Playback)
[ 🔄 MyAnimeList Auto-Sync API ]
```

1. **64-Connection Swarm Engine (`yt-dlp -N 64 --concurrent-fragments 64`)**:
   Instead of downloading 1 chunk at a time, `ani-sync` requests 64 fragments simultaneously across multiple TCP sockets with 16MB socket buffers.
2. **RAM Disk In-Memory Storage (`/dev/shm`)**:
   Linux systems automatically utilize tmpfs RAM storage, eliminating disk read/write bottlenecks.
3. **GPU Hardware Decoding (`--hwdec=auto-safe`, `--profile=fast`, `--audio-buffer=0.8`)**:
   Offloads video decoding from CPU to your GPU, keeping CPU usage under 5% and preventing audio underruns or frame drops.
4. **Predictive Dual Pre-fetch**:
   While Episode 1 is playing, Episodes 2 and 3 are preloaded in the background.

---

## 📦 Installation

### 🪟 Windows (PowerShell / Winget / Scoop)
Run this single command in **PowerShell** (Run as Administrator or standard User):

```powershell
irm https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.ps1 | iex
```

*Or install dependencies via Winget:*
```powershell
winget install Python.Python.3.12 mpv.net yt-dlp
```

---

### 🐧 Linux & 🍎 macOS (One-Line Curl Installer)
Run this single command in your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | bash
```

To install system-wide into `/usr/local/bin`:
```bash
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | sudo bash
```

---

### 🏹 Arch Linux (AUR / PKGBUILD)
```bash
# Using yay or paru
yay -S ani-sync

# Or build manually with makepkg
git clone https://github.com/idrisharis12/ani-sync.git
cd ani-sync
makepkg -si
```

---

### 📦 Debian / Ubuntu (`.deb`)
Download and install the native Debian package:

```bash
curl -LO https://github.com/idrisharis12/ani-sync/releases/latest/download/ani-sync_2.0.0_all.deb
sudo apt install -y ./ani-sync_2.0.0_all.deb
```

---

### 🐍 Python Pip (Cross-Platform)
```bash
pip install --user git+https://github.com/idrisharis12/ani-sync.git
```

---

### Prerequisites & System Dependencies

`ani-sync` requires **Python 3.8+**, **`yt-dlp`**, and **`mpv`** (or VLC).

#### 🪟 Windows (Winget or Scoop)
```powershell
winget install Python.Python.3.12 mpv.net yt-dlp
# Or using Scoop: scoop install python mpv yt-dlp
```

#### 🏹 Arch Linux / Manjaro
```bash
sudo pacman -S python python-pip git mpv yt-dlp curl
pip install --user requests tqdm
```

#### 🐧 Ubuntu / Debian / Pop!_OS / Mint
```bash
sudo apt update
sudo apt install -y python3 python3-pip git mpv yt-dlp curl
pip install --user requests tqdm
```

#### 🎩 Fedora / RHEL
```bash
sudo dnf install -y python3 python3-pip git mpv yt-dlp curl
pip install --user requests tqdm
```

#### 🍎 macOS (Homebrew)
```bash
brew install python mpv yt-dlp curl
pip3 install requests tqdm
```

---

## 🚀 Detailed Usage & Feature Guide

### 1. Search & Stream by Anime Name
Search for any anime title directly from your terminal:

```bash
ani-sync "frieren"
ani-sync "attack on titan"
ani-sync "jujutsu kaisen"
```
Or start an interactive search prompt:
```bash
ani-sync
```

---

### 2. ⏪ Smart Resume & Continue Watching (`-c`)
Quickly jump back into the anime you were last watching. `ani-sync` automatically tracks your progress and starts the **next episode**:

```bash
ani-sync continue
# or
ani-sync -c
```

---

### 3. 🔥 Top Airing & Trending Anime (`-t`)
Browse and watch currently airing seasonal anime without typing a search query:

```bash
ani-sync trending
# or
ani-sync -t
```

---

### 4. 📺 View & Manage Watch History
Review your recently watched anime and choose any entry to instantly resume:

```bash
ani-sync history
```

---

### 5. 🎬 Seasons, Movies & Episode Selection
When searching a franchise with multiple seasons, movies, or OVAs, `ani-sync` displays a clean selection menu:

```
Seasons & Movies for 'Attack on Titan':
-------------------------------------
  [1] Attack on Titan (Season 1)
  [2] Attack on Titan Season 2
  [3] Attack on Titan Season 3
  [4] Attack on Titan: The Final Season
  [5] Attack on Titan Movie: Chronicle

Select [1-5] (default: 1):
```

You can jump straight to a specific episode using the `-e` / `--episode` flag:
```bash
ani-sync "naruto shippuden" -e 167
```

---

### 6. 🎯 Multi-Resolution Quality Selection (1080p, 720p, etc.)
By default, `ani-sync` streams in **720p HD** for zero-buffering instant start. You can specify any desired resolution with `-q`:

```bash
# Stream in 1080p Full HD
ani-sync "chainsaw man" -q 1080p

# Stream in 720p HD (Default)
ani-sync "one piece" -q 720p

# Stream in 480p SD (for slower connections)
ani-sync "bleach" -q 480p
```

---

### 7. 🎙️ Japanese Subtitles vs English Dub (`--dub`)
By default, episodes are streamed in **Japanese audio with Subtitles**. To stream English Dubs:

```bash
ani-sync "solo leveling" --dub
```

---

### 8. ⏩ Auto-Skip Anime Opening & Ending (`--skip`)
Never sit through 90 seconds of anime intros or spoilers again:

- **Automatic Skip Mode**: Pass `--skip` or `--auto-skip` to automatically fast-forward past the opening intro (+85 seconds):
  ```bash
  ani-sync "frieren" --skip
  ```
- **In-Player Shortcuts (Interactive)**: During playback in MPV, you can skip anytime:
  - Press **`Tab`** or **`i`**: Instantly skip Opening / Intro (+85 seconds forward).
  - Press **`o`**: Instantly skip Outro / Ending (+85 seconds forward).

---

### 9. 📥 High-Speed Offline Download Mode (`-d`)
Download episodes directly to your disk with 64x multi-connection acceleration without launching the media player:

```bash
# Download Episode 1 of Jujutsu Kaisen
ani-sync "jujutsu kaisen" -e 1 -d
```

---

### 10. 🎮 Interactive Post-Playback Controls
When an episode finishes (or when you exit the media player), `ani-sync` updates your MyAnimeList progress and displays an interactive control loop:

```
------------------- Playback Controls -------------------
  [n] Next Ep (2)  |  [r] Replay Ep 1  |  [p] Previous Ep  |  [s] Select Episode  |  [q] Change Quality  |  [S] Change Season/Movie  |  [x] Quit
Choice:
```
- Press **`Enter`** or **`n`**: Play the next episode (starts in **0.00s** due to background pre-fetching).
- Press **`r`**: Replay the current episode.
- Press **`p`**: Go back to the previous episode.
- Press **`s`**: Pick another episode from the list.
- Press **`q`**: Switch video resolution (e.g. 720p / 1080p).
- Press **`S`**: Switch to a different season or movie in the franchise.
- Press **`x`**: Exit the application.

---

### 11. 🎧 Custom Media Player Support
`ani-sync` defaults to `mpv` with hardware acceleration, but you can specify VLC or IINA:

```bash
# Using VLC
ani-sync "death note" --player vlc

# Using IINA (macOS)
ani-sync "spy x family" --player iina
```

---

### 12. 💬 Discord Rich Presence Integration
`ani-sync` automatically connects to your local Discord desktop app via IPC and displays your watch activity in real-time:
> **Watching Frieren: Beyond Journey's End**  
> *Episode 5 • 12:45 elapsed*

> [!NOTE]
> Ensure **"Display current activity as a status message"** is enabled in your Discord Settings (`User Settings` -> `Activity Privacy`).  
> You can also specify a custom Discord Application ID by setting `export DISCORD_CLIENT_ID="YOUR_ID"` in `~/.config/ani-sync/config.env`.

---

## 📋 CLI Cheat Sheet & Flag Reference

| Command / Flag | Description | Example |
| :--- | :--- | :--- |
| `ani-sync <title>` | Search and stream anime by title | `ani-sync "frieren"` |
| `ani-sync -c`, `continue` | Resume last watched anime | `ani-sync continue` |
| `ani-sync -t`, `trending` | Browse top trending / airing anime | `ani-sync trending` |
| `ani-sync history` | Browse and resume from watch history | `ani-sync history` |
| `--skip`, `--auto-skip` | Automatically skip anime opening/intro (+85s) | `ani-sync "one piece" --skip` |
| `-e, --episode <num>` | Jump directly to specific episode number | `ani-sync "naruto" -e 50` |
| `-q, --quality <res>` | Preferred video resolution (`1080p`, `720p`, `480p`) | `ani-sync "one piece" -q 1080p` |
| `-d, --download` | Download episode locally without playing | `ani-sync "jujutsu kaisen" -e 1 -d` |
| `--dub` | Stream English Dubbed version | `ani-sync "solo leveling" --dub` |
| `--direct` | Stream directly without local caching | `ani-sync "frieren" --direct` |
| `--player <player>` | Media player binary (`mpv`, `vlc`, `iina`) | `ani-sync "bleach" --player vlc` |
| `ani-sync update`, `-U` | Check and update to latest version | `ani-sync update` |
| `ani-sync auth` | Launch MyAnimeList OAuth2 setup wizard | `ani-sync auth` |
| `-h, --help` | Display CLI help menu | `ani-sync --help` |
| `ani-sync history` | Browse and resume from watch history | `ani-sync history` |
| `-e, --episode <num>` | Jump directly to specific episode number | `ani-sync "naruto" -e 50` |
| `-q, --quality <res>` | Preferred video resolution (`1080p`, `720p`, `480p`) | `ani-sync "one piece" -q 1080p` |
| `-d, --download` | Download episode locally without playing | `ani-sync "jujutsu kaisen" -e 1 -d` |
| `--dub` | Stream English Dubbed version | `ani-sync "solo leveling" --dub` |
| `--direct` | Stream directly without local caching | `ani-sync "frieren" --direct` |
| `--player <player>` | Media player binary (`mpv`, `vlc`, `iina`) | `ani-sync "bleach" --player vlc` |
| `ani-sync update`, `-U` | Check and update to latest version | `ani-sync update` |
| `ani-sync auth` | Launch MyAnimeList OAuth2 setup wizard | `ani-sync auth` |
| `-h, --help` | Display CLI help menu | `ani-sync --help` |

---

## 🔄 Universal Auto-Updates

`ani-sync` stays up-to-date automatically across all Linux distributions, macOS, and Windows:

1. **Background Auto-Sync**: Whenever you run `ani-sync`, it silently checks GitHub for updates in a non-blocking background thread.
2. **Manual Update Command**:
   ```bash
   ani-sync update
   # or
   ani-sync -U
   ```
3. **APT Package Manager Integration**:
   On Debian/Ubuntu systems, `sudo apt update && sudo apt upgrade` automatically updates `ani-sync`.

---

## 🔑 Step-by-Step MyAnimeList API Setup (Complete Walkthrough)

To enable automatic episode tracking and syncing with your MyAnimeList account, you need a free personal API Client ID from MyAnimeList.

### Step 1: Open the Developer Portal & Create an App ID
1. Log in to your account on [MyAnimeList.net](https://myanimelist.net/).
2. Open the **API Developer Portal**: [https://myanimelist.net/apiconfig](https://myanimelist.net/apiconfig).
3. Click the **"Create ID"** (or **"Create an App"**) button.

### Step 2: Fill in the Application Form
Fill in each field exactly as described below:

| Field Name | Value to Enter | Notes |
| :--- | :--- | :--- |
| **App Name** | `ani-sync` | Name of your personal client |
| **App Type** | `other` | Select `other` from the dropdown menu |
| **App Redirect URL** | `http://localhost` | **Must be exact** (use `http://`, not `https://`) |
| **Homepage URL** | `https://github.com/idrisharis12/ani-sync/` | *Include the trailing slash `/`* |
| **App Description** | *(See copy-paste text below)* | Detailed description required by MAL |
| **Commercial use?** | `No` | Select No |
| **Non-commercial use?** | `Yes` | Select Yes |
| **Terms of Service** | `Checked` | Check the box to agree to API terms |

> **📋 Copy-Paste Description for MAL:**
> ```
> ani-sync is an open-source command-line tool built for personal use that allows users to stream anime episodes directly in their terminal and automatically sync watched episode numbers, watch history, and anime status to their MyAnimeList profile using the official MyAnimeList OAuth 2.0 API.
> ```

4. Click **"Submit"** at the bottom of the form.
5. Copy your **`Client ID`** (and optional `Client Secret`).

---

### Step 3: Run the Terminal Setup Wizard

In your terminal, run:
```bash
ani-sync auth
```

1. Paste your **Client ID** (and Client Secret if requested).
2. `ani-sync` opens the authorization URL in your web browser.
3. Log in (if prompted) and click **"Allow"**.
4. You will be redirected to an address like:
   ```
   http://localhost/?code=EXAMPLE_AUTHORIZATION_CODE_HERE...
   ```
   > [!NOTE]
   > Your browser may display **"This site can’t be reached"**. **This is completely normal** because no local server is running. The authorization code is directly inside your browser's **URL address bar**!

5. Copy the entire URL (or the string after `code=`) from your address bar.
6. Paste it into your terminal prompt and press `Enter`.
7. `ani-sync` exchanges the code for tokens and saves them automatically to:
   ```
   ~/.config/ani-sync/config.env
   ```

---

### Configuration File Format

Credentials are saved in `~/.config/ani-sync/config.env` (or `%APPDATA%\ani-sync\config.env` on Windows):

```bash
# Example ~/.config/ani-sync/config.env
export MAL_CLIENT_ID="example_client_id_123456"
export MAL_CLIENT_SECRET="example_client_secret_abcdef"  # Optional
export MAL_REFRESH_TOKEN="example_refresh_token_xyz789"
```

---

## 💖 Credits & Acknowledgements

Special thanks and credit to the open-source projects that inspired `ani-sync`:

- **[ani-cli](https://github.com/pystardust/ani-cli)** by *pystardust* — The groundbreaking CLI anime player that pioneered command-line streaming.
- **[mal-cli](https://github.com/mdomke/mal-cli)** by *mdomke* — The pioneering command-line interface for MyAnimeList tracking.

---

## 📄 License
Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more details.

