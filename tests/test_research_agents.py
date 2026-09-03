"""
Testit ResearchAgentille ja TechnologyResearcherAgentille (M3).
"""

import json
from pathlib import Path

import pytest

from agents.researcher_agent import (
    ResearcherAgent,
    ResearchInput,
    ResearchOutput,
    TechnologyResearcherAgent,
    TechResearchInput,
    TechResearchOutput,
)


@pytest.fixture
def researcher():
    return ResearcherAgent()


@pytest.fixture
def tech_researcher():
    return TechnologyResearcherAgent()


@pytest.fixture
def sample_project(tmp_path):
    """Luo testiprojektin analysointia varten."""
    # Päämoduuli
    (tmp_path / "main.py").write_text(
        '''"""Päämoduuli."""
import os
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

def get_user(user_id: int):
    """Hakee käyttäjän."""
    return {"id": user_id}

def create_user(name: str):
    """Luo uuden käyttäjän."""
    return {"name": name}
''',
        encoding="utf-8",
    )

    # Testitiedosto
    (tmp_path / "test_main.py").write_text(
        '''import pytest
from main import app

def test_get_user():
    assert True
''',
        encoding="utf-8",
    )

    # Tiedostotilatuksia
    (tmp_path / "README.md").write_text("# TestProject\n\nTestausprojekti.", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("fastapi\npydantic\npytest\n", encoding="utf-8")

    return tmp_path


class TestResearcherAgentInit:
    """Testit init-luonnille."""

    def test_agent_type(self, researcher):
        assert researcher.agent_type == "researcher"

    def test_input_schema(self, researcher):
        assert researcher.input_schema == ResearchInput

    def test_output_schema(self, researcher):
        assert researcher.output_schema == ResearchOutput


class TestFileScanning:
    """Testit tiedostojen skannaukselle."""

    def test_scan_finds_python_files(self, researcher, sample_project):
        """Skannaus löytää .py-tiedostot."""
        files = researcher._scan_files(sample_project, [".py"], max_files=100)
        assert len(files) == 2  # main.py + test_main.py

    def test_scan_with_extensions(self, researcher, sample_project):
        """Skannaus kunnioittaa tiedostotyyppejä."""
        files = researcher._scan_files(sample_project, [".md"], max_files=100)
        assert len(files) == 1
        assert files[0].name == "README.md"

    def test_scan_all_extensions(self, researcher, sample_project):
        """Kaikki tiedostot tulevat ilman rajoitteita."""
        files = researcher._scan_files(sample_project, None, max_files=100)
        assert len(files) == 4

    def test_scan_skips_git_and_cache(self, researcher, tmp_path):
        """Skannaus ohittaa .git- ja __pycache__-kansiot."""
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("git", encoding="utf-8")
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "cache.pyc").write_text("cached", encoding="utf-8")
        (tmp_path / "app.py").write_text("print('hello')", encoding="utf-8")

        files = researcher._scan_files(tmp_path, [".py"], max_files=100)
        assert len(files) == 1
        assert files[0].name == "app.py"

    def test_scan_max_files_limit(self, researcher, tmp_path):
        """max_files rajoittaa löydösten määrää."""
        for i in range(20):
            (tmp_path / f"file{i}.py").write_text("x", encoding="utf-8")

        files = researcher._scan_files(tmp_path, [".py"], max_files=5)
        assert len(files) == 5

    def test_scan_nonexistent_path(self, researcher, tmp_path):
        """Ei olemassa oleva polku palauttaa tyhjän listan."""
        files = researcher._scan_files(tmp_path / "nonexistent", [".py"], max_files=100)
        assert files == []


class TestPythonAnalysis:
    """Testit Python-tiedostojen analysoinnille."""

    def test_analyze_python_finds_classes(self, researcher, sample_project):
        """Analyysi löytää luokat."""
        result = researcher._analyze_python_file(sample_project / "main.py")
        class_names = [c["name"] for c in result["classes"]]
        assert "User" in class_names

    def test_analyze_python_finds_functions(self, researcher, sample_project):
        """Analyysi löytää funktiot."""
        result = researcher._analyze_python_file(sample_project / "main.py")
        func_names = [f["name"] for f in result["functions"]]
        assert "get_user" in func_names
        assert "create_user" in func_names

    def test_analyze_python_finds_imports(self, researcher, sample_project):
        """Analyysi löytää importit."""
        result = researcher._analyze_python_file(sample_project / "main.py")
        assert "os" in result["imports"]
        assert "pydantic" in result["imports"]
        assert "fastapi" in result["imports"]

    def test_analyze_python_invalid_syntax(self, researcher, tmp_path):
        """Virheellinen syntaksi ei kaata analyysiä."""
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("def broken(\n", encoding="utf-8")
        result = researcher._analyze_python_file(bad_file)
        assert "error" in result

    def test_analyze_python_line_count(self, researcher, sample_project):
        """Linjamäärä lasketaan oikein."""
        result = researcher._analyze_python_file(sample_project / "main.py")
        assert result["lines"] > 0


class TestTechnologyDetection:
    """Testit teknologioiden havaitsemiselle."""

    def test_detect_fastapi(self, researcher, sample_project):
        """FastAPI tunnistetaan."""
        files = researcher._scan_files(sample_project, None, max_files=100)
        techs = researcher._detect_technologies(files)
        assert "fastapi" in techs

    def test_detect_pydantic(self, researcher, sample_project):
        """Pydantic tunnistetaan."""
        files = researcher._scan_files(sample_project, None, max_files=100)
        techs = researcher._detect_technologies(files)
        assert "pydantic" in techs

    def test_detect_pytest(self, researcher, sample_project):
        """Pytest tunnistetaan testitiedostoista."""
        files = researcher._scan_files(sample_project, None, max_files=100)
        techs = researcher._detect_technologies(files)
        assert "pytest" in techs

    def test_detect_no_technologies(self, researcher, tmp_path):
        """Tyhjästä projektista ei löydy teknologioita."""
        (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
        files = researcher._scan_files(tmp_path, [".py"], max_files=100)
        techs = researcher._detect_technologies(files)
        assert techs == []


class TestStructureBuilding:
    """Testit rakenteen rakentamiselle."""

    def test_build_structure_returns_dict(self, researcher, sample_project):
        """Rakenne on dictionary."""
        files = researcher._scan_files(sample_project, None, max_files=100)
        structure = researcher._build_structure(files, sample_project)
        assert isinstance(structure, dict)
        assert structure["name"] == sample_project.name
        assert "children" in structure


class TestRun:
    """Testit run()-metodille."""

    def test_run_analyzes_project(self, researcher, sample_project):
        """run() analysoi projektin oikein."""
        result = researcher.run(
            task="Analysoi tämä projekti",
            project_path=str(sample_project),
            file_extensions=[".py", ".md", ".txt"],
        )
        assert isinstance(result, ResearchOutput)
        assert result.success is True
        assert result.file_count == 4
        assert result.project_name == sample_project.name
        assert len(result.functions) >= 2
        assert len(result.classes) >= 1
        assert "fastapi" in result.technologies

    def test_run_with_extensions(self, researcher, sample_project):
        """run() kunnioittaa tiedostotyyppejä."""
        result = researcher.run(
            task="Analysoi Python-tiedostot",
            project_path=str(sample_project),
            file_extensions=[".py"],
        )
        assert result.file_count == 2

    def test_run_minimal_project(self, researcher, tmp_path):
        """run() toimii tyhjässä projekissa."""
        result = researcher.run(
            task="Analysoi",
            project_path=str(tmp_path),
        )
        assert result.success is True
        assert result.file_count == 0

    def test_run_serializes(self, researcher, sample_project):
        """run()-tulos voidaan serialisoida."""
        result = researcher.run(
            task="Analysoi projekti",
            project_path=str(sample_project),
        )
        d = result.to_dict()
        assert d["agent_type"] == "researcher"
        assert d["project_name"] == sample_project.name


class TestTechnologyResearcherAgent:
    """Testit TechnologyResearcherAgentille."""

    def test_agent_type(self, tech_researcher):
        assert tech_researcher.agent_type == "tech_researcher"

    def test_input_schema(self, tech_researcher):
        assert tech_researcher.input_schema == TechResearchInput

    def test_output_schema(self, tech_researcher):
        assert tech_researcher.output_schema == TechResearchOutput

    def test_run_detects_technologies(self, tech_researcher, sample_project):
        """run() tunnistaa teknologiat tiedostoista."""
        result = tech_researcher.run(
            task="Tutki projektitiedostot",
            project_files=[str(sample_project / "main.py")],
        )
        assert isinstance(result, TechResearchOutput)
        assert result.success is True
        assert "pydantic" in result.detected_technologies
        assert "fastapi" in result.detected_technologies

    def test_run_recommendations_generated(self, tech_researcher, sample_project):
        """run()generoi suositukset."""
        result = tech_researcher.run(
            task="Tutki projektitiedostot",
            project_files=[str(sample_project / "main.py")],
        )
        assert len(result.recommendations) > 0

    def test_run_no_files(self, tech_researcher):
        """run() toimii ilman tiedostoja."""
        result = tech_researcher.run(
            task="Tutki projektitiedostot",
            project_files=[],
        )
        assert result.success is True
        assert "no_files" in result.detected_technologies

    def test_run_nonexistent_file(self, tech_researcher):
        """run() käsittelee puuttuvat tiedostot."""
        result = tech_researcher.run(
            task="Tutki tiedostoja",
            project_files=["/nonexistent/file.py"],
        )
        assert result.success is True
        assert len(result.detected_technologies) >= 0

    def test_analyze_file_returns_dict(self, tech_researcher, sample_project):
        """analyze_file palauttaa dictionaryn."""
        result = tech_researcher.analyze_file_for_tech(str(sample_project / "main.py"))
        assert "pydantic" in result
        assert "fastapi" in result

    def test_serializes_to_dict(self, tech_researcher, sample_project):
        """Tulokset voidaan serialisoida."""
        result = tech_researcher.run(
            task="Tutki",
            project_files=[str(sample_project / "main.py")],
        )
        d = result.to_dict()
        assert d["agent_type"] == "tech_researcher"
        assert "detected_technologies" in d
