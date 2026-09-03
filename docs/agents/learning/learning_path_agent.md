# LearningPathAgent (M12 Learning & Assessment)

**Tiedosto:** `agents/learning_path_agent.py`  
**Moduuli:** M12 — Learning & Assessment  
**Status:** ✅ Valmiina  
**Testit:** 57 (yhteinen M12) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Suunnitella henkilökohtaisia oppimispolkuja `user_background`-, `interests`-, `prev_score`- ja `strategy`-parametrien avulla. Laskee `progress_percentage` ja antaa `next_recommendations`.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"learning_path"` |

---

## Syöte (LearningPathAgentInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["create", "update", "evaluate"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Oppimistavoite |
| `user_background` | `dict[str, Any]` | ✅ | Profiili (skill_level, time_available, prev_score) |
| `interests` | `list[str]` | ❌ | Kiinnostukset |
| `strategy` | `str` | ❌ | Strategia (`PATH_STRATEGIES` — progressive, intensive, balanced) |

---

## Tuloste (LearningPathAgentOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `path` | `dict[str, Any]` | Valmis oppimispolku |
| `modules` | `list[dict[str, Any]]` | Moduulit (name, duration, description) |
| `progress_percentage` | `float` | Edistymisprosentti (0–100) |
| `next_recommendations` | `list[str]` | Seuraavat suositukset |
| `estimated_completion` | `str` | Arvioitu valmistumisaika |

---

## Esimerikkoodi

```python
from agents import LearningPathAgent

learner = LearningPathAgent()
result = learner.run(
    action="create",
    query="Opi data-analyysi Pythonilla",
    user_background={
        "skill_level": "beginner",
        "time_available": 10,
        "prev_score": 65,
        "experience": "basic-python"
    },
    interests=["pandas", "visualization"],
    strategy="progressive"
)

print(f"Moduulit: {len(result.modules)}")
# Output: Moduulit: 8

print(f"Edistymys: {result.progress_percentage}%")
# Output: Edistymys: 0% (uusi polku)

for mod in result.modules:
    print(f"  {mod['name']} ({mod['duration']}) — {mod['description']}")
```

---

## PATH_STRATEGIES

| Strategia | Kuvaus |
|---|---|
| `progressive` | Vaiheittain vaikeampiin tehtäviin |
| `intensive` | Tiivis ja nopea eteneminen |
| `balanced` | Tasapainoinen aiheiden ja harjoitusten sekoitus |

---

## Testikattavuus

M12-testit (57) sisältävät:
- `test_create_learning_path_for_beginner`
- `test_update_path_with_new_score`
- `test_evaluate_returns_recommendations`
