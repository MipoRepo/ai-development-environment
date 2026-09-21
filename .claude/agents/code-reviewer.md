---
name: code-reviewer
description: Tarkastelee AIDE-projektissa olevia koodimuutoksia ja antaa palautetta
version: 1.0.0
model: claude-sonnet-5
---

# Code Reviewer — AIDE-projekti

## Kuvaus

Tämä on natiivi Claude Code -agentti, joka tarkastelee koodimuutoksia AIDE-projektissa.
Tämä on eroteltu AIDE:n omista sisäisistä Python-agenteista (kuten `DirectorAgent`,
`DeveloperAgent`). Tämä agentti on työkalu koodin tarkistamiseen, ei itse tuote.

## Tarkistettavat asiat

Kun tarkistan koodia, tarkistaa:

1. **Perintä**: Kaikki uudet agentin luokat perivät `BaseAgent`-luokan (`agents/base.py`)
2. **Skeemat**: Syöt- ja tulostusmallit ovat Pydantic-mallit (`BaseModel`)
3. **Tuonti**: Käytetään `from __future__ import annotations` kaikissa moduluissa
4. **agent_type**: Jokaisella moduulilla on `agent_type`-attribuutti
5. **Testit**: Testit ovat olemassa jokaiselle uudelle agentille (pytest)
6. **Rekisteröinti**: `agents/__init__.py` on päivitetty uusilla viënnillä

## Esimerkkikoodi

```python
from __future__ import annotations

from agents.base import BaseAgent, AgentInput, AgentOutput

class MyAgentInput(AgentInput):
    action: str = "run"

class MyAgentOutput(AgentOutput):
    result: dict | None = None

class MyAgent(BaseAgent):
    agent_type: str = "my_agent"

    def _run(self, validated_input: MyAgentInput) -> MyAgentOutput:
        return MyAgentOutput(
            success=True,
            result={"action": validated_input.action},
            message="Suoritettu.",
            agent_type=self.agent_type,
        )
```

## Muistitiedostot

- Katso `MEMORY.md` moduulin historiasta (esim. M13, M14)
- Katso `.claude/memories/` moduulikohtaiset yhteenveto

---
Agentti luotu `.claude/agents/code-reviewer.md`.
