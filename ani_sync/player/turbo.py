# -*- coding: utf-8 -*-
"""Instant streaming playback, background prefetching, and multi-connection downloading."""

import shutil
import subprocess

from ani_sync.config import CACHE_DIR, IS_TERMUX, USER_AGENT, sanitize_filename
from ani_sync.player.launcher import launch_player
from ani_sync.providers.manager import resolve_streams
from ani_sync.ui.themes import C_BOLD, C_CYAN, C_GREEN, C_RED, C_RESET


def turbo_play(
    stream_url,
    title,
    ep_num,
    player="mpv",
    direct=False,
    download_only=False,
    auto_skip=False,
    mal_id=None,
    party_room=None,
    low_ram=False,
    volume=None,
    start_time=None,
):
    """Zero-latency instant playback with high-throughput RAM buffer and local cache fallback."""
    safe_title = sanitize_filename(f"{title}_EP{ep_num}")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{safe_title}.mp4"

    # 1. Instant local playback if cached
    if cache_file.exists() and cache_file.stat().st_size > 5 * 1024 * 1024:
        print(
            f"\n{C_GREEN}{C_BOLD}⚡ Episode loaded from turbo cache — 0.0s instant start!{C_RESET}"
        )
        if download_only:
            print(f"{C_GREEN}✓ File ready at: {cache_file}{C_RESET}")
            return True, 0
        return launch_player(
            str(cache_file),
            title,
            ep_num,
            player=player,
            auto_skip=auto_skip,
            mal_id=mal_id,
            party_room=party_room,
            low_ram=low_ram,
            volume=volume,
            start_time=start_time,
        )

    # 2. Download-only mode
    if download_only:
        has_ytdlp = shutil.which("yt-dlp") is not None
        if not has_ytdlp:
            print(
                f"{C_RED}❌ yt-dlp is required for downloading anime episodes.{C_RESET}"
            )
            return False

        concurrency = "16" if (low_ram or IS_TERMUX) else "32"
        buffer_size = "4M" if (low_ram or IS_TERMUX) else "16M"
        chunk_size = "2M" if (low_ram or IS_TERMUX) else "10M"

        print(
            f"\n{C_CYAN}{C_BOLD}📥 Downloading Episode {ep_num} via multi-connection turbo engine...{C_RESET}"
        )
        dl_cmd = [
            "yt-dlp",
            "-N",
            concurrency,
            "--concurrent-fragments",
            concurrency,
            "--socket-timeout",
            "10",
            "--buffer-size",
            buffer_size,
            "--http-chunk-size",
            chunk_size,
            "--fragment-retries",
            "10",
            "--retries",
            "5",
            "--add-header",
            "Referer: https://anidb.app/",
            "--add-header",
            "Origin: https://anidb.app",
            "--user-agent",
            USER_AGENT,
            "--no-warnings",
            "--no-part",
            "-o",
            str(cache_file),
            stream_url,
        ]
        try:
            subprocess.run(dl_cmd, check=True)
            print(f"\n{C_GREEN}{C_BOLD}✓ Download complete:{C_RESET} {cache_file}")
            return True
        except Exception as e:
            print(f"{C_RED}❌ Download failed: {e}{C_RESET}")
            return False

    # 3. Instant streaming with deep RAM buffer
    res = launch_player(
        stream_url,
        title,
        ep_num,
        player=player,
        auto_skip=auto_skip,
        mal_id=mal_id,
        party_room=party_room,
        low_ram=low_ram,
        volume=volume,
    )

    # Cache cleanup: Keep newest ~4GB of anime
    try:
        cached_files = sorted(CACHE_DIR.glob("*.mp4"), key=lambda f: f.stat().st_mtime)
        total_size = sum(f.stat().st_size for f in cached_files)
        while total_size > 4 * 1024 * 1024 * 1024 and len(cached_files) > 6:
            oldest = cached_files.pop(0)
            total_size -= oldest.stat().st_size
            oldest.unlink(missing_ok=True)
    except Exception:
        pass

    return res


def prefetch_episode(
    next_ep_data, title, preferred_quality=None, mode="sub", slug=None
):
    """Background pre-fetch of next episode so it loads in 0.0s."""
    try:
        ep_num = next_ep_data.get("number")
        ep_id = next_ep_data.get("id")
        safe_title = sanitize_filename(f"{title}_EP{ep_num}")
        cache_file = CACHE_DIR / f"{safe_title}.mp4"
        if cache_file.exists() and cache_file.stat().st_size > 5 * 1024 * 1024:
            return

        streams = resolve_streams(ep_id, mode=mode, anime_slug=slug, ep_num=ep_num)
        if not streams:
            return

        selected_url = None
        if preferred_quality and preferred_quality in streams:
            selected_url = streams[preferred_quality]
        elif "720p" in streams:
            selected_url = streams["720p"]
        else:
            selected_url = list(streams.values())[0]

        dl_cmd = [
            "yt-dlp",
            "-N",
            "8",
            "--concurrent-fragments",
            "8",
            "--socket-timeout",
            "5",
            "--buffer-size",
            "8M",
            "--http-chunk-size",
            "4M",
            "--fragment-retries",
            "10",
            "--retries",
            "5",
            "--add-header",
            "Referer: https://anidb.app/",
            "--add-header",
            "Origin: https://anidb.app",
            "--user-agent",
            USER_AGENT,
            "--no-warnings",
            "--quiet",
            "--no-part",
            "-o",
            str(cache_file),
            selected_url,
        ]
        subprocess.run(dl_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
