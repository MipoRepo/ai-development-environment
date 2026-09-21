#!/bin/bash
# /doc-sync — Rebuild MkDocs site and check for doc consistency.

set -e

echo "[doc-sync] Building MkDocs site..."
.venv/Scripts/python -m mkdocs build --clean

echo "[doc-sync] Validating site structure..."
SITE_DIR="site"

if [ -d "$SITE_DIR" ]; then
    HTML_COUNT=$(find "$SITE_DIR" -name "*.html" | wc -l)
    echo "[doc-sync] Generated ${HTML_COUNT} HTML pages."
else
    echo "[doc-sync] WARNING: site/ directory not found."
fi

echo "[doc-sync] Checking for broken memory links..."

# Check MEMORY.md for dead links
if [ -f "MEMORY.md" ]; then
    grep -oP '\[.*?\]\(\.claude/memories/[^)]+\)' MEMORY.md | while read -r line; do
        LINK=$(echo "$line" | grep -oP '\(\K[^)]+')
        if [ ! -f "$LINK" ]; then
            echo "[doc-sync] BROKEN LINK: $LINK"
        fi
    done
fi

echo "[doc-sync] Done."
