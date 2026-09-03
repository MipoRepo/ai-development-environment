"""
Testit Agent Engineering -agenteille (M16): AgentDesignAgent, PromptOptimizerAgent, AgentFactoryAgent.
"""

import pytest

from agents.agent_engineering_agent import (
    AgentDesignAgent,
    AgentDesignInput,
    AgentDesignOutput,
    PromptOptimizerAgent,
    PromptOptimizerInput,
    PromptOptimizerOutput,
    AgentFactoryAgent,
    AgentFactoryInput,
    AgentFactoryOutput,
    AGENT_DESIGN_ACTIONS,
    PROMPT_OPTIMIZE_ACTIONS,
    AGENT_FACTORY_ACTIONS,
    KNOWN_AGENT_TYPES,
    SCHEMA_FIELDS,
    PROMPT_OPTIMIZATION_TIPS,
)


# ============================================================
# AgentDesignAgent tests
# ============================================================


@pytest.fixture
def design_agent():
    """Palauttaa AgentDesignAgent-instanssin."""
    return AgentDesignAgent()


class TestAgentDesignAgent:
    """Testit AgentDesignAgentille."""

    def test_agent_type(self, design_agent):
        """Testaa agentin tyyppi."""
        assert design_agent.agent_type == "agent_design"

    def test_input_schema(self, design_agent):
        """Testaa syöteskeema."""
        assert design_agent.input_schema == AgentDesignInput

    def test_output_schema(self, design_agent):
        """Testaa tulosteskeema."""
        assert design_agent.output_schema == AgentDesignOutput

    def test_design_agent_basic(self, design_agent):
        """Testaa perusagentin suunnittelu."""
        result = design_agent.run(
            "Suunnittele data-analyysi agentti",
            action="design",
            agent_name="AnalyzerAgent",
            agent_description="Data-analyysi agentti",
            agent_type="analyzer",
            capabilities=["analyze", "report"],
        )
        assert result.success is True
        assert result.agent_spec["name"] == "AnalyzerAgent"
        assert result.agent_spec["agent_type"] == "analyzer"
        assert "analyze" in result.agent_spec["capabilities"]
        assert "success" in result.agent_spec["output_schema"]

    def test_design_agent_with_input_fields(self, design_agent):
        """Testaa agentin suunnittelu annetuilla syötefieldilla."""
        result = design_agent.run(
            "Suunnittele agentti",
            action="design",
            agent_name="DataAgent",
            input_fields={"task": "Tehtävä", "query": "Hakukysely"},
        )
        assert result.agent_spec["name"] == "DataAgent"

    def test_design_agent_with_output_fields(self, design_agent):
        """Testaa agentin suunnittelu annetuilla tulostefieldilla."""
        result = design_agent.run(
            "Suunnittele agentti",
            action="design",
            agent_name="DataAgent",
            output_fields={"success": "Onnistuminen", "result": "Tulos", "message": "Viesti", "agent_type": "Tyyppi"},
        )
        assert result.success is True
        assert "result" in result.agent_spec["output_schema"]

    def test_design_agent_no_name_validation(self, design_agent):
        """Testaa validointi ilman nimeä."""
        result = design_agent.run(
            "Suunnittele",
            action="design",
            agent_name="",
        )
        assert result.success is False
        assert "nimi" in result.validation_issues[0].lower()

    def test_design_agent_bad_name_format(self, design_agent):
        """Testaa virheellisen nimen validointi."""
        result = design_agent.run(
            "Suunnittele",
            action="design",
            agent_name="bad_name",
        )
        assert result.success is False
        assert any("PascalCase" in issue for issue in result.validation_issues)

    def test_design_agent_name_with_spaces(self, design_agent):
        """Testaa nimessä olevan välilyöntien validointi."""
        result = design_agent.run(
            "Suunnittele",
            action="design",
            agent_name="Bad Agent",
        )
        assert result.success is False
        assert any("välily" in issue.lower() for issue in result.validation_issues)

    def test_design_agent_suggest_input_schema(self, design_agent):
        """Testaa syötetietorakenteen ehdotus."""
        result = design_agent.run(
            "Suunnittele",
            action="design",
            agent_name="SearchAgent",
            capabilities=["search"],
        )
        assert "query" in result.input_schema_suggestion

    def test_design_agent_suggest_output_schema(self, design_agent):
        """Testaa tulostetietorakenteen ehdotus."""
        result = design_agent.run(
            "Suunnittele",
            action="design",
            agent_name="SearchAgent",
            capabilities=["search"],
        )
        assert "results" in result.output_schema_suggestion

    def test_design_agent_recommend_types(self, design_agent):
        """Testaa agenttityyppien suosittelu."""
        result = design_agent.run(
            "Suunnittele",
            action="recommend",
            capabilities=["analyze", "search", "summarize"],
        )
        assert len(result.recommended_agent_types) > 0

    def test_design_agent_recommend_no_match(self, design_agent):
        """Testaa suosittelut tyhjällä kyvykkyyksillä."""
        result = design_agent.run(
            "Suosita",
            action="recommend",
            capabilities=[],
        )
        assert len(result.recommended_agent_types) == 0

    def test_design_agent_validate_action(self, design_agent):
        """Testaa validointitoiminto."""
        result = design_agent.run(
            "Varmista",
            action="validate",
            agent_name="TestAgent",
        )
        assert result.success is False  # TestAgent ei ole PascalCase + Agent

    def test_design_agent_validate_good_name(self, design_agent):
        """Testaa validointi hyvällä nimellä."""
        result = design_agent.run(
            "Varmista",
            action="validate",
            agent_name="TestAgent",
            agent_description="Testausta varten",
            input_fields={"task": "Tehtävä"},
            output_fields={"success": "Onnistuminen", "message": "Viesti", "agent_type": "Tyyppi"},
        )
        assert result.success is True

    def test_design_agent_analyze_code_missing(self, design_agent):
        """Testaa koodin analyysi puuttuvilla kentillä."""
        result = design_agent.run(
            "Analysoi",
            action="analyze",
            existing_agent_code="class Test:\n    pass",
        )
        assert result.success is True
        assert "agent_type" in result.validation_issues[0]

    def test_design_agent_analyze_code_good(self, design_agent):
        """Testaa koodin analyysi hyvällä koodilla."""
        code = """
class TestAgent(BaseAgent):
    agent_type = "test"
    input_schema = Input
    output_schema = Output
    def _run(self, input_data):
        pass
"""
        result = design_agent.run("Analysoi", action="analyze", existing_agent_code=code)
        assert result.success is True
        assert len(result.validation_issues) == 0

    def test_design_agent_unknown_action(self, design_agent):
        """Testaa tuntematon toiminto."""
        result = design_agent.run("Tuntematon", action="unknown")
        assert result.success is False
        assert "tuntematon" in result.message.lower()

    def test_design_agent_default_action(self, design_agent):
        """Testaa oletustoiminto."""
        result = design_agent.run("Suunnittele", agent_name="TestAgent", agent_description="Testi")
        assert result.success is True
        assert result.agent_spec["name"] == "TestAgent"

    def test_agent_design_actions_available(self):
        """Testaa että kaikki suunnittelutoiminnot ovat määritelty."""
        assert "design" in AGENT_DESIGN_ACTIONS
        assert "analyze" in AGENT_DESIGN_ACTIONS
        assert "validate" in AGENT_DESIGN_ACTIONS
        assert "recommend" in AGENT_DESIGN_ACTIONS

    def test_known_agent_types_available(self):
        """Testaa että tunnetut agenttitapaukset ovat määritelty."""
        assert "director" in KNOWN_AGENT_TYPES
        assert "researcher" in KNOWN_AGENT_TYPES
        assert "developer" in KNOWN_AGENT_TYPES
        assert "release_manager" in KNOWN_AGENT_TYPES

    def test_schema_fields_available(self):
        """Testaa että skeemakentät ovat määritelty."""
        assert "task" in SCHEMA_FIELDS["input"]
        assert "success" in SCHEMA_FIELDS["output"]


# ============================================================
# PromptOptimizerAgent tests
# ============================================================


@pytest.fixture
def optimizer_agent():
    """Palauttaa PromptOptimizerAgent-instanssin."""
    return PromptOptimizerAgent()


class TestPromptOptimizerAgent:
    """Testit PromptOptimizerAgentille."""

    def test_agent_type(self, optimizer_agent):
        """Testaa agentin tyyppi."""
        assert optimizer_agent.agent_type == "prompt_optimizer"

    def test_input_schema(self, optimizer_agent):
        """Testaa syöteskeema."""
        assert optimizer_agent.input_schema == PromptOptimizerInput

    def test_output_schema(self, optimizer_agent):
        """Testaa tulosteskeema."""
        assert optimizer_agent.output_schema == PromptOptimizerOutput

    def test_optimize_basic(self, optimizer_agent):
        """Testaa perusoptimointi."""
        result = optimizer_agent.run(
            "Optimoi",
            action="optimize",
            prompt="Kerro mina kaikista ohjelmointikielista.",
            target_token_limit=4096,
        )
        assert result.success is True
        assert result.optimized_prompt != ""
        assert result.original_token_estimate > 0
        assert len(result.optimized_prompt) <= len("Kerro mina kaikista ohjelmointikielista.") or \
               "##" in result.optimized_prompt  # Optimized or added structure

    def test_optimize_empty_prompt(self, optimizer_agent):
        """Testaa tyhjän promptin optimointi."""
        result = optimizer_agent.run("Optimoi", action="optimize", prompt="")
        assert result.success is False
        assert result.optimization_score == 0

    def test_estimate_tokens(self, optimizer_agent):
        """Testaa tokenien arviointi."""
        result = optimizer_agent.run(
            "Arvioi", action="estimate", prompt="Tämä on testaus prompt."
        )
        assert result.success is True
        assert result.original_token_estimate > 0
        assert result.original_token_estimate == len("Tämä on testaus prompt.") // 4

    def test_analyze_prompt(self, optimizer_agent):
        """Testaa promptin rakenteen analyysi."""
        result = optimizer_agent.run(
            "Analysoi",
            action="analyze",
            prompt="Tämä on pidempi prompt, joka analysoidaan struktuurin tarkisseluun.",
        )
        assert result.success is True
        assert len(result.suggestions) > 0
        assert "chars" in result.result["structure"]

    def test_optimize_long_prompt_suggestions(self, optimizer_agent):
        """Testaa että pitkälle promptille annetaan ehdotuksia lyhentämiseen."""
        long_prompt = " ".join(["sana"] * 250)
        result = optimizer_agent.run("Optimoi", action="analyze", prompt=long_prompt)
        assert result.success is True
        assert any("Lyhennä" in s for s in result.suggestions)

    def test_optimize_adds_examples_suggestion(self, optimizer_agent):
        """Testaa että esimerkkiehdotus annetaan jos esimerkkejä ei ole."""
        result = optimizer_agent.run(
            "Analysoi", action="analyze", prompt="Kerro mina kaikista."
        )
        assert result.success is True
        assert any("esimerkk" in s.lower() for s in result.suggestions)

    def test_suggest_action(self, optimizer_agent):
        """Testaa parannusehdotusten antaminen."""
        result = optimizer_agent.run(
            "Ehdota", action="suggest", prompt="Kerro mina kaikista."
        )
        assert result.success is True
        assert len(result.suggestions) > 0

    def test_optimize_creates_structure(self, optimizer_agent):
        """Testaa että optimointi lisää rakenteen jos puuttuu."""
        result = optimizer_agent.run(
            "Optimoi", action="optimize", prompt="Kerro mina kaikista ohjelmointikielista."
        )
        assert result.success is True
        assert "##" in result.optimized_prompt

    def test_tokens_saved(self, optimizer_agent):
        """Testaa että tokenien säästö lasketaan."""
        result = optimizer_agent.run(
            "Optimoi", action="optimize", prompt="Tämä on testaus."
        )
        assert result.success is True
        # tokens_saved voi olla negatiivinen jos optimointi lisäsi rakennetta
        assert isinstance(result.tokens_saved, int)

    def test_optimization_score(self, optimizer_agent):
        """Testaa optimointipistemäärän laskeminen."""
        result = optimizer_agent.run(
            "Optimoi", action="optimize", prompt="Tämä on testaus."
        )
        assert result.success is True
        assert 0 <= result.optimization_score <= 100

    def test_unknown_action(self, optimizer_agent):
        """Testaa tuntematon toiminto."""
        result = optimizer_agent.run("Tuntematon", action="unknown")
        assert result.success is False

    def test_prompt_optimize_actions_available(self):
        """Testaa että kaikki prompt-optimointitoiminnot ovat määritelty."""
        assert "optimize" in PROMPT_OPTIMIZE_ACTIONS
        assert "analyze" in PROMPT_OPTIMIZE_ACTIONS
        assert "estimate" in PROMPT_OPTIMIZE_ACTIONS
        assert "suggest" in PROMPT_OPTIMIZE_ACTIONS

    def test_prompt_optimization_tips_available(self):
        """Testaa että optimointivihjeet ovat määritelty."""
        assert len(PROMPT_OPTIMIZATION_TIPS) > 0
        assert isinstance(PROMPT_OPTIMIZATION_TIPS[0], str)


# ============================================================
# AgentFactoryAgent tests
# ============================================================


@pytest.fixture
def factory_agent():
    """Palauttaa AgentFactoryAgent-instanssin."""
    return AgentFactoryAgent()


class TestAgentFactoryAgent:
    """Testit AgentFactoryAgentille."""

    def test_agent_type(self, factory_agent):
        """Testaa agentin tyyppi."""
        assert factory_agent.agent_type == "agent_factory"

    def test_input_schema(self, factory_agent):
        """Testaa syöteskeema."""
        assert factory_agent.input_schema == AgentFactoryInput

    def test_output_schema(self, factory_agent):
        """Testaa tulosteskeema."""
        assert factory_agent.output_schema == AgentFactoryOutput

    def test_factory_create_agent(self, factory_agent):
        """Testaa agentin luominen."""
        result = factory_agent.run(
            "Luo uusi agentti",
            action="create",
            agent_type="researcher",
            agent_name="ResearcherAgent",
        )
        assert result.success is True
        assert result.agent_instance["agent_type"] == "researcher"
        assert result.agent_instance["name"] == "ResearcherAgent"

    def test_factory_create_with_config(self, factory_agent):
        """Testaa agentin luominen konfiguraatiolla."""
        config = {"custom_param": "value", "another": 123}
        result = factory_agent.run(
            "Luo",
            action="create",
            agent_type="developer",
            agent_name="DevAgent",
            config=config,
        )
        assert result.success is True
        assert result.agent_instance["config"]["custom_param"] == "value"

    def test_factory_create_with_module_path(self, factory_agent):
        """Testaa agentin luominen moduulipolulla."""
        result = factory_agent.run(
            "Luo",
            action="create",
            agent_type="custom",
            agent_name="CustomAgent",
            module_path="agents.custom_agent",
        )
        assert result.success is True
        assert result.agent_instance["module"] == "agents.custom_agent"

    def test_factory_list_registered(self, factory_agent):
        """Testaa rekisteröitya agenttien luettelointi."""
        result = factory_agent.run("Luelista rekisteröidyt agentit", action="list")
        assert result.success is True
        assert "researcher" in result.registered_agents
        assert "developer" in result.registered_agents
        assert "director" in result.registered_agents

    def test_factory_instantiate_known_type(self, factory_agent):
        """Testaa tunnetun tyypin instanssikin."""
        result = factory_agent.run("Instantiate", action="instantiate", agent_type="researcher")
        assert result.success is True
        assert result.agent_instance["agent_type"] == "researcher"
        assert "agents.researcher_agent" in result.agent_instance["module"]

    def test_factory_instantiate_unknown_type(self, factory_agent):
        """Testaa tuntemattoman tyypin instanssikin."""
        result = factory_agent.run("Instantiate", action="instantiate", agent_type="nonexistent_type")
        assert result.success is False
        assert "ei löydy" in result.message.lower()

    def test_factory_register_new_agent(self, factory_agent):
        """Testaa uuden agentin rekisteröinti."""
        result = factory_agent.run(
            "Rekisteroi",
            action="register",
            agent_type="new_custom",
            module_path="agents.new_custom",
        )
        assert result.success is True
        assert result.registered_agents["new_custom"] == "agents.new_custom"

    def test_factory_register_no_type(self, factory_agent):
        """Testaa rekisteröinti ilman agenttityyppiä."""
        result = factory_agent.run("Rekisteroi", action="register")
        assert result.success is False
        assert "agent_type" in result.message.lower() or "agent_type" in result.result

    def test_factory_register_no_module(self, factory_agent):
        """Testaa rekisteröinti ilman moduulipolkua."""
        result = factory_agent.run("Rekisteroi", action="register", agent_type="test")
        assert result.success is False

    def test_factory_default_action_is_create(self, factory_agent):
        """Testaa oletustoiminto on 'create'."""
        result = factory_agent.run("Luo agentti", agent_type="qa", agent_name="QAAgent")
        assert result.success is True

    def test_factory_unknown_action(self, factory_agent):
        """Testaa tuntematon toiminto."""
        result = factory_agent.run("Tuntematon", action="unknown")
        assert result.success is False

    def test_factory_agent_registry_has_entries(self, factory_agent):
        """Testaa että rekisteri sisältää merkintöjä."""
        assert len(factory_agent.AGENT_REGISTRY) > 0
        assert "director" in factory_agent.AGENT_REGISTRY
        assert "release_manager" in factory_agent.AGENT_REGISTRY
        assert "knowledge" in factory_agent.AGENT_REGISTRY

    def test_factory_register_updates_custom_registry(self, factory_agent):
        """Testaa että rekisteröinti päivittää rekisterin."""
        custom_registry = {"existing": "agents.existing"}
        result = factory_agent.run("Lista", action="list", registered_agents=custom_registry)
        assert result.success is True
        assert "existing" in result.registered_agents

    def test_agent_factory_actions_available(self):
        """Testaa että kaikki agent Factory -toiminnot ovat määritelty."""
        assert "create" in AGENT_FACTORY_ACTIONS
        assert "register" in AGENT_FACTORY_ACTIONS
        assert "list" in AGENT_FACTORY_ACTIONS
        assert "instantiate" in AGENT_FACTORY_ACTIONS


# ============================================================
# Module-level tests
# ============================================================


class TestAgentEngineeringModuleLevel:
    """Moduulin ja paketin tasolla olevat testit."""

    def test_import_from_agents_package(self):
        """Testaa että kaikki voidaan tuoda agents-paketista."""
        from agents import AgentDesignAgent, PromptOptimizerAgent, AgentFactoryAgent
        assert AgentDesignAgent is not None
        assert PromptOptimizerAgent is not None
        assert AgentFactoryAgent is not None

    def test_import_input_output_models(self):
        """Testaa että kaikki Input/Output-mallit on tuotavissa."""
        from agents import (
            AgentDesignInput,
            AgentDesignOutput,
            PromptOptimizerInput,
            PromptOptimizerOutput,
            AgentFactoryInput,
            AgentFactoryOutput,
        )
        assert AgentDesignInput is not None
        assert AgentDesignOutput is not None
        assert PromptOptimizerInput is not None
        assert PromptOptimizerOutput is not None
        assert AgentFactoryInput is not None
        assert AgentFactoryOutput is not None

    def test_import_constants(self):
        """Testaa että kaikki vakiot on tuotavissa."""
        from agents import (
            AGENT_DESIGN_ACTIONS,
            PROMPT_OPTIMIZE_ACTIONS,
            AGENT_FACTORY_ACTIONS,
            KNOWN_AGENT_TYPES,
            SCHEMA_FIELDS,
            PROMPT_OPTIMIZATION_TIPS,
        )
        assert AGENT_DESIGN_ACTIONS is not None
        assert PROMPT_OPTIMIZE_ACTIONS is not None
        assert AGENT_FACTORY_ACTIONS is not None
        assert KNOWN_AGENT_TYPES is not None
        assert SCHEMA_FIELDS is not None
        assert PROMPT_OPTIMIZATION_TIPS is not None

    def test_all_agents_subclass_baseagent(self):
        """Testaa että kaikki agentit ovat BaseAgent-alaisluokkia."""
        from agents.base import BaseAgent

        assert issubclass(AgentDesignAgent, BaseAgent)
        assert issubclass(PromptOptimizerAgent, BaseAgent)
        assert issubclass(AgentFactoryAgent, BaseAgent)

    def test_known_agent_types_completeness(self):
        """Testaa että tunnetut agenttitapaukset sisältävät wichtige tyypit."""
        for expected_type in ["director", "researcher", "developer", "security_review", "release_manager"]:
            assert expected_type in KNOWN_AGENT_TYPES

    def test_schema_fields_structure(self):
        """Testaa että skeemakentät ovat oikean rakenteelliset."""
        assert isinstance(SCHEMA_FIELDS, dict)
        assert "input" in SCHEMA_FIELDS
        assert "output" in SCHEMA_FIELDS
        assert isinstance(SCHEMA_FIELDS["input"], list)
        assert isinstance(SCHEMA_FIELDS["output"], list)
