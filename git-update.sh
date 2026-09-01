#!/usr/bin/env bash
# Automated Git Sync & Version Bumper Script for ani-sync
set -euo pipefail

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

# Automatically bump version (+0.0.1 for patch or +0.1.0 for minor/major update)
python3 bump_version.py "$BUMP_TYPE"

# Stage all changes
git add -A

if git diff-index --quiet HEAD --; then
  echo "ℹ️  No changes to commit."
else
  git commit -m "$MSG"
fi

git push origin main
echo "✅  Successfully bumped version (+${BUMP_TYPE}), synchronized and pushed changes to GitHub (origin main)!"
