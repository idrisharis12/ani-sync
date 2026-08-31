# -*- coding: utf-8 -*-
"""Kitsu JSON:API authentication and watch progress synchronization."""

import os
import requests

from ani_sync.config import _append_config, load_config, log_debug
from ani_sync.ui.themes import C_CYAN, C_GREEN, C_RESET, C_YELLOW

KITSU_API_URL = "https://kitsu.io/api/edge"
KITSU_TOKEN_URL = "https://kitsu.io/api/oauth/token"


def get_kitsu_env():
    load_config()
    token = os.getenv("KITSU_ACCESS_TOKEN", "").strip()
    user_id = os.getenv("KITSU_USER_ID", "").strip()
    return token, user_id


def is_kitsu_configured():
    token, _ = get_kitsu_env()
    return bool(token)


def save_kitsu_config(access_token, refresh_token=None, user_id=None):
    _append_config("KITSU_ACCESS_TOKEN", access_token)
    if refresh_token:
        _append_config("KITSU_REFRESH_TOKEN", refresh_token)
    if user_id:
        _append_config("KITSU_USER_ID", user_id)


def sync_episode_to_kitsu(anime_title, episode_num, quiet=False):
    """Sync episode progress to Kitsu library."""
    token, user_id = get_kitsu_env()
    if not token or not user_id:
        if not quiet:
            print(f"{C_YELLOW}ℹ️  Kitsu sync skipped (run 'ani-sync auth kitsu'){C_RESET}")
        return False, "Not configured"

    if not quiet:
        print(f"\n{C_CYAN}🔄 Syncing Episode {episode_num} to Kitsu...{C_RESET}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }
    try:
        # 1. Search anime ID
        r = requests.get(f"{KITSU_API_URL}/anime", headers=headers, params={"filter[text]": anime_title, "page[limit]": 1}, timeout=10)
        if r.status_code != 200:
            return False, "Search failed"
        results = r.json().get("data", [])
        if not results:
            return False, "Anime not found on Kitsu"
        anime_id = results[0]["id"]

        # 2. Check existing library entry
        r2 = requests.get(
            f"{KITSU_API_URL}/library-entries",
            headers=headers,
            params={"filter[user_id]": user_id, "filter[anime_id]": anime_id},
            timeout=10,
        )
        existing = r2.json().get("data", []) if r2.status_code == 200 else []

        if existing:
            entry_id = existing[0]["id"]
            payload = {
                "data": {
                    "id": entry_id,
                    "type": "libraryEntries",
                    "attributes": {"progress": episode_num, "status": "current"},
                }
            }
            patch_res = requests.patch(f"{KITSU_API_URL}/library-entries/{entry_id}", headers=headers, json=payload, timeout=10)
            if patch_res.status_code == 200:
                if not quiet:
                    print(f"{C_GREEN}✓ Successfully synced Episode {episode_num} to Kitsu!{C_RESET}")
                return True, "Synced"
        else:
            payload = {
                "data": {
                    "type": "libraryEntries",
                    "attributes": {"progress": episode_num, "status": "current"},
                    "relationships": {
                        "anime": {"data": {"type": "anime", "id": anime_id}},
                        "user": {"data": {"type": "users", "id": user_id}},
                    },
                }
            }
            post_res = requests.post(f"{KITSU_API_URL}/library-entries", headers=headers, json=payload, timeout=10)
            if post_res.status_code == 201:
                if not quiet:
                    print(f"{C_GREEN}✓ Created entry and synced Episode {episode_num} to Kitsu!{C_RESET}")
                return True, "Synced"
    except Exception as e:
        log_debug(f"Kitsu sync error: {e}")
    return False, "Failed"
