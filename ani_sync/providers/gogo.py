# -*- coding: utf-8 -*-
"""Gogoanime and fast CDN secondary fallback scraper."""

import requests
import urllib.parse
from ani_sync.config import log_debug
from ani_sync.providers.base import BaseProvider


class GogoProvider(BaseProvider):
    name = "gogo"

    def search(self, query):
        endpoints = [
            f"https://api.consumet.org/anime/gogoanime/{urllib.parse.quote_plus(query)}",
            f"https://consumet.vercel.app/anime/gogoanime/{urllib.parse.quote_plus(query)}",
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
            f"https://api.consumet.org/anime/gogoanime/info/{slug}",
            f"https://consumet.vercel.app/anime/gogoanime/info/{slug}",
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
        target_id = episode_id
        if not target_id and anime_slug:
            clean_slug = anime_slug.rsplit("-", 1)[0]
            target_id = f"{clean_slug}-episode-{ep_num}"

        if not target_id:
            return streams

        endpoints = [
            f"https://api.consumet.org/anime/gogoanime/watch/{target_id}",
            f"https://consumet.vercel.app/anime/gogoanime/watch/{target_id}",
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
                log_debug(f"Gogo stream extraction error: {e}")
        return streams
