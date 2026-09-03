# AIDE-projektin TODO-lista (Alpha 1.1)

> Tämä lista seuraa projektin edistymistä **M2–M7** -moduuleissa (Käytössä -vaihe).
> Kun tämä lista on valmis, siirä se `old_todo/`-kansioon ja luo uusi lista (`TODO-alpha1.2.md`) seuraaville moduuleille (M8–M11).

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

> ⚠️ **Tärkeä muistutus:** AINA ennen kuin teet jotain uutta, varmista että projektimuistisi on ajantasalla. Päivitä `.claude/memories/project-rules.md` säännöllisesti päätöksillesi.

Esimerkiksi, kun teet päätöksen siitä, mitä kirjastoa käytetään M2:ssa, tallenna se heti:
```markdown
# project-rules.md (päivitetty)

- M2 Project Management -moduulissa käytetty CLI-kirjasto on: `Typer`.
- ...
```

---

## Tehtävä 6: M2 — Project Management  ✅ VALMIS
- [x] Totea `ProjectManagerAgent`-luokka (`agents/project_manager.py`)
- [x] Totea `aide init`-toiminto (luo `PROJECT.md`, `AGENTS.md`, `planning/`, `src/`)
- [x] Lisää `RequirementsAgent`-agentti (`agents/requirements_agent.py`)
- [x] Kirjoita integraatiotestit projektin luomiselle (`tests/test_project_init.py`)
- [x] Lisää testit `test_project_manager.py` (22 testiä)
- [x] Kaikki M2-testit läpäisty (30 uutta testiä, 116 yhteensä)
- [x] CLI `init` integroi RequirementsAgent + ProjectManagerAgent
- [x] Kaikki 116 testiä läpäistyi (94 % koodikattavuus)

## Tehtävä 7: M3 — Research  ✅ VALMIS
- [x] Totea `ResearcherAgent`- ja `TechnologyResearcherAgent`-luokat
- [x] AST-pohjainen tiedostojen analyysi (funktiot, luokat, importit)
- [x] Projektirakenteen rekonstruointi dictionaryna
- [x] Teknologisten havaitsijan avulla teknologioiden havaitseminen
- [x] Kirjoita testit (`tests/test_research_agents.py`) — 32 testiä

## Tehtävä 8: M4 — Development  ✅ VALMIS
- [x] Totea `DeveloperAgent` ja sen sora (`agents/developer.py`)
- [x] Lisää `RefactoringAgent`- ja `CodeReviewAgent`-luokat
- [x] Koodin generointi (Python/JS/Markdown), tiedostojen luonti
- [x] Refaktorointi: puuttuvat doksekeinnot, käyttämättomat importit, pitkät funktiot
- [x] Koodin tarkistus: turvallisuus + laatu ongelmat
- [x] Kirjoita testit (`tests/test_developer_agent.py`) — 32 testiä

## Tehtävä 9: M5 — Testing & QA  ✅ VALMIS
- [x] Totea `TestDesignerAgent`, `TesterAgent`, `QAAgent`
- [x] AST-pohjainen testisuunnittelu (funktiot → testitapaukset)
- [x] Pytest-komennon suoritus subprocessillä ja tulosteen parsinta
- [x] QA: koodikattavuus, testitiedostot, ohjelmointikäytännöt
- [x] Varmista 80 % koodikattavuus ensimmäisissä moduuleissa (94 %)
- [x] Kirjoita testit (`tests/test_testing_agents.py`) — 24 testiä

## Tehtävä 10: M6 — Security  ✅ VALMIS
- [x] Totea `SecurityReviewAgent`, `SASTAgent`, `DependencySecurityAgent`, `SecretsAgent`, `ContainerSecurityAgent`
- [x] AST-pohjainen SAST-analyysi (eval, exec, vaaralliset importit)
- [x] Riippuvuusturva (tunnetut paketit: django, flask, requests, pyyaml, numpy, pillow)
- [x] Salaisuusskanningi (AWS-keys, GitHub-tokenit, API-avaimet, salaisuusavaimet)
- [x] Dockerfile-turvallisuus (root-käyttäjä, ADD, chmod 777, EXPOSE 22, curl|sh)
- [x] Kirjoita testit (`tests/test_security_agents.py`) — 40 testiä

## Tehtävä 11: M7 — Documentation  ✅ VALMIS
- [x] Totea `TechnicalWriterAgent`, `APIDocumentationAgent`, `UserDocumentationAgent`, `MkDocsAgent`
- [x] AST-pohjainen API-endpointin analyysi (FastAPI-decoratorit, funktiot, docstringit)
- [x] OpenAPI-3.0-skeeman generointi endpointeista
- [x] README-generointin ominaisuuksilla, asennusohjeilla, käyttöohjeilla
- [x] MkDocs-generointi (mkdocs.yml, nav, oletussivut: index/api/user-guide)
- [x] Kirjoita testit (`tests/test_documentation_agents.py`) — 46 testiä

## Tehtävä 12: M8 — Testing Automation  ✅ VALMIS
- [x] Totea `TestRunnerAgent`, `PerformanceTestAgent`, `IntegrationTestAgent`
- [x] Test-runner (pytest subprocess, coverage-analyysi, fail-fast, output-parseri)
- [x] Performance-testaus (benchmarkit, warmup, percentile-laskenta)
- [x] Integraatiotestaus (moduulien tuonti, cross-module-riippuvuudet)

## Tehtävä 13: M9 — Orchestration  ✅ VALMIS
- [x] Totea `WorkflowOrchestratorAgent` ja `MultiAgentCoordinator`
- [x] Workflow-orkesterointi (vaiheiden suoritus, kontekstin päivitys, stop_on_error)
- [x] Topologinen järjestys riippuvuuksien mukaan (Kahnin algoritmi)
- [x] Moniagentti-koordinaatio (suoritusaika, koordinaatiopisteet)

---

**Beta valmis kun (Käytössä valmis):**
Käyttäjän antama yksi tehtävä ajettaa läpi koko `Analyze → Plan → Implement → Test → Review → Document` -ketjun itsenäisesti.

**Beta käynnistys Promptti:**
```bash
# Jatka M2 Project Managementin toteutuksella:
aide run "Aloita M2 Project Management -moduulin toteutus. Totea ProjectManagerAgent ja aide init -toiminto."
```

---

## Projektin dokumentaation päivitys

Kun olet edistymässä, pävitä dokumentaasi jokaisella moduulilla:
- Pävitä `docs/agents/*.md`-tiedostot kuvaamaan uusia agentteja.
- Pävitä `docs/architecture/agent-layer.md` viittaamaan kaikkiin 22 moduuliin.
- Jatka `.project-management/todo/TODO-alpha1.1.md` päivitystä tarkistuksin.
