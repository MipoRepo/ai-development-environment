# AIDE — Dataputki

**Generoitu:** 2026-09-03 | **Versio:** Alpha 2.10

---

## Miten data liikkuu AIDE:ssa

```
Käyttäjä
  │
  ▼
CLI (cli.py)
  │
  ▼
ControlCenterAgent (M20) ──► DashboardAgent (M20)
  │                              │
  │                              ▼
  │                      Järjestelmästatus
  │
  ▼
WorkflowOrchestratorAgent (M9)
  │
  │─────────────► Agentit M1–M19 (yksittäin tai putkekkain)
  │        │
  │        │
  │        ▼
  │      KnowledgeAgent (M13)  ◄── Tiedon tallennus/muisti
  │        │
  │        ▼
  │      AI Gateway (M17)      ◄── OpenRouter API
  │        │
  │        ▼
  │      Paikalliset LLM:t (M18)
  │
  ▼
MCP-palvelimet (M19) ◄── MCP-integraatio
  │
  ▼
Webhook-vastaanotto (M19) ──► Prosessointi → KnowledgeAgent (M13)
```

---

## 1. Käyttäjän syöte → Agenttiputki

1. Käyttäjä kirjoittaa komennon CLI:hin (esim. `aide run "Refaktoroi projekti"`).
2. CLI reitittää komennon:
   - Tyypillinen tehtävä → `DirectorAgent` (M1)
   - `init`-komento → `ProjectManagerAgent` + `RequirementsAgent` (M2)
   - `dashboard`-komento → `DashboardAgent` (M20)
3. Director hajottaa pyynnöksen → antaa alitehtävät agenteille.

---

## 2. Agentin sisäinen dataputki

```
AgentInput (Pydantic)
  │
  ▼
run()  ──► Orchestraatio (logging, stats, error handling)
  │
  ▼
_run() ──► Todellinen logiikka
  │        ├─ AI Gateway (M17) → OpenRouter API
  │        ├─ Paikallinen LLM (M18) → Ollama
  │        ├─ KnowledgeAgent (M13) → tiedon haku/tallennus
  │        └─ MCP (M19) → paikalliset työkalut
  │
  ▼
AgentOutput (Pydantic) ← Validoitu JSON
  │
  ▼
Paluu ketjeen: Director → CLIOrchestrator → käyttäjälle
```

---

## 3. Workflow-dataputki

```
base.yaml / bugfix.yaml / feature.yaml
  │
  ▼
WorkflowEngine (workflows/engine.py)
  │
  ├─ Vaihe 1: Requirements (M2)
  │
  ├─ Vaihe 2: Research (M3)
  │
  ├─ Vaihe 3: Development (M4)
  │
  ├─ Vaihe 4: Security Review (M6)
  │
  └─ Vaihe 5: Testing (M5/M8)
```

Jokainen vaihe päivittää yhteistä **kontekstia** (`context`), joka kulkee seuraavalle agentille.

---

## 4. Knowledge & Memory -putki

```
AgentInput
  │
  ▼
ContextCompilerAgent (M13) ──► AST-suodatus (imports, functions, classes, docstrings)
  │
  ▼
KnowledgeAgent (M13) ──► Tallennus (store/retrieve/search/index)
  │
  ▼
MemoryAgent (M13) ──► Istmuisti (session/short_term/long_term, TTL)
  │
  ▼
Paluu seuraavalle agentille kontekstina
```

---

## 5. API- ja MCP-integraatio

```
APIIntegrationAgent (M19)
  │
  ├─ HTTP-pyyntöjä (GET/POST/PUT/PATCH/DELETE)
  ├─ OpenAPI-spesifikaation parsinta
  ├─ Client-koodin generaatio (Python/TS/JS/Go/Rust/Java/curl)
  │
  ▼
MCPIntegrationAgent (M19)
  │
  ├─ Yhdistä MCP-palvelimiin (stdio/HTTP)
  ├─ Listaa työkalut ja resurssit
  ├─ Kutsuu työkaluja argumenteilla
  │
  ▼
WebhookAgent (M19)
  │
  ├─ Vastaanottaa webhook-payloadit
  ├─ SHA256 HMAC-vahvistus
  ├─ Prosessoi tapahtumat (push, pull_request, issues, ping)
  │
  ▼
KnowledgeAgent (M13) ──► Tallennus
```

---

## 6. DevOps ja deployment

```
Dockerfile / docker-compose.yaml (M10)
  │
  ▼
GitHub Actions (M10)
  │
  ├─ ci-cd workflow
  ├─ linting
  ├─ security audit
  │
  ▼
DeploymentAgent (M10)
  │
  ├─ Strategy: docker-swarm | kubernetes | aws-ecs | static
  └─ Deploy-vaiheiden ohjeet
```

---

## 7. Control Center - näkymä

```
ControlCenterAgent (M20)
  │
  ├─ Listaa agentit + satus
  ├─ Listaa workflow-tilat
  ├─ Järjestelmän terveys (health_check)
  ├─ Komponenttitila (DATABASE, REDIS, WORKERS, ...)
  │
  ▼
DashboardAgent (M20)
  │
  ├─ System metrics (agent_count, workflow_count, ...)
  ├─ Quality metrics (total_tests, test_coverage, ...)
  ├─ Hälytykset (info, warning, critical, resolved)
  ├─ Suorituskyky (avg_response_time, p95, ...)
  │
  ▼
CLIOrchestrator (M20)
  │
  ├─ Parsii komennot
  ├─ Reitittää agentteihin
  ├─ Tab-completion
  └─ Komentohistoria (50 kpl)
```

---

## Data-muodot

| Lähetin | Vastaanottaja | Muoto | Skeema |
|---|---|---|---|
| Käyttäjä | CLI | CLI-arg | `cli.py` |
| CLI | DirectorAgent | `AgentInput` | `run(action, query, ...)` |
| DirectorAgent | MultiAgentCoordinator (M9) | `CoordinationInput` | `agents, dependencies, context` |
| WorkflowOrchestratorAgent | Agentit M2–M19 | `AgentInput` | `action, query, context_data` |
| Agentit → KnowledgeAgent | KnowledgeAgent | `KnowledgeAgentInput` | `action, content, tags, knowledge_id` |
| Agentit → AI Gateway | AIGatewayAgent | `AIGatewayInput` | `action, query, model, ...` |
| APIIntegrationAgent | WebhookAgent | `WebhookInput` | `action, event_type, signature, payload` |
| MCPIntegrationAgent | resurssit | `MCPIntegrationOutput` | `data, metadata, resources` |
| Kaikki agentit | ControlCenterAgent | `ControlCenterOutput` | `status, agents, metrics, ...` |

Katso myös [`agent-lifecycle.md`](agent-lifecycle.md) agentin elinkierroksesta.
