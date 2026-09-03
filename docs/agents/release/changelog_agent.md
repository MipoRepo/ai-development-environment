# ChangelogAgent (M15 Release & Governance)

**Tiedosto:** `agents/release_agent.py`  
**Moduuli:** M15 — Release & Governance  
**Status:** ✅ Valmiina  
**Testit:** 60 | **Kattavuus:** 88 %

---

## Tarkoitus

Muutoshistorian (changelogin) generaatio muutoksista. Tukee viitoille (feature/fix/change/remove/deprecated/security) ja muodoissa (Keep a Changelog / markdown / unreleased). Ryhmittää muutokset ja laskee määrät.

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"changelog"` |

---

## Syöte (ChangelogInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["generate", "update", "parse"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Muutosten lähde (git log, tiedosto tai kuvaus) |
| `format` | `str` | ❌ | `keepachangelog`, `markdown`, `json` (oletus: `keepachangelog`) |
| `version` | `str` | ❌ | Käsiteltävä versio |
| `changes` | `list[dict[str, Any]]` | ❌ | Muutosten lista (update-generointia varten) |

---

## Tuloste (ChangelogOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `changelog` | `str` | Generoitu changelog-teksti |
| `file_path` | `str` | Luonnin polku (`CHANGELOG.md`) |
| `sections` | `dict[str, list[str]]` | Ryhmitellyt muutokset per tyypin |
| `change_count` | `dict[str, int]` | Muutosten lukumäärä per tyyppi |
| `total_changes` | `int` | Kaikki muutokset yhteensä |

---

## Tuetut muutostyypit

| Tyyppi | Kuvaus | Esimerkkimuoto |
|---|---|---|
| `feature` | Uudet ominaisuudet | `[+] Käyttäjäprofiilin päivitys` |
| `fix` | Bugikorjaukset | `[-] Korjattu login-virhe` |
| `change` | Muutokset | `[*] Päivitetty API-kutsu` |
| `remove` | Poistetut ominaisuudet | `[x] Poistettiin vanha endpoint` |
| `deprecated` | Vanhentuneet | `[~] Vanhut parametrit` |
| `security` | Turvallisuuspäivitykset | `[!] Korjattu XSS-haavoittuvuus` |

---

## Esimerkkikoodi

```python
from agents import ChangelogAgent

changelog = ChangelogAgent()

# Generoi git-lokin perusteella
result = changelog.run(
    action="generate",
    query="git log v1.4.0..v1.5.0",
    format="keepachangelog",
    version="1.5.0"
)

print(result.file_path)
# Output: CHANGELOG.md

print(result.changelog)
# Output:
# ## [1.5.0] - 2026-09-03
# ### Added
# - Käyttäjäprofiilin päivitys
# - API-gatewaytukea
# ### Fixed
# - Kirjautumisvirhe korjattu
# ### Security
# - Päivitetty riippuvuudet

print(result.change_count)
# Output: {'feature': 2, 'fix': 1, 'security': 1}
```

### Muutosten lisääminen

```python
# Lisää muutoksia suoraan
result = changelog.run(
    action="update",
    query="CHANGELOG.md",
    changes=[
        {"type": "feature", "description": "GraphQL endpointit"},
        {"type": "fix", "description": "Korjattu timeout-ongelma"}
    ]
)
print(result.file_path)  # Päivitetty CHANGELOG.md
```

---

## Testikattavuus

M15-testit (60) sisältävät:
- `test_generate_keepachangelog_format`
- `test_change_count_per_type`
- `test_update_appends_to_changelog`
- `test_parse_git_log`
