# AssessmentAgent (M12 Learning & Assessment)

**Tiedosto:** `agents/learning_path_agent.py`  
**Moduuli:** M12 — Learning & Assessment  
**Status:** ✅ Valmiina  
**Testit:** 57 (yhteinen M12) | **Kattavuus:** Kaikki läpäisti

---

## Tarkoitus

Luo kyselyitä (quiz), koodihaasteita (coding_challenge) ja projektiareioita (project_review) sekä peer_reviewit. Säätää vaikeus tasolla `previous_scores`-pisteiden perusteella.

## Agentin tiedot

| Kenttä | Arvo |
|---|---|
| `agent_type` | `"assessment"` |

---

## Syöte (AssessmentInput)

| Kenttä | Tyyppi | Pakollinen | Kuvaus |
|---|---|---|---|
| `action` | `Literal["create", "evaluate"]` | ✅ | Toiminto |
| `query` | `str` | ✅ | Aihe tai kysymys |
| `assessment_type` | `str` | ✅ | `quiz`, `coding_challenge`, `project_review` |
| `previous_scores` | `list[float]` | ❌ | Aikaisemmat pisteet (vaikeuksan säädöntiin) |
| `difficulty` | `str` | ❌ | `easy`, `medium`, `hard` (ohittaa automaticin) |

---

## Tuloste (AssessmentOutput)

| Kenttä | Tyyppi | Kuvaus |
|---|---|---|
| `success` | `bool` | Onnistuminen |
| `items` | `list[dict[str, Any]]` | Luodut kyselyt/haasteet |
| `assessment_type` | `str` | Tyyppi |
| `difficulty` | `str` | Määritelty vaikeus |
| `score` | `float` | Annetun vastauksen pisteet (evaluate-toiminto) |
| `feedback` | `str` | Palaute |

---

## Esimerikkoodi

```python
from agents import AssessmentAgent

assessor = AssessmentAgent()
result = assessor.run(
    action="create",
    query="Pythonin listat ja sanakirjat",
    assessment_type="quiz",
    previous_scores=[75, 80, 85]  # Keskiverto: 80 → medium
)

print(f"Kyselyt: {len(result.items)}")
# Output: Kyselyt: 5

for item in result.items:
    print(f"  {item['question']}")
    if 'options' in item:
        print(f"  Vastaukset: {item['options']}")

# Vastauksen arviointiin
evaluation = assessor.run(
    action="evaluate",
    query="Vastaus kysymykseen 1: ['a', 'b', 'c']",
    assessment_type="quiz"
)

print(f"Pisteet: {evaluation.score}")
# Output: Kyselyt: 0.9
print(evaluation.feedback)
```

---

## Koodihaasteen generointi

```python
result = assessor.run(
    action="create",
    query="Palauta listan palindromit",
    assessment_type="coding_challenge",
    difficulty="hard"
)

for item in result.items:
    print(item['description'])
    print(f"  Rajoit: {item['constraints']}")
```

---

## ASSESSMENT_CRITERIA

| Kriteeri | Kuvaus |
|---|---|
| `accuracy` | Oikeellisuus |
| `efficiency` | Suorituskyky |
| `readability` | Luettavuus |
| `best_practices` | Parhaat käytännöt |
| `edge_cases` | reunatilanteet |

---

## Testikattavuus

M12-testit (57) sisältävät:
- `test_quiz_generation`
- `test_coding_challenge_with_constraints`
- `test_difficulty_adjustment_from_scores`
- `test_project_review_checklist`
