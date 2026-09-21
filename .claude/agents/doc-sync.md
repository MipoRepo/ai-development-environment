---
name: doc-sync
description: Pitää ajan tasalla MkDocs-dokumentaation ja projektin muistitiedostot
version: 1.0.0
model: claude-sonnet-5
---

# Doc Sync — AIDE-projekti

## Kuvaus

Tämä on natiivi Claude Code -agentti, joka vastaa projektin dokumentaation ja
muistitiedostojen yhtenäisyydestä:

1. **CLAUDE.md** on ajan tasalla projektin rakenteesta
2. **MEMORY.md**-indeksi viittaa olemassaoleviin tiedostoihin
3. Muistitiedostot ovat oikeassa muodissa (YAML frontmatter + **Miksi:** / **Kuinka sovellettavaksi:**)
4. MkDocs `site/`-hakemisto on rakennettu uusimmista lähteistä

## Toiminnot

Kun aktivoit tämän agentin, se:

1. Skannaa kaikki `.py`-tiedostot ja vertaa niitä `site/`-HTML-sivuisiin
2. Tarkistaa `MEMORY.md`-viitteet osoittaisevat oikeisiin tiedostoihin (.claude/memories/)
3. Varmistaa että jokainen muistitiedosto noudattaa tätä muistimuotoa:

```yaml
---
name: <kebab-case-tunniste>
description: <yhden-rivin-tiivistelmä>
metadata:
  type: user | feedback | project | reference
---
<sisältö>

## Miksi:

<Miksi tämä muisti on tärkeä>

## Kuinka sovellettavaksi:

<Koodiesimerkki>
```

4. Ehdottaa päivityksiä vanhentuneisiin tiedostoihin

## Esimerkkikäyttö

```
/doc-sync
```

---
Agentti luotu `.claude/agents/doc-sync.md`.
