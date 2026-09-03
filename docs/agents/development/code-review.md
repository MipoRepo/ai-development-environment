# CodeReviewAgent (M4 Development)

**Tiedosto:** `agents/developer.py`  
**Moduuli:** M4 — Development  
**Status:** ✅ Valmiina  
**Testit:** 32 (osuus M4) | **Kattavuus:** 91 %

---

## Tarkoitus

Turvallisuus- ja laadun tarkistus koodista. Skannaa AST-puun läpi löytääkseen vaaratilanteet, turvallisuusongelmat ja laatupoikkeamät.

---

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"code_review"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `scan` | Skannaa koodi turvallisuusongelmoihin |
| `suggest` | Ehdota korjauksia |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["scan", "suggest"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Tiedoston polku tai koodi |
| `language` | `str` | ❌ | Kieli (oletus: `python`) |
| `severity` | `str` | ❌ | Minimivaatimus: `low`, `medium`, `high` |
| `categories` | `list[str]` | ❌ | `security`, `quality`, `performance` |

---

## Tuloste

| Kenttelu | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `issues` | `list[dict[str, Any]]` | Löydetyt ongelmat |
| `total_issues` | `int` | Ongelmien määrä |
| `severity_summary` | `dict[str, int]` | Severity-jakauma |
| `suggestions` | `list[str]` | Parannukehdotuksia |
| `risk_score` | `float` | Riskipiste (0.0–10.0) |

---

## Havaitut ongelmat (AST-pohjainen)

| Ongelma | AST-solmu | Riskitaso |
|---|---|---|
| `eval()` käyttö | `ast.Call` (eval) | `high` |
| `exec()` käyttö | `ast.Call` (exec) | `high` |
| `subprocess.run(..., shell=True)` | `ast.Call` (subprocess) | `high` |
| Kiinalainen salasana | `ast.Assign` (password) | `medium` |
| `pickle` deserialisointi | `ast.Call` (pickle) | `high` |
| `yaml.load` (turvaton) | `ast.Call` (yaml.load) | `high` |

---

## Esimerkkikoodi

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

for issue in result.issues:
    print(f"  [{issue['severity']}] {issue['file']}:{issue['line']} — {issue['description']}")

print(f"Riskipiste: {result.risk_score}")
# Output: Riskipiste: 7.5
```

---

## AST-skripti

```python
import ast

tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = getattr(node.func, 'id', str(node.func))
        if func in ('eval', 'exec', 'pickle.loads'):
            print(f"⚠️  Vaara: {func}() rivi {node.lineno}")
```

---

## Testikattavuus

M4-testit (32) sisältävät:
- `test_generate_valid_python`
- `test_refactor_preserves_functionality`
- `test_fix_bug_resolves_index_error`
- `test_generate_unit_tests_pytest_format`
- `test_code_review_detects_eval`

---

## Liittyvät moduulit

- **Edeltäjä:** ResearcherAgent (M1) — tiedonhaku
- **Seuraaja:** TesterAgent (M5) — testien generaattori

## CLI-käyttö

```bash
aide run "Tarkista turvallisuus" src/api.py     # → CodeReviewAgent.scan
aide run "Ehdota korjauksia" src/api.py         # → CodeReviewAgent.suggest
```
