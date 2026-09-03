# AIDE-projektin TODO-lista (Alpha 2.3)

> Tämä lista seuraa projektin edistymistä **M20** -moduulissa (GUI / Control Center / Käyttöliittymä).
> **Aktiivinen versio.** Kun tämä lista on valmis, siirä se `old_todo/`-kansioon ja luo uusi lista (`.project-management/todo/TODO-alpha2.4.md`).

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

> ⚠️ **Tärkeä muistutus:** AINA ennen kuin teet jotain uutta, varmista että projektimuistisi on ajantasalla. Päivitä `.claude/memories/project-rules.md` säännöllisesti päätöksillesi.

---

## Tehtävä 20: M20 — GUI / Control Center  ✅ VALMIS

- [x] Totea `ControlCenterAgent`-luokka (`agents/control_center_agent.py`) — keskitetty ohjauspaneeli agenttien ja työpöytänäytöntekijöiden välillä
- [x] Totea `DashboardAgent`-luokka — visuaaliset mittarit ja tilanseuranta
- [x] Totea `CLIOrchestrator`-luokka — CLI:n ja agenttien välinen orkestrointi
- [x] Lisää CLI-toiminnot (`aide dashboard`, `aide status`, `aide orchestrate`)
- [x] Kirjoita testit (`tests/test_control_center_agent.py`) — 58 testiä, kaikki läpäisti

---

## 🎯 Alpha 2.3 valmis kun

Kaikki M20-komponentit (ControlCenter, Dashboard, CLIOrchestrator) on toteutettu ja testattu. Testikattavuus on vähintään 80 %.

Seuraava käynnistys (kun olet valmis seuraavaan moduuliin):

```bash
aide run "Jatka seuraavalla moduulilla."
```

---

> **Huom:** Tämä on viimeinen suunniteltu moduuli (M20). Projekti on valmis kun kaikki 20 moduulia on täytetty.
