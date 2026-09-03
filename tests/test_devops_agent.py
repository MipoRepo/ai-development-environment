"""
Testit DevOpsAgenteille (M10).
"""

from pathlib import Path

import pytest

from agents.devops_agent import (
    DockerAgent,
    DockerAgentInput,
    DockerAgentOutput,
    CI_CDAgent,
    CICDAgentInput,
    CICDAgentOutput,
    InfrastructureAgent,
    InfrastructureAgentInput,
    InfrastructureAgentOutput,
    DeploymentAgent,
    DeploymentAgentInput,
    DeploymentAgentOutput,
    COMPOSE_TEMPLATES,
    GITHUB_WORKFLOW_TEMPLATES,
    DEPLOYMENT_TEMPLATES,
)


# ===================
# Fixtures
# ===================


@pytest.fixture
def docker_agent():
    return DockerAgent()


@pytest.fixture
def ci_cd_agent():
    return CI_CDAgent()


@pytest.fixture
def infra_agent():
    return InfrastructureAgent()


@pytest.fixture
def deploy_agent():
    return DeploymentAgent()


@pytest.fixture
def sample_project(tmp_path):
    """Luo minimipaketin testiprojektista."""
    (tmp_path / "requirements.txt").write_text(
        "fastapi>=0.95.0\npydantic>=2.0.0\npytest>=7.0.0\n",
        encoding="utf-8",
    )
    (tmp_path / "Dockerfile").write_text(
        "FROM python:3.11-alpine\nUSER app\nCMD [\"python\", \"app.py\"]\n",
        encoding="utf-8",
    )
    (tmp_path / ".dockerignore").write_text("__pycache__\n*.pyc\n", encoding="utf-8")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n",
        encoding="utf-8",
    )
    return tmp_path


# ===================
# DockerAgent tests
# ===================


class TestDockerAgent:
    """Testit DockerAgentille."""

    def test_agent_type(self, docker_agent):
        assert docker_agent.agent_type == "docker"

    def test_input_schema(self, docker_agent):
        assert docker_agent.input_schema == DockerAgentInput

    def test_output_schema(self, docker_agent):
        assert docker_agent.output_schema == DockerAgentOutput

    def test_run_python_api(self, docker_agent, tmp_path):
        """Python-API-projektin Docker-tiedostot luodaan oikein."""
        result = docker_agent.run(
            task="Luo Docker-tiedostot",
            project_type="python-api",
            output_path=str(tmp_path),
        )
        assert isinstance(result, DockerAgentOutput)
        assert result.success is True
        assert result.template_used == "python-api"
        assert result.dockerfile_path == str(tmp_path / "Dockerfile")
        assert result.compose_path == str(tmp_path / "docker-compose.yaml")

    def test_run_web_app(self, docker_agent, tmp_path):
        """Web-app-projekti saa oikean mallin."""
        result = docker_agent.run(
            task="Luo Docker",
            project_type="web-app",
            output_path=str(tmp_path),
        )
        assert result.template_used == "web-app"
        assert result.success is True

    def test_run_cli(self, docker_agent, tmp_path):
        """CLI-projekti saa oikean mallin."""
        result = docker_agent.run(
            task="Luo Docker",
            project_type="cli",
            output_path=str(tmp_path),
        )
        assert result.template_used == "cli"

    def test_run_unknown_type(self, docker_agent, tmp_path):
        """Tuntematon tyyppi käyttää default-mallia."""
        result = docker_agent.run(
            task="Luo Docker",
            project_type="unknown-type",
            output_path=str(tmp_path),
        )
        assert result.template_used == "default"
        assert result.success is True

    def test_dockerfile_content(self, docker_agent, tmp_path):
        """Dockerfile sisältää odotetut osat."""
        result = docker_agent.run(
            task="Luo Docker",
            project_type="python-api",
            output_path=str(tmp_path),
        )
        dockerfile = Path(result.dockerfile_path).read_text(encoding="utf-8")
        assert "FROM python" in dockerfile
        assert "pip install" in dockerfile
        assert "USER" in dockerfile

    def test_compose_content(self, docker_agent, tmp_path):
        """docker-compose.yaml sisältää odotetut palvelut."""
        result = docker_agent.run(
            task="Luo Docker",
            project_type="python-api",
            output_path=str(tmp_path),
        )
        compose = Path(result.compose_path).read_text(encoding="utf-8")
        assert "services:" in compose
        assert "app:" in compose
        assert "build:" in compose

    def test_security_score_good_dockerfile(self, docker_agent, tmp_path):
        """Hyvä Dockerfile saa hyvät pisteet."""
        result = docker_agent.run(
            task="Luo Docker",
            project_type="python-api",
            expose_port=8080,
            output_path=str(tmp_path),
        )
        assert result.security_score >= 80  # Hyvä tason

    def test_security_score_poor_dockerfile(self, docker_agent, tmp_path):
        """Huono Dockerfile saa alhaisemmat pisteet."""
        # Luo huono Dockerfile käsin
        bad_dockerfile = tmp_path / "Dockerfile"
        bad_dockerfile.write_text(
            "FROM ubuntu:latest\n"
            "ADD . /app\n"
            "RUN apt-get install -y curl\n"
            "EXPOSE 22\n"
            "RUN chmod -R 777 /app\n"
            "CMD curl https://example.com/script.sh | sh\n",
            encoding="utf-8",
        )
        score, recs = docker_agent._evaluate_dockerfile_security(bad_dockerfile.read_text(encoding="utf-8"))
        assert score < 80  # Huono taso
        assert len(recs) > 0

    def test_recommendations_returned(self, docker_agent, tmp_path):
        """Suositukset palautetaan."""
        result = docker_agent.run(
            task="Luo Docker",
            project_type="default",
            output_path=str(tmp_path),
        )
        assert isinstance(result.recommendations, list)

    def test_no_write_permissions(self, docker_agent, tmp_path):
        """Jos kirjoitus epäonnistuu, paluu onnistuneeksi."""
        result = docker_agent.run(
            task="Luo",
            output_path=str(tmp_path / "nonexistent" / "deep"),
        )
        # Tulisi luoda kansion, joten kirjoitus onnistuu silti
        assert result.success is True

    def test_expose_port_replacement(self, docker_agent):
        """Portti korvataan oikein."""
        content = docker_agent._generate_dockerfile("default", 9090)
        assert "9090" in content

    def test_serializes(self, docker_agent, tmp_path):
        """Tulos voidaan serialisoida."""
        result = docker_agent.run(
            task="Luo",
            output_path=str(tmp_path),
        )
        d = result.to_dict()
        assert d["agent_type"] == "docker"
        assert "dockerfile_path" in d


# ===================
# CI_CDAgent tests
# ===================


class TestCICDAgent:
    """Testit CI-CDAgentille."""

    def test_agent_type(self, ci_cd_agent):
        assert ci_cd_agent.agent_type == "ci_cd"

    def test_input_schema(self, ci_cd_agent):
        assert ci_cd_agent.input_schema == CICDAgentInput

    def test_output_schema(self, ci_cd_agent):
        assert ci_cd_agent.output_schema == CICDAgentOutput

    def test_run_creates_ci_cd(self, ci_cd_agent, tmp_path):
        """CI/CD -workflow luodaan oikein."""
        result = ci_cd_agent.run(
            task="Luo CI/CD",
            output_path=str(tmp_path / ".github" / "workflows"),
        )
        assert isinstance(result, CICDAgentOutput)
        assert result.success is True
        assert result.total_workflows > 0
        assert len(result.created_workflows) == result.total_workflows

    def test_run_creates_linting(self, ci_cd_agent, tmp_path):
        """Linting-workflow luodaan."""
        result = ci_cd_agent.run(
            task="Luo linting",
            workflows=["linting"],
            output_path=str(tmp_path / ".github" / "workflows"),
        )
        assert result.total_workflows == 1
        assert "linting" in result.created_workflows[0]

    def test_run_creates_security(self, ci_cd_agent, tmp_path):
        """Security-workflow luodaan."""
        result = ci_cd_agent.run(
            task="Luo security",
            workflows=["security"],
            output_path=str(tmp_path / ".github" / "workflows"),
        )
        assert result.total_workflows == 1

    def test_run_multiple_workflows(self, ci_cd_agent, tmp_path):
        """Useampi workflow luodaan yhtä aikaa."""
        result = ci_cd_agent.run(
            task="Luo kaikki",
            workflows=["ci-cd", "linting", "security"],
            output_path=str(tmp_path / ".github" / "workflows"),
        )
        assert result.total_workflows == 3

    def test_workflow_content(self, ci_cd_agent, tmp_path):
        """Workflow-sisältö sisältää oikeat komennot."""
        output = tmp_path / ".github" / "workflows"
        result = ci_cd_agent.run(
            task="Luo CI",
            workflows=["ci-cd"],
            output_path=str(output),
        )
        content = Path(result.created_workflows[0]).read_text(encoding="utf-8")
        assert "name:" in content
        assert "on:" in content
        assert "pytest" in content

    def test_python_version_replacement(self, ci_cd_agent, tmp_path):
        """Python-versiot korvataan matriisissa."""
        result = ci_cd_agent.run(
            task="Luo CI",
            workflows=["ci-cd"],
            python_versions=["3.11"],
            output_path=str(tmp_path / ".github" / "workflows"),
        )
        content = Path(result.created_workflows[0]).read_text(encoding="utf-8")
        assert "3.11" in content

    def test_custom_workflow_list(self, ci_cd_agent, tmp_path):
        """Vain valitut workflowt luodaan."""
        result = ci_cd_agent.run(
            task="Vain ci-cd",
            workflows=["ci-cd"],
            output_path=str(tmp_path / ".github" / "workflows"),
        )
        assert result.total_workflows == 1

    def test_serializes(self, ci_cd_agent, tmp_path):
        """Tulos voidaan serialisoida."""
        result = ci_cd_agent.run(
            task="Luo",
            output_path=str(tmp_path / ".github" / "workflows"),
        )
        d = result.to_dict()
        assert d["agent_type"] == "ci_cd"
        assert "created_workflows" in d


# ===================
# InfrastructureAgent tests
# ===================


class TestInfrastructureAgent:
    """Testit InfrastructureAgentille."""

    def test_agent_type(self, infra_agent):
        assert infra_agent.agent_type == "infrastructure"

    def test_input_schema(self, infra_agent):
        assert infra_agent.input_schema == InfrastructureAgentInput

    def test_output_schema(self, infra_agent):
        assert infra_agent.output_schema == InfrastructureAgentOutput

    def test_run_finds_infra_files(self, infra_agent, sample_project):
        """Infra-tiedostot löydetään oikein."""
        result = infra_agent.run(
            task="Analysoi infra",
            project_path=str(sample_project),
        )
        assert isinstance(result, InfrastructureAgentOutput)
        assert result.success is True
        assert len(result.infrastructure_files) >= 3  # requirements.txt, Dockerfile, .dockerignore, ci.yml
        assert "Dockerfile" in result.infrastructure_files
        assert ".dockerignore" in result.infrastructure_files

    def test_run_finds_dependencies(self, infra_agent, sample_project):
        """Riippuvuudet löydetään oikein."""
        result = infra_agent.run(
            task="Analysoi",
            project_path=str(sample_project),
        )
        assert len(result.dependencies) == 3
        dep_names = {d["name"] for d in result.dependencies}
        assert "fastapi" in dep_names
        assert "pydantic" in dep_names
        assert "pytest" in dep_names

    def test_run_finds_workflows(self, infra_agent, sample_project):
        """GitHub Actions -workflowt löydetään."""
        result = infra_agent.run(
            task="Analysoi",
            project_path=str(sample_project),
        )
        wf_files = [f for f in result.infrastructure_files if ".github" in f]
        assert len(wf_files) >= 1

    def test_recommendations_generated(self, infra_agent, sample_project):
        """Suositukset generoidaan löydetyistä tiedostoista."""
        result = infra_agent.run(
            task="Analysoi",
            project_path=str(sample_project),
        )
        assert len(result.recommendations) > 0

    def test_recommendations_for_missing_docker(self, infra_agent, tmp_path):
        """Suositukset puutteellista Dockeria koskevat."""
        (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")
        result = infra_agent.run(
            task="Analysoi",
            project_path=str(tmp_path),
        )
        rec_text = " ".join(result.recommendations)
        assert "Dockerfile" in rec_text

    def test_complexity_score(self, infra_agent, sample_project):
        """Monimutkaisuus pisteytetään."""
        result = infra_agent.run(
            task="Analysoi",
            project_path=str(sample_project),
        )
        assert 0.0 <= result.complexity_score <= 100.0

    def test_no_requirements(self, infra_agent, tmp_path):
        """Ilman requirements.txt paluu onnistunee tyhjänä."""
        result = infra_agent.run(
            task="Analysoi tyhjää",
            project_path=str(tmp_path),
        )
        assert result.success is True
        assert len(result.dependencies) == 0

    def test_serializes(self, infra_agent, sample_project):
        """Tulos voidaan serialisoida."""
        result = infra_agent.run(
            task="Analysoi",
            project_path=str(sample_project),
        )
        d = result.to_dict()
        assert d["agent_type"] == "infrastructure"
        assert "dependencies" in d

    def test_skip_directories(self, infra_agent, tmp_path):
        """Skipataan .venv ja __pycache__."""
        venv_dir = tmp_path / ".venv"
        venv_dir.mkdir()
        (venv_dir / "some_file.txt").write_text("test", encoding="utf-8")

        result = infra_agent.run(
            task="Analysoi",
            project_path=str(tmp_path),
        )
        assert not any(".venv" in f for f in result.infrastructure_files)


# ===================
# DeploymentAgent tests
# ===================


class TestDeploymentAgent:
    """Testit DeploymentAgentille."""

    def test_agent_type(self, deploy_agent):
        assert deploy_agent.agent_type == "deployment"

    def test_input_schema(self, deploy_agent):
        assert deploy_agent.input_schema == DeploymentAgentInput

    def test_output_schema(self, deploy_agent):
        assert deploy_agent.output_schema == DeploymentAgentOutput

    def test_run_docker_swarm(self, deploy_agent, tmp_path):
        """Docker Swarm -strategia toimii."""
        result = deploy_agent.run(
            task="Deploy",
            strategy="docker-swarm",
            project_name="myapp",
            output_path=str(tmp_path),
        )
        assert isinstance(result, DeploymentAgentOutput)
        assert result.success is True
        assert result.strategy == "docker-swarm"
        assert "docker-swarm" in result.config_path

    def test_run_kubernetes(self, deploy_agent, tmp_path):
        """Kubernetes-strategia toimii."""
        result = deploy_agent.run(
            task="Deploy",
            strategy="kubernetes",
            project_name="myapp",
            output_path=str(tmp_path),
        )
        assert result.strategy == "kubernetes"
        assert "kubernetes" in result.config_path

    def test_run_aws_ecs(self, deploy_agent, tmp_path):
        """AWS ECS -strategia toimii."""
        result = deploy_agent.run(
            task="Deploy",
            strategy="aws-ecs",
            project_name="myapp",
            output_path=str(tmp_path),
        )
        assert result.strategy == "aws-ecs"

    def test_run_static(self, deploy_agent, tmp_path):
        """Static hosting -strategia toimii."""
        result = deploy_agent.run(
            task="Deploy",
            strategy="static",
            project_name="myapp",
            output_path=str(tmp_path),
        )
        assert result.strategy == "static"
        assert "static" in result.config_path

    def test_deployment_steps_docker_swarm(self, deploy_agent, tmp_path):
        """Docker Swarm -vaiheet sisältävät odotetut komennot."""
        result = deploy_agent.run(
            task="Deploy",
            strategy="docker-swarm",
            project_name="myapp",
            output_path=str(tmp_path),
        )
        steps_text = " ".join(result.deployment_steps)
        assert "docker build" in steps_text
        assert "docker stack deploy" in steps_text

    def test_deployment_steps_kubernetes(self, deploy_agent, tmp_path):
        """Kubernetes-vaiheet sisältävät kubectl-komennot."""
        result = deploy_agent.run(
            task="Deploy",
            strategy="kubernetes",
            project_name="myapp",
            output_path=str(tmp_path),
        )
        steps_text = " ".join(result.deployment_steps)
        assert "kubectl" in steps_text

    def test_deployment_steps_aws_ecs(self, deploy_agent, tmp_path):
        """AWS ECS -vaiheet sisältävät aws-komennot."""
        result = deploy_agent.run(
            task="Deploy",
            strategy="aws-ecs",
            project_name="myapp",
            output_path=str(tmp_path),
        )
        steps_text = " ".join(result.deployment_steps)
        assert "aws" in steps_text

    def test_environment_stored(self, deploy_agent, tmp_path):
        """Deploy-ympäristö tallennetaan tuloksessa."""
        result = deploy_agent.run(
            task="Deploy",
            strategy="docker-swarm",
            project_name="myapp",
            environment="staging",
            output_path=str(tmp_path),
        )
        assert result.environment == "staging"

    def test_config_written_to_file(self, deploy_agent, tmp_path):
        """Konfiguraatio kirjoitetaan tiedostoon."""
        result = deploy_agent.run(
            task="Deploy",
            strategy="kubernetes",
            project_name="myapp",
            output_path=str(tmp_path),
        )
        assert Path(result.config_path).exists()
        content = Path(result.config_path).read_text(encoding="utf-8")
        assert "myapp" in content
        assert "Deployment" in content

    def test_config_content_returned(self, deploy_agent, tmp_path):
        """Konfiguraation sisältö palautetaan tulosteessa."""
        result = deploy_agent.run(
            task="Deploy",
            strategy="docker-swarm",
            project_name="myapp",
            output_path=str(tmp_path),
        )
        assert result.config_content != ""
        assert "myapp" in result.config_content or "deploy" in result.config_content.lower()

    def test_unknown_strategy_defaults(self, deploy_agent, tmp_path):
        """Tuntematon strategia käyttää defaultia."""
        result = deploy_agent.run(
            task="Deploy",
            strategy="unknown",
            project_name="myapp",
            output_path=str(tmp_path),
        )
        # Tulisi käyttää docker-swarm defaultina
        assert result.strategy == "unknown"  # Säilytetään alkuperäisenä
        assert result.success is True

    def test_serializes(self, deploy_agent, tmp_path):
        """Tulos voidaan serialisoida."""
        result = deploy_agent.run(
            task="Deploy",
            strategy="docker-swarm",
            project_name="myapp",
            output_path=str(tmp_path),
        )
        d = result.to_dict()
        assert d["agent_type"] == "deployment"
        assert "config_path" in d


# ===================
# Module-level tests
# ===================


class TestModuleLevel:
    """Testit moduulin tasolla."""

    def test_compose_templates_exist(self):
        """COMPOSE_TEMPLATES -dict on olemassa ja täynnä."""
        assert "python-api" in COMPOSE_TEMPLATES
        assert "web-app" in COMPOSE_TEMPLATES
        assert "cli" in COMPOSE_TEMPLATES
        assert "default" in COMPOSE_TEMPLATES
        for key, tmpl in COMPOSE_TEMPLATES.items():
            assert "dockerfile" in tmpl
            assert "compose" in tmpl

    def test_workflow_templates_exist(self):
        """GITHUB_WORKFLOW_TEMPLATES -dict on olemassa ja täynnä."""
        assert "ci-cd" in GITHUB_WORKFLOW_TEMPLATES
        assert "linting" in GITHUB_WORKFLOW_TEMPLATES
        assert "security" in GITHUB_WORKFLOW_TEMPLATES

    def test_deployment_templates_exist(self):
        """DEPLOYMENT_TEMPLATES -dict on olemassa ja täynnä."""
        assert "docker-swarm" in DEPLOYMENT_TEMPLATES
        assert "kubernetes" in DEPLOYMENT_TEMPLATES
        assert "aws-ecs" in DEPLOYMENT_TEMPLATES
        assert "static" in DEPLOYMENT_TEMPLATES
        for key, tmpl in DEPLOYMENT_TEMPLATES.items():
            assert "strategy" in tmpl
            assert "config" in tmpl
            assert "description" in tmpl

    def test_all_agents_importable(self):
        """Kaikki agentit tuodaan onnistuneesti."""
        from agents import (
            DockerAgent,
            CI_CDAgent,
            InfrastructureAgent,
            DeploymentAgent,
        )
        assert DockerAgent.agent_type == "docker"
        assert CI_CDAgent.agent_type == "ci_cd"
        assert InfrastructureAgent.agent_type == "infrastructure"
        assert DeploymentAgent.agent_type == "deployment"


# ===================
# Pydantic-validointi
# ===================


class TestPydanticValidation:
    """Testit Pydantic-validoinnille."""

    def test_docker_input_defaults(self):
        """DockerAgentInput saa oletusarvot."""
        inp = DockerAgentInput(task="test")
        assert inp.project_type == "python-api"
        assert inp.expose_port == 8000

    def test_docker_input_custom(self):
        """DockerAgentInput ottaa yliajetut arvot."""
        inp = DockerAgentInput(
            task="test",
            project_type="web-app",
            expose_port=3000,
        )
        assert inp.project_type == "web-app"
        assert inp.expose_port == 3000

    def test_cicd_input_defaults(self):
        """CICDAgentInput saa oletusarvot."""
        inp = CICDAgentInput(task="test")
        assert len(inp.workflows) == 3  # ci-cd, linting, security

    def test_infra_input_defaults(self):
        """InfrastructureAgentInput saa oletusarvot."""
        inp = InfrastructureAgentInput(task="test")
        assert inp.project_path == "."
        assert inp.check_docker is True

    def test_deploy_input_defaults(self):
        """DeploymentAgentInput saa oletusarvot."""
        inp = DeploymentAgentInput(task="test")
        assert inp.strategy == "docker-swarm"
        assert inp.replicas == 1
        assert inp.environment == "production"

    def test_output_schemas_serialize(self):
        """Kaikki output-skeemat voidaan serialisoida dictiksi."""
        docker_out = DockerAgentOutput(success=True, agent_type="docker")
        ci_out = CICDAgentOutput(success=True, agent_type="ci_cd")
        infra_out = InfrastructureAgentOutput(success=True, agent_type="infrastructure")
        deploy_out = DeploymentAgentOutput(success=True, agent_type="deployment")

        for out in [docker_out, ci_out, infra_out, deploy_out]:
            d = out.to_dict()
            assert "success" in d
            assert "agent_type" in d
