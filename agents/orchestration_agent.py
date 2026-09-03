"""
OrchestrationAgent-moduuli (M9) — workflow- ja moniagenttiorkesterointi.

Sisältää kaksi agenttia:
- WorkflowOrchestratorAgent: orkestroi agentteja työnkulkuvaiheiden läpi.
- MultiAgentCoordinator: koordinoi monia agentteja yhtäaikaisesti riippuvuuksien mukaan.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


class WorkflowOrchestratorInput(AgentInput):
    """WorkflowOrchestratorAgentin syöte."""

    task: str = Field(..., min_length=1, description="Suoritettava tehtävä.")
    agents: Optional[list[str]] = Field(default=None, description="Käytettävät agentit.")
    phases: Optional[list[str]] = Field(default=None, description="Vaiheiden nimet järjekunnassa.")
    context: dict[str, Any] = Field(default_factory=dict, description="Alustava konteksti.")
    max_phases: int = Field(default=8, description="Vaiheiden enimmäismäärä.")
    stop_on_error: bool = Field(default=False, description="Pysäytetäänkö virheen sattuessa.")


class WorkflowOrchestratorOutput(AgentOutput):
    """WorkflowOrchestratorAgentin tuloste."""

    phase_results: list[dict[str, Any]] = Field(default_factory=list, description="Vaiheiden tulokset.")
    phases_executed: int = Field(default=0, description="Suoritettujen vaiheiden lukumäärä.")
    final_agent: str = Field(default="", description="Viime agentti, joka suoritettiin.")
    total_duration: float = Field(default=0.0, description="Kokonaisaika sekuntina.")
    context: dict[str, Any] = Field(default_factory=dict, description="Päivitetty konteksti.")
    phase_sequence: list[str] = Field(default_factory=list, description="Suoritettujen vaiheiden nimet.")


class CoordinationInput(AgentInput):
    """MultiAgentCoordinatorin syöte."""

    task: str = Field(..., min_length=1, description="Koordinoitava tehtävä.")
    agent_descriptions: dict[str, str] = Field(default_factory=dict, description="Agenttien kuvaukset.")
    dependencies: dict[str, list[str]] = Field(default_factory=dict, description="Riippuvuussuhdepuu.")
    timeout: float = Field(default=60.0, description="Aikakatkaika sekunteina.")


class CoordinationOutput(AgentOutput):
    """MultiAgentCoordinatorin tuloste."""

    execution_order: list[str] = Field(default_factory=list, description="Suoritusjärjestys riippuvuuksien mukaan.")
    results: dict[str, Any] = Field(default_factory=dict, description="Agenttien tulokset.")
    execution_times: dict[str, float] = Field(default_factory=dict, description="Agenttien suoritusaika.")
    total_duration: float = Field(default=0.0, description="Kokonaisaika.")
    coordination_score: float = Field(default=0.0, description="Koordinaatiopisteet (0-100).")


class _PhaseHandler:
    """Mock-käsittelijä workflow-vaiheille (simulointi."""

    @staticmethod
    def handle(phase: str, context: dict[str, Any]) -> dict[str, Any]:
        """Käsittelee yhden vaiheen."""
        # Simuloitu vastaus vaiheelta
        responses = {
            "analyze": {"analyzed": True, "technologies": ["fastapi", "pydantic"]},
            "plan": {"planned": True, "tasks": ["dev", "test", "document"]},
            "implement": {"implemented": True, "files": ["main.py"]},
            "test": {"tested": True, "passed": 8, "failed": 1},
            "review": {"approved": True, "comments": []},
            "document": {"documented": True, "files": ["README.md"]},
        }
        result = responses.get(phase.lower(), {"processed": True, "phase": phase})
        result["phase"] = phase
        result["timestamp"] = time.time()
        return result


class WorkflowOrchestratorAgent(BaseAgent):
    """
    WorkflowOrchestratorAgent orkestroi agentit työnkulku vaiheittain.

    Käyttää WorkflowEngineä ja WorkflowState-enumia. Simuloi vaiheiden suorittamista
    ja päivittää kontekstin joka vaiheen jälkeen.

    Usage:
        agent = WorkflowOrchestratorAgent()
        result = agent.run("Aloita projekti", phases=["analyze", "plan", "implement"])
    """

    agent_type: str = "workflow_orchestrator"
    input_schema = WorkflowOrchestratorInput
    output_schema = WorkflowOrchestratorOutput

    # Oletusvaiheiden määritykset
    DEFAULT_PHASES: list[str] = ["analyze", "plan", "implement", "test", "review", "document"]

    DEFAULT_AGENT_MAP: dict[str, list[str]] = {
        "analyze": ["ResearcherAgent", "TechnologyResearcherAgent"],
        "plan": ["ProjectManagerAgent", "RequirementsAgent"],
        "implement": ["DeveloperAgent", "CodeReviewAgent"],
        "test": ["TestDesignerAgent", "TesterAgent", "QAAgent"],
        "review": ["SecurityReviewAgent", "SASTAgent", "CodeReviewAgent"],
        "document": ["TechnicalWriterAgent", "APIDocumentationAgent", "MkDocsAgent"],
    }

    def _validate_phase(self, phase: str, valid_phases: list[str]) -> bool:
        """Vahvista, että vaihe on sallittu."""
        return phase.lower() in [p.lower() for p in valid_phases]

    def _get_agents_for_phase(self, phase: str) -> list[str]:
        """Hae agentit, jotka kuuluvat vaiheeseen."""
        agents = self.DEFAULT_AGENT_MAP.get(phase.lower(), [])
        if not agents:
            # yleinen fallback
            agents = ["DirectorAgent"]
        return agents

    def _resolve_phase_sequence(self, phases: Optional[list[str]], max_phases: int) -> list[str]:
        """Päätä vaihejärjestys."""
        if phases:
            valid = [p for p in phases if self._validate_phase(p, self.DEFAULT_PHASES)]
            return valid
        return self.DEFAULT_PHASES[:max_phases]

    def _run(self, input_data: WorkflowOrchestratorInput) -> WorkflowOrchestratorOutput:
        """WorkflowOrchestratorAgentin päälogiika."""
        start_time = time.perf_counter()

        # 1. Päätä vaihejärjestys
        phase_sequence = self._resolve_phase_sequence(input_data.phases, input_data.max_phases)

        if not phase_sequence:
            return WorkflowOrchestratorOutput(
                success=False,
                result=None,
                message="Ei kelvollisia vaiheita annettu.",
                agent_type=self.agent_type,
                total_duration=0.0,
            )

        # 2. Alusta konteksti
        context = dict(input_data.context) if input_data.context else {}

        # 3. Suorita vaiheet
        phase_results: list[dict[str, Any]] = []
        phases_executed = 0
        final_agent = ""
        error_occurred = False

        for phase in phase_sequence:
            phase_start = time.perf_counter()
            try:
                # Hae agentit vaiheelle
                phase_agents = input_data.agents if input_data.agents else self._get_agents_for_phase(phase)

                # Suorita vaihe
                result = _PhaseHandler.handle(phase, context)

                # Päivitä konteksti
                context.update(result)
                context[f"{phase}_agents"] = phase_agents

                phase_duration = time.perf_counter() - phase_start
                result["duration"] = phase_duration
                result["agents"] = phase_agents

                phase_results.append(result)
                phases_executed += 1
                final_agent = phase_agents[-1] if phase_agents else ""

            except Exception as e:
                error_occurred = True
                phase_results.append({
                    "phase": phase,
                    "error": str(e),
                    "success": False,
                })
                if input_data.stop_on_error:
                    break

        total_duration = time.perf_counter() - start_time
        success = not error_occurred or (error_occurred and not input_data.stop_on_error)

        return WorkflowOrchestratorOutput(
            success=success,
            result={"phases_executed": phases_executed, "final_context_keys": len(context)},
            message=f"Orkesterointi valmis: {phases_executed}/{len(phase_sequence)} vaihetta.",
            agent_type=self.agent_type,
            phase_results=phase_results,
            phases_executed=phases_executed,
            final_agent=final_agent,
            total_duration=total_duration,
            context=context,
            phase_sequence=phase_sequence,
        )


class MultiAgentCoordinator(BaseAgent):
    """
    MultiAgentCoordinator koordinoi useita agentteja riippuvuuksien mukaan.

    Usage:
        agent = MultiAgentCoordinator()
        result = agent.run("Koordinoi agentit", agent_descriptions={...}, dependencies={...})
    """

    agent_type: str = "multi_agent_coordinator"
    input_schema = CoordinationInput
    output_schema = CoordinationOutput

    def _topological_sort(self, deps: dict[str, list[str]]) -> list[str]:
        """Topologinen järjestys riippuvuuksien mukaan (Kahnin algoritmi)."""
        # Kasvata kaikki moduulit
        all_nodes: set[str] = set()
        for node, dep_list in deps.items():
            all_nodes.add(node)
            all_nodes.update(dep_list)

        # Laske sisääntulot
        in_degree: dict[str, int] = {n: 0 for n in all_nodes}
        for node, dep_list in deps.items():
            for dep in dep_list:
                if dep in in_degree:
                    pass  # riippuvuus laskettu
            in_degree[node] = len(dep_list)

        # Aseta jono (nolla sisääntulot)
        queue: list[str] = [n for n, d in in_degree.items() if d == 0]
        order: list[str] = []

        while queue:
            # Järjestä aakkosellisesti determinismi
            queue.sort()
            current = queue.pop(0)
            order.append(current)

            # välti solmut, jotka riippuvat tästä
            for node, dep_list in deps.items():
                if current in dep_list:
                    in_degree[node] -= 1
                    if in_degree[node] == 0 and node not in order and node not in queue:
                        queue.append(node)

        return order

    def _execute_agent(self, name: str, description: str, context: dict[str, Any]) -> dict[str, Any]:
        """Simuloi agentin suoritusta."""
        start = time.perf_counter()
        # Simuloi nopeasti
        result = {
            "agent": name,
            "description": description,
            "executed": True,
            "timestamp": time.time(),
        }
        elapsed = time.perf_counter() - start
        return {"result": result, "duration": elapsed}

    async def _execute_async(self, name: str, description: str, context: dict[str, Any]) -> dict[str, Any]:
        """Asynhroninen agentin suoritus (simulointi)."""
        start = time.perf_counter()
        await asyncio.sleep(0.001)  # pieni viive simulointia varten
        result = {
            "agent": name,
            "description": description,
            "executed": True,
            "timestamp": time.time(),
        }
        elapsed = time.perf_counter() - start
        return {"result": result, "duration": elapsed}

    def _run(self, input_data: CoordinationInput) -> CoordinationOutput:
        """MultiAgentCoordinatorin päälogiika."""
        start_time = time.perf_counter()

        # 1. Päätä suoritusjärjestys
        if input_data.dependencies:
            execution_order = self._topological_sort(input_data.dependencies)
        else:
            # Yksinkertainen järjestys ilman riippuvuuksia
            execution_order = list(input_data.agent_descriptions.keys()) if input_data.agent_descriptions else []

        # 2. Valitse agentit (jos ei annettu, käytetään oletus)
        agent_descs = input_data.agent_descriptions
        if not agent_descs:
            agent_descs = {a: f"Agentti {a}" for a in execution_order}

        # 3. Suorita agentit
        results: dict[str, Any] = {}
        execution_times: dict[str, float] = {}
        context: dict[str, Any] = dict(input_data.context) if input_data.context else {}

        for agent_name in execution_order:
            desc = agent_descs.get(agent_name, "")
            exec_result = self._execute_agent(agent_name, desc, context)
            results[agent_name] = exec_result["result"]
            execution_times[agent_name] = exec_result["duration"]
            context[agent_name] = exec_result["result"]

        total_duration = time.perf_counter() - start_time

        # 4. Laske koordinaatiopisteet
        success_count = sum(1 for r in results.values() if r.get("executed"))
        total = len(execution_order)
        score = (success_count / total * 100) if total > 0 else 0.0

        return CoordinationOutput(
            success=success_count == total,
            result={"agents_executed": success_count, "total_agents": total},
            message=f"Koordinaatio valmis: {success_count}/{total} agenttia suoriteltu.",
            agent_type=self.agent_type,
            execution_order=execution_order,
            results=results,
            execution_times=execution_times,
            total_duration=total_duration,
            coordination_score=score,
        )


__all__ = [
    "WorkflowOrchestratorAgent",
    "WorkflowOrchestratorInput",
    "WorkflowOrchestratorOutput",
    "MultiAgentCoordinator",
    "CoordinationInput",
    "CoordinationOutput",
]
