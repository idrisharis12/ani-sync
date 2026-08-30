#!/usr/bin/env python3
"""
ani-sync – a thin wrapper around ani-cli that also updates MyAnimeList.

Usage:
    ani-sync watch <episode-url> [--player mpv]

Prerequisites:
    * ani-cli installed (pip)
    * MAL OAuth env vars: MAL_CLIENT_ID, MAL_CLIENT_SECRET, MAL_REFRESH_TOKEN
"""

import os
import sys
import subprocess
import re
import json
from pathlib import Path

import requests
from tqdm import tqdm

# ----------------------------------------------------------------------
# MAL helper functions
# ----------------------------------------------------------------------
TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"
API_URL   = "https://api.myanimelist.net/v2"

def _load_env():
    """Read required env vars – abort with a clear message if missing."""
    client_id     = os.getenv("MAL_CLIENT_ID")
    client_secret = os.getenv("MAL_CLIENT_SECRET")
    refresh_token = os.getenv("MAL_REFRESH_TOKEN")
    missing = [k for k, v in [
               ("MAL_CLIENT_ID", client_id),
               ("MAL_CLIENT_SECRET", client_secret),
               ("MAL_REFRESH_TOKEN", refresh_token)] if not v]
    if missing:
        sys.exit(f"Error: Missing environment variable(s): {', '.join(missing)}")
    return client_id, client_secret, refresh_token

def _refresh_access_token():
    """Use the stored refresh token to obtain a fresh access token."""
    client_id, client_secret, refresh_token = _load_env()
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    r = requests.post(TOKEN_URL, data=data, timeout=10)
    if r.status_code != 200:
        sys.exit(f"Failed to refresh MAL token: {r.text}")
    token = r.json()
    return token["access_token"]

def _search_anime(title):
    """Return MAL anime ID for a given title (best‑match)."""
    token = _refresh_access_token()
    params = {"q": title, "limit": 1}
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_URL}/anime", params=params, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data["data"]:
        sys.exit(f"⚠️  No MAL entry found for title: {title}")
    return data["data"][0]["node"]["id"]

def _mark_episode_watched(anime_id, episode_number):
    """POST to MAL to mark a specific episode as watched."""
    token = _refresh_access_token()
    url = f"{API_URL}/anime/{anime_id}/my_list_status"
    payload = {
        "num_watched_episodes": episode_number,
        "status": "watching"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.patch(url, data=payload, headers=headers, timeout=10)
    if r.status_code not in (200, 201):
        sys.exit(f"❌  MAL update failed: {r.text}")
    print(f"✅  MAL updated – episode {episode_number} of anime ID {anime_id} marked as watched.")

# ----------------------------------------------------------------------
# ani-cli handling
# ----------------------------------------------------------------------
def _run_ani_watch(url, player):
    """Run `ani watch` and capture stdout (which contains title/episode)."""
    cmd = ["ani", "watch", url, "--player", player, "--no-player"]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        sys.exit(f"ani-cli error:\n{result.stdout}")
    title = None
    episode = None
    for line in result.stdout.splitlines():
        if line.lower().startswith("title:"):
            title = line.split(":", 1)[1].strip()
        if line.lower().startswith("episode:"):
            ep_str = line.split(":", 1)[1].strip()
            episode = int(re.search(r"\d+", ep_str).group())
    if not title or not episode:
        sys.exit("Could not parse title/episode from ani-cli output.")
    return title, episode, result.stdout

def _launch_player(stream_url, player):
    """Spawn the actual media player (mpv, vlc, …) – let it take over."""
    subprocess.run([player, stream_url])

# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------
def main():
    if len(sys.argv) < 3 or sys.argv[1] != "watch":
        sys.exit("Usage: ani-sync watch <episode-url> [--player <player>]")
    episode_url = sys.argv[2]
    player = "mpv"
    if "--player" in sys.argv:
        idx = sys.argv.index("--player")
        if idx + 1 < len(sys.argv):
            player = sys.argv[idx + 1]
    title, ep_num, ani_output = _run_ani_watch(episode_url, player)
    stream_match = re.search(r"https?://\S+", ani_output)
    if not stream_match:
        sys.exit("Failed to locate stream URL in ani-cli output.")
    stream_url = stream_match.group()
    print(f"▶️  Launching {player} – {title} – Episode {ep_num}")
    _launch_player(stream_url, player)
    print("\n🔄  Syncing progress to MyAnimeList …")
    mal_anime_id = _search_anime(title)
    _mark_episode_watched(mal_anime_id, ep_num)

if __name__ == "__main__":
    main()
