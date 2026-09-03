# AIDE WebDOC — Web-dokumentaatio

Tämä on kattava web-dokumentaatio (WebDOC) AIDE-järjestelmästä — siinä kuvataan kaikki 20 moduulia, 60+ agenttia, arkkitehtuuri, käyttö ja kehitysprosessi. Dokumentaatiodokumentit ovat tässä organisoitu valikoista ja sisältöjä vastaavasti.

---

## Sisällysluettelo

| No. | Osa | Sivut | Kuvaus |
|-----|------|--------|--------|
| 1 | [Aloeitus](#1-aloitus) | `index.md`, `getting-started/*` | Projektin yleiskatsaus, asennus, ensimmäinen projekti |
| 2 | [Käyttöopas](#2-käyttöopas) | `user-guide/*` | Tehtävät, orkestrointi, työnkulut |
| 3 | [Käsitteet](#3-käsitteet) | `concepts/*` | Agentti, workflow, moduuli, pohja-arkkitehtuuri |
| 4 | [Agentit](#4-agentit) | `agents/overview.md`, `agents/*/` | Kaikki 20 moduulin 60+ agenttia |
| 5 | [Arkkitehtuuri](#5-arkkitehtuuri) | `architecture/*` | Moduulit, dataputki, agenttien elinkaari |
| 6 | [Työnkulut](#6-työnkulut) | `workflows/*` | YAML-pohjaiset feature/bugfix/new-project ketjut |
| 7 | [Esimerkit](#7-esimerkit) | `examples/*` | Web-sovellus, API-palvelu |
| 8 | [Projektinhallinta](#8-projektinhallinta) | `project-management/*` | Vision, roadmap, TODO-lista |
| 9 | [Kehittäjäoppaat](#9-kehittäjäoppaat) | `todo-use.md` | Kontribuointi, kehitysprosessi |

---

## 1. Aloitus

Tämä osio kattaa projektin asennuksen, ensimmäisen projektin luomisen ja Claude Code -työkalun käytön.

### `index.md` — Projektin yleiskatsaus
- **Nimeä:** AI Development Environment (AIDE)
- **Versio:** 2.1.0
- **Kuvaus:** Agenttipohjainen ohjelmistokehitysympäristö, joka automatisoi rutiinit ja opettaa sinua samalla
- **Käyttöohjeistus:** https://MipoRepo.github.io/ai-development-environment/

### `getting-started/installation.md` — Asennus
- Vaatimukset: Python 3.11+, pip, git
- Vaihtoehtoinen: Docker (joka sisältää kaikki riippuvuudet)
- Asennus vaiheet:
  1. `git clone https://github.com/MipoRepo/ai-development-environment.git`
  2. `cd ai-development-environment`
  3. `python -m venv .venv`
  4. `source .venv/bin/activate` (Linux/Mac) tai `.venv\Scripts\activate` (Windows)
  5. `pip install -r requirements.txt`

### `getting-started/first-project.md` — Ensimmäinen projekti
- Komennot:
  ```bash
  aide init my_project
  cd my_project
  aide run "Luo sovellus, joka näyttää 'Hello World'"
  ```
- Tämä luo projektirakenteen:
  - `src/` — lähdelähdet
  - `tests/` — testit
  - `docs/` — dokumentaatio

### `getting-started/claude-code-use.md` — Claude Code -työkalun käyttö
- Claude Code on pääsy AIDE-agentteihin
- Käyttö:
  ```bash
  aide run "Refaktoroi auth-moduuli"
  aide task "Lisää käyttäjätuki"
  ```

---

## 2. Käyttöopas

Opas siitä, miten käyttää AIDE-anneja päivittäisessä työssä.

### `user-guide/tasks.md` — Tehtävät
- Komennot:
  | Komento | Toiminto |
  |--------|---------|
  | `aide run "kysymys"` | Suorita yksi agentti |
  | `aide init project` | Luo uusi projekti |
  | `aide test` | Suorita testit |
  | `aide orchestrate --workflow feature` | Aja YAML-workflow |
  | `aide dashboard` | Avaa valvontapaneeli |

### `user-guide/orchestration.md` — Orkestrointi
- Orkestroinnin 4-tason malli:
  1. **Orkestron taso:** CLI → CLIOrchestrator → DirectorAgent
  2. **DirectorAgent:** hajottaa projektin osaongelmiin
  3. **MultiAgentCoordinator:** topological sort (Kahnin algoritmi)
  4. **ControlCenterAgent:** päivittää tilan reaaliaikaisesti

### `user-guide/workflows.md` — Työnkulut
- Työnkulkujen yleiskatsaus
- Esimerkkikäyttö:
  ```bash
  aide orchestrate --workflow feature.yaml --param "query=OAuth2 integraatio"
  ```

---

## 3. Käsitteet

Perusarvaukset ja arkkitehtuurin käänteinen.

### `concepts/overview.md` — Käsitteiden yleiskatsaus
- AIDE:n arkkitehtuuri perustuu modular-agenttiin malliin
- 20 moduulia (M1–M20), jokainen eri osa-alueelle
- Agentit viestitsevät WorkflowOrchestratorin ja MultiAgentCoordinatorin kautta

### `concepts/agent.md` — Agentti
- **BaseAgent ABC:** `run()` → `_run()` → validaatio (Pydantic)
- `ClassVar agent_type` — tunnus agentille
- `input_schema` ja `output_schema` — Pydantic Field-määrittelyt
- Lazy-importti MODULE_REGISTRY → import-kierteiltä välttäminen

### `concepts/workflow.md` — Työnkulku
- YAML-pohjaiset ketjut
- Phase-moduulit: requirements → research → develop → review → test
- Dependency-kaaviot (DAG) ja Kahnin algoritmi

---

## 4. Agentit

Kaikki AIDE-agentit on järjestelty 20 moduuliin. Alla on modulit ja niiden agentit.

### M1 — Core
- **ResearcherAgent** — tiedonhaku (WebSearch, WebFetch, tiedostot)
  - Toiminnot: `research`, `summarize`, `compare`
  - Testit: 52 | Kattavuus: 93%

### M2 — Development
- **DeveloperAgent** — koodin generointi, refaktorointi, bugikorjaus
  - Toiminnot: `write`, `refactor`, `fix_bug`, `generate_unit_tests`
  - Kielituki: Python, JavaScript, TypeScript, Go, Rust
  - Testit: 32 | Kattavuus: 91%
- **TaskPlannerAgent** — tehtävien suunnittelu ja priorisointi
  - Toiminnot: `plan`, `prioritize`, `schedule`

### M3 — Director
- **DirectorAgent** — projektin hajottaminen osaongelmiin
  - Toiminnot: `analyze`, `decompose`, `assign`
  - TYÖTYYPPIT: `feature`, `bugfix`, `refactor`, `research`, `maintenance`
  - Testit: 51 | Kattavuus: 94%

### M4 — Project Manager
- **ProjectManagerAgent** — projektinhallinta, backlog, milestonet
  - Toiminnot: `update_backlog`, `set_milestone`, `reprioritize`, `status_report`
  - Testit: 46 | Kattavuus: 89%

### M5 — Tester
- **TesterAgent** — testien suunnittelu ja generointi
  - Toiminnot: `generate_unit_tests`, `run_tests`, `coverage_report`, `analyze_failures`
- **QAGent** — laadunvalvonta ja bugiraportointi

### M6 — Technical Writer
- **TechnicalWriterAgent** — MARKDOWN, API, käyttöoppaat
  - Toiminnot: `generate_docs`, `write_api_reference`, `generate_user_guide`, `build_mkdocs`
- **APIDocumentationAgent** — OpenAPI-speksit
- **UserDocumentationAgent** — käyttöohjeet

### M7 — Security
- **SecurityArchitectAgent** — turvallisuusdesigni
- **SecurityReviewAgent** — regex-pohjainen skannaus (`eval`, `exec`, `pickle`, `yaml.load`)
- **SASTAgent** — AST-pohjainen statinen analyysi
- **DependencySecurityAgent** — `pip-audit` ja haavoittuvuustarkistus
- **SecretsAgent** — AWS-keyt, API-avaimet, tokenit
- **ContainerSecurityAgent** — Dockerfile-turvallisuus (root USER, ADD, chmod 777, EXPOSE 22)
  - Testit: 40 | Kattavuus: 94%

### M8 — Testing Automation
- **TestRunnerAgent** — pytest, kattavuus (--cov), rinnakkaisuus (-n auto)
- **PerformanceTestAgent** — Lastitestaus (locust), benchmarkit
- **IntegrationTestAgent** — service-tason integrointitestaus

### M9 — Orchestration
- **WorkflowOrchestratorAgent** — YAML-workflowin suoritus (phases + transitions)
- **MultiAgentCoordinatorAgent** — topologinen järjestys (Kahnin algoritmi)
  - Tunnisteet: `execution_order`, `dependency_graph`, `errors`

### M10 — DevOps
- **CI_CDAgent** — GitHub Actions / GitLab CI -pipeline
- **DockerAgent** — Dockerfile-generointi, optimointi (8 kerää kerrostusta)
- **DeploymentAgent** — Kubernetes-manifestit, Helm-chartit
- **InfrastructureAgent** — Terraform/IaC-generointi

### M11 — Pedagogiikka
- **MentorAgent** — henkilopaikka-ohjauksen antaminen
- **ContentDesignerAgent** — oppimateriaalien suunnittelu (Socratic, Bloom)
- **ExplainerAgent** — koodin selittäminen eri tasoissa
- **LearningPathAgent** — henkilopaikallinen oppimispolku (ADAPTIVE)

### M12 — Learning & Assessment
- **AssessmentAgent** — kysymykset, vastaukset, pisteytys
- **FeedbackAgent** — palautteen antaminen ja parannusehdotukset
- **LearningPathAgent** — oppimispolkua seuraava versio (ADAPTIVE)

### M13 — Knowledge & Memory
- **KnowledgeAgent** — tiedon tallentaminen ja hakeminen
  - Toiminnot: `store`, `retrieve`, `search`
  - Pohjana: ChromaDB (768-dimensiovainen embeddings)
- **MemoryAgent** — pitkäaikainen konteksti (conversational_memory)
- **ContextCompilerAgent** — kontekstin kääntäminen tiivistetyksi yhteenvetokeksi

### M14 — Maintenance
- **CleanupAgent** — vanojen tiedostojen poisto (`*.pyc`, `__pycache__/`, `node_modules/`)
- **DependencyAgent** — riippuvuuksien tarkistus ja päivitys
- **UpgradeAgent** — automaattinen riippuvuusversioinnin nostaaminen

### M15 — Release & Governance
- **ReleaseManagerAgent** — versiopaketin luonti (CHANGELOG.md, tagaus)
- **ChangelogAgent** — muetusten analyysi (Conventional Commits)
- **ComplianceAgent** — rekisteröinti (LICENSE, NOTICE, SBOM)

### M16 — Agent Engineering
- **AgentDesignAgent** — agentin rakenteen suunnittelu (agent_type, schema, actions)
- **AgentFactoryAgent** — agentin automaattinen generointi (template + pydantic)
- **PromptOptimizerAgent** — Promptin optimointi (Chain-of-Thought, FSG, ABE)

### M17 — AI Gateway
- **AIGatewayAgent** — yleinen pääsy kaikkiin LLM:iin (Anthropic, OpenAI, Ollama)
- **LLMRouterAgent** — mallin valinta (GPT-4o, Claude 3, Llama 3)
- **TokenTrackerAgent** — tokenien lukumäärää ja kustannuksia seuraava

### M18 — Local LLM
- **LocalModelAgent** — paikallisten mallien asennus (ollama pull, GGUF)
- **ModelRunnerAgent** — mallin suorittaminen (llama.cpp, GPU-niiputtä)
- **QuantizationAgent** — kvanttien säädöntä (Q4_K, Q8_0, F16)

### M19 — MCP & Integrations
- **MCPIntegrationAgent** — Model Context Protocol (MCP)
  - Toolit: `list_resources`, `read_resource`, `call_tool`
  - Resurssit: `list_resources`, `read_resource`
- **APIIntegrationAgent** — REST/GraphQL API-rajapinnat
  - URL-validointi `urlparse` -kirjastolla
- **WebhookAgent** — SHA256 HMAC -allekirjoatusten validointi
  - WEBHOOK_ACTIONS: `github`, `gitlab`, `slack`, `discord`, `generic`
  - WEBHOOK_STATUSES: `pending`, `verified`, `failed`, `replayed`

### M20 — Control Center
- **ControlCenterAgent** — järjestelmänvalvonta
  - Toiminnot: `metrics`, `health`, `agents`, `register_agent`
  - Palauttaa: agent_count, active_agents, queue_depth, error_rate
- **DashboardAgent** — tekstipohjainen valvontapaneeli
- **CLIOrchestrator** — CLI-reititys (`aide [subcommand]`)
  - MODULE_REGISTRY lazy-importit
  - Komennot: `run`, `init`, `test`, `orchestrate`, `dashboard`, `status`, `monitor`

---

## 5. Arkkitehtuuri

Järjestelmän perusmuoto ja modulien välinen vuorovaihtelu.

### `architecture/overview.md` — Arkkitehtuurin yleiskatsaus
```
[User] → CLI → CLIOOrchestrator → DirectorAgent
                    ↓
           WorkflowOrchestrator
                    ↓
           MultiAgentCoordinator (DAG)
                    ↓
    ┌───────┬───────┬───────┬───────┬───────┐
    │ M1-M5 │ M6-M10│ M11-M13│ M14-M16│ M17-M20│
    └───────┴───────┴───────┴───────┴───────┘
                    ↓
           ControlCenterAgent
```

### `architecture/modules.md` — Modulit (M1–M20)
| Moduuli | Aihe | Agentit | Tila |
|--------|------|---------|------|
| M1 | Core | ResearcherAgent | ✅ |
| M2 | Development | DeveloperAgent, TaskPlannerAgent | ✅ |
| M3 | Director | DirectorAgent | ✅ |
| M4 | Project Manager | ProjectManagerAgent | ✅ |
| M5 | Tester | TesterAgent, QAGent | ✅ |
| M6 | Technical Writer | TechnicalWriterAgent, APIDocumentationAgent, UserDocumentationAgent | ✅ |
| M7 | Security | SecurityArchitectAgent, SecurityReviewAgent, SASTAgent, DependencySecurityAgent, SecretsAgent, ContainerSecurityAgent | ✅ |
| M8 | Testing Automation | TestRunnerAgent, PerformanceTestAgent, IntegrationTestAgent | ✅ |
| M9 | Orchestration | MultiAgentCoordinatorAgent, WorkflowOrchestratorAgent | ✅ |
| M10 | DevOps | CI_CDAgent, DockerAgent, DeploymentAgent, InfrastructureAgent | ✅ |
| M11 | Pedagogiikka | MentorAgent, ContentDesignerAgent, ExplainerAgent, LearningPathAgent | ✅ |
| M12 | Learning & Assessment | AssessmentAgent, FeedbackAgent, LearningPathAgent | ✅ |
| M13 | Knowledge & Memory | KnowledgeAgent, MemoryAgent, ContextCompilerAgent | ✅ |
| M14 | Maintenance | CleanupAgent, DependencyAgent, UpgradeAgent | ✅ |
| M15 | Release & Governance | ReleaseManagerAgent, ChangelogAgent, ComplianceAgent | ✅ |
| M16 | Agent Engineering | AgentDesignAgent, AgentFactoryAgent, PromptOptimizerAgent | ✅ |
| M17 | AI Gateway | AIGatewayAgent, LLMRouterAgent, TokenTrackerAgent | ✅ |
| M18 | Local LLM | LocalModelAgent, ModelRunnerAgent, QuantizationAgent | ✅ |
| M19 | MCP & Integrations | MCPIntegrationAgent, APIIntegrationAgent, WebhookAgent | ✅ |
| M20 | Control Center | ControlCenterAgent, DashboardAgent, CLIOrchestrator | ✅ |

### `architecture/agent-layer.md` — Agenttakerros
- BaseAgent ABC-arkkitehtuuri
- Pydantic-validointi input/output -schemoissa
- Lazy-importti MODULE_REGISTRY
- pytest-fixturit ja --cov-kattavuusmittaus

### `architecture/dataflow.md` — Dataputki
```
User query → DirectorAgent.analyze → DirectorAgent.decompose → MultiAgentCoordinator.coordinate → [agent.run()] → KnowledgeAgent.store → ControlCenterAgent.metrics
```

### `architecture/agent-lifecycle.md` — Agentit-elinkaari
1. **Initialize:** `agent = AgentType()`
2. **Run:** `agent.run(action="...", **params)`
3. **Validate:** Pydantic input_schema validointi
4. **Execute:** `_run()` metodi
5. **Return:** Pydantic output_schema serialisointi
6. **Log:** KnowledgeAgent.store

---

## 6. Työnkulut

Eri tyypit työnkuluista ja niiden YAML-määrittelyt.

### `workflows/base-workflow.md` — Perus-workflow
- Kaikkien workflowen perusmuodon
- 5-vaiheinen rakenne: requirements → research → develop → review → test

### `workflows/feature.md` — Uusi ominaisuus
```yaml
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

### `workflows/new-project.md` — Uusi projekti
- Automaattinen projektin generointi (`aide init project_name`)
- Sisältää: src/, tests/, docs/ -rakenteen

### `workflows/bugfix.md` — Bugikorjaus
- Virheenkorjauksen kulku
- Sisältää testausvaiheen ennen mergeä

---

## 7. Esimerkit

Käytännön esimerkit AIDE:n käytöstä eri tilanteissa.

### `examples/web-app.md` — Web-sovellus
- React + FastAPI -yhteensopiva sovellus
- Käyttö: `aide run "Luo React-sovellus, joka näyttää käyttäjät"`

### `examples/api-service.md` — API-palvelu
- REST API service pydantic-mallien kanssa
- Generoi: routerit, middleware, exception handlerit

---

## 8. Projektinhallinta

### `project-management/vision.md` — Näkymä
- AIDE tavoitteeet: "Agenttipohjainen ohjelmistokehitysympäristö, joka automatisoi rutiinit ja opettaa sinua samalla"

### `project-management/roadmap.md` — Seurantataulu
| Versio | Kuvaus | Status |
|--------|--------|--------|
| Alpha 1.0 | Perusagentit (M1–M5) | ✅ |
| Alpha 1.1 | Kevyt orkestointi + Security | ✅ |
| Alpha 2.0 | Kaikki 20 moduulia | ✅ |
| Alpha 2.1 | MCP-integraatiot | ✅ |
| Alpha 2.2 | Local LLM + AI Gateway | ✅ |
| Alpha 2.3 | Control Center + dokumentaatio | ✅ |

### `project-management/todo/TODO-alpha2.3.md` — TODO-listat
- Kaikki moduulit M1–M20
- Testauskattavuus ≥85 % (useimmissa 90 %+)
- Kaikilla agenteilla on dokumentaatio

---

## 9. Kehittäjäoppaat

### `todo-use.md` — AIDE-kehittäjäoppaat
- Asennus Dockerissa
- Modulien kehittäminen
- Testaus (`pytest --cov`)
- MkDocs-dokumentaation rakentaminen (`mkdocs serve`)
- Muut asiat: `.env.example`-konfiguraatio, requirements.txt, CLI-komennot

---

## 10. Kääntö (Translation)

WebDOC sisältää kääntöominaisuuden, joka mahdollistaa sen kääntämisen eri kielille käyttäen **MyMemory API:a** (ilmainen taso: 100 kääntöä/päivä). Kaikki WebDOC-aineisto on oletuksena käännettävissä suomesta englantiin, ja suomenkieliset statusviestit näytetään aina.

### Kääntäjämoduuli

Kääntäjämä on `tools/translator.py` — se:
- Lukee `MYMEMORY_API_KEY` -avain `.env`-tiedostosta (ilmainen taso toimii ilman avainta)
- Kutsuu MyMemory API:a `https://api.mymemory.translated.net/get`
- Palauttaa käännetyn tekstin
- Käsittelee virheet (liian monta kääntöä, verkkovirheet)
- Näyttää suomenkieliset edistymisviestit (esim. "✅ Käännetään: 50%")

---

### Kääntäjän asetukset (.env.example)

```env
# MyMemory API (ilmainen käännöspalvelu: 100 kääntöä/päivä, 5000/päivä avaimella)
# Saat avaimen rekisteröitymällä: https://mymemory.translated.net/
MYMEMORY_API_KEY=your_api_key_here
MYMEMORY_LANG_FROM=fi
MYMEMORY_LANG_TO=en
```

### Käyttö

**Yksittäisen tekstin kääntäminen:**

```bash
python tools/translator.py --text "Hei maailma" --lang fi --to en
# 🔤 fi → en:
# 📝 Hei maailma
# 🎯 Hello World
```

**Tiedoston kääntäminen (esim. WebDOC):**
```bash
python tools/translator.py --input webdoc.md --output webdoc-en.md --lang fi --to en
# ℹ️  Käytetään ilmaista MyMemory-tasoa (100 kääntöä/päivä).
# ℹ.  Suositus: lisää MYMEMORY_API_KEY .env-tiedostoon lisätäksesi kiistamukaisuuden (5000/päivä).
# ✅ Käännetään: 10%
# ✅ Käännetään: 20%
# ...
# ✅ Käännös suoritettu! Tiedosto tallennettu: webdoc-en.md
```

**Vaihtoehtoiset komennot:**

| Komento | Toiminto |
|--------|---------|
| `--reverse` | Käännä suoraan suomi → englanti (oletus) |
| `--api-key <avain>` | Ylikirjoita API-avain komentoriviltä |
| `--lang fi --to en` | Määritä kielet (tukee: `fi`, `en`) |

### Rajoitukset

| Palvelu | Ilmainen taso | Maksullinen taso |
|---------|---------------|------------------|
| MyMemory | 100 kääntöä/päivä | 5000 kääntöä/päivä (API-avain) |
| Kielet | Suomi - Englanti | Tulevat versiot tukevat lisää kieliä |
| API-avain | Ei vaadittu | Suositeltu lisäoikeuksien lisäämiseksi |

---

## Liitetyt tiedostot

| Liite | Kuvaus |
|-------|--------|
| `cli.py` | CLI-årsinnan pääsyagentti |
| `schemas/` | Pydantic-skeemat |
| `workflows/` | YAML-workflow-tiedostot |
| `agents/` | Agenttien lähdelähettajat |
| `tools/` | CLI-työkalut (mukaan lukien `translator.py`) |
| `tests/` | Pytest-testit |
| `.env.example` | Ympäristömuuttuja-esimerkki |
| `webdoc.md` | Tämä WebDOC-dokumentti |
