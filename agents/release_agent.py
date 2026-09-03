"""
ReleaseAgent-moduuli (M15) — julkaisun ja sääntelyn hallinta.

Sisältää kolme agenttia:
- ReleaseManagerAgent: versiointi, julkaisuvaiheet ja deploy-valmius.
- ChangelogAgent: automaattinen changelog-generointi muutuksista.
- ComplianceAgent: lisenssi- ja standardintutkimus (MIT, Apache, GDPR, PCI).
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


# Julkaisuvaiheet
RELEASE_PHASES: list[str] = [
    "pre_release",
    "build",
    "test",
    "security_check",
    "documentation",
    "packaging",
    "deploy",
]

# Riippuvuustyypit
DEPLOYMENT_STRATEGIES: dict[str, dict[str, str]] = {
    "blue_green": {
        "name": "Sinivihreä",
        "description": "Kaksi ympäristöä: sininen (tuotanto) ja vihreä (uusi). Vaihda yhtä kerralla.",
    },
    "rolling": {
        "name": "Pyöreä",
        "description": "Päivitä palvelimet yksitellen ilman poistuvuutta.",
    },
    "canary": {
        "name": "Canary",
        "description": "Pääosan käyttäjistä alkuperäisessä, pienen osan uudessa versiossa.",
    },
    "recreate": {
        "name": "Uudelleenkäsittely",
        "description": "Poista vanha ja luo uusi kaikki palvelimet.",
    },
}

# SemVer-komponentit
SEMVER_PATTERN = r"^v?(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?(?:\+([a-zA-Z0-9.]+))?$"

# Lisenssit ja standardit
LICENSE_TYPES: dict[str, dict[str, Any]] = {
    "MIT": {
        "name": "MIT License",
        "osi_approved": True,
        "commercial_use": True,
        "modification": True,
        "distribution": True,
        "patent_use": False,
        "description": "Yksinkertainen avoin lähde, joka sallii likaaliaisen käytön.",
    },
    "Apache-2.0": {
        "name": "Apache License 2.0",
        "osi_approved": True,
        "commercial_use": True,
        "modification": True,
        "distribution": True,
        "patent_use": True,
        "description": "Avoin lähde patenttikärsinnän kanssa.",
    },
    "GPL-3.0": {
        "name": "GNU General Public License v3.0",
        "osi_approved": True,
        "commercial_use": True,
        "modification": True,
        "distribution": True,
        "patent_use": True,
        "description": "Copyleft-lisenssi, joka vaatii lähdekoodin jakamista muutettuina.",
    },
    "BSD-3-Clause": {
        "name": "BSD 3-Clause",
        "osi_approved": True,
        "commercial_use": True,
        "modification": True,
        "distribution": True,
        "patent_use": False,
        "description": "Kolmen ehdon BSD-lisenssi.",
    },
    "proprietary": {
        "name": "Proprietary",
        "osi_approved": False,
        "commercial_use": False,
        "modification": False,
        "distribution": False,
        "patent_use": False,
        "description": "Suljetun lähdekoodin lisenssi.",
    },
}

# Sääntelyn standardit
REGULATORY_STANDARDS: dict[str, dict[str, str]] = {
    "gdpr": {
        "name": "GDPR (Yleinen tietosuoja-asetus)",
        "description": "EU:n tietosuojasääntely henkilötietojen käsittelyssä.",
        "scope": "EU:ssa toimivat sovellukset henkilötietojen käsittelyssä",
        "requirements": "Käyttäjän suostumus, oikeus tietoihin, oikeus unohda, ilmoitus 72h",
    },
    "pci-dss": {
        "name": "PCI DSS",
        "description": "Maksukorttitietoja koskevat turvallisuusstandardit.",
        "scope": "Käsittelevät maksukorttia koskevia tietoja",
        "requirements": "Verkkomallit, salaus, pääsyhallinta, lokiointi",
    },
    "soc2": {
        "name": "SOC 2",
        "description": "Palvelintason ehtiivyys ja turvallisuusmittarit.",
        "scope": "SaaS-yritykset ja pilvituspalvelut",
        "requirements": "Turvallisuus, yksityisyys, saatavuus, prosessointi, seuranta",
    },
    "iso27001": {
        "name": "ISO 27001",
        "description": "Tiedon turvallisuuden hallintojärjestelmä.",
        "scope": "Kaikki organisaatiot",
        "requirements": "Riskienhallinta, turvallisuuspolitiikat, prosessit, koulutus",
    },
    "hipaa": {
        "name": "HIPAA",
        "description": "Yhdysvaltain laki terveydenomintiedoille.",
        "scope": "Terveyspalvelu ja terveysdatan käsittely",
        "requirements": "Suojaus, salaus, pääsyoikeudet, audit-loki",
    },
}


class ReleaseManagerInput(AgentInput):
    """ReleaseManagerAgentin syöte."""
    action: str = Field(default="plan", description="Toiminto (plan, execute, validate, bump_version).")
    current_version: str = Field(default="1.0.0", description="Nykyinen versio SemVer-muodossa.")
    target_version: str = Field(default="", description="Kohdeversio SemVer-muodossa.")
    release_type: str = Field(default="patch", description="Julkaisun tyyppi (major, minor, patch, pre-release).")
    deployment_strategy: str = Field(default="rolling", description="Deploy-strategia (blue_green, rolling, canary, recreate).")
    auto_tag: bool = Field(default=True, description="Luo automaattisesti Git-tag versiolle.")
    run_tests: bool = Field(default=True, description="Aja testit ennen julkaisua.")
    check_security: bool = Field(default=True, description="Tarkista turvallisuus ennen julkaisua.")


class ReleaseManagerOutput(AgentOutput):
    """ReleaseManagerAgentin tuloste."""
    current_version: str = Field(default="", description="Nykyinen versio.")
    target_version: str = Field(default="", description="Kohdeversio.")
    release_plan: list[dict[str, Any]] = Field(default_factory=list, description="Julkaisusuunnitelma.")
    phases: list[str] = Field(default_factory=list, description="Suoritettavat vaiheet.")
    git_tag: str = Field(default="", description="Luodun Git-tagin nimi.")
    deployment_ready: bool = Field(default=False, description="Onko deploy valmiina?")
    deployment_ready_reason: str = Field(default="", description="Miksi deploy ei ole valmis?")


class ChangelogInput(AgentInput):
    """ChangelogAgentin syöte."""
    action: str = Field(default="generate", description="Toiminto (generate, parse, format).")
    changes: list[dict[str, Any]] = Field(default_factory=list, description="Muutoshistoria (commitit, bugit, ominaisuudet).")
    version: str = Field(default="", description="Versio jolle changelog-generoidaan.")
    format: str = Field(default="keepachangelog", description="Muotoilu (keepachangelog, unreleased, markdown).")
    previous_version: str = Field(default="", description="Edellinen versio.")


class ChangelogOutput(AgentOutput):
    """ChangelogAgentin tuloste."""
    changelog_content: str = Field(default="", description="Generoitu changelog.")
    version: str = Field(default="", description="Versio.")
    sections: list[str] = Field(default_factory=list, description="Changelog-osiot.")
    changes_count: dict[str, int] = Field(default_factory=dict, description="Muutosten lukumäärä osioittain.")
    total_changes: int = Field(default=0, description="Muutosten kokonaismäärä.")


class ComplianceInput(AgentInput):
    """ComplianceAgentin syöte."""
    action: str = Field(default="check_license", description="Toiminto (check_license, check_regulatory, check_dependencies, full_audit).")
    license_type: str = Field(default="MIT", description="Projektin lisenssi.")
    project_path: str = Field(default=".", description="Projektin polku tarkistuksia varten.")
    regulatory_standards: list[str] = Field(default_factory=list, description="Tarkistettavat sääntelyt (gdpr, pci-dss, soc2, iso27001, hipaa).")
    dependencies: list[str] = Field(default_factory=list, description="Riippuvuusnimet turvallisuustarkistukselle.")


class ComplianceOutput(AgentOutput):
    """ComplianceAgentin tuloste."""
    license_info: dict[str, Any] = Field(default_factory=dict, description="Lisenssitiedot.")
    regulatory_findings: list[dict[str, str]] = Field(default_factory=list, description="Sääntelyn havainnot.")
    dependency_issues: list[dict[str, str]] = Field(default_factory=list, description="Riippuidetut turvallisuusongelmat.")
    compliance_score: float = Field(default=0, description="Yhteensopivuuspistemäärä 0-100.")
    recommendations: list[str] = Field(default_factory=list, description="Suositukset.")
    total_standards: int = Field(default=0, description="Tarkistettujen standardien määrä.")


class ReleaseManagerAgent(BaseAgent):
    """
    ReleaseManagerAgent hallitsee versiointia, julkaisevaiheita ja deploy-valmiutta.

    Usage:
        agent = ReleaseManagerAgent()
        result = agent.run("Suunnittele julkaisu", current_version="1.2.0", release_type="minor")
    """

    agent_type: str = "release_manager"
    input_schema = ReleaseManagerInput
    output_schema = ReleaseManagerOutput

    def _parse_version(self, version: str) -> tuple[int, int, int]:
        """Parsi SemVer-versio major.minor.patch -muotoon."""
        match = re.match(SEMVER_PATTERN, version)
        if match:
            return int(match.group(1)), int(match.group(2)), int(match.group(3))
        return 1, 0, 0

    def _bump_version(self, major: int, minor: int, patch: int, release_type: str) -> str:
        """Nosta versiota release-tyypin mukaan."""
        if release_type == "major":
            return f"{major + 1}.0.0"
        elif release_type == "minor":
            return f"{major}.{minor + 1}.0"
        else:  # patch
            return f"{major}.{minor}.{patch + 1}"

    def _generate_git_tag(self, version: str) -> str:
        """Luo Git-tagin."""
        return f"v{version}"

    def _plan_phases(self, input_data: ReleaseManagerInput) -> list[str]:
        """Suunnittelee julkaisuvaiheet."""
        phases = list(RELEASE_PHASES)

        if not input_data.run_tests:
            phases = [p for p in phases if p != "test"]

        if not input_data.check_security:
            phases = [p for p in phases if p != "security_check"]

        return phases

    def _validate_deployment(self, input_data: ReleaseManagerInput, target_version: str) -> tuple[bool, str]:
        """Varmista että deploy on valmiina."""
        if not target_version:
            return False, "Kohdeversiota ei ole määritelty."

        if not input_data.target_version:
            return False, "Kohdeversiota ei ole määritelty."

        current = self._parse_version(input_data.current_version)
        target = self._parse_version(target_version)

        if target[0] < current[0] or (target[0] == current[0] and target[1] < current[1]) or \
           (target[0] == current[0] and target[1] == current[1] and target[2] < current[2]):
            return False, f"Kohdeversio {target_version} on vanhempi kuin nykyinen {input_data.current_version}."

        return True, ""

    def _plan_release(self, input_data: ReleaseManagerInput) -> ReleaseManagerOutput:
        """Suunnittelee julkaisun."""
        major, minor, patch = self._parse_version(input_data.current_version)

        if input_data.target_version:
            target_version = input_data.target_version
        else:
            target_version = self._bump_version(major, minor, patch, input_data.release_type)

        phases = self._plan_phases(input_data)
        git_tag = self._generate_git_tag(target_version) if input_data.auto_tag else ""

        deployment_ready, reason = self._validate_deployment(input_data, target_version)

        release_plan = [
            {"phase": "pre_release", "action": f"Vahvista versio {input_data.current_version} -> {target_version}", "status": "planned"},
            {"phase": "build", "action": "Käännä tuote", "status": "planned"},
            {"phase": "test", "action": "Suorita testit", "status": "planned" if input_data.run_tests else "skipped"},
            {"phase": "security_check", "action": "Turvallisuustarkistus", "status": "planned" if input_data.check_security else "skipped"},
            {"phase": "documentation", "action": "Generoi dokumentaatio", "status": "planned"},
            {"phase": "packaging", "action": "Pakkaus (wheel, sdist)", "status": "planned"},
            {"phase": "deploy", "action": f"Deploy strategia: {input_data.deployment_strategy}", "status": "planned"},
        ]

        return ReleaseManagerOutput(
            success=True,
            result={"current": input_data.current_version, "target": target_version, "phases": len(phases)},
            message=f"Julkaisu suunniteltu {input_data.current_version} -> {target_version} (strategia: {input_data.deployment_strategy}).",
            agent_type=self.agent_type,
            current_version=input_data.current_version,
            target_version=target_version,
            release_plan=release_plan,
            phases=phases,
            git_tag=git_tag,
            deployment_ready=deployment_ready,
            deployment_ready_reason=reason,
        )

    def _bump_version_only(self, input_data: ReleaseManagerInput) -> ReleaseManagerOutput:
        """Vain version bumped."""
        major, minor, patch = self._parse_version(input_data.current_version)
        target_version = self._bump_version(major, minor, patch, input_data.release_type)

        return ReleaseManagerOutput(
            success=True,
            result={"bumped": input_data.current_version, "to": target_version},
            message=f"Versio nostettu {input_data.current_version} -> {target_version}.",
            agent_type=self.agent_type,
            current_version=input_data.current_version,
            target_version=target_version,
            release_plan=[],
            phases=[],
            git_tag=self._generate_git_tag(target_version),
        )

    def _execute_release(self, input_data: ReleaseManagerInput) -> ReleaseManagerOutput:
        """Suorita julkaisu."""
        plan_result = self._plan_release(input_data)

        for step in plan_result.release_plan:
            step["status"] = "completed"

        return ReleaseManagerOutput(
            success=True,
            result={"executed": True, "target_version": plan_result.target_version},
            message=f"Julkaisu suoritettu versioon {plan_result.target_version}.",
            agent_type=self.agent_type,
            current_version=input_data.current_version,
            target_version=plan_result.target_version,
            release_plan=plan_result.release_plan,
            phases=[],
            git_tag=plan_result.git_tag,
            deployment_ready=True,
        )

    def _validate_release(self, input_data: ReleaseManagerInput) -> ReleaseManagerOutput:
        """Varmista julkaisu on valmis."""
        if input_data.target_version:
            target = input_data.target_version
        else:
            major, minor, patch = self._parse_version(input_data.current_version)
            target = self._bump_version(major, minor, patch, input_data.release_type)

        deployment_ready, reason = self._validate_deployment(input_data, target)

        return ReleaseManagerOutput(
            success=True,
            result={"validated": True, "version": target, "ready": deployment_ready},
            message=f"Julkaisu valmius tarkistettu. Valmiina: {deployment_ready}.",
            agent_type=self.agent_type,
            current_version=input_data.current_version,
            target_version=target,
            release_plan=[],
            phases=[],
            git_tag=self._generate_git_tag(target) if input_data.auto_tag else "",
            deployment_ready=deployment_ready,
            deployment_ready_reason=reason,
        )

    def _run(self, input_data: ReleaseManagerInput) -> ReleaseManagerOutput:
        """ReleaseManagerAgentin päälogiikka."""
        action = input_data.action.lower()

        if action == "plan":
            return self._plan_release(input_data)
        elif action == "execute":
            return self._execute_release(input_data)
        elif action == "validate":
            return self._validate_release(input_data)
        elif action == "bump_version":
            return self._bump_version_only(input_data)
        else:
            return ReleaseManagerOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'.",
                agent_type=self.agent_type,
                deployment_ready=False,
            )


class ChangelogAgent(BaseAgent):
    """
    ChangelogAgent generoi changelogit muutouksista.

    Usage:
        agent = ChangelogAgent()
        result = agent.run("Luo changelog", changes=[{"type": "feature", "description": "Uusi API"}], version="1.2.0")
    """

    agent_type: str = "changelog"
    input_schema = ChangelogInput
    output_schema = ChangelogOutput

    def _categorize_changes(self, changes: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Ryhmittelee muutokset tyyppeihin."""
        categorized: dict[str, list[dict[str, Any]]] = {
            "Added": [],
            "Changed": [],
            "Deprecated": [],
            "Removed": [],
            "Fixed": [],
            "Security": [],
        }

        for change in changes:
            change_type = change.get("type", "").lower()
            description = change.get("description", change.get("title", ""))

            entry = {
                "description": description,
                "author": change.get("author", "tuntematon"),
                "commit": change.get("commit", change.get("id", ""))[:8] if change.get("commit") or change.get("id") else "",
            }

            if change_type in ("feature", "added", "add", "feat"):
                categorized["Added"].append(entry)
            elif change_type in ("fix", "bugfix", "bug", "patch"):
                categorized["Fixed"].append(entry)
            elif change_type in ("change", "changed", "update", "updated"):
                categorized["Changed"].append(entry)
            elif change_type in ("remove", "removed", "delete"):
                categorized["Removed"].append(entry)
            elif change_type in ("deprecate", "deprecated"):
                categorized["Deprecated"].append(entry)
            elif change_type in ("security", "vulnerability"):
                categorized["Security"].append(entry)

        return categorized

    def _format_keepachangelog(self, version: str, categorized: dict[str, list[dict[str, Any]]]) -> str:
        """Generoi Keep a Changelog -muodon."""
        lines = [f"## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n"]

        sections = []
        for section_name, entries in categorized.items():
            if entries:
                sections.append(f"### {section_name}")
                for entry in entries:
                    desc = entry["description"]
                    commit_info = f" ({entry['commit']})" if entry.get("commit") else ""
                    author_info = f" - {entry['author']}" if entry.get("author") else ""
                    sections.append(f"- {desc}{commit_info}{author_info}")
                sections.append("")

        lines.extend(sections)
        return "\n".join(lines).rstrip()

    def _format_markdown(self, version: str, categorized: dict[str, list[dict[str, Any]]]) -> str:
        """Generoi yksinkertaisen markdown-muodon."""
        lines = [f"# Changelog\n\n## {version}\n"]

        for section_name, entries in categorized.items():
            if entries:
                lines.append(f"\n### {section_name}\n")
                for entry in entries:
                    lines.append(f"- {entry['description']}")

        return "\n".join(lines)

    def _count_changes(self, categorized: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
        """Laskee muutosten määrän osioittain."""
        return {name: len(entries) for name, entries in categorized.items() if entries}

    def _run(self, input_data: ChangelogInput) -> ChangelogOutput:
        """ChangelogAgentin päälogiika."""
        action = input_data.action.lower()
        changes = input_data.changes
        version = input_data.version or "Unreleased"
        fmt = input_data.format.lower()

        if action == "generate":
            categorized = self._categorize_changes(changes)

            if fmt == "keepachangelog":
                content = self._format_keepachangelog(version, categorized)
            elif fmt == "markdown":
                content = self._format_markdown(version, categorized)
            elif fmt == "unreleased":
                content = self._format_keepachangelog("Unreleased", categorized)
            else:
                content = self._format_keepachangelog(version, categorized)

            changes_count = self._count_changes(categorized)
            sections = [s for s, e in categorized.items() if e]
            total = sum(changes_count.values())

            return ChangelogOutput(
                success=True,
                result={"version": version, "total_changes": total},
                message=f"Changelog generoitu versiolle {version} ({total} muutosta).",
                agent_type=self.agent_type,
                changelog_content=content,
                version=version,
                sections=sections,
                changes_count=changes_count,
                total_changes=total,
            )
        elif action == "parse":
            changelog_path = Path(input_data.context.get("changelog_path", "CHANGELOG.md"))
            if changelog_path.exists():
                content = changelog_path.read_text(encoding="utf-8")
                return ChangelogOutput(
                    success=True,
                    result={"parsed": True, "lines": len(content.splitlines())},
                    message="Changelog parsittu.",
                    agent_type=self.agent_type,
                    changelog_content=content[:500],
                    version=version,
                    sections=[],
                    total_changes=content.count("## [") if "## [" in content else 0,
                )
            return ChangelogOutput(
                success=False,
                result=None,
                message="Changelog-tiedostoa ei loytynt.",
                agent_type=self.agent_type,
            )
        else:
            return ChangelogOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'.",
                agent_type=self.agent_type,
            )


class ComplianceAgent(BaseAgent):
    """
    ComplianceAgent tarkistaa lisenssit ja saaetelystandit.

    Usage:
        agent = ComplianceAgent()
        result = agent.run("Tarkista standardit", action="check_regulatory", regulatory_standards=["gdpr", "pci-dss"])
    """

    agent_type: str = "compliance"
    input_schema = ComplianceInput
    output_schema = ComplianceOutput

    def _get_license_info(self, license_type: str) -> dict[str, Any]:
        """Hakee lisenssin tiedot."""
        return LICENSE_TYPES.get(license_type, {
            "name": license_type,
            "osi_approved": False,
            "commercial_use": False,
            "modification": False,
            "distribution": False,
            "patent_use": False,
            "description": "Tuntematon lisenssi.",
        })

    def _check_regulatory_compliance(self, standards: list[str]) -> list[dict[str, str]]:
        """Tarkista saatetlyystandit."""
        findings = []
        for standard in standards:
            standard_lower = standard.lower().replace("-", "")
            info = REGULATORY_STANDARDS.get(standard_lower)
            if info:
                findings.append({
                    "standard": info["name"],
                    "scope": info["scope"],
                    "requirements": info["requirements"],
                    "description": info["description"],
                    "status": "needs_review",
                })
            else:
                findings.append({
                    "standard": standard,
                    "scope": "tuntematon",
                    "requirements": "tuntematon",
                    "status": "not_recognized",
                })
        return findings

    def _check_dependency_security(self, dependencies: list[str]) -> list[dict[str, str]]:
        """Tarkista riippuidetut turvallisuusongelmat (simulointi)."""
        issues = []
        known_vulnerable = {"django<3.2", "flask<2.0", "requests<2.28"}

        for dep in dependencies:
            for vuln in known_vulnerable:
                if vuln in dep:
                    pkg_name = dep.split(">=")[0].split("<")[0].split("==")[0]
                    issues.append({
                        "dependency": dep,
                        "issue": "vanhentunut versio",
                        "severity": "high",
                        "recommendation": f"Paivita {pkg_name} uudempaan versioon.",
                    })
        return issues

    def _scan_license_file(self, project_path: str) -> Optional[str]:
        """Etsi lisenssitiedosto projektista."""
        path = Path(project_path)
        license_files = ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "COPYING.txt"]

        for filename in license_files:
            license_path = path / filename
            if license_path.exists():
                return license_path.read_text(encoding="utf-8")[:500]

        return None

    def _detect_license_from_file(self, content: str) -> str:
        """Havaitse lisenssi tiedoston perusteesta."""
        content_lower = content.lower()

        if "mit license" in content_lower:
            return "MIT"
        elif "apache license" in content_lower and "2.0" in content_lower:
            return "Apache-2.0"
        elif "gnu general public" in content_lower:
            return "GPL-3.0"
        elif "bsd" in content_lower and "3-clause" in content_lower:
            return "BSD-3-Clause"
        elif "proprietary" in content_lower or "all rights reserved" in content_lower:
            return "proprietary"

        return "unknown"

    def _calculate_compliance_score(
        self,
        license_info: dict[str, Any],
        regulatory_findings: list[dict[str, str]],
        dependency_issues: list[dict[str, str]],
    ) -> float:
        """Laskee yhteensopivuuspistemäärän."""
        score = 100.0

        if not license_info.get("osi_approved", False):
            score -= 20

        score -= len(dependency_issues) * 10

        needs_review = sum(1 for f in regulatory_findings if f.get("status") == "needs_review")
        score -= needs_review * 5

        unknown = sum(1 for f in regulatory_findings if f.get("status") == "not_recognized")
        score -= unknown * 10

        return max(0.0, round(score, 1))

    def _generate_recommendations(
        self,
        license_info: dict[str, Any],
        regulatory_findings: list[dict[str, str]],
        dependency_issues: list[dict[str, str]],
    ) -> list[str]:
        """Luo suositukset."""
        recommendations = []

        if not license_info.get("osi_approved"):
            recommendations.append("Harkitse OSI-hyvaksuttua avoimen lahdevoinnin lisenssia.")

        for issue in dependency_issues:
            recommendations.append(f"Paivita {issue['dependency']}: {issue['recommendation']}")

        unresolved = [f for f in regulatory_findings if f.get("status") == "needs_review"]
        if unresolved:
            recommendations.append("Kayy lapi saatetlyn vaatimukset jokaiselle standardille.")

        if not recommendations:
            recommendations.append("Ei tunnistettuja ongelmia. Jatka säännollista valvontaa.")

        return recommendations

    def _run(self, input_data: ComplianceInput) -> ComplianceOutput:
        """ComplianceAgentin päälogiika."""
        action = input_data.action.lower()

        license_info = self._get_license_info(input_data.license_type)

        if input_data.project_path != ".":
            file_license = self._scan_license_file(input_data.project_path)
            if file_license:
                detected = self._detect_license_from_file(file_license)
                if detected != "unknown":
                    license_info = self._get_license_info(detected)

        regulatory_findings = []
        if input_data.regulatory_standards:
            if action in ("check_regulatory", "full_audit"):
                regulatory_findings = self._check_regulatory_compliance(input_data.regulatory_standards)

        dependency_issues = []
        if input_data.dependencies:
            if action in ("check_dependencies", "full_audit"):
                dependency_issues = self._check_dependency_security(input_data.dependencies)

        compliance_score = self._calculate_compliance_score(license_info, regulatory_findings, dependency_issues)
        recommendations = self._generate_recommendations(license_info, regulatory_findings, dependency_issues)

        return ComplianceOutput(
            success=True,
            result={"score": compliance_score, "standards_checked": len(regulatory_findings)},
            message=f"Yhteensopivuustarkistus valmis. Pisteet: {compliance_score}/100.",
            agent_type=self.agent_type,
            license_info=license_info,
            regulatory_findings=regulatory_findings,
            dependency_issues=dependency_issues,
            compliance_score=compliance_score,
            recommendations=recommendations,
            total_standards=len(regulatory_findings),
        )
