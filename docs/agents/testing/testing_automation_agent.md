# TestRunnerAgent, PerformanceTestAgent & IntegrationTestAgent (M8 Testing Automation)

**Tiedosto:** `agents/testing_automation_agent.py`  
**Moduuli:** M8 — Testing Automation  
**Status:** ✅ Valmiina  
**Testit:** 37 | **Kattavuus:** 91 %

---

## Tarkoitus

Testiautomaation edistynyt versio. **TestRunnerAgent** suorittaa pytest-subprosessin ja analysoi tulokset; **PerformanceTestAgent** tekee suorituskykytestit benchmark- ja p95-laskelmin; **IntegrationTestAgent** tarkistaa moduulien väliset riippuvuudet.

## Agentit

| Agentti | `agent_type` | Tiedosto |
|---|---|---|
| **TestRunnerAgent** | `"test_runner"` | `agents/testing_automation_agent.py` |
| **PerformanceTestAgent** | `"performance_test"` | `agents/testing_automation_agent.py` |
| **IntegrationTestAgent** | `"integration_test"` | `agents/testing_automation_agent.py` |

---

## TestRunnerAgent

### Syöte (TestRunnerInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["run", "report"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Testikansio tai -tiedosto |
| `verbose` | `bool` | ❌ | Yksityiskohtainen tuloste |
| `fail_fast` | `bool` | ❌ | Pysäytetäänkö virheen sattuessa |
| `coverage` | `bool` | ❌ | Laskeaanko kattavuus |

### Tuloste (TestRunnerOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Kaikki testit läpäisty |
| `total_tests` | `int` | Kokonaismäärä |
| `passed` | `int` | Läpäistyt |
| `failed` | `int` | Epäonnistuneet |
| `errors` | `int` | Virheet |
| `skipped` | `int` | Ohitatut |
| `coverage_percent` | `float` | Kattavuusprosentti |
| `failures` | `list[dict]` | Virheelliset testit |
| `duration` | `float` | Suorituksen kesto (s) |

---

## PerformanceTestAgent

### Syöte (PerformanceTestInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["benchmark", "compare"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Testikomento tai benchmark-funktio |
| `iterations` | `int` | ❌ | Toistojen määrä (oletus: 5) |
| `warmup` | `bool` | ❌ | Suoritetaanko kuumennusaihe |

### Tuloste (PerformanceTestResult)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `avg_latency` | `float` | Keskesviiva (ms) |
| `p95_latency` | `float` | 95. persenttiilu (ms) |
| `p99_latency` | `float` | 99. persenttiilu (ms) |
| `throughput` | `float` | Pyyntöjä/sekunti |
| `min_latency` | `float` | Minimi (ms) |
| `max_latency` | `float` | Maksimi (ms) |
| `iterations` | `int` | Toistojen määrä |

---

## IntegrationTestAgent

### Syöte (IntegrationTestInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["run", "analyze"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Projekti- tai modulikansio |
| `modules` | `list[str]` | ❌ | Testattavat moduulit |
| `dependencies` | `dict[str, list[str]]` | ❌ | Riippuvuussolmub

### Tuloste (IntegrationTestOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Kaikki integraatiot läpäisti |
| `total_tests` | `int` | Kokonaismäärä |
| `passed` | `int` | Läpäistyt |
| `failed` | `int` | Epäonnistuneet |
| `dependency_matrix` | `dict[str, list[str]]` | Moduulien väliset riippuvuudet |
| `coverage_score` | `float` | Riippuvuuskatetelma (0.0–1.0) |
| `issues` | `list[str]` | Integraatio-ongelmat |

---

## Esimerkkikoodi

### Testien automatisaatio

```python
from agents import TestRunnerAgent

runner = TestRunnerAgent()
result = runner.run(
    action="run",
    query="./tests",
    coverage=True,
    fail_fast=False
)

print(f"Läpäisty: {result.passed}/{result.total_tests}")
print(f"Kattavuus: {result.coverage_percent}%")
# Output: Läpäisty: 45/46
# Output: Kattavuus: 90%
```

### Suorituskyvytestaus

```python
from agents import PerformanceTestAgent

perf = PerformanceTestAgent()
result = perf.run(
    action="benchmark",
    query="api_call_with_payload",
    iterations=10,
    warmup=True
)

print(f"Keskipituus: {result.avg_latency}ms")
print(f"P95: {result.p95_latency}ms")
# Output: Keskipituus: 42.3ms
# Output: P95: 68.7ms
```

### Integraatiotestaus

```python
from agents import IntegrationTestAgent

integration = IntegrationTestAgent()
result = integration.run(
    action="analyze",
    query="./src"
)

print(f"Riippuvuuskatetelma: {result.coverage_score}")
print(f"Ongelmat: {result.issues}")
# Output: Riippuvuuskatetelma: 0.89
# Output: Ongelmat: ['Moduuli A importtaa B muttei testaa sitä']
```

---

## Testikattavuus

```
tests/test_testing_automation_agent.py — 37 testiä
Kattavuus: 91 %
```

Tärkeimmät testit:
- `test_run_executes_pytest_subprocess`
- `test_calculate_percentiles`
- `test_benchmark_iterations`
- `test_dependency_matrix_generated`
- `test_coverage_report_parsed`

## Liittyvät moduulit

- **Riippuu:** TesterAgent (M5) — perustoiminnot
- **Seuraaja:** QAGent (M5) laadun tarkistukseen
- **Integroi:** MultiAgentCoordinator (M9) CI/CD-workflowissa

## CLI-käyttö

```bash
aide run "Aja testit"                           # → TestRunnerAgent.run
aide run "Tee benchmark"                       # → PerformanceTestAgent.benchmark
aide orchestrate --workflow ci-cd.yaml         # → sisältää testausvaiheen
```

## Katso myös

- [`testing_agent.md`](testing_agent.md) — M5 perustoiminnot
- [`modules.md`](../../architecture/modules.md) — kaikki moduulit
- [`agent-lifecycle.md`](../../architecture/agent-lifecycle.md) — agentin elinkaari
