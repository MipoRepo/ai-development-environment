"""
Testit AI Gateway -agenteille (M17): AIGatewayAgent, LLMRouterAgent, TokenTrackerAgent.
"""

from datetime import datetime

import pytest

from agents.ai_gateway_agent import (
    AIGatewayAgent,
    AIGatewayInput,
    AIGatewayOutput,
    LLMRouterAgent,
    LLMRouterInput,
    LLMRouterOutput,
    TokenTrackerAgent,
    TokenTrackerInput,
    TokenTrackerOutput,
    GATEWAY_ACTIONS,
    ROUTING_CRITERIA,
    TOKEN_TRACKER_ACTIONS,
    MODEL_REGISTRY,
)


# ============================================================
# AIGatewayAgent tests
# ============================================================


@pytest.fixture
def gateway_agent():
    """Palauttaa AIGatewayAgent-instanssin."""
    return AIGatewayAgent(api_key="sk-or-v1-test")


class TestAIGatewayAgent:
    """Testit AIGatewayAgentille."""

    def test_agent_type(self, gateway_agent):
        """Testaa agentin tyyppi."""
        assert gateway_agent.agent_type == "ai_gateway"

    def test_input_schema(self, gateway_agent):
        """Testaa syöteskeema."""
        assert gateway_agent.input_schema == AIGatewayInput

    def test_output_schema(self, gateway_agent):
        """Testaa tulosteskeema."""
        assert gateway_agent.output_schema == AIGatewayOutput

    def test_agent_attributes(self, gateway_agent):
        """Testaa että agentilla on oikeat attribuutit."""
        assert gateway_agent._api_key == "sk-or-v1-test"
        assert gateway_agent._default_model == "openai/gpt-4o-mini"

    def test_list_models(self, gateway_agent):
        """Testaa mallien luettelo."""
        result = gateway_agent.run("Llista mallit", action="list_models")
        assert result.success is True
        assert len(result.available_models) > 0
        assert "model_used" not in result or result.response_format == "list"

    def test_chat_basic(self, gateway_agent):
        """Testaa chat-toiminnon perustoteutus."""
        messages = [{"role": "user", "content": "Mistä elämä on?"}]
        result = gateway_agent.run(
            "Kysy mistä elämä on", action="chat", model="openai/gpt-4o-mini", messages=messages
        )
        assert result.success is True
        assert result.model_used == "openai/gpt-4o-mini"
        assert result.response != ""
        assert "input" in result.tokens_used
        assert "output" in result.tokens_used
        assert "total" in result.tokens_used
        assert result.tokens_used["total"] > 0
        assert result.estimated_cost >= 0
        assert result.latency_ms >= 0

    def test_chat_no_messages(self, gateway_agent):
        """Testaa chat ilman viestejä."""
        result = gateway_agent.run("Chatuta", action="chat", model="openai/gpt-4o-mini")
        assert result.success is False
        assert "viestejä" in result.message.lower()

    def test_complete_prompt(self, gateway_agent):
        """Testaa täydennystoiminnon perustoteutus."""
        result = gateway_agent.run(
            "Täydenna tämä", action="complete", model="openai/gpt-4o-mini", prompt="Kerro mina kaikista"
        )
        assert result.success is True
        assert result.model_used == "openai/gpt-4o-mini"
        assert result.response != ""
        assert result.tokens_used["total"] > 0

    def test_complete_no_prompt(self, gateway_agent):
        """Testaa täydennystoiminto ilman kehoitetta."""
        result = gateway_agent.run("Täydenna", action="complete", model="openai/gpt-4o-mini", prompt="")
        assert result.success is False

    def test_embed_action(self, gateway_agent):
        """Testaa upotustoiminnon perustoteutus."""
        result = gateway_agent.run("Upota tämä", action="embed", model="openai/gpt-4o-mini")
        assert result.success is True
        assert result.response_format == "embed"
        assert result.model_used == "openai/gpt-4o-mini"

    def test_unknown_action(self, gateway_agent):
        """Testaa tuntematon toiminto."""
        result = gateway_agent.run("Tuntematon", action="unknown")
        assert result.success is False
        assert "tuntematon" in result.message.lower()

    def test_default_action_is_chat(self, gateway_agent):
        """Testaa että oletustoiminto on chat."""
        messages = [{"role": "user", "content": "Hei"}]
        result = gateway_agent.run("Testaa", messages=messages)
        assert result.success is True

    def test_get_model_info_known(self, gateway_agent):
        """Testaa tunnetun mallin haku."""
        info = gateway_agent._get_model_info("openai/gpt-4o")
        assert info is not None
        assert info["name"] == "GPT-4o"
        assert info["provider"] == "openai"

    def test_get_model_info_unknown(self, gateway_agent):
        """Testaa tuntemattoman mallin haku."""
        info = gateway_agent._get_model_info("tuntematon/malli")
        assert info is None

    def test_estimate_tokens(self, gateway_agent):
        """Testaa tokenien arviointi."""
        tokens = gateway_agent._estimate_tokens("Tämä on koe teksti.")
        assert tokens > 0
        assert tokens == len("Tämä on koe teksti.") // 4

    def test_calculate_cost(self, gateway_agent):
        """Testaa kustannuksen laskeminen."""
        model_info = MODEL_REGISTRY["openai/gpt-4o-mini"]
        cost = gateway_agent._calculate_cost(model_info, 1000, 500)
        assert cost > 0
        expected = (1000 / 1000) * 0.00015 + (500 / 1000) * 0.0006
        assert round(cost, 6) == round(expected, 6)

    def test_simulate_chat_response(self, gateway_agent):
        """Testaa chat-vastauksen simulointi."""
        messages = [{"role": "user", "content": "Testviesti"}]
        response = gateway_agent._simulate_chat_response(messages, "openai/gpt-4o-mini")
        assert "simuloitu" in response.lower()
        assert "GPT-4o Mini" in response

    def test_model_registry_has_entries(self):
        """Testaa että mallirekisteri sisältää merkintöjä."""
        assert len(MODEL_REGISTRY) > 0
        assert "openai/gpt-4o-mini" in MODEL_REGISTRY
        assert "anthropic/claude-3-5-sonnet" in MODEL_REGISTRY

    def test_model_info_fields(self):
        """Testaa että mallitiedot sisältävät kaikki kentät."""
        for model_id, info in MODEL_REGISTRY.items():
            assert "name" in info
            assert "provider" in info
            assert "context_length" in info
            assert "input_price_per_1k" in info
            assert "output_price_per_1k" in info
            assert "capabilities" in info
            assert "latency_tier" in info


# ============================================================
# LLMRouterAgent tests
# ============================================================


@pytest.fixture
def router_agent():
    """Palauttaa LLMRouterAgent-instanssin."""
    return LLMRouterAgent()


class TestLLMRouterAgent:
    """Testit LLMRouterAgentille."""

    def test_agent_type(self, router_agent):
        """Testaa agentin tyyppi."""
        assert router_agent.agent_type == "llm_router"

    def test_input_schema(self, router_agent):
        """Testaa syöteskeema."""
        assert router_agent.input_schema == LLMRouterInput

    def test_output_schema(self, router_agent):
        """Testaa tulosteskeema."""
        assert router_agent.output_schema == LLMRouterOutput

    def test_route_basic(self, router_agent):
        """Testaa perusreititys."""
        result = router_agent.run(
            "Reitä halvin malli", action="route", criteria=["cost"]
        )
        assert result.success is True
        assert result.routed_model != ""
        assert result.routing_reason != ""

    def test_route_with_capabilities(self, router_agent):
        """Testaa reititys vaatimilla ominaisuuksilla."""
        result = router_agent.run(
            "Reitä käyttäen reasoning", action="route",
            criteria=["capability"], required_capabilities=["reasoning", "code"]
        )
        assert result.success is True
        routed_info = MODEL_REGISTRY.get(result.routed_model, {})
        assert "reasoning" in routed_info.get("capabilities", [])

    def test_route_with_context_length(self, router_agent):
        """Testaa reititys vaatimilla kontekstipituuksilla."""
        result = router_agent.run(
            "Reitä pitkään kontekstiin", action="route",
            context_length=100000
        )
        assert result.success is True
        routed_info = MODEL_REGISTRY[result.routed_model]
        assert routed_info["context_length"] >= 100000

    def test_route_no_candidates(self, router_agent):
        """Testaa reititys kun ei ole ehdokkaita."""
        result = router_agent.run(
            "Reitä", action="route",
            criteria=["capability"], required_capabilities=["nonexistent_cap"],
        )
        assert result.success is False

    def test_route_model_scores(self, router_agent):
        """Testaa mallien pisteytystä."""
        result = router_agent.run(
            "Reitä", action="route", criteria=["cost"]
        )
        assert result.success is True
        assert len(result.model_scores) > 0
        for model_id, score in result.model_scores.items():
            assert isinstance(score, (int, float))

    def test_route_candidate_models(self, router_agent):
        """Testaa ehdokasmallit."""
        result = router_agent.run(
            "Reitä", action="route", criteria=["cost"]
        )
        assert result.success is True
        assert len(result.candidate_models) > 0

    def test_evaluate_models(self, router_agent):
        """Testaa mallien arviointi."""
        result = router_agent.run(
            "Arvioi mallit", action="evaluate", criteria=["cost"]
        )
        assert result.success is True
        assert len(result.model_scores) > 0

    def test_compare_models(self, router_agent):
        """Testaa mallien vertailu."""
        result = router_agent.run(
            "Vertaile mallit", action="compare",
            compare_models=["openai/gpt-4o-mini", "openai/gpt-4o"],
        )
        assert result.success is True
        assert len(result.comparison_results) == 2
        assert result.best_model in ("openai/gpt-4o-mini", "openai/gpt-4o")

    def test_compare_default_models(self, router_agent):
        """Testaa oletusmallien vertailu."""
        result = router_agent.run(
            "Vertaile", action="compare"
        )
        assert result.success is True
        assert len(result.comparison_results) >= 3

    def test_unknown_action(self, router_agent):
        """Testaa tuntematon toiminto."""
        result = router_agent.run("Tuntematon", action="unknown")
        assert result.success is False

    def test_score_model_cost(self, router_agent):
        """Testaa mallin pisteytys kustannuskriteerillä."""
        info = MODEL_REGISTRY["openai/gpt-4o-mini"]
        score = router_agent._score_model(info, ["cost"], [])
        assert score >= 0

    def test_score_model_with_required_caps(self, router_agent):
        """Testaa että vaatimattomat ominaisuudet lisäävät pisteitä."""
        info = MODEL_REGISTRY["openai/gpt-4o-mini"]
        score = router_agent._score_model(info, [], ["reasoning"])
        assert score >= 100  # Kustannus lisätään koska "reasoning" puuttuu capabilities

    def test_routing_criteria_available(self):
        """Testaa että kaikki reitityskriteerit ovat määritelty."""
        assert "cost" in ROUTING_CRITERIA
        assert "latency" in ROUTING_CRITERIA
        assert "capability" in ROUTING_CRITERIA
        assert "context" in ROUTING_CRITERIA


# ============================================================
# TokenTrackerAgent tests
# ============================================================


@pytest.fixture
def tracker_agent():
    """Palauttaa TokenTrackerAgent-instanssin."""
    # Nollaa tietueet ennen joka testia
    TokenTrackerAgent._records.clear()
    return TokenTrackerAgent()


class TestTokenTrackerAgent:
    """Testit TokenTrackerAgentille."""

    def test_agent_type(self, tracker_agent):
        """Testaa agentin tyyppi."""
        assert tracker_agent.agent_type == "token_tracker"

    def test_input_schema(self, tracker_agent):
        """Testaa syöteskeema."""
        assert tracker_agent.input_schema == TokenTrackerInput

    def test_output_schema(self, tracker_agent):
        """Testaa tulosteskeema."""
        assert tracker_agent.output_schema == TokenTrackerOutput

    def test_track_tokens(self, tracker_agent):
        """Testaa tokenien seuranta."""
        result = tracker_agent.run(
            "Seuraa tätä", model="openai/gpt-4o-mini", input_tokens=500, output_tokens=250, cost=0.001
        )
        assert result.success is True
        assert result.total_tokens == 750
        assert result.input_tokens == 500
        assert result.output_tokens == 250
        assert result.total_cost == 0.001
        assert len(result.records) == 1

    def test_track_no_model(self, tracker_agent):
        """Testaa tokenien seuranta ilman mallia."""
        result = tracker_agent.run("Seuraa", model="", input_tokens=100, output_tokens=50)
        assert result.success is False
        assert "mallin nimi" in result.message.lower()

    def test_track_multiple_records(self, tracker_agent):
        """Testaa useiden tietueiden seuranta."""
        tracker_agent.run("Seuraa 1", model="openai/gpt-4o", input_tokens=100, output_tokens=50, cost=0.01)
        tracker_agent.run("Seuraa 2", model="openai/gpt-4o-mini", input_tokens=200, output_tokens=100, cost=0.005)

        result = tracker_agent.run("Raportoi", action="report", period="all")
        assert result.success is True
        assert result.total_tokens == 450
        assert result.total_cost == 0.015
        assert len(result.model_breakdown) == 2

    def test_report_daily(self, tracker_agent):
        """Testaa päiväraportti."""
        tracker_agent.run("Track", model="openai/gpt-4o-mini", input_tokens=100, output_tokens=50, cost=0.001)
        result = tracker_agent.run("Raportoi", action="report", period="daily")
        assert result.success is True
        assert result.period == "daily"
        assert result.total_tokens == 150

    def test_report_monthly(self, tracker_agent):
        """Testaa kuukausiraportti."""
        tracker_agent.run("Track", model="openai/gpt-4o-mini", input_tokens=100, output_tokens=50, cost=0.001)
        result = tracker_agent.run("Raportti", action="report", period="monthly")
        assert result.success is True
        assert result.total_tokens == 150

    def test_reset_records(self, tracker_agent):
        """Testaa tietueiden nollaus."""
        tracker_agent.run("Track", model="openai/gpt-4o-mini", input_tokens=100, output_tokens=50, cost=0.001)
        result = tracker_agent.run("Nollaa", action="reset")
        assert result.success is True
        assert "nollattu" in result.message.lower()
        assert result.total_tokens == 0

    def test_reset_clears_records(self, tracker_agent):
        """Testaa että nollaus tyhjentää tietueet."""
        tracker_agent.run("Track", model="openai/gpt-4o-mini", input_tokens=100, output_tokens=50, cost=0.001)
        assert len(TokenTrackerAgent._records) > 0
        tracker_agent.run("Nollaa", action="reset")
        assert len(TokenTrackerAgent._records) == 0

    def test_get_period_records_daily(self, tracker_agent):
        """Testaa päivätietueiden haku."""
        tracker_agent.run("Track", model="openai/gpt-4o-mini", input_tokens=100, output_tokens=50, cost=0.001)
        records = tracker_agent._get_period_records("daily")
        assert len(records) == 1

    def test_get_period_records_all(self, tracker_agent):
        """Testaa kaikkien tietueiden haku."""
        tracker_agent.run("Track", model="openai/gpt-4o-mini", input_tokens=100, output_tokens=50, cost=0.001)
        tracker_agent.run("Track", model="openai/gpt-4o", input_tokens=200, output_tokens=100, cost=0.01)
        records = tracker_agent._get_period_records("all")
        assert len(records) == 2

    def test_compute_aggregate(self, tracker_agent):
        """Testaa aggregaatin laskeminen."""
        records = [
            {"model": "openai/gpt-4o", "input_tokens": 100, "output_tokens": 50, "cost": 0.01, "timestamp": datetime.now().isoformat()},
            {"model": "openai/gpt-4o-mini", "input_tokens": 200, "output_tokens": 100, "cost": 0.005, "timestamp": datetime.now().isoformat()},
        ]
        agg = tracker_agent._compute_aggregate(records)
        assert agg["total_input"] == 300
        assert agg["total_output"] == 150
        assert agg["total_tokens"] == 450
        assert agg["total_cost"] == 0.015
        assert len(agg["model_breakdown"]) == 2

    def test_unknown_action(self, tracker_agent):
        """Testaa tuntematon toiminto."""
        result = tracker_agent.run("Tuntematon", action="unknown")
        assert result.success is False

    def test_default_action_is_track(self, tracker_agent):
        """Testaa että oletustoiminto on track."""
        result = tracker_agent.run("Seuraa", model="openai/gpt-4o-mini", input_tokens=100, output_tokens=50, cost=0.001)
        assert result.success is True

    def test_gateway_actions_available(self):
        """Testaa että kaikki gateway-toiminnot ovat määritelty."""
        assert "chat" in GATEWAY_ACTIONS
        assert "complete" in GATEWAY_ACTIONS
        assert "embed" in GATEWAY_ACTIONS
        assert "list_models" in GATEWAY_ACTIONS

    def test_token_tracker_actions_available(self):
        """Testaa että kaikki token-tracker-toiminnot ovat määritelty."""
        assert "track" in TOKEN_TRACKER_ACTIONS
        assert "report" in TOKEN_TRACKER_ACTIONS
        assert "reset" in TOKEN_TRACKER_ACTIONS


# ============================================================
# Module-level tests
# ============================================================


class TestAIGatewayModuleLevel:
    """Moduulin ja paketin tasolla olevat testit."""

    def test_import_from_agents_package(self):
        """Testaa että kaikki voidaan tuoda agents-paketista."""
        from agents import AIGatewayAgent, LLMRouterAgent, TokenTrackerAgent
        assert AIGatewayAgent is not None
        assert LLMRouterAgent is not None
        assert TokenTrackerAgent is not None

    def test_import_input_output_models(self):
        """Testaa että kaikki Input/Output-mallit on tuotavissa."""
        from agents import (
            AIGatewayInput,
            AIGatewayOutput,
            LLMRouterInput,
            LLMRouterOutput,
            TokenTrackerInput,
            TokenTrackerOutput,
        )
        assert AIGatewayInput is not None
        assert AIGatewayOutput is not None
        assert LLMRouterInput is not None
        assert LLMRouterOutput is not None
        assert TokenTrackerInput is not None
        assert TokenTrackerOutput is not None

    def test_import_constants(self):
        """Testaa että kaikki vakiot on tuotavissa."""
        from agents import (
            GATEWAY_ACTIONS,
            ROUTING_CRITERIA,
            TOKEN_TRACKER_ACTIONS,
            MODEL_REGISTRY,
        )
        assert GATEWAY_ACTIONS is not None
        assert ROUTING_CRITERIA is not None
        assert TOKEN_TRACKER_ACTIONS is not None
        assert MODEL_REGISTRY is not None

    def test_all_agents_subclass_baseagent(self):
        """Testaa että kaikki agentit ovat BaseAgent-alaisluokkia."""
        from agents.base import BaseAgent

        assert issubclass(AIGatewayAgent, BaseAgent)
        assert issubclass(LLMRouterAgent, BaseAgent)
        assert issubclass(TokenTrackerAgent, BaseAgent)

    def test_model_registry_has_major_providers(self):
        """Testaa että mallirekisteri sisältää suuret palveluntarjoajat."""
        providers = set()
        for info in MODEL_REGISTRY.values():
            providers.add(info["provider"])
        assert "openai" in providers
        assert "anthropic" in providers

    def test_model_capabilities_structure(self):
        """Testaa että mallien ominaisuudet ovat oikean muotoiset."""
        for model_id, info in MODEL_REGISTRY.items():
            assert isinstance(info["capabilities"], list)
            assert isinstance(info["context_length"], int)
            assert info["context_length"] > 0
            assert isinstance(info["input_price_per_1k"], (int, float))
            assert isinstance(info["output_price_per_1k"], (int, float))
