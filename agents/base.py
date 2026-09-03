"""
BaseAgent — kaikkien AIDE-agenttien perusluokka.

Ominaisuudet:
- Pydantic-validoitu rajoite syötteelle (input_schema) ja tulosteelle (output_schema).
- `run()`-metodi, joka ottaa AgentInputin ja palauttaa AgentOutputin.
- `agent_type`-attribuutti, joka tunnistaa agentin tyypin.
- `to_dict()` ja `from_dict()` helperit serialisointia varten.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Optional

from pydantic import BaseModel, Field


class AgentInput(BaseModel):
    """
    Yleinen syöte kaikille agenteille.

    Attributes:
        task: Käsiteltävä tehtävä luonnollisessa kielessä.
        context: Lisäkontekstitietoja (esim. projektin rakenne, tiedostot).
        metadata: Vapaa muotoisuus omaa lisätietoihin.
    """

    task: str = Field(..., min_length=1, description="Käsiteltävä tehtävä.")
    context: dict[str, Any] = Field(default_factory=dict, description="Lisäkonteksti.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Vapaa metadata.")


class AgentOutput(BaseModel):
    """
    Yleinen tuloste kaikille agenteille.

    Attributes:
        success: Onnistuiko toiminto.
        result: Tulos (generaalinen).
        message: Kuvaava viesti (esim. virheilmoitus tai selostus).
        agent_type: Agentin tyyppi.
    """

    success: bool = Field(..., description="Onko toimenpide onnistunut.")
    result: Any = Field(default=None, description="Tulossievu/ vastuu.")
    message: str = Field(default="", description="Kuvaava viesti.")
    agent_type: str = Field(..., description="Agentin tyyppi.")

    def to_dict(self) -> dict[str, Any]:
        """Serialoi AgentOutputin dictiksi (JSON-mukainen)."""
        return self.model_dump()


class BaseAgent(ABC):
    """
    Abstrakti perusluokka kaikille agenteille.

    Alemmat luokat täytyy toteuttaa:
    - `agent_type`-attribuutti (luokkamuuttuja)
    - `_run()`-metodi (varsinaisen logiikan täytäminen)
    - `input_schema` ja `output_schema`-luokkamuuttujat (Pydantic-mallit)
    """

    # Luokkamuuttujat (ylikirjoitettavissa aliluokissa)
    agent_type: ClassVar[str] = "base"
    input_schema: ClassVar[type[BaseModel]] = AgentInput
    output_schema: ClassVar[type[BaseModel]] = AgentOutput

    def __init__(self, ai_provider: Optional[Any] = None, **kwargs: Any) -> None:
        """
        Args:
            ai_provider: AIProvider-instanssi (valinnainen). Joissain agenteissa vaaditaan.
            **kwargs: Lisäasetukset aliluokalle.
        """
        self.ai_provider = ai_provider
        self._config: dict[str, Any] = kwargs

    @abstractmethod
    def _run(self, input_data: AgentInput) -> AgentOutput:
        """
        Toteuta tämä aliluokassa. Tämä on varsinaisen agentin logiikka.

        Args:
            input_data: Validoitu AgentInput.

        Returns:
            AgentOutput.
        """
        ...

    def run(self, task: str, context: Optional[dict[str, Any]] = None, **kwargs: Any) -> AgentOutput:
        """
        Julkinen pääsymetodi. Validoi syötteen, kutsuu `_run()` ja validoi tulosteen.

        Args:
            task: Tehtävä luonnollisessa kielessä.
            context: Lisäkonteksti.
            **kwargs: Lisäargumentit, jotka siirtyvät input_schema:lle.

        Returns:
            Validoitu AgentOutput.
        """
        # 1. Validoi syöte
        input_data = self.input_schema(
            task=task,
            context=context or {},
            **kwargs,
        )

        # 2. Kutsu toteutusta
        output = self._run(input_data)

        # 3. Validoi ja palauta
        if isinstance(output, dict):
            output = self.output_schema(**output)
        elif not isinstance(output, self.output_schema):
            output = self.output_schema(
                success=getattr(output, "success", True),
                result=getattr(output, "result", None),
                message=getattr(output, "message", ""),
                agent_type=self.agent_type,
            )

        # Varmista agent_type on oikein
        output.agent_type = self.agent_type
        return output

    def to_dict(self) -> dict[str, Any]:
        """Serialoi agentin konfiguraation."""
        return {
            "agent_type": self.agent_type,
            "config": self._config,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseAgent":
        """Luo agentin dictistä (ei lataa stateä)."""
        config = data.get("config", {})
        return cls(**config)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(type={self.agent_type})>"
