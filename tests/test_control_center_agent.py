"""Testit Control Center -moduulille (M20).

Testaa kolme agenttia:
- ControlCenterAgent (keskitetty ohjauspaneeli)
- DashboardAgent (visuaaliset mittarit ja tilasehdotus)
- CLIOrchestrator (CLI-komennon jäsentäminen ja reitintäminen)
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agents.control_center_agent import (
    ControlCenterAgent,
    ControlCenterInput,
    ControlCenterOutput,
    DashboardAgent,
    DashboardInput,
    DashboardOutput,
    CLIOrchestrator,
    CLIOrchestratorInput,
    CLIOrchestratorOutput,
    CONTROL_CENTER_ACTIONS,
    DASHBOARD_ACTIONS,
    CLI_ORCHESTRATOR_ACTIONS,
    SYSTEM_COMPONENTS,
    COMMAND_ROUTES,
    AGENT_STATES,
    WORKFLOW_STATES,
    METRIC_CONNECTIONS,
    ALERT_LEVELS,
    CLI_HELP_TEXT,
)
from agents.base import BaseAgent


# =============================================================================
# ControlCenterAgent
# =============================================================================

class TestControlCenterAgent:
    """Testit ControlCenterAgentille."""

    @pytest.fixture
    def agent(self):
        return ControlCenterAgent()

    def test_agent_type(self, agent):
        """Vahvistaa agentin tyyppi."""
        assert agent.agent_type == "control_center"

    def test_input_output_schemat(self, agent):
        """Vahvistaa syöte- ja tulosteasemats."""
        assert agent.input_schema == ControlCenterInput
        assert agent.output_schema == ControlCenterOutput

    def test_actions_dict_exists(self):
        """Vahvistaa että CONTROL_CENTER_ACTIONS sisältää oikeat toiminnot."""
        assert "status" in CONTROL_CENTER_ACTIONS
        assert "list_agents" in CONTROL_CENTER_ACTIONS
        assert "list_workflows" in CONTROL_CENTER_ACTIONS
        assert "execute" in CONTROL_CENTER_ACTIONS
        assert "monitor" in CONTROL_CENTER_ACTIONS
        assert "health" in CONTROL_CENTER_ACTIONS

    def test_system_components_defined(self):
        """Vahvistaa että järjestelmäkomponentit on määritelty."""
        assert len(SYSTEM_COMPONENTS) >= 5
        comp_names = [c["name"] for c in SYSTEM_COMPONENTS]
        assert "agent_system" in comp_names
        assert "cli" in comp_names
        assert "model_gateway" in comp_names

    def test_status_returns_system_status(self, agent):
        """Testaa että status-toiminto palauttaa järjestelmän tilan."""
        result = agent.run("Näytä tila", action="status")

        assert result.success is True
        assert result.system_status == "healthy"
        assert len(result.components) > 0
        assert "cpu_percent" in result.metrics

    def test_status_metrics_contains_system(self, agent):
        """Testaa että metrics sisältää järjestelmätiedot."""
        result = agent.run("Näytä tila", action="status")

        assert result.metrics.get("cpu_percent") is not None

    def test_list_agents(self, agent):
        """Testaa agenttien listaus."""
        result = agent.run("Listaa agentit", action="list_agents")

        assert result.success is True
        assert len(result.agents) > 0
        assert "name" in result.agents[0]
        assert "type" in result.agents[0]

    def test_list_workflows(self, agent):
        """TestaA työnkulkujen listaus."""
        result = agent.run("Listaa työnkulku", action="list_workflows")

        assert result.success is True
        assert len(result.workflows) >= 4
        workflow_names = [w["name"] for w in result.workflows]
        assert "base-workflow" in workflow_names
        assert "bugfix" in workflow_names

    def test_execute_without_agent_name(self, agent):
        """TestaA suoritus ilman agentin nimeä."""
        result = agent.run("Suorita", action="execute")

        assert result.success is False
        assert "nimi" in result.message.lower() or "pakollinen" in result.message.lower()

    def test_execute_with_known_agent(self, agent):
        """TestaA tunnetun agentin suorittaminen."""
        result = agent.run("Suorita agentti", action="execute", agent_name="ControlCenterAgent")

        assert result.success is True

    def test_execute_with_unknown_agent(self, agent):
        """TestaA tuntemattoman agentin suorittaminen."""
        result = agent.run("Suorita", action="execute", agent_name="tuntematon_moduuli")

        assert result.success is False

    def test_execute_with_short_name(self, agent):
        """TestaA lyhyen nimen (ilman 'Agent'-päätettä) käyttö."""
        result = agent.run("Suorita", action="execute", agent_name="Dashboard")

        assert result.success is True

    def test_monitor(self, agent):
        """TestaaS seurinta."""
        result = agent.run("Seuraa", action="monitor", monitor_interval=3)

        assert result.success is True
        assert len(result.monitor_data) >= 1

    def test_health_check(self, agent):
        """TestaaS terveys tarkistus."""
        result = agent.run("Terveys tarkistus", action="health")

        assert result.success is True
        assert "overall_status" in result.health_report
        assert "checks" in result.health_report

    def test_health_check_all_passed(self, agent):
        """TestaA että terveys tarkistus palauttaa 'healthy' kun kaikki ok."""
        result = agent.run("Terveys", action="health")

        assert result.health_report["overall_status"] == "healthy"

    def test_unknown_action(self, agent):
        """TestaA tuntemattoman toiminnon käsittely."""
        result = agent.run("Testaa", action="tuntematon")

        assert result.success is False
        assert "tuntematon" in result.message.lower()

    def test_command_routes_exists(self):
        """Vahvistaa että COMMAND_ROUTES on määritelty."""
        assert "aide" in COMMAND_ROUTES
        subcommands = COMMAND_ROUTES["aide"]["subcommands"]
        assert "init" in subcommands
        assert "run" in subcommands
        assert "status" in subcommands
        assert "local" in subcommands

    def test_cli_help_text_exists(self):
        """Vahvistaa että CLI_HELP_TEXT on määritelty."""
        assert "main" in CLI_HELP_TEXT
        assert "aide" in CLI_HELP_TEXT["main"].lower()

    def test_agent_states_defined(self):
        """Vahvistaa että AGENT_STATES on määritelty."""
        assert "idle" in AGENT_STATES
        assert "running" in AGENT_STATES
        assert "completed" in AGENT_STATES

    def test_workflow_states_defined(self):
        """Vahvistaa että WORKFLOW_STATES on määritelty."""
        assert "pending" in WORKFLOW_STATES
        assert "running" in WORKFLOW_STATES
        assert "completed" in WORKFLOW_STATES


# =============================================================================
# DashboardAgent
# =============================================================================

class TestDashboardAgent:
    """Testit DashboardAgentille."""

    @pytest.fixture
    def agent(self):
        return DashboardAgent()

    def test_agent_type(self, agent):
        """Vahvistaa agentin tyyppi."""
        assert agent.agent_type == "dashboard"

    def test_input_output_schemat(self, agent):
        """Vahvistaa syöte- ja tulosteasemats."""
        assert agent.input_schema == DashboardInput
        assert agent.output_schema == DashboardOutput

    def test_actions_dict_exists(self):
        """Vahvistaa että DASHBOARD_ACTIONS sisältää oikeat tokinnot."""
        assert "metrics" in DASHBOARD_ACTIONS
        assert "status" in DASHBOARD_ACTIONS
        assert "alerts" in DASHBOARD_ACTIONS
        assert "performance" in DASHBOARD_ACTIONS

    def test_metrics_returns_system_data(self, agent):
        """TestaaS että metrics-toiminto palauttaa järjestelmätiedot."""
        result = agent.run("Näytä mittarit", action="metrics")

        assert result.success is True
        assert "system" in result.metrics
        sys_metrics = result.metrics["system"]
        assert "cpu_percent" in sys_metrics
        assert "memory_used_mb" in sys_metrics
        assert "agent_count" in sys_metrics

    def test_metrics_with_quality(self, agent):
        """TestaaS että metrics sisältää myös laadun tiedot."""
        result = agent.run("Näytä mittarit", action="metrics", include_quality=True)

        assert result.success is True
        assert "quality" in result.metrics
        assert "test_coverage" in result.metrics["quality"]

    def test_metrics_without_quality(self, agent):
        """TestaaS että laadun tiedot voidaan sulkea pois."""
        result = agent.run("Näytä mittarit", action="metrics", include_quality=False)

        assert result.success is True
        assert "quality" not in result.metrics

    def test_status_returns_components(self, agent):
        """TestaaS että status-toiminto palauttaa komponentit."""
        result = agent.run("Näytä status", action="status")

        assert result.success is True
        assert len(result.component_status) > 0
        assert result.component_status[0]["status"] == "ok"

    def test_status_filtered_by_component(self, agent):
        """TestaA komponenttien suodatus."""
        result = agent.run("Näytä status", action="status", component_filter="agent")

        assert result.success is True
        for comp in result.component_status:
            assert "agent" in comp["name"].lower()

    def test_alerts_returns_list(self, agent):
        """TestaaS että hälytykset palautetaan listana."""
        result = agent.run("Näytä hälytykset", action="alerts")

        assert result.success is True
        assert len(result.alerts) >= 1
        assert result.alerts[0]["level"] in ALERT_LEVELS

    def test_alerts_filtered(self, agent):
        """TestaA hälyysten suodatus."""
        result = agent.run("Näytä hälytykset", action="alerts", component_filter="kaikki")

        assert result.success is True

    def test_performance(self, agent):
        """TestaaS suorituskyvyn tiedot."""
        result = agent.run("Näytä suorituskyky", action="performance")

        assert result.success is True
        assert "performance_data" in result.result or result.success
        perf = result.performance_data
        assert "window" in perf
        assert "avg_response_ms" in perf

    def test_performance_with_different_windows(self, agent):
        """TestaSsuorituskyvyn eri aikajaksoissa."""
        for window in ["1h", "24h", "7d", "30d"]:
            result = agent.run("Suoritus", action="performance", time_window=window)
            assert result.success is True
            assert result.performance_data["window"] == window

    def test_unknown_action(self, agent):
        """TestaaS tuntemattoman toiminnon käsittely."""
        result = agent.run("Testaa", action="tuntematon")

        assert result.success is False

    def test_metric_connections_defined(self):
        """Vahvistaa että METRIC_CONNECTIONS on määritelty."""
        assert "cpu" in METRIC_CONNECTIONS
        assert "memory" in METRIC_CONNECTIONS
        assert "test_coverage" in METRIC_CONNECTIONS


# =============================================================================
# CLIOrchestrator
# =============================================================================

class TestCLIOrchestrator:
    """Testit CLIOrchestratorille."""

    @pytest.fixture
    def agent(self):
        return CLIOrchestrator()

    def test_agent_type(self, agent):
        """Vahittaa agentin tyyppi."""
        assert agent.agent_type == "cli_orchestrator"

    def test_input_output_schemat(self, agent):
        """Vahvistaa syöte- ja tulosteasemats."""
        assert agent.input_schema == CLIOrchestratorInput
        assert agent.output_schema == CLIOrchestratorOutput

    def test_actions_dict_exists(self):
        """Vahvistaa että CLI_ORCHESTRATOR_ACTIONS sisältää oikeat tokinnot."""
        assert "parse" in CLI_ORCHESTRATOR_ACTIONS
        assert "route" in CLI_ORCHESTRATOR_ACTIONS
        assert "execute" in CLI_ORCHESTRATOR_ACTIONS
        assert "complete" in CLI_ORCHESTRATOR_ACTIONS
        assert "history" in CLI_ORCHESTRATOR_ACTIONS

    def test_parse_simple_command(self, agent):
        """TestaaS yksinkertaisen per-komennon jäsentäminen."""
        result = agent.run("Jäseä komento", command="aide status", action="parse")

        assert result.success is True
        assert result.parsed_command["base_command"] == "aide"
        assert result.parsed_command["subcommand"] == "status"

    def test_parse_command_with_args(self, agent):
        """TestaaS komennon jäsentäminen argumenteilla."""
        result = agent.run("Jäseä", command='aide run "Luo projekti"', action="parse")

        assert result.success is True
        assert result.parsed_command["subcommand"] == "run"
        assert "Luo projekti" in result.parsed_command.get("task_description", "")

    def test_parse_command_with_init(self, agent):
        """TestaaS 'init'-komennon jäsentäminen."""
        result = agent.run("Jäseä", command="aide init", action="parse")

        assert result.success is True
        assert result.parsed_command["subcommand"] == "init"

    def test_route_to_correct_agent(self, agent):
        """TestaaS että komennot reitittyvät oikeisiin agentteihin."""
        result = agent.run("Reititä", command="aide status", action="route")

        assert result.success is True
        assert result.routed_agent == "ControlCenterAgent"
        assert "tila" in result.routed_task.lower() or "status" in result.routed_task.lower()

    def test_route_run_command(self, agent):
        """TestaaS 'run'-komennon reittäminen."""
        result = agent.run("Reititä", command='aide run "tehtävä"', action="route")

        assert result.success is True
        assert result.routed_agent == "WorkflowOrchestratorAgent"

    def test_route_local_command(self, agent):
        """TestaaS 'local'-komennon reittäminen."""
        result = agent.run("Reititä", command="aide local list", action="route")

        assert result.success is True
        assert result.routed_agent == "LocalModelAgent"

    def test_route_integration_command(self, agent):
        """TestaaS 'integration'-komennon reittäminen."""
        result = agent.run("Reititä", command="aide integration list", action="route")

        assert result.success is True
        assert result.routed_agent == "MCPIntegrationAgent"

    def test_execute_command(self, agent):
        """TestaaS komennon suoritus."""
        result = agent.run("Suorita", command="aide status", action="execute")

        assert result.success is True
        assert len(result.execution_result) > 0

    def test_complete_suggestions(self, agent):
        """TestaaS Bash-täydennys ehdottelut."""
        result = agent.run("Täydennä", command="aide s", action="complete", raw_input="aide s")

        assert result.success is True
        assert len(result.completion_suggestions) > 0
        suggestions = result.completion_suggestions
        for s in suggestions:
            assert s.startswith("aide ")

    def test_complete_all_commands(self, agent):
        """TestaaS että täydennys ottaa kaikki komennot."""
        result = agent.run("Täydennä", command="aide ", action="complete", raw_input="aide ")

        assert result.success is True
        assert len(result.completion_suggestions) >= 5

    def test_history(self, agent):
        """TestaaS komennohistorian hakeminen."""
        result = agent.run("Historia", command="aide history", action="history", session_id="test_session")

        assert result.success is True
        assert len(result.command_history) >= 1

    def test_unknown_action(self, agent):
        """TestaaS tuntemattoman toiminnon käsittely."""
        result = agent.run("Testaa", action="tuntematon")

        assert result.success is False


# =============================================================================
# Integraatiot testit
# =============================================================================

class TestM20Integration:
    """Integraatiot testit M20 Control Center -moduulille."""

    def test_all_agents_inherit_base(self):
        """Vahvistaa että kaikki agentit perivät BaseAgentin."""
        assert issubclass(ControlCenterAgent, BaseAgent)
        assert issubclass(DashboardAgent, BaseAgent)
        assert issubclass(CLIOrchestrator, BaseAgent)

    def test_all_agents_have_inputs(self):
        """Vahvistaa että kaikilla agenteilla on oikeat syöteklassit."""
        assert ControlCenterAgent.input_schema == ControlCenterInput
        assert DashboardAgent.input_schema == DashboardInput
        assert CLIOrchestrator.input_schema == CLIOrchestratorInput

    def test_all_agents_have_outputs(self):
        """Vahistaa että kaikilla agenteilla on oikeat tulosteklassit."""
        assert ControlCenterAgent.output_schema == ControlCenterOutput
        assert DashboardAgent.output_schema == DashboardOutput
        assert CLIOrchestrator.output_schema == CLIOrchestratorOutput

    def test_control_center_routes_to_agents(self):
        """TestaaS että ControlCenter osaa listata reititellyt agentit."""
        cc_agent = ControlCenterAgent()
        result = cc_agent.run("Listaa agentit", action="list_agents")

        assert result.success
        assert len(result.agents) > 10
        agent_names = [a["name"] for a in result.agents]
        assert "ControlCenterAgent" in agent_names
        assert "DashboardAgent" in agent_names
        assert len(result.agents) > 10

    def test_cli_orchestrator_routes_to_dashboard(self):
        """TestaaS että CLI reitittää dashboard-komennon oikein."""
        cli_agent = CLIOrchestrator()
        result = cli_agent.run("Reititä", command="aide dashboard metrics", action="route")

        assert result.success
        assert "dashboard" in result.routed_agent.lower() or result.routed_agent == "CLIOrchestrator"

    def test_dashboard_shows_all_quality_metrics(self):
        """TestaaS että dashboard näyttää kaikki laadunmittarit."""
        dashboard = DashboardAgent()
        result = dashboard.run("Näytä kaikki", action="metrics", include_system=True, include_quality=True)

        assert result.success
        assert "system" in result.metrics
        assert "quality" in result.metrics
        quality = result.metrics["quality"]
        assert "total_tests" in quality
        assert "test_coverage" in quality

    def test_workflow_list_from_control_center(self):
        """TestaaS että ControlCenter listaa saatavilla olevat työnkulku."""
        cc_agent = ControlCenterAgent()
        result = cc_agent.run("Listaa työnkulku", action="list_workflows")

        assert result.success
        workflow_names = [w["name"] for w in result.workflows]
        assert len(workflow_names) >= 4

    def test_system_health_complete(self):
        """TestaaS että täydellinen terveys tarkistus sisältää kaiken."""
        cc_agent = ControlCenterAgent()
        result = cc_agent.run("Terveys", action="health")

        assert result.success
        report = result.health_report
        assert report["overall_status"] == "healthy"
        assert "agents_loaded" in report["checks"]
        assert "workflows_available" in report["checks"]
        assert "components_ok" in report["checks"]

    def test_cli_command_routing_chain(self):
        """TestaS kokonaista CLI-komennon ketjua: parse → route → execute."""
        cli_agent = CLIOrchestrator()

        # 1. Parse
        parse_result = cli_agent.run("Jäseä", command="aide init", action="parse")
        assert parse_result.success
        assert parse_result.parsed_command["subcommand"] == "init"

        # 2. Route
        route_result = cli_agent.run("Reititä", command="aide init", action="route")
        assert route_result.success
        assert route_result.routed_agent == "ProjectManagerAgent"

        # 3. Execute
        exec_result = cli_agent.run("Suorita", command="aide init", action="execute")
        assert exec_result.success
        assert exec_result.execution_result["status"] == "simulated"
