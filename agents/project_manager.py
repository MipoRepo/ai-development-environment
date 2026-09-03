"""
ProjectManagerAgent (M2) — hallitsee projektin elinkaarta.

Toiminnot:
1. Lukee projektispeksin (ProjectSpec) ja luo tiedostorakenteen.
2. Luo projektisuunnitelman (ProjectPlan) faset-merkkijonojen avulla.
3. Seuraa projektin edistymistä.
4. Tuottaa PROJECT.md- ja AGENTS.md-sisällöt.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent
from schemas.project import ProjectPlan, ProjectSpec, ProjectType, RequirementList


class ProjectManagerInput(AgentInput):
    """ProjectManagerin syöte."""

    project_spec: Optional[dict[str, Any]] = Field(
        default=None, description="Projektispeksi (sanakirja ProjectSpecistä)."
    )
    create_structure: bool = Field(default=True, description="Luo tiedostorakenne projektin juureen.")
    project_path: str = Field(default=".", description="Polku projektipuohon.")
    generate_docs: bool = Field(default=True, description="Luo PROJECT.md ja AGENTS.md.")


class ProjectManagerOutput(AgentOutput):
    """ProjectManagerin tuloste."""

    project_name: str = Field(default="", description="Projektin nimi.")
    project_path: str = Field(default="", description="Polku projektiin.")
    created_files: list[str] = Field(default_factory=list, description="Luodut tiedostot.")
    plan: Optional[dict[str, Any]] = Field(default=None, description="Projektisuunnitelma (projektina).")
    spec: Optional[dict[str, Any]] = Field(default=None, description="Projektispeksi.")

    model_config = {"arbitrary_types_allowed": True}


class ProjectManagerAgent(BaseAgent):
    """
    ProjectManagerAgent hallitsee projektin elinkaarta.

    Usage:
        manager = ProjectManagerAgent()
        result = manager.run(
            task="Luo uusi Python-API-projekti nimeltä MyAPI",
            project_spec={...}
        )
    """

    agent_type: str = "project_manager"
    input_schema = ProjectManagerInput
    output_schema = ProjectManagerOutput

    def __init__(self, ai_provider: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(ai_provider=ai_provider, **kwargs)

    def _get_default_structure(self, project_type: ProjectType) -> list[str]:
        """Palauttaa oletetun tiedostorakenteen projektityypin mukaan."""
        base = ["src/", "tests/", "docs/", "planning/"]
        type_specific: dict[ProjectType, list[str]] = {
            ProjectType.PYTHON_API: ["src/api/", "src/models/", "src/schemas/"],
            ProjectType.WEB_APP: ["src/components/", "src/pages/", "src/styles/"],
            ProjectType.CLI: ["src/commands/"],
            ProjectType.LIBRARY: ["src/"],
            ProjectType.SCRIPT: [],
            ProjectType.UNKNOWN: [],
        }
        return base + type_specific.get(project_type, [])

    def _create_file_structure(self, spec: ProjectSpec, project_path: Path) -> list[str]:
        """Luo tiedostorakenteen projektin juureen."""
        project_path.mkdir(parents=True, exist_ok=True)
        created: list[str] = []

        # Aseta oletus-tiedostorakenne jos ei ole määritelty
        if not spec.file_structure:
            dirs = self._get_default_structure(spec.type)
            for d in dirs:
                dir_path = project_path / d
                dir_path.mkdir(parents=True, exist_ok=True)
                created.append(str(dir_path.relative_to(project_path)) + "/")

        # Luo määritellyt tiedostot
        for f in spec.file_structure:
            file_path = project_path / f.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if not file_path.exists():
                file_path.write_text(f"# {f.description or 'Projektitiedosto'}\n", encoding="utf-8")
                created.append(str(file_path.relative_to(project_path)))

        return created

    def _generate_project_md(self, spec: ProjectSpec) -> str:
        """Generoi PROJECT.md-sisällön."""
        return spec.to_markdown()

    def _generate_agents_md(self, spec: ProjectSpec, plan: ProjectPlan) -> str:
        """Generoi AGENTS.md-sisällön agenttien kuvauksena."""
        type_str = spec.type.value if isinstance(spec.type, ProjectType) else str(spec.type)
        phase_lines = "\n".join(
            f"  {i}. {p}" for i, p in enumerate(plan.phases, 1)
        ) if plan.phases else "  Ei faset määritelty."

        return (
            f"# Agentit — {spec.name}\n\n"
            f"Tämän projektin yhteydessä käytettävät agentit:\n\n"
            f"- **[DirectorAgent]** — Valitsee oikean workflowin tehtävällä.\n"
            f"- **[ProjectManagerAgent]** — Hallitsee tämän projektin elinkaarta ({type_str}).\n"
            f"- **[DeveloperAgent]** — Kirjoittaa ja muokkaa koodia.\n"
            f"- **[TesterAgent]** — Suunnittelee ja suorittaa testit.\n"
            f"- **[SecurityReviewerAgent]** — Tarkistaa turvallisuuden.\n"
            f"- **[TechnicalWriterAgent]** — Päivittää dokumentaation.\n\n"
            f"## Toteutussuunnitelma\n\n"
            f"{phase_lines}\n"
        )

    def _generate_plan(self, spec: ProjectSpec) -> ProjectPlan:
        """Luo projektisuunnitelman vaatintojen ja projektipohjan perusteella."""
        type_defaults: dict[str, list[str]] = {
            ProjectType.PYTHON_API.value: [
                "1. Projektin asetukset ja riippuvuudet",
                "2. Tietokantamallit ja skeemat",
                "3. API-endpointit (FastAPI tai Flask)",
                "4. Testit javalidointi",
                "5. Dokumentaatio API:stä",
            ],
            ProjectType.WEB_APP.value: [
                "1. Frontend-kehysvalikoima (React, Next.js)",
                "2. Backend-integraatio",
                "3. Komponentit ja sivut",
                "4. Ulkoasu ja tyyli",
                "5. Testaus ja deploy",
            ],
            ProjectType.CLI.value: [
                "1. CLI-arkkitehtuuri ja komennot",
                "2. Argumenttien jäsentäminen (Typer)",
                "3 toteutus",
                "3. Testaus ja dokumentaatio",
            ],
        }

        ptype = spec.type.value if isinstance(spec.type, ProjectType) else str(spec.type)
        phases = type_defaults.get(ptype, [
            "1. Projektin asetukset",
            "2. Arkkitehtuuri",
            "3. Toteutus",
            "4. Testaus",
            "5. Dokumentaatio",
        ])
        # Lisää vaatimusten mukaan
        for req in spec.requirements.requirements[:3]:
            phases.append(f"   - Vaatimus: {req.title} ({req.priority})")

        return ProjectPlan(
            project_name=spec.name,
            phases=phases,
            deadline=spec.metadata.get("deadline"),
        )

    def _run(self, input_data: ProjectManagerInput) -> ProjectManagerOutput:
        """ProjectManagerAgentin päälogiikka."""
        project_path = Path(input_data.project_path)
        created_files: list[str] = []

        # 1. Muodista projektispeksi
        if input_data.project_spec:
            spec = ProjectSpec(**input_data.project_spec)
        else:
            # Luo minimispecs kuvauksen perusteella
            spec = ProjectSpec(
                name=input_data.metadata.get("project_name", "UntitledProject"),
                type=ProjectType(input_data.metadata.get("project_type", ProjectType.UNKNOWN.value)),
                description=input_data.task,
            )

        # 2. Luo tiedostorakenne
        if input_data.create_structure:
            created_files = self._create_file_structure(spec, project_path)

            # 3. Generoi dokumentaatio
            if input_data.generate_docs:
                plan = self._generate_plan(spec)

                project_md = project_path / "PROJECT.md"
                project_md.write_text(self._generate_project_md(spec), encoding="utf-8")
                created_files.append("PROJECT.md")

                agents_md = project_path / "AGENTS.md"
                agents_md.write_text(self._generate_agents_md(spec, plan), encoding="utf-8")
                created_files.append("AGENTS.md")

                plan_md = project_path / "planning" / "plan.md"
                plan_md.parent.mkdir(parents=True, exist_ok=True)
                plan_md.write_text(plan.to_markdown(), encoding="utf-8")
                created_files.append("planning/plan.md")
            else:
                plan = self._generate_plan(spec)

            # 4. Luo requirements.json (vaatimusten serialisointi)
            req_json = project_path / "requirements.json"
            req_data = {
                "project_name": spec.name,
                "type": spec.type.value if isinstance(spec.type, ProjectType) else str(spec.type),
                "requirements": [r.model_dump() for r in spec.requirements.requirements],
            }
            req_json.write_text(json.dumps(req_data, indent=2, ensure_ascii=False), encoding="utf-8")
            created_files.append("requirements.json")
        else:
            plan = self._generate_plan(spec)

        return ProjectManagerOutput(
            success=True,
            result={"project_name": spec.name, "created_count": len(created_files)},
            message=f"Projekti '{spec.name}' alustettu. Luodut tiedostot: {len(created_files)}.",
            agent_type=self.agent_type,
            project_name=spec.name,
            project_path=str(project_path),
            created_files=created_files,
            plan=plan.model_dump(),
            spec=spec.model_dump(),
        )


__all__ = ["ProjectManagerAgent", "ProjectManagerInput", "ProjectManagerOutput"]
