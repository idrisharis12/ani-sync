#!/usr/bin/env bash
# ==============================================================================
# ani-sync Automated Semantic Version Bumper & GitHub Sync Script
# ==============================================================================
# Usage:
#   ./version.sh patch "fix thumbnail bug"    # +0.0.1 (e.g., 2.11.1 -> 2.11.2)
#   ./version.sh minor "add new provider"     # +0.1.0 (e.g., 2.11.1 -> 2.12.0)
#   ./version.sh major "v3 architecture"      # +1.0.0 (e.g., 2.11.1 -> 3.0.0)
# ==============================================================================
set -euo pipefail

TYPE="patch"
MSG=""

if [ $# -ge 1 ]; then
    case "$1" in
        patch|+0.0.1|--patch)
            TYPE="patch"
            shift
            ;;
        minor|+0.1.0|--minor|major-update|--major-update)
            TYPE="minor"
            shift
            ;;
        major|+1.0.0|--major)
            TYPE="major"
            shift
            ;;
    esac
fi

if [ $# -ge 1 ]; then
    MSG="$*"
else
    MSG="update: apply ${TYPE} version release"
fi

echo "🚀 Bumping semantic version (+${TYPE})..."
python3 bump_version.py "$TYPE"

echo "📦 Staging and committing changes..."
git add -A

if git diff-index --quiet HEAD --; then
    echo "ℹ️  No changes to commit."
else
    git commit -m "${MSG}"
fi

echo "🚀 Auto-pushing commit to GitHub (origin main)..."
git push origin main

echo "✅ Successfully bumped version (+${TYPE}) and synchronized with GitHub!"
