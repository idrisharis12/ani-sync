# -*- coding: utf-8 -*-
"""High-performance network session, proxy routing, and DoH DNS-over-HTTPS engine."""

import json
import os
import subprocess
import urllib.parse
import requests

from ani_sync.config import USER_AGENT, log_debug

_HTTP_SESSION = None
_CUSTOM_PROXY = None


def set_custom_proxy(proxy_url):
    """Set global custom proxy for all HTTP requests."""
    global _CUSTOM_PROXY, _HTTP_SESSION
    _CUSTOM_PROXY = proxy_url
    if _HTTP_SESSION is not None and proxy_url:
        _HTTP_SESSION.proxies.update({"http": proxy_url, "https": proxy_url})


def resolve_doh(domain):
    """Resolve domain using Cloudflare DNS-over-HTTPS (DoH) to bypass ISP DNS poisoning."""
    try:
        url = f"https://cloudflare-dns.com/dns-query?name={domain}&type=A"
        headers = {"Accept": "application/dns-json", "User-Agent": USER_AGENT}
        r = requests.get(url, headers=headers, timeout=3)
        if r.status_code == 200:
            data = r.json()
            answers = data.get("Answer", [])
            for ans in answers:
                if ans.get("type") == 1:  # Type A (IPv4)
                    return ans.get("data")
    except Exception as e:
        log_debug(f"DoH resolution error for {domain}: {e}")
    return None


def get_http_session():
    """Return shared requests Session configured with browser headers and proxy."""
    global _HTTP_SESSION
    if _HTTP_SESSION is None:
        _HTTP_SESSION = requests.Session()
        _HTTP_SESSION.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://anidb.app/",
                "Sec-Ch-Ua": '"Not-A.Brand";v="99", "Chromium";v="124", "Google Chrome";v="124"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Linux"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
        )
        proxy = _CUSTOM_PROXY or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY") or os.getenv("ALL_PROXY")
        if proxy:
            _HTTP_SESSION.proxies.update({"http": proxy, "https": proxy})
    return _HTTP_SESSION


def http_get(url, is_json=False, timeout=12, headers=None):
    """Fetch URL with session and automatic curl fallback."""
    session = get_http_session()

    # 1. Try requests
    try:
        res = session.get(url, headers=headers, timeout=timeout)
        if res.status_code == 200:
            return res.json() if is_json else res.text
    except Exception as e:
        log_debug(f"requests.get failed for {url}: {e}")

    # 2. Try curl fallback
    try:
        cmd = [
            "curl",
            "-sL",
            "-A",
            USER_AGENT,
            "--max-time",
            str(timeout + 3),
            "-H",
            "Referer: https://anidb.app/",
            "-H",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            url,
        ]
        if _CUSTOM_PROXY:
            cmd.extend(["-x", _CUSTOM_PROXY])
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
        if out.strip():
            return json.loads(out) if is_json else out
    except Exception as e:
        log_debug(f"curl fallback failed for {url}: {e}")

    # 3. Final retry with direct request
    res = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Referer": "https://anidb.app/"},
        timeout=timeout + 8,
    )
    res.raise_for_status()
    return res.json() if is_json else res.text
