# -*- coding: utf-8 -*-
"""Multi-provider resolution engine with automatic failover."""

from ani_sync.config import log_debug
from ani_sync.providers.anidb import AniDBProvider
from ani_sync.providers.gogo import GogoProvider
from ani_sync.providers.hianime import HiAnimeProvider

PROVIDERS = {
    "anidb": AniDBProvider(),
    "gogo": GogoProvider(),
    "hianime": HiAnimeProvider(),
}


def resolve_streams(episode_id, mode="sub", anime_slug=None, ep_num=1, provider_name="auto"):
    """Fetch streams with automatic fallback across AniDB, Gogo, and HiAnime providers."""
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

    # 2. Auto-Failover: Try AniDB -> Gogo -> HiAnime
    fallback_order = ["anidb", "gogo", "hianime"]
    for p_name in fallback_order:
        try:
            p = PROVIDERS[p_name]
            streams = p.get_streams(
                episode_id, mode=mode, anime_slug=anime_slug, ep_num=ep_num
            )
            if streams:
                log_debug(f"Streams successfully resolved via provider '{p_name}'")
                return streams
        except Exception as e:
            log_debug(f"Provider '{p_name}' failover attempt error: {e}")

    return {}
