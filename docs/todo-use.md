# Miten käytän TODO-listaa ja -prompptia?

Tämä ohje selittää, **miten TODO-listat ja -promptit käytetään** projektin seuraamiseen ja kehittämiseen. Jokainen versio on erillinen tiedosto, joka kuvaa tietyn vaiheen tehtävät.

---

## Versioned TODO -rakenne

Projektin edistymisen seuraamiseen käytetään **versionoitua TODO-listaa**. Jokainen versio on erillinen tiedosto, joka kuvaa tietyn vaiheen tehtävät.

| Versio | Vaihe | Kuvaus |
| --- | --- | --- |
| `TODO-alpha1.0.md` | Alpha | M1 Core & Director -moduulin perustoiminnot. |
| `TODO-alpha1.1.md` | Alpha (jatko) | M2–M7 -moduulit (Project Management → Documentation). |
| `TODO-beta1.0.md` | Beta | Beta-vaihe (siirrytään kun kaikki Alpha-tehtavat valmiita). |
| `TODO-release-ready1.0.md` | Release Ready | Julkaisukuntoinen versio. |
| `TODO-release1.0.md` | Release | Tuotantokäyttöinen versio. |

> **Sääntö:** Joka kerta, kun Claude Code -pyyntö edistyy seuraavaan vaiheeseen, se kysyy sinuilta, mihin versioon siirrytään (alpha → beta → release-ready → release). Tämän jälkeen se tallentaa uuden TODO-version `.project-management/todo/`-kansioon.

---

## Miten käytän TODO-listaa?

### 1. Aloita projekti
```bash
# Lue ensimmäisen tehtävän aktiivisesta TODO:sta:
aide run "Aloita M1 Core & Director -moduulin toteutus. Katso .project-management/todo/TODO-alpha1.0.md."
```

### 2. Seuraa edistymistä
```bash
# Tarkista tehtaiden edistyminen:
cat .project-management/todo/TODO-alpha1.0.md
```

### 3. Siirry seuraavaan versioon
```bash
# Kun nykyinen versio on valmiina, siirry seuraavaan:
aide run "Siirry seuraavaan versioon. Katso .project-management/todo/TODO-alpha1.1.md."

# Tai yksinkertaisesti kirjoita:
Siirry <versio>

# Esimerkiksi:
Siirry alpha1.1
```

---

## Esimerkkisofta: TODO-alpha1.0.md

Tässä on esimerkki siitä, miten TODO-alpha1.0.md -tiedoston tulisi näyttää:

---

### Tehtävä 1: Grundiviiviot ja projektirakenne
- [ ] Luo projektin perusrakenne (`agents/`, `workflows/`, `tools/`, `schemas/`, `tests/`, jne.)
- [ ] Aseta Python-venv ja asenna `requirements.txt`
- [ ] Määritä `.gitignore` ja `.env`

### Tehtävä 2: OpenRouter-integraatio
- [ ] Totea `AIProvider`-luokka OpenRouterille
- [ ] Lisää pääsy AVAIN `.env`-tiedostoon
- [ ] Kirjoita yksikkötesti yhteyden testaamiseen

### Tehtävä 3: Agenttien ydin
- [ ] Määritä `Agent`-perusluokka Pydanticillä
- [ ] Totea `BaseAgent`-interface (input_schema, run(), output_schema)
- [ ] Kirjoita testit `BaseAgent`-luokalle

### Tehtävä 4: Director-agentti
- [ ] Totea `DirectorAgent`-luokka
- [ ] Määritä sen kyky tulkita käyttäjätehtävät YAML/JSON-muodossa
- [ ] Kirjoita testi, jolla Director valitsee oikean workflowin

### Tehtävä 5: Workflowjen tilakone
- [ ] Määritä `Workflow`-luokka YAML-konfiguraatiolle
- [ ] Totea tilan siirtyminen (`Analyze → Plan → Implement → ... → Document`)
- [ ] Kirjoaa testi, joka toimii läpi koko workflowin

---

**Käynnistys valmis kun:** CLI-komento `aide run "testi projektin luominen"` toimii ja tuottaa tulosteen jokaisesta workflow-vaiheesta.

**CLI-käynnistys Promptti:**
```bash
# Luo .venv ja asenna riippuvuudet:
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
# Aja CLI:
aide run "Analysoi tämä projekti ja ehdota uusi feature."
# Tai aloita uusi projekti:
aide init --name TestiProjekti --type python-api
```

---

## Miten promptit toimivat?

### Käynnistyskomennot
```bash
# Esimerkki M1 Core & Directorin aloittamisesta:
aide run "Aloita M1 Core & Director -moduulin toteutus. Katso .project-management/plans/suunnitelmat/1-startup/MODULE_PLAN_UPDATED.md. Luo DirectorAgent, BaseAgent ja Workflow Engine."

# Esimerkki M2 Project Managementin jatkamisesta:
aide run "Siirry M2 Project Management -moduuliin. Totea Project Manager -agentti ja aide init -komento."
```

### Edistymisen tarkistus
```bash
# Käytä tätä tarkistaaksesi testien edistymisen:
pytest tests/ --cov=agents --cov-report=term-missing
```

---

Jos sinulla on kysymyksiä tai tarvitset apua projektissa, voit aina kysyä: **"Jatka"** — ja järjestelmä siirtyy seuraavaan vaiheeseen.
