# DeveloperAgent, RefactoringAgent & CodeReviewAgent (M4 Development)

**Tiedosto:** `agents/developer.py`  
**Moduuli:** M4 — Development  
**Status:** ✅ Valmiina  
**Testit:** 32 | **Kattavuus:** 94 %

---

## Tarkoitus

Koodin generointi, refaktointi ja turvallisuustarkastus. **DeveloperAgent** luo Python/JS/Markdown-koodia; **RefactoringAgent** tarkistaa puuttuvat dokumentaatiot, käyttämättomat importit ja pitkät funktiot; **CodeReviewAgent** havaitsee turvallisuusongelmat ja laadun.

## Agentit

| Agentti | `agent_type` | Tiedosto |
|---|---|---|
| **DeveloperAgent** | `"developer"` | `agents/developer.py` |
| **RefactoringAgent** | `"refactoring"` | `agents/developer.py` |
| **CodeReviewAgent** | `"code_review"` | `agents/developer.py` |

---

## DeveloperAgent

### Syöte (DeveloperInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["generate", "extend", "refactor"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Generoitava koodi tai kuvaus |
| `language` | `str` | ✅ | Kieli (python, javascript, markdown) |
| `file_path` | `str` | ❌ | Polku tiedostoon (extend/refactor-lähtönä) |
| `project_type` | `str` | ❌ | Projektin tyyppi (web-app, api, script) |

### Tuloste (DeveloperOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `code` | `str` | Generoitu koodi |
| `file_path` | `str` | Luodun/täydennetyn tiedoston polku |
| `language` | `str` | Käytetty kieli |
| `explanation` | `str` | Koodin selitys |
| `changes` | `list[str]` | Tekemät muutokset (extend/refactor) |
| `error` | `str \| None` | Virheviesti |

---

## RefactoringAgent

### Syöte (RefactoringInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["analyze", "fix"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Tiedoston tai kansion polku |
| `checks` | `list[str]` | ❌ | Tarkistukset (docstrings, imports, complexity, dead_code) |

### Tuloste (RefactoringOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `issues` | `list[dict[str, Any]]` | Löydetyt ongelmat |
| `file_path` | `str` | Analysoitu tiedosto |
| `total_issues` | `int` | Ongelmien kokonaismäärä |
| `suggestions` | `list[str]` | Parannusehdotuksia |

---

## CodeReviewAgent

### Syöte (CodeReviewInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["scan", "suggest"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Tiedosto tai koodi |
| `severity` | `str` | ❌ | Minimivaatimus (low, medium, high) |
| `categories` | `list[str]` | ❌ | Kategoriat (security, quality, performance) |

### Tuloste (CodeReviewOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `issues` | `list[dict[str, Any]]` | Löydetyt ongelmat |
| `total_issues` | `int` | Ongelmien määrä |
| `severity_summary` | `dict[str, int]` | Severityjakauma |
| `suggestions` | `list[str]` | Parannusehdotuksia |

---

## Esimerkkikoodi

### Python-injeksin generointi

```python
from agents import DeveloperAgent

dev = DeveloperAgent()
result = dev.run(
    action="generate",
    query="Funktio joka laskee kahden numeron keskiarvon ja palauttaa sen JSON-muodossa",
    language="python"
)

print(result.code)
# Output:
# def average_json(a: float, b: float) -> str:
#     avg = (a + b) / 2
#     return json.dumps({"average": avg})

with open("math_utils.py", "w") as f:
    f.write(result.code)
```

### JavaScript-funktion generointi

```python
result = dev.run(
    action="generate",
    query="React-komponentti, joka näyttää käyttäjän nimen ja painikkeen",
    language="javascript",
    project_type="web-app"
)

print(result.explanation)
# Output: Komponentti 'UserProfile' näyttää nimen propsina ja renderöi painikkeen
```

### Refaktorointi

```python
from agents import RefactoringAgent

refactor = RefactoringAgent()
result = refactor.run(
    action="analyze",
    query="src/utils.py",
    checks=["docstrings", "imports", "complexity"]
)

for issue in result.issues:
    print(f"  {issue['type']}: {issue['description']}")
# Output:
#   docstrings: Funktio 'process_data' puuttuu docstring
#   complexity: Funktio 'main' on liian pitkä (45 riviä)
```

### Koodin tarkastus

```python
from agents import CodeReviewAgent

reviewer = CodeReviewAgent()
result = reviewer.run(
    action="scan",
    query="src/api.py",
    severity="medium"
)

print(f"Turvallisuusongelmia: {result.severity_summary.get('high', 0)}")
# Output: Turvallisuusongelmia: 2
```

---

## Turvallisuustarkkaus

CodeReviewAgent skannaa seuraavia mustteita (AST-pohjaisesti):

```python
import ast

tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = getattr(node.func, 'id', str(node.func))
        if func == 'eval':
            print(f"⚠️  Turvallinen ongelma: eval() rivi {node.lineno}")
        if func == 'exec':
            print(f"⚠️  Turvallinen ongelma: exec() rivi {node.lineno}")
```

Havaitut ongelmat: `eval()`, `exec()`, `shell=True`, kiinteät salasanat, `pickle`, `subprocess.run` turvattomuus.

---

## Testikattavuus

```
tests/test_developer_agent.py — 32 testiä
Kattavuus: 94 %
```

Tärkeimmät testit:
- `test_generate_returns_valid_python`
- `test_generate_javascript_function`
- `test_extend_appends_to_existing_file`
- `test_refactoring_finds_missing_docstrings`
- `test_code_review_detects_eval`
- `test_code_review_detects_shell_true`

## Liittyvät moduulit

- **Edeltäjä:** ResearcherAgent (M3) — tekijät analysointi
- **Seuraaja:** TesterAgent (M5) — testien suunnittelu
- **Riippuu:** KnowledgeAgent (M13) tiedostojen lukemiseen

## CLI-käyttö

```bash
aide run "Luo Python-funktio joka laskee keskiarvon"   # → DeveloperAgent.generate
aide run "Refaktoroi src/utils.py"                    # → RefactoringAgent.analyze
aide run "Tarkista turvallisuus src/api.py"           # → CodeReviewAgent.scan
```

## Katso myös

- [`modules.md`](../../architecture/modules.md) — kaikki moduulit
- [`agent-lifecycle.md`](../../architecture/agent-lifecycle.md) — agentin elinkaari
- [`dataflow.md`](../../architecture/dataflow.md) — generoidun koodin kulku
