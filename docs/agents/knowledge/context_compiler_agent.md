# ContextCompilerAgent (M13 Knowledge & Memory)

**Tiedosto:** `agents/knowledge_agent.py`  
**Moduuli:** M13 — Knowledge & Memory  
**Status:** ✅ Valmiina  
**Testit:** 64 (yhteinen M13) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Kontekstin kääntäminen lähteistä (files/strings). AST-suodattimet (imports, classes, functions, errors, docstrings, constants). Tukee muotoja: `json`, `markdown`, `text`, `summary`. Prioriteetit ja `max_context_length`-rajoitus.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"context_compiler"` |

---

## Syöte (ContextCompilerInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["compile", "summarize", "extract"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Lähde (tiedoston polku tai koodi) |
| `source_type` | `str` | ❌ | `file`, `string` |
| `format` | `str` | ❌ | `json`, `markdown`, `text`, `summary` |
| `filters` | `list[str]` | ❌ | AST-suodattimet: `imports`, `classes`, `functions`, `errors`, `docstrings`, `constants` |
| `priority` | `str` | ❌ | `low`, `medium`, `high` — mitä otetaan mukaan |
| `max_context_length` | `int` | ❌ | Maksimimerkkimäärä (oletus: 4000) |

---

## Tuloste (ContextCompilerOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `compiled_context` | `str` | Käännetty konteksti |
| `source_summary` | `dict[str, Any]` | Lähdetyyotelmän yhteenveto |
| `elements_found` | `dict[str, int]` | Löydettujen elementtien lukumäärä (per suodatin) |
| `total_length` | `int` | Kontektin kokonaismitta |
| `truncated` | `bool` | Onko typistetty `max_context_length`-rajan takia |

---

## Esimerikkoodi

```python
from agents import ContextCompilerAgent

compiler = ContextCompilerAgent()

# Tiedoston kontekstin kääntäminen
result = compiler.run(
    action="compile",
    query="src/app.py",
    source_type="file",
    format="json",
    filters=["imports", "classes", "docstrings"],
    priority="high",
    max_context_length=2000
)

print(f"Elementit: {result.elements_found}")
# Output: Elementit: {'imports': 5, 'classes': 3, 'docstrings': 7}

print(f"Typistetty: {result.truncated}")
# Output: Typistetty: False

print(result.compiled_context[:100])
# Output: {"imports": ["json", "os", "sys"], "classes": [...], ...}
```

### Yhteenveto

```python
result = compiler.run(
    action="summarize",
    query="src/app.py",
    format="text"
)

print(result.source_summary)
# Output: {"language": "python", "lines": 142, "functions": 8, "classes": 2}
```

---

## AST-suodattimet

| Suodatin | Mitä kaipaillaan |
|---|---|
| `imports` | `import` ja `from ... import` -rivit |
| `classes` | Luokkien nimet ja metodit |
| `functions` | Funktioiden nimet ja parametrit |
| `errors` | `try/except` -lohdot |
| `docstrings` | Docstringit |
| `constants` | Moduulitasoarvot (UPPER_CASE) |

---

## Prioriteetit

| Taso | Kuvaus |
|---|---|
| `low` | Vain olennolliset elementit |
| `medium` | Tärkeitä elementit + selitykset |
| `high` | Kaikki elementit + lisätiedot |

---

## Testikattavuus

M13-testit (64) sisältävät:
- `test_compile_file_to_json`
- `test_filters_applied_correctly`
- `test_max_context_length_truncation`
- `test_summarize_returns_key_stats`
- `test_extract_classes_and_functions`
