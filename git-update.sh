#!/usr/bin/env bash
set -euo pipefail

# Generate a timestamp‑based branch name
TS=$(date +"%Y%m%d-%H%M%S")
BRANCH="update-${TS}"

# Create and switch to the new branch
git checkout -b "$BRANCH"

# Stage all changes (adjust if you only want specific files)
git add -A

# Use supplied commit message or a default one
if [ $# -eq 0 ]; then
  MSG="Update ${TS}"
else
  MSG="$*"
fi

git commit -m "$MSG"

# Push the new branch to origin
git push -u origin "$BRANCH"

echo "✅  Created and pushed branch: $BRANCH"
