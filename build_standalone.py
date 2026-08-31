#!/usr/bin/env python3
"""
ani-sync — Multi-Platform Standalone Binary & Package Builder
Compiles standalone binaries, tarballs, zip archives, and package bundles
with zero external Python runtime dependencies required by end-users.
"""

import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

# Force UTF-8 encoding for standard streams on Windows runners
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

VERSION = "2.8.0"
BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"


def get_os_arch_tag():
    """Determine OS and architecture tag."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if machine in ("x86_64", "amd64"):
        arch = "x86_64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        arch = machine

    if system == "linux":
        return f"linux-{arch}", system, arch
    elif system == "darwin":
        return f"macos-{arch}", system, arch
    elif system == "windows":
        return f"windows-{arch}", system, arch
    return f"{system}-{arch}", system, arch


def compile_binary(tag, system):
    """Compile single-file binary using PyInstaller."""
    print(f"\n🔨 [1/4] Compiling standalone binary for {tag} with PyInstaller...")
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    exe_name = f"ani-sync-{tag}.exe" if system == "windows" else f"ani-sync-{tag}"
    out_path = DIST_DIR / exe_name

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        exe_name,
        "--clean",
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        str(BASE_DIR / "ani_sync.py"),
    ]

    res = subprocess.run(cmd)
    if res.returncode != 0 or not out_path.exists():
        print(f"❌ Failed to compile standalone binary for {tag}")
        return None

    # Make executable on Unix
    if system != "windows":
        out_path.chmod(0o755)

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"✓ Standalone binary created: {out_path.name} ({size_mb:.1f} MB)")
    return out_path


def create_archives(binary_path, tag, system):
    """Package binary with docs into tar.gz and zip archives."""
    print(f"\n📦 [2/4] Packaging distribution archive for {tag}...")
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    archive_base = f"ani-sync-v{VERSION}-{tag}"

    if system == "windows":
        zip_path = DIST_DIR / f"{archive_base}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(binary_path, arcname="ani-sync.exe")
            if (BASE_DIR / "README.md").exists():
                zf.write(BASE_DIR / "README.md", arcname="README.md")
            if (BASE_DIR / "CHEATSHEET.md").exists():
                zf.write(BASE_DIR / "CHEATSHEET.md", arcname="CHEATSHEET.md")
            if (BASE_DIR / "CREDITS.md").exists():
                zf.write(BASE_DIR / "CREDITS.md", arcname="CREDITS.md")
            if (BASE_DIR / "LICENSE").exists():
                zf.write(BASE_DIR / "LICENSE", arcname="LICENSE")
            if (BASE_DIR / "install.ps1").exists():
                zf.write(BASE_DIR / "install.ps1", arcname="install.ps1")
        print(
            f"✓ Created ZIP archive: {zip_path.name} ({zip_path.stat().st_size / 1024:.1f} KB)"
        )
        return zip_path
    else:
        tar_path = DIST_DIR / f"{archive_base}.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(binary_path, arcname="ani-sync")
            if (BASE_DIR / "README.md").exists():
                tar.add(BASE_DIR / "README.md", arcname="README.md")
            if (BASE_DIR / "CHEATSHEET.md").exists():
                tar.add(BASE_DIR / "CHEATSHEET.md", arcname="CHEATSHEET.md")
            if (BASE_DIR / "CREDITS.md").exists():
                tar.add(BASE_DIR / "CREDITS.md", arcname="CREDITS.md")
            if (BASE_DIR / "LICENSE").exists():
                tar.add(BASE_DIR / "LICENSE", arcname="LICENSE")
            if (BASE_DIR / "install.sh").exists():
                tar.add(BASE_DIR / "install.sh", arcname="install.sh")
        print(
            f"✓ Created Tarball archive: {tar_path.name} ({tar_path.stat().st_size / 1024:.1f} KB)"
        )
        return tar_path


def build_deb():
    """Build Debian / Ubuntu .deb package if build_deb.py exists."""
    deb_script = BASE_DIR / "build_deb.py"
    if deb_script.exists():
        print("\n📦 [3/4] Building Debian/Ubuntu package (.deb)...")
        res = subprocess.run([sys.executable, str(deb_script)])
        if res.returncode == 0:
            print("✓ Debian package built successfully!")


def generate_checksums():
    """Generate SHA256SUMS.txt for all built release artifacts in dist/."""
    print("\n🔐 [4/4] Generating SHA-256 checksums...")
    checksums = []
    for p in sorted(DIST_DIR.iterdir()):
        if p.is_file() and p.name != "SHA256SUMS.txt" and not p.name.endswith(".spec"):
            sha = hashlib.sha256(p.read_bytes()).hexdigest()
            checksums.append(f"{sha}  {p.name}\n")
            print(f"  {sha[:16]}...  {p.name}")

    sums_path = DIST_DIR / "SHA256SUMS.txt"
    sums_path.write_text("".join(checksums), encoding="utf-8")
    print(f"✓ Saved checksums to {sums_path.name}")


def main():
    print("=" * 60)
    print(f"   ani-sync v{VERSION} — Standalone Binary & Package Builder")
    print("=" * 60)

    tag, system, arch = get_os_arch_tag()
    bin_path = compile_binary(tag, system)

    if bin_path:
        create_archives(bin_path, tag, system)

    if system == "linux":
        build_deb()

    generate_checksums()

    print("\n🎉 Build process completed! All artifacts are in dist/:")
    for item in sorted(DIST_DIR.iterdir()):
        if item.is_file():
            size = item.stat().st_size
            size_str = (
                f"{size / 1024:.1f} KB"
                if size < 1024 * 1024
                else f"{size / (1024 * 1024):.1f} MB"
            )
            print(f"  📁 {item.name:<38} ({size_str})")


if __name__ == "__main__":
    main()
