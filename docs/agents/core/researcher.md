# ResearcherAgent (M1 Core)

**Tiedosto:** `agents/researcher_agent.py`  
**Moduuli:** M1 — Core  
**Status:** ✅ Valmiina  
**Testit:** 52 | **Kattavuus:** 93 %

---

## Tarkoitus

Tiedonhaku eri lähteistä: paikallisista tiedostoista, verkkomerkinnästä (WebFetch) ja internetsivuilta (WebSearch). Tukee useita hakustrategioita ja palauttaa tiivisteltyä, lähteitählinkittelemää yhteenvetoa.

---

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"researcher"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `research` | Hae tieto tietysti aiheesta |
| `summarize` | Tiivistä löydetty sisältö |
| `compare` | Vertaa useita lähteitä tai vaihtoehtoja |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["research", "summarize", "compare"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Tutkittava aihe tai kysymys |
| `sources` | `list[str]` | ❌ | Rajoita lähteisiin (esim. `["web", "files"]`) |
| `max_results` | `int` | ❌ | Enimmäismäärä (oletus: 5) |
| `depth` | `str` | ❌ | `shallow` / `deep` |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `summary` | `str` | Tiivistelmä |
| `sources_found` | `list[dict[str, str]]` | Lähteet (`{"title", "url"}`) |
| `total_results` | `int` | Löydettyjen lähteiden määrä |
| `comparison` | `dict[str, Any]` | Vertailutulokset (compare) |
| `message` | `str` | Tilanneilmoitus |

---

## Esimerkkikoodi

```python
from agents import ResearcherAgent

researcher = ResearcherAgent()

# Tutki aihetta
result = researcher.run(
    action="research",
    query="Pythonin async/await parhaat käytännöt 2026",
    max_results=10,
    depth="deep"
)

print(f"Lähteitä: {result.total_results}")
print(result.summary[:200])

# Tiivistä sisältö
result = researcher.run(
    action="summarize",
    query="https://docs.python.org/3/library/asyncio.html"
)
print(result.summary)

# Vertaa vaihtoehtoja
result = researcher.run(
    action="compare",
    query="FastAPI vs Django REST",
    sources=["web"]
)
print(result.comparison)
```

---

## Hakulähteet

| Lähde | Selitys |
|---|---|
| `files` | Paikalliset tiedostot (`*.py`, `*.md`, `docs/`) |
| `web` | WebSearch verkkohaku |
| `urls` | WebFetch tietyt URL-osoitteet |
| `knowledge` | KnowledgeAgent (M13) tiedotus |

---

## Testikattavuus

M1-testit (52) sisältävät:
- `test_research_returns_summary`
- `test_summarize_extracts_key_points`
- `test_compare_returns_both_sides`
- `test_web_fetch_integration`
- `test_source_filtering`

---

## Liittyvät moduulit

- **Seuraa:** DirectorAgent (M3) — tavoitteen tulkitsee
- **Integroi:** KnowledgeAgent (M13) — löydetyn tiedon tallentamiseen
