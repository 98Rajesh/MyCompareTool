#!/usr/bin/env bash
# Helper: create 'pro' branch from main and push (run once)

set -e

git checkout main
git pull
git checkout -b pro
git push -u origin pro

echo "Created and pushed 'pro' branch. Configure CI to build Pro artifacts from this branch."
