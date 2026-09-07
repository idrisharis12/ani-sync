#!/usr/bin/env bash
# Automated Git Sync, SemVer Version Bumper & Tag Generator for ani-sync
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BUMP_TYPE="patch"
if [ $# -ge 1 ]; then
  if [ "$1" = "--minor" ] || [ "$1" = "-m" ] || [ "$1" = "minor" ]; then
    BUMP_TYPE="minor"
    shift
  elif [ "$1" = "--major" ] || [ "$1" = "major" ]; then
    BUMP_TYPE="major"
    shift
  elif [ "$1" = "--patch" ] || [ "$1" = "patch" ]; then
    BUMP_TYPE="patch"
    shift
  fi
fi

TS=$(date +"%Y-%m-%d %H:%M:%S")
if [ $# -eq 0 ]; then
  MSG="update: ${TS}"
else
  MSG="$*"
fi

# 1. Bump version across all project manifests
NEW_VER=$(python3 bump_version.py "$BUMP_TYPE" | grep -oE "v[0-9]+\.[0-9]+\.[0-9]+" | tail -n1 | tr -d 'v' || true)
if [ -z "$NEW_VER" ]; then
  NEW_VER=$(python3 -c "from ani_sync.config import VERSION; print(VERSION)")
fi

TAG_NAME="v${NEW_VER}"
COMMIT_MSG="${MSG} [${TAG_NAME}]"

# 2. Stage all changes
git add -A

if git diff-index --quiet HEAD --; then
  echo "ℹ️  No changes to commit."
else
  git commit -m "$COMMIT_MSG"
fi

# 3. Create Git Release Tag
if ! git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
  git tag -a "$TAG_NAME" -m "Release $TAG_NAME - $MSG"
  echo "🏷️ Created tag: $TAG_NAME"
fi

# 4. Push commits and tags to GitHub
git push origin main --tags
echo "✅ Successfully bumped version to ${TAG_NAME}, created release tag, and pushed changes to GitHub!"
