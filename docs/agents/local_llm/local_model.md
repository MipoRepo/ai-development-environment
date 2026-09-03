# LocalModelAgent (M18 Local LLM)

**Tiedosto:** `agents/local_llm_agent.py`  
**Moduuli:** M18 — Local LLM  
**Status:** ✅ Valmiina  
**Testit:** 54 | **Kattavuus:** 89 %

---

## Tarkoitus

Paiklisten mallien (Ollama, llama.cpp, GGUF) hallinta. Lista, asenna, poista, info, config-toiminnot.

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"local_model"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `list` | Lista asennetuista paikallisista malleista |
| `install` | Asenna uusi malli |
| `remove` | Poista malli |
| `info` | Näytä mallin tiedot |
| `config` | Konfiguuri päivitys |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["list", "install", "remove", "info", "config"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Mallin nimi tai polku |
| `backend` | `str` | ❌ | `ollama`, `llama.cpp`, `gguf` |
| `path` | `str` | ❌ | Asennuspolku |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `models` | `list[dict[str, Any]]` | Mallit (list-toiminto) |
| `model` | `dict[str, Any]` | Yksittäisen mallin tiedot |
| `status` | `str` | Asennus/poistotoimenpiteen tulos |
| `message` | `str` | Tilanneilmoitus |

---

## KNOWN_LOCAL_MODELS

| Malli | Koko | Format |
|---|---|---|
| `llama3:8b-instruct-q4_K_M` | 8B | GGUF |
| `phi3:3.8b-mini-4k-instruct-q4_K_M` | 3.8B | GGUF |
| `gemma:2b-instruct-q4_K_M` | 2B | GGUF |
| `qwen:7b-chat-q4_K_M` | 7B | GGUF |

---

## Esimerikkoodi

```python
from agents import LocalModelAgent

lm = LocalModelAgent()

# Lista mallit
result = lm.run(
    action="list",
    query="*",
    backend="ollama"
)

for model in result.models:
    print(f"  {model['name']} ({model['size']}) — käytettävissä: {model['available']}")

# Asena uusi malli
result = lm.run(
    action="install",
    query="phi3:3.8b-mini-4k-instruct-q4_K_M",
    backend="ollama"
)
print(result.status)
# Output: Status: asennettu

# Tiedot
result = lm.run(
    action="info",
    query="llama3:8b-instruct-q4_K_M"
)
print(f"Koko: {result.model['size']}, Parametrit: {result.model['parameters']}")
# Output: Koko: 4.9 GB, Parametrit: 8.0B
```

---

## Testikattavuus

M18-testit (54) sisältävät:
- `test_list_returns_local_models`
- `test_install_validates_model_name`
- `test_remove_cleans_up_files`
- `test_info_returns_metadata`
- `test_config_updates_settings`
