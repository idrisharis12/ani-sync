# -*- coding: utf-8 -*-
"""Local Docker Scraper Provider for ultra-low latency (<50ms) streaming."""

import json
import urllib.parse
import urllib.request
from ani_sync.config import USER_AGENT, log_debug
from ani_sync.providers.base import BaseProvider


class LocalProvider(BaseProvider):
    name = "local"

    def __init__(self, base_urls=None):
        self.base_urls = base_urls or [
            "http://localhost:4000",
            "http://127.0.0.1:4000",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]

    def get_active_endpoint(self):
        """Quick health check to find active local scraper container."""
        for base in self.base_urls:
            try:
                req = urllib.request.Request(
                    f"{base}/",
                    headers={"User-Agent": USER_AGENT},
                )
                with urllib.request.urlopen(req, timeout=0.2) as resp:
                    if resp.status in (200, 404):
                        return base
            except Exception:
                continue
        return None

    def search(self, query):
        base = self.get_active_endpoint()
        if not base:
            return []
        endpoints = [
            f"{base}/anime/search?q={urllib.parse.quote_plus(query)}",
            f"{base}/api/v2/hianime/search?q={urllib.parse.quote_plus(query)}",
            f"{base}/anime/gogoanime/{urllib.parse.quote_plus(query)}",
        ]
        for url in endpoints:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    results = (
                        data.get("animes")
                        or data.get("results")
                        or data.get("data", {}).get("animes")
                        or []
                    )
                    out = []
                    for it in results:
                        out.append(
                            {
                                "title": it.get("name") or it.get("title"),
                                "slug": it.get("id"),
                            }
                        )
                    if out:
                        return out
            except Exception:
                pass
        return []

    def get_episodes(self, slug):
        base = self.get_active_endpoint()
        if not base:
            return []
        endpoints = [
            f"{base}/anime/episodes/{slug}",
            f"{base}/api/v2/hianime/anime/{slug}/episodes",
            f"{base}/anime/gogoanime/info/{slug}",
        ]
        for url in endpoints:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    eps = (
                        data.get("episodes")
                        or data.get("data", {}).get("episodes")
                        or []
                    )
                    out = []
                    for e in eps:
                        out.append(
                            {
                                "number": e.get("number"),
                                "id": e.get("episodeId") or e.get("id"),
                            }
                        )
                    if out:
                        return out
            except Exception:
                pass
        return []

    def get_streams(self, episode_id, mode="sub", anime_slug=None, ep_num=1):
        base = self.get_active_endpoint()
        if not base:
            return {}

        target_id = episode_id or (
            f"{anime_slug}-episode-{ep_num}" if anime_slug else None
        )
        if not target_id:
            return {}

        endpoints = [
            f"{base}/anime/episode-srcs?id={urllib.parse.quote_plus(target_id)}&server=hd-1&category={mode}",
            f"{base}/api/v2/hianime/episode/sources?animeEpisodeId={urllib.parse.quote_plus(target_id)}&category={mode}",
            f"{base}/anime/gogoanime/watch/{urllib.parse.quote_plus(target_id)}",
        ]
        streams = {}
        for url in endpoints:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    sources = (
                        data.get("sources") or data.get("data", {}).get("sources") or []
                    )
                    for s in sources:
                        q = s.get("quality") or "Auto / Best"
                        if q == "default":
                            q = "Auto / Best"
                        url_stream = s.get("url")
                        if url_stream:
                            streams[q] = url_stream
                    if streams:
                        log_debug(
                            f"LocalProvider resolved {len(streams)} stream(s) via {base}"
                        )
                        return streams
            except Exception as e:
                log_debug(f"LocalProvider stream extraction failed on {url}: {e}")

        return streams
