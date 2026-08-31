#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ani-sync — Standalone launcher (backward-compatibility wrapper).

This script exists for backward compatibility with installers and standalone
deployments that reference ``ani_sync.py`` at the repository root.  The real
implementation now lives in :mod:`ani_sync.cli`.
"""

import os
import sys

# Ensure the package directory is on sys.path when running standalone.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ani_sync.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
