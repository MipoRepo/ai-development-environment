# AI Development Environment (AIDE) 🚀

**Agenttipohjainen ohjelmistokehitysympäristö, joka automatisoi rutiinit ja opettaa sinua samalla.**

> ⚠️ **HUOM:** Tämä on **kehittelyssä oleva alusta**. Dokumentaatio ja koodi päivittyvät jatkuvasti. Katso [dokumentaatiosivusto](https://aide-env.github.io/ai-development-environment/) saadaksesi täyden kaavan.

---

## ❓ Mitä tämä on?

AIDE ei ole yksittäinen agentti. Se on **kokonainen kehitysjärjestelmä**, joka:

- **Analysoi** projektin rakenteen.
- **Suunnittelee** tehtävät ja toteutussuunnitelmat.
- **Ottaa** koodimuutoksia.
- **Testaa** ja **tarkastaa turvallisuuden**.
- **Päivittää dokumentaation** automaattisesti.
- **Opettaa** ja **kehittää itseään** ajan myötä.

Se toimii **Claude Code** + **MCP-integraation** kautta.

---

## 🚀 Miten käytän sitä?

### 1. Asennus (tulevat vaiheet)
```bash
# Kloonaa tämä repository
git clone https://github.com/aide-env/ai-development-environment.git
cd ai-development-environment

# Luo virtuaaliympäristö
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows

# Asenna riippuvuudet
pip install -r requirements.txt
```

### 2. Käyttö (CLI)
```bash
# Aloita uusi projekti
aide init --name MyProject --type python-api

# Aja tehtävä
aide run "Lisää projektiin authentication-mekaniikka."

# Jaa dokumentaation päivättäväksi
mkdocs serve
```

---

## 🏗️ Projektin rakenne

Projekti on jaettu **20 moduuliin**, jotka on järjestetty kehityksen edistymisen mukaan:

| Vaihe | Moduulit | Tavoite |
| --- | --- | --- |
| **MVP (M1–M7)** | Core, Project Management, Research, Development, Testing, Security, Documentation | Työtävä CLI-kehityssilmukka |
| **Beta (M8–M11)** | Web Design, Frontend/Backend, DevOps, Pedagogy | Käyttöliittymäkehitys |
| **Kypsä (M12–M20)** | Learning, Knowledge, Local LLM, MCP, GUI | Organisaatiotaso ja itsekehitys |

Lue lisää [moduulisuunnitelmasta](.project-management/plans/MODULE_PLAN_UPDATED.md).

---

## 📚 Dokumentaatio

Kokosa dokumentaatio löytyy `.project-management/`-kansiosta tai [tämän sivun kautta](https://aide-env.github.io/ai-development-environment/).

---

## 🙋‍♂️ Yhteydet

- **Omistaja:** [Miko](https://github.com/MipoRepo)
- **Avainsäsanat:** AI Development, Agent, DevOps, Documentation, Security
- **Lisenssi:** [MIT](LICENSE) (suunnitellaan myöhemmin)

---

> **Projekti on kehityksessä.** Kiitos bukkereista ja ehdotuksista!
