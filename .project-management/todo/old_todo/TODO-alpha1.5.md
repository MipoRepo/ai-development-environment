# AIDE-projektin TODO-lista (Alpha 1.5)

> Tämä lista seuraa projektin edistymistä **M13** -moduulissa (Knowledge & Memory / Tieto ja muisti).
> **Arkistoitu.** Tämä versio on valmis. Aktiivinen versio on `TODO-alpha1.6.md` (M14 Maintenance).

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

> ⚠️ **Tärkeä muistutus:** AINA ennen kuin teet jotain uutta, varmista että projektimuistisi on ajantasalla. Päiväitä `.claude/memories/project-rules.md` säännöllisesti päätöksillesi.

---

## Tehtävä 13: M13 — Knowledge & Memory  ✅ Valmis
- [x] Totea `KnowledgeAgent`-luokka (`agents/knowledge_agent.py`) — hallitsee tiedon tallentamista, haun ja indeksoinnin
- [x] Totea `MemoryAgent`-luokka — käyttäjän istunto- ja pitkäaikaisuuden muistin hallinta (TTL, filtterit, persistenssi)
- [x] Totea `ContextCompilerAgent`-luokka — kokoaa yhteyttiedot useista lähteistä (file/string) AST-suodattimilla (imports, classes, functions, errors, docstrings, constants) ja muun muotojen (json, markdown, text, summary)
- [x] Lisätty tietomallit: KnowledgeAgentInput/Output, MemoryInput/Output, ContextCompilerInput/Output + INDEX_TYPES ja MEMORY_STORE_TYPES -sanakirjät
- [x] Kirjoita testit (`tests/test_knowledge_agent.py`, `tests/test_memory_agent.py`, `tests/test_context_compiler_agent.py`) — 64 testiä, kaikki läpäisti

---

## 🎯 Alpha 1.5 valmis kun

Kaikki M13 -komponentit (Knowledge, Memory, Context Compiler) on toteutettu ja testattu. Testikattavuus on vähintään 80 %.

**Seuraava käynnistys Promptti (kun olet valmis M14:ään):**
```bash
# Aloita M14 Maintenance -moduulin toteutus:
aide run "Toteuta M14 Maintenance -moduuli: UpgradeAgent, CleanupAgent, DependencyAgent. Lisää automaattinen riippuvuuden päivitystarkistus."
```

---

> **Huom:** Kun olet valmis siirtymään seuraavaan versioon, kirjoita **"Siirry Alpha 1.7"**. Jokainen moduuli saa oman versionumeronsa (Alpha 1.7 = M15, Alpha 1.8 = M16, jne.).
