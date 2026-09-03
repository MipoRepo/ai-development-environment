# DirectorAgent (M1 Core & Director)

**Tiedosto:** `agents/director.py`  
**Moduuli:** M1 — Core & Director  
**Status:** ✅ Valmiina  
**Testit:** 46 | **Kattavuus:** 99 %

---

## Tarkoitus

Projektin johdannot agentti. Hajottaa käyttäjän suuret kysymykset pienempiin tehtäviin ja antaa ne kyseisille agenteille käsittelemättä.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"director"` |
| `input_schema` | `DirectorInput` |
| `output_schema` | `DirectorOutput` |
| `ClassVar` | `AGENT_DESIGN_ACTIONS` (toiminta-ohjeet) |

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `analyze` | Analysoi projektirakenteen, tunnistaa tiedostotyypit ja teknologiat |
| `decompose` | Hajottaa suuren kysymyksen alitehtäviksi |
| `assign` | Kohdistää tehtävät oikeisiin agentteihin riippuvuuksien perusteella |
| `track` | Seuraa tehtaiden edistymistä ja palauttaa raportin |

## Syöte (DirectorInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["analyze", "decompose", "assign", "track"]` | ✅ | Suoritettava toiminto |
| `query` | `str` | ✅ | Käyttäjän kysymys |
| `context_data` | `dict[str, Any]` | ❌ | Projekti- tai kontekstitiedot |
| `project_path` | `str` | ❌ | Polku projektiin (oletus: nykyinen hakemisto) |

## Tuloste (DirectorOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Toimenpiteen onnistuminen |
| `action` | `str` | Suoritettu toiminto |
| `tasks` | `list[dict[str, Any]]` | Hajotetut tehtävät (toimii `decompose`-toiminnossa) |
| `assignments` | `dict[str, str]` | Tehtävä → agentti -kartoitus (`assign`-toiminto) |
| `project_structure` | `dict[str, Any]` | Projektin rakenne (`analyze`-toiminto) |
| `progress` | `dict[str, Any]` | Edistymisen tilanne (`track`-toiminto) |
| `error` | `str \| None` | Virheviesti |

## Esimerkkikoodi

### 1. Projektin analyysi

```python
from agents import DirectorAgent, DirectorInput

agent = DirectorAgent()
result = agent.run(
    action="analyze",
    query="Analysoi tämä projekti"
)

print(result.project_structure)
# Output: {"type": "python", "frameworks": ["flask"], "files": [...], "tests": 46}
```

### 2. Tehtaan hajottaminen

```python
result = agent.run(
    action="decompose",
    query="Rakenna REST API käyttäjähallinnalla käyttäen JWT-todennuksella"
)

for task in result.tasks:
    print(f"  {task['id']}: {task['description']} (prioriteetti: {task['priority']})")
# Output:
#   1: Luo käyttäjämodeli (prioriteetti: high)
#   2: Implementoi JWT-login (prioriteetti: high)
#   3: Lisää validaatiot (prioriteetti: medium)
```

### 3. Tehtaiden kohdistaminen

```python
assignments = agent.run(
    action="assign",
    context_data={"tasks": result.tasks}
)

for task_id, agent_type in assignments.assignments.items():
    print(f"  Tehtävä {task_id} → {agent_type}")
# Output:
#   1 → developer
#   2 → developer
#   3 → testing
```

## Testikattavuus

```
tests/test_director.py — 46 testiä
Kattavuus: 99 % (1 rivi kattamatta: virhepolku)
```

Kaikki testit läpäisti. Tärkeimmät testit:
- `test_analyze_returns_project_structure`
- `test_decompose_creates_ordered_tasks`
- `test_assign_returns_correct_agents`
- `test_track_progress_reports`

## Liittyvät moduulit

- **Seuraaja:** ProjectManagerAgent (M2) projektin luomisessa
- **Riippuu:** KnowledgeAgent (M13) tiedon tallentämiseen
- **Reititaan:** ControlCenterAgent (M20) komennona

## CLI-käyttö

```bash
aide run "Analysoi projektini"                # → DirectorAgent.analyze
aide run "Hajota tehtäväksi"                  # → DirectorAgent.decompose
aide orchestrate --workflow base.yaml         # → WorkflowOrchestratorAgent → Director
```

## Katso myös

- [`dataflow.md`](../../architecture/dataflow.md) — Directorin rooli dataputkessa
- [`agent-lifecycle.md`](../../architecture/agent-lifecycle.md) — agentin elinkaari
- [`modules.md`](../../architecture/modules.md) — kaikki moduulit yhteensä
