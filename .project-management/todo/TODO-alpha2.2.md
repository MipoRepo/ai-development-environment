# AIDE-projektin TODO-lista (Alpha 2.2)

> Tämä lista seuraa projektin edistymistä **M19** -moduulissa (MCP & Integrations / Mallipalvelun yhteydet).
> **Arkistoitu.** Tämä versio on valmis. Aktiivinen versio on `TODO-alpha2.3.md` (M20 — GUI / Control Center).

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

> ⚠️ **Tärkeä muistutus:** AINA ennen kuin teet jotain uutta, varmista että projektimuistisi on ajantasalla. Päivitä `.claude/memories/project-rules.md` säännöllisesti päätöksillesi.

---

## Tehtävä 19: M19 — MCP & Integrations  ✅ Valmis

- [x] Totea `MCPIntegrationAgent`-luokka (`agents/mcp_integration_agent.py`) — MCP-palvelinten ja -työkalujen yhdistäminen
- [x] Totea `APIIntegrationAgent`-luokka — ulkoisten REST/GraphQL-palveluiden integrointi
- [x] Totea `WebhookAgent`-luokka — webhook-jen vastaanottaminen ja käsittely
- [x] Lisätty MCPIntegrationInput/Output, APIIntegrationInput/Output, WebhookInput/Output -mallit
- [x] Lisätty MCP_INTEGRATION_ACTIONS, API_INTEGRATION_ACTIONS, WEBHOOK_ACTIONS, KNOWN_MCP_SERVERS, RESOURCE_TYPES, HTTP_METHODS, API_CLIENT_LANGUAGES, WEBHOOK_STATUSES, OPENAPI_VERSIONS, MCP_CONNECTION_STATUS vakiot
- [x] Päivitetty `agents/__init__.py` kaikilla M19-viehimilla ja -vakioilla
- [x] Kirjoita testit (`tests/test_mcp_integration_agent.py`) — 67 testiä, kaikki läpäisti, 95 % kattavuus

---

## 🎯 Alpha 2.2 valmis

Kaikki M19-komponentit (MCPIntegration, APIIntegration, Webhook) on toteutettu ja testattu. Testikattavuus on 95 %.

Seuraava käynnistys (kun olet valmis M20:een):

```bash
aide run "Toteuta M20 GUI / Control Center -moduuli."
```

---

> **Huom:** Kun olet valmis siirtymään seuraavaan versioon, kirjoita **"Siirry Alpha 2.3"**. Esim. Alpha 2.3 = M20 (GUI / Control Center).
