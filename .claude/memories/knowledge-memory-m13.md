---
name: knowledge-memory-m13
description: M13 Knowledge & Memory -agentit ja tietojärjestelmän käyttö
metadata:
  type: project
---

# M13 — Knowledge & Memory: Tiedon tallennus, muisti ja kontekstin kääntäminen

## Agentit

### KnowledgeAgent (`agents/knowledge_agent.py`)
- `agent_type="knowledge"`
- Tietojärjestelmän pitkäaikainen muisti — tallentaa oppimiskokemuksia, projektin päätöksiä ja tekee ne hakukelpoisiksi.
- **Toiminnot:** `store`, `retrieve`, `search`, `index`, `delete`
- **Syöte:** `KnowledgeAgentInput` (operation, knowledge_type, content, tags, query, index_fields, source, knowledge_id)
- **Tuloste:** `KnowledgeAgentOutput` (knowledge_id, entries, index_name, total_found, confidence)
- Tallentaa tiedot JSON-tiedostoon (`.aide_knowledge.json` oletus)
- Automaattinen tunnisteen poiminnaksi: importit, funktiot, luokat, TODO/FIXME-merkinnät
- Haun scoreeraus: sisältö 0.5, tunnisteet 0.3, tyyppi 0.2

### MemoryAgent (`agents/knowledge_agent.py`)
- `agent_type="memory"`
- Käyttäjän istunto- ja pitkäaikaisuuden muisti (session, short_term, long_term).
- **Toiminnot:** `store`, `retrieve`, `list`, `forget`, `clear`
- **Syöte:** `MemoryInput` (store_type, key, value, action, ttl, filter_tags)
- **Tuloste:** `MemoryOutput` (key, value, entries, store_type, remaining_ttl, total_found)
- TTL-tuki lyhyen- ja pitkäaikaisten muistien vanhentumiseen
- Tallentaa JSON-tiedostoon (`.aide_memory.json` oletus)
- LRU-pohjainen kuutos vanhimman poistoon kun max_size ylittyy

### ContextCompilerAgent (`agents/knowledge_agent.py`)
- `agent_type="context_compiler"`
- Yhdistää tiedot lähteistä (tiedostot, merkkijonot) yhteen kontekstiin.
- **Syöte:** `ContextCompilerInput` (sources, target_format, priority_sources, context_filters, max_context_length)
- **Tuloste:** `ContextCompilerOutput` (compiled_context, source_summaries, total_sources, context_length, priority_ranking)
- Tukee AST-suodattimia: imports, classes, functions, errors, docstrings, constants
- Käännösmuodot: json, markdown, text, summary
- Lähdejärjestäminen prioriteettien mukaan

## Vakiot

- `INDEX_TYPES`: 4 tietovarantaa tyyppiä (concept, pattern, snippet, decision)
- `MEMORY_STORE_TYPES`: 3 muistintyyppiä (session, short_term, long_term)

## Testaus

- 64 testiä: `tests/test_knowledge_agent.py`, `tests/test_memory_agent.py`, `tests/test_context_compiler_agent.py`
- 609 testiä kaikkiaan (Alpha 2.3)
- Kaikki testit läpäisti

## Miksi:

M13 tarjoaa tiedon säilyttämisen ja kontekstin kääntämisen AIDE-järjestelmän pitkäaikaiseksi muistoksi. KnowledgeAgent on projektin tietokanta, MemoryAgent on istunnon muisti, ja ContextCompilerAgent on yhteyskääntäjä.

## Kuinka sovellettavaksi:

```python
from agents import KnowledgeAgent, MemoryAgent, ContextCompilerAgent

# Tallenna konsepti
ka = KnowledgeAgent()
ka.run("Tallenna", operation="store", knowledge_type="concept",
       content="Dependency injection on suunnittelumalli...", tags=["python"])

# Muista istuntosessa
mem = MemoryAgent()
mem.run("Muista", action="store", key="user_pref", value="dark_mode", store_type="session")

# Käännä konteksti useista lähteistä
cc = ContextCompilerAgent()
ctx = cc.run("Käännä", sources=["agents/base.py", "agents/developer.py"],
             target_format="summary", context_filters=["imports", "classes"])
```