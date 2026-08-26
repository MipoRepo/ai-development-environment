# Projekti: AI Development Environment (AIDE)
> Tämä on **projektin keskimmäinen ohje**, joka kuvaa projektin tarkoituksen, vaiheet ja tavan, jolla Claude Codea käytetään tämän projektin toteuttamisessa.

---

## 1. Mikä tämä projekti on (Purpose)

Tämä on **AI Development Environmentin (AIDE) toteutusprojekti**. Tavoitteena on rakentaa agenttipohjainen ohjelmistokehitysympäristö, joka:

- Vastaanottaa käyttäjän tehtävät luonnollisessa kielessä.
- Orkestroi agenttijoukkoa niiden läpimennessä kehitysworkflowit.
- Automatoi ohjelmistokehityksen osa-alueet: analyysi, suunnittelu, koodaus, testaus, turvallisuus, dokumentaatio.
- Toimii sekä kehitystyökaluna että oppimisympäristönä.
- Pystyy myöhemmin kehittämään itseään ja tarjoamaan graafisen käyttöliittymän.

Tämä projekti **ei ole vielä valmis** — se on rakenteilla oleva alusta, jonka koodi kirjoitetaan eri moduuleissa (M1 Core & Director → M20 GUI).

---

## 2. Projektin vaiheet (Phases)

Projekti etenee viidessä selkeässä vaiheessa. Jokainen vaihe koostuu yhdestä tai useammasta moduulista.

| Vaihe | Moduulit | Tavoite |
| --- | --- | --- |
| **1. Käynnistys (Initiation)** | M1 Core & Director | Toimiva agenttijärjestelmän ydin. Director voi vastaanottaa tehtäviä ja valita workflowt. |
| **2. Käyttöaika (Runtime)** | M2 Project Mgmt, M3 Research, M4 Development, M5 Testing | Analysoi → Suunnittele → Toteuta → Testaa -silmukka toimii itsenäisesti. |
| **3. Laajennus (Extension)** | M6 Security → M11 Pedagogy | Lisää turvallisuus, dokumentaatio, web-kehitys, DevOps ja oppiminen. |
| **4. Itsekehitys (Self-Improvement)** | M12 Learning → M17 AI Gateway | AIDE pystyy oppimaan, ylläpitämään tietoa ja kehittämään itseään. |
| **5. Integraatio & GUI** | M18 Local LLM → M20 GUI | Graafinen käyttöliittymä ja paikalliset mallit. Tuotantokäyttökelpoinen versio. |

---

## 3. Miten Claude Codea käytetään tämän projektin toteuttamisessa?

Claude Code on **agenttien suunnittelija ja toteuttaja** tässä projektissa. Sen käyttö tapahtuu kahdella tavalla:

### A. Käynnistyskomennot (Prompts)
Käytä näitä tarkasti määriteltyjä komentoja aloittaaksesi työn jokaisessa vaiheessa:

```bash
# Esimerkki M1 Core & Directorin aloittamisesta:
aide run "Aloita M1 Core & Director -moduulin toteutus. Katsele .project-management/plans/suunnitelmat/1-startup/MODULE_PLAN_UPDATED.md. Luo DirectorAgent, BaseAgent ja Workflow Engine."

# Esimerkki M2 Project Managementin jatkamisesta:
aide run "Siirry M2 Project Management -moduuliin. Totea Project Manager -agentti ja aide init -komento."
```

### B. Edistymisen tarkistus
Voit tarkistaa edistymisen antamalla Claude Code -kehotuksen:
```bash
pytest tests/ --cov=agents --cov-report=term-missing
```

### C. Dokumentaation päivitys
Kun suunnitelmat muuttuvat, päivitä niitä komennolla:
```bash
aide run "Päivitä .project-management/plans suunnitelmat vastaamaan viimeisintä päätöstä."
```

---

## 4. Mitä tätä projektia koskee tietoa tarvitaan?

Projektinhallinta tarvitsee seuraavia tietoja luodakseen AIDE-ympäristön:

- **Tehtävälista (TODO):** `.project-management/todo/TODO.md`
- **Suunnitelmat (Plans):** `.project-management/plans/` — sisältää kaikki modulisuunnitelmat, vaatimukset, arkkitehtuurin.
- **Aikataulu (Schedule):** Sprintit ja milestone-t.
- **Riskit (Risk Register):** Mahdolliset tekniset ja organisatoriset riskit.
- **Resurssit (Resources):** Käytettävät kirjastot, työkalut ja mallit.
- **Budjetti (Budget):** API-kutsujen kustannukset ja optimointi.

Kaikki nämä dokumentit sijaitsevat `.project-management/`-kansiossa ja ne päivittyvät projektin edistymisen myötä.

---

## 5. Projektin lähtötiedot (Outputs)

Kun projekti on valmis, se tuottaa:

1. **`ai-dev-environment/`-repositorion**, jossa on:
   - Agentit (Director, Developer, Security jne.)
   - Workflowt (Analyze → Plan → Implement → Test → Review → Document)
   - CLI-komento (`aide run`, `aide init`)
   - Paikalliset LLM-tuet ja API-integraatiot
2. **Graafisen käyttöliittymän (M20)**, joka näyttää agenttien tilat ja workflowt.
3. **Dokumentaation (MkDocs-sivusto)**, joka kuvaa kaikki yllä.

---

## 6. Projektin omistaja ja yhteystiedot

| Kenti | Tieto |
| --- | --- |
| **Omistaja** | Miko |
| **Tiimi** | Yksittäinen projekti (Claude Code + käyttäjä) |
| **Yhteystapa** | Projekti- ja suunnitelmapohjaiset tiedot `.project-management/`-kansiosta. |
