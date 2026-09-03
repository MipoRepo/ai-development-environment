---
name: agent-engineering-m16
description: M16 Agent Engineering -agentit ja niiden käyttö
type: project
---

# M16 Agent Engineering — Agent Design, Prompt Optimization, Factory (Alpha 2.6)

## Agentit

- **AgentDesignAgent** (`agents/agent_engineering_agent.py`): suunnittelee ja validoi uusia agenteja
  - Toiminnot: `design`, `analyze`, `validate`, `recommend`
  - Syöte: `AgentDesignInput` (action, agent_name, agent_description, agent_type, capabilities, input_fields, output_fields, required_tools, existing_agent_code)
  - Tuloste: `AgentDesignOutput` (agent_spec, validation_issues, recommended_agent_types, input_schema_suggestion, output_schema_suggestion, tool_requirements)

- **PromptOptimizerAgent** (`agents/agent_engineering_agent.py`): optimoi ja analysoi prompteja
  - Toiminnot: `optimize`, `analyze`, `estimate`, `suggest`
  - Syöte: `PromptOptimizerInput` (action, prompt, context_variables, target_token_limit, temperature, model)
  - Tuloste: `PromptOptimizerOutput` (optimized_prompt, original/optimized_token_estimate, tokens_saved, suggestions, prompt_length, optimization_score)

- **AgentFactoryAgent** (`agents/agent_engineering_agent.py`): luo agentteja instansseja dynaamisesti
  - Toiminnot: `create`, `register`, `list`, `instantiate`
  - Syöte: `AgentFactoryInput` (action, agent_type, agent_name, module_path, config, registered_agents)
  - Tuloste: `AgentFactoryOutput` (agent_instance, registered_agents, success_message)
  - Luokkanäkymä: `AGENT_REGISTRY` (tyyppi → moduuli) rekisteröityille agenteille

## Vakiot

- `AGENT_DESIGN_ACTIONS`: design, analyze, validate, recommend
- `PROMPT_OPTIMIZE_ACTIONS`: optimize, analyze, estimate, suggest
- `AGENT_FACTORY_ACTIONS`: create, register, list, instantiate
- `KNOWN_AGENT_TYPES`: lista kaikista tunetuista agenttityypeistä
- `SCHEMA_FIELDS`: perus-kentät syöte- ja tulosteskeemoille
- `PROMPT_OPTIMIZATION_TIPS`: optimointivinkit

## Testaus

- 61 testiä: `tests/test_agent_engineering_agent.py`
- 85 % kattavuus
- 776 testiä kaikkiaan (kaikki läpäisti)

## Miksi:

M16 tarjoaa työkalut agenttien itsekehittämiseen — agenttien suunnittelu, prompttien optimointi ja agenttitehtaan, jotka kaikki muut moduulit voivat käyttää agenttien laajentamiseen.

## Kuinka sovellettavaksi:

```python
from agents import AgentDesignAgent, PromptOptimizerAgent, AgentFactoryAgent

# Suunnittele uusi agentti
designer = AgentDesignAgent()
spec = designer.run("Suunnittele data-analyysi agentti",
                    agent_name="AnalyzerAgent",
                    capabilities=["analyze", "report"])

# Optimoi prompt
opt = PromptOptimizerAgent()
result = opt.run("Optimoi tämä prompt", prompt="Kerro minä kaikista...", target_token_limit=4096)

# Luo agentti instanssi
factory = AgentFactoryAgent()
agent = factory.run("Luo researcher", action="instantiate", agent_type="researcher")
```
