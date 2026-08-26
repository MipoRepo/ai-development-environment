# Director-agentti

**Vastuu:** Koko järjestelmän orkestrointi. Tulkitsee käyttäjän tavoitteen → valitsee oikean workflowin → ohjaa agentteja sen läpi.

## Toiminnallisuudet
- Tehtaan luokkaus (YAML/JSON-muoto)
- Workflowin valinta (`feature`, `bugfix`, `security-review`, jne.)
- Agenttien orkestointi
- Virheiden ja kyselyiden hallinta

## CLI-esimerkki
```bash
aide run "Lisää projektiin käyttäjätason roolit."
```
Director tunnistaa tämän `feature`-tyyppiseksi ja käynnistää sen.
