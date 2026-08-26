# AI Development Environment - Toteutussuunnitelma

## Johdanto

Tämä dokumentti määrittelee modulaarisen toteutussuunnitelman AI Development Environment (AIDE) -järjestelmälle. Se pohjautuu `ai-development-environment-doc`-repositorion ohjeistukseen ja tarkentaa, miten järjestelmä toteutetaan moduuleihin, joista kukin on itsenäinen ja testattavissa. Lisäksi sisältää token- ja API-kutsujen optimointistrategian.

---

## 1. Moduulijako (toteutusmoduulit)

AIDE jakaan **20 toteutusmoduuliin**, jotka vastaavat alkuperäisen dokumentaation M1–M20 -moduuleja. Jokainen moduuli on itsenäinen ja sisältää oman agenttiesitynsä, workflownsä ja testinsä.

### M1 — Core & Director
- **Sisältö:** Director-agentti, agenttien perusrakenne, tehtävien jako, workflowjen tilakone, kontekstinhallinta, AI-adapteri (OpenRouter).
- **Lopputulos:** Toimiva agenttijärjestelmän ydin.

### M2 — Project Management
- **Sisältö:** Project Manager, Product Planner, Requirements Agent, projektin luonti, backlog, milestone-t, tehtävien pilkkominen.
- **Lopputulos:** AIDE pystyy luomaan ja hallitsemaan projekteja.

### M3 — Research
- **Sisältö:** Researcher, Technology Researcher, dokumentaation ja standardien analysointi.
- **Lopputulos:** Agentit osaavat tutkia teknisiä ratkaisuja.

### M4 — Development
- **Sisältö:** Developer, Refactoring Agent, Code Review Agent, koodin generointi, muokkaus ja arviointi.
- **Lopputulos:** AIDE pystyy toteuttamaan koodimuutoksia.

### M5 — Testing & QA
- **Sisältö:** Test Designer, Tester, QA Agent, testien generointi ja suoritus.
- **Lopputulos:** Automaattinen testaus ja laadun arviointi.

### M6 — Security / DevSecOps
- **Sisältävät:** Security Review, SAST, Dependency Security, Secrets, Container Security.
- **Lopputulos:** Kehityksen turvallisuustarkastus.

### M7 — Documentation
- **Sisältö:** Technical Writer, User Documentation, API Documentation, MkDocs Agent.
- **Lopputulos:** Dokumentaatio syntyy ja päivittyy automaattisesti.

### M8 — Web Design
- **Sisältö:** UX, UI, Visual Design, Accessibility, Responsive Design.
- **Lopputulos:** Käyttöliittymien suunnittelu ja toteutus.

### M9 — Frontend & Backend
- **Sisältö:** Frontend Developer, Component Agent, Backend Developer, API Agent, Database Agent.
- **Lopputulos:** Täydellisten web-sovellusten toteutus.

### M10 — DevOps
- **Sisältö:** Docker, CI/CD, Infrastructure, Deployment.
- **Lopputulos:** Build → test → security → deploy -ketju.

### M11 — Pedagogy
- **Sisältö:** Mentor, Explainer, Pedagogy Agent, Content Designer.
- **Lopputulos:** AIDE toimii oppimisympäristönä.

### M12 — Learning & Assessment
- **Sisältö:** Curriculum Agent, Assessment Agent, Instructional Design.
- **Lopputulos:** Henkilökohtainen oppimispolku ja osaamisen arviointi.

### M13 — Knowledge & Memory
- **Sisältö:** Context Manager, Knowledge Agent, Memory Manager.
- **Lopputulos:** Projektin pitkäkestoinen konteksti ja historiatieto.

### M14 — Maintenance
- **Sisältö:** Issue Triage, Dependency Manager, Technical Debt Agent, Maintenance Agent.
- **Lopputulos:** Projektin ylläpito ja teknisen vellan hallinta.

### M15 — Release & Governance
- **Sisältö:** Release Manager, Changelog Agent, Policy Agent, Compliance Agent.
- **Lopputulos:** Hallittu julkaisu ja sääntöjen valvonta.

### M16 — Agent Engineering
- **Sisältö:** Agent Designer, Agent Tester, Agent Evaluator, Agent Optimizer.
- **Lopputulos:** AIDE pystyy kehittämään omia agenttejaan.

### M17 — AI Gateway
- **Sisältö:** AI Provider, Model Router, Model Registry, Model Evaluator.
- **Lopputulos:** Yhtenäinen rajapinta OpenRouteriin ja muihin AI-palveluiin.

### M18 — Local LLM
- **Sisältö:** Ollama-integraatio, paikalliset mallit, VRAM/latency-hallinta, benchmarking.
- **Lopputulos:** Paikallinen AI osuuks järjestelmään.

### M19 — MCP & Integrations
- **Sisältö:** MCP-integraatio, GitHub/GitLab API, ulkoiset työkalut, turvallinen agenttipääsy.
- **Lopputulos:** Agentit voivat käyttää ulkoisia järjestelmiä.

### M20 — GUI / Agent Control Center
- **Sisältö:** dashboard, agenttien hallinta, workflowjen visualisointi, projektien näkymä, monitorointi.
- **Lopputulos:** Graafinen käyttöliittymä koko ympäristölle.

> **Huom:** M21 (Sales) ja M22 (AI-SEO) eivät kuulu tähän moduulijakoihin, koska ne eivät ole osa ytimen toiminnallisuutta. Ne voidaan lisätä myöhemmin erillisenä laajennuksina.

---

## 2. Kehitysjärjestys

Kehitys etenee **moduulien M1–M20 mukaisessa järjestyksessä**, jossa jokainen moduuli on itsenäinen ja sisältää oman agentitason, workflownsä ja testinsä.

### Vaihe 1: MVP (M1–M7)
- Core & Director, Project Management, Research, Development, Testing & QA, Security, Documentation.
- AIDE pystyy suunnittelemaan, toteuttamaan, testaamaan, tarkastamaan turvallisuutta ja päivittämään dokumentaatiota.
- Komentopohjainen käyttöliittymä Claude Code / MCP:n kautta.

### Vaihe 2: Beta (M8–M11)
- Web Design, Frontend & Backend, DevOps, Pedagogy.
- AIDE pystyy suunnittelemaan käyttöliittymiä ja rakentamaan web-sovelluksia sekä CI/CD-pipelineja.

### Vaihe 3: Kypsä versio (M12–M20)
- Learning & Assessment, Knowledge & Memory, Maintenance, Release & Governance, Agent Engineering, AI Gateway, Local LLM, MCP & Integrations, GUI.
- AIDE pystyy ylläpitämään projektin historiatietoa, arvioimaan käyttäjän osaamista, käyttämään paikallisia LLM-malleja ja tarjoamaan graafista käyttöliittymää.

### Vaihe 4: AI-first development loop
- Kun kaikki moduulit ovat valmiit, AIDE pystyy kehittämään itseään iteratiivisesti.

---

## 3. Token- ja API-kutsujen optimointi

AIDE on suunniteltu toimimaan tehokkaasti myös rajallisilla API-kutsuilla. Seuraavat strategiat minimoivat tokenkäytön ja API-kutsujen määrää.

### 3.1 Mallin valinta (Model Routing)
- **Analyysi & koodin generointi & review & dokumentaatio:** Claude 3.5 Sonnet (korkea laatu).
- **Yksinkertaiset muokkaukset & tiivistelmät:** Gemini 2.0 Flash (nopeampi ja halvempi).
- **Offline & alhaisempi hinta:** paikalliset LLM-mallit (esim. llama-3.1-8b-instruct).

### 3.2 Caching & Batching
- Toistuvat analyysit (esim. koodin tilarakenteet) väcacheoidaan.
- Useat pienet pyynnöt yhdistetään yhteen batch-requestiin.

### 3.3 Kontekstin minimointi
- Projektin konteksti karsitaan moduulin ja workflown tarpeiden mukaan.
- Vain relevantit tiedostot ja standardit ladataan agentin työntekemiseksi.

### 3.4 API-budget tierit (kyvykkyys tasot)
| Kiintiö | Kehitystapa |
| --- | --- |
| 1 000 kutsua/päivä | Iteratiivinen, mutta rajoitettut kehitys. Offline-fallback sijoihin. |
| 60 000 kutsua/kk | AI-first kehityssilmukka. Agentit keyttävät itseään. |
| 100 000+ kutsua/kk | Itseparannava järjestelmä, joka oppii projektin historiasta. |

### 3.5 Offline-fallback
- Kun kiintiö laskee alle `offline_threshold: 50 %%`, siirrytään paikallisiin malleihin.
- Tämä varmistaa jatkuvan toiminnan myös ilman verkkoa.

---

## 4. Tiedoston sijoittelu suunnitelmaan

Tämä suunnitelma tallennetaan seuraavaan tiedostoon:
`F:\github-repositories\ai-dev-environment\AI_DEVELOPMENT_ENVIRONMENT_IMPL_PLAN.md`

---
