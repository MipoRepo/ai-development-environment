"""
Testit ContextCompilerAgentille (M13).
"""

from pathlib import Path

import pytest

from agents.knowledge_agent import (
    ContextCompilerAgent,
    ContextCompilerInput,
    ContextCompilerOutput,
)


@pytest.fixture
def context_compiler():
    """Palauttaa ContextCompilerAgent-instanssin."""
    return ContextCompilerAgent()


@pytest.fixture
def sample_file(tmp_path):
    """Luo testitiedoston."""
    file_path = tmp_path / "sample.py"
    file_path.write_text("""
import os
import sys

'''Sample module.'''

class MyClass:
    '''A sample class.'''
    pass

def my_function(arg1, arg2):
    '''A sample function.'''
    return arg1 + arg2

# FIXME: This should be refactored
CONSTANT = "value"
""")
    return str(file_path)


@pytest.fixture
def broken_file(tmp_path):
    """Luo rikkinäisen testitiedoston."""
    file_path = tmp_path / "broken.py"
    file_path.write_text("def broken(\n    if True\n")
    return str(file_path)


# ===================
# ContextCompilerAgent tests
# ===================


class TestContextCompilerAgent:
    """Testit ContextCompilerAgentille."""

    def test_agent_type(self, context_compiler):
        """Agentin tyyppi on oikein."""
        assert context_compiler.agent_type == "context_compiler"

    def test_input_schema(self, context_compiler):
        """Input-skeema on oikein."""
        assert context_compiler.input_schema == ContextCompilerInput

    def test_output_schema(self, context_compiler):
        """Output-skeema on oikein."""
        assert context_compiler.output_schema == ContextCompilerOutput

    def test_basic_compilation_text(self, context_compiler, sample_file):
        """Tekstimuotoisen kontekstin kääntäminen toimii."""
        result = context_compiler.run(
            task="Käännä konteksti",
            sources=[sample_file],
            target_format="text",
        )
        assert result.success is True
        assert len(result.compiled_context) > 0
        assert result.total_sources == 1

    def test_compilation_json(self, context_compiler, sample_file):
        """JSON-muotoisen kontekstin kääntäminen toimii."""
        result = context_compiler.run(
            task="Käännä JSON:ksi",
            sources=[sample_file],
            target_format="json",
        )
        assert result.success is True
        assert "sources" in result.compiled_context

    def test_compilation_markdown(self, context_compiler, sample_file):
        """Markdown-muotoisen kontekstin kääntäminen toimii."""
        result = context_compiler.run(
            task="Käännä markdowniksi",
            sources=[sample_file],
            target_format="markdown",
        )
        assert result.success is True
        assert "## " in result.compiled_context or "#" in result.compiled_context

    def test_compilation_summary(self, context_compiler, sample_file):
        """Tiivistelmän kääntäminen toimii."""
        result = context_compiler.run(
            task="Tiivistä konteksti",
            sources=[sample_file],
            target_format="summary",
        )
        assert result.success is True
        assert len(result.compiled_context) > 0

    def test_empty_sources(self, context_compiler):
        """Tyhjät lähteet palauttavat epäonnistumisen."""
        result = context_compiler.run(
            task="Tyhjät lähteet",
            sources=[],
        )
        assert result.success is False

    def test_nonexistent_source(self, context_compiler):
        """Olematon lähde käsitellään merkkijonona."""
        result = context_compiler.run(
            task="Käsittele merkkijono",
            sources=["Tämä on merkkijono eikä tiedosto."],
        )
        assert result.success is True
        assert len(result.compiled_context) > 0

    def test_multiple_sources(self, context_compiler, sample_file):
        """Useiden lähtsten käsittely toimii."""
        result = context_compiler.run(
            task="Monet lähteet",
            sources=[sample_file, "Lisäkonteksti tähän."],
            target_format="text",
        )
        assert result.success is True
        assert result.total_sources == 2

    def test_context_filters_imports(self, context_compiler, sample_file):
        """Importtien suodatus toimii."""
        result = context_compiler.run(
            task="Suodata importit",
            sources=[sample_file],
            context_filters=["imports"],
        )
        assert result.success is True
        assert "import" in result.compiled_context.lower() or "os" in result.compiled_context

    def test_context_filters_classes(self, context_compiler, sample_file):
        """Luokkien suodatus toimii."""
        result = context_compiler.run(
            task="Suodata luokat",
            sources=[sample_file],
            context_filters=["classes"],
        )
        assert result.success is True
        assert "MyClass" in result.compiled_context

    def test_context_filters_functions(self, context_compiler, sample_file):
        """Funktioiden suodatus toimii."""
        result = context_compiler.run(
            task="Suodata funktiot",
            sources=[sample_file],
            context_filters=["functions"],
        )
        assert result.success is True
        assert "my_function" in result.compiled_context

    def test_context_filters_errors(self, context_compiler, sample_file):
        """Virheiden suodatus toimii."""
        result = context_compiler.run(
            task="Suodata virheet",
            sources=[sample_file],
            context_filters=["errors"],
        )
        assert result.success is True
        assert "FIXME" in result.compiled_context or "TODO" in result.compiled_context

    def test_context_filters_docstrings(self, context_compiler, sample_file):
        """Docstringien suodatus toimii."""
        result = context_compiler.run(
            task="Suodata docstringit",
            sources=[sample_file],
            context_filters=["docstrings"],
        )
        assert result.success is True

    def test_context_filters_constants(self, context_compiler, sample_file):
        """Vakioiden suodatus toimii."""
        result = context_compiler.run(
            task="Suodata vakiot",
            sources=[sample_file],
            context_filters=["constants"],
        )
        assert result.success is True
        assert "CONSTANT" in result.compiled_context

    def test_broken_code_handling(self, context_compiler, broken_file):
        """Rikkinäinen koodi käsitellää virheellisesti mutta ei kaadu."""
        result = context_compiler.run(
            task="Käytä rikkinäistä",
            sources=[broken_file],
            context_filters=["classes", "functions"],
        )
        # Pitäisi silti palauttaa jokin konteksti
        assert result.success is True

    def test_priority_sources(self, context_compiler, sample_file):
        """Prioriteetit lähteille toimivat."""
        result = context_compiler.run(
            task="Priorisoi lähteet",
            sources=[sample_file, "Toinen lähde."],
            priority_sources=[sample_file],
            target_format="text",
        )
        assert result.success is True
        assert sample_file in result.priority_ranking
        assert result.priority_ranking[0] == sample_file

    def test_max_context_length(self, context_compiler, sample_file):
        """Maksimipituus rajoittaa tuloksen."""
        result = context_compiler.run(
            task="Lyhennä konteksti",
            sources=[sample_file],
            target_format="text",
            max_context_length=100,
        )
        assert result.success is True
        assert len(result.compiled_context) <= 100 + 50  # Sallii pientä ylikuortaa leikkausalueessa

    def test_unknown_format_defaults(self, context_compiler, sample_file):
        """Tuntematon muoto käyttää tekstiä."""
        result = context_compiler.run(
            task="Tuntematon muoto",
            sources=[sample_file],
            target_format="unknown_format",
        )
        assert result.success is True

    def test_source_summaries_populated(self, context_compiler, sample_file):
        """Lähdesummat ovat täytetty."""
        result = context_compiler.run(
            task="Tarkista summat",
            sources=[sample_file],
            target_format="text",
        )
        assert result.success is True
        assert sample_file in result.source_summaries
        assert len(result.source_summaries[sample_file]) > 0

    def test_serializes(self, context_compiler, sample_file):
        """Tulos voidään serialisoida."""
        result = context_compiler.run(
            task="Testaa serialisointia",
            sources=[sample_file],
            target_format="text",
        )
        d = result.to_dict()
        assert d["agent_type"] == "context_compiler"
        assert "compiled_context" in d
        assert "source_summaries" in d


class TestContextCompilerAgentModuleLevel:
    """Moduulitasolla olevat testit."""

    def test_agent_importable_from_package(self):
        """Agentti on tuotavissa paketista."""
        from agents import ContextCompilerAgent as CCA
        assert CCA.agent_type == "context_compiler"
