# -*- coding: utf-8 -*-
"""AniDB primary HLS streaming provider backend."""

import html
import re
import urllib.parse

from ani_sync.config import log_debug
from ani_sync.network.session import http_get
from ani_sync.providers.base import BaseProvider

ANIDB_BASE = "https://anidb.app"


class AniDBProvider(BaseProvider):
    name = "anidb"

    def search(self, query):
        url = f"{ANIDB_BASE}/browse?q={urllib.parse.quote_plus(query)}"
        html_text = http_get(url)
        matches = re.findall(r"/anime/([a-z0-9-]+-[0-9]+).*?alt=\"([^\"]+)\"", html_text, re.DOTALL)
        results = []
        seen = set()
        for slug, raw_title in matches:
            if slug not in seen:
                seen.add(slug)
                title = html.unescape(raw_title).strip()
                results.append({"slug": slug, "title": title})
        return results

    def get_details(self, slug):
        url = f"{ANIDB_BASE}/anime/{slug}"
        html_text = http_get(url)
        mal_id_match = re.search(r"myanimelist\.net/anime/([0-9]+)", html_text)
        mal_id = int(mal_id_match.group(1)) if mal_id_match else None

        seasons = []
        season_section = re.search(r">Seasons<.*?>Details<", html_text, re.DOTALL)
        if season_section:
            sec_text = season_section.group(0)
            s_matches = re.findall(r"/anime/([a-z0-9-]+-[0-9]+)\"[^>]*title=\"([^\"]+)\"", sec_text)
            seen = {slug}
            for s_slug, s_title in s_matches:
                if s_slug not in seen:
                    seen.add(s_slug)
                    seasons.append({"slug": s_slug, "title": html.unescape(s_title).strip()})
        return {"mal_id": mal_id, "seasons": seasons}

    def get_episodes(self, slug):
        anime_id = slug.split("-")[-1]
        url = f"{ANIDB_BASE}/api/frontend/anime/{anime_id}/episodes"
        data = http_get(url, is_json=True)
        return data.get("episodes", [])

    def get_streams(self, episode_id, mode="sub", anime_slug=None, ep_num=1):
        streams = {}
        if not episode_id:
            return streams
        try:
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

            if embed_url:
                embed_html = http_get(embed_url)
                m3u8_match = re.search(r"file:\s*['\"]([^'\"]+)['\"]", embed_html)
                if m3u8_match:
                    master_m3u8_url = m3u8_match.group(1)
                    master_content = http_get(master_m3u8_url)

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
        except Exception as e:
            log_debug(f"AniDB stream extraction error: {e}")
        return streams
