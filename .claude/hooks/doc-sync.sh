#!/bin/bash
# Documentation sync hook: runs after commits to regenerate MkDocs site
# if any .py or .md source files changed.

CHANGED_FILES=$(git diff --name-only HEAD@{1} HEAD 2>/dev/null || echo "")

# Check if doc-relevant files changed
if echo "$CHANGED_FILES" | grep -qE '\.(py|md)$|site/'; then
    echo "[doc-sync] Documentation-relevant files changed, syncing site..."
    .venv/Scripts/python -m mkdocs build --clean
    echo "[doc-sync] Site rebuilt."
else
    echo "[doc-sync] No doc-relevant changes, skipping."
fi
