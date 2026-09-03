# QuantizationAgent (M18 Local LLM)

**Tiedosto:** `agents/local_llm_agent.py`  
**Moduuli:** M18 — Local LLM  
**Status:** ✅ Valmiina  
**Testit:** 54 | **Kattavuus:** 89 %

---

## Tarkoitus

Kvantisoi ja optimoi paikalliset LLM-mallit. Tukee 8 GGUF-muotoa (F32 – Q8_0).

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"quantization"` |

---

## Toiminnot

| Toiminto | Kuvaus |
|---|---|
| `quantize` | Kvantisoi malli annettuun muotoon |
| `analyze` | Analysoi kunkin mallin muistitaaksen ja koon |
| `recommend` | Suositalistalla oikea muoto laitteiston ja tarkan tason perusteella |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["quantize", "analyze", "recommend"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Mallin polku tai nimi |
| `format` | `str` | ❌ | `QUANTIZATION_FORMATS` (F32, F16, Q4_K_M, Q4_K_S, Q5_K_M, Q5_K_S, Q8_0) |
| `target_size` | `str` | ❌ | Tavoitekokonaisuus (esim. `"4GB"`) |
| `hardware` | `str` | ❌ | Laitteisto (cpu, gpu, ram) |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `quantized_path` | `str` | Kvantoidun tiedoston polku |
| `format_used` | `str` | Käytetty muoto |
| `original_size` | `float` | Alkuperäinen koko (GB) |
| `quantized_size` | `float` | Kvantoidun tiedoston koko (GB) |
| `size_reduction` | `float` | Koon pieneneminen (%) |
| `analysis` | `dict[str, Any]` | Muiston ja tehokkuuden analyysi |
| `recommendation` | `str` | Suositeltu muoto (recommend) |
| `error` | `str \| None` | Virhe |

---

## QUANTIZATION_FORMATS

| Muoto | Kuvaus | Koko | Suosituslaitteisto |
|---|---|---|---|
| `F32` | Täydellinen tarkkuus | 100% | GPU / korkea RAM |
| `F16` | Puolipuolinen tarkkuus | 50% | GPU / 8+ GB RAM |
| `Q4_K_M` | 4-bittis kuivuminen | 25% | CPU / 4–8 GB RAM |
| `Q4_K_S` | 4-bittis pienempi | 18% | CPU / 4 GB RAM |
| `Q5_K_M` | 5-bittis kuivuminen | 30% | CPU / 6 GB RAM |
| `Q5_K_S` | 5-bittis pienempi | 22% | CPU / 4–6 GB RAM |
| `Q8_0` | 8-bittis | 50% | CPU / 8+ GB RAM |

---

## Esimerkkikoodi

```python
from agents import QuantizationAgent

quant = QuantizationAgent()

# Kvantisointi
result = quant.run(
    action="quantize",
    query="models/llama-3-8b-instruct-f32.gguf",
    format="Q4_K_M",
    target_size="3GB"
)

print(f"Muoto: {result.format_used}")
print(f"Koko: {result.original_size}GB → {result.quantized_size}GB")

# Suositus laitteistolta
result = quant.run(
    action="recommend",
    query="llama-3-8b",
    hardware="cpu",
    target_size="4GB"
)

print(f"Suositus: {result.recommendation}")
# Output: Suositus: Q4_K_M (2.3GB) — tarkka ja pienen koko

# Analyysi
result = quant.run(
    action="analyze",
    query="models/"
)

for model, analysis in result.analysis.items():
    print(f"  {model}: {analysis['size_gb']}GB — {analysis['ram_needed']}")
```

---

## MEMORY_ESTIMATES

| Muoto | RAM (pienin) | Soveltui |
|---|---|---|
| `F32 / F16` | 16 GB | Koulutus / tarkkuus |
| `Q8_0` | 10 GB | Laadukas vastaus |
| `Q5_K_M / Q5_K_S` | 7 GB | Tasapaino |
| `Q4_K_M / Q4_K_S` | 5 GB | Suositeltu CPU |

---

## Testikattavuus

M18-testit (54) sisältävät:
- `test_quantize_creates_file`
- `test_analyze_returns_memory_stats`
- `test_recommend_selects_appropriate_format`
- `test_size_reduction_calculated`
- `test_all_formats_supported`
