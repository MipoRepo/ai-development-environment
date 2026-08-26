# AIDE-projektin TODO-lista

> Tämä lista seuraa projektin edistymistä ja määrittelee tarkat tehtävät.
> Jokainen tehtävä on merkitty sen mukaiseen moduuliin (M1–M20) ja vaiheeseen (Käynnistys, Käyttäminen, Laajennus, Itsekehitys, Integraatio & GUI).

---

## Projektin käynnistys — M1 (Core & Director)

### Tehtävä 1: Grundiviiviot ja projektirakenne
- [ ] Luo projektin perusrakenne (`agents/`, `workflows/`, `tools/`, `schemas/`, `tests/`, jne.)
- [ ] Aseta Python-venv ja asenna `requirements.txt`
- [ ] Määritä `.gitignore` ja `.env`

### Tehtävä 2: OpenRouter-integraatio
- [ ] Toteuta `AIProvider`-luokka OpenRouterille
- [ ] Lisää pääsy AVAIN `.env`-tiedostoon
- [ ] Kirjoita yksikkötesti yhteyden testaamiseen

### Tehtävä 3: Agenttien ydin
- [ ] Määritä `Agent`-perusluokka Pydanticillä
- [ ] Toteuta `BaseAgent`-interface (input_schema, run(), output_schema)
- [ ] Kirjoita testit `BaseAgent`-luokalle

### Tehtävä 4: Director-agentti
- [ ] Toteuta `DirectorAgent`-luokka
- [ ] Määritä sen kyky tulkita käyttäjätehtävät YAML/JSON-muodossa
- [ ] Kirjoita testi, jolla Director valitsee oikean workflowin

### Tehtävä 5: Workflowjen tilakone
- [ ] Määritä `Workflow`-luokka YAML-konfiguraatiolle
- [ ] Toteuta tilan siirtyminen (`Analyze → Plan → Implement → ... → Document`)
- [ ] Kirjoaa testi, joka toimii läpi koko workflowin

**Käynnistys valmis kun:** CLI komento `aide run "testi projektin luominen"` toimii ja tuottaa tulosteen jokaisesta workflow-vaiheesta.

**CLI-käynnistys Promptti:**
```bash
# Käynnistä projekti CLI-komennolla:
aide run "Analysoi tämä projekti ja ehdota uusi feature."
# Tai aloita uusi projekti:
aide init --name TestiProjekti --type python-api
```

---

## Käyttäminen — M2–M5

### Tehtävä 6: M2 — Project Management
- [ ] Toteuta Project Manager -agentti
- [ ] Totea `aide init` -komento (luo PROJECT.md, AGENTS.md, planning/, src/)
- [ ] Lisää Requirements Agent -agentti
- [ ] Kirjoita testi projektin luomiselle

### Tehtävä 7: M3 — Research
- [ ] Toteuta Researcher- ja Technology Researcher -agentit
- [ ] Lisää kyky analysoida projektin tiedostoja
- [ ] Kirjoita testi teknologian ehdotuksille

### Tehtävä 8: M4 — Development
- [ ] Toteuta Developer-, Refactoring- ja Code Review -agentit
- [ ] Lisää kyky generoida ja muokata koodia
- [ ] Kirjoita testi koodin generoinnille

### Tehtävä 9: M5 — Testing & QA
- [ ] Toteuta Test Designer-, Tester- ja QA-agentit
- [ ] Lisää testien generointi ja suoritus
- [ ] Varmista 80 % koodikattavuus ensimmäisissä moduuleissa

**Käyttäminen valmis kun:** Käyttäjä voi antaa yhden tavoitteen, ja AIDE suorittaa koko `Analyze → Plan → Implement → Test → Review → Document` -ketjun itsenäisesti.

**Jatkokäynnistys Promptti (kun olet kesken):**
```bash
# Jatka kehittelyä tästä kohdasta:
aide run "Jatka M5 Testing & QA -moduulin toteutusta. Kirjoita testit Test Designer- ja Tester-agenteille."
# Tai tarkista edistyminen:
pytest tests/ --cov=agents --cov-report=term-missing
```

---

## Laajennus — M6–M11

### Tehtävä 10: M6 — Security
- [ ] Toteuta Security Review -agentti
- [ ] Lisää SAST-integralointi (esim. Bandit)
- [ ] Lisää riippuvuuksien turvallisuus tarkistus (pip-audit)
- [ ] Kirjoaa testi turvallisuusrutiineille

### Tehtävä 11: M7 — Documentation
- [ ] Toteuta Technical Writer- ja API Documentation -agentit
- [ ] Määritä MkDocs-generointi agentin avulla
- [ ] Lisää Architecture Sync -toiminto

### Tehtävä 12: M8 — Web Design
- [ ] Toteuta UX-, UI-, ja Visual Design -agentit
- [ ] Lisää käyttöliittymäkomponenttien generointi

### Tehtävä 13: M9 — Frontend & Backend
- [ ] Toteuta Frontend-, Backend-, API- ja Database -agentit
- [ ] Lisää web-sovelluksen generointi

### Tehtävä 14: M10 — DevOps
- [ ] Toteuta Docker-, CI/CD-, Infrastructure- ja Deployment -agentit
- [ ] Luo GitHub Actions -workflow projekteille

### Tehtävä 15: M11 — Pedagogy
- [ ] Toteura Mentor-, Explainer-, Pedagogy- ja Content Designer -agentit
- [ ] Lisää oppimismateriaalin generointi

**Laajennus valmis kun:** AIDE pystyy rakentamaan täysi REST API:n, joka sisältää turvallisuustestit, dokumentaation ja CI/CD:n.

**Laajennus käynnistys Promptti:**
```bash
# Aloita M6 Security -moduulin toteutus:
aide run "Toteuta M6 Security -moduuli: Security Review, SAST, ja Dependency tarkistukset."
```

---

## Itsekehitys — M12–M17

### Tehtävä 16: M12 — Learning & Assessment
- [ ] Toteuta Curriculum- ja Assessment -agentit

### Tehtävä 17: M13 — Knowledge & Memory
- [ ] Toteuta Context Manager-, Knowledge Agent- ja Memory Manager -agentit
- [ ] Lisää SQLite-tietokanta (knowledge.db) historian tallentamiseen

### Tehtävä 18: M14 — Maintenance
- [ ] Toteura Issue Triage-, Dependency Manager-, ja Technical Debt -agentit

### Tehtävä 19: M15 — Release & Governance
- [ ] Toteura Release Manager-, Changelog-, Policy- ja Compliance -agentit

### Tehtävä 20: M16 — Agent Engineering
- [ ] Totea Agent Designer-, Tester-, Evaluator- ja Optimizer -agentit
- [ ] Lisää Agent Engineeringin testaus ja benchmarkkaus

### Tehtävä 21: M17 — AI Gateway
- [ ] Laajenna AI Provideria monimallitukseen
- [ ] Lisää Model Routing ja offline-fallback logiikka

**Itsekehitys valmis kun:** AIDE pystyy benchmarkoimaan omia agenttejaan, optimoimaan niitä, ja käyttämään paikallisia malleja rajoitettuun käyttöön.

**Itsekehitys käynnistys Promptti:**
```bash
# Aloita M13 Knowledge & Memory -moduulin toteutus:
aide run "Toteuta M13 Knowledge & Memory -moduuli: Context Manager, Knowledge Agent, Memory Manager. Lisää SQLite-tietokanta historian tallentamiseen."
```

---

## Integraatio & GUI — M18–M20

### Tehtävä 22: M18 — Local LLM
- [ ] Lisää Ollama-integraatio
- [ ] Lisää GGUF-mallien lataus ja VRAM-hallinta

### Tehtävä 23: M19 — MCP & Integrations
- [ ] Totea MCP-integraatio
- [ ] Lisää GitHub/GitLab API-integraatio turvallisella pääsillä

### Tehtävä 24: M20 — GUI / Control Center
- [ ] Rakenna web-pohjainen dashboard
- [ ] Lisää agenttien tilan ja workflowjen visualisointi

**Integraatio & GUI valmis kun:** AIDE on käytettävissä selaimessa, jossa kaikki agentit ja workflowt voidaan seurata reaaliajassa.

**Integraatio käynnistys Promptti:**
```bash
# Aloita M20 GUI -moduulin suunnittelu:
aide run "Suunnittele ja aloita M20 GUI / Agent Control Center -moduulin toteutus: dashboard, agenttien visualisointi, workflowjen seuranta."
```

---

## Lopputulos

**KOKOASKELE TÄMÄN LISTAN JÄLKEEN ON KUN 100% VALMIS.**

Kun kaikki 24 tehtävää on suoritettu, AIDE on täysi toiminnallinen agenttinen kehitysympäristö:
- CLI-komennot (`aide init`, `aide run`)
- Täysi `Analyze → Plan → Implement → Test → Review → Document` -silmukka
- Turvallisuus- ja dokumentaatiointegraatiot
- Paikalliset LLM-tuet ja graafinen käyttöliittymä
