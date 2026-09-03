"""
AIGatewayAgent-moduuli (M17) — keskitetty tekoälymallin käsittely.

Sisältää kolme agenttia:
- AIGatewayAgent: OpenRouter/LangChain-keskinäinen pääsymalli, mallien vaihto ja yhdenmukainen API
- LLMRouterAgent: reitittää pyynnöt oikeaan malliin (kustannus, latency, capability -tasapaino)
- TokenTrackerAgent: seuraa tokenikulumia ja kustannuksia (per tokeni, kuukausikulu)
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, ClassVar, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


# Gateway-toiminnot
GATEWAY_ACTIONS: dict[str, str] = {
    "chat": "Chat-viestien käsittely",
    "complete": "Tekstin täydentäminen",
    "embed": "Paikannusvektoreiden luominen",
    "list_models": "Luettele saatavilla olevat modelit",
}

# Reititystoiminnot
ROUTING_ACTIONS: dict[str, str] = {
    "route": "Reititä pyyntö malliin",
    "evaluate": "Arvioi mallit kriteereillä",
    "compare": "Vertaile mallien ominaisuuksia",
}

# Token-tracker-toiminnot
TOKEN_TRACKER_ACTIONS: dict[str, str] = {
    "track": "Seuraa tokenikulumia",
    "report": "Luo raportti kustannuksista",
    "reset": "Nollaa laskurit",
}

# Tunnetut mallit OpenRouterissa (simuloitu rekisteri)
MODEL_REGISTRY: dict[str, dict[str, Any]] = {
    "openai/gpt-4o": {
        "name": "GPT-4o",
        "provider": "openai",
        "context_length": 128000,
        "input_price_per_1k": 0.005,
        "output_price_per_1k": 0.015,
        "capabilities": ["text", "code", "reasoning", "multilingual"],
        "latency_tier": "fast",
        "max_output_tokens": 16384,
    },
    "openai/gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "provider": "openai",
        "context_length": 128000,
        "input_price_per_1k": 0.00015,
        "output_price_per_1k": 0.0006,
        "capabilities": ["text", "code", "fast"],
        "latency_tier": "fast",
        "max_output_tokens": 16384,
    },
    "anthropic/claude-3-5-sonnet": {
        "name": "Claude 3.5 Sonnet",
        "provider": "anthropic",
        "context_length": 200000,
        "input_price_per_1k": 0.003,
        "output_price_per_1k": 0.015,
        "capabilities": ["text", "code", "reasoning", "multilingual"],
        "latency_tier": "medium",
        "max_output_tokens": 8192,
    },
    "anthropic/claude-3-5-haiku": {
        "name": "Claude 3.5 Haiku",
        "provider": "anthropic",
        "context_length": 200000,
        "input_price_per_1k": 0.00025,
        "output_price_per_1k": 0.00125,
        "capabilities": ["text", "code", "fast"],
        "latency_tier": "fast",
        "max_output_tokens": 8192,
    },
    "google/gemini-2.0-flash": {
        "name": "Gemini 2.0 Flash",
        "provider": "google",
        "context_length": 1000000,
        "input_price_per_1k": 0.0015,
        "output_price_per_1k": 0.0035,
        "capabilities": ["text", "code", "multilingual"],
        "latency_tier": "fast",
        "max_output_tokens": 8192,
    },
}

# Reitityskriteerit
ROUTING_CRITERIA: dict[str, list[str]] = {
    "cost": ["input_price_per_1k", "output_price_per_1k"],
    "latency": ["latency_tier"],
    "capability": ["capabilities"],
    "context": ["context_length"],
}


class AIGatewayInput(AgentInput):
    """AIGatewayAgentin syöte."""
    action: str = Field(default="chat", description="Toiminto (chat, complete, embed, list_models).")
    model: str = Field(default="openai/gpt-4o-mini", description="Käytettävä malli.")
    messages: list[dict[str, str]] = Field(default_factory=list, description="Viestit (chat-muodossa).")
    prompt: str = Field(default="", description="Täydennyskehoite (complete-toimintoissa).")
    max_tokens: int = Field(default=1024, description="Enintään tuotettavat tokenit.")
    temperature: float = Field(default=0.7, description="Lämpötila (0-1).")
    api_key: str = Field(default="", description="OpenRouter-API-avain.")


class AIGatewayOutput(AgentOutput):
    """AIGatewayAgentin tuloste."""
    response: str = Field(default="", description="Mallin vastaus.")
    model_used: str = Field(default="", description="Käytetty malli.")
    tokens_used: dict[str, int] = Field(default_factory=dict, description="Käytetyt tokenit (input, output, total).")
    estimated_cost: float = Field(default=0, description="Arvioitu kustannus USD:ssa.")
    response_format: str = Field(default="text", description="Vasteen muoto (text, json, embed).")
    available_models: list[dict[str, Any]] = Field(default_factory=list, description="Saatavilla olevat mallit.")
    latency_ms: int = Field(default=0, description="Reakointi millisekunteina.")


class LLMRouterInput(AgentInput):
    """LLMRouterAgentin syöte."""
    action: str = Field(default="route", description="Toiminto (route, evaluate, compare).")
    criteria: list[str] = Field(default_factory=list, description="Reitityskriteerit (cost, latency, capability, context).")
    required_capabilities: list[str] = Field(default_factory=list, description="Vaaditut malliominaisuudet.")
    max_cost: float = Field(default=0.01, description="Maksimikustannus USD:ssa.")
    max_latency: str = Field(default="medium", description="Maksimi latenssi (fast, medium, slow).")
    context_length: int = Field(default=8000, description="Vaatittu kontekstipituus.")
    compare_models: list[str] = Field(default_factory=list, description="Vertailuun käytettävät mallit.")


class LLMRouterOutput(AgentOutput):
    """LLMRouterAgentin tuloste."""
    routed_model: str = Field(default="", description="Reititetty malli.")
    candidate_models: list[dict[str, Any]] = Field(default_factory=list, description="Ehdokasmallit.")
    routing_reason: str = Field(default="", description="Reitityssyy.")
    model_scores: dict[str, float] = Field(default_factory=dict, description="Mallit pisteinä.")
    comparison_results: list[dict[str, Any]] = Field(default_factory=list, description="Vertailutulokset.")
    best_model: str = Field(default="", description="Paras malli vertailun perusteella.")


class TokenTrackerInput(AgentInput):
    """TokenTrackerAgentin syöte."""
    action: str = Field(default="track", description="Toiminto (track, report, reset).")
    model: str = Field(default="", description="Malli, jota seurataan.")
    input_tokens: int = Field(default=0, description="Syötetokenit.")
    output_tokens: int = Field(default=0, description="Tuottamot tokenit.")
    cost: float = Field(default=0, description="Tähän kierrokseen kuluva summa USD:ssa.")
    period: str = Field(default="daily", description="Raportointi-ajanjakso (daily, weekly, monthly).")


class TokenTrackerOutput(AgentOutput):
    """TokenTrackerAgentin tuloste."""
    total_tokens: int = Field(default=0, description="Kaikkia käytettyjä tokenit.")
    input_tokens: int = Field(default=0, description="Kaikki syötetokenit.")
    output_tokens: int = Field(default=0, description="Kaikki tuotetut tokenit.")
    total_cost: float = Field(default=0, description="Kokonaiskustannus USD:ssä.")
    records: list[dict[str, Any]] = Field(default_factory=list, description="Tokenitietueet.")
    period: str = Field(default="daily", description="Raportointijakso.")
    model_breakdown: dict[str, dict[str, Any]] = Field(default_factory=dict, description="Mallit kohtaiset katseelmat.")


class AIGatewayAgent(BaseAgent):
    """
    AIGatewayAgent tarjoaa keskitetyn pääsyn tekoälymalleihin OpenRouterin kautta.

    Se abstrioi OpenAI/LangChain-integraation, mallien väzin ja yhdenmukaisen API.

    Usage:
        agent = AIGatewayAgent(api_key="sk-or-v1-...")
        result = agent.run("Kysy mistä elämä on", model="openai/gpt-4o-mini")
    """

    agent_type: ClassVar[str] = "ai_gateway"
    input_schema = AIGatewayInput
    output_schema = AIGatewayOutput

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self._default_model = kwargs.get("default_model", os.getenv("DEFAULT_MODEL", "openai/gpt-4o-mini"))

    def _get_model_info(self, model_id: str) -> Optional[dict[str, Any]]:
        """Hakee mallin tiedot rekisteristä."""
        return MODEL_REGISTRY.get(model_id)

    def _estimate_tokens(self, text: str) -> int:
        """Arvioi tokeniemää tekstistä."""
        return max(1, len(text) // 4)

    def _calculate_cost(self, model_info: dict[str, Any], input_tokens: int, output_tokens: int) -> float:
        """Laskee arvioidun kustannuksen."""
        input_cost = (input_tokens / 1000) * model_info.get("input_price_per_1k", 0)
        output_cost = (output_tokens / 1000) * model_info.get("output_price_per_1k", 0)
        return round(input_cost + output_cost, 6)

    def _simulate_chat_response(self, messages: list[dict[str, str]], model: str) -> str:
        """Simuloi chat-vastausta (koska emme voi oikeasti kutsua API:ta tässä ympäristössä)."""
        model_info = self._get_model_info(model)
        model_name = model_info["name"] if model_info else model

        # Käytä viimeistä käyttäjäviesti vastauksena
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        return f"Tämä on simuloitu vastaus mallilta {model_name}. Kysymyksesi oli: '{last_user_msg[:100]}{'...' if len(last_user_msg) > 100 else ''}'"

    def _simulate_complete_response(self, prompt: str, model: str) -> str:
        """Simuloi täydennystä."""
        model_info = self._get_model_info(model)
        model_name = model_info["name"] if model_info else model
        return f"Tämä on simuloitu täydennys mallilta {model_name} kehikseen: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'"

    def _run(self, input_data: AIGatewayInput) -> AIGatewayOutput:
        """AIGatewayAgentin päälogiika."""
        action = input_data.action.lower()
        start_time = datetime.now()

        if action == "list_models":
            models = [
                {"id": model_id, **info}
                for model_id, info in MODEL_REGISTRY.items()
            ]
            return AIGatewayOutput(
                success=True,
                result={"model_count": len(models)},
                message=f"{len(models)} mallia saatavilla.",
                agent_type=self.agent_type,
                available_models=models,
                response_format="list",
            )

        # Valitse malli
        model = input_data.model or self._default_model
        model_info = self._get_model_info(model)

        if not model_info and action != "chat":
            return AIGatewayOutput(
                success=False,
                result=None,
                message=f"Mallia '{model}' ei löydy rekisteristä.",
                agent_type=self.agent_type,
            )

        if action == "chat":
            if not input_data.messages:
                return AIGatewayOutput(
                    success=False,
                    result=None,
                    message="Ei viestejä annettu. Käytä 'messages'-parametria.",
                    agent_type=self.agent_type,
                )

            response = self._simulate_chat_response(input_data.messages, model)
            input_tokens = sum(self._estimate_tokens(msg.get("content", "")) for msg in input_data.messages)
            output_tokens = self._estimate_tokens(response)
            cost = self._calculate_cost(model_info or MODEL_REGISTRY[model], input_tokens, output_tokens)

            latency = (datetime.now() - start_time).total_seconds() * 1000

            return AIGatewayOutput(
                success=True,
                result={"response": response, "model": model},
                message=f"Vastaus vastaanotettu mallilta {model}.",
                agent_type=self.agent_type,
                response=response,
                model_used=model,
                tokens_used={"input": input_tokens, "output": output_tokens, "total": input_tokens + output_tokens},
                estimated_cost=round(cost, 4),
                latency_ms=int(latency),
            )

        elif action == "complete":
            if not input_data.prompt:
                return AIGatewayOutput(
                    success=False,
                    result=None,
                    message="Kea kysymys on pakollinen täydennyksessä.",
                    agent_type=self.agent_type,
                )

            response = self._simulate_complete_response(input_data.prompt, model)
            input_tokens = self._estimate_tokens(input_data.prompt)
            output_tokens = self._estimate_tokens(response)
            cost = self._calculate_cost(model_info or MODEL_REGISTRY[model], input_tokens, output_tokens)
            latency = (datetime.now() - start_time).total_seconds() * 1000

            return AIGatewayOutput(
                success=True,
                result={"response": response, "model": model},
                message=f"Täydennys valmiina mallilta {model}.",
                agent_type=self.agent_type,
                response=response,
                model_used=model,
                tokens_used={"input": input_tokens, "output": output_tokens, "total": input_tokens + output_tokens},
                estimated_cost=round(cost, 4),
                latency_ms=int(latency),
            )

        elif action == "embed":
            # Simuloi vektoripohjaisen vastapinnin
            return AIGatewayOutput(
                success=True,
                result={"embedded": True, "dimensions": 1536},
                message=f"Paikannus luotsattu mallilta {model}.",
                agent_type=self.agent_type,
                model_used=model,
                response_format="embed",
            )

        else:
            return AIGatewayOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'. Käytä yhtä: chat, complete, embed, list_models.",
                agent_type=self.agent_type,
            )


class LLMRouterAgent(BaseAgent):
    """
    LLMRouterAgent reitittää pyyntöjä oikeaan malliin.

    Se arviolee mallit kriteereillä (kustannus, latenssi, ominaisuus, konteksti)
    ja valitsee parhaan mallin annetuissa rajoissa.

    Usage:
        agent = LLMRouterAgent()
        result = agent.run("Reitä tämä halvinta malliin", criteria=["cost"], max_cost=0.005)
    """

    agent_type: ClassVar[str] = "llm_router"
    input_schema = LLMRouterInput
    output_schema = LLMRouterOutput

    def _score_model(self, model_info: dict[str, Any], criteria: list[str], required_caps: list[str]) -> float:
        """Pisteytää mallin kriteerien perusteella. Alempi pisteet = parempi."""
        score = 0.0

        if "cost" in criteria:
            avg_cost = (model_info.get("input_price_per_1k", 0) + model_info.get("output_price_per_1k", 0)) / 2
            score += avg_cost * 100  # kustannus osuus

        if "latency" in criteria:
            latency_map = {"fast": 0, "medium": 5, "slow": 10}
            score += latency_map.get(model_info.get("latency_tier", "medium"), 5)

        if "capability" in criteria:
            # Laske ominaisuuksia
            caps = len(model_info.get("capabilities", []))
            score += max(0, 10 - caps)  # vähemmän ominaisuuksia = enemmän rajoitteita täyttävästi

        if "context" in criteria:
            ctx = model_info.get("context_length", 4000)
            # pienempi konteksti jos se riittää = parempi
            if ctx < 8000:
                score += 2

        # Tarkista vaaditut ominaisuudet
        model_caps = set(model_info.get("capabilities", []))
        required = set(cap.lower() for cap in required_caps)
        if required and not required.issubset(model_caps):
            score += 100  # rangaista ei-tukevat mallit

        return round(score, 2)

    def _filter_models(self, required_caps: list[str], max_cost: float, context_length: int) -> list[tuple[str, dict[str, Any]]]:
        """Suodata mallit kriteereillä."""
        filtered = []
        for model_id, info in MODEL_REGISTRY.items():
            # Tarkista ominaisuudet
            model_caps = set(cap.lower() for cap in info.get("capabilities", []))
            required = set(cap.lower() for cap in required_caps)
            if required and not required.issubset(model_caps):
                continue

            # Tarkista konteksti
            if context_length and info.get("context_length", 0) < context_length:
                continue

            # Tarkista maksimikustannus (arvioitu 1000 input + 1000 output tokenia)
            est_cost = (1000 / 1000) * info.get("input_price_per_1k", 999) + (1000 / 1000) * info.get("output_price_per_1k", 999)
            if est_cost > max_cost * 100:  # skaalataan oikeaksi
                pass  # Ei suodata — sallitse kaikat

            filtered.append((model_id, info))

        return filtered

    def _select_best(self, candidates: list[tuple[str, dict[str, Any]]], criteria: list[str], required_caps: list[str]) -> tuple[str, str]:
        """Valitsee parhaan mallin."""
        if not candidates:
            return "", "Ei sopivia malleja löytynyt annetuissa rajoissa."

        scored = []
        for model_id, info in candidates:
            score = self._score_model(info, criteria, required_caps)
            scored.append((model_id, score, info))

        # Valitse alhainen pisteet (paras)
        scored.sort(key=lambda x: x[1])
        best = scored[0]

        reason = f"Valittu {best[2]['name']} pisteillä {best[1]} (kritiiinit: {', '.join(criteria) or 'ei kriteerejä'})."

        return best[0], reason

    def _run(self, input_data: LLMRouterInput) -> LLMRouterOutput:
        """LLMRouterAgentin päälogiikka."""
        action = input_data.action.lower()

        if action == "route":
            candidates = self._filter_models(
                input_data.required_capabilities,
                input_data.max_cost,
                input_data.context_length,
            )

            best_model, reason = self._select_best(candidates, input_data.criteria, input_data.required_capabilities)

            if not best_model:
                return LLMRouterOutput(
                    success=False,
                    result=None,
                    message=reason,
                    agent_type=self.agent_type,
                )

            scores = {}
            for model_id, info in candidates:
                scores[model_id] = self._score_model(info, input_data.criteria, input_data.required_capabilities)

            return LLMRouterOutput(
                success=True,
                result={"routed_model": best_model, "candidates": len(candidates)},
                message=f"Reititetty malliin {best_model}.",
                agent_type=self.agent_type,
                routed_model=best_model,
                candidate_models=[{"id": m, **info} for m, info in candidates],
                routing_reason=reason,
                model_scores=scores,
            )

        elif action == "evaluate":
            candidates = list(MODEL_REGISTRY.items())
            scores = {}
            for model_id, info in candidates:
                scores[model_id] = self._score_model(info, input_data.criteria, input_data.required_capabilities)

            sorted_models = sorted(scores.items(), key=lambda x: x[1])[:5]

            return LLMRouterOutput(
                success=True,
                result={"evaluated": len(scores), "top_model": sorted_models[0][0]},
                message=f"Arvioitu {len(scores)} mallia. Paras: {sorted_models[0][0]} ({sorted_models[0][1]} pistettä).",
                agent_type=self.agent_type,
                model_scores=scores,
                routed_model=sorted_models[0][0],
            )

        elif action == "compare":
            models_to_compare = input_data.compare_models if input_data.compare_models else ["openai/gpt-4o", "openai/gpt-4o-mini", "anthropic/claude-3-5-sonnet"]
            results = []

            for model_id in models_to_compare:
                info = MODEL_REGISTRY.get(model_id)
                if info:
                    score = self._score_model(info, input_data.criteria, input_data.required_capabilities)
                    results.append({
                        "model": model_id,
                        "name": info["name"],
                        "provider": info["provider"],
                        "cost": info["input_price_per_1k"] + info["output_price_per_1k"],
                        "latency_tier": info["latency_tier"],
                        "capabilities": info["capabilities"],
                        "context_length": info["context_length"],
                        "score": score,
                    })

            results.sort(key=lambda x: x["score"])
            best = results[0]["model"] if results else ""

            return LLMRouterOutput(
                success=True,
                result={"compared": len(results), "best": best},
                message=f"Vertailu valmiina. Paras: {best}.",
                agent_type=self.agent_type,
                comparison_results=results,
                best_model=best,
                routed_model=best,
            )

        else:
            return LLMRouterOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'. Käytä yhtä: route, evaluate, compare.",
                agent_type=self.agent_type,
            )


class TokenTrackerAgent(BaseAgent):
    """
    TokenTrackerAgent seuroo tokenikulumia ja kustannuksia.

    Se kokoaa tokenitietueet mallin, ajankohdan ja kustannuksena ja
    tuottaa raportteja eri ajanjaksoissa.

    Usage:
        agent = TokenTrackerAgent()
        result = agent.run("Seuraa tätä pyyntöä", model="openai/gpt-4o-mini", input_tokens=150, output_tokens=75, cost=0.002)
    """

    agent_type: ClassVar[str] = "token_tracker"
    input_schema = TokenTrackerInput
    output_schema = TokenTrackerOutput

    # Sisäinen tietovarasto (simuloi tietokantaa)
    _records: ClassVar[list[dict[str, Any]]] = []

    def _get_period_records(self, period: str) -> list[dict[str, Any]]:
        """Hakee tietueet annetusta jaksosta."""
        today = datetime.now().date()
        records = []

        for record in self._records:
            record_date = datetime.fromisoformat(record["timestamp"]).date()
            if period == "daily" and record_date == today:
                records.append(record)
            elif period == "weekly" and (today - record_date).days <= 7:
                records.append(record)
            elif period == "monthly" and (today.year == record_date.year and today.month == record_date.month):
                records.append(record)
            elif period == "all":
                records.append(record)

        return records

    def _compute_aggregate(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        """Laskee aggregaatit tietueista."""
        total_input = sum(r.get("input_tokens", 0) for r in records)
        total_output = sum(r.get("output_tokens", 0) for r in records)
        total_tokens = total_input + total_output
        total_cost = sum(r.get("cost", 0) for r in records)

        model_breakdown: dict[str, dict[str, Any]] = {}
        for r in records:
            model = r.get("model", "tuntematon")
            if model not in model_breakdown:
                model_breakdown[model] = {"tokens": 0, "cost": 0, "calls": 0}
            model_breakdown[model]["tokens"] += r.get("input_tokens", 0) + r.get("output_tokens", 0)
            model_breakdown[model]["cost"] = round(model_breakdown[model]["cost"] + r.get("cost", 0), 6)
            model_breakdown[model]["calls"] += 1

        return {
            "total_input": total_input,
            "total_output": total_output,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 6),
            "model_breakdown": model_breakdown,
            "record_count": len(records),
        }

    def _run(self, input_data: TokenTrackerInput) -> TokenTrackerOutput:
        """TokenTrackerAgentin päälogiika."""
        action = input_data.action.lower()

        if action == "track":
            if not input_data.model:
                return TokenTrackerOutput(
                    success=False,
                    result=None,
                    message="Mallin nimi vaaditaan seurantaan.",
                    agent_type=self.agent_type,
                )

            record = {
                "model": input_data.model,
                "input_tokens": input_data.input_tokens,
                "output_tokens": input_data.output_tokens,
                "cost": input_data.cost,
                "timestamp": datetime.now().isoformat(),
            }
            self._records.append(record)

            total_tokens = input_data.input_tokens + input_data.output_tokens

            return TokenTrackerOutput(
                success=True,
                result={"recorded": True, "total_tokens": total_tokens},
                message=f"Tokenit tallennettu mallille {input_data.model}: {total_tokens} tokenia ({input_data.cost} USD).",
                agent_type=self.agent_type,
                total_tokens=total_tokens,
                input_tokens=input_data.input_tokens,
                output_tokens=input_data.output_tokens,
                total_cost=round(input_data.cost, 6),
                records=[record],
                period=input_data.period,
            )

        elif action == "report":
            period = input_data.period
            period_records = self._get_period_records(period)
            aggregate = self._compute_aggregate(period_records)

            return TokenTrackerOutput(
                success=True,
                result=aggregate,
                message=f"Raportti ({period}): {aggregate['record_count']} tietuetta, {aggregate['total_tokens']} tokenia, {aggregate['total_cost']} USD.",
                agent_type=self.agent_type,
                total_tokens=aggregate["total_tokens"],
                input_tokens=aggregate["total_input"],
                output_tokens=aggregate["total_output"],
                total_cost=aggregate["total_cost"],
                records=period_records,
                period=period,
                model_breakdown=aggregate["model_breakdown"],
            )

        elif action == "reset":
            count = len(self._records)
            self._records.clear()

            return TokenTrackerOutput(
                success=True,
                result={"reset": True, "cleared_records": count},
                message=f"Tokenitietueet nollattu. Poistettu {count} tietuetta.",
                agent_type=self.agent_type,
                total_tokens=0,
                input_tokens=0,
                output_tokens=0,
                total_cost=0,
                records=[],
                period=input_data.period,
            )

        else:
            return TokenTrackerOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'. Käytä yhtä: track, report, reset.",
                agent_type=self.agent_type,
            )
