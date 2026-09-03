# DockerAgent (M10 DevOps)

**Tiedosto:** `agents/devops_agent.py`  
**Moduuli:** M10 — DevOps  
**Status:** ✅ Valmiina  
**Testit:** 63 (yhteinen M10) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Konttien ja docker-compose.yaml:n luominen projektin tyypin mukaan. Analysoi projektin teknologian ja suosii oikeat kääntäjät ja turvallisuustoimenpiteet.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"docker_agent"` |

---

## Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["generate", "build", "push"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Projektin polku or kuvaus |
| `project_type` | `str` | ❌ | Tyyppi: `python-api`, `web-app`, `cli`, `default` (oletus: `auto`) |
| `dockerfile_name` | `str` | ❌ | Generoitava tiedostonimi |

---

## Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `dockerfile` | `str` | Generoitu Dockerfile-koodi |
| `docker_compose` | `str` | docker-compose.yaml-sisältö |
| `files_created` | `list[str]` | Luodut tiedostopolut |
| `project_type` | `str` | Tunnistettu projektin tyyppi |
| `security_recommendations` | `list[str]` | Turvallisuussuositukset |

---

## Esimerkkikoodi

```python
from agents import DockerAgent

docker = DockerAgent()
result = docker.run(
    action="generate",
    query="./src",
    project_type="python-api"
)

print(result.project_type)
# Output: python-api

print(result.dockerfile)
# Output:
# FROM python:3.11-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# ...
```

Tuki projektit: `python-api`, `web-app`, `cli`, `default`. Turvallisuus suositukset sisältävät `--no-install-recommends`, `HEALTHCHECK` ja eksplisiittisen käyttäjän.

---

## Testikattavuus

Kaikki M10-testit (63) sisältävät DockerAgent-testit:
- `test_generate_dockerfile`
- `test_detect_project_type`
- `test_security_recommendations_present`
- `test_compose_has_correct_ports`
