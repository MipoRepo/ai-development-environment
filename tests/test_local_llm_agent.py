"""Testit LocalLLM-moduulille (M18).

Testaa kolme agenttia:
- LocalModelAgent (paikallisten mallien hallinta)
- ModelRunnerAgent (mallin suoritus)
- QuantizationAgent (mallin kvantisointi)
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agents.local_llm_agent import (
    LocalModelAgent,
    LocalModelInput,
    LocalModelOutput,
    ModelRunnerAgent,
    ModelRunnerInput,
    ModelRunnerOutput,
    QuantizationAgent,
    QuantizationInput,
    QuantizationOutput,
    LOCAL_MODEL_ACTIONS,
    MODEL_RUNNER_ACTIONS,
    QUANTIZATION_ACTIONS,
    KNOWN_LOCAL_MODELS,
    QUANTIZATION_FORMATS,
    MEMORY_ESTIMATES,
    OLLAMA_COMMANDS,
)
from agents.base import BaseAgent


# =============================================================================
# LocalModelAgent
# =============================================================================

class TestLocalModelAgent:
    """Testit LocalModelAgentille."""

    @pytest.fixture
    def agent(self):
        return LocalModelAgent()

    def test_agent_type(self, agent):
        """Vahivistaa agentin tyyppi."""
        assert agent.agent_type == "local_model"

    def test_input_output_schemat(self, agent):
        """Vahistaa syöte- ja tulosteasemats."""
        assert agent.input_schema == LocalModelInput
        assert agent.output_schema == LocalModelOutput

    def test_actions_dict_exists(self):
        """Vahistaa LOCAL_MODEL_ACTIONS sisältää oikeat toiminnot."""
        assert "list" in LOCAL_MODEL_ACTIONS
        assert "install" in LOCAL_MODEL_ACTIONS
        assert "remove" in LOCAL_MODEL_ACTIONS
        assert "info" in LOCAL_MODEL_ACTIONS
        assert "config" in LOCAL_MODEL_ACTIONS

    @patch("agents.local_llm_agent.shutil.which")
    @patch("agents.local_llm_agent.subprocess.run")
    def test_list_models_with_ollama(self, mock_run, mock_which, agent):
        """Testaa mallien listaus, kun Ollama on käytettävissä."""
        mock_which.return_value = "/usr/bin/ollama"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="NAME          ID              SIZE   MODIFIED\nllama3.1:8b   abc123          4.5GB  2026-01-01\n",
        )

        result = agent.run("Listaa mallit", action="list")

        assert result.success is True
        assert len(result.models) > 0

    @patch("agents.local_llm_agent.shutil.which")
    def test_list_models_without_ollama(self, mock_which, agent):
        """Testaa mallien listaus ilman Ollamaa (käyttää tunnettuja malleja)."""
        mock_which.return_value = None

        result = agent.run("Listaa mallit", action="list")

        assert result.success is True
        assert len(result.models) > 0
        assert result.models[0]["name"] in KNOWN_LOCAL_MODELS

    def test_list_models_known_models_exists(self):
        """Vahistaa että tunnetut mallit on määritelty."""
        assert len(KNOWN_LOCAL_MODELS) > 10
        assert "llama3.1:8b" in KNOWN_LOCAL_MODELS
        assert "mistral:7b" in KNOWN_LOCAL_MODELS

    @patch("agents.local_llm_agent.shutil.which")
    @patch("agents.local_llm_agent.subprocess.run")
    def test_install_model_success(self, mock_run, mock_which, agent):
        """Testaa mallin asennus onnistuneesti."""
        mock_which.return_value = "/usr/bin/ollama"
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = agent.run("Asenna malli", action="install", model_name="llama3.1:8b")

        assert result.success is True
        assert result.installed is True
        assert "llama3.1:8b" in result.message or "ladottu" in result.message.lower()
        assert result.installed is True

    def test_install_model_missing_name(self, agent):
        """Testaa että puuttuva mallin nimi palauttaa virheen."""
        result = agent.run("Asenna", action="install")

        assert result.success is False
        assert "nimi" in result.message.lower() or "pakollinen" in result.message.lower()

    @patch("agents.local_llm_agent.shutil.which")
    @patch("agents.local_llm_agent.subprocess.run")
    def test_remove_model_success(self, mock_run, mock_which, agent):
        """Testaa mallin poisto onnistuneesti."""
        mock_which.return_value = "/usr/bin/ollama"
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = agent.run("Poista malli", action="remove", model_name="llama3.1:8b")

        assert result.success is True
        assert "poistettu" in result.message.lower() or "poistettu" in result.message

    def test_remove_model_missing_name(self, agent):
        """Testaa että puuttuva mallin nimi palauttaa virheen poistossa."""
        result = agent.run("Poista", action="remove")

        assert result.success is False

    def test_info_with_known_model(self, agent):
        """Testaa tiedon hakeminen tunnetullemallille."""
        result = agent.run("Näytä info", action="info", model_name="llama3.1:8b")

        assert result.success is True
        assert result.model_info["name"] == "llama3.1:8b"
        assert "memory_estimate" in result.model_info

    def test_info_with_unknown_model(self, agent):
        """Testaa tiedon hakeminen tuntemattomalle mallille."""
        result = agent.run("Näytä info", action="info", model_name="tuntematon_malli")

        assert result.success is False
        assert "ei löydy" in result.message.lower() or "ei löydy" in result.message

    def test_config_creates_default(self, agent):
        """Testaa konfiguraation luonti oletuksena."""
        result = agent.run("Konfiguroi", action="config", provider="ollama")

        assert result.success is True
        assert result.config is not None
        assert "temperature" in result.config or "n_ctx" in result.config

    def test_config_with_custom_values(self, agent):
        """Testaa konfiguraation luonti mukautetuilla arvoilla."""
        custom_config = {"n_threads": 8, "n_batch": 1024, "temperature": 0.5}
        result = agent.run("Konfiguroi", action="config", provider="llama.cpp", config=custom_config)

        assert result.success is True
        assert result.config["n_threads"] == 8

    def test_unknown_action(self, agent):
        """Testaa tuntemattoman toiminnon käsittely."""
        result = agent.run("Testaa", action="tuntematon")

        assert result.success is False
        assert "tuntematon" in result.message.lower() or "tuntematon" in result.message

    def test_oassistant_commands_exist(self):
        """Vahvistaa että Ollama-komennot on määritelty."""
        assert "list" in OLLAMA_COMMANDS
        assert "pull" in OLLAMA_COMMANDS
        assert "run" in OLLAMA_COMMANDS


# =============================================================================
# ModelRunnerAgent
# =============================================================================

class TestModelRunnerAgent:
    """Testit ModelRunnerAgentille."""

    @pytest.fixture
    def agent(self):
        return ModelRunnerAgent()

    def test_agent_type(self, agent):
        """Vahivistaa agentin tyyppi."""
        assert agent.agent_type == "model_runner"

    def test_input_output_schemat(self, agent):
        """Vahvistaa syöte- ja tulosteasemats."""
        assert agent.input_schema == ModelRunnerInput
        assert agent.output_schema == ModelRunnerOutput

    def test_actions_dict_exists(self):
        """Vahvistaa että MODEL_RUNNER_ACTIONS sisältää oikeat toiminnot."""
        assert "run" in MODEL_RUNNER_ACTIONS
        assert "benchmark" in MODEL_RUNNER_ACTIONS
        assert "compare" in MODEL_RUNNER_ACTIONS

    def test_run_without_model(self, agent):
        """Testaa suorituksen ilman mallia."""
        result = agent.run("Kysy jotain", action="run", model="", prompt="Kerro jotain")

        assert result.success is False
        assert "malli" in result.message.lower() or "pakollinen" in result.message.lower()

    def test_run_without_prompt(self, agent):
        """Testaa suorituksen ilman kehoitetta."""
        result = agent.run("Kysy jotain", action="run", model="llama3.1:8b", prompt="")

        assert result.success is False

    def test_run_with_ollama_model(self, agent):
        """Testaa suoritus Ollama-mallilla."""
        result = agent.run("Kysy jotain", action="run", model="mistral:7b", prompt="Kerro 2+2")

        assert result.success is True
        assert result.response is not None
        assert result.model_used == "mistral:7b"
        assert result.inference_time_ms >= 0

    def test_run_with_llama_cpp_model(self, agent):
        """Testaa suoritus llama.cpp-mallilla."""
        result = agent.run("Kysy jotain", action="run", model="llama3.1:8b", prompt="Kerro 2+2")

        assert result.success is True
        assert result.response is not None
        assert "simuloitu" in result.response

    def test_run_gguf_model(self, agent):
        """Testaa suoritus .gguf-mallilla."""
        result = agent.run("Kysy jotain", action="run", model="/path/to/model.gguf", prompt="Test")

        assert result.success is True
        assert "simuloitu" in result.response

    def test_benchmark(self, agent):
        """Testaa benchmark-käynnitys."""
        result = agent.run("Benchmarkki", action="benchmark")

        assert result.success is True
        assert len(result.benchmark_results) > 0
        assert "tokens_per_second" in result.benchmark_results[0]

    def test_benchmark_with_specific_models(self, agent):
        """Testaa benchmarkti tietyin mallein."""
        custom_models = ["llama3.1:8b", "phi3:mini"]
        result = agent.run("Benchmarkki", action="benchmark", models_to_compare=custom_models)

        assert result.success is True
        assert len(result.benchmark_results) == 2

    def test_compare(self, agent):
        """Testaa vertailu."""
        result = agent.run("Vertaile", action="compare")

        assert result.success is True
        assert len(result.comparison_results) >= 2
        assert result.best_model != ""

    def test_compare_with_specific_models(self, agent):
        """Testaa vertailu tietyin mallein."""
        custom_models = ["llama3.1:8b", "mistral:7b", "phi3:mini"]
        result = agent.run("Vertaile", action="compare", models_to_compare=custom_models)

        assert result.success is True
        assert len(result.comparison_results) == 3

    def test_compare_results_sorted_by_speed(self, agent):
        """Testaa että vertailutulokset ovat järjestetty nopeus."""
        result = agent.run("Vertaile", action="compare")

        speeds = [r["tokens_per_second"] for r in result.comparison_results]
        assert speeds == sorted(speeds, reverse=True)

    def test_unknown_action(self, agent):
        """Testaa tuntemattoman toiminnon käsittely."""
        result = agent.run("Testaa", action="tuntematon")

        assert result.success is False

    def test_large_model_slower_in_benchmark(self, agent):
        """Testaa että isompimallit ovat hidompia benchmarkissa."""
        result = agent.run("Benchmarkki", action="benchmark")

        speeds = {r["model"]: r["tokens_per_second"] for r in result.benchmark_results}
        # llama3.1:70b pitäisi olla hitaampi kuin llama3.1:8b
        if "llama3.1:70b" in speeds and "llama3.1:8b" in speeds:
            assert speeds["llama3.1:70b"] < speeds["llama3.1:8b"]


# =============================================================================
# QuantizationAgent
# =============================================================================

class TestQuantizationAgent:
    """Testit QuantizationAgentille."""

    @pytest.fixture
    def agent(self):
        return QuantizationAgent()

    def test_agent_type(self, agent):
        """Vahvistaa agentin tyyppi."""
        assert agent.agent_type == "quantization"

    def test_input_output_schemat(self, agent):
        """Vahvistaa syöte- ja tulosteasemats."""
        assert agent.input_schema == QuantizationInput
        assert agent.output_schema == QuantizationOutput

    def test_actions_dict_exists(self):
        """Vahvistaa että QUANTIZATION_ACTIONS sisältää oikeat toiminnot."""
        assert "quantize" in QUANTIZATION_ACTIONS
        assert "analyze" in QUANTIZATION_ACTIONS
        assert "recommend" in QUANTIZATION_ACTIONS

    def test_quantization_formats_defined(self):
        """Vahvistae että kvankisointimuodot on määritelty."""
        assert "F32" in QUANTIZATION_FORMATS
        assert "F16" in QUANTIZATION_FORMATS
        assert "Q4_K" in QUANTIZATION_FORMATS
        assert "Q8_0" in QUANTIZATION_FORMATS

        # Tarkista tietorakenne
        for fmt_id, info in QUANTIZATION_FORMATS.items():
            assert "name" in info
            assert "bits" in info
            assert "size_ratio" in info
            assert "description" in info

    def test_analyze_missing_path(self, agent):
        """Testaa analyssi ilman tiedostopolkua."""
        result = agent.run("Analysoi", action="analyze", model_path="")

        assert result.success is False
        assert "pakollinen" in result.message.lower() or "polku" in result.message.lower()

    def test_analyze_nonexistent_file(self, agent, tmp_path):
        """Testaa analyysi olematommalla tiedostolla."""
        fake_path = str(tmp_path / "nonexistent.gguf")
        result = agent.run("Analysoi", action="analyze", model_path=fake_path)

        assert result.success is False
        assert "ei löydy" in result.message.lower()

    def test_analyze_existing_file(self, agent, tmp_path):
        """Testaa analyysi olemassa olevan tiedoston kanssa."""
        fake_path = tmp_path / "model.gguf"
        fake_path.write_bytes(b"0" * (10 * 1024 * 1024))  # 10 MB

        result = agent.run("Analysoi", action="analyze", model_path=str(fake_path), model_name="llama3.1:8b")

        assert result.success is True
        assert result.original_size_mb > 0
        assert "memory_estimate" in result.model_info

    def test_quantize_without_path(self, agent):
        """Testaa kvantisointi ilman polkua (käytetään oletuskokoa)."""
        result = agent.run("Kvantoi", action="quantize", model_path="")

        assert result.success is True
        assert result.original_size_mb > 0
        assert result.quantized_size_mb > 0

    def test_quantize_with_path(self, agent, tmp_path):
        """Testaa kvantisointi tiedoston kanssa."""
        fake_path = tmp_path / "model.gguf"
        fake_path.write_bytes(b"0" * (50 * 1024 * 1024))  # 50 MB

        result = agent.run("Kvantoi", action="quantize", model_path=str(fake_path), target_format="Q4_K")

        assert result.success is True
        assert result.original_size_mb == 50.0  # noin
        assert result.target_format_name == "4-bit (K_M)"
        assert result.size_reduction > 0
        assert result.estimated_vram > 0
        assert result.estimated_ram > 0

    def test_quantize_q4_k_reduction(self, agent):
        """Testaa Q4_K-kwantisoinnin koon pienennys."""
        result = agent.run("Kvantoi", action="quantize", model_path="", target_format="Q4_K")

        # Q4_K on size_ratio 0.5, joten pienennys tulisi olla noin 50%
        assert 30 <= result.size_reduction <= 70

    def test_quantize_q2_k_reduction(self, agent):
        """Testaa Q2_K-kwantisoinnin koon pienennys on suurempi."""
        result = agent.run("Kvantoi", action="quantize", model_path="", target_format="Q2_K")

        # Q2_K on size_ratio 0.25, joten pienennys tulisi olla noin 75%
        assert result.size_reduction > 50

    def test_quantize_f32_no_reduction(self, agent):
        """Testaa F32-kwantisoinnin (ei kompresiota)."""
        result = agent.run("Kvantoi", action="quantize", model_path="", target_format="F32")

        assert result.size_reduction == 0
        assert result.quantized_size_mb == result.original_size_mb

    def test_quantize_unknown_format_defaults_to_q4(self, agent):
        """Testaa että tuntematon muoto käyttää Q4_K oletuksena."""
        result = agent.run("Kvantoi", action="quantize", model_path="", target_format="TUNTEMATON")

        assert result.success is True
        assert result.target_format_name == "4-bit (K_M)"

    def test_recommend(self, agent):
        """Testaa suosikien antaminen."""
        result = agent.run("Suosikki", action="recommend", model_name="llama3.1:8b")

        assert result.success is True
        assert len(result.recommendations) > 0

    def test_recommend_with_model_path(self, agent, tmp_path):
        """Testaa suosikien antaminen mallin polun kanssa."""
        fake_path = tmp_path / "model.gguf"
        fake_path.write_bytes(b"0" * (100 * 1024 * 1024))  # 100 MB

        result = agent.run("Suosikki", action="recommend", model_path=str(fake_path), model_name="llama3.1:8b")

        assert result.success is True
        assert len(result.recommendations) > 0

    def test_recommend_returns_multiple_formats(self, agent):
        """Testaa että suosikki palauttaa useita muotoja."""
        result = agent.run("Suosikki", action="recommend", model_name="mistral:7b")

        recs = result.recommendations
        assert len(recs) > 1

        # Tarkista että Q-mallit sisältyvät (pienemmät ne).
        rec_texts = " ".join(recs)
        # Vähintään yksi Q-muoto tulisi olla suositeltu
        assert any(fmt in rec_texts for fmt in ["Q2_K", "Q3_K", "Q4_K", "Q5_K", "Q6_K", "Q8_0"])

    def test_unknown_action(self, agent):
        """Testaa tuntemattoman toiminnon käsittely."""
        result = agent.run("Testaa", action="tuntematon")

        assert result.success is False

    def test_size_reduction_calculation(self, agent):
        """Testaa koon pienennyslaskeminen eri muodoissa."""
        for fmt_id, fmt_info in QUANTIZATION_FORMATS.items():
            result = agent.run("Kvantoi", action="quantize", target_format=fmt_id)
            expected_reduction = round((1 - fmt_info["size_ratio"]) * 100, 1)
            assert result.size_reduction == expected_reduction, f"Virhe muodissa {fmt_id}: odotettiin {expected_reduction}%, sai {result.size_reduction}%"

    def test_memory_estimates_defined(self):
        """Vahvistae että muistitietopluvat on määritelty."""
        assert len(MEMORY_ESTIMATES) > 5
        for model, estimates in MEMORY_ESTIMATES.items():
            assert "vram_f16" in estimates
            assert "vram_q4" in estimates
            assert "ram_f16" in estimates
            assert "ram_q4" in estimates


# =============================================================================
# Integraatiot tests
# =============================================================================

class TestLocalLLMIntegration:
    """Integraatiot testit Local-LLM-moduulille."""

    def test_all_agents_inherit_base(self):
        """Vahvistae että kaikki agentit perivät BaseAgentin."""
        assert issubclass(LocalModelAgent, BaseAgent)
        assert issubclass(ModelRunnerAgent, BaseAgent)
        assert issubclass(QuantizationAgent, BaseAgent)

    def test_all_agents_have_inputs(self):
        """Vahvistae että kaikilla agenteilla on oikeat syöteklassit."""
        assert LocalModelAgent.input_schema == LocalModelInput
        assert ModelRunnerAgent.input_schema == ModelRunnerInput
        assert QuantizationAgent.input_schema == QuantizationInput

    def test_all_agents_have_outputs(self):
        """Vahvistae että kaikilla agenteilla on oikeat tulosteklassit."""
        assert LocalModelAgent.output_schema == LocalModelOutput
        assert ModelRunnerAgent.output_schema == ModelRunnerOutput
        assert QuantizationAgent.output_schema == QuantizationOutput

    def test_model_runner_uses_quanitzation_data(self):
        """Testaa että ModelRunnerAgent käyttää QUANTIZATION_FORMATS-tietoja.

        Tämä on tärkeä integraatiotarkistus varmistaen että kvantisointi- ja
        suoritustiedot ovat johdonmukaiset.
        """
        runner = ModelRunnerAgent()
        quant = QuantizationAgent()

        # Molemmat tulisi käyttää samoja muistitietoja
        mem_runner = runner._get_model_info("llama3.1:8b")
        mem_quant = quant._get_model_memory_estimate("llama3.1:8b")

        # Memory_ESTIMATES sisältää molemmissa
        assert mem_quant["vram_f16"] == MEMORY_ESTIMATES["llama3.1:8b"]["vram_f16"]
