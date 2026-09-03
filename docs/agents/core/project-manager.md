# ProjectManagerAgent (M4 Project Manager)

**Tiedosto:** `agents/project_manager_agent.py`  
**Moduuli:** M4 — Project Manager  
**Status:** ✅ Valmiina  
**Testit:** 46 | **Kattavuus:** 89 %

---

## Tarkoitus

Hallitsee projektin kulkua: backlogia, milestoneja ja tehtävien priorisointia. Tukee projektin tilan seurontaa ja aikataulun päästöä.

---

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"project_manager"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `update_backlog` | Lisää tai päivitä tehtävät backlogseljaimossa |
| `set_milestone` | Aseta uusi projekti-milestone |
| `reprioritize` | Järjestä tehtävät prioriteetin mukaan |
| `status_report` | Tuota projekti-tilan raportti |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["update_backlog", "set_milestone", "reprioritize", "status_report"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Tehtävän kuvaus tai kysymys |
| `tasks` | `list[dict[str, Any]]` | ❌ | Taustalistan kokonaan (update_backlog) |
| `milestone_name` | `str` | ❌ | Milestone-nimi (set_milestone) |
| `due_date` | `str` | ❌ | Deadline ISO-muodossa (set_milestone) |
| `priority_scores` | `dict[str, int]` | ❌ | Prioriteetit (reprioritize) |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `backlog` | `list[dict[str, Any]]` | Päivitetty taustalista |
| `milestones` | `list[dict[str, Any]]` | Projektimilestone-tilat |
| `ranked_tasks` | `list[dict[str, Any]]` | Priorisoidut tehtävät |
| `status_summary` | `str` | Tilanneusannetseloste |
| `completion_percent` | `float` | Prosentuaalinen edistyminen |

---

## Esimerkkikoodi

```python
from agents import ProjectManagerAgent

pm = ProjectManagerAgent()

# Lisää tehtävä backlogiin
result = pm.run(
    action="update_backlog",
    query="Lisää tehtävä dokumentaation kirjoittamisesta"
)

print(result.backlog[-1])
# Output: {'id': 'task-003', 'title': '...', 'priority': 3}

# Aseta milestone
result = pm.run(
    action="set_milestone",
    query="M20-dokumentaatio",
    milestone_name="Q3 Documentation Sprint",
    due_date="2026-09-15"
)

print(f"Milestone: {result.milestones[-1]['name']}")

# Statusraportti
result = pm.run(
    action="status_report",
    query="nykyinen"
)

print(f"Edistyminen: {result.completion_percent}%")
print(result.status_summary)
```

---

## Liittyvät moduulit

- **Käyttää:** TaskPlannerAgent (M2) työtehtävien yksityiskohtaansa
- **Integroi:** TechnicalWriterAgent (M6) dokumentaation aikataulun kanssa

## CLI-käyttö

```bash
aide run "Päivitä roadmap Projekti-ohjelman mukaan."
```
