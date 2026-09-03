# Dokumentaatioagentit (M6 Documentation)

**Tiedosto:** `agents/documentation_agent.py`  
**Moduuli:** M6 — Documentation  
**Status:** ✅ Valmiina  
**Testit:** 46 | **Kattavuus:** 94 %

---

## Tarkoitus

Projektin kokonaan dokumentaation automatisoitu luonti. Vaihtoehtoiset:

1. **TechnicalWriterAgent** — generoi `PROJECT.md`, `AGENTS.md`, `ARCHITECTURE.md`
2. **APIDocumentationAgent** — API-endpointin analyysi ja OpenAPI-schema
3. **UserDocumentationAgent** — README-generointi (ominaisuudet, asennus, käyttö)
4. **MkDocsAgent** — `mkdocs.yml`-generointi ja nav-konfiguuraatio

## Agentit

| Agentti | `agent_type` | Selitys |
|---|---|---|
| **TechnicalWriterAgent** | `"technical_writer"` | Projektin teknis- ja arkkitehtuuridokumentaatio |
| **APIDocumentationAgent** | `"api_documenter"` | REST/GraphQL endpoint-analyysi, OpenAPI-3.0-schema |
| **UserDocumentationAgent** | `"user_documentation"` | Käyttöjärjestödokumentaatio ja README |
| **MkDocsAgent** | `"mkdocs_agent"` | MkDocs-konfiguuri ja sivuversiot |

---

## TechnicalWriterAgent

### Syöte (TechnicalWriterInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["project", "agents", "architecture"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Projektin polku |
| `project_name` | `str` | ❌ | Projektin nimi |
| `project_description` | `str` | ❌ | Lyhyt kuvaus |

### Tuloste (TechnicalWriterOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `document` | `str` | Generoitu markdown-teksti |
| `document_type` | `str` | `project` / `agents` / `architecture` |
| `file_path` | `str` | Tallennuspolut |
| `sections` | `list[str]` | Luodut osiot |

### Esimerkkikoodi

```python
from agents import TechnicalWriterAgent

writer = TechnicalWriterAgent()
result = writer.run(
    action="project",
    query="./",
    project_name="AIDE",
    project_description="AI Development Environment 20-moduulisena agenttina"
)

print(result.file_path)
# Output: ./PROJECT.md

print(result.sections)
# Output: ['Yleiskuva', 'Asennus', 'Käyttö', 'Arkkitehtuuri']
```

---

## APIDocumentationAgent

### Syöte (APIDocumentationInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["analyze", "generate"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | API-tiedosto (esim. app.py) |
| `format` | `str` | ❌ | Generoitava formaatti (openapi/markdown/text) |

### Tuloste (APIDocumentationOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `endpoints` | `list[dict[str, Any]]` | Löydetyt endpointit |
| `schema` | `dict[str, Any]` | OpenAPI-3.0-schema |
| `document` | `str` | Generoitu markdown |
| `total_endpoints` | `int` | Endpointin määrä |

### Esimerkkikoodi

```python
from agents import APIDocumentationAgent

api_doc = APIDocumentationAgent()
result = api_doc.run(
    action="analyze",
    query="src/app.py"
)

print(f"Endpointit: {result.total_endpoints}")
# Output: Endpointit: 5

for ep in result.endpoints:
    print(f"  {ep['method']} {ep['path']} — {ep['description']}")
# Output:
#   GET /api/users — Hae kaikki käyttäjät
#   POST /api/users — Luo uusi käyttäjä
```

---

## UserDocumentationAgent

### Syöte (UserDocumentationInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["generate", "update"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Ominaisuus tai projekti |
| `style` | `str` | ❌ | Tyylisuuntaus (concise/detailed/tutorial) |
| `sections` | `list[str]` | ❌ | Sisällettävät osiot |

### Tuloste (UserDocumentationOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `document` | `str` | Generoitu README |
| `sections_created` | `list[str]` | Luodut osiot |
| `word_count` | `int` | Sanamäärä |
| `estimated_reading_time` | `str` | Arvioitu lukuaika |

### Esimerkkikoodi

```python
from agents import UserDocumentationAgent

user = UserDocumentationAgent()
result = user.run(
    action="generate",
    query="AI API palvelin Pythonilla käyttäen FastAPI:tä"
)

print(result.sections_created)
# Output: ['Ominaisuudet', 'Asennus', 'Käyttö', 'Testaus', 'Deployment']
print(f"Sanoja: {result.word_count} ({result.estimated_reading_time})")
# Output: Sanoja: 847 (3 min)
```

---

## MkDocsAgent

### Syöte (MkDocsInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["generate", "update"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Projektin polku |
| `project_name` | `str` | ✅ | Projektin nimi |
| `modules` | `list[str]` | ❌ | Moduulit dokumentoimiseen |

### Tuloste (MkDocsOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `config` | `dict[str, Any]` | Generoitu mkdocs.yml -rakenne |
| `pages_created` | `list[str]` | Luodut sivut |
| `nav_structure` | `dict[str, list]` | Sivuston navigointirakenne |

### Esimerkkikoodi

```python
from agents import MkDocsAgent

mkdocs = MkDocsAgent()
result = mkdocs.run(
    action="generate",
    query="./",
    project_name="AIDE"
)

print(result.pages_created)
# Output: ['index.md', 'architecture/overview.md', 'agents/director.md', ...]

print(result.nav_structure)
# Output: {'AIDE': ['index'], 'Arkitehtuuri': ['overview', 'modules'], ...}
```

---

## Testikattavuus

```
tests/test_documentation_agents.py — 46 testiä
Kattavuus: 94 %
```

Tärkeimmät testit:
- `test_generate_project_doc`
- `test_api_endpoint_extraction`
- `test_openapi_schema_generation`
- `test_readme_contains_sections`
- `test_mkdocs_config_has_nav`

---

## Liittyvät moduulit

- **Edeltäjä:** ProjectManagerAgent (M2) — dokumentaation luomisen yhteydessä
- **Riippuu:** ResearcherAgent (M3) — projektin rakenteen tuntemiseen
- **Integroi:** ReleaseManagerAgent (M15) — julkaisun yhteydessä

## CLI-käyttö

```bash
aide run "Luo projektin dokumentaatio"         # → TechnicalWriterAgent.project
aide run "Dokumentoi tämän API:n"              # → APIDocumentationAgent.analyze
aide run "Luo README"                          # → UserDocumentationAgent.generate
aide run "Luo MkDocs-sivusto"                    # → MkDocsAgent.generate
```

## Katso myös

- [`modules.md`](../../architecture/modules.md) — kaikki moduulit
- [`agent-lifecycle.md`](../../architecture/agent-lifecycle.md) — agentin elinkaari
- [`dataflow.md`](../../architecture/dataflow.md) — dokumentaation luonti putkessa
