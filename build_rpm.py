#!/usr/bin/env python3
"""Build script for Fedora/RHEL/openSUSE RPM packages of ani-sync."""

import shutil
import subprocess
from pathlib import Path

VERSION = "2.11.21"
PACKAGE_NAME = "ani-sync"
DIST_DIR = Path("dist")
DIST_DIR.mkdir(exist_ok=True)


def build_rpm():
    print(f"📦 Building RPM package for {PACKAGE_NAME} v{VERSION}...")
    rpmbuild_bin = shutil.which("rpmbuild")
    if not rpmbuild_bin:
        print(
            "⚠️  'rpmbuild' not found on system. On Fedora/RHEL/openSUSE, install via: sudo dnf install rpm-build"
        )
        print("   Spec file is ready at: packaging/rpm/ani-sync.spec")
        return False

    rpm_root = Path("build/rpmbuild")
    for d in ["BUILD", "RPMS", "SOURCES", "SPECS", "SRPMS"]:
        (rpm_root / d).mkdir(parents=True, exist_ok=True)

    # Archive source into SOURCES
    src_tar = rpm_root / "SOURCES" / f"{PACKAGE_NAME}-{VERSION}.tar.gz"
    tar_cmd = [
        "tar",
        "-czf",
        str(src_tar),
        "--transform",
        f"s,^,{PACKAGE_NAME}-{VERSION}/,",
        "ani_sync.py",
        "ani_sync",
        "README.md",
        "CHEATSHEET.md",
        "LICENSE",
    ]
    subprocess.run(tar_cmd, check=True)

    # Copy spec file
    spec_path = Path("packaging/rpm/ani-sync.spec")
    spec_dest = rpm_root / "SPECS" / "ani-sync.spec"
    shutil.copy(spec_path, spec_dest)

    # Run rpmbuild
    build_cmd = [
        "rpmbuild",
        "--define",
        f"_topdir {rpm_root.resolve()}",
        "-bb",
        str(spec_dest),
    ]
    res = subprocess.run(build_cmd)
    if res.returncode == 0:
        for rpm_file in (rpm_root / "RPMS").rglob("*.rpm"):
            target = DIST_DIR / rpm_file.name
            shutil.copy(rpm_file, target)
            print(f"✓ Built RPM package: {target}")
        return True
    return False


if __name__ == "__main__":
    build_rpm()
