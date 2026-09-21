---
name: maintenance-m14
description: M14 Maintenance -agentit (Upgrade, Cleanup, Dependency) ja käyttöohjeet
metadata:
  type: project
---

# M14 — Maintenance: Järjestelmän ylläpito, päivitykset ja optimointi

## Agentit

### UpgradeAgent (`agents/maintenance_agent.py`)
- `agent_type="upgrade"`
- Tarkistaa ja päivittää projektin riippuvuudet.
- **Toiminnot:** `check`, `upgrade`, `dry_run`
- **Syöte:** `UpgradeAgentInput` (action, packages, package_manager, dry_run)
- **Tuloste:** `UpgradeAgentOutput` (upgradable_packages, current_versions, latest_versions, upgrade_commands, upgrade_results)
- Lukee `requirements.txt` ja `pyproject.toml` riippuvuudet
- Käyttää `tomllib` (sisäänrakennettu Python 3.11:ssa) pyproject.toml-parsintaan

### CleanupAgent (`agents/maintenance_agent.py`)
- `agent_type="cleanup"`
- Poistaa turhat tiedostot, cachet ja tilapäiset resurssit.
- **Toiminnot:** `scan`, `clean`, `dry_run`
- **Syöte:** `CleanupAgentInput` (action, directories, clean_cache, clean_temp, clean_build, custom_patterns)
- **Tuloste:** `CleanupAgentOutput` (found_items, cleaned_items, space_freed, total_files)
- Skannaa: `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `dist`, `build`, `*.egg-info`, `.DS_Store`, `Thumbs.db`
- Tilapäistiedostot: `.tmp`, `.temp`, `~`, `.bak`, `.swp`, `.swo`
- Laskee vapautuneen tilan (MB) ja tiedostomäärät

### DependencyAgent (`agents/maintenance_agent.py`)
- `agent_type="dependency"`
- Analysoi riippuvuudet turvallisuudesta ja riippuvuussuhteista.
- **Toiminnot:** `analyze`, `check`, `report`
- **Syöte:** `DependencyAgentInput` (action, dependency_files, check_security, check_outdated, include_dev)
- **Tuloste:** `DependencyAgentOutput` (dependencies, security_issues, outdated_packages, recommendations, dependency_graph, total_dependencies)
- Parsii: `requirements.txt`, `pyproject.toml`, `Pipfile`, `poetry.lock`, `package.json`, `composer.json`, `Gemfile`
- Tunnetut turvallisuusongelmat: django, flask, requests
- Rakentaa riippuvuussolmut (graph)

## Vakiot

- `MAINTENANCE_ACTIONS`: 4 ylläpitotoimenpidettä (upgrade, cleanup, optimize, audit)
- `CACHE_DIRS`: 12 cache-/build-kansiota/mallia
- `DEPENDENCY_FILES`: 7 riippuvuustiedoston muotoa (requirements.txt, pyproject.toml, Pipfile, jne.)

## Korjaukset (Alpha 2.4)

- **tomllib**: `pyproject_parser`-kirjasto korvattu sisäänrakennetulla `tomllib`-moduulilla (Python 3.11+)
- **upgradable_packages tyypitys**: korjattu `list[dict[str, Any]]`-tyypiksi
- **_parse_requirement**: palauttaa tyhjän version ilman versiomäärää oikein

## Testaus

- 46 testiä: `tests/test_maintenance_agent.py`
- 655 testiä kaikkiaan (Alpha 2.4)
- Kaikki testit läpäisti

## Miksi:

M14 tarjoaa projektin ylläpidon — riippuvuuksien päivitykset, turmien siivinta ja riippuvuusanalyysin. Tämä pitää projektin terveänä ja ajan tasalla.

## Kuinka sovellettavaksi:

```python
from agents import UpgradeAgent, CleanupAgent, DependencyAgent

# Tarkista päivitettävät paketit
up = UpgradeAgent()
result = up.run("Tarkista", action="check", packages=["pydantic", "fastapi"])

# Skannaa turhat tiedostot
clean = CleanupAgent()
result = clean.run("Skannaa", action="scan", directories=["."])

# Analysoi riippuvuudet
dep = DependencyAgent()
result = dep.run("Analysoi", action="analyze", check_security=True, check_outdated=True)
```