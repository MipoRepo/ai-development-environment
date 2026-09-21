# AIDE (AI Development Environment) – Tulevaisuuden arkkitehtuuri & liiketoimintapositio

## Strateginen Deep Tech & Agentic RaaS -infrastruktuuridokumentti

Tämä dokumentti määrittelee teknisen arkkitehtuurin, keskeiset teknologiapilarit ja markkinaposition AIDE (AI Development Environment) -ympäristölle. AIDE siirtää tekoälyavusteisen ohjelmistotuotannon probabilistisesta (arvailevasta) deterministiseen (varmistettuun) malliin. Se toimii eristettynä ohjausraamina, suoritusympäristönä ja laadunvalvontmoottorina autonomisille koodausagentille (kuten Claude Code).

---

## 1. Markkinapositio ja arkkitehtuurinen erottautuminen

Perinteiset ohjelmistokehitystyökalut keskittyvät koodin tuottamiseen. Autonomisten agenttien aikakaudella koodin tuottaminen on jo ratkaistu ongelma. Todellinen pullonkaula on koodin todentaminen, determinismi ja turvallisuus.

Claude Code ja muut kaupalliset LLM-agentit ovat probabilistisia työkaluja – ne voivat hallusinoida, rikkoa riippuvuuksia ja ohittaa yritysten tietoturvastandardit. AIDE ei kilpaile tekoälymallin älykkyyden kanssa; sen sijaan se hallitsee suoritusympäristöä ja pakottaa säännöt.

### Markkinan vertailuanalyysi

| Metriikka | Perinteinen IT-konsultointi | SaaS-malli (Cursor, Copilot Workspace) | AIDE Agentic RaaS -malli |
| :--- | :--- | :--- | :--- |
| **Laskutusperuste** | Tehdyt työtunnit (Time & Material) | Kiinteä kuukausittainen lisenssi | Validoidut kooditason lopputulokset |
| **Asiakkaan riski** | Korkea (Tunnit juoksevat, tulos epävarma) | Keskisuuri (Ohjelmisto voi jäädä käyttämättä) | **Nolla** (Asiakas maksaa vain toimivasta koodista) |
| **Skaalautuvuus** | Lineaarinen (Vaatii uuden ihmisen palkkaamista) | Korkea | **Eksponentiaalinen** (Tekoälyvipu + automaatio) |
| **Laadunvarmistus** | Manuaalinen koodikatselmointi (PR-review) | Täysin riippuvainen ihmiskäyttäjän taidosta | **Automatisoitu hiekkalaatikkovalidointi** |

---

## 2. AIDE-ympäristön viisi keskeisintä teknologiapilaria

Jotta autonomisia koodausagentteja voidaan tehokkaasti eristää, ohjata ja validoida, AIDE-infrastruktuurin on sisällytettävä natiivisti seuraavat viisi teknistä pilaria:

### 1. Eristetty ja dynaaminen suoritusympäristö (Sandboxing)

Agenttien ei voida antaa ajaa koodia suoraan isäntäpalvelimella tai kehittäjän omalla käyttöjärjestelmällä. AIDE orkestroi dynaamisia, turvallisia ja resurssirajoitettuja hiekkalaatikoita.

*   **Teknologiat:** Docker, Podman tai MicroVM-teknologiat (kuten Firecracker).
*   **Toteutus:** AIDE käyttää rajapintoja pystyttääkseen puhtaan, eristetyn kontin aina, kun agentti aloittaa tehtävän. Konttiin on esiasennettu tarvittavat SDK-työkalut, mutta se on eristetty ulkoisesta verkosta (`network_mode="none"`). Tämä estää datan vuotamisen tai haitallisten skriptien lataamisen.

### 2. Projektin tilan ja kontekstin hallinta (State-as-Code)

LLM-agentit epäonnisuvat, kun ne kadottavat laajan koodikannan kontekstin tai ylittävät token-rajat. AIDE toimii älykkäänä kontekstin kuraattorina.

*   **Teknologiat:** Tree-sitter (Abstract Syntax Tree -jäsentämiseen), RAG (Retrieval-Augmented Generation) ja Vektoritietokannat (esim. Qdrant, ChromaDB).
*   **Toteutus:** Indiksointimoduuli parseroi koodikannan rakenteen. Kun agentti pyytää projektin kontekstia, AIDE suorittaa semanttisen ja syntaksitietoisen haun syöttääkseen agentille tarkasti vain ne funktiorajapinnat, riippuvuuspuut ja tiedostot, joita kyseisen tehtävän suorittamiseen tarvitaan.

### 3. Deterministiset itsestäänkorjaavat silmukat (Self-Healing Loops)

Tämä on Results-as-a-Service (RaaS) -mallin ydintoiminto. Kun agentti muokkaa koodia, AIDE validoi lopputuloksen automaattisesti ja empiirisesti ilman ihmisen väliintuloa.

*   **Teknologiat:** Linterit (ESLint, Ruff), staattiset tyypintarkastajat (TypeScript, MyPy) ja testauskehykset (Jest, PyTest).
*   **Toteutus:** AIDE-orkestraattori ajaa testit eristetyn kontin sisällä heti, kun agentti ilmoittaa tehtävän valmistuneen. Se lukee exit-koodit ja stderr-virhevirran. Jos validointi epäonnistuu, AIDE parseroi lokit strukturoiduksi promptiksi ja pakottaa agentin takaisin korjaussilmukkaan, kunnes puhdas exit-koodi (`0`) saavutetaan.

### 4. Pääsynhallinta, tietoturva ja LLM-suojakaiteet (Guardrails)

Yritysvalmiuden takaamiseksi AIDE valvoo ja estää taustalla olevan mallin yrittämät vaaralliset tai luvattomat toiminnot.

*   **Teknologiat:** LlamaGuard, Guardrails AI tai NeMo Guardrails.
*   **Toteutus:** Tietoturvaproxy istuu agentin aikeiden ja suorituskerroksen välissä. Jos agentti yrittää tuhoisaa komentoa (kuten luvatonta tietokannan tyhjennystä tai suojausasetusten muuttamista), AIDE estää suorituksen deterministisesti ja ilmoittaa agentille sääntörikkomuksesta.

### 5. Tapahtumapohjainen RaaS-mittaus ja laskutusintegraatio

Koska liiketoimintamalli perustuu siihen, että asiakasta laskutetaan vain varmistetuista tuloksista, AIDE sisältää mittausjärjestelmän, joka kirjaa onnistuneet suoritustilat laskutuksen varmistamiseksi.

*   **Teknologiat:** OpenTelemetry, Prometheus ja käyttöpohjaiset laskutustyökalut (esim. Lago, Togai).
*   **Toteutus:** Kun validointiputki vahvistaa, että koodi läpäisee kaikki testit ja semanttiset tarkistukset, järjestelmä lähettää kryptografisesti allekirjoitetun laskutustapahtuman (*Billing Event*). Tämä arkkitehtuuri takaa läpinäkyvän auditointijäljen tulosperusteiselle kaupallistamiselle.

---

## 3. Tekninen toteutusesimerkki (Python + Docker)

Seuraava tuotantovalmis Python-toteutus käyttää virallista `docker`-SDK:ta demonstroidakseen AIDE-validointimoottoria ja sen automaattista itsestäänkorjaavaa silmukkaa (Self-Healing Loop).

```python
import docker
import os
import sys

class AIDESandbox:
    def __init__(self, project_path: str, image_name: str = "python:3.11-slim"):
        """
        Alustaa deterministisen AIDE-suoritusympäristön.
        """
        self.client = docker.from_env()
        self.project_path = os.path.abspath(project_path)
        self.image_name = image_name

    def run_validation(self, test_command: str = "pytest") -> dict:
        """
        Pystyttää eristetyn ja väliaikaisen Docker-kontin, ajaa testit 
        ja palauttaa deterministiset suorituslokit sekä exit-koodit.
        """
        print(f"[AIDE] Käynnistetään eristetty hiekkalaatikko imagella: {self.image_name}...")
        
        # Montteerataan asiakkaan koodikansio kontin sisäiseen työtilaan
        volumes = {
            self.project_path: {
                'bind': '/app',
                'mode': 'rw'  # Lukuoikeus ja kirjoitusoikeus kontin sisällä testiajoa varten
            }
        }
        
        try:
            # Suoritetaan validointikomennot suojatussa hiekkalaatikossa.
            # network_mode="none" takaa, ettei dataa voida vuotaa ulkoverkkoon ajon aikana.
            container = self.client.containers.run(
                image=self.image_name,
                command=f"sh -c 'pip install pytest && cd /app && {test_command}'",
                volumes=volumes,
                working_dir="/app",
                network_mode="none", 
                detach=True
            )
            
            # Asetetaan tiukka 30 sekunnin aikaraja, jotta agentti ei jää ikuiseen silmukkaan tai jumiin
            result = container.wait(timeout=30)
            exit_code = result["StatusCode"]
            
            # Kerätään kaikki lokitiedot (STDOUT & STDERR)
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")
            
            # Varmistetaan ympäristön puhtaus tuhoamalla kontti välittömästi suorituksen jälkeen
            container.remove() 
            
            if exit_code == 0:
                return {
                    "success": True,
                    "message": "Deterministinen validointi onnistui. Koodi täyttää kaikki vaatimukset.",
                    "logs": logs
                }
            else:
                return {
                    "success": False,
                    "message": "Validointi epäonnistui. Suoritusympäristö palautti virheitä.",
                    "logs": logs
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Kriittinen AIDE-ympäristövirhe: {str(e)}",
                "logs": ""
            }

# --- KONKREETTINEN AUTOMAATTINEN RAAS-ORKESTROINTIPUTKI ---
if __name__ == "__main__":
    # Kohdekansio, jota tekoälyagentti (esim. Claude Code) on muokannut
    TARGET_WORKSPACE = "./my_project"
    
    # Alustetaan AIDE-orkestraattori
    sandbox = AIDESandbox(project_path=TARGET_WORKSPACE)
    
    # Suoritetaan validointi deterministisesti
    validation_result = sandbox.run_validation(test_command="pytest test_auth.py")
    
    if not validation_result["success"]:
        print("[AIDE] Virhe havaittu agentin tuottamassa lähdekoodissa.")
        
        # Korjattu merkkijonorakenne ilman Markdownia sekoittavia sisäisiä kolmois-lainausmerkkejä
        agent_feedback_prompt = (
            "[AIDE VALIDATION CRITICAL FAILURE]\n"
            f"Suoritusympäristö hylkäsi tekemäsi koodimuutoksen.\n"
            f"Tila: {validation_result['message']}\n\n"
            "Deterministiset suorituslokit:\n"
            "----------------------------------------------------------------------\n"
            f"{validation_result['logs']}\n"
            "----------------------------------------------------------------------\n\n"
            "Ohje: Analyze the execution failure logs. Refactor the implementation\n"
            "and resolve all failing assertions. You will remain locked in this loop until\n"
            "the environment returns Exit Code 0."
        )
        print("\nAgentille generoitu korjausprompti:\n", agent_feedback_prompt)
    else:
        print("[AIDE] Validointi meni läpi. Käynnistetään tapahtumapohjainen RaaS-laskutustapahtuma.")
```

---

## 4. Liiketoimintapositio ja arvolupaus

AIDE-infrastruktuurin hyödyntäminen muuttaa perinteisen ohjelmistokehityksen tekoälyinfrastruktuurin hallinnaksi ja tekoälyauditoinniksi (AI Infrastructure Engineering & AI Auditing).

> "Autonomisten agenttien, kuten Claude Coden, käyttö nopeuttaa ohjelmistokehitystä, mutta altistaa järjestelmät hallusinaatioille, arkkitehtuurin rappeutumiselle ja tietoturvariskeille. AIDE tarjoaa deterministisen infrastruktuuriraamin, joka ottaa tekoälyagentit tiukkaan hallintaan. Se sulkee ne eristettyyn hiekkalaatikkoon, korjaa suoritusvirheet automaattisesti ilman ihmistä ja varmistaa, että tuotantoympäristöihin päätyy ainoastaan 100-prosenttisesti validoitua, virheetöntä koodia."