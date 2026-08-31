# 💖 Credits & Acknowledgements — ani-sync

`ani-sync` is built on the shoulders of giants in the free and open-source software (FOSS) community. Deepest gratitude and appreciation go out to the creators, maintainers, organizations, and open-source contributors whose tools, libraries, protocols, and ideas made this project possible.

---

## 🎬 Trailblazers & Direct Inspirations

| Project | Author / Maintainers | Contribution to ani-sync |
| :--- | :--- | :--- |
| **[ani-cli](https://github.com/pystardust/ani-cli)** | **[pystardust](https://github.com/pystardust)** & Contributors | The pioneering shell script that popularized command-line anime streaming and proved that watching anime from the terminal can be faster and cleaner than web browsers. |
| **[mal-cli](https://github.com/mdomke/mal-cli)** | **[mdomke](https://github.com/mdomke)** | The original command-line tool for MyAnimeList that inspired automated CLI-based episode tracking. |
| **[animdl](https://github.com/justfoolingaround/animdl)** | **[justfoolingaround](https://github.com/justfoolingaround)** | Early Python-based terminal anime streaming architectures and scraping techniques. |
| **[aria2](https://github.com/aria2/aria2)** | **[Tatsuhiro Tsujikawa](https://github.com/tatsuhiro-t)** | The multi-connection, multi-source segmented downloading paradigm that inspired ani-sync's 64x parallel fragment swarm engine. |

---

## ⚡ Core Media Engines & Terminal Powerhouses

| Software / Tool | Creators / Maintainers | Role in ani-sync |
| :--- | :--- | :--- |
| **[mpv](https://github.com/mpv-player/mpv)** | **[mpv-player Team](https://github.com/mpv-player)** | The gold-standard open-source media player powering GPU hardware-accelerated video decoding, on-screen OSD messages, Lua script intro/outro auto-skipping, and buffer management. |
| **[fzf](https://github.com/junegunn/fzf)** | **[Junegunn Choi (@junegunn)](https://github.com/junegunn)** | The blazingly fast, interactive fuzzy finder powering ani-sync's interactive search, franchise seasons browser, episode selector, and history navigation. |
| **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** | **[yt-dlp Team](https://github.com/yt-dlp)** & youtube-dl contributors | The unparalleled multi-connection HLS segment downloader and stream extractor that enables 64x turbo downloading. |
| **[FFmpeg](https://ffmpeg.org/)** | **[FFmpeg Developers](https://ffmpeg.org/)** | The universal multimedia demuxer and codec library enabling MPEG-TS stream fixup and audio/video synchronization. |
| **[curl](https://curl.se/)** | **[Daniel Stenberg (@bagder)](https://github.com/bagder)** & curl team | The robust command-line network transfer utility used in ani-sync's one-line installers and binary fetchers. |
| **[VLC media player](https://www.videolan.org/vlc/)** | **[VideoLAN Organization](https://www.videolan.org/)** | Alternative cross-platform media player engine supported natively via `--player vlc`. |
| **[IINA](https://iina.io/)** | **[Collider LI (@colliderli)](https://github.com/colliderli)** & IINA Team | Modern macOS video player supported natively via `--player iina`. |

---

## 🌐 Tracking Platforms & Anime Metadata APIs

| Platform / API | Organization | Functionality |
| :--- | :--- | :--- |
| **[MyAnimeList Official API](https://myanimelist.net/apiconfig)** | **[MyAnimeList Co., Ltd.](https://myanimelist.net/)** | Official OAuth 2.0 API used for real-time watched episode synchronization and user watch history imports. |
| **[AniList GraphQL API](https://anilist.co/)** | **[AniList (@AniList)](https://anilist.co/)** | Modern, flexible GraphQL API used for anime metadata search, cover assets, and cloud list progress mutations. |
| **[AniSkip API](https://aniskip.com/)** | **[AniSkip Community](https://aniskip.com/)** | Open-source crowd-sourced database for frame-accurate opening and ending theme timestamp skips. |
| **[Kitsu JSON:API](https://kitsu.io/)** | **[Kitsu (@kitsu-io)](https://kitsu.io/)** | Clean JSON:API standard used for seamless email/password authentication and library synchronization. |
| **[AniDB](https://anidb.app/)** | **[AniDB Community](https://anidb.app/)** | Anime title database indexing and HLS stream resolver backend. |

---

## 🐍 Python Libraries & Tooling

| Library | Authors / Maintainers | Purpose in ani-sync |
| :--- | :--- | :--- |
| **[Requests](https://requests.readthedocs.io/)** | **[Kenneth Reitz (@kennethreitz)](https://github.com/kennethreitz)** & urllib3 team | "HTTP for Humans" — handles all API requests, OAuth exchanges, and web scraping with resilient session management. |
| **[tqdm](https://github.com/tqdm/tqdm)** | **[Casper da Costa-Luis (@casperdcl)](https://github.com/casperdcl)** & contributors | Fast, extensible CLI progress bars during multi-platform library synchronization. |
| **[PyInstaller](https://pyinstaller.org/)** | **[PyInstaller Development Team](https://github.com/pyinstaller)** | Compiles standalone, self-contained single-file binaries for Linux, macOS, and Windows with 0 runtime dependencies. |
| **[Black](https://github.com/psf/black)** & **[isort](https://github.com/PyCQA/isort)** | **[Python Software Foundation](https://www.python.org/psf/)** | Automated PEP 8 code formatting and import sorting across the repository. |
| **[VHS](https://github.com/charmbracelet/vhs)** | **[Charmbracelet (@charmbracelet)](https://charm.sh/)** | Declarative terminal GIF and video generator for documentation demos. |
| **[Shields.io](https://shields.io/)** | **[Shields.io Team](https://shields.io/)** | Dynamic SVG status and release badges in README documentation. |

---

## 💬 Protocols & Inter-Process Communication

- **[Discord RPC Protocol](https://discord.com/developers/docs/topics/rpc)** — Discord local Unix domain socket (`/run/user/$UID/discord-ipc-0`) and Windows named pipe (`\\.\pipe\discord-ipc-0`) communication protocol used in `ani-sync`'s zero-dependency Rich Presence engine.

---

## 📜 Individual Authors & Maintainers

- **Creator & Lead Maintainer**: **[Idris Haris (@idrisharis12)](https://github.com/idrisharis12)**
- **License**: **[MIT License](LICENSE)** — Free and open-source for everyone forever.
