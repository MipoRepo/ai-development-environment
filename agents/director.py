"""
DirectorAgent — tämän moduulin pääagentti.

Toiminnot:
1. Ottaa vastaan käyttäjän tehtävän (luonnollinen kieli).
2. Tulkitsee sen YAML/JSON-muotoon workflow-konfiguraatiksi.
3. Valitsee oikean workflowin (esim. base.yaml, bugfix.yaml, feature.yaml).
4. Antaa ohjeet sen jokaiselle vaiheelle (Analyze → Plan → Implement → ...).
"""

from __future__ import annotations

import os
from typing import Any, Optional

import yaml
from pydantic import Field

from .base import AgentInput, AgentOutput, BaseAgent


class DirectorInput(AgentInput):
    """Directorin syöte — lisää workflow-prioriteetin."""

    preferred_workflow: Optional[str] = Field(default=None, description="Käytettävä workflow-tiedoston nimi (ilman .yaml).")
    priority: str = Field(default="normal", description="Prioriteetti: low / normal / high / urgent.")
    max_steps: int = Field(default=10, ge=1, le=50, description="Maksimi vaiheiden määrä.")


class DirectorOutput(AgentOutput):
    """Directorin tuloste — sisältää valitun workflowin ja vaiheiden listan."""

    workflow: str = Field(default="", description="Valittu workflow-tiedoston nimi.")
    phases: list[str] = Field(default_factory=list, description="Workflowin vaiheiden nimet.")
    task_breakdown: str = Field(default="", description="Tehtävän hajotus (generoitu teksti.)")
    workflow_config: dict[str, Any] = Field(default_factory=dict, description="Latautettu workflow-konfiguraatio.")

    model_config = {"arbitrary_types_allowed": True}


class DirectorAgent(BaseAgent):
    """
    DirectorAgent valitsee oikean workflowin käyttäjän tehtävän perusteella.

    Usage:
        director = DirectorAgent(workflow_dir="workflows/")
        result: DirectorOutput = director.run(
            task="Lisää User-moduuli projektiin.",
            priority="high",
        )
    """

    agent_type: str = "director"
    input_schema = DirectorInput
    output_schema = DirectorOutput

    def __init__(
        self,
        workflow_dir: str = "workflows",
        ai_provider: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(ai_provider=ai_provider, **kwargs)
        self.workflow_dir = workflow_dir

    def _list_available_workflows(self) -> list[str]:
        """Listaa käytettäviss olevat workflow-tiedostot (ilman .yaml-päätettä)."""
        if not os.path.isdir(self.workflow_dir):
            return []
        workflows = []
        for f in sorted(os.listdir(self.workflow_dir)):
            if f.endswith((".yaml", ".yml")):
                workflows.append(f.rsplit(".", 1)[0])
        return workflows

    def _load_workflow(self, workflow_name: str) -> dict[str, Any]:
        """Lataa YAML-workflow-tiedoston dictiksi."""
        # Jos päätettä ei ole, yritetään molempia (.yaml ja .yml)
        if workflow_name.endswith((".yaml", ".yml")):
            path = os.path.join(self.workflow_dir, workflow_name)
        else:
            path_yaml = os.path.join(self.workflow_dir, f"{workflow_name}.yaml")
            path_yml = os.path.join(self.workflow_dir, f"{workflow_name}.yml")
            path = path_yaml if os.path.exists(path_yaml) else path_yml

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Workflow-tiedostoa ei löydy: {workflow_name}. "
                f"Saatavilla olevat workflowt: {self._list_available_workflows()}"
            )

        with open(path, "r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh)
            if config is None:
                config = {}
        return config

    def _select_workflow(self, task: str, preferred: Optional[str]) -> tuple[str, dict[str, Any]]:
        """
        Valitsee oikean workflowin käyttäjän tehtävän perusteella.

        Prioriteetti:
        1. Jos `preferred` on annettu ja se on käytettäviss, käytä sitä.
        2. Analysoi tehtävän sanat (/bug|fix|virhe|parannus → bugfix;
           /feature|uusi|lisää|toimi → feature; muu → base).
        3. Palauta latautettu workflow-konfiguraatio.

        Returns:
            (workflow_nimi, workflow_config)
        """
        available = self._list_available_workflows()
        if not available:
            # Fallback: palauta minimi-konfiguraatio
            return ("base", self._default_workflow_config())

        # 1. Suora valinta
        if preferred and preferred in available:
            return (preferred, self._load_workflow(preferred))

        # 2. Avainsanasilmukointi
        task_lower = task.lower()
        keyword_map = {
            "bugfix": [
                "bug", "virhe", "poistaa", "korjata", "parannus",
                "error", "crash", "exception", "broken",
            ],
            "feature": [
                "uusi", "lisää", "feature", "toiminnallisuus",
                "implement", "add", "create", "build",
            ],
            "new-project": [
                "projekti", "project", "uusi projekti",
                "init", "luo projekti", "set up",
            ],
        }

        for workflow, keywords in keyword_map.items():
            if workflow in available and any(kw in task_lower for kw in keywords):
                return (workflow, self._load_workflow(workflow))

        # 3. Oletus
        if "base" in available:
            return ("base", self._load_workflow("base"))
        return (available[0], self._load_workflow(available[0]))

    def _default_workflow_config(self) -> dict[str, Any]:
        """Minimikonfiguraatio, joka käytetään jos workflow-tiedostoja ei ole."""
        return {
            "name": "base",
            "phases": ["analyze", "plan", "implement", "test", "review", "document"],
        }

    def _interpret_task_to_yaml(self, task: str, priority: str, max_steps: int) -> str:
        """
        Generoi YAML-merkkijonon käyttäjän tehtävän workflow-konfiguraationa.

        Tämä on "tulkitsee käyttäjätehtävät YAML/JSON-muodossa" -ominaisuus.
        """
        phases = ["analyze", "plan", "implement", "test", "review", "document"]
        config = {
            "name": "generated",
            "description": f"Workflow käyttäjän tehtävästä: {task}",
            "priority": priority,
            "max_steps": max_steps,
            "phases": phases,
        }
        return yaml.dump(config, default_flow_style=False, sort_keys=False)

    def _run(self, input_data: DirectorInput) -> DirectorOutput:
        """DirectorAgentin päälogiikka."""
        task = input_data.task
        context = input_data.context or {}

        # 1. Valitse workflow
        workflow_name, workflow_config = self._select_workflow(
            task=task,
            preferred=input_data.preferred_workflow,
        )

        # 2. Hae vaiheet workflow-konfiguraatiosta (normalisoi dict → str)
        raw_phases = workflow_config.get("phases", ["analyze", "plan", "implement", "test", "review", "document"])
        phases = []
        for p in raw_phases:
            if isinstance(p, dict):
                phases.append(p.get("name", str(p)))
            else:
                phases.append(str(p))

        # 3. Tulkitse tehtävä (YAML-muotoon)
        task_yaml = self._interpret_task_to_yaml(
            task=task,
            priority=input_data.priority,
            max_steps=input_data.max_steps,
        )

        # 4. Generoi tehtävän hajoittamisen teksti
        breakdown = (
            f"Tehtävä: '{task}'\n"
            f"Valittu workflow: {workflow_name}\n"
            f"Vaiheet ({len(phases)}): {', '.join(phases)}\n"
            f"Prioriteetti: {input_data.priority}\n"
            f"Max vaihetta: {input_data.max_steps}\n\n"
            f"Task YAML:\n{task_yaml}"
        )

        return DirectorOutput(
            success=True,
            result={"workflow_name": workflow_name, "phases": phases},
            message=breakdown,
            agent_type=self.agent_type,
            workflow=workflow_name,
            phases=phases,
            task_breakdown=breakdown,
            workflow_config=workflow_config,
        )


__all__ = ["DirectorAgent", "DirectorInput", "DirectorOutput"]
