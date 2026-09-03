# CleanupAgent (M14 Maintenance)

**Tiedosto:** `agents/maintenance_agent.py`  
**Moduuli:** M14 — Maintenance  
**Status:** ✅ Valmiina  
**Testit:** 46 (yhteinen M14) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Cache-tiedostojen, temp-tiedostojen ja build-tulosten poistoaminen projektista. Laskee vapautuneen tilan (`space_freed`) ja antaa yhteenvetoja.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"cleanup"` |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["clean", "analyze", "reset"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Projektin polku |
| `target` | `str` | ❌ | Käsiteltävä alue: `caches`, `temp`, `build` (oletus: kaikki) |
| `dry_run` | `bool` | ❌ | Simuloidunko poiston (ilman todellista poistoa) |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `cleaned_items` | `list[dict[str, Any]]` | Poistetut tiedostot/kansiosehdot |
| `space_freed` | `float` | Vapautunut tila (MB) |
| `total_size` | `float` | Kokonaiskoko (MB) |
| `summary` | `dict[str, Any]` | Tiivistelmä (count, size_per_type) |
| `skipped` | `list[str]` | Saltitut tiedostot (dry_run) |

---

## Tunnistettavat kohteet

### Cachet (CACHE_DIRS)

| Polku | Tyyppi |
|---|---|
| `__pycache__/` | Python-bytetimet |
| `.pytest_cache/` | pytest-välimuistit |
| `.mypy_cache/` | mypy-välimuistit |
| `.ruff_cache/` | Ruff-välimuistit |

### Temp-tiedostot (.bak, .tmp)

| Kuvio | Esimerkki |
|---|---|
| `*.bak` | `config.bak` |
| `*.tmp` | `temp.tmp` |
| `*~` | Emacs-tilde-tiedostot |

### Build-tulokset (BUILD_DIRS)

| Polku | Tyyppi |
|---|---|
| `dist/` | Jakelupaketit |
| `build/` | Käännoskansiot |
| `*.egg-info/` | Egg-metadata |
| `node_modules/` | Node.js-riippuvuudet |

---

## Esimerkkikoodi

```python
from agents import CleanupAgent

cleaner = CleanupAgent()

# Analyysi ilman poistoa
result = cleaner.run(
    action="analyze",
    query="./"
)

print(f"Siistittävissä oleva tila: {result.total_size} MB")
# Output: Siistittävissä oleva tila: 124.7 MB

# Simuloidu poisto
result = cleaner.run(
    action="clean",
    query="./",
    dry_run=True
)

print(f"Poistettavissa: {len(result.skipped)} tiedostoa")
# Output: Poistettavissa: 156 tiedostoa

# Todellinen poisto
result = cleaner.run(
    action="clean",
    query="./",
    target="caches"
)

print(f"Vapautui: {result.space_freed} MB")
# Output: Vapautui: 12.3 MB
```

---

## Testikattavuus

M14-testit (46) sisältävät:
- `test_clean_removes_pycache`
- `test_calculate_space_freed`
- `test_dry_run_does_not_delete`
- `test_all_cache_dirs_detected`
- `test_skips_protected_files`
