# Mikä on agentti?

Agentti on **ohjelmoima toimija**, joka vastaanottaa tehtävän, suorittaa sen ja palauttaa rakenteisen tuloksen. Jokainen agentti on erikoistunut tiettyyn rooliin (esim. Director, Developer, Tester).

## Perusrakenne

1. **Input Schema** — Määrittää, mitä agentti ottaa vastaan (JSON, YAML).
2. **Run** — Agentin päälogiikka (LangChain, LLM-kutsut, työkalut).
3. **Output Schema** — Määrittää, mitä agentti tuottaa (validoitu).

---

## Esimerkki: Director-agentti

```json
{
  "task": "Lisää projektiin authentication.",
  "project": "RepoStageAI",
  "context": "Python API"
}
```

Director valitsee oikean workflowin (`feature`) ja käynnistää sen.
