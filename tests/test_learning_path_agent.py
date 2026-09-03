"""
Testit LearningPathAgentille (M12).
"""

import hashlib

import pytest

from agents.learning_path_agent import (
    LearningPathAgent,
    LearningPathAgentInput,
    LearningPathAgentOutput,
    PATH_STRATEGIES,
)


@pytest.fixture
def learning_path_agent():
    """Palauttaa LearningPathAgent-instanssin."""
    return LearningPathAgent()


@pytest.fixture
def learning_path_agent_with_progress():
    """Palauttaa LearningPathAgent-instanssin edistymispäätöksillä."""
    return LearningPathAgent()


# ===================
# LearningPathAgent tests
# ===================


class TestLearningPathAgent:
    """Testit LearningPathAgentille."""

    def test_agent_type(self, learning_path_agent):
        """Agentin tyyppi on oikein."""
        assert learning_path_agent.agent_type == "learning_path"

    def test_input_schema(self, learning_path_agent):
        """Input-skeema on oikein."""
        assert learning_path_agent.input_schema == LearningPathAgentInput

    def test_output_schema(self, learning_path_agent):
        """Output-skeema on oikein."""
        assert learning_path_agent.output_schema == LearningPathAgentOutput

    def test_basic_path_creation(self, learning_path_agent):
        """Perusoppimispolan luominen toimii."""
        result = learning_path_agent.run(
            task="Luon oppimispolan",
            context={"topic": "python"},
            current_skill_level="beginner",
            target_skill_level="intermediate",
        )
        assert result.success is True
        assert result.path_id  # Ei-tyhjä
        assert len(result.modules) > 0
        assert result.estimated_duration_hours > 0

    def test_path_id_is_unique(self, learning_path_agent):
        """Erillaiset käyttäjät saavat eri polkunimet."""
        result1 = learning_path_agent.run(
            task="Luon oppimispolan",
            context={"topic": "python"},
            user_id="user1",
        )
        result2 = learning_path_agent.run(
            task="Luon oppimispolan",
            context={"topic": "python"},
            user_id="user2",
        )
        assert result1.path_id != result2.path_id

    def test_progress_calculation(self, learning_path_agent):
        """Edistymisen laskeminen toimii."""
        result = learning_path_agent.run(
            task="Tarkista edistymisen",
            context={"topic": "python"},
            current_progress={
                "completed_modules": ["module_1"],
                "in_progress_module": "module_2",
            },
        )
        assert result.progress_percentage > 0

    def test_progress_percentage_max_100(self, learning_path_agent):
        """Edistymisen prosentti ei ylitä 100."""
        result = learning_path_agent.run(
            task="Tarkista edistymisen",
            context={"topic": "python"},
            current_progress={
                "completed_modules": ["module_1", "module_2", "module_3"],
            },
        )
        assert result.progress_percentage <= 100

    def test_strategy_selection(self, learning_path_agent):
        """Strategian valinta toimii preferoidun strategian perusteella."""
        result = learning_path_agent.run(
            task="Valitse strategia",
            context={"topic": "python"},
            preferred_strategy="hands_on",
        )
        assert result.success is True

    def test_interests_filtering(self, learning_path_agent):
        """Kiinnostukset vaikuttavat moduuleihin."""
        result = learning_path_agent.run(
            task="Ota kiinnostukset huomioon",
            context={"topic": "python"},
            interests=["web-dev", "security"],
        )
        assert result.success is True
        assert len(result.modules) > 0

    def test_next_recommendation(self, learning_path_agent):
        """Seuraava suositus luodaan."""
        result = learning_path_agent.run(
            task="Anna suositus",
            context={"topic": "python"},
            current_skill_level="beginner",
            target_skill_level="advanced",
        )
        assert len(result.next_recommendation) > 0

    def test_advanced_path(self, learning_path_agent):
        """Edistyneen oppimispolan luominen."""
        result = learning_path_agent.run(
            task="Luo edistykseen",
            context={"topic": "python"},
            current_skill_level="advanced",
            target_skill_level="advanced",
        )
        assert result.success is True

    def test_full_progress(self, learning_path_agent):
        """Kun kaikki moduulit suoritettu, näytä onnitus."""
        result = learning_path_agent.run(
            task="Kaikki valmis",
            context={"topic": "python"},
            current_progress={
                "completed_modules": ["module_1", "module_2"],
            },
        )
        assert "valmis" in result.next_recommendation.lower() or "onn" in result.next_recommendation.lower()

    def test_serializes(self, learning_path_agent):
        """Tulos voidaan serialisoida."""
        result = learning_path_agent.run(
            task="Testaa serialisointia",
            context={"topic": "python"},
        )
        d = result.to_dict()
        assert d["agent_type"] == "learning_path"
        assert "path_id" in d
        assert "modules" in d
        assert "estimated_duration_hours" in d


class TestLearningPathAgentModuleLevel:
    """Moduulitasolla olevat testit."""

    def test_path_strategies_exist(self):
        """Strategiat-sanakirja on olemassa."""
        assert len(PATH_STRATEGIES) >= 3

    def test_strategies_have_weights(self):
        """Jokaisella strategiavainnilla on painot."""
        for strategy, config in PATH_STRATEGIES.items():
            assert "name" in config
            assert "description" in config
            assert "weight_code_reading" in config
            assert "weight_exercises" in config
            assert "weight_theory" in config

    def test_agent_importable_from_package(self):
        """Agentti on tuotavissa paketista."""
        from agents import LearningPathAgent as LPA
        assert LPA.agent_type == "learning_path"
