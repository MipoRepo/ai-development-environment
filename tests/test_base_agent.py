"""
Testit BaseAgent-luokalle (agents/base.py).

Käytämään konkreettista aliluokkaa testaukseen, koska BaseAgent on abstrakti.
"""

import pytest

from agents.base import AgentInput, AgentOutput, BaseAgent


class ConcreteAgent(BaseAgent):
    """Testaamista varten: konkreettinen BaseAgent-aliluokka."""

    agent_type = "concrete_test"
    input_schema = AgentInput
    output_schema = AgentOutput

    def _run(self, input_data: AgentInput) -> AgentOutput:
        """Palauttaa syötteen käännettynä."""
        return AgentOutput(
            success=True,
            result=f"Käsitelty: {input_data.task}",
            message=f"Tehtävä {input_data.task} suoritettu.",
            agent_type=self.agent_type,
        )


class ConcreteErrorAgent(BaseAgent):
    """Testaamista varten: virhe- agentti."""

    agent_type = "error_test"
    input_schema = AgentInput
    output_schema = AgentOutput

    def _run(self, input_data: AgentInput) -> AgentOutput:
        raise RuntimeError("Testivirhe!")


class TestAgentInput:
    """Testit AgentInput-mallille."""

    def test_input_defaults(self):
        """AgentInput-olekolle oletusarvot."""
        inp = AgentInput(task="Testi")
        assert inp.task == "Testi"
        assert inp.context == {}
        assert inp.metadata == {}

    def test_input_with_context(self):
        """AgentInput vastaanottaa kontekstin."""
        inp = AgentInput(
            task="Tee jotain",
            context={"files": ["main.py"]},
            metadata={"priority": "high"},
        )
        assert inp.context["files"] == ["main.py"]
        assert inp.metadata["priority"] == "high"

    def test_input_requires_task(self):
        """AgentInput vaatii task-kentän."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AgentInput(task="")


class TestAgentOutput:
    """Testit AgentOutput-mallille."""

    def test_output_defaults(self):
        """AgentOutput-olekolle oletusarvot."""
        out = AgentOutput(success=True, agent_type="test")
        assert out.success is True
        assert out.result is None
        assert out.message == ""
        assert out.agent_type == "test"

    def test_output_to_dict(self):
        """AgentOutput voidaan serialisoida dictiksi."""
        out = AgentOutput(
            success=True,
            result={"key": "value"},
            message="Valmis",
            agent_type="test",
        )
        d = out.to_dict()
        assert d["success"] is True
        assert d["result"] == {"key": "value"}
        assert d["message"] == "Valmis"
        assert d["agent_type"] == "test"


class TestBaseAgent:
    """Testit BaseAgent-perustoiminnoille."""

    def test_agent_repr(self):
        """Agentin __repr__ näyttää tyypin."""
        agent = ConcreteAgent()
        repr_str = repr(agent)
        assert "ConcreteAgent" in repr_str
        assert "concrete_test" in repr_str

    def test_agent_to_dict(self):
        """Agentin konfiguraatio serialisoidaan."""
        agent = ConcreteAgent(ai_provider=None, extra_option="arvo")
        d = agent.to_dict()
        assert d["agent_type"] == "concrete_test"
        assert d["config"]["extra_option"] == "arvo"

    def test_agent_from_dict(self):
        """Agentin luominen dictistä."""
        agent = ConcreteAgent.from_dict({
            "agent_type": "concrete_test",
            "config": {"debug": True},
        })
        assert agent.agent_type == "concrete_test"
        assert agent._config["debug"] is True

    def test_run_validates_input(self):
        """run() validoi syötteen ennen suoritusta."""
        agent = ConcreteAgent()
        result = agent.run("Testitehtävä")
        assert isinstance(result, AgentOutput)
        assert result.success is True
        assert result.agent_type == "concrete_test"

    def test_run_with_context(self):
        """run() välittää kontekstin."""
        agent = ConcreteAgent()
        result = agent.run("Tehtävä", context={"project": "AIDE"})
        assert result.success is True
        assert "käsitelty" in result.result.lower() or "Testitehtävä" in result.result or "käsitelty" in str(result.result)

    def test_run_with_kwargs(self):
        """run() ottaa vastaan ylimääräisiä argumentteja."""
        agent = ConcreteAgent()
        result = agent.run("Tehtävä", metadata={"custom": True})
        assert result.success is True

    def test_error_propagates(self):
        """Virheet _run():sta nousevat run()-metodissa."""
        agent = ConcreteErrorAgent()
        with pytest.raises(RuntimeError, match="Testivirhe"):
            agent.run("Virheellinen tehtävä")

    def test_run_accepts_string_input_only(self):
        """run() hyväksyy pelkästään merkkijonon tehtävänä."""
        agent = ConcreteAgent()
        # Tämä tulisi toimia — pelkkä string
        result = agent.run("Yksinkertainen tehtävä")
        assert result.success is True

    def test_custom_input_schema(self):
        """Alemmat voivat määrittää omat input_schema:it."""
        from pydantic import BaseModel, Field

        class CustomInput(BaseModel):
            task: str
            custom_field: str = Field(default="oletus")

        class CustomAgent(BaseAgent):
            agent_type = "custom"
            input_schema = CustomInput
            output_schema = AgentOutput

            def _run(self, input_data: CustomInput) -> AgentOutput:
                return AgentOutput(
                    success=True,
                    result=input_data.custom_field,
                    message="OK",
                    agent_type=self.agent_type,
                )

        agent = CustomAgent()
        result = agent.run("Tehtävä", custom_field="erityinen-arvo")
        assert result.result == "erityinen-arvo"
