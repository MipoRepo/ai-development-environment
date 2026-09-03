# PedagogyAgent (M11 Pedagogy)

**Tiedosto:** `agents/pedagogy_agent.py`  
**Moduuli:** M11 — Pedagogy  
**Status:** ✅ Valmiina  
**Testit:** 68 (yhteinen M11) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Rakentaa kokonaisan oppimissuunnitelman käyttäjäprofiilin perusteella. Ottaa `user_background`-profiilin (taito, aika, tavoitteet) ja luo rakenteen moduuleilla, viikoilla, harjoituksilla ja resursseilla.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"pedagogy"` |

---

## Syöte (PedagogyAgentInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["create", "adapt", "recommend"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Käyttäjän kysymys |
| `user_background` | `dict[str, Any]` | ✅ | Profiili |
| `existing_plan` | `dict[str, Any]` | ❌ | Olemassa oleva suunnitelma (adapt) |

---

## Tuloste (PedagogyAgentOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `learning_path` | `dict[str, Any]` | Valmis suunnitelma |
| `modules` | `list[dict[str, Any]]` | Moduulit |
| `duration_weeks` | `int` | Kestävyys (viikot) |
| `resources` | `list[str]` | Suositeltavat resurssit |
| `adaptations` | `list[str]` | Mukautukset (adapt-toiminto) |

---

## Esimerikkoodi

```python
from agents import PedagogyAgent

pedagogy = PedagogyAgent()
result = pedagogy.run(
    action="create",
    query="Opi Python-ohjelmointi 3 kuussa",
    user_background={
        "skill_level": "beginner",
        "available_hours": 8,
        "goal": "web development",
        "previous_experience": "none"
    }
)

print(result.duration_weeks)
# Output: 12

for module in result.modules:
    print(f"  {module['name']}: {module['week']} — {module['description']}")
```

---

## Testikattavuus

M11-testit sisältävät:
- `test_create_learning_path`
- `test_adapt_existing_plan`
- `test_recommend_adjusts_for_background`
