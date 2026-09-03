# CLIOrchestrator (M20 Control Center)

**Tiedosto:** `agents/control_center_agent.py`  
**Moduuli:** M20 — Control Center  
**Status:** ✅ Valmiina  
**Testit:** 58 | **Kattavuus:** 92 %

---

## Tarkoitus

Pääkäskyjärjestelyn reittääminen AIDE-agenttien välillä. Käsittelee CLI-argumentit, reitittää subcommandit oikeisiin agentteihin `MODULE_REGISTRY`-importin kautta ja tukee `--help`, `--list-agents` ja monimutkaisia parametrien parseja.

---

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"cli_orchestrator"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `route` | Reititä CLI-komento oikeaan agenttiin |
| `help` | Näytä käyttöohjeet |
| `list_agents` | Lista kaikki rekisteröityt agentit |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["route", "help", "list_agents"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | CLI-komento |
| `args` | `dict[str, Any]` | ❌ | Lisäargumentit |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `routed_to` | `str` | Mihin agenttiin reitittyi |
| `response` | `dict[str, Any]` | Agentin vastaus |
| `available_commands` | `list[str]` | Saatavilla olevat komennot |
| `help_text` | `str` | Apunteksti |
| `agents` | `list[dict[str, Any]]` | Rekisteröityt agentit |
| `message` | `str` | Tilanneilmoitus |

---

## CLI-komennot

| Komento | Kuvaus | Reititetty agenttiin |
|---|---|---|
| `aide [agent] [query]` | Agentin suoritus | Tietty agentti |
| `aide list-agents` | Lista agentit | CLIOrchestrator |
| `aide help` | Näytä apu | CLIOrchestrator |
| `aide metrics` | Järjestelmänmetriikit | ControlCenterAgent |
| `aide health` | Järjestelmänterveys | ControlCenterAgent |
| `aide dashboard` | Dashboard-näytön renderöinti | DashboardAgent |
| `aide monitor` | Webhookin vastaanotto | WebhookAgent |

---

## MODULE_REGISTRY

CLIOrchestrator käyttää lazy importia `MODULE_REGISTRY`-dictistä, joka kartoittaa agentin nimen agentin luokkaan:

| Avain | Luokka |
|---|---|
| `knowledge` | KnowledgeAgent (M1) |
| `task` | TaskPlannerAgent (M2) |
| `code_review` | CodeReviewAgent (M3) |
| `test` | TesterAgent (M4) |
| `doc` | TechnicalWriterAgent (M5) |
| `workflow` | WorkflowAgent (M6) |
| `mcp` | MCPIntegrationAgent (M19) |
| `api` | APIIntegrationAgent (M19) |
| `webhook` | WebhookAgent (M19) |
| `control` | ControlCenterAgent (M20) |
| `dashboard` | DashboardAgent (M20) |

Importti tapahtuu lazy-moodissa (importlib) importtikiertorakenteen välttämiseksi.

---

## Esimerkkikoodi

```python
from agents import CLIOrchestrator

orchestrator = CLIOrchestrator()

# Reititä komento
result = orchestrator.run(
    action="route",
    query="knowledge Kerro Dockerin perustuksista"
)

print(f"Reititty: {result.routed_to}")
# Output: Reititty: knowledge

print(result.response)
# Output: {'success': True, 'response': 'Docker on...' }

# Lista agentit
result = orchestrator.run(
    action="list_agents",
    query="*"
)

for a in result.agents:
    print(f"  {a['name']}: {a['type']}")

# Apunteksti
result = orchestrator.run(
    action="help",
    query="general"
)
print(result.help_text)
```

---

## Reitityslogiikka

```
aide [subcommand] [query] [--key=value]

1. Parsitaan subcommand (esim. "knowledge")
2. Etsitään MODULE_REGISTRY:stä
3. Lazy-importataan agentti
4. Agentin .run() kutsu kyselyllä ja parametreillä
5. Vastaus palautetaan JSON-muodossa
```

---

## Testikattavuus

M20-testit (58) sisältävät:
- `test_cli_orchestrator_routes_to_correct_agent`
- `test_cli_orchestrator_handles_args`
- `test_list_agents_returns_all`
- `test_help_returns_help_text`
- `test_route_with_unknown_agent`
- `test_control_center_routes_to_agents`

---

## Liittyvät moduulit

- **Käyttää:** kaikkia AIDE-agentteja (M1–M20) `MODULE_REGISTRY`-importin kautta
- **Tarjoaa:** pääkäskyliittymän (`cli.py`) agenttien välillä

## CLI-käyttö

```bash
aide knowledge "Missä on projektin TODO-lista?"
aide code_review --file src/main.py
aide doc "Kirjoita API-ohjeet"
aide test  # automaattinen testaustasoite
aide workflow "uusi projekti"
```
