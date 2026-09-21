
<div style="margin-bottom:2rem;width:100%;max-width:1600px">
  <img src="assets/images/hero.jpg" alt="AI Development Environment - ympäristön yleiskuva" class="hero-image" style="width:100%;height:auto;border-radius:16px" />
</div>

# AI Development Environment - AIDE

**AIDE** (AI Development Environment) on **agenttipohjainen ohjelmistokehitysympäristö**, joka yhdistää perinteisen ohjelmistotuotannon rakenteet moderniin tekoälyavustamiseen. Se ei ole yksittäinen agentti — se on kokonainen järjestelmä, jossa eri roolit yhteistoimivat. 

Sen sijaan, että luotettaisiin tekoälyn tuottavan aina virheetöntä koodia, AIDE toimii valvojana: se ajaa agentin tekemät muutokset eristetyssä ympäristössä, suorittaa automaattiset testit ja syöttää havaitut virheet takaisin agentille korjattavaksi – kunnes lopputulos täyttää määritellyt testaus- ja validointivaatimukset.

**Tämä projekti toimii henkilökohtaisena opiskelu- ja tutkimusympäristönä.**

### AIDE ei ole valmis – enkä ole minäkään.

AIDE kasvaa sitä mukaa kuin minä opin ymmärtämään paremmin agenttipohjaista ohjelmistokehitystä, tekoälyä ja niiden ympärille rakennettavia järjestelmiä. Projektin tarkoitus ei ole osoittaa, että kaikki on jo valmista, vaan tehdä näkyväksi se, mitä tutkin, rakennan, kokeilen ja opin.

## AIDE vs. Perinteinen DevOps

<div style="margin-bottom:2rem;width:100%;max-width:1600px">
  <img src="assets/images/aida-devops.jpg" alt="AI Development Environment - ympäristön yleiskuva" class="hero-image" style="width:100%;height:auto;border-radius:16px" />
</div>
>*Kuvan AIDA-merkintä korjataan seuraavassa versiossa.*

## AIDE‑arkkitehtuuri - Kolme tasoa
<br>

<div style="margin-bottom:2rem;width:100%;max-width:1600px">
  <img src="assets/images/kolmetasoa.jpg" alt="AI Development Environment - ympäristön yleiskuva" class="hero-image" style="width:100%;height:auto;border-radius:16px" />
</div>

### Agenttikerros – Älykäs osaaminen
Tekoälyagentit muodostavat AIDE:n ylimmän tason. Ne analysoivat, suunnittelevat ja tuottavat sisältöä projektin tavoitteiden mukaisesti. Agentit ovat kontekstia ymmärtäviä ja oppivia, mutta niiden toiminta ei ole koskaan villiä — alemmat tasot pitävät ne kurissa.

### Workflow‑kerros – Orkestraatio ja prosessit
Tämä taso ohjaa koko ohjelmistokehityksen elinkaarta vaihe vaiheelta. Se varmistaa, että työ etenee järjestelmällisesti: **Analyze → Plan → Implement → Test → Review → Document**.

Workflow toimii kuin projektin liikennevalo: seuraavaan vaiheeseen ei siirrytä ennen kuin laatuportit täyttyvät.

### Deterministinen Engine – Luotettava perusta
Arkkitehtuurin alin taso on AIDE:n turvaverkko. Se ohjaa agenttien tuottamat muutokset sääntöjen, validointien, testien ja turvaskannausten läpi. Moottori varmistaa, että agentin tuottama lopputulos täyttää määritellyt turvallisuus-, validointi- ja testausvaatimukset ennen hyväksymistä.

---

## Opiskelun ja tutkimuksen neljä kohdetta

AIDE toimii käytännön laboratoriona, jossa tutkin neljää keskeistä osa‑aluetta modernissa agenttipohjaisessa ohjelmistokehityksessä:

### 1. Agenttien konteksti ja osaaminen (Älykäs osaaminen)
Tutkimusalue keskittyy tehtävien analysointiin, koodin generointiin ja ratkaisujen validointiin roolitettujen agenttien kautta.

**Kokeilut**

- **AST & Konteksti:** Vertailen eri tapoja syöttää koodikannan kontekstia agentille. Tutkin, saavutetaanko parempia tuloksia raakakoodilla vai muodostamalla koodista syntaksipuita (AST), jotka tiivistävät agentille vain olennaiset funktiorajapinnat ja tyypitykset.
- **Semanttinen haku:** Testaan RAG‑arkkitehtuureja, jotka hakevat koodista semanttisesti relevantteja osia ja tarjoavat agentille täsmällisemmän kontekstin.

**Osaamistavoitteet**

- Abstract Syntax Tree (AST) -parserointi Tree-sitter-työkalulla  
- Koodikantojen semanttinen haku  
- RAG-arkkitehtuurien hyödyntäminen agenttien kontekstin parantamisessa

---

### 2. Valvonta ja laadunvarmistus (Determinismi)
Tämä tutkimusalue keskittyy agentin toiminnan valvontaan ja koodin laadun varmistamiseen automaattisilla testeillä ja staattisella analyysilla.

**Kokeilut**

- **Self-Healing Loop:** Syötän agentille tahallaan virheellistä koodia. AIDE ajaa testit (pytest / npm test), kerää virhelokit ja välittää havaitut virheet takaisin agentille korjauskierrosta varten. Tavoitteena on toistaa sykli, kunnes määritellyt testit läpäistään (Exit Code 0).
- **Staattinen analyysi:** Testaan linttereitä, tyyppitarkistimia ja analysoin, miten agentti reagoi eri virheluokkiin.

**Osaamistavoitteet**

- Automaattiset palautekytkennät  
- Virhelokien reaaliaikainen parserointi  
- LLM-promptien dynaaminen optimointi  
- Testiautomaatio ja regressioiden tunnistus

---

### 3. Ajo, eristys ja turvallisuus (Turvallisuus & Suoritus)
Agentin tuottamaa koodia ei ajeta suoraan isäntäjärjestelmässä, vaan eristetyssä ja rajatussa ajoympäristössä.

**Kokeilut**

- **Sandbox Lab:** Tutkin eri koodausagenttien käyttäytymistä, kun suoritusympäristö lukitaan eristettyyn Docker- tai MicroVM-pohjaiseen ajoympäristöön ilman ulkoista verkkoyhteyttä (network_mode="none").

**Osaamistavoitteet**

- Konttiorkestrointi Docker/Podman SDK:lla  
- Prosessien eristys ja turvallinen suorituskonteksti  
- Resurssirajoitusten hallinta  
- Kyberturvallisuus agenttiympäristöissä

---

### 4. Rajapinnat, lokitus ja jäljitettävyys

Tämä tutkimusalue keskittyy käyttäjän syötteiden (kehotteet, koodipohjat)ja järjestelmän tuottamien tulosten hallintaan (koodimuutokset, testiraportit, lokitiedostot).

**Kokeilut**

- **Audit Trail:** Rakennan lokitusjärjestelmän, joka tallentaa jokaisen agentin toiminnon ja koodimuutoksen.
- **JSON-rajapinnat:** Testaan jäsenneltyjä rajapintoja, joilla agentit kommunikoivat workflow-kerroksen kanssa.
- **Tilannekuvan taltiointi:** Tutkin, miten koko kehitysympäristön tila voidaan tallentaa ja palauttaa.

**Osaamistavoitteet**

- Tapahtumalokituksen (audit trail) rakenne  
- Jäsennellyt JSON-rajapinnat  
- Kehitysympäristön tilannekuvan taltiointi ja rekonstruointi  
- Jäljitettävyyden ja läpinäkyvyyden varmistaminen

---