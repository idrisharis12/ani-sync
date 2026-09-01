import re

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

faq_old = r"""## 🔍 Frequently Asked Questions \(SEO & Search Guide\)

### How to watch anime in terminal\?
To \*\*watch anime in terminal\*\*, install `ani-sync` \(`curl -fsSL https://raw\.githubusercontent\.com/idrisharis12/ani-sync/main/install\.sh \| bash`\) and run `ani-sync "anime title"`\. It launches high-speed 64x turbo streaming directly in MPV, VLC, or IINA with 100% zero buffering\.

### What is the best CLI anime player for Linux, macOS, Windows & Termux\?
`ani-sync` is the top-rated open-source CLI anime player supporting \*\*Linux\*\* \(Arch, Ubuntu, Fedora, Debian\), \*\*macOS\*\*, \*\*Windows\*\*, and \*\*Android Termux\*\*\. It features 24-bit TrueColor ANSI graphic thumbnails, frame-accurate AniSkip intro skipping, Syncplay watch parties, and automatic MyAnimeList, AniList, and Kitsu multi-platform tracking\.

### How to stream anime in command line with zero buffering\?
`ani-sync` uses a 64-socket parallel TCP fragment engine combined with Linux `/dev/shm` RAM-disk caching to eliminate buffering completely, starting playback in \*\*0\.0 seconds\*\*\.

### How to sync MyAnimeList and AniList watch progress automatically from terminal\?
Run `ani-sync auth` to connect your MyAnimeList, AniList, or Kitsu account\. Whenever you watch an episode using `ani-sync`, your watch progress, episode count, and completion status are updated across all 3 platforms in parallel\."""

faq_new = """## 🔍 Frequently Asked Questions (SEO & Search Guide)

<details>
<summary><b>📺 How to watch anime in terminal?</b></summary>
<br>
To <b>watch anime in terminal</b>, install <code>ani-sync</code> (<code>curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | bash</code>) and run <code>ani-sync "anime title"</code>. It launches high-speed 64x turbo streaming directly in MPV, VLC, or IINA with 100% zero buffering.
</details>

<details>
<summary><b>🏆 What is the best CLI anime player for Linux, macOS, Windows & Termux?</b></summary>
<br>
<code>ani-sync</code> is the top-rated open-source CLI anime player supporting <b>Linux</b> (Arch, Ubuntu, Fedora, Debian), <b>macOS</b>, <b>Windows</b>, and <b>Android Termux</b>. It features 24-bit TrueColor ANSI graphic thumbnails, frame-accurate AniSkip intro skipping, Syncplay watch parties, and automatic MyAnimeList, AniList, and Kitsu multi-platform tracking.
</details>

<details>
<summary><b>⚡ How to stream anime in command line with zero buffering?</b></summary>
<br>
<code>ani-sync</code> uses a 64-socket parallel TCP fragment engine combined with Linux <code>/dev/shm</code> RAM-disk caching to eliminate buffering completely, starting playback in <b>0.0 seconds</b>.
</details>

<details>
<summary><b>🔄 How to sync MyAnimeList and AniList watch progress automatically from terminal?</b></summary>
<br>
Run <code>ani-sync auth</code> to connect your MyAnimeList, AniList, or Kitsu account. Whenever you watch an episode using <code>ani-sync</code>, your watch progress, episode count, and completion status are updated across all 3 platforms in parallel.
</details>"""

content = re.sub(faq_old, faq_new, content)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)
