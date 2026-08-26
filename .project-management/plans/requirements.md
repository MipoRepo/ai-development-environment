# Vaatimussuunnitelma (Requirements Specification)
> Tämä dokumentti määrittelee AIDE:n toiminnalliset ja ei-toiminnalliset vaatimukset.

---

## 1. Toiminnalliset vaatimukset (Functional Requirements)

| Vaatimus ID | Kuvaus |
| --- | --- |
| REQ-001 | AIDE vastaanottaa tehtävät luonnollisesta kielestä (`aide run "..."`). |
| REQ-002 | Director valitsee oikean workflowin tehtävän perusteella. |
| REQ-003 | Jokainen agentti tuottaa Pydantic-validoidun outputin. |
| REQ-004 | Workflowt etenee `Analyze → Plan → Implement → Test → Review → Document` -järjestyksessä. |
| REQ-005 | AIDE pystyy luomaan uusia projekteja (`aide init`). |
| REQ-006 | AIDE pystyy synkronoimaan projektitiedostot (Git). |
| REQ-007 | Turvallisuustarkastus (M6) integroi SAST- ja riippuvuustarkastuksia. |
| REQ-008 | Dokumentaatio (M7) päivittyy automaattisesti koodimuutosskenin yhteydessä. |
| REQ-009 | API-kutsujen optimointi (tokenit, caching) on toteutettu. |
| REQ-010 | AIDE pystyy käyttämään paikallisia LLM-malleja (M18). |

---

## 2. Ei-toiminnalliset vaatimukset (Non-Functional Requirements)

| Vaatimus ID | Kuvaus | Tavoite |
| --- | --- | --- |
| NFR-001 | Suoritusaika | Yksi workflow-vaihe ≤ 30 sekuntia. |
| NFR-002 | Skaalautuvuus | Järjestelmä tukee 100 samanaikaista projektia. |
| NFR-003 | Saatavuus | 99.9 % (CLI-käynnistys). |
| NFR-004 | Turvallisuus | GDPR- ja EU AI Act -yhteensopivuus. |
| NFR-005 | Ylläpidettävyys | 80 % koodikattavuus testeillä. |
| NFR-006 | API-budjetti | Työskentely onnistuu jopa 1 000 kutsulla/päivä. |
| NFR-007 | Dokumentaatio | Kaikki muutokset dokumentoidaan automaattisesti. |

---

## 3. Hyväksymiskriteerit (Acceptance Criteria)

- CLI-komennot (`aide run`, `aide init`) toimivat ilman virheitä.
- Jokainen workflow tuottaa validoidun JSON-outputin seuraavalle vaiheelle.
- Testikattavuus on vähintään 80 % kaikissa moduuleissa (M1–M20).
- Turvallisuustarkastukset eivät salli API-avaimia koodiin.
- Dokumentaatio päivittyy `Architecture Sync` -workflowin yhteydessä.

---

## 4. Rajaukset (Constraints)

- Käytetään ainoastaan avoimen lähdekoodin kirjastoja.
- API-kutsut kohdistyvät OpenRouteriin (alkuperäinen) ja paikallisiin malleihin (myöhemmin).
- Käytettävä kieli on Python ≥ 3.11.
- Graafinen käyttöliittymä (M20) toteutetaan vasta beta-vaiheessa.
