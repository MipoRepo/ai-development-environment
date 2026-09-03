# Agenttien orkestointi

AIDE:ssa työntekijät eivät toimisi yksistään — ne orkestrointiinsa eri tavoin. Tämä oppaissa kuvaillaan, kuinka DirectorAgent, WorkflowOrchestratorAgent ja MultiAgentCoordinator yhteistoiminnassa tuottavat monimutkaisen tehtävän.

---

## 1. Orkestron taso: CLI → ControlCenter

Käyttäjä kirjoittaa komennon:

```bash
aide run "Luo projekti Dockerilla ja aseta CI/CD"
```

Tämä kulkee seuraavasti:

```text
CLI (cli.py)
  │
  ▼
CLIOrchestrator (M20)
  │  — parsii komennon
  │  — reitittää agenttiin
  ▼
DirectorAgent (M1)
  │  — hajottaa "Luo projekti Dockerilla ja aseta CI/CD"
  │  — kolmeen alitehtävään:
  │    1. "Luo projekti Dockerilla" → DeveloperAgent + DockerAgent
  │    2. "Aseta CI/CD" → CI_CDAgent (M10)
  │    3. "Aseta CI/CD" → DeploymentAgent (M10)
  ▼
MultiAgentCoordinator (M9)
  │  — topologinen järjestys (Kahnin algoritmi)
  │  — Dependency-kaavio:
  │    DeveloperAgent ───► DockerAgent
  │    DockerAgent ───► CI_CDAgent
  │    CI_CDAgent ───► DeploymentAgent
  │  — Rinnakkain: DeveloperAgent ja DockerAgent voivat osiolisten
  ▼
ControlCenterAgent (M20)
  — päivittää tilan: 4/4 agenttia suoritettu
```

---

## 2. DirectorAgent: hajoitus

DirectorAgent vastaa siitä, että käyttäjän yleinen pyyntö jaetaan osaongelmiksi. Sen kanssa on kolme päätoimintoa:

| Toiminto | Kuvaus |
|---|---|
| `analyze` | Analysoi projektirakenteen (AST + tiedostojärjestelmä) |
| `decompose` | Hajottaa suuren kysymyksen 2–5 pienempään tehtävään |
| `assign` | Määrittää jokaisen alitehtävän vastuun agentille |

Esimerki:

```python
from agents import DirectorAgent

director = DirectorAgent()
result = director.run(
    action="decompose",
    query="Refaktoroi auth-moduuli: poista vanhat funktiot, lisää role-pohjainen pääsy, kirjoita testit"
)

# Tuloste
result.tasks
# [
#   {"description": "Poista vanhat funktiot auth.py:stä", "agent": "developer"},
#   {"description": "Lisää roolipohjainen pääsy", "agent": "security"},
#   {"description": "Kirjoita testit", "agent": "tester"},
# ]
```

---

## 3. MultiAgentCoordinator: riippuvuussuunnittelu

Kun Director on antanut alitehtävät, MultiAgentCoordinator varmistaa, että ne ajetaan oikeassa järjestyksessä.

```python
from agents import MultiAgentCoordinator

coordinator = MultiAgentCoordinator()
result = coordinator.run(
    action="coordinate",
    agents=[
        {"agent_type": "developer", "dependencies": [], "params": {"action": "refactor", "query": "auth.py"}},
        {"agent_type": "security", "dependencies": ["developer"], "params": {"action": "scan", "query": "auth.py"}},
        {"agent_type": "tester", "dependencies": ["security"], "params": {"action": "run", "query": "./tests"}},
    ]
)

print(result.execution_order)
# Output: ['developer', 'security', 'tester']
```

### Kahnin algoritmi

```
1. Laske jokaisen agentin "syntymä" luku (montako riippuu siitä)
2. Lisää kaikki 0-syntyneet (ei riippuvuuksia) ajon jonoon
3. Poista kyseinen agentti ja vähennä sen riippuvuuksista lukua
4. Toista kunnes kaikki on prosessoitu tai jää kiertomerkkien (syke)
5. Jos jääkiertoja → virhe (kiikkuminen)
```

---

## 4. WorkflowOrchestrator: YAML-pohjaiset ketjut

Tyypilliset tehtävät (esim. `feature`, `bugfix`, `new-project`) määritellään YAML-workflowina:

```yaml
# workflows/feature.yaml
name: feature
phases:
  - name: requirements
    agent: project_manager
    action: create
  - name: research
    agent: researcher
    action: research
  - name: develop
    agent: developer
    action: generate
  - name: review
    agent: code_review
    action: scan
  - name: test
    agent: tester
    action: run
```

Käyttö:

```bash
aide orchestrate --workflow feature.yaml --param "query=OAuth2 integraatio"
```

---

## 5. Knowledge-agentin rooli orkestroinnissa

Kaikissa workfloweissa KnowledgeAgent (M13) toimii yhteisenä muistina:

```text
DeveloperAgent
  │  — luo koodin
  │
  ▼
KnowledgeAgent ──► "store" action tallentaaa koodin kontekstin
  │
  ▼
SecurityAgent
  │  — hakee aiemman kontekstin "retrieve"
  │  — tarkistaa turvallisuuden
  │
  ▼
KnowledgeAgent ──► "store" tallentaa security-tulokset
```

---

## 6. CLIOrchestrator: reititys ja konteksti

CLIOrchestrator (M20) on pääsymälta kaikille käskyille:

| Komentomerkintä | Reititetty agenttiin |
|---|---|
| `aide run "..."` | DirectorAgent (M1) |
| `aide init` | ProjectManagerAgent (M2) |
| `aide test` | TesterAgent (M5) |
| `aide orchestrate` | WorkflowOrchestratorAgent (M9) |
| `aide dashboard` | DashboardAgent (M20) |
| `aide status` | ControlCenterAgent (M20) |
| `aide monitor` | WebhookAgent (M19) |

Komentohistoria (50 kpl) ja tab-completion ovat käytettävissä.

---

## 7. ControlCenter: tilan valvonta

ControlCenterAgent (M20) seuraa kaikkia orkestroituja agenteja:

```python
from agents import ControlCenterAgent

cc = ControlCenterAgent()
result = cc.run(action="metrics")
print(f"Agentit: {result.metrics['agent_count']}")  # 20
print(f"Aktiivit: {result.metrics['active_agents']}")  # 18
```

Dashboard-agentti renderöi tämän teksti- tai JSON-muotoon:

```text
╔══════════════════════════════════════╗
║         AIDE Control Center          ║
╠══════════════════════════════════════╣
║ Status: healthy    Version: 2.1.0    ║
║ Agents: 20 (18 active)                ║
║ Uptime: 1d 0h 0m                      ║
╠══════════════════════════════════════╣
║ Agents:                               ║
║  M1  ResearcherAgent     ✓            ║
║  M2  DeveloperAgent      ✓            ║
║  ...                                    ║
║  M20 CLIOrchestrator     ✓            ║
╚══════════════════════════════════════╝
```

---

## Katso myös

- [Workflow-orchestrator (M9)](../agents/orchestration/workflow_orchestrator.md)
- [Multiagent-coordinator (M9)](../agents/orchestration/multiagent_coordinator.md)
- [Moduulit yhteensä](../architecture/modules.md)
