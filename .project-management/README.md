# Projektinhallinta

Tämä on **AI Development Environmentin (AIDE) projektinhallintaa**. Tässä on kaikki, mitä tarvitset projektin seuraamiseen, suunnitteluun ja dokumentointiin.

---

## Rakenne

```
.project-management/
├── PROJECT.md                        ← Tämä projekti-ohje (tarkoitus, vaiheet, käyttö)
├── plans/                            ← Kaikki suunnitelman dokumentit
│   ├── PROJECT_MAIN-PLAN.md          ← Pääsuunnitelma (visio, laajuus, vaiheet)
│   ├── requirements.md               ← Vaatimussuunnitelma
│   ├── architecture.md               ← Arkkitehtuuri
│   ├── suunnitelmat/                 ← Moduulikohtaiset suunnitelmat (M1–M20)
│   │   ├── 1-startup/
│   │   ├── 2-runtime/
│   │   ├── 3-extension/
│   │   ├── 4-self-improvement/
│   │   └── 5-integration-gui/
│   └── TODO-alpha1.0.md              ← Aikaisempi suunnitelma (arkisto)
└── todo/                             ← Tehtävien seuranta
    ├── TODO-alpha1.0.md              ← Nykyinen aktiivinen TODO (M1 Core & Director)
    └── old_todo/                     ← Arkistoitujen versioiden kansio
        └── TODO-alpha1.1.md          ← Seuraava versio (M2–M7)
```

---

## Versioned TODO-rakenne

Projektin edistymisen seuraamiseen käytetään **versionoitua TODO-listaa**. Jokainen versio on erillinen tiedosto, joka kuvaa tietyn vaiheen tehtävät.

| Versio | Vaihe | Kuvaus |
| --- | --- | --- |
| `TODO-alpha1.0.md` | Alpha | M1 Core & Director -moduulin perustoiminnot. |
| `TODO-beta1.0.md` | Beta | Tulevat moduulit (M2–M7). |
| `TODO-release-ready1.0.md` | Release Ready | Julkaisukuntoinen versio. |
| `TODO-release1.0.md` | Release | Tuotantokäyttöinen versio. |

> **Sääntö:** Joka kerta, kun Claude Code -pyyntö edistyy seuraavaan vaiheeseen, se kysyy käyttäjän valitsemaa seuraavaa versiota (alpha → beta → release-ready → release). Tämän jälkeen se tallentaa uuden TODO-version tähän kansioon.

---

## Miten käytän tätä?

- **`PROJECT.md`** on ensimmäinen lähde, jonka Claude Code lukee aloittaessaan projektin.
- **`plans/PROJECT_MAIN-PLAN.md`** tarjoaa laajennetun kontekstin (visio, laajuus, roolit, linkit).
- **`plans/suunnitelmat/`** -kansio sisältää yksityiskohtaiset modulisuunnitelmat.
- **`todo/TODO-alpha1.0.md`** on tämän hetkinen aktiivinen tehtävälista.

Kun olet valmis siirtymään seuraavaan vaiheeseen, kirjoita vain **"jatka"** — Claude Code siirtyy automaattisesti seuraavaan moduuliin.
