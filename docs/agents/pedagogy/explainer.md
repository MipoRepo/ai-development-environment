# ExplainerAgent (M11 Pedagogy)

**Tiedosto:** `agents/pedagogy_agent.py`  
**Moduuli:** M11 — Pedagogy  
**Status:** ✅ Valmiina  
**Testit:** 68 (yhteinen M11) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Koodin selittäminen AST-pohjaisesti `EXPLANATION_PROMPTS`-glien avulla. Tukee myös rikkinäisen koodin käsittelyä.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"explainer"` |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["explain", "summarize"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Koodi tai tiedoston polku |
| `language` | `str` | ❌ | Kieli (oletus: `python`) |
| `detail_level` | `str` | ❌ | `simple`, `detailed`, `expert` |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `explanation` | `str` | Selitysteksti |
| `summary` | `str` | Tiivistelmä |
| `key_concepts` | `list[str]` | Avainkäsitteet |
| `code_elements` | `dict[str, int]` | ELEMENTEJÄ (funktiot, luokat, importit) |

---

## Esimerkkikoodi

```python
from agents import ExplainerAgent

explainer = ExplainerAgent()
result = explainer.run(
    action="explain",
    query="src/app.py",
    detail_level="detailed"
)

print(result.explanation)
print(result.key_concepts)
# Output: ['Flask-sovellus', 'REST-endpointit', 'Pydantic-validointi']
```

---

## Testikattavuus

M11-testit sisältävät:
- `test_explain_python_code`
- `test_handle_syntax_error_gracefully`
- `test_key_concepts_extracted`
