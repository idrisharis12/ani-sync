# ⚡ ani-sync — Ultimate CLI CheatSheet & Command Reference

<p align="center">
  <img src="assets/ani-sync_logo.jpeg" alt="ani-sync logo" width="180" />
</p>

<p align="center">
  <b>Comprehensive Quick-Reference, Keybindings, Flags, Platform Auth & Power-User Recipes for ani-sync</b>
</p>

---

## 📑 Quick Navigation

- [⚡ Quick Start One-Liners](#-quick-start-one-liners)
- [🎮 Core Commands Reference](#-core-commands-reference)
- [🚩 CLI Flags & Options Matrix](#-cli-flags--options-matrix)
- [🎬 In-Player Keybindings (MPV)](#-in-player-keybindings-mpv)
- [🔄 Post-Playback Interactive Controls](#-post-playback-interactive-controls)
- [🔑 Platform Authentication Commands](#-platform-authentication-commands)
- [⚙️ Configuration Environment Variables](#-configuration-environment-variables)
- [💡 Power-User Tips & Shell Aliases](#-power-user-tips--shell-aliases)
- [🩺 System Diagnostics & Troubleshooting](#-system-diagnostics--troubleshooting)

---

## ⚡ Quick Start One-Liners

| Goal | Command |
| :--- | :--- |
| **Search & Watch** | `ani-sync "frieren"` |
| **Interactive Mode (FZF)** | `ani-sync` |
| **Resume Last Anime (Next Ep)** | `ani-sync continue` *(or `ani-sync -c`)* |
| **Browse Top Trending** | `ani-sync trending` *(or `ani-sync -t`)* |
| **Airing Schedule & Calendar** | `ani-sync schedule` *(or `ani-sync -s`)* |
| **Browse Watch History** | `ani-sync history` |
| **Sync Cloud Libraries** | `ani-sync sync` *(or `ani-sync import`)* |
| **Play Episode 1 in 1080p** | `ani-sync "solo leveling" -e 1 -q 1080p` |
| **Stream English Dub** | `ani-sync "attack on titan" --dub` |
| **Download Episode to Disk** | `ani-sync "jujutsu kaisen" -e 1 -d` |
| **Batch Download Range** | `ani-sync "jujutsu kaisen" -d -e 1-12` |
| **Download Entire Season** | `ani-sync "chainsaw man" -d --all` |
| **Rate & Score Anime** | `ani-sync score "frieren" 10` *(or `ani-sync score`)* |
| **Select Stream Provider** | `ani-sync "naruto" --provider gogo` *(or `anidb`, `auto`)* |
| **Change Color Theme** | `ani-sync theme tokyonight` *(or `catppuccin`, `dracula`, `nord`, `gruvbox`)* |
| **Verify System Health** | `ani-sync doctor` |
| **Open-Source Credits** | `ani-sync credits` |
| **Update ani-sync** | `ani-sync update` *(or `ani-sync -U`)* |

---

## 🎮 Core Commands Reference

### 1. `ani-sync [anime title]`
Searches the database and launches interactive episode selection.
```bash
ani-sync "demon slayer"
ani-sync "death note"
ani-sync "one piece"
```

### 2. `ani-sync continue` / `ani-sync -c`
Reads `~/.config/ani-sync/history.json` and immediately launches **Episode N+1** of your last watched series with zero startup delay.
```bash
ani-sync -c
```

### 3. `ani-sync trending` / `ani-sync -t`
Fetches top currently airing and popular seasonal anime directly from the API and opens an interactive FZF picker.
```bash
ani-sync -t
```

### 4. `ani-sync history`
Displays your complete chronological local watch history with anime titles, last watched episode, quality, and audio mode. Selecting an item resumes playback immediately.
```bash
ani-sync history
```

### 5. `ani-sync sync` / `ani-sync import`
Connects to all authenticated tracking platforms (**MyAnimeList**, **AniList**, **Kitsu**), pulls your full anime lists (Watching + Completed), merges them without duplicates, and populates your local history.
```bash
ani-sync sync
```

### 6. `ani-sync auth [platform]`
Interactive setup wizard for linking your anime tracking accounts.
```bash
ani-sync auth          # Interactive multi-platform menu
ani-sync auth mal      # Connect MyAnimeList (OAuth2)
ani-sync auth anilist  # Connect AniList (OAuth2 PIN)
ani-sync auth kitsu    # Connect Kitsu (Email / Password)
```

### 7. `ani-sync doctor` / `ani-sync check`
Performs an automated diagnostic scan of all runtime dependencies, package versions, binary paths, and platform authentication statuses.
```bash
ani-sync doctor
```

### 8. `ani-sync credits`
Displays project credits and open-source acknowledgements for all libraries and tools that power `ani-sync`.
```bash
ani-sync credits
```

### 9. `ani-sync update` / `ani-sync -U`
Checks GitHub releases for the latest version and self-updates in place.
```bash
ani-sync update
ani-sync update --quiet   # Silent mode (used in cron / scripts)
```

---

## 🚩 CLI Flags & Options Matrix

| Flag | Long Flag | Description | Default | Example |
| :--- | :--- | :--- | :--- | :--- |
| `-c` | `--continue` | Resume last anime from next episode | `false` | `ani-sync -c` |
| `-t` | `--trending` | Browse top trending & seasonal anime | `false` | `ani-sync -t` |
| `-e <n>` | `--episode <n>` | Jump directly to episode number `<n>` | Prompt | `ani-sync "naruto" -e 135` |
| `-q <res>` | `--quality <res>` | Stream resolution (`1080p`, `720p`, `480p`, `360p`) | `720p` | `ani-sync "bleach" -q 1080p` |
| `--dub` | `--dub` | Stream English Dubbed version | `Sub` | `ani-sync "cyberpunk" --dub` |
| `--skip` | `--auto-skip` | Auto fast-forward +85s past anime OP | `false` | `ani-sync "frieren" --skip` |
| `-d` | `--download` | Save episode locally to disk without player | `false` | `ani-sync "one punch man" -d -e 1` |
| `--direct` | `--direct` | Direct stream without RAM-disk cache | `false` | `ani-sync "gintama" --direct` |
| `--no-fzf` | `--no-fzf` | Disable interactive fuzzy search (use numbers) | `false` | `ani-sync --no-fzf` |
| `--player` | `--player <bin>` | Media player binary (`mpv`, `vlc`, `iina`) | `mpv` | `ani-sync "mha" --player vlc` |
| `-U` | `--update` | Check and install latest version | `false` | `ani-sync -U` |
| `-h` | `--help` | Display quick help menu | `false` | `ani-sync --help` |

---

## 🎬 In-Player Keybindings (MPV)

While watching an episode in the default `mpv` player, use these built-in keyboard shortcuts:

### ⚡ Ani-Sync Custom Shortcuts
| Key | Action |
| :--- | :--- |
| **`Tab`** or **`i`** | **Skip Anime Intro / Opening** (+85 seconds forward) |
| **`o`** | **Skip Anime Outro / Ending** (+85 seconds forward) |
| **`q`** | **Quit Player & Return to Post-Playback Menu** |

### ⏯️ Standard MPV Navigation
| Key | Action |
| :--- | :--- |
| **`Space`** or **`p`** | Pause / Resume playback |
| **`→`** / **`←`** | Seek forward / backward **5 seconds** |
| **`↑`** / **`↓`** | Seek forward / backward **60 seconds** |
| **`[`** / **`]`** | Decrease / Increase playback speed by 10% |
| **`Backspace`** | Reset playback speed to normal (1.0x) |
| **`9`** / **`0`** | Decrease / Increase audio volume |
| **`m`** | Mute / Unmute audio |
| **`f`** | Toggle Fullscreen mode |
| **`s`** | Take a screenshot (saved to current directory) |
| **`Shift + s`** | Take a screenshot without subtitles |
| **`j`** | Cycle through subtitle tracks |
| **`v`** | Toggle subtitle visibility on / off |
| **`Shift + T`** | Toggle "Always on Top" window mode |

---

## 🔄 Post-Playback Interactive Controls

When an episode concludes or you press `q` in the player, `ani-sync` syncs progress to your accounts and provides an interactive control loop:

```
┌──────────────────────────────────────────────────────────┐
│  [Enter] Next Ep (4)  │  [r] Replay  │  [p] Previous     │
│  [s] Select Episode   │  [q] Quality │  [S] Season/Movie │
│  [m] Menu (FZF)       │  [x] Quit                        │
└──────────────────────────────────────────────────────────┘
```

| Key | Action | Description |
| :--- | :--- | :--- |
| **`Enter`** or **`n`** | **Next Episode** | Plays next episode instantly (0.00s pre-fetched) |
| **`r`** | **Replay** | Replays the current episode from the beginning |
| **`p`** | **Previous Episode** | Plays episode N-1 |
| **`s`** | **Select Episode** | Opens episode picker list |
| **`q`** | **Change Quality** | Switch between 1080p, 720p, 480p, 360p |
| **`S`** | **Change Season/Movie** | Switch to another season or movie in the franchise |
| **`m`** | **FZF Menu** | Full interactive menu with all options |
| **`x`** | **Exit** | Safely exits `ani-sync` |

---

## 🔑 Platform Authentication Commands

`ani-sync` supports automatic simultaneous tracking across all 3 major platforms:

```
                  ┌──► MyAnimeList (MAL) ──► Auto-Increment Episode Count
[ Finished Ep ] ──┼──► AniList (GraphQL) ──► Update Progress & Status
                  └──► Kitsu (JSON:API)  ──► Real-Time Library Sync
```

### 🟣 AniList (`ani-sync auth anilist`)
1. Create client at: [https://anilist.co/settings/developer](https://anilist.co/settings/developer)
2. Redirect URL: `https://anilist.co/api/v2/oauth/pin`
3. Enter Client ID & Secret in terminal ➔ Authorize ➔ Paste PIN code.

### 🟠 Kitsu (`ani-sync auth kitsu`)
1. Run `ani-sync auth kitsu`
2. Enter your Kitsu email / username and password.
3. Tokens are generated and encrypted locally; passwords are never saved.

### 🔵 MyAnimeList (`ani-sync auth mal`)
1. Create client at: [https://myanimelist.net/apiconfig](https://myanimelist.net/apiconfig)
2. Redirect URL: `http://localhost`
3. Enter Client ID in terminal ➔ Authorize ➔ Paste redirect URL.

---

## ⚙️ Configuration Environment Variables

All settings and tokens are stored in `~/.config/ani-sync/config.env` (Linux/macOS) or `%APPDATA%\ani-sync\config.env` (Windows):

```bash
# === MyAnimeList Configuration ===
export MAL_CLIENT_ID="your_mal_client_id"
export MAL_CLIENT_SECRET=""
export MAL_REFRESH_TOKEN="your_mal_refresh_token"

# === AniList Configuration ===
export ANILIST_CLIENT_ID="your_anilist_client_id"
export ANILIST_CLIENT_SECRET="your_anilist_client_secret"
export ANILIST_TOKEN="your_anilist_access_token"

# === Kitsu Configuration ===
export KITSU_TOKEN="your_kitsu_access_token"
export KITSU_REFRESH_TOKEN="your_kitsu_refresh_token"

# === Discord Rich Presence ===
export DISCORD_CLIENT_ID="1543718626400403466"
```

---

## 💡 Power-User Tips & Shell Aliases

Add these productivity shortcuts to your `~/.bashrc` or `~/.zshrc`:

```bash
# Quick resume last anime
alias anic="ani-sync continue"

# Quick trending browser
alias anit="ani-sync trending"

# Quick history browser
alias anih="ani-sync history"

# Full 1080p anime search
alias anihd="ani-sync -q 1080p"

# English Dub search
alias anidub="ani-sync --dub"

# Download episode helper (e.g. anidl "naruto" 1)
anidl() {
    ani-sync "$1" -e "$2" -d
}
```

---

## 🩺 System Diagnostics & Troubleshooting

Run the doctor command anytime you encounter issues:
```bash
ani-sync doctor
```

### Common Fixes:
- **Missing FZF**: Handled automatically! `ani-sync` downloads the standalone binary if missing.
- **Buffering on slow networks**: Use `-q 480p` or 720p (default).
- **MPV hardware acceleration**: `ani-sync` enables `--hwdec=auto-safe` automatically. Ensure GPU drivers (VAAPI / NVDEC) are installed.
- **Discord Rich Presence not showing**: Verify Discord is running on the same user session and **Activity Privacy** -> **Display current activity** is turned **ON** in Discord settings.

---

<p align="center">
  <b>ani-sync</b> — Designed with ❤️ for anime enthusiasts who love the terminal.
</p>
