import re

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

bench_old = r"""## ⚡ Why ani-sync is Better \(Performance Benchmarks\)

Streaming anime in a web browser loads bloated JavaScript bundles, video ads, crypto-miners, and pop-unders\. `ani-sync` runs directly in your terminal using hardware-accelerated MPV:

```text
┌──────────────────────────────────────┬───────────────────────┬───────────────────────┐
│ Metric                               │ 🌐 Web Browser Anime  │ 📺 ani-sync v2\.7\.0    │
├──────────────────────────────────────┼───────────────────────┼───────────────────────┤
│ 💾 RAM Memory Footprint              │ 1,800 MB – 3,500 MB   │ 28 MB – 45 MB         │
│ ⚡ CPU Utilization                   │ 35% – 70% \(Software\)  │ 2% – 5% \(GPU Decoded\) │
│ 🛡️ Telemetry, Popups & Ad Trackers   │ 40\+ JavaScript pixels │ 0 \(Zero Telemetry\)    │
│ ⏱️ Playback Start & Seek Latency    │ 15s – 30s buffering   │ 0\.00s \(RAM Cache\)     │
│ 🔄 Multi-Cloud Progress Auto-Sync    │ ❌ None               │ ✅ MAL \+ AniList\+Kitsu│
│ ⏩ Frame-Accurate OP/ED Skipping     │ ❌ Manual dragging    │ ✅ AniSkip \[Tab\]/\[o\]  │
│ 🔋 Battery Drain \(Laptops/Handhelds\) │ ⚠️ Heavy Drain        │ 🌿 Ultra Low          │
---

## 💾 Storage Requirements & System Footprint

`ani-sync` is engineered to be extremely lightweight with minimal disk footprint and system overhead:

\| Package / Component \| Storage Size \| Description / Notes \|
\| :--- \| :--- \| :--- \|
\| 📦 \*\*Core Python Package Source \(`ani_sync`\)\*\* \| \*\*~568 KB\*\* \| Ultra-compact package size for `pip` / system installations \|
\| ⚡ \*\*Standalone Pre-Compiled Binary\*\* \| \*\*~21\.7 MB\*\* \| Single self-contained binary with zero Python runtime dependency \|
\| 📄 \*\*Native Debian Package \(`\.deb`\)\*\* \| \*\*~52 KB\*\* \| Compressed Debian/Ubuntu release package \|
\| 🧠 \*\*RAM Memory Footprint During Playback\*\* \| \*\*~28 MB – 45 MB\*\* \| \*\*98% lighter\*\* than web browser streaming \(~2,500 MB\) \|
\| ⚙️ \*\*External Dependencies \(`mpv`, `yt-dlp`, `fzf`\)\*\* \| \*\*~50 MB total\*\* \| Standard lightweight system tools \|
\| 🔄 \*\*Dynamic Stream Cache Buffer\*\* \| \*\*Auto-Managed \(~4 GB max\)\*\* \| Stored in `/dev/shm` RAM-disk on Linux; automatically rotates and purges old episodes \|
"""

bench_new = """## ⚡ Why ani-sync is Better (Performance Benchmarks)

Streaming anime in a web browser loads bloated JavaScript bundles, video ads, crypto-miners, and pop-unders. `ani-sync` runs directly in your terminal using hardware-accelerated MPV!

<details open>
<summary><b>🚀 Performance Comparison vs Web Browser (Click to collapse)</b></summary>
<br>

| Metric | 🌐 Web Browser Anime | 📺 ani-sync |
| :--- | :--- | :--- |
| 💾 **RAM Memory Footprint** | `1,800 MB` – `3,500 MB` | **`28 MB` – `45 MB`** |
| ⚡ **CPU Utilization** | `35%` – `70%` (Software) | **`2%` – `5%`** (GPU Hardware Decoded) |
| 🛡️ **Ad Trackers & Telemetry**| 40+ JavaScript pixels | **`0`** (100% Zero Telemetry) |
| ⏱️ **Start & Seek Latency** | `15s` – `30s` buffering | **`0.00s`** (Instant RAM Cache) |
| 🔄 **Multi-Cloud Syncing** | ❌ None | ✅ **MAL** + **AniList** + **Kitsu** |
| ⏩ **Opening / Ending Skip** | ❌ Manual dragging | ✅ **Auto AniSkip** `[Tab]`/`[o]` |
| 🔋 **Battery Drain (Laptops)**| ⚠️ Heavy Drain | 🌿 **Ultra Low** |

</details>

<details>
<summary><b>💾 Storage Requirements & System Footprint (Click to expand)</b></summary>
<br>

`ani-sync` is engineered to be extremely lightweight with minimal disk footprint and system overhead:

| Package / Component | Storage Size | Description / Notes |
| :--- | :--- | :--- |
| 📦 **Core Python Package Source (`ani_sync`)** | **~568 KB** | Ultra-compact package size for `pip` / system installations |
| ⚡ **Standalone Pre-Compiled Binary** | **~21.7 MB** | Single self-contained binary with zero Python runtime dependency |
| 📄 **Native Debian Package (`.deb`)** | **~52 KB** | Compressed Debian/Ubuntu release package |
| 🧠 **RAM Memory Footprint During Playback** | **~28 MB – 45 MB** | **98% lighter** than web browser streaming (~2,500 MB) |
| ⚙️ **External Dependencies (`mpv`, `yt-dlp`, `fzf`)** | **~50 MB total** | Standard lightweight system tools |
| 🔄 **Dynamic Stream Cache Buffer** | **Auto-Managed (~4 GB max)** | Stored in `/dev/shm` RAM-disk on Linux; automatically rotates and purges old episodes |

</details>
"""
content = re.sub(bench_old, bench_new, content)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)
