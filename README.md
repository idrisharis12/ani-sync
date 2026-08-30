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
- [✨ Features](#-features)
- [⚡ How It Works: The Turbo Speed Architecture](#-how-it-works-the-turbo-speed-architecture)
- [📦 Installation](#-installation)
  - [Method 1: One-Line Installer (Recommended)](#method-1-one-line-installer-recommended)
  - [Method 2: Debian / Ubuntu Package (`.deb`)](#method-2-debian--ubuntu-package-deb)
  - [Method 3: Git Clone & Local Install](#method-3-git-clone--local-install)
  - [Method 4: Python Pip](#method-4-python-pip)
  - [Prerequisites & System Dependencies](#prerequisites--system-dependencies)
- [🚀 Detailed Usage & Examples](#-detailed-usage--examples)
  - [1. Search & Stream by Anime Name](#1-search--stream-by-anime-name)
  - [2. Seasons, Movies & Episode Selection](#2-seasons-movies--episode-selection)
  - [3. Video Quality Selection (720p, 1080p, etc.)](#3-video-quality-selection-720p-1080p-etc)
  - [4. Japanese Sub vs English Dub](#4-japanese-sub-vs-english-dub)
  - [5. Download Mode for Offline Viewing](#5-download-mode-for-offline-viewing)
  - [6. Interactive Playback Controls](#6-interactive-playback-controls)
  - [7. Custom Media Player](#7-custom-media-player)
- [🔄 Universal Auto-Updates](#-universal-auto-updates)
- [🔑 Step-by-Step MyAnimeList API Setup](#-step-by-step-myanimelist-api-setup)
- [💖 Credits & Acknowledgements](#-credits--acknowledgements)
- [📄 License](#-license)

---

## ✨ Features

- ⚡ **64x Multi-Connection Turbo Speed**: Downloads 64 video fragments simultaneously in parallel, saturating your full Wi-Fi / fiber connection and downloading episodes in ~3–5 seconds.
- 🚀 **100% Zero-Buffering Local Playback**: Never experience pauses, stutters, or 30-second buffering freezes mid-video.
- 💾 **RAM-Disk In-Memory Caching (`/dev/shm`)**: On Linux, streams are cached directly to high-speed RAM (10,000+ MB/s) with zero SSD wear and 0ms disk latency.
- ⏩ **Dual-Episode Background Pre-Fetching**: While you watch Episode N, Episodes N+1 and N+2 are silently pre-cached in the background so next episodes load in **0.00 seconds**!
- 🔍 **Instant Anime Search**: Just run `ani-sync <anime name>` — interactive menu or direct episode jump.
- 🎬 **Seasons, OVAs & Movies**: Effortlessly switch between TV seasons, movies, and franchise entries.
- 🎯 **Multi-Resolution Picker**: Crisp 720p HD (instant default), 1080p Full HD, 480p, or 360p.
- 🔄 **Automatic MyAnimeList Sync**: Automatically records and increments watched episodes on your **MyAnimeList** profile upon playback finish.
- 🎮 **Post-Playback Controls**: Seamlessly navigate `[n]` Next, `[p]` Previous, `[r]` Replay, `[s]` Select Episode, `[q]` Change Quality, or `[S]` Change Season.
- 🔒 **Privacy-First**: No telemetry, and your API credentials stay strictly on your local machine (`~/.config/ani-sync/config.env`).

---

## ⚡ How It Works: The Turbo Speed Architecture

Traditional web scrapers and terminal anime players stream video sequentially using a single HTTP connection. When remote anime CDN servers throttle single-thread speeds to ~50 KB/s, playback freezes every 2–3 seconds.

`ani-sync` solves this with a **4-tier acceleration pipeline**:

```
[ Remote Stream ]
       │
       ▼  (64 Parallel Concurrent Sockets)
[ ⚡ Turbo Multi-Thread Swarm Engine ]
       │
       ▼  (10,000+ MB/s Zero Latency Transfer)
[ 💾 RAM Disk (/dev/shm) / Local Cache ] ◄── (Silent Pre-fetch of Next 2 Episodes in Background)
       │
       ▼  (Hardware Accelerated Decoding: Intel/AMD/Nvidia)
[ 🎬 MPV Player / Smooth Zero-Buffering Playback ]
       │
       ▼  (On Finished Playback)
[ 🔄 MyAnimeList Auto-Sync API ]
```

1. **64-Connection Swarm Engine (`yt-dlp -N 64 --concurrent-fragments 64`)**:
   Instead of downloading 1 chunk at a time, `ani-sync` requests 64 fragments simultaneously across multiple TCP sockets with 16MB socket buffers.
2. **RAM Disk In-Memory Storage (`/dev/shm`)**:
   Linux systems automatically utilize tmpfs RAM storage, eliminating disk read/write bottlenecks.
3. **GPU Hardware Decoding (`--hwdec=auto-safe`, `--profile=fast`)**:
   Offloads video decoding from CPU to your GPU, keeping CPU usage under 5% and preventing audio underruns or frame drops.
4. **Predictive Dual Pre-fetch**:
   While Episode 1 is playing, Episodes 2 and 3 are preloaded in the background.

---

## 📦 Installation

### Method 1: Linux / macOS One-Line Installer (Recommended)
Run this single command in your terminal to install `ani-sync` and all dependencies automatically:

```bash
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | bash
```

To install system-wide into `/usr/local/bin`:
```bash
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | sudo bash
```

---

### Method 2: Windows PowerShell One-Line Installer
Run this command in **PowerShell** (Run as Administrator or standard User):

```powershell
irm https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.ps1 | iex
```

---

### Method 3: Debian / Ubuntu Package (`.deb`)
Download and install the native Debian package:

```bash
curl -LO https://github.com/idrisharis12/ani-sync/releases/latest/download/ani-sync_2.0.0_all.deb
sudo apt install -y ./ani-sync_2.0.0_all.deb
```

---

### Method 4: Git Clone & Local Install
```bash
git clone https://github.com/idrisharis12/ani-sync.git
cd ani-sync
chmod +x install.sh
./install.sh
```

Or on Windows PowerShell:
```powershell
git clone https://github.com/idrisharis12/ani-sync.git
cd ani-sync
.\install.ps1
```

---

### Method 5: Python Pip (Cross-Platform)
```bash
pip install --user git+https://github.com/idrisharis12/ani-sync.git
```

---

### Prerequisites & System Dependencies

`ani-sync` requires **Python 3.8+**, **`yt-dlp`**, and **`mpv`** (or VLC).

#### 🪟 Windows (Winget or Scoop)
```powershell
# Using Winget (Built-in on Windows 10/11)
winget install Python.Python.3.12 mpv.net yt-dlp

# Or using Scoop
scoop install python mpv yt-dlp
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

## 🚀 Detailed Usage & Examples

### 1. Search & Stream by Anime Name
Simply pass the name of the anime:

```bash
ani-sync "frieren"
```
Or start an interactive search prompt:
```bash
ani-sync
```

---

### 2. ⏪ Smart Resume & Continue Watching
Resume your last watched anime with a single command (automatically plays the next episode):

```bash
ani-sync continue
# or
ani-sync -c
```

---

### 3. 🔥 Browse Top Airing & Trending Anime
Browse currently airing and top trending anime without typing a search query:

```bash
ani-sync trending
# or
ani-sync -t
```

---

### 4. 📺 View & Resume from Watch History
Browse and pick from your recent watch history:

```bash
ani-sync history
```

---

### 5. Seasons, Movies & Episode Selection
If an anime has multiple seasons or movies (e.g. *Attack on Titan*, *Demon Slayer*, *Jujutsu Kaisen*), `ani-sync` presents a clean interactive menu:

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

### 6. Video Quality Selection (720p, 1080p, etc.)
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

### 4. Japanese Sub vs English Dub
By default, episodes are streamed in **Japanese audio with Subtitles**. To stream English Dubs:

```bash
ani-sync "solo leveling" --dub
```

---

### 5. Download Mode for Offline Viewing
Download episodes directly to your disk without launching the media player using `-d` / `--download`:

```bash
# Download Episode 1 of Jujutsu Kaisen
ani-sync "jujutsu kaisen" -e 1 -d
```

---

### 6. Interactive Playback Controls
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

### 7. Custom Media Player
`ani-sync` defaults to `mpv` with hardware acceleration, but you can specify VLC or IINA:

```bash
# Using VLC
ani-sync "death note" --player vlc

# Using IINA (macOS)
ani-sync "spy x family" --player iina
```

---

## 🔄 Universal Auto-Updates

`ani-sync` stays up-to-date automatically across all Linux distributions and macOS:

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

Credentials are saved in `~/.config/ani-sync/config.env`:

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
