# InfrastructureAgent (M10 DevOps)

**Tiedosto:** `agents/devops_agent.py`  
**Moduuli:** M10 — DevOps  
**Status:** ✅ Valmiina  
**Testit:** osuus M10 (63 yhteensä) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Infra-tiedostojen analyysi, riippuvuuksien analyysi ja parannussuoritusten laskeminen.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"infrastructure"` |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["scan", "analyze", "recommend"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Projektin polku |
| `include_dependencies` | `bool` | ❌ | Analysoidaanko riippuvuudet |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `infrastructure_files` | `list[dict[str, Any]]` | Löydetyt tiedostot (Dockerfile, docker-compose, kubernetes, ...) |
| `dependencies` | `dict[str, Any]` | Riippuvuussolmut |
| `recommendations` | `list[str]` | Parannusehdotuksia |
| `complexity_score` | `float` | Monimutkaiisuuspiste (0.0–10.0) |

---

## Esimerkkikoodi

```python
from agents import InfrastructureAgent

infra = InfrastructureAgent()
result = infra.run(
    action="analyze",
    query="./"
)

print(f"Monimutkaiisuus: {result.complexity_score}")
# Output: Monimutkaiisuus: 6.2

print(result.infrastructure_files)
# Output: [{"file": "Dockerfile", "type": "docker"}, {"file": "docker-compose.yml", "type": "compose"}]

print(result.dependencies)
# Output: {"flask": "2.3.3", "psycopg2": "2.9.7"}
```

---

## Testikattavuus

M10-testit (63) sisältävät:
- `test_infra_files_detected`
- `test_complexity_score_calculated`
- `test_recommendations_generated`
- `test_dependencies_parsed`
