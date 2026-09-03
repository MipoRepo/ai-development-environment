# AgentDesignAgent (M16 Agent Engineering)

**Tiedosto:** `agents/agent_engineering_agent.py`  
**Moduuli:** M16 — Agent Engineering  
**Status:** ✅ Valmiina  
**Testit:** 61 | **Kattavuus:** 85 %

---

## Tarkoitus

Suunnitella ja validoi uusia agenteja. Määrittää `agent_name`, `agent_type`, `capabilities`, syöte- ja tulostemuodot.

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"agent_design"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `design` | Luo uusi agentti määrittelyistä perustuen |
| `analyze` | Analysoi olemassa olevan agentin rakenteen |
| `validate` | Validoi agentin määritystä |
| `recommend` | Suosittelee parannuksia tai uusia agentteja |

---

## Syöte (AgentDesignInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["design", "analyze", "validate", "recommend"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Kuvaus tai kysymys |
| `agent_type` | `str` | ❌ | Esimerkki: `"my_custom_agent"` |
| `capabilities` | `list[str]` | ❌ | Toiminnot (esim. `["code_generation", "analysis"]`) |
| `constraints` | `list[str]` | ❌ | Rajoitteet (esim. `["no_network"]`) |

---

## Tuloste (AgentDesignOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `design` | `dict[str, Any]` | Luonnin rakenne |
| `code` | `str` | Generoitu Python-luokka |
| `schema` | `dict[str, Any]` | Syöte/tuloste-skeemat |
| `recommendations` | `list[str]` | Suosituksia |
| `confidence` | `float` | Luotettavuus (0.0–1.0) |

---

## Esimerkkikoodi

```python
from agents import AgentDesignAgent

designer = AgentDesignAgent()
result = designer.run(
    action="design",
    query="Agenti, joka automatisoi tiedostojen järjestämisen projekteissa",
    agent_type="file_organizer",
    capabilities=["scan", "sort", "rename", "report"]
)

print(f"Luottamus: {result.confidence}")
# Output: Luottamus: 0.91

print(result.schema)
# Output: {"input_schema": {...}, "output_schema": {...}}

print("Generoitu koodi:")
print(result.code[:200])
# Output: class FileOrganizerAgent(BaseAgent):\n    agent_type = ...
```

---

## AGENT_DESIGN_ACTIONS

| Toiminto | Selitys |
|---|---|
| `design` | Luo uusi agentti skeeman perusteelta |
| `analyze` | Analysoi olemassa olevan agentin vaatimuksia |
| `validate` | Tarkista onko kaikki kentät oikeassa muodossa |
| `recommend` | Ehdota lisätoimintoja tai muutoksia |

---

## Testikattavuus

M16-testit (61) sisältävät:
- `test_design_creates_valid_agent`
- `test_analyze_returns_schema`
- `test_validate_rejects_missing_fields`
- `test_recommend_suggests_capability`
