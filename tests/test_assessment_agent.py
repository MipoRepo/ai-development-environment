"""
Testit AssessmentAgentille (M12).
"""

import pytest

from agents.learning_path_agent import (
    AssessmentAgent,
    AssessmentInput,
    AssessmentOutput,
    ASSESSMENT_CRITERIA,
)


@pytest.fixture
def assessment_agent():
    """Palauttaa AssessmentAgent-instanssin."""
    return AssessmentAgent()


SAMPLE_CODE = """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)
"""


# ===================
# AssessmentAgent tests
# ===================


class TestAssessmentAgent:
    """Testit AssessmentAgentille."""

    def test_agent_type(self, assessment_agent):
        """Agentin tyyppi on oikein."""
        assert assessment_agent.agent_type == "assessment"

    def test_input_schema(self, assessment_agent):
        """Input-skeema on oikein."""
        assert assessment_agent.input_schema == AssessmentInput

    def test_output_schema(self, assessment_agent):
        """Output-skeema on oikein."""
        assert assessment_agent.output_schema == AssessmentOutput

    def test_basic_quiz_generation(self, assessment_agent):
        """Kyselyn generointi toimii."""
        result = assessment_agent.run(
            task="Luo kysely",
            assessment_type="quiz",
            topic="python",
            skill_level="beginner",
            num_items=3,
        )
        assert result.success is True
        assert result.total_items == 3
        assert len(result.assessments) == 3
        assert all("question" in item for item in result.assessments)

    def test_coding_challenge(self, assessment_agent):
        """Koodaushaasteen generointi toimii."""
        result = assessment_agent.run(
            task="Luo koodaushaaste",
            assessment_type="coding_challenge",
            topic="python",
            skill_level="beginner",
            num_items=2,
        )
        assert result.success is True
        assert result.total_items == 2
        assert all("description" in item for item in result.assessments)

    def test_project_review(self, assessment_agent):
        """Projektin arviointi toimii koodikontekstin kanssa."""
        result = assessment_agent.run(
            task="Arvioi projekti",
            assessment_type="project_review",
            topic="python",
            skill_level="beginner",
            num_items=2,
            context_text=SAMPLE_CODE,
        )
        assert result.success is True
        assert result.total_items == 2
        for item in result.assessments:
            assert "context_analysis" in item

    def test_project_review_without_code(self, assessment_agent):
        """Projektin arviointi toimii ilman koodia."""
        result = assessment_agent.run(
            task="Arvioi projekti",
            assessment_type="project_review",
            topic="python",
            num_items=1,
        )
        assert result.success is True

    def test_peer_review(self, assessment_agent):
        """Peer Review -tyyppi toimii."""
        result = assessment_agent.run(
            task="Peer Review",
            assessment_type="peer_review",
            topic="python",
            num_items=3,
        )
        assert result.success is True
        assert all(item.get("type") == "peer_review" for item in result.assessments)

    def test_unknown_assessment_type(self, assessment_agent):
        """Tuntematon tyyppi antaa oletusarvon (quiz)."""
        result = assessment_agent.run(
            task="Tunematon tyyppi",
            assessment_type="unknown_type",
            topic="python",
            num_items=2,
        )
        assert result.success is True
        assert result.total_items == 2

    def test_previous_scores_adjustment(self, assessment_agent):
        """Edelliset pisteet säätelevät vaikeutta."""
        # Hyvät pisteet → vaikeampi
        result_high = assessment_agent.run(
            task="Korkeat pisteet",
            assessment_type="quiz",
            topic="python",
            previous_scores=[90, 85, 92],
            num_items=3,
        )
        assert all(item.get("difficulty_adjustment") == "harder" for item in result_high.assessments)

        # Heikot pisteet → helpompi
        result_low = assessment_agent.run(
            task="Madalat pisteet",
            assessment_type="quiz",
            topic="python",
            previous_scores=[30, 40, 20],
            num_items=3,
        )
        assert all(item.get("difficulty_adjustment") == "easier" for item in result_low.assessments)

        # Keskiverto → sama
        result_mid = assessment_agent.run(
            task="Keskipisteet",
            assessment_type="quiz",
            topic="python",
            previous_scores=[60, 65, 70],
            num_items=3,
        )
        assert all(item.get("difficulty_adjustment") == "same" for item in result_mid.assessments)

    def test_no_previous_scores(self, assessment_agent):
        """Ilman aikaisempia pisteitä ei ole säädöstä."""
        result = assessment_agent.run(
            task="Ei pisteitä",
            assessment_type="quiz",
            topic="python",
            num_items=3,
        )
        assert result.success is True
        assert not any("difficulty_adjustment" in item for item in result.assessments)

    def test_criteria_for_beginner(self, assessment_agent):
        """Aloittelijan kriteerit ovat oikein."""
        result = assessment_agent.run(
            task="Aloittava",
            assessment_type="quiz",
            topic="python",
            skill_level="beginner",
            num_items=2,
        )
        assert "comprehension" in result.criteria
        assert "accuracy" in result.criteria

    def test_criteria_for_advanced(self, assessment_agent):
        """Edistyneen kriteerit painottuivät ymmärrykseen."""
        result = assessment_agent.run(
            task="Edistynyt",
            assessment_type="quiz",
            topic="python",
            skill_level="advanced",
            num_items=2,
        )
        assert result.criteria["comprehension"] == 0.6

    def test_average_difficulty_calculated(self, assessment_agent):
        """Keskimääräinen vaikeus lasketaan."""
        result = assessment_agent.run(
            task="Vaikeus",
            assessment_type="quiz",
            topic="python",
            skill_level="beginner",
            num_items=3,
        )
        assert result.average_difficulty > 0

    def test_exercise_uses_num_items(self, assessment_agent):
        """Kyselytusten määrä noudattaa num_items-parametria."""
        for n in [1, 3, 5, 10]:
            result = assessment_agent.run(
                task=f"Testaa määrä {n}",
                assessment_type="quiz",
                topic="python",
                num_items=n,
            )
            assert result.total_items == n

    def test_serializes(self, assessment_agent):
        """Tulos voidaan serialisoida."""
        result = assessment_agent.run(
            task="Testaa serialisointia",
            assessment_type="quiz",
            topic="python",
            num_items=2,
        )
        d = result.to_dict()
        assert d["agent_type"] == "assessment"
        assert "assessments" in d
        assert "criteria" in d
        assert "average_difficulty" in d


class TestAssessmentModuleLevel:
    """Moduulitasolla olevat testit."""

    def test_assessment_criteria_exist(self):
        """Arviointikriteerit-sanakirja on olemassa."""
        assert len(ASSESSMENT_CRITERIA) >= 3

    def test_agent_importable_from_package(self):
        """Agentti on tuotavissa paketista."""
        from agents import AssessmentAgent as AA
        assert AA.agent_type == "assessment"
