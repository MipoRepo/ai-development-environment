# Ensimmäinen projekti

Tässä opaassissa luo ensimmäinen projekti AIDE:n kanssa.

---

## 1. Projektin luonti

Luodaksesi uuden projektin, käytä komentoa:

```bash
aide init --name MyProject --type python-api
```

Tämä luo seuraavan rakenteen:

```
MyProject/
├── PROJECT.md
├── AGENTS.md
├── planning/
│   ├── vision.md
│   ├── architecture.md
│   ├── roadmap.md
│   └── decisions.md
├── docs/
├── src/
└── tests/
```

---

## 2. Projektin dokumentaatio

- **PROJECT.md** — Projektin visio, tavoitteet ja rajaukset.
- **AGENTS.md** — Projektitason ohjeet, jotka ohjaavat agentteja.

---

## 3. Seuraavat askeleet

Kun projekti on luotu, voit aloittaa kehittämisen antamalla tehtävän:

```bash
aide run "Lisää projektiin yhteystietolomake."
```

Katso lisää [käyttöoppaasta](user-guide/tasks.md) ja [agenttien listalta](agents/director.md).
