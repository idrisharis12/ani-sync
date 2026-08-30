<p align="center">
  <img src="assets/ani-sync_logo.jpeg" alt="ani-sync logo" width="280" />
</p>

<h1 align="center">ani-sync</h1>

<p align="center">
  <b>Stream anime from your terminal with <code>ani-cli</code> and automatically sync your watch progress to MyAnimeList (MAL).</b>
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
  - [Method 3: Python Pip / Pipx](#method-3-python-pip--pipx)
  - [Prerequisites & System Dependencies](#prerequisites--system-dependencies)
- [🔑 Step-by-Step MyAnimeList API Setup](#-step-by-step-myanimelist-api-setup)
  - [Step 1: Create an Application on MyAnimeList](#step-1-create-an-application-on-myanimelist)
  - [Step 2: Generate Authentication Tokens](#step-2-generate-authentication-tokens)
  - [Step 3: Manual Environment Variable Setup (Optional)](#step-3-manual-environment-variable-setup-optional)
- [🚀 Usage](#-usage)
  - [Basic Command](#basic-command)
  - [Custom Media Player](#custom-media-player)
- [💖 Credits & Acknowledgements](#-credits--acknowledgements)
- [📄 License](#-license)

---

## ✨ Features
- 🎬 **Terminal Streaming**: Instant anime playback directly from your command line using `ani-cli`.
- 🔄 **Auto Sync to MAL**: Automatically detects the anime title and episode, searching MyAnimeList and updating your episode count & list status immediately upon finishing.
- ⚡ **Easy 1-Command Auth**: Interactive `ani-sync auth` setup that completes OAuth2 PKCE without manual curl commands.
- 🔒 **Secure**: No hardcoded API keys; credentials stay stored safely in your personal environment or `~/.config/ani-sync/config.env`.
- 🎮 **Player Agnostic**: Default playback with `mpv`, with full support for `vlc`, `iina`, `celluloid`, and more.

---

## 📦 Installation

### Method 1: One-Line Installer (Recommended)
Run the following command in your Linux/macOS terminal to download, configure dependencies, and install `ani-sync` system-wide:

```bash
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | bash
```

To install system-wide into `/usr/local/bin`:
```bash
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | sudo bash
```

---

### Method 2: Git Clone & Local Install
Clone the repository and run the included installer:

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

### Method 3: Python Pip / Pipx
You can also install directly via Python's package manager:

```bash
# Install directly from GitHub
pip install --user git+https://github.com/idrisharis12/ani-sync.git

# Or locally from the cloned folder
pip install --user .
```

---

### Prerequisites & System Dependencies

`ani-sync` requires **Python 3.8+**, **`ani-cli`**, and a media player like **`mpv`**.

#### 🐧 Ubuntu / Debian / Pop!_OS / Linux Mint
```bash
sudo apt update
sudo apt install -y python3 python3-pip git mpv curl
pip install --user ani-cli requests tqdm
```

#### 🏹 Arch Linux / Manjaro
```bash
sudo pacman -S python python-pip git mpv curl
yay -S ani-cli-git python-requests python-tqdm
```

#### 🎩 Fedora / RHEL
```bash
sudo dnf install -y python3 python3-pip git mpv curl
pip install --user ani-cli requests tqdm
```

#### 🍎 macOS (Homebrew)
```bash
brew install python mpv ani-cli curl
pip3 install requests tqdm
```

---

## 🔑 Step-by-Step MyAnimeList API Setup

To enable auto-syncing with your MyAnimeList account, you need a free API Client ID from MyAnimeList.

### Step 1: Create an Application on MyAnimeList
1. Log in to your account on [MyAnimeList.net](https://myanimelist.net/).
2. Navigate to the **MAL API Developer Portal**: [https://myanimelist.net/apiconfig](https://myanimelist.net/apiconfig).
3. Click on **"Create ID"** (or **"Edit"** if modifying an existing client).
4. Fill in the required fields with the following details:
   | Field | Value | Notes |
   | :--- | :--- | :--- |
   | **App Name** | `ani-sync` | Name of your personal client |
   | **App Type** | `other` | Select `other` from the dropdown |
   | **App Redirect URL** | `http://localhost` | **Must be exact** for OAuth redirect |
   | **Description** | `CLI sync tool for ani-cli` | Brief description |
   | **Commercial Use** | `No` | Select No |
   | **Terms of Service** | `Checked` | Agree to the API terms |
5. Click **"Submit"**.
6. Once created, you will see your **Client ID** (and optional Client Secret). Copy the **Client ID**.

---

### Step 2: Generate Authentication Tokens

`ani-sync` includes a built-in authentication wizard that automates the OAuth2 PKCE login flow.

Simply run:
```bash
ani-sync auth
```

1. Enter your **Client ID** when prompted.
2. Your browser will automatically open the MyAnimeList authorization page.
3. Click **"Allow"**.
4. You will be redirected to a URL starting with `http://localhost/?code=...`.
5. Copy the URL or code from your browser's address bar and paste it back into your terminal.
6. `ani-sync` will automatically generate your `refresh_token` and save your credentials securely to:
   ```
   ~/.config/ani-sync/config.env
   ```

---

### Step 3: Manual Environment Variable Setup (Optional)
If you prefer managing environment variables manually, you can export them in your `~/.bashrc` or `~/.zshrc`:

```bash
export MAL_CLIENT_ID="your_client_id_here"
export MAL_CLIENT_SECRET=""   # Optional
export MAL_REFRESH_TOKEN="your_refresh_token_here"
```

Then reload your shell:
```bash
source ~/.bashrc   # or source ~/.zshrc
```

---

## 🚀 Usage

### Basic Command
To watch an episode and sync it to MyAnimeList:

```bash
ani-sync watch <episode-url>
```

**Example:**
```bash
ani-sync watch https://gogoanime.cm/one-piece-episode-1000
```

#### What happens under the hood:
1. `ani-sync` resolves the stream source via `ani-cli`.
2. Starts playback in your chosen media player.
3. Once playback finishes, it queries the MyAnimeList API for the matching anime title.
4. Marks the episode as **watched** on your MAL account!

---

### Custom Media Player
Specify a custom video player using the `--player` flag:

```bash
ani-sync watch https://gogoanime.cm/naruto-episode-1 --player vlc
```

---

## 💖 Credits & Acknowledgements

This project was inspired by and built on top of amazing open-source projects created by the anime & terminal community:

- **[ani-cli](https://github.com/pystardust/ani-cli)** by *pystardust* — The incredible command-line anime browser and streaming tool that powers stream resolution and episode scraping.
- **[mal-cli](https://github.com/mdomke/mal-cli)** by *mdomke* — The pioneering command-line interface for MyAnimeList that inspired terminal tracking and synchronization workflows.

A huge thank you to the authors and contributors of these projects!

---

## 📄 License
Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.
