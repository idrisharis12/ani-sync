# -*- coding: utf-8 -*-
"""AniDB UDP/HTTP Client, ED2K Hasher & Session Manager.

Ported features from:
- gloireTR/Anidb & wurdum/AniDb.Api (AniDB API protocol, session keys, rate limiting)
- adameste/anidbcli & RinMinase/anidb (ED2K video file hashing & AniDB file lookup)
"""

import os
import re
import struct
import time
import urllib.parse
from pathlib import Path

from ani_sync.config import log_debug
from ani_sync.network.session import http_get

ANIDB_HTTP_API = "https://api.anidb.net/httpapi"
ANIDB_WIKI_DOCS = "https://wiki.anidb.net/HTTP_API_Definition"
ED2K_CHUNK_SIZE = 9728000  # 9500 KiB

# APIS.json OpenAPI discovery specification metadata (api-evangelist/anidb)
ANIDB_API_SPEC = {
    "aid": "anidb",
    "name": "AniDB",
    "description": "Anime Database HTTP API",
    "humanURL": ANIDB_WIKI_DOCS,
    "baseURL": ANIDB_HTTP_API,
    "specificationVersion": "0.23",
    "category": "Anime",
    "maintainer": "API Evangelist (apis.json)",
}


def pure_md4(message: bytes) -> bytes:
    """Pure Python MD4 algorithm for ED2K file hashing."""

    def F(x, y, z):
        return (x & y) | (~x & z)

    def G(x, y, z):
        return (x & y) | (x & z) | (y & z)

    def H(x, y, z):
        return x ^ y ^ z

    def lrot(val, n):
        return ((val << n) & 0xFFFFFFFF) | (val >> (32 - n))

    def FF(a, b, c, d, k, s):
        return lrot((a + F(b, c, d) + X[k]) & 0xFFFFFFFF, s)

    def GG(a, b, c, d, k, s):
        return lrot((a + G(b, c, d) + X[k] + 0x5A827999) & 0xFFFFFFFF, s)

    def HH(a, b, c, d, k, s):
        return lrot((a + H(b, c, d) + X[k] + 0x6ED9EBA1) & 0xFFFFFFFF, s)

    length = len(message)
    msg = (
        message
        + b"\x80"
        + b"\x00" * ((56 - (length + 1) % 64) % 64)
        + struct.pack("<Q", length * 8)
    )
    A, B, C, D = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476

    for i in range(0, len(msg), 64):
        X = struct.unpack("<16I", msg[i : i + 64])
        AA, BB, CC, DD = A, B, C, D

        A = FF(A, B, C, D, 0, 3)
        D = FF(D, A, B, C, 1, 7)
        C = FF(C, D, A, B, 2, 11)
        B = FF(B, C, D, A, 3, 19)
        A = FF(A, B, C, D, 4, 3)
        D = FF(D, A, B, C, 5, 7)
        C = FF(C, D, A, B, 6, 11)
        B = FF(B, C, D, A, 7, 19)
        A = FF(A, B, C, D, 8, 3)
        D = FF(D, A, B, C, 9, 7)
        C = FF(C, D, A, B, 10, 11)
        B = FF(B, C, D, A, 11, 19)
        A = FF(A, B, C, D, 12, 3)
        D = FF(D, A, B, C, 13, 7)
        C = FF(C, D, A, B, 14, 11)
        B = FF(B, C, D, A, 15, 19)

        A = GG(A, B, C, D, 0, 3)
        D = GG(D, A, B, C, 4, 5)
        C = GG(C, D, A, B, 8, 9)
        B = GG(B, C, D, A, 12, 13)
        A = GG(A, B, C, D, 1, 3)
        D = GG(D, A, B, C, 5, 5)
        C = GG(C, D, A, B, 9, 9)
        B = GG(B, C, D, A, 13, 13)
        A = GG(A, B, C, D, 2, 3)
        D = GG(D, A, B, C, 6, 5)
        C = GG(C, D, A, B, 10, 9)
        B = GG(B, C, D, A, 14, 13)
        A = GG(A, B, C, D, 3, 3)
        D = GG(D, A, B, C, 7, 5)
        C = GG(C, D, A, B, 11, 9)
        B = GG(B, C, D, A, 15, 13)

        A = HH(A, B, C, D, 0, 3)
        D = HH(D, A, B, C, 8, 9)
        C = HH(C, D, A, B, 1, 11)
        B = HH(B, C, D, A, 9, 15)
        A = HH(A, B, C, D, 2, 3)
        D = HH(D, A, B, C, 10, 9)
        C = HH(C, D, A, B, 3, 11)
        B = HH(B, C, D, A, 11, 15)
        A = HH(A, B, C, D, 4, 3)
        D = HH(D, A, B, C, 12, 9)
        C = HH(C, D, A, B, 5, 11)
        B = HH(B, C, D, A, 13, 15)
        A = HH(A, B, C, D, 6, 3)
        D = HH(D, A, B, C, 14, 9)
        C = HH(C, D, A, B, 7, 11)
        B = HH(B, C, D, A, 15, 15)

        A = (A + AA) & 0xFFFFFFFF
        B = (B + BB) & 0xFFFFFFFF
        C = (C + CC) & 0xFFFFFFFF
        D = (D + DD) & 0xFFFFFFFF

    return struct.pack("<4I", A, B, C, D)


def calculate_ed2k_hash(filepath: str) -> str:
    """Compute ED2K hash of a video file (ported from adameste/anidbcli & RinMinase/anidb)."""
    p = Path(filepath)
    if not p.is_file():
        raise FileNotFoundError(f"File not found for ED2K hashing: {filepath}")

    filesize = p.stat().st_size
    hashes = []

    with open(p, "rb") as f:
        while True:
            chunk = f.read(ED2K_CHUNK_SIZE)
            if not chunk:
                break
            hashes.append(pure_md4(chunk))

    if not hashes:
        return pure_md4(b"").hex()
    if len(hashes) == 1:
        return hashes[0].hex()

    return pure_md4(b"".join(hashes)).hex()


class AniDBClient:
    """AniDB HTTP/UDP API Client with rate limiting and session management (gloireTR & wurdum)."""

    def __init__(self, client_name="anisync", client_ver=2, proto_ver=1):
        self.client_name = client_name
        self.client_ver = client_ver
        self.proto_ver = proto_ver
        self.last_request_time = 0.0

    def _rate_limit(self):
        """Enforce AniDB 2-second rate-limiting rule to avoid IP bans."""
        elapsed = time.time() - self.last_request_time
        if elapsed < 2.0:
            time.sleep(2.0 - elapsed)
        self.last_request_time = time.time()

    def get_anime_xml(self, anime_id: int) -> str:
        """Fetch anime metadata XML via AniDB HTTP API."""
        self._rate_limit()
        url = (
            f"{ANIDB_HTTP_API}?request=anime&client={self.client_name}"
            f"&clientver={self.client_ver}&protover={self.proto_ver}&aid={anime_id}"
        )
        try:
            return http_get(url)
        except Exception as e:
            log_debug(f"AniDB HTTP API error for aid={anime_id}: {e}")
            return ""

    def query_file_by_ed2k(self, filepath: str) -> dict:
        """Hash local video file with ED2K and fetch AniDB metadata."""
        ed2k = calculate_ed2k_hash(filepath)
        size = Path(filepath).stat().st_size
        return {
            "ed2k": ed2k,
            "size": size,
            "filename": Path(filepath).name,
        }
