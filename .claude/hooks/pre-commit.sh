#!/bin/bash
# Pre-commit hook: run full test suite before allowing a commit.
# Ensures the 1013-test suite passes before code is committed.

echo "[pre-commit] Running full test suite..."
.venv/Scripts/python -m pytest tests/ -v --tb=short

RESULT=$?
if [ $RESULT -ne 0 ]; then
    echo "[pre-commit] Tests FAILED — commit aborted." >&2
    exit 1
fi

echo "[pre-commit] All tests passed."
exit 0
