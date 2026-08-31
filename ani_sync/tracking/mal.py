# -*- coding: utf-8 -*-
"""MyAnimeList OAuth2 authentication, token caching, and watch progress synchronization."""

import html
import os
import secrets
import time
import urllib.parse
import webbrowser
import requests

from ani_sync.config import CONFIG_PATH, _append_config, load_config, log_debug
from ani_sync.ui.themes import (
    C_BLUE,
    C_BOLD,
    C_CYAN,
    C_GREEN,
    C_RED,
    C_RESET,
    C_YELLOW,
    C_DIM,
)

TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"
AUTH_URL = "https://myanimelist.net/v1/oauth2/authorize"
API_URL = "https://api.myanimelist.net/v2"

# In-memory access token cache (P1 Optimization)
_CACHED_ACCESS_TOKEN = None
_TOKEN_EXPIRES_AT = 0


def get_mal_env():
    load_config()
    client_id = os.getenv("MAL_CLIENT_ID", "").strip()
    client_secret = os.getenv("MAL_CLIENT_SECRET", "").strip()
    refresh_token = os.getenv("MAL_REFRESH_TOKEN", "").strip()
    return client_id, client_secret, refresh_token


def is_mal_configured():
    client_id, _, refresh_token = get_mal_env()
    return bool(client_id and refresh_token)


def save_config(client_id, client_secret, refresh_token):
    _append_config("MAL_CLIENT_ID", client_id)
    if client_secret:
        _append_config("MAL_CLIENT_SECRET", client_secret)
    _append_config("MAL_REFRESH_TOKEN", refresh_token)


def refresh_mal_token():
    """Exchange refresh_token for a valid access_token with in-memory caching."""
    global _CACHED_ACCESS_TOKEN, _TOKEN_EXPIRES_AT

    # Check in-memory cache first (valid for 30 days, cached buffer 60s)
    now = time.time()
    if _CACHED_ACCESS_TOKEN and now < _TOKEN_EXPIRES_AT:
        log_debug("Reusing cached in-memory MAL access token")
        return _CACHED_ACCESS_TOKEN

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

            access_token = token_json.get("access_token")
            expires_in = token_json.get("expires_in", 2592000)  # default 30 days
            _CACHED_ACCESS_TOKEN = access_token
            _TOKEN_EXPIRES_AT = now + expires_in - 300  # 5 minute safety buffer
            return access_token
    except Exception as e:
        log_debug(f"MAL token refresh exception: {e}")
    return None


def search_mal_id(title):
    access_token = refresh_mal_token()
    if not access_token:
        return None
    headers = {"Authorization": f"Bearer {access_token}"}
    clean_title = re_clean_title(title)
    params = {"q": clean_title, "limit": 5}
    try:
        res = requests.get(
            f"{API_URL}/anime", headers=headers, params=params, timeout=10
        )
        if res.status_code == 200:
            data = res.json()
            if data.get("data"):
                return data["data"][0]["node"]["id"]
    except Exception as e:
        log_debug(f"MAL search error: {e}")
    return None


def re_clean_title(t):
    import re

    t = re.sub(
        r"\b(TV|Movie|OVA|ONA|Special|Season \d+|Part \d+)\b",
        "",
        t,
        flags=re.IGNORECASE,
    )
    t = re.sub(r"[^\w\s]", " ", t)
    return " ".join(t.split())


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

    if not mal_id:
        mal_id = search_mal_id(anime_title)
        if not mal_id:
            if not quiet:
                print(
                    f"{C_YELLOW}⚠️  Could not locate '{anime_title}' on MyAnimeList.{C_RESET}"
                )
            return False, "Anime not found"

    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"num_watched_episodes": episode_num, "status": "watching"}
    try:
        url = f"{API_URL}/anime/{mal_id}/my_list_status"
        res = requests.put(url, headers=headers, data=data, timeout=10)
        if res.status_code == 200:
            if not quiet:
                print(
                    f"{C_GREEN}✓  Successfully synced Episode {episode_num} to MyAnimeList!{C_RESET}"
                )
            return True, "Synced"
        else:
            if not quiet:
                print(
                    f"{C_RED}❌ MAL API Error ({res.status_code}): {res.text}{C_RESET}"
                )
            return False, f"API Error {res.status_code}"
    except Exception as e:
        if not quiet:
            print(f"{C_RED}❌ Network error syncing to MyAnimeList: {e}{C_RESET}")
        return False, str(e)
