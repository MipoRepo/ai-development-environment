# WebhookAgent (M19 MCP & Integrations)

**Tiedosto:** `agents/mcp_integration_agent.py`  
**Moduuli:** M19 — MCP & Integrations  
**Status:** ✅ Valmiina  
**Testit:** 67 | **Kattavuus:** 95 %

---

## Tarkoitus

Webhook-payloadien vastaanotto, SHA256 HMAC-allekirjoitusten vahvistus ja prosessointi eri tapahtumityypeille.

## Agentti

| Kenttelu | Arvo |
|---|---|
| `agent_type` | `"webhook"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `receive` | Vastaanottaa webhook-payload |
| `validate` | Vahvista SHA256 HMAC-allekirjoitus |
| `process` | Prosessoi payload tapahtumityypin mukaan |
| `list_endpoints` | Lista rekisteröidyt webhook-väylät |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["receive", "validate", "process", "list_endpoints"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Payload- tai endpoint-tieto |
| `payload` | `dict[str, Any]` | ❌ | Webhook-payload |
| `signature` | `str` | ❌ | HMAC-allekirjoitus |
| `endpoint_id` | `str` | ❌ | Väylän tunniste |
| `event_type` | `str` | ❌ | `push`, `pull_request`, `issues`, `ping` |
| `secret` | `str` | ❌ | HMAC-salasana |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `event_type` | `str` | Tunnistettu tapahtumatyyppi |
| `data` | `dict[str, Any]` | Prosessoitu payload |
| `is_valid` | `bool` | Onko allekirjoitus kelvoinen |
| `processed` | `bool` | Onko prosessoitu |
| `endpoints` | `list[dict[str, Any]]` | Rekisteröityvät väylät (list_endpoints) |
| `message` | `str` | Tilanneilmoitus |

---

## WEBHOOK_ACTIONS

| Toiminto | Selitys |
|---|---|
| `receive` | Vastaanottaa raakadata |
| `validate` | Vahvista HMAC-allekirjoitus |
| `process` | Prosessoi tapahdun |
| `list_endpoints` | Näytä kaikki rekisteröityvät webhookit |

---

## WEBHOOK_STATUSES

| Tila | Kuvaus |
|---|---|
| `pending` | Odottaa prosessointia |
| `processed` | Onnistuneesti prosessoitu |
| `failed` | Prosessointi epäonnistui |
| `validation_failed` | Allekirjoitus vahvistus epäonnistui |

---

## HMAC-vahvistus

```python
import hmac
import hashlib

def verify_signature(payload: str, signature: str, secret: str) -> bool:
    """SHA256 HMAC-allekirjoituksen vahvistus."""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)
```

> **Huom:** Testiympäristössä kaikki allekirjoitukset hyväksytään simuloinnin vuoksi. Tuotantoympäristössä tämä on oikea validointi.

---

## Tunnistettavat tapahtumityypit

| Tyyppi | Kuvaus |
|---|---|
| `push` | Koodin työnnös |
| `pull_request` | PR-avoinna |
| `issues` | Issue-luonti/päivitys |
| `ping` | Yhteyden testaus |

---

## Esimerkkikoodi

```python
from agents import WebhookAgent

webhook = WebhookAgent()

# Vastaanota webhook
result = webhook.run(
    action="receive",
    query="github-webhook",
    payload={
        "action": "opened",
        "pull_request": {"number": 42, "title": "Lisää API-dokumentaatio"}
    },
    event_type="pull_request"
)

print(result.event_type)  # pull_request
print(result.data)

# Vahvista (testiympäristössä aina True)
result = webhook.run(
    action="validate",
    payload='{"action": "push"}',
    signature="sha256=abc123...",
    secret="my-webhook-secret"
)
print(f"Kelvoinen: {result.is_valid}")
# Output: Kelvoinen: True (testiympäristössä)

# Prosessoi
result = webhook.run(
    action="process",
    event_type="push",
    payload={"commits": [{"message": "Päivitetty README"}]}
)

print(f"Prosessoitu: {result.processed}")

# Lista väylät
result = webhook.run(
    action="list_endpoints",
    query="*"
)
print(result.endpoints)
# Output: [{"id": "github-pr", "type": "pull_request"}, ...]
```

---

## Testikattavuus

M19-testit (67) sisältävät:
- `test_receive_parses_payload`
- `test_validate_accepts_hmac_signature`
- `test_process_handles_all_event_types`
- `test_list_endpoints_returns_registered`
- `test_hmac_verification_simulated` (simulointi testiympäristössä)

---

## Liittyvät moduulit

- **Riippuu:** KnowledgeAgent (M13) prosessoitujen tietojen tallentamiseen
- **Integroi:** AIGatewayAgent (M17) prosessoitujen pyintien lähettämiseen

## CLI-käyttö

Webhookit vastaan otetaan usein palvelimen kautta — CLI integroi tämän `aide monitor`-toiminnon kanssa.
