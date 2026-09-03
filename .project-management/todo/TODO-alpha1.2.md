# AIDE-projektin TODO-lista (Alpha 1.2)

> Tämä lista seuraa projektin edistymistä **M10–M20** -moduuleissa (Laajennus & Kypsä & Integraatio & GUI).
> Kun tämä lista on valmis, siirry se `old_todo/`-kansioon ja luo uusi lista (`.project-management/todo/TODO-alpha1.3.md`) seuraaville moduuleille.

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

> ⚠️ **Tärkeä muistutus:** AINA ennen kuin teet jotain uutta, varmista että projektimuistisi on ajantasalla. Päivitä `.claude/memories/project-rules.md` säännöllisesti päätöksillesi.

Esimerkiksi, kun teet päätöksen siitä, mitä kirjastoa käytetään M10:ssa, tallenna se heti:
```markdown
# project-rules.md (päivitetty)

- M10 DevOps -moduulissa käytetty CLI-kirjasto on: `Typer`.
- ...
```

---

## Tehtävä 10: M10 — DevOps  ✅ VALMIS

- [x] Totea `DockerAgent`-luokka (`agents/devops_agent.py`) — luo Dockerfile + docker-compose.yaml projekti-tyypin mukaan (python-api, web-app, cli, default)
- [x] Totea `CI_CDAgent` (luo GitHub Actions -workflowit: ci-cd, linting, security)
- [x] Totea `InfrastructureAgent`-luokka — analysoi infra-tiedostot, riippuvuudet, suositukset
- [x] Totea `DeploymentAgent`-luokka — deploy-strategiat (docker-swarm, kubernetes, aws-ecs, static)
- [x] Luo projektille `Dockerfile`-mallipohja ja `.github/workflows/` -mallit
- [x] Kirjoita testit (`tests/test_devops_agent.py`) — 63 testiä, kaikki läpäisti

## Tehtävä 11: M11 — Pedagogy  ❌ Ei aloitettu
- [ ] Totea `MentorAgent` ja `ExplainerAgent` (`agents/pedagogy_agent.py`)
- [ ] Totea `PedagogyAgent` ja `ContentDesignerAgent`
- [ ] Lisää oppimismateriaalin generointi
- [ ] Kirjoita testit (`tests/test_pedagogy_agents.py`)

## Tehtävä 12: M12 — Learning & Assessment  ❌ Ei aloitettu
- [ ] Totea `CurriculumAgent`-luokka (`agents/learning_agent.py`)
- [ ] Totea `AssessmentAgent`-luokka
- [ ] Lisää henkilökohtaisen oppimispolun luominen
- [ ] Kirjoita testit (`tests/test_learning_agents.py`)

## Tehtävä 13: M13 — Knowledge & Memory  ❌ Ei aloitettu
- [ ] Totea `ContextManagerAgent`, `KnowledgeAgent`, `MemoryManagerAgent` (`agents/knowledge_agent.py`)
- [ ] Lisää SQLite-tietokanta (`knowledge.db`) historian tallentamiseen
- [ ] Lisää projektin pitkäkestoinen konteksti ja päätösten tallennus
- [ ] Kirjoita testit (`tests/test_knowledge_agents.py`)

## Tehtävä 14: M14 — Maintenance  ❌ Ei aloitettu
- [ ] Totea `IssueTriageAgent`-luokka (`agents/maintenance_agent.py`)
- [ ] Totea `DependencyManagerAgent` ja `TechnicalDebtAgent`
- [ ] Totea `MaintenanceAgent`
- [ ] Kirjoita testit (`tests/test_maintenance_agents.py`)

## Tehtävä 15: M15 — Release & Governance  ❌ Ei aloitettu
- [ ] Totea `ReleaseManagerAgent`-luokka (`agents/release_agent.py`)
- [ ] Totea `ChangelogAgent`, `PolicyAgent`, `ComplianceAgent`
- [ ] Lisää julkaisujen ja standardien valvonnan automaatio
- [ ] Kirjoita testit (`tests/test_release_agents.py`)

## Tehtävä 16: M16 — Agent Engineering  ❌ Ei aloitettu
- [ ] Totea `AgentDesignerAgent`-luokka (`agents/agent_engineering_agent.py`)
- [ ] Totea `AgentTesterAgent`, `AgentEvaluatorAgent`, `AgentOptimizerAgent`
- [ ] Lisää agenttien suunnittelu, testaus ja benchmarkkaus
- [ ] Kirjoita testit (`tests/test_agent_engineering_agents.py`)

## Tehtävä 17: M17 — AI Gateway  ❌ Ei aloitettu
- [ ] Laaja `AIProvider`-luokkaa monimallitukseen (`tools/ai_provider.py`)
- [ ] Lisää `ModelRouter`, `ModelRegistry`, `ModelEvaluator`
- [ ] Lisää offline-fallback logiikka (Ollama)
- [ ] Kirjoita testit (`tests/test_ai_gateway.py`)

## Tehtävä 18: M18 — Local LLM  ❌ Ei aloitettu
- [ ] Lisää Ollama-integraatio (`tools/local_llm_provider.py`)
- [ ] Lisää GGUF-mallien lataus ja VRAM-hallinta
- [ ] Lisää paikallisten mallien benchmarkkaus
- [ ] Kirjoita testit (`tests/test_local_llm_provider.py`)

## Tehtävä 19: M19 — MCP & Integrations  ❌ Ei aloitettu
- [ ] Totea MCP-integraatio (`tools/mcp_client.py`)
- [ ] Lisää GitHub/GitLab API-integraatio turvallisella pääsillä
- [ ] Lisää ulkoisten työkalujen turkin käyttö agenteille
- [ ] Kirjoita testit (`tests/test_mcp_integration.py`)

## Tehtävä 20: M20 — GUI / Control Center  ❌ Ei aloitettu
- [ ] Rakenna web-pohjainen dashboard (`gui/`)
- [ ] Lisää agenttien tilan ja workflowjen visualisointi
- [ ] Lisää projektien näkymä ja reaaliaikainen seuranta
- [ ] Kirjoaa testit (`tests/test_gui.py`)

---

## 📊 Edistymistilanne yhteensä (M1–M20)

| Moduuli | Nimi | Status |
| --- | --- | --- |
| M1 | Core & Director | ✅ Valmis |
| M2 | Project Management | ✅ Valmis |
| M3 | Research | ✅ Valmis |
| M4 | Development | ✅ Valmis |
| M5 | Testing & QA | ✅ Valmis |
| M6 | Security | ✅ Valmis |
| M7 | Documentation | ✅ Valmis |
| M8 | Testing Automation | ✅ Valmis |
| M9 | Orchestration | ✅ Valmis |
| M10 | DevOps | ✅ Valmis |
| M11 | Pedagogy | ❌ Ei aloitettu |
| M12 | Learning & Assessment | ❌ Ei aloitettu |
| M13 | Knowledge & Memory | ❌ Ei aloitettu |
| M14 | Maintenance | ❌ Ei aloitettu |
| M15 | Release & Governance | ❌ Ei aloitettu |
| M16 | Agent Engineering | ❌ Ei aloitettu |
| M17 | AI Gateway | ❌ Ei aloitettu |
| M18 | Local LLM | ❌ Ei aloitettu |
| M19 | MCP & Integrations | ❌ Ei aloitettu |
| M20 | GUI / Control Center | ❌ Ei aloitettu |

---

## 🎯 Alpha 1.2 valmis kun

Kaikki M10–M20 -moduulit on toteutettu ja testattu. Proktin edistymisen voi jälkeen seurata taulukon avulla.

**Seuraava käynnistys Promptti (kun olet valmis M10:ään):**
```bash
# Aloita M10 DevOps -moduulin toteutus:
aide run "Toteuta M10 DevOps -moduuli: Docker, CI/CD, Infrastructure ja Deployment -agentit. Luo GitHub Actions -workflow projekteille."
```

---

> **Huom:** Kun olet valmis siirtymään seuraavaan versioon, kirjoita **"Siirry Alpha 1.3"**. Jokainen moduuli saa oman versionumeronsa (Alpha 1.3 = M11, Alpha 1.4 = M12, jne.).
