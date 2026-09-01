#!/usr/bin/env bash
# Automated Git Sync Script for ani-sync
set -euo pipefail

# Stage all changes
git add -A

TS=$(date +"%Y-%m-%d %H:%M:%S")

if [ $# -eq 0 ]; then
  MSG="Update ${TS}"
else
  MSG="$*"
fi

if git diff-index --quiet HEAD --; then
  echo "ℹ️  No changes to commit."
else
  git commit -m "$MSG"
fi

git push origin main
echo "✅  Successfully synchronized and pushed changes to GitHub (origin main)!"
