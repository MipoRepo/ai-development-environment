# MultiAgentCoordinator (M9 Orchestration)

**Tiedosto:** `agents/orchestration_agent.py`  
**Moduuli:** M9 — Orchestration  
**Status:** ✅ Valmiina  
**Testit:** 30 | **Kattavuus:** 92 %

---

## Tarkoitus

Moniagentti-koordinaatio topologisen järjestyksen mukaisesti riippuvuuksien perusteella. Käyttää **Kahnin algoritmia** projektien ja agenttien välisten riippuvuuksien ajaminiseen oikeassa järjestyksessä.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"multiagent_coordinator"` |
| `input_schema` | `CoordinationInput` |
| `output_schema` | `CoordinationOutput` |

---

## Syöte (CoordinationInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["coordinate", "analyze", "optimize"]` | ✅ | Toiminto |
| `agents` | `list[dict[str, Any]]` | ✅ | Koordinoitavat agentit + niiden riippuvuudet |
| `context` | `dict[str, Any]` | ❌ | Yhteinen konteksti agenttien välisessä tiedonvaihdossa |
| `max_parallel` | `int` | ❌ | Samanaikaisten agenttien enimmäismäärä (oletus: 3) |

### Agentin määrittely

Jokainen agentti määritellään sanakirjana:

```python
{
    "agent_type": "researcher",
    "dependencies": ["project_manager"],  # aina suoritettu ennen kuin tämä voidaan käynnittää
    "params": {"query": "analysoi rakenteet"},
}
```

---

## Tuloste (CoordinationOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Kaikki agentit suoritettu onnistuneesti |
| `execution_order` | `list[str]` | Agenttien sija järjestyksessä |
| `results` | `dict[str, dict[str, Any]]` | agent_type → AgentOutput |
| `total_agents` | `int` | Koordinoitujen agenttien määrä |
| `parallel_groups` | `list[list[str]]` | Ryhmitellyt agentit, jotka voitaisiin ajaa rinnakkain |
| `error` | `str \| None` | Virheviesti |

---

## Kahnin algoritmi — miten se toteutuu

```
1. Laske jokaisen agentin "syntymä" luku (montako toinen riippuu siitä)
2. Lisää kaikki 0-syntyneet (ei riippuvuuksia) ajon jonoon
3. Poista kyseinen agentti ja vähennä sen riippuvuuksista lukua
4. Toista kunnes kaikki on prosessoitu tai jää kiertomerkkien (syke)
5. Jos jääkiertoja → virhe (kiikkuminen)
```

---

## Esimerkkikoodi

### Koordinaatio kolmeen agenttiin

```python
from agents import MultiAgentCoordinator

coordinator = MultiAgentCoordinator()
result = coordinator.run(
    action="coordinate",
    agents=[
        {"agent_type": "project_manager", "dependencies": [], "params": {"query": "Luo projekti"}},
        {"agent_type": "researcher", "dependencies": ["project_manager"], "params": {"query": "Analyysi"}},
        {"agent_type": "developer", "dependencies": ["researcher"], "params": {"query": "Koodin generointi"}},
    ],
    max_parallel=2
)

print(result.execution_order)
# Output: ['project_manager', 'researcher', 'developer']

print(result.parallel_groups)
# Output: [['project_manager'], ['researcher'], ['developer']]

for agent, output in result.results.items():
    print(f"{agent}: success={output.success}")
```

### Riippuvuuksien optimointi

```python
result = coordinator.run(
    action="optimize",
    agents=[
        {"agent_type": "researcher", "dependencies": []},
        {"agent_type": "developer", "dependencies": ["researcher"]},
        {"agent_type": "security_review", "dependencies": ["researcher"]},
        {"agent_type": "tester", "dependencies": ["developer", "security_review"]},
    ],
    max_parallel=3
)

print(result.parallel_groups)
# Output: [['researcher'], ['developer', 'security_review'], ['tester']]
# developer ja security_review voivat ajaa rinnakkain — riippumattomia toisistaan
```

---

## Testikattavuus

```
tests/test_orchestration_agent.py — osuus M9 -testeistä
Kattavuus: 92 %
```

Tärkeimmät testit:
- `test_coordinate_runs_agents_in_order`
- `test_coordinate_handles_dependencies`
- `test_kahns_algorithm_detects_cycle`
- `test_optimize_groups_parallel_agents`
- `test_max_parallel_limits_concurrency`

---

## Liittyvät moduulit

- **Riippuu:** kaikki M1–M20 agentit — ne ovat koordinoitavia "työntekijöitä)"
- **Seuraa:** WorkflowOrchestratorAgent (M9) — YAML-workflowjen orkesterointi
- **Käytetään:** ControlCenterAgent (M20) — tilan valvonta

## CLI-käyttö

```bash
aide orchestrate --agents director,developer,testing  # → MultiAgentCoordinator.coordinate
```

## Katso myös

- [`workflow_orchestrator.md`](workflow_orchestrator.md) — YAML-workflowjen orkesterointi
- [`modules.md`](../../architecture/modules.md) — kaikki moduulit
- [`dataflow.md`](../../architecture/dataflow.md) — agenttien välinen data
