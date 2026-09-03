# Agentit — Yleiskatsaus

Tämä on keskuspolkunavi AIDE-järjestelmän kaikista agenteista. Valitse kategoria alla olevista linkeistä saadaksesi tarkemman tiedon kultakaikilta agenteilta.

## Moduulijako (Alpha 1.x → 2.x)

Agentit on järjestelty 20 moduuliin (M1–M20). Alla on lyhyt yhteenveto kultakaikilta:

| Moduuli | Aihe | Agentit | Status |
|---|---|---|---|
| **M1** | Core | ResearcherAgent | ✅ |
| **M2** | Development | DeveloperAgent, TaskPlannerAgent | ✅ |
| **M3** | Director | DirectorAgent | ✅ |
| **M4** | Project Manager | ProjectManagerAgent | ✅ |
| **M5** | Tester | TesterAgent, QAGent | ✅ |
| **M6** | Technical Writer | TechnicalWriterAgent, APIDocumentationAgent, UserDocumentationAgent | ✅ |
| **M7** | Security | SecurityArchitectAgent | ✅ |
| **M8** | Testing Automation | TestRunnerAgent, PerformanceTestAgent, IntegrationTestAgent | ✅ |
| **M9** | Orchestration | MultiAgentCoordinatorAgent, WorkflowOrchestratorAgent | ✅ |
| **M10** | DevOps | CI_CDAgent, DeploymentAgent, DockerAgent, InfrastructureAgent | ✅ |
| **M11** | Pedagogy | PedagogyAgent, ContentDesignerAgent, ExplainerAgent, MentorAgent, LearningPathAgent | ✅ |
| **M12** | Learning & Assessment | AssessmentAgent, FeedbackAgent, LearningPathAgent | ✅ |
| **M13** | Knowledge & Memory | KnowledgeAgent, MemoryAgent, ContextCompilerAgent | ✅ |
| **M14** | Maintenance | CleanupAgent, DependencyAgent, UpgradeAgent | ✅ |
| **M15** | Release & Governance | ReleaseManagerAgent, ChangelogAgent, ComplianceAgent | ✅ |
| **M16** | Agent Engineering | AgentDesignAgent, AgentFactoryAgent, PromptOptimizerAgent | ✅ |
| **M17** | AI Gateway | AIGatewayAgent, LLMRouterAgent, TokenTrackerAgent | ✅ |
| **M18** | Local LLM | LocalModelAgent, ModelRunnerAgent, QuantizationAgent | ✅ |
| **M19** | MCP & Integrations | MCPIntegrationAgent, APIIntegrationAgent, WebhookAgent | ✅ |
| **M20** | Control Center | ControlCenterAgent, DashboardAgent, CLIOrchestrator | ✅ |

## Ryhmitellyt agentit

### Pääosastot

- [DirectorAgent (M3)](core/director.md) — järjestelmän orkestrointi
- [ProjectManagerAgent (M4)](core/project-manager.md) — projektinhallinta
- [ResearcherAgent (M1)](core/researcher.md) — tiedonhaku

### Devaus

- [DeveloperAgent (M2)](development/developer.md) — koodin generointi ja refaktorointi
- [CodeReviewAgent (M4)](development/code-review.md) — turvallisuus- ja laadun tarkistus

### Testaus

- [TesterAgent (M5)](testing/testing_agent.md) — testien suunnittelu ja suoritus
- [TestRunnerAgent (M8)](testing/testing_automation_agent.md) — testiautomaatio

### Dokumentaatio

- [TechnicalWriterAgent (M6)](documentation/documentation.md) — tekninen dokumentaatio
- [MkDocsAgent (M7)](documentation/documentation.md) — sivuston generointi

### Turvallisuus

- [SecurityArchitectAgent (M7)](security/security.md) — turvallisuusdesigni
- [ContainerSecurityAgent (M7)](security/security.md) — Dockerfile-turvallisuus

### AI Gateway & LLM

- [AIGatewayAgent (M17)](ai_gateway/gateway.md) — mallien reittäminen
- [LocalModelAgent (M18)](local_llm/local_model.md) — paikalliset mallit

### MCP & Integrations

- [MCPIntegrationAgent (M19)](mcp/mcp_integration.md) — MCP-palvelimet
- [WebhookAgent (M19)](mcp/webhook.md) — webhook-käsittely

### Control Center

- [ControlCenterAgent (M20)](control_center/control_center.md) — järjestelmänvalvonta
- [CLIOrchestrator (M20)](control_center/cli_orchestrator.md) — CLI-reititys

[Lisää moduulidokumentit →](../architecture/modules.md)
