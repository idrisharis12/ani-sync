<p align="center">
  <img src="assets/ani-sync_logo.jpeg" alt="ani-sync logo" width="280" />
</p>

<h1 align="center">ani-sync</h1>

<p align="center">
  <b>Stream anime from your terminal and automatically sync watch progress to MyAnimeList.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.8+" />
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT" />
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-informational" alt="Platform" />
</p>

---

## 📖 Table of Contents
- [✨ Features](#-features)
- [📦 Installation](#-installation)
  - [Method 1: One-Line Installer (Recommended)](#method-1-one-line-installer-recommended)
  - [Method 2: Git Clone & Local Install](#method-2-git-clone--local-install)
  - [Method 3: Python Pip](#method-3-python-pip)
  - [Prerequisites & System Dependencies](#prerequisites--system-dependencies)
- [🚀 Detailed Usage](#-detailed-usage)
  - [1. Search & Stream by Anime Name](#1-search--stream-by-anime-name)
  - [2. Seasons, Movies & Episode Selection](#2-seasons-movies--episode-selection)
  - [3. Video Quality Selection (720p, 1080p, etc.)](#3-video-quality-selection-720p-1080p-etc)
  - [4. Japanese Sub vs English Dub](#4-japanese-sub-vs-english-dub)
  - [5. Interactive Playback Controls](#5-interactive-playback-controls)
  - [6. Custom Media Player](#6-custom-media-player)
- [🔑 Step-by-Step MyAnimeList API Setup](#-step-by-step-myanimelist-api-setup)
  - [Step 1: Create an Application on MyAnimeList](#step-1-create-an-application-on-myanimelist)
  - [Step 2: Generate Authentication Tokens](#step-2-generate-authentication-tokens)
  - [Step 3: Manual Environment Variables (Optional)](#step-3-manual-environment-variables-optional)
- [💖 Credits & Acknowledgements](#-credits--acknowledgements)
- [📄 License](#-license)

---

## ✨ Features
- 🔍 **Instant Anime Search**: Just run `ani-sync <anime name>` — no need to copy and paste stream URLs.
- 🎬 **Seasons & Movies**: Effortlessly switch between TV seasons, movies, OVAs, and specials.
- 🎯 **Resolution Selection**: Stream in 1080p, 720p, 480p, or 360p with the `-q` flag or interactive menu.
- 🔄 **Automatic MAL Sync**: Automatically records and updates your watched episodes on **MyAnimeList** as soon as playback finishes.
- 🎮 **Playback Controls**: Intuitive post-playback loop allowing you to seamlessly go to **[n] Next**, **[p] Previous**, **[r] Replay**, **[s] Select Episode**, or **[S] Change Season**.
- ⚡ **1-Command OAuth Setup**: Interactive `ani-sync auth` wizard connects your MyAnimeList account in seconds.
- 🔒 **Secure**: API credentials are saved locally in your own machine (`~/.config/ani-sync/config.env`).

---

## 📦 Installation

### Method 1: One-Line Installer (Recommended)
Run this command in your terminal to install `ani-sync` and all dependencies automatically:

```bash
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | bash
```

To install system-wide into `/usr/local/bin`:
```bash
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | sudo bash
```

---

### Method 2: Git Clone & Local Install
```bash
git clone https://github.com/idrisharis12/ani-sync.git
cd ani-sync
chmod +x install.sh
./install.sh
```

Or using `make`:
```bash
sudo make install
```

---

### Method 3: Python Pip
```bash
pip install --user git+https://github.com/idrisharis12/ani-sync.git
```

---

### Prerequisites & System Dependencies

`ani-sync` requires **Python 3.8+** and a media player (default is **`mpv`**).

#### 🐧 Ubuntu / Debian / Pop!_OS / Mint
```bash
sudo apt update
sudo apt install -y python3 python3-pip git mpv curl
pip install --user requests tqdm
```

#### 🏹 Arch Linux / Manjaro
```bash
sudo pacman -S python python-pip git mpv curl
pip install --user requests tqdm
```

#### 🎩 Fedora / RHEL
```bash
sudo dnf install -y python3 python3-pip git mpv curl
pip install --user requests tqdm
```

#### 🍎 macOS (Homebrew)
```bash
brew install python mpv curl
pip3 install requests tqdm
```

---

## 🚀 Detailed Usage

### 1. Search & Stream by Anime Name
Simply supply the name of the anime:

```bash
ani-sync "frieren"
```
Or start an interactive search prompt:
```bash
ani-sync
```

`ani-sync` automatically queries the best sources, fetches available seasons and episodes, and launches your player.

---

### 2. Seasons, Movies & Episode Selection
If an anime has multiple seasons or movies (e.g. *Attack on Titan*, *Demon Slayer*, *Jujutsu Kaisen*), `ani-sync` will present a clean selection menu:

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

### 3. Video Quality Selection (720p, 1080p, etc.)
Specify your desired resolution using the `-q` / `--quality` flag:

```bash
# Stream in 1080p Full HD
ani-sync "chainsaw man" -q 1080p

# Stream in 720p HD
ani-sync "one piece" -q 720p

# Stream in 480p SD (for slower connections)
ani-sync "bleach" -q 480p
```
*If a requested resolution is not available, it will automatically fallback to the highest available quality.*

---

### 4. Japanese Sub vs English Dub
By default, episodes are streamed in **Japanese audio with Subtitles**. To stream English Dubs:

```bash
ani-sync "solo leveling" --dub
```

---

### 5. Interactive Playback Controls
When an episode ends (or when you close the media player), `ani-sync` syncs your progress to MyAnimeList and presents an interactive action menu:

```
------------------- Playback Controls -------------------
  [n] Next Ep (2)  |  [r] Replay Ep 1  |  [p] Previous Ep  |  [s] Select Episode  |  [q] Change Quality  |  [S] Change Season/Movie  |  [x] Quit
Choice:
```
- Press **`Enter`** or **`n`**: Play the next episode.
- Press **`r`**: Replay the current episode.
- Press **`p`**: Go back to the previous episode.
- Press **`s`**: Pick another episode from the list.
- Press **`q`**: Switch video resolution (e.g. 720p / 1080p).
- Press **`S`**: Switch to a different season or movie in the franchise.
- Press **`x`**: Exit the application.

---

### 6. Custom Media Player
`ani-sync` defaults to `mpv` with full subtitle styling, but you can specify VLC, IINA, or any player of your choice:

```bash
# Using VLC
ani-sync "death note" --player vlc

# Using IINA (macOS)
ani-sync "spy x family" --player iina
```

---

## 🔑 Step-by-Step MyAnimeList API Setup (Complete Walkthrough)

To enable automatic episode tracking and syncing with your MyAnimeList account, you need a free personal API Client ID from MyAnimeList. Follow this exact walkthrough:

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
| **Homepage URL** | `https://github.com/idrisharis12/ani-sync/` | *Include the trailing slash `/` or MAL will say invalid* |
| **App Description** | *(See copy-paste text below)* | MAL requires a detailed description |
| **Commercial use?** | `No` | Select No |
| **Non-commercial use?** | `Yes` | Select Yes |
| **Terms of Service** | `Checked` | Check the box to agree to API terms |

> **📋 Copy-Paste Description for MAL:**
> ```
> ani-sync is an open-source command-line tool built for personal use that allows users to stream anime episodes directly in their terminal and automatically sync watched episode numbers, watch history, and anime status to their MyAnimeList profile using the official MyAnimeList OAuth 2.0 API.
> ```

4. Click **"Submit"** at the bottom of the form.
5. Your newly created app details will appear. Copy your **`Client ID`** (and optional `Client Secret`).

---

### Step 3: Run the Terminal Setup Wizard

In your terminal, run:
```bash
ani-sync auth
```

1. Paste your **Client ID** (and Client Secret if requested).
2. `ani-sync` will open the authorization URL in your web browser.
3. Log in (if prompted) and click **"Allow"**.
4. You will be redirected to an address like:
   ```
   http://localhost/?code=def50200611fe883d9...
   ```
   > [!NOTE]
   > Your browser may display **"This site can’t be reached"** or **"Unable to connect"**. **This is completely normal** because no local server is running on your machine. The authorization code is located directly in your browser's **URL address bar**!

5. Copy the entire URL (or the long string after `code=`) from your browser address bar.
6. Paste it into your terminal prompt and press `Enter`.
7. `ani-sync` will exchange the authorization code for your tokens and save them to:
   ```
   ~/.config/ani-sync/config.env
   ```

---

### Step 4: Verification & Manual Environment Variables (Optional)
Once completed, `ani-sync` is ready to go! If you ever want to check or manually set your credentials in `~/.bashrc` or `~/.zshrc`:

```bash
export MAL_CLIENT_ID="your_client_id_here"
export MAL_CLIENT_SECRET=""   # Optional
export MAL_REFRESH_TOKEN="your_refresh_token_here"
```
Reload your shell with `source ~/.bashrc` or `source ~/.zshrc`.

---

## 💖 Credits & Acknowledgements

Special thanks and huge credit to the amazing open-source projects and authors that inspired and paved the way for `ani-sync`:

- **[ani-cli](https://github.com/pystardust/ani-cli)** by *pystardust* — The groundbreaking CLI anime player that pioneered command-line streaming and scraping workflows.
- **[mal-cli](https://github.com/mdomke/mal-cli)** by *mdomke* — The pioneering command-line interface for MyAnimeList that inspired terminal tracking and synchronization.

---

## 📄 License
Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more details.
