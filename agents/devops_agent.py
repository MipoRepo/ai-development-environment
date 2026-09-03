"""
DevOpsAgent-moduuli (M10) — projektin Docker, CI/CD, infra ja deploy -integraatiot.

Sisältää neljää agenttia:
- DockerAgent: luo Dockerfile- ja docker-compose.yaml-mallit.
- CI-CDAgent: luo GitHub Actions -workflowit.
- InfrastructureAgent: analysoi projektin infrastruktuurin ja suosittelee parannuksia.
- DeploymentAgent: suunnittelee deploy-strategian ja -ympäristöt.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


# Docker-compose-mallit eri projekti-tyyppeille
COMPOSE_TEMPLATES: dict[str, dict[str, str]] = {
    "python-api": {
        "dockerfile": '''FROM python:3.11-slim

WORKDIR /app

# Asenna riippuvuudet ensin (cache-optiimointi)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Käytä ei-root-käyttäjää
RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser

# Kopioi sovellus
COPY --chown=appuser:appuser . .

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
''',
        "compose": '''version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 5s
      retries: 3

  redis:
    image: redis:7-alpine
    restart: unless-stopped
''',
    },
    "web-app": {
        "dockerfile": '''FROM python:3.11-slim

WORKDIR /app

# Asenna riippuvuudet
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Frontend-riippuvuudet
RUN if [ -f "package.json" ]; then \\
        apt-get update && apt-get install -y --no-install-recommends nodejs npm && \\
        npm ci --only=production; \\
    fi

# Käytä ei-root-käyttäjää
RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser

COPY --chown=appuser:appuser . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
''',
        "compose": '''version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
    depends_on:
      - db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
''',
    },
    "cli": {
        "dockerfile": '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser

COPY --chown=appuser:appuser . .

ENTRYPOINT ["python", "cli.py"]
''',
        "compose": '''version: "3.8"

services:
  app:
    build: .
    volumes:
      - .:/app
    working_dir: /app
    entrypoint: ["python", "cli.py"]
    environment:
      - PYTHONUNBUFFERED=1
''',
    },
    "default": {
        "dockerfile": '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser

COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["python", "app.py"]
''',
        "compose": '''version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    restart: unless-stopped
''',
    },
}


# GitHub Actions -workflow-mallit
GITHUB_WORKFLOW_TEMPLATES: dict[str, str] = {
    "ci-cd": '''name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest --cov=agents --cov-report=xml --cov-report=term-missing

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run linter
        run: |
          pip install flake8
          flake8 .

  build-and-push:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - name: Login to container registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
''',
    "linting": '''name: Linting

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install linting tools
        run: |
          pip install flake8 black isort
      - name: Run flake8
        run: flake8 .
      - name: Check formatting
        run: |
          black --check . || true
          isort --check . || true
''',
    "security": '''name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install security tools
        run: pip install bandit safety
      - name: Run Bandit
        run: bandit -r . -ll
      - name: Check dependencies
        run: safety check
''',
}


# Deploy-mallit eri strategioille
DEPLOYMENT_TEMPLATES: dict[str, dict[str, Any]] = {
    "docker-swarm": {
        "strategy": "docker-swarm",
        "config": "version: \"3.8\"\n\nservices:\n  app:\n    image: {image}\n    deploy:\n      replicas: {replicas}\n      restart_policy:\n        condition: on-failure\n    ports:\n      - \"{port}:{port}\"",
        "description": "Docker Swarm klusteriin asennus",
    },
    "kubernetes": {
        "strategy": "kubernetes",
        "config": "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: {name}\nspec:\n  replicas: {replicas}\n  selector:\n    matchLabels:\n      app: {name}\n  template:\n    metadata:\n      labels:\n        app: {name}\n    spec:\n      containers:\n      - name: {name}\n        image: {image}\n        ports:\n        - containerPort: {port}\n---\napiVersion: v1\nkind: Service\nmetadata:\n  name: {name}-service\ntype: LoadBalancer\nspec:\n  ports:\n  - port: {port}\n    targetPort: {port}\n  selector:\n    app: {name}",
        "description": "Kubernetes deployausta varten",
    },
    "aws-ecs": {
        "strategy": "aws-ecs",
        "config": "Resources:\n  AppService:\n    Type: AWS::ECS::Service\n    Properties:\n      Cluster: !Ref ECSCluster\n      TaskDefinition: !Ref TaskDefinition\n      DesiredCount: {replicas}\n      LoadBalancers:\n        - ContainerName: {name}\n          ContainerPort: {port}\n          TargetGroupArn: !Ref TargetGroup",
        "description": "AWS ECS -klusteriin asennus",
    },
    "static": {
        "strategy": "static-hosting",
        "config": "# Deploy static files to:\n# - AWS S3 + CloudFront\n# - Vercel\n# - Netlify\n# - GitHub Pages\n\n# Build command:\n{build_cmd}\n\n# Publish directory:\n{publish_dir}",
        "description": "Staattisten tiedostojen hostaukseen",
    },
}


class DockerAgentInput(AgentInput):
    """DockerAgentin syöte."""

    project_type: str = Field(
        default="python-api",
        description="Projekti-tyyppi (python-api, web-app, cli, default).",
    )
    output_path: str = Field(
        default=".",
        description="Polku jonne Dockerfile ja docker-compose.yaml luodaan.",
    )
    expose_port: int = Field(default=8000, description="Sisäänotettu portti.")


class DockerAgentOutput(AgentOutput):
    """DockerAgentin tuloste."""

    dockerfile_path: str = Field(default="", description="Luodun Dockerfile-polku.")
    compose_path: str = Field(default="", description="Luodun docker-compose.yaml-polku.")
    template_used: str = Field(default="default", description="Käytetty mallin nimi.")
    security_score: float = Field(default=100.0, description="Turvallisuuspisteet Dockerfilelle (0-100).")
    recommendations: list[str] = Field(default_factory=list, description="Suositukset parannuksiin.")


class CICDAgentInput(AgentInput):
    """CI-CDAgentin syöte."""

    workflows: list[str] = Field(
        default_factory=lambda: ["ci-cd", "linting", "security"],
        description="Luotavat workflow-tiedostot (ci-cd, linting, security).",
    )
    output_path: str = Field(default=".github/workflows", description="GitHub Actions -kansio polussa.")
    python_versions: list[str] = Field(default_factory=lambda: ["3.11", "3.12"], description="Testattavat Python-versiot.")


class CICDAgentOutput(AgentOutput):
    """CI-CDAgentin tuloste."""

    created_workflows: list[str] = Field(default_factory=list, description="Luodut workflow-tiedostot.")
    total_workflows: int = Field(default=0, description="Workflow-tiedostojen yhteismäärä.")


class InfrastructureAgentInput(AgentInput):
    """InfrastructureAgentin syöte."""

    project_path: str = Field(default=".", description="Projektipolku analysoitavaksi.")
    requirements_file: str = Field(default="requirements.txt", description="Riippuvuustiedoston nimi.")
    check_docker: bool = Field(default=True, description="Tarkista Docker- ja infra-tiedostot.")


class InfrastructureAgentOutput(AgentOutput):
    """InfrastructureAgentin tuloste."""

    dependencies: list[dict[str, Any]] = Field(default_factory=list, description="Projektin riippuvuudet.")
    infrastructure_files: list[str] = Field(default_factory=list, description="Löydetyt infra-tiedostot.")
    recommendations: list[str] = Field(default_factory=list, description="Infrastruktuurin parannussuositukset.")
    complexity_score: float = Field(default=50.0, description="Infrastruktiikan monimutaisuuspisteet (0-100).")


class DeploymentAgentInput(AgentInput):
    """DeploymentAgentin syöte."""

    strategy: str = Field(
        default="docker-swarm",
        description="Deploy-strategia (docker-swarm, kubernetes, aws-ecs, static).",
    )
    project_name: str = Field(default="app", description="Projektin nimi.")
    image_name: str = Field(default="app:latest", description="Docker-kuvan nimi.")
    port: int = Field(default=8000, description=" Palvelimen portti.")
    replicas: int = Field(default=1, description=" Replikoitu määrä.")
    environment: str = Field(default="production", description="Deploy-ympäristö (development, staging, production).")
    output_path: str = Field(default=".", description="Polku deploy-konfigitiedostoon.")


class DeploymentAgentOutput(AgentOutput):
    """DeploymentAgentin tuloste."""

    strategy: str = Field(default="", description="Käytetty deploy-strategia.")
    config_path: str = Field(default="", description="Luodun konfig-tiedoston polku.")
    environment: str = Field(default="", description="Deploy-ympäristö.")
    config_content: str = Field(default="", description="Generoitu konfiguraatio.")
    deployment_steps: list[str] = Field(default_factory=list, description="Deployausvaiheiden seloste.")


class DockerAgent(BaseAgent):
    """
    DockerAgent luo Docker- ja docker-compose.yaml-mallit projektille.

    Tukee projekti-tyyppejä: python-api, web-app, cli, default.

    Usage:
        agent = DockerAgent()
        result = agent.run("Luo Docker-tiedostot", project_type="python-api")
    """

    agent_type: str = "docker"
    input_schema = DockerAgentInput
    output_schema = DockerAgentOutput

    def _generate_dockerfile(self, project_type: str, expose_port: int) -> str:
        """Generoi Dockerfile-mallin projekti-tyypin perusteella."""
        templates = COMPOSE_TEMPLATES
        if project_type in templates:
            content = templates[project_type]["dockerfile"]
        else:
            content = templates["default"]["dockerfile"]

        # Korvaa portti paikanpidon
        content = content.replace("8000", str(expose_port))
        return content

    def _generate_compose(self, project_type: str) -> str:
        """Generoi docker-compose.yaml-mallin."""
        templates = COMPOSE_TEMPLATES
        if project_type in templates:
            return templates[project_type]["compose"]
        return templates["default"]["compose"]

    def _evaluate_dockerfile_security(self, dockerfile_content: str) -> tuple[float, list[str]]:
        """Arvioi Dockerfile-turvallisuuden pisteet ja anna suositukset."""
        score = 100.0
        recs: list[str] = []

        issues = [
            (r"USER\s+root", "Käytetään root-käyttäjää", -20),
            (r"ADD\s+", "Käytetään ADD-komentoa", -5),
            (r"chmod\s+-R\s+777", "Liian laaja chmod 777", -15),
            (r"EXPOSE\s+22", "SSH-puhelin avattu", -10),
            (r"curl.*\|\s*sh", "curl|sh putki", -15),
            (r"apt-get.*install.*[^-]-[^-]", "Puuttuu --no-install-recommends", -5),
            (r"--no-cache-dir\s*$", "Cache-hakemisto", -0),
        ]

        for pattern, msg, penalty in issues:
            if re.search(pattern, dockerfile_content, re.IGNORECASE):
                score += penalty
                if penalty < 0:
                    recs.append(msg)

        # Positiiviset tarkistukset
        if re.search(r"HEALTHCHECK", dockerfile_content, re.IGNORECASE):
            score += 5
        else:
            recs.append("Lisää HEALTHCHECK")
            score -= 5

        if re.search(r"USER\s+(?!root)", dockerfile_content, re.IGNORECASE):
            score += 5
        else:
            recs.append("Käytä ei-root-käyttäjää")
            score -= 5

        score = max(0.0, min(100.0, score))
        return score, recs

    def _run(self, input_data: DockerAgentInput) -> DockerAgentOutput:
        """DockerAgentin päälogiika."""
        project_type = input_data.project_type
        output_path = Path(input_data.output_path)
        expose_port = input_data.expose_port

        # 1. Generoi tiedostot
        dockerfile_content = self._generate_dockerfile(project_type, expose_port)
        compose_content = self._generate_compose(project_type)

        # 2. Arvioi turvallisuus
        security_score, recommendations = self._evaluate_dockerfile_security(dockerfile_content)

        # 3. Kirjoita tiedostot (jos output_path on kirjoitettavissa)
        dockerfile_path = ""
        compose_path = ""

        try:
            output_path.mkdir(parents=True, exist_ok=True)
            dockerfile_path = str(output_path / "Dockerfile")
            compose_path = str(output_path / "docker-compose.yaml")
            (output_path / "Dockerfile").write_text(dockerfile_content, encoding="utf-8")
            (output_path / "docker-compose.yaml").write_text(compose_content, encoding="utf-8")
        except (OSError, PermissionError):
            # Ei voida kirjoittaa — palauta sisältö kyseisesti
            pass

        template_used = project_type if project_type in COMPOSE_TEMPLATES else "default"

        return DockerAgentOutput(
            success=True,
            result={"dockerfile_path": dockerfile_path, "compose_path": compose_path},
            message=f"Docker-tiedostot luodaan ({template_used}-malli, portti {expose_port}). Turvallisuuspisteet: {security_score}/100.",
            agent_type=self.agent_type,
            dockerfile_path=dockerfile_path,
            compose_path=compose_path,
            template_used=template_used,
            security_score=security_score,
            recommendations=recommendations,
        )


class CI_CDAgent(BaseAgent):
    """
    CI-CDAgent luo GitHub Actions -workflowit projektille.

    Tukee workflow-tyyppejä: ci-cd, linting, security.

    Usage:
        agent = CI_CDAgent()
        result = agent.run("Luo CI/CD -pipeline", workflows=["ci-cd", "linting"])
    """

    agent_type: str = "ci_cd"
    input_schema = CICDAgentInput
    output_schema = CICDAgentOutput

    def _generate_workflow(self, workflow_type: str, python_versions: list[str]) -> str:
        """Generoi GitHub Actions -workflowin."""
        template = GITHUB_WORKFLOW_TEMPLATES.get(workflow_type, GITHUB_WORKFLOW_TEMPLATES["ci-cd"])

        # Korvaa Python-versiot matriisin
        if python_versions and "python-version:" in template:
            versions_str = ", ".join(f'"{v}"' for v in python_versions)
            template = re.sub(
                r'python-version: \[[^\]]+\]',
                f'python-version: [{versions_str}]',
                template,
            )

        return template

    def _run(self, input_data: CICDAgentInput) -> CICDAgentOutput:
        """CI-CDAgentin päälogiika."""
        output_path = Path(input_data.output_path)
        python_versions = input_data.python_versions
        created_workflows: list[str] = []

        for workflow_type in input_data.workflows:
            content = self._generate_workflow(workflow_type, python_versions)
            filename = f"{workflow_type}.yml"

            try:
                output_path.mkdir(parents=True, exist_ok=True)
                workflow_path = output_path / filename
                workflow_path.write_text(content, encoding="utf-8")
                created_workflows.append(str(workflow_path))
            except (OSError, PermissionError):
                # Ei voida kirjoittaa — palauta kyseisessä
                pass

        return CICDAgentOutput(
            success=True,
            result={"created_workflows": created_workflows},
            message=f"Luodaan {len(created_workflows)} GitHub Actions -workflowia.",
            agent_type=self.agent_type,
            created_workflows=created_workflows,
            total_workflows=len(created_workflows),
        )


class InfrastructureAgent(BaseAgent):
    """
    InfrastructureAgent analysoi projektin infrastruktiurin ja suosittelee parannuksia.

    Usage:
        agent = InfrastructureAgent()
        result = agent.run("Analysoi infra", project_path=".")
    """

    agent_type: str = "infrastructure"
    input_schema = InfrastructureAgentInput
    output_schema = InfrastructureAgentOutput

    # Etsittävät infra-tiedostot
    INFRA_FILES = [
        "Dockerfile",
        "docker-compose.yaml",
        "docker-compose.yml",
        ".dockerignore",
        "Makefile",
        "terraform/*.tf",
        "*.tf",
        ".github/workflows/*.yml",
        ".github/workflows/*.yaml",
        "requirements.txt",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
    ]

    # Parannussuositukset riippuvuuksiin
    INFRA_RECOMMENDATIONS: dict[str, list[str]] = {
        "Dockerfile": [
            "Käytä --no-cache-dir pip-asennuksessa",
            "Vältä root-käyttäjää",
            "Lisää HEALTHCHECK",
            "Käytä monivaiheista rakentamista (multi-stage build)",
        ],
        ".github/workflows": [
            "Lisää fail-fast matrix-osa",
            "Varmista että coverage lähetetään CI:stä",
            "Lisää security-scanning workflow",
        ],
        "requirements.txt": [
            "Lukitse tarkat versiot tuotantoympäristössä (==)",
            "Tarkista haavoittuvuudet säännöllisesti (pip-audit)",
        ],
    }

    def _parse_requirements(self, filepath: Path) -> list[dict[str, Any]]:
        """Parse requirements.txt- tai vastaavan."""
        deps: list[dict[str, Any]] = []
        if not filepath.exists():
            return deps

        content = filepath.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r"^([a-zA-Z0-9_-]+)\s*(.*)$", line)
            if match:
                deps.append({"name": match.group(1).lower(), "version_spec": match.group(2)})

        return deps

    def _find_infra_files(self, project_path: Path) -> list[str]:
        """Etsi infra- ja deploy-tiedostot projektista."""
        found: list[str] = []

        for pattern in self.INFRA_FILES:
            # Käytetään glob-kuvioita
            for f in project_path.glob(pattern):
                if f.is_file() and ".venv" not in str(f) and "__pycache__" not in str(f):
                    found.append(str(f.relative_to(project_path)))

        # Tarkista myös .github/workflows
        workflows_dir = project_path / ".github" / "workflows"
        if workflows_dir.exists():
            for wf in workflows_dir.glob("*.yml"):
                found.append(str(wf.relative_to(project_path)))
            for wf in workflows_dir.glob("*.yaml"):
                found.append(str(wf.relative_to(project_path)))

        # Tarkista terraform
        for tf in project_path.glob("**/*.tf"):
            if ".venv" not in str(tf):
                found.append(str(tf.relative_to(project_path)))

        return sorted(set(found))

    def _generate_recommendations(self, infra_files: list[str]) -> list[str]:
        """Generoi parannussuositukset löydetyistä tiedostoista."""
        recs: list[str] = []

        has_dockerfile = any("Dockerfile" in f for f in infra_files)
        has_workflow = any(".github/workflows" in f for f in infra_files)
        has_requirements = any("requirements.txt" in f for f in infra_files)
        has_dockerignore = any(".dockerignore" in f for f in infra_files)

        if has_dockerfile:
            recs.extend(self.INFRA_RECOMMENDATIONS["Dockerfile"])
        else:
            recs.append("Lisää Dockerfile projektin containerisointia varten")

        if not has_dockerignore:
            recs.append("Lisää .dockerignore turvallisuuksia varten")

        if has_workflow:
            recs.extend(self.INFRA_RECOMMENDATIONS[".github/workflows"])
        else:
            recs.append("Lisää GitHub Actions -workflow CI/CD:a varten")

        if has_requirements:
            recs.extend(self.INFRA_RECOMMENDATIONS["requirements.txt"])

        return recs

    def _calculate_complexity(self, infra_files: list[str], deps: list[dict]) -> float:
        """Laskee infrastruktiikan monimutaisuuspisteet."""
        score = 50.0  # Oletus

        # Enemmän tiedostoja = monimutkaisempi
        score += len(infra_files) * 2

        # Riippuvuuksia useampi = monimutkaisempi
        score += min(len(deps) * 0.5, 20)

        # Olemassa oleva infra laskee pisteet
        if any("Dockerfile" in f for f in infra_files):
            score += 5
        if any(".github" in f for f in infra_files):
            score += 5

        score = max(0.0, min(100.0, score))
        return round(score, 1)

    def _run(self, input_data: InfrastructureAgentInput) -> InfrastructureAgentOutput:
        """InfrastructureAgentin päälogiika."""
        project_path = Path(input_data.project_path)
        req_file = project_path / input_data.requirements_file

        # 1. Analysoi riippuvuudet
        dependencies = self._parse_requirements(req_file)

        # 2. Etsi infra-tiedostot
        infrastructure_files: list[str] = []
        if input_data.check_docker:
            infrastructure_files = self._find_infra_files(project_path)

        # 3. Generoi suositukset
        recommendations = self._generate_recommendations(infrastructure_files)

        # 4. Laske monimutkaisuus
        complexity_score = self._calculate_complexity(infrastructure_files, dependencies)

        return InfrastructureAgentOutput(
            success=True,
            result={"infra_files": len(infrastructure_files), "deps": len(dependencies)},
            message=f"Infra-analyysi valmis: {len(infrastructure_files)} tiedostoa, {len(dependencies)} riippuvuutta.",
            agent_type=self.agent_type,
            dependencies=dependencies,
            infrastructure_files=infrastructure_files,
            recommendations=recommendations,
            complexity_score=complexity_score,
        )


class DeploymentAgent(BaseAgent):
    """
    DeploymentAgent suunnittelee deploy-strategian ja -ympäristöt projektille.

    Tukee strategioita: docker-swarm, kubernetes, aws-ecs, static.

    Usage:
        agent = DeploymentAgent()
        result = agent.run("Suunnittele deploy", strategy="kubernetes", project_name="myapp")
    """

    agent_type: str = "deployment"
    input_schema = DeploymentAgentInput
    output_schema = DeploymentAgentOutput

    def _generate_deployment_config(self, strategy: str, project_name: str, image_name: str,
                                     port: int, replicas: int) -> str:
        """Generoi deploy-konfiguraation valitulle strategialle."""
        template = DEPLOYMENT_TEMPLATES.get(strategy, DEPLOYMENT_TEMPLATES["docker-swarm"])
        return template["config"].format(
            image=image_name,
            name=project_name,
            port=port,
            replicas=replicas,
            build_cmd="npm run build",
            publish_dir="dist/",
        )

    def _generate_deployment_steps(self, strategy: str, environment: str) -> list[str]:
        """Generoi deployausvaiheiden selosteen."""
        steps = [
            f"1. Buildaa Docker-kuva: docker build -t {environment} .",
        ]

        if strategy == "docker-swarm":
            steps.extend([
                "2. Työnnä kuva: docker push registry.example.com/app",
                "3. Deployaa: docker stack deploy -c deploy.yml app-stack",
                "4. Tarkista: docker stack services app-stack",
            ])
        elif strategy == "kubernetes":
            steps.extend([
                "2. Työnnä kuva: docker push registry.example.com/app",
                "3. Deployaa: kubectl apply -f deploy.yaml",
                "4. Tarkista: kubectl get pods,svc",
            ])
        elif strategy == "aws-ecs":
            steps.extend([
                "2. Työnnä kuva AWS ECR:iin: aws ecr get-login-password | docker login",
                "3. Deployaa CloudFormation: aws cloudformation deploy",
                "4. Tarkista: aws ecs list-services",
            ])
        else:  # static
            steps.extend([
                "2. Buildaa frontend: npm run build",
                "3. Työnnä tiedostot: aws s3 sync dist/ s3://bucket-name --delete",
                "4. Invalidoi CDN: aws cloudfront create-invalidation",
            ])

        return steps

    def _run(self, input_data: DeploymentAgentInput) -> DeploymentAgentOutput:
        """DeploymentAgentin päälogiika."""
        strategy = input_data.strategy
        project_name = input_data.project_name
        image_name = input_data.image_name
        port = input_data.port
        replicas = input_data.replicas
        environment = input_data.environment
        output_path = Path(input_data.output_path)

        # 1. Generoi konfiguraatio
        template_info = DEPLOYMENT_TEMPLATES.get(strategy, DEPLOYMENT_TEMPLATES["docker-swarm"])
        config_content = self._generate_deployment_config(
            strategy, project_name, image_name, port, replicas
        )

        # 2. Kirjoita tiedosto (jos mahdollista)
        config_path = ""
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            filename = f"deploy-{strategy}.yaml" if strategy != "static" else f"deploy-{strategy}.txt"
            config_path = str(output_path / filename)
            (output_path / filename).write_text(config_content, encoding="utf-8")
        except (OSError, PermissionError):
            pass

        # 3. Generoi vaiheet
        deployment_steps = self._generate_deployment_steps(strategy, environment)

        return DeploymentAgentOutput(
            success=True,
            result={"strategy": strategy, "config_path": config_path},
            message=f"Deploy-suunnitelma luoda (strategia: {strategy}, ympäristö: {environment}).",
            agent_type=self.agent_type,
            strategy=strategy,
            config_path=config_path,
            environment=environment,
            config_content=config_content,
            deployment_steps=deployment_steps,
        )


__all__ = [
    "DockerAgent",
    "DockerAgentInput",
    "DockerAgentOutput",
    "CI_CDAgent",
    "CICDAgentInput",
    "CICDAgentOutput",
    "InfrastructureAgent",
    "InfrastructureAgentInput",
    "InfrastructureAgentOutput",
    "DeploymentAgent",
    "DeploymentAgentInput",
    "DeploymentAgentOutput",
    "COMPOSE_TEMPLATES",
    "GITHUB_WORKFLOW_TEMPLATES",
    "DEPLOYMENT_TEMPLATES",
]
