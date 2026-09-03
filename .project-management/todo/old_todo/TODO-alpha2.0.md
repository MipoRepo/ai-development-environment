# AIDE-projektin TODO-lista (Alpha 2.0)

> Tämä lista seuraa projektin edistymistä **M17** -moduulissa (AI Gateway / Tekoälyportti).
> **Arkistoitu.** Tämä versio on valmis. Aktiivinen versio on `TODO-alpha2.1.md` (M18 — Local LLM).

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

> ⚠️ **Tärkeä muistutus:** AINA ennen kuin teet jotain uutta, varmista että projektimuistisi on ajantasalla. Päivitä `.claude/memories/project-rules.md` säännöllisesti päätöksillesi.

---

## Tehtävä 17: M17 — AI Gateway  ✅ Valmis

- [x] Totea `AIGatewayAgent`-luokka (`agents/ai_gateway_agent.py`) — keskitetty AI-mallin käsittely (OpenRouter, LangChain, mallien vaihto)
- [x] Totea `LLMRouterAgent`-luokka — reitittääpytää pyynnöt oikeaan malliin (kustannus, latency, capability-tasapaino)
- [x] Totea `TokenTrackerAgent`-luokka — seuraa tokenikulumit ja maksut (per tokeni, kuutiskulu)
- [x] Lisätty AIGatewayInput/Output, LLMRouterInput/Output, TokenTrackerInput/Output -mallit
- [x] Lisätty GATEWAY_ACTIONS, ROUTING_CRITERIA, TOKEN_TRACKER_ACTIONS, MODEL_REGISTRY, ROUTING_CRITERIA vakiot
- [x] Päivitetty `agents/__init__.py` kaikilla M17-viehimilla ja -vakioilla
- [x] Kirjoita testit (`tests/test_ai_gateway_agent.py`) — 58 testiä, kaikki läpäisti, 96 % kattavuus

---

## 🎯 Alpha 2.0 valmis

Kaikki M17-komponentit (AIGateway, LLMRouter, TokenTracker) on toteutettu ja testattu. Testikattavuus on 96 %.

**Seuraava käynnistys (kun olet valmis M18:een):**

```bash
aide run "Toteuta M18 Local LLM -moduuli: LocalModelAgent, ModelRunnerAgent, QuantizationAgent."
```

---

> **Huom:** Kun olet valmis siirtymään seuraavaan versioon, kirjoita **"Siirry Alpha 2.1"**. Esim. Alpha 2.1 = M18 (Local LLM).
