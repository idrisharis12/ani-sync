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
import secrets
import webbrowser
import urllib.parse
from pathlib import Path

import requests
from tqdm import tqdm

# ----------------------------------------------------------------------
# Config & Environment Handling
# ----------------------------------------------------------------------
CONFIG_PATH = Path.home() / ".config" / "ani-sync" / "config.env"
TOKEN_URL   = "https://myanimelist.net/v1/oauth2/token"
AUTH_URL    = "https://myanimelist.net/v1/oauth2/authorize"
API_URL     = "https://api.myanimelist.net/v2"

def _load_config_file():
    """Load config from ~/.config/ani-sync/config.env if present."""
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

def _load_env():
    """Read required env vars – abort with a clear message if missing."""
    _load_config_file()
    client_id     = os.getenv("MAL_CLIENT_ID")
    client_secret = os.getenv("MAL_CLIENT_SECRET", "")
    refresh_token = os.getenv("MAL_REFRESH_TOKEN")
    
    missing = []
    if not client_id:
        missing.append("MAL_CLIENT_ID")
    if not refresh_token:
        missing.append("MAL_REFRESH_TOKEN")
        
    if missing:
        sys.exit(
            f"❌ Error: Missing configuration: {', '.join(missing)}\n"
            f"👉 Run 'ani-sync auth' to set up your MyAnimeList credentials easily,\n"
            f"   or set the environment variables in your ~/.bashrc / ~/.zshrc."
        )
    return client_id, client_secret, refresh_token

# ----------------------------------------------------------------------
# Interactive MAL Authentication Helper
# ----------------------------------------------------------------------
def run_auth():
    """Interactive OAuth2 PKCE setup for MyAnimeList."""
    print("=" * 60)
    print("         ani-sync — MyAnimeList Authentication Setup        ")
    print("=" * 60)
    print("\n1. Go to: https://myanimelist.net/apiconfig")
    print("2. Create a new Client / Application with:")
    print("   - App Type: other")
    print("   - Redirect URL: http://localhost")
    print("=" * 60)
    
    client_id = input("\nEnter your MAL Client ID: ").strip()
    if not client_id:
        sys.exit("Error: Client ID is required.")
        
    client_secret = input("Enter your MAL Client Secret (press Enter if none): ").strip()
    
    code_verifier = secrets.token_urlsafe(100)[:128]
    
    params = {
        "response_type": "code",
        "client_id": client_id,
        "code_challenge": code_verifier,
        "code_challenge_method": "plain",
    }
    auth_link = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    
    print("\n" + "-" * 60)
    print("Opening browser for authorization...")
    print("If it doesn't open automatically, visit:")
    print(auth_link)
    print("-" * 60)
    
    try:
        webbrowser.open(auth_link)
    except Exception:
        pass
        
    print("\nAfter clicking 'Allow', you will be redirected to:")
    print("  http://localhost/?code=AUTHORIZATION_CODE")
    
    auth_input = input("\nEnter the 'code' parameter (or the full redirect URL): ").strip()
    if "code=" in auth_input:
        parsed = urllib.parse.urlparse(auth_input)
        query_params = urllib.parse.parse_qs(parsed.query)
        auth_code = query_params.get("code", [auth_input.split("code=")[1].split("&")[0]])[0]
    else:
        auth_code = auth_input

    if not auth_code:
        sys.exit("Error: Authorization code cannot be empty.")
        
    print("\nExchanging authorization code for tokens...")
    data = {
        "client_id": client_id,
        "grant_type": "authorization_code",
        "code": auth_code,
        "code_verifier": code_verifier,
    }
    if client_secret:
        data["client_secret"] = client_secret
        
    res = requests.post(TOKEN_URL, data=data)
    if res.status_code != 200:
        print(f"\n❌ Error ({res.status_code}): {res.text}")
        sys.exit(1)
        
    tokens = res.json()
    refresh_token = tokens.get("refresh_token")
    
    # Save to config file
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(f"export MAL_CLIENT_ID=\"{client_id}\"\n")
        f.write(f"export MAL_CLIENT_SECRET=\"{client_secret}\"\n")
        f.write(f"export MAL_REFRESH_TOKEN=\"{refresh_token}\"\n")
        
    print("\n" + "=" * 60)
    print("✅ Authorization Successful!")
    print(f"📁 Credentials saved to: {CONFIG_PATH}")
    print("=" * 60)
    print("\nYou're ready to use ani-sync!")

# ----------------------------------------------------------------------
# MAL helper functions
# ----------------------------------------------------------------------
def _refresh_access_token():
    """Use the stored refresh token to obtain a fresh access token."""
    client_id, client_secret, refresh_token = _load_env()
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }
    if client_secret:
        data["client_secret"] = client_secret
        
    r = requests.post(TOKEN_URL, data=data, timeout=10)
    if r.status_code != 200:
        sys.exit(f"Failed to refresh MAL token: {r.text}")
    token = r.json()
    
    # If a new refresh token is returned, update config
    new_refresh = token.get("refresh_token")
    if new_refresh and new_refresh != refresh_token and CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                f.write(f"export MAL_CLIENT_ID=\"{client_id}\"\n")
                f.write(f"export MAL_CLIENT_SECRET=\"{client_secret}\"\n")
                f.write(f"export MAL_REFRESH_TOKEN=\"{new_refresh}\"\n")
        except Exception:
            pass
            
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

def print_help():
    print("""ani-sync — Watch anime via ani-cli and auto-sync progress to MyAnimeList

Usage:
    ani-sync watch <episode-url> [--player <player>]
    ani-sync auth
    ani-sync --help

Commands:
    watch <url>      Stream anime episode with ani-cli and sync progress to MAL
    auth             Run interactive MyAnimeList OAuth2 authentication setup
    --help, -h       Show this help message

Options:
    --player <name>  Custom media player executable (default: mpv)
""")

# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------
def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print_help()
        sys.exit(0)

    if sys.argv[1] in ("auth", "setup", "--auth"):
        run_auth()
        sys.exit(0)

    if sys.argv[1] != "watch" or len(sys.argv) < 3:
        print_help()
        sys.exit(1)

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

