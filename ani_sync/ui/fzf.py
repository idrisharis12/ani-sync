# -*- coding: utf-8 -*-
"""Interactive FZF fuzzy search caller and fallback menus."""

import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

from ani_sync.config import IS_WINDOWS, IS_TERMUX, log_debug
from ani_sync.ui.themes import (
    C_BOLD,
    C_CYAN,
    C_DIM,
    C_GREEN,
    C_RED,
    C_RESET,
    C_YELLOW,
    _FZF_THEME_COLORS,
)

_FZF_ENABLED = True


def _get_bin_dir():
    if IS_WINDOWS:
        local_app = os.environ.get("LOCALAPPDATA")
        if local_app:
            p = Path(local_app) / "ani-sync" / "bin"
        else:
            p = Path.home() / ".local" / "bin"
    else:
        p = Path.home() / ".local" / "bin"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _ensure_path():
    bin_dir = str(_get_bin_dir())
    current_path = os.environ.get("PATH", "")
    if bin_dir not in current_path:
        os.environ["PATH"] = f"{bin_dir}{os.pathsep}{current_path}"


def _has_fzf():
    _ensure_path()
    return shutil.which("fzf") is not None or shutil.which("fzf.exe") is not None


def _download_fzf_binary():
    """Download official standalone fzf binary from GitHub releases."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    bin_dir = _get_bin_dir()

    fzf_version = "0.60.3"
    fzf_exe = "fzf.exe" if system == "windows" else "fzf"
    target_path = bin_dir / fzf_exe
    if target_path.exists():
        return target_path

    if "x86_64" in machine or "amd64" in machine:
        arch = "amd64"
    elif "arm64" in machine or "aarch64" in machine:
        arch = "arm64"
    elif "arm" in machine:
        arch = "armv7"
    elif "386" in machine or "i686" in machine:
        arch = "386"
    else:
        arch = "amd64"

    if system == "windows":
        archive_name = f"fzf-{fzf_version}-windows_{arch}.zip"
    elif system == "darwin":
        archive_name = f"fzf-{fzf_version}-darwin_{arch}.tar.gz"
    elif system == "linux":
        archive_name = f"fzf-{fzf_version}-linux_{arch}.tar.gz"
    else:
        return None

    download_url = f"https://github.com/junegunn/fzf/releases/download/v{fzf_version}/{archive_name}"
    tmp_archive = bin_dir / archive_name

    try:
        urllib.request.urlretrieve(download_url, tmp_archive)
        if archive_name.endswith(".zip"):
            with zipfile.ZipFile(tmp_archive, "r") as zip_ref:
                zip_ref.extractall(bin_dir)
        elif archive_name.endswith(".tar.gz"):
            with tarfile.open(tmp_archive, "r:gz") as tar_ref:
                tar_ref.extractall(bin_dir)
        tmp_archive.unlink(missing_ok=True)
        if target_path.exists():
            target_path.chmod(0o755)
            _ensure_path()
            return target_path
    except Exception as e:
        log_debug(f"FZF auto-download error: {e}")
        tmp_archive.unlink(missing_ok=True)
    return None


def run_fzf_menu(items, prompt="Select: ", header="", preview=None):
    """Run interactive FZF fuzzy menu with numbered menu fallback."""
    if not items:
        return None

    if _FZF_ENABLED and not _has_fzf():
        _download_fzf_binary()

    fzf_bin = shutil.which("fzf") or shutil.which("fzf.exe")
    if _FZF_ENABLED and fzf_bin:
        cmd = [
            fzf_bin,
            "--ansi",
            "--height=40%",
            "--layout=reverse",
            "--border=rounded",
            f"--prompt=🔍 {prompt} ❯ ",
            f"--color={_FZF_THEME_COLORS}",
            "--pointer=▶",
            "--marker=✓",
        ]
        if header:
            cmd.append(f"--header=📺  ani-sync  ❯  {header}\n")

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            )
            stdout, _ = proc.communicate(input="\n".join(items))
            selected = stdout.strip()
            return selected if selected else None
        except Exception:
            pass

    # Numbered fallback menu
    print(f"\n{C_CYAN}{C_BOLD}--- {header or prompt} ---{C_RESET}")
    for idx, item in enumerate(items, 1):
        clean_item = item
        import re

        clean_item = re.sub(r"\033\[[0-9;]*m", "", clean_item)
        print(f"  {C_GREEN}{idx:2d}.{C_RESET} {clean_item}")

    while True:
        try:
            choice = input(
                f"\n{C_BOLD}Select number [1-{len(items)}] (or 'q' to quit): {C_RESET}"
            ).strip()
            if choice.lower() in ("q", "quit", "exit"):
                return None
            if choice.isdigit() and 1 <= int(choice) <= len(items):
                return items[int(choice) - 1]
            print(f"{C_RED}Invalid selection. Please enter 1-{len(items)}.{C_RESET}")
        except (KeyboardInterrupt, EOFError):
            print()
            return None
