# LLMRouterAgent (M17 AI Gateway)

**Tiedosto:** `agents/ai_gateway_agent.py`  
**Moduuli:** M17 — AI Gateway  
**Status:** ✅ Valmiina  
**Testit:** 58 | **Kattavuus:** 96 %

---

## Tarkoitus

Reitittää pyynnöt oikeaan malliin kustannuksen, viiveen ja kyvykkyyyden perusteella. Käyttää painoitettua pisteytystä valitun mallin valitsemiseen.

## Agentti

| Kenttelo | Arvo |
|---|---|
| `agent_type` | `"llm_router"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `route` | Valitse malli pyynnön perusteella |
| `classify` | Luokittele pyyntö (esim. coding, analysis, creative) |
| `balance` | Tasapainoita kustannus/latency/kyvykkyyksia |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["route", "classify", "balance"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Kysymys |
| `priority` | `str` | ❌ | `cost`, `latency`, `quality`, `balanced` |
| `budget` | `float` | ❌ | Enimmäiskustannus (USD) |
| `max_latency` | `int` | ❌ | Enimmäisviive (ms) |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `model` | `str` | Valittu malli |
| `provider` | `str` | Palveluntarjoaja |
| `score` | `float` | Valitsemismallin pisteet |
| `classification` | `str` | Luokittelu (route/classify) |
| `alternatives` | `list[dict[str, Any]]` | Muut mahdolliset mallit |
| `cost_estimate` | `float` | Arvioitu kustannus (USD) |

---

## ROUTING_CRITERIA

| Kriteeri | Kuvaus |
|---|---|
| `cost` | Edullin valinnainen malli |
| `latency` | Nopein mahdollinen malli |
| `quality` | Paras laatu (usein halvempi kuin halkeava) |
| `balanced` | Tasapaino kaikista kolmesta |

---

## Esimerikkoodi

```python
from agents import LLMRouterAgent

router = LLMRouterAgent()

# Reititä optimoituun malliin
result = router.run(
    action="route",
    query="Kirjoita Python-funktio joka laskee fibon accin",
    priority="balanced",
    budget=0.05
)

print(f"Malli: {result.model}")
# Output: Malli: claude-3-7-sonnet
print(f"Kustannus: ${result.cost_estimate}")
# Output: Kustannus: $0.008

print("Vaihtoehdot:")
for alt in result.alternatives:
    print(f"  {alt['model']}: {alt['score']} (USD ${alt['cost']})")

# Luokittele pyyntö
result = router.run(
    action="classify",
    query="Selitä maskeerausfunktioita Pythonissa"
)
print(f"Luokittelu: {result.classification}")
# Output: Luokittelu: coding
```

---

## Testikattavuus

M17-testit (58) sisältävät:
- `test_route_balances_cost_and_quality`
- `test_classify_identifies_query_type`
- `test_budget_constraint_applied`
- `test_alternatives_returned`
- `test_max_latency_enforced`
