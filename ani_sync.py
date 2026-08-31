#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""":"
exec python3 "$0" "$@"
"""

import concurrent.futures
import html
import io
import json
import os
import platform
import re
import secrets
import shutil
import subprocess
import sys
import tarfile
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
import zipfile
from pathlib import Path

import requests

# Enable ANSI colors & UTF-8 on Windows Command Prompt & PowerShell
if sys.platform == "win32":
    os.system("")
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass


def get_config_dir():
    """Return OS-appropriate config directory (AppData on Windows, ~/.config on Linux/macOS)."""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "ani-sync"
    return Path.home() / ".config" / "ani-sync"


def get_cache_dir():
    """Return ultra-fast RAM disk /dev/shm on Linux, or standard cache dir on Windows/macOS."""
    if sys.platform != "win32":
        shm = Path("/dev/shm/ani-sync")
        try:
            if Path("/dev/shm").exists() and hasattr(os, "statvfs"):
                st = os.statvfs("/dev/shm")
                free_bytes = st.f_bavail * st.f_frsize
                if free_bytes > 1024 * 1024 * 1024:  # > 1GB free RAM
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


VERSION = "2.0.0"
CONFIG_DIR = get_config_dir()
CONFIG_PATH = CONFIG_DIR / "config.env"
HISTORY_PATH = CONFIG_DIR / "history.json"
CACHE_DIR = get_cache_dir()

ANIDB_BASE = "https://anidb.app"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"
AUTH_URL = "https://myanimelist.net/v1/oauth2/authorize"
API_URL = "https://api.myanimelist.net/v2"

# AniList GraphQL API
ANILIST_API_URL = "https://graphql.anilist.co"
ANILIST_AUTH_URL = "https://anilist.co/api/v2/oauth/authorize"
ANILIST_TOKEN_URL = "https://anilist.co/api/v2/oauth/token"
ANILIST_REDIRECT_URI = "https://anilist.co/api/v2/oauth/pin"

# Kitsu JSON:API
KITSU_API_URL = "https://kitsu.io/api/edge"
KITSU_TOKEN_URL = "https://kitsu.io/api/oauth/token"

# Terminal Colors
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_MAGENTA = "\033[95m"
C_RED = "\033[91m"
C_WHITE = "\033[97m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_RESET = "\033[0m"


# ----------------------------------------------------------------------
# Config & Environment Handling
# ----------------------------------------------------------------------
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
    """Append or update a key in config.env without overwriting other keys."""
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
    os.environ[key] = str(value)


def save_config(client_id, client_secret, refresh_token):
    """Safely update MAL config keys without touching other platform tokens."""
    _append_config("MAL_CLIENT_ID", client_id)
    if client_secret:
        _append_config("MAL_CLIENT_SECRET", client_secret)
    _append_config("MAL_REFRESH_TOKEN", refresh_token)


def get_mal_env():
    load_config()
    client_id = os.getenv("MAL_CLIENT_ID", "").strip()
    client_secret = os.getenv("MAL_CLIENT_SECRET", "").strip()
    refresh_token = os.getenv("MAL_REFRESH_TOKEN", "").strip()
    return client_id, client_secret, refresh_token


def is_mal_configured():
    client_id, _, refresh_token = get_mal_env()
    return bool(client_id and refresh_token)


# ----------------------------------------------------------------------
# Interactive MAL Authentication Helper
# ----------------------------------------------------------------------
def run_auth():
    print(
        f"\n{C_CYAN}{C_BOLD}============================================================{C_RESET}"
    )
    print(
        f"{C_MAGENTA}{C_BOLD}         ani-sync — MyAnimeList Authentication Setup        {C_RESET}"
    )
    print(
        f"{C_CYAN}{C_BOLD}============================================================{C_RESET}"
    )
    print(f"\n1. Go to: {C_BLUE}https://myanimelist.net/apiconfig{C_RESET}")
    print(f"2. Click {C_BOLD}'Create ID'{C_RESET} with the following settings:")
    print(f"   - {C_BOLD}App Name:{C_RESET} ani-sync")
    print(f"   - {C_BOLD}App Type:{C_RESET} other")
    print(f"   - {C_BOLD}Redirect URL:{C_RESET} http://localhost")
    print(
        f"{C_CYAN}------------------------------------------------------------{C_RESET}"
    )

    client_id = input(f"\n{C_BOLD}Enter your MAL Client ID: {C_RESET}").strip()
    if not client_id:
        print(f"{C_RED}Error: Client ID is required.{C_RESET}")
        return

    client_secret = input(
        f"{C_BOLD}Enter your MAL Client Secret (press Enter if none): {C_RESET}"
    ).strip()
    code_verifier = secrets.token_urlsafe(100)[:128]

    params = {
        "response_type": "code",
        "client_id": client_id,
        "code_challenge": code_verifier,
        "code_challenge_method": "plain",
    }
    auth_link = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    print(f"\n{C_YELLOW}Opening browser for authorization...{C_RESET}")
    print(f"If your browser doesn't open automatically, visit this URL:")
    print(f"{C_BLUE}{auth_link}{C_RESET}\n")

    try:
        webbrowser.open(auth_link)
    except Exception:
        pass

    print(
        f"After logging in and clicking '{C_BOLD}Allow{C_RESET}', you will be redirected to:"
    )
    print(f"  {C_DIM}http://localhost/?code=AUTHORIZATION_CODE{C_RESET}")

    auth_input = input(
        f"\n{C_BOLD}Paste the redirected URL (or the 'code' parameter): {C_RESET}"
    ).strip()
    if "code=" in auth_input:
        parsed = urllib.parse.urlparse(auth_input)
        query_params = urllib.parse.parse_qs(parsed.query)
        auth_code = query_params.get(
            "code", [auth_input.split("code=")[1].split("&")[0]]
        )[0]
    else:
        auth_code = auth_input

    if not auth_code:
        print(f"{C_RED}Error: Authorization code cannot be empty.{C_RESET}")
        return

    print(f"\n{C_CYAN}Exchanging authorization code for tokens...{C_RESET}")
    data = {
        "client_id": client_id,
        "grant_type": "authorization_code",
        "code": auth_code,
        "code_verifier": code_verifier,
    }
    if client_secret:
        data["client_secret"] = client_secret

    try:
        res = requests.post(TOKEN_URL, data=data, timeout=15)
        if res.status_code != 200:
            print(f"{C_RED}❌ OAuth Error ({res.status_code}): {res.text}{C_RESET}")
            return
        tokens = res.json()
        refresh_token = tokens.get("refresh_token")
        save_config(client_id, client_secret, refresh_token)
        print(f"\n{C_GREEN}{C_BOLD}✅ Authorization Successful!{C_RESET}")
        print(f"📁 Credentials saved to: {C_CYAN}{CONFIG_PATH}{C_RESET}")
        sync_all_libraries()
    except Exception as e:
        print(f"{C_RED}❌ Connection error: {e}{C_RESET}")


# ----------------------------------------------------------------------
# MyAnimeList Syncing
# ----------------------------------------------------------------------
def refresh_mal_token():
    client_id, client_secret, refresh_token = get_mal_env()
    if not client_id or not refresh_token:
        return None
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }
    if client_secret:
        data["client_secret"] = client_secret
    try:
        r = requests.post(TOKEN_URL, data=data, timeout=10)
        if r.status_code == 200:
            token_json = r.json()
            new_refresh = token_json.get("refresh_token")
            if new_refresh and new_refresh != refresh_token:
                save_config(client_id, client_secret, new_refresh)
            return token_json.get("access_token")
    except Exception:
        pass
    return None


def sync_episode_to_mal(anime_title, episode_num, mal_id=None, quiet=False):
    """Sync episode progress to MyAnimeList."""
    if not is_mal_configured():
        if not quiet:
            print(
                f"{C_YELLOW}ℹ️  MAL sync skipped (Run 'ani-sync auth' to connect MyAnimeList){C_RESET}"
            )
        return False, "Not configured"

    if not quiet:
        print(f"\n{C_CYAN}🔄  Syncing episode {episode_num} to MyAnimeList...{C_RESET}")
    access_token = refresh_mal_token()
    if not access_token:
        if not quiet:
            print(
                f"{C_RED}⚠️  Failed to refresh MyAnimeList access token. Try running 'ani-sync auth'.{C_RESET}"
            )
        return False, "Token refresh failed"

    headers = {"Authorization": f"Bearer {access_token}"}

    # If MAL ID not provided, search by title
    if not mal_id:
        try:
            search_res = requests.get(
                f"{API_URL}/anime",
                params={"q": anime_title, "limit": 1},
                headers=headers,
                timeout=8,
            )
            if search_res.status_code == 200:
                data = search_res.json()
                if data.get("data"):
                    mal_id = data["data"][0]["node"]["id"]
                    found_title = data["data"][0]["node"].get("title", anime_title)
        except Exception:
            pass

    if not mal_id:
        if not quiet:
            print(
                f"{C_YELLOW}⚠️  Could not find MAL entry for '{anime_title}'{C_RESET}"
            )
        return False, f"Anime not found on MAL"

    try:
        update_url = f"{API_URL}/anime/{mal_id}/my_list_status"
        payload = {
            "num_watched_episodes": episode_num,
            "status": "watching",
        }
        res = requests.patch(
            update_url,
            data=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=8,
        )
        if res.status_code in (200, 201):
            if not quiet:
                print(
                    f"{C_GREEN}{C_BOLD}✅  MAL Synced:{C_RESET} Episode {episode_num} marked as watched!"
                )
            return True, f"Episode {episode_num} marked as watched"
        else:
            if not quiet:
                print(
                    f"{C_RED}❌  MAL Sync update failed ({res.status_code}): {res.text}{C_RESET}"
                )
            return False, f"HTTP {res.status_code} Error"
    except Exception as e:
        if not quiet:
            print(f"{C_RED}❌  MAL Sync error: {e}{C_RESET}")
        return False, str(e)


# ----------------------------------------------------------------------
# AniList Tracking (GraphQL API)
# ----------------------------------------------------------------------
ANILIST_SEARCH_QUERY = """
query ($search: String) {
  Media (search: $search, type: ANIME) {
    id
    title { romaji english userPreferred }
    episodes
  }
}
"""

ANILIST_UPDATE_MUTATION = """
mutation ($mediaId: Int, $progress: Int, $status: MediaListStatus) {
  SaveMediaListEntry (mediaId: $mediaId, progress: $progress, status: $status) {
    id mediaId status progress
  }
}
"""


def is_anilist_configured():
    load_config()
    return bool(os.getenv("ANILIST_TOKEN", "").strip())


def run_anilist_auth():
    """Interactive AniList OAuth2 setup wizard."""
    print(
        f"\n{C_CYAN}{C_BOLD}============================================================{C_RESET}"
    )
    print(
        f"{C_MAGENTA}{C_BOLD}         ani-sync — AniList Authentication Setup            {C_RESET}"
    )
    print(
        f"{C_CYAN}{C_BOLD}============================================================{C_RESET}"
    )
    print(f"\n1. Go to: {C_BLUE}https://anilist.co/settings/developer{C_RESET}")
    print(f"2. Click {C_BOLD}'Create New Client'{C_RESET} with these settings:")
    print(f"   - {C_BOLD}Name:{C_RESET} ani-sync")
    print(f"   - {C_BOLD}Redirect URL:{C_RESET} https://anilist.co/api/v2/oauth/pin")
    print(
        f"{C_CYAN}------------------------------------------------------------{C_RESET}"
    )

    load_config()
    default_cid = os.getenv("ANILIST_CLIENT_ID", "").strip()
    default_secret = os.getenv("ANILIST_CLIENT_SECRET", "").strip()

    cid_prompt = (
        f"\n{C_BOLD}Enter your AniList Client ID (default: {default_cid}): {C_RESET}"
        if default_cid
        else f"\n{C_BOLD}Enter your AniList Client ID: {C_RESET}"
    )
    client_id = input(cid_prompt).strip() or default_cid
    if not client_id:
        print(f"{C_RED}Error: Client ID is required.{C_RESET}")
        return

    secret_prompt = (
        f"{C_BOLD}Enter your AniList Client Secret (default: [saved]): {C_RESET}"
        if default_secret
        else f"{C_BOLD}Enter your AniList Client Secret: {C_RESET}"
    )
    client_secret = input(secret_prompt).strip() or default_secret

    auth_link = (
        f"{ANILIST_AUTH_URL}?client_id={client_id}"
        f"&redirect_uri={ANILIST_REDIRECT_URI}&response_type=code"
    )
    print(f"\n{C_YELLOW}Opening browser for authorization...{C_RESET}")
    print(f"If browser doesn't open, visit: {C_BLUE}{auth_link}{C_RESET}\n")
    try:
        webbrowser.open(auth_link)
    except Exception:
        pass

    auth_code = input(
        f"\n{C_BOLD}Paste the authorization code shown on the page: {C_RESET}"
    ).strip()
    if not auth_code:
        print(f"{C_RED}Error: Authorization code is required.{C_RESET}")
        return

    print(f"\n{C_CYAN}Exchanging code for AniList access token...{C_RESET}")
    try:
        res = requests.post(
            ANILIST_TOKEN_URL,
            json={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": ANILIST_REDIRECT_URI,
                "code": auth_code,
            },
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=15,
        )
        if res.status_code != 200:
            print(
                f"{C_RED}❌ AniList OAuth Error ({res.status_code}): {res.text}{C_RESET}"
            )
            return
        token = res.json().get("access_token", "")
        # Append to config.env
        _append_config("ANILIST_TOKEN", token)
        print(f"\n{C_GREEN}{C_BOLD}✅ AniList Authorization Successful!{C_RESET}")
        print(f"📁 Token saved to: {C_CYAN}{CONFIG_PATH}{C_RESET}")
        sync_all_libraries()
    except Exception as e:
        print(f"{C_RED}❌ Connection error: {e}{C_RESET}")


def sync_episode_to_anilist(anime_title, episode_num, quiet=False):
    """Sync episode progress to AniList."""
    if not is_anilist_configured():
        return False, "Not configured"
    token = os.getenv("ANILIST_TOKEN", "").strip()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        # Search for anime
        clean_search = re.sub(r'["\\]', "", anime_title)
        search_query = f'{{ Media (search: "{clean_search}", type: ANIME) {{ id title {{ romaji english userPreferred }} episodes }} }}'
        res = requests.post(
            ANILIST_API_URL,
            json={"query": search_query},
            headers={"Content-Type": "application/json"},
            timeout=8,
        )
        media = (
            res.json().get("data", {}).get("Media") if res.status_code == 200 else None
        )
        if not media:
            return False, "Anime not found on AniList"
        media_id = media["id"]
        total_eps = media.get("episodes")
        status = "COMPLETED" if total_eps and episode_num >= total_eps else "CURRENT"
        # Update progress
        update_mutation = f"""
        mutation {{
          SaveMediaListEntry (mediaId: {media_id}, progress: {episode_num}, status: {status}) {{
            id mediaId status progress
          }}
        }}
        """
        res = requests.post(
            ANILIST_API_URL,
            json={"query": update_mutation},
            headers=headers,
            timeout=8,
        )
        if res.status_code == 200:
            entry = res.json().get("data", {}).get("SaveMediaListEntry", {})
            status_text = entry.get("status", status).lower()
            if not quiet:
                print(
                    f"{C_GREEN}{C_BOLD}✅  AniList Synced:{C_RESET} Episode {entry.get('progress', episode_num)} marked as {status_text}!"
                )
            return True, f"Episode {episode_num} marked as {status_text}"
    except Exception as e:
        if not quiet:
            print(f"{C_RED}❌  AniList Sync error: {e}{C_RESET}")
        return False, str(e)
    return False, "Failed"


# ----------------------------------------------------------------------
# Kitsu Tracking (JSON:API)
# ----------------------------------------------------------------------
def is_kitsu_configured():
    load_config()
    return bool(os.getenv("KITSU_TOKEN", "").strip())


def run_kitsu_auth():
    """Interactive Kitsu authentication setup (username/password grant)."""
    print(
        f"\n{C_CYAN}{C_BOLD}============================================================{C_RESET}"
    )
    print(
        f"{C_MAGENTA}{C_BOLD}         ani-sync — Kitsu Authentication Setup              {C_RESET}"
    )
    print(
        f"{C_CYAN}{C_BOLD}============================================================{C_RESET}"
    )
    print(f"\n{C_YELLOW}Kitsu uses email/password authentication.{C_RESET}")
    print(f"Your credentials are sent directly to Kitsu and are NOT stored locally.\n")

    username = input(f"{C_BOLD}Enter your Kitsu email or username: {C_RESET}").strip()
    if not username:
        print(f"{C_RED}Error: Email/username is required.{C_RESET}")
        return

    import getpass

    password = getpass.getpass(f"{C_BOLD}Enter your Kitsu password: {C_RESET}")
    if not password:
        print(f"{C_RED}Error: Password is required.{C_RESET}")
        return

    print(f"\n{C_CYAN}Authenticating with Kitsu...{C_RESET}")
    try:
        res = requests.post(
            KITSU_TOKEN_URL,
            data={"grant_type": "password", "username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )
        if res.status_code != 200:
            print(
                f"{C_RED}❌ Kitsu Auth Error ({res.status_code}): {res.text}{C_RESET}"
            )
            return
        token_data = res.json()
        access_token = token_data.get("access_token", "")
        refresh_token = token_data.get("refresh_token", "")
        _append_config("KITSU_TOKEN", access_token)
        _append_config("KITSU_REFRESH_TOKEN", refresh_token)
        print(f"\n{C_GREEN}{C_BOLD}✅ Kitsu Authorization Successful!{C_RESET}")
        print(f"📁 Token saved to: {C_CYAN}{CONFIG_PATH}{C_RESET}")
        sync_all_libraries()
    except Exception as e:
        print(f"{C_RED}❌ Connection error: {e}{C_RESET}")


def refresh_kitsu_token():
    """Refresh Kitsu access token using stored refresh token."""
    load_config()
    refresh_token = os.getenv("KITSU_REFRESH_TOKEN", "").strip()
    if not refresh_token:
        return None
    try:
        res = requests.post(
            KITSU_TOKEN_URL,
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        if res.status_code == 200:
            data = res.json()
            new_token = data.get("access_token", "")
            new_refresh = data.get("refresh_token", "")
            if new_token:
                _append_config("KITSU_TOKEN", new_token)
            if new_refresh:
                _append_config("KITSU_REFRESH_TOKEN", new_refresh)
            return new_token
    except Exception:
        pass
    return None


def sync_episode_to_kitsu(anime_title, episode_num, quiet=False):
    """Sync episode progress to Kitsu."""
    if not is_kitsu_configured():
        return False, "Not configured"
    token = os.getenv("KITSU_TOKEN", "").strip()
    kitsu_headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }
    try:
        # Search anime
        res = requests.get(
            f"{KITSU_API_URL}/anime",
            params={"filter[text]": anime_title, "page[limit]": 1},
            headers={"Accept": "application/vnd.api+json"},
            timeout=8,
        )
        if res.status_code != 200:
            return False, f"Kitsu search error ({res.status_code})"
        results = res.json().get("data", [])
        if not results:
            return False, "Anime not found on Kitsu"
        anime_id = results[0]["id"]

        # Get user ID
        res = requests.get(
            f"{KITSU_API_URL}/users?filter[self]=true",
            headers=kitsu_headers,
            timeout=8,
        )
        if res.status_code != 200:
            # Token might be expired, try refresh
            new_token = refresh_kitsu_token()
            if not new_token:
                return False, "Token refresh failed"
            kitsu_headers["Authorization"] = f"Bearer {new_token}"
            res = requests.get(
                f"{KITSU_API_URL}/users?filter[self]=true",
                headers=kitsu_headers,
                timeout=8,
            )
            if res.status_code != 200:
                return False, "User profile fetch failed"
        users = res.json().get("data", [])
        if not users:
            return False, "User profile not found"
        user_id = users[0]["id"]

        # Find existing library entry
        res = requests.get(
            f"{KITSU_API_URL}/library-entries",
            params={"filter[userId]": user_id, "filter[animeId]": anime_id},
            headers=kitsu_headers,
            timeout=8,
        )
        entries = res.json().get("data", []) if res.status_code == 200 else []

        if entries:
            entry_id = entries[0]["id"]
            res = requests.patch(
                f"{KITSU_API_URL}/library-entries/{entry_id}",
                json={
                    "data": {
                        "id": entry_id,
                        "type": "libraryEntries",
                        "attributes": {"progress": episode_num, "status": "current"},
                    }
                },
                headers=kitsu_headers,
                timeout=8,
            )
        else:
            res = requests.post(
                f"{KITSU_API_URL}/library-entries",
                json={
                    "data": {
                        "type": "libraryEntries",
                        "attributes": {"progress": episode_num, "status": "current"},
                        "relationships": {
                            "anime": {"data": {"type": "anime", "id": anime_id}},
                            "user": {"data": {"type": "users", "id": user_id}},
                        },
                    }
                },
                headers=kitsu_headers,
                timeout=8,
            )

        if res.status_code in (200, 201, 202):
            if not quiet:
                print(
                    f"{C_GREEN}{C_BOLD}✅  Kitsu Synced:{C_RESET} Episode {episode_num} marked as watching!"
                )
            return True, f"Episode {episode_num} marked as watching"
    except Exception as e:
        if not quiet:
            print(f"{C_RED}❌  Kitsu Sync error: {e}{C_RESET}")
        return False, str(e)
    return False, "Failed"


def sync_all_platforms(anime_title, episode_num, mal_id=None):
    """Sync episode progress to all configured tracking platforms in parallel and return results dictionary."""
    tasks = {}
    sync_results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        if is_mal_configured():
            tasks["MyAnimeList"] = executor.submit(
                sync_episode_to_mal, anime_title, episode_num, mal_id=mal_id, quiet=True
            )
        if is_anilist_configured():
            tasks["AniList"] = executor.submit(
                sync_episode_to_anilist, anime_title, episode_num, quiet=True
            )
        if is_kitsu_configured():
            tasks["Kitsu"] = executor.submit(
                sync_episode_to_kitsu, anime_title, episode_num, quiet=True
            )

        for p_name, future in tasks.items():
            try:
                ok, msg = future.result(timeout=4)
                sync_results[p_name] = (ok, msg)
            except Exception as e:
                sync_results[p_name] = (False, str(e))

    return sync_results


# ----------------------------------------------------------------------
# Multi-Platform Library Sync & Auto-Import Engine
# ----------------------------------------------------------------------
def fetch_mal_library():
    """Fetch user's watching and completed anime library from MyAnimeList."""
    if not is_mal_configured():
        return []
    token = refresh_mal_token()
    if not token:
        return []
    headers = {"Authorization": f"Bearer {token}"}
    results = []
    for status in ["watching", "completed"]:
        try:
            r = requests.get(
                f"{API_URL}/users/@me/animelist",
                params={
                    "fields": "list_status,num_episodes",
                    "limit": 100,
                    "status": status,
                },
                headers=headers,
                timeout=12,
            )
            if r.status_code == 200:
                data = r.json().get("data", [])
                for item in data:
                    node = item.get("node", {})
                    list_status = item.get("list_status", {})
                    title = node.get("title", "").strip()
                    ep = list_status.get("num_episodes_watched", 1)
                    if title:
                        results.append(
                            {
                                "title": title,
                                "episode": max(1, ep),
                                "status": list_status.get("status", status),
                                "platform": "MyAnimeList",
                            }
                        )
        except Exception:
            pass
    return results


def fetch_anilist_library():
    """Fetch user's watching and completed anime library from AniList."""
    if not is_anilist_configured():
        return []
    token = os.getenv("ANILIST_TOKEN", "").strip()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    results = []
    try:
        # Get viewer ID
        vr = requests.post(
            ANILIST_API_URL,
            json={"query": "{ Viewer { id name } }"},
            headers=headers,
            timeout=10,
        )
        if vr.status_code != 200:
            return []
        viewer_id = vr.json().get("data", {}).get("Viewer", {}).get("id")
        if not viewer_id:
            return []

        # Get media list collection
        list_query = f"""
        {{
          MediaListCollection (userId: {viewer_id}, type: ANIME, status_in: [CURRENT, COMPLETED, PAUSED]) {{
            lists {{
              name
              entries {{
                progress
                status
                media {{
                  id
                  title {{ userPreferred english romaji }}
                  episodes
                }}
              }}
            }}
          }}
        }}
        """
        lr = requests.post(
            ANILIST_API_URL,
            json={"query": list_query},
            headers=headers,
            timeout=12,
        )
        if lr.status_code == 200:
            lists = (
                lr.json()
                .get("data", {})
                .get("MediaListCollection", {})
                .get("lists", [])
            )
            for l in lists:
                for entry in l.get("entries", []):
                    media = entry.get("media", {})
                    titles = media.get("title", {})
                    title = (
                        titles.get("userPreferred")
                        or titles.get("english")
                        or titles.get("romaji")
                    )
                    progress = entry.get("progress", 1)
                    status = entry.get("status", "CURRENT").lower()
                    if title:
                        results.append(
                            {
                                "title": title,
                                "episode": max(1, progress),
                                "status": status,
                                "platform": "AniList",
                            }
                        )
    except Exception:
        pass
    return results


def fetch_kitsu_library():
    """Fetch user's watching and completed anime library from Kitsu."""
    if not is_kitsu_configured():
        return []
    token = os.getenv("KITSU_TOKEN", "").strip()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }
    results = []
    try:
        # Get user ID
        ur = requests.get(
            f"{KITSU_API_URL}/users?filter[self]=true", headers=headers, timeout=10
        )
        if ur.status_code != 200:
            new_token = refresh_kitsu_token()
            if not new_token:
                return []
            headers["Authorization"] = f"Bearer {new_token}"
            ur = requests.get(
                f"{KITSU_API_URL}/users?filter[self]=true", headers=headers, timeout=10
            )
            if ur.status_code != 200:
                return []
        users = ur.json().get("data", [])
        if not users:
            return []
        uid = users[0]["id"]

        # Fetch entries
        er = requests.get(
            f"{KITSU_API_URL}/library-entries?filter[userId]={uid}&include=anime&page[limit]=50",
            headers=headers,
            timeout=12,
        )
        if er.status_code == 200:
            data = er.json()
            anime_map = {}
            for inc in data.get("included", []):
                if inc.get("type") == "anime":
                    anime_map[inc["id"]] = inc.get("attributes", {}).get(
                        "canonicalTitle"
                    )
            entries = data.get("data", [])
            for e in entries:
                aid = (
                    e.get("relationships", {})
                    .get("anime", {})
                    .get("data", {})
                    .get("id")
                )
                title = anime_map.get(aid)
                progress = e.get("attributes", {}).get("progress", 1)
                status = e.get("attributes", {}).get("status", "current")
                if title:
                    results.append(
                        {
                            "title": title,
                            "episode": max(1, progress),
                            "status": status,
                            "platform": "Kitsu",
                        }
                    )
    except Exception:
        pass
    return results


def sync_all_libraries(quiet=False):
    """Import and merge user's watched anime libraries from MAL, AniList, and Kitsu into ani-sync."""
    load_config()
    mal_items = []
    anilist_items = []
    kitsu_items = []

    has_mal = is_mal_configured()
    has_al = is_anilist_configured()
    has_kt = is_kitsu_configured()

    if not (has_mal or has_al or has_kt):
        if not quiet:
            print(f"\n{C_YELLOW}ℹ️  No tracking platforms connected yet.{C_RESET}")
            print(
                f"Run {C_GREEN}ani-sync auth{C_RESET} to connect MyAnimeList, AniList, or Kitsu!"
            )
        return 0

    if not quiet:
        print(
            f"\n{C_CYAN}{C_BOLD}📥 Syncing Anime Libraries from Connected Platforms...{C_RESET}"
        )

    # Fetch in parallel for high performance
    threads = []

    def _mal():
        nonlocal mal_items
        mal_items = fetch_mal_library()

    def _al():
        nonlocal anilist_items
        anilist_items = fetch_anilist_library()

    def _kt():
        nonlocal kitsu_items
        kitsu_items = fetch_kitsu_library()

    if has_mal:
        t = threading.Thread(target=_mal)
        threads.append(t)
        t.start()
    if has_al:
        t = threading.Thread(target=_al)
        threads.append(t)
        t.start()
    if has_kt:
        t = threading.Thread(target=_kt)
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=15)

    if not quiet:
        if has_mal:
            print(f"  {C_GREEN}✓{C_RESET} MyAnimeList: {len(mal_items)} anime found")
        if has_al:
            print(
                f"  {C_GREEN}✓{C_RESET} AniList:     {len(anilist_items)} anime found"
            )
        if has_kt:
            print(f"  {C_GREEN}✓{C_RESET} Kitsu:       {len(kitsu_items)} anime found")

    total_fetched = mal_items + anilist_items + kitsu_items
    if not total_fetched:
        if not quiet:
            print(f"{C_YELLOW}No anime entries found on connected platforms.{C_RESET}")
        return 0

    # Merge into local history
    history_data = load_history()
    existing_history = history_data.get("history", [])
    history_map = {h.get("slug"): h for h in existing_history if h.get("slug")}
    title_to_slug = {
        h.get("title", "").lower(): h.get("slug")
        for h in existing_history
        if h.get("title")
    }

    merged_count = 0
    for item in total_fetched:
        raw_title = item["title"]
        ep = item["episode"]
        slug = title_to_slug.get(raw_title.lower())
        if not slug:
            slug = re.sub(r"[^\w\s-]", "", raw_title.lower()).strip().replace(" ", "-")
            title_to_slug[raw_title.lower()] = slug

        if slug in history_map:
            if ep > history_map[slug].get("episode", 1):
                history_map[slug]["episode"] = ep
        else:
            entry = {
                "slug": slug,
                "title": raw_title,
                "episode": ep,
                "quality": "720p",
                "mode": "sub",
                "platform": item["platform"],
                "timestamp": int(time.time()),
            }
            history_map[slug] = entry
            merged_count += 1

    merged_list = list(history_map.values())
    merged_list.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    history_data["history"] = merged_list[:100]
    if merged_list and not history_data.get("last_watched"):
        history_data["last_watched"] = merged_list[0]

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2)
    except Exception:
        pass

    if not quiet:
        print(
            f"\n{C_GREEN}{C_BOLD}✨ Library Sync Complete:{C_RESET} {len(merged_list)} anime tracked in ani-sync history!"
        )
    return len(merged_list)


# ----------------------------------------------------------------------
# Watch History & Resume Manager
# ----------------------------------------------------------------------
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
    """Record watched episode to local history and check for appreciation milestone."""
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

    # Increment total watched counter
    data["total_episodes_watched"] = data.get("total_episodes_watched", 0) + 1

    # Update list without duplicates
    history_list = [h for h in data.get("history", []) if h.get("slug") != slug]
    history_list.insert(0, entry)
    data["history"] = history_list[:50]  # Keep last 50

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

    # One-time friendly star prompt on 5th episode milestone
    if data.get("total_episodes_watched", 0) >= 5 and not data.get("star_prompt_shown"):
        data["star_prompt_shown"] = True
        try:
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
        print(
            f"\n{C_MAGENTA}╭────────────────────────────────────────────────────────────╮{C_RESET}"
        )
        print(
            f"{C_MAGENTA}│{C_RESET}  {C_YELLOW}{C_BOLD}✨ Enjoying ani-sync?{C_RESET}                                      {C_MAGENTA}│{C_RESET}"
        )
        print(
            f"{C_MAGENTA}│{C_RESET}  If you love streaming anime in your terminal, consider      {C_MAGENTA}│{C_RESET}"
        )
        print(
            f"{C_MAGENTA}│{C_RESET}  starring the project on GitHub:                            {C_MAGENTA}│{C_RESET}"
        )
        print(
            f"{C_MAGENTA}│{C_RESET}  {C_CYAN}{C_BOLD}⭐ https://github.com/idrisharis12/ani-sync{C_RESET}                 {C_MAGENTA}│{C_RESET}"
        )
        print(
            f"{C_MAGENTA}╰────────────────────────────────────────────────────────────╯{C_RESET}\n"
        )


def get_last_watched():
    """Return the last watched anime entry from history."""
    data = load_history()
    return data.get("last_watched")


# ----------------------------------------------------------------------
# Discord Rich Presence (Zero-Dependency IPC)
# ----------------------------------------------------------------------
class DiscordRPC:
    """Zero-dependency Discord Rich Presence client via local IPC socket."""

    _sock = None
    _thread = None
    _active = False

    @classmethod
    def start_activity(cls, title, ep_num):
        """Start persistent Discord Rich Presence activity."""
        cls.stop_activity()
        cls._active = True

        def _run():
            try:
                import socket
                import struct

                load_config()
                client_id = os.getenv(
                    "DISCORD_CLIENT_ID", "1543718626400403466"
                ).strip()
                if not client_id:
                    return

                sock = None
                if sys.platform == "win32":
                    for i in range(10):
                        pipe_name = rf"\\.\pipe\discord-ipc-{i}"
                        if os.path.exists(pipe_name):
                            # On Windows, open named pipe
                            break
                else:
                    uid = os.getuid()
                    candidates = [
                        f"/run/user/{uid}/discord-ipc-0",
                        f"/run/user/{uid}/app/com.discordapp.Discord/discord-ipc-0",
                        os.path.join(
                            os.environ.get("XDG_RUNTIME_DIR", ""), "discord-ipc-0"
                        ),
                        "/tmp/discord-ipc-0",
                    ]
                    for c in candidates:
                        if os.path.exists(c):
                            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                            sock.connect(c)
                            break

                if not sock:
                    return

                cls._sock = sock

                # Send Handshake opcode 0
                handshake = json.dumps({"v": 1, "client_id": client_id}).encode("utf-8")
                sock.sendall(struct.pack("<II", 0, len(handshake)) + handshake)
                sock.recv(1024)

                # Send Set Activity opcode 1
                activity = {
                    "cmd": "SET_ACTIVITY",
                    "args": {
                        "pid": os.getpid(),
                        "activity": {
                            "details": f"Watching {title[:120]}",
                            "state": f"Episode {ep_num} • 64x Turbo Speed",
                            "timestamps": {"start": int(time.time())},
                            "assets": {
                                "large_image": "ani_sync_logo",
                                "large_text": "ani-sync: Zero-Buffering Terminal Player",
                            },
                            "buttons": [
                                {
                                    "label": "⚡ Get ani-sync CLI",
                                    "url": "https://github.com/idrisharis12/ani-sync",
                                },
                                {
                                    "label": "⭐ Star on GitHub",
                                    "url": "https://github.com/idrisharis12/ani-sync",
                                },
                            ],
                        },
                    },
                    "nonce": str(time.time()),
                }
                payload = json.dumps(activity).encode("utf-8")
                sock.sendall(struct.pack("<II", 1, len(payload)) + payload)

                # Keep socket open and alive while active
                while cls._active:
                    time.sleep(1)
            except Exception:
                pass
            finally:
                if cls._sock:
                    try:
                        cls._sock.close()
                    except Exception:
                        pass
                    cls._sock = None

        cls._thread = threading.Thread(target=_run, daemon=True)
        cls._thread.start()

    @classmethod
    def stop_activity(cls):
        """Close Discord Rich Presence activity cleanly."""
        cls._active = False
        if cls._sock:
            try:
                cls._sock.close()
            except Exception:
                pass
            cls._sock = None


# ----------------------------------------------------------------------
# AniDB Scraper & Video Stream Extraction
# ----------------------------------------------------------------------
_HTTP_SESSION = None


def get_http_session():
    global _HTTP_SESSION
    if _HTTP_SESSION is None:
        _HTTP_SESSION = requests.Session()
        _HTTP_SESSION.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://anidb.app/",
                "Sec-Ch-Ua": '"Not-A.Brand";v="99", "Chromium";v="124", "Google Chrome";v="124"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Linux"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
        )
    return _HTTP_SESSION


def http_get(url, is_json=False):
    """Fetch URL using session with automatic curl fallback to prevent timeouts."""
    session = get_http_session()

    # 1. Try requests with robust headers
    try:
        res = session.get(url, timeout=12)
        if res.status_code == 200:
            return res.json() if is_json else res.text
    except Exception:
        pass

    # 2. Fallback to curl with browser headers
    try:
        cmd = [
            "curl",
            "-sL",
            "-A",
            USER_AGENT,
            "--max-time",
            "15",
            "-H",
            "Referer: https://anidb.app/",
            "-H",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            url,
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode(
            "utf-8", errors="ignore"
        )
        if out.strip():
            return json.loads(out) if is_json else out
    except Exception:
        pass

    # 3. Last retry with higher timeout
    res = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Referer": "https://anidb.app/"},
        timeout=20,
    )
    res.raise_for_status()
    return res.json() if is_json else res.text


def search_anime(query):
    """Search for anime on AniDB provider."""
    url = f"{ANIDB_BASE}/browse?q={urllib.parse.quote_plus(query)}"
    html_text = http_get(url)
    matches = re.findall(
        r"/anime/([a-z0-9-]+-[0-9]+).*?alt=\"([^\"]+)\"", html_text, re.DOTALL
    )
    results = []
    seen = set()
    for slug, raw_title in matches:
        if slug not in seen:
            seen.add(slug)
            title = html.unescape(raw_title).strip()
            results.append({"slug": slug, "title": title})
    return results


def get_trending_anime():
    """Fetch currently top trending and airing anime."""
    url = f"{ANIDB_BASE}/browse"
    html_text = http_get(url)
    matches = re.findall(
        r"/anime/([a-z0-9-]+-[0-9]+).*?alt=\"([^\"]+)\"", html_text, re.DOTALL
    )
    results = []
    seen = set()
    for slug, raw_title in matches:
        if slug not in seen:
            seen.add(slug)
            title = html.unescape(raw_title).strip()
            results.append({"slug": slug, "title": title})
    return results


def get_anime_details(slug):
    """Fetch anime seasons and mal_id if present."""
    url = f"{ANIDB_BASE}/anime/{slug}"
    html_text = http_get(url)
    mal_id_match = re.search(r"myanimelist\.net/anime/([0-9]+)", html_text)
    mal_id = int(mal_id_match.group(1)) if mal_id_match else None

    # Parse related seasons / franchise entries
    seasons = []
    season_section = re.search(r">Seasons<.*?>Details<", html_text, re.DOTALL)
    if season_section:
        sec_text = season_section.group(0)
        s_matches = re.findall(
            r"/anime/([a-z0-9-]+-[0-9]+)\"[^>]*title=\"([^\"]+)\"", sec_text
        )
        seen = {slug}
        for s_slug, s_title in s_matches:
            if s_slug not in seen:
                seen.add(s_slug)
                seasons.append(
                    {"slug": s_slug, "title": html.unescape(s_title).strip()}
                )
    return {"mal_id": mal_id, "seasons": seasons}


def get_episodes(slug):
    """Fetch available episodes for an anime."""
    anime_id = slug.split("-")[-1]
    url = f"{ANIDB_BASE}/api/frontend/anime/{anime_id}/episodes"
    data = http_get(url, is_json=True)
    return data.get("episodes", [])


def get_episode_streams(episode_id, mode="sub"):
    """Fetch m3u8 streams and available qualities for an episode."""
    url = f"{ANIDB_BASE}/api/frontend/episode/{episode_id}/languages"
    data = http_get(url, is_json=True)
    languages = data.get("languages", [])

    target_code = "eng" if mode == "dub" else "jpn"
    embed_url = None
    for lang in languages:
        if lang.get("code") == target_code:
            embed_url = lang.get("embed_url")
            break
    if not embed_url and languages:
        embed_url = languages[0].get("embed_url")

    if not embed_url:
        return {}

    embed_html = http_get(embed_url)
    m3u8_match = re.search(r"file:\s*['\"]([^'\"]+)['\"]", embed_html)
    if not m3u8_match:
        return {}

    master_m3u8_url = m3u8_match.group(1)
    master_content = http_get(master_m3u8_url)

    streams = {}
    lines = master_content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("#EXT-X-STREAM-INF"):
            res_match = re.search(r"RESOLUTION=\d+x(\d+)", line)
            quality_label = f"{res_match.group(1)}p" if res_match else "Auto"
            if i + 1 < len(lines):
                stream_link = lines[i + 1].strip()
                if not stream_link.startswith("http"):
                    stream_link = urllib.parse.urljoin(master_m3u8_url, stream_link)
                streams[quality_label] = stream_link

    if not streams:
        streams["Auto / Best"] = master_m3u8_url
    return streams


# ----------------------------------------------------------------------
# Player Launch & Playback Management
# ----------------------------------------------------------------------
def sanitize_filename(name):
    """Clean title string for safe filesystem filename."""
    return re.sub(r"[^\w\-_\. ]", "_", name).strip()


def find_player_binary(player="mpv"):
    """Find player binary across Windows, macOS, and Linux."""
    exe = shutil.which(player)
    if exe:
        return exe
    if sys.platform == "win32":
        exe_win = shutil.which(f"{player}.exe")
        if exe_win:
            return exe_win
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
    return player


def get_auto_skip_script(auto_skip=False):
    """Generate lightweight MPV Lua script for skipping anime intros/outros."""
    cache_dir = get_cache_dir()
    script_path = cache_dir / "ani_skip.lua"

    lua_code = f"""
-- ani-sync Auto-Skip & Fast-Skip Lua Integration
local auto_skip = {str(auto_skip).lower()}
local skipped_intro = false

function on_pos_change(name, pos)
    if not pos then return end
    if auto_skip and not skipped_intro and pos >= 0 and pos < 85 then
        mp.osd_message("⏩ Auto-Skipping Opening (+85s)", 3)
        mp.set_property_number("time-pos", 85)
        skipped_intro = true
    end
end

if auto_skip then
    mp.observe_property("time-pos", "number", on_pos_change)
end

-- Keybindings for instant manual intro/outro skips
mp.add_key_binding("i", "skip-intro", function()
    local pos = mp.get_property_number("time-pos", 0)
    mp.osd_message("⏩ Skipped Intro (+85s)", 2)
    mp.set_property_number("time-pos", pos + 85)
end)

mp.add_key_binding("Tab", "skip-intro-tab", function()
    local pos = mp.get_property_number("time-pos", 0)
    mp.osd_message("⏩ Skipped Intro (+85s)", 2)
    mp.set_property_number("time-pos", pos + 85)
end)

mp.add_key_binding("o", "skip-outro", function()
    local pos = mp.get_property_number("time-pos", 0)
    mp.osd_message("⏩ Skipped Outro (+85s)", 2)
    mp.set_property_number("time-pos", pos + 85)
end)
"""
    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(lua_code)
        return str(script_path)
    except Exception:
        return None


def launch_player(target_path, title, ep_num, player="mpv", auto_skip=False):
    """Launch the chosen media player with title, stream/file, and optimal smooth playback."""
    media_title = f"{title} - Episode {ep_num}"
    player_bin = find_player_binary(player)
    cmd = []
    if player == "mpv" or "mpv" in Path(player_bin).stem.lower():
        cmd = [
            player_bin,
            f"--force-media-title={media_title}",
            f"--user-agent={USER_AGENT}",
            "--referrer=https://anidb.app/",
            "--hwdec=auto-safe",
            "--profile=fast",
            "--audio-buffer=0.8",
        ]
        skip_script = get_auto_skip_script(auto_skip=auto_skip)
        if skip_script:
            cmd.append(f"--script={skip_script}")
        cmd.append(target_path)
    elif player == "vlc" or "vlc" in Path(player_bin).stem.lower():
        cmd = [
            player_bin,
            "--play-and-exit",
            f"--meta-title={media_title}",
            target_path,
        ]
    elif player == "iina" or "iina" in Path(player_bin).stem.lower():
        cmd = [
            player_bin,
            f"--mpv-force-media-title={media_title}",
            target_path,
        ]
    else:
        cmd = [player_bin, target_path]

    print(f"\n{C_BOLD}▶️  Now Playing:{C_RESET} {C_CYAN}{media_title}{C_RESET}")
    print(
        f"{C_DIM}Shortcuts: [Tab]/[i] Skip Intro (+85s) | [o] Skip Outro | [q] Quit{C_RESET}\n"
    )

    proc = subprocess.run(cmd)
    return proc.returncode == 0


def turbo_play(
    stream_url,
    title,
    ep_num,
    player="mpv",
    direct=False,
    download_only=False,
    auto_skip=False,
):
    """Zero-buffering maximum-speed playback using 64 parallel multi-connections."""
    safe_title = sanitize_filename(f"{title}_EP{ep_num}")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{safe_title}.mp4"

    # 1. Instant Play if already in cache
    if cache_file.exists() and cache_file.stat().st_size > 5 * 1024 * 1024:
        print(
            f"\n{C_GREEN}{C_BOLD}⚡ Episode already cached locally — Starting instantly (0.0s latency)!{C_RESET}"
        )
        if download_only:
            print(f"{C_GREEN}✓ File ready at: {cache_file}{C_RESET}")
            return True
        return launch_player(str(cache_file), title, ep_num, player=player)

    has_ytdlp = shutil.which("yt-dlp") is not None

    if direct or not has_ytdlp:
        return launch_player(stream_url, title, ep_num, player=player)

    print(
        f"\n{C_CYAN}{C_BOLD}🚀 MAXIMUM TURBO SPEED (64 Parallel Multi-Connections)...{C_RESET}"
    )
    print(
        f"{C_DIM}Saturating maximum Wi-Fi bandwidth for 100% buffer-free local playback.{C_RESET}\n"
    )

    dl_cmd = [
        "yt-dlp",
        "-N",
        "64",
        "--concurrent-fragments",
        "64",
        "--socket-timeout",
        "5",
        "--buffer-size",
        "16M",
        "--http-chunk-size",
        "10M",
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
        subprocess.run(dl_cmd)
    except Exception as e:
        print(f"{C_RED}Download error: {e}{C_RESET}")

    if download_only:
        print(f"\n{C_GREEN}{C_BOLD}✓ Download complete:{C_RESET} {cache_file}")
        return True

    target_to_play = (
        str(cache_file)
        if (cache_file.exists() and cache_file.stat().st_size > 5 * 1024 * 1024)
        else stream_url
    )
    res = launch_player(target_to_play, title, ep_num, player=player)

    # Cache cleanup: Keep newest ~4GB of anime, delete older
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


def prefetch_episode(next_ep_data, title, preferred_quality=None, mode="sub"):
    """Background pre-fetch of next episode so it loads in 0.0 seconds."""
    try:
        ep_num = next_ep_data.get("number")
        ep_id = next_ep_data.get("id")
        safe_title = sanitize_filename(f"{title}_EP{ep_num}")
        cache_file = CACHE_DIR / f"{safe_title}.mp4"
        if cache_file.exists() and cache_file.stat().st_size > 5 * 1024 * 1024:
            return

        streams = get_episode_streams(ep_id, mode=mode)
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
            "64",
            "--concurrent-fragments",
            "64",
            "--socket-timeout",
            "5",
            "--buffer-size",
            "16M",
            "--http-chunk-size",
            "10M",
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


# ----------------------------------------------------------------------
# Interactive Menus (FZF Fuzzy Search + Fallback + Auto-Installer)
# ----------------------------------------------------------------------
def _get_bin_dir():
    """Return user-writable bin directory for binary tools like fzf."""
    if sys.platform == "win32":
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
    """Ensure user's local bin directories are present in os.environ['PATH']."""
    bin_dir = str(_get_bin_dir())
    usr_local = "/usr/local/bin"
    home_local = str(Path.home() / ".local" / "bin")
    current_path = os.environ.get("PATH", "")
    paths = current_path.split(os.pathsep)
    added = False
    for p in [bin_dir, home_local, usr_local]:
        if p not in paths and os.path.exists(p):
            paths.insert(0, p)
            added = True
    if added:
        os.environ["PATH"] = os.pathsep.join(paths)


def _download_fzf_binary():
    """Download pre-built standalone fzf binary for current platform."""
    sys_name = platform.system().lower()
    machine = platform.machine().lower()

    # Map architecture
    if machine in ("x86_64", "amd64", "x64"):
        arch = "amd64"
    elif machine in ("aarch64", "arm64", "armv8"):
        arch = "arm64"
    elif machine.startswith("armv7") or machine.startswith("armhf"):
        arch = "armv7"
    elif machine.startswith("arm"):
        arch = "armv6"
    elif machine in ("i386", "i686", "x86"):
        arch = "386"
    else:
        arch = "amd64"

    # Map OS
    if sys_name == "linux":
        os_tag = "linux"
        ext = "tar.gz"
        bin_name = "fzf"
    elif sys_name == "darwin":
        os_tag = "darwin"
        ext = "tar.gz"
        bin_name = "fzf"
    elif sys_name == "windows":
        os_tag = "windows"
        ext = "zip"
        bin_name = "fzf.exe"
    else:
        return None

    version = "0.60.3"
    url = f"https://github.com/junegunn/fzf/releases/download/v{version}/fzf-{version}-{os_tag}_{arch}.{ext}"

    dest_dir = _get_bin_dir()
    dest_file = dest_dir / bin_name

    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()

        if ext == "tar.gz":
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
                for member in tar.getmembers():
                    if member.name == "fzf" or member.name.endswith("/fzf"):
                        extracted = tar.extractfile(member)
                        if extracted:
                            with open(dest_file, "wb") as out:
                                out.write(extracted.read())
                            break
        elif ext == "zip":
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for item in z.namelist():
                    if item in ("fzf.exe", "fzf"):
                        with open(dest_file, "wb") as out:
                            out.write(z.read(item))
                        break

        if dest_file.exists():
            dest_file.chmod(0o755)
            _ensure_path()
            return str(dest_file)
    except Exception:
        pass
    return None


_FZF_CHECKED = False


def _has_fzf():
    """Check if fzf is available on the system, auto-installing standalone binary if missing."""
    global _FZF_CHECKED
    _ensure_path()

    exe = shutil.which("fzf") or shutil.which("fzf.exe")
    if exe:
        return True

    bin_dir = _get_bin_dir()
    candidate = bin_dir / ("fzf.exe" if sys.platform == "win32" else "fzf")
    if candidate.is_file() and os.access(candidate, os.X_OK):
        _ensure_path()
        return True

    # Attempt automatic background download once
    if not _FZF_CHECKED and _FZF_ENABLED:
        _FZF_CHECKED = True
        try:
            installed = _download_fzf_binary()
            if installed and (shutil.which("fzf") or shutil.which("fzf.exe")):
                return True
        except Exception:
            pass

    return False


_FZF_ENABLED = True  # Set to False by --no-fzf CLI flag


def pick_option(title, options, default_idx=0, use_fzf=True):
    """Interactive selection menu with fzf fuzzy search (auto-fallback to numbered list).

    When fzf is installed, launches an interactive fuzzy finder with live
    search filtering, arrow-key navigation, and instant selection.
    Falls back to a clean numbered menu when fzf is not available.
    """
    if not options:
        return 0

    if len(options) == 1:
        clean_title = re.sub(r"\033\[[0-9;]*m", "", title).strip()
        clean_opt = re.sub(r"\033\[[0-9;]*m", "", options[0]).strip()
        print(
            f"\n{C_CYAN}ℹ️  {clean_title} {C_BOLD}{C_YELLOW}{clean_opt}{C_RESET} {C_GREEN}(Auto-selected){C_RESET}"
        )
        return 0

    if use_fzf and _FZF_ENABLED and _has_fzf() and len(options) > 1:
        try:
            result = _fzf_pick(title, options)
            if result is not None:
                return result
        except Exception:
            pass  # Fallback to numbered menu

    # Sleek styled numbered menu fallback
    clean_t = re.sub(r"\033\[[0-9;]*m", "", title).strip()
    raw_lengths = [len(re.sub(r"\033\[[0-9;]*m", "", str(o))) for o in options]
    box_width = max(len(clean_t) + 6, max(raw_lengths) + 12, 46)

    print(f"\n{C_CYAN}╭{'─' * box_width}╮{C_RESET}")
    print(f"{C_CYAN}│{C_RESET}  {C_BOLD}{C_MAGENTA}{clean_t}{C_RESET}")
    print(f"{C_CYAN}├{'─' * box_width}┤{C_RESET}")
    for idx, opt in enumerate(options, 1):
        is_default = (idx - 1) == default_idx
        prefix = f"{C_GREEN}{C_BOLD}[{idx}]{C_RESET}"
        def_tag = f" {C_YELLOW}(default){C_RESET}" if is_default else ""
        print(f"{C_CYAN}│{C_RESET}  {prefix} {opt}{def_tag}")
    print(f"{C_CYAN}╰{'─' * box_width}╯{C_RESET}")

    while True:
        try:
            choice = input(
                f"{C_BOLD}Select [1-{len(options)}] (default: {default_idx+1}) ❯ {C_RESET}"
            ).strip()
            if not choice:
                return default_idx
            val = int(choice)
            if 1 <= val <= len(options):
                return val - 1
            print(
                f"{C_RED}Please enter a number between 1 and {len(options)}.{C_RESET}"
            )
        except ValueError:
            print(f"{C_RED}Invalid input. Please enter a number.{C_RESET}")
        except (KeyboardInterrupt, EOFError):
            print("\n")
            sys.exit(0)


def _fzf_pick(title, options):
    """Launch fzf with the list of options and return the selected index."""
    clean_title = (
        title.replace("\033[94m", "")
        .replace("\033[96m", "")
        .replace("\033[92m", "")
        .replace("\033[93m", "")
        .replace("\033[95m", "")
        .replace("\033[91m", "")
        .replace("\033[1m", "")
        .replace("\033[2m", "")
        .replace("\033[0m", "")
        .strip()
    )
    numbered = [f"{i+1}. {opt}" for i, opt in enumerate(options)]
    input_text = "\n".join(numbered)

    fzf_cmd = [
        "fzf",
        "--height=~50%",
        "--layout=reverse",
        "--border=rounded",
        "--margin=1,2",
        "--padding=0,1",
        "--info=inline",
        f"--header= 📺  ani-sync  ❯  {clean_title} ",
        "--prompt=  🔍 Search ❯ ",
        "--pointer=▶ ",
        "--marker=✦ ",
        "--color=header:bold:cyan,info:yellow,prompt:bold:magenta,pointer:bold:cyan,marker:bold:green,border:cyan",
        "--ansi",
        "--no-scrollbar",
        "--cycle",
    ]

    proc = subprocess.run(
        fzf_cmd,
        input=input_text,
        capture_output=True,
        text=True,
    )

    if proc.returncode != 0 or not proc.stdout.strip():
        return None  # User cancelled (Esc/Ctrl-C)

    selected = proc.stdout.strip()
    num_match = re.match(r"^(\d+)\.", selected)
    if num_match:
        return int(num_match.group(1)) - 1
    for i, opt in enumerate(options):
        if opt in selected:
            return i
    return 0


# ----------------------------------------------------------------------
# Main Interactive Flow
# ----------------------------------------------------------------------
def play_loop(
    anime,
    initial_ep_idx=0,
    preferred_quality=None,
    mode="sub",
    player="mpv",
    direct=False,
    download_only=False,
    auto_skip=False,
):
    """Watch loop with next, replay, previous, change episode/quality/season."""
    slug = anime["slug"]
    title = anime["title"]

    print(f"{C_YELLOW}Fetching episodes for {title}...{C_RESET}")
    episodes = get_episodes(slug)
    if not episodes:
        # Try automatic title search fallback on AniDB
        search_res = search_anime(title)
        if search_res:
            slug = search_res[0]["slug"]
            anime["slug"] = slug
            episodes = get_episodes(slug)

    if not episodes:
        print(f"{C_RED}❌ No episodes found for {title}.{C_RESET}")
        return

    # Check for details and MAL ID
    details = get_anime_details(slug)
    mal_id = details.get("mal_id")
    seasons = details.get("seasons", [])

    current_idx = initial_ep_idx

    while True:
        if current_idx < 0 or current_idx >= len(episodes):
            print(f"{C_YELLOW}No more episodes in this list.{C_RESET}")
            break

        ep_data = episodes[current_idx]
        ep_num = ep_data.get("number", current_idx + 1)
        ep_id = ep_data.get("id")

        print(
            f"\n{C_CYAN}Resolving streams for Episode {ep_num} ({mode.upper()})...{C_RESET}"
        )
        streams = get_episode_streams(ep_id, mode=mode)
        if not streams:
            print(
                f"{C_RED}❌ Could not resolve video streams for Episode {ep_num}.{C_RESET}"
            )
            break

        # Quality Selection
        selected_url = None
        if preferred_quality and preferred_quality in streams:
            selected_url = streams[preferred_quality]
            quality_used = preferred_quality
        elif "720p" in streams:
            # 720p is optimal for zero-buffering instant start on any Wi-Fi
            selected_url = streams["720p"]
            quality_used = "720p"
        else:
            # Fallback to available quality
            qualities = list(streams.keys())
            if len(qualities) == 1:
                quality_used = qualities[0]
                selected_url = streams[quality_used]
            else:

                def sort_key(q):
                    num = re.findall(r"\d+", q)
                    return int(num[0]) if num else 0

                sorted_qualities = sorted(qualities, key=sort_key, reverse=True)
                quality_used = sorted_qualities[0]
                selected_url = streams[quality_used]

        # Background pre-fetch next 2 episodes so upcoming episodes load in 0.0s
        if not direct and not download_only:
            if current_idx + 1 < len(episodes):
                threading.Thread(
                    target=prefetch_episode,
                    args=(episodes[current_idx + 1], title, preferred_quality, mode),
                    daemon=True,
                ).start()
            if current_idx + 2 < len(episodes):
                threading.Thread(
                    target=prefetch_episode,
                    args=(episodes[current_idx + 2], title, preferred_quality, mode),
                    daemon=True,
                ).start()

        # Update Discord Rich Presence
        DiscordRPC.start_activity(title, ep_num)

        # Launch Turbo Multi-Connection Player
        turbo_play(
            selected_url,
            title,
            ep_num,
            player=player,
            direct=direct,
            download_only=download_only,
            auto_skip=auto_skip,
        )

        # Stop Discord Rich Presence on player close
        DiscordRPC.stop_activity()

        # Record to local history
        save_history(slug, title, ep_num, quality=quality_used, mode=mode)

        # Auto-sync to all configured tracking platforms (MAL, AniList, Kitsu) in parallel
        has_tracking = (
            is_mal_configured() or is_anilist_configured() or is_kitsu_configured()
        )
        sync_res = {}
        if has_tracking:
            print(
                f"\n{C_CYAN}🔄 Syncing progress to connected platforms...{C_RESET}",
                end="",
                flush=True,
            )
            sync_res = sync_all_platforms(title, ep_num, mal_id=mal_id)
            print("\r" + " " * 60 + "\r", end="", flush=True)

        # Interactive post-playback controls
        while True:
            has_next = (current_idx + 1) < len(episodes)
            has_prev = (current_idx - 1) >= 0
            next_num = (
                episodes[current_idx + 1].get("number", current_idx + 2)
                if has_next
                else None
            )

            # Modern Aesthetic Completion & Action Card
            card_width = 62
            display_title = title if len(title) <= 34 else title[:31] + "..."
            print(f"\n{C_CYAN}╭{'─' * card_width}╮{C_RESET}")
            print(
                f"{C_CYAN}│{C_RESET}  {C_MAGENTA}{C_BOLD}🎬 Episode {ep_num} Completed{C_RESET} • {C_WHITE}{C_BOLD}{display_title:<36}{C_RESET} {C_CYAN}│{C_RESET}"
            )

            if has_tracking and sync_res:
                print(f"{C_CYAN}├{'─' * card_width}┤{C_RESET}")
                for p_name, (p_ok, p_msg) in sync_res.items():
                    if p_ok:
                        status_line = f"  {C_GREEN}✓{C_RESET} {C_BOLD}{p_name:<13}{C_RESET} {C_GREEN}{p_msg}{C_RESET}"
                    else:
                        status_line = f"  {C_YELLOW}⚠{C_RESET} {C_BOLD}{p_name:<13}{C_RESET} {C_YELLOW}{p_msg}{C_RESET}"
                    print(f"{C_CYAN}│{C_RESET}{status_line}")

            print(f"{C_CYAN}├{'─' * card_width}┤{C_RESET}")

            # Formatted action rows
            if has_next:
                row1 = f"  {C_GREEN}{C_BOLD}[Enter/n]{C_RESET} Next (Ep {next_num})  │  {C_CYAN}[r]{C_RESET} Replay Ep {ep_num}  │  {C_YELLOW}[p]{C_RESET} Prev"
            else:
                row1 = f"  {C_CYAN}[r]{C_RESET} Replay Ep {ep_num}  │  {C_YELLOW}[p]{C_RESET} Previous Episode"

            if seasons:
                row2 = f"  {C_YELLOW}[s]{C_RESET} Select Ep │ {C_YELLOW}[q]{C_RESET} Quality │ {C_YELLOW}[S]{C_RESET} Season │ {C_MAGENTA}[m]{C_RESET} Menu (FZF) │ {C_RED}[x]{C_RESET} Quit"
            else:
                row2 = f"  {C_YELLOW}[s]{C_RESET} Select Ep  │  {C_YELLOW}[q]{C_RESET} Quality  │  {C_MAGENTA}[m]{C_RESET} Menu (FZF)  │  {C_RED}[x]{C_RESET} Quit"

            print(f"{C_CYAN}│{C_RESET}{row1}")
            print(f"{C_CYAN}│{C_RESET}{row2}")
            print(f"{C_CYAN}╰{'─' * card_width}╯{C_RESET}")

            try:
                cmd = input(f"{C_BOLD}Choice ❯ {C_RESET}").strip()
            except (KeyboardInterrupt, EOFError):
                print(
                    f"\n{C_MAGENTA}╭────────────────────────────────────────────────────────────╮{C_RESET}"
                    f"\n{C_MAGENTA}│{C_RESET}  {C_GREEN}{C_BOLD}✨ Thanks for using ani-sync! Sayonara! 👋{C_RESET}                 {C_MAGENTA}│{C_RESET}"
                    f"\n{C_MAGENTA}╰────────────────────────────────────────────────────────────╯{C_RESET}\n"
                )
                return

            if (not cmd and has_next) or cmd.lower() in ("n", "next"):
                if has_next:
                    current_idx += 1
                    break
                else:
                    print(f"{C_YELLOW}No more episodes available.{C_RESET}")
            elif cmd.lower() in ("r", "replay"):
                break  # loops same ep
            elif cmd.lower() in ("p", "prev", "previous") and has_prev:
                current_idx -= 1
                break
            elif cmd.lower() in ("s", "select", "ep"):
                ep_options = [
                    f"Episode {e.get('number', i+1)}" for i, e in enumerate(episodes)
                ]
                current_idx = pick_option(
                    f"Select Episode for '{title[:32]}':",
                    ep_options,
                    default_idx=current_idx,
                )
                break
            elif cmd.lower() in ("q", "quality"):
                q_options = list(streams.keys())
                q_idx = pick_option(
                    f"Select Video Quality (Current: {quality_used}):",
                    q_options,
                    default_idx=0,
                )
                preferred_quality = q_options[q_idx]
                break
            elif cmd.lower() in ("s", "season") and seasons:
                s_options = [s["title"] for s in seasons]
                s_idx = pick_option(
                    "Select Season / Movie in Franchise:", s_options, default_idx=0
                )
                return play_loop(
                    seasons[s_idx],
                    initial_ep_idx=0,
                    preferred_quality=preferred_quality,
                    mode=mode,
                    player=player,
                    direct=direct,
                    download_only=download_only,
                    auto_skip=auto_skip,
                )
            elif cmd.lower() in ("m", "menu", "fzf"):
                menu_opts = []
                actions = []
                if has_next:
                    menu_opts.append(f"▶   Play Next Episode (Episode {next_num})")
                    actions.append("next")
                menu_opts.append(f"🔄  Replay Current Episode (Episode {ep_num})")
                actions.append("replay")
                if has_prev:
                    menu_opts.append(
                        f"⏮   Play Previous Episode (Episode {ep_num-1 if ep_num > 1 else 1})"
                    )
                    actions.append("prev")
                menu_opts.append("📋  Select Different Episode (FZF Finder)")
                actions.append("select")
                menu_opts.append(f"🎯  Change Video Quality (Current: {quality_used})")
                actions.append("quality")
                if seasons:
                    menu_opts.append("🎬  Switch Season / Movie in Franchise")
                    actions.append("season")
                menu_opts.append("📥  Sync & Update Watch Library")
                actions.append("sync")
                menu_opts.append("🩺  Run System Diagnostics (Doctor)")
                actions.append("doctor")
                menu_opts.append("❌  Exit ani-sync")
                actions.append("quit")

                selected_action_idx = pick_option(
                    "Playback Actions & Navigation Menu", menu_opts, default_idx=0
                )
                action = actions[selected_action_idx]
                if action == "next":
                    current_idx += 1
                    break
                elif action == "replay":
                    break
                elif action == "prev":
                    current_idx -= 1
                    break
                elif action == "select":
                    ep_options = [
                        f"Episode {e.get('number', i+1)}"
                        for i, e in enumerate(episodes)
                    ]
                    current_idx = pick_option(
                        f"Select Episode for '{title[:32]}':",
                        ep_options,
                        default_idx=current_idx,
                    )
                    break
                elif action == "quality":
                    q_options = list(streams.keys())
                    q_idx = pick_option(
                        f"Select Video Quality (Current: {quality_used}):",
                        q_options,
                        default_idx=0,
                    )
                    preferred_quality = q_options[q_idx]
                    break
                elif action == "season":
                    s_options = [s["title"] for s in seasons]
                    s_idx = pick_option(
                        "Select Season / Movie in Franchise:", s_options, default_idx=0
                    )
                    return play_loop(
                        seasons[s_idx],
                        initial_ep_idx=0,
                        preferred_quality=preferred_quality,
                        mode=mode,
                        player=player,
                        direct=direct,
                        download_only=download_only,
                        auto_skip=auto_skip,
                    )
                elif action == "sync":
                    sync_all_libraries()
                elif action == "doctor":
                    run_doctor()
                elif action == "quit":
                    print(
                        f"\n{C_MAGENTA}╭────────────────────────────────────────────────────────────╮{C_RESET}"
                        f"\n{C_MAGENTA}│{C_RESET}  {C_GREEN}{C_BOLD}✨ Thanks for using ani-sync! Sayonara! 👋{C_RESET}                 {C_MAGENTA}│{C_RESET}"
                        f"\n{C_MAGENTA}╰────────────────────────────────────────────────────────────╯{C_RESET}\n"
                    )
                    return
            elif cmd.lower() in ("x", "quit", "exit"):
                print(
                    f"\n{C_MAGENTA}╭────────────────────────────────────────────────────────────╮{C_RESET}"
                    f"\n{C_MAGENTA}│{C_RESET}  {C_GREEN}{C_BOLD}✨ Thanks for using ani-sync! Sayonara! 👋{C_RESET}                 {C_MAGENTA}│{C_RESET}"
                    f"\n{C_MAGENTA}╰────────────────────────────────────────────────────────────╯{C_RESET}\n"
                )
                return
            else:
                print(
                    f"{C_RED}Invalid option. Press [Enter] for Next, [r] to Replay, or [m] for Menu.{C_RESET}"
                )


# ----------------------------------------------------------------------
# Self-Updater
# ----------------------------------------------------------------------
def update_self(quiet=False):
    """Update ani-sync to the latest version directly from GitHub."""
    if not quiet:
        print(
            f"\n{C_CYAN}{C_BOLD}🔄 Checking for ani-sync updates from GitHub...{C_RESET}"
        )
    url = "https://raw.githubusercontent.com/idrisharis12/ani-sync/main/ani_sync.py"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        remote_code = r.text

        v_match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', remote_code)
        remote_version = v_match.group(1) if v_match else "latest"

        targets = [
            Path(__file__).resolve(),
            Path.home() / ".local" / "share" / "ani-sync" / "ani_sync.py",
            Path("/usr/local/share/ani-sync/ani_sync.py"),
            Path("/usr/share/ani-sync/ani_sync.py"),
        ]

        updated = False
        for target in set(targets):
            if target.exists():
                try:
                    with open(target, "w", encoding="utf-8") as f:
                        f.write(remote_code)
                    os.chmod(target, 0o755)
                    updated = True
                except PermissionError:
                    if not quiet:
                        print(
                            f"{C_YELLOW}Notice: Permission denied writing to {target}. Run with sudo to update system-wide install.{C_RESET}"
                        )

        if updated and not quiet:
            print(
                f"{C_GREEN}{C_BOLD}✅ Successfully updated ani-sync to v{remote_version}!{C_RESET}\n"
            )
        elif not quiet:
            print(
                f"{C_GREEN}{C_BOLD}✅ ani-sync is already up to date (v{remote_version}).{C_RESET}\n"
            )
    except Exception as e:
        if not quiet:
            print(f"{C_RED}❌ Failed to update ani-sync: {e}{C_RESET}")


# ----------------------------------------------------------------------
# CLI Interface & Entry Point
# ----------------------------------------------------------------------
def run_doctor():
    """Diagnostic tool to verify all dependencies and configuration."""
    _ensure_path()
    print(
        f"\n{C_CYAN}{C_BOLD}============================================================{C_RESET}"
    )
    print(
        f"{C_MAGENTA}{C_BOLD}             ani-sync System & Dependency Doctor            {C_RESET}"
    )
    print(
        f"{C_CYAN}{C_BOLD}============================================================{C_RESET}\n"
    )

    # 1. Python Environment
    py_ver = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    print(f"{C_BOLD}Runtime & Libraries:{C_RESET}")
    print(
        f"  {C_GREEN}✓{C_RESET} Python:            {C_CYAN}v{py_ver}{C_RESET} ({sys.executable})"
    )

    # 2. Python Packages
    try:
        import requests

        req_ver = getattr(requests, "__version__", "installed")
        print(f"  {C_GREEN}✓{C_RESET} requests:          {C_CYAN}v{req_ver}{C_RESET}")
    except ImportError:
        print(
            f"  {C_RED}✗{C_RESET} requests:          {C_RED}Missing (pip install requests){C_RESET}"
        )

    try:
        import tqdm

        tqdm_ver = getattr(tqdm, "__version__", "installed")
        print(f"  {C_GREEN}✓{C_RESET} tqdm:              {C_CYAN}v{tqdm_ver}{C_RESET}")
    except ImportError:
        print(
            f"  {C_RED}✗{C_RESET} tqdm:              {C_RED}Missing (pip install tqdm){C_RESET}"
        )

    # 3. Interactive FZF
    print(f"\n{C_BOLD}Interactive Fuzzy Search:{C_RESET}")
    has_fzf = _has_fzf()
    fzf_path = shutil.which("fzf") or shutil.which("fzf.exe")
    if has_fzf:
        print(
            f"  {C_GREEN}✓{C_RESET} fzf:               {C_CYAN}Ready{C_RESET} ({fzf_path or 'auto-installed'})"
        )
    else:
        print(
            f"  {C_YELLOW}⚠{C_RESET} fzf:               {C_YELLOW}Not found (falling back to numbered menus){C_RESET}"
        )
        print("      Attempting automatic standalone download...")
        dl = _download_fzf_binary()
        if dl:
            print(f"      {C_GREEN}✓ Successfully installed FZF to {dl}!{C_RESET}")
        else:
            print(
                f"      {C_RED}Could not auto-download FZF. Check internet connection.{C_RESET}"
            )

    # 4. Media Player & Acceleration
    print(f"\n{C_BOLD}Media Player & Stream Acceleration:{C_RESET}")
    mpv_path = shutil.which("mpv") or shutil.which("mpv.exe")
    if mpv_path:
        print(
            f"  {C_GREEN}✓{C_RESET} mpv:               {C_CYAN}Ready{C_RESET} ({mpv_path})"
        )
    else:
        print(
            f"  {C_YELLOW}⚠{C_RESET} mpv:               {C_YELLOW}Not found (Recommended: sudo apt install mpv / pacman -S mpv / winget install mpv.net){C_RESET}"
        )

    ytdlp_path = shutil.which("yt-dlp") or shutil.which("yt-dlp.exe")
    if ytdlp_path:
        print(
            f"  {C_GREEN}✓{C_RESET} yt-dlp:            {C_CYAN}Ready{C_RESET} ({ytdlp_path})"
        )
    else:
        print(
            f"  {C_YELLOW}⚠{C_RESET} yt-dlp:            {C_YELLOW}Not found (Multi-threaded turbo speed fallback active){C_RESET}"
        )

    curl_path = shutil.which("curl") or shutil.which("curl.exe")
    if curl_path:
        print(
            f"  {C_GREEN}✓{C_RESET} curl:              {C_CYAN}Ready{C_RESET} ({curl_path})"
        )
    else:
        print(f"  {C_YELLOW}⚠{C_RESET} curl:              {C_YELLOW}Not found{C_RESET}")

    # 5. Auth Credentials
    print(f"\n{C_BOLD}Connected Tracking Platforms:{C_RESET}")
    load_config()
    mal_token = os.environ.get("MAL_REFRESH_TOKEN") or os.environ.get("MAL_CLIENT_ID")
    if mal_token:
        print(f"  {C_GREEN}✓{C_RESET} MyAnimeList:       {C_GREEN}Connected{C_RESET}")
    else:
        print(
            f"  {C_DIM}○{C_RESET} MyAnimeList:       {C_DIM}Not linked (run: ani-sync auth mal){C_RESET}"
        )

    if is_anilist_configured():
        print(f"  {C_GREEN}✓{C_RESET} AniList:           {C_GREEN}Connected{C_RESET}")
    else:
        print(
            f"  {C_DIM}○{C_RESET} AniList:           {C_DIM}Not linked (run: ani-sync auth anilist){C_RESET}"
        )

    if is_kitsu_configured():
        print(f"  {C_GREEN}✓{C_RESET} Kitsu:             {C_GREEN}Connected{C_RESET}")
    else:
        print(
            f"  {C_DIM}○{C_RESET} Kitsu:             {C_DIM}Not linked (run: ani-sync auth kitsu){C_RESET}"
        )

    print(f"\n{C_GREEN}Doctor check completed.{C_RESET}\n")


def print_help():
    print(
        f"""{C_CYAN}{C_BOLD}ani-sync v{VERSION}{C_RESET} - Stream anime in terminal and auto-sync watch progress

{C_BOLD}Usage:{C_RESET}
    {C_GREEN}ani-sync <anime name>{C_RESET}
    {C_GREEN}ani-sync continue{C_RESET}
    {C_GREEN}ani-sync trending{C_RESET}
    {C_GREEN}ani-sync sync{C_RESET}
    {C_GREEN}ani-sync doctor{C_RESET}
    {C_GREEN}ani-sync "attack on titan" --dub{C_RESET}
    {C_GREEN}ani-sync "jujutsu kaisen" -d -e 1{C_RESET}

{C_BOLD}Options:{C_RESET}
    -c, --continue, continue  Resume last watched anime (plays next episode)
    -t, --trending, trending  Browse top airing and trending anime
    history, --history        View recent watch history and pick to resume
    sync, --sync, import      Sync & import watch library from all connected platforms
    doctor, check, --doctor   Verify dependencies, system status & credentials
    -e, --episode <num>       Jump directly to specified episode number
    -q, --quality <res>       Preferred quality (e.g. 1080p, 720p, 480p, 360p)
    --skip, --auto-skip       Automatically skip anime opening/intro (+85s)
    -d, --download            Download episode locally without opening player
    --direct                  Stream directly without multi-threaded local turbo cache
    --dub                     Play English dub if available (default: Japanese sub)
    --no-fzf                  Disable fzf fuzzy search (use numbered menus)
    --player <player>         Media player executable (default: mpv)
    -U, --update, update      Check and update ani-sync to the latest version
    -h, --help                Show this help menu

{C_BOLD}Authentication (Multi-Platform Tracking):{C_RESET}
    auth                      Interactive auth picker (MAL / AniList / Kitsu)
    auth mal                  Connect MyAnimeList account
    auth anilist              Connect AniList account
    auth kitsu                Connect Kitsu account

{C_BOLD}Player Keybindings:{C_RESET}
    {C_CYAN}[Tab]{C_RESET} or {C_CYAN}[i]{C_RESET}         Skip anime intro / opening (+85 seconds)
    {C_CYAN}[o]{C_RESET}                   Skip anime outro / ending
    {C_CYAN}[q]{C_RESET}                   Quit player and return to post-playback controls

{C_BOLD}FZF Fuzzy Search:{C_RESET}
    FZF interactive fuzzy filtering is automatically configured and enabled
    by default for all search results, episode selections, and history menus.
    Use {C_YELLOW}--no-fzf{C_RESET} to force classic numbered menus.
"""
    )


def main():
    args = sys.argv[1:]

    # Asynchronous background auto-updater for all Linux distributions & macOS
    if not (
        args
        and args[0]
        in (
            "-h",
            "--help",
            "help",
            "auth",
            "setup",
            "--auth",
            "doctor",
            "check",
            "--doctor",
            "--check",
        )
    ):
        threading.Thread(
            target=update_self, kwargs={"quiet": True}, daemon=True
        ).start()

    if not args or args[0] in ("-h", "--help", "help"):
        if not args:
            # Interactive prompt if no arguments
            pass
        else:
            print_help()
            return

    if args and args[0] in ("doctor", "check", "--doctor", "--check"):
        run_doctor()
        return

    if args and args[0] in ("-U", "--update", "update"):
        quiet = "--quiet" in args or "-q" in args
        update_self(quiet=quiet)
        return

    # Check for library sync command
    if args and args[0] in ("sync", "import", "library", "pull", "--sync"):
        sync_all_libraries()
        return

    if args and args[0] in ("auth", "setup", "--auth"):
        if len(args) >= 2 and args[1].lower() in ("anilist", "al"):
            run_anilist_auth()
        elif len(args) >= 2 and args[1].lower() in ("kitsu", "kt"):
            run_kitsu_auth()
        elif len(args) >= 2 and args[1].lower() in ("mal", "myanimelist"):
            run_auth()
        else:
            # Interactive platform picker
            print(
                f"\n{C_CYAN}{C_BOLD}🔗 Select tracking platform to authenticate:{C_RESET}"
            )
            platforms = [
                "MyAnimeList (MAL)",
                "AniList",
                "Kitsu",
            ]
            idx = pick_option(
                "Authentication Setup:", platforms, default_idx=0, use_fzf=False
            )
            if idx == 0:
                run_auth()
            elif idx == 1:
                run_anilist_auth()
            elif idx == 2:
                run_kitsu_auth()
        return

    # Check for continue / resume command
    if args and args[0] in ("-c", "--continue", "continue", "resume"):
        last = get_last_watched()
        if not last:
            print(
                f"{C_YELLOW}No previous watch history found. Start watching an anime first!{C_RESET}"
            )
            return
        slug = last["slug"]
        title = last["title"]
        next_ep = last.get("episode", 1) + 1
        print(
            f"\n{C_GREEN}{C_BOLD}⏪ Resuming {title} from Episode {next_ep}...{C_RESET}"
        )
        play_loop(
            {"slug": slug, "title": title},
            initial_ep_idx=next_ep - 1,
            preferred_quality=last.get("quality", "720p"),
            mode=last.get("mode", "sub"),
            player="mpv",
        )
        return

    # Check for trending / top anime
    if args and args[0] in ("-t", "--trending", "trending", "airing", "top"):
        print(f"\n{C_YELLOW}🔥 Fetching top trending & airing anime...{C_RESET}")
        try:
            results = get_trending_anime()
            if not results:
                print(f"{C_RED}Could not fetch trending anime.{C_RESET}")
                return
            options = [r["title"] for r in results]
            selected_idx = pick_option(
                "🔥 Top Airing & Trending Anime:", options, default_idx=0
            )
            chosen_anime = results[selected_idx]
            play_loop(chosen_anime, initial_ep_idx=0, player="mpv")
            return
        except Exception as e:
            print(f"{C_RED}Error fetching trending: {e}{C_RESET}")
            return

    # Check for history command
    if args and args[0] in ("history", "--history"):
        hist = load_history().get("history", [])
        if not hist:
            print(f"{C_YELLOW}No watch history recorded yet.{C_RESET}")
            return
        print(f"\n{C_CYAN}{C_BOLD}📺 Recent Watch History:{C_RESET}")
        options = [
            f"{h['title']} - Ep {h['episode']} ({h.get('quality', '720p')})"
            for h in hist
        ]
        selected_idx = pick_option("Select to resume watching:", options, default_idx=0)
        chosen = hist[selected_idx]
        play_loop(
            {"slug": chosen["slug"], "title": chosen["title"]},
            initial_ep_idx=chosen.get("episode", 1) - 1,
            preferred_quality=chosen.get("quality", "720p"),
            mode=chosen.get("mode", "sub"),
            player="mpv",
        )
        return

    # Check for legacy watch <url> syntax
    if args and args[0] == "watch" and len(args) >= 2:
        url = args[1]
        player = "mpv"
        if "--player" in args:
            p_idx = args.index("--player")
            if p_idx + 1 < len(args):
                player = args[p_idx + 1]
        launch_player(url, "Anime Episode", 1, player=player)
        return

    # Parse Flags
    query_parts = []
    episode_target = None
    preferred_quality = None
    mode = "sub"
    player = "mpv"
    direct = False
    download_only = False
    auto_skip = False
    use_fzf = True

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-e", "--episode", "-r", "--range"):
            if i + 1 < len(args):
                episode_target = int(args[i + 1])
                i += 1
        elif arg in ("-q", "--quality"):
            if i + 1 < len(args):
                preferred_quality = args[i + 1]
                if not preferred_quality.endswith("p") and preferred_quality.isdigit():
                    preferred_quality += "p"
                i += 1
        elif arg in ("-d", "--download"):
            download_only = True
        elif arg == "--direct":
            direct = True
        elif arg in ("--skip", "--auto-skip"):
            auto_skip = True
        elif arg == "--no-fzf":
            use_fzf = False
            global _FZF_ENABLED
            _FZF_ENABLED = False
        elif arg == "--dub":
            mode = "dub"
        elif arg == "--player":
            if i + 1 < len(args):
                player = args[i + 1]
                i += 1
        elif not arg.startswith("-"):
            query_parts.append(arg)
        i += 1

    query = " ".join(query_parts).strip()
    if not query:
        print(
            f"\n{C_CYAN}{C_BOLD}============================================================{C_RESET}"
        )
        print(
            f"{C_MAGENTA}{C_BOLD}              ani-sync — Terminal Anime Player              {C_RESET}"
        )
        print(
            f"{C_CYAN}{C_BOLD}============================================================{C_RESET}"
        )
        try:
            query = input(f"\n{C_BOLD}🔍 Search anime title: {C_RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            return
        if not query:
            print(f"{C_RED}No search query entered.{C_RESET}")
            return

    print(f"\n{C_YELLOW}Searching for '{query}'...{C_RESET}")
    try:
        results = search_anime(query)
    except Exception as e:
        print(f"{C_RED}❌ Search error: {e}{C_RESET}")
        return

    if not results:
        print(
            f"{C_RED}❌ No anime found matching '{query}'. Try another search term!{C_RESET}"
        )
        return

    # Pick Anime
    if len(results) == 1:
        chosen_anime = results[0]
    else:
        options = [r["title"] for r in results]
        selected_idx = pick_option("Search Results:", options, default_idx=0)
        chosen_anime = results[selected_idx]

    # Check for seasons / movies franchise options
    details = get_anime_details(chosen_anime["slug"])
    seasons = details.get("seasons", [])
    if seasons:
        franchise_options = [f"{chosen_anime['title']} (Selected)"] + [
            s["title"] for s in seasons
        ]
        f_idx = pick_option(
            f"Seasons & Movies for '{chosen_anime['title']}':",
            franchise_options,
            default_idx=0,
        )
        if f_idx > 0:
            chosen_anime = seasons[f_idx - 1]

    # Fetch episodes
    episodes = get_episodes(chosen_anime["slug"])
    if not episodes:
        print(f"{C_RED}❌ No episodes found for {chosen_anime['title']}.{C_RESET}")
        return

    # Pick Episode
    ep_idx = 0
    if episode_target:
        for idx, ep in enumerate(episodes):
            if ep.get("number") == episode_target:
                ep_idx = idx
                break
    elif len(episodes) > 1:
        ep_options = [f"Episode {e.get('number', i+1)}" for i, e in enumerate(episodes)]
        ep_idx = pick_option(
            f"Select Episode for '{chosen_anime['title']}':", ep_options, default_idx=0
        )

    # Launch Playback Loop
    play_loop(
        chosen_anime,
        initial_ep_idx=ep_idx,
        preferred_quality=preferred_quality,
        mode=mode,
        player=player,
        direct=direct,
        download_only=download_only,
        auto_skip=auto_skip,
    )


if __name__ == "__main__":
    main()
