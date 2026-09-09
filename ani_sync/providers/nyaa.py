# -*- coding: utf-8 -*-
"""Nyaa.si Torrent Provider for Peer-to-Peer Fallback."""

import html
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from ani_sync.config import USER_AGENT, log_debug
from ani_sync.providers.base import BaseProvider


class NyaaProvider(BaseProvider):
    name = "nyaa"

    def search(self, query):
        return []

    def get_episodes(self, slug):
        return []

    def get_streams(self, episode_id, mode="sub", anime_slug=None, ep_num=1):
        """Fetch torrent magnet links from resilient Nyaa mirrors."""
        raw_title = anime_slug or episode_id or ""
        # Clean slug: remove trailing numeric IDs e.g. -1234
        clean_title = re.sub(r"-\d+$", "", raw_title).replace("-", " ").strip()
        if not clean_title:
            return {}

        queries = [
            f'"{clean_title}" {ep_num:02d}',
            f'"{clean_title}" {ep_num}',
            f"{clean_title} {ep_num:02d}",
            f"{clean_title} {ep_num}",
        ]
        if mode == "dub":
            queries = [f"{q} dub" for q in queries] + queries

        mirrors = [
            "https://nyaa.net",
            "https://nyaa.si",
            "https://nyaa.land",
        ]

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        # Strict title boundary validation
        def is_valid_match(torrent_name, target):
            t_low = torrent_name.lower()
            s_low = target.lower()
            if s_low not in t_low:
                return False
            # Find the position of s_low
            idx = t_low.find(s_low)
            after = t_low[idx + len(s_low) :].strip()
            # If followed immediately by 'with ', 'and ', or alphanumeric words before delimiters
            if re.match(r"^(with\s+|and\s+|vs\.?\s+|at\s+)", after):
                return False
            return True

        for q in queries:
            encoded_q = urllib.parse.quote_plus(q)
            for base in mirrors:
                # 1. Try HTML search table sorted by seeders
                search_url = f"{base}/?f=0&c=1_2&s=seeders&o=desc&q={encoded_q}"
                try:
                    req = urllib.request.Request(search_url, headers=headers)
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        page_text = resp.read().decode("utf-8", errors="ignore")
                        # Parse table rows to get both title and magnet link
                        rows = re.findall(
                            r'<tr class="[^"]*default[^"]*">.*?<a href="/view/\d+" title="([^"]+)".*?href=["\'](magnet:\?[^"\']+)["\']',
                            page_text,
                            re.DOTALL,
                        )
                        for t_title, mag in rows:
                            if is_valid_match(t_title, clean_title):
                                first_mag = html.unescape(mag)
                                log_debug(
                                    f"NyaaProvider verified match '{t_title}' for '{clean_title}'"
                                )
                                return {
                                    "1080p": first_mag,
                                    "720p": first_mag,
                                    "default": first_mag,
                                    "type": "torrent",
                                }
                        # Fallback to direct magnets if regex table match didn't catch rows
                        if not rows:
                            magnets = re.findall(
                                r'href=["\'](magnet:\?[^"\']+)["\']', page_text
                            )
                            if magnets and f'"{clean_title}"' in q:
                                first_mag = html.unescape(magnets[0])
                                return {
                                    "1080p": first_mag,
                                    "720p": first_mag,
                                    "default": first_mag,
                                    "type": "torrent",
                                }
                except Exception as e:
                    log_debug(f"NyaaProvider search on {base} failed: {e}")

                # 2. Try RSS endpoint fallback sorted by seeders
                rss_url = f"{base}/?page=rss&q={encoded_q}&c=1_2&f=0&s=seeders&o=desc"
                try:
                    req = urllib.request.Request(rss_url, headers=headers)
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        xml_data = resp.read()
                        root = ET.fromstring(xml_data)
                        items = root.findall("./channel/item")
                        if items:
                            # Parse seeders from custom element if present to pick top seeded item
                            best_item = items[0]
                            max_seeds = -1
                            for it in items:
                                for child in it:
                                    if "seeders" in child.tag:
                                        try:
                                            s_count = int(child.text or 0)
                                            if s_count > max_seeds:
                                                max_seeds = s_count
                                                best_item = it
                                        except Exception:
                                            pass
                                        break
                            torrent_url = best_item.find("link").text
                            log_debug(
                                f"NyaaProvider resolved RSS item from {base} with {max_seeds} seeds for query '{q}'"
                            )
                            return {
                                "1080p": torrent_url,
                                "720p": torrent_url,
                                "default": torrent_url,
                                "type": "torrent",
                            }
                except Exception as e:
                    log_debug(f"NyaaProvider RSS on {base} failed: {e}")

        return {}
