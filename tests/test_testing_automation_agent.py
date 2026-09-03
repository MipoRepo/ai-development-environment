"""
Testit TestingAutomationAgenteille (M8).
"""

from pathlib import Path

import pytest

from agents.testing_automation_agent import (
    TestRunnerAgent,
    TestRunnerInput,
    TestRunnerOutput,
    PerformanceTestAgent,
    PerformanceTestInput,
    PerformanceTestResult,
    IntegrationTestAgent,
    IntegrationTestInput,
    IntegrationTestOutput,
)


@pytest.fixture
def runner():
    return TestRunnerAgent()


@pytest.fixture
def perf():
    return PerformanceTestAgent()


@pytest.fixture
def integration():
    return IntegrationTestAgent()


@pytest.fixture
def simple_test_project(tmp_path):
    """Luo yksinkertainen testiprojekti."""
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_simple.py").write_text(
        '''"""Testit."""
def test_pass():
    assert 1 + 1 == 2

def test_pass_again():
    assert "a" == "a"
''',
        encoding="utf-8",
    )
    return tmp_path / "tests"


@pytest.fixture
def failing_test_project(tmp_path):
    """Luo projekti jonka kanssa testi epäonnistuu."""
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_fail.py").write_text(
        '''"""Testit."""
def test_pass():
    assert 1 + 1 == 2

def test_fail():
    assert 1 + 1 == 3
''',
        encoding="utf-8",
    )
    return tmp_path / "tests"


@pytest.fixture
def benchmark_code():
    """Palauttaa benchmarkoitavan koodin."""
    return "result = sum(range(1000))"


class TestTestRunnerAgent:
    """Testit TestRunnerAgentille."""

    def test_agent_type(self, runner):
        assert runner.agent_type == "test_runner"

    def test_input_schema(self, runner):
        assert runner.input_schema == TestRunnerInput

    def test_output_schema(self, runner):
        assert runner.output_schema == TestRunnerOutput

    def test_run_executes_tests(self, runner, simple_test_project):
        """run() suorittaa testit ja laskee tulokset."""
        result = runner.run(
            task="Aja testit",
            test_path=str(simple_test_project),
            verbose=False,
            coverage=False,
        )
        assert isinstance(result, TestRunnerOutput)
        assert result.success is True
        assert result.passed >= 2

    def test_run_detects_failures(self, runner, failing_test_project):
        """run() havaitsee epäonnistuneet testit."""
        result = runner.run(
            task="Aja testit",
            test_path=str(failing_test_project),
            verbose=False,
            coverage=False,
        )
        assert isinstance(result, TestRunnerOutput)
        assert result.failed >= 1
        assert result.passed >= 1

    def test_run_with_fail_fast(self, runner, failing_test_project):
        """fail_fast-parametri pysäyttää ensimmässä virheessä."""
        result = runner.run(
            task="Aja testit",
            test_path=str(failing_test_project),
            verbose=False,
            coverage=False,
            fail_fast=True,
        )
        assert result.exit_code != 0 or result.failed >= 1

    def test_run_calculates_duration(self, runner, simple_test_project):
        """run() laskee kesto-ajan."""
        result = runner.run(
            task="Aja testit",
            test_path=str(simple_test_project),
            verbose=False,
            coverage=False,
        )
        assert result.duration > 0

    def test_run_nonexistent_path(self, runner):
        """run() käsittelee virheellisesti polkua."""
        result = runner.run(
            task="Aja testit",
            test_path="/nonexistent/tests/",
            verbose=False,
            coverage=False,
        )
        assert result.success is False

    def test_run_with_extra_args(self, runner, simple_test_project):
        """run() välittää extra_args pytestille."""
        result = runner.run(
            task="Aja testit",
            test_path=str(simple_test_project),
            verbose=False,
            coverage=False,
            extra_args=["-k", "pass"],
        )
        assert result.success is True

    def test_parse_output_parses_counts(self, runner):
        """_parse_output parsii oikein."""
        output = "3 passed, 1 failed"
        counts = runner._parse_output(output)
        assert counts["passed"] == 3
        assert counts["failed"] == 1

    def test_extract_coverage(self, runner):
        """_extract_coverage poimii prosenttiluvun."""
        output = "Name    Stmts  Miss  Cover\nTOTAL     100    10    90%"
        coverage = runner._extract_coverage(output)
        assert coverage == 90.0

    def test_run_serializes(self, runner, simple_test_project):
        """Tulos voidaan serialisoida."""
        result = runner.run(
            task="Aja testit",
            test_path=str(simple_test_project),
            verbose=False,
            coverage=False,
        )
        d = result.to_dict()
        assert d["agent_type"] == "test_runner"
        assert "passed" in d
        assert "duration" in d


class TestPerformanceTestAgent:
    """Testit PerformanceTestAgentille."""

    def test_agent_type(self, perf):
        assert perf.agent_type == "performance_test"

    def test_input_schema(self, perf):
        assert perf.input_schema == PerformanceTestInput

    def test_output_schema(self, perf):
        assert perf.output_schema == PerformanceTestResult

    def test_run_benchmarks_code(self, perf, benchmark_code):
        """run() benchmarkoi koodin."""
        result = perf.run(
            task="Benchmarkoi",
            code=benchmark_code,
            iterations=50,
            warmup=5,
        )
        assert isinstance(result, PerformanceTestResult)
        assert result.success is True
        assert result.total_calls > 0
        assert result.total_time > 0

    def test_run_calculates_avg_time(self, perf, benchmark_code):
        """run() laskee keskimääräisen ajan."""
        result = perf.run(
            task="Benchmarkoi",
            code=benchmark_code,
            iterations=50,
            warmup=5,
        )
        assert result.avg_time > 0
        assert result.avg_time <= result.max_time

    def test_run_min_max_times(self, perf, benchmark_code):
        """run() laskee min/max-ajat."""
        result = perf.run(
            task="Benchmarkoi",
            code=benchmark_code,
            iterations=50,
            warmup=5,
        )
        assert result.min_time <= result.avg_time
        assert result.max_time >= result.avg_time

    def test_run_calculates_p95(self, perf, benchmark_code):
        """run() laskee 95. percentyilin."""
        result = perf.run(
            task="Benchmarkoi",
            code=benchmark_code,
            iterations=100,
            warmup=10,
        )
        assert result.p95_time > 0
        assert result.p95_time >= result.min_time

    def test_run_warmup_executes(self, perf, benchmark_code):
        """run() suorittaa lämmityssyklyt ennen benchmarkia."""
        result = perf.run(
            task="Benchmarkoi",
            code=benchmark_code,
            iterations=20,
            warmup=10,
        )
        assert result.success is True
        assert result.iterations_completed > 0

    def test_run_invalid_code(self, perf):
        """run() käsittelee virheellisen koodin."""
        result = perf.run(
            task="Benchmarkoi",
            code="def broken(\n",
        )
        assert result.success is False

    def test_run_empty_code(self, perf):
        """run() antaa virheen tyhjälle koodille."""
        result = perf.run(
            task="Benchmarkoi",
            code="",
        )
        assert result.success is False

    def test_run_from_file(self, perf, tmp_path, benchmark_code):
        """run() lukee koodin tiedostosta."""
        filepath = tmp_path / "bench.py"
        filepath.write_text(benchmark_code, encoding="utf-8")

        result = perf.run(
            task="Benchmarkoi tiedosto",
            file_path=str(filepath),
            iterations=20,
            warmup=5,
        )
        assert result.success is True
        assert result.total_calls > 0

    def test_run_benchmark_name(self, perf, benchmark_code):
        """run() määrittää oletusbenchmarkin nimen."""
        result = perf.run(
            task="Benchmarkoi",
            code=benchmark_code,
            iterations=10,
            warmup=2,
        )
        assert result.benchmark_name == "custom_benchmark"

    def test_run_serializes(self, perf, benchmark_code):
        """Tulos voidaan serialisoida."""
        result = perf.run(
            task="Benchmarkoi",
            code=benchmark_code,
            iterations=10,
            warmup=2,
        )
        d = result.to_dict()
        assert d["agent_type"] == "performance_test"
        assert "avg_time" in d


class TestIntegrationTestAgent:
    """Testit IntegrationTestAgentille."""

    def test_agent_type(self, integration):
        assert integration.agent_type == "integration_test"

    def test_input_schema(self, integration):
        assert integration.input_schema == IntegrationTestInput

    def test_output_schema(self, integration):
        assert integration.output_schema == IntegrationTestOutput

    def test_run_nonexistent_project(self, integration):
        """run() antaa virheen olemattomalle projektille."""
        result = integration.run(
            task="Testaa integraatiota",
            project_path="/nonexistent/project",
        )
        assert result.success is False

    def test_run_finds_modules(self, integration, tmp_path):
        """run() löytää agenttimoduulit projektista."""
        result = integration.run(
            task="Testaa integraatiota",
            project_path=str(tmp_path),
            check_imports=False,
        )
        assert isinstance(result, IntegrationTestOutput)
        assert len(result.modules_tested) > 0

    def test_run_uses_default_modules_on_empty(self, integration, tmp_path):
        """Tyhjällä projektille käytetään oletusmoduuleja."""
        result = integration.run(
            task="Testaa",
            project_path=str(tmp_path),
            check_imports=False,
        )
        assert "agents.base" in result.modules_tested

    def test_run_tests_imports(self, integration, tmp_path):
        """run() testaa moduulien tuonnin."""
        result = integration.run(
            task="Testaa integraatiota",
            project_path=".",
            check_imports=True,
        )
        assert len(result.import_results) > 0

    def test_run_all_modules_importable(self, integration, tmp_path):
        """Kaikki oletusmoduulit ovat tuonnissa."""
        result = integration.run(
            task="Testaa integraatiota",
            project_path=".",
            check_imports=True,
        )
        assert result.all_modules_importable is True
        assert result.score > 0

    def test_run_with_custom_modules(self, integration):
        """run() testaa määritellyt moduulit."""
        result = integration.run(
            task="Testaa näitä moduuleja",
            modules_to_test=["agents.base", "agents.director"],
            check_imports=False,
        )
        assert "agents.base" in result.modules_tested
        assert "agents.director" in result.modules_tested

    def test_run_calculates_score(self, integration):
        """run() laskee intelligenssipisteet."""
        result = integration.run(
            task="Testaa integraatiota",
            project_path=".",
        )
        assert 0 <= result.score <= 100

    def test_run_no_issues_when_success(self, integration):
        """Ei integraatiovirheitä kun kaikki on OK."""
        result = integration.run(
            task="Testaa integraatiota",
            project_path=".",
            check_imports=True,
        )
        assert len(result.integration_issues) == 0

    def test_run_serializes(self, integration):
        """Tulos voidaan serialisoida."""
        result = integration.run(
            task="Testaa integraatiota",
            project_path=".",
            check_imports=False,
        )
        d = result.to_dict()
        assert d["agent_type"] == "integration_test"
        assert "modules_tested" in d
        assert "score" in d
