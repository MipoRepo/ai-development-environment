# AIDE-moduulit — yksityiskohtainen kuvaus

**Generoitu:** 2026-09-03 | **Versio:** Alpha 2.10

---

## M1 — Core & Director

**Tiedosto:** `agents/director.py`  
**Agentti:** `DirectorAgent`  
**Status:** ✅ Valmiina  
**Testit:** 46 (99% kattavuus)

### Tarkoitus
Projektin johdannot agentti, joka hajottaa käyttäjän pyynnökset pienempiin tehtäviin ja antaa ne muidille agenteille käsitettäväksi.

### Toiminnot
- `analyze` — analysoi projektirakenteen ja tunnista tiedostotyyppit
- `decompose` — hajottaa suuren kysymyksen pienempiin alitehtäviin
- `assign` — kohdistää tehtävät oikeisiin agentteihin
- `track` — seurtaa tehtaiden edistymistä

---

## M2 — Project Management

**Tiedosto:** `agents/project_manager.py`  
**Agentit:** `ProjectManagerAgent`, `RequirementsAgent`  
**Status:** ✅ Valmiina  
**Testit:** 30 (94 % kattavuus)

### Tarkoitus
Projektin luominen ja ylläpito, vaatintojen kerääminen aloituksessa.

### Toiminnot
- **ProjectManagerAgent:** `create`, `configure`, `generate_docs`, `add_module`, `add_task`
- **RequirementsAgent:** vaatintojen analyysi, modulisuunnittelu

---

## M3 — Research

**Tiedosto:** `agents/researcher_agent.py`  
**Agentit:** `ResearcherAgent`, `TechnologyResearcherAgent`  
**Status:** ✅ Valmiina  
**Testit:** 32 (94 % kattavuus)

### Tarkoitus
Projektin teknologisten tuntuntoimintojen ja rakenteen analyysi.

### Toiminnot
- **ResearcherAgent:** AST-parsimus, tiedostojen skannaus, teknologioiden tunnistus, projektirakenteen muodostus
- **TechnologyResearcherAgent:** teknologiasuositukset, stack-analyysi

---

## M4 — Development

**Tiedosto:** `agents/developer.py`  
**Agentit:** `DeveloperAgent`, `RefactoringAgent`, `CodeReviewAgent`  
**Status:** ✅ Valmiina  
**Testit:** 32 (94 % kattavuus)

### Tarkoitus
Koodin generointi, refaktorointi ja laadunvalvinta.

### Toiminnot
- **DeveloperAgent:** generaatio Python/JS/Markdown-koodista, tiedostojen luonti/täydennys
- **RefactoringAgent:** puuttuvat dokumentaatiot, käyttämättomat importit, pitkät funktiot
- **CodeReviewAgent:** turvallisuusongelmat (eval, exec, shell=True), laatuongelmat (bare except, import *)

---

## M5 — Testing

**Tiedosto:** `agents/testing_agent.py`  
**Agentit:** `TestDesignerAgent`, `TesterAgent`, `QAAgent`  
**Status:** ✅ Valmiina  
**Testit:** 24 (94 % kattavuus)

### Tarkoitus
Testien suunnittelu ja automaosa testaamisessa.

### Toiminnot
- **TestDesignerAgent:** AST-pohjainen testisuunnittelu
- **TesterAgent:** `pytest`-subprosessin suoritus, tulosteen tarkkailu
- **QAAgent:** kattavuustarkistus, testitiedostojen tarkistus, ohjelmointikäytäntöjö

---

## M6 — Security

**Tiedosto:** `agents/security_agent.py`  
**Agentit:** `SecurityReviewAgent`, `SASTAgent`, `DependencySecurityAgent`, `SecretsAgent`, `ContainerSecurityAgent`  
**Status:** ✅ Valmiina  
**Testit:** 40 (94 % kattavuus)

### Tarkoitus
Projektin turvallisuustarkastus kaikilta osa-alueilta.

### Toiminnot
- **SecurityReviewAgent:** regex-pohjainen skannaus (eval, exec, salasanat, SQL-injektiot)
- **SASTAgent:** AST-pohjainen statinen analyysi
- **DependencySecurityAgent:** haavoittuvien pakettien tarkistus + `pip-audit`
- **SecretsAgent:** AWS-keyt, GitHub-tokenit, API-avaimet, `.env`-skannaus
- **ContainerSecurityAgent:** Dockerfile-turvallisuus (root, ADD, chmod 777, EXPOSE 22)

---

## M7 — Documentation

**Tiedosto:** `agents/documentation_agent.py`  
**Agentit:** `TechnicalWriterAgent`, `APIDocumentationAgent`, `UserDocumentationAgent`, `MkDocsAgent`  
**Status:** ✅ Valmiina  
**Testit:** 46 (94 % kattavuus)

### Tarkoitus
Projektin dokumentaation automatisoitu luonti.

### Toiminnot
- **TechnicalWriterAgent:** `PROJECT.md`, `AGENTS.md`, `ARCHITECTURE.md`
- **APIDocumentationAgent:** AST-pohjainen API-analyysi, OpenAPI-3.0-schema
- **UserDocumentationAgent:** README-generointi (ominaisuudet, asennus, käyttö)
- **MkDocsAgent:** `mkdocs.yml`-generointi, nav-konfiguuraatio

---

## M8 — Testing Automation

**Tiedosto:** `agents/testing_automation_agent.py`  
**Agentit:** `TestRunnerAgent`, `PerformanceTestAgent`, `IntegrationTestAgent`  
**Status:** ✅ Valmiina  
**Testit:** 37 (91 % kattavuus)

### Tarkoitus
Testiautomaatio, suorituskykytestaus ja integraatiotestaus.

### Toiminnot
- **TestRunnerAgent:** `pytest`-subprosessi, coverage-analyysi, fail-fast
- **PerformanceTestAgent:** benchmarkit, warmup, p95-lukema
- **IntegrationTestAgent:** moduulien tuonti, cross-moduuli-riippuvuudet

---

## M9 — Orchestration

**Tiedosto:** `agents/orchestration_agent.py`  
**Agentit:** `WorkflowOrchestratorAgent`, `MultiAgentCoordinator`  
**Status:** ✅ Valmiina  
**Testit:** 30 (91 % kattavuus)

### Tarkoitus
Agenttien ja workflowjen orkesterointi.

### Toiminnot
- **WorkflowOrchestratorAgent:** YAML-workflowsin suoritus (vaiheet, stop_on_error, max_phases)
- **MultiAgentCoordinator:** topologinen järjestys riippuvuuksien mukaan (Kahnin algoritmi)

---

## M10 — DevOps

**Tiedosto:** `agents/devops_agent.py`  
**Agentit:** `DockerAgent`, `CI_CDAgent`, `InfrastructureAgent`, `DeploymentAgent`  
**Status:** ✅ Valmiina  
**Testit:** 63 (kaikki läpäisti)

### Tarkoitus
Sovelluksen konttien ja deploymentin hallinta.

### Toiminnot
- **DockerAgent:** `Dockerfile` + `docker-compose.yaml` (python-api, web-app, cli, default)
- **CI_CDAgent:** GitHub Actions -workflowit (ci-cd, linting, security)
- **InfrastructureAgent:** infra-tiedostojen analyysi, complexity_score
- **DeploymentAgent:** deploy-strategiat (docker-swarm, kubernetes, aws-ecs, static)

---

## M11 — Pedagogy

**Tiedosto:** `agents/pedagogy_agent.py`  
**Agentit:** `MentorAgent`, `ExplainerAgent`, `PedagogyAgent`, `ContentDesignerAgent`  
**Status:** ✅ Valmiina  
**Testit:** 68 (kaikki läpäisti)

### Tarkoitus
Käyttäjän ohjaus ja oppiminen ohjelmistokehityksessä.

### Toiminnot
- **MentorAgent:** oppimissuunnitelma, aihepiirit
- **ExplainerAgent:** koodin selittäminen AST-pohjaisesti
- **PedagogyAgent:** oppimissuunnitelma (moduulit, viikot, harjoitukset)
- **ContentDesignerAgent:** sisällön luonti (quiz, exercise, tutorial, cheat_sheet, explanation)

---

## M12 — Learning & Assessment

**Tiedosto:** `agents/learning_path_agent.py`  
**Agentit:** `LearningPathAgent`, `AssessmentAgent`, `FeedbackAgent`  
**Status:** ✅ Valmiina  
**Testit:** 57 (kaikki läpäisti)

### Tarkoitus
Henkilökohtaiset oppimispolut ja arviointi.

### Toiminnot
- **LearningPathAgent:** oppimispolku (user_background, interests, prev_score, strategy)
- **AssessmentAgent:** kyselyt, koodihaasteet, projektiarviot
- **FeedbackAgent:** AST-pohjainen palaute (score 0–100)

---

## M13 — Knowledge & Memory

**Tiedosto:** `agents/knowledge_agent.py`  
**Agentit:** `KnowledgeAgent`, `MemoryAgent`, `ContextCompilerAgent`  
**Status:** ✅ Valmiina  
**Testit:** 64 (kaikki läpäisti)

### Tarkoitus
Tiedon ja muistin hallinta projektille.

### Toiminnot
- **KnowledgeAgent:** tiedon tallennus/haku/indeksointi
- **MemoryAgent:** istunto- ja pitkäaikaismuisti (TTL, tag-suodatus)
- **ContextCompilerAgent:** kontekstin kääntäminen AST-suodattareilla (imports, classes, functions, docstrings)

---

## M14 — Maintenance

**Tiedosto:** `agents/maintenance_agent.py`  
**Agentit:** `UpgradeAgent`, `CleanupAgent`, `DependencyAgent`  
**Status:** ✅ Valmiina  
**Testit:** 46 (kaikki läpäisti)

### Tarkoitus
Projektin ylläpito ja riippuvuustarkastus.

### Toiminnot
- **UpgradeAgent:** päivitystarkistus (`requirements.txt`, `pyproject.toml`)
- **CleanupAgent:** cachet, temp-tiedostot, build-tulokset (`space_freed`)
- **DependencyAgent:** riippuvuusanalyysi (tyhjennystutkimus, security-score)

---

## M15 — Release & Governance

**Tiedosto:** `agents/release_agent.py`  
**Agentit:** `ReleaseManagerAgent`, `ChangelogAgent`, `ComplianceAgent`  
**Status:** ✅ Valmiina  
**Testit:** 60 (88 % kattavuus)

### Tarkoitus
Julkaisujen hallinta ja yhteensopivuusvaatintojen tarkistus.

### Toiminnot
- **ReleaseManagerAgent:** semanttinen versiointi, julkaisuvaiheet (RELEASE_PHASES)
- **ChangelogAgent:** muutosloki (Keep a Changelog -muodossa)
- **ComplianceAgent:** lisenssi- ja standardintutkimus (GDPR, PCI-DSS, SOC2, HIPAA)

---

## M16 — Agent Engineering

**Tiedosto:** `agents/agent_engineering_agent.py`  
**Agentit:** `AgentDesignAgent`, `PromptOptimizerAgent`, `AgentFactoryAgent`  
**Status:** ✅ Valmiina  
**Testit:** 61 (85 % kattavuus)

### Tarkoitus
Uusien agenttien suunnittelu, prompt-optimitointi ja tehdasluonnin.

### Toiminnot
- **AgentDesignAgent:** agentin suunnittelu + validointi
- **PromptOptimizerAgent:** tokene-arviointi, rakenteen analyysi, parannusehdotukset
- **AgentFactoryAgent:** dynaaminen agentin luonti (`AGENT_REGISTRY`)

---

## M17 — AI Gateway

**Tiedosto:** `agents/ai_gateway_agent.py`  
**Agentit:** `AIGatewayAgent`, `LLMRouterAgent`, `TokenTrackerAgent`  
**Status:** ✅ Valmiina  
**Testit:** 58 (96 % kattavuus)

### Tarkoitus
Keskitetty AI-mallin käsittely ja tokenilasku.

### Toiminnot
- **AIGatewayAgent:** mallin reititys (OpenRouter, LangChain)
- **LLMRouterAgent:** kustannus/latency/capability-painotettu reittinta
- **TokenTrackerAgent:** tokenikulumien seurinta ja maksujen laskeminen

### Vakiot
`MODEL_REGISTRY` — yli 20 mallia (Claude, GPT-4, Llama, Mistral, jne.)

---

## M18 — Local LLM

**Tiedosto:** `agents/local_llm_agent.py`  
**Agentit:** `LocalModelAgent`, `ModelRunnerAgent`, `QuantizationAgent`  
**Status:** ✅ Valmiina  
**Testit:** 54 (89 % kattavuus)

### Tarkoitus
Paikallisten mallien (Ollama, llama.cpp, GGUF) hallinta ja optimointi.

### Toiminnot
- **LocalModelAgent:** mallien listaus/asennus/poisto/info/config
- **ModelRunnerAgent:** päätteen suoritus, benchmarkit, vertailut
- **QuantizationAgent:** kvantisointi (F32–Q8_0, 8 muotoa)

### Vakiot
`KNOWN_LOCAL_MODELS`, `QUANTIZATION_FORMATS`, `OLLAMA_COMMANDS`

---

## M19 — MCP & Integrations

**Tiedosto:** `agents/mcp_integration_agent.py`  
**Agentit:** `MCPIntegrationAgent`, `APIIntegrationAgent`, `WebhookAgent`  
**Status:** ✅ Valmiina  
**Testit:** 67 (95 % kattavuus)

### Tarkoitus
MCP-palvelinten yhteys, ulkoisten API-rajapintojen integrointi ja webhookien käsittely.

### Toiminnot
- **MCPIntegrationAgent:** MCP-palvelimet (connect, list_tools, call_tool, list_resources, read_resource)
- **APIIntegrationAgent:** REST/GraphQL API (request, test_connection, generate_client, parse_openapi)
- **WebhookAgent:** webhook-vastaanotto, SHA256 HMAC-vahvistus, prosessointi (receive, validate, process)

### Vakiot
`KNOWN_MCP_SERVERS` (6 palvelinta), `HTTP_METHODS`, `API_CLIENT_LANGUAGES`, `WEBHOOK_STATUSES`

---

## M20 — GUI / Control Center

**Tiedosto:** `agents/control_center_agent.py`  
**Agentit:** `ControlCenterAgent`, `DashboardAgent`, `CLIOrchestrator`  
**Status:** ✅ Valmiina  
**Testit:** 58 (99 % kattavuus)

### Tarkoitus
Keskitetty ohjauspaneeli, joka näyttää projektin tilan kokonaisuudessaan.

### Toiminnot
- **ControlCenterAgent:** listaa agentit/workflow-tilat, execute-toiminto reitittää komennot
- **DashboardAgent:** mittarit (system/quality), komponenttitila, hälytykset, suorituskykykaaviot
- **CLIOrchestrator:** CLI-komennon jäsentäminen, reitintaminen agentteihin, tab-completion, komentohistoria

### Vakiot
`CONTROL_CENTER_ACTIONS`, `DASHBOARD_ACTIONS`, `CLI_ORCHESTRATOR_ACTIONS`, `AGENT_STATES`, `WORKFLOW_STATES`, `ALERT_LEVELS`

---

## Moduulien yhteydet

```
M1 (Director) → M2 (Project) → M3 (Research) → M4 (Dev) → M5 (Testing)
                ↓                   ↓              ↓           ↓
              M14 (Upgrade)    M13 (Knowledge)  M8 (QA)    M6 (Security)
                ↓                   ↓              ↓           ↓
              M15 (Release)   M11 (Pedagogy)   M9 (Orchestrate)
                                      ↓              ↓
                                   M12 (Learning)  M10 (DevOps)
                                      ↓              ↓
                                   M16 (Agent Eng) M17 (Gateway)
                                      ↓              ↓
                                   M18 (Local LLM) M19 (MCP)
                                      ↓              ↓
                                   M20 (Control Center)
```
