# AIDE — AI Development Environment

> **Claude Code -projekti** • Python 3.11+ • Pydantic-validoidut agentit • pytest-testit (1013 kpl)

## Projektin yleiskuva

AIDE (AI Development Environment) on 20-moduulinen agenttipohjainen Python-kehitysympäristö. Jokainen moduuli (M1–M20) sisältää 2–3 Pydantic-agenttia, joilla on tarkat sisääntulostulot. Kaikki agentit perivät `BaseAgent`-luokan (`agents/base.py`), joka validoi syyt Pydantic-malleilla ennen ja jälkeen `_run()`-metodia.

### Arkkitehtuuri

```
aide/
├── agents/           # 20 moduulia, 50+ agenttiluokkaa (M1-M20)
│   ├── base.py       # BaseAgent, AgentInput, AgentOutput (PERUSLUOKKA)
│   ├── __init__.py   # Kaikki viennit ja vakiot
│   ├── knowledge_agent.py       # M13: Knowledge/Memory/ContextCompiler
│   ├── maintenance_agent.py     # M14: Upgrade/Cleanup/Dependency
│   └── ... (18 muuta)
├── schemas/
│   ├── project.py    # ProjectType, ProjectTemplate, Priority, ProjectSpec, ProjectPlan
│   └── ...
├── tests/            # 1013 testiä (pydanti + pytest-asyncio)
├── site/             # MkDocs-dokumentaatio (site/*.html)
└── tools/            # CLI-työkalut
```

### Moduulit

| Moduuli | Kuvaus | Agentit | Testit |
|---------|--------|---------|--------|
| M1 | Core & Director | DirectorAgent | 86 |
| M2 | Project Management | RequirementsAgent | 116 |
| M3-M7 | Research, Development, Security, Documentation | useat | 290 |
| M8 | Testing Automation | TestRunnerAgent, PerformanceTestAgent | 327 |
| M9 | Orchestration | WorkflowOrchestratorAgent | 357 |
| M10 | DevOps | MonitoringAgent, LoggingAgent | 420 |
| M13 | Knowledge & Memory | KnowledgeAgent, MemoryAgent, ContextCompilerAgent | 609 |
| M14 | Maintenance | UpgradeAgent, CleanupAgent, DependencyAgent | 655 |
| M15-M20 | Release, Agent Engineering, AI Gateway, Local LLM, MCP, GUI | useat | 1013 (yht.) |

## Kehityssäännöt

- **Python**: >= 3.11 (Käytetään `tomllib`-moduulia M14:ssa)
- **Riippuvuudet**: MkDocs 1.5.x, Pydantic, pytest + pytest-asyncio + pytest-cov
- **Versio**: Alphaversion (Alpha X.Y)
- **Testaus**: Kaikki agentit pakollinen testikansiollisuus — aina ennen committia ajetaan `pytest`

## Claude Code -työtyyt

Tämä projekti käyttää:
- **Muistitiedostoja** (`.claude/memories/`) — moduulikohtaiset yhteenvetot (katso `MEMORY.md`)
- **Taitoja** (`.claude/skills/`) — slash-komennot kehitystehtäviin
- **Agentteja** (`.claude/agents/`) — natiivit Claude Code -agentit
- **Koukkuja** (`.claude/hooks/`) — automaatiota tallenna/siirry -hetkillä
- **asettauksia** (`.claude/settings.local.json`) — tarkat suoritusoikeudet

## Työkalut

| Komento | Kuvaus |
|---------|--------|
| `.venv/Scripts/python -m pytest tests/ -v` | Aja kaikki testit |
| `/run-tests M13` | Aja vain M13-testit (skill) |
| `/doc-sync` | Synkkaa dokumentaatio (skill) |
| `/code-review` | Katseloija agentti (agentti) |

## Muistutus

- **Muistitiedostot**: `.claude/memories/` — projektimuistit, joko `project`- tai `reference`-tyyppiä
- **Muisti-indeksi**: `MEMORY.md` — kaikki muistit on listattu tässä
- **Muistamuodon**: YAML-frontmatter (`name`, `description`, `metadata.type`) + sisältö (`**Miksi:**`, `**Kuinka sovellettavaksi:**`)
