# WorkflowOrchestratorAgent (M9 Orchestration)

**Tiedosto:** `agents/orchestration_agent.py`  
**Moduuli:** M9 — Orchestration  
**Status:** ✅ Valmiina  
**Testit:** 30 (osasta myös M9-testit yms.) | **Kattavuus:** 91 %

---

## Tarkoitus

YAML-pohjaisten workflowjen suoritus agenttien välillä. Tukee vaiheiden ajoittamista (phases), kontekstin päivitystä, stop_on_error-asetusta ja max_phases-rajaa. WorkflowOrchestrator on keskeinen orkesterointiagentti, joka lukee YAML-workflowt ja ajaa ne agenttien läpi.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"workflow_orchestrator"` |
| `input_schema` | `WorkflowOrchestratorInput` |
| `output_schema` | `WorkflowOrchestratorOutput` |

---

## Syöte (WorkflowOrchestratorInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["execute", "validate"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Workflow-tiedoston polku (YAML) tai workflow-nimi |
| `params` | `dict[str, Any]` | ❌ | Parametrit, jotka annetaan workflowille |
| `stop_on_error` | `bool` | ❌ | Pysähdetäänkö virheen sattuessa (oletus: `True`) |
| `max_phases` | `int` | ❌ | Maksimivaikutelmafaseja (oletus: kaikki) |

---

## Tuloste (WorkflowOrchestratorOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Workflow suoritettu onnistuneesti |
| `workflow_name` | `str` | Suoritettu workflowin nimi |
| `phases_executed` | `int` | Montako vaihetta suoritettu |
| `results` | `list[dict[str, Any]]` | Kunkin vaiheen tulos |
| `final_agent` | `str` | Viimeisenä toimineen agentin tyyppi |
| `final_output` | `dict[str, Any]` | Lopullinen tuloste |
| `error` | `str \| None` | Virheviesti (jos `success=False`) |

---

## Esimerkkikoodi

### Workflowin suoritus

```python
from agents import WorkflowOrchestratorAgent

orchestrator = WorkflowOrchestratorAgent()
result = orchestrator.run(
    action="execute",
    query="workflows/base.yaml",
    params={"project_name": "my-api"},
    stop_on_error=True,
    max_phases=10
)

print(result.workflow_name)
# Output: base-workflow

print(f"Vaiheita suoritettu: {result.phases_executed}")
# Output: Vaiheita suoritettu: 5

print(result.final_output)
# Output: {'project_structure': {...}, 'test_results': {...}, 'security_scan': {...}}
```

### Workflowin validointi

```python
result = orchestrator.run(
    action="validate",
    query="workflows/base.yaml"
)

print(result.success)
# Output: True
```

---

## Workflow YAML -muotoilu

```yaml
name: base-workflow
description: Base development workflow

params:
  - project_name
  - project_type

phases:
  - name: initialize
    agent: project_manager
    action: create
    depends_on: []

  - name: analyze
    agent: researcher
    action: analyze
    depends_on: [initialize]

  - name: develop
    agent: developer
    action: generate
    depends_on: [analyze]

  - name: review
    agent: code_review
    action: scan
    depends_on: [develop]

  - name: test
    agent: tester
    action: run
    depends_on: [review]
```

---

## Testikattavuus

```
tests/test_workflow_engine.py + test_orchestration_agent.py — osuuta testit M9:stä
Kattavuus: 91 %
```

Tärkeimmät testit:
- `test_execute_runs_all_phases`
- `test_validate_accepts_valid_yaml`
- `test_phases_run_in_correct_order`
- `test_stop_on_error_halts_workflow`

---

## Liittyvät moduulit

- **Riippuu:** kaikki M1–M20 agentit — workflowissa voidaan viitata mihin tahansa agenttityyppiin
- **Seuraa:** MultiAgentCoordinator (M9) — moniagentti-koordinaatio
- **Käytetään:** ControlCenterAgent (M20) — statusseja varten

## CLI-käyttö

```bash
aide orchestrate --workflow base.yaml              # → WorkflowOrchestratorAgent.execute
aide orchestrate --workflow bugfix.yaml --param issue=BUG-123
```

## Katso myös

- [`multiagent_coordinator.md`](multiagent_coordinator.md) — koordinaatio
- [`modules.md`](../../architecture/modules.md) — kaikki moduulit
- [`dataflow.md`](../../architecture/dataflow.md) — workflow-dataputki
