# ControlCenterAgent & DashboardAgent (M20 Control Center)

**Tiedosto:** `agents/control_center_agent.py`  
**Moduuli:** M20 — Control Center  
**Status:** ✅ Valmiina  
**Testit:** 58 | **Kattavuus:** 92 %

---

## Tarkoitus

Kaksi integroitu agenttia järjestelmän yläkokoonnan valvoimiseen ja kontrollaan. ControlCenterAgent tarjoaa järjestelmätunnukset (metriikat, terveys, resurssit) ja agentitietueen, kun DashboardAgent renderöi interaktiivisen tekstipohjaisen näytön näillä tiedoilla.

---

## ControlCenterAgent

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"control_center"` |

### Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `metrics` | Palauttaa järjestelmänmetriikut |
| `health` | Palauttaa järjestelmän terveys-tason |
| `agents` | Palauttaa rekisteröidyt agentit |
| `register_agent` | Rekisteröi uuden agentin |

### Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["metrics", "health", "agents", "register_agent"]` | ✅ | Toiminto |
| `agent_type` | `str` | ❌ | Agentin tyyppi (register_agent) |
| `agent_name` | `str` | ❌ | Agentin nimi (register_agent) |

---

### Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `metrics` | `dict[str, Any]` | Järjestelmänmetriikit |
| `agent_count` | `int` | Rekisteröityjä agentteja |
| `system` | `dict[str, Any]` | Järjestelmätiedot |
| `health_status` | `str` | `healthy`, `degraded`, `critical` |
| `issues` | `list[str]` | Havaitut ongelmat |
| `health_checks` | `dict[str, bool]` | Tarkistustulokset |
| `registered_agents` | `list[dict[str, Any]]` | Rekisteröityt agentit |
| `agent_name` | `str` | Rekisteröidyn agentin nimi |
| `message` | `str` | Tilanneilmoitus |

---

### Järjestelmätunnus (metrics)

```python
{
    "agent_count": 20,             # AIDE-moduulit
    "active_agents": 18,
    "memory_usage_mb": 512,
    "cpu_usage_percent": 34.5,
    "uptime_seconds": 86400,
    "version": "2.1.0"
}
```

---

### Terveys-taso (health)

| Tila | Kuvaus |
|---|---|
| `healthy` | Kaikki tarkistukset läpäisty |
| `degraded` | Joitain tarkistuksia epäonnistunut |
| `critical` | useat tarkistukset epäonnistuneet |

---

## DashboardAgent

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"dashboard"` |

### Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `render` | Renderöi dashboard-näytön |
| `refresh` | Päivitä näytön tiedot |
| `format_text` | Muotoile teksti taulukkoon |

### Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `query` | `str` | ✅ | Näytettävät tiedot |
| `metrics` | `dict[str, Any]` | ❌ | Järjestelmänmetriikit |
| `agent_list` | `list[dict[str, Any]]` | ❌ | Agenttilista |
| `health_data` | `dict[str, Any]` | ❌ | Terveysdata |

---

### Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `output` | `str` | Renderöity tekstisisäänitys |
| `sections_rendered` | `int` | Renderöityjä osioita |

---

## Esimerkkikoodi

```python
from agents import ControlCenterAgent, DashboardAgent

# Control Center -metriikat
cc = ControlCenterAgent()
result = cc.run(action="metrics")
print(f"Agentit: {result.agent_count}")
print(f"Versio: {result.metrics['version']}")

# Terveys-taso
health = cc.run(action="health")
print(f"Tila: {health.health_status}")
print(f"Ongelmat: {health.issues}")

# Agenttilista
agents = cc.run(action="agents")
for a in agents.registered_agents:
    print(f"  {a['name']} ({a['type']})")

# Dashboard -näytön renderöinti
dashboard = DashboardAgent()
output = dashboard.run(
    query="system",
    metrics=result.metrics,
    agent_list=agents.registered_agents,
    health_data={"status": health.health_status, "issues": health.issues}
)

print(output.output)
```

---

### Dashboard-ulos (esimerkki)

```
╔══════════════════════════════════════╗
║         AIDE Control Center          ║
╠══════════════════════════════════════╣
║ Status: healthy          Version: 2.1.0 ║
║ Agents: 20 (18 active)                  ║
║ Uptime: 1d 0h 0m                          ║
║ Memory: 512MB    CPU: 34.5%              ║
╠══════════════════════════════════════╣
║ Agents:                                ║
║  M1  KnowledgeAgent    ✓              ║
║  M2  TaskPlannerAgent  ✓              ║
║  M3  CodeReviewAgent   ✓              ║
║  ...                                    ║
║  M20 CLIOrchestrator   ✓              ║
╚══════════════════════════════════════╝
```

---

## Testikattavuus

M20-testit (58) sisältävät:
- `test_metrics_returns_system_stats`
- `test_health_checks_all_components`
- `test_get_registered_agents`
- `test_register_new_agent`
- `test_dashboard_render_system_view`
- `test_dashboard_refresh_updates_metrics`
- `test_control_center_routes_to_agents`
- `test_system_health_complete`

---

## Liittyvät moduulit

- **Käyttää:** kaikkia AIDE-agentteja (M1–M20) kautta `MODULE_REGISTRY`-importin
- **Integroi:** CLIOrchestrator (M20) päätapahtumiin

## CLI-käyttö

```bash
aide control metrics
aide control health
aide control agents
aide dashboard
```
