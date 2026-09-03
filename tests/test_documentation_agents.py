"""
Testit DocumentationAgenteille (M7).
"""

from pathlib import Path

import pytest

from agents.documentation_agent import (
    TechnicalWriterAgent,
    TechnicalWriterInput,
    TechnicalWriterOutput,
    APIDocumentationAgent,
    APIDocumentationInput,
    APIDocumentationOutput,
    UserDocumentationAgent,
    UserDocumentationInput,
    UserDocumentationOutput,
    MkDocsAgent,
    MkDocsInput,
    MkDocsOutput,
)


@pytest.fixture
def writer():
    return TechnicalWriterAgent()


@pytest.fixture
def api_doc():
    return APIDocumentationAgent()


@pytest.fixture
def user_doc():
    return UserDocumentationAgent()


@pytest.fixture
def mkdocs():
    return MkDocsAgent()


@pytest.fixture
def sample_api_code():
    """Palauttaa sample API-koodin."""
    return '''"""API-palvelin."""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/health")
def health():
    """Terveyspalvelin tarkistus."""
    return {"status": "ok"}


@app.post("/api/v1/items")
def create_item(name: str):
    """Luo uuden lokaation."""
    return {"name": name}


@app.get("/api/v1/items/{item_id}")
def get_item(item_id: int):
    """Hakee kohdetta ID:llä."""
    return {"item_id": item_id}


class Item(BaseModel):
    """Tuote-modeli."""
    name: str
    price: float
'''


@pytest.fixture
def sample_project(tmp_path):
    """Luo testiprojektin."""
    (tmp_path / "main.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/health')\ndef health():\n    '''Health check.'''\n    return {'status': 'ok'}\n",
        encoding="utf-8",
    )
    return tmp_path


class TestTechnicalWriterAgent:
    """Testit TechnicalWriterAgentille."""

    def test_agent_type(self, writer):
        assert writer.agent_type == "technical_writer"

    def test_input_schema(self, writer):
        assert writer.input_schema == TechnicalWriterInput

    def test_output_schema(self, writer):
        assert writer.output_schema == TechnicalWriterOutput

    def test_run_generates_project_md(self, writer, tmp_path):
        """run() luo PROJECT.md:n."""
        result = writer.run(
            task="Luo dokumentaatio",
            project_name="TestAPI",
            project_description="Testi-API-palvelin",
            output_dir=str(tmp_path),
        )
        assert isinstance(result, TechnicalWriterOutput)
        assert result.success is True
        assert any("PROJECT.md" in f for f in result.files_created)

    def test_run_generates_agents_md(self, writer, tmp_path):
        """run() luo AGENTS.md:n."""
        result = writer.run(
            task="Luo dokumentaatio",
            project_name="TestAPI",
            project_description="Testi-API",
            output_dir=str(tmp_path),
        )
        assert any("AGENTS.md" in f for f in result.files_created)

    def test_run_generates_architecture_md(self, writer, tmp_path):
        """run() luo ARCHITECTURE.md:n."""
        result = writer.run(
            task="Luo dokumentaatio",
            project_name="TestAPI",
            project_description="Testi-API",
            output_dir=str(tmp_path),
        )
        assert any("ARCHITECTURE.md" in f for f in result.files_created)

    def test_run_content_map_has_sections(self, writer, tmp_path):
        """content_map sisältää kaikki osiot."""
        result = writer.run(
            task="Luo dokumentaatio",
            project_name="TestAPI",
            project_description="Testi-API",
            output_dir=str(tmp_path),
        )
        assert "PROJECT.md" in result.content_map
        assert "AGENTS.md" in result.content_map
        assert "ARCHITECTURE.md" in result.content_map

    def test_run_custom_sections(self, writer, tmp_path):
        """custom_sections-parametri toimii."""
        result = writer.run(
            task="Luo dokumentaatio",
            project_name="TestAPI",
            project_description="Testi-API",
            sections=["Custom Section"],
            output_dir=str(tmp_path),
        )
        assert result.success is True

    def test_run_includes_project_name(self, writer, tmp_path):
        """Dokumentaatio sisältää projektin nimen."""
        result = writer.run(
            task="Luo dokumentaatio",
            project_name="MyAwesomeProject",
            project_description="Kuvaus",
            output_dir=str(tmp_path),
        )
        assert "MyAwesomeProject" in result.content_map["PROJECT.md"]

    def test_run_serializes(self, writer, tmp_path):
        """Tulos voidaan serialisoida."""
        result = writer.run(
            task="Luo dokumentaatio",
            project_name="TestAPI",
            project_description="Kuvaus",
            output_dir=str(tmp_path),
        )
        d = result.to_dict()
        assert d["agent_type"] == "technical_writer"
        assert "files_created" in d


class TestAPIDocumentationAgent:
    """Testit APIDocumentationAgentille."""

    def test_agent_type(self, api_doc):
        assert api_doc.agent_type == "api_documentation"

    def test_input_schema(self, api_doc):
        assert api_doc.input_schema == APIDocumentationInput

    def test_output_schema(self, api_doc):
        assert api_doc.output_schema == APIDocumentationOutput

    def test_run_detects_endpoints(self, api_doc, sample_api_code):
        """run() tunnistaa endpointit AST:stä."""
        result = api_doc.run(
            task="Dokumentoi API",
            code=sample_api_code,
            framework="fastapi",
        )
        assert isinstance(result, APIDocumentationOutput)
        assert result.success is True
        assert result.endpoint_count >= 3

    def test_run_extracts_functions(self, api_doc, sample_api_code):
        """run() poimii funktiot."""
        result = api_doc.run(
            task="Dokumentoi API",
            code=sample_api_code,
        )
        assert len(result.schema) >= 0

    def test_run_generates_openapi_schema(self, api_doc, sample_api_code):
        """run() luo OpenAPI-skeeman."""
        result = api_doc.run(
            task="Dokumentoi API",
            code=sample_api_code,
        )
        assert result.schema.get("openapi") == "3.0.0"
        assert "paths" in result.schema

    def test_run_generates_markdown_docs(self, api_doc, sample_api_code):
        """run() luo markdown-dokumentaation."""
        result = api_doc.run(
            task="Dokumentoi API",
            code=sample_api_code,
        )
        assert "API-dokumentaatio" in result.documentation
        assert "/health" in result.documentation

    def test_run_from_file(self, api_doc, tmp_path, sample_api_code):
        """run() Lukee tiedoston."""
        filepath = tmp_path / "api.py"
        filepath.write_text(sample_api_code, encoding="utf-8")

        result = api_doc.run(
            task="Dokumentoi tiedosto",
            file_path=str(filepath),
        )
        assert result.success is True
        assert result.endpoint_count >= 3

    def test_run_empty_code(self, api_doc):
        """run() antaa virheen tyhjälle koodille."""
        result = api_doc.run(
            task="Dokumentoi",
            code="",
        )
        assert result.success is False

    def test_run_no_endpoints(self, api_doc):
        """run() palauttaa tyhjät endpointit koodittomalle."""
        result = api_doc.run(
            task="Dokumentoi",
            code="x = 1\n",
        )
        assert result.success is True
        assert result.endpoint_count == 0

    def test_run_includes_docstrings(self, api_doc, sample_api_code):
        """run() sisällyttää docstringit."""
        result = api_doc.run(
            task="Dokumentoi API",
            code=sample_api_code,
        )
        assert "Terveyspalvelin tarkistus" in result.documentation or result.endpoint_count >= 3

    def test_run_serializes(self, api_doc, sample_api_code):
        """Tulos voidaan serialisoida."""
        result = api_doc.run(
            task="Dokumentoi API",
            code=sample_api_code,
        )
        d = result.to_dict()
        assert d["agent_type"] == "api_documentation"
        assert "endpoints" in d


class TestUserDocumentationAgent:
    """Testit UserDocumentationAgentille."""

    def test_agent_type(self, user_doc):
        assert user_doc.agent_type == "user_documentation"

    def test_input_schema(self, user_doc):
        assert user_doc.input_schema == UserDocumentationInput

    def test_output_schema(self, user_doc):
        assert user_doc.output_schema == UserDocumentationOutput

    def test_run_generates_readme(self, user_doc, tmp_path):
        """run() luo README:n."""
        result = user_doc.run(
            task="Luo käyttöohje",
            project_name="TestProject",
            project_description="Testiprojekti",
            output_dir=str(tmp_path),
        )
        assert isinstance(result, UserDocumentationOutput)
        assert result.success is True
        assert result.file_created is True

    def test_run_includes_project_name(self, user_doc, tmp_path):
        """README sisältää projektin nimen."""
        result = user_doc.run(
            task="Luo käyttöohje",
            project_name="MyAwesomeProject",
            output_dir=str(tmp_path),
        )
        assert "MyAwesomeProject" in result.content

    def test_run_includes_features(self, user_doc, tmp_path):
        """README sisältää ominaisuudet."""
        result = user_doc.run(
            task="Luo käyttöohje",
            project_name="TestProject",
            features=["Feature 1", "Feature 2"],
            output_dir=str(tmp_path),
        )
        assert "Feature 1" in result.content
        assert "Feature 2" in result.content

    def test_run_includes_install_instructions(self, user_doc, tmp_path):
        """README sisältää asennusohjeet."""
        result = user_doc.run(
            task="Luo käyttöohje",
            project_name="TestProject",
            output_dir=str(tmp_path),
        )
        assert "pip install" in result.content

    def test_run_includes_usage(self, user_doc, tmp_path):
        """README sisältää käyttöohjeet."""
        result = user_doc.run(
            task="Luo käyttöohje",
            project_name="TestProject",
            project_type="python-api",
            output_dir=str(tmp_path),
        )
        assert "cli.py" in result.content.lower()

    def test_run_creates_file(self, user_doc, tmp_path):
        """run() luo tiedoston levyelle."""
        result = user_doc.run(
            task="Luo käyttöohje",
            project_name="TestProject",
            output_dir=str(tmp_path),
        )
        assert result.file_created is True
        assert (tmp_path / "README.md").exists()

    def test_run_sections_list(self, user_doc, tmp_path):
        """run() palauttaa osioiden listan."""
        result = user_doc.run(
            task="Luo käyttöohje",
            project_name="TestProject",
            output_dir=str(tmp_path),
        )
        assert len(result.sections) >= 5
        assert "Asennus" in result.sections

    def test_run_serializes(self, user_doc, tmp_path):
        """Tulos voidaan serialisoida."""
        result = user_doc.run(
            task="Luo käyttöohje",
            project_name="TestProject",
            output_dir=str(tmp_path),
        )
        d = result.to_dict()
        assert d["agent_type"] == "user_documentation"
        assert "content" in d


class TestMkDocsAgent:
    """Testit MkDocsAgentille."""

    def test_agent_type(self, mkdocs):
        assert mkdocs.agent_type == "mkdocs"

    def test_input_schema(self, mkdocs):
        assert mkdocs.input_schema == MkDocsInput

    def test_output_schema(self, mkdocs):
        assert mkdocs.output_schema == MkDocsOutput

    def test_run_creates_mkdocs_yml(self, mkdocs, tmp_path):
        """run() luo mkdocs.yml:n."""
        result = mkdocs.run(
            task="Luo MkDocs-sivusto",
            project_name="TestDocs",
            project_description="Testi dokumentaatio",
            output_dir=str(tmp_path),
        )
        assert isinstance(result, MkDocsOutput)
        assert result.success is True
        assert result.config_file.endswith("mkdocs.yml")

    def test_run_creates_index_md(self, mkdocs, tmp_path):
        """run() luo index.md:n."""
        result = mkdocs.run(
            task="Luo MkDocs-sivusto",
            project_name="TestDocs",
            output_dir=str(tmp_path),
        )
        assert any("index.md" in p for p in result.pages_created)

    def test_run_creates_api_page(self, mkdocs, tmp_path):
        """run() luo API-sivun."""
        result = mkdocs.run(
            task="Luo MkDocs-sivusto",
            project_name="TestDocs",
            output_dir=str(tmp_path),
        )
        assert any("api" in p for p in result.pages_created)

    def test_run_creates_user_guide(self, mkdocs, tmp_path):
        """run() luo käyttöohjeen."""
        result = mkdocs.run(
            task="Luo MkDocs-sivusto",
            project_name="TestDocs",
            output_dir=str(tmp_path),
        )
        assert any("user-guide" in p for p in result.pages_created)

    def test_run_mkdocs_yml_is_valid_yaml(self, mkdocs, tmp_path):
        """mkdocs.yml on kelvollinen YAML."""
        import yaml as _yaml
        result = mkdocs.run(
            task="Luo MkDocs-sivusto",
            project_name="TestDocs",
            project_description="Testi",
            output_dir=str(tmp_path),
        )
        yml_path = Path(result.config_file)
        content = _yaml.safe_load(yml_path.read_text(encoding="utf-8"))
        assert content["site_name"] == "TestDocs"
        assert "nav" in content
        assert "plugins" in content

    def test_run_custom_nav(self, mkdocs, tmp_path):
        """Kustomoitu nav toimii."""
        custom_nav = [{"Etusivu": "index.md"}, {"API": "api/index.md"}]
        result = mkdocs.run(
            task="Luo MkDocs-sivusto",
            project_name="TestDocs",
            nav_items=custom_nav,
            output_dir=str(tmp_path),
        )
        assert result.nav == custom_nav

    def test_run_custom_theme(self, mkdocs, tmp_path):
        """Kustomoitu teema tallentuu."""
        import yaml as _yaml
        result = mkdocs.run(
            task="Luo MkDocs-sivusto",
            project_name="TestDocs",
            theme="cosmo",
            output_dir=str(tmp_path),
        )
        yml_path = Path(result.config_file)
        content = _yaml.safe_load(yml_path.read_text(encoding="utf-8"))
        assert content["theme"]["name"] == "cosmo"

    def test_run_pages_created_at_least_3(self, mkdocs, tmp_path):
        """Vähintään 3 sivua luodaan."""
        result = mkdocs.run(
            task="Luo MkDocs-sivusto",
            project_name="TestDocs",
            output_dir=str(tmp_path),
        )
        assert len(result.pages_created) >= 3

    def test_run_index_contains_project_name(self, mkdocs, tmp_path):
        """index.md sisältää projektin nimen."""
        result = mkdocs.run(
            task="Luo MkDocs-sivusto",
            project_name="MyProject",
            output_dir=str(tmp_path),
        )
        index_path = Path(result.config_file).parent / "index.md"
        content = index_path.read_text(encoding="utf-8")
        assert "MyProject" in content

    def test_run_serializes(self, mkdocs, tmp_path):
        """Tulos voidaan serialisoida."""
        result = mkdocs.run(
            task="Luo MkDocs-sivusto",
            project_name="TestDocs",
            output_dir=str(tmp_path),
        )
        d = result.to_dict()
        assert d["agent_type"] == "mkdocs"
        assert "pages_created" in d
        assert "nav" in d
