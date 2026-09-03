# ContentDesignerAgent (M11 Pedagogy)

**Tiedosto:** `agents/pedagogy_agent.py`  
**Moduuli:** M11 — Pedagogy  
**Status:** ✅ Valmiina  
**Testit:** 68 (yhteinen M11) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Sisällön luonti eri muodoissa: kyselyt (quiz), harjoitukset (exercise), oppaat (tutorial), tiivistelmät (cheat_sheet), selitykset (explanation). Määrittää `num_items` ja `context_text` parametrien avulla.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"content_designer"` |

---

## Syöte (ContentDesignerAgentInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["create", "generate", "expand"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Aihe tai kysymys |
| `content_type` | `str` | ✅ | `quiz`, `exercise`, `tutorial`, `cheat_sheet`, `explanation` |
| `num_items` | `int` | ❌ | Tuotettaiden määrä (oletus: 3) |
| `context_text` | `str` | ❌ | Lisäkonteksti |
| `difficulty` | `str` | ❌ | `beginner`, `intermediate`, `advanced` |

---

## Tuloste (ContentDesignerAgentOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `items` | `list[dict[str, Any]]` | Luodut sisällöt |
| `content_type` | `str` | Tuotetun sisällön tyyppi |
| `total_items` | `int` | Luotujen nimikkeiden määrä |
| `estimated_time` | `str` | Arvioitu suoritusaika |

---

## Esimerikkoodi

```python
from agents import ContentDesignerAgent

designer = ContentDesignerAgent()
result = designer.run(
    action="create",
    query="Pythonin silmukat",
    content_type="quiz",
    num_items=5,
    difficulty="beginner"
)

print(f"Luodut kyselyt: {result.total_items}")
# Output: Luodut kyselyt: 5

for item in result.items:
    print(f"  Kysymys: {item['question']}")
    print(f"  Vastaukset: {item['options']}")
```

```python
# Harjoituksen luominen
result = designer.run(
    action="create",
    query="Funktioiden määrittely Pythonissa",
    content_type="exercise",
    num_items=3,
    context_text="Aloiksi"
)

for item in result.items:
    print(f"Tehtävä: {item['instructions']}")
    print(f"Ratkaisu: {item['solution']}")
```

---

## Sisällöntyypit

| Tyyppi | Kuvaus |
|---|---|
| `quiz` | Usein valittavat kysymykset |
| `exercise` | Koodiharjoitukset ratkaisun kanssa |
| `tutorial` | Askeleen-askeleelta ohje |
| `cheat_sheet` | Tiivistettyä materiaalia |
| `explanation` | Yksityiskohtelut selitykset |

---

## Testikattavuus

M11-testit sisältävät:
- `test_create_quiz_items`
- `test_generate_tutorial`
- `test_cheat_sheet_contains_key_points`
- `test_exercise_includes_solution`
