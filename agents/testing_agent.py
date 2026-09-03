"""
TestingAgent-moduuli (M5) — testien suunnittelu, suoritus ja QA.

Sisältää kolme agenttia:
- TestDesignerAgent: suunnittelee testit annetulle koodille ja vaatimuksille.
- TesterAgent: suorittaa testit ja analysoi tulokset.
- QAAgent: tarkistaa projektin laadun, kattavuuden ja struktuurin.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


class TestDesignInput(AgentInput):
    """TestDesignerAgentin syöte."""

    code: str = Field(default="", description="Testattava koodi.")
    file_path: Optional[str] = Field(default=None, description="Polku analysoitavalle tiedostolle.")
    framework: str = Field(default="pytest", description="Testauskehyksen nimi (pytest, unittest, jest).")
    requirements: list[dict[str, Any]] = Field(default_factory=list, description="Vaatimukset.")


class TestDesignOutput(AgentOutput):
    """TestDesignerAgentin tuloste."""

    test_cases: list[dict[str, Any]] = Field(default_factory=list, description="Suunnitellut testitapaukset.")
    test_file_content: str = Field(default="", description="Generoitu testitiedoston sisältö.")
    coverage_target: list[str] = Field(default_factory=list, description="Kattavuusreunat.")


class TestRunInput(AgentInput):
    """TesterAgentin syöte."""

    test_path: str = Field(default="tests/", description="Polku testikansiolle tai tiedostolle.")
    framework: str = Field(default="pytest", description="Testauskehys.")
    capture_output: bool = Field(default=True, description="Kaapaa tuloste.")
    fail_fast: bool = Field(default=False, description="Pysäytä ensimmäisen epäonnistumisen jälkeen.")


class TestRunOutput(AgentOutput):
    """TesterAgentin tuloste."""

    passed: int = Field(default=0, description="Testien määrä, jotka läpäistyivät.")
    failed: int = Field(default=0, description="Testien määrä, jotka epäonnistuivat.")
    errors: int = Field(default=0, description="Testien määrä, jotka kaatuivat.")
    skipped: int = Field(default=0, description="Testien määrä, jotka ohitettiin.")
    exit_code: int = Field(default=0, description="Testikomennon paluuarvo.")
    output: str = Field(default="", description="Komennon tuloste.")


class QAInput(AgentInput):
    """QAAgentin syöte."""

    project_path: str = Field(default=".", description="Projektipolku.")
    check_coverage: bool = Field(default=True, description="Tarkasta koodikattavuus.")
    check_tests: bool = Field(default=True, description="Tarkasta testit.")
    min_coverage: float = Field(default=80.0, description="Minimikattavuus prosentteina.")


class QAOutput(AgentOutput):
    """QAAgentin tuloste."""

    coverage: float = Field(default=0.0, description="Koodikattavuus prosentteina.")
    test_files: list[str] = Field(default_factory=list, description="Löydetyt testitiedostot.")
    issues: list[str] = Field(default_factory=list, description="Laatu- ja kattavuusongelmat.")
    score: float = Field(default=0.0, description="QA-pisteet (0-100).")


class TestDesignerAgent(BaseAgent):
    """
    TestDesignerAgent suunnittelee testit annetulle koodille.

    Usage:
        agent = TestDesignerAgent()
        result = agent.run(
            task="Suunnittele testit tälle funktiolle",
            code="def add(a, b): return a + b",
        )
    """

    agent_type: str = "test_designer"
    input_schema = TestDesignInput
    output_schema = TestDesignOutput

    def _extract_functions(self, code: str) -> list[dict[str, Any]]:
        """Purkaa Python-koodista funktiot ja niiden parametrit."""
        functions: list[dict[str, Any]] = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    params = [a.arg for a in node.args.args]
                    returns = ast.unparse(node.returns) if node.returns else None
                    functions.append({
                        "name": node.name,
                        "params": params,
                        "returns": returns,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node) or "",
                    })
        except SyntaxError:
            pass
        return functions

    def _generate_pytest_tests(self, functions: list[dict[str, Any]], class_name: str = "TestClass") -> str:
        """Generoi pytest-testit funktioille."""
        lines = ["""Automaattisesti generoidut testit.""", ""]

        for func in functions:
            name = func["name"]
            params = func["params"]

            # Ohita dunder-metodit
            if name.startswith("_"):
                continue

            lines.append(f"def test_{name}():")
            lines.append(f'    """Testaa funktio: {name}."""')

            # Luo testiparametrit dummy-arvoilla
            test_args = []
            for p in params:
                if p == "self":
                    continue
                test_args.append("1")  # Yksinkertainen dummy-arvo

            if test_args:
                lines.append(f"    result = {name}({', '.join(test_args)})")
            else:
                lines.append(f"    result = {name}()")
            lines.append("    assert result is not None")
            lines.append("")

        return "\n".join(lines)

    def _generate_test_cases(self, functions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Luo testitapaus-dictionaryt funktioille."""
        cases: list[dict[str, Any]] = []
        for func in functions:
            func_name = func["name"]
            if func_name.startswith("_"):
                continue
            cases.append({
                "name": f"test_{func_name}",
                "function": func_name,
                "params": func["params"],
                "description": func["docstring"] or f"Testaa {func_name}-funktiota.",
                "type": "unit",
            })
        return cases

    def _run(self, input_data: TestDesignInput) -> TestDesignOutput:
        """TestDesignerAgentin päälogiikka."""
        code = input_data.code
        framework = input_data.framework

        # Lue koodi tiedostosta jos annettu
        if not code and input_data.file_path:
            path = Path(input_data.file_path)
            if path.exists():
                code = path.read_text(encoding="utf-8")

        if not code:
            return TestDesignOutput(
                success=False,
                result=None,
                message="Ei koodia testaukseen.",
                agent_type=self.agent_type,
                test_cases=[],
                test_file_content="",
                coverage_target=[],
            )

        # 1. Purku funktiot
        functions = self._extract_functions(code)

        # 2. Luo testitapaukset
        test_cases = self._generate_test_cases(functions)

        # 3. Generoi testitiedoston sisältö
        if framework == "pytest":
            test_content = self._generate_pytest_tests(functions)
        elif framework == "unittest":
            test_content = self._generate_unittest_tests(functions)
        else:
            test_content = f"# Tests for {len(functions)} functions\n"

        # 4. Määritä kattavuusreunat
        coverage_targets = [f"{f['name']}" for f in functions if not f["name"].startswith("_")]

        return TestDesignOutput(
            success=True,
            result={"function_count": len(functions), "test_case_count": len(test_cases)},
            message=f"Suunniteltu {len(test_cases)} testitapausta {len(functions)} funktiolle.",
            agent_type=self.agent_type,
            test_cases=test_cases,
            test_file_content=test_content,
            coverage_target=coverage_targets,
        )

    def _generate_unittest_tests(self, functions: list[dict[str, Any]]) -> str:
        """Generoi unittest-testit."""
        lines = ['"""Unittest-testit."""', "", "import unittest", ""]

        for func in functions:
            func_name = func["name"]
            if func_name.startswith("_"):
                continue
            lines.append(f"def test_{func_name}(self):")
            lines.append(f'    """Testaa {func_name}."""')
            params = [p for p in func["params"] if p != "self"]
            args = ", ".join(["1"] * len(params))
            lines.append(f"    result = {func_name}({args})")
            lines.append("    assertIsNotNone(result)")
            lines.append("")

        lines.append("")
        lines.append("if __name__ == '__main__':")
        lines.append("    unittest.main()")
        return "\n".join(lines)


class TesterAgent(BaseAgent):
    """
    TesterAgent suorittaa testit ja analysoi tulokset.

    Usage:
        agent = TesterAgent()
        result = agent.run(
            task="Aja testit tests/-kansiosta",
            test_path="tests/",
        )
    """

    agent_type: str = "tester"
    input_schema = TestRunInput
    output_schema = TestRunOutput

    def _parse_pytest_output(self, output: str) -> dict[str, int]:
        """Parsi pytest-tuloste lukumäärille."""
        passed = failed = errors = skipped = 0

        # Etsi yhteenveto: "180 passed"
        match = re.search(r"(\d+)\s+passed", output)
        if match:
            passed = int(match.group(1))

        match = re.search(r"(\d+)\s+failed", output)
        if match:
            failed = int(match.group(1))

        match = re.search(r"(\d+)\s+error", output)
        if match:
            errors = int(match.group(1))

        match = re.search(r"(\d+)\s+skipped", output)
        if match:
            skipped = int(match.group(1))

        return {"passed": passed, "failed": failed, "errors": errors, "skipped": skipped}

    def _parse_pytest_json(self, output: str) -> dict[str, int]:
        """Parsi pytest-json-reportin tuloste (jos käytössä)."""
        try:
            data = json.loads(output)
            summary = data.get("summary", {})
            return {
                "passed": summary.get("passed", 0),
                "failed": summary.get("failed", 0),
                "errors": summary.get("error", 0),
                "skipped": summary.get("skipped", 0),
            }
        except (json.JSONDecodeError, KeyError):
            return {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}

    def _run(self, input_data: TestRunInput) -> TestRunOutput:
        """TesterAgentin päälogiikka."""
        test_path = input_data.test_path
        framework = input_data.framework

        path = Path(test_path)
        if not path.exists():
            return TestRunOutput(
                success=False,
                result=None,
                message=f"Testipolku ei löydy: {test_path}",
                agent_type=self.agent_type,
                passed=0,
                failed=0,
                errors=0,
                skipped=0,
                exit_code=-1,
                output="",
            )

        # Muodista komento
        if framework == "pytest":
            cmd = ["python", "-m", "pytest", str(path), "-v", "--tb=short"]
            if input_data.fail_fast:
                cmd.append("-x")
        else:
            cmd = [str(test_path)]

        try:
            result = subprocess.run(
                cmd,
                capture_output=input_data.capture_output,
                text=True,
                timeout=120,
            )
            output = result.stdout or result.stderr or ""

            # Parsi luvut
            if framework == "pytest":
                counts = self._parse_pytest_output(output)
            else:
                counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}

            return TestRunOutput(
                success=(result.returncode == 0),
                result=counts,
                message=f"Testit suoritettu: {counts['passed']} ok, {counts['failed']} epäonnistui.",
                agent_type=self.agent_type,
                passed=counts["passed"],
                failed=counts["failed"],
                errors=counts["errors"],
                skipped=counts["skipped"],
                exit_code=result.returncode,
                output=output,
            )

        except subprocess.TimeoutExpired:
            return TestRunOutput(
                success=False,
                result=None,
                message="Testit aikakatkaistiin (120s timeout).",
                agent_type=self.agent_type,
                passed=0,
                failed=0,
                errors=1,
                skipped=0,
                exit_code=-1,
                output="",
            )
        except FileNotFoundError:
            return TestRunOutput(
                success=False,
                result=None,
                message=f"Testauskehys '{framework}' ei ole asennettu.",
                agent_type=self.agent_type,
                passed=0,
                failed=0,
                errors=1,
                skipped=0,
                exit_code=-1,
                output="",
            )


class QAAgent(BaseAgent):
    """
    QAAgent tarkistaa projektin laadun ja kattavuuden.

    Usage:
        agent = QAAgent()
        result = agent.run(
            task="Tarkista projektin laatu",
            project_path=".",
            min_coverage=80.0,
        )
    """

    agent_type: str = "qa"
    input_schema = QAInput
    output_schema = QAOutput

    def _find_test_files(self, project_path: Path) -> list[str]:
        """Löydä testitiedostot projektista."""
        test_files: list[str] = []
        skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", "site-packages"}

        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for fname in files:
                if fname.startswith("test_") and fname.endswith(".py"):
                    test_files.append(str(Path(root) / fname))
                elif fname.endswith("_test.py"):
                    test_files.append(str(Path(root) / fname))

        return test_files

    def _count_test_functions(self, test_path: str) -> int:
        """Laskee testifunktiot tiedostossa."""
        try:
            source = Path(test_path).read_text(encoding="utf-8")
            tree = ast.parse(source)
            count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    count += 1
            return count
        except (SyntaxError, OSError):
            return 0

    def _check_coding_standards(self, project_path: Path) -> list[str]:
        """Tarkista ohjelmointikäytännöt."""
        issues: list[str] = []
        py_files = list(project_path.rglob("*.py"))
        skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv"}

        for py_file in py_files:
            if any(part in skip_dirs for part in py_file.parts):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                # Tarkista moduulin doksekeinnot
                if not content.startswith('"""') and not content.startswith("#"):
                    issues.append(f"{py_file}: Puute moduulin doksekeinnot")

                # Tarkista käytettyjen importtien määrä
                if "import *" in content:
                    issues.append(f"{py_file}: import * -tyyppi")
            except (OSError, UnicodeDecodeError):
                continue

        return issues[:10]  # Rajoita määrä

    def _run(self, input_data: QAInput) -> QAOutput:
        """QAAgentin päälogiika."""
        project_path = Path(input_data.project_path)

        if not project_path.exists():
            return QAOutput(
                success=False,
                result=None,
                message=f"Projektiota ei löydy: {input_data.project_path}",
                agent_type=self.agent_type,
                coverage=0.0,
                test_files=[],
                issues=["Projektiota ei löydy"],
                score=0.0,
            )

        issues: list[str] = []
        test_files: list[str] = []
        total_tests = 0
        coverage = 0.0

        # 1. Etsi testitiedostot
        if input_data.check_tests:
            test_files = self._find_test_files(project_path)
            for tf in test_files:
                total_tests += self._count_test_functions(tf)

            if not test_files:
                issues.append("Ei löydy testitiedostoja")
            elif total_tests == 0:
                issues.append("Testitiedostot ovat tyhjiä")

        # 2. Tarkista kattavuus (käytetään pytest-covia jos saatavilla)
        if input_data.check_coverage:
            try:
                result = subprocess.run(
                    ["python", "-m", "pytest", "--cov=.", "--cov-report=term-missing", "-q"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(project_path),
                )
                output = result.stdout or result.stderr

                # Etsi kattavuusluku
                match = re.search(r"(\d+)%", output)
                if match:
                    coverage = float(match.group(1))

                if coverage < input_data.min_coverage:
                    issues.append(f"Kattavuus {coverage}% on ali kynnysarvon {input_data.min_coverage}%")

            except (subprocess.TimeoutExpired, FileNotFoundError):
                issues.append("Ei voitu laskea koodikattavuutta (pytest-cov puuttuu tai aikakatkaistiin)")
                coverage = 0.0

        # 3. Tarkista ohjelmointikäytännöt
        std_issues = self._check_coding_standards(project_path)
        issues.extend(std_issues)

        # 4. Laske QA-pisteet
        score = 100.0
        score -= len(issues) * 5  # 5 pistettä per ongelma
        if not test_files:
            score -= 20
        elif total_tests < 10:
            score -= 10

        score = max(0.0, score)

        return QAOutput(
            success=True,
            result={"coverage": coverage, "test_count": total_tests, "issue_count": len(issues)},
            message=f"QA-valmiivi: {len(test_files)} testitiedostoa, {total_tests} testia, kattavuus {coverage}%, pisteet {score}/100.",
            agent_type=self.agent_type,
            coverage=coverage,
            test_files=test_files,
            issues=issues,
            score=score,
        )


__all__ = [
    "TestDesignerAgent",
    "TestDesignInput",
    "TestDesignOutput",
    "TesterAgent",
    "TestRunInput",
    "TestRunOutput",
    "QAAgent",
    "QAInput",
    "QAOutput",
]
