"""
Testit SecurityAgenteille (M6).
"""

from pathlib import Path

import pytest

from agents.security_agent import (
    SecurityReviewAgent,
    SecurityReviewInput,
    SecurityReviewOutput,
    SASTAgent,
    SASTInput,
    SASTOutput,
    DependencySecurityAgent,
    DependencySecurityInput,
    DependencySecurityOutput,
    SecretsAgent,
    SecretsInput,
    SecretsOutput,
    ContainerSecurityAgent,
    ContainerSecurityInput,
    ContainerSecurityOutput,
)


@pytest.fixture
def security_reviewer():
    return SecurityReviewAgent()


@pytest.fixture
def sast():
    return SASTAgent()


@pytest.fixture
def dep_sec():
    return DependencySecurityAgent()


@pytest.fixture
def secrets():
    return SecretsAgent()


@pytest.fixture
def container():
    return ContainerSecurityAgent()


@pytest.fixture
def vulnerable_code():
    """Palauttaa koodin, jossa on turvallisuusongelmia."""
    return '''"""Moduuli."""
import os
import pickle

password = "supersecret123"
api_key = "sk-abc123def456ghi789jkl012"

result = eval('1 + 1')
os.system("rm -rf /")
'''


@pytest.fixture
def clean_code():
    """Palauttaa turvallisen koodin."""
    return '''"""Turvallinen moduuli."""
import os
from typing import Optional


class Calculator:
    """Laskinluokka."""

    def add(self, x: int, y: int) -> int:
        """Suorittaa lisäyksen."""
        return x + 1


def safe_function(x: int) -> int:
    """Suorittaa turvallisen laskun."""
    return x + 1
'''


@pytest.fixture
def requirements_file(tmp_path):
    """Luo testi-requirements.txt:n."""
    req = tmp_path / "requirements.txt"
    req.write_text(
        "fastapi>=0.95.0\n"
        "pydantic>=2.0.0\n"
        "flask\n"
        "django\n"
    )
    return tmp_path


class TestSecurityReviewAgent:
    """Testit SecurityReviewAgentille."""

    def test_agent_type(self, security_reviewer):
        assert security_reviewer.agent_type == "security_review"

    def test_input_schema(self, security_reviewer):
        assert security_reviewer.input_schema == SecurityReviewInput

    def test_output_schema(self, security_reviewer):
        assert security_reviewer.output_schema == SecurityReviewOutput

    def test_run_detects_vulnerabilities(self, security_reviewer, vulnerable_code):
        """run() tunnistaa turvallisuusongelmat."""
        result = security_reviewer.run(
            task="Tarkista turvallisuus",
            code=vulnerable_code,
        )
        assert isinstance(result, SecurityReviewOutput)
        assert result.success is True
        assert result.vulnerability_count > 0
        assert result.score < 100

    def test_run_clean_code(self, security_reviewer, clean_code):
        """Puhtaalla koodilla on täydet pisteet."""
        result = security_reviewer.run(
            task="Tarkista turvallisuus",
            code=clean_code,
        )
        assert result.vulnerability_count == 0
        assert result.score == 100.0

    def test_run_detects_eval(self, security_reviewer):
        """eval() tunnistetaan kriittisenä."""
        result = security_reviewer.run(
            task="Tarkista",
            code="result = eval('1 + 1')",
        )
        vulns = result.vulnerabilities
        eval_vulns = [v for v in vulns if v["type"] == "eval"]
        assert len(eval_vulns) >= 1
        assert eval_vulns[0]["severity"] == "critical"

    def test_run_detects_hardcoded_password(self, security_reviewer):
        """Kiinteä salasana tunnistetaan."""
        result = security_reviewer.run(
            task="Tarkista",
            code="password = 'mySecretPass123'",
        )
        assert any("password" in v["type"] for v in result.vulnerabilities)

    def test_run_detects_hardcoded_api_key(self, security_reviewer):
        """Kiinteä API-avain tunnistetaan."""
        result = security_reviewer.run(
            task="Tarkista",
            code="api_key = 'sk-abc123def456ghi789jkl012'",
        )
        assert any("api_key" in v["type"] for v in result.vulnerabilities)

    def test_run_severity_counts(self, security_reviewer, vulnerable_code):
        """Vakaudet lasketaan oikein."""
        result = security_reviewer.run(
            task="Tarkista",
            code=vulnerable_code,
        )
        assert result.severity_counts.get("critical", 0) > 0

    def test_run_from_file(self, security_reviewer, tmp_path, vulnerable_code):
        """run() lukee tiedoston file_path-parametrista."""
        filepath = tmp_path / "vuln.py"
        filepath.write_text(vulnerable_code, encoding="utf-8")

        result = security_reviewer.run(
            task="Tarkista tiedosto",
            file_path=str(filepath),
        )
        assert result.vulnerability_count > 0

    def test_run_from_directory(self, security_reviewer, tmp_path, vulnerable_code):
        """run() skannaa koko kansion."""
        (tmp_path / "vuln.py").write_text(vulnerable_code, encoding="utf-8")

        result = security_reviewer.run(
            task="Skannaa kansio",
            file_path=str(tmp_path),
        )
        assert result.vulnerability_count > 0

    def test_serializes(self, security_reviewer, vulnerable_code):
        """Tulos voidaan serialisoida."""
        result = security_reviewer.run(
            task="Tarkista",
            code=vulnerable_code,
        )
        d = result.to_dict()
        assert d["agent_type"] == "security_review"


class TestSASTAgent:
    """Testit SASTAgentille."""

    def test_agent_type(self, sast):
        assert sast.agent_type == "sast"

    def test_run_detects_eval(self, sast):
        """AST-analyysi havaitsee eval-kutsun."""
        code = "result = eval('1 + 1')"
        result = sast.run(
            task="Analysoi koodi AST:llä",
            code=code,
        )
        assert isinstance(result, SASTOutput)
        assert result.success is True
        assert any(f["type"] == "code_injection" for f in result.findings)

    def test_run_detects_exec(self, sast):
        """AST-analyysi havaitsee exec-kutsun."""
        code = "exec('print(1)')"
        result = sast.run(
            task="Analysoi",
            code=code,
        )
        assert any(f["type"] == "code_injection" for f in result.findings)

    def test_run_detects_dangerous_imports(self, sast):
        """AST-analyysi havaitsee vaaralliset importit."""
        code = "import pickle\nimport os"
        result = sast.run(
            task="Analysoi",
            code=code,
        )
        assert any(f["type"] == "dangerous_import" for f in result.findings)

    def test_run_analyzes_ast_metrics(self, sast, clean_code):
        """AST-metriikit lasketaan oikein."""
        result = sast.run(
            task="Analysoi",
            code=clean_code,
        )
        assert result.ast_analysis["functions"] >= 1
        assert result.ast_analysis["classes"] >= 1
        assert result.ast_analysis["complexity"] >= 0

    def test_run_syntax_error(self, sast):
        """Syntaksivirhe käsitellään."""
        result = sast.run(
            task="Analysoi",
            code="def broken(\n",
        )
        assert result.success is False

    def test_run_empty_code(self, sast):
        """Tyhjä koodi antaa virheen."""
        result = sast.run(
            task="Analysoi",
            code="",
        )
        assert result.success is False

    def test_run_from_file(self, sast, tmp_path, clean_code):
        """run() lukee tiedoston."""
        filepath = tmp_path / "code.py"
        filepath.write_text(clean_code, encoding="utf-8")

        result = sast.run(
            task="Analysoi tiedosto",
            file_path=str(filepath),
        )
        assert result.success is True
        assert result.finding_count == 0


class TestDependencySecurityAgent:
    """Testit DependencySecurityAgentille."""

    def test_agent_type(self, dep_sec):
        assert dep_sec.agent_type == "dependency_security"

    def test_run_finds_dependencies(self, dep_sec, requirements_file):
        """run() löytää riippuvuudet requirements.txt:stä."""
        result = dep_sec.run(
            task="Tarkista riippuvuudet",
            project_path=str(requirements_file),
        )
        assert isinstance(result, DependencySecurityOutput)
        assert result.success is True
        assert len(result.dependencies) == 4

    def test_run_detects_vulnerable_package(self, dep_sec, tmp_path):
        """Haavoittuva paketti tunnistetaan."""
        req = tmp_path / "requirements.txt"
        req.write_text("django==1.11.1\nflask\n", encoding="utf-8")

        result = dep_sec.run(
            task="Tarkista",
            project_path=str(tmp_path),
        )
        assert result.vulnerable_count >= 1
        assert any("django" in rec for rec in result.recommendations)

    def test_run_no_requirements(self, dep_sec, tmp_path):
        """Ei requirements.txt:tä — tyhjä lista."""
        result = dep_sec.run(
            task="Tarkista",
            project_path=str(tmp_path),
        )
        assert result.success is True
        assert len(result.dependencies) == 0
        assert any("ei" in rec.lower() for rec in result.recommendations)

    def test_serializes(self, dep_sec, requirements_file):
        """Tulos voidaan serialisoida."""
        result = dep_sec.run(
            task="Tarkista",
            project_path=str(requirements_file),
        )
        d = result.to_dict()
        assert d["agent_type"] == "dependency_security"


class TestSecretsAgent:
    """Testit SecretsAgentille."""

    def test_agent_type(self, secrets):
        assert secrets.agent_type == "secrets"

    def test_run_detects_aws_key(self, secrets):
        """AWS Access Key tunnistetaan."""
        code = "AKIAIOSFODNN7EXAMPLE"
        result = secrets.run(
            task="Etsi salaisuudet",
            code=code,
        )
        assert isinstance(result, SecretsOutput)
        assert result.secret_count >= 1
        assert any("aws" in s["type"].lower() for s in result.secrets_found)

    def test_run_detects_github_token(self, secrets):
        """GitHub Token tunnistetaan."""
        code = "token = 'ghp_abcdefghijklmnopqrstuvwxyz1234567890AB'"
        result = secrets.run(
            task="Etsi salaisuudet",
            code=code,
        )
        assert any("github" in s["type"].lower() for s in result.secrets_found)

    def test_run_detects_private_key(self, secrets):
        """Private key tunnistetaan."""
        code = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAA..."
        result = secrets.run(
            task="Etsi salaisuudet",
            code=code,
        )
        assert any("private" in s["type"].lower() for s in result.secrets_found)

    def test_run_detects_api_key(self, secrets):
        """Generic API Key tunnistetaan."""
        result = secrets.run(
            task="Etsi",
            code="api_key = 'sk-abcdef1234567890'",
        )
        assert result.secret_count >= 1

    def test_run_no_secrets(self, secrets, clean_code):
        """Puhdasta koodia ei paljasta salaisuuksia."""
        result = secrets.run(
            task="Etsi",
            code=clean_code,
        )
        assert result.secret_count == 0

    def test_run_scan_directory(self, secrets, tmp_path):
        """Kansion skannaus löytää salaisuudet tiedostoista."""
        (tmp_path / ".env").write_text("API_KEY=sk-abc123def456ghi789jkl012", encoding="utf-8")
        (tmp_path / "config.py").write_text("password = 'secret123'", encoding="utf-8")

        result = secrets.run(
            task="Skannaa kansio",
            scan_all=True,
            project_path=str(tmp_path),
        )
        assert result.secret_count >= 1
        assert result.scanned_files >= 2

    def test_serializes(self, secrets, vulnerable_code):
        """Tulos voidaan serialisoida."""
        result = secrets.run(
            task="Etsi",
            code=vulnerable_code,
        )
        d = result.to_dict()
        assert d["agent_type"] == "secrets"


class TestContainerSecurityAgent:
    """Testit ContainerSecurityAgentille."""

    def test_agent_type(self, container):
        assert container.agent_type == "container_security"

    def test_run_no_dockerfile(self, container, tmp_path):
        """Ei Dockerfile-tiedostoa antaa virheen."""
        result = container.run(
            task="Tarkista Dockerfile",
            dockerfile_path=str(tmp_path / "Dockerfile"),
            project_path=str(tmp_path),
        )
        assert result.success is False
        assert any("Dockerfile" in issue for issue in result.issues)

    def test_run_detects_root_user(self, container, tmp_path):
        """USER root tunnistetaan."""
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text(
            "FROM python:3.11\nUSER root\nCMD [\"python\", \"app.py\"]",
            encoding="utf-8",
        )

        result = container.run(
            task="Tarkista Dockerfile",
            dockerfile_path=str(dockerfile),
        )
        assert isinstance(result, ContainerSecurityOutput)
        assert result.success is True
        assert any("root" in issue.lower() for issue in result.issues)

    def test_run_detects_missing_user(self, container, tmp_path):
        """USER-määrittelyn puute tunnistetaan."""
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text(
            "FROM python:3.11-alpine\nCMD [\"python\", \"app.py\"]",
            encoding="utf-8",
        )

        result = container.run(
            task="Tarkista",
            dockerfile_path=str(dockerfile),
        )
        assert any("USER" in issue for issue in result.issues)

    def test_run_detects_shell_true_risk(self, container, tmp_path):
        """curl | sh -mallinnus tunnistetaan."""
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text(
            "FROM ubuntu:latest\nRUN curl https://example.com/script.sh | sh\n",
            encoding="utf-8",
        )

        result = container.run(
            task="Tarkista",
            dockerfile_path=str(dockerfile),
        )
        assert any("curl" in issue.lower() for issue in result.issues)

    def test_run_good_practices_detected(self, container, tmp_path):
        """Hyvät käytännöt tunnistetaan."""
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text(
            "FROM python:3.11-alpine\n"
            "USER nobody\n"
            "RUN pip install --no-cache-dir .\n"
            "HEALTHCHECK CMD python --version\n",
            encoding="utf-8",
        )

        result = container.run(
            task="Tarkista",
            dockerfile_path=str(dockerfile),
        )
        assert result.score > 80
        assert len(result.issues) <= 3  # Vain puuttuvat huomautukset

    def test_serializes(self, container, tmp_path):
        """Tulos voidaan serialisoida."""
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text(
            "FROM python:3.11\nUSER app\nCMD [\"python\", \"app.py\"]",
            encoding="utf-8",
        )

        result = container.run(
            task="Tarkista",
            dockerfile_path=str(dockerfile),
        )
        d = result.to_dict()
        assert d["agent_type"] == "container_security"
        assert "score" in d
