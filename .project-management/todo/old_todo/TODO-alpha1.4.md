# AIDE-projektin TODO-lista (Alpha 1.4)

> Tämä lista seuraa projektin edistymistä **M12** -moduulissa (Learning & Assessment / Oppiminen ja arviointi).
> **Arkistoitu.** Tämä versio on valmis. Aktiivinen versio on `TODO-alpha1.5.md` (M13 Knowledge & Memory).

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

> ⚠️ **Tärkeä muistutus:** AINA ennen kuin teet jotain uutta, varmista että projektimuistisi on ajantasalla. Päivitä `.claude/memories/project-rules.md` säännöllisesti päätöksillesi.

---

## Tehtävä 12: M12 — Learning & Assessment  ✅ Valmis
- [x] Totea `LearningPathAgent`-luokka (`agents/learning_path_agent.py`) — suunnittelee henkilökohtaiset oppimispolut user_background, interests, prev_score ja strategy-parametrien avulla; laskee progress_percentage ja antaa next_recommendations
- [x] Totea `AssessmentAgent`-luokka — luo kyselyjä (quiz), koodihaasteita (coding_challenge), projektiarvioituksia (project_review) ja peer_reviewit; säätää vaikeutta previous_scores-pisteidem
- [x] Totea `FeedbackAgent`-luokka — antaa AST-pohjaista palautetta koodinrakennetta varten; tukee code_review, learning, style, performance-tyyppejä; laskee score 0–100 ja antaa parannusehdotukset
- [x] Lisää oppimisprosessorseuranta projekteihin (progress_percentage, next_recommendation)
- [x] Kirjoita testit (`tests/test_learning_path_agent.py`, `tests/test_assessment_agent.py`, `tests/test_feedback_agent.py`) — 57 testiä, kaikki läpäisti

---

## 🎯 Alpha 1.4 valmis kun

Kaikki M12 -komponentit (Learning Path, Assessment, Feedback) on toteutettu ja testattu. Testikattavuus on vähintään 80 %.

**Seuraava käynnistys Promptti (kun olet valmis M13:ään):**
```bash
# Aloita M13 Knowledge & Memory -moduulin toteutus:
aide run "Toteuta M13 Knowledge & Memory -moduuli: KnowledgeAgent, MemoryAgent, ContextCompilerAgent."
```

---

> **Huom:** Kun olet valmis siirtymään seuraavaan versioon, kirjoita **"Siirry Alpha 1.6"**. Jokainen moduuli saa oman versionumeronsa (Alpha 1.6 = M14, Alpha 1.7 = M15, jne.).
