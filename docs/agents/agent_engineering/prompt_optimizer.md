# PromptOptimizerAgent (M16 Agent Engineering)

**Tiedosto:** `agents/agent_engineering_agent.py`  
**Moduuli:** M16 — Agent Engineering  
**Status:** ✅ Valmiina  
**Testit:** 61 | **Kattavuus:** 85 %

---

## Tarkoitus

Promptien optimointi. Sisältää tokene-arviointia, rakenteen analyysiä, parannusehdotuksia ja optimointipisteet.

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"prompt_optimizer"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `optimize` | Optimoi promptia tokene- ja selkeystarkistuksilla |
| `analyze` | Analyysi promptin rakenteesta |
| `estimate` | Arvioi tokenimäärää ennen lähettöä |
| `suggest` | Ehdottaa parannuksia promptille |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["optimize", "analyze", "estimate", "suggest"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Prompti tai tiedoston polku |
| `model` | `str` | ❌ | Käytetty malli tokenilaskuun |
| `max_tokens` | `int` | ❌ | Rajoitus (oletus: 4096) |
| `language` | `str` | ❌ | Kieli |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `optimized_prompt` | `str` | Optimoitu prompti |
| `token_estimate` | `int` | Arvioitu tokenimäärä |
| `suggestions` | `list[str]` | Parannusehdotuksia |
| `improvement_points` | `list[dict[str, Any]]` | Parannuskohdat |

---

## Esimerkkikoodi

```python
from agents import PromptOptimizerAgent

optimizer = PromptOptimizerAgent()
result = optimizer.run(
    action="optimize",
    query="Kerää minulle tietoja Pythonista jokaiseen tulkin vaikeaan kysymykseen johon niko pysyvästi."
)

print(f"Alkup. prompt: {len(result.original)} merkkiä")
print(f"Optimoitu: {len(result.optimized_prompt)} merkkiä")
# Output: Alkup. prompt: 156 merkkiä
# Output: Optimoitu: 98 merkkiä

print("Parannusehdotukset:")
for suggestion in result.suggestions:
    print(f"  → {suggestion}")

# Tokenien arviointi
estimate = optimizer.run(
    action="estimate",
    query="Selitä Pythonin dekorrit",
    model="claude-3-opus-2048"
)
print(f"Tokenit: {estimate.token_estimate}")
# Output: Tokenit: 45
```

---

## PROMPT_OPTIMIZATION_TIPS

| Vihje | Kuvaus |
|---|---|
| Selkeys | Vältä turhia sanoja |
| Rakenne | Käytä selkeitä osioita |
| Context | Anna riittävästi taustaa |
| Tokenit | Pidä lyhyet |

---

## Testikattavuus

M16-testit (61) sisältävät:
- `test_optimize_reduces_token_count`
- `test_analyze_identifies_issues`
- `test_estimate_within_range`
- `test_suggest_improves_clarity`
