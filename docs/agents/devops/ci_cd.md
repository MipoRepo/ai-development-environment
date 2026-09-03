# CI_CDAgent (M10 DevOps)

**Tiedosto:** `agents/devops_agent.py`  
**Moduuli:** M10 — DevOps  
**Status:** ✅ Valmiina  
**Testit:** 63 (yhteinen M10) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

GitHub Actions -workflowjen generointi projektille. Valitsee oikeat workflow-mallit Python-version ja projektin tarpeiden mukaan.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"ci_cd"` |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["generate", "deploy"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Projektin polku |
| `workflow_type` | `str` | ❌ | Tyyppi: `ci-cd`, `linting`, `security` (oletus: `ci-cd`) |
| `python_version` | `str` | ❌ | Python-versio (oletus: `3.11`) |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `workflow_file` | `str` | Generoitu YAML-koodi |
| `file_path` | `str` | Luonnin polku (`/.github/workflows/`) |
| `steps` | `list[dict[str, Any]]` | Vaiheiden kuvaus |
| `python_version` | `str` | Käytetty Python-versio |

---

## Esimerkkikoodi

```python
from agents import CI_CDAgent

ci = CI_CDAgent()
result = ci.run(
    action="generate",
    query="./",
    workflow_type="ci-cd",
    python_version="3.11"
)

print(result.file_path)
# Output: .github/workflows/ci-cd.yml

print(result.workflow_file)
# Output:
# name: CI/CD
# on: [push, pull_request]
# jobs:
#   test:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - uses: actions/setup-python@v5
#         with: {python-version: "3.11"}
# ...
```

Tuetut workflow-tyypit:
- `ci-cd` — täysi pipeline (testaus, build, deploy)
- `linting` — koodinlaatu (ruff, mypy)
- `security` — turvallisuustarkastus (pip-audit, bandit)

---

## Testikattavuus

Kaikki M10-testit (63) sisältävät CI_CDAgent-testit:
- `test_ci_cd_workflow_generated`
- `test_python_version_in_workflow`
- `test_linting_workflow_correct`
- `test_security_workflow_correct`
