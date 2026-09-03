# ComplianceAgent (M15 Release & Governance)

**Tiedosto:** `agents/release_agent.py`  
**Moduuli:** M15 — Release & Governance  
**Status:** ✅ Valmiina  
**Testit:** 60 | **Kattavuus:** 88 %

---

## Tarkoitus

Lisenssi- ja sääntelystandardintutkimus. Tukee useita lisenssi- ja määräystyksen ja standardit. Laskee `compliance_score` (0–100) ja antaa suosituksia.

## Agentti

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"compliance"` |

---

## Syöte (ComplianceInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["check", "audit", "report"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Projektin polku tai paketti |
| `license_types` | `list[str]` | ❌ | Tarkistettavat lisenssit |
| `standards` | `list[str]` | ❌ | Tarkistettavat standardiot |

---

## Tuloste (ComplianceOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `compliance_score` | `float` | Yhteensopivuuspiste (0–100) |
| `licenses` | `dict[str, str]` | Paketti → lisenssi |
| `violations` | `list[dict[str, Any]]` | Löydetyt rikkomukset |
| `recommendations` | `list[str]` | Parannusehdotuksia |
| `standards_met` | `dict[str, bool]` | Käsitellyt standardit |

---

## Tuetut lisenssit (LICENSE_TYPES)

| Liites | Kuvaus |
|---|---|
| `MIT` | Massachusetts Institute of Technology |
| `Apache-2.0` | Apache License 2.0 |
| `GPL-3.0` | GNU General Public License 3.0 |
| `BSD-3-Clause` | Berkeley Software Distribution |
| `Proprietary` | Omia oikeuksia |

---

## Tuetut standardit (REGULATORY_STANDARDS)

| Standardi | Kuvaus |
|---|---|
| `GDPR` | Euroopan tietosuoja-asetus |
| `PCI-DSS` | Korttimaksutietojen suoja |
| `SOC2` | Palvelun laatu ja turvallisuus |
| `ISO 27001` | Tiedoturvaohjelma |
| `HIPAA` | terveydenhuollon tietosuoja (Yhdysvallat) |

---

## Esimerikkoodi

```python
from agents import ComplianceAgent

compliance = ComplianceAgent()
result = compliance.run(
    action="check",
    query="./"
)

print(f"Yhteensopivuuspiste: {result.compliance_score}")
# Output: Yhteensopivuuspiste: 85.5

print("Lisenssit:")
for pkg, license in result.licenses.items():
    print(f"  {pkg}: {license}")

print("Violations:")
for v in result.violations:
    print(f"  {v['package']}: {v['violation']}")

print("Suositukset:")
for rec in result.recommendations:
    print(f"  → {rec}")
```

---

## Testikattavuus

M15-testit (60) sisältävät:
- `test_check_returns_compliance_score`
- `test_gpl_conflict_detected`
- `test_gdpr_recommendations_generated`
- `test_standards_met_populated`
