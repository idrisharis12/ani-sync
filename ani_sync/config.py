# -*- coding: utf-8 -*-
"""Configuration, environment handling, and local watch history management."""

import json
import os
import re
import sys
import time
from pathlib import Path

VERSION = "2.10.3"

IS_WINDOWS = sys.platform == "win32"
IS_TERMUX = (
    "TERMUX_VERSION" in os.environ
    or "/data/data/com.termux" in os.environ.get("PREFIX", "")
    or Path("/data/data/com.termux").exists()
)

if IS_WINDOWS:
    os.system("")
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass


def get_config_dir():
    """Return OS-appropriate config directory (AppData on Windows, ~/.config on Linux/macOS/Termux)."""
    if IS_WINDOWS:
        appdata = os.environ.get("APPDATA")
        p = (
            Path(appdata) / "ani-sync"
            if appdata
            else Path.home() / ".config" / "ani-sync"
        )
    else:
        p = Path.home() / ".config" / "ani-sync"
    try:
        p.mkdir(parents=True, exist_ok=True)
        if not IS_WINDOWS:
            os.chmod(p, 0o700)
    except Exception:
        pass
    return p


def get_cache_dir():
    """Return ultra-fast RAM disk /dev/shm on Linux, or standard cache dir on Windows/macOS/Termux."""
    if IS_TERMUX:
        termux_tmp = os.environ.get("TMPDIR") or (os.environ.get("PREFIX", "") + "/tmp")
        if termux_tmp and Path(termux_tmp).exists():
            p = Path(termux_tmp) / "ani-sync"
        else:
            p = Path.home() / ".cache" / "ani-sync"
        p.mkdir(parents=True, exist_ok=True)
        return p

    if not IS_WINDOWS:
        shm = Path("/dev/shm/ani-sync")
        try:
            if Path("/dev/shm").exists() and hasattr(os, "statvfs"):
                st = os.statvfs("/dev/shm")
                free_bytes = st.f_bavail * st.f_frsize
                if free_bytes > 512 * 1024 * 1024:  # > 512MB free RAM
                    shm.mkdir(parents=True, exist_ok=True)
                    return shm
        except Exception:
            pass
        fallback = Path.home() / ".cache" / "ani-sync"
    else:
        temp_dir = os.environ.get("TEMP") or os.environ.get("LOCALAPPDATA")
        if temp_dir:
            fallback = Path(temp_dir) / "ani-sync"
        else:
            fallback = Path.home() / ".cache" / "ani-sync"

    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


CONFIG_DIR = get_config_dir()
CONFIG_PATH = CONFIG_DIR / "config.env"
HISTORY_PATH = CONFIG_DIR / "history.json"
CACHE_DIR = get_cache_dir()

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

VERBOSE = False


def log_debug(msg):
    """Print debug log when VERBOSE is enabled."""
    if VERBOSE:
        print(f"\033[2m[DEBUG] {msg}\033[0m")


def load_config():
    """Load configuration from ~/.config/ani-sync/config.env if present."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        key = key.replace("export ", "").strip()
                        val = val.strip().strip("'\"")
                        if key not in os.environ:
                            os.environ[key] = val
        except Exception:
            pass


def _append_config(key, value):
    """Append or update a key in config.env with secure 0600 file permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    found = False
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#") and "=" in stripped:
                    line_key = stripped.replace("export ", "").split("=", 1)[0].strip()
                    if line_key == key:
                        lines.append(f'export {key}="{value}"\n')
                        found = True
                        continue
                lines.append(line if line.endswith("\n") else line + "\n")
    if not found:
        lines.append(f'export {key}="{value}"\n')
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    if not IS_WINDOWS:
        try:
            os.chmod(CONFIG_PATH, 0o600)
        except Exception:
            pass
    os.environ[key] = str(value)


def sanitize_filename(name):
    """Clean title string for safe filesystem filename."""
    return re.sub(r"[^\w\-_\. ]", "_", name).strip()


def load_history():
    """Load local watch history."""
    if HISTORY_PATH.exists():
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_watched": None, "history": []}


def save_history(slug, title, episode_num, quality="720p", mode="sub"):
    """Record watched episode to local history."""
    data = load_history()
    entry = {
        "slug": slug,
        "title": title,
        "episode": episode_num,
        "quality": quality,
        "mode": mode,
        "timestamp": int(time.time()),
    }
    data["last_watched"] = entry
    data["total_episodes_watched"] = data.get("total_episodes_watched", 0) + 1

    history_list = [h for h in data.get("history", []) if h.get("slug") != slug]
    history_list.insert(0, entry)
    data["history"] = history_list[:50]

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def get_last_watched():
    """Return the last watched anime entry from history."""
    data = load_history()
    return data.get("last_watched")
