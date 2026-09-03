# UpgradeAgent (M14 Maintenance)

**Tiedosto:** `agents/maintenance_agent.py`  
**Moduuli:** M14 — Maintenance  
**Status:** ✅ Valmiina  
**Testit:** 46 (yhteinen M14) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Päivytspanitustarkistus `requirements.txt` ja `pyproject.toml`-tiedostoille. Automaattiset päivityskomennot — `check`, `upgrade`, `dry_run`. Käyttää `tomllib`-kirjastoa Python 3.11:ssa (ei vanhentunutta `pyproject_parser`-pakettia).

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"upgrade"` |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["check", "upgrade", "dry_run"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Tiedoston polku (`requirements.txt` tai `pyproject.toml`) |
| `package_filter` | `list[str]` | ❌ | Rajoita tarkistukseen tietyt paketit |
| `security_only` | `bool` | ❌ | Vain turvallisuusmuodostuksia |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `packages` | `list[dict[str, Any]]` | Paketit ja versiot |
| `upgradable_packages` | `list[dict[str, str]]` | Päivitettävät paketit |
| `total_upgradable` | `int` | Päivitettävien määrä |
| `upgrade_plan` | `list[str]` | Suoritettavat komennot (`upgrade`-toiminto) |
| `error` | `str \| None` | Virhe |

---

## Esimerkkikoodi

```python
from agents import UpgradeAgent

upgrader = UpgradeAgent()

# Tarkista päivitykset (dry-run)
result = upgrader.run(
    action="dry_run",
    query="requirements.txt"
)

print(f"Päivitettävästi: {result.total_upgradable}")
for pkg in result.upgradable_packages:
    print(f"  {pkg['name']}: {pkg['current']} → {pkg['latest']}")

# Suorita päivitys
result = upgrader.run(
    action="upgrade",
    query="requirements.txt",
    package_filter=["flask", "requests"]
)

for cmd in result.upgrade_plan:
    print(f"Suoritetaan: {cmd}")
# Output: Suoritetaan: pip install flask==3.0.0
```

---

## Tuetut tiedostot

| Tiedosto | Käsittely |
|---|---|
| `requirements.txt` | rivittäin käännetään |
| `pyproject.toml` | `tomllib`-kirjastolla (Python 3.11+) |

---

## Testikattavuus

M14-testit (46) sisältävät:
- `test_check_requirements_txt`
- `test_upgrade_pyproject_toml`
- `test_security_filtered_packages`
- `test_dry_run_no_changes_made`
