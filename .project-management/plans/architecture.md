# Arkkitehtuurisuunnitelma (Architecture Plan)

## 1. Komponentit

| Komponentti | Kuvaus | Moduuli |
| --- | --- | --- |
| Director Agent | Orkestroi agenttijärjestöä ja workflowja | M1 |
| BaseAgent | Pydantic-pohjainen agenttien ydinluokka | M1 |
| Workflow Engine | YAML-pohjaiset workflowt ja tilanhallinta | M1 |
| AI Provider | yhteys OpenRouteriin ja paikallisiin malleihin | M17, M18 |
| Project Manager | Hallinnoi projekteja, backlogia ja milestoneja | M2 |
| Developer | Koodin generointi, refaktointi | M4 |
| Tester & QA | Testien luonti ja suoritus | M5 |
| Security | SAST, riippuvuustarkistus, turvallisuusrutiinit | M6 |
| Documentation | MkDocs-generointi ja dokumentaation synkkaus | M7 |
| GUI Agent Control Center | Web-pohjainen dashboard | M20 |

## 2. Rajapinnat (Interfaces)

- `AgentInterface`: `input_schema`, `run()`, `output_schema`
- `ToolInterface`: `execute()`, `validate_input()`, `format_output()`
- `WorkflowInterface`: `start()`, `pause()`, `resume()`, `get_state()`

## 3. Tietovirrat (Data Flows)

1. Käyttäjä → Director (tehtävä)
2. Director → Workflow Engine (valittu workflow)
3. Workflow Engine → Agentit (vaiheittain)
4. Agentit → Tools (toimenpiteet)
5. Agentit → Output Validator (validointi)
6. Output Validator → Seuraava vaihe / Director
7. Director → Documentation Agent (päivitys)

## 4. Teknologiapäätökset (Tech Stack)

| Kerros | Teknologia | Perustelu |
| --- | --- | --- |
| Kieli | Python 3.11+ | Tyyppituki, async/await, Laaja ekosysteemii |
| Framework | LangChain + Pydantic | Agentit, validointi |
| CLI | Typer | Nopea CLI-kehitys |
| Testaus | Pytest + Pytest-Cov | Laaja tuki ja coverage |
| Dokumentaatio | MkDocs Material | Selkeä ja käytettävä |
| CI/CD | GitHub Actions | Integroitu GitHubiin |
| Tietokanta | SQLite (myöhemmin PostgreSQL) | Projektin historia ja konteksti |
| Paikalliset LLM:t | Ollama + GGUF | Offline-tuki |
| API-aineisto | OpenRouter | Monipuoliset mallit |

## 5. Turvallisuusmalli (Security Model)

- Salaisuudet eivät koskaan pysy koodissa → `.env`-tiedosto + GitHub Secrets.
- SAST tarkistukset ajetaan CI:ssä ennen mergeä.
- API-avaimet ovat ainoastaan `AIProvider`-luokan käytettävissä.
- Paikalliset LLM:t eivät lähetä dataa ulkopuolisille palvelimille.
