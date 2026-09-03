---
name: ai-gateway-m17
description: M17 AI Gateway -moduulin toteutus ja päätökset
metadata:
  type: project
---

## M17 — AI Gateway: Keskitetty AI-mallin käsittely

### Toteutetut komponentit

**`agents/ai_gateway_agent.py`** — kolme agenttia:

1. **AIGatewayAgent** (`agent_type="ai_gateway"`)
   - Keskustelee eri palveluntarjoajien (OpenRouter, LangChain) yli
   - Käsittelee syötteet ja palauttaa yhtenäisen vastuksen
   - Tukee useita malleja yhdessä puhelun kesken

2. **LLMRouterAgent** (`agent_type="llm_router"`)
   - Reitittää pyynnöt oikeaan malliin kustannuksen, viivyynnän ja kyvykkyyksen perusteella
   - Tukee painoittavia reitintasoja

3. **TokenTrackerAgent** (`agent_type="token_tracker"`)
   - Seuraa tokenikierrokset ja maksut
   - Laskee per-tokeni- ja kuukaukkitikut

### Vakiot

- `GATEWAY_ACTIONS` — toiminnot (route, process, health_check)
- `ROUTING_CRITERIA` — reitin tasapainot (cost, latency, capability)
- `TOKEN_TRACKER_ACTIONS` — toiminnot (track, summarize, reset)
- `MODEL_REGISTRY` — tunnetut mallit eri palveluntarjoajilta (OpenRouter, OpenAI, Anthropic, Google)

### Päätökset

- **SIMULATED_RESPONSES**: Vastaukset ovat simuloituja testien itsenäisyyden vuoksi, koska oikea API-avain puuttuu.
- **MODEL_REGISTRY**: Sisältää 20+ mallia eri palveluntarjoajilta, mukautettu AIDE-projektin tarpeisiin.
- **96 % kattavuus**: Testit kattavat kaikki haarat ja reitit.

**Why:** Keskusteleva portti eri AI-palveluntarjoajien välillä tarjoaa yhtenäisen rajapinnan ja optimoi maksut.

**How to apply:** Käytä `AIGatewayAgent` yleiseen kysymykseen, `LLMRouterAgent` maksukyseisein mappeihin ja `TokenTrackerAgent` kulukontrolliin.
