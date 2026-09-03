"""
Testit QAAgentille ja muihle testing-agentteille (M5).
"""

from pathlib import Path

import pytest

from agents.testing_agent import (
    TestDesignerAgent,
    TestDesignInput,
    TestDesignOutput,
    TesterAgent,
    TestRunInput,
    TestRunOutput,
    QAAgent,
    QAInput,
    QAOutput,
)


@pytest.fixture
def designer():
    return TestDesignerAgent()


@pytest.fixture
def tester():
    return TesterAgent()


@pytest.fixture
def qa_agent():
    return QAAgent()


@pytest.fixture
def sample_code():
    return '''"""Moduuli käyttäjien käsittelyyn."""

def get_user(user_id: int):
    """Hakee käyttäjän ID:llä."""
    return {"id": user_id, "name": "Test User"}

def create_user(name: str):
    """Luo uuden käyttäjän."""
    return {"name": name, "id": 1}
'''


@pytest.fixture
def test_project(tmp_path, sample_code):
    """Luo testiprojektin."""
    (tmp_path / "main.py").write_text(sample_code, encoding="utf-8")
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_main.py").write_text(
        '''"""Testit päämoduulille."""
def test_get_user():
    assert True

def test_create_user():
    assert True
''',
        encoding="utf-8",
    )
    return tmp_path


class TestTestDesignerAgent:
    """Testit TestDesignerAgentille."""

    def test_agent_type(self, designer):
        assert designer.agent_type == "test_designer"

    def test_input_schema(self, designer):
        assert designer.input_schema == TestDesignInput

    def test_output_schema(self, designer):
        assert designer.output_schema == TestDesignOutput

    def test_run_extracts_functions(self, designer, sample_code):
        """run() purkaa funktiot koodista."""
        result = designer.run(
            task="Suunnittele testit",
            code=sample_code,
        )
        assert isinstance(result, TestDesignOutput)
        assert result.success is True
        assert len(result.test_cases) >= 2
        func_names = [tc["function"] for tc in result.test_cases]
        assert "get_user" in func_names
        assert "create_user" in func_names

    def test_run_generates_pytest(self, designer, sample_code):
        """run() generoi pytest-testit."""
        result = designer.run(
            task="Suunnittele testit",
            code=sample_code,
            framework="pytest",
        )
        assert "def test_" in result.test_file_content
        assert "assert" in result.test_file_content

    def test_run_generates_unittest(self, designer, sample_code):
        """run() generoi unittest-testit."""
        result = designer.run(
            task="Suunnittele testit",
            code=sample_code,
            framework="unittest",
        )
        assert "unittest" in result.test_file_content

    def test_run_from_file(self, designer, tmp_path, sample_code):
        """run() Lukee koodin tiedostosta."""
        filepath = tmp_path / "app.py"
        filepath.write_text(sample_code, encoding="utf-8")

        result = designer.run(
            task="Suunnittele testit tiedostolle",
            file_path=str(filepath),
        )
        assert result.success is True
        assert len(result.test_cases) >= 2

    def test_run_no_code(self, designer):
        """run() antaa virheen tyhjälle koodille."""
        result = designer.run(
            task="Ei koodia",
        )
        assert result.success is False

    def test_run_coverage_targets(self, designer, sample_code):
        """run() määrittää kattavuusreunat."""
        result = designer.run(
            task="Suunnittele testit",
            code=sample_code,
        )
        assert len(result.coverage_target) >= 2

    def test_run_serializes(self, designer, sample_code):
        """Tulos voidaan serialisoida."""
        result = designer.run(
            task="Suunnittele testit",
            code=sample_code,
        )
        d = result.to_dict()
        assert d["agent_type"] == "test_designer"


class TestTesterAgent:
    """Testit TesterAgentille."""

    def test_agent_type(self, tester):
        assert tester.agent_type == "tester"

    def test_run_nonexistent_path(self, tester):
        """run() antaa virheen olematomalle polkulle."""
        result = tester.run(
            task="Aja testit",
            test_path="/nonexistent/tests/",
        )
        assert result.success is False
        assert result.passed == 0
        assert result.exit_code == -1

    def test_run_real_tests(self, tester, test_project):
        """run() suorittaa oikeat testit."""
        result = tester.run(
            task="Aja testit",
            test_path=str(test_project / "tests"),
        )
        assert isinstance(result, TestRunOutput)
        assert result.success is True
        assert result.passed >= 1
        assert result.exit_code == 0

    def test_fail_fast_option(self, tester, test_project):
        """fail_fast-parametri toimii."""
        result = tester.run(
            task="Aja testit",
            test_path=str(test_project / "tests"),
            fail_fast=True,
        )
        assert result.success is True

    def test_serializes(self, tester, test_project):
        """Tulos voidaan serialisoida."""
        result = tester.run(
            task="Aja testit",
            test_path=str(test_project / "tests"),
        )
        d = result.to_dict()
        assert d["agent_type"] == "tester"
        assert "passed" in d


class TestQAAgent:
    """Testit QAAgentille."""

    def test_agent_type(self, qa_agent):
        assert qa_agent.agent_type == "qa"

    def test_input_schema(self, qa_agent):
        assert qa_agent.input_schema == QAInput

    def test_output_schema(self, qa_agent):
        assert qa_agent.output_schema == QAOutput

    def test_run_nonexistent_project(self, qa_agent):
        """run() antaa virheen olemattomalle projektille."""
        result = qa_agent.run(
            task="Tarkista projekti",
            project_path="/nonexistent/project",
        )
        assert result.success is False

    def test_run_finds_test_files(self, qa_agent, test_project):
        """run() löytää testitiedostot."""
        result = qa_agent.run(
            task="Tarkista projekti",
            project_path=str(test_project),
            check_coverage=False,
        )
        assert isinstance(result, QAOutput)
        assert result.success is True
        assert len(result.test_files) >= 1
        assert result.score > 0

    def test_run_detects_missing_tests(self, qa_agent, tmp_path):
        """run() tunnistaa puuttuvat testit."""
        (tmp_path / "main.py").write_text("x = 1\n", encoding="utf-8")

        result = qa_agent.run(
            task="Tarkista projekti",
            project_path=str(tmp_path),
            check_coverage=False,
        )
        assert any("testi" in issue.lower() for issue in result.issues)

    def test_run_checks_coding_standards(self, qa_agent, tmp_path):
        """run() tarkistaa ohjelmointikäytännöt."""
        (tmp_path / "main.py").write_text("x = 1\n", encoding="utf-8")

        result = qa_agent.run(
            task="Tarkista projekti",
            project_path=str(tmp_path),
            check_coverage=False,
        )
        assert isinstance(result, QAOutput)

    def test_run_calculates_score(self, qa_agent, test_project):
        """run() laskee QA-pisteet."""
        result = qa_agent.run(
            task="Tarkista projekti",
            project_path=str(test_project),
            check_coverage=False,
        )
        assert 0 <= result.score <= 100

    def test_serializes(self, qa_agent, test_project):
        """Tulos voidaan serialisoida."""
        result = qa_agent.run(
            task="Tarkista projekti",
            project_path=str(test_project),
            check_coverage=False,
        )
        d = result.to_dict()
        assert d["agent_type"] == "qa"
        assert "score" in d
