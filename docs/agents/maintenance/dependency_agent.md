# DependencyAgent (M14 Maintenance)

**Tiedosto:** `agents/maintenance_agent.py`  
**Moduuli:** M14 — Maintenance  
**Status:** ✅ Valmiina  
**Testit:** 46 (yhteinen M14) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Riippuvuusanalyysi `requirements.txt`, `pyproject.toml` ja `package.json`-tiedostoille. Tunnistaa turvallisuusonkoimet, vanhentuneet paketit ja riippuvuussolmupuu.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"dependency"` |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["analyze", "audit", "report"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Tiedosto (`requirements.txt`, `pyproject.toml`, `package.json`) |
| `depth` | `int` | ❌ | Riippuvuussolmuksen syvyys (oletus: 2) |
| `security_only` | `bool` | ❌ | Vain turvallisuusrivat |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `dependencies` | `list[dict[str, Any]]` | Paketit ja versiot |
| `dependency_tree` | `dict[str, list[str]]` | Riippuvuussolmut |
| `security_score` | `float` | Turvallisuuspiste (0.0–10.0) |
| `outdated` | `list[dict[str, str]]` | Vanhentuneet paketit |
| `issues` | `list[dict[str, Any]]` | Turvallisuusongelmat |

---

## Esimerkkikoodi

```python
from agents import DependencyAgent

dep = DependencyAgent()

# Analyysi
result = dep.run(
    action="analyze",
    query="requirements.txt"
)

print(f"Riippuvuuksia: {len(result.dependencies)}")
# Output: Riippuvuuksia: 24

print(f"Turvallisuuspiste: {result.security_score}")
# Output: Turvallisuuspiste: 8.2

print("Vanhentuneet paketit:")
for pkg in result.outdated:
    print(f"  {pkg['name']}: {pkg['current']} → {pkg['latest']}")

# Täydellinen raportti
result = dep.run(
    action="report",
    query="."
)

print(result.dependency_tree)
# Output: {'app': ['flask', 'requests'], 'flask': ['werkzeug', 'jinja2']}
```

---

## Tunnistettavat tiedostot

| Tiedosto | Käsittely |
|---|---|
| `requirements.txt` | rivittäin käännetään |
| `pyproject.toml` | `tomllib`-kirjastolla (Python 3.11+) |
| `package.json` | JSON-parsimus |

---

## Testikattavuus

M14-testit (46) sisältävät:
- `test_analyze_requirements_txt`
- `test_audit_finds_vulnerabilities`
- `test_dependency_tree_built`
- `test_outdated_packages_detected`
- `test_security_score_calculated`
