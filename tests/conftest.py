"""
Pytest-asetukset ja fixturet AIDE:n testeille.
"""

import os
import sys
from pathlib import Path

# Lisätään projekti polkuun testien aikana
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# Aseta testi-ympyristömuuttujat (jos .env puuttuu)
os.environ.setdefault("OPENROUTER_API_KEY", "sk-or-v1-test-key")
os.environ.setdefault("DEFAULT_MODEL", "openai/gpt-4o-mini")

from pytest import fixture


@fixture
def mock_api_key(monkeypatch):
    """Asettaa testi-API-avaimen."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-test-key")
    return "sk-or-v1-test-key"


@fixture
def workflow_dir() -> str:
    """Palauttaa workflow-kansion polkin."""
    return str(ROOT / "workflows")


@fixture
def sample_task() -> str:
    """Palauttaa testiaikaisen tehtävän."""
    return "Lisää projektiin authentication-mekaniikka."


@fixture
def sample_bugfix_task() -> str:
    """Palauttaa bugfix-tehtävän."""
    return "Korjaa bugi, jossa sovellus kaatuu kirjautumisessa."


@fixture
def sample_project_task() -> str:
    """Palauttaa uuden projektin luomistehtävän."""
    return "Luo uusi Python-API-projekti nimeltä TestAPI."
