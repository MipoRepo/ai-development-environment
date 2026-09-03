"""
ResearcherAgent (M3) — analysoi projektin tiedostoja ja rakenteen.

Toiminnot:
1. Etsii Python-tiedostoja ja jäsentää funktiot, luokat, moduulit.
2. Antaa yhteenvetonäkemyksen projektirakenteesta.
3. Poimii importit ja riippuvuudet.

TechnologyResearcherAgent:
- Tutkii teknologioita / kirjastoja ja antaa suosituksia.
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


# Sanat, jotka auttavat tunnistama teknologian kirjastoja
TECH_KEYWORDS: dict[str, list[str]] = {
    "fastapi": ["fastapi", "uvicorn", "starlette"],
    "flask": ["flask", "werkzeug"],
    "django": ["django", "celery"],
    "react": ["react", "reactjs", "jsx"],
    "nextjs": ["nextjs", "next/", "next.config"],
    "vue": ["vue", "vuejs"],
    "pytest": ["pytest"],
    "pydantic": ["pydantic"],
    "sqlalchemy": ["sqlalchemy", "alembic"],
    "requests": ["requests", "httpx"],
    "openai": ["openai", "langchain"],
    "typer": ["typer"],
    "pyyaml": ["yaml", "pyyaml"],
    "jinja2": ["jinja2", "jinja"],
}


class ResearchInput(AgentInput):
    """ResearchAgentin syöte."""

    project_path: str = Field(default=".", description="Polku tutkittavaksi projektipuukäsittelemään.")
    file_extensions: Optional[list[str]] = Field(
        default=None, description="Tutkittavat tiedostotyypit (esim. ['.py', '.js'])."
    )
    max_files: int = Field(default=100, description="Enimmäismäärä tutittavia tiedostoja.")


class ResearchOutput(AgentOutput):
    """ResearchAgentin tuloste."""

    project_name: str = Field(default="", description="Projektin nimi.")
    file_count: int = Field(default=0, description="Löydettyjen tiedostojen määrä.")
    structure: dict[str, Any] = Field(default_factory=dict, description="Projektirakeneesta.")
    functions: list[dict[str, Any]] = Field(default_factory=list, description="Löydetyt funktiot.")
    classes: list[dict[str, Any]] = Field(default_factory=list, description="Löydetyt luokat.")
    imports: list[str] = Field(default_factory=list, description="Uniikit importit.")
    technologies: list[str] = Field(default_factory=list, description="Löydetyt teknologiat.")


class TechResearchInput(AgentInput):
    """TechnologyResearcherAgentin syöte."""

    technologies: Optional[list[str]] = Field(
        default=None, description="Etsittävät teknologiat (esim. ['fastapi'])."
    )
    project_files: list[str] = Field(default_factory=list, description="Projektitiedostopolut.")


class TechResearchOutput(AgentOutput):
    """TechnologyResearcherAgentin tuloste."""

    detected_technologies: dict[str, list[str]] = Field(
        default_factory=dict, description="Teknologiat ja niiden löydökset."
    )
    recommendations: list[str] = Field(default_factory=list, description="Suositukset.")
    missing_dependencies: list[str] = Field(default_factory=list, description="Puuttuvat riippuvuudet.")


class ResearcherAgent(BaseAgent):
    """
    ResearcherAgent analysoi projektin tiedostoja ja antaa rakenteesta yhtzeen vetoja.

    Usage:
        agent = ResearcherAgent()
        result = agent.run(
            task="Analysoi tämä projekti",
            project_path=".",
            file_extensions=[".py", ".js"],
        )
    """

    agent_type: str = "researcher"
    input_schema = ResearchInput
    output_schema = ResearchOutput

    def _scan_files(self, project_path: Path, extensions: Optional[list[str]], max_files: int) -> list[Path]:
        """Skannaa projektista tiedostot annetuista päätteistä."""
        if not project_path.exists():
            return []

        found: list[Path] = []
        # Ohita yleiset hakemistot
        skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", "site-packages", "dist", "build", "htmlcov", ".pytest_cache", "docs"}

        for root, dirs, files in os.walk(project_path):
            # Suodata ohjattavat hakemistot
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for fname in files:
                if extensions is None or any(fname.endswith(ext) for ext in extensions):
                    fpath = Path(root) / fname
                    found.append(fpath)
                    if len(found) >= max_files:
                        return found

        return found[:max_files]

    def _analyze_python_file(self, filepath: Path) -> dict[str, Any]:
        """Analysoi yksittäisen Python-tiedoston AST-parsimisemellä."""
        result: dict[str, Any] = {
            "path": str(filepath),
            "functions": [],
            "classes": [],
            "imports": [],
            "lines": 0,
        }
        try:
            source = filepath.read_text(encoding="utf-8", errors="replace")
            result["lines"] = len(source.splitlines())
            tree = ast.parse(source, filename=str(filepath))

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    result["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node) or "",
                    })
                elif isinstance(node, ast.ClassDef):
                    result["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        "docstring": ast.get_docstring(node) or "",
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            result["imports"].append(alias.name)
                    else:
                        if node.module:
                            result["imports"].append(node.module)

        except (SyntaxError, ValueError) as e:
            result["error"] = str(e)

        return result

    def _detect_technologies(self, all_files: list[Path]) -> list[str]:
        """Havaitsee teknologiat tiedostojen sisällöistä."""
        detected: set[str] = set()

        for fpath in all_files:
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace").lower()
                for tech, keywords in TECH_KEYWORDS.items():
                    if any(kw in content for kw in keywords):
                        detected.add(tech)
            except (OSError, PermissionError):
                continue

        return sorted(detected)

    def _build_structure(self, files: list[Path], base: Path) -> dict[str, Any]:
        """Rakentaa hakemistorakenteen dictionaryna."""
        structure: dict[str, Any] = {"name": base.name, "children": []}

        for fpath in sorted(files, key=lambda x: str(x)):
            try:
                rel = fpath.relative_to(base)
            except ValueError:
                rel = fpath

            parts = rel.parts
            current = structure
            for part in parts[:-1]:
                child = next((c for c in current.get("children", []) if c["name"] == part and "children" in c), None)
                if child is None:
                    child = {"name": part, "children": []}
                    current.setdefault("children", []).append(child)
                current = child

            file_entry = {"name": parts[-1], "type": "file"}
            current.setdefault("children", []).append(file_entry)

        return structure

    def _run(self, input_data: ResearchInput) -> ResearchOutput:
        """ResearchAgentin päälogiikka."""
        project_path = Path(input_data.project_path)
        extensions = input_data.file_extensions or [".py"]
        max_files = input_data.max_files

        # 1. Skannaa tiedostot
        files = self._scan_files(project_path, extensions, max_files)

        # 2. Analysoi tiedostot
        all_functions: list[dict[str, Any]] = []
        all_classes: list[dict[str, Any]] = []
        all_imports: set[str] = set()
        file_details: list[dict[str, Any]] = []

        py_files = [f for f in files if f.suffix == ".py"]
        for fpath in py_files:
            analysis = self._analyze_python_file(fpath)
            all_functions.extend(analysis["functions"])
            all_classes.extend(analysis["classes"])
            all_imports.update(analysis["imports"])
            file_details.append(analysis)

        # 3. Havaitse teknologiat
        technologies = self._detect_technologies(files)

        # 4. Rakenna rakenne
        structure = self._build_structure(files, project_path) if files else {"name": project_path.name, "children": []}

        # 5. Poimi projektin nimi
        project_name = project_path.name if project_path.exists() else "projekti"

        return ResearchOutput(
            success=True,
            result={
                "project_name": project_name,
                "file_count": len(files),
                "function_count": len(all_functions),
                "class_count": len(all_classes),
            },
            message=f"Analysoitu {len(files)} tiedostoa: {len(all_functions)} funktiota, {len(all_classes)} luokkaa, {len(technologies)} teknologiaa.",
            agent_type=self.agent_type,
            project_name=project_name,
            file_count=len(files),
            structure=structure,
            functions=all_functions,
            classes=all_classes,
            imports=sorted(all_imports),
            technologies=technologies,
        )


class TechnologyResearcherAgent(BaseAgent):
    """
    TechnologyResearcherAgent tutkii teknologioita ja antaa suosituksia.

    Usage:
        agent = TechnologyResearcherAgent()
        result = agent.run(
            task="Tutki käytetyt teknologiat tässä projektissa",
            project_files=["src/main.py", "requirements.txt"],
        )
    """

    agent_type: str = "tech_researcher"
    input_schema = TechResearchInput
    output_schema = TechResearchOutput

    def analyze_file_for_tech(self, filepath: str) -> dict[str, list[str]]:
        """Analysoi yksittäisen tiedoston teknologioille."""
        path = Path(filepath)
        if not path.exists():
            return {"error": [f"Tiedostoa ei löydy: {filepath}"]}

        try:
            content = path.read_text(encoding="utf-8", errors="replace").lower()
            found: dict[str, list[str]] = {}

            for tech, keywords in TECH_KEYWORDS.items():
                matches = [kw for kw in keywords if kw in content]
                if matches:
                    found[tech] = matches

            return found
        except (OSError, PermissionError) as e:
            return {"error": [str(e)]}

    def _generate_recommendations(self, detected: dict[str, list[str]]) -> list[str]:
        """Generoi suositukset havaituista teknologioista."""
        recs: list[str] = []
        tech_names = set(detected.keys())

        # Työkalu
        if "pydantic" in tech_names and "pytest" in tech_names:
            recs.append("Hyödynnä Pydantic-malleja testaustapauksiin validoimiseen.")

        if "fastapi" in tech_names:
            recs.append("Käytä FastAPI:n TestClientia integraatiotestien ajamiseen.")
            if "sqlalchemy" not in tech_names:
                recs.append("Harkitse SQLAlchemy:n tai SQLModelin käyttöä ORM-integraatiota varten.")

        if "django" in tech_names:
            recs.append("Käytä Django:n omia testimoottoria ja fixturesia.")
            if "pytest" not in tech_names:
                recs.append("Lisää pytest Django-projektiin tehokkaampaan testaukseen.")

        if "react" in tech_names:
            recs.append("Käytä Jest tai React Testing Libraryia komponenttitestien ajamiseen.")

        if "openai" in tech_names and "langchain" in tech_names:
            recs.append("LangChain + OpenAI -yhdistelmään: muista rate-limitit ja token-kustannukset.")

        if "sqlalchemy" in tech_names:
            recs.append("Käytä Alembicia tietokantamallien versionhallintaan.")

        if not recs:
            recs.append("Ei erityisiä suosituksia. Projekti käyttää peruskirjastoja.")

        return recs

    def _check_missing_deps(self, detected: dict[str, list[str]]) -> list[str]:
        """Tarkistaa puuttuvat riippuvuudet standardikirjastosta."""
        missing: list[str] = []
        for tech in detected:
            if tech == "pyyaml" and "yaml" in detected.get(tech, []):
                missing.append("Varmista, että pyyaml on requirements.txt:ssä")
            if tech == "openai" and "langchain" not in detected:
                pass  # OpenAI voi olla itsenäinen

        return missing

    def _run(self, input_data: TechResearchInput) -> TechResearchOutput:
        """TechnologyResearcherAgentin päälogiikka."""
        project_files = input_data.project_files
        technologies = input_data.technologies or list(TECH_KEYWORDS.keys())

        # 1. Analysoi jokainen tiedosto
        detected: dict[str, list[str]] = {}
        for filepath in project_files:
            results = self.analyze_file_for_tech(filepath)
            for tech, matches in results.items():
                if tech != "error":
                    if tech in technologies or not technologies:
                        detected.setdefault(tech, [])
                        detected[tech].extend(matches)

        # Poimi duplikaatit
        for tech in detected:
            detected[tech] = sorted(set(detected[tech]))

        # 2. Generoi suositukset
        recommendations = self._generate_recommendations(detected)

        # 3. Tarkista puuttuvat riippuvuudet
        missing = self._check_missing_deps(detected)

        # 4. Jos tiedostoja ei annettu, yritetään skannata nykyisestä hakemistosta
        if not project_files:
            detected["no_files"] = []
            recommendations.append("Ei tiedostoja annettu — anna project_files tarkempaan analyysiin.")

        return TechResearchOutput(
            success=True,
            result={"detected": list(detected.keys()), "recommendation_count": len(recommendations)},
            message=f"Haettiin teknologioita {len(project_files)} tiedostosta. Löydetty {len(detected)} teknologiaa.",
            agent_type=self.agent_type,
            detected_technologies=detected,
            recommendations=recommendations,
            missing_dependencies=missing,
        )


__all__ = [
    "ResearcherAgent",
    "ResearchInput",
    "ResearchOutput",
    "TechnologyResearcherAgent",
    "TechResearchInput",
    "TechResearchOutput",
]
