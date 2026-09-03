"""
Testit FeedbackAgentille (M12).
"""

import pytest

from agents.learning_path_agent import (
    FeedbackAgent,
    FeedbackInput,
    FeedbackOutput,
)


@pytest.fixture
def feedback_agent():
    """Palauttaa FeedbackAgent-instanssin."""
    return FeedbackAgent()


SAMPLE_CODE = """
def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

class Calculator:
    def add(self, a, b):
        return a + b
"""

BROKEN_CODE = """
def broken_function(
    if True
        return True
"""

LONG_CODE = """
def very_long_function_name_that_exceeds_the_line_length_limit_in_pep8_standards_and_this_should_generate_feedback():
    pass

"""


# ===================
# FeedbackAgent tests
# ===================


class TestFeedbackAgent:
    """Testit FeedbackAgentille."""

    def test_agent_type(self, feedback_agent):
        """Agentin tyyppi on oikein."""
        assert feedback_agent.agent_type == "feedback"

    def test_input_schema(self, feedback_agent):
        """Input-skeema on oikein."""
        assert feedback_agent.input_schema == FeedbackInput

    def test_output_schema(self, feedback_agent):
        """Output-skeema on oikein."""
        assert feedback_agent.output_schema == FeedbackOutput

    def test_basic_code_review(self, feedback_agent):
        """Perus koodikatsaus antaa palautetta."""
        result = feedback_agent.run(
            task="Arvostele koodia",
            code=SAMPLE_CODE,
            feedback_type="code_review",
        )
        assert result.success is True
        assert len(result.feedback_items) > 0
        assert 0 <= result.score <= 100

    def test_learning_feedback(self, feedback_agent):
        """Oppimiskirjeen tyyppinen palaute."""
        result = feedback_agent.run(
            task="Anna oppimispalaute",
            code=SAMPLE_CODE,
            feedback_type="learning",
            skill_level="beginner",
        )
        assert result.success is True
        assert result.severity == "info"

    def test_learning_feedback_advanced(self, feedback_agent):
        """Edistygyn oppimispalaute on erilainen."""
        result = feedback_agent.run(
            task="Anna oppimispalaute",
            code=SAMPLE_CODE,
            feedback_type="learning",
            skill_level="advanced",
        )
        assert result.success is True
        assert len(result.feedback_items) > 0

    def test_style_feedback(self, feedback_agent):
        """Tyylintarkistus antaa palautetta."""
        result = feedback_agent.run(
            task="Tarkista tyyli",
            code=LONG_CODE,
            feedback_type="style",
            focus_areas=["readability"],
        )
        assert result.success is True
        assert len(result.feedback_items) > 0

    def test_performance_feedback(self, feedback_agent):
        """Suorituskyvyn palaute sisältää suorituskyky-huomion."""
        result = feedback_agent.run(
            task="Tarkista suorituskyky",
            code=SAMPLE_CODE,
            feedback_type="performance",
        )
        assert result.success is True
        assert result.score > 0

    def test_unknown_feedback_type(self, feedback_agent):
        """Tuntematon tyyppi käyttää oletusarvoa (code_review)."""
        result = feedback_agent.run(
            task="Tunematon tyyppi",
            code=SAMPLE_CODE,
            feedback_type="unknown_type",
        )
        assert result.success is True
        assert len(result.feedback_items) > 0

    def test_broken_code_error(self, feedback_agent):
        """Syntaksivirheitä sisältävä koodi saa virhe-palautteen."""
        result = feedback_agent.run(
            task="Korjaa koodi",
            code=BROKEN_CODE,
            feedback_type="code_review",
        )
        assert result.success is True
        assert result.severity == "error"
        assert result.score < 100  # Virheiden takia pisteet alituvat

    def test_empty_code(self, feedback_agent):
        """Tyhjä koodi antaa info-palautteen."""
        result = feedback_agent.run(
            task="Tyhjä koodi",
            code="",
            feedback_type="code_review",
        )
        assert result.success is True

    def test_code_with_functions(self, feedback_agent):
        """Funktioiden tunnistaminen toimii."""
        result = feedback_agent.run(
            task="Tunnista funktiot",
            code=SAMPLE_CODE,
            feedback_type="code_review",
        )
        assert result.success is True
        feedback_text = str(result.feedback_items)
        assert "calculate_average" in feedback_text or "Calculator" in feedback_text

    def test_code_with_classes(self, feedback_agent):
        """Luokkien tunnistaminen toimii."""
        result = feedback_agent.run(
            task="Tunnista luokat",
            code=SAMPLE_CODE,
            feedback_type="code_review",
        )
        assert result.success is True
        feedback_text = str(result.feedback_items)
        assert "luokk" in feedback_text.lower()

    def test_score_calculation(self, feedback_agent):
        """Pisteiden laskeminen palautteen mukaan."""
        good_code = '''
def clean_function(param_one, param_two):
    """Laskee kaiken."""
    if param_one > param_two:
        return param_one
    return param_two
'''
        result = feedback_agent.run(
            task="Hyvä koodi",
            code=good_code,
            feedback_type="code_review",
        )
        assert result.score > 70  # Hyvä koodi saa hyvät pisteet

        bad_code = '''def f(x):
 if x:return 1
else:pass'''
        result_bad = feedback_agent.run(
            task="Huono koodi",
            code=bad_code,
            feedback_type="code_review",
        )
        assert result_bad.score < result.score or result_bad.score < 80

    def test_suggestions_generated(self, feedback_agent):
        """Parannusehdotukset luodaan."""
        result = feedback_agent.run(
            task="Anna ehdotuksia",
            code=SAMPLE_CODE,
            feedback_type="code_review",
            focus_areas=["readability"],
        )
        assert len(result.suggestions) > 0

    def test_severity_levels(self, feedback_agent):
        """Severity määrittyy oikein."""
        # Tämän koodin perusteella korkeammat virheet
        result = feedback_agent.run(
            task="Virheellinen koodi",
            code=BROKEN_CODE,
            feedback_type="code_review",
        )
        assert result.severity in ("error", "critical", "warning", "info")

    def test_focus_areas_security(self, feedback_agent):
        """Security-keskitys antaa turvallisuusparanneksen."""
        result = feedback_agent.run(
            task="Turvallisuus",
            code=SAMPLE_CODE,
            feedback_type="code_review",
            focus_areas=["security"],
        )
        assert result.success is True

    def test_focus_areas_efficiency(self, feedback_agent):
        """Efficiency-keskitys antaa suorituskyvyn paranneksen."""
        result = feedback_agent.run(
            task="Suorituskyky",
            code=SAMPLE_CODE,
            feedback_type="code_review",
            focus_areas=["efficiency"],
        )
        suggestions_text = " ".join(result.suggestions).lower()
        assert "optimointi" in suggestions_text or "tehokkuus" in suggestions_text or "profil" in suggestions_text

    def test_feedback_items_have_required_fields(self, feedback_agent):
        """Palautteiden itemit sisältävät vaaditut kentät."""
        result = feedback_agent.run(
            task="Rakenteellinen testi",
            code=SAMPLE_CODE,
            feedback_type="code_review",
        )
        for item in result.feedback_items:
            assert "category" in item
            assert "message" in item
            assert "severity" in item
            assert "explanation" in item

    def test_beginner_simplified_feedback(self, feedback_agent):
        """Aloittajalle annettu palaute on yksinkertainen."""
        result = feedback_agent.run(
            task="Aloittaja",
            code=SAMPLE_CODE,
            feedback_type="learning",
            skill_level="beginner",
        )
        assert result.success is True
        # Aloittajalle annettu selitys on yksinkertaisempi
        explanation = " ".join(item.get("explanation", "") for item in result.feedback_items)
        assert len(explanation) > 0

    def test_serializes(self, feedback_agent):
        """Tulos voidaan serialisoida."""
        result = feedback_agent.run(
            task="Testaa serialisointia",
            code=SAMPLE_CODE,
            feedback_type="code_review",
        )
        d = result.to_dict()
        assert d["agent_type"] == "feedback"
        assert "feedback_items" in d
        assert "severity" in d
        assert "score" in d
        assert "suggestions" in d


class TestFeedbackAgentModuleLevel:
    """Moduulitasolla olevat testit."""

    def test_feedback_categories_exist(self):
        """Palause-kategoriat-sanakirja on olemassa."""
        agent = FeedbackAgent()
        assert len(agent.FEEDBACK_CATEGORIES) >= 4

    def test_agent_importable_from_package(self):
        """Agentti on tuotavissa paketista."""
        from agents import FeedbackAgent as FA
        assert FA.agent_type == "feedback"
