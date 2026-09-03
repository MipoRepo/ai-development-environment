"""
AgentEngineeringAgent-moduuli (M16) — agenttien muotoilu, prompttien optimointi ja agenttitehtaan.

Sisältää kolme agenttia:
- AgentDesignAgent: suunnittelee ja luo uusia agenteja (tyyppi, skeemat, työkalut, kuvaus)
- PromptOptimizerAgent: optimoi prompteja (pituus, token-arvio, parametrien hienosäädöt, parannukset)
- AgentFactoryAgent: luo agentteja instansseja dynaamisesti (registrointi, konfigurointi, instantiate)
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


# Agentin kehitystoiminnot
AGENT_DESIGN_ACTIONS: dict[str, str] = {
    "design": "Suunnittele uusi agentti",
    "analyze": "Analysoi olemassa oleva agentti",
    "validate": "Varmista agentin skeema",
    "recommend": "Suodata agenttityypeille ja työkaluille",
}

# Prompt-optimointitoiminnot
PROMPT_OPTIMIZE_ACTIONS: dict[str, str] = {
    "optimize": "Optimoi prompt",
    "analyze": "Analysoi promptin rakenne",
    "estimate": "Arvioi tokenimäärä",
    "suggest": "Ehdota parannuksia",
}

# AgentFactory-toiminnot
AGENT_FACTORY_ACTIONS: dict[str, str] = {
    "create": "Luo agentti instanssi",
    "register": "Rekisteroi agentintyyppi",
    "list": "Luettele kaikki rekisteröidyt agentit",
    "instantiate": "Instantiate agent from config",
}

# Tunnetut agenttityypit
KNOWN_AGENT_TYPES: list[str] = [
    "director",
    "project_manager",
    "requirements",
    "researcher",
    "technology_researcher",
    "developer",
    "refactoring",
    "code_review",
    "test_designer",
    "tester",
    "qa",
    "security_review",
    "sast",
    "dependency_security",
    "secrets",
    "container_security",
    "technical_writer",
    "api_documentation",
    "user_documentation",
    "mkdocs",
    "test_runner",
    "performance_test",
    "integration_test",
    "workflow_orchestrator",
    "multi_agent_coordinator",
    "docker",
    "ci_cd",
    "infrastructure",
    "deployment",
    "mentor",
    "explainer",
    "pedagogy",
    "content_designer",
    "learning_path",
    "assessment",
    "feedback",
    "knowledge",
    "memory",
    "context_compiler",
    "upgrade",
    "cleanup",
    "dependency",
    "release_manager",
    "changelog",
    "compliance",
]

# Agentin skeeman kentät
SCHEMA_FIELDS: dict[str, list[str]] = {
    "input": [
        "task",
        "context",
        "metadata",
    ],
    "output": [
        "success",
        "result",
        "message",
        "agent_type",
    ],
}

# Prompt-optimointiohjeet
PROMPT_OPTIMIZATION_TIPS: list[str] = [
    "Vältä epäselvyyksiä — käytä selkeitä, kuvaavia kieltä.",
    "Pysy tiivis — poista turhoutta ja toistuvia lauseita.",
    "Käytä rakateltua muotoa (esim. listat, numeroitujen) kompleksisille ohjeille.",
    "Määritä tarkat rajoitteet ja esimerkit.",
    "Käytä negatiivisia esimerkkejä mitä ei tule tehdä.",
    "Sido konteksti selvästi erilliseen parametriin.",
    "Vältä promptin lukemista järjestelmässä (prompt injection -riski).",
]


class AgentDesignInput(AgentInput):
    """AgentDesignAgentin syöte."""
    action: str = Field(default="design", description="Toiminto (design, analyze, validate, recommend).")
    agent_name: str = Field(default="", description="Uuden agentin nimi.")
    agent_description: str = Field(default="", description="Uuden agentin kuvaus.")
    agent_type: str = Field(default="", description="Agentin tyyppi (esim. custom_agent).")
    capabilities: list[str] = Field(default_factory=list, description="Agentin kyvykkyykset (esim. [analyze, generate, summarize]).")
    input_fields: dict[str, Any] = Field(default_factory=dict, description="Syöteskeeman kentät ja kuvaukset.")
    output_fields: dict[str, Any] = Field(default_factory=dict, description="Tulosteskeeman kentät ja kuvaukset.")
    required_tools: list[str] = Field(default_factory=list, description="Tarvittavat työkalut.")
    existing_agent_code: str = Field(default="", description="Olemassa olevan agentin koodi analysointia varten.")


class AgentDesignOutput(AgentOutput):
    """AgentDesignAgentin tuloste."""
    agent_spec: dict[str, Any] = Field(default_factory=dict, description="Suunniteltu agentin määritelmä.")
    validation_issues: list[str] = Field(default_factory=list, description="Validointiongelmista.")
    recommended_agent_types: list[str] = Field(default_factory=list, description="Suositellut agenttitapaukset.")
    input_schema_suggestion: dict[str, str] = Field(default_factory=dict, description="Ehdoteltu syötetietorakenne.")
    output_schema_suggestion: dict[str, str] = Field(default_factory=dict, description="Ehdoteltu tulostetietorakenne.")
    tool_requirements: list[str] = Field(default_factory=list, description="Työmäärävaatimukset.")


class PromptOptimizerInput(AgentInput):
    """PromptOptimizerAgentin syöte."""
    action: str = Field(default="optimize", description="Toiminto (optimize, analyze, estimate, suggest).")
    prompt: str = Field(default="", description="Optimoitava prompt.")
    context_variables: list[str] = Field(default_factory=list, description="Käytetyt kontekstimuuttujat.")
    target_token_limit: int = Field(default=4096, description="Kohde tokenimäärä.")
    temperature: float = Field(default=0.7, description="Lämpötila-asetus.")
    model: str = Field(default="gpt-3.5-turbo", description="Käytetty malli.")


class PromptOptimizerOutput(AgentOutput):
    """PromptOptimizerAgentin tuloste."""
    optimized_prompt: str = Field(default="", description="Optimoitu prompt.")
    original_token_estimate: int = Field(default=0, description="Alkuperäisen promptin arvioitu tokenimäärä.")
    optimized_token_estimate: int = Field(default=0, description="Optimoidun promptin arvioitu tokenimäärä.")
    tokens_saved: int = Field(default=0, description="Säästetyt tokenit.")
    suggestions: list[str] = Field(default_factory=list, description="Parannusehdotukset.")
    prompt_length: int = Field(default=0, description="Optimoidun promptin pituus merkekeinä.")
    optimization_score: float = Field(default=0, description="Optimointipisteet 0-100.")


class AgentFactoryInput(AgentInput):
    """AgentFactoryAgentin syöte."""
    action: str = Field(default="create", description="Toiminto (create, register, list, instantiate).")
    agent_type: str = Field(default="", description=" Agentin tyyppi.")
    agent_name: str = Field(default="", description="Agentin nimi.")
    module_path: str = Field(default="", description="Agentin moduulin polku.")
    config: dict[str, Any] = Field(default_factory=dict, description="Agentin konfiguraatio.")
    registered_agents: dict[str, str] = Field(default_factory=dict, description="Rekisteröidyt agentit (tyyppi -> moduuli).")


class AgentFactoryOutput(AgentOutput):
    """AgentFactoryAgentin tuloste."""
    agent_instance: dict[str, Any] = Field(default_factory=dict, description="Luodun agentin instanssin tiedot.")
    registered_agents: dict[str, str] = Field(default_factory=dict, description="Kaikki rekisteröidyt agentit.")
    success_message: str = Field(default="", description="Onnistumistviesti.")


class AgentDesignAgent(BaseAgent):
    """
    AgentDesignAgent suunnittelee ja validoi uusia aiheita.

    Se auttaa määrittämään agentin tyypin, skeemat, työkalut ja kuvauksen.

    Usage:
        agent = AgentDesignAgent()
        result = agent.run("Suunnittele data-analyysi agentti", agent_name="AnalyzerAgent", capabilities=["analyze", "report"])
    """

    agent_type: ClassVar[str] = "agent_design"
    input_schema = AgentDesignInput
    output_schema = AgentDesignOutput

    def _validate_agent_name(self, name: str) -> list[str]:
        """Validoi agentin nimi."""
        issues = []
        if not name:
            issues.append("Agentin nimi on pakollinen.")
        elif not re.match(r"^[A-Z][a-zA-Z0-9]*Agent$", name):
            issues.append(f"Agentin nimen tulee olla PascalCase + 'Agent' (esim. MyAgent), ei '{name}'.")
        if " " in name:
            issues.append("Agentin nimessä ei saa olla välilyöntejä.")
        return issues

    def _validate_input_fields(self, fields: dict[str, Any]) -> list[str]:
        """Validoi syötetietorakenteen."""
        issues = []
        if not fields:
            issues.append("Syötetietorakenne on tyhjä. Lisää vähintään task-kenttä.")
        else:
            if "task" not in fields:
                issues.append("Syötetietorakenteessa tulee olla 'task'-kenttä.")
            for field_name, field_def in fields.items():
                if not isinstance(field_def, (dict, str)):
                    issues.append(f"Kenttä '{field_name}' tulee olla merkkijono tai sanakirja.")
        return issues

    def _validate_output_fields(self, fields: dict[str, Any]) -> list[str]:
        """Validoi tulostetietorakenteen."""
        issues = []
        if not fields:
            issues.append("Tulostetietorakenne on tyhjä. Lisää vähintään 'success'-kenttä.")
        else:
            required = {"success", "message", "agent_type"}
            missing = required - set(fields.keys())
            if missing:
                issues.append(f"Tulostetietorakenteessa puuttuu vaaditut kentät: {', '.join(missing)}.")
        return issues

    def _suggest_input_schema(self, capabilities: list[str]) -> dict[str, str]:
        """Ehdottelee syöteskeemaa kyvykkyyksien perusteella."""
        base_fields = {
            "task": "Käsiteltävä tehtävä luonnollisessa kielessä.",
            "context": "Lisäkontekstitietoja (esim. projektin rakenne).",
            "metadata": "Vapaa metadata.",
        }

        for cap in capabilities:
            cap_lower = cap.lower()
            if cap_lower == "analyze":
                base_fields["target"] = "Analysoitava kohde (tiedosto, moduuli, data)."
            elif cap_lower == "generate":
                base_fields["requirements"] = "Tuotantomvaatimukset."
            elif cap_lower == "summarize":
                base_fields["source"] = "Tiivittelyn lähde."
            elif cap_lower == "classify":
                base_fields["categories"] = "Luokitteluun käytettävät luokat."
            elif cap_lower == "search":
                base_fields["query"] = "Hakukysely."

        return base_fields

    def _suggest_output_schema(self, capabilities: list[str]) -> dict[str, str]:
        """Ehdottelee tulosteskeemaa kyvykkyyksiden perusteella."""
        base_fields = {
            "success": "Onnistuiko toiminto.",
            "result": "Tulossievu.",
            "message": "Kuvaava viesti.",
            "agent_type": "Agentin tyyppi.",
        }

        for cap in capabilities:
            cap_lower = cap.lower()
            if cap_lower == "analyze":
                base_fields["findings"] = "Analyysitulokset."
            elif cap_lower == "generate":
                base_fields["generated_content"] = "Generoitu sisältö."
            elif cap_lower == "summarize":
                base_fields["summary"] = "Tiivistelmä."
            elif cap_lower == "classify":
                base_fields["classification"] = "Luokittelu."
            elif cap_lower == "search":
                base_fields["results"] = "Hakutokokset."

        return base_fields

    def _recommend_agent_types(self, capabilities: list[str]) -> list[str]:
        """Suosittelee tunnetut agenttitapaukset kyvykkyyksien perusteella."""
        matches = []
        cap_set = set(c.lower() for c in capabilities)

        type_to_caps = {
            "researcher": {"analyze", "search", "summarize"},
            "developer": {"generate", "create", "write"},
            "qa": {"test", "validate", "check"},
            "security_review": {"analyze", "detect", "check"},
            "technical_writer": {"summarize", "generate", "document"},
            "pedagogy": {"teach", "explain", "design"},
            "compliance": {"validate", "check", "audit"},
        }

        for agent_type, required_caps in type_to_caps.items():
            overlap = cap_set & required_caps
            if len(overlap) >= 2:
                matches.append(agent_type)

        return matches if matches else []

    def _design_agent(self, input_data: AgentDesignInput) -> dict[str, Any]:
        """Suunnittelee uuden agentin speksin."""
        input_schema = input_data.input_fields if input_data.input_fields else self._suggest_input_schema(input_data.capabilities)
        output_schema = input_data.output_fields if input_data.output_fields else self._suggest_output_schema(input_data.capabilities)

        return {
            "name": input_data.agent_name or f"Custom{input_data.agent_type.capitalize() if input_data.agent_type else ''}Agent",
            "agent_type": input_data.agent_type or "custom",
            "description": input_data.agent_description or "Kustomoitu agentti.",
            "capabilities": input_data.capabilities,
            "input_schema": input_schema,
            "output_schema": output_schema,
            "required_tools": input_data.required_tools,
            "created_at": datetime.now().isoformat(),
        }

    def _run(self, input_data: AgentDesignInput) -> AgentDesignOutput:
        """AgentDesignAgentin päälogiikka."""
        action = input_data.action.lower()

        if action == "design":
            validation_issues = self._validate_agent_name(input_data.agent_name)
            # Validoi syötetietorakenne vain jos se on annettu
            if input_data.input_fields:
                validation_issues += self._validate_input_fields(input_data.input_fields)
            # Validoi tulostetietorakenne vain jos se on annettu
            if input_data.output_fields:
                validation_issues += self._validate_output_fields(input_data.output_fields)

            agent_spec = self._design_agent(input_data)
            input_suggestion = self._suggest_input_schema(input_data.capabilities)
            output_suggestion = self._suggest_output_schema(input_data.capabilities)
            recommendations = self._recommend_agent_types(input_data.capabilities)

            return AgentDesignOutput(
                success=len(validation_issues) == 0,
                result={"agent_spec": agent_spec, "issues_count": len(validation_issues)},
                message=f"Agent spec luotsattu. {len(validation_issues)} validointiongelt." if validation_issues
                        else f"Agent spec luotsattu onnistuneesti: {agent_spec['name']}.",
                agent_type=self.agent_type,
                agent_spec=agent_spec,
                validation_issues=validation_issues,
                recommended_agent_types=recommendations,
                input_schema_suggestion=input_suggestion,
                output_schema_suggestion=output_suggestion,
                tool_requirements=input_data.required_tools,
            )
        elif action == "analyze":
            issues = []
            code = input_data.existing_agent_code

            if code:
                if "agent_type" not in code:
                    issues.append("Agentissa ei ole 'agent_type'-attribivia.")
                if "_run" not in code:
                    issues.append("Agentissa ei ole '_run'-metodia.")
                if "input_schema" not in code:
                    issues.append("Agentissa ei ole 'input_schema'-attribivia.")
                if "output_schema" not in code:
                    issues.append("Agentissa ei ole 'output_schema'-attribivia.")
                if code.count("class ") > 2:
                    issues.append("Liian monta sisäkkäistä luokkaa.")

            return AgentDesignOutput(
                success=True,
                result={"issues_found": len(issues), "code_length": len(code)},
                message=f"Analysoitu {len(code)} merkkiä. Löydetty {len(issues)} ongelmaa." if issues
                        else "Agentin koodi näyttää tervettökivaltaisuudelta.",
                agent_type=self.agent_type,
                validation_issues=issues,
            )
        elif action == "validate":
            issues = (
                self._validate_agent_name(input_data.agent_name)
                + self._validate_input_fields(input_data.input_fields)
                + self._validate_output_fields(input_data.output_fields)
            )

            return AgentDesignOutput(
                success=len(issues) == 0,
                result={"valid": len(issues) == 0, "issues": len(issues)},
                message=f"Validointi valmis: {len(issues)} ongelmaa." if issues
                        else "Agent spec on validi.",
                agent_type=self.agent_type,
                validation_issues=issues,
            )
        elif action == "recommend":
            recommendations = self._recommend_agent_types(input_data.capabilities)

            return AgentDesignOutput(
                success=True,
                result={"recommended_types": recommendations},
                message=f"Ehdottytty {len(recommendations)} suositusta." if recommendations
                        else "Ei täydettäviä agenttitavoitteita.",
                agent_type=self.agent_type,
                recommended_agent_types=recommendations,
            )
        else:
            return AgentDesignOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'.",
                agent_type=self.agent_type,
                validation_issues=[f"Tuntematon toiminto: '{action}'"],
            )


class PromptOptimizerAgent(BaseAgent):
    """
    PromptOptimizerAgent optimoi ja analysoi prompteja.

    Se arvioi tokenimäärän, ehdottaa parannuksia ja optimoi promptin rakennetta.

    Usage:
        agent = PromptOptimizerAgent()
        result = agent.run("Optimoi tämä prompt", action="optimize", prompt="Kerro mina kaikista...")
    """

    agent_type: ClassVar[str] = "prompt_optimizer"
    input_schema = PromptOptimizerInput
    output_schema = PromptOptimizerOutput

    def _estimate_tokens(self, text: str) -> int:
        """Arvioi tokenimäärää tekstistä (noin 4 merkkiä per token)."""
        return max(1, len(text) // 4)

    def _analyze_prompt_structure(self, prompt: str) -> dict[str, Any]:
        """Analysoi promptin rakenteen."""
        lines = prompt.strip().splitlines()
        words = prompt.split()

        # Etsi rakenteet
        has_list = any(line.strip().startswith(("-", "*", "1.", "2.")) for line in lines)
        has_code_block = "```" in prompt
        has_examples = "esimerki" in prompt.lower() or "esim." in prompt.lower()
        has_constraints = " älä " in prompt.lower() or "välttämättä" in prompt.lower() or "käytä vain" in prompt.lower()

        # Laske osa-alueet
        sections = sum(1 for line in lines if line.strip().startswith(("#", "##", "**", "Toiminto", "Ohje", "Ehto")))

        return {
            "lines": len(lines),
            "words": len(words),
            "chars": len(prompt),
            "has_lists": has_list,
            "has_code_blocks": has_code_block,
            "has_examples": has_examples,
            "has_constraints": has_constraints,
            "sections": sections,
            "avg_line_length": round(len(prompt) / max(len(lines), 1), 1),
        }

    def _optimize_prompt(self, prompt: str, target_limit: int) -> str:
        """Optimoi promptin tiiviydellä."""
        # Poista ylimääräiset tyhjät rivit
        lines = [line for line in prompt.splitlines()]
        optimized_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped:
                # Vältä turhia tyhjiä rivejä
                if stripped in optimized_lines and stripped == "":
                    continue
                optimized_lines.append(stripped if line.strip() else "")

        optimized = "\n".join(optimized_lines)
        # Poista päätteet ja alussat
        optimized = "\n".join(line for line in optimized.splitlines() if line.strip())
        optimized = optimized.strip()

        # Lisää rakennetta jos puuttuu
        if not any(line.startswith(("#", "**")) for line in optimized.splitlines()):
            optimized = f"## Tehtävä\n\n{optimized}"

        token_count = self._estimate_tokens(optimized)
        if token_count > target_limit:
            # Lyhennä tiivistämällä
            ratio = target_limit / max(token_count, 1)
            optimized = optimized[:int(len(optimized) * ratio)]

        return optimized

    def _generate_suggestions(self, prompt: str, structure: dict[str, Any]) -> list[str]:
        """Luo parannusehdotuksia promptille."""
        suggestions = []

        if structure["words"] > 200:
            suggestions.append("Lyhennä promptia — yli 200 sanaa voi olla turhaa yksityiskohtaa.")

        if not structure["has_lists"]:
            if ";" in prompt or "," in prompt:
                suggestions.append("Käytä listamuotoa helpottaaksesi lukijaa.")

        if not structure["has_examples"]:
            suggestions.append("Lisää esimerkkejä parantaaksesi ymmärrystä.")

        if not structure["has_constraints"]:
            suggestions.append("Määritä selkeät rajoitteet (esim. 'Älä käytä ...').")

        if structure["avg_line_length"] > 80:
            suggestions.append("Pitäkää rivit lyhyimpinä — pidemät rivit vaikeuttavat lukua.")

        if "???" in prompt or "..." in prompt:
            suggestions.append("Vältä epäselvää merkintää (??? tai ...).")

        if not suggestions:
            suggestions.append("Prompt on jo melko hyvä. Harkitse vielä esimerkkien lisäämistä.")

        return suggestions

    def _calculate_optimization_score(self, original: str, optimized: str, suggestions: list[str]) -> float:
        """Laskee optimointipistemäärän."""
        score = 50.0

        # Pituusparannus
        if len(optimized) < len(original):
            score += 20

        # Rakenteellinen parannus
        opt_structure = self._analyze_prompt_structure(optimized)
        if opt_structure["has_lists"]:
            score += 10
        if opt_structure["has_examples"]:
            score += 10
        if opt_structure["has_constraints"]:
            score += 5
        if len(suggestions) == 0:
            score += 5

        return min(100.0, round(score, 1))

    def _run(self, input_data: PromptOptimizerInput) -> PromptOptimizerOutput:
        """PromptOptimizerAgentin päälogiika."""
        action = input_data.action.lower()
        prompt = input_data.prompt

        if not prompt:
            return PromptOptimizerOutput(
                success=False,
                result=None,
                message="Promptia ei annettu.",
                agent_type=self.agent_type,
                optimization_score=0,
            )

        original_tokens = self._estimate_tokens(prompt)
        structure = self._analyze_prompt_structure(prompt)

        if action == "optimize":
            optimized = self._optimize_prompt(prompt, input_data.target_token_limit)
            optimized_tokens = self._estimate_tokens(optimized)
            suggestions = self._generate_suggestions(prompt, structure)
            score = self._calculate_optimization_score(prompt, optimized, suggestions)

            return PromptOptimizerOutput(
                success=True,
                result={"original_tokens": original_tokens, "optimized_tokens": optimized_tokens},
                message=f"Prompt optimoitu ({original_tokens} -> {optimized_tokens} tokenia).",
                agent_type=self.agent_type,
                optimized_prompt=optimized,
                original_token_estimate=original_tokens,
                optimized_token_estimate=optimized_tokens,
                tokens_saved=original_tokens - optimized_tokens,
                suggestions=suggestions,
                prompt_length=len(optimized),
                optimization_score=score,
            )
        elif action == "analyze":
            suggestions = self._generate_suggestions(prompt, structure)

            return PromptOptimizerOutput(
                success=True,
                result={"structure": structure, "tokens": original_tokens},
                message=f"Prompt analysoitu. {len(suggestions)} parannusehdotusta.",
                agent_type=self.agent_type,
                original_token_estimate=original_tokens,
                optimized_token_estimate=original_tokens,
                tokens_saved=0,
                suggestions=suggestions,
                prompt_length=len(prompt),
                optimization_score=round(50.0 + len([s for s in suggestions if "lisää" in s.lower()]) * 5, 1),
            )
        elif action == "estimate":
            return PromptOptimizerOutput(
                success=True,
                result={"tokens": original_tokens, "chars": len(prompt), "words": len(prompt.split())},
                message=f"Tokeniarvio: {original_tokens} (noin 4 merkkiä per token).",
                agent_type=self.agent_type,
                original_token_estimate=original_tokens,
                optimized_token_estimate=original_tokens,
                tokens_saved=0,
                suggestions=[],
                prompt_length=len(prompt),
                optimization_score=50.0,
            )
        elif action == "suggest":
            suggestions = self._generate_suggestions(prompt, structure)

            return PromptOptimizerOutput(
                success=True,
                result={"suggestion_count": len(suggestions)},
                message=f"Luotsattu {len(suggestions)} parannusehdotusta.",
                agent_type=self.agent_type,
                original_token_estimate=original_tokens,
                optimized_token_estimate=original_tokens,
                tokens_saved=0,
                suggestions=suggestions,
                prompt_length=len(prompt),
                optimization_score=50.0,
            )
        else:
            return PromptOptimizerOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'.",
                agent_type=self.agent_type,
                optimization_score=0,
            )


class AgentFactoryAgent(BaseAgent):
    """
    AgentFactoryAgent luo agentteja instansseja dynaamisesti.

    Se rekisteroi, luo ja instantiate-agentit konfiguraatiosta.

    Usage:
        agent = AgentFactoryAgent()
        result = agent.run("Luo uusi researcher-agentti", action="create", agent_type="researcher", agent_name="ResearcherAgent")
    """

    agent_type: ClassVar[str] = "agent_factory"
    input_schema = AgentFactoryInput
    output_schema = AgentFactoryOutput

    # Rekisteröityjen agenttien kirjasto (tyyppi -> moduuli)
    AGENT_REGISTRY: ClassVar[dict[str, str]] = {
        "director": "agents.director",
        "project_manager": "agents.project_manager",
        "researcher": "agents.researcher_agent",
        "developer": "agents.developer",
        "test_designer": "agents.testing_agent",
        "security_review": "agents.security_agent",
        "technical_writer": "agents.documentation_agent",
        "docker": "agents.devops_agent",
        "mentor": "agents.pedagogy_agent",
        "knowledge": "agents.knowledge_agent",
        "upgrade": "agents.maintenance_agent",
        "cleanup": "agents.maintenance_agent",
        "dependency": "agents.maintenance_agent",
        "release_manager": "agents.release_agent",
        "changelog": "agents.release_agent",
        "compliance": "agents.release_agent",
        "agent_design": "agents.agent_engineering_agent",
        "prompt_optimizer": "agents.agent_engineering_agent",
        "agent_factory": "agents.agent_engineering_agent",
    }

    def _resolve_agent_class(self, agent_type: str) -> Optional[str]:
        """Etsii agentin luokan tyypin perusteella."""
        module_path = self.AGENT_REGISTRY.get(agent_type)
        return module_path

    def _generate_agent_code(self, spec: dict[str, Any]) -> str:
        """Generoi agentin koodin speksistä."""
        name = spec.get("name", "CustomAgent")
        agent_type = spec.get("agent_type", "custom")
        description = spec.get("description", "...")
        input_fields = spec.get("input_schema", {})
        output_fields = spec.get("output_schema", {})

        # Muodosta Input/Output mallit
        input_lines = [f"    task: str = Field(..., description=\"Käsiteltävä tehtävä.\")"]
        for field_name, field_def in input_fields.items():
            if field_name == "task":
                continue
            if isinstance(field_def, dict):
                desc = field_def.get("description", f"{field_name}-kenttä.")
                field_type = field_def.get("type", "str")
            else:
                desc = str(field_def)
                field_type = "str"
            input_lines.append(f"    {field_name}: str = Field(default=\"\", description=\"{desc}\")")

        output_lines = [f"    success: bool = Field(..., description=\"Onnistuiko toiminto.\")"]
        for field_name, field_def in output_fields.items():
            if field_name in ("success", "message", "agent_type"):
                continue
            if isinstance(field_def, dict):
                desc = field_def.get("description", f"{field_name}-kenttä.")
            else:
                desc = str(field_def)
            output_lines.append(f"    {field_name}: Any = Field(default=None, description=\"{desc}\")")

        input_model = "\n".join(input_lines)
        output_model = "\n".join(output_lines)

        code = f'''"""
{name}-moduuli — generoitu agentti.

Description: {description}
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


class {name}Input(AgentInput):
    """Syöte."""
{input_model}


class {name}Output(AgentOutput):
    """Tuloste."""
{output_model}


class {name}(BaseAgent):
    """{description}"""

    agent_type: str = "{agent_type}"
    input_schema = {name}Output
    output_schema = {name}Output

    def _run(self, input_data: {name}Input) -> {name}Output:
        """Agentin päälogiikka."""
        return {name}Output(
            success=True,
            result=None,
            message="Agentti luotsattu.",
            agent_type=self.agent_type,
        )
'''
        return code

    def _create_agent(self, input_data: AgentFactoryInput) -> dict[str, Any]:
        """Luo agentin speksistä."""
        agent_type = input_data.agent_type or input_data.agent_name.lower().replace("agent", "")
        agent_name = input_data.agent_name or f"Custom{agent_type.capitalize()}Agent"

        config = input_data.config or {
            "agent_type": agent_type,
            "agent_name": agent_name,
            "module": input_data.module_path or f"agents.{agent_type}_agent",
        }

        return {
            "name": agent_name,
            "agent_type": agent_type,
            "module": config.get("module"),
            "config": config,
            "registry_entry": f'"{agent_type}": "agents.{agent_type}_agent"',
            "created_at": datetime.now().isoformat(),
        }

    def _run(self, input_data: AgentFactoryInput) -> AgentFactoryOutput:
        """AgentFactoryAgentin päälogiika."""
        action = input_data.action.lower()

        # Yhdistä rekisteriöityjät
        registry = input_data.registered_agents or dict(self.AGENT_REGISTRY)

        if action == "create":
            agent_instance = self._create_agent(input_data)
            module_path = agent_instance.get("module", "")

            # Tarkista onko tyyppi rekisteröity
            is_registered = input_data.agent_type in registry

            return AgentFactoryOutput(
                success=True,
                result={"created": True, "agent_type": agent_instance["agent_type"]},
                message=f"Agentti luotsattu: {agent_instance['name']} (tyyppi: {agent_instance['agent_type']}, moduli: {module_path}).",
                agent_type=self.agent_type,
                agent_instance=agent_instance,
                registered_agents=registry,
                success_message=f"Agentti '{agent_instance['name']}' on rejoistutettu.",
            )
        elif action == "register":
            if input_data.agent_type and input_data.module_path:
                registry[input_data.agent_type] = input_data.module_path
                return AgentFactoryOutput(
                    success=True,
                    result={"registered": True, "agent_type": input_data.agent_type},
                    message=f"Agentti tyyppi '{input_data.agent_type}' rekisteröitu moduliin '{input_data.module_path}'.",
                    agent_type=self.agent_type,
                    registered_agents=registry,
                    success_message=f"Agentti '{input_data.agent_type}' rekisteröitu.",
                )
            return AgentFactoryOutput(
                success=False,
                result=None,
                message="agent_type ja module_path vaaditaan rekisteröintiin.",
                agent_type=self.agent_type,
                registered_agents=registry,
            )
        elif action == "list":
            return AgentFactoryOutput(
                success=True,
                result={"agent_count": len(registry), "agents": registry},
                message=f"{len(registry)} rekisteröityä agenttia.",
                agent_type=self.agent_type,
                registered_agents=registry,
                success_message="Luettelo haettu.",
            )
        elif action == "instantiate":
            module_path = self._resolve_agent_class(input_data.agent_type)
            if module_path:
                return AgentFactoryOutput(
                    success=True,
                    result={"instantiated": True, "module": module_path},
                    message=f"Agentti '{input_data.agent_type}' voidaan instanssia moduulista {module_path}.",
                    agent_type=self.agent_type,
                    agent_instance={"agent_type": input_data.agent_type, "module": module_path},
                    registered_agents=registry,
                    success_message=f"Agentti '{input_data.agent_type}' valmiina instantsointia varten.",
                )
            return AgentFactoryOutput(
                success=False,
                result=None,
                message=f"Agenttityyppiä '{input_data.agent_type}' ei löydy rekisteristä.",
                agent_type=self.agent_type,
                registered_agents=registry,
            )
        else:
            return AgentFactoryOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'.",
                agent_type=self.agent_type,
                registered_agents=registry,
            )
