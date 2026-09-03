# MentorAgent (M11 Pedagogy)

**Tiedosto:** `agents/pedagogy_agent.py`  
**Moduuli:** M11 — Pedagogy  
**Status:** ✅ Valmiina  
**Testit:** 68 (yhteinen M11) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Käyttäjän ohjaus ohjelmistokehityksen oppimisessa. Valitsee oikeat aihepiirrot käyttäjän taitotasosta ja LEARNING_TOPICS-kirjastosta.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"mentor"` |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["teach", "suggest", "assess"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Aihe tai kysymys |
| `skill_level` | `str` | ❌ | `beginner`, `intermediate`, `advanced` |
| `interests` | `list[str]` | ❌ | Käyttäjän kiinnostukset |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `topic` | `str` | Valittu aihe |
| `skill_level` | `str` | Taso |
| `explanation` | `str` | Selitys |
| `exercises` | `list[dict[str, Any]]` | Harjoitukset |
| `resources` | `list[str]` | Linkeistä resurssit |
| `next_topic` | `str` | Seuraava ehdotettu aihe |

---

## Esimerikkoodi

```python
from agents import MentorAgent

mentor = MentorAgent()
result = mentor.run(
    action="teach",
    query="Miksi käytetään JWT-todennuksessa?",
    skill_level="intermediate"
)

print(result.topic)
print(result.explanation)  # 300–500 merkkiä selitys

for ex in result.exercises:
    print(f"  {ex['type']}: {ex['title']}")
```

---

## Testikattavuus

M11-testit (68) sisältävät:

- `test_teach_advances_skill_level`
- `test_suggest_returns_relevant_topics`
- `test_exercises_generated`
