# AgentFactoryAgent (M16 Agent Engineering)

**Tiedosto:** `agents/agent_engineering_agent.py`  
**Moduuli:** M16 — Agent Engineering  
**Status:** ✅ Valmiina  
**Testit:** 61 | **Kattavuus:** 85 %

---

## Tarkoitus

Dynaamisten agenttien luomista ClassVar `AGENT_REGISTRY`-kirjastosta. Tukee agenttien rekisteröintiä, listailua, instanssintamista.

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"agent_factory"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `create` | Luo agenttiinstanssi nimetyillä parametreillä |
| `register` | Rekisteroi uuden agentin |
| `list` | Lista kaikista rekisteroiduista agenteista |
| `instantiate` | Synkroninen instanssintaminen |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["create", "register", "list", "instantiate"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Agenttityyppi tai kysymys |
| `agent_name` | `str` | ❌ | Agentin nimi (create/register) |
| `agent_class` | `str` | ❌ | Luokan polku (register) |
| `config` | `dict[str, Any]` | ❌ | Konfiguuraatio (create/instantiate) |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `agent` | `dict[str, Any]` | Luodun agentin tiedot |
| `agents` | `list[dict[str, Any]]` | Lista rekisteroiduista (list) |
| `instance` | `object` | Agenttiinstanssi (instantiate) |
| `message` | `str` | Tilanneilmoitus |

---

## KNOWN_AGENT_TYPES

| Tyyppi | Selitys |
|---|---|
| `director` | Hankeohjaaja |
| `developer` | Koodin generaati |
| `tester` | Testit |
| `researcher` | Tutkija |
| `security_review` | Turvallisuustarkastus |
| `documentation` | Dokumentaatio |
| `orchestrator` | Orkesterointi |

---

## Esimerkkikoodi

```python
from agents import AgentFactoryAgent

factory = AgentFactoryAgent()

# Lista rekisteroiduista agenteista
result = factory.run(
    action="list",
    query="*"
)

print(f"Agenttia: {len(result.agents)}")
# Output: Agenttia: 45

for agent in result.agents:
    print(f"  {agent['name']} ({agent['type']})")

# Luo agenttiinstanssi
result = factory.run(
    action="create",
    query="Luovatko minulle agentti joka tekee koodikatsauksia?",
    agent_name="CustomReviewer",
    config={"max_files": 10, "severity_threshold": "high"}
)

print(result.agent)
# Output: {"name": "CustomReviewer", "type": "code_review", "config": {"max_files": 10}}
```

---

## Rekisteröinti

Uusia agentit voidaan rekisteröidä:

```python
result = factory.run(
    action="register",
    query="Uusi analyysitehdas",
    agent_name="LogAnalyzer",
    agent_class="log_analyzer.agents.LogAnalyzerAgent"
)

print(result.message)
# Output: Agentti 'LogAnalyzer' rekisteröity onnistuneesti
```

---

## Testikattavuus

M16-testit (61) sisältävät:
- `test_list_all_agents`
- `test_create_agent_with_config`
- `test_register_new_agent`
- `test_instantiate_returns_instance`
