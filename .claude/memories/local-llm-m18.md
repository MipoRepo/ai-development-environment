---
name: local-llm-m18
description: M18 Local LLM -moduulin toteutus, agentit ja päätökset
metadata:
  type: project
---

## M18 — Local LLM: Paikallisten tekoälymallien hallinta ja suoritus

### Toteutetut komponentit

**`agents/local_llm_agent.py`** — kolme uutta agenttia:

1. **LocalModelAgent** (`agent_type="local_model"`)
   - Listaa paikalliset mallit (Ollama, llama.cpp, GGUF)
   - Asentaa malleja (Ollama `pull`)
   - Poistaa malleja (Ollama `rm`)
   - Näyttää mallin tiedot ja muistitietopluvat
   - Konfiguroi malliasetukset (n_threads, n_batch, n_ctx)

2. **ModelRunnerAgent** (`agent_type="model_runner"`)
   - Suorittaa päätettä paikallisessa mallissa
   - Tukee Ollamaa ja llama.cpp:ää GGUF-mallien kanssa
   - Benchmark-toiminto simuloiduilla tuloksilla
   - Vertailu-toiminto jenmien eri mallejen suorituskyvystä

3. **QuantizationAgent** (`agent_type="quantization"`)
   - Analysoi GGUF-tiedostoja (koko, muistitietopluvat)
   - Kvantisoi malleja eri muodoissa (F32, F16, Q2_K–Q8_0)
   - Suosii sopivat kvantisointimuodot saatavilla olevan VRAM-in perusteella

### Vakiot

- `LOCAL_MODEL_ACTIONS` — toiminnot (list, install, remove, info, config)
- `MODEL_RUNNER_ACTIONS` — toiminnot (run, benchmark, compare)
- `QUANTIZATION_ACTIONS` — toiminnot (quantize, analyze, recommend)
- `KNOWN_LOCAL_MODELS` — 17 tunnetun mallin lista (llama3.1, mistral, gemma, phi3, qwen2, codellama, deepseek-r1)
- `QUANTIZATION_FORMATS` — 8 GGUF-muotoa (F32, F16, Q2_K, Q3_K, Q4_K, Q5_K, Q6_K, Q8_0)
- `MEMORY_ESTIMATES` — VRAM/RAM-tietopluvat 7 mallille
- `OLLAMA_COMMANDS` — Ollama CLI-komennot

### Testit

- `tests/test_local_llm_agent.py` — 54 testiä
- Kattavuus: 89 %
- Kaikki testit läpäisti

### Päätökset

- **Simuloitu suoritus**: ModelRunnerAgent simuloi vastaukset paikallisissa malleissa, koska oikea malli ei ole käytettävissä testiympäristössä. Tämä tekee testeistä itsenäisiä paikallisista riippuvuuksista.
- **Lazy import `MODEL_REGISTRY`**: `ModelRunnerAgent.get_model_info()` tekee importin `ai_gateway_agent`-moduulista vain kutsuttaessa, välppaaten import-kierteeltä.
- **Q4_K oletusmuoto**: Kvantisointi olettaa Q4_K-muodon tuntemattomille muodoille, koska se on paras tasapaino laadun ja koon välillä.
- **Oletusmuistitietopluvut**: Tuntemillelle muodoille annetut muistitietopluvut perustuvat yhteisesti hyväksyttyihin arvoihin. Tuntemille mallille annetut oletusarvot ovat 16 GB VRAM/RAM (F32) ja 4 GB (Q4_K).

**Why:** Paikalliset mallit vaativat erillisen agentin Ollaman, llama.cpp:n ja GGUF-tiedostojen käsittelyyn, jotka erosivat pilvimallien hallinnasta.

**How to apply:** Käytä `LocalModelAgent` mallien listauksen, `ModelRunnerAgent` tekstin generointiin ja `QuantizationAgent` mallin optimointiin ennen paikallista käyttöä.
