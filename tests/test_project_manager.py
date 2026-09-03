"""
Testit ProjectManagerAgent-luokalle (agents/project_manager.py).
"""

import json
from pathlib import Path

import pytest

from agents.project_manager import ProjectManagerAgent, ProjectManagerInput, ProjectManagerOutput
from schemas.project import Priority, ProjectSpec, ProjectType, Requirement, RequirementList


@pytest.fixture
def manager(tmp_path):
    """Luo ProjectManagerAgentin tilapäiseen projektipolkuun."""
    return ProjectManagerAgent()


@pytest.fixture
def sample_spec_dict():
    """Palauttaa testi-projektin speksi dict-muodossa."""
    return {
        "name": "TestAPI",
        "type": "python-api",
        "description": "Testaustarkoitus API.",
        "version": "1.0.0",
        "author": "Testaaja",
        "requirements": {
            "requirements": [
                {"id": "REQ-001", "title": "User auth", "priority": "high", "tags": ["auth"]}
            ]
        },
        "file_structure": [],
    }


class TestProjectManagerInit:
    """Testit ProjectManagerAgentin alustukselle."""

    def test_agent_type(self, manager):
        """ProjectManagerin agent_type on 'project_manager'."""
        assert manager.agent_type == "project_manager"

    def test_input_schema(self, manager):
        """Käyttää ProjectManagerInput -mallia."""
        assert manager.input_schema == ProjectManagerInput

    def test_output_schema(self, manager):
        """Käyttää ProjectManagerOutput -mallia."""
        assert manager.output_schema == ProjectManagerOutput


class TestDefaultStructure:
    """Testit oletus-tiedostorakenteelle."""

    def test_python_api_structure(self, manager):
        """Python API -tyyppi saa oikean rakenteen."""
        dirs = manager._get_default_structure(ProjectType.PYTHON_API)
        assert "src/" in dirs
        assert "tests/" in dirs
        assert "docs/" in dirs
        assert "planning/" in dirs
        assert "src/api/" in dirs
        assert "src/models/" in dirs

    def test_web_app_structure(self, manager):
        """Web App -tyyppi saa komponenttikansion."""
        dirs = manager._get_default_structure(ProjectType.WEB_APP)
        assert "src/components/" in dirs
        assert "src/pages/" in dirs

    def test_cli_structure(self, manager):
        """CLI-tyyppi saa commands-kansion."""
        dirs = manager._get_default_structure(ProjectType.CLI)
        assert "src/commands/" in dirs

    def test_script_structure(self, manager):
        """Script-tyyppi ei saa ylimääräisiä kansioita."""
        dirs = manager._get_default_structure(ProjectType.SCRIPT)
        assert dirs.count("src/") == 1
        assert len(dirs) == 4  # Vain perus (src, tests, docs, planning)


class TestCreateFileStructure:
    """Testit tiedostorakenteen luomiselle."""

    def test_create_creates_base_dirs(self, manager, tmp_path, sample_spec_dict):
        """Peruskansiot luodaan."""
        spec = ProjectSpec(**sample_spec_dict)
        project_path = tmp_path / "project"
        created = manager._create_file_structure(spec, project_path)

        assert (project_path / "src").exists()
        assert (project_path / "tests").exists()
        assert (project_path / "docs").exists()
        assert (project_path / "planning").exists()
        assert "src/" in created

    def test_create_creates_custom_files(self, manager, tmp_path):
        """Määritellyt tiedostot luodaan."""
        spec = ProjectSpec(
            name="CustomProject",
            type=ProjectType.PYTHON_API,
            file_structure=[
                {"path": "src/main.py", "description": "Päämoduuli"},
                {"path": "src/config.py", "description": "Asetukset"},
            ],
        )
        project_path = tmp_path / "custom"
        created = manager._create_file_structure(spec, project_path)

        assert (project_path / "src" / "main.py").exists()
        assert (project_path / "src" / "config.py").exists()
        assert any(p.endswith("main.py") for p in created)
        assert any(p.endswith("config.py") for p in created)

    def test_create_file_content_has_description(self, manager, tmp_path):
        """Luodut tiedostot sisältävät kuvauksen."""
        spec = ProjectSpec(
            name="Test",
            type=ProjectType.LIBRARY,
            file_structure=[{"path": "src/module.py", "description": "Tämä on moduuli."}],
        )
        project_path = tmp_path / "test"
        manager._create_file_structure(spec, project_path)

        content = (project_path / "src" / "module.py").read_text()
        assert "moduuli" in content.lower()


class TestGenerateProjectMd:
    """Testit PROJECT.md-generoinnille."""

    def test_generates_markdown(self, manager):
        """PROJECT.md-generaatti tuottaa Markdownin."""
        spec = ProjectSpec(name="TestProject", description="Testausprojekti.", author="Testaaja")
        md = manager._generate_project_md(spec)

        assert "# TestProject" in md
        assert "python" in md.lower() or "unknown" in md.lower()
        assert "Testausprojekti" in md
        assert "Testaaja" in md

    def test_generates_with_requirements(self, manager):
        """PROJECT.md sisältää vaatimukset."""
        req_list = RequirementList(requirements=[
            Requirement(id="REQ-001", title="Testi vaatimus", priority=Priority.HIGH, tags=["test"])
        ])
        spec = ProjectSpec(
            name="WithReqs",
            type=ProjectType.PYTHON_API,
            requirements=req_list,
        )
        md = manager._generate_project_md(spec)
        assert "REQ-001" in md
        assert "Testi vaatimus" in md


class TestGenerateAgentsMd:
    """Testit AGENTS.md-generoinnille."""

    def test_generates_agents_doc(self, manager):
        """AGENTS.md-generaatti tuottaa Markdownin."""
        from schemas.project import ProjectPlan
        spec = ProjectSpec(name="AgentTest", type=ProjectType.PYTHON_API)
        plan = ProjectPlan(project_name="AgentTest", phases=["Setup", "API", "Test"])

        md = manager._generate_agents_md(spec, plan)
        assert "# Agentit" in md
        assert "ProjectManagerAgent" in md
        assert "DirectorAgent" in md
        assert "DeveloperAgent" in md

    def test_includes_phases(self, manager):
        """AGENTS.md sisältää suunnitelman faset."""
        from schemas.project import ProjectPlan
        spec = ProjectSpec(name="PhaseTest")
        plan = ProjectPlan(project_name="PhaseTest", phases=["Fase 1", "Fase 2", "Fase 3"])

        md = manager._generate_agents_md(spec, plan)
        assert "Fase 1" in md
        assert "Fase 2" in md


class TestGeneratePlan:
    """Testit suunnitelman generoinnille."""

    def test_python_api_plan(self, manager):
        """Python API -suunnitelma sisältää standardifaset."""
        spec = ProjectSpec(name="ApiTest", type=ProjectType.PYTHON_API)
        plan = manager._generate_plan(spec)

        assert plan.project_name == "ApiTest"
        assert "API-endpointit" in " ".join(plan.phases)

    def test_includes_requirement_phases(self, manager):
        """Suunnitelma sisältää vaatimuksista johtuen ylimääräiset faset."""
        req_list = RequirementList(requirements=[
            Requirement(id="REQ-001", title="Auth-moduuli", priority=Priority.HIGH),
            Requirement(id="REQ-002", title="Tietokanta-integraatio", priority=Priority.NORMAL),
        ])
        spec = ProjectSpec(
            name="ReqPlan",
            type=ProjectType.PYTHON_API,
            requirements=req_list,
        )
        plan = manager._generate_plan(spec)
        assert any("Auth-moduuli" in p for p in plan.phases)
        assert any("Tietokanta" in p for p in plan.phases)

    def test_unknown_type_plan(self, manager):
        """Tuntematon tyyppi saa oletusfaset."""
        spec = ProjectSpec(name="Generic", type=ProjectType.UNKNOWN)
        plan = manager._generate_plan(spec)

        assert "Projektin asetukset" in " ".join(plan.phases)


class TestRun:
    """Testit run()-metodille."""

    def test_run_with_spec_creates_project(self, manager, tmp_path, sample_spec_dict):
        """run() luo projektin annetuissa tiedoissa."""
        result = manager.run(
            task="Luo projekti",
            project_spec=sample_spec_dict,
            project_path=str(tmp_path / "created"),
            create_structure=True,
            generate_docs=True,
        )

        assert isinstance(result, ProjectManagerOutput)
        assert result.success is True
        assert result.project_name == "TestAPI"
        assert len(result.created_files) > 0
        assert (tmp_path / "created" / "PROJECT.md").exists()
        assert (tmp_path / "created" / "AGENTS.md").exists()
        assert (tmp_path / "created" / "requirements.json").exists()

    def test_run_with_minimal_input(self, manager, tmp_path):
        """run() toimii minimaarisen syötteen kanssa."""
        result = manager.run(
            task="Joku projekti",
            project_path=str(tmp_path / "minimal"),
            create_structure=False,
        )
        assert result.success is True
        assert result.project_name == "UntitledProject"

    def test_run_creates_requirements_json(self, manager, tmp_path, sample_spec_dict):
        """run() luo requirements.json -tiedoston."""
        manager.run(
            task="Luo projekti",
            project_spec=sample_spec_dict,
            project_path=str(tmp_path / "reqtest"),
            create_structure=True,
        )

        req_file = tmp_path / "reqtest" / "requirements.json"
        assert req_file.exists()
        data = json.loads(req_file.read_text())
        assert data["project_name"] == "TestAPI"
        assert data["requirements"][0]["title"] == "User auth"

    def test_run_output_has_plan(self, manager, tmp_path, sample_spec_dict):
        """run()-tuloste sisältää suunnitelman."""
        result = manager.run(
            task="Luo projekti",
            project_spec=sample_spec_dict,
            project_path=str(tmp_path / "plan"),
        )
        assert result.plan is not None
        assert "project_name" in result.plan
        assert result.plan["project_name"] == "TestAPI"

    def test_run_output_has_spec(self, manager, tmp_path, sample_spec_dict):
        """run()-tuloste sisältää speksin."""
        result = manager.run(
            task="Luo projekti",
            project_spec=sample_spec_dict,
            project_path=str(tmp_path / "spec"),
        )
        assert result.spec is not None
        assert result.spec["name"] == "TestAPI"

    def test_run_to_dict_serializes(self, manager, tmp_path, sample_spec_dict):
        """Projektin luomisen jälkeen se voidaan serialisoida."""
        result = manager.run(
            task="Testi",
            project_spec=sample_spec_dict,
            project_path=str(tmp_path / "serial"),
        )
        d = result.to_dict()
        assert d["agent_type"] == "project_manager"
        assert d["project_name"] == "TestAPI"
