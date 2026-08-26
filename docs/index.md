# AI Development Environment (AIDE)

**Agenttipohjainen ohjelmistokehitysympäristö, joka automatisoi rutiinit ja opettaa sinua samalla.**

---

## 🔗 AI Development Environment DOC's – Käyttöohjeistus

Voit lukea tämän projektin täyden käyttöohjeistuksen ja dokumentaation osoitteessa:

👉 **[https://miporepo.github.io/ai-development-environment-doc/](https://miporepo.github.io/ai-development-environment-doc/)**

Tämä sivusto tarjoaa:
- Asennus- ja käyttöohjeet projektin käynnistykseen.
- Selitykset jokaiselle agentille ja workflowlle.
- Esimerkeja toteutuksista ja oppimispoluista.
- Tekniset speksit ja moduulikuvaukset.

---

## Mikä tämä on?

**AIDE** (AI Development Environment) on **agenttipohjainen ohjelmistokehitysympäristö**, joka yhdistää perinteisen ohjelmistotuotannon rakenteet moderniin tekoälyavustamiseen. Se ei ole yksittäinen agentti — se on kokonainen järjestelmä, jossa eri roolit (Director, Planner, Developer, Tester, Security, jne.) yhteistoimivat.

---

## Miten se toimii?

1. **Anna tehtävä:** Käytä komentoa `aide run "..."` tai `aide init`.
2. **Director toimii:** Se tulkitsee tavoitteen ja valitsee oikean workflowin.
3. **Agentit tekevät työn:** Analyysi → Suunnittelu → Toteutus → Testaus → Tarkistus → Dokumentointi.
4. **Dokumentaatio päivittyy:** Kaikki muutokset dokumentoidaan automaattisesti.

---

## Miten käytän sitä?

### 1. Asennus
```bash
git clone https://github.com/aide-env/ai-development-environment.git
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Käyttö
```bash
aide run "Lisää projektiin käyttäjätuki."
```

---

## Haluatko oppia lisää?
- [Asennus](getting-started/installation.md)
- [Agentit](agents/director.md)
- [Workflowt](workflows/base-workflow.md)
- [Arkkitehtuuri](architecture/overview.md)

---

> Tämä dokumentaatiosivusto päivittyy **automatisesti**, kun AIDE:n lähdekoodi muuttuu.
