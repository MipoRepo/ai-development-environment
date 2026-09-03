"""
Testit DeveloperAgentille, RefactoringAgentille ja CodeReviewAgentille (M4).
"""

from pathlib import Path

import pytest

from agents.developer import (
    DeveloperAgent,
    DeveloperInput,
    DeveloperOutput,
    RefactoringAgent,
    RefactoringInput,
    RefactoringOutput,
    CodeReviewAgent,
    CodeReviewInput,
    CodeReviewOutput,
)


@pytest.fixture
def developer():
    return DeveloperAgent()


@pytest.fixture
def refactorer():
    return RefactoringAgent()


@pytest.fixture
def reviewer():
    return CodeReviewAgent()


@pytest.fixture
def sample_code():
    """Palauttaa testikoodin."""
    return '''"""Moduulin doksekeinnot."""
import os
import sys

def oldFunction():
    """Vanha funktio."""
    pass

def calculateTotal(a, b):
    return a + b
'''


class TestDeveloperAgentInit:
    """Testit DeveloperAgentin alustukselle."""

    def test_agent_type(self, developer):
        assert developer.agent_type == "developer"

    def test_input_schema(self, developer):
        assert developer.input_schema == DeveloperInput

    def test_output_schema(self, developer):
        assert developer.output_schema == DeveloperOutput


class TestCodeGeneration:
    """Testit koodin generoinnille."""

    def test_run_generates_python(self, developer, tmp_path):
        """Python-koodi generoidaan oikein."""
        result = developer.run(
            task="Luo Python-moduuli käyttäjistä",
            file_path="src/users.py",
            language="python",
            project_path=str(tmp_path),
        )
        assert isinstance(result, DeveloperOutput)
        assert result.success is True
        assert result.lines_written > 0
        assert "language" in result.result
        assert result.result["language"] == "python"
        assert (tmp_path / "src" / "users.py").exists()

    def test_run_generates_javascript(self, developer, tmp_path):
        """JavaScript-koodi generoidaan oikein."""
        result = developer.run(
            task="Luo JavaScript-moduuli",
            file_path="src/app.js",
            language="javascript",
            project_path=str(tmp_path),
        )
        assert result.success is True
        assert (tmp_path / "src" / "app.js").exists()

    def test_run_generates_markdown(self, developer, tmp_path):
        """Markdown generoidaan oikein."""
        result = developer.run(
            task="Luo dokumentaatio",
            file_path="docs/guide.md",
            language="markdown",
            project_path=str(tmp_path),
        )
        assert result.success is True
        assert (tmp_path / "docs" / "guide.md").exists()

    def test_run_creates_file_content(self, developer, tmp_path):
        """Luodussa tiedostossa on oikea sisältö."""
        result = developer.run(
            task="Luo moduuli",
            file_path="src/module.py",
            language="python",
            project_path=str(tmp_path),
        )
        content = (tmp_path / "src" / "module.py").read_text(encoding="utf-8")
        assert len(content) > 0
        assert "def" in content

    def test_run_append_mode(self, developer, tmp_path):
        """Kirjoitusliitos ei ylikirjoita olemassa olevaa."""
        # Luo ensin tiedosto
        filepath = tmp_path / "src" / "append_test.py"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text("# Olenna sisältö\n", encoding="utf-8")

        result = developer.run(
            task="Lisää toiminnallisuus",
            file_path="src/append_test.py",
            language="python",
            project_path=str(tmp_path),
            overwrite=False,
        )
        content = filepath.read_text(encoding="utf-8")
        assert "# Olenna sisältö" in content  # Vanha sisälty

    def test_run_default_path(self, developer, tmp_path):
        """Oletuspolku luodaan oikein ilman file_path-parametria."""
        result = developer.run(
            task="Luo moduuli",
            language="python",
            project_path=str(tmp_path),
        )
        assert result.success is True
        assert result.file_path != ""


class TestDeveloperOperations:
    """Testit operaatioille."""

    def test_operations_list(self, developer, tmp_path):
        """Operaatiot näkyvät tuloksessa."""
        result = developer.run(
            task="Luo moduuli",
            file_path="src/test.py",
            language="python",
            project_path=str(tmp_path),
        )
        assert "create_file" in result.operations

    def test_serializes(self, developer, tmp_path):
        """Tulos voidaan serialisoida."""
        result = developer.run(
            task="Luo moduuli",
            file_path="src/serial.py",
            language="python",
            project_path=str(tmp_path),
        )
        d = result.to_dict()
        assert d["agent_type"] == "developer"
        assert "file_path" in d


class TestRefactoringAgent:
    """Testit RefactoringAgentille."""

    def test_agent_type(self, refactorer):
        assert refactorer.agent_type == "refactoring"

    def test_run_with_code(self, refactorer, sample_code):
        """run() analysoi koodin."""
        result = refactorer.run(
            task="Refaktoroi tämä koodi",
            code=sample_code,
        )
        assert isinstance(result, RefactoringOutput)
        assert result.success is True
        assert len(result.suggestions) >= 1

    def test_run_detects_missing_docstrings(self, refactorer):
        """Puuttuvat doksekeinnot tunnistetaan."""
        code = '''
def my_func():
    pass

def another_func():
    """Olen olemassa."""
    return 42
'''
        result = refactorer.run(
            task="Tarkista doksekeinnot",
            code=code,
            rules=["add_docstrings"],
        )
        assert any("doksekeinnot" in s for s in result.suggestions)

    def test_run_detects_unused_imports(self, refactorer):
        """Käyttämättomat importit tunnistetaan."""
        code = '''import os
import sys

def main():
    print("hello")
'''
        result = refactorer.run(
            task="Poista käyttämättomat",
            code=code,
            rules=["remove_unused"],
        )
        assert any("import" in s.lower() for s in result.suggestions)

    def test_run_detects_long_function(self, refactorer):
        """Pitkä funktio tunnistetaan."""
        long_body = "\n    x += 1" * 35
        code = f'''
def long_function():
    x = 0{long_body}
    return x
'''
        result = refactorer.run(
            task="Etsi pitkät funktiot",
            code=code,
        )
        assert any("pitk" in s.lower() or "rivi" in s.lower() for s in result.suggestions)

    def test_run_with_file_path(self, refactorer, tmp_path):
        """run() lukee tiedoston file_path-parametrista."""
        filepath = tmp_path / "analyze_me.py"
        filepath.write_text("def foo(): pass", encoding="utf-8")

        result = refactorer.run(
            task="Refaktoroi tiedosto",
            file_path=str(filepath),
        )
        assert result.success is True
        assert result.original_code == "def foo(): pass"

    def test_run_invalid_syntax(self, refactorer):
        """Virheellinen syntaksi käsitellään viikoittelematta."""
        result = refactorer.run(
            task="Refaktoroi",
            code="def broken(\n",
        )
        assert result.success is True  # Ei kaada, vaan antaa palautetta
        assert any("syntaksi" in s.lower() or "virhe" in s.lower() for s in result.suggestions)

    def test_run_empty_code(self, refactorer):
        """Tyhjä koodi antaa virheilmoituksen."""
        result = refactorer.run(
            task="Refaktoroi",
            code="",
        )
        assert result.success is False


class TestCodeReviewAgent:
    """Testit CodeReviewAgentille."""

    def test_agent_type(self, reviewer):
        assert reviewer.agent_type == "code_review"

    def test_run_clean_code(self, reviewer):
        """Puhdas koodi saa hyvät pisteet."""
        code = '''"""Moduuli."""


def well_documented():
    """Tämä on hyvin dokumentoitu."""
    return True
'''
        result = reviewer.run(
            task="Tarkista tämä koodi",
            code=code,
        )
        assert isinstance(result, CodeReviewOutput)
        assert result.success is True
        assert result.issue_count == 0
        assert result.score == 100.0

    def test_run_detects_eval(self, reviewer):
        """eval() tunnistetaan kriittisenä."""
        code = "result = eval('1 + 1')"
        result = reviewer.run(
            task="Tarkista turvallisuus",
            code=code,
            severity_threshold="low",
        )
        assert any(i["type"] == "security" for i in result.issues)
        assert result.issue_count >= 1

    def test_run_detects_hardcoded_password(self, reviewer):
        """Kiinteä salasana tunnistetaan."""
        code = "password = 'supersecret123'"
        result = reviewer.run(
            task="Tarkista turvallisuus",
            code=code,
            severity_threshold="low",
        )
        assert any("salasana" in i["message"] for i in result.issues)

    def test_run_detects_bare_except(self, reviewer):
        """Bare except tunnistetaan."""
        code = '''
try:
    pass
except:
    pass
'''
        result = reviewer.run(
            task="Tarkista laatu",
            code=code,
            severity_threshold="low",
        )
        assert any("except" in i["message"].lower() for i in result.issues)

    def test_run_detects_import_star(self, reviewer):
        """import * tunnistetaan."""
        code = "from os import *"
        result = reviewer.run(
            task="Tarkista laatu",
            code=code,
            severity_threshold="low",
        )
        assert any("import" in i["message"].lower() for i in result.issues)

    def test_run_severity_filter(self, reviewer):
        """Severity-puute suodattaa vammat."""
        code = "password = 'secret'\neval('1')"
        result = reviewer.run(
            task="Tarkista",
            code=code,
            severity_threshold="high",
        )
        # Kaikki ongelmamme ovat critical tai high
        for issue in result.issues:
            assert issue["severity"] in ("critical", "high")

    def test_run_syntax_error(self, reviewer):
        """Syntaksivirhe tunnistetaan."""
        code = "def broken(\n"
        result = reviewer.run(
            task="Tarkista",
            code=code,
        )
        assert any(i["severity"] == "high" and "syntaksi" in i["message"] for i in result.issues)

    def test_run_file_path(self, reviewer, tmp_path):
        """run() lukee tiedoston file_path-parametrista."""
        filepath = tmp_path / "review_me.py"
        filepath.write_text("password = 'secret123'", encoding="utf-8")

        result = reviewer.run(
            task="Tarkista tiedosto",
            file_path=str(filepath),
            severity_threshold="low",
        )
        assert result.success is True
        assert result.issue_count >= 1

    def test_run_nonexistent_file(self, reviewer):
        """Puuttunut tiedosto antaa virheviestin."""
        result = reviewer.run(
            task="Tarkista",
            file_path="/nonexistent/file.py",
        )
        assert result.success is False

    def test_run_calculates_score(self, reviewer):
        """Pisteet lasketaan oikein."""
        # Koodi ilman ongelmia
        code = "'''Moduuli.'''\n\n\nprint('hello')"
        result = reviewer.run(
            task="Tarkista",
            code=code,
        )
        # Tämä voi aiheuttaa doksekeinnot puutteeraukset
        assert 0 <= result.score <= 100

    def test_severity_levels_count(self, reviewer):
        """Vakautatasot lasketaan oikein."""
        code = "password = 'secret'\nshell = True\neval('1')"
        result = reviewer.run(
            task="Tarkista",
            code=code,
            severity_threshold="low",
        )
        assert result.severity_levels.get("critical", 0) >= 1
        assert result.severity_levels.get("high", 0) >= 1

    def test_serializes(self, reviewer):
        """Tulos voidaan serialisoida."""
        result = reviewer.run(
            task="Tarkista",
            code="print('test')",
        )
        d = result.to_dict()
        assert d["agent_type"] == "code_review"
        assert d["score"] == 100.0
