# -*- coding: utf-8 -*-
"""Media player binary discovery and execution (MPV, VLC, IINA, Android Intents, Syncplay)."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from ani_sync.config import CONFIG_DIR, IS_TERMUX, IS_WINDOWS, USER_AGENT, load_config
from ani_sync.player.aniskip import fetch_aniskip_times, get_auto_skip_script
from ani_sync.tracking.discord import DiscordRPC
from ani_sync.ui.themes import (
    C_BOLD,
    C_CYAN,
    C_DIM,
    C_GREEN,
    C_MAGENTA,
    C_RESET,
    C_YELLOW,
)


def find_player_binary(player="mpv"):
    """Find media player executable across Windows, macOS, Linux, and Android Termux."""
    if IS_TERMUX:
        if shutil.which("mpv"):
            return "mpv"
        if shutil.which("termux-open"):
            return "termux-open"
        if shutil.which("am"):
            return "am"
        return "termux-open"

    which_bin = shutil.which(player) or shutil.which(f"{player}.exe")
    if which_bin:
        return which_bin

    if IS_WINDOWS:
        if player == "mpv":
            candidates = [
                Path.home() / "scoop" / "apps" / "mpv" / "current" / "mpv.exe",
                Path(os.environ.get("LOCALAPPDATA", ""))
                / "Programs"
                / "mpv"
                / "mpv.exe",
                Path("C:/Program Files/mpv/mpv.exe"),
                Path("C:/Program Files (x86)/mpv/mpv.exe"),
                Path("C:/tools/mpv/mpv.exe"),
            ]
            for c in candidates:
                if c.exists():
                    return str(c)
        elif player == "vlc":
            candidates = [
                Path("C:/Program Files/VideoLAN/VLC/vlc.exe"),
                Path("C:/Program Files (x86)/VideoLAN/VLC/vlc.exe"),
            ]
            for c in candidates:
                if c.exists():
                    return str(c)

    if sys.platform == "darwin":
        if (
            player == "iina"
            and Path("/Applications/IINA.app/Contents/MacOS/iina-cli").exists()
        ):
            return "/Applications/IINA.app/Contents/MacOS/iina-cli"
        if (
            player == "vlc"
            and Path("/Applications/VLC.app/Contents/MacOS/VLC").exists()
        ):
            return "/Applications/VLC.app/Contents/MacOS/VLC"

    return player


def launch_player(
    target_path,
    title,
    ep_num,
    player="mpv",
    auto_skip=False,
    mal_id=None,
    party_room=None,
    low_ram=False,
    volume=None,
    start_time=None,
):
    """Launch player with large demuxer RAM buffers and frame-accurate AniSkip."""
    media_title = f"{title} - Episode {ep_num}"
    player_bin = find_player_binary(player)
    aniskip_data = fetch_aniskip_times(mal_id, ep_num) if mal_id else None

    # Syncplay Party Mode
    if party_room:
        syncplay_bin = shutil.which("syncplay") or shutil.which("syncplay.exe")
        if syncplay_bin:
            load_config()
            s_user = os.getenv("SYNCPLAY_NAME") or os.getenv("USER") or "Otaku"
            s_server = os.getenv("SYNCPLAY_SERVER") or "syncplay.pl:8999"
            cmd = [
                syncplay_bin,
                f"--player-path={player_bin}",
                target_path,
                "--name",
                s_user,
                "--room",
                party_room,
                "--server",
                s_server,
            ]
            print(
                f"\n{C_MAGENTA}{C_BOLD}🎉 Syncplay Party Active:{C_RESET} Room '{C_CYAN}{party_room}{C_RESET}' on {C_YELLOW}{s_server}{C_RESET}"
            )
            proc = subprocess.run(cmd)
            return proc.returncode == 0

    cmd = []
    if player_bin == "termux-open":
        cmd = ["termux-open", target_path]
    elif player_bin == "am":
        cmd = [
            "am",
            "start",
            "-a",
            "android.intent.action.VIEW",
            "-d",
            target_path,
            "-t",
            "video/*",
        ]
    elif player == "mpv" or "mpv" in Path(player_bin).stem.lower():
        demux_bytes = "150M" if (low_ram or IS_TERMUX) else "500M"
        back_bytes = "30M" if (low_ram or IS_TERMUX) else "100M"
        readahead = "60" if (low_ram or IS_TERMUX) else "300"
        stream_buf = "4MiB" if (low_ram or IS_TERMUX) else "16MiB"
        cmd = [
            player_bin,
            f"--force-media-title={media_title}",
            f"--user-agent={USER_AGENT}",
            "--referrer=https://anidb.app/",
            "--hwdec=auto-safe",
            "--profile=fast",
            "--audio-buffer=0.8",
            "--cache=yes",
        ]
        if volume is not None:
            cmd.append(f"--volume={volume}")
        if start_time and float(start_time) > 5:
            cmd.append(f"--start={int(start_time)}")
        cmd.extend([
            f"--demuxer-max-bytes={demux_bytes}",
            f"--demuxer-max-back-bytes={back_bytes}",
            f"--demuxer-readahead-secs={readahead}",
            f"--stream-buffer-size={stream_buf}",
            "--cache-pause=no",
            "--cache-pause-initial=no",
            "--force-seekable=yes",
            "--demuxer-seekable-cache=yes",
            "--hls-bitrate=max",
            "--network-timeout=20",
            "--msg-level=ffmpeg=error",
        ])
        skip_script = get_auto_skip_script(
            auto_skip=auto_skip, aniskip_data=aniskip_data
        )
        if skip_script:
            cmd.append(f"--script={skip_script}")
        user_scripts_dir = CONFIG_DIR / "scripts"
        if user_scripts_dir.exists():
            for script_file in user_scripts_dir.glob("*.lua"):
                cmd.append(f"--script={script_file}")
        cmd.append(target_path)
    elif player == "vlc" or "vlc" in Path(player_bin).stem.lower():
        cmd = [
            player_bin,
            "--play-and-exit",
            f"--meta-title={media_title}",
            "--network-caching=3000",
            "--http-reconnect",
            target_path,
        ]
    elif player == "iina" or "iina" in Path(player_bin).stem.lower():
        cmd = [
            player_bin,
            f"--mpv-force-media-title={media_title}",
            "--mpv-cache=yes",
            "--mpv-demuxer-max-bytes=500M",
            "--mpv-demuxer-readahead-secs=300",
            target_path,
        ]
    else:
        cmd = [player_bin, target_path]

    print(f"\n{C_BOLD}▶️  Now Playing:{C_RESET} {C_CYAN}{media_title}{C_RESET}")
    if aniskip_data and (aniskip_data.get("op") or aniskip_data.get("ed")):
        skip_info = []
        if aniskip_data.get("op"):
            s, e = aniskip_data["op"]
            skip_info.append(f"OP: {s:.0f}s-{e:.0f}s")
        if aniskip_data.get("ed"):
            s, e = aniskip_data["ed"]
            skip_info.append(f"ED: {s:.0f}s-{e:.0f}s")
        print(
            f"{C_GREEN}⚡ AniSkip Active:{C_RESET} {C_BOLD}{' • '.join(skip_info)}{C_RESET}"
        )
    print(
        f"{C_DIM}Shortcuts: [Tab]/[i] Skip Intro | [o] Skip Outro | [q] Quit{C_RESET}\n"
    )

    DiscordRPC.start_activity(title, ep_num)
    try:
        proc = subprocess.run(cmd)
        return proc.returncode == 0
    finally:
        DiscordRPC.stop_activity()
