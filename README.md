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

## 🔑 Step-by-Step MyAnimeList API Setup

To enable auto-syncing with your MyAnimeList account, create a free personal API Client ID on MyAnimeList:

### Step 1: Create an Application on MyAnimeList
1. Log in to [MyAnimeList.net](https://myanimelist.net/).
2. Go to the **MAL API Developer Portal**: [https://myanimelist.net/apiconfig](https://myanimelist.net/apiconfig).
3. Click on **"Create ID"**.
4. Fill in the form:
   | Field | Value | Notes |
   | :--- | :--- | :--- |
   | **App Name** | `ani-sync` | Name of your client |
   | **App Type** | `other` | Select `other` from the dropdown |
   | **App Redirect URL** | `http://localhost` | **Must be exact** for OAuth redirect |
   | **Description** | `CLI anime tracker and streamer` | Brief description |
   | **Commercial Use** | `No` | Select No |
   | **Terms of Service** | `Checked` | Agree to terms |
5. Click **"Submit"** and copy your **Client ID**.

---

### Step 2: Generate Authentication Tokens

Run the interactive setup wizard:
```bash
ani-sync auth
```

1. Enter your **Client ID** when prompted.
2. Your browser will open the MAL authorization page. Click **"Allow"**.
3. You will be redirected to an address like `http://localhost/?code=AUTHORIZATION_CODE`.
4. Copy the URL or code from your address bar and paste it into the terminal.
5. `ani-sync` will exchange the code for tokens and save them securely in:
   ```
   ~/.config/ani-sync/config.env
   ```

---

### Step 3: Manual Environment Variables (Optional)
You can also manually export credentials in `~/.bashrc` or `~/.zshrc`:

```bash
export MAL_CLIENT_ID="your_client_id_here"
export MAL_CLIENT_SECRET=""   # Optional
export MAL_REFRESH_TOKEN="your_refresh_token_here"
```

---

## 💖 Credits & Acknowledgements

Special thanks and huge credit to the amazing open-source projects and authors that inspired and paved the way for `ani-sync`:

- **[ani-cli](https://github.com/pystardust/ani-cli)** by *pystardust* — The groundbreaking CLI anime player that pioneered command-line streaming and scraping workflows.
- **[mal-cli](https://github.com/mdomke/mal-cli)** by *mdomke* — The pioneering command-line interface for MyAnimeList that inspired terminal tracking and synchronization.

---

## 📄 License
Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more details.
