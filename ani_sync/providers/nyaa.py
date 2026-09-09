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
                        # Parse table rows with title, magnet, and seeders
                        # Typical row has <a href="/view/..." title="...">, magnet, and seeders count
                        row_blocks = re.findall(
                            r'<tr class="[^"]*default[^"]*">(.*?)</tr>',
                            page_text,
                            re.DOTALL,
                        )
                        matched_candidates = []
                        for block in row_blocks:
                            m_title = re.search(
                                r'<a href="/view/\d+" title="([^"]+)"', block
                            )
                            m_mag = re.search(
                                r'href=["\'](magnet:\?[^"\']+)["\']', block
                            )
                            if m_title and m_mag:
                                t_name = m_title.group(1)
                                if is_valid_match(t_name, clean_title):
                                    m_seeds = re.findall(
                                        r'<td class="text-center"[^>]*>([0-9]+)</td>',
                                        block,
                                    )
                                    seeds = int(m_seeds[0]) if m_seeds else 0
                                    matched_candidates.append(
                                        (seeds, t_name, html.unescape(m_mag.group(1)))
                                    )

                        if matched_candidates:
                            matched_candidates.sort(key=lambda x: x[0], reverse=True)
                            top_seeds, top_name, top_mag = matched_candidates[0]
                            log_debug(
                                f"NyaaProvider resolved healthiest swarm '{top_name}' with {top_seeds} seeders for '{clean_title}'"
                            )
                            return {
                                "1080p": top_mag,
                                "720p": top_mag,
                                "default": top_mag,
                                "type": "torrent",
                                "seeders": top_seeds,
                                "release_name": top_name,
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
                        rss_candidates = []
                        trackers = [
                            "udp://open.stealth.si:80/announce",
                            "udp://tracker.opentrackr.org:1337/announce",
                            "udp://exodus.desync.com:6969/announce",
                            "udp://tracker.torrent.eu.org:451/announce",
                            "udp://tracker.moeking.me:6969/announce",
                        ]
                        tr_params = "&".join(
                            [f"tr={urllib.parse.quote(tr)}" for tr in trackers]
                        )
                        for it in items:
                            item_title = (
                                it.find("title").text
                                if it.find("title") is not None
                                else ""
                            )
                            if is_valid_match(item_title, clean_title):
                                s_count = 0
                                info_hash = None
                                for child in it:
                                    if "seeders" in child.tag:
                                        try:
                                            s_count = int(child.text or 0)
                                        except Exception:
                                            pass
                                    elif "infoHash" in child.tag:
                                        info_hash = (child.text or "").strip()

                                if info_hash:
                                    magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(item_title)}&{tr_params}"
                                    rss_candidates.append((s_count, item_title, magnet))
                                else:
                                    link_elem = it.find("link")
                                    if (
                                        link_elem is not None
                                        and link_elem.text
                                        and link_elem.text.startswith("magnet:")
                                    ):
                                        rss_candidates.append(
                                            (s_count, item_title, link_elem.text)
                                        )

                        if rss_candidates:
                            rss_candidates.sort(key=lambda x: x[0], reverse=True)
                            top_seeds, top_name, top_mag = rss_candidates[0]
                            log_debug(
                                f"NyaaProvider resolved RSS magnet '{top_name}' with {top_seeds} seeds for query '{q}'"
                            )
                            return {
                                "1080p": top_mag,
                                "720p": top_mag,
                                "default": top_mag,
                                "type": "torrent",
                                "seeders": top_seeds,
                                "release_name": top_name,
                            }
                except Exception as e:
                    log_debug(f"NyaaProvider RSS on {base} failed: {e}")

        return {}
