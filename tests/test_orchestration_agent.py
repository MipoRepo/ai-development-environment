"""
Testit OrchestrationAgenteille (M9).
"""

import pytest

from agents.orchestration_agent import (
    WorkflowOrchestratorAgent,
    WorkflowOrchestratorInput,
    WorkflowOrchestratorOutput,
    MultiAgentCoordinator,
    CoordinationInput,
    CoordinationOutput,
    _PhaseHandler,
)


@pytest.fixture
def orchestrator():
    return WorkflowOrchestratorAgent()


@pytest.fixture
def coordinator():
    return MultiAgentCoordinator()


class TestWorkflowOrchestratorAgent:
    """Testit WorkflowOrchestratorAgentille."""

    def test_agent_type(self, orchestrator):
        assert orchestrator.agent_type == "workflow_orchestrator"

    def test_input_schema(self, orchestrator):
        assert orchestrator.input_schema == WorkflowOrchestratorInput

    def test_output_schema(self, orchestrator):
        assert orchestrator.output_schema == WorkflowOrchestratorOutput

    def test_run_executes_default_phases(self, orchestrator):
        """run() suorittaa oletusvaiheet."""
        result = orchestrator.run(
            task="Aloita projekti",
        )
        assert isinstance(result, WorkflowOrchestratorOutput)
        assert result.success is True
        assert result.phases_executed >= 3
        assert len(result.phase_results) >= 3

    def test_run_with_custom_phases(self, orchestrator):
        """run() käyttää määriteltyjä vaiheita."""
        result = orchestrator.run(
            task="Aloita projekti",
            phases=["analyze", "plan", "implement"],
        )
        assert result.phases_executed == 3
        assert result.phase_sequence == ["analyze", "plan", "implement"]

    def test_run_passes_context(self, orchestrator):
        """run() ottaa vastaan ja päivittää kontekstin."""
        result = orchestrator.run(
            task="Aloita projekti",
            context={"project_name": "TestProject", "language": "python"},
        )
        assert result.context.get("project_name") == "TestProject"

    def test_run_returns_phase_results(self, orchestrator):
        """run() palauttaa vaiheiden tulokset."""
        result = orchestrator.run(
            task="Aloita projekti",
            phases=["analyze", "plan"],
        )
        assert len(result.phase_results) == 2
        assert all("phase" in pr for pr in result.phase_results)

    def test_run_calculates_duration(self, orchestrator):
        """run() laskee kokonaisajan."""
        result = orchestrator.run(
            task="Aloita projekti",
        )
        assert result.total_duration > 0

    def test_run_returns_final_agent(self, orchestrator):
        """run() palauttaa viimeisen agentin."""
        result = orchestrator.run(
            task="Aloita projekti",
            phases=["analyze", "plan", "implement", "document"],
        )
        assert result.final_agent != ""

    def test_run_with_agents_param(self, orchestrator):
        """run() hyväksyy mukautetut agentit."""
        result = orchestrator.run(
            task="Aloita projekti",
            phases=["analyze"],
            agents=["CustomAgent"],
        )
        assert result.phases_executed == 1
        assert result.phase_results[0]["agents"] == ["CustomAgent"]

    def test_run_max_phases_limits(self, orchestrator):
        """max_phases rajoittaa vaiheiden määrää."""
        result = orchestrator.run(
            task="Aloita projekti",
            max_phases=2,
        )
        assert result.phases_executed == 2

    def test_run_invalid_phases_filtered(self, orchestrator):
        """Virheelliset vaiheet suodatetaan."""
        result = orchestrator.run(
            task="Aloita projekti",
            phases=["unknown_phase", "analyze", "invalid"],
        )
        assert result.phases_executed == 1
        assert result.phase_sequence == ["analyze"]

    def test_run_stop_on_error(self, orchestrator):
        """stop_on_error pysäyttää virheen sattuessa."""
        result = orchestrator.run(
            task="Aloita projekti",
            phases=["analyze", "unknown_phase", "plan"],
            stop_on_error=True,
        )
        assert result.success is True  # unknown phases filtered, not error

    def test_run_phase_handler_returns_data(self):
        """_PhaseHandler palauttaa oikean datan vaiheelta."""
        result = _PhaseHandler.handle("analyze", {})
        assert result["phase"] == "analyze"
        assert result["analyzed"] is True

    def test_run_phase_handler_unknown_phase(self):
        """_PhaseHandler käsittelee tuntemattomat vaiheet."""
        result = _PhaseHandler.handle("custom", {})
        assert result["phase"] == "custom"
        assert result["processed"] is True

    def test_run_serializes(self, orchestrator):
        """Tulos voidaan serialisoida."""
        result = orchestrator.run(
            task="Aloita projekti",
            phases=["analyze", "plan"],
        )
        d = result.to_dict()
        assert d["agent_type"] == "workflow_orchestrator"
        assert "phase_results" in d
        assert "phase_sequence" in d

    def test_run_context_updates_through_phases(self, orchestrator):
        """Konteksti päivittyy jokaisen vaian jälkeen."""
        result = orchestrator.run(
            task="Aloita",
            phases=["analyze", "plan", "implement"],
        )
        # analyze-vaihe päivittää kontekstin "technologies"-avainnolla
        assert "technologies" in result.context


class TestMultiAgentCoordinator:
    """Testit MultiAgentCoordinatorille."""

    def test_agent_type(self, coordinator):
        assert coordinator.agent_type == "multi_agent_coordinator"

    def test_input_schema(self, coordinator):
        assert coordinator.input_schema == CoordinationInput

    def test_output_schema(self, coordinator):
        assert coordinator.output_schema == CoordinationOutput

    def test_run_returns_execution_order(self, coordinator):
        """run() palauttaa suoritusjärjestyksen."""
        result = coordinator.run(
            task="Koordinoi",
            agent_descriptions={"A": "Agent A", "B": "Agent B"},
        )
        assert isinstance(result, CoordinationOutput)
        assert len(result.execution_order) >= 2

    def test_run_executes_all_agents(self, coordinator):
        """run() suorittaa kaikki agentit."""
        result = coordinator.run(
            task="Koordinoi",
            agent_descriptions={
                "Analyzer": "Analysoi projektin",
                "Planner": "Suunnittelee",
                "Builder": "Rakentaa",
            },
        )
        assert result.success is True
        assert len(result.results) == 3

    def test_run_with_dependencies(self, coordinator):
        """run() kääsittää riippuvuudet oikeaan järjestykseen."""
        result = coordinator.run(
            task="Koordinoi riippuvuuksia",
            agent_descriptions={"A": "Agent A", "B": "Agent B", "C": "Agent C"},
            dependencies={"C": ["A", "B"], "B": ["A"]},
        )
        assert "A" in result.execution_order
        assert result.execution_order.index("A") < result.execution_order.index("C")
        assert result.execution_order.index("A") < result.execution_order.index("B")

    def test_run_topological_sort_acyclic(self, coordinator):
        """Topologinen järjestys onnistuu silmukoittomasti riippuvuuksissa."""
        deps = {"C": ["A", "B"], "B": ["A"]}
        order = coordinator._topological_sort(deps)
        assert order.index("A") < order.index("B")
        assert order.index("B") < order.index("C")

    def test_run_calculates_duration(self, coordinator):
        """run() laskee suoritusaika."""
        result = coordinator.run(
            task="Koordinoi",
            agent_descriptions={"A": "A", "B": "B"},
        )
        assert result.total_duration > 0

    def test_run_calculates_score(self, coordinator):
        """run() laskee koordinaatiopisteet."""
        result = coordinator.run(
            task="Koordinoi",
            agent_descriptions={"A": "A", "B": "B", "C": "C"},
        )
        assert 0 <= result.coordination_score <= 100

    def test_run_serializes(self, coordinator):
        """Tulos voidaan serialisoida."""
        result = coordinator.run(
            task="Koordinoi",
            agent_descriptions={"A": "Agent A"},
        )
        d = result.to_dict()
        assert d["agent_type"] == "multi_agent_coordinator"
        assert "execution_order" in d

    def test_run_empty_agents(self, coordinator):
        """run() käsittelee tyhjät agentit."""
        result = coordinator.run(
            task="Koordinoi",
        )
        assert isinstance(result, CoordinationOutput)
        assert len(result.execution_order) == 0

    def test_run_execution_times_recorded(self, coordinator):
        """run() tallentaa suoritusaika."""
        result = coordinator.run(
            task="Koordinoi",
            agent_descriptions={"A": "A", "B": "B"},
        )
        assert "A" in result.execution_times
        assert "B" in result.execution_times
        assert result.execution_times["A"] >= 0

    def test_run_all_agents_executed(self, coordinator):
        """Kaikki agentit on suoritettu."""
        result = coordinator.run(
            task="Koordinoi",
            agent_descriptions={"A": "A", "B": "B", "C": "C"},
        )
        for agent_name in result.execution_order:
            result_entry = result.results.get(agent_name, {})
            assert result_entry.get("executed") is True
