# -*- coding: utf-8 -*-
"""Nyaa.si Torrent Provider for Peer-to-Peer Fallback."""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from ani_sync.providers.base import BaseProvider


class NyaaProvider(BaseProvider):
    name = "nyaa"

    def search(self, query):
        return []

    def get_episodes(self, slug):
        return []

    def get_streams(self, episode_id, mode="sub", anime_slug=None, ep_num=1):
        title = anime_slug.replace("-", " ") if anime_slug else episode_id

        # Format query for Nyaa: "Title {ep_num} 1080p"
        # Category 1_2 is English Translated Anime
        query_str = f"{title} {ep_num:02d} 1080p"
        if mode == "dub":
            query_str += " dub"

        query = urllib.parse.quote(query_str)
        url = f"https://nyaa.si/?page=rss&q={query}&c=1_2&f=0"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                xml_data = resp.read()

            root = ET.fromstring(xml_data)
            items = root.findall("./channel/item")
            if not items:
                return {}

            # Get the first torrent magnet link or torrent file
            first_item = items[0]
            torrent_url = first_item.find("link").text

            return {
                "default": torrent_url,
                "1080p": torrent_url,
                "720p": torrent_url,
                "type": "torrent",
            }
        except Exception:
            return {}
