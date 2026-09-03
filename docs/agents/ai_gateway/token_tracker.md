# TokenTrackerAgent (M17 AI Gateway)

**Tiedosto:** `agents/ai_gateway_agent.py`  
**Moduuli:** M17 — AI Gateway  
**Status:** ✅ Valmiina  
**Testit:** 58 | **Kattavuus:** 96 %

---

## Tarkoitus

Seurata tokenikulumat ja maksut prosessin yli. Seurauksia voidaan tarkastella, yhtmetään ja nollata.

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"token_tracker"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `track` | Tallenna tokenikulumat yhtä istuntoa varten |
| `summarize` | Yhteenveto tokeneista ja maksuista |
| `reset` | Nollaa kaikki kulumat |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["track", "summarize", "reset"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Mallin nimi tai kysymys |
| `input_tokens` | `int` | ❌ | Syötetokenien määrä |
| `output_tokens` | `int` | ❌ | Tulostetokenien määrä |
| `cost` | `float` | ❌ | Kulut (USD) |
| `session_id` | `str` | ❌ | Istunnon tunniste |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `total_tokens` | `int` | Kaikki tokenit (input + output) |
| `total_cost` | `float` | Kuluvat kokonaisuudessa (USD) |
| `session_summary` | `dict[str, Any]` | Istunnon yhteenveto |
| `daily_totals` | `dict[str, Any]` | Päivittäiskäsittelyt |
| `models_used` | `list[str]` | Käytetyt mallit |

---

## TOKEN_TRACKER_ACTIONS

| Toimiinto | Kuvaus |
|---|---|
| `track` | Tallenna yhden kutsun tiedot |
| `summarize` | Kaikki yhteensä / keskiarvo / prosentit |
| `reset` | Nollaa kaikki tiedot |

---

## Esimerikkoodi

```python
from agents import TokenTrackerAgent

tracker = TokenTrackerAgent()

# Seuraa yhtä kutsua
result = tracker.run(
    action="track",
    query="claude-3-7-sonnet",
    input_tokens=456,
    output_tokens=1234,
    cost=0.018,
    session_id="sess_001"
)

print(f"Tokenit: {result.total_tokens}")
# Output: Tokenit: 1690

# Yhteenveto
result = tracker.run(
    action="summarize",
    query="*"
)

print(f"Kokonaiskustannus: ${result.total_cost}")
# Output: Kokonaiskustannus: $4.23

print(result.models_used)
# Output: ['claude-3-7-sonnet', 'gpt-4-turbo', 'meta-llama-3']
```

---

## CLI-integraatio

```bash
aide status                         # Näyttää tokenikulumat ControlCentressä (M20)
```

---

## Testikattavuus

M17-testit (58) sisältävät:
- `test_track_records_tokens`
- `test_summarize_aggregates_costs`
- `test_daily_totals_calculated`
- `test_reset_clears_all_data`
