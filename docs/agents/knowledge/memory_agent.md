# MemoryAgent (M13 Knowledge & Memory)

**Tiedosto:** `agents/knowledge_agent.py`  
**Moduuli:** M13 — Knowledge & Memory  
**Status:** ✅ Valmiina  
**Testit:** 64 (yhteinen M13) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Istunto- ja pitkäaikaismuistit. Tukee kolmea muistintyyppiä: `session`, `short_term`, `long_term`. TTL-ajot, tag-suodatus, `forget`- ja `clear`-toiminnot. Tiedostopohjainen persistenssi.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"memory"` |

---

## Syöte (MemoryInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["store", "retrieve", "forget", "clear", "summarize"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Muistin sisältö tai hakusana |
| `memory_type` | `str` | ❌ | `MEMORY_STORE_TYPES` (session, short_term, long_term) |
| `tags` | `list[str]` | ❌ | Muiston tunnisteet |
| `ttl` | `int` | ❌ | Ikä (sekuntia) ennen vankenemista |
| `memory_id` | `str` | ❌ | Muistin ID (retrieve/forget-toiminnoissa) |

---

## Tuloste (MemoryOutput)

| Kentty | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `memory_id` | `str` | Luodun muistin ID |
| `results` | `list[dict[str, Any]]` | Haetut muistit |
| `total_found` | `int` | Muistien lukumäärä |
| `summarized` | `bool` | Onko yhteennetty |
| `cleared` | `int` | Tyhjennettyjen muisten määrä (clear-toiminto) |
| `expired` | `int` | Vanentuneiden muistien määrä |

---

## Esimerikkoodi

```python
from agents import MemoryAgent

mem = MemoryAgent()

# Istmuksen muisti (automaattinen)
result = mem.run(
    action="store",
    query="Käytä SHA256 HMAC webhook-allekirjoituksiin.",
    memory_type="session"
)
print(result.memory_id)

# Lyhyt aika (10 minuuttia)
result = mem.run(
    action="store",
    query="Tämä on tärkeitä tietoja projektista.",
    memory_type="short_term",
    ttl=600,  # 10 minuuttia
    tags=["project", "important"]
)

# Haku
result = mem.run(
    action="retrieve",
    query="HMAC",
    memory_type="long_term"
)
print(f"Löydetty: {result.total_found} muistia")

# Vanhentuneiden poisto
forgotten = mem.run(
    action="forget",
    memory_id="mem-abc123"
)
```

---

## MEMORY_STORE_TYPES

| Tyyppi | Kuvaus |
|---|---|
| `session` | Istunnon aikana voimassa oleva muisti |
| `short_term` | Lyhytikäinen (TTL määriteltävissä) |
| `long_term` | Pysyvä muisti |

---

## Testikattavuus

M13-testit (64) sisältävät:
- `test_store_and_retrieve_session_memory`
- `test_short_term_with_ttl`
- `test_forget_removes_memory`
- `test_retrieve_by_tag`
- `test_ttl_expiration`
