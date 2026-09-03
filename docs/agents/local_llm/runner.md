# ModelRunnerAgent (M18 Local LLM)

**Tiedosto:** `agents/local_llm_agent.py`  
**Moduuli:** M18 — Local LLM  
**Status:** ✅ Valmiina  
**Testit:** 54 | **Kattavuus:** 89 %

---

## Tarkoitus

Suorittaa päätettä paikallisissa malleissa. Tukee `run`, `benchmark`, `compare`-toimintoja.

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"model_runner"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `run` | Suorita malli kyselyn avulla |
| `benchmark` | Benchmarki suorituskyvystä |
| `compare` | Vertaa kahta mallia samalla kyselyllä |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["run", "benchmark", "compare"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Kysymys tai prompti |
| `model` | `str` | ✅ | Mallin nimi (esim. `llama3:8b-instruct-q4_K_M`) |
| `iterations` | `int` | ❌ | Toistot (benchmark) |
| `compare_with` | `str` | ❌ | Vertailu-malli (compare) |
| `temperature` | `float` | ❌ | 0.0–1.0 (oletus: 0.7) |
| `max_tokens` | `int` | ❌ | Enimmäistokenit |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `response` | `str` | Mallin vastaus |
| `model` | `str` | Käytetty malli |
| `latency` | `float` | Viive (ms) |
| `tokens_per_second` | `float` | Tokenit/sekunti |
| `comparison` | `dict[str, Any]` | Vertailutulokset (compare) |
| `benchmark_results` | `dict[str, Any]` | Benchmark-tulokset (benchmark) |

---

## Esimerkkikoodi

```python
from agents import ModelRunnerAgent

runner = ModelRunnerAgent()

# Simpiilyssuoritus
result = runner.run(
    action="run",
    query="Kuvaa Docker-turvallisuus 3 kohdalla",
    model="llama3:8b-instruct-q4_K_M",
    temperature=0.3
)

print(result.response)
print(f"Generoitu: {result.tokens_per_second} tokenia/s")

# Benchmarki
result = runner.run(
    action="benchmark",
    query="Selittäminen Pythonista",
    model="llama3:8b-instruct-q4_K_M",
    iterations=10
)

print(f"Keskipituus: {result.latency}ms")
print(f"Lukitus: {result.tokens_per_second} t/s")

# Vertailu
result = runner.run(
    action="compare",
    query="Kirjoita tiivis API-ohje",
    model="llama3:8b-instruct-q4_K_M",
    compare_with="phi3:3.8b-mini-4k-instruct-q4_K_M"
)

print("Vertailu:")
for model, res in result.comparison.items():
    print(f"  {model}: {res['tokens_per_second']} t/s")
```

---

## MODEL_RUNNER_ACTIONS

| Toiminto | Selitys |
|---|---|
| `run` | Yksinkertainen generointi |
| `benchmark` | Toistettu ajoitus |
| `compare` | Kaksi mallia yhdellä kyselyllä |

---

## Testikattavuus

M18-testit (54) sisältävät:
- `test_run_returns_model_response`
- `test_benchmark_measures_latency`
- `test_compare_returns_both_outputs`
- `test_iterations_respected`
