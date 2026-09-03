---
name: release-agents-m15
description: M15 Release & Governance -agentit ja niiden käyttö
type: project
---

# M15 Release & Governance — Release Agents (Alpha 2.5)

## Agentit

- **ReleaseManagerAgent** (`agents/release_agent.py`): versiointi, julkaisuvaiheet ja deploy-valmius
  - Toiminnot: `plan`, `execute`, `validate`, `bump_version`
  - Syöte: `ReleaseManagerInput` (action, current_version, target_version, release_type, deployment_strategy, auto_tag, run_tests, check_security)
  - Tuloste: `ReleaseManagerOutput` (release_plan, phases, git_tag, deployment_ready, deployment_ready_reason)

- **ChangelogAgent** (`agents/release_agent.py`): changelog-generointi muutoksista
  - Toiminnot: `generate`, `parse`
  - Syöte: `ChangelogInput` (action, changes, version, format, previous_version)
  - Tuloste: `ChangelogOutput` (changelog_content, version, sections, changes_count, total_changes)

- **ComplianceAgent** (`agents/release_agent.py`): lisenssi- ja sääntelystandardit
  - Toiminnot: `check_license`, `check_regulatory`, `check_dependencies`, `full_audit`
  - Syöte: `ComplianceInput` (action, license_type, project_path, regulatory_standards, dependencies)
  - Tuloste: `ComplianceOutput` (license_info, regulatory_findings, dependency_issues, compliance_score, recommendations, total_standards)

## Käyttöesimerkit

```python
from agents import ReleaseManagerAgent, ChangelogAgent, ComplianceAgent

# Julkaisun suunnittelu
rm = ReleaseManagerAgent()
plan = rm.run("Suunnittele", current_version="1.0.0", release_type="minor")
print(plan.target_version)  # "1.1.0"

# Changelog-generointi
ca = ChangelogAgent()
changes = [{"type": "feature", "description": "Uusi API"}]
changelog = ca.run("Luo changelog", changes=changes, version="1.1.0")

# Compliance-tarkistus
cmp = ComplianceAgent()
audit = cmp.run("Auditointi", action="full_audit", license_type="MIT",
                regulatory_standards=["gdpr", "soc2"], dependencies=["django<3.2"])
```

## Vakiot

- `RELEASE_PHASES`: pre_release, build, test, security_check, documentation, packaging, deploy
- `DEPLOYMENT_STRATEGIES`: blue_green, rolling, canary, recreate
- `LICENSE_TYPES`: MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, proprietary
- `REGULATORY_STANDARDS`: gdpr, pci-dss, soc2, iso27001, hipaa

## Testaus

- 60 testiä: `tests/test_release_agent.py`
- 88 % kattavuus
- 715 testiä kaikkiaan (kaikki läpäisti)

## Miksi:

M15 tarjoaa julkaisun ja sääntelyn agentit, jotka kaikki muut moduulit tarvitsevat. ReleaseManagerAgent integroi versiointilogiikan ja deploy-strategiat; ChangelogAgent generoi muutoshistorian; ComplianceAgent tarkistaa lisenssit ja sääntelystandarat (GDPR, PCI-DSS, SOC2, ISO 27001, HIPAA).

## Kuinka sovellettavaksi:

Tuo `from agents import ReleaseManagerAgent, ChangelogAgent, ComplianceAgent` missä tahdotan. Käytä release_agent-moduulia julkaisuvaiheiden suunnitteluun, changelog-generointiin ja compliance-auditointiin. Kaikki agentit noudattavat AgentInput/AgentOutput-pohjaista rakennetta ja tukevat `agent.run(intent, **params)`-kutsua.
