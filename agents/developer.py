"""
DeveloperAgent (M4) — kirjoittaa ja muokkaa koodia projekteissa.

Sisältää kolme agenttia:
- DeveloperAgent: generoi koodia, luo ja päivittää tiedostoja.
- RefactoringAgent: refaktoroi koodia ja antaa parannusehdotuksia.
- CodeReviewAgent: tarkistaa koodin laatuun ja turvallisuuteen liittyen.
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


class DeveloperInput(AgentInput):
    """DeveloperAgentin syöte."""

    file_path: Optional[str] = Field(default=None, description="Polku luodulle/päivitetulle tiedostolle.")
    language: str = Field(default="python", description="Koodikieli (python, javascript, markdown).")
    project_path: str = Field(default=".", description="Projektipolku.")
    overwrite: bool = Field(default=False, description="Yhdistä vanhan ja uuden sisällön, eikä ylikirjoita.")
    dependencies: list[str] = Field(default_factory=list, description="Projektin riippuvuudet.")


class DeveloperOutput(AgentOutput):
    """DeveloperAgentin tuloste."""

    file_path: str = Field(default="", description="Luolen/päivitetyn tiedoston polku.")
    content: str = Field(default="", description="Luodun tiedoston sisältö.")
    operations: list[str] = Field(default_factory=list, description="Suoritellut operaatiot.")
    lines_written: int = Field(default=0, description="Kirjoitettujen rivien määrä.")


class RefactoringInput(AgentInput):
    """RefactoringAgentin syöte."""

    code: str = Field(default="", description="Refaktoroitava koodi.")
    file_path: Optional[str] = Field(default=None, description="Polku analysoitavalle tiedostolle.")
    rules: list[str] = Field(default_factory=list, description="Käytettävät refaktorointisäännöt.")


class RefactoringOutput(AgentOutput):
    """RefactoringAgentin tuloste."""

    original_code: str = Field(default="", description="Alkuperäinen koodi.")
    refactored_code: str = Field(default="", description="Refaktoroitu koodi.")
    changes: list[str] = Field(default_factory=list, description="Teetyt muutokset.")
    suggestions: list[str] = Field(default_factory=list, description="Parannusehdotukset.")


class CodeReviewInput(AgentInput):
    """CodeReviewAgentin syöte."""

    code: str = Field(default="", description="Tarkistettava koodi.")
    file_path: Optional[str] = Field(default=None, description="Tiedoston polku.")
    severity_threshold: str = Field(default="medium", description="Vakavin hyväksytty vakaus.")
    project_path: str = Field(default=".", description="Projekkipolku tarkistusta varten.")


class CodeReviewOutput(AgentOutput):
    """CodeReviewAgentin tuloste."""

    issues: list[dict[str, Any]] = Field(default_factory=list, description="Löydetyt ongelmit.")
    issue_count: int = Field(default=0, description="Ongelmien yhteismäärä.")
    severity_levels: dict[str, int] = Field(default_factory=dict, description="Vakautustasot lukumäärinä.")
    score: float = Field(default=100.0, description="Koodin laadun pisteet (0-100).")


class DeveloperAgent(BaseAgent):
    """
    DeveloperAgent generoi koodia, luo ja päivittää tiedostoja.

    Usage:
        agent = DeveloperAgent()
        result = agent.run(
            task="Luo FastAPI-sovellus, jossa on /hello-endpoint",
            file_path="src/api/main.py",
            language="python",
        )
    """

    agent_type: str = "developer"
    input_schema = DeveloperInput
    output_schema = DeveloperOutput

    # Koodimallipohjat eri kielille
    _TEMPLATES: dict[str, str] = {
        "python": {
            "api_endpoint": '''"""{description}."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class {class_name}(BaseModel):
{model_fields}


@app.get("/")
def read_root():
    return {"message": "Hello from {project_name}"}


{endpoint_code}
''',
            "basic_module": '''"""{description}."""


def main():
    pass


if __name__ == "__main__":
    main()
''',
        },
        "javascript": {
            "basic_module": '''/**
 * {description}
 */

function main() {{
    console.log("Hello from {module_name}");
}}

main();
''',
        },
        "markdown": {
            "doc_template": '''# {title}

{description}

## Osat

- [ ] Osio 1
- [ ] Osio 2

## Liitteet
''',
        },
    }

    def _generate_code(self, description: str, language: str, class_name: str = "Item") -> str:
        """Generoi koodin käänteeseen (perusmallit)."""
        if language == "python":
            return self._TEMPLATES["python"]["basic_module"].format(
                description=description,
            )
        elif language == "javascript":
            return self._TEMPLATES["javascript"]["basic_module"].format(
                description=description,
                module_name=class_name,
            )
        elif language == "markdown":
            return self._TEMPLATES["markdown"]["doc_template"].format(
                title=description,
                description="",
            )
        return f"# {description}\n"

    def _resolve_file_path(self, file_path: Optional[str], project_path: str, language: str) -> Path:
        """Päättää tiedoston sijainnin."""
        if file_path:
            path = Path(file_path)
            if path.is_absolute():
                return path
            return Path(project_path) / path

        # Generoi oletuspolku
        ext = {"python": ".py", "javascript": ".js", "markdown": ".md"}.get(language, ".txt")
        return Path(project_path) / f"src/generated{ext}"

    def _run(self, input_data: DeveloperInput) -> DeveloperOutput:
        """DeveloperAgentin päälogiikka."""
        language = input_data.language
        task = input_data.task
        operations: list[str] = []

        # 1. Generoi koodi
        generated_code = self._generate_code(task, language)
        operations.append("generate_code")

        # 2. Päätä tiedostopolku
        file_path = self._resolve_file_path(
            input_data.file_path, input_data.project_path, language
        )

        content = generated_code
        lines_written = len(generated_code.splitlines())

        # 3. Kirjoita tiedostoon (jos annettu)
        written_path = ""
        if file_path:
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)

                if file_path.exists() and not input_data.overwrite:
                    # Liitä uusi sisältö vanhan jälkeen
                    old_content = file_path.read_text(encoding="utf-8")
                    content = old_content + "\n\n" + generated_code
                    operations.append("append_to_file")
                else:
                    operations.append("create_file")

                file_path.write_text(content, encoding="utf-8")
                written_path = str(file_path)
            except (OSError, PermissionError) as e:
                return DeveloperOutput(
                    success=False,
                    result=None,
                    message=f"Virhe kirjoitettaessa tiedostoa: {e}",
                    agent_type=self.agent_type,
                    file_path=str(file_path),
                    content="",
                    operations=operations,
                    lines_written=0,
                )

        return DeveloperOutput(
            success=True,
            result={"language": language, "file": written_path},
            message=f"Koodia generoitu ({language}): {lines_written} riviä.",
            agent_type=self.agent_type,
            file_path=written_path,
            content=content,
            operations=operations,
            lines_written=lines_written,
        )


class RefactoringAgent(BaseAgent):
    """
    RefactoringAgent parantaa koodin laatua eikä muuta toiminnallisuutta.

    Usage:
        agent = RefactoringAgent()
        result = agent.run(
            task="Refaktoroi tämä funktio",
            code="def foo(): pass",
        )
    """

    agent_type: str = "refactoring"
    input_schema = RefactoringInput
    output_schema = RefactoringOutput

    # Refaktorointisäännöt Pythonille
    _PY_RULES = {
        "sort_imports": "Lajittele importit aakkosjärjestykseen",
        "remove_unused": "Poista käyttämättömät muuttujat",
        "rename_function": "Nimeä funktiot selkeästi (camelCase → snake_case)",
        "add_docstrings": "Lisää puuttuvat doksekeinnot",
        "simplify_booleans": "Yksinkertaistaan booleset lausekkeet",
        "extract_hardcoded": "Erota kiinteätarveiset arvot vakioiksi",
    }

    def _find_unused_imports(self, tree: ast.AST, source: str) -> list[str]:
        """Etsii käyttämättömät importit Python-koodista."""
        imported: set[str] = set()
        used: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported.add(alias.asname or alias.name)

        # Etsi käytetyt nimet (Simple ast.Name, ast.Attribute)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                # tarkista modulin nimi
                if isinstance(node.value, ast.Name):
                    used.add(node.value.id)

        return sorted(imported - used)

    def _find_long_functions(self, tree: ast.AST, threshold: int = 30) -> list[dict[str, Any]]:
        """Etsii pitkät funktiot (ylittyvät rivimäärän)."""
        long_funcs: list[dict[str, Any]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = getattr(node, "end_lineno", node.lineno)
                length = end - node.lineno + 1
                if length > threshold:
                    long_funcs.append({
                        "name": node.name,
                        "line": node.lineno,
                        "length": length,
                    })
        return long_funcs

    def _find_missing_docstrings(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Etsii puuttuvat doksekeinnot funktioista ja luokista."""
        missing: list[dict[str, Any]] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    missing.append({"name": node.name, "line": node.lineno})
        return missing

    def _analyze_python(self, code: str, rules: list[str]) -> tuple[list[str], list[str]]:
        """Analysoi Python-koodia refaktorointia varten."""
        changes: list[str] = []
        suggestions: list[str] = []

        try:
            tree = ast.parse(code)
            ref_rules = rules or list(self._PY_RULES.keys())

            if "remove_unused" in ref_rules:
                unused = self._find_unused_imports(tree, code)
                if unused:
                    suggestions.append(f"Poista käyttämättomat importit: {', '.join(unused)}")

            if "add_docstrings" in ref_rules:
                missing_docs = self._find_missing_docstrings(tree)
                for item in missing_docs:
                    suggestions.append(f"Lisää doksekeinnot: {item['name']} (rivi {item['line']})")

            if "simplify_booleans" in ref_rules:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Compare) and isinstance(node.ops[0], ast.Eq):
                        if isinstance(node.comparators[0], ast.Constant) and node.comparators[0].value is True:
                            suggestions.append(f"Yksinkertaistaan: if {ast.unparse(node.left)}: (rivi {node.lineno})")

            if "extract_hardcoded" in ref_rules:
                # Etsi kovat nimet (merkkijonot, jotka toistuvat)
                strings = re.findall(r'["\']([^"\']+)["\']', code)
                from collections import Counter
                counts = Counter(strings)
                for s, count in counts.items():
                    if count >= 3 and len(s) > 5:
                        suggestions.append(f"Eriski vakioksi: \"{s}\" toistuu {count} kertaa")

            # Long function -tunnistus (ei riippu säännöistä)
            long_funcs = self._find_long_functions(tree, threshold=30)
            for func in long_funcs:
                suggestions.append(f"Pituus>30 riviä: {func['name']} ({func['length']} riviä, rivi {func['line']})")

            # Muokkaus: lisää moduulin doksekeinnot jos puuttuu
            if code and not code.startswith('"""') and "add_docstrings" in ref_rules:
                if not code.startswith("#"):
                    changes.append("Lisätty moduulin doksekeinnot")
                    code = '"""Moduulin doksekeinnot."""\n' + code

            if not suggestions and not changes:
                suggestions.append("Ei automaattisia muutoksia — koodi näyttää jo hyvältä.")

        except SyntaxError:
            suggestions.append("Virheellinen Python-syntaksi — tarkista ensin.")
            return [], suggestions

        return changes, suggestions

    def _run(self, input_data: RefactoringInput) -> RefactoringOutput:
        """RefactoringAgentin päälogiikka."""
        code = input_data.code
        rules = input_data.rules

        # Jos annettu tiedostopolku, lue tiedosto
        original_code = code
        if input_data.file_path and not code:
            path = Path(input_data.file_path)
            if path.exists():
                original_code = path.read_text(encoding="utf-8")
                code = original_code
            else:
                return RefactoringOutput(
                    success=False,
                    result=None,
                    message=f"Tiedostoa ei löydy: {input_data.file_path}",
                    agent_type=self.agent_type,
                    original_code="",
                    refactored_code="",
                    changes=[],
                    suggestions=[],
                )

        if not code:
            return RefactoringOutput(
                success=False,
                result=None,
                message="Ei koodia analysoitavaksi.",
                agent_type=self.agent_type,
                original_code="",
                refactored_code="",
                changes=[],
                suggestions=[],
            )

        # Tarkista kieli (oletetaan Python, jollei ole ilmeistä)
        changes, suggestions = self._analyze_python(code, rules)

        # Refaktoroidun koodin muotoilu (tässä vain moduulin doksekeinnot)
        refactored_code = code
        for change in changes:
            if "doksekeinnot" in change.lower():
                if not refactored_code.startswith('"""'):
                    refactored_code = '"""Moduulin doksekeinnot."""\n' + refactored_code

        return RefactoringOutput(
            success=True,
            result={"change_count": len(changes), "suggestion_count": len(suggestions)},
            message=f"Refaktorointi valmis: {len(changes)} muutosta, {len(suggestions)} ehdotusta.",
            agent_type=self.agent_type,
            original_code=original_code,
            refactored_code=refactored_code,
            changes=changes,
            suggestions=suggestions,
        )


class CodeReviewAgent(BaseAgent):
    """
    CodeReviewAgent tarkistaa Python-koodin turvallisuutta ja laatua.

    Usage:
        agent = CodeReviewAgent()
        result = agent.run(
            task="Tarkista tämä koodi",
            code="print('hello')",
            severity_threshold="medium",
        )
    """

    agent_type: str = "code_review"
    input_schema = CodeReviewInput
    output_schema = CodeReviewOutput

    # Turvallisuus- ja laatu-odotukset
    _SECURITY_PATTERNS = [
        {"pattern": r"eval\s*\(", "message": "epävarma: eval()-funktio suorittaa mielivalallista koodia", "severity": "critical"},
        {"pattern": r"exec\s*\(", "message": "epävarma: exec() suorittaa mielivalallista koodia", "severity": "critical"},
        {"pattern": r"shell\s*=\s*True", "message": "turvallisuus: shell=True voi altistaa komennon injektiolle", "severity": "high"},
        {"pattern": r"password\s*=\s*['\"][^'\"]+['\"]", "message": "salaus: kiinteä salasana koodissa", "severity": "critical"},
        {"pattern": r"secret\s*=\s*['\"][^'\"]+['\"]", "message": "salaus: kiinteä salaisuus koodissa", "severity": "high"},
        {"pattern": r"sql.*format\s*\(", "message": "SQL-injektiota voidaan hyu: .format() SQL-lauseessa", "severity": "high"},
        {"pattern": r"SELECT.*%s.*%", "message": "SQL-injektiota voidaan: merkintämuotoilu SQL:ssä", "severity": "high"},
    ]

    _QUALITY_PATTERNS = [
        {"pattern": r"bare\s+except", "message": "laatu: bare except -päätymättä (käytä except Exception)", "severity": "medium"},
        {"pattern": r"except\s*:", "message": "laatu: tyhjä except (käytä except Exception)", "severity": "medium"},
        {"pattern": r"import\s+\*", "message": "laatu: import * -tyyppi (väärentävä nimiavaruuden rohkaiseminen)", "severity": "medium"},
    ]

    _SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1}

    def _scan_security(self, code: str, file_path: str) -> list[dict[str, Any]]:
        """Skannaa turvallisuusongelmat codeista."""
        issues: list[dict[str, Any]] = []
        for pattern in self._SECURITY_PATTERNS:
            for match in re.finditer(pattern["pattern"], code, re.IGNORECASE):
                line_no = code[:match.start()].count("\n") + 1
                issues.append({
                    "type": "security",
                    "message": pattern["message"],
                    "line": line_no,
                    "file": file_path,
                    "severity": pattern["severity"],
                })
        return issues

    def _scan_quality(self, code: str, file_path: str) -> list[dict[str, Any]]:
        """Skannaa laatu- ja tyyliongelmista."""
        issues: list[dict[str, Any]] = []

        # Tarkista Python-koodi AST-parsimuksen avulla
        try:
            tree = ast.parse(code)

            # Tarkista doksekeinnot
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not ast.get_docstring(node):
                        line_no = node.lineno
                        issues.append({
                            "type": "quality",
                            "message": f"funktiosta puuttuu doksekeinnot: {node.name}",
                            "line": line_no,
                            "file": file_path,
                            "severity": "low",
                        })

                # Tarkista pitkät funktiot
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    end = getattr(node, "end_lineno", node.lineno)
                    length = end - node.lineno + 1
                    if length > 50:
                        issues.append({
                            "type": "quality",
                            "message": f"funktio liian pitkä ({length} riviä): {node.name}",
                            "line": node.lineno,
                            "file": file_path,
                            "severity": "medium",
                        })
        except SyntaxError:
            issues.append({
                "type": "syntax",
                "message": "virheellinen Python-syntaksi",
                "line": 0,
                "file": file_path,
                "severity": "high",
            })

        # Regulaarilausekkeet laadun tarkistukseen
        for pattern in self._QUALITY_PATTERNS:
            for match in re.finditer(pattern["pattern"], code, re.IGNORECASE):
                line_no = code[:match.start()].count("\n") + 1
                issues.append({
                    "type": "quality",
                    "message": pattern["message"],
                    "line": line_no,
                    "file": file_path,
                    "severity": pattern["severity"],
                })

        return issues

    def _calculate_score(self, issues: list[dict[str, Any]]) -> float:
        """Laskee koodin laadun pisteet (0-100)."""
        score = 100.0
        penalties = {"critical": 25, "high": 15, "medium": 8, "low": 3}
        for issue in issues:
            sev = issue.get("severity", "medium")
            score -= penalties.get(sev, 5)
        return max(0.0, score)

    def _run(self, input_data: CodeReviewInput) -> CodeReviewOutput:
        """CodeReviewAgentin päälogiikka."""
        code = input_data.code
        file_path = input_data.file_path or "<buffer>"

        # Jos tiedostopolku annettu, lue tiedosto
        if not code and input_data.file_path:
            path = Path(input_data.file_path)
            if path.exists():
                code = path.read_text(encoding="utf-8")
            else:
                return CodeReviewOutput(
                    success=False,
                    result=None,
                    message=f"Tiedostoa ei löydy: {input_data.file_path}",
                    agent_type=self.agent_type,
                    issues=[],
                    issue_count=0,
                    severity_levels={},
                    score=0.0,
                )

        if not code:
            return CodeReviewOutput(
                success=False,
                result=None,
                message="Ei koodia tarkistettavaksi.",
                agent_type=self.agent_type,
                issues=[],
                issue_count=0,
                severity_levels={},
                score=0.0,
            )

        # 1. Skannaukset
        all_issues = self._scan_security(code, file_path) + self._scan_quality(code, file_path)

        # 2. Suodata vakauden puutteiden mukaan
        threshold = self._SEVERITY_ORDER.get(input_data.severity_threshold, 2)
        filtered = [i for i in all_issues if self._SEVERITY_ORDER.get(i["severity"], 0) >= threshold]

        # 3. Laske tilastot
        severity_levels: dict[str, int] = {}
        for issue in all_issues:
            sev = issue.get("severity", "unknown")
            severity_levels[sev] = severity_levels.get(sev, 0) + 1

        score = self._calculate_score(all_issues)

        return CodeReviewOutput(
            success=True,
            result={"issue_count": len(all_issues), "score": score},
            message=f"Tarkistus valmis: {len(all_issues)} ongelmaa, pisteet {score}/100.",
            agent_type=self.agent_type,
            issues=filtered,
            issue_count=len(all_issues),
            severity_levels=severity_levels,
            score=score,
        )


__all__ = [
    "DeveloperAgent",
    "DeveloperInput",
    "DeveloperOutput",
    "RefactoringAgent",
    "RefactoringInput",
    "RefactoringOutput",
    "CodeReviewAgent",
    "CodeReviewInput",
    "CodeReviewOutput",
]
