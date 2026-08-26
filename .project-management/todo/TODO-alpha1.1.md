# AIDE-projektin TODO-lista (Beta 1.0)

> Tämä lista seuraa projektin edistymistä **M2–M7** -moduuleissa (Käytössä -vaihe).
> Kun tämä lista on valmis, siirä se `old_todo/`-kansioon ja luo uusi lista (`.project-management/todo/TODO-release-ready1.0.md`) seuraaville moduuleille (M8–M11).

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

## Tehtävä 6: M2 — Project Management
- [ ] Totea `ProjectManagerAgent`-luokka (`agents/project_manager.py`)
- [ ] Totea `aide init`-toiminto (luo `PROJECT.md`, `AGENTS.md`, `planning/`, `src/`)
- [ ] Lisää `RequirementsAgent`-agentti (`agents/requirements_agent.py`)
- [ ] Kirjoita integraatiotestit projektin luomiselle (`tests/test_project_init.py`)

## Tehtävä 7: M3 — Research
- [ ] Totea `ResearcherAgent`- ja `TechnologyResearcherAgent`-luokat
- [ ] Lisää kyky analysoida projektin tiedostoja ja rakenteen
- [ ] Kirjoita testit (`tests/test_research_agents.py`)

## Tehtävä 8: M4 — Development
- [ ] Totea `DeveloperAgent` ja sen sora (`agents/developer.py`)
- [ ] Lisää `RefactoringAgent`- ja `CodeReviewAgent`-luokat
- [ ] Kirjoita testit (`tests/test_developer_agent.py`)

## Tehtävä 9: M5 — Testing & QA
- [ ] Totea `TestDesignerAgent`, `TesterAgent`, `QAAgent`
- [ ] Totea testien generointi ja suoritus
- [ ] Varmista 80 % koodikattavuus ensimmäisissä moduuleissa
- [ ] Kirjoita testit (`tests/test_testing_agents.py`)

## Tehtävä 10: M6 — Security
- [ ] Totea `SecurityReviewAgent`, `SASTAgent`, `DependencySecurityAgent`, `SecretsAgent`, `ContainerSecurityAgent`
- [ ] Lisää SAST-integraatio (Bandit, pip-audit)
- [ ] Kirjoita testit (`tests/test_security_agents.py`)

## Tehtävä 11: M7 — Documentation
- [ ] Totea `TechnicalWriterAgent`, `APIDocumentationAgent`, `UserDocumentationAgent`, `MkDocsAgent`
- [ ] Määritä MkDocs-generointi agentin avulla
- [ ] Lisää Architecture Sync -toiminto
- [ ] Kirjoita testit (`tests/test_documentation_agents.py`)

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
