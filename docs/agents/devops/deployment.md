# DeploymentAgent (M10 DevOps)

**Tiedosto:** `agents/devops_agent.py`  
**Moduuli:** M10 — DevOps  
**Status:** ✅ Valmiina  
**Testit:** osuus M10 (63 yhteensä) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Deployment-strategioiden ja deploy-vaiheiden ohjaus. Tukee neljää deploy-strategiaa ja antaa vaiheittaset ohjeet.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"deployment"` |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["plan", "generate", "validate"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Kuvaus tai nykyinen prosessi |
| `strategy` | `str` | ❌ | Strategia: `docker-swarm`, `kubernetes`, `aws-ecs`, `static` |
| `environment` | `str` | ❌ | Ympäristö (dev/staging/production) |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `strategy` | `str` | Valittu deploy-strategia |
| `steps` | `list[dict[str, Any]]` | Deploya-vaiheet |
| `commands` | `list[str]` | Suoritettavat komennot |
| `validation` | `list[str]` | Vahvistusaskeleet |

---

## Tuetut strategiat

| Strategia | Kuvaus |
|---|---|
| `docker-swarm` | Paikallinen klusteri Docker-containereilla |
| `kubernetes` | Kubernetes klusterin deployaaminen |
| `aws-ecs` | Amazon ECS pilvessä |
| `static` | Staattisten tiedostojen deployaaminen (S3/CloudFront, Netlify, ...) |

---

## Esimerakkikoodi

```python
from agents import DeploymentAgent

deploy = DeploymentAgent()
result = deploy.run(
    action="plan",
    query="Python FastAPI backend, tarvitsi 3 instanssia, high availability",
    strategy="docker-swarm"
)

print(result.strategy)
# Output: docker-swarm

print(f"Vaiheita: {len(result.steps)}")
# Output: Vaiheita: 4

for step in result.steps:
    print(f"  {step['name']}: {step['description']}")
# Output:
#   1. Initialize Swarm: docker swarm init
#   2. Create Secrets: docker secret create ...
#   3. Deploy Stack: docker stack deploy ...
#   4. Verify: docker service ls
```

---

## Testikattavuus

M10-testit (63) sisältävät:
- `test_plan_returns_correct_strategy`
- `test_generate_creates_deploy_commands`
- `test_validate_checks_prerequisites`
- `test_all_strategies_supported`
