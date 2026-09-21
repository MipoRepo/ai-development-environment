#!/bin/bash
# On-save hook: syntax check + test runner for changed Python files
# Triggered when a file is saved in the agents/ or schemas/ directories.

FILE="$1"

# Skip non-Python files
if [[ ! "$FILE" == *.py ]]; then
    exit 0
fi

echo "[on-save] Syntax check: $FILE"

# 1. AST syntax check
if ! .venv/Scripts/python -c "import ast; ast.parse(open('$FILE').read())" 2>&1; then
    echo "[on-save] SYNTAX ERROR in $FILE" >&2
    exit 1
fi
echo "[on-save] Syntax OK"

# 2. Run relevant tests (fast feedback for changed agent module)
MODULE=$(basename "$FILE" .py)
if [[ -f "tests/test_${MODULE}.py" ]]; then
    echo "[on-save] Running tests/test_${MODULE}.py"
    .venv/Scripts/python -m pytest "tests/test_${MODULE}.py" -v --tb=short
else
    echo "[on-save] No dedicated test file for $MODULE, skipping."
fi
