# -*- coding: utf-8 -*-
"""AniList GraphQL API authentication and watch progress synchronization."""

import os
import requests

from ani_sync.config import _append_config, load_config, log_debug
from ani_sync.ui.themes import C_BOLD, C_CYAN, C_GREEN, C_RED, C_RESET, C_YELLOW

ANILIST_API_URL = "https://graphql.anilist.co"
ANILIST_AUTH_URL = "https://anilist.co/api/v2/oauth/authorize"


def get_anilist_env():
    load_config()
    return os.getenv("ANILIST_ACCESS_TOKEN", "").strip()


def is_anilist_configured():
    return bool(get_anilist_env())


def save_anilist_config(token):
    _append_config("ANILIST_ACCESS_TOKEN", token)


def sync_episode_to_anilist(anime_title, episode_num, quiet=False):
    """Sync episode progress to AniList via GraphQL mutation."""
    token = get_anilist_env()
    if not token:
        if not quiet:
            print(
                f"{C_YELLOW}ℹ️  AniList sync skipped (run 'ani-sync auth anilist'){C_RESET}"
            )
        return False, "Not configured"

    if not quiet:
        print(f"\n{C_CYAN}🔄 Syncing Episode {episode_num} to AniList...{C_RESET}")

    # Search Media ID
    query = """
    query ($search: String) {
        Media (search: $search, type: ANIME) {
            id
            title { romaji english }
        }
    }
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r = requests.post(
            ANILIST_API_URL,
            json={"query": query, "variables": {"search": anime_title}},
            headers=headers,
            timeout=10,
        )
        if r.status_code != 200:
            return False, "Media search failed"
        data = r.json()
        media = data.get("data", {}).get("Media")
        if not media:
            return False, "Media not found on AniList"
        media_id = media["id"]

        # Update Progress
        mutation = """
        mutation ($mediaId: Int, $progress: Int, $status: MediaListStatus) {
            SaveMediaListEntry (mediaId: $mediaId, progress: $progress, status: $status) {
                id
                progress
                status
            }
        }
        """
        r2 = requests.post(
            ANILIST_API_URL,
            json={
                "query": mutation,
                "variables": {
                    "mediaId": media_id,
                    "progress": episode_num,
                    "status": "CURRENT",
                },
            },
            headers=headers,
            timeout=10,
        )
        if r2.status_code == 200:
            if not quiet:
                print(
                    f"{C_GREEN}✓ Successfully synced Episode {episode_num} to AniList!{C_RESET}"
                )
            return True, "Synced"
    except Exception as e:
        log_debug(f"AniList sync error: {e}")
    return False, "Failed"
