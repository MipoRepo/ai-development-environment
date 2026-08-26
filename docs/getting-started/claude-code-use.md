# Claude Coden käyttö AIDE-projektissa

> Tämä ohje kertoo, **miten Claude Codea käytetään AIDE:n (AI Development Environment) projektin toteuttamisessa**. Se on erillinen sivu, jonka tarkoitus on olla projektiin liittymisen ensimmäinen lähde.

---

## Mikä tämä on?

Claude Code on **ohjelmiston kehittämisen apuväline**, joka voi:
- Lukea ja ymmärtää projektin rakenteen.
- Kirjoittaa koodia, testejä ja dokumentaatiota.
- Seurata tehtaita TODO-listan avulla.
- Itse optimoida koodia ja dokumentaatiota.

Tämä sivu kertoo, miten sinun täytyy käyttää Claude Coden projektiisi.

---

## Kuinka käytän Claude Coden projektissa?

### 1. Aktivoi projektimuisti (Memory)
Ensinnäkin, varmista että projektin säännöt ja päätökset säilyvät:

```bash
# Luo muistikansio:
mkdir -p .claude/memories

# Luo sääntö-tiedosto:
touch .claude/memories/project-rules.md
```

Lisää sinne tärkeimmät säännöt (esim. "Käytä MkDocs 1.5.x", "Testikattavuus 80 %+").

---

### 2. Lue ensin TODO-listan
Aina kun aloitat keskustelun Claude Coden kanssa, kirjoita ensin:
```text
Katso .project-management/todo/TODO-alpha1.0.md ja aloita Tehtävä 2: OpenRouter-integraatio.
```

Tämä antaa Claude Coden täyden konteksitin siitä, missä kohtaa olet.

---

### 3. Anna tarkat ohjeet
Älä kirjoita liian yleitä kehotteita. Esimerkiksi:

**HUONO:**
> "Totea Director-agentti."

**HYVÄ:**
> "Totea DirectorAgent-luokka tiedostoon `agents/director.py` käyttäen Pydanticiä. Se valitsee workflowin YAML-tiedoston peruste. Katso `.project-management/todo/TODO-alpha1.0.md`."

Tämä auttaa Claude Coden ymmärtämään, mitä juuri haluat.

---

## Mitkä ovat työnkulkuun kuuluvat promptit?

| Tilanne | Promptti |
| --- | --- |
| **Aloita M1** | `"Aloita M1 Core & Director -moduulin toteutus. Katso .project-management/todo/TODO-alpha1.0.md."` |
| **Jatka M2** | `"Siirry Alpha 1.1 -versioon (M2–M7). Katso .project-management/todo/TODO-alpha1.1.md."` |
| **Tarkista edistyminen** | `"Tarkista TODO-listan edistyminen ja anna seuraavat vaiheet."` |
| **Kirjoita testi** | `"Kirjoaa testi `test_director.py`, joka testaa, että Director valitsee oikean workflowin."` |
| **Päivitä dokumentaatio** | `"Päivitä docs/architecture/overview.md vastaamaan nykyistä koodia."` |

---

## Miten seurata edistymistä?

Käytä tätä komentoa:

```bash
pytest tests/ --cov=agents --cov-report=term-missing
```

Tämä näyttää, kuinka monta testiä läpäistiin ja mikään koodi ei ole vielä testattu. Tavoitteena on vähintään **80 %** koodikattavuus jokaisessa moduulissa.

---

## Vinkit

1. **Muista päivittää muistit:** Kun tehdät päätöksen (esim. "valitsen X kirjaston"), pävitängi se `.claude/memories/project-rules.md`.
2. **Älä unohda `.env`-tiedostoa:** Se sisältää salaisuudet eikä saa päätyä versionhallintoon.
3. **Käytä `#` -kommentteja koodissa:** Tämä auttaa myöhemmässä ymmärtämisessä.
