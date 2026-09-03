# AIDE-projektin TODO-lista (Alpha 2.1)

> Tämä lista seuraa projektin edistymistä **M18** -moduulissa (Local LLM / Paikkinen kielimalli).
> **Arkistoitu.** Tämä versio on valmis. Aktiivinen versio on `TODO-alpha2.2.md` (M19 — MCP & Integrations).

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

> ⚠️ **Tärkeä muistutus:** AINA ennen kuin teet jotain uutta, varmista että projektimuistisi on ajantasalla. Päivitä `.claude/memories/project-rules.md` säännöllisesti päätöksillesi.

---

## Tehtävä 18: M18 — Local LLM  ✅ Valmis

- [x] Totea `LocalModelAgent`-luokka (`agents/local_llm_agent.py`) — paikallisten mallien (Ollama, llama.cpp) hallinta ja konfigurointi
- [x] Totea `ModelRunnerAgent`-luokka — suorittaa päätettä paikallisissa malleissa (prompt → vastaus)
- [x] Totea `QuantizationAgent`-luokka — mallin kvantisointi ja optimointi (GGUF, bitit)
- [x] Lisätty LocalModelInput/Output, ModelRunnerInput/Output, QuantizationInput/Output -mallit
- [x] Lisätty LOCAL_MODEL_ACTIONS, MODEL_RUNNER_ACTIONS, QUANTIZATION_ACTIONS, KNOWN_LOCAL_MODELS, QUANTIZATION_FORMATS, MEMORY_ESTIMATES, OLLAMA_COMMANDS vakiot
- [x] Päivitetty `agents/__init__.py` kaikilla M18-liityksillä ja vakioilla
- [x] Kirjoita testit (`tests/test_local_llm_agent.py`) — 54 testiä, kaikki läpäisti, 89 % kattavuus

---

## 🎯 Alpha 2.1 valmis

Kaikki M18-komponentit (LocalModel, ModelRunner, Quantization) on toteutettu ja testattu. Testikattavuus on 89 %.

Seuraava käynnistys (kun olet valmis M19:een):

```bash
aide run "Toteuta M19 MCP & Integrations -moduuli: MCPIntegrationAgent, APIIntegrationAgent, WebhookAgent."
```

---

> **Huom:** Kun olet valmis siirtymään seuraavaan versioon, kirjoita **"Siirry Alpha 2.2"**. Esim. Alpha 2.2 = M19 (MCP & Integrations).
