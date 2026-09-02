#!/usr/bin/env python3
import io
import tarfile
import time
from pathlib import Path

VERSION = "2.11.23"
PACKAGE_NAME = "ani-sync"
DIST_DIR = Path("dist")
DIST_DIR.mkdir(exist_ok=True)
DEB_PATH = DIST_DIR / f"{PACKAGE_NAME}_{VERSION}_all.deb"

# 1. debian-binary
debian_binary = b"2.0\n"

# 2. control.tar.gz
control_content = f"""Package: ani-sync
Version: {VERSION}
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-requests, python3-tqdm, mpv, yt-dlp, curl, fzf
Maintainer: Idris Haris <https://github.com/idrisharis12/ani-sync>
Description: Terminal anime streamer and MyAnimeList auto-sync client
 Stream anime episodes directly in your terminal and automatically
 synchronize episode progress and watch status to MyAnimeList.
""".encode("utf-8")

postinst_content = f"""#!/usr/bin/env bash
set -e
if [ -d "/etc/apt/apt.conf.d" ]; then
    cat << 'APTHOOK' > /etc/apt/apt.conf.d/99ani-sync-updater
APT::Update::Post-Invoke-Success {{ "if command -v ani-sync >/dev/null 2>&1; then ani-sync update --quiet || true; fi"; }};
APTHOOK
    chmod 644 /etc/apt/apt.conf.d/99ani-sync-updater
fi
echo "✓ ani-sync v{VERSION} successfully installed!"
echo "Run 'ani-sync' to get started."
exit 0
""".encode("utf-8")

control_tar_buf = io.BytesIO()
with tarfile.open(fileobj=control_tar_buf, mode="w:gz") as tar:
    # control file
    ti = tarfile.TarInfo("control")
    ti.size = len(control_content)
    ti.mode = 0o644
    ti.mtime = int(time.time())
    tar.addfile(ti, io.BytesIO(control_content))

    # postinst file
    ti_post = tarfile.TarInfo("postinst")
    ti_post.size = len(postinst_content)
    ti_post.mode = 0o755
    ti_post.mtime = int(time.time())
    tar.addfile(ti_post, io.BytesIO(postinst_content))

control_tar_bytes = control_tar_buf.getvalue()

# 3. data.tar.gz
with open("ani_sync.py", "rb") as f:
    script_content = f.read()

launcher_content = """#!/usr/bin/env bash
exec python3 /usr/share/ani-sync/ani_sync.py "$@"
""".encode("utf-8")

data_tar_buf = io.BytesIO()
with tarfile.open(fileobj=data_tar_buf, mode="w:gz") as tar:
    # /usr/share/ani-sync/ani_sync.py
    ti_share = tarfile.TarInfo("usr/share/ani-sync/ani_sync.py")
    ti_share.size = len(script_content)
    ti_share.mode = 0o755
    ti_share.mtime = int(time.time())
    tar.addfile(ti_share, io.BytesIO(script_content))

    # /usr/share/ani-sync/ani_sync subpackage
    pkg_dir = Path("ani_sync")
    if pkg_dir.exists():
        for fpath in pkg_dir.rglob("*.py"):
            rel_path = fpath.relative_to(pkg_dir)
            tar_target = f"usr/share/ani-sync/ani_sync/{rel_path.as_posix()}"
            with open(fpath, "rb") as pf:
                pcontent = pf.read()
            ti_p = tarfile.TarInfo(tar_target)
            ti_p.size = len(pcontent)
            ti_p.mode = 0o644
            ti_p.mtime = int(time.time())
            tar.addfile(ti_p, io.BytesIO(pcontent))

    # /usr/bin/ani-sync
    ti_bin = tarfile.TarInfo("usr/bin/ani-sync")
    ti_bin.size = len(launcher_content)
    ti_bin.mode = 0o755
    ti_bin.mtime = int(time.time())
    tar.addfile(ti_bin, io.BytesIO(launcher_content))

data_tar_bytes = data_tar_buf.getvalue()


# 4. Pack into AR archive (Debian .deb format)
def create_ar_header(filename, size):
    return (
        f"{filename:<16}"
        f"{int(time.time()):<12}"
        f"{'0':<6}"
        f"{'0':<6}"
        f"{'100644':<8}"
        f"{size:<10}"
        f"`\n"
    ).encode("ascii")


with open(DEB_PATH, "wb") as deb:
    # AR file signature
    deb.write(b"!<arch>\n")

    # debian-binary
    deb.write(create_ar_header("debian-binary", len(debian_binary)))
    deb.write(debian_binary)
    if len(debian_binary) % 2 != 0:
        deb.write(b"\n")

    # control.tar.gz
    deb.write(create_ar_header("control.tar.gz", len(control_tar_bytes)))
    deb.write(control_tar_bytes)
    if len(control_tar_bytes) % 2 != 0:
        deb.write(b"\n")

    # data.tar.gz
    deb.write(create_ar_header("data.tar.gz", len(data_tar_bytes)))
    deb.write(data_tar_bytes)
    if len(data_tar_bytes) % 2 != 0:
        deb.write(b"\n")

print(f"✓ Built Debian package: {DEB_PATH} ({DEB_PATH.stat().st_size} bytes)")
