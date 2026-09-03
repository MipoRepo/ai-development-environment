# FeedbackAgent (M12 Learning & Assessment)

**Tiedosto:** `agents/learning_path_agent.py`  
**Moduuli:** M12 — Learning & Assessment  
**Status:** ✅ Valmiina  
**Testit:** 57 (yhteinen M12) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Antaa AST-pohjainen palaute koodin rakenteelle. Tukee neljää palautetyyppiä: `code_review`, `learning`, `style`, `performance`. Laskee score 0–100 ja antaa parannusehdotuksia.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"feedback"` |

---

## Syöte (FeedbackInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["review", "score", "suggest"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Koodi tai tiedoston polku |
| `feedback_type` | `str` | ✅ | `code_review`, `learning`, `style`, `performance` |
| `language` | `str` | ❌ | Kieli (oletus: `python`) |
| `detail_level` | `str` | ❌ | `basic`, `detailed`, `expert` |

---

## Tuloste (FeedbackOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `score` | `float` | Arvosana 0–100 |
| `feedback` | `str` | Palaute- tai selitysteksti |
| `issues` | `list[dict[str, Any]]` | Löydetyt ongelmat |
| `suggestions` | `list[str]` | Parannusehdotukset |
| `recommendations` | `list[str]` | Oppimissuositukset (learning-tyyppi) |

---

## Esimerikkoodi

### Koodikritiikki

```python
from agents import FeedbackAgent

feedback = FeedbackAgent()
result = feedback.run(
    action="review",
    query="src/app.py",
    feedback_type="code_review"
)

print(f"Arvosana: {result.score}/100")
# Output: Arvosana: 78/100

for issue in result.issues:
    print(f"  [{issue['severity']}] {issue['type']}: {issue['description']}")

print(result.suggestions)
# Output: ['Lisää docstring funktioihin', 'Käytä list-comprehension sijaan map-filttereitä']
```

### Oppimismuoto

```python
result = feedback.run(
    action="suggest",
    query="src/utils.py",
    feedback_type="learning"
)

print(result.feedback)
# Output: Tämä koodi demonstroi hyviä käytäntöjä, mutta puuttuu funktioiden dokumentaatiot

print(result.recommendations)
# Output: ['Opiskele Pythonin docstring-käytäntöjä', 'Tutki funktioiden modulaarisuutta']
```

---

## Tukemat palautetyypit

| Tyyppi | Kuvaus |
|---|---|
| `code_review` | Virheiten ja laadun tarkistus |
| `learning` | Oppimisharjoitteita ja oppimissuosituksia |
| `style` | Tyylisääntöjen (PEP 8) tarkistus |
| `performance` | Suorituskyvyntarkastus |

---

## Testikattavuus

M12-testit (57) sisältävät:
- `test_score_below_100_for_poor_code`
- `test_learning_feedback_includes_recommendations`
- `test_suggestions_generated_from_issues`
- `test_handles_syntax_errors_gracefully`
