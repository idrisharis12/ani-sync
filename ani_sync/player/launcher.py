# -*- coding: utf-8 -*-
"""Media player binary discovery and execution (MPV, VLC, IINA, Android Intents, Syncplay)."""

import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
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

_LAST_MPV_TIME_POS = 0.0


def poll_mpv_ipc(ipc_path, stop_event):
    """Poll MPV IPC JSON socket for real-time playback position (time-pos)."""
    global _LAST_MPV_TIME_POS
    _LAST_MPV_TIME_POS = 0.0

    time.sleep(1.5)
    while not stop_event.is_set():
        try:
            if IS_WINDOWS:
                if os.path.exists(ipc_path):
                    with open(ipc_path, "r+b", buffering=0) as pipe:
                        req = (
                            json.dumps({"command": ["get_property", "time-pos"]}) + "\n"
                        )
                        pipe.write(req.encode("utf-8"))
                        res = pipe.readline()
                        data = json.loads(res.decode("utf-8", errors="ignore"))
                        if "data" in data and isinstance(data["data"], (int, float)):
                            _LAST_MPV_TIME_POS = float(data["data"])
            else:
                if os.path.exists(ipc_path):
                    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                        s.settimeout(1.5)
                        s.connect(ipc_path)
                        req = (
                            json.dumps({"command": ["get_property", "time-pos"]}) + "\n"
                        )
                        s.sendall(req.encode("utf-8"))
                        res = s.recv(1024)
                        data = json.loads(res.decode("utf-8", errors="ignore"))
                        if "data" in data and isinstance(data["data"], (int, float)):
                            _LAST_MPV_TIME_POS = float(data["data"])
        except Exception:
            pass
        time.sleep(2.0)


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


def get_torrent_episode_index(streamer_bin, target_path, ep_num):
    """Inspect torrent file list to find the exact file index matching the requested episode number."""
    if not ep_num or int(ep_num) <= 0:
        return 0
    try:
        proc = subprocess.run(
            [streamer_bin, target_path, "--list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = proc.stdout.splitlines()
        ep_pats = [
            re.compile(rf"(?:s\d+)?e{int(ep_num):02d}(?:\D|$)", re.I),
            re.compile(rf"(?:s\d+)?e{int(ep_num)}(?:\D|$)", re.I),
            re.compile(rf"(?:ep|episode|\s|-|_){int(ep_num):02d}(?:\D|$)", re.I),
            re.compile(rf"(?:ep|episode|\s|-|_){int(ep_num)}(?:\D|$)", re.I),
        ]
        for line in lines:
            m = re.match(r"^\s*(\d+)\s*:\s*(.+?)\s*:\s*[\d\.]+\s*[KMGT]?B", line)
            if m:
                idx = int(m.group(1))
                fname = m.group(2)
                for pat in ep_pats:
                    if pat.search(fname):
                        return idx
    except Exception:
        pass
    return int(ep_num) - 1


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

    # Handle BitTorrent / Magnet Fallback
    if target_path.startswith("magnet:") or "torrent" in target_path:
        torrent_streamer = (
            shutil.which("peerflix")
            or shutil.which("webtorrent")
            or shutil.which("webtorrent.cmd")
        )
        if torrent_streamer:
            print(f"\n{C_CYAN}🧲 Streaming via BitTorrent (Nyaa fallback)...{C_RESET}")
            # Wipe stale torrent-stream cache to prevent resuming stalled/dead torrents
            try:
                subprocess.run(["pkill", "-f", "peerflix"], stderr=subprocess.DEVNULL)
            except Exception:
                pass

            # Detect exact episode file index in batch torrents
            file_idx = get_torrent_episode_index(torrent_streamer, target_path, ep_num)
            print(
                f"{C_DIM}Starting P2P stream proxy on http://127.0.0.1:8888/ (File index {file_idx})...{C_RESET}"
            )

            # Run peerflix in background as a local streaming HTTP server
            server_cmd = [
                torrent_streamer,
                target_path,
                "-p",
                "8888",
                "-i",
                str(file_idx),
                "--remove",
            ]
            server_proc = subprocess.Popen(
                server_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Wait for HTTP server to become live and ready to serve
            http_url = "http://127.0.0.1:8888/"
            ready = False
            for _ in range(40):
                if server_proc.poll() is not None:
                    break
                try:
                    import urllib.request

                    req = urllib.request.Request(
                        http_url, headers={"User-Agent": USER_AGENT}
                    )
                    with urllib.request.urlopen(req, timeout=0.5) as resp:
                        if resp.status in (200, 206):
                            ready = True
                            break
                except Exception:
                    pass
                time.sleep(0.4)

            # Launch native MPV connected to localhost:8888
            try:
                return launch_player(
                    http_url,
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
            finally:
                try:
                    server_proc.terminate()
                    server_proc.wait(timeout=2)
                except Exception:
                    server_proc.kill()
                shutil.rmtree("/tmp/torrent-stream", ignore_errors=True)
        else:
            print(
                f"\n{C_CYAN}{C_BOLD}🧲 Magnet stream resolved via Nyaa P2P Fallback:{C_RESET}"
            )
            print(f"{C_DIM}{target_path}{C_RESET}\n")
            copied = False
            if shutil.which("wl-copy"):
                try:
                    subprocess.run(
                        ["wl-copy"], input=target_path.encode("utf-8"), check=True
                    )
                    copied = True
                except Exception:
                    pass
            elif shutil.which("xclip"):
                try:
                    subprocess.run(
                        ["xclip", "-selection", "clipboard"],
                        input=target_path.encode("utf-8"),
                        check=True,
                    )
                    copied = True
                except Exception:
                    pass
            if copied:
                print(
                    f"{C_GREEN}✓ Copied magnet link to system clipboard! (Paste into qBittorrent or torrent player){C_RESET}"
                )
            print(
                f"{C_YELLOW}💡 Tip: To stream torrents directly in MPV without manual download, install webtorrent:{C_RESET}"
            )
            print(f"{C_DIM}   npm install -g webtorrent-cli{C_RESET}\n")
            return True

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
        cmd.extend(
            [
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
            ]
        )
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

    ipc_path = r"\\.\pipe\ani-sync-mpv-pipe" if IS_WINDOWS else "/tmp/ani-sync-mpv.sock"
    if player_bin == "mpv" or "mpv" in Path(player_bin).stem.lower():
        cmd.append(f"--input-ipc-server={ipc_path}")

    stop_ipc = threading.Event()
    ipc_thread = threading.Thread(
        target=poll_mpv_ipc, args=(ipc_path, stop_ipc), daemon=True
    )
    ipc_thread.start()

    DiscordRPC.start_activity(title, ep_num)
    try:
        proc = subprocess.run(cmd)
        return (proc.returncode == 0, _LAST_MPV_TIME_POS)
    finally:
        stop_ipc.set()
        DiscordRPC.stop_activity()
