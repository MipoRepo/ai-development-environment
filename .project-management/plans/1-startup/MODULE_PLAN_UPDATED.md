# AI Development Environment (AIDE) - Moduulisovellus

> Tämä dokumentti jako on päivitetty käyttöönottoon ja sen jälkeen ajatellen.
> Perusmodulirakenne on säilytetty (20 moduulit M1–M20).

---

## Käynnistys (Startup) — M1

### Tiivistelmä
AIDE:n ydin on toipitettavissa. Se tarjoaa agenttijärjestelmän, joka voi vastaanottaa tavoitteita ja ohjata agentteja niiden läpimeäksesi.

### Komponentit
- **Director-agentti** — Tulkitsee käyttäjän tavoitteen → valitsee oikean workflowin → orkestroi agentit.
- **Agenttien perusrakenne** — Pydantic-mallit + LangChain-runnerit.
- **Workflowjen tilakone** — YAML-pohjaiset workflowt + tilanhallinta.
- **OpenRouter-integraatio** — LLM-kutsuja varten.
- **Projektin kontekstin lataus** — Lukee `PROJECT.md`, `AGENTS.md`, standardit.

### Laadi (Definition of Done)
- Agentit vastaanottavat JSON- tai YAML-muodossa tehtävät.
- Director valitsee oikean workflowin ja käynnistää sen.
- OpenRouteristä pystyy kutkomaan vähintään yhtä mallia.
- Tilakone pystyy kulkemaan vähintään yhtavan workflowin vaiheiden läpi.
- Testit päälttyvävät vähintään 80 % koodikattavuudella.

---

## Käyttäminen (Runtime) — M2–M5

### M2 — Project Management
- **Komponentit:** Project Manager, Product Planner, Requirements Agent, projektitason tiedostomalli.
- **Laadi:** Uuden projektin luominen (`aide init`) luo `PROJECT.md`, `AGENTS.md`, `planning/`, ja `src/` -hakemistot oikein.

### M3 — Research
- **Komponentit:** Researcher, Technology Researcher.
- **Laadi:** Agentit osaavat analysoida projektin rakenteen ja tarjota teknologivalinnan ehdotuksia.

### M4 — Development
- **Komponentit:** Developer, Refactoring Agent, Code Review Agent.
- **Laadi:** Agentit pystyvät generoimaan, muokkaamaan ja arvioimaan koodia.

### M5 — Testing & QA
- **Komponentit:** Test Designer, Tester, QA Agent.
- **Laadi:** Testit generoidaan ja ajetaan projektin läpivieneen yhteeyksiä vastaan, ja 80 % kattavuus saavutetaan.

### Yhteinen Laadi (M2–M5)
- `Analyze → Plan → Implement → Test → Review → Document` -workflow toimii kokonaisuudessaan käyttäjän antaman pisteestä lähtien.
- Kaikki agentit tuottavat Pydantic-validoidun outputin, jonka seuraava vaihe voi käyttää.

---

## Laajennus (Extension) — M6–M11

### M6 — Security
- **Komponentit:** Security Review, SAST, Dependency Security, Secrets, Container Security.
- **Laadi:** Turvallisuustarkastus saattaa kyseisen workflowin osaksi.

### M7 — Documentation
- **Komponentit:** Technical Writer, API Docs, MkDocs Agent.
- **Laadi:** Dokumentaatio päivittyy automaattisesti koodimuutosskenin yhteydessä.

### M8 — Web Design
- **Komponentit:** UX, UI, Visual Design, Accessibility, Responsive Design.
- **Laadi:** Agentit osaavat suunnitella ja toteuttaa käyttöliittymäkomponentit.

### M9 — Frontend & Backend
- **Komponentit:** Frontend Developer, Backend Developer, API, Database.
- **Laadi:** Web-sovellusten stacki voidaan rakentaa agenttien avulla.

### M10 — DevOps
- **Komponentit:** Docker, CI/CD, Infrastructure, Deployment.
- **Laadi:** Build → Test → Security → Deploy -ketju on automatisoitu.

### M11 — Pedagogy
- **Komponentit:** Mentor, Explainer, Pedagogy, Content Designer.
- **Laadi:** Oppimismateriaali ja ohjeet voidaan tuottaa interaktiivisesti.

### Yhteinen Laadi (M6–M11)
- AIDE pystyy tekemään omanaan kehityssilmäyksen turvallisuuteen asti.
- CI/CD-pipeline on konfiguroitu ja toimii.

---

## Itsekehitys (Self-Improvement) — M12–M17

### M12 — Learning & Assessment
- **Komponentit:** Curriculum, Assessment, Instructional Design.
- **Laadi:** Käyttäjän läpipääsemät oppimispolut luodaan dynaamisesti.

### M13 — Knowledge & Memory
- **Komponentit:** Context Manager, Knowledge Agent, Memory Manager.
- **Laadi:** Projektin historia ja päätökset talletetaan ja toistuvat.

### M14 — Maintenance
- **Komponentit:** Issue Triage, Dependency Manager, Technical Debt, Maintenance.
- **Laadi:** Projektin ylläpito tapahtuu jatkuvasti.

### M15 — Release & Governance
- **Komponentit:** Release Manager, Changelog, Policy, Compliance.
- **Laadi:** Julkaisut ja standardien noudattaminen ovat hallittuja.

### M16 — Agent Engineering
- **Komponentit:** Agent Designer, Tester, Evaluator, Optimizer.
- **Laadi:** Agentit voivat suunnitella ja parantaa omianne.

### M17 — AI Gateway
- **Komponentit:** AI Provider, Model Router, Registry, Evaluator.
- **Laadi:** Mallit reititys ja benchmarkkaus on dynamiikkaa.

### Yhteinen Laadi (M12–M17)
- AIDE pystyy kehittämään omia agenttejaan ja optimoimaan omaa infraaansa.
- API-budjetti seurataan ja offline-fallback toimii.

---

## Integraatio & GUI (Integration & UI) — M18–M20

### M18 — Local LLM
- **Komponentit:** Ollama, GGUF, VRAM-hallinta.
- **Laadi:** Paikalliset LLM:t voidaan käyttää offline-tilaan.

### M19 — MCP & Integrations
- **Komponentit:** MCP-integraatio, GitHub API, ulkoiset työkalut.
- **Laadi:** Agentit voivat turvallisesti käyttää ulkoisia järjestelmiä.

### M20 — GUI / Control Center
- **Komponentit:** Dashboard, visualisointi, seuranta.
- **Laadi:** Graafinen käyttöliittymä tarjoaa kokonaan kuvan järjestelmästä.

### Yhteinen Laadi (M18–M20)
- AIDE on käytettävissä myös graafisen käyttöliittymän kautta ilman komentoriviä.
- Kaikki agentit ja workflowt voidaan seurata reaaliajassa.

---

## Lopputulos

Kun kaikki moduulit ovat valmiita:
- AIDE toimii **CLI:nä**, **agenttijärjestönä** ja **graafisenä työkaluna**.
- Se on **organisaatiotason kehitysjärjestelmä**, joka voi myös **kehittää itseään**.
