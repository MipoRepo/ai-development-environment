# Projektin TODO-hallinta

Tämä on AIDE:n projektiin liittyvä TODO-hallinta. Tässä on kaikki, mitä tarvitset projektin seuraamiseen, suunnitteluun ja dokumentointiin.

---

## Versioned TODO -rakenne

Projektin edistymisen seuraamiseen käytetään **versionoitua TODO-listaa**. Jokainen versio on erillinen tiedosto, joka kuvaa **yhden vaiheen** (Alpha, Beta, Release Ready, Release).

| Versio | Vaihe | Kuvaus |
| --- | --- | --- |
| `alpha1.0` | Alpha | M1 Core & Director perustoiminnot. |
| `alpha1.1` | Alpha (päivitys) | Tarvittaessa lisäkorjaukset M1:ään. |
| `beta1.0` | Beta | M2–M7 -moduulit (Käytössä). |
| `beta1.1` | Beta (päivitys) | M2–M7 -lisäykset. |
| `release-ready1.0` | Julkaisukunto | MVP valmiina. |
| `release-ready1.1` | Julkaisukunto (päivitys) | Viimeistelyt. |
| `release1.0` | Julkaisu | Tuotantokäyttöinen versio. |

> **Versioneerullinen kasvatus:** AINA `major` pysyy samanaan, kunnes vaihetaan seuraavaan vaiheeseen. `minor` kasvaa `+0.1` jokaisella "korjausversiolla".
> **Sääntö:** Kun olet valmis siirtymään seuraavaan vaiheeseen, kysy ensin, mihin versioon siirrytään (alpha → beta → release-ready → release). Tämän jälkeen tallenna uusi versio tähän kansioon.

---

## Miten käytän tämtä?

- **`alpha1.0`** on tämä hetkinen aktiivinen tehtävälista.
- **`beta1.0`** tulee vasta Kun Alpha on valmiina.
- **`old_todo/`** sisältää arkistoituja versioita.

---

## Muistutus: Claude Code -muistit

Varmista AINA että `.claude/memories/project-rules.md` on ajantasala. Lisää sinne jokainen suuri päätös:
```markdown
- Versiokasvatus: Alpha 1.0 → Alpha 1.1 (jos tarvitaan korjaus).
- Seuraava versio on `beta1.0` kun M1 valmistuu.
```

---

Kun olet valmis siirtymään seuraavaan versioon, kirjoita: **"Siirry beta1.0"**.
