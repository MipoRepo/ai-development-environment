# Turvallisuusagentit (M7 Security)

**Tiedosto:** `agents/security_agent.py`  
**Moduuli:** M7 — Security  
**Status:** ✅ Valmiina  
**Testit:** 40 | **Kattavuus:** 94 %

---

## Tarkoitus

Projektin kokonaisturvallisuustarkastus koodista, riippuvuuksista, salaisuuksista ja konttioista. Vaihtaaanalaisuudet:

1. **SecurityReviewAgent** — regex-pohjainen skannaus
2. **SASTAgent** — AST-pohjainen statinen analyysi
3. **DependencySecurityAgent** — haavoittuvien pakettien tarkistus
4. **SecretsAgent** — salaisuuksien ja API-avien skannaus
5. **ContainerSecurityAgent** — Dockerfile-turvallisuus

## Agentit

| Agentti | `agent_type` | Selitys |
|---|---|---|
| **SecurityReviewAgent** | `"security_review"` | Säännölliset lausekkeet (regex) turvallisuusongelmien havaitseminen |
| **SASTAgent** | `"sast"` | AST-puun läpikäynti Python-koodin turvallisuustarkastukseen |
| **DependencySecurityAgent** | `"dependency_security"` | `pip-audit` ja haavoittuvuuksien tarkistus requirements.txt:stä |
| **SecretsAgent** | `"secrets"` | AWS-keyt, API-avaimet, GitHub-tokenit, salasanat |
| **ContainerSecurityAgent** | `"container_security"` | Dockerfile-turvallisuus (root, ADD, chmod 777, EXPOSE 22) |

---

## SecurityReviewAgent — Regex-pohjainen skannaus

### Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["scan", "suggest"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Tiedoston polku tai koodi |
| `file_types` | `list[str]` | ❌ | Tiedostojen suodatus (oletus: kaikki) |

### Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `findings` | `list[dict[str, Any]]` | Löydetyt ongelmat `[{"type", "file", "line", "severity", "description"}]` |
| `total_findings` | `int` | Ongelmien yhteismäärä |
| `risk_score` | `float` | Riskipiste (0.0–10.0) |

### Esimerkkikoodi

```python
from agents import SecurityReviewAgent

scanner = SecurityReviewAgent()
result = scanner.run(
    action="scan",
    query="src/api.py"
)

for finding in result.findings:
    print(f"  [{finding['severity']}] {finding['file']}:{finding['line']} — {finding['description']}")
# Output:
#   [high] src/api.py:45 — Käytetty eval()
#   [medium] src/api.py:102 — Kiinteä salasana

print(f"Riskipisteet: {result.risk_score}")
# Output: Riskipisteet: 7.5
```

---

## SASTAgent — AST-pohjainen analyysi

### Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["analyze", "report"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Tiedoston polku |
| `depth` | `str` | ❌ | Analyysin syvyys (shallow/deep) |

### Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `issues` | `list[dict[str, Any]]` | Koodiongelmia AST-puun perusteella |
| `function_count` | `int` | Funktioiden määrä |
| `import_count` | `int` | Importtien määrä |
| `risk_score` | `float` | Riskipiste |

### Esimerkkikoodi

```python
from agents import SASTAgent

sast = SASTAgent()
result = sast.run(
    action="analyze",
    query="src/app.py",
    depth="deep"
)

print(f"Funktioita: {result.function_count}")
print(f"Importteja: {result.import_count}")
# Output: Funktioita: 23
# Output: Importteja: 12
```

---

## DependencySecurityAgent — Riippuvuustarkastus

### Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["check", "update"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | requirements.txt/polkua |
| `auto_fix` | `bool` | ❌ | Korjataanko automaattisesti |

### Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `vulnerable_packages` | `list[dict[str, Any]]` | Haavoittuvat paketit |
| `total_vulnerabilities` | `int` | Haavoittuvuuksien määrä |
| `security_score` | `float` | Turvallisuuspiste (0.0–10.0) |
| `upgrade_suggestions` | `list[str]` | Päivitysehdotuksia |

### Esimerkkikoodi

```python
from agents import DependencySecurityAgent

dep = DependencySecurityAgent()
result = dep.run(
    action="check",
    query="requirements.txt"
)

print(f"Haavoittuvuudet: {result.total_vulnerabilities}")
# Output: Haavoittuvuudet: 3

for pkg in result.vulnerable_packages:
    print(f"  {pkg['name']} {pkg['version']} — {pkg['severity']}")
# Output:
#   flask 1.0.2 — critical
#   requests 2.18.0 — high
```

---

## SecretsAgent — Salaisuuksien skannaus

### Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["scan", "validate"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Tiedosto tai kansio |
| `patterns` | `list[str]` | ❌ | Etsittävät kuviot |

### Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `found_secrets` | `list[dict[str, Any]]` | Löydetyt salaisuudet |
| `total_secrets` | `int` | Salaisuuksien määrä |
| `scan_paths` | `list[str]` | Skannatut polput |

### Esimerkkikoodi

```python
from agents import SecretsAgent

secrets = SecretsAgent()
result = secrets.run(
    action="scan",
    query="./"
)

print(f"Salaisuuksia löydetty: {result.total_secrets}")
# Output: Salaisuuksia löydetty: 2

for secret in result.found_secrets:
    print(f"  {secret['type']} — {secret['file']}:{secret['line']}")
# Output:
#   AWS_ACCESS_KEY_ID — .env:5
#   GITHUB_TOKEN — config.py:22
```

### Tunnistettavat kuviot

| Tyyppi | Esimerkkikuvio |
|---|---|
| AWS Access Key | `AKIA[0-9A-Z]{16}` |
| AWS Secret Key | `aws_secret_access_key = "..."` |
| GitHub Token | `gh[pous]_[A-Za-z0-9]+` |
| API Key | `api_key = "..." / Authorization: Bearer ...` |
| Generic Secret | `secret = "..." / password = "..."` |

---

## ContainerSecurityAgent — Docker-turvallisuus

### Syöte

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["scan", "harden"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Dockerfile-polku |
| `policy` | `str` | ❌ | Turvallisuuspolitiikka (strict/standard) |

### Tuloste

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `findings` | `list[dict[str, Any]]` | Löydetyt ongelmat |
| `hardening_score` | `float` | Kovitus pisteet (0.0–10.0) |
| `recommendations` | `list[str]` | Parannusehdotuksia |

### Esimerkkikoodi

```python
from agents import ContainerSecurityAgent

container = ContainerSecurityAgent()
result = container.run(
    action="scan",
    query="Dockerfile"
)

print(f"Kovitus pisteet: {result.hardening_score}")
# Output: Kovitus pisteet: 6.5

for finding in result.findings:
    print(f"  [{finding['severity']}] {finding['issue']}")
# Output:
#   [high] Käytetään root-käyttäjää
#   [medium] Pakettien asennus ilman --no-install-recommends
```

### Tunnistettavat ongelmat

| Tarkistus | Kuvaus |
|---|---|
| `USER root` | Root-käyttäjä kontissa |
| `ADD` | ADD-käsky (suosittelee COPY):ssa |
| `chmod 777` | Maalliskirjoitusoikeus |
| `EXPOSE 22` | SSH-portti containerissa |
| `curl|sh` | Epäsuora kriittisen koodin suoritus |
| Ei `--no-install-recommends` | Tarpeettomat paketit |
| Ei `HEALTHCHECK` | Terveyttä tarkastava komennus puuttuu |

---

## Testikattavuus

```
tests/test_security_agents.py — 40 testiä
Kattavuus: 94 %
```

Tärkeimmät testit:
- `test_scan_detects_eval_usage`
- `test_sast_analyzes_python_ast`
- `test_dependency_check_finds_vulnerabilities`
- `test_secrets_scan_finds_aws_keys`
- `test_container_security_detects_root_user`

---

## Liittyvät moduulit

- **Riippuu:** DeveloperAgent (M4) — tarkastuksen kohteena koodi
- **Integroi:** ReleaseManagerAgent (M15) — compliance-tarkastuksissa
- **Seuraa:** DependencyAgent (M14) — riippuvuudet päivitettäessä

## CLI-käyttö

```bash
aide run "Skannaa projektin turvallisuus"            # → SecurityReviewAgent.scan
aide run "Tarkista riippuvuudet"                    # → DependencySecurityAgent.check
aide run "Etsi salaisuudet"                         # → SecretsAgent.scan
aide run "Tarkista Dockerfile"                      # → ContainerSecurityAgent.scan
```

## Katso myös

- [`modules.md`](../../architecture/modules.md) — kaikki moduulit
- [`agent-lifecycle.md`](../../architecture/agent-lifecycle.md) — agentin elinkaari
- [`dataflow.md`](../../architecture/dataflow.md) — turvallisuus tarkistettavissa workflowssa
