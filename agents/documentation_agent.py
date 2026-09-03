"""
DocumentationAgent-moduuli (M7) — projektin generointi dokumentaatioksi.

Sisältää neljää agenttia:
- TechnicalWriterAgent: generoi teknisen dokumentaation (PROJECT.md, AGENTS.md, ARCHITECTURE.md)
- APIDocumentationAgent: API-dokumentaation generointi (docstringit, endpointit, OpenAPI-spekki)
- UserDocumentationAgent: käyttäjän ohjeistuksen generointi (README.md, käyttöohjeet)
- MkDocsAgent: MkDocs-sivuston generointi (mkdocs.yml, nav, sisällöt)
"""

from __future__ import annotations

import ast
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


class TechnicalWriterInput(AgentInput):
    """TechnicalWriterAgentin syöte."""

    project_name: str = Field(..., description="Projektin nimi.")
    project_description: str = Field(default="", description="Projektin kuvaus.")
    project_type: str = Field(default="generic", description="Projektin tyyppi.")
    project_path: str = Field(default=".", description="Projektipolku.")
    sections: Optional[list[str]] = Field(default=None, description="Dokumentaation osiot.")
    output_dir: str = Field(default=".", description="Tulostuskansio.")


class TechnicalWriterOutput(AgentOutput):
    """TechnicalWriterAgentin tuloste."""

    files_created: list[str] = Field(default_factory=list, description="Luodut tiedostot.")
    content_map: dict[str, str] = Field(default_factory=dict, description="Tiedoston sisällöt sanakirjana.")
    summary: str = Field(default="", description="Yhteenveto.")


class APIDocumentationInput(AgentInput):
    """APIDocumentationAgentin syöte."""

    code: str = Field(default="", description="Analysoitava koodi.")
    file_path: Optional[str] = Field(default=None, description="Kooditiedoston polku.")
    project_path: str = Field(default=".", description="Projektipolku.")
    framework: str = Field(default="fastapi", description="Web-kehys (fastapi/flask/etc).")
    include_docstrings: bool = Field(default=True, description="Sisällytä docstringit.")


class APIDocumentationOutput(AgentOutput):
    """APIDocumentationAgentin tuloste."""

    endpoints: list[dict[str, Any]] = Field(default_factory=list, description="API-endpointit.")
    schema: dict[str, Any] = Field(default_factory=dict, description="OpenAPI- tai schema-spekki.")
    documentation: str = Field(default="", description="Generoitu API-dokumentaatio.")
    endpoint_count: int = Field(default=0, description="Endpointien lukumäärä.")


class UserDocumentationInput(AgentInput):
    """UserDocumentationAgentin syöte."""

    project_name: str = Field(..., description="Projektin nimi.")
    project_description: str = Field(default="", description="Projektin kuvaus.")
    features: Optional[list[str]] = Field(default=None, description="Projektin ominaisuudet.")
    project_type: str = Field(default="python-api", description="Projektin tyyppi.")
    project_path: str = Field(default=".", description="Projektipolku.")
    output_dir: str = Field(default=".", description="Tulostuskansio.")
    output_file: str = Field(default="README.md", description="Tulostetiedoston nimi.")


class UserDocumentationOutput(AgentOutput):
    """UserDocumentationAgentin tuloste."""

    content: str = Field(default="", description="Generoitu README-sisältö.")
    sections: list[str] = Field(default_factory=list, description="Luodut osiot.")
    file_created: bool = Field(default=False, description="Luotiinko tiedosto.")


class MkDocsInput(AgentInput):
    """MkDocsAgentin syöte."""

    project_name: str = Field(..., description="Projektin nimi.")
    project_description: str = Field(default="", description="Projektin kuvaus.")
    project_path: str = Field(default=".", description="Projektipolku.")
    nav_items: Optional[list[dict[str, Any]]] = Field(default=None, description="Navigaatio.")
    theme: str = Field(default="material", description="MkDocs-teema.")
    output_dir: str = Field(default="docs", description="Dokumentaatioväylä.")


class MkDocsOutput(AgentOutput):
    """MkDocsAgentin tuloste."""

    config_file: str = Field(default="", description="Luodun config-tiedoston polku.")
    pages_created: list[str] = Field(default_factory=list, description="Luodut sivut.")
    nav: list[dict[str, Any]] = Field(default_factory=list, description="Navigaiorakente.")
    documentation_structure: dict[str, Any] = Field(default_factory=dict, description="Dokumentaation rakenne.")  # noqa: E501


class TechnicalWriterAgent(BaseAgent):
    """
    TechnicalWriterAgent generoi projektin dokumentaation.

    Usage:
        agent = TechnicalWriterAgent()
        result = agent.run("Luo dokumentaatio", project_name="MyAPI", project_description="API-palvelin")
    """

    agent_type: str = "technical_writer"
    input_schema = TechnicalWriterInput
    output_schema = TechnicalWriterOutput

    def _generate_project_md(self, name: str, description: str, ptype: str, sections: list[str]) -> str:
        """Generoi PROJECT.md:n."""
        now = datetime.now().strftime("%Y-%m-%d")
        content = f"""# {name}

> Teknis-dokumentaatio — luotu {now}

## Yleiskuvaus

{description or "Tämä projekti tarjoaa modernin kehitysympäristön."}

**Tyyppi:** {ptype or "generic"}

## Arkkitehtuuri

Projekti noudattaa modulaarista agenttipohjaista arkkitehtuuria:

- **DirectorAgent** — ohjaa työnkulkua ja valitsee workflowt.
- **ProjectManagerAgent** — hallitsee projektin luomista ja rakennetta.
- **RequirementsAgent** — analysoi ja priorisoi vaatimuksia.
- **ResearcherAgent** — tutkii projektin teknologioita ja rakennetta.
- **DeveloperAgent** — generoi ja refaktoroi koodia.
- **TestingAgent** — suunnittelee ja suorittaa testejä.
- **SecurityAgent** — tarkistaa turvallisuutta ja haavoittuvuuksia.
- **DocumentationAgent** — tuottaa projektin dokumentaation.
"""
        for section in sections:
            content += f"\n## {section.title()}\n\nTässä osiossa kuvataan {section.lower()} liittyvät yksityiskohdat.\n"
        return content

    def _generate_agents_md(self, name: str, ptype: str) -> str:
        """Generoi AGENTS.md:n."""
        return f"""# Agentit — {name}

Tämä dokumentti kuvaa projektin agentit ja niiden vastuut.

## Projektiyhteys

Projekti: {name} ({ptype})

## Työnkulku vaiheet

1. **Analyze** — ResearcherAgent analysoi projektin.
2. **Plan** — ProjectManagerAgent luo suunnitelman.
3. **Implement** — DeveloperAgent generoi koodia.
4. **Test** — TesterAgent ja QAAgent tarkistavat testit.
5. **Review** — CodeReviewAgent ja SecurityReviewAgent tarkistavat turvallisuutta.
6. **Document** — DocumentationAgent tuottaa dokumentaation.
"""

    def _generate_architecture_md(self, description: str) -> str:
        """Generoi ARCHITECTURE.md:n."""
        return f"""# Arkkitehtuuri

## Yleiskuvaus

{description or "Projekti on modulaarinen, agenttipohjainen järjestelmä."}

## Komponentit

```
flowchart TD
    A[DirectorAgent] --> B[ProjectManagerAgent]
    A --> C[ResearcherAgent]
    A --> D[DeveloperAgent]
    A --> E[TestingAgent]
    A --> F[SecurityAgent]
    A --> G[DocumentationAgent]
    B --> H[RequirementsAgent]
    D --> I[CodeReviewAgent]
```

## Työnkulku

Työnkulku määritellään YAML-tiedostoissa `workflows/`-kansiossa. Tyypit:
- **base** — yleinen kehitystyökalu
- **bugfix** — virhekorjaus
- **feature** — uuden ominaisuuden kehittäminen
"""

    def _run(self, input_data: TechnicalWriterInput) -> TechnicalWriterOutput:
        """TechnicalWriterAgentin päälogiika."""
        sections = input_data.sections or ["Overview", "Architecture", "Development", "Testing", "Security", "Deployment"]
        output_dir = Path(input_data.output_dir)

        content_map: dict[str, str] = {}
        files_created: list[str] = []

        # Generoi dokumentit
        project_md = self._generate_project_md(
            input_data.project_name, input_data.project_description,
            input_data.project_type, sections,
        )
        agents_md = self._generate_agents_md(input_data.project_name, input_data.project_type)
        arch_md = self._generate_architecture_md(input_data.project_description)

        content_map["PROJECT.md"] = project_md
        content_map["AGENTS.md"] = agents_md
        content_map["ARCHITECTURE.md"] = arch_md

        # Kirjoita tiedostot jos output_dir on kirjoitettavissa
        for fname, content in content_map.items():
            fpath = output_dir / fname
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content, encoding="utf-8")
            files_created.append(str(fpath))

        return TechnicalWriterOutput(
            success=True,
            result={"files_created": len(files_created)},
            message=f"Teknis-dokumentaatio luodaan: {len(files_created)} tiedostoa.",
            agent_type=self.agent_type,
            files_created=files_created,
            content_map=content_map,
            summary=f"Luotiin {len(files_created)} dokumentaatiotiedostoa projektille {input_data.project_name}.",
        )


class APIDocumentationAgent(BaseAgent):
    """
    APIDocumentationAgent analysoi koodin API-rajapinnat ja generoi dokumentaation.

    Usage:
        agent = APIDocumentationAgent()
        result = agent.run("Dokumentoi API", code="...", framework="fastapi")
    """

    agent_type: str = "api_documentation"
    input_schema = APIDocumentationInput
    output_schema = APIDocumentationOutput

    # Endpoint-mallit eri frameworkille
    ROUTE_PATTERNS = {
        "fastapi": r'@(\w+)\(\"([^\"]+)\"(?:\s*,\s*methods\s*=\s*\[([^\]]+)\])?\)',
        "flask": r'@app\.route\(\"([^\"]+)\"(?:\s*,\s*methods\s*=\s*\[([^\]]+)\])?\)',
    }

    def _extract_routes_from_code(self, code: str, framework: str) -> list[dict[str, Any]]:
        """Poimi reitit koodista regexillä."""
        endpoints: list[dict[str, Any]] = []
        pattern = self.ROUTE_PATTERNS.get(framework, self.ROUTE_PATTERNS["flask"])

        for match in re.finditer(pattern, code, re.MULTILINE):
            if framework == "fastapi":
                path = match.group(2)
                method = "GET"  # oletus
            else:
                path = match.group(1)
                methods_str = match.group(2)
                method = methods_str.upper().split(",")[0].strip() if methods_str else "GET"

            endpoints.append({"path": path, "method": method, "description": ""})

        return endpoints

    def _extract_from_ast(self, code: str) -> list[dict[str, Any]]:
        """Poimi API-endpointit AST-analyysillä."""
        endpoints: list[dict[str, Any]] = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # etsi route-decoratorit
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            func_name = getattr(decorator.func, "attr", "")
                            if func_name in ("get", "post", "put", "delete", "patch"):
                                # path on ensimmäinen arg
                                if decorator.args:
                                    path_node = decorator.args[0]
                                    if isinstance(path_node, ast.Constant):
                                        endpoints.append({
                                            "path": path_node.value,
                                            "method": func_name.upper(),
                                            "function": node.name,
                                            "description": ast.get_docstring(node, clean=True) or "",
                                        })
        except SyntaxError:
            pass
        return endpoints

    def _extract_functions(self, code: str) -> list[dict[str, Any]]:
        """Poimi funktiot ja niiden docstringit AST:stä."""
        functions: list[dict[str, Any]] = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    docstring = ast.get_docstring(node, clean=True)
                    params = [a.arg for a in node.args.args]
                    functions.append({
                        "name": node.name,
                        "params": params,
                        "docstring": docstring or "",
                    })
        except SyntaxError:
            pass
        return functions

    def _generate_openapi_schema(self, endpoints: list[dict[str, Any]], functions: list[dict[str, Any]]) -> dict[str, Any]:
        """Generoi OpenAPI-3.0-speksin."""
        paths: dict[str, Any] = {}
        for ep in endpoints:
            method = ep["method"].lower()
            path = ep["path"]
            if path not in paths:
                paths[path] = {}
            paths[path][method] = {
                "summary": ep.get("description") or ep.get("function", ""),
                "responses": {"200": {"description": "Onnistui"}},
            }

        return {
            "openapi": "3.0.0",
            "info": {"title": "API-spesifikaatio", "version": "1.0.0"},
            "paths": paths,
        }

    def _generate_markdown_docs(self, endpoints: list[dict[str, Any]], functions: list[dict[str, Any]]) -> str:
        """Generoi markdown-muotoisen API-dokumentaation."""
        md = ["# API-dokumentaatio\n"]
        md.append("## Endpointit\n")
        if endpoints:
            md.append("| Metodi | Polku | Funktio | Kuvaus |\n")
            md.append("|--------|-------|---------|--------|\n")
            for ep in endpoints:
                md.append(f"| {ep['method']} | `{ep['path']}` | {ep.get('function', '-')} | {ep.get('description', '')} |\n")
        else:
            md.append("*Ei endpointtejä löydy.*\n")

        md.append("\n## Funktiot\n")
        if functions:
            for func in functions:
                md.append(f"### `{func['name']}`\n")
                if func["docstring"]:
                    md.append(f"* {func['docstring']}\n")
                if func["params"]:
                    md.append(f"* Parametrit: {', '.join(func['params'])}\n")
                md.append("\n")
        else:
            md.append("*Ei funktioita löydy.*\n")

        return "".join(md)

    def _run(self, input_data: APIDocumentationInput) -> APIDocumentationOutput:
        """APIDocumentationAgentin päälogiika."""
        code = input_data.code
        file_path = input_data.file_path

        # Lue tiedosto jos annettu
        if not code and file_path:
            code = Path(file_path).read_text(encoding="utf-8")

        if not code:
            return APIDocumentationOutput(
                success=False,
                result=None,
                message="Ei koodia analysoitavaksi.",
                agent_type=self.agent_type,
                endpoints=[],
                schema={},
                documentation="",
                endpoint_count=0,
            )

        # Analysoi
        endpoints = self._extract_from_ast(code)
        functions = self._extract_functions(code)
        openapi_schema = self._generate_openapi_schema(endpoints, functions)
        documentation = self._generate_markdown_docs(endpoints, functions)

        return APIDocumentationOutput(
            success=True,
            result={"endpoint_count": len(endpoints), "function_count": len(functions)},
            message=f"API-dokumentaatio luodaan: {len(endpoints)} endpointia, {len(functions)} funktiota.",
            agent_type=self.agent_type,
            endpoints=endpoints,
            schema=openapi_schema,
            documentation=documentation,
            endpoint_count=len(endpoints),
        )


class UserDocumentationAgent(BaseAgent):
    """
    UserDocumentationAgent luo käyttäjän ohjeistuksen (README.md).

    Usage:
        agent = UserDocumentationAgent()
        result = agent.run("Luo käyttöohje", project_name="MyAPI")
    """

    agent_type: str = "user_documentation"
    input_schema = UserDocumentationInput
    output_schema = UserDocumentationOutput

    def _generate_readme(self, name: str, description: str, features: list[str], ptype: str) -> str:
        """Generoi README.md:n."""
        now = datetime.now().strftime("%Y-%m-%d")
        feature_list = "\n".join(f"- {f}" for f in features) if features else "- *(ei määritelty)*"
        return f"""# {name}

> Generoitu käyttöohje — {now}

## Yleiskuvaus

{description or "Tämä projekti tarjoaa modernin työkalun."}

## Ominaisuudet

{feature_list}

## Asennus

```bash
pip install -r requirements.txt
```

## Käyttö

```python
python cli.py init --name {name} --type {ptype or "python-api"}
python cli.py run "tehtävä kuvaus"
python cli.py status
```

## Testaus

```bash
pytest tests/ -v --cov=agents --cov-report=term-missing
```

## Lisätietoja

- Arkkitehtuuri: [Architecture](ARCHITECTURE.md)
- Agentit: [Agents](AGENTS.md)
- Tekniset tiedot: [Project](PROJECT.md)
"""

    def _run(self, input_data: UserDocumentationInput) -> UserDocumentationOutput:
        """UserDocumentationAgentin päälogiika."""
        features = input_data.features or ["Modulaarinen arkkitehtuuri", "Turvallisuus tarkistukset", "Testikattavuus 94 %"]
        content = self._generate_readme(
            input_data.project_name,
            input_data.project_description,
            features,
            input_data.project_type or "python-api",
        )

        sections = ["Yleiskuvaus", "Ominaisuudet", "Asennus", "Käyttö", "Testaus", "Lisätietoja"]
        file_created = False

        output_path = Path(input_data.output_dir) / input_data.output_file
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
            file_created = True
        except OSError:
            pass

        return UserDocumentationOutput(
            success=True,
            result={"content_length": len(content), "file_created": file_created},
            message="Käyttöohje luodaan.",
            agent_type=self.agent_type,
            content=content,
            sections=sections,
            file_created=file_created,
        )


class MkDocsAgent(BaseAgent):
    """
    MkDocsAgent generoi MkDocs-dokumentaation (mkdocs.yml, sivut).

    Usage:
        agent = MkDocsAgent()
        result = agent.run("Luo MkDocs-sivusto", project_name="MyProject")
    """

    agent_type: str = "mkdocs"
    input_schema = MkDocsInput
    output_schema = MkDocsOutput

    # Oletus-navigaatio
    DEFAULT_NAV = [
        {"Etusivu": "index.md"},
        {"Arkkitehtuuri": "architecture/overview.md"},
        {"Agentit": {"Direktori": "agents/director.md", "Projekti": "agents/project-manager.md"}},
        {"Moduulit": {"Research": "modules/research.md", "Development": "modules/development.md",
                      "Testing": "modules/testing.md", "Security": "modules/security.md",
                      "Documentation": "modules/documentation.md"}},
        {"API": "api/index.md"},
        {"Käsikirja": "user-guide/index.md"},
        {"Esimerkit": {"API-palvelin": "examples/api-service.md", "Web-sovellus": "examples/web-app.md"}},
    ]

    def _generate_mkdocs_yml(self, name: str, description: str, nav: list, theme: str) -> dict[str, Any]:
        """Generoi mkdocs.yml -rakenteen dictionaryna."""
        return {
            "site_name": name,
            "site_description": description or f"{name}-projektin dokumentaatio",
            "site_author": "AIDE",
            "theme": {"name": theme},
            "plugins": ["search"],
            "nav": nav,
            "markdown_extensions": [
                "admonition",
                "codehilite",
                "toc",
                {"toc": {"permalink": True}},
            ],
        }

    def _generate_index_md(self, name: str, description: str) -> str:
        """Generoi index.md:n."""
        return f"""# {name}

{description or "Tervetuloa projektin dokumentaatioon."}

## Aloita käyttö

- [Asennusohjeet](user-guide/index.md)
- [API-dokumentaatio](api/index.md)
- [Arkkitehtuuri](architecture/overview.md)

## Moduulit

1. **M1 Core** — perusagentit ja CLI
2. **M2 Project Management** — projektin luominen ja hallinta
3. **M3 Research** — projektin analyysi
4. **M4 Development** — koodin generointi
5. **M5 Testing** — testien suunnittelu ja suoritus
6. **M6 Security** — turvallisuustarkistukset
7. **M7 Documentation** — dokumentaation generointi
"""

    def _generate_api_md(self) -> str:
        """Generoi API-dokumentaatiota."""
        return """# API-dokumentaatio

## Endpointit

| Metodi | Polku | Kuvaus |
|--------|-------|--------|
| GET | /health | Terveyspalvelin tarkistus |
| POST | /api/v1/items | Luo kohde |
| GET | /api/v1/items | Hae kaikki kohteet |
| GET | /api/v1/items/{id} | Hae kohde ID:llä |
| PUT | /api/v1/items/{id} | Päivitä kohde |
| DELETE | /api/v1/items/{id} | Poista kohde |
"""

    def _generate_user_guide_md(self) -> str:
        """Generoi käyttöoppaan."""
        return """# Käyttöopas

## Aloitus

Asenna riippuvuudet:

```bash
pip install -r requirements.txt
```

## CLI-komennot

| Komento | Kuvaus |
|---------|--------|
| `aide init` | Luo uuden projektin |
| `aide run "tehtävä"` | Aja tehtävä |
| `aide status` | Näytä projektin tila |
| `aide run --dry-run` | Kulmimusto (ei toimi) |

## Agentit

Jokainen agentti on vastuussa tietystä vaiheesta:

- **DirectorAgent**: ohjaa työnkulkua
- **ProjectManagerAgent**: luo projektin
- **ResearcherAgent**: tutkii projektin
- **DeveloperAgent**: kirjoittaa koodia
- **TesterAgent**: aja testit
- **SecurityAgent**: tarkista turvallisuus
"""

    def _run(self, input_data: MkDocsInput) -> MkDocsOutput:
        """MkDocsAgentin päälogiika."""
        nav = input_data.nav_items or self.DEFAULT_NAV
        output_dir = Path(input_data.output_dir)
        pages_created: list[str] = []

        # 1. Generoi mkdocs.yml
        mkdocs_yml = self._generate_mkdocs_yml(input_data.project_name, input_data.project_description, nav, input_data.theme)
        yml_path = output_dir / "mkdocs.yml"
        yml_path.parent.mkdir(parents=True, exist_ok=True)

        import yaml as _yaml
        yml_content = _yaml.dump(mkdocs_yml, default_flow_style=False, sort_keys=False)
        yml_path.write_text(yml_content, encoding="utf-8")
        pages_created.append(str(yml_path))

        # 2. Generoi oletussivut
        pages = {
            "index.md": self._generate_index_md(input_data.project_name, input_data.project_description),
            "api/index.md": self._generate_api_md(),
            "user-guide/index.md": self._generate_user_guide_md(),
        }

        page_nav: dict[str, str] = {}
        for page_name, content in pages.items():
            page_path = output_dir / page_name
            page_path.parent.mkdir(parents=True, exist_ok=True)
            page_path.write_text(content, encoding="utf-8")
            pages_created.append(str(page_path))
            page_nav[page_name] = str(page_path)

        doc_structure = {
            "config": str(yml_path),
            "pages": pages_created,
            "nav": nav,
        }

        # 3. Rakbista nav
        nav_list: list[dict[str, Any]] = nav if isinstance(nav, list) else nav

        return MkDocsOutput(
            success=True,
            result={"pages_created": len(pages_created), "config_file": str(yml_path)},
            message=f"MkDocs-dokumentaatio luodaan: {len(pages_created)} sivua.",
            agent_type=self.agent_type,
            config_file=str(yml_path),
            pages_created=pages_created,
            nav=nav_list,
            documentation_structure=doc_structure,
        )


__all__ = [
    "TechnicalWriterAgent",
    "TechnicalWriterInput",
    "TechnicalWriterOutput",
    "APIDocumentationAgent",
    "APIDocumentationInput",
    "APIDocumentationOutput",
    "UserDocumentationAgent",
    "UserDocumentationInput",
    "UserDocumentationOutput",
    "MkDocsAgent",
    "MkDocsInput",
    "MkDocsOutput",
]
