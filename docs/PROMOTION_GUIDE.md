# 📢 Promotion & Community Growth Guide for `ani-sync`

This guide contains copy-paste post templates and strategies to share `ani-sync` with communities to build active users and GitHub stars.

---

## 🎯 Target Communities

1. [**r/animepiracy**](https://reddit.com/r/animepiracy) (Top target — 300k+ members)
2. [**r/commandline**](https://reddit.com/r/commandline) & [**r/linux**](https://reddit.com/r/linux)
3. [**r/unixporn**](https://reddit.com/r/unixporn) (Post with a nice rice screenshot)
4. [**r/myanimelist**](https://reddit.com/r/myanimelist)
5. **Hacker News ("Show HN")**
6. **AlternativeTo.net**

---

## 📝 Reddit Post Template (Copy & Paste)

### 📌 Title:
> **[Release] ani-sync v2.0: Stream anime from your terminal with 64x multi-connection turbo speed and automatic MyAnimeList tracking (Linux, Windows, macOS)**

### 📄 Post Body:

```markdown
Hey everyone! 👋

I built **ani-sync**, an open-source command-line tool that lets you search and stream anime directly from your terminal and automatically syncs your watch progress to **MyAnimeList** in real-time.

### 🌟 Why I built it:
Existing CLI players (like `ani-cli`) are great, but they lack automatic list tracking (you have to manually update MAL after bingeing), and single-thread streaming often stutters when CDNs throttle bandwidth.

**ani-sync** fixes this with a **4-tier acceleration engine**:

1. ⚡ **64x Turbo Multi-Connections**: Downloads 64 fragments in parallel, downloading full episodes in ~3–5 seconds and eliminating all buffering.
2. 💾 **RAM-Disk In-Memory Caching (`/dev/shm`)**: Caches streams directly into RAM at 10,000+ MB/s for 0ms seek latency and 0 SSD wear.
3. ⏩ **Predictive Dual Pre-Fetching**: While watching Episode N, Episodes N+1 and N+2 are preloaded in the background so next episodes start in **0.00 seconds**.
4. 🔄 **Automatic MyAnimeList OAuth2 Sync**: Automatically records watched episodes on your MAL profile as soon as playback finishes.
5. 🪟 **Cross-Platform**: Runs natively on **Linux**, **macOS**, and **Windows (PowerShell/CMD)**.
6. 🎮 **Interactive Controls**: Next/Prev episode, seasons/movies selector, 720p/1080p switcher, English Dub support, and offline download mode (`-d`).

---

### 📦 Installation:

**Linux / macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.ps1 | iex
```

---

### 🚀 Usage:
```bash
ani-sync "frieren"
ani-sync continue          # Resumes your last watched anime
ani-sync trending          # Browses top airing anime
ani-sync "naruto" -q 1080p # Stream in 1080p
ani-sync auth              # 1-command MyAnimeList connection wizard
```

🔗 **GitHub Repository & Source Code**: https://github.com/idrisharis12/ani-sync

Feedback, bug reports, and feature requests are very welcome! If you like the project, a ⭐ on GitHub means a lot!
```

---

## 🏷️ GitHub Topic Tags
Make sure your GitHub repo has these tags configured under "About":
`anime`, `cli`, `myanimelist`, `mal`, `mpv`, `terminal`, `anime-streaming`, `streaming`, `python`, `cross-platform`, `zero-buffering`, `ani-cli`
