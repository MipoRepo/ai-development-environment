#!/bin/bash
# /run-tests — Run AIDE test suite with flexible filtering.
#
# Usage:
#   /run-tests           → all tests
#   /run-tests M13        → M13-specific test files
#   /run-tests knowledge  → test files matching pattern

set -e

TARGET="${1:-all}"

case "$TARGET" in
    all)
        .venv/Scripts/python -m pytest tests/ -v --tb=short
        ;;
    M13)
        .venv/Scripts/python -m pytest \
            tests/test_knowledge_agent.py \
            tests/test_memory_agent.py \
            tests/test_context_compiler_agent.py -v --tb=short
        ;;
    M14)
        .venv/Scripts/python -m pytest tests/test_maintenance_agent.py -v --tb=short
        ;;
    *)
        # Match any test file containing the argument
        .venv/Scripts/python -m pytest tests/ -v --tb=short -k "$TARGET"
        ;;
esac
