# -*- coding: utf-8 -*-
"""Base abstract class for anime stream and metadata scrapers."""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    name = "base"

    @abstractmethod
    def search(self, query):
        """Search anime and return list of dicts: [{'title': str, 'slug': str}]."""
        pass

    @abstractmethod
    def get_episodes(self, slug):
        """Fetch available episode list for anime: [{'number': int, 'id': str}]."""
        pass

    @abstractmethod
    def get_streams(self, episode_id, mode="sub", anime_slug=None, ep_num=1):
        """Resolve streams returning dict: {'1080p': url, '720p': url, 'Auto / Best': url}."""
        pass
