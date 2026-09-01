# -*- coding: utf-8 -*-
"""Multi-provider resolution engine with automatic failover."""

import concurrent.futures
import urllib.request

from ani_sync.config import USER_AGENT, log_debug
from ani_sync.providers.anidb import AniDBProvider
from ani_sync.providers.gogo import GogoProvider
from ani_sync.providers.hianime import HiAnimeProvider
from ani_sync.providers.nyaa import NyaaProvider
from ani_sync.config import get_config_dir
import importlib.util
from pathlib import Path

PROVIDERS = {
    "anidb": AniDBProvider(),
    "gogo": GogoProvider(),
    "hianime": HiAnimeProvider(),
    "nyaa": NyaaProvider(),
    "torrent": NyaaProvider(),
}

def load_plugins():
    plugins_dir = get_config_dir() / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)
    
    for file in plugins_dir.glob("*.py"):
        try:
            name = file.stem
            spec = importlib.util.spec_from_file_location(name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Find any class ending with Provider to register
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and attr.__name__.endswith("Provider") and attr.__name__ != "BaseProvider":
                    PROVIDERS[name] = attr()
                    log_debug(f"Loaded custom provider plugin: {name}")
        except Exception as e:
            log_debug(f"Failed to load plugin {file.name}: {e}")

load_plugins()


def verify_stream_url(url, timeout=0.8):
    """Fast HTTP HEAD check to verify CDN stream URL status (returns True if HTTP 200/206/302)."""
    if not url:
        return False
    try:
        req = urllib.request.Request(
            url,
            method="HEAD",
            headers={"User-Agent": USER_AGENT, "Referer": "https://anidb.app/"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status in (200, 206, 301, 302, 304)
    except Exception:
        return True


def resolve_streams(
    episode_id, mode="sub", anime_slug=None, ep_num=1, provider_name="auto"
):
    """Fetch streams with concurrent multi-provider lookup and automatic failover."""
    provider_name = (provider_name or "auto").lower()

    # 1. Selected specific provider
    if provider_name in PROVIDERS:
        try:
            streams = PROVIDERS[provider_name].get_streams(
                episode_id, mode=mode, anime_slug=anime_slug, ep_num=ep_num
            )
            if streams:
                return streams
        except Exception as e:
            log_debug(f"Selected provider {provider_name} failed: {e}")

    # 2. Try primary AniDB provider first
    try:
        anidb_res = PROVIDERS["anidb"].get_streams(
            episode_id, mode=mode, anime_slug=anime_slug, ep_num=ep_num
        )
        if anidb_res:
            log_debug("Streams resolved via primary provider 'anidb'")
            return anidb_res
    except Exception as e:
        log_debug(f"Primary provider 'anidb' attempt failed: {e}")

    # 3. Concurrent Failover: Run fallback providers (Gogo & HiAnime) in parallel
    def _fetch_from_provider(p_name):
        try:
            p = PROVIDERS[p_name]
            st = p.get_streams(
                episode_id, mode=mode, anime_slug=anime_slug, ep_num=ep_num
            )
            if st:
                log_debug(f"Streams resolved via fallback provider '{p_name}'")
                return p_name, st
        except Exception as e:
            log_debug(f"Fallback provider '{p_name}' error: {e}")
        return p_name, None

    fallback_providers = ["gogo", "hianime"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(_fetch_from_provider, p_name): p_name
            for p_name in fallback_providers
        }
        for future in concurrent.futures.as_completed(futures):
            p_name, st = future.result()
            if st:
                return st

    return {}
