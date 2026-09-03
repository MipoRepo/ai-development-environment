# AIDE-projektin TODO-lista (Alpha 1.8)

> Tämä lista seuraa projektin edistymistä **M16** -moduulissa (Agent Engineering / Agtien muotoilu).
> **Aktiivinen versio.** Kun tämä lista on valmis, siirä se `old_todo/`-kansioon ja luo uusi lista (`.project-management/todo/TODO-alpha1.9.md`) seuraaville moduuleille.

---

## 📋 Claude Code -muiston käyttö tämän projektin yhteydessä

> ⚠️ **Tärkeä muistutus:** AINA ennen kuin teet jotain uutta, varmista että projektimuistisi on ajantasalla. Päivitä `.claude/memories/project-rules.md` säännöllisesti päätöksillesi.

---

## Tehtävä 16: M16 — Agent Engineering  ❌ Ei aloitettu

- [ ] Totea `AgentDesignAgent`-luokka (`agents/agent_engineering_agent.py`) — suunnittele uusia agenteja (agent_type, syöte/tuloste-skeemat, työnkuvaus)
- [ ] Totea `PromptOptimizerAgent`-luokka — paranna ja optimoi prompteja (templaatit, parametrien hienosäätö, prompt-pituus)
- [ ] Totea `AgentFactoryAgent`-luokka — luo agenteista instanssit dynamisesti (luokan generointi, rekisteröinti)
- [ ] Lisää agenttien muotoilun ja registöinnin tuki CLI:ään (`aide create-agent`, `aide optimize-prompt`)
- [ ] Kirjoita testit (`tests/test_agent_engineering_agent.py`)

---

## 🎯 Alpha 1.8 valmis kun

Kaikki M16-komponentit (AgentDesign, PromptOptimizer, AgentFactory) on toteutettu ja testattu. Testikattavuus on vähintään 80 %.

**Seuraava käynnistys (kun olet valmis M16:een):**

```bash
aide run "Toteuta M16 Agent Engineering -moduuli: AgentDesignAgent, PromptOptimizerAgent, AgentFactoryAgent."
```

---

> **Huom:** Kun olet valmis siirtymään seuraavaan versioon, kirjoita **"Siirry Alpha 1.9"**. Esim. Alpha 1.9 = M17 (AI Gateway).
