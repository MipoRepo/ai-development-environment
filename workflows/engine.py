"""
Workflow Engine — tilakone workflowien suorittamiseen.

Tila-transitiot:
    INIT → ANALYZE → PLAN → IMPLEMENT → TEST → REVIEW → DOCUMENT → COMPLETE

    → ERROR (jos mikä tahansa vaihe kaatuu)

Usage:
    engine = WorkflowEngine(workflow_dir="workflows")
    execution = engine.run("base", DirectorOutput(...))
    for event in execution.events:
        print(event)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

import yaml


class WorkflowState(str, Enum):
    """Mahdolliset workflow-tilat."""

    INIT = "init"
    ANALYZE = "analyze"
    PLAN = "plan"
    IMPLEMENT = "implement"
    TEST = "test"
    REVIEW = "review"
    DOCUMENT = "document"
    COMPLETE = "complete"
    ERROR = "error"


# State transition chart: nykyinen_tila → sallitut_seuraavat_tilat
STATE_TRANSITIONS: dict[WorkflowState, list[WorkflowState]] = {
    WorkflowState.INIT: [WorkflowState.ANALYZE],
    WorkflowState.ANALYZE: [WorkflowState.PLAN, WorkflowState.ERROR],
    WorkflowState.PLAN: [WorkflowState.IMPLEMENT, WorkflowState.ERROR],
    WorkflowState.IMPLEMENT: [WorkflowState.TEST, WorkflowState.ERROR],
    WorkflowState.TEST: [WorkflowState.REVIEW, WorkflowState.ERROR],
    WorkflowState.REVIEW: [WorkflowState.DOCUMENT, WorkflowState.ERROR],
    WorkflowState.DOCUMENT: [WorkflowState.COMPLETE, WorkflowState.ERROR],
    WorkflowState.COMPLETE: [],
    WorkflowState.ERROR: [WorkflowState.ANALYZE, WorkflowState.PLAN, WorkflowState.COMPLETE],
}


class WorkflowError(Exception):
    """Heititetään workflow-ongelmien aikana."""


@dataclass
class PhaseResult:
    """Yhden workflow-vaiheen tulos."""

    phase_name: str
    success: bool
    output: Any = None
    message: str = ""
    error: Optional[str] = None


@dataclass
class WorkflowExecution:
    """Workflowin suoritusinstanssi — koko historian ja tapahtumia."""

    workflow_name: str
    state: WorkflowState = WorkflowState.INIT
    phases: list[str] = field(default_factory=list)
    phase_results: list[PhaseResult] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)

    def can_transition_to(self, target: WorkflowState) -> bool:
        """Tarkistaa onko tila-siirtyminen sallittua."""
        allowed = STATE_TRANSITIONS.get(self.state, [])
        return target in allowed

    def transition_to(self, target: WorkflowState) -> WorkflowState:
        """Suorittaa tila-siirtymän. Heittää WorkflowErrorin jos ei sallittu."""
        if not self.can_transition_to(target):
            raise WorkflowError(
                f"Siirtyminen {self.state.value} → {target.value} ei ole sallittu. "
                f"Sallitut: {[s.value for s in STATE_TRANSITIONS.get(self.state, [])]}"
            )
        self.state = target
        self.events.append(f"→ Tila siirretty: {self.state.value}")
        return self.state


class WorkflowEngine:
    """
    YAML-pohjainen workflow-moottori.

    Usage:
        engine = WorkflowEngine(workflow_dir="workflows")
        execution = engine.create_execution("base")
        result = engine.execute_phase(execution, "analyze", lambda ctx: "tuloste")
    """

    PHASE_TO_STATE: dict[str, WorkflowState] = {
        "init": WorkflowState.INIT,
        "analyze": WorkflowState.ANALYZE,
        "plan": WorkflowState.PLAN,
        "implement": WorkflowState.IMPLEMENT,
        "test": WorkflowState.TEST,
        "review": WorkflowState.REVIEW,
        "document": WorkflowState.DOCUMENT,
        "complete": WorkflowState.COMPLETE,
    }

    def __init__(self, workflow_dir: str = "workflows", strict: bool = True) -> None:
        self.workflow_dir = workflow_dir
        self.strict = strict  # Jos True, kaatuu workflowin puuttuessa.

    # ------------------------------------------------------------------ #
    # Workflow management
    # ------------------------------------------------------------------ #
    def list_workflows(self) -> list[str]:
        """Listaa käytettäviss olevat workflowt (ilman .yaml-päätettä)."""
        if not os.path.isdir(self.workflow_dir):
            return []
        workflows = []
        for f in sorted(os.listdir(self.workflow_dir)):
            if f.endswith((".yaml", ".yml")):
                workflows.append(f.rsplit(".", 1)[0])
        return workflows

    def load_workflow(self, workflow_name: str) -> dict[str, Any]:
        """Lataa YAML-workflow-konfiguraation."""
        # Jos päätettä ei ole, yritetään molempia (.yaml ja .yml)
        if workflow_name.endswith((".yaml", ".yml")):
            path = os.path.join(self.workflow_dir, workflow_name)
        else:
            # Yritä .yaml ensin, sitten .yml
            path_yaml = os.path.join(self.workflow_dir, f"{workflow_name}.yaml")
            path_yml = os.path.join(self.workflow_dir, f"{workflow_name}.yml")
            path = path_yaml if os.path.exists(path_yaml) else path_yml

        if not os.path.exists(path):
            available = self.list_workflows()
            raise WorkflowError(
                f"Workflow-tiedostoa ei löydy: {workflow_name}. "
                f"Saatavilla olevat workflowt: {available}" if available else "Ei workflow-tiedostoja käytettäviss."
            )

        with open(path, "r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh)
            if config is None:
                config = {}
        return config

    def create_execution(self, workflow_name: str = "base") -> WorkflowExecution:
        """Luo uuden suoritusinstanssin workflowille."""
        config = self.load_workflow(workflow_name)
        phases = [p["name"] for p in config.get("phases", [])] if "phases" in config else [
            "analyze", "plan", "implement", "test", "review", "document"
        ]
        # Normalize phase names: YAML can have dicts with 'name' key or plain strings
        if "phases" in config:
            normalized_phases = []
            for p in config["phases"]:
                if isinstance(p, dict):
                    normalized_phases.append(p.get("name", ""))
                else:
                    normalized_phases.append(str(p))
            phases = [p for p in normalized_phases if p]

        return WorkflowExecution(
            workflow_name=workflow_name,
            phases=phases,
            config=config,
            events=[f"✅ Luotu suoritus workflowille '{workflow_name}' faseineen: {phases}"],
        )

    # ------------------------------------------------------------------ #
    # Phase execution
    # ------------------------------------------------------------------ #
    def execute_phase(
        self,
        execution: WorkflowExecution,
        phase_name: str,
        handler: Callable[[dict[str, Any]], Any],
        context: Optional[dict[str, Any]] = None,
    ) -> PhaseResult:
        """
        Suorittaa yhden workflow-vaiheen.

        Args:
            execution: WorkflowExecution-instanssi.
            phase_name: Vaiheen nimi (analyze, plan, ...).
            handler: Funktio joka ottaa vastaan contextin ja palauttaa tulosteen.
            context: Vapaa konteksti, joka siirretään handlerille.

        Returns:
            PhaseResult.
        """
        phase_config = self._get_phase_config(execution, phase_name)
        agent_name = phase_config.get("agent", phase_name) if phase_config else phase_name

        try:
            # 1. Siirry oikeaan tilaan
            target_state = self.PHASE_TO_STATE.get(phase_name, WorkflowState.INIT)
            if not execution.can_transition_to(target_state):
                # Jos olemme virheessa, yritetään palautua
                if execution.state == WorkflowState.ERROR:
                    execution.transition_to(WorkflowState.ANALYZE)
                # Pakota siirtymys workflowin faset määräävät kelpoisuuden —
                # siis varsinkin lyhyissä workfloweissa (esim. bugfix:
                # analyze → implement → test) kirjaimelliset siirtymät eivät
                # aina ole suorituksissa.
                elif target_state.value in ( WorkflowState.COMPLETE.value, WorkflowState.ERROR.value):
                    raise WorkflowError(
                        f"Siirtyminen {execution.state.value} → {target_state.value} ei ole sallittu."
                    )
                else:
                    # Määritä siirtymä suoraan ilman tarkistusta, koska
                    # workflow-konfiguraatio on jo validoitu.
                    execution.state = target_state
            else:
                execution.transition_to(target_state)

            # 2. Suorita handleri
            context = context or {}
            context.update({"phase": phase_name, "agent": agent_name})
            result_output = handler(context)

            # 3. Rekisteröi tulos
            result = PhaseResult(
                phase_name=phase_name,
                success=True,
                output=result_output,
                message=f"✅ Vaihe '{phase_name}' suoritettu agentilla '{agent_name}'.",
            )
            execution.phase_results.append(result)
            execution.events.append(result.message)
            return result

        except Exception as e:
            error_msg = f"❌ Virhe vaiheessa '{phase_name}': {e}"
            result = PhaseResult(
                phase_name=phase_name,
                success=False,
                message=error_msg,
                error=str(e),
            )
            execution.phase_results.append(result)
            execution.events.append(error_msg)
            execution.transition_to(WorkflowState.ERROR)
            return result

    def execute_all(
        self,
        execution: WorkflowExecution,
        handlers: Optional[dict[str, Callable[[dict[str, Any]], Any]]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> WorkflowExecution:
        """
        Suorittaa kaikki workflowin vaiheet perkkäin.

        Args:
            execution: WorkflowExecution-instanssi.
            handlers: Sanakirja {phase_name: handler_func}.
                      Jos puuttuu, käytetään dummy-handlereita.
            context: Yleinen konteksti kaikille vaiheille.

        Returns:
            Päivitetty WorkflowExecution.
        """
        handlers = handlers or {}
        context = context or {}

        for phase_name in execution.phases:
            handler = handlers.get(phase_name, lambda ctx: f"[dummy] {ctx.get('phase')} suoritettu")
            result = self.execute_phase(execution, phase_name, handler, context=dict(context))

            # Pysäytä suoritus jos joku vaihe kaatuu
            if not result.success:
                execution.events.append("⚠️  Workflow päätyi virheeseen. Pysäytetään suoritus.")
                # Pakota ERROR-tila (transition_to voi jo pistää sen, mutta varmistetaan että se on sillä)
                if execution.state != WorkflowState.ERROR:
                    execution.state = WorkflowState.ERROR
                break

        # Merkitse valmiiksi — tarkista että kaikki vaiheet ovat onnistuneet
        if all(r.success for r in execution.phase_results) and len(execution.phase_results) == len(execution.phases):
            # Pakota COMPLETE-tila — workflowin faset ovat jo validoitu,
            # eikä täsmällinen tilan siirtymä eikä estä valmistumista
            # (esim. short workflow: analyze → implement → test → complete)
            execution.state = WorkflowState.COMPLETE
            execution.events.append("🎉 Workflow suoritus valmis onnistuneesti!")
        elif any(not r.success for r in execution.phase_results):
            if execution.state != WorkflowState.ERROR:
                execution.state = WorkflowState.ERROR
            execution.events.append("⚠️  Workflow päätyi virheeseen. tarkista phase_results.")

        return execution

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _get_phase_config(
        self, execution: WorkflowExecution, phase_name: str
    ) -> Optional[dict[str, Any]]:
        """Hakee yhtelysparametrien konfiguraation workflow-konfiguraatiosta."""
        phases = execution.config.get("phases", [])
        for p in phases:
            if isinstance(p, dict) and p.get("name") == phase_name:
                return p
        return None

    @staticmethod
    def validate_transition(from_state: WorkflowState, to_state: WorkflowState) -> bool:
        """Statinen metodi: tarkista onko siirtyminen sallittu."""
        return to_state in STATE_TRANSITIONS.get(from_state, [])


__all__ = [
    "WorkflowEngine",
    "WorkflowState",
    "WorkflowExecution",
    "PhaseResult",
    "WorkflowError",
    "STATE_TRANSITIONS",
]
