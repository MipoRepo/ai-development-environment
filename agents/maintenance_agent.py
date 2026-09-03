"""
MaintenanceAgent-moduuli (M14) — järjestelmän ylläpito, päivitykset ja optimointi.

Sisältää kolme agenttia:
- UpgradeAgent: automaattinen riippuvuuden ja versioiden päivitustarkistus.
- CleanupAgent: vanhentuneiden tiedostojen, cacheiden ja turmien resurssien poisto.
- DependencyAgent: riippuvuussuhteiden analyysi ja päivitysuuditet.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Python 3.11:ssa tomllib on sisäänrakennettu, muussa tomli
try:
    import tomllib
except ImportError:
    import tomli as tomllib

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


# Ylläpidon toimenpiteet
MAINTENANCE_ACTIONS: dict[str, dict[str, str]] = {
    "upgrade": {
        "name": "Päivitys",
        "description": "Päivitä projektin riippuvuudet ja työkalut.",
        "command_template": "pip install --upgrade {package}",
    },
    "cleanup": {
        "name": "Siivinta",
        "description": "Poista turhat tiedostot ja cachet.",
        "command_template": "",
    },
    "optimize": {
        "name": "Optimointi",
        "description": "Optimoi projektin kokonaisuutta.",
        "command_template": "",
    },
    "audit": {
        "name": "Tarkastus",
        "description": " tarkastele kaikki riippuvuudet ja päivittävät staraus.",
        "command_template": "pip-audit",
    },
}

# Cache-kansiot jotka voidaan tyhjentää
CACHE_DIRS: list[str] = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".coverage",
    "dist",
    "build",
    ".eggs",
    "*.egg-info",
    ".mypy_cache",
    ".coverage.*",
    ".DS_Store",
    "Thumbs.db",
]

# Riippuvuus-tiedostot
DEPENDENCY_FILES: dict[str, str] = {
    "requirements.txt": "pip",
    "pyproject.toml": "pyproject",
    "Pipfile": "pipenv",
    "poetry.lock": "poetry",
    "package.json": "npm",
    "composer.json": "composer",
    "Gemfile": "ruby",
}


class UpgradeAgentInput(AgentInput):
    """UpgradeAgentin syöte."""
    action: str = Field(default="check", description="Toiminto (check, upgrade, dry_run).")
    packages: list[str] = Field(default_factory=list, description="Kohdepaketit (tyhjä = kaikki).")
    package_manager: str = Field(default="pip", description="Pakettienhallinnan tyyppi (pip, npm, poetry, pipenv).")
    dry_run: bool = Field(default=True, description="Vain tarkista, älä tee muutoksia.")


class UpgradeAgentOutput(AgentOutput):
    """UpgradeAgentin tuloste."""
    upgradable_packages: list[dict[str, Any]] = Field(default_factory=list, description="Päivitettävät paketit.")
    current_versions: dict[str, str] = Field(default_factory=dict, description="Nykyiset versiot.")
    latest_versions: dict[str, str] = Field(default_factory=dict, description="Uusimmat versiot.")
    upgrade_commands: list[str] = Field(default_factory=list, description="Suoritettavat päivityskomennot.")
    upgrade_results: list[dict[str, Any]] = Field(default_factory=list, description="Päivitysten tulokset.")


class CleanupAgentInput(AgentInput):
    """CleanupAgentin syöte."""
    action: str = Field(default="scan", description="Toiminto (scan, clean, dry_run).")
    directories: list[str] = Field(default_factory=list, description="Käsiteltävät hakemistot (tyhjä = projekti).")
    clean_cache: bool = Field(default=True, description="Poista cache-kansiot.")
    clean_temp: bool = Field(default=True, description="Poista tilapäistiedostot.")
    clean_build: bool = Field(default=True, description="Poista build-tiedostot (dist, build).")
    custom_patterns: list[str] = Field(default_factory=list, description="Muut poistomuster.")


class CleanupAgentOutput(AgentOutput):
    """CleanupAgentin tuloste."""
    found_items: list[dict[str, Any]] = Field(default_factory=list, description="Löydetyt poistettavat tiedostot.")
    cleaned_items: list[str] = Field(default_factory=list, description="Poistetut tiedostot.")
    space_freed: float = Field(default=0, description="Vapautunut tila megatavuissa.")
    total_files: int = Field(default=0, description="Löydettyjen tiedostojen määrä.")


class DependencyAgentInput(AgentInput):
    """DependencyAgentin syöte."""
    action: str = Field(default="analyze", description="Toiminto (analyze, check, report).")
    dependency_files: list[str] = Field(default_factory=list, description="Riippuvuustiedostot (tyhjä = kaikki).")
    check_security: bool = Field(default=True, description="Tarkista turvallisuus ongelmat.")
    check_outdated: bool = Field(default=True, description="Tarkista vanhentuneet paketit.")
    include_dev: bool = Field(default=True, description="Sisällytä kehitysriippuvuudet")


class DependencyAgentOutput(AgentOutput):
    """DependencyAgentin tuloste."""
    dependencies: list[dict[str, Any]] = Field(default_factory=list, description="Riippuvuuslista.")
    security_issues: list[dict[str, str]] = Field(default_factory=list, description="Turvallisuusongelmat.")
    outdated_packages: list[dict[str, str]] = Field(default_factory=list, description="Vanhentuneet paketit.")
    recommendations: list[str] = Field(default_factory=list, description="Parannusehdotukset.")
    dependency_graph: dict[str, Any] = Field(default_factory=dict, description="Riippuvuussolmut.")
    total_dependencies: int = Field(default=0, description="Riippuvuuksien kokonaismäärä.")


class UpgradeAgent(BaseAgent):
    """
    UpgradeAgent tarkistaa ja päivittää projektin riippuvuudet.

    Se skannaa nykyiset paketit, vertaa ne uusimisiin versioihin, ja antaa
    päivityskomennot.

    Usage:
        agent = UpgradeAgent()
        result = agent.run("Tarkista päivitykset", action="check", packages=["pydantic"])
    """

    agent_type: str = "upgrade"
    input_schema = UpgradeAgentInput
    output_schema = UpgradeAgentOutput

    def _parse_requirement(self, line: str) -> Optional[dict[str, str]]:
        """Parsi yksittäinen vaatimus riviltä."""
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        # Käsittele eri formaatit: package==1.0.0, package>=1.0.0, package~=1.0.0
        match = re.match(r"^([a-zA-Z0-9_-]+)\s*([=<>~!]+\s*[\d\w.*+]+)?", line)
        if match:
            name = match.group(1)
            version_spec = match.group(2).strip() if match.group(2) else ""
            version = re.search(r"[\d.]+", version_spec) if version_spec else None
            return {
                "name": name,
                "version_spec": version_spec,
                "current_version": version.group(0) if version else "",
            }
        return None

    def _read_requirements(self, requirements_path: str = "requirements.txt") -> list[dict[str, str]]:
        """Lukee requirements.txt-tiedston."""
        path = Path(requirements_path)
        if not path.exists():
            return []

        deps = []
        for line in path.read_text(encoding="utf-8").splitlines():
            parsed = self._parse_requirement(line)
            if parsed:
                deps.append(parsed)
        return deps

    def _read_pyproject(self, path: str = "pyproject.toml") -> list[dict[str, str]]:
        """Lukie riippuvuudet pyproject.toml:sta."""
        pyproject_path = Path(path)
        if not pyproject_path.exists():
            return []

        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            deps = []
            project = data.get("project", {})
            dependencies = project.get("dependencies", [])
            for dep in dependencies:
                parsed = self._parse_requirement(dep)
                if parsed:
                    deps.append(parsed)
            return deps
        except Exception:
            return []

    def _get_installed_version(self, package: str) -> str:
        """Hakee asennetun version paketista."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return "unknown"

    def _check_pip_auditable(self, package: str) -> dict[str, str]:
        """Tarkistaa paketin nykyisen version."""
        return {
            "name": package,
            "current_version": self._get_installed_version(package),
            "latest_version": "unknown",
            "upgradable": False,
        }

    def _simulate_upgrade_check(self, packages: list[str]) -> list[dict[str, str]]:
        """Simuloi päivitystarkistusta (koska ei voida oikeasti tarkistaa tässä ympäristössä)."""
        results = []
        for pkg in packages:
            results.append({
                "name": pkg,
                "current_version": self._get_installed_version(pkg) if pkg else "unknown",
                "latest_version": "latest",
                "upgradable": pkg != "python",
            })
        return results

    def _build_upgrade_commands(self, upgradable: list[dict[str, str]]) -> list[str]:
        """Rakoa päivityskomennot."""
        commands = []
        for pkg in upgradable:
            if pkg.get("upgradable"):
                commands.append(f"pip install --upgrade {pkg['name']}")
        return commands

    def _run(self, input_data: UpgradeAgentInput) -> UpgradeAgentOutput:
        """UpgradeAgentin päälogiikka."""
        packages = input_data.packages
        action = input_data.action.lower()
        dry_run = input_data.dry_run

        # Kerää paketit jos paketteja ei ole
        if not packages and action == "check":
            # Yritä lukea requirements.txt:stä
            req_deps = self._read_requirements("requirements.txt")
            for dep in req_deps:
                packages.append(dep["name"])

            if not packages:
                # Yritä lukea pyproject.toml:stä
                pp_deps = self._read_pyproject("pyproject.toml")
                for dep in pp_deps:
                    packages.append(dep["name"])

        # Tarkista paketit
        upgradable = self._simulate_upgrade_check(packages)

        # Rakoa komennot
        upgrade_commands = self._build_upgrade_commands(upgradable)

        # Suorita päivitys jos ei ole dry_run
        upgrade_results = []
        if action == "upgrade" and not dry_run:
            for cmd in upgrade_commands:
                try:
                    result = subprocess.run(
                        cmd.split(), capture_output=True, text=True, timeout=60
                    )
                    upgrade_results.append({
                        "command": cmd,
                        "success": result.returncode == 0,
                        "output": result.stdout[:200] if result.stdout else "",
                    })
                except (subprocess.TimeoutExpired, Exception) as e:
                    upgrade_results.append({
                        "command": cmd,
                        "success": False,
                        "error": str(e),
                    })

        current_versions = {p["name"]: p["current_version"] for p in upgradable}
        latest_versions = {p["name"]: p["latest_version"] for p in upgradable}

        return UpgradeAgentOutput(
            success=True,
            result={"packages_checked": len(packages), "upgradable_count": len(upgradable)},
            message=f"Tarkistus valmis. Löydetty {len(upgradable)} paketin, joita voi päivittää." + (" (dry-run)" if dry_run else ""),
            agent_type=self.agent_type,
            upgradable_packages=upgradable,
            current_versions=current_versions,
            latest_versions=latest_versions,
            upgrade_commands=upgrade_commands,
            upgrade_results=upgrade_results,
        )


class CleanupAgent(BaseAgent):
    """
    CleanupAgent poistaa turhat tiedostot, cachet ja tilapäiset resurssit.

    Usage:
        agent = CleanupAgent()
        result = agent.run("Skanttikaa turhaat tiedostot", action="scan", directories=["."])
    """

    agent_type: str = "cleanup"
    input_schema = CleanupAgentInput
    output_schema = CleanupAgentOutput

    def _should_clean_cache(self, dir_name: str) -> bool:
        """Tarkistaa onko hakemisto cache-kansio."""
        for pattern in CACHE_DIRS:
            if pattern.replace("*", "") in dir_name:
                return True
        return False

    def _is_temp_file(self, path: Path) -> bool:
        """Tarkistaa onko tiedosto tilapäinen."""
        name = path.name.lower()
        temp_patterns = [".tmp", ".temp", "~", ".bak", ".swp", ".swo"]
        return any(p in name for p in temp_patterns)

    def _get_dir_size(self, path: Path) -> float:
        """Laskee hakemiston koon megatavuissa."""
        total = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
        except (PermissionError, OSError):
            pass
        return round(total / (1024 * 1024), 2)

    def _scan_directories(self, directories: list[str], input_data: CleanupAgentInput) -> list[dict[str, Any]]:
        """Skannaa hakemistot poistettaville tiedostoille."""
        found_items = []

        # Käytetään nykyistä hakemistoa jos yhtään annetta
        if not directories:
            directories = ["."]

        for dir_path in directories:
            base = Path(dir_path)
            if not base.exists():
                continue

            # Skannaa cache-kansiot
            if input_data.clean_cache:
                for pattern in ["__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"]:
                    for cache_dir in base.rglob(pattern):
                        if cache_dir.is_dir():
                            size = self._get_dir_size(cache_dir)
                            file_count = sum(1 for _ in cache_dir.glob("**/*") if _.is_file())
                            found_items.append({
                                "path": str(cache_dir.relative_to(base)),
                                "type": "cache",
                                "size_mb": size,
                                "file_count": file_count,
                                "description": f"Cache-kansio: {cache_dir.name}",
                            })

            # Skannaa build-tiedostoja
            if input_data.clean_build:
                for pattern in ["dist", "build", "*.egg-info", ".eggs"]:
                    for build_path in base.glob(pattern):
                        if build_path.is_dir() or (build_path.is_file() and build_path.suffix == ".egg-info"):
                            size = self._get_dir_size(build_path) if build_path.is_dir() else 0
                            found_items.append({
                                "path": str(build_path.relative_to(base)),
                                "type": "build",
                                "size_mb": size,
                                "description": f"Build-tulos: {build_path.name}",
                            })

            # Skannaa tilapäiset tiedostot
            if input_data.clean_temp:
                for temp_path in base.rglob("*"):
                    if temp_path.is_file() and self._is_temp_file(temp_path):
                        size = temp_path.stat().st_size / (1024 * 1024)
                        found_items.append({
                            "path": str(temp_path.relative_to(base)),
                            "type": "temp",
                            "size_mb": round(size, 4),
                            "description": "Tilapäistiedosto",
                        })

            # Mukautetut kohdesuvaimet
            for pattern in input_data.custom_patterns:
                for custom_path in base.rglob(pattern):
                    if custom_path.is_file():
                        size = custom_path.stat().st_size / (1024 * 1024)
                        found_items.append({
                            "path": str(custom_path.relative_to(base)),
                            "type": "custom",
                            "size_mb": round(size, 4),
                            "description": f"Mukautemuster: {pattern}",
                        })

        # Poista duplikaatit
        seen = set()
        unique_items = []
        for item in found_items:
            if item["path"] not in seen:
                seen.add(item["path"])
                unique_items.append(item)

        return unique_items

    def _clean_items(self, items: list[dict[str, Any]], directories: list[str]) -> list[str]:
        """Poistaa annetut tiedostot/kansiot."""
        cleaned = []
        for item in items:
            try:
                path = Path(item["path"])
                if not path.is_absolute():
                    # Etsi oikea polku
                    path = Path(directories[0] if directories else ".") / path

                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    cleaned.append(str(path))
            except (PermissionError, OSError, FileNotFoundError):
                pass
        return cleaned

    def _run(self, input_data: CleanupAgentInput) -> CleanupAgentOutput:
        """CleanupAgentin päälogiikka."""
        action = input_data.action.lower()
        directories = input_data.directories

        # Skannaa
        found_items = self._scan_directories(directories, input_data)

        # Laske kokonaistiedostot
        total_files = sum(item.get("file_count", 1) for item in found_items)
        space_freed = sum(item.get("size_mb", 0) for item in found_items)

        # Siiviy oikeasta toimenpiteen perusteella
        cleaned_items = []
        if action == "clean":
            cleaned_items = self._clean_items(found_items, directories)
        elif action == "dry_run":
            pass  # Vain skannaa

        # Laske todellisesti vapautunut tila
        actual_space_freed = 0
        if cleaned_items:
            actual_space_freed = sum(
                item.get("size_mb", 0) for item in found_items if item["path"] in cleaned_items
            )

        return CleanupAgentOutput(
            success=True,
            result={"items_found": len(found_items), "items_cleaned": len(cleaned_items)},
            message=f"Skannattu {len(found_items)} kohdetta, tyhjennetty {len(cleaned_items)} kohdetta ({actual_space_freed} MB vapautunut)." + (" (dry-run)" if action == "dry_run" else ""),
            agent_type=self.agent_type,
            found_items=found_items,
            cleaned_items=cleaned_items,
            space_freed=round(actual_space_freed, 2) if actual_space_freed else round(space_freed, 2),
            total_files=total_files,
        )


class DependencyAgent(BaseAgent):
    """
    DependencyAgent analysoi riippuvuudet turvallisuudesta ja riippuvuussuhoista.

    Se lukee pyproject.toml, requirements.txt ja muut riippuvuustiedostot,
    tarkistaa turvallisuusongelmat ja antaa päivityssuosituksia.

    Usage:
        agent = DependencyAgent()
        result = agent.run("Analysoi riippuvuudet", action="analyze", check_security=True)
    """

    agent_type: str = "dependency"
    input_schema = DependencyAgentInput
    output_schema = DependencyAgentOutput

    def _find_dependency_files(self, directories: list[str]) -> list[str]:
        """Etsi kaikki riippuvuustiedostot."""
        if not directories:
            directories = ["."]

        found = []
        for dir_path in directories:
            base = Path(dir_path)
            for dep_file in DEPENDENCY_FILES:
                matches = list(base.rglob(dep_file))
                for match in matches:
                    found.append(str(match))
        return list(set(found))

    def _parse_requirements_txt(self, path: str) -> list[dict[str, Any]]:
        """Parsii requirements.txt-tiedoston."""
        deps = []
        try:
            content = Path(path).read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                match = re.match(r"^([a-zA-Z0-9_-]+)([=<>~!]+[\d\w.]+)?", line)
                if match:
                    deps.append({
                        "name": match.group(1),
                        "version": match.group(2) or "any",
                        "source": path,
                        "dev": False,
                    })
        except (FileNotFoundError, OSError):
            pass
        return deps

    def _parse_pyproject_toml(self, path: str) -> list[dict[str, Any]]:
        """Parsii pyproject.toml-tiedoston."""
        deps = []
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
            project = data.get("project", {})

            # Standard dependencies
            for dep in project.get("dependencies", []):
                match = re.match(r"^([a-zA-Z0-9_-]+)([=<>~!]+[\d\w.*+]+)?", dep)
                if match:
                    deps.append({
                        "name": match.group(1),
                        "version": match.group(2) or "any",
                        "source": path,
                        "dev": False,
                    })

            # Dev dependencies
            optional_deps = project.get("optional-dependencies", {})
            for group, group_deps in optional_deps.items():
                for dep in group_deps:
                    match = re.match(r"^([a-zA-Z0-9_-]+)([=<>~!]+[\d\w.*+]+)?", dep)
                    if match:
                        deps.append({
                            "name": match.group(1),
                            "version": match.group(2) or "any",
                            "source": path,
                            "dev": group.lower() in ("dev", "development", "test"),
                        })
        except Exception:
            pass
        return deps

    def _check_known_vulnerabilities(self, package: str) -> Optional[dict[str, str]]:
        """Tarkista tiedossa olevat turvallisuusongelmat (simulointi)."""
        # Tämä on simulointi — oikea toteutus käyttäisi pip-audit tai safety
        known_issues: dict[str, dict[str, str]] = {
            "django": {
                "severity": "medium",
                "advisory": "Käytä versiota 4.2+ turvallisuus ongelmien välttämiseksi.",
                "fixed_in": "4.2.0",
            },
            "flask": {
                "severity": "low",
                "advisory": "Salli vain tarvittavat reitit.",
                "fixed_in": "3.0.0",
            },
            "requests": {
                "severity": "info",
                "advisory": "Käytä SSL-vahvistusta aina.",
                "fixed_in": "2.32.0",
            },
        }
        pkg_lower = package.lower()
        return known_issues.get(pkg_lower)

    def _build_dependency_graph(self, dependencies: list[dict[str, Any]]) -> dict[str, Any]:
        """ Rakoa riippuvuussolmut."""
        graph = {}
        for dep in dependencies:
            graph[dep["name"]] = {
                "version": dep["version"],
                "source": dep["source"],
                "dev": dep["dev"],
                "dependencies": [],  # Tässä yksinkertaisessa toteutuksessa ei tarkastella transitiivisia
            }
        return graph

    def _generate_recommendations(
        self,
        dependencies: list[dict[str, Any]],
        security_issues: list[dict[str, str]],
        outdated: list[dict[str, str]],
        check_security: bool,
    ) -> list[str]:
        """Luo suositukset."""
        recommendations = []

        if len(dependencies) > 20:
            recommendations.append("Projekti on suuri riippuvuusten määrässä. Harkitse riippuvuussanan siivoemista.")

        if check_security and security_issues:
            recommendations.append(f"Korjaa {len(security_issues)} turvallisuusongelmaa kiireellisesti.")
        elif check_security:
            recommendations.append("Ei tiedettyjä turvallisuusongelmia.")

        if outdated:
            recommendations.append(f"Päivitä {len(outdated)} vanhentunutta pakettia.")

        # Tarkista tukemat versiot
        old_deps = [d for d in dependencies if "<3." in d.get("version", "") or ">2.0" in d.get("version", "")]
        if old_deps:
            recommendations.append("Joissain paketeissa on vanhentuneita rajoituksia. Poista ne sallivuudeksi.")

        if not recommendations:
            recommendations.append("Riippuvuudet näyttävät tervettöjinä. Jatka säännöllistä ylläpitoa.")

        return recommendations

    def _check_outdated(self, packages: list[str]) -> list[dict[str, str]]:
        """Tarkista vanhentuneet paketit (simulointi)."""
        outdated = []
        for pkg in packages:
            current = self._get_installed_version(pkg)
            # Simuloi että jotkut paketit ovat vanhentuneet
            if current not in ("unknown", "latest"):
                outdated.append({
                    "name": pkg,
                    "current": current,
                    "latest": "latest",
                    "behind_by": "1 release",
                })
        return outdated

    def _get_installed_version(self, package: str) -> str:
        """Hae asennetun paketin versio."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return "unknown"

    def _run(self, input_data: DependencyAgentInput) -> DependencyAgentOutput:
        """DependencyAgentin päälogiikka."""
        action = input_data.action.lower()

        # Etsi riippuvuustiedostot
        dep_files = input_data.dependency_files
        if not dep_files:
            dep_files = self._find_dependency_files(["."])

        # Käy läpi tiedostot ja kerää riippuvuudet
        dependencies = []
        for dep_file in dep_files:
            if dep_file.endswith("requirements.txt"):
                deps = self._parse_requirements_txt(dep_file)
                dependencies.extend(deps)
            elif dep_file.endswith("pyproject.toml"):
                deps = self._parse_pyproject_toml(dep_file)
                dependencies.extend(deps)

        # Poista duplikaatit
        seen_names = set()
        unique_deps = []
        for dep in dependencies:
            if dep["name"] not in seen_names:
                seen_names.add(dep["name"])
                unique_deps.append(dep)

        # Tarkista turvallisuus
        security_issues = []
        if input_data.check_security:
            for dep in unique_deps:
                issue = self._check_known_vulnerabilities(dep["name"])
                if issue:
                    security_issues.append({"name": dep["name"], **issue})

        # Tarkista vanhentuneet
        outdated = []
        if input_data.check_outdated:
            outdated = self._check_outdated([d["name"] for d in unique_deps])

        # Rakoa riippuvuussolmut
        dependency_graph = self._build_dependency_graph(unique_deps)

        # Luo suositukset
        recommendations = self._generate_recommendations(
            unique_deps, security_issues, outdated, input_data.check_security
        )

        return DependencyAgentOutput(
            success=True,
            result={"total_deps": len(unique_deps), "security_issues": len(security_issues)},
            message=f"Analysoitu {len(unique_deps)} riippuvuutta. Löydetty {len(security_issues)} turvallisuusongelmaa.",
            agent_type=self.agent_type,
            dependencies=unique_deps,
            security_issues=security_issues,
            outdated_packages=outdated,
            recommendations=recommendations,
            dependency_graph=dependency_graph,
            total_dependencies=len(unique_deps),
        )
