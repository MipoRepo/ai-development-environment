# ReleaseManagerAgent (M15 Release & Governance)

**Tiedosto:** `agents/release_agent.py`  
**Moduuli:** M15 — Release & Governance  
**Status:** ✅ Valmiina  
**Testit:** 60 | **Kattavuus:** 88 %

---

## Tarkoitus

Versionhallinta ja julkaisun suunnittelu. Tukee semanttista versionhallintaa (major/minor/patch) ja neljää julkaisuvaihetta (`RELEASE_PHASES`). Valitsee deploy-strategian (`DEPLOYMENT_STRATEGIES`).

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"release_manager"` |

---

## Syöte (ReleaseManagerInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["plan", "execute", "validate", "bump_version"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Julkaisun kuvaus tai polku |
| `version_type` | `str` | ❌ | `major`, `minor`, `patch` (oletus: `auto`) |
| `strategy` | `str` | ❌ | `DEPLOYMENT_STRATEGIES` |
| `phases` | `list[str]` | ❌ | `RELEASE_PHASES` (rajoitus) |

---

## Tuloste (ReleaseManagerOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `version` | `str` | Uusi versio (semanttinen) |
| `phases` | `list[dict[str, Any]]` | Suunnitellut vaiheet |
| `deployment_strategy` | `str` | Valittu deploy-strategia |
| `commands` | `list[str]` | Suoritettavat komennot |
| `validation_checks` | `list[str]` | Vahvistuskohdat |
| `error` | `str \| None` | Virhe |

---

## RELEASE_PHASES

| Vaihe | Kuvaus |
|---|---|
| `prepare` | Valmistelut (dependency freeze, changelog) |
| `build` | Käännös ja paketointi |
| `test` | QA ja integraatiotestaus |
| `stage` | Vaiheenvaihto (staging-ympäristö) |
| `release` | Tuotantoon vieminen |
| `rollback` | automaattinen poistautuminen (onnistuneessa virheessä) |

---

## DEPLOYMENT_STRATEGIES

| Strategia | Kuvaus |
|---|---|
| `blue_green` | Vaihtaminen kahdesta ympäristöstä |
| `canary` | Vaiheittainen siirtäminen prosentteina |
| `rolling` | Astiomaisten päivitysten asettelu |
| `recreate` | Vanpon poisto ja uuden luonti |

---

## Esimerkkikoodi

```python
from agents import ReleaseManagerAgent

rm = ReleaseManagerAgent()

# Suunnittele julkaisu
plan = rm.run(
    action="plan",
    query="Julkaise versio 1.5 kaikki ominaisuudet mukaanlukien API gatewayt",
    version_type="minor",
    strategy="blue_green"
)

print(f"Versio: {plan.version}")
# Output: Versio: 2.5.0

print(f"Strategia: {plan.deployment_strategy}")
# Output: Strategia: blue_green

for phase in plan.phases:
    print(f"  {phase['name']}: {phase['status']}")

# Bumpaa versio
bumper = rm.run(
    action="bump_version",
    query="1.4.3",
    version_type="minor"
)
print(bumper.version)  # Output: 1.5.0
```

---

## Testikattavuus

M15-testit (60) sisältävät:
- `test_plan_creates_phases`
- `test_bump_version_major_minor_patch`
- `test_validate_checks_prerequisites`
- `test_strategy_selection_correct`
