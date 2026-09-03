# KnowledgeAgent (M13 Knowledge & Memory)

**Tiedosto:** `agents/knowledge_agent.py`  
**Moduuli:** M13 — Knowledge & Memory  
**Status:** ✅ Valmiina  
**Testit:** 64 (yhteinen M13) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Tiedon tallennus, hakeminen ja indeksointi. Automaattisesti aiheuttaa tunnisteet tiedoston sisällöstä. Tiedostopohjainen persistenssi.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"knowledge"` |

---

## Syöte (KnowledgeAgentInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["store", "retrieve", "search", "index", "delete"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Hakusana tai tiedoston polku |
| `content` | `str` | ❌ | Tallennettava sisältö |
| `tags` | `list[str]` | ❌ | Tunnisteet |
| `knowledge_id` | `str` | ❌ | ID (store/retrieve/delete-toiminnoissa) |
| `index_type` | `str` | ❌ | `INDEX_TYPES` (keyword, semantic, tag) |

---

## Tuloste (KnowledgeAgentOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `knowledge_id` | `str` | Tallennetun tiedon ID |
| `results` | `list[dict[str, Any]]` | Haun/tuloksen viemät tiedot |
| `total_found` | `int` | Löydettyjen nimikkeiden määrä |
| `indexed` | `bool` | Onko indeksoitu |
| `message` | `str` | Tilanneilmoitus |
| `error` | `str \| None` | Virhe |

---

## Esimerikkoodi

```python
from agents import KnowledgeAgent

kb = KnowledgeAgent()

# Tallennus
store_result = kb.run(
    action="store",
    content="GraphQL on parempi kuin REST kompleksisissa sovelluksissa.",
    tags=["api", "graphql", "architecture"]
)

print(store_result.knowledge_id)
# Output: kn-abc123

# Haku
search_result = kb.run(
    action="search",
    query="API-arkkitehtuuri",
    index_type="keyword"
)

print(f"Löydetty: {search_result.total_found}")
for r in search_result.results:
    print(f"  {r['content'][:50]}...")

# Haetaan ID:llä
retrieve_result = kb.run(
    action="retrieve",
    knowledge_id="kn-abc123"
)

print(retrieve_result.results[0]["content"])
```

---

## INDEX_TYPES

| Tyyppi | Kuvaus |
|---|---|
| `keyword` | Avainsaitehaku |
| `semantic` | Semanttinen haku |
| `tag` | Tunnustehaku |

---

## Testikattavuus

M13-testit (64) sisältävät:
- `test_store_and_retrieve_knowledge`
- `test_search_returns_relevant_results`
- `test_auto_tags_generated`
- `test_delete_removes_knowledge`
- `test_index_creates_keyword_index`
