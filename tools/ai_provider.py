"""
AIProvider — yhteinen rajapinta LLM-päätteille OpenRouterin kautta.

Luku .env-varmistuksesta:
- OPENROUTER_API_KEY  (pakollinen)
- DEFAULT_MODEL       (valinnainen, oletus: openai/gpt-4o-mini)
- OPENROUTER_BASE_URL (valinnainen, oletus: https://openrouter.ai/api)
"""

from __future__ import annotations

import os
from typing import Any, Optional

from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel, Field


class AIResponse(BaseModel):
    """Pydantic-validoitu vastaus yhdistämisestä LLM:lle."""

    text: str = Field(..., description="Generoitu teksti.")
    model: str = Field(..., description="Käytetty mallin nimi.")
    usage: dict[str, Any] = Field(
        default_factory=dict, description="Token-käytön tiedot (prompt / completion / total)."
    )


class AIProvider:
    """
    Yksinkertainen AIProvider OpenRouterille.

    Usage:
        provider = AIProvider()
        response: AIResponse = provider.chat("Kerää projektin tiedostot.")
    """

    DEFAULT_BASE_URL = "https://openrouter.ai/api"
    DEFAULT_MODEL = "openai/gpt-4o-mini"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
    ) -> None:
        resolved_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not resolved_key:
            raise ValueError(
                "OPENROUTER_API_KEY -ympäristömuuttuja on asetettava tai "
                "annettava api_key parametrina."
            )

        self.api_key = resolved_key
        self.base_url = (base_url or os.getenv("OPENROUTER_BASE_URL") or self.DEFAULT_BASE_URL).rstrip("/")
        self.default_model = default_model or os.getenv("DEFAULT_MODEL") or self.DEFAULT_MODEL

        # Sync client (oletus)
        self._client: OpenAI = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={
                "HTTP-Referer": "https://github.com/aide-env/ai-development-environment",
                "X-Title": "AI Development Environment (AIDE)",
            },
        )
        # Async client (myöhemmille tarvekäsitteille)
        self._async_client: AsyncOpenAI = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={
                "HTTP-Referer": "https://github.com/aide-env/ai-development-environment",
                "X-Title": "AI Development Environment (AIDE)",
            },
        )

    # ------------------------------------------------------------------ #
    # Sync
    # ------------------------------------------------------------------ #
    def chat(
        self,
        prompt: str,
        system_prompt: str = "Olet avulias assistentti. Vastaa selkeästi ja rakenteellisesti.",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **extra_kwargs: Any,
    ) -> AIResponse:
        """
        Sync-chatin yksinkertainen käänteinen kutsu.
        Palauttaa AIResponse -objektin.
        """
        model = model or self.default_model
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        kwargs.update(extra_kwargs)

        raw = self._client.chat.completions.create(**kwargs)
        choice = raw.choices[0]
        usage = raw.usage.model_dump() if raw.usage else {}
        return AIResponse(
            text=choice.message.content or "",
            model=model,
            usage=usage,
        )

    # ------------------------------------------------------------------ #
    # Async
    # ------------------------------------------------------------------ #
    async def chat_async(
        self,
        prompt: str,
        system_prompt: str = "Olet avulias assistentti. Vastaa selkeästi ja rakenteellisesti.",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **extra_kwargs: Any,
    ) -> AIResponse:
        """Async-chatin yksinkertainen käänteinen kutsu."""
        model = model or self.default_model
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        kwargs.update(extra_kwargs)

        raw = await self._async_client.chat.completions.create(**kwargs)
        choice = raw.choices[0]
        usage = raw.usage.model_dump() if raw.usage else {}
        return AIResponse(
            text=choice.message.content or "",
            model=model,
            usage=usage,
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def get_config(self) -> dict[str, str]:
        """Palauttaa nykyisen konfiguraation selväkäs paketiksi (ei API-avainta)."""
        return {
            "base_url": self.base_url,
            "default_model": self.default_model,
        }

    @staticmethod
    def load_env(env_path: str = ".env") -> None:
        """Lataa .env-tiedosto ympäristömuuttujiin (jos python-dotenv on asennettu)."""
        try:
            from dotenv import load_dotenv  # type: ignore[import-not-found]

            if os.path.exists(env_path):
                load_dotenv(env_path)
        except ImportError:
            # Jos dotenv ei ole asennettu, emme ole estämässä toiminnallisuutta.
            # Käyttäjä voi asettaa ympäristömuuttujat manuaalisesti.
            pass


__all__ = ["AIProvider", "AIResponse"]
