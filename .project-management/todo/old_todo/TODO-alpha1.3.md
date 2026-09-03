# AIDE-projektin TODO-lista (Alpha 1.3)

> Tämä lista seuraa projektin edistymistä **M11** -moduulissa (Pedagogy / Oppiminen).
> **Arkistoitu.** Tämä versio on valmis. Aktiivinen versio on `TODO-alpha1.4.md` (M12 Learning & Assessment).

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

> ⚠️ **Tärkeä muistutus:** AINA ennen kuin teet jotain uutta, varmista että projektimuistisi on ajantasalla. Päivitä `.claude/memories/project-rules.md` säännöllisesti päätöksillesi.

---

## Tehtävä 11: M11 — Pedagogy  ✅ Valmis
- [x] Totea `MentorAgent`-luokka (`agents/pedagogy_agent.py`) — opettaja-agentti, joka opettaa käyttäjälle ohjelmistokehitystä
- [x] Totea `ExplainerAgent`-luokka — selittää koodin ja konseptit ymmärrettävästi
- [x] Totea `PedagogyAgent`-luokka — suunnittelee oppimisalan suunnitelmat
- [x] Totea `ContentDesignerAgent`-luokka — luo oppimismateriaalia (esim. harjoitukset, selitykset)
- [x] Lisää oppimismateriaalin generointi projekteihin
- [x] Kirjoita testit (`tests/test_pedagogy_agents.py`) — 68 testiä, kaikki läpäisevät

---

## 🎯 Alpha 1.3 valmis kun

Kaikki M11 -komponentit (Mentor, Explainer, Pedagogy, Content Designer) on toteutettu ja testattu. Testikattavuus on vähintään 80 %.

**Seuraava käynnistys Promptti (kun olet valmis M11:ään):**
```bash
# Aloita M11 Pedagogy -moduulin toteutus:
aide run "Toteuta M11 Pedagogy -moduuli: MentorAgent, ExplainerAgent, PedagogyAgent, ContentDesignerAgent. Lisää oppimismateriaalin generointi."
```

---

> **Huom:** Kun olet valmis siirtymään seuraavaan versioon, kirjoita **"Siirry Alpha 1.4"**. Jokainen moduuli saa oman versionumeronsa (Alpha 1.4 = M12, Alpha 1.5 = M13, jne.).
