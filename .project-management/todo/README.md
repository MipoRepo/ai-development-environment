# Projektin TODO-hallinta

Tämä on AIDE:n projektiin liittyvä TODO-hallinta. Tässä on kaikki, mitä tarvitset projektin seuraamiseen, suunnitteluun ja dokumentointiin.

---

## Versioned TODO -rakenne

Projektin edistymisen seuraamiseen käytetään **versionoitua TODO-listaa**. Jokainen versio on erillinen tiedosto, joka kuvaa **yhden vaiheen** (Alpha, Beta, Release Ready, Release).

| Versio | Vaihe | Moduulit | Kuvaus |
| --- | --- | --- | --- |
| `alpha1.0` | Alpha | M1 | Core & Director perustoiminnot. |
| `alpha1.1` | Alpha | M2–M9 | Käytössä-vaihe (Project Management → Orchestration). |
| `alpha2.0` | Alpha | M10 | DevOps. |
| `alpha2.1` | Alpha | M11 | Pedagogy. |
| `alpha2.2` | Alpha | M12 | Learning & Assessment. |
| `alpha2.3` | Alpha | M13 | Knowledge & Memory. |
| `alpha2.4` | Alpha | M14 | Maintenance. |
| `alpha2.5` | Alpha | M15 | Release & Governance. |
| `alpha2.6` | Alpha | M16 | Agent Engineering. |
| `alpha2.7` | Alpha | M17 | AI Gateway. |
| `alpha2.8` | Alpha | M18 | Local LLM. |
| `alpha2.9` | Alpha | M19 | MCP & Integrations. |
| `alpha2.10` | Alpha | M20 | GUI / Control Center. |
| `beta1.0` | Beta | — | Kaikki M1–M20 valmiit, integroitu versio. |
| `beta1.1` | Beta (päivitys) | — | M1–M20 -lisäykset. |
| `release-ready1.0` | Julkaisukunto | — | MVP valmiina. |
| `release1.0` | Julkaisu | — | Tuotantokäyttöinen versio. |

> **Versioneerullinen kasvatus:** AINA `major` pysyy samanaan, kunnes vaihetaan seuraavaan vaiheeseen. `minor` kasvaa `+0.1` jokaisella "korjausversiolla".
> **Sääntö:** Kun olet valmis siirtymään seuraavaan vaiheeseen, kysy ensin, mihin versioon siirrytään (alpha → beta → release-ready → release). Tämän jälkeen tallenna uusi versio tähän kansioon.

---

## Miten käytän tämtä?

- **`alpha2.1`** on tämä hetkinen aktiivinen tehtävälista (M11 Pedagogy).
- **`old_todo/`** sisältää arkistoituja versioita (alpha1.0, alpha1.1, alpha2.0).
- **`beta1.0`** tulee vasta kun kaikki M1–M20 ovat valmiita.

---

## Muistutus: Claude Code -muistit

Varmista AINA että `.claude/memories/project-rules.md` on ajantasala. Lisää sinne jokainen suuri päätös:
```markdown
- Versiokasvatus: Alpha 1.0 → Alpha 1.1 → Alpha 2.0 → Alpha 2.1 (jokainen moduuli +0.1).
- Seuraava versio on `beta1.0` kun kaikki M1–M20 valmistuvat.
```

---

Kun olet valmis siirtymään seuraavaan moduuliin, kirjoita: **"Siirry Alpha X.Y"** (esim. "Siirry Alpha 2.1").
