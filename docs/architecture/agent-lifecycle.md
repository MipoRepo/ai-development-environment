# AIDE — Agentin elinkaari

**Generoitu:** 2026-09-03 | **Versio:** Alpha 2.10

---

## Agentin elinkaari vaiheittain

```
luomus Agent()
  │
  ▼
run(action, query, **kwargs)
  │
  ├─ 1. Syötteen validointi (Pydantic: input_schema → AgentInput)
  │
  ├─ 2. Kutsu _run() — todella logiikka
  │      │
  │      ├─ a. AI-mallin kutsu (OpenRouter / paikallinen LLM)
  │      ├─ b. Knowledge/Memory -pyyntö (M13)
  │      ├─ c. MCP-työkalukutsut (M19)
  │      ├─ d. API-integraatiot (M19)
  │      ├─ e. Tilastot/logging (BaseAgent.run)
  │      │
  │      ▼
  │     Tulostus (AgentOutput)
  │
  ├─ 3. Tulcheen validointi (Pydantic: output_schema → AgentOutput)
  │
  ├─ 4. Paluu AgentOutput
  │      │
  │      ├─ JSON-muutettu tuloste (Pydantic .model_dump())
  │      ├─ Success / Failure -merkintä
  │      ├─ Metadata (agent_type, input_id, timestamps)
  │      └─ Konteksti seuraavalle vaiheelle
  │
  ▼
paluu kutsujalle (esim. DirectorAgent, WorkflowOrchestrator, CLI)
```

---

## 1. Luominen (`__init__`)

```python
agent = ControlCenterAgent()
# tai
agent = DeveloperAgent(model="meta-llama-3", temperature=0.3)
```

- **`agent_type`**: luokkamuuttuja (esim. `"developer"`)
- **`input_schema`**: Pydantic-malli syötteelle
- **`output_schema`**: Pydantic-malli tulosteelle

---

## 2. Syötteen validointi (`run` → input_schema)

```python
input_data = self.input_schema(action="refactor", query="...", context_data=...)
```

- Kaikki syötteet validoidaan Pydanticilla.
- Pakollista kenttä: `action`, `query`.
- Valinnainen: `context_data`, `metadata`, agenttikohtaiset parametrit.

---

## 3. Kirjekuori (Logging & Error Handling)

```python
try:
    result = self._run(input_data)
except Exception as e:
    return AgentOutput(success=False, error=str(e), ...)
else:
    return result
```

- Kaikki poikkeukset sallitaan ja palautetaan `success=False`.
- Virhe- ja metatiedot lisätään `AgentOutput`-olioon.

---

## 4. Todennut kääntäminen (`_run`)

Tämä on agentin itse logiikka — ylikirjoitettu jokaisessa aliluokassa.

### Esimerkki: DirectorAgent._run()

```python
def _run(self, input_data: DirectorInput) -> DirectorOutput:
    # 1. Analysoi kysymys
    tasks = self._decompose(input_data.query)
    
    # 2. Kohdista tehtävät
    assignments = self._assign(tasks)
    
    # 3. Paluu tulos
    return DirectorOutput(
        success=True,
        tasks=tasks,
        assignments=assignments
    )
```

---

## 5. Tuloutuksen validointi (`output_schema`)

```python
output = self.output_schema(**kwargs)
# automaattinen validointi Pydanticilla
# invalid → raise ValidationError → caught → success=False
```

Tulosteen täytyy mä passata `output_schema`-validoinnin (Pydantic).

---

## 6. Paluu ja konteksti

AgentOutput sisältää:

| Kenttä | Kuvaus |
|---|---|
| `success` | Totuusarvo, onnistuuko operaatio |
| `error` | Virheviesti (jos `success=False`) |
| `data` | Varsinainen data (dict tai list) |
| `metadata` | Tämäm, agent_type, input_id |
| `timestamp` | UTC-aikamerkintä |
| `execution_time` | Suorituksen kesto (ms) |

Konteksti kulkee seuraavalle agentille `context_data`-parametrissa.

---

## State Management

Joissakin agenteissa on sisäistä tilaa (esim. CLIOrchestratorin komentohistoria):

```python
class CLIOrchestrator(BaseAgent):
    def __init__(self):
        super().__init__()
        self._history: list[str] = []  # ei persistoida
```

- Tilaa ei tallenneta kovottuun tilaan (ei pickles).
- Stateful agentit luo- tai konfiguroidaan uudelleen jokaisella ajokerralla.

---

## Workflow-orchestration (M9)

```
WorkflowOrchestratorAgent
  │
  ├─ Lukee YAML-workflowin
  ├─ Ajaa jokaisen vaiheen agenttinä
  ├─ Päivittää yhteistä kontekstia
  ├─ Stop-on-error (keskeytetään virheen sattuessa)
  └─ Palauttaa lopullisen AgentOutput
```

---

## Control Center - integraatio (M20)

```
ControlCenterAgent
  │
  ├─ Seuraa agenttien satus
  ├─ Listaa workflow-tilat
  ├─ Health-check jokaiselle komponentille
  └─ Reitittää komennot CLIOrchestratorin kautta
```

---

## Esimerkki: Agentin käyttö koodissa

```python
from agents.developer import DeveloperAgent, DeveloperInput

agent = DeveloperAgent()
result = agent.run(
    action="refactor",
    query="Poista käytämättomat importit tiedostosta main.py",
    file_path="src/main.py"
)

if result.success:
    print(result.explanation)
    print(result.changes)
else:
    print(f"Virhe: {result.error}")
```

Tämä elinkaari koskee **kaikkia** agentteja yhdellä rajapinnalla (BaseAgent) ja varmistaa yhtenenmukaisen käyttäytymisen — vaikka eri moduulit tekevät erita-asioita.
