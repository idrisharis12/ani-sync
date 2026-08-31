# -*- coding: utf-8 -*-
"""Entry point for ``python -m ani_sync``.

This module now forwards directly to the package's ``main`` function defined in
``ani_sync.__init__``. The previous indirect import of a non‑existent ``cli``
module has been removed.
"""

from . import main

if __name__ == "__main__":
    main()
