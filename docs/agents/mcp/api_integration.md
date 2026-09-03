# APIIntegrationAgent (M19 MCP & Integrations)

**Tiedosto:** `agents/mcp_integration_agent.py`  
**Moduuli:** M19 — MCP & Integrations  
**Status:** ✅ Valmiina  
**Testit:** 67 | **Kattavuus:** 95 %

---

## Tarkoitus

Ulkoisten REST/GraphQL API-rajapintojen integrointi. Tukee useita todennustyyppejä, URL-vahvistuksen, OpenAPI-spesifikaatien lukemista ja API-asiakasohjelmien generointia 7 kielellä.

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"api_integration"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `request` | Lähettää HTTP-pyyntöjä |
| `test_connection` | Testaa yhteyttä URL-osoitteiden validoinnin kanssa |
| `generate_client` | Generoi API-asiakasohjelman |
| `parse_openapi` | Lukee OpenAPI-spesifikaatit päätepisteiksi |

---

## Syöte

| Kenttelu | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["request", "test_connection", "generate_client", "parse_openapi"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | API-URL tai speci-fikointi |
| `method` | `str` | ❌ | `HTTP_METHODS` (GET, POST, PUT, ...) |
| `headers` | `dict[str, str]` | ❌ | Otsikot |
| `params` | `dict[str, Any]` | ❌ | Kyselyparametrit |
| `body` | `dict[str, Any]` | ❌ | Pyynnöntävaiheen data |
| `auth_type` | `str` | ❌ | `bearer`, `api_key`, `basic` |
| `auth_token` | `str` | ❌ | Todennusavain |
| `language` | `str` | ❌ | `API_CLIENT_LANGUAGES` (generate_client-toiminnossa) |
| `validate_url` | `bool` | ❌ | Validoidaanko URL (oletus: `True`) |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `response` | `dict[str, Any]` | HTTP-vastaus (request) |
| `endpoints` | `list[dict[str, Any]]` | Päätepisteet (parse_openapi) |
| `client_code` | `str` | Generoitu asiakasohjelma (generate_client) |
| `language` | `str` | Käytetty kieli |
| `connection_status` | `str` | `connected` / `failed` |
| `openapi_version` | `str` | OpenAPI-versio |

---

## API_CLIENT_LANGUAGES

| Kieli | Kuvaus |
|---|---|
| `python` | Python `requests`-kirjasto |
| `typescript` | TypeScript (axios) |
| `javascript` | JavaScript (fetch) |
| `go` | Go (net/http) |
| `rust` | Rust (reqwest) |
| `java` | Java (HttpClient) |
| `curl` | curl-komento |

---

## Esimerkkikoodi

```python
from agents import APIIntegrationAgent

api = APIIntegrationAgent()

# HTTP-pyyntö
result = api.run(
    action="request",
    query="https://api.github.com/users/octocat",
    method="GET",
    auth_type="bearer",
    auth_token="ghp_xxx"
)

print(f"Status: {result.response['status_code']}")
# Output: Status: 200
print(result.response['body'])

# Testaa yhteys
result = api.run(
    action="test_connection",
    query="https://api.stripe.com/v1/customers"
)
print(f"Yhteys: {result.connection_status}")
# Output: Yhteys: connected

# Generoi Python-client
result = api.run(
    action="generate_client",
    query="https://api.openweathermap.org/data/3.0",
    language="python"
)

print(result.client_code[:100])
# Output: import requests\n\nclass WeatherAPIClient:\n    def __init__(self, ...

# OpenAPI-spesifikaation luku
result = api.run(
    action="parse_openapi",
    query="https://petstore3.swagger.io/api/v3/openapi.json"
)

print(f"OpenAPI versio: {result.openapi_version}")
print(f"Endpointit: {len(result.endpoints)}")
```

---

## URL-vahvistus

```python
from urllib.parse import urlparse

parsed = urlparse("https://api.example.com/v1/users")
if not parsed.scheme or not parsed.netloc:
    raise ValueError("Virheellinen URL")
```

Raide voidaan ohettaa `validate_url=False`-lipulla.

---

## Testikattavuus

M19-testit (67) sisältävät:
- `test_request_returns_response`
- `test_connection_test_validates_url`
- `test_generate_client_for_python`
- `test_generate_client_for_typescript`
- `test_parse_openapi_extracts_endpoints`
- `test_auth_types_supported`
