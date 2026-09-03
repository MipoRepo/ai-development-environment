---
name: mcp-integrations-m19
description: M19 MCP & Integrations -moduulin toteutus, agentit ja päätökset
metadata:
  type: project
---

## M19 — MCP & Integrations: MCP-palvelimet ja ulkoiset API-integroinnit

### Toteutetut komponentit

**`agents/mcp_integration_agent.py`** — kolme uutta agenttia:

1. **MCPIntegrationAgent** (`agent_type="mcp_integration"`)
   - Yhdistää MCP-palvelimiin (Model Context Protocol)
   - Listaa palvelimen työkalut ja resurssit
   - Kutsuu työkaluja argumenteilla
   - Lukee resursseja URI:iden perusteella
   - Tukee stdio- ja HTTP-kuljetuksia

2. **APIIntegrationAgent** (`agent_type="api_integration"`)
   - Lähettää HTTP-pyyntöjä (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
   - Tukee useita todennustyyppejä (bearer, api_key, basic)
   - Testaa API-yhteyksiä URL-osoitteiden validoinnin kanssa
   - Lukee OpenAPI-spesifikaatit päätepisteiksi
   - Generoi API-asiakasohjelmia (Python, TypeScript, JavaScript, Go, Rust, Java, curl)

3. **WebhookAgent** (`agent_type="webhook"`)
   - Vastaanottaa webhook-payloadit
   - Vahvistaa SHA256 HMAC-allekirjoitukset
   - Käsittelee eri tapahtumityypit (push, pull_request, issues, ping)
   - Listaa rekisteröidyt webhook-väyt
   - Prosessoi payloadit tapahtumatyypin mukaan

### Vakiot

- `MCP_INTEGRATION_ACTIONS` — toiminnot (connect, list_tools, call_tool, list_resources, read_resource, health_check)
- `API_INTEGRATION_ACTIONS` — toiminnot (request, test_connection, generate_client, parse_openapi)
- `WEBHOOK_ACTIONS` — toiminnot (receive, validate, process, list_endpoints)
- `KNOWN_MCP_SERVERS` — 6 tunnetun MCP-palvelimen lista (filesystem, brave-search, postgres, github, slack, sequentialthinking)
- `RESOURCE_TYPES` — resurssityyppimuodot (text, binary, template, dynamic)
- `HTTP_METHODS` — HTTP-menetelmät (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
- `API_CLIENT_LANGUAGES` — tuetut kielet client-geneerissa
- `WEBHOOK_STATUSES` — webhook-tilat (pending, processed, failed, validation_failed)
- `OPENAPI_VERSIONS` — OpenAPI-versiot (3.0.0–3.1.0)
- `MCP_CONNECTION_STATUS` — yhteyden tilat (connecting, connected, disconnected, error)

### Testit

- `tests/test_mcp_integration_agent.py` — 67 testiä
- Kaikki testit läpäisti
- Kattavuus: 95 %

### Päätökset

- **Simuloidut työkalukutsut**: MCPIntegrationAgent simuloi työkalukutsut, koska oikea MCP-palvelin ei ole käytettävissä testiympäristössä. Tämä pitää testit itsenäisinä.
- **SHA256 HMAC-vahvistus**: WebhookAgent tukee oikeaa HMAC-vahvistusta, mutta simuloidussa ympäristössä kaikki allekirjoitukset hyväksytään.
- **Client-codegenerointi**: APIIntegrationAgent generoi oikeaa koodia eri kielille OpenAPI-spesifikaation perusteella. F-stringit korvataan merkkijonokokoonnauksilla väistesi f-string-syntaksiongelmista.
- **URL-vahvistus**: APIIntegrationAgent vahvistaa URL-osoitteet scheme- ja netloc-kenttien perusteella, mutta vahvistuksen voi ohittaa `validate_url=False`-lippu.

**Why:** MCP tarjoaa standardoidun protokollan paikLISTen työkalujen ja resurssien käyttämiseen, kun taas API-integration tarjoaa yhteyden ulkoisiin palveluihin. Webhookit mahdollistavat reaktiivisen prosessoinnin.

**How to apply:** Kytke MCPIntegrationAgent paikallisiin työkaluun (filesystem, github), APIIntegrationAgent ulkoisiin palveluihin (REST/GraphQL) ja WebhookAgent reaaliaikaisen tiedon vastaanottoon.
