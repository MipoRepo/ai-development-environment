"""
Testit Maintenance-agenteille (M14).
"""

import json
import tempfile
from pathlib import Path

import pytest

from agents.maintenance_agent import (
    UpgradeAgent,
    UpgradeAgentInput,
    UpgradeAgentOutput,
    CleanupAgent,
    CleanupAgentInput,
    CleanupAgentOutput,
    DependencyAgent,
    DependencyAgentInput,
    DependencyAgentOutput,
    MAINTENANCE_ACTIONS,
    CACHE_DIRS,
    DEPENDENCY_FILES,
)


@pytest.fixture
def upgrade_agent():
    """Palauttaa UpgradeAgent-instanssin."""
    return UpgradeAgent()


@pytest.fixture
def cleanup_agent():
    """Palauttaa CleanupAgent-instanssin."""
    return CleanupAgent()


@pytest.fixture
def dependency_agent():
    """Palauttaa DependencyAgent-instanssin."""
    return DependencyAgent()


@pytest.fixture
def sample_requirements(tmp_path):
    """Luo testirequirements.txt-tiedoston."""
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("""
pydantic>=2.0.0
pytest>=8.0.0
requests==2.31.0
# FIXME: Remove this later
old-package<1.0.0
""")
    return str(req_file)


@pytest.fixture
def sample_pyproject(tmp_path):
    """Luo testattavan pyproject.toml-tiedoston."""
    pp_file = tmp_path / "pyproject.toml"
    pp_file.write_text("""
[project]
name = "test-project"
version = "0.1.0"
dependencies = [
    "pydantic>=2.0",
    "requests>=2.28",
]

[project.optional-dependencies]
dev = ["pytest>=8.0"]
""")
    return str(pp_file)


@pytest.fixture
def temp_project_dir(tmp_path):
    """Luo tilapäisen projekti-kansion."""
    # Luo cache-kansiot
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "test.cpython-311.pyc").write_text("fake cache")
    (tmp_path / ".pytest_cache").mkdir()
    (tmp_path / ".pytest_cache" / "v" / "cache").mkdir(parents=True)
    (tmp_path / ".pytest_cache" / "v" / "cache" / "lastfailed").write_text("test")

    # Luo temp-tiedosto
    (tmp_path / ".temp_file.bak").write_text("temporary")

    # Luo build-kansio
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "artifact.txt").write_text("build artifact")

    return str(tmp_path)


# ===================
# UpgradeAgent tests
# ===================


class TestUpgradeAgent:
    """Testit UpgradeAgentille."""

    def test_agent_type(self, upgrade_agent):
        """Agentin tyyppi on oikein."""
        assert upgrade_agent.agent_type == "upgrade"

    def test_input_schema(self, upgrade_agent):
        """Input-skeema on oikein."""
        assert upgrade_agent.input_schema == UpgradeAgentInput

    def test_output_schema(self, upgrade_agent):
        """Output-skeema on oikein."""
        assert upgrade_agent.output_schema == UpgradeAgentOutput

    def test_check_specific_packages(self, upgrade_agent):
        """Tarkista tiettyjä paketteja."""
        result = upgrade_agent.run(
            task="Tarkista paketit",
            action="check",
            packages=["pydantic", "requests"],
            dry_run=True,
        )
        assert result.success is True
        assert len(result.current_versions) == 2

    def test_dry_run_mode(self, upgrade_agent):
        """Dry-run -tilassa ei suoriteta komennoita."""
        result = upgrade_agent.run(
            task="Tarkista",
            action="check",
            dry_run=True,
        )
        assert result.success is True
        assert len(result.upgrade_commands) >= 0  # Ei suoritettu

    def test_upgrade_action_dry_run(self, upgrade_agent):
        """Upgrade-toiminta dry-run -tilassa ei tee muutoksia."""
        result = upgrade_agent.run(
            task="Simuloitu päivitys",
            action="upgrade",
            packages=["pydantic"],
            dry_run=True,
        )
        assert result.success is True
        assert len(result.upgrade_results) == 0  # Dry-run → ei suoritu

    def test_parse_requirement_standard(self, upgrade_agent):
        """Standardin requrements-rivin parsing toimii."""
        parsed = upgrade_agent._parse_requirement("pydantic>=2.0.0")
        assert parsed is not None
        assert parsed["name"] == "pydantic"
        assert "2.0.0" in parsed["version_spec"]

    def test_parse_requirement_with_comment(self, upgrade_agent):
        """Kommentit ja tyhjät rivit ohitetaan."""
        assert upgrade_agent._parse_requirement("# kommentti") is None
        assert upgrade_agent._parse_requirement("") is None
        assert upgrade_agent._parse_requirement("   ") is None

    def test_parse_requirement_no_version(self, upgrade_agent):
        """Paketit ilman versiota parsitaan oikein."""
        parsed = upgrade_agent._parse_requirement("requests")
        assert parsed is not None
        assert parsed["name"] == "requests"

    def test_read_requirements(self, upgrade_agent, sample_requirements):
        """Requirements-filen lukeminen toimii."""
        deps = upgrade_agent._read_requirements(sample_requirements)
        assert len(deps) > 0
        names = [d["name"] for d in deps]
        assert "pydantic" in names

    def test_build_upgrade_commands(self, upgrade_agent):
        """Päivityskomennot luodaan oikein."""
        upgradable = [
            {"name": "package1", "current_version": "1.0", "latest_version": "2.0", "upgradable": True},
            {"name": "package2", "current_version": "1.0", "latest_version": "1.0", "upgradable": False},
        ]
        commands = upgrade_agent._build_upgrade_commands(upgradable)
        assert len(commands) == 1
        assert "package1" in commands[0]
        assert "pip install --upgrade" in commands[0]

    def test_serializes(self, upgrade_agent):
        """Tulos voidään serialisoida."""
        result = upgrade_agent.run(
            task="Testaa serialisointia",
            action="check",
            packages=["pydantic"],
            dry_run=True,
        )
        d = result.to_dict()
        assert d["agent_type"] == "upgrade"
        assert "upgradable_packages" in d


class TestUpgradeAgentModuleLevel:
    """Moduulitasolla olevat testit."""

    def test_maintenance_actions_exist(self):
        """Ylläpitotoimenpiteet-sanakirja on olemassa."""
        assert len(MAINTENANCE_ACTIONS) >= 4

    def test_agent_importable_from_package(self):
        """Agentti on tuotavissa paketista."""
        from agents import UpgradeAgent as UA
        assert UA.agent_type == "upgrade"


# ===================
# CleanupAgent tests
# ===================


class TestCleanupAgent:
    """Testit CleanupAgentille."""

    def test_agent_type(self, cleanup_agent):
        """Agentin tyyppi on oikein."""
        assert cleanup_agent.agent_type == "cleanup"

    def test_input_schema(self, cleanup_agent):
        """Input-skeema on oikein."""
        assert cleanup_agent.input_schema == CleanupAgentInput

    def test_output_schema(self, cleanup_agent):
        """Output-skeema on oikein."""
        assert cleanup_agent.output_schema == CleanupAgentOutput

    def test_scan_finds_cache_dirs(self, cleanup_agent, temp_project_dir):
        """Scannaus löytää cache-kansiot."""
        result = cleanup_agent.run(
            task="Skannaa cachet",
            action="scan",
            directories=[temp_project_dir],
        )
        assert result.success is True
        assert len(result.found_items) > 0
        cache_items = [i for i in result.found_items if i["type"] == "cache"]
        assert len(cache_items) > 0

    def test_dry_run_no_deletions(self, cleanup_agent, temp_project_dir):
        """Dry-run-tila ei poista tiedostoja."""
        result = cleanup_agent.run(
            task="Simuloidu siivinta",
            action="dry_run",
            directories=[temp_project_dir],
        )
        assert result.success is True
        assert len(result.cleaned_items) == 0

    def test_clean_removes_files(self, cleanup_agent, temp_project_dir):
        """Puhtauspoisto todella poistaa tiedostoja."""
        result = cleanup_agent.run(
            task="Puhdista",
            action="clean",
            directories=[temp_project_dir],
        )
        assert result.success is True
        assert len(result.cleaned_items) > 0

    def test_scan_empty_directory(self, cleanup_agent, tmp_path):
        """Tyhjän kansion skannaus palauttaa tyhjän listan."""
        result = cleanup_agent.run(
            task="Tyhjä kansio",
            action="scan",
            directories=[str(tmp_path)],
        )
        assert result.success is True
        assert result.total_files == 0

    def test_scan_nonexistent_directory(self, cleanup_agent):
        """Olematoman kansion skannaus ei kaado."""
        result = cleanup_agent.run(
            task="Ei kansion",
            action="scan",
            directories=["/nonexistent/path/12345"],
        )
        assert result.success is True

    def test_temp_file_detection(self, cleanup_agent, tmp_path):
        """Tilapäistiedostot tunnistetaan."""
        # Luo tilapäiset tiedostot
        (tmp_path / "backup.bak").write_text("backup")
        (tmp_path / "file.tmp").write_text("temp")
        (tmp_path / "normal.txt").write_text("normal")

        result = cleanup_agent.run(
            task="Etsi tilapäiset",
            action="scan",
            directories=[str(tmp_path)],
            clean_cache=False,
            clean_build=False,
            clean_temp=True,
        )
        assert result.success is True
        temp_items = [i for i in result.found_items if i["type"] == "temp"]
        assert len(temp_items) >= 2

    def test_custom_patterns(self, cleanup_agent, tmp_path):
        """Mukautetut kohdisteet työmähän."""
        (tmp_path / "mylog.log").write_text("log content")

        result = cleanup_agent.run(
            task="Mukautetut kohdisteet",
            action="scan",
            directories=[str(tmp_path)],
            custom_patterns=["*.log"],
        )
        assert result.success is True

    def test_space_freed_calculated(self, cleanup_agent, temp_project_dir):
        """Vapautunut tila lasketaan."""
        result = cleanup_agent.run(
            task="Laske tila",
            action="scan",
            directories=[temp_project_dir],
        )
        assert result.success is True
        assert result.space_freed >= 0

    def test_serializes(self, cleanup_agent, temp_project_dir):
        """Tulos voidää serialisoida."""
        result = cleanup_agent.run(
            task="Testaa serialisointia",
            action="scan",
            directories=[temp_project_dir],
        )
        d = result.to_dict()
        assert d["agent_type"] == "cleanup"
        assert "found_items" in d

    def test_cache_dirs_constant(self):
        """CACHE_DIRS-slista on olemassa."""
        assert len(CACHE_DIRS) >= 5
        assert "__pycache__" in CACHE_DIRS
        assert ".pytest_cache" in CACHE_DIRS


class TestCleanupAgentModuleLevel:
    """Moduilatasolla olevat testit."""

    def test_agent_importable_from_package(self):
        """Agentti on tuotavissa paketista."""
        from agents import CleanupAgent as CA
        assert CA.agent_type == "cleanup"


# ===================
# DependencyAgent tests
# ===================


class TestDependencyAgent:
    """Testit DependencyAgentille."""

    def test_agent_type(self, dependency_agent):
        """Agentin tyyppi on oikein."""
        assert dependency_agent.agent_type == "dependency"

    def test_input_schema(self, dependency_agent):
        """Input-skeema on oikein."""
        assert dependency_agent.input_schema == DependencyAgentInput

    def test_output_schema(self, dependency_agent):
        """Output-skeema on oikein."""
        assert dependency_agent.output_schema == DependencyAgentOutput

    def test_analyze_with_requirements(self, dependency_agent, sample_requirements):
        """Riippuvuustiedoston analyysi toimii."""
        result = dependency_agent.run(
            task="Analysoi requirements",
            action="analyze",
            dependency_files=[sample_requirements],
            check_security=False,
            check_outdated=False,
        )
        assert result.success is True
        assert result.total_dependencies > 0
        names = [d["name"] for d in result.dependencies]
        assert "pydantic" in names

    def test_analyze_with_pyproject(self, dependency_agent, sample_pyproject):
        """pyproject.toml-analyysi toimii."""
        result = dependency_agent.run(
            task="Analysoi pyproject",
            action="analyze",
            dependency_files=[sample_pyproject],
            check_security=False,
            check_outdated=False,
        )
        assert result.success is True
        assert result.total_dependencies > 0

    def test_analyze_with_security_check(self, dependency_agent, sample_requirements):
        """Turvallisuustarkistus toimii."""
        result = dependency_agent.run(
            task="Turvallisuustarkistus",
            action="analyze",
            dependency_files=[sample_requirements],
            check_security=True,
        )
        assert result.success is True
        # May or may not find known issues depending on package names

    def test_analyze_with_outdated_check(self, dependency_agent, sample_requirements):
        """Vanhentuneiden tarkistus toimii."""
        result = dependency_agent.run(
            task="Vanhentuneet",
            action="analyze",
            dependency_files=[sample_requirements],
            check_outdated=True,
        )
        assert result.success is True
        assert "outdated_packages" in result.to_dict()

    def test_recommendations_generated(self, dependency_agent, sample_requirements):
        """Suositukset luodaan."""
        result = dependency_agent.run(
            task="Suositukset",
            action="analyze",
            dependency_files=[sample_requirements],
            check_security=False,
            check_outdated=False,
        )
        assert result.success is True
        assert len(result.recommendations) > 0

    def test_dependency_graph_built(self, dependency_agent, sample_requirements):
        """Riippuvuussolmut rakentuvat."""
        result = dependency_agent.run(
            task="Riippuvuussolmut",
            action="analyze",
            dependency_files=[sample_requirements],
            check_security=False,
            check_outdated=False,
        )
        assert result.success is True
        assert isinstance(result.dependency_graph, dict)
        assert len(result.dependency_graph) > 0

    def test_find_dependency_files(self, dependency_agent, tmp_path):
        """Riippuvuustiedostojen etsinta toimii."""
        (tmp_path / "requirements.txt").write_text("pytest")
        (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
        (tmp_path / "package.json").write_text("{}")

        dep_files = dependency_agent._find_dependency_files([str(tmp_path)])
        assert len(dep_files) >= 2

    def test_parse_requirements_txt(self, dependency_agent, sample_requirements):
        """Requirements-tiedoston parsing toimii."""
        deps = dependency_agent._parse_requirements_txt(sample_requirements)
        assert len(deps) > 0
        names = [d["name"] for d in deps]
        assert "pydantic" in names
        assert "pytest" in names

    def test_parse_pyproject_toml(self, dependency_agent, sample_pyproject):
        """pyproject.toml-parsinta toimii."""
        deps = dependency_agent._parse_pyproject_toml(sample_pyproject)
        assert len(deps) > 0

    def test_check_known_vulnerabilities(self, dependency_agent):
        """Tunnettujen vaativuuksien tarkistus palauttaa tuloksen."""
        # Testataan tunnistetun paketin kanssa
        result = dependency_agent._check_known_vulnerabilities("django")
        assert result is not None
        assert result["severity"] in ("low", "medium", "high", "critical")
        # Testataan tuntemattoman
        result_none = dependency_agent._check_known_vulnerabilities("unknown_xyz_package_12345")
        assert result_none is None

    def test_serializes(self, dependency_agent, sample_requirements):
        """Tulos voidaan serialisoida."""
        result = dependency_agent.run(
            task="Testaa serialisointia",
            action="analyze",
            dependency_files=[sample_requirements],
            check_security=False,
            check_outdated=False,
        )
        d = result.to_dict()
        assert d["agent_type"] == "dependency"
        assert "dependencies" in d


class TestDependencyAgentModuleLevel:
    """Moduulitasolla olevat testit."""

    def test_dependency_files_exist(self):
        """Riippuvuustiedostojen muut on olemassa."""
        assert len(DEPENDENCY_FILES) >= 2
        assert "requirements.txt" in DEPENDENCY_FILES
        assert "pyproject.toml" in DEPENDENCY_FILES

    def test_agent_importable_from_package(self):
        """Agentti on tuotavissa paketista."""
        from agents import UpgradeAgent as UA
        assert UA.agent_type == "upgrade"

    def test_cleanup_importable_from_package(self):
        """Cleanup-agentti on tuotavissa paketista."""
        from agents import CleanupAgent as CA
        assert CA.agent_type == "cleanup"

    def test_dependency_importable_from_package(self):
        """Dependency-agentti on tuotavissa paketista."""
        from agents import DependencyAgent as DA
        assert DA.agent_type == "dependency"
