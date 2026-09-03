# TestDesignerAgent, TesterAgent & QAGent (M5 Testing)

**Tiedosto:** `agents/testing_agent.py`  
**Moduuli:** M5 — Testing  
**Status:** ✅ Valmiina  
**Testit:** 24 | **Kattavuus:** 94 %

---

## Tarkoitus

Testiautomaation ja laadunvalvonnan perusagentit. **TestDesignerAgent** suunnittelee testit koodista; **TesterAgent** suorittaa pytest-komennon; **QAGent** tarkistaa koodin laadun ja testikattavuuden.

## Agentit

| Agentti | `agent_type` | Tiedosto |
|---|---|---|
| **TestDesignerAgent** | `"test_designer"` | `agents/testing_agent.py` |
| **TesterAgent** | `"tester"` | `agents/testing_agent.py` |
| **QAGent** | `"qa"` | `agents/testing_agent.py` |

---

## TestDesignerAgent

### Syöte (TestDesignerInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["design", "analyze"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Kooditiedoston polku tai koodi |
| `language` | `str` | ❌ | Kieli (oletus: `"python"`) |
| `framework` | `str` | ❌ | Testikirjasto (oletus: `"pytest"`) |

### Tuloste (TestDesignerOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `test_cases` | `list[dict[str, Any]]` | Suunnitellut testitapaukset |
| `test_file` | `str` | Generoitu testitiedoston koodi |
| `coverage_gaps` | `list[str]` | Kattamattomat koodialueet |

---

## TesterAgent

### Syöte (TesterInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["run", "collect"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Testikansion polku |
| `verbose` | `bool` | ❌ | Yksityiskohtainen tuloste (oletus: `False`) |
| `fail_fast` | `bool` | ❌ | Pysäytetäänkö virheen sattuessa (oletus: `False`) |

### Tuloste (TesterOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `total_tests` | `int` | Testien kokonaismäärä |
| `passed` | `int` | Läpäistyt testit |
| `failed` | `int` | Epäonnistuneet testit |
| `errors` | `int` | Virheet |
| `skipped` | `int` | Ohitatut testit |
| `coverage` | `float` | Kattavuusprosentti |
| `failures` | `list[str]` | Virheviestit |
| `duration` | `float` | Suorituksen kesto (sekuntia) |

---

## QAGent

### Syöte (QAInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["check", "recommend"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Projektin polku |
| `test_files` | `bool` | ❌ | Tarkastellaanko testitiedostoja (oletus: `True`) |
| `code_quality` | `bool` | ❌ | Tarkastellaanko koodin laatua (oletus: `True`) |

### Tuloste (QAOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `total_tests` | `int` | Testien lukumäärä |
| `test_coverage` | `float` | Kattavuuksen prosentti |
| `passing_tests` | `int` | Läpäistyt |
| `failing_tests` | `int` | Epäonnistuneet |
| `code_issues` | `list[dict[str, Any]]` | Koodiongelmia |
| `test_files_found` | `list[str]` | Löydetyt testitiedostot |

---

## Esimerkkikoodi

### Testisuunnittelijan käyttö

```python
from agents import TestDesignerAgent

designer = TestDesignerAgent()
result = designer.run(
    action="design",
    query="src/api/user.py"
)

print(result.test_cases)
# Output: [{"description": "test_create_user", "inputs": {...}, "expected": {...}}]

# Generoitu testitiedosto
with open("tests/test_generated.py", "w") as f:
    f.write(result.test_file)
```

### Testien suoritus

```python
from agents import TesterAgent

tester = TesterAgent()
result = tester.run(
    action="run",
    query="./tests",
    fail_fast=True
)

print(f"Läpäisty: {result.passed}/{result.total_tests}")
print(f"Kattavuus: {result.coverage}%")
# Output: Läpäisty: 45/46
# Output: Kattavuus: 87%
```

### QA-tarkistus

```python
from agents import QAGent

qa = QAGent()
result = qa.run(
    action="check",
    query="./src"
)

print(f"Koodiongelmia: {len(result.code_issues)}")
print(f"Testit: {result.total_tests} ({result.test_coverage}% kattavuus)")
# Output: Koodiongelmia: 3
# Output: Testit: 46 (89% kattavuus)
```

---

## AST-pohjainen testisuunnittelu

TestDesignerAgent käyttää AST-puuta koodin analysointiin:

```python
import ast

tree = ast.parse(source_code)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        # Luo testi jokaiselle funktiolle
        func_name = node.name
        params = [arg.arg for arg in node.args.args]
        print(f"test_{func_name}({', '.join(params)})")
```

---

## Testikattavuus

```
tests/test_testing_agents.py — 24 testiä
Kattavuus: 94 %
```

Eri moduulit testataan erikseen. Tärkeimmät testit:
- `test_design_returns_test_cases`
- `test_run_executes_pytest`
- `test_qa_finds_code_issues`
- `test_calculate_coverage`
- `test_fail_fast_stops_on_error`

## Liittyvät moduulit

- **Edeltäjä:** DeveloperAgent (M4) — kehittämisen jälkeen testaus
- **Seuraaja:** TestRunnerAgent (M8) jatkokäynnin automatisoimiseen
- **Integroi:** MultiAgentCoordinator (M9) workflowissa

## CLI-käyttö

```bash
aide run "Testaa projekti"                          # → TesterAgent.run
aide run "Tarkista koodin laatu"                    # → QAGent.check
aide orchestrate --workflow base.yaml               # → sisältää QA-vaiheen
```

## Katso myös

- [`testing_automation_agent.md`](testing_automation_agent.md) — jatkokäynnin automatisoitu versio
- [`modules.md`](../../architecture/modules.md) — kaikki moduulit
- [`agent-lifecycle.md`](../../architecture/agent-lifecycle.md) — agentin elinkaari
