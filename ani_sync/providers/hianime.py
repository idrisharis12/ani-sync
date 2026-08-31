# -*- coding: utf-8 -*-
"""HiAnime / Zoro high-definition streaming provider."""

import requests
import urllib.parse
from ani_sync.config import log_debug
from ani_sync.providers.base import BaseProvider


class HiAnimeProvider(BaseProvider):
    name = "hianime"

    def search(self, query):
        endpoints = [
            f"https://api.consumet.org/anime/zoro/{urllib.parse.quote_plus(query)}",
            f"https://consumet.vercel.app/anime/zoro/{urllib.parse.quote_plus(query)}",
        ]
        for url in endpoints:
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    results = r.json().get("results", [])
                    return [
                        {"title": x.get("title"), "slug": x.get("id")} for x in results
                    ]
            except Exception:
                pass
        return []

    def get_episodes(self, slug):
        endpoints = [
            f"https://api.consumet.org/anime/zoro/info/{slug}",
            f"https://consumet.vercel.app/anime/zoro/info/{slug}",
        ]
        for url in endpoints:
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    episodes = r.json().get("episodes", [])
                    return [
                        {"number": ep.get("number"), "id": ep.get("id")}
                        for ep in episodes
                    ]
            except Exception:
                pass
        return []

    def get_streams(self, episode_id, mode="sub", anime_slug=None, ep_num=1):
        streams = {}
        if not episode_id:
            return streams
        endpoints = [
            f"https://api.consumet.org/anime/zoro/watch/{episode_id}",
            f"https://consumet.vercel.app/anime/zoro/watch/{episode_id}",
        ]
        for url in endpoints:
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    sources = r.json().get("sources", [])
                    for s in sources:
                        q = s.get("quality", "Auto / Best")
                        if q == "default":
                            q = "Auto / Best"
                        streams[q] = s.get("url")
                    if streams:
                        break
            except Exception as e:
                log_debug(f"HiAnime stream extraction error: {e}")
        return streams
