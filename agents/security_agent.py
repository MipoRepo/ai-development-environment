"""
SecurityAgent-moduuli (M6) — projektin turvallisuudentarkastus.

Sisältää viisi agenttia:
- SecurityReviewAgent: tarkistaa turvallisuusongelmat koodissa.
- SASTAgent: AST-pohjainen staattinen koodianalyysi.
- DependencySecurityAgent: tarkistaa riippuvuudet.
- SecretsAgent: etsii salaisuudet (avaimet, salasanat).
- ContainerSecurityAgent: tarkistaa Docker/Dockerfile-turvallisuuden.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


# Turvallisuusmalleja regexilla
SECURITY_PATTERNS: list[dict[str, str]] = [
    {"name": "eval", "pattern": r"\beval\s*\(", "severity": "critical",
     "description": "eval() suorittaa mielivalallista koodia"},
    {"name": "exec", "pattern": r"\bexec\s*\(", "severity": "critical",
     "description": "exec() suorittaa mielivalallista koodia"},
    {"name": "shell_true", "pattern": r"shell\s*=\s*True", "severity": "high",
     "description": "shell=True altistaa komennon injektiolle"},
    {"name": "pickle_loads", "pattern": r"pickle\.loads?\s*\(", "severity": "high",
     "description": "pickle voi suorittaa mielivalallista koodia purettaessaan"},
    {"name": "hardcoded_password", "pattern": r"password\s*=\s*['\"][^'\"]{3,}['\"]", "severity": "critical",
     "description": "Kiinteä salasana koodissa"},
    {"name": "hardcoded_secret", "pattern": r"secret\s*=\s*['\"][^'\"]{3,}['\"]", "severity": "high",
     "description": "Kiinteä salaisuus koodissa"},
    {"name": "hardcoded_api_key", "pattern": r"api[_-]?key\s*=\s*['\"][a-zA-Z0-9_-]{10,}['\"]", "severity": "critical",
     "description": "Kiinteä API-avain koodissa"},
    {"name": "subprocess_shell", "pattern": r"os\.system\s*\(", "severity": "high",
     "description": "os.system() altistaa komennon injektiolle — käytä subprocessia"},
    {"name": "sql_injection_risk", "pattern": r"execute\s*\([^,]*\+|execute\s*\([^,]*%\s*\(", "severity": "high",
     "description": "SQL-injektiota voidaan: merkkijonoketjut SQL-lauseissa"},
    {"name": "http_not_https", "pattern": r"https?://(?!localhost|127\.0\.0\.1)[^'\"\\s]+", "severity": "low",
     "description": "Käytetään HTTP-versiota — HTTPS suositaan"},
    {"name": "unsafe_yaml", "pattern": r"yaml\.load\s*\([^)]*[^)]*Loader\s*=", "severity": "high",
     "description": "yaml.load ilman SafeLoaderia voi suorittaa koodia"},
]


class SecurityReviewInput(AgentInput):
    """SecurityReviewAgentin syöte."""

    file_path: Optional[str] = Field(default=None, description="Tiedosto tai kansio tarkistettavaksi.")
    code: str = Field(default="", description="Analysoitava koodi suoraan.")
    scan_all: bool = Field(default=False, description="Skannaa koko projekti.")
    severity_threshold: str = Field(default="low", description="Vähimmäisvaikutus.")


class SecurityReviewOutput(AgentOutput):
    """SecurityReviewAgentin tuloste."""

    vulnerabilities: list[dict[str, Any]] = Field(default_factory=list, description="Löydetyt haavoittuvuudet.")
    vulnerability_count: int = Field(default=0, description="Haavoittuvuuksien lukumäärä.")
    severity_counts: dict[str, int] = Field(default_factory=dict, description="Vakaudet lukumäärinä.")
    score: float = Field(default=100.0, description="Turvallisuuspisteet (0-100).")


class SASTInput(AgentInput):
    """SASTAgentin syöte."""

    file_path: Optional[str] = Field(default=None, description="Python-tiedosto analysoitavaksi.")
    code: str = Field(default="", description="Analysoitava koodi.")
    rules: Optional[list[str]] = Field(default=None, description="Käytettävät säännöt.")


class SASTOutput(AgentOutput):
    """SASTAgentin tuloste."""

    findings: list[dict[str, Any]] = Field(default_factory=list, description="Löydetyt ongelmit.")
    finding_count: int = Field(default=0, description="Ongelmien lukumäärä.")
    ast_analysis: dict[str, Any] = Field(default_factory=dict, description="AST-analyysin tulos.")


class DependencySecurityInput(AgentInput):
    """DependencySecurityAgentin syöte."""

    project_path: str = Field(default=".", description="Projektipolku.")
    requirements_file: str = Field(default="requirements.txt", description="Riippuvuustiedoston nimi.")
    check_updates: bool = Field(default=True, description="Tarkista päivitettävät paketti.")


class DependencySecurityOutput(AgentOutput):
    """DependencySecurityAgentin tuloste."""

    dependencies: list[dict[str, Any]] = Field(default_factory=list, description="Riippuvuudet.")
    vulnerable_count: int = Field(default=0, description="Haavoittuvuuksien lukumäärä.")
    outdated_count: int = Field(default=0, description="Vanhentuneiden pakettien lukumäärä.")
    recommendations: list[str] = Field(default_factory=list, description="Suositukset.")


class SecretsInput(AgentInput):
    """SecretsAgentin syöte."""

    file_path: Optional[str] = Field(default=None, description="Tiedosto tai kansio scanata.")
    project_path: str = Field(default=".", description="Projektipolku skannatavaksi.")
    scan_all: bool = Field(default=False, description="Skannaa koko projekti.")
    code: str = Field(default="", description="Koodi suoraan.")


class SecretsOutput(AgentOutput):
    """SecretsAgentin tuloste."""

    secrets_found: list[dict[str, Any]] = Field(default_factory=list, description="Löydetyt salaisuudet.")
    secret_count: int = Field(default=0, description="Salaisuuksien lukumäärä.")
    scanned_files: int = Field(default=0, description="Skannatujen tiedostojen lukumäärä.")
    patterns_matched: list[str] = Field(default_factory=list, description="Osumaksiin tulleet malleja.")


class ContainerSecurityInput(AgentInput):
    """ContainerSecurityAgentin syöte."""

    dockerfile_path: str = Field(default="Dockerfile", description="Dockerfile-polku.")
    project_path: str = Field(default=".", description="Projektipolku.")


class ContainerSecurityOutput(AgentOutput):
    """ContainerSecurityAgentin tuloste."""

    issues: list[str] = Field(default_factory=list, description="Löydetyt ongelmat.")
    score: float = Field(default=100.0, description="Pisteet (0-100).")


class SecurityReviewAgent(BaseAgent):
    """
    SecurityReviewAgent tarkistaa turvallisuusongelmat koodissa.

    Usage:
        agent = SecurityReviewAgent()
        result = agent.run("Tarkista tämä tiedosto", file_path="src/main.py")
    """

    agent_type: str = "security_review"
    input_schema = SecurityReviewInput
    output_schema = SecurityReviewOutput

    def _scan_code(self, code: str, file_path: str = "<buffer>") -> list[dict[str, Any]]:
        """Skannaa koodin turvallisuuskaavoilla."""
        vulnerabilities: list[dict[str, Any]] = []
        for pattern_info in SECURITY_PATTERNS:
            matches = re.finditer(pattern_info["pattern"], code, re.IGNORECASE)
            for match in matches:
                line_no = code[:match.start()].count("\n") + 1
                vulnerabilities.append({
                    "type": pattern_info["name"],
                    "description": pattern_info["description"],
                    "line": line_no,
                    "severity": pattern_info["severity"],
                    "file": file_path,
                    "code_snippet": match.group(0)[:100],
                })
        return vulnerabilities

    def _scan_file(self, filepath: Path) -> list[dict[str, Any]]:
        """Skannaa yksittäisen tiedoston."""
        try:
            code = filepath.read_text(encoding="utf-8")
            return self._scan_code(code, str(filepath))
        except (OSError, UnicodeDecodeError) as e:
            return [{"type": "error", "description": str(e), "line": 0, "severity": "low", "file": str(filepath)}]

    def _scan_directory(self, dirpath: Path, extensions: Optional[list[str]] = None) -> tuple[list[dict[str, Any]], int]:
        """Skannaa koko kansion."""
        extensions = extensions or [".py", ".js", ".yaml", ".yml", ".json", ".env"]
        all_vulns: list[dict[str, Any]] = []
        file_count = 0
        skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv"}

        for root, dirs, files in os.walk(dirpath):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for fname in files:
                if any(fname.endswith(ext) or fname == ".env" for ext in extensions):
                    fpath = Path(root) / fname
                    vulns = self._scan_file(fpath)
                    all_vulns.extend(v for v in vulns if v["type"] != "error")
                    file_count += 1

        return all_vulns, file_count

    def _run(self, input_data: SecurityReviewInput) -> SecurityReviewOutput:
        """SecurityReviewAgentin päälogiikka."""
        file_path = input_data.file_path
        code = input_data.code
        vulnerabilities: list[dict[str, Any]] = []

        # 1. Analysoi koodi tai tiedosto
        if code:
            vulnerabilities = self._scan_code(code, input_data.file_path or "<buffer>")
        elif file_path:
            path = Path(file_path)
            if path.is_file():
                vulnerabilities = self._scan_file(path)
            elif path.is_dir():
                vulnerabilities, _ = self._scan_directory(path)
        elif input_data.scan_all:
            vulnerabilities, _ = self._scan_directory(Path(input_data.project_path))
        elif input_data.context and "code" in input_data.context:
            code = input_data.context["code"]
            vulnerabilities = self._scan_code(code)

        # 2. Suodata vakauden vähemmäisestä
        sev_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        threshold = sev_order.get(input_data.severity_threshold, 1)
        filtered = [v for v in vulnerabilities if sev_order.get(v["severity"], 0) >= threshold]

        # 3. Laske tilastot
        severity_counts: dict[str, int] = {}
        for v in filtered:
            sev = v["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        # 4. Laske pisteet
        penalties = {"critical": 20, "high": 12, "medium": 6, "low": 2}
        score = 100.0 - sum(penalties.get(v["severity"], 5) for v in filtered)
        score = max(0.0, score)

        return SecurityReviewOutput(
            success=True,
            result={"vulnerability_count": len(filtered), "score": score},
            message=f"Turvallisuustarkastus valmis: {len(filtered)} haavoittuvuutta, pisteet {score}/100.",
            agent_type=self.agent_type,
            vulnerabilities=filtered,
            vulnerability_count=len(filtered),
            severity_counts=severity_counts,
            score=score,
        )


class SASTAgent(BaseAgent):
    """
    SASTAgent suorittaa AST-pohjaisen staattisen koodin analysoinnin.

    Usage:
        agent = SASTAgent()
        result = agent.run("Analysoi koodi", code="eval('test')")
    """

    agent_type: str = "sast"
    input_schema = SASTInput
    output_schema = SASTOutput

    def _analyze_ast(self, tree: ast.AST, code: str) -> list[dict[str, Any]]:
        """AST-analyysi turvallisuusongelmille."""
        findings: list[dict[str, Any]] = []

        for node in ast.walk(tree):
            # eval/exec-kutsut
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id == "eval":
                        findings.append({
                            "type": "code_injection",
                            "line": node.lineno,
                            "message": "eval() suorittaa dynaamista koodia",
                            "severity": "critical",
                        })
                    elif node.func.id == "exec":
                        findings.append({
                            "type": "code_injection",
                            "line": node.lineno,
                            "message": "exec() suorittaa dynaamista koodia",
                            "severity": "critical",
                        })
                    elif node.func.id == "system":
                        findings.append({
                            "type": "command_injection",
                            "line": node.lineno,
                            "message": "os.system() altistaa komennon injektiolle",
                            "severity": "high",
                        })

            # Importit vaarujen avulla
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("pickle", "marshal", "ctypes"):
                        findings.append({
                            "type": "dangerous_import",
                            "line": node.lineno,
                            "message": f"Vaarallinen kirjasto: {alias.name}",
                            "severity": "medium",
                        })

        return findings

    def _analyze_source(self, code: str) -> dict[str, Any]:
        """Analysoi koodin AST:llä."""
        analysis: dict[str, Any] = {"functions": 0, "classes": 0, "imports": [], "complexity": 0}
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    analysis["functions"] += 1
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"] += 1
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                elif isinstance(node, ast.If):
                    analysis["complexity"] += 1
                elif isinstance(node, ast.For):
                    analysis["complexity"] += 1
        except SyntaxError:
            analysis["error"] = "Virheellinen syntaksi"
        return analysis

    def _run(self, input_data: SASTInput) -> SASTOutput:
        """SASTAgentin päälogiika."""
        code = input_data.code
        file_path = input_data.file_path

        # Lue tiedosto jos annettu
        if not code and file_path:
            path = Path(file_path)
            if path.exists():
                code = path.read_text(encoding="utf-8")

        if not code:
            return SASTOutput(
                success=False,
                result=None,
                message="Ei koodia analysoitavaksi.",
                agent_type=self.agent_type,
                findings=[],
                finding_count=0,
                ast_analysis={},
            )

        findings: list[dict[str, Any]] = []

        # AST-analyysi
        try:
            tree = ast.parse(code)
            findings = self._analyze_ast(tree, code)
        except SyntaxError as e:
            return SASTOutput(
                success=False,
                result=None,
                message=f"Syntaksivirhe: {e}",
                agent_type=self.agent_type,
                findings=[],
                finding_count=0,
                ast_analysis={"error": str(e)},
            )

        # AST-metriikit
        ast_analysis = self._analyze_source(code)

        return SASTOutput(
            success=True,
            result={"finding_count": len(findings), "complexity": ast_analysis.get("complexity", 0)},
            message=f"SAST-analyysi valmis: {len(findings)} havaintoa, monimutaisuus {ast_analysis.get('complexity', 0)}.",
            agent_type=self.agent_type,
            findings=findings,
            finding_count=len(findings),
            ast_analysis=ast_analysis,
        )


class DependencySecurityAgent(BaseAgent):
    """
    DependencySecurityAgent tarkistaa projektin riippuvuudet.

    Usage:
        agent = DependencySecurityAgent()
        result = agent.run("Tarkista riippuvuudet", project_path=".")
    """

    agent_type: str = "dependency_security"
    input_schema = DependencySecurityInput
    output_schema = DependencySecurityOutput

    # Tunnetut haavoittuvat paketit
    VULNERABLE_PACKAGES: dict[str, list[str]] = {
        "django": ["1.11.x", "2.2.x < 2.2.28", "3.2.x < 3.2.16", "4.0.x < 4.0.8"],
        "flask": ["< 2.2.5"],
        "requests": ["< 2.28.1"],
        "pyyaml": ["< 6.2"],
        "numpy": ["< 1.24.2"],
        "pillow": ["< 9.2.0"],
    }

    def _parse_requirements(self, filepath: Path) -> list[dict[str, str]]:
        """Parse requirements.txt- tai vastaavan."""
        deps: list[dict[str, str]] = []
        if not filepath.exists():
            return deps

        content = filepath.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Poimi nimi ja versio (esim. "pydantic>=2.0.0")
            match = re.match(r"^([a-zA-Z0-9_-]+)\s*(.*)$", line)
            if match:
                deps.append({"name": match.group(1).lower(), "version_spec": match.group(2)})

        return deps

    def _check_vulnerabilities(self, deps: list[dict[str, str]]) -> list[str]:
        """Tarkista haavoittuvuudet tunetuista paketeista."""
        vulnerable: list[str] = []
        dep_names = {d["name"] for d in deps}
        for pkg, vuln_versions in self.VULNERABLE_PACKAGES.items():
            if pkg.lower() in dep_names:
                vulnerable.append(f"Haavoittuva paketti: {pkg} ({', '.join(vuln_versions)})")
        return vulnerable

    def _run(self, input_data: DependencySecurityInput) -> DependencySecurityOutput:
        """DependencySecurityAgentin päälogiika."""
        project_path = Path(input_data.project_path)
        req_file = project_path / input_data.requirements_file

        # 1. Parse dependencies
        dependencies = self._parse_requirements(req_file)

        # 2. Tarkista haavoittuvuudet
        vulnerable = self._check_vulnerabilities(dependencies)

        # 3. Tarkista vanhentuneet paketit (jos mahdollista)
        outdated = []
        if input_data.check_updates:
            try:
                result = subprocess.run(
                    ["python", "-m", "pip", "list", "--outdated", "--format=json"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    import json as _json
                    outdated_data = _json.loads(result.stdout)
                    dep_names = {d["name"].lower() for d in dependencies}
                    for pkg in outdated_data:
                        if pkg["name"].lower() in dep_names:
                            outdated.append(pkg["name"])
            except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
                pass

        # 4. Suositukset
        recommendations: list[str] = []
        for v in vulnerable:
            recommendations.append(v)
        if outdated:
            recommendations.append(f"Päivitä vanhentuneet paketit: {', '.join(outdated[:5])}")
        if not dependencies:
            recommendations.append("Ei riippuvuustiedostoa löydy projektista.")

        return DependencySecurityOutput(
            success=True,
            result={"dependency_count": len(dependencies), "vulnerable_count": len(vulnerable)},
            message=f"Riippuvuustarkistus: {len(dependencies)} pakettia, {len(vulnerable)} haavoittuvuutta.",
            agent_type=self.agent_type,
            dependencies=dependencies,
            vulnerable_count=len(vulnerable),
            outdated_count=len(outdated),
            recommendations=recommendations,
        )


class SecretsAgent(BaseAgent):
    """
    SecretsAgent etsii salaisuudet koodista ja tiedostoista.

    Usage:
        agent = SecretsAgent()
        result = agent.run("Etsi salaisuudet", scan_all=True, project_path=".")
    """

    agent_type: str = "secrets"
    input_schema = SecretsInput
    output_schema = SecretsOutput

    # Salaisuusaltaat
    SECRET_PATTERNS: list[dict[str, str]] = [
        {"name": "aws_access_key", "pattern": r"AKIA[0-9A-Z]{16}", "description": "AWS Access Key"},
        {"name": "aws_secret", "pattern": r"aws_secret_access_key['\"]?\s*[:=]\s*['\"][^'\"]+['\"]", "description": "AWS Secret Access Key"},
        {"name": "github_token", "pattern": r"gh[pousr]_[A-Za-z0-9]+", "description": "GitHub Token"},
        {"name": "generic_api_key", "pattern": r"api[_-]?key\s*=\s*['\"][a-zA-Z0-9_-]{10,}['\"]", "description": "Generic API Key"},  # noqa: E501
        {"name": "bearer_token", "pattern": r"Bearer\s+[a-zA-Z0-9._-]+", "description": "Bearer Token"},
        {"name": "private_key", "pattern": r"-----BEGIN [A-Z ]+PRIVATE KEY-----", "description": "Private key"},
        {"name": "password_var", "pattern": r"password\s*=\s*['\"][a-zA-Z0-9!@#$%^&*()_]{4,}['\"]", "description": "Hardcoded password"},
    ]

    def _scan_text(self, text: str, filepath: str) -> list[dict[str, Any]]:
        """Skannaa teksti salaisuuksille."""
        found: list[dict[str, Any]] = []
        for pattern_info in self.SECRET_PATTERNS:
            for match in re.finditer(pattern_info["pattern"], text, re.IGNORECASE):
                line_no = text[:match.start()].count("\n") + 1
                found.append({
                    "type": pattern_info["name"],
                    "description": pattern_info["description"],
                    "line": line_no,
                    "file": filepath,
                    "match_preview": match.group(0)[:50],
                })
        return found

    def _scan_file(self, filepath: Path) -> list[dict[str, Any]]:
        """Skannaa tiedosto salaisuuksille."""
        try:
            text = filepath.read_text(encoding="utf-8", errors="replace")
            return self._scan_text(text, str(filepath))
        except (OSError, PermissionError):
            return []

    def _scan_directory(self, dirpath: Path) -> tuple[list[dict[str, Any]], int]:
        """Skannaa kansion kaikista tiedostoistaan."""
        all_secrets: list[dict[str, Any]] = []
        file_count = 0
        skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv"}
        relevant_exts = [".py", ".js", ".env", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini", ".conf"]

        for root, dirs, files in os.walk(dirpath):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for fname in files:
                if fname.endswith(".env") or any(fname.endswith(ext) for ext in relevant_exts) or fname == ".env":
                    fpath = Path(root) / fname
                    secrets = self._scan_file(fpath)
                    all_secrets.extend(secrets)
                    file_count += 1

        return all_secrets, file_count

    def _run(self, input_data: SecretsInput) -> SecretsOutput:
        """SecretsAgentin päälogiika."""
        code = input_data.code
        file_path = input_data.file_path
        secrets_found: list[dict[str, Any]] = []
        scanned_files = 0
        patterns_matched: list[str] = []

        # 1. Skannaa koodi suoraan
        if code:
            secrets_found = self._scan_text(code, file_path or "<buffer>")
            scanned_files = 1
            patterns_matched = list(set(s["type"] for s in secrets_found))

        # 2. Tai skannaa tiedosto/kansion
        elif file_path:
            path = Path(file_path)
            if path.is_file():
                secrets_found = self._scan_file(path)
                scanned_files = 1
                patterns_matched = list(set(s["type"] for s in secrets_found))
            elif path.is_dir():
                secrets_found, scanned_files = self._scan_directory(path)
                patterns_matched = list(set(s["type"] for s in secrets_found))

        # 3. Tai skannaa koko projekti
        if input_data.scan_all and not file_path:
            secrets_found, scanned_files = self._scan_directory(Path(input_data.project_path))
            patterns_matched = list(set(s["type"] for s in secrets_found))

        return SecretsOutput(
            success=True,
            result={"secret_count": len(secrets_found), "scanned_files": scanned_files},
            message=f"Salaisuusskanningi valmis: {len(secrets_found)} salaisuutta {scanned_files} tiedostosta.",
            agent_type=self.agent_type,
            secrets_found=secrets_found,
            secret_count=len(secrets_found),
            scanned_files=scanned_files,
            patterns_matched=patterns_matched,
        )


class ContainerSecurityAgent(BaseAgent):
    """
    ContainerSecurityAgent tarkistaa Docker/Dockerfile-turvallisuuden.

    Usage:
        agent = ContainerSecurityAgent()
        result = agent.run("Tarkista Dockerfile", dockerfile_path="Dockerfile")
    """

    agent_type: str = "container_security"
    input_schema = ContainerSecurityInput
    output_schema = ContainerSecurityOutput

    # Vaarat Dockerfile-käskyistä
    DANGEROUS_INSTRUCTIONS = [
        (r"^\s*USER\s+root", "Käytetään root-käyttäjää — vaihda ei-root:ksi"),
        (r"^\s*ADD\s+", "Käytetään ADD — wget/curl ehkäisevät sen sijaan"),
        (r"^\s*RUN\s+apt-get.*install.*-[a-zA-Z]", "Asennus järjestelmäpaketteja ilman --no-install-recommends"),
        (r"^\s*RUN\s+chmod\s+-R\s+777", "Liian laaja chmod 777"),
        (r"^\s*EXPOSE\s+22", "SSH-puhelin avattu — poista EXPOSE 22"),
        (r"^\s*RUN\s+curl.*\|\s*sh", "Suora putkimuodossa curl skripti — tarkista ensin"),
    ]

    # Hyvät käytännöt
    GOOD_PRACTICES = [
        (r"FROM\s+\S+:(?:alpine|slim|\d+\.\d+-slim)", "Käytetään kevyttä kantakuvaa"),
        (r"USER\s+(?!root)", "Käytetään ei-root-käyttäjää"),
        (r"--no-install-recommends", "Käytetään --no-install-recommends"),
        (r"HEALTHCHECK", "Määritelty terveyspalvelin tarkistus"),
    ]

    def _analyze_dockerfile(self, content: str) -> tuple[list[str], list[str], int]:
        """Analysoi Dockerfile-sisällön."""
        issues: list[str] = []
        good: list[str] = []
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            for pattern, msg in self.DANGEROUS_INSTRUCTIONS:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(f"Rivi {i}: {msg} (`{line.strip()[:50]}`)")

            for pattern, msg in self.GOOD_PRACTICES:
                if re.search(pattern, line, re.IGNORECASE):
                    good.append(msg)

        # Tarkista puuttuvat hyvät käytännöt
        has_user = any(re.search(r"^\s*USER\s+", line) for line in lines)
        has_from = any(re.search(r"^\s*FROM\s+", line, re.IGNORECASE) for line in lines)
        has_healthcheck = any(re.search(r"^\s*HEALTHCHECK", line, re.IGNORECASE) for line in lines)

        if not has_user:
            issues.append("USER-määrittely puuttuu — suositaan ei-root-käyttäjää")
        if not has_from:
            issues.append("FROM-määrittely puuttuu")
        if not has_healthcheck and has_from:
            issues.append("HEALTHCHECK puuttuu — lisää terveyspalvelin tarkistus")

        return issues, good, len(lines)

    def _run(self, input_data: ContainerSecurityInput) -> ContainerSecurityOutput:
        """ContainerSecurityAgentin päälogiika."""
        dockerfile_path = Path(input_data.dockerfile_path)
        project_path = Path(input_data.project_path)

        # 1. Etsi Dockerfile
        if not dockerfile_path.exists():
            dockerfile_path = project_path / "Dockerfile"
            if not dockerfile_path.exists():
                return ContainerSecurityOutput(
                    success=False,
                    result=None,
                    message="Dockerfile-tiedostoa ei löydy.",
                    agent_type=self.agent_type,
                    issues=["Dockerfile-tiedostoa ei löydy projektista"],
                    score=0.0,
                )

        # 2. Analysoi
        content = dockerfile_path.read_text(encoding="utf-8")
        issues, good_practices, line_count = self._analyze_dockerfile(content)

        # 3. Laske pisteet
        score = 100.0 - len(issues) * 10
        score = max(0.0, score)

        issues.extend(f"[HYVÄ] {gp}" for gp in good_practices)

        return ContainerSecurityOutput(
            success=True,
            result={"issue_count": len(issues), "line_count": line_count, "score": score},
            message=f"Dockerfile-analyysi valmis: {len(issues)} huomautusta, pisteet {score}/100.",
            agent_type=self.agent_type,
            issues=issues,
            score=score,
        )


__all__ = [
    "SecurityReviewAgent",
    "SecurityReviewInput",
    "SecurityReviewOutput",
    "SASTAgent",
    "SASTInput",
    "SASTOutput",
    "DependencySecurityAgent",
    "DependencySecurityInput",
    "DependencySecurityOutput",
    "SecretsAgent",
    "SecretsInput",
    "SecretsOutput",
    "ContainerSecurityAgent",
    "ContainerSecurityInput",
    "ContainerSecurityOutput",
]
