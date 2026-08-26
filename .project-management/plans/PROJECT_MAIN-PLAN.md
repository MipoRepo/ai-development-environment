# AI Development Environment (AIDE) — Pääsuunnitelma
> Tämä on **pääasiallinen suunnitelma**, joka kuvaa koko projektin alusta tuotantoon.
> Kaikki muut alisuunnitelmat ovat tästä asiakirjasta löydettävät.

---

## 1. Projektin tavoite ja visio

### Tavoite
AI Development Environment (AIDE) on agenttipohjainen ohjelmistokehitysympäristö, jonka tarkoitus on automatisoida ohjelmistokehitystyön rutiinit (koodin analyysi, testaus, turvallisuustarkastus, dokumentointi) ja tarjota järjestetty kehitysmetodi projekteille. Sen lopullinen tavoite on toimia **agenttijärjestönä**, joka pystyy kehittämään itseään ja tarjoamaan graafisen käyttöliittymän.

### Visio
AIDE on sekä **kehitystyökalu** että **oppimisympäristö**, jossa yksittäinen agentti tai kokonainen agenttijoukko voi suorittaa projektin vaiheet (Analyze → Plan → Implement → Test → Review → Document) itsenäisesti. Käyttäjä säilyttää päätösvalta.

---

## 2. Projektin laajuus (Scope)

### Sisällä (In-Scope)
- Agenttien logiikka (M1 Core & Director, M2 Project Management, M4 Development jne.)
- Workflowjen moottori ja tilakone
- OpenRouteri ja paikallisten mallien (M17, M18) integraatio
- CLI- ja myöhemmin GUI-käyttöliittymä (M20)
- Dokumentaation (MkDocs) automaatio (M7)
- Projektitason tiedostomalli (PROJECT.md, AGENTS.md)
- CI/CD-integraatio (M10)

### Ulkopuolella (Out-of-Scope)
- Itse ohjelmistotuotannon yksityiskohdat (käyttäjän projektin koodi)
- Tuotolistan ja markkinoinnin automaatio (M21/M22)
- Pilvipalveluiden (AWS/GCP) automaattinen infra-allocatio

---

## 3. Projektin vaiheistus

| Vaihe | Kuvaus | Ajanjakso | Vastuualue |
| --- | --- | --- | --- |
| **Initiation** | Projektin käynnistys, tavoitteiden määrittely | M1 | Core & Director |
| **Planning** | Työjako, riskit, aikataulu | M2 | Project Management |
| **Execution** | Moduuli- ja agenttien toteutus | M3–M11 | Kaikki moduulit |
| **Release** | MVP:n julkaisu | M1–M7 | Release, DevOps |
| **Maintenance** | Seuranta, päivitykset, itsekehitys | M12–M20 | Knowledge, Maintenance, Agent Engineering |

---

## 4. Projektin roolit

| Rooli | Vastuu |
| --- | --- |
| **Director** | Työn orkestrointi ja priorisointi |
| **Developer** | Koodin kirjoittaminen ja testaus |
| **QA Engineer** | Testien automatisointi ja laadunvalvonta |
| **Security Specialist** | Turvallisuustarkastukset ja DevSecOps |
| **Documentation Specialist** | Dokumentaation tuottaminen ja ylläpito |
| **DevOps Engineer** | CI/CD, deploy ja infra |
| **Project Manager** | Aikataulu, budjetti ja kommunikointi |

---

## 5. Dokumentaation rakenne

Kaikki projektinhallintaan liittyvät suunnitelmat sijaitsevat `.project-management/`-kansiossa:

```
.project-management/
├── plans/
│   ├── suunnitelmat/              ← Kaikki tarkat suunnitelmat (M1–M20)
│   │   ├── 1-startup/             ← Käynnistysvaihe (M1)
│   │   ├── 2-runtime/             ← Käyttöaika (M2–M5)
│   │   └── 3-extension/           ← Laajennus (M6–M11)
│   ├── suunnitelmat/              ← Yksityiskohtaiset dokumentit (requirements, architecture, jne.)
│   └── PROJECT_MAIN-PLAN.md       ← Tämä pääasiallinen suunnitelma
├── todo/
│   ├── TODO.md                   ← Aktiivinen tehtävälista
│   └── old_todo/                 ← Arkistoitu lista
└── README.md                     ← Projektinhallinnan ohjeet
```

---

## 6. Linkit kaikkiin alisuunnitelmiin

| Nimi | Tiedosto | Kuvaus |
| --- | --- | --- |
| **Pääsuunnitelma** | `PROJECT_MAIN-PLAN.md` | Tämä |
| **Vaatimussuunnitelma** | `suunnitelmat/requirements.md` | Toiminnalliset ja ei-toiminnalliset vaatimukset |
| **Arkkitehtuurisuunnitelma** | `suunnitelmat/architecture.md` | Järjestelmän komponentit ja rajapinnat |
| **Työjako (WBS)** | `suunnitelmat/work-breakdown-structure.md` | Projektin palauttaminen konkreettisiksi tehtäviksi |
| **Aikataulu** | `suunnitelmat/schedule.md` | Sprintit, milestone-t ja Gantt |
| **Resurssit** | `suunnitelmat/resources.md` | Tiimin kokoonpano ja resurssit |
| **Budjetti** | `suunnitelmat/budget.md` | Kustannusarvio |
| **Riskit** | `suunnitelmat/risk-register.md` | Riskit, todennäköisyydet, mitigointi |
| **Kommunikaatio** | `suunnitelmat/communication.md` | Kanavat ja raportointi |
| **Laatu & Testaus** | `suunnitelmat/quality-testing.md` | Testitasot ja QA-prosessi |
| **Muutoshallinta** | `suunnitelmat/change-management.md` | Muutosten hyväksyminen |
| **Julkaisu** | `suunnitelmat/release-deployment.md` | CI/CD ja julkaisuputki |
| **Ylläpito** | `suunnitelmat/maintenance-operations.md` | Monitorointi ja SLA:t |
```