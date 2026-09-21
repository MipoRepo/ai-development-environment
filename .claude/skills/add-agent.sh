#!/bin/bash
# /add-agent — Scaffold a new AIDE agent module.
#
# Usage: /add-agent <ModuleNumber> "<ModuleName>"
#
# Example: /add-agent M21 "Notification & Alerting"
#
# Creates:
#   agents/<module_name>_agent.py  (stub agent classes)
#   tests/test_<module_name>_agent.py (test stubs)

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: /add-agent <ModuleNumber> \"<ModuleName>\""
    echo "Example: /add-agent M21 \"Notification & Alerting\""
    exit 1
fi

MODULE_NUM="$1"
MODULE_NAME="$2"
MODULE_FILE=$(echo "$MODULE_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | sed 's/[^a-z0-9_]//g')

echo "[add-agent] Creating agent module $MODULE_NUM: $MODULE_NAME"
echo "[add-agent]   File: agents/${MODULE_FILE}_agent.py"
echo "[add-agent]   Tests: tests/test_${MODULE_FILE}_agent.py"

# Check if file already exists
if [ -f "agents/${MODULE_FILE}_agent.py" ]; then
    echo "[add-agent] ERROR: agents/${MODULE_FILE}_agent.py already exists."
    exit 1
fi

# Create agent file
cat > "agents/${MODULE_FILE}_agent.py" << EOF
"""
AIDE-module agents for ${MODULE_NAME} (${MODULE_NUM}).
"""
from __future__ import annotations

from agents.base import BaseAgent, AgentInput, AgentOutput


class ExampleAgentInput(AgentInput):
    """Syöte esimerkkiagentille."""
    action: str = "run"


class ExampleAgentOutput(AgentOutput):
    """Tuloste esimerkkiagenteille."""
    result: dict | None = None


class ExampleAgent(BaseAgent):
    """Esimerkkiluokka — korvaa todellisilla agenteillä."""
    agent_type: str = "example"

    def _run(self, validated_input: ExampleAgentInput) -> ExampleAgentOutput:
        return ExampleAgentOutput(
            success=True,
            result={"action": validated_input.action},
            message="Example agent suoritettu.",
            agent_type=self.agent_type,
        )


__all__ = ["ExampleAgent", "ExampleAgentInput", "ExampleAgentOutput"]
EOF

# Create test file
cat > "tests/test_${MODULE_FILE}_agent.py" << EOF
"""Tests for ${MODULE_NUM} ${MODULE_NAME} agents."""
import pytest
from agents.${MODULE_FILE}_agent import ExampleAgent, ExampleAgentInput


class TestExampleAgent:
    """Testataan ExampleAgent."""

    def test_run_success(self):
        agent = ExampleAgent()
        result = agent.run(
            "Testaa",
            input_data=ExampleAgentInput(action="test"),
        )
        assert result.success is True
        assert result.agent_type == "example"
EOF

echo "[add-agent] Created. Muista lisätä viennit agents/__init__.py:iin."
