"""
Testit Release-agenteille (M15): ReleaseManagerAgent, ChangelogAgent, ComplianceAgent.
"""

import pytest

from agents.release_agent import (
    ReleaseManagerAgent,
    ReleaseManagerInput,
    ReleaseManagerOutput,
    ChangelogAgent,
    ChangelogInput,
    ChangelogOutput,
    ComplianceAgent,
    ComplianceInput,
    ComplianceOutput,
    RELEASE_PHASES,
    DEPLOYMENT_STRATEGIES,
    LICENSE_TYPES,
    REGULATORY_STANDARDS,
)


# ============================================================
# ReleaseManagerAgent tests
# ============================================================


@pytest.fixture
def release_agent():
    """Palauttaa ReleaseManagerAgent-instanssin."""
    return ReleaseManagerAgent()


class TestReleaseManagerAgent:
    """Testit ReleaseManagerAgentille."""

    def test_agent_type(self, release_agent):
        """Testaa agentin tyyppi."""
        assert release_agent.agent_type == "release_manager"

    def test_input_schema(self, release_agent):
        """Testaa syöteskeema."""
        assert release_agent.input_schema == ReleaseManagerInput

    def test_output_schema(self, release_agent):
        """Testaa tulosteskeema."""
        assert release_agent.output_schema == ReleaseManagerOutput

    def test_plan_release_default(self, release_agent):
        """Testaa oletusjulkaisun suunnittelu."""
        result = release_agent.run("Suunnittele julkaisu")
        assert result.success is True
        assert result.current_version == "1.0.0"
        assert result.target_version == "1.0.1"
        assert "suunniteltu" in result.message.lower()

    def test_plan_release_major(self, release_agent):
        """Testaa major-version nosto."""
        result = release_agent.run("Suunnittele major", current_version="2.5.3", release_type="major")
        assert result.success is True
        assert result.target_version == "3.0.0"

    def test_plan_release_minor(self, release_agent):
        """Testaa minor-version nosto."""
        result = release_agent.run("Suunnittele minor", current_version="2.5.3", release_type="minor")
        assert result.success is True
        assert result.target_version == "2.6.0"

    def test_plan_release_patch(self, release_agent):
        """Testaa patch-version nosto."""
        result = release_agent.run("Suunnittele patch", current_version="2.5.3", release_type="patch")
        assert result.success is True
        assert result.target_version == "2.5.4"

    def test_plan_release_with_target(self, release_agent):
        """Testaa kohdeversion asettaminen."""
        result = release_agent.run("Suunnittele", current_version="1.0.0", target_version="2.0.0")
        assert result.success is True
        assert result.target_version == "2.0.0"

    def test_plan_release_git_tag(self, release_agent):
        """Testaa Git-tagin luonti."""
        result = release_agent.run("Suunnittele", current_version="1.0.0", auto_tag=True)
        assert result.git_tag == "v1.0.1"

    def test_plan_release_no_git_tag(self, release_agent):
        """Testaa että Git-tagia ei luoda kun auto_tag=False."""
        result = release_agent.run("Suunnittele", current_version="1.0.0", auto_tag=False)
        assert result.git_tag == ""

    def test_plan_release_phases(self, release_agent):
        """Testaa että vaiheet sisältyvät suunnitelmaan."""
        result = release_agent.run("Suunnitelle", run_tests=True, check_security=True)
        assert "test" in result.phases
        assert "security_check" in result.phases
        assert "build" in result.phases
        assert "deploy" in result.phases

    def test_plan_release_skip_tests(self, release_agent):
        """Testaa testien ohittaminen."""
        result = release_agent.run("Suunnittele", run_tests=False)
        assert "test" not in result.phases

    def test_plan_release_skip_security(self, release_agent):
        """Testaa turvallisuustarkistuksen ohittaminen."""
        result = release_agent.run("Suunnittele", check_security=False)
        assert "security_check" not in result.phases

    def test_plan_release_deployment_ready(self, release_agent):
        """Testaa deploy-valmius oletusarvoin."""
        result = release_agent.run("Suunnittele", current_version="1.0.0", target_version="1.1.0")
        # deployment_ready riippuu _validate_deployment -logiikasta
        assert isinstance(result.deployment_ready, bool)

    def test_execute_release(self, release_agent):
        """Testaa julkaisun suoritus."""
        result = release_agent.run("Suorita", action="execute", current_version="1.0.0")
        assert result.success is True
        assert "suoritettu" in result.message.lower()
        assert len(result.release_plan) > 0

    def test_execute_release_phases_completed(self, release_agent):
        """Testaa että kaikki vaiheet merkitään suoritetuiksi."""
        result = release_agent.run("Suorita", action="execute", current_version="1.0.0")
        for step in result.release_plan:
            assert step["status"] == "completed"

    def test_validate_release(self, release_agent):
        """Testaa julkaisun validointi."""
        result = release_agent.run("Validoi", action="validate", current_version="1.0.0", target_version="1.1.0")
        assert result.success is True
        assert result.target_version == "1.1.0"

    def test_bump_version(self, release_agent):
        """Testaa version nosto ilman suunnitelmaa."""
        result = release_agent.run("Nosta", action="bump_version", current_version="1.2.3", release_type="minor")
        assert result.success is True
        assert result.target_version == "1.3.0"
        assert result.git_tag == "v1.3.0"

    def test_unknown_action(self, release_agent):
        """Testaa tuntemattoman toiminnon."""
        result = release_agent.run("Tuntematon", action="unknown_action")
        assert result.success is False
        assert "tuntematon" in result.message.lower()

    def test_deployment_strategies_available(self):
        """Testaa että kaikki deploy-strategiat ovat määritelty."""
        assert "blue_green" in DEPLOYMENT_STRATEGIES
        assert "rolling" in DEPLOYMENT_STRATEGIES
        assert "canary" in DEPLOYMENT_STRATEGIES
        assert "recreate" in DEPLOYMENT_STRATEGIES

    def test_release_phases_available(self):
        """Testaa että kaikki julkaisuvaiheet ovat määritelty."""
        assert "pre_release" in RELEASE_PHASES
        assert "build" in RELEASE_PHASES
        assert "test" in RELEASE_PHASES
        assert "security_check" in RELEASE_PHASES
        assert "documentation" in RELEASE_PHASES
        assert "packaging" in RELEASE_PHASES
        assert "deploy" in RELEASE_PHASES


# ============================================================
# ChangelogAgent tests
# ============================================================


@pytest.fixture
def changelog_agent():
    """Palauttaa ChangelogAgent-instanssin."""
    return ChangelogAgent()


class TestChangelogAgent:
    """Testit ChangelogAgentille."""

    def test_agent_type(self, changelog_agent):
        """Testaa agentin tyyppi."""
        assert changelog_agent.agent_type == "changelog"

    def test_input_schema(self, changelog_agent):
        """Testaa syöteskeema."""
        assert changelog_agent.input_schema == ChangelogInput

    def test_output_schema(self, changelog_agent):
        """Testaa tulosteskeema."""
        assert changelog_agent.output_schema == ChangelogOutput

    def test_generate_changelog_keepachangelog(self, changelog_agent):
        """Testaa changelogin generointi Keep a Changelog -muodossa."""
        changes = [
            {"type": "feature", "description": "Uusi API-liitinta"},
            {"type": "fix", "description": "Bugi kirjautumisessa"},
        ]
        result = changelog_agent.run(
            "Luo changelog",
            action="generate",
            changes=changes,
            version="1.2.0",
            format="keepachangelog",
        )
        assert result.success is True
        assert "1.2.0" in result.changelog_content
        assert "Added" in result.changelog_content
        assert "Fixed" in result.changelog_content
        assert result.version == "1.2.0"
        assert result.total_changes == 2

    def test_generate_changelog_markdown(self, changelog_agent):
        """Testaa changelogin generointi markdown-muodossa."""
        changes = [
            {"type": "feature", "description": "Uusi toiminta"},
        ]
        result = changelog_agent.run(
            "Luo changelog",
            action="generate",
            changes=changes,
            version="1.0.0",
            format="markdown",
        )
        assert result.success is True
        assert "# Changelog" in result.changelog_content

    def test_generate_changelog_unreleased(self, changelog_agent):
        """Testaa changelogin generointi 'unreleased'-muodossa."""
        changes = [
            {"type": "fix", "description": "Pikakorjaus"},
        ]
        result = changelog_agent.run(
            "Luo changelog",
            action="generate",
            changes=changes,
            format="unreleased",
        )
        assert result.success is True
        assert "Unreleased" in result.changelog_content

    def test_generate_changelog_empty_changes(self, changelog_agent):
        """Testaa tyhjän changelogin generointi."""
        result = changelog_agent.run("Luo changelog", action="generate", changes=[], version="1.0.0")
        assert result.success is True
        assert result.total_changes == 0
        assert "1.0.0" in result.changelog_content

    def test_categorize_changes_feature(self, changelog_agent):
        """Testaa feature-muusten luokittelu."""
        changes = [{"type": "feature", "description": "Uusi toiminta"}]
        categorized = changelog_agent._categorize_changes(changes)
        assert len(categorized["Added"]) == 1

    def test_categorize_changes_fix(self, changelog_agent):
        """Testaa korjauksien luokittelu."""
        changes = [{"type": "fix", "description": "Korjaus"}]
        categorized = changelog_agent._categorize_changes(changes)
        assert len(categorized["Fixed"]) == 1

    def test_categorize_changes_remove(self, changelog_agent):
        """Testaa poistusten luokittelu."""
        changes = [{"type": "remove", "description": "Poistettu"}]
        categorized = changelog_agent._categorize_changes(changes)
        assert len(categorized["Removed"]) == 1

    def test_categorize_changes_deprecated(self, changelog_agent):
        """Testaa deprekatoitujen luokittelu."""
        changes = [{"type": "deprecated", "description": "Vanhentunut"}]
        categorized = changelog_agent._categorize_changes(changes)
        assert len(categorized["Deprecated"]) == 1

    def test_categorize_changes_security(self, changelog_agent):
        """Testaa turvallisuusmuutosten luokittelu."""
        changes = [{"type": "security", "description": "Turvallisuusfiksaus"}]
        categorized = changelog_agent._categorize_changes(changes)
        assert len(categorized["Security"]) == 1

    def test_categorize_changes_changed(self, changelog_agent):
        """Testaa muutosten luokittelu."""
        changes = [{"type": "change", "description": "Muutos"}]
        categorized = changelog_agent._categorize_changes(changes)
        assert len(categorized["Changed"]) == 1

    def test_categorize_changes_mixed(self, changelog_agent):
        """Testaa sekoitettujen muutosten luokittelu."""
        changes = [
            {"type": "feature", "description": "Feature 1"},
            {"type": "fix", "description": "Fix 1"},
            {"type": "feature", "description": "Feature 2"},
        ]
        categorized = changelog_agent._categorize_changes(changes)
        assert len(categorized["Added"]) == 2
        assert len(categorized["Fixed"]) == 1

    def test_changelog_sections(self, changelog_agent):
        """Testaa että osiot palautetaan oikein."""
        changes = [
            {"type": "feature", "description": "Feature"},
            {"type": "fix", "description": "Fix"},
        ]
        result = changelog_agent.run("Luo changelog", action="generate", changes=changes, version="1.0.0")
        assert "Added" in result.sections
        assert "Fixed" in result.sections

    def test_changelog_changes_count(self, changelog_agent):
        """Testaa että muutosten lukumäärä lasketaan oikein."""
        changes = [
            {"type": "feature", "description": "F1"},
            {"type": "feature", "description": "F2"},
            {"type": "fix", "description": "Fix1"},
        ]
        result = changelog_agent.run("Luo changelog", action="generate", changes=changes, version="1.0.0")
        assert result.changes_count["Added"] == 2
        assert result.changes_count["Fixed"] == 1
        assert result.total_changes == 3

    def test_changelog_unknown_action(self, changelog_agent):
        """Testaa tuntemattoman toiminnon."""
        result = changelog_agent.run("Tuntematon", action="unknown")
        assert result.success is False
        assert "tuntematon" in result.message.lower()

    def test_changelog_with_author(self, changelog_agent):
        """Testaa changelogin generointi tekijän kanssa."""
        changes = [
            {"type": "feature", "description": "Feature", "author": "testaaja"},
        ]
        result = changelog_agent.run("Luo changelog", action="generate", changes=changes, version="1.0.0")
        assert "testaaja" in result.changelog_content

    def test_changelog_with_commit(self, changelog_agent):
        """Testaa changelogin generointi commixin tiedoilla."""
        changes = [
            {"type": "feature", "description": "Feature", "commit": "abc123def456"},
        ]
        result = changelog_agent.run("Luo changelog", action="generate", changes=changes, version="1.0.0")
        assert "abc123de" in result.changelog_content


# ============================================================
# ComplianceAgent tests
# ============================================================


@pytest.fixture
def compliance_agent():
    """Palauttaa ComplianceAgent-instanssin."""
    return ComplianceAgent()


class TestComplianceAgent:
    """Testit ComplianceAgentille."""

    def test_agent_type(self, compliance_agent):
        """Testaa agentin tyyppi."""
        assert compliance_agent.agent_type == "compliance"

    def test_input_schema(self, compliance_agent):
        """Testaa syöteskeema."""
        assert compliance_agent.input_schema == ComplianceInput

    def test_output_schema(self, compliance_agent):
        """Testaa tulosteskeema."""
        assert compliance_agent.output_schema == ComplianceOutput

    def test_check_license_mit(self, compliance_agent):
        """Testaa MIT-lisensin tarkistus."""
        result = compliance_agent.run("Tarkista lisenssi", license_type="MIT")
        assert result.success is True
        assert "license_info" in result.model_dump()
        assert result.license_info.get("osi_approved") is True

    def test_check_license_apache(self, compliance_agent):
        """Testaa Apache-lisensin tarkistus."""
        result = compliance_agent.run("Tarkista lisenssi", license_type="Apache-2.0")
        assert result.success is True
        assert result.license_info.get("patent_use") is True

    def test_check_license_proprietary(self, compliance_agent):
        """Testaa omistetun lisenssin tarkistus."""
        result = compliance_agent.run("Tarkista lisenssi", license_type="proprietary")
        assert result.success is True
        assert result.license_info.get("osi_approved") is False

    def test_check_license_unknown(self, compliance_agent):
        """Testaa tuntemattoman lisenssin tarkistus."""
        result = compliance_agent.run("Tarkista lisenssi", license_type="unknown-license")
        assert result.success is True
        assert result.license_info.get("osi_approved") is False

    def test_check_regulatory_gdpr(self, compliance_agent):
        """Testaa GDPR-standardin tarkistus."""
        result = compliance_agent.run(
            "Tarkista", action="check_regulatory", regulatory_standards=["gdpr"]
        )
        assert result.success is True
        assert result.total_standards == 1
        assert "GDPR" in result.regulatory_findings[0]["standard"]

    def test_check_regulatory_multiple(self, compliance_agent):
        """Testaa useiden standardien tarkistus."""
        result = compliance_agent.run(
            "Tarkista",
            action="check_regulatory",
            regulatory_standards=["gdpr", "pci-dss", "soc2"],
        )
        assert result.success is True
        assert result.total_standards == 3

    def test_check_regulatory_unknown_standard(self, compliance_agent):
        """Testaa tuntemattoman standardin tarkistus."""
        result = compliance_agent.run(
            "Tarkista", action="check_regulatory", regulatory_standards=["unknown-standard"]
        )
        assert result.success is True
        assert result.total_standards == 1
        assert result.regulatory_findings[0]["status"] == "not_recognized"

    def test_check_dependencies(self, compliance_agent):
        """Testaa riippuidettujen turvallisuustarkistus."""
        result = compliance_agent.run(
            "Tarkista", action="check_dependencies", dependencies=["django<3.2", "requests>=2.28"]
        )
        assert result.success is True
        assert len(result.dependency_issues) > 0
        assert "django" in result.dependency_issues[0]["dependency"]

    def test_full_audit(self, compliance_agent):
        """Testaa täydellinen auditointi."""
        result = compliance_agent.run(
            "Auditointi",
            action="full_audit",
            license_type="MIT",
            regulatory_standards=["gdpr", "soc2"],
            dependencies=["django<3.2"],
        )
        assert result.success is True
        assert result.total_standards == 2
        assert len(result.dependency_issues) > 0

    def test_compliance_score(self, compliance_agent):
        """Testaa yhteensopivuuspistemäärän laskeminen."""
        result = compliance_agent.run(
            "Tarkista",
            action="full_audit",
            license_type="proprietary",
            regulatory_standards=["gdpr"],
            dependencies=["django<3.2"],
        )
        assert result.compliance_score < 100  # Alle 100 koska ongelmia on

    def test_compliance_score_deduplicated_license(self, compliance_agent):
        """Testaa yhteensopivuuspisteet hyvälle lisenssille."""
        result = compliance_agent.run(
            "Tarkista",
            action="check_license",
            license_type="MIT",
            regulatory_standards=[],
            dependencies=[],
        )
        assert result.compliance_score == 100.0

    def test_recommendations(self, compliance_agent):
        """Testaa suositzysten luonnin."""
        result = compliance_agent.run(
            "Tarkista",
            action="full_audit",
            license_type="proprietary",
            regulatory_standards=["gdpr"],
            dependencies=["flask<2.0"],
        )
        assert len(result.recommendations) > 0

    def test_recommendations_no_issues(self, compliance_agent):
        """Testaa suositzysten luonnin ilman ongelmia."""
        result = compliance_agent.run(
            "Tarkista",
            action="check_license",
            license_type="MIT",
            regulatory_standards=[],
            dependencies=[],
        )
        assert len(result.recommendations) >= 1  # Vähintään "ei tunnistettuja ongelmia"

    def test_license_types_available(self):
        """Testaa että kaikki lisenssityypit ovat määritelty."""
        assert "MIT" in LICENSE_TYPES
        assert "Apache-2.0" in LICENSE_TYPES
        assert "GPL-3.0" in LICENSE_TYPES
        assert "BSD-3-Clause" in LICENSE_TYPES
        assert "proprietary" in LICENSE_TYPES

    def test_regulatory_standards_available(self):
        """Testaa että kaikki sääntelyn standardit ovat määritelty."""
        assert "gdpr" in REGULATORY_STANDARDS
        assert "pci-dss" in REGULATORY_STANDARDS
        assert "soc2" in REGULATORY_STANDARDS
        assert "iso27001" in REGULATORY_STANDARDS
        assert "hipaa" in REGULATORY_STANDARDS

    def test_license_type_fields(self):
        """Testaa että lisenssitiedot sisältävät kaikki kentät."""
        for license_type, info in LICENSE_TYPES.items():
            assert "name" in info
            assert "osi_approved" in info
            assert "description" in info

    def test_regulatory_standard_fields(self):
        """Testaa että sääntelystandardit sisältävät kaikki kentät."""
        for standard, info in REGULATORY_STANDARDS.items():
            assert "name" in info
            assert "description" in info
            assert "scope" in info
            assert "requirements" in info
