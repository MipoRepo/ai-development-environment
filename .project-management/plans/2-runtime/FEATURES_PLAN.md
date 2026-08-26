# Toiminnallisuuksia (Featureit) kuvaava suunnitelma

Tämä dokumentti kuvaa **mitä AIDE:n päärepositoriossa tulisi toteuttaa** ja mitkä toiminnallisuudet on priorisoitu. Featureit jolautuvat moduulikohtaisesti (M1–M20).

## Featureit M1–M7 (MVP-vaihe)

### M1 — Core & Director
- Agenttien perusrakenne (JSON-in/Zuul-out)
- Director-agentti (tehtävän tulkitseminen → workflowin valinta → agenttien orkestrointi)
- Workflowjen tilakone (Analyze → Plan → Implement → Test → Review → Document)
- OpenRouter-integraatio (Claude 3.5 Sonnet, Gemini 2.0 Flash)
- Projektin kontekstin lataus (AGENTS.md, PROJECT.md, standardit)
- Git-perustoiminnot agenteille (checkout, branch, commit)

### M2 — Project Management
- Project Manager -agentti
- Product Planner -agentti
- Requirements Agent (käyttäjätarinat, hyväksymiskriteerit)
- Uuden projektin luonti (hakemiston luonti, PROJECT.md, AGENTS.md)
- Backlogin ja milestoneiden hallinta

### M3 — Research
- Researcher -agentti (yleistutkimus)
- Technology Researcher -agentti (teknologian vertailu)
- Standardien ja dokumentaation analysointi

### M4 — Development
- Developer -agentti (yleinen koodijen generointi/muokkaus)
- Refactoring Agent
- Code Review Agent
- Testien generointi (unit-, integraatio-, API-testit)

### M5 — Testing & QA
- Test Designer (testisuunnitelma)
- Tester (testien suoritus)
- QA Agent (laadun arviointi)
- Testikattavuusraportti (≥ 80 % koodikattavuus määritys)

### M6 — Security / DevSecOps
- Security Review Agent (turvallisuuskatsaus)
- SAST (vastaavasti Bandit/SonarQube)
- Dependency Security (CVE-tarkistus)
- Secrets -etsintä (API-avaimet, salasanat)
- Container Security (Dockerfile-analyysi)

### M7 — Documentation
- Technical Writer (arkkitehtuuridokit)
- API Documentation Agent (OpenAPI-käsikirjoitukset)
- User Documentation Agent (käyttöohjeet, tutorialit)
- MkDocs Agent (sivuston generointi ja päivitys)

---

## Featureit M8–M11 (Beta-vaihe)

### M8 — Web Design
- UX Agent (käyttäjäpolkujen suunnittelu)
- UI Agent (komponenttimallit)
- Visual Design Agent (tyylit, brändäys)
- Accessibility Agent (WCAG-tarkistus)
- Responsive Design Agent (laitteiston tarkistus)

### M9 — Frontend & Backend
- Frontend Developer Agent (HTML/CSS/JS)
- Backend Developer Agent (palvelinlogiikka)
- API Agent (REST/GraphQL-rajapinnat)
- Database Agent (skema, migraatiot)
- Component Agent (design systemin ylläpito)

### M10 — DevOps
- Docker Agent (Dockerfilejen generointi)
- CI/CD Agent (GitHub Actions -workflowt)
- Infrastructure Agent (IaC-skriptit)
- Deployment Agent (release-flow)

### M11 — Pedagogy
- Mentor Agent (vinkit ongelmanratkaukseen)
- Explainer Agent (selitykset 4-tasolla)
- Pedagogy Agent (opetusstrategia)
- Content Designer (sisällön rakenne)

---

## Featureit M12–M20 (Kypsä versio)

### M12 — Learning & Assessment
- Curriculum Agent (oppimispolku)
- Assessment Agent (osaamisen tarkistus)
- Instructional Design Agent (teoria → esimerkki → harjoitus → haaste → arviointi)

### M13 — Knowledge & Memory
- Context Manager (istunnon konteksti)
- Knowledge Agent (projektin tietopankki)
- Memory Manager (historian ja päätösten tallennus)

### M14 — Maintenance
- Issue Triage Agent (bugien luokittelu)
- Dependency Manager (riippuvuuksien päivitykset)
- Technical Debt Agent (refaktorointitarve)
- Maintenance Agent (yleinen ylläpito)

### M15 — Release & Governance
- Release Manager (versionhallinta, julkaisut)
- Changelog Agent (CHANGELOG-generointi)
- Policy Agent (standardien valvonta)
- Compliance Agent (GDPR, EU AI Act -tarkistus)

### M16 — Agent Engineering
- Agent Designer (uusien agenttien luonti)
- Agent Tester (agentin outputin tarkistus)
- Agent Evaluator (laadun mittarit)
- Agent Optimizer (promptin parantaminen)

### M17 — AI Gateway
- AI Provider (OpenRouter/OpenAI yhteys)
- Model Router (mallin valinta tehtävän avulla)
- Model Registry (mallien metadata)
- Model Evaluator (mallin benchmarkkaus)

### M18 — Local LLM
- Ollama-integraatio
- GGUF-mallin lataus
- VRAM/latency-hallinta
- Mallien benchmarkkaus

### M19 — MCP & Integrations
- MCP-integraatio (Secure Context Tool -protokolla)
- GitHub/GitLab -rajapinnat
- Ulkoisten työkalujen turva-asetukset

### M20 — GUI / Agent Control Center
- Dashboard (projektit, agentit)
- Agenttien tilan visualisointi
- Workflowjen seuronta (reaaliaikainen edistymispalkki)
- Dokumentaation selaus ja päivitys

---

## Featureien priorisointi

| Feature-taso | Prioriteetti | Selitys |
| --- | --- | --- |
| MVP (M1–M7) | **Korkea** | Pakollinen CLI-toiminta ja komennollinen kehityssilmukka. |
| Beta (M8–M11) | **Keski** | Tuoda käyttöliittymä- ja DevOps-ominaisuudet sekä oppimisversion. |
| Kypsä (M12–M20) | **Tärkeä** | Tukea organisaatiotason käyttöön ja itsekehittämistä. |
