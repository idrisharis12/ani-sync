#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ani-sync — Standalone launcher (backward-compatibility wrapper).

This script exists for backward compatibility with installers and standalone
deployments. The real implementation now lives in the `ani_sync` package.
"""

import os
import sys
import subprocess

# Ensure the package directory is on sys.path when running standalone.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from ani_sync.cli import main
except ImportError:
    print("\n\033[1;33m[!] ani-sync architecture has been updated.\033[0m")
    print(
        "It seems you updated using the legacy script updater, which did not download the new package files."
    )
    print("Automatically repairing your installation...\n")

    # Run the new install script to properly install the package
    try:
        subprocess.run(
            "curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | bash",
            shell=True,
            check=True,
        )
        print("\n\033[1;32m[✓] Repair complete! Please run ani-sync again.\033[0m")
    except Exception as e:
        print(f"\n\033[1;31m[x] Repair failed: {e}\033[0m")
        print("Please run this command manually:")
        print(
            "curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/install.sh | bash"
        )
    sys.exit(1)

if __name__ == "__main__":
    main()
