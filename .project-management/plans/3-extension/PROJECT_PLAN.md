# AI Development Environment (AIDE) - Projektisuunnitelma

## 1. Johdanto

### Mikä on AIDE?
AI Development Environment (AIDE) on agenttipohjainen ohjelmistokehitysympäristö, joka yhdistää perinteisen ohjelmistotuotannon rakenteet moderniin tekoälyavustamiseen. Se ei ole yksittäinen agentti, vaan kokonainen järjestelmä, joka analysoi projektin, suunnittelee tehtävät, toteuttaa muutokset, testaa, tarkastaa turvallisuuden, päivittää dokumentaation ja oppii järjestelmän historiasta.

### Tavoite ja käyttötarkoitus
1. **Kehitystyön automatisointi** — vähentää rutiinityötä (koodin analyysi, testien generointi, dokumentaation päivitys, refaktorointi, turvallisuustarkastukset).
2. **Projektien yhtenäinen toimintamalli** — määritellään selkeät kehitysmetodit (miten projektit aloitetaan, miten tehtävät pilkotaan, miten agentit toimivat, miten workflowt etenevät).
3. **Oppimisympäristö** — AIDE toimii myös opettajana (Mentor, Explainer, Curriculum, Assessment).

### Ensimmäinen versio
AIDE toimii **komentopohjaisena agenttijärjestönä** (Claude Code / MCP). Graafinen käyttöliittymä (GUI / Agent Control Center) sekä paikalliset LLM:t tulevat myöhemmin.

### Moduulit (20 päämoduulia)
| Moduuli | Nimi | Kuvaus |
| --- | --- | --- |
| M1 | Core & Director | Agenttijärjestelmän ydin, Director, tilakone, OpenRouter-integraatio |
| M2 | Project Management | Project Manager, Product Planner, Requirements, projektin luonti |
| M3 | Research | Researcher, Technology Researcher |
| M4 | Development | Developer, Refactoring, Code Review |
| M5 | Testing & QA | Test Designer, Tester, QA |
| M6 | Security | Security Review, SAST, Dependency, Secrets, Container Security |
| M7 | Documentation | Technical Writer, API Docs, MkDocs Agent |
| M8 | Web Design | UX, UI, Visual Design, Accessibility, Responsive Design |
| M9 | Frontend & Backend | Frontend, Backend, API, Database |
| M10 | DevOps | Docker, CI/CD, Infrastructure, Deployment |
| M11 | Pedagogy | Mentor, Explainer, Pedagogy, Content Designer |
| M12 | Learning & Assessment | Curriculum, Assessment, Instructional Design |
| M13 | Knowledge & Memory | Context Manager, Knowledge Agent, Memory Manager |
| M14 | Maintenance | Issue Triage, Dependency Manager, Technical Debt, Maintenance |
| M15 | Release & Governance | Release Manager, Changelog, Policy, Compliance |
| M16 | Agent Engineering | Agent Designer, Tester, Evaluator, Optimizer |
| M17 | AI Gateway | AI Provider, Model Router, Registry, Evaluator |
| M18 | Local LLM | Ollama, GGUF, VRAM-hallinta |
| M19 | MCP & Integrations | MCP-integraatio, GitHub API, ulkoiset työkalut |
| M20 | GUI / Control Center | Dashboard, visualisointi, seuranta |

> Huom: M21 (Sales) ja M22 (AI-SEO) eivät kuulu ytimeen → ne toteutetaan erikseen myöhemmin.

---

## 2. Arkkitehtuuri

### Ympäristön kolme tasoa
1. **AI Development Environment (päärepo)** — määrittää *miten* kehitys tapahtuu (agentit, workflowt, standardit, työkalut).
2. **AI Development Environment-doc (doc-repo)** — selittää järjestelmän ihmiselle (MkDocs-sivusto, oppaat, käsitteet).
3. **Projektit (esim. RepoStageAI)** — määrittää *mitä* rakennetaan (PROJECT.md, AGENTS.md, src/, tests/).

### Keskeiset periaatteet
- **Agenttiorganisaatio:** Selkeä roolijaotelu (Director, Planner, Developer, Reviewer, Tester, Security, Documentation, Mentor jne.).
- **Workflow-pohjainen toiminta:** `Analyze → Plan → Implement → Test → Review → Document`.
- **Deterministinen engine + AI layer:** AI tekee päätöksenteon ja sisällöntuotannon; engine hoitaa tiedostot, Gitin, testit, validoinnit ja rakenteen datan.
- **Dokumentaatio on osa järjestelmää:** Doc-repo päivittyy automaattisesti.
- **Ihmisen päätösvalta säilytetään:** Agentit ehdottavat muutoksia, eivät tee niitä ilman hyväksyntää.

---

## 3. Repository-rakenne

```
ai-dev-environment/
│
├── agents/                ← kaikki agentit (Director, Developer, jne.)
│   └── <agentti-nimi>/
│       ├── __init__.py
│       ├── agent.py       ← pääluokka (LangChain)
│       └── prompt.j2      ← Jinja2-malli outputille
│
├── workflows/             ← workflowt (Analyze → Plan → ... → Document)
│   └── <workflow-nimi>.yaml
│
├── tools/                 ← työkalukirjastot (Git, Schema Validator, jne.)
│   └── <työkalu-nimi>/
│
├── policies/              ← toimintaperiaatteet (Coding, Security)
├── standards/             ← ympäristön standardit (esim. agent-behavior.md)
├── templates/             ← projektimallit (project-plan.md, roadmap.md)
├── schemas/               ← JSON/YAML-mallioutputit validointia varten
├── tests/                 ← ympäristön omat testit
├── knowledge/             ← pitkäkestoinen tietopankki (adrt/)
│
├── requirements.txt       ← riippuvuudet
├── pyproject.toml         ← projektin määrittely (valinnainen)
├── mkdocs.yml             ← dokumentaatiosivuston konfiguraatio
├── .env                   ← paikalliset salaisuudet (ei commitata)
├── .gitignore
└── .aide/
    └── config.yaml        ← käyttäjäkohtaiset asetukset
```

### Työkalut ja riippuvuudet
- **Python 3.11+** — kieli.
- **LangChain** — agenttien logiikan orkestrointi.
- **OpenAI SDK / OpenRouter** — LLM-kommunikaatio.
- **Pydantic** — outputin validointi.
- **PyYAML** — konfiguraation luku.
- **Jinja2** — prompt-mallit.
- **Typer** — CLI-komennot (`aide init`, `aide run feature`).
- **Pytest** — testaus.

---

## 4. Kehitysjärjestys

Kehitys etenee **neljässä vaiheessa**, jossa jokainen moduuli toteutetaan ja testataan erikseen.

### Vaihe 1: MVP (M1–M7) — 2–4 kuukautta
- **Tavoite:** Työtävä CLI-kehityssilmukka.
- **Moduulit:** Core, Project Management, Research, Development, Testing, Security, Documentation.
- **Lopputulos:** `Sinä → AIDE → Analyze → Plan → Implement → Test → Review → Document` -silmukka toimii.

### Vaihe 2: Beta (M8–M11) — 3–5 kuukautta
- **Tavoite:** Käyttöliittymäkehitys ja DevOps-integraatio.
- **Moduulit:** Web Design, Frontend/Backend, DevOps, Pedagogy.
- **Lopputulos:** AIDE pystyy suunnittelemaan ja rakentamaan web-sovelluksia sekä opettamaan käyttäjää.

### Vaihe 3: Kypsä versio (M12–M20) — 4–8 kuukautta
- **Tavoite:** Autonomian ja organisaatiotason ominaisuudet.
- **Moduulit:** Learning, Knowledge/Memory, Maintenance, Release, Agent Engineering, AI Gateway, Local LLM, MCP, GUI.
- **Lopputulos:** AIDE toimii organisaatiotason välineenä ja voi kehittää itseään.

### Vaihe 4: AI-first development loop — jatkuva
- **Tavoite:** Itsestään kehittävä järjestelmä.
- **Mekaniikka:** AIDE kehittää itseään ja projektejaan iteratiivisesti, säilyttäen ihmisen päätösvalta.

---

## 5. Token- ja API-optimointi

AIDE on suunniteltu toimimaan tehokkaasti myös rajallisilla API-kutsuilla. Seuraavat strategiat minimoivat token- ja kustannuksia:

### 5.1 Mallinvalinta (Model Routing)
- **Analyysi & koodi & review & dokumentaatio:** Claude 3.5 Sonnet (korkea laatu).
- **Yksinkertaiset muokkaukset:** Gemini 2.0 Flash (nopeampi, halvempi).
- **Offline:** Paikalliset LLM-mallit (llama-3.1-8b-instruct).

### 5.2 Caching & Batching
- Toistuvat analyysit (esim. koodin tilarakenteet) väcacheoidaan tiedostoissa (`knowledge/`).
- Useat pienet pyynnöt yhdistetään batch-yksikköihin.

### 5.3 Kontekstin minimointi
- Vain relevantit tiedostot (`PROJECT.md`, `AGENTS.md`, standardit) ladataan agentin työntekemiseksi.
- Konteksti karsitaan moduulin ja workflown tarpeiden mukaan.

### 5.4 API-budget tierit
| Kiintiö | Kehitystapa |
| --- | --- |
| 1 000 kutsua/päivä | Iteratiivinen, mutta rajoitettu. Offline-fallback sijoihin. |
| 60 000 kutsua/kk | AI-first silmukka. Agentit kehittävät iteään. |
| 100 000+ kutsua/kk | Itsekehittävä järjestelmä, joka oppii projektin historiasta. |

### 5.5 Offline-fallback
Kun kiintiö laskee alle `offline_threshold: 50 %`, siirrytään paikallisiin malleihin. Tämä takaa jatkuvan toiminnan myös ilman verkkoa.

---

## 6. CI/CD ja testaus

### GitHub Actions (ci.yml)
- Automaattinen testaus jokaisessa commitissa ja branchissä.
- Asentaa `requirements.txt`, aja `pytest tests/` ja lähetetään coverage-raportti.

```
py.test tests/ --cov=agents --cov-report=xml --cov-fail-under=80
```

### Testaustrategia
- **Unit tests:** Jokainen agentti ja työkalu testataan erikseen (esim. Directorin päätöksenteko, Developerin koodin generaatio).
- **Coverage-vaate:** Vähintään 80 % koodikattavuus.
- **Integration tests:** Workflowt (Analyze → Plan → ... → Document) simuloidaan end-to-end -testein.

---

## 7. Dokumentaatio (MkDocs)

MkDocs Materialilla luodaan projektin dokumentaatiosivusto. Dokumentaatio syntyy automaattisesti agenteista ja workflowistä.

- **`mkdocs.yml`:** Navigaatio ja teema.
- **`docs/`:** Getting Started, User Guide, Concepts, Agents, Architecture.
- **Automaatio:** `Architecture Sync Workflow` → `Documentation Agent` → `docs/architecture/*.md`.

---

## 8. Seuraavat askel

### Moduuli M1: Core & Director
- **Sisältö:** Director-agentti, agenttien perusrakenne, workflowjen tilakone, OpenRouter-integraatio, kontekstinhallinta, Git-perustoiminnot.
- **Lopputulos:** Toimiva agenttijärjestelmän ydin.

Kun olet valmis siirtymään M1:ssä toteuttamiseen, voit kirjoittaa **"jatka"** saadaksesi sen yksityiskohtaisen koodirakenteen, riippuvuudet ja testausstrategian — mukaan lukien:
- Pydantic-malli Directorin outputille
- Jinja2-malli Directorin promptille
- LangChain-agentin rakenteen esimerkin
- `pytest`-testien rakenne M1:lle

---

Tämä projektisuunnitelma on **valmis ja tallennettu**. Se tarjoaa kiinnitetyn perustan, johon voidaan alkaa kirjoittamaan AIDE-järjestelmän koodia.
