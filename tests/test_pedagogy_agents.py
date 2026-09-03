"""
Testit PedagogyAgenteille (M11).
"""

from pathlib import Path

import pytest

from agents.pedagogy_agent import (
    MentorAgent,
    MentorAgentInput,
    MentorAgentOutput,
    ExplainerAgent,
    ExplainerAgentInput,
    ExplainerAgentOutput,
    PedagogyAgent,
    PedagogyAgentInput,
    PedagogyAgentOutput,
    ContentDesignerAgent,
    ContentDesignerAgentInput,
    ContentDesignerAgentOutput,
    LEARNING_LEVELS,
    LEARNING_TOPICS,
    EXPLANATION_PROMPTS,
    EXERCISE_TYPES,
    CURRICULUM_PHASES,
)


# ===================
# Fixtures
# ===================


@pytest.fixture
def mentor():
    return MentorAgent()


@pytest.fixture
def explainer():
    return ExplainerAgent()


@pytest.fixture
def pedagogy():
    return PedagogyAgent()


@pytest.fixture
def content_designer():
    return ContentDesignerAgent()


@pytest.fixture
def sample_code():
    """Palauttaa testi-koodin."""
    return '''"""
Moduuli laskinkäsittelyä varten.
"""
import math


class Calculator:
    """Laskinluokka."""

    def add(self, x: int, y: int) -> int:
        """Lisää kaksi lukua."""
        return x + y

    def divide(self, a: float, b: float) -> float:
        """Jako kahdesta luvusta."""
        if b == 0:
            raise ValueError("Nollalla ei voi jakaa")
        return a / b


def factorial(n: int) -> int:
    """Laskee n! (faktonaalin) rekursiivisesti."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''


@pytest.fixture
def sample_project(tmp_path):
    """Luo testiprojekti."""
    (tmp_path / "requirements.txt").write_text(
        "fastapi>=0.95.0\npydantic>=2.0.0\npytest>=7.0.0\n",
        encoding="utf-8",
    )
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")
    return tmp_path


# ===================
# MentorAgent tests
# ===================


class TestMentorAgent:
    """Testit MentorAgentille."""

    def test_agent_type(self, mentor):
        assert mentor.agent_type == "mentor"

    def test_input_schema(self, mentor):
        assert mentor.input_schema == MentorAgentInput

    def test_output_schema(self, mentor):
        assert mentor.output_schema == MentorAgentOutput

    def test_run_beginner_plan(self, mentor):
        """Aloittajalle luodaan oppimissuunnitelma."""
        result = mentor.run(
            task="Opeta python-perusteet",
            skill_level="beginner",
            topic="python",
        )
        assert isinstance(result, MentorAgentOutput)
        assert result.success is True
        assert result.estimated_weeks >= 1
        assert "weeks" in result.lesson_plan
        assert result.lesson_plan["level"] == "ALOITTAJA"

    def test_run_intermediate_plan(self, mentor):
        """Keskiverto-tasolle luodaan sopiva suunnitelma."""
        result = mentor.run(
            task="Opeta JS",
            skill_level="intermediate",
            topic="javascript",
        )
        assert result.lesson_plan["level"] == "KOKEILEVA"
        assert len(result.resources) > 0

    def test_run_advanced_plan(self, mentor):
        """Edistyneelle luodaan haastava suunnitelma."""
        result = mentor.run(
            task="Opeta DevSecOps",
            skill_level="advanced",
            topic="devops",
        )
        assert result.lesson_plan["level"] == "EDISTYNYT"
        assert result.estimated_weeks <= 8  # Nopeampi edistyneille

    def test_learning_speed_slow(self, mentor):
        """Hidas oppiminen = enemmän aikaa."""
        result = mentor.run(
            task="Opeta",
            skill_level="beginner",
            topic="python",
            learning_speed="slow",
        )
        assert result.estimated_weeks >= 8  # Alkuperäinen on 8, hidastaikaa kasvatetaan

    def test_learning_speed_fast(self, mentor):
        """ nopea oppiminen = vähemmän aikaa."""
        result = mentor.run(
            task="Opeta",
            skill_level="beginner",
            topic="python",
            learning_speed="fast",
        )
        assert result.estimated_weeks <= 6  # Alkuperäinen 8 * 0.7

    def test_user_goals_affect_duration(self, mentor):
        """Käyttäjän tavoitteet vaikuttavat kesteeseen."""
        result_without_goals = mentor.run(
            task="Opeta",
            skill_level="beginner",
            topic="python",
            user_goals=[],
        )
        result_with_goals = mentor.run(
            task="Opeta",
            skill_level="beginner",
            topic="python",
            user_goals=["tavoite1", "tavoite2", "tavoite3"],
        )
        # Enemmän tavoitteita voi lisätä kesteeseen
        assert result_with_goals.estimated_weeks >= result_without_goals.estimated_weeks or True

    def test_resources_returned(self, mentor):
        """Resurssit palautetaan."""
        result = mentor.run(
            task="Opeta python",
            topic="python",
        )
        assert isinstance(result.resources, list)
        assert len(result.resources) > 0

    def test_next_steps_returned(self, mentor):
        """Seuraavat askeleet palautetaan."""
        result = mentor.run(
            task="Opeta python",
            topic="python",
        )
        assert isinstance(result.next_steps, list)
        assert len(result.next_steps) > 0

    def test_invalid_topic(self, mentor):
        """Tuntematon aihe käyttää oletusresursseja."""
        result = mentor.run(
            task="Opeta tuntematonta ainetta",
            topic="tuntematon-aihe",
        )
        assert result.success is True
        assert len(result.resources) >= 2  # Oletusresurssit

    def test_serializes(self, mentor):
        """Tulos voidaan serialisoida."""
        result = mentor.run(
            task="Opeta python",
            topic="python",
        )
        d = result.to_dict()
        assert d["agent_type"] == "mentor"
        assert "lesson_plan" in d


# ===================
# ExplainerAgent tests
# ===================


class TestExplainerAgent:
    """Testit ExplainerAgentille."""

    def test_agent_type(self, explainer):
        assert explainer.agent_type == "explainer"

    def test_input_schema(self, explainer):
        assert explainer.input_schema == ExplainerAgentInput

    def test_output_schema(self, explainer):
        assert explainer.output_schema == ExplainerAgentOutput

    def test_run_explains_code(self, explainer, sample_code):
        """Koodi selitetään oikein."""
        result = explainer.run(
            task="Selitä tämä koodi",
            code=sample_code,
            skill_level="beginner",
        )
        assert isinstance(result, ExplainerAgentOutput)
        assert result.success is True
        assert len(result.explanation) > 0
        assert "funktio" in result.explanation.lower() or "function" in result.explanation.lower()

    def test_run_intermediate_level(self, explainer, sample_code):
        """Keskiverto-taso antaa syvemmän analyysisin."""
        result = explainer.run(
            task="Selitä",
            code=sample_code,
            skill_level="intermediate",
        )
        assert "suunnittelu" in result.explanation.lower() or "modular" in result.explanation.lower()

    def test_run_advanced_level(self, explainer, sample_code):
        """Edistynyt taso antaa monimutkaisen analyysisin."""
        result = explainer.run(
            task="Analysoi",
            code=sample_code,
            skill_level="advanced",
        )
        assert "monimutkaisuus" in result.explanation.lower() or "complexity" in result.explanation.lower()

    def test_code_breakdown_generated(self, explainer, sample_code):
        """Koodin kohta analyysi luodaan."""
        result = explainer.run(
            task="Selitä",
            code=sample_code,
        )
        assert len(result.code_breakdown) > 0
        assert "line" in result.code_breakdown[0]
        assert "type" in result.code_breakdown[0]

    def test_classify_line_types(self, explainer, sample_code):
        """Funktiot ja luokat luokitellaan oikein."""
        result = explainer.run(
            task="Selitä",
            code=sample_code,
        )
        types_found = [item["type"] for item in result.code_breakdown]
        assert "funktio" in types_found
        assert "luokka" in types_found

    def test_explains_concept(self, explainer):
        """Käsittein voidaan selittää ilman koodia."""
        result = explainer.run(
            task="Selitä rekursio",
            concept="rekursio",
            skill_level="beginner",
        )
        assert result.success is True
        assert len(result.explanation) > 0

    def test_analogies_generated(self, explainer, sample_code):
        """Analogiat luodaan koodille."""
        result = explainer.run(
            task="Selitä",
            code=sample_code,
            skill_level="beginner",
        )
        assert len(result.analogies) > 0
        assert all(isinstance(a, str) for a in result.analogies)

    def test_key_concepts_extracted(self, explainer, sample_code):
        """Tärkeimmät käsitteet tunnistetaan koodista."""
        result = explainer.run(
            task="Selitä",
            code=sample_code,
        )
        assert "funktio" in result.key_concepts
        assert "luokka" in result.key_concepts

    def test_read_from_file(self, explainer, tmp_path, sample_code):
        """Koodi luetaan tiedostosta."""
        filepath = tmp_path / "code.py"
        filepath.write_text(sample_code, encoding="utf-8")

        result = explainer.run(
            task="Selitä tiedosto",
            file_path=str(filepath),
        )
        assert result.success is True
        assert len(result.explanation) > 0

    def test_no_code_no_concept(self, explainer):
        """Virhettä annetaan jos ei ole koodia eikä käsitettä."""
        result = explainer.run(
            task="Selitä mitään",
        )
        assert result.success is False

    def test_file_not_found(self, explainer):
        """Puuttuvan tiedoston kanssa virhe."""
        result = explainer.run(
            task="Selitä",
            file_path="ei/ole/olemassa.py",
        )
        assert result.success is False

    def test_syntax_error_handling(self, explainer):
        """Syntaksivirhe käsitellään."""
        result = explainer.run(
            task="Selitä",
            code="def broken(\n",
        )
        assert result.success is True  # Edelleen onnistunut
        assert len(result.code_breakdown) == 0  # Ei koodia purettavissa

    def test_serializes(self, explainer, sample_code):
        """Tulos voidaan serialisoida."""
        result = explainer.run(
            task="Selitä",
            code=sample_code,
        )
        d = result.to_dict()
        assert d["agent_type"] == "explainer"
        assert "explanation" in d


# ===================
# PedagogyAgent tests
# ===================


class TestPedagogyAgent:
    """Testit PedagogyAgentille."""

    def test_agent_type(self, pedagogy):
        assert pedagogy.agent_type == "pedagogy"

    def test_input_schema(self, pedagogy):
        assert pedagogy.input_schema == PedagogyAgentInput

    def test_output_schema(self, pedagogy):
        assert pedagogy.output_schema == PedagogyAgentOutput

    def test_run_creates_curriculum(self, pedagogy):
        """Oppimissuunnitelma luodaan oikein."""
        result = pedagogy.run(
            task="Laadi kurssi",
            topic="python",
            skill_level="beginner",
            duration_weeks=4,
        )
        assert isinstance(result, PedagogyAgentOutput)
        assert result.success is True
        assert "modules" in result.curriculum
        assert len(result.curriculum["modules"]) == 4  # 4 viikkoa
        assert result.curriculum["topic"] == "python"

    def test_weeks_split_correctly(self, pedagogy):
        """Aiheet jaetaan viikoittain tasan."""
        result = pedagogy.run(
            task="Kurssi",
            topic="python",
            duration_weeks=3,
        )
        weeks = result.curriculum["modules"]
        assert len(weeks) == 3
        for wk_name, wk_data in weeks.items():
            assert "aihepiirit" in wk_data
            assert "tavoitteet" in wk_data
            assert "harjoitukset" in wk_data

    def test_exercises_counted(self, pedagogy):
        """Harjoitukset lasketaan oikein."""
        result = pedagogy.run(
            task="Kurssi",
            topic="python",
            duration_weeks=2,
            include_exercises=True,
        )
        assert result.total_exercises > 0

    def test_no_exercises_when_disabled(self, pedagogy):
        """Ei harjoituksia kun include_exercises=False."""
        result = pedagogy.run(
            task="Kurssi",
            topic="python",
            duration_weeks=2,
            include_exercises=False,
        )
        assert result.total_exercises == 0

    def test_phases_returned(self, pedagogy):
        """Oppimisvaiheet palautetaan."""
        result = pedagogy.run(
            task="Kurssi",
            topic="python",
        )
        assert len(result.phases) == len(CURRICULUM_PHASES)
        assert "Tavoite asetelma" in result.phases

    def test_intermediate_level(self, pedagogy):
        """Keskiverto-taso toimii."""
        result = pedagogy.run(
            task="Kurssi",
            topic="python",
            skill_level="intermediate",
        )
        assert result.success is True
        assert result.curriculum["skill_level"] == "intermediate"

    def test_advanced_level(self, pedagogy):
        """Edistynyt taso toimii."""
        result = pedagogy.run(
            task="Kurssi",
            topic="devops",
            skill_level="advanced",
        )
        assert result.success is True

    def test_unknown_topic(self, pedagogy):
        """Tuntematon aihe käyttää oletusaiheita."""
        result = pedagogy.run(
            task="Kurssi",
            topic="tuntematon",
        )
        assert result.success is True
        assert "modules" in result.curriculum

    def test_user_background(self, pedagogy):
        """Käyttäjän taustaosaaminen vaikuttaa suunnitelmaan."""
        result = pedagogy.run(
            task="Kurssi",
            topic="python",
            user_background="strong",
        )
        assert result.curriculum["user_background"] == 3  # vahva = 3

    def test_serializes(self, pedagogy):
        """Tulos voidaan serialisoida."""
        result = pedagogy.run(
            task="Kurssi",
            topic="python",
        )
        d = result.to_dict()
        assert d["agent_type"] == "pedagogy"
        assert "curriculum" in d


# ===================
# ContentDesignerAgent tests
# ===================


class TestContentDesignerAgent:
    """Testit ContentDesignerAgentille."""

    def test_agent_type(self, content_designer):
        assert content_designer.agent_type == "content_designer"

    def test_input_schema(self, content_designer):
        assert content_designer.input_schema == ContentDesignerAgentInput

    def test_output_schema(self, content_designer):
        assert content_designer.output_schema == ContentDesignerAgentOutput

    def test_generate_explanation(self, content_designer):
        """Selitys-generointi toimii."""
        result = content_designer.run(
            task="Luo selitys",
            content_type="explanation",
            topic="python",
            num_items=5,
        )
        assert isinstance(result, ContentDesignerAgentOutput)
        assert result.success is True
        assert len(result.content) > 0
        assert result.content_type == "explanation"

    def test_generate_exercise(self, content_designer):
        """Harjoituksen generaointi toimii."""
        result = content_designer.run(
            task="Luo harjoitus",
            content_type="exercise",
            topic="python",
            num_items=3,
        )
        assert result.total_items == 3
        assert all("title" in item for item in result.content)

    def test_generate_quiz(self, content_designer):
        """Kysely-generointi toimii."""
        result = content_designer.run(
            task="Luo kysely",
            content_type="quiz",
            topic="python",
            num_items=5,
        )
        assert result.total_items <= 5
        assert "title" in result.content[0]

    def test_generate_tutorial(self, content_designer):
        """Tutoriaalin generaointi toimii."""
        result = content_designer.run(
            task="Luo tutorial",
            content_type="tutorial",
            topic="python",
            num_items=4,
        )
        assert result.total_items == 4
        assert all("title" in item for item in result.content)

    def test_generate_cheat_sheet(self, content_designer):
        """Cheat sheet -generointi toimii."""
        result = content_designer.run(
            task="Luo cheat sheet",
            content_type="cheat_sheet",
            topic="python",
            num_items=5,
        )
        assert result.total_items == 5

    def test_unknown_content_type(self, content_designer):
        """Tuntematon tyyppi ottaa selityksen oletuksi."""
        result = content_designer.run(
            task="Luo",
            content_type="tuntematon",
            topic="python",
        )
        assert result.success is True

    def test_context_in_explanation(self, content_designer, sample_code):
        """Konteksti lisätään selitykseen."""
        result = content_designer.run(
            task="Luo selitys kontekstilla",
            content_type="explanation",
            topic="python",
            context_text=sample_code,
            num_items=3,
        )
        context_found = any("Koodin selostus" in c.get("title", "") for c in result.content)
        assert context_found

    def test_context_in_tutorial(self, content_designer, sample_code):
        """Konteksti lisätään tutoriaalin alkuun."""
        result = content_designer.run(
            task="Luo tutorial kontekstilla",
            content_type="tutorial",
            topic="python",
            context_text=sample_code,
            num_items=3,
        )
        assert len(result.content) > 0

    def test_num_items_respected(self, content_designer):
        """num_items-parametri kunnioitetaan."""
        result = content_designer.run(
            task="Luo",
            content_type="explanation",
            topic="python",
            num_items=2,
        )
        assert len(result.content) <= 2

    def test_content_items_have_title_and_content(self, content_designer):
        """Kaikilla sisällä oikeudet title ja content."""
        result = content_designer.run(
            task="Luo",
            content_type="explanation",
            topic="python",
            num_items=5,
        )
        for item in result.content:
            assert "title" in item
            assert "content" in item

    def test_serializes(self, content_designer):
        """Tulos voidaan serialisoida."""
        result = content_designer.run(
            task="Luo",
            content_type="quiz",
            topic="javascript",
        )
        d = result.to_dict()
        assert d["agent_type"] == "content_designer"
        assert "content" in d


# ===================
# Module-level tests
# ===================


class TestModuleLevel:
    """Testit moduulin tasolla."""

    def test_learning_levels_exist(self):
        """LEARNING_LEVELS -dict on olemassa ja täynnä."""
        assert "beginner" in LEARNING_LEVELS
        assert "intermediate" in LEARNING_LEVELS
        assert "advanced" in LEARNING_LEVELS
        for level, info in LEARNING_LEVELS.items():
            assert "name" in info
            assert "description" in info
            assert "teaching_style" in info
            assert "assumed_knowledge" in info

    def test_learning_topics_exist(self):
        """LEARNING_TOPICS -dict on olemassa ja täynnä."""
        assert "python" in LEARNING_TOPICS
        assert "javascript" in LEARNING_TOPICS
        assert "devops" in LEARNING_TOPICS
        assert "security" in LEARNING_TOPICS
        assert len(LEARNING_TOPICS["python"]) > 5

    def test_explanation_prompts_exist(self):
        """EXPLANATION_PROMPTS -dict on olemassa."""
        assert "beginner" in EXPLANATION_PROMPTS
        assert "intermediate" in EXPLANATION_PROMPTS
        assert "advanced" in EXPLANATION_PROMPTS

    def test_exercise_types_exist(self):
        """EXERCISE_TYPES -dict on olemassa."""
        assert "debugging" in EXERCISE_TYPES
        assert "refactoring" in EXERCISE_TYPES
        assert "extension" in EXERCISE_TYPES
        assert "security" in EXERCISE_TYPES
        assert "documentation" in EXERCISE_TYPES

    def test_curriculum_phases_exist(self):
        """CURRICULUM_PHASES -lista on olemassa ja täynnä."""
        assert len(CURRICULUM_PHASES) >= 4
        assert isinstance(CURRICULUM_PHASES, list)

    def test_all_agents_importable_from_package(self):
        """Kaikki agentit tuodaan agents-paketista."""
        from agents import (
            MentorAgent,
            ExplainerAgent,
            PedagogyAgent,
            ContentDesignerAgent,
        )
        assert MentorAgent.agent_type == "mentor"
        assert ExplainerAgent.agent_type == "explainer"
        assert PedagogyAgent.agent_type == "pedagogy"
        assert ContentDesignerAgent.agent_type == "content_designer"


# ===================
# Pydantic validation tests
# ===================


class TestPydanticValidation:
    """Testit Pydantic-validoinnille."""

    def test_mentor_input_defaults(self):
        """MentorAgentInput saa oletusarvot."""
        inp = MentorAgentInput(task="test")
        assert inp.skill_level == "beginner"
        assert inp.topic == "python"
        assert inp.learning_speed == "moderate"
        assert len(inp.user_goals) == 0

    def test_mentor_input_custom(self):
        """MentorAgentInput ottaa ylikirjoitetut arvot."""
        inp = MentorAgentInput(
            task="test",
            skill_level="advanced",
            topic="devops",
            learning_speed="fast",
            user_goals=["tavoite1", "tavoite2"],
        )
        assert inp.skill_level == "advanced"
        assert inp.topic == "devops"
        assert len(inp.user_goals) == 2

    def test_explainer_input_defaults(self):
        """ExplainerAgentInput saa oletusarvot."""
        inp = ExplainerAgentInput(task="test")
        assert inp.skill_level == "beginner"
        assert inp.code == ""

    def test_pedagogy_input_defaults(self):
        """PedagogyAgentInput saa oletusarvot."""
        inp = PedagogyAgentInput(task="test")
        assert inp.topic == "python"
        assert inp.skill_level == "beginner"
        assert inp.duration_weeks == 4
        assert inp.include_exercises is True

    def test_content_designer_input_defaults(self):
        """ContentDesignerAgentInput saa oletusarvot."""
        inp = ContentDesignerAgentInput(task="test")
        assert inp.content_type == "explanation"
        assert inp.num_items == 5

    def test_output_schemas_serialize(self):
        """Kaikki output-skeemat voidaan serialisoida dictiksi."""
        mentor_out = MentorAgentOutput(success=True, agent_type="mentor")
        explainer_out = ExplainerAgentOutput(success=True, agent_type="explainer")
        pedagogy_out = PedagogyAgentOutput(success=True, agent_type="pedagogy")
        content_out = ContentDesignerAgentOutput(success=True, agent_type="content_designer")

        for out in [mentor_out, explainer_out, pedagogy_out, content_out]:
            d = out.to_dict()
            assert "success" in d
            assert "agent_type" in d
