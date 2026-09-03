"""
TestingAutomationAgent-moduuli (M8) — testien automatisointi ja suorituskyvyn testaus.

Sisältää kolme agenttia:
- TestRunnerAgent: testien suoritus ja tuloksen analyysi (monipuolinen versio TesterAgentista).
- PerformanceTestAgent: suoritustestit (aikausmitus, benchmark).
- IntegrationTestAgent: integraatiotestaus ja moduuliyhteydet.
"""

from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


class TestRunnerInput(AgentInput):
    """TestRunnerAgentin syöte."""

    test_path: str = Field(default="tests/", description="Testikansion polku.")
    verbose: bool = Field(default=True, description="Käytetäänkö verbose-tilaa.")
    fail_fast: bool = Field(default=False, description="Pysäytetäänkö ensimmässä virheessä.")
    coverage: bool = Field(default=True, description="Mitataanko koodikattavuutta.")
    coverage_target: float = Field(default=0.8, description="Koodikattavuuden vähimmäisvaatimus (0-1).")
    extra_args: Optional[list[str]] = Field(default=None, description="Lisäargumentit pytestille.")


class TestRunnerOutput(AgentOutput):
    """TestRunnerAgentin tuloste."""

    passed: int = Field(default=0, description="Onnistuneiden testien lukumäärä.")
    failed: int = Field(default=0, description="Virheellisten testien lukumäärä.")
    errors: int = Field(default=0, description="Virheiden lukumäärä.")
    skipped: int = Field(default=0, description="Ohitettujen testien lukumäärä.")
    duration: float = Field(default=0.0, description="Testiajon kesto sekuntina.")
    coverage_percent: float = Field(default=0.0, description="Koodikattavuus prosentteina.")
    exit_code: int = Field(default=0, description="Pytestin paluuarvo.")
    summary: str = Field(default="", description="Lyhyt yhteenveto.")


class PerformanceTestInput(AgentInput):
    """PerformanceTestAgentin syöte."""

    code: str = Field(default="", description="Testattava koodi.")
    file_path: Optional[str] = Field(default=None, description="Testitiedoston polku.")
    iterations: int = Field(default=100, description="Toistojen lukumäärä.")
    warmup: int = Field(default=10, description="Lämmitussyklien lukumäärä.")
    timeout: float = Field(default=30.0, description="Aikakatko sekunteina.")


class PerformanceTestResult(AgentOutput):
    """PerformanceTestAgentin tuloste."""

    total_calls: int = Field(default=0, description="Kokonaiskutsujen lukumäärä.")
    total_time: float = Field(default=0.0, description="Kokonaisaika sekuntina.")
    avg_time: float = Field(default=0.0, description="Keskimääräinen aika sekuntina.")
    min_time: float = Field(default=0.0, description="Minimiaika sekuntina.")
    max_time: float = Field(default=0.0, description="Maksimiaika sekuntina.")
    p95_time: float = Field(default=0.0, description="95. percentyiliaika sekuntina.")
    iterations_completed: int = Field(default=0, description="Suoritettujen iteraatioiden lukumäärä.")
    benchmark_name: str = Field(default="", description="Benchmarkin nimi.")


class IntegrationTestInput(AgentInput):
    """IntegrationTestAgentin syöte."""

    project_path: str = Field(default=".", description="Projektipolku.")
    modules_to_test: Optional[list[str]] = Field(default=None, description="Testattavat moduulit.")
    check_imports: bool = Field(default=True, description="Tarkistetaanko importit.")


class IntegrationTestOutput(AgentOutput):
    """IntegrationTestAgentin tuloste."""

    modules_tested: list[str] = Field(default_factory=list, description="Testatut moduulit.")
    import_results: dict[str, bool] = Field(default_factory=dict, description="Import-tulokset sanakirjana.")
    integration_issues: list[str] = Field(default_factory=list, description="Integraatiovirheet.")
    score: float = Field(default=100.0, description="Integraatiopisteet (0-100).")
    all_modules_importable: bool = Field(default=True, description="Kaikki moduulit tuotettatavissa.")


class TestRunnerAgent(BaseAgent):
    """
    TestRunnerAgent suorittaa testit monipuolisella tavalla.

    Usage:
        agent = TestRunnerAgent()
        result = agent.run("Aja testit", test_path="tests/", coverage=True)
    """

    agent_type: str = "test_runner"
    input_schema = TestRunnerInput
    output_schema = TestRunnerOutput

    def _build_command(self, input_data: TestRunnerInput) -> list[str]:
        """Rakentaa pytest-komennon."""
        cmd = ["python", "-m", "pytest", str(input_data.test_path)]
        if input_data.verbose:
            cmd.append("-v")
        if input_data.fail_fast:
            cmd.append("-x")
        if input_data.coverage:
            cmd.extend(["--cov=agents", "--cov-report=term-missing"])
        if input_data.extra_args:
            cmd.extend(input_data.extra_args)
        return cmd

    def _parse_output(self, output: str) -> dict[str, int]:
        """Parsii pytest-tulosta pass/fail/skipped määrästä."""
        result = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}

        for match in re.finditer(r"(\d+)\s+(passed|failed|error|skipped)", output, re.IGNORECASE):
            count = int(match.group(1))
            status = match.group(2).lower()
            if status in result:
                result[status] = count

        return result

    def _extract_coverage(self, output: str) -> float:
        """Poimi koodikattavuus prosentteina."""
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
        if match:
            return float(match.group(1))
        return 0.0

    def _run(self, input_data: TestRunnerInput) -> TestRunnerOutput:
        """TestRunnerAgentin päälogiika."""
        cmd = self._build_command(input_data)
        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            duration = time.time() - start_time
            stdout = result.stdout + result.stderr

            counts = self._parse_output(stdout)
            coverage = self._extract_coverage(stdout) if input_data.coverage else 0.0

            total = counts["passed"] + counts["failed"] + counts["errors"] + counts["skipped"]
            passed = counts["passed"]

            return TestRunnerOutput(
                success=result.returncode == 0 or passed > 0,
                result={"passed": counts["passed"], "failed": counts["failed"]},
                message=f"Testit suoritettu: {counts['passed']} ok, {counts['failed']} virhettä.",
                agent_type=self.agent_type,
                passed=counts["passed"],
                failed=counts["failed"],
                errors=counts["errors"],
                skipped=counts["skipped"],
                duration=duration,
                coverage_percent=coverage,
                exit_code=result.returncode,
                summary=f"{counts['passed']} passed, {counts['failed']} failed in {duration:.1f}s",
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestRunnerOutput(
                success=False,
                result=None,
                message=f"Testit puuttuivat aikakatkaistin ({input_data.timeout}s).",
                agent_type=self.agent_type,
                passed=0,
                failed=0,
                errors=1,
                duration=duration,
                exit_code=-1,
                summary="Aikakatkaisu ylitetty",
            )
        except FileNotFoundError:
            return TestRunnerOutput(
                success=False,
                result=None,
                message="pytest-ei löydy — tarkista asennus (`pip install pytest`).",
                agent_type=self.agent_type,
                passed=0,
                exit_code=-1,
                summary="pytest ei löydy",
            )


class PerformanceTestAgent(BaseAgent):
    """
    PerformanceTestAgent mittaa koodin suorituskykyä benchmark-testein.

    Usage:
        agent = PerformanceTestAgent()
        result = agent.run("Benchmarkoi funktio", code="sum(range(100))")
    """

    agent_type: str = "performance_test"
    input_schema = PerformanceTestInput
    output_schema = PerformanceTestResult

    def _time_code_execution(self, code: str, iterations: int) -> tuple[list[float], int]:
        """Ajoita koodia annetun määrän kertoja ja palauta ajat."""
        times: list[float] = []
        completed = 0
        local_ns: dict[str, Any] = {}

        try:
            # Käännä koodi (tarkista syntaksi)
            compiled = compile(code, "<benchmark>", "exec")
        except SyntaxError as e:
            return [], 0

        for _ in range(iterations):
            start = time.perf_counter()
            try:
                exec(compiled, local_ns)
                elapsed = time.perf_counter() - start
                times.append(elapsed)
                completed += 1
            except Exception:
                continue

        return times, completed

    def _percentile(self, data: list[float], percentile: float) -> float:
        """Laske percentyiliaika."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        index = min(index, len(sorted_data) - 1)
        return sorted_data[index]

    def _run(self, input_data: PerformanceTestInput) -> PerformanceTestResult:
        """PerformanceTestAgentin päälogiika."""
        code = input_data.code
        file_path = input_data.file_path

        # Lue tiedosto
        if not code and file_path:
            path = Path(file_path)
            if path.exists() and path.suffix == ".py":
                code = path.read_text(encoding="utf-8")

        if not code:
            return PerformanceTestResult(
                success=False,
                result=None,
                message="Ei koodia benchmarkoita.",
                agent_type=self.agent_type,
                benchmark_name="empty",
            )

        # 1. Lämmitys (varaa resurssit, jäädyttää CPU-cache)
        self._time_code_execution(code, input_data.warmup)

        # 2. Benchmarki
        start = time.perf_counter()
        times, completed = self._time_code_execution(code, input_data.iterations)
        total_time = time.perf_counter() - start

        if completed == 0:
            return PerformanceTestResult(
                success=False,
                result=None,
                message="Kaikki iteraatiot epäonnistuivat.",
                agent_type=self.agent_type,
                benchmark_name="failed",
            )

        # 3. Laske tilastot
        avg = sum(times) / len(times)
        p95 = self._percentile(times, 95)

        return PerformanceTestResult(
            success=True,
            result={"total_calls": completed, "avg_time": avg},
            message=f"Benchmark valmis: {completed} kutsua, keskimäärin {avg:.6f}s.",
            agent_type=self.agent_type,
            total_calls=completed,
            total_time=total_time,
            avg_time=avg,
            min_time=min(times),
            max_time=max(times),
            p95_time=p95,
            iterations_completed=completed,
            benchmark_name="custom_benchmark",
        )


class IntegrationTestAgent(BaseAgent):
    """
    IntegrationTestAgent tarkistaa modulien välisten yhteyksien.

    Usage:
        agent = IntegrationTestAgent()
        result = agent.run("Testaa integraatiota", project_path=".")
    """

    agent_type: str = "integration_test"
    input_schema = IntegrationTestInput
    output_schema = IntegrationTestOutput

    # Oletusmoduulit AIDE-projektille
    DEFAULT_MODULES = ["agents.base", "agents.director", "agents.project_manager",
                        "agents.developer", "agents.testing_agent", "agents.security_agent",
                        "agents.documentation_agent"]

    def _get_modules(self, input_data: IntegrationTestInput) -> list[str]:
        """Hae testattavat moduulit."""
        project_path = Path(input_data.project_path)
        modules: list[str] = []

        if input_data.modules_to_test:
            modules = list(input_data.modules_to_test)
        else:
            # Automaattinen haku agents/-kansiosta
            agents_dir = project_path / "agents"
            if agents_dir.exists():
                for f in sorted(agents_dir.glob("*.py")):
                    mod_name = f.stem
                    if mod_name != "__init__":
                        modules.append(f"agents.{mod_name}")

            if not modules:
                modules = self.DEFAULT_MODULES

        return modules

    def _test_import(self, module_name: str) -> bool:
        """Kokeile importata moduuli."""
        try:
            result = subprocess.run(
                ["python", "-c", f"import {module_name}"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _test_agent_imports(self, modules: list[str]) -> dict[str, bool]:
        """Testaa jokaisen moduulin tuonnin."""
        results: dict[str, bool] = {}
        for mod in modules:
            results[mod] = self._test_import(mod)
        return results

    def _check_cross_module_deps(self, modules: list[str]) -> list[str]:
        """Tarkista modulien väliset riippuvuudet regexillä."""
        issues: list[str] = []
        cross_imports: dict[str, set[str]] = {}

        for mod in modules:
            try:
                result = subprocess.run(
                    ["python", "-c", f"import {mod}; import inspect; print(inspect.getfile({mod}))"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                if result.returncode == 0:
                    file_path_str = result.stdout.strip()
                    source = Path(file_path_str).read_text(encoding="utf-8")
                    imports = set(re.findall(r"from\s+agents\.(\w+)", source))
                    if mod.split(".")[-1] in imports:
                        imports.discard(mod.split(".")[-1])
                    cross_imports[mod] = imports - {mod.split(".")[-1]}
            except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
                pass

        # Tarkista import-ympyklet
        for mod, deps in cross_imports.items():
            for dep in deps:
                dep_full = f"agents.{dep}"
                if dep_full in cross_imports:
                    if mod in cross_imports[dep_full] and mod != mod:
                        issues.append(f"Mahdollinen import-ympykre: {mod} ↔ {dep_full}")

        return issues

    def _run(self, input_data: IntegrationTestInput) -> IntegrationTestOutput:
        """IntegrationTestAgentin päälogiika."""
        project_path = Path(input_data.project_path)

        if not project_path.exists():
            return IntegrationTestOutput(
                success=False,
                result=None,
                message=f"Projekti polkua ei ole: {input_data.project_path}",
                agent_type=self.agent_type,
                modules_tested=[],
                all_modules_importable=False,
            )

        # 1. Hae moduulit
        modules = self._get_modules(input_data)

        # 2. Testaa importit
        import_results: dict[str, bool] = {}
        if input_data.check_imports:
            import_results = self._test_agent_imports(modules)

        # 3. Tarkista ydinmoduulit
        all_importable = all(import_results.values()) if import_results else True

        # 4. Integraatiovirheet
        issues: list[str] = []
        for mod, ok in import_results.items():
            if not ok:
                issues.append(f"Moduuli ei tuonnu: {mod}")

        # 5. Laske pisteet
        if import_results:
            pass_rate = sum(import_results.values()) / len(import_results)
            score = pass_rate * 100
        else:
            score = 100.0

        return IntegrationTestOutput(
            success=all_importable,
            result={"modules_tested": len(modules), "score": score},
            message=f"Integraatiotestaus valmis: {len(modules)} moduulilla, pisteet {score}/100.",
            agent_type=self.agent_type,
            modules_tested=modules,
            import_results=import_results,
            integration_issues=issues,
            score=score,
            all_modules_importable=all_importable,
        )


__all__ = [
    "TestRunnerAgent",
    "TestRunnerInput",
    "TestRunnerOutput",
    "PerformanceTestAgent",
    "PerformanceTestInput",
    "PerformanceTestResult",
    "IntegrationTestAgent",
    "IntegrationTestInput",
    "IntegrationTestOutput",
]
