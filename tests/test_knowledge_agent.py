"""
Testit KnowledgeAgentille (M13).
"""

import json
import pytest

from agents.knowledge_agent import (
    KnowledgeAgent,
    KnowledgeAgentInput,
    KnowledgeAgentOutput,
    INDEX_TYPES,
)


@pytest.fixture
def knowledge_agent(tmp_path):
    """Palauttaa KnowledgeAgent-instanssin tilapäiseen tiedistöön."""
    return KnowledgeAgent(storage_path=str(tmp_path / "knowledge.json"))


# ===================
# KnowledgeAgent tests
# ===================


class TestKnowledgeAgent:
    """Testit KnowledgeAgentille."""

    def test_agent_type(self, knowledge_agent):
        """Agentin tyyppi on oikein."""
        assert knowledge_agent.agent_type == "knowledge"

    def test_input_schema(self, knowledge_agent):
        """Input-skeema on oikein."""
        assert knowledge_agent.input_schema == KnowledgeAgentInput

    def test_output_schema(self, knowledge_agent):
        """Output-skeema on oikein."""
        assert knowledge_agent.output_schema == KnowledgeAgentOutput

    def test_store_concept(self, knowledge_agent):
        """Konseptin tallennus toimii."""
        result = knowledge_agent.run(
            task="Tallenna konsepti",
            operation="store",
            knowledge_type="concept",
            content="Dependency injection on suunnittelumalli.",
            tags=["python", "design"],
        )
        assert result.success is True
        assert result.knowledge_id  # Ei-tyhjä

    def test_store_with_source(self, knowledge_agent):
        """Lähteen tallennus toimii."""
        result = knowledge_agent.run(
            task="Tallenna lähteellä",
            operation="store",
            knowledge_type="pattern",
            content="Käytetään singleton-mallia loggeroinnin yhteydessä.",
            tags=["logging"],
            source="agents/logger.py",
        )
        assert result.success is True

    def test_store_and_retrieve(self, knowledge_agent):
        """Tallennuksen ja hakemisen perustoimi."""
        # Tallenna
        store_result = knowledge_agent.run(
            task="Tallenna",
            operation="store",
            knowledge_type="concept",
            content="REST API on tilasta riippymätön rajapinta.",
            tags=["api", "rest"],
        )
        # Hae
        retrieve_result = knowledge_agent.run(
            task="Hae",
            operation="retrieve",
            knowledge_id=store_result.knowledge_id,
        )
        assert retrieve_result.success is True
        assert retrieve_result.knowledge_id == store_result.knowledge_id
        assert "content" in retrieve_result.result

    def test_search_by_query(self, knowledge_agent):
        """Haku kyselyllä toimii."""
        # Tallenna useampi kohde
        knowledge_agent.run(
            task="Tallenna 1",
            operation="store",
            knowledge_type="concept",
            content="Python on ohjelmointikieli.",
            tags=["python"],
        )
        knowledge_agent.run(
            task="Tallenna 2",
            operation="store",
            knowledge_type="concept",
            content="Java on myös ohjelmointikieli.",
            tags=["java"],
        )
        # Hae
        result = knowledge_agent.run(
            task="Hae",
            operation="search",
            query="python",
        )
        assert result.success is True
        assert result.total_found > 0

    def test_search_by_tag(self, knowledge_agent):
        """Haku tunnisteen perusteella toimii."""
        knowledge_agent.run(
            task="Tallenna merkitus",
            operation="store",
            knowledge_type="concept",
            content="Flask on Python-web-framework.",
            tags=["flask", "web", "python"],
        )
        result = knowledge_agent.run(
            task="Hae merkinnällä",
            operation="search",
            query="flask",
        )
        assert result.success is True
        assert result.total_found > 0

    def test_retrieve_nonexistent(self, knowledge_agent):
        """Olematonten hakeminen palauttaa epäonnistumisen."""
        result = knowledge_agent.run(
            task="Hae olematonta",
            operation="retrieve",
            knowledge_id="0000000000000000",
        )
        assert result.success is False

    def test_delete_entry(self, knowledge_agent):
        """Poisto toimii."""
        # Tallenna
        store_result = knowledge_agent.run(
            task="Tallenna",
            operation="store",
            knowledge_type="snippet",
            content="print('Hello, World!')",
        )
        # Poista
        delete_result = knowledge_agent.run(
            task="Poista",
            operation="delete",
            knowledge_id=store_result.knowledge_id,
        )
        assert delete_result.success is True

        # Varmista että haku ei löydä
        retrieve_result = knowledge_agent.run(
            task="Varmista poisto",
            operation="retrieve",
            knowledge_id=store_result.knowledge_id,
        )
        assert retrieve_result.success is False

    def test_delete_nonexistent(self, knowledge_agent):
        """Poistoetaan olematonta palauttaa epäonnistumisen."""
        result = knowledge_agent.run(
            task="Poista olematonta",
            operation="delete",
            knowledge_id="0000000000000000",
        )
        assert result.success is False

    def test_index_entry(self, knowledge_agent):
        """Indeksointi päivittää kenttiä."""
        # Tallenna
        store_result = knowledge_agent.run(
            task="Tallenna",
            operation="store",
            knowledge_type="concept",
            content="Testikonsepti.",
            tags=["test"],
        )
        # Indeksoi
        index_result = knowledge_agent.run(
            task="Indeksoi",
            operation="index",
            knowledge_id=store_result.knowledge_id,
            index_fields=["content"],
            context={"content": "Indeksoitu sisältö"},
        )
        assert index_result.success is True
        assert "index_name" in index_result.model_dump()

    def test_unknown_operation(self, knowledge_agent):
        """Tuntematon operaatio palauttaa epäonnistumisen."""
        result = knowledge_agent.run(
            task="Tunematon",
            operation="unknown_op",
        )
        assert result.success is False
        assert "tuntematon" in result.message.lower() or "virhe" in result.message.lower()

    def test_auto_tags_extraction(self, knowledge_agent):
        """Automaattiset tunnisteet extrakoituu."""
        result = knowledge_agent.run(
            task="Auto-tunnisteet",
            operation="store",
            knowledge_type="concept",
            content="""
import os
import sys

def my_function():
    pass

class MyClass:
    pass
            """,
        )
        assert result.success is True
        # Tunnisteet tulisi sisältää importit
        entries = knowledge_agent._index
        for entry in entries.values():
            if entry["id"] == result.knowledge_id:
                # Tarkista että jokin tunniste on löydetty
                assert len(entry["tags"]) > 0

    def test_store_persistence(self, knowledge_agent, tmp_path):
        """Tallennus säilyuu tiedostoon."""
        knowledge_agent.run(
            task="Tallenna",
            operation="store",
            knowledge_type="concept",
            content="Pysyvä testi.",
            tags=["persist"],
        )

        # Lataa uudelleen
        agent2 = KnowledgeAgent(storage_path=str(tmp_path / "knowledge.json"))
        assert len(agent2._index) > 0

    def test_search_confidence(self, knowledge_agent):
        """Hakatuloksen luottamus laskeutuu."""
        knowledge_agent.run(
            task="Tallenna",
            operation="store",
            knowledge_type="concept",
            content="Tämä on tärkeä tieto.",
            tags=["important"],
        )
        result = knowledge_agent.run(
            task="Hae tärkee",
            operation="search",
            query="important",
        )
        assert result.confidence >= 0

    def test_serializes(self, knowledge_agent):
        """Tulos voidaan serialisoida."""
        result = knowledge_agent.run(
            task="Testaa serialisointia",
            operation="store",
            knowledge_type="concept",
            content="Testisisältö serialisointia varten.",
        )
        d = result.to_dict()
        assert d["agent_type"] == "knowledge"
        assert "knowledge_id" in d


class TestKnowledgeAgentModuleLevel:
    """Moduulitasolla olevat testit."""

    def test_index_types_exist(self):
        """Indeksointityyppien sanakirja on olemassa."""
        assert len(INDEX_TYPES) >= 3

    def test_index_types_have_extractors(self):
        """Jokaisella indeksoinnitetyyppillä on extraktorit."""
        for idx, config in INDEX_TYPES.items():
            assert "name" in config
            assert "description" in config
            assert "extractors" in config
            assert isinstance(config["extractors"], list)

    def test_agent_importable_from_package(self):
        """Agentti on tuotavissa paketista."""
        from agents import KnowledgeAgent as KA
        assert KA.agent_type == "knowledge"
