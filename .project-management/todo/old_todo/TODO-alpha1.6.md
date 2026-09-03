# AIDE-projektin TODO-lista (Alpha 1.6)

> Tämä lista seuraa projektin edistymistä **M14** -moduulissa (Maintenance / Ylläpito).
> **Arkistoitu.** Tämä versio on valmis. Aktiivinen versio on `TODO-alpha1.7.md` (M15 Release & Governance).

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

> ⚠️ **Tärkeä muistutus:** AINA ennen kuin teet jotain uutta, varmista että projektimuistisi on ajantasalla. Päivitä `.claude/memories/project-rules.md` säännöllisesti päätöksillesi.

---

## Tehtävä 14: M14 — Maintenance  ✅ Valmis
- [x] Totea `UpgradeAgent`-luokka (`agents/maintenance_agent.py`) — tarkistaa ja päivittää riippuvuudet (check, upgrade, dry_run); tukee requirements.txt ja pyproject.toml
- [x] Totea `CleanupAgent`-luokka — poistaa vanhat cachet (__pycache__, .pytest_cache, .mypy_cache), temp-tiedostot (.bak, .tmp) ja build-tulokset (dist, build, *.egg-info)
- [x] Totea `DependencyAgent`-luokka — analysoi riippuvuusriippuvuudet (requirements.txt, pyproject.toml, package.json); tarkistaa turvallisuusongelmat ja vanhentuneet paketit; rakentaa riippuvuussolmut
- [x] Lisätty tietomallit: UpgradeAgentInput/Output, CleanupAgentInput/Output, DependencyAgentInput/Output + MAINTENANCE_ACTIONS, CACHE_DIRS, DEPENDENCY_FILES -sanakirjät
- [x] Kirjoita testit (`tests/test_maintenance_agent.py`) — 46 testiä, kaikki läpäisti

---

## 🎯 Alpha 1.6 valmis kun

Kaikki M14 -komponentit (Upgrade, Cleanup, Dependency) on toteutettu ja testattu. Testikattavuus on vähintään 80 %.

**Seuraava käynnistys Promptti (kun olet valmis M15:ään):**
```bash
# Aloita M15 Release & Governance -moduulin toteutus:
aide run "Toteuta M15 Release & Governance -moduuli: ReleaseManagerAgent, ChangelogAgent, ComplianceAgent."
```

---

> **Huom:** Kun olet valmis siirtymään seuraavaan versioon, kirjoita **"Siirry Alpha 1.8"**. Jokainen moduuli saa oman versionumeronsa (Alpha 1.8 = M16, Alpha 1.9 = M17, jne.).
