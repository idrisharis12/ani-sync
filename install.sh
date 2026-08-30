#!/usr/bin/env bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${CYAN}${BOLD}"
echo "  ============================================"
echo "          ani-sync Installation Script         "
echo "  ============================================"
echo -e "${NC}"

# Check for Python 3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Error: python3 is not installed.${NC} Please install Python 3 and rerun this script."
    exit 1
fi

# Detect installation target directory
if [ "$EUID" -eq 0 ]; then
    INSTALL_DIR="/usr/local/bin"
    SHARE_DIR="/usr/local/share/ani-sync"
else
    INSTALL_DIR="${HOME}/.local/bin"
    SHARE_DIR="${HOME}/.local/share/ani-sync"
    mkdir -p "$INSTALL_DIR"
fi

mkdir -p "$SHARE_DIR"

echo -e "${CYAN}[1/3] Checking and installing Python dependencies...${NC}"
python3 -m pip install --upgrade --quiet requests tqdm ani-cli || {
    echo -e "${YELLOW}Warning: pip install with user flag fallback...${NC}"
    python3 -m pip install --user --quiet requests tqdm ani-cli || true
}

echo -e "${CYAN}[2/3] Installing ani-sync to ${INSTALL_DIR}...${NC}"

# If running directly from git cloned repo
if [ -f "ani_sync.py" ]; then
    cp ani_sync.py "$SHARE_DIR/ani_sync.py"
    if [ -d "assets" ]; then
        cp -r assets "$SHARE_DIR/"
    fi
else
    # Downloading directly from raw GitHub if run via curl / standalone
    echo -e "Downloading latest ani-sync script from GitHub..."
    curl -fsSL https://raw.githubusercontent.com/idrisharis12/ani-sync/main/ani_sync.py -o "$SHARE_DIR/ani_sync.py"
fi

# Create launcher wrapper in INSTALL_DIR
cat << 'LAUNCHER' > "$INSTALL_DIR/ani-sync"
#!/usr/bin/env bash
SHARE_DIR_USER="${HOME}/.local/share/ani-sync"
SHARE_DIR_SYS="/usr/local/share/ani-sync"

if [ -f "$SHARE_DIR_SYS/ani_sync.py" ]; then
    exec python3 "$SHARE_DIR_SYS/ani_sync.py" "$@"
elif [ -f "$SHARE_DIR_USER/ani_sync.py" ]; then
    exec python3 "$SHARE_DIR_USER/ani_sync.py" "$@"
else
    echo "Error: ani_sync.py not found." >&2
    exit 1
fi
LAUNCHER

chmod +x "$SHARE_DIR/ani_sync.py"
chmod +x "$INSTALL_DIR/ani-sync"

echo -e "${CYAN}[3/3] Verifying installation...${NC}"

# Check if INSTALL_DIR is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}Note: ${INSTALL_DIR} is not in your current PATH.${NC}"
    echo "Add the following line to your ~/.bashrc or ~/.zshrc:"
    echo "    export PATH=\"\$PATH:${INSTALL_DIR}\""
fi

echo -e "\n${GREEN}${BOLD}✓ Successfully installed ani-sync!${NC}"
echo -e "Run ${CYAN}ani-sync watch <url>${NC} to start."
