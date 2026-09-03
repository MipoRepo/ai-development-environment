# MCPIntegrationAgent (M19 MCP & Integrations)

**Tiedosto:** `agents/mcp_integration_agent.py`  
**Moduuli:** M19 — MCP & Integrations  
**Status:** ✅ Valmiina  
**Testit:** 67 | **Kattavuus:** 95 %

---

## Tarkoitus

Yhdistää MCP-palvelimiin (Model Context Protocol) paikallisten työkalujen ja resurssien käsittelyyn. Tukee stdio- ja HTTP-kuljetuksia.

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"mcp_integration"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `connect` | Yhdistä MCP-palvelimeen |
| `list_tools` | Lista saatavilla olevat työkalut |
| `call_tool` | Kutsu työkalu argumenteilla |
| `list_resources` | Lista resurssit |
| `read_resource` | Lue resurssi URI:n avulla |
| `health_check` | Tarkista palvelimen terveys |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["connect", "list_tools", "call_tool", "list_resources", "read_resource", "health_check"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Palvelimen URL tai haku |
| `transport` | `str` | ❌ | `stdio`, `http` |
| `server` | `str` | ❌ | Palvelimen nimi tai polku |
| `tool_name` | `str` | ❌ | Kutsuttavan työkalun nimi |
| `arguments` | `dict[str, Any]` | ❌ | Työkalun argumentit |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `tools` | `list[dict[str, Any]]` | Työkalut (list_tools) |
| `result` | `Any` | Työkalun paluuarvo (call_tool) |
| `resources` | `list[dict[str, Any]]` | Resurssit (list_resources) |
| `content` | `str` | Resurssin sisältö (read_resource) |
| `connection_status` | `str` | `MCP_CONNECTION_STATUS` |
| `server_info` | `dict[str, Any]` | Palvelimen tiedot |

---

## KNOWN_MCP_SERVERS

| Palvelin | Tyyppi | Kuvaus |
|---|---|---|
| `filesystem` | stdio | Paikallisen tiedostojärjestelmät |
| `brave-search` | stdio | Brave-haku |
| `postgres` | stdio | PostgreSQL-tietokanta |
| `github` | stdio | GitHub-integraatio |
| `slack` | stdio | Slack-viestit |
| `sequentialthinking` | stdio | Jatkuva ajattelu |

---

## Esimerkkikoodi

```python
from agents import MCPIntegrationAgent

mcp = MCPIntegrationAgent()

# Yhdistä palvelimeen
result = mcp.run(
    action="connect",
    server="filesystem",
    transport="stdio"
)
print(f"Tila: {result.connection_status}")
# Output: Tila: connected

# Lista työkalut
result = mcp.run(
    action="list_tools",
    query="*"
)

for tool in result.tools:
    print(f"  {tool['name']}: {tool['description']}")
# Output:
#   read_file: Lukee tiedoston
#   write_file: Kirjoittaa tiedostoon
#   list_directory: Listaa hakemistosisällöt

# Kutsu työkalu
result = mcp.run(
    action="call_tool",
    tool_name="read_file",
    arguments={"path": "/src/main.py"}
)
print(result.result)
# Output: def hello_world(): print("Hello World!")

# Resurssit
result = mcp.run(
    action="list_resources",
    query="*"
)
for res in result.resources:
    print(f"  {res['uri']}: {res['type']}")
```

---

## MCP_CONNECTION_STATUS

| Tila | Kuvaus |
|---|---|
| `connecting` | Yhteyttä muodostuissaan |
| `connected` | Yhteys muodostettu |
| `disconnected` | Yhteys katkennut |
| `error` | Yhteysvirhe |

---

## Testikattavuus

M19-testit (67) sisältävät:
- `test_connect_to_filesystem_server`
- `test_list_tools_returns_valid_tools`
- `test_call_tool_with_arguments`
- `test_read_resource_by_uri`
- `test_health_check_detects_server_status`

Simulointi: oikea MCP-palvelin ei ole käytettävissä testiympäristössä — kaikki työkalukutsut simuloidaan.
