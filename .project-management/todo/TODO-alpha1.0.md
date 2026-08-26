# AIDE-projektin TODO-lista (Alpha 1.0)

> Tämä lista seuraa projektin edistymistä M1 (Core & Director) -moduulissa.
> Kun tämä lista on valmis, siirry se `old_todo/`-kansioon ja luo uusi lista (.project-management/todo/TODO-alpha1.1.md) seuraaville moduuleille (M2–M7).

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

Tämä on erillinen osio siitä, **miten projektin tulee käyttää Claude Code -muistia** (eli projektin muistoita) oikein ja johdonmukaisesti. Jos muisti ei ole käytössä, ota se käyttöön seuraamalla tätä ohjetta.

### Ongelma
Jos projektin keskeiset päätökset, standardit tai työnkulku eivät säilyudu yhä läpinäkyvänä, projekti voi " unoistaa" aiemmat päätökset tai tehdä ne uudelleen ristiriidallisiksi.

### Ratkaisu
Aseta Claude Code -muistit käyttöön tämän projektin juureen seuraavilla avuksilla:

1. Luo hakemisto muisteille:
   ```bash
   mkdir .claude/memories
   ```

2. Luo tiedosto `.claude/memories/project-rules.md` ja lisää sinne tärkeimmät säännöt:
   ```markdown
   ---
   name: project-rules
   description: AIDE-projektin yleiset säännöt ja päätökset
   type: reference
   ---

   # AIDE-projektin säännöt

   - AINA käytä Python ≥3.11.
   - AINA käytä MkDocs versiota 1.5.x (EI 1.6 tai uudempaa).
   - Älä koskaan committaa .env-tiedostoa.
   - Testikattavuuden tulee olla vähintään 80 % jokaisessa moduulissa.
   - Jokaisen agentin täytyy olla Pydantic-validoitu JSON-output.
   ```

3. (Valinnainen) Luo `.claude/memories/architecture-decisions.md`, jossa dokumentoidaan jokainen suuri päätös (esim. miksi valitit LangChainin).

4. Varmista, että nämä tiedostot ovat mukana Git-versiossa.

Kun nämä muistit ovat käytössä, **tämä projekti tulee muistamaan kaikki päätöksensä** koko kehityksen ajan. Jos sinä (tai Claude Code) teet päätöstä, jota ei ole vielä dokumentoitu, kirjoita se heti muistitiedostoon!

---

## Tehtävä 1: Grundiviiviot ja projektirakenne ✅
- ✅ Luo projektin perusrakenne (`agents/`, `workflows/`, `tools/`, `schemas/`, `tests/`).
- ✅ Aseta Python-venv ja asenna `requirements.txt`.
- ✅ Määritä `.gitignore` (lisätty: `.env`, `.venv/`, `__pycache__/`, `site/`, `knowledge.db`).
- ✅ Luo ja varmista `.claude/memories/`-kansio käytön sääntöjen säilyttämiseksi (katso yllä).

## Tehtävä 2: OpenRouter-integraatio
- [ ] Totea `AIProvider`-luokka OpenRouterille (`tools/ai_provider.py`).
- [ ] Lisää pääsy AVAIN `.env`-tiedostoon.
- [ ] Kirjoita yksikkötesti yhteyden testaamiseen (`tests/test_ai_provider.py`).

## Tehtävä 3: Agenttien ydin ✅
- ✅ Määritä `Agent`-perusluokka Pydanticillä (`agents/base.py`).
- ✅ Totea `BaseAgent`-interface (input_schema, run(), output_schema).
- [ ] Kirjoita testit `BaseAgent`-luokalle (`tests/test_base_agent.py`).

## Tehtävä 4: Director-agentti ✅
- ✅ Totea `DirectorAgent`-luokka (`agents/director.py`).
- ✅ Määritä sen kyky tulkita käyttäjätehtävät YAML/JSON-muodossa.
- [ ] Kirjoita testi, jolla Director valitsee oikean workflowin (`tests/test_director.py`).

## Tehtävä 5: Workflowjen tilakone ✅
- ✅ Määritä `Workflow`-luokka YAML-konfiguraatiolle (`workflows/engine.py`).
- ✅ Totea tilan siirtyminen (`Analyze → Plan → Implement → Test → Review → Document`).
- [ ] Kirjoaa testi, joka toimii läpi koko workflowin (`tests/test_workflow_engine.py`).
- [ ] Luo `base.yaml` workflow-tiedosto (`workflows/base.yaml`).

---

**M1 valmis kun (Käynnistys valmis):**
CLI-komento `aide run "testi projektin luominen"` toimii ja tuottaa tulosteen jokaisesta workflow-vaiheesta.

**CLI-käynnistys Promptti:**
```bash
# Käynnistä projekti CLI-komennolla:
# Luo .venv ja asenna riippuvuudet:
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
# Aja CLI:
python cli.py run "Analysoi tämä projekti ja ehdota uusi feature."
# Tai aloita uusi projekti:
python cli.py init --name TestiProjekti
```
