"""
Testit MemoryAgentille (M13).
"""

import json
import pytest

from agents.knowledge_agent import (
    MemoryAgent,
    MemoryInput,
    MemoryOutput,
    MEMORY_STORE_TYPES,
)


@pytest.fixture
def memory_agent(tmp_path):
    """Palauttaa MemoryAgent-instanssin tilapäiseen tiedistöön."""
    return MemoryAgent(storage_path=str(tmp_path / "memory.json"))


# ===================
# MemoryAgent tests
# ===================


class TestMemoryAgent:
    """Testit MemoryAgentille."""

    def test_agent_type(self, memory_agent):
        """Agentin tyyppi on oikein."""
        assert memory_agent.agent_type == "memory"

    def test_input_schema(self, memory_agent):
        """Input-skeema on oikein."""
        assert memory_agent.input_schema == MemoryInput

    def test_output_schema(self, memory_agent):
        """Output-skeema on oikein."""
        assert memory_agent.output_schema == MemoryOutput

    def test_store_session(self, memory_agent):
        """Tallennus istunnon muistiin toimii."""
        result = memory_agent.run(
            task="Muista minut tähän",
            action="store",
            store_type="session",
            key="user_name",
            value="Alice",
        )
        assert result.success is True
        assert result.key == "user_name"
        assert result.value == "Alice"
        assert result.store_type == "session"

    def test_store_long_term(self, memory_agent):
        """Tallennus pitkäaikaiseen muistiin toimii."""
        result = memory_agent.run(
            task="Muista pitkällä aikavälillä",
            action="store",
            store_type="long_term",
            key="preferred_language",
            value="python",
        )
        assert result.success is True
        assert result.store_type == "long_term"

    def test_retrieve_session(self, memory_agent):
        """Hakeminen istunnon muistista toimii."""
        # Tallenna
        memory_agent.run(
            task="Tallenna",
            action="store",
            store_type="session",
            key="test_key",
            value="test_value",
        )
        # Hae
        result = memory_agent.run(
            task="Hae",
            action="retrieve",
            store_type="session",
            key="test_key",
        )
        assert result.success is True
        assert result.value == "test_value"

    def test_retrieve_nonexistent(self, memory_agent):
        """Olematoman avaimen hakeminen palauttaa epäonnistumisen."""
        result = memory_agent.run(
            task="Hae olematonta",
            action="retrieve",
            store_type="session",
            key="nonexistent_key",
        )
        assert result.success is False
        assert "ei löytynyt" in result.message.lower() or "ei löytynyt" in result.message

    def test_retrieve_with_ttl_expiry(self, memory_agent):
        """Vanhentunut TTL poistetaan."""
        # Tallenna lyhyellä TTL:llä (0.1 sekuntia)
        memory_agent.run(
            task="Tallenna lyhyesti",
            action="store",
            store_type="short_term",
            key="temp_data",
            value="vanhentunut_arvo",
            ttl=1,  # 1 sekunti TTL
        )
        import time
        time.sleep(1.2)  # Odota että vanhenee

        # Yritä hakea — tulisi epäonnistua vanhentuneenä
        result = memory_agent.run(
            task="Hae vanhentunut",
            action="retrieve",
            store_type="short_term",
            key="temp_data",
        )
        # TTL vanhenee ennen hakemista — tulisi epäonnistua
        assert result.success is False or result.value is None

    def test_list_session(self, memory_agent):
        """Listaus toimii."""
        memory_agent.run(
            task="Tallenna 1",
            action="store",
            store_type="session",
            key="key1",
            value="value1",
        )
        memory_agent.run(
            task="Tallenna 2",
            action="store",
            store_type="session",
            key="key2",
            value="value2",
        )

        result = memory_agent.run(
            task="Listaa",
            action="list",
            store_type="session",
        )
        assert result.success is True
        assert result.total_found == 2 or len(result.entries) == 2

    def test_list_with_filter_tags(self, memory_agent):
        """Tunnisteiden suodatus listauksessa toimii."""
        memory_agent.run(
            task="Tallenna tagatuimella",
            action="store",
            store_type="session",
            key="tagged",
            value="arvo",
            metadata={"tags": ["important", "python"]},
        )
        memory_agent.run(
            task="Tallenna ilman tagia",
            action="store",
            store_type="session",
            key="untagged",
            value="arvo2",
        )

        result = memory_agent.run(
            task="Listaa tärkeillä",
            action="list",
            store_type="session",
            filter_tags=["important"],
        )
        assert result.success is True
        assert len(result.entries) == 1
        assert result.entries[0]["key"] == "tagged"

    def test_forget_entry(self, memory_agent):
        """Muistin poistaminen (forget) toimii."""
        # Tallenna
        memory_agent.run(
            task="Tallenna",
            action="store",
            store_type="session",
            key="to_delete",
            value="arvo",
        )
        # Unohda
        result = memory_agent.run(
            task="Unohda",
            action="forget",
            store_type="session",
            key="to_delete",
        )
        assert result.success is True

        # Varmista että haku epäonnistuu
        retrieve_result = memory_agent.run(
            task="Varmista poisto",
            action="retrieve",
            store_type="session",
            key="to_delete",
        )
        assert retrieve_result.success is False

    def test_forget_nonexistent(self, memory_agent):
        """Olematoman muistin poistaminen palauttaa epäonnistumisen."""
        result = memory_agent.run(
            task="Unohda olematonta",
            action="forget",
            store_type="session",
            key="nonexistent",
        )
        assert result.success is False

    def test_clear_store(self, memory_agent):
        """Muistin tyhjentäminen toimii."""
        memory_agent.run(
            task="Tallenna 1",
            action="store",
            store_type="session",
            key="key1",
            value="value1",
        )
        memory_agent.run(
            task="Tallenna 2",
            action="store",
            store_type="session",
            key="key2",
            value="value2",
        )

        result = memory_agent.run(
            task="Tyhjennä",
            action="clear",
            store_type="session",
        )
        assert result.success is True
        assert result.result["cleared"] == 2

        # Varmista että listaus on tyhjä
        list_result = memory_agent.run(
            task="Varmista tyhjeneminen",
            action="list",
            store_type="session",
        )
        assert len(list_result.entries) == 0

    def test_store_with_ttl(self, memory_agent):
        """TTL:n tallennus toimi."""
        result = memory_agent.run(
            task="Tallenna TTL:llä",
            action="store",
            store_type="short_term",
            key="ttl_test",
            value="arvo",
            ttl=3600,
        )
        assert result.success is True

    def test_unknown_action(self, memory_agent):
        """Tuntematon toiminto palauttaa epäonnistumisen."""
        result = memory_agent.run(
            task="Tunematon",
            action="unknown_action",
        )
        assert result.success is False
        assert "tuntematon" in result.message.lower()

    def test_serializes(self, memory_agent):
        """Tulos voidään serialisoida."""
        result = memory_agent.run(
            task="Testaa serialisointia",
            action="store",
            store_type="session",
            key="test",
            value="arvo",
        )
        d = result.to_dict()
        assert d["agent_type"] == "memory"
        assert "key" in d

    def test_multiple_store_types(self, memory_agent):
        """Erilaiset muistimuodot toimivat erikseen."""
        # Session
        memory_agent.run(
            task="Session-tallennus",
            action="store",
            store_type="session",
            key="session_key",
            value="session_value",
        )
        # Long term
        memory_agent.run(
            task="Long-term-tallennus",
            action="store",
            store_type="long_term",
            key="long_key",
            value="long_value",
        )

        # Hae molemmat
        session_result = memory_agent.run(
            task="Hae session",
            action="retrieve",
            store_type="session",
            key="session_key",
        )
        long_result = memory_agent.run(
            task="Hae long-term",
            action="retrieve",
            store_type="long_term",
            key="long_key",
        )
        assert session_result.success is True
        assert long_result.success is True

    def test_persistence(self, memory_agent, tmp_path):
        """Muistin tallennus säilyy tiedostossa."""
        memory_agent.run(
            task="Tallenna",
            action="store",
            store_type="long_term",
            key="persist_key",
            value="persist_value",
        )

        # Lataa uudelleen
        agent2 = MemoryAgent(storage_path=str(tmp_path / "memory.json"))
        assert len(agent2._stores["long_term"]) > 0


class TestMemoryAgentModuleLevel:
    """Moduulitasolla olevat testit."""

    def test_memory_store_types_exist(self):
        """Muistin tavaralajit ovat olemassa."""
        assert len(MEMORY_STORE_TYPES) >= 3

    def test_store_types_have_ttl(self):
        """Jokaisella tavaralajilla on TTL-asetukset."""
        for store_type, config in MEMORY_STORE_TYPES.items():
            assert "ttl" in config
            assert "max_size" in config
            assert "description" in config

    def test_agent_importable_from_package(self):
        """Agentti on tuotavissa paketista."""
        from agents import MemoryAgent as MA
        assert MA.agent_type == "memory"
