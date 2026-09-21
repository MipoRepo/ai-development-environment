
<div style="margin-bottom:2rem;width:100%;max-width:1600px">
  <img src="assets/images/hero.jpg" alt="AI Development Environment - ympäristön yleiskuva" class="hero-image" style="width:100%;height:auto;border-radius:16px" />
</div>

# AI Development Environment - AIDE

**AIDE** (AI Development Environment) on **agenttipohjainen ohjelmistokehitysympäristö**, joka yhdistää perinteisen ohjelmistotuotannon rakenteet moderniin tekoälyavustamiseen. Se ei ole yksittäinen agentti — se on kokonainen järjestelmä, jossa eri roolit yhteistoimivat. 

Sen sijaan, että luotettaisiin tekoälyn tuottavan aina virheetöntä koodia, AIDE toimii valvojana: se ajaa agentin tekemät muutokset eristetyssä ympäristössä, suorittaa automaattiset testit ja syöttää havaitut virheet takaisin agentille korjattavaksi – kunnes koodi toimii varmistetusti.

Tämä projekti toimii henkilökohtaisena opiskelu- ja tutkimusympäristönä.

## AIDA‑arkkitehtuuri - Kolme tasoa
<br>

<div style="margin-bottom:2rem;width:100%;max-width:1600px">
  <img src="assets/images/kolmetasoa.jpg" alt="AI Development Environment - ympäristön yleiskuva" class="hero-image" style="width:100%;height:auto;border-radius:16px" />
</div>

### Agenttikerros – Älykäs osaaminen
Tekoälyagentit muodostavat AIDA:n ylimmän tason. Ne analysoivat, suunnittelevat ja tuottavat sisältöä projektin tavoitteiden mukaisesti. Agentit ovat kontekstia ymmärtäviä ja oppivia, mutta niiden toiminta ei ole koskaan villiä — alemmat tasot pitävät ne kurissa.

### Workflow‑kerros – Orkestraatio ja prosessit
Tämä taso ohjaa koko ohjelmistokehityksen elinkaarta vaihe vaiheelta. Se varmistaa, että työ etenee järjestelmällisesti: **Analyze → Plan → Implement → Test → Review → Document**.

Workflow toimii kuin projektin liikennevalo: seuraavaan vaiheeseen ei siirrytä ennen kuin laatuportit täyttyvät.

### Deterministinen Engine – Luotettava perusta
Arkkitehtuurin alin taso on AIDA:n turvaverkko. Se pakottaa kaiken agenttien tuottaman materiaalin sääntöjen, validointien, testien ja turvaskannausten läpi. Moottori takaa, että samasta syötteestä syntyy aina sama, turvallinen ja ennustettava lopputulos — ilman hallusinaatioita, hyppyjä prosessissa tai tietoturvariskejä.

## Opiskelun ja tutkimuksen neljä kohdetta

AIDE toimii käytännön laboratoriona, jossa tutkin neljää keskeistä osa‑aluetta modernissa agenttipohjaisessa ohjelmistokehityksessä:

### 1. Agenttikerros (Älykäs osaaminen)
Kerros vastaa tehtävien analysoinnista, koodin generoinnista ja ratkaisujen validoinnista roolitettujen agenttien kautta.

**Kokeilut**

- **AST & Konteksti:** Vertailen eri tapoja syöttää koodikannan kontekstia agentille. Tutkin, saavutetaanko parempia tuloksia raakakoodilla vai muodostamalla koodista syntaksipuita (AST), jotka tiivistävät agentille vain olennaiset funktiorajapinnat ja tyypitykset.
- **Semanttinen haku:** Testaan RAG‑arkkitehtuureja, jotka hakevat koodista semanttisesti relevantteja osia ja tarjoavat agentille täsmällisemmän kontekstin.

**Osaamistavoitteet**

- Abstract Syntax Tree (AST) -parserointi Tree-sitter-työkalulla  
- Koodikantojen semanttinen haku  
- RAG-arkkitehtuurien hyödyntäminen agenttien kontekstin parantamisessa

---

### 2. Valvonta- ja laadunvarmistuskerros (Determinismi)
Tämä kerros valvoo agentin toimintaa ja varmistaa koodin laadun automaattisilla testeillä ja staattisella analyysilla.

**Kokeilut**

- **Self-Healing Loop:** Syötän agentille tahallaan virheellistä koodia.  
  AIDE ajaa testit (pytest / npm test), kerää virhelokit ja pakottaa agentin automaattiseen korjaussilmukkaan, kunnes koodi läpäisee testit (Exit Code 0).
- **Staattinen analyysi:** Testaan linttereitä, tyyppitarkistimia ja analysoin, miten agentti reagoi eri virheluokkiin.

**Osaamistavoitteet**

- Automaattiset palautekytkennät  
- Virhelokien reaaliaikainen parserointi  
- LLM-promptien dynaaminen optimointi lennosta  
- Testiautomaatio ja regressioiden tunnistus

---

### 3. Ajo- ja eristyskerros (Turvallisuus & Suoritus)
Agentin tuottamaa koodia ei koskaan ajeta suoraan isäntäjärjestelmässä, vaan aina täysin eristetyssä ajoympäristössä.

**Kokeilut**

- **Sandbox Lab:** Tutkin eri koodausagenttien (Claude Code, AutoGPT, Devika) käyttäytymistä, kun suoritusympäristö lukitaan täysin eristettyyn Docker- tai MicroVM-konttiin ilman ulkoista verkoyhteyttä (network_mode="none").
- **Resurssirajoitukset:** Testaan CPU-, muisti- ja I/O-rajoituksia ja tarkkailen, miten agentin tuottama koodi käyttäytyy niissä.

**Osaamistavoitteet**

- Konttiorkestrointi Docker/Podman SDK:lla  
- Prosessien eristys ja turvallinen suorituskonteksti  
- Resurssirajoitusten hallinta  
- Kyberturvallisuus agenttiympäristöissä

---

### 4. Syöte- ja tuloskerros (Rajapinnat & Lokitus)
Kerros hallinnoi käyttäjän syötteitä (kehotteet, koodipohjat) ja järjestelmän tuottamia tuloksia (koodimuutokset, testiraportit, lokitiedostot).

**Kokeilut**

- **Audit Trail:** Rakennan lokitusjärjestelmän, joka tallentaa jokaisen agentin toiminnon ja koodimuutoksen.
- **JSON-rajapinnat:** Testaan jäsenneltyjä rajapintoja, joilla agentit kommunikoivat workflow-kerroksen kanssa.
- **Tilannekuvan taltiointi:** Tutkin, miten koko kehitysympäristön tila voidaan tallentaa ja palauttaa.

**Osaamistavoitteet**

- Tapahtumalokituksen (audit trail) rakenne  
- Jäsennellyt JSON-rajapinnat  
- Kehitysympäristön tilannekuvan taltiointi ja rekonstruointi  
- Jäljitettävyyden ja läpinäkyvyyden varmistaminen

## AIDA vs. Perinteinen DevOps

<div style="margin-bottom:2rem;width:100%;max-width:1600px">
  <img src="assets/images/aida-devops.jpg" alt="AI Development Environment - ympäristön yleiskuva" class="hero-image" style="width:100%;height:auto;border-radius:16px" />
</div>

---

<img src="assets/images/logo-aide-vaalea-transparent.png" width="45px"> 
