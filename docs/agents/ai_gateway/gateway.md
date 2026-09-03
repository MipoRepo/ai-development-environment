# AIGatewayAgent (M17 AI Gateway)

**Tiedosto:** `agents/ai_gateway_agent.py`  
**Moduuli:** M17 — AI Gateway  
**Status:** ✅ Valmiina  
**Testit:** 58 | **Kattavuus:** 96 %

---

## Tarkoitus

Keskitetty AI-mallin käsittely OpenRouterin ja LangChainin kautta. Reitittää, prosessoi ja valvoo mallien terveyttä.

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"ai_gateway"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `route` | Reititä pyyntö oikeaan malliin |
| `process` | Prosessoi merkinnän tai kyselyn |
| `health_check` | Tarkista mallin terveyden tila |
| `list_models` | Lista käytettävistä malleistä |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["route", "process", "health_check", "list_models"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Kysymys tai pyyntö |
| `model` | `str` | ❌ | Kohdemalli |
| `provider` | `str` | ❌ | Palveluntarjoaja |
| `priority` | `str` | ❌ | `cost`, `latency`, `quality`, `balanced` |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `response` | `str` | Mallin vastaus |
| `model_used` | `str` | Käytetty malli |
| `usage` | `dict[str, int]` | Tokenkäyttö (input, output, total) |
| `latency` | `float` | Viive (ms) |
| `healthy` | `bool` | Onko malli terve (health_check) |
| `models` | `list[dict[str, Any]]` | Saatavilla olevat mallit (list_models) |

---

## MODEL_REGISTRY (valinta osista)

| Malli | Palveluntarjoaja | Tyypituki |
|---|---|---|
| `claude-3-opus` | Anthropic | ✅ |
| `claude-3-7-sonnet` | Anthropic | ✅ |
| `gpt-4-turbo` | OpenAI | ✅ |
| `meta-llama-3` | Meta | ✅ |
| `mistral-large` | Mistral | ✅ |

Kokonaan yli 20 mallia on `MODEL_REGISTRY`-sanastossa.

---

## Esimerkkikoodi

```python
from agents import AIGatewayAgent

gateway = AIGatewayAgent()

# Prosessoi kysymys
result = gateway.run(
    action="process",
    query="Selitä Pythonin dekorrit",
    priority="balanced"
)

print(result.response)
print(f"Malli: {result.model_used}")
print(f"Tokenit: {result.usage['total']}")

# Reititä haluttuun malliin
result = gateway.run(
    action="route",
    query="Kirjoita tiivis koodi Pythonissa",
    model="claude-3-7-sonnet"
)
print(f"Käytetty: {result.model_used}")

# Terveys tarkistus
result = gateway.run(
    action="health_check",
    query="openrouter"
)
print(f"Terven: {result.healthy}")
```

---

## Testikattavuus

M17-testit (58) sisältävät:
- `test_process_returns_response`
- `test_route_selects_correct_model`
- `test_health_check_returns_bool`
- `test_all_models_in_registry`
- `test_usage_tracked_correctly`
