#!/usr/bin/env bash
# ==============================================================================
# ani-sync Universal Auto-Installer (Linux, Arch Linux, macOS, & Termux/Android)
# Automatically installs ani-sync, FZF, MPV, yt-dlp, chafa, ffmpeg & dependencies
# ==============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

echo -e "${CYAN}${BOLD}"
echo "  ============================================"
echo "          ani-sync Universal Installer        "
echo "     Stream Anime & Auto-Sync Watch Progress  "
echo "  ============================================"
echo -e "${NC}"

# Detect Termux / Android environment
IS_TERMUX=false
if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux" ] || [[ "$PREFIX" == *"com.termux"* ]]; then
    IS_TERMUX=true
fi

# Detect installation target directory
if [ "$IS_TERMUX" = true ]; then
    INSTALL_DIR="${PREFIX:-/data/data/com.termux/files/usr}/bin"
    SHARE_DIR="${PREFIX:-/data/data/com.termux/files/usr}/share/ani-sync"
    SUDO_CMD=""
elif [ "$EUID" -eq 0 ]; then
    INSTALL_DIR="/usr/local/bin"
    SHARE_DIR="/usr/local/share/ani-sync"
    SUDO_CMD=""
else
    INSTALL_DIR="${HOME}/.local/bin"
    SHARE_DIR="${HOME}/.local/share/ani-sync"
    mkdir -p "$INSTALL_DIR"
    if command -v sudo &>/dev/null; then
        SUDO_CMD="sudo"
    else
        SUDO_CMD=""
    fi
fi

mkdir -p "$INSTALL_DIR" "$SHARE_DIR"

# ------------------------------------------------------------------------------
# 1. Package Manager Detection & System Dependencies (fzf, mpv, yt-dlp, chafa, etc.)
# ------------------------------------------------------------------------------
echo -e "${CYAN}[1/4] Checking and installing system dependencies (fzf, mpv, yt-dlp, chafa, ffmpeg, curl)...${NC}"

install_system_packages() {
    if [ "$IS_TERMUX" = true ] && command -v pkg &>/dev/null; then
        echo -e "  ${DIM}Detected Termux (Android) environment...${NC}"
        pkg update -y 2>/dev/null || true
        pkg install -y fzf mpv yt-dlp chafa curl git ffmpeg python termux-api 2>/dev/null || \
        pkg install -y fzf mpv chafa curl git ffmpeg python 2>/dev/null || true
    elif command -v pacman &>/dev/null; then
        echo -e "  ${DIM}Detected Arch Linux (pacman) package manager...${NC}"
        $SUDO_CMD pacman -Sy --noconfirm --needed fzf mpv yt-dlp chafa curl git ffmpeg python python-pip python-requests python-tqdm python-pillow 2>/dev/null || true
    elif command -v apt-get &>/dev/null; then
        echo -e "  ${DIM}Detected Debian/Ubuntu (APT) package manager...${NC}"
        $SUDO_CMD apt-get update -y -qq || true
        $SUDO_CMD apt-get install -y -qq fzf mpv yt-dlp chafa curl git ffmpeg python3 python3-pip python3-requests python3-tqdm python3-pil 2>/dev/null || \
        $SUDO_CMD apt-get install -y -qq fzf mpv chafa curl git ffmpeg python3 python3-pip 2>/dev/null || true
    elif command -v dnf &>/dev/null; then
        echo -e "  ${DIM}Detected Fedora/RHEL (DNF) package manager...${NC}"
        $SUDO_CMD dnf install -y -q fzf mpv yt-dlp chafa curl git ffmpeg python3 python3-pip python3-requests python3-tqdm python3-pillow 2>/dev/null || true
    elif command -v zypper &>/dev/null; then
        echo -e "  ${DIM}Detected openSUSE (zypper) package manager...${NC}"
        $SUDO_CMD zypper --non-interactive in fzf mpv yt-dlp chafa curl git ffmpeg python3 python3-pip python3-requests python3-tqdm 2>/dev/null || true
    elif command -v apk &>/dev/null; then
        echo -e "  ${DIM}Detected Alpine Linux (apk) package manager...${NC}"
        $SUDO_CMD apk add --no-cache fzf mpv yt-dlp chafa curl git ffmpeg python3 py3-pip py3-requests py3-tqdm 2>/dev/null || true
    elif command -v brew &>/dev/null; then
        echo -e "  ${DIM}Detected macOS (Homebrew) package manager...${NC}"
        brew install fzf mpv yt-dlp chafa curl git ffmpeg python3 2>/dev/null || true
    elif command -v xbps-install &>/dev/null; then
        echo -e "  ${DIM}Detected Void Linux (XBPS) package manager...${NC}"
        $SUDO_CMD xbps-install -Sy fzf mpv yt-dlp chafa curl git ffmpeg python3 python3-pip python3-requests python3-tqdm 2>/dev/null || true
    fi
}

install_system_packages || true

# ------------------------------------------------------------------------------
# 2. Standalone FZF Binary Auto-Downloader Fallback
# ------------------------------------------------------------------------------
if ! command -v fzf &>/dev/null && [ ! -f "$INSTALL_DIR/fzf" ]; then
    echo -e "${YELLOW}  Installing standalone FZF binary from GitHub releases...${NC}"
    ARCH="$(uname -m)"
    OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
    FZF_ARCH="amd64"

    case "$ARCH" in
        x86_64|amd64) FZF_ARCH="amd64" ;;
        aarch64|arm64|armv8*) FZF_ARCH="arm64" ;;
        armv7*) FZF_ARCH="armv7" ;;
        armv6*) FZF_ARCH="armv6" ;;
        i386|i686) FZF_ARCH="386" ;;
        *) FZF_ARCH="amd64" ;;
    esac

    FZF_VERSION="0.60.3"
    FZF_URL="https://github.com/junegunn/fzf/releases/download/v${FZF_VERSION}/fzf-${FZF_VERSION}-${OS}_${FZF_ARCH}.tar.gz"
    
    TMP_FZF_DIR="$(mktemp -d)"
    if curl -fsSL "$FZF_URL" -o "$TMP_FZF_DIR/fzf.tar.gz" 2>/dev/null; then
        tar -xzf "$TMP_FZF_DIR/fzf.tar.gz" -C "$TMP_FZF_DIR"
        if [ -f "$TMP_FZF_DIR/fzf" ]; then
            cp "$TMP_FZF_DIR/fzf" "$INSTALL_DIR/fzf"
            chmod +x "$INSTALL_DIR/fzf"
            echo -e "  ${GREEN}✓ Standalone FZF installed to $INSTALL_DIR/fzf${NC}"
        fi
    fi
    rm -rf "$TMP_FZF_DIR"
fi

# Check Python 3
PYTHON_BIN="python3"
if ! command -v python3 &>/dev/null; then
    if command -v python &>/dev/null; then
        PYTHON_BIN="python"
    else
        echo -e "${RED}Error: Python 3 is not installed.${NC} Please install Python 3 and rerun this script."
        exit 1
    fi
fi

# ------------------------------------------------------------------------------
# 3. Python Dependencies (requests, tqdm, yt-dlp, Pillow)
# ------------------------------------------------------------------------------
echo -e "${CYAN}[2/4] Checking and installing Python packages (requests, tqdm, yt-dlp, Pillow)...${NC}"
$PYTHON_BIN -m pip install --upgrade --quiet requests tqdm yt-dlp Pillow 2>/dev/null || \
$PYTHON_BIN -m pip install --user --upgrade --quiet requests tqdm yt-dlp Pillow 2>/dev/null || {
    echo -e "${YELLOW}Warning: Could not run pip automatically. Install manually: pip install requests tqdm yt-dlp Pillow${NC}"
}

# ------------------------------------------------------------------------------
# 4. Install ani-sync Package & Wrapper Launcher
# ------------------------------------------------------------------------------
echo -e "${CYAN}[3/4] Installing ani-sync package to ${INSTALL_DIR}...${NC}"

# Clean up any stale package files in SHARE_DIR before updating
rm -rf "$SHARE_DIR/ani_sync"

# Check if local source tree exists (running installer directly inside cloned repo)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
if [ -d "$SCRIPT_DIR/ani_sync" ]; then
    echo -e "  Installing from local repository source..."
    cp -r "$SCRIPT_DIR/ani_sync" "$SHARE_DIR/"
    if [ -d "$SCRIPT_DIR/assets" ]; then
        cp -r "$SCRIPT_DIR/assets" "$SHARE_DIR/" 2>/dev/null || true
    fi
else
    echo -e "  Downloading latest ani-sync package from GitHub..."
    TMP_DIR=$(mktemp -d)
    if curl -fsSL https://github.com/idrisharis12/ani-sync/archive/refs/heads/main.tar.gz | tar -xz -C "$TMP_DIR" 2>/dev/null; then
        if [ -d "$TMP_DIR/ani-sync-main/ani_sync" ]; then
            cp -r "$TMP_DIR/ani-sync-main/ani_sync" "$SHARE_DIR/"
            cp -r "$TMP_DIR/ani-sync-main/assets" "$SHARE_DIR/" 2>/dev/null || true
        fi
    fi
    rm -rf "$TMP_DIR"
fi

$PYTHON_BIN -m pip install --quiet --no-cache-dir --force-reinstall --no-deps "git+https://github.com/idrisharis12/ani-sync.git" 2>/dev/null || true

# Update active version manager shims (mise, pyenv, asdf) if installed
if command -v mise &>/dev/null; then
    mise reshim 2>/dev/null || true
fi

# Create launcher wrapper in INSTALL_DIR
cat << 'LAUNCHER' > "$INSTALL_DIR/ani-sync"
#!/usr/bin/env bash
export PATH="${HOME}/.local/bin:${PREFIX}/bin:/usr/local/bin:$PATH"
SHARE_DIR_USER="${HOME}/.local/share/ani-sync"
SHARE_DIR_SYS="/usr/local/share/ani-sync"
SHARE_DIR_TERMUX="${PREFIX}/share/ani-sync"

PY_EXE="python3"
if ! command -v python3 &>/dev/null; then
    PY_EXE="python"
fi

if [ -d "$SHARE_DIR_TERMUX/ani_sync" ]; then
    export PYTHONPATH="$SHARE_DIR_TERMUX:$PYTHONPATH"
    exec "$PY_EXE" -m ani_sync "$@"
elif [ -d "$SHARE_DIR_SYS/ani_sync" ]; then
    export PYTHONPATH="$SHARE_DIR_SYS:$PYTHONPATH"
    exec "$PY_EXE" -m ani_sync "$@"
elif [ -d "$SHARE_DIR_USER/ani_sync" ]; then
    export PYTHONPATH="$SHARE_DIR_USER:$PYTHONPATH"
    exec "$PY_EXE" -m ani_sync "$@"
else
    # Fallback to pip installed version
    exec "$PY_EXE" -m ani_sync "$@"
fi
LAUNCHER

chmod +x "$INSTALL_DIR/ani-sync"

# ------------------------------------------------------------------------------
# 5. Environment & PATH Verification
# ------------------------------------------------------------------------------
echo -e "${CYAN}[4/4] Finalizing setup & PATH configuration...${NC}"

if [ "$IS_TERMUX" = false ] && [ "$EUID" -ne 0 ]; then
    case ":$PATH:" in
        *":$INSTALL_DIR:"*) ;;
        *)
            for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
                if [ -f "$rc" ] && ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$rc"; then
                    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
                fi
            done
            export PATH="$INSTALL_DIR:$PATH"
            ;;
    esac
fi

# ------------------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------------------
echo -e "\n${GREEN}${BOLD}============================================================${NC}"
echo -e "${GREEN}${BOLD}           ✓ Successfully installed ani-sync!               ${NC}"
echo -e "${GREEN}${BOLD}============================================================${NC}"
echo -e "  ${CYAN}• FZF Search:${NC}      $([ "$(command -v fzf 2>/dev/null || [ -f "$INSTALL_DIR/fzf" ] && echo "yes")" ] && echo -e "${GREEN}Enabled (Interactive Fuzzy Finder)${NC}" || echo -e "${YELLOW}Numbered Menu Fallback${NC}")"
echo -e "  ${CYAN}• Media Player:${NC}    $([ "$(command -v mpv 2>/dev/null)" ] && echo -e "${GREEN}mpv detected${NC}" || echo -e "${YELLOW}mpv recommended (install via pacman/apt/pkg/brew)${NC}")"
echo -e "  ${CYAN}• Image Previews:${NC}  $([ "$(command -v chafa 2>/dev/null)" ] && echo -e "${GREEN}chafa enabled (High-Res Cover Art)${NC}" || echo -e "${YELLOW}ANSI Fallback${NC}")"
echo -e "  ${CYAN}• Turbo Engine:${NC}    $([ "$(command -v yt-dlp 2>/dev/null)" ] && echo -e "${GREEN}yt-dlp ready${NC}" || echo -e "${GREEN}yt-dlp installed via python${NC}")"
echo -e "\n${BOLD}Quick Start:${NC}"
echo -e "  ${CYAN}ani-sync${NC}                     Interactive anime search & launcher"
echo -e "  ${CYAN}ani-sync \"frieren\"${NC}           Search and stream specific anime"
echo -e "  ${CYAN}ani-sync -c${NC}                  Continue watching next episode"
echo -e "  ${CYAN}ani-sync history${NC}             Browse watch history with interactive FZF"
echo -e "  ${CYAN}ani-sync auth${NC}                Connect MyAnimeList / AniList / Kitsu"
echo -e "  ${CYAN}ani-sync doctor${NC}              Verify dependencies and system health"
echo ""
