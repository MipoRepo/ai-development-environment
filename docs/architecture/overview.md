# AIDE-arkkitehtuuri — Yleiskatsaus

**Versio:** Alpha 2.10 (M20 GUI / Control Center)  
**Testit:** 1 021 (90 % kattavuus)  
**Generoitu:** 2026-09-03

---

## 1. Mikä on AIDE?

AIDE (AI Development Environment) on 20-moduulinen monorepo-agenttipino, joka tukee koko ohjelmistokehityksen elinkaarta. Jokainen moduuli keskittyy tiettyyn osa-alueeseen — projektinhallinta, tutkimus, kehitys, testaus, turva, dokumentaatio, orkesterointi, DevOps, oppiminen, knowledge, ylläpito, julkaiseminen, agenttimekhenologia, API-gateway, paikalliset LLM:t, MCP-integraatiot — ja lopulta keskitetty ohjauspaneeli.

### Arkkitehti

- **BaseAgent-ABC** — kaikista agenteista peritty perusluokka (`agents/base.py`)
- **Pydantic-validointi** — kaikki syötteet ja tulosteet ovat Pydantic-malleja
- **Module registry** — importit ovat lazy-tyyppisiä `__init__.py`-ssä
- **Workflow engine** — YAML-pohjaiset workflowt (`workflows/engine.py`)

---

## 2. Modulit — yhden lukuisana

| # | Moduuli | Agentit | Status |
|---|---|---|---|
| M1 | Core & Director | DirectorAgent | ✅ |
| M2 | Project Management | ProjectManagerAgent, RequirementsAgent | ✅ |
| M3 | Research | ResearcherAgent, TechnologyResearcherAgent | ✅ |
| M4 | Development | DeveloperAgent, RefactoringAgent, CodeReviewAgent | ✅ |
| M5 | Testing | TestDesignerAgent, TesterAgent, QAAgent | ✅ |
| M6 | Security | SecurityReviewAgent, SASTAgent, DependencySecurityAgent, SecretsAgent, ContainerSecurityAgent | ✅ |
| M7 | Documentation | TechnicalWriterAgent, APIDocumentationAgent, UserDocumentationAgent, MkDocsAgent | ✅ |
| M8 | Testing Automation | TestRunnerAgent, PerformanceTestAgent, IntegrationTestAgent | ✅ |
| M9 | Orchestration | WorkflowOrchestratorAgent, MultiAgentCoordinator | ✅ |
| M10 | DevOps | DockerAgent, CI_CDAgent, InfrastructureAgent, DeploymentAgent | ✅ |
| M11 | Pedagogy | MentorAgent, ExplainerAgent, PedagogyAgent, ContentDesignerAgent | ✅ |
| M12 | Learning & Assessment | LearningPathAgent, AssessmentAgent, FeedbackAgent | ✅ |
| M13 | Knowledge & Memory | KnowledgeAgent, MemoryAgent, ContextCompilerAgent | ✅ |
| M14 | Maintenance | UpgradeAgent, CleanupAgent, DependencyAgent | ✅ |
| M15 | Release & Governance | ReleaseManagerAgent, ChangelogAgent, ComplianceAgent | ✅ |
| M16 | Agent Engineering | AgentDesignAgent, PromptOptimizerAgent, AgentFactoryAgent | ✅ |
| M17 | AI Gateway | AIGatewayAgent, LLMRouterAgent, TokenTrackerAgent | ✅ |
| M18 | Local LLM | LocalModelAgent, ModelRunnerAgent, QuantizationAgent | ✅ |
| M19 | MCP & Integrations | MCPIntegrationAgent, APIIntegrationAgent, WebhookAgent | ✅ |
| M20 | GUI / Control Center | ControlCenterAgent, DashboardAgent, CLIOrchestrator | ✅ |

Kunkin modulin tarkempi kuvaus on tiedostossa [`modules.md`](modules.md).

---

## 3. Arkkitehtuurin kerrosmalli

```text
┌─────────────────────────────────────────────────────────┐
│                      CLI (cli.py)                        │
│                      Typer                               │
├─────────────────────────────────────────────────────────┤
│                  ControlCenterAgent (M20)                │
│              DashboardAgent + CLIOrchestrator            │
├─────────────────────────────────────────────────────────┤
│              OrchestrationAgent (M9)                      │
│       (WorkflowOrchestratorAgent, MultiAgentCoordinator)  │
├─────────────────────────────────────────────────────────┤
│               AI Gateway (M17)                            │
│        (AIGatewayAgent, LLMRouterAgent)                  │
├─────────────────────────────────────────────────────────┤
│               Agentit M1–M19                              │
│  (Director, Dev, Security, DevOps, Knowledge, ...)        │
├─────────────────────────────────────────────────────────┤
│              AI-mallit (OpenRouter)                      │
│              Paikalliset LLM:t (Ollama)                  │
│              MCP-palvelimet (M19)                         │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Tärkeimmät komponentit

| Komponentti | Tiedosto | Kuvaus |
|---|---|---|
| **BaseAgent** | `agents/base.py` | ABC-arkkitehtuuri: `run()` → `_run()` → validointi |
| **Module Registry** | `agents/__init__.py` | Lazy-importit kaikista agenteista |
| **Workflow Engine** | `workflows/engine.py` | YAML-pohjaiset workflowt (base, bugfix, feature) |
| **AI Provider** | `tools/ai_provider.py` | OpenRouter-integraatio (langchain + openai) |
| **CLI** | `cli.py` | Typer CLI (`aide init`, `aide run`, `aide dashboard`, ...) |
| **Schemas** | `schemas/project.py` | Pydantic-mallit projektille ja moduuleille |
| **Testit** | `tests/` | 1021 testiä — 90 % kokonaisuudessa |

---

## 5. CLI-käyttö

```bash
aide init              # Luo uuden projektin (M2 + RequirementsAgent)
aide run "Tehtävä"     # Aja tehtävä DirectorAgentillä (M1)
aide dashboard         # Näytä mittarit (M20 DashboardAgent)
aide status            # Järjestelmän tila (M20 ControlCenterAgent)
aide orchestrate       # Aja workflow YAML (M9 WorkflowOrchestratorAgent)
```

---

## 6. Testaus ja kattavuus

- **Kirjasto:** `pytest` + `pytest-asyncio` + `pytest-cov`
- **Vähimmäiskattavuus:** 80 % jokaisessa moduulissa
- **Testitiedostot:** `tests/test_*.py` (yksi tiedosto joka agenttimoduulille)
- **Fixturet:** `tests/conftest.py`

---

## 7. Versio- ja kehityskäytäntö

- **Versiokäytäntö:** Alpha 2.x (M1–M20) → Beta 1.0 (kun käyttäjä kääntää sen käyttöön)
- **Muistit:** `.claude/memories/` — yksi tiedosto joka moduulille
- **Muutosluettelo:** päivitettävä `docs/changelog.md:ssa

---

## 8. Seuraavat askeleet

- Lue [`modules.md`](modules.md) — jokaisen moduulin tarkempi selitys
- Lue [`dataflow.md`](dataflow.md) — miten data liikkuu agenttien välillä
- Lue [`agent-lifecycle.md`](agent-lifecycle.md) — agentin elinkaari
