---
name: project-rules
description: AIDE-projektin yleiset säännöt ja päätökset
type: reference
---

# AIDE-projektin säännöt ja päätökset

- ✅ AINA käytä Python ≥3.11.
- ✅ AINA käytä MkDocs-versiota 1.5.x (EI 1.6 tai uudempaa).
- ❌ Älä koskaan committaa .env-tiedostoa.
- Testikattavuuden tulee olla vähintään 80 % jokaisessa moduulissa.
- Jokaisen agentin tulee olla Pydantic-validoitu JSON-output.
- CLI-kirjasto (M2:ssa): `Typer`.
- AI-mallikäänti: käytetään `langchain` + `openai`-kirjastoja OpenRouterin kautta.
- OpenRouter-API-avaimen lukeminen `OPENROUTER_API_KEY`-ympäristömuuttujasta `.env`-tiedostosta.
- Testauskirjasto: `pytest` + `pytest-asyncio` + `pytest-cov`.
- Versiokäytäntö: Alpha 1.x → Alpha 1.x+0.1 (korjaukset) → Beta 1.0 (M2–M7) kun käyttäjä kääntää sen käyttöön.

## Versio- ja ohjeistusmuisti

- **Versio:** Alpha 1.0 (M1 Core & Director) on **VALMIS** ✅
  - Kaikki moduulit toteutettu ja testattu (86 testiä, 94 % kattavuus)
  - CLI toimii: `aide init`, `aide run --dry-run`, `aide status`
  - Workflowt: base, bugfix, feature
  - `.env.example`, `project-rules.md` ja muistit luodut
- **Versio:** Alpha 1.1 (M2 Project Management) on **VALMIS** ✅
  - M2 toteutettu: schemas/project.py (Pydantic-mallit), ProjectManagerAgent, RequirementsAgent
  - CLI `init` integroi RequirementsAgent + ProjectManagerAgent (agentit lukevat parametrit, luo rakenteen ja dokumentaation)
  - Testit: 30 uutta (test_project_manager.py + test_project_init.py), 116 yhteensä, 94 % kattavuus
  - CLI `--version` päivitetty Alpha 1.2:ksi
- **Versio:** Alpha 1.2 (M3 Research) on **VALMIS** ✅
  - M3 toteutettu: agents/researcher_agent.py (ResearcherAgent, TechnologyResearcherAgent)
  - ResearcherAgent analysoi tiedostoja (AST-parsimus), havaitsee teknologiat, rakentaa rakenteen
  - TechnologyResearcherAgent antaa suosituksia teknologioita
  - Testit: 32 uutta (test_research_agents.py), 148 yhteensä, 94 % kattavuus
- **Versio:** Alpha 1.3 (M4 Development) on **VALMIS** ✅
  - M4 toteutettu: agents/developer.py (DeveloperAgent, RefactoringAgent, CodeReviewAgent)
  - DeveloperAgent generoi koodia (Python/JS/Markdown), luo/täydentää tiedostoja
  - RefactoringAgent analysoi puuttuvat doksekeinnot, käyttämättomat importit, pitkät funktiot
  - CodeReviewAgent skannaa turvallisuusongelmat (eval, exec, salasana, shell=True) ja laadun (bare except, import *)
  - Testit: 32 uutta (test_developer_agent.py), 180 yhteensä, 94 % kattavuus
- **Versio:** Alpha 1.4 (M5 Testing) on **VALMIS** ✅
  - M5 toteutettu: agents/testing_agent.py (TestDesignerAgent, TesterAgent, QAAgent)
  - TestDesignerAgent suunnittelee testit AST-parsimuksen avulla
  - TesterAgent suorittaa pytest-komennon subprocessillä ja parsii tulosteen
  - QAAgent tarkistaa koodikattavuuden, testitiedostot ja ohjelmointikäytännöt
  - Testit: 24 uutta (test_testing_agents.py), 204 yhteensä, 94 % kattavuus
- **Versio:** Alpha 1.5 (M6 Security) on **VALMIS** ✅
  - M6 toteutettu: agents/security_agent.py (SecurityReviewAgent, SASTAgent, DependencySecurityAgent, SecretsAgent, ContainerSecurityAgent)
  - SecurityReviewAgent: regex-pohjainen turvallisuusskanningi (eval, exec, shell=True, pickle, kiinteät salasanat, SQL-injektiota, HTTP)
  - SASTAgent: AST-pohjainen analyysi (koodinjäte, vaaralliset importit, funktiolukumuoto)
  - DependencySecurityAgent: haavoittuvamien pakettien tarkistus + pip-audit päivitystarkistus
  - SecretsAgent: AWS-keys, GitHub-tokenit, API-avaimet, salaisuusavaimet, Bearer-tokenit, .env-skannaus
  - ContainerSecurityAgent: Dockerfile-turvallisuus (root-käyttäjä, ADD, chmod 777, EXPOSE 22, curl|sh, --no-install-recommends, HEALTHCHECK)
  - Testit: 40 uutta (test_security_agents.py), 244 yhteensä, 94 % kattavuus
- **Versio:** Alpha 1.6 (M7 Documentation) on **VALMIS** ✅
  - M7 toteutettu: agents/documentation_agent.py (TechnicalWriterAgent, APIDocumentationAgent, UserDocumentationAgent, MkDocsAgent)
  - TechnicalWriterAgent: generoi PROJECT.md, AGENTS.md, ARCHITECTURE.md projektille
  - APIDocumentationAgent: AST-pohjainen API-endpointin analyysi, OpenAPI-3.0-schema, markdown-dokumentaatio
  - UserDocumentationAgent: README-generointi (ominaisuudet, asennus, käyttö, testaus)
  - MkDocsAgent: mkdocs.yml-generointi, nav-konfiguurointi, oletussivut (index/api/user-guide)
  - Testit: 46 uutta (test_documentation_agents.py), 290 yhteensä, 94 % kattavuus
- **Versio:** Alpha 1.7 (M8 Testing Automation) on **VALMIS** ✅
  - M8 toteutettu: agents/testing_automation_agent.py (TestRunnerAgent, PerformanceTestAgent, IntegrationTestAgent)
  - TestRunnerAgent: pytest-subprosessi, coverage-analyysi, fail-fast, output-parseri
  - PerformanceTestAgent: benchmarkit, warmup, percentile-laskenta (p95)
  - IntegrationTestAgent: moduulien tuonti, cross-module-riippuvuudet, pisteytetty analyysi
  - Testit: 37 uutta (test_testing_automation_agent.py), 327 yhteensä, 91 % kattavuus
- **Versio:** Alpha 1.8 (M9 Orchestration) on **VALMIS** ✅
  - M9 toteutettu: agents/orchestration_agent.py (WorkflowOrchestratorAgent, MultiAgentCoordinator)
  - WorkflowOrchestratorAgent: workflow-orkesterointi (vaiheiden suoritus, kontekstin päivitys, stop_on_error, max_phases)
  - MultiAgentCoordinator: topologinen järjestys riippuvuuksien mukaan (Kahnin algoritmi), moniagentti-koordinaatio
  - Testit: 30 uutta (test_orchestration_agent.py), 357 yhteensä, 91 % kattavuus

- **Versio:** Alpha 1.9 (M10 DevOps) on **VALMIS** ✅
  - M10 toteutettu: agents/devops_agent.py (DockerAgent, CI_CDAgent, InfrastructureAgent, DeploymentAgent)
  - DockerAgent: luo Dockerfile + docker-compose.yaml projekti-tyypin mukaan (python-api, web-app, cli, default); turvallisuuspistemäärä + suositukset
  - CI_CDAgent: luo GitHub Actions -workflowit (ci-cd, linting, security) Python-versiomasaulasta
  - InfrastructureAgent: analysoi infra-tiedostot, riippuvuudet, generoi parannussuositukset, laskema complexity_score
  - DeploymentAgent: deploy-strategiat (docker-swarm, kubernetes, aws-ecs, static) + deploy-vaiheiden ohjeet
  - Testit: 63 uutta (test_devops_agent.py), 420 yhteensä, kaikki läpäisti

- **Versio:** Alpha 1.10 (M11 Pedagogy) on **VALMIS** ✅
  - M11 toteutettu: agents/pedagogy_agent.py (MentorAgent, ExplainerAgent, PedagogyAgent, ContentDesignerAgent)
  - MentorAgent: opettaa käyttäjälle ohjelmistokehitystä, suosii aihepiirrejä skill_levelin ja LEARNING_TOPICSin perusteella
  - ExplainerAgent: selittää koodin AST-parsimuksen ja EXPLANATION_PROMPTS-glien avulla; tukee myös rikkinäisen koodin käsittelyä
  - PedagogyAgent: rakentaa oppimissuunnitelman (moduulit, viikot, harjoitukset, resurssit) ja ottaa user_background-profiilin
  - ContentDesignerAgent: luo sisältöä (quiz, exercise, tutorial, cheat_sheet, explanation) num_items ja context_text-parametrien avulla
  - Korjaukset: context→context_text-nimikäännös, LEARNING_LEVELS-tyhjennysten poisto, ast.parse()-tarkistus rikkinäiselle koodille
  - Testit: 68 uutta (test_pedagogy_agents.py), 488 yhteensä, kaikki läpäisti

- **Versio:** Alpha 2.2 (M12 Learning & Assessment) on **VALMIS** ✅
  - M12 toteutettu: agents/learning_path_agent.py (LearningPathAgent, AssessmentAgent, FeedbackAgent)
  - LearningPathAgent: suunnittelee henkilökohtaiset oppimispolut user_background, interests, prev_score ja strategy-parametrien avulla; laskee progress_percentage ja antaa next_recommendations
  - AssessmentAgent: luo kyselyjä (quiz), koodihaasteita (coding_challenge), projektiarvioituksia (project_review) ja peer_reviewit; säätää vaikeutta previous_scores-pisteidem
  - FeedbackAgent: antaa AST-pohjaista palautetta koodinrakennetta varten; tukee code_review, learning, style, performance-tyyppejä; laskee score 0–100 ja antaa parannusehdotukset
  - Tietomallit: LearningPathAgentInput/Output, AssessmentInput/Output, FeedbackInput/Output + PATH_STRATEGIES ja ASSESSMENT_CRITERIA -sanakirjät
  - Testit: 57 uutta (test_learning_path_agent.py, test_assessment_agent.py, test_feedback_agent.py), 545 yhteensä, kaikki läpäisti

- **Versio:** Alpha 2.3 (M13 Knowledge & Memory) on **VALMIS** ✅
  - M13 toteutettu: agents/knowledge_agent.py (KnowledgeAgent, MemoryAgent, ContextCompilerAgent)
  - KnowledgeAgent: tiedon tallennus, haku ja indeksointi (store, retrieve, search, index, delete); automaattiset tunnisteet; tiedostopohjainen persistenssi
  - MemoryAgent: istunto- ja pitkäaikaisuuden muistit (session, short_term, long_term); TTL, tag-suodatus, forget, clear; tiedostopohjainen persistenssi
  - ContextCompilerAgent: kontekstin kääntäminen lähteistä (files/strings); AST-suodattimet (imports, classes, functions, errors, docstrings, constants); json/markdown/text/summary-muodot; prioriteetit ja max_context_length
  - Tietomallit: KnowledgeAgentInput/Output, MemoryInput/Output, ContextCompilerInput/Output + INDEX_TYPES ja MEMORY_STORE_TYPES
  - Korjaukset: knowledge_id kenttä KnowledgeAgentInput:iin lisätty; total_found MemoryOutput:iin lisätty; TTL-vanheneminen korjattu
  - Testit: 64 uutta (test_knowledge_agent.py, test_memory_agent.py, test_context_compiler_agent.py), 609 yhteensä, kaikki läpäisti

- **Versio:** Alpha 2.4 (M14 Maintenance) on **VALMIS** ✅
  - M14 toteutettu: agents/maintenance_agent.py (UpgradeAgent, CleanupAgent, DependencyAgent)
  - UpgradeAgent: päivitystarkistus (check/upgrade/dry_run); tukee requirements.txt ja pyproject.toml (tomllib); automaattiset päivityskomennot
  - CleanupAgent: poistaa cachet (__pycache__, .pytest_cache, .mypy_cache), temp-tiedostot (.bak, .tmp) ja build-tulokset (dist, build); space_freed-laskelut
  - DependencyAgent: riippuvuusanalyysi (requirements.txt, pyproject.toml, package.json); turvallisuustarkastus; vanhentuneiden pakettien tarkistus; riippuvuussolmut
  - Tietomallit: UpgradeAgentInput/Output, CleanupAgentInput/Output, DependencyAgentInput/Output + MAINTENANCE_ACTIONS, CACHE_DIRS, DEPENDENCY_FILES
  - Korjaus: pyproject_parser tilalle tomllib (sisäänrakennettu Python 3.11:ssa); upgradable_packages tyypitys list[dict[str, Any]]; _parse_requirement palauttaa tyhjän version ilman versiomäärää
  - Testit: 46 uutta (test_maintenance_agent.py), 655 yhteensä, kaikki läpäisti

- **Versio:** Alpha 2.5 (M15 Release & Governance) on **VALMIS** ✅
  - M15 toteutettu: agents/release_agent.py (ReleaseManagerAgent, ChangelogAgent, ComplianceAgent)
  - ReleaseManagerAgent: versiointi (major/minor/patch), julkaisuvaiheet (RELEASE_PHASES), deploy-strategiat (DEPLOYMENT_STRATEGIES); plan/execute/validate/bump_version-toiminnot
  - ChangelogAgent: changelog-generointi muutoksista (feature/fix/change/remove/deprecated/security); Keep a Changelog / markdown / unreleased -muodot; muutosten ryhmittely ja lukumäärä
  - ComplianceAgent: lisenssi- ja standardintutkimus (MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, proprietary; GDPR, PCI-DSS, SOC2, ISO 27001, HIPAA); compliance_score, recommendations
  - Tietomallit: ReleaseManagerInput/Output, ChangelogInput/Output, ComplianceInput/Output + RELEASE_PHASES, DEPLOYMENT_STRATEGIES, LICENSE_TYPES, REGULATORY_STANDARDS
  - Päivitetty `agents/__init__.py` kaikilla M15-viehimilla ja -vakioilla
  - Testit: 60 uutta (test_release_agent.py), 715 yhteensä, kaikki läpäisti, 88 % kattavuus

- **Versio:** Alpha 2.6 (M16 Agent Engineering) on **VALMIS** ✅
  - M16 toteutettu: agents/agent_engineering_agent.py (AgentDesignAgent, PromptOptimizerAgent, AgentFactoryAgent)
  - AgentDesignAgent: suunnittelee ja validoi uusia agenteja; agent_name, agent_type, capabilities, syöte/tuloste-skeemat; design/analyze/validate/recommend-toiminnot
  - PromptOptimizerAgent: optimoi prompteja; tokenien arviointi, rakenteen analyysi, parannusehdotukset, optimointipisteet; optimize/analyze/estimate/suggest-toiminnot
  - AgentFactoryAgent: luo agentteja instansseja dynaamisesti; classi‑level AGENT_REGISTRY; create/register/list/instantiate-toiminnot
  - Tietomallit: AgentDesignInput/Output, PromptOptimizerInput/Output, AgentFactoryInput/Output + AGENT_DESIGN_ACTIONS, PROMPT_OPTIMIZE_ACTIONS, AGENT_FACTORY_ACTIONS, KNOWN_AGENT_TYPES, SCHEMA_FIELDS, PROMPT_OPTIMIZATION_TIPS
  - Päivitetty `agents/__init__.py` kaikilla M16-viehimilla ja -vakioilla
  - Testit: 61 uutta (test_agent_engineering_agent.py), 776 yhteensä, kaikki läpäisti, 85 % kattavuus
- **Versio:** Alpha 2.7 (M17 AI Gateway) on **VALMIS** ✅
  - M17 toteutettu: agents/ai_gateway_agent.py (AIGatewayAgent, LLMRouterAgent, TokenTrackerAgent)
  - AIGatewayAgent: keskitetty AI-mallin käsittely (OpenRouter, LangChain, mallien vaihto); route/process/health_check-toiminnot
  - LLMRouterAgent: reitittää pyynnöt oikeaan malliin (kustannus, latency, capability-tasapaino); ROUTING_CRITERIA
  - TokenTrackerAgent: seuraa tokenikulumit ja maksut; track/summarize/reset-toiminnot
  - Vakioita: GATEWAY_ACTIONS, ROUTING_CRITERIA, TOKEN_TRACKER_ACTIONS, MODEL_REGISTRY (20+ mallia)
  - Testit: 58 uutta (test_ai_gateway_agent.py), 834 yhteensä, 96 % kattavuus
- **Versio:** Alpha 2.8 (M18 Local LLM) on **VALMIS** ✅
  - M18 toteutettu: agents/local_llm_agent.py (LocalModelAgent, ModelRunnerAgent, QuantizationAgent)
  - LocalModelAgent: paiklisten mallien (Ollama, llama.cpp, GGUF) hallinta; list/install/remove/info/config-toiminnot
  - ModelRunnerAgent: suorittaa päätettä paikallisissa malleissa; run/benchmark/compare-toiminnot
  - QuantizationAgent: kvantisoi ja optimoi malleja; quantize/analyze/recommend-toiminnot; 8 GGUF-muotoa (F32–Q8_0)
  - Vakioita: LOCAL_MODEL_ACTIONS, MODEL_RUNNER_ACTIONS, QUANTIZATION_ACTIONS, KNOWN_LOCAL_MODELS, QUANTIZATION_FORMATS, MEMORY_ESTIMATES, OLLAMA_COMMANDS
  - Testit: 54 uutta (test_local_llm_agent.py), 888 yhteensä, 89 % kattavuus
- **Versio:** Alpha 2.9 (M19 MCP & Integrations) on **VALMIS** ✅
  - M19 toteutettu: agents/mcp_integration_agent.py (MCPIntegrationAgent, APIIntegrationAgent, WebhookAgent)
  - MCPIntegrationAgent: MCP-palvelinten yhdistäminen, työkalujen ja resurssien listaus/käsittely; connect/list_tools/call_tool/list_resources/read_resource/health_check-toiminnot
  - APIIntegrationAgent: ulkoisten REST/GraphQL API-rajapintojen integrointi; request/test_connection/generate_client/parse_openapi-toiminnot; 7 kieltä client-koodin generointiin
  - WebhookAgent: webhook-jen vastaanotto, SHA256 HMAC-vahvistus, prosessointi eri tapahtumityypeille; receive/validate/process/list_endpoints-toiminnot
  - Vakioita: MCP_INTEGRATION_ACTIONS, API_INTEGRATION_ACTIONS, WEBHOOK_ACTIONS, KNOWN_MCP_SERVERS (6 palvelinta), RESOURCE_TYPES, HTTP_METHODS, API_CLIENT_LANGUAGES, WEBHOOK_STATUSES, OPENAPI_VERSIONS, MCP_CONNECTION_STATUS
  - Testit: 67 uutta (test_mcp_integration_agent.py), 955 yhteensä, 95 % kattavuus

- **Versio:** Alpha 2.10 (M20 GUI / Control Center) on **VALMIS** ✅
  - M20 toteutettu: agents/control_center_agent.py (ControlCenterAgent, DashboardAgent, CLIOrchestrator)
  - ControlCenterAgent: keskitetty ohjauspaneeli; listaa agentit, työkalu-, workflow-tilat, järjestelmän terveyttä, komennosyyt; execute-toiminto reitittää agentit
  - DashboardAgent: visuaaliset mittarit, järjestelmä-/laadun metriikat, komponenttitila, hälytykset, suorituskyky; metrics/status/alerts/performance-toiminnot
  - CLIOrchestrator: CLI-komennon jäsentäminen, reittien mukainen ohjaus agentteihin, tab-completions, komentohistoria; parse/route/execute/suggest/history-toiminnot
  - Vakioita: CONTROL_CENTER_ACTIONS, DASHBOARD_ACTIONS, CLI_ORCHESTRATOR_ACTIONS, SYSTEM_COMPONENTS, COMMAND_ROUTES, AGENT_STATES, WORKFLOW_STATES, METRIC_CONNECTIONS, ALERT_LEVELS, CLI_HELP_TEXT
  - Korjaus: test_control_center_routes_to_agents-testi päivitetty tarkistaamaan ControlCenterAgent, DashboardAgent ja agenttilistan kokoa (>10), koska CLIOrchestrator jää [20]-rajonnan ulkopuolelle aakkosellisessa järjestyksessä

Siihen liittyvät muistit:
- [[mcp-integrations-m19]]
- [[agent-architecture]]
- [[workflow-design]]
- [[release-agents-m15]]
