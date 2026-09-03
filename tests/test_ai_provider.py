"""
Testit AIProvider-luokalle (tools/ai_provider.py).

Käytetään mock-olioita OpenAI-asiakkaan sijaan, jotta emme tarvitse oikeaa API-avainta.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from tools.ai_provider import AIProvider, AIResponse


class TestAIProviderInit:
    """AIProviderin alustus ja konfiguraatio."""

    def test_init_requires_api_key(self):
        """AIProvider vaatii API-avan — ilman sen heittää ValueErrorin."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENROUTER_API_KEY", None)
            with pytest.raises(ValueError, match="API_KEY"):
                AIProvider()

    def test_init_with_explicit_api_key(self, monkeypatch):
        """AIProvider vastaanottaa api_key parametrina suoraan."""
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        provider = AIProvider(api_key="sk-or-v1-explicit-key")
        assert provider.api_key == "sk-or-v1-explicit-key"

    def test_init_loads_from_env(self, mock_api_key):
        """AIProvider lukee avaimen ympäristömuuttujasta."""
        provider = AIProvider()
        assert provider.api_key == "sk-or-v1-test-key"
        assert provider.default_model == "openai/gpt-4o-mini"
        assert provider.base_url == "https://openrouter.ai/api"

    def test_init_custom_config(self, mock_api_key):
        """AIProvider hyväksyy mukautetut asetukset."""
        provider = AIProvider(
            api_key="sk-or-v1-custom",
            base_url="https://custom.openrouter.ai/api",
            default_model="anthropic/claude-3",
        )
        assert provider.base_url == "https://custom.openrouter.ai/api"
        assert provider.default_model == "anthropic/claude-3"

    def test_get_config_excludes_api_key(self, mock_api_key):
        """get_config() ei palauta API-avainta."""
        provider = AIProvider()
        config = provider.get_config()
        assert "api_key" not in config
        assert config["base_url"] == "https://openrouter.ai/api"
        assert config["default_model"] == "openai/gpt-4o-mini"

    def test_load_env_file(self, tmp_path, monkeypatch):
        """load_env() lataa .env-tiedoston jos python-dotenv on asennettu."""
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        env_file = tmp_path / ".env"
        env_file.write_text("OPENROUTER_API_KEY=sk-or-v1-from-env-file\n")
        AIProvider.load_env(str(env_file))
        # Tämä asettaa OPENROUTER_API_KEY -muuttujan, jonka voimme lukea
        assert os.getenv("OPENROUTER_API_KEY") == "sk-or-v1-from-env-file"


class TestAIResponse:
    """Testit AIResponse-modelille."""

    def test_ai_response_is_pydantic_model(self):
        """AIResponse on Pydantic-malli."""
        resp = AIResponse(text="Hei!", model="test-model", usage={"total": 10})
        assert resp.text == "Hei!"
        assert resp.model == "test-model"
        assert resp.usage["total"] == 10

    def test_ai_response_serializes(self):
        """AIResponse voidaan serialisoida JSON-muotoon."""
        resp = AIResponse(text="Vastaus", model="gpt-4", usage={})
        serialized = resp.model_dump()
        assert serialized["text"] == "Vastaus"
        assert serialized["model"] == "gpt-4"


class TestAIProviderChat:
    """Testit chat()-metodille mock-olioilla."""

    @pytest.fixture
    def mock_provider(self, mock_api_key):
        """Luo mockattu AIProvider, jossa _client on mock-olio."""
        provider = AIProvider()
        # Korvaa _client mock-olioilla — OpenAI-asiakas ei yhdistä konstruktorissa
        provider._client = MagicMock()
        provider._async_client = MagicMock()
        return provider

    def test_chat_returns_ai_response(self, mock_provider):
        """chat() palauttaa AIResponse-olion."""
        mock_choice = MagicMock()
        mock_choice.message.content = "Testivastaus"
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = MagicMock()
        mock_completion.usage.model_dump.return_value = {"prompt_tokens": 5, "completion_tokens": 3}
        mock_provider._client.chat.completions.create.return_value = mock_completion

        response = mock_provider.chat("Testikysymys")
        assert isinstance(response, AIResponse)
        assert response.text == "Testivastaus"
        assert response.model == mock_provider.default_model

    def test_chat_uses_system_prompt(self, mock_provider):
        """chat() käyttää järjestelmäviestiä."""
        mock_choice = MagicMock()
        mock_choice.message.content = "OK"
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = MagicMock()
        mock_completion.usage.model_dump.return_value = {}
        mock_provider._client.chat.completions.create.return_value = mock_completion

        mock_provider.chat("Testi", system_prompt="Olet testi-assistentti.")

        call_args = mock_provider._client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "Olet testi-assistentti."
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Testi"

    def test_chat_async_returns_response(self, mock_provider):
        """chat_async() toimii async-moodissa."""
        import asyncio

        mock_choice = MagicMock()
        mock_choice.message.content = "Async-vastaus"
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = MagicMock()
        mock_completion.usage.model_dump.return_value = {"total_tokens": 10}

        async def mock_create(*args, **kwargs):
            return mock_completion

        mock_provider._async_client = MagicMock()
        mock_provider._async_client.chat.completions.create = mock_create

        response = asyncio.run(mock_provider.chat_async("Async-testi"))
        assert isinstance(response, AIResponse)
        assert response.text == "Async-vastaus"

    def test_chat_passes_model_parameter(self, mock_provider):
        """chat() lähettää mukautun nonmallin."""
        mock_choice = MagicMock()
        mock_choice.message.content = "OK"
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = MagicMock()
        mock_completion.usage.model_dump.return_value = {}
        mock_provider._client.chat.completions.create.return_value = mock_completion

        mock_provider.chat("Testi", model="anthropic/claude-3-opus")

        call_args = mock_provider._client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "anthropic/claude-3-opus"

    def test_chat_with_max_tokens(self, mock_provider):
        """chat() lähettää max_tokens-parametrin jos se on annettu."""
        mock_choice = MagicMock()
        mock_choice.message.content = "OK"
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = MagicMock()
        mock_completion.usage.model_dump.return_value = {}
        mock_provider._client.chat.completions.create.return_value = mock_completion

        mock_provider.chat("Testi", max_tokens=100)

        call_args = mock_provider._client.chat.completions.create.call_args
        assert call_args.kwargs["max_tokens"] == 100
