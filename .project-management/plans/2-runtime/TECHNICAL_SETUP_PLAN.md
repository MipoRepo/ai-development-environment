# Tekninen perusrakenteen suunnitelma

Tämä dokumentti määrittelee **uuden repositorin teknisen pohjan**, joka tarvitaan AIDE:n toiminnallisuuden tukea. Se kattaa ympäristön, CI/CD:n, dokumentaation, riippuvuudet ja salaisuudet.

## 1. Kehitysympäristö (venv + työkalut)

Käytämme Python 3.11+ virtuaalia ympäristöä (venv) projektin riippuvuuksiin eristämiseksi järjestelmästä.

```
ai-dev-environment/
│
├── .venv/                                ← paikallinen Python-venv (ei commitataa .gitignoreissa)
├── requirements.txt                      ← riippuvuudet (LangChain, OpenAI SDK, Pydantic, PyYAML, Jinja2, Typer, pytest)
└── pyproject.toml                        ← projektin määrittely (valinnainen moderni vaihtoehto)
```

- **Virtuaalien luominen:** `python -m venv .venv`
- **Aktivoiminen:** `source .venv/bin/activate` (Linux/macOS) tai `.venv\Scripts\activate` (Windows)
- **Asennus:** `pip install -r requirements.txt`
- **Tyytyväisyys tarkistus:** `pip freeze > requirements-lock.txt` (versioiden lukon asettaminen tuotantokäytössä)

## 2. CI/CD -pipeline (GitHub Actions)

GitHub Actions määrittelee automaattisen testaustoiminnon jokaisessa commitissa ja branchissä.

### Tiedosto: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install -r requirements.txt
          pip install -e .  # jos projekti on asennuskelpoinen

      - name: Run unit tests
        run: |
          source .venv/bin/activate
          pytest tests/ --cov=agents --cov-report=xml --cov-fail-under=80

      - name: Upload coverage report
        uses: codecov/codecov-action@v4
```

## 3. Salaisuudet (.env ja GitHub Secrets)

Salaisuudet eivät koskaan pääse käsiksi versionhallintoon. Käytetään `.env`-tiedostoa paikallisessa kehittämisessä ja **GitHub Secrets**-ominaisuutta CI:ssä.

### Tiedosto: `.env` (ei commitata)

```env
OPENROUTER_API_KEY=sk-or-v1-...
GITHUB_TOKEN=ghp_...
DATABASE_URL=postgresql://...
```

### .gitignore -päivitys

```
.env
.venv/
__pycache__/
*.pyc
.knowledge.db
```

### GitHub Secrets (asetetaan manuaalisesti repo-asetuksissa)

- `OPENROUTER_API_KEY` – AIDE:n pääsymyöntö OpenRouteriin.
- `GITHUB_TOKEN` – GitToimintojen (push, pull request) toteuttamiseksi.

## 4. Dokumentaatio (MkDocs)

MkDocs Material -teemalla luodaan projektin dokumentaatiosivusto. Dokumentaatio syntyy automaattisesti agenteista ja workflowistä.

### Tiedosto: `mkdocs.yml`

```yaml
site_name: AI Development Environment
repo_url: https://github.com/aide-env/ai-development-environment
docs_dir: docs
site_dir: site

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: blue

nav:
  - Home: index.md
  - Getting Started:
      - Installation: getting-started/installation.md
      - First Project: getting-started/first-project.md
  - Agents:
      - Director: agents/director.md
      - Project Manager: agents/project-manager.md
  - Architecture:
      - Overview: architecture/overview.md
      - Agent Layer: architecture/agent-layer.md

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          setup_options:
            docstring_style: google
```

## 5. requirements.txt -riippuvuudet

```
langchain>=0.2.0
openai>=1.0.0
pydantic>=2.0.0
pyyaml>=6.0
jinja2>=3.1.0
typer>=0.9.0
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
requests>=2.31.0
aiohttp>=3.9.0
```

## 6. Lisäsuunnitelma: Mitä tarvitaan teknisesti toimimiseen?

### Riippuvuudet
- **LangChain:** Agenttien logiikan orkestrointiin ja prompttien hallintaan.
- **OpenAI SDK:** OpenRouterin kautta tapahtuvan LLM-kommunikaation toteuttamiseen.
- **Pydantic:** Agenttien outputin validointiin (tyypit, rajoitteet).
- **PyYAML:** Projektin (PROJECT.md, AGENTS.md) ja workflowjen konfiguraation lukemiseen.
- **Jinja2:** Prompt-mallien (prompt.j2) dynaamiseen renderöintiin.
- **Typer:** CLI-komennon ("aide init", "aide run feature") luomiseen.
- **Pytest:** Kaikkien agenttien ja workflowjen automaattiseen testaukseen.

### Tiedonhallinta
- **SQLite (.knowledge.db):** Projektin historian, päätösten ja historian tallentamiseen paikallisesti. Tämä toimii M13 Knowledge & Memory -moduulin "pitkäkestoinen tietopankki". Ei tarvitse tätä heti, mutta tulee myöhemmin.

### Suoritusympäristö
- **Python 3.11+:** Kaikki uudet ominaisuudet (tyypitys, async/await) vaativat tämän version.
- **Git:** AIDE tukee Git-toimia (checkout, branch, push) kaikissa workflowissa.

Tämä teknisuunnitelma tarjoaa kiinnitetyn perustan, johon jokainen moduuli (M1–M20) voidaan liittää jälkeen. Se on nyt valmis toteutuksen alkuun.
