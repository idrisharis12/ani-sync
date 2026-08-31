# -*- coding: utf-8 -*-
"""Executable entrypoint for python -m ani_sync."""

import sys
import ani_sync

if __name__ == "__main__":
    import ani_sync.config

    # Execute root script or package entrypoint
    try:
        import ani_sync.cli as cli

        cli.main()
    except (ImportError, AttributeError):
        import importlib

        mod = importlib.import_module("ani_sync")
        if hasattr(mod, "main"):
            mod.main()
        else:
            print(f"ani-sync v{ani_sync.config.VERSION}")
