# Arkkitehtuurin yleiskuva

AIDE koostuu kolmesta tasosta:

1. **Engine-repo** (`ai-dev-environment/`) — määrittelee toiminnan.
2. **Doc-repo** (`docs/`) — selittää sen ihmiselle.
3. **Projektirepo** (`esim. RepoStageAI/`) — määrittelee tavoitteen.

---

## Kolme kerrosta

- **Agenttikerros** — Director, Planner, Developer, jne.
- **Workflow-kerros** — Analyze → ... → Document.
- **Deterministinen engine** — Git, testit, validoinnit.
