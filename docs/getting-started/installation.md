# Asennus

Tämä opas kertoo, miten asennat AI Development Environmentin (AIDE) paikalliseen kehitysympäristöösi.

---

## 1. Edellytykset

- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **Git** — [git-scm.com](https://git-scm.com/)

---

## 2. Asennus vaiheittain

### Vaihe 1: Kloonaa repositorio

```bash
git clone https://github.com/aide-env/ai-development-environment.git
cd ai-development-environment
```

### Vaihe 2: Luo virtuauliympäristö

```bash
python -m venv .venv
```

Aktivoi se:

```bash
# Linux/macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### Vaihe 3: Asenna riippuvuudet

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Testaa asennus

Ongelmatilanteiden välttämiseksi, varmista että kaikki riippuvuudet ovat oikeissa versioissa.

```bash
# Tarkistaa MkDocs-version
mkdocs --version

# Aja testit (tulisi näyttää 80 % kattavuuden läpi)
pytest tests/ --cov=agents --cov-fail-under=80
```

---

## 4. Seuraavat askeleet

Kun asennus on valmis, siirry [ensimmäisen projektin luomiseen](first-project.md).
