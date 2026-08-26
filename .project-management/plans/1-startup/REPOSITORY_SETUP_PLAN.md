# Repository-rakenne ennen toteutusta

Tämä on "tyhjä kangas" — se määrittelee, miten `ai-dev-environment` -repositoriossa tulee olemaan järjestetyt hakemistot ja tiedostot **ennen kuin toteutus alkaa**. Tämä takaa, että jokainen moduuli (M1–M20) saa oman kaupunkilauttansa.

```
ai-dev-environment/                        ← päärepositorio
│
├── agents/                                 ← kaikki agentit (Director, Project Manager, Developer, jne.)
│   ├── director/
│   │   └── prompt.j2                       ← Jinja2-mallipohjat agentin sylissä
│   ├── project-manager/
│   └── ...
│
├── workflows/                              ← workflowt (Analyze → Plan → Implement → Test → Review → Document)
│   ├── base.yaml
│   ├── feature.yaml
│   └── ...
│
├── tools/                                  ← työkalukirjastot, joita agentit voivat kutsua
│   ├── git-tool/
│   ├── schema-validator/
│   └── ...
│
├── policies/                               ← toimintaperiaatteet (coding standards, security policies)
│
├── standards/                              ← ympäristön yleiset standardit (esim. agent-behavior.md)
│
├── templates/                              ← projektin ja dokumentaation mallipohjat
│   ├── project-plan.md
│   ├── requirements.md
│   └── ...
│
├── schemas/                                ← rakenteiset määrittelyt (JSON/YAML-skeemat agenttien outputeille)
│
├── tests/                                  ← ympäristön omat testit (agenttien ja workflowjen laatu)
│
├── knowledge/                              ← projektin ja ympäristön pitkäkestoinen tietopankki
│   ├── adr/                                ← Architecture Decision Records
│   └── ...
│
├── requirements.txt                        ← riippuvuudet (LangChain, OpenAI SDK, Pydantic, jne.)
│ ├── README.md                            ← lyhyt kuvaus
├── mkdocs.yml                              ← dokumentaatiosivuston konfiguraatio
└── .aide/                                  ← paikallinen konfiguraatiohakemisto
    └── config.yaml                         ← käyttäjäkohtaiset asetukset (AI-mallit, budjetit, työkalut)
```

# Projektitaso (RepoStageAI-esimerkkiä varten)

Jokainen projekti, jota AIDE kehittää, on itsenäinen repositorio tällä rakenteella:

```
projekti-repo/                              ← esim. repositorystage-ai
│
├── PROJECT.md                              ← projektin visio, tavoitteet, rajaukset
├── AGENTS.md                               ← projektikohtaiset agenttiohjeet
│
├── planning/                               ← suunnitelma- ja päätösdokumentit
│   ├── vision.md
│   ├── architecture.md
│   ├── roadmap.md
│   └── decisions.md                       ← ADR:t
│
├── docs/                                   ← projektin oma dokumentaatio (MkDocs)
│
├── src/                                    ← varsanaista lähdekoodi
│
└── tests/                                  ← projektin testit
```
