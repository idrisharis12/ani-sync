# -*- coding: utf-8 -*-
"""ani-sync — Terminal Anime Streaming & Multi-Platform Tracking Engine."""

from ani_sync import config
from ani_sync.config import (
    VERSION,
    CONFIG_DIR,
    CONFIG_PATH,
    HISTORY_PATH,
    CACHE_DIR,
    IS_WINDOWS,
    IS_TERMUX,
    sanitize_filename,
    load_config,
    save_history,
    load_history,
    get_last_watched,
    _append_config,
)
from ani_sync.ui import themes
from ani_sync.ui.themes import apply_theme, THEMES, get_current_theme

__version__ = VERSION


# Backward-compatibility alias
def __getattr__(name):
    if name == "CURRENT_THEME":
        return themes.get_current_theme()
    if hasattr(config, name):
        return getattr(config, name)
    if hasattr(themes, name):
        return getattr(themes, name)
    raise AttributeError(f"module 'ani_sync' has no attribute '{name}'")
