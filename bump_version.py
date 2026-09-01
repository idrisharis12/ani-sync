#!/usr/bin/env python3
"""
ani-sync — Automated Version Bumper & Release Synchronizer
Synchronizes semantic versioning across all package manifests, scripts, and documentation.
"""

import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def get_current_version():
    config_file = BASE_DIR / "ani_sync" / "config.py"
    cli_file = BASE_DIR / "ani_sync" / "cli.py"

    for file_path in [config_file, cli_file]:
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)

    raise ValueError("Could not find VERSION in ani_sync/config.py or ani_sync/cli.py")


def calculate_next_version(current, bump_type):
    parts = current.split(".")
    if len(parts) != 3:
        raise ValueError(f"Version {current} is not in SemVer X.Y.Z format")
    major, minor, patch = map(int, parts)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    elif re.match(r"^\d+\.\d+\.\d+$", bump_type):
        return bump_type
    else:
        raise ValueError(f"Unknown bump type or invalid version: {bump_type}")


def update_file(path, pattern, replacement):
    if not path.exists():
        return False
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"  ✓ Updated {path.relative_to(BASE_DIR)}")
        return True
    return False


def bump_all(new_ver):
    curr = get_current_version()
    print(f"🚀 Bumping version: v{curr} ──► v{new_ver}\n")

    # 1. ani_sync.py
    update_file(
        BASE_DIR / "ani_sync.py",
        r'VERSION\s*=\s*["\'][^"\']+["\']',
        f'VERSION = "{new_ver}"',
    )

    # 1b. ani_sync/config.py
    update_file(
        BASE_DIR / "ani_sync" / "config.py",
        r'VERSION\s*=\s*["\'][^"\']+["\']',
        f'VERSION = "{new_ver}"',
    )

    # 3. pyproject.toml
    update_file(
        BASE_DIR / "pyproject.toml",
        r'version\s*=\s*["\'][^"\']+["\']',
        f'version = "{new_ver}"',
    )

    # 4. PKGBUILD & AUR files
    update_file(BASE_DIR / "PKGBUILD", r"pkgver=[^\n]+", f"pkgver={new_ver}")
    update_file(
        BASE_DIR / "packaging/aur/ani-sync/PKGBUILD",
        r"pkgver=[^\n]+",
        f"pkgver={new_ver}",
    )
    update_file(
        BASE_DIR / "packaging/aur/ani-sync/.SRCINFO",
        r"pkgver = [^\n]+",
        f"pkgver = {new_ver}",
    )
    update_file(
        BASE_DIR / "packaging/aur/ani-sync-bin/PKGBUILD",
        r"pkgver=[^\n]+",
        f"pkgver={new_ver}",
    )
    update_file(
        BASE_DIR / "packaging/aur/ani-sync-bin/.SRCINFO",
        r"pkgver = [^\n]+",
        f"pkgver = {new_ver}",
    )

    # 5. RPM spec
    update_file(
        BASE_DIR / "packaging/rpm/ani-sync.spec",
        r"Version:\s*[^\n]+",
        f"Version:        {new_ver}",
    )

    # 6. Formula/ani-sync.rb
    update_file(
        BASE_DIR / "Formula/ani-sync.rb",
        r"v\d+\.\d+\.\d+\.tar\.gz",
        f"v{new_ver}.tar.gz",
    )

    # 7. build_deb.py & build_rpm.py & build_standalone.py & default.nix
    update_file(
        BASE_DIR / "build_deb.py",
        r'VERSION\s*=\s*["\'][^"\']+["\']',
        f'VERSION = "{new_ver}"',
    )
    update_file(
        BASE_DIR / "build_rpm.py",
        r'VERSION\s*=\s*["\'][^"\']+["\']',
        f'VERSION = "{new_ver}"',
    )
    update_file(
        BASE_DIR / "build_standalone.py",
        r'VERSION\s*=\s*["\'][^"\']+["\']',
        f'VERSION = "{new_ver}"',
    )
    update_file(
        BASE_DIR / "default.nix",
        r'version\s*=\s*["\'][^"\']+["\'];',
        f'version = "{new_ver}";',
    )
    update_file(
        BASE_DIR / "packaging/ani-sync.json",
        r'"version"\s*:\s*["\'][^"\']+["\']',
        f'"version": "{new_ver}"',
    )
    
    # 8. README.md
    update_file(
        BASE_DIR / "README.md",
        r'ani-sync_\d+\.\d+\.\d+_all\.deb',
        f'ani-sync_{new_ver}_all.deb',
    )

    print(
        f"\n✨ Version successfully bumped to v{new_ver} across all project manifests!"
    )


def main():
    if len(sys.argv) < 2:
        print(f"Current version: v{get_current_version()}")
        print("Usage:")
        print("    python bump_version.py patch   # e.g. 2.0.0 -> 2.0.1")
        print("    python bump_version.py minor   # e.g. 2.0.0 -> 2.1.0")
        print("    python bump_version.py major   # e.g. 2.0.0 -> 3.0.0")
        print("    python bump_version.py 2.1.0   # explicit version")
        return

    bump_arg = sys.argv[1].lower().lstrip("v")
    curr = get_current_version()
    new_ver = calculate_next_version(curr, bump_arg)
    bump_all(new_ver)


if __name__ == "__main__":
    main()
