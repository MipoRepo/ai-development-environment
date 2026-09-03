# AIDE-projektin TODO-lista (Alpha 1.7)

> Tämä lista seuraa projektin edistymistä **M15** -moduulissa (Release & Governance / Julkaisu ja hallinta).
> **Arkistoitu.** Tämä versio on valmis. Aktiivinen versio on `TODO-alpha1.8.md` (M16 — Agent Engineering).

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

> ⚠️ **Tärkeä muistutus:** AINA ennen kuin teet jotain uutta, varmista että projektimuistisi on ajantasalla. Päivitä `.claude/memories/project-rules.md` säännöllisesti päätöksillesi.

---

## Tehtävä 15: M15 — Release & Governance  ✅ Valmis

- [x] Totea `ReleaseManagerAgent`-luokka (`agents/release_agent.py`) — versiointi, julkaisuvaiheet ja deploy-valmiudet
- [x] Totea `ChangelogAgent`-luokka — automaattinen changelog-generointi muutoksista
- [x] Totea `ComplianceAgent`-luokka — lisenssi- ja standardintutkimus (MIT, Apache, GDPR, PCI)
- [x] Lisätty ReleaseManagerInput/Output, ChangelogInput/Output, ComplianceInput/Output -mallit
- [x] Lisätty RELEASE_PHASES, DEPLOYMENT_STRATEGIES, LICENSE_TYPES, REGULATORY_STANDARDS -sanakirjät
- [x] Päivitetty `agents/__init__.py` M15-viehimmalla
- [x] Kirjoita testit (`tests/test_release_agent.py`) — 60 testiä, kaikki läpäisti, 88 % kattavuus

---

## 🎯 Alpha 1.7 valmis

Kaikki M15-komponentit (ReleaseManagerAgent, ChangelogAgent, ComplianceAgent) on toteutettu ja testattu. Testikattavuus on 88 % (yli vaatimuksen 80 %).

**Seuraava käynnistys (kun olet valmis M16:een):**

```bash
aide run "Toteuta M16 Agent Engineering -moduuli: AgentDesignAgent, PromptOptimizerAgent, AgentFactoryAgent."
```

---

---

> **Huom:** Kun olet valmis siirtymään seuraavaan versioon, kirjoita **"Siirry Alpha 1.8"**. Jokainen moduuli saa oman versionumeronsa (Alpha 1.8 = M16, Alpha 1.9 = M17, jne.).
