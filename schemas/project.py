"""
Pydantic-skeemat M2 Project Management -moduulille.

Mallit:
- Requirement       — yksittäinen vaatimus.
- RequirementList   — vaatimusten kokoelma.
- ProjectFile       — projektiin kuuluva tiedosto.
- ProjectSpec       — täydellinen projektipaketti (nimi, tyyppi, vaatimukset, rakenne).
- ProjectPlan       — projektisuunnitelma (vaiheet + määräaika).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ProjectType(str, Enum):
    """Projekttien tyypit, jotka AIDE tukee."""

    PYTHON_API = "python-api"
    WEB_APP = "web-app"
    CLI = "cli"
    LIBRARY = "library"
    SCRIPT = "script"
    UNKNOWN = "unknown"


class ProjectTemplate(str, Enum):
    """ Projektipohjat."""

    FASTAPI = "fastapi"
    FLASK = "flask"
    DJANGO = "django"
    NEXTJS = "nextjs"
    REACT = "react"
    REACT_NATIVE = "react-native"
    CLI_TOOL = "cli-tool"
    AGENT = "agent"


class Priority(str, Enum):
    """Vaatimusten prioriteetti."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Requirement(BaseModel):
    """
    Yksittäinen vaatimus projektille.

    Example:
        req = Requirement(
            id="REQ-001",
            title="Käyttäjien kirjautuminen",
            description="Käyttäjän on pystyttävä rekisteröitymään ja kirjautumaan.",
            priority=Priority.HIGH,
            tags=["auth", "security"],
        )
    """

    id: str = Field(..., description="Vaatimuksen yksilöllinen tunniste (esim. REQ-001).")
    title: str = Field(..., min_length=1, description="Lyhyt otsikko.")
    description: str = Field(default="", description="Yksityiskohtainen kuvaus.")
    priority: Priority = Field(default=Priority.NORMAL, description="Prioriteetti.")
    tags: list[str] = Field(default_factory=list, description="Tagit luokitteluun.")
    related_files: list[str] = Field(default_factory=list, description="Liittyvät tiedostot.")

    model_config = {"use_enum_values": True}


class RequirementList(BaseModel):
    """Vaatimusten kokoelma."""

    requirements: list[Requirement] = Field(default_factory=list)

    def add(self, req: Requirement) -> "RequirementList":
        """Lisää vaatimuksen listalle."""
        self.requirements.append(req)
        return self

    def get_by_tag(self, tag: str) -> list[Requirement]:
        """Hakee vaatimukset tietystä tagista."""
        return [r for r in self.requirements if tag in r.tags]

    def get_by_priority(self, priority: Priority) -> list[Requirement]:
        """Hakee vaatimukset tietystä prioriteetista."""
        return [r for r in self.requirements if r.priority == priority]

    def to_markdown(self) -> str:
        """Serialoi vaatimukset Markdown-muotoon."""
        if not self.requirements:
            return "Ei vaatimuksia."

        lines = ["## Vaatimukset\n"]
        for r in self.requirements:
            lines.append(
                f"- **{r.id}** [{r.priority.upper()}] {r.title}\n"
                f"  Kuvaus: {r.description or 'Ei lisätietoja.'}\n"
                f"  Tagit: {', '.join(r.tags) if r.tags else 'Ei tagkeja'}\n"
            )
        return "\n".join(lines)


class ProjectFile(BaseModel):
    """Yksittäinen tiedosto projektin rakenteessa."""

    path: str = Field(..., description="Polku tiedostoon projektin juuren kohdalla.")
    description: str = Field(default="", description="Mitä tiedosto sisältää.")
    template: bool = Field(default=False, description="Onko tämä pohjatiedosto?")

    model_config = {"use_enum_values": True}


class ProjectSpec(BaseModel):
    """
    Täydellinen projektipaketti — kuvaa projektin alustuksen yhteydessä.

    Example:
        spec = ProjectSpec(
            name="MyAPI",
            type=ProjectType.PYTHON_API,
            description="Kuvaus projektilta.",
            requirements=RequirementList(...),
            file_structure=[ProjectFile("src/main.py", "Pääasiallinen moduuli.")],
        )
        spec.to_markdown()
    """

    name: str = Field(..., min_length=1, description="Projektin nimi.")
    type: ProjectType = Field(default=ProjectType.UNKNOWN, description="Projektin tyyppi.")
    template: Optional[ProjectTemplate] = Field(default=None, description="Valittu pohja.")
    description: str = Field(default="", description="Kuvaus projektilta.")
    version: str = Field(default="0.1.0", description="Aseta projektin versio.")
    author: str = Field(default="", description="Projektin omistaja.")
    requirements: RequirementList = Field(default_factory=RequirementList)
    file_structure: list[ProjectFile] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"use_enum_values": True}

    def to_markdown(self) -> str:
        """Serialoi projektin speksi Markdown-muotoon."""
        type_str = self.type.value if isinstance(self.type, ProjectType) else str(self.type)
        template_str = self.template.value if self.template and isinstance(self.template, ProjectTemplate) else (str(self.template) if self.template else "ei")

        lines = [
            f"# {self.name}\n",
            f"**Tyyppi:** {type_str}",
            f"**Pohja:** {template_str}",
            f"**Versio:** {self.version}",
            f"**Omistaja:** {self.author or 'Ei määritelty'}",
            "",
            f"## Kuvaus\n{self.description or 'Ei kuvausta.'}\n",
            self.requirements.to_markdown(),
            "",
        ]

        if self.file_structure:
            lines.append("## Tiedostorakenne\n")
            for f in self.file_structure:
                lines.append(f"- `{f.path}` — {f.description or ''}")

        return "\n".join(lines)


class ProjectPlan(BaseModel):
    """
    Projektisuunnitelma — määrittelee toteutusfaset.

    Example:
        plan = ProjectPlan(
            project_name="MyAPI",
            phases=["Setup", "API Endpoints", "Testing", "Documentation"],
            deadline="2026-12-31",
        )
    """

    project_name: str = Field(..., description="Projektin nimi.")
    phases: list[str] = Field(default_factory=list, description="Faset toteutuksessa.")
    deadline: Optional[str] = Field(default=None, description="Määräaika (ISO-muoto).")
    created_at: datetime = Field(default_factory=datetime.now, description="Luontipäivämäärä.")
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_markdown(self) -> str:
        """Serialoi suunnitelman Markdown-muotoon."""
        phase_lines = "\n".join(
            f"{i}. {phase}" for i, phase in enumerate(self.phases, 1)
        ) if self.phases else "Ei faset määritelty."

        return (
            f"## {self.project_name} — Toteutussuunnitelma\n\n"
            f"**Luotu:** {self.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"{f'**Määraaika:** {self.deadline}' if self.deadline else ''}\n"
            f"\n### Faset\n\n{phase_lines}\n"
        )


__all__ = [
    "ProjectType",
    "ProjectTemplate",
    "Priority",
    "Requirement",
    "RequirementList",
    "ProjectFile",
    "ProjectSpec",
    "ProjectPlan",
]
